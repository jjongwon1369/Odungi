---
entity: Thermostat User Interface Configuration
ids: ['0x0204']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/README.md', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h', 'data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Thermostat User Interface Configuration

## 개요

`Thermostat User Interface Configuration`은 온도 조절기의 사용자 인터페이스를 설정하기 위한 클러스터입니다. 온도 조절기와 원격으로 연결된 사용자 인터페이스에도 적용할 수 있습니다.

- 클러스터 ID: `0x0204`
- 도메인: `HVAC`
- PICS 코드: `TSUIC`
- 계층: `base`
- 역할: `application`
- 범위: `Endpoint`
- 서버 지원: 지원
- 클라이언트 지원: 지원
- 클러스터 revision: `2`
- define: `THERMOSTAT_USER_INTERFACE_CONFIGURATION_CLUSTER`

## 스펙

출처: `data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml`

### 속성

| ID | 이름 | 타입 | 접근 | 쓰기 권한 | 적합성 | 기본값 |
|---|---|---|---|---|---|---|
| `0x0000` | `TemperatureDisplayMode` | `TemperatureDisplayModeEnum` | 읽기/쓰기 | `operate` | 필수 | - |
| `0x0001` | `KeypadLockout` | `KeypadLockoutEnum` | 읽기/쓰기 | `manage` | 필수 | - |
| `0x0002` | `ScheduleProgrammingVisibility` | `ScheduleProgrammingVisibilityEnum` | 읽기/쓰기 | `manage` | 선택 | `ScheduleProgrammingPermitted` |

모든 속성의 읽기 권한은 `view`입니다.

### `TemperatureDisplayModeEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0` | `Celsius` | 온도를 °C로 표시 |
| `1` | `Fahrenheit` | 온도를 °F로 표시 |

### `KeypadLockoutEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0` | `NoLockout` | 사용자가 모든 기능을 사용할 수 있음 |
| `1` | `Lockout1` | 기능이 1단계로 제한됨 |
| `2` | `Lockout2` | 기능이 2단계로 제한됨 |
| `3` | `Lockout3` | 기능이 3단계로 제한됨 |
| `4` | `Lockout4` | 기능이 4단계로 제한됨 |
| `5` | `Lockout5` | 사용 가능한 기능이 가장 적음 |

### `ScheduleProgrammingVisibilityEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0` | `ScheduleProgrammingPermitted` | 온도 조절기에서 로컬 일정 프로그래밍 기능을 활성화 |
| `1` | `ScheduleProgrammingDenied` | 온도 조절기에서 로컬 일정 프로그래밍 기능을 비활성화 |

### 전역 속성

SDK 정의에는 다음 전역 속성이 포함되어 있습니다.

| ID | 값 |
|---|---|
| `0xFFFD` | `2` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml`

### 속성 정의

- `TemperatureDisplayMode`
  - ID: `0x0000`
  - 타입: `TemperatureDisplayModeEnum`
  - 쓰기 가능
  - 최대값: `0x01`
- `KeypadLockout`
  - ID: `0x0001`
  - 타입: `KeypadLockoutEnum`
  - 쓰기 가능
  - 최대값: `0x05`
  - 쓰기 작업에 `manage` 역할 필요
- `ScheduleProgrammingVisibility`
  - ID: `0x0002`
  - 타입: `ScheduleProgrammingVisibilityEnum`
  - 쓰기 가능
  - 최대값: `0x01`
  - 쓰기 작업에 `manage` 역할 필요
  - `optionalConform`
  - `introducedIn`: `ha-1.2-05-3520-29`
  - 기본값: `0x00`

### SDK 열거형

- `KeypadLockoutEnum`
  - `NoLockout`: `0x00`
  - `Lockout1`: `0x01`
  - `Lockout2`: `0x02`
  - `Lockout3`: `0x03`
  - `Lockout4`: `0x04`
  - `Lockout5`: `0x05`
- `ScheduleProgrammingVisibilityEnum`
  - `ScheduleProgrammingPermitted`: `0x00`
  - `ScheduleProgrammingDenied`: `0x01`
- `TemperatureDisplayModeEnum`
  - `Celsius`: `0x00`
  - `Fahrenheit`: `0x01`

## 구현

### 구현 파일

- `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h`
- `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp`
- `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h`
- `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp`

### `ThermostatUserInterfaceConfigurationCluster`

`ThermostatUserInterfaceConfigurationCluster`는 `DefaultServerCluster`를 상속하는 code-driven server cluster입니다. 속성 값은 클러스터 인스턴스에 저장되며, 애플리케이션에서 사용할 수 있는 타입 지정 getter와 setter를 제공합니다.

생성자는 다음 `Config` 값을 사용합니다.

```cpp
struct Config
{
    Config() :
        temperatureDisplayMode(ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum::kCelsius),
        keypadLockout(ThermostatUserInterfaceConfiguration::KeypadLockoutEnum::kNoLockout),
        scheduleProgrammingVisibility(
            ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted)
    {}

    ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum temperatureDisplayMode;
    ThermostatUserInterfaceConfiguration::KeypadLockoutEnum keypadLockout;
    ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum scheduleProgrammingVisibility;
    OptionalAttributeSet optionalAttributes{};
};
```

`ScheduleProgrammingVisibility`는 `Config::optionalAttributes`에 해당 속성을 활성화했을 때 노출됩니다.

### 속성 읽기와 쓰기

`ReadAttribute()`는 다음 값을 반환합니다.

- `ClusterRevision::Id`: `kRevision`
- `FeatureMap::Id`: `static_cast<uint32_t>(0)`
- `TemperatureDisplayMode::Id`: `mTemperatureDisplayMode`
- `KeypadLockout::Id`: `mKeypadLockout`
- `ScheduleProgrammingVisibility::Id`: `mScheduleProgrammingVisibility`

지원하지 않는 속성 ID에는 `Status::UnsupportedAttribute`를 반환합니다.

`WriteAttribute()`는 다음 setter를 호출합니다.

- `TemperatureDisplayMode::Id` → `SetTemperatureDisplayMode()`
- `KeypadLockout::Id` → `SetKeypadLockout()`
- `ScheduleProgrammingVisibility::Id` → `SetScheduleProgrammingVisibility()`

### setter 동작

다음 setter는 모두 전달된 값이 알려진 열거형 값인지 `EnsureKnownEnumValue()`로 확인합니다.

- `SetTemperatureDisplayMode()`
- `SetKeypadLockout()`
- `SetScheduleProgrammingVisibility()`

알 수 없는 열거형 값이면 `Status::ConstraintError`를 반환합니다. 값이 유효하면 속성 값을 저장하고 `Status::Success`를 반환합니다.

값이 실제로 변경되었고 `mDelegate`가 설정되어 있으면 해당 delegate callback을 동기적으로 호출합니다.

- `OnTemperatureDisplayModeChanged()`
- `OnKeypadLockoutChanged()`
- `OnScheduleProgrammingVisibilityChanged()`

현재 값과 동일한 값을 설정할 때는 callback이 호출되지 않습니다. 초기 설정과 delegate 연결 시에도 callback은 호출되지 않습니다. callback은 변경 알림만 제공하며 변경을 거부할 수 없습니다.

이 클러스터는 legacy `MatterPostAttributeChangeCallback`을 호출하지 않습니다. 해당 클러스터에 대해 기존 callback을 사용하던 애플리케이션은 delegate로 처리를 이동해야 합니다.

### `Delegate`

`ThermostatUserInterfaceConfiguration::Delegate`를 구현하고 `SetDelegate()`로 연결할 수 있습니다.

```cpp
class Delegate
{
public:
    virtual ~Delegate() = default;

    virtual void OnTemperatureDisplayModeChanged(TemperatureDisplayModeEnum value) {}
    virtual void OnKeypadLockoutChanged(KeypadLockoutEnum value) {}
    virtual void OnScheduleProgrammingVisibilityChanged(ScheduleProgrammingVisibilityEnum value) {}
};
```

필요한 callback만 override할 수 있습니다. 애플리케이션은 delegate의 수명을 관리해야 하며, delegate를 삭제하기 전에 `SetDelegate(nullptr)`로 분리해야 합니다. 클러스터 인스턴스 하나에는 delegate 포인터 하나만 연결할 수 있습니다.

callback에는 endpoint ID가 전달되지 않으므로 endpoint별 상태가 필요한 경우 별도의 delegate 인스턴스를 사용해야 합니다.

### `CodegenIntegration`

`CodegenIntegration.h`는 endpoint의 실행 중인 클러스터 인스턴스를 찾는 다음 함수를 제공합니다.

```cpp
ThermostatUserInterfaceConfigurationCluster * FindClusterOnEndpoint(EndpointId endpointId);
```

`CodegenIntegration.cpp`의 `IntegrationDelegate::CreateRegistration()`은 다음 순서로 `Config`를 초기화합니다.

1. `optionalAttributeBits`로 `optionalAttributes`를 설정합니다.
2. `TemperatureDisplayMode::GetDefaultOr()`로 `temperatureDisplayMode`를 초기화합니다.
3. `KeypadLockout::GetDefaultOr()`로 `keypadLockout`을 초기화합니다.
4. `ScheduleProgrammingVisibility`가 활성화된 경우 `ScheduleProgrammingVisibility::GetDefaultOr()`로 값을 초기화합니다.
5. `gServers[clusterInstanceIndex].Create(endpointId, config)`로 서버 클러스터를 생성합니다.

`MatterThermostatUserInterfaceConfigurationClusterInitCallback()`은 다음 설정으로 서버를 등록합니다.

- `clusterId`: `ThermostatUserInterfaceConfiguration::Id`
- `fetchFeatureMap`: `false`
- `fetchOptionalAttributes`: `true`

`MatterThermostatUserInterfaceConfigurationClusterShutdownCallback()`은 서버 등록을 해제합니다.

### Live attribute API

`CodegenIntegration.h`에는 실행 중인 `ThermostatUserInterfaceConfigurationCluster` 상태에 접근하기 위한 `Get()` 및 `Set()` 함수가 선언되어 있습니다.

#### `TemperatureDisplayMode`

```cpp
Protocols::InteractionModel::Status Get(
    EndpointId endpoint,
    ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum * value);

Protocols::InteractionModel::Status Set(
    EndpointId endpoint,
    ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum value);
```

#### `KeypadLockout`

```cpp
Protocols::InteractionModel::Status Get(
    EndpointId endpoint,
    ThermostatUserInterfaceConfiguration::KeypadLockoutEnum * value);

Protocols::InteractionModel::Status Set(
    EndpointId endpoint,
    ThermostatUserInterfaceConfiguration::KeypadLockoutEnum value);
```

#### `ScheduleProgrammingVisibility`

```cpp
Protocols::InteractionModel::Status Get(
    EndpointId endpoint,
    ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum * value);

Protocols::InteractionModel::Status Set(
    EndpointId endpoint,
    ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum value);
```

endpoint에서 클러스터를 찾지 못하면 `Protocols::InteractionModel::Status::UnsupportedEndpoint`를 반환합니다.

생성된 `GetDefault()` accessor는 ZAP/Ember attribute store에 저장된 startup default를 읽으며, live cluster state를 읽지 않습니다.

### 직접 생성하는 애플리케이션

애플리케이션에서 클러스터를 직접 생성하는 경우 다음 작업이 필요합니다.

1. endpoint와 `Config`를 사용해 `ThermostatUserInterfaceConfigurationCluster`를 생성합니다.
2. `SetDelegate()`로 delegate를 연결합니다.
3. 애플리케이션의 data model provider에 인스턴스를 등록합니다.

이 방식에서는 `CodegenIntegration` lookup이 필요하지 않습니다. endpoint와 클러스터 인스턴스가 재생성되면 delegate를 다시 연결해야 합니다.

## 관련 문서

- `src/app/clusters/thermostat-user-interface-configuration-server/README.md`
- `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h`
- `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp`
- `src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h`
- `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp`
- `src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml`
- `data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml`
- [클러스터 개발 가이드](../../../../docs/guides/writing_clusters.md)

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
