---
entity: Refrigerator Alarm
ids: ['0x0057']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml', 'src/app/clusters/alarm-base-server/README.md', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp', 'src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h', 'data_model/1.7/clusters/RefrigeratorAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Refrigerator Alarm

## 스펙

- 스펙 파일: `data_model/1.7/clusters/RefrigeratorAlarm.xml`
- 클러스터:
  - 이름: `Refrigerator Alarm Cluster`
  - 클러스터 ID: `0x0057`
  - revision: `1`
  - classification: `derived`
  - base cluster: `Alarm Base`
  - role: `application`
  - PICS code: `REFALM`
  - scope: `Endpoint`
- revision history:
  - revision `1`: `Initial revision`

### 기능

| bit | code | name | 설명 | 적합성 |
|---:|---|---|---|---|
| 0 | `RESET` | `Reset` | Supports the ability to reset alarms | `disallowConform` |

### 데이터 타입

#### `AlarmBitmap`

| bit | 이름 | 설명 | 적합성 |
|---:|---|---|---|
| 0 | `DoorOpen` | The cabinet's door has been open for a vendor defined amount of time. | `mandatoryConform` |

### 명령

| ID | 이름 | 적합성 |
|---|---|---|
| `0x01` | `ModifyEnabledAlarms` | `disallowConform` |

## SDK 정의

- SDK 데이터 모델 파일: `src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml`
- domain: `Appliances`
- 설명: `Attributes and commands for configuring the Refrigerator alarm.`
- 클러스터 ID: `0x0057`
- define: `REFRIGERATOR_ALARM_CLUSTER`
- client: 활성화, `tick="false"`, `init="false"`
- server: 활성화, `tick="false"`, `init="false"`

### 비트맵

#### `AlarmBitmap`

- type: `bitmap32`
- cluster code: `0x0057`

| 이름 | mask |
|---|---|
| `DoorOpen` | `0x01` |

### 속성

| side | code | 이름 | define | type | max |
|---|---|---|---|---|---|
| server | `0x0000` | `Mask` | `MASK` | `AlarmBitmap` | `0x00000001` |
| server | `0x0002` | `State` | `STATE` | `AlarmBitmap` | `0x00000001` |
| server | `0x0003` | `Supported` | `SUPPORTED` | `AlarmBitmap` | `0x00000001` |
| either | `0xFFFD` | — | — | — | value `1` |

### 이벤트

#### `Notify`

- event code: `0x00`
- side: server
- priority: `info`
- 설명: `This event SHALL be generated when one or more alarms change state.`

| field id | 이름 | type | max |
|---:|---|---|---|
| 0 | `Active` | `AlarmBitmap` | `0x00000001` |
| 1 | `Inactive` | `AlarmBitmap` | `0x00000001` |
| 2 | `State` | `AlarmBitmap` | `0x00000001` |
| 3 | `Mask` | `AlarmBitmap` | `0x00000001` |

## 구현

구현 경로:

- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h`
- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp`
- `src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h`
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h`
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp`

### 클래스 구조

`RefrigeratorAlarmCluster`는 `AlarmBaseCluster`를 상속합니다.

```cpp
class RefrigeratorAlarmCluster : public AlarmBaseCluster
```

생성자는 `RefrigeratorAlarm::Id`와 `RefrigeratorAlarm::kRevision`을 사용해 기반 클래스를 초기화합니다.

```cpp
RefrigeratorAlarmCluster(EndpointId endpointId, const Config & config) :
    AlarmBaseCluster(endpointId, { RefrigeratorAlarm::Id, RefrigeratorAlarm::kRevision }, config)
{}
```

`SendNotifyEvent`를 재정의하여 `Notify` 이벤트를 생성합니다.

### `RefrigeratorAlarmServer`

`RefrigeratorAlarmServer`는 다음 API를 제공합니다.

```cpp
static RefrigeratorAlarmServer & Instance();
```

#### 값 읽기

```cpp
GetMaskValue(
    chip::EndpointId endpoint,
    chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> * mask);

GetStateValue(
    chip::EndpointId endpoint,
    chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> * state);

GetSupportedValue(
    chip::EndpointId endpoint,
    chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> * suppported);
```

#### 값 쓰기

```cpp
SetMaskValue(
    chip::EndpointId endpoint,
    const chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> mask);

SetStateValue(
    chip::EndpointId endpoint,
    chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> newState);
```

클러스터를 찾을 수 없는 경우 `Status::UnsupportedEndpoint`를 반환합니다. 읽기 API의 출력 포인터가 `nullptr`이 아니면 클러스터 값을 출력 인자에 기록하고 `Status::Success`를 반환합니다.

### 속성 접근자

namespace `chip::app::Clusters::RefrigeratorAlarm::Attributes`에 다음 접근자가 정의됩니다.

#### `Mask`

```cpp
Protocols::InteractionModel::Status Get(
    EndpointId endpoint,
    BitMask<AlarmMap> * value);

Protocols::InteractionModel::Status Set(
    EndpointId endpoint,
    BitMask<AlarmMap> value);
```

#### `State`

```cpp
Protocols::InteractionModel::Status Get(
    EndpointId endpoint,
    BitMask<AlarmMap> * value);

Protocols::InteractionModel::Status Set(
    EndpointId endpoint,
    BitMask<AlarmMap> value);
```

#### `Supported`

```cpp
Protocols::InteractionModel::Status Get(
    EndpointId endpoint,
    BitMask<AlarmMap> * value);
```

`Supported`에는 `Set` 접근자가 없습니다.

### 코드 생성 통합

`MatterRefrigeratorAlarmClusterInitCallback`은 `CodegenClusterIntegration::RegisterServer`를 호출하여 서버 클러스터를 등록합니다.

등록 설정은 다음과 같습니다.

```cpp
{
    .endpointId                = endpointId,
    .clusterId                 = RefrigeratorAlarm::Id,
    .fixedClusterInstanceCount = kRefrigeratorAlarmFixedClusterCount,
    .maxClusterInstanceCount   = kRefrigeratorAlarmMaxClusterCount,
    .fetchFeatureMap           = false,
    .fetchOptionalAttributes   = false,
}
```

`RefrigeratorAlarmIntegrationDelegate::CreateRegistration`은 다음 기본값을 사용합니다.

- `Supported::GetDefault(endpointId, supportedDefault)`로 `Supported` 기본값을 읽음
- `Mask::GetDefault(endpointId, maskDefault)`로 `Mask` 기본값을 읽고 `cluster.SetMask(...)` 호출
- `State::GetDefault(endpointId, stateDefault)`로 `State` 기본값을 읽고 `cluster.SetState(...)` 호출
- `supportsModifyEnabledAlarms = false`
- `feature = BitFlags<AlarmBase::Feature>()`

클러스터 인스턴스 수는 다음 상수로 계산됩니다.

```cpp
constexpr size_t kRefrigeratorAlarmFixedClusterCount =
    RefrigeratorAlarm::StaticApplicationConfig::kFixedClusterConfig.size();

constexpr size_t kRefrigeratorAlarmMaxClusterCount =
    kRefrigeratorAlarmFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT;
```

다음 조건이 정적으로 검증됩니다.

```cpp
static_assert(
    kRefrigeratorAlarmFixedClusterCount ==
        MATTER_DM_REFRIGERATOR_ALARM_CLUSTER_SERVER_ENDPOINT_COUNT,
    "RefrigeratorAlarm static cluster config must match ZAP server endpoint count");

static_assert(
    kRefrigeratorAlarmMaxClusterCount <= kEmberInvalidEndpointIndex,
    "RefrigeratorAlarm cluster table size error");
```

### 초기화 및 종료

```cpp
void MatterRefrigeratorAlarmClusterInitCallback(EndpointId endpointId);
```

```cpp
void MatterRefrigeratorAlarmClusterShutdownCallback(
    EndpointId endpointId,
    MatterClusterShutdownType shutdownType);
```

초기화 시 `CodegenClusterIntegration::RegisterServer`를 호출하고, 종료 시 `CodegenClusterIntegration::UnregisterServer`를 호출합니다.

다음 weak callback도 정의됩니다.

```cpp
__attribute__((weak))
void MatterRefrigeratorAlarmPluginServerInitCallback() {}

__attribute__((weak))
void MatterRefrigeratorAlarmPluginServerShutdownCallback() {}
```

### 클러스터 조회

```cpp
RefrigeratorAlarmCluster * FindClusterOnEndpoint(EndpointId endpointId);
```

`FindClusterOnEndpoint`는 `CodegenClusterIntegration::FindClusterOnEndpoint`를 통해 지정된 `endpointId`의 `RefrigeratorAlarmCluster`를 반환합니다.

### `Notify` 이벤트 생성

`RefrigeratorAlarmCluster::SendNotifyEvent`는 다음 값을 `RefrigeratorAlarm::Events::Notify::Type`으로 변환합니다.

- `becameActive` → `active`
- `becameInactive` → `inactive`
- `newState` → `state`
- `mask` → `mask`

각 값은 다음 타입으로 변환됩니다.

```cpp
BitMask<RefrigeratorAlarm::AlarmBitmap>
```

이벤트 생성은 다음 호출로 수행됩니다.

```cpp
mContext->interactionContext.eventsGenerator.GenerateEvent(
    event,
    mPath.mEndpointId);
```

`mContext == nullptr`이면 이벤트를 생성하지 않고 반환합니다.

### Alarm Base 관련 동작

`src/app/clusters/alarm-base-server/README.md`에 따르면 `Alarm Base`는 자체 클러스터 ID가 없는 pseudo cluster이며, `Dishwasher Alarm` 및 `Refrigerator Alarm`과 같은 alarm cluster가 상속하는 기반 클러스터입니다.

`Supported`와 `Latch`는 fixed attributes로 설명됩니다.

- `AlarmBaseCluster::Config`의 `.supported`와 `.latch`로 생성 시 한 번 초기화
- `AlarmBaseCluster`의 `const` 멤버인 `mSupported`, `mLatch`에 저장
- 읽기 전용 접근자:
  - `GetSupported()`
  - `GetLatch()`
- 해당 속성에 대한 `WriteAttribute`는 구현하지 않음

기존 `DishwasherAlarmServer`의 다음 메서드는 제거되었습니다.

- `SetSupportedValue()`
- `SetLatchValue()`

런타임에 변경 가능한 상태 API는 다음과 같습니다.

- `SetMask()` / `GetMask()`
- `SetState()` / `GetState()`
- `ResetLatchedAlarms()` (`Reset` 기능이 활성화된 경우)

## 관련 문서

- `src/app/clusters/alarm-base-server/README.md`
- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h`
- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp`
- `src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h`
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h`
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp`
- `src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml`
- `data_model/1.7/clusters/RefrigeratorAlarm.xml`