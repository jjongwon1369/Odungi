# System B — 분해형 RAG (Decomposition RAG)

질문 1개를 하위 질의 2~5개로 분해한 뒤, **System A(`systems/system_a_rag/rag_proto`)의
검색기를 그대로 재사용**해 하위질의마다 검색하고 근거를 병합한다. 별도 청킹·색인은
만들지 않는다 — A가 만든 `data/chroma`, `data/chunks.jsonl`을 그대로 쓴다.

| 팀 폴더 | 구현 |
|---|---|
| `decomposition/` | `decompose.py` — 질문 → 하위질의 2~5개. `FakeDecomposer`(배관 확인용, API 키 없을 때) / `LLMDecomposer`(실제 분해) |
| `pipeline/` | `ask_decomposed.py` — 하위질의별 검색 → `merge_candidates()`로 병합 → 생성. `AnswerRecord`는 System A와 **완전히 같은 스키마**, `query_mode: "decomposed"`로만 구분 |
| `pipeline/` | `run_batch_decomposed.py` — 본실험 배치(참가자 LLM × 반복 × 문항). System A의 배치 러너를 그대로 쓰고 파이프라인만 교체 |

토큰은 **분해 호출 + 생성 호출**을 열별로 더해 기록한다(분해도 참가자 LLM 비용이다).
분해 LLM은 생성과 같은 참가자 LLM을 쓴다.

## 실행

`system_a_rag/rag_proto`와 같은 가상환경(FlagEmbedding, chromadb 등)이 필요하고,
그 저장소의 `data/`(색인 결과)가 이미 있는 위치에서 실행해야 한다.

```bash
cd systems/system_a_rag/rag_proto && source .venv/bin/activate
python ../../system_b_decomposition_rag/pipeline/ask_decomposed.py "질문"
python ../../system_b_decomposition_rag/pipeline/ask_decomposed.py "질문" --fake-llm   # 검색은 실제, 분해·생성만 가짜

# 본실험 (인자는 System A의 run_eval 배치와 동일)
python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py --smoke
python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py \
    --participants all --runs 3 --questions ../../../benchmark/questions_v1.jsonl
```

## 병합 규칙

같은 `chunk_id`가 여러 하위질의에서 나오면 점수를 **합산하지 않고 최댓값만** 취한다.
합산하면 하위질의 개수가 많을수록 같은 청크가 유리해져 실제 관련성과 무관하게
점수가 부풀려지기 때문이다. 병합 후 점수 내림차순으로 `rerank_top_k`개만 남긴다.

## 검증

- 하위질의 1개(FakeDecomposer)로 실행 시 System A의 단일 질의 결과와 **완전히 동일** —
  회귀 확인용으로 쓸 수 있다.
- 하위질의 2개(스텁 LLM)로 실행 시 `bm25`/`vector`가 각 50건씩 정확히 2배(100건)로
  나오고, `merge_candidates()`가 중복 제거 후 점수순 top-k를 올바르게 뽑는 것을 확인.

## 미해결

- 실제 LLM으로 분해하는 `LLMDecomposer`는 코드는 있으나 API 키 대기 중이라 아직
  실호출 검증 전 (System A의 S6와 동일한 사유).
