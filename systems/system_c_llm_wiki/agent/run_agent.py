# -*- coding: utf-8 -*-
"""
LLM Wiki 에이전트 루프 (System C) — run_agent.py
=================================================

provider 추상화: OpenAI Responses API / OpenAI-compatible Chat / Anthropic Messages.
models.json에서 모델별 설정을 읽는다.

사용법 (리포 루트에서):
    set -a; . ./.env.local; set +a
    python3 systems/system_c_llm_wiki/agent/run_agent.py \\
        --query "LaundryWasherMode가 지원하는 표준 모드 태그는?" \\
        --model gpt-6-luna --verbose
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 경로 설정
# ---------------------------------------------------------------------------
WIKI_ROOT = Path("systems/system_c_llm_wiki/wiki")
MODELS_JSON = Path(__file__).parent / "models.json"

# 모델별 마지막 API 호출 시각 (min_interval_s 강제용)
_last_call_times: dict[str, float] = {}

# 호출 간격 강제로 기다린 누적 시간(초). A·B처럼 지연 기록에서 빼기 위해 run_batch가 읽는다.
_interval_wait_s: float = 0.0


def reset_interval_wait() -> None:
    global _interval_wait_s
    _interval_wait_s = 0.0


def get_interval_wait_s() -> float:
    return _interval_wait_s


# 오류 문구 속 키 조각·계정 식별자 가림. System A 의 run_eval._redact 와 같은 규칙이다.
# failed_attempts.jsonl·answers.jsonl 은 git 에 올라가는데, 제공자 오류 문구에는
# 조직 ID(org-…)나 키 조각(sk-…, ak-…)이 들어오기도 한다(9/28 Kimi 429). (#27 3차 리뷰 4)
_KEY_LIKE = re.compile(r"\b(sk|ak|org)-[A-Za-z0-9_\-*.]{4,}")


def redact(text) -> str:
    return _KEY_LIKE.sub(lambda m: f"{m.group(1)}-[가림]", str(text))


def _error_text(exc: Exception) -> str:
    """예외를 기록용 문구로 바꾼다(가림 적용)."""
    return redact(f"{exc.__class__.__name__}: {exc}")


# ---------------------------------------------------------------------------
# models.json 로딩
# ---------------------------------------------------------------------------

def _load_models() -> dict:
    with open(MODELS_JSON, encoding="utf-8") as f:
        return json.load(f)


def _get_default_model() -> str:
    return (
        os.environ.get("WIKI_AGENT_MODEL")
        or os.environ.get("WIKI_COMPILER_MODEL")
        or "gpt-6-luna"
    )


# 클라이언트 재시도 횟수. System A 의 s6_generate(OpenAI·Anthropic 모두 max_retries=5)와 같다.
# 타임아웃은 넘기지 않는다. A 처럼 SDK 기본값(연결 5초, 응답 600초)을 쓴다.
# 예전에는 WIKI_AGENT_TIMEOUT(기본 120초, 연결 단계 포함)을 넘겨 C 만 먼저 끊겼고,
# 그 값은 config_hash 에도 없었다. (#27 A 기준 점검)
CLIENT_MAX_RETRIES = 5


# ---------------------------------------------------------------------------
# 라우팅: openai_responses / openai_chat / anthropic
# ---------------------------------------------------------------------------

def _get_route(model_cfg: dict) -> str:
    if model_cfg.get("provider") == "anthropic":
        return "anthropic"
    # 엔드포인트는 models.json에만 적는다. 환경변수로 바뀌면 실행마다 조건이
    # 달라져도 레코드에 드러나지 않는다. (#23 2절)
    base_url = _require_base_url(model_cfg)
    if "api.openai.com" in base_url:
        return "openai_responses"
    return "openai_chat"


# ---------------------------------------------------------------------------
# 클라이언트 생성
# ---------------------------------------------------------------------------

def _require_base_url(model_cfg: dict) -> str:
    """models.json 의 base_url 을 강제한다. (#23 2절)

    base_url 을 생략하면 SDK가 OPENAI_BASE_URL / ANTHROPIC_BASE_URL 환경변수를 읽는다.
    즉 "인자를 안 넘기는 것"은 엔드포인트 고정이 아니라 환경변수 지배를 허용하는 것이다.
    실측:
        OpenAI(api_key=k)                                  -> 환경변수 값
        OpenAI(api_key=k, base_url="https://api.openai.com/v1") -> 고정
    그래서 항상 명시적으로 넘기고, 없으면 실행을 막는다.
    """
    base_url = model_cfg.get("base_url")
    if not base_url:
        raise ValueError(
            f"models.json 의 {model_cfg.get('model_id')} 에 base_url 이 없습니다. "
            "엔드포인트를 환경변수에 맡기면 실행 조건이 레코드에 드러나지 않습니다."
        )
    return base_url


def _make_openai_client(model_cfg: dict):
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai 패키지가 필요합니다: pip install openai")
    key = os.environ.get(model_cfg["key_env"])
    if not key:
        raise ValueError(f"환경변수 {model_cfg['key_env']}가 설정되지 않았습니다.")
    return OpenAI(
        api_key=key,
        base_url=_require_base_url(model_cfg),   # 생략하면 env가 이긴다
        max_retries=CLIENT_MAX_RETRIES,
    )


def _make_anthropic_client(model_cfg: dict):
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic 패키지가 필요합니다: pip install anthropic")
    key = os.environ.get(model_cfg["key_env"])
    if not key:
        raise ValueError(f"환경변수 {model_cfg['key_env']}가 설정되지 않았습니다.")
    return anthropic.Anthropic(
        api_key=key,
        base_url=_require_base_url(model_cfg),   # ANTHROPIC_BASE_URL 을 막는다
        max_retries=CLIENT_MAX_RETRIES,
    )


# ---------------------------------------------------------------------------
# 속도 제한 + 호출 시간
# ---------------------------------------------------------------------------

def _enforce_interval(model_name: str, min_interval_s: float) -> None:
    """호출 간격 강제 (min_interval_s > 0인 경우만)."""
    if min_interval_s <= 0:
        return
    last = _last_call_times.get(model_name)
    if last is None:
        return
    wait = min_interval_s - (time.monotonic() - last)
    if wait > 0:
        global _interval_wait_s
        _interval_wait_s += wait
        time.sleep(wait)


def _call_api(call_fn, model_name: str, min_interval_s: float):
    """
    API 호출. 호출 전 간격을 강제하고, 호출에 걸린 시간을 잰다.
    Returns (response, failed_attempts: list[dict], api_ms: int)

    재시도는 SDK 에 맡긴다(CLIENT_MAX_RETRIES). System A 도 앱 수준 재시도 없이
    SDK 재시도만 쓴다. 예전의 429 전용 루프(최대 5번, 5~40초 대기)는 C 에만 재시도를
    더 주던 것이라 뺐다. (#27 A 기준 점검)
    api_ms 는 A 의 latency_ms.generate 처럼 LLM 호출 시간이다. SDK 재시도는 포함하고
    간격 강제 대기는 뺀다. perf_counter 는 시스템 시계 조정에 흔들리지 않는다.
    """
    _enforce_interval(model_name, min_interval_s)
    _last_call_times[model_name] = time.monotonic()
    t0 = time.perf_counter()
    response = call_fn()
    return response, [], int((time.perf_counter() - t0) * 1000)


# ---------------------------------------------------------------------------
# 위키 유틸
# ---------------------------------------------------------------------------

def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def _build_toc(wiki_root: Path) -> tuple[str, dict[str, Path]]:
    index: dict[str, Path] = {}
    lines: list[str] = []
    for path in sorted(wiki_root.rglob("*.md")):
        if path.stem.lower() == "readme":
            continue
        subdir = path.parent.name
        page_id = f"{subdir}/{path.stem}"
        index[page_id] = path
        raw = path.read_text(encoding="utf-8")
        body = _strip_frontmatter(raw)
        m = re.search(r"^#\s+(.+)", body, re.MULTILINE)
        title = m.group(1).strip() if m else path.stem
        lines.append(f"- {page_id} : {title}")
    toc = f"위키 페이지 목록 ({len(index)} 페이지):\n" + "\n".join(lines)
    return toc, index


def _read_page(page_id: str, index: dict[str, Path]) -> str:
    path = index.get(page_id)
    if path is None:
        return f"[오류] 페이지를 찾을 수 없습니다: {page_id}"
    return _strip_frontmatter(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 도구 정의 (공유)
# ---------------------------------------------------------------------------

_TOOL_DEFS = [
    {
        "name": "list_pages",
        "description": "위키 페이지 목록(목차)을 반환한다. 어떤 페이지가 있는지 파악할 때 먼저 호출한다.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_page",
        "description": "지정한 위키 페이지의 전문을 반환한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "페이지 ID (예: clusters/0x0006-on-off). list_pages 결과에 나온 ID를 그대로 사용한다.",
                }
            },
            "required": ["page_id"],
        },
    },
    {
        "name": "submit_answer",
        "description": "최종 답변을 제출한다. 이 도구를 호출하면 루프가 종료된다.",
        "parameters": {
            "type": "object",
            "properties": {
                # 언어 지시는 시스템 프롬프트의 "Answer in the same language as the question."
                # 하나뿐이다(A 와 같음). 예전의 "(한국어)"는 C 에만 있던 지시라 뺐다. (#27 A 기준 점검)
                "answer": {"type": "string", "description": "질의에 대한 최종 답변."},
                "cited_pages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "답변 근거로 사용한 페이지 ID 목록.",
                },
            },
            "required": ["answer", "cited_pages"],
        },
    },
]


def _tools_responses():
    return [
        {"type": "function", "name": t["name"], "description": t["description"], "parameters": t["parameters"]}
        for t in _TOOL_DEFS
    ]


def _tools_chat():
    return [
        {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
        for t in _TOOL_DEFS
    ]


def _tools_anthropic():
    return [
        {"name": t["name"], "description": t["description"], "input_schema": t["parameters"]}
        for t in _TOOL_DEFS
    ]


# ---------------------------------------------------------------------------
# 시스템 프롬프트
# ---------------------------------------------------------------------------

# 근거가 없을 때 내놓아야 하는 정확한 문구.
# System A/B(s6_generate.ABSTAIN_PHRASE)와 글자 그대로 동일해야 한다. 마침표 없음.
ABSTAIN_PHRASE = "제공된 문서에서 확인되지 않음"
# 출력 상한. System A 의 participants.yaml defaults.max_tokens(16000)와 같다.
# 환경변수로 바꾸지 않는다. 예전에는 WIKI_AGENT_MAX_OUTPUT_TOKENS 로 바뀌었는데,
# Anthropic 경로는 16000 을 따로 박아 두어 모델마다 상한이 달라질 수 있었다. (#27 A 기준 점검)
MAX_OUTPUT_TOKENS = 16000

# 질문 뒤에 붙는 문장. A 의 s6_generate.build_prompt 끝 문장
# "Answer using only the context above, citing [chunk_id] for each claim." 에 대응한다.
# A 는 생성 직전에 규칙 1·3을 한 번 더 말하므로 C 도 같은 자리에서 말한다.
# 인용 대상만 C 의 방식(cited_pages 의 페이지 ID)으로 바뀐다. (#27 A 기준 점검)
C_USER_TAIL = ("Answer using only the wiki pages you read, citing their page ids in "
               "cited_pages for each claim.")


def _build_user_message(query: str) -> str:
    """첫 user 메시지. A 의 build_prompt 와 같은 틀에서 <context> 만 빠진다(문맥은 도구로 읽는다)."""
    return f"<question>\n{query}\n</question>\n\n{C_USER_TAIL}"


def _build_system_prompt() -> str:
    """에이전트 시스템 프롬프트. A 영어 원문을 쓴다. (9/30 팀 결정)

    규칙 1·2·4와 머리말·맺음말은 System A/B 의 s6_generate.SYSTEM_PROMPT 와
    **글자 그대로 같다**. 번역본을 쓰면 프롬프트 차이가 시스템 간 변수로 남는다.
    C 고유 차이는 두 군데뿐이다:
      - 문맥이 주어지는 방식(검색 결과 일괄 → 위키 탐색 도구)
      - 규칙 3의 인용 대상([chunk_id] → cited_pages 의 페이지 ID)
      - 규칙 5(제출 경로). A·B 는 본문만 쓰면 되지만 C 는 도구로 제출해야 기록된다.
        기권 조건은 규칙 1에만 둔다 — 5번에 기권 문구를 또 쓰면 별개의 기권 조건처럼
        읽혀 C 기권률이 올라간다. (#23 리뷰)
    tests/test_prompt_parity.py 가 공통 문장의 일치를 검사한다.
    """
    return (
        "You are a technical documentation assistant for the Matter smart home "
        "standard and the connectedhomeip SDK.\n"
        "\n"
        "You read the documentation through a wiki. Call list_pages to see the table "
        "of contents, read_page to read a page in full, and submit_answer to submit "
        "your final answer. The pages you read are your context.\n"
        "\n"
        "Answer ONLY from the provided context. Follow these rules without exception:\n"
        "\n"
        "1. Never use knowledge outside the provided context. If the context does not "
        f'contain the answer, reply exactly: "{ABSTAIN_PHRASE}"\n'
        "2. Copy identifiers verbatim. Cluster names, attribute names, command names "
        "and hex IDs (e.g. OnOff, TemperatureSetpoint, 0x0201) must appear exactly as "
        "written in the context. Never translate, reformat or guess them.\n"
        "3. Cite every claim. List the page id of every page that supports a factual "
        "claim in the cited_pages argument of submit_answer. Use only page ids you "
        "actually read with read_page.\n"
        "4. Be concise. Do not add caveats, summaries of your own process, or "
        "recommendations that are not in the context.\n"
        "5. Deliver every answer through the answer argument of submit_answer, "
        "including when you decline under rule 1. Text written without calling the "
        "tool is not recorded.\n"
        "\n"
        "Answer in the same language as the question."
    )


# ---------------------------------------------------------------------------
# 토큰 사용량 추출 (provider별)
# ---------------------------------------------------------------------------

def _tokens_responses(usage) -> dict:
    if usage is None:
        return {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    details = getattr(usage, "input_tokens_details", None)
    cache_read = getattr(details, "cached_tokens", None) if details else None
    return {
        "prompt_tokens": getattr(usage, "input_tokens", None),
        "cache_read": cache_read,
        # Responses API: 캐시 쓰기는 input_tokens_details 안에 있다 (최상위 아님)
        "cache_write": getattr(details, "cache_write_tokens", None) if details else None,
        "output_tokens": getattr(usage, "output_tokens", None),
    }


def _tokens_chat(usage) -> dict:
    if usage is None:
        return {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    details = getattr(usage, "prompt_tokens_details", None)
    # 캐시 읽기 위치가 provider마다 다르다:
    #   OpenAI 호환 표준 prompt_tokens_details.cached_tokens,
    #   DeepSeek 최상위 prompt_cache_hit_tokens, Kimi 최상위 cached_tokens
    cache_read = getattr(details, "cached_tokens", None) if details else None
    if cache_read is None:
        cache_read = getattr(usage, "prompt_cache_hit_tokens", None)
    if cache_read is None:
        cache_read = getattr(usage, "cached_tokens", None)
    # 캐시 쓰기: Kimi는 prompt_tokens_details.cache_write_tokens
    cache_write = getattr(details, "cache_write_tokens", None) if details else None
    if cache_write is None:
        cache_write = getattr(usage, "cache_write_tokens", None)
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "cache_read": cache_read,
        "cache_write": cache_write,
        "output_tokens": getattr(usage, "completion_tokens", None),
    }


def _tokens_anthropic(usage) -> dict:
    if usage is None:
        return {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    # Anthropic input_tokens는 캐시 읽기·쓰기를 뺀 나머지다.
    # OpenAI와 같은 기준(캐시 포함 전체)으로 맞춰 prompt_tokens에 합친다.
    inp = getattr(usage, "input_tokens", None)
    cr = getattr(usage, "cache_read_input_tokens", None)
    cw = getattr(usage, "cache_creation_input_tokens", None)
    total = None if inp is None else inp + (cr or 0) + (cw or 0)
    return {
        "prompt_tokens": total,
        "cache_read": cr,
        "cache_write": cw,
        "output_tokens": getattr(usage, "output_tokens", None),
    }


# 온전히 끝난 종료 사유. 이 밖의 사유는 모두 잘림·차단·거절로 보고 그 턴에서 멈춘다.
# A 의 GenerationError 처럼 허용 목록으로 판정한다(막을 사유만 나열하면
# model_context_window_exceeded, max_messages, failed 같은 사유가 빠진다). (#27 3차 리뷰 1)
# 도구를 부르는 정상 턴도 tool_calls(Chat) / tool_use(Anthropic) / completed(Responses) 로 끝난다.
NORMAL_STOP_REASONS = {
    "stop",            # Chat Completions: 본문으로 끝남
    "tool_calls",      # Chat Completions: 도구 호출
    "function_call",   # Chat Completions: 예전 이름
    "completed",       # Responses: status
    "end_turn",        # Anthropic
    "stop_sequence",   # Anthropic
    "tool_use",        # Anthropic: 도구 호출
}

# 대표적인 잘림·차단·거절 사유(설명과 테스트용). 판정은 NORMAL_STOP_REASONS 로 한다.
HARD_STOP_REASONS = {
    "length",              # Chat Completions: 출력 상한
    "content_filter",      # Chat Completions: 차단
    "max_output_tokens",   # Responses: incomplete_details.reason
    "incomplete",          # Responses: status
    "refusal",             # 거절
    "max_tokens",          # Anthropic: 출력 상한
}


def _hard_stop(finish_reason, had_tool_calls: bool = False):
    """온전하지 않은 종료면 그 사유를 돌려준다. 아니면 None.

    도구 호출 여부와 관계없이 종료 사유로만 판단한다. 도구 인자를 쓰다가 출력 상한에
    걸리면 length(Chat), max_output_tokens(Responses), max_tokens(Anthropic)로 오기
    때문이다. 호출하는 쪽은 도구 인자를 읽기 전에 이 판정을 한다. (#27 3차 리뷰 1)
    finish_reason 이 None(제공자가 보고하지 않음)이면 판단할 수 없어 정상으로 둔다.
    had_tool_calls 는 예전 호출 형태를 위해 남겨 둔 인자이고 판정에 쓰지 않는다.
    """
    if finish_reason is None or finish_reason in NORMAL_STOP_REASONS:
        return None
    return finish_reason


def _turn_meta(response) -> dict:
    """턴별 종료 사유와 원본 usage. 원본을 남겨 두면 토큰 추출 규칙이 바뀌어도 재실행 없이 다시 계산할 수 있다."""
    finish_reason = None
    choices = getattr(response, "choices", None)
    if choices:  # Chat Completions (DeepSeek, Kimi)
        finish_reason = getattr(choices[0], "finish_reason", None)
    elif getattr(response, "stop_reason", None) is not None:  # Anthropic
        finish_reason = response.stop_reason
    else:  # OpenAI Responses: 끝까지 생성되면 completed, 잘리면 incomplete_details.reason
        inc = getattr(response, "incomplete_details", None)
        finish_reason = getattr(inc, "reason", None) or getattr(response, "status", None)
    usage = getattr(response, "usage", None)
    try:
        usage_raw = usage.model_dump() if usage is not None and hasattr(usage, "model_dump") else None
    except Exception:
        usage_raw = None
    return {"finish_reason": finish_reason, "usage_raw": usage_raw}


def _sum_tokens(a: dict, b: dict) -> dict:
    """열별 누적. None + N = N, None + None = None."""
    result = {}
    for k in ("prompt_tokens", "cache_read", "cache_write", "output_tokens"):
        av, bv = a.get(k), b.get(k)
        if av is None and bv is None:
            result[k] = None
        elif av is None:
            result[k] = bv
        elif bv is None:
            result[k] = av
        else:
            result[k] = av + bv
    return result


# ---------------------------------------------------------------------------
# 도구 실행 (공통)
# ---------------------------------------------------------------------------

def _execute_tool(
    fn_name: str,
    fn_args: dict,
    toc_text: str,
    page_index: dict,
    retrieved_pages: list,
    page_evidence: list,
    turn: int,
    deliver: bool = True,
) -> tuple[str, bool, str, list, str | None]:
    """
    반환: (result_text, is_final, answer, cited_pages, sha256_or_none)
    retrieved_pages, page_evidence는 in-place 업데이트.
    deliver=False 는 submit_answer 와 같은 응답에 온 read_page 다. 루프가 제출로 끝나서
    그 결과는 모델에게 가지 않으므로 문맥(retrieved_pages → citations)에 넣지 않는다.
    A 의 citations 도 실제로 프롬프트에 들어간 청크뿐이다. (#27 A 기준 점검)
    """
    if fn_name == "list_pages":
        return toc_text, False, "", [], None

    elif fn_name == "read_page":
        pid = fn_args.get("page_id", "")
        if not deliver:
            return "(제출과 같은 응답이라 전달되지 않음)", False, "", [], None
        result_text = _read_page(pid, page_index)
        path = page_index.get(pid)
        sha256 = None
        if pid and pid in page_index:
            if pid not in retrieved_pages:
                retrieved_pages.append(pid)
            if path is not None:
                sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
                page_evidence.append({"path": str(path), "sha256": sha256, "turn": turn})
        return result_text, False, "", [], sha256

    elif fn_name == "submit_answer":
        answer = fn_args.get("answer", "")
        cited = fn_args.get("cited_pages", [])
        return "답변이 제출되었습니다.", True, answer, cited, None

    else:
        return f"[오류] 알 수 없는 도구: {fn_name}", False, "", [], None


# ---------------------------------------------------------------------------
# 공통 결과 패키징
# ---------------------------------------------------------------------------

def _make_result(
    query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
    page_evidence, reasoning_applied, reasoning_note, reasoning_config_sent,
    status, failed_attempts, error=None,
) -> dict:
    # LLM 호출 시간 합. run_batch 가 latency_ms.generate 에 넣는다(A 의 generate 와 같은 뜻).
    llm_ms = sum(int(t.get("api_ms") or 0) for t in turn_details)
    return {
        "llm_ms": llm_ms,
        "query": query,
        "answer": answer,
        "retrieved": {"wiki_pages": retrieved_pages},
        "cited_pages": cited_pages,
        "turns": len(turn_details),
        "token_usage": total_usage,
        "turn_details": turn_details,
        "page_evidence": page_evidence,
        "reasoning_applied": reasoning_applied,
        "reasoning_note": reasoning_note,
        "reasoning_config_sent": reasoning_config_sent,
        "status": status,
        "error": error,
        "failed_attempts": failed_attempts,
    }


# ---------------------------------------------------------------------------
# OpenAI Responses API 루프
# ---------------------------------------------------------------------------

def _run_openai_responses(query, model_cfg, sys_prompt, toc_text, page_index, max_turns, verbose):
    client = _make_openai_client(model_cfg)
    model_name = model_cfg["model_id"]
    model_key = model_cfg.get("model_id", "")  # for _call_api key
    tools = _tools_responses()
    min_interval_s = float(model_cfg.get("min_interval_s", 0))

    reasoning_cfg = dict(model_cfg.get("reasoning_config") or {})
    active_reasoning = dict(reasoning_cfg)
    reasoning_applied = bool(reasoning_cfg)
    reasoning_note = None

    input_items: list = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": _build_user_message(query)},
    ]

    retrieved_pages: list = []
    cited_pages: list = []
    answer = ""
    page_evidence: list = []
    turn_details: list = []
    all_failed: list = []
    total_usage = {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    status = "ok"
    stop_error = None   # 잘림·거절로 끊긴 경우의 사유 (#23 리뷰)
    submitted = False   # submit_answer로 끝났는가 (#23 3절)

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] Responses API 호출 중...", file=sys.stderr)

        # 요청 파라미터 구성
        req = {
            "model": model_name,
            "input": input_items,
            "tools": tools,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        }
        req_with_r = {**req, **active_reasoning} if active_reasoning else req

        # 400(파라미터 거부) 시 자동 재시도하지 않는다.
        # 추론 강도를 조용히 빼고 다시 부르면 통제 실패가 정상 종료로 가려진다. (#23 2절)
        # 호출이 끝내 실패하면 예외를 그냥 올리지 않는다. 앞 턴의 과금 토큰과
        # invocations 줄이 사라지기 때문이다. status=error 로 끊고 기록은 남긴다. (#23 리뷰)
        try:
            response, failed, api_ms = _call_api(
                lambda r=req_with_r: client.responses.create(**r),
                model_key, min_interval_s,
            )
            all_failed.extend(failed)
        except Exception as exc:  # noqa: BLE001
            err = _error_text(exc)
            all_failed.append({
                "attempt": f"turn{turn}-final",
                "error": err[:500],
                "wait_s": 0,
                "ts": time.time(),
            })
            status = "error"
            stop_error = err
            break

        usage = _tokens_responses(getattr(response, "usage", None))
        total_usage = _sum_tokens(total_usage, usage)
        meta = _turn_meta(response)

        turn_calls: list[dict] = []
        final_answer_found = False

        # 출력 상한·차단·거절로 끝난 턴은 도구 인자를 읽기 전에 멈춘다. 잘린 인자를 읽다가
        # 예외가 나거나 잘린 본문이 답이 되지 않게 하고, 같은 대화로 다시 부르지도 않는다
        # (같은 사유로 또 잘리고 과금만 늘어난다). 이 턴의 과금분은 turn_details 에 남는다. (#27 3차 리뷰 1)
        stop = _hard_stop(meta.get("finish_reason"))
        if stop:
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            status = "error"
            stop_error = f"응답이 온전하지 않음 (finish_reason={stop})"
            break

        try:
            output = list(response.output)
            # 도구 호출이 하나라도 있으면 이 턴은 탐색 중이다. 같은 응답의 메시지(서두 문장)를
            # 답으로 보지 않는다. 예전에는 서두 문장이 답이 되어 no_submit 으로 끝났다. (#27 A 기준 점검)
            has_fc = any(getattr(i, "type", "") == "function_call" for i in output)
            has_submit = any(getattr(i, "type", "") == "function_call"
                             and getattr(i, "name", "") == "submit_answer" for i in output)
            final_texts: list = []
            if has_fc:
                # 추론(reasoning) 항목과 id 가 붙은 function_call 을 받은 순서 그대로 다음 입력에 넣는다.
                # 예전에는 function_call 만 새로 만들어 넣어 GPT 만 매 턴 추론을 처음부터 다시 했다.
                # Claude(thinking 블록)와 DeepSeek·Kimi(메시지 전체)는 이전 추론을 넘기고 있었다. (#27 A 기준 점검)
                input_items.extend(output)
            for item in output:
                item_type = getattr(item, "type", "")
                if item_type == "function_call":
                    fn_name = item.name
                    fn_args = json.loads(item.arguments)
                    if verbose:
                        print(f"  → {fn_name}({fn_args})", file=sys.stderr)

                    result_text, is_final, ans, cited, sha256 = _execute_tool(
                        fn_name, fn_args, toc_text, page_index,
                        retrieved_pages, page_evidence, turn,
                        deliver=not has_submit,
                    )
                    if is_final:
                        answer = ans
                        cited_pages = cited
                        final_answer_found = True
                        submitted = True

                    turn_calls.append({
                        "tool": fn_name,
                        "args": fn_args,
                        "result_len": len(result_text),
                        "sha256": sha256,
                    })

                    input_items.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": result_text,
                    })

                elif item_type == "message":
                    for block in getattr(item, "content", []):
                        if getattr(block, "type", "") == "refusal":
                            # 거절은 답이 아니다. 잘림과 같은 기준으로 오류로 남긴다. (#23 리뷰)
                            refused = getattr(block, "refusal", None) or "refusal"
                            status = "error"
                            stop_error = f"모델이 거절함: {str(refused)[:200]}"
                            final_answer_found = True
                        elif hasattr(block, "text") and not has_fc and not submitted:
                            # 제출한 답을 뒤따르는 텍스트가 덮어쓰지 않게 한다. 본문 조각은 A 처럼
                            # 모두 이어 붙인다(마지막 조각만 남기지 않는다). (#27 A 기준 점검)
                            final_texts.append(block.text or "")
                            answer = "".join(final_texts)
                            final_answer_found = True
        except Exception as exc:  # noqa: BLE001
            # 응답을 받은 뒤의 처리(도구 인자 파싱·도구 실행)에서 예외가 나도 앞 턴까지의
            # 과금 토큰과 기록을 남긴 채 끊는다. 예전에는 run_batch 까지 올라가 전부 0 이 됐다. (#27 3차 리뷰 2)
            err = _error_text(exc)
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            all_failed.append({
                "attempt": f"turn{turn}-after-response",
                "error": err[:500],
                "wait_s": 0,
                "ts": time.time(),
            })
            status = "error"
            stop_error = err
            break

        if not turn_calls and not final_answer_found:
            final_answer_found = True

        turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})

        if verbose:
            print(
                f"  usage: prompt={usage['prompt_tokens']} "
                f"cache_read={usage['cache_read']} output={usage['output_tokens']}",
                file=sys.stderr,
            )

        if final_answer_found:
            if verbose:
                print(f"[완료] {turn}턴 종료.", file=sys.stderr)
            break
    else:
        status = "max_turns"

    if status == "ok" and not submitted:
        # 도구를 쓰지 않고 본문만 반환한 경우. 근거 페이지가 없으므로 구분한다. (#23 3절)
        status = "no_submit"

    return _make_result(
        query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
        page_evidence, reasoning_applied, reasoning_note,
        (dict(reasoning_cfg) if reasoning_applied else None),
        status, all_failed, stop_error,
    )


# ---------------------------------------------------------------------------
# OpenAI Chat Completions 루프
# ---------------------------------------------------------------------------

def _run_openai_chat(query, model_cfg, sys_prompt, toc_text, page_index, max_turns, verbose):
    client = _make_openai_client(model_cfg)
    model_name = model_cfg["model_id"]
    model_key = model_cfg.get("model_id", "")
    tools = _tools_chat()
    min_interval_s = float(model_cfg.get("min_interval_s", 0))

    reasoning_cfg = dict(model_cfg.get("reasoning_config") or {})
    active_reasoning = dict(reasoning_cfg)
    reasoning_applied = bool(reasoning_cfg)
    reasoning_note = None

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": _build_user_message(query)},
    ]

    retrieved_pages: list = []
    cited_pages: list = []
    answer = ""
    page_evidence: list = []
    turn_details: list = []
    all_failed: list = []
    total_usage = {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    status = "ok"
    stop_error = None   # 잘림·거절로 끊긴 경우의 사유 (#23 리뷰)
    submitted = False   # submit_answer로 끝났는가 (#23 3절)

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] Chat Completions 호출 중...", file=sys.stderr)

        base_req = {
            "model": model_name,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            # DeepSeek은 max_tokens만 읽고, A·B는 그 외 모델에 max_completion_tokens를 쓴다
            model_cfg.get("max_tokens_param", "max_tokens"): MAX_OUTPUT_TOKENS,
        }
        req = {**base_req, **active_reasoning} if active_reasoning else base_req

        # 400(파라미터 거부) 시 자동 재시도하지 않는다.
        # 추론 강도를 조용히 빼고 다시 부르면 통제 실패가 정상 종료로 가려진다. (#23 2절)
        # 호출이 끝내 실패하면 예외를 그냥 올리지 않는다. 앞 턴의 과금 토큰과
        # invocations 줄이 사라지기 때문이다. status=error 로 끊고 기록은 남긴다. (#23 리뷰)
        try:
            response, failed, api_ms = _call_api(
                lambda r=req: client.chat.completions.create(**r),
                model_key, min_interval_s,
            )
            all_failed.extend(failed)
        except Exception as exc:  # noqa: BLE001
            err = _error_text(exc)
            all_failed.append({
                "attempt": f"turn{turn}-final",
                "error": err[:500],
                "wait_s": 0,
                "ts": time.time(),
            })
            status = "error"
            stop_error = err
            break

        usage = _tokens_chat(getattr(response, "usage", None))
        total_usage = _sum_tokens(total_usage, usage)
        meta = _turn_meta(response)

        turn_calls: list[dict] = []
        final_answer_found = False

        # choices 가 빈 응답이면 과금분을 남긴 채 끊는다. 예전에는 여기서 IndexError 가 나서
        # 앞 턴까지의 기록이 사라졌다. (#27 3차 리뷰 2)
        if not getattr(response, "choices", None):
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            status = "error"
            stop_error = "응답에 choices 가 없음"
            break

        # 출력 상한·차단·거절로 끝난 턴은 도구 인자를 읽기 전에 멈춘다. 잘린 인자를 읽다가
        # 예외가 나거나 잘린 본문이 답이 되지 않게 하고, 같은 대화로 다시 부르지도 않는다
        # (같은 사유로 또 잘리고 과금만 늘어난다). 이 턴의 과금분은 turn_details 에 남는다. (#27 3차 리뷰 1)
        stop = _hard_stop(meta.get("finish_reason"))
        if stop:
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            status = "error"
            stop_error = f"응답이 온전하지 않음 (finish_reason={stop})"
            break

        try:
            msg = response.choices[0].message
            if msg.tool_calls:
                messages.append(msg)
                has_submit = any(getattr(getattr(t, "function", None), "name", "") == "submit_answer"
                                 for t in msg.tool_calls)
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    fn_args = json.loads(tc.function.arguments)
                    if verbose:
                        print(f"  → {fn_name}({fn_args})", file=sys.stderr)

                    result_text, is_final, ans, cited, sha256 = _execute_tool(
                        fn_name, fn_args, toc_text, page_index,
                        retrieved_pages, page_evidence, turn,
                        deliver=not has_submit,
                    )
                    if is_final:
                        answer = ans
                        cited_pages = cited
                        final_answer_found = True
                        submitted = True

                    turn_calls.append({
                        "tool": fn_name,
                        "args": fn_args,
                        "result_len": len(result_text),
                        "sha256": sha256,
                    })

                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result_text})
            else:
                answer = msg.content or ""
                final_answer_found = True
        except Exception as exc:  # noqa: BLE001
            # 응답을 받은 뒤의 처리(도구 인자 파싱·도구 실행)에서 예외가 나도 앞 턴까지의
            # 과금 토큰과 기록을 남긴 채 끊는다. 예전에는 run_batch 까지 올라가 전부 0 이 됐다. (#27 3차 리뷰 2)
            err = _error_text(exc)
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            all_failed.append({
                "attempt": f"turn{turn}-after-response",
                "error": err[:500],
                "wait_s": 0,
                "ts": time.time(),
            })
            status = "error"
            stop_error = err
            break

        turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})

        if verbose:
            print(
                f"  usage: prompt={usage['prompt_tokens']} "
                f"cache_read={usage['cache_read']} output={usage['output_tokens']}",
                file=sys.stderr,
            )

        if final_answer_found:
            if verbose:
                print(f"[완료] {turn}턴 종료.", file=sys.stderr)
            break
    else:
        status = "max_turns"

    if status == "ok" and not submitted:
        # 도구를 쓰지 않고 본문만 반환한 경우. 근거 페이지가 없으므로 구분한다. (#23 3절)
        status = "no_submit"

    return _make_result(
        query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
        page_evidence, reasoning_applied, reasoning_note,
        (dict(reasoning_cfg) if reasoning_applied else None),
        status, all_failed, stop_error,
    )


# ---------------------------------------------------------------------------
# Anthropic Messages API 루프
# ---------------------------------------------------------------------------

def _run_anthropic(query, model_cfg, sys_prompt, toc_text, page_index, max_turns, verbose):
    client = _make_anthropic_client(model_cfg)
    model_name = model_cfg["model_id"]
    model_key = model_cfg.get("model_id", "")
    tools = _tools_anthropic()
    min_interval_s = float(model_cfg.get("min_interval_s", 0))

    reasoning_cfg = dict(model_cfg.get("reasoning_config") or {})
    active_reasoning = dict(reasoning_cfg)
    reasoning_applied = bool(reasoning_cfg)
    reasoning_note = None

    messages = [{"role": "user", "content": _build_user_message(query)}]
    narration = ""      # 도구를 부른 턴의 본문. 답으로 쓰지 않는다

    retrieved_pages: list = []
    cited_pages: list = []
    answer = ""
    page_evidence: list = []
    turn_details: list = []
    all_failed: list = []
    total_usage = {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    status = "ok"
    stop_error = None   # 잘림·거절로 끊긴 경우의 사유 (#23 리뷰)
    submitted = False   # submit_answer로 끝났는가 (#23 3절)

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] Anthropic Messages 호출 중...", file=sys.stderr)

        base_req = {
            "model": model_name,
            "max_tokens": MAX_OUTPUT_TOKENS,   # A 와 같은 16000. 다른 경로와 같은 상수를 쓴다
            "system": sys_prompt,
            "messages": messages,
            "tools": tools,
        }
        req = {**base_req, **active_reasoning} if active_reasoning else base_req

        # 400(파라미터 거부) 시 자동 재시도하지 않는다.
        # 추론 강도를 조용히 빼고 다시 부르면 통제 실패가 정상 종료로 가려진다. (#23 2절)
        # 호출이 끝내 실패하면 예외를 그냥 올리지 않는다. 앞 턴의 과금 토큰과
        # invocations 줄이 사라지기 때문이다. status=error 로 끊고 기록은 남긴다. (#23 리뷰)
        try:
            response, failed, api_ms = _call_api(
                lambda r=req: client.messages.create(**r),
                model_key, min_interval_s,
            )
            all_failed.extend(failed)
        except Exception as exc:  # noqa: BLE001
            err = _error_text(exc)
            all_failed.append({
                "attempt": f"turn{turn}-final",
                "error": err[:500],
                "wait_s": 0,
                "ts": time.time(),
            })
            status = "error"
            stop_error = err
            break

        usage = _tokens_anthropic(getattr(response, "usage", None))
        total_usage = _sum_tokens(total_usage, usage)
        meta = _turn_meta(response)

        turn_calls: list[dict] = []
        tool_results: list = []
        final_answer_found = False

        # 출력 상한·차단·거절로 끝난 턴은 도구 인자를 읽기 전에 멈춘다. 잘린 인자를 읽다가
        # 예외가 나거나 잘린 본문이 답이 되지 않게 하고, 같은 대화로 다시 부르지도 않는다
        # (같은 사유로 또 잘리고 과금만 늘어난다). 이 턴의 과금분은 turn_details 에 남는다. (#27 3차 리뷰 1)
        stop = _hard_stop(meta.get("finish_reason"))
        if stop:
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            status = "error"
            stop_error = f"응답이 온전하지 않음 (finish_reason={stop})"
            break

        try:
            # thinking 블록 포함한 전체 content 보존. content 가 없는 응답(프록시가 돌려준
            # HTML 등)도 아래 except 로 보내려고 try 안에 둔다.
            messages.append({"role": "assistant", "content": response.content})
            has_submit = any(getattr(b, "type", "") == "tool_use" and getattr(b, "name", "") == "submit_answer"
                             for b in response.content)
            turn_texts: list = []
            for block in response.content:
                block_type = getattr(block, "type", "")
                if block_type == "tool_use":
                    fn_name = block.name
                    fn_args = block.input
                    if verbose:
                        print(f"  → {fn_name}({fn_args})", file=sys.stderr)

                    result_text, is_final, ans, cited, sha256 = _execute_tool(
                        fn_name, fn_args, toc_text, page_index,
                        retrieved_pages, page_evidence, turn,
                        deliver=not has_submit,
                    )
                    if is_final:
                        answer = ans
                        cited_pages = cited
                        final_answer_found = True
                        submitted = True

                    turn_calls.append({
                        "tool": fn_name,
                        "args": fn_args,
                        "result_len": len(result_text),
                        "sha256": sha256,
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })
                elif block_type == "text":
                    # 이 응답의 본문 조각을 모은다. 답으로 쓸지는 아래에서 정한다.
                    if block.text:
                        turn_texts.append(block.text)
        except Exception as exc:  # noqa: BLE001
            # 응답을 받은 뒤의 처리(도구 인자 파싱·도구 실행)에서 예외가 나도 앞 턴까지의
            # 과금 토큰과 기록을 남긴 채 끊는다. 예전에는 run_batch 까지 올라가 전부 0 이 됐다. (#27 3차 리뷰 2)
            err = _error_text(exc)
            turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})
            all_failed.append({
                "attempt": f"turn{turn}-after-response",
                "error": err[:500],
                "wait_s": 0,
                "ts": time.time(),
            })
            status = "error"
            stop_error = err
            break

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
            # 도구를 부른 턴의 본문은 서두(narration)다. 답이 아니다. 오류·최대 턴으로 끝날 때만
            # partial_answer 로 남기려고 따로 둔다. (#27 A 기준 점검)
            if turn_texts and not submitted:
                narration = "".join(turn_texts)
        else:
            # 판정을 통과했고 도구 호출이 없으면 end_turn·stop_sequence 로 끝난 것이다.
            # 예전에는 end_turn 만 끝으로 봐서, stop_sequence 면 같은 대화로 다시 불렀다.
            # 답은 이 마지막 응답의 본문만, A 처럼 조각을 모두 이어 붙인 것이다
            # (s6_generate.py 282행). 본문이 없으면 빈 답이 되어 run_batch 가 A 처럼 오류로
            # 남기고 다시 돌린다. 예전에는 앞 턴의 서두가 답으로 남았다. (#27 A 기준 점검)
            if not submitted:
                answer = "".join(turn_texts)
            final_answer_found = True

        turn_details.append({"turn": turn, "calls": turn_calls, "api_ms": api_ms, **usage, **meta})

        if verbose:
            print(
                f"  usage: prompt={usage['prompt_tokens']} "
                f"cache_read={usage['cache_read']} output={usage['output_tokens']}",
                file=sys.stderr,
            )

        if final_answer_found:
            if verbose:
                print(f"[완료] {turn}턴 종료.", file=sys.stderr)
            break
    else:
        status = "max_turns"

    if status in ("error", "max_turns") and not answer and narration:
        answer = narration      # run_batch 가 partial_answer 로 옮기고 answer 는 비운다

    if status == "ok" and not submitted:
        # 도구를 쓰지 않고 본문만 반환한 경우. 근거 페이지가 없으므로 구분한다. (#23 3절)
        status = "no_submit"

    return _make_result(
        query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
        page_evidence, reasoning_applied, reasoning_note,
        (dict(reasoning_cfg) if reasoning_applied else None),
        status, all_failed, stop_error,
    )


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def run_agent(
    query: str,
    max_turns: int = 30,
    verbose: bool = False,
    model: str | None = None,
    wiki_root=None,
) -> dict:
    """
    에이전트 루프 실행. provider를 자동 감지한다.

    반환값:
        query, answer, retrieved.wiki_pages, cited_pages, turns,
        token_usage {prompt_tokens, cache_read, cache_write, output_tokens},
        turn_details [{turn, calls:[{tool,args,result_len,sha256}], ...tokens}],
        page_evidence [{path, sha256, turn}],
        reasoning_applied, reasoning_note, reasoning_config_sent,
        status ("ok"|"max_turns"), failed_attempts
    """
    models_db = _load_models()
    model_name = model or _get_default_model()

    if model_name not in models_db:
        raise ValueError(f"models.json에 없는 모델입니다: {model_name}")

    model_cfg = models_db[model_name]
    route = _get_route(model_cfg)
    wiki_root_path = Path(wiki_root) if wiki_root else WIKI_ROOT

    if verbose:
        print(f"[에이전트] model={model_name} route={route} wiki={wiki_root_path}", file=sys.stderr)

    toc_text, page_index = _build_toc(wiki_root_path)
    sys_prompt = _build_system_prompt()

    if route == "openai_responses":
        return _run_openai_responses(query, model_cfg, sys_prompt, toc_text, page_index, max_turns, verbose)
    elif route == "openai_chat":
        return _run_openai_chat(query, model_cfg, sys_prompt, toc_text, page_index, max_turns, verbose)
    else:
        return _run_anthropic(query, model_cfg, sys_prompt, toc_text, page_index, max_turns, verbose)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _safe_console() -> None:
    """Windows 기본 콘솔(cp949)처럼 출력 인코딩이 모든 문자를 담지 못해도 멈추지 않게 한다.
    담지 못하는 문자는 '?' 로 바뀐다. (#27 동수님 리뷰 P1-1)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _safe_console()
    parser = argparse.ArgumentParser(description="LLM Wiki 에이전트 — 위키 탐색 기반 질의응답")
    parser.add_argument("--query", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--wiki-root", default=None)
    parser.add_argument("--output", help="결과 JSON 저장 경로")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    result = run_agent(
        query=args.query,
        max_turns=args.max_turns,
        verbose=args.verbose,
        model=args.model,
        wiki_root=args.wiki_root,
    )

    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"결과 저장: {args.output}", file=sys.stderr)
    else:
        print(output_json)

    print(
        f"\n[요약] model={args.model or _get_default_model()} turns={result['turns']} "
        f"retrieved={len(result['retrieved']['wiki_pages'])}페이지 "
        f"reasoning_applied={result['reasoning_applied']} status={result['status']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
