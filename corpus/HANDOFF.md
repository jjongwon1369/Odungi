# Corpus Handoff

현재 전달 버전은 **Corpus v0.1**이며 v1.0 Freeze 준비 검토 상태다. v1.0 tag는 생성하지 않았다.
최종 준비 여부는 [freeze_gate.json](metadata/freeze_gate.json)을 확인한다.

SSOT는 connectedhomeip의 `master`에서 확인한 commit
`1ac132b5ecd42cb6c78772f2576ed6f7fc814183`이다. 사용 기준은 branch의 최신 상태가 아니라 이 commit이다.
snapshot_id는 [snapshot.json](metadata/snapshot.json)에 있으며 commit·Scope·Coverage·pipeline Hash를 결합한다.
사양 XML baseline은 `data_model/1.7` 개발 snapshot이며, 안정 배포 사양이라고 보장하지 않는다.

## 범위와 수량

대상은 Laundry Washer(0x0073), Room Air Conditioner(0x0072), Refrigerator(0x0070),
그리고 Refrigerator의 명시된 구성 관계인 Temperature Controlled Cabinet(0x0071, Cooler-only)이다.
제품군 3개/Device Type ID 4개, 고유 Cluster 23개, Device→Cluster 관계 42개다.
Root 조건과 Base는 정해진 지원 문맥이며 새로운 제품 범위가 아니다.

원본 파일 282개, 정규화 문서 282개, 전체 관계 764개. raw 3,884,956 bytes,
정규화 2,144,062 characters. Token 수는 미측정이다.
전체 파일 집계는 물리 source path마다 한 번이다. 제품/Cluster별 집계는 공유 파일을 중복 연결할 수 있다.
제품별 관련 파일은 Washer 113, Room AC 209, Refrigerator 99, Cabinet 81개다.
전체 role/type/Cluster 집계는 [statistics.json](metadata/statistics.json)에 있다.

| 경로 | 역할 |
|---|---|
| `metadata/scope.json`, `metadata/coverage_matrix.csv` | 확정 범위와 결손 감사 기록 |
| `raw/connectedhomeip/<source_path>` | 고정 Git blob 바이트 원본 |
| `processed/documents.jsonl` | 파일별 선택 원문·정규화·원본 위치 |
| `metadata/corpus_manifest.csv` | 물리 원본마다 하나의 문서 ID·Hash·출처·Revision |
| `metadata/entities.jsonl`, `metadata/relations.jsonl` | provenance 관계와 Entity |
| `metadata/snapshot.json`, `statistics.json`, `validation_report.json` | 실행 기준·통계·검증 |
| `metadata/freeze_audit.json`, `freeze_gate.json` | 최종 범위 검토의 근거와 준비 상태 |
| `research/` | missing/이용 조건/Freeze 체크리스트 |
| `../scripts/corpus/` | 추출·정규화·검증 구현 |

## documents.jsonl 계약

각 줄은 JSON 객체 하나이며 한 물리 원본에 한 record다.

| 필드 | 의미 |
|---|---|
| `document_id` | source_id와 저장소 상대 경로 기반 안정 ID; 내용 Hash와 별개 |
| `snapshot_id` | snapshot.json과 동일한 고정 입력 버전 |
| `text` | 선택 원문의 발췌 구간을 LF로 연결한 문자열 |
| `metadata` | manifest 필드, source_id/url, normalized_hash, entity_bindings, identifier_inventory 등 |
| `source_spans[]` | source_path, char_start/end, line_start/end, locator |

metadata의 source_role은 specification/sdk_codegen/implementation/example/documentation/generated_definition을 구분한다.
definition_kind는 정의 대상, doc_type은 파일 형식이다. CSV의 device_types/clusters/source_revision 등의
배열·객체는 JSON 문자열로 저장되므로 CSV 파싱 후 JSON으로 다시 읽는다.
source_revision.artifact는 Git commit, declarations는 **그 출처의** Entity별 revision·scheme·locator다.
구현에 숫자 revision이 없으면 declarations가 비어 있을 수 있다. 서로 다른 출처의 revision을 합치거나 오류로 판정하지 않는다.

char_start/end는 UTF-8 decode 후 CRLF/CR을 LF로 통일한 원본 view의 Unicode code point offset이다.
끝 offset은 exclusive, 줄 번호는 1-based inclusive다. 본문은 standalone XML/JSON/IDL일 필요가 없다.
원문 구간 전체를 보존하며 검색용 chunk, 요약 또는 Wiki 산출물이 아니다.

## relations.jsonl 계약

필수 필드: relation_id, relation_type, source_entity, target_entity, document_id,
role, requirement, condition, evidence. assertion_scope/status도 저장한다.
Entity는 `{kind, namespace, id}`다. Cluster ID와 Device Type ID의 숫자가 같아도 kind가 다르면 별개다.
example_endpoint의 namespace는 예제 source_path다.

requires_cluster, inherits_requirements, requires_related_device_condition, requires_endpoint,
requires_endpoint_scope, example_composes_endpoint, defined_by_specification/sdk, implemented_by,
uses_shared_implementation, derives_cluster_base, illustrated_by, uses_revision_declaration,
has_source_file 등의 관계가 있다. coverage_ids/via_entities/scope_condition 등은 해당 관계에서만 제공한다.
requirement_raw 및 conformance AST/raw는 원문 조건을 보존한다. optional을 실제 활성화로 해석하지 않는다.
공유 구현의 여러 관계는 같은 문서/구현 component를 참조하며 파일을 제품별로 복제하지 않는다.

evidence에는 source_path, commit_sha, content_hash, line_start, locator, document_id, source_role, storage가 있다.
764개 관계의 primary document는 모두 Corpus에 존재한다. 근거 897건 중 893건은 Corpus 문서로 연결된다.
**4건은 upstream_reference_only이며 document_id=null이다.** R005/R008/R011/R014의
`src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py:1963` 참조다.
이 파일은 manifest/raw에 없으며, pinned checkout의 존재·Hash·줄 범위만 검증했다.
모든 근거가 Corpus 안에 있다는 보장은 하지 않는다. 2026-09-20 검토에서 4건 모두
external_reference_only로 유지하기로 결정했다. 현재 재생성·검증에는 pinned checkout의 해당 파일 접근이 필요하다.
상세 결정은 [upstream_exceptions.md](research/upstream_exceptions.md)에 있다.
locator=file인 765건은 파일 단위 근거이므로 세부 문장/함수 수준의 위치로 과장하지 않는다.

## Provenance 확인

1. document_id로 manifest 행을 찾는다. source_path와 raw_path, commit_hash를 읽는다.
2. raw_path의 파일 SHA-256이 content_hash와 같은지 확인한다.
3. pinned connectedhomeip에서 `git show <commit>:<source_path>` 또는 binary-safe cat-file로 원본을 대조한다.
   Windows checkout의 autocrlf 결과와 혼동하지 않는다.
4. UTF-8/LF 원본 view에서 source_spans를 절취하고 LF로 연결한 결과가 text와 같은지 확인한다.
5. relation.evidence의 문서 ID·경로·Hash·commit·줄 범위를 대조한다. 외부 참조 예외는 upstream checkout에서 확인한다.

## 재생성·검증

프로젝트 루트에서 Python 3.10+와 Git으로 실행한다. connectedhomeip는 읽기 전용이며 commit이 다르거나 dirty면 실패한다.
실제 재생성은 [이용 조건 검토](research/licensing_review.md)의 확인 사항을 함께 읽고 수행한다.

```powershell
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --dry-run
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --validate-only
python scripts/corpus_review/freeze_audit.py
```

검증은 원본/정규화 Hash·Identifier·metadata·관계·Coverage 및 두 임시 디렉터리 독립 재생성을 포함한다.
Freeze audit는 검토 기록만 갱신하고 Corpus Scope/원본/추출 pipeline을 바꾸지 않는다.

## 담당 경계

Corpus 담당자는 명시된 snapshot의 동일성, 문서별 Source provenance, Metadata, 결정적 재현성,
선택 원문 구간의 Identifier 보존을 보장한다. 관계 근거의 위 4건 예외와 파일 단위 근거의 한계는 명시적으로 남긴다.
원본 전체에서 제외된 Scope 밖 구간은 정규화 대상이 아니다.

Corpus 담당자는 RAG chunk 품질, retrieval 성능, embedding 적합성, Wiki compilation 품질,
Wiki context window 적합성, 답변 정확도를 보장하지 않는다. 이 문서는 시스템별 구현 방법을 결정하지 않는다.
사양 적합성·실행 동작·Code-Document Consistency·benchmark 적절성도 평가하지 않았다.
기존 보고서의 token/의미 검토 경고는 이번 Corpus Freeze Gate의 필수 성능 조건으로 사용하지 않는다.
이용 권한 검토·교차검토가 끝나기 전 전체 raw 공개 배포를 승인한 것으로 해석하지 않는다.
