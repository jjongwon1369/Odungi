---
entity: Descriptor
ids: ['0x001D']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml', 'src/app/clusters/descriptor/DescriptorCluster.h', 'src/app/clusters/descriptor/CodegenIntegration.cpp', 'src/app/clusters/descriptor/DescriptorCluster.cpp', 'data_model/1.7/clusters/Descriptor-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Descriptor

## 개요

Descriptor Cluster는 노드, 해당 endpoint 및 cluster를 설명하기 위해 Zigbee Device Object (ZDO)의 지원 기능을 대체하는 Cluster입니다.

- Cluster name: `Descriptor`
- Cluster ID: `0x001D`
- SDK code: `0x001d`
- Classification: `hierarchy="base"`, `role="utility"`, `scope="Endpoint"`
- PICS code: `DESC`
- Revision: `3`
- 지원 방향:
  - Client: 지원
  - Server: 지원

## 스펙

### Revision history

| Revision | 내용 |
|---:|---|
| `1` | Initial revision |
| `2` | Semantic tag list; `TagList` feature |
| `3` | Add `EndpointUniqueID` attribute |

### Feature

| Bit | Code | Name | 설명 |
|---:|---|---|---|
| `0` | `TAGLIST` | `TagList` | `TagList` attribute is present |

### 데이터 타입

#### `DeviceTypeStruct`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| `0` | `DeviceType` | `devtype-id` | 필수 |
| `1` | `Revision` | `uint16` | 필수, 최솟값 `1` |

### Attributes

모든 Attribute는 읽기 권한이 있으며 `readPrivilege="view"`입니다.

| ID | 이름 | 타입 | 기본값 | 조건 및 제약 |
|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `list` of `DeviceTypeStruct` | `desc` | 필수, 최소 항목 수 `1`, `persistence="fixed"` |
| `0x0001` | `ServerList` | `list` of `cluster-id` | `empty` | 필수, `persistence="fixed"` |
| `0x0002` | `ClientList` | `list` of `cluster-id` | `empty` | 필수, `persistence="fixed"` |
| `0x0003` | `PartsList` | `list` of `endpoint-no` | `empty` | 필수 |
| `0x0004` | `TagList` | `list` of `SemanticTagStruct` | `MS` | `TAGLIST` feature 필요, 항목 수 `1`~`6`, `persistence="fixed"` |
| `0x0005` | `EndpointUniqueID` | `string` | - | 선택 사항, 최대 길이 `32`, `persistence="fixed"` |

## SDK 정의

### 파일

`src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml`

### Cluster 정의

```xml
<cluster>
  <domain>General</domain>
  <name>Descriptor</name>
  <code>0x001d</code>
  <define>DESCRIPTOR_CLUSTER</define>
</cluster>
```

Description:

> The Descriptor Cluster is meant to replace the support from the Zigbee Device Object (ZDO) for describing a node, its endpoints and clusters.

Global Attribute:

- ID: `0xFFFD`
- Value: `3`

### `DeviceTypeStruct`

```xml
<struct name="DeviceTypeStruct">
  <cluster code="0x001d"/>
  <item fieldId="0" name="DeviceType" type="devtype_id"/>
  <item fieldId="1" name="Revision" type="int16u" min="1"/>
</struct>
```

### Feature

```xml
<feature bit="0" code="TAGLIST" name="TagList" summary="The TagList attribute is present">
```

### Attributes

| ID | 이름 | Define | 타입 | Entry type | 조건 |
|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `DEVICE_LIST` | `array` | `DeviceTypeStruct` | `minLength="1"` |
| `0x0001` | `ServerList` | `SERVER_LIST` | `array` | `cluster_id` | - |
| `0x0002` | `ClientList` | `CLIENT_LIST` | `array` | `cluster_id` | - |
| `0x0003` | `PartsList` | `PARTS_LIST` | `array` | `endpoint_no` | - |
| `0x0004` | `TagList` | `TAG_LIST` | `array` | `SemanticTagStruct` | optional, `length="6"`, `minLength="1"`, `TAGLIST` 필요 |
| `0x0005` | `EndpointUniqueID` | `END_POINT_UNIQUE_ID` | `char_string` | - | optional, `length="32"` |

## 구현

### 파일

- `src/app/clusters/descriptor/DescriptorCluster.h`
- `src/app/clusters/descriptor/DescriptorCluster.cpp`
- `src/app/clusters/descriptor/CodegenIntegration.cpp`

### `DescriptorCluster`

`DescriptorCluster`는 `DefaultServerCluster`를 상속합니다.

```cpp
class DescriptorCluster : public DefaultServerCluster
```

주요 타입 정의:

```cpp
using SemanticTag = Globals::Structs::SemanticTagStruct::Type;
using OptionalAttributesSet = OptionalAttributeSet<Descriptor::Attributes::EndpointUniqueID::Id>;
```

생성자:

```cpp
DescriptorCluster(EndpointId endpointId, OptionalAttributesSet optionalAttributeSet,
                  Span<const SemanticTag> semanticTags)
```

`semanticTags`는 소유하지 않는 view이며, `DescriptorCluster` 인스턴스의 수명 동안 underlying data가 유효해야 합니다.

주요 함수:

```cpp
CHIP_ERROR Attributes(const ConcreteClusterPath & path,
                      ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

DataModel::ActionReturnStatus ReadAttribute(
    const DataModel::ReadAttributeRequest & request,
    AttributeValueEncoder & encoder) override;
```

### Attribute 목록 구성

`DescriptorCluster::Attributes`는 다음 항목을 mandatory 또는 optional Attribute 목록으로 구성합니다.

- mandatory Attribute:
  - `Attributes::kMandatoryMetadata`
- optional Attribute:
  - `TagList::kMetadataEntry`
    - `mSemanticTags`가 비어 있지 않을 때 추가
  - `EndpointUniqueID::kMetadataEntry`
    - `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID`가 활성화되고 `mEnabledOptionalAttributes.IsSet(EndpointUniqueID::Id)`가 참일 때 추가

### Attribute 읽기

`DescriptorCluster::ReadAttribute`는 다음 Attribute를 처리합니다.

| Attribute | 구현 동작 |
|---|---|
| `FeatureMap::Id` | `mSemanticTags`가 비어 있지 않으면 `Descriptor::Feature::kTagList` 설정 |
| `ClusterRevision::Id` | `Descriptor::kRevision` 반환 |
| `DeviceTypeList::Id` | `DataModel::Provider::DeviceTypes`에서 Device Type을 가져와 `DeviceTypeStruct`로 인코딩 |
| `ServerList::Id` | `DataModel::Provider::ServerClusters`에서 Server Cluster 목록을 가져와 `clusterId`를 인코딩 |
| `ClientList::Id` | `DataModel::Provider::ClientClusters`에서 Client Cluster 목록을 가져와 인코딩 |
| `PartsList::Id` | `ReadPartsAttribute`를 통해 endpoint 구성에 따라 목록 인코딩 |
| `TagList::Id` | `mSemanticTags`를 목록으로 인코딩 |
| `EndpointUniqueID::Id` | `DataModel::Provider::EndpointUniqueID`에서 값을 가져와 인코딩 |
| 그 외 | `Status::UnsupportedAttribute` 반환 |

`EndpointUniqueID::Id` 처리는 `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID`가 활성화된 경우에만 컴파일됩니다.

### `PartsList` 처리

`ReadPartsAttribute`는 endpoint와 `compositionPattern`에 따라 다음과 같이 동작합니다.

- `kRootEndpointId`:
  - endpoint ID `0`을 제외한 모든 endpoint를 인코딩
- `DataModel::EndpointCompositionPattern::kFullFamily`:
  - 지정된 endpoint를 descendant로 가지는 모든 endpoint를 인코딩
  - `IsDescendantOf`를 사용해 계층을 검색
- `DataModel::EndpointCompositionPattern::kTree`:
  - 지정된 endpoint를 직접 parent로 가지는 endpoint를 인코딩
- endpoint를 찾지 못하면 `CHIP_ERROR_NOT_FOUND` 반환

### `EmberDescriptorCluster`

`CodegenIntegration.cpp`에는 `DescriptorCluster`에서 상속한 `EmberDescriptorCluster`가 정의되어 있습니다.

`EmberDescriptorCluster`는 `Attributes()` 또는 `ReadAttribute()`가 처음 호출될 때 `GetSemanticTagsForEndpoint`를 통해 semantic tag 목록을 한 번 가져옵니다.

```cpp
GetSemanticTagsForEndpoint(path.mEndpointId, mSemanticTags);
```

또는:

```cpp
GetSemanticTagsForEndpoint(request.path.mEndpointId, mSemanticTags);
```

가져온 이후에는 `mFetchedSemanticTags`를 `true`로 설정하며, 이후 호출에서는 다시 가져오지 않습니다.

### Server registration

`MatterDescriptorClusterInitCallback`은 다음 설정으로 Server Cluster를 등록합니다.

- `clusterId`: `Descriptor::Id`
- `fixedClusterInstanceCount`: `kDescriptorFixedClusterCount`
- `maxClusterInstanceCount`: `kDescriptorMaxClusterCount`
- `fetchFeatureMap`: `false`
- `fetchOptionalAttributes`: `true`

등록 및 해제 함수:

```cpp
void MatterDescriptorClusterInitCallback(EndpointId endpointId);
void MatterDescriptorClusterShutdownCallback(EndpointId endpointId,
                                             MatterClusterShutdownType shutdownType);
```

Server Cluster 인스턴스는 다음 배열로 관리됩니다.

```cpp
LazyRegisteredServerCluster<EmberDescriptorCluster> gServers[kDescriptorMaxClusterCount];
```

`IntegrationDelegate`는 다음 작업을 제공합니다.

- `CreateRegistration`
- `FindRegistration`
- `ReleaseRegistration`

## 관련 문서

- `data_model/1.7/clusters/Descriptor-Cluster.xml`
- `src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml`
- `src/app/clusters/descriptor/DescriptorCluster.h`
- `src/app/clusters/descriptor/DescriptorCluster.cpp`
- `src/app/clusters/descriptor/CodegenIntegration.cpp`

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
