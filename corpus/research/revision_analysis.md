# Revision 차이 분석 — scope-v1.0

대상 SDK Commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`.
선택 사양 모델: `data_model/1.7`.

## 1. 무엇을 authoritative definition으로 보는가

사양 요구 질문에는 선택된 `data_model/1.7` XML을 기준으로 삼는다.
이것은 Repository에 보관된 사양 모델의 authority이지 외부 사양 원문·인증 준수에 대한 검증이 아니다.
근거: `data_model/README.md:7–16`, `data_model/1.7/spec_sha`, `spec_tag`.
SDK codegen 정의 질문에는 `src/app/zap-templates/zcl/data-model/chip`의 선언이 기준이다.
예제 구성 질문은 해당 ZAP/IDL, 구현 질문은 C++ 본문 및 참조 Metadata가 기준이다.

`src/app/SpecificationDefinedRevisions.h:53`의 값은 0x01070000이나,
루트 `SPECIFICATION_VERSION:1`은 1.2.0이다. 이 둘의 용도·역사적 관계는 이번 범위에서 확정하지 않았다.
정의 baseline을 루트 파일 하나로 자동 선택하지 않는다.
`spec_tag=0.9-1.7-winter2027`이며 provisional 항목을 포함하므로 정식 1.7 배포판이라고 부르지 않는다.

## 2. Device Type Revision과 예제 Revision

| Device Type | 사양 XML Revision | SDK Device Type Revision | 확인한 예제 선언 |
|---|---:|---:|---|
| Laundry Washer 0x0073 | 2 | 2 | NXP ZAP/IDL은 1 |
| Room Air Conditioner 0x0072 | 5 | 5 | Chef ZAP/IDL은 5 |
| Refrigerator 0x0070 | 3 | 3 | Chef 및 전용 ZAP/IDL은 1 |
| Temperature Controlled Cabinet 0x0071 | 6 | 6 | Chef 및 전용 ZAP/IDL은 1 |

근거:

- `data_model/1.7/device_types/{LaundryWasher,RoomAirConditioner,Refrigerator,TemperatureControlledCabinet}.xml:60`.
- `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml`의 해당 deviceId/revision 요소.
- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap`의 endpointTypes/deviceIdentifiers/deviceVersions 및 대응 .matter.
- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap` 및 .matter.
- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap` 및 .matter.
- `examples/refrigerator-app/refrigerator-common/refrigerator-app.zap` 및 .matter.

Device Type Revision과 그 endpoint의 Cluster Revision은 다른 축이다.
예를 들어 Laundry Washer가 version 1이어도 `.matter:1956`의 LaundryWasherMode는 revision 4,
`:2020`의 LaundryWasherControls는 2, `:2078`의 OperationalState는 3이다.
장치 version 1을 모든 Cluster revision 1로 전파하지 않는다.

## 3. Cluster 선언과 구현의 Revision 차이

| Cluster | 사양 모델 | SDK XML | 선택 예제 IDL | 생성 Metadata / 구현 참조 |
|---|---:|---:|---:|---|
| HEPA Filter Monitoring 0x0071 | 2 | 1 | 1 | kRevision=1 |
| Activated Carbon Filter Monitoring 0x0072 | 2 | 1 | 1 | kRevision=1 |
| Relative Humidity Measurement 0x0405 | 5 | 3 | 3 | kRevision=3 |
| Temperature Alarm 0x0064 | 1, provisional | concrete 정의 missing | missing | concrete 구현 missing |

필터 근거:

- `data_model/1.7/clusters/ResourceMonitoring.xml:60–63`: root revision 2, 변경 이력에 Medium 추가.
- 같은 파일 `:177`: Medium(0x0006) 정의가 존재한다.
- `src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml:34,85`: 해당 두 Cluster의 0xFFFD 값은 1.
- `zzz_generated/app-common/clusters/{HepaFilterMonitoring,ActivatedCarbonFilterMonitoring}/Metadata.h:20`의 kRevision=1.
- `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp:101–106`은 해당 kRevision을 인코딩한다.

습도 근거:

- `data_model/1.7/clusters/WaterContentMeasurement.xml:60–66`: root revision 5와 품질 변경 이력.
- `src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml:33`: 값 3.
- `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h:20`: kRevision=3.
- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp:84–85`: 해당 상수 인코딩.

이는 **선언 값과 코드 참조**를 확인한 결과다. 실행해서 읽은 ClusterRevision 값이 아니다.
전체 필드의 의미·품질·명령 동작이 어떤 Revision을 완전히 구현하는지는 unverified다.
Temperature Alarm은 `TemperatureAlarm.xml`에 provisional 선언이 있고 SDK Device include는 있지만
concrete 정의/구현은 검색 범위 내 missing이다. 다른 알람 구현을 근거로 있다고 판단하지 않는다.

그 밖의 포함 Cluster의 spec/SDK 선언 값은 CSV의 specification_revision/sdk_revision으로 대조했다.
같은 숫자만으로 전체 정합성을 증명하지 않는다.

## 4. 같은 Revision 또는 다른 Revision에서의 구성 차이

### Refrigerator composition

SDK `matter-devices.xml:3055–3060`은 tree/min 1 Cabinet endpoint를 선언한다.
Chef ZAP `:5015–5025`에서 Cabinet 2·3은 부모 1을 가진다.
전용 refrigerator-app.zap의 두 Cabinet은 parentEndpointIdentifier=null이다.
사양 Refrigerator.xml은 Cooler conditionRequirement는 있지만 같은 cardinality 요소를 제공하지 않는다.
따라서 SDK 요구/예제 관찰/사양 조건을 별도 assertion으로 기록한다.
부모 값 null만으로 실제 동작·전체 사양 위반을 확정하지 않는다.

### Cabinet 온도 제어

선택 Cabinet XML은 TN mandatory/TL disallowed를 요구한다.
전용 냉장고 예제의 `refrigerator-common/src/static-supported-temperature-levels.cpp:30–39`에는
온도 level delegate가 남아 있다. 예제 Device Type revision은 1이다.
파일 존재만으로 실행 중 TL 기능이 활성화되었다고 판정하지 않으며,
추후 FeatureMap/연결 코드까지 대조할 비교 사례로 유지한다.

### 동일 ID, 서로 다른 정의 내용

SDK matter-devices.xml의 Refrigerator Mode include에는 requireAttribute START_UP_MODE가 있고,
선택 Refrigerator.xml의 같은 Mode 요구에는 StartUpMode disallowConform이 있다.
이 내용 차이는 단순 Device Type revision 숫자 일치(둘 다 3)로 발견할 수 없다.
SDK requireAttribute 처리 의미까지 확인하지 않았으므로 자동 오류로 분류하지 않는다.

## 5. Corpus에 차이를 기록하는 방법

- 원본 source_role·path·Commit을 보존하고 Entity별 선언 Revision을 source_revision.declarations에 저장한다.
- C++ artifact_revision은 Commit이고, 참조 ClusterRevision은 별도의 evidence 관계다.
- CSV에는 Device Type / specification Cluster / SDK Cluster / example Device / example Cluster Revision을 분리했다.
- `revision_comparison=different_declared_values`는 숫자 차이만 뜻한다. error/mismatch defect 판정이 아니다.
- 차이가 있다는 이유만으로 제외하지 않는다. 선정된 기능을 다루는 자료이면 원본 그대로 포함한다.
- 제외 근거는 제품/조건/탐색 경계다. 특정 시스템에 유리하도록 최신 자료만 고르지 않는다.

## 6. Code-Document Consistency 평가에서의 활용

향후 평가 유형으로 source-qualified 조회, 버전 간 차이 설명, 구현 Revision 참조 추적,
필수/선택 요구와 예제 구성을 구별하는 질문을 만들 수 있다.
Gold Evidence에는 양쪽 출처와 Revision을 함께 연결한다. 예제 omission은 optional 기능의 미선택일 수 있다.
답변은 일치/차이/증거 부족을 구별해야 하며 모든 차이를 결함으로 부르면 오답이다.
이번에는 질문·정답 세트를 만들지 않았고, 어떠한 차이도 사전 정답으로 Corpus 본문에 주입하지 않았다.

미해결: 같은 Revision의 의미적 차이, 예제의 실제 Feature 활성 상태, root 버전 파일의 용도,
런타임 동작 및 외부 사양 원문과의 완전한 대응. 이들은 Coverage 파일 존재 판정과 별개다.
