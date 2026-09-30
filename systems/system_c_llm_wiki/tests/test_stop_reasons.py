#!/usr/bin/env python3
"""잘림·거절 판정 테스트. (#23 리뷰 2번)

가짜 응답 객체로 세 provider 형태를 만들어, 온전하지 않은 종료가
status='error' 로 남는지 본다. 도구를 부른 턴이라도 잘렸으면 오류다. (#27 3차 리뷰 1)
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace as NS

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))

from run_agent import _hard_stop, _turn_meta, HARD_STOP_REASONS  # noqa: E402


def chat(finish):          # DeepSeek / Kimi
    return NS(choices=[NS(finish_reason=finish)], usage=None)


def responses(status=None, inc_reason=None):
    return NS(choices=None, stop_reason=None, status=status,
              incomplete_details=NS(reason=inc_reason) if inc_reason else None,
              usage=None)


def anthropic(stop):
    return NS(choices=None, stop_reason=stop, usage=None)


def test_chat_length_and_filter_are_errors():
    for fr in ("length", "content_filter"):
        assert _hard_stop(_turn_meta(chat(fr))["finish_reason"], False) == fr
    print("  ✓ Chat length·content_filter → 오류")


def test_chat_normal_stops_are_ok():
    for fr in ("stop", "tool_calls", None):
        assert _hard_stop(_turn_meta(chat(fr))["finish_reason"], False) is None
    print("  ✓ Chat stop·tool_calls → 정상")


def test_responses_incomplete_is_error():
    assert _hard_stop(_turn_meta(responses(status="incomplete",
                                          inc_reason="max_output_tokens"))["finish_reason"],
                      False) == "max_output_tokens"
    assert _hard_stop(_turn_meta(responses(status="incomplete"))["finish_reason"],
                      False) == "incomplete"
    assert _hard_stop(_turn_meta(responses(status="completed"))["finish_reason"],
                      False) is None
    print("  ✓ Responses incomplete → 오류 / completed → 정상")


def test_anthropic_max_tokens_and_refusal_are_errors():
    for sr in ("max_tokens", "refusal"):
        assert _hard_stop(_turn_meta(anthropic(sr))["finish_reason"], False) == sr
    for sr in ("end_turn", "tool_use"):
        assert _hard_stop(_turn_meta(anthropic(sr))["finish_reason"], False) is None
    print("  ✓ Anthropic max_tokens·refusal → 오류 / end_turn·tool_use → 정상")


def test_truncated_tool_call_turn_is_an_error():
    """도구 인자를 쓰다가 출력 상한에 걸려도 오류다. 도구 호출 여부로 봐주지 않는다. (#27 3차 리뷰 1)"""
    for fr in sorted(HARD_STOP_REASONS):
        assert _hard_stop(fr, True) == fr, fr
    for fr in ("tool_calls", "tool_use", "completed"):
        assert _hard_stop(fr, True) is None, fr
    print("  ✓ 도구 호출 턴도 잘리면 오류 / tool_calls·tool_use·completed 는 정상")


def test_unlisted_reasons_are_errors():
    """허용 목록 밖의 사유는 모두 오류. 막을 사유만 나열하면 이런 사유가 빠진다."""
    for fr in ("model_context_window_exceeded", "max_messages", "failed", "pause_turn"):
        assert _hard_stop(fr, False) == fr, fr
    print("  ✓ 목록에 없는 사유(model_context_window_exceeded 등) → 오류")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"종료 사유 판정 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
