---
entity: Temperature Measurement
ids: ['0x0402']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.h', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-measurement-server/README.md', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp', 'data_model/1.7/clusters/TemperatureMeasurement.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

`Temperature Measurement`는 온도 측정값을 구성하고 온도 측정값을 보고하기 위한 클러스터입니다.

- 클러스터 ID: `0x0402`
- 도메인: `Measurement & Sensing`
- PICS 코드: `TMP`
- 범위: `Endpoint`
- 역할: `application`
- 계층: `base`
- 클러스터 revision: `6`
- 서버 및 클라이언트 지원: `true`

## 스펙

### 클러스터 정보

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Temperature Measurement Cluster` |
| 클러스터 ID | `0x0402` |
| Revision | `6` |
| PICS 코드 | `TMP` |

### 속성

| ID | 이름 | 타입 | 접근 | 품질 | 적합성 | 제약 |
|---|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `temperature` | 읽기, `view` | nullable | 필수 | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 |
| `0x0001` | `MinMeasuredValue` | `temperature` | 읽기, `view` | nullable, `persistence="fixed"` | 필수 | `-27315` 이상, `32766` 이하 |
| `0x0002` | `MaxMeasuredValue` | `temperature` | 읽기, `view` | nullable, `persistence="fixed"` | 필수 | `MinMeasuredValue + 1` 이상 |
| `0x0003` | `Tolerance` | `uint16` | 읽기, `view` | `persistence="fixed"` | 선택 | 기본값 `0`, 최대 `2048` |

`Temperature Measurement`에는 명령과 이벤트가 정의되어 있지 않습니다.

### Revision history

| Revision | Summary |
|---|---|
| `1` | Mandatory global `ClusterRevision` attribute added |
| `2` | CCB 2241 2370 |
| `3` | CCB 2823 |
| `4` | New data model format and notation |
| `5` | Removed P quality |
| `6` | Added F quality to `MinMeasuredValue`, `MaxMeasuredValue` and `Tolerance` attributes |

## SDK 정의

SDK 데이터 모델 정의는 `src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml`에 있습니다.

```xml
<cluster>
  <name>Temperature Measurement</name>
  <domain>Measurement &amp; Sensing</domain>
  <description>Attributes and commands for configuring the measurement of temperature, and reporting temperature measurements.</description>
  <code>0x0402</code>
  <define>TEMPERATURE_MEASUREMENT_CLUSTER</define>
  <client tick="false" init="false">true</client>
  <server tick="false" init="false">true</server>
</cluster>
```

### SDK 속성 정의

```xml
<attribute side="server" code="0x0000" name="MeasuredValue"
           define="TEMP_MEASURED_VALUE" type="temperature"
           min="-27315" isNullable="true"/>

<attribute side="server" code="0x0001" name="MinMeasuredValue"
           define="TEMP_MIN_MEASURED_VALUE" type="temperature"
           min="-27315" max="0x7ffe" isNullable="true"/>

<attribute side="server" code="0x0002" name="MaxMeasuredValue"
           define="TEMP_MAX_MEASURED_VALUE" type="temperature"
           min="-27314" isNullable="true"/>

<attribute side="server" code="0x0003" name="Tolerance"
           define="TEMP_TOLERANCE" type="int16u"
           max="0x0800" default="0" optional="true">
  <optionalConform/>
</attribute>
```

## 구현

구현은 `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h` 및 `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp`에 있습니다.

### `TemperatureMeasurementCluster`

`TemperatureMeasurementCluster`는 `DefaultServerCluster`를 상속합니다.

```cpp
class TemperatureMeasurementCluster : public DefaultServerCluster
{
public:
    using OptionalAttributeSet = app::OptionalAttributeSet<TemperatureMeasurement::Attributes::Tolerance::Id>;

    struct StartupConfiguration
    {
        DataModel::Nullable<int16_t> minMeasuredValue{};
        DataModel::Nullable<int16_t> maxMeasuredValue{};
        uint16_t tolerance{};
    };

    TemperatureMeasurementCluster(EndpointId endpointId, const OptionalAttributeSet & optionalAttributeSet,
                                  const StartupConfiguration & config);

    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                AttributeValueEncoder & encoder) override;
    CHIP_ERROR Attributes(const ConcreteClusterPath & path,
                          ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

    CHIP_ERROR SetMeasuredValue(DataModel::Nullable<int16_t> measuredValue);
    DataModel::Nullable<int16_t> GetMeasuredValue() const { return mMeasuredValue; }

    CHIP_ERROR SetMeasuredValueRange(DataModel::Nullable<int16_t> minMeasuredValue,
                                     DataModel::Nullable<int16_t> maxMeasuredValue);
    DataModel::Nullable<int16_t> GetMinMeasuredValue() const { return mMinMeasuredValue; }
    DataModel::Nullable<int16_t> GetMaxMeasuredValue() const { return mMaxMeasuredValue; }
};
```

주요 멤버는 다음과 같습니다.

```cpp
const OptionalAttributeSet mOptionalAttributeSet;
DataModel::Nullable<int16_t> mMeasuredValue{};
DataModel::Nullable<int16_t> mMinMeasuredValue{};
DataModel::Nullable<int16_t> mMaxMeasuredValue{};
uint16_t mTolerance{};
```

### 속성 읽기

`ReadAttribute`는 다음 속성을 처리합니다.

- `ClusterRevision`
- `FeatureMap`
- `MeasuredValue`
- `MinMeasuredValue`
- `MaxMeasuredValue`
- `Tolerance`

`FeatureMap`은 `0`으로 인코딩됩니다. 지원되지 않는 속성은 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환합니다.

### 값 및 범위 검증

구현에서 사용하는 제약 상수는 다음과 같습니다.

```cpp
constexpr int16_t kMinMeasuredValueRange = -27315;
constexpr int16_t kMaxMeasuredValueRange = 32766;
constexpr uint16_t kMaxTolerance = 2048;
```

생성 시 다음 조건을 검증합니다.

- `minMeasuredValue`가 null이 아니면 `-27315` 이상 `32766` 이하이어야 합니다.
- `maxMeasuredValue`가 null이 아니면 `minMeasuredValue + 1` 이상이어야 합니다.
- `Tolerance`가 활성화되어 있으면 `tolerance`는 `2048` 이하이어야 합니다.

`SetMeasuredValue`는 설정할 값이 null이 아닌 경우 현재 `mMinMeasuredValue` 및 `mMaxMeasuredValue` 범위를 검증합니다. 범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환합니다.

`SetMeasuredValueRange`는 새로운 `minMeasuredValue` 및 `maxMeasuredValue`를 검증한 후 `MinMeasuredValue`와 `MaxMeasuredValue`를 갱신합니다.

### Codegen 통합

통합 선언은 `src/app/clusters/temperature-measurement-server/CodegenIntegration.h`에 있습니다.

```cpp
TemperatureMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);

CHIP_ERROR SetMeasuredValue(EndpointId endpointId,
                            DataModel::Nullable<int16_t> measuredValue);

CHIP_ERROR SetMeasuredValueRange(EndpointId endpointId,
                                 DataModel::Nullable<int16_t> minMeasuredValue,
                                 DataModel::Nullable<int16_t> maxMeasuredValue);
```

구현은 `src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp`에 있습니다.

`MatterTemperatureMeasurementClusterInitCallback`은 다음 설정으로 서버 클러스터를 등록합니다.

```cpp
{
    .endpointId                = endpointId,
    .clusterId                 = TemperatureMeasurement::Id,
    .fixedClusterInstanceCount = kTemperatureMeasurementFixedClusterCount,
    .maxClusterInstanceCount   = kTemperatureMeasurementMaxClusterCount,
    .fetchFeatureMap           = false,
    .fetchOptionalAttributes   = true,
}
```

`MatterTemperatureMeasurementClusterShutdownCallback`은 서버 클러스터를 등록 해제합니다.

`FindClusterOnEndpoint`는 지정된 `EndpointId`에서 `TemperatureMeasurementCluster`를 검색합니다. 클러스터를 찾지 못하면 `nullptr`를 반환하며, `SetMeasuredValue`와 `SetMeasuredValueRange`는 이 경우 `CHIP_ERROR_INVALID_ARGUMENT`를 반환합니다.

## 예시

`MeasuredValue`는 더 이상 Accessors를 통해 설정할 수 없습니다. 다음과 같이 `app::Clusters::TemperatureMeasurement::SetMeasuredValue`를 사용합니다.

### 이전 방식

```cpp
app::Clusters::TemperatureMeasurement::Attributes::MeasuredValue::Set(
    1, static_cast<int16_t>(1000));
```

### 현재 방식

```cpp
CHIP_ERROR err =
    app::Clusters::TemperatureMeasurement::SetMeasuredValue(
        1, static_cast<int16_t>(1000));

if (err == CHIP_NO_ERROR)
{
    // SetMeasuredValue() succeeded
}
else
{
    // SetMeasuredValue() failed
}
```

## 관련 문서

- `data_model/1.7/clusters/TemperatureMeasurement.xml`
- `src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml`
- `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h`
- `src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp`
- `src/app/clusters/temperature-measurement-server/CodegenIntegration.h`
- `src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp`
- `src/app/clusters/temperature-measurement-server/README.md`