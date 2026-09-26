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
from typing import Protocol


class Decomposer(Protocol):
    def decompose(self, question: str, max_subq: int) -> list[str]: ...


class FakeDecomposer:
    """API 키 없을 때 배관 확인용. 원 질문을 그대로 하위질의 1개로 돌려준다."""

    def decompose(self, question: str, max_subq: int) -> list[str]:
        return [question]


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

    def decompose(self, question: str, max_subq: int) -> list[str]:
        prompt = f"{_SYSTEM_PROMPT}\n\n최대 하위질의 수: {max_subq}\n\n질문: {question}"
        text, _usage = self.client.complete(_SYSTEM_PROMPT, prompt)
        try:
            subqs = json.loads(text)
            if isinstance(subqs, list) and subqs and all(isinstance(s, str) and s.strip() for s in subqs):
                return subqs[:max_subq]
        except (json.JSONDecodeError, TypeError):
            pass
        # 파싱 실패 시 원 질문 그대로 — 검색 자체가 죽으면 안 된다.
        return [question]


def make_decomposer(fake: bool, client=None) -> Decomposer:
    return FakeDecomposer() if fake or client is None else LLMDecomposer(client)
