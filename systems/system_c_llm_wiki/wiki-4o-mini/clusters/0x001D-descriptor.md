---
entity: Descriptor
ids: ['0x001D']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml', 'src/app/clusters/descriptor/DescriptorCluster.h', 'src/app/clusters/descriptor/CodegenIntegration.cpp', 'src/app/clusters/descriptor/DescriptorCluster.cpp', 'data_model/1.7/clusters/Descriptor-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
The Descriptor Cluster is meant to replace the support from the Zigbee Device Object (ZDO) for describing a node, its endpoints and clusters.

## 스펙
### 클러스터 정보
- **클러스터 ID**: 0x001d
- **클러스터 이름**: Descriptor
- **버전**: 3
- **기능**:
  - **TAGLIST**: The TagList attribute is present

### 데이터 타입
- **DeviceTypeStruct**:
  - `DeviceType` (devtype_id)
  - `Revision` (int16u, min=1)

### 속성
- `DeviceTypeList` (0x0000): array of DeviceTypeStruct, minLength=1
- `ServerList` (0x0001): array of cluster_id
- `ClientList` (0x0002): array of cluster_id
- `PartsList` (0x0003): array of endpoint_no
- `TagList` (0x0004): array of SemanticTagStruct, optional, length=6, minLength=1 (requires TAGLIST feature)
- `EndpointUniqueID` (0x0005): char_string, optional, length=32

## SDK 정의
### Header 파일
```cpp
#pragma once

#include <app/server-cluster/DefaultServerCluster.h>
#include <app/server-cluster/OptionalAttributeSet.h>
#include <clusters/Descriptor/AttributeIds.h>
#include <clusters/Descriptor/ClusterId.h>
#include <clusters/shared/Structs.h>
#include <lib/support/BitFlags.h>
#include <lib/support/Span.h>

namespace chip::app::Clusters {

class DescriptorCluster : public DefaultServerCluster {
public:
    using SemanticTag = Globals::Structs::SemanticTagStruct::Type;
    using OptionalAttributesSet = OptionalAttributeSet<Descriptor::Attributes::EndpointUniqueID::Id>;

    DescriptorCluster(EndpointId endpointId, OptionalAttributesSet optionalAttributeSet, Span<const SemanticTag> semanticTags) :
        DefaultServerCluster({ endpointId, Descriptor::Id }), mEnabledOptionalAttributes(optionalAttributeSet),
        mSemanticTags(semanticTags) {}

    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;
    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                AttributeValueEncoder & encoder) override;

protected:
    OptionalAttributesSet mEnabledOptionalAttributes;
    Span<const SemanticTag> mSemanticTags;
};

} // namespace chip::app::Clusters
```

## 구현
### DescriptorCluster.cpp
```cpp
#include <app/clusters/descriptor/DescriptorCluster.h>

namespace chip::app::Clusters {
CHIP_ERROR DescriptorCluster::Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) {
    AttributeListBuilder listBuilder(builder);

    AttributeListBuilder::OptionalAttributeEntry optionalAttributeEntries[] = {
        { !mSemanticTags.empty(), TagList::kMetadataEntry },
        { mEnabledOptionalAttributes.IsSet(EndpointUniqueID::Id), EndpointUniqueID::kMetadataEntry },
    };

    return listBuilder.Append(Span(Attributes::kMandatoryMetadata), Span(optionalAttributeEntries));
}

DataModel::ActionReturnStatus DescriptorCluster::ReadAttribute(const DataModel::ReadAttributeRequest & request, AttributeValueEncoder & encoder) {
    switch (request.path.mAttributeId) {
    case FeatureMap::Id: {
        BitFlags<Descriptor::Feature> features;
        if (!mSemanticTags.empty()) {
            features.Set(Descriptor::Feature::kTagList);
        }
        return encoder.Encode(features);
    }
    // ...
    default:
        return Status::UnsupportedAttribute;
    }
}

} // namespace chip::app::Clusters
```

## 예시
### 초기화 함수
```cpp
void MatterDescriptorClusterInitCallback(EndpointId endpointId) {
    IntegrationDelegate integrationDelegate;

    CodegenClusterIntegration::RegisterServer(
        {
            .endpointId                = endpointId,
            .clusterId                 = Descriptor::Id,
            .fixedClusterInstanceCount = kDescriptorFixedClusterCount,
            .maxClusterInstanceCount   = kDescriptorMaxClusterCount,
            .fetchFeatureMap           = false,
            .fetchOptionalAttributes   = true,
        },
        integrationDelegate);
}
```

## 관련 문서
- [Descriptor-Cluster XML - Spec](data_model/1.7/clusters/Descriptor-Cluster.xml)
- [DescriptorCluster.h - Header File](src/app/clusters/descriptor/DescriptorCluster.h)
- [DescriptorCluster.cpp - Implementation](src/app/clusters/descriptor/DescriptorCluster.cpp)