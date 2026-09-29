# 작업 지시 — 다중 모델 배치 실행 지원

기존 `run_agent.py`(OpenAI chat/completions 전용)와 `run_batch.py`(v0.3 스키마, 단일 모델)를
7개 참가자 모델로 확장한다. **v0.3 스키마의 기존 필드는 이름·타입·의미를 바꾸지 않는다.
필요한 것은 새 필드로 추가만 한다.** (종원님 채점 스크립트 호환)

---

## A. `run_agent.py` — provider 추상화

### A-1. 모델 해석
`models.json`을 읽어 모델 이름 → `{provider, model_id, key_env, base_url_env, reasoning_config}`로 해석한다.
`run_agent(..., model=...)`의 `model`은 `models.json`의 최상위 키다.

### A-2. 세 가지 호출 경로

| 경로 | 대상 | 엔드포인트 |
| --- | --- | --- |
| `openai_responses` | base_url이 api.openai.com | `POST /v1/responses` |
| `openai_chat` | base_url이 그 외 (DeepSeek, Moonshot) | `POST /v1/chat/completions` |
| `anthropic` | provider == anthropic | `POST /v1/messages` |

**OpenAI는 반드시 Responses API를 쓴다.** chat/completions에서는
`Function tools with reasoning_effort are not supported` 400이 발생함 (확인됨).

- Responses API 도구 형식은 평탄하다: `{"type":"function","name":...,"description":...,"parameters":...}`
  (chat/completions의 `{"type":"function","function":{...}}` 중첩 형식이 아님)
- 추론 강도는 `"reasoning": {"effort": "low"}`
- 대화 상태는 `input` 배열에 `function_call` / `function_call_output` 항목을 누적해 이어간다
- 도구 호출은 응답의 `output[]` 중 `type == "function_call"` 항목

**Anthropic**은 Messages API를 쓴다.
- 도구: `{"name":..., "description":..., "input_schema":...}`
- 추론: `"thinking": {"type": "adaptive"}` + `"output_config": {"effort": "low"}`
  (`thinking.type.enabled`는 이 모델들에서 거부됨 — 확인됨)
- 도구 호출은 `content[]` 중 `type == "tool_use"`, 결과는 `type == "tool_result"` 블록으로 회신

### A-3. reasoning_config 처리
`models.json`의 `reasoning_config`를 요청에 merge한다.
400 응답이면 **해당 키들을 제거해 1회만 재시도**하고, 결과에
`reasoning_applied: false`, `reasoning_note: "provider rejected"`를 남긴다.
성공하면 `reasoning_applied: true`.

### A-4. 토큰 4열 매핑
provider별 필드명을 통일 dict로 정규화한다.
**제공하지 않는 열은 0이 아니라 `None`으로 둔다.** (0과 "미제공"은 다르다)

| 열 | OpenAI Responses | Anthropic | OpenAI-호환(chat) |
| --- | --- | --- | --- |
| prompt_tokens | `usage.input_tokens` | `usage.input_tokens` | `usage.prompt_tokens` |
| output_tokens | `usage.output_tokens` | `usage.output_tokens` | `usage.completion_tokens` |
| cache_read | `usage.input_tokens_details.cached_tokens` | `usage.cache_read_input_tokens` | `usage.prompt_tokens_details.cached_tokens` |
| cache_write | `usage.cache_write_tokens` | `usage.cache_creation_input_tokens` | `usage.cache_write_tokens` |

턴별로 **열마다 따로 누적**한다. 열끼리 절대 합산하지 않는다.

### A-5. 기권 강제
시스템 프롬프트에 다음을 명시한다(이미 있으면 문구만 확인).

> 위키에서 근거를 찾지 못하면 추측하지 말고, 반드시 정확히
> `제공된 문서에서 확인되지 않음.` 만 답변으로 제출할 것.

### A-6. 페이지 해시
`read_page`로 페이지를 읽을 때마다 그 파일의 SHA-256을 계산해
`page_evidence` 리스트에 `{"path":..., "sha256":..., "turn":N}`으로 누적해 반환한다.

---

## B. `run_batch.py` — 다중 모델 / 재개 / 증거

### B-1. CLI
```
--models        쉼표 구분 모델 목록 또는 "all" (models.json 기준). 기본 all
--wiki-root     위키 경로
--wiki-label    위키 라벨 (예: astra)
--run           실행 회차, 기본 1
--out-dir       기본 results/system_c
--questions     기본 benchmark/questions_v1.jsonl
--limit         앞에서 N문항만 (스모크 테스트용)
```

### B-2. 출력 배치 — 팀 공용 구조를 따른다

```
results/raw/<run_label>/system_c/
├── answers.jsonl                  제출본 (40문항 × 7모델 = 280줄)
├── README.md                      실행 조건 + 위키 참조 정보
└── runs/<wiki_label>_run<N>/
    ├── summary.json               모델별 ok/error/abstained/avg_turns, 시작·종료 시각
    ├── invocations.jsonl          턴별 도구 호출 로그 (한 줄 = 한 턴)
    ├── failed_attempts.jsonl      실패한 호출
    └── models.json                사용한 모델 레지스트리 스냅샷
```

`--run-label`(기본 `run1`)로 상위 폴더를 지정한다.
작업 중에는 모델별 파일(`.partial/<model>.jsonl`)에 append 하고,
전 모델 완료 후 `answers.jsonl`로 합친다. 중단 시 재개는 partial을 기준으로 한다.

**위키 스냅샷은 복사하지 않는다.** README에 위키 경로와 커밋 SHA를 적고,
재현성은 레코드의 `wiki_build` + 페이지별 `sha256`으로 확보한다.

### B-3. 재개
시작 시 해당 모델의 jsonl을 읽어 이미 존재하는 `(qid, model, run)`은 건너뛴다.
레코드는 한 줄씩 즉시 append + flush 한다 (중단되어도 직전까지 보존).

### B-4. 트레이스 (증거)
`run_agent`의 `turn_details` 전체를 `invocations.jsonl`에 한 줄=한 턴으로 저장한다.
각 줄에 `qid`, `model`, `run`, `turn`, `tool_calls`, `arguments`, `result_len`, `sha256`, 턴별 토큰을 포함한다.
턴마다 어떤 도구를 호출했고 어떤 결과를 받았는지 전부 포함.
레코드에 `trace_path`(results/raw/<run_label>/ 기준 상대경로)를 넣는다.

### B-5. 레코드에 추가할 필드 (기존 필드는 그대로 유지)
```
wiki_build          위키를 컴파일한 모델 (페이지 프론트매터의 compiled_by에서 읽음)
wiki_label          astra / luna / 4o-mini
reasoning_effort    "light"
reasoning_config    실제로 전송한 파라미터 dict (거부되었으면 null)
reasoning_applied   true / false
abstained           answer가 정확히 "제공된 문서에서 확인되지 않음." 이면 true
status              "ok" | "max_turns" | "error"
trace_path          invocations.jsonl 내 해당 (qid, model) 항목을 가리키는 상대경로
wiki_pages_evidence [{path, sha256, turn}]   ← retrieved.wiki_pages는 기존 형식 유지
questions_sha256    질문셋 파일 해시
agent_commit        git rev-parse --short HEAD
```

`latency_ms.total`을 실제로 측정해 채운다 (현재 0으로 고정되어 있음).

### B-6. 실패 격리
모델 하나가 실패해도 나머지 모델은 계속 진행한다.
질문 하나가 실패하면 `status:"error"`, `error:"<메시지>"`로 기록하고 다음 질문으로 넘어간다.

### B-7. summary.json
`run_label`, `wiki_label`, `wiki_build`, `wiki_commit`, `ssot_commit`,
`questions_sha256`, `reasoning_effort`(= "light"), 실행한 모델 목록,
모델별 성공/실패/기권 수와 평균 턴 수, 시작·종료 시각, `agent_commit`.

### B-8. README.md 자동 생성
`results/raw/<run_label>/system_c/README.md`에 실행 조건을 기록한다.
위키 경로(`systems/system_c_llm_wiki/wiki-astra`)와 그 커밋 SHA,
SSOT 커밋, 질문셋 해시, 참가자 모델 7종과 각 모델의 추론 강도 적용 여부,
토큰 4열 중 provider가 제공하지 않는 열 목록.

---

## C. 검증

구현 후 반드시 실행할 것:

```bash
cd ~/capstone/Odungi && (set -a; . ./.env.local; set +a
python3 systems/system_c_llm_wiki/agent/run_batch.py \
  --wiki-root systems/system_c_llm_wiki/wiki-astra \
  --wiki-label astra --models all --limit 2 --run 1 --run-label smoke_test)
```

확인 사항:
1. 7개 모델 전부 레코드가 생성되었는가
2. 각 레코드의 `tokens` 4열이 채워졌는가 (미지원은 null)
3. `reasoning_applied`가 모델별로 기록되었는가
4. 트레이스 파일이 생성되고 `trace_path`가 맞는가
5. 같은 명령을 다시 실행하면 "건너뜀"으로 아무것도 새로 호출하지 않는가

---

## D. 팀 정합성 요구사항 (System A/B 실행 조건에 맞춤) — **최우선**

System A/B가 이미 `results/raw/test_low_0928/`에 40문항 × 7모델 = 280줄을
effort low로 실행 완료했다. System C는 **동일 조건**이어야 비교가 성립한다.
아래는 `results/raw/test_low_0928/system_a/README.md`에서 확인한 실제 조건이다.

### D-1. 출력 폴더 정정
`--run-label` 기본값을 **`test_low_0928`**으로 바꾼다.
결과는 `results/raw/test_low_0928/system_c/`에 들어간다. (`run1` 아님)

### D-2. 출력 상한
모든 모델에 **최대 출력 토큰 16000**을 설정한다.
(OpenAI Responses: `max_output_tokens`, Anthropic: `max_tokens`,
 OpenAI 호환 chat: `max_tokens`)

### D-3. temperature 미전송
**어떤 모델에도 `temperature`를 보내지 않는다.**
GPT·DeepSeek·Kimi는 추론 모드에서 거부하거나 무시하고, Claude는 원래 보내지 않는다.

### D-4. kimi-k3 요청 속도 제한
계정에 **분당 요청 3회** 제한이 있다. 에이전트 루프는 질문당 여러 번 호출하므로
`models.json`의 kimi-k3 항목에 `"min_interval_s": 21`을 추가하고,
러너가 **해당 모델의 API 호출 사이에 그 간격을 강제**하도록 한다
(질문 사이가 아니라 호출 사이여야 한다).
kimi-k3만 40문항에 50분 이상 걸릴 수 있으므로 **다른 모델보다 먼저 시작**하거나
별도 프로세스로 병행 실행할 것.
429를 받으면 지수 백오프로 최대 5회 재시도하고, 재시도는
`failed_attempts.jsonl`에 기록한다.

### D-5. 코퍼스 식별자 채우기
현재 `run_batch.py`는 `corpus_snapshot`과 `corpus_version`을 `None`으로 둔다.
A/B와 조인되도록 아래 값을 채운다 (`corpus/tiers/c3/metadata/snapshot.json` 출처).

```
corpus_version   : "0.1-c3"
corpus_snapshot  : "corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e"
corpus_commit    : "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"   (기존 유지)
corpus_phase     : "integrated"                                  (기존 유지)
```

하드코딩하지 말고 `corpus/tiers/c3/metadata/snapshot.json`에서 런타임에 읽는다.

### D-6. 모델 표기
A/B가 쓴 문자열과 정확히 일치해야 한다. `models.json`의 키가 이미 일치한다:
`gpt-6-luna`, `gpt-6-sol`, `gpt-5.6-sol`, `claude-sonnet-5`, `claude-opus-5-5`,
`deepseek-flash`, `kimi-k3`.
참고: `deepseek-flash`는 실제로 DeepSeek-V4.1-Flash다(V4 Flash가 9/10에 교체됨).
README에 이 사실을 적는다.

### D-7. 검증 명령 정정
```bash
cd ~/capstone/Odungi && (set -a; . ./.env.local; set +a
python3 systems/system_c_llm_wiki/agent/run_batch.py \
  --wiki-root systems/system_c_llm_wiki/wiki-astra \
  --wiki-label astra --models all --limit 2 --run 1 --run-label smoke_test)
```
스모크는 `smoke_test`로, 본실행은 `--run-label test_low_0928`로 한다.
