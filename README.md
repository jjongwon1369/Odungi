# Odungi

Matter `connectedhomeip` 기술 문서를 대상으로 단일 RAG, 분해형 RAG, LLM Wiki를 비교하는 프로젝트다.
세 시스템은 동일한 고정 Corpus와 평가 질문을 사용하며, 원본이 아니라 처리 방식의 차이를 비교한다.

## Corpus 빠른 시작

현재 구현된 Corpus는 `connectedhomeip`의 고정 commit에서 raw 282개, 정규화 문서 282개,
relation 764개를 결정적으로 생성하고 검증한다. Python 3.10+와 Git만 필요하다.

두 저장소를 같은 workspace 아래에 둔다.

```text
workspace/
├── connectedhomeip/
└── project/
```

Windows PowerShell에서 project 디렉터리로 이동한 후 실행한다.

```powershell
git -C ..\connectedhomeip checkout 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
$env:CONNECTEDHOMEIP_PATH = (Resolve-Path "..\connectedhomeip").Path
python scripts/corpus/build.py
```

정상 결과는 raw 282개, normalized document 282개, relation 764개, 고유 cluster 23개,
validation failure 0개다. 입력 checkout은 clean 상태여야 하며 빌드 과정에서 수정되지 않는다.
상세 사용법과 데이터 계약은 [Corpus README](corpus/README.md), 실행 CLI와 실패 조건은
[Corpus pipeline README](scripts/corpus/README.md)를 참고한다.

## Corpus 확장 로드맵

현재 3개 제품군 Corpus를 C3 기준선으로 사용하고, 동일한 SSOT·metadata schema·정규화·검증 규칙을
유지하며 C6, C12로 단계적으로 확장한다. 각 단계는 이전 단계의 superset이다.

```text
C3 (3 product families) ⊂ C6 (6) ⊂ C12 (12)
```

확장 실험에서는 answer accuracy, groundedness, hallucination rate, identifier accuracy, retrieval 성능,
응답 지연, query token 사용량, ingestion/compilation 비용을 비교한다. Documents, relations, clusters,
raw size, token count도 함께 기록해 단순 제품군 수가 아닌 실제 정보량 증가의 영향을 분석한다.
세부 계획은 [Corpus ROADMAP](corpus/ROADMAP.md)에 있다.


## 프로젝트 폴더 구조

Matter / connectedhomeip의 동일 코퍼스·질문·LLM으로 단일 RAG(A), 분해형 RAG(B), LLM Wiki(C)를 비교한다.
Corpus 생성·검증 파이프라인은 구현되어 있으며, downstream 시스템과 전체 비교 실험은 단계적으로 진행한다.
각 폴더의 README에 역할과 계약을 기록한다.

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
│   └── system_c_llm_wiki/             # C: 위키 전체 정적 context 주입
│       ├── compiler/                  # 원본 → 구조화 Markdown
│       ├── wiki/                      # 컴파일된 위키
│       │   ├── cluster/               # Cluster·Attribute·Command
│       │   ├── device_type/           # Device Type과 Cluster 관계
│       │   ├── commissioning/         # Commissioning 절차
│       │   └── implementation/        # 스펙과 구현 연결
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
├── scripts/                           # Corpus 생성·검증 등 실행 스크립트
├── meetings/                          # 기존 회의록
├── RAG/                               # 기존 폴더 유지
└── LLM Wiki/                          # 기존 폴더 유지
```

Corpus의 `snapshot.json`과 관련 metadata는 현재 생성되어 있다. Benchmark의 `questions.json`,
`gold_labels.json` 등은 해당 단계에서 확정한다. System B는 A의 검색을 재사용하며, 기본 System C는
검색 없이 위키 전체를 주입한다. Corpus/Data, RAG(A/B), LLM Wiki(C), Evaluation을 각각 담당 영역으로 나눈다.
