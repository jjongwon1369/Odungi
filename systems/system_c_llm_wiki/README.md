# System C — LLM 위키

공통 코퍼스를 **사전 컴파일된 구조화 Markdown 위키**로 변환해두고, 질의 시 LLM 에이전트가
그 위키를 **페이지 단위로 탐색**해 답변한다. 벡터 임베딩과 청킹을 쓰지 않는 것이
System A / B(RAG 계열)와의 핵심 대조점이다.

## 두 단계

### 1. 오프라인 — 위키 컴파일 (`compiler/`)
코퍼스를 엔티티(클러스터 / 디바이스 타입 / 공유 베이스) 단위로 묶어 엔티티당 1페이지로
컴파일한다. 282개 문서 → 34개 페이지. 모든 페이지가 `source_paths`, SSOT `commit_hash`,
`corpus_source` 를 프론트매터로 기록한다. 코퍼스가 갱신될 때만 다시 수행한다.

**입력은 `corpus/tiers/c3/processed/documents.jsonl` 이다.** `corpus/HANDOFF.md` 가 정한
"RAG와 LLM Wiki가 함께 사용하는 282개 정규화 문서"이며, 원본 전문(`corpus/raw/`)을
읽으면 System A / B 와 입력 범위가 달라진다. 구축에 쓴 토큰은 위키 루트의
`build_tokens.json` 에 4열로 기록된다(질의 단계 토큰과 합산하지 않는다).

### 2. 온라인 — 에이전트 페이지 탐색
질의가 들어오면 LLM 에이전트가 3개 도구로 위키를 탐색한다 (수행계획서 8절).

| 도구 | 역할 |
| --- | --- |
| `list_pages` | 위키의 페이지 목록(목차)을 반환 |
| `read_page` | 지정한 페이지 1개의 전문을 반환 |
| `submit_answer` | 근거 페이지와 함께 최종 답변을 제출하고 루프 종료 |

에이전트는 목차를 보고 필요한 페이지만 골라 읽는다. 루프는 최대 30턴으로 제한한다.
열람한 페이지는 팀 공용 답변 레코드의 `retrieved.wiki_pages` 에 기록되어, System A / B 의
검색 결과와 같은 방식으로 근거 추적이 가능하다.

**위키 전체를 한 번에 주입하지 않는다.** 가구 4종 기준 위키 전체가 이미 12만 토큰을
넘어 128K 컨텍스트 모델에 들어가지 않고, 계획된 Device Type 12종 확장 시 약 40만
토큰에 이르러 질의마다 전량을 주입하는 방식은 성립하지 않는다. 에이전트 탐색은 목차와
필요한 페이지 2\~3개(약 1만 토큰)만 읽는다.

## System A / B 와 맞춘 조건

세 시스템 비교가 성립하려면 입력과 생성 조건이 같아야 한다. 다음은 의도적으로 맞춘 것이다.

| 항목 | 맞춘 내용 |
| --- | --- |
| 입력 범위 | `corpus/tiers/c3/processed/documents.jsonl` (A·B와 동일) |
| 생성 규칙 | 제공 자료 밖 지식 금지 / 식별자 원문 표기 / 근거 표시 / 간결성 |
| 기권 문구 | `제공된 문서에서 확인되지 않음` (마침표 없음, A의 `ABSTAIN_PHRASE` 와 동일) |
| 기권 판정 | 완전일치가 아니라 포함 여부 |
| 식별자 추출 | A의 `pipeline.yaml` identifiers 패턴·stopwords와 동일 |
| 추론 강도 | low 고정. provider별 파라미터명이 달라 `models.json` 에 명시 |
| 출력 상한 | 16000 토큰, `temperature` 미전송 |

파라미터가 거부되어도 자동으로 빼고 재시도하지 않는다. 조건이 조용히 바뀐 채
정상 종료되면 통제 실패가 드러나지 않기 때문이다. 실행 조건은 `config_hash` 에
시스템 프롬프트 SHA-256과 모델 레지스트리까지 포함해 해싱한다.

## 구성

```
systems/system_c_llm_wiki/
├── compiler/      위키 컴파일러 (오프라인 1단계)
├── linker/        페이지 간 상호링크 생성
├── agent/         에이전트 루프와 배치 러너 (온라인 2단계)
│   ├── run_agent.py    3개 도구 루프, provider별 호출 경로
│   ├── run_batch.py    다중 모델 배치 실행, 재개, 증거 기록
│   ├── models.json     참가자 모델 레지스트리
│   └── probe_api.py    도구 호출·추론 파라미터·토큰 열 지원 확인
├── wiki*/         컴파일된 위키 산출물 (컴파일 모델별)
└── validation/    위키 검증(validate_wiki.py) · 위키 간 비교 · 답변 레코드 검증(validate_records.py)
```

각 폴더의 README 에 세부 설계와 사용법이 있다.

## 현재 상태

- [x] 문서트리 설계 — 엔티티 단위 페이지 구조
- [x] 컴파일러 (`compiler/compile_wiki.py`)
- [x] 검증 (`validation/validate_wiki.py`, `validation/validate_records.py`)
- [ ] 전체 34페이지 컴파일 — API 크레딧 확보 후
- [ ] 상호링크 생성
- [ ] 에이전트 루프 (`list_pages` / `read_page` / `submit_answer`)

생성 모델은 System A / B 와 동일한 모델을 사용해야 한다(팀 합의 대기).
