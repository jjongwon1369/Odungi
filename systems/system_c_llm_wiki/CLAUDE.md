# System C — LLM 위키 (프로젝트 맥락 · 불변식)

경북대 종합설계프로젝트1 팀 `Odungi` 의 System C 담당(정채희) 작업 공간.
이 컴포넌트를 건드리기 전에 반드시 알아야 할 맥락과 불변식을 기록한다.

## 연구 주제

"RAG와 LLM 위키 아키텍처 기반 기술문서 지식베이스 실증 비교 연구".
동일한 코퍼스 · 동일한 질의셋 · 동일한 생성 모델로 세 시스템을 비교한다.

| 시스템 | 방식 | 담당 |
| --- | --- | --- |
| A | 단일 RAG (청킹 → 임베딩 → 하이브리드 검색 → 재순위) | 김태이 |
| B | 분해형 RAG (질문 분해 후 A의 검색 반복) | — |
| **C** | **LLM 위키 (사전 컴파일 + 에이전트 페이지 탐색)** | **정채희 (이 폴더)** |

코퍼스 담당은 이동수. `corpus/` 와 `scripts/corpus/` 는 코퍼스 담당 영역이므로 임의 수정하지 않는다.

베이스라인 논문: arXiv 2605.18490 (Vector RAG vs LLM-Compiled Wiki)

## 불변식 (바꾸려면 팀 합의 필요)

- **SSOT**: connectedhomeip 커밋 `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`. 모든 산출물이 이 해시를 프론트매터에 기록한다.
- **코퍼스**: `corpus/raw/connectedhomeip` 282개 파일. 로컬에서 `scripts/corpus/extract_corpus.py` 로 생성하며 git에 커밋하지 않는다(라이선스 검토 미완).
- **범위**: `corpus/metadata/scope.json` 이 정의하는 4 Device Type / 23 Cluster. 코드에서 하드코딩으로 대체하지 말고 런타임에 읽는다.
- **생성 모델**: System A/B/C가 반드시 동일 모델을 사용한다. 현재 `gpt-5.6-luna` (Azure OpenAI 게이트웨이).
- **질의 방식**: 에이전트 페이지 탐색형 (수행계획 발표 시 확정). 정적 전체주입 아님.

## 아키텍처

### 1단계 — 오프라인 위키 컴파일 (`compiler/compile_wiki.py`)

코퍼스를 **엔티티 단위**(클러스터 / 디바이스 타입 / 공유 베이스)로 묶어 **엔티티당 페이지 1개**로 컴파일한다. 282개 파일 → 34개 엔티티.

**왜 엔티티 단위인가**: 한 클러스터의 정보가 스펙 XML · SDK 정의 XML · 구현 C++ · README에 흩어져 있다. 파일 단위나 콘텐츠 종류 단위로 쪼개면 질의 시 한 기능을 이해하는 데 여러 페이지를 열어야 한다. (초기 스캐폴드가 `cluster/`, `device_type/`, `implementation/`, `commissioning/` 종류별 분리였는데 이 이유로 폐기했다.)

`scope.json` 에서 `specification_path` 를 공유하는 클러스터는 자동 병합된다. 예: HEPA Filter Monitoring `0x0071` + Activated Carbon Filter Monitoring `0x0072` → `ResourceMonitoring.xml` 한 페이지.

### 2단계 — 온라인 에이전트 페이지 탐색 (미구현, 다음 작업)

| 도구 | 역할 |
| --- | --- |
| `list_pages` | 위키 페이지 목록(목차) 반환 |
| `read_page` | 지정 페이지 1개 전문 반환 |
| `submit_answer` | 근거 페이지와 함께 최종 답변 제출, 루프 종료 |

최대 30턴. 열람한 페이지는 팀 공용 답변 레코드의 `retrieved.wiki_pages` 에 기록한다.

**정적 전체주입을 쓰지 않는 근거(실측)**: 코퍼스 원본 약 971K 토큰, 실측 압축비 14.0% → 위키 전체 약 136K 토큰. 가구 3종에서 이미 128K 모델에 안 들어간다. 계획된 12종 확장 시 약 54만 토큰이며 질의마다 전량을 지불해야 한다. 에이전트 탐색은 목차 + 페이지 2~3개(약 1만 토큰)면 된다.

## 디렉토리

```
systems/system_c_llm_wiki/
├── CLAUDE.md                   이 파일
├── compiler/compile_wiki.py    위키 컴파일러
├── validation/validate_wiki.py 출처·식별자 보존·토큰 수 검증
└── wiki/                       컴파일 산출물 (손으로 수정하지 않는다)
    ├── base/  clusters/  device-types/  examples/  guides/  misc/
```

## 명령어

모두 **리포 루트에서** 실행한다 (스크립트가 `corpus/`, `systems/` 를 CWD 기준 상대 경로로 참조).

```bash
# 환경변수 로드 (.env.local 은 gitignore 되어 있음)
set -a; . ./.env.local; set +a

# 그룹핑 결과만 확인 (API 호출 없음)
python3 systems/system_c_llm_wiki/compiler/compile_wiki.py --dry-run

# 전체 컴파일
WIKI_COMPILER_PROVIDER=openai WIKI_COMPILER_MODEL=gpt-5.6-luna \
  python3 systems/system_c_llm_wiki/compiler/compile_wiki.py

# 검증
python3 systems/system_c_llm_wiki/validation/validate_wiki.py
```

컴파일러 옵션: `--dry-run` / `--only <key>` / `--limit N` / `--force`(기생성 페이지도 재생성).
기본 동작은 이미 만들어진 페이지 건너뛰기라, 중단 후 재실행하면 못 만든 것만 이어서 만든다.
환경변수 `WIKI_COMPILER_TIMEOUT`(초, 기본 600)으로 요청 타임아웃 조절.

## 환경

- API 키와 엔드포인트는 리포 루트 `.env.local` 에만 둔다. **절대 커밋하거나 대화/스크린샷에 노출하지 않는다.** (`.gitignore` 에 등록되어 있음)
- 엔드포인트는 Azure OpenAI 게이트웨이(`.../openai/v1`)이며 OpenAI SDK + `base_url` 로 붙는다. `OPENAI_BASE_URL`, `OPENAI_API_KEY` 사용.
- 이 게이트웨이는 `usage.prompt_tokens_details.cached_tokens`(cache_read), `cache_write_tokens`(cache_creation), `completion_tokens`(output)를 제공하므로 팀 공용 스키마의 **토큰 4열을 그대로 채울 수 있다**. 토큰은 절대 합산하지 말 것 — 베이스라인 논문이 합산 때문에 비용 가설 판정에 실패했다.
- 도구 호출(function calling) 지원 확인됨 → 에이전트 루프 구현 가능.

## 알려진 함정

- **`.DS_Store`**: macOS가 코퍼스 폴더에도 만든다. 컴파일러는 `SKIP_NAMES` 로 거른다. `.gitignore` 에도 있다.
- **큰 엔티티 타임아웃**: Thermostat(54개 파일), Scenes(21개) 같은 엔티티는 입력이 수만 토큰이라 타임아웃/연결 오류가 난다. `_TRANSIENT_ERROR_HINTS` 에 타임아웃 계열을 포함시켜 재시도하도록 되어 있다.
- **코퍼스 메타데이터 불일치 (미해결)**: 로컬 추출 시 `snapshot.json` 의 `origin` 이 `DS-J-L/connectedhomeip` → `project-chip/connectedhomeip` 로, `validation_report.json` 의 `artifact_set_hash` 가 `43eb0ad2...` → `a44005d0...` 로 달라진다. 같은 SSOT 커밋인데 해시가 다른 건 결정적 재현성 문제라 이동수님 확인 대기 중. 이 두 파일은 커밋하지 말 것.
- **`scope.json` 의 `cluster_base`**: `source_role` 이 `specification` / `sdk_codegen` 두 항목으로 나뉘어 있고 파일명 stem이 제각각(`ModeBase`, `mode-base-cluster`)이다. `CLUSTER_BASE_CANONICAL_NAME` 로 정규화해 한 엔티티로 묶는다.
- **병합된 엔티티의 `.name`**: 여러 클러스터가 한 엔티티로 합쳐지면 `.name` 은 먼저 등록된 클러스터명으로 고정된다. 이름으로 역탐색하지 말고 `cluster_name_to_key` 를 쓴다.

## 현재 상태

- [x] 문서트리 설계 (엔티티 단위)
- [x] 컴파일러 + 검증 스크립트 — 커밋 `8cc6b86`
- [x] 문서를 에이전트 탐색형으로 정정 — 커밋 `d3c633b`
- [x] 엔드포인트 진단 (모델 / 토큰 4열 / 긴 입력 / 도구 호출 전부 통과)
- [x] 전체 34페이지 컴파일 — `gpt-5.6-luna` 로 `--force` 재컴파일 완료 — 커밋 `686cc94`
- [x] PR 생성 — [#6](https://github.com/jjongwon1369/Odungi/pull/6)
- [ ] 상호링크 생성
- [ ] 에이전트 루프 구현

페이지가 어떤 모델로 만들어졌는지는 프론트매터 `compiled_by` 로 확인한다:
`grep -h compiled_by systems/system_c_llm_wiki/wiki/*/*.md | sort | uniq -c`

## 규칙

- 커밋 메시지는 Conventional Commits (`feat(system-c):`, `docs(system-c):`, `chore:`). 본문은 한국어.
- `wiki/` 의 Markdown은 컴파일 산출물이므로 손으로 고치지 않는다. 내용이 잘못되면 프롬프트나 그룹핑 로직을 고치고 재컴파일한다.
- PR 리뷰어는 이동수(`DS-J-L`), 김태이.
- 논문 사사문구: "본 연구는 과학기술정보통신부 및 정보통신기획평가원의 SW중심대학사업의 연구결과로 수행되었음"(2021-0-01082)
