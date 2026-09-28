---
entity: Relative Humidity Measurement
ids: ['0x0405']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h', 'src/app/clusters/relative-humidity-measurement-server/README.md', 'data_model/1.7/clusters/WaterContentMeasurement.xml', 'zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Relative Humidity Measurement 클러스터는 상대 습도의 측정을 구성하고 상대 습도 측정을 보고하기 위한 속성과 명령을 정의합니다. 클러스터 코드: 0x0405.

## 스펙
```xml
<cluster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="types types.xsd cluster cluster.xsd" name="Water Content Measurement Clusters" revision="5">
  <attributes>
    <attribute id="0x0000" name="MeasuredValue" type="uint16">
      <access read="true" readPrivilege="view"/>
      <mandatoryConform/>
    </attribute>
    <attribute id="0x0001" name="MinMeasuredValue" type="uint16">
      <access read="true" readPrivilege="view"/>
      <mandatoryConform/>
      <constraint>
        <max value="9999"/>
      </constraint>
    </attribute>
    <attribute id="0x0002" name="MaxMeasuredValue" type="uint16">
      <access read="true" readPrivilege="view"/>
      <mandatoryConform/>
      <constraint>
        <between>
          <from>
            <compute>
              <operation>add</operation>
              <left>
                <attribute name="MinMeasuredValue"/>
              </left>
              <right value="1"/>
            </compute>
          </from>
          <to value="10000"/>
        </between>
      </constraint>
    </attribute>
    <attribute id="0x0003" name="Tolerance" type="uint16">
      <access read="true" readPrivilege="view"/>
      <optionalConform/>
      <constraint>
        <max value="2048"/>
      </constraint>
    </attribute>
  </attributes>
</cluster>
```

## SDK 정의
`RelativeHumidityMeasurementCluster` 관련 구성 요소 및 속성을 정의합니다.

### Cluster 및 Attribute 정의
```cpp
namespace chip::app::Clusters {
class RelativeHumidityMeasurementCluster : public DefaultServerCluster {
public:
    using OptionalAttributeSet = app::OptionalAttributeSet<RelativeHumidityMeasurement::Attributes::Tolerance::Id>;
    
    ... // 기타 정의
};

namespace RelativeHumidityMeasurement {
inline constexpr uint32_t kRevision = 3;

namespace Attributes {
namespace MeasuredValue {
inline constexpr DataModel::AttributeEntry kMetadataEntry(MeasuredValue::Id, BitFlags<DataModel::AttributeQualityFlags>(),
                                                          Access::Privilege::kView, std::nullopt);
}
...
} // namespace Attributes
```

## 구현
클러스터 구현 코드와 관련된 파일 및 메서드 정의를 포함합니다.

### RelativeHumidityMeasurementCluster.cpp
```cpp
DataModel::ActionReturnStatus RelativeHumidityMeasurementCluster::ReadAttribute(const DataModel::ReadAttributeRequest & request, AttributeValueEncoder & encoder) {
    switch (request.path.mAttributeId) {
    case MeasuredValue::Id:
        return encoder.Encode(mMeasuredValue);
    ...
    }
}

CHIP_ERROR RelativeHumidityMeasurementCluster::SetMeasuredValue(DataModel::Nullable<uint16_t> measuredValue) {
    ...
}
```

### CodegenIntegration
```cpp
namespace chip::app::Clusters::RelativeHumidityMeasurement {
RelativeHumidityMeasurementCluster * FindClusterOnEndpoint(EndpointId endpointId);
CHIP_ERROR SetMeasuredValue(EndpointId endpointId, DataModel::Nullable<uint16_t> measuredValue);
}
```

## 예시
사용 예시는 다음과 같습니다:

### 1. 클러스터 인스턴스화
```cpp
chip::app::Clusters::RelativeHumidityMeasurementCluster::Config gHumidityConfig;
gHumidityConfig.minMeasuredValue = chip::app::DataModel::MakeNullable(uint16_t(0));
gHumidityConfig.maxMeasuredValue = chip::app::DataModel::MakeNullable(uint16_t(10000));
gHumidityConfig.WithTolerance(100);
chip::app::RegisteredServerCluster<chip::app::Clusters::RelativeHumidityMeasurementCluster> gHumidityCluster(kYourEndpointId, gHumidityConfig);
```

### 2. 새 센서 측정값 푸시
```cpp
void OnSensorReading(uint16_t newHumidity) {
    chip::app::Clusters::RelativeHumidityMeasurementCluster * cluster = gHumidityCluster.Get();
    if (cluster) {
        CHIP_ERROR err = cluster->SetMeasuredValue(chip::app::DataModel::MakeNullable(newHumidity));
        // err 처리
    }
}
```

## 관련 문서
- [Relative Humidity Measurement Specification](data_model/1.7/clusters/WaterContentMeasurement.xml)
- [README for Relative Humidity Measurement Cluster](src/app/clusters/relative-humidity-measurement-server/README.md)
- [Cluster Metadata Definitions](zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h)