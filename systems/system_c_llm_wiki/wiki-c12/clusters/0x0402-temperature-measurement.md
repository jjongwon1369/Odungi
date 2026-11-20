---
entity: Temperature Measurement
ids: ['0x0402']
source_paths: ['data_model/1.7/clusters/TemperatureMeasurement.xml', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.h', 'src/app/clusters/temperature-measurement-server/README.md', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h', 'src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Temperature Measurement

## 개요

`Temperature Measurement`는 온도 측정 설정과 측정값 보고를 위한 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0402` |
| 스펙 이름 | `Temperature Measurement Cluster` |
| 리비전 | `6` |
| 분류 | `hierarchy="base"`, `role="application"` |
| PICS 코드 | `TMP` |
| 범위 | `Endpoint` |
| SDK 도메인 | `Measurement & Sensing` |

현재 구현은 code driven 방식을 사용한다. `MeasuredValue`를 설정하는 기존 Accessors 대신 `SetMeasuredValue`를 사용한다.

## 스펙

출처: `data_model/1.7/clusters/TemperatureMeasurement.xml`

### 속성

모든 속성은 읽기를 지원하며 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 적합성 | Nullable | 고정성 | 제약 | 기본값 |
|---|---|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `temperature` | 필수 | 지원 | — | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 | 명시 없음 |
| `0x0001` | `MinMeasuredValue` | `temperature` | 필수 | 지원 | `persistence="fixed"` | `-27315` 이상, `32766` 이하 | 명시 없음 |
| `0x0002` | `MaxMeasuredValue` | `temperature` | 필수 | 지원 | `persistence="fixed"` | `MinMeasuredValue + 1` 이상 | 명시 없음 |
| `0x0003` | `Tolerance` | `uint16` | 선택 | 명시 없음 | `persistence="fixed"` | 최대 `2048` | `0` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | CCB 2241 2370 |
| `3` | CCB 2823 |
| `4` | 새로운 데이터 모델 형식 및 표기법 적용 |
| `5` | P 품질 제거 |
| `6` | `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 F 품질 추가 |

제공된 XML에는 명령 및 이벤트 정의가 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml`

### 클러스터 설정

- 클러스터 코드: `0x0402`
- 매크로: `TEMPERATURE_MEASUREMENT_CLUSTER`
- `client`, `server` 모두 활성화되어 있으며 각각 `tick="false"`, `init="false"`로 정의된다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="6"`으로 정의된다.
- XML은 Alchemy로 생성되며 직접 수정하지 않도록 표시되어 있다.
  - 원본: `src/app_clusters/TemperatureMeasurement.adoc`
  - Git: `0.9-1.7-winter2027`
  - Alchemy: `v1.7.10`

### 속성 매핑

모든 속성은 `side="server"`로 정의된다.

| ID | 이름 | define | 타입 | SDK XML의 제약 및 설정 |
|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `TEMP_MEASURED_VALUE` | `temperature` | `min="-27315"`, `isNullable="true"` |
| `0x0001` | `MinMeasuredValue` | `TEMP_MIN_MEASURED_VALUE` | `temperature` | `min="-27315"`, `max="0x7ffe"`, `isNullable="true"` |
| `0x0002` | `MaxMeasuredValue` | `TEMP_MAX_MEASURED_VALUE` | `temperature` | `min="-27314"`, `isNullable="true"` |
| `0x0003` | `Tolerance` | `TEMP_TOLERANCE` | `int16u` | `max="0x0800"`, `default="0"`, `optional="true"` |

스펙의 속성 간 제약과 달리, SDK XML에는 위와 같은 정적 범위가 명시되어 있다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h` | 서버 클래스, 초기 설정, 속성 접근 API 선언 |
| `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp` | 초기 설정 검증, 속성 읽기, 측정값 및 범위 갱신 |
| `src/app/clusters/temperature-measurement-server/CodegenIntegration.h` | Endpoint 기반 조회 및 설정 API 선언 |
| `src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp` | 서버 등록·해제, 기본값 로딩, Endpoint 기반 API 구현 |

### 서버 클래스와 초기 설정

`chip::app::Clusters`의 `TemperatureMeasurementCluster`는 `DefaultServerCluster`를 상속한다.

- `OptionalAttributeSet`은 `TemperatureMeasurement::Attributes::Tolerance::Id`를 선택 속성으로 관리한다.
- `StartupConfiguration`은 다음 필드를 가진다.
  - `DataModel::Nullable<int16_t> minMeasuredValue`
  - `DataModel::Nullable<int16_t> maxMeasuredValue`
  - `uint16_t tolerance`

생성자는 다음 조건을 `VerifyOrDie`로 검증한다.

1. `minMeasuredValue`가 null이 아니면 `-27315` 이상, `32766` 이하이어야 한다.
2. 두 경계가 모두 null이 아니면 `maxMeasuredValue`는 `minMeasuredValue + 1` 이상이어야 한다.
3. `Tolerance`가 선택된 경우 `tolerance`는 `2048` 이하여야 한다.

검증 후 설정값을 `mMinMeasuredValue`, `mMaxMeasuredValue`, `mTolerance`에 저장한다.

### 속성 읽기와 목록

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 대상 |
|---|---|
| `ClusterRevision` | `TemperatureMeasurement::kRevision` |
| `FeatureMap` | `uint32_t` 값 `0` |
| `MeasuredValue` | `mMeasuredValue` |
| `MinMeasuredValue` | `mMinMeasuredValue` |
| `MaxMeasuredValue` | `mMaxMeasuredValue` |
| `Tolerance` | `mTolerance` |

그 외 속성 ID에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용하여 `kMandatoryMetadata`와 선택 속성 `Tolerance::kMetadataEntry`를 결합한다. 선택 속성 포함 여부는 `mOptionalAttributeSet`으로 결정한다.

### 측정값 및 범위 API

#### `SetMeasuredValue`

- 입력 타입은 `DataModel::Nullable<int16_t>`이다.
- 입력이 null이 아닌 경우:
  - `mMinMeasuredValue`가 null이 아니면 하한을 검사한다.
  - `mMaxMeasuredValue`가 null이 아니면 상한을 검사한다.
- 제약 위반 시 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
- 검증에 통과하면 `SetAttributeValue`로 `mMeasuredValue`를 갱신하고 `CHIP_NO_ERROR`를 반환한다.
- null 입력에는 범위 검사를 수행하지 않는다.

#### `SetMeasuredValueRange`

- `minMeasuredValue`, `maxMeasuredValue`를 `DataModel::Nullable<int16_t>`로 받는다.
- `minMeasuredValue`가 null이 아니면 `-27315` 이상, `32766` 이하인지 검사한다.
- 두 입력이 모두 null이 아니면 `maxMeasuredValue >= minMeasuredValue + 1`을 검사한다.
- 제약 위반 시 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
- 검증 후 `SetAttributeValue`로 두 경계를 갱신하고 `CHIP_NO_ERROR`를 반환한다.

제공된 구현에서 `SetMeasuredValueRange`는 기존 `mMeasuredValue`를 다시 검증하거나 조정하지 않는다. 또한 `minMeasuredValue`가 null인 경우 `maxMeasuredValue`에 대한 별도 검사를 수행하지 않는다.

조회 메서드는 `GetMeasuredValue`, `GetMinMeasuredValue`, `GetMaxMeasuredValue`이다.

### Codegen 통합

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

- `kTemperatureMeasurementFixedClusterCount`는 `TemperatureMeasurement::StaticApplicationConfig::kFixedClusterConfig.size()`로 계산한다.
- `kTemperatureMeasurementMaxClusterCount`는 고정 인스턴스 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `gServers`는 `LazyRegisteredServerCluster<TemperatureMeasurementCluster>` 배열이다.

`CreateRegistration`은 다음 순서로 서버를 생성한다.

1. `optionalAttributeBits`로 `OptionalAttributeSet`을 구성한다.
2. `MinMeasuredValue::GetDefaultOr`, `MaxMeasuredValue::GetDefaultOr`로 초기 경계를 읽는다. 기본값이 없으면 `DataModel::NullNullable`을 사용한다.
3. `Tolerance::GetDefaultOr`로 값을 읽으며 기본값이 없으면 `0`을 사용한다.
4. `StartupConfiguration`을 전달하여 인스턴스를 생성하고 등록 정보를 반환한다.

| 함수 | 동작 |
|---|---|
| `MatterTemperatureMeasurementClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap=false`, `fetchOptionalAttributes=true` |
| `MatterTemperatureMeasurementClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 및 `shutdownType` 전달 |
| `FindRegistration` | 생성된 인스턴스를 반환하며, 생성되지 않았으면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy` 호출 |

`chip::app::Clusters::TemperatureMeasurement`에는 Endpoint 기반 API가 제공된다.

```cpp
TemperatureMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);

CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<int16_t> measuredValue);
CHIP_ERROR SetMeasuredValueRange(EndpointId endpointId, DataModel::Nullable<int16_t> minMeasuredValue,
                                 DataModel::Nullable<int16_t> maxMeasuredValue);
```

두 설정 함수는 `FindClusterOnEndpoint`로 인스턴스를 조회한다. 인스턴스가 없으면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환하고, 있으면 해당 클래스 메서드에 호출을 위임한다.

## 관련 문서

### code driven 방식으로의 전환

출처: `src/app/clusters/temperature-measurement-server/README.md`

문서는 `MeasuredValue`용 Accessors를 더 이상 사용할 수 없으며, 다음과 같이 호출을 변경하도록 안내한다.

기존 방식:

```cpp
app::Clusters::TemperatureMeasurement::Attributes::MeasuredValue::Set(1, static_cast<int16_t>(1000));
```

현재 방식:

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

- [Cook Surface](../device-types/cook-surface.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
