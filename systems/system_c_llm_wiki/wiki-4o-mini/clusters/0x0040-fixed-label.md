---
entity: Fixed Label
ids: ['0x0040']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml', 'src/app/clusters/fixed-label-server/FixedLabelCluster.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.h', 'src/app/clusters/fixed-label-server/CodegenIntegration.cpp', 'data_model/1.7/clusters/FixedLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
The Fixed Label Cluster provides a feature for the device to tag an endpoint with zero or more read only labels.

## 스펙
```xml
<cluster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="types types.xsd cluster cluster.xsd" id="0x0040" name="Fixed Label Cluster" revision="1">
  <revisionHistory>
    <revision revision="1" summary="Initial revision"/>
  </revisionHistory>
  <clusterIds>
    <clusterId id="0x0040" name="Fixed Label"/>
  </clusterIds>
  <classification hierarchy="derived" baseCluster="Label" role="utility" picsCode="FLABEL" scope="Endpoint"/>
  <attributes>
    <attribute id="0x0000" name="LabelList" type="list" default="empty">
      <entry type="LabelStruct"/>
      <access read="true" readPrivilege="view"/>
      <quality persistence="nonVolatile"/>
      <mandatoryConform/>
    </attribute>
  </attributes>
</cluster>
```

## SDK 정의
### LabelStruct
```xml
<struct name="LabelStruct">
    <cluster code="0x0040"/>
    <cluster code="0x0041"/>
    <item fieldId="0" name="Label" type="char_string" length="16"/>
    <item fieldId="1" name="Value" type="char_string" length="16"/>
</struct>
```

## 구현
### FixedLabelCluster.cpp
```cpp
namespace chip::app::Clusters {

using namespace FixedLabel::Attributes;

namespace {

CHIP_ERROR ReadLabelList(EndpointId endpoint, AttributeValueEncoder & encoder, DeviceLayer::DeviceInfoProvider & provider)
{
    AutoRelease it(provider.IterateFixedLabel(endpoint));
    VerifyOrReturnValue(!it.IsNull(), encoder.EncodeEmptyList());

    return encoder.EncodeList([&it](const auto & encod) -> CHIP_ERROR {
        FixedLabel::Structs::LabelStruct::Type fixedlabel;
        while (it->Next(fixedlabel))
        {
            ReturnErrorOnFailure(encod.Encode(fixedlabel));
        }
        return CHIP_NO_ERROR;
    });
}

} // namespace

FixedLabelCluster::FixedLabelCluster(EndpointId endpoint, DeviceLayer::DeviceInfoProvider & deviceInfoProvider) :
    DefaultServerCluster({ endpoint, FixedLabel::Id }), mDeviceInfoProvider(deviceInfoProvider)
{}

DataModel::ActionReturnStatus FixedLabelCluster::ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                               AttributeValueEncoder & encoder)
{
    switch (request.path.mAttributeId)
    {
    case LabelList::Id:
        return ReadLabelList(mPath.mEndpointId, encoder, mDeviceInfoProvider);
    case ClusterRevision::Id:
        return encoder.Encode(FixedLabel::kRevision);
    case FeatureMap::Id:
        return encoder.Encode<uint32_t>(0);
    default:
        return Protocols::InteractionModel::Status::UnsupportedAttribute;
    }
}

CHIP_ERROR FixedLabelCluster::Attributes(const ConcreteClusterPath & path,
                                         ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder)
{
    AttributeListBuilder listBuilder(builder);
    return listBuilder.Append(Span(FixedLabel::Attributes::kMandatoryMetadata), {});
}

} // namespace chip::app::Clusters
```

### FixedLabelCluster.h
```cpp
#pragma once

#include <app/server-cluster/DefaultServerCluster.h>
#include <platform/DeviceInfoProvider.h>

namespace chip::app::Clusters {

class FixedLabelCluster : public DefaultServerCluster
{
public:
    FixedLabelCluster(EndpointId endpoint, DeviceLayer::DeviceInfoProvider & deviceInfoProvider);

    // Server cluster implementation
    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                AttributeValueEncoder & encoder) override;
    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

private:
    DeviceLayer::DeviceInfoProvider & mDeviceInfoProvider;
};

} // namespace chip::app::Clusters
```

### CodegenIntegration.cpp
```cpp
void MatterFixedLabelClusterInitCallback(EndpointId endpointId)
{
    IntegrationDelegate integrationDelegate;

    CodegenClusterIntegration::RegisterServer(
        {
            .endpointId                = endpointId,
            .clusterId                 = FixedLabel::Id,
            .fixedClusterInstanceCount = kFixedLabelFixedClusterCount,
            .maxClusterInstanceCount   = kFixedLabelMaxClusterCount,
            .fetchFeatureMap           = false,
            .fetchOptionalAttributes   = false,
        },
        integrationDelegate);
}

void MatterFixedLabelClusterShutdownCallback(EndpointId endpointId, MatterClusterShutdownType shutdownType)
{
    IntegrationDelegate integrationDelegate;

    CodegenClusterIntegration::UnregisterServer(
        {
            .endpointId                = endpointId,
            .clusterId                 = FixedLabel::Id,
            .fixedClusterInstanceCount = kFixedLabelFixedClusterCount,
            .maxClusterInstanceCount   = kFixedLabelMaxClusterCount,
        },
        integrationDelegate, shutdownType);
}
```

## 예시
No specific examples provided.

## 관련 문서
- [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
- [CHIP Specification](data_model/1.7/clusters/FixedLabel-Cluster.xml)