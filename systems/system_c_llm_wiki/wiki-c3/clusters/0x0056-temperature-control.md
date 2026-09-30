---
entity: Temperature Control
ids: ['0x0056']
source_paths: ['data_model/1.7/clusters/TemperatureControl.xml', 'src/app/clusters/temperature-control-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-control-server/CodegenIntegration.h', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.h', 'src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h', 'src/app/clusters/temperature-control-server/temperature-control-server.h', 'src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Temperature Control

## 개요

Temperature Control은 온도 제어 설정과 온도 보고를 위한 속성 및 명령을 제공한다. 실제 온도 값을 사용하는 `TemperatureNumber`, 온도 레벨을 사용하는 `TemperatureLevel`, 온도 값의 단계 제어를 지원하는 `TemperatureStep` 기능을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Temperature Control` |
| 스펙 이름 | `Temperature Control Cluster` |
| 클러스터 ID | `0x0056` |
| Revision | `1` |
| SDK 도메인 | `Appliances` |
| PICS 코드 | `TCTL` |
| 분류 | hierarchy=`base`, role=`application`, scope=`Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/TemperatureControl.xml`

Revision `1`의 이력은 `Initial revision`이다.

### 기능

| Bit | 코드 | 이름 | 설명 | 적합성 조건 |
|---|---|---|---|---|
| `0` | `TN` | `TemperatureNumber` | 실제 온도 값 사용 | `optionalConform choice="a"` |
| `1` | `TL` | `TemperatureLevel` | 온도 레벨 사용 | `optionalConform choice="a"` |
| `2` | `STEP` | `TemperatureStep` | 온도 값의 단계 제어 | `TN` 조건의 `optionalConform` |

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 필수 조건 | 제약 | Persistence |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureSetpoint` | `temperature` | `TN` | `MinTemperature` 이상, `MaxTemperature` 이하 | 명시 없음 |
| `0x0001` | `MinTemperature` | `temperature` | `TN` | `MaxTemperature - 1` 이하 | `fixed` |
| `0x0002` | `MaxTemperature` | `temperature` | `TN` | `<desc/>`만 제공됨 | `fixed` |
| `0x0003` | `Step` | `temperature` | `STEP` | `1` 이상, `MaxTemperature - MinTemperature` 이하 | `fixed` |
| `0x0004` | `SelectedTemperatureLevel` | `uint8` | `TL` | 최댓값 `31` | 명시 없음 |
| `0x0005` | `SupportedTemperatureLevels` | `list` | `TL` | 최대 `32`개 항목, 각 `string`의 `maxLength`는 `16` | 명시 없음 |

### 명령

#### `SetTemperature`

| 항목 | 값 |
|---|---|
| ID | `0x00` |
| 방향 | `commandToServer` |
| 응답 설정 | `response="Y"` |
| 호출 권한 | `operate` |
| 적합성 | 필수 |

| 필드 ID | 이름 | 타입 | 필수 조건 | 제약 |
|---|---|---|---|---|
| `0` | `TargetTemperature` | `temperature` | `TN` | `<desc/>`만 제공됨 |
| `1` | `TargetTemperatureLevel` | `uint8` | `TL` | `<desc/>`만 제공됨 |

제공된 XML에는 `<desc/>`에 대응하는 상세 제약 설명이 포함되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml`

### 클러스터 설정

| 항목 | 값 |
|---|---|
| 이름 | `Temperature Control` |
| 코드 | `0x0056` |
| define | `TEMPERATURE_CONTROL_CLUSTER` |
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| client | 활성화, `tick="false"`, `init="false"` |
| server | 활성화, `tick="false"`, `init="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

파일은 `Alchemy`로 생성되었으며 `DO NOT EDIT`로 표시되어 있다. 생성 원본 경로는 `src/app_clusters/TemperatureControl.adoc`이다.

### 속성 매핑

모든 속성은 `side="server"`, `optional="true"`로 선언되며, 기능별 `mandatoryConform` 조건이 함께 지정되어 있다.

| 코드 | 이름 | define | SDK 타입 | 필수 조건 | 추가 설정 |
|---|---|---|---|---|---|
| `0x0000` | `TemperatureSetpoint` | `TEMP_SETPOINT` | `temperature` | `TN` | 없음 |
| `0x0001` | `MinTemperature` | `MIN_TEMP` | `temperature` | `TN` | 없음 |
| `0x0002` | `MaxTemperature` | `MAX_TEMP` | `temperature` | `TN` | 없음 |
| `0x0003` | `Step` | `STEP` | `temperature` | `STEP` | 없음 |
| `0x0004` | `SelectedTemperatureLevel` | `SELECTED_TEMP_LEVEL` | `int8u` | `TL` | `max="31"` |
| `0x0005` | `SupportedTemperatureLevels` | `SUPPORTED_TEMP_LEVELS` | `array` | `TL` | `entryType="char_string"`, `length="32"` |

기능의 bit, 코드, 이름 및 적합성 조건은 스펙 XML과 동일하다.

### 명령 매핑

`SetTemperature`는 `source="client"`, `code="0x00"`, `optional="false"`로 정의된다.

| 인자 ID | 이름 | SDK 타입 | 설정 |
|---|---|---|---|
| `0` | `TargetTemperature` | `temperature` | `optional="true"` |
| `1` | `TargetTemperatureLevel` | `int8u` | `optional="true"` |

SDK XML에서는 두 인자가 모두 선택적으로 표현되지만, 구현은 활성화된 기능에 해당하는 인자의 존재 여부를 검사한다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/temperature-control-server/CodegenIntegration.cpp` | 클러스터 등록·해제, 기본값 로딩, endpoint 기반 API |
| `src/app/clusters/temperature-control-server/CodegenIntegration.h` | endpoint 기반 API 선언 |
| `src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp` | 초기 설정 검증, 속성 읽기·갱신, 명령 처리 |
| `src/app/clusters/temperature-control-server/TemperatureControlCluster.h` | `TemperatureControlCluster` 및 `StartupConfiguration` 선언 |
| `src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h` | `SupportedTemperatureLevelsIteratorDelegate` 인터페이스 |
| `src/app/clusters/temperature-control-server/temperature-control-server.h` | `app/clusters/temperature-control-server/CodegenIntegration.h` 포함 |

### 클러스터 클래스와 초기 설정

`chip::app::Clusters::TemperatureControlCluster`는 `DefaultServerCluster`를 상속한다.

`StartupConfiguration`은 다음 초기값을 보관한다. 모든 필드는 `{}`로 초기화된다.

| 필드 | 타입 |
|---|---|
| `temperatureSetpoint` | `int16_t` |
| `minTemperature` | `int16_t` |
| `maxTemperature` | `int16_t` |
| `step` | `int16_t` |
| `selectedTemperatureLevel` | `uint8_t` |

생성자는 다음 조건을 `VerifyOrDie`로 검증한다.

- `Feature::kTemperatureNumber`가 활성화된 경우:
  - `Feature::kTemperatureLevel`은 비활성화되어야 한다.
  - `mMinTemperature`는 `kMinTemperatureRange`(`-27315`) 이상, `kMaxTemperatureRange`(`32766`) 이하여야 한다.
  - `mMaxTemperature`는 `mMinTemperature + 1` 이상이어야 한다.
  - `mTemperatureSetpoint`는 `mMinTemperature` 이상, `mMaxTemperature` 이하여야 한다.
  - `Feature::kTemperatureStep`도 활성화되어 있으면 `mStep`은 `kMinStep`(`1`) 이상, `mMaxTemperature - mMinTemperature` 이하여야 한다.
- `Feature::kTemperatureLevel`이 활성화된 경우:
  - `mSelectedTemperatureLevel`은 `kMaxSelectedTemperatureLevel`(`31`) 이하여야 한다.

### 등록 및 수명주기

`CodegenIntegration.cpp`는 다음 크기의 `gServers` 배열을 관리한다.

- `kTemperatureControlFixedClusterCount`: `TemperatureControl::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kTemperatureControlMaxClusterCount`: `kTemperatureControlFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- 배열 요소 타입: `LazyRegisteredServerCluster<TemperatureControlCluster>`

`IntegrationDelegate::CreateRegistration`의 처리 순서는 다음과 같다.

1. `optionalAttributeBits`로 `app::OptionalAttributeSet`을, `featureMap`으로 `BitFlags<Feature>`를 구성한다.
2. 활성 기능에 필요한 속성이 존재하는지 검증한다.
3. `GetDefault`로 초기값을 읽고 반환값이 `Status::Success`인지 검증한다.
   - `Feature::kTemperatureNumber`: `TemperatureSetpoint`, `MinTemperature`, `MaxTemperature`
   - 위 조건에서 `Feature::kTemperatureStep`: `Step`
   - `Feature::kTemperatureLevel`: `SelectedTemperatureLevel`
4. `Feature::kTemperatureLevel`에서는 `SupportedTemperatureLevels`의 존재도 검증한다. 목록 값 자체를 `GetDefault`로 읽지는 않는다.
5. `StartupConfiguration`으로 인스턴스를 생성하고 `Registration()`을 반환한다.

| 함수 | 동작 |
|---|---|
| `MatterTemperatureControlClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`과 `fetchOptionalAttributes`를 `true`로 설정 |
| `MatterTemperatureControlClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 시 `shutdownType` 전달 |
| `MatterTemperatureControlPluginServerInitCallback` | 빈 구현 |
| `IntegrationDelegate::FindRegistration` | 인스턴스가 생성되지 않았으면 `nullptr`, 생성되었으면 `Cluster()`의 주소 반환 |
| `IntegrationDelegate::ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

### 속성 노출 및 읽기

`Attributes`는 `AttributeListBuilder`를 통해 `kMandatoryMetadata`와 기능별 속성을 추가한다.

| 기능 | 추가되는 속성 |
|---|---|
| `Feature::kTemperatureNumber` | `TemperatureSetpoint`, `MinTemperature`, `MaxTemperature` |
| `Feature::kTemperatureStep` | `Step` |
| `Feature::kTemperatureLevel` | `SelectedTemperatureLevel`, `SupportedTemperatureLevels` |

`ReadAttribute`는 다음을 처리한다.

- `ClusterRevision`: `TemperatureControl::kRevision` 인코딩
- `FeatureMap`: `mFeatures` 인코딩
- 온도 및 선택 레벨 속성: 대응하는 멤버 값 인코딩
- `SupportedTemperatureLevels`:
  - `mDelegate == nullptr`이면 `EncodeEmptyList()` 호출
  - delegate가 있으면 `Reset(request.path.mEndpointId)` 호출
  - `Next(item)`이 `CHIP_NO_ERROR`를 반환하는 동안 각 항목 인코딩
  - 항목 인코딩 오류는 반환하며, `Next(item)`이 다른 값을 반환하면 반복을 종료
- 그 밖의 속성: `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환

### 속성 갱신

#### `SetTemperatureSetpoint`

검증 순서는 다음과 같다.

1. `Feature::kTemperatureNumber`가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)` 반환
2. 요청 값이 `mMinTemperature`부터 `mMaxTemperature`까지의 범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)` 반환
3. `Feature::kTemperatureStep`이 활성화되어 있으면 다음 조건 검사:

   ```cpp
   (temperatureSetpoint - mMinTemperature) % mStep == 0
   ```

   조건을 만족하지 않으면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.

검증 성공 시 `SetAttributeValue`로 `mTemperatureSetpoint`를 갱신하고 `CHIP_NO_ERROR`를 반환한다.

#### `SetSelectedTemperatureLevel`

검증 순서는 다음과 같다.

1. `Feature::kTemperatureLevel`이 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)` 반환
2. `mDelegate == nullptr`이면 `CHIP_IM_GLOBAL_STATUS(NotFound)` 반환
3. `selectedTemperatureLevel < mDelegate->Size()`를 만족하지 않으면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)` 반환

검증 성공 시 `mDelegate->Reset(mPath.mEndpointId)`를 호출한 뒤 `SetAttributeValue`로 `mSelectedTemperatureLevel`을 갱신하고 `CHIP_NO_ERROR`를 반환한다. 이 구현에서는 `Size()` 검사가 `Reset()`보다 먼저 수행된다.

### 명령 처리

`AcceptedCommands`는 `Commands::SetTemperature::kMetadataEntry`를 등록한다.

`InvokeCommand`는 `Commands::SetTemperature::Id`에 대해 `Commands::SetTemperature::DecodableType`으로 입력을 디코딩하고 `HandleSetTemperature`를 호출한다. 다른 명령은 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

| 활성 기능 | 필수 입력 검사 | 호출 함수 | 결과 처리 |
|---|---|---|---|
| `Feature::kTemperatureNumber` | `targetTemperature.HasValue()` | `SetTemperatureSetpoint` | 누락: `Status::InvalidCommand`; 범위·단계 오류: `Status::ConstraintError`; 그 외 오류: `Status::InvalidInState` |
| `Feature::kTemperatureLevel` | `targetTemperatureLevel.HasValue()` | `SetSelectedTemperatureLevel` | 누락: `Status::InvalidCommand`; delegate 없음: `Status::NotFound`; 범위 오류: `Status::ConstraintError`; 그 외 오류: `Status::InvalidInState` |

해당 처리를 모두 통과하면 `Status::Success`를 반환한다.

### 온도 레벨 delegate

`SupportedTemperatureLevelsIteratorDelegate`는 다음 인터페이스를 제공한다.

| 함수 | 동작 |
|---|---|
| `Reset(EndpointId endpoint)` | `mEndpoint`를 설정하고 `mIndex`를 `0`으로 초기화 |
| `Size()` | `SupportedTemperatureLevels`의 전체 크기를 반환하는 순수 가상 함수. 반환 타입은 `uint8_t` |
| `Next(MutableCharSpan & item)` | 다음 항목을 제공하는 순수 가상 함수. 반환 타입은 `CHIP_ERROR` |

`TemperatureControlCluster::mDelegate`는 `static` 멤버이며 초기값은 `nullptr`이다. `GetDelegate`와 `SetDelegate`로 접근한다.

### 외부 접근 API

`CodegenIntegration.h`는 `chip::app::Clusters::TemperatureControl`에 다음 API를 선언한다.

```cpp
TemperatureControlCluster * FindClusterOnEndpoint(EndpointId endpointId);

CHIP_ERROR SetTemperatureSetpoint(EndpointId endpointId, int16_t temperatureSetpoint);
CHIP_ERROR SetSelectedTemperatureLevel(EndpointId endpointId, uint8_t selectedTemperatureLevel);

SupportedTemperatureLevelsIteratorDelegate * GetDelegate();
void SetDelegate(SupportedTemperatureLevelsIteratorDelegate * delegate);
```

- `FindClusterOnEndpoint`는 `CodegenClusterIntegration::FindClusterOnEndpoint`의 결과를 `TemperatureControlCluster *`로 변환한다.
- endpoint 기반 `SetTemperatureSetpoint`와 `SetSelectedTemperatureLevel`은 인스턴스를 찾지 못하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. 인스턴스가 있으면 해당 멤버 함수를 호출한다.
- `GetDelegate`와 `SetDelegate`는 `TemperatureControlCluster`의 정적 함수로 전달한다.

클래스는 현재 설정 조회용으로 `GetTemperatureSetpoint`, `GetSelectedTemperatureLevel`, `GetStep`, `GetMinTemperature`, `GetMaxTemperature`도 제공한다.

### 스펙과 구현을 함께 볼 때의 확인 사항

- 스펙은 `SupportedTemperatureLevels`에 최대 `32`개 항목과 항목별 `maxLength="16"`을 지정한다. SDK XML에는 `length="32"`가 있으며, 제공된 구현은 `kMaxTemperatureLevelStringSize = 32` 크기의 `char` 버퍼를 사용한다. `ReadAttribute`에는 목록 개수 `32` 또는 항목 길이 `16`을 직접 검사하는 코드가 없다.
- 생성자는 `mSelectedTemperatureLevel <= 31`을 검사하지만, `SetSelectedTemperatureLevel`은 `mDelegate->Size()`와 비교하며 `31`을 별도로 검사하지 않는다.
- 생성자는 초기 `mTemperatureSetpoint`의 범위를 검사하지만 단계 정렬은 검사하지 않는다. 단계 정렬은 `SetTemperatureSetpoint`에서 검사한다.
- 생성자는 `TN`과 `TL`의 동시 활성화를 거부한다. 제공된 생성자에는 최소 하나의 기능 활성화 여부나 `STEP` 단독 활성화를 직접 검증하는 코드가 없다.
- `kMaxTemperatureRange`는 제공된 생성자에서 `mMinTemperature`의 상한 검사에 사용된다. `mMaxTemperature`에는 `mMinTemperature + 1` 이상인지 확인하는 검사가 있다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
