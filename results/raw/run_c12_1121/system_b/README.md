# System B — 분해형 RAG · run_c12_1121

`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.

- 줄 수: 280 (gpt-6-luna 40, deepseek-flash 40, kimi-k3 40, claude-sonnet-5 40, gpt-6-sol 40, gpt-5.6-sol 40, claude-opus-5-5 40), 실패 줄 0
- `system`은 `rag`, `query_mode`는 `decomposed`, `run`은 1
- 코퍼스만 C12로 바꾸고 나머지 조건은 1차 실행(`results/raw/test_low_0928/system_b`)과 같다. 파이프라인 설정 해시도 같은 `7ea3fe637dd8174e`다

## 실행 조건
- SSOT: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- 코퍼스: `0.1-c12` `corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad`
- 입력: System A와 같은 색인(`../index/chunks.jsonl`, 청크 2,137개)을 쓴다
  - 색인의 원천은 C12 `corpus/tiers/c12/processed/documents.jsonl`의 `text`(범위에 맞춘 발췌, 369개 문서)
  - sha256 `8e20ab2dea3cf1905ad2fe97faedfd0d7ba965d1cb9bb7ac0e908940c845ea71`. System C c12 위키 입력과 같은 파일이다
  - 원본 파일(`corpus/raw`)은 읽지 않는다
- 검색: 하위 질문마다 System A와 같은 검색(BM25 50 + 벡터 50 → RRF → 재순위)을 돌려 근거를 병합한다
  - 임베딩 `BAAI/bge-m3`(revision `5617a9f61b028005a4858fdac845db406aefb181`)
  - 재순위 `BAAI/bge-reranker-v2-m3`(revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`)
  - 실행 중에는 `HF_HUB_OFFLINE=1`로 위 revision에 고정했다
- 질문: `benchmark/questions_v1.jsonl` 40문항, sha256 `9be6a33eb122d892ee8f6f6fb0ddfd1b40f1bda8ebedbe36e6d199a3105389a2`
- 코드 커밋: `11165b8`
  - 1차 실행 커밋(`defa7ab`)과 비교해 분해·검색·생성 코드와 프롬프트는 같다
  - 바뀐 것은 `ssot.yaml`의 코퍼스 라벨, 비용 환산용 캐시 요율 설정, 주석뿐이다
- SDK: python 3.10.13, openai 3.16.2, anthropic 1.7.0, httpx 0.28.1
- 실행(한국 시간), 두 번에 나눠 실행했다
  - 1회차: 2026-11-21 02:33:07 ~ 04:42:08. 7종 실행
  - 2회차: 2026-11-22 16:45:06 ~ 17:21:12. Claude 2종의 실패 53문항만 이어서 실행
  - 두 번 모두 같은 코드 커밋, 같은 색인, 같은 설정이다. 두 실행 사이에 색인 파일(청크·임베딩)의 sha256이 바뀌지 않았음을 확인했다

## 두 번에 나눠 실행한 이유
- 11/21 04:12:18에 Anthropic 계정 크레딧이 소진되었다. 그 뒤의 Claude 호출이 모두 `400 Your credit balance is too low`로 실패했다
  - claude-sonnet-5 13문항(Q-codedoc-009부터), claude-opus-5-5 40문항 전부
  - 나머지 5종은 1회차에서 실패 없이 끝났다
- 크레딧을 충전한 뒤 같은 결과 폴더에서 이어하기(`--resume`)로 실패한 53문항만 다시 돌렸다
- 그래서 claude-sonnet-5는 27문항이 11/21, 13문항이 11/22에 생성되었고, claude-opus-5-5는 40문항 모두 11/22에 생성되었다
- 실패 시도 53건은 `failed_attempts.jsonl`에 남겼다. 채점 대상은 아니다
  - 이 중 과금된 것은 claude-sonnet-5 Q-codedoc-009 1건이다(분해 호출까지 진행된 뒤 실패, 492토큰). 이 토큰은 `summary.json`의 `billed_tokens`에 들어 있다

## 참가자 설정
- 7종 모두 추론 강도 effort low(라이트). 분해 호출과 생성 호출에 같은 값을 보냈다
  - OpenAI 3종, DeepSeek, Kimi: Chat Completions `reasoning_effort: "low"`
  - Claude 2종: `output_config.effort: "low"`. thinking 필드는 보내지 않았다(두 모델 모두 adaptive thinking이 기본)
- 출력 상한 16000토큰
  - DeepSeek은 `max_tokens`(`max_completion_tokens`는 오류 없이 무시됨)
  - OpenAI 3종과 Kimi는 `max_completion_tokens`, Claude는 `max_tokens`
- temperature는 보내지 않았다
- 캐시 토큰은 4열(캐시 없는 입력·캐시 쓰기·캐시 읽기·출력)로 나눠 담았다. 제공자별 매핑은 1차 실행 README와 같다
- deepseek-flash는 DeepSeek-V4.1-Flash다(V4 Flash가 9/10에 교체됨)
- kimi-k3는 계정의 분당 요청 3회 제한 때문에 문항 시작 사이를 50초 벌려 실행했다(지연 기록에는 넣지 않음)
- 질문 분해는 참가자 모델이 각자 했다(분해 토큰은 그 모델 토큰에 합산). 분해에 실패해 원래 질문으로 대체한 문항은 없다
- 실행 조건 전체는 실행 폴더의 `participants.yaml` 사본에 있다

## 실행 폴더 (`runs/`)
| 폴더 | 모델 | 시작 | 코드 커밋 | 커밋 안 된 변경 | 다시 돌린 실패 시도 |
|---|---|---|---|---|---|
| `20261121_023307_7ea3fe637dd8174e_batch_decomposed` | 7종 전부 | 11/21 02:33~ (2회 실행) | 11165b8 | 없음 | 53 |

- `summary.json`: 모델별 토큰 4열과 청구 기준 토큰(`billed_tokens`, 다시 돌린 실패 시도 포함)
- `invocations.jsonl`: 실행할 때마다 한 줄(시각, 코드 커밋, 참가자)
- `failed_attempts.jsonl`: 이어하기로 다시 돌린 실패 시도. 채점 대상은 아니지만 비용 집계에는 넣는다
- 오류 문구 속 API 키 조각과 계정 식별자를 가리는 처리를 거쳤다(이번 실행에는 해당 문자열 없음)

## 채점할 때 참고
- `dangling_citations` 줄(검색 결과에 없는 chunk_id 인용)은 없다
- 기권 문구는 "제공된 문서에서 확인되지 않음"이다. 일부만 답하고 나머지에 이 문구를 쓴 부분 답변도 있다
