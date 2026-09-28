# System B — 분해형 RAG · effort low 테스트 (2026-09-28)

`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.
객관 지표 보고서(정답 미사용): `systems/system_a_rag/reports/2026-09-28_test_low_7models.md`

- 줄 수: 280 (gpt-6-luna 40, deepseek-flash 40, kimi-k3 40, claude-sonnet-5 40, gpt-6-sol 40, claude-opus-5-5 40, gpt-5.6-sol 40), 실패 줄 0
- `system`은 `rag`, `query_mode`는 `decomposed`, `run`은 1
- 질문: `benchmark/questions_v1.jsonl` 40문항
- 코퍼스: 0.1-c3 `corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e`, 원본 commit `1ac132b5`
- 파이프라인 설정 해시: `7ea3fe637dd8174e`
- 인용 발췌: `../index/chunks.jsonl`의 청크 본문(`[chunk_id]`로 연결)

## 참가자 설정
- 7종 모두 추론 강도 effort low(라이트), 출력 상한 16000토큰
- temperature는 보내지 않았다(GPT·DeepSeek·Kimi는 추론 모드에서 거부·무시·고정, Claude는 원래 보내지 않음)
- deepseek-flash는 DeepSeek-V4.1-Flash다(V4 Flash가 9/10에 교체됨)
- kimi-k3는 계정의 분당 요청 3회 제한 때문에 System B에서 문항 사이를 50초 벌려 실행했다(지연 기록에는 넣지 않음)
- 질문 분해는 참가자 모델이 각자 했다(분해 토큰은 그 모델 토큰에 합산)
- 실행 조건 전체는 각 실행 폴더의 `participants.yaml` 사본에 있다

## 실행 폴더 (`runs/`)
| 폴더 | 모델 | 시작 | 코드 커밋 | 커밋 안 된 변경 | 다시 돌린 실패 시도 |
|---|---|---|---|---|---|
| `20260928_143517_7ea3fe637dd8174e_batch_decomposed` | gpt-6-luna | 14:35~ (1회 실행) | 5a2964e | 없음 | 0 |
| `20260928_183805_7ea3fe637dd8174e_batch_decomposed` | deepseek-flash, kimi-k3, claude-sonnet-5, gpt-6-sol, claude-opus-5-5, gpt-5.6-sol | 18:38~ (4회 실행) | defa7ab, fefff7c | 없음 | 4 |

- 커밋이 두 개인 폴더: `fefff7c`와 `defa7ab`의 차이는 Kimi 문항 간격 설정과 오류 문구 가림뿐이고, 프롬프트·검색·생성 코드는 같다
- `summary.json`: 모델별 토큰 4열(캐시 없는 입력·캐시 쓰기·캐시 읽기·출력)과 청구 기준 토큰(`billed_tokens`, 다시 돌린 실패 시도 포함)
- `invocations.jsonl`: 실행할 때마다 한 줄(시각, 코드 커밋)
- `failed_attempts.jsonl`: 이어하기로 다시 돌린 실패 시도. 채점 대상은 아니지만 비용 집계에는 넣는다
- 오류 문구 속 API 키 조각과 계정 식별자는 가렸다

## 채점할 때 참고
- `error`가 `dangling_citations`로 시작하는 줄은 답변이 있는 정상 줄이다(검색 결과에 없는 chunk_id를 인용). 1줄: gpt-6-luna Q-codedoc-001
- 기권 문구는 "제공된 문서에서 확인되지 않음"이다. 일부만 답하고 나머지에 이 문구를 쓴 부분 답변도 있다
