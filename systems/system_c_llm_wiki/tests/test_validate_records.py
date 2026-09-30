#!/usr/bin/env python3
"""검증기 테스트. (#23 리뷰 6번)

태이님이 지적한 두 가지 빈틈을 합성 데이터로 재현해, 지금은 잡히는지 본다:
  1. 열 배분이 틀린 경우(#23의 캐시 쓰기 누락) — 입력 합계만 보면 통과했다
  2. output 만 부풀린 경우 — 역시 통과했다
그리고 같은 폴더 재실행 시 attempt_id 로 이전 호출 기록을 걸러내는지 본다.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
VALIDATOR = REPO / "systems/system_c_llm_wiki/validation/validate_records.py"
MODELS = REPO / "systems/system_c_llm_wiki/agent/models.json"


def build(tmp: Path, *, break_columns=False, inflate_output=False,
          duplicate_invocations=False, stale_attempt=False):
    """1모델 × 2문항의 최소 결과 폴더를 만든다."""
    base = tmp / "system_c"
    run = base / "runs" / "c3_run1"
    run.mkdir(parents=True)
    rows, invs = [], []
    for i, qid in enumerate(("Q1", "Q2"), 1):
        # 진짜 usage: prompt 1000 = uncached 700 + read 200 + write 100, output 50
        raw = {"prompt_tokens": 1000, "completion_tokens": 50,
               "prompt_tokens_details": {"cached_tokens": 200, "cache_write_tokens": 100}}
        cols = {"uncached_input": 700, "cache_creation": 100,
                "cache_read": 200, "output": 50}
        if break_columns:
            # 옛 버그: 캐시 쓰기를 못 읽어 uncached 로 흘러든다 (합계는 같다)
            cols = {"uncached_input": 800, "cache_creation": 0,
                    "cache_read": 200, "output": 50}
        if inflate_output:
            cols = {**cols, "output": 550}
        rows.append({
            "schema_version": "0.3", "qid": qid, "model": "gpt-6-luna", "run": 1,
            "system": "wiki", "query_mode": "simple", "question": "q", "answer": "a",
            "citations": [], "retrieved": {"bm25": [], "vector": [], "fused": [],
                                           "reranked": [], "wiki_pages": ["p1"]},
            "cited_pages": ["p1"], "identifiers_in_answer": [],
            "latency_ms": {"retrieve": 0, "rerank": 0, "generate": 0, "total": 1},
            "tokens": cols, "corpus_commit": "c", "corpus_phase": "integrated",
            "corpus_snapshot": "corpus-c3:x", "corpus_version": "0.1-c3",
            "config_hash": "AAA", "error": None, "status": "ok",
            "reasoning_applied": True, "reasoning_effort": "light",
            "attempt_id": "NEW", "wiki_label": "c3",
        })
        invs.append({"attempt_id": "NEW", "qid": qid, "model": "gpt-6-luna", "run": 1,
                     "turn": 1, "prompt_tokens": 1000, "usage_raw": raw})
        if duplicate_invocations:
            invs.append(dict(invs[-1]))
        if stale_attempt:
            invs.append({**invs[-1], "attempt_id": "OLD"})
    (base / "answers.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    (run / "invocations.jsonl").write_text(
        "\n".join(json.dumps(r) for r in invs) + "\n", encoding="utf-8")
    return base


def run_validator(base: Path, *extra):
    cmd = [sys.executable, str(VALIDATOR), str(base),
           "--models", "gpt-6-luna", "--infer-grid-from-file", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    return p.returncode, p.stdout + p.stderr


def test_clean_data_passes():
    base = build(Path(tempfile.mkdtemp()))
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "4열 전부 == usage_raw 재계산" in out
    print("  ✓ 정상 데이터 통과 + 4열 재계산 대조 수행")


def test_wrong_column_split_is_caught():
    base = build(Path(tempfile.mkdtemp()), break_columns=True)
    rc, out = run_validator(base)
    assert rc == 1, out
    assert "cache_creation" in out and "usage_raw" in out, out
    print("  ✓ 열 배분 오류(캐시 쓰기 누락) 적발 — 입력 합계는 같았다")


def test_inflated_output_is_caught():
    base = build(Path(tempfile.mkdtemp()), inflate_output=True)
    rc, out = run_validator(base)
    assert rc == 1 and ".output" in out, out
    print("  ✓ output 부풀림 적발")


def test_stale_attempt_lines_are_excluded():
    base = build(Path(tempfile.mkdtemp()), stale_attempt=True)
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "다른 attempt_id" in out, out
    print("  ✓ 이전 시도(attempt_id) 호출 기록은 대조에서 제외")


def test_duplicate_same_attempt_is_a_real_mismatch():
    """같은 attempt_id 줄이 두 번이면 진짜 불일치다(거짓 통과 금지)."""
    base = build(Path(tempfile.mkdtemp()), duplicate_invocations=True)
    rc, out = run_validator(base)
    assert rc == 1, out
    print("  ✓ 같은 시도의 중복 호출 기록은 불일치로 보고")


def test_grid_args_are_required():
    base = build(Path(tempfile.mkdtemp()))
    p = subprocess.run([sys.executable, str(VALIDATOR), str(base)],
                       capture_output=True, text=True, cwd=str(REPO))
    assert p.returncode == 2 and "기대 모델 목록이 없습니다" in p.stdout, p.stdout
    print("  ✓ 기대 격자 인자 없으면 거부(폴백으로 조용히 통과하지 않음)")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"검증기 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
