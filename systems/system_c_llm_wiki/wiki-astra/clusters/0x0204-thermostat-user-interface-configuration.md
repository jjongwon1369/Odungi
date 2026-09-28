---
entity: Thermostat User Interface Configuration
ids: ['0x0204']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/README.md', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h', 'data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Thermostat User Interface Configuration

## 개요

Thermostat User Interface Configuration은 온도조절기의 사용자 인터페이스를 구성하는 클러스터이다. 사용자 인터페이스는 온도조절기와 떨어져 있을 수 있다.

- 클러스터 ID: `0x0204`
- 도메인: `HVAC`
- 리비전: `2`
- 주요 속성: `TemperatureDisplayMode`, `KeypadLockout`, `ScheduleProgrammingVisibility`
- 서버 구현: `ThermostatUserInterfaceConfigurationCluster`

`ThermostatUserInterfaceConfigurationCluster`는 속성 값을 클러스터 인스턴스에 저장하는 코드 기반 서버 클러스터이다. 애플리케이션은 타입이 지정된 getter와 setter로 현재 상태에 접근하고, `Delegate`로 값 변경을 통지받는다.

## 스펙

출처: `data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml`

### 분류 및 리비전

| 항목 | 값 |
|---|---|
| 이름 | `Thermostat User Interface Configuration Cluster` |
| 클러스터 ID | `0x0204` |
| revision | `2` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `TSUIC` |
| scope | `Endpoint` |

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | 새로운 데이터 모델 형식과 표기법 적용, “Conversion of Temperature Values for Display” 섹션 추가 |

제공된 XML에는 온도 표시 변환 절차의 본문이 포함되어 있지 않다.

### 속성

모든 속성은 읽기와 쓰기를 지원하며, 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 적합성 | 쓰기 권한 | 명시된 기본값 |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureDisplayMode` | `TemperatureDisplayModeEnum` | 필수 | `operate` | 명시 없음 |
| `0x0001` | `KeypadLockout` | `KeypadLockoutEnum` | 필수 | `manage` | 명시 없음 |
| `0x0002` | `ScheduleProgrammingVisibility` | `ScheduleProgrammingVisibilityEnum` | 선택 | `manage` | `ScheduleProgrammingPermitted` |

### 열거형

아래 열거형의 모든 항목은 스펙에서 필수로 정의되어 있다.

#### `TemperatureDisplayModeEnum`

| 스펙 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Celsius` | 온도를 °C로 표시 |
| `1` | `Fahrenheit` | 온도를 °F로 표시 |

#### `KeypadLockoutEnum`

| 스펙 값 | 이름 | 의미 |
|---|---|---|
| `0` | `NoLockout` | 사용자가 모든 기능을 사용할 수 있음 |
| `1` | `Lockout1` | 수준 1의 기능 제한 |
| `2` | `Lockout2` | 수준 2의 기능 제한 |
| `3` | `Lockout3` | 수준 3의 기능 제한 |
| `4` | `Lockout4` | 수준 4의 기능 제한 |
| `5` | `Lockout5` | 사용자가 사용할 수 있는 기능이 가장 적음 |

#### `ScheduleProgrammingVisibilityEnum`

| 스펙 값 | 이름 | 의미 |
|---|---|---|
| `0` | `ScheduleProgrammingPermitted` | 온도조절기의 로컬 일정 설정 기능 활성화 |
| `1` | `ScheduleProgrammingDenied` | 온도조절기의 로컬 일정 설정 기능 비활성화 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| name | `Thermostat User Interface Configuration` |
| domain | `HVAC` |
| code | `0x0204` |
| define | `THERMOSTAT_USER_INTERFACE_CONFIGURATION_CLUSTER` |
| client | `true`, `tick="false"`, `init="false"` |
| server | `true`, `tick="false"`, `tickFrequency="half"`, `init="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="2"` |

이 XML은 Alchemy가 생성한 파일이며, 직접 수정하지 않도록 표시되어 있다.

- 생성 원본: `src/app_clusters/ThermostatUserInterfaceConfiguration.adoc`
- Git: `0.9.2-summer2025-124-g2b25c360b`

### 서버 속성 정의

모든 속성은 `side="server"` 및 `writable="true"`로 정의되어 있다.

| code | name | define | type | max |
|---|---|---|---|---|
| `0x0000` | `TemperatureDisplayMode` | `TEMPERATURE_DISPLAY_MODE` | `TemperatureDisplayModeEnum` | `0x01` |
| `0x0001` | `KeypadLockout` | `KEYPAD_LOCKOUT` | `KeypadLockoutEnum` | `0x05` |
| `0x0002` | `ScheduleProgrammingVisibility` | `SCHEDULE_PROGRAMMING_VISIBILITY` | `ScheduleProgrammingVisibilityEnum` | `0x01` |

- `KeypadLockout`과 `ScheduleProgrammingVisibility`에는 `op="write"`, `role="manage"`가 명시되어 있다.
- `ScheduleProgrammingVisibility`는 `optionalConform`이며, 기본값은 `0x00`이다.
- `ScheduleProgrammingVisibility`의 `introducedIn`은 `ha-1.2-05-3520-29`이다.

### 열거형 표현

세 열거형 모두 `enum8`이며, 클러스터 `0x0204`에 연결된다.

| 타입 | SDK 항목과 값 |
|---|---|
| `TemperatureDisplayModeEnum` | `Celsius` = `0x00`, `Fahrenheit` = `0x01` |
| `KeypadLockoutEnum` | `NoLockout` = `0x00`, `Lockout1` = `0x01`, `Lockout2` = `0x02`, `Lockout3` = `0x03`, `Lockout4` = `0x04`, `Lockout5` = `0x05` |
| `ScheduleProgrammingVisibilityEnum` | `ScheduleProgrammingPermitted` = `0x00`, `ScheduleProgrammingDenied` = `0x01` |

## 구현

### 구성 파일

| 파일 | 역할 |
|---|---|
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h` | 클러스터 클래스, `Config`, 속성 접근 API 선언 |
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp` | 속성 목록, 읽기·쓰기, 값 검증 및 변경 통지 |
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h` | 변경 통지용 `Delegate` 정의 |
| `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h` | 인스턴스 조회 및 현재 속성 값 접근 API 선언 |
| `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp` | 서버 등록·해제와 접근 API 구현 |

### 인스턴스 구성과 초기값

`chip::app::Clusters`의 `ThermostatUserInterfaceConfigurationCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 `EndpointId endpointId`와 `const Config & config`를 받으며, `config`의 기본 인수는 `{}`이다.

| `Config` 필드 | 생성자 기본값 |
|---|---|
| `temperatureDisplayMode` | `ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum::kCelsius` |
| `keypadLockout` | `ThermostatUserInterfaceConfiguration::KeypadLockoutEnum::kNoLockout` |
| `scheduleProgrammingVisibility` | `ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted` |
| `optionalAttributes` | `{}` |

`OptionalAttributeSet`의 대상은 `ThermostatUserInterfaceConfiguration::Attributes::ScheduleProgrammingVisibility::Id`이다. 이 속성을 노출하려면 인스턴스 생성 시 `Config::optionalAttributes`에서 활성화해야 한다.

생성자는 구성 값을 `mTemperatureDisplayMode`, `mKeypadLockout`, `mScheduleProgrammingVisibility`에 저장하고, 선택 속성 구성을 `mOptionalAttributes`에 저장한다.

### 속성 목록과 읽기

`Attributes()`는 `AttributeListBuilder`를 사용해 `kMandatoryMetadata`와 선택 속성 `ScheduleProgrammingVisibility::kMetadataEntry`를 `mOptionalAttributes`에 따라 추가한다.

`ReadAttribute()`의 처리는 다음과 같다.

| 속성 | 반환하는 값 |
|---|---|
| `ClusterRevision::Id` | `kRevision` |
| `FeatureMap::Id` | `static_cast<uint32_t>(0)` |
| `TemperatureDisplayMode::Id` | `mTemperatureDisplayMode` |
| `KeypadLockout::Id` | `mKeypadLockout` |
| `ScheduleProgrammingVisibility::Id` | `mScheduleProgrammingVisibility` |
| 그 외 | `Status::UnsupportedAttribute` |

### 쓰기와 애플리케이션 접근

`WriteAttribute()`는 `decoder.Decode(value)`로 해당 열거형 값을 디코딩한 후 setter를 호출한다. 디코딩 실패는 `ReturnErrorOnFailure`로 반환하며, 처리 대상이 아닌 속성에는 `Status::UnsupportedAttribute`를 반환한다.

| 속성 | getter | setter |
|---|---|---|
| `TemperatureDisplayMode` | `GetTemperatureDisplayMode()` | `SetTemperatureDisplayMode()` |
| `KeypadLockout` | `GetKeypadLockout()` | `SetKeypadLockout()` |
| `ScheduleProgrammingVisibility` | `GetScheduleProgrammingVisibility()` | `SetScheduleProgrammingVisibility()` |

각 setter는 다음 순서로 동작한다.

1. `EnsureKnownEnumValue(value)`로 값을 확인한다.
2. 해당 열거형의 `kUnknownEnumValue`이면 `Status::ConstraintError`를 반환한다.
3. `SetAttributeValue`로 값을 갱신한다.
4. 값이 변경되었고 `mDelegate != nullptr`이면 해당 콜백을 호출한다.
5. 유효한 값에 대해 `Status::Success`를 반환한다.

### 변경 통지와 `Delegate`

`chip::app::Clusters::ThermostatUserInterfaceConfiguration`의 `Delegate`는 다음 콜백을 제공한다. 기본 구현은 아무 작업도 하지 않으므로 필요한 콜백만 재정의할 수 있다.

| 콜백 | 인수 타입 |
|---|---|
| `OnTemperatureDisplayModeChanged()` | `TemperatureDisplayModeEnum` |
| `OnKeypadLockoutChanged()` | `KeypadLockoutEnum` |
| `OnScheduleProgrammingVisibilityChanged()` | `ScheduleProgrammingVisibilityEnum` |

`SetDelegate()`로 delegate를 연결한다.

- 콜백은 새 값이 저장된 후 동기적으로 실행된다.
- 값을 변경하는 Matter 쓰기와 애플리케이션 setter 호출 모두에 적용된다.
- 유효하지 않은 값이나 현재 값과 동일한 값의 쓰기는 콜백을 발생시키지 않는다.
- 콜백은 통지용이며 변경을 거부할 수 없다.
- 초기 구성과 delegate 연결은 콜백을 발생시키지 않는다. 초기 UI 상태가 필요하면 getter를 사용한다.
- 이 클러스터는 기존 `MatterPostAttributeChangeCallback`을 호출하지 않는다. 해당 콜백에서 처리하던 로직은 delegate로 옮겨야 한다.

delegate는 애플리케이션이 소유한다. 연결된 동안 유지하거나, 파괴 전에 `SetDelegate(nullptr)`로 분리해야 한다. 클러스터 인스턴스마다 delegate 포인터는 하나이며, 콜백은 값만 받고 endpoint ID는 받지 않는다. endpoint별 상태가 필요하면 별도 delegate 인스턴스를 사용한다.

### 코드 생성 통합과 수명 주기

`CodegenIntegration.cpp`는 `LazyRegisteredServerCluster<ThermostatUserInterfaceConfigurationCluster>` 배열인 `gServers`를 관리한다.

- `kFixedClusterCount`: `ThermostatUserInterfaceConfiguration::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kMaxClusterCount`: `kFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`

`IntegrationDelegate::CreateRegistration()`은 다음 작업을 수행한다.

1. `optionalAttributeBits`로 `config.optionalAttributes`를 구성한다.
2. `TemperatureDisplayMode::GetDefaultOr()`와 `KeypadLockout::GetDefaultOr()`로 시작 값을 읽는다.
3. `ScheduleProgrammingVisibility::Id`가 선택된 경우에만 `ScheduleProgrammingVisibility::GetDefaultOr()`로 시작 값을 읽는다.
4. `gServers[clusterInstanceIndex].Create(endpointId, config)`로 인스턴스를 생성하고 `Registration()`을 반환한다.

`GetDefaultOr()`에 전달되는 대체 값은 각각 `TemperatureDisplayModeEnum::kCelsius`, `KeypadLockoutEnum::kNoLockout`, `ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted`이다.

| 함수 | 동작 |
|---|---|
| `MatterThermostatUserInterfaceConfigurationClusterInitCallback()` | `CodegenClusterIntegration::RegisterServer()` 호출 |
| `MatterThermostatUserInterfaceConfigurationClusterShutdownCallback()` | `CodegenClusterIntegration::UnregisterServer()` 호출 |
| `FindClusterOnEndpoint()` | endpoint에 등록된 클러스터 조회 |
| `IntegrationDelegate::FindRegistration()` | 생성된 인스턴스를 반환하고, 미생성 상태이면 `nullptr` 반환 |
| `IntegrationDelegate::ReleaseRegistration()` | `Destroy()` 호출 |

등록 시 `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true`이다.

### 현재 값과 시작 기본값의 구분

`CodegenIntegration.h`의 `Attributes` 아래에는 `TemperatureDisplayMode`, `KeypadLockout`, `ScheduleProgrammingVisibility` 각각의 `Get()`과 `Set()`이 선언되어 있다.

- `Get()`은 실행 중인 클러스터의 getter로 현재 값을 읽는다.
- `Set()`은 실행 중인 클러스터의 setter를 호출한다.
- `FindClusterOnEndpoint()`가 `nullptr`을 반환하면 `Protocols::InteractionModel::Status::UnsupportedEndpoint`를 반환한다.
- 생성된 `GetDefault()`는 현재 클러스터 상태가 아니라 ZAP/Ember 속성 저장소의 시작 기본값을 읽는다. 선언 파일은 `app-common/zap-generated/attributes/Accessors.h`이다.

### 애플리케이션 연결 절차

**ZAP 애플리케이션**

클러스터 등록 후 `CodegenIntegration.h`의 `FindClusterOnEndpoint()`로 인스턴스를 찾고 `SetDelegate()`를 호출한다. 이 작업은 Matter 스레드에서 수행하거나 스택 잠금을 보유한 상태에서 수행해야 한다. endpoint와 클러스터 인스턴스가 재생성되면 delegate를 다시 연결해야 한다.

**클러스터를 직접 생성하는 애플리케이션**

endpoint와 `Config`로 `ThermostatUserInterfaceConfigurationCluster`를 생성하고, `SetDelegate()`로 delegate를 연결한 뒤 애플리케이션의 데이터 모델 제공자에 등록한다. 이 경우 `CodegenIntegration` 조회는 필요하지 않다.

## 관련 문서

- `src/app/clusters/thermostat-user-interface-configuration-server/README.md`
  - 코드 기반 서버의 속성 저장 모델, delegate 동작, ZAP 애플리케이션 연결 및 직접 생성 시 수명 주기를 설명한다.
  - `ThermostatUiDelegate`와 `AttachThermostatUiDelegate()`를 사용하는 delegate 연결 코드가 포함되어 있다.
- [cluster development guide](../../../../docs/guides/writing_clusters.md)
  - README에서 클러스터 등록 및 수명 주기 모델의 참조 문서로 안내한다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
