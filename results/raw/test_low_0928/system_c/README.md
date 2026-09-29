# System C — LLM Wiki · test_low_0928

`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나이며 총 280줄입니다.

질문 40문항 × 참가자 모델 7종 × 1회 실행.

## 실행 조건

- 위키: `systems/system_c_llm_wiki/wiki-astra` (34페이지, `compiled_by: openai/gpt-6-astra`)
- SSOT: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- 코퍼스: `0.1-c3` `corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e`
- 질문셋: `benchmark/questions_v1.jsonl` 40문항, SHA-256 `9be6a33eb122d892ee8f6f6fb0ddfd1b40f1bda8ebedbe36e6d199a3105389a2`
- 질의 방식: 에이전트 페이지 탐색 (`list_pages` / `read_page` / `submit_answer`, 최대 30턴)
- 추론 강도: light — OpenAI `reasoning.effort=low`, Anthropic `thinking.adaptive` + `output_config.effort=low`
- 출력 상한: 16000 토큰 / `temperature`는 보내지 않음
- 근거를 찾지 못한 경우 `제공된 문서에서 확인되지 않음.` 만 답하도록 지시

## 참가자 모델

| 모델 | 호출 경로 | 추론 강도 적용 | 비고 |
| --- | --- | --- | --- |
| `gpt-6-luna` | openai (Responses API) | 적용 | — |
| `gpt-6-sol` | openai (Responses API) | 적용 | — |
| `gpt-5.6-sol` | openai (Responses API) | 적용 | — |
| `claude-sonnet-5` | anthropic (Messages API) | 적용 | — |
| `claude-opus-5-5` | anthropic (Messages API) | 적용 | — |
| `deepseek-flash` | openai 호환 (chat/completions) | 미지원 | DeepSeek-V4.1-Flash (V4 Flash가 9/10 교체됨) |
| `kimi-k3` | openai 호환 (chat/completions) | 미지원 | 분당 요청 3회 제한 → 호출 간 21초 간격 강제 |

DeepSeek·Moonshot은 추론 강도 파라미터를 제공하지 않아 provider 기본값으로 실행되었습니다.

## 결과

| 모델 | ok | err | max_turns | 기권 | 평균 턴 | 지연 중앙값 |
| --- | --- | --- | --- | --- | --- | --- |
| `gpt-6-luna` | 40 | 0 | 0 | 4 | 3.1 | 5.3초 |
| `gpt-6-sol` | 40 | 0 | 0 | 4 | 3.0 | 6.5초 |
| `gpt-5.6-sol` | 40 | 0 | 0 | 3 | 3.1 | 7.9초 |
| `claude-sonnet-5` | 40 | 0 | 0 | 3 | 3.0 | 9.3초 |
| `claude-opus-5-5` | 40 | 0 | 0 | 4 | 3.0 | 13.5초 |
| `deepseek-flash` | 40 | 0 | 0 | 4 | 3.3 | 5.8초 |
| `kimi-k3` | 40 | 0 | 0 | 4 | 3.3 | 67.6초 |

## 토큰 (열별, 절대 합산하지 말 것)

| 모델 | uncached_input | output | cache_read | cache_creation |
| --- | --- | --- | --- | --- |
| `gpt-6-luna` | 346,060 | 7,891 | 52,705 | 미제공 |
| `gpt-6-sol` | 324,219 | 6,989 | 25,867 | 미제공 |
| `gpt-5.6-sol` | 366,492 | 11,949 | 13,417 | 미제공 |
| `claude-sonnet-5` | 590,408 | 33,165 | 0 | 0 |
| `claude-opus-5-5` | 602,791 | 34,623 | 0 | 0 |
| `deepseek-flash` | 440,147 | 52,432 | 231,168 | 미제공 |
| `kimi-k3` | 461,513 | 61,810 | 300,800 | 미제공 |

`cache_creation`을 보고하는 provider는 Anthropic뿐입니다. DeepSeek은 캐시 읽기만, Moonshot은 두 열 모두 제공하지 않아 `null`로 기록했습니다. 0은 '캐시를 쓰지 않음', `null`은 'provider가 값을 주지 않음'으로 서로 다른 의미입니다. Anthropic 프롬프트 캐싱(`cache_control`)은 A·B와 동일하게 적용하지 않았습니다.

## 기권 분포

| 문항 계열 | 기권 / 전체 |
| --- | --- |
| `Q-codedoc` | 0 / 70 |
| `Q-control` | 26 / 28 |
| `Q-multihop` | 0 / 70 |
| `Q-practical` | 0 / 49 |
| `Q-simple` | 0 / 63 |

기권 26건이 모두 대조군(`Q-control-*`) 문항에서 발생했고, 답변 가능한 문항에서는 한 건도 발생하지 않았습니다. 대조군 문항별 기권 모델 수: `Q-control-001` 5/7, `Q-control-002` 7/7, `Q-control-003` 7/7, `Q-control-004` 7/7.

## 증거 자료

- `runs/astra_run1/invocations.jsonl` — 턴별 도구 호출 기록 (호출한 도구, 인자, 응답 길이, 읽은 페이지의 SHA-256, 턴별 토큰)
- 각 레코드의 `retrieved.wiki_pages` — 에이전트가 열람한 페이지 목록
- 각 레코드의 `wiki_pages_evidence` — 열람 페이지의 경로 + SHA-256 + 몇 번째 턴 (280건 중 278건)
- `runs/astra_run1/models.json` — 참가자 모델 레지스트리 스냅샷 (A·B의 `participants.yaml` 대응)
- `runs/astra_run1/summary.json` — 실행 요약

A·B의 `index/chunks.jsonl`에 해당하는 공용 색인은 System C에 없습니다. 인용 검증은 위 두 필드로 하시면 됩니다.

## 알려두어야 할 사항

- `claude-sonnet-5`가 `Q-simple-001`, `Q-simple-002`를 2턴에 페이지 열람 없이 답했습니다. 페이지 ID(`clusters/0x0202-fan-control`)에 식별자가 포함되어 있어 목차만으로 답이 가능한 구조입니다. 식별자 계열 문항의 구조적 한계입니다.
- `gpt-6-sol`의 `Q-practical-004`는 3턴인데 1369초가 걸렸습니다. 호출 하나가 장시간 지연된 이상치로, 평균 지연(26.7초)을 왜곡합니다. 중앙값은 8.5초입니다.
- `deepseek-flash`의 `Q-simple-005/006/007`이 최초 실행에서 `APIConnectionError`로 실패해 재실행했습니다. 재실행분이 최종 결과에 반영되어 있으며 실패 기록은 `runs/astra_run1/failed_attempts.jsonl`에 있습니다.

코드 커밋: `987e4a0` · 실행: 2026-09-29
