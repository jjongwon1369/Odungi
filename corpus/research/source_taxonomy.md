# Source taxonomy — scope-v1.0

기준 checkout: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`, 조사 baseline: `data_model/1.7`.
이 분류는 Corpus 출처를 구분한다. RAG/Wiki용 요약·컴파일 결과를 뜻하지 않는다.

## 1. 역할과 정의 대상을 서로 다른 축으로 둔다

`source_role`은 단일 주 역할이다. `device_type_definition`/`cluster_definition`은
specification과 sdk_codegen 양쪽에 존재하므로 역할 enum에 섞지 않고 `definition_kind`로 분리한다.
물리적 파일은 한 번만 등록하고 한 파일의 여러 정의는 `entity_bindings`로 연결한다.

| source_role | definition_kind 예 | 실제 근거 |
|---|---|---|
| specification | device_type | `data_model/1.7/device_types/LaundryWasher.xml` |
| specification | cluster / cluster_base | `data_model/1.7/clusters/LaundryWasherControls.xml`, `ModeBase.xml` |
| sdk_codegen | device_type | `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml` |
| sdk_codegen | cluster / cluster_base | 같은 디렉터리 `washer-controls-cluster.xml`, `mode-base-cluster.xml` |
| implementation | cluster / framework_contract / none | `src/app/clusters/mode-base-server/ModeBaseCluster.cpp`, `src/app/server-cluster/DefaultServerCluster.h` |
| documentation | none | `src/app/clusters/operational-state-server/README.md` |
| example | none | `examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap` 및 `.matter` |
| generated_definition | cluster | `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h` |
| test | none | `src/app/clusters/laundry-washer-controls-server/tests/TestLaundryWasherControlsCluster.cpp` |

SDK 설명은 `data_model/README.md:15`에서 사양 XML이 SDK codegen 입력이 아님을 명시한다.
시험 파일은 분류할 수 있지만 현재 Core scope에는 포함하지 않는다.
예제 C++는 `source_role=example`, `content_kind=implementation`으로 구분한다.
생성된 Metadata는 구현의 Revision 참조 근거이며 독립적인 수작업 구현으로 세지 않는다.

## 2. 문서 Metadata 계약

공통 키: `document_id`, `source_id`, `snapshot_id`, `source_path`, `source_url`, `commit_hash`,
`source_role`, `definition_kind`, `content_kind`, `source_revision`, `entity_bindings`,
`included_reason`, `content_hash`, `normalized_hash`, `source_spans`.
`doc_type`은 content_kind의 이전 이름이며 새 레코드에서 두 필드를 중복 저장하지 않는다.
`device_types`/`clusters`는 entity_bindings로부터 재생성할 수 있는 검색용 요약이며 관계의 원본이 아니다.

다음은 실제 source 값을 사용한 **향후 레코드 형식 예시**다. 추출 레코드 자체를 만든 것은 아니다.

```json
{
  "source_path": "data_model/1.7/device_types/Refrigerator.xml",
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
  }
}
```

- `source_revision.artifact`는 원본 파일 버전이다. 코드·문서의 Commit을 ClusterRevision 숫자와 비교하지 않는다.
- `declarations`는 한 파일에 여러 Device Type/Cluster Revision이 있는 경우 배열로 보존한다.
  SDK XML은 해당 cluster의 globalAttribute `0xFFFD`, Device Type은 해당 revision 요소,
  IDL은 해당 `revision N`과 `device type ..., version N`을 각각 기록한다.
- 숫자 Revision이 선언되지 않은 C++/Markdown은 빈 declarations 배열을 사용한다.
  구현이 생성 Metadata를 참조하면 별도 evidence가 있는 `uses_revision_declaration` 관계로 기록한다.
- spec SHA/tag, SDK Git SHA, Device Type Revision, ClusterRevision은 서로 다른 버전 축이다.
- `ResourceMonitoring.xml`처럼 root Revision이 여러 Cluster ID에 적용되는 파일은
  공통 root 선언 위치와 대상 ID를 모두 기록하고 파일을 Cluster마다 복제하지 않는다.
- `content_hash`는 원본 바이트 SHA-256, normalized_hash는 공통 정규화 본문 SHA-256이다.
  아직 추출하지 않았으므로 이번 단계에서 Hash 값을 만들어 넣지 않는다.
- source_role/정의 종류는 파일 출처와 내용으로 결정한다. `.xml` 확장자만으로 정하지 않는다.

## 3. 권위의 범위

1. **선택 baseline의 요구 정의:** `data_model/1.7` XML을 본 연구의 정의 기준으로 사용한다.
   외부 공식 사양 원문을 읽었다는 뜻이 아니며 안정 배포 사양이라고 주장하지 않는다.
2. **이 checkout의 codegen 선언:** `src/app/zap-templates/zcl/data-model/chip` XML을 사용한다.
   사양 XML에 없는 SDK endpointComposition을 사양 요구로 바꿔 기록하지 않는다.
3. **예제 구성:** 해당 `.zap`의 endpoint·부모 관계, `.matter`의 선언을 그 예제에 한정하여 사용한다.
4. **동작 구현:** C++ 본문을 근거로 삼되 실행 결과는 별도 검증이다.

충돌을 하나의 값으로 병합하지 않는다. 동일 ID·다른 출처·다른 Revision은 각각 유지한다.

## 4. 이전 unverified 37행 처리

Discovery의 74행은 지우지 않고 CSV의 `discovery_row_id`, `discovery_status`, `resolution`으로 연결했다.

| 이전 unverified의 범위 | 행 수 | 이번 처리 |
|---|---:|---|
| 선택 제품군 및 Cabinet | 21 | missing: 20행은 정해진 구현 디렉터리에 독립 Markdown 설명이 없음; 1행은 Temperature Alarm의 concrete SDK/구현/IDL도 없음 |
| Air Purifier / Dishwasher / Laundry Dryer | 16 | not_applicable: 최종 제품 scope에서 제외. 자료 부재나 구현 실패로 판정한 것이 아님 |

선택 scope의 핵심 Device→Cluster, spec 정의, SDK 정의와 구현 경로는 Temperature Alarm을 제외하고 확인했다.
일부 documentation 누락만으로 이 핵심 관계를 unverified로 되돌리지 않도록 항목별 상태를 분리했다.

추가 제외는 Cabinet의 Heater 전용 관계 2행이다. 기존 present였지만 Cooler-only scope에는 적용되지 않는다.
총 74행의 감사 기록에 신규 관계 17행을 더하여 91행이 되었다.

## 5. missing의 검색 범위와 한계

다음 9개 구현 디렉터리 바로 아래 `*.md`를 확인했으며 파일이 없었다:

- `src/app/clusters/descriptor`
- `src/app/clusters/fixed-label-server`
- `src/app/clusters/user-label-server`
- `src/app/clusters/groups-server`
- `src/app/clusters/on-off-server`
- `src/app/clusters/scenes-server`
- `src/app/clusters/thermostat-server`
- `src/app/clusters/laundry-washer-controls-server`
- `src/app/clusters/temperature-control-server`

보조 검색은 `docs/guides`, `docs/cluster_and_device_type_dev`, `docs/zap_and_codegen`과
선택 냉장고/세탁기 README, Thermostat linux/realtek README에서 수행했다.
구축 안내·일회성 언급·ID 표를 독립 Cluster 기능 가이드로 계산하지 않았다.
다른 파일의 API 주석과 외부 문서의 존재를 부정하는 판정이 아니다.
missing은 CSV에 기록한 **한정된 문서 유형·검색 범위**의 부재다.

Temperature Alarm 검색 범위:
`src/app/clusters`, `src/app/zap-templates/zcl/data-model/chip`,
`zzz_generated/app-common/clusters`, 선택 예제 및 all-clusters IDL.
`TemperatureAlarm`/`Temperature Alarm` 검색과 XML 직접 cluster/code 목록을 대조했다.
SDK의 `matter-devices.xml:3263` include는 존재하지만 concrete Cluster 정의는 아니다.
가장 비슷한 Alarm 구현을 해당 구현으로 대체하지 않는다.

## 6. 상태 집계 규칙

CSV의 `status`는 scope 적용 여부와 요청된 자료 Coverage의 종합 상태다.

- 제외 감사 행: `not_applicable` + scope_decision=exclude. 기존 항목 상태는 유지한다.
- 포함 Cluster 행: 확인할 주요 항목에 unverified가 있으면 unverified, 없고 missing이 있으면 missing, 그 외 present.
- 관계 전용 행: 해당 관계의 evidence로 판정하며 문서·IDL 등 불필요한 칸은 not_applicable.
- 문서/구현 등의 path가 unverified 표기여도 항목 status=missing이면 검색 범위 내 부재가 확인된 상태다.
  path 칸의 표기는 없는 경로를 추정하여 만들지 않았다는 뜻이다. 판단은 status 컬럼을 따른다.

현재 38 present / 21 missing / 32 not_applicable / 0 unverified.
이 중 선택 Cluster 관계는 42행(21 present / 21 missing), 신규 provenance 관계는 17행(present),
제외 감사 행은 32행이다. 서로 다른 분모를 섞어 Coverage 비율을 계산하지 않는다.
0 unverified는 **파일 존재·관계 조사 표의 결과**이며 의미적 정합성·실행·이용 조건까지 검증했다는 뜻이 아니다.
