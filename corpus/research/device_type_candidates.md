# Device Type 후보와 근거 조사

조사 기준: connectedhomeip HEAD 1ac132b5ecd42cb6c78772f2576ed6f7fc814183,
data_model/1.7. 최종 baseline 선정 전의 Discovery 결과다.
모든 source path는 connectedhomeip 루트 기준이다. Repository 구조·제약은 repository_structure.md를 참조한다.

## 1. 후보 비교

아래 모든 Device Type 이름·ID·Revision은 data_model/1.7/device_types의 해당 XML:60에서 확인했다.
직접 Cluster 수에는 Base 요구 4종과 Root Node의 Cluster를 포함하지 않는다.

| 후보 | ID / Revision | 직접 Cluster | 근거 파일 | 판단 |
|---|---|---:|---|---|
| Refrigerator | 0x0070 / 3 | 4 | data_model/1.7/device_types/Refrigerator.xml | 추천하되 Cabinet을 함께 조사 범위에 포함 |
| Room Air Conditioner | 0x0072 / 5 | 12 | data_model/1.7/device_types/RoomAirConditioner.xml | 추천; HVAC·조건부 기능의 다양성 |
| Laundry Washer | 0x0073 / 2 | 6 | data_model/1.7/device_types/LaundryWasher.xml | 추천; 필수 상태와 선택 제어 연결이 명확 |
| Temperature Controlled Cabinet | 0x0071 / 6 | 6 | data_model/1.7/device_types/TemperatureControlledCabinet.xml | 냉장고 보조 범위; 독립 추천 제품군 아님 |
| Air Purifier | 0x002D / 4 | 6 | data_model/1.7/device_types/AirPurifier.xml | 문서 Coverage를 우선할 때 유력 대체 후보 |
| Dishwasher | 0x0075 / 2 | 6 | data_model/1.7/device_types/Dishwasher.xml | 세탁기와 비교할 수 있는 추가 후보 |
| Laundry Dryer | 0x007C / 2 | 6 | data_model/1.7/device_types/LaundryDryer.xml | 세탁기와 기능 중복이 커 후순위 |

LG전자 제품과의 연관성은 냉장고·에어컨·세탁기·공기청정기·식기세척기·건조기라는 제품군을
기준으로 한 연구 범위 판단이다. 특정 LG 제품의 Matter 인증·지원 여부를 확인한 결과는 아니다.

## 2. 공통 요구와 CSV 판정 기준

CSV 74행은 직접 관계 46행과 Base Device Type 관계 28행이다.
직접 항목은 모두 server이며 client 관계를 임의 생성하지 않았다.
BaseDeviceType.xml은 Descriptor(0x001D) 필수, Binding(0x001E)은 Simple AND Client 조건의 필수,
Fixed Label(0x0040)/User Label(0x0041)은 선택으로 선언한다.
Descriptor TAGLIST에는 Duplicate 조건이 있다.
근거: data_model/1.7/device_types/BaseDeviceType.xml,
src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py:1963–1964.

RootNodeDeviceType.xml의 commissioning/security 및 조건 전파는 별도 후속 범위다.
현재 CSV는 노드 전체의 모든 transitive dependency를 완성한 Manifest가 아니다.

- present: 요구 관계, 사양/SDK 정의, IDL 선언, 관련 설명 문서, C++ 구현 파일을 확인했다.
- unverified: 이 연결 중 하나 이상을 확보하지 못했다. 항목별 status 컬럼을 함께 본다.
- missing: 지정 검색 범위의 부재가 확정된 경우에만 사용한다. 이번 초안에서는 사용하지 않았다.
- not_applicable: 적용되지 않는 근거가 명확한 경우에만 사용한다. 이번 초안에서는 사용하지 않았다.

현재 present 37행, unverified 37행이다. present는 기능 완성도·버전 동등성·실행 성공 판정이 아니다.
documentation_path는 Cluster 또는 공유 기반 구현 설명을 기록했다.
ID 표만 확인한 경우 상세 문서 Coverage를 채운 것으로 계산하지 않았다.
IDL은 숫자 Cluster ID로 선언을 확인했고, generic_all_clusters 출처는 장치 예제 연결로 간주하지 않는다.
example_device_server_endpoints는 선택 IDL에서 해당 Device Type과 server가 함께 선언된 endpoint다.
확인되지 않은 경우 unverified이며, 다른 예제에서도 없다는 뜻은 아니다.
feature_condition에는 XML 조건 구조를 보존한 축약 표기를 기록했다.
provisional/otherwiseConform을 단순 Optional로 단정하지 않는다.

## 3. Refrigerator → Cabinet

직접 선택 Cluster는 Identify(0x0003), Refrigerator And Temperature Controlled Cabinet Mode(0x0052),
Refrigerator Alarm(0x0057), Activated Carbon Filter Monitoring(0x0072)이다.
마지막 항목은 revision >= 3 조건이며 Mode에는 DEPONOFF/StartUpMode 금지가 있다.
직접 목록에 Temperature Control이 없는 점을 주의해야 한다.

Refrigerator.xml:68의 conditionRequirements는 Temperature Controlled Cabinet의 Cooler를 요구한다.
Cabinet.xml은 Temperature Control(0x0056) 필수, TN 필수/TL 금지를 선언한다.
냉각용 Mode는 Cooler 조건, Oven Mode/상태는 Heater 조건이며 Temperature Alarm에는 provisional 선언이 있다.
CSV는 Cabinet의 전체 직접 관계를 보여주므로 Heater 관계를 냉장고 Corpus에 자동 포함하지 않는다.

근거 연결:

- 정의: data_model/1.7/clusters/Mode_Refrigerator.xml, RefrigeratorAlarm.xml, TemperatureControl.xml.
- SDK XML: src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml,
  refrigerator-alarm.xml, temperature-control-cluster.xml.
- IDL/ZAP: examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter 및 .zap.
- 전용 앱 IDL: examples/refrigerator-app/refrigerator-common/refrigerator-app.matter:1714,1730.
  냉장고와 Cabinet endpoint가 분리되고 각각 revision 1을 선언한다.
- 문서: examples/refrigerator-app/linux/README.md, src/app/clusters/mode-base-server/README.md,
  src/app/clusters/alarm-base-server/README.md.
- 구현: src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp,
  src/app/clusters/mode-base-server/ModeBaseCluster.cpp,
  src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp.
- 앱 연결: examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp:30–39.

**선정 근거:** 여러 endpoint와 공유 모드·알람·온도 제어를 잇는 복합 질의에 적합하다.
**제약:** 전용 앱의 revision 1과 조사 XML revision 3/6은 다르다.
전용 앱 IDL에는 냉장고 Mode/Alarm 선언이 없으나 Chef 구성에는 있다.
예제의 온도 level delegate와 현재 Cabinet TN/TL 요구의 정합성은 추가 확인해야 한다.
docs/issue_triage.md:136에는 refrigerator-app이 UNMAINTAINED로 표시되어 있다.
문서·코드 일치 여부를 확인하는 대상이지, 정상 동작 제품의 검증 근거로 쓰지 않는다.

## 4. Room Air Conditioner

직접 필수: Identify(0x0003), On/Off(0x0006, DF 필수), Thermostat(0x0201).
직접 선택: Groups(0x0004), Scenes Management(0x0062), HEPA Filter Monitoring(0x0071),
Activated Carbon Filter Monitoring(0x0072), Fan Control(0x0202),
Thermostat User Interface Configuration(0x0204), Temperature Measurement(0x0402),
Relative Humidity Measurement(0x0405).
Thermostat Mode(0x0063)는 otherwise/provisional 및 revision >= 5 조건을 그대로 보존했다.
Root Node GroupcastListenerCond와의 관계도 RoomAirConditioner.xml:70에 선언되어 있다.

근거 연결:

- 정의: data_model/1.7/clusters/Thermostat.xml, FanControl.xml, Mode_Thermostat.xml,
  ThermostatUserInterfaceConfiguration.xml, ResourceMonitoring.xml.
- SDK XML: src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml,
  fan-control-cluster.xml, thermostat-mode-cluster.xml, resource-monitoring-cluster.xml.
- IDL/ZAP: examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter 및 .zap.
- 문서: examples/chef/README.md(구성 방법), src/app/clusters/fan-control-server/README.md,
  thermostat-user-interface-configuration-server/README.md 및 resource-monitoring-server/README.md.
- 구현: src/app/clusters/thermostat-server/ThermostatClusterBase.cpp 및 Read/Write 분할 파일,
  src/app/clusters/fan-control-server/FanControlCluster.cpp,
  src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp.

**선정 근거:** 필수/선택 제어, 센서, 필터 및 공유 구현을 비교할 수 있어 다른 두 제품군과 자료 구성이 다르다.
**제약:** Chef IDL:2375–2556에서 AC는 endpoint 1, 온도/습도 센서는 endpoint 2/3이다.
센서 Cluster가 같은 파일에 있다는 이유로 AC endpoint가 구현했다고 판단하면 안 된다.
Scenes/Filter/Thermostat Mode는 선택 Chef 구성에서 확인되지 않아 범용 all-clusters IDL을 별도로 참조했다.
AC 전용 설명 prose의 충분성과 최신 Thermostat 기능의 구현 대응은 unverified다.

## 5. Laundry Washer

사용자가 제시한 Washer의 실제 대응 이름은 Laundry Washer이다.
직접 필수는 Operational State(0x0060)와 그 OperationCompletion 이벤트다.
Identify(0x0003), On/Off(0x0006), Laundry Washer Mode(0x0051),
Laundry Washer Controls(0x0053), Temperature Control(0x0056)은 선택이다.
On/Off를 포함할 때 DF 필수, Mode는 DEPONOFF/StartUpMode 금지 조건이 있다.

근거 연결:

- 정의: data_model/1.7/clusters/Mode_LaundryWasher.xml, LaundryWasherControls.xml, OperationalState.xml.
- SDK XML: src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml,
  washer-controls-cluster.xml, operational-state-cluster.xml.
- IDL/ZAP: examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter 및 .zap.
- 문서: examples/laundry-washer-app/nxp/README.md,
  src/app/clusters/operational-state-server/README.md, mode-base-server/README.md.
- 구현: src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp:27,49,
  src/app/clusters/operational-state-server/OperationalStateCluster.cpp,
  examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp:39.

**선정 근거:** 6개의 직접 Cluster 범위가 비교적 작고, 모드·세탁 제어·동작 상태의 구조화 정의와 예제 연결이 있다.
**제약:** NXP 예제는 prototype이며 .matter의 Laundry Washer revision은 1이다.
조사 XML revision 2가 요구하는 이벤트의 예제 대응은 별도 검증해야 한다.
플랫폼 부분은 포함/제외 규칙을 정해 필요한 delegate·구성만 범위에 넣어야 한다.

## 6. 추가 후보

### Air Purifier

필수 Identify/Fan Control, 선택 Groups/OnOff/HEPA/Activated Carbon Filter Monitoring.
정의는 data_model/1.7/device_types/AirPurifier.xml과 clusters/FanControl.xml, ResourceMonitoring.xml.
examples/air-purifier-app/air-purifier-common/air-purifier-app.matter 및 .zap,
같은 디렉터리 README.md의 Fan/Filter PICS와
examples/air-purifier-app/air-purifier-common/src/air-purifier-manager.cpp가 있다.
서버 구현은 src/app/clusters/fan-control-server/FanControlCluster.cpp와
resource-monitoring-server/ResourceMonitoringCluster.cpp다.
문서와 구현의 연결이 비교적 좋아 2~3종을 더 작은 범위로 구성할 때 Room AC의 대체 후보로 적합하다.
앱의 추가 Air Quality/온습도/Thermostat endpoint를 Air Purifier의 필수 요구로 오인하지 않는다.

### Dishwasher

필수 Operational State 및 OperationCompletion; 선택 Identify/OnOff/Temperature Control/
Dishwasher Mode(0x0059)/Dishwasher Alarm(0x005D).
정의는 data_model/1.7/device_types/Dishwasher.xml과 clusters/Mode_Dishwasher.xml, DishwasherAlarm.xml.
examples/chef/devices/rootnode_dishwasher_cc105034fe.matter 및 .zap에서 구성을 확인했다.
전용 examples/dishwasher-app/dishwasher-common/dishwasher-app.matter는 더 작은 선택 구성을 가진다.
문서는 docs/examples/dishwasher.md(인덱스), examples/dishwasher-app/silabs/README.md(앱 안내),
src/app/clusters/alarm-base-server/README.md(공통 알람 설명)다.
구현은 src/app/clusters/dishwasher-alarm-server/DishwasherAlarmCluster.cpp와
mode-base-server/ModeBaseCluster.cpp, operational-state-server/OperationalStateCluster.cpp다.
세탁기와 요구 구조가 유사하므로 초기 3종의 다양성을 늘리는 효과는 상대적으로 작다.

### Laundry Dryer

필수 Operational State 및 OperationCompletion; 선택 Identify/OnOff/Laundry Dryer Controls(0x004A)/
Laundry Washer Mode(0x0051)/Temperature Control.
건조기에서 Laundry Washer Mode를 사용하는 관계는 추정이 아니라 LaundryDryer.xml의 실제 선언이다.
정의는 data_model/1.7/clusters/LaundryDryerControls.xml,
SDK 정의는 src/app/zap-templates/zcl/data-model/chip/laundry-dryer-controls-cluster.xml.
IDL/ZAP는 examples/chef/devices/rootnode_laundrydryer_01796fe396.matter 및 .zap.
구현은 src/app/clusters/laundry-dryer-controls-server/LaundryDryerControlsCluster.cpp.
Chef 사용 문서와 공유 Mode/Operational State 문서는 있지만 건조기 상세 설명 Coverage는 unverified다.
세탁기와의 공유 기능 비교용 후속 후보로 둔다.

## 7. 추천과 선정 전 확인 사항

기본 추천은 **Laundry Washer + Room Air Conditioner + Refrigerator(냉각 Cabinet 포함)**이다.
2종으로 시작하면 Laundry Washer와 Room Air Conditioner를 우선 조사 범위로 삼고,
구성 관계를 포함한 복합 추론이 핵심일 때 냉장고 제품군을 추가하는 것이 적합하다.
이는 파일 근거의 다양성과 범위에 대한 판단이며 최종 선정·성능 검증 결과가 아니다.
문서 확보와 단순한 초기 범위를 우선하면 Air Purifier를 Room AC 대신 검토할 수 있다.

선정 전에 다음을 해소해야 한다.

1. 1.7의 provisional 상태와 원본 spec tag, SDK/예제 Revision 차이를 고려하여 baseline을 확정한다.
2. 상세 Cluster prose가 unverified인 행을 보완한다. 앱 설치 문서·ID 표만으로 기능 설명 Coverage를 충족했다고 보지 않는다.
3. 냉장고의 Cooler 조건과 Cabinet endpoint 범위, Base/Root 공통 의존을 scope에 명시한다.
4. 공유 Mode/Alarm 기반 코드·delegate 및 조건부 기능까지 어디까지 포함할지 정한다.
5. 사양 XML의 파일별 이용 조건을 확인하고 외부 사양 문서 필요 여부를 정한다.
6. Token 수/Context 적합성은 이번에 측정하지 않았다. 추출·컴파일이 허용되는 다음 단계에서 평가한다.

현재 PLAN의 구조상 보완점은 repository_structure.md 7절에 정리했다.
이번 단계의 산출물은 조사 문서 2개와 Coverage 초안이며 원본 Corpus/정규화 자료/색인은 생성하지 않았다.
