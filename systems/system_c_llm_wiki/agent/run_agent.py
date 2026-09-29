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


def _get_timeout() -> int:
    return int(os.environ.get("WIKI_AGENT_TIMEOUT", "120"))


# ---------------------------------------------------------------------------
# 라우팅: openai_responses / openai_chat / anthropic
# ---------------------------------------------------------------------------

def _get_route(model_cfg: dict) -> str:
    if model_cfg.get("provider") == "anthropic":
        return "anthropic"
    base_url = model_cfg.get("base_url") or ""
    if not base_url:
        env_key = model_cfg.get("base_url_env")
        if env_key:
            base_url = os.environ.get(env_key, "") or ""
    if not base_url or "api.openai.com" in base_url:
        return "openai_responses"
    return "openai_chat"


# ---------------------------------------------------------------------------
# 클라이언트 생성
# ---------------------------------------------------------------------------

def _make_openai_client(model_cfg: dict):
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai 패키지가 필요합니다: pip install openai")
    key = os.environ.get(model_cfg["key_env"])
    if not key:
        raise ValueError(f"환경변수 {model_cfg['key_env']}가 설정되지 않았습니다.")
    base_url = model_cfg.get("base_url") or ""
    if not base_url:
        env_key = model_cfg.get("base_url_env")
        if env_key:
            base_url = os.environ.get(env_key, "") or None
    kwargs: dict = {"api_key": key, "timeout": _get_timeout()}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _make_anthropic_client(model_cfg: dict):
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic 패키지가 필요합니다: pip install anthropic")
    key = os.environ.get(model_cfg["key_env"])
    if not key:
        raise ValueError(f"환경변수 {model_cfg['key_env']}가 설정되지 않았습니다.")
    return anthropic.Anthropic(api_key=key, timeout=_get_timeout())


# ---------------------------------------------------------------------------
# 속도 제한 + 429 재시도
# ---------------------------------------------------------------------------

def _enforce_interval(model_name: str, min_interval_s: float) -> None:
    """호출 간격 강제 (min_interval_s > 0인 경우만)."""
    if min_interval_s <= 0:
        return
    last = _last_call_times.get(model_name, 0.0)
    wait = min_interval_s - (time.time() - last)
    if wait > 0:
        time.sleep(wait)


def _is_rate_limit(exc: Exception) -> bool:
    code = getattr(exc, "status_code", None)
    return code == 429 or "429" in str(exc)


def _call_api(call_fn, model_name: str, min_interval_s: float, max_retries: int = 5):
    """
    API 호출. 호출 전 간격 강제, 429이면 지수 백오프로 재시도.
    Returns (response, failed_attempts: list[dict])
    """
    failed: list[dict] = []
    for attempt in range(max_retries):
        _enforce_interval(model_name, min_interval_s)
        _last_call_times[model_name] = time.time()
        try:
            return call_fn(), failed
        except Exception as e:
            if _is_rate_limit(e) and attempt < max_retries - 1:
                wait_s = 5 * (2 ** attempt)  # 5, 10, 20, 40, 80 s
                failed.append({
                    "attempt": attempt + 1,
                    "error": str(e)[:300],
                    "wait_s": wait_s,
                    "ts": time.time(),
                })
                time.sleep(wait_s)
            else:
                raise
    raise RuntimeError("unreachable")


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
                "answer": {"type": "string", "description": "질의에 대한 답변 (한국어)."},
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

def _build_system_prompt() -> str:
    return (
        "당신은 Matter/connectedhomeip 기술문서 위키를 탐색해 질문에 답하는 에이전트입니다.\n"
        "먼저 list_pages로 목차를 확인하고, 필요한 페이지를 read_page로 읽은 뒤, "
        "충분한 정보를 얻으면 submit_answer로 답변을 제출하세요.\n"
        "답변은 한국어로 작성하고, 근거 페이지 ID를 cited_pages에 포함하세요.\n"
        "위키에서 근거를 찾지 못하면 추측하지 말고, 반드시 정확히 "
        "`제공된 문서에서 확인되지 않음.` 만 답변으로 제출할 것."
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
        "cache_write": getattr(usage, "cache_write_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
    }


def _tokens_chat(usage) -> dict:
    if usage is None:
        return {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    details = getattr(usage, "prompt_tokens_details", None)
    cache_read = getattr(details, "cached_tokens", None) if details else None
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "cache_read": cache_read,
        "cache_write": getattr(usage, "cache_write_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
    }


def _tokens_anthropic(usage) -> dict:
    if usage is None:
        return {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    return {
        "prompt_tokens": getattr(usage, "input_tokens", None),
        "cache_read": getattr(usage, "cache_read_input_tokens", None),
        "cache_write": getattr(usage, "cache_creation_input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
    }


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
) -> tuple[str, bool, str, list, str | None]:
    """
    반환: (result_text, is_final, answer, cited_pages, sha256_or_none)
    retrieved_pages, page_evidence는 in-place 업데이트.
    """
    if fn_name == "list_pages":
        return toc_text, False, "", [], None

    elif fn_name == "read_page":
        pid = fn_args.get("page_id", "")
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
    status, failed_attempts,
) -> dict:
    return {
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
    reasoning_rejected = False

    input_items: list = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": query},
    ]

    retrieved_pages: list = []
    cited_pages: list = []
    answer = ""
    page_evidence: list = []
    turn_details: list = []
    all_failed: list = []
    total_usage = {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    status = "ok"

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] Responses API 호출 중...", file=sys.stderr)

        # 요청 파라미터 구성
        req = {
            "model": model_name,
            "input": input_items,
            "tools": tools,
            "max_output_tokens": 16000,
        }
        req_with_r = {**req, **active_reasoning} if (active_reasoning and not reasoning_rejected) else req

        try:
            response, failed = _call_api(
                lambda r=req_with_r: client.responses.create(**r),
                model_key, min_interval_s,
            )
            all_failed.extend(failed)
        except Exception as e:
            err_str = str(e)
            if (("400" in err_str or getattr(e, "status_code", None) == 400)
                    and active_reasoning and not reasoning_rejected):
                if verbose:
                    print(f"  [재시도] 400 오류, reasoning 제거: {e}", file=sys.stderr)
                active_reasoning = {}
                reasoning_applied = False
                reasoning_note = "provider rejected"
                reasoning_rejected = True
                response, failed = _call_api(
                    lambda r=req: client.responses.create(**r),
                    model_key, min_interval_s,
                )
                all_failed.extend(failed)
            else:
                raise

        usage = _tokens_responses(getattr(response, "usage", None))
        total_usage = _sum_tokens(total_usage, usage)

        turn_calls: list[dict] = []
        final_answer_found = False

        for item in response.output:
            item_type = getattr(item, "type", "")
            if item_type == "function_call":
                fn_name = item.name
                fn_args = json.loads(item.arguments)
                if verbose:
                    print(f"  → {fn_name}({fn_args})", file=sys.stderr)

                result_text, is_final, ans, cited, sha256 = _execute_tool(
                    fn_name, fn_args, toc_text, page_index,
                    retrieved_pages, page_evidence, turn,
                )
                if is_final:
                    answer = ans
                    cited_pages = cited
                    final_answer_found = True

                turn_calls.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result_len": len(result_text),
                    "sha256": sha256,
                })

                input_items.append({
                    "type": "function_call",
                    "call_id": item.call_id,
                    "name": item.name,
                    "arguments": item.arguments,
                })
                input_items.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": result_text,
                })

            elif item_type == "message":
                for block in getattr(item, "content", []):
                    if hasattr(block, "text"):
                        answer = block.text
                        final_answer_found = True

        if not turn_calls and not final_answer_found:
            final_answer_found = True

        turn_details.append({"turn": turn, "calls": turn_calls, **usage})

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

    return _make_result(
        query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
        page_evidence, reasoning_applied, reasoning_note,
        (dict(reasoning_cfg) if reasoning_applied else None),
        status, all_failed,
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
    reasoning_rejected = False

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": query},
    ]

    retrieved_pages: list = []
    cited_pages: list = []
    answer = ""
    page_evidence: list = []
    turn_details: list = []
    all_failed: list = []
    total_usage = {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    status = "ok"

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] Chat Completions 호출 중...", file=sys.stderr)

        base_req = {
            "model": model_name,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": 16000,
        }
        req = {**base_req, **active_reasoning} if (active_reasoning and not reasoning_rejected) else base_req

        try:
            response, failed = _call_api(
                lambda r=req: client.chat.completions.create(**r),
                model_key, min_interval_s,
            )
            all_failed.extend(failed)
        except Exception as e:
            err_str = str(e)
            if (("400" in err_str or getattr(e, "status_code", None) == 400)
                    and active_reasoning and not reasoning_rejected):
                if verbose:
                    print(f"  [재시도] 400 오류, reasoning 제거: {e}", file=sys.stderr)
                active_reasoning = {}
                reasoning_applied = False
                reasoning_note = "provider rejected"
                reasoning_rejected = True
                response, failed = _call_api(
                    lambda r=base_req: client.chat.completions.create(**r),
                    model_key, min_interval_s,
                )
                all_failed.extend(failed)
            else:
                raise

        msg = response.choices[0].message
        usage = _tokens_chat(getattr(response, "usage", None))
        total_usage = _sum_tokens(total_usage, usage)

        turn_calls: list[dict] = []
        final_answer_found = False

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                if verbose:
                    print(f"  → {fn_name}({fn_args})", file=sys.stderr)

                result_text, is_final, ans, cited, sha256 = _execute_tool(
                    fn_name, fn_args, toc_text, page_index,
                    retrieved_pages, page_evidence, turn,
                )
                if is_final:
                    answer = ans
                    cited_pages = cited
                    final_answer_found = True

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

        turn_details.append({"turn": turn, "calls": turn_calls, **usage})

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

    return _make_result(
        query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
        page_evidence, reasoning_applied, reasoning_note,
        (dict(reasoning_cfg) if reasoning_applied else None),
        status, all_failed,
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
    reasoning_rejected = False

    messages = [{"role": "user", "content": query}]

    retrieved_pages: list = []
    cited_pages: list = []
    answer = ""
    page_evidence: list = []
    turn_details: list = []
    all_failed: list = []
    total_usage = {"prompt_tokens": None, "cache_read": None, "cache_write": None, "output_tokens": None}
    status = "ok"

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] Anthropic Messages 호출 중...", file=sys.stderr)

        base_req = {
            "model": model_name,
            "max_tokens": 16000,
            "system": sys_prompt,
            "messages": messages,
            "tools": tools,
        }
        req = {**base_req, **active_reasoning} if (active_reasoning and not reasoning_rejected) else base_req

        try:
            response, failed = _call_api(
                lambda r=req: client.messages.create(**r),
                model_key, min_interval_s,
            )
            all_failed.extend(failed)
        except Exception as e:
            err_str = str(e)
            if (("400" in err_str or getattr(e, "status_code", None) == 400)
                    and active_reasoning and not reasoning_rejected):
                if verbose:
                    print(f"  [재시도] 400 오류, reasoning 제거: {e}", file=sys.stderr)
                active_reasoning = {}
                reasoning_applied = False
                reasoning_note = "provider rejected"
                reasoning_rejected = True
                response, failed = _call_api(
                    lambda r=base_req: client.messages.create(**r),
                    model_key, min_interval_s,
                )
                all_failed.extend(failed)
            else:
                raise

        usage = _tokens_anthropic(getattr(response, "usage", None))
        total_usage = _sum_tokens(total_usage, usage)

        # thinking 블록 포함한 전체 content 보존
        messages.append({"role": "assistant", "content": response.content})

        turn_calls: list[dict] = []
        tool_results: list = []
        final_answer_found = False

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
                )
                if is_final:
                    answer = ans
                    cited_pages = cited
                    final_answer_found = True

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
                if block.text:
                    answer = block.text

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        elif response.stop_reason == "end_turn":
            final_answer_found = True

        turn_details.append({"turn": turn, "calls": turn_calls, **usage})

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

    return _make_result(
        query, answer, retrieved_pages, cited_pages, turn_details, total_usage,
        page_evidence, reasoning_applied, reasoning_note,
        (dict(reasoning_cfg) if reasoning_applied else None),
        status, all_failed,
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

def main():
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
