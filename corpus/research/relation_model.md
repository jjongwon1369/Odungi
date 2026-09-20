# 관계 중심 Corpus Metadata — schema 2.0

이 모델은 원본의 provenance·coverage·출처별 주장만 표현한다.
LLM 생성 지식, 질문별 추론 결과, Wiki 페이지나 RAG 청크가 아니다.
이번에는 구조와 범위를 확정하며 entities.jsonl/relations.jsonl 등의 추출 결과는 만들지 않는다.

## 1. Entity와 assertion을 분리한다

Entity 종류: `device_type`, `cluster`, `cluster_base`, `device_type_base`, `endpoint_requirement`,
`example_endpoint`, `source_document`, `implementation_component`, `condition`.

- 식별자는 `(entity_kind, namespace, id)`이다. Cluster `0x0071`과 Device Type `0x0071`을 혼동하지 않는다.
- Base Device Type / Mode Base / Alarm Base / Label은 숫자 ID가 없으므로 안정적인 symbolic ID를 쓴다.
- 예제 endpoint ID에는 반드시 예제 source_path namespace를 붙인다. 서로 다른 앱의 endpoint 1은 같은 Entity가 아니다.
- Revision은 Entity의 유일한 전역 값이 아니다. 각 출처 assertion과 evidence에 붙인다.
- 물리 파일 ID는 Snapshot+상대 경로로 결정하며 여러 Entity가 같은 파일을 가리킬 수 있다.

## 2. Relation 레코드

실제 Refrigerator 요구를 표현하는 형식 예시:

```json
{
  "relation_id": "ref-cabinet-cooler@source-assertion",
  "relation_type": "requires_related_device_condition",
  "source_entity": {"kind": "device_type", "namespace": "matter", "id": "0x0070"},
  "target_entity": {"kind": "device_type", "namespace": "matter", "id": "0x0071"},
  "role": null,
  "requirement": "mandatory",
  "condition": {"op": "condition", "name": "Cooler", "required_value": true},
  "assertion_scope": "specification",
  "source_revision": {"device_type_revision": "3", "model_version": "1.7"},
  "evidence": [{
    "commit_sha": "1ac132b5ecd42cb6c78772f2576ed6f7fc814183",
    "source_path": "data_model/1.7/device_types/Refrigerator.xml",
    "source_role": "specification",
    "locator": "/deviceType/conditionRequirements/deviceType[@id='0x0071']/conditionRequirement[@name='Cooler']",
    "line_start": 68
  }],
  "status": "present"
}
```

필수: relation_id/type, source/target, assertion_scope, evidence, status.
role은 server/client가 해당할 때만 값이 있다. requirement는 mandatory/optional/conditional/
provisional/disallowed/not_applicable 중 하나이며 otherwiseConform 같은 조합은 condition AST와 raw 표현을 함께 보존한다.
단순 mandatory/optional 플래그로 조건을 제거하지 않는다.
`scope_condition`은 연구에서 선택한 Cooler=true, Heater=false 같은 프로필로서 원본 condition과 별도 필드다.

relation_id는 Snapshot, 출처 경로, locator, relation_type, 양 끝 Entity로 결정한다.
같은 두 Entity에 서로 다른 출처가 주장하는 관계는 서로 다른 레코드다.
`status=missing`인 lookup 결과와 evidence가 있는 사실 관계를 구별한다.
없는 구현 Entity를 생성해 implements 관계를 만들지 않는다. 누락은 Coverage 평가 레코드에 남긴다.

## 3. 필요한 관계와 실제 근거

| relation_type | 방향 | 의미·근거 |
|---|---|---|
| requires_cluster | Device Type → Cluster | 역할·mandatory/optional/조건을 가진 선언. `LaundryWasher.xml`의 clusters |
| inherits_requirements | Device Type → Base | `BaseDeviceType.xml`, `spec_parsing.py:1963`의 적용 |
| requires_related_device_condition | Device Type → Device Type | Refrigerator→Cabinet Cooler, Room AC→Root GroupcastListenerCond |
| requires_endpoint_scope | Device Type → Endpoint requirement | 각 XML의 classification scope=endpoint; 실제 번호를 요구하지 않음 |
| requires_endpoint | Device Type → Endpoint requirement | SDK matter-devices.xml:3055의 tree/min 1 Cabinet |
| example_composes_endpoint | 예제 Endpoint → 예제 Endpoint | Chef ZAP endpoint 1→2/3; 그 앱의 관찰 사실 |
| defined_by_specification | Cluster/Device Type → Source | 선택 `data_model/1.7` XML |
| defined_by_sdk | Cluster/Device Type → Source | SDK Cluster XML 또는 matter-devices.xml의 특정 요소 |
| implemented_by | Cluster → Implementation component | C++ entry point와 namespace/ID/alias 연결 |
| uses_shared_implementation | Device Type → Implementation component | requires_cluster + implemented_by 근거 사슬을 명시 |
| derives_cluster_base | Cluster → Cluster base | Mode_Refrigerator.xml classification baseCluster=Mode Base 등 |
| illustrated_by | Entity → Example source | 예제 선택 구성, 사양 준수 판정과 분리 |
| uses_revision_declaration | Implementation → Generated definition | ResourceMonitoringCluster.cpp:101–106 → Metadata.h kRevision |

multiple Device Types → shared implementation은 동일 target ID를 공유하는 여러 관계로 표현한다.
예: Laundry Washer의 0x0051, Refrigerator/Cabinet의 0x0052, Room AC의 0x0063은
`src/app/clusters/mode-base-server/mode-base-cluster-objects.h:61–69`와 ModeBaseCluster.cpp로 연결된다.
직접적인 제품별 구현이라고 부르지 않는다. 필요한 중간 Cluster ID는 `via_entities`에 보존한다.

## 4. 냉장고 관계의 출처별 분리

1. **사양 모델:** Refrigerator.xml:68–71은 Cabinet의 Cooler 조건을 mandatory로 요구한다.
2. **SDK 모델:** matter-devices.xml:3055–3060은 tree 구성과 최소 1개의 0x0071 endpoint를 선언한다.
   이 cardinality는 선택 사양 XML에 없으므로 SDK assertion으로 보존한다.
3. **예제:** Chef ZAP의 `$.endpoints`에서 2·3의 parentEndpointIdentifier=1이다.
   전용 refrigerator-app.zap은 Cabinet의 parent 값이 null이므로 같은 assertion으로 병합하지 않는다.
4. **연구 scope:** Cooler=true/Heater=false를 선택한다. 실제 모든 냉장고나 모든 Cabinet의 전역 특성이라는 주장은 아니다.

추상 요구와 실제 endpoint 번호를 별개 Entity로 둔다.
SDK 조건을 사용해 사양 XML에서 빠진 문장을 임의로 복원하지 않는다.

## 5. Coverage CSV는 관계 그래프의 검토용 뷰다

- Cluster 행은 requires_cluster와 그 정의/문서/구현 lookup 결과를 한 행에 펼친다.
- `specification_path/revision`과 `sdk_definition_path/revision`은 별개 컬럼이다.
- `device_type_definition_path/revision`은 Cluster Revision과 구분한다.
- `implementation_revision`은 Git SHA, `example_cluster_revision`과 `example_device_revision`은 선언 숫자다.
- `evidence_location`은 경로+행 또는 selector 객체의 JSON 배열이다.
- `related_device_type`, `endpoint_requirement`, `relation_type`, `implementation_scope`로
  단순 Device–Cluster 목록에 없던 관계를 표현한다.
- 관계 전용 행에서 cluster_id가 not_applicable이면 Cluster 수에 포함하지 않는다.
- `discovery_row_id/status`와 scope_decision으로 이전 74행을 추적한다. 제외 행은 현재 scope 통계에서 별도 집계한다.
- 문서 부족 때문에 status=missing이어도 relation_status=present일 수 있다.

CSV는 모든 원자적 graph edge의 완전한 직렬화가 아니다. 이후 관계 생성 시 각 path와 evidence를
typed Entity/Relation로 분리하고 중복 제거한다. 요구·부모 연결·공유 구현을 생성 모델로 추론하지 않는다.

## 6. 검증 규칙

1. source/target kind와 namespace에 맞는 ID를 검증한다.
2. 원본 locator를 해석할 수 있어야 하며 선택 SHA의 파일과 매칭해야 한다.
3. source_role마다 declaration Revision을 별도로 검사한다. 같은 숫자여도 의미적 일치로 간주하지 않는다.
4. shared implementation은 원본 파일 하나와 여러 근거 사슬로 표현한다.
5. example assertion에는 반드시 예제 namespace를 붙인다.
6. 사양 조건을 평가할 정보가 없으면 원본 AST와 unverified 평가 상태를 남긴다.
7. 이 모델은 평가용 정답/질문을 포함하지 않는다. A/B/C 중 한 시스템에만 추가 관계 지식을 제공하지 않는다.
