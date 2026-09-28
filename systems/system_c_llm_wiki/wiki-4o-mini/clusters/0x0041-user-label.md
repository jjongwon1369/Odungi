---
entity: User Label
ids: ['0x0041']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml', 'src/app/clusters/user-label-server/CodegenIntegration.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.h', 'data_model/1.7/clusters/UserLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
The User Label Cluster provides a feature to tag an endpoint with zero or more labels.

## 스펙
```xml
<cluster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="types types.xsd cluster cluster.xsd" id="0x0041" name="User Label Cluster" revision="1">
  <revisionHistory>
    <revision revision="1" summary="Initial revision"/>
  </revisionHistory>
  <clusterIds>
    <clusterId id="0x0041" name="User Label"/>
  </clusterIds>
  <classification hierarchy="derived" baseCluster="Label" role="utility" picsCode="ULABEL" scope="Endpoint"/>
  <attributes>
    <attribute id="0x0000" name="LabelList" type="list" default="empty">
      <entry type="LabelStruct"/>
      <access read="true" write="true" readPrivilege="view" writePrivilege="manage"/>
      <quality persistence="nonVolatile"/>
      <mandatoryConform/>
      <constraint>
        <desc/>
      </constraint>
    </attribute>
  </attributes>
</cluster>
```

## SDK 정의
### 사용 클러스터 정의
```xml
<configurator xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../zcl.xsd">
  <domain name="CHIP"/>
  <cluster>
    <domain>General</domain>
    <name>User Label</name>
    <code>0x0041</code>
    <define>USER_LABEL_CLUSTER</define>
    <description>The User Label Cluster provides a feature to tag an endpoint with zero or more labels.</description>
    <client init="false" tick="false">true</client>
    <server init="false" tick="false">true</server>
    <globalAttribute code="0xFFFD" side="either" value="1"/>
    <attribute side="server" code="0x0000" name="LabelList" define="LABEL_LIST" type="array" entryType="LabelStruct" writable="true">
      <access op="write" privilege="manage"/>
    </attribute>
  </cluster>
</configurator>
```

## 구현
### CodegenIntegration.cpp
```cpp
#include <app/clusters/user-label-server/UserLabelCluster.h>
#include <app/server/Server.h>
#include <app/static-cluster-config/UserLabel.h>
#include <data-model-providers/codegen/ClusterIntegration.h>
#include <data-model-providers/codegen/CodegenDataModelProvider.h>
#include <platform/DeviceInfoProvider.h>

using namespace chip;
using namespace chip::app;
using namespace chip::app::Clusters;
using namespace chip::app::Clusters::UserLabel;
using namespace chip::app::Clusters::UserLabel::Attributes;

namespace {
constexpr size_t kUserLabelFixedClusterCount = UserLabel::StaticApplicationConfig::kFixedClusterConfig.size();
constexpr size_t kUserLabelMaxClusterCount   = kUserLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT;

LazyRegisteredServerCluster<UserLabelCluster> gServers[kUserLabelMaxClusterCount];

class IntegrationDelegate : public CodegenClusterIntegration::Delegate {
public:
    ServerClusterRegistration & CreateRegistration(EndpointId endpointId, unsigned clusterInstanceIndex,
                                                   uint32_t optionalAttributeBits, uint32_t featureMap) override {
        DeviceLayer::DeviceInfoProvider * deviceInfoProvider = DeviceLayer::GetDeviceInfoProvider();
        VerifyOrDie(deviceInfoProvider != nullptr);

        gServers[clusterInstanceIndex].Create(endpointId,
                                              UserLabelCluster::Context{
                                                  .deviceInfoProvider = *deviceInfoProvider,
                                                  .fabricTable        = Server::GetInstance().GetFabricTable(),
                                              });
        return gServers[clusterInstanceIndex].Registration();
    }

    ServerClusterInterface * FindRegistration(unsigned clusterInstanceIndex) override {
        VerifyOrReturnValue(gServers[clusterInstanceIndex].IsConstructed(), nullptr);
        return &gServers[clusterInstanceIndex].Cluster();
    }

    void ReleaseRegistration(unsigned clusterInstanceIndex) override { gServers[clusterInstanceIndex].Destroy(); }
};
} // namespace

void MatterUserLabelClusterInitCallback(EndpointId endpointId) {
    IntegrationDelegate integrationDelegate;

    CodegenClusterIntegration::RegisterServer(
        {
            .endpointId                = endpointId,
            .clusterId                 = UserLabel::Id,
            .fixedClusterInstanceCount = kUserLabelFixedClusterCount,
            .maxClusterInstanceCount   = kUserLabelMaxClusterCount,
            .fetchFeatureMap           = false,
            .fetchOptionalAttributes   = false,
        },
        integrationDelegate);
}

void MatterUserLabelClusterShutdownCallback(EndpointId endpointId, MatterClusterShutdownType shutdownType) {
    IntegrationDelegate integrationDelegate;

    CodegenClusterIntegration::UnregisterServer(
        {
            .endpointId                = endpointId,
            .clusterId                 = UserLabel::Id,
            .fixedClusterInstanceCount = kUserLabelFixedClusterCount,
            .maxClusterInstanceCount   = kUserLabelMaxClusterCount,
        },
        integrationDelegate, shutdownType);
}

void MatterUserLabelPluginServerInitCallback() {}
```

### UserLabelCluster.cpp
```cpp
#include <app/clusters/user-label-server/UserLabelCluster.h>
#include <app/server-cluster/AttributeListBuilder.h>
#include <clusters/UserLabel/Metadata.h>
#include <lib/support/AutoRelease.h>

#include <array>

namespace chip::app::Clusters {

using namespace UserLabel;
using namespace UserLabel::Attributes;

namespace {

CHIP_ERROR ReadLabelList(EndpointId endpoint, AttributeValueEncoder & encoder, DeviceLayer::DeviceInfoProvider & provider) {
    AutoRelease it(provider.IterateUserLabel(endpoint));
    VerifyOrReturnValue(!it.IsNull(), encoder.EncodeEmptyList());

    return encoder.EncodeList([&it](const auto & encod) -> CHIP_ERROR {
        UserLabel::Structs::LabelStruct::Type userlabel;
        while (it->Next(userlabel)) {
            ReturnErrorOnFailure(encod.Encode(userlabel));
        }
        return CHIP_NO_ERROR;
    });
}

/// Matches constraints on a LabelStruct.
bool IsValidLabelEntry(const Structs::LabelStruct::Type & entry) {
    return (entry.label.size() <= UserLabelCluster::kMaxLabelSize) && (entry.value.size() <= UserLabelCluster::kMaxValueSize);
}

CHIP_ERROR WriteLabelList(const ConcreteDataAttributePath & path, AttributeValueDecoder & decoder,
                          DeviceLayer::DeviceInfoProvider & provider) {
    EndpointId endpoint = path.mEndpointId;

    if (!path.IsListItemOperation()) {
        size_t numLabels = 0;
        std::array<Structs::LabelStruct::Type, DeviceLayer::kMaxUserLabelListLength> labels;
        LabelList::TypeInfo::DecodableType decodablelist;

        ReturnErrorOnFailure(decoder.Decode(decodablelist));
        auto iter = decodablelist.begin();
        while (iter.Next()) {
            auto & label = iter.GetValue();
            VerifyOrReturnError(IsValidLabelEntry(label), CHIP_IM_GLOBAL_STATUS(ConstraintError));
            VerifyOrReturnError(numLabels < labels.size(), CHIP_ERROR_NO_MEMORY);
            labels[numLabels++] = label;
        }
        ReturnErrorOnFailure(iter.GetStatus());

        return provider.SetUserLabelList(endpoint, Span(labels.data(), numLabels));
    }

    if (path.mListOp == ConcreteDataAttributePath::ListOperation::AppendItem) {
        Structs::LabelStruct::DecodableType entry;

        ReturnErrorOnFailure(decoder.Decode(entry));
        VerifyOrReturnError(IsValidLabelEntry(entry), CHIP_IM_GLOBAL_STATUS(ConstraintError));

        // Append the single user label entry
        CHIP_ERROR err = provider.AppendUserLabel(endpoint, entry);
        if (err == CHIP_ERROR_NO_MEMORY) {
            return CHIP_IM_GLOBAL_STATUS(ResourceExhausted);
        }

        return err;
    }

    return CHIP_ERROR_UNSUPPORTED_CHIP_FEATURE;
}

} // namespace

DataModel::ActionReturnStatus UserLabelCluster::ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                              AttributeValueEncoder & encoder) {
    switch (request.path.mAttributeId) {
    case LabelList::Id:
        return ReadLabelList(mPath.mEndpointId, encoder, mContext.deviceInfoProvider);
    case ClusterRevision::Id:
        return encoder.Encode(UserLabel::kRevision);
    case FeatureMap::Id:
        return encoder.Encode<uint32_t>(0);
    default:
        return Protocols::InteractionModel::Status::UnsupportedAttribute;
    }
}

DataModel::ActionReturnStatus UserLabelCluster::WriteAttribute(const DataModel::WriteAttributeRequest & request,
                                                               AttributeValueDecoder & decoder) {
    switch (request.path.mAttributeId) {
    case LabelList::Id:
        return NotifyAttributeChangedIfSuccess(LabelList::Id, WriteLabelList(request.path, decoder, mContext.deviceInfoProvider));
    default:
        return Protocols::InteractionModel::Status::UnsupportedWrite;
    }
}

CHIP_ERROR UserLabelCluster::Attributes(const ConcreteClusterPath & path,
                                        ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) {
    AttributeListBuilder listBuilder(builder);
    return listBuilder.Append(Span(UserLabel::Attributes::kMandatoryMetadata), {});
}

CHIP_ERROR UserLabelCluster::Startup(ServerClusterContext & context) {
    ReturnErrorOnFailure(DefaultServerCluster::Startup(context));
    return mContext.fabricTable.AddFabricDelegate(this);
}

void UserLabelCluster::Shutdown(ClusterShutdownType shutdownType) {
    mContext.fabricTable.RemoveFabricDelegate(this);
    DefaultServerCluster::Shutdown(shutdownType);
}

void UserLabelCluster::OnFabricRemoved(const FabricTable & fabricTable, FabricIndex fabricIndex) {
    VerifyOrReturn(mContext.fabricTable.FabricCount() == 0);

    ChipLogProgress(Zcl, "UserLabel: Last Fabric index 0x%x was removed", static_cast<unsigned>(fabricIndex));

    if (CHIP_NO_ERROR != mContext.deviceInfoProvider.ClearUserLabelList(mPath.mEndpointId)) {
        ChipLogError(Zcl, "UserLabel: Failed to clear UserLabelList for endpoint: %d", mPath.mEndpointId);
    }
}

} // namespace chip::app::Clusters
```

### UserLabelCluster.h
```cpp
#pragma once

#include <app/server-cluster/DefaultServerCluster.h>
#include <platform/DeviceInfoProvider.h>

namespace chip::app::Clusters {

class UserLabelCluster : public DefaultServerCluster, public chip::FabricTable::Delegate {
public:
    struct Context {
        DeviceLayer::DeviceInfoProvider & deviceInfoProvider;
        chip::FabricTable & fabricTable;
    };

    UserLabelCluster(EndpointId endpoint, Context && context) :
        DefaultServerCluster({ endpoint, UserLabel::Id }), mContext(std::move(context)){};

    CHIP_ERROR Startup(ServerClusterContext & context) override;
    void Shutdown(ClusterShutdownType type) override;

    void OnFabricRemoved(const FabricTable & fabricTable, FabricIndex fabricIndex) override;

    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                AttributeValueEncoder & encoder) override;
    DataModel::ActionReturnStatus WriteAttribute(const DataModel::WriteAttributeRequest & request,
                                                 AttributeValueDecoder & decoder) override;
    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

    static constexpr size_t kMaxLabelSize = 16;
    static constexpr size_t kMaxValueSize = 16;

private:
    Context mContext;
};

} // namespace chip::app::Clusters
```

## 예시
특정 예시는 제공되지 않았습니다.

## 관련 문서
- [UserLabel-Cluster.spec](data_model/1.7/clusters/UserLabel-Cluster.xml)