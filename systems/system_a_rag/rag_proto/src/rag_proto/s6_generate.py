"""
rag_proto.s6_generate — S6. 근거 기반 생성

top-k 청크 → LLM → 답변 + 인용

명세서 §04 S6. 프롬프트가 강제하는 것:
  - 제공된 컨텍스트 밖의 내용을 쓰지 말 것
  - 근거가 없으면 "제공된 문서에서 확인되지 않음"이라고 답할 것
  - 식별자는 원문 표기 그대로 복사할 것
  - 각 주장 끝에 근거 [chunk_id]를 표기할 것

토큰은 반드시 4열로 기록한다. OpenAI usage 필드 매핑:
  prompt_tokens - cached - cache_write      → uncached_input
  prompt_tokens_details.cache_write_tokens  → cache_creation  (게이트웨이는 최상위 cache_creation_input_tokens)
  prompt_tokens_details.cached_tokens       → cache_read      (DeepSeek prompt_cache_hit_tokens, Kimi 최상위 cached_tokens)
  completion_tokens (추론 토큰 포함)         → output
호출마다 원본 usage를 raw_calls에 남긴다. 배치는 이것을 calls.jsonl로 기록해 매핑을 사후에 대조한다.

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
that makes a factual claim. Use only chunk_ids that appear in the context. \
Write each chunk_id in its own square brackets, e.g. [chunk_a][chunk_b]. Never \
put two chunk_ids, backticks or any other text inside one pair of brackets, and \
never use square brackets for anything else (such as hex IDs or code).
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


def require_api_key(env_name: str) -> str:
    """
    참가자 키는 지정한 환경변수에서만 읽는다. 비어 있으면 None을 SDK에 넘기지 않고 멈춘다 —
    openai SDK는 None이면 OPENAI_API_KEY로 대신 채우는데, 그러면 DeepSeek·Kimi처럼
    base_url이 다른 곳으로 OpenAI 키가 전송된다(Anthropic SDK도 ANTHROPIC_API_KEY로 채운다).
    """
    value = os.environ.get(env_name, "").strip()
    if not value:
        raise ValueError(f"{env_name}가 비어 있습니다 (.env 확인)")
    return value


class GenerationError(RuntimeError):
    """답변을 쓸 수 없는 응답(거절, 토큰 상한으로 본문이 비어 있음 등).
    run_eval이 잡아서 error 행으로 남긴다 — 빈 답변을 정상 답변처럼 채점하면 안 된다.
    이미 과금된 호출이므로 usage를 함께 실어 error 행의 토큰 비용에 반영한다."""

    def __init__(self, message: str, usage: TokenUsage | None = None):
        super().__init__(message)
        self.usage = usage or TokenUsage()


def _openai_cached_tokens(u) -> int:
    """
    OpenAI 호환 API마다 캐시 적중 토큰을 보고하는 위치가 다르다.
    OpenAI는 prompt_tokens_details.cached_tokens, DeepSeek는 prompt_cache_hit_tokens,
    Moonshot(Kimi)은 최상위 cached_tokens. 못 찾으면 0 — 이 경우 캐시 적중분이
    uncached_input으로 잡혀 비용이 과대 계상되니 smoke 단계에서 usage를 확인할 것.
    """
    details = getattr(u, "prompt_tokens_details", None)
    for value in (
        getattr(details, "cached_tokens", None) if details else None,
        getattr(u, "prompt_cache_hit_tokens", None),
        getattr(u, "cached_tokens", None),
    ):
        if value:
            return int(value)
    return 0


def _openai_cache_write_tokens(u) -> int:
    """
    캐시 쓰기 토큰. OpenAI는 GPT-5.6 이후 prompt_tokens_details.cache_write_tokens로
    보고하고 기본 입력 요율의 1.25배로 과금한다(OpenAI 프롬프트 캐시 문서). Azure
    게이트웨이는 최상위 cache_creation_input_tokens 확장 필드를 쓴다(System C
    run_agent.py도 이 필드를 읽는다). 못 찾으면 0 — 쓰기분이 uncached_input으로 잡힌다.
    """
    details = getattr(u, "prompt_tokens_details", None)
    for value in (
        getattr(details, "cache_write_tokens", None) if details else None,
        getattr(u, "cache_creation_input_tokens", None),
    ):
        if value:
            return int(value)
    return 0


class OpenAIClient:
    """
    OpenAI 및 OpenAI 호환 엔드포인트(DeepSeek, Kimi 등 base_url만 다른 곳)용.

    토큰 4열 매핑 주의 — OpenAI와 Anthropic의 의미가 다르다.

      OpenAI  : prompt_tokens가 캐시된 토큰을 *포함*한다.
                따라서 uncached는 prompt_tokens - cached_tokens로 빼야 한다.
      Anthropic: input_tokens가 캐시된 토큰을 *제외*한다.

    이걸 모르고 prompt_tokens를 그대로 uncached에 넣으면 캐시 적중분이
    두 번 계산되어 비용이 부풀려진다. 베이스라인 논문이 판정을 포기한 것과
    같은 종류의 오류다.

    캐시 *쓰기* 토큰은 _openai_cache_write_tokens가 읽어 cache_creation에 넣는다.
    OpenAI 문서상 prompt_tokens는 캐시 읽기·쓰기를 모두 포함하므로 둘 다 빼서
    uncached를 구한다 — 호환 엔드포인트도 같은지는 --smoke의 원본 usage 출력으로 확인할 것.
    """

    def __init__(
        self,
        model: str,
        max_tokens: int,
        temperature: float | None,
        base_url: str | None = None,
        api_key_env: str = "OPENAI_API_KEY",
        max_retries: int = 5,
        effort: str | None = None,
        max_tokens_param: str = "max_completion_tokens",
    ):
        from openai import OpenAI

        self.name = model
        self.max_tokens = max_tokens
        # 추론형 모델 일부는 기본값 외 temperature를 거부한다. None이면 아예 안 보낸다.
        self.temperature = temperature
        # 추론 강도(reasoning_effort). None이면 보내지 않아 모델 기본값을 쓴다
        # (GPT-6 Luna는 medium). 추론 토큰은 출력 토큰으로 과금된다.
        self.effort = effort
        # 출력 상한을 보내는 파라미터 이름. OpenAI 추론 모델은 max_completion_tokens만 받고,
        # DeepSeek은 max_tokens만 읽는다(max_completion_tokens는 오류 없이 무시돼 상한이 64K가 된다)
        self.max_tokens_param = max_tokens_param
        self.raw_calls: list[dict] = []
        self.client = OpenAI(
            api_key=require_api_key(api_key_env),
            base_url=base_url,
            max_retries=max_retries,
        )

    def complete(self, system: str, prompt: str) -> tuple[str, TokenUsage]:
        kwargs = {}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.effort:
            kwargs["reasoning_effort"] = self.effort
        kwargs[self.max_tokens_param] = self.max_tokens
        resp = self.client.chat.completions.create(
            model=self.name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            **kwargs,
        )
        choice = resp.choices[0]
        text = choice.message.content or ""

        u = resp.usage
        self.last_raw_usage = u
        prompt_tokens = getattr(u, "prompt_tokens", 0) or 0
        cached = _openai_cached_tokens(u)
        created = _openai_cache_write_tokens(u)
        residual = prompt_tokens - cached - created
        if residual < 0:
            # prompt_tokens가 캐시분을 제외하는 엔드포인트라는 뜻이다. 0으로 잘리는 입력이 생긴다
            print(f"\n경고: {self.name} prompt_tokens({prompt_tokens}) < 캐시 읽기({cached})+쓰기({created}). "
                  "이 엔드포인트의 usage 의미를 calls.jsonl로 확인할 것", file=sys.stderr)
        usage = TokenUsage(
            uncached_input=max(residual, 0),
            cache_creation=created,
            cache_read=cached,
            output=getattr(u, "completion_tokens", 0) or 0,
        )
        self.raw_calls.append({
            "finish_reason": choice.finish_reason,
            "refusal": getattr(choice.message, "refusal", None),
            "usage": u.model_dump() if hasattr(u, "model_dump") else None,
            "mapped": usage.model_dump(),
        })
        if not text.strip():
            raise GenerationError(f"빈 답변 (finish_reason={choice.finish_reason})", usage)
        if choice.finish_reason not in (None, "stop"):
            # length·content_filter·insufficient_system_resource·aborted: 중간에 끊긴 답이라 채점하면 안 된다.
            # 오류 행(과금분 보존)으로 남겨 --resume이 다시 돌게 한다. 앞부분은 오류 문구에 남긴다
            raise GenerationError(
                f"끝까지 생성되지 않음 (finish_reason={choice.finish_reason}) 앞부분: {text[:80]!r}", usage
            )
        return text, usage


class AnthropicClient:
    """
    Claude(Sonnet 5, Opus 5.5 등)용.

    - temperature/top_p/top_k를 보내면 400이다(Sonnet 5, Opus 5.5에서 샘플링
      파라미터 제거). OpenAI 쪽과 조건을 맞추려고 0.0을 보내면 전 문항이 실패한다.
    - thinking은 항상 켜져 있고(Opus 5.5는 끌 수 없음) thinking 토큰도 max_tokens에
      포함된다. max_tokens가 작으면 본문 없이 잘린다 → 참가자 설정에서 넉넉히 준다.
    - 응답 content에 thinking 블록이 섞여 오므로 text 블록만 모은다.
    - usage는 이미 4열과 같은 의미다: input_tokens는 캐시분을 *제외*한 값.
    """

    def __init__(
        self,
        model: str,
        max_tokens: int,
        effort: str | None = None,
        api_key_env: str = "ANTHROPIC_API_KEY",
        base_url: str | None = None,
        max_retries: int = 5,
    ):
        import anthropic

        self.name = model
        self.max_tokens = max_tokens
        self.effort = effort  # None이면 모델 기본값(Opus 5.5는 medium, Sonnet 5는 high)
        self.raw_calls: list[dict] = []
        self.client = anthropic.Anthropic(
            api_key=require_api_key(api_key_env), base_url=base_url, max_retries=max_retries
        )

    def complete(self, system: str, prompt: str) -> tuple[str, TokenUsage]:
        kwargs = {}
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        resp = self.client.messages.create(
            model=self.name,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        text = "".join(b.text for b in resp.content if b.type == "text")

        u = resp.usage
        self.last_raw_usage = u
        usage = TokenUsage(
            uncached_input=u.input_tokens or 0,
            cache_creation=u.cache_creation_input_tokens or 0,
            cache_read=u.cache_read_input_tokens or 0,
            output=u.output_tokens or 0,
        )
        self.raw_calls.append({
            "finish_reason": resp.stop_reason,
            "usage": u.model_dump() if hasattr(u, "model_dump") else None,
            "mapped": usage.model_dump(),
        })
        if resp.stop_reason == "refusal":
            category = getattr(resp.stop_details, "category", None) if resp.stop_details else None
            raise GenerationError(f"refusal (category={category})", usage)
        if not text.strip():
            raise GenerationError(f"빈 답변 (stop_reason={resp.stop_reason})", usage)
        if resp.stop_reason not in ("end_turn", "stop_sequence"):
            # max_tokens·model_context_window_exceeded 등: 끊긴 답이라 오류 행으로 남긴다(과금분 보존)
            raise GenerationError(
                f"끝까지 생성되지 않음 (stop_reason={resp.stop_reason}) 앞부분: {text[:80]!r}", usage
            )
        return text, usage


class FakeLLM:
    """
    배관 확인용. 첫 청크에서 문장 하나를 뽑아 인용을 붙인 답변을 만든다.
    답변 품질은 무의미하다. 절대 실험에 쓰지 말 것.
    """

    def __init__(self, name: str = "fake-llm"):
        self.name = name

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


OFFICIAL_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com",
}


PROVIDERS = ("openai", "openai_compatible", "anthropic")


def resolve_base_url(participant: dict) -> str:
    """
    참가자 엔드포인트를 명시적으로 정한다: base_url → base_url_env가 가리키는 환경변수
    → 제공자 공식 주소. 범용 OPENAI_BASE_URL/ANTHROPIC_BASE_URL은 일부러 읽지 않는다.
    SDK는 주소를 안 넘기면 그 변수를 조용히 읽는데, 거기엔 개발용 테스트 게이트웨이
    (이동수님 쪽 과금) 주소가 들어 있을 수 있어 본실험 호출이 그리로 샌다.
    그래서 None을 돌려주지 않는다 — 정할 수 없으면 예외.
    """
    if participant.get("base_url"):
        return participant["base_url"]
    env_name = participant.get("base_url_env")
    if env_name:
        value = os.environ.get(env_name)
        if not value:
            raise ValueError(f"{participant['model']}: base_url_env={env_name} 환경변수가 비어 있습니다")
        return value
    official = OFFICIAL_BASE_URLS.get(participant["provider"])
    if official is None:
        raise ValueError(f"{participant['model']}: {participant['provider']}은 base_url 또는 base_url_env가 필요합니다")
    return official


def resolve_api_key_env(participant: dict) -> str:
    """
    참가자 키가 든 환경변수 이름. openai_compatible은 반드시 명시해야 한다 —
    기본값 OPENAI_API_KEY로 두면 OpenAI 키가 제3자 주소(DeepSeek·Kimi 등)로 전송된다.
    """
    if participant.get("api_key_env"):
        return participant["api_key_env"]
    default = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}.get(participant["provider"])
    if default is None:
        raise ValueError(f"{participant['model']}: {participant['provider']}은 api_key_env를 명시해야 합니다")
    return default


def make_client(cfg: Config, fake: bool = False, participant: dict | None = None) -> LLMClient:
    """
    participant가 없으면 pipeline.yaml의 generation 설정으로 OpenAI 클라이언트를 만든다
    (단일 질의 ask.py 경로). participant가 있으면 configs/participants.yaml 항목대로
    제공자별 클라이언트를 만든다(본실험 배치 경로).
    """
    gen = cfg.pipeline["generation"]
    if participant is None:
        if fake:
            return FakeLLM()
        return OpenAIClient(gen["model"], gen.get("max_tokens", 2048), gen.get("temperature", 0.0))

    if fake:
        return FakeLLM(name=participant["model"])

    provider = participant["provider"]
    if provider not in PROVIDERS:
        raise ValueError(f"알 수 없는 provider: {provider!r} ({participant['model']})")
    max_tokens = participant.get("max_tokens", gen.get("max_tokens", 2048))
    base_url = resolve_base_url(participant)
    api_key_env = resolve_api_key_env(participant)
    if provider == "anthropic":
        return AnthropicClient(
            participant["model"],
            max_tokens,
            effort=participant.get("effort"),
            api_key_env=api_key_env,
            base_url=base_url,
        )
    return OpenAIClient(
        participant["model"],
        max_tokens,
        temperature=participant.get("temperature", gen.get("temperature", 0.0)),
        base_url=base_url,
        api_key_env=api_key_env,
        effort=participant.get("effort"),
        max_tokens_param=participant.get("max_tokens_param", "max_completion_tokens"),
    )


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
