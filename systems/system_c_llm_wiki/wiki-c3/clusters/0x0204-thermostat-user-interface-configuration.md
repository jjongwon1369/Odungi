---
entity: Thermostat User Interface Configuration
ids: ['0x0204']
source_paths: ['data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h', 'src/app/clusters/thermostat-user-interface-configuration-server/README.md', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h', 'src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Thermostat User Interface Configuration

## 개요

Thermostat User Interface Configuration은 온도 조절기의 사용자 인터페이스를 구성하는 클러스터이다. 사용자 인터페이스는 온도 조절기와 떨어진 위치에 있을 수 있다.

- 클러스터 ID: `0x0204`
- 리비전: `2`
- 주요 속성: `TemperatureDisplayMode`, `KeypadLockout`, `ScheduleProgrammingVisibility`
- 서버 구현: `ThermostatUserInterfaceConfigurationCluster`
- 구현 방식: 속성 값을 클러스터 인스턴스에 저장하고, 타입이 지정된 getter와 setter로 접근하는 code-driven 서버 클러스터

## 스펙

출처: `data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Thermostat User Interface Configuration Cluster` |
| 클러스터 ID | `0x0204` |
| 리비전 | `2` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `TSUIC` |
| scope | `Endpoint` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | 새로운 데이터 모델 형식과 표기법 적용, “Conversion of Temperature Values for Display” 섹션 추가 |

제공된 XML에는 온도 표시 변환의 구체적인 규칙은 포함되어 있지 않다.

### 속성

| ID | 이름 | 타입 | 적합성 | 읽기 권한 | 쓰기 권한 | 명시된 기본값 |
|---|---|---|---|---|---|---|
| `0x0000` | `TemperatureDisplayMode` | `TemperatureDisplayModeEnum` | 필수 | `view` | `operate` | 명시 없음 |
| `0x0001` | `KeypadLockout` | `KeypadLockoutEnum` | 필수 | `view` | `manage` | 명시 없음 |
| `0x0002` | `ScheduleProgrammingVisibility` | `ScheduleProgrammingVisibilityEnum` | 선택 | `view` | `manage` | `ScheduleProgrammingPermitted` |

세 속성 모두 읽기와 쓰기를 지원한다.

### 데이터 타입

각 enum의 나열된 항목은 모두 필수로 정의되어 있다.

#### `TemperatureDisplayModeEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Celsius` | 온도를 °C로 표시 |
| `1` | `Fahrenheit` | 온도를 °F로 표시 |

#### `KeypadLockoutEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `NoLockout` | 사용자가 모든 기능을 사용할 수 있음 |
| `1` | `Lockout1` | 수준 1의 기능 제한 |
| `2` | `Lockout2` | 수준 2의 기능 제한 |
| `3` | `Lockout3` | 수준 3의 기능 제한 |
| `4` | `Lockout4` | 수준 4의 기능 제한 |
| `5` | `Lockout5` | 사용자가 사용할 수 있는 기능이 가장 적음 |

#### `ScheduleProgrammingVisibilityEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `ScheduleProgrammingPermitted` | 온도 조절기의 로컬 일정 프로그래밍 기능 활성화 |
| `1` | `ScheduleProgrammingDenied` | 온도 조절기의 로컬 일정 프로그래밍 기능 비활성화 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml`

### ZAP 클러스터 정의

| 항목 | 값 |
|---|---|
| name | `Thermostat User Interface Configuration` |
| domain | `HVAC` |
| code | `0x0204` |
| define | `THERMOSTAT_USER_INTERFACE_CONFIGURATION_CLUSTER` |
| 전역 속성 | `0xFFFD`, 값 `2`, side `either` |

- `client`와 `server`가 모두 활성화되어 있다.
- `client` 설정은 `tick="false"`, `init="false"`이다.
- `server` 설정은 `tick="false"`, `tickFrequency="half"`, `init="false"`이다.
- 파일은 Alchemy로 생성되었으며 `DO NOT EDIT`로 표시되어 있다.
- 생성 원본으로 `src/app_clusters/ThermostatUserInterfaceConfiguration.adoc`가 명시되어 있다.

### 속성 정의

모든 속성은 `side="server"`, `writable="true"`로 정의된다.

| code | name | define | type | max | 추가 설정 |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureDisplayMode` | `TEMPERATURE_DISPLAY_MODE` | `TemperatureDisplayModeEnum` | `0x01` | — |
| `0x0001` | `KeypadLockout` | `KEYPAD_LOCKOUT` | `KeypadLockoutEnum` | `0x05` | 쓰기 역할 `manage` |
| `0x0002` | `ScheduleProgrammingVisibility` | `SCHEDULE_PROGRAMMING_VISIBILITY` | `ScheduleProgrammingVisibilityEnum` | `0x01` | 선택 속성, 쓰기 역할 `manage`, 기본값 `0x00`, `introducedIn="ha-1.2-05-3520-29"` |

### enum 정의

세 enum은 모두 `enum8`이며 클러스터 `0x0204`에 연결된다.

| 타입 | 항목과 SDK 값 |
|---|---|
| `TemperatureDisplayModeEnum` | `Celsius` = `0x00`, `Fahrenheit` = `0x01` |
| `KeypadLockoutEnum` | `NoLockout` = `0x00`, `Lockout1` = `0x01`, `Lockout2` = `0x02`, `Lockout3` = `0x03`, `Lockout4` = `0x04`, `Lockout5` = `0x05` |
| `ScheduleProgrammingVisibilityEnum` | `ScheduleProgrammingPermitted` = `0x00`, `ScheduleProgrammingDenied` = `0x01` |

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h` | 서버 클래스, `Config`, 속성 접근 API 선언 |
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp` | 속성 목록, 읽기·쓰기, enum 검증, 변경 알림 구현 |
| `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h` | `Delegate`와 변경 콜백 정의 |
| `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h` | 클러스터 조회 및 런타임 속성 접근 API 선언 |
| `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp` | 서버 등록·해제, 초기값 로딩, 속성 접근 연동 |

### 서버 클래스와 초기 구성

`chip::app::Clusters`의 `ThermostatUserInterfaceConfigurationCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 `EndpointId`와 `Config`를 받아 클러스터 인스턴스를 구성한다.

| `Config` 필드 | 기본값 |
|---|---|
| `temperatureDisplayMode` | `ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum::kCelsius` |
| `keypadLockout` | `ThermostatUserInterfaceConfiguration::KeypadLockoutEnum::kNoLockout` |
| `scheduleProgrammingVisibility` | `ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted` |
| `optionalAttributes` | `{}` |

`OptionalAttributeSet`이 대상으로 삼는 선택 속성은 `ThermostatUserInterfaceConfiguration::Attributes::ScheduleProgrammingVisibility::Id`이다. 이 속성을 노출하려면 인스턴스 생성 시 `Config::optionalAttributes`에서 활성화해야 한다.

생성자는 구성 값을 `mTemperatureDisplayMode`, `mKeypadLockout`, `mScheduleProgrammingVisibility`에 저장한다. `mOptionalAttributes`는 `const`이며, `mDelegate`의 초기값은 `nullptr`이다.

### 속성 목록과 읽기·쓰기

- `Attributes()`는 `AttributeListBuilder`를 사용해 `kMandatoryMetadata`와 선택 속성 메타데이터를 결합한다. `ScheduleProgrammingVisibility::kMetadataEntry`의 포함 여부는 `mOptionalAttributes`로 결정된다.
- `ReadAttribute()`는 다음 값을 인코딩한다.
  - `ClusterRevision::Id`: `kRevision`
  - `FeatureMap::Id`: `static_cast<uint32_t>(0)`
  - 세 구성 속성: 해당 인스턴스에 저장된 값
- `WriteAttribute()`는 입력을 각 enum 타입으로 디코딩한 뒤 대응하는 setter를 호출한다.
- 두 메서드의 `switch`에서 처리하지 않는 속성은 `Status::UnsupportedAttribute`를 반환한다.

### 타입 지정 접근 API

| 속성 | getter | setter |
|---|---|---|
| `TemperatureDisplayMode` | `GetTemperatureDisplayMode()` | `SetTemperatureDisplayMode()` |
| `KeypadLockout` | `GetKeypadLockout()` | `SetKeypadLockout()` |
| `ScheduleProgrammingVisibility` | `GetScheduleProgrammingVisibility()` | `SetScheduleProgrammingVisibility()` |

setter의 공통 처리 순서는 다음과 같다.

1. `EnsureKnownEnumValue()`로 enum 값을 검증한다.
2. 해당 enum의 `kUnknownEnumValue`이면 `Status::ConstraintError`를 반환한다.
3. `SetAttributeValue()`로 값을 갱신한다.
4. 값이 변경되었고 `mDelegate != nullptr`이면 대응하는 변경 콜백을 호출한다.
5. 유효한 값에 대해서는 `Status::Success`를 반환한다.

### 변경 알림

`chip::app::Clusters::ThermostatUserInterfaceConfiguration`의 `Delegate`는 다음 콜백을 제공한다. 기본 구현은 아무 작업도 하지 않으므로 필요한 콜백만 재정의할 수 있다.

| 콜백 | 전달 타입 |
|---|---|
| `OnTemperatureDisplayModeChanged()` | `TemperatureDisplayModeEnum` |
| `OnKeypadLockoutChanged()` | `KeypadLockoutEnum` |
| `OnScheduleProgrammingVisibilityChanged()` | `ScheduleProgrammingVisibilityEnum` |

`SetDelegate()`로 delegate를 연결한다.

- 콜백은 새 값이 저장된 후 동기적으로 실행된다.
- 실제 값을 변경하는 Matter 쓰기와 애플리케이션 setter 호출 모두에 적용된다.
- 잘못된 값이나 현재 값과 동일한 값의 쓰기는 콜백을 발생시키지 않는다.
- 콜백은 알림용이며 변경을 거부할 수 없다.
- 초기 구성이나 delegate 연결만으로는 콜백이 발생하지 않는다. UI 초기화에는 getter를 사용한다.
- 이 클러스터는 기존 `MatterPostAttributeChangeCallback`을 호출하지 않는다. 해당 콜백에서 수행하던 처리는 delegate로 이전해야 한다.

애플리케이션이 delegate를 소유한다. 연결된 동안 생존을 유지하거나, 파괴 전에 `SetDelegate(nullptr)`로 분리해야 한다. 인스턴스마다 delegate 포인터는 하나이며, 콜백에는 값만 전달되고 endpoint ID는 전달되지 않는다. endpoint별 상태가 필요하면 별도의 delegate 인스턴스를 사용한다.

### Codegen 등록과 수명 주기

`CodegenIntegration.cpp`는 다음과 같이 서버 저장 공간을 구성한다.

- `kFixedClusterCount`: `ThermostatUserInterfaceConfiguration::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kMaxClusterCount`: `kFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: `LazyRegisteredServerCluster<ThermostatUserInterfaceConfigurationCluster>` 배열

`IntegrationDelegate::CreateRegistration()`은 다음 작업을 수행한다.

1. `optionalAttributeBits`로 `config.optionalAttributes`를 구성한다.
2. `TemperatureDisplayMode::GetDefaultOr()`와 `KeypadLockout::GetDefaultOr()`로 초기값을 읽는다.
3. `ScheduleProgrammingVisibility::Id`가 선택 속성 집합에 있으면 `ScheduleProgrammingVisibility::GetDefaultOr()`로 초기값을 읽는다.
4. `gServers[clusterInstanceIndex].Create()`로 인스턴스를 생성하고 `Registration()`을 반환한다.

초기값을 읽을 수 없을 때의 대체값은 각각 `TemperatureDisplayModeEnum::kCelsius`, `KeypadLockoutEnum::kNoLockout`, `ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted`이다.

| 함수 | 처리 |
|---|---|
| `MatterThermostatUserInterfaceConfigurationClusterInitCallback()` | `CodegenClusterIntegration::RegisterServer()` 호출 |
| `MatterThermostatUserInterfaceConfigurationClusterShutdownCallback()` | `CodegenClusterIntegration::UnregisterServer()` 호출 |
| `FindClusterOnEndpoint()` | `CodegenClusterIntegration::FindClusterOnEndpoint()`를 통해 서버 인스턴스 조회 |
| `IntegrationDelegate::FindRegistration()` | 생성된 인스턴스를 반환하며, 미생성 상태이면 `nullptr` 반환 |
| `IntegrationDelegate::ReleaseRegistration()` | 해당 인스턴스의 `Destroy()` 호출 |

등록 시 `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true`이다.

### 런타임 접근과 시작 기본값의 구분

`CodegenIntegration.h`는 `Attributes` 아래의 `TemperatureDisplayMode`, `KeypadLockout`, `ScheduleProgrammingVisibility` 네임스페이스에 `Get()`과 `Set()`을 선언한다.

- `Get()`은 현재 클러스터 인스턴스의 getter로 값을 읽고 `Protocols::InteractionModel::Status::Success`를 반환한다.
- `Set()`은 현재 클러스터 인스턴스의 setter를 호출하고 그 결과를 반환한다.
- 클러스터를 찾지 못하면 두 함수 모두 `Protocols::InteractionModel::Status::UnsupportedEndpoint`를 반환한다.

반면 `app-common/zap-generated/attributes/Accessors.h`의 생성된 `GetDefault()`는 런타임 상태가 아니라 ZAP/Ember 속성 저장소의 시작 기본값을 읽는다.

### 애플리케이션 연결 방식

**ZAP 애플리케이션**

클러스터 등록 이후 `CodegenIntegration.h`의 `FindClusterOnEndpoint()`로 인스턴스를 찾고 `SetDelegate()`를 호출한다. 이 작업은 Matter 스레드에서 수행하거나 stack lock을 보유한 상태에서 수행해야 한다. endpoint와 클러스터 인스턴스가 다시 생성되면 delegate도 다시 연결해야 한다.

**직접 인스턴스를 생성하는 애플리케이션**

endpoint와 `Config`로 `ThermostatUserInterfaceConfigurationCluster`를 생성하고, `SetDelegate()`로 delegate를 연결한 다음 애플리케이션의 data model provider에 인스턴스를 등록한다. 이 방식에서는 `CodegenIntegration` 조회가 필요하지 않다.

## 관련 문서

- `src/app/clusters/thermostat-user-interface-configuration-server/README.md`
  - code-driven 서버의 속성 접근 방식
  - 변경 콜백과 `MatterPostAttributeChangeCallback` 이전 지침
  - ZAP 애플리케이션의 `ThermostatUiDelegate` 및 `AttachThermostatUiDelegate()` 코드
  - 직접 생성한 클러스터의 등록과 delegate 수명 관리
- [cluster development guide](../../../../docs/guides/writing_clusters.md)
  - README에서 클러스터 등록 및 수명 주기 모델의 참고 문서로 연결한다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
