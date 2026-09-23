# -*- coding: utf-8 -*-
"""
LLM Wiki 에이전트 루프 (System C) — run_agent.py
=================================================

위키 페이지를 탐색해 질문에 답하는 온라인 에이전트.
정적 전체주입(136K 토큰) 대신 필요한 페이지만 골라 읽는다.

사용법 (리포 루트에서):
    set -a; . ./.env.local; set +a
    python3 systems/system_c_llm_wiki/agent/run_agent.py \\
        --query "LaundryWasherMode가 지원하는 표준 모드 태그는?" \\
        --verbose

옵션:
    --query TEXT        질의 (필수)
    --output FILE       결과 JSON 저장 경로
    --max-turns N       최대 턴 수 (기본 30)
    --verbose           도구 호출 로그 출력
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 경로 설정 (리포 루트에서 실행한다고 가정)
# ---------------------------------------------------------------------------
WIKI_ROOT = Path("systems/system_c_llm_wiki/wiki")

# ---------------------------------------------------------------------------
# 모델 / 환경변수
# ---------------------------------------------------------------------------
def _get_model() -> str:
    return (
        os.environ.get("WIKI_AGENT_MODEL")
        or os.environ.get("WIKI_COMPILER_MODEL")
        or "gpt-5.6-luna"
    )

def _get_timeout() -> int:
    return int(os.environ.get("WIKI_AGENT_TIMEOUT", "120"))

# ---------------------------------------------------------------------------
# 위키 유틸 — 목차 생성 / 페이지 읽기
# ---------------------------------------------------------------------------

def _strip_frontmatter(text: str) -> str:
    """YAML 프론트매터(--- ... ---) 제거."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def _build_toc() -> tuple[str, dict[str, Path]]:
    """
    위키 디렉토리를 스캔해 목차 텍스트와 page_id → Path 매핑을 반환한다.

    page_id 형식: <subdir>/<stem>
    예: clusters/0x0006-on-off
        device-types/laundry-washer
        base/modebase
    """
    index: dict[str, Path] = {}
    lines: list[str] = []

    for path in sorted(WIKI_ROOT.rglob("*.md")):
        # README는 목차에서 제외
        if path.stem.lower() == "readme":
            continue
        subdir = path.parent.name  # clusters, device-types, base, ...
        page_id = f"{subdir}/{path.stem}"
        index[page_id] = path

        # 타이틀 추출 (첫 번째 # 헤더 또는 파일명)
        raw = path.read_text(encoding="utf-8")
        body = _strip_frontmatter(raw)
        title_match = re.search(r"^#\s+(.+)", body, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem

        lines.append(f"- {page_id} : {title}")

    toc = "위키 페이지 목록 ({} 페이지):\n".format(len(index))
    toc += "\n".join(lines)
    return toc, index


def _read_page(page_id: str, index: dict[str, Path]) -> str:
    """page_id에 해당하는 페이지 본문(프론트매터 제외)을 반환한다."""
    path = index.get(page_id)
    if path is None:
        return f"[오류] 페이지를 찾을 수 없습니다: {page_id}"
    raw = path.read_text(encoding="utf-8")
    return _strip_frontmatter(raw)


# ---------------------------------------------------------------------------
# OpenAI 클라이언트 초기화
# ---------------------------------------------------------------------------

def _make_client():
    try:
        from openai import OpenAI
    except ImportError:
        print("[오류] openai 패키지가 필요합니다: pip install openai", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[오류] OPENAI_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    kwargs = {"api_key": api_key, "timeout": _get_timeout()}
    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url

    return OpenAI(**kwargs)


# ---------------------------------------------------------------------------
# 도구 스키마 정의 (function calling)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_pages",
            "description": "위키 페이지 목록(목차)을 반환한다. 어떤 페이지가 있는지 파악할 때 먼저 호출한다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "submit_answer",
            "description": "최종 답변을 제출한다. 이 도구를 호출하면 루프가 종료된다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "질의에 대한 답변 (한국어).",
                    },
                    "cited_pages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "답변 근거로 사용한 페이지 ID 목록.",
                    },
                },
                "required": ["answer", "cited_pages"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# 토큰 사용량 추출
# ---------------------------------------------------------------------------

def _extract_token_usage(usage) -> dict:
    """
    팀 공용 스키마의 토큰 4열을 채운다.
    절대 합산하지 않는다 (CLAUDE.md 불변식).

    매핑:
      prompt_tokens  <- usage.prompt_tokens
      cache_read     <- usage.prompt_tokens_details.cached_tokens
      cache_write    <- usage.cache_creation_input_tokens (게이트웨이 확장)
      output_tokens  <- usage.completion_tokens
    """
    if usage is None:
        return {"prompt_tokens": 0, "cache_read": 0, "cache_write": 0, "output_tokens": 0}

    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    output_tokens = getattr(usage, "completion_tokens", 0) or 0

    cache_read = 0
    details = getattr(usage, "prompt_tokens_details", None)
    if details is not None:
        cache_read = getattr(details, "cached_tokens", 0) or 0

    # Azure OpenAI 게이트웨이 확장 필드
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0

    return {
        "prompt_tokens": prompt_tokens,
        "cache_read": cache_read,
        "cache_write": cache_write,
        "output_tokens": output_tokens,
    }


def _sum_token_usage(a: dict, b: dict) -> dict:
    """두 토큰 레코드를 열별로 합산한다 (누적용, 출력 레코드에는 쓰지 않음)."""
    return {k: a.get(k, 0) + b.get(k, 0) for k in a}


# ---------------------------------------------------------------------------
# 에이전트 루프
# ---------------------------------------------------------------------------

def run_agent(query: str, max_turns: int = 30, verbose: bool = False) -> dict:
    """
    에이전트 루프를 실행하고 결과 레코드를 반환한다.

    반환 레코드 스키마 (팀 공용):
    {
        "query": str,
        "answer": str,
        "retrieved": {"wiki_pages": [page_id, ...]},
        "cited_pages": [page_id, ...],
        "turns": int,
        "token_usage": {prompt_tokens, cache_read, cache_write, output_tokens},
        "turn_details": [{"turn": int, "tool_calls": [...], ...}, ...]
    }
    """
    client = _make_client()
    model = _get_model()

    toc_text, page_index = _build_toc()

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 Matter/connectedhomeip 기술문서 위키를 탐색해 질문에 답하는 에이전트입니다.\n"
                "먼저 list_pages로 목차를 확인하고, 필요한 페이지를 read_page로 읽은 뒤, "
                "충분한 정보를 얻으면 submit_answer로 답변을 제출하세요.\n"
                "답변은 한국어로 작성하고, 근거 페이지 ID를 cited_pages에 포함하세요."
            ),
        },
        {"role": "user", "content": query},
    ]

    retrieved_pages: list[str] = []
    cited_pages: list[str] = []
    answer: str = ""
    turn_details: list[dict] = []
    total_usage = {"prompt_tokens": 0, "cache_read": 0, "cache_write": 0, "output_tokens": 0}
    final_answer_found = False

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[턴 {turn}] API 호출 중...", file=sys.stderr)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        usage = _extract_token_usage(response.usage)
        total_usage = _sum_token_usage(total_usage, usage)

        tool_call_names: list[str] = []
        tool_results_for_detail: list[dict] = []

        # 도구 호출 처리
        if msg.tool_calls:
            messages.append(msg)  # assistant 메시지 (tool_calls 포함)

            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                tool_call_names.append(fn_name)

                if verbose:
                    print(f"  → {fn_name}({fn_args})", file=sys.stderr)

                if fn_name == "list_pages":
                    result_text = toc_text

                elif fn_name == "read_page":
                    pid = fn_args.get("page_id", "")
                    result_text = _read_page(pid, page_index)
                    if pid and pid in page_index:
                        if pid not in retrieved_pages:
                            retrieved_pages.append(pid)

                elif fn_name == "submit_answer":
                    answer = fn_args.get("answer", "")
                    cited_pages = fn_args.get("cited_pages", [])
                    result_text = "답변이 제출되었습니다."
                    final_answer_found = True

                else:
                    result_text = f"[오류] 알 수 없는 도구: {fn_name}"

                tool_results_for_detail.append({"name": fn_name, "result_len": len(result_text)})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result_text,
                    }
                )

        else:
            # 도구 없이 텍스트만 반환 → 루프 종료 (답변으로 사용)
            if msg.content:
                answer = msg.content
            tool_call_names = []
            final_answer_found = True

        turn_detail = {
            "turn": turn,
            "tool_calls": tool_call_names,
            **usage,
        }
        turn_details.append(turn_detail)

        if verbose:
            print(
                f"  usage: prompt={usage['prompt_tokens']} "
                f"cache_read={usage['cache_read']} "
                f"cache_write={usage['cache_write']} "
                f"output={usage['output_tokens']}",
                file=sys.stderr,
            )

        if final_answer_found:
            if verbose:
                print(f"[완료] {turn}턴에 답변 제출.", file=sys.stderr)
            break
    else:
        # max_turns 소진
        if verbose:
            print(f"[경고] 최대 턴({max_turns}) 소진. 마지막 텍스트 응답을 사용합니다.", file=sys.stderr)
        if not answer and msg.content:
            answer = msg.content

    return {
        "query": query,
        "answer": answer,
        "retrieved": {"wiki_pages": retrieved_pages},
        "cited_pages": cited_pages,
        "turns": len(turn_details),
        "token_usage": total_usage,
        "turn_details": turn_details,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LLM Wiki 에이전트 — 위키 탐색 기반 질의응답"
    )
    parser.add_argument("--query", required=True, help="질의 텍스트")
    parser.add_argument("--output", help="결과 JSON 저장 경로 (없으면 stdout)")
    parser.add_argument("--max-turns", type=int, default=30, help="최대 턴 수 (기본 30)")
    parser.add_argument("--verbose", action="store_true", help="도구 호출 로그 출력")
    args = parser.parse_args()

    result = run_agent(
        query=args.query,
        max_turns=args.max_turns,
        verbose=args.verbose,
    )

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"결과 저장: {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # 요약 출력 (stderr)
    print(
        f"\n[요약] turns={result['turns']} | "
        f"retrieved={len(result['retrieved']['wiki_pages'])}페이지 | "
        f"prompt_tokens={result['token_usage']['prompt_tokens']} | "
        f"output_tokens={result['token_usage']['output_tokens']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
