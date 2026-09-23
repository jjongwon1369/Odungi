# -
A comparative study of RAG and LLM-based knowledge systems for Matter (connectedhomeip) technical documentation.


## 프로젝트 폴더 구조

Matter / connectedhomeip의 동일 코퍼스·질문·LLM으로 단일 RAG(A), 분해형 RAG(B), LLM Wiki(C)를 비교합니다.
현재는 폴더와 역할 설명만 준비한 상태이며, 구현 코드와 실험 데이터는 없습니다.
각 폴더의 README.md에 역할을 적었습니다.

```text
Odungi/
├── prereg/                            # 사전 가설·벤치마크 설계·평가 규칙
├── corpus/                            # 특정 commit으로 고정한 공통 SSOT
│   ├── raw/                           # 원본 문서·IDL·JSON·C++
│   ├── processed/                     # 공통 추출·정규화 자료
│   └── metadata/                      # 출처·commit·문서 유형·토큰 수
├── benchmark/                         # 공통 질문 및 정답 근거
├── systems/
│   ├── system_a_rag/                  # A: 단일 RAG
│   │   ├── chunking/                  # 문서 유형별 청킹
│   │   ├── indexing/                  # 임베딩·벡터 색인
│   │   └── retrieval/                 # A/B 공통 Top-k 검색
│   ├── system_b_decomposition_rag/    # B: 분해형 RAG
│   │   ├── decomposition/             # 질문을 2~5개로 분해
│   │   └── pipeline/                  # A 검색 반복·근거 병합·답변 생성
│   └── system_c_llm_wiki/             # C: 사전 컴파일 위키 + 에이전트 페이지 탐색
│       ├── compiler/                  # 원본 → 구조화 Markdown
│       ├── wiki/                      # 컴파일된 위키 (엔티티당 1페이지)
│       │   ├── base/                  # 공유 베이스 클러스터
│       │   ├── clusters/              # Cluster·Attribute·Command
│       │   ├── device-types/          # Device Type과 Cluster 관계
│       │   └── examples/ guides/ misc/
│       └── validation/                # 출처·식별자·context 크기 검증
├── evaluation/
│   ├── judges/                        # 블라인드 품질 평가 4개 축
│   ├── grounding/                     # 주장별 인용 근거 검증
│   ├── statistics/                    # 시스템·질문 유형별 비교 분석
│   └── cost/                          # 구축·추론·갱신 비용
├── results/
│   ├── raw/                           # 원시 답변·인용·로그
│   ├── judged/                        # 평가·근거 판정 결과
│   └── analyzed/                      # 분석 결과·표·그래프
├── scripts/                           # 향후 실행 보조 스크립트
├── meetings/                          # 기존 회의록
├── RAG/                               # 기존 폴더 유지
└── LLM Wiki/                          # 기존 폴더 유지
```

`snapshot.json`, `questions.json`, `gold_labels.json` 등은 실제 데이터 준비 시 작성합니다.
System B는 A의 검색을 재사용하며, 기본 System C는 검색 없이 위키 전체를 주입합니다.
Corpus/Data, RAG(A/B), LLM Wiki(C), Evaluation을 각각 담당 영역으로 나눌 수 있습니다.
