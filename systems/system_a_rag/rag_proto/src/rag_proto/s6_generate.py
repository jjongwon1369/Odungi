"""
rag_proto.s6_generate — S6. 근거 기반 생성

top-k 청크 → LLM → 답변 + 인용

명세서 §04 S6. 프롬프트가 강제하는 것:
  - 제공된 컨텍스트 밖의 내용을 쓰지 말 것
  - 근거가 없으면 "제공된 문서에서 확인되지 않음"이라고 답할 것
  - 식별자는 원문 표기 그대로 복사할 것
  - 각 주장 끝에 근거 [chunk_id]를 표기할 것

토큰은 반드시 4열로 기록한다. OpenAI usage 필드 매핑:
  prompt_tokens - cached_tokens → uncached_input
  (보고 없음)                    → cache_creation
  prompt_tokens_details.cached_tokens → cache_read
  completion_tokens             → output

실행:
    python -m rag_proto.s6_generate --selftest        # 가짜 LLM으로 배관만 확인
"""

from __future__ import annotations

import os
import sys
from typing import Protocol

from .config import Config, load
from .schema import TokenUsage

# 근거가 없을 때 내놓아야 하는 정확한 문구.
# run_eval이 대조군 문항의 기권 여부를 이 문자열로 판정하므로,
# 프롬프트와 판정 로직이 같은 상수를 보도록 한 곳에 둔다.
ABSTAIN_PHRASE = "제공된 문서에서 확인되지 않음"

SYSTEM_PROMPT = """You are a technical documentation assistant for the Matter \
smart home standard and the connectedhomeip SDK.

Answer ONLY from the provided context. Follow these rules without exception:

1. Never use knowledge outside the provided context. If the context does not \
contain the answer, reply exactly: "제공된 문서에서 확인되지 않음"
2. Copy identifiers verbatim. Cluster names, attribute names, command names and \
hex IDs (e.g. OnOff, TemperatureSetpoint, 0x0201) must appear exactly as written \
in the context. Never translate, reformat or guess them.
3. Cite every claim. Put the supporting [chunk_id] at the end of each sentence \
that makes a factual claim. Use only chunk_ids that appear in the context.
4. Be concise. Do not add caveats, summaries of your own process, or \
recommendations that are not in the context.

Answer in the same language as the question."""


def build_context(candidates) -> str:
    """검색된 청크를 [chunk_id] 본문 형식으로 조립한다."""
    blocks = []
    for c in candidates:
        blocks.append(f"[{c.chunk_id}] (source: {c.source_path})\n{c.text}")
    return "\n\n---\n\n".join(blocks)


def build_prompt(question: str, candidates) -> str:
    return (
        f"<context>\n{build_context(candidates)}\n</context>\n\n"
        f"<question>\n{question}\n</question>\n\n"
        "Answer using only the context above, citing [chunk_id] for each claim."
    )


class LLMClient(Protocol):
    name: str

    def complete(self, system: str, prompt: str) -> tuple[str, TokenUsage]: ...


class OpenAIClient:
    """
    공식 SDK 사용. 모델 구조나 추론은 전부 API가 담당한다.
    RAG와 LLM Wiki가 반드시 같은 모델을 써야 비교가 성립한다.

    토큰 4열 매핑 주의 — OpenAI와 Anthropic의 의미가 다르다.

      OpenAI  : prompt_tokens가 캐시된 토큰을 *포함*한다.
                따라서 uncached는 prompt_tokens - cached_tokens로 빼야 한다.
      Anthropic: input_tokens가 캐시된 토큰을 *제외*한다.

    이걸 모르고 prompt_tokens를 그대로 uncached에 넣으면 캐시 적중분이
    두 번 계산되어 비용이 부풀려진다. 베이스라인 논문이 판정을 포기한 것과
    같은 종류의 오류다.

    또한 OpenAI는 캐시 *쓰기* 토큰을 따로 보고하지 않으므로
    cache_creation은 항상 0으로 남는다. 최신 모델에서 캐시 쓰기에
    추가 요율이 붙으므로, 비용을 엄밀히 따질 때는 이 한계를 명시할 것.
    """

    def __init__(self, cfg: Config):
        from openai import OpenAI

        gen = cfg.pipeline["generation"]
        self.name = gen["model"]
        self.max_tokens = gen.get("max_tokens", 2048)
        self.temperature = gen.get("temperature", 0.0)
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def complete(self, system: str, prompt: str) -> tuple[str, TokenUsage]:
        resp = self.client.chat.completions.create(
            model=self.name,
            max_completion_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        text = resp.choices[0].message.content or ""

        u = resp.usage
        prompt_tokens = getattr(u, "prompt_tokens", 0) or 0
        details = getattr(u, "prompt_tokens_details", None)
        cached = getattr(details, "cached_tokens", 0) or 0 if details else 0

        usage = TokenUsage(
            uncached_input=max(prompt_tokens - cached, 0),
            cache_creation=0,  # OpenAI는 캐시 쓰기 토큰을 보고하지 않는다
            cache_read=cached,
            output=getattr(u, "completion_tokens", 0) or 0,
        )
        return text, usage


class FakeLLM:
    """
    배관 확인용. 첫 청크에서 문장 하나를 뽑아 인용을 붙인 답변을 만든다.
    답변 품질은 무의미하다. 절대 실험에 쓰지 말 것.
    """

    name = "fake-llm"

    def complete(self, system: str, prompt: str) -> tuple[str, TokenUsage]:
        import re

        ids = re.findall(r"\[([a-zA-Z0-9_\-]+)\] \(source:", prompt)
        if not ids:
            return "제공된 문서에서 확인되지 않음", TokenUsage()

        body = prompt.split(f"[{ids[0]}]", 1)[1]
        snippet = " ".join(body.split("\n")[1:3]).strip()[:160]
        answer = f"{snippet} [{ids[0]}]"
        return answer, TokenUsage(
            uncached_input=len(prompt) // 4, output=len(answer) // 4
        )


def make_client(cfg: Config, fake: bool = False) -> LLMClient:
    return FakeLLM() if fake else OpenAIClient(cfg)


def generate(
    question: str, candidates, client: LLMClient
) -> tuple[str, TokenUsage]:
    if not candidates:
        return "제공된 문서에서 확인되지 않음", TokenUsage()
    return client.complete(SYSTEM_PROMPT, build_prompt(question, candidates))


def _selftest() -> int:
    """검색 없이 S6만 확인한다. 모델도 색인도 필요 없다."""
    from dataclasses import dataclass

    @dataclass
    class Stub:
        chunk_id: str
        source_path: str
        text: str

    candidates = [
        Stub(
            "docs_guides_refrigerator__0002",
            "docs/guides/refrigerator.md",
            "The TemperatureSetpoint attribute holds the target temperature.",
        )
    ]
    answer, usage = generate("냉장고 온도 설정 속성은?", candidates, FakeLLM())

    print("--- 프롬프트 (앞부분) ---")
    print(build_prompt("냉장고 온도 설정 속성은?", candidates)[:220], "...\n")
    print("--- 답변 ---")
    print(answer, "\n")
    print("--- 토큰 4열 ---")
    print(usage.model_dump())
    print(f"청구 환산 입력: {usage.billable_equivalent()}")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return _selftest()
    print("S6은 단독 실행하지 않습니다. python -m rag_proto.ask \"질문\" 을 쓰세요.")
    print("배관 확인은 --selftest 플래그를 붙이세요.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
