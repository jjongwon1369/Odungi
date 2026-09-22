# System C — 위키 컴파일러

공통 코퍼스(`corpus/raw/connectedhomeip`)를 출처와 식별자를 보존한 구조화 Markdown
위키로 사전 컴파일한다.

## 구성

- `compile_wiki.py` — 컴파일러 본체

## 설계

### 1. 엔티티 단위 그룹핑
`corpus/metadata/scope.json` 을 런타임에 읽어서, 원본 파일들을 **엔티티**
(클러스터 / 디바이스 타입 / 공유 베이스) 단위로 묶는다. 한 엔티티에 속한
spec · sdk · 구현 · 문서 파일을 모두 모아 **페이지 1개**로 컴파일한다.

파일 하나당 페이지 하나가 아니라 엔티티 하나당 페이지 하나인 이유는, 같은 기능에
대한 정보가 여러 파일(스펙 XML, SDK 정의 XML, 구현 C++, README)에 흩어져 있어서
파일 단위로 쪼개면 질의 시 한 기능을 이해하는 데 여러 페이지를 봐야 하기 때문이다.

`scope.json` 에서 `specification_path` 를 공유하는 클러스터들(예: HEPA Filter
Monitoring 0x0071 과 Activated Carbon Filter Monitoring 0x0072)은 자동으로 같은
페이지로 병합된다.

### 2. 컴파일 프롬프트
식별자 보존을 최우선 규칙으로 지시한다. 클러스터 ID(`0x0006`), 속성·명령·이벤트
이름, 함수명, 파일 경로는 번역·변형 없이 원문 그대로 복사하게 한다. 원문에 없는
내용을 추측해 채우는 것을 금지한다.

### 3. 출처 메타데이터
모든 페이지 상단에 YAML 프론트매터로 `entity` / `ids` / `source_paths` /
`commit_hash`(SSOT) / `doc_type` 을 기록한다.

## 사용법

리포 루트에서 실행한다 (스크립트가 `corpus/`, `systems/` 를 현재 작업 디렉터리
기준 상대 경로로 참조하기 때문).

```bash
# 1) 그룹핑 결과만 확인 (API 호출 없음)
python3 systems/system_c_llm_wiki/compiler/compile_wiki.py --dry-run

# 2) 실제 컴파일
export GOOGLE_API_KEY="..."          # provider 에 맞는 키
WIKI_COMPILER_PROVIDER=google \
WIKI_COMPILER_MODEL=<모델명> \
  python3 systems/system_c_llm_wiki/compiler/compile_wiki.py
```

### 옵션

| 옵션 | 설명 |
| --- | --- |
| `--dry-run` | 파일 → 엔티티 그룹핑 결과만 출력, API 호출 없음 |
| `--only <key>` | 엔티티 하나만 컴파일 (예: `--only "base:Label"`) |
| `--limit N` | 최대 N개 엔티티만 컴파일 |
| `--force` | 이미 생성된 페이지도 다시 컴파일 (기본은 건너뜀) |

### 환경변수

| 변수 | 설명 |
| --- | --- |
| `WIKI_COMPILER_PROVIDER` | `anthropic` / `openai` / `google` |
| `WIKI_COMPILER_MODEL` | 사용할 모델명 |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GOOGLE_API_KEY` | provider 별 API 키 |

## 재실행 동작

- 이미 생성된 페이지는 건너뛴다(`--force` 로 무시 가능). 컴파일이 중간에 실패해도
  다시 실행하면 못 만든 것만 이어서 만든다.
- API 가 일시적 오류(503 / 429)를 반환하면 지수 백오프로 재시도한다. 재시도까지
  실패한 엔티티는 건너뛰고 나머지를 계속 진행한 뒤, 종료 시 실패 목록을 출력한다.
