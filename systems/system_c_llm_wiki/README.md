# System C — LLM 위키

공통 코퍼스를 **사전 컴파일된 구조화 Markdown 위키**로 변환해두고, 질의 시 LLM 에이전트가
그 위키를 **페이지 단위로 탐색**해 답변한다. 벡터 임베딩과 청킹을 쓰지 않는 것이
System A / B(RAG 계열)와의 핵심 대조점이다.

실행 조건과 본실행 순서(입력 sha256 확인 → 컴파일 → 링크 → 검사 → 스모크 → 본실행 → 레코드 검증)는
`CLAUDE.md` 의 "본실행 조건" · "본실행 절차" 를 따른다. 그 밖의 방법으로 돌린 결과는 A 와 비교하지 않는다.

## 두 단계

### 1. 오프라인 — 위키 컴파일 (`compiler/`)
코퍼스를 엔티티(클러스터 / 디바이스 타입 / 공유 베이스) 단위로 묶어 엔티티당 1페이지로
컴파일한다. 282개 문서 → 34개 페이지. 컴파일 모델은 `gpt-6-astra`(참가자 아님)다.
모든 페이지가 `source_paths`, SSOT `commit_hash`, `compiled_by`, `corpus_source`, `corpus_snapshot` 을
프론트매터로 기록하고, 위키 루트의 `wiki_manifest.json` 이 있어야 할 페이지 목록과 입력 파일 sha256 을
기록한다. 코퍼스가 갱신될 때만 다시 수행한다.

**입력은 `corpus/tiers/c3/processed/documents.jsonl` 이다.** `corpus/HANDOFF.md` 가 정한
"RAG와 LLM Wiki가 함께 사용하는 282개 정규화 문서"이며, 원본 전문(`corpus/raw/`)을
읽으면 System A / B 와 입력 범위가 달라진다. 파일 sha256 이 A 가 색인한 파일과 같아야 한다
(`71c40454…`). 구축에 쓴 토큰은 호출 1건이 위키 루트의 `build_calls.jsonl` 에 한 줄로 즉시
쌓이고(과금 원장), `build_tokens.json` 은 그 원장에서 `uncached_input`/`cache_creation`/`cache_read`/`output`
4열로 집계한다. 질의 단계 토큰과 합산하지 않는다.

컴파일 뒤 `linker/` 가 scope.json 관계로 페이지마다 `## 관련 페이지` 섹션을 넣고(LLM 호출 없음),
`validation/check_rebuilt_wiki.py` 가 PASS 여야 질의 단계로 넘어간다.

### 2. 온라인 — 에이전트 페이지 탐색
질의가 들어오면 LLM 에이전트가 3개 도구로 위키를 탐색한다 (수행계획서 8절).

| 도구 | 역할 |
| --- | --- |
| `list_pages` | 위키의 페이지 목록(목차)을 반환 |
| `read_page` | 지정한 페이지 1개의 전문을 반환 |
| `submit_answer` | 근거 페이지와 함께 최종 답변을 제출하고 루프 종료 |

에이전트는 목차를 보고 필요한 페이지만 골라 읽는다. 루프는 최대 30턴, 호출마다 출력 상한
16000 토큰이다. 읽은 페이지는 팀 공용 답변 레코드의 `retrieved.wiki_pages` 와 `citations` 에,
모델이 인용한 페이지는 `cited_pages` 에 기록되어, System A / B 의 검색 결과와 같은 방식으로
근거 추적이 가능하다.

**위키 전체를 한 번에 주입하지 않는다.** 가구 4종 기준 위키 전체가 이미 12만 토큰을
넘어 128K 컨텍스트 모델에 들어가지 않고, 계획된 Device Type 12종 확장 시 약 40만
토큰에 이르러 질의마다 전량을 주입하는 방식은 성립하지 않는다. 에이전트 탐색은 목차와
필요한 페이지 2\~3개(약 1만 토큰)만 읽는다.

## System A / B 와 맞춘 조건

세 시스템 비교가 성립하려면 입력과 생성 조건이 같아야 한다. 다음은 의도적으로 맞춘 것이다.
기준은 System A 의 `test_low_0928` 실행이다. (#27 A 기준 점검)

| 항목 | 맞춘 내용 |
| --- | --- |
| 입력 범위 | `corpus/tiers/c3/processed/documents.jsonl` (A·B와 바이트까지 동일, sha256 `71c40454…`) |
| 참가자 | 7종. `agent/models.json` = A 의 `configs/participants.yaml` (모델 ID · effort · 출력 상한 파라미터) |
| 질문 · 회차 | `benchmark/questions_v1.jsonl` 40문항, run 1 |
| 생성 규칙 | A `SYSTEM_PROMPT` 영어 원문. C 고유는 위키 도구 단락 · 규칙 3(인용 대상) · 규칙 5(제출 경로) |
| 첫 user 메시지 | A `build_prompt` 의 `<question>` 틀과 끝 문장. `<context>` 는 도구로 읽으므로 없고, 인용 대상만 페이지 ID |
| 기권 문구 | `제공된 문서에서 확인되지 않음` (마침표 없음, A의 `ABSTAIN_PHRASE` 와 동일) |
| 기권 판정 | 완전일치가 아니라 포함 여부 |
| 식별자 추출 | A의 `pipeline.yaml` identifiers 패턴·stopwords와 동일 |
| 추론 강도 | low 고정. provider별 파라미터명이 달라 `models.json` 에 명시 |
| 출력 상한 | 호출마다 16000 토큰, `temperature` 미전송 |
| 클라이언트 | 재시도 5회, 타임아웃 SDK 기본값(연결 5초 · 응답 600초), 앱 수준 429 재시도 없음 |
| 오류 행 | 빈 답변 · 최대 턴 · 호출 실패는 `status: error`, `answer: ""` 로 두고 다시 돌린다 (A 의 GenerationError · 크래시 행) |
| 지연 | `latency_ms.generate` = LLM 호출 시간 합, 호출 간격 대기 제외 (A 의 generate 와 같은 뜻) |

파라미터가 거부되어도 자동으로 빼고 재시도하지 않는다. 조건이 조용히 바뀐 채
정상 종료되면 통제 실패가 드러나지 않기 때문이다. 실행 조건은 `config_hash` 에
시스템 프롬프트 SHA-256, 도구 정의, 첫 user 메시지 틀, 클라이언트 설정, 위키 페이지 본문,
위키 입력 sha256, 모델 레지스트리까지 포함해 해싱한다.

## System A 와 다른 점 (설계상 차이)

고치지 않고 결과 README 와 논문 방법 절에 적는 차이다. 1~6 은 `run_batch.py` 가 결과 폴더
`README.md` 에 자동으로 적는다.

1. 문맥을 검색 top-5 로 한 번에 받지 않고 도구(`list_pages` · `read_page`)로 읽고 `submit_answer` 로 제출한다. 최대 30턴, 턴마다 출력 상한 16000.
2. GPT 3종은 Responses API 로 부른다(A 는 Chat Completions). 도구와 effort 를 함께 쓰려면 Responses 가 필요하다.
3. 목차에 페이지 ID 가 보이고, 클러스터 페이지 ID 에는 hex ID 가 들어 있다.
4. 위키는 gpt-6-astra 가 C3 발췌 원문을 읽어 만든다. A 는 XML 주석 · 라이선스 머리말을 지운 뒤 청킹한다.
5. 페이지 사이 링크(`## 관련 페이지`)는 scope.json 에서 만든다.
6. Kimi 호출 간격: C 는 호출마다 21초, A 는 문항마다 50초. 둘 다 지연에서 뺀다.
7. 위키 본문은 영어 원문을 한국어로 정리한 것이다(컴파일 프롬프트가 한국어).

`results/raw/test_low_0928/system_c` 의 280행은 corpus/raw 로 만든 옛 위키(`wiki-astra`)와
옛 한국어 프롬프트로 만든 것이라 A 와 비교하거나 합치지 않는다.

## 구성

```
systems/system_c_llm_wiki/
├── compiler/      위키 컴파일러 (오프라인 1단계)
├── linker/        페이지 간 상호링크 생성 (scope.json 관계, API 호출 없음)
├── agent/         에이전트 루프와 배치 러너 (온라인 2단계)
│   ├── run_agent.py    3개 도구 루프, provider별 호출 경로
│   ├── run_batch.py    다중 모델 배치 실행, 재개, 증거 기록
│   ├── models.json     참가자 모델 레지스트리
│   └── probe_api.py    도구 호출·추론 파라미터·토큰 열 지원 확인
├── wiki-c3/       본실행 위키 (gpt-6-astra, C3 입력) — 재구축 후 생긴다
├── wiki/  wiki-astra/  wiki-4o-mini/   옛 산출물 (corpus/raw 입력, manifest 없음). 본실행에 쓰지 않는다
├── tests/         단위 테스트 (API 호출 없음)
└── validation/    재구축 검사(check_rebuilt_wiki.py) · 답변 레코드 검증(validate_records.py) · 위키 검증 · 위키 간 비교
```

각 폴더의 README 에 세부 설계와 사용법이 있다.

## 현재 상태

- [x] 문서트리 설계 — 엔티티 단위 페이지 구조
- [x] 컴파일러 (`compiler/compile_wiki.py`, `wiki_manifest.json` 기록)
- [x] 상호링크 생성기 (`linker/crosslink_wiki.py --wiki-root`)
- [x] 에이전트 루프 (`list_pages` / `read_page` / `submit_answer`)와 배치 러너
- [x] 검증 (`validation/check_rebuilt_wiki.py`, `validation/validate_records.py`, `validation/validate_wiki.py`)
- [x] 9/28 테스트 실행 — 옛 위키 · 옛 프롬프트라 인용하지 않는다
- [ ] 위키 재구축 (`wiki-c3`, gpt-6-astra) → 링크 → 검사 PASS
- [ ] 7종 본실행 → 레코드 검증 통과
