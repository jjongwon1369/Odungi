# System A — RAG · run_c12_1121

`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.

- 줄 수: 280 (gpt-6-luna 40, deepseek-flash 40, kimi-k3 40, claude-sonnet-5 40, gpt-6-sol 40, claude-opus-5-5 40, gpt-5.6-sol 40), 실패 줄 0
- `system`은 `rag`, `query_mode`는 `simple`, `run`은 1
- 코퍼스만 C12로 바꾸고 나머지 조건은 1차 실행(`results/raw/test_low_0928/system_a`)과 같다. 파이프라인 설정 해시도 같은 `7ea3fe637dd8174e`다

## 실행 조건
- SSOT: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- 코퍼스: `0.1-c12` `corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad`
- 입력: C12 `corpus/tiers/c12/processed/documents.jsonl`의 `text`(범위에 맞춘 발췌, 369개 문서)
  - sha256 `8e20ab2dea3cf1905ad2fe97faedfd0d7ba965d1cb9bb7ac0e908940c845ea71`. System C c12 위키 입력과 같은 파일이다
  - 이름 매핑용 `corpus/tiers/c12/metadata/scope.json` sha256 `18c9cd209b28c815aefb2777ed9622d8373ae88800ae112ce18e23f0c29fdfd4`
  - 원본 파일(`corpus/raw`)은 읽지 않는다. 청킹 전에 XML 주석(CSA 고지 포함)과 코드 라이선스 헤더를 지운다
- 색인: 청크 2,137개, 512토큰·중첩 50. 청크 본문은 `../index/chunks.jsonl`(답변의 `[chunk_id]`로 연결)
- 검색: BM25 50 + 벡터 50 → RRF → 재순위 top-5
  - 임베딩 `BAAI/bge-m3`(revision `5617a9f61b028005a4858fdac845db406aefb181`)
  - 재순위 `BAAI/bge-reranker-v2-m3`(revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`)
  - 실행 중에는 `HF_HUB_OFFLINE=1`로 위 revision에 고정했다
- 질문: `benchmark/questions_v1.jsonl` 40문항, sha256 `9be6a33eb122d892ee8f6f6fb0ddfd1b40f1bda8ebedbe36e6d199a3105389a2`
- 코드 커밋: `11165b8`
  - 1차 실행 커밋(`defa7ab`)과 비교해 프롬프트·검색·생성 코드는 같다
  - 바뀐 것은 `ssot.yaml`의 코퍼스 라벨, 비용 환산용 캐시 요율 설정, 주석뿐이다
- SDK: python 3.10.13, openai 3.16.2, anthropic 1.7.0, httpx 0.28.1
- 실행: 2026-11-21 01:38:54 ~ 02:32:45 (한국 시간), 1회 실행으로 280줄 완료

## 참가자 설정
- 7종 모두 추론 강도 effort low(라이트)
  - OpenAI 3종, DeepSeek, Kimi: Chat Completions `reasoning_effort: "low"`
  - Claude 2종: `output_config.effort: "low"`. thinking 필드는 보내지 않았다(두 모델 모두 adaptive thinking이 기본)
- 출력 상한 16000토큰
  - DeepSeek은 `max_tokens`(`max_completion_tokens`는 오류 없이 무시됨)
  - OpenAI 3종과 Kimi는 `max_completion_tokens`, Claude는 `max_tokens`
- temperature는 보내지 않았다
- 캐시 토큰은 4열(캐시 없는 입력·캐시 쓰기·캐시 읽기·출력)로 나눠 담았다. 제공자별 매핑은 1차 실행 README와 같다
- deepseek-flash는 DeepSeek-V4.1-Flash다(V4 Flash가 9/10에 교체됨)
- kimi-k3는 계정의 분당 요청 3회 제한 때문에 문항 시작 사이를 50초 벌려 실행했다(지연 기록에는 넣지 않음)
- 실행 조건 전체는 실행 폴더의 `participants.yaml` 사본에 있다

## 실행 폴더 (`runs/`)
| 폴더 | 모델 | 시작 | 코드 커밋 | 커밋 안 된 변경 | 다시 돌린 실패 시도 |
|---|---|---|---|---|---|
| `20261121_013855_7ea3fe637dd8174e_batch` | 7종 전부 | 11/21 01:38~ (1회 실행) | 11165b8 | 없음 | 0 |

- `summary.json`: 모델별 토큰 4열과 청구 기준 토큰(`billed_tokens`, 다시 돌린 실패 시도 포함)
- `invocations.jsonl`: 실행할 때마다 한 줄(시각, 코드 커밋)
- 오류 문구 속 API 키 조각과 계정 식별자를 가리는 처리를 거쳤다(이번 실행에는 해당 문자열 없음)

## 채점할 때 참고
- `error`가 `dangling_citations`로 시작하는 줄은 답변이 있는 정상 줄이다(검색 결과에 없는 chunk_id를 인용). 1줄: claude-sonnet-5 Q-multihop-010
- 기권 문구는 "제공된 문서에서 확인되지 않음"이다. 일부만 답하고 나머지에 이 문구를 쓴 부분 답변도 있다
