---
entity: Descriptor
ids: ['0x001D']
source_paths: ['data_model/1.7/clusters/Descriptor-Cluster.xml', 'src/app/clusters/descriptor/CodegenIntegration.cpp', 'src/app/clusters/descriptor/DescriptorCluster.cpp', 'src/app/clusters/descriptor/DescriptorCluster.h', 'src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Descriptor

## 개요

Descriptor는 노드, 엔드포인트 및 클러스터를 설명하는 클러스터로, SDK 설명에서는 Zigbee Device Object (ZDO)의 해당 기능을 대체하기 위한 것으로 정의한다.

| 항목 | 값 |
|---|---|
| 스펙 이름 | `Descriptor Cluster` |
| 클러스터 이름 | `Descriptor` |
| 클러스터 ID | 스펙: `0x001D`, SDK: `0x001d` |
| revision | `3` |
| hierarchy | `base` |
| role | `utility` |
| picsCode | `DESC` |
| scope | `Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/Descriptor-Cluster.xml`

### 개정 이력

| revision | 변경 내용 |
|---|---|
| `1` | 최초 개정 |
| `2` | 의미 태그 목록 및 `TagList` 기능 추가 |
| `3` | `EndpointUniqueID` 속성 추가 |

### 기능

| bit | code | name | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `TAGLIST` | `TagList` | `TagList` 속성이 존재함 | `describedConform` |

### 데이터 타입

#### DeviceTypeStruct

| field id | 이름 | 타입 | 필수 여부 | 제약 |
|---|---|---|---|---|
| `0` | `DeviceType` | `devtype-id` | 필수 | — |
| `1` | `Revision` | `uint16` | 필수 | 최솟값 `1` |

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`이다.

| ID | 이름 | 타입 / 항목 타입 | 적합성 | 기본값 | persistence | 제약 |
|---|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `list` / `DeviceTypeStruct` | 필수 | `desc` | `fixed` | 최소 항목 수 `1` |
| `0x0001` | `ServerList` | `list` / `cluster-id` | 필수 | `empty` | `fixed` | — |
| `0x0002` | `ClientList` | `list` / `cluster-id` | 필수 | `empty` | `fixed` | — |
| `0x0003` | `PartsList` | `list` / `endpoint-no` | 필수 | `empty` | 명시 없음 | — |
| `0x0004` | `TagList` | `list` / `SemanticTagStruct` | `TAGLIST` 기능 사용 시 필수 | `MS` | `fixed` | 항목 수 `1`~`6` |
| `0x0005` | `EndpointUniqueID` | `string` | 선택 | 명시 없음 | `fixed` | 최대 길이 `32` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml`

이 파일은 Alchemy가 생성한 XML이며, 직접 수정하지 않도록 명시되어 있다. 생성 원본은 `src/data_model/Descriptor-Cluster.adoc`이다.

### 클러스터 설정

| 항목 | 정의 |
|---|---|
| configurator domain | `CHIP` |
| cluster domain | `General` |
| name | `Descriptor` |
| code | `0x001d` |
| define | `DESCRIPTOR_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="3"` |

기능은 스펙과 동일하게 bit `0`, code `TAGLIST`, name `TagList`로 정의된다.

### DeviceTypeStruct 매핑

`DeviceTypeStruct`는 클러스터 code `0x001d`에 연결된다.

| fieldId | 이름 | SDK 타입 | 제약 |
|---|---|---|---|
| `0` | `DeviceType` | `devtype_id` | — |
| `1` | `Revision` | `int16u` | `min="1"` |

### 속성 매핑

모든 속성의 `side`는 `server`이다.

| code | name | define | type | entryType | 선택 여부 및 길이 설정 |
|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `DEVICE_LIST` | `array` | `DeviceTypeStruct` | `minLength="1"` |
| `0x0001` | `ServerList` | `SERVER_LIST` | `array` | `cluster_id` | — |
| `0x0002` | `ClientList` | `CLIENT_LIST` | `array` | `cluster_id` | — |
| `0x0003` | `PartsList` | `PARTS_LIST` | `array` | `endpoint_no` | — |
| `0x0004` | `TagList` | `TAG_LIST` | `array` | `SemanticTagStruct` | `optional="true"`, `length="6"`, `minLength="1"` |
| `0x0005` | `EndpointUniqueID` | `END_POINT_UNIQUE_ID` | `char_string` | — | `optional="true"`, `length="32"` |

`TagList`에는 `TAGLIST` 기능에 따른 `mandatoryConform`이, `EndpointUniqueID`에는 `optionalConform`이 정의되어 있다.

## 구현

### 클래스와 데이터 수명

출처: `src/app/clusters/descriptor/DescriptorCluster.h`

`chip::app::Clusters`의 `DescriptorCluster`는 `DefaultServerCluster`를 상속한다.

- `SemanticTag`는 `Globals::Structs::SemanticTagStruct::Type`의 별칭이다.
- `OptionalAttributesSet`은 `OptionalAttributeSet<Descriptor::Attributes::EndpointUniqueID::Id>`의 별칭이다.
- 생성자는 `endpointId`, `optionalAttributeSet`, `semanticTags`를 받는다.
- `mEnabledOptionalAttributes`에 선택 속성 설정을 저장한다.
- `mSemanticTags`는 `Span<const SemanticTag>`이며 데이터를 소유하지 않는다. 호출자는 기반 데이터를 `DescriptorCluster` 인스턴스의 전체 수명 동안 유효하게 유지해야 한다.
- `Attributes()`와 `ReadAttribute()`를 재정의한다.

### 속성 목록 구성

출처: `src/app/clusters/descriptor/DescriptorCluster.cpp`

`DescriptorCluster::Attributes()`는 `AttributeListBuilder`를 사용하여 `Attributes::kMandatoryMetadata`와 조건부 속성 항목을 추가한다.

| 속성 | 목록에 추가되는 조건 |
|---|---|
| `TagList` | `mSemanticTags`가 비어 있지 않음 |
| `EndpointUniqueID` | `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID`가 활성화되고, `mEnabledOptionalAttributes.IsSet(EndpointUniqueID::Id)`가 참임 |

### 속성 읽기

`DescriptorCluster::ReadAttribute()`는 요청의 `request.path.mAttributeId`에 따라 처리한다.

| 속성 | 처리 |
|---|---|
| `FeatureMap` | `mSemanticTags`가 비어 있지 않으면 `Descriptor::Feature::kTagList`를 설정하여 인코딩 |
| `ClusterRevision` | `Descriptor::kRevision` 인코딩 |
| `DeviceTypeList` | `ReadDeviceAttribute()` 호출 |
| `ServerList` | `mContext->provider.ServerClusters()`에서 가져온 각 `entry.clusterId` 인코딩 |
| `ClientList` | `mContext->provider.ClientClusters()`에서 가져온 각 `clusterId` 인코딩 |
| `PartsList` | `ReadPartsAttribute()` 호출 |
| `TagList` | `ReadTagListAttribute()`로 `mSemanticTags`의 각 항목 인코딩 |
| `EndpointUniqueID` | `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID` 활성화 시 `mContext->provider.EndpointUniqueID()`의 결과 인코딩 |

처리되지 않는 속성 ID에는 `Status::UnsupportedAttribute`를 반환한다.

`ReadDeviceAttribute()`는 `provider.DeviceTypes()`의 결과를 `Descriptor::Structs::DeviceTypeStruct::Type`으로 변환한다. `deviceTypeId`는 `deviceType`에, `deviceTypeRevision`은 `revision`에 대응한다.

`EndpointUniqueID` 읽기에는 `EndpointUniqueID::TypeInfo::MaxLength()` 크기의 버퍼와 `MutableCharSpan`을 사용한다.

### PartsList 구성

`ReadPartsAttribute()`는 `provider.Endpoints()`에서 엔드포인트 목록을 가져온다.

| 조건 | 인코딩하는 엔드포인트 |
|---|---|
| 요청 엔드포인트가 `kRootEndpointId` | `ep.id == 0`인 항목을 제외한 모든 엔드포인트 |
| `DataModel::EndpointCompositionPattern::kFullFamily` | `IsDescendantOf()`로 판별한 요청 엔드포인트의 모든 후손 |
| `DataModel::EndpointCompositionPattern::kTree` | `ep.parentId`가 요청 엔드포인트와 같은 직접 자식 |

루트가 아닌 요청 엔드포인트를 목록에서 찾지 못하면 `CHIP_ERROR_NOT_FOUND`를 반환한다.

`IsDescendantOf()`는 `parentId`를 따라 상위 엔드포인트를 탐색한다. 대상 부모를 만나면 참을 반환하고, 엔드포인트를 찾지 못하거나 `kInvalidEndpointId`에 도달하면 거짓을 반환한다.

### 코드 생성 통합과 초기화

출처: `src/app/clusters/descriptor/CodegenIntegration.cpp`

#### 의미 태그 지연 조회

`EmberDescriptorCluster`는 `DescriptorCluster`를 상속하며, `Attributes()` 또는 `ReadAttribute()`가 처음 호출될 때 `GetSemanticTagsForEndpoint()`로 `mSemanticTags`를 가져온다. `mFetchedSemanticTags`를 통해 조회를 한 번만 수행한다.

이 방식은 엔드포인트 초기화 순서와 기존 동작과의 호환성을 위한 것이다.

- 고정 엔드포인트는 `InitDataModelHandler()`에서 연속 호출되는 `emberAfEndpointConfigure()`와 `emberAfInit()`를 통해 정의 및 초기화된다.
- 동적 엔드포인트는 `emberAfSetDynamicEndpointWithEpUniqueId()`에서 `emberAfEndpointEnableDisable()`을 호출하고, 이어서 `initializeEndpoint()`를 통해 초기화된다.
- 따라서 초기화 전에 의미 태그를 조회하여 일반 `DescriptorCluster` 생성자에 전달하는 방식을 사용할 수 없다고 주석에 설명되어 있다.

#### 인스턴스 관리

- `CHIP_CONFIG_SKIP_APP_SPECIFIC_GENERATED_HEADER_INCLUDES`가 활성화되면 `kDescriptorFixedClusterCount`는 `0`이다.
- 그렇지 않으면 `Descriptor::StaticApplicationConfig::kFixedClusterConfig.size()`를 사용한다.
- `kDescriptorMaxClusterCount`는 `kDescriptorFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`이다.
- `gServers`는 `LazyRegisteredServerCluster<EmberDescriptorCluster>` 배열이다.

`IntegrationDelegate`는 다음 등록 수명주기를 구현한다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration()` | 선택 속성 비트와 빈 의미 태그 목록으로 인스턴스를 생성하고 등록 객체 반환 |
| `FindRegistration()` | 생성된 인스턴스의 인터페이스 반환. 생성되지 않았으면 `nullptr` 반환 |
| `ReleaseRegistration()` | 해당 인스턴스의 `Destroy()` 호출 |

#### 콜백

| 콜백 | 동작 |
|---|---|
| `MatterDescriptorClusterInitCallback()` | `CodegenClusterIntegration::RegisterServer()`로 `Descriptor::Id` 등록 |
| `MatterDescriptorClusterShutdownCallback()` | `CodegenClusterIntegration::UnregisterServer()` 호출 및 `shutdownType` 전달 |
| `MatterDescriptorPluginServerInitCallback()` | 빈 구현 |
| `MatterDescriptorPluginServerShutdownCallback()` | 빈 구현 |

등록 시 `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true`로 설정된다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
