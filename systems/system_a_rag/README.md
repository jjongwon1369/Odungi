# System A — 단일 RAG

구현: `rag_proto/` (Python 패키지). 실행·불변식은 `rag_proto/CLAUDE.md`, 통합 절차는 `rag_proto/TEAM_INTEGRATION.md` 참조.

| 팀 폴더 | rag_proto 대응 |
|---|---|
| chunking/ | `src/rag_proto/s1_convert.py`, `s2_chunk.py` |
| indexing/ | `src/rag_proto/s3_embed.py`, `s4_index.py` |
| retrieval/ | `src/rag_proto/s5_retrieve.py` — System B 가 재사용하는 `Retriever` 클래스 |
| (생성) | `src/rag_proto/s6_generate.py`, `ask.py` |
| (평가 원자료) | `src/rag_proto/run_eval.py` → `runs/<ts>_<config_hash>/answers.jsonl` |

입력: C3 tier `corpus/tiers/c3/processed/documents.jsonl` (팀 스크립트로 로컬 생성). 저장소를 직접 파싱하지 않음.
SSOT: `corpus/tiers/c3/metadata/snapshot.json` 의 commit / snapshot_id 를 `rag_proto/configs/ssot.yaml` 에 복사
(현재 `corpus-c3:2f00a807…`, 버전 `0.1-c3`).

## 본실험 실행 절차 (System A·B)

모든 명령은 이 폴더 아래 **`rag_proto/`에서** 실행한다. System B도 같은 폴더에서 A의 검색 색인을 재사용해 돈다.
여기서 돌려야 결과의 `code_commit`에 팀 저장소 커밋이 남는다.

다른 위치에 editable로 설치한 venv를 쓰면 그쪽 코드가 import된다. 이때는 명령 앞에 `PYTHONPATH=src`를 붙인다.
배치 첫 줄에 찍히는 `코드: <경로> @ <커밋>`의 경로가 이 폴더인지 확인한다.

### 0. 준비 (한 번)

| 단계 | 명령 | 비고 |
|---|---|---|
| 설치·코퍼스 | `rag_proto/TEAM_INTEGRATION.md`의 "실행" | `data/team/`에 C3 `documents.jsonl`·`scope.json` 복사 |
| 설정 확인 | `python -m rag_proto.config` | 코퍼스 파일 라벨이 `ssot.yaml`과 다르면 여기서 멈춘다 |
| 색인 | `python -m rag_proto.s1_convert && python -m rag_proto.s2_chunk && python -m rag_proto.s3_embed && python -m rag_proto.s4_index --reset` | 임베딩은 처음 한 번만 오래 걸리고 이후 캐시 |
| API 키 | 이 폴더에 `.env` 작성(`.env.example` 참고): `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `MOONSHOT_API_KEY` | git 제외. 범용 `OPENAI_BASE_URL`은 일부러 읽지 않는다 |

참가자 모델·접속 주소·호출 설정은 `configs/participants.yaml` 한 곳에 있다. 모델 이름이 `TODO-`로 시작하는 참가자가
대상에 들어 있으면 명령 전체가 실행 전에 멈춘다. 확정 전에는 `--participants`로 그 참가자를 빼고 돌린다.

### 1~3. 본실험 전 확인

```bash
python -m rag_proto.run_eval --list-models   # 1. 주소·키마다 쓸 수 있는 모델 ID 목록 (과금 없음)
python -m rag_proto.run_eval --smoke         # 2. 참가자마다 1번 호출해 키·모델 ID·호출 설정 확인 (소량 과금)
python -m rag_proto.run_eval --participants all --runs 1 --limit 2 \
    --questions ../../../benchmark/questions_v1.jsonl                     # 3. A 2문항 시험
python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py --participants all --runs 1 --limit 2 \
    --questions ../../../benchmark/questions_v1.jsonl                     # 3. B 2문항 시험
```

### 4. 본실험

```bash
# 1회차 (심판 채점 대상)
python -m rag_proto.run_eval --participants all --runs 1 --questions ../../../benchmark/questions_v1.jsonl
python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py --participants all --runs 1 \
    --questions ../../../benchmark/questions_v1.jsonl

# 2·3회차 추가: 1회차 폴더를 이어서 쓰면 이미 끝난 1회차는 건너뛴다
python -m rag_proto.run_eval --participants all --runs 3 --questions ../../../benchmark/questions_v1.jsonl \
    --resume runs/<A 1회차 폴더>
python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py --participants all --runs 3 \
    --questions ../../../benchmark/questions_v1.jsonl --resume runs/<B 1회차 폴더(_batch_decomposed)>
```

- 중간에 끊기면 같은 명령에 `--resume runs/<폴더>`를 붙인다. 실패한 문항만 다시 돈다.
- 참가자 일부만 돌리려면 `--participants claude-sonnet-5,gpt-6-sol`처럼 쓴다.
- 종료 코드가 1이면 실패 행이나 건너뛴 참가자가 있다는 뜻이다(`summary.json`의 `skipped_participants`).

### 5. 결과

`runs/<시각>_<config_hash>_batch/`(B는 `_batch_decomposed`)에 생긴다. `runs/`는 git 제외 대상이다.

| 파일 | 내용 |
|---|---|
| `answers.jsonl` | 채점 대상. (qid, model, run)마다 한 줄, 실패도 `error` 행으로 남는다 |
| `summary.json` | 모델별 토큰 4열·청구 기준 토큰·지연, 건너뛴 참가자, `code_commit`·`config_hash`·코퍼스 라벨 |
| `invocations.jsonl` | 실행할 때마다 한 줄(시각, 코드 커밋, 참가자, 회차) |
| `failed_attempts.jsonl` | 이어하기로 다시 돌린 실패 시도. 채점 대상은 아니지만 과금은 됐다 |
| `eval.jsonl` | 행마다 인용 무결성·기권·식별자 점검 결과 |
| `participants.yaml` | 이 실행에 쓴 참가자 설정 사본 |

### 예상 시간 (Mac 노트북 MPS, 1회차 = 참가자 7 × 40문항)

| | 검색 | LLM 호출 |
|---|---|---|
| A | 약 7분 (문항당 재순위 약 11초, 참가자·회차 간 재사용) | 280회 |
| B | 참가자가 분해하면 약 3시간, 고정 모델이 분해하면 약 20분 | 560회 (생성 + 분해) |

2·3회차는 A의 검색을 1회차 결과에서 재사용하므로 LLM 호출 시간만 더 든다. B는 참가자가 분해하면
하위질의가 회차마다 달라질 수 있어 회차당 최대 약 3시간이 더 든다.

LLM 생성 시간은 모델마다 다르다. 3단계 2문항 시험을 돌리면 문항별 소요 시간이 화면에 찍히고,
`summary.json`의 모델별 `latency_ms`(p50·max)로 본실험 시간을 가늠한다. `--smoke`는 연결만 보며 시간을 재지 않는다.
