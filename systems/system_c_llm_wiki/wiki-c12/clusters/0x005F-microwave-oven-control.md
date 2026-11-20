---
entity: Microwave Oven Control
ids: ['0x005F']
source_paths: ['data_model/1.7/clusters/MicrowaveOvenControl.xml', 'src/app/clusters/microwave-oven-control-server/AppDelegate.h', 'src/app/clusters/microwave-oven-control-server/CodegenIntegration.cpp', 'src/app/clusters/microwave-oven-control-server/CodegenIntegration.h', 'src/app/clusters/microwave-oven-control-server/Delegate.h', 'src/app/clusters/microwave-oven-control-server/IntegrationDelegate.h', 'src/app/clusters/microwave-oven-control-server/MicrowaveOvenControlCluster.cpp', 'src/app/clusters/microwave-oven-control-server/MicrowaveOvenControlCluster.h', 'src/app/clusters/microwave-oven-control-server/microwave-oven-control-server.h', 'src/app/zap-templates/zcl/data-model/chip/microwave-oven-control-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Microwave Oven Control

## 개요

`Microwave Oven Control`은 전자레인지의 조리 매개변수를 설정하고 조리 상태 정보를 제공하는 클러스터이다. 조리 시간과 출력 설정을 다루며, `SetCookingParameters`와 선택적 명령인 `AddMoreTime`을 제공한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Microwave Oven Control Cluster` |
| 클러스터 ID | `0x005F` |
| revision | `1` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `MWOCTRL` |
| scope | `Endpoint` |

구현은 애플리케이션 로직을 `AppDelegate`로, `OperationalState` 및 `MicrowaveOvenMode`와의 연동을 `IntegrationDelegate`로 분리한다.

## 스펙

출처: `data_model/1.7/clusters/MicrowaveOvenControl.xml`

### 기능

| bit | code | name | 의미 및 적합성 |
|---|---|---|---|
| `0` | `PWRNUM` | `PowerAsNumber` | 출력을 단위 없는 수 또는 백분율로 지정한다. `optionalConform choice="a"` |
| `1` | `WATTS` | `PowerInWatts` | 출력을 와트 단위로 지정한다. `otherwiseConform`에 `provisionalConform`과 `optionalConform choice="a"`가 포함된다. |
| `2` | `PWRLMTS` | `PowerNumberLimits` | `PWRNUM`에 사용하는 제한 속성을 지원한다. `PWRNUM`을 조건으로 하는 선택 기능이다. |

`PowerAsNumber`와 `PowerInWatts` 중 정확히 하나를 지원해야 하며, `PowerNumberLimits`는 `PowerAsNumber`를 지원할 때만 허용된다. 제공된 `Instance::Init()`도 이 조건을 검사한다.

### 속성

모든 속성의 접근은 읽기이며, `readPrivilege`는 `view`이다.

| ID | 이름 | 타입 | 적합성 | 제약 | persistence / 기본값 |
|---|---|---|---|---|---|
| `0x0000` | `CookTime` | `elapsed-s` | 필수 | `1` 이상, `MaxCookTime` 이하 | — |
| `0x0001` | `MaxCookTime` | `elapsed-s` | 필수 | `1` 이상, `86400` 이하 | `fixed` |
| `0x0002` | `PowerSetting` | `uint8` | `PWRNUM` 지원 시 필수 | `<desc/>`; 구체적인 설명은 입력에 없음 | — |
| `0x0003` | `MinPower` | `uint8` | `PWRLMTS` 지원 시 필수 | `1` 이상, `99` 이하 | `fixed` |
| `0x0004` | `MaxPower` | `uint8` | `PWRLMTS` 지원 시 필수 | `MinPower + 1` 이상, `100` 이하 | `fixed` |
| `0x0005` | `PowerStep` | `uint8` | `PWRLMTS` 지원 시 필수 | `<desc/>`; 구체적인 설명은 입력에 없음 | `fixed` |
| `0x0006` | `SupportedWatts` | `list`, 항목 `uint16` | `provisionalConform`; `WATTS` 조건의 `mandatoryConform` | 항목 수 `1` 이상, `10` 이하 | `fixed` |
| `0x0007` | `SelectedWattIndex` | `uint8` | `provisionalConform`; `WATTS` 조건의 `mandatoryConform` | `<desc/>`; 구체적인 설명은 입력에 없음 | — |
| `0x0008` | `WattRating` | `uint16` | 선택 | 별도 제약 없음 | `fixed`, 기본값 `MS` |

### 명령

두 명령 모두 `direction="commandToServer"`, `response="Y"`, `invokePrivilege="operate"`로 정의된다.

#### SetCookingParameters

- ID: `0x00`
- 적합성: 필수
- 용도: 장치 동작에 사용할 조리 매개변수 설정

| 필드 ID | 이름 | 타입 | 적합성 및 제약 |
|---|---|---|---|
| `0` | `CookMode` | `uint8` | 선택 그룹 `b`; 제약은 `<desc/>` |
| `1` | `CookTime` | `elapsed-s` | 선택 그룹 `b`; `1` 이상, `MaxCookTime` 이하 |
| `2` | `PowerSetting` | `uint8` | `PWRNUM` 조건의 선택 그룹 `b`; 제약은 `<desc/>` |
| `3` | `WattSettingIndex` | `uint8` | `WATTS` 조건의 선택 그룹 `b`; 제약은 `<desc/>` |
| `4` | `StartAfterSetting` | `bool` | 선택 |

선택 그룹 `b`에는 `more="true"`, `min="1"`이 지정되어 있다. 해당 그룹에서 최소 하나의 필드를 제공해야 하며, 여러 필드를 제공할 수 있다.

#### AddMoreTime

- ID: `0x01`
- 적합성: 선택
- 용도: 서버의 `CookTime`에 시간 추가

| 필드 ID | 이름 | 타입 | 적합성 및 제약 |
|---|---|---|---|
| `0` | `TimeToAdd` | `elapsed-s` | 필수; `1` 이상, `MaxCookTime` 이하 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/microwave-oven-control-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| configurator domain | `CHIP` |
| cluster domain | `Appliances` |
| name | `Microwave Oven Control` |
| code | `0x005F` |
| define | `MICROWAVE_OVEN_CONTROL_CLUSTER` |
| client / server | 모두 `true`; `tick="false"`, `init="false"` |
| globalAttribute | `code="0xFFFD"`, `side="either"`, `value="1"` |

파일 주석에는 Alchemy가 생성한 XML이며 직접 수정하지 말라고 명시되어 있다. 생성 원본 경로는 `src/app_clusters/MicrowaveOvenControl.adoc`이다.

### 속성 정의

모든 속성은 `side="server"`로 정의된다.

| code | name | define | SDK 타입 | 기본값 | SDK에 명시된 범위 |
|---|---|---|---|---|---|
| `0x0000` | `CookTime` | `COOK_TIME` | `elapsed_s` | `30` | `1`–`86400` |
| `0x0001` | `MaxCookTime` | `MAX_COOK_TIME` | `elapsed_s` | — | `1`–`86400` |
| `0x0002` | `PowerSetting` | `POWER_SETTING` | `int8u` | — | — |
| `0x0003` | `MinPower` | `MIN_POWER` | `int8u` | `10` | `1`–`99` |
| `0x0004` | `MaxPower` | `MAX_POWER` | `int8u` | `100` | `2`–`100` |
| `0x0005` | `PowerStep` | `POWER_STEP` | `int8u` | `10` | — |
| `0x0006` | `SupportedWatts` | `SUPPORTED_WATTS` | `array`, `entryType="int16u"` | — | `minLength="1"`, `length="10"` |
| `0x0007` | `SelectedWattIndex` | `SELECTED_WATT_INDEX` | `int8u` | — | — |
| `0x0008` | `WattRating` | `WATT_RATING` | `int16u` | — | — |

기능 조건은 스펙의 `PWRNUM`, `PWRLMTS`, `WATTS` 조건을 반영한다. `PowerInWatts`, `SupportedWatts`, `SelectedWattIndex`에는 `apiMaturity="provisional"`이 명시되어 있다.

### 명령 인자 정의

두 명령은 `source="client"`로 정의된다.

| 명령 | 인자 | SDK 타입 | 선택 여부 | 기본값 | 범위 |
|---|---|---|---|---|---|
| `SetCookingParameters` | `CookMode` | `int8u` | 선택 | — | — |
| `SetCookingParameters` | `CookTime` | `elapsed_s` | 선택 | `30` | `1`–`86400` |
| `SetCookingParameters` | `PowerSetting` | `int8u` | 선택 | `100` | `1`–`100` |
| `SetCookingParameters` | `WattSettingIndex` | `int8u` | 선택 | — | — |
| `SetCookingParameters` | `StartAfterSetting` | `boolean` | 선택 | `0` | — |
| `AddMoreTime` | `TimeToAdd` | `elapsed_s` | 필수 | — | `1`–`86400` |

### 스펙과 SDK 표현의 차이

- 스펙의 `elapsed-s`, `uint8`, `uint16`은 SDK XML에서 각각 `elapsed_s`, `int8u`, `int16u`로 표현된다.
- 스펙은 `CookTime`과 `TimeToAdd`의 상한을 `MaxCookTime`으로 지정한다. SDK XML에는 정적 상한 `86400`이 기록되어 있다.
- 스펙은 `MaxPower`의 하한을 `MinPower + 1`로 지정한다. SDK XML에는 정적 하한 `2`가 기록되어 있다.
- 스펙의 `SetCookingParameters` 선택 그룹 `b` 조건은 제공된 SDK XML의 인자 정의에 명시되어 있지 않다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/microwave-oven-control-server/AppDelegate.h` | 애플리케이션별 명령 처리 및 속성 값 제공 인터페이스 |
| `src/app/clusters/microwave-oven-control-server/IntegrationDelegate.h` | 동작 상태와 조리 모드 의존성을 분리하는 인터페이스 |
| `src/app/clusters/microwave-oven-control-server/Delegate.h` | `AppDelegate`를 상속하고 `Instance` 접근 제공 |
| `src/app/clusters/microwave-oven-control-server/CodegenIntegration.h` | `CodegenIntegrationDelegate`, `Instance` 선언 |
| `src/app/clusters/microwave-oven-control-server/CodegenIntegration.cpp` | codegen 연동, 초기화 및 등록 해제 구현 |
| `src/app/clusters/microwave-oven-control-server/MicrowaveOvenControlCluster.h` | `MicrowaveOvenControlCluster`, `Config`, 서버 인터페이스 선언 |
| `src/app/clusters/microwave-oven-control-server/MicrowaveOvenControlCluster.cpp` | 속성 읽기, 명령 처리, 범위 검사, 변경 알림 구현 |
| `src/app/clusters/microwave-oven-control-server/microwave-oven-control-server.h` | `app/clusters/microwave-oven-control-server/CodegenIntegration.h` 포함 |

`MicrowaveOvenControlCluster`는 `chip::app::Clusters`에 정의된다. `AppDelegate`, `IntegrationDelegate`, `Delegate`, `CodegenIntegrationDelegate`, `Instance`는 `chip::app::Clusters::MicrowaveOvenControl`에 정의된다.

### MicrowaveOvenControlCluster 구성

`MicrowaveOvenControlCluster`는 `DefaultServerCluster`를 상속한다.

`Config`의 구성 요소는 다음과 같다.

| 필드 | 역할 |
|---|---|
| `feature` | 지원 기능 비트마스크 |
| `optionalAttributeSet` | 선택적 `WattRating` 노출 설정 |
| `supportsAddMoreTime` | `AddMoreTime` 지원 여부; 기본 초기값은 `false` |
| `integrationDelegate` | `IntegrationDelegate` 참조 |
| `appDelegate` | `AppDelegate` 참조 |

`OptionalAttributeSet`에는 `MicrowaveOvenControl::Attributes::WattRating::Id`만 포함된다. 나머지 조건부 속성은 기능 비트로 제어한다.

### AppDelegate

애플리케이션은 다음 순수 가상 메서드를 구현한다.

| 메서드 | 역할 |
|---|---|
| `HandleSetCookingParametersCallback` | 조리 매개변수 처리 후 `Protocols::InteractionModel::Status` 반환 |
| `HandleModifyCookTimeSecondsCallback` | 시간 추가 후 최종 조리 시간 처리 및 상태 반환 |
| `GetWattSettingByIndex` | 인덱스에 해당하는 와트 값 조회 |
| `GetMaxCookTimeSec` | 최대 조리 시간 제공 |
| `GetPowerSettingNum` | 현재 숫자 출력 설정 제공 |
| `GetMinPowerNum` | 최소 숫자 출력 제공 |
| `GetMaxPowerNum` | 최대 숫자 출력 제공 |
| `GetPowerStepNum` | 숫자 출력 간격 제공 |
| `GetCurrentWattIndex` | 현재 와트 인덱스 제공 |
| `GetWattRating` | `WattRating` 값 제공 |

`HandleSetCookingParametersCallback`의 인자는 다음과 같다.

```cpp
uint8_t cookMode
uint32_t cookTimeSec
bool startAfterSetting
Optional<uint8_t> powerSettingNum
Optional<uint8_t> wattSettingIndex
```

- `cookMode`는 애플리케이션이 Microwave Oven Mode 인스턴스에 정의한 값이어야 한다.
- `startAfterSetting`이 `true`이면 명령 처리 후 조리 동작을 시작한다.
- `powerSettingNum`과 `wattSettingIndex`는 상호 배타적이다.
- 숫자 출력 방식에서는 `wattSettingIndex`가 `NullOptional`이다.
- 와트 출력 방식에서는 `powerSettingNum`이 `NullOptional`이다.

`HandleModifyCookTimeSecondsCallback`은 추가 시간 자체가 아니라 합산된 `finalCookTimeSec`를 받는다.

`GetWattSettingByIndex`는 `0`부터 빈 인덱스 없이 조회할 수 있어야 한다. 성공 시 `CHIP_NO_ERROR`, 목록 범위를 벗어나면 `CHIP_ERROR_NOT_FOUND`를 반환한다.

### IntegrationDelegate와 CodegenIntegrationDelegate

| 메서드 | `CodegenIntegrationDelegate`의 동작 |
|---|---|
| `GetCurrentOperationalState` | `mOpStateInstance.GetCurrentOperationalState()` 호출 |
| `GetNormalOperatingMode` | `GetModeValueByModeTag`에 `MicrowaveOvenMode::ModeTag::kNormal`을 전달하여 모드 값 조회 |
| `IsSupportedMode` | `mMicrowaveOvenModeInstance.IsSupportedMode(mode)` 호출 |
| `IsSupportedOperationalStateCommand` | `CodegenDataModelProvider::Instance()`에서 `OperationalState::Id`의 수락 명령을 조회하고 `commandId` 검색 |

`IsSupportedOperationalStateCommand`는 수락 명령 조회가 실패하면 `false`를 반환한다.

### Instance 수명주기

생성 시 다음 객체와 설정을 전달한다.

- `Delegate * aDelegate`
- `EndpointId aEndpointId`
- `ClusterId aClusterId`
- `BitMask<MicrowaveOvenControl::Feature> aFeature`
- `Clusters::OperationalState::Instance & aOpStateInstance`
- `Clusters::ModeBase::Instance & aMicrowaveOvenModeInstance`

`aEndpointId`는 zap 설정과 일치해야 한다. 생성자는 `aClusterId == MicrowaveOvenControl::Id`를 `VerifyOrDie`로 검사한다.

호출자는 다음 수명 조건을 보장해야 한다.

- `Delegate`는 `Instance`의 전체 수명 동안 유효해야 한다.
- `OperationalState::Instance`와 `ModeBase::Instance`는 `Instance::Init()` 전에 생성 및 초기화되어 있어야 한다.

#### Init

`Instance::Init()`은 다음 순서로 처리한다.

1. `emberAfContainsServer`로 zap의 서버 클러스터 활성화 여부를 검사한다.
2. `Feature::kPowerAsNumber`와 `Feature::kPowerInWatts` 중 정확히 하나가 설정되어 있는지 검사한다.
3. `Feature::kPowerNumberLimits`가 설정되어 있으면 `Feature::kPowerAsNumber`도 설정되어 있는지 검사한다.
4. `emberAfContainsAttribute`로 `WattRating::Id`의 존재를 확인하여 `mOptionalAttributeSet`에 반영한다.
5. `emberAfFindServerCluster`로 서버 클러스터를 찾는다.
6. `acceptedCommandList`에서 `Commands::AddMoreTime::Id`를 찾아 지원 여부를 설정한다.
7. `mDelegate`가 유효한지 검사하고 `SetInstance(this)`를 호출한다.
8. `MicrowaveOvenControlCluster::Config`를 구성하고 `mCluster.Create`를 호출한다.
9. `CodegenDataModelProvider::Instance().Registry().Register`로 등록한다.

주요 실패 결과:

| 조건 | 결과 |
|---|---|
| zap에서 서버 클러스터 미활성화 | `CHIP_ERROR_INVALID_ARGUMENT` |
| 기능 조합이 유효하지 않음 | `CHIP_ERROR_INVALID_ARGUMENT` |
| 서버 클러스터를 찾지 못함 | `CHIP_ERROR_NOT_FOUND` |
| `mDelegate == nullptr` | `CHIP_ERROR_INCORRECT_STATE` |

#### Deinit

`Instance::Deinit()`은 delegate의 인스턴스 포인터를 해제하고, 클러스터가 생성되어 있는지 검사한다. 이후 `Registry().Unregister`를 호출하고 `mCluster.Destroy()`로 클러스터를 파괴한다.

- 클러스터가 생성되지 않았다면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
- 등록 해제 오류는 `LogErrorOnFailure`로 기록하고 반환한다.
- 소멸자는 `Deinit()`을 호출하며 반환값을 무시한다.

`Delegate::SetInstance`는 서로 다른 유효한 인스턴스로 직접 교체하는 것을 `VerifyOrDie`로 방지한다. 파생 클래스에는 `GetInstance()`의 const 및 비const 버전을 제공한다.

### 기본값과 Startup

| 상수 | 값 |
|---|---|
| `kDefaultCookTimeSec` | `30u` |
| `kMinCookTimeSec` | `1u` |
| `kDefaultMinPowerNum` | `10u` |
| `kDefaultMaxPowerNum` | `100u` |
| `kDefaultPowerStepNum` | `10u` |

생성자는 `mCookTimeSec`를 `kDefaultCookTimeSec`로 초기화한다.

`Startup()`은 `DefaultServerCluster::Startup(context)` 호출 후, `Feature::kPowerInWatts`가 설정된 경우 지원 와트 항목 수를 조회하여 `mSupportedWattLevels`에 저장한다. 항목 수가 `0`이면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.

`GetCountOfSupportedWattLevels()`는 인덱스 `0`부터 `GetWattSettingByIndex`를 호출하며, `CHIP_NO_ERROR`가 아닌 결과를 처음 만날 때까지의 항목 수를 반환한다.

### 속성 읽기와 노출

`ReadAttribute()`는 다음 값을 인코딩한다.

| 속성 | 값의 출처 |
|---|---|
| `ClusterRevision` | `MicrowaveOvenControl::kRevision` |
| `CookTime` | `GetCookTimeSec()` |
| `MaxCookTime` | `mAppDelegate.GetMaxCookTimeSec()` |
| `PowerSetting` | `mAppDelegate.GetPowerSettingNum()` |
| `MinPower` | `mAppDelegate.GetMinPowerNum()` |
| `MaxPower` | `mAppDelegate.GetMaxPowerNum()` |
| `PowerStep` | `mAppDelegate.GetPowerStepNum()` |
| `SupportedWatts` | `mAppDelegate.GetWattSettingByIndex()`의 순차 조회 결과 |
| `SelectedWattIndex` | `mAppDelegate.GetCurrentWattIndex()` |
| `WattRating` | `mAppDelegate.GetWattRating()` |
| `FeatureMap` | `mFeature` |

`SupportedWatts`를 읽을 때 `CHIP_ERROR_NOT_FOUND`는 정상적인 목록 종료로 처리한다. 다른 오류는 반환한다. 처리하지 않는 속성 ID에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes()`는 `AttributeListBuilder`로 `kMandatoryMetadata`와 다음 조건부 속성을 추가한다.

- `Feature::kPowerAsNumber`: `PowerSetting`
- `Feature::kPowerNumberLimits`: `MinPower`, `MaxPower`, `PowerStep`
- `Feature::kPowerInWatts`: `SupportedWatts`, `SelectedWattIndex`
- `mOptionalAttributeSet` 설정: `WattRating`

`SetCookTimeSec()`는 `1 <= cookTimeSec <= mAppDelegate.GetMaxCookTimeSec()`를 검사한다. 실패하면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환하고, 성공하면 `SetAttributeValue`로 `mCookTimeSec`와 `CookTime::Id`를 갱신한다.

`Instance::SetCookTimeSec()`는 이 메서드에 위임하지만 반환 오류는 무시한다.

### 명령 디스패치

`InvokeCommand()`는 `Commands::SetCookingParameters::DecodableType` 또는 `Commands::AddMoreTime::DecodableType`으로 인자를 디코딩한 뒤 각각 `HandleSetCookingParameters` 또는 `HandleAddMoreTime`을 호출한다. 그 외 명령에는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

`AcceptedCommands()`는 다음과 같이 명령을 노출한다.

- `SetCookingParameters`: 항상 추가
- `AddMoreTime`: `mSupportsAddMoreTime`이 `true`인 경우 추가

### SetCookingParameters 처리

#### 공통 검사와 기본값

1. 현재 상태가 `OperationalState::OperationalStateEnum::kStopped`가 아니면 `Status::InvalidInState`를 반환한다.
2. `startAfterSetting`이 제공되었다면 `OperationalState::Commands::Start::Id`의 지원 여부를 검사한다. 지원하지 않으면 `Status::InvalidCommand`를 반환한다.
   - 이 검사는 값이 `false`여도 필드가 존재하면 수행한다.
   - 생략 시 `reqStartAfterSetting`은 `false`이다.
3. `GetNormalOperatingMode`로 기본 모드를 조회한다. 실패하면 `Status::InvalidCommand`를 반환한다.
   - `cookMode`가 제공되어도 기본 모드 조회를 먼저 수행한다.
4. 생략된 `cookMode`는 조회한 기본 모드로 대체한다. 지원하지 않는 모드는 `Status::ConstraintError`이다.
5. 생략된 `cookTime`은 `30`초로 대체한다. `1`부터 `GetMaxCookTimeSec()`까지의 범위를 벗어나면 `Status::ConstraintError`이다.

#### 숫자 출력 방식

`Feature::kPowerAsNumber`가 설정된 경우:

- `wattSettingIndex`가 있으면 `Status::InvalidCommand`를 반환한다.
- 기본 최소 출력, 최대 출력, 간격은 각각 `10`, `100`, `10`이다.
- `Feature::kPowerNumberLimits`가 있으면 delegate의 `GetMinPowerNum`, `GetMaxPowerNum`, `GetPowerStepNum` 값을 사용한다.
- 생략된 `powerSetting`은 최대 출력으로 대체한다.
- 다음 조건을 만족하지 않으면 `Status::ConstraintError`를 반환한다.

```cpp
minPowerNum <= reqPowerSettingNum && reqPowerSettingNum <= maxPowerNum
(reqPowerSettingNum - minPowerNum) % powerStepNum == 0
```

검사 후 `HandleSetCookingParametersCallback`에 `MakeOptional(reqPowerSettingNum)`과 `NullOptional`을 전달한다.

#### 와트 출력 방식

숫자 출력 분기가 아닌 경우:

- `powerSetting`이 있으면 `Status::InvalidCommand`를 반환한다.
- `mSupportedWattLevels`가 `0`이면 `Status::ConstraintError`를 반환한다.
- 최대 인덱스는 `mSupportedWattLevels - 1`이다.
- 생략된 `wattSettingIndex`는 최대 인덱스로 대체한다.
- 요청 인덱스가 최대 인덱스를 초과하면 `Status::ConstraintError`를 반환한다.

검사 후 `HandleSetCookingParametersCallback`에 `NullOptional`과 `MakeOptional(reqWattSettingIndex)`를 전달한다.

#### 변경 알림과 조리 시간 갱신

콜백 전후의 delegate 값을 비교하여 변경 시 `NotifyAttributeChanged`를 호출한다.

- 숫자 출력 방식: `PowerSetting::Id`
- 와트 출력 방식: `SelectedWattIndex::Id`, `WattRating::Id`

이 비교와 알림은 콜백의 성공 여부와 별개로 수행한다.

콜백 결과가 `Status::Success`이면 `SetCookTimeSec(reqCookTimeSec)`를 호출한다. 이 갱신이 실패하면 `Status::Failure`를 반환하며, 그 외에는 콜백 상태를 반환한다.

### AddMoreTime 처리

`HandleAddMoreTime()`은 다음 순서로 처리한다.

1. 현재 상태가 `OperationalState::OperationalStateEnum::kError`이면 `Status::InvalidInState`를 반환한다.
2. 다음 조건으로 추가 시간과 합산 결과의 상한을 검사한다.

```cpp
commandData.timeToAdd <= mAppDelegate.GetMaxCookTimeSec()
GetCookTimeSec() <= mAppDelegate.GetMaxCookTimeSec() - commandData.timeToAdd
```

3. 범위를 초과하면 `Status::ConstraintError`를 반환하며 조리 시간은 변경하지 않는다.
4. `finalCookTimeSec = GetCookTimeSec() + commandData.timeToAdd`를 계산한다.
5. `HandleModifyCookTimeSecondsCallback(finalCookTimeSec)`를 호출한다.
6. 콜백이 `Status::Success`를 반환하면 `SetCookTimeSec(finalCookTimeSec)`로 갱신한다. 갱신 실패 시 `Status::Failure`를 반환한다.

### 제공된 코드에서 확인되는 검사 범위

- 기능 조합 검사는 `Instance::Init()`에 있다. 제공된 `MicrowaveOvenControlCluster::Startup()`에는 동일한 검사가 없다.
- `HandleSetCookingParameters()`에는 스펙의 선택 그룹 `b`에서 최소 하나의 필드가 존재하는지 확인하는 명시적 검사가 없다.
- `HandleAddMoreTime()`에는 `timeToAdd >= 1`을 직접 확인하는 검사가 없다. 스펙과 SDK XML에는 하한 `1`이 정의되어 있다.
- 와트 목록의 개수를 세는 함수와 `Startup()`에는 스펙의 최대 항목 수 `10`을 검사하는 코드가 없다.
- 숫자 출력 간격 검사에는 `powerStepNum`이 `0`인지 확인하는 코드가 없다.

### 전역 콜백

다음 콜백은 제공된 구현에서 본문이 비어 있다.

- `MatterMicrowaveOvenControlClusterInitCallback`
- `MatterMicrowaveOvenControlClusterShutdownCallback`
- `MatterMicrowaveOvenControlPluginServerInitCallback`
- `MatterMicrowaveOvenControlPluginServerShutdownCallback`

## 관련 페이지

**사용 기기**

- [Microwave Oven](../device-types/microwave-oven.md)
