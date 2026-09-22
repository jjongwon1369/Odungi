# System A — 단일 RAG

구현: `rag_proto/` (Python 패키지). 실행·불변식은 `rag_proto/CLAUDE.md`, 통합 절차는 `rag_proto/TEAM_INTEGRATION.md` 참조.

| 팀 폴더 | rag_proto 대응 |
|---|---|
| chunking/ | `src/rag_proto/s1_convert.py`, `s2_chunk.py` |
| indexing/ | `src/rag_proto/s3_embed.py`, `s4_index.py` |
| retrieval/ | `src/rag_proto/s5_retrieve.py` — System B 가 재사용하는 `Retriever` 클래스 |
| (생성) | `src/rag_proto/s6_generate.py`, `ask.py` |
| (평가 원자료) | `src/rag_proto/run_eval.py` → `runs/<ts>_<config_hash>/answers.jsonl` |

입력: `corpus/processed/documents.jsonl` (CORPUS_V1.md §15). 저장소를 직접 파싱하지 않음.
SSOT: `corpus/metadata/snapshot.json` 의 commit / snapshot_id 를 `rag_proto/configs/ssot.yaml` 에 복사.
