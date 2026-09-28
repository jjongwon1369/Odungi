---
entity: Fan Control
ids: ['0x0202']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml', 'src/app/clusters/fan-control-server/FanControlCluster.cpp', 'src/app/clusters/fan-control-server/CodegenIntegration.h', 'src/app/clusters/fan-control-server/CodegenIntegration.cpp', 'src/app/clusters/fan-control-server/README.md', 'src/app/clusters/fan-control-server/fan-control-delegate.h', 'src/app/clusters/fan-control-server/fan-control-server.h', 'src/app/clusters/fan-control-server/FanControlCluster.h', 'data_model/1.7/clusters/FanControl.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Fan Control

## 개요

Fan Control은 난방·냉방 시스템의 팬을 제어하는 인터페이스다. 팬 모드, 속도, 공기 흐름 방향, 바람 모사 및 회전 동작을 구성한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0202` |
| 스펙 이름 | `Fan Control Cluster` |
| 도메인 | `HVAC` |
| 리비전 | `7` |
| 분류 | `hierarchy="base"`, `role="application"` |
| PICS 코드 | `FAN` |
| 범위 | `Endpoint` |
| 서버 구현 | `chip::app::Clusters::FanControlCluster` |
| 애플리케이션 연동 | `chip::app::Clusters::FanControl::Delegate` |

서버는 코드 기반 C++ 구현이며, `Delegate`를 통해 하드웨어별 명령 처리와 상태 변경 알림을 애플리케이션에 연결한다. 기존 ZAP/Ember 애플리케이션을 위한 통합 계층도 제공한다.

## 스펙

출처: `data_model/1.7/clusters/FanControl.xml`

### 기능

모든 기능은 선택 사항이다. 기능을 지원하면 해당 기능에 종속된 속성 또는 명령은 필수다.

| 비트 | 코드 | 이름 | 지원 내용 |
|---|---|---|---|
| `0` | `SPD` | `MultiSpeed` | `0`부터 `SpeedMax`까지의 팬 속도 |
| `1` | `AUT` | `Auto` | 팬 속도 자동 모드 |
| `2` | `RCK` | `Rocking` | 회전 동작 |
| `3` | `WND` | `Wind` | 바람 모사 |
| `4` | `STEP` | `Step` | `Step` 명령 |
| `5` | `DIR` | `AirflowDirection` | `AirflowDirection` 속성 |

### 데이터 타입

#### `FanModeEnum`

| 값 | 이름 | 적합성 |
|---|---|---|
| `0` | `Off` | 필수 |
| `1` | `Low` | 선택 |
| `2` | `Medium` | `Low`를 조건으로 선택 |
| `3` | `High` | 필수 |
| `4` | `On` | `obsoleteConform` |
| `5` | `Auto` | `AUT` 지원 시 필수 |
| `6` | `Smart` | `obsoleteConform` |

#### `FanModeSequenceEnum`

| 값 | 이름 | 적합성 조건 |
|---|---|---|
| `0` | `OffLowMedHigh` | `AUT` 미지원, `choice="a"` |
| `1` | `OffLowHigh` | `AUT` 미지원, `choice="a"` |
| `2` | `OffLowMedHighAuto` | `AUT` 지원, `choice="b"` |
| `3` | `OffLowHighAuto` | `AUT` 지원, `choice="b"` |
| `4` | `OffHighAuto` | `AUT` 지원, `choice="b"` |
| `5` | `OffHigh` | `AUT` 미지원, `choice="a"` |

각 항목은 위 조건을 가진 `optionalConform`으로 정의된다.

#### 방향 및 비트맵

| 타입 | 항목 | 값 또는 비트 | 의미 |
|---|---|---|---|
| `AirflowDirectionEnum` | `Forward` | 값 `0` | 정방향 공기 흐름 |
| `AirflowDirectionEnum` | `Reverse` | 값 `1` | 역방향 공기 흐름 |
| `StepDirectionEnum` | `Increase` | 값 `0` | 증가 방향 |
| `StepDirectionEnum` | `Decrease` | 값 `1` | 감소 방향 |
| `RockBitmap` | `RockLeftRight` | 비트 `0` | 좌우 회전 |
| `RockBitmap` | `RockUpDown` | 비트 `1` | 상하 회전 |
| `RockBitmap` | `RockRound` | 비트 `2` | 원형 회전 |
| `WindBitmap` | `SleepWind` | 비트 `0` | 수면 바람 |
| `WindBitmap` | `NaturalWind` | 비트 `1` | 자연 바람 |

위 항목은 모두 각 타입 내에서 필수로 정의된다.

### 속성

모든 속성의 읽기 권한은 `view`이며, 쓰기 가능한 속성의 쓰기 권한은 `operate`다.

| ID | 이름 | 타입 | 접근 | 적합성 | 제약 및 품질 |
|---|---|---|---|---|---|
| `0x0000` | `FanMode` | `FanModeEnum` | 읽기/쓰기 | 필수 | `persistence="nonVolatile"` |
| `0x0001` | `FanModeSequence` | `FanModeSequenceEnum` | 읽기 | 필수 | `persistence="fixed"` |
| `0x0002` | `PercentSetting` | `percent` | 읽기/쓰기 | 필수 | 최대 `100`, `nullable="true"` |
| `0x0003` | `PercentCurrent` | `percent` | 읽기 | 필수 | 최대 `100`, `quieterReporting="true"` |
| `0x0004` | `SpeedMax` | `uint8` | 읽기 | `SPD` | `1`–`100`, `persistence="fixed"` |
| `0x0005` | `SpeedSetting` | `uint8` | 읽기/쓰기 | `SPD` | 최대 `SpeedMax`, `nullable="true"` |
| `0x0006` | `SpeedCurrent` | `uint8` | 읽기 | `SPD` | 최대 `SpeedMax`, `quieterReporting="true"` |
| `0x0007` | `RockSupport` | `RockBitmap` | 읽기 | `RCK` | 최소 `1`, `persistence="fixed"` |
| `0x0008` | `RockSetting` | `RockBitmap` | 읽기/쓰기 | `RCK` | 제약의 상세 내용은 XML에 비어 있음 |
| `0x0009` | `WindSupport` | `WindBitmap` | 읽기 | `WND` | 최소 `1`, `persistence="fixed"` |
| `0x000A` | `WindSetting` | `WindBitmap` | 읽기/쓰기 | `WND` | 제약의 상세 내용은 XML에 비어 있음 |
| `0x000B` | `AirflowDirection` | `AirflowDirectionEnum` | 읽기/쓰기 | `DIR` | — |

`FanMode`의 제약도 XML에서는 빈 `desc`로 표현되어 있다. 구체적인 서버 검증 동작은 구현 섹션에 구분하여 기술한다.

### `Step` 명령

| 항목 | 값 |
|---|---|
| ID | `0x00` |
| 방향 | `commandToServer` |
| 응답 표기 | `response="Y"` |
| 실행 권한 | `operate` |
| 적합성 | `STEP` 지원 시 필수 |

| 필드 ID | 이름 | 타입 | 필수 여부 |
|---|---|---|---|
| `0` | `Direction` | `StepDirectionEnum` | 필수 |
| `1` | `Wrap` | `bool` | 선택 |
| `2` | `LowestOff` | `bool` | 선택 |

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 필수 전역 `ClusterRevision` 속성 추가 |
| `2` | 데이터 모델 형식과 표기 변경, 백분율·속도·동작 설정 추가 및 정리 |
| `3` | `AirflowDirection` 및 `Step` 추가 |
| `4` | `FanModeSequenceEnum` 적합성 변경 |
| `5` | 속성 사용 설명 명확화 및 적합성 열 추가 |
| `6` | Zigbee 관련 요소 및 `P` 품질 제거 |
| `7` | `PercentCurrent`, `SpeedCurrent`에 `Q` 품질 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml`

### 생성 및 클러스터 메타데이터

- Alchemy 생성 파일이며 직접 편집하지 않도록 명시되어 있다.
- 생성 원본: `src/app_clusters/FanControl.adoc`
- 생성 정보: `Git: 0.9-1.7-winter2027`, `Alchemy: v1.7.10`
- 클러스터 이름: `Fan Control`
- 클러스터 코드: `0x0202`
- 매크로: `FAN_CONTROL_CLUSTER`
- client와 server 모두 활성화되어 있으며, 각각 `tick="false"`, `init="false"`다.
- 전역 속성 `0xFFFD`의 값은 `7`이며 `side="either"`로 정의된다.
- 기능 비트와 코드는 스펙의 `SPD`, `AUT`, `RCK`, `WND`, `STEP`, `DIR` 정의와 같다.

### 타입 표현

SDK의 열거형은 `enum8`, 비트맵은 `bitmap8`로 정의된다.

| 타입 | SDK 항목과 값 |
|---|---|
| `FanModeEnum` | `Off=0x00`, `Low=0x01`, `Medium=0x02`, `High=0x03`, `On=0x04`, `Auto=0x05`, `Smart=0x06` |
| `FanModeSequenceEnum` | `OffLowMedHigh=0x00`, `OffLowHigh=0x01`, `OffLowMedHighAuto=0x02`, `OffLowHighAuto=0x03`, `OffHighAuto=0x04`, `OffHigh=0x05` |
| `StepDirectionEnum` | `Increase=0x00`, `Decrease=0x01` |
| `AirflowDirectionEnum` | `Forward=0x00`, `Reverse=0x01` |
| `RockBitmap` | `RockLeftRight=0x01`, `RockUpDown=0x02`, `RockRound=0x04` |
| `WindBitmap` | `SleepWind=0x01`, `NaturalWind=0x02` |

### 속성 매핑

속성은 모두 `side="server"`로 정의된다.

| 속성 | `define` | SDK 타입 | SDK 수치 제약 |
|---|---|---|---|
| `FanMode` | `FAN_MODE` | `FanModeEnum` | 최대 `6` |
| `FanModeSequence` | `FAN_MODE_SEQUENCE` | `FanModeSequenceEnum` | 최대 `5` |
| `PercentSetting` | `PERCENT_SETTING` | `percent` | 최대 `100` |
| `PercentCurrent` | `PERCENT_CURRENT` | `percent` | 최대 `100` |
| `SpeedMax` | `SPEED_MAX` | `int8u` | 최소 `1`, 최대 `100` |
| `SpeedSetting` | `SPEED_SETTING` | `int8u` | 최대 `100` |
| `SpeedCurrent` | `SPEED_CURRENT` | `int8u` | 최대 `100` |
| `RockSupport` | `ROCK_SUPPORT` | `RockBitmap` | 최소 `1` |
| `RockSetting` | `ROCK_SETTING` | `RockBitmap` | 최대 `0x07` |
| `WindSupport` | `WIND_SUPPORT` | `WindBitmap` | 최소 `1` |
| `WindSetting` | `WIND_SETTING` | `WindBitmap` | 최대 `0x03` |
| `AirflowDirection` | `AIRFLOW_DIRECTION` | `AirflowDirectionEnum` | 최대 `0x01` |

- `PercentSetting`, `SpeedSetting`은 `isNullable="true"`다.
- 기능 종속 속성은 `optional="true"`와 해당 기능의 `mandatoryConform`을 함께 가진다.
- SDK XML의 `SpeedSetting`, `SpeedCurrent` 상한은 `100`이지만, 스펙 XML의 상한은 `SpeedMax`다.
- 스펙에서 `obsoleteConform`인 `On`, `Smart`도 SDK 열거형에는 포함되어 있다.

### 명령 정의

`Step`은 `source="client"`, `code="0x00"`이며, `STEP` 기능에 종속된다.

`FanMode`, `PercentSetting`, `SpeedSetting`을 직접 지정하는 대신 단계적으로 팬 속도 관련 속성을 변경하는 명령으로 설명된다. SDK에서 `Direction`은 최대 `0x01`인 `StepDirectionEnum`, `Wrap`과 `LowestOff`는 선택적 `boolean`이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/fan-control-server/FanControlCluster.h` | `FanControlCluster`, `Config`, 속성 접근 및 기능 지원 정의 |
| `src/app/clusters/fan-control-server/FanControlCluster.cpp` | 속성 처리, 상태 연동, 명령 전달 및 영속화 |
| `src/app/clusters/fan-control-server/fan-control-delegate.h` | `Delegate`, `FanDriveState` 정의 |
| `src/app/clusters/fan-control-server/CodegenIntegration.h` | 기존 통합 API와 런타임 속성 접근 선언 |
| `src/app/clusters/fan-control-server/CodegenIntegration.cpp` | codegen 등록, delegate 중계, 속성 접근 구현 |
| `src/app/clusters/fan-control-server/fan-control-server.h` | `CodegenIntegration.h`를 포함하는 호환 헤더 |

### 구성과 초기 상태

`FanControlCluster`는 `DefaultServerCluster`를 상속한다. `Config` 생성에는 `EndpointId`와 `FanControl::Delegate &`가 필요하다.

| 구성 함수 | 동작 |
|---|---|
| `WithFanModeSequence` | `FanModeSequence`를 설정하고, 자동 모드가 포함된 시퀀스인지에 따라 `FanControl::Feature::kAuto` 설정 또는 해제 |
| `WithSpeedMax` | 입력을 `1`–`100`으로 제한하고 `MultiSpeed` 및 관련 속성 활성화 |
| `WithRockSupport` | 지원 비트맵 설정, `Rocking` 및 관련 속성 활성화 |
| `WithWindSupport` | 지원 비트맵 설정, `Wind` 및 관련 속성 활성화 |
| `WithAirflowDirection` | `AirflowDirection` 기능과 속성 활성화 |
| `WithStep` | `Step` 기능 활성화 |

주요 초기값은 다음과 같다.

- `mFanModeSequence`: `FanControl::FanModeSequenceEnum::kOffLowHigh`
- `mSpeedMax`: `0`; `WithSpeedMax` 호출 시 `0`은 `1`, `100` 초과는 `100`으로 조정된다.
- `mFanMode`: `FanControl::FanModeEnum::kOff`
- `mPercentSetting`, `mSpeedSetting`: null이 아닌 `0`
- `mPercentCurrent`, `mSpeedCurrent`: `0`
- `mAirflowDirection`: `FanControl::AirflowDirectionEnum::kForward`

`Attributes`는 필수 메타데이터에 지원 기능의 선택 속성을 추가한다. `SupportsAuto`는 시퀀스, `SupportsStep`은 기능 비트, 나머지 지원 판정은 관련 선택 속성 등록 여부를 사용한다.

### 속성 읽기와 쓰기

`ReadAttribute`는 개별 속성 외에 `ClusterRevision`을 `FanControl::kRevision`으로, `FeatureMap`을 `mFeatureMap`으로 인코딩한다.

`WriteAttribute`가 처리하는 속성은 다음과 같다.

- `FanMode`
- `PercentSetting`
- `SpeedSetting`
- `RockSetting`
- `WindSetting`
- `AirflowDirection`

그 외 쓰기는 `Status::UnsupportedAttribute`를 반환한다.

### `FanMode` 검증 및 상태 연동

`SetFanMode`는 알 수 없는 열거형 값에 `Status::ConstraintError`를 반환한다. `IsFanModeSupportedBySequence`는 다음을 검사한다.

- `kLow`: `kOffHigh`, `kOffHighAuto`에서 허용하지 않는다.
- `kMedium`: `kOffLowMedHigh`, `kOffLowMedHighAuto`에서만 허용한다.
- `kAuto`: `SupportsAuto()`가 참일 때만 허용한다.

시퀀스에서 지원하지 않는 모드는 현재 `Status::InvalidInState`를 반환한다. 코드에는 테스트 갱신 후 `Status::ConstraintError`로 변경하려는 TODO가 있다.

입력값은 다음과 같이 정규화된다.

- `FanModeEnum::kOn` → `FanModeEnum::kHigh`
- `FanModeEnum::kSmart` → 자동 모드 지원 시 `FanModeEnum::kAuto`, 그렇지 않으면 `FanModeEnum::kHigh`

모드가 실제로 변경되면 `ApplyFanModeSideEffects`, `StoreFanModePersistence`, `NotifyDelegateFanDriveState`를 실행한다.

| 모드 | `PercentSetting` | `SpeedSetting` | 현재 속도 처리 |
|---|---|---|---|
| `FanModeEnum::kOff` | `0` | `0` | `PercentCurrent`, 지원 시 `SpeedCurrent`를 `0`으로 설정 |
| `FanModeEnum::kLow` | `33` | `1` | 변경하지 않음 |
| `FanModeEnum::kMedium` | `66` | `std::max<uint8_t>(1, (mSpeedMax + 1) / 2)` | 변경하지 않음 |
| `FanModeEnum::kHigh` | `100` | `mSpeedMax` | 변경하지 않음 |
| `FanModeEnum::kAuto` | null | null | 변경하지 않음 |

`SpeedSetting` 갱신은 `MultiSpeed` 지원 시에만 수행한다. 모드가 이미 같은 경우 `SetFanMode`는 부수 효과를 다시 적용하지 않고 `Status::Success`를 반환한다.

### 백분율과 단계 속도 변환

`SetPercentSetting`:

- null은 `FanModeEnum::kAuto`에서만 허용한다.
- `100` 초과는 `Status::ConstraintError`다.
- 변경된 값이 `0`이면 `CommitFanModeOffState`를 호출한다.
- 변경된 값이 양수이고 `MultiSpeed`를 지원하면 다음 식으로 `SpeedSetting`을 갱신한다.

```cpp
(mSpeedMax * percent + 99) / 100
```

`SetSpeedSetting`:

- null은 `FanModeEnum::kAuto`에서만 허용한다.
- `mSpeedMax` 초과는 `Status::ConstraintError`다.
- `ApplySpeedSettingChanged`는 `MultiSpeed` 미지원 또는 null이면 종료한다.
- 변경된 값이 `0`이면 `CommitFanModeOffState`를 호출한다.
- 양수이며 `mSpeedMax`가 `0`이 아니면 다음 식으로 `PercentSetting`을 갱신한다.

```cpp
(speedSetting * 100) / mSpeedMax
```

두 setter의 null 처리 경로는 자동 모드 여부를 검사한 뒤 반환하며, 값을 별도로 재설정하지 않는다. 자동 모드 진입 시 설정값을 null로 만드는 처리는 `ApplyFanModeSideEffects`가 담당한다.

`ComputeFanModeFromPercent`의 매핑은 다음과 같다.

| 조건 | 결과 |
|---|---|
| 백분율 `0` | `FanModeEnum::kOff` |
| 3단계 시퀀스, `1`–`33` | `FanModeEnum::kLow` |
| 3단계 시퀀스, `34`–`66` | `FanModeEnum::kMedium` |
| 3단계 시퀀스, `67` 이상 | `FanModeEnum::kHigh` |
| `Low`가 있는 2단계 시퀀스, `1`–`50` | `FanModeEnum::kLow` |
| `Low`가 있는 2단계 시퀀스, `51` 이상 | `FanModeEnum::kHigh` |
| `Low`가 없는 시퀀스, 양수 | `FanModeEnum::kHigh` |

`CommitFanModeOffState`는 이미 `kOff`이면 아무 작업도 하지 않는다. 그렇지 않으면 모드와 관련 설정·현재 속도를 정지 상태로 맞추고 모드를 저장한다.

### 실제 속도와 재진입 방지

`PercentCurrent`, `SpeedCurrent`는 애플리케이션이 반영하는 실제 동작 속도이므로 설정값과 다를 수 있다.

- `SetPercentCurrent`는 `SetAttributeValue`의 결과를 반환한다.
- `SetSpeedCurrent`는 `MultiSpeed` 미지원 시 `false`를 반환한다.
- 제공된 두 setter에는 각각 `100`, `SpeedMax` 상한 검사가 없다.
- 두 setter는 delegate 알림 중에도 호출할 수 있다.

`NotifyDelegateFanDriveState`는 `FanDriveState` 스냅샷을 전달하는 동안 `mTemporarilyIgnoreFanDriveDelegateCallbacks`를 설정한다. 이때 재진입한 `SetFanMode`, `SetPercentSetting`, `SetSpeedSetting`은 값을 변경하지 않고 `Status::Success`를 반환한다. 이는 클러스터가 계산한 설정값이 콜백에서 덮어써지는 것을 방지한다.

### 회전·바람·방향 설정

| 함수 | 검증 | 변경 후 알림 |
|---|---|---|
| `SetRockSetting` | 설정 비트가 `mRockSupport`의 부분집합인지 검사 | `OnRockSettingChanged` |
| `SetWindSetting` | 설정 비트가 `mWindSupport`의 부분집합인지 검사 | `OnWindSettingChanged` |
| `SetAirflowDirection` | 알려진 열거형 값인지 검사 | `OnAirflowDirectionChanged` |

검증 실패는 `Status::ConstraintError`다. 값이 바뀌지 않으면 알림 없이 `Status::Success`를 반환한다.

### `Step` 처리

`AcceptedCommands`는 `SupportsStep()`이 참일 때만 `Commands::Step::kMetadataEntry`를 제공한다.

`InvokeCommand` 처리 순서:

1. `Commands::Step::DecodableType`으로 디코딩한다. 실패하면 `Status::InvalidCommand`를 반환한다.
2. `Direction`이 알려진 값인지 검사한다. 실패하면 `Status::ConstraintError`를 반환한다.
3. 생략된 `Wrap`은 `false`, `LowestOff`는 `true`로 처리한다.
4. `mDelegate.HandleStep`을 호출하고 결과를 반환한다.

단계별 속도 변경 로직 자체는 delegate가 담당한다. 다른 명령 ID는 `Status::UnsupportedCommand`다.

### Delegate

`src/app/clusters/fan-control-server/fan-control-delegate.h`의 `FanDriveState`는 다음 필드를 가진다.

| 필드 | 타입 |
|---|---|
| `mode` | `FanModeEnum` |
| `percentSetting` | `DataModel::Nullable<chip::Percent>` |
| `percentCurrent` | `chip::Percent` |
| `speedSetting` | `DataModel::Nullable<uint8_t>` |
| `speedCurrent` | `uint8_t` |

`Delegate`에서 `HandleStep`은 순수 가상 함수다. 다음 알림 함수는 기본 구현이 빈 선택적 콜백이다.

- `OnFanDriveStateChanged`
- `OnRockSettingChanged`
- `OnWindSettingChanged`
- `OnAirflowDirectionChanged`

### 영속화

`Startup`은 `DefaultServerCluster::Startup` 이후 `AttributePersistence::LoadNativeEndianValue`로 `FanMode`를 복원하고 `SetFanMode`를 적용한다. 복원된 모드가 거부되면 `FanModeEnum::kOff`로 대체한다.

`StoreFanModePersistence`는 `mContext`가 존재할 때 `AttributePersistence::StoreNativeEndianValue`로 `FanMode`를 저장한다. 제공된 구현에서 직접 영속화하는 속성은 `FanMode`다.

### codegen 통합

`CodegenIntegration.h`와 `CodegenIntegration.cpp`는 기존 ZAP/Ember 구성과 코드 기반 서버를 연결한다.

| API 또는 콜백 | 역할 |
|---|---|
| `MatterFanControlClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterFanControlClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | 등록된 서버 인스턴스 조회, 없으면 `nullptr` |
| `SetDefaultDelegate` | endpoint별 애플리케이션 delegate 등록 또는 해제 |
| `GetDelegate` | 등록된 delegate 조회, 없거나 유효하지 않으면 `nullptr` |

`IntegrationDelegate::CreateRegistration`은 다음 초기 구성을 사용한다.

- `FanModeSequence`: 저장된 기본값을 우선 사용한다. 대체값은 `Auto` 기능이 있으면 `kOffLowHighAuto`, 없으면 `kOffLowHigh`다. 알 수 없는 값도 대체값으로 바꾼다.
- `SpeedMax`: `MultiSpeed` 지원 시 기본값을 읽으며, 대체값은 `100`이다.
- `RockSupport`, `WindSupport`: 해당 기능 지원 시 기본값 읽기가 성공하고 하나 이상의 비트가 설정되어 있어야 한다. 그렇지 않으면 `VerifyOrDie`가 실패한다.
- `AirflowDirection`, `Step`: 기능 비트에 따라 활성화한다.

#### `FanControlIntegrationDelegateWrapper`

클러스터에는 항상 내부 wrapper가 연결되며, wrapper는 선택적인 애플리케이션 delegate 포인터를 유지한다.

- delegate가 없으면 `HandleStep`은 `Status::Failure`를 반환한다.
- 선택적 알림은 delegate가 있을 때 전달한다.
- `OnFanDriveStateChanged`는 delegate 호출 후 `MatterPostAttributeChangeCallback`도 발생시킨다.
- 기존 콜백에는 `FanMode`, `PercentSetting`, null이 아닌 `SpeedSetting`을 전달한다.
- null인 `PercentSetting`은 `0xFF`로 전달한다.
- null인 `SpeedSetting`은 기존 `SpeedSettingWriteCallback`이 자동 모드 상태를 손상시키는 것을 방지하기 위해 전달하지 않는다.

#### 런타임 속성 접근

`CodegenIntegration.h`의 `Attributes` 접근 함수는 ZAP/Ember 저장소가 아니라 `FanControlCluster`의 현재 상태를 읽고 쓴다. 시작 기본값은 `app-common/zap-generated/attributes/Accessors.h`의 `GetDefault` 계열을 사용한다.

- 인스턴스 조회가 필요한 접근에서 서버가 없으면 `Status::UnsupportedEndpoint`를 반환한다.
- 기능 종속 속성 접근은 기능이 없으면 `Status::UnsupportedAttribute`를 반환한다.
- `FanModeSequence`, `RockSupport`, `WindSupport`의 `Set`은 항상 `Status::UnsupportedWrite`다.
- `PercentCurrent`, `SpeedCurrent`의 `Set`은 내부 setter의 `bool` 결과를 `Status::Success` 또는 `Status::Failure`로 변환한다.
- `SpeedSetting`의 `Set`은 `uint8_t`와 `const DataModel::Nullable<uint8_t> &` 오버로드를 제공한다.
- `PercentSetting`의 통합 `Set`은 `chip::Percent`를 받는다.

## 관련 문서

### `src/app/clusters/fan-control-server/README.md`

코드 기반 서버의 사용 및 기존 API에서의 이전 방법을 설명한다.

권장 통합 순서:

1. `chip::app::Clusters::FanControl::Delegate`를 상속하고 `HandleStep`과 필요한 알림 함수를 구현한다.
2. endpoint별 delegate와 `FanControlCluster::Config`를 생성한다.
3. `WithFanModeSequence`, `WithSpeedMax`, `WithStep` 등으로 기능을 구성한다.
4. `chip::app::RegisteredServerCluster<chip::app::Clusters::FanControlCluster>` 인스턴스를 생성한다.
5. `CodegenDataModelProvider::Instance().Registry().Register`로 등록한다.

README의 구성 코드는 `MyFanControlDelegate`, `kYourEndpointId`, `gFanControlCluster`를 사용하며, `FanModeSequenceEnum::kOffLowHigh`, `WithSpeedMax(10)`, `WithStep()`을 지정한다.

이전 지침:

- 새 코드는 `FanControlCluster.h`를 직접 포함한다.
- `fan-control-server.h`는 얇은 호환 헤더로만 유지된다.
- 통합 계층에 의존하지 않게 되면 `SetDefaultDelegate`를 제거하고 `Config`에 `Delegate`를 직접 연결한다.
- 기존 방식의 `SetDefaultDelegate(endpoint, &myDelegate)` 사용은 비권장으로 설명된다.

### 구현 주석의 참조

- `TestFanControl.yaml`: `SpeedSetting`의 null 처리 주석에서 참조한다.
- https://github.com/project-chip/matter-test-scripts/issues/780: 지원하지 않는 `FanMode`와 `FanModeSequence` 조합의 반환 상태 변경 TODO에서 참조한다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
