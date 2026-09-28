---
entity: Temperature Control
ids: ['0x0056']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.h', 'src/app/clusters/temperature-control-server/temperature-control-server.h', 'src/app/clusters/temperature-control-server/CodegenIntegration.h', 'src/app/clusters/temperature-control-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp', 'src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h', 'data_model/1.7/clusters/TemperatureControl.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Temperature Control

## 개요

Temperature Control은 온도 제어 설정과 온도 보고를 위한 속성 및 명령을 제공한다. 실제 온도 수치를 사용하는 `TemperatureNumber`, 온도 레벨을 사용하는 `TemperatureLevel`, 온도 수치의 단계 제어를 위한 `TemperatureStep` 기능을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0056` |
| 스펙 이름 | Temperature Control Cluster |
| 클러스터 이름 | Temperature Control |
| Revision | `1` |
| SDK 정의 | `TEMPERATURE_CONTROL_CLUSTER` |
| SDK 도메인 | `Appliances` |
| PICS 코드 | `TCTL` |
| 분류 | hierarchy=`base`, role=`application`, scope=`Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/TemperatureControl.xml`

### 기능

| bit | code | 이름 | 설명 | 적합성 조건 |
|---|---|---|---|---|
| `0` | `TN` | `TemperatureNumber` | 실제 온도 수치 사용 | `optionalConform choice="a"` |
| `1` | `TL` | `TemperatureLevel` | 온도 레벨 사용 | `optionalConform choice="a"` |
| `2` | `STEP` | `TemperatureStep` | 온도 수치에 단계 제어 사용 | `TN` 조건의 `optionalConform` |

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 필수 조건 | 제약 | persistence |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureSetpoint` | `temperature` | `TN` | `MinTemperature` 이상, `MaxTemperature` 이하 | — |
| `0x0001` | `MinTemperature` | `temperature` | `TN` | `MaxTemperature - 1` 이하 | `fixed` |
| `0x0002` | `MaxTemperature` | `temperature` | `TN` | `<desc/>`만 제공됨 | `fixed` |
| `0x0003` | `Step` | `temperature` | `STEP` | `1` 이상, `MaxTemperature - MinTemperature` 이하 | `fixed` |
| `0x0004` | `SelectedTemperatureLevel` | `uint8` | `TL` | 최대 `31` | — |
| `0x0005` | `SupportedTemperatureLevels` | `list` | `TL` | 최대 `32`개 항목 | — |

`SupportedTemperatureLevels`의 항목 타입은 `string`이며, 각 항목의 `maxLength`는 `16`이다.

### 명령

| ID | 이름 | 방향 | 호출 권한 | 적합성 | response |
|---|---|---|---|---|---|
| `0x00` | `SetTemperature` | `commandToServer` | `operate` | 필수 | `Y` |

| 필드 ID | 이름 | 타입 | 필수 조건 | 제약 |
|---|---|---|---|---|
| `0` | `TargetTemperature` | `temperature` | `TN` | `<desc/>`만 제공됨 |
| `1` | `TargetTemperatureLevel` | `uint8` | `TL` | `<desc/>`만 제공됨 |

제공된 스펙 XML에는 `<desc/>`에 해당하는 상세 제약 설명이 포함되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml`

이 파일은 Alchemy로 생성되었으며 `DO NOT EDIT`로 표시되어 있다.

- 생성 원본: `src/app_clusters/TemperatureControl.adoc`
- Parameters: `in-progress`
- Git: `0.7-summer-2025-253-gd51479a48`
- `client`와 `server` 모두 활성화되어 있으며 각각 `tick="false"`, `init="false"`이다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="1"`로 정의된다.
- 기능의 bit, code, 이름 및 적합성 조건은 스펙 입력과 동일하다.

### 속성 정의

모든 속성은 `side="server"`, `optional="true"`로 선언되며, 기능별 `mandatoryConform`을 함께 가진다.

| code | name | define | type | 필수 조건 | 추가 설정 |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureSetpoint` | `TEMP_SETPOINT` | `temperature` | `TN` | — |
| `0x0001` | `MinTemperature` | `MIN_TEMP` | `temperature` | `TN` | — |
| `0x0002` | `MaxTemperature` | `MAX_TEMP` | `temperature` | `TN` | — |
| `0x0003` | `Step` | `STEP` | `temperature` | `STEP` | — |
| `0x0004` | `SelectedTemperatureLevel` | `SELECTED_TEMP_LEVEL` | `int8u` | `TL` | `max="31"` |
| `0x0005` | `SupportedTemperatureLevels` | `SUPPORTED_TEMP_LEVELS` | `array` | `TL` | `entryType="char_string"`, `length="32"` |

스펙의 `SupportedTemperatureLevels` 항목에는 `maxLength="16"`이 있지만, 제공된 SDK XML에는 이에 대응하는 항목별 길이 제약이 명시되어 있지 않다.

### 명령 정의

`SetTemperature`는 `source="client"`, `code="0x00"`, `optional="false"`로 선언된다.

| id | name | type | optional |
|---|---|---|---|
| `0` | `TargetTemperature` | `temperature` | `true` |
| `1` | `TargetTemperatureLevel` | `int8u` | `true` |

SDK XML에서는 두 인자를 선택적으로 선언한다. 기능에 따른 인자 존재 여부는 구현의 `HandleSetTemperature`에서 검사한다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/temperature-control-server/TemperatureControlCluster.h` | `TemperatureControlCluster`, `StartupConfiguration` 및 공개 API 선언 |
| `src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp` | 초기 구성 검증, 속성 읽기·갱신, 명령 처리 |
| `src/app/clusters/temperature-control-server/CodegenIntegration.h` | endpoint 기반 조회·갱신 및 delegate API 선언 |
| `src/app/clusters/temperature-control-server/CodegenIntegration.cpp` | 서버 등록·해제, 기본값 로드, API 연결 |
| `src/app/clusters/temperature-control-server/temperature-control-server.h` | `app/clusters/temperature-control-server/CodegenIntegration.h` 포함 |
| `src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h` | `SupportedTemperatureLevelsIteratorDelegate` 정의 |

### 클래스와 초기 구성

`chip::app::Clusters`의 `TemperatureControlCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 `EndpointId`, `BitFlags<TemperatureControl::Feature>`, `StartupConfiguration`을 받는다.

`StartupConfiguration`의 모든 필드는 `{}`로 초기화된다.

| 필드 | 타입 |
|---|---|
| `temperatureSetpoint` | `int16_t` |
| `minTemperature` | `int16_t` |
| `maxTemperature` | `int16_t` |
| `step` | `int16_t` |
| `selectedTemperatureLevel` | `uint8_t` |

구현에서 정의하는 상수는 다음과 같다.

| 이름 | 값 |
|---|---|
| `kMinTemperatureRange` | `-27315` |
| `kMaxTemperatureRange` | `32766` |
| `kMinStep` | `1` |
| `kMaxSelectedTemperatureLevel` | `31` |
| `kMaxTemperatureLevelStringSize` | `32` |

생성자는 다음 조건을 `VerifyOrDie`로 검증한다.

- `Feature::kTemperatureNumber` 사용 시:
  - `Feature::kTemperatureLevel`을 동시에 사용하지 않는다.
  - `mMinTemperature`는 `kMinTemperatureRange` 이상, `kMaxTemperatureRange` 이하이다.
  - `mMaxTemperature >= mMinTemperature + 1`이다.
  - `mTemperatureSetpoint`는 `mMinTemperature` 이상, `mMaxTemperature` 이하이다.
  - `Feature::kTemperatureStep`도 사용하면 `mStep`은 `kMinStep` 이상, `mMaxTemperature - mMinTemperature` 이하이다.
- `Feature::kTemperatureLevel` 사용 시:
  - `mSelectedTemperatureLevel <= kMaxSelectedTemperatureLevel`이다.

`mFeatures`, `mMinTemperature`, `mMaxTemperature`, `mStep`은 `const` 멤버이다. `mDelegate`는 모든 인스턴스가 공유하는 정적 포인터이며 초기값은 `nullptr`이다.

### 속성 목록과 읽기

`Attributes`는 `AttributeListBuilder`로 `kMandatoryMetadata`와 기능별 속성을 추가한다.

| 기능 | 추가 속성 |
|---|---|
| `Feature::kTemperatureNumber` | `TemperatureSetpoint`, `MinTemperature`, `MaxTemperature` |
| `Feature::kTemperatureStep` | `Step` |
| `Feature::kTemperatureLevel` | `SelectedTemperatureLevel`, `SupportedTemperatureLevels` |

`ReadAttribute`의 동작은 다음과 같다.

- `ClusterRevision`: `TemperatureControl::kRevision`을 인코딩한다.
- `FeatureMap`: `mFeatures`를 인코딩한다.
- 수치 및 선택 레벨 속성: 해당 멤버 값을 인코딩한다.
- `SupportedTemperatureLevels`:
  - `mDelegate == nullptr`이면 `EncodeEmptyList`를 호출한다.
  - 그 외에는 `Reset(request.path.mEndpointId)` 후 `Next`로 항목을 순회한다.
  - 항목 버퍼는 `char buffer[kMaxTemperatureLevelStringSize]`이다.
  - `Next`가 `CHIP_NO_ERROR`를 반환하는 동안 항목을 인코딩한다.
  - `Next`가 다른 값을 반환하면 순회를 종료한다. 항목 인코딩 오류는 반환하지만, `Next`의 종료 값 자체는 반환하지 않는다.
- 지원하지 않는 속성은 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

### 속성 갱신 API

#### `SetTemperatureSetpoint`

검사 순서는 다음과 같다.

1. `Feature::kTemperatureNumber`가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`.
2. 입력값이 `mMinTemperature`부터 `mMaxTemperature`까지의 범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`.
3. `Feature::kTemperatureStep` 사용 시 `(temperatureSetpoint - mMinTemperature) % mStep == 0`을 만족하지 않으면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`.
4. `SetAttributeValue`로 `mTemperatureSetpoint`를 갱신하고 `CHIP_NO_ERROR`를 반환한다.

#### `SetSelectedTemperatureLevel`

검사 및 처리 순서는 다음과 같다.

1. `Feature::kTemperatureLevel`이 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`.
2. `mDelegate == nullptr`이면 `CHIP_IM_GLOBAL_STATUS(NotFound)`.
3. `selectedTemperatureLevel < mDelegate->Size()`를 만족하지 않으면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`.
4. `mDelegate->Reset(mPath.mEndpointId)`를 호출한다.
5. `SetAttributeValue`로 `mSelectedTemperatureLevel`을 갱신하고 `CHIP_NO_ERROR`를 반환한다.

이 함수에서는 `Size` 검사가 `Reset`보다 먼저 실행되며, `31` 상한을 별도로 검사하지 않는다.

조회 API는 `GetTemperatureSetpoint`, `GetSelectedTemperatureLevel`, `GetStep`, `GetMinTemperature`, `GetMaxTemperature`이다.

### 명령 처리

`AcceptedCommands`는 `Commands::SetTemperature::kMetadataEntry`를 추가한다.

`InvokeCommand`는 `Commands::SetTemperature::Id`에 대해 `Commands::SetTemperature::DecodableType`으로 입력을 디코딩하고 `HandleSetTemperature`를 호출한다. 다른 명령 ID에는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

| 기능 | 필수 입력 | 갱신 함수 |
|---|---|---|
| `Feature::kTemperatureNumber` | `targetTemperature` | `SetTemperatureSetpoint` |
| `Feature::kTemperatureLevel` | `targetTemperatureLevel` | `SetSelectedTemperatureLevel` |

`HandleSetTemperature`는 다음 상태를 반환한다.

| 조건 | 상태 |
|---|---|
| 기능에 필요한 입력이 없음 | `Status::InvalidCommand` |
| 갱신 함수가 `CHIP_IM_GLOBAL_STATUS(ConstraintError)` 반환 | `Status::ConstraintError` |
| `SetSelectedTemperatureLevel`이 `CHIP_IM_GLOBAL_STATUS(NotFound)` 반환 | `Status::NotFound` |
| 그 밖의 갱신 오류 | `Status::InvalidInState` |
| 처리 완료 | `Status::Success` |

### 온도 레벨 delegate

`SupportedTemperatureLevelsIteratorDelegate`는 `chip::app::Clusters::TemperatureControl`에 정의된다.

| API | 동작 |
|---|---|
| `Reset(EndpointId endpoint)` | `mEndpoint`를 설정하고 `mIndex`를 `0`으로 초기화 |
| `Size()` | `SupportedTemperatureLevels` 목록의 전체 크기를 반환하는 순수 가상 함수. 반환 타입은 `uint8_t` |
| `Next(MutableCharSpan & item)` | 다음 항목을 제공하는 순수 가상 함수. 반환 타입은 `CHIP_ERROR` |

`TemperatureControlCluster::GetDelegate`와 `TemperatureControlCluster::SetDelegate`는 정적 `mDelegate`에 접근한다.

### Codegen 통합

`CodegenIntegration.cpp`는 다음 크기의 `gServers` 배열을 유지한다.

- `kTemperatureControlFixedClusterCount`: `TemperatureControl::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kTemperatureControlMaxClusterCount`: `kTemperatureControlFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- 배열 요소 타입: `LazyRegisteredServerCluster<TemperatureControlCluster>`

`IntegrationDelegate::CreateRegistration`은 다음을 수행한다.

1. `optionalAttributeBits`로 `app::OptionalAttributeSet`을 구성하고 `featureMap`으로 `BitFlags<Feature>`를 구성한다.
2. 활성 기능에 필요한 속성의 존재 여부를 `VerifyOrDie`로 검사한다.
3. `GetDefault`를 통해 초기값을 읽고 `Status::Success` 여부를 검사한다.
   - `Feature::kTemperatureNumber`: `TemperatureSetpoint`, `MinTemperature`, `MaxTemperature`
   - 위 기능과 함께 `Feature::kTemperatureStep` 사용 시: `Step`
   - `Feature::kTemperatureLevel`: `SelectedTemperatureLevel`
   - `SupportedTemperatureLevels`는 존재 여부만 검사한다.
4. `StartupConfiguration`으로 클러스터를 생성하고 `Registration`을 반환한다.

`FindRegistration`은 인스턴스가 생성되지 않았으면 `nullptr`을 반환한다. `ReleaseRegistration`은 `Destroy`를 호출한다.

| 콜백 | 동작 |
|---|---|
| `MatterTemperatureControlClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`과 `fetchOptionalAttributes`는 `true` |
| `MatterTemperatureControlClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 및 `shutdownType` 전달 |
| `MatterTemperatureControlPluginServerInitCallback` | 빈 구현 |

`chip::app::Clusters::TemperatureControl`의 통합 API는 다음과 같다.

- `FindClusterOnEndpoint`: endpoint의 클러스터를 조회한다.
- `SetTemperatureSetpoint`: 조회한 인스턴스의 동명 함수를 호출한다.
- `SetSelectedTemperatureLevel`: 조회한 인스턴스의 동명 함수를 호출한다.
- 두 갱신 API는 클러스터를 찾지 못하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
- `GetDelegate`와 `SetDelegate`는 `TemperatureControlCluster`의 동명 정적 함수로 위임한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
