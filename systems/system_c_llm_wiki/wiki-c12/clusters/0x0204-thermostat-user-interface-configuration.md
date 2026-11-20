---
entity: Thermostat User Interface Configuration
ids: ['0x0204']
source_paths: ['data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h', 'src/app/clusters/thermostat-user-interface-configuration-server/README.md', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h', 'src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Thermostat User Interface Configuration

## 개요

Thermostat User Interface Configuration은 온도 조절기의 사용자 인터페이스를 구성하는 클러스터다. 사용자 인터페이스는 온도 조절기와 떨어진 위치에 있을 수도 있다.

- 클러스터 ID: `0x0204`
- 리비전: `2`
- 주요 속성: `TemperatureDisplayMode`, `KeypadLockout`, `ScheduleProgrammingVisibility`
- 서버 구현: `ThermostatUserInterfaceConfigurationCluster`
- 속성값은 클러스터 인스턴스에 저장되며, 애플리케이션은 타입이 지정된 getter와 setter로 접근한다.
- `Config`는 초기 속성값과 선택 속성의 사용 여부를 지정한다.

## 스펙

출처: `data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 이름 | `Thermostat User Interface Configuration Cluster` |
| 클러스터 ID | `0x0204` |
| 클러스터 ID 이름 | `Thermostat User Interface Configuration` |
| 리비전 | `2` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `TSUIC` |
| scope | `Endpoint` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | 새 데이터 모델 형식 및 표기법 적용, “Conversion of Temperature Values for Display” 섹션 추가 |

제공된 XML에는 온도 표시값 변환에 관한 구체적인 규칙은 포함되어 있지 않다.

### 데이터 타입

아래 열거형의 모든 항목은 필수다.

| 타입 | 값 | 이름 | 의미 |
|---|---|---|---|
| `KeypadLockoutEnum` | `0` | `NoLockout` | 사용자가 모든 기능을 사용할 수 있음 |
| `KeypadLockoutEnum` | `1` | `Lockout1` | 수준 1의 기능 제한 |
| `KeypadLockoutEnum` | `2` | `Lockout2` | 수준 2의 기능 제한 |
| `KeypadLockoutEnum` | `3` | `Lockout3` | 수준 3의 기능 제한 |
| `KeypadLockoutEnum` | `4` | `Lockout4` | 수준 4의 기능 제한 |
| `KeypadLockoutEnum` | `5` | `Lockout5` | 사용자가 사용할 수 있는 기능이 가장 적음 |
| `ScheduleProgrammingVisibilityEnum` | `0` | `ScheduleProgrammingPermitted` | 온도 조절기에서 로컬 일정 프로그래밍 기능 활성화 |
| `ScheduleProgrammingVisibilityEnum` | `1` | `ScheduleProgrammingDenied` | 온도 조절기에서 로컬 일정 프로그래밍 기능 비활성화 |
| `TemperatureDisplayModeEnum` | `0` | `Celsius` | 온도를 °C로 표시 |
| `TemperatureDisplayModeEnum` | `1` | `Fahrenheit` | 온도를 °F로 표시 |

### 속성

모든 속성은 읽기와 쓰기를 지원한다.

| ID | 이름 | 타입 | 적합성 | 읽기 권한 | 쓰기 권한 | 명시된 기본값 |
|---|---|---|---|---|---|---|
| `0x0000` | `TemperatureDisplayMode` | `TemperatureDisplayModeEnum` | 필수 | `view` | `operate` | 없음 |
| `0x0001` | `KeypadLockout` | `KeypadLockoutEnum` | 필수 | `view` | `manage` | 없음 |
| `0x0002` | `ScheduleProgrammingVisibility` | `ScheduleProgrammingVisibilityEnum` | 선택 | `view` | `manage` | `ScheduleProgrammingPermitted` |

제공된 스펙 XML에는 명령 및 이벤트 정의가 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml`

### 클러스터 설정

| 항목 | 정의 |
|---|---|
| 이름 | `Thermostat User Interface Configuration` |
| 도메인 | `HVAC` |
| 코드 | `0x0204` |
| define | `THERMOSTAT_USER_INTERFACE_CONFIGURATION_CLUSTER` |
| client | 활성화, `tick="false"`, `init="false"` |
| server | 활성화, `tick="false"`, `tickFrequency="half"`, `init="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="2"`, `side="either"` |

이 XML은 Alchemy가 생성한 파일이며 직접 편집하지 않도록 명시되어 있다. 생성 원본은 `src/app_clusters/ThermostatUserInterfaceConfiguration.adoc`이다.

### 속성 매핑

모든 속성은 `side="server"` 및 `writable="true"`로 정의된다.

| 이름 | 코드 | define | 타입 | 최댓값 | 추가 설정 |
|---|---|---|---|---|---|
| `TemperatureDisplayMode` | `0x0000` | `TEMPERATURE_DISPLAY_MODE` | `TemperatureDisplayModeEnum` | `0x01` | — |
| `KeypadLockout` | `0x0001` | `KEYPAD_LOCKOUT` | `KeypadLockoutEnum` | `0x05` | 쓰기 역할 `manage` |
| `ScheduleProgrammingVisibility` | `0x0002` | `SCHEDULE_PROGRAMMING_VISIBILITY` | `ScheduleProgrammingVisibilityEnum` | `0x01` | 선택 속성, 쓰기 역할 `manage`, 기본값 `0x00`, `introducedIn="ha-1.2-05-3520-29"` |

### 열거형 표현

SDK의 세 열거형은 모두 `enum8`이며 클러스터 `0x0204`에 연결된다.

| 타입 | 항목과 값 |
|---|---|
| `KeypadLockoutEnum` | `NoLockout` = `0x00`, `Lockout1` = `0x01`, `Lockout2` = `0x02`, `Lockout3` = `0x03`, `Lockout4` = `0x04`, `Lockout5` = `0x05` |
| `ScheduleProgrammingVisibilityEnum` | `ScheduleProgrammingPermitted` = `0x00`, `ScheduleProgrammingDenied` = `0x01` |
| `TemperatureDisplayModeEnum` | `Celsius` = `0x00`, `Fahrenheit` = `0x01` |

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h` | 서버 클래스, `Config`, 속성 getter/setter 선언 |
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp` | 속성 목록, 읽기·쓰기, 값 검증 및 변경 알림 구현 |
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h` | 속성 변경 콜백 인터페이스 |
| `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h` | 클러스터 조회 및 런타임 속성 접근 함수 선언 |
| `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp` | 서버 등록·해제 및 런타임 속성 접근 구현 |

### 인스턴스와 초기 설정

`chip::app::Clusters`의 `ThermostatUserInterfaceConfigurationCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 `EndpointId`와 `Config`를 받아 속성값을 인스턴스에 저장한다.

| `Config` 멤버 | 기본값 | 저장 멤버 |
|---|---|---|
| `temperatureDisplayMode` | `ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum::kCelsius` | `mTemperatureDisplayMode` |
| `keypadLockout` | `ThermostatUserInterfaceConfiguration::KeypadLockoutEnum::kNoLockout` | `mKeypadLockout` |
| `scheduleProgrammingVisibility` | `ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted` | `mScheduleProgrammingVisibility` |
| `optionalAttributes` | 빈 집합 | `mOptionalAttributes` |

`OptionalAttributeSet`의 대상은 `ThermostatUserInterfaceConfiguration::Attributes::ScheduleProgrammingVisibility::Id`다. 해당 속성을 노출하려면 인스턴스 생성 시 `Config::optionalAttributes`에서 활성화해야 한다.

### 속성 목록과 읽기·쓰기

- `Attributes()`는 `AttributeListBuilder`로 `kMandatoryMetadata`와 선택 속성 메타데이터를 조합한다.
- 선택 속성 목록에는 `ScheduleProgrammingVisibility::kMetadataEntry`가 있으며, 포함 여부는 `mOptionalAttributes`로 결정된다.
- `ReadAttribute()`는 다음 값을 인코딩한다.
  - `ClusterRevision::Id`: `kRevision`
  - `FeatureMap::Id`: `static_cast<uint32_t>(0)`
  - `TemperatureDisplayMode::Id`: `mTemperatureDisplayMode`
  - `KeypadLockout::Id`: `mKeypadLockout`
  - `ScheduleProgrammingVisibility::Id`: `mScheduleProgrammingVisibility`
- `WriteAttribute()`는 속성별 열거형으로 값을 디코딩한 뒤 해당 setter를 호출한다. 디코딩 오류는 `ReturnErrorOnFailure`로 반환한다.
- 읽기·쓰기의 처리 대상이 아닌 속성 ID는 `Status::UnsupportedAttribute`를 반환한다.

선택 속성의 노출 여부는 속성 목록 생성에서 반영된다. 제공된 `ReadAttribute()`, `WriteAttribute()` 및 setter 내부에는 `mOptionalAttributes`를 확인하는 별도 분기가 없다.

### 런타임 접근과 값 검증

| 속성 | getter | setter | 변경 콜백 |
|---|---|---|---|
| `TemperatureDisplayMode` | `GetTemperatureDisplayMode()` | `SetTemperatureDisplayMode()` | `OnTemperatureDisplayModeChanged()` |
| `KeypadLockout` | `GetKeypadLockout()` | `SetKeypadLockout()` | `OnKeypadLockoutChanged()` |
| `ScheduleProgrammingVisibility` | `GetScheduleProgrammingVisibility()` | `SetScheduleProgrammingVisibility()` | `OnScheduleProgrammingVisibilityChanged()` |

각 setter는 다음 순서로 처리한다.

1. `EnsureKnownEnumValue()`로 값을 확인한다.
2. 해당 열거형의 `kUnknownEnumValue`이면 `Status::ConstraintError`를 반환한다.
3. `SetAttributeValue()`로 값을 설정한다.
4. 실제 값이 변경되었고 `mDelegate`가 `nullptr`가 아니면 대응하는 콜백을 호출한다.
5. `Status::Success`를 반환한다.

### 변경 알림과 수명 관리

`ThermostatUserInterfaceConfiguration::Delegate`를 구현하고 `SetDelegate()`로 연결한다. 콜백은 기본적으로 빈 구현이므로 필요한 함수만 재정의할 수 있다.

- 새 값이 저장된 뒤 동기적으로 호출된다.
- 값을 변경하는 Matter 쓰기와 애플리케이션 setter 호출 모두에 적용된다.
- 유효하지 않은 값이나 현재 값과 같은 값을 쓰는 경우에는 호출되지 않는다.
- 콜백은 알림 용도이며 변경을 거부할 수 없다.
- 초기 설정과 delegate 연결만으로는 호출되지 않는다. 초기 UI 상태가 필요하면 getter를 사용한다.
- 이 클러스터는 기존 `MatterPostAttributeChangeCallback`을 호출하지 않는다. 기존 처리는 delegate로 옮겨야 한다.

delegate는 애플리케이션이 소유한다. 연결된 동안 유지하거나, 파괴하기 전에 `SetDelegate(nullptr)`로 분리해야 한다. 클러스터 인스턴스당 delegate 포인터는 하나이며, 콜백은 새 값만 받고 endpoint ID는 받지 않는다. endpoint별 상태가 필요하면 별도 delegate 인스턴스를 사용한다.

### Codegen 등록과 해제

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

- `kFixedClusterCount`는 `ThermostatUserInterfaceConfiguration::StaticApplicationConfig::kFixedClusterConfig.size()`로 정한다.
- `kMaxClusterCount`는 `kFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`다.
- `gServers`는 `LazyRegisteredServerCluster<ThermostatUserInterfaceConfigurationCluster>` 배열이다.

`CreateRegistration()`은 다음을 수행한다.

1. `optionalAttributeBits`로 `config.optionalAttributes`를 구성한다.
2. `TemperatureDisplayMode::GetDefaultOr()`와 `KeypadLockout::GetDefaultOr()`로 초기값을 가져온다.
3. 선택 속성이 활성화된 경우 `ScheduleProgrammingVisibility::GetDefaultOr()`를 호출한다.
4. `gServers[clusterInstanceIndex].Create()`로 인스턴스를 만들고 `Registration()`을 반환한다.

기본값을 얻지 못했을 때 사용하는 값은 각각 `TemperatureDisplayModeEnum::kCelsius`, `KeypadLockoutEnum::kNoLockout`, `ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted`다.

| 함수 | 동작 |
|---|---|
| `MatterThermostatUserInterfaceConfigurationClusterInitCallback()` | `CodegenClusterIntegration::RegisterServer()` 호출. `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true` |
| `MatterThermostatUserInterfaceConfigurationClusterShutdownCallback()` | `shutdownType`을 전달하여 `CodegenClusterIntegration::UnregisterServer()` 호출 |
| `FindClusterOnEndpoint()` | `CodegenClusterIntegration::FindClusterOnEndpoint()`로 조회하고 `ThermostatUserInterfaceConfigurationCluster *`로 반환 |
| `FindRegistration()` | 인스턴스가 생성되지 않았으면 `nullptr`, 생성되었으면 클러스터 포인터 반환 |
| `ReleaseRegistration()` | 해당 인스턴스의 `Destroy()` 호출 |

### ZAP 애플리케이션 접근

`CodegenIntegration.h`의 `Attributes` 아래에는 `TemperatureDisplayMode`, `KeypadLockout`, `ScheduleProgrammingVisibility` 각각의 `Get()`과 `Set()`이 선언되어 있다.

- `Get()`은 클러스터 getter로 런타임 값을 읽고 `Protocols::InteractionModel::Status::Success`를 반환한다.
- `Set()`은 클러스터 setter의 결과를 반환한다.
- 클러스터를 찾지 못하면 두 함수 모두 `Protocols::InteractionModel::Status::UnsupportedEndpoint`를 반환한다.
- `app-common/zap-generated/attributes/Accessors.h`의 생성된 `GetDefault()`는 런타임 상태가 아니라 ZAP/Ember 속성 저장소의 시작 기본값을 읽는다.

delegate 연결은 클러스터 등록 이후 `FindClusterOnEndpoint()`로 인스턴스를 찾은 뒤 수행한다. 이 작업은 Matter 스레드에서 또는 스택 잠금을 보유한 상태에서 실행해야 한다. endpoint와 클러스터 인스턴스를 다시 생성하면 delegate도 다시 연결해야 한다.

### 직접 생성하는 애플리케이션

`ThermostatUserInterfaceConfigurationCluster`를 endpoint와 `Config`로 생성하고, `SetDelegate()`로 delegate를 연결한 뒤 애플리케이션의 데이터 모델 제공자에 등록한다. 이 경우 `CodegenIntegration` 조회는 필요하지 않다.

## 관련 문서

- `src/app/clusters/thermostat-user-interface-configuration-server/README.md`
  - 코드 기반 서버의 속성 저장 및 접근 방식
  - delegate 콜백의 실행 조건과 수명 관리
  - ZAP 애플리케이션의 `ThermostatUiDelegate` 및 `AttachThermostatUiDelegate()` 연결 코드
  - 직접 생성한 클러스터의 등록 방식
- [cluster development guide](../../../../docs/guides/writing_clusters.md)
  - README에서 클러스터 등록 및 수명 주기 모델을 위해 참조하는 문서

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Water Heater](../device-types/water-heater.md)
