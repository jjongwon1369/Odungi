---
entity: Relative Humidity Measurement
ids: ['0x0405']
source_paths: ['data_model/1.7/clusters/WaterContentMeasurement.xml', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h', 'src/app/clusters/relative-humidity-measurement-server/README.md', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h', 'src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml', 'zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Relative Humidity Measurement

## 개요

`Relative Humidity Measurement`는 상대 습도 측정 구성과 측정값 보고를 위한 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0405` |
| PICS 코드 | `RH` |
| 분류 | `hierarchy="base"`, `role="application"` |
| 범위 | `Endpoint` |
| SDK 도메인 | `Measurement & Sensing` |
| 구현 클래스 | `chip::app::Clusters::RelativeHumidityMeasurementCluster` |

구현은 code-driven 방식을 사용한다. `MeasuredValue`, `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 대한 기존 Ember attribute accessors는 더 이상 제공되지 않는다. 측정값은 `SetMeasuredValue`로 갱신하며, 범위와 허용 오차는 생성 시 `Config`로 설정한다.

## 스펙

출처: `data_model/1.7/clusters/WaterContentMeasurement.xml`

### 속성

모든 속성은 `uint16`이며, 읽기 접근 권한은 `view`이다.

| ID | 이름 | 적합성 | null 허용 | 고정 속성 | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | 필수 | 예 | 아니요 | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 |
| `0x0001` | `MinMeasuredValue` | 필수 | 예 | 예 | 최대 `9999` |
| `0x0002` | `MaxMeasuredValue` | 필수 | 예 | 예 | `MinMeasuredValue + 1` 이상, `10000` 이하 |
| `0x0003` | `Tolerance` | 선택 | 아니요 | 예 | 최대 `2048` |

고정 속성은 XML에서 `persistence="fixed"`로 지정되어 있다. 제공된 스펙 XML에는 명령과 이벤트 정의가 없다.

### 개정 이력

`Water Content Measurement Clusters`의 `revision`은 `5`이다.

| revision | 변경 내용 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | `CCB 2241` |
| `3` | 새 데이터 모델 형식과 표기법 적용 |
| `4` | `P` quality 제거 |
| `5` | `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 `F` quality 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml`

### 클러스터 구성

- 클러스터 이름: `Relative Humidity Measurement`
- 클러스터 코드: `0x0405`
- 매크로: `RELATIVE_HUMIDITY_MEASUREMENT_CLUSTER`
- client와 server 모두 지원하며, 두 구성 모두 `tick="false"`, `init="false"`이다.
- server에는 `tickFrequency="half"`가 지정되어 있다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="3"`으로 정의된다.
- XML은 Alchemy 생성 파일이며, 원본 경로는 `src/app_clusters/WaterContentMeasurement.adoc`이다.

### 속성 정의

모든 속성은 `side="server"`, `type="int16u"`로 정의된다.

| ID | 이름 | define | XML 제약 |
|---|---|---|---|
| `0x0000` | `MeasuredValue` | `RELATIVE_HUMIDITY_MEASURED_VALUE` | `isNullable="true"`, `max="10000"` |
| `0x0001` | `MinMeasuredValue` | `RELATIVE_HUMIDITY_MIN_MEASURED_VALUE` | `isNullable="true"`, `max="0x270F"` |
| `0x0002` | `MaxMeasuredValue` | `RELATIVE_HUMIDITY_MAX_MEASURED_VALUE` | `isNullable="true"`, `min="0x0001"`, `max="0x2710"` |
| `0x0003` | `Tolerance` | `RELATIVE_HUMIDITY_TOLERANCE` | `max="0x0800"`, `optionalConform` |

### 생성된 메타데이터

출처: `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h`

생성 기준 파일은 `src/controller/data_model/controller-clusters.matter`이다.

- `RelativeHumidityMeasurement::kRevision`은 `3`이다.
- 네 속성의 `kMetadataEntry`는 읽기 권한으로 `Access::Privilege::kView`를 사용하고, 쓰기 권한 자리에는 `std::nullopt`를 지정한다.
- 각 속성의 `BitFlags<DataModel::AttributeQualityFlags>()`는 비어 있다.
- `kMandatoryMetadata`에는 다음 세 항목이 포함된다.
  - `MeasuredValue::kMetadataEntry`
  - `MinMeasuredValue::kMetadataEntry`
  - `MaxMeasuredValue::kMetadataEntry`
- `Commands`와 `Events` 네임스페이스는 비어 있다.

### 입력 간 차이

- 스펙 XML의 `revision`은 `5`이지만, SDK XML의 `0xFFFD` 값과 생성된 `kRevision`은 `3`이다.
- 스펙 XML은 `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 `persistence="fixed"`를 명시하지만, 제공된 SDK XML에는 해당 표기가 없다.
- 스펙의 `MeasuredValue`와 `MaxMeasuredValue`에는 다른 속성을 참조하는 범위 제약이 있다. SDK XML에는 표에 기재된 정적 한계가 정의되어 있으며, 속성 간 범위 검증은 구현에서도 수행한다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h` | 클래스, `Config`, 측정값 갱신 및 조회 API 선언 |
| `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp` | 생성 시 검증, 속성 읽기, 속성 목록 구성, 측정값 갱신 |
| `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h` | endpoint 기반 조회 및 갱신 헬퍼 선언 |
| `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp` | ZAP/Codegen 등록, 해제, 기본값 로딩 구현 |

### 클래스와 초기 설정

`RelativeHumidityMeasurementCluster`는 `DefaultServerCluster`를 상속하며, `chip::app::Clusters` 네임스페이스에 정의된다.

생성자는 두 가지 형태이다.

```cpp
explicit RelativeHumidityMeasurementCluster(EndpointId endpointId);
RelativeHumidityMeasurementCluster(EndpointId endpointId, const Config & config);
```

`Config`의 구성은 다음과 같다.

| 멤버/API | 의미 |
|---|---|
| `minMeasuredValue` | `DataModel::Nullable<uint16_t>` 형식의 최소 측정값 |
| `maxMeasuredValue` | `DataModel::Nullable<uint16_t>` 형식의 최대 측정값 |
| `mOptionalAttributeSet` | 선택 속성 활성화 상태 |
| `mTolerance` | 기본값이 `0`인 허용 오차 |
| `WithTolerance(uint16_t value)` | `mTolerance` 설정 및 `Tolerance::Id` 활성화 |

`OptionalAttributeSet`은 `RelativeHumidityMeasurement::Attributes::Tolerance::Id`를 대상으로 한다. 기본 구성에서 범위 값과 초기 측정값은 null이다.

생성자는 `VerifyOrDie`로 다음을 검증한다.

- `minMeasuredValue`가 null이 아니면 `9999` 이하이다.
- 두 범위 값이 모두 null이 아니면 `maxMeasuredValue >= minMeasuredValue + 1`이다.
- `maxMeasuredValue`가 null이 아니면 `10000` 이하이다.
- `Tolerance`가 활성화되어 있으면 `mTolerance <= 2048`이다.

`MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`는 시작 시 설정되며 런타임에 변경할 수 없다.

### 속성 읽기와 목록

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 값 |
|---|---|
| `ClusterRevision` | `RelativeHumidityMeasurement::kRevision` |
| `FeatureMap` | `uint32_t` 값 `0` |
| `MeasuredValue` | `mMeasuredValue` |
| `MinMeasuredValue` | `mMinMeasuredValue` |
| `MaxMeasuredValue` | `mMaxMeasuredValue` |
| `Tolerance` | `mTolerance` |

그 외 속성 ID에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용해 `kMandatoryMetadata`와 선택 속성 `Tolerance::kMetadataEntry`를 결합한다. 선택 속성 포함 여부는 `mOptionalAttributeSet`으로 결정한다.

### 측정값 갱신과 조회

```cpp
CHIP_ERROR SetMeasuredValue(DataModel::Nullable<uint16_t> measuredValue);
```

`SetMeasuredValue`는 null을 허용한다. null이 아닌 값은 `IsValueInHumidityRange`로 다음 조건을 검증한다.

- `kMeasuredValueMax`, 즉 `10000` 이하이다.
- 최소값이 null이 아니면 해당 최소값 이상이다.
- 최대값이 null이 아니면 해당 최대값 이하이다.

범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다. 유효한 값은 `SetAttributeValue(mMeasuredValue, measuredValue, MeasuredValue::Id)`로 반영하고 `CHIP_NO_ERROR`를 반환한다.

조회 API는 다음과 같다.

- `GetMeasuredValue()`
- `GetMinMeasuredValue()`
- `GetMaxMeasuredValue()`

### ZAP/Codegen 통합

`CodegenIntegration.cpp`는 다음 개수로 `gServers`를 구성한다.

- `kRelativeHumidityFixedClusterCount`: `RelativeHumidityMeasurement::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kRelativeHumidityMaxClusterCount`: `kRelativeHumidityFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`

각 항목은 `LazyRegisteredServerCluster<RelativeHumidityMeasurementCluster>`이다.

`IntegrationDelegate::CreateRegistration`은 다음 순서로 인스턴스를 생성한다.

1. `MinMeasuredValue::GetDefaultOr`와 `MaxMeasuredValue::GetDefaultOr`로 Ember attribute store에서 기본값을 읽는다. 기본값이 없으면 `DataModel::NullNullable`을 사용한다.
2. 두 값이 모두 null이 아니면서 `maxMeasuredValue < minMeasuredValue + 1`이면 두 값을 모두 null로 바꾼다. 이는 `0/0`과 같은 잘못된 기본 범위를 처리한다.
3. `optionalAttributeBits`에 `Tolerance::Id`가 설정되어 있으면 `Tolerance::GetDefaultOr`로 값을 읽는다. 기본값은 `0`이며, `config.WithTolerance(tolerance)`로 적용한다.
4. `gServers[clusterInstanceIndex].Create(endpointId, config)`를 호출하고 등록 정보를 반환한다.

등록 수명주기는 다음 콜백이 담당한다.

| 함수 | 동작 |
|---|---|
| `MatterRelativeHumidityMeasurementClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterRelativeHumidityMeasurementClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `IntegrationDelegate::FindRegistration` | 생성된 인스턴스를 반환하며, 미생성 상태이면 `nullptr` 반환 |
| `IntegrationDelegate::ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

초기 등록에는 `fetchFeatureMap = false`, `fetchOptionalAttributes = true`가 지정된다.

### endpoint 기반 헬퍼

`chip::app::Clusters::RelativeHumidityMeasurement` 네임스페이스에서 제공한다.

```cpp
RelativeHumidityMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);
CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<uint16_t> measuredValue);
```

- `FindClusterOnEndpoint`는 등록된 인스턴스를 반환하며, 찾지 못하면 `nullptr`를 반환한다.
- `SetMeasuredValue`는 인스턴스를 찾지 못하면 `CHIP_ERROR_NOT_FOUND`를 반환하고, 찾으면 해당 인스턴스의 `SetMeasuredValue`에 위임한다.

## 관련 문서

### 사용 가이드

출처: `src/app/clusters/relative-humidity-measurement-server/README.md`

문서는 다음 사용 흐름을 설명한다.

1. `.cpp` 파일의 전역 또는 정적 범위에서 `RegisteredServerCluster`를 선언한다.
2. 범위와 선택 속성 `Tolerance`가 필요하면 생성 시 `Config`를 전달한다.
3. 애플리케이션 초기화에서 `CodegenDataModelProvider::Instance().Registry().Register`로 등록한다.
4. 새 센서 측정값은 Matter task context에서 `SetMeasuredValue`로 전달한다. 별도 스레드에서는 `ScheduleWork`를 사용한다.

문서의 범위 및 허용 오차 구성 코드는 다음과 같다.

```cpp
RelativeHumidityMeasurementCluster::Config config;
config.minMeasuredValue = DataModel::MakeNullable(uint16_t(0));
config.maxMeasuredValue = DataModel::MakeNullable(uint16_t(10000));
config.WithTolerance(100);
auto cluster = RelativeHumidityMeasurementCluster(endpointId, config);
```

ZAP/Codegen 방식에서는 호환 계층이 자동으로 클러스터를 생성하며, 다음 헬퍼로 측정값을 전달할 수 있다.

```cpp
#include <app/clusters/relative-humidity-measurement-server/CodegenIntegration.h>

CHIP_ERROR err = chip::app::Clusters::RelativeHumidityMeasurement::SetMeasuredValue(
    endpointId, chip::app::DataModel::MakeNullable(uint16_t(newValue)));
```

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
