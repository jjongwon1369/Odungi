#!/usr/bin/env python3
"""검증기 테스트. (#23 리뷰 6번)

태이님이 지적한 두 가지 빈틈을 합성 데이터로 재현해, 지금은 잡히는지 본다:
  1. 열 배분이 틀린 경우(#23의 캐시 쓰기 누락) — 입력 합계만 보면 통과했다
  2. output 만 부풀린 경우 — 역시 통과했다
그리고 같은 폴더 재실행 시 attempt_id 로 이전 호출 기록을 걸러내는지 본다.

행 판정을 A 규칙에 맞춘 뒤의 규칙별 테스트도 둔다. (#27 A 기준 점검)
  실패: error + 빈 answer, status error, max_turns, 오류 없는 빈 answer, C 행 generate 0
  참고: error + answer(A dangling), no_submit, 읽지 않은 페이지 인용, 도구 호출 표기
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
          duplicate_invocations=False, stale_attempt=False, patch=None):
    """1모델 × 2문항의 최소 결과 폴더를 만든다. patch={qid: {필드: 값}} 으로 행을 덮어쓴다."""
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
            # C 행은 LLM 호출 시간을 generate 에 남긴다 (#27 A 기준 점검)
            "latency_ms": {"retrieve": 0, "rerank": 0, "generate": 1, "total": 1},
            "tokens": cols, "corpus_commit": "c", "corpus_phase": "integrated",
            "corpus_snapshot": "corpus-c3:x", "corpus_version": "0.1-c3",
            "config_hash": "AAA", "error": None, "status": "ok",
            "reasoning_applied": True, "reasoning_effort": "light",
            "attempt_id": "NEW", "wiki_label": "c3",
            **((patch or {}).get(qid) or {}),
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


def build_ab(tmp: Path, patch=None):
    """System A/B 형식(status·cited_pages 등 C 전용 필드 없음, 호출기록 없음) 1모델 × 2문항."""
    base = tmp / "system_a"
    base.mkdir(parents=True)
    rows = []
    for qid in ("Q1", "Q2"):
        rows.append({
            "schema_version": "0.3", "qid": qid, "model": "gpt-6-luna", "run": 1,
            "system": "rag", "query_mode": "simple", "question": "q",
            "answer": "OnOff 는 0x0006 이다 [c1]",
            "citations": [], "retrieved": {"bm25": [], "vector": [], "fused": [],
                                           "reranked": [], "wiki_pages": []},
            "identifiers_in_answer": [],
            "latency_ms": {"retrieve": 5, "rerank": 5, "generate": 5, "total": 15},
            "tokens": {"uncached_input": 700, "cache_creation": 0,
                       "cache_read": 0, "output": 50},
            "corpus_commit": "c", "corpus_phase": "integrated",
            "corpus_snapshot": "corpus-c3:x", "corpus_version": "0.1-c3",
            "config_hash": "AAA", "error": None,
            **((patch or {}).get(qid) or {}),
        })
    (base / "answers.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return base


def run_validator(base: Path, *extra):
    cmd = [sys.executable, str(VALIDATOR), str(base),
           "--models", "gpt-6-luna", "--infer-grid-from-file", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    return p.returncode, p.stdout + p.stderr


def _fail_lines(out: str) -> list:
    return [l for l in out.splitlines() if l.startswith("[실패]")]


def test_clean_data_passes():
    base = build(Path(tempfile.mkdtemp()))
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "4열 전부 == usage_raw 재계산" in out
    assert "latency_ms.generate 기록됨" in out, out
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


# ---------- A 기준 행 판정 (#27 A 기준 점검) ----------

def test_ab_dangling_row_is_note_not_failure():
    """A 의 dangling_citations 행은 답변이 있는 정상 줄이다(run_eval._is_retryable)."""
    base = build_ab(Path(tempfile.mkdtemp()),
                    patch={"Q1": {"error": "dangling_citations: ['chunk_id']"}})
    rc, out = run_validator(base)
    assert rc == 0, out
    assert not _fail_lines(out), out
    assert "[참고] error 가 있지만 답변이 있는 행 1건" in out, out
    assert "dangling_citations" in out, out
    print("  ✓ A/B dangling_citations 행(error + answer)은 참고, 재실행 요구 안 함")


def test_ab_crash_row_is_failure():
    """A 의 크래시 행(error + 빈 answer)은 재실행 대상이다."""
    base = build_ab(Path(tempfile.mkdtemp()),
                    patch={"Q2": {"answer": "", "error": "APIConnectionError: Connection error."}})
    rc, out = run_validator(base)
    assert rc == 1, out
    assert "오류 행 1건 - 재실행 필요" in out and "Q2" in out, out
    # 한 번만 센다: 빈 답·출력 0 항목에서 다시 실패로 잡히면 안 된다
    assert len(_fail_lines(out)) == 1, out
    print("  ✓ A/B 크래시 행(error + 빈 answer)은 실패, 한 번만 센다")


def test_ab_generate_zero_is_not_checked():
    """generate 0 규칙은 C 전용이다. A/B 행에는 적용하지 않는다."""
    base = build_ab(Path(tempfile.mkdtemp()),
                    patch={q: {"latency_ms": {"retrieve": 1, "rerank": 1, "generate": 0,
                                              "total": 2}} for q in ("Q1", "Q2")})
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "[건너뜀] latency_ms.generate 검사는 System C 전용" in out, out
    print("  ✓ A/B 행은 generate 0 이어도 실패로 두지 않음")


def test_c_error_row_is_failure():
    """C 의 status error 행(새 run_batch: answer '', 부분 답은 partial_answer)은 재실행 대상."""
    base = build(Path(tempfile.mkdtemp()),
                 patch={"Q1": {"status": "error", "answer": "",
                               "error": "turn2-after-response: RateLimitError",
                               "partial_answer": "먼저 목차를 확인하겠습니다.",
                               "latency_ms": {"retrieve": 0, "rerank": 0,
                                              "generate": 0, "total": 5},
                               "tokens": {"uncached_input": 0, "cache_creation": 0,
                                          "cache_read": 0, "output": 0}}})
    rc, out = run_validator(base)
    assert rc == 1, out
    assert "AnswerRecord 전 줄 검증" in out, out   # partial_answer 가 스키마를 깨지 않는다
    fails = _fail_lines(out)
    assert len(fails) == 1 and "오류 행 1건" in fails[0], out
    print("  ✓ C status error 행은 실패, generate·출력 0 으로 중복 실패 안 함")


def test_c_error_row_with_leftover_answer_is_flagged():
    """구버전 run_batch 는 오류 행 answer 에 Anthropic 중간 서술을 남겼다."""
    base = build(Path(tempfile.mkdtemp()),
                 patch={"Q1": {"status": "error", "answer": "먼저 목차를 확인하겠습니다.",
                               "error": "응답이 온전하지 않음 (finish_reason=max_tokens)"}})
    rc, out = run_validator(base)
    assert rc == 1, out
    assert "오류 행 1건" in out and "자 남음" in out, out
    # A 규칙(error + answer = 정상 줄)의 참고 항목으로 새어 나가면 안 된다
    assert "error 가 있지만 답변이 있는 행" not in out, out
    print("  ✓ answer 가 남은 C 오류 행은 참고가 아니라 실패로, 남은 답을 표시")


def test_no_submit_is_note():
    """도구 없이 텍스트로 답한 행은 인용 없는 답변으로 채점한다(A 의 평문 답변과 같다)."""
    base = build(Path(tempfile.mkdtemp()),
                 patch={"Q2": {"status": "no_submit", "cited_pages": [],
                               "answer": "OnOff 클러스터 ID 는 0x0006 이다."}})
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "[참고] submit_answer 없이 텍스트로 끝난 행 1건" in out, out
    print("  ✓ no_submit 행은 참고, 재실행 요구 안 함")


def test_max_turns_is_failure():
    """max_turns 행은 새 run_batch 에서 오류 행이 된다. 남아 있으면 실패."""
    base = build(Path(tempfile.mkdtemp()),
                 patch={"Q1": {"status": "max_turns", "answer": ""}})
    rc, out = run_validator(base)
    assert rc == 1, out
    fails = _fail_lines(out)
    assert len(fails) == 1 and "max_turns 로 끝난 행 1건" in fails[0], out
    print("  ✓ max_turns 행은 실패, 빈 답 항목으로 중복 실패 안 함")


def test_empty_answer_without_error_is_failure():
    """A 는 빈 답을 GenerationError 로 재실행한다. 오류 없이 빈 답이 남으면 실패."""
    base = build(Path(tempfile.mkdtemp()), patch={"Q1": {"answer": "  "}})
    rc, out = run_validator(base)
    assert rc == 1 and "answer 가 빈 행 1건" in out, out
    print("  ✓ 오류 없는 빈 answer 는 실패")


def test_cited_not_read_is_note():
    """읽지 않은 페이지 인용은 A/B dangling 과 같은 성격이라 참고로만 표시한다."""
    base = build(Path(tempfile.mkdtemp()), patch={"Q1": {"cited_pages": ["p1", "p9"]}})
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "[참고] read_page 로 읽지 않은 페이지를 인용한 행 1건" in out and "p9" in out, out
    print("  ✓ 읽지 않은 페이지 인용은 참고")


def test_tool_markup_is_noted():
    """답변에 섞인 도구 호출 표기를 행 키와 함께 표시한다 (9/28 sonnet Q-codedoc-004)."""
    leak = ('빈 목록이 됩니다.</answer>\n<parameter name="cited_pages">'
            '["clusters/0x0057-refrigerator-alarm"]')
    base = build(Path(tempfile.mkdtemp()), patch={"Q2": {"answer": leak, "cited_pages": []}})
    rc, out = run_validator(base)
    assert rc == 0, out
    assert "[참고] 답변에 도구 호출 표기가 섞인 행 1건" in out, out
    assert "('Q2', 'gpt-6-luna', 1)" in out and "'<parameter'" in out and "'</answer>'" in out, out
    # A/B 답변에도 같은 검사를 돌리되, 평문이면 통과
    rc2, out2 = run_validator(build_ab(Path(tempfile.mkdtemp())))
    assert rc2 == 0 and "[통과] 답변에 도구 호출 표기 없음" in out2, out2
    print("  ✓ 도구 호출 표기(<parameter, </answer>)는 행 키와 함께 참고")


def test_c_generate_zero_is_failure():
    """C 행은 LLM 호출 시간을 generate 에 남겨야 한다. 0 이거나 칸이 없으면 실패."""
    base = build(Path(tempfile.mkdtemp()),
                 patch={"Q1": {"latency_ms": {"retrieve": 0, "rerank": 0,
                                              "generate": 0, "total": 9}},
                        "Q2": {"status": "no_submit",
                               "latency_ms": {"retrieve": 0, "rerank": 0, "total": 9}}})
    rc, out = run_validator(base)
    assert rc == 1, out
    assert "latency_ms.generate 가 0이거나 없는 System C 행 2건" in out, out
    print("  ✓ C 행(ok/no_submit) generate 0·누락은 실패")


if __name__ == "__main__":
    # 검증기는 팀 공용 스키마(pydantic)를 쓴다. 없으면 건너뛴다 — 위키 재구축에는
    # 필요 없는 의존성이라, 이것 때문에 재구축이 막히면 안 된다.
    try:
        import pydantic  # noqa: F401
    except ImportError:
        print("검증기 테스트 건너뜀 — pydantic 이 없습니다.")
        print("  답변 레코드 검증(step2·step3)에는 필요합니다: pip3 install pydantic")
        raise SystemExit(0)
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"검증기 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
