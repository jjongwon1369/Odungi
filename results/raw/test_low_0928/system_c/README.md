> **사용하지 않는 결과 (2026-10-06 표시).** 이 280줄은 이슈 #23 수정 전, 원본 전체로 만든 옛 위키(`wiki-astra`)와 옛 프롬프트로 만든 답변입니다.
> 본실험 C 결과는 [`results/raw/run_c3_0930/system_c`](../../run_c3_0930/system_c/) 입니다. 비교·채점·인용에 쓰지 않습니다.

# System C — LLM Wiki · test_low_0928

`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.

## 실행 조건
- 위키: `systems/system_c_llm_wiki/wiki-astra` (compiled_by: openai/gpt-6-astra)
- SSOT: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- 코퍼스: `0.1-c3` `corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e`
- 질문셋 SHA-256: `9be6a33eb122d892ee8f6f6fb0ddfd1b40f1bda8ebedbe36e6d199a3105389a2`
- 코드 커밋: `987e4a0 (GPT 3종·Claude 2종, 9/28) + 4b3f9aa (DeepSeek·Kimi, 9/29 재실행)`
- 추론 강도: light (effort=low)
- 출력 상한: max_tokens=16000
- temperature: 보내지 않음

## 참가자 모델

| 모델 | provider | reasoning_applied | 비고 |
| --- | --- | --- | --- |
| kimi-k3 | openai_compatible | True | RPM 3/min → min_interval_s=21 |
| deepseek-flash | openai_compatible | True | DeepSeek-V4.1-Flash (V4 Flash, 9/10 교체) |
| gpt-6-luna | openai | True |  |
| gpt-6-sol | openai | True |  |
| gpt-5.6-sol | openai | True |  |
| claude-sonnet-5 | anthropic | True |  |
| claude-opus-5-5 | anthropic | True |  |

## 결과

| 모델 | ok | err | abstained | 코드 커밋 |
| --- | --- | --- | --- | --- |
| kimi-k3 | 40 | 0 | 4 | 4b3f9aa |
| deepseek-flash | 40 | 0 | 4 | 4b3f9aa |
| gpt-6-luna | 40 | 0 | 4 | 987e4a0 |
| gpt-6-sol | 40 | 0 | 4 | 987e4a0 |
| gpt-5.6-sol | 40 | 0 | 3 | 987e4a0 |
| claude-sonnet-5 | 40 | 0 | 3 | 987e4a0 |
| claude-opus-5-5 | 40 | 0 | 4 | 987e4a0 |

## 실행 이력
- 2026-09-28: 7종 전체 실행 (코드 `987e4a0`)
- 2026-09-29: DeepSeek·Kimi만 effort low로 재실행하고 두 모델 행을 교체 (코드 `4b3f9aa`, 이슈 #23 1-1). 9/28 실행에서는 두 모델의 `reasoning_config`가 비어 low가 전송되지 않았다(DeepSeek 기본값 high, Kimi 기본값 max). 나머지 5종 행은 9/28 그대로다.

## 알려진 한계
- GPT 3종 행은 캐시 쓰기 토큰을 읽지 못한 옛 코드(`987e4a0`)로 기록되어 `tokens.cache_creation`이 null이다(이슈 #23 1-2·1-3). 원본 usage가 저장되지 않아 재계산할 수 없으므로 재실행이 필요하다.
- 기권 판정은 `4b3f9aa`부터 A·B와 같은 방식(마침표 없는 문구 포함 여부)이다. 9/28 행에 새 기준을 적용해도 기권 수는 바뀌지 않음을 확인했다.
- Kimi 지연(`latency_ms.total`)은 `4b3f9aa`부터 호출 간격 대기(21초)를 뺀 값이다.
