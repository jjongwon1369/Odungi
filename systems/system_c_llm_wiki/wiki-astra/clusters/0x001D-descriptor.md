---
entity: Descriptor
ids: ['0x001D']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml', 'src/app/clusters/descriptor/DescriptorCluster.h', 'src/app/clusters/descriptor/CodegenIntegration.cpp', 'src/app/clusters/descriptor/DescriptorCluster.cpp', 'data_model/1.7/clusters/Descriptor-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Descriptor

## 개요

Descriptor는 노드, 엔드포인트 및 클러스터를 기술하기 위한 클러스터로, Zigbee Device Object (ZDO)의 해당 지원을 대체하는 것을 목적으로 한다.

- 클러스터 ID: 스펙 `0x001D`, SDK `0x001d`
- 리비전: `3`
- 분류: `hierarchy="base"`, `role="utility"`, `scope="Endpoint"`
- PICS 코드: `DESC`

## 스펙

출처: `data_model/1.7/clusters/Descriptor-Cluster.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 의미 태그 목록 및 `TagList` 기능 추가 |
| `3` | `EndpointUniqueID` 속성 추가 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `TAGLIST` | `TagList` | `TagList` 속성이 존재함 | `describedConform` |

### 데이터 타입

#### DeviceTypeStruct

| 필드 ID | 이름 | 타입 | 필수 여부 | 제약 |
|---|---|---|---|---|
| `0` | `DeviceType` | `devtype-id` | 필수 | — |
| `1` | `Revision` | `uint16` | 필수 | 최솟값 `1` |

### 속성

모든 속성은 `read="true"`, `readPrivilege="view"`로 정의된다.

| ID | 이름 | 타입 / 항목 타입 | 적합성 | 제약 | 기본값 | persistence |
|---|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `list` / `DeviceTypeStruct` | 필수 | 최소 `1`개 | `desc` | `fixed` |
| `0x0001` | `ServerList` | `list` / `cluster-id` | 필수 | — | `empty` | `fixed` |
| `0x0002` | `ClientList` | `list` / `cluster-id` | 필수 | — | `empty` | `fixed` |
| `0x0003` | `PartsList` | `list` / `endpoint-no` | 필수 | — | `empty` | — |
| `0x0004` | `TagList` | `list` / `SemanticTagStruct` | `TAGLIST` 기능에 따른 필수 속성 | `1`~`6`개 | `MS` | `fixed` |
| `0x0005` | `EndpointUniqueID` | `string` | 선택 | 최대 길이 `32` | — | `fixed` |

`—`는 제공된 스펙 XML에 해당 항목이 명시되지 않았음을 뜻한다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml`

이 파일은 Alchemy가 생성한 XML이며, 주석에 직접 수정하지 말라고 명시되어 있다. 생성 원본은 `src/data_model/Descriptor-Cluster.adoc`이다.

### 클러스터 설정

| 항목 | 정의 |
|---|---|
| 이름 | `Descriptor` |
| 코드 | `0x001d` |
| define | `DESCRIPTOR_CLUSTER` |
| 클러스터 domain | `General` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="3"` |

기능은 비트 `0`, 코드 `TAGLIST`, 이름 `TagList`로 정의된다.

### DeviceTypeStruct 매핑

| fieldId | 이름 | SDK 타입 | 제약 |
|---|---|---|---|
| `0` | `DeviceType` | `devtype_id` | — |
| `1` | `Revision` | `int16u` | `min="1"` |

### 속성 매핑

모든 속성은 `side="server"`로 정의된다.

| 코드 | 이름 | define | 타입 | entryType | 제약 및 선택 설정 |
|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `DEVICE_LIST` | `array` | `DeviceTypeStruct` | `minLength="1"` |
| `0x0001` | `ServerList` | `SERVER_LIST` | `array` | `cluster_id` | — |
| `0x0002` | `ClientList` | `CLIENT_LIST` | `array` | `cluster_id` | — |
| `0x0003` | `PartsList` | `PARTS_LIST` | `array` | `endpoint_no` | — |
| `0x0004` | `TagList` | `TAG_LIST` | `array` | `SemanticTagStruct` | `optional="true"`, `length="6"`, `minLength="1"`; `TAGLIST`에 대한 `mandatoryConform` |
| `0x0005` | `EndpointUniqueID` | `END_POINT_UNIQUE_ID` | `char_string` | — | `optional="true"`, `length="32"`, `optionalConform` |

## 구현

### DescriptorCluster

출처: `src/app/clusters/descriptor/DescriptorCluster.h`

`chip::app::Clusters`의 `DescriptorCluster`는 `DefaultServerCluster`를 상속한다.

- `SemanticTag`: `Globals::Structs::SemanticTagStruct::Type`의 별칭.
- `OptionalAttributesSet`: `OptionalAttributeSet<Descriptor::Attributes::EndpointUniqueID::Id>`의 별칭.
- 생성자는 `endpointId`, `optionalAttributeSet`, `semanticTags`를 받아 `{ endpointId, Descriptor::Id }`로 기반 클래스를 초기화한다.
- 선택 속성 설정은 `mEnabledOptionalAttributes`, 의미 태그는 `mSemanticTags`에 저장한다.
- `Attributes`와 `ReadAttribute`를 재정의한다.

`Span<const SemanticTag>`는 데이터를 소유하지 않는다. 호출자는 의미 태그의 기반 데이터가 `DescriptorCluster` 인스턴스의 수명 동안 유효하도록 보장해야 한다.

### 속성 목록 구성

출처: `src/app/clusters/descriptor/DescriptorCluster.cpp`

`DescriptorCluster::Attributes`는 `AttributeListBuilder`로 `Attributes::kMandatoryMetadata`와 조건부 속성을 추가한다.

| 속성 | 추가 조건 |
|---|---|
| `TagList` | `mSemanticTags`가 비어 있지 않음 |
| `EndpointUniqueID` | `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID`가 활성화되고 `mEnabledOptionalAttributes.IsSet(EndpointUniqueID::Id)`가 참 |

### 속성 읽기

`DescriptorCluster::ReadAttribute`는 `request.path.mAttributeId`에 따라 값을 인코딩한다.

| 속성 | 처리 |
|---|---|
| `FeatureMap` | `mSemanticTags`가 비어 있지 않으면 `Descriptor::Feature::kTagList`를 설정하여 인코딩 |
| `ClusterRevision` | `Descriptor::kRevision` 인코딩 |
| `DeviceTypeList` | `ReadDeviceAttribute` 호출 |
| `ServerList` | `mContext->provider.ServerClusters`의 각 항목에서 `entry.clusterId` 인코딩 |
| `ClientList` | `mContext->provider.ClientClusters`가 반환한 각 `clusterId` 인코딩 |
| `PartsList` | `ReadPartsAttribute` 호출 |
| `TagList` | `ReadTagListAttribute`로 `mSemanticTags`의 각 태그 인코딩 |
| `EndpointUniqueID` | `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID`가 활성화된 경우 `mContext->provider.EndpointUniqueID`로 조회하여 인코딩 |

처리하지 않는 속성에는 `Status::UnsupportedAttribute`를 반환한다.

`ReadDeviceAttribute`는 `provider.DeviceTypes`의 결과를 `Descriptor::Structs::DeviceTypeStruct::Type`으로 변환한다.

- `type.deviceTypeId` → `deviceStruct.deviceType`
- `type.deviceTypeRevision` → `deviceStruct.revision`

`EndpointUniqueID` 읽기에서는 `EndpointUniqueID::TypeInfo::MaxLength()` 크기의 버퍼와 `MutableCharSpan`을 사용한다.

### PartsList 구성

`ReadPartsAttribute`는 `provider.Endpoints`로 엔드포인트 목록을 조회한다.

| 조건 | 인코딩 대상 |
|---|---|
| `endpoint == kRootEndpointId` | `ep.id == 0`인 항목을 제외한 모든 엔드포인트 |
| `DataModel::EndpointCompositionPattern::kFullFamily` | `IsDescendantOf`가 해당 엔드포인트의 후손으로 판정한 모든 엔드포인트 |
| `DataModel::EndpointCompositionPattern::kTree` | `ep.parentId == endpoint`인 직접 자식 엔드포인트 |

루트가 아닌 요청 엔드포인트를 목록에서 찾지 못하면 `CHIP_ERROR_NOT_FOUND`를 반환한다.

`IsDescendantOf`는 `parentId`를 따라 부모를 목록에서 반복 검색한다. 대상 부모를 찾으면 참을 반환하며, 부모 항목을 찾지 못하거나 `kInvalidEndpointId`에 도달하면 거짓을 반환한다.

### Codegen 통합

출처: `src/app/clusters/descriptor/CodegenIntegration.cpp`

#### 의미 태그의 지연 조회

`EmberDescriptorCluster`는 `DescriptorCluster`를 상속하며, 최초의 `Attributes` 또는 `ReadAttribute` 호출에서 `GetSemanticTagsForEndpoint`를 실행한다. 이후 `mFetchedSemanticTags`를 참으로 설정하여 다시 조회하지 않는다.

이 지연 조회는 엔드포인트 초기화 순서와 이전 동작의 호환성을 고려한 것이다.

- 고정 엔드포인트는 `InitDataModelHandler()`에서 연속 호출되는 `emberAfEndpointConfigure()`와 `emberAfInit()`를 통해 정의되고 초기화된다.
- 동적 엔드포인트는 `emberAfSetDynamicEndpointWithEpUniqueId()`에서 `emberAfEndpointEnableDisable()`을 호출하고, 이어서 `initializeEndpoint()`를 통해 초기화된다.
- 코드 주석은 엔드포인트 초기화 전에 태그 목록을 조회하여 일반 `DescriptorCluster` 생성자에 전달할 수 없다고 설명한다.

#### 인스턴스 관리

- `CHIP_CONFIG_SKIP_APP_SPECIFIC_GENERATED_HEADER_INCLUDES`가 활성화되면 `kDescriptorFixedClusterCount`는 `0`이다.
- 그렇지 않으면 `Descriptor::StaticApplicationConfig::kFixedClusterConfig.size()`를 사용한다.
- `kDescriptorMaxClusterCount`는 `kDescriptorFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`이다.
- `gServers`는 `LazyRegisteredServerCluster<EmberDescriptorCluster>` 배열이다.

`IntegrationDelegate`는 다음 작업을 수행한다.

| 함수 | 처리 |
|---|---|
| `CreateRegistration` | `optionalAttributeBits`와 빈 의미 태그 `Span`으로 인스턴스를 생성하고 등록 객체 반환 |
| `FindRegistration` | 생성된 인스턴스를 반환하며, 생성되지 않았다면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

#### 수명주기 콜백

| 콜백 | 처리 |
|---|---|
| `MatterDescriptorClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterDescriptorClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `MatterDescriptorPluginServerInitCallback` | 빈 구현 |
| `MatterDescriptorPluginServerShutdownCallback` | 빈 구현 |

등록 시 `clusterId`는 `Descriptor::Id`이며, `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true`로 설정된다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
