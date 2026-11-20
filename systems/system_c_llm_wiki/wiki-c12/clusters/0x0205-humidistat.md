---
entity: Humidistat
ids: ['0x0205']
source_paths: ['data_model/1.7/clusters/Humidistat.xml', 'src/app/clusters/humidistat-server/CodegenIntegration.cpp', 'src/app/clusters/humidistat-server/CodegenIntegration.h', 'src/app/clusters/humidistat-server/HumidistatCluster.cpp', 'src/app/clusters/humidistat-server/HumidistatCluster.h', 'src/app/clusters/humidistat-server/HumidistatTestEventTriggerHandler.h', 'src/app/zap-templates/zcl/data-model/chip/humidistat-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Humidistat

## 개요

`Humidistat`는 환경의 습도를 제어하는 인터페이스를 정의하는 클러스터다. 기능 구성에 따라 가습, 제습, 연속 운전, 센서 기반 설정값 제어, 자동 운전, 팬 단독 운전, 분무 방식 및 응축수 펌프 제어를 지원한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Humidistat Cluster` |
| 식별자 이름 | `Humidistat` |
| 클러스터 ID | `0x0205` |
| 리비전 | `1` |
| 성숙도 | `provisional` |
| PICS 코드 | `HSTAT` |
| 분류 | hierarchy=`base`, role=`application`, scope=`Endpoint` |
| SDK 도메인 | `HVAC` |
| 서버 구현 | `chip::app::Clusters::HumidistatCluster` |

## 스펙

출처: `data_model/1.7/clusters/Humidistat.xml`

리비전 `1`의 변경 요약은 `Initial revision`이다.

### 기능

| bit | code | name | 기능 및 적합성 조건 |
|---|---|---|---|
| `0` | `HUM` | `Humidifier` | 공간의 습도를 높인다. `DEHUM`과 함께 choice=`a`에 속하며 최소 하나 필요 |
| `1` | `DEHUM` | `Dehumidifier` | 공간의 습도를 낮춘다. `HUM`과 함께 choice=`a`에 속하며 최소 하나 필요 |
| `2` | `CONT` | `Continuous` | 연속 습도 운전. 선택 |
| `3` | `SENSOR` | `Sensor` | 습도 센서를 이용한 설정값 제어. 선택 |
| `4` | `AUTO` | `Auto` | 설정 습도를 유지하도록 운전 상태를 자동 전환. `HUM`, `DEHUM`, `SENSOR`가 모두 있을 때 선택 |
| `5` | `FAN` | `FanOnly` | 습도 제어 없이 팬만 운전. 선택 |
| `6` | `OPT` | `Optimal` | 최적 습도 제어. `SENSOR`가 있을 때 선택 |
| `7` | `WARM` | `WarmMist` | 온열 분무. `HUM` 조건의 choice=`b` |
| `8` | `COLD` | `ColdMist` | 냉각 분무. `HUM` 조건의 choice=`b` |
| `9` | `COND` | `CondPump` | 응축수 펌프 제어 및 모니터링. 선택 |

choice=`a`와 choice=`b`는 모두 `min="1"`, `more="true"`다. `HUM`에 대해 `WARM`과 `COLD` 중 최소 하나를 선택하는 조건이 지정되어 있다.

### 데이터 타입

#### `ModeEnum`

| 값 | 이름 | 의미 | 필수 조건 |
|---|---|---|---|
| `0` | `Humidifier` | 습도 증가 | `HUM` |
| `1` | `Dehumidifier` | 습도 감소 | `DEHUM` |
| `2` | `Auto` | 습도 유지 | `AUTO` |
| `3` | `FanOnly` | 습도 제어 없이 팬 운전 | `FAN` |

#### `SystemStateEnum`

| 값 | 이름 | 의미 | 필수 조건 |
|---|---|---|---|
| `0` | `Humidifying` | 습도 증가 중 | `HUM` |
| `1` | `Dehumidifying` | 습도 감소 중 | `DEHUM` |
| `2` | `Fan` | 습도 제어 없이 팬 운전 중 | `FAN` |
| `3` | `Idle` | 습도가 충족되었거나 장치가 꺼진 상태 | 항상 필수 |

#### `MistTypeBitmap`

| bit | 이름 | 의미 | 필수 조건 |
|---|---|---|---|
| `0` | `MistCold` | 냉각 분무 가습 | `COLD` |
| `1` | `MistWarm` | 온열 분무 가습 | `WARM` |

### 속성

모든 속성의 읽기 권한은 `view`다. 쓰기가 가능한 속성의 쓰기 권한은 `operate`다.

| ID | 이름 | 타입 | 접근 | persistence | 적합성 및 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `list`, entry=`ModeEnum` | 읽기 | `fixed` | 필수. 최대 항목 수 `4` |
| `0x0001` | `Mode` | `ModeEnum` | 읽기/쓰기 | `nonVolatile` | 필수 |
| `0x0002` | `SystemState` | `SystemStateEnum` | 읽기 | `nonVolatile` | 필수 |
| `0x0003` | `UserSetpoint` | `percent` | 읽기/쓰기 | `nonVolatile` | `SENSOR`에서 필수. `MinSetpoint` 이상, `MaxSetpoint` 이하 |
| `0x0004` | `MinSetpoint` | `percent` | 읽기 | `fixed` | `SENSOR`에서 필수. `0`–`99` |
| `0x0005` | `MaxSetpoint` | `percent` | 읽기 | `fixed` | `SENSOR`에서 필수. `MinSetpoint + 1` 이상, `100` 이하 |
| `0x0006` | `Step` | `percent` | 읽기 | `fixed` | `SENSOR`에서 필수. `0`–`100` |
| `0x0007` | `TargetSetpoint` | `percent` | 읽기 | 지정 없음 | `OPT`에서 필수, 그 외 `SENSOR`에서 선택. `MinSetpoint` 이상, `MaxSetpoint` 이하. 기본값은 `UserSetpoint` |
| `0x0008` | `MistType` | `MistTypeBitmap` | 읽기/쓰기 | `nonVolatile` | `HUM`에서 필수. `nullable="true"` |
| `0x0009` | `Continuous` | `bool` | 읽기/쓰기 | `nonVolatile` | `CONT`에서 필수 |
| `0x000A` | `Sleep` | `bool` | 읽기/쓰기 | `nonVolatile` | 선택. 기본값 `false` |
| `0x000B` | `Optimal` | `bool` | 읽기/쓰기 | `nonVolatile` | `OPT`에서 필수 |
| `0x000C` | `CondPumpEnabled` | `bool` | 읽기/쓰기 | `nonVolatile` | `COND`에서 필수 |
| `0x000D` | `CondRunCount` | `uint16` | 읽기 | `nonVolatile` | `COND`에서 필수 |

### 명령: `SetSettings`

| 항목 | 정의 |
|---|---|
| ID | `0x00` |
| 방향 | `commandToServer` |
| 응답 표기 | `response="Y"` |
| 호출 권한 | `operate` |
| 적합성 | 필수 |

지정된 설정을 새 값으로 변경한다. 모든 필드는 선택 사항이다.

| field ID | 이름 | 타입 |
|---|---|---|
| `0` | `UserSetpoint` | `percent` |
| `1` | `Mode` | `ModeEnum` |
| `2` | `MistType` | `MistTypeBitmap` |
| `3` | `Continuous` | `bool` |
| `4` | `Sleep` | `bool` |
| `5` | `Optimal` | `bool` |

`UserSetpoint` 필드의 제약에는 빈 `<desc/>`만 있으며, 제공된 스펙 XML에 추가 설명은 없다. 이벤트 정의도 포함되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/humidistat-cluster.xml`

### 생성 정보와 클러스터 메타데이터

- Alchemy가 생성한 XML이며 `DO NOT EDIT`로 표시되어 있다.
- 생성 원본: `src/app_clusters/Humidistat.adoc`
- Git: `0.9-1.7-winter2027-3-gb265a3f82d`
- Alchemy: `v1.7.10`
- 클러스터 define: `HUMIDISTAT_CLUSTER`
- `apiMaturity="provisional"`
- `client`와 `server`가 모두 활성화되어 있으며, 각각 `init="false"`, `tick="false"`다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="1"`로 선언된다.

### 타입 표현

| 정의 | SDK 표현 |
|---|---|
| `MistTypeBitmap` | `bitmap8`; `MistCold`=`0x01`, `MistWarm`=`0x02` |
| `ModeEnum` | `enum8`; `Humidifier`=`0x00`, `Dehumidifier`=`0x01`, `Auto`=`0x02`, `FanOnly`=`0x03` |
| `SystemStateEnum` | `enum8`; `Humidifying`=`0x00`, `Dehumidifying`=`0x01`, `Fan`=`0x02`, `Idle`=`0x03` |
| `SupportedModes` | `array`, entryType=`ModeEnum`, length=`4` |
| 스펙의 `bool` 속성 및 명령 필드 | `boolean` |
| `CondRunCount` | `int16u` |

기능 비트와 적합성 조건은 스펙 XML의 구성을 따른다. `SetSettings`는 `source="client"`이며, 필드 ID와 선택 여부는 스펙 정의와 동일하다.

### 속성 define

아래는 SDK XML에 기록된 값을 그대로 정리한 것이다.

| 속성 | define |
|---|---|
| `SupportedModes` | `MODE` |
| `Mode` | `SYSTEM_STATE` |
| `SystemState` | `USER_SETPOINT` |
| `UserSetpoint` | `MIN_SETPOINT` |
| `MinSetpoint` | `MAX_SETPOINT` |
| `MaxSetpoint` | `STEP` |
| `Step` | `TARGET_SETPOINT` |
| `TargetSetpoint` | `MIST_TYPE` |
| `MistType` | `CONTINUOUS` |
| `Continuous` | `SLEEP` |
| `Sleep` | `OPTIMAL` |
| `Optimal` | `OPTIMAL` |
| `CondPumpEnabled` | `COND_PUMP_ENABLED` |
| `CondRunCount` | `COND_RUN_COUNT` |

### 스펙 XML과의 표현 차이

- `UserSetpoint`와 `TargetSetpoint`에는 `max="100"`이 지정되지만, `MinSetpoint`와 `MaxSetpoint`를 참조하는 범위 제약은 SDK XML에 표현되어 있지 않다.
- `MaxSetpoint`는 `min="1"`, `max="100"`으로 선언된다.
- `MistType`는 `max="0x03"`이며, 스펙 XML의 `nullable="true"`에 해당하는 표시는 없다.
- `Sleep`의 기본값은 `default="0"`이다.
- 스펙 XML의 `persistence` 및 접근 권한 수준은 이 SDK XML에 명시되어 있지 않다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/humidistat-server/CodegenIntegration.cpp` | codegen 기반 인스턴스 생성, 등록, 해제 및 조회 |
| `src/app/clusters/humidistat-server/CodegenIntegration.h` | `FindClusterOnEndpoint` 선언 |
| `src/app/clusters/humidistat-server/HumidistatCluster.cpp` | 속성 상태, 영속성, 검증, 읽기/쓰기 및 명령 처리 |
| `src/app/clusters/humidistat-server/HumidistatCluster.h` | `HumidistatCluster`, `HumidistatDelegate`, 초기 구성 및 공개 API |
| `src/app/clusters/humidistat-server/HumidistatTestEventTriggerHandler.h` | 인증 시험용 트리거 값과 처리 인터페이스 |

### 클래스와 선택 속성

`HumidistatCluster`는 `DefaultServerCluster`를 상속하며 속성 상태, 서버 인터페이스 및 명령 처리를 함께 소유한다.

- `OptionalAttributeSet`: 사용자가 선택하는 `Sleep::Id`, `TargetSetpoint::Id`.
- `FullOptionalAttributeSet`: 기능에 따라 활성화되는 속성까지 포함한다.
- `ComputeActiveOptionalAttributes`: 기능과 선택 속성 구성을 바탕으로 활성 속성 집합을 구성한다.
- `Attributes`: `Humidistat::Attributes::kMandatoryMetadata`와 활성 선택 속성의 메타데이터를 결합한다.
- `AcceptedCommands`: `Humidistat::Commands::SetSettings::kMetadataEntry`를 반환한다.

### codegen 등록과 조회

인스턴스 저장 공간은 `LazyRegisteredServerCluster<HumidistatCluster>` 배열인 `gServers`다.

- `kHumidistatFixedClusterCount`는 `Humidistat::StaticApplicationConfig::kFixedClusterConfig.size()`다.
- `kHumidistatMaxClusterCount`는 고정 인스턴스 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `IntegrationDelegate::CreateRegistration`은 기능 및 선택 속성 구성을 해석하고 `StartupConfiguration`을 채운 뒤 인스턴스를 생성한다.
- `FindRegistration`은 생성되지 않은 슬롯에 대해 `nullptr`를 반환한다.
- `ReleaseRegistration`은 해당 슬롯의 인스턴스를 제거한다.

| 함수 | 동작 |
|---|---|
| `MatterHumidistatClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`과 `fetchOptionalAttributes`를 모두 `true`로 설정 |
| `MatterHumidistatClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `MatterHumidistatPluginServerInitCallback` | 빈 구현 |
| `chip::app::Clusters::Humidistat::FindClusterOnEndpoint` | 등록된 `HumidistatCluster`를 조회하며, 없으면 `nullptr` 반환 |

`CreateRegistration`은 다음 의존성을 `VerifyOrDie`로 검사한다.

- `Feature::kOptimal`에는 `Feature::kSensor`가 필요하다.
- `Feature::kColdMist` 또는 `Feature::kWarmMist`에는 `Feature::kHumidifier`가 필요하다.
- `Feature::kAuto`에는 `Feature::kHumidifier`, `Feature::kDehumidifier`, `Feature::kSensor`가 모두 필요하다.

`Feature::kSensor`가 없으면 선택 속성의 `TargetSetpoint::Id`를 해제한다. 속성 기본값은 기능별 `GetDefault` 호출로 읽으며, `Sleep`은 `GetDefaultOr`로 읽고 대체 기본값 `false`를 사용한다. `Feature::kOptimal`이 활성화된 경우에는 `TargetSetpoint::GetDefault` 성공을 필수로 검사한다.

### 초기 상태와 검증

`StartupConfiguration`의 기본값은 다음과 같다.

| 멤버 | 기본값 |
|---|---|
| `mode` | `Humidistat::ModeEnum::kAuto` |
| `systemState` | `Humidistat::SystemStateEnum::kIdle` |
| `userSetpoint` | `50` |
| `minSetpoint` | `0` |
| `maxSetpoint` | `100` |
| `step` | `1` |
| `targetSetpoint` | `50` |
| `mistType` | `0` |
| `continuous` | `false` |
| `sleep` | `false` |
| `optimal` | `false` |

생성자는 `mCondPumpEnabled`를 `false`, `mCondRunCount`를 `0`으로 초기화한다.

`IsFeatureConfigurationValid`는 다음을 검사한다.

- `Feature::kHumidifier` 또는 `Feature::kDehumidifier`가 최소 하나 있어야 한다.
- `Feature::kAuto`에는 `Feature::kHumidifier`와 `Feature::kDehumidifier`가 필요하다.
- 분무 기능에는 `Feature::kHumidifier`가 필요하다.

생성자는 추가로 다음을 검사한다.

- `minSetpoint <= 99`
- `minSetpoint + 1 <= maxSetpoint <= 100`
- `1 <= step <= maxSetpoint - minSetpoint`
- `maxSetpoint - minSetpoint`가 `step`으로 나누어떨어짐
- 초기 `mistType`이 지원되는 비트만 포함함

지원하지 않는 초기 `mode`는 `DefaultModeForFeatures`로 대체한다. 선택 우선순위는 `ModeEnum::kAuto`, `ModeEnum::kDehumidifier`, `ModeEnum::kFanOnly`, `ModeEnum::kHumidifier`다.

지원하지 않는 초기 `systemState`는 `DefaultSystemStateForMode`로 대체한다.

| 모드 | 대체 상태 |
|---|---|
| `ModeEnum::kHumidifier` | `SystemStateEnum::kHumidifying` |
| `ModeEnum::kDehumidifier` | `SystemStateEnum::kDehumidifying` |
| `ModeEnum::kFanOnly` | `SystemStateEnum::kFan` |
| `ModeEnum::kAuto` | `SystemStateEnum::kIdle` |

### 설정값 처리

`SnapToNearestStep`은 다음 규칙으로 값을 보정한다.

1. 범위 밖 값은 `mMinSetpoint` 또는 `mMaxSetpoint`로 제한한다.
2. 범위 안 값은 `mMinSetpoint`를 기준으로 가장 가까운 `mStep` 간격의 값으로 맞춘다.
3. 두 값과의 거리가 같으면 낮은 값을 선택한다.

초기 `mUserSetpoint`, `mTargetSetpoint` 및 영속 저장소에서 복원한 `mUserSetpoint`에는 이 보정이 적용된다.

| 함수 | 검증 및 동작 |
|---|---|
| `SetUserSetpoint` | `Feature::kSensor`와 범위를 검사. 실패 시 `ConstraintError`. 범위 안 값은 간격에 맞춘 뒤 저장 |
| `SetTargetSetpoint` | `Feature::kSensor`가 없으면 `InvalidInState`, 속성이 활성화되지 않았으면 `UnsupportedAttribute`, 범위 밖이면 `ConstraintError`. 유효한 값은 간격에 맞춤 |
| `ShouldTargetSetpointMatchUserSetpoint` | `Feature::kSensor`가 있고 `mSleep`, `mOptimal`이 모두 `false`일 때 참 |
| `SyncTargetSetpointToUserSetpoint` | 위 조건과 `TargetSetpoint::Id` 활성화를 확인한 뒤 값을 동기화 |

`SetUserSetpoint`, `SetSleep`, `SetOptimal`에서 실제 값이 변경되면 `SyncTargetSetpointToUserSetpoint`를 호출한다. `SetTargetSetpoint` 자체는 `ShouldTargetSetpointMatchUserSetpoint` 조건으로 쓰기를 제한하지 않는다.

### 상태 변경 API

| 함수 | 주요 동작 |
|---|---|
| `SetMode` | 지원 모드 검사. 미지원 값은 `ConstraintError` |
| `SetSystemState` | 지원 상태 검사. 미지원 값은 `ConstraintError` |
| `SetMistType` | `Feature::kHumidifier` 및 비트 지원 여부 검사. 실패 시 `ConstraintError` |
| `SetContinuous` | 기능 및 활성화 허용 여부 검사. 실패 시 `InvalidInState` |
| `SetSleep` | 선택 속성 지원 및 활성화 허용 여부 검사. 실패 시 `InvalidInState` |
| `SetOptimal` | 기능 및 활성화 허용 여부 검사. 실패 시 `InvalidInState` |
| `SetCondPumpEnabled` | `Feature::kCondPump`가 없으면 `InvalidInState` |
| `SetCondRunCount` | `Feature::kCondPump`가 없으면 `InvalidInState` |
| `ResetCondRunCount` | `SetCondRunCount(0)` 호출 |
| `IncrementCondRunCount` | 최대 `uint16_t` 값에서는 증가하지 않고 성공 반환 |

`SetMode`는 `SystemState`를 함께 변경하지 않는다.

`IsMistTypeSupportable`은 `MistTypeBitmap::kMistCold`, `MistTypeBitmap::kMistWarm` 외의 비트를 거부하며, 각 비트에 대응하는 기능도 검사한다.

다음 API는 각각 `true`로 설정하는 동작의 허용 여부를 제어한다. 허용 플래그의 초기값은 모두 `true`다.

- `SetSetSettingsAllowContinuous`
- `SetSetSettingsAllowSleep`
- `SetSetSettingsAllowOptimal`

검사는 개별 setter 내부에 있으므로 `SetSettings`뿐 아니라 속성 쓰기와 직접 setter 호출에도 적용된다. `false`로 변경할 때는 이 허용 플래그를 검사하지 않는다.

읽기 API로 `GetFeatures`, `GetMode`, `GetSystemState`, `GetUserSetpoint`, `GetMinSetpoint`, `GetMaxSetpoint`, `GetStep`, `GetTargetSetpoint`, `GetMistType`, `GetContinuous`, `GetSleep`, `GetOptimal`, `GetCondPumpEnabled`, `GetCondRunCount`를 제공한다.

### 영속성

`Startup`은 `DefaultServerCluster::Startup` 이후 `LoadPersistentAttributes`를 호출한다.

복원 대상은 기능과 선택 속성 구성에 따라 다음과 같다.

- `Mode`, `SystemState`
- `UserSetpoint`
- `MistType`
- `Continuous`
- `Sleep`
- `Optimal`
- `CondPumpEnabled`, `CondRunCount`

복원 후에는 다음 보정이 수행된다.

- 미지원 `Mode`는 기능 기반 기본 모드로 대체한다.
- 미지원 `SystemState`는 현재 모드 기반 기본 상태로 대체한다.
- `UserSetpoint`는 유효 간격에 맞춘다.
- `MistType`의 미정의 비트 및 비활성 기능에 해당하는 비트를 제거한다.
- `ShouldTargetSetpointMatchUserSetpoint`가 참이면 `mTargetSetpoint`를 `mUserSetpoint`로 맞춘다.

값 변경 시 영속 속성은 컨텍스트가 있으면 저장한다. `CondRunCount`는 `attributeStorage.WriteValue`를 사용하고, 나머지 해당 속성은 `AttributePersistence::StoreNativeEndianValue`를 사용한다. 저장 실패는 `LogErrorOnFailure`로 기록하며 setter의 성공 반환을 바꾸지 않는다.

`TargetSetpoint`에는 영속 저장 및 복원 처리가 없다.

### 속성 및 명령 디스패치

- `ReadAttribute`는 클러스터 속성과 `FeatureMap`, `ClusterRevision`을 인코딩한다.
- `SupportedModes`는 활성 기능에 따라 `Humidifier`, `Dehumidifier`, `Auto`, `FanOnly` 순으로 인코딩한다.
- `WriteAttribute`는 `Mode`, `UserSetpoint`, `MistType`, `Continuous`, `CondPumpEnabled`, `Sleep`, `Optimal`을 디코딩하여 해당 setter를 호출한다.
- 처리하지 않는 속성 ID에는 `Status::UnsupportedAttribute`를 반환한다.
- `InvokeCommand`는 `SetSettings`를 `HandleSetSettings`에 전달하며, 그 외 명령에는 `Status::UnsupportedCommand`를 반환한다.

### `SetSettings` 처리 순서

`HandleSetSettings`는 명령 디코딩 후 다음 항목을 먼저 검증한다.

1. 전달된 `mode`의 지원 여부
2. `Feature::kHumidifier`가 있을 때 전달된 `mistType`의 지원 여부
3. `Feature::kSensor`가 있을 때 전달된 `userSetpoint`의 원래 요청 범위

이후 다음 순서로 적용한다.

1. `SetMode`
2. `SetMistType`
3. `SetContinuous`
4. `SetSleep`
5. `SetOptimal`
6. `SetUserSetpoint`

`Mode` 외의 필드는 해당 기능 또는 선택 속성이 지원되는 경우에만 처리한다. 미지원 조건의 필드는 이 처리 경로에서 건너뛴다.

초기 검증은 일부 잘못된 요청의 부분 적용을 방지하지만, 이후 setter가 실패하면 이미 적용한 변경을 되돌리는 처리는 없다.

### 변경 알림

`SetDelegate`로 `HumidistatDelegate`를 등록하며, `nullptr`로 해제할 수 있다.

| 속성 | 콜백 |
|---|---|
| `Mode` | `OnModeChanged` |
| `SystemState` | `OnSystemStateChanged` |
| `UserSetpoint` | `OnUserSetpointChanged` |
| `TargetSetpoint` | `OnTargetSetpointChanged` |
| `MistType` | `OnMistTypeChanged` |
| `Continuous` | `OnContinuousChanged` |
| `Sleep` | `OnSleepChanged` |
| `Optimal` | `OnOptimalChanged` |
| `CondPumpEnabled` | `OnCondPumpEnabledChanged` |
| `CondRunCount` | `OnCondRunCountChanged` |

콜백은 상태 변경이 반영된 이후의 알림이다. 반환값이 없으며 변경을 거부할 수 없다.

### 인증 시험용 트리거

`HumidistatTrigger`는 General Diagnostics의 `TestEventTrigger`를 통해 제조사 enable key와 함께 보내는 인증 시험용 값을 정의한다.

| 이름 | 값 |
|---|---|
| `kDisallowContinuous` | `0x0205000000000000` |
| `kAllowContinuous` | `0x0205000000000001` |
| `kDisallowSleep` | `0x0205000000000002` |
| `kAllowSleep` | `0x0205000000000003` |
| `kDisallowOptimal` | `0x0205000000000004` |
| `kAllowOptimal` | `0x0205000000000005` |

`HumidistatTestEventTriggerHandler::HandleEventTrigger`는 다음 순서로 처리한다.

1. `clearEndpointInEventTrigger`로 endpoint 정보를 제거한다.
2. `HandleHumidistatTestEventTrigger`를 호출한다.
3. 결과가 `true`이면 `CHIP_NO_ERROR`, 아니면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.

`TestEventTrigger`를 활성화하는 애플리케이션은 `HandleHumidistatTestEventTrigger`를 구현해야 한다. 제공된 입력에는 이 함수의 구현이 없다.

### 스펙과 구현의 확인 가능한 차이

- 스펙 XML의 `Step` 범위는 `0`–`100`이지만, 생성자는 `1` 이상이며 설정값 범위를 정확히 나누는 간격을 요구한다.
- 스펙 XML의 `MistType`는 nullable이지만, 제공된 SDK XML에는 nullable 표시가 없고 구현은 `chip::BitMask<Humidistat::MistTypeBitmap>`로 읽기와 쓰기를 처리한다.
- `AUTO`의 `SENSOR` 의존성과 `OPT`의 `SENSOR` 의존성은 `CreateRegistration`에서 검사하지만, `IsFeatureConfigurationValid`에서는 검사하지 않는다.
- 제공된 기능 검증 함수에는 `HUM` 사용 시 `WARM` 또는 `COLD`가 최소 하나 필요하다는 choice=`b` 조건의 검사가 없다.
- `ComputeActiveOptionalAttributes`는 `mOptionalAttributes`를 복사한 뒤 기능 기반 속성을 추가한다. `SENSOR`가 없을 때 요청된 `TargetSetpoint`를 제거하는 처리는 `CreateRegistration`에 있으며, 직접 생성 경로의 이 함수에는 별도 제거 처리가 없다.

## 관련 페이지

**사용 기기**

- [Humidity Conditioner](../device-types/humidity-conditioner.md)
