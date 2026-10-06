"""심판자 LLM 채점 — 구독 계정으로 자동 실행 (API 키 불필요)

심판
  claude : Claude Code 헤드리스 (`claude -p`, Claude 구독)   기본 모델 claude-opus-5-5
           Claude 데스크톱 앱에 든 최신 claude.exe 사용. 처음 한 번 터미널에서 로그인 필요
  gpt    : ChatGPT 앱 내장 Codex CLI (`codex exec`, ChatGPT 구독) 기본 모델 gpt-6-astra

원칙
  - 한 답변 = 한 번의 독립 호출 (대화창 누적 없음 → 앞 답변이 판정에 영향 X)
  - 블라인드: 시스템(A/B/C)·모델 이름을 프롬프트에 넣지 않고, 무작위 item_id·무작위 순서
  - 프롬프트는 github_upload/evaluation/judges/judge_prompt_v1.md 의 코드블록을 그대로 사용 (sha 기록)
  - 도구 없음: claude --tools "" --safe-mode / codex -s read-only, 빈 임시 폴더에서 실행
  - 이어하기: 결과 파일에 이미 있는 (item_id, judge)는 건너뜀

입력
  answers : adapt_records.py 출력 jsonl (여러 개 가능)
  queries : eval/queries/test_v1.jsonl (정답 메모 포함, 비공개)

사용
  python eval/run_judge.py results/raw/*.jsonl --judge claude --out results/judged/claude.jsonl
  python eval/run_judge.py results/raw/*.jsonl --judge gpt    --out results/judged/gpt.jsonl
  python eval/run_judge.py ... --dry-run 1        # 프롬프트만 출력
  python eval/run_judge.py ... --limit 5          # 5건만 시험
  python eval/run_judge.py ... --sample 0.1 --out results/judged/claude_rejudge.jsonl   # 10% 재채점(일관성)
"""
import argparse, glob, hashlib, json, os, pathlib, random, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT_FILE = ROOT / "evaluation" / "judges" / "judge_prompt_v1.md"
CORPUS_RAW = pathlib.Path(r"C:\Users\jjong\Claude\ow\project\corpus\raw\connectedhomeip")
WIKI_ROOT = pathlib.Path(r"C:\Users\jjong\Claude\ow\wiki_c\systems\system_c_llm_wiki\wiki")
DEFAULT_MODEL = {"claude": "claude-opus-5-5", "gpt": "gpt-6-astra"}
EFFORT = "medium"         # 두 심판의 추론 강도를 같게 고정 (Codex 사용자 설정·Claude 기본값에 휘둘리지 않게)
SYSTEM = "당신은 채점자입니다. 도구를 쓰지 말고, 요청된 JSON 하나만 출력하세요."
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["correctness", "groundedness", "structural_integrity", "cross_document_synthesis",
                 "hallucination", "abstained", "reason"],
    "properties": {
        "correctness": {"type": "string", "enum": ["correct", "partial", "incorrect"]},
        "groundedness": {"type": "integer", "minimum": 0, "maximum": 2},
        "structural_integrity": {"type": "integer", "minimum": 0, "maximum": 2},
        "cross_document_synthesis": {"type": ["integer", "string"]},
        "hallucination": {"type": "boolean"},
        "abstained": {"type": "boolean"},
        "reason": {"type": "string"},
    },
}
EXCERPT_FULL = 8000      # 이보다 짧은 문서는 통째로
EXCERPT_WIN = 700        # 긴 문서는 답변 속 식별자·이름 주변만
EXCERPT_MAX = 6
CHUNKS = {}              # --chunks: RAG 청크 본문 (chunk_id → text). 있으면 파일 대신 청크 본문을 인용 발췌로 쓴다
WIKI_FULL = False        # --wiki-root 지정 시 True: 위키 페이지는 길이와 무관하게 전체를 넣는다
                         # (원칙: 심판은 참가자가 실제로 읽은 단위를 통째로 본다 — A·B 청크, C 위키 페이지)


def template():
    t = PROMPT_FILE.read_text(encoding="utf-8")
    m = re.search(r"```\n(.*?)```", t, re.S)
    return m.group(1)


def find_codex():
    hits = sorted(glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe")), key=os.path.getmtime)
    if not hits:
        sys.exit("codex.exe 를 찾지 못함 (ChatGPT/Codex 앱 설치 확인)")
    return hits[-1]


def find_claude():
    """Claude 데스크톱 앱에 든 최신 Claude Code → 없으면 PATH의 claude"""
    hits = sorted(glob.glob(os.path.expandvars(r"%APPDATA%\Claude\claude-code\*\claude.exe")),
                  key=lambda p: [int(x) for x in re.findall(r"\d+", pathlib.Path(p).parent.name)])
    return hits[-1] if hits else "claude"


def resolve(path):
    p = path.split("@")[0]
    for base, cand in ((WIKI_ROOT, p if p.endswith(".md") else p + ".md"), (CORPUS_RAW, p)):
        f = base / cand
        if f.is_file():
            return f
    return None


def excerpt(path, answer):
    f = resolve(path)
    if f is None:
        return f"<{path}: 파일을 찾지 못함>"
    txt = f.read_text(encoding="utf-8", errors="replace")
    if WIKI_FULL and f.is_relative_to(WIKI_ROOT):       # C 위키 페이지: 자르지 않고 전체
        return txt
    # 파일 맨 앞 라이선스 주석(XML <!-- -->, C++ /* */) 제거 — 판정과 무관하고 토큰만 씀
    txt = re.sub(r"\A(\s*<\?xml[^>]*\?>)?\s*<!--.*?Copyright.*?-->", r"\1", txt, count=1, flags=re.S)
    txt = re.sub(r"\A\s*/\*.*?Copyright.*?\*/", "", txt, count=1, flags=re.S).strip()
    if len(txt) <= EXCERPT_FULL:
        return txt
    keys = set(re.findall(r"0x[0-9A-Fa-f]{2,4}", answer)) | set(re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", answer))
    spans = []
    for k in sorted(keys):
        for m in re.finditer(re.escape(k), txt):
            spans.append((max(m.start() - EXCERPT_WIN, 0), min(m.end() + EXCERPT_WIN, len(txt))))
            break
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    if not merged:
        return txt[:EXCERPT_FULL] + "\n…(이하 생략)"
    return "\n…\n".join(txt[s:e] for s, e in merged[:EXCERPT_MAX])


def build_items(answer_files, queries, run, seed):
    qs = {q["query_id"]: q for q in map(json.loads, open(queries, encoding="utf-8"))}
    items = []
    for fpath in answer_files:
        for line in open(fpath, encoding="utf-8"):
            a = json.loads(line)
            q = qs.get(a["query_id"])
            if not q or q.get("scoring") == "l1":
                continue
            if run is not None and a.get("run") not in (run, None):
                continue
            src = f"{a['query_id']}|{a.get('system')}|{a.get('model')}|{a.get('run')}"
            iid = hashlib.sha256(f"{seed}|{src}".encode()).hexdigest()[:12]
            items.append({"item_id": iid, "src": src, "q": q, "a": a})
    random.Random(seed).shuffle(items)
    return items


def cited_text(k, v, a):
    cid = (a.get("cited_chunks") or {}).get(k)
    if cid and cid in CHUNKS:
        return CHUNKS[cid]
    return excerpt(v, a["answer_text"])


def render(tpl, q, a):
    ex = "\n\n".join(f"[{k}] {v}\n{cited_text(k, v, a)}" for k, v in (a.get("cited_sources") or {}).items()) \
        or "(인용 없음)"
    return (tpl.replace("{question}", q["question_ko"]).replace("{gold_answer}", q["gold_answer"])
            .replace("{gold_note}", q.get("gold_note", "")).replace("{answer_text}", a["answer_text"])
            .replace("{cited_excerpts}", ex))


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        raise ValueError("JSON 없음")
    d = json.loads(m.group(0))
    missing = [k for k in SCHEMA["required"] if k not in d]
    if missing:
        raise ValueError(f"필드 누락 {missing}")
    return d


def call_claude(prompt, model, workdir, exe="claude"):
    r = subprocess.run([exe, "-p", "--model", model, "--effort", EFFORT, "--tools", "", "--safe-mode", "--no-session-persistence",
                        "--output-format", "json", "--system-prompt", SYSTEM],
                       input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=workdir, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr[-500:] or r.stdout[-500:])
    out = json.loads(r.stdout)
    return out.get("result", ""), {"usage": out.get("usage"), "cost_usd": out.get("total_cost_usd")}


def call_codex(prompt, model, workdir, codex):
    sch, last = pathlib.Path(workdir) / "schema.json", pathlib.Path(workdir) / f"last_{time.time_ns()}.txt"
    sch.write_text(json.dumps(SCHEMA), encoding="utf-8")
    r = subprocess.run([codex, "exec", "-m", model, "-c", f"model_reasoning_effort=\"{EFFORT}\"", "-s", "read-only", "--ephemeral", "--skip-git-repo-check",
                        "--output-schema", str(sch), "-o", str(last), "-"],
                       input=prompt, capture_output=True, text=True, encoding="utf-8", cwd=workdir, timeout=900)
    if r.returncode:
        raise RuntimeError(r.stderr[-500:] or r.stdout[-500:])
    return last.read_text(encoding="utf-8"), {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("answers", nargs="+")
    ap.add_argument("--queries", default=str(ROOT / "eval" / "queries" / "test_v1.jsonl"))
    ap.add_argument("--judge", choices=["claude", "gpt"], required=True)
    ap.add_argument("--model")
    ap.add_argument("--run", type=int, default=1, help="심판할 반복 회차 (기본 1). 0이면 전부")
    ap.add_argument("--seed", type=int, default=20260926)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--dry-run", type=int, metavar="N", help="프롬프트 N개만 출력하고 종료")
    ap.add_argument("--sample", type=float, help="일관성 재채점용: 대상 중 이 비율만 무작위 추출 (예 0.1). 다른 --out 파일로 실행")
    ap.add_argument("--chunks", help="RAG chunks.jsonl (chunk_id, text) — 태이님 data/chunks.jsonl")
    ap.add_argument("--wiki-root", help="C 인용 페이지를 읽을 위키 폴더 (기본: WIKI_ROOT). 예: .../wiki_c3/systems/system_c_llm_wiki/wiki-c3")
    a = ap.parse_args()
    global WIKI_ROOT, WIKI_FULL
    if a.wiki_root:
        WIKI_ROOT, WIKI_FULL = pathlib.Path(a.wiki_root), True
        if not WIKI_ROOT.is_dir():
            sys.exit(f"--wiki-root 폴더 없음: {WIKI_ROOT}")
    if a.chunks:
        for l in open(a.chunks, encoding="utf-8"):
            c = json.loads(l)
            CHUNKS[c["chunk_id"]] = c.get("text") or c.get("content") or ""

    files = [f for p in a.answers for f in (glob.glob(p) or [p])]
    items = build_items(files, a.queries, None if a.run == 0 else a.run, a.seed)
    if a.sample:
        items = sorted(items, key=lambda it: hashlib.sha256(f"resample|{it['item_id']}".encode()).hexdigest())
        items = items[: max(1, round(len(items) * a.sample))]
    tpl = template()
    tpl_sha = hashlib.sha256(tpl.encode()).hexdigest()[:12]
    model = a.model or DEFAULT_MODEL[a.judge]
    if a.dry_run is not None:
        for it in items[:a.dry_run]:
            print(f"===== item {it['item_id']} =====\n{render(tpl, it['q'], it['a'])}")
        print(f"(심판 대상 {len(items)}건)")
        return

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for l in open(out, encoding="utf-8"):
            r = json.loads(l)
            if r.get("verdict"):
                done.add(r["item_id"])
    todo = [it for it in items if it["item_id"] not in done][: a.limit]
    print(f"심판 {a.judge}/{model}  대상 {len(items)}  완료 {len(done)}  이번 {len(todo)}  prompt {tpl_sha}  wiki {WIKI_ROOT}")
    codex = find_codex() if a.judge == "gpt" else None
    claude_exe = find_claude() if a.judge == "claude" else None
    work = tempfile.mkdtemp(prefix="judge_")

    def one(it):
        prompt = render(tpl, it["q"], it["a"])
        t0 = time.time()
        rec = {"item_id": it["item_id"], "query_id": it["q"]["query_id"], "judge": a.judge, "judge_model": model, "effort": EFFORT,
               "prompt_sha": tpl_sha, "wiki_root": str(WIKI_ROOT),
               "wiki_excerpt": "full" if WIKI_FULL else "window", "src": it["src"], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        for attempt in range(3):
            try:
                raw, meta = call_claude(prompt, model, work, claude_exe) if a.judge == "claude" else call_codex(prompt, model, work, codex)
                rec.update(verdict=parse(raw), raw=raw, meta=meta, seconds=round(time.time() - t0, 1), error=None)
                return rec
            except Exception as e:                      # 사용 한도·일시 오류 → 잠시 뒤 재시도
                rec.update(verdict=None, error=str(e)[:500])
                time.sleep(20 * (attempt + 1))
        return rec

    ok = bad = 0
    with out.open("a", encoding="utf-8") as fp, ThreadPoolExecutor(a.workers) as ex:
        for fut in as_completed([ex.submit(one, it) for it in todo]):
            r = fut.result()
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")
            fp.flush()
            ok, bad = ok + (r["verdict"] is not None), bad + (r["verdict"] is None)
            v = r["verdict"] or {}
            print(f"  {r['item_id']} {r['query_id']:16} {v.get('correctness', 'ERR'):9} {r.get('error') or ''}"[:160])
    print(f"완료 {ok}  실패 {bad}  → {out}")


if __name__ == "__main__":
    main()
