---
entity: ModeBase
ids: []
source_paths: ['src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml', 'src/app/clusters/mode-base-server/Delegate.h', 'src/app/clusters/mode-base-server/AppDelegate.h', 'src/app/clusters/mode-base-server/mode-base-cluster-objects.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h', 'src/app/clusters/mode-base-server/CodegenIntegration.h', 'src/app/clusters/mode-base-server/CodegenIntegration.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp', 'src/app/clusters/mode-base-server/mode-base-server.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.h', 'data_model/1.7/clusters/ModeBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
---

# ModeBase

## 개요

`ModeBase`는 지원되는 모드 목록에서 장치의 동작 모드를 선택하기 위한 기반 클러스터이다. `SupportedModes`로 선택 가능한 모드를 제공하고, `CurrentMode`로 현재 모드를 나타낸다.

- 스펙의 이름은 `Mode Base Cluster`이며, revision은 `3`이다.
- 분류는 `hierarchy="base"`, `role="application"`, `scope="Endpoint"`이고, PICS 코드는 `MODB`이다.
- 제공된 스펙에는 `Mode Base` 자체의 숫자 클러스터 ID가 없다.
- 구현은 `ModeBaseCluster`가 공통 동작을 담당하고, `AppDelegate`가 애플리케이션별 모드 정보와 전환 정책을 제공하는 구조이다.
- `Instance`와 `CodegenModeBaseCluster`는 ZAP 설정 및 `CodegenDataModelProvider`와의 통합을 담당한다.

## 스펙

출처: `data_model/1.7/clusters/ModeBase.xml`

### revision 이력

| revision | 변경 내용 |
|---|---|
| `1` | 최초 정의 |
| `2` | `ChangeToModeResponse`의 `InvalidInMode` 상태에서 `StatusText` 제공 요구, 최소 하나의 표준 모드 태그 요구, 기반/파생 클러스터의 예약 범위 정의 |
| `3` | `CoreModeTags` 속성과 `ChangeToModeByCoreTag` 명령 추가 |

### Feature

| bit | 코드 | 이름 | 적합성 및 설명 |
|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | 선택 사항. `OnOff` 클러스터와의 의존성 |
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 핵심 모드 지원. `otherwiseConform`에 `provisionalConform`과 `optionalConform` 정의 |

### 데이터 타입

#### ModeOptionStruct

| 필드 ID | 이름 | 타입 | 필수 여부 | 제약 및 품질 |
|---|---|---|---|---|
| `0` | `Label` | `string` | 필수 | 최대 길이 `64`, `persistence="fixed"` |
| `1` | `Mode` | `uint8` | 필수 | `persistence="fixed"` |
| `2` | `ModeTags` | `list` | 필수 | 항목 타입 `ModeTagStruct`, 최대 `8`개, `persistence="fixed"` |

#### ModeTagStruct

| 필드 ID | 이름 | 타입 | 필수 여부 |
|---|---|---|---|
| `0` | `MfgCode` | `vendor-id` | 선택 |
| `1` | `Value` | `enum16` | 필수 |

### 속성

| ID | 이름 | 타입 | 접근 권한 | 적합성 | 제약 및 품질 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `list<ModeOptionStruct>` | 읽기: `view` | 필수 | `2`~`255`개, `persistence="fixed"` |
| `0x0001` | `CurrentMode` | `uint8` | 읽기: `view` | 필수 | `persistence="nonVolatile"` |
| `0x0002` | `StartUpMode` | `uint8` | 읽기: `view`, 쓰기: `operate` | 선택 | nullable, `persistence="nonVolatile"`, 기본값 `MS` |
| `0x0003` | `OnMode` | `uint8` | 읽기: `view`, 쓰기: `operate` | `DEPONOFF` 지원 시 필수 | nullable, `persistence="nonVolatile"` |
| `0x0004` | `CoreModeTags` | `list<enum16>` | 읽기: `view` | `otherwiseConform`에 `provisionalConform` 및 `COREMODES` 조건부 필수 정의 | `1`~`16`개, `persistence="fixed"` |

`CurrentMode`, `StartUpMode`, `OnMode`의 추가 제약은 제공된 XML에서 빈 `<desc/>`로 표시되어 있다.

### 명령

| ID | 이름 | 방향 | 응답 | 적합성 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `commandToServer` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `responseFromServer` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `commandToServer` | `ChangeToModeResponse` | `otherwiseConform`에 `provisionalConform` 및 `COREMODES` 조건부 필수 정의 |

`ChangeToMode`의 호출 권한은 `operate`이다. 제공된 XML에는 `ChangeToModeByCoreTag`의 호출 권한이 명시되어 있지 않다.

| 명령 | 필드 ID | 필드 | 타입 | 조건 |
|---|---|---|---|---|
| `ChangeToMode` | `0` | `NewMode` | `uint8` | 필수 |
| `ChangeToModeResponse` | `0` | `Status` | `enum8` | 필수 |
| `ChangeToModeResponse` | `1` | `StatusText` | `string` | 최대 길이 `64`. `Status`가 `SUCCESS`이면 선택, 그 외에는 필수 |
| `ChangeToModeByCoreTag` | `0` | `NewModeTag` | `enum16` | 필수 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml`

### 공통 구조체

| 구조체 | 필드 | SDK 타입 | 선택 여부 | 추가 정의 |
|---|---|---|---|---|
| `ModeTagStruct` | `MfgCode` | `vendor_id` | 선택 | 주석에서 deprecated로 표시 |
| `ModeTagStruct` | `Value` | `enum16` | 필수 | — |
| `ModeOptionStruct` | `Label` | `char_string` | 필수 | `length="64"` |
| `ModeOptionStruct` | `Mode` | `int8u` | 필수 | — |
| `ModeOptionStruct` | `ModeTags` | `ModeTagStruct` | 필수 | `array="true"`, `length="8"` |

두 구조체에 연결된 클러스터는 다음과 같다. 이름은 XML 주석에 표시된 이름이다.

| 클러스터 ID | 이름 |
|---|---|
| `0x0051` | Laundry Washer Mode |
| `0x0052` | Refrigerator and temperature controlled cabinet Mode |
| `0x0054` | RVC Run Mode |
| `0x0055` | RVC Clean Mode |
| `0x0059` | Dishwasher Mode |
| `0x005E` | Microwave Oven Mode |
| `0x0049` | Oven Mode |
| `0x009D` | Energy EVSE Mode |
| `0x009E` | Water Heater Mode |
| `0x009F` | Device Energy Management Mode |

### 코드 생성 제한과 주석 처리된 정의

SDK XML 주석에 따르면, ZAP은 클러스터 ID가 없는 클러스터의 코드 생성을 지원하지 않는다. 이에 따라 공통 `StatusCode`와 `ModeTag` 값은 `mode-base-cluster-objects.h`의 `ModeBase` 네임스페이스에서 정의하며, 파생 클러스터에도 각 값을 복사하여 나열한다.

XML의 `Mode Base` 클러스터 본문은 전체가 주석 처리되어 있다. 해당 본문에는 다음 정의가 포함된다.

- `SupportedModes`, `CurrentMode`, `StartUpMode`, `OnMode`
- `ChangeToMode`, `ChangeToModeResponse`
- `0xFFFD`에 대한 값 `2`
- `SupportedModes`의 `length="255"`
- `CurrentMode`의 `reportable="true"`
- 각 속성의 `storage="external"`

이 주석 처리된 본문은 스펙 revision `3`과 다음 차이가 있다.

- `CoreModeTags`와 `ChangeToModeByCoreTag`가 없다.
- `StatusText`가 조건 없이 `optional="true"`로 표시되어 있다.
- `ChangeToModeResponse` 설명은 `ChangeToModeWithStatus` 수신을 언급하지만, 해당 본문에 정의된 요청 명령 이름은 `ChangeToMode`이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/mode-base-server/AppDelegate.h` | 애플리케이션별 모드 정보와 전환 정책 인터페이스 |
| `src/app/clusters/mode-base-server/Delegate.h` | `AppDelegate` 확장 및 `Instance` 연결 |
| `src/app/clusters/mode-base-server/mode-base-cluster-objects.h` | 공통 별칭, 속성 메타데이터, 열거형 |
| `src/app/clusters/mode-base-server/ModeBaseCluster.h` | `ModeBaseCluster` 및 `Config` 선언 |
| `src/app/clusters/mode-base-server/ModeBaseCluster.cpp` | 속성 접근, 명령 처리, 초기화, 영속 저장 구현 |
| `src/app/clusters/mode-base-server/CodegenIntegration.h` | `CodegenModeBaseCluster`, `Instance` 선언 |
| `src/app/clusters/mode-base-server/CodegenIntegration.cpp` | ZAP 검증, 등록, 종료, 시작 시 저장소 마이그레이션 |
| `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h` | `MigrateModeBaseServerStorage` 선언 |
| `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp` | 영속 속성 마이그레이션 구현 |
| `src/app/clusters/mode-base-server/mode-base-server.h` | `CodegenIntegration.h` 포함 |

### 공통 정의와 별칭

`chip::app::Clusters::ModeBase`의 `ClusterEntry`는 `ClusterId id`와 `uint32_t revision`을 가진다. 각 항목은 해당 파생 클러스터의 `Id`와 `kRevision`을 사용한다.

`kAliasedClusters`에는 다음 `11`개 항목이 포함된다.

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

제공된 SDK XML의 구조체 연결 목록에는 `ThermostatMode`가 없지만, 구현의 별칭 목록에는 포함되어 있다.

| 정의 | 연결 또는 내용 |
|---|---|
| `Commands` | `ThermostatMode::Commands` |
| `Attributes::SupportedModes` | `DeviceEnergyManagementMode::Attributes::SupportedModes` |
| `Attributes::CurrentMode` | `DeviceEnergyManagementMode::Attributes::CurrentMode` |
| `Attributes::CoreModeTags` | `ThermostatMode::Attributes::CoreModeTags` |
| `StartUpMode::Id` | `0x00000002` |
| `OnMode::Id` | `0x00000003` |
| `kMandatoryMetadata` | `SupportedModes::kMetadataEntry`, `CurrentMode::kMetadataEntry` |

`StartUpMode`와 `OnMode`의 `Type` 및 `DecodableType`은 `DataModel::Nullable<uint8_t>`이다. 두 속성의 `MustUseTimedWrite()`는 `false`를 반환하며, 메타데이터의 읽기/쓰기 권한은 각각 `Access::Privilege::kView`, `Access::Privilege::kOperate`이다.

`GeneratedCommandList`, `AcceptedCommandList`, `AttributeList`, `FeatureMap`, `ClusterRevision`은 `DeviceEnergyManagementMode::Attributes`의 해당 정의를 사용한다.

### 열거형

#### ModeTag

기반 타입은 `uint16_t`이다.

| 값 | 이름 |
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

#### StatusCode

기반 타입은 `uint8_t`이다.

| 값 | 이름 |
|---|---|
| `0x0` | `kSuccess` |
| `0x1` | `kUnsupportedMode` |
| `0x2` | `kGenericFailure` |
| `0x3` | `kInvalidInMode` |

#### Feature

기반 타입은 `uint32_t`이다.

| 이름 | 정의 |
|---|---|
| `kOnOff` | `0x1` |
| `kCoreModes` | `to_underlying(ThermostatMode::Feature::kCoreModes)` |

### AppDelegate와 Delegate

`AppDelegate`는 애플리케이션이 구현할 인터페이스이다.

| 함수 | 역할 |
|---|---|
| `Init()` | 애플리케이션 초기화. 순수 가상 함수 |
| `GetModeLabelByIndex(uint8_t modeIndex, MutableCharSpan & label)` | 모드 라벨 제공 |
| `GetModeValueByIndex(uint8_t modeIndex, uint8_t & value)` | 모드 값 제공 |
| `GetModeTagsByIndex(uint8_t modeIndex, DataModel::List<detail::Structs::ModeTagStruct::Type> & modeTags)` | 모드 태그 목록 제공 |
| `HandleChangeToMode(uint8_t NewMode, ModeBase::Commands::ChangeToModeResponse::Type & response)` | 모드 전환 허용 여부 결정 및 응답 작성 |
| `GetCoreModeTagByIndex(uint8_t tagIndex, uint16_t & tag)` | 핵심 모드 태그 제공. 기본 구현은 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED` 반환 |
| `HandleChangeToModeByCoreTag(uint16_t newModeTag, uint8_t & newMode, ModeBase::Commands::ChangeToModeResponse::Type & response)` | 태그 기반 전환 정책. 기본 구현은 `HandleChangeToMode(newMode, response)` 호출 |

목록 제공 함수의 계약은 다음과 같다.

- 인덱스는 `0`부터 시작하며 중간에 빈 인덱스가 없어야 한다.
- 성공하면 `CHIP_NO_ERROR`, 목록 끝이면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.
- 라벨 복사에는 `CopyCharSpanToMutableCharSpan`을 사용하도록 안내한다.
- 태그 버퍼에는 초기화한 항목을 기록하고 목록 크기를 줄여야 한다. 주석은 이 작업을 `tags.reduce_size`로 설명한다.
- 지원 모드 목록이 변경되면 장치는 `ReportSupportedModesChange()`를 호출해야 한다.

`HandleChangeToModeByCoreTag`의 `newMode`는 클러스터가 선택한 일치 모드로 미리 설정된다. 애플리케이션은 같은 태그를 가진 다른 지원 모드로 변경할 수 있다. 오류는 반환값이 아니라 `response.status`로 전달한다.

`Delegate`는 `AppDelegate`를 상속하며 다음 연결 기능을 추가한다.

- `SetInstance(Instance * aInstance)`
- 보호된 `const Instance * GetInstance() const`
- 보호된 `Instance * GetInstance()`
- 초기값이 `nullptr`인 `mInstance`

### ModeBaseCluster 구성

`chip::app::Clusters::ModeBaseCluster`는 `DefaultServerCluster`를 상속한다.

`Config`에는 다음 필드가 있다.

| 필드 | 타입 및 초기값 |
|---|---|
| `feature` | `BitMask<ModeBase::Feature>` |
| `optionalAttributeSet` | `OptionalAttributeSet` |
| `appDelegate` | `ModeBase::AppDelegate &` |
| `onOffValueForStartUp` | `bool`, 기본값 `false` |
| `diagnosticDataProvider` | `DeviceLayer::DiagnosticDataProvider &` |

`OptionalAttributeSet`은 `ModeBase::Attributes::StartUpMode::Id`를 대상으로 한다. 생성자는 전달받은 `ClusterEntry`의 `id`와 `revision`을 사용한다.

### 초기화와 시작 모드

`ModeBaseCluster::Startup()`은 다음 순서로 동작한다.

1. `DefaultServerCluster::Startup(context)`를 호출한다.
2. `GetModeValueByIndex(0, mCurrentMode)`로 첫 번째 모드를 초기 `CurrentMode`로 설정한다.
3. `LoadPersistentAttributes()`로 저장된 속성을 읽는다.
4. `StartUpMode`가 null이 아니면 부팅 원인을 확인한다.
   - `BootReasonType::kSoftwareUpdateCompleted`이면 `StartUpMode` 적용을 생략한다.
   - 그 외에는 필요할 때 `UpdateCurrentMode(mStartUpMode.Value())`를 호출한다.
   - 부팅 원인 조회 실패 시 OTA 재시작이 아닌 것으로 처리한다.
5. `mOnOffValueForStartUp`이 참이고 `OnMode`가 null이 아니면, 필요할 때 `CurrentMode`를 `OnMode`로 변경한다.

따라서 마지막 단계의 조건이 충족되면 `OnMode`가 앞서 설정한 모드보다 나중에 적용된다. 구현 주석에는 OTA 예외 처리가 현재 Matter OTA에 대해서만 동작한다는 TODO가 있다.

### 속성 접근과 영속 저장

`ReadAttribute()`는 다음 속성을 직접 처리한다.

- `ClusterRevision`
- `SupportedModes`
- `CurrentMode`
- `StartUpMode`
- `OnMode`
- `CoreModeTags`
- `FeatureMap`

그 외에는 `Status::UnsupportedAttribute`를 반환한다.

`WriteAttribute()`는 `StartUpMode`와 `OnMode`를 `DataModel::Nullable<uint8_t>`로 디코딩하여 갱신한다. 그 외에는 `Status::UnsupportedAttribute`를 반환한다.

`Attributes()`가 구성하는 속성 메타데이터의 조건은 다음과 같다.

| 속성 | 포함 조건 |
|---|---|
| `SupportedModes`, `CurrentMode` | 필수 메타데이터 |
| `StartUpMode` | `mOptionalAttributeSet.IsSet(StartUpMode::Id)` |
| `OnMode` | `mFeature.Has(Feature::kOnOff)` |
| `CoreModeTags` | `mFeature.Has(Feature::kCoreModes)` |

속성 갱신 함수는 다음 검증을 수행한다.

- `UpdateCurrentMode()`는 지원되는 모드만 허용한다.
- `UpdateStartUpMode()`와 `UpdateOnMode()`는 null 또는 지원되는 모드만 허용한다.
- 유효하지 않으면 `Status::ConstraintError`를 반환한다.
- 값이 변경되고 `mContext`가 있으면 `AttributePersistence::StoreNativeEndianValue()`로 저장한다.
- 저장 실패는 `LogErrorOnFailure`로 기록하며, 해당 실패만으로 반환값을 실패 상태로 바꾸지는 않는다.

`LoadPersistentAttributes()`는 `CurrentMode`를 읽고, 설정 조건에 따라 `StartUpMode`와 `OnMode`를 읽는다. 읽은 값은 각 갱신 함수를 통해 검증한다.

`ReportSupportedModesChange()`는 `NotifyAttributeChanged(SupportedModes::Id)`를 호출한다.

### 목록 인코딩과 검색

| 함수 | 동작 |
|---|---|
| `EncodeSupportedModes()` | 각 인덱스의 라벨, 모드 값, 태그를 받아 `ModeOptionStructType`으로 인코딩 |
| `EncodeCoreModeTags()` | `GetCoreModeTagByIndex()`가 제공하는 태그를 순서대로 인코딩 |
| `IsSupportedMode()` | 모드 값을 순회하여 일치 여부 확인 |
| `GetModeValueByModeTag()` | 지정한 태그를 가진 첫 번째 모드의 값 반환 |
| `IsSupportedCoreModeTag()` | 핵심 모드 태그 목록에 포함되는지 확인 |
| `ModeHasTag()` | 지정한 모드의 태그 목록에 해당 태그가 있는지 확인 |

라벨과 태그 버퍼에는 각각 다음 상수를 사용한다.

- `kMaxModeLabelSize = 64`
- `kMaxNumOfModeTags = 8`

`EncodeSupportedModes()`는 라벨 조회가 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환하면 정상 종료한다. `EncodeCoreModeTags()`도 같은 오류를 목록 종료로 처리한다.

### ChangeToMode 처리

`HandleChangeToMode()`의 흐름은 다음과 같다.

1. 요청 모드가 지원되지 않으면 `StatusCode::kUnsupportedMode`로 응답한다.
2. 요청 모드가 현재 모드와 같으면 delegate를 호출하지 않고 `StatusCode::kSuccess`로 응답한다.
3. 그 외에는 `mAppDelegate.HandleChangeToMode(newMode, response)`를 호출한다.
4. `response.status`가 `StatusCode::kSuccess`이면 `UpdateCurrentMode(newMode)`를 호출한다.
5. 갱신 실패 시 응답 상태를 `StatusCode::kGenericFailure`로 바꾼다.
6. `commandObj.AddResponse(commandPath, response)`로 응답한다.

### ChangeToModeByCoreTag 처리

`HandleChangeToModeByCoreTag()`의 흐름은 다음과 같다.

1. 요청 태그가 `CoreModeTags`에 없으면 `StatusCode::kUnsupportedMode`로 응답한다.
2. 현재 모드가 요청 태그를 가지고 있으면 현재 모드를 초기 후보로 선택한다.
3. 그렇지 않으면 `GetModeValueByModeTag()`로 첫 번째 일치 모드를 찾는다. 실패하면 `StatusCode::kGenericFailure`로 응답한다.
4. `mAppDelegate.HandleChangeToModeByCoreTag(newModeTag, newMode, response)`를 호출한다.
5. delegate가 성공을 반환하지 않으면 해당 응답을 그대로 보낸다.
6. 성공인 경우 선택된 모드가 지원되는지, 요청 태그를 포함하는지 다시 검증한다.
7. 검증 실패 또는 `UpdateCurrentMode()` 실패 시 `StatusCode::kGenericFailure`로 응답한다.

현재 모드가 이미 태그를 포함하더라도 delegate 호출은 수행한다.

`InvokeCommand()`는 `ChangeToMode`와 `ChangeToModeByCoreTag`를 디코딩하여 처리하며, 그 외에는 `Status::UnsupportedCommand`를 반환한다.

### 명령 목록과 예외

- `AcceptedCommands()`는 `MicrowaveOvenMode::Id`가 아닌 경우 `ChangeToMode`를 추가한다.
- `Feature::kCoreModes`가 설정되어 있으면 `ChangeToModeByCoreTag`를 추가한다.
- `GeneratedCommands()`는 `MicrowaveOvenMode::Id`가 아닌 경우 `ChangeToModeResponse`를 추가한다.

구현은 `MicrowaveOvenMode`를 `ChangeToMode`와 `ChangeToModeResponse`를 지원하지 않는 특별한 경우로 처리한다.

### Instance와 코드 생성 통합

`Instance::Init()`은 다음을 수행한다.

1. `emberAfFindServerCluster()`로 ZAP의 서버 클러스터를 확인한다. 없으면 `CHIP_ERROR_NOT_FOUND`를 반환한다.
2. `kAliasedClusters`에서 클러스터를 찾는다. 없으면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
3. `ThermostatMode::Id`이면 ZAP에 존재하는 `StartUpMode`를 선택 속성으로 설정한다.
4. 그 외 클러스터에서는 `StartUpMode`의 존재 및 `Feature::kCoreModes` 설정을 허용하지 않는다.
5. `OnOff` 관련 시작 값을 결정한다.
6. delegate가 없으면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
7. `mDelegate->SetInstance(this)`와 `mDelegate->Init()`을 호출한다.
8. `Config`를 구성하고 `mCluster.Create()`를 호출한다.
9. `RegisterThisInstance()`로 목록에 추가하고 `CodegenDataModelProvider::Instance().Registry().Register()`를 호출한다.

`MATTER_DM_PLUGIN_ON_OFF_SERVER`가 정의된 경우, `OnOff` 서버와 `StartUpOnOff`, `OnMode`, `Feature::kOnOff` 등의 조건을 확인한 뒤 `OnOffServer::Instance().getOnOffValueForStartUp()`으로 시작 값을 얻는다. 이 매크로가 정의되지 않은 경우 `Feature::kOnOff` 설정은 `CHIP_ERROR_INCORRECT_STATE`로 거부된다.

delegate는 `Instance`의 수명 동안 유효해야 한다. `Instance`의 속성 접근 및 모드 검색 래퍼는 내부 클러스터가 생성되었는지 `VerifyOrDie(mCluster.IsConstructed())`로 확인한다.

종료 동작은 다음과 같다.

- `Instance::~Instance()`는 `Shutdown()`을 호출한다.
- `Shutdown()`은 delegate의 `Instance` 포인터를 `nullptr`로 설정한다.
- 전역 목록에서 인스턴스를 제거한다.
- 내부 클러스터가 생성되어 있으면 레지스트리에서 등록 해제하고 `mCluster.Destroy()`를 호출한다.

`GetModeBaseInstanceList()`는 `IntrusiveList<Instance> &`를 반환한다. `GetFailTransition()`과 `ToggleFailTransition()`은 초기값이 `false`인 `mFailTransition`을 조회하거나 반전한다.

### 저장소 마이그레이션

`CodegenModeBaseCluster::Startup()`은 영속 저장 제공자를 사용할 수 있는 시점에 마이그레이션을 수행한다.

1. `GetSafeAttributePersistenceProvider()`로 이전 저장 제공자를 얻는다.
2. 제공자가 있으면 `MigrateModeBaseServerStorage()`를 호출한다.
3. 마이그레이션 오류는 기록한다.
4. 이어서 `ModeBaseCluster::Startup(context)`를 호출한다.

`MigrateModeBaseServerStorage()`의 대상은 다음과 같다.

- `Attributes::CurrentMode::Id`
- `Attributes::StartUpMode::Id`
- `Attributes::OnMode::Id`

각 항목은 `sizeof(uint8_t)`와 `isScalar = true`로 기술된다. `MaxAttrMigrationValueSize()`로 버퍼 크기를 정하고, `MigrateFromSafeToAttributePersistenceProvider()`로 이전한다.

### 원문 주석과 구현의 차이

- `AppDelegate::Init()` 주석은 `Instance` 검증 및 등록 후 호출된다고 설명하지만, 제공된 `Instance::Init()` 구현에서는 `mCluster.Create()`와 레지스트리 등록 전에 호출한다.
- `Instance` 소멸자 주석은 `Deinit()`을 언급하지만, 제공된 클래스에는 해당 함수 선언이 없으며 실제 소멸자는 `Shutdown()`을 호출한다.
- 스펙은 성공이 아닌 `ChangeToModeResponse`에 `StatusText`를 요구한다. 제공된 명령 처리 코드의 즉시 실패 분기에서는 `response.status`를 설정하지만 `StatusText`를 명시적으로 설정하지 않는다. 응답 타입의 기본 필드 상태는 제공된 조각에 정의되어 있지 않다.
- `LoadPersistentAttributes()`의 `CurrentMode` 읽기 실패 로그는 `Assuming zero.`라고 표시하지만, 실제 `Startup()`은 그보다 먼저 첫 번째 지원 모드로 `mCurrentMode`를 초기화한다.

## 관련 페이지

**파생 클러스터**

- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)
- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
