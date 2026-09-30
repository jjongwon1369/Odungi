#!/usr/bin/env python3
"""에이전트 루프 테스트. (#27 3차 리뷰 1·2·4)

가짜 클라이언트로 정해 둔 응답을 차례로 돌려주고, 세 루프가
  1. 도구 인자를 쓰다가 잘린 턴을 인자를 읽기 전에 오류로 끊는지
  2. 응답을 받은 뒤의 예외(인자 JSON 깨짐, 빈 choices, content 없는 응답, 도구 실행 실패)에도
     앞 턴의 토큰을 남기는지
  3. 오류 문자열에서 키처럼 생긴 값을 가리는지
  4. System A 와 같게 동작하는지(재시도는 SDK 5회만, 첫 user 메시지 틀, 출력 상한 16000,
     호출 시간 기록, GPT 의 이전 추론 전달, 제출한 답 보존) (#27 A 기준 점검)
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
        self.requests = []          # 호출 시점의 요청(메시지 목록은 얕은 복사)
        self.chat = NS(completions=NS(create=self._create))
        self.responses = NS(create=self._create)
        self.messages = NS(create=self._create)

    def _create(self, **req):
        self.calls += 1
        snap = dict(req)
        for k in ("messages", "input"):
            if k in snap:
                snap[k] = list(snap[k])
        self.requests.append(snap)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def run(loop, script, page_index=None, with_fake=False, max_turns=5):
    fake = FakeClient(script)
    saved = (ra._make_openai_client, ra._make_anthropic_client, ra.time.sleep)
    ra._make_openai_client = lambda cfg: fake
    ra._make_anthropic_client = lambda cfg: fake
    ra.time.sleep = lambda s: None          # 429 백오프를 기다리지 않는다
    try:
        result = loop("질문", CFG, "sys", "toc", page_index or {}, max_turns, False)
    finally:
        ra._make_openai_client, ra._make_anthropic_client, ra.time.sleep = saved
    if with_fake:
        return result, fake
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


def test_no_app_level_429_retry():
    """재시도는 SDK 에만 맡긴다(A 와 같은 max_retries=5). C 만의 429 재시도 루프는 없다. (#27 A 기준 점검)"""
    r, calls = run(ra._run_openai_chat, [
        RuntimeError(f"429 Too Many Requests for key {FAKE_KEY}"),
        chat_resp("tool_calls", [tc("submit_answer", '{"answer": "답", "cited_pages": []}')]),
    ])
    assert calls == 1 and r["status"] == "error", (calls, r["status"])
    blob = repr(r["error"]) + repr(r["failed_attempts"])
    assert FAKE_KEY not in blob and "sk-[가림]" in r["error"], blob
    assert ra.CLIENT_MAX_RETRIES == 5
    print("  ✓ 429 는 SDK 재시도(5회)만, 앱 수준 재시도 없음, 오류 문구 가림")


# ---- A 기준 점검 (#27) ----

def test_first_user_message_matches_a_structure():
    """A: <context>…</context> + <question>…</question> + 'Answer using only the context above, …'.
    C 는 문맥만 도구로 읽고 나머지 틀은 같다."""
    q = "OnOff 클러스터 ID 는?"
    want = f"<question>\n{q}\n</question>\n\n{ra.C_USER_TAIL}"
    assert ra._build_user_message(q) == want
    for loop, script, key in (
        (ra._run_openai_chat, [chat_resp("stop", None, content="답")], "messages"),
        (ra._run_openai_responses, [resp_resp([NS(type="message", content=[NS(type="output_text", text="답")])])], "input"),
        (ra._run_anthropic, [anth_resp("end_turn", [NS(type="text", text="답")])], "messages"),
    ):
        fake = FakeClient(script)
        saved = (ra._make_openai_client, ra._make_anthropic_client)
        ra._make_openai_client = lambda cfg: fake
        ra._make_anthropic_client = lambda cfg: fake
        try:
            loop(q, CFG, "sys", "toc", {}, 5, False)
        finally:
            ra._make_openai_client, ra._make_anthropic_client = saved
        users = [m for m in fake.requests[0][key] if isinstance(m, dict) and m.get("role") == "user"]
        assert users and users[0]["content"] == want, (loop.__name__, users)
    print("  ✓ 세 경로 모두 첫 user 메시지 = <question>…</question> + 규칙 재강조(A 와 같은 틀)")


def test_responses_carries_reasoning_items_to_next_turn():
    """GPT 도 이전 턴의 추론을 다음 턴에 넘긴다(Claude·DeepSeek·Kimi 는 원래 넘겼다)."""
    reasoning = NS(type="reasoning", id="rs_1", summary=[])
    fc = fcall("list_pages", "{}")
    r, fake = run(ra._run_openai_responses, [
        resp_resp([reasoning, fc]),
        resp_resp([fcall("submit_answer", '{"answer": "답", "cited_pages": []}', "c2")]),
    ], with_fake=True)
    assert r["status"] == "ok", r
    turn2 = fake.requests[1]["input"]
    assert reasoning in turn2 and fc in turn2, turn2
    assert turn2.index(reasoning) < turn2.index(fc)
    outs = [i for i in turn2 if isinstance(i, dict) and i.get("type") == "function_call_output"]
    assert len(outs) == 1 and outs[0]["call_id"] == "c1"
    print("  ✓ Responses: 2턴 입력에 reasoning 항목과 원래 function_call 이 순서대로 들어감")


def test_responses_preamble_with_tool_call_does_not_end_loop():
    """서두 메시지와 도구 호출이 한 응답에 와도 서두를 답으로 끝내지 않는다."""
    preamble = NS(type="message", content=[NS(type="output_text", text="목차를 먼저 보겠습니다.")])
    r, calls = run(ra._run_openai_responses, [
        resp_resp([preamble, fcall("list_pages", "{}")]),
        resp_resp([fcall("submit_answer", '{"answer": "진짜 답", "cited_pages": []}', "c2")]),
    ])
    assert calls == 2 and r["status"] == "ok" and r["answer"] == "진짜 답", (calls, r["status"], r["answer"])
    print("  ✓ Responses: 서두 + 도구 호출 응답에서 멈추지 않고 제출한 답을 씀")


def test_text_after_submit_does_not_overwrite_answer():
    r, _ = run(ra._run_anthropic, [anth_resp("tool_use", [
        tool_use("submit_answer", {"answer": "제출한 답", "cited_pages": []}),
        NS(type="text", text="제출했습니다."),
    ])])
    assert r["answer"] == "제출한 답", r["answer"]
    r, _ = run(ra._run_openai_responses, [resp_resp([
        fcall("submit_answer", '{"answer": "제출한 답", "cited_pages": []}'),
        NS(type="message", content=[NS(type="output_text", text="제출했습니다.")]),
    ])])
    assert r["answer"] == "제출한 답", r["answer"]
    print("  ✓ submit_answer 뒤의 텍스트가 제출한 답을 덮어쓰지 않음 (Anthropic·Responses)")


def test_llm_call_time_is_recorded_per_turn():
    """A 의 latency_ms.generate 처럼 LLM 호출 시간을 턴마다 남기고 합을 돌려준다."""
    r, _ = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("list_pages", "{}")]),
        chat_resp("tool_calls", [tc("submit_answer", '{"answer": "답", "cited_pages": []}', "c2")]),
    ])
    ms = [t.get("api_ms") for t in r["turn_details"]]
    assert all(isinstance(x, int) and x >= 0 for x in ms) and len(ms) == 2, ms
    assert r["llm_ms"] == sum(ms), (r["llm_ms"], ms)
    print("  ✓ 턴별 api_ms 와 합 llm_ms 기록")


def test_output_cap_is_fixed_16000_on_all_routes():
    import importlib
    import os
    global ra
    saved = os.environ.get("WIKI_AGENT_MAX_OUTPUT_TOKENS")
    os.environ["WIKI_AGENT_MAX_OUTPUT_TOKENS"] = "8000"      # 예전 코드는 이 값을 읽었다
    try:
        ra = importlib.reload(ra)
        assert ra.MAX_OUTPUT_TOKENS == 16000, ra.MAX_OUTPUT_TOKENS
        _check_cap_requests()
    finally:
        if saved is None:
            os.environ.pop("WIKI_AGENT_MAX_OUTPUT_TOKENS", None)
        else:
            os.environ["WIKI_AGENT_MAX_OUTPUT_TOKENS"] = saved
        ra = importlib.reload(ra)
    print("  ✓ 출력 상한 16000 고정 (세 경로, 환경변수를 넣어도 안 바뀜)")


def _check_cap_requests():
    for loop, script, key in (
        (ra._run_openai_chat, [chat_resp("stop", None, content="답")], "max_tokens"),
        (ra._run_openai_responses, [resp_resp([NS(type="message", content=[NS(type="output_text", text="답")])])], "max_output_tokens"),
        (ra._run_anthropic, [anth_resp("end_turn", [NS(type="text", text="답")])], "max_tokens"),
    ):
        _, fake = run(loop, script, with_fake=True)
        assert fake.requests[0][key] == 16000, (loop.__name__, fake.requests[0].get(key))


def test_anthropic_answer_is_final_turn_text_like_a():
    """A 는 마지막 응답의 본문 조각을 이어 붙인 것만 답으로 쓴다(s6_generate.py 282행).
    도구를 부른 턴의 서두는 답이 아니다. 마지막 턴에 본문이 없으면 빈 답이다."""
    narr = NS(type="text", text="먼저 목차를 확인하겠습니다.")
    r, _ = run(ra._run_anthropic, [
        anth_resp("tool_use", [narr, tool_use("list_pages", {})]),
        anth_resp("end_turn", []),
    ])
    assert r["answer"] == "" and r["status"] == "no_submit", (r["answer"], r["status"])
    r, _ = run(ra._run_anthropic, [anth_resp("end_turn", [
        NS(type="text", text="OnOff 클러스터 ID는 "), NS(type="text", text="0x0006 이다.")])])
    assert r["answer"] == "OnOff 클러스터 ID는 0x0006 이다.", r["answer"]
    r, _ = run(ra._run_anthropic, [
        anth_resp("tool_use", [narr, tool_use("list_pages", {})]),
        anth_resp("tool_use", [tool_use("list_pages", {}, "t2")]),
    ], max_turns=2)
    assert r["status"] == "max_turns" and r["answer"] == narr.text, (r["status"], r["answer"])
    print("  ✓ Anthropic 답 = 마지막 응답 본문 이어 붙임(A 와 같음), 서두는 답이 아님(최대 턴이면 partial 로 넘김)")


def test_page_read_in_submit_turn_is_not_context():
    """제출과 같은 응답의 read_page 결과는 모델에게 가지 않으므로 문맥(→ citations)에 넣지 않는다."""
    page = Path(__file__)                                   # 아무 파일이나 읽을 수 있으면 된다
    idx = {"device-types/light": page}
    cases = [
        (ra._run_openai_chat, [chat_resp("tool_calls", [
            tc("read_page", '{"page_id": "device-types/light"}', "c1"),
            tc("submit_answer", '{"answer": "답", "cited_pages": ["device-types/light"]}', "c2")])]),
        (ra._run_openai_responses, [resp_resp([
            fcall("read_page", '{"page_id": "device-types/light"}', "c1"),
            fcall("submit_answer", '{"answer": "답", "cited_pages": ["device-types/light"]}', "c2")])]),
        (ra._run_anthropic, [anth_resp("tool_use", [
            tool_use("read_page", {"page_id": "device-types/light"}, "t1"),
            tool_use("submit_answer", {"answer": "답", "cited_pages": ["device-types/light"]}, "t2")])]),
    ]
    for loop, script in cases:
        r, _ = run(loop, script, page_index=idx)
        assert r["status"] == "ok" and r["retrieved"]["wiki_pages"] == [], (loop.__name__, r["retrieved"])
        assert r["page_evidence"] == [], loop.__name__
    r, _ = run(ra._run_openai_chat, [
        chat_resp("tool_calls", [tc("read_page", '{"page_id": "device-types/light"}', "c1")]),
        chat_resp("tool_calls", [tc("submit_answer", '{"answer": "답", "cited_pages": []}', "c2")]),
    ], page_index=idx)
    assert r["retrieved"]["wiki_pages"] == ["device-types/light"], r["retrieved"]
    print("  ✓ 제출과 같은 응답의 read_page 는 문맥에 안 넣음(세 경로), 앞 턴에 읽은 페이지는 그대로")

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"에이전트 루프 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
