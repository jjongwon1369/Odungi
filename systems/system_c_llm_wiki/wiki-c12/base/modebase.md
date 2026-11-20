---
entity: ModeBase
ids: []
source_paths: ['data_model/1.7/clusters/ModeBase.xml', 'src/app/clusters/mode-base-server/AppDelegate.h', 'src/app/clusters/mode-base-server/CodegenIntegration.cpp', 'src/app/clusters/mode-base-server/CodegenIntegration.h', 'src/app/clusters/mode-base-server/Delegate.h', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp', 'src/app/clusters/mode-base-server/ModeBaseCluster.h', 'src/app/clusters/mode-base-server/mode-base-cluster-objects.h', 'src/app/clusters/mode-base-server/mode-base-server.h', 'src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# ModeBase

## 개요

`ModeBase`는 지원되는 모드 목록과 현재 모드를 관리하고, 모드 값 또는 코어 모드 태그를 사용한 전환을 제공하는 기반 클러스터이다.

- 스펙 이름: `Mode Base Cluster`
- revision: `3`
- 분류: hierarchy=`base`, role=`application`, scope=`Endpoint`
- PICS 코드: `MODB`
- 제공된 스펙에는 `Mode Base`의 숫자 클러스터 ID가 없다.
- 구현은 `ModeBaseCluster`에 공통 동작을 두고, `AppDelegate`에 애플리케이션별 모드 데이터와 전환 판단을 위임한다.
- 파생 클러스터의 ID와 revision은 `ClusterEntry`로 전달한다.

## 스펙

출처: `data_model/1.7/clusters/ModeBase.xml`

### revision 이력

| revision | 변경 내용 |
|---|---|
| `1` | 최초 정의 |
| `2` | `ChangeToModeResponse`의 `InvalidInMode` 상태에 `StatusText` 요구, 최소 하나의 표준 모드 태그 요구, 기반 및 파생 클러스터의 예약 범위 정의 |
| `3` | `CoreModeTags` 속성과 `ChangeToModeByCoreTag` 명령 추가 |

revision 이력에 언급된 예약 범위의 구체적인 값은 제공된 XML에 없다.

### 기능

| bit | code | name | 정의 |
|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존 관계. 선택 사항 |
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 코어 모드 지원. `otherwiseConform`에 `provisionalConform` 및 `optionalConform` 명시 |

### 데이터 형식

#### `ModeOptionStruct`

| 필드 ID | 이름 | 형식 | 요구 사항 |
|---|---|---|---|
| `0` | `Label` | `string` | 필수, 최대 길이 `64`, persistence=`fixed` |
| `1` | `Mode` | `uint8` | 필수, persistence=`fixed` |
| `2` | `ModeTags` | `list` of `ModeTagStruct` | 필수, 최대 `8`개, persistence=`fixed` |

#### `ModeTagStruct`

| 필드 ID | 이름 | 형식 | 요구 사항 |
|---|---|---|---|
| `0` | `MfgCode` | `vendor-id` | 선택 사항 |
| `1` | `Value` | `enum16` | 필수 |

### 속성

| ID | 이름 | 형식 | 접근 권한 | 적합성 및 제약 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `list` of `ModeOptionStruct` | 읽기: `view` | 필수, `2`~`255`개, persistence=`fixed` |
| `0x0001` | `CurrentMode` | `uint8` | 읽기: `view` | 필수, persistence=`nonVolatile` |
| `0x0002` | `StartUpMode` | `uint8` | 읽기: `view`, 쓰기: `operate` | 선택 사항, nullable, persistence=`nonVolatile`, default=`MS` |
| `0x0003` | `OnMode` | `uint8` | 읽기: `view`, 쓰기: `operate` | `DEPONOFF` 기능에 따라 필수, nullable, persistence=`nonVolatile` |
| `0x0004` | `CoreModeTags` | `list` of `enum16` | 읽기: `view` | `1`~`16`개, persistence=`fixed`; `otherwiseConform`에 `provisionalConform` 및 `COREMODES`에 따른 필수 조건 명시 |

`CurrentMode`, `StartUpMode`, `OnMode`의 추가 제약은 XML에서 빈 `desc`로만 제시된다.

### 명령

| ID | 이름 | 방향 | 응답 | 요구 사항 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `commandToServer` | `ChangeToModeResponse` | 필수, 호출 권한 `operate` |
| `0x01` | `ChangeToModeResponse` | `responseFromServer` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `commandToServer` | `ChangeToModeResponse` | `otherwiseConform`에 `provisionalConform` 및 `COREMODES`에 따른 필수 조건 명시 |

`ChangeToModeByCoreTag`의 호출 권한은 제공된 XML에 명시되어 있지 않다.

| 명령 | 필드 ID | 필드 | 형식 | 요구 사항 |
|---|---|---|---|---|
| `ChangeToMode` | `0` | `NewMode` | `uint8` | 필수 |
| `ChangeToModeResponse` | `0` | `Status` | `enum8` | 필수 |
| `ChangeToModeResponse` | `1` | `StatusText` | `string` | 최대 길이 `64`; `Status`가 `SUCCESS`이면 선택 사항, 그 외에는 필수 |
| `ChangeToModeByCoreTag` | `0` | `NewModeTag` | `enum16` | 필수 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml`

### 코드 생성 범위

SDK XML의 주석에 따르면 ZAP는 클러스터 ID가 없는 클러스터의 코드 생성을 지원하지 않는다. 따라서 공통 `StatusCode` 및 `ModeTag` 열거형 값은 `mode-base-cluster-objects.h`의 `ModeBase` 네임스페이스에서 정의하고, 파생 클러스터에도 각 값을 나열하거나 복사한다.

`ModeTagStruct`와 `ModeOptionStruct`는 활성 XML 정의이다. 반면 `Mode Base`의 클러스터, 속성 및 명령 블록은 전체가 주석 처리되어 있다.

### 구조체 정의

| 구조체 | 필드 | SDK 형식 | 제약 |
|---|---|---|---|
| `ModeTagStruct` | `MfgCode` | `vendor_id` | optional=`true`; 주석에서 deprecated로 표시 |
| `ModeTagStruct` | `Value` | `enum16` | optional=`false` |
| `ModeOptionStruct` | `Label` | `char_string` | length=`64`, optional=`false` |
| `ModeOptionStruct` | `Mode` | `int8u` | optional=`false` |
| `ModeOptionStruct` | `ModeTags` | `ModeTagStruct` | array=`true`, length=`8`, optional=`false` |

두 구조체에는 다음 클러스터 코드가 실제 요소로 연결되어 있다.

- `0x0051`
- `0x0052`
- `0x0054`
- `0x0055`
- `0x0059`
- `0x005E`
- `0x009E`

그 외 일부 파생 클러스터는 이름 주석만 있으며 코드 요소는 없다.

### 스펙과 구분할 사항

- `MfgCode`는 스펙에서 선택 필드이며, SDK XML에서는 deprecated 주석이 추가되어 있다.
- 주석 처리된 클러스터 블록에는 `0xFFFD` 값 `2`가 남아 있으나, 제공된 스펙 revision은 `3`이다.
- 주석 처리된 `ChangeToModeResponse` 정의는 `StatusText`를 optional=`true`로 표시한다. 스펙의 상태별 필수 조건과 구분해야 한다.
- SDK XML에는 `CoreModeTags` 및 `ChangeToModeByCoreTag` 정의가 없다. 구현에서는 `ThermostatMode`의 정의를 재사용한다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/mode-base-server/AppDelegate.h` | 애플리케이션별 모드 데이터 및 전환 인터페이스 |
| `src/app/clusters/mode-base-server/Delegate.h` | `AppDelegate` 확장 및 `Instance` 연결 |
| `src/app/clusters/mode-base-server/ModeBaseCluster.h` | `ModeBaseCluster`, `Config`, 속성 및 명령 처리 API 선언 |
| `src/app/clusters/mode-base-server/ModeBaseCluster.cpp` | 시작 처리, 속성 접근, 모드 검색, 명령 처리 및 영속화 |
| `src/app/clusters/mode-base-server/CodegenIntegration.h` | `CodegenModeBaseCluster`, `Instance`, 인스턴스 목록 API 선언 |
| `src/app/clusters/mode-base-server/CodegenIntegration.cpp` | ZAP 구성 검증, 클러스터 생성·등록·종료 및 저장소 마이그레이션 연결 |
| `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h` | `MigrateModeBaseServerStorage` 선언 |
| `src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp` | 영속 속성 마이그레이션 |
| `src/app/clusters/mode-base-server/mode-base-cluster-objects.h` | 파생 클러스터 항목, 별칭, 속성 메타데이터 및 열거형 |
| `src/app/clusters/mode-base-server/mode-base-server.h` | `app/clusters/mode-base-server/CodegenIntegration.h` 포함 |

### 공통 정의와 파생 클러스터

`ClusterEntry`는 `ClusterId id`와 `uint32_t revision`으로 구성된다. `kAliasedClusters`에는 다음 11개 항목이 포함된다.

| 항목 | 클러스터 ID 참조 |
|---|---|
| `kDeviceEnergyManagementMode` | `DeviceEnergyManagementMode::Id` |
| `kDishwasherMode` | `DishwasherMode::Id` |
| `kEnergyEvseMode` | `EnergyEvseMode::Id` |
| `kLaundryWasherMode` | `LaundryWasherMode::Id` |
| `kMicrowaveOvenMode` | `MicrowaveOvenMode::Id` |
| `kOvenMode` | `OvenMode::Id` |
| `kRefrigeratorAndTemperatureControlledCabinetMode` | `RefrigeratorAndTemperatureControlledCabinetMode::Id` |
| `kRvcCleanMode` | `RvcCleanMode::Id` |
| `kRvcRunMode` | `RvcRunMode::Id` |
| `kThermostatMode` | `ThermostatMode::Id` |
| `kWaterHeaterMode` | `WaterHeaterMode::Id` |

각 항목의 revision은 해당 파생 클러스터의 `kRevision`을 사용한다.

공통 정의의 재사용 관계는 다음과 같다.

- `Commands`는 `ThermostatMode::Commands`의 별칭이다.
- `SupportedModes`와 `CurrentMode`는 `DeviceEnergyManagementMode::Attributes`의 정의를 재사용한다.
- `CoreModeTags`는 `ThermostatMode::Attributes::CoreModeTags`의 별칭이다.
- `GeneratedCommandList`, `AcceptedCommandList`, `AttributeList`, `FeatureMap`, `ClusterRevision`은 `DeviceEnergyManagementMode::Attributes`의 정의를 재사용한다.
- `StartUpMode::Id`는 `0x00000002`, `OnMode::Id`는 `0x00000003`으로 직접 정의한다.
- `StartUpMode`와 `OnMode`의 `TypeInfo`는 `DataModel::Nullable<uint8_t>`를 사용하고, `MustUseTimedWrite()`는 `false`를 반환한다.
- `kMandatoryMetadata`에는 `SupportedModes`와 `CurrentMode`가 포함된다.

### 열거형

#### `ModeTag`

| 이름 | 값 |
|---|---|
| `kAuto` | `0x0` |
| `kQuick` | `0x1` |
| `kQuiet` | `0x2` |
| `kLowNoise` | `0x3` |
| `kLowEnergy` | `0x4` |
| `kVacation` | `0x5` |
| `kMin` | `0x6` |
| `kMax` | `0x7` |
| `kNight` | `0x8` |
| `kDay` | `0x9` |

#### `StatusCode`

| 이름 | 값 |
|---|---|
| `kSuccess` | `0x0` |
| `kUnsupportedMode` | `0x1` |
| `kGenericFailure` | `0x2` |
| `kInvalidInMode` | `0x3` |

#### `Feature`

| 이름 | 정의 |
|---|---|
| `kOnOff` | `0x1` |
| `kCoreModes` | `to_underlying(ThermostatMode::Feature::kCoreModes)` |

### `AppDelegate`와 `Delegate`

`AppDelegate`는 `chip::app::Clusters::ModeBase`에 정의되며 다음 인터페이스를 제공한다.

| 함수 | 계약 |
|---|---|
| `Init()` | 애플리케이션 로직 초기화. 순수 가상 함수 |
| `GetModeLabelByIndex()` | 인덱스로 모드의 라벨 제공 |
| `GetModeValueByIndex()` | 인덱스로 모드 값 제공 |
| `GetModeTagsByIndex()` | 인덱스로 모드 태그 목록 제공 |
| `HandleChangeToMode()` | 모드 전환 수락 여부와 `ChangeToModeResponse` 결정 |
| `GetCoreModeTagByIndex()` | 코어 모드 태그 제공. 기본 구현은 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED` 반환 |
| `HandleChangeToModeByCoreTag()` | 태그에 맞는 전환 모드 선택 및 응답 결정. 기본 구현은 `HandleChangeToMode(newMode, response)` 호출 |

목록 제공 함수의 계약:

- 인덱스는 `0`부터 시작하며 중간에 빈 인덱스가 없어야 한다.
- 정상 반환은 `CHIP_NO_ERROR`, 목록 끝은 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`로 표시한다.
- 라벨 복사에는 `CopyCharSpanToMutableCharSpan` 사용을 안내한다.
- 태그 버퍼를 채운 뒤 실제 초기화된 항목 수로 목록 크기를 줄여야 한다.
- 지원 모드 목록을 변경하면 `Instance`의 `ReportSupportedModesChange()`를 호출해야 한다.

`HandleChangeToModeByCoreTag()`의 `newMode`는 입출력 매개변수이다. 클러스터가 태그와 일치하는 지원 모드를 미리 넣고, delegate는 같은 태그에 해당하는 다른 지원 모드로 변경할 수 있다.

`Delegate`는 `AppDelegate`를 상속하며 다음을 추가한다.

- `SetInstance()`로 연결된 `Instance` 포인터 설정
- protected `GetInstance()`의 const 및 non-const 오버로드
- 초기 `mInstance` 값은 `nullptr`

### `Instance` 초기화와 종료

`Instance` 생성자는 `Delegate *`, `EndpointId`, `ClusterId`, 기능 비트마스크를 받는다. delegate는 `Instance`의 전체 수명 동안 유효해야 하고, endpoint는 ZAP 구성과 일치해야 한다.

`Instance::Init()`의 처리 순서는 다음과 같다.

1. `emberAfFindServerCluster()`로 서버 클러스터를 찾는다. 없으면 `CHIP_ERROR_NOT_FOUND`를 반환한다.
2. `kAliasedClusters`에서 ID를 찾는다. 없으면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
3. 파생 클러스터별 구성을 검증한다.
   - `ThermostatMode::Id`이면 `StartUpMode`의 존재 여부를 `mOptionalAttributeSet`에 반영한다.
   - 나머지는 `StartUpMode`가 존재하거나 `ModeBase::Feature::kCoreModes`가 설정되면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
4. `MATTER_DM_PLUGIN_ON_OFF_SERVER` 구성에 따라 시작 시 `OnOff` 상태를 계산한다.
   - `OnOff` 서버, `StartUpOnOff`, `OnMode`, `ModeBase::Feature::kOnOff`를 확인한다.
   - `StartUpOnOff`가 알려진 volatile 속성이 아니고 `getOnOffValueForStartUp()`가 성공하면 결과를 사용한다.
   - 플러그인이 없는 빌드에서는 `ModeBase::Feature::kOnOff`가 설정되어 있으면 오류를 반환한다.
5. delegate가 유효한지 검사하고 `SetInstance(this)` 및 `Init()`을 호출한다.
6. `ModeBaseCluster::Config`를 구성하고 `mCluster.Create()`를 호출한다.
7. 인스턴스 목록에 추가하고 `CodegenDataModelProvider::Instance().Registry().Register()`로 등록한다.

`Config`에는 `feature`, `optionalAttributeSet`, `appDelegate`, `onOffValueForStartUp`, `diagnosticDataProvider`가 들어간다.

`GetModeBaseInstanceList()`는 초기화된 인스턴스를 관리하는 `IntrusiveList<Instance>`의 수정 가능한 참조를 반환한다.

`Shutdown()`은 delegate의 연결을 해제하고 목록에서 인스턴스를 제거한다. 클러스터가 생성되어 있으면 등록을 해제하고 `mCluster.Destroy()`를 호출한다. 소멸자는 `Shutdown()`을 호출한다.

> `AppDelegate::Init()`의 주석은 등록 이후 호출을 설명하지만, 제공된 `Instance::Init()`의 실제 호출은 클러스터 생성·등록보다 앞선다. 또한 `Instance` 소멸자 주석은 `Deinit()`을 언급하지만, 제공된 선언과 구현에는 `Shutdown()`이 사용된다.

### 시작 시 모드 결정

`ModeBaseCluster::Startup()`은 다음 순서로 실행된다.

1. `DefaultServerCluster::Startup()` 호출
2. `GetModeValueByIndex(0, mCurrentMode)`로 첫 번째 지원 모드를 초기값으로 설정
3. `LoadPersistentAttributes()`로 저장된 속성 복원
4. `StartUpMode`가 null이 아니면 부팅 이유 확인
   - `BootReasonType::kSoftwareUpdateCompleted`이면 `StartUpMode` 적용 생략
   - 그 외에는 `UpdateCurrentMode()`로 적용
   - 부팅 이유 조회 실패 시 `BootReasonType::kUnspecified`로 처리
5. `mOnOffValueForStartUp`이 참이고 `OnMode`가 null이 아니면 `OnMode` 적용

두 시작 조건이 모두 적용되는 경우 코드상 `OnMode` 처리가 뒤에 실행된다. 시작 모드 적용 실패는 `StatusIB(status).ToChipError()`로 반환한다.

코드에는 OTA 예외 처리가 현재 Matter OTA에 대해서만 동작하며 일반 OTA에도 적용되어야 한다는 TODO가 있다.

### 속성 접근 및 영속화

| 함수 | 동작 |
|---|---|
| `UpdateCurrentMode()` | 지원 모드인지 검사. 유효하지 않으면 `Status::ConstraintError` |
| `UpdateStartUpMode()` | null 또는 지원 모드 허용 |
| `UpdateOnMode()` | null 또는 지원 모드 허용 |
| `GetCurrentMode()` | 현재 모드 반환 |
| `GetStartUpMode()` | 시작 모드 반환 |
| `GetOnMode()` | `OnMode` 반환 |
| `ReportSupportedModesChange()` | `NotifyAttributeChanged(SupportedModes::Id)` 호출 |

갱신 함수는 `SetAttributeValue()`로 변경을 반영하고, 값이 바뀌었으며 `mContext`가 있으면 `StoreNativeEndianValue()`로 저장한다. 저장 오류는 `LogErrorOnFailure`로 기록하며, 그 오류를 반환 상태로 전달하지는 않는다.

`LoadPersistentAttributes()`는 다음을 복원한다.

- `CurrentMode`
- `mOptionalAttributeSet`에 포함된 경우의 `StartUpMode`
- `Feature::kOnOff`가 설정된 경우의 `OnMode`

복원된 값도 각각의 갱신 함수로 검증한다. `CurrentMode` 로드 실패 로그에는 zero를 가정한다는 문구가 있지만, 시작 코드에서 설정한 값은 첫 번째 지원 모드이다.

`ReadAttribute()`는 `ClusterRevision`, `SupportedModes`, `CurrentMode`, `StartUpMode`, `OnMode`, `CoreModeTags`, `FeatureMap`을 처리한다. `WriteAttribute()`는 `StartUpMode`와 `OnMode`만 처리한다. 그 외에는 `Status::UnsupportedAttribute`를 반환한다.

`Attributes()`는 필수 속성에 다음 조건부 속성을 추가한다.

- `StartUpMode`: `mOptionalAttributeSet`에 포함된 경우
- `OnMode`: `Feature::kOnOff`가 설정된 경우
- `CoreModeTags`: `Feature::kCoreModes`가 설정된 경우

### 목록 인코딩과 모드 검색

- `EncodeSupportedModes()`는 각 인덱스의 라벨, 값, 태그를 받아 인코딩한다.
  - 라벨 버퍼: `kMaxModeLabelSize = 64`
  - 태그 버퍼: `kMaxNumOfModeTags = 8`
  - `GetModeLabelByIndex()`의 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 목록 종료로 처리한다.
- `EncodeCoreModeTags()`는 `GetCoreModeTagByIndex()`가 목록 종료를 반환할 때까지 인코딩한다.
- `IsSupportedMode()`는 모드 값을 순회해 일치 여부를 확인한다.
- `GetModeValueByModeTag()`는 태그 값이 일치하는 첫 번째 모드의 값을 반환한다. 찾지 못하면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.
- `IsSupportedCoreModeTag()`는 코어 모드 태그 목록에서 일치 여부를 확인한다.
- `ModeHasTag()`는 특정 모드의 태그 목록에 지정된 태그가 있는지 확인한다.

제공된 `GetModeValueByModeTag()`와 `ModeHasTag()`는 태그의 `value`를 비교하며 `MfgCode`는 비교하지 않는다.

### 명령 처리

`InvokeCommand()`는 `ChangeToMode`와 `ChangeToModeByCoreTag`를 디코딩해 해당 처리 함수로 전달한다. 그 외에는 `Status::UnsupportedCommand`를 반환한다.

#### `ChangeToMode`

`ModeBaseCluster::HandleChangeToMode()`의 흐름:

1. `NewMode`가 지원되지 않으면 `StatusCode::kUnsupportedMode`로 응답한다.
2. 현재 모드와 같으면 delegate 호출 없이 `StatusCode::kSuccess`로 응답한다.
3. 그 외에는 `mAppDelegate.HandleChangeToMode()`를 호출한다.
4. delegate의 `response.status`가 성공이면 `UpdateCurrentMode()`를 호출한다.
5. 갱신 실패 시 `StatusCode::kGenericFailure`로 바꾼다.
6. `AddResponse()`로 `ChangeToModeResponse`를 반환한다.

delegate가 실패 상태를 반환하면 `CurrentMode`는 변경하지 않는다.

#### `ChangeToModeByCoreTag`

`ModeBaseCluster::HandleChangeToModeByCoreTag()`의 흐름:

1. `NewModeTag`가 `CoreModeTags`에 없으면 `StatusCode::kUnsupportedMode`로 응답한다.
2. 현재 모드에 태그가 있으면 현재 모드를 초기 후보로 선택한다.
3. 없으면 `GetModeValueByModeTag()`로 첫 번째 일치 모드를 찾는다. 실패 시 `StatusCode::kGenericFailure`로 응답한다.
4. `mAppDelegate.HandleChangeToModeByCoreTag()`를 호출해 후보 모드와 응답을 결정한다.
5. delegate가 성공을 반환하면 후보가 지원 모드이고 요청 태그를 포함하는지 다시 검증한다.
6. 검증 실패 또는 모드 갱신 실패 시 `StatusCode::kGenericFailure`로 응답한다.
7. 후보가 현재 모드와 같으면 값을 변경하지 않고 응답한다.

`ChangeToMode`와 달리, 초기 후보가 현재 모드여도 delegate를 호출한다.

#### 명령 목록의 예외

- `AcceptedCommands()`는 `MicrowaveOvenMode::Id`에 대해 `ChangeToMode`를 추가하지 않는다.
- `Feature::kCoreModes`가 설정되면 `ChangeToModeByCoreTag`를 추가한다.
- `GeneratedCommands()`는 `MicrowaveOvenMode::Id`에 대해 `ChangeToModeResponse`를 추가하지 않는다.

### 저장소 마이그레이션

`CodegenModeBaseCluster::Startup()`은 영속성 제공자를 사용할 수 있는 시작 시점에 마이그레이션을 수행한다.

1. `GetSafeAttributePersistenceProvider()`로 기존 제공자를 가져온다.
2. 제공자가 있으면 `MigrateModeBaseServerStorage()`를 호출한다.
3. 마이그레이션 오류는 기록한다.
4. 이후 `ModeBaseCluster::Startup()`을 호출한다.

`MigrateModeBaseServerStorage()`의 대상은 다음 세 속성이다.

- `Attributes::CurrentMode::Id`
- `Attributes::StartUpMode::Id`
- `Attributes::OnMode::Id`

각 항목은 `sizeof(uint8_t)`와 `isScalar = true`로 등록된다. `MaxAttrMigrationValueSize()`로 버퍼 크기를 계산하고, `MigrateFromSafeToAttributePersistenceProvider()`를 통해 `SafeAttributePersistenceProvider`에서 `AttributePersistenceProvider`로 이전한다.

## 관련 페이지

**파생 클러스터**

- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)
- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [RVC Run Mode `0x0054`](../clusters/0x0054-rvc-run-mode.md)
- [RVC Clean Mode `0x0055`](../clusters/0x0055-rvc-clean-mode.md)
- [Dishwasher Mode `0x0059`](../clusters/0x0059-dishwasher-mode.md)
- [Microwave Oven Mode `0x005E`](../clusters/0x005E-microwave-oven-mode.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
- [Water Heater Mode `0x009E`](../clusters/0x009E-water-heater-mode.md)
