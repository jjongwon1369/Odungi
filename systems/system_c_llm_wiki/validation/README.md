# System C — 검증

재구축한 위키가 System A 와 같은 입력에서 빠짐없이 만들어졌는지(재구축 검사), 답변 레코드가
팀 공용 형식과 A 의 행 규칙을 지키는지(레코드 검증), 위키가 원본 정보를 보존하는지(위키 검증)를 본다.
전부 읽기 전용이고 LLM API 를 부르지 않는다. 모두 리포 루트에서 실행한다.

## 구성과 순서

본실행에서는 아래 순서로 돌린다. 전체 절차는 `../CLAUDE.md` 의 "본실행 절차" 를 따른다.

| 순서 | 스크립트 | 언제 | 통과 기준 |
| --- | --- | --- | --- |
| 1 | `check_rebuilt_wiki.py` | 컴파일 · 링크 뒤, run_batch 전 | 마지막 줄 `RESULT: PASS` (exit 0), `[WARN] 페이지 수` 없음, 캐비닛 페이지 손 검토 |
| 2 | `validate_records.py` | run_batch 뒤 | `[실패]` 없음 (exit 0) |
| 참고 | `validate_wiki.py` | 컴파일 뒤 | 출처 · 식별자 보존율 · 토큰 수 |
| 참고 | `compare_wikis.py` | 컴파일 모델 비교 때 | — |

## 1. 재구축 검사 — `check_rebuilt_wiki.py`

A 는 색인 청크 수나 코퍼스 라벨이 어긋나면 검색기가 멈춘다. C 의 위키는 컴파일 모델이 쓴
결과물이라, A 와 같은 입력에서 나왔는지와 입력 밖 지식이 섞이지 않았는지를 run_batch 전에
따로 확인한다. 하나라도 FAIL 이면 exit 1 이다. (#27 A 기준 점검)

- **(a) manifest**: `wiki_manifest.json` 이 있고, 적힌 페이지가 전부 있고, 그 밖의 `.md` 가 없다.
  입력 sha256 = 저장소 `documents.jsonl` 의 sha256 = A 가 색인한 파일(`71c40454…`).
  페이지 수 34개는 참고 항목 (h) 에서 본다. `[WARN] 페이지 수` 줄이 나오면 PASS 여도 멈춘다.
- **(b) 출처**: 전 페이지의 `corpus_source` · `corpus_snapshot` · `commit_hash` 가 기대값이고 `compiled_by` 가 `openai/gpt-6-astra` 다.
- **(c) 코퍼스 밖 식별자**: A 의 `pipeline.yaml` 규칙으로 페이지 본문에서 뽑은 식별자가 컴파일 입력 어디에도 없으면 실패(page:line 으로 보고).
  (c3) 은 hex ID 를 다른 개체 이름에 붙인 것으로 보이는 줄의 **검토 목록**이며 종료 코드와 무관하다. 사람이 읽고, ID 를 잘못 붙인 줄이면 알린다.
- **(d) 제외 ID 유출**: scope.json 이 제외한 디바이스 타입 · 캐비닛 클러스터 ID 가 본문에 들어갔는지.
- **(e) 구축 원장**: `build_calls.jsonl` · `build_tokens.json` 이 있고, 호출마다 4열이 따로 있으며 합산 필드가 없다.
- **(f) 상호링크**: `## 관련 페이지` 가 있는 페이지가 있고, 링크 대상이 전부 있고, 라벨의 이름 · ID 가 scope.json 과 같다. 링커를 빼먹거나 다른 폴더에 돌리면 여기서 FAIL 이다.

검사기가 못 잡는 것이 하나 있다. 컴파일 모델이 C3 에서 빠진 클러스터를 hex ID 없이 이름으로만
다시 적는 경우다. 그래서 `device-types/temperature-controlled-cabinet.md` 의 Heater / Cooler 줄은
손으로 본다. C3 는 Heater 에 클러스터를 하나도 붙이지 않고, Cooler 아래 `0x0052`(선택)만 있다.
`0x0048` · `0x0049`(Oven Cavity Operational State · Oven Mode)가 클러스터로 적혀 있으면 불합격이다.

```bash
python3 systems/system_c_llm_wiki/validation/check_rebuilt_wiki.py systems/system_c_llm_wiki/wiki-c3
# 보고서 파일이 필요하면 --json-out <경로>
```

옛 위키(`wiki/`, `wiki-astra/`, `wiki-4o-mini/`)는 manifest 가 없고 corpus/raw 로 만들어져 FAIL 이 정상이다.

## 2. 답변 레코드 검증 — `validate_records.py`

System A / B / C 어느 결과 폴더에나 돌아간다. 기대 격자(모델 × 문항 × 회차)는 파일 내용이 아니라
인자로 받는다. `--models-json` 과 `--questions` 를 빼면 모델이 통째로 빠져도 통과하므로 반드시 준다.

행 판정은 A 규칙을 따른다(A 의 `run_eval._is_retryable`: error 가 있고 answer 가 빈 행만 다시 돌린다).

- **실패**: 오류 행(`status: error`, 빈 answer), `max_turns` 행(구버전), 오류 없이 빈 answer, 출력 토큰 0,
  C 행의 `latency_ms.generate` 0, (qid, model, run) 중복 · 누락, `config_hash` 여러 종, 4열 ≠ 호출 기록 합.
- **참고**: A/B 의 dangling_citations, `no_submit`(도구 없이 텍스트로 답한 행, 채점 대상), 읽지 않은 페이지 인용,
  답변 속 도구 호출 표기.

```bash
python3 systems/system_c_llm_wiki/validation/validate_records.py \
    results/raw/<run label>/system_c \
    --models-json systems/system_c_llm_wiki/agent/models.json \
    --questions benchmark/questions_v1.jsonl --runs 1
```

오류 행이 남으면 run_batch 를 같은 인자로 다시 돌린다(끝난 행은 건너뛰고 오류 행만 다시 돈다).
run_batch 의 종료 코드는 남은 오류 행을 알려주지 않으므로 이 검증이 관문이다.
스모크 폴더(개발용 질문 일부만 돌림)는 격자가 맞지 않으므로 `--infer-grid-from-file` 로 확인만 한다.

## 3. 위키 검증 — `validate_wiki.py` (참고)

- **출처**: 모든 페이지가 `source_paths` 와 `commit_hash`(SSOT) 프론트매터를 갖는지 확인한다.
  출처 없는 페이지는 실험 결과의 추적 가능성을 깨뜨리므로 실패로 처리한다.
- **식별자 보존**: 페이지의 `source_paths` 로 컴파일러가 실제로 읽은 `documents.jsonl` 본문을 찾아,
  그 안의 식별자(클러스터·속성 ID `0x....`, XML `name` 속성값)가 페이지에 그대로 남아있는지 대조한다.
  보존율이 60% 미만인 페이지는 정보 누락으로 경고한다. 식별자는 컴파일 과정에서 LLM 이 바꾸거나
  빠뜨리기 가장 쉬운 값이면서, 기술문서 질의에서 정답 판정의 기준이 되는 값이라 별도로 검사한다.
- **전체 토큰 수**: 위키 전체의 추정 토큰 수와 페이지별 분포를 계산한다. 페이지 1개가 단일 `read_page`
  호출로 읽히는 크기인지 확인하고, 전체 주입 대비 에이전트 탐색의 토큰 절감 효과를 정량화하는 기준으로 쓴다.

```bash
python3 systems/system_c_llm_wiki/validation/validate_wiki.py systems/system_c_llm_wiki/wiki-c3
```

인자를 빼면 옛 `wiki/` 를 검사한다. 프론트매터 누락 또는 식별자 보존율 미달 시 exit code 1 을 반환한다.
