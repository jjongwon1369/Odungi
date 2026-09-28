"""
System B — 질의 분해.

질문 1개 → 하위 질의 2~5개. LLM으로 실제 분해하되, API 키가 없을 때는
FakeDecomposer로 배관만 확인한다(원 질문을 그대로 하위질의 1개로 취급 —
이 경우 System B는 System A와 동일하게 동작하므로 회귀 확인용으로도 쓴다).

실행:
    python decompose.py "질문"              # LLMDecomposer 필요(client 인자로 주입)
"""

from __future__ import annotations

import json
import re
from typing import Protocol


class Decomposer(Protocol):
    def decompose(self, question: str, max_subq: int) -> tuple[list[str], object | None]:
        """(하위질의 목록, 분해 호출의 TokenUsage 또는 None)"""
        ...


class FakeDecomposer:
    """API 키 없을 때 배관 확인용. 원 질문을 그대로 하위질의 1개로 돌려준다."""

    def decompose(self, question: str, max_subq: int) -> tuple[list[str], object | None]:
        return [question], None


_SYSTEM_PROMPT = (
    "질문을 답하는 데 필요한, 서로 다른 정보를 찾는 하위 질의로 분해하라. "
    "각 하위 질의는 그 자체로 검색 가능한 완결된 문장이어야 한다. "
    "분해가 불필요하면(단순 조회) 원문 그대로 1개만 반환하라. "
    "다른 설명 없이 JSON 문자열 배열만 반환하라. 예: [\"하위질의1\", \"하위질의2\"]"
)


class LLMDecomposer:
    """실제 LLM으로 질문을 max_subq개 이하 하위질의로 분해한다."""

    def __init__(self, client):
        self.client = client
        # 직전 분해가 파싱에 실패해 원 질문으로 떨어졌는지, 그리고 응답 원문. 배치가 calls.jsonl에 남긴다
        self.last_fallback: bool = False
        self.last_raw_text: str | None = None

    def decompose(self, question: str, max_subq: int) -> tuple[list[str], object | None]:
        prompt = f"최대 하위질의 수: {max_subq}\n\n질문: {question}"
        self.last_raw_text = None
        # 분해 호출도 참가자 LLM 비용이다. usage를 버리면 System B 비용이 과소 계상된다.
        text, usage = self.client.complete(_SYSTEM_PROMPT, prompt)
        self.last_raw_text = text
        subqs = parse_subqueries(text)
        if subqs:
            self.last_fallback = False
            return subqs[:max_subq], usage
        # 파싱 실패 시 원 질문 그대로 — 검색 자체가 죽으면 안 된다.
        self.last_fallback = True
        return [question], usage


_SUBQ_KEYS = ("subqueries", "sub_queries", "queries", "sub_questions", "questions")


def _as_subqueries(value) -> list[str]:
    """JSON 값 하나가 하위질의 목록이면 정리해서 돌려준다. 아니면 빈 리스트."""
    if isinstance(value, dict):
        # {"subqueries": [...]}처럼 정해진 키 아래의 목록만 받는다(다른 키의 목록은 하위질의가 아니다)
        value = next((value[k] for k in _SUBQ_KEYS if k in value), None)
    if isinstance(value, list) and value and all(isinstance(s, str) and s.strip() for s in value):
        return list(dict.fromkeys(s.strip() for s in value))
    return []


def parse_subqueries(text: str) -> list[str]:
    """
    모델 출력에서 하위질의 배열을 꺼낸다. 못 꺼내면 빈 리스트.

    "JSON 배열만"을 지시해도 ```json 코드 펜스로 감싸거나 앞뒤에 설명을 붙이는 모델이 있다.
    json.loads만 하면 조용히 원 질문으로 떨어져 B가 A와 같아진다.
    설명 속에도 배열이 나올 수 있으므로 본문 끝에서 끝나는 배열을 우선하고, 없으면 마지막 배열을 쓴다.
    """
    body = re.sub(r"^\s*```[a-zA-Z]*\s*|\s*```\s*$", "", text.strip())
    try:
        got = _as_subqueries(json.loads(body))
        if got:
            return got
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    found: list[list[str]] = []
    i = 0
    while i < len(body):
        if body[i] not in "[{":
            i += 1
            continue
        try:
            value, end = decoder.raw_decode(body, i)
        except json.JSONDecodeError:
            i += 1
            continue
        got = _as_subqueries(value)
        if got:
            if not body[end:].strip():
                return got
            found.append(got)
        # 읽어 낸 JSON 값의 안쪽(다른 키의 목록 등)은 하위질의로 보지 않는다
        i = end
    return found[-1] if found else []


def make_decomposer(fake: bool, client=None) -> Decomposer:
    return FakeDecomposer() if fake or client is None else LLMDecomposer(client)
