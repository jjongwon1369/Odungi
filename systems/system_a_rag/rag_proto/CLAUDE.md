# rag_proto — System A (단일 RAG) 컨텍스트

종합설계프로젝트 1 · 오둥이조 · Matter/connectedhomeip 기술문서 지식베이스
팀 저장소 `Odungi` 의 `systems/system_a_rag/` 에 위치한다.

## 무엇을 하는 프로젝트인가

동일한 코퍼스·질문·LLM으로 세 시스템을 비교한다.

| 시스템 | 내용 | 담당 | 비고 |
|---|---|---|---|
| **A** 단일 RAG | 청킹 → 색인 → Top-k 검색 → 답변 | 김태이 | **이 패키지** |
| **B** 분해형 RAG | 질문을 2~5개로 분해 → **A의 검색 재사용** → 근거 병합 | — | `Retriever` 클래스가 공용 부품 |
| **C** LLM Wiki | 원본 → 구조화 Markdown 위키 → 전체 컨텍스트 주입 | 정채희 | `list_pages` / `read_page` |

`query_mode: decomposed` 와 `--decompose` 자리는 System B 의 몫이다. A 는 검색기를 노출만 한다.

베이스라인은 arXiv 2605.18490 "Vector RAG vs LLM-Compiled Wiki". 같은 구조를
학술 논문 대신 **기술 규격 문서 도메인**에 적용하는 것이 이 연구의 차별점이다.

**이번 프로토타입의 목표는 검색 품질이 아니다.** 질의 1개가 6단계를 관통해
근거 인용이 달린 답변 JSON으로 나오는 것, 그리고 코퍼스가 교체돼도 아무것도
다시 짜지 않아도 되도록 스키마를 동결하는 것 두 가지다.

## 절대 깨면 안 되는 불변식 4개

이걸 어기면 실험 전체가 무효가 된다. 코드를 고칠 때 반드시 확인할 것.

### 1. 식별자 무손실

`OnOff`, `TemperatureSetpoint`, `0x0056` 같은 식별자는 어느 단계에서도
표기가 변형되거나 사라지면 안 된다.

- `s2_chunk.verify_identifiers()`가 문서별로 검증한다. 반환이 빈 dict여야 통과.
- **길이 필터가 식별자를 삼킨 버그가 실제로 있었다.** 초단문 제거 조건에
  "식별자가 없을 때만"을 반드시 유지할 것.
- 문단이 512토큰을 넘어도 문장 중간을 자르지 않는다. 식별자가 쪼개질 위험이
  토큰 상한보다 중요하다.
- 코드 블록(` ``` `)은 토큰 수와 무관하게 절대 분할하지 않는다.

### 2. 토큰은 4열로 기록한다

`TokenUsage`의 `uncached_input` / `cache_creation` / `cache_read` / `output`을
**절대 합산 필드로 바꾸지 말 것.**

베이스라인 논문이 위키 ingest 토큰을 한 필드에 뭉쳐 기록한 탓에 비용 가설의
절반을 판정하지 못했다. 캐시 읽기는 기본 입력 요율의 약 10%로 과금되므로
액면 합산은 청구액을 자릿수 단위로 과대 계상한다. 논문이 복제 연구자에게
남긴 방법론 노트가 이 4열 기록이다.

환산이 필요하면 `TokenUsage.billable_equivalent()`를 쓰고 원자료는 보존한다.

### 3. 경로는 corpus.yaml에만 존재한다

코드에 파일 경로나 디렉토리 패턴을 하드코딩하지 않는다. Phase 2에서 코퍼스를
교체할 때 `corpus.yaml` 한 곳만 고치면 되어야 한다.

### 4. 답변 JSON 스키마는 RAG와 위키 공용

`AnswerRecord`는 System B도 그대로 쓴다. 필드 추가·삭제는 팀 합의 사항.
`retrieved` 블록만 시스템별로 내용이 달라진다(위키는 `wiki_pages` 사용).

## 확정된 결정 사항

| 항목 | 값 | 비고 |
|---|---|---|
| **코퍼스 입력** | 팀 `corpus/processed/documents.jsonl` | CORPUS_V1.md §15. 저장소 클론·파싱 금지 |
| **SSOT** | `1ac132b5ecd42cb6c78772f2576ed6f7fc814183` (포크 DS-J-L, master 관찰) | `corpus/metadata/snapshot.json` |
| Data Model | `data_model/1.7` 개발 스냅샷 | 배포 사양 아님. spec_tag `0.9-1.7-winter2027` |
| 코퍼스 버전 | v0.1 (v1.0 candidate), snapshot_id 기록 | `frozen: false` — 라이선스·교차검토 미완 |
| 범위 | 3제품군 / 4 Device Type / 23 Cluster | 범위 변경은 코퍼스 담당자에게 요청 |
| Phase | `integrated` | 개인 샘플(b9c05ca0, 1.4.2)은 폐기 |
| 청킹 | 512토큰 / 중첩 50 | 베이스라인 논문과 동일 |
| 검색 | BM25 50 + 벡터 50 → RRF → 재순위 top-5 | top-5도 논문과 동일 |
| 임베딩 | `BAAI/bge-m3` | dense만 사용. 희소는 BM25 담당 |
| 재순위 | `BAAI/bge-reranker-v2-m3` | 논문은 Cohere. 재순위기만 교체로 명시 |
| 생성 LLM | **미정** | RAG와 위키가 반드시 동일 모델 |

**코퍼스 확장 계획**: Device Type 3개 → 6개 → 12개로 비교군을 만든다. 같은 commit에서
갈라지므로 `corpus_snapshot` 과 `corpus_version` 을 청크·답변 JSON 에 함께 기록한다.
commit 만으로는 어느 코퍼스로 낸 수치인지 구분할 수 없다.

**개인 샘플 시기(1.4.2) 수치는 논문에 인용하지 않는다.** 질의셋 gold answer 도 1.4.2 XML
기준으로 작성됐으므로, 1.7 코퍼스를 받으면 `check_queries` 를 다시 돌려 확인한다. 개인별 코퍼스가 다르므로 비교가
성립하지 않는다. 파이프라인 동작 확인용이다.

## 구조

```
configs/ssot.yaml       커밋 SHA, phase, owner
configs/corpus.yaml     수집 경로 패턴 (경로는 여기에만)
configs/pipeline.yaml   하이퍼파라미터. 해시가 config_hash가 된다
src/rag_proto/
  schema.py             데이터 계약 (동결 대상)
  config.py             설정 로더 + 검증 CLI
  s1_convert.py ~ s6_generate.py   수행계획서 6단계와 1:1 대응
```

파일명 `s1`~`s6`은 발표 슬라이드 p.13–18의 6단계 번호와 같다.

## 실행

```bash
python -m rag_proto.config              # 설정 검증. 먼저 통과시킬 것
python -m rag_proto.s1_convert
python -m rag_proto.s2_chunk
python -m rag_proto.s3_embed            # --fake 로 모델 없이 배관만 확인 가능
python -m rag_proto.s4_index            # --reset 으로 컬렉션 재생성
python -m rag_proto.s5_retrieve "질문"
```

## 확인된 API 규약

작성 시점에 공식 문서로 검증했다. 버전이 올라 깨지면 여기를 갱신할 것.

```python
# BGE-m3 — encode()는 dict를 돌려준다
from FlagEmbedding import BGEM3FlagModel
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
vecs = model.encode(texts, batch_size=12, max_length=8192)['dense_vecs']

# 재순위 — 쌍이 하나면 float, 여럿이면 list. normalize=True로 0~1 매핑
from FlagEmbedding import FlagReranker
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
scores = reranker.compute_score([[q, p1], [q, p2]], normalize=True)

# Chroma
col = client.get_or_create_collection(name=..., metadata={"hnsw:space": "cosine"})
col.query(query_embeddings=[[...]], n_results=k,
          include=["metadatas", "documents", "distances"])
```

## 알려진 함정

- **팀 코퍼스의 `text` 는 완전한 XML 문서가 아닐 수 있다.** "선택된 원문 발췌"라
  루트 엘리먼트가 없거나 최상위 엘리먼트가 여러 개 이어진다 (processed/README.md).
  `split_xml_segments` 가 `<_excerpt>` 로 감싸 재시도하고, 그래도 실패하면 문단 분할로
  떨어진다. 발췌엔 클러스터명이 없어 메타데이터의 `cluster` 를 경로 앞에 붙인다.
- **`document_id` 는 `doc:<sha256>` 형태다.** 콜론과 64자 해시가 chunk_id 에 들어가면
  `[chunk_id]` 인용 파싱과 가독성이 나빠져 경로 기반 id 를 쓴다. 원본 id 는 source_path 로
  역추적 가능하다.
- **`device_types` / `clusters` 는 hex ID 다.** `scope.json` 의 products / clusters 로
  이름을 매핑한다. scope.json 이 없으면 hex 그대로 남는다.

- **`data_model/` 아래에 버전이 5개 있다.** `1.3`, `1.4`, `1.4.1`, `1.4.2`, `master`.
  하나만 골라야 한다(`corpus.yaml`의 `data_model_version`). 전부 넣으면 같은
  클러스터가 5번 색인되어 검색 top-5가 거의 동일한 청크로 채워진다.
- **모든 Data Model XML은 CSA 저작권 고지 50줄로 시작한다.** 제거하지 않으면
  전 청크가 같은 법률 문구로 채워져 BM25와 벡터 검색이 모두 무의미해진다.
  `s1_convert.strip_xml_boilerplate()`가 처리한다.
- **C++ 파일도 앞머리에 아파치 라이선스 헤더가 붙어 있다.** XML의 CSA 고지와
  같은 문제로, 제거하지 않으면 청크 수십 개가 순수 법률 문구가 되어 검색
  후보를 오염시킨다. `s1_convert.strip_code_license()`가 처리하며,
  Copyright / Licensed under / SPDX-License 가 있을 때만 지운다.
- **클러스터 파일명은 이름에서 유추할 수 없다.** "Refrigerator And Temperature
  Controlled Cabinet Mode" → `Mode_Refrigerator.xml`. 파일명이 아니라 루트
  엘리먼트의 `id` 속성으로 매칭할 것.
- **`SPECIFICATION_VERSION` 파일은 신뢰하지 말 것.** master를 포함한 모든
  브랜치에서 `1.2.0`으로 방치되어 있다. 스펙 버전은 브랜치명과
  `data_model/<version>/` 디렉토리로 판단한다.
- **`docs/`만으로는 코퍼스가 성립하지 않는다.** 칩 벤더 빌드 가이드뿐이라
  Device Type이나 Cluster 속성에 대한 질문에 답할 자료가 없다. 실제로
  리랭커가 전 후보에 0.001점을 준 적이 있다. 코퍼스의 본체는 `data_model/`이다.
- **Chroma 메타데이터는 스칼라만 받는다.** str/int/float/bool 뿐이다. 우리
  스키마의 `device_type`, `heading_path`, `identifiers`는 리스트라 그대로
  넣으면 터진다. `s4_index.flatten_metadata()`가 `|` 구분자로 이어붙인다.
- **컬렉션 차원은 첫 add에서 고정된다.** 임베딩 모델을 바꾸면
  `--reset`으로 컬렉션을 지우고 다시 만들어야 한다.
- **CPU에서 `use_fp16=True`는 오히려 느리거나 미지원이다.** `device: cpu`면 끈다.
- **리랭커가 접두사 공유 식별자에서 오판한다.** `bge-reranker-v2-m3`가 질의어를
  부분 문자열로 포함한 더 긴 식별자를 정확 일치보다 높게 평가한다. 실측: 질의
  `TemperatureSetpoint`에 대해 `TemperatureSetpointHoldDuration`을 1위로 올렸고,
  BM25·벡터·융합이 모두 1위로 올린 정답을 top-5 밖으로 밀어냈다(한국어 질의).
  영어 질의에서는 2위까지 회복. Matter 식별자는 접두사 공유가 흔하므로
  (`Occupied`/`Unoccupied`, `Min`/`AbsMin`) 구조적 약점이다.
  → 리랭커 ablation 조건을 실험에 포함할 것. Q-07, Q-10이 해당 사례.
- **OpenAI와 Anthropic은 토큰 의미가 반대다.** OpenAI `prompt_tokens`는 캐시된
  토큰을 포함하고, Anthropic `input_tokens`는 제외한다. 그대로 옮겨 담으면
  캐시 적중분이 이중 계산된다.

## 미해결 사항

- 생성 LLM 미정 (`pipeline.yaml`의 `TODO_MODEL_ID`)
- S6 미구현
- 질의셋 20문항 미작성 — 반드시 `must_include_keywords` 영역 안에서 만들 것.
  그래야 Phase 2 교체 후에도 대상 문서가 살아남는다.
- Decomposition-Retrieval은 `query_mode` 필드만 있고 미구현
