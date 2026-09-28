---
entity: Temperature Measurement
ids: ['0x0402']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/temperature-measurement-cluster.xml', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.h', 'src/app/clusters/temperature-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-measurement-server/README.md', 'src/app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.cpp', 'data_model/1.7/clusters/TemperatureMeasurement.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Temperature Measurement 클러스터는 온도 측정의 구성을 위한 속성과 명령을 제공하며, 온도 측정값을 보고합니다.

## 스펙
### Temperature Measurement Cluster
- **ID**: 0x0402
- **설명**: Attributes and commands for configuring the measurement of temperature, and reporting temperature measurements.

#### 속성
- **MeasuredValue** (0x0000): 온도
- **MinMeasuredValue** (0x0001): 최소 온도
- **MaxMeasuredValue** (0x0002): 최대 온도
- **Tolerance** (0x0003): 허용 오차

## SDK 정의
### TemperatureMeasurementCluster.h
```cpp
#pragma once

#include <app-common/zap-generated/attributes/Accessors.h>
#include <app/server-cluster/DefaultServerCluster.h>
#include <app/server-cluster/OptionalAttributeSet.h>
#include <clusters/TemperatureMeasurement/Attributes.h>
#include <clusters/TemperatureMeasurement/Metadata.h>

namespace chip::app::Clusters {

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
    CHIP_ERROR SetMeasuredValue(DataModel::Nullable<int16_t> measuredValue);
    DataModel::Nullable<int16_t> GetMeasuredValue() const { return mMeasuredValue; }

protected:
    const OptionalAttributeSet mOptionalAttributeSet;
    DataModel::Nullable<int16_t> mMeasuredValue{};
    DataModel::Nullable<int16_t> mMinMeasuredValue{};
    DataModel::Nullable<int16_t> mMaxMeasuredValue{};
    uint16_t mTolerance{};
};

} // namespace chip::app::Clusters
```

### TemperatureMeasurementCluster.cpp
```cpp
#include <app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h>
#include <app/server-cluster/AttributeListBuilder.h>
#include <clusters/TemperatureMeasurement/Metadata.h>

namespace chip::app::Clusters {

DataModel::ActionReturnStatus TemperatureMeasurementCluster::ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                                           AttributeValueEncoder & encoder)
{
    switch (request.path.mAttributeId)
    {
    case MeasuredValue::Id:
        return encoder.Encode(mMeasuredValue);
    case MinMeasuredValue::Id:
        return encoder.Encode(mMinMeasuredValue);
    case MaxMeasuredValue::Id:
        return encoder.Encode(mMaxMeasuredValue);
    case Tolerance::Id:
        return encoder.Encode(mTolerance);
    default:
        return Protocols::InteractionModel::Status::UnsupportedAttribute;
    }
}

CHIP_ERROR TemperatureMeasurementCluster::SetMeasuredValue(DataModel::Nullable<int16_t> measuredValue)
{
    SetAttributeValue(mMeasuredValue, measuredValue, MeasuredValue::Id);
    return CHIP_NO_ERROR;
}

} // namespace chip::app::Clusters
```

## 구현
### CodegenIntegration.h
```cpp
#pragma once

#include <app/clusters/temperature-measurement-server/TemperatureMeasurementCluster.h>

namespace chip::app::Clusters::TemperatureMeasurement {

TemperatureMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);
CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<int16_t> measuredValue);

} // namespace chip::app::Clusters::TemperatureMeasurement
```

### CodegenIntegration.cpp
```cpp
#include <app/clusters/temperature-measurement-server/CodegenIntegration.h>

namespace chip::app::Clusters::TemperatureMeasurement {

TemperatureMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId)
{
    // Implementation here ...
}

CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<int16_t> measuredValue)
{
    auto temperatureMeasurement = FindClusterOnEndpoint(endpointId);
    return temperatureMeasurement->SetMeasuredValue(measuredValue);
}

} // namespace chip::app::Clusters::TemperatureMeasurement
```

## 예시
온도 측정 값을 설정하는 방식은 다음과 같습니다.

### 이전 방식 (Accessors 사용)
```cpp
app::Clusters::TemperatureMeasurement::Attributes::MeasuredValue::Set(1, static_cast<int16_t>(1000));
```

### 현재 방식 (코드 기반 접근)
```cpp
CHIP_ERROR err = app::Clusters::TemperatureMeasurement::SetMeasuredValue(1, static_cast<int16_t>(1000));
if (err == CHIP_NO_ERROR) {
    // SetMeasuredValue() succeeded
} else {
    // SetMeasuredValue() failed
}
```

## 관련 문서
- [Temperature Measurement Specification](data_model/1.7/clusters/TemperatureMeasurement.xml)