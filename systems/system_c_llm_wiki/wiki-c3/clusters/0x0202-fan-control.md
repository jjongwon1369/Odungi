---
entity: Fan Control
ids: ['0x0202']
source_paths: ['data_model/1.7/clusters/FanControl.xml', 'src/app/clusters/fan-control-server/CodegenIntegration.cpp', 'src/app/clusters/fan-control-server/CodegenIntegration.h', 'src/app/clusters/fan-control-server/FanControlCluster.cpp', 'src/app/clusters/fan-control-server/FanControlCluster.h', 'src/app/clusters/fan-control-server/README.md', 'src/app/clusters/fan-control-server/fan-control-delegate.h', 'src/app/clusters/fan-control-server/fan-control-server.h', 'src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Fan Control

## 개요

Fan Control은 팬의 동작 모드, 속도, 기류 방향, 바람 모드 및 회전 동작을 제어하는 Matter 클러스터다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | Fan Control |
| 클러스터 ID | `0x0202` |
| revision | `7` |
| 분류 | hierarchy=`base`, role=`application` |
| 범위 | `Endpoint` |
| PICS 코드 | `FAN` |
| SDK 도메인 | `HVAC` |

서버 구현은 `FanControlCluster`를 중심으로 구성된다. 애플리케이션별 하드웨어 동작은 `chip::app::Clusters::FanControl::Delegate`로 분리하며, 기존 ZAP/Ember 기반 애플리케이션에는 `CodegenIntegration.h` / `CodegenIntegration.cpp`를 통한 호환 계층을 제공한다.

## 스펙

출처: `data_model/1.7/clusters/FanControl.xml`

### 기능

모든 기능은 선택 사항이며, 활성화한 기능에 해당하는 속성 또는 명령은 아래 조건에 따라 필수다.

| bit | 코드 | 이름 | 설명 |
|---|---|---|---|
| `0` | `SPD` | `MultiSpeed` | `0`부터 `SpeedMax`까지의 팬 속도 지원 |
| `1` | `AUT` | `Auto` | 팬 속도의 자동 모드 지원 |
| `2` | `RCK` | `Rocking` | 회전 동작 지원 |
| `3` | `WND` | `Wind` | 바람 모사 지원 |
| `4` | `STEP` | `Step` | `Step` 명령 지원 |
| `5` | `DIR` | `AirflowDirection` | `AirflowDirection` 속성 지원 |

### 데이터 타입

#### FanModeEnum

| 값 | 이름 | 의미 | 적합성 |
|---|---|---|---|
| `0` | `Off` | 팬 정지 | 필수 |
| `1` | `Low` | 저속 | 선택 |
| `2` | `Medium` | 중속 | `Low` 조건의 선택 항목 |
| `3` | `High` | 고속 | 필수 |
| `4` | `On` | — | `obsoleteConform` |
| `5` | `Auto` | 자동 모드 | `AUT` 지원 시 필수 |
| `6` | `Smart` | 스마트 모드 | `obsoleteConform` |

#### FanModeSequenceEnum

| 값 | 이름 | 지원 모드 | 적합성 |
|---|---|---|---|
| `0` | `OffLowMedHigh` | `Off`, `Low`, `Medium`, `High` | `AUT` 미지원 조건, 선택 그룹 `a` |
| `1` | `OffLowHigh` | `Off`, `Low`, `High` | `AUT` 미지원 조건, 선택 그룹 `a` |
| `2` | `OffLowMedHighAuto` | `Off`, `Low`, `Medium`, `High`, `Auto` | `AUT` 지원 조건, 선택 그룹 `b` |
| `3` | `OffLowHighAuto` | `Off`, `Low`, `High`, `Auto` | `AUT` 지원 조건, 선택 그룹 `b` |
| `4` | `OffHighAuto` | `Off`, `High`, `Auto` | `AUT` 지원 조건, 선택 그룹 `b` |
| `5` | `OffHigh` | `Off`, `High` | `AUT` 미지원 조건, 선택 그룹 `a` |

#### 방향 열거형

각 항목은 해당 열거형에서 필수다.

| 타입 | 값 | 이름 | 의미 |
|---|---|---|---|
| `AirflowDirectionEnum` | `0` | `Forward` | 정방향 기류 |
| `AirflowDirectionEnum` | `1` | `Reverse` | 역방향 기류 |
| `StepDirectionEnum` | `0` | `Increase` | 증가 방향 |
| `StepDirectionEnum` | `1` | `Decrease` | 감소 방향 |

#### 비트맵

각 비트 필드는 해당 비트맵에서 필수다.

| 타입 | bit | 이름 | 의미 |
|---|---|---|---|
| `RockBitmap` | `0` | `RockLeftRight` | 좌우 회전 |
| `RockBitmap` | `1` | `RockUpDown` | 상하 회전 |
| `RockBitmap` | `2` | `RockRound` | 원형 회전 |
| `WindBitmap` | `0` | `SleepWind` | 수면 바람 |
| `WindBitmap` | `1` | `NaturalWind` | 자연 바람 |

### 속성

모든 속성의 읽기 권한은 `view`다. 쓰기 가능한 속성의 쓰기 권한은 `operate`다.

| ID | 이름 | 타입 | 접근 | 필수 조건 | 제약 및 품질 |
|---|---|---|---|---|---|
| `0x0000` | `FanMode` | `FanModeEnum` | 읽기/쓰기 | 항상 | `persistence="nonVolatile"` |
| `0x0001` | `FanModeSequence` | `FanModeSequenceEnum` | 읽기 | 항상 | `persistence="fixed"` |
| `0x0002` | `PercentSetting` | `percent` | 읽기/쓰기 | 항상 | 최대 `100`, `nullable="true"` |
| `0x0003` | `PercentCurrent` | `percent` | 읽기 | 항상 | 최대 `100`, `quieterReporting="true"` |
| `0x0004` | `SpeedMax` | `uint8` | 읽기 | `SPD` | `1`~`100`, `persistence="fixed"` |
| `0x0005` | `SpeedSetting` | `uint8` | 읽기/쓰기 | `SPD` | 최대 `SpeedMax`, `nullable="true"` |
| `0x0006` | `SpeedCurrent` | `uint8` | 읽기 | `SPD` | 최대 `SpeedMax`, `quieterReporting="true"` |
| `0x0007` | `RockSupport` | `RockBitmap` | 읽기 | `RCK` | 최소 `1`, `persistence="fixed"` |
| `0x0008` | `RockSetting` | `RockBitmap` | 읽기/쓰기 | `RCK` | 제약에 빈 `<desc/>`가 제공됨 |
| `0x0009` | `WindSupport` | `WindBitmap` | 읽기 | `WND` | 최소 `1`, `persistence="fixed"` |
| `0x000A` | `WindSetting` | `WindBitmap` | 읽기/쓰기 | `WND` | 제약에 빈 `<desc/>`가 제공됨 |
| `0x000B` | `AirflowDirection` | `AirflowDirectionEnum` | 읽기/쓰기 | `DIR` | — |

`FanMode`의 제약에도 빈 `<desc/>`가 제공되어 있으며, 이 XML에는 해당 제약의 상세 설명이 없다.

### Step 명령

| 항목 | 값 |
|---|---|
| ID | `0x00` |
| 이름 | `Step` |
| 방향 | `commandToServer` |
| response | `Y` |
| 호출 권한 | `operate` |
| 필수 조건 | `STEP` 지원 |

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `Direction` | `StepDirectionEnum` | 필수 |
| `1` | `Wrap` | `bool` | 선택 |
| `2` | `LowestOff` | `bool` | 선택 |

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | 데이터 모델 형식 및 표기 변경, 백분율·속도·움직임 설정 추가, 전반적 정리 |
| `3` | `AirflowDirection` 및 `Step` 추가 |
| `4` | `FanModeSequenceEnum` 적합성 변경 |
| `5` | 속성 사용 명확화 및 적합성 열 추가 |
| `6` | Zigbee 관련 요소 및 `P` 품질 제거 |
| `7` | `PercentCurrent`, `SpeedCurrent`에 `Q` 품질 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml`

### 클러스터 메타데이터

- 이름: `Fan Control`
- 도메인: `HVAC`
- 코드: `0x0202`
- define: `FAN_CONTROL_CLUSTER`
- 클라이언트와 서버 모두 지원하며, 양쪽 모두 `tick="false"`, `init="false"`다.
- 전역 속성 `0xFFFD`는 `side="either"`, 값 `7`로 정의된다.
- XML 주석은 Alchemy 생성 파일이며 직접 편집하지 말 것을 명시한다.
  - Source: `src/app_clusters/FanControl.adoc`
  - Git: `0.9-1.7-winter2027`
  - Alchemy: `v1.7.10`

### 타입 및 비트마스크

`FanModeEnum`, `FanModeSequenceEnum`, `StepDirectionEnum`, `AirflowDirectionEnum`은 `enum8`로 정의된다. 스펙의 열거형 이름과 값에 대응하며, `On`과 `Smart`도 SDK 정의에 포함된다.

`RockBitmap`, `WindBitmap`은 `bitmap8`로 정의된다.

| 타입 | 필드 | mask |
|---|---|---|
| `RockBitmap` | `RockLeftRight` | `0x01` |
| `RockBitmap` | `RockUpDown` | `0x02` |
| `RockBitmap` | `RockRound` | `0x04` |
| `WindBitmap` | `SleepWind` | `0x01` |
| `WindBitmap` | `NaturalWind` | `0x02` |

### 속성 정의

모든 속성은 `side="server"`다.

| 이름 | define | SDK 정의의 주요 제약 |
|---|---|---|
| `FanMode` | `FAN_MODE` | 최대 `6`, 쓰기 가능 |
| `FanModeSequence` | `FAN_MODE_SEQUENCE` | 최대 `5` |
| `PercentSetting` | `PERCENT_SETTING` | 최대 `100`, 쓰기 가능, nullable |
| `PercentCurrent` | `PERCENT_CURRENT` | 최대 `100` |
| `SpeedMax` | `SPEED_MAX` | `int8u`, 최소 `1`, 최대 `100`, 선택 속성 |
| `SpeedSetting` | `SPEED_SETTING` | `int8u`, 최대 `100`, 쓰기 가능, nullable, 선택 속성 |
| `SpeedCurrent` | `SPEED_CURRENT` | `int8u`, 최대 `100`, 선택 속성 |
| `RockSupport` | `ROCK_SUPPORT` | 최소 `1`, 선택 속성 |
| `RockSetting` | `ROCK_SETTING` | 최대 `0x07`, 쓰기 가능, 선택 속성 |
| `WindSupport` | `WIND_SUPPORT` | 최소 `1`, 선택 속성 |
| `WindSetting` | `WIND_SETTING` | 최대 `0x03`, 쓰기 가능, 선택 속성 |
| `AirflowDirection` | `AIRFLOW_DIRECTION` | 최대 `0x01`, 쓰기 가능, 선택 속성 |

선택 속성에는 스펙과 동일한 기능별 `mandatoryConform` 조건이 붙는다.

스펙 XML에서 `SpeedSetting`과 `SpeedCurrent`의 상한은 `SpeedMax`를 참조하지만, SDK XML의 정적 상한은 `100`이다.

### 명령 정의

`Step`은 `source="client"`, `code="0x00"`, `optional="true"`로 정의되며, `STEP` 지원 시 필수다.

- `Direction`: `StepDirectionEnum`, 최대 `0x01`
- `Wrap`: `boolean`, 선택
- `LowestOff`: `boolean`, 선택

SDK 설명에 따르면 `Step`은 `FanMode`, `PercentSetting`, `SpeedSetting`을 직접 사용하는 대신 단계적으로 속도 관련 속성을 간접 변경하는 명령이다.

## 구현

### 파일 구성

| 경로 | 역할 |
|---|---|
| `src/app/clusters/fan-control-server/FanControlCluster.h` | `FanControlCluster`, `Config`, 속성 접근 및 기능 판별 선언 |
| `src/app/clusters/fan-control-server/FanControlCluster.cpp` | 속성 처리, 상태 연동, 명령 처리, 영속화 |
| `src/app/clusters/fan-control-server/fan-control-delegate.h` | `Delegate`, `FanDriveState` 정의 |
| `src/app/clusters/fan-control-server/CodegenIntegration.h` | 기존 애플리케이션용 등록 및 속성 접근 API |
| `src/app/clusters/fan-control-server/CodegenIntegration.cpp` | codegen 등록, delegate 중계, 기존 콜백 호환 |
| `src/app/clusters/fan-control-server/fan-control-server.h` | `CodegenIntegration.h`를 포함하는 호환 헤더 |

### FanControlCluster 구성

`chip::app::Clusters::FanControlCluster`는 `DefaultServerCluster`를 상속한다.

`Config` 생성에는 `EndpointId`와 `FanControl::Delegate &`가 필요하다. delegate는 필수 참조이므로 `nullptr`를 직접 전달하는 구성이 아니다.

| 구성 함수 | 동작 |
|---|---|
| `WithFanModeSequence` | 모드 시퀀스를 설정하고 자동 모드 포함 여부에 따라 `Feature::kAuto` 설정 또는 해제 |
| `WithSpeedMax` | 값을 `1`~`100`으로 제한하고 `Feature::kMultiSpeed` 및 관련 속성 활성화 |
| `WithRockSupport` | 지원 비트맵을 저장하고 `Feature::kRocking` 및 관련 속성 활성화 |
| `WithWindSupport` | 지원 비트맵을 저장하고 `Feature::kWind` 및 관련 속성 활성화 |
| `WithAirflowDirection` | `Feature::kAirflowDirection` 및 해당 속성 활성화 |
| `WithStep` | `Feature::kStep` 활성화 |

기본 구성의 `mFanModeSequence`는 `FanModeSequenceEnum::kOffLowHigh`, `mSpeedMax`는 `0`이다. `WithSpeedMax`는 입력 `0`을 `1`로, `100` 초과 입력을 `100`으로 조정한다.

초기 런타임 상태는 다음과 같다.

- `mFanMode`: `FanModeEnum::kOff`
- `mPercentSetting`, `mSpeedSetting`: null이 아닌 `0`
- `mPercentCurrent`, `mSpeedCurrent`: `0`
- `mAirflowDirection`: `AirflowDirectionEnum::kForward`

### 속성 및 명령 노출

- `ReadAttribute`는 클러스터 속성과 `ClusterRevision`, `FeatureMap`을 인코딩한다.
- `ClusterRevision`은 `FanControl::kRevision`을 사용한다.
- `WriteAttribute`는 `FanMode`, `PercentSetting`, `SpeedSetting`, `RockSetting`, `WindSetting`, `AirflowDirection`을 각 setter로 전달한다.
- 처리하지 않는 속성 ID에는 `Status::UnsupportedAttribute`를 반환한다.
- `Attributes`는 필수 메타데이터에 활성화된 기능의 속성 메타데이터를 추가한다.
- `AcceptedCommands`는 `SupportsStep()`이 참일 때만 `Commands::Step::kMetadataEntry`를 제공한다.

### FanMode 변경과 연동 상태

`SetFanMode`는 알려지지 않은 열거형 값을 `Status::ConstraintError`로 거부한다.

`IsFanModeSupportedBySequence`는 다음을 검사한다.

- `kLow`: `kOffHigh`, `kOffHighAuto`에서 거부
- `kMedium`: `kOffLowMedHigh`, `kOffLowMedHighAuto`에서만 허용
- `kAuto`: `SupportsAuto()`가 참일 때만 허용

지원하지 않는 모드에는 현재 `Status::InvalidInState`를 반환한다. 코드에는 테스트 갱신 후 `Status::ConstraintError`로 변경하려는 TODO가 있다.

호환 모드 변환은 다음과 같다.

- `FanModeEnum::kOn` → `FanModeEnum::kHigh`
- `FanModeEnum::kSmart` → 자동 모드 지원 시 `FanModeEnum::kAuto`, 아니면 `FanModeEnum::kHigh`

실제 모드가 변경되면 `ApplyFanModeSideEffects`, `StoreFanModePersistence`, `NotifyDelegateFanDriveState`를 수행한다. 같은 모드의 재설정은 추가 처리 없이 성공한다.

| 모드 | `PercentSetting` | `SpeedSetting` | 현재 속도 처리 |
|---|---|---|---|
| `kOff` | `0` | `0` | `PercentCurrent` 및 지원 시 `SpeedCurrent`를 `0`으로 설정 |
| `kLow` | `33` | `1` | 유지 |
| `kMedium` | `66` | `std::max<uint8_t>(1, (mSpeedMax + 1) / 2)` | 유지 |
| `kHigh` | `100` | `mSpeedMax` | 유지 |
| `kAuto` | null | null | 유지 |

`SpeedSetting`과 `SpeedCurrent`의 모드 연동은 `SupportsMultiSpeed()`가 참일 때 적용된다.

### PercentSetting과 SpeedSetting의 연동

`SetPercentSetting`과 `SetSpeedSetting`은 다음을 검사한다.

| 조건 | 결과 |
|---|---|
| null 입력이며 현재 모드가 `kAuto`가 아님 | `Status::InvalidInState` |
| null 입력이며 현재 모드가 `kAuto` | 추가 변경 없이 `Status::Success` |
| `PercentSetting`이 `100` 초과 | `Status::ConstraintError` |
| `SpeedSetting`이 `mSpeedMax` 초과 | `Status::ConstraintError` |
| 기존 값과 동일 | 추가 처리 없이 `Status::Success` |

값이 변경되면 관련 상태를 연동한 뒤 delegate에 알린다.

- `PercentSetting`이 양수이고 `MultiSpeed`를 지원하면:
  - `SpeedSetting`을 `(mSpeedMax * percent + 99) / 100`으로 계산한다.
  - `FanMode`보다 먼저 `SpeedSetting`을 갱신한다.
- `SpeedSetting`이 양수이면:
  - `PercentSetting`을 `(speedSetting * 100) / mSpeedMax`로 계산한다.
  - `mSpeedMax`가 `0`이면 백분율 계산을 수행하지 않는다.
- 설정값이 `0`이면 `CommitFanModeOffState`를 호출한다.
  - 이미 `kOff`이면 이 함수는 아무 작업도 하지 않는다.
  - 그렇지 않으면 모드와 관련 설정값·현재값을 정지 상태로 맞추고 모드를 저장한다.

`ComputeFanModeFromPercent`의 모드 매핑은 다음과 같다.

| 시퀀스 구성 | 백분율 매핑 |
|---|---|
| 모든 구성 | `0` → `kOff` |
| `kOffLowMedHigh`, `kOffLowMedHighAuto` | `1`~`33` → `kLow`, `34`~`66` → `kMedium`, 나머지 양수 → `kHigh` |
| 저속을 포함하는 나머지 구성 | `1`~`50` → `kLow`, 나머지 양수 → `kHigh` |
| `kOffHigh`, `kOffHighAuto` | 양수 → `kHigh` |

### 실제 동작 속도와 재진입 방지

`PercentCurrent`와 `SpeedCurrent`는 애플리케이션이 반영하는 실제 동작 속도이며, 설정값과 다를 수 있다.

- `SetPercentCurrent`는 `SetAttributeValue`의 결과를 반환한다.
- `SetSpeedCurrent`는 `MultiSpeed` 미지원 시 `false`, 지원 시 `SetAttributeValue`의 결과를 반환한다.
- 제공된 두 setter에는 각각 `100` 또는 `mSpeedMax`와 비교하는 범위 검사 코드가 없다.

`NotifyDelegateFanDriveState`는 다음 상태를 `FanDriveState`로 전달한다.

| 필드 | 타입 |
|---|---|
| `mode` | `FanModeEnum` |
| `percentSetting` | `DataModel::Nullable<chip::Percent>` |
| `percentCurrent` | `chip::Percent` |
| `speedSetting` | `DataModel::Nullable<uint8_t>` |
| `speedCurrent` | `uint8_t` |

알림 중에는 `mTemporarilyIgnoreFanDriveDelegateCallbacks`를 설정한다.

- 중첩 `OnFanDriveStateChanged` 알림을 방지한다.
- 재진입한 `SetFanMode`, `SetPercentSetting`, `SetSpeedSetting`은 변경 없이 `Status::Success`를 반환한다.
- `SetPercentCurrent`, `SetSpeedCurrent`는 억제하지 않으므로 delegate 콜백 안에서도 실제 속도를 갱신할 수 있다.

### 기타 설정 검증

| 함수 | 검증 및 알림 |
|---|---|
| `SetRockSetting` | 입력 비트가 모두 `mRockSupport`에 포함되어야 함. 변경 시 `OnRockSettingChanged` 호출 |
| `SetWindSetting` | 입력 비트가 모두 `mWindSupport`에 포함되어야 함. 변경 시 `OnWindSettingChanged` 호출 |
| `SetAirflowDirection` | 알려진 열거형 값이어야 함. 변경 시 `OnAirflowDirectionChanged` 호출 |

검증 실패 시 `Status::ConstraintError`를 반환한다. 값이 동일하면 알림 없이 `Status::Success`를 반환한다.

### Step 처리와 Delegate

`Delegate`는 다음 인터페이스를 제공한다.

| 함수 | 요구 사항 |
|---|---|
| `HandleStep` | 순수 가상 함수. 애플리케이션이 구현해야 함 |
| `OnFanDriveStateChanged` | 선택 콜백, 기본 구현은 아무 작업도 하지 않음 |
| `OnRockSettingChanged` | 선택 콜백, 기본 구현은 아무 작업도 하지 않음 |
| `OnWindSettingChanged` | 선택 콜백, 기본 구현은 아무 작업도 하지 않음 |
| `OnAirflowDirectionChanged` | 선택 콜백, 기본 구현은 아무 작업도 하지 않음 |

`InvokeCommand`의 `Step` 처리 순서는 다음과 같다.

1. `Commands::Step::DecodableType`으로 디코딩한다.
2. 디코딩 실패 시 `Status::InvalidCommand`를 반환한다.
3. 알려지지 않은 `Direction` 값에는 `Status::ConstraintError`를 반환한다.
4. 생략된 `Wrap`은 `false`, `LowestOff`는 `true`로 처리한다.
5. `mDelegate.HandleStep`의 반환값을 그대로 반환한다.

그 밖의 명령 ID에는 `Status::UnsupportedCommand`를 반환한다. 단계별 실제 속도 변경 로직은 delegate에 위임된다.

### FanMode 영속화

`Startup`은 `DefaultServerCluster::Startup` 이후 `AttributePersistence`로 `FanMode`를 복원한다.

- `LoadNativeEndianValue`로 저장값을 읽는다.
- 복원한 값을 `SetFanMode`로 적용한다.
- 거부되면 `FanModeEnum::kOff`로 대체한다.

`StoreFanModePersistence`는 `mContext`가 있을 때 `StoreNativeEndianValue`로 현재 모드를 저장한다. 저장 실패는 `LogErrorOnFailure`로 기록한다.

### codegen 통합 및 생명주기

`CodegenIntegration.cpp`는 endpoint 슬롯마다 다음을 보관한다.

- 애플리케이션 delegate 포인터 `userDelegate`
- `FanControlIntegrationDelegateWrapper`
- `LazyRegisteredServerCluster<FanControlCluster>`

슬롯 수는 다음 값으로 구성된다.

- `kFanControlFixedClusterCount`: `FanControl::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kFanControlMaxClusterCount`: 고정 슬롯 수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합

`static_assert`는 고정 슬롯 수와 `MATTER_DM_FAN_CONTROL_CLUSTER_SERVER_ENDPOINT_COUNT`의 일치 및 최대 슬롯 수의 한계를 검사한다.

| 함수 | 역할 |
|---|---|
| `MatterFanControlClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterFanControlClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | 등록된 `FanControlCluster` 조회. 없으면 `nullptr` |
| `SetDefaultDelegate` | endpoint의 delegate 등록 또는 `nullptr`로 연결 해제 |
| `GetDelegate` | 등록된 delegate 반환. 없거나 유효하지 않으면 `nullptr` |

등록 시 `fetchFeatureMap`은 `true`, `fetchOptionalAttributes`는 `false`다.

`IntegrationDelegate::CreateRegistration`은 다음 초기 구성을 수행한다.

- `FanModeSequence::GetDefaultOr`로 초기 시퀀스를 읽는다.
  - `Feature::kAuto`가 있으면 기본값은 `kOffLowHighAuto`
  - 없으면 `kOffLowHigh`
  - 알려지지 않은 열거형 값도 이 기본값으로 대체
- `Feature::kMultiSpeed`가 있으면 `SpeedMax::GetDefaultOr`를 사용하며 기본값은 `100`
- `Feature::kRocking`, `Feature::kWind`가 있으면 각각 `RockSupport::GetDefault`, `WindSupport::GetDefault`의 성공과 비트 존재를 `VerifyOrDie`로 검사
- 나머지 기능에 따라 `WithAirflowDirection`, `WithStep` 호출

### 기존 delegate 및 콜백 호환

`FanControlIntegrationDelegateWrapper`는 필수 delegate 참조와 지연 등록되는 애플리케이션 delegate 사이를 중계한다.

- 애플리케이션 delegate가 있으면 `HandleStep`과 선택 콜백을 전달한다.
- 없으면 `HandleStep`은 `Status::Failure`를 반환한다.
- `SetDefaultDelegate`는 클러스터 생성 전후 모두 사용할 수 있으며, 생성 후에도 wrapper의 대상을 갱신한다.

`OnFanDriveStateChanged`는 애플리케이션 콜백 전달 후 `EmitLegacyPostAttributeCallbacks`를 호출한다.

| 속성 | `MatterPostAttributeChangeCallback` 전달 방식 |
|---|---|
| `FanMode` | `ZCL_ENUM8_ATTRIBUTE_TYPE`, 1바이트 |
| `PercentSetting` | `ZCL_INT8U_ATTRIBUTE_TYPE`, 1바이트, null은 `0xFF` |
| `SpeedSetting` | null이 아닐 때만 `ZCL_INT8U_ATTRIBUTE_TYPE`, 1바이트 |

코드 주석에 따르면 null `SpeedSetting` 알림은 기존 `SpeedSettingWriteCallback`이 `FanMode::Set(kOff)`를 호출하여 `kAuto` 상태를 손상할 수 있으므로 생략한다.

### 호환 속성 접근 API

`CodegenIntegration.h`의 `Attributes` 접근자는 `FanControlCluster`의 런타임 상태를 읽고 쓴다. ZAP/Ember 저장소의 시작값에는 `app-common/zap-generated/attributes/Accessors.h`의 생성된 `GetDefault` 함수를 사용한다.

- 클러스터를 조회하는 접근자는 클러스터가 없으면 `Status::UnsupportedEndpoint`를 반환한다.
- 기능별 속성 접근자는 해당 기능이 없으면 `Status::UnsupportedAttribute`를 반환한다.
- `FanModeSequence`, `RockSupport`, `WindSupport`의 `Set`은 항상 `Status::UnsupportedWrite`를 반환한다.
- `SpeedMax`, `FeatureMap`은 `Get`만 제공한다.
- `PercentSetting`의 `Get`은 nullable 값을 받지만, 통합 계층의 `Set`은 `chip::Percent` 입력만 제공한다.
- `SpeedSetting`의 `Set`은 `uint8_t`와 `DataModel::Nullable<uint8_t>` 입력을 모두 제공한다.
- `PercentCurrent`, `SpeedCurrent`의 `Set`은 내부 setter의 `bool` 결과를 `Status::Success` 또는 `Status::Failure`로 변환한다.

스펙상 읽기 전용인 현재 속도 속성에 C++ setter가 존재하는 것은 애플리케이션이 실제 동작 속도를 갱신하기 위한 경로다. `WriteAttribute`에는 이 두 속성의 쓰기 처리가 없다.

## 관련 문서

### src/app/clusters/fan-control-server/README.md

코드 기반 서버 통합 및 기존 API 마이그레이션 절차를 설명한다.

권장 통합 순서는 다음과 같다.

1. `chip::app::Clusters::FanControl::Delegate`를 상속하여 `HandleStep`과 필요한 콜백을 구현한다.
2. endpoint마다 delegate와 `FanControlCluster`를 생성한다.
3. `FanControlCluster::Config`로 기능을 구성하고 delegate를 연결한다.
4. `CodegenDataModelProvider`의 registry에 클러스터를 등록한다.

문서에 포함된 구성 코드는 `MyFanControlDelegate`, `gMyFanDelegate`, `gFanControlCluster`를 사용하며, `WithFanModeSequence`, `WithSpeedMax(10)`, `WithStep()`으로 기능을 지정한다.

마이그레이션 지침은 다음과 같다.

- 새 코드는 `FanControlCluster.h`를 직접 사용한다.
- `fan-control-server.h`는 얇은 호환 include로만 유지된다.
- 통합 계층에 대한 의존성이 없어지면 `SetDefaultDelegate`를 제거한다.
- 기존 ZAP/Ember 방식의 `SetDefaultDelegate(endpoint, &myDelegate)` 사용은 비권장 경로로 설명된다.

### 구현 주석의 참조

- `TestFanControl.yaml`: `SpeedSetting`의 null 입력을 `Auto` 모드에서만 허용하는 규칙과 관련하여 언급된다.
- https://github.com/project-chip/matter-test-scripts/issues/780 : 지원하지 않는 `FanMode`에 대한 반환 상태 변경 TODO와 연결된다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
