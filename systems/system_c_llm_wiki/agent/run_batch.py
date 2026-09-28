# -*- coding: utf-8 -*-
"""
LLM Wiki 배치 평가 러너 (System C) — run_batch.py
===================================================

benchmark/questions_v1.jsonl 의 질문을 에이전트로 실행하고
팀 공용 AnswerRecord v0.3 형식으로 JSONL을 출력한다.

사용법 (리포 루트에서):
    set -a; . ./.env.local; set +a

    # luna 위키 실행
    python3 systems/system_c_llm_wiki/agent/run_batch.py \\
        --wiki-root systems/system_c_llm_wiki/wiki \\
        --wiki-label luna \\
        --output runs/wiki_luna_run1.jsonl

    # sol 위키 실행 (비교용)
    python3 systems/system_c_llm_wiki/agent/run_batch.py \\
        --wiki-root systems/system_c_llm_wiki/wiki_sol \\
        --wiki-label sol \\
        --output runs/wiki_sol_run1.jsonl

    # 두 결과 비교
    python3 systems/system_c_llm_wiki/agent/run_batch.py --compare \\
        runs/wiki_luna_run1.jsonl runs/wiki_sol_run1.jsonl
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# run_agent.py 가 같은 디렉토리에 있다
sys.path.insert(0, str(Path(__file__).parent))
from run_agent import run_agent

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
SCHEMA_VERSION = "0.3"
CORPUS_COMMIT = "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"
CORPUS_PHASE = "integrated"
SSOT = CORPUS_COMMIT  # 동일


def _config_hash(cfg: dict) -> str:
    canonical = json.dumps(cfg, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _to_answer_record(
    q: dict,
    agent_result: dict,
    *,
    model: str,
    run: int,
    cfg_hash: str,
    error: str | None = None,
) -> dict:
    """
    run_agent() 결과 → AnswerRecord v0.3 dict.

    OpenAI token 매핑:
      uncached_input = prompt_tokens - cache_read  (OpenAI는 cache 포함해서 보고)
      cache_creation = cache_write
      cache_read     = cache_read
      output         = output_tokens
    """
    tu = agent_result.get("token_usage", {})
    prompt = tu.get("prompt_tokens", 0)
    cache_read = tu.get("cache_read", 0)
    cache_write = tu.get("cache_write", 0)
    output = tu.get("output_tokens", 0)

    return {
        "schema_version": SCHEMA_VERSION,
        "qid": q["query_id"],
        "model": model,
        "run": run,
        "system": "wiki",
        "query_mode": "simple",
        "question": q["question"],
        "answer": agent_result.get("answer", ""),
        "citations": [],   # wiki는 retrieved.wiki_pages 사용
        "retrieved": {
            "bm25": [],
            "vector": [],
            "fused": [],
            "reranked": [],
            "wiki_pages": agent_result.get("retrieved", {}).get("wiki_pages", []),
        },
        "identifiers_in_answer": [],  # 채점 스크립트가 채운다
        "latency_ms": {
            "retrieve": 0,
            "rerank": 0,
            "generate": agent_result.get("turns", 0) * 0,  # 미측정
            "total": 0,
        },
        "tokens": {
            "uncached_input": max(0, prompt - cache_read),
            "cache_creation": cache_write,
            "cache_read": cache_read,
            "output": output,
        },
        "cited_pages": agent_result.get("cited_pages", []),  # system-c 전용 보조 필드
        "turns": agent_result.get("turns", 0),               # system-c 전용 보조 필드
        "corpus_commit": CORPUS_COMMIT,
        "corpus_phase": CORPUS_PHASE,
        "corpus_snapshot": None,
        "corpus_version": None,
        "config_hash": cfg_hash,
        "error": error,
    }


# ---------------------------------------------------------------------------
# 배치 실행
# ---------------------------------------------------------------------------

def run_batch(
    questions_path: str,
    wiki_root: str,
    wiki_label: str,
    output_path: str | None,
    model: str,
    run: int,
    max_turns: int,
    verbose: bool,
    limit: int | None,
) -> list[dict]:
    questions = []
    with open(questions_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    if limit:
        questions = questions[:limit]

    cfg = {
        "wiki_root": wiki_root,
        "wiki_label": wiki_label,
        "agent_model": model,
        "max_turns": max_turns,
    }
    cfg_hash = _config_hash(cfg)

    # WIKI_ROOT를 run_agent가 읽도록 환경에 반영
    # run_agent 는 WIKI_ROOT 전역을 쓰므로 동적으로 패치
    import run_agent as _ra
    original_wiki_root = _ra.WIKI_ROOT
    _ra.WIKI_ROOT = Path(wiki_root)

    records = []
    out_f = open(output_path, "w", encoding="utf-8") if output_path else None

    try:
        for i, q in enumerate(questions, 1):
            qid = q["query_id"]
            question = q["question"]
            print(
                f"[{i}/{len(questions)}] {qid} ...",
                end=" ",
                flush=True,
                file=sys.stderr,
            )
            t0 = time.time()
            error = None
            try:
                result = run_agent(query=question, max_turns=max_turns, verbose=verbose, model=model)
            except Exception as e:
                result = {
                    "answer": "",
                    "retrieved": {"wiki_pages": []},
                    "cited_pages": [],
                    "turns": 0,
                    "token_usage": {},
                }
                error = f"{e.__class__.__name__}: {e}"

            elapsed = time.time() - t0
            record = _to_answer_record(
                q, result,
                model=model,
                run=run,
                cfg_hash=cfg_hash,
                error=error,
            )
            records.append(record)

            status = "OK" if not error else f"ERR({error[:40]})"
            print(
                f"{status} turns={record['turns']} "
                f"tokens={record['tokens']['uncached_input']+record['tokens']['cache_read']} "
                f"({elapsed:.1f}s)",
                file=sys.stderr,
            )

            line = json.dumps(record, ensure_ascii=False)
            if out_f:
                out_f.write(line + "\n")
                out_f.flush()
            else:
                print(line)

    finally:
        _ra.WIKI_ROOT = original_wiki_root
        if out_f:
            out_f.close()

    ok = sum(1 for r in records if not r["error"])
    err = len(records) - ok
    total_tokens = sum(
        r["tokens"]["uncached_input"] + r["tokens"]["cache_read"]
        for r in records
    )
    print(
        f"\n[배치 완료] wiki={wiki_label} model={model} "
        f"ok={ok} err={err} 총토큰={total_tokens}",
        file=sys.stderr,
    )
    return records


# ---------------------------------------------------------------------------
# 비교 리포트
# ---------------------------------------------------------------------------

def compare(paths: list[str]):
    datasets = {}
    for p in paths:
        label = Path(p).stem
        records = {}
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    records[r["qid"]] = r
        datasets[label] = records

    labels = list(datasets.keys())
    all_qids = sorted(set(qid for d in datasets.values() for qid in d))

    print(f"\n{'QID':<22} " + "  ".join(f"{'turns_'+l:<12} {'in_'+l:<10}" for l in labels))
    print("-" * 80)

    for qid in all_qids:
        parts = []
        for l in labels:
            r = datasets[l].get(qid)
            if r:
                t = r.get("turns", "-")
                inp = r["tokens"]["uncached_input"] + r["tokens"]["cache_read"]
                parts.append(f"{str(t):<12} {str(inp):<10}")
            else:
                parts.append(f"{'N/A':<12} {'N/A':<10}")
        print(f"{qid:<22} " + "  ".join(parts))

    # 요약
    print("\n[요약]")
    for l in labels:
        recs = list(datasets[l].values())
        ok = [r for r in recs if not r.get("error")]
        avg_turns = sum(r.get("turns", 0) for r in ok) / len(ok) if ok else 0
        avg_tokens = sum(
            r["tokens"]["uncached_input"] + r["tokens"]["cache_read"]
            for r in ok
        ) / len(ok) if ok else 0
        errors = sum(1 for r in recs if r.get("error"))
        print(
            f"  {l}: {len(ok)}/{len(recs)} 성공 | "
            f"평균 {avg_turns:.1f}턴 | "
            f"평균 {avg_tokens:.0f}토큰 | "
            f"오류 {errors}건"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 배치 평가 러너")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="비교 모드: 두 JSONL 파일을 비교한다 (배치 실행 없음)",
    )
    parser.add_argument("files", nargs="*", help="비교 모드: JSONL 파일 경로 2개")
    parser.add_argument(
        "--questions",
        default="benchmark/questions_v1.jsonl",
        help="질문셋 JSONL (기본: benchmark/questions_v1.jsonl)",
    )
    parser.add_argument(
        "--wiki-root",
        default="systems/system_c_llm_wiki/wiki",
        help="위키 루트 디렉토리",
    )
    parser.add_argument(
        "--wiki-label",
        default="",
        help="위키 레이블 (출력 파일명 등에 사용, 예: luna / sol)",
    )
    parser.add_argument("--output", help="결과 JSONL 저장 경로")
    parser.add_argument(
        "--model",
        default=None,
        help="에이전트 모델 (기본: WIKI_AGENT_MODEL 또는 gpt-5.6-luna)",
    )
    parser.add_argument("--run", type=int, default=1, help="실행 회차 (기본 1)")
    parser.add_argument("--max-turns", type=int, default=30, help="최대 턴 수")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=None, help="테스트용: 첫 N개 문항만"
    )
    args = parser.parse_args()

    if args.compare:
        if len(args.files) < 2:
            print("[오류] --compare 모드는 JSONL 파일 2개가 필요합니다.", file=sys.stderr)
            sys.exit(1)
        compare(args.files)
        return

    model = (
        args.model
        or os.environ.get("WIKI_AGENT_MODEL")
        or os.environ.get("WIKI_COMPILER_MODEL")
        or "gpt-5.6-luna"
    )

    run_batch(
        questions_path=args.questions,
        wiki_root=args.wiki_root,
        wiki_label=args.wiki_label or Path(args.wiki_root).name,
        output_path=args.output,
        model=model,
        run=args.run,
        max_turns=args.max_turns,
        verbose=args.verbose,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
