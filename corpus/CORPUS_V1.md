# Matter / connectedhomeip Corpus v1.0 Candidate

상태: **candidate — 공식 v1.0으로 freeze되지 않음**

현재 Corpus 버전: **0.1**

Freeze gate: **blocked** (`ready_for_freeze=false`)

## 1. Corpus 개요

이 Corpus는 Matter `connectedhomeip`의 제품·Device Type·Cluster 정의와 관련 SDK 정의,
구현, 문서, 예제를 하나의 고정된 공통 입력으로 제공한다. 단일 RAG, 분해형 RAG, LLM Wiki가
각자 다른 자료를 수집해 비교 조건이 흔들리지 않게 하기 위한 것이다.

핵심 원칙은 **동일한 원본을 고정하고 처리 방식만 다르게 한다**는 것이다. Corpus는 공통 입력이고,
chunking·embedding·retrieval·Wiki compilation은 각 시스템의 downstream 처리다.

## 2. SSOT

- Source repository: `connectedhomeip`
- Observed branch: `master`
- Commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- Specification baseline: `data_model/1.7` 개발 snapshot
- Snapshot ID: `corpus-v0.1:ee88b47ac7a901be55e52cb8039314b740d312dbff6982eec65bc3af6a735680`

branch 이름은 움직일 수 있으므로 재현 기준은 commit SHA다. raw는 checkout의 개행 변환 결과가 아니라
고정 commit의 Git blob byte에서 생성한다. 이 개발 snapshot을 안정 배포 사양으로 간주하지 않는다.

## 3. Corpus 범위

| 제품군 | Device Type | ID | 제품군 내 역할 |
|---|---|---:|---|
| Laundry Washer | Laundry Washer | `0x0073` | 직접 대상 |
| Room Air Conditioner | Room Air Conditioner | `0x0072` | 직접 대상 |
| Refrigerator | Refrigerator | `0x0070` | 직접 대상 |
| Refrigerator | Temperature Controlled Cabinet | `0x0071` | Cooler-only 보조 범위 |

제품군은 3개, Device Type ID는 4개, 전체 고유 Cluster는 23개다. Refrigerator는 사양·SDK·예제에서
Temperature Controlled Cabinet과 구성 관계를 가지므로 Cabinet을 1-hop 보조 범위로 포함했다.
Heater-only Cabinet 기능은 포함하지 않는다.

## 4. Scope 선정 과정

초기 후보 조사에서 Device Type, Cluster, specification, SDK definition, documentation,
implementation과 example 경로를 실제 고정 checkout에서 확인했다. 직접 required/optional/conditional/
provisional Cluster를 포함하고, 명시된 Base와 Cluster base만 제한적으로 따라갔다. related Device Type은
Cabinet만 1-hop 확장했다. 공유 component의 직접 CPP/H, 허용한 delegate와 framework entry point만 포함하고
third_party, build output, 광범위한 생성 client code, 테스트 본문과 무관한 예제는 제외했다.

확정 기준은 `metadata/scope.json`, 감사 뷰는 `metadata/coverage_matrix.csv`다. Refrigerator와 Cabinet의
관계, 탐색 종료 규칙과 제외 사유는 `corpus_scope.md`에 기록되어 있다.

## 5. Corpus Source 유형

| source_role | 파일 수 | 의미 |
|---|---:|---|
| specification | 34 | `data_model/1.7`의 사양 모델 정의 |
| sdk_codegen | 23 | SDK/code-generation용 XML 정의 |
| implementation | 185 | Cluster·framework 구현 |
| documentation | 17 | 저장소 내 Markdown 설명 |
| example | 20 | 제품/endpoint 구성과 delegate 예제 |
| generated_definition | 3 | 제한된 생성 revision 선언 |

`source_role`은 출처의 역할, `definition_kind`는 device type/cluster/base/framework 등 정의 대상,
`source_revision`은 해당 출처의 artifact와 선언 revision을 나타낸다. Specification XML과 SDK Codegen
XML은 경로·생성 목적·revision 축이 다르므로 같은 자료로 합치지 않는다. 비슷한 내용이어도 서로 다른
주장을 제공하는 출처는 별도 문서와 relation으로 보존한다.

## 6. 관계 모델

Corpus는 단순 파일 모음이 아니다. Device Type → Cluster 요구, Device Type → Base 상속,
Refrigerator → Cabinet 구성 조건, Cluster → specification/SDK 정의, Cluster → 구현,
예제 endpoint 구성, 구현 → 생성 revision 근거를 relation으로 보존한다.

공유 구현은 제품별로 복사하지 않는다. 물리 파일 하나에 안정된 `document_id` 하나를 부여하고,
여러 Device Type/Cluster가 각각의 relation과 `via_entities`로 같은 문서를 가리킨다. 따라서 파일 수와
제품별 관련 파일 수는 합산 기준이 다르다. condition, requirement, assertion scope와 evidence를 함께
읽어야 하며 optional을 enabled로 바꾸어 해석하지 않는다.

## 7. 최종 Corpus 규모

| 항목 | 수 |
|---|---:|
| Raw files | 282 |
| Normalized documents | 282 |
| Relations | 764 |
| Entities | 342 |
| Unique clusters | 23 |

| Device Type | 관련 파일 수 |
|---|---:|
| Laundry Washer (`0x0073`) | 113 |
| Room Air Conditioner (`0x0072`) | 209 |
| Refrigerator (`0x0070`) | 99 |
| Temperature Controlled Cabinet (`0x0071`) | 81 |

제품별 수는 공유 문서를 중복 연결하므로 합계가 282보다 크다. 전체 282는 고유 physical source path 수다.

## 8. Coverage

| 상태 | 수 |
|---|---:|
| present | 38 |
| missing | 21 |
| not_applicable | 32 |
| unverified | 0 |

missing 21개는 `documentation_missing` 20개와 `unavailable_source` 1개다. 전자는 지정된 component
경로에 독립 Markdown 문서가 없다는 뜻이고, 후자는 Temperature Alarm의 concrete SDK/implementation/IDL
자료가 고정 snapshot에서 확인되지 않았다는 뜻이다. raw 또는 normalized 추출 실패가 아니며, 없는 자료를
만들거나 다른 자료로 대체하지 않았다.

## 9. Metadata

`processed/documents.jsonl`의 핵심 필드는 다음과 같다.

- `document_id`: source ID와 상대 경로에서 만든 안정 식별자
- `source_path`: connectedhomeip 기준 POSIX 경로
- `commit_hash`: 원본을 고정한 commit
- `source_role`: specification, sdk_codegen, implementation 등 출처 역할
- `definition_kind`: 정의 대상의 종류
- `source_revision`: artifact와 출처별 entity revision/locator
- `device_types`, `clusters`: 범위 관련성 요약
- `content_hash`: 원본 byte의 SHA-256
- `normalized_hash`: 정규화 UTF-8 text의 SHA-256
- `source_spans`: 정규화 본문을 원본 위치로 되짚는 offset·line·locator

이 필드들은 문서가 어디서 왔는지, 어떤 snapshot과 entity에 속하는지, 원본이 바뀌지 않았는지,
정규화 본문을 어느 원문 구간으로 역추적할지를 제공한다.

## 10. Normalization

raw는 Git blob의 원본 byte를 그대로 보존한다. 공통 normalization은 UTF-8 strict decoding(BOM 제거),
CRLF/CR→LF, 확정 scope의 원문 구간 선택, provenance 위치 매핑으로 제한한다. identifier, 조건, 표와
코드 표현을 요약하거나 재작성하지 않는다.

RAG chunking, embedding, Wiki compilation, LLM summarization, benchmark 기반 선택은 normalization에
포함하지 않는다. XML/IDL/ZAP 발췌는 완전한 standalone 문서가 아닐 수 있으며 완전 원문은 raw를 사용한다.

## 11. Validation

2026-09-22 현재 실제 재실행 결과다.

| Validation | Result |
|---|---|
| SSOT commit / clean checkout | PASS |
| Raw ↔ Manifest (282/282) | PASS |
| Raw SHA-256 | PASS |
| Normalized documents / source spans | PASS (282 / 755) |
| Duplicate document/relation ID | PASS |
| Identifier preservation | PASS (191,531 occurrences) |
| Provenance / relation target | PASS (764 relations) |
| Cluster coverage | PASS (23/23) |
| Extraction missing | PASS (0) |
| Out-of-scope output | PASS (0) |
| Deterministic rebuild | PASS (2 builds, 288 files) |
| Unit tests | PASS (13/13) |
| Validation failure | 0 |

기계 검증은 14 PASS / 3 warning이다. warning은 허용된 coverage gap, 출처 간 revision 의미 정합성
미평가, tokenizer/model 미결정이다. 데이터 무결성 실패가 아니다. 단, 기술 검증 통과는 라이선스나
팀 승인 통과를 대신하지 않는다.

## 12. 재현 방법

Python 3.10+, Git, 고정 commit의 clean `../connectedhomeip` checkout을 준비하고 프로젝트 루트에서 실행한다.

```powershell
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --dry-run
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --validate-only
python -m unittest discover -s scripts/corpus/tests -v
```

전체 생성은 알려진 산출물만 교체하고, scope 밖 파일이 output에 있거나 source가 dirty/다른 commit이면
실패한다. 세부 CLI 계약은 `scripts/corpus/README.md`를 따른다.

## 13. Directory Structure

```text
corpus/
├── raw/connectedhomeip/          # 원본 Git blob
├── processed/documents.jsonl     # 공통 정규화 입력
├── metadata/
│   ├── scope.json
│   ├── coverage_matrix.csv
│   ├── corpus_manifest.csv
│   ├── entities.jsonl
│   ├── relations.jsonl
│   ├── snapshot.json
│   ├── statistics.json
│   ├── validation_report.json
│   └── freeze_gate.json
├── research/                     # 조사·검토 근거
├── README.md
├── CORPUS_V1.md
├── DATASET_CARD.md
├── CHANGELOG.md
├── HANDOFF.md
└── PUBLISHING.md
scripts/corpus/                   # 추출·정규화·검증 코드와 테스트
```

## 14. 책임 범위

Corpus 담당자가 보장하는 것:

- 동일한 source snapshot과 확정 scope
- 문서별 provenance와 metadata
- raw integrity와 identifier 보존
- source span을 통한 원문 역추적
- 결정적 재생성

Corpus 담당자가 보장하지 않는 것:

- RAG chunking·embedding·retrieval 성능
- Wiki compilation 설계와 context 적합성
- LLM 답변 정확도
- specification/implementation의 의미적 일치나 실행 동작
- benchmark 결과 또는 Gold Answer 품질

## 15. 후속 사용

RAG 담당자는 `documents.jsonl`을 chunking → embedding → indexing → retrieval의 공통 입력으로 사용한다.
LLM Wiki 담당자는 같은 문서 집합을 compilation → Wiki structure → QA의 입력으로 사용한다.
`relations.jsonl`은 entity 연결과 provenance를 해석하는 보조 자료다. downstream 결과에 맞춰 Corpus를
묵시적으로 수정하지 말고, 변경이 필요하면 Corpus 담당자에게 scope/snapshot/version 검토를 요청한다.

현재 v1.0 freeze의 남은 blocker는 다음 두 가지다.

1. 31개 `reference_only`와 34개 `needs_review` source에 대한 실제 이용·변환·공유 권한 결정
2. 최소 1명의 실제 팀원이 snapshot과 audit 자료를 확인하고 남기는 교차검토 기록

두 항목이 통과하기 전에는 `version.json`, `ready_for_freeze=true`, frozen metadata, `corpus-v1.0` tag를
생성하지 않는다.
