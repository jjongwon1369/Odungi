---
entity: ModeBase
ids: []
source_paths: ['src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml', 'src/app/clusters/mode-base-server/Delegate.h', 'src/app/clusters/mode-base-server/AppDelegate.h', 'src/app/clusters/mode-base-server/mode-base-cluster-objects.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h', 'src/app/clusters/mode-base-server/CodegenIntegration.h', 'src/app/clusters/mode-base-server/CodegenIntegration.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp', 'src/app/clusters/mode-base-server/mode-base-server.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.h', 'data_model/1.7/clusters/ModeBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 기본 정보

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Mode Base Cluster` |
| revision | `3` |
| classification | `hierarchy="base"`, `role="application"`, `picsCode="MODB"`, `scope="Endpoint"` |
| cluster ID | `Mode Base` |
| PICS | `MODB` |

### revisionHistory

| revision | summary |
|---:|---|
| `1` | Initial revision |
| `2` | `ChangeToModeResponse` command: `StatusText` must be provided for `InvalidInMode` status. Require at least one standard mode tag. Define reserved ranges for base/derived clusters. |
| `3` | Added `CoreModeTags` attribute and `ChangeToModeByCoreTag` command. |

### Features

| bit | code | name | summary | 적합성 |
|---:|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | Dependency with the OnOff cluster | optional |
| `1` | `COREMODES` | `CoreModes` | One or more core modes are supported | provisional, optional 또는 `COREMODES` feature에서 mandatory |

### 데이터 타입

#### `ModeOptionStruct`

| field id | 이름 | 타입 | 제약 조건 | 적합성 |
|---:|---|---|---|---|
| `0` | `Label` | `string` | `maxLength=64` | mandatory |
| `1` | `Mode` | `uint8` | - | mandatory |
| `2` | `ModeTags` | `list` of `ModeTagStruct` | `maxCount=8` | mandatory |

#### `ModeTagStruct`

| field id | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `MfgCode` | `vendor-id` | optional |
| `1` | `Value` | `enum16` | mandatory |

### Attributes

| ID | 이름 | 타입 | 접근 | 저장성 | 적합성 | 제약 조건 |
|---|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `list` of `ModeOptionStruct` | read, `view` | fixed | mandatory | 2~255개 |
| `0x0001` | `CurrentMode` | `uint8` | read, `view` | nonVolatile | mandatory | - |
| `0x0002` | `StartUpMode` | `uint8` | read/write, `view`/`operate` | nonVolatile, nullable | optional | default=`MS` |
| `0x0003` | `OnMode` | `uint8` | read/write, `view`/`operate` | nonVolatile, nullable | `DEPONOFF` feature에서 mandatory | - |
| `0x0004` | `CoreModeTags` | `list` of `enum16` | read, `view` | fixed | `COREMODES` feature에서 mandatory, provisional | 1~16개 |

### Commands

#### `ChangeToMode`

| 항목 | 값 |
|---|---|
| ID | `0x00` |
| 방향 | `commandToServer` |
| 응답 | `ChangeToModeResponse` |
| invoke privilege | `operate` |
| 적합성 | mandatory |

필드:

| field id | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `NewMode` | `uint8` | mandatory |

#### `ChangeToModeResponse`

| 항목 | 값 |
|---|---|
| ID | `0x01` |
| 방향 | `responseFromServer` |
| 적합성 | mandatory |

필드:

| field id | 이름 | 타입 | 적합성 | 제약 조건 |
|---:|---|---|---|---|
| `0` | `Status` | `enum8` | mandatory | - |
| `1` | `StatusText` | `string` | `Status=SUCCESS`이면 optional, 그 외 mandatory | `maxLength=64` |

#### `ChangeToModeByCoreTag`

| 항목 | 값 |
|---|---|
| ID | `0x02` |
| 방향 | `commandToServer` |
| 응답 | `ChangeToModeResponse` |
| 적합성 | `COREMODES` feature에서 mandatory, provisional |

필드:

| field id | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `NewModeTag` | `enum16` | mandatory |

## SDK 정의

### 파일

`src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml`

`ModeBase`에는 직접적인 cluster ID가 정의되어 있지 않으며, 공통 enum 값은 `mode-base-server` 소스의 `mode-base-cluster-objects.h`에서 `ModeBase` namespace에 정의됩니다. 각 enum 값은 derived clusters에도 나열 및 복사됩니다.

### `ModeTagStruct`

지원 대상 cluster:

| cluster code | 설명 |
|---|---|
| `0x0051` | Laundry Washer Mode |
| `0x0052` | Refrigerator and temperature controlled cabinet Mode |
| `0x0054` | RVC Run Mode |
| `0x0055` | RVC Clean Mode |
| `0x0059` | Dishwasher Mode |
| `0x005E` | Microwave Oven Mode |
| `0x0049` | Oven Mode |
| `0x009D` | Energy EVSE Mode |
| `0x009E` | Water Heater Mode |
| `0x009F` | Device Energy Management Mode |

필드:

| 이름 | 타입 | optional |
|---|---|---|
| `MfgCode` | `vendor_id` | `true` |
| `Value` | `enum16` | `false` |

`MfgCode` has been deprecated.

### `ModeOptionStruct`

동일한 지원 대상 cluster에 대해 다음 필드를 정의합니다.

| 이름 | 타입 | 제약 조건 | optional |
|---|---|---|---|
| `Label` | `char_string` | `length="64"` | `false` |
| `Mode` | `int8u` | - | `false` |
| `ModeTags` | `ModeTagStruct` array | `length="8"` | `false` |

### 생성 코드에 주석 처리된 공통 정의

SDK 템플릿에는 다음 공통 attributes와 commands의 정의가 주석으로 포함되어 있습니다.

Attributes:

| code | define | 이름 | 타입 | 접근 | optional |
|---|---|---|---|---|---|
| `0x0000` | `SUPPORTED_MODES` | `SupportedModes` | array of `ModeOptionStruct` | read-only | `false` |
| `0x0001` | `CURRENT_MODE` | `CurrentMode` | `int8u` | read-only | `false` |
| `0x0002` | `START_UP_MODE` | `StartUpMode` | `int8u` | writable | `true` |
| `0x0003` | `ON_MODE` | `OnMode` | `int8u` | writable | `true` |

Commands:

| code | 이름 | 방향 | response |
|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` |
| `0x01` | `ChangeToModeResponse` | `server` | - |

`ChangeToMode`의 인자는 `NewMode`이며, `ChangeToModeResponse`의 인자는 `Status`와 optional `StatusText`입니다.

## 구현

### 주요 파일

- `src/app/clusters/mode-base-server/Delegate.h`
- `src/app/clusters/mode-base-server/AppDelegate.h`
- `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`
- `src/app/clusters/mode-base-server/ModeBaseCluster.h`
- `src/app/clusters/mode-base-server/ModeBaseCluster.cpp`
- `src/app/clusters/mode-base-server/CodegenIntegration.h`
- `src/app/clusters/mode-base-server/CodegenIntegration.cpp`
- `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h`
- `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp`
- `src/app/clusters/mode-base-server/mode-base-server.h`

### namespace 및 derived cluster

구현 namespace:

```cpp
chip::app::Clusters::ModeBase
```

`ModeBase` 공통 구조를 사용하는 `ClusterEntry`:

| 상수 | cluster |
|---|---|
| `kDeviceEnergyManagementMode` | `DeviceEnergyManagementMode` |
| `kDishwasherMode` | `DishwasherMode` |
| `kEnergyEvseMode` | `EnergyEvseMode` |
| `kLaundryWasherMode` | `LaundryWasherMode` |
| `kMicrowaveOvenMode` | `MicrowaveOvenMode` |
| `kOvenMode` | `OvenMode` |
| `kRefrigeratorAndTemperatureControlledCabinetMode` | `RefrigeratorAndTemperatureControlledCabinetMode` |
| `kRvcCleanMode` | `RvcCleanMode` |
| `kRvcRunMode` | `RvcRunMode` |
| `kThermostatMode` | `ThermostatMode` |
| `kWaterHeaterMode` | `WaterHeaterMode` |

모든 aliased clusters는 `MicrowaveOvenMode`의 예외를 제외하고 mandatory attributes와 commands를 공유합니다.

```cpp
namespace Commands = ThermostatMode::Commands;
```

주요 attribute alias:

```cpp
namespace SupportedModes = DeviceEnergyManagementMode::Attributes::SupportedModes;
namespace CurrentMode    = DeviceEnergyManagementMode::Attributes::CurrentMode;
namespace CoreModeTags   = ThermostatMode::Attributes::CoreModeTags;
```

### `ModeBase::Feature`

```cpp
enum class Feature : uint32_t
{
    kOnOff     = 0x1,
    kCoreModes = to_underlying(ThermostatMode::Feature::kCoreModes),
};
```

### `ModeBase::ModeTag`

```cpp
enum class ModeTag : uint16_t
{
    kAuto      = 0x0,
    kQuick     = 0x1,
    kQuiet     = 0x2,
    kLowNoise  = 0x3,
    kLowEnergy = 0x4,
    kVacation  = 0x5,
    kMin       = 0x6,
    kMax       = 0x7,
    kNight     = 0x8,
    kDay       = 0x9,
};
```

### `ModeBase::StatusCode`

```cpp
enum class StatusCode : uint8_t
{
    kSuccess         = 0x0,
    kUnsupportedMode = 0x1,
    kGenericFailure  = 0x2,
    kInvalidInMode   = 0x3,
};
```

### `AppDelegate`

파일: `src/app/clusters/mode-base-server/AppDelegate.h`

`AppDelegate`는 application-specific logic을 구현하기 위한 추상 클래스입니다. SDK 사용자는 다음 함수를 override해야 합니다.

```cpp
virtual CHIP_ERROR Init() = 0;

virtual CHIP_ERROR GetModeLabelByIndex(uint8_t modeIndex, MutableCharSpan & label) = 0;

virtual CHIP_ERROR GetModeValueByIndex(uint8_t modeIndex, uint8_t & value) = 0;

virtual CHIP_ERROR GetModeTagsByIndex(
    uint8_t modeIndex,
    DataModel::List<detail::Structs::ModeTagStruct::Type> & modeTags) = 0;

virtual void HandleChangeToMode(
    uint8_t NewMode,
    ModeBase::Commands::ChangeToModeResponse::Type & response) = 0;
```

다음 함수는 기본 구현을 제공합니다.

```cpp
virtual CHIP_ERROR GetCoreModeTagByIndex(uint8_t tagIndex, uint16_t & tag)
{
    return CHIP_ERROR_PROVIDER_LIST_EXHAUSTED;
}
```

```cpp
virtual void HandleChangeToModeByCoreTag(
    uint16_t newModeTag,
    uint8_t & newMode,
    ModeBase::Commands::ChangeToModeResponse::Type & response)
{
    HandleChangeToMode(newMode, response);
}
```

`GetModeLabelByIndex`, `GetModeValueByIndex`, `GetModeTagsByIndex`의 목록 내용이 변경되면 `Instance::ReportSupportedModesChange`를 호출해야 합니다.

### `Delegate`

파일: `src/app/clusters/mode-base-server/Delegate.h`

`Delegate`는 `AppDelegate`를 상속하며 `Instance` 포인터를 관리합니다.

```cpp
class Delegate : public AppDelegate
{
public:
    Delegate() = default;
    virtual ~Delegate() = default;

    void SetInstance(Instance * aInstance) { mInstance = aInstance; }

protected:
    const Instance * GetInstance() const { return mInstance; }
    Instance * GetInstance() { return mInstance; }
};
```

`SetInstance`는 `Instance` 생성 과정에서 SDK가 호출합니다.

### `ModeBaseCluster`

파일: `src/app/clusters/mode-base-server/ModeBaseCluster.h`

`ModeBaseCluster`는 `DefaultServerCluster`를 상속합니다.

```cpp
class ModeBaseCluster : public DefaultServerCluster
```

`Config`:

```cpp
struct Config
{
    BitMask<ModeBase::Feature> feature;
    OptionalAttributeSet optionalAttributeSet;
    ModeBase::AppDelegate & appDelegate;
    bool onOffValueForStartUp = false;
    DeviceLayer::DiagnosticDataProvider & diagnosticDataProvider;
};
```

주요 public API:

```cpp
Protocols::InteractionModel::Status UpdateCurrentMode(uint8_t aNewMode);

Protocols::InteractionModel::Status UpdateStartUpMode(
    DataModel::Nullable<uint8_t> aNewStartUpMode);

Protocols::InteractionModel::Status UpdateOnMode(
    DataModel::Nullable<uint8_t> aNewOnMode);

uint8_t GetCurrentMode() const;

DataModel::Nullable<uint8_t> GetStartUpMode() const;

DataModel::Nullable<uint8_t> GetOnMode() const;

void ReportSupportedModesChange();

bool IsSupportedMode(uint8_t mode);

CHIP_ERROR GetModeValueByModeTag(uint16_t modeTag, uint8_t & value);

bool IsSupportedCoreModeTag(uint16_t coreModeTag);

bool ModeHasTag(uint8_t mode, uint16_t tag);
```

`UpdateCurrentMode`, `UpdateStartUpMode`, `UpdateOnMode`는 값이 지원되는 mode가 아니면 `Status::ConstraintError`를 반환하며, 성공 시 non-volatile storage에도 기록합니다.

### Attribute 처리

`ReadAttribute`는 다음 attributes를 처리합니다.

- `ClusterRevision`
- `SupportedModes`
- `CurrentMode`
- `StartUpMode`
- `OnMode`
- `CoreModeTags`
- `FeatureMap`

`WriteAttribute`는 다음 attributes를 처리합니다.

- `StartUpMode`
- `OnMode`

mandatory metadata는 다음 두 attributes입니다.

```cpp
constexpr std::array<DataModel::AttributeEntry, 2> kMandatoryMetadata = {
    SupportedModes::kMetadataEntry,
    CurrentMode::kMetadataEntry,
};
```

optional attributes:

- `StartUpMode`: `OptionalAttributeSet`에 포함된 경우
- `OnMode`: `Feature::kOnOff`가 활성화된 경우
- `CoreModeTags`: `Feature::kCoreModes`가 활성화된 경우

### Command 처리

`InvokeCommand`는 다음 commands를 처리합니다.

- `Commands::ChangeToMode::Id`
- `Commands::ChangeToModeByCoreTag::Id`

`ChangeToMode` 처리:

1. `NewMode`가 `SupportedModes`에 없으면 `StatusCode::kUnsupportedMode`를 반환합니다.
2. `NewMode`가 `CurrentMode`와 같으면 `StatusCode::kSuccess`를 반환합니다.
3. 그 외에는 `AppDelegate::HandleChangeToMode`를 호출합니다.
4. response의 status가 `StatusCode::kSuccess`이면 `CurrentMode`를 갱신합니다.
5. 갱신에 실패하면 `StatusCode::kGenericFailure`를 반환합니다.

`ChangeToModeByCoreTag` 처리:

1. `NewModeTag`가 `CoreModeTags`에 없으면 `StatusCode::kUnsupportedMode`를 반환합니다.
2. 현재 mode가 해당 tag를 포함하면 현재 mode를 우선합니다.
3. 그렇지 않으면 `GetModeValueByModeTag`로 초기 mode를 찾습니다.
4. `AppDelegate::HandleChangeToModeByCoreTag`를 호출합니다.
5. 선택된 mode가 지원되고 해당 tag를 포함하는지 검증합니다.
6. 검증을 통과하면 `CurrentMode`를 갱신합니다.

`MicrowaveOvenMode`는 예외적으로 다음 command를 지원하지 않습니다.

- `ChangeToMode`
- `ChangeToModeResponse`

### Startup 및 persistence

`ModeBaseCluster::Startup`은 다음 순서로 동작합니다.

1. `DefaultServerCluster::Startup`을 호출합니다.
2. `GetModeValueByIndex(0, mCurrentMode)`로 첫 번째 mode를 초기 `CurrentMode`로 설정합니다.
3. persistent attributes를 로드합니다.
4. `StartUpMode`가 설정되어 있고 OTA reboot가 아니면 `CurrentMode`를 `StartUpMode`로 설정합니다.
5. `onOffValueForStartUp`가 활성화되고 `OnMode`가 null이 아니면 `CurrentMode`를 `OnMode`로 설정합니다.

OTA reboot에서 `StartUpMode`는 무시되며, boot reason이 `BootReasonType::kSoftwareUpdateCompleted`인 경우가 이에 해당합니다.

persistent attributes:

- `CurrentMode`
- `StartUpMode`
- `OnMode`

### `Instance` 및 codegen integration

파일: `src/app/clusters/mode-base-server/CodegenIntegration.h`

`CodegenModeBaseCluster`는 `ModeBaseCluster`의 subclass이며 `Startup` 시 storage migration을 수행합니다.

```cpp
class CodegenModeBaseCluster : public ModeBaseCluster
{
public:
    using ModeBaseCluster::ModeBaseCluster;

    CHIP_ERROR Startup(ServerClusterContext & context) override;
};
```

`Instance` 생성자:

```cpp
Instance(
    Delegate * aDelegate,
    EndpointId aEndpointId,
    ClusterId aClusterId,
    uint32_t aFeature);
```

`Instance::Init()`은 다음을 검증하고 수행합니다.

- endpoint와 cluster가 ZAP에 활성화되어 있는지 확인
- `aClusterId`가 `kAliasedClusters` 중 하나인지 확인
- `ThermostatMode`에서 `StartUpMode` optional attribute 확인
- 다른 aliased clusters에서 `StartUpMode` 및 `Feature::kCoreModes` 사용 여부 검증
- `OnOff` cluster와 `StartUpOnOff` attribute 연동
- `Delegate::SetInstance`
- `Delegate::Init`
- `CodegenDataModelProvider::Instance().Registry().Register`

인스턴스는 `GetModeBaseInstanceList()`를 통해 intrusive list로 관리됩니다.

```cpp
IntrusiveList<Instance> & GetModeBaseInstanceList();
```

`Shutdown()`은 `Delegate`의 instance 포인터를 해제하고, instance를 unregister한 뒤 cluster를 destroy합니다.

### Storage migration

파일:

- `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h`
- `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp`

함수:

```cpp
CHIP_ERROR MigrateModeBaseServerStorage(
    EndpointId endpointId,
    ClusterId clusterId,
    SafeAttributePersistenceProvider & safeProvider,
    AttributePersistenceProvider & dstProvider);
```

migration 대상 attributes:

```cpp
Attributes::CurrentMode::Id
Attributes::StartUpMode::Id
Attributes::OnMode::Id
```

`CodegenModeBaseCluster::Startup`에서 `SafeAttributePersistenceProvider`를 `AttributePersistenceProvider`로 migration합니다.

## 관련 문서

- `data_model/1.7/clusters/ModeBase.xml`
- `src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml`
- `src/app/clusters/mode-base-server/mode-base-server.h`
- `src/app/clusters/mode-base-server/ModeBaseCluster.h`
- `src/app/clusters/mode-base-server/ModeBaseCluster.cpp`
- `src/app/clusters/mode-base-server/AppDelegate.h`
- `src/app/clusters/mode-base-server/Delegate.h`
- `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`
- `src/app/clusters/mode-base-server/CodegenIntegration.h`
- `src/app/clusters/mode-base-server/CodegenIntegration.cpp`
- `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h`
- `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp`

## 관련 페이지

**파생 클러스터**

- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)
- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
