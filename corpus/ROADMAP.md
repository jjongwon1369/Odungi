## Future Work: Corpus Scale Experiment

현재 Corpus v1.0은 3개 제품군을 대상으로 하는
기본 비교 실험용 Corpus로 구성한다.

후속 실험에서는 동일한 SSOT, Metadata Schema,
Normalization 및 Validation 규칙을 유지하면서
제품군 수를 단계적으로 확장한다.

### Corpus Tiers

- C3: 3 Product Families
- C6: 6 Product Families
- C12: 12 Product Families

각 Corpus는 이전 단계의 Superset으로 구성한다.

C3 ⊂ C6 ⊂ C12

이를 통해 Corpus 규모 증가가
RAG와 LLM Wiki의 성능에 미치는 영향을 비교한다.

### 주요 비교 지표

- Answer Accuracy
- Groundedness
- Hallucination Rate
- Identifier Accuracy
- Retrieval Performance
- Response Latency
- Query Token Usage
- Ingestion / Compilation Cost

제품군 수뿐 아니라 각 Corpus의

- Documents
- Relations
- Clusters
- Raw Size
- Token Count

를 함께 기록하여 실제 정보량 증가와 성능 변화를 분석한다.