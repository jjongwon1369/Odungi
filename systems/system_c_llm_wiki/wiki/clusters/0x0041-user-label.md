---
entity: User Label
ids: ['0x0041']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml', 'src/app/clusters/user-label-server/CodegenIntegration.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.h', 'data_model/1.7/clusters/UserLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# User Label

## 개요

User Label Cluster는 endpoint에 0개 이상의 label을 지정하는 기능을 제공합니다.

- Cluster name: `User Label`
- Cluster ID: `0x0041`
- Define: `USER_LABEL_CLUSTER`
- Domain: `General`
- PICS code: `ULABEL`
- Scope: `Endpoint`
- Revision: `1`
- Classification: `derived`
- Base cluster: `Label`
- Role: `utility`

## 스펙

### 클러스터

| 항목 | 값 |
|---|---|
| Cluster ID | `0x0041` |
| Name | `User Label` |
| Revision | `1` |
| Revision history | `Initial revision` |

### 속성

#### `LabelList`

| 항목 | 값 |
|---|---|
| Attribute ID | `0x0000` |
| Type | `list` |
| Entry type | `LabelStruct` |
| Default | `empty` |
| Read | 지원 |
| Write | 지원 |
| Read privilege | `view` |
| Write privilege | `manage` |
| Persistence | `nonVolatile` |
| Conformance | Mandatory |

## SDK 정의

소스 파일: `src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml`

### 클러스터 정의

```xml
<cluster>
  <domain>General</domain>
  <name>User Label</name>
  <code>0x0041</code>
  <define>USER_LABEL_CLUSTER</define>
  <description>The User Label Cluster provides a feature to tag an endpoint with zero or more labels.</description>
  <client init="false" tick="false">true</client>
  <server init="false" tick="false">true</server>
  <globalAttribute code="0xFFFD" side="either" value="1"/>
</cluster>
```

### 속성 정의

```xml
<attribute
    side="server"
    code="0x0000"
    name="LabelList"
    define="LABEL_LIST"
    type="array"
    entryType="LabelStruct"
    writable="true">
  <access op="write" privilege="manage"/>
</attribute>
```

## 구현

### 파일

- `src/app/clusters/user-label-server/CodegenIntegration.cpp`
- `src/app/clusters/user-label-server/UserLabelCluster.cpp`
- `src/app/clusters/user-label-server/UserLabelCluster.h`

### `UserLabelCluster`

`UserLabelCluster`는 `DefaultServerCluster` 및 `chip::FabricTable::Delegate`를 상속합니다.

```cpp
class UserLabelCluster : public DefaultServerCluster, public chip::FabricTable::Delegate
```

생성 시 다음 `Context`를 사용합니다.

```cpp
struct Context
{
    DeviceLayer::DeviceInfoProvider & deviceInfoProvider;
    chip::FabricTable & fabricTable;
};
```

클러스터 경로는 `endpoint`와 `UserLabel::Id`로 구성됩니다.

```cpp
UserLabelCluster(EndpointId endpoint, Context && context) :
    DefaultServerCluster({ endpoint, UserLabel::Id }), mContext(std::move(context)){};
```

### `LabelList` 읽기

`ReadAttribute`는 다음 속성을 처리합니다.

- `LabelList::Id`
- `ClusterRevision::Id`
- `FeatureMap::Id`

`LabelList::Id`를 읽을 때 `DeviceLayer::DeviceInfoProvider::IterateUserLabel`을 통해 label 목록을 순회합니다.

```cpp
AutoRelease it(provider.IterateUserLabel(endpoint));
VerifyOrReturnValue(!it.IsNull(), encoder.EncodeEmptyList());
```

각 항목은 다음 타입으로 인코딩됩니다.

```cpp
UserLabel::Structs::LabelStruct::Type
```

`ClusterRevision::Id`와 `FeatureMap::Id`의 읽기 동작은 다음과 같습니다.

```cpp
case ClusterRevision::Id:
    return encoder.Encode(UserLabel::kRevision);
case FeatureMap::Id:
    return encoder.Encode<uint32_t>(0);
```

지원하지 않는 속성은 다음 상태를 반환합니다.

```cpp
Protocols::InteractionModel::Status::UnsupportedAttribute
```

### `LabelList` 쓰기

`WriteAttribute`는 `LabelList::Id`에 대한 쓰기를 처리합니다.

```cpp
case LabelList::Id:
    return NotifyAttributeChangedIfSuccess(LabelList::Id, WriteLabelList(request.path, decoder, mContext.deviceInfoProvider));
```

지원하지 않는 쓰기는 다음 상태를 반환합니다.

```cpp
Protocols::InteractionModel::Status::UnsupportedWrite
```

#### 전체 목록 쓰기

`path.IsListItemOperation()`이 `false`이면 전체 목록을 디코딩합니다.

```cpp
std::array<Structs::LabelStruct::Type, DeviceLayer::kMaxUserLabelListLength> labels;
LabelList::TypeInfo::DecodableType decodablelist;
```

디코딩한 목록은 `DeviceLayer::DeviceInfoProvider::SetUserLabelList`로 저장합니다.

```cpp
return provider.SetUserLabelList(endpoint, Span(labels.data(), numLabels));
```

#### 목록 항목 추가

`ConcreteDataAttributePath::ListOperation::AppendItem`인 경우 단일 항목을 디코딩하여 추가합니다.

```cpp
Structs::LabelStruct::DecodableType entry;
```

추가는 다음 함수를 통해 수행됩니다.

```cpp
provider.AppendUserLabel(endpoint, entry);
```

`CHIP_ERROR_NO_MEMORY`가 발생하면 다음 Interaction Model 상태로 변환합니다.

```cpp
CHIP_IM_GLOBAL_STATUS(ResourceExhausted)
```

`AppendItem` 이외의 목록 연산은 다음 오류를 반환합니다.

```cpp
CHIP_ERROR_UNSUPPORTED_CHIP_FEATURE
```

### `LabelStruct` 제약 조건

`LabelStruct` 항목은 `IsValidLabelEntry`로 검증합니다.

```cpp
static constexpr size_t kMaxLabelSize = 16;
static constexpr size_t kMaxValueSize = 16;
```

검증 조건은 다음과 같습니다.

```cpp
return (entry.label.size() <= UserLabelCluster::kMaxLabelSize) &&
       (entry.value.size() <= UserLabelCluster::kMaxValueSize);
```

`label`과 `value`는 모두 빈 값이 허용됩니다. 제약 조건을 위반하면 다음 상태를 반환합니다.

```cpp
CHIP_IM_GLOBAL_STATUS(ConstraintError)
```

### 속성 목록

`Attributes`는 `UserLabel::Attributes::kMandatoryMetadata`를 사용하여 속성 목록을 구성합니다.

```cpp
AttributeListBuilder listBuilder(builder);
return listBuilder.Append(Span(UserLabel::Attributes::kMandatoryMetadata), {});
```

### 시작 및 종료

`Startup`은 `DefaultServerCluster::Startup`을 호출한 뒤 `fabricTable`에 `UserLabelCluster`를 delegate로 추가합니다.

```cpp
ReturnErrorOnFailure(DefaultServerCluster::Startup(context));
return mContext.fabricTable.AddFabricDelegate(this);
```

`Shutdown`에서는 `fabricTable`에서 delegate를 제거한 뒤 기본 클러스터를 종료합니다.

```cpp
mContext.fabricTable.RemoveFabricDelegate(this);
DefaultServerCluster::Shutdown(shutdownType);
```

### Fabric 제거 처리

`OnFabricRemoved`는 마지막 Fabric이 제거된 경우 endpoint의 User Label 데이터를 삭제합니다.

```cpp
VerifyOrReturn(mContext.fabricTable.FabricCount() == 0);
```

데이터 삭제는 다음 함수를 통해 수행합니다.

```cpp
mContext.deviceInfoProvider.ClearUserLabelList(mPath.mEndpointId)
```

삭제에 실패하면 오류를 기록합니다.

```cpp
ChipLogError(Zcl, "UserLabel: Failed to clear UserLabelList for endpoint: %d", mPath.mEndpointId);
```

### Codegen 통합

`CodegenIntegration.cpp`는 `LazyRegisteredServerCluster<UserLabelCluster>` 배열을 사용하여 서버 클러스터를 등록합니다.

```cpp
constexpr size_t kUserLabelFixedClusterCount = UserLabel::StaticApplicationConfig::kFixedClusterConfig.size();
constexpr size_t kUserLabelMaxClusterCount   = kUserLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT;

LazyRegisteredServerCluster<UserLabelCluster> gServers[kUserLabelMaxClusterCount];
```

`IntegrationDelegate::CreateRegistration`은 다음 context로 `UserLabelCluster`를 생성합니다.

```cpp
UserLabelCluster::Context{
    .deviceInfoProvider = *deviceInfoProvider,
    .fabricTable        = Server::GetInstance().GetFabricTable(),
}
```

서버 등록은 `MatterUserLabelClusterInitCallback`에서 수행합니다.

```cpp
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
```

서버 등록 해제는 `MatterUserLabelClusterShutdownCallback`에서 수행합니다.

```cpp
CodegenClusterIntegration::UnregisterServer(
    {
        .endpointId                = endpointId,
        .clusterId                 = UserLabel::Id,
        .fixedClusterInstanceCount = kUserLabelFixedClusterCount,
        .maxClusterInstanceCount   = kUserLabelMaxClusterCount,
    },
    integrationDelegate, shutdownType);
```

플러그인 서버 초기화 callback은 비어 있습니다.

```cpp
void MatterUserLabelPluginServerInitCallback() {}
```