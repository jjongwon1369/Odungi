---
entity: Fan Control
ids: ['0x0202']
source_paths: ['data_model/1.7/clusters/FanControl.xml', 'src/app/clusters/fan-control-server/CodegenIntegration.cpp', 'src/app/clusters/fan-control-server/CodegenIntegration.h', 'src/app/clusters/fan-control-server/FanControlCluster.cpp', 'src/app/clusters/fan-control-server/FanControlCluster.h', 'src/app/clusters/fan-control-server/README.md', 'src/app/clusters/fan-control-server/fan-control-delegate.h', 'src/app/clusters/fan-control-server/fan-control-server.h', 'src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Fan Control

## 개요

Fan Control은 팬의 모드, 속도, 풍향, 바람 모드 및 회전 동작을 제어하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Fan Control` |
| 스펙 이름 | `Fan Control Cluster` |
| 클러스터 ID | `0x0202` |
| revision | `7` |
| 분류 | hierarchy=`base`, role=`application` |
| 범위 | `Endpoint` |
| PICS 코드 | `FAN` |
| SDK 도메인 | `HVAC` |

구현은 `FanControlCluster`를 중심으로 하는 코드 기반 C++ 서버이다. `chip::app::Clusters::FanControl::Delegate`를 통해 애플리케이션에 상태 변경을 알리고 `Step` 처리를 위임한다. 기존 ZAP/Ember 기반 애플리케이션에는 `CodegenIntegration.h`와 `CodegenIntegration.cpp`가 호환 계층을 제공한다.

## 스펙

출처: `data_model/1.7/clusters/FanControl.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | 데이터 모델 형식 및 표기 변경, 백분율·속도·동작 설정 추가, 전반적인 정리 |
| `3` | `AirflowDirection` 및 `Step` 추가 |
| `4` | `FanModeSequenceEnum` 적합성 조건 변경 |
| `5` | 속성 사용 명확화 및 적합성 열 추가 |
| `6` | Zigbee 관련 요소 및 P quality 제거 |
| `7` | `PercentCurrent`, `SpeedCurrent`에 Q quality 추가 |

### 기능

모든 기능은 선택 사항이다. 각 기능에 연결된 속성 또는 명령은 해당 기능을 지원하면 필수이다.

| bit | code | name | 기능 |
|---|---|---|---|
| `0` | `SPD` | `MultiSpeed` | `0`부터 `SpeedMax`까지의 팬 속도 |
| `1` | `AUT` | `Auto` | 팬 속도 자동 모드 |
| `2` | `RCK` | `Rocking` | 회전 동작 |
| `3` | `WND` | `Wind` | 바람 에뮬레이션 |
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
| `0` | `OffLowMedHigh` | `AUT` 미지원, `optionalConform choice="a"` |
| `1` | `OffLowHigh` | `AUT` 미지원, `optionalConform choice="a"` |
| `2` | `OffLowMedHighAuto` | `AUT` 지원, `optionalConform choice="b"` |
| `3` | `OffLowHighAuto` | `AUT` 지원, `optionalConform choice="b"` |
| `4` | `OffHighAuto` | `AUT` 지원, `optionalConform choice="b"` |
| `5` | `OffHigh` | `AUT` 미지원, `optionalConform choice="a"` |

#### 방향 enum

각 항목은 필수이다.

| 타입 | 값 | 이름 | 의미 |
|---|---|---|---|
| `AirflowDirectionEnum` | `0` | `Forward` | 정방향 공기 흐름 |
| `AirflowDirectionEnum` | `1` | `Reverse` | 역방향 공기 흐름 |
| `StepDirectionEnum` | `0` | `Increase` | 증가 방향 |
| `StepDirectionEnum` | `1` | `Decrease` | 감소 방향 |

#### bitmap

각 bitfield는 필수이다.

| 타입 | bit | 이름 | 의미 |
|---|---|---|---|
| `RockBitmap` | `0` | `RockLeftRight` | 좌우 회전 |
| `RockBitmap` | `1` | `RockUpDown` | 상하 회전 |
| `RockBitmap` | `2` | `RockRound` | 원형 회전 |
| `WindBitmap` | `0` | `SleepWind` | 수면 바람 |
| `WindBitmap` | `1` | `NaturalWind` | 자연 바람 |

### 속성

모든 속성의 읽기 권한은 `view`이며, 쓰기 가능한 속성의 쓰기 권한은 `operate`이다.

| ID | 이름 | 타입 | 접근 | 필수 조건 | 제약 및 quality |
|---|---|---|---|---|---|
| `0x0000` | `FanMode` | `FanModeEnum` | 읽기/쓰기 | 항상 | `persistence="nonVolatile"` |
| `0x0001` | `FanModeSequence` | `FanModeSequenceEnum` | 읽기 | 항상 | `persistence="fixed"` |
| `0x0002` | `PercentSetting` | `percent` | 읽기/쓰기 | 항상 | 최대 `100`, `nullable="true"` |
| `0x0003` | `PercentCurrent` | `percent` | 읽기 | 항상 | 최대 `100`, `quieterReporting="true"` |
| `0x0004` | `SpeedMax` | `uint8` | 읽기 | `SPD` | `1`~`100`, `persistence="fixed"` |
| `0x0005` | `SpeedSetting` | `uint8` | 읽기/쓰기 | `SPD` | 최대 `SpeedMax`, `nullable="true"` |
| `0x0006` | `SpeedCurrent` | `uint8` | 읽기 | `SPD` | 최대 `SpeedMax`, `quieterReporting="true"` |
| `0x0007` | `RockSupport` | `RockBitmap` | 읽기 | `RCK` | 최소 `1`, `persistence="fixed"` |
| `0x0008` | `RockSetting` | `RockBitmap` | 읽기/쓰기 | `RCK` | 제약에 빈 `<desc/>`만 제공됨 |
| `0x0009` | `WindSupport` | `WindBitmap` | 읽기 | `WND` | 최소 `1`, `persistence="fixed"` |
| `0x000A` | `WindSetting` | `WindBitmap` | 읽기/쓰기 | `WND` | 제약에 빈 `<desc/>`만 제공됨 |
| `0x000B` | `AirflowDirection` | `AirflowDirectionEnum` | 읽기/쓰기 | `DIR` | 별도 제약 없음 |

`FanMode`의 제약에도 빈 `<desc/>`만 포함되어 있으며, 제공된 XML에는 그 상세 설명이 없다.

### `Step` 명령

| 항목 | 값 |
|---|---|
| ID | `0x00` |
| 이름 | `Step` |
| direction | `commandToServer` |
| response | `Y` |
| 호출 권한 | `operate` |
| 적합성 | `STEP` 지원 시 필수 |

| field ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `Direction` | `StepDirectionEnum` | 필수 |
| `1` | `Wrap` | `bool` | 선택 |
| `2` | `LowestOff` | `bool` | 선택 |

제공된 스펙 XML에는 이벤트 정의가 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| name | `Fan Control` |
| domain | `HVAC` |
| code | `0x0202` |
| define | `FAN_CONTROL_CLUSTER` |
| client | `true`, `tick="false"`, `init="false"` |
| server | `true`, `tick="false"`, `init="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="7"` |

파일은 Alchemy가 생성했으며 직접 수정하지 않도록 표시되어 있다.

- Source: `src/app_clusters/FanControl.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

### 타입 표현

| 타입 | SDK 타입 | 항목과 값 |
|---|---|---|
| `FanModeEnum` | `enum8` | `Off=0x00`, `Low=0x01`, `Medium=0x02`, `High=0x03`, `On=0x04`, `Auto=0x05`, `Smart=0x06` |
| `FanModeSequenceEnum` | `enum8` | `OffLowMedHigh=0x00`, `OffLowHigh=0x01`, `OffLowMedHighAuto=0x02`, `OffLowHighAuto=0x03`, `OffHighAuto=0x04`, `OffHigh=0x05` |
| `StepDirectionEnum` | `enum8` | `Increase=0x00`, `Decrease=0x01` |
| `AirflowDirectionEnum` | `enum8` | `Forward=0x00`, `Reverse=0x01` |
| `RockBitmap` | `bitmap8` | `RockLeftRight=0x01`, `RockUpDown=0x02`, `RockRound=0x04` |
| `WindBitmap` | `bitmap8` | `SleepWind=0x01`, `NaturalWind=0x02` |

스펙에서 `obsoleteConform`으로 표시된 `On`, `Smart`도 SDK enum에는 포함된다.

### 속성 매핑

모든 속성은 `side="server"`로 정의된다.

| 속성 | define | SDK 표현 및 제약 |
|---|---|---|
| `FanMode` | `FAN_MODE` | `FanModeEnum`, 최대 `6`, 쓰기 가능 |
| `FanModeSequence` | `FAN_MODE_SEQUENCE` | `FanModeSequenceEnum`, 최대 `5` |
| `PercentSetting` | `PERCENT_SETTING` | `percent`, 최대 `100`, 쓰기 가능, nullable |
| `PercentCurrent` | `PERCENT_CURRENT` | `percent`, 최대 `100` |
| `SpeedMax` | `SPEED_MAX` | `int8u`, 최소 `1`, 최대 `100` |
| `SpeedSetting` | `SPEED_SETTING` | `int8u`, 최대 `100`, 쓰기 가능, nullable |
| `SpeedCurrent` | `SPEED_CURRENT` | `int8u`, 최대 `100` |
| `RockSupport` | `ROCK_SUPPORT` | `RockBitmap`, 최소 `1` |
| `RockSetting` | `ROCK_SETTING` | `RockBitmap`, 최대 `0x07`, 쓰기 가능 |
| `WindSupport` | `WIND_SUPPORT` | `WindBitmap`, 최소 `1` |
| `WindSetting` | `WIND_SETTING` | `WindBitmap`, 최대 `0x03`, 쓰기 가능 |
| `AirflowDirection` | `AIRFLOW_DIRECTION` | `AirflowDirectionEnum`, 최대 `0x01`, 쓰기 가능 |

`SpeedMax`부터 `AirflowDirection`까지는 `optional="true"`이며, 각각 스펙과 동일한 기능별 `mandatoryConform` 조건을 갖는다.

스펙은 `SpeedSetting`, `SpeedCurrent`의 최대값을 `SpeedMax`로 지정하지만, SDK XML의 정적 최대값은 `100`이다.

### 명령 표현

`Step`은 `source="client"`, `code="0x00"`, `optional="true"`로 정의되며, `STEP` 지원 시 필수이다.

- `Direction`: `StepDirectionEnum`, 최대 `0x01`.
- `Wrap`: 선택적 `boolean`.
- `LowestOff`: 선택적 `boolean`.

SDK 설명에 따르면 `Step`은 `FanMode`, `PercentSetting`, `SpeedSetting`을 직접 지정하는 대신 속도 관련 속성을 단계적으로 간접 변경한다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/fan-control-server/FanControlCluster.h` | `FanControlCluster`, `Config`, 속성 접근자 및 내부 상태 선언 |
| `src/app/clusters/fan-control-server/FanControlCluster.cpp` | 속성 처리, 상태 연동, 명령 위임, 영속화 |
| `src/app/clusters/fan-control-server/fan-control-delegate.h` | `Delegate`, `FanDriveState` 정의 |
| `src/app/clusters/fan-control-server/CodegenIntegration.h` | codegen 통합 API와 런타임 속성 접근자 선언 |
| `src/app/clusters/fan-control-server/CodegenIntegration.cpp` | 클러스터 등록, delegate 래핑, 기존 접근자 연결 |
| `src/app/clusters/fan-control-server/fan-control-server.h` | `app/clusters/fan-control-server/CodegenIntegration.h`를 포함하는 호환 헤더 |

### `FanControlCluster` 구성

`chip::app::Clusters::FanControlCluster`는 `DefaultServerCluster`를 상속한다. `Config` 생성자에는 `EndpointId`와 필수 `FanControl::Delegate &`가 필요하다.

| 구성 함수 | 동작 |
|---|---|
| `WithFanModeSequence` | 모드 시퀀스를 설정하고 자동 모드 포함 여부에 따라 `FanControl::Feature::kAuto`를 설정하거나 해제 |
| `WithSpeedMax` | 입력을 `1`~`100`으로 제한하고 `FanControl::Feature::kMultiSpeed` 및 관련 속성 활성화 |
| `WithRockSupport` | 지원 bitmap을 저장하고 `FanControl::Feature::kRocking` 및 관련 속성 활성화 |
| `WithWindSupport` | 지원 bitmap을 저장하고 `FanControl::Feature::kWind` 및 관련 속성 활성화 |
| `WithAirflowDirection` | `FanControl::Feature::kAirflowDirection` 및 관련 속성 활성화 |
| `WithStep` | `FanControl::Feature::kStep` 활성화 |

주요 초기값은 다음과 같다.

- `mFanModeSequence`: `FanControl::FanModeSequenceEnum::kOffLowHigh`
- `mSpeedMax`: `0`
- `mFanMode`: `FanControl::FanModeEnum::kOff`
- `mPercentSetting`, `mSpeedSetting`: null이 아닌 `0`
- `mPercentCurrent`, `mSpeedCurrent`: `0`
- `mAirflowDirection`: `FanControl::AirflowDirectionEnum::kForward`

`SupportsMultiSpeed`, `SupportsRocking`, `SupportsWind`, `SupportsAirflowDirection`은 `mOptionalAttributes`를 확인한다. `SupportsAuto`는 모드 시퀀스를, `SupportsStep`은 기능 맵을 확인한다.

### 속성 및 명령 노출

- `ReadAttribute`는 클러스터 속성, `ClusterRevision`, `FeatureMap`을 인코딩한다. `ClusterRevision`에는 `FanControl::kRevision`을 사용한다.
- `WriteAttribute`는 `FanMode`, `PercentSetting`, `SpeedSetting`, `RockSetting`, `WindSetting`, `AirflowDirection`을 디코딩하여 해당 setter로 전달한다.
- 두 함수에서 처리하지 않는 속성은 `Status::UnsupportedAttribute`를 반환한다.
- `Attributes`는 `AttributeListBuilder`를 사용하여 필수 속성과 지원 기능에 따른 속성을 나열한다.
- `AcceptedCommands`는 `SupportsStep()`이 참일 때만 `Commands::Step::kMetadataEntry`를 노출한다.

### `FanMode`와 설정값 연동

`SetFanMode`는 enum 및 모드 시퀀스 지원 여부를 검사한다.

- 알 수 없는 enum 값: `Status::ConstraintError`
- 시퀀스에서 지원하지 않는 모드: 현재 구현은 `Status::InvalidInState`
- `FanModeEnum::kOn`: `FanModeEnum::kHigh`로 변환
- `FanModeEnum::kSmart`: 자동 모드 지원 시 `FanModeEnum::kAuto`, 그렇지 않으면 `FanModeEnum::kHigh`로 변환

지원하지 않는 모드에 대한 반환값을 `Status::ConstraintError`로 변경하는 TODO가 있으며, 다음 이슈를 참조한다.

<https://github.com/project-chip/matter-test-scripts/issues/780>

실제 모드가 변경되면 `ApplyFanModeSideEffects`, `StoreFanModePersistence`, `NotifyDelegateFanDriveState`를 호출한다. 모드가 같으면 추가 처리 없이 `Status::Success`를 반환한다.

| 모드 | `PercentSetting` | `SpeedSetting` | 현재 속도 처리 |
|---|---|---|---|
| `FanModeEnum::kOff` | `0` | `0` | `PercentCurrent` 및 지원되는 `SpeedCurrent`를 `0`으로 설정 |
| `FanModeEnum::kLow` | `33` | `1` | 변경하지 않음 |
| `FanModeEnum::kMedium` | `66` | `std::max<uint8_t>(1, (mSpeedMax + 1) / 2)` | 변경하지 않음 |
| `FanModeEnum::kHigh` | `100` | `mSpeedMax` | 변경하지 않음 |
| `FanModeEnum::kAuto` | null | null | 변경하지 않음 |

`SpeedSetting`과 `SpeedCurrent`의 모드 연동은 `SupportsMultiSpeed()`가 참일 때 적용된다.

### 백분율 및 속도 설정

#### `SetPercentSetting`

- null은 현재 모드가 `FanModeEnum::kAuto`인 경우에만 허용한다.
- null이 허용되는 경우에도 값을 별도로 변경하지 않고 `Status::Success`를 반환한다.
- `100` 초과는 `Status::ConstraintError`이다.
- 값이 변경되면 `ApplyPercentSettingChanged` 후 delegate에 알린다.

`ApplyPercentSettingChanged`는 다음을 수행한다.

- `0`: `CommitFanModeOffState` 호출.
- 양수이며 `MultiSpeed` 지원: `(mSpeedMax * percent + 99) / 100`으로 `SpeedSetting` 계산.
- 이어서 `ApplyNonZeroFanDrive`로 모드를 결정.

`SpeedSetting`을 먼저 갱신하여 모드 변경에 반응하는 delegate가 일관된 설정값을 읽도록 한다.

#### `SetSpeedSetting`

- null은 현재 모드가 `FanModeEnum::kAuto`일 때만 허용한다.
- null이 허용되는 경우 값을 별도로 변경하지 않고 `Status::Success`를 반환한다.
- `mSpeedMax` 초과는 `Status::ConstraintError`이다.
- 값이 변경되면 `ApplySpeedSettingChanged` 후 delegate에 알린다.

`ApplySpeedSettingChanged`는 `MultiSpeed` 미지원 또는 null이면 처리하지 않는다. 값이 `0`이면 `CommitFanModeOffState`를 호출하고, 양수이면 `(speedSetting * 100) / mSpeedMax`로 `PercentSetting`을 계산한 뒤 모드를 갱신한다. `mSpeedMax == 0`이면 계산하지 않는다.

#### 백분율에서 모드 결정

`ComputeFanModeFromPercent`의 매핑은 다음과 같다.

| 조건 | 모드 결정 |
|---|---|
| 백분율 `0` | `FanModeEnum::kOff` |
| `OffLowMedHigh` 또는 `OffLowMedHighAuto` | `33` 이하: `FanModeEnum::kLow`, `66` 이하: `FanModeEnum::kMedium`, 그 외: `FanModeEnum::kHigh` |
| `Low`를 포함하는 나머지 시퀀스 | `50` 이하: `FanModeEnum::kLow`, 그 외: `FanModeEnum::kHigh` |
| `OffHigh` 또는 `OffHighAuto` | 양수이면 `FanModeEnum::kHigh` |

`CommitFanModeOffState`는 모드가 이미 `FanModeEnum::kOff`이면 아무 작업도 하지 않는다. 그렇지 않으면 모드를 변경하고 관련 설정값과 현재값을 정리한 뒤 영속화한다.

### 현재 속도와 재진입 처리

`PercentCurrent`, `SpeedCurrent`는 실제 동작 속도이며 애플리케이션이 갱신한다. 설정값과 다를 수 있다.

- `SetPercentCurrent`는 `SetAttributeValue`의 결과를 반환한다.
- `SetSpeedCurrent`는 `MultiSpeed` 미지원 시 `false`, 지원 시 `SetAttributeValue`의 결과를 반환한다.
- 제공된 두 setter 본문에는 각각 `100`, `mSpeedMax`에 대한 상한 검사가 없다.

`NotifyDelegateFanDriveState`는 `mTemporarilyIgnoreFanDriveDelegateCallbacks`로 재진입을 방지한다. 알림 처리 중 재진입한 `SetFanMode`, `SetPercentSetting`, `SetSpeedSetting`은 값을 변경하지 않고 `Status::Success`를 반환한다.

`SetPercentCurrent`, `SetSpeedCurrent`에는 이 억제 조건을 적용하지 않으므로 애플리케이션이 변경 콜백 안에서도 실제 속도를 갱신할 수 있다.

### 회전, 바람 및 풍향

| 함수 | 검증 및 알림 |
|---|---|
| `SetRockSetting` | 설정 비트가 `mRockSupport`에 모두 포함되어야 함. 변경 시 `OnRockSettingChanged` 호출 |
| `SetWindSetting` | 설정 비트가 `mWindSupport`에 모두 포함되어야 함. 변경 시 `OnWindSettingChanged` 호출 |
| `SetAirflowDirection` | 알 수 없는 enum 값 거부. 변경 시 `OnAirflowDirectionChanged` 호출 |

검증 실패는 `Status::ConstraintError`이며, 기존 값과 같으면 알림 없이 `Status::Success`를 반환한다.

### `Step` 처리

`InvokeCommand`의 `Step` 처리 순서는 다음과 같다.

1. `Commands::Step::DecodableType`으로 디코딩한다. 실패하면 `Status::InvalidCommand`.
2. `Direction`이 알 수 없는 enum 값이면 `Status::ConstraintError`.
3. 생략된 `Wrap`에는 `false`, `LowestOff`에는 `true`를 적용한다.
4. `mDelegate.HandleStep(commandData.direction, wrapValue, lowestOffValue)`의 결과를 반환한다.

다른 명령은 `Status::UnsupportedCommand`를 반환한다. 실제 단계 변경 로직은 `FanControlCluster`가 아니라 delegate가 담당한다.

### `Delegate`와 `FanDriveState`

`FanDriveState`는 다음 필드를 포함한다.

| 필드 | 타입 |
|---|---|
| `mode` | `FanModeEnum` |
| `percentSetting` | `DataModel::Nullable<chip::Percent>` |
| `percentCurrent` | `chip::Percent` |
| `speedSetting` | `DataModel::Nullable<uint8_t>` |
| `speedCurrent` | `uint8_t` |

`Delegate`의 인터페이스는 다음과 같다.

| 함수 | 요구 사항 |
|---|---|
| `HandleStep` | 순수 가상 함수. 애플리케이션에서 구현 필요 |
| `OnFanDriveStateChanged` | 선택적 상태 변경 콜백 |
| `OnRockSettingChanged` | 선택적 회전 설정 콜백 |
| `OnWindSettingChanged` | 선택적 바람 설정 콜백 |
| `OnAirflowDirectionChanged` | 선택적 풍향 설정 콜백 |

선택적 콜백의 기본 구현은 아무 작업도 하지 않는다.

### 영속화

`Startup`은 `DefaultServerCluster::Startup` 이후 `AttributePersistence`로 `FanMode`를 복원하고 `SetFanMode`로 적용한다. 복원된 모드가 거부되면 `FanModeEnum::kOff`를 적용한다.

`StoreFanModePersistence`는 `mContext`가 있을 때 `StoreNativeEndianValue`로 `FanMode`를 저장하고, 오류는 `LogErrorOnFailure`로 기록한다.

### codegen 통합

#### 등록과 조회

- `MatterFanControlClusterInitCallback`: `CodegenClusterIntegration::RegisterServer` 호출.
- `MatterFanControlClusterShutdownCallback`: `CodegenClusterIntegration::UnregisterServer` 호출.
- `FindClusterOnEndpoint`: 등록된 `FanControlCluster` 조회. 대상 서버가 없거나 미등록이면 `nullptr`.
- `GetDelegate`: 등록된 애플리케이션 delegate 조회.
- `SetDefaultDelegate`: endpoint별 delegate 등록 또는 `nullptr`로 연결 해제.

`SetDefaultDelegate`는 클러스터 생성 전후에 호출할 수 있으며, 이미 생성된 경우에도 wrapper의 대상을 갱신한다.

저장 공간은 `gClusters`가 관리한다.

- `kFanControlFixedClusterCount`: `FanControl::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kFanControlMaxClusterCount`: 고정 개수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값

`static_assert`로 고정 개수가 `MATTER_DM_FAN_CONTROL_CLUSTER_SERVER_ENDPOINT_COUNT`와 일치하고, 최대 개수가 `kEmberInvalidEndpointIndex` 이하인지 확인한다.

#### 구성값 로드

`IntegrationDelegate::CreateRegistration`은 다음 방식으로 `Config`를 구성한다.

- `FanModeSequence`: `GetDefaultOr`로 읽는다. 기본값은 자동 모드 지원 시 `FanModeSequenceEnum::kOffLowHighAuto`, 그 외 `FanModeSequenceEnum::kOffLowHigh`. 알 수 없는 enum이면 기본값으로 대체한다.
- `SpeedMax`: `MultiSpeed` 지원 시 `GetDefaultOr`로 읽으며 기본값은 `100`.
- `RockSupport`, `WindSupport`: 기능 지원 시 `GetDefault`가 성공하고 하나 이상의 비트가 설정되어 있어야 한다. `VerifyOrDie`로 확인하며 대체값은 없다.
- 풍향 및 단계 명령 기능은 각각 `WithAirflowDirection`, `WithStep`으로 활성화한다.

등록 시 `fetchFeatureMap=true`, `fetchOptionalAttributes=false`를 사용한다.

#### `FanControlIntegrationDelegateWrapper`

wrapper는 클러스터에 항상 유효한 delegate 참조를 제공하면서 선택적인 애플리케이션 delegate 포인터를 유지한다.

- 애플리케이션 delegate가 있으면 `HandleStep`과 선택적 알림을 전달한다.
- 없으면 `HandleStep`은 `Status::Failure`, 선택적 애플리케이션 알림은 아무 작업도 하지 않는다.
- `OnFanDriveStateChanged`는 애플리케이션 알림 후 `EmitLegacyPostAttributeCallbacks`도 호출한다.

기존 `MatterPostAttributeChangeCallback`은 다음과 같이 발생한다.

| 속성 | 전달 방식 |
|---|---|
| `FanMode` | `ZCL_ENUM8_ATTRIBUTE_TYPE`, 1바이트 |
| `PercentSetting` | `ZCL_INT8U_ATTRIBUTE_TYPE`, 1바이트, null은 `0xFF` |
| `SpeedSetting` | `ZCL_INT8U_ATTRIBUTE_TYPE`, 1바이트, null이 아닐 때만 전달 |

`SpeedSetting`의 null 콜백은 `SpeedSettingWriteCallback`이 `FanMode::Set(kOff)`를 호출하여 자동 모드 상태를 손상시킬 수 있으므로 생략한다.

#### 런타임 속성 접근자

`CodegenIntegration.h`의 `Attributes` 접근자는 ZAP/Ember 저장소가 아니라 `FanControlCluster`의 런타임 상태를 읽고 쓴다. 시작 설정값은 `app-common/zap-generated/attributes/Accessors.h`의 `GetDefault`를 사용한다.

| 속성 | 제공 접근자 | 특이사항 |
|---|---|---|
| `FanMode` | `Get`, `Set` | 클러스터 getter/setter로 전달 |
| `FanModeSequence` | `Get`, `Set` | `Set`은 항상 `Status::UnsupportedWrite` |
| `PercentSetting` | `Get`, `Set` | `Get`은 nullable, `Set`은 `chip::Percent` |
| `PercentCurrent` | `Get`, `Set` | setter의 bool을 `Status::Success` 또는 `Status::Failure`로 변환 |
| `SpeedSetting` | `Get`, `Set` | `Set`은 `uint8_t` 및 nullable 오버로드 |
| `SpeedCurrent` | `Get`, `Set` | setter의 bool을 `Status::Success` 또는 `Status::Failure`로 변환 |
| `SpeedMax` | `Get` | 읽기만 제공 |
| `FeatureMap` | `Get` | `GetFeatureMap().Raw()` 반환 |
| `AirflowDirection` | `Get`, `Set` | 클러스터 getter/setter로 전달 |
| `RockSupport` | `Get`, `Set` | `Set`은 항상 `Status::UnsupportedWrite` |
| `RockSetting` | `Get`, `Set` | 클러스터 getter/setter로 전달 |
| `WindSupport` | `Get`, `Set` | `Set`은 항상 `Status::UnsupportedWrite` |
| `WindSetting` | `Get`, `Set` | 클러스터 getter/setter로 전달 |

클러스터 조회를 수행하는 접근자는 대상이 없으면 `Status::UnsupportedEndpoint`를 반환한다. 기능별 접근자는 해당 기능이 없으면 `Status::UnsupportedAttribute`를 반환한다. 항상 `Status::UnsupportedWrite`를 반환하는 세 setter는 endpoint 조회를 하지 않는다.

## 관련 문서

### `src/app/clusters/fan-control-server/README.md`

코드 기반 서버의 사용 절차와 기존 API에서의 이전 방법을 설명한다.

권장 통합 순서는 다음과 같다.

1. `chip::app::Clusters::FanControl::Delegate`를 상속하고 `HandleStep` 및 필요한 변경 콜백을 구현한다.
2. endpoint별 delegate와 `FanControlCluster`를 생성한다.
3. `FanControlCluster::Config`에 delegate를 전달하고 지원 기능을 구성한다.
4. `CodegenDataModelProvider`의 registry에 클러스터를 등록한다.

문서의 구성 코드는 `MyFanControlDelegate`, `gMyFanDelegate`, `gFanControlCluster`, `kYourEndpointId`를 사용하며, `WithFanModeSequence`, `WithSpeedMax(10)`, `WithStep()`으로 기능을 지정한다. `ApplicationInit`에서는 `CodegenDataModelProvider::Instance().Registry().Register`와 `VerifyOrDie`로 등록을 수행한다.

이전 지침은 다음과 같다.

- 새 코드는 `FanControlCluster.h`를 직접 포함한다.
- `fan-control-server.h`는 얇은 호환 include로만 남아 있다.
- 직접 생성하는 클러스터에는 `Config`로 `Delegate`를 연결한다.
- 통합 계층에 대한 의존성이 없어지면 `SetDefaultDelegate`를 제거한다.
- 기존 ZAP/Ember 방식의 `SetDefaultDelegate` 사용은 호환 목적으로 유지되지만 권장되지 않는다.

## 관련 페이지

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md)
- [Extractor Hood](../device-types/extractor-hood.md)
- [Humidity Conditioner](../device-types/humidity-conditioner.md)
- [Microwave Oven](../device-types/microwave-oven.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
