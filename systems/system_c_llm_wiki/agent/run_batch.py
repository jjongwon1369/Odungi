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
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_agent import run_agent, ABSTAIN_PHRASE, _build_system_prompt, _load_models, reset_interval_wait, get_interval_wait_s

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
SCHEMA_VERSION = "0.3"
CORPUS_COMMIT = "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"
CORPUS_PHASE = "integrated"
# 위키 컴파일러가 읽어야 하는 입력. 위키 프론트매터의 corpus_source 와 대조한다. (#23 1-4)
EXPECTED_CORPUS_SOURCE = os.environ.get(
    "CORPUS_DOCS", "corpus/tiers/c3/processed/documents.jsonl")
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
    """현재 커밋. 커밋되지 않은 변경이 있으면 -dirty를 붙인다. (#23 3절)

    깨끗한 커밋에서 돌렸는지 레코드만 보고 알 수 있어야 재현이 성립한다.
    """
    cwd = Path(__file__).parent
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=cwd,
        ).stdout.strip()
        if not head:
            return "unknown"
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, cwd=cwd,
        ).stdout.strip()
        return f"{head}-dirty" if dirty else head
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


def _get_wiki_provenance(wiki_root: Path) -> tuple:
    """위키 페이지 프론트매터의 corpus_source / corpus_snapshot 을 모은다. (#23 1-4)

    반환: (corpus_source 집합, corpus_snapshot 집합, 둘 중 하나라도 없는 페이지 수)
    """
    sources: set = set()
    snapshots: set = set()
    missing = 0
    for md_file in sorted(wiki_root.rglob("*.md")):
        if md_file.stem.lower() == "readme":
            continue
        text = md_file.read_text(encoding="utf-8")
        if not text.startswith("---") or text.count("---") < 2:
            missing += 1
            continue
        head = text.split("---", 2)[1]
        found = {}
        for line in head.split("\n"):
            for key in ("corpus_source", "corpus_snapshot"):
                if line.startswith(key + ":"):
                    found[key] = line.split(":", 1)[1].strip().strip('"').strip("'")
        if "corpus_source" in found:
            sources.add(found["corpus_source"])
        if found.get("corpus_snapshot") and found["corpus_snapshot"] != "UNKNOWN":
            snapshots.add(found["corpus_snapshot"])
        if "corpus_source" not in found or not found.get("corpus_snapshot"):
            missing += 1
    return sources, snapshots, missing


def check_wiki_provenance(wiki_root: Path, expected_source: str,
                          expected_snapshot: str | None,
                          allow_mismatch: bool) -> dict:
    """위키가 실제로 어떤 코퍼스로 컴파일됐는지 확인한다. (#23 1-4)

    레코드의 corpus_version / corpus_snapshot 은 코퍼스 메타데이터를 그대로 베껴 쓴다.
    위키가 다른 입력으로 만들어져 있어도 "c3로 돌렸다"고 적히게 된다 — 실제로 그랬다.
    그래서 실행 전에 위키 프론트매터를 직접 보고, 경로와 snapshot_id 둘 다 대조한다.
    """
    sources, snapshots, missing = _get_wiki_provenance(wiki_root)
    problems = []
    if missing:
        problems.append(f"출처 정보가 없는 페이지 {missing}개(구버전 컴파일)")
    if sources - {expected_source}:
        problems.append(f"다른 경로로 컴파일된 페이지: {sorted(sources - {expected_source})}")
    if expected_snapshot and snapshots - {expected_snapshot}:
        problems.append(
            f"snapshot 불일치 — 레코드에 적을 값 {expected_snapshot} / "
            f"위키에 박힌 값 {sorted(snapshots)}"
        )
    if not problems:
        print(f"[확인] 위키 출처 = {expected_source} / {expected_snapshot} (전 페이지 일치)")
        return {"corpus_source": expected_source, "corpus_snapshot": expected_snapshot}

    msg = (
        f"[경고] {wiki_root} 의 출처가 이번 실행이 기록할 값과 다르다 — "
        + " / ".join(problems) + "\n"
        f"        이대로 돌리면 레코드에는 {expected_snapshot} 로 적히지만 실제 입력은 다르다.\n"
        f"        위키를 --force 로 재컴파일하거나, 의도한 것이면 --allow-corpus-mismatch 를 붙일 것."
    )
    if not allow_mismatch:
        print(msg, file=sys.stderr)
        raise SystemExit(2)
    print(msg + "\n        (--allow-corpus-mismatch 로 계속 진행)", file=sys.stderr)
    return {
        "corpus_source": ",".join(sorted(sources)) or "unknown",
        "corpus_snapshot": ",".join(sorted(snapshots)) or "unknown",
    }


def _record_key(rec: dict) -> tuple:
    return (rec.get("qid"), rec.get("model"), rec.get("run", 1))


def _upsert_answers(answers_path: Path, runs_dir: Path) -> tuple:
    """기존 answers.jsonl 위에 이번 실행의 partial 결과를 덮어씌운다. (#23 3절)

    커밋돼 있는 줄은 그대로 두고, 같은 (qid, model, run) 이 새로 나온 것만 교체한다.
    원자적으로 쓴다(임시파일 → replace). 중간에 죽어도 기존 파일이 잘리지 않는다.
    """
    records: dict = {}
    order: list = []

    def put(rec: dict) -> str:
        k = _record_key(rec)
        seen = k in records
        if not seen:
            order.append(k)
        records[k] = rec
        return "replaced" if seen else "added"

    # 1) 기존 파일 (git 에 커밋돼 있는 것 포함)
    if answers_path.exists():
        for line in answers_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                put(json.loads(line))
    kept_before = len(records)

    # 2) 모든 run 의 partial 로 덮어쓰기
    replaced = added = 0
    for partial_path in sorted(runs_dir.glob("*/.partial/*.jsonl")):
        for line in partial_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if put(json.loads(line)) == "replaced":
                replaced += 1
            else:
                added += 1

    tmp = answers_path.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for k in order:
            f.write(json.dumps(records[k], ensure_ascii=False) + "\n")
    os.replace(tmp, answers_path)
    return len(records), kept_before - replaced, replaced, added


def _load_existing(path: Path, cfg_hash: str | None = None,
                   allow_config_change: bool = False) -> set:
    """이미 끝난 (qid, model, run) 세트. 설정이 바뀌었으면 이어하지 않는다. (#23 3절)

    config_hash 를 보지 않고 이어하면, 추론 강도나 프롬프트를 바꾼 뒤 재개했을 때
    한 파일 안에 서로 다른 조건의 행이 섞인다. 그러고도 status 는 전부 ok 다.
    """
    if not path.exists():
        return set()
    done: set = set()
    stale: dict = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                key = (r["qid"], r["model"], r["run"])
            except (json.JSONDecodeError, KeyError):
                continue
            row_cfg = r.get("config_hash")
            if cfg_hash and row_cfg and row_cfg != cfg_hash:
                stale[row_cfg] = stale.get(row_cfg, 0) + 1
                continue
            done.add(key)
    if stale:
        detail = ", ".join(f"{h}×{n}" for h, n in sorted(stale.items()))
        msg = (
            f"[경고] {path} 에 지금과 다른 설정으로 만든 행이 있다 — 현재 {cfg_hash} / 기존 {detail}\n"
            f"        설정이 바뀐 뒤 이어서 돌리면 한 파일에 조건이 섞인다.\n"
            f"        새 --run-label 로 처음부터 돌리거나, 의도한 것이면 "
            f"--allow-config-change 를 붙일 것."
        )
        if not allow_config_change:
            print(msg, file=sys.stderr)
            raise SystemExit(3)
        print(msg + "\n        (--allow-config-change 로 계속 진행: 해당 행은 다시 돌린다)",
              file=sys.stderr)
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

# A·B와 동일하게 마침표 없는 문구를 기준으로, 답변에 포함되어 있으면 기권으로 본다.
# 기권 문구는 run_agent(프롬프트)와 같은 상수를 본다.
# System A/B의 s6_generate.ABSTAIN_PHRASE와도 글자 그대로 같아야 한다.
ABSTAIN_TEXT = ABSTAIN_PHRASE


# 식별자 추출 규칙. 하드코딩하지 않고 System A의 configs/pipeline.yaml 을 런타임에 읽는다.
# 같은 패턴·같은 스톱워드·같은 정렬이어야 A·B·C의 식별자 무손실 지표를 대조할 수 있다. (#23 3절)
# re.ASCII: 유니코드 \b는 한글도 단어 문자로 봐서 "0x0202입니다"를 놓친다.
# (rag_proto.schema.extract_identifiers 와 동일한 동작 — pydantic 의존을 피하려고 여기서 재현한다.)
IDENTIFIER_CONFIG = Path(
    os.environ.get("IDENTIFIER_CONFIG", "systems/system_a_rag/rag_proto/configs/pipeline.yaml")
)
_FALLBACK_PATTERNS = [
    r"\b0x[0-9A-Fa-f]{4}\b",                     # 클러스터/속성 ID
    r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b",    # CamelCase
]
_FALLBACK_STOPWORDS = ["GitHub", "JavaScript", "TypeScript", "README"]


def _load_identifier_rules() -> tuple:
    """System A 설정에서 patterns/stopwords 를 읽는다. 못 읽으면 폴백을 쓰고 경고한다."""
    try:
        import yaml  # type: ignore
        cfg = yaml.safe_load(IDENTIFIER_CONFIG.read_text(encoding="utf-8")) or {}
        ident = cfg.get("identifiers") or {}
        pats = list(ident.get("patterns") or [])
        stops = list(ident.get("stopwords") or [])
        if pats:
            return pats, stops
        raise ValueError("identifiers.patterns 가 비어 있음")
    except Exception as exc:  # noqa: BLE001
        print(
            f"[경고] {IDENTIFIER_CONFIG} 에서 식별자 규칙을 읽지 못해 폴백을 쓴다: {exc}",
            file=sys.stderr,
        )
        return _FALLBACK_PATTERNS, _FALLBACK_STOPWORDS


IDENTIFIER_PATTERNS, IDENTIFIER_STOPWORDS = _load_identifier_rules()


def _extract_identifiers(text: str) -> list:
    stop = set(IDENTIFIER_STOPWORDS)
    found: list = []
    seen: set = set()
    for pat in IDENTIFIER_PATTERNS:
        for m in re.finditer(pat, text or "", re.ASCII):
            tok = m.group(0)
            if tok in stop or tok in seen:
                continue
            seen.add(tok)
            found.append(tok)
    return sorted(found)   # 공용 helper 와 같은 순서


def _build_citations(result: dict, wiki_root: str) -> list:
    """cited_pages를 공용 Citation 형식으로 옮긴다. (#23 3절)

    RAG의 chunk_id 자리에 위키 페이지 ID가, source_path에 그 페이지 파일이 들어간다.
    재순위 단계가 없으므로 rerank_score는 None.
    """
    root = wiki_root.rstrip("/")
    return [
        {
            "chunk_id": pid,
            "source_path": f"{root}/{pid}.md",
            "rerank_score": None,
        }
        for pid in (result.get("cited_pages") or [])
    ]


def _to_answer_record(
    q: dict,
    result: dict,
    *,
    model: str,
    run: int,
    wiki_label: str,
    wiki_build: str,
    wiki_root: str,
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
    abstained = ABSTAIN_TEXT in answer

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
        "citations": _build_citations(result, wiki_root),
        "retrieved": {
            "bm25": [],
            "vector": [],
            "fused": [],
            "reranked": [],
            "wiki_pages": result.get("retrieved", {}).get("wiki_pages", []),
        },
        "identifiers_in_answer": _extract_identifiers(answer),
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
        "wiki_corpus_source": corpus_meta.get("wiki_corpus_source"),
        "wiki_corpus_snapshot": corpus_meta.get("wiki_corpus_snapshot"),
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
    allow_corpus_mismatch: bool = False,
    allow_config_change: bool = False,
) -> None:
    # ---- 프리플라이트: 위키 출처 확인 (폴더를 만들기 전에 막는다) ----
    _corpus_meta_pre = _read_corpus_meta()
    wiki_provenance = check_wiki_provenance(
        Path(wiki_root), EXPECTED_CORPUS_SOURCE,
        _corpus_meta_pre.get("corpus_snapshot"), allow_corpus_mismatch
    )

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
    corpus_meta = {
        **_corpus_meta_pre,
        "wiki_corpus_source": wiki_provenance["corpus_source"],
        "wiki_corpus_snapshot": wiki_provenance["corpus_snapshot"],
    }

    # ---- 질문 로드 ----
    questions: list[dict] = []
    with open(questions_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    if limit:
        questions = questions[:limit]

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

    # ---- config_hash ----
    # 실행 조건이 하나라도 바뀌면 해시가 달라지도록, 프롬프트와 모델 레지스트리를
    # 값 그대로 넣는다. (#23 3절)
    cfg = {
        "wiki_root": wiki_root,
        "wiki_label": wiki_label,
        "wiki_build": wiki_build,
        "max_turns": max_turns,
        "run_label": run_label,
        "system_prompt_sha256": hashlib.sha256(
            _build_system_prompt().encode("utf-8")
        ).hexdigest(),
        "abstain_phrase": ABSTAIN_PHRASE,
        "models": {name: models_db.get(name, {}) for name in sorted(ordered_models)},
    }
    cfg_hash = _config_hash(cfg)

    started_at = datetime.now(timezone.utc).isoformat()
    summary_models: dict[str, dict] = {}

    # invocations / failed_attempts 파일 열기 (append 모드)
    inv_f = open(invocations_path, "a", encoding="utf-8")
    fail_f = open(failed_attempts_path, "a", encoding="utf-8")

    try:
        for model_name in ordered_models:
            partial_path = partial_dir / f"{model_name}.jsonl"
            # 재개 판정은 partial 파일 기준. 설정(config_hash)이 다르면 이어하지 않는다.
            done = _load_existing(partial_path, cfg_hash, allow_config_change)

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
                    reset_interval_wait()
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
                        # 재시도 기록뿐 아니라 최종 실패도 남긴다. (#23 3절)
                        result.setdefault("failed_attempts", []).append({
                            "attempt": "final",
                            "error": error[:500],
                            "wait_s": 0,
                            "ts": time.time(),
                        })

                    # Kimi 호출 간격 대기(min_interval_s)는 A·B처럼 지연에서 제외한다
                    elapsed_ms = int((time.time() - t0 - get_interval_wait_s()) * 1000)

                    record = _to_answer_record(
                        q, result,
                        model=model_name,
                        run=run,
                        wiki_label=wiki_label,
                        wiki_build=wiki_build,
                        wiki_root=wiki_root,
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
                            "finish_reason": td.get("finish_reason"),
                            "usage_raw": td.get("usage_raw"),
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

    # ---- answers.jsonl 갱신: 업서트 ----
    # .partial/ 은 .gitignore 대상이다. 그래서 "partial만 모아 새로 쓰기"를 하면
    # 클론받은 곳에서 한 모델만 재실행할 때 커밋돼 있던 다른 모델 줄이 전부 사라진다.
    # 기존 answers.jsonl을 읽어두고 (qid, model, run) 단위로 이번 결과만 갈아끼운다. (#23 3절)
    answers_path = base_dir / "answers.jsonl"
    merged, kept, replaced, added = _upsert_answers(answers_path, base_dir / "runs")
    print(
        f"[병합] {answers_path} — 총 {merged}줄 "
        f"(유지 {kept} / 교체 {replaced} / 신규 {added})",
        file=sys.stderr,
    )

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
        "wiki_corpus_source": corpus_meta.get("wiki_corpus_source"),
        "wiki_corpus_snapshot": corpus_meta.get("wiki_corpus_snapshot"),
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
        "--run-label", required=True,
        help="출력 상위 폴더 이름. 필수 — 기본값을 두면 새 실행이 기존 결과 폴더에 섞인다 (#23 3절)"
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
    parser.add_argument(
        "--allow-corpus-mismatch", action="store_true",
        help="위키가 지정 코퍼스로 컴파일된 게 아니어도 강행 (#23 1-4)"
    )
    parser.add_argument(
        "--allow-config-change", action="store_true",
        help="기존 partial 과 config_hash 가 달라도 이어서 실행 (#23 3절)"
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
        allow_corpus_mismatch=args.allow_corpus_mismatch,
        allow_config_change=args.allow_config_change,
    )


if __name__ == "__main__":
    main()
