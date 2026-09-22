# 팀 저장소 통합 절차 — System A (rag_proto)

Odungi 저장소에 `rag_proto` 를 올리고 PR 을 만드는 순서.
저장소 규칙: **브랜치 파서 작업 → PR → 리뷰 → main 머지.** main 에 직접 push 하지 않음.

---

## 0. 사전 확인

```bash
cd ~/Desktop/김태이/대학교/수업/3-2/종합설계프로젝트1/RAG설계/rag_proto
git status --short          # 미커밋 변경이 있으면 먼저 커밋
grep -c "team_corpus" configs/corpus.yaml src/rag_proto/s1_convert.py   # 둘 다 0 이면 안 됨
```

---

## 1. 팀 저장소 클론 및 브랜치 생성

```bash
cd ~/Desktop/김태이/대학교/수업/3-2/종합설계프로젝트1/RAG설계
git clone <Odungi 저장소 URL> Odungi
cd Odungi
git checkout main
git pull
git checkout -b feature/system-a-rag-prototype
```

브랜치 이름은 `feature/<시스템>-<내용>` 형식. 나중에 B 담당자가 `feature/system-b-decomposition` 처럼 맞출 수 있음.

---

## 2. rag_proto 를 systems/system_a_rag/ 아래로 복사

```bash
# 팀 저장소의 system_a_rag 는 README 만 있는 빈 껍데기. 그 안에 패키지를 통째로 넣는다.
rsync -av --exclude '.git' --exclude '.venv' --exclude 'data/raw' --exclude 'data/team' \
      --exclude 'data/chroma' --exclude 'data/.embed_cache' --exclude 'runs' \
      --exclude '__pycache__' --exclude '*.egg-info' --exclude '.env' \
      ../rag_proto/  systems/system_a_rag/rag_proto/

ls systems/system_a_rag/rag_proto/
```

팀 README 의 `chunking/ indexing/ retrieval/` 하위 폴더는 **그대로 두고** 건드리지 않음.
패키지를 쪼개 넣으면 import 경로가 전부 바뀌어 위험함. 폴더 대응은 README 에 한 줄로 적어줌.

---

## 3. system_a_rag/README.md 갱신

`systems/system_a_rag/README.md` 를 아래로 교체.

```markdown
# System A — 단일 RAG

구현: `rag_proto/` (Python 패키지). 실행·불변식은 `rag_proto/CLAUDE.md` 참조.

| 팀 폴더 | rag_proto 대응 |
|---|---|
| chunking/  | `src/rag_proto/s1_convert.py`, `s2_chunk.py` |
| indexing/  | `src/rag_proto/s3_embed.py`, `s4_index.py` |
| retrieval/ | `src/rag_proto/s5_retrieve.py` — **System B 가 재사용하는 `Retriever` 클래스** |
| (생성)     | `src/rag_proto/s6_generate.py`, `ask.py` |
| (평가 원자료) | `src/rag_proto/run_eval.py` → `runs/<ts>_<config_hash>/answers.jsonl` |

입력: `corpus/processed/documents.jsonl` (CORPUS_V1.md §15). 저장소 직접 파싱하지 않음.
SSOT: `corpus/metadata/snapshot.json` 의 commit / snapshot_id 를 `configs/ssot.yaml` 에 복사.

## 실행

    cd systems/system_a_rag/rag_proto
    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[models,llm]"
    mkdir -p data/team
    cp ../../../corpus/processed/documents.jsonl data/team/     # 로컬에 있을 때
    cp ../../../corpus/metadata/scope.json      data/team/
    python -m rag_proto.config
    python -m rag_proto.s1_convert && python -m rag_proto.s2_chunk
    python -m rag_proto.check_queries
```

---

## 4. 커밋

```bash
git add systems/system_a_rag/
git status --short          # data/team, .env, runs 가 없는지 확인
git commit -m "feat(system-a): RAG 프로토타입 추가 — 팀 코퍼스 documents.jsonl 입력, SSOT 1ac132b5"
git push -u origin feature/system-a-rag-prototype
```

---

## 5. PR 생성

GitHub 웹에서 `feature/system-a-rag-prototype` → `main` 으로 PR. 아래 본문 사용.

```markdown
## System A 단일 RAG 프로토타입

### 요약
- 수행계획서 RAG 6단계(s1~s6) 구현. 질의 → 근거 인용 답변 JSON 관통 확인
- 입력을 팀 코퍼스 `documents.jsonl` 로 전환 (CORPUS_V1.md §15 준수)
- SSOT `1ac132b5` / snapshot `corpus-v0.1:ee88b47a…` 로 설정 (`configs/ssot.yaml`)
- 개인 샘플 시기(1.4.2, b9c05ca0) 설정은 폐기

### 팀 자산과의 접점
- `Retriever` (s5_retrieve.py) — System B 가 재사용할 검색 인터페이스
- `answers.jsonl` — A/B/C 공용 답변 스키마 초안 (Notion 참조). `retrieved` 블록만 시스템별 상이
- 청크·답변에 `corpus_snapshot` / `corpus_version` 기록 — Device Type 3/6/12 비교군 구분용

### 검증
- 팀 형식 픽스처(`tests/fixtures/team/`)로 S1–S2 통과. 발췌형 XML(루트 없음) 처리 확인
- 식별자 무손실 0건, chunk_id 중복 0건
- 실제 `documents.jsonl` 로는 미검증 — 파일 수령 후 `check_queries` 재실행 필요

### 리뷰 요청
- @이동수 `documents.jsonl` 필드 해석이 맞는지 (`s1_convert.convert_from_team_corpus`)
- @정채희 답변 스키마 `retrieved.wiki_pages` 매핑이 자연스러운지
- 질의셋 gold answer 는 1.4.2 기준 작성 → 1.7 코퍼스에서 재확인 예정

### 미포함
- 생성 LLM 실호출 (API 키·모델 ID 팀 합의 대기)
- data/, runs/, .env 는 .gitignore 로 제외
```

---

## 6. 머지 후

```bash
git checkout main && git pull
git branch -d feature/system-a-rag-prototype
```

이후 작업은 항상 새 브랜치에서. 예: `feature/system-a-reranker-ablation`.

---

## 자주 하는 실수

| 실수 | 결과 | 예방 |
|---|---|---|
| `.venv` 가 복사됨 | 수백 MB 커밋 | rsync `--exclude '.venv'` 확인 |
| `data/team/documents.jsonl` 커밋 | 라이선스 미승인 자료 공개 | `.gitignore` 에 `data/team/` 있음. `git status` 로 재확인 |
| `.env` 커밋 | API 키 노출 | 커밋 전 `git ls-files | grep .env` 가 비어야 함 |
| main 에 직접 push | 팀 규칙 위반 | 항상 `git checkout -b` 먼저 |
