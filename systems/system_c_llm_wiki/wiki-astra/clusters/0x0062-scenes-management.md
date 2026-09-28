---
entity: Scenes Management
ids: ['0x0062']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/scene.xml', 'src/app/clusters/scenes-server/SceneHandlerImpl.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h', 'src/app/clusters/scenes-server/SceneTableImpl.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp', 'src/app/clusters/scenes-server/SceneHandlerImpl.cpp', 'src/app/clusters/scenes-server/scenes-server.h', 'src/app/clusters/scenes-server/ExtensionFieldSets.h', 'src/app/clusters/scenes-server/CodegenIntegration.h', 'src/app/clusters/scenes-server/CodegenIntegration.cpp', 'src/app/clusters/scenes-server/Constants.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h', 'src/app/clusters/scenes-server/CodegenEndpointToIndex.h', 'src/app/clusters/scenes-server/SceneTable.h', 'src/app/clusters/scenes-server/AttributeValuePairValidator.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.h', 'src/app/clusters/scenes-server/SceneTableImpl.cpp', 'src/app/clusters/scenes-server/ScenesIntegrationDelegate.h', 'data_model/1.7/clusters/Scenes.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Scenes Management

## 개요

Scenes Management는 장면 구성과 조작을 위한 속성 및 명령을 제공한다. 구현은 클러스터별 속성 데이터를 Extension Field Set으로 저장하고, 저장된 장면을 조회하거나 적용한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0062` |
| 스펙 이름 | `Scenes Management Cluster` |
| 리비전 | `2` |
| 분류 | `hierarchy="base"`, `role="application"` |
| 범위 | `Endpoint` |
| PICS 코드 | `S` |
| 선택 기능 | `SceneNames` (`SN`) |
| 선택 명령 | `CopyScene` |

장면 저장소는 endpoint 및 fabric을 구분하며, 장면 데이터에는 이름, 전환 시간, 클러스터별 Extension Field Set이 포함된다. `OnOff`, `LevelControl`, `ColorControl` 등의 클러스터는 `ScenesIntegrationDelegate`를 통해 전역 장면 저장·호출 및 그룹 제거 알림과 연동할 수 있다.

## 스펙

출처: `data_model/1.7/clusters/Scenes.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | ZCL Scenes Cluster를 기반으로 클러스터 ID를 `0x0062`, 이름을 `Scenes Management`로 변경하고 provisional 상태를 제거했다. 속성 `SceneCount`, `CurrentScene`, `CurrentGroup`, `SceneValid`, `NameSupport`와 기능 `Explicit`, `TableSize`, `FabricScenes`를 제거했다. `EnhancedAddScene`, `EnhancedAddSceneResponse`, `EnhancedViewScene`, `EnhancedViewSceneResponse`를 제거했다. `AddScene`, `ViewSceneResponse`, `RecallScene`의 `TransitionTime` 단위를 밀리초로 변경했다. |
| `2` | `SceneInfoStruct`의 `CurrentScene`, `CurrentGroup`, `SceneValid` 필드를 deprecated로 지정했다. |

### 기능

| 비트 | 코드 | 이름 | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `SN` | `SceneNames` | 선택 | 장면 이름 저장 |

### 데이터 타입

#### `CopyModeBitmap`

| 비트 | 필드 | 적합성 | 설명 |
|---|---|---|---|
| `0` | `CopyAllScenes` | 필수 | 장면 테이블의 모든 장면 복사 |

#### `AttributeValuePairStruct`

| 필드 ID | 이름 | 스펙 타입 | 적합성 |
|---|---|---|---|
| `0` | `AttributeID` | `attribute-id` | 필수 |
| `1` | `ValueUnsigned8` | `uint8` | 선택, `choice="a"` |
| `2` | `ValueSigned8` | `int8` | 선택, `choice="a"` |
| `3` | `ValueUnsigned16` | `uint16` | 선택, `choice="a"` |
| `4` | `ValueSigned16` | `int16` | 선택, `choice="a"` |
| `5` | `ValueUnsigned32` | `uint32` | 선택, `choice="a"` |
| `6` | `ValueSigned32` | `int32` | 선택, `choice="a"` |
| `7` | `ValueUnsigned64` | `uint64` | 선택, `choice="a"` |
| `8` | `ValueSigned64` | `int64` | 선택, `choice="a"` |

#### `ExtensionFieldSetStruct`

| 필드 ID | 이름 | 스펙 타입 | 적합성 |
|---|---|---|---|
| `0` | `ClusterID` | `cluster-id` | 필수 |
| `1` | `AttributeValueList` | `list`, 항목 `AttributeValuePairStruct` | 필수 |

#### `SceneInfoStruct`

구조체 전체는 fabric 범위이다.

| 필드 ID | 이름 | 스펙 타입 | 기본값 | 조건 |
|---|---|---|---|---|
| `0` | `SceneCount` | `uint8` | — | 필수 |
| `1` | `CurrentScene` | `uint8` | `0xFF` | fabric-sensitive, 리비전 `2`에서 deprecated |
| `2` | `CurrentGroup` | `group-id` | `0` | fabric-sensitive, 리비전 `2`에서 deprecated |
| `3` | `SceneValid` | `bool` | `false` | fabric-sensitive, 리비전 `2`에서 deprecated |
| `4` | `RemainingCapacity` | `uint8` | — | 필수, 최댓값 `253` |

`CurrentScene`, `CurrentGroup`, `SceneValid`에는 XML의 `otherwiseConform` 안에 `mandatoryConform`과 `deprecateConform`이 함께 기술되어 있다.

### 속성

| ID | 이름 | 스펙 타입 | 접근 | 적합성 및 품질 |
|---|---|---|---|---|
| `0x0000` | `DoNotUse` | 미지정 | 읽기, `view` | `disallowConform` |
| `0x0001` | `SceneTableSize` | `uint16` | 읽기, `view` | 필수, `persistence="fixed"` |
| `0x0002` | `FabricSceneInfo` | `list`, 항목 `SceneInfoStruct` | 읽기, `view` | 필수, fabric 범위 |

### 요청 명령

모든 요청 명령은 `commandToServer` 방향이며 fabric 범위이다. 필드 목록의 숫자는 필드 ID이다.

| ID | 이름 | 권한 | 적합성 | 필드 | 응답 |
|---|---|---|---|---|---|
| `0x00` | `AddScene` | `manage` | 필수 | `0: GroupID`, `1: SceneID`, `2: TransitionTime`, `3: SceneName`, `4: ExtensionFieldSetStructs` | `AddSceneResponse` |
| `0x01` | `ViewScene` | `operate` | 필수 | `0: GroupID`, `1: SceneID` | `ViewSceneResponse` |
| `0x02` | `RemoveScene` | `manage` | 필수 | `0: GroupID`, `1: SceneID` | `RemoveSceneResponse` |
| `0x03` | `RemoveAllScenes` | `manage` | 필수 | `0: GroupID` | `RemoveAllScenesResponse` |
| `0x04` | `StoreScene` | `manage` | 필수 | `0: GroupID`, `1: SceneID` | `StoreSceneResponse` |
| `0x05` | `RecallScene` | `operate` | 필수 | `0: GroupID`, `1: SceneID`, `2: TransitionTime` | XML에 `response="Y"` |
| `0x06` | `GetSceneMembership` | `operate` | 필수 | `0: GroupID` | `GetSceneMembershipResponse` |
| `0x40` | `CopyScene` | `manage` | 선택 | `0: Mode`, `1: GroupIdentifierFrom`, `2: SceneIdentifierFrom`, `3: GroupIdentifierTo`, `4: SceneIdentifierTo` | `CopySceneResponse` |

요청 필드의 타입과 제약은 다음과 같다.

| 필드 | 스펙 타입 | 제약 |
|---|---|---|
| `GroupID`, `GroupIdentifierFrom`, `GroupIdentifierTo` | `group-id` | 필수 |
| `SceneID`, `SceneIdentifierFrom`, `SceneIdentifierTo` | `uint8` | 필수, 최댓값 `254` |
| `TransitionTime` | `uint32` | 최댓값 `60000000`, 밀리초 |
| `SceneName` | `string` | 필수, 최대 길이 `16` |
| `ExtensionFieldSetStructs` | `list`, 항목 `ExtensionFieldSetStruct` | 필수 |
| `Mode` | `CopyModeBitmap` | 필수 |

`AddScene`의 `TransitionTime`은 필수이다. `RecallScene`의 `TransitionTime`은 선택이며 nullable이다.

### 응답 명령

모든 응답 명령의 방향은 `responseFromServer`이다.

| ID | 이름 | 필드 |
|---|---|---|
| `0x00` | `AddSceneResponse` | `0: Status`, `1: GroupID`, `2: SceneID` |
| `0x01` | `ViewSceneResponse` | `0: Status`, `1: GroupID`, `2: SceneID`, `3: TransitionTime`, `4: SceneName`, `5: ExtensionFieldSetStructs` |
| `0x02` | `RemoveSceneResponse` | `0: Status`, `1: GroupID`, `2: SceneID` |
| `0x03` | `RemoveAllScenesResponse` | `0: Status`, `1: GroupID` |
| `0x04` | `StoreSceneResponse` | `0: Status`, `1: GroupID`, `2: SceneID` |
| `0x06` | `GetSceneMembershipResponse` | `0: Status`, `1: Capacity`, `2: GroupID`, `3: SceneList` |
| `0x40` | `CopySceneResponse` | `0: Status`, `1: GroupIdentifierFrom`, `2: SceneIdentifierFrom` |

- `Status`의 타입은 `status`이다.
- 그룹 및 장면 식별자의 타입과 최댓값은 요청 필드와 같다.
- `ViewSceneResponse`의 `TransitionTime`, `SceneName`, `ExtensionFieldSetStructs`는 `Status`가 `SUCCESS`일 때 필수이다.
  - `TransitionTime`: `uint32`, 최댓값 `60000000`.
  - `SceneName`: `string`, 최대 길이 `16`.
  - `ExtensionFieldSetStructs`: `ExtensionFieldSetStruct` 목록.
- `GetSceneMembershipResponse`의 `Capacity`는 필수 nullable `uint8`이다.
- `GetSceneMembershipResponse`의 `SceneList`는 `uint8` 목록이며, `Status`가 `SUCCESS`일 때 필수이다.
- `CopySceneResponse`는 `CopyScene`을 지원할 때 필수이다. 나머지 응답 명령은 필수이다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/scene.xml`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| 이름 | `Scenes Management` |
| 도메인 | `General` |
| 코드 | `0x0062` |
| define | `SCENES_CLUSTER` |
| client | 활성, `tick="false"`, `init="false"` |
| server | 활성, `tick="false"`, `init="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="2"`, `side="either"` |

이 XML은 Alchemy가 생성한 파일이며 직접 수정하지 않도록 표시되어 있다.

- 원본: `src/app_clusters/Scenes.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

### 타입 및 속성 매핑

SDK는 스펙의 필드 이름과 ID를 유지하면서 다음 타입 표기를 사용한다.

| 스펙 타입 | SDK 타입 |
|---|---|
| `attribute-id` | `attrib_id` |
| `cluster-id` | `cluster_id` |
| `group-id` | `group_id` |
| `uint8`, `int8` | `int8u`, `int8s` |
| `uint16`, `int16` | `int16u`, `int16s` |
| `uint32`, `int32` | `int32u`, `int32s` |
| `uint64`, `int64` | `int64u`, `int64s` |
| `bool` | `boolean` |
| `string` | `char_string` |

- `CopyModeBitmap`은 `bitmap8`이며 `CopyAllScenes`의 mask는 `0x01`이다.
- `SceneInfoStruct`에는 `isFabricScoped="true"`가 지정되어 있다.
- `CurrentScene`, `CurrentGroup`, `SceneValid`는 SDK에서도 유지되며 `isFabricSensitive="true"`가 지정되어 있다.
- `AttributeValuePairStruct`의 값 필드들은 `optional="true"`와 `choice="a"`를 사용한다.
- `ExtensionFieldSetStruct.AttributeValueList`는 `AttributeValuePairStruct` 배열이다.

| ID | 이름 | define | SDK 타입 |
|---|---|---|---|
| `0x0001` | `SceneTableSize` | `SCENE_TABLE_SIZE` | `int16u` |
| `0x0002` | `FabricSceneInfo` | `FABRIC_SCENE_INFO` | `array`, `entryType="SceneInfoStruct"` |

### 명령 정의와 CLI 메타데이터

모든 요청 명령은 `source="client"`와 `isFabricScoped="true"`로 정의된다.

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

SDK 표현에서 주의할 차이는 다음과 같다.

- `ViewSceneResponse`의 `TransitionTime`, `SceneName`, `ExtensionFieldSetStructs`는 `optional="true"`로 표현된다.
- `GetSceneMembershipResponse.SceneList`도 `optional="true"`로 표현된다.
- `CopyScene.Mode`에는 `max="0x01"`이 지정되어 있다.
- `CopySceneResponse`에는 `optional="true"`와 함께 `CopyScene`에 대한 `mandatoryConform`이 지정되어 있다.
- 모든 서버 응답은 `source="server"`, `disableDefaultResponse="true"`로 정의된다.
- `RecallScene`에는 별도의 이름 있는 응답 명령이 지정되어 있지 않다.

## 구현

### 서버 클러스터와 의존성

출처:

- `src/app/clusters/scenes-server/ScenesManagementCluster.h`
- `src/app/clusters/scenes-server/ScenesManagementCluster.cpp`

`chip::app::Clusters::ScenesManagementCluster`는 다음 인터페이스를 구현한다.

- `DefaultServerCluster`
- `FabricTable::Delegate`
- `scenes::ScenesIntegrationDelegate`

`Context`를 통해 의존성을 주입받는다.

| 필드 | 용도 |
|---|---|
| `groupDataProvider` | 그룹과 endpoint의 관계 확인 |
| `fabricTable` | fabric 생명주기 연동 |
| `features` | `SceneNames` 등의 기능 비트 |
| `sceneTableProvider` | 장면 테이블 접근 |
| `supportsCopyScene` | `CopyScene` 지원 여부 |

`ScenesManagementTableProvider`는 `Take()`와 `Release()`를 제공한다. `ScopedSceneTable`은 생성 시 `Take()`, 소멸 시 `Release()`를 호출하며, `Take()`가 `nullptr`를 반환하면 `VerifyOrDie`로 실패한다.

### 속성 및 명령 노출

- `Attributes()`는 `kMandatoryMetadata`를 사용한다.
- `ReadAttribute()`는 `ClusterRevision`, `FeatureMap`, `SceneTableSize`, `FabricSceneInfo`를 처리한다.
- `SceneTableSize`는 `GetTableSize()` 결과를 인코딩한다.
- `FabricSceneInfo`를 읽을 때는 각 fabric의 `remainingCapacity`를 다시 조회한다.
- 알 수 없는 속성은 `Status::UnsupportedAttribute`를 반환한다.
- `AcceptedCommands()`와 `GeneratedCommands()`는 `mSupportCopyScenes`가 참일 때 각각 `CopyScene`, `CopySceneResponse`를 추가한다.
- `InvokeCommand()`는 요청을 디코딩하여 해당 `Handle...` 함수에 전달한다. 지원하지 않는 명령은 `Status::UnsupportedCommand`를 반환한다.
- `RecallScene`은 이름 있는 응답 대신 `HandleRecallScene()`의 상태를 반환한다.

### 명령 처리

| 처리 함수 | 주요 동작 |
|---|---|
| `HandleAddScene()` | 전환 시간, 이름 길이, 장면 ID를 검사한다. 그룹 관계를 확인한 뒤 지원하는 handler의 `SerializeAdd()`를 호출한다. 잔여 용량을 확인하고 저장한 후 `UpdateFabricSceneInfo()`를 호출한다. |
| `HandleViewScene()` | 저장된 장면을 조회하고 handler의 `Deserialize()`로 Extension Field Set을 응답 형식으로 변환한다. 성공 시 전환 시간, 이름, Extension Field Set 목록을 설정한다. |
| `HandleRemoveScene()` | 장면 존재 여부를 확인한 뒤 삭제하고 fabric 정보를 갱신한다. |
| `HandleRemoveAllScenes()` | 지정 그룹의 장면을 `DeleteAllScenesInGroup()`으로 삭제하고 fabric 정보를 갱신한다. |
| `HandleStoreScene()` | 장면 ID를 검사하고 `StoreSceneParse()`에 위임한다. |
| `HandleRecallScene()` | 장면 ID를 검사하고 `RecallSceneParse()`에 위임한다. |
| `HandleGetSceneMembership()` | 잔여 용량과 그룹 내 장면 ID 목록을 조회한다. 성공 시 `capacity`를 non-null로 설정하고 `sceneList`를 포함한다. |
| `HandleCopyScene()` | 출발·도착 장면 ID와 그룹 관계를 검사한다. 단일 장면 또는 그룹의 모든 장면을 복사한다. |

일반적인 그룹 검사에서는 그룹 ID가 `0`이 아닐 때 `HasEndpoint()`로 현재 endpoint가 해당 그룹에 속하는지 확인한다. 일치하지 않으면 `Status::InvalidCommand`에 해당하는 오류를 반환한다.

#### 저장과 호출

`StoreSceneParse()`:

1. 기존 장면을 조회한다.
2. 새 장면이면 이름을 비우고 전환 시간을 `0`으로 설정한다.
3. 기존 장면이면 Extension Field Set을 비운다. `SceneNames`를 지원하지 않으면 이름도 비운다.
4. `SceneSaveEFS()`로 현재 상태를 수집한다.
5. `SetSceneTableEntry()`로 저장하고 `UpdateFabricSceneInfo()`를 호출한다.

`RecallSceneParse()`:

1. 저장된 장면을 조회한다.
2. 요청의 `TransitionTime`이 존재하고 null이 아닌 경우, 적용에 사용할 전환 시간을 교체한다.
3. `SceneApplyEFS()`로 장면을 적용한다.
4. `UpdateFabricSceneInfo()`를 호출한다.

`TransitionTime`이 없거나 null이면 저장된 전환 시간을 사용한다.

#### 복사와 용량 처리

- `HandleCopyScene()`은 먼저 지정된 도착 장면의 존재 여부를 확인한다.
- 도착 장면이 없을 때만 사전 잔여 용량 검사를 수행한다. 기존 장면 덮어쓰기는 새 슬롯을 소비하지 않는다는 주석이 있다.
- `CopyAllScenes`가 설정되면 출발 그룹의 장면 ID 목록을 순회하며, 각 장면 ID를 유지한 채 도착 그룹에 저장한다.
- 전체 복사에서는 중간에 용량 제한에 도달할 수 있으므로 각 저장 후 `UpdateFabricSceneInfo()`를 호출한다.
- `HandleAddScene()`은 저장 전에 잔여 용량을 검사하며, `0`이면 `Status::ResourceExhausted`를 반환한다.

#### 오류 변환

`ResponseStatus()`의 명시적 변환은 다음과 같다.

| 오류 | 응답 상태 |
|---|---|
| `CHIP_ERROR_NOT_FOUND` | `Status::NotFound` |
| `CHIP_ERROR_NO_MEMORY` | `Status::ResourceExhausted` |
| `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)` | `Status::InvalidCommand` |
| 그 외 | `StatusIB(err).mStatus` |

`HandleRecallScene()`은 성공과 `CHIP_ERROR_NOT_FOUND`를 별도로 처리하고, 나머지는 `StatusIB(err).mStatus`로 변환한다.

### `FabricSceneInfo`와 생명주기

`FabricSceneInfo`는 최대 `CHIP_CONFIG_MAX_FABRICS`개의 `SceneInfoStruct`를 고정 배열로 보관한다.

`UpdateFabricSceneInfo()`는 다음을 수행한다.

- 유효한 fabric인지 검사한다.
- 해당 항목을 갱신하거나 새로 추가한다.
- `currentGroup = 0`, `currentScene = 0xFF`, `sceneValid = false`로 설정한다.
- `sceneCount`와 `remainingCapacity`를 조회한다.
- `NotifyAttributeChanged()`로 `FabricSceneInfo` 변경을 알린다.

따라서 제공된 구현에서는 장면 호출 뒤에도 이 함수가 deprecated 필드를 위 값으로 설정한다.

| 함수 | 동작 |
|---|---|
| `Startup()` | 저장소와 data model provider로 테이블을 초기화하고 fabric delegate를 등록한다. 기존 fabric 정보를 갱신한다. |
| `OnFabricCommitted()` | 해당 fabric의 `FabricSceneInfo`를 갱신한다. |
| `OnFabricRemoved()` | fabric의 저장된 장면과 메모리의 정보를 제거한다. |
| `ClearPersistentData()` | 시작된 상태에서만 호출할 수 있으며 `RemoveEndpoint()`로 영속 데이터를 제거한다. |
| `Shutdown()` | fabric delegate를 제거한다. `ClusterShutdownType::kPermanentRemove`이면 영속 데이터도 제거한다. |
| `GroupWillBeRemoved()` | 해당 그룹의 장면을 삭제한다. |
| `RemoveFabric()` | fabric의 장면과 `FabricSceneInfo` 항목을 제거한다. |

### 장면 테이블과 영속 저장

출처:

- `src/app/clusters/scenes-server/SceneTable.h`
- `src/app/clusters/scenes-server/SceneTableImpl.h`
- `src/app/clusters/scenes-server/SceneTableImpl.cpp`

`SceneTable<EFStype>`는 저장, 조회, 삭제, 용량 조회, 그룹별 작업, handler 관리 및 Extension Field Set 저장·적용 인터페이스를 제공한다.

#### 데이터 모델

| 타입 | 구성 |
|---|---|
| `SceneStorageId` | `mGroupId`, `mSceneId` |
| `SceneData` | `mName`, `mNameLength`, `mSceneTransitionTimeMs`, `mExtensionFieldSets` |
| `SceneTableEntry` | `app::Storage::Data::TableEntry<SceneStorageId, SceneData>` |
| `SceneIndex` | `app::Storage::Data::EntryIndex` |
| `TransitionTimeMs` | `uint32_t` |
| `SceneTransitionTime` | `uint32_t` |

`SceneStorageId::IsValid()`는 `mSceneId`가 `kUndefinedSceneId`가 아닌지 검사한다. `SceneData::SetName()`은 입력 길이를 `kSceneNameMaxLength` 이내로 제한하여 복사한다.

#### 상수와 크기 설정

| 식별자 | 값 또는 정의 |
|---|---|
| `kMaxScenesPerEndpoint` | `CHIP_CONFIG_MAX_SCENES_TABLE_SIZE` |
| `kMaxScenesPerFabric` | `(kMaxScenesPerEndpoint - 1) / 2` |
| `kGlobalGroupSceneId` | `0x0000` |
| `kUndefinedSceneId` | `0xff` |
| `kSceneNameMaxLength` | `CHIP_CONFIG_SCENES_CLUSTER_MAXIMUM_NAME_LENGTH` |
| `kScenesMaxTransitionTime` | `60'000'000u` |
| `Serializer::kEntryMaxBytes()` | `CHIP_CONFIG_SCENES_MAX_SERIALIZED_SCENE_SIZE_BYTES` |
| `Serializer::kFabricMaxBytes()` | `128` |

`kMaxScenesPerEndpoint >= 16`은 `static_assert`로 검사된다.

`DefaultSceneTableImpl`은 `SceneTableBase`와 `app::Storage::FabricTableImpl<SceneTableBase::SceneStorageId, SceneTableBase::SceneData>`를 상속하며, `PersistentStorageDelegate`를 사용한다.

저장 키는 다음 함수에 연결된다.

- `DefaultStorageKeyAllocator::EndpointSceneCountKey()`
- `DefaultStorageKeyAllocator::FabricSceneKey()`
- `DefaultStorageKeyAllocator::FabricSceneDataKey()`

직렬화는 다음 데이터를 기록한다.

- `TagScene::kGroupId`: `mGroupId`
- `TagScene::kSceneId`: `mSceneId`
- `TagScene::kName`: 비어 있지 않은 이름에만 기록
- `TagScene::kTransitionTimeMs`: 밀리초 전환 시간
- `mExtensionFieldSets.Serialize()`의 결과

#### 공유 인스턴스 주의사항

`GetSceneTableImpl()`은 전역 정적 `DefaultSceneTableImpl`을 재사용하며, 호출할 때마다 `SetEndpoint()`와 `SetTableSize()`를 수행한다.

- 원문 주석은 테이블 사용 전에 매번 호출하고 반환 포인터를 캐시하지 않도록 명시한다.
- 여러 endpoint에서 사용할 때 thread-safe하지 않으므로 호출을 동기화해야 한다.
- 저장 작업에는 `kInvalidEndpointId`가 아닌 endpoint가 필요하다.
- `Startup()` 주석은 저장소와 provider도 공유 전역 객체에 다시 설정되므로 여러 stack의 병렬 사용에 적합하지 않다고 설명한다.
- 제공된 코드에서 `SetTableSize()`는 `FabricTableImpl::SetTableSize()`에 위임한다. `GetTableSize()`는 `mCurrentTableSize`를 반환하며, 해당 멤버는 `kMaxScenesPerEndpoint`로 초기화되어 있다.

### `SceneHandler`와 기본 구현

출처:

- `src/app/clusters/scenes-server/SceneTable.h`
- `src/app/clusters/scenes-server/SceneHandlerImpl.h`
- `src/app/clusters/scenes-server/SceneHandlerImpl.cpp`

`SceneHandler`는 클러스터와 장면 테이블 사이의 인터페이스이다.

| 함수 | 용도 |
|---|---|
| `SupportsCluster()` | endpoint와 cluster 조합 지원 여부 |
| `SerializeAdd()` | `AddScene`의 Extension Field Set 직렬화 |
| `SerializeSave()` | `StoreScene`에서 현재 클러스터 상태 직렬화 |
| `Deserialize()` | 저장된 데이터를 `ExtensionFieldSetStruct`로 복원 |
| `ApplyScene()` | 저장된 상태를 `TransitionTimeMs` 동안 적용 |

각 endpoint와 cluster 조합에는 하나의 handler만 대응하도록 권장된다. 여러 handler가 같은 조합을 지원하면 하나만 호출되며, 인터페이스 주석은 어떤 handler가 선택될지 정의하지 않는다. 제공된 테이블 구현은 목록에서 처음 일치한 handler를 호출한다.

`DefaultSceneHandlerImpl`은 다음을 제공한다.

- `EncodeAttributeValueList()`: 익명 태그의 TLV로 인코딩하고 출력 `MutableByteSpan` 크기를 실제 길이로 줄인다.
- `DecodeAttributeValueList()`: 익명 태그의 TLV 배열을 디코딩한다.
- `SerializeAdd()`: 항목 수를 검사하고 각 항목에 `mValidator.Validate()`를 적용한 뒤 인코딩한다.
- `Deserialize()`: 디코딩된 항목을 `mAVPairs`에 복사하여 응답 구조체에 연결한다.

`kMaxAvPair`는 `CHIP_CONFIG_SCENES_MAX_AV_PAIRS_EFS`이다. 직렬화·역직렬화 과정에서 항목 수가 버퍼보다 많으면 `CHIP_ERROR_BUFFER_TOO_SMALL`을 반환한다.

`SupportsCluster()`, `SerializeSave()`, `ApplyScene()`은 사용하는 클러스터에 맞게 구현해야 한다. 특히 `SerializeSave()`와 `ApplyScene()`은 `SerializeAdd()`의 출력 형식과 호환되어야 한다.

메모리 수명에도 주의가 필요하다.

- `DecodeAttributeValueList()`의 결과는 입력 버퍼가 존재하고 변경되지 않는 동안만 유효하다.
- `Deserialize()`가 반환하는 목록은 handler의 `mAVPairs`를 참조한다.
- `HandleViewScene()`의 응답은 이름과 Extension Field Set 목록에 대해 호출자가 제공한 버퍼를 참조한다.

### 속성 값 검증

출처:

- `src/app/clusters/scenes-server/AttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h`
- `src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp`

`AttributeValuePairValidator::Validate()`는 속성의 유효성을 확인하고 필요하면 값을 조정한다.

`CodegenAttributeValuePairValidator::Validate()`의 처리 순서는 다음과 같다.

1. `emberAfLocateAttributeMetadata()`로 속성 메타데이터를 찾는다.
2. 메타데이터가 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
3. `IsExactlyOneValuePopulated()`로 값 필드가 정확히 하나 설정되었는지 검사한다.
4. 속성의 기본 타입에 맞는 값 필드인지 확인한다.
5. `CapAttributeValue()`로 범위를 조정한다.

| 속성 기본 타입 | 요구되는 값 멤버 |
|---|---|
| `ZCL_BOOLEAN_ATTRIBUTE_TYPE`, `ZCL_INT8U_ATTRIBUTE_TYPE` | `valueUnsigned8` |
| `ZCL_INT16U_ATTRIBUTE_TYPE` | `valueUnsigned16` |
| `ZCL_INT24U_ATTRIBUTE_TYPE`, `ZCL_INT32U_ATTRIBUTE_TYPE` | `valueUnsigned32` |
| `ZCL_INT40U_ATTRIBUTE_TYPE`, `ZCL_INT48U_ATTRIBUTE_TYPE`, `ZCL_INT56U_ATTRIBUTE_TYPE`, `ZCL_INT64U_ATTRIBUTE_TYPE` | `valueUnsigned64` |
| `ZCL_INT8S_ATTRIBUTE_TYPE` | `valueSigned8` |
| `ZCL_INT16S_ATTRIBUTE_TYPE` | `valueSigned16` |
| `ZCL_INT24S_ATTRIBUTE_TYPE`, `ZCL_INT32S_ATTRIBUTE_TYPE` | `valueSigned32` |
| `ZCL_INT40S_ATTRIBUTE_TYPE`, `ZCL_INT48S_ATTRIBUTE_TYPE`, `ZCL_INT56S_ATTRIBUTE_TYPE`, `ZCL_INT64S_ATTRIBUTE_TYPE` | `valueSigned64` |

- 값 필드가 없거나 여러 개이거나 타입이 맞지 않으면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
- 지원하지 않는 기본 타입은 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
- 24·40·48·56비트 정수 범위는 `OddSizedInteger`로 처리한다.
- 명시적 min/max가 있으면 해당 값을 사용하고, 없으면 타입과 nullable 여부에 따른 범위를 사용한다.
- nullable 속성의 범위 밖 값은 null로 설정한다.
- nullable이 아니면 최솟값 또는 최댓값으로 제한한다.
- boolean은 `uint8_t` 저장 표현을 사용하면서 boolean 범위를 적용한다.

### Extension Field Set 저장 형식

출처:

- `src/app/clusters/scenes-server/ExtensionFieldSets.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h`
- `src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp`

| 식별자 | 정의 |
|---|---|
| `kInvalidPosition` | `0xff` |
| `kMaxClustersPerScene` | `CHIP_CONFIG_SCENES_MAX_CLUSTERS_PER_SCENE` |
| `kMaxFieldBytesPerCluster` | `CHIP_CONFIG_SCENES_MAX_EXTENSION_FIELDSET_SIZE_PER_CLUSTER` |

`ExtensionFieldSet`은 다음 멤버를 갖는다.

- `mID`: 클러스터 ID, 초기값 `kInvalidClusterId`
- `mBytesBuffer`: 직렬화된 데이터
- `mUsedBytes`: 사용 중인 데이터 길이

`TagEFS`는 `kFieldSetArrayContainer`, `kClusterID`, `kClusterFieldSetData`를 정의한다. `ExtensionFieldSetsImpl`은 필드 집합들을 TLV 배열로 저장한다.

| 함수 | 동작 |
|---|---|
| `InsertFieldSet()` | 같은 `mID`가 있으면 덮어쓴다. 없으면 첫 빈 위치에 삽입한다. |
| `GetFieldSetAtPosition()` | 유효한 위치의 항목을 복사한다. |
| `RemoveFieldAtPosition()` | 항목 제거 후 배열을 압축한다. 범위 밖 위치는 성공으로 처리한다. |
| `Clear()` | 사용 중인 항목을 비우고 개수를 `0`으로 만든다. |
| `GetFieldSetCount()` | 초기화된 필드 집합 개수를 반환한다. |

주요 오류 처리:

- 잘못된 클러스터 ID 또는 빈 필드 집합 삽입: `CHIP_ERROR_INVALID_ARGUMENT`
- 삽입 공간 부족: `CHIP_ERROR_NO_MEMORY`
- 개별 데이터 또는 역직렬화할 집합 수가 버퍼 한도 초과: `CHIP_ERROR_BUFFER_TOO_SMALL`

OTA로 `kMaxClustersPerScene`이 줄어 저장된 집합을 모두 읽을 수 없는 경우, 데이터를 잘라 사용하지 않고 오류를 반환한다. 주석은 이런 장면을 삭제해야 한다고 설명한다.

### 전환 지원 도구

출처:

- `src/app/clusters/scenes-server/SceneHandlerImpl.h`
- `src/app/clusters/scenes-server/CodegenEndpointToIndex.h`

- `EndpointStatePair<ValueType>`은 `mEndpoint`와 `mValue`를 연결한다.
- `StatePairBuffer<ValueType, MaxEndpointCount>`는 `FindPair()`, `InsertPair()`, `GetPair()`, `RemovePair()`를 제공한다.
  - 기존 endpoint는 갱신한다.
  - 새 항목을 넣을 공간이 없으면 `CHIP_ERROR_NO_MEMORY`를 반환한다.
  - `ValueType`은 trivial이어야 하고 `MaxEndpointCount`는 `65535`보다 작아야 한다.
- `TransitionTimeInterface<Finder>`는 `Finder::kMaxEndpointCount` 크기의 event control 배열을 유지한다.
- `sceneEventControl()`은 endpoint에 해당하는 control의 `endpoint`와 `callback`을 설정한다.
- `CodegenEndpointToIndex`는 `emberAfGetClusterServerEndpointIndex()` 결과가 `MaxIndexCount`보다 작은지 확인하여 0 기반 인덱스를 제공한다.
- `CodegenEndpointToIndex::EventControlType`은 `EmberEventControl`이다.

### Codegen 및 클러스터 간 연동

출처:

- `src/app/clusters/scenes-server/CodegenIntegration.h`
- `src/app/clusters/scenes-server/CodegenIntegration.cpp`
- `src/app/clusters/scenes-server/ScenesIntegrationDelegate.h`
- `src/app/clusters/scenes-server/Constants.h`
- `src/app/clusters/scenes-server/scenes-server.h`

`IntegrationDelegate::CreateRegistration()`은 다음 정보를 사용해 `ScenesManagementCluster`를 생성한다.

- `Attributes::SceneTableSize::GetDefault()`의 endpoint별 테이블 크기
- `acceptedCommandList`의 `CopyScene` 포함 여부
- `Credentials::GetGroupDataProvider()`
- `Server::GetInstance().GetFabricTable()`
- `featureMap`

고정 인스턴스 수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 합산하여 최대 클러스터 인스턴스 수를 정한다.

| 함수 | 역할 |
|---|---|
| `MatterScenesManagementClusterInitCallback()` | `CodegenClusterIntegration::RegisterServer()` 호출 |
| `MatterScenesManagementClusterShutdownCallback()` | `CodegenClusterIntegration::UnregisterServer()` 호출 |
| `MatterScenesManagementPluginServerInitCallback()` | 빈 구현 |
| `FindClusterOnEndpoint()` | endpoint의 초기화된 클러스터 조회. 없거나 초기화되지 않았으면 `nullptr` |

`SCENES_MANAGEMENT_TABLE_SIZE`가 설정되면 `kMaxScenesPerEndpoint` 이하인지 컴파일 시 검사한다. 원문 주석은 ZAP의 `SCENES_MANAGEMENT_TABLE_SIZE`만 변경해서는 충분하지 않고 `CHIP_CONFIG`도 갱신해야 한다고 명시한다.

`ScenesServer`는 싱글턴 진입점으로 다음 기능을 제공한다.

- `GroupWillBeRemoved()`
- `StoreCurrentScene()`
- `RecallScene()`
- `IsHandlerRegistered()`
- `RegisterSceneHandler()`
- `UnregisterSceneHandler()`
- `RemoveFabric()`

`ScenesIntegrationDelegate`는 다른 클러스터에 다음 인터페이스를 제공한다.

| 함수 | 역할 |
|---|---|
| `StoreCurrentGlobalScene()` | 현재 상태를 전역 장면에 저장 |
| `RecallGlobalScene()` | 전역 장면 호출 |
| `GroupWillBeRemoved()` | 그룹 제거 전 알림 |

전역 장면 상수는 `kGlobalSceneId = 0`, `kGlobalSceneGroupId = 0`이다.

`src/app/clusters/scenes-server/scenes-server.h`는 하위 호환성 전용이며 `app/clusters/scenes-server/CodegenIntegration.h`를 포함한다. 새 코드는 `ScenesManagementCluster.h`를 직접 사용하도록 명시되어 있다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
