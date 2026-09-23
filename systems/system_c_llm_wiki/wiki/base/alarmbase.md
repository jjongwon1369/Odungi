---
entity: AlarmBase
ids: []
source_paths: ['src/app/clusters/alarm-base-server/Delegate.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp', 'src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h', 'data_model/1.7/clusters/AlarmBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 클러스터 정보

- 이름: `Alarm Base Cluster`
- revision: `2`
- classification: base
- role: application
- scope: `Endpoint`
- PICS code: `ALARM`
- cluster ID 이름: `Alarm Base`

### revisionHistory

| revision | summary |
|---|---|
| `1` | Initial revision |
| `2` | Changed event field ID's to match SDK |

### Feature

| bit | code | name | summary | 적합성 |
|---:|---|---|---|---|
| `0` | `RESET` | `Reset` | Supports the ability to reset alarms | optional |

### 데이터 타입

- `AlarmBitmap`: bitmap

### 속성

| ID | 이름 | 타입 | 접근 | 적합성 | 비고 |
|---|---|---|---|---|---|
| `0x0000` | `Mask` | `AlarmBitmap` | read, `view` | mandatory |  |
| `0x0001` | `Latch` | `AlarmBitmap` | read, `view` | `RESET` feature에서 mandatory | `fixed` persistence |
| `0x0002` | `State` | `AlarmBitmap` | read, `view` | mandatory |  |
| `0x0003` | `Supported` | `AlarmBitmap` | read, `view` | mandatory | `fixed` persistence |

### 명령

| ID | 이름 | 방향 | 응답 | invoke privilege | 적합성 |
|---|---|---|---|---|---|
| `0x00` | `Reset` | commandToServer | Y | `operate` | `RESET` feature에서 mandatory |
| `0x01` | `ModifyEnabledAlarms` | commandToServer | Y | `operate` | optional |

#### `Reset`

필드:

| ID | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `Alarms` | `AlarmBitmap` | mandatory |

#### `ModifyEnabledAlarms`

필드:

| ID | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `Mask` | `AlarmBitmap` | mandatory |

### 이벤트

#### `Notify`

- ID: `0x00`
- priority: `info`
- read privilege: `view`
- 적합성: mandatory

필드:

| ID | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `Active` | `AlarmBitmap` | mandatory |
| `1` | `Inactive` | `AlarmBitmap` | mandatory |
| `2` | `State` | `AlarmBitmap` | mandatory |
| `3` | `Mask` | `AlarmBitmap` | mandatory |

## 구현

### 파일

- `src/app/clusters/alarm-base-server/Delegate.h`
- `src/app/clusters/alarm-base-server/AlarmBaseCluster.h`
- `src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp`
- `src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h`

### `AlarmBase::Delegate`

`AlarmBase` 명령 처리를 위한 선택적 애플리케이션 delegate입니다. 클러스터가 Matter attributes를 업데이트하기 전에 메서드를 호출합니다.

- `true`: 클러스터가 변경을 적용
- `false`: 명령을 거부하고 `Failure`를 응답하며 attributes를 변경하지 않음

Matter attribute model만 사용하는 구현은 두 메서드에서 항상 `true`를 반환할 수 있습니다. 물리적 alarm, annunciator 또는 latched hardware state가 있는 제품은 해당 장치 동작을 수행하거나 거부하기 위해 hook을 사용할 수 있습니다.

```cpp
namespace chip::app::Clusters::AlarmBase {

class Delegate
{
public:
    Delegate()          = default;
    virtual ~Delegate() = default;

    virtual bool ModifyEnabledAlarms(AlarmMap mask) { return true; }

    virtual bool ResetAlarms(AlarmMap alarms) { return true; }
};

} // namespace chip::app::Clusters::AlarmBase
```

#### `ModifyEnabledAlarms`

`ModifyEnabledAlarms` command 수신 후 `Mask` attribute가 업데이트되기 전에 호출됩니다.

- `mask`: `Mask` attribute의 새 값
- 설정된 각 bit는 derived cluster가 정의한 alarm type에 해당
- 반환값이 `false`이면 `Mask` 또는 `State`를 변경하지 않음
- 반환값이 `true`이면 클러스터가 `Mask`를 업데이트하고 새 mask와 active alarms의 일관성을 위해 `State`를 조정할 수 있음

#### `ResetAlarms`

`Reset` command 수신 후 `State` attribute가 업데이트되기 전에 호출됩니다.

- `alarms`: client가 reset을 요청한 alarm bits
- 반환값이 `false`이면 `State`를 변경하지 않음
- 반환값이 `true`이면 클러스터가 `ResetLatchedAlarms()`를 통해 `State`에서 요청된 bits를 지우고 `Notify` event를 발생시킬 수 있음

### `AlarmBaseCluster`

`AlarmBase` cluster의 code-driven implementation입니다. `DishwasherAlarm`, `RefrigeratorAlarm`과 같은 derivation을 위한 base implementation을 제공합니다.

```cpp
class AlarmBaseCluster : public DefaultServerCluster
{
public:
    struct Config
    {
        AlarmBase::Delegate & delegate;
        BitMask<AlarmBase::Feature> feature{};
        AlarmBase::AlarmMap supported{};
        AlarmBase::AlarmMap latch{};
        bool supportsModifyEnabledAlarms = false;
    };

    AlarmBaseCluster(EndpointId endpointId, AlarmBase::ClusterEntry cluster, const Config & config);
};
```

#### `Config`

| 필드 | 타입 | 설명 |
|---|---|---|
| `delegate` | `AlarmBase::Delegate &` | 명령 처리 delegate |
| `feature` | `BitMask<AlarmBase::Feature>` | 활성화된 feature |
| `supported` | `AlarmBase::AlarmMap` | 지원되는 alarm bitmap |
| `latch` | `AlarmBase::AlarmMap` | latch 설정 |
| `supportsModifyEnabledAlarms` | `bool` | `ModifyEnabledAlarms` 지원 여부 |

#### Application-facing API

```cpp
AlarmBase::AlarmMap GetMask() const;
AlarmBase::AlarmMap GetState() const;
AlarmBase::AlarmMap GetSupported() const;
AlarmBase::AlarmMap GetLatch() const;
BitMask<AlarmBase::Feature> GetFeatures() const;

Protocols::InteractionModel::Status SetMask(const AlarmBase::AlarmMap & mask);
Protocols::InteractionModel::Status SetState(const AlarmBase::AlarmMap & newState);
Protocols::InteractionModel::Status ResetLatchedAlarms(const AlarmBase::AlarmMap & alarms);
```

| API | 동작 |
|---|---|
| `GetMask()` | 현재 `Mask` 반환 |
| `GetState()` | 현재 `State` 반환 |
| `GetSupported()` | 현재 `Supported` 반환 |
| `GetLatch()` | 현재 `Latch` 반환 |
| `GetFeatures()` | 현재 feature bitmap 반환 |
| `SetMask()` | `Mask` 설정 |
| `SetState()` | `State` 설정 |
| `ResetLatchedAlarms()` | 지정한 alarm을 `State`에서 reset |

#### `SetMask()`

1. `mask`의 모든 bits가 `mSupported`에 포함되어야 합니다.
2. `Mask` attribute를 업데이트합니다.
3. 새 `mask`가 현재 `State`의 일부 alarm을 포함하지 않으면 해당 alarm을 `State`에서 제거합니다.
4. `State` 조정에는 `SetStateIgnoringLatch()`를 사용합니다.

조건을 만족하지 못하면 `Status::Failure`, attribute 업데이트 성공 시 `Status::Success`를 반환합니다.

#### `SetState()`

```cpp
return SetStateInternal(newState, false);
```

`newState`는 `mSupported`와 현재 `mMask`가 모두 허용해야 합니다. `Feature::kReset`이 활성화되어 있으면 `Latch`와 현재 `State`에 해당하는 bits를 유지합니다.

`State`가 변경되면 다음 값을 계산하여 `SendNotifyEvent()`를 호출합니다.

- `becameActive`: 새로 active가 된 alarms
- `becameInactive`: inactive가 된 alarms
- `finalNewState`
- 현재 `mMask`

#### `SetStateIgnoringLatch()`

```cpp
return SetStateInternal(newState, true);
```

`Latch` attribute가 state update를 막지 않아야 하는 경우에 사용합니다. 구현 주석에서는 mask adjustment, reset, integration init 용도로 설명하며, 애플리케이션은 `SetState()` 또는 `ResetLatchedAlarms()` 사용을 권장합니다.

#### `ResetLatchedAlarms()`

1. 요청된 `alarms`가 `mSupported`에 포함되는지 확인합니다.
2. 현재 `mState`에서 `alarms`를 제거합니다.
3. `SetStateIgnoringLatch()`를 호출합니다.

#### Attribute 처리

`ReadAttribute()`는 다음 attributes를 지원합니다.

- `ClusterRevision::Id`
- `FeatureMap::Id`
- `Mask::Id`
- `Latch::Id`
- `State::Id`
- `Supported::Id`

그 외 attribute ID에는 `Status::UnsupportedAttribute`를 반환합니다.

`Attributes()`는 다음 mandatory attributes를 등록합니다.

- `Mask`
- `State`
- `Supported`

`Latch`는 `Feature::kReset`이 활성화된 경우 optional attribute로 등록합니다.

#### Accepted commands

`AcceptedCommands()`는 다음 조건에 따라 command를 등록합니다.

- `Feature::kReset`이 활성화되면 `Commands::Reset::kMetadataEntry`
- `mSupportsModifyEnabledAlarms`가 `true`이면 `Commands::ModifyEnabledAlarms::kMetadataEntry`

#### Command 처리

`InvokeCommand()`는 command ID에 따라 다음과 같이 처리합니다.

| command | 처리 |
|---|---|
| `Commands::Reset::Id` | `Commands::Reset::DecodableType`을 decode한 후 `HandleReset()` 호출 |
| `Commands::ModifyEnabledAlarms::Id` | `Commands::ModifyEnabledAlarms::DecodableType`을 decode한 후 `HandleModifyEnabledAlarms()` 호출 |
| 그 외 | `Status::UnsupportedCommand` |

#### `HandleReset()`

1. `alarms`의 모든 bits가 `mSupported`에 포함되는지 확인합니다.
2. 지원되지 않으면 `Status::InvalidCommand`를 반환합니다.
3. `mDelegate.ResetAlarms(alarms)`를 호출합니다.
4. delegate가 `false`를 반환하면 `Status::Failure`를 반환합니다.
5. 성공하면 `ResetLatchedAlarms(alarms)`를 호출합니다.

#### `HandleModifyEnabledAlarms()`

1. `mask`의 모든 bits가 `mSupported`에 포함되는지 확인합니다.
2. 지원되지 않으면 `Status::InvalidCommand`를 반환합니다.
3. `mDelegate.ModifyEnabledAlarms(mask)`를 호출합니다.
4. delegate가 `false`를 반환하면 `Status::Failure`를 반환합니다.
5. 성공하면 `SetMask(mask)`를 호출합니다.

### 내부 타입 및 매핑

`alarm-base-cluster-objects.h`는 `AlarmBase` derivation에서 공유하는 타입과 generated cluster 정의를 매핑합니다.

```cpp
struct ClusterEntry
{
    ClusterId id;
    uint32_t revision;
};

enum class AlarmBitmap : uint32_t
{
    kNone = 0,
};

using AlarmMap = BitMask<AlarmBitmap>;
using Feature = DishwasherAlarm::Feature;
namespace Commands = DishwasherAlarm::Commands;
namespace Events = DishwasherAlarm::Events;
```

Attributes 매핑:

```cpp
namespace Mask      = DishwasherAlarm::Attributes::Mask;
namespace Latch     = DishwasherAlarm::Attributes::Latch;
namespace State     = DishwasherAlarm::Attributes::State;
namespace Supported = DishwasherAlarm::Attributes::Supported;
```

다음 namespace도 `DishwasherAlarm::Attributes`에서 매핑합니다.

- `GeneratedCommandList`
- `AcceptedCommandList`
- `AttributeList`
- `FeatureMap`
- `ClusterRevision`

`kMandatoryMetadata`에는 다음 entries가 포함됩니다.

- `Mask::kMetadataEntry`
- `State::kMetadataEntry`
- `Supported::kMetadataEntry`

### 내부 멤버

```cpp
const BitMask<AlarmBase::Feature> mFeature;
const uint32_t mClusterRevision;
const bool mSupportsModifyEnabledAlarms;
AlarmBase::Delegate & mDelegate;

AlarmBase::AlarmMap mMask{};
const AlarmBase::AlarmMap mLatch;
AlarmBase::AlarmMap mState{};
const AlarmBase::AlarmMap mSupported;
```

주요 내부 메서드:

```cpp
Protocols::InteractionModel::Status SetStateInternal(
    const AlarmBase::AlarmMap & newState,
    bool ignoreLatchState);

DataModel::ActionReturnStatus HandleReset(
    const AlarmBase::AlarmMap & alarms);

DataModel::ActionReturnStatus HandleModifyEnabledAlarms(
    const AlarmBase::AlarmMap & mask);
```

`SendNotifyEvent()`는 다음 signature의 pure virtual protected method입니다.

```cpp
virtual void SendNotifyEvent(
    AlarmBase::AlarmMap becameActive,
    AlarmBase::AlarmMap becameInactive,
    AlarmBase::AlarmMap newState,
    AlarmBase::AlarmMap mask) = 0;
```