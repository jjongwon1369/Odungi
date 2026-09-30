#!/usr/bin/env python3
"""위키 구축 토큰 원장(build_calls.jsonl) 집계 테스트. (#23 리뷰)

리뷰에서 지적된 세 가지 손실을 재현해 막았는지 확인한다:
  1. --force 재컴파일 시 이전 시도의 과금분이 사라짐
  2. 중간에 K하면 이미 과금·저장된 페이지의 토큰이 사라짐
  3. 집계 파일을 읽지 못하면 조용히 새로 써서 이전 기록이 사라짐

실행: python3 systems/system_c_llm_wiki/tests/test_build_tokens.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "compiler"))

import compile_wiki as cw  # noqa: E402

COLS = ("uncached_input", "cache_creation", "cache_read", "output")


def call(entity, attempt, uncached, creation, read, out):
    return {"entity": entity, "attempt": attempt, "uncached_input": uncached,
            "cache_creation": creation, "cache_read": read, "output": out}


def test_force_attempts_are_all_billed():
    """--force 로 같은 엔티티를 두 번 만들면 두 호출 모두 과금이다."""
    lines = [call("base:A", 1, 100, 0, 0, 101),
             call("base:A", 2, 100, 0, 0, 520)]
    totals, per = cw.aggregate_build_calls(lines)
    assert totals["output"] == 621, totals
    assert per["base:A"]["attempts"] == 2
    print("  ✓ --force 재시도 합산 (621, 시도 2회)")


def test_interrupted_run_keeps_earlier_pages():
    """중간에 멈춰도 원장에 적힌 호출은 남는다."""
    lines = [call("base:A", 1, 10, 0, 0, 107)]          # Ctrl-C 직전에 저장된 페이지
    totals, _ = cw.aggregate_build_calls(lines)
    assert totals["output"] == 107
    lines.append(call("base:B", 1, 10, 0, 0, 733))       # 이어서 실행
    totals, _ = cw.aggregate_build_calls(lines)
    assert totals["output"] == 840, totals
    print("  ✓ 중단 후 이어하기 누적 (107 → 840)")


def test_none_columns_do_not_crash():
    lines = [call("x", 1, None, None, None, None), call("y", 1, 5, None, 2, 3)]
    totals, _ = cw.aggregate_build_calls(lines)
    assert totals == {"uncached_input": 5, "cache_creation": 0,
                      "cache_read": 2, "output": 3}, totals
    print("  ✓ None 칼럼 무시")


def test_broken_ledger_line_stops_instead_of_dropping():
    """원장 한 줄이 깨졌으면 조용히 버리지 않고 멈춘다 — 그 줄도 과금분이다."""
    tmp = Path(tempfile.mkdtemp())
    cw.WIKI_ROOT = tmp
    ledger = tmp / cw.BUILD_CALLS_NAME
    ledger.write_text(
        json.dumps(call("base:A", 1, 1, 0, 0, 50)) + "\n{깨진 줄\n",
        encoding="utf-8")
    try:
        cw.write_build_tokens("ssot")
    except SystemExit as exc:
        assert "과금된 호출" in str(exc), exc
        print("  ✓ 깨진 원장 줄에서 SystemExit")
        return
    raise AssertionError("깨진 줄을 조용히 넘겼다")


def test_write_build_tokens_roundtrip():
    tmp = Path(tempfile.mkdtemp())
    cw.WIKI_ROOT = tmp
    (tmp / cw.BUILD_CALLS_NAME).write_text(
        "\n".join(json.dumps(c) for c in
                 [call("base:A", 1, 100, 7, 3, 101), call("base:A", 2, 100, 0, 110, 520)]),
        encoding="utf-8")
    out = cw.write_build_tokens("abc123")
    saved = json.loads((tmp / "build_tokens.json").read_text(encoding="utf-8"))
    assert saved["totals"] == out["totals"]
    assert saved["totals"]["output"] == 621
    assert saved["calls"] == 2
    assert saved["columns"] == list(COLS)
    assert not (tmp / "build_tokens.json.tmp").exists(), "임시파일이 남았다"
    print("  ✓ build_tokens.json 원자적 기록 + 4열")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"build_tokens 원장 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
