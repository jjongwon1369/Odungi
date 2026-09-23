---
entity: Temperature Control
ids: ['0x0056']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.h', 'src/app/clusters/temperature-control-server/temperature-control-server.h', 'src/app/clusters/temperature-control-server/CodegenIntegration.h', 'src/app/clusters/temperature-control-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp', 'src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h', 'data_model/1.7/clusters/TemperatureControl.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Temperature Control

## 스펙

### 클러스터 기본 정보

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Temperature Control Cluster` |
| Cluster ID | `0x0056` |
| Revision | `1` |
| Classification | `base` |
| Role | `application` |
| PICS Code | `TCTL` |
| Scope | `Endpoint` |
| Revision history | `Initial revision` |

### Features

| Bit | Code | Name | Summary | 조건 |
|---:|---|---|---|---|
| 0 | `TN` | `TemperatureNumber` | Use actual temperature numbers | 선택 사항 |
| 1 | `TL` | `TemperatureLevel` | Use temperature levels | 선택 사항 |
| 2 | `STEP` | `TemperatureStep` | Use step control with temperature numbers | `TN` 필요 |

### Attributes

| ID | Name | Type | Access | 조건 | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureSetpoint` | `temperature` | 읽기, `view` | `TN` | `MinTemperature` 이상, `MaxTemperature` 이하 |
| `0x0001` | `MinTemperature` | `temperature` | 읽기, `view` | `TN` | `MaxTemperature - 1` 이하, `persistence="fixed"` |
| `0x0002` | `MaxTemperature` | `temperature` | 읽기, `view` | `TN` | `persistence="fixed"` |
| `0x0003` | `Step` | `temperature` | 읽기, `view` | `STEP` | `1` 이상, `MaxTemperature - MinTemperature` 이하, `persistence="fixed"` |
| `0x0004` | `SelectedTemperatureLevel` | `uint8` | 읽기, `view` | `TL` | 최댓값 `31` |
| `0x0005` | `SupportedTemperatureLevels` | `list` | 읽기, `view` | `TL` | 최대 항목 수 `32`, 각 `string`의 최대 길이 `16` |

### Commands

#### `SetTemperature`

- Command ID: `0x00`
- Direction: `commandToServer`
- Invoke privilege: `operate`
- Response: `Y`
- Mandatory conformance: 항상 적용

| Field ID | Name | Type | 조건 |
|---|---|---|---|
| `0` | `TargetTemperature` | `temperature` | `TN` |
| `1` | `TargetTemperatureLevel` | `uint8` | `TL` |

## SDK 정의

### 클러스터 설정

- Source: `src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml`
- Domain: `Appliances`
- Description: `Attributes and commands for configuring the temperature control, and reporting temperature.`
- Cluster code: `0x0056`
- Define: `TEMPERATURE_CONTROL_CLUSTER`
- Client: 활성화
- Server: 활성화
- Global attribute: `0xFFFD`, 값 `1`

### Features

| Bit | Code | Name | Summary |
|---:|---|---|---|
| 0 | `TN` | `TemperatureNumber` | Use actual temperature numbers |
| 1 | `TL` | `TemperatureLevel` | Use temperature levels |
| 2 | `STEP` | `TemperatureStep` | Use step control with temperature numbers |

`STEP`는 `TN` Feature가 필요합니다.

### Attributes

| Code | Name | Define | Type | Optional | Feature |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureSetpoint` | `TEMP_SETPOINT` | `temperature` | `true` | `TN` |
| `0x0001` | `MinTemperature` | `MIN_TEMP` | `temperature` | `true` | `TN` |
| `0x0002` | `MaxTemperature` | `MAX_TEMP` | `temperature` | `true` | `TN` |
| `0x0003` | `Step` | `STEP` | `temperature` | `true` | `STEP` |
| `0x0004` | `SelectedTemperatureLevel` | `SELECTED_TEMP_LEVEL` | `int8u` | `true` | `TL`, 최댓값 `31` |
| `0x0005` | `SupportedTemperatureLevels` | `SUPPORTED_TEMP_LEVELS` | `array` | `true` | `TL`, `entryType="char_string"`, `length="32"` |

### Command

#### `SetTemperature`

- Code: `0x00`
- Optional: `false`
- Description: `The SetTemperature command SHALL have the following data fields:`

| Arg ID | Name | Type | Optional |
|---:|---|---|---|
| `0` | `TargetTemperature` | `temperature` | `true` |
| `1` | `TargetTemperatureLevel` | `int8u` | `true` |

## 구현

### 구현 파일

- `src/app/clusters/temperature-control-server/TemperatureControlCluster.h`
- `src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp`
- `src/app/clusters/temperature-control-server/temperature-control-server.h`
- `src/app/clusters/temperature-control-server/CodegenIntegration.h`
- `src/app/clusters/temperature-control-server/CodegenIntegration.cpp`
- `src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h`

### `TemperatureControlCluster`

`TemperatureControlCluster`는 `DefaultServerCluster`를 상속합니다.

```cpp
class TemperatureControlCluster : public DefaultServerCluster
```

#### `StartupConfiguration`

```cpp
struct StartupConfiguration
{
    int16_t temperatureSetpoint{};
    int16_t minTemperature{};
    int16_t maxTemperature{};
    int16_t step{};
    uint8_t selectedTemperatureLevel{};
};
```

#### 주요 메서드

```cpp
TemperatureControlCluster(EndpointId endpointId,
                          const BitFlags<TemperatureControl::Feature> features,
                          const StartupConfiguration & config);

DataModel::ActionReturnStatus ReadAttribute(
    const DataModel::ReadAttributeRequest & request,
    AttributeValueEncoder & encoder) override;

CHIP_ERROR Attributes(
    const ConcreteClusterPath & path,
    ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

std::optional<DataModel::ActionReturnStatus> InvokeCommand(
    const DataModel::InvokeRequest & request,
    TLV::TLVReader & input_arguments,
    CommandHandler * handler) override;

CHIP_ERROR AcceptedCommands(
    const ConcreteClusterPath & path,
    ReadOnlyBufferBuilder<DataModel::AcceptedCommandEntry> & builder) override;
```

#### Temperature 값 API

```cpp
CHIP_ERROR SetTemperatureSetpoint(int16_t temperatureSetpoint);
int16_t GetTemperatureSetpoint() const;

int16_t GetStep() const;
int16_t GetMinTemperature() const;
int16_t GetMaxTemperature() const;
```

`SetTemperatureSetpoint`는 다음을 검증합니다.

- `TemperatureNumber` Feature가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환합니다.
- `temperatureSetpoint`가 `mMinTemperature`와 `mMaxTemperature` 범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환합니다.
- `TemperatureStep` Feature가 있으면 `(temperatureSetpoint - mMinTemperature) % mStep == 0`이어야 합니다.
- 검증 성공 시 `TemperatureSetpoint::Id`를 사용해 속성값을 갱신합니다.

#### Temperature Level API

```cpp
CHIP_ERROR SetSelectedTemperatureLevel(uint8_t selectedTemperatureLevel);
uint8_t GetSelectedTemperatureLevel() const;

static TemperatureControl::SupportedTemperatureLevelsIteratorDelegate * GetDelegate();
static void SetDelegate(
    TemperatureControl::SupportedTemperatureLevelsIteratorDelegate * delegate);
```

`SetSelectedTemperatureLevel`는 다음을 검증합니다.

- `TemperatureLevel` Feature가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환합니다.
- Delegate가 없으면 `CHIP_IM_GLOBAL_STATUS(NotFound)`를 반환합니다.
- `selectedTemperatureLevel`이 Delegate의 `Size()` 이상이면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환합니다.
- 검증 성공 시 `SelectedTemperatureLevel::Id`를 사용해 속성값을 갱신합니다.

### 초기화 검증

`TemperatureControlCluster.cpp`에는 다음 상수가 정의되어 있습니다.

```cpp
constexpr int16_t kMinTemperatureRange           = -27315;
constexpr int16_t kMaxTemperatureRange           = 32766;
constexpr int16_t kMinStep                       = 1;
constexpr uint8_t kMaxSelectedTemperatureLevel   = 31;
constexpr uint8_t kMaxTemperatureLevelStringSize = 32;
```

생성자는 다음을 검증합니다.

- `TemperatureNumber`가 활성화된 경우 `TemperatureLevel`이 동시에 활성화되지 않아야 합니다.
- `mMinTemperature`는 `-27315` 이상 `32766` 이하이어야 합니다.
- `mMaxTemperature`는 `mMinTemperature + 1` 이상이어야 합니다.
- `mTemperatureSetpoint`는 `mMinTemperature` 이상 `mMaxTemperature` 이하이어야 합니다.
- `TemperatureStep`가 활성화된 경우 `mStep`은 `1` 이상 `mMaxTemperature - mMinTemperature` 이하이어야 합니다.
- `TemperatureLevel`이 활성화된 경우 `mSelectedTemperatureLevel`은 `31` 이하여야 합니다.

### Attribute 읽기

`ReadAttribute`는 다음 항목을 제공합니다.

| Attribute | 처리 |
|---|---|
| `ClusterRevision::Id` | `TemperatureControl::kRevision` 인코딩 |
| `FeatureMap::Id` | `mFeatures` 인코딩 |
| `TemperatureSetpoint::Id` | `mTemperatureSetpoint` 인코딩 |
| `MinTemperature::Id` | `mMinTemperature` 인코딩 |
| `MaxTemperature::Id` | `mMaxTemperature` 인코딩 |
| `Step::Id` | `mStep` 인코딩 |
| `SelectedTemperatureLevel::Id` | `mSelectedTemperatureLevel` 인코딩 |
| `SupportedTemperatureLevels::Id` | Delegate를 통한 목록 인코딩 |
| 그 외 | `UnsupportedAttribute` |

`SupportedTemperatureLevels::Id`를 읽을 때 Delegate가 `nullptr`이면 빈 목록을 인코딩합니다. Delegate가 있으면 `Reset` 후 `Next`를 반복 호출해 목록을 인코딩합니다.

### `SetTemperature` 처리

`InvokeCommand`는 `Commands::SetTemperature::Id`를 처리하고, 그 외 Command에는 `UnsupportedCommand`를 반환합니다.

`HandleSetTemperature`의 동작은 활성화된 Feature에 따라 달라집니다.

#### `TemperatureNumber`가 활성화된 경우

- `TargetTemperature`가 없으면 `InvalidCommand`를 반환합니다.
- `SetTemperatureSetpoint`를 호출합니다.
- 범위 또는 `Step` 제약 위반 시 `ConstraintError`를 반환합니다.
- 그 외 실행 실패 시 `InvalidInState`를 반환합니다.

#### `TemperatureLevel`가 활성화된 경우

- `TargetTemperatureLevel`이 없으면 `InvalidCommand`를 반환합니다.
- `SetSelectedTemperatureLevel`을 호출합니다.
- Delegate가 없으면 `NotFound`를 반환합니다.
- Level 제약 위반 시 `ConstraintError`를 반환합니다.
- 그 외 실행 실패 시 `InvalidInState`를 반환합니다.

모든 처리가 성공하면 `Success`를 반환합니다.

### `SupportedTemperatureLevelsIteratorDelegate`

`SupportedTemperatureLevelsIteratorDelegate`는 `SupportedTemperatureLevels` 목록을 관리하기 위한 인터페이스입니다.

```cpp
class SupportedTemperatureLevelsIteratorDelegate
{
public:
    virtual ~SupportedTemperatureLevelsIteratorDelegate() = default;

    void Reset(EndpointId endpoint);

    virtual uint8_t Size() = 0;
    virtual CHIP_ERROR Next(MutableCharSpan & item) = 0;

protected:
    EndpointId mEndpoint;
    uint8_t mIndex;
};
```

- `Reset(EndpointId endpoint)`는 대상 `EndpointId`와 반복 인덱스를 초기화합니다.
- `Size()`는 `SupportedTemperatureLevels` 목록의 전체 크기를 반환합니다.
- `Next(MutableCharSpan & item)`은 다음 항목을 반환합니다.

### Codegen 통합

`CodegenIntegration.cpp`는 `CodegenClusterIntegration`을 통해 서버 클러스터를 등록합니다.

```cpp
void MatterTemperatureControlClusterInitCallback(EndpointId endpointId);
void MatterTemperatureControlClusterShutdownCallback(
    EndpointId endpointId,
    MatterClusterShutdownType shutdownType);
void MatterTemperatureControlPluginServerInitCallback();
```

등록 시 다음 설정을 사용합니다.

```cpp
{
    .endpointId                = endpointId,
    .clusterId                 = TemperatureControl::Id,
    .fixedClusterInstanceCount = kTemperatureControlFixedClusterCount,
    .maxClusterInstanceCount   = kTemperatureControlMaxClusterCount,
    .fetchFeatureMap           = true,
    .fetchOptionalAttributes   = true,
}
```

`IntegrationDelegate::CreateRegistration`은 다음 선택 속성을 구성합니다.

```cpp
app::OptionalAttributeSet<
    TemperatureSetpoint::Id,
    MinTemperature::Id,
    MaxTemperature::Id,
    Step::Id,
    SelectedTemperatureLevel::Id,
    SupportedTemperatureLevels::Id>
    optionalAttributeSet(optionalAttributeBits);
```

`TemperatureNumber`가 활성화되면 `TemperatureSetpoint::Id`, `MinTemperature::Id`, `MaxTemperature::Id`의 기본값을 가져옵니다. `TemperatureStep`가 활성화된 경우 `Step::Id`의 기본값도 가져옵니다.

`TemperatureLevel`이 활성화되면 `SelectedTemperatureLevel::Id`의 기본값과 `SupportedTemperatureLevels::Id`의 존재를 검증합니다.

### Codegen 통합 API

`src/app/clusters/temperature-control-server/CodegenIntegration.h`에 다음 API가 정의되어 있습니다.

```cpp
TemperatureControlCluster * FindClusterOnEndpoint(EndpointId endpointId);

CHIP_ERROR SetTemperatureSetpoint(
    EndpointId endpointId,
    int16_t temperatureSetpoint);

CHIP_ERROR SetSelectedTemperatureLevel(
    EndpointId endpointId,
    uint8_t selectedTemperatureLevel);

SupportedTemperatureLevelsIteratorDelegate * GetDelegate();

void SetDelegate(
    SupportedTemperatureLevelsIteratorDelegate * delegate);
```

`FindClusterOnEndpoint`가 클러스터를 찾지 못하면 `SetTemperatureSetpoint`와 `SetSelectedTemperatureLevel`은 `CHIP_ERROR_INVALID_ARGUMENT`를 반환합니다.

### 서버 헤더

`src/app/clusters/temperature-control-server/temperature-control-server.h`는 다음 파일을 포함합니다.

```cpp
#include <app/clusters/temperature-control-server/CodegenIntegration.h>
```

### 관련 문서