# System C — LLM 위키 (프로젝트 맥락 · 불변식)

경북대 종합설계프로젝트1 팀 `Odungi` 의 System C 담당(정채희) 작업 공간.
이 컴포넌트를 건드리기 전에 반드시 알아야 할 맥락과 불변식을 기록한다.

## 연구 주제

"RAG와 LLM 위키 아키텍처 기반 기술문서 지식베이스 실증 비교 연구".
동일한 코퍼스 · 동일한 질의셋 · 동일한 생성 모델로 세 시스템을 비교한다.

| 시스템 | 방식 | 담당 |
| --- | --- | --- |
| A | 단일 RAG (청킹 → 임베딩 → 하이브리드 검색 → 재순위) | 김태이 |
| B | 분해형 RAG (질문 분해 후 A의 검색 반복) | 김태이 |
| **C** | **LLM 위키 (사전 컴파일 + 에이전트 페이지 탐색)** | **정채희 (이 폴더)** |

코퍼스 담당은 이동수. `corpus/` 와 `scripts/corpus/` 는 코퍼스 담당 영역이므로 임의 수정하지 않는다.

베이스라인 논문: arXiv 2605.18490 (Vector RAG vs LLM-Compiled Wiki)

## 불변식 (바꾸려면 팀 합의 필요)

- **SSOT**: connectedhomeip 커밋 `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`. 모든 산출물이 이 해시를 프론트매터에 기록한다.
- **코퍼스**: 위키 컴파일러의 입력은 **`corpus/tiers/c3/processed/documents.jsonl`** (팀 공용 정규화 산출물, 282개 문서 / 264 whole · 18 trimmed)이다.
  `corpus/raw/connectedhomeip` 원본을 컴파일러가 직접 읽지 않는다 — System A/B와 입력 범위를 맞추기 위한 조건이며 이슈 #23 1·4절의 핵심.
  이 파일의 sha256 은 System A 가 색인한 파일과 같은 `71c40454c6695fc6fd13aade191e1a21dfd11e5311def31f1f07adddf1618359` 이어야 한다.
  `snapshot_id`(`corpus-c3:2f00a807…`)는 라벨이라 본문이 달라도 같게 나올 수 있어 대조 기준이 못 된다. (#27 A 기준 점검)
  티어 산출물은 로컬에서 `python3 scripts/corpus/build_tiers.py --tier c3` 로 만들며 git에 커밋하지 않는다(라이선스 검토 미완).
  `CONNECTEDHOMEIP_PATH` 환경변수에 로컬 clone 경로가 필요하다.
- **엔드포인트**: `models.json` 의 `base_url` 을 항상 명시적으로 넘긴다. 생략하면 SDK가 `OPENAI_BASE_URL`/`ANTHROPIC_BASE_URL` 을 읽어 환경변수가 이긴다(실측 확인). 인자를 빼는 건 고정이 아니다.
- **범위**: `corpus/metadata/scope.json` 이 정의하는 4 Device Type / 23 Cluster. 코드에서 하드코딩으로 대체하지 말고 런타임에 읽는다.
- **참가자 모델**: System A/B/C가 같은 7종을 같은 조건으로 쓴다. C 는 `agent/models.json`, A 는 `systems/system_a_rag/rag_proto/configs/participants.yaml` 이 기준이고,
  모델 ID · effort · 출력 상한 파라미터가 서로 같아야 한다(`tests/test_a_parity.py` 가 검사). 7종 모두 effort low, 출력 상한 16000, temperature 미전송.
- **위키 컴파일 모델**: `gpt-6-astra` (OpenAI 공식 엔드포인트). 참가자가 아니며 위키 구축에만 쓴다(9/28 팀 확인).
- **질의 방식**: 에이전트 페이지 탐색형 (수행계획 발표 시 확정). 정적 전체주입 아님.
- **프롬프트**: System A 의 `s6_generate.SYSTEM_PROMPT` **영어 원문**을 쓴다(9/30 팀 결정). 번역본을 쓰면 프롬프트 차이가 시스템 간 변수로 남는다.
  C 고유 차이는 위키 도구 안내 단락, 규칙 3(인용 대상이 `[chunk_id]` → `cited_pages`), 규칙 5(제출 경로) 세 곳뿐이다. 기권 문구는 규칙 1에만 한 번 나온다.
  첫 user 메시지는 A `build_prompt` 의 틀에서 `<context>` 만 빠진 `<question>…</question>` 과 끝 문장 `C_USER_TAIL` 이다(인용 대상만 페이지 ID).
  `submit_answer` 의 answer 설명에 언어 지시를 넣지 않는다. `tests/test_prompt_parity.py` · `tests/test_a_parity.py` 가 검사한다. (#27 A 기준 점검)
- **클라이언트**: A 의 `s6_generate` 와 같게 `max_retries=5`, 타임아웃은 넘기지 않는다(SDK 기본값 연결 5초 · 응답 600초). 앱 수준 429 재시도 루프도 두지 않는다(A 에 없다). (#27 A 기준 점검)

## 본실행 조건

System A 의 `test_low_0928`(`results/raw/test_low_0928/system_a/README.md`)과 **같은 조건**으로 한 번 돌린다.
하나라도 다르면 A 행과 (qid, model, run) 으로 짝지어 비교할 수 없다. (#27 A 기준 점검)

| 항목 | 값 |
| --- | --- |
| 참가자 | 7종 전부 — gpt-6-luna, gpt-6-sol, gpt-5.6-sol, claude-sonnet-5, claude-opus-5-5, deepseek-flash, kimi-k3 |
| 추론 강도 | effort low (`models.json` 의 `reasoning_config`) |
| 출력 상한 | 호출마다 16000 (`run_agent.MAX_OUTPUT_TOKENS`) |
| temperature | `models.json` 그대로 = 7종 모두 보내지 않는다 |
| 질문 | `benchmark/questions_v1.jsonl` 40문항 (run_batch 기본값) |
| 회차 | `--run 1` (기본값). `--limit` 없음 |
| 위키 | `systems/system_c_llm_wiki/wiki-c3`, `--wiki-label c3` |
| 결과 | 새 run label 하나. `results/raw/<run label>/system_c/answers.jsonl` 280행 (7 × 40 × 1) |

## 본실행 절차 (순서대로, 리포 루트에서)

모두 **리포 루트에서** 실행한다 (스크립트가 `corpus/`, `systems/` 를 CWD 기준 상대 경로로 참조).
한 단계라도 기대값과 다르면 다음 단계로 넘어가지 않고 김태이에게 알린다.
커밋되지 않은 변경이 없는 상태에서 돌린다(레코드의 `agent_commit` 에 `-dirty` 가 붙지 않아야 한다).

```bash
# 0. 키 로드. 조건을 바꾸는 환경변수가 없어야 한다(아래 줄이 아무것도 출력하지 않아야 한다)
set -a; . ./.env.local; set +a
env | grep -E '^(CORPUS_DOCS|IDENTIFIER_CONFIG|WIKI_[A-Z_]*)=' | cut -d= -f1

# (a) 입력 파일이 A 가 색인한 파일과 바이트까지 같은지
shasum -a 256 corpus/tiers/c3/processed/documents.jsonl
#   → 71c40454c6695fc6fd13aade191e1a21dfd11e5311def31f1f07adddf1618359 이어야 한다
#   (shasum 이 없으면 python3 -c "import hashlib;print(hashlib.sha256(open('corpus/tiers/c3/processed/documents.jsonl','rb').read()).hexdigest())")

# (b) 위키 컴파일 — gpt-6-astra, 새 폴더 wiki-c3, 전체 --force
#   wiki-c3 폴더가 이미 있으면 시작하지 말고 먼저 알린다(이전 시도의 원장·페이지가 섞인다)
python3 systems/system_c_llm_wiki/compiler/compile_wiki.py \
  --wiki-root systems/system_c_llm_wiki/wiki-c3 --dry-run        # "282개 파일을 34개 엔티티로 그룹핑함" (API 호출 없음, 아무것도 쓰지 않음)
WIKI_COMPILER_PROVIDER=openai WIKI_COMPILER_MODEL=gpt-6-astra \
  python3 systems/system_c_llm_wiki/compiler/compile_wiki.py \
  --wiki-root systems/system_c_llm_wiki/wiki-c3 --force
#   마지막 [요약] 이 "실패 0개" 여야 한다. 실패가 있으면 같은 명령에서 --force 만 빼고
#   다시 실행한다(wiki_manifest.json 이 같으면 빠진 페이지만 만든다).

# (c) 상호링크 (API 호출 없음). --wiki-root 는 (b) 와 같은 값
python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --wiki-root systems/system_c_llm_wiki/wiki-c3
python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --wiki-root systems/system_c_llm_wiki/wiki-c3 --check
#   --check 가 "문제 0건" 이어야 한다

# (d) 위키 검사. 마지막 줄이 RESULT: PASS 이고, (h) 에 "[WARN] 페이지 수" 줄이 없어야 한다(34페이지)
python3 systems/system_c_llm_wiki/validation/check_rebuilt_wiki.py systems/system_c_llm_wiki/wiki-c3
#   + 손 검토: 캐비닛 페이지의 Heater / Cooler 줄 (검사기는 hex ID 없이 이름만 적은 것을 못 잡는다)
grep -n "Heater\|Cooler\|0x0048\|0x0049\|Oven" \
  systems/system_c_llm_wiki/wiki-c3/device-types/temperature-controlled-cabinet.md
#   C3 는 Heater 에 클러스터를 하나도 붙이지 않는다. Cooler 아래 0x0052(선택)만 있다.
#   0x0048 · 0x0049 · Oven Cavity Operational State · Oven Mode 가 클러스터로 적혀 있으면 불합격이다
#   (개정 이력 요약 속 "Oven Cavity Operational State" 한 줄은 C3 원문에도 있다).

# (e) 스모크 — 개발용 질문셋으로만 한다. questions_v1 로 하면 시험셋을 한 번 더 보는 것이다
python3 systems/system_c_llm_wiki/agent/run_batch.py \
    --wiki-root systems/system_c_llm_wiki/wiki-c3 --wiki-label c3 \
    --questions systems/system_a_rag/rag_proto/data/queries.jsonl \
    --models all --limit 2 --run-label smoke_c3
python3 -c "import json;[print(r['model'],r['qid'],r['status'],r['turns'],r['tokens']['cache_creation'],r['latency_ms']['generate']) for r in map(json.loads,open('results/raw/smoke_c3/system_c/answers.jsonl'))]"
#   status error 행이 없고, 전 행 latency_ms.generate > 0 이어야 한다.
#   페이지를 읽은(turns ≥ 2) GPT 행 중 하나 이상에서 tokens.cache_creation > 0 이어야 한다(긴 프롬프트의 캐시 쓰기).
#   0 이면 Responses 4열 매핑 문제이므로 멈춘다
#   (results/raw/smoke_c3/system_c/runs/c3_run1/invocations.jsonl 의 usage_raw 와 대조).
#   학교망이면 DeepSeek 은 (f) 처럼 빼고 돌린 뒤 다른 네트워크에서 --models deepseek-flash 로 한 번 더.
#   smoke_c3 는 버리는 폴더다. 커밋하지 않고 본실행 결과와 합치지 않는다.

# (f) 본실행. 새 run label — test_low_0928 이나 다른 wiki_label 행이 있는 폴더는 안 된다
#   학교망 밖(핫스팟 등)이면 한 번에:
python3 systems/system_c_llm_wiki/agent/run_batch.py \
    --wiki-root systems/system_c_llm_wiki/wiki-c3 --wiki-label c3 \
    --models all --run-label <합의한 run label>
#   학교망은 DeepSeek 접속을 막는다. 학교망에서는 6종만 돌리고
#   --models gpt-6-luna,gpt-6-sol,gpt-5.6-sol,claude-sonnet-5,claude-opus-5-5,kimi-k3
#   DeepSeek 은 다른 네트워크에서 같은 인자로 따로 돌린다(A·B 는 9/28 21시대 핫스팟에서 돌렸다)
python3 systems/system_c_llm_wiki/agent/run_batch.py \
    --wiki-root systems/system_c_llm_wiki/wiki-c3 --wiki-label c3 \
    --models deepseek-flash --run-label <같은 run label>

# (g) 레코드 검증. [실패] 가 하나도 없어야 한다
python3 systems/system_c_llm_wiki/validation/validate_records.py \
    results/raw/<run label>/system_c \
    --models-json systems/system_c_llm_wiki/agent/models.json \
    --questions benchmark/questions_v1.jsonl --runs 1
#   오류 행이 남으면 (f) 를 같은 인자로 다시 실행한다(끝난 행은 건너뛰고 오류 행만 다시 돈다).
#   run_batch 의 종료 코드는 남은 오류 행을 알려주지 않으므로 이 검증이 관문이다.
#   전 행의 위키 출처가 한 가지인지도 본다. 결과가 키 하나 × 280 이어야 한다:
#   ('c3', 'corpus/tiers/c3/processed/documents.jsonl', True, <config_hash>, <커밋, -dirty 없음>)
python3 -c "import json,collections;print(collections.Counter((r['wiki_label'],r['wiki_corpus_source'],r['wiki_corpus_snapshot']==r['corpus_snapshot'],r['config_hash'],r['agent_commit']) for r in map(json.loads,open('results/raw/<run label>/system_c/answers.jsonl'))))"
```

나눠 돌린 경우에도 `config_hash` 는 같다(`models.json` 전체를 해싱한다). `--wiki-root` · `--wiki-label` · `--run-label` 문자열과 코드 커밋까지 같아야 한다.
검증을 통과하면 `wiki-c3/` (페이지 · `wiki_manifest.json` · `build_calls.jsonl` · `build_tokens.json`)와 결과 폴더를 함께 커밋한다.

## 본실행에서 금지

- **`--allow-corpus-mismatch` / `--allow-config-change`**: 위키 출처 · manifest · 이어하기 설정 검사를 끄는 옵션이다. 멈추면 옵션을 붙이지 말고 원인을 고친다(위키 재컴파일, 새 run label).
- **출력 상한 바꾸기**: `WIKI_AGENT_MAX_OUTPUT_TOKENS` 를 설정하지 않고 `run_agent.MAX_OUTPUT_TOKENS` 도 고치지 않는다. 지금 코드는 이 변수를 읽지 않는다(16000 고정). 예전 `WIKI_AGENT_TIMEOUT` 도 더 이상 읽지 않는다.
- **입력 · 대상을 바꾸는 환경변수**: `CORPUS_DOCS`, `WIKI_ROOT`, `IDENTIFIER_CONFIG`. `.env.local` 에도 두지 않는다.
- **인자 바꾸기**: `--run 2` 이상, `--limit`, `--questions`, `--max-turns`(기본 30).
- **`results/raw/test_low_0928/system_c` 재사용**: 그 280행은 corpus/raw 로 만든 옛 위키(`wiki-astra`)와 옛 한국어 프롬프트로 만든 것이다. 인용 · 합산 · 이어하기에 쓰지 않는다. 그 폴더로 돌리면 run_batch 가 다른 wiki_label 이 있다며 exit 2 로 멈춘다.

## System A 와 다른 점 (설계상 차이, 고치지 않고 적는다)

run_batch 가 결과 폴더 `README.md` 의 "System A 와의 설계상 차이" 절에 앞의 6개를 자동으로 적는다. README 를 손으로 고칠 때도 지우지 않는다.

1. **다중 턴 도구 사용**: `list_pages` / `read_page` / `submit_answer`. 최대 30턴, 호출(턴)마다 출력 상한 16000. A 는 top-5 문맥을 받아 한 번 생성한다.
2. **GPT 3종은 Responses API** (A 는 Chat Completions). Chat Completions 에서는 function tools 와 reasoning_effort 를 함께 보내면 400 이다(`agent/TASK_multimodel.md`).
3. **목차에 페이지 ID 가 보인다**. 클러스터 페이지 ID 에는 hex ID 가 들어 있다(예: `clusters/0x0006-on-off`). ID 질문 일부는 목차만으로 답할 수 있다.
4. **컴파일 입력**: 위키는 gpt-6-astra 가 C3 발췌 원문을 그대로 읽어 만든다. A 는 XML 주석(CSA 고지)과 라이선스 머리말을 지운 뒤 청킹한다.
5. **상호링크**: `## 관련 페이지` 는 LLM 이 아니라 linker 가 scope.json 관계로 만든다.
6. **Kimi 호출 간격**: C 는 호출마다 21초(`min_interval_s`), A 는 문항마다 50초(`min_question_interval_s`). 둘 다 지연에서 뺀다.
7. **위키 본문 언어**: 컴파일 프롬프트가 한국어라 위키는 영어 원문을 한국어로 정리한 것이다. 논문 방법 절에 적는다.

## 아키텍처

### 1단계 — 오프라인 위키 컴파일 (`compiler/compile_wiki.py`)

`corpus/tiers/c3/processed/documents.jsonl` 의 문서를 **엔티티 단위**(클러스터 / 디바이스 타입 / 공유 베이스)로 묶어 **엔티티당 페이지 1개**로 컴파일한다. 282개 문서 → 34개 엔티티.

**왜 엔티티 단위인가**: 한 클러스터의 정보가 스펙 XML · SDK 정의 XML · 구현 C++ · README에 흩어져 있다. 파일 단위나 콘텐츠 종류 단위로 쪼개면 질의 시 한 기능을 이해하는 데 여러 페이지를 열어야 한다. (초기 스캐폴드가 `cluster/`, `device_type/`, `implementation/`, `commissioning/` 종류별 분리였는데 이 이유로 폐기했다.)

`scope.json` 에서 `specification_path` 를 공유하는 클러스터는 자동 병합된다. 예: HEPA Filter Monitoring `0x0071` + Activated Carbon Filter Monitoring `0x0072` → `ResourceMonitoring.xml` 한 페이지.

그룹핑 직후, 첫 엔티티를 컴파일하기 전에 `wiki_manifest.json`(있어야 할 페이지 목록, 입력 파일 sha256, snapshot_id, 컴파일 모델)을 쓴다.
A 는 색인 청크 수가 어긋나면 검색기가 멈춘다. C 는 엔티티 하나가 실패하면 그 페이지만 조용히 빠지므로, run_batch 가 이 목록으로 페이지 누락과 입력 파일을 확인한다. (#27 A 기준 점검)

컴파일 뒤 `linker/crosslink_wiki.py` 가 scope.json 관계로 `## 관련 페이지` 섹션을 넣는다. 페이지 바이트가 바뀌므로 반드시 run_batch 전에 돌린다.

### 2단계 — 온라인 에이전트 페이지 탐색 (`agent/run_agent.py`, `agent/run_batch.py`)

| 도구 | 역할 |
| --- | --- |
| `list_pages` | 위키 페이지 목록(목차) 반환 |
| `read_page` | 지정 페이지 1개 전문 반환 |
| `submit_answer` | 근거 페이지와 함께 최종 답변 제출, 루프 종료 |

최대 30턴. 호출 경로는 GPT 3종 Responses API, DeepSeek · Kimi Chat Completions 호환, Claude 2종 Messages API 다.
읽은 페이지는 팀 공용 답변 레코드의 `retrieved.wiki_pages` 와 `citations`(A 의 문맥 top-5 자리)에, 모델이 인용한 페이지는 `cited_pages` 에 기록한다.
`latency_ms.generate` 는 A 와 같은 뜻으로 LLM 호출 시간의 합이다(턴별 `api_ms`, 호출 간격 대기 제외).

행 판정은 A 규칙을 따른다. 빈 답변 · 최대 턴 도달 · 호출 실패는 `status: error`, `answer: ""` 로 두고(남은 문장은 C 전용 필드 `partial_answer`) 다시 돌린다.
도구 없이 텍스트로 답한 `no_submit` 행은 A 의 평문 답변처럼 채점 대상으로 둔다. 한 결과 폴더에는 wiki_label 하나만 둔다. (#27 A 기준 점검)

**정적 전체주입을 쓰지 않는 근거(실측)**: 코퍼스 원본 약 971K 토큰, 실측 압축비 14.0% → 위키 전체 약 136K 토큰. 가구 3종에서 이미 128K 모델에 안 들어간다. 계획된 12종 확장 시 약 54만 토큰이며 질의마다 전량을 지불해야 한다. 에이전트 탐색은 목차 + 페이지 2~3개(약 1만 토큰)면 된다.

## 디렉토리

```
systems/system_c_llm_wiki/
├── CLAUDE.md                          이 파일
├── compiler/compile_wiki.py           위키 컴파일러
├── linker/crosslink_wiki.py           상호링크 생성기 (scope.json 관계, API 호출 없음)
├── validation/check_rebuilt_wiki.py   재구축 위키 검사 (run_batch 전 관문)
├── validation/validate_records.py     답변 레코드를 팀 공용 AnswerRecord · A 행 규칙으로 검증
├── validation/validate_wiki.py        출처 · 식별자 보존 · 토큰 수 (참고)
├── agent/run_agent.py                 에이전트 루프 (질의 1건)
├── agent/run_batch.py                 40문항 × 7모델 배치 실행 + 팀 공용 레코드 생성
├── agent/models.json                  참가자 7종 provider / reasoning 설정
├── wiki-c3/                           본실행 위키 (컴파일 산출물, 손으로 수정하지 않는다)
│   ├── base/  clusters/  device-types/  examples/  guides/  misc/
│   ├── wiki_manifest.json             있어야 할 페이지 목록 · 입력 sha256 · 컴파일 모델
│   ├── build_calls.jsonl              API 호출 1건 = 1줄 (과금 원장, append-only)
│   └── build_tokens.json              위 원장에서 집계한 4열 (위키 구축 비용)
└── wiki/  wiki-astra/  wiki-4o-mini/  옛 산출물 (corpus/raw 입력, manifest 없음). 본실행에 쓰지 않는다
```

## 개발용 명령

본실행은 위 "본실행 절차" 만 따른다. 아래는 개발 · 점검용이며 질의 예시는 시험셋(`questions_v1`)에 없는 것만 쓴다.

```bash
# 그룹핑 결과만 확인 (API 호출 없음, 아무것도 쓰지 않음)
python3 systems/system_c_llm_wiki/compiler/compile_wiki.py --dry-run

# 링크 변경 예정만 확인 (파일 수정 없음)
python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --wiki-root systems/system_c_llm_wiki/wiki-c3 --dry-run

# 단위 테스트 (API 호출 없음)
for t in systems/system_c_llm_wiki/tests/test_*.py; do python3 "$t"; done

# 에이전트 질의 1건 (verbose). --wiki-root 를 빼면 옛 wiki/ 를 읽는다
python3 systems/system_c_llm_wiki/agent/run_agent.py \
    --wiki-root systems/system_c_llm_wiki/wiki-c3 --model gpt-6-luna \
    --query "On/Off 클러스터의 OFFONLY feature 제약은?" --verbose

# 결과 파일 저장 / 최대 턴 제한
python3 systems/system_c_llm_wiki/agent/run_agent.py \
    --wiki-root systems/system_c_llm_wiki/wiki-c3 --query "..." --output result.json --max-turns 5
```

컴파일러 옵션: `--dry-run` / `--wiki-root <dir>` / `--only <key>` / `--limit N` / `--force`(기생성 페이지도 재생성).
기본 동작은 이미 만들어진 페이지 건너뛰기라, 중단 후 재실행하면 못 만든 것만 이어서 만든다.
기존 페이지가 같은 입력 · 같은 모델의 manifest 로 설명되지 않으면(옛 컴파일러 산출물, 다른 코퍼스 · 모델) `--only`/`--limit` 없는 전체 `--force` 가 아닌 한 시작하지 않는다.
환경변수: `WIKI_COMPILER_PROVIDER` · `WIKI_COMPILER_MODEL`(본실행은 `openai` / `gpt-6-astra`, 기본값은 쓰지 않는다), `WIKI_COMPILER_TIMEOUT`(초, 기본 600), `WIKI_COMPILER_MAX_TOKENS`(Anthropic 출력 상한, 기본 16000). `CORPUS_DOCS` · `WIKI_ROOT` 는 본실행에서 설정하지 않는다.
출력 상한·차단·거절(`finish_reason=length` / `content_filter` / Anthropic `max_tokens`·`refusal`)로 끝난 응답은 페이지로 저장하지 않고 실패로 남긴다. 호출은 이미 과금됐으므로 `build_calls.jsonl` 에는 기록된다.

에이전트 환경변수: `WIKI_AGENT_MODEL`(run_agent 단독 실행의 기본 모델만 정한다. run_batch 는 모델을 직접 넘긴다), `IDENTIFIER_CONFIG`(개발용, 본실행에서 설정하지 않는다).

`run_batch.py` 옵션: `--run-label`(**필수**) / `--models` / `--wiki-root` / `--wiki-label` / `--questions` / `--run` / `--max-turns` / `--limit` / `--allow-corpus-mismatch` / `--allow-config-change`.
첫 API 호출 전에 ① 위키 출처(`corpus_source`·`corpus_snapshot`) ② `wiki_manifest.json`(페이지 누락, 입력 sha256 = A 색인 입력) ③ 결과 폴더의 wiki_label 단일성 ④ 선택한 전 모델의 이어하기 설정을 검사한다.
어긋나면 ①~③ 은 exit 2, ④ 는 exit 3 으로 **호출 전에** 멈춘다.

## 환경

- API 키와 엔드포인트는 리포 루트 `.env.local` 에만 둔다. **절대 커밋하거나 대화/스크린샷에 노출하지 않는다.** (`.gitignore` 에 등록되어 있음)
- 엔드포인트는 `models.json` 의 `base_url` 을 **항상 명시적으로** 넘긴다. 없으면 실행을 막는다. 인자를 생략하면 SDK가 `OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` 환경변수를 읽어 환경변수가 이긴다 — 즉 생략은 고정이 아니라 환경변수 지배 허용이다(실측 확인, 이슈 #23). 진단 스크립트(`probe_*.py`)도 같은 규칙이다. 폴백을 두면 다른 provider 키가 엉뚱한 호스트로 전송된다.
- 키만 `.env.local` 에 둔다: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY`.
- 토큰 4열은 `uncached_input` / `cache_creation` / `cache_read` / `output` 이다. provider마다 원본 필드 위치가 다르다:
  OpenAI `prompt_tokens` 는 캐시를 **포함**하므로 읽기·쓰기를 빼서 `uncached_input` 을 만든다. Anthropic `input_tokens` 는 캐시를 **제외**한 값이라 그대로 쓴다. 캐시 쓰기는 Chat Completions 는 `prompt_tokens_details.cache_write_tokens`, Responses 는 `input_tokens_details.cache_write_tokens` 에 있다(최상위에 없다).
- 토큰은 절대 합산하지 말 것 — 베이스라인 논문이 합산 때문에 비용 가설 판정에 실패했다. `usage_raw` 원본을 함께 남겨 사후 재계산이 가능하게 한다.
- 도구 호출(function calling)과 추론 파라미터 지원은 `agent/probe_api.py` 로 확인했다.

## 알려진 함정

- **`.DS_Store`**: macOS가 코퍼스 폴더에도 만든다. 컴파일러는 `SKIP_NAMES` 로 거른다. `.gitignore` 에도 있다.
- **큰 엔티티 타임아웃**: Thermostat(54개 파일), Scenes(21개) 같은 엔티티는 입력이 수만 토큰이라 타임아웃/연결 오류가 난다. `_TRANSIENT_ERROR_HINTS` 에 타임아웃 계열을 포함시켜 재시도하도록 되어 있다. 그래도 실패한 엔티티는 페이지가 없으므로 `[요약]` 의 실패 수와 검사기 (a) 로 확인한다.
- **코퍼스 메타데이터 불일치 (미해결)**: 로컬 추출 시 `snapshot.json` 의 `origin` 이 `DS-J-L/connectedhomeip` → `project-chip/connectedhomeip` 로, `validation_report.json` 의 `artifact_set_hash` 가 `43eb0ad2...` → `a44005d0...` 로 달라진다. 같은 SSOT 커밋인데 해시가 다른 건 결정적 재현성 문제라 이동수님 확인 대기 중. 이 두 파일은 커밋하지 말 것. 본문이 같은지는 `documents.jsonl` 의 sha256 으로만 판단한다.
- **`scope.json` 의 `cluster_base`**: `source_role` 이 `specification` / `sdk_codegen` 두 항목으로 나뉘어 있고 파일명 stem이 제각각(`ModeBase`, `mode-base-cluster`)이다. `CLUSTER_BASE_CANONICAL_NAME` 로 정규화해 한 엔티티로 묶는다.
- **레코드의 `corpus_version` 은 자기검증이 아니다**: 코퍼스 메타데이터에서 그대로 베껴 쓰기 때문에, 위키가 다른 입력으로 만들어져 있어도 `0.1-c3` 로 적힌다. 실제로 그렇게 됐었다(이슈 #23 1-4). 그래서 `run_batch.py` 가 실행 전에 위키 프론트매터의 `corpus_source` 와 `wiki_manifest.json` 의 입력 sha256 을 직접 보고 다르면 종료한다.
- **컴파일러 입력은 `documents.jsonl` 뿐**: `corpus/raw` 를 직접 읽으면 scope 밖 디바이스 타입까지 위키에 들어가 System A/B와 입력 범위가 달라진다(실제로 발생 → 7개 페이지 오염, 이슈 #23).
- **제외 클러스터의 이름만 재등장**: C3 캐비닛 발췌에는 Heater 쪽 클러스터(0x0048 · 0x0049)가 없다. 컴파일 모델이 이를 hex ID 없이 이름으로만 다시 적으면 검사기가 못 잡는다. 9/28 옛 위키에서는 Q-multihop-010 에서 7종 모두 Oven 클러스터를 답했다. 절차 (d) 의 손 검토가 이 때문이다.
- **링커를 빼먹거나 다른 폴더에 돌리기**: 예전 링커는 환경변수 `WIKI_ROOT` 만 봐서, 빠뜨리면 기본 `wiki/` 를 고쳤다. 지금은 `--wiki-root` 를 주고 `[대상]` 줄로 확인한다. 링크가 없으면 검사기 (f) 가 FAIL 이다.
- **학교망은 DeepSeek 접속을 막는다**: DNS 는 풀리지만 연결이 안 된다(9/28 A 확인). 연결 타임아웃 5초 × 재시도 5회 뒤 오류 행이 된다. 다른 네트워크에서 `--models deepseek-flash` 로 따로 돌린다.
- **나눠 돌린 실행의 summary · README**: run_batch 가 결과 폴더의 전 모델로 다시 만들지만, 280행이 다 찼는지는 절차 (g) 의 validate_records 로 확인한다.
- **400 응답은 재시도하지 않는다**: 추론 강도 파라미터가 거부됐을 때 조용히 빼고 다시 부르면 "추론 강도 low 고정"이라는 통제가 깨진 채 정상 종료된 것처럼 보인다. 그래서 400은 그대로 실패로 기록한다.
- **병합된 엔티티의 `.name`**: 여러 클러스터가 한 엔티티로 합쳐지면 `.name` 은 먼저 등록된 클러스터명으로 고정된다. 이름으로 역탐색하지 말고 `cluster_name_to_key` 를 쓴다. 링커는 링크마다 그 ID 자신의 scope.json 이름을 붙인다(예전에는 `0x0072` 를 HEPA Filter Monitoring 으로 적었다).

## 현재 상태

- [x] 문서트리 설계 (엔티티 단위)
- [x] 컴파일러 + 검증 스크립트 — 커밋 `8cc6b86`
- [x] 문서를 에이전트 탐색형으로 정정 — 커밋 `d3c633b`
- [x] 엔드포인트 진단 (모델 / 토큰 4열 / 긴 입력 / 도구 호출 전부 통과)
- [x] 전체 34페이지 컴파일 — `gpt-5.6-luna`, 커밋 `686cc94` (corpus/raw 입력 시절 `wiki/`. 본실행에 쓰지 않는다)
- [x] PR 생성 — [#6](https://github.com/jjongwon1369/Odungi/pull/6)
- [x] 상호링크 생성 — `linker/crosslink_wiki.py`
- [x] 에이전트 루프 구현 — `agent/run_agent.py`
- [x] 7종 × 40문항 테스트 실행 (9/28, `results/raw/test_low_0928/system_c` 280행) — 옛 위키 `wiki-astra`(corpus/raw 입력) · 옛 프롬프트라 인용 · 합산하지 않는다
- [x] 이슈 #23 1~3절 반영 (입력을 `documents.jsonl` 로 교체 / 400 재시도 제거 / 레코드 필드 보강)
- [x] 답변 레코드 검증기 — `validation/validate_records.py` (#23 5절 체크리스트)
- [x] PR #27 리뷰 1차 반영 (엔드포인트 명시 / 캐시쓰기 위치 / 병합 업서트 / 코퍼스 c3 경로)
- [x] PR #27 리뷰 2차 반영 (과금 원장 / 잘림·거절 처리 / config_hash 범위 / 검증기 4열 재계산 / 식별자 기준)
- [x] PR #27 3차 리뷰 · 동수님 리뷰 P1 반영 — 커밋 `4fb852a`
- [x] #27 A 기준 점검 반영 (wiki_manifest · check_rebuilt_wiki · 링커 `--wiki-root`·라벨 · 클라이언트 설정 · 첫 user 메시지 · 오류 행 규칙 · generate 지연)
- [ ] 위키 재구축 (`wiki-c3`, gpt-6-astra, `--force`) → 링크 → 검사 PASS
- [ ] 7종 본실행 (새 run label) → validate_records 통과

페이지가 어떤 모델로 만들어졌는지는 프론트매터 `compiled_by` 로 확인한다(`34 compiled_by: openai/gpt-6-astra` 한 줄이어야 한다):
`grep -h compiled_by systems/system_c_llm_wiki/wiki-c3/*/*.md | sort | uniq -c`

## 규칙

- 커밋 메시지는 Conventional Commits (`feat(system-c):`, `docs(system-c):`, `chore:`). 본문은 한국어.
- `wiki*/` 의 Markdown은 컴파일 산출물이므로 손으로 고치지 않는다. 내용이 잘못되면 프롬프트나 그룹핑 로직을 고치고 재컴파일한다. `## 관련 페이지` 는 링커만 쓴다.
- PR 리뷰어는 이동수(`DS-J-L`), 김태이.
- 논문 사사문구: "본 연구는 과학기술정보통신부 및 정보통신기획평가원의 SW중심대학사업의 연구결과로 수행되었음"(2021-0-01082)
