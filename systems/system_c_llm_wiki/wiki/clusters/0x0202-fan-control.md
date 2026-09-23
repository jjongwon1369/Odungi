---
entity: Fan Control
ids: ['0x0202']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml', 'src/app/clusters/fan-control-server/FanControlCluster.cpp', 'src/app/clusters/fan-control-server/CodegenIntegration.h', 'src/app/clusters/fan-control-server/CodegenIntegration.cpp', 'src/app/clusters/fan-control-server/README.md', 'src/app/clusters/fan-control-server/fan-control-delegate.h', 'src/app/clusters/fan-control-server/fan-control-server.h', 'src/app/clusters/fan-control-server/FanControlCluster.h', 'data_model/1.7/clusters/FanControl.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

Fan Control 클러스터는 난방/냉방 시스템의 팬을 제어하기 위한 인터페이스입니다. 팬 모드, 속도, airflow direction, wind mode 및 rocking 동작을 설정할 수 있습니다.

- 클러스터 이름: `Fan Control`
- 클러스터 ID: `0x0202`
- 도메인: `HVAC`
- PICS 코드: `FAN`
- Revision: `7`
- 역할: Endpoint 범위의 application 클러스터
- SDK 정의: `FAN_CONTROL_CLUSTER`
- 설명: `An interface for controlling a fan in a heating/cooling system.`

## 스펙

### 기능

| Bit | Code | Name | Summary |
|---:|---|---|---|
| 0 | `SPD` | `MultiSpeed` | `0-SpeedMax Fan Speeds` |
| 1 | `AUT` | `Auto` | `Automatic mode supported for fan speed` |
| 2 | `RCK` | `Rocking` | `Rocking movement supported` |
| 3 | `WND` | `Wind` | `Wind emulation supported` |
| 4 | `STEP` | `Step` | `Step command supported` |
| 5 | `DIR` | `AirflowDirection` | `Airflow Direction attribute is supported` |

모든 기능은 optional conform입니다.

### 데이터 타입

#### `AirflowDirectionEnum`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0` | `Forward` | `Airflow is in the forward direction` |
| `1` | `Reverse` | `Airflow is in the reverse direction` |

#### `FanModeEnum`

| 값 | 이름 | 설명 및 적합성 |
|---:|---|---|
| `0` | `Off` | `Fan is off`, mandatory |
| `1` | `Low` | `Fan using low speed`, optional |
| `2` | `Medium` | `Fan using medium speed`, `Low`가 필요하며 optional |
| `3` | `High` | `Fan using high speed`, mandatory |
| `4` | `On` | obsolete |
| `5` | `Auto` | `Fan is using auto mode`, `AUT` 기능 필요 |
| `6` | `Smart` | `Fan is using smart mode`, obsolete |

#### `FanModeSequenceEnum`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0` | `OffLowMedHigh` | `Fan is capable of off, low, medium and high modes` |
| `1` | `OffLowHigh` | `Fan is capable of off, low and high modes` |
| `2` | `OffLowMedHighAuto` | `Fan is capable of off, low, medium, high and auto modes` |
| `3` | `OffLowHighAuto` | `Fan is capable of off, low, high and auto modes` |
| `4` | `OffHighAuto` | `Fan is capable of off, high and auto modes` |
| `5` | `OffHigh` | `Fan is capable of off and high modes` |

`OffLowMedHigh`, `OffLowHigh`, `OffHigh`는 `AUT` 기능이 없는 경우에 사용하며, `OffLowMedHighAuto`, `OffLowHighAuto`, `OffHighAuto`는 `AUT` 기능과 함께 사용합니다.

#### `StepDirectionEnum`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0` | `Increase` | `Step moves in increasing direction` |
| `1` | `Decrease` | `Step moves in decreasing direction` |

#### `RockBitmap`

| Bit | 이름 | 설명 |
|---:|---|---|
| 0 | `RockLeftRight` | `Indicate rock left to right` |
| 1 | `RockUpDown` | `Indicate rock up and down` |
| 2 | `RockRound` | `Indicate rock around` |

#### `WindBitmap`

| Bit | 이름 | 설명 |
|---:|---|---|
| 0 | `SleepWind` | `Indicate sleep wind` |
| 1 | `NaturalWind` | `Indicate natural wind` |

### 속성

| ID | 이름 | 타입 | 접근 | 적합성 및 제약 |
|---|---|---|---|---|
| `0x0000` | `FanMode` | `FanModeEnum` | 읽기/쓰기 | mandatory, nonVolatile |
| `0x0001` | `FanModeSequence` | `FanModeSequenceEnum` | 읽기 | mandatory, fixed |
| `0x0002` | `PercentSetting` | `percent` | 읽기/쓰기 | mandatory, nullable, 최대 `100` |
| `0x0003` | `PercentCurrent` | `percent` | 읽기 | mandatory, quieter reporting, 최대 `100` |
| `0x0004` | `SpeedMax` | `uint8` | 읽기 | `SPD` 기능 필요, `1`~`100`, fixed |
| `0x0005` | `SpeedSetting` | `uint8` | 읽기/쓰기 | `SPD` 기능 필요, nullable, `SpeedMax` 이하 |
| `0x0006` | `SpeedCurrent` | `uint8` | 읽기 | `SPD` 기능 필요, quieter reporting, `SpeedMax` 이하 |
| `0x0007` | `RockSupport` | `RockBitmap` | 읽기 | `RCK` 기능 필요, 최소값 `1`, fixed |
| `0x0008` | `RockSetting` | `RockBitmap` | 읽기/쓰기 | `RCK` 기능 필요 |
| `0x0009` | `WindSupport` | `WindBitmap` | 읽기 | `WND` 기능 필요, 최소값 `1`, fixed |
| `0x000A` | `WindSetting` | `WindBitmap` | 읽기/쓰기 | `WND` 기능 필요 |
| `0x000B` | `AirflowDirection` | `AirflowDirectionEnum` | 읽기/쓰기 | `DIR` 기능 필요 |

### 명령

#### `Step`

- Command ID: `0x00`
- 방향: `commandToServer`
- Invoke privilege: `operate`
- `STEP` 기능 필요
- 응답: `Y`

`Step` 명령은 `FanMode`, `PercentSetting`, `SpeedSetting`과 같은 속성을 직접 사용하는 대신 팬의 speed-oriented attributes를 단계적으로 변경합니다.

| Field ID | 이름 | 타입 | 적합성 |
|---:|---|---|---|
| `0` | `Direction` | `StepDirectionEnum` | mandatory |
| `1` | `Wrap` | `bool` | optional |
| `2` | `LowestOff` | `bool` | optional |

## SDK 정의

### 파일

- `src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml`
- `src/app/clusters/fan-control-server/FanControlCluster.h`
- `src/app/clusters/fan-control-server/fan-control-delegate.h`
- `src/app/clusters/fan-control-server/CodegenIntegration.h`

### `FanControlCluster::Config`

`FanControlCluster::Config`는 팬별 지원 기능을 fluent interface로 설정합니다.

```cpp
Config(EndpointId endpointId, FanControl::Delegate & delegate)
```

지원되는 설정 메서드:

```cpp
Config & WithFanModeSequence(FanControl::FanModeSequenceEnum fanModeSequence);
Config & WithSpeedMax(uint8_t speedMax);
Config & WithRockSupport(BitMask<FanControl::RockBitmap> rockSupport);
Config & WithWindSupport(BitMask<FanControl::WindBitmap> windSupport);
Config & WithAirflowDirection();
Config & WithStep();
```

`WithSpeedMax()`는 `mSpeedMax`를 `1`~`100` 범위로 제한하고 `MultiSpeed` 관련 속성을 optional attributes에 추가합니다.

- `SpeedMax`
- `SpeedSetting`
- `SpeedCurrent`

`WithRockSupport()`는 다음 속성을 추가합니다.

- `RockSupport`
- `RockSetting`

`WithWindSupport()`는 다음 속성을 추가합니다.

- `WindSupport`
- `WindSetting`

`WithAirflowDirection()`은 `AirflowDirection`을 추가합니다.

`WithStep()`은 `Step` command를 활성화합니다.

### `FanControl::Delegate`

`chip::app::Clusters::FanControl::Delegate`는 애플리케이션별 팬 제어 로직을 구현하기 위한 추상 클래스입니다.

필수 메서드:

```cpp
virtual Protocols::InteractionModel::Status HandleStep(
    StepDirectionEnum aDirection,
    bool aWrap,
    bool aLowestOff) = 0;
```

선택적 알림 메서드:

```cpp
virtual void OnFanDriveStateChanged(const FanDriveState & newState) {}
virtual void OnRockSettingChanged(BitMask<RockBitmap> newValue) {}
virtual void OnWindSettingChanged(BitMask<WindBitmap> newValue) {}
virtual void OnAirflowDirectionChanged(AirflowDirectionEnum newValue) {}
```

`FanDriveState`는 다음 상태를 포함합니다.

```cpp
struct FanDriveState
{
    FanModeEnum mode;
    DataModel::Nullable<chip::Percent> percentSetting;
    chip::Percent percentCurrent;
    DataModel::Nullable<uint8_t> speedSetting;
    uint8_t speedCurrent;
};
```

### `FanControlCluster` 주요 메서드

#### Getter

```cpp
FanControl::FanModeEnum GetFanMode() const;
FanControl::FanModeSequenceEnum GetFanModeSequence() const;
DataModel::Nullable<chip::Percent> GetPercentSetting() const;
chip::Percent GetPercentCurrent() const;
DataModel::Nullable<uint8_t> GetSpeedSetting() const;
uint8_t GetSpeedCurrent() const;
uint8_t GetSpeedMax() const;
BitFlags<FanControl::Feature> GetFeatureMap() const;
BitMask<FanControl::RockBitmap> GetRockSupport() const;
BitMask<FanControl::RockBitmap> GetRockSetting() const;
BitMask<FanControl::WindBitmap> GetWindSupport() const;
BitMask<FanControl::WindBitmap> GetWindSetting() const;
FanControl::AirflowDirectionEnum GetAirflowDirection() const;
```

#### Setter

```cpp
Protocols::InteractionModel::Status SetFanMode(FanControl::FanModeEnum value);
Protocols::InteractionModel::Status SetPercentSetting(DataModel::Nullable<chip::Percent> value);
Protocols::InteractionModel::Status SetSpeedSetting(DataModel::Nullable<uint8_t> value);
Protocols::InteractionModel::Status SetRockSetting(BitMask<FanControl::RockBitmap> value);
Protocols::InteractionModel::Status SetWindSetting(BitMask<FanControl::WindBitmap> value);
Protocols::InteractionModel::Status SetAirflowDirection(FanControl::AirflowDirectionEnum value);
bool SetPercentCurrent(chip::Percent value);
bool SetSpeedCurrent(uint8_t value);
```

## 구현

### 파일

- `src/app/clusters/fan-control-server/FanControlCluster.cpp`
- `src/app/clusters/fan-control-server/FanControlCluster.h`
- `src/app/clusters/fan-control-server/fan-control-delegate.h`
- `src/app/clusters/fan-control-server/CodegenIntegration.cpp`
- `src/app/clusters/fan-control-server/CodegenIntegration.h`
- `src/app/clusters/fan-control-server/fan-control-server.h`

### 속성 처리

`ReadAttribute()`는 다음 속성을 처리합니다.

- `ClusterRevision`
- `FeatureMap`
- `FanMode`
- `FanModeSequence`
- `PercentSetting`
- `PercentCurrent`
- `SpeedMax`
- `SpeedSetting`
- `SpeedCurrent`
- `RockSupport`
- `RockSetting`
- `WindSupport`
- `WindSetting`
- `AirflowDirection`

지원되지 않는 속성은 `Status::UnsupportedAttribute`를 반환합니다.

`WriteAttribute()`는 다음 속성의 쓰기를 처리합니다.

- `FanMode`
- `PercentSetting`
- `SpeedSetting`
- `RockSetting`
- `WindSetting`
- `AirflowDirection`

### `FanMode` 처리

`Startup()`에서는 `FanMode`를 `AttributePersistence`에서 복원합니다. 저장된 값이 유효하지 않으면 `FanModeEnum::kOff`로 대체합니다.

`SetFanMode()`의 주요 동작은 다음과 같습니다.

- 알 수 없는 enum 값은 `Status::ConstraintError`를 반환합니다.
- `FanModeSequence`에서 지원하지 않는 모드는 `Status::InvalidInState`를 반환합니다.
- `FanModeEnum::kOn`은 `FanModeEnum::kHigh`로 변환됩니다.
- `FanModeEnum::kSmart`는 `Auto`가 지원되면 `FanModeEnum::kAuto`, 그렇지 않으면 `FanModeEnum::kHigh`로 변환됩니다.
- 변경 후 `ApplyFanModeSideEffects()`를 호출합니다.
- 현재 `FanMode`를 영속 저장합니다.
- `NotifyDelegateFanDriveState()`로 애플리케이션에 알립니다.

`FanModeSequence`에 따른 모드 제한:

- `kLow`: `OffHigh` 및 `OffHighAuto`에서는 지원되지 않습니다.
- `kMedium`: `OffLowMedHigh` 및 `OffLowMedHighAuto`에서만 지원됩니다.
- `kAuto`: `Auto` sequence가 설정된 경우에만 지원됩니다.

### `FanMode`에 따른 side effects

| `FanMode` | `PercentSetting` | `SpeedSetting` | `PercentCurrent` | `SpeedCurrent` |
|---|---:|---:|---:|---:|
| `kOff` | `0` | `0` | `0` | `0` (`MultiSpeed`인 경우) |
| `kLow` | `33` | `1` | 변경하지 않음 | 변경하지 않음 |
| `kMedium` | `66` | `max(1, (mSpeedMax + 1) / 2)` | 변경하지 않음 | 변경하지 않음 |
| `kHigh` | `100` | `mSpeedMax` | 변경하지 않음 | 변경하지 않음 |
| `kAuto` | null | null (`MultiSpeed`인 경우) | 변경하지 않음 | 변경하지 않음 |
| `kOn`, `kSmart`, `kUnknown` | 별도 side effect 없음 | 별도 side effect 없음 | 별도 side effect 없음 | 별도 side effect 없음 |

`PercentCurrent`와 `SpeedCurrent`는 실제로 동작 중인 팬 속도이며 애플리케이션이 관리합니다. 따라서 `*Setting` 속성과 다를 수 있습니다.

### `PercentSetting`과 `SpeedSetting`의 연동

`SetPercentSetting()`:

- null은 `FanModeEnum::kAuto`일 때만 허용됩니다.
- 값이 `100`보다 크면 `Status::ConstraintError`를 반환합니다.
- 값이 `0`이면 `CommitFanModeOffState()`를 호출합니다.
- `MultiSpeed`가 활성화되어 있으면 다음 식으로 `SpeedSetting`을 계산합니다.

```cpp
const uint8_t speedSetting = static_cast<uint8_t>((mSpeedMax * percent + 99) / 100);
```

- 0이 아닌 값은 `ComputeFanModeFromPercent()`를 통해 `FanMode`로 변환합니다.

`SetSpeedSetting()`:

- `MultiSpeed`가 비활성화되어 있으면 변경되지 않습니다.
- null은 `FanModeEnum::kAuto`일 때만 허용됩니다.
- 값이 `mSpeedMax`보다 크면 `Status::ConstraintError`를 반환합니다.
- 값이 `0`이면 `CommitFanModeOffState()`를 호출합니다.
- `PercentSetting`은 다음 식으로 계산됩니다.

```cpp
const chip::Percent percent = static_cast<chip::Percent>((speedSetting * 100) / mSpeedMax);
```

### `RockSetting` 및 `WindSetting`

`SetRockSetting()`과 `SetWindSetting()`은 설정하려는 bit가 각각의 지원 bit에 포함되는지 검사합니다.

```cpp
(rawValue & rawSupport) == rawValue
```

지원되지 않는 bit가 포함되면 `Status::ConstraintError`를 반환합니다.

변경이 성공하면 다음 delegate 메서드를 호출합니다.

- `RockSetting`: `mDelegate.OnRockSettingChanged(mRockSetting)`
- `WindSetting`: `mDelegate.OnWindSettingChanged(mWindSetting)`

`RockSupport`와 `WindSupport`는 읽기 전용입니다.

### `AirflowDirection`

`SetAirflowDirection()`은 알 수 없는 enum 값에 대해 `Status::ConstraintError`를 반환합니다. 변경이 성공하면 다음 delegate 메서드를 호출합니다.

```cpp
mDelegate.OnAirflowDirectionChanged(mAirflowDirection);
```

### `Step` 명령

`InvokeCommand()`는 `Commands::Step::Id`를 처리합니다.

- `Direction`이 알 수 없는 값이면 `Status::ConstraintError`를 반환합니다.
- `Wrap`의 기본값은 `false`입니다.
- `LowestOff`의 기본값은 `true`입니다.
- `mDelegate.HandleStep(commandData.direction, wrapValue, lowestOffValue)`를 호출합니다.
- `STEP` 기능이 비활성화되어 있으면 `Step`이 accepted commands 목록에 포함되지 않습니다.

### Delegate 재진입 방지

`NotifyDelegateFanDriveState()`는 delegate 알림 중 재진입을 방지하기 위해 `mTemporarilyIgnoreFanDriveDelegateCallbacks`를 사용합니다.

클러스터가 `FanMode`, `PercentSetting`, `SpeedSetting`의 매핑을 계산하는 동안 재진입한 `*Setting` 쓰기는 무시됩니다. 반면 `PercentCurrent`와 `SpeedCurrent`는 실제 팬 동작 상태를 반영하므로 애플리케이션이 계속 갱신할 수 있습니다.

### Codegen 통합

`CodegenIntegration.cpp`는 ZAP/Ember 기반 애플리케이션과 code-driven `FanControlCluster` 사이의 통합 계층을 제공합니다.

주요 함수:

```cpp
FanControlCluster * FindClusterOnEndpoint(EndpointId endpointId);
void SetDefaultDelegate(EndpointId aEndpoint, Delegate * aDelegate);
Delegate * GetDelegate(EndpointId aEndpoint);
```

`FanControlIntegrationDelegateWrapper`는 다음 동작을 제공합니다.

- 애플리케이션 delegate가 있으면 `HandleStep` 및 선택적 알림을 전달합니다.
- 애플리케이션 delegate가 없으면 `HandleStep`에서 `Status::Failure`를 반환합니다.
- `OnFanDriveStateChanged()`에서 기존 `MatterPostAttributeChangeCallback`도 발생시킵니다.
- `SpeedSetting`이 null인 경우 legacy callback을 발생시키지 않습니다.

초기화 및 종료 함수:

```cpp
void MatterFanControlClusterInitCallback(EndpointId endpointId);
void MatterFanControlClusterShutdownCallback(
    EndpointId endpointId,
    MatterClusterShutdownType shutdownType);
```

### Codegen attribute accessors

`chip::app::Clusters::FanControl::Attributes` 네임스페이스는 런타임 `FanControlCluster` 상태에 접근하는 함수를 제공합니다.

지원되는 accessor namespace:

- `FanMode`
- `FanModeSequence`
- `PercentSetting`
- `PercentCurrent`
- `SpeedSetting`
- `SpeedCurrent`
- `SpeedMax`
- `FeatureMap`
- `AirflowDirection`
- `RockSupport`
- `RockSetting`
- `WindSupport`
- `WindSetting`

`FanModeSequence::Set()`, `RockSupport::Set()`, `WindSupport::Set()`은 `Status::UnsupportedWrite`를 반환합니다.

기능이 활성화되지 않은 optional attribute에 접근하면 `Status::UnsupportedAttribute`를 반환합니다. 클러스터가 해당 endpoint에 없으면 `Status::UnsupportedEndpoint`를 반환합니다.

## 예시

### `Delegate` 구현

```cpp
#include <app/clusters/fan-control-server/fan-control-delegate.h>

class MyFanControlDelegate : public chip::app::Clusters::FanControl::Delegate
{
public:
    MyFanControlDelegate(chip::EndpointId endpoint) : Delegate(endpoint) {}

    chip::Protocols::InteractionModel::Status HandleStep(
        chip::app::Clusters::FanControl::StepDirectionEnum aDirection,
        bool aWrap,
        bool aLowestOff) override
    {
        // Handle step command logic here
        return chip::Protocols::InteractionModel::Status::Success;
    }

    void OnFanDriveStateChanged(
        const chip::app::Clusters::FanControl::FanDriveState & newState) override
    {
        // React to fan state changes (mode, speed, etc.)
    }
};
```

### `FanControlCluster` 생성 및 등록

```cpp
#include "app/clusters/fan-control-server/FanControlCluster.h"

MyFanControlDelegate gMyFanDelegate(kYourEndpointId);

chip::app::RegisteredServerCluster<chip::app::Clusters::FanControlCluster> gFanControlCluster(
    chip::app::Clusters::FanControlCluster::Config(kYourEndpointId, gMyFanDelegate)
        .WithFanModeSequence(chip::app::Clusters::FanControl::FanModeSequenceEnum::kOffLowHigh)
        .WithSpeedMax(10)
        .WithStep()
);
```

```cpp
#include "data-model-providers/codegen/CodegenDataModelProvider.h"

void ApplicationInit()
{
    CHIP_ERROR err =
        chip::app::CodegenDataModelProvider::Instance().Registry().Register(
            gFanControlCluster.Registration());
    VerifyOrDie(err == CHIP_NO_ERROR);
}
```

### 기존 Codegen 통합 API 사용

기존 ZAP/Ember 기반 애플리케이션에서는 endpoint별 delegate를 다음과 같이 등록할 수 있습니다.

```cpp
#include <app/clusters/fan-control-server/CodegenIntegration.h>

chip::app::Clusters::FanControl::SetDefaultDelegate(endpoint, &myDelegate);
```

## 관련 문서

- `src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml`
- `data_model/1.7/clusters/FanControl.xml`
- `src/app/clusters/fan-control-server/README.md`
- `src/app/clusters/fan-control-server/FanControlCluster.h`
- `src/app/clusters/fan-control-server/FanControlCluster.cpp`
- `src/app/clusters/fan-control-server/fan-control-delegate.h`
- `src/app/clusters/fan-control-server/CodegenIntegration.h`
- `src/app/clusters/fan-control-server/CodegenIntegration.cpp`
- `src/app/clusters/fan-control-server/fan-control-server.h`