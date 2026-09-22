"""
rag_proto.run_eval — 질의셋 배치 실행

data/queries.jsonl → runs/<타임스탬프>/answers.jsonl + summary.json

명세서 §07. 이 단계에서 지표를 *채점*하지는 않는다. 지표가 나중에 계산될 수
있도록 원자료를 남기고, DoD 항목만 자동으로 점검한다.
루브릭 채점과 주장 단위 검증은 Phase 2 평가 스크립트의 몫이다.

실행:
    python -m rag_proto.run_eval
    python -m rag_proto.run_eval --fake-llm      # 검색은 실제, LLM만 가짜 (API 키 없을 때)
    python -m rag_proto.run_eval --fake          # 전부 가짜 (색인도 --fake 로 만들어야 함)
    python -m rag_proto.run_eval --tier identifier
    python -m rag_proto.run_eval --limit 3
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from .ask import Pipeline
from .check_queries import load_queries
from .config import load
from .s6_generate import ABSTAIN_PHRASE
from .schema import AnswerRecord, EvalQuery, QueryTier, find_dangling_citations

RUNS_DIR = Path("runs")


def arg_value(flag: str, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def select_queries(queries: list[EvalQuery]) -> list[EvalQuery]:
    tier = arg_value("--tier")
    if tier:
        queries = [q for q in queries if q.tier.value == tier]
    limit = arg_value("--limit")
    if limit:
        queries = queries[: int(limit)]
    return queries


def abstained(record: AnswerRecord) -> bool:
    return ABSTAIN_PHRASE in record.answer


def score_identifiers(query: EvalQuery, record: AnswerRecord) -> dict:
    """
    식별자 인용 정확도의 원자료.

    답변 본문으로 대조한다. identifiers_in_answer는 추출 정규식을 거치므로
    On, Off 같은 단일 단어 식별자가 빠진다. (check_queries가 경고하는 그 한계)
    """
    gold = query.gold_identifiers
    if not gold:
        return {"gold": 0, "hit": 0, "missed": [], "recall": None}
    hit = [g for g in gold if g in record.answer]
    return {
        "gold": len(gold),
        "hit": len(hit),
        "missed": sorted(set(gold) - set(hit)),
        "recall": round(len(hit) / len(gold), 3),
    }


def run(pipeline: Pipeline, queries: list[EvalQuery], pattern: str) -> list[dict]:
    rows: list[dict] = []
    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {q.qid} ({q.tier.value}) ...", end="", flush=True)
        started = time.perf_counter()
        try:
            record = pipeline.ask(q.question, qid=q.qid)
        except Exception as exc:  # 한 문항 실패가 전체를 멈추면 안 된다
            print(f" 실패: {type(exc).__name__}")
            rows.append(
                {
                    "query": q.model_dump(mode="json"),
                    "record": None,
                    "eval": {"crashed": True, "error": traceback.format_exc(limit=2)},
                }
            )
            continue

        dangling = find_dangling_citations(record, pattern)
        is_control = q.tier is QueryTier.CONTROL
        did_abstain = abstained(record)

        rows.append(
            {
                "query": q.model_dump(mode="json"),
                "record": record.model_dump(mode="json"),
                "eval": {
                    "crashed": False,
                    "dangling_citations": dangling,
                    "abstained": did_abstain,
                    # 대조군은 기권해야 통과, 나머지는 기권하면 실패
                    "control_ok": did_abstain if is_control else None,
                    "identifiers": score_identifiers(q, record),
                },
            }
        )
        print(f" {int((time.perf_counter() - started) * 1000)}ms")
    return rows


def summarize(rows: list[dict]) -> dict:
    ok = [r for r in rows if not r["eval"]["crashed"]]
    crashed = len(rows) - len(ok)

    dangling_total = sum(len(r["eval"]["dangling_citations"]) for r in ok)
    controls = [r for r in ok if r["query"]["tier"] == "control"]
    control_pass = sum(1 for r in controls if r["eval"]["control_ok"])

    # 대조군이 아닌데 기권한 문항 — 검색이 못 찾았거나 코퍼스에 답이 없다
    false_abstain = [
        r["query"]["qid"]
        for r in ok
        if r["query"]["tier"] != "control" and r["eval"]["abstained"]
    ]

    recalls = [
        r["eval"]["identifiers"]["recall"]
        for r in ok
        if r["eval"]["identifiers"]["recall"] is not None
    ]

    tok = {"uncached_input": 0, "cache_creation": 0, "cache_read": 0, "output": 0}
    latencies: list[int] = []
    for r in ok:
        for k in tok:
            tok[k] += r["record"]["tokens"][k]
        latencies.append(r["record"]["latency_ms"]["total"])

    latencies.sort()

    def pct(p: float) -> int:
        return latencies[min(int(len(latencies) * p), len(latencies) - 1)] if latencies else 0

    return {
        "total": len(rows),
        "ok": len(ok),
        "crashed": crashed,
        "dangling_citations": dangling_total,
        "control_total": len(controls),
        "control_pass": control_pass,
        "false_abstain": false_abstain,
        "identifier_recall_mean": round(sum(recalls) / len(recalls), 3) if recalls else None,
        "latency_ms": {"p50": pct(0.5), "p90": pct(0.9), "max": latencies[-1] if latencies else 0},
        "tokens": tok,
        "tokens_billable_input": round(
            tok["uncached_input"] + tok["cache_creation"] + tok["cache_read"] * 0.1, 1
        ),
    }


def print_report(summary: dict, rows: list[dict], fake: bool) -> None:
    if fake:
        print("\n!! 가짜 모드입니다. 답변 품질과 토큰은 무의미합니다.")

    s = summary
    print(f"\n{'─' * 52}")
    print(f"실행 {s['ok']}/{s['total']}건 성공, {s['crashed']}건 예외")
    print(f"지연 p50={s['latency_ms']['p50']}ms p90={s['latency_ms']['p90']}ms max={s['latency_ms']['max']}ms")
    t = s["tokens"]
    print(
        f"토큰 uncached={t['uncached_input']} cache_creation={t['cache_creation']} "
        f"cache_read={t['cache_read']} output={t['output']}"
    )
    print(f"     청구 환산 입력 {s['tokens_billable_input']}")
    if s["identifier_recall_mean"] is not None:
        print(f"식별자 재현율 평균 {s['identifier_recall_mean']}")

    print(f"\n{'─' * 52}")
    print("DoD 점검")
    checks = [
        ("20문항 예외 없이 응답", s["crashed"] == 0),
        ("dangling citation 0건", s["dangling_citations"] == 0),
        ("대조군 기권", s["control_pass"] == s["control_total"]),
        ("본문항 오기권 없음", not s["false_abstain"]),
        ("시연 1분 내", s["latency_ms"]["max"] < 60_000),
    ]
    for label, passed in checks:
        print(f"  {'통과' if passed else '실패'}  {label}")

    if s["false_abstain"]:
        print(f"\n  오기권 문항: {s['false_abstain']}")
        print("  → 검색이 근거를 못 찾았거나 코퍼스에 답이 없습니다")

    bad = [r for r in rows if not r["eval"]["crashed"] and r["eval"]["dangling_citations"]]
    for r in bad[:3]:
        print(f"\n  {r['query']['qid']} dangling: {r['eval']['dangling_citations']}")

    weak = [
        r
        for r in rows
        if not r["eval"]["crashed"]
        and (r["eval"]["identifiers"]["missed"])
    ]
    if weak:
        print(f"\n식별자 누락 문항 {len(weak)}건")
        for r in weak[:5]:
            print(f"  {r['query']['qid']}: {r['eval']['identifiers']['missed']}")


def write_run(rows: list[dict], summary: dict, cfg) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RUNS_DIR / f"{stamp}_{cfg.config_hash}"
    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "answers.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            if r["record"]:
                f.write(json.dumps(r["record"], ensure_ascii=False) + "\n")

    (out_dir / "eval.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.json").write_text(
        json.dumps(
            {
                **summary,
                "corpus_commit": cfg.commit,
                "corpus_phase": cfg.phase.value,
                "corpus_snapshot": cfg.corpus_snapshot,
                "corpus_version": cfg.corpus_version,
                "config_hash": cfg.config_hash,
                "model": cfg.pipeline["generation"]["model"],
                "ran_at": stamp,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    fake = "--fake" in sys.argv
    fake_llm = fake or "--fake-llm" in sys.argv
    cfg = load()
    queries = select_queries(load_queries())
    if not queries:
        print("실행할 질의가 없습니다.")
        return 1

    pipeline = Pipeline(cfg, fake=fake, fake_llm=fake_llm)
    pattern = cfg.pipeline["generation"]["citation_pattern"]

    rows = run(pipeline, queries, pattern)
    summary = summarize(rows)
    out_dir = write_run(rows, summary, cfg)
    print_report(summary, rows, pipeline.fake)

    print(f"\n{out_dir}/ 기록 완료")
    return 0 if summary["crashed"] == 0 and summary["dangling_citations"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
