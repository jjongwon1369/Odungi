"""L1 v2: typed identifier-set matching, not whole-answer factual accuracy.
Preferred spelling is reported separately. Explicit type/parent contradictions
must not be silently corrected using gold. Prose parsing is conservative and
limited; negation, version assertions and citation support require L2.
"""
import argparse, json, pathlib, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from matter_ids import norm_id, width_ok, norm_name, WIDTH

ROOT = pathlib.Path(__file__).resolve().parent.parent
GT = ROOT / "eval" / "ground_truth"

TOP = ("cluster", "device_type", "base_cluster")
CHILD = ("attribute", "command", "generated_command", "event", "feature")
ID_ENTITIES = ("cluster", "device_type", "attribute", "command", "generated_command", "event")
HEX = re.compile(r"(?<![0-9A-Za-z])0[xX][0-9A-Fa-f]{1,8}(?![0-9A-Za-z])")
CITE = re.compile(r"\[S(\d+)\]")
KEYWORDS = [  # (정규식, 엔티티) — 창 안에서 식별자에 가장 가까운 것 채택
    (re.compile(r"device[\s-]*types?", re.I), "device_type"),
    (re.compile(r"clusters?", re.I), "cluster"),
    (re.compile(r"attributes?", re.I), "attribute"),
    (re.compile(r"commands?", re.I), "command"),
    (re.compile(r"events?", re.I), "event"),
    # 한국어 답변 (2026-09-28): "Fan Control 클러스터(0x0202)"가 커맨드 ID로 오판되던 문제
    (re.compile(r"디바이스\s*타입|기기\s*유형|장치\s*유형"), "device_type"),
    (re.compile(r"클러스터"), "cluster"),
    (re.compile(r"속성|어트리뷰트"), "attribute"),
    (re.compile(r"커맨드|명령"), "command"),
    (re.compile(r"이벤트"), "event"),
]
WINDOW = 100


class Index:
    """버전별 ground truth. (entity, parent, id) 조회 + 이름 조회."""

    def __init__(self):
        self.by_ver = {}
        for d in sorted(GT.iterdir()):
            f = d / "records.jsonl"
            if f.exists():
                recs = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
                self.by_ver[d.name] = {(r["entity"], r["parent_id"], r["id"]): r for r in recs}

    def get(self, ver, ent, parent, id_):
        return self.by_ver.get(ver, {}).get((ent, parent, id_))

    def exists_any(self, ent, parent, id_, versions):
        return [v for v in versions if self.get(v, ent, parent, id_)]

    def name_table(self, versions, parents):
        """정규화 이름 → [record]. 최상위 엔티티 전체 + 관련 부모 클러스터의 자식들."""
        tab = defaultdict(list)
        for v in versions:
            for (e, p, i), r in self.by_ver[v].items():
                if e in TOP or (e in CHILD and p in parents):
                    n = norm_name(r["name"])
                    if n and r not in tab[n]:
                        tab[n].append(r)
        return tab


def name_regex(name):
    """'On/Off' → On\\W*Off,  'Room Air Conditioner' → Room\\W*Air\\W*Conditioner (대소문자 무시)"""
    toks = re.findall(r"[A-Za-z0-9]+", re.sub(r"\s+Cluster$", "", name))
    return re.compile(r"(?<![A-Za-z0-9])" + r"[\W_]*".join(map(re.escape, toks)) + r"(?![A-Za-z0-9])", re.I)


def find_names(text, table):
    """텍스트 속 알려진 이름의 (start, end, records). 겹치면 긴 것 우선."""
    hits = []
    seen = set()
    for nm in dict.fromkeys(r["name"] for recs in table.values() for r in recs):
        if nm in seen:
            continue
        seen.add(nm)
        for m in name_regex(nm).finditer(text):
            hits.append((m.start(), m.end(), table[norm_name(nm)]))
    hits.sort(key=lambda h: (-(h[1] - h[0]), h[0]))
    kept = []
    for h in hits:
        if all(h[1] <= k[0] or h[0] >= k[1] for k in kept):
            kept.append(h)
    return sorted(kept)


def pick_record(recs, raw, default_ent, explicit_ent=None, explicit_parent=None):
    """같은 이름의 후보 중 선택: ① ID가 맞는 것 ② answer_entity ③ 첫 번째"""
    if explicit_ent:
        candidates = [r for r in recs if r["entity"] == explicit_ent or
                      (explicit_ent == "command" and r["entity"] == "generated_command")]
        if candidates:
            recs = candidates
    if explicit_parent is not None:
        candidates = [r for r in recs if r["parent_id"] == explicit_parent]
        if candidates:
            recs = candidates
    for r in recs:
        if r["entity"] in WIDTH and norm_id(r["entity"], raw) == r["id"]:
            return r, True
    for r in recs:
        if r["entity"] == default_ent:
            return r, False
    return recs[0], False


# 마크다운 표기(`Name` (0x..), **Name**(0x..), "Name"(0x..))도 인접으로 본다 (2026-09-28)
MD = "`\"'*“”‘’"
ADJ = re.compile(rf"[\s(:=\-{MD}]*(?:(?:device[\s-]*type|cluster|attribute|command|event)s?"
                 rf"|디바이스\s*타입|기기\s*유형|클러스터|속성|어트리뷰트|커맨드|명령|이벤트)?[\s(:=\-{MD}]*"
                 rf"(?:id\s*)?(?:[은는이가의]\s*)?(?:is\s*)?[\s(:=\-{MD}]*", re.I)
AFTER = re.compile(rf"[\s{MD}]*\(\s*[{MD}]*")
SENT_END = re.compile(r"[.;\n](?=\s|$)")


def explicit_cluster_scopes(text, names, start, end, whole_text=False):
    """Only named clusters with an explicit 'cluster' suffix, within a sentence.
    Multiple distinct parents are ambiguous instead of choosing a gold parent.
    """
    lo = 0 if whole_text else max([m.end() for m in SENT_END.finditer(text, 0, start)] or [0])
    stop = SENT_END.search(text, end)
    hi = len(text) if whole_text or stop is None else stop.start()
    scopes = set()
    for a, b, recs in names:
        if lo <= a < b <= hi and re.match(r"\s+(?:cluster|클러스터)\b", text[b:hi], re.I):
            scopes.update(r["id"] for r in recs if r["entity"] == "cluster")
    for ident in HEX.finditer(text, lo, hi):
        before = text[max(lo, ident.start() - WINDOW):ident.start()]
        if re.search(r"(?:\bcluster|클러스터)\s*(?:ID\s*)?(?:[은는이가의]\s*)?(?:is\s*)?[:=(\s]*$", before, re.I):
            scopes.add(norm_id("cluster", ident.group()))
    return sorted(scopes)


def unknown_cluster_scope(text, names, start, end):
    lo = max([m.end() for m in SENT_END.finditer(text, 0, start)] or [0])
    stop = SENT_END.search(text, end)
    hi = len(text) if stop is None else stop.start()
    for m in re.finditer(r"\b[A-Z][A-Za-z0-9_]*(?:[ /-]+[A-Z][A-Za-z0-9_]*)*\s+cluster\b", text[lo:hi]):
        a, b = lo + m.start(), lo + m.end()
        if re.match(r"\s*(?:ID\s*)?(?:is\s*)?[:=(\s]*0[xX][0-9A-Fa-f]+", text[b:hi], re.I):
            continue
        if not any(a <= x < y <= b and any(r["entity"] == "cluster" for r in recs)
                   for x, y, recs in names):
            return True
    return False


def unknown_adjacent_name(text, start):
    """Recognize a bounded Name (ID) form, not arbitrary prose nouns."""
    m = re.search(r"(?<![A-Za-z0-9_])([A-Z][A-Za-z0-9_]*)\s*"
                  r"(?:(?:cluster|attribute|command|event|device type)\s*)?\(\s*$", text[:start])
    if m and m.group(1) not in {"ID", "Id", "Answer", "The", "IDs"}:
        return m.group(1)
    return None


def extract(text, table, default_ent):
    """0x.. 식별자 언급 목록 → [{raw, span, entity, name_rec, name_consistent, how}]

    이름 짝짓기 2단계:
      ① 인접 짝: "Name (0x..)", "Name cluster: 0x..", "0x.. (Name)" — 그 식별자가 이름을 '점유'
      ② 인접 짝이 없으면 같은 문장에서 다른 식별자가 점유하지 않은 이름 중
         answer_entity 타입 우선, 가장 가까운 것
         (예: "The SetActivePresetRequest command of the Thermostat cluster (0x0201) has ID 0x05"
              → Thermostat은 0x0201이 점유, 0x05는 SetActivePresetRequest와 짝)
    """
    names = find_names(text, table)
    hexes = list(HEX.finditer(text))

    adj = {}
    for i, m in enumerate(hexes):
        prev_end = hexes[i - 1].end() if i else 0
        after = [n for n in names if n[0] > m.end() and AFTER.fullmatch(text[m.end():n[0]])]
        before = [n for n in names if prev_end <= n[1] <= m.start() and ADJ.fullmatch(text[n[1]:m.start()])]
        if before:
            adj[i] = max(before, key=lambda n: n[0])
        elif after:
            adj[i] = min(after, key=lambda n: n[0])
    claimed = {id(n) for n in adj.values()}

    out = []
    for i, m in enumerate(hexes):
        mention = {"raw": m.group(), "span": [m.start(), m.end()]}
        near = adj.get(i)
        if near is None:
            ends = [e.end() for e in SENT_END.finditer(text, 0, m.start())]
            lo = max(ends[-1] if ends else 0, m.start() - 2 * WINDOW)
            cands = [n for n in names if lo <= n[0] and n[1] <= m.start() and id(n) not in claimed]
            # A sentence-level fallback requires canonical case AND the target
            # entity. Lowercase English verbs such as "identify" are not names.
            cands = [n for n in cands if any(
                r["entity"] == default_ent and text[n[0]:n[1]] == r["name"]
                for r in n[2])]
            pref = cands
            if pref or cands:
                near = max(pref or cands, key=lambda n: n[0])
                claimed.add(id(near))
        if near is not None:
            gap = text[near[1]:m.start()] if near[1] <= m.start() else ""
            explicit_ent = next((ent for rx, ent in KEYWORDS if rx.match(gap.lstrip(" (:=\t-"))), None)
            scopes = explicit_cluster_scopes(text, names, m.start(), m.end())
            parent = scopes[0] if len(scopes) == 1 else None
            rec, consistent = pick_record(near[2], m.group(), default_ent, explicit_ent, parent)
            if explicit_ent:
                mention["explicit_entity"] = explicit_ent
                if not (explicit_ent == rec["entity"] or
                        (explicit_ent == "command" and rec["entity"] == "generated_command")):
                    mention["type_conflict"] = True
            mention.update(entity=rec["entity"], name=rec["name"], name_rec=rec, name_consistent=consistent,
                           how="name" if i in adj else "name(sentence)")
        else:
            prev_end = hexes[i - 1].end() if i else 0
            win = text[max(prev_end, m.start() - WINDOW):m.start()]
            best = None
            for rx, ent in KEYWORDS:
                for k in rx.finditer(win):
                    if best is None or k.start() > best[0]:
                        best = (k.start(), ent)
            mention.update(entity=best[1] if best else default_ent, name=None, name_rec=None,
                           name_consistent=None, how="keyword" if best else "default")
        if mention["entity"] in CHILD:
            scopes = explicit_cluster_scopes(text, names, m.start(), m.end())
            if len(scopes) == 1:
                mention["explicit_parent"] = scopes[0]
            elif len(scopes) > 1:
                mention["ambiguous_parent"] = True
            if unknown_cluster_scope(text, names, m.start(), m.end()):
                mention["ambiguous_parent"] = True
        if near is None:
            unknown = unknown_adjacent_name(text, m.start())
            if unknown:
                mention["unknown_name"] = unknown
        out.append(mention)
    return out


def classify(mn, q, idx, gold_keys, versions, all_versions, gold_parents):
    ent, raw = mn["entity"], mn["raw"]
    if ent == "generated_command":
        ent_w = "command"
    else:
        ent_w = ent
    nid = norm_id(ent, raw) if ent in WIDTH else None
    mn["id"] = nid

    # 부모 결정: 최상위면 None, 자식이면 이름 레코드의 부모 → gold 부모(유일할 때)
    if ent in TOP:
        parent = None
    elif mn.get("ambiguous_parent"):
        mn["verdict"] = "unresolved"
        return
    elif mn.get("explicit_parent") is not None:
        parent = mn["explicit_parent"]
    elif mn.get("name_rec"):
        parent = mn["name_rec"]["parent_id"]
    elif len(gold_parents) == 1:
        parent = next(iter(gold_parents))
    else:
        mn["verdict"] = "unresolved"
        return
    mn["parent_id"] = parent

    mn["format_error"] = not width_ok(ent_w, raw)
    if nid is None:
        mn["verdict"] = "unresolved"
        return
    rec = mn.get("name_rec")
    if mn.get("type_conflict"):
        mn["verdict"] = "type_conflict"
        return
    if rec and ent in CHILD and parent != rec["parent_id"]:
        mn["verdict"] = "parent_conflict"
        return
    if mn.get("unknown_name") and idx.exists_any(ent, parent, nid, all_versions):
        mn["verdict"] = "unknown_name"
        return
    if rec is not None and not mn["name_consistent"]:
        # 이름은 실존. ID도 같은 부모·타입 아래 실존하면 mismatch, 아니면 fabricated
        if idx.exists_any(ent, parent, nid, versions):
            mn["verdict"] = "mismatch"
            mn["note"] = f"{rec['name']} 의 실제 ID는 {rec['id']}"
        elif idx.exists_any(ent, parent, nid, all_versions):
            mn["verdict"] = "mismatch"
            mn["other_version"] = idx.exists_any(ent, parent, nid, all_versions)
        else:
            mn["verdict"] = "fabricated"
            mn["note"] = f"{rec['name']} 는 실존하나 {nid} 는 없음 (실제 {rec['id']})"
        return

    key = (ent, parent, nid)
    scored = ent == q["answer_entity"] or (q["answer_entity"] == "command" and ent == "generated_command")
    if key in gold_keys:
        mn["verdict"] = "gold"
    elif idx.exists_any(ent, parent, nid, versions):
        # 채점 타입이 아닌 실존 언급(질문 맥락 반복 등)은 오답이 아니라 context
        mn["verdict"] = "offscope" if scored else "context"
    elif idx.exists_any(ent, parent, nid, all_versions):
        mn["verdict"] = "offscope" if scored else "context"
        mn["other_version"] = idx.exists_any(ent, parent, nid, all_versions)
    else:
        mn["verdict"] = "fabricated"


def score_features(text, q, idx, versions):
    """Known codes anywhere; unknown uppercase codes only in explicit lists.

    Unknown prose words are not automatically fabricated references. For a
    fully general natural-language answer use L2; code-list answers are the
    supported deterministic contract for feature questions.
    """
    parents = {k[2] for k in q["gold_record_keys"]}
    if q.get("target_parent") is not None:
        parents = {norm_id("cluster", q["target_parent"])}
    codes = defaultdict(set)
    for v in versions:
        for (e, p, i), r in idx.by_ver[v].items():
            if e == "feature" and p in parents:
                codes[r["name"]].add((p, i))
    candidates = {}
    for code in codes:
        for m in re.finditer(rf"(?<![A-Za-z0-9]){re.escape(code)}(?![A-Za-z0-9])", text):
            candidates[(m.start(), m.end())] = code
    # Bare code lists, optionally prefixed by 'Features:' and with bit numbers.
    cleaned = CITE.sub(lambda m: " " * len(m.group()), text)
    for line in re.finditer(r"[^\n]+", cleaned):
        part = re.sub(r"^\s*(?:feature codes?|features?|the answer is)\s*[:=]?\s*",
                      "", line.group(), flags=re.I)
        token = r"[A-Z][A-Z0-9_]*(?:\s*\([0-9]+\))?"
        if re.fullmatch(rf"\s*{token}(?:\s*(?:,|;|\band\b)\s*{token})*\s*[.]?\s*", part):
            offset = line.start() + len(line.group()) - len(part)
            for m in re.finditer(r"[A-Z][A-Z0-9_]*", part):
                candidates[(offset + m.start(), offset + m.end())] = m.group()
    found = []
    gold = {tuple(k[1:]) for k in q["gold_record_keys"]}
    for span, code in sorted(candidates.items()):
        options = codes.get(code, set())
        parent, ident = next(iter(options)) if len(options) == 1 else (None, None)
        verdict = ("gold" if ("feature", parent, ident) in gold else "offscope") if len(options) == 1 else (
            "unknown_name" if not options else "unresolved")
        found.append({"raw": code, "span": list(span), "entity": "feature", "parent_id": parent,
                      "id": ident, "verdict": verdict, "how": "code"})
    return found


def score_one(ans, q, idx):
    text = ans["answer_text"]
    gold_list = [tuple(k) for k in q["gold_record_keys"]]
    versions = sorted({k[0] for k in gold_list} | {q["version_to"]})
    all_versions = sorted(idx.by_ver)
    gold_keys = {k[1:] for k in gold_list}
    gold_parents = {k[2] for k in gold_list if k[1] in CHILD}
    if q.get("target_parent") is not None:
        gold_parents = {norm_id("cluster", q["target_parent"])}
    ae = q["answer_entity"]

    top_table = idx.name_table(versions, set())
    explicit_parents = {cid for cid in explicit_cluster_scopes(
        text, find_names(text, top_table), 0, len(text), whole_text=True)}
    table = idx.name_table(versions, gold_parents | explicit_parents)
    mentions = extract(text, table, ae)
    for mn in mentions:
        classify(mn, q, idx, gold_keys, versions, all_versions, gold_parents)

    if ae == "feature":
        scored = score_features(text, q, idx, versions)
        mentions += scored
    else:
        scored = [m for m in mentions if m["entity"] == ae or
                  (ae in ("command", "generated_command") and m["entity"] in ("command", "generated_command")) or
                  (m.get("type_conflict") and m.get("explicit_entity") == ae)]
    pred = set()
    invalid = {"mismatch", "unresolved", "type_conflict", "parent_conflict", "unknown_name", "fabricated"}
    for m in scored:
        if m["verdict"] in invalid:
            # Set-based scoring: repeating the same invalid assertion is not
            # a new prediction. Mention counts remain available separately.
            pred.add(("__wrong__", m["entity"], m.get("parent_id"), m.get("id"),
                      m.get("unknown_name") or m.get("name") or m["raw"], m["verdict"]))
        else:
            pred.add((m["entity"], m["parent_id"], m["id"]))
    gold = {tuple(k[1:]) for k in gold_list}
    # 이름 인정 (2026-09-28): 질문이 ID를 요구하지 않으면('ID' 문구 없음) 정답 요소의 이름만 써도 맞은 것으로 본다.
    # 재현율만 보정한다 — ID 없이 언급된 다른 이름은 감점하지 않는다(설명 속 대조 언급 보호).
    name_credit = set()
    if ae != "feature" and "ID" not in q.get("question_ko", q.get("question_en", "")):
        named = {(r["entity"], r["parent_id"], r["id"]) for _, _, recs in find_names(text, table) for r in recs}
        fam = lambda e: "command" if e == "generated_command" else e
        name_credit = {k for k in (named & gold) if fam(k[0]) == fam(ae)} - pred
        pred |= name_credit
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    status = ans.get("answer_status", "answered")
    if status not in ("answered", "abstained", "error", "dummy"):
        raise ValueError(f"Invalid answer_status: {status}")
    expected = q.get("expected_answer_status")
    if expected not in (None, "answered", "abstained"):
        raise ValueError(f"Invalid expected_answer_status: {expected}")
    if expected == "abstained" and gold:
        raise ValueError("An abstention question must have empty gold_record_keys")
    eligible = status not in ("error", "dummy") and not ans.get("is_dummy", False) and not ans.get("error")
    empty_set_declared = (expected == "answered" and ans.get("final_identifiers") == [])
    # 사전등록 채점 방식(test_v1 `scoring`)이 judge인 문항은 L1 대상이 아니다. scoring 칸이 없는 dev 문항은 기존대로.
    l1_eligible = (eligible and expected != "abstained" and bool(gold or empty_set_declared)
                   and q.get("scoring") != "judge")
    em = int(pred == gold)
    if status == "abstained":
        # A claimed abstention with identifiers is a contradictory output.
        em, p, r, f1 = 0, 0.0, 0.0, 0.0
    elif not gold and not pred and empty_set_declared:
        em, p, r, f1 = 1, 1.0, 1.0, 1.0
    abstention_correct = (int(status == "abstained" and not mentions)
                          if expected == "abstained" and eligible else None)

    markers = sorted(set(CITE.findall(text)))
    cited = ans.get("cited_sources") or {}
    cnt = lambda v: sum(1 for m in mentions if m.get("verdict") == v)
    return {
        "run_id": ans.get("run_id"), "system": ans.get("system"), "caching": ans.get("caching"),
        "query_id": q["query_id"], "split": q["split"], "type": q["type"], "answer_entity": ae,
        "scorer_version": "l1-v2", "answer_status": status, "l1_eligible": l1_eligible,
        "abstention_correct": abstention_correct,
        "l1_em": em if l1_eligible else None, "l1_p": round(p, 4) if l1_eligible else None,
        "l1_r": round(r, 4) if l1_eligible else None, "l1_f1": round(f1, 4) if l1_eligible else None,
        "n_pred": len(pred), "n_gold": len(gold), "n_tp": tp, "n_name_credit": len(name_credit),
        "fabricated": cnt("fabricated"), "offscope": cnt("offscope"), "mismatch": cnt("mismatch"),
        "format_error": sum(bool(m.get("format_error")) for m in mentions),
        "type_conflict": cnt("type_conflict"), "parent_conflict": cnt("parent_conflict"),
        "unknown_name": cnt("unknown_name"), "unresolved": cnt("unresolved"),
        "parent_context_source": ("not_used" if ae in TOP else "question" if q.get("target_parent") is not None else "legacy_gold"),
        "format_compliance": (all(not m.get("format_error") for m in mentions if m.get("id") is not None)
                              if any(m.get("format_error") is not None for m in mentions) else None),
        "stale_version": sum(1 for m in mentions if m.get("other_version")),
        "uncited": int(not markers or not cited),
        "dangling_citations": [f"S{i}" for i in markers if f"S{i}" not in cited],
        "missing_gold": sorted(f"{p_}/{i}" if p_ else i for e_, p_, i in gold - pred),
        "mentions": [{k: v for k, v in m.items() if k not in ("name_rec",)} for m in mentions],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("answers")
    ap.add_argument("--queries", default=str(ROOT / "eval" / "queries" / "dev.jsonl"))
    ap.add_argument("--out")
    ap.add_argument("-v", "--verbose", action="store_true", help="언급별 판정 출력")
    a = ap.parse_args()

    qs = {q["query_id"]: q for q in map(json.loads, open(a.queries, encoding="utf-8"))}
    idx = Index()
    answers = [json.loads(l) for l in open(a.answers, encoding="utf-8") if l.strip()]
    res = [score_one(x, qs[x["query_id"]], idx) for x in answers]

    out = pathlib.Path(a.out) if a.out else pathlib.Path(a.answers).with_name(
        pathlib.Path(a.answers).stem + ".l1.jsonl")
    with out.open("w", encoding="utf-8") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    hdr = f"{'run_id':22} {'query_id':15} {'EM':>2} {'P':>5} {'R':>5} {'F1':>5}  fab off mis fmt  uncited  missing"
    print(hdr); print("-" * len(hdr))
    for r in res:
        num = lambda key: "  N/A" if r[key] is None else f"{r[key]:5.2f}"
        print(f"{str(r['run_id']):22} {r['query_id']:15} {str(r['l1_em']):>2} {num('l1_p')} {num('l1_r')} {num('l1_f1')}"
              f"  {r['fabricated']:>3} {r['offscope']:>3} {r['mismatch']:>3} {r['format_error']:>3}  {r['uncited']:>7}  "
              f"{','.join(r['missing_gold']) or '-'}")
        if a.verbose:
            for m in r["mentions"]:
                extra = f"  ({m['note']})" if m.get("note") else ""
                extra += f"  [다른 버전에만 존재: {m['other_version']}]" if m.get("other_version") else ""
                nm = f" ← '{m['name']}'" if m.get("name") else ""
                print(f"      {m['raw']:>8} → {m['entity']:12} {str(m.get('parent_id') or ''):7} "
                      f"{m.get('verdict','?'):12} via {m['how']}{nm}{extra}")
    print(f"\n→ {out}")


if __name__ == "__main__":
    main()
