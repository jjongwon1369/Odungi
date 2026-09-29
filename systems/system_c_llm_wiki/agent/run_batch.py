# -*- coding: utf-8 -*-
"""
LLM Wiki 배치 평가 러너 (System C) — run_batch.py
==================================================

benchmark/questions_v1.jsonl의 질문을 7개 모델로 실행하고
팀 공용 AnswerRecord v0.3 형식으로 results/raw/<run_label>/system_c/answers.jsonl을 출력한다.

사용법 (리포 루트에서):
    set -a; . ./.env.local; set +a

    # 스모크 테스트 (2문항, 전 모델)
    python3 systems/system_c_llm_wiki/agent/run_batch.py \\
        --wiki-root systems/system_c_llm_wiki/wiki-astra \\
        --wiki-label astra --models all --limit 2 --run-label smoke_test

    # 본실행
    python3 systems/system_c_llm_wiki/agent/run_batch.py \\
        --wiki-root systems/system_c_llm_wiki/wiki-astra \\
        --wiki-label astra --models all --run-label test_low_0928
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_agent import run_agent, _load_models

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
SCHEMA_VERSION = "0.3"
CORPUS_COMMIT = "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"
CORPUS_PHASE = "integrated"
SNAPSHOT_JSON = Path("corpus/tiers/c3/metadata/snapshot.json")
REASONING_EFFORT_LABEL = "light"


# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _config_hash(cfg: dict) -> str:
    canonical = json.dumps(cfg, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _git_short_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True,
            cwd=Path(__file__).parent,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _read_corpus_meta() -> dict:
    """corpus/tiers/c3/metadata/snapshot.json에서 corpus_snapshot, corpus_version을 읽는다."""
    try:
        data = json.loads(SNAPSHOT_JSON.read_text(encoding="utf-8"))
        return {
            "corpus_snapshot": data.get("snapshot_id"),
            "corpus_version": data.get("corpus_version"),
        }
    except Exception:
        return {"corpus_snapshot": None, "corpus_version": None}


def _get_wiki_build(wiki_root: Path) -> str:
    """위키 페이지 프론트매터의 compiled_by를 읽는다."""
    for md_file in sorted(wiki_root.rglob("*.md")):
        if md_file.stem.lower() == "readme":
            continue
        text = md_file.read_text(encoding="utf-8")
        if text.startswith("---"):
            for line in text.split("\n"):
                if line.startswith("compiled_by:"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
    return "unknown"


def _load_existing(path: Path) -> set:
    """기존 JSONL에서 (qid, model, run) 세트를 반환한다."""
    if not path.exists():
        return set()
    done: set = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    done.add((r["qid"], r["model"], r["run"]))
                except (json.JSONDecodeError, KeyError):
                    pass
    return done


def _sort_models_kimi_first(models: list[str]) -> list[str]:
    """kimi-k3를 맨 앞으로 옮긴다 (RPM 제한으로 가장 오래 걸림)."""
    if "kimi-k3" in models:
        rest = [m for m in models if m != "kimi-k3"]
        return ["kimi-k3"] + rest
    return models


# ---------------------------------------------------------------------------
# AnswerRecord 생성
# ---------------------------------------------------------------------------

ABSTAIN_TEXT = "제공된 문서에서 확인되지 않음."


def _to_answer_record(
    q: dict,
    result: dict,
    *,
    model: str,
    run: int,
    wiki_label: str,
    wiki_build: str,
    questions_sha256: str,
    agent_commit: str,
    trace_path: str,
    elapsed_ms: int,
    status: str,
    error: str | None,
    corpus_meta: dict,
    cfg_hash: str,
) -> dict:
    tu = result.get("token_usage", {})
    prompt = tu.get("prompt_tokens")
    cache_read = tu.get("cache_read")
    cache_write = tu.get("cache_write")
    output = tu.get("output_tokens")

    # 공용 TokenUsage 스키마는 네 칸 모두 int(기본 0)이므로 None은 0으로 통일한다.
    prompt = prompt or 0
    cache_read = cache_read or 0
    cache_write = cache_write or 0
    output = output or 0
    # prompt는 모든 provider에서 캐시 포함 전체 입력이므로 읽기·쓰기를 모두 뺀다.
    uncached_input = max(0, prompt - cache_read - cache_write)

    answer = result.get("answer", "")
    abstained = answer.strip() == ABSTAIN_TEXT

    return {
        # ---- v0.3 기존 필드 (변경 금지) ----
        "schema_version": SCHEMA_VERSION,
        "qid": q["query_id"],
        "model": model,
        "run": run,
        "system": "wiki",
        "query_mode": "simple",
        "question": q["question"],
        "answer": answer,
        "citations": [],
        "retrieved": {
            "bm25": [],
            "vector": [],
            "fused": [],
            "reranked": [],
            "wiki_pages": result.get("retrieved", {}).get("wiki_pages", []),
        },
        "identifiers_in_answer": [],
        "latency_ms": {
            "retrieve": 0,
            "rerank": 0,
            "generate": 0,
            "total": elapsed_ms,
        },
        "tokens": {
            "uncached_input": uncached_input,
            "cache_creation": cache_write,
            "cache_read": cache_read,
            "output": output,
        },
        "corpus_commit": CORPUS_COMMIT,
        "corpus_phase": CORPUS_PHASE,
        "corpus_snapshot": corpus_meta.get("corpus_snapshot"),
        "corpus_version": corpus_meta.get("corpus_version"),
        "config_hash": cfg_hash,
        "error": error,
        # ---- v0.3 추가 필드 (system-c 전용) ----
        "cited_pages": result.get("cited_pages", []),
        "turns": result.get("turns", 0),
        "wiki_build": wiki_build,
        "wiki_label": wiki_label,
        # 실제로 전송된 경우에만 라벨을 남긴다 (전송 안 됐는데 low로 기록되는 것 방지)
        "reasoning_effort": REASONING_EFFORT_LABEL if result.get("reasoning_applied") else None,
        "reasoning_config": result.get("reasoning_config_sent"),
        "reasoning_applied": result.get("reasoning_applied", False),
        "abstained": abstained,
        "status": status,
        "trace_path": trace_path,
        "wiki_pages_evidence": result.get("page_evidence", []),
        "questions_sha256": questions_sha256,
        "agent_commit": agent_commit,
    }


# ---------------------------------------------------------------------------
# 배치 실행
# ---------------------------------------------------------------------------

def run_batch(
    models_list: list[str],
    questions_path: str,
    wiki_root: str,
    wiki_label: str,
    run: int,
    run_label: str,
    max_turns: int,
    verbose: bool,
    limit: int | None,
) -> None:
    # ---- 출력 디렉토리 구조 ----
    base_dir = Path("results") / "raw" / run_label / "system_c"
    run_dir = base_dir / "runs" / f"{wiki_label}_run{run}"
    partial_dir = run_dir / ".partial"
    for d in [base_dir, run_dir, partial_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # ---- 메타데이터 수집 ----
    questions_sha256 = _file_sha256(questions_path)
    wiki_build = _get_wiki_build(Path(wiki_root))
    agent_commit = _git_short_head()
    corpus_meta = _read_corpus_meta()

    # ---- 질문 로드 ----
    questions: list[dict] = []
    with open(questions_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    if limit:
        questions = questions[:limit]

    # ---- config_hash ----
    cfg = {
        "wiki_root": wiki_root,
        "wiki_label": wiki_label,
        "wiki_build": wiki_build,
        "max_turns": max_turns,
        "run_label": run_label,
    }
    cfg_hash = _config_hash(cfg)

    # ---- trace 경로 (run_dir 기준 상대 경로) ----
    invocations_path = run_dir / "invocations.jsonl"
    failed_attempts_path = run_dir / "failed_attempts.jsonl"
    # trace_path는 results/raw/<run_label>/ 기준
    trace_path_rel = str(
        (run_dir / "invocations.jsonl").relative_to(Path("results") / "raw" / run_label)
    )

    # ---- models.json 스냅샷 저장 ----
    models_db = _load_models()
    (run_dir / "models.json").write_text(
        json.dumps(models_db, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- kimi-k3 먼저 ----
    ordered_models = _sort_models_kimi_first(models_list)

    started_at = datetime.now(timezone.utc).isoformat()
    summary_models: dict[str, dict] = {}

    # invocations / failed_attempts 파일 열기 (append 모드)
    inv_f = open(invocations_path, "a", encoding="utf-8")
    fail_f = open(failed_attempts_path, "a", encoding="utf-8")

    try:
        for model_name in ordered_models:
            partial_path = partial_dir / f"{model_name}.jsonl"
            # 재개 판정은 partial 파일만 기준으로 한다.
            # answers.jsonl은 덮어써지므로 신뢰할 수 없다.
            done = _load_existing(partial_path)

            ok = err = abstained_count = 0
            model_start = time.time()

            print(
                f"\n[모델 시작] {model_name} ({len(questions)}문항 중 {len(done)}개 기존)",
                file=sys.stderr,
            )

            with open(partial_path, "a", encoding="utf-8") as out_f:
                for i, q in enumerate(questions, 1):
                    qid = q["query_id"]
                    if (qid, model_name, run) in done:
                        print(f"  [건너뜀] {qid}", file=sys.stderr)
                        continue

                    print(
                        f"  [{i}/{len(questions)}] {qid} ...",
                        end=" ", flush=True, file=sys.stderr,
                    )
                    t0 = time.time()
                    error = None
                    result: dict = {}
                    q_status = "ok"

                    try:
                        result = run_agent(
                            query=q["question"],
                            max_turns=max_turns,
                            verbose=verbose,
                            model=model_name,
                            wiki_root=wiki_root,
                        )
                        q_status = result.get("status", "ok")
                    except Exception as e:
                        q_status = "error"
                        error = f"{e.__class__.__name__}: {e}"
                        print(f"ERR({error[:60]})", file=sys.stderr)

                    elapsed_ms = int((time.time() - t0) * 1000)

                    record = _to_answer_record(
                        q, result,
                        model=model_name,
                        run=run,
                        wiki_label=wiki_label,
                        wiki_build=wiki_build,
                        questions_sha256=questions_sha256,
                        agent_commit=agent_commit,
                        trace_path=trace_path_rel,
                        elapsed_ms=elapsed_ms,
                        status=q_status if not error else "error",
                        error=error,
                        corpus_meta=corpus_meta,
                        cfg_hash=cfg_hash,
                    )

                    # append to partial
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out_f.flush()

                    # invocations.jsonl: 턴별 1줄
                    for td in result.get("turn_details", []):
                        inv_line = {
                            "qid": qid,
                            "model": model_name,
                            "run": run,
                            "turn": td["turn"],
                            "tool_calls": [c["tool"] for c in td.get("calls", [])],
                            "arguments": [c["args"] for c in td.get("calls", [])],
                            "result_len": [c["result_len"] for c in td.get("calls", [])],
                            "sha256": [c["sha256"] for c in td.get("calls", [])],
                            "prompt_tokens": td.get("prompt_tokens"),
                            "cache_read": td.get("cache_read"),
                            "cache_write": td.get("cache_write"),
                            "output_tokens": td.get("output_tokens"),
                        }
                        inv_f.write(json.dumps(inv_line, ensure_ascii=False) + "\n")
                    inv_f.flush()

                    # failed_attempts.jsonl
                    for fa in result.get("failed_attempts", []):
                        fa_line = {"qid": qid, "model": model_name, "run": run, **fa}
                        fail_f.write(json.dumps(fa_line, ensure_ascii=False) + "\n")
                    fail_f.flush()

                    if error:
                        err += 1
                    else:
                        ok += 1
                        if record.get("abstained"):
                            abstained_count += 1

                    status_str = "OK" if not error else f"ERR"
                    tok = record["tokens"]
                    print(
                        f"{status_str} turns={record['turns']} "
                        f"({elapsed_ms/1000:.1f}s)",
                        file=sys.stderr,
                    )

            model_elapsed = time.time() - model_start
            summary_models[model_name] = {
                "ok": ok, "err": err, "abstained": abstained_count,
                "elapsed_s": round(model_elapsed, 1),
            }
            print(
                f"[모델 완료] {model_name}: ok={ok} err={err} abstained={abstained_count} "
                f"({model_elapsed:.0f}s)",
                file=sys.stderr,
            )

    finally:
        inv_f.close()
        fail_f.close()

    # ---- 모든 partial 병합 → answers.jsonl ----
    # --models와 무관하게 .partial/ 안의 모든 jsonl을 합친다.
    # 일부 모델만 재실행해도 나머지 모델 답변이 사라지지 않는다.
    answers_path = base_dir / "answers.jsonl"
    merged = 0
    with open(answers_path, "w", encoding="utf-8") as out_f:
        for partial_path in sorted(partial_dir.glob("*.jsonl")):
            with open(partial_path, encoding="utf-8") as pf:
                for line in pf:
                    line = line.strip()
                    if line:
                        out_f.write(line + "\n")
                        merged += 1

    finished_at = datetime.now(timezone.utc).isoformat()

    # ---- summary 통계: partial 파일 전체에서 재집계 (재개 실행 포함) ----
    final_results: dict[str, dict] = {}
    for model_name in ordered_models:
        partial_path = partial_dir / f"{model_name}.jsonl"
        if partial_path.exists():
            records = [
                json.loads(l) for l in partial_path.read_text(encoding="utf-8").splitlines() if l.strip()
            ]
            final_results[model_name] = {
                "ok": sum(1 for r in records if not r.get("error")),
                "err": sum(1 for r in records if r.get("error")),
                "abstained": sum(1 for r in records if r.get("abstained")),
                "elapsed_s": summary_models.get(model_name, {}).get("elapsed_s", 0),
            }
        else:
            final_results[model_name] = summary_models.get(
                model_name, {"ok": 0, "err": 0, "abstained": 0, "elapsed_s": 0}
            )

    # ---- summary.json ----
    summary = {
        "run_label": run_label,
        "wiki_label": wiki_label,
        "wiki_build": wiki_build,
        "wiki_root": wiki_root,
        "ssot_commit": CORPUS_COMMIT,
        "corpus_snapshot": corpus_meta.get("corpus_snapshot"),
        "corpus_version": corpus_meta.get("corpus_version"),
        "questions_sha256": questions_sha256,
        "reasoning_effort": REASONING_EFFORT_LABEL,
        "models": ordered_models,
        "results": final_results,
        "agent_commit": agent_commit,
        "started_at": started_at,
        "finished_at": finished_at,
        "total_records": merged,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- README.md ----
    _write_readme(base_dir, summary, models_db)

    print(
        f"\n[배치 완료] {merged}줄 → {answers_path}\n"
        f"  summary: {run_dir / 'summary.json'}",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# README.md 자동 생성
# ---------------------------------------------------------------------------

def _write_readme(base_dir: Path, summary: dict, models_db: dict) -> None:
    lines = [
        f"# System C — LLM Wiki · {summary['run_label']}",
        "",
        "`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.",
        "",
        "## 실행 조건",
        f"- 위키: `{summary['wiki_root']}` (compiled_by: {summary['wiki_build']})",
        f"- SSOT: `{summary['ssot_commit']}`",
        f"- 코퍼스: `{summary['corpus_version']}` `{summary['corpus_snapshot']}`",
        f"- 질문셋 SHA-256: `{summary['questions_sha256']}`",
        f"- 코드 커밋: `{summary['agent_commit']}`",
        f"- 추론 강도: {summary['reasoning_effort']} (effort=low)",
        f"- 출력 상한: max_tokens=16000",
        f"- temperature: 보내지 않음",
        "",
        "## 참가자 모델",
        "",
        "| 모델 | provider | reasoning_applied | 비고 |",
        "| --- | --- | --- | --- |",
    ]
    for m in summary["models"]:
        cfg = models_db.get(m, {})
        provider = cfg.get("provider", "?")
        has_reason = bool(cfg.get("reasoning_config"))
        note = ""
        if m == "deepseek-flash":
            note = "DeepSeek-V4.1-Flash (V4 Flash, 9/10 교체)"
        elif m == "kimi-k3":
            note = f"RPM 3/min → min_interval_s={cfg.get('min_interval_s', '?')}"
        lines.append(f"| {m} | {provider} | {has_reason} | {note} |")

    lines += [
        "",
        "## 결과",
        "",
        "| 모델 | ok | err | abstained |",
        "| --- | --- | --- | --- |",
    ]
    for m, r in summary.get("results", {}).items():
        lines.append(f"| {m} | {r['ok']} | {r['err']} | {r['abstained']} |")

    lines += [
        "",
        f"시작: {summary['started_at']}  완료: {summary['finished_at']}",
    ]

    (base_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 배치 평가 러너")
    parser.add_argument(
        "--models", default="all",
        help="쉼표 구분 모델 목록 또는 'all' (models.json 기준)"
    )
    parser.add_argument(
        "--wiki-root", default="systems/system_c_llm_wiki/wiki",
        help="위키 루트 디렉토리"
    )
    parser.add_argument(
        "--wiki-label", default="",
        help="위키 레이블 (예: astra)"
    )
    parser.add_argument(
        "--run", type=int, default=1,
        help="실행 회차 (기본 1)"
    )
    parser.add_argument(
        "--run-label", default="test_low_0928",
        help="출력 상위 폴더 이름 (기본: test_low_0928)"
    )
    parser.add_argument(
        "--questions", default="benchmark/questions_v1.jsonl",
        help="질문셋 JSONL"
    )
    parser.add_argument(
        "--max-turns", type=int, default=30,
        help="에이전트 최대 턴 수 (기본 30)"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="테스트용: 첫 N문항만"
    )
    args = parser.parse_args()

    # 모델 목록 결정
    all_models = list(_load_models().keys())
    if args.models.strip().lower() == "all":
        models_list = all_models
    else:
        models_list = [m.strip() for m in args.models.split(",") if m.strip()]
        unknown = [m for m in models_list if m not in all_models]
        if unknown:
            print(f"[오류] models.json에 없는 모델: {unknown}", file=sys.stderr)
            sys.exit(1)

    wiki_label = args.wiki_label or Path(args.wiki_root).name

    run_batch(
        models_list=models_list,
        questions_path=args.questions,
        wiki_root=args.wiki_root,
        wiki_label=wiki_label,
        run=args.run,
        run_label=args.run_label,
        max_turns=args.max_turns,
        verbose=args.verbose,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
