# Corpus Construction Plan

## 1. 목적과 현재 단계

Matter / connectedhomeip의 동일 원본을 사용하여 A(단일 RAG), B(분해형 RAG), C(LLM Wiki)를 비교한다.
B는 A의 검색을 재사용하고 C는 컴파일 Wiki 전체를 정적 Context로 제공하는 실험을 기본으로 한다.

**현재 상태: Corpus Scope Finalization 완료(scope-v1.0), Corpus 추출·전처리·v1.0 Freeze 미실행.**
이번 단계는 범위와 Metadata 계약만 확정한다. 추출 Script 작성과 실행은 다음 단계다.
connectedhomeip는 계속 읽기 전용이며 현재 프로젝트만 수정한다.

범위의 실행 기준은 [corpus_scope.md](corpus_scope.md)와 [metadata/scope.json](metadata/scope.json)이다.
[metadata/coverage_matrix.csv](metadata/coverage_matrix.csv)는 출처별 관계 및 결손의 검토용 뷰다.
기술 계약은 [source_taxonomy.md](research/source_taxonomy.md), [relation_model.md](research/relation_model.md),
[revision_analysis.md](research/revision_analysis.md)에 정의한다.
이전 Discovery 문서는 당시 조사 기록으로 보존하며 현재 범위 확정은 위 문서가 우선한다.

    고정된 Source Snapshot
    └── Core Corpus
        ├── raw: 원본 바이트
        ├── processed: A/B/C 공통 추출·정규화 자료
        └── metadata: 출처·Revision·Entity·Relation·Coverage
            ├── A/B 전처리 → 청크·임베딩·색인
            └── C 전처리 → Markdown Wiki

관계 Metadata는 provenance와 Coverage를 표현한다. 평가 정답·LLM 추론 결과·시스템별 가공 지식이 아니다.

## 2. 고정 Source와 최종 Device Type 범위

- Repository: connectedhomeip, 관찰 branch master.
- Commit: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183.
- 사양 모델 baseline: data_model/1.7.
- 원본 spec SHA: 214e40c9d51cfe89050eae68ca5b76238fcfa332.
- 원본 spec tag: 0.9-1.7-winter2027.
- SDK/codegen baseline: 같은 Commit의 src/app/zap-templates/zcl/data-model/chip.

외부 공식 사양 원문을 확인한 결과나 정식 배포판으로 취급하지 않는다.
Source별 선언과 Revision은 병합하지 않는다.

| 제품군 / Device Type | ID | 포함 직접 Cluster | Base 포함 고유 Cluster |
|---|---|---:|---:|
| Laundry Washer | 0x0073 | 6 | 10 |
| Room Air Conditioner | 0x0072 | 12 | 16 |
| Refrigerator | 0x0070 | 4 | 8 |
| Temperature Controlled Cabinet, 냉장고 보조 범위 | 0x0071 | 4 | 8 |
| 냉장고 제품군 합집합 | 0x0070 + 0x0071 | 7 | 11 |

3개 제품군, 4개 공식 Device Type ID, 전체 고유 Cluster 23개를 포함한다.
Base 지원 정의와 숫자 ID 없는 Cluster base는 이 고유 Cluster 수에 추가하지 않는다.
Air Purifier/Dishwasher/Laundry Dryer는 현재 scope에서 제외한다.

## 3. 관계 중심 Corpus 구성

    Device Type
    ├── Base / inherited requirements
    ├── Endpoint scope / composition requirements
    ├── Required / Optional / Conditional / Provisional Clusters
    ├── Related / composed Device Types
    ├── Specification definitions
    ├── SDK / code-generation definitions
    └── Shared / device-specific implementations
          └── 명시된 Cluster base / delegate / entry point까지만 연결

Required와 실제 enabled는 다르며 Optional 선언도 Corpus 대상이다.
추상 endpoint 요구와 특정 예제의 endpoint 번호·부모 관계도 구분한다.

Refrigerator는 독립 Device Type만으로 범위를 끝내지 않는다.

- 사양 Refrigerator.xml:68–71은 Temperature Controlled Cabinet의 Cooler 조건을 요구한다.
- SDK matter-devices.xml:3055–3060은 tree와 최소 1개 Cabinet endpoint를 선언한다.
- Chef ZAP은 냉장고 endpoint 1 → Cabinet 2/3 관계를 기록한다.
- 전용 냉장고 ZAP은 부모 값이 null이므로 다른 예제 assertion으로 보존한다.
- 연구 프로필은 Cooler=true / Heater=false다. Cabinet의 Oven Mode와 Oven Cavity Operational State는 제외한다.

SDK의 cardinality를 사양 XML의 요구라고 바꿔 기록하지 않는다.
상세 관계의 authoritative 범위는 출처별로 정한다.

## 4. Source taxonomy

확장자·내용 형식과 출처 역할을 분리한다.

| 필드 | 값 / 용도 |
|---|---|
| source_role | specification, sdk_codegen, documentation, implementation, example, test, generated_definition |
| definition_kind | device_type, cluster, cluster_base, framework_contract, none |
| content_kind | xml, json, idl, markdown, implementation 등 실제 내용 형식 |
| source_revision | 원본 artifact 버전과 Entity별 선언 Revision 배열 |
| entity_bindings | 파일 안의 Entity와 그 위치 |
| implementation_scope | device_specific, cluster_shared, framework_shared, unverified |

specification XML은 data_model/1.7, SDK XML은 src/app/zap-templates/zcl/data-model/chip이다.
동일한 Data Model 출처로 분류하지 않는다. 근거: data_model/README.md:15.

device_type_definition과 cluster_definition은 두 역할 모두에 존재하므로 definition_kind에 둔다.
예제 C++는 example 역할과 implementation 내용 형식을 가진다.
test 역할은 지원하지만 이번 Core에는 테스트 본문을 포함하지 않는다.
generated_definition은 선언 Revision을 추적하는 제한된 Metadata.h만 포함한다.

## 5. 공통 문서 Metadata

다음은 향후 추출 레코드의 형식 예시다. 아직 실제 Corpus 레코드는 생성하지 않았다.

```json
{
  "document_id": "source-id:relative-path",
  "source_id": "connectedhomeip",
  "snapshot_id": "commit-and-scope-id",
  "source_path": "data_model/1.7/device_types/Refrigerator.xml",
  "source_url": "commit-pinned-permalink",
  "commit_hash": "1ac132b5ecd42cb6c78772f2576ed6f7fc814183",
  "source_role": "specification",
  "definition_kind": "device_type",
  "content_kind": "xml",
  "source_revision": {
    "artifact": {
      "scheme": "git_commit",
      "value": "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"
    },
    "model_version": "1.7",
    "declarations": [
      {
        "entity_kind": "device_type",
        "entity_id": "0x0070",
        "scheme": "device_type_revision",
        "value": "3",
        "status": "present",
        "locator": "/deviceType/@revision"
      }
    ]
  },
  "entity_bindings": [
    {"kind": "device_type", "namespace": "matter", "id": "0x0070", "locator": "/deviceType"}
  ],
  "included_reason": "selected refrigerator definition",
  "content_hash": "sha256-original-bytes",
  "normalized_hash": "sha256-common-normalized-text",
  "source_spans": []
}
```

- document_id는 Source ID+경로에서 결정하고 Snapshot을 별도로 고정한다.
- content_hash는 원본 바이트, normalized_hash는 공통 정규화 UTF-8 본문의 SHA-256이다.
- 여러 Entity/Revision을 가진 통합 파일은 declarations/entity_bindings 배열로 표현한다.
- Git Commit, model_version, Device Type Revision, ClusterRevision을 구별한다.
- C++는 Commit으로 버전을 고정한다. 생성 상수 참조는 별도 evidence로 기록하며 구현 Revision 숫자를 추측하지 않는다.
- device_types/clusters 요약 배열은 선택적으로 재생성할 수 있으나 관계의 원본은 아니다.
- 이전 doc_type은 content_kind로 대체하고 중복된 필드 의미를 유지하지 않는다.
- text 및 source_spans는 공통 입력에 저장한다. 원본 행/구조화 위치/PDF 페이지와 본문 문자 오프셋을 연결한다.
- 문자 범위는 Unicode 코드 포인트 기준 시작 포함·끝 제외다.
- 외부 문서를 이후 추가하면 URL·수집 시각·보관 경로·원본 Hash·이용 조건·버전을 별도 등록한다.
  Git Commit이 없으면 null을 허용하되 출처 고정에 필요한 필드는 생략하지 않는다.

## 6. Entity / Relation Metadata

Entity의 key는 kind+namespace+ID다. Device Type과 Cluster의 같은 숫자 ID를 혼동하지 않는다.
예제 endpoint에는 예제 경로 namespace를 붙이며 abstract endpoint_requirement와 별개로 둔다.
숫자 ID 없는 Base는 symbolic ID를 사용한다.

Relation은 source_entity, target_entity, relation_type, role, requirement, condition,
assertion_scope, source_revision, evidence, status를 가진다.
상세 타입은 relation_model.md를 따른다.

필수 관계:

- Device Type → Cluster: requires_cluster, 조건/역할 보존.
- Device Type → Base: inherits_requirements.
- Device Type → Device Type: requires_related_device_condition.
- Device Type → Endpoint requirement: requires_endpoint / requires_endpoint_scope.
- 예제 Endpoint → 예제 Endpoint: example_composes_endpoint.
- Entity → 사양/SDK 정의: defined_by_specification / defined_by_sdk.
- Cluster → 구현: implemented_by.
- 여러 Device Type → 동일 구현: uses_shared_implementation, via_entities에 Cluster 연결 보존.
- Cluster → 공통 기반 정의: derives_cluster_base.
- 구현 → 생성 Revision 근거: uses_revision_declaration.

동일 Entity 관계라도 서로 다른 출처의 주장은 따로 저장한다.
SDK assertion을 사양 assertion으로 승격하거나 예제 선택을 필수 요구로 해석하지 않는다.
조건을 판정할 정보가 없으면 원본 구조와 unverified 평가 상태를 유지한다.

## 7. Inclusion / Exclusion과 탐색 종료

정확한 Device/Cluster/path 목록은 scope.json과 coverage_matrix.csv로 고정한다.

1. 직접 required/optional/conditional/provisional Cluster를 포함한다. Cabinet Heater-only 2개는 제외한다.
2. related Device Type은 1-hop, Cabinet만 확장한다. Root는 GroupcastListenerCond 정의 문맥만 포함한다.
3. Base Device Type 4종의 선언과 구현을 포함하되 조건을 항상 참으로 가정하지 않는다.
4. Cluster base는 Mode Base/Alarm Base/Label 1-hop만 포함한다. 다른 alias나 제품으로 역탐색하지 않는다.
5. 명시한 component 루트의 직접 CPP/H를 포함하고 하위 디렉터리·외부 include는 따라가지 않는다.
6. DefaultServerCluster.h와 명시 예제 delegate는 allowlist 예외다. build/RTOS/platform 전체를 가져오지 않는다.
7. 공유 구현은 원본 파일 한 개에 여러 관계를 연결한다.
8. third_party, build output, binary, 무관한 예제, 광범위한 생성 client 코드, 테스트 본문은 제외한다.
9. 원본 통합 파일은 추후 raw에 보존하되 공통 입력은 선정 Entity와 필요한 공통 정의만 절취한다.
10. selector가 공통 정의를 안전하게 보존하지 못하면 실패로 기록한다. 임의 누락·전체 파일 fallback을 하지 않는다.

바이트 Hash가 같은 자료의 물리 중복만 자동 처리한다.
spec/SDK/example/implementation은 유사한 내용이어도 역할이 다르면 제거하지 않는다.
제외 이유와 중복 원본 출처를 기록한다.

## 8. Coverage Matrix

현재 CSV는 Discovery 74행과 신규 관계 17행, 총 91행이다.
기존 후보 제외도 삭제하지 않고 discovery_row_id/status 및 scope_decision으로 추적한다.

핵심 컬럼은 다음과 같다.

- Device Type 이름·ID·정의 경로·Revision.
- related_device_type, relation_type, relationship_origin, endpoint_requirement.
- Cluster 이름·ID, server_client_role, requirement, feature_condition.
- specification_path/revision, sdk_definition_path/revision.
- documentation_path/kind, implementation_path/scope/revision.
- idl_path/scope, example_device_revision, example_cluster_revision, example_device_server_endpoints.
- evidence_location(JSON), 항목별 status, 종합 status, resolution, notes, Commit.

status는 present/missing/not_applicable/unverified만 사용한다.
현재 집계: present 38 / missing 21 / not_applicable 32 / unverified 0.
선택 Cluster 관계 42행, 신규 provenance 관계 17행, 제외 감사 32행을 별도로 집계한다.

missing은 기록한 검색 범위 내 부재이며 저장소 전체의 부재를 뜻하지 않는다.
독립 component prose가 없는 20행과 specification-only Temperature Alarm 1행은 허용한 Coverage 결손이다.
관계 존재는 확인했지만 문서가 없으면 relation_status=present, 종합 status=missing일 수 있다.
파일 존재·관계 조사와 의미적 정합성·런타임 검증의 상태를 혼동하지 않는다.

## 9. Revision 차이 처리

사양 모델·SDK·예제·구현의 버전 축을 분리하고 차이만으로 제외하거나 오류라고 판단하지 않는다.
대표 차이는 Filter Monitoring 2/1, Relative Humidity 5/3,
냉장고/Cabinet/세탁기 Device Type의 최신 정의와 예제 version 1이다.
구체 값과 근거는 revision_analysis.md를 따른다.

Consistency 평가에서는 출처·Revision을 명시하여 차이 설명, 구현의 선언 참조 추적,
optional 미선택과 미구현의 구별을 평가할 수 있다.
자료 간 숫자 일치도 완전한 의미적 일치를 보장하지 않는다.
이번 단계에서 평가 질문·정답은 생성하지 않는다.

## 10. Repository 구조와 산출물

    corpus/
    ├── corpus-plan.md
    ├── corpus_scope.md
    ├── research/
    │   ├── repository_structure.md
    │   ├── device_type_candidates.md
    │   ├── source_taxonomy.md
    │   ├── relation_model.md
    │   └── revision_analysis.md
    ├── metadata/
    │   ├── scope.json
    │   ├── coverage_matrix.csv
    │   ├── SSOT.md                 (추후)
    │   ├── snapshot.json           (추후)
    │   ├── corpus_manifest.csv     (추후)
    │   ├── entities.jsonl          (추후, provenance)
    │   ├── relations.jsonl         (추후, provenance)
    │   ├── exclusions.csv          (추후)
    │   ├── statistics.json         (추후)
    │   └── validation_report.json  (추후)
    ├── raw/                       (이번 단계에서 원본 미추출)
    ├── processed/                 (이번 단계에서 공통 입력 미생성)
    └── freshness/                 (Core 이후)
    systems/                       (시스템별 파생 결과)
    benchmark/                     (질문·정답, 구축 입력과 분리)
    scripts/corpus/                (Extraction Script는 다음 단계)

Manifest는 원본 파일당 한 행으로 공통 Source Metadata를 저장한다.
배열/객체는 CSV 셀 안에 JSON으로 직렬화한다.
부분 정규화 문서가 여러 개이면 원본 document_id와 segment_id를 분리한다.
원본/Manifest ID 집합과 정규화의 parent_document_id 집합이 일치하도록 검증한다.

## 11. 구축 Pipeline

1. Discovery: 실제 checkout·정의·구현 위치 확인 — 완료.
2. Scope Finalization: 범위·source taxonomy·relation·Revision·종료 규칙 고정 — 완료.
3. Extraction Script 설계/구현: scope.json을 읽는 결정적 수집·선택·검증 — 다음 단계, 아직 미작성.
4. 실행 전 입력 SHA·범위·자료 이용 조건 확인.
5. 읽기 전용 원본에서 raw 복사, 출처·Hash·Manifest 작성.
6. 공통 정규화와 위치 매핑, Entity/Relation provenance 생성.
7. 중복·추출 오류·Coverage 검증.
8. Token 집계와 실제 Wiki Context 검증.
9. 2회 재생성, 팀 검토, 결손 기록을 포함한 검증 보고서 작성.
10. 모든 gate 충족 후 Corpus v1.0 Freeze.

공통 정규화는 인코딩·개행, 본문 추출, 범위 선택, 위치 매핑으로 제한한다.
요약·질의별 선별·정답 생성은 하지 않으며 Identifier·표·코드·조건을 보존한다.
A/B/C는 동일한 공통 입력을 사용하고 각 파생 결과는 입력 Snapshot/Manifest Hash와 처리 설정을 기록한다.

## 12. 통계와 Context 검증

전체 고유 파일 수와 제품/Cluster별 중복 관계 집계를 구분한다.
원본 본문·공통 입력·컴파일 Wiki의 Token 수, 문서 역할별 분포, 결손·제외 수를 기록한다.
Tokenizer 이름/버전, 모델과 집계 대상도 고정한다.

    Wiki + 시스템 지시문 + 질문 + 출력 예약 + 안전 여유 <= Context Window

최종 판정은 실제 Wiki Token으로 수행한다. 컴파일 입력 분할 제약은 별도 기록한다.
초과 시 Freeze 전에 모든 시스템의 공통 범위를 규칙에 따라 함께 조정하고 새 scope 버전을 부여한다.
C에만 자료를 선택 제공하거나 묵시적 잘라내기를 하지 않는다.
현재 Scope Finalization에서는 추출·컴파일·Token 측정을 실행하지 않는다.

## 13. Validation / Freeze

현재 Freeze를 막는 미완료 작업: 이용 조건 확인, 추출/selector 구현, 원본·정규화 Hash/Manifest,
Identifier·위치 매핑·2회 재생성, Token/Context 측정, 팀 검토와 평가 근거 사용 범위 점검.

완료 조건:

- [x] 3개 제품군과 보조 Cabinet, Cluster·탐색 종료 범위 확정.
- [x] 고정 Commit과 사양 모델 디렉터리, 출처별 Revision 계약 확정.
- [x] Source 역할·Entity/Relation·Coverage 상태 규칙 확정.
- [x] 결손 및 제외 감사 기록, 원본 경로와 관계 근거 확보.
- [ ] 수집·변환·공유에 적용할 원본 이용 조건과 실행 범위 확인.
- [ ] 원본·Manifest·정규화 parent 관계와 Hash 검증.
- [ ] Identifier 및 조건·표·코드 보존, 추출 실패·빈 본문 검사.
- [ ] 2회 생성한 문서 ID·원본/정규화 Hash 일치.
- [ ] provenance 관계와 source locator 검증.
- [ ] Token/Context 적합성 확인.
- [ ] A/B/C 동일 입력과 평가 질문/정답 차단 확인.
- [ ] 알려진 Coverage 결손 및 Revision 차이를 포함한 팀 검토 완료.
- [ ] Corpus v1.0 Git 버전과 데이터 Snapshot Hash 고정.

모든 missing을 억지로 present로 만드는 것은 완료 조건이 아니다.
허용한 결손은 검증 보고서와 평가 가능 범위에 반영하고,
예상하지 못한 결손은 추출 실패/검토 대상으로 보고한다.

## 14. Benchmark와 Freshness 분리

Benchmark 질문·정답·Gold Evidence는 추출·청킹·색인·Wiki 컴파일 입력에 넣지 않는다.
Gold Evidence는 Snapshot ID, source document, 원본 위치와 Entity/Revision을 참조한다.
개발용 질문과 최종 평가 질문을 분리하고 평가 결과에 맞춰 Corpus를 수정하지 않는다.

Freshness는 Core Freeze 이후 별도 before/after Snapshot으로 진행한다.
선정 규칙을 유지하고 추가·수정·삭제·이름 변경, 전후 Hash를 기록한다.
각 버전 내 A/B/C 입력을 동일하게 유지하고 갱신 방식·비용 기준을 사전에 정한다.
새 버전 평가에 이전 삭제/수정 근거가 남는지 검증한다.

## 15. 버전과 일정

scope-v1.0은 수집 대상과 Metadata 계약의 버전이며 corpus-v1.0과 다르다.
Corpus는 수집 v0.1 → 범위 반영 v0.5 → 정제/검증 v0.9 → Freeze v1.0으로 관리한다.
현재 수집을 하지 않았으므로 Corpus 버전을 생성 완료했다고 보고하지 않는다.

기존 일정은 목표이며 완료 조건을 충족하지 않으면 날짜만으로 Freeze하지 않는다.

| 목표 기간 | 작업 |
|---|---|
| 09.18–09.22 | Discovery/Scope 확정 및 검토 |
| 09.22–09.24 | 추출 구현 준비, SSOT·자료 조건·입력 검증 |
| 09.24–09.27 | 별도 실행 단계에서 수집·정규화 |
| 09.27–09.29 | 정제·재현성·통계·Context 검증 |
| 09.29–09.30 | 팀 검토 및 모든 gate 충족 시 Freeze |

핵심 원칙은 동일한 원본·동일한 공통 입력에 서로 다른 시스템 처리 방식을 적용하는 것이다.
