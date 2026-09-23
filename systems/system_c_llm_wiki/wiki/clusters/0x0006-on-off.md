---
entity: On/Off
ids: ['0x0006']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml', 'src/app/clusters/on-off-server/on-off-server.h', 'src/app/clusters/on-off-server/OnOffDelegate.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.cpp', 'src/app/clusters/on-off-server/OnOffCluster.cpp', 'src/app/clusters/on-off-server/OnOffEffectDelegate.h', 'src/app/clusters/on-off-server/OnOffCluster.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.h', 'data_model/1.7/clusters/OnOff.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# On/Off

## 스펙

- 클러스터: `On/Off Cluster`
- 클러스터 ID: `0x0006`
- Revision: `7`
- 분류:
  - hierarchy: `base`
  - role: `application`
  - picsCode: `OO`
  - scope: `Endpoint`
- 설명: 장치를 `On` 및 `Off` 상태 사이로 전환하기 위한 속성과 명령을 제공한다.

### Revision 이력

| Revision | 내용 |
|---:|---|
| `1` | 필수 전역 `ClusterRevision` 속성 추가 |
| `2` | `StartUpOnOff` 추가 |
| `3` | `FeatureMap` 전역 속성 및 `Level Control`, `Lighting` feature 지원 추가 |
| `4` | 새로운 data model 형식 및 표기법 적용 |
| `5` | `Dead Front` 동작 및 관련 `FeatureMap` 항목 추가 |
| `6` | `OffOnly` feature 및 관련 `FeatureMap` 항목 추가 |
| `7` | `OnTime`, `OffWaitTime` 속성에 `Q` quality 추가 |

### Features

| Bit | Code | Name | 설명 |
|---:|---|---|---|
| `0` | `LT` | `Lighting` | 조명 애플리케이션을 지원하는 동작 |
| `1` | `DF` | `DeadFrontBehavior` | `Dead Front` 동작을 지원하는 장치 |
| `2` | `OFFONLY` | `OffOnly` | `OffOnly Feature`를 지원하는 장치 |

`LT`와 `DF`는 `OFFONLY`와 함께 사용할 수 없다. `OFFONLY`는 `LT` 또는 `DF`와 함께 사용할 수 없다.

### Data types

#### `StartUpOnOffEnum`

| 값 | 항목 | 동작 |
|---:|---|---|
| `0x00` | `Off` | `OnOff` 속성을 `FALSE`로 설정 |
| `0x01` | `On` | `OnOff` 속성을 `TRUE`로 설정 |
| `0x02` | `Toggle` | 이전 `OnOff` 값의 반대 값으로 설정 |

#### `EffectIdentifierEnum`

| 값 | 항목 | 설명 |
|---:|---|---|
| `0x00` | `DelayedAllOff` | Delayed All Off |
| `0x01` | `DyingLight` | Dying Light |

#### `DelayedAllOffEffectVariantEnum`

| 값 | 항목 | 설명 |
|---:|---|---|
| `0x00` | `DelayedOffFastFade` | 0.8초 동안 `Off`로 fade |
| `0x01` | `NoFade` | Fade 없음 |
| `0x02` | `DelayedOffSlowFade` | 0.8초 동안 50% dim down 후 12초 동안 `Off`로 fade |

#### `DyingLightEffectVariantEnum`

| 값 | 항목 | 설명 |
|---:|---|---|
| `0x00` | `DyingLightFadeOff` | 0.5초 동안 20% dim up 후 1초 동안 `Off`로 fade |

#### `OnOffControlBitmap`

| Bit | Field | 설명 |
|---:|---|---|
| `0` | `AcceptOnlyWhenOn` | 장치가 `On` 상태일 때만 명령을 수락하도록 지정 |

### Attributes

| ID | 이름 | 타입 | Access | Quality | 조건 |
|---|---|---|---|---|---|
| `0x0000` | `OnOff` | `bool` | 읽기 | `scene`, `persistence="nonVolatile"` | 필수 |
| `0x4000` | `GlobalSceneControl` | `bool` | 읽기 | - | `LT` 필요 |
| `0x4001` | `OnTime` | `uint16` | 읽기/쓰기 | `quieterReporting` | `LT` 필요 |
| `0x4002` | `OffWaitTime` | `uint16` | 읽기/쓰기 | `quieterReporting` | `LT` 필요 |
| `0x4003` | `StartUpOnOff` | `StartUpOnOffEnum` | 읽기/쓰기 | `nullable`, `persistence="nonVolatile"` | `LT` 필요 |

- `OnOff`의 읽기 privilege: `view`
- `GlobalSceneControl`의 읽기 privilege: `view`
- `OnTime` 및 `OffWaitTime`의 읽기 privilege: `view`, 쓰기 privilege: `operate`
- `StartUpOnOff`의 읽기 privilege: `view`, 쓰기 privilege: `manage`

### Commands

| ID | 이름 | 방향 | Invoke privilege | 조건 |
|---|---|---|---|---|
| `0x00` | `Off` | `commandToServer` | `operate` | 필수 |
| `0x01` | `On` | `commandToServer` | `operate` | `OFFONLY`가 아니어야 함 |
| `0x02` | `Toggle` | `commandToServer` | `operate` | `OFFONLY`가 아니어야 함 |
| `0x40` | `OffWithEffect` | `commandToServer` | `operate` | `LT` 필요 |
| `0x41` | `OnWithRecallGlobalScene` | `commandToServer` | `operate` | `LT` 필요 |
| `0x42` | `OnWithTimedOff` | `commandToServer` | `operate` | `LT` 필요 |

#### `OffWithEffect`

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `EffectIdentifier` | `EffectIdentifierEnum` |
| `1` | `EffectVariant` | `enum8` |

`OffWithEffect`는 향상된 fade 방식으로 장치를 `Off` 상태로 전환한다.

#### `OnWithTimedOff`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| `0` | `OnOffControl` | `OnOffControlBitmap` | `0`~`1` |
| `1` | `OnTime` | `uint16` | 최대 `0xFFFE` |
| `2` | `OffWaitTime` | `uint16` | 최대 `0xFFFE` |

`OnWithTimedOff`는 지정된 시간 동안 장치를 `On` 상태로 유지하고, 이후 장치가 다시 켜지는 것을 제한하기 위한 guarded `Off` 시간을 설정한다.

## SDK 정의

### Cluster 정의

- 이름: `On/Off`
- Cluster ID: `0x0006`
- Domain: `General`
- Define: `ON_OFF_CLUSTER`
- Client: 지원
- Server: 지원
- Global attribute:
  - ID: `0xFFFD`
  - 값: `7`

### Enum 및 Bitmap

```text
StartUpOnOffEnum : enum8
  Off    = 0x00
  On     = 0x01
  Toggle = 0x02

EffectIdentifierEnum : enum8
  DelayedAllOff = 0x00
  DyingLight    = 0x01

DelayedAllOffEffectVariantEnum : enum8
  DelayedOffFastFade = 0x00
  NoFade             = 0x01
  DelayedOffSlowFade = 0x02

DyingLightEffectVariantEnum : enum8
  DyingLightFadeOff = 0x00

OnOffControlBitmap : bitmap8
  AcceptOnlyWhenOn = 0x01
```

### SDK Attributes

| ID | 이름 | Define | 타입 | 특성 |
|---|---|---|---|---|
| `0x0000` | `OnOff` | `ON_OFF` | `boolean` | Server |
| `0x4000` | `GlobalSceneControl` | `GLOBAL_SCENE_CONTROL` | `boolean` | Server, optional, `LT` |
| `0x4001` | `OnTime` | `ON_TIME` | `int16u` | Server, writable, optional, `LT` |
| `0x4002` | `OffWaitTime` | `OFF_WAIT_TIME` | `int16u` | Server, writable, optional, `LT` |
| `0x4003` | `StartUpOnOff` | `START_UP_ON_OFF` | `StartUpOnOffEnum` | Server, writable, nullable, optional, `LT` |

`StartUpOnOff`에는 `manage` privilege를 요구하는 쓰기 access가 정의되어 있다.

### SDK Commands

| ID | 이름 | Source | 특성 |
|---|---|---|---|
| `0x00` | `Off` | `client` | 필수 |
| `0x01` | `On` | `client` | optional, `OFFONLY`가 아니어야 함 |
| `0x02` | `Toggle` | `client` | optional, `OFFONLY`가 아니어야 함 |
| `0x40` | `OffWithEffect` | `client` | optional, `LT` |
| `0x41` | `OnWithRecallGlobalScene` | `client` | optional, `LT` |
| `0x42` | `OnWithTimedOff` | `client` | optional, `LT` |

## 구현

### 구현 파일

- `src/app/clusters/on-off-server/on-off-server.h`
- `src/app/clusters/on-off-server/OnOffDelegate.h`
- `src/app/clusters/on-off-server/OnOffCluster.h`
- `src/app/clusters/on-off-server/OnOffCluster.cpp`
- `src/app/clusters/on-off-server/OnOffLightingCluster.h`
- `src/app/clusters/on-off-server/OnOffLightingCluster.cpp`
- `src/app/clusters/on-off-server/OnOffEffectDelegate.h`

### `OnOffCluster`

`OnOffCluster`는 `On/Off` server cluster를 구현한다. `Lighting` feature는 지원하지 않는다.

#### `Context` 및 `Defaults`

```cpp
struct Defaults
{
    bool onOff;
};

struct Context
{
    TimerDelegate & timerDelegate;
    BitMask<OnOff::Feature> featureMap = {};
    Defaults defaults = {};
};
```

생성자는 `supportedFeatures`를 사용해 `featureMap`이 구현 가능한 feature의 부분집합인지 검증한다. `OFFONLY` feature는 다른 feature와 함께 사용할 수 없다.

#### Delegate 연동

`OnOffCluster`는 여러 `OnOffDelegate`를 등록할 수 있다.

```cpp
void AddDelegate(OnOffDelegate * delegate);
void RemoveDelegate(OnOffDelegate * delegate);
```

`SetOnOff(bool on)`은 다음 작업을 수행한다.

1. 값이 변경되지 않았으면 종료한다.
2. `OnOff` 속성을 갱신한다.
3. `Attributes::OnOff::Id` 변경을 통지한다.
4. `AttributePersistence`를 통해 값을 저장한다.
5. 등록된 delegate의 `OnOnOffChanged(bool on)`을 호출한다.

#### Startup

`Startup(ServerClusterContext & context)`에서 `OnOff` 값을 persistent storage로부터 읽는다. 초기화 후 등록된 각 delegate에 `OnOffStartup(mOnOff)`를 호출한다.

#### 기본 명령 처리

`InvokeCommand`는 다음 명령을 처리한다.

- `Commands::Off::Id`: `SetOnOff(false)`
- `Commands::On::Id`: `SetOnOff(true)`
- `Commands::Toggle::Id`: `SetOnOff(!mOnOff)`

`OFFONLY` feature가 활성화된 경우 `AcceptedCommands`에는 `Commands::Off::kMetadataEntry`만 포함된다.

#### Scene 처리

`OnOffCluster`는 `scenes::DefaultSceneHandlerImpl`을 상속하며 다음 기능을 제공한다.

- `SupportsCluster`
- `SerializeSave`
- `ApplyScene`

Scene 데이터에는 `Attributes::OnOff::Id` 값이 저장된다. `timeMs`가 `0`보다 크면 `SceneTransitionTimer`를 사용해 지연 전환하고, 그렇지 않으면 즉시 `SetOnOff`를 호출한다.

### `OnOffDelegate`

`OnOffDelegate`는 애플리케이션별 `On/Off` 동작을 구현하기 위한 인터페이스다.

```cpp
class OnOffDelegate : public IntrusiveListNodeBase<IntrusiveMode::AutoUnlink>
{
public:
    virtual ~OnOffDelegate() = default;

    virtual void OnOffStartup(bool on) = 0;
    virtual void OnOnOffChanged(bool on) = 0;
};
```

- `OnOffStartup(bool on)`:
  - Cluster startup 시 호출된다.
  - 조명 애플리케이션에서는 `StartUpOnOffEnum`에 따른 최종 값이 전달된다.
  - startup의 일부로 `OnOnOffChanged`가 호출되지는 않는다.
- `OnOnOffChanged(bool on)`:
  - `OnOff` 속성이 변경될 때 호출된다.
  - delegate는 하드웨어 상태를 새 값에 맞게 갱신해야 한다.

### `OnOffLightingCluster`

`OnOffLightingCluster`는 `OnOffCluster`에 `Lighting` 기능을 추가한 구현이다.

지원 기능:

- `GlobalSceneControl`
- `OnTime`
- `OffWaitTime`
- `StartUpOnOff`
- `OffWithEffect`
- `OnWithRecallGlobalScene`
- `OnWithTimedOff`

기본 생성 시 `Feature::kLighting`, `Feature::kDeadFrontBehavior`를 사용한다.

#### `StartupType`

```cpp
enum class StartupType
{
    kRegular,
    kOTA,
};
```

`StartupType::kOTA`인 경우 `StartUpOnOff` 동작을 적용하지 않는다. OTA restart에서는 restart 이전의 `OnOff` 값을 유지한다.

일반 startup에서는 `StartUpOnOff` 값에 따라 다음 동작을 수행한다.

- `StartUpOnOffEnum::kOff`: `OnOff`를 `false`로 설정
- `StartUpOnOffEnum::kOn`: `OnOff`를 `true`로 설정
- `StartUpOnOffEnum::kToggle`: 현재 `OnOff` 값을 반전
- 유효하지 않은 값: 기존 상태 유지

상태가 변경되면 변경된 `OnOff` 값도 persistent storage에 저장한다. 이후 각 delegate에 `OnOffStartup(mOnOff)`를 호출한다.

#### `OnTime` 및 `OffWaitTime`

- `OnTime`과 `OffWaitTime`은 `1/10`초 단위로 동작한다.
- 값이 `0xFFFF`이면 timer를 시작하지 않는다.
- `SetOnTime` 및 `SetOffWaitTime`은 값이 변경될 때 timer를 갱신한다.
- 값의 차이가 `kValueDeltaReportTrigger`보다 크거나 새 값이 `0`이면 attribute 변경을 통지한다.
- `kValueDeltaReportTrigger` 값은 `10`이다.

`OnOffLightingCluster`는 다음 상태를 관리한다.

| 상태 | 설명 |
|---|---|
| `ON` | `On`, timer 없음 |
| `OFF` | `Off`, timer 없음 |
| `TIMED_ON` | `On`, `mOnTime`이 감소하며 `0`에서 `Off`로 전환 |
| `TIMED_OFF` | `Off`, `mOffWaitTime`이 감소하며 `0`에서 `On`으로 전환 |

#### `SetOnOffWithTimeReset`

`SetOnOffWithTimeReset(bool on)`은 다른 Cluster와의 연동을 위한 `OnOff` 변경 API다.

- `on == false`이면 `OnTime`을 `0`으로 설정한다.
- `on == true`이고 `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정한다.
- 이후 `SetOnOff(on)`을 호출한다.

#### 기본 명령 동작

- `HandleOff`
  - `SetOnOffFromCommand(false)` 호출
  - `OnTime`을 `0`으로 설정
  - timer 갱신
- `HandleOn`
  - `SetOnOffFromCommand(true)` 호출
  - `GlobalSceneControl`을 `true`로 설정
  - `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정
  - timer 갱신
- `HandleToggle`
  - 현재 `OnOff`가 `true`이면 `HandleOff`
  - 그렇지 않으면 `HandleOn`

#### `OffWithEffect`

`HandleOffWithEffect`는 `Commands::OffWithEffect::DecodableType`을 디코드한 뒤 `OnOffEffectDelegate::TriggerEffect`를 호출한다.

`GlobalSceneControl`이 `true`인 경우:

1. `ScenesIntegrationDelegate`가 있으면 현재 global scene을 저장한다.
2. `effectIdentifier`와 `effectVariant`로 효과를 실행한다.
3. `GlobalSceneControl`을 `false`로 설정한다.
4. `OnOff`를 `false`로 설정한다.
5. `OnTime`을 `0`으로 설정한다.

`GlobalSceneControl`이 `false`이면 일반적인 `HandleOff`를 수행한다.

#### `OnWithRecallGlobalScene`

`HandleOnWithRecallGlobalScene`은 다음과 같이 동작한다.

- `GlobalSceneControl`이 `true`이면 명령을 버리고 성공을 반환한다.
- `ScenesIntegrationDelegate`가 있으면 global scene을 복원한다.
- Scene을 복원할 수 없으면 오류를 기록하고 `OnOff`를 `true`로 설정한다.
- `GlobalSceneControl`을 `true`로 설정한다.
- `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정한다.
- timer를 갱신한다.

#### `OnWithTimedOff`

`HandleOnWithTimedOff`는 다음 입력을 검증한다.

- `OnTime <= 0xFFFE`
- `OffWaitTime <= 0xFFFE`

`OnOffControlBitmap::kAcceptOnlyWhenOn`이 설정되어 있고 현재 `OnOff`가 `false`이면 명령을 성공으로 처리하지만 버린다.

상태 전환 동작:

- 현재 `On` 상태이고 `mOnTime > 0`이면 `OnTime`을 현재 값과 명령 값 중 큰 값으로 설정한다.
- 현재 `On` 상태이고 `mOnTime == 0`이면 `TIMED_ON`으로 전환한다.
- 현재 `Off` 상태이고 `mOffWaitTime > 0`이면 `OnTime`은 무시하고 `OffWaitTime`을 현재 값과 명령 값 중 작은 값으로 설정한다.
- 현재 `Off` 상태이고 `mOffWaitTime == 0`이면 `OnTime` 및 `OffWaitTime`을 명령 값으로 설정하고 `TIMED_ON`으로 전환한다.
- 시간이 변경되면 `UpdateTimer()`를 호출한다.

#### Timer 처리

`TimerFired()`는 현재 상태에 따라 다음을 수행한다.

- `GetOnOff()`가 `true`인 경우:
  - `mOnTime`을 감소시킨다.
  - `mOnTime`이 `0`이 되면 `OffWaitTime`을 `0`으로 설정하고 `SetOnOff(false)`를 호출한다.
- `GetOnOff()`가 `false`인 경우:
  - `mOffWaitTime`을 감소시킨다.
  - `mOffWaitTime`이 `0`이 될 때 attribute 변경을 통지한다.
  - timer를 갱신한다.

timer 간격은 `100ms`다.

### `OnOffEffectDelegate`

`OnOffEffectDelegate`는 조명 효과를 처리하는 인터페이스다.

```cpp
virtual DataModel::ActionReturnStatus TriggerEffect(
    OnOff::EffectIdentifierEnum effectId,
    uint8_t effectVariant);
```

기본 `TriggerEffect` 구현은 다음과 같이 dispatch한다.

- `OnOff::EffectIdentifierEnum::kDelayedAllOff`
  - `TriggerDelayedAllOff`
- `OnOff::EffectIdentifierEnum::kDyingLight`
  - `TriggerDyingLight`
- 그 외 값
  - `InvalidCommand`

기본 `TriggerDelayedAllOff` 및 `TriggerDyingLight` 구현은 `UnsupportedCommand`를 반환한다.

### Backwards compatibility header

`src/app/clusters/on-off-server/on-off-server.h`는 codegen Cluster 구현과의 backwards compatibility를 위해 제공된다. 실제로는 다음 파일을 include한다.

```cpp
#include "codegen/on-off-server.h"
```

## 관련 문서

- `data_model/1.7/clusters/OnOff.xml`
- `src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml`
- `src/app/clusters/on-off-server/on-off-server.h`
- `src/app/clusters/on-off-server/OnOffDelegate.h`
- `src/app/clusters/on-off-server/OnOffCluster.h`
- `src/app/clusters/on-off-server/OnOffCluster.cpp`
- `src/app/clusters/on-off-server/OnOffLightingCluster.h`
- `src/app/clusters/on-off-server/OnOffLightingCluster.cpp`
- `src/app/clusters/on-off-server/OnOffEffectDelegate.h`

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
