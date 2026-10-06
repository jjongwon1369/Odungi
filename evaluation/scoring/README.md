# 채점 스크립트 (평가분석 담당 박종원)

정답 파일(`test_v1.jsonl`)과 정답표(`ground_truth/1.7`)는 실험이 끝날 때까지 공개하지 않습니다. 이 폴더에는 코드만 있습니다.

| 파일 | 하는 일 |
| --- | --- |
| `adapt_records.py` | A·B `AnswerRecord`와 C `run_agent.py` 결과를 채점 입력으로 변환 |
| `score_l1.py` | 식별자 자동 채점 (비용 0) |
| `run_judge.py` | 심판자 LLM 채점 (Claude Code · Codex CLI, 구독 계정) |
| `parse_matter.py`, `matter_ids.py` | 원본 XML → 정답표 생성, ID 정규화 |

## 변환 규칙 (`adapt_records.py`)

- 인용: A·B는 `citations`(LLM에 넘긴 상위 청크 전부)가 아니라 **답변 본문의 `[chunk_id]` 표기**만 인용으로 본다. 표기는 `[S1]`, `[S2]`…로 바꾼다.
- 검색 결과에 없는 청크 ID 표기는 `[인용오류]`로 바꾸고 `citation_error`에 남긴다. 답변은 정상 채점한다.
- `error`가 `dangling_citations`로 시작하면 실패가 아니라 인용 오류로 본다.
- 답변 **전체가** `제공된 문서에서 확인되지 않음`일 때만 기권(`abstained`)으로 본다. 기권 문구 뒤에 설명을 덧붙이면 답한 것으로 채점하고 `partial_abstain`을 표시한다.
- C(위키)는 `cited_pages`를 인용으로 쓴다. 비어 있으면 `citations`의 페이지 ID를 쓴다. 답 본문에 섞인 도구 호출 표기는 잘라내고 `markup_leak`을 표시한다.
- 제출 도구를 부르지 않았지만 본문과 인용이 있는 C 답(`no_submit`)은 답한 것으로 채점한다.
- B는 `query_mode: "decomposed"`로 구분한다.
- C의 `prompt_tokens`는 캐시 읽기분을 포함하므로 `uncached_input = prompt_tokens - cache_read`로 바꾼다.

## 자동 채점 규칙 (`score_l1.py`)

- 16진 ID는 자릿수와 대소문자를 무시하고 같은 값으로 본다 (`0x06` = `0x0006`).
- 이름은 영숫자 경계로 찾는다. 한국어 조사가 붙어도 찾는다 (`OnOff는`).
- 질문에 "ID"가 있으면 ID까지 맞아야 정답이다. 없으면 정답 요소의 이름만 맞게 써도 인정한다.
- 실패 행(`error`)은 품질 점수에서 빼고 실패율로 따로 보고한다.
- 문항의 `scoring`이 `judge`(심판 전용)이면 자동 채점 대상에서 뺀다. 사전등록 기준 자동 채점은 34문항이다.

## 심판 실행 규칙 (`run_judge.py`)

- 답변 1건 = 독립 호출 1회. Claude는 도구를 모두 끈 상태(`--tools "" --safe-mode`), GPT는 읽기 전용, 둘 다 빈 임시 폴더에서 실행한다.
- 시스템·모델 이름은 넣지 않고 순서를 섞는다. 추론 강도는 medium. 프롬프트는 `judges/judge_prompt_v1.md`(9/26 고정).
- 인용 근거: A·B는 인용한 청크 전체, C는 `--wiki-root`로 지정한 위키에서 인용한 페이지 전체를 넣는다.
- `--sample 0.1`로 재채점해 같은 판정이 나오는지 확인한다.

## 실행

```bash
python adapt_records.py runs/<폴더>/answers.jsonl -o results/raw/A_gpt-6-luna_run1.jsonl
python score_l1.py results/raw/A_gpt-6-luna_run1.jsonl --queries <test_v1.jsonl>
python run_judge.py results/raw/*.jsonl --judge claude --chunks data/chunks.jsonl --out results/judged/claude.jsonl
```
