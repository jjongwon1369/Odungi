---
entity: Descriptor
ids: ['0x001D']
source_paths: ['data_model/1.7/clusters/Descriptor-Cluster.xml', 'src/app/clusters/descriptor/CodegenIntegration.cpp', 'src/app/clusters/descriptor/DescriptorCluster.cpp', 'src/app/clusters/descriptor/DescriptorCluster.h', 'src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Descriptor

## 개요

Descriptor는 노드, 엔드포인트 및 클러스터를 기술하기 위한 클러스터로, SDK 설명에서는 Zigbee Device Object (ZDO)의 해당 기능을 대체하는 용도로 정의한다.

- 스펙 이름: `Descriptor Cluster`
- 클러스터 이름: `Descriptor`
- 클러스터 ID: 스펙 `0x001D`, SDK `0x001d`
- 리비전: `3`
- 분류: hierarchy=`base`, role=`utility`, picsCode=`DESC`, scope=`Endpoint`
- 주요 속성: `DeviceTypeList`, `ServerList`, `ClientList`, `PartsList`, `TagList`, `EndpointUniqueID`

## 스펙

출처: `data_model/1.7/clusters/Descriptor-Cluster.xml`

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 의미 태그 목록 및 `TagList` 기능 추가 |
| `3` | `EndpointUniqueID` 속성 추가 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `TAGLIST` | `TagList` | `TagList` 속성 존재 | `describedConform` |

### 데이터 타입

`DeviceTypeStruct`의 필드는 모두 필수다.

| 필드 ID | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `DeviceType` | `devtype-id` | 별도 제약 없음 |
| `1` | `Revision` | `uint16` | 최솟값 `1` |

### 속성

모든 속성은 읽기를 지원하며 읽기 권한은 `view`다.

| ID | 이름 | 타입 | 기본값 | 적합성 | 제약 | persistence |
|---|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `list`, 항목 `DeviceTypeStruct` | `desc` | 필수 | 최소 `1`개 | `fixed` |
| `0x0001` | `ServerList` | `list`, 항목 `cluster-id` | `empty` | 필수 | 명시 없음 | `fixed` |
| `0x0002` | `ClientList` | `list`, 항목 `cluster-id` | `empty` | 필수 | 명시 없음 | `fixed` |
| `0x0003` | `PartsList` | `list`, 항목 `endpoint-no` | `empty` | 필수 | 명시 없음 | 명시 없음 |
| `0x0004` | `TagList` | `list`, 항목 `SemanticTagStruct` | `MS` | `TAGLIST` 기능 사용 시 필수 | `1`~`6`개 | `fixed` |
| `0x0005` | `EndpointUniqueID` | `string` | 명시 없음 | 선택 | 최대 길이 `32` | `fixed` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/descriptor-cluster.xml`

### 클러스터 설정

| 항목 | 정의 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `General` |
| 이름 | `Descriptor` |
| 코드 | `0x001d` |
| define | `DESCRIPTOR_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="3"` |

기능 정의는 bit=`0`, code=`TAGLIST`, name=`TagList`이며, `describedConform`을 사용한다.

### 데이터 타입 매핑

| 구조체 | 필드 | fieldId | SDK 타입 | 제약 |
|---|---|---|---|---|
| `DeviceTypeStruct` | `DeviceType` | `0` | `devtype_id` | 명시 없음 |
| `DeviceTypeStruct` | `Revision` | `1` | `int16u` | `min="1"` |

### 속성 정의

모든 속성은 `side="server"`로 정의된다.

| 코드 | 이름 | define | 타입 | entryType | 선택 여부 및 길이 |
|---|---|---|---|---|---|
| `0x0000` | `DeviceTypeList` | `DEVICE_LIST` | `array` | `DeviceTypeStruct` | `minLength="1"` |
| `0x0001` | `ServerList` | `SERVER_LIST` | `array` | `cluster_id` | 별도 지정 없음 |
| `0x0002` | `ClientList` | `CLIENT_LIST` | `array` | `cluster_id` | 별도 지정 없음 |
| `0x0003` | `PartsList` | `PARTS_LIST` | `array` | `endpoint_no` | 별도 지정 없음 |
| `0x0004` | `TagList` | `TAG_LIST` | `array` | `SemanticTagStruct` | `optional="true"`, `length="6"`, `minLength="1"` |
| `0x0005` | `EndpointUniqueID` | `END_POINT_UNIQUE_ID` | `char_string` | 해당 없음 | `optional="true"`, `length="32"` |

`TagList`는 SDK에서 `optional="true"`로 표시되지만, `TAGLIST` 기능에 대한 `mandatoryConform`도 포함한다. `EndpointUniqueID`는 `optionalConform`으로 정의된다.

## 구현

### 클래스 및 데이터 수명

출처: `src/app/clusters/descriptor/DescriptorCluster.h`

`chip::app::Clusters`의 `DescriptorCluster`는 `DefaultServerCluster`를 상속한다.

- `SemanticTag`: `Globals::Structs::SemanticTagStruct::Type`의 별칭.
- `OptionalAttributesSet`: `OptionalAttributeSet<Descriptor::Attributes::EndpointUniqueID::Id>`의 별칭.
- 생성자는 `endpointId`, `optionalAttributeSet`, `semanticTags`를 받는다.
- `mEnabledOptionalAttributes`에 선택 속성 설정을 저장한다.
- `mSemanticTags`는 `Span<const SemanticTag>`이며 데이터를 소유하지 않는다. 호출자는 원본 데이터가 `DescriptorCluster` 인스턴스의 수명 동안 유효하도록 보장해야 한다.
- `Attributes`와 `ReadAttribute`를 재정의한다.

### 속성 목록 구성

출처: `src/app/clusters/descriptor/DescriptorCluster.cpp`

`DescriptorCluster::Attributes`는 `AttributeListBuilder`로 속성 목록을 구성한다.

- `Attributes::kMandatoryMetadata`를 추가한다.
- `mSemanticTags`가 비어 있지 않으면 `TagList::kMetadataEntry`를 추가한다.
- `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID`가 활성화된 빌드에서, `mEnabledOptionalAttributes.IsSet(EndpointUniqueID::Id)`가 참이면 `EndpointUniqueID::kMetadataEntry`를 추가한다.

### 속성 읽기

`DescriptorCluster::ReadAttribute`는 `request.path.mAttributeId`에 따라 처리한다.

| 속성 | 처리 |
|---|---|
| `FeatureMap` | `mSemanticTags`가 비어 있지 않으면 `Descriptor::Feature::kTagList`를 설정하여 인코딩 |
| `ClusterRevision` | `Descriptor::kRevision` 인코딩 |
| `DeviceTypeList` | `ReadDeviceAttribute` 호출 |
| `ServerList` | `mContext->provider.ServerClusters` 결과의 `entry.clusterId`를 목록으로 인코딩 |
| `ClientList` | `mContext->provider.ClientClusters` 결과의 `clusterId`를 목록으로 인코딩 |
| `PartsList` | `ReadPartsAttribute` 호출 |
| `TagList` | `ReadTagListAttribute`로 `mSemanticTags` 인코딩 |
| `EndpointUniqueID` | `CHIP_CONFIG_USE_ENDPOINT_UNIQUE_ID` 활성화 시 `mContext->provider.EndpointUniqueID` 결과 인코딩 |
| 그 외 | `Status::UnsupportedAttribute` 반환 |

`ReadDeviceAttribute`는 `provider.DeviceTypes`로 목록을 가져와 각 항목을 `Descriptor::Structs::DeviceTypeStruct::Type`으로 변환한다.

- `deviceType`에는 `type.deviceTypeId`를 사용한다.
- `revision`에는 `type.deviceTypeRevision`을 사용한다.

`EndpointUniqueID` 읽기에서는 `EndpointUniqueID::TypeInfo::MaxLength()` 크기의 버퍼와 `MutableCharSpan`을 사용한다.

### PartsList 구성

`ReadPartsAttribute`는 `provider.Endpoints`로 엔드포인트 목록을 가져온다.

| 조건 | 결과 |
|---|---|
| `endpoint == kRootEndpointId` | `ep.id == 0`인 항목을 제외한 모든 엔드포인트 ID |
| 대상 엔드포인트를 찾지 못함 | `CHIP_ERROR_NOT_FOUND` |
| `DataModel::EndpointCompositionPattern::kFullFamily` | `IsDescendantOf`가 참인 모든 후손 엔드포인트 ID |
| `DataModel::EndpointCompositionPattern::kTree` | `ep.parentId == endpoint`인 직접 자식 엔드포인트 ID |

`IsDescendantOf`는 `parentId` 연결을 따라 부모를 검색한다. 대상 부모를 찾으면 참을 반환하고, 부모가 `kInvalidEndpointId`이거나 부모 항목을 찾지 못하면 거짓을 반환한다.

### 코드 생성 통합 및 태그 지연 조회

출처: `src/app/clusters/descriptor/CodegenIntegration.cpp`

`EmberDescriptorCluster`는 `DescriptorCluster`를 상속하며, 첫 `Attributes` 또는 `ReadAttribute` 호출에서 `GetSemanticTagsForEndpoint`로 태그를 가져온다.

- `mFetchedSemanticTags`의 초기값은 `false`다.
- 태그 조회 후 `mFetchedSemanticTags`를 `true`로 설정한다.
- 이후 호출에서는 다시 조회하지 않고 기반 클래스의 해당 함수를 호출한다.

이 지연 조회는 엔드포인트 초기화 순서와 하위 호환성을 위한 것이다.

- 고정 엔드포인트는 `InitDataModelHandler()`에서 연속 호출되는 `emberAfEndpointConfigure()`와 `emberAfInit()`을 통해 정의 및 초기화된다.
- 동적 엔드포인트는 `emberAfSetDynamicEndpointWithEpUniqueId()`에서 `emberAfEndpointEnableDisable()`을 호출하고, 이어 `initializeEndpoint()`를 통해 초기화된다.

### 등록 및 해제

클러스터 인스턴스는 `LazyRegisteredServerCluster<EmberDescriptorCluster>` 타입의 `gServers` 배열로 관리한다.

- `CHIP_CONFIG_SKIP_APP_SPECIFIC_GENERATED_HEADER_INCLUDES`가 활성화되면 `kDescriptorFixedClusterCount`는 `0`이다.
- 그렇지 않으면 `Descriptor::StaticApplicationConfig::kFixedClusterConfig.size()`를 사용한다.
- `kDescriptorMaxClusterCount`는 `kDescriptorFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`다.

`IntegrationDelegate`의 역할은 다음과 같다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | `optionalAttributeBits`와 빈 태그 `Span`으로 인스턴스를 생성하고 등록 정보 반환 |
| `FindRegistration` | 생성된 인스턴스의 클러스터 포인터 반환, 미생성 시 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

콜백 동작:

- `MatterDescriptorClusterInitCallback`: `CodegenClusterIntegration::RegisterServer`를 호출한다. `clusterId`는 `Descriptor::Id`, `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true`다.
- `MatterDescriptorClusterShutdownCallback`: `CodegenClusterIntegration::UnregisterServer`에 `shutdownType`을 전달한다.
- `MatterDescriptorPluginServerInitCallback`과 `MatterDescriptorPluginServerShutdownCallback`은 빈 함수다.

## 관련 페이지

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md)
- [Cook Surface](../device-types/cook-surface.md)
- [Cooktop](../device-types/cooktop.md)
- [Dishwasher](../device-types/dishwasher.md)
- [Extractor Hood](../device-types/extractor-hood.md)
- [Humidity Conditioner](../device-types/humidity-conditioner.md)
- [Laundry Dryer](../device-types/laundry-dryer.md)
- [Laundry Washer](../device-types/laundry-washer.md)
- [Microwave Oven](../device-types/microwave-oven.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
- [Water Heater](../device-types/water-heater.md)
