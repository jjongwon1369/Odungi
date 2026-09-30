#!/usr/bin/env python3
"""A·C 요청 일치 테스트 — 본실험 전 완료 관문. (#27 A 기준 점검)

참가자 7종마다 System A 의 generate() 요청과 System C 의 첫 턴 요청을 SDK 전송 계층에서
가로채(httpx MockTransport, 네트워크 없음) 나란히 놓고 비교한다. 기준은 A 다.

  1. model id, 엔드포인트 호스트 — OPENAI_BASE_URL / ANTHROPIC_BASE_URL 을 엉뚱한 주소로 둬도
  2. 추론 강도 값과 보내는 자리 (GPT 3종은 A Chat / C Responses 라 자리만 다르다 — 설계상 차이)
  3. temperature 유무와 값, 그 밖의 제어 파라미터
  4. 출력 상한 값(16000)과 파라미터 이름
  5. 클라이언트 타임아웃(연결 5초 / 응답 600초)과 max_retries(5), 계속 실패할 때 시도 횟수
  6. 시스템 프롬프트 — C 고유 세 줄 말고는 A 와 같은 줄이 같은 순서로
  7. 첫 user 메시지 — "<question>…</question>" 과 맺음 문장이 A 와 같은 틀
  8. submit_answer.answer 설명에 언어 지시가 없는지 (A 의 언어 지시는 프롬프트 한 문장뿐)

A 는 이 작업 트리의 systems/system_a_rag/rag_proto 사본을 쓴다(요청을 만드는 부분은 main 과 같다).
A 의 런타임(pyyaml, pydantic)이나 SDK(openai, anthropic)가 없으면 건너뛴다.
키는 가짜 문자열만 쓰고 .env 는 읽지 않는다. 실제 API 는 부르지 않는다.
"""
from __future__ import annotations

import difflib
import importlib
import importlib.util
import json
import os
import sys
import tempfile
import time
import types
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[3]
C_AGENT = REPO / "systems" / "system_c_llm_wiki" / "agent"
A_ROOT = REPO / "systems" / "system_a_rag" / "rag_proto"
A_SRC = A_ROOT / "src"
A_CFG = A_ROOT / "configs"
sys.path.insert(0, str(C_AGENT))

QUESTION = "OnOff 클러스터의 클러스터 ID는?"
# A 의 build_prompt 와 합의한 C 의 첫 user 메시지가 공유하는 질문 틀
QUESTION_BLOCK = f"<question>\n{QUESTION}\n</question>\n\n"
A_USER_TAIL = "Answer using only the context above, citing [chunk_id] for each claim."
# 합의한 C 맺음 문장. 인용 대상만 다르고 앞뒤("Answer using only the … for each claim.")는 A 와 같다.
C_USER_TAIL = ("Answer using only the wiki pages you read, citing their page ids in "
               "cited_pages for each claim.")
C_ANSWER_DESC = "질의에 대한 최종 답변."

# C 고유 시스템 프롬프트 세 줄. 나머지 줄은 A 와 글자 그대로, 같은 순서여야 한다.
# test_prompt_parity 는 공통 문장이 "들어 있는지"만 봐서, 번호 없는 지침을 덧붙이거나
# 규칙 3·위키 문단에 문장을 더해도 통과했다(감사 항목 43). 여기서는 전문을 맞춘다.
# 이 세 줄을 바꾸려면 팀 합의 뒤 여기도 함께 고친다.
C_WIKI_PARAGRAPH = (
    "You read the documentation through a wiki. Call list_pages to see the table "
    "of contents, read_page to read a page in full, and submit_answer to submit "
    "your final answer. The pages you read are your context."
)
C_RULE3 = (
    "3. Cite every claim. List the page id of every page that supports a factual "
    "claim in the cited_pages argument of submit_answer. Use only page ids you "
    "actually read with read_page."
)
C_RULE5 = (
    "5. Deliver every answer through the answer argument of submit_answer, "
    "including when you decline under rule 1. Text written without calling the "
    "tool is not recorded."
)

# 9/28 팀 결정: 모든 모델에 출력 상한 16000 (participants.yaml defaults.max_tokens)
EXPECTED_MAX_TOKENS = 16000
# A 는 timeout 을 넘기지 않아 SDK 기본값(openai·anthropic DEFAULT_TIMEOUT)을 쓴다
EXPECTED_TIMEOUT = (5.0, 600.0)   # (connect, read)
EXPECTED_MAX_RETRIES = 5          # s6_generate OpenAIClient·AnthropicClient 기본값

# 환경변수로 조건이 바뀌지 않는지 보려고 일부러 엉뚱한 값을 넣는다.
HOSTILE_BASE_URL = "http://env-redirect.invalid"
HOSTILE_TIMEOUT = "7"             # WIKI_AGENT_TIMEOUT. 합의대로면 C 는 더 이상 읽지 않는다
DUMMY_KEY = "dummy-not-a-real-key"

# 계속 실패하는 호출의 종류. 셋 다 A 는 SDK 재시도만으로 1 + max_retries 번 시도한다.
FAIL_KINDS = ("429", "503", "timeout")

# 요청 경로 끝 → 엔드포인트 종류
ENDPOINTS = {"/chat/completions": "chat", "/responses": "responses", "/messages": "messages"}
# 추론 강도를 보내는 자리. A 는 Chat·Messages 두 가지, C 는 Responses 가 더 있다.
A_EFFORT_AT = {"chat": "reasoning_effort", "messages": "output_config.effort"}
C_EFFORT_AT = {"chat": "reasoning_effort", "responses": "reasoning.effort",
               "messages": "output_config.effort"}
MAX_TOKEN_KEYS = ("max_tokens", "max_completion_tokens", "max_output_tokens")
# 제어 파라미터 비교에서 따로 보는 키(내용·추론·상한·temperature). 나머지는 A·C 가 같아야 한다.
SEPARATE_KEYS = {"model", "messages", "input", "system", "tools", "tool_choice", "thinking",
                 "temperature", "reasoning_effort", *MAX_TOKEN_KEYS}

ABSENT = "<보내지 않음>"

_STATE: dict = {"cap": None, "skip": None}


# A 의 generate() 에 넣을 검색 결과 대역(chunk_id, source_path, text 만 쓴다).
# dataclass 는 쓰지 않는다. 스위트 러너가 sys.modules 에 등록하지 않고 불러와 dataclass 가 깨진다.
CANDIDATES = [types.SimpleNamespace(chunk_id="docs_x__0001", source_path="data_model/clusters/OnOff.xml",
                                    text="OnOff cluster id 0x0006")]


# ---------------------------------------------------------------------------
# 가로채기
# ---------------------------------------------------------------------------

def _missing_packages() -> list[str]:
    need = {"yaml": "pyyaml", "pydantic": "pydantic", "openai": "openai", "anthropic": "anthropic"}
    return [pip for mod, pip in need.items() if importlib.util.find_spec(mod) is None]


def _sdk_httpx(sdk):
    """SDK 가 실제로 쓰는 httpx 계열 모듈. openai 3.x·anthropic 1.x 는 httpx2, 그 전은 httpx."""
    base = importlib.import_module(sdk.__name__ + "._base_client")
    mod = getattr(base, "httpx2", None) or getattr(base, "httpx", None)
    assert mod is not None, f"{sdk.__name__} 의 전송 모듈을 찾지 못했다"
    return mod


def _ok_body(path: str, body: dict) -> dict:
    """정상 응답. 도구가 있으면(C) 1턴에 submit_answer 를 불러 루프를 끝낸다."""
    model = body.get("model", "?")
    tools = bool(body.get("tools"))
    submit = {"answer": "OnOff 0x0006", "cited_pages": ["clusters/0x0006-on-off"]}
    text = "OnOff 0x0006 [docs_x__0001]"
    if path.endswith("/chat/completions"):
        if tools:
            msg = {"role": "assistant", "content": None, "tool_calls": [{
                "id": "call_1", "type": "function",
                "function": {"name": "submit_answer", "arguments": json.dumps(submit)}}]}
            finish = "tool_calls"
        else:
            msg, finish = {"role": "assistant", "content": text}, "stop"
        return {"id": "c1", "object": "chat.completion", "created": 0, "model": model,
                "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110}}
    if path.endswith("/responses"):
        return {"id": "resp_1", "object": "response", "created_at": 0, "status": "completed",
                "model": model, "incomplete_details": None, "error": None,
                "output": [{"type": "function_call", "id": "fc_1", "call_id": "call_1",
                            "name": "submit_answer", "arguments": json.dumps(submit),
                            "status": "completed"}],
                "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
                "usage": {"input_tokens": 100, "input_tokens_details": {"cached_tokens": 0},
                          "output_tokens": 10, "output_tokens_details": {"reasoning_tokens": 0},
                          "total_tokens": 110}}
    # /messages
    if tools:
        content = [{"type": "tool_use", "id": "tu_1", "name": "submit_answer", "input": submit}]
        stop = "tool_use"
    else:
        content, stop = [{"type": "text", "text": text}], "end_turn"
    return {"id": "msg_1", "type": "message", "role": "assistant", "model": model,
            "content": content, "stop_reason": stop, "stop_sequence": None,
            "usage": {"input_tokens": 100, "output_tokens": 10,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}


class _Recorder:
    """SDK 전송 계층 대역. 요청을 적어 두고 정해 둔 응답(또는 실패)을 돌려준다."""

    def __init__(self):
        self.requests: list[dict] = []
        self.clients: dict = {}   # (쪽, 모델, 단계) -> {"client": SDK 클라이언트, "kwargs": 넘긴 인자 이름}
        self.tag = None           # 지금 부르는 쪽 (A|C, 모델, ok|429|503|timeout)
        self.fail = None          # None 이면 정상 응답

    def handler_for(self, hx):
        def handler(request):
            body = json.loads(request.content or b"{}")
            self.requests.append({
                "tag": self.tag, "url": str(request.url), "path": request.url.path,
                "timeout": dict(request.extensions.get("timeout") or {}), "body": body,
            })
            if self.fail == "timeout":
                raise hx.ReadTimeout("mock read timeout", request=request)
            if self.fail:
                return hx.Response(int(self.fail), json={
                    "type": "error", "error": {"type": "mock_error", "message": f"mock {self.fail}"}})
            if not any(request.url.path.endswith(s) for s in ENDPOINTS):
                return hx.Response(404, json={"error": {"message": "unexpected path"}})
            return hx.Response(200, json=_ok_body(request.url.path, body),
                               headers={"request-id": "req_mock"})
        return handler


def _patch_sdk_clients(rec: _Recorder, openai, anthropic):
    """두 SDK 클라이언트 생성자를 감싸 전송 계층만 대역으로 바꾼다.

    A·C 가 넘기는 인자(timeout, max_retries, base_url)는 그대로 원래 생성자에 간다.
    그래서 생성된 클라이언트의 timeout·max_retries 는 실제 실행과 같다."""
    saved = (openai.OpenAI.__init__, anthropic.Anthropic.__init__)

    def wrap(orig, hx):
        def __init__(self, *args, **kwargs):
            passed = sorted(kwargs)          # 인자 이름만 남긴다(키 값은 남기지 않는다)
            kwargs["http_client"] = hx.Client(transport=hx.MockTransport(rec.handler_for(hx)))
            orig(self, *args, **kwargs)
            rec.clients[rec.tag] = {"client": self, "kwargs": passed}
        return __init__

    openai.OpenAI.__init__ = wrap(saved[0], _sdk_httpx(openai))
    anthropic.Anthropic.__init__ = wrap(saved[1], _sdk_httpx(anthropic))
    return saved


def _import_a():
    """이 작업 트리의 A 사본에서 s6_generate 와 load_participants 를 불러온다.

    rag_proto.config 는 import 할 때 .env 를 읽는다(load_dotenv). 진짜 키가 환경에
    들어오지 않도록 그 순간만 dotenv 를 빈 대역으로 바꿔 둔다."""
    stub = types.ModuleType("dotenv")
    stub.load_dotenv = lambda *a, **k: False
    saved_dotenv = sys.modules.get("dotenv")
    sys.modules["dotenv"] = stub
    sys.path.insert(0, str(A_SRC))
    try:
        from rag_proto import s6_generate
        from rag_proto.config import load_participants
    finally:
        sys.path.remove(str(A_SRC))
        if saved_dotenv is None:
            sys.modules.pop("dotenv", None)
        else:
            sys.modules["dotenv"] = saved_dotenv
    # venv 에 editable 로 깔린 다른 rag_proto 가 잡히면 비교 대상이 달라진다
    src = Path(s6_generate.__file__).resolve()
    assert A_SRC.resolve() in src.parents, f"작업 트리 밖의 rag_proto 를 불러왔다: {src}"
    return s6_generate, load_participants


def _tiny_wiki(root: Path) -> Path:
    page = root / "clusters" / "0x0006-on-off.md"
    page.parent.mkdir(parents=True)
    page.write_text("---\nid: x\n---\n# On/Off\n\nOnOff cluster id 0x0006\n", encoding="utf-8")
    return root


def _capture():
    """참가자마다 A·C 를 한 번씩(정상) + 실패 종류마다 한 번씩 돌려 요청을 모은다. 한 번만 돈다."""
    if _STATE["cap"] is not None or _STATE["skip"] is not None:
        return _STATE["cap"]
    missing = _missing_packages()
    if missing:
        _STATE["skip"] = (f"{', '.join(missing)} 이(가) 없습니다. A 의 참가자 설정을 읽고 A·C 요청을 "
                          f"만들려면 필요합니다: pip3 install {' '.join(missing)}")
        return None

    import anthropic
    import openai
    import yaml
    s6, load_participants = _import_a()
    import run_agent as ra

    participants = load_participants(A_CFG)
    models_db = ra._load_models()
    cfg_stub = types.SimpleNamespace(
        pipeline=yaml.safe_load((A_CFG / "pipeline.yaml").read_text(encoding="utf-8")))
    key_envs = ({s6.resolve_api_key_env(p) for p in participants}
                | {c["key_env"] for c in models_db.values() if c.get("key_env")})

    rec = _Recorder()
    env_keys = key_envs | {"OPENAI_BASE_URL", "ANTHROPIC_BASE_URL", "WIKI_AGENT_TIMEOUT"}
    saved_env = {k: os.environ.get(k) for k in env_keys}
    saved_init = _patch_sdk_clients(rec, openai, anthropic)
    saved_sleep = time.sleep
    saved_calls = dict(ra._last_call_times)
    saved_wait = getattr(ra, "_interval_wait_s", 0.0)
    outcomes: dict = {}
    try:
        for k in key_envs:
            os.environ[k] = DUMMY_KEY
        os.environ["OPENAI_BASE_URL"] = HOSTILE_BASE_URL + "/v1"
        os.environ["ANTHROPIC_BASE_URL"] = HOSTILE_BASE_URL
        os.environ["WIKI_AGENT_TIMEOUT"] = HOSTILE_TIMEOUT
        time.sleep = lambda s: None   # SDK 재시도 백오프와 C 호출 간격을 기다리지 않는다
        with tempfile.TemporaryDirectory() as tmp:
            wiki = _tiny_wiki(Path(tmp))
            for p in participants:
                name = p["model"]
                for fail in (None, *FAIL_KINDS):
                    stage = fail or "ok"
                    rec.fail = fail
                    rec.tag = ("A", name, stage)
                    try:
                        s6.generate(QUESTION, CANDIDATES, s6.make_client(cfg_stub, participant=p))
                        a_out = "ok"
                    except Exception as exc:  # noqa: BLE001
                        a_out = type(exc).__name__
                    c_out = "models.json 에 없음"
                    if name in models_db:
                        rec.tag = ("C", name, stage)
                        ra._last_call_times.pop(models_db[name]["model_id"], None)
                        try:
                            c_out = ra.run_agent(QUESTION, max_turns=2, model=name,
                                                 wiki_root=str(wiki)).get("status")
                        except Exception as exc:  # noqa: BLE001
                            c_out = f"예외 {type(exc).__name__}: {str(exc)[:120]}"
                    outcomes[(name, stage)] = (a_out, c_out)
    finally:
        time.sleep = saved_sleep
        openai.OpenAI.__init__, anthropic.Anthropic.__init__ = saved_init
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        ra._last_call_times.clear()
        ra._last_call_times.update(saved_calls)
        ra._interval_wait_s = saved_wait

    _STATE["cap"] = {"s6": s6, "ra": ra, "participants": participants, "models_db": models_db,
                     "requests": rec.requests, "clients": rec.clients, "outcomes": outcomes}
    return _STATE["cap"]


def _cap_or_skip():
    cap = _capture()
    if cap is None:
        print(f"  - 건너뜀: {_STATE['skip']}")
    return cap


# ---------------------------------------------------------------------------
# 비교 도우미
# ---------------------------------------------------------------------------

def _requests(cap, side, name, stage="ok"):
    return [r for r in cap["requests"] if r["tag"] == (side, name, stage)]


def _pair(cap, name):
    """(A 요청, C 첫 턴 요청). 없으면 None."""
    a, c = _requests(cap, "A", name), _requests(cap, "C", name)
    return (a[0] if a else None), (c[0] if c else None)


def _endpoint(path: str):
    """(엔드포인트 종류, 앞부분 경로). /v1/chat/completions → ("chat", "/v1")"""
    for suffix, kind in ENDPOINTS.items():
        if path.endswith(suffix):
            return kind, path[: -len(suffix)]
    return None, path


def _effort_sent(body: dict) -> dict:
    """추론 강도를 보낸 자리와 값. 예: {"reasoning.effort": "low"}"""
    found = {}
    if "reasoning_effort" in body:
        found["reasoning_effort"] = body["reasoning_effort"]
    for parent in ("reasoning", "output_config"):
        sub = body.get(parent)
        if isinstance(sub, dict) and "effort" in sub:
            found[f"{parent}.effort"] = sub["effort"]
    return found


def _other_controls(body: dict) -> dict:
    """따로 보는 키를 뺀 나머지 제어 파라미터(stream, top_p, metadata, 캐시 키 등)."""
    rest = {k: v for k, v in body.items() if k not in SEPARATE_KEYS}
    for parent in ("reasoning", "output_config"):
        if isinstance(rest.get(parent), dict):
            sub = {k: v for k, v in rest[parent].items() if k != "effort"}
            if sub:
                rest[parent] = sub
            else:
                rest.pop(parent)
    return rest


def _turn1(body: dict, kind: str):
    """첫 요청의 (시스템 프롬프트, 역할 순서, user 메시지 목록). 시스템 채널도 역할로 센다."""
    if kind == "messages":
        items = body.get("messages") or []
        system = body.get("system")
        roles = (["system"] if "system" in body else []) + [m.get("role") for m in items]
    else:
        items = body.get("input") if kind == "responses" else body.get("messages")
        items = items or []
        systems = [i.get("content") for i in items if i.get("role") == "system"]
        system = systems[0] if len(systems) == 1 else systems
        roles = [i.get("role") or i.get("type") for i in items]
    users = [i.get("content") for i in items if i.get("role") == "user"]
    return system, roles, users


def _timeout_pair(t):
    """SDK 클라이언트 timeout 을 (connect, read) 로. 숫자 하나면 모든 단계가 그 값이다."""
    if t is None:
        return (None, None)
    if isinstance(t, (int, float)):
        return (float(t), float(t))
    return (float(t.connect) if t.connect is not None else None,
            float(t.read) if t.read is not None else None)


def _request_timeout_pair(ext: dict):
    return (ext.get("connect"), ext.get("read"))


def _expected_c_prompt(a_prompt: str) -> str:
    """A 프롬프트에 C 고유 세 줄(위키 문단 추가, 규칙 3 교체, 규칙 5 추가)만 반영한 기대 전문."""
    out = []
    for line in a_prompt.split("\n"):
        if line.startswith("Answer ONLY from the provided context."):
            out += [C_WIKI_PARAGRAPH, ""]
        if line.startswith("3. "):
            out.append(C_RULE3)
            continue
        out.append(line)
        if line.startswith("4. "):
            out.append(C_RULE5)
    return "\n".join(out)


def _submit_answer_schema(tool: dict, kind: str):
    if kind == "chat":
        fn = tool.get("function") or {}
        return fn.get("name"), fn.get("parameters") or {}
    if kind == "messages":
        return tool.get("name"), tool.get("input_schema") or {}
    return tool.get("name"), tool.get("parameters") or {}


def _report(problems: list[str], ok_msg: str) -> None:
    """불일치를 모두 찍고 실패시킨다. 스위트 러너는 예외 문구를 200자로 자르므로 먼저 찍는다."""
    if problems:
        for p in problems:
            print(f"  ✗ {p}")
        raise AssertionError(f"{len(problems)}건 불일치 — {problems[0]}")
    print(f"  ✓ {ok_msg}")


# ---------------------------------------------------------------------------
# 1. 참가자와 model id
# ---------------------------------------------------------------------------

def test_participants_and_model_ids():
    """A 의 참가자 7종이 C models.json 과 같고, 두 쪽이 같은 model id 를 보낸다."""
    cap = _cap_or_skip()
    if cap is None:
        return
    names = [p["model"] for p in cap["participants"]]
    problems = []
    if len(names) != 7:
        problems.append(f"A participants.yaml 참가자가 7종이 아니다: {names}")
    if set(names) != set(cap["models_db"]):
        problems.append(f"참가자 불일치: A 에만 {sorted(set(names) - set(cap['models_db']))}, "
                        f"C 에만 {sorted(set(cap['models_db']) - set(names))}")
    for name in names:
        a, c = _pair(cap, name)
        a_out, c_out = cap["outcomes"].get((name, "ok"), (None, None))
        if a is None or c is None:
            problems.append(f"{name}: 요청을 잡지 못했다 (A {a_out}, C {c_out})")
            continue
        # 가로채기 자체가 제대로 돌았는지 (정상 응답에서 A 는 답, C 는 submit_answer 로 끝남)
        if a_out != "ok" or c_out != "ok":
            problems.append(f"{name}: 정상 응답인데 끝이 이상하다 (A {a_out}, C {c_out})")
        if not (a["body"].get("model") == c["body"].get("model") == name):
            problems.append(f"{name}: model id A={a['body'].get('model')!r} C={c['body'].get('model')!r}")
        if name in cap["models_db"] and cap["models_db"][name].get("model_id") != name:
            problems.append(f"{name}: models.json model_id 가 {cap['models_db'][name].get('model_id')!r}")
    _report(problems, f"참가자 {len(names)}종 동일, model id 가 A·C 요청에서 같다")


# ---------------------------------------------------------------------------
# 2. 엔드포인트
# ---------------------------------------------------------------------------

def test_endpoint_host_and_api_surface():
    """같은 호스트·같은 앞부분 경로. OPENAI_BASE_URL/ANTHROPIC_BASE_URL 은 두 쪽 다 무시한다.
    GPT 3종만 A Chat Completions / C Responses 로 엔드포인트가 다르다. C 는 도구와
    reasoning_effort 를 함께 보내야 하는데 chat/completions 는 이를 400 으로 거부한다(감사 항목 2)."""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    surfaces = 0
    for p in cap["participants"]:
        name = p["model"]
        a, c = _pair(cap, name)
        if a is None or c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        a_host, c_host = urlsplit(a["url"]).netloc, urlsplit(c["url"]).netloc
        (a_kind, a_base), (c_kind, c_base) = _endpoint(a["path"]), _endpoint(c["path"])
        if a_host != c_host:
            problems.append(f"{name}: 호스트 A={a_host} C={c_host}")
        if "env-redirect.invalid" in (a_host + c_host):
            problems.append(f"{name}: 환경변수 주소로 샜다 (A={a_host} C={c_host})")
        if a_base != c_base:
            problems.append(f"{name}: 앞부분 경로 A={a_base!r} C={c_base!r}")
        if p["provider"] == "openai" and (a_kind, c_kind) == ("chat", "responses"):
            surfaces += 1                      # 설계상 차이로 허용
        elif a_kind != c_kind:
            problems.append(f"{name}: 엔드포인트 A={a['path']} C={c['path']}")
    _report(problems, f"호스트·경로 동일, 환경변수 무시 (Chat↔Responses 허용 {surfaces}종)")


# ---------------------------------------------------------------------------
# 3. 추론 강도
# ---------------------------------------------------------------------------

def test_reasoning_effort_value_and_place():
    """강도 값은 participants.yaml effort 와 같고, 각 API 의 제자리에 한 번만 간다.
    Claude 의 thinking 은 A 가 생략하고 C 가 {"type": "adaptive"} 를 보낸다. Sonnet 5·Opus 5.5 는
    생략해도 adaptive 로 돌므로 같은 조건이다(감사 항목 5). 그 밖의 값은 허용하지 않는다."""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    for p in cap["participants"]:
        name = p["model"]
        a, c = _pair(cap, name)
        if a is None or c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        a_kind, c_kind = _endpoint(a["path"])[0], _endpoint(c["path"])[0]
        a_eff, c_eff = _effort_sent(a["body"]), _effort_sent(c["body"])
        effort = p.get("effort")
        want_a = {A_EFFORT_AT.get(a_kind, "?"): effort} if effort else {}
        want_c = {C_EFFORT_AT.get(c_kind, "?"): effort} if effort else {}
        if a_eff != want_a:
            problems.append(f"{name}: A 추론 강도 {a_eff} (기대 {want_a})")
        if c_eff != want_c:
            problems.append(f"{name}: C 추론 강도 {c_eff} (기대 {want_c}, A 는 {a_eff})")
        if set(a_eff.values()) != set(c_eff.values()):
            problems.append(f"{name}: 강도 값이 다르다 A={a_eff} C={c_eff}")
        if "thinking" in a["body"]:
            problems.append(f"{name}: A 가 thinking 을 보낸다 {a['body']['thinking']}")
        c_thinking = c["body"].get("thinking", ABSENT)
        allowed = (ABSENT, {"type": "adaptive"}) if c_kind == "messages" else (ABSENT,)
        if c_thinking not in allowed:
            problems.append(f"{name}: C thinking {c_thinking} (허용 {allowed})")
    _report(problems, "추론 강도 값·자리 일치 (7종 모두 participants.yaml 값)")


# ---------------------------------------------------------------------------
# 4. temperature 와 그 밖의 제어 파라미터
# ---------------------------------------------------------------------------

def test_temperature_and_other_controls():
    """temperature 는 유무와 값이 같다(participants.yaml 이 null 이면 둘 다 안 보낸다).
    stream·top_p·캐시 키 같은 나머지 제어 파라미터도 A·C 가 같아야 한다.
    C 에만 있는 것은 도구 정의와 tool_choice="auto" 뿐이다(감사 항목 16)."""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    for p in cap["participants"]:
        name = p["model"]
        a, c = _pair(cap, name)
        if a is None or c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        a_t, c_t = a["body"].get("temperature", ABSENT), c["body"].get("temperature", ABSENT)
        want_t = ABSENT if p.get("temperature") is None else p["temperature"]
        if not (a_t == c_t == want_t):
            problems.append(f"{name}: temperature A={a_t} C={c_t} (participants.yaml {want_t})")
        a_rest, c_rest = _other_controls(a["body"]), _other_controls(c["body"])
        if a_rest != c_rest:
            problems.append(f"{name}: 제어 파라미터 A={a_rest} C={c_rest}")
        if "tools" in a["body"] or "tool_choice" in a["body"]:
            problems.append(f"{name}: A 가 도구를 보낸다")
        if c["body"].get("tool_choice", "auto") != "auto":
            problems.append(f"{name}: C tool_choice={c['body']['tool_choice']!r} (auto 만 허용)")
    _report(problems, "temperature 유무·값과 나머지 제어 파라미터 일치")


# ---------------------------------------------------------------------------
# 5. 출력 상한
# ---------------------------------------------------------------------------

def test_max_output_tokens_value_and_param():
    """값은 16000. 이름은 A 의 participants.yaml max_tokens_param(없으면 max_completion_tokens,
    Anthropic 은 max_tokens)과 같고, GPT 의 Responses 는 그에 해당하는 max_output_tokens 다."""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    for p in cap["participants"]:
        name = p["model"]
        a, c = _pair(cap, name)
        if a is None or c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        a_kind, c_kind = _endpoint(a["path"])[0], _endpoint(c["path"])[0]
        a_mt = {k: a["body"][k] for k in MAX_TOKEN_KEYS if k in a["body"]}
        c_mt = {k: c["body"][k] for k in MAX_TOKEN_KEYS if k in c["body"]}
        # make_client 과 같은 규칙: Anthropic 은 max_tokens, 나머지는 max_tokens_param 기본 max_completion_tokens
        a_key = "max_tokens" if a_kind == "messages" else (p.get("max_tokens_param") or "max_completion_tokens")
        c_key = "max_output_tokens" if c_kind == "responses" else a_key
        if a_mt != {a_key: EXPECTED_MAX_TOKENS}:
            problems.append(f"{name}: A 출력 상한 {a_mt} (기대 {{{a_key!r}: {EXPECTED_MAX_TOKENS}}})")
        if c_mt != {c_key: EXPECTED_MAX_TOKENS}:
            problems.append(f"{name}: C 출력 상한 {c_mt} (기대 {{{c_key!r}: {EXPECTED_MAX_TOKENS}}}, A 는 {a_mt})")
        if p.get("max_tokens") != EXPECTED_MAX_TOKENS:
            problems.append(f"{name}: participants.yaml max_tokens={p.get('max_tokens')}")
    _report(problems, f"출력 상한 {EXPECTED_MAX_TOKENS}, 파라미터 이름 A 대응 일치")


# ---------------------------------------------------------------------------
# 6. 타임아웃·재시도
# ---------------------------------------------------------------------------

def test_client_timeout_and_max_retries():
    """C 클라이언트 생성자(_make_openai_client / _make_anthropic_client)를 실제로 거쳐
    만들어진 SDK 클라이언트의 timeout·max_retries 와, 요청마다 실제로 걸린 타임아웃이 A 와 같다.
    WIKI_AGENT_TIMEOUT 에 엉뚱한 값을 넣어 두므로, C 가 그 변수를 읽으면 여기서 드러난다."""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    for p in cap["participants"]:
        name = p["model"]
        a_cl = cap["clients"].get(("A", name, "ok"))
        c_cl = cap["clients"].get(("C", name, "ok"))
        a, c = _pair(cap, name)
        if not (a_cl and c_cl and a and c):
            problems.append(f"{name}: 클라이언트나 요청을 잡지 못했다")
            continue
        a_to, c_to = _timeout_pair(a_cl["client"].timeout), _timeout_pair(c_cl["client"].timeout)
        a_mr, c_mr = a_cl["client"].max_retries, c_cl["client"].max_retries
        hint = " (C 가 timeout 인자를 넘긴다)" if "timeout" in c_cl["kwargs"] else ""
        if not (a_to == c_to == EXPECTED_TIMEOUT):
            problems.append(f"{name}: 클라이언트 timeout(connect, read) A={a_to} C={c_to}{hint} "
                            f"[WIKI_AGENT_TIMEOUT={HOSTILE_TIMEOUT} 로 둔 상태]")
        if not (a_mr == c_mr == EXPECTED_MAX_RETRIES):
            problems.append(f"{name}: max_retries A={a_mr} C={c_mr}")
        # 생성자 인자 이름도 같아야 한다. http_client·timeout 같은 인자로 조건을 바꾸면
        # 이 테스트의 가짜 전송이 그 값을 덮어써서 위 검사만으로는 드러나지 않는다.
        if set(a_cl["kwargs"]) != set(c_cl["kwargs"]):
            problems.append(f"{name}: 생성자 인자 A={sorted(a_cl['kwargs'])} C={sorted(c_cl['kwargs'])}")
        # Anthropic SDK 는 비스트리밍 요청의 타임아웃을 max_tokens 로 따로 계산한다.
        # 클라이언트 값이 같아도 요청에 실린 값을 한 번 더 본다.
        a_req, c_req = _request_timeout_pair(a["timeout"]), _request_timeout_pair(c["timeout"])
        if a_req != c_req:
            problems.append(f"{name}: 요청 timeout(connect, read) A={a_req} C={c_req}")
    _report(problems, f"timeout(connect, read)={EXPECTED_TIMEOUT}, max_retries={EXPECTED_MAX_RETRIES} "
                      "— 클라이언트·요청 모두 A 와 같다")


def test_retry_attempts_on_persistent_failure():
    """계속 429·503·응답 시간 초과가 나면 A 와 C 가 같은 횟수(1 + max_retries)만 시도한다.
    A 에는 앱 수준 재시도가 없다. C 에 429 전용 루프가 남아 있으면 429 에서만 횟수가 늘고,
    SDK 재시도가 A 보다 적으면 503·시간 초과에서 줄어든다. 끝나면 C 는 오류 행이어야 한다."""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    for p in cap["participants"]:
        name = p["model"]
        for kind in FAIL_KINDS:
            n_a, n_c = len(_requests(cap, "A", name, kind)), len(_requests(cap, "C", name, kind))
            a_out, c_out = cap["outcomes"].get((name, kind), (None, None))
            if not (n_a == n_c == EXPECTED_MAX_RETRIES + 1):
                problems.append(f"{name} {kind}: 시도 A={n_a} C={n_c} (기대 {EXPECTED_MAX_RETRIES + 1})")
            if a_out == "ok":
                problems.append(f"{name} {kind}: A 가 실패하지 않았다(가로채기 확인)")
            if c_out != "error":
                problems.append(f"{name} {kind}: C 결과 {c_out!r} (오류 행이어야 한다)")
    _report(problems, f"계속 실패할 때 시도 횟수 A=C={EXPECTED_MAX_RETRIES + 1} "
                      f"({'/'.join(FAIL_KINDS)}), C 는 오류 행")


# ---------------------------------------------------------------------------
# 7. 시스템 프롬프트
# ---------------------------------------------------------------------------

def test_system_prompt_matches_a_except_three_lines():
    """두 쪽 다 시스템 채널로 보낸다. C 는 A 전문에서 위키 문단 추가·규칙 3 교체·규칙 5 추가만
    다르다. 세 경로(Responses·Chat·Anthropic)가 같은 글을 보낸다."""
    cap = _cap_or_skip()
    if cap is None:
        return
    s6, ra = cap["s6"], cap["ra"]
    problems = []
    a_prompt = s6.SYSTEM_PROMPT
    anchors = ("Answer ONLY from the provided context.", "3. ", "4. ")
    for anchor in anchors:
        if sum(1 for l in a_prompt.split("\n") if l.startswith(anchor)) != 1:
            problems.append(f"A SYSTEM_PROMPT 에 {anchor!r} 로 시작하는 줄이 정확히 한 줄이 아니다")
    expected = _expected_c_prompt(a_prompt)
    if ra._build_system_prompt() != expected:
        diff = list(difflib.unified_diff(expected.split("\n"), ra._build_system_prompt().split("\n"),
                                         "기대(A+C 고유 세 줄)", "C", lineterm="", n=0))
        problems.append("C _build_system_prompt 가 기대 전문과 다르다:\n    " + "\n    ".join(diff[:12]))
    for p in cap["participants"]:
        name = p["model"]
        a, c = _pair(cap, name)
        if a is None or c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        a_sys, a_roles, _ = _turn1(a["body"], _endpoint(a["path"])[0])
        c_sys, c_roles, _ = _turn1(c["body"], _endpoint(c["path"])[0])
        if a_sys != a_prompt:
            problems.append(f"{name}: A 가 보낸 시스템 프롬프트가 SYSTEM_PROMPT 와 다르다")
        if c_sys != expected:
            problems.append(f"{name}: C 가 보낸 시스템 프롬프트가 기대 전문과 다르다")
        if a_roles != c_roles:
            problems.append(f"{name}: 첫 요청 메시지 구성 A={a_roles} C={c_roles}")
    _report(problems, "시스템 프롬프트: A 전문 + C 고유 세 줄, 7종 모두 시스템 채널로 같은 글")


# ---------------------------------------------------------------------------
# 8. 첫 user 메시지
# ---------------------------------------------------------------------------

def test_first_user_message_parallels_a():
    """A: "<context>…</context>\\n\\n<question>\\n{q}\\n</question>\\n\\n" + A 맺음 문장.
    C: "<question>\\n{q}\\n</question>\\n\\n" + C_USER_TAIL. 문맥은 도구로 읽으므로 <context> 만 빠진다.
    맺음 문장은 앞뒤가 같고 인용 대상만 다르다. (감사 항목 26)"""
    cap = _cap_or_skip()
    if cap is None:
        return
    s6, ra = cap["s6"], cap["ra"]
    problems = []
    for tail in (A_USER_TAIL, C_USER_TAIL):
        if not (tail.startswith("Answer using only the ") and tail.endswith(" for each claim.")):
            problems.append(f"맺음 문장 틀이 다르다: {tail!r}")
    if getattr(ra, "C_USER_TAIL", None) != C_USER_TAIL:
        problems.append(f"run_agent.C_USER_TAIL={getattr(ra, 'C_USER_TAIL', ABSENT)!r} (합의 문장과 다름)")
    build = getattr(ra, "_build_user_message", None)
    if build is None:
        problems.append("run_agent._build_user_message 가 없다")
    elif build(QUESTION) != QUESTION_BLOCK + C_USER_TAIL:
        problems.append(f"_build_user_message(q)={build(QUESTION)!r}")
    a_expected = s6.build_prompt(QUESTION, CANDIDATES)
    if not (a_expected.startswith("<context>\n") and a_expected.endswith(QUESTION_BLOCK + A_USER_TAIL)):
        problems.append(f"A build_prompt 끝이 기대와 다르다: ...{a_expected[-120:]!r}")
    for p in cap["participants"]:
        name = p["model"]
        a, c = _pair(cap, name)
        if a is None or c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        _, _, a_users = _turn1(a["body"], _endpoint(a["path"])[0])
        _, _, c_users = _turn1(c["body"], _endpoint(c["path"])[0])
        if a_users != [a_expected]:
            problems.append(f"{name}: A user 메시지가 build_prompt 와 다르다")
        if c_users != [QUESTION_BLOCK + C_USER_TAIL]:
            got = c_users[0] if len(c_users) == 1 else c_users
            problems.append(f"{name}: C user 메시지 {got!r}")
    _report(problems, "첫 user 메시지: 같은 <question> 틀 + 대응하는 맺음 문장 (7종)")


# ---------------------------------------------------------------------------
# 9. 도구 설명의 언어 지시
# ---------------------------------------------------------------------------

def test_submit_answer_description_has_no_language_directive():
    """A 의 언어 지시는 "Answer in the same language as the question." 하나뿐이다.
    C 도구 설명에 "(한국어)" 같은 지시가 더 있으면 C 에만 번역 압력이 생긴다. (감사 항목 27)"""
    cap = _cap_or_skip()
    if cap is None:
        return
    problems = []
    for p in cap["participants"]:
        name = p["model"]
        _, c = _pair(cap, name)
        if c is None:
            problems.append(f"{name}: 요청 없음")
            continue
        kind = _endpoint(c["path"])[0]
        tools = c["body"].get("tools") or []
        desc = ABSENT
        for t in tools:
            tname, schema = _submit_answer_schema(t, kind)
            if tname == "submit_answer":
                desc = ((schema.get("properties") or {}).get("answer") or {}).get("description", ABSENT)
        if desc != C_ANSWER_DESC:
            problems.append(f"{name}: submit_answer.answer 설명 {desc!r} (기대 {C_ANSWER_DESC!r})")
        blob = json.dumps(tools, ensure_ascii=False)
        for word in ("한국어", "Korean"):
            if word in blob:
                problems.append(f"{name}: 도구 정의에 언어 지시 {word!r} 가 있다")
    _report(problems, f"submit_answer.answer 설명 {C_ANSWER_DESC!r}, 도구 정의에 언어 지시 없음")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"A·C 요청 일치 테스트 {len(fns)}개")
    if _capture() is None:
        # 검증기 테스트처럼 건너뛴다 — C 만 도는 환경에서 이것 때문에 막히면 안 된다.
        print(f"A·C 요청 일치 테스트 건너뜀 — {_STATE['skip']}")
        raise SystemExit(0)
    failed = []
    for fn in fns:
        try:
            fn()
        except AssertionError:
            failed.append(fn.__name__)
    if failed:
        print(f"실패 {len(failed)}개: {', '.join(failed)}")
        raise SystemExit(1)
    print("전부 통과")
