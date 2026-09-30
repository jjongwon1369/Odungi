---
entity: ModeBase
ids: []
source_paths: ['data_model/1.7/clusters/ModeBase.xml', 'src/app/clusters/mode-base-server/AppDelegate.h', 'src/app/clusters/mode-base-server/CodegenIntegration.cpp', 'src/app/clusters/mode-base-server/CodegenIntegration.h', 'src/app/clusters/mode-base-server/Delegate.h', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp', 'src/app/clusters/mode-base-server/ModeBaseCluster.h', 'src/app/clusters/mode-base-server/mode-base-cluster-objects.h', 'src/app/clusters/mode-base-server/mode-base-server.h', 'src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# ModeBase

## 개요

`ModeBase`는 지원되는 모드 목록과 현재 모드를 제공하고, 모드 값 또는 core mode tag를 통해 모드 전환을 처리하는 기반 클러스터이다.

- 스펙 이름: `Mode Base Cluster`
- revision: `3`
- 분류: `hierarchy="base"`, `role="application"`, `scope="Endpoint"`
- PICS 코드: `MODB`
- 제공된 스펙에는 `Mode Base`의 숫자 클러스터 ID가 없다.
- 구현은 `ModeBaseCluster`의 공통 처리와 `AppDelegate`의 애플리케이션별 동작을 분리한다.
- `Instance`와 `CodegenModeBaseCluster`는 codegen 등록 및 기존 영속 저장소 마이그레이션을 담당한다.

## 스펙

출처: `data_model/1.7/clusters/ModeBase.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 최초 정의 |
| `2` | `InvalidInMode` 상태에서 `ChangeToModeResponse`의 `StatusText` 제공 요구, 최소 하나의 표준 mode tag 요구, 기반/파생 클러스터의 예약 범위 정의 |
| `3` | `CoreModeTags` 속성과 `ChangeToModeByCoreTag` 명령 추가 |

예약 범위의 구체적인 값은 제공된 XML에 나타나지 않는다.

### Feature

| bit | code | name | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터 의존성 | 선택 |
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 core mode 지원 | `otherwiseConform`에 `provisionalConform`, `optionalConform` 지정 |

### 데이터 구조

#### `ModeOptionStruct`

| 필드 ID | 이름 | 타입 | 요구 사항 | 제약 |
|---|---|---|---|---|
| `0` | `Label` | `string` | 필수, `fixed` | 최대 길이 `64` |
| `1` | `Mode` | `uint8` | 필수, `fixed` | 별도 값 제약 미기재 |
| `2` | `ModeTags` | `list` of `ModeTagStruct` | 필수, `fixed` | 최대 `8`개 |

#### `ModeTagStruct`

| 필드 ID | 이름 | 타입 | 요구 사항 |
|---|---|---|---|
| `0` | `MfgCode` | `vendor-id` | 선택 |
| `1` | `Value` | `enum16` | 필수 |

### 속성

모든 속성의 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 쓰기 권한 | 영속성 | 적합성 및 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `list` of `ModeOptionStruct` | 없음 | `fixed` | 필수, `2`~`255`개 |
| `0x0001` | `CurrentMode` | `uint8` | 없음 | `nonVolatile` | 필수 |
| `0x0002` | `StartUpMode` | `uint8` | `operate` | `nonVolatile` | 선택, nullable, 기본값 `MS` |
| `0x0003` | `OnMode` | `uint8` | `operate` | `nonVolatile` | nullable, `DEPONOFF` 조건에서 필수 |
| `0x0004` | `CoreModeTags` | `list` of `enum16` | 없음 | `fixed` | `1`~`16`개, `otherwiseConform`에 `provisionalConform`과 `COREMODES` 조건의 필수 적합성 지정 |

`CurrentMode`, `StartUpMode`, `OnMode`의 추가 제약은 XML에서 빈 `desc`로만 표시되어 있다.

### 명령

| ID | 이름 | 방향 | 응답 | 적합성 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `commandToServer` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `responseFromServer` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `commandToServer` | `ChangeToModeResponse` | `otherwiseConform`에 `provisionalConform`과 `COREMODES` 조건의 필수 적합성 지정 |

`ChangeToMode`의 호출 권한은 `operate`이다. `ChangeToModeByCoreTag`의 호출 권한은 제공된 XML에 명시되어 있지 않다.

| 명령 | 필드 ID | 필드 | 타입 | 요구 사항 |
|---|---|---|---|---|
| `ChangeToMode` | `0` | `NewMode` | `uint8` | 필수 |
| `ChangeToModeResponse` | `0` | `Status` | `enum8` | 필수 |
| `ChangeToModeResponse` | `1` | `StatusText` | `string` | 최대 길이 `64`; `Status`가 `SUCCESS`이면 선택, 그 외 필수 |
| `ChangeToModeByCoreTag` | `0` | `NewModeTag` | `enum16` | 필수 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml`

### 코드 생성 범위

SDK XML 주석은 zap이 클러스터 ID가 없는 클러스터의 코드 생성을 지원하지 않으므로, 공통 `StatusCode`와 `ModeTag`를 `ModeBase` 네임스페이스의 `mode-base-cluster-objects.h`에 정의한다고 설명한다. 해당 열거형 값은 파생 클러스터에도 복사되어 있다.

실제 XML 요소로 정의된 구조체는 다음과 같다.

| 구조체 | 필드 | SDK 타입 | 정의 |
|---|---|---|---|
| `ModeTagStruct` | `MfgCode` | `vendor_id` | 선택, 주석에서 deprecated로 표시 |
| `ModeTagStruct` | `Value` | `enum16` | 필수 |
| `ModeOptionStruct` | `Label` | `char_string` | 필수, `length="64"` |
| `ModeOptionStruct` | `Mode` | `int8u` | 필수 |
| `ModeOptionStruct` | `ModeTags` | `ModeTagStruct` | 필수, `array="true"`, `length="8"` |

두 구조체에 명시된 클러스터 연결은 `0x0051`과 `0x0052`이다. 다른 파생 클러스터 이름은 이 부분에서 주석으로만 나타난다.

### 주석 처리된 클러스터 정의

`Mode Base`의 클러스터 블록 전체는 주석 처리되어 있으며, 활성 클러스터 정의가 아니다.

- `SupportedModes`, `CurrentMode`, `StartUpMode`, `OnMode`가 기재되어 있다.
- `ChangeToMode`, `ChangeToModeResponse`가 기재되어 있다.
- `CoreModeTags`, `ChangeToModeByCoreTag`는 이 SDK XML에 정의되어 있지 않다.
- `0xFFFD` 전역 속성 값은 `2`로 기재되어 있다.
- `StatusText`는 `optional="true"`로 기재되어 있어, revision `3` 스펙 XML의 상태별 필수 조건과 표현이 다르다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/mode-base-server/AppDelegate.h` | 애플리케이션별 모드 데이터 및 전환 처리 인터페이스 |
| `src/app/clusters/mode-base-server/Delegate.h` | `AppDelegate`를 확장하여 `Instance` 접근 제공 |
| `src/app/clusters/mode-base-server/ModeBaseCluster.h` | `ModeBaseCluster`, `Config`, 속성 및 명령 API 선언 |
| `src/app/clusters/mode-base-server/ModeBaseCluster.cpp` | 시작 처리, 속성 접근, 모드 검색, 명령 처리, 영속 저장 |
| `src/app/clusters/mode-base-server/CodegenIntegration.h` | `CodegenModeBaseCluster`, `Instance` 선언 |
| `src/app/clusters/mode-base-server/CodegenIntegration.cpp` | codegen 설정 검증, 등록, 해제 및 시작 시 마이그레이션 연결 |
| `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h` | `MigrateModeBaseServerStorage` 선언 |
| `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp` | 기존 속성 저장소 마이그레이션 |
| `src/app/clusters/mode-base-server/mode-base-cluster-objects.h` | 파생 클러스터 매핑, 속성 별칭, 공통 열거형 |
| `src/app/clusters/mode-base-server/mode-base-server.h` | `app/clusters/mode-base-server/CodegenIntegration.h` 포함 |

### 공통 타입 및 파생 클러스터

`chip::app::Clusters::ModeBase`의 `ClusterEntry`는 `ClusterId id`와 `uint32_t revision`을 보관한다.

다음 상수는 각 파생 클러스터의 `Id`와 `kRevision`을 연결하며, `kAliasedClusters`에도 포함된다.

- `kDeviceEnergyManagementMode`
- `kDishwasherMode`
- `kEnergyEvseMode`
- `kLaundryWasherMode`
- `kMicrowaveOvenMode`
- `kOvenMode`
- `kRefrigeratorAndTemperatureControlledCabinetMode`
- `kRvcCleanMode`
- `kRvcRunMode`
- `kThermostatMode`
- `kWaterHeaterMode`

공통 정의의 연결 방식은 다음과 같다.

| 정의 | 연결 대상 또는 값 |
|---|---|
| `Commands` | `ThermostatMode::Commands` |
| `SupportedModes` | `DeviceEnergyManagementMode::Attributes::SupportedModes` |
| `CurrentMode` | `DeviceEnergyManagementMode::Attributes::CurrentMode` |
| `CoreModeTags` | `ThermostatMode::Attributes::CoreModeTags` |
| `StartUpMode::Id` | `0x00000002` |
| `OnMode::Id` | `0x00000003` |

`StartUpMode`와 `OnMode`의 `TypeInfo`는 `DataModel::Nullable<uint8_t>`를 사용하며, `MustUseTimedWrite()`는 `false`를 반환한다. 읽기/쓰기 메타데이터 권한은 각각 `Access::Privilege::kView`, `Access::Privilege::kOperate`이다.

`kMandatoryMetadata`에는 `SupportedModes::kMetadataEntry`와 `CurrentMode::kMetadataEntry`가 포함된다. `GeneratedCommandList`, `AcceptedCommandList`, `AttributeList`, `FeatureMap`, `ClusterRevision`은 `DeviceEnergyManagementMode::Attributes`의 대응 정의를 사용한다.

### 열거형

#### `ModeTag`

| 값 | 식별자 |
|---|---|
| `0x0` | `kAuto` |
| `0x1` | `kQuick` |
| `0x2` | `kQuiet` |
| `0x3` | `kLowNoise` |
| `0x4` | `kLowEnergy` |
| `0x5` | `kVacation` |
| `0x6` | `kMin` |
| `0x7` | `kMax` |
| `0x8` | `kNight` |
| `0x9` | `kDay` |

#### `StatusCode`

| 값 | 식별자 |
|---|---|
| `0x0` | `kSuccess` |
| `0x1` | `kUnsupportedMode` |
| `0x2` | `kGenericFailure` |
| `0x3` | `kInvalidInMode` |

#### `Feature`

| 식별자 | 구현 값 |
|---|---|
| `kOnOff` | `0x1` |
| `kCoreModes` | `to_underlying(ThermostatMode::Feature::kCoreModes)` |

### `AppDelegate`와 `Delegate`

`AppDelegate`의 필수 구현 메서드는 다음과 같다.

| 메서드 | 역할 |
|---|---|
| `Init()` | 애플리케이션 초기화 |
| `GetModeLabelByIndex` | 인덱스로 모드 레이블 제공 |
| `GetModeValueByIndex` | 인덱스로 모드 값 제공 |
| `GetModeTagsByIndex` | 인덱스로 모드 태그 목록 제공 |
| `HandleChangeToMode` | 전환 허용 여부 결정 및 응답 작성 |

목록 인덱스는 `0`부터 빈틈없이 이어져야 한다. 정상 반환은 `CHIP_NO_ERROR`, 목록 끝은 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`로 표시한다.

- 레이블 복사에는 `CopyCharSpanToMutableCharSpan` 사용이 안내되어 있다.
- 태그 버퍼에는 초기화한 항목을 기록한 뒤 `reduce_size`로 실제 항목 수를 지정해야 한다.
- 지원 모드 목록이 바뀌면 `ReportSupportedModesChange()`를 호출해야 한다.
- 전환 처리 오류는 `response.status`로 전달한다.

core mode 관련 기본 동작:

- `GetCoreModeTagByIndex`는 기본적으로 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.
- `HandleChangeToModeByCoreTag`는 기본적으로 `HandleChangeToMode(newMode, response)`를 호출한다.
- `newMode`는 클러스터가 선택한 초기 모드 값을 전달받는 입출력 인자이다. delegate는 같은 태그를 가진 다른 지원 모드로 변경할 수 있다.

`Delegate`는 `AppDelegate`를 상속하며, `SetInstance`와 protected `GetInstance()` 오버로드로 연결된 `Instance`에 접근한다.

### `Instance` 초기화와 해제

`Instance` 생성 인자는 `aDelegate`, `aEndpointId`, `aClusterId`, `aFeature`이다. 호출자는 delegate의 수명이 `Instance`의 수명 전체를 포함하도록 보장해야 한다.

`Instance::Init()`의 실행 순서는 다음과 같다.

1. `emberAfFindServerCluster`로 서버 클러스터를 확인한다. 없으면 `CHIP_ERROR_NOT_FOUND`를 반환한다.
2. `kAliasedClusters`에서 파생 클러스터를 찾는다. 없으면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
3. `StartUpMode`와 feature 구성을 검증한다.
   - `ThermostatMode::Id`에서는 속성이 존재하면 `mOptionalAttributeSet`에 `StartUpMode::Id`를 설정한다.
   - 나머지 클러스터에서는 `StartUpMode`가 없어야 하고, `ModeBase::Feature::kCoreModes`가 비활성화되어 있어야 한다.
4. `MATTER_DM_PLUGIN_ON_OFF_SERVER` 조건에서 시작 시 `OnOff` 값을 확인한다.
   - 동일 endpoint에 필요한 서버와 속성이 있고 `ModeBase::Feature::kOnOff`가 활성화되어 있어야 한다.
   - `StartUpOnOff`가 알려진 volatile 속성이 아니며 `getOnOffValueForStartUp`이 `Status::Success`를 반환하면 값을 반영한다.
   - 해당 컴파일 조건이 없으면 `ModeBase::Feature::kOnOff`가 비활성화되어 있어야 한다.
5. delegate가 있는지 확인하고 `SetInstance(this)`, `Init()`을 호출한다.
6. `ModeBaseCluster::Config`를 구성하고 `mCluster.Create`를 호출한다.
7. `RegisterThisInstance()`와 `CodegenDataModelProvider::Instance().Registry().Register`를 호출한다.

`GetModeBaseInstanceList()`는 `gModeBaseInstances`를 반환한다. 등록과 해제는 각각 `RegisterThisInstance()`, `UnregisterThisInstance()`가 처리한다.

`Shutdown()`은 delegate 연결을 해제하고 목록에서 제거한 뒤, 생성된 클러스터가 있으면 레지스트리에서 해제하고 파괴한다. `Instance::~Instance()`는 `Shutdown()`을 호출한다.

> `AppDelegate::Init()` 주석은 검증 및 등록 이후 호출된다고 설명하지만, 제공된 `Instance::Init()`에서는 클러스터 생성·등록 전에 호출된다. 또한 소멸자 선언 주석에는 `Deinit()`이 언급되지만 실제 해제 API와 소멸자 호출은 `Shutdown()`이다.

### `ModeBaseCluster` 시작 처리

`ModeBaseCluster`는 `chip::app::Clusters`에 정의되며 `DefaultServerCluster`를 상속한다.

`Config`는 다음 값을 받는다.

- `feature`
- `optionalAttributeSet`
- `appDelegate`
- `onOffValueForStartUp` — 기본값 `false`
- `diagnosticDataProvider`

`Startup()`은 다음 순서로 동작한다.

1. `DefaultServerCluster::Startup` 호출.
2. `GetModeValueByIndex(0, mCurrentMode)`로 첫 번째 지원 모드를 초기값으로 설정.
3. `LoadPersistentAttributes()`로 저장된 속성 로드.
4. `StartUpMode`가 null이 아니면 부팅 원인 확인.
   - `BootReasonType::kSoftwareUpdateCompleted`이면 `StartUpMode` 적용을 생략한다.
   - 부팅 원인 조회 실패 시 `BootReasonType::kUnspecified`로 처리한다.
   - 그 외에는 현재 값과 다를 때 `UpdateCurrentMode`로 `StartUpMode`를 적용한다.
5. `mOnOffValueForStartUp`이 참이고 `OnMode`가 null이 아니면 `OnMode`를 적용한다.

따라서 두 시작 조건이 모두 적용되면 `OnMode` 처리가 `StartUpMode` 처리보다 나중에 수행된다. 시작 중 `UpdateCurrentMode`가 실패하면 해당 상태를 `CHIP_ERROR`로 변환하여 반환한다.

### 속성 접근과 영속 저장

- `ReadAttribute`는 `ClusterRevision`, `SupportedModes`, `CurrentMode`, `StartUpMode`, `OnMode`, `CoreModeTags`, `FeatureMap`을 처리한다.
- `ClusterRevision`은 전달된 `ClusterEntry`의 revision을 사용한다.
- `WriteAttribute`는 `StartUpMode`와 `OnMode`만 처리한다.
- 그 외 속성 요청은 `Status::UnsupportedAttribute`를 반환한다.

`Attributes()`는 필수 속성에 다음 조건부 속성을 추가한다.

| 속성 | 노출 조건 |
|---|---|
| `StartUpMode` | `mOptionalAttributeSet.IsSet(StartUpMode::Id)` |
| `OnMode` | `mFeature.Has(Feature::kOnOff)` |
| `CoreModeTags` | `mFeature.Has(Feature::kCoreModes)` |

`UpdateCurrentMode`는 지원 모드만 허용한다. `UpdateStartUpMode`와 `UpdateOnMode`는 null 또는 지원 모드를 허용한다. 제약 위반은 `Status::ConstraintError`를 반환한다.

값이 변경되고 `mContext`가 있으면 `AttributePersistence::StoreNativeEndianValue`로 저장한다. 저장 실패는 `LogErrorOnFailure`로 기록하며, 이 실패 자체를 반환 상태로 전파하지 않는다.

`LoadPersistentAttributes()`는 `CurrentMode`를 로드하고, 지원 조건에 따라 `StartUpMode`와 `OnMode`를 로드한다. 로드된 값도 대응하는 update 메서드로 검증한다.

`ReportSupportedModesChange()`는 `NotifyAttributeChanged(SupportedModes::Id)`를 호출한다.

### 모드 검색 및 목록 인코딩

| 메서드 | 동작 |
|---|---|
| `IsSupportedMode` | `GetModeValueByIndex`를 순회하여 모드 값 확인 |
| `GetModeValueByModeTag` | 태그 값이 일치하는 첫 번째 모드의 값 반환 |
| `IsSupportedCoreModeTag` | `GetCoreModeTagByIndex`를 순회하여 태그 지원 여부 확인 |
| `ModeHasTag` | 특정 모드의 태그 목록에 지정 태그가 있는지 확인 |
| `EncodeSupportedModes` | 레이블, 모드 값, 태그를 읽어 목록 인코딩 |
| `EncodeCoreModeTags` | core mode tag 목록 인코딩 |

`GetModeValueByModeTag`와 `ModeHasTag`는 태그의 `value`를 비교하며 `MfgCode`는 비교하지 않는다.

인코딩 버퍼 상수는 `kMaxModeLabelSize = 64`, `kMaxNumOfModeTags = 8`이다.

### 명령 노출과 실행

`AcceptedCommands()`는 다음과 같이 명령을 노출한다.

- `MicrowaveOvenMode::Id`를 제외하면 `ChangeToMode`를 추가한다.
- `Feature::kCoreModes`가 활성화되어 있으면 `ChangeToModeByCoreTag`를 추가한다.

`GeneratedCommands()`는 `MicrowaveOvenMode::Id`를 제외하면 `ChangeToModeResponse`를 추가한다.

`InvokeCommand()`는 두 입력 명령을 디코딩해 대응 핸들러를 호출하며, 다른 명령에는 `Status::UnsupportedCommand`를 반환한다.

#### `HandleChangeToMode`

1. `NewMode`가 지원되지 않으면 `StatusCode::kUnsupportedMode`로 응답한다.
2. `CurrentMode`와 같으면 delegate 호출 없이 `StatusCode::kSuccess`로 응답한다.
3. 그 외에는 `mAppDelegate.HandleChangeToMode`를 호출한다.
4. `response.status`가 `StatusCode::kSuccess`이면 `UpdateCurrentMode`를 호출한다.
5. 업데이트 실패 시 `StatusCode::kGenericFailure`로 응답한다.

#### `HandleChangeToModeByCoreTag`

1. `NewModeTag`가 `CoreModeTags`에 없으면 `StatusCode::kUnsupportedMode`로 응답하고 현재 모드를 유지한다.
2. 현재 모드가 해당 태그를 가지면 현재 모드를 초기 후보로 사용한다.
3. 그렇지 않으면 해당 태그를 가진 첫 번째 지원 모드를 찾는다. 실패하면 `StatusCode::kGenericFailure`로 응답한다.
4. `mAppDelegate.HandleChangeToModeByCoreTag`를 호출한다.
5. delegate가 성공을 반환하면 선택된 모드가 지원되며 요청한 태그를 갖는지 다시 검증한다.
6. 검증 실패 또는 업데이트 실패 시 `StatusCode::kGenericFailure`로 응답한다.
7. 선택된 모드가 현재 모드와 같으면 값을 변경하지 않는다.

`ChangeToMode`와 달리, core mode tag 처리에서는 현재 모드가 초기 후보로 선택되어도 delegate를 호출한다.

자동 실패 응답 분기에서는 `response.status`만 명시적으로 설정한다. 제공된 코드에는 해당 분기에서 `StatusText`를 직접 설정하는 구문이 없다.

### 저장소 마이그레이션

`CodegenModeBaseCluster::Startup()`은 영속 저장소 provider를 사용할 수 있는 시점에 마이그레이션을 수행한다.

- 원본: `GetSafeAttributePersistenceProvider()`
- 대상: `context.attributeStorage`
- 원본 provider가 있으면 `MigrateModeBaseServerStorage` 호출
- 실패는 `LogErrorOnFailure`로 기록
- 이후 `ModeBaseCluster::Startup(context)` 호출

`MigrateModeBaseServerStorage`의 대상은 다음과 같다.

- `Attributes::CurrentMode::Id`
- `Attributes::StartUpMode::Id`
- `Attributes::OnMode::Id`

각 항목은 `sizeof(uint8_t)`와 `isScalar = true`로 지정된다. `MaxAttrMigrationValueSize`로 버퍼 크기를 계산한 뒤 `MigrateFromSafeToAttributePersistenceProvider`로 이전한다.

### `Instance`의 추가 API

`Instance`는 속성 getter/setter, `ReportSupportedModesChange`, `IsSupportedMode`, `GetModeValueByModeTag`, `IsSupportedCoreModeTag`를 내부 클러스터에 전달하며, 호출 전 `VerifyOrDie(mCluster.IsConstructed())`로 생성 여부를 확인한다.

추가로 다음 API를 제공한다.

- `GetEndpointId()` — endpoint ID 반환
- `HasFeature()` — feature 지원 여부 확인
- `GetFailTransition()` — `mFailTransition` 반환
- `ToggleFailTransition()` — `mFailTransition` 반전

제공된 명령 처리 구현에는 `mFailTransition`을 참조하는 코드가 없다.

## 관련 페이지

**파생 클러스터**

- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)
- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
