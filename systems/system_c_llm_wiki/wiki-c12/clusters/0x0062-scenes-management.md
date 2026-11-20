---
entity: Scenes Management
ids: ['0x0062']
source_paths: ['data_model/1.7/clusters/Scenes.xml', 'src/app/clusters/scenes-server/AttributeValuePairValidator.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h', 'src/app/clusters/scenes-server/CodegenEndpointToIndex.h', 'src/app/clusters/scenes-server/CodegenIntegration.cpp', 'src/app/clusters/scenes-server/CodegenIntegration.h', 'src/app/clusters/scenes-server/Constants.h', 'src/app/clusters/scenes-server/ExtensionFieldSets.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h', 'src/app/clusters/scenes-server/SceneHandlerImpl.cpp', 'src/app/clusters/scenes-server/SceneHandlerImpl.h', 'src/app/clusters/scenes-server/SceneTable.h', 'src/app/clusters/scenes-server/SceneTableImpl.cpp', 'src/app/clusters/scenes-server/SceneTableImpl.h', 'src/app/clusters/scenes-server/ScenesIntegrationDelegate.h', 'src/app/clusters/scenes-server/ScenesManagementCluster.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.h', 'src/app/clusters/scenes-server/scenes-server.h', 'src/app/zap-templates/zcl/data-model/chip/scene.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Scenes Management

## 개요

Scenes Management는 장면 구성과 조작을 위한 속성 및 명령을 제공한다. 장면에는 이름, 전환 시간, 클러스터별 속성 데이터를 나타내는 `ExtensionFieldSetStruct`가 포함된다.

- 클러스터 ID: `0x0062`
- 스펙 이름: `Scenes Management Cluster`
- revision: `2`
- 분류: hierarchy=`base`, role=`application`, scope=`Endpoint`
- PICS 코드: `S`
- 선택 기능: `SceneNames`
- 주요 동작: `AddScene`, `ViewScene`, `RemoveScene`, `RemoveAllScenes`, `StoreScene`, `RecallScene`, `GetSceneMembership`, `CopyScene`

구현은 `ScenesManagementCluster`, 장면 저장소인 `SceneTable`, 클러스터별 데이터를 처리하는 `SceneHandler`, 코드 생성 통합 계층으로 구성된다.

## 스펙

출처: `data_model/1.7/clusters/Scenes.xml`

### 변경 이력

| revision | 변경 내용 |
|---|---|
| `1` | ZCL Scenes Cluster 기반. 클러스터 ID를 `0x0062`, 이름을 Scenes Management로 변경하고 provisional 상태 제거. 속성 `SceneCount`, `CurrentScene`, `CurrentGroup`, `SceneValid`, `NameSupport` 제거. 기능 `Explicit`, `TableSize`, `FabricScenes` 제거. 명령 `EnhancedAddScene`, `EnhancedAddSceneResponse`, `EnhancedViewScene`, `EnhancedViewSceneResponse` 제거. `AddScene`, `ViewSceneResponse`, `RecallScene`의 `TransitionTime`을 밀리초 단위로 변경. |
| `2` | `SceneInfoStruct`의 `CurrentScene`, `CurrentGroup`, `SceneValid` 필드를 deprecated 처리. |

### 기능

| 비트 | 코드 | 이름 | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `SN` | `SceneNames` | 선택 | 장면 이름 저장 기능 |

### 데이터 타입

#### `CopyModeBitmap`

| 비트 | 이름 | 적합성 | 설명 |
|---|---|---|---|
| `0` | `CopyAllScenes` | 필수 | 장면 테이블의 모든 장면 복사 |

#### `AttributeValuePairStruct`

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `AttributeID` | `attribute-id` | 필수 |
| `1` | `ValueUnsigned8` | `uint8` | 선택, choice=`a` |
| `2` | `ValueSigned8` | `int8` | 선택, choice=`a` |
| `3` | `ValueUnsigned16` | `uint16` | 선택, choice=`a` |
| `4` | `ValueSigned16` | `int16` | 선택, choice=`a` |
| `5` | `ValueUnsigned32` | `uint32` | 선택, choice=`a` |
| `6` | `ValueSigned32` | `int32` | 선택, choice=`a` |
| `7` | `ValueUnsigned64` | `uint64` | 선택, choice=`a` |
| `8` | `ValueSigned64` | `int64` | 선택, choice=`a` |

#### `ExtensionFieldSetStruct`

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `ClusterID` | `cluster-id` | 필수 |
| `1` | `AttributeValueList` | `list`, 항목 `AttributeValuePairStruct` | 필수 |

#### `SceneInfoStruct`

구조체는 `fabricScoped="true"`이다.

| 필드 ID | 이름 | 타입 | 기본값 | 조건 및 제약 |
|---|---|---|---|---|
| `0` | `SceneCount` | `uint8` | — | 필수 |
| `1` | `CurrentScene` | `uint8` | `0xFF` | `fabricSensitive="true"`, revision `2`에서 deprecated |
| `2` | `CurrentGroup` | `group-id` | `0` | `fabricSensitive="true"`, revision `2`에서 deprecated |
| `3` | `SceneValid` | `bool` | `false` | `fabricSensitive="true"`, revision `2`에서 deprecated |
| `4` | `RemainingCapacity` | `uint8` | — | 필수, 최대 `253` |

`CurrentScene`, `CurrentGroup`, `SceneValid`의 XML 적합성에는 `otherwiseConform` 아래 `mandatoryConform`과 `deprecateConform`이 함께 명시되어 있다.

### 속성

| ID | 이름 | 타입 | 적합성 | 접근 및 특성 |
|---|---|---|---|---|
| `0x0000` | `DoNotUse` | 미지정 | 금지 | 읽기, `view` |
| `0x0001` | `SceneTableSize` | `uint16` | 필수 | 읽기, `view`, persistence=`fixed` |
| `0x0002` | `FabricSceneInfo` | `list`, 항목 `SceneInfoStruct` | 필수 | 읽기, `view`, `fabricScoped="true"` |

`SceneTableSize`, `FabricSceneInfo` 등의 일부 제약은 빈 `<desc/>`로 제공되어 있으며, 구체적인 내용은 입력 XML에 없다.

### 명령

모든 요청 명령은 `commandToServer` 방향이며 `fabricScoped="true"`이다.

| ID | 명령 | 호출 권한 | 적합성 | 응답 |
|---|---|---|---|---|
| `0x00` | `AddScene` | `manage` | 필수 | `AddSceneResponse` |
| `0x01` | `ViewScene` | `operate` | 필수 | `ViewSceneResponse` |
| `0x02` | `RemoveScene` | `manage` | 필수 | `RemoveSceneResponse` |
| `0x03` | `RemoveAllScenes` | `manage` | 필수 | `RemoveAllScenesResponse` |
| `0x04` | `StoreScene` | `manage` | 필수 | `StoreSceneResponse` |
| `0x05` | `RecallScene` | `operate` | 필수 | XML의 `response="Y"` |
| `0x06` | `GetSceneMembership` | `operate` | 필수 | `GetSceneMembershipResponse` |
| `0x40` | `CopyScene` | `manage` | 선택 | `CopySceneResponse` |

#### 요청 필드

아래에서 별도로 표시하지 않은 필드는 필수이다.

| 명령 | 필드 ID: 이름 — 타입 및 제약 |
|---|---|
| `AddScene` | `0`: `GroupID` — `group-id`<br>`1`: `SceneID` — `uint8`, 최대 `254`<br>`2`: `TransitionTime` — `uint32`, 최대 `60000000`<br>`3`: `SceneName` — `string`, 최대 길이 `16`<br>`4`: `ExtensionFieldSetStructs` — `list`, 항목 `ExtensionFieldSetStruct` |
| `ViewScene` | `0`: `GroupID` — `group-id`<br>`1`: `SceneID` — `uint8`, 최대 `254` |
| `RemoveScene` | `0`: `GroupID` — `group-id`<br>`1`: `SceneID` — `uint8`, 최대 `254` |
| `RemoveAllScenes` | `0`: `GroupID` — `group-id` |
| `StoreScene` | `0`: `GroupID` — `group-id`<br>`1`: `SceneID` — `uint8`, 최대 `254` |
| `RecallScene` | `0`: `GroupID` — `group-id`<br>`1`: `SceneID` — `uint8`, 최대 `254`<br>`2`: `TransitionTime` — `uint32`, 선택, nullable, 최대 `60000000` |
| `GetSceneMembership` | `0`: `GroupID` — `group-id` |
| `CopyScene` | `0`: `Mode` — `CopyModeBitmap`<br>`1`: `GroupIdentifierFrom` — `group-id`<br>`2`: `SceneIdentifierFrom` — `uint8`, 최대 `254`<br>`3`: `GroupIdentifierTo` — `group-id`<br>`4`: `SceneIdentifierTo` — `uint8`, 최대 `254` |

`TransitionTime`의 단위는 밀리초이다. `SceneNames`가 선택 기능이어도 `AddScene`의 `SceneName` 필드 자체는 필수로 정의되어 있다.

#### 응답 필드

응답 방향은 `responseFromServer`이다. `CopySceneResponse`는 `CopyScene` 지원 시 필수이며, 나머지 아래 응답은 필수이다.

| ID | 응답 | 필드 ID: 이름 — 타입 및 조건 |
|---|---|---|
| `0x00` | `AddSceneResponse` | `0`: `Status` — `status`<br>`1`: `GroupID` — `group-id`<br>`2`: `SceneID` — `uint8`, 최대 `254` |
| `0x01` | `ViewSceneResponse` | `0`: `Status` — `status`<br>`1`: `GroupID` — `group-id`<br>`2`: `SceneID` — `uint8`, 최대 `254`<br>`3`: `TransitionTime` — `uint32`, 최대 `60000000`<br>`4`: `SceneName` — `string`, 최대 길이 `16`<br>`5`: `ExtensionFieldSetStructs` — `list`, 항목 `ExtensionFieldSetStruct` |
| `0x02` | `RemoveSceneResponse` | `0`: `Status` — `status`<br>`1`: `GroupID` — `group-id`<br>`2`: `SceneID` — `uint8`, 최대 `254` |
| `0x03` | `RemoveAllScenesResponse` | `0`: `Status` — `status`<br>`1`: `GroupID` — `group-id` |
| `0x04` | `StoreSceneResponse` | `0`: `Status` — `status`<br>`1`: `GroupID` — `group-id`<br>`2`: `SceneID` — `uint8`, 최대 `254` |
| `0x06` | `GetSceneMembershipResponse` | `0`: `Status` — `status`<br>`1`: `Capacity` — `uint8`, nullable<br>`2`: `GroupID` — `group-id`<br>`3`: `SceneList` — `list`, 항목 `uint8` |
| `0x40` | `CopySceneResponse` | `0`: `Status` — `status`<br>`1`: `GroupIdentifierFrom` — `group-id`<br>`2`: `SceneIdentifierFrom` — `uint8`, 최대 `254` |

조건부 필수 필드:

- `ViewSceneResponse`: `Status`가 `SUCCESS`이면 `TransitionTime`, `SceneName`, `ExtensionFieldSetStructs`가 필수이다.
- `GetSceneMembershipResponse`: `Status`가 `SUCCESS`이면 `SceneList`가 필수이다.
- 나머지 응답 필드는 필수이다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/scene.xml`

### 생성 정보 및 클러스터 메타데이터

입력 XML은 Alchemy 생성 파일이며 직접 편집하지 않도록 표시되어 있다.

| 항목 | 값 |
|---|---|
| 생성 원본 | `src/app_clusters/Scenes.adoc` |
| Git | `0.9-1.7-winter2027` |
| Alchemy | `v1.7.10` |
| 이름 | `Scenes Management` |
| 클러스터 코드 | `0x0062` |
| 도메인 | `General` |
| define | `SCENES_CLUSTER` |
| 전역 속성 | `0xFFFD`, 값 `2` |

`client`와 `server`가 모두 활성화되어 있으며, 두 요소 모두 `tick="false"`, `init="false"`로 정의된다.

### 타입 및 속성 표현

SDK XML은 스펙의 이름과 필드 ID를 유지하면서 다음 타입 표기를 사용한다.

| 스펙 타입 | SDK 타입 |
|---|---|
| `uint8`, `uint16`, `uint32`, `uint64` | `int8u`, `int16u`, `int32u`, `int64u` |
| `int8`, `int16`, `int32`, `int64` | `int8s`, `int16s`, `int32s`, `int64s` |
| `attribute-id` | `attrib_id` |
| `cluster-id` | `cluster_id` |
| `group-id` | `group_id` |
| `bool` | `boolean` |
| `string` | `char_string` |

- `CopyModeBitmap`은 `bitmap8`이며, `CopyAllScenes`의 mask는 `0x01`이다.
- `CopyScene`의 `Mode`에는 최대값 `0x01`이 명시된다.
- `AttributeValuePairStruct`의 값 필드는 `optional="true"`와 choice=`a`를 유지한다.
- `SceneInfoStruct`는 `isFabricScoped="true"`이다.
- `CurrentScene`, `CurrentGroup`, `SceneValid`는 `isFabricSensitive="true"`로 유지되지만, 제공된 SDK XML에는 deprecated 표기가 없다.
- `SceneValid`의 SDK 기본값은 `0`이다.

| 속성 | 코드 | define | SDK 타입 |
|---|---|---|---|
| `SceneTableSize` | `0x0001` | `SCENE_TABLE_SIZE` | `int16u` |
| `FabricSceneInfo` | `0x0002` | `FABRIC_SCENE_INFO` | `array`, entryType=`SceneInfoStruct` |

`DoNotUse`는 제공된 SDK XML에 정의되어 있지 않다.

### 명령 메타데이터

- 요청은 `source="client"`, 응답은 `source="server"`로 정의된다.
- 모든 요청에 `isFabricScoped="true"`가 지정된다.
- `AddScene`, `RemoveScene`, `RemoveAllScenes`, `StoreScene`, `CopyScene`은 `manage` 호출 권한을 명시한다.
- `ViewScene`, `RecallScene`, `GetSceneMembership`에는 별도 `<access>` 요소가 없다.
- 모든 정의된 응답은 `disableDefaultResponse="true"`이다.
- `ViewSceneResponse`의 `TransitionTime`, `SceneName`, `ExtensionFieldSetStructs`와 `GetSceneMembershipResponse`의 `SceneList`는 SDK에서 `optional="true"`로 표현된다.
- `CopySceneResponse`는 `optional="true"`와 함께 `CopyScene`에 대한 `mandatoryConform`을 갖는다.

### CLI 메타데이터

다음은 SDK XML에 기록된 `cli` 값이다.

| 명령 | `cli` |
|---|---|
| `AddScene` | `chip scenes add` |
| `ViewScene` | `chip scenes view` |
| `RemoveScene` | `chip scenes remove` |
| `RemoveAllScenes` | `chip scenes rmall` |
| `StoreScene` | `chip scenes store` |
| `RecallScene` | `chip scenes recall` |
| `GetSceneMembership` | `chip scenes get` |
| `CopyScene` | `chip scenes copy` |

## 구현

### 구성 및 의존성

주요 파일:

- `src/app/clusters/scenes-server/ScenesManagementCluster.h`
- `src/app/clusters/scenes-server/ScenesManagementCluster.cpp`
- `src/app/clusters/scenes-server/ScenesIntegrationDelegate.h`

`ScenesManagementCluster`는 다음 인터페이스를 구현한다.

- `DefaultServerCluster`
- `FabricTable::Delegate`
- `scenes::ScenesIntegrationDelegate`

`Context`로 주입되는 의존성은 다음과 같다.

| 멤버 | 역할 |
|---|---|
| `groupDataProvider` | 그룹 및 Endpoint 소속 확인 |
| `fabricTable` | Fabric 정보와 수명주기 알림 |
| `features` | `ScenesManagement::Feature` 비트 집합 |
| `sceneTableProvider` | 장면 테이블 접근 |
| `supportsCopyScene` | `CopyScene` 지원 여부 |

`ScenesManagementTableProvider`는 `Take()`와 `Release()`를 제공한다. `ScopedSceneTable`은 생성 시 `Take()`, 소멸 시 `Release()`를 호출하며, `Take()`가 `nullptr`을 반환하면 `VerifyOrDie`로 실패한다.

### 클러스터 수명주기와 속성

- `Startup`
  - 장면 테이블에 `context.storage`와 `context.provider`를 전달하여 초기화한다.
  - Fabric delegate를 등록한다.
  - 기존 Fabric마다 `UpdateFabricSceneInfo`를 호출한다.
  - `DefaultServerCluster::Startup`을 호출한다.
- `Shutdown`
  - Fabric delegate를 제거한다.
  - `ClusterShutdownType::kPermanentRemove`이면 `ClearPersistentData`를 호출한다.
- `ClearPersistentData`
  - 시작된 상태를 요구한다.
  - 장면 테이블의 `RemoveEndpoint`를 호출한다.
- `OnFabricCommitted`
  - 해당 Fabric의 `FabricSceneInfo`를 갱신한다.
- `OnFabricRemoved`
  - 저장된 Fabric 장면을 제거하고 메모리의 `SceneInfoStruct`를 삭제한다.

`ReadAttribute`는 `ClusterRevision`, `FeatureMap`, `SceneTableSize`, `FabricSceneInfo`를 처리한다. `FabricSceneInfo`를 읽을 때는 다른 Fabric의 사용량을 반영하도록 각 항목의 `remainingCapacity`를 다시 조회한다.

`UpdateFabricSceneInfo`는 장면 수와 잔여 용량을 갱신하고 `NotifyAttributeChanged`를 호출한다. 이때 deprecated 필드는 다음 값으로 설정된다.

| 구현 필드 | 설정값 |
|---|---|
| `currentGroup` | `0` |
| `currentScene` | `0xFF` |
| `sceneValid` | `false` |

따라서 제공된 코드에서는 장면을 재현한 뒤에도 `sceneValid`를 `true`로 설정하지 않는다.

### 명령 처리

`InvokeCommand`는 요청을 디코딩한 뒤 해당 `Handle...` 함수로 전달한다. `RecallScene`은 직접 상태를 반환하며, 나머지 지원 명령은 응답 구조체를 `AddResponse`로 전달한다.

`AcceptedCommands`와 `GeneratedCommands`는 `mSupportCopyScenes`가 설정되었을 때 각각 `CopyScene`, `CopySceneResponse`를 추가한다.

| 처리 함수 | 주요 동작 |
|---|---|
| `HandleAddScene` | 전환 시간, 이름 길이, 장면 ID를 검사한다. `SceneNames` 지원 시 이름을 저장하고, `SerializeAdd`로 EFS를 구성한다. 잔여 용량 확인 후 장면을 저장하고 `FabricSceneInfo`를 갱신한다. |
| `HandleViewScene` | 저장 장면을 조회하고 지원 handler의 `Deserialize`로 EFS를 응답 형식으로 변환한다. 성공 시 전환 시간, 이름, EFS를 반환한다. |
| `HandleRemoveScene` | 장면 존재 확인 후 제거하고 `FabricSceneInfo`를 갱신한다. |
| `HandleRemoveAllScenes` | `DeleteAllScenesInGroup`으로 그룹의 장면을 제거하고 `FabricSceneInfo`를 갱신한다. |
| `HandleStoreScene` | 장면 ID 검사 후 `StoreSceneParse`를 호출한다. |
| `HandleRecallScene` | 장면 ID 검사 후 `RecallSceneParse`를 호출하고 상태를 반환한다. |
| `HandleGetSceneMembership` | 잔여 용량과 그룹의 장면 ID 목록을 반환한다. |
| `HandleCopyScene` | 출발지·목적지 장면 ID와 그룹 소속을 검사한 뒤 단일 장면 또는 그룹의 장면들을 복사한다. |

`GroupID`가 `0`이 아닌 경우 관련 명령은 `GroupDataProvider::HasEndpoint`로 Endpoint의 그룹 소속을 확인한다. `CopyScene`은 출발지와 목적지 그룹을 모두 검사한다.

#### 저장 및 재현

`StoreSceneParse`:

1. 기존 장면을 조회한다.
2. 새 장면이면 이름을 비우고 전환 시간을 `0`으로 설정한다.
3. 기존 장면이면 EFS를 비우고, `SceneNames` 미지원 시 이름도 비운다.
4. `SceneSaveEFS`로 현재 클러스터 상태를 수집한다.
5. `SetSceneTableEntry`로 저장하고 `UpdateFabricSceneInfo`를 호출한다.

`RecallSceneParse`:

1. 저장된 장면을 조회한다.
2. `transitionTime`이 제공되었고 null이 아니면, 읽어 온 장면 데이터의 전환 시간을 덮어쓴다.
3. `SceneApplyEFS`로 장면을 적용한다.
4. `UpdateFabricSceneInfo`를 호출한다.

이 경로는 덮어쓴 전환 시간을 다시 저장하지 않는다.

#### 복사

`HandleCopyScene`은 목적지 장면이 이미 있으면 신규 슬롯에 대한 사전 용량 검사를 생략한다. 목적지가 없고 잔여 용량이 `0`이면 `Status::ResourceExhausted`를 반환한다.

- `CopyModeBitmap::kCopyAllScenes` 설정 시 출발지 그룹의 장면 ID를 유지하여 목적지 그룹에 복사한다.
- 전체 복사에서는 각 저장 후 `UpdateFabricSceneInfo`를 호출한다.
- 단일 복사에서는 목적지의 `GroupIdentifierTo`, `SceneIdentifierTo`를 사용한다.

#### 오류 변환

`ResponseStatus`는 다음 변환을 수행한다.

| 오류 | 응답 상태 |
|---|---|
| `CHIP_ERROR_NOT_FOUND` | `Status::NotFound` |
| `CHIP_ERROR_NO_MEMORY` | `Status::ResourceExhausted` |
| `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)` | `Status::InvalidCommand` |
| 그 외 | `StatusIB(err).mStatus` |

`HandleRecallScene`은 별도로 `CHIP_NO_ERROR`, `CHIP_ERROR_NOT_FOUND`를 처리하고, 나머지는 `StatusIB(err).mStatus`로 변환한다.

### 장면 테이블과 영속 저장

출처:

- `src/app/clusters/scenes-server/SceneTable.h`
- `src/app/clusters/scenes-server/SceneTableImpl.h`
- `src/app/clusters/scenes-server/SceneTableImpl.cpp`

#### 데이터 모델

`SceneTable<EFStype>`는 다음 데이터를 정의한다.

| 구성 요소 | 내용 |
|---|---|
| `SceneStorageId` | `mGroupId`, `mSceneId` |
| `SceneData` | `mName`, `mNameLength`, `mSceneTransitionTimeMs`, `mExtensionFieldSets` |
| `SceneTableEntry` | `app::Storage::Data::TableEntry<SceneStorageId, SceneData>` |

Endpoint와 Fabric 범위는 테이블 및 저장 API에서 관리한다. `SceneStorageId::IsValid()`는 `mSceneId`가 `kUndefinedSceneId`가 아닌지 확인한다.

`SceneData::SetName`은 입력 이름을 `kSceneNameMaxLength`까지 복사한다. 빈 이름은 영속 저장 시 생략된다.

#### 인터페이스

| 분류 | 함수 |
|---|---|
| 초기화 | `Init`, `Finish` |
| 크기 및 개수 | `GetTableSize`, `GetEndpointSceneCount`, `GetFabricSceneCount`, `GetRemainingCapacity` |
| 항목 관리 | `SetSceneTableEntry`, `GetSceneTableEntry`, `RemoveSceneTableEntry`, `RemoveSceneTableEntryAtPosition` |
| 그룹 관리 | `GetAllSceneIdsInGroup`, `DeleteAllScenesInGroup` |
| handler 관리 | `RegisterHandler`, `UnregisterHandler`, `UnregisterAllHandlers`, `HandlerListEmpty` |
| EFS 처리 | `SceneSaveEFS`, `SceneApplyEFS` |
| 범위 삭제 | `RemoveFabric`, `RemoveEndpoint` |

`DefaultSceneTableImpl`은 `PersistentStorageDelegate`와 `app::Storage::FabricTableImpl`을 사용한다.

저장 키는 다음 함수에 연결된다.

- `DefaultStorageKeyAllocator::EndpointSceneCountKey`
- `DefaultStorageKeyAllocator::FabricSceneKey`
- `DefaultStorageKeyAllocator::FabricSceneDataKey`

직렬화는 `TagScene`의 `kGroupId`, `kSceneId`, `kName`, `kTransitionTimeMs`와 EFS 직렬화를 사용한다. `Serializer::kFabricMaxBytes()`는 `128`을 반환한다.

`RemoveFabric`은 Fabric 삭제 후 호출될 수 있으므로 실제 Fabric 테이블에 다시 접근하지 않아야 한다는 계약이 명시되어 있다.

#### EFS 저장·적용 흐름

- `SceneSaveEFS`
  - 데이터 모델의 `ServerClusters`를 조회한다.
  - 각 클러스터에 대해 `SupportsCluster`가 참인 첫 handler의 `SerializeSave`를 호출한다.
  - 결과를 장면의 EFS에 삽입한다.
- `SceneApplyEFS`
  - 저장된 EFS를 순회한다.
  - 각 비어 있지 않은 EFS에 대해 첫 지원 handler의 `ApplyScene`을 호출한다.
  - 전환 시간으로 `mSceneTransitionTimeMs`를 전달한다.

`SceneHandler`의 계약은 일반적으로 각 `<endpoint, cluster>`에 하나의 handler만 대응하도록 요구한다. 여러 handler가 같은 쌍을 지원할 경우 어느 handler가 선택되는지에 의존해서는 안 된다.

### EFS 표현과 직렬화

출처:

- `src/app/clusters/scenes-server/ExtensionFieldSets.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp`

`ExtensionFieldSets`는 `Serialize`, `Deserialize`, `Clear`, `IsEmpty`, `GetFieldSetCount`를 제공하는 추상 인터페이스이다.

`ExtensionFieldSet`은 다음 멤버를 가진다.

| 멤버 | 내용 |
|---|---|
| `mID` | 클러스터 ID, 초기값 `kInvalidClusterId` |
| `mBytesBuffer` | 크기 `kMaxFieldBytesPerCluster`의 직렬화 버퍼 |
| `mUsedBytes` | 실제 사용 바이트 수 |

- `IsEmpty()`는 `mUsedBytes == 0`을 검사한다.
- 생성자에서 입력 데이터가 버퍼보다 크면 `mUsedBytes`를 `0`으로 설정한다.
- `Deserialize`에서 데이터가 버퍼보다 크면 `CHIP_ERROR_BUFFER_TOO_SMALL`을 반환한다.
- `Clear`는 ID, 버퍼, 사용량을 초기화한다.

TLV 태그는 `TagEFS`로 정의된다.

- `kFieldSetArrayContainer = 1`
- `kClusterID`
- `kClusterFieldSetData`

`ExtensionFieldSetsImpl`의 주요 동작:

| 함수 | 동작 |
|---|---|
| `InsertFieldSet` | 유효하지 않은 ID 또는 빈 데이터를 거부한다. 같은 ID는 덮어쓰고, 새 ID는 첫 빈 위치에 저장한다. 공간 부족 시 `CHIP_ERROR_NO_MEMORY`. |
| `GetFieldSetAtPosition` | 범위를 벗어나면 `CHIP_ERROR_INVALID_ARGUMENT`. |
| `RemoveFieldAtPosition` | 유효한 위치를 제거하고 배열을 압축한다. 범위를 벗어나면 변경 없이 `CHIP_NO_ERROR`. |
| `Serialize` | 사용 중인 EFS를 TLV 배열로 저장한다. |
| `Deserialize` | 최대 `kMaxClustersPerScene`까지 읽고, 전체를 읽지 못하면 오류를 반환한다. |

OTA로 `kMaxClustersPerScene`이 줄어 저장된 EFS 전체를 읽을 수 없는 경우, 구현은 잘라서 수용하지 않고 `CHIP_ERROR_BUFFER_TOO_SMALL`을 반환한다. 주석은 이 경우 해당 장면을 삭제해야 한다고 설명한다.

### 속성 값 검증

출처:

- `src/app/clusters/scenes-server/AttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp`

`AttributeValuePairValidator`는 다음 인터페이스를 제공한다.

```cpp
virtual CHIP_ERROR Validate(const app::ConcreteClusterPath & clusterPath, AttributeValuePairType & value) = 0;
```

`AttributeValuePairType`은 `app::Clusters::ScenesManagement::Structs::AttributeValuePairStruct::Type`의 별칭이다. 검증기는 속성 유효성을 검사하고 값 범위를 조정할 수 있다.

`CodegenAttributeValuePairValidator::Validate`의 순서:

1. `emberAfLocateAttributeMetadata`로 속성 메타데이터를 조회한다.
2. 속성이 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
3. `IsExactlyOneValuePopulated`로 값 필드가 정확히 하나인지 확인한다.
4. `app::Compatibility::Internal::AttributeBaseType`에 맞는 값 필드인지 확인한다.
5. `CapAttributeValue`로 값을 조정한다.

값 개수 또는 값 필드 타입이 맞지 않으면 `CHIP_ERROR_INVALID_ARGUMENT`을 반환한다.

| 속성 타입 | 사용되는 구현 필드 |
|---|---|
| `ZCL_BOOLEAN_ATTRIBUTE_TYPE`, `ZCL_INT8U_ATTRIBUTE_TYPE` | `valueUnsigned8` |
| `ZCL_INT16U_ATTRIBUTE_TYPE` | `valueUnsigned16` |
| `ZCL_INT24U_ATTRIBUTE_TYPE`, `ZCL_INT32U_ATTRIBUTE_TYPE` | `valueUnsigned32` |
| `ZCL_INT40U_ATTRIBUTE_TYPE`, `ZCL_INT48U_ATTRIBUTE_TYPE`, `ZCL_INT56U_ATTRIBUTE_TYPE`, `ZCL_INT64U_ATTRIBUTE_TYPE` | `valueUnsigned64` |
| `ZCL_INT8S_ATTRIBUTE_TYPE` | `valueSigned8` |
| `ZCL_INT16S_ATTRIBUTE_TYPE` | `valueSigned16` |
| `ZCL_INT24S_ATTRIBUTE_TYPE`, `ZCL_INT32S_ATTRIBUTE_TYPE` | `valueSigned32` |
| `ZCL_INT40S_ATTRIBUTE_TYPE`, `ZCL_INT48S_ATTRIBUTE_TYPE`, `ZCL_INT56S_ATTRIBUTE_TYPE`, `ZCL_INT64S_ATTRIBUTE_TYPE` | `valueSigned64` |

그 외 타입은 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.

`CapAttributeValue`는 메타데이터의 최소·최대값이 있으면 이를 사용하고, 없으면 타입의 범위를 사용한다.

- nullable 속성의 범위 밖 값: `SetNull`로 설정한다.
- nullable이 아닌 속성의 범위 밖 값: 최소값 또는 최대값으로 제한한다.
- boolean은 `uint8_t`로 표현하되 범위 계산에는 `bool`을 사용한다.
- 비표준 바이트 폭의 정수에는 `OddSizedInteger`를 사용한다.

`ConvertDefaultValueToWorkingValue`는 작은 기본값을 직접 변환하고, 더 큰 값은 저장 표현을 복사한 뒤 `StorageToWorking`으로 변환한다.

### 기본 handler와 전환 보조 구조

출처:

- `src/app/clusters/scenes-server/SceneHandlerImpl.h`
- `src/app/clusters/scenes-server/SceneHandlerImpl.cpp`
- `src/app/clusters/scenes-server/CodegenEndpointToIndex.h`

`SceneHandler`는 다음 동작을 추상화한다.

| 함수 | 용도 |
|---|---|
| `SupportsCluster` | Endpoint와 클러스터 지원 여부 |
| `SerializeAdd` | `AddScene`에서 받은 EFS 직렬화 |
| `SerializeSave` | `StoreScene`을 위한 현재 상태 직렬화 |
| `Deserialize` | 저장된 EFS를 명령 응답 구조체로 복원 |
| `ApplyScene` | 저장된 상태를 지정된 밀리초 전환 시간으로 적용 |

`DefaultSceneHandlerImpl`은 `SerializeAdd`, `Deserialize`와 속성 목록 인코딩·디코딩을 제공한다. `SerializeSave`, `ApplyScene`은 제공하지 않으므로 `SerializeAdd` 출력과 호환되게 구현해야 한다. `SupportsCluster`도 구현해야 한다.

- `SerializeAdd`: 목록 크기를 검사하고, 각 항목을 `mValidator.Validate`로 검증한 뒤 인코딩한다.
- `EncodeAttributeValueList`: 익명 태그로 인코딩하고 출력 버퍼의 크기를 실제 데이터 길이로 줄인다.
- `DecodeAttributeValueList`: 익명 TLV 배열을 디코딩한다. 결과는 원본 버퍼가 유지되고 변경되지 않는 동안만 유효하다.
- `Deserialize`: 목록을 `mAVPairs`에 복사하고 `extensionFieldSet.clusterID`, `extensionFieldSet.attributeValueList`를 설정한다.

전환 및 상태 관리용 보조 구조:

- `EndpointStatePair`: Endpoint와 값을 묶는다.
- `StatePairBuffer`: `FindPair`, `InsertPair`, `GetPair`, `RemovePair`를 제공한다. `ValueType`은 trivial이어야 하며 `MaxEndpointCount`는 `65535`보다 작아야 한다.
- `TransitionTimeInterface`: `Finder::EndpointIdToIndex`로 Endpoint별 이벤트 제어 객체를 찾고 `sceneEventControl`에서 Endpoint와 콜백을 설정한다.
- `CodegenEndpointToIndex`: `emberAfGetClusterServerEndpointIndex`를 사용하며 결과가 `MaxIndexCount` 이상이면 `false`를 반환한다. `EventControlType`은 `EmberEventControl`이다.

### 코드 생성 통합

출처:

- `src/app/clusters/scenes-server/CodegenIntegration.h`
- `src/app/clusters/scenes-server/CodegenIntegration.cpp`
- `src/app/clusters/scenes-server/scenes-server.h`

`IntegrationDelegate::CreateRegistration`은 다음 작업을 수행한다.

1. `Attributes::SceneTableSize::GetDefault`로 Endpoint별 테이블 크기를 읽는다.
2. `emberAfFindServerCluster`로 클러스터 메타데이터를 찾는다.
3. `acceptedCommandList`에서 `ScenesManagement::Commands::CopyScene::Id`를 찾아 지원 여부를 결정한다.
4. `DefaultScenesManagementTableProvider`에 Endpoint와 테이블 크기를 설정한다.
5. 의존성을 구성하여 `ScenesManagementCluster`를 생성한다.

클러스터 인스턴스 최대 개수는 고정 구성 개수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합이다.

| 함수 | 역할 |
|---|---|
| `MatterScenesManagementClusterInitCallback` | 서버 등록, `fetchFeatureMap=true`, `fetchOptionalAttributes=false` |
| `MatterScenesManagementClusterShutdownCallback` | 서버 등록 해제 |
| `MatterScenesManagementPluginServerInitCallback` | 빈 구현 |
| `FindClusterOnEndpoint` | 해당 Endpoint의 인스턴스 반환. 없거나 초기화 전이면 `nullptr` |

`ScenesServer::Instance()`는 호환용 접근 객체를 제공한다.

- handler 관련: `IsHandlerRegistered`, `RegisterSceneHandler`, `UnregisterSceneHandler`
- 클러스터 전달 함수: `GroupWillBeRemoved`, `StoreCurrentScene`, `RecallScene`, `RemoveFabric`

`ScenesServer`의 전달 함수는 클러스터를 찾지 못하면 반환하고, 호출 오류는 `LogErrorOnFailure`로 기록한다.

`scenes-server.h`는 하위 호환 전용이다. 주석은 새 코드에서 `ScenesManagementCluster.h`를 직접 사용하도록 안내한다.

### 다른 클러스터와의 통합

출처:

- `src/app/clusters/scenes-server/ScenesIntegrationDelegate.h`
- `src/app/clusters/scenes-server/Constants.h`

`ScenesIntegrationDelegate`는 `OnOff`, `LevelControl`, `ColorControl` 등의 클러스터가 장면 기능과 연동하기 위한 인터페이스이다.

| 함수 | 역할 |
|---|---|
| `StoreCurrentGlobalScene` | 해당 Fabric의 전역 장면에 현재 상태 저장 |
| `RecallGlobalScene` | 해당 Fabric의 전역 장면 재현 |
| `GroupWillBeRemoved` | 그룹 삭제 예정 알림 |

전역 장면 상수는 다음과 같다.

```cpp
static constexpr SceneId kGlobalSceneId      = 0;
static constexpr GroupId kGlobalSceneGroupId = 0;
```

`ScenesManagementCluster`는 전역 장면 함수를 `StoreCurrentScene` 및 `RecallScene`으로 연결한다. `GroupWillBeRemoved`는 해당 그룹의 장면을 `DeleteAllScenesInGroup`으로 삭제한다.

### 용량과 구성 상수

| 상수 | 값 또는 구성 매크로 |
|---|---|
| `kMaxScenesPerEndpoint` | `CHIP_CONFIG_MAX_SCENES_TABLE_SIZE` |
| `kMaxScenesPerFabric` | `(kMaxScenesPerEndpoint - 1) / 2` |
| `kSceneNameMaxLength` | `CHIP_CONFIG_SCENES_CLUSTER_MAXIMUM_NAME_LENGTH` |
| `kScenesMaxTransitionTime` | `60'000'000u` |
| `kMaxClustersPerScene` | `CHIP_CONFIG_SCENES_MAX_CLUSTERS_PER_SCENE` |
| `kMaxFieldBytesPerCluster` | `CHIP_CONFIG_SCENES_MAX_EXTENSION_FIELDSET_SIZE_PER_CLUSTER` |
| `kMaxAvPair` | `CHIP_CONFIG_SCENES_MAX_AV_PAIRS_EFS` |
| `kScenesServerMaxFabricCount` | `CHIP_CONFIG_MAX_FABRICS` |
| `Serializer::kEntryMaxBytes()` | `CHIP_CONFIG_SCENES_MAX_SERIALIZED_SCENE_SIZE_BYTES` |
| `kGlobalGroupSceneId` | `0x0000` |
| `kUndefinedSceneId` | `0xff` |
| `kInvalidPosition` | `0xff` |

- `kMaxScenesPerEndpoint >= 16`이 정적 검증된다.
- `SCENES_MANAGEMENT_TABLE_SIZE`가 정의되어 있고 0이 아니면 `kMaxScenesPerEndpoint >= SCENES_MANAGEMENT_TABLE_SIZE`가 정적 검증된다.
- 코드 주석은 ZAP의 `SCENES_MANAGEMENT_TABLE_SIZE`만 바꾸는 것으로 충분하지 않으며 `CHIP_CONFIG`도 갱신해야 한다고 명시한다.
- `SetTableSize`는 Endpoint 크기와 `(endpointSceneTableSize - 1) / 2`를 `FabricTableImpl::SetTableSize`에 전달한다.

### 공유 객체 및 메모리 수명 주의사항

- `GetSceneTableImpl`은 하나의 정적 `DefaultSceneTableImpl`을 재사용하며 호출마다 Endpoint와 테이블 크기를 설정한다.
- 해당 API의 주석은 반환 포인터를 캐시하지 말고 사용 전에 다시 호출하도록 명시한다.
- 동일 주석은 현재 thread-safe하지 않으며, 여러 Endpoint를 동시에 사용하는 경우 호출을 thread-safe하게 해야 한다고 설명한다.
- `Startup`의 주석도 저장 delegate와 데이터 모델 provider가 공유 전역 객체에 다시 설정되므로 여러 스택의 병렬 실행에 적합하지 않다고 설명한다.
- `HandleViewScene`의 응답은 `scene`과 `responseEFSBuffer`가 소유하는 메모리를 참조한다.
- `HandleGetSceneMembership`의 응답 목록은 전달받은 `scenesInGroup` 버퍼를 참조한다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
