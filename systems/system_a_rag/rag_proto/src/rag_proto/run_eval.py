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

본실험 (참가자 LLM × 반복, configs/participants.yaml):
    python -m rag_proto.run_eval --smoke                          # 모델마다 1회 호출로 키·ID 확인
    python -m rag_proto.run_eval --participants all --runs 3 \\
        --questions ../../../benchmark/questions_v1.jsonl         # 7 × 3 × 40 = 840건
    python -m rag_proto.run_eval --participants all --runs 3 \\
        --questions ... --resume runs/<디렉터리>                    # 끊긴 지점부터 이어서
    python -m rag_proto.run_eval --participants claude-sonnet-5 --runs 1 --limit 2 --questions ...
"""

from __future__ import annotations

import json
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from .ask import Pipeline
from .check_queries import QUERIES_PATH, load_queries
from .config import CONFIG_DIR, PARTICIPANTS_FILE, load, load_participants
from .s5_retrieve import CachedRetriever, Retriever
from .s6_generate import ABSTAIN_PHRASE, make_client
from .schema import (
    AnswerRecord,
    EvalQuery,
    QueryTier,
    SystemName,
    TokenUsage,
    find_dangling_citations,
)

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

    단순 부분 문자열(`g in answer`)로 대조하면 gold "On"이 "OnOff"나
    "OnWithTimedOff" 내부에 있어도 hit으로 잡혀 재현율이 과대 계상된다.
    \b 단어 경계로 정확히 대조한다 (hex ID·CamelCase·단일 단어 전부 커버).
    """
    gold = query.gold_identifiers
    if not gold:
        return {"gold": 0, "hit": 0, "missed": [], "recall": None}
    hit = [g for g in gold if re.search(rf"\b{re.escape(g)}\b", record.answer)]
    return {
        "gold": len(gold),
        "hit": len(hit),
        "missed": sorted(set(gold) - set(hit)),
        "recall": round(len(hit) / len(gold), 3),
    }


def _error_record(pipeline: Pipeline, q: EvalQuery, exc: Exception, run: int) -> AnswerRecord:
    """
    실패한 문항도 answers.jsonl에 한 줄 남긴다(박종원 answer_format.md 요구사항).
    이전엔 record=None으로 두고 write_run()이 통째로 건너뛰어 실패 문항이
    채점 대상에서 조용히 사라졌다.
    """
    cfg = pipeline.cfg
    return AnswerRecord(
        qid=q.qid,
        model=getattr(pipeline.client, "name", None),
        run=run,
        system=SystemName.RAG,
        query_mode=pipeline.query_mode,
        question=q.question,
        answer="",
        # 거절·잘림처럼 이미 과금된 실패는 GenerationError가 usage를 싣고 온다
        tokens=getattr(exc, "usage", None) or TokenUsage(),
        corpus_commit=cfg.commit,
        corpus_phase=cfg.phase,
        corpus_snapshot=cfg.corpus_snapshot,
        corpus_version=cfg.corpus_version,
        config_hash=cfg.config_hash,
        error=f"{type(exc).__name__}: {exc}",
    )


def run(
    pipeline: Pipeline,
    queries: list[EvalQuery],
    pattern: str,
    run_no: int = 1,
    sink=None,
    label: str = "",
) -> list[dict]:
    """sink가 주어지면 행이 만들어지는 즉시 sink(row)를 호출한다(배치 실행의 즉시 기록용)."""
    rows: list[dict] = []
    for i, q in enumerate(queries, 1):
        print(f"{label}[{i}/{len(queries)}] {q.qid} ({q.tier.value}) ...", end="", flush=True)
        started = time.perf_counter()
        try:
            record = pipeline.ask(q.question, qid=q.qid, run=run_no)
        except Exception as exc:  # 한 문항 실패가 전체를 멈추면 안 된다
            print(f" 실패: {type(exc).__name__}: {exc}")
            row = {
                "query": q.model_dump(mode="json"),
                "record": _error_record(pipeline, q, exc, run_no).model_dump(mode="json"),
                "eval": {"crashed": True, "error": traceback.format_exc(limit=2)},
            }
            rows.append(row)
            if sink:
                sink(row)
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
        if sink:
            sink(rows[-1])
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


def dod_checks(summary: dict, expected_total: int | None) -> list[tuple[str, bool]]:
    """
    DoD 5개 항목. print_report와 main()의 종료 코드가 같은 판정을 보도록
    한 곳에서 계산한다 (예전엔 화면 출력만 5개를 보고 종료 코드는 2개만 봤다).

    expected_total이 None이면 --limit/--tier로 부분 실행된 것이므로 "문항
    예외 없이 응답"은 실제 실행한 개수 기준으로만 판정하고 라벨에 부분
    실행임을 표시한다 — 20문항을 다 돌린 것처럼 보이면 안 된다.
    """
    s = summary
    if expected_total is None:
        count_label = f"{s['total']}문항(부분 실행) 예외 없이 응답"
        count_ok = s["crashed"] == 0
    else:
        count_label = f"{expected_total}문항 예외 없이 응답"
        count_ok = s["crashed"] == 0 and s["total"] == expected_total

    return [
        (count_label, count_ok),
        ("dangling citation 0건", s["dangling_citations"] == 0),
        ("대조군 기권", s["control_pass"] == s["control_total"]),
        ("본문항 오기권 없음", not s["false_abstain"]),
        ("시연 1분 내", s["latency_ms"]["max"] < 60_000),
    ]


def print_report(summary: dict, rows: list[dict], fake: bool, expected_total: int | None) -> None:
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
    for label, passed in dod_checks(summary, expected_total):
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


# --------------------------------------------------------------------------
# 본실험 배치: 참가자 LLM × 반복 회차 × 문항
# --------------------------------------------------------------------------

def select_participants(all_participants: list[dict], spec: str | None) -> list[dict]:
    if spec in (None, "", "all"):
        return all_participants
    names = [s.strip() for s in spec.split(",") if s.strip()]
    by_name = {p["model"]: p for p in all_participants}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise SystemExit(f"participants.yaml에 없는 모델: {missing}")
    return [by_name[n] for n in names]


def smoke_test(cfg, participants: list[dict]) -> int:
    """참가자마다 1회 짧게 호출해 모델 ID·키·파라미터 오류를 본실험 전에 잡는다(검색 모델은 안 띄운다)."""
    failures = 0
    for p in participants:
        try:
            client = make_client(cfg, participant=p)
            text, usage = client.complete("Reply with exactly: OK", "ping")
            print(f"  OK    {p['model']:<28} {text.strip()[:30]!r}  tokens={usage.model_dump()}")
            # 제공자·게이트웨이마다 usage 필드 의미가 달라 4열 매핑이 맞는지 원본으로 확인한다
            print(f"        원본 usage: {getattr(client, 'last_raw_usage', None)}")
        except Exception as exc:
            failures += 1
            print(f"  실패  {p['model']:<28} {type(exc).__name__}: {exc}")
    return 1 if failures else 0


def _is_retryable(rec: dict) -> bool:
    # 크래시 행(답변 없음 + error)만 다시 돈다. dangling citation은 답변이 있는
    # 정상 생성이라 다시 돌리면 돈만 더 쓰고 결과가 바뀐다.
    return bool(rec.get("error")) and not rec.get("answer")


def _load_done(answers_path: Path) -> set[tuple[str, str, int]]:
    """
    이어하기용. 이미 성공한 (qid, model, run)을 돌려주고, 크래시 행은 파일에서
    지운다(다시 돌린 결과와 중복되면 채점 스크립트가 같은 문항을 두 번 센다).
    """
    if not answers_path.exists():
        return set()
    kept: list[str] = []
    done: set[tuple[str, str, int]] = set()
    for line in answers_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if _is_retryable(rec):
            continue
        kept.append(line)
        done.add((rec["qid"], rec["model"], rec["run"]))
    answers_path.write_text("".join(line + "\n" for line in kept), encoding="utf-8")
    return done


def summarize_batch(answers_path: Path) -> dict:
    """answers.jsonl 전체(이어하기로 여러 번 나눠 돈 것 포함) 기준 모델별 집계. 토큰은 4열 그대로."""
    per: dict[str, dict] = {}
    for line in answers_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        s = per.setdefault(
            rec["model"],
            {"answers": 0, "errors": 0, "tokens": dict.fromkeys(TokenUsage.model_fields, 0), "_lat": []},
        )
        s["answers"] += 1
        if _is_retryable(rec):
            s["errors"] += 1
        for k in s["tokens"]:
            s["tokens"][k] += rec["tokens"][k]
        s["_lat"].append(rec["latency_ms"]["total"])
    for s in per.values():
        lat = sorted(s.pop("_lat"))
        s["latency_ms"] = {"p50": lat[len(lat) // 2] if lat else 0, "max": lat[-1] if lat else 0}
    return per


def run_batch(
    cfg,
    questions: list[EvalQuery],
    participants: list[dict],
    runs: int,
    out_dir: Path,
    pipeline_factory,
    retriever,
    fake_llm: bool = False,
) -> dict:
    """
    참가자 LLM마다 client만 바꿔 끼우고 retriever(CachedRetriever)는 공유한다.
    답변은 한 건씩 즉시 기록한다 — 840건 도중에 끊겨도 이미 과금된 답변을 잃지 않고
    --resume으로 이어서 돈다. pipeline_factory(client, retriever)로 System B도 재사용한다.
    """
    pattern = cfg.pipeline["generation"]["citation_pattern"]
    out_dir.mkdir(parents=True, exist_ok=True)
    answers_path = out_dir / "answers.jsonl"
    done = _load_done(answers_path)
    # 어떤 참가자 설정으로 돌렸는지 결과 옆에 남긴다(participants.yaml은 config_hash에 안 들어감)
    (out_dir / PARTICIPANTS_FILE).write_text(
        (CONFIG_DIR / PARTICIPANTS_FILE).read_text(encoding="utf-8"), encoding="utf-8"
    )

    with answers_path.open("a", encoding="utf-8") as af, (out_dir / "eval.jsonl").open(
        "a", encoding="utf-8"
    ) as ef:

        def sink(row: dict) -> None:
            af.write(json.dumps(row["record"], ensure_ascii=False) + "\n")
            af.flush()
            ef.write(json.dumps(row, ensure_ascii=False) + "\n")
            ef.flush()

        for p in participants:
            client = make_client(cfg, fake=fake_llm, participant=p)
            pipeline = pipeline_factory(client, retriever)
            for run_no in range(1, runs + 1):
                todo = [q for q in questions if (q.qid, client.name, run_no) not in done]
                if not todo:
                    print(f"[{client.name} run{run_no}] 이미 완료 — 건너뜀")
                    continue
                run(pipeline, todo, pattern, run_no=run_no, sink=sink, label=f"[{client.name} run{run_no}] ")

    summary = summarize_batch(answers_path)
    (out_dir / "summary.json").write_text(
        json.dumps(
            {
                "per_model": summary,
                "questions": len(questions),
                "runs": runs,
                "query_mode": pipeline.query_mode.value if participants else None,
                "corpus_commit": cfg.commit,
                "corpus_snapshot": cfg.corpus_snapshot,
                "corpus_version": cfg.corpus_version,
                "config_hash": cfg.config_hash,
                "fake_llm": fake_llm,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return summary


def print_batch_summary(summary: dict) -> None:
    print(f"\n{'─' * 72}")
    print(f"{'model':<28} {'답변':>5} {'실패':>5} {'uncached':>10} {'c_create':>9} {'c_read':>9} {'output':>8}")
    for model, s in summary.items():
        t = s["tokens"]
        print(
            f"{model:<28} {s['answers']:>5} {s['errors']:>5} {t['uncached_input']:>10} "
            f"{t['cache_creation']:>9} {t['cache_read']:>9} {t['output']:>8}"
        )


def main_batch(pipeline_factory=None, tag: str = "") -> int:
    fake = "--fake" in sys.argv
    fake_llm = fake or "--fake-llm" in sys.argv
    cfg = load()
    participants = select_participants(load_participants(), arg_value("--participants"))

    unresolved = [p["model"] for p in participants if str(p["model"]).startswith("TODO")]
    if unresolved and not fake_llm:
        print(f"participants.yaml에 모델 ID가 확정되지 않은 항목이 있습니다: {unresolved}")
        print("configs/participants.yaml을 채우거나 --participants로 제외하세요.")
        return 1

    if "--smoke" in sys.argv:
        return smoke_test(cfg, participants)

    questions = select_queries(load_queries(Path(arg_value("--questions", str(QUERIES_PATH)))))
    if not questions:
        print("실행할 질의가 없습니다.")
        return 1
    runs = int(arg_value("--runs", "1"))

    resume = arg_value("--resume")
    if resume:
        out_dir = Path(resume)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = RUNS_DIR / f"{stamp}_{cfg.config_hash}_batch{tag}{'_fake' if fake_llm else ''}"

    if pipeline_factory is None:
        def pipeline_factory(client, retriever):
            return Pipeline(cfg, retriever=retriever, client=client)

    retriever = CachedRetriever(Retriever(cfg, fake=fake))
    print(
        f"참가자 {len(participants)}개 × 반복 {runs}회 × 문항 {len(questions)}개 "
        f"= {len(participants) * runs * len(questions)}건 → {out_dir}/"
    )
    summary = run_batch(cfg, questions, participants, runs, out_dir, pipeline_factory, retriever, fake_llm)
    print_batch_summary(summary)
    print(f"\n검색 캐시: 실제 검색 {retriever.misses}회, 재사용 {retriever.hits}회")
    print(f"{out_dir}/ 기록 완료")
    return 0 if all(s["errors"] == 0 for s in summary.values()) else 1


def main() -> int:
    if "--participants" in sys.argv or "--smoke" in sys.argv:
        return main_batch()

    fake = "--fake" in sys.argv
    fake_llm = fake or "--fake-llm" in sys.argv
    cfg = load()
    all_queries = load_queries()
    queries = select_queries(all_queries)
    if not queries:
        print("실행할 질의가 없습니다.")
        return 1

    # --limit/--tier로 부분 실행하면 "20문항 예외 없이 응답"을 판정할 수 없다.
    # 이럴 때 expected_total을 None으로 둬서 dod_checks가 부분 실행임을 표시하게 한다.
    is_partial = ("--limit" in sys.argv) or ("--tier" in sys.argv)
    expected_total = None if is_partial else len(all_queries)

    pipeline = Pipeline(cfg, fake=fake, fake_llm=fake_llm)
    pattern = cfg.pipeline["generation"]["citation_pattern"]

    rows = run(pipeline, queries, pattern)
    summary = summarize(rows)
    out_dir = write_run(rows, summary, cfg)
    print_report(summary, rows, pipeline.fake, expected_total)

    print(f"\n{out_dir}/ 기록 완료")
    dod_pass = all(passed for _, passed in dod_checks(summary, expected_total))
    return 0 if dod_pass else 1


if __name__ == "__main__":
    sys.exit(main())
