---
entity: Temperature Measurement
ids: ['0x0402']
source_paths: ['data_model/1.7/clusters/TemperatureMeasurement.xml', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.h', 'src/app/clusters/temperature-measurement-server/README.md', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h', 'src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Temperature Measurement

## 개요

`Temperature Measurement`는 온도 측정 구성과 측정값 보고를 위한 클러스터이다. 클러스터 ID는 `0x0402`이며, 제공된 스펙과 SDK 정의의 리비전은 `6`이다.

구현은 code driven approach를 사용한다. `MeasuredValue` 설정에는 기존 Accessors 대신 `SetMeasuredValue`를 사용한다.

## 스펙

출처: `data_model/1.7/clusters/TemperatureMeasurement.xml`

### 기본 정보

| 항목 | 값 |
|---|---|
| 스펙 이름 | `Temperature Measurement Cluster` |
| 클러스터 이름 | `Temperature Measurement` |
| 클러스터 ID | `0x0402` |
| 리비전 | `6` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `TMP` |
| scope | `Endpoint` |

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 필수 여부 | Nullable | persistence | 제약 | 기본값 |
|---|---|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `temperature` | 필수 | 지원 | 명시 없음 | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 | 명시 없음 |
| `0x0001` | `MinMeasuredValue` | `temperature` | 필수 | 지원 | `fixed` | `-27315` 이상, `32766` 이하 | 명시 없음 |
| `0x0002` | `MaxMeasuredValue` | `temperature` | 필수 | 지원 | `fixed` | `MinMeasuredValue + 1` 이상 | 명시 없음 |
| `0x0003` | `Tolerance` | `uint16` | 선택 | 명시 없음 | `fixed` | 최댓값 `2048` | `0` |

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | CCB 2241 2370 |
| `3` | CCB 2823 |
| `4` | 새로운 데이터 모델 형식 및 표기법 도입 |
| `5` | P quality 제거 |
| `6` | `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 F quality 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml`

### 클러스터 설정

| 항목 | 값 |
|---|---|
| 이름 | `Temperature Measurement` |
| 도메인 | `Measurement & Sensing` |
| 코드 | `0x0402` |
| define | `TEMPERATURE_MEASUREMENT_CLUSTER` |
| client | `true`, `tick="false"`, `init="false"` |
| server | `true`, `tick="false"`, `init="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="6"` |

### 속성 매핑

모든 속성은 `side="server"`로 정의되어 있다.

| ID | 이름 | define | 타입 | SDK XML 제약 및 설정 |
|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `TEMP_MEASURED_VALUE` | `temperature` | `min="-27315"`, `isNullable="true"` |
| `0x0001` | `MinMeasuredValue` | `TEMP_MIN_MEASURED_VALUE` | `temperature` | `min="-27315"`, `max="0x7ffe"`, `isNullable="true"` |
| `0x0002` | `MaxMeasuredValue` | `TEMP_MAX_MEASURED_VALUE` | `temperature` | `min="-27314"`, `isNullable="true"` |
| `0x0003` | `Tolerance` | `TEMP_TOLERANCE` | `int16u` | `max="0x0800"`, `default="0"`, `optional="true"` |

스펙은 속성 사이의 관계를 제약으로 명시하며, SDK XML은 위와 같은 정적 최솟값·최댓값을 정의한다. `Tolerance`의 타입 표기는 스펙에서 `uint16`, SDK XML에서 `int16u`이다.

이 XML은 Alchemy로 생성되었으며 직접 수정하지 않도록 표시되어 있다.

- 생성 원본: `src/app_clusters/TemperatureMeasurement.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

## 구현

### 구성 파일

| 파일 | 역할 |
|---|---|
| `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h` | `TemperatureMeasurementCluster`, `StartupConfiguration`, 속성 접근 함수 선언 |
| `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp` | 초기 설정 검증, 속성 읽기, 측정값 및 범위 변경 |
| `src/app/clusters/temperature-measurement-server/CodegenIntegration.h` | Endpoint 기반 조회 및 설정 함수 선언 |
| `src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp` | 서버 등록·해제와 Endpoint 기반 함수 구현 |

### 클래스와 초기 설정

`chip::app::Clusters`의 `TemperatureMeasurementCluster`는 `DefaultServerCluster`를 상속한다.

`OptionalAttributeSet`은 `TemperatureMeasurement::Attributes::Tolerance::Id`를 선택 속성으로 관리한다.

`StartupConfiguration`은 다음 필드를 가진다.

| 필드 | 타입 |
|---|---|
| `minMeasuredValue` | `DataModel::Nullable<int16_t>` |
| `maxMeasuredValue` | `DataModel::Nullable<int16_t>` |
| `tolerance` | `uint16_t` |

생성자는 다음 조건을 `VerifyOrDie`로 검사한다.

- `minMeasuredValue`가 null이 아니면 `-27315` 이상, `32766` 이하이어야 한다.
- `minMeasuredValue`와 `maxMeasuredValue`가 모두 null이 아니면 `maxMeasuredValue >= minMeasuredValue + 1`이어야 한다.
- `Tolerance`가 선택되어 있으면 `tolerance <= 2048`이어야 한다.

검증 후 설정값을 `mMinMeasuredValue`, `mMaxMeasuredValue`, `mTolerance`에 저장한다. `mMeasuredValue`는 `DataModel::Nullable<int16_t>`의 `{}` 초기화를 사용한다.

### 속성 읽기와 목록 구성

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 값 |
|---|---|
| `ClusterRevision` | `TemperatureMeasurement::kRevision` |
| `FeatureMap` | `uint32_t` 값 `0` |
| `MeasuredValue` | `mMeasuredValue` |
| `MinMeasuredValue` | `mMinMeasuredValue` |
| `MaxMeasuredValue` | `mMaxMeasuredValue` |
| `Tolerance` | `mTolerance` |

그 외 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용해 `kMandatoryMetadata`와 선택 속성 `Tolerance::kMetadataEntry`를 결합한다. 선택 속성 포함 여부는 `mOptionalAttributeSet`에 따른다.

### 측정값 설정

`TemperatureMeasurementCluster::SetMeasuredValue`는 `DataModel::Nullable<int16_t>`를 받는다.

- 입력이 null이면 범위 검사를 생략한다.
- 입력과 `mMinMeasuredValue`가 null이 아니면 하한을 검사한다.
- 입력과 `mMaxMeasuredValue`가 null이 아니면 상한을 검사한다.
- 범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
- 성공하면 `SetAttributeValue`로 `mMeasuredValue`를 갱신하고 `CHIP_NO_ERROR`를 반환한다.

이 함수에는 SDK XML의 `min="-27315"`를 별도로 검사하는 코드가 없다. 제공된 구현의 검사는 현재 설정된 null이 아닌 경계값을 기준으로 한다.

### 측정 범위 설정

`TemperatureMeasurementCluster::SetMeasuredValueRange`는 다음을 검사한다.

1. `minMeasuredValue`가 null이 아니면 `-27315` 이상, `32766` 이하인지 검사한다.
2. 두 경계값이 모두 null이 아니면 `maxMeasuredValue >= minMeasuredValue + 1`인지 검사한다.

실패하면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다. 성공하면 `SetAttributeValue`로 두 경계값을 갱신하고 `CHIP_NO_ERROR`를 반환한다.

제공된 구현에서는:

- `minMeasuredValue`가 null이면 `maxMeasuredValue`의 별도 범위 검사를 하지 않는다.
- 범위를 변경할 때 기존 `mMeasuredValue`를 재검증하거나 조정하지 않는다.

조회 함수는 `GetMeasuredValue`, `GetMinMeasuredValue`, `GetMaxMeasuredValue`이다.

### Codegen 통합과 서버 수명주기

`gServers`는 `LazyRegisteredServerCluster<TemperatureMeasurementCluster>` 배열이다.

- `kTemperatureMeasurementFixedClusterCount`는 `TemperatureMeasurement::StaticApplicationConfig::kFixedClusterConfig.size()`에서 계산한다.
- `kTemperatureMeasurementMaxClusterCount`는 고정 개수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.

`IntegrationDelegate`의 동작은 다음과 같다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | `optionalAttributeBits`로 선택 속성을 구성하고 기본값을 읽어 서버 인스턴스 생성 |
| `FindRegistration` | 생성된 인스턴스의 `Cluster()` 반환; 생성되지 않았으면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

`CreateRegistration`은 다음 기본값을 사용한다.

- `MinMeasuredValue::GetDefaultOr`: 기본값이 없으면 `DataModel::NullNullable`
- `MaxMeasuredValue::GetDefaultOr`: 기본값이 없으면 `DataModel::NullNullable`
- `Tolerance::GetDefaultOr`: 기본값이 없으면 `0`

`MinMeasuredValue`와 `MaxMeasuredValue`는 필수 속성이지만, 앱이 ember 기본값을 설정하지 않은 경우도 허용한다.

서버 수명주기 함수는 다음과 같다.

- `MatterTemperatureMeasurementClusterInitCallback`: `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true`이다.
- `MatterTemperatureMeasurementClusterShutdownCallback`: `CodegenClusterIntegration::UnregisterServer` 호출. `shutdownType`을 전달한다.

### Endpoint 기반 API

`chip::app::Clusters::TemperatureMeasurement`에서 다음 함수를 제공한다.

```cpp
TemperatureMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);

CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<int16_t> measuredValue);
CHIP_ERROR SetMeasuredValueRange(EndpointId endpointId, DataModel::Nullable<int16_t> minMeasuredValue,
                                 DataModel::Nullable<int16_t> maxMeasuredValue);
```

`FindClusterOnEndpoint`는 `CodegenClusterIntegration::FindClusterOnEndpoint`를 통해 인스턴스를 조회한다.

두 설정 함수는 해당 Endpoint에서 인스턴스를 찾지 못하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. 인스턴스가 있으면 대응하는 `TemperatureMeasurementCluster` 멤버 함수에 처리를 위임한다.

## 관련 문서

### code driven approach 전환

출처: `src/app/clusters/temperature-measurement-server/README.md`

문서는 `MeasuredValue`의 Accessors를 더 이상 사용할 수 없으며, `SetMeasuredValue`로 전환해야 한다고 설명한다.

**이전 방식:**

```cpp
app::Clusters::TemperatureMeasurement::Attributes::MeasuredValue::Set(1, static_cast<int16_t>(1000));
```

**현재 방식:**

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
