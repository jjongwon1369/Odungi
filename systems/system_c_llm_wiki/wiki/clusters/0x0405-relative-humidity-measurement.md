---
entity: Relative Humidity Measurement
ids: ['0x0405']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h', 'src/app/clusters/relative-humidity-measurement-server/README.md', 'data_model/1.7/clusters/WaterContentMeasurement.xml', 'zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Relative Humidity Measurement

## 개요

- 클러스터 이름: `Relative Humidity Measurement`
- 클러스터 ID: `0x0405`
- 도메인: `Measurement & Sensing`
- PICS 코드: `RH`
- 역할: application
- 범위: Endpoint
- 설명: 상대 습도 측정을 구성하고 상대 습도 측정값을 보고하기 위한 Attributes 및 commands를 제공합니다.
- Server 및 Client가 지원됩니다.
  - Client: `tick="false"`, `init="false"`
  - Server: `tick="false"`, `tickFrequency="half"`, `init="false"`

## 스펙

스펙 파일: `data_model/1.7/clusters/WaterContentMeasurement.xml`

- 스펙 클러스터 이름: `Water Content Measurement Clusters`
- 스펙 revision: `5`
- 클러스터 ID: `0x0405`
- 클러스터 이름: `Relative Humidity Measurement`
- PICS 코드: `RH`

### Attributes

| ID | 이름 | 타입 | 접근 | 적합성 | 품질 및 제약 |
|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `uint16` | read, `readPrivilege="view"` | mandatory | nullable; `MinMeasuredValue` 이상 `MaxMeasuredValue` 이하 |
| `0x0001` | `MinMeasuredValue` | `uint16` | read, `readPrivilege="view"` | mandatory | nullable, fixed; 최대 `9999` |
| `0x0002` | `MaxMeasuredValue` | `uint16` | read, `readPrivilege="view"` | mandatory | nullable, fixed; `MinMeasuredValue + 1` 이상 `10000` 이하 |
| `0x0003` | `Tolerance` | `uint16` | read, `readPrivilege="view"` | optional | fixed; 최대 `2048` |

### 글로벌 Attribute

- `0xFFFD`: `ClusterRevision`
- 스펙 revision history에는 `Mandatory global ClusterRevision attribute added`가 포함되어 있습니다.

### Revision history

| Revision | Summary |
|---:|---|
| `1` | Mandatory global ClusterRevision attribute added |
| `2` | CCB 2241 |
| `3` | New data model format and notation |
| `4` | Removed P quality |
| `5` | Added F quality to `MinMeasuredValue`, `MaxMeasuredValue` and `Tolerance` attributes |

## SDK 정의

SDK 템플릿 파일: `src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml`

- 클러스터 이름: `Relative Humidity Measurement`
- 도메인: `Measurement & Sensing`
- 클러스터 코드: `0x0405`
- define: `RELATIVE_HUMIDITY_MEASUREMENT_CLUSTER`
- 글로벌 Attribute:
  - code: `0xFFFD`
  - value: `3`

### Attributes 정의

| Side | Code | 이름 | Define | 타입 | Nullable | 제약 | 적합성 |
|---|---|---|---|---|---|---|---|
| server | `0x0000` | `MeasuredValue` | `RELATIVE_HUMIDITY_MEASURED_VALUE` | `int16u` | true | 최대 `10000` | mandatory |
| server | `0x0001` | `MinMeasuredValue` | `RELATIVE_HUMIDITY_MIN_MEASURED_VALUE` | `int16u` | true | 최대 `0x270F` | mandatory |
| server | `0x0002` | `MaxMeasuredValue` | `RELATIVE_HUMIDITY_MAX_MEASURED_VALUE` | `int16u` | true | 최소 `0x0001`, 최대 `0x2710` | mandatory |
| server | `0x0003` | `Tolerance` | `RELATIVE_HUMIDITY_TOLERANCE` | `int16u` | 아니오 | 최대 `0x0800` | optional |

생성된 메타데이터 파일: `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h`

- 생성 대상 클러스터 코드: `1029/0x405`
- 생성된 `kRevision`: `3`
- `Attributes::kMandatoryMetadata`에는 다음 항목이 포함됩니다.
  - `MeasuredValue::kMetadataEntry`
  - `MinMeasuredValue::kMetadataEntry`
  - `MaxMeasuredValue::kMetadataEntry`
- `Tolerance::kMetadataEntry`는 optional attribute로 정의되어 있습니다.
- `Commands` namespace는 비어 있습니다.
- `Events` namespace는 비어 있습니다.

## 구현

구현 파일:

- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h`
- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp`
- `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h`
- `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp`

### `RelativeHumidityMeasurementCluster`

`RelativeHumidityMeasurementCluster`는 `DefaultServerCluster`를 상속합니다.

```cpp
class RelativeHumidityMeasurementCluster : public DefaultServerCluster
```

주요 타입과 설정:

```cpp
using OptionalAttributeSet = app::OptionalAttributeSet<RelativeHumidityMeasurement::Attributes::Tolerance::Id>;
```

```cpp
struct Config
{
    Config() : minMeasuredValue(), maxMeasuredValue(), mOptionalAttributeSet(), mTolerance(0) {}

    Config & WithTolerance(uint16_t value);

    DataModel::Nullable<uint16_t> minMeasuredValue;
    DataModel::Nullable<uint16_t> maxMeasuredValue;
    OptionalAttributeSet mOptionalAttributeSet;
    uint16_t mTolerance;
};
```

### 생성자 제약 검증

구현에서 사용하는 상한:

```cpp
constexpr uint16_t kMinMeasuredValueMax = 9999;
constexpr uint16_t kMeasuredValueMax = 10000;
constexpr uint16_t kMaxTolerance = 2048;
```

생성 시 다음을 검증합니다.

- `minMeasuredValue`가 null이 아니면 `kMinMeasuredValueMax` 이하이어야 합니다.
- `minMeasuredValue`와 `maxMeasuredValue`가 모두 null이 아니면 `maxMeasuredValue`는 `minMeasuredValue + 1` 이상이어야 합니다.
- `maxMeasuredValue`가 null이 아니면 `kMeasuredValueMax` 이하이어야 합니다.
- `Tolerance`가 optional attribute set에 포함된 경우 `config.mTolerance`는 `kMaxTolerance` 이하이어야 합니다.

### Attribute 읽기

`ReadAttribute`는 다음 Attribute를 지원합니다.

- `ClusterRevision::Id`
  - `RelativeHumidityMeasurement::kRevision` 반환
- `FeatureMap::Id`
  - `0` 반환
- `MeasuredValue::Id`
- `MinMeasuredValue::Id`
- `MaxMeasuredValue::Id`
- `Tolerance::Id`

그 외 Attribute ID에는 다음 상태를 반환합니다.

```cpp
Protocols::InteractionModel::Status::UnsupportedAttribute
```

### Attribute 목록

`Attributes`는 다음 mandatory metadata를 사용합니다.

- `MeasuredValue::kMetadataEntry`
- `MinMeasuredValue::kMetadataEntry`
- `MaxMeasuredValue::kMetadataEntry`

optional metadata로 다음 항목을 사용합니다.

- `Tolerance::kMetadataEntry`

### `SetMeasuredValue`

```cpp
CHIP_ERROR SetMeasuredValue(DataModel::Nullable<uint16_t> measuredValue);
```

`measuredValue`가 null이 아닌 경우 다음 조건을 검증합니다.

- `value`는 `10000` 이하이어야 합니다.
- `MinMeasuredValue`가 null이 아니면 `value`는 `MinMeasuredValue` 이상이어야 합니다.
- `MaxMeasuredValue`가 null이 아니면 `value`는 `MaxMeasuredValue` 이하이어야 합니다.

조건을 만족하지 않으면 다음 오류를 반환합니다.

```cpp
CHIP_IM_GLOBAL_STATUS(ConstraintError)
```

검증을 통과하면 다음 방식으로 Attribute를 갱신합니다.

```cpp
SetAttributeValue(mMeasuredValue, measuredValue, MeasuredValue::Id);
```

조회 함수로 다음을 제공합니다.

```cpp
DataModel::Nullable<uint16_t> GetMeasuredValue() const;
DataModel::Nullable<uint16_t> GetMinMeasuredValue() const;
DataModel::Nullable<uint16_t> GetMaxMeasuredValue() const;
```

### Codegen 통합

다음 함수를 제공합니다.

```cpp
RelativeHumidityMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);
CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<uint16_t> measuredValue);
```

`MatterRelativeHumidityMeasurementClusterInitCallback`는 `CodegenClusterIntegration::RegisterServer`를 사용하여 Server cluster를 등록합니다.

등록 설정:

- `clusterId`: `RelativeHumidityMeasurement::Id`
- `fetchFeatureMap`: `false`
- `fetchOptionalAttributes`: `true`
- 고정 인스턴스 수: `kRelativeHumidityFixedClusterCount`
- 최대 인스턴스 수: `kRelativeHumidityMaxClusterCount`

`CreateRegistration`은 Ember attribute store에서 다음 기본값을 읽습니다.

- `MinMeasuredValue::GetDefaultOr`
- `MaxMeasuredValue::GetDefaultOr`
- `Tolerance::GetDefaultOr`

`MinMeasuredValue`와 `MaxMeasuredValue`가 모두 non-null이면서 유효하지 않은 범위를 형성하면 두 값을 모두 null로 설정합니다.

`SetMeasuredValue(EndpointId endpointId, ...)`에서 endpoint에 해당하는 cluster를 찾지 못하면 다음 오류를 반환합니다.

```cpp
CHIP_ERROR_NOT_FOUND
```

## 예시

### Cluster 인스턴스 생성

```cpp
#include <app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h>
#include <app/server-cluster/ServerClusterInterfaceRegistry.h>

// Minimal — no optional attributes
chip::app::RegisteredServerCluster<chip::app::Clusters::RelativeHumidityMeasurementCluster>
    gHumidityCluster(kYourEndpointId);

// With min/max range and optional Tolerance attribute
chip::app::Clusters::RelativeHumidityMeasurementCluster::Config gHumidityConfig;
gHumidityConfig.minMeasuredValue = chip::app::DataModel::MakeNullable(uint16_t(0));
gHumidityConfig.maxMeasuredValue = chip::app::DataModel::MakeNullable(uint16_t(10000));
gHumidityConfig.WithTolerance(100);

chip::app::RegisteredServerCluster<chip::app::Clusters::RelativeHumidityMeasurementCluster>
    gHumidityCluster(kYourEndpointId, gHumidityConfig);
```

### Cluster 등록

```cpp
#include <data-model-providers/codegen/CodegenDataModelProvider.h>

void ApplicationInit()
{
    CHIP_ERROR err = chip::app::CodegenDataModelProvider::Instance().Registry().Register(
        gHumidityCluster.Registration());
    // handle err
}
```

### 센서 측정값 갱신

```cpp
void OnSensorReading(uint16_t newHumidity)
{
    chip::app::Clusters::RelativeHumidityMeasurementCluster * cluster = gHumidityCluster.Get();
    if (cluster)
    {
        CHIP_ERROR err = cluster->SetMeasuredValue(chip::app::DataModel::MakeNullable(newHumidity));
        // handle err
    }
}
```

별도 스레드에서 호출하는 경우 `ScheduleWork`를 사용하도록 문서에 설명되어 있습니다.

### Codegen 호환 계층 사용

```cpp
#include <app/clusters/relative-humidity-measurement-server/CodegenIntegration.h>

CHIP_ERROR err = chip::app::Clusters::RelativeHumidityMeasurement::SetMeasuredValue(
    endpointId, chip::app::DataModel::MakeNullable(uint16_t(newValue)));
```

### `Config`로 범위와 `Tolerance` 설정

```cpp
// Min/max only
RelativeHumidityMeasurementCluster::Config config;
config.minMeasuredValue = DataModel::MakeNullable(uint16_t(0));
config.maxMeasuredValue = DataModel::MakeNullable(uint16_t(10000));
auto cluster = RelativeHumidityMeasurementCluster(endpointId, config);

// With optional Tolerance attribute
RelativeHumidityMeasurementCluster::Config config;
config.minMeasuredValue = DataModel::MakeNullable(uint16_t(0));
config.maxMeasuredValue = DataModel::MakeNullable(uint16_t(10000));
config.WithTolerance(100);
auto cluster = RelativeHumidityMeasurementCluster(endpointId, config);
```

## 관련 문서

- `src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml`
- `data_model/1.7/clusters/WaterContentMeasurement.xml`
- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h`
- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp`
- `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h`
- `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp`
- `src/app/clusters/relative-humidity-measurement-server/README.md`
- `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h`