#!/usr/bin/env python3
"""에이전트 루프 테스트. (#27 3차 리뷰 1·2·4)

가짜 클라이언트로 정해 둔 응답을 차례로 돌려주고, 세 루프가
  1. 도구 인자를 쓰다가 잘린 턴을 인자를 읽기 전에 오류로 끊는지
  2. 응답을 받은 뒤의 예외(인자 JSON 깨짐, 빈 choices, content 없는 응답, 도구 실행 실패)에도
     앞 턴의 토큰을 남기는지
  3. 오류 문자열에서 키처럼 생긴 값을 가리는지
본다. 실제 API 는 부르지 않는다.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace as NS

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))

import run_agent as ra  # noqa: E402

CFG = {"model_id": "fake-model"}
FAKE_KEY = "sk-proj-ABCD1234efgh5678"


class FakeClient:
    """create() 가 불릴 때마다 script 의 다음 항목을 돌려준다. 예외면 던진다."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.chat = NS(completions=NS(create=self._create))
        self.responses = NS(create=self._create)
        self.messages = NS(create=self._create)

    def _create(self, **req):
        self.calls += 1
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def run(loop, script, page_index=None):
    fake = FakeClient(script)
    saved = (ra._make_openai_client, ra._make_anthropic_client, ra.time.sleep)
    ra._make_openai_client = lambda cfg: fake
    ra._make_anthropic_client = lambda cfg: fake
    ra.time.sleep = lambda s: None          # 429 백오프를 기다리지 않는다
    try:
        result = loop("질문", CFG, "sys", "toc", page_index or {}, 5, False)
    finally:
        ra._make_openai_client, ra._make_anthropic_client, ra.time.sleep = saved
    return result, fake.calls


# ---- 응답 모양 ----

def chat_resp(finish, tool_calls=None, content=None, prompt=100, out=10):
    return NS(choices=[NS(finish_reason=finish,
                          message=NS(tool_calls=tool_calls, content=content))],
              usage=NS(prompt_tokens=prompt, completion_tokens=out,
                       prompt_tokens_details=NS(cached_tokens=0, cache_write_tokens=0)))


def tc(name, args, cid="c1"):
    return NS(id=cid, function=NS(name=name, arguments=args))


def resp_resp(output, status="completed", reason=None, prompt=100, out=10):
    return NS(status=status, output=output,
              incomplete_details=NS(reason=reason) if reason else None,
              usage=NS(input_tokens=prompt, output_tokens=out,
                       input_tokens_details=NS(cached_tokens=0, cache_write_tokens=0)))


def fcall(name, args, cid="c1"):
    return NS(type="function_call", name=name, arguments=args, call_id=cid)


def anth_resp(stop, content, prompt=100, out=10):
    return NS(stop_reason=stop, content=content,
              usage=NS(input_tokens=prompt, output_tokens=out,
                       cache_read_input_tokens=0, cache_creation_input_tokens=0))


def tool_use(name, args, tid="t1"):
    return NS(type="tool_use", name=name, input=args, id=tid)


# ---- 1. 잘린 도구 호출 턴 ----

def test_chat_truncated_tool_call_is_error_and_keeps_tokens():
    r, calls = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("list_pages", "{}")]),
        chat_resp("length", [tc("submit_answer", '{"answer": "OnOff 는', "c2")]),
    ])
    assert r["status"] == "error" and "length" in r["error"], r["error"]
    assert r["answer"] == "" and calls == 2 and r["turns"] == 2
    assert r["token_usage"]["prompt_tokens"] == 200 and r["token_usage"]["output_tokens"] == 20
    print("  ✓ Chat: 도구 인자가 잘린 턴 → 오류, 잘린 답 채택 안 함, 두 턴 토큰 보존")


def test_responses_truncated_function_call_is_error():
    r, calls = run(ra._run_openai_responses, [
        resp_resp([fcall("submit_answer", '{"answer": "잘')],
                  status="incomplete", reason="max_output_tokens", out=16000),
    ])
    assert r["status"] == "error" and "max_output_tokens" in r["error"], r["error"]
    assert r["answer"] == "" and calls == 1 and r["token_usage"]["output_tokens"] == 16000
    print("  ✓ Responses: max_output_tokens 로 잘린 function_call → 오류")


def test_anthropic_max_tokens_tool_use_is_error():
    r, calls = run(ra._run_anthropic, [
        anth_resp("max_tokens", [tool_use("submit_answer", {"answer": "잘"})], out=16000),
    ])
    assert r["status"] == "error" and "max_tokens" in r["error"], r["error"]
    assert r["answer"] == "" and calls == 1
    print("  ✓ Anthropic: max_tokens 로 끝난 tool_use 턴 → 오류, 도구 실행 안 함")


def test_normal_tool_turns_still_finish_ok():
    r, _ = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("list_pages", "{}")]),
        chat_resp("tool_calls", [tc("submit_answer", '{"answer": "답", "cited_pages": []}', "c2")]),
    ])
    assert r["status"] == "ok" and r["answer"] == "답", r
    r, _ = run(ra._run_openai_responses, [
        resp_resp([fcall("submit_answer", '{"answer": "답", "cited_pages": []}')]),
    ])
    assert r["status"] == "ok" and r["answer"] == "답", r
    r, _ = run(ra._run_anthropic, [
        anth_resp("tool_use", [tool_use("list_pages", {})]),
        anth_resp("tool_use", [tool_use("submit_answer", {"answer": "답", "cited_pages": []}, "t2")]),
    ])
    assert r["status"] == "ok" and r["answer"] == "답", r
    print("  ✓ 정상 도구 호출 턴은 세 루프 모두 ok")


def test_anthropic_stop_sequence_ends_without_recalling():
    r, calls = run(ra._run_anthropic, [anth_resp("stop_sequence", [NS(type="text", text="본문")])])
    assert calls == 1 and r["status"] == "no_submit" and r["answer"] == "본문", (calls, r["status"])
    print("  ✓ Anthropic: stop_sequence 는 끝으로 본다(같은 대화로 다시 부르지 않음)")


# ---- 2. 응답을 받은 뒤의 예외 ----

def test_chat_bad_tool_json_keeps_earlier_turns():
    r, _ = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("list_pages", "{}")]),
        chat_resp("tool_calls", [tc("read_page", "{not json", "c2")]),
    ])
    assert r["status"] == "error" and "JSONDecodeError" in r["error"], r["error"]
    assert r["turns"] == 2 and r["token_usage"]["prompt_tokens"] == 200
    assert r["failed_attempts"][-1]["attempt"] == "turn2-after-response"
    print("  ✓ Chat: 2턴 도구 인자 JSON 깨짐 → 오류, 1·2턴 토큰과 기록 보존")


def test_responses_bad_tool_json_keeps_earlier_turns():
    r, _ = run(ra._run_openai_responses, [
        resp_resp([fcall("list_pages", "{}")]),
        resp_resp([fcall("read_page", "{not json", "c2")]),
    ])
    assert r["status"] == "error" and r["turns"] == 2, r
    assert r["token_usage"]["prompt_tokens"] == 200
    print("  ✓ Responses: 2턴 도구 인자 JSON 깨짐 → 오류, 앞 턴 보존")


def test_chat_empty_choices_is_error_not_crash():
    r, _ = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("list_pages", "{}")]),
        NS(choices=[], usage=NS(prompt_tokens=50, completion_tokens=0,
                                prompt_tokens_details=None)),
    ])
    assert r["status"] == "error" and "choices" in r["error"], r["error"]
    assert r["turns"] == 2 and r["token_usage"]["prompt_tokens"] == 150
    print("  ✓ Chat: 빈 choices → IndexError 대신 오류 행, 토큰 보존")


def test_anthropic_response_without_content_keeps_earlier_turns():
    """본문이 JSON 이 아닌 200 응답(프록시 HTML 등)은 SDK 가 문자열로 돌려준다."""
    r, _ = run(ra._run_anthropic, [
        anth_resp("tool_use", [tool_use("list_pages", {})]),
        "<html>blocked</html>",
    ])
    assert r["status"] == "error" and "AttributeError" in r["error"], r["error"]
    assert r["turns"] == 2 and r["token_usage"]["prompt_tokens"] == 100
    assert r["failed_attempts"][-1]["attempt"] == "turn2-after-response"
    print("  ✓ Anthropic: content 없는 응답 → 오류, 앞 턴 토큰 보존")


def test_tool_execution_error_keeps_earlier_turns():
    """도구 실행 중 예외(목차에는 있는데 파일이 없는 페이지)도 앞 턴을 남기고 끊는다."""
    missing = {"c/x": Path("/nonexistent/c/x.md")}
    cases = [
        (ra._run_openai_chat, [
            chat_resp("tool_calls", [tc("list_pages", "{}")]),
            chat_resp("tool_calls", [tc("read_page", '{"page_id": "c/x"}', "c2")]),
        ]),
        (ra._run_openai_responses, [
            resp_resp([fcall("list_pages", "{}")]),
            resp_resp([fcall("read_page", '{"page_id": "c/x"}', "c2")]),
        ]),
        (ra._run_anthropic, [
            anth_resp("tool_use", [tool_use("list_pages", {})]),
            anth_resp("tool_use", [tool_use("read_page", {"page_id": "c/x"}, "t2")]),
        ]),
    ]
    for loop, script in cases:
        r, _ = run(loop, script, page_index=missing)
        assert r["status"] == "error" and "FileNotFoundError" in r["error"], (loop.__name__, r["error"])
        assert r["turns"] == 2 and r["token_usage"]["prompt_tokens"] == 200, loop.__name__
        assert r["failed_attempts"][-1]["attempt"] == "turn2-after-response", loop.__name__
    print("  ✓ 세 루프 모두 도구 실행 예외 → 오류, 1·2턴 토큰과 기록 보존")


# ---- 4. 오류 문자열 가림 ----

def test_api_error_text_is_redacted():
    r, _ = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("list_pages", "{}")]),
        RuntimeError(f"401 Incorrect API key provided: {FAKE_KEY}"),
    ])
    assert r["status"] == "error" and r["token_usage"]["prompt_tokens"] == 100
    blob = repr(r["error"]) + repr(r["failed_attempts"])
    assert FAKE_KEY not in blob and "ABCD1234" not in blob, blob
    assert "sk-[가림]" in r["error"], r["error"]
    print("  ✓ API 예외 문자열의 키 가림 (error, failed_attempts)")


def test_rate_limit_retry_record_is_redacted():
    r, calls = run(ra._run_openai_chat, [
        RuntimeError(f"429 Too Many Requests for key {FAKE_KEY}"),
        chat_resp("tool_calls", [tc("submit_answer", '{"answer": "답", "cited_pages": []}')]),
    ])
    assert r["status"] == "ok" and calls == 2, r
    blob = repr(r["failed_attempts"])
    assert FAKE_KEY not in blob and "sk-[가림]" in blob, blob
    print("  ✓ 429 재시도 기록의 키 가림")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"에이전트 루프 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
