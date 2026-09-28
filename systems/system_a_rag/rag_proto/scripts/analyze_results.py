"""
참가자 × System A·B 배치 결과의 객관 지표(정답 미사용). rag_proto 폴더에서:
  PYTHONPATH=src python scripts/analyze_results.py <출력 md> <출력 json> \
      --questions ../../../benchmark/questions_v1.jsonl --a <A 결과 폴더>... --b <B 결과 폴더>...
결과 폴더는 run_eval 배치 출력(answers.jsonl, calls.jsonl, failed_attempts.jsonl, invocations.jsonl, summary.json).

objective_metrics.py(v2, 독립 재계산·수작업 대조로 검증)와 같은 정의를 모델별로 적용한다.
정답 여부는 판정하지 않는다(정답표는 평가 담당이 봉인). 지연은 평가 담당 결정(C5)대로 API 생성 시간을 본다.
"""
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from rag_proto.config import load
from rag_proto.s3_embed import IN_PATH as CHUNKS_PATH
from rag_proto.s6_generate import ABSTAIN_PHRASE

args = sys.argv[1:]
OUT_MD, OUT_JSON = Path(args[0]), Path(args[1])
QUESTIONS = Path(args[args.index("--questions") + 1])
A_DIRS = [Path(x) for x in args[args.index("--a") + 1:args.index("--b")]]
B_DIRS = [Path(x) for x in args[args.index("--b") + 1:]]

cfg = load()
STOPS = set(cfg.pipeline["identifiers"].get("stopwords", []))
CITE = re.compile(cfg.pipeline["generation"]["citation_pattern"])
CHUNKS = {c["chunk_id"]: c for c in map(json.loads, open(CHUNKS_PATH, encoding="utf-8"))}
BENCH = {r["query_id"]: r for r in map(json.loads, open(QUESTIONS, encoding="utf-8"))}
DOCS = "\n".join(json.loads(l)["text"] for l in open(Path(cfg.corpus["team_corpus"]["documents_path"]), encoding="utf-8"))
ORDER = ["gpt-6-luna", "deepseek-flash", "kimi-k3", "claude-sonnet-5", "gpt-6-sol", "claude-opus-5-5", "gpt-5.6-sol"]
# 100만 토큰당 USD: (캐시 없는 입력, 캐시 쓰기, 캐시 읽기, 출력). 각 제공자 가격 페이지 9/28 확인.
# DeepSeek은 시간대 요금이 있어 이번 실행 시간(한국 21~22시 = UTC 12~13시, 비혼잡)의 값을 쓴다.
PRICE = {
    "gpt-6-luna": (0.1, 0.125, 0.01, 0.5),
    "deepseek-flash": (0.15, 0.15, 0.003, 0.6),
    "kimi-k3": (3.0, 3.0, 0.3, 15.0),
    "claude-sonnet-5": (2.0, 2.5, 0.2, 10.0),
    "gpt-6-sol": (2.0, 2.5, 0.2, 10.0),
    "claude-opus-5-5": (4.0, 5.0, 0.2, 20.0),
    "gpt-5.6-sol": (4.0, 5.0, 0.4, 20.0),
}
ABSTAIN_LIKE = re.compile(r"확인되지\s*않|확인할\s*수\s*없|나와\s*있지\s*않|정보가\s*없|명시되어\s*있지\s*않|포함되어\s*있지\s*않"
                          r"|답변할\s*수\s*없|제시되어\s*있지\s*않|나타나지\s*않|나열되어\s*있지\s*않")
# 원문을 읽은 표본 감사로 확인한 보정(규칙으로 못 가르는 경우: 문서 속 부정문, "참고로" 배경만 붙인 기권 등)
AUDITED = {
    ("A", "claude-sonnet-5", "Q-multihop-008"): "partial", ("A", "kimi-k3", "Q-multihop-008"): "answer",
    ("A", "kimi-k3", "Q-multihop-007"): "answer", ("B", "kimi-k3", "Q-multihop-002"): "abstain",
    ("B", "kimi-k3", "Q-codedoc-010"): "abstain", ("B", "kimi-k3", "Q-practical-003"): "abstain",
    ("B", "claude-opus-5-5", "Q-practical-005"): "answer",
    ("A", "kimi-k3", "Q-control-001"): "abstain", ("A", "kimi-k3", "Q-control-003"): "abstain",
    ("B", "kimi-k3", "Q-control-003"): "abstain",
}
ID_PATS = [r"0x[0-9A-Fa-f]{2,8}", r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+"]
BRACKETS = re.compile(r"\[[^\[\]\n]+\]")
COLS = ("uncached_input", "cache_creation", "cache_read", "output")


def jl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def present(tok: str, text: str) -> bool:
    flags = re.IGNORECASE if tok.lower().startswith("0x") else 0
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(tok)}(?![A-Za-z0-9_])", text, flags) is not None


def answer_identifiers(text: str) -> set[str]:
    body = BRACKETS.sub(" ", text)
    ids = {m.group(0) for p in ID_PATS for m in re.finditer(rf"(?<![A-Za-z0-9_]){p}(?![A-Za-z0-9_])", body, re.ASCII)}
    for tok in re.findall(r"`([^`\n]+)`", body):
        tok = tok.strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:.\-]+|0x[0-9A-Fa-f]+", tok):
            ids.add(tok)
    return {i for i in ids if i not in STOPS}


def claim_units(text: str) -> list[str]:
    units: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or re.fullmatch(r"[-*_#\s|:]+", line):
            continue
        for piece in re.split(r"(?<=[.!?])((?:\s*\[[^\[\]\n]+\])*)\s+", line):
            if not piece or not piece.strip():
                continue
            piece = piece.strip()
            residue = re.sub(r"[\W_]", "", BRACKETS.sub("", piece))
            if len(residue) < 6 and units:
                units[-1] += " " + piece
            elif len(residue) >= 6:
                units.append(piece)
    def heading(u: str) -> bool:
        t = BRACKETS.sub("", u).strip().replace("**", "").replace("__", "").strip()
        return t.endswith(":") or bool(re.fullmatch(r"\*\*[^*]{1,40}\*\*:?", u.strip()))
    return [u for u in units if not heading(u)]


def abstain_like(unit: str) -> bool:
    return ABSTAIN_PHRASE in unit or bool(ABSTAIN_LIKE.search(BRACKETS.sub("", unit)))


def shown(cid: str) -> str:
    c = CHUNKS[cid]
    return f"[{cid}] (source: {c['source_path']})\n{c['text']}"


def id_kind(tok: str, ctx: str) -> str:
    """맥락에 그대로 없는 식별자를 네 가지로 나눈다. '코퍼스에도 없음'만 지어낸 것이다."""
    parts = [x for x in tok.split("::") if x]
    if tok in ctx:
        return "더 긴 식별자의 일부"
    if tok.lower() in ctx.lower():
        return "대소문자 차이"
    if len(parts) > 1 and all(x.lower() in ctx.lower() for x in parts):
        return "합성"
    if tok in DOCS or tok.lower() in DOCS.lower():
        return "맥락 밖(코퍼스엔 있음)"
    return "코퍼스에도 없음"


def cost(model: str, t: dict, neutral: bool = False) -> float:
    u, w, r, o = PRICE[model]
    if neutral:
        return ((t["uncached_input"] + t["cache_creation"] + t["cache_read"]) * u + t["output"] * o) / 1e6
    return (t["uncached_input"] * u + t["cache_creation"] * w + t["cache_read"] * r + t["output"] * o) / 1e6


def per_answer(rec: dict) -> dict:
    ans = rec.get("answer") or ""
    q = BENCH[rec["qid"]]
    top5 = [c["chunk_id"] for c in rec["citations"]]
    ctx = "\n".join(shown(c) for c in top5 if c in CHUNKS)
    cited = set(CITE.findall(ans)) | {m[1:-1] for m in BRACKETS.findall(ans)}
    cited_valid = {c for c in cited if c in top5}
    units = claim_units(ans)
    claim = [u for u in units if not abstain_like(u)]
    if not ans:
        st = "crash"
    elif not claim:
        st = "abstain"
    elif len(units) > len(claim):
        st = "partial"
    else:
        st = "answer"
    ids = {i for i in answer_identifiers(ans) if not present(i, q["question"])}
    scores = [c["rerank_score"] or 0.0 for c in rec["citations"]]
    return {
        "qid": rec["qid"], "model": rec["model"], "tier": q["tier"], "type": q["type"], "control": q["tier"] == "control",
        "status": st, "phrase": ABSTAIN_PHRASE in ans,
        "claim_units": len(claim), "claim_units_cited": sum(1 for u in claim if any(c in cited_valid for c in CITE.findall(u))),
        "dangling": sorted(cited - cited_valid), "n_ids": len(ids), "fabricated": sorted(i for i in ids if not present(i, ctx)),
        "id_kinds": {i: id_kind(i, ctx) for i in ids if not present(i, ctx)},
        "extra_after_abstain": ans.strip().startswith(ABSTAIN_PHRASE) and len(ans.strip()) > len(ABSTAIN_PHRASE) + 3,
        "top1": max(scores) if scores else 0.0, "tokens": rec["tokens"], "lat": rec["latency_ms"], "answer": ans,
        "top5": top5,
    }


def load_system(dirs: list[Path]) -> dict:
    recs, traces, fails, invs, summ = {}, defaultdict(list), [], [], []
    for d in dirs:
        for r in jl(d / "answers.jsonl"):
            recs[(r["model"], r["qid"])] = per_answer(r)
        for t in jl(d / "calls.jsonl"):
            traces[(t["model"], t["qid"])].append(t)
        fails += jl(d / "failed_attempts.jsonl")
        invs += jl(d / "invocations.jsonl")
        s = d / "summary.json"
        if s.exists():
            summ.append(json.loads(s.read_text(encoding="utf-8")))
    return {"recs": recs, "traces": traces, "fails": fails, "invs": invs, "summ": summ}


def reasoning_tokens(traces: list[dict]) -> int:
    n = 0
    for t in traces[-1:]:  # 채점 대상이 된 마지막 시도
        for c in t["calls"]:
            u = c.get("usage") or {}
            n += (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
            n += (u.get("output_tokens_details") or {}).get("thinking_tokens") or 0
    return n


def auc(pos, neg):
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


S = {"A": load_system(A_DIRS), "B": load_system(B_DIRS)}
n_audit = 0
for (k, m, q), st in AUDITED.items():
    if (m, q) in S[k]["recs"] and S[k]["recs"][(m, q)]["status"] != st:
        S[k]["recs"][(m, q)]["status"] = st; n_audit += 1
models = [m for m in ORDER if any(k[0] == m for k in S["A"]["recs"]) or any(k[0] == m for k in S["B"]["recs"])]
QIDS = list(BENCH)
NONCTL = [q for q in QIDS if BENCH[q]["tier"] != "control"]
CTL = [q for q in QIDS if BENCH[q]["tier"] == "control"]

md: list[str] = []
w = md.append
w("# 참가자 7종 × System A·B 결과 (effort low 테스트, 40문항)\n")
commits = sorted({(i["code_commit"] or "?")[:7] for s in S.values() for i in s["invs"]})
dirty = any(i.get("code_dirty") for s in S.values() for i in s["invs"])
starts = sorted(i["started_at"] for s in S.values() for i in s["invs"])
w(f"- 실행: {starts[0]} ~ {starts[-1]} 시작분, 코드 커밋 {', '.join(commits)} (code_dirty {'있음' if dirty else '없음'}), "
  f"config_hash `{cfg.config_hash}`, 코퍼스 {cfg.corpus_version} `{cfg.corpus_snapshot[:22]}…`")
w("- 설정: 7종 모두 effort low, temperature 생략(Claude는 원래 보내지 않음), 출력 상한 16000. B 분해는 참가자 모델이 각자 한다.")
w("- 정답 여부는 판정하지 않았다(정답표는 평가 담당이 봉인). 아래는 답변·인용·검색 결과·청크 원문만으로 재현 가능한 지표다.")
w(f"- 답변 상태는 문장 단위 규칙으로 가르고, 원문을 읽은 표본 감사로 확인한 {n_audit}행을 보정했다. 수치는 독립 재계산과 대조했다.\n")

w("## 1. 실행 완결성\n")
w("| 모델 | A 답변 행 | A 실패 | B 답변 행 | B 실패 | 다시 돌린 실패 시도 |")
w("|---|---|---|---|---|---|")
for m in models:
    row = []
    for k in ("A", "B"):
        rs = [S[k]["recs"].get((m, q)) for q in QIDS]
        row += [sum(1 for r in rs if r), sum(1 for r in rs if r and r["status"] == "crash")]
    fa = sum(1 for k in ("A", "B") for f in S[k]["fails"] if f.get("model") == m)
    w(f"| {m} | {row[0]}/40 | {row[1]} | {row[2]}/40 | {row[3]} | {fa} |")
w("")

w("## 2. 답변 상태 (대조군 제외 36문항: 답변 / 부분 기권 / 전체 기권)\n")
w("| 모델 | A | B | A 기권 문구 포함 | B 기권 문구 포함 | 대조군 기권 문구 포함 A / B (설명 덧붙임) |")
w("|---|---|---|---|---|---|")
for m in models:
    cells = []
    for k in ("A", "B"):
        c = Counter(S[k]["recs"][(m, q)]["status"] for q in NONCTL if (m, q) in S[k]["recs"])
        cells.append(f"{c['answer']} / {c['partial']} / {c['abstain']}" + (f" (+실패 {c['crash']})" if c["crash"] else ""))
    ph = [sum(1 for q in NONCTL if S[k]["recs"].get((m, q), {}).get("phrase")) for k in ("A", "B")]
    ctl = [sum(1 for q in CTL if S[k]["recs"].get((m, q), {}).get("phrase")) for k in ("A", "B")]
    ext = [sum(1 for q in CTL if S[k]["recs"].get((m, q), {}).get("extra_after_abstain")) for k in ("A", "B")]
    w(f"| {m} | {cells[0]} | {cells[1]} | {ph[0]} | {ph[1]} | {ctl[0]}/4 / {ctl[1]}/4 ({ext[0]} / {ext[1]}) |")
w("\n'기권 문구 포함'은 평가 담당의 자동 판정(문구 포함 여부)에 해당한다. 부분 답변도 여기에 잡힌다. "
  "대조군의 '설명 덧붙임'은 기권 문구 뒤에 문서에 무엇이 있고 없는지를 인용과 함께 적은 답이다(예: 'revision 5까지만 있고 6은 없음'). "
  "지어낸 내용인지는 4절 점검과 심판 채점으로 본다.\n")

w("## 3. 문항 분류(tier)별 전체 기권 (A / B)\n")
tiers = sorted({BENCH[q]["tier"] for q in NONCTL})
w("| 모델 | " + " | ".join(f"{t} ({sum(1 for q in NONCTL if BENCH[q]['tier'] == t)})" for t in tiers) + " |")
w("|---|" + "---|" * len(tiers))
for m in models:
    cells = []
    for t in tiers:
        qs = [q for q in NONCTL if BENCH[q]["tier"] == t]
        a = sum(1 for q in qs if S["A"]["recs"].get((m, q), {}).get("status") == "abstain")
        b = sum(1 for q in qs if S["B"]["recs"].get((m, q), {}).get("status") == "abstain")
        cells.append(f"{a} / {b}")
    w(f"| {m} | " + " | ".join(cells) + " |")
w("")

w("## 4. 근거·인용 (안전 점검)\n")
w("| 모델 | 맥락에 그대로 없는 식별자 A / B | 그중 코퍼스에도 없음(지어냄) A / B | 인용 오류 행 A / B | 주장 문장 인용률 A / B |")
w("|---|---|---|---|---|")
for m in models:
    cells = []
    for key in ("fab", "made", "dang", "cite"):
        vals = []
        for k in ("A", "B"):
            rs = [S[k]["recs"][(m, q)] for q in QIDS if (m, q) in S[k]["recs"] and S[k]["recs"][(m, q)]["status"] != "crash"]
            if key == "fab":
                vals.append(str(sum(len(r["fabricated"]) for r in rs)))
            elif key == "made":
                vals.append(str(sum(1 for r in rs for v in r["id_kinds"].values() if v == "코퍼스에도 없음")))
            elif key == "dang":
                vals.append(str(sum(1 for r in rs if r["dangling"])))
            else:
                u = sum(r["claim_units"] for r in rs); c = sum(r["claim_units_cited"] for r in rs)
                vals.append(f"{c / u:.0%}" if u else "-")
        cells.append(" / ".join(vals))
    w(f"| {m} | " + " | ".join(cells) + " |")
w("\n'맥락에 그대로 없는 식별자'는 답변 속 ID·이름(질문에 없던 것) 중 모델에 준 top-5 맥락에 글자 그대로 없는 것이다. "
  "아래처럼 나눈다: 더 긴 식별자의 일부(예: 맥락의 HandleChangeToMode에서 ChangeToMode만 씀), 대소문자 차이, 합성(맥락의 이름을 이어 붙임), 맥락 밖(코퍼스 다른 곳엔 있음 = 문서 밖 지식 사용), "
  "코퍼스에도 없음(지어냄). 맥락 안의 다른 식별자를 잘못 고른 오답은 이 점검으로 잡지 못한다.\n")
kinds = Counter(v for k in ("A", "B") for r in S[k]["recs"].values() for v in r["id_kinds"].values())
w("- 종류별 합계: " + ", ".join(f"{k} {n}" for k, n in kinds.most_common()))
for k in ("A", "B"):
    for (m, q), r in S[k]["recs"].items():
        for tok, kind in r["id_kinds"].items():
            if kind in ("맥락 밖(코퍼스엔 있음)", "코퍼스에도 없음"):
                w(f"- {kind}: {k} {m} {q} `{tok}`")
dl = [(k, m, q, S[k]["recs"][(m, q)]["dangling"]) for k in ("A", "B") for m in models for q in QIDS
      if (m, q) in S[k]["recs"] and S[k]["recs"][(m, q)]["dangling"]]
for k, m, q, d in dl:
    w(f"- 인용 오류: {k} {m} {q} → {', '.join(f'`{x}`' for x in d)}")
w("")

w("## 5. 토큰·비용·지연 (40문항 합계)\n")
w("| 모델 | 시스템 | 캐시 없는 입력 | 캐시 쓰기 | 캐시 읽기 | 출력 | 추론 토큰 | 비용 (캐시 중립) | 비용 (실청구) | 생성 지연 중앙값 |")
w("|---|---|---|---|---|---|---|---|---|---|")
tot_bill = tot_neu = 0.0
for m in models:
    for k in ("A", "B"):
        rs = [S[k]["recs"][(m, q)] for q in QIDS if (m, q) in S[k]["recs"]]
        if not rs:
            continue
        t = {c: sum(r["tokens"][c] for r in rs) for c in COLS}
        # 다시 돌린 실패 시도도 과금됐다(failed_attempts)
        for f in S[k]["fails"]:
            if f.get("model") == m:
                for c in COLS:
                    t[c] += f["tokens"][c]
        reason = sum(reasoning_tokens(S[k]["traces"].get((m, q), [])) for q in QIDS)
        b, n = cost(m, t), cost(m, t, neutral=True)
        tot_bill += b; tot_neu += n
        gen = statistics.median(r["lat"]["generate"] for r in rs) / 1000
        w(f"| {m} | {k} | {t['uncached_input']:,} | {t['cache_creation']:,} | {t['cache_read']:,} | {t['output']:,} | {reason:,} | "
          f"${n:.3f} | ${b:.3f} | {gen:.1f}s |")
w(f"\n**합계: 캐시 중립 ${tot_neu:.2f}, 실청구 ${tot_bill:.2f}** (모델별 공식 단가 적용, 과금된 실패 시도 포함). "
  "B 생성 지연에는 분해 호출 시간이 들어 있다(동결 스키마에 분해 칸이 없음). 실청구 비용은 실행 순서에 따른 캐시 적중에 좌우된다.\n")

w("## 6. System B 분해\n")
w("| 모델 | 하위질의 1 / 2 / 3 / 4+ | 분해 파싱 실패 | top-5가 A와 같은 문항 |")
w("|---|---|---|---|")
for m in models:
    subs = [S["B"]["traces"][(m, q)][-1].get("subqueries", []) for q in QIDS if S["B"]["traces"].get((m, q))]
    fb = sum(1 for q in QIDS if S["B"]["traces"].get((m, q)) and S["B"]["traces"][(m, q)][-1].get("decompose_fallback"))
    c = Counter(min(len(s), 4) for s in subs)
    same = sum(1 for q in QIDS if (m, q) in S["A"]["recs"] and (m, q) in S["B"]["recs"]
               and S["A"]["recs"][(m, q)]["top5"] == S["B"]["recs"][(m, q)]["top5"])
    w(f"| {m} | {c[1]} / {c[2]} / {c[3]} / {c[4]} | {fb} | {same}/40 |")
w("")

w("## 7. 검색 확신도와 전체 기권 (System A, 대조군 제외)\n")
w("재순위 1위 점수로 답변 문항과 전체 기권 문항을 가르는 정도(AUC, 1에 가까울수록 기권이 검색 확신도가 낮은 문항에 몰림). "
  "A의 top-5는 모델과 무관하게 같으므로, 모델마다 어떤 문항에서 기권했는지의 차이를 보여 준다.\n")
w("| 모델 | 답변 문항 1위 점수 중앙값 | 기권 문항 1위 점수 중앙값 | AUC |")
w("|---|---|---|---|")
for m in models:
    pos = [S["A"]["recs"][(m, q)]["top1"] for q in NONCTL if S["A"]["recs"].get((m, q), {}).get("status") == "answer"]
    neg = [S["A"]["recs"][(m, q)]["top1"] for q in NONCTL if S["A"]["recs"].get((m, q), {}).get("status") == "abstain"]
    a = auc(pos, neg)
    w(f"| {m} | {statistics.median(pos):.2f} (n={len(pos)}) | " + (f"{statistics.median(neg):.2f} (n={len(neg)})" if neg else "-")
      + f" | {a:.2f} |" if a is not None else f"| {m} | - | - | - |")
w("")

w("## 8. 연구 한계로 남길 것\n")
for s in [
    "기권 규칙(System A에서 시작해 팀 공통이 된 규칙)은 일부만 답할 수 있는 질문을 정하지 않는다. GPT 계열은 기권 문구만 답하는 경향이, "
    "Claude·DeepSeek·Kimi는 있는 부분만 답하는 경향이 있어 모델 간 순위 일부는 지시문 해석 차이를 반영한다.",
    "평가 담당의 자동 기권 판정(문구 포함 여부)은 부분 답변도 기권으로 잡는다. 위 2절에서 전체 기권과 문구 포함을 따로 보였다.",
    "effort는 7종 모두 low지만 실제 추론 토큰은 모델마다 크게 다르다(5절). '같은 추론 강도 설정'이지 '같은 추론 예산'이 아니다.",
    "DeepSeek-V4-Flash는 9/10에 V4.1 Flash로 교체되어 V4.1 Flash(`deepseek-flash`)로 실행했다.",
    "Kimi는 계정의 분당 요청 3회 제한 때문에 B에서 문항 사이 50초 간격으로 실행했다(지연 기록에는 넣지 않음).",
    "참가자 1회 실행이라 반복 간 흔들림은 아직 알 수 없다. 이번 실행은 effort low 테스트이며 본실험은 medium 예정이다.",
]:
    w(f"- {s}")

OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
OUT_JSON.write_text(json.dumps({k: {f"{m}|{q}": v for (m, q), v in S[k]["recs"].items()} for k in S}, ensure_ascii=False, indent=1),
                    encoding="utf-8")
print("\n".join(md))
