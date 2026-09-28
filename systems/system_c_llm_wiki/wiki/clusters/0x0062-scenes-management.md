---
entity: Scenes Management
ids: ['0x0062']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/scene.xml', 'src/app/clusters/scenes-server/SceneHandlerImpl.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h', 'src/app/clusters/scenes-server/SceneTableImpl.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp', 'src/app/clusters/scenes-server/SceneHandlerImpl.cpp', 'src/app/clusters/scenes-server/scenes-server.h', 'src/app/clusters/scenes-server/ExtensionFieldSets.h', 'src/app/clusters/scenes-server/CodegenIntegration.h', 'src/app/clusters/scenes-server/CodegenIntegration.cpp', 'src/app/clusters/scenes-server/Constants.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h', 'src/app/clusters/scenes-server/CodegenEndpointToIndex.h', 'src/app/clusters/scenes-server/SceneTable.h', 'src/app/clusters/scenes-server/AttributeValuePairValidator.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.h', 'src/app/clusters/scenes-server/SceneTableImpl.cpp', 'src/app/clusters/scenes-server/ScenesIntegrationDelegate.h', 'data_model/1.7/clusters/Scenes.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

`Scenes Management`는 장면(scene)의 구성 및 조작을 위한 속성과 명령을 제공하는 General 클러스터입니다.

- 클러스터 ID: `0x0062`
- 정의: `SCENES_CLUSTER`
- 도메인: `General`
- 클라이언트 및 서버 지원
- 설명: Attributes and commands for scene configuration and manipulation.
- 선택 기능:
  - `SceneNames` (`SN`): 장면 이름을 저장하는 기능
- 전역 장면 식별자:
  - `kGlobalSceneId = 0`
  - `kGlobalSceneGroupId = 0`
  - `kGlobalGroupSceneId = 0x0000`
- 정의된 장면 테이블 최대값:
  - `kMaxScenesPerEndpoint = CHIP_CONFIG_MAX_SCENES_TABLE_SIZE`
  - `kMaxScenesPerFabric = (kMaxScenesPerEndpoint - 1) / 2`

## 스펙

### 데이터 타입

#### `CopyModeBitmap`

`bitmap8` 타입입니다.

| 비트 | 이름 | 설명 |
|---:|---|---|
| 0 | `CopyAllScenes` | scene table의 모든 장면을 복사 |

#### `SceneInfoStruct`

fabric-scoped 구조체입니다.

| Field ID | 이름 | 타입 | 속성 |
|---:|---|---|---|
| 0 | `SceneCount` | `uint8` / `int8u` | 필수 |
| 1 | `CurrentScene` | `uint8` / `int8u` | fabric-sensitive, 기본값 `0xFF`, deprecated |
| 2 | `CurrentGroup` | `group-id` / `group_id` | fabric-sensitive, 기본값 `0`, deprecated |
| 3 | `SceneValid` | `bool` / `boolean` | fabric-sensitive, 기본값 `false` / `0`, deprecated |
| 4 | `RemainingCapacity` | `uint8` / `int8u` | 최대 `253` |

#### `AttributeValuePairStruct`

| Field ID | 이름 | 타입 | 조건 |
|---:|---|---|---|
| 0 | `AttributeID` | `attribute-id` / `attrib_id` | 필수 |
| 1 | `ValueUnsigned8` | `uint8` / `int8u` | 선택, `choice="a"` |
| 2 | `ValueSigned8` | `int8` / `int8s` | 선택, `choice="a"` |
| 3 | `ValueUnsigned16` | `uint16` / `int16u` | 선택, `choice="a"` |
| 4 | `ValueSigned16` | `int16` / `int16s` | 선택, `choice="a"` |
| 5 | `ValueUnsigned32` | `uint32` / `int32u` | 선택, `choice="a"` |
| 6 | `ValueSigned32` | `int32` / `int32s` | 선택, `choice="a"` |
| 7 | `ValueUnsigned64` | `uint64` / `int64u` | 선택, `choice="a"` |
| 8 | `ValueSigned64` | `int64` / `int64s` | 선택, `choice="a"` |

#### `ExtensionFieldSetStruct`

| Field ID | 이름 | 타입 |
|---:|---|---|
| 0 | `ClusterID` | `cluster-id` / `cluster_id` |
| 1 | `AttributeValueList` | `list` / 배열 |

### 속성

| ID | 이름 | 타입 | 접근 |
|---|---|---|---|
| `0x0001` | `SceneTableSize` | `uint16` / `int16u` | 서버, 읽기 |
| `0x0002` | `FabricSceneInfo` | `list` / `array` of `SceneInfoStruct` | 서버, 읽기, fabric-scoped |

글로벌 속성:

- `0xFFFD`: 클러스터 revision
- revision 값: `2`

### 클라이언트 명령

#### `AddScene` (`0x00`)

새 장면을 추가합니다.

- 응답: `AddSceneResponse`
- 접근 권한: `manage`
- fabric-scoped
- CLI: `chip scenes add`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| 0 | `GroupID` | `group-id` / `group_id` | 필수 |
| 1 | `SceneID` | `uint8` / `int8u` | 최대 `254` |
| 2 | `TransitionTime` | `uint32` / `int32u` | 최대 `60000000` |
| 3 | `SceneName` | `string` / `char_string` | 최대 길이 `16` |
| 4 | `ExtensionFieldSetStructs` | `list` / 배열 of `ExtensionFieldSetStruct` | 필수 |

#### `ViewScene` (`0x01`)

요청한 장면의 세부 정보를 반환합니다.

- 응답: `ViewSceneResponse`
- 접근 권한: `operate`
- fabric-scoped
- CLI: `chip scenes view`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| 0 | `GroupID` | `group-id` / `group_id` | 필수 |
| 1 | `SceneID` | `uint8` / `int8u` | 최대 `254` |

#### `RemoveScene` (`0x02`)

지정한 장면을 삭제합니다.

- 응답: `RemoveSceneResponse`
- 접근 권한: `manage`
- fabric-scoped
- CLI: `chip scenes remove`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| 0 | `GroupID` | `group-id` / `group_id` | 필수 |
| 1 | `SceneID` | `uint8` / `int8u` | 최대 `254` |

#### `RemoveAllScenes` (`0x03`)

지정한 `GroupID`의 모든 장면을 삭제합니다.

- 응답: `RemoveAllScenesResponse`
- 접근 권한: `manage`
- fabric-scoped
- CLI: `chip scenes rmall`

| Field ID | 이름 | 타입 |
|---:|---|---|
| 0 | `GroupID` | `group-id` / `group_id` |

#### `StoreScene` (`0x04`)

현재 상태를 지정한 장면 항목에 저장합니다.

- 응답: `StoreSceneResponse`
- 접근 권한: `manage`
- fabric-scoped
- CLI: `chip scenes store`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| 0 | `GroupID` | `group-id` / `group_id` | 필수 |
| 1 | `SceneID` | `uint8` / `int8u` | 최대 `254` |

#### `RecallScene` (`0x05`)

지정한 장면을 복원합니다.

- 접근 권한: `operate`
- fabric-scoped
- CLI: `chip scenes recall`

| Field ID | 이름 | 타입 | 조건 |
|---:|---|---|---|
| 0 | `GroupID` | `group-id` / `group_id` | 필수 |
| 1 | `SceneID` | `uint8` / `int8u` | 최대 `254` |
| 2 | `TransitionTime` | `uint32` / `int32u` | 선택, nullable, 최대 `60000000` |

#### `GetSceneMembership` (`0x06`)

특정 그룹에서 사용 중인 장면 식별자를 조회합니다.

- 응답: `GetSceneMembershipResponse`
- 접근 권한: `operate`
- fabric-scoped
- CLI: `chip scenes get`

| Field ID | 이름 | 타입 |
|---:|---|---|
| 0 | `GroupID` | `group-id` / `group_id` |

#### `CopyScene` (`0x40`)

한 `GroupID`/`SceneID` 쌍에서 다른 쌍으로 장면을 복사합니다.

- 선택 명령
- 응답: `CopySceneResponse`
- 접근 권한: `manage`
- fabric-scoped
- CLI: `chip scenes copy`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| 0 | `Mode` | `CopyModeBitmap` | 최대 `0x01` |
| 1 | `GroupIdentifierFrom` | `group-id` / `group_id` | 필수 |
| 2 | `SceneIdentifierFrom` | `uint8` / `int8u` | 최대 `254` |
| 3 | `GroupIdentifierTo` | `group-id` / `group_id` | 필수 |
| 4 | `SceneIdentifierTo` | `uint8` / `int8u` | 최대 `254` |

### 서버 응답 명령

| 명령 ID | 응답 이름 | 요청 명령 |
|---|---|---|
| `0x00` | `AddSceneResponse` | `AddScene` |
| `0x01` | `ViewSceneResponse` | `ViewScene` |
| `0x02` | `RemoveSceneResponse` | `RemoveScene` |
| `0x03` | `RemoveAllScenesResponse` | `RemoveAllScenes` |
| `0x04` | `StoreSceneResponse` | `StoreScene` |
| `0x06` | `GetSceneMembershipResponse` | `GetSceneMembership` |
| `0x40` | `CopySceneResponse` | `CopyScene` |

각 응답의 공통 필드는 다음과 같습니다.

- `Status`
- 요청에 대응하는 `GroupID` 또는 `GroupIdentifierFrom`
- 요청에 대응하는 `SceneID` 또는 `SceneIdentifierFrom`

추가 응답 필드:

- `ViewSceneResponse`
  - `TransitionTime`
  - `SceneName`
  - `ExtensionFieldSetStructs`
- `GetSceneMembershipResponse`
  - `Capacity`
  - `SceneList`
- `CopySceneResponse`
  - `GroupIdentifierFrom`
  - `SceneIdentifierFrom`

## SDK 정의

### 생성 파일

- `src/app/zap-templates/zcl/data-model/chip/scene.xml`

주요 생성 정의:

```xml
<cluster>
  <name>Scenes Management</name>
  <code>0x0062</code>
  <define>SCENES_CLUSTER</define>
</cluster>
```

### SDK 구조체

생성되는 주요 타입은 다음과 같습니다.

- `CopyModeBitmap`
- `SceneInfoStruct`
- `AttributeValuePairStruct`
- `ExtensionFieldSetStruct`

구조체는 `app::Clusters::ScenesManagement::Structs` 아래에서 사용됩니다.

예시:

```cpp
using AttributeValuePairType =
    app::Clusters::ScenesManagement::Structs::AttributeValuePairStruct::Type;

using AttributeValuePairDecodableType =
    app::Clusters::ScenesManagement::Structs::AttributeValuePairStruct::DecodableType;

using ExtensionFieldSetType =
    app::Clusters::ScenesManagement::Structs::ExtensionFieldSetStruct::Type;

using ExtensionFieldSetDecodableType =
    app::Clusters::ScenesManagement::Structs::ExtensionFieldSetStruct::DecodableType;
```

### 서버 클러스터 인터페이스

파일:

- `src/app/clusters/scenes-server/ScenesManagementCluster.h`

주요 타입:

- `ScenesManagementSceneTable`
- `ScenesManagementTableProvider`
- `ScopedSceneTable`
- `ScenesManagementCluster`

`ScenesManagementCluster::Context`는 다음 의존성을 주입합니다.

```cpp
struct Context
{
    Credentials::GroupDataProvider * groupDataProvider;
    FabricTable * fabricTable;
    const BitMask<ScenesManagement::Feature> features;
    ScenesManagementTableProvider & sceneTableProvider;
    const bool supportsCopyScene;
};
```

주요 공개 메서드:

```cpp
CHIP_ERROR Startup(ServerClusterContext & context) override;
void Shutdown(ClusterShutdownType shutdownType) override;

CHIP_ERROR StoreCurrentGlobalScene(FabricIndex fabricIndex) override;
CHIP_ERROR RecallGlobalScene(FabricIndex fabricIndex) override;
CHIP_ERROR GroupWillBeRemoved(FabricIndex fabricIndex, GroupId groupId) override;

CHIP_ERROR StoreCurrentScene(FabricIndex aFabricIx, GroupId aGroupId, SceneId aSceneId);
CHIP_ERROR RecallScene(FabricIndex aFabricIx, GroupId aGroupId, SceneId aSceneId);
CHIP_ERROR RemoveFabric(FabricIndex aFabricIndex);
```

### 장면 저장 모델

파일:

- `src/app/clusters/scenes-server/SceneTable.h`

`SceneTable`은 다음 정보를 사용해 장면을 식별합니다.

```cpp
struct SceneStorageId
{
    GroupId mGroupId = kGlobalGroupSceneId;
    SceneId mSceneId = kUndefinedSceneId;
};
```

장면 데이터는 `SceneData`에 저장됩니다.

```cpp
struct SceneData
{
    char mName[kSceneNameMaxLength] = { 0 };
    size_t mNameLength = 0;
    SceneTransitionTime mSceneTransitionTimeMs = 0;
    EFStype mExtensionFieldSets;
};
```

관련 상수:

```cpp
inline constexpr GroupId kGlobalGroupSceneId = 0x0000;
inline constexpr SceneId kUndefinedSceneId = 0xff;

static constexpr size_t kSceneNameMaxLength =
    CHIP_CONFIG_SCENES_CLUSTER_MAXIMUM_NAME_LENGTH;

static constexpr size_t kScenesMaxTransitionTime = 60'000'000u;
```

### `SceneHandler`

`SceneHandler`는 Scenes Management와 다른 클러스터 사이의 인터페이스입니다.

필수 구현 메서드:

```cpp
virtual bool SupportsCluster(EndpointId endpoint, ClusterId cluster) = 0;

virtual CHIP_ERROR SerializeAdd(
    EndpointId endpoint,
    const app::Clusters::ScenesManagement::Structs::ExtensionFieldSetStruct::DecodableType & extensionFieldSet,
    MutableByteSpan & serialisedBytes) = 0;

virtual CHIP_ERROR SerializeSave(
    EndpointId endpoint,
    ClusterId cluster,
    MutableByteSpan & serializedBytes) = 0;

virtual CHIP_ERROR Deserialize(
    EndpointId endpoint,
    ClusterId cluster,
    const ByteSpan & serializedBytes,
    app::Clusters::ScenesManagement::Structs::ExtensionFieldSetStruct::Type & extensionFieldSet) = 0;

virtual CHIP_ERROR ApplyScene(
    EndpointId endpoint,
    ClusterId cluster,
    const ByteSpan & serializedBytes,
    TransitionTimeMs timeMs) = 0;
```

일반적으로 각 `<endpoint, cluster>` 쌍에는 해당 쌍을 처리하는 `SceneHandler`가 하나만 등록됩니다.

### `AttributeValuePairValidator`

파일:

- `src/app/clusters/scenes-server/AttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp`

인터페이스:

```cpp
virtual CHIP_ERROR Validate(
    const app::ConcreteClusterPath & clusterPath,
    AttributeValuePairType & value) = 0;
```

`CodegenAttributeValuePairValidator::Validate`는 다음을 수행합니다.

- `emberAfLocateAttributeMetadata`를 사용해 속성 메타데이터 조회
- 지원되지 않는 속성이면 `UnsupportedAttribute` 반환
- `AttributeValuePairType`에서 정확히 하나의 값만 채워졌는지 확인
- 속성 기본 타입에 맞는 value 필드 확인
- 속성의 min/max 또는 타입 범위에 맞게 값 조정
- nullable 속성의 범위를 벗어난 값은 null로 설정

지원되는 주요 타입:

- `ZCL_BOOLEAN_ATTRIBUTE_TYPE`
- `ZCL_INT8U_ATTRIBUTE_TYPE`
- `ZCL_INT16U_ATTRIBUTE_TYPE`
- `ZCL_INT24U_ATTRIBUTE_TYPE`
- `ZCL_INT32U_ATTRIBUTE_TYPE`
- `ZCL_INT40U_ATTRIBUTE_TYPE`
- `ZCL_INT48U_ATTRIBUTE_TYPE`
- `ZCL_INT56U_ATTRIBUTE_TYPE`
- `ZCL_INT64U_ATTRIBUTE_TYPE`
- `ZCL_INT8S_ATTRIBUTE_TYPE`
- `ZCL_INT16S_ATTRIBUTE_TYPE`
- `ZCL_INT24S_ATTRIBUTE_TYPE`
- `ZCL_INT32S_ATTRIBUTE_TYPE`
- `ZCL_INT40S_ATTRIBUTE_TYPE`
- `ZCL_INT48S_ATTRIBUTE_TYPE`
- `ZCL_INT56S_ATTRIBUTE_TYPE`
- `ZCL_INT64S_ATTRIBUTE_TYPE`

### `DefaultSceneHandlerImpl`

파일:

- `src/app/clusters/scenes-server/SceneHandlerImpl.h`
- `src/app/clusters/scenes-server/SceneHandlerImpl.cpp`

`DefaultSceneHandlerImpl`은 `SceneHandler`의 기본 구현입니다.

주요 메서드:

```cpp
virtual CHIP_ERROR EncodeAttributeValueList(
    const List<AttributeValuePairType> & aVlist,
    MutableByteSpan & serializedBytes);

virtual CHIP_ERROR DecodeAttributeValueList(
    const ByteSpan & serializedBytes,
    DecodableList<AttributeValuePairDecodableType> & aVlist);

CHIP_ERROR SerializeAdd(
    EndpointId endpoint,
    const ExtensionFieldSetDecodableType & extensionFieldSet,
    MutableByteSpan & serializedBytes) override;

CHIP_ERROR Deserialize(
    EndpointId endpoint,
    ClusterId cluster,
    const ByteSpan & serializedBytes,
    ExtensionFieldSetType & extensionFieldSet) override;
```

동작:

- `EncodeAttributeValueList`는 `AttributeValuePairType` 목록을 TLV array로 인코딩합니다.
- `DecodeAttributeValueList`는 TLV array를 `DecodableList<AttributeValuePairDecodableType>`로 디코딩합니다.
- `SerializeAdd`는 `ExtensionFieldSetStruct`의 각 `AttributeValuePairType`을 검증한 뒤 인코딩합니다.
- `Deserialize`는 저장된 TLV 데이터를 디코딩하여 `ExtensionFieldSetType`으로 구성합니다.
- `kMaxAvPair`는 `CHIP_CONFIG_SCENES_MAX_AV_PAIRS_EFS`로 정의됩니다.

### `ExtensionFieldSets`

파일:

- `src/app/clusters/scenes-server/ExtensionFieldSets.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp`

관련 상수:

```cpp
static constexpr uint8_t kInvalidPosition = 0xff;
static constexpr uint8_t kMaxClustersPerScene =
    CHIP_CONFIG_SCENES_MAX_CLUSTERS_PER_SCENE;
static constexpr uint8_t kMaxFieldBytesPerCluster =
    CHIP_CONFIG_SCENES_MAX_EXTENSION_FIELDSET_SIZE_PER_CLUSTER;
```

`ExtensionFieldSet`은 하나의 클러스터에 대한 직렬화 데이터를 보관합니다.

```cpp
struct ExtensionFieldSet
{
    ClusterId mID = kInvalidClusterId;
    uint8_t mBytesBuffer[kMaxFieldBytesPerCluster] = { 0 };
    uint8_t mUsedBytes = 0;
};
```

`ExtensionFieldSetsImpl` 주요 메서드:

```cpp
CHIP_ERROR Serialize(TLV::TLVWriter & writer) const override;
CHIP_ERROR Deserialize(TLV::TLVReader & reader) override;
void Clear() override;
bool IsEmpty() const override;
uint8_t GetFieldSetCount() const override;

CHIP_ERROR InsertFieldSet(const ExtensionFieldSet & field);
CHIP_ERROR GetFieldSetAtPosition(ExtensionFieldSet & field, uint8_t position) const;
CHIP_ERROR RemoveFieldAtPosition(uint8_t position);
```

동작:

- 동일한 `ClusterId`가 이미 존재하면 해당 field set을 덮어씁니다.
- 비어 있는 위치가 있으면 새 field set을 삽입합니다.
- field set 배열이 가득 차면 `CHIP_ERROR_NO_MEMORY`를 반환합니다.
- 저장된 field set 수가 OTA 이후 `kMaxClustersPerScene`보다 크면 `CHIP_ERROR_BUFFER_TOO_SMALL`을 반환합니다.

### `DefaultSceneTableImpl`

파일:

- `src/app/clusters/scenes-server/SceneTableImpl.h`
- `src/app/clusters/scenes-server/SceneTableImpl.cpp`

`DefaultSceneTableImpl`은 `PersistentStorageDelegate`를 사용해 장면 테이블을 비휘발성 저장소에 저장합니다.

```cpp
using SceneTableBase =
    SceneTable<scenes::ExtensionFieldSetsImpl>;

class DefaultSceneTableImpl :
    public SceneTableBase,
    public app::Storage::FabricTableImpl<
        SceneTableBase::SceneStorageId,
        SceneTableBase::SceneData>
```

주요 기능:

- endpoint별 장면 테이블 관리
- fabric별 장면 수 및 용량 관리
- `GroupID`별 장면 목록 조회
- 그룹 삭제 시 그룹의 모든 장면 삭제
- fabric 제거 시 fabric 관련 장면 삭제
- `SceneHandler` 등록 및 해제
- `SceneSaveEFS` 및 `SceneApplyEFS`를 통한 extension field set 저장 및 적용

인스턴스 접근 함수:

```cpp
DefaultSceneTableImpl * GetSceneTableImpl(
    EndpointId endpoint = kInvalidEndpointId,
    uint16_t endpointTableSize = kMaxScenesPerEndpoint);
```

`GetSceneTableImpl`은 전역 `DefaultSceneTableImpl` 인스턴스를 반환하며, 반환 포인터를 캐시하지 않는 방식으로 사용됩니다.

### 서버 초기화 및 codegen 통합

파일:

- `src/app/clusters/scenes-server/CodegenIntegration.h`
- `src/app/clusters/scenes-server/CodegenIntegration.cpp`
- `src/app/clusters/scenes-server/scenes-server.h`

`ScenesServer`는 다음 기능을 제공합니다.

```cpp
static ScenesServer & Instance();

void GroupWillBeRemoved(
    FabricIndex aFabricIx,
    EndpointId aEndpointId,
    GroupId aGroupId);

void StoreCurrentScene(
    FabricIndex aFabricIx,
    EndpointId aEndpointId,
    GroupId aGroupId,
    SceneId aSceneId);

void RecallScene(
    FabricIndex aFabricIx,
    EndpointId aEndpointId,
    GroupId aGroupId,
    SceneId aSceneId);

bool IsHandlerRegistered(
    EndpointId endpointId,
    scenes::SceneHandler * handler);

void RegisterSceneHandler(
    EndpointId endpointId,
    scenes::SceneHandler * handler);

void UnregisterSceneHandler(
    EndpointId endpointId,
    scenes::SceneHandler * handler);

void RemoveFabric(
    EndpointId aEndpointId,
    FabricIndex aFabricIndex);
```

endpoint의 클러스터 인스턴스는 다음 함수로 찾습니다.

```cpp
ScenesManagementCluster * FindClusterOnEndpoint(EndpointId endpointId);
```

초기화 및 종료 콜백:

```cpp
void MatterScenesManagementClusterInitCallback(EndpointId endpointId);

void MatterScenesManagementClusterShutdownCallback(
    EndpointId endpointId,
    MatterClusterShutdownType shutdownType);

void MatterScenesManagementPluginServerInitCallback();
```

`IntegrationDelegate::CreateRegistration`은 다음 정보를 기반으로 `ScenesManagementCluster`를 생성합니다.

- `endpointId`
- `SceneTableSize`
- `featureMap`
- `CopyScene` 지원 여부
- `Credentials::GetGroupDataProvider()`
- `Server::GetInstance().GetFabricTable()`

`CopyScene` 지원 여부는 `acceptedCommandList`에 `ScenesManagement::Commands::CopyScene::Id`가 포함되어 있는지로 확인합니다.

## 구현

### 명령 처리 흐름

`ScenesManagementCluster::InvokeCommand`는 다음 명령을 처리합니다.

```cpp
AddScene
ViewScene
RemoveScene
RemoveAllScenes
StoreScene
RecallScene
GetSceneMembership
CopyScene
```

각 요청은 해당 `DecodableType`으로 디코딩된 후 다음 핸들러로 전달됩니다.

```cpp
HandleAddScene
HandleViewScene
HandleRemoveScene
HandleRemoveAllScenes
HandleStoreScene
HandleRecallScene
HandleGetSceneMembership
HandleCopyScene
```

지원하지 않는 명령은 `Status::UnsupportedCommand`를 반환합니다.

### `AddScene`

`HandleAddScene`은 다음 순서로 처리합니다.

1. `SceneTable`을 획득합니다.
2. `TransitionTime`, `SceneName`, `SceneID` 제약을 검사합니다.
3. `GroupID`가 유효한 endpoint를 포함하는지 확인합니다.
4. `SceneNames` 기능이 활성화된 경우 `SceneName`을 저장합니다.
5. `ExtensionFieldSetStructs`를 순회합니다.
6. 각 field set에 대해 등록된 `SceneHandler::SupportsCluster`를 확인합니다.
7. 지원하는 handler의 `SerializeAdd`를 호출합니다.
8. 직렬화된 데이터를 `ExtensionFieldSet`으로 저장합니다.
9. fabric의 남은 용량을 확인합니다.
10. `SetSceneTableEntry`로 장면을 저장합니다.
11. `UpdateFabricSceneInfo`로 `FabricSceneInfo`를 갱신합니다.

다음 경우 응답 상태가 실패합니다.

- `SceneID == scenes::kUndefinedSceneId`
- `TransitionTime > scenes::kScenesMaxTransitionTime`
- `SceneName` 길이 초과
- 그룹에 endpoint가 없음
- 장면 테이블 용량 부족

### `ViewScene`

`HandleViewScene`은 다음 작업을 수행합니다.

- `SceneTableEntry`를 조회합니다.
- 저장된 `ExtensionFieldSet`을 순회합니다.
- 각 `ClusterID`에 대해 지원하는 `SceneHandler`를 찾습니다.
- `SceneHandler::Deserialize`로 응답용 `ExtensionFieldSetStruct`를 구성합니다.
- `TransitionTime`, `SceneName`, `ExtensionFieldSetStructs`를 응답에 설정합니다.

응답에 사용되는 메모리는 다음 입력 버퍼가 제공합니다.

- `scene`
- `responseEFSBuffer`

### `RemoveScene`

`HandleRemoveScene`은 다음 순서로 동작합니다.

1. `SceneID` 제약을 확인합니다.
2. 지정한 `GroupID`와 `SceneID`로 `SceneStorageId`를 만듭니다.
3. 장면을 조회합니다.
4. `RemoveSceneTableEntry`로 장면을 삭제합니다.
5. `UpdateFabricSceneInfo`를 호출합니다.

### `RemoveAllScenes`

`HandleRemoveAllScenes`는 다음 작업을 수행합니다.

- `GroupID`에 해당하는 endpoint 유효성을 검사합니다.
- `DeleteAllScenesInGroup`을 호출합니다.
- `UpdateFabricSceneInfo`를 호출합니다.

### `StoreScene`

`HandleStoreScene`은 `StoreSceneParse`를 호출합니다.

`StoreSceneParse`는 다음과 같이 현재 상태를 저장합니다.

- 기존 scene entry를 조회합니다.
- 기존 entry가 있으면 `mExtensionFieldSets`를 초기화합니다.
- `SceneSaveEFS`를 통해 endpoint의 클러스터 상태를 저장합니다.
- `SetSceneTableEntry`로 장면을 저장합니다.
- `FabricSceneInfo`를 갱신합니다.

기존 장면을 저장할 때 `SceneNames` 기능이 비활성화되어 있으면 장면 이름을 비웁니다.

### `RecallScene`

`HandleRecallScene`은 `RecallSceneParse`를 호출합니다.

`RecallSceneParse`는 다음과 같이 동작합니다.

- `SceneStorageId`로 저장된 장면을 조회합니다.
- 요청에 nullable이 아닌 `TransitionTime`이 있으면 저장된 전환 시간을 덮어씁니다.
- `SceneApplyEFS`를 호출해 각 클러스터의 상태를 적용합니다.
- `FabricSceneInfo`를 갱신합니다.

전역 장면은 다음 상수를 사용합니다.

```cpp
kGlobalSceneGroupId
kGlobalSceneId
```

관련 메서드:

```cpp
CHIP_ERROR StoreCurrentGlobalScene(FabricIndex fabricIndex);
CHIP_ERROR RecallGlobalScene(FabricIndex fabricIndex);
```

### `GetSceneMembership`

`HandleGetSceneMembership`은 다음 정보를 응답합니다.

- `Capacity`
- 요청한 `GroupID`의 `SceneList`

`DefaultSceneTableImpl::GetAllSceneIdsInGroup`은 fabric 저장소를 순회하여 해당 `GroupID`의 `SceneId`를 수집합니다.

### `CopyScene`

`HandleCopyScene`은 `Mode`의 `CopyAllScenes` 비트에 따라 동작합니다.

- `CopyAllScenes`가 설정되지 않은 경우:
  - 하나의 source scene을 destination으로 복사합니다.
- `CopyAllScenes`가 설정된 경우:
  - source `GroupIdentifierFrom`의 모든 장면을 조회합니다.
  - 각 장면을 `GroupIdentifierTo`로 복사합니다.

destination 장면이 기존에 있으면 새 용량을 소비하지 않고 덮어씁니다. destination 장면이 없으면 `GetRemainingCapacity`로 용량을 확인합니다.

### fabric 및 그룹 수명주기

`ScenesManagementCluster`는 `FabricTable::Delegate`를 구현합니다.

```cpp
void OnFabricRemoved(
    const FabricTable & fabricTable,
    FabricIndex fabricIndex) override;

void OnFabricCommitted(
    const FabricTable & fabricTable,
    FabricIndex fabricIndex) override;
```

- `OnFabricRemoved`:
  - fabric에 속한 장면을 삭제합니다.
  - 해당 fabric의 `SceneInfoStruct`를 제거합니다.
- `OnFabricCommitted`:
  - 해당 fabric의 `FabricSceneInfo`를 갱신합니다.

그룹 제거 시:

```cpp
CHIP_ERROR GroupWillBeRemoved(
    FabricIndex aFabricIdx,
    GroupId aGroupId);
```

해당 그룹에 속한 모든 장면을 삭제합니다.

### 영속화

`DefaultSceneTableImpl`은 `FabricTableImpl`을 통해 scene 데이터를 저장합니다.

저장되는 주요 데이터:

- `GroupID`
- `SceneID`
- `SceneName`
- `TransitionTime`
- `ExtensionFieldSets`

scene 저장 TLV 태그:

```cpp
enum class TagScene : uint8_t
{
    kGroupId,
    kSceneId,
    kName,
    kTransitionTimeMs,
};
```

`ExtensionFieldSet` 저장 TLV 태그:

```cpp
enum class TagEFS : uint8_t
{
    kFieldSetArrayContainer = 1,
    kClusterID,
    kClusterFieldSetData,
};
```

기본 serializer 설정:

- `Serializer::kMaxPerFabric()`: `kMaxScenesPerFabric`
- `Serializer::kMaxPerEndpoint()`: `kMaxScenesPerEndpoint`
- `Serializer::kEntryMaxBytes()`: `CHIP_CONFIG_SCENES_MAX_SERIALIZED_SCENE_SIZE_BYTES`
- `Serializer::kFabricMaxBytes()`: `128`

### 전환 시간 처리

`SceneData::mSceneTransitionTimeMs`는 장면 전환 시간을 밀리초 단위로 저장합니다.

```cpp
using TransitionTimeMs = uint32_t;
using SceneTransitionTime = uint32_t;
```

최대 전환 시간:

```cpp
static constexpr size_t kScenesMaxTransitionTime = 60'000'000u;
```

`DefaultSceneHandlerImpl::TransitionTimeInterface`는 클러스터에 기존 비동기 처리 메커니즘이 없는 경우 endpoint별 이벤트 제어 객체를 사용해 전환을 지원할 수 있도록 합니다.

## 관련 문서

- `src/app/zap-templates/zcl/data-model/chip/scene.xml`
- `data_model/1.7/clusters/Scenes.xml`
- `src/app/clusters/scenes-server/ScenesManagementCluster.h`
- `src/app/clusters/scenes-server/ScenesManagementCluster.cpp`
- `src/app/clusters/scenes-server/SceneTable.h`
- `src/app/clusters/scenes-server/SceneTableImpl.h`
- `src/app/clusters/scenes-server/SceneTableImpl.cpp`
- `src/app/clusters/scenes-server/SceneHandlerImpl.h`
- `src/app/clusters/scenes-server/SceneHandlerImpl.cpp`
- `src/app/clusters/scenes-server/AttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp`
- `src/app/clusters/scenes-server/ExtensionFieldSets.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp`
- `src/app/clusters/scenes-server/CodegenIntegration.h`
- `src/app/clusters/scenes-server/CodegenIntegration.cpp`
- `src/app/clusters/scenes-server/CodegenEndpointToIndex.h`
- `src/app/clusters/scenes-server/Constants.h`
- `src/app/clusters/scenes-server/ScenesIntegrationDelegate.h`
- `src/app/clusters/scenes-server/scenes-server.h`

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
