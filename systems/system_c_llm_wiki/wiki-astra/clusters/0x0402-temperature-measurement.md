---
entity: Temperature Measurement
ids: ['0x0402']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.h', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-measurement-server/README.md', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp', 'data_model/1.7/clusters/TemperatureMeasurement.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Temperature Measurement

## 개요

Temperature Measurement는 온도 측정을 구성하고 측정 결과를 보고하기 위한 클러스터다.

- 클러스터 ID: `0x0402`
- 리비전: `6`
- SDK 도메인: `Measurement & Sensing`
- 구현 방식: code driven approach
- 주요 속성: `MeasuredValue`, `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`

## 스펙

출처: `data_model/1.7/clusters/TemperatureMeasurement.xml`

### 분류

| 항목 | 값 |
|---|---|
| 이름 | Temperature Measurement Cluster |
| 클러스터 ID | `0x0402` |
| revision | `6` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `TMP` |
| scope | `Endpoint` |

### 속성

모든 속성은 `read="true"`, `readPrivilege="view"`로 정의된다.

| ID | 이름 | 타입 | 필수 여부 | Nullable | persistence | 제약 | 기본값 |
|---|---|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `temperature` | 필수 | 예 | 명시 없음 | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 | 명시 없음 |
| `0x0001` | `MinMeasuredValue` | `temperature` | 필수 | 예 | `fixed` | `-27315` 이상, `32766` 이하 | 명시 없음 |
| `0x0002` | `MaxMeasuredValue` | `temperature` | 필수 | 예 | `fixed` | `MinMeasuredValue + 1` 이상 | 명시 없음 |
| `0x0003` | `Tolerance` | `uint16` | 선택 | 명시 없음 | `fixed` | 최대 `2048` | `0` |

### 리비전 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | CCB 2241 2370 |
| `3` | CCB 2823 |
| `4` | 새로운 데이터 모델 형식과 표기법 적용 |
| `5` | P quality 제거 |
| `6` | `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 F quality 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml`

이 파일은 Alchemy가 생성한 XML이며, 주석에 직접 수정하지 않도록 명시되어 있다.

- 생성 원본: `src/app_clusters/TemperatureMeasurement.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`
- 클러스터 define: `TEMPERATURE_MEASUREMENT_CLUSTER`
- client와 server 모두 활성화되며, 각각 `tick="false"`, `init="false"`로 설정된다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="6"`으로 정의된다.

### 서버 속성 정의

| code | name | define | type | min | max | 기타 |
|---|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `TEMP_MEASURED_VALUE` | `temperature` | `-27315` | 명시 없음 | `isNullable="true"` |
| `0x0001` | `MinMeasuredValue` | `TEMP_MIN_MEASURED_VALUE` | `temperature` | `-27315` | `0x7ffe` | `isNullable="true"` |
| `0x0002` | `MaxMeasuredValue` | `TEMP_MAX_MEASURED_VALUE` | `temperature` | `-27314` | 명시 없음 | `isNullable="true"` |
| `0x0003` | `Tolerance` | `TEMP_TOLERANCE` | `int16u` | 명시 없음 | `0x0800` | `default="0"`, `optional="true"`, `optionalConform` |

스펙의 속성 간 제약과 달리, 제공된 SDK XML에는 `MeasuredValue`의 `MinMeasuredValue`·`MaxMeasuredValue` 참조 제약이나 `MaxMeasuredValue`의 `MinMeasuredValue + 1` 제약이 표현되어 있지 않다.

## 구현

### 클래스와 상태

출처:

- `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h`
- `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp`

`chip::app::Clusters`의 `TemperatureMeasurementCluster`는 `DefaultServerCluster`를 상속한다.

`OptionalAttributeSet`은 다음과 같이 `Tolerance`를 선택 속성으로 취급한다.

```cpp
using OptionalAttributeSet = app::OptionalAttributeSet<TemperatureMeasurement::Attributes::Tolerance::Id>;
```

`StartupConfiguration`은 초기 범위와 허용 오차를 전달한다.

```cpp
struct StartupConfiguration
{
    DataModel::Nullable<int16_t> minMeasuredValue{};
    DataModel::Nullable<int16_t> maxMeasuredValue{};
    uint16_t tolerance{};
};
```

내부 상태는 다음과 같다.

| 멤버 | 타입 | 용도 |
|---|---|---|
| `mOptionalAttributeSet` | `const OptionalAttributeSet` | 선택 속성 구성 |
| `mMeasuredValue` | `DataModel::Nullable<int16_t>` | 현재 측정값 |
| `mMinMeasuredValue` | `DataModel::Nullable<int16_t>` | 측정 범위 최솟값 |
| `mMaxMeasuredValue` | `DataModel::Nullable<int16_t>` | 측정 범위 최댓값 |
| `mTolerance` | `uint16_t` | 허용 오차 |

### 생성 시 검증

구현은 다음 상수를 사용한다.

| 상수 | 값 |
|---|---|
| `kMinMeasuredValueRange` | `-27315` |
| `kMaxMeasuredValueRange` | `32766` |
| `kMaxTolerance` | `2048` |

생성자는 다음 조건을 `VerifyOrDie`로 검증한다.

- `config.minMeasuredValue`가 null이 아니면 `-27315` 이상, `32766` 이하이어야 한다.
- 위 조건에서 `config.maxMeasuredValue`도 null이 아니면 `config.minMeasuredValue + 1` 이상이어야 한다.
- `Tolerance::Id`가 선택 속성 집합에 포함되면 `config.tolerance`는 `2048` 이하여야 한다.

검증 후 `mMinMeasuredValue`, `mMaxMeasuredValue`, `mTolerance`에 설정값을 저장한다. `mMeasuredValue`는 멤버의 기본 초기화 상태를 유지한다.

### 속성 읽기와 목록

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 값 |
|---|---|
| `ClusterRevision::Id` | `TemperatureMeasurement::kRevision` |
| `FeatureMap::Id` | `uint32_t` 값 `0` |
| `MeasuredValue::Id` | `mMeasuredValue` |
| `MinMeasuredValue::Id` | `mMinMeasuredValue` |
| `MaxMeasuredValue::Id` | `mMaxMeasuredValue` |
| `Tolerance::Id` | `mTolerance` |

그 밖의 속성은 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용하여 `kMandatoryMetadata`와 선택 속성 `Tolerance::kMetadataEntry`를 추가한다. 선택 속성의 포함 여부는 `mOptionalAttributeSet`으로 결정한다.

### 측정값과 범위 API

| 함수 | 동작 |
|---|---|
| `SetMeasuredValue` | 측정값을 검증하고 갱신 |
| `GetMeasuredValue` | `mMeasuredValue` 반환 |
| `SetMeasuredValueRange` | 측정 범위를 검증하고 갱신 |
| `GetMinMeasuredValue` | `mMinMeasuredValue` 반환 |
| `GetMaxMeasuredValue` | `mMaxMeasuredValue` 반환 |

#### `SetMeasuredValue`

- 입력이 null이면 범위 검증을 건너뛴다.
- 입력이 null이 아니면, null이 아닌 `mMinMeasuredValue`와 `mMaxMeasuredValue`에 대해 각각 하한과 상한을 검증한다.
- 제약 위반 시 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
- 검증 통과 시 `SetAttributeValue(mMeasuredValue, measuredValue, MeasuredValue::Id)`로 갱신하고 `CHIP_NO_ERROR`를 반환한다.

이 함수에는 `-27315`를 직접 적용하는 별도의 절대 하한 검사가 없다.

#### `SetMeasuredValueRange`

- `minMeasuredValue`가 null이 아니면 `-27315` 이상, `32766` 이하인지 검증한다.
- 이때 `maxMeasuredValue`도 null이 아니면 `minMeasuredValue + 1` 이상인지 검증한다.
- 제약 위반 시 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
- 검증 통과 시 두 범위 속성을 각각 `SetAttributeValue`로 갱신하고 `CHIP_NO_ERROR`를 반환한다.

제공된 구현에서는 `minMeasuredValue`가 null일 때 `maxMeasuredValue`를 별도로 검증하지 않는다. 범위 변경 시 기존 `mMeasuredValue`를 재검증하거나 조정하는 코드도 없다.

### codegen 통합

출처:

- `src/app/clusters/temperature-measurement-server/CodegenIntegration.h`
- `src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp`

#### 인스턴스 관리

- `kTemperatureMeasurementFixedClusterCount`는 `TemperatureMeasurement::StaticApplicationConfig::kFixedClusterConfig.size()`로 계산한다.
- `kTemperatureMeasurementMaxClusterCount`는 고정 인스턴스 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `gServers`는 `LazyRegisteredServerCluster<TemperatureMeasurementCluster>` 배열이다.

`IntegrationDelegate`는 다음 동작을 제공한다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | 기본 속성값을 읽고 `StartupConfiguration`으로 인스턴스를 생성한 뒤 등록 객체 반환 |
| `FindRegistration` | 생성된 인스턴스의 인터페이스 반환. 생성되지 않았으면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

초기값은 다음과 같이 읽는다.

- `MinMeasuredValue::GetDefaultOr`: 기본값이 없으면 `DataModel::NullNullable`
- `MaxMeasuredValue::GetDefaultOr`: 기본값이 없으면 `DataModel::NullNullable`
- `Tolerance::GetDefaultOr`: 기본값이 없으면 `0`

주석은 `MinMeasuredValue`와 `MaxMeasuredValue`가 필수 속성이지만, 모든 앱이 ember 기본값을 설정하지는 않으므로 누락을 허용하고 null로 처리한다고 설명한다.

#### 등록과 해제

- `MatterTemperatureMeasurementClusterInitCallback`은 `CodegenClusterIntegration::RegisterServer`를 호출한다.
  - `clusterId`: `TemperatureMeasurement::Id`
  - `fetchFeatureMap`: `false`
  - `fetchOptionalAttributes`: `true`
- `MatterTemperatureMeasurementClusterShutdownCallback`은 `CodegenClusterIntegration::UnregisterServer`를 호출하고 `shutdownType`을 전달한다.

#### Endpoint 단위 접근

`chip::app::Clusters::TemperatureMeasurement`는 다음 함수를 제공한다.

```cpp
TemperatureMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);

CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<int16_t> measuredValue);
CHIP_ERROR SetMeasuredValueRange(EndpointId endpointId, DataModel::Nullable<int16_t> minMeasuredValue,
                                 DataModel::Nullable<int16_t> maxMeasuredValue);
```

`FindClusterOnEndpoint`는 codegen 통합 계층에서 클러스터를 찾아 `TemperatureMeasurementCluster *`로 반환한다.

두 설정 함수는 클러스터를 찾지 못하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. 찾으면 해당 인스턴스의 `SetMeasuredValue` 또는 `SetMeasuredValueRange`를 호출하고 그 결과를 반환한다.

## 관련 문서

### code driven approach 전환 안내

출처: `src/app/clusters/temperature-measurement-server/README.md`

README는 현재 클러스터가 code driven approach를 따르며, `MeasuredValue`의 Accessors를 더 이상 사용할 수 없다고 설명한다.

기존 Accessors 호출:

```cpp
app::Clusters::TemperatureMeasurement::Attributes::MeasuredValue::Set(1, static_cast<int16_t>(1000));
```

현재 호출 방식:

```cpp
CHIP_ERROR err = app::Clusters::TemperatureMeasurement::SetMeasuredValue(1, static_cast<int16_t>(1000));
if (err == CHIP_NO_ERROR)
{
    // SetMeasuredValue() succeeded
}
else
{
    // SetMeasuredValue() failed
}
```

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
