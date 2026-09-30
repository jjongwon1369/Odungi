---
entity: Scenes Management
ids: ['0x0062']
source_paths: ['data_model/1.7/clusters/Scenes.xml', 'src/app/clusters/scenes-server/AttributeValuePairValidator.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h', 'src/app/clusters/scenes-server/CodegenEndpointToIndex.h', 'src/app/clusters/scenes-server/CodegenIntegration.cpp', 'src/app/clusters/scenes-server/CodegenIntegration.h', 'src/app/clusters/scenes-server/Constants.h', 'src/app/clusters/scenes-server/ExtensionFieldSets.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h', 'src/app/clusters/scenes-server/SceneHandlerImpl.cpp', 'src/app/clusters/scenes-server/SceneHandlerImpl.h', 'src/app/clusters/scenes-server/SceneTable.h', 'src/app/clusters/scenes-server/SceneTableImpl.cpp', 'src/app/clusters/scenes-server/SceneTableImpl.h', 'src/app/clusters/scenes-server/ScenesIntegrationDelegate.h', 'src/app/clusters/scenes-server/ScenesManagementCluster.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.h', 'src/app/clusters/scenes-server/scenes-server.h', 'src/app/zap-templates/zcl/data-model/chip/scene.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Scenes Management

## 개요

Scenes Management는 장면 구성과 조작을 위한 속성 및 명령을 제공한다. 장면의 추가, 조회, 삭제, 현재 상태 저장, 저장된 상태 재현, 그룹 내 장면 조회 및 선택적 복사를 지원한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Scenes Management` |
| 스펙 이름 | `Scenes Management Cluster` |
| 클러스터 ID | `0x0062` |
| revision | `2` |
| 분류 | hierarchy=`base`, role=`application` |
| 범위 | `Endpoint` |
| PICS 코드 | `S` |
| 선택 기능 | `SceneNames` (`SN`, bit `0`) |

구현은 `ScenesManagementCluster`, 장면 저장소인 `SceneTable`, 클러스터별 상태 직렬화·적용 인터페이스인 `SceneHandler`로 구성된다. 장면 데이터에는 이름, 밀리초 단위 전환 시간, 클러스터별 확장 필드 집합이 포함된다.

## 스펙

출처: `data_model/1.7/clusters/Scenes.xml`

### revision 이력

- revision `1`
  - ZCL Scenes Cluster를 기반으로 클러스터 ID를 `0x0062`, 이름을 `Scenes Management`로 변경하고 provisional 상태를 제거했다.
  - 속성 `SceneCount`, `CurrentScene`, `CurrentGroup`, `SceneValid`, `NameSupport`를 제거했다.
  - 기능 `Explicit`, `TableSize`, `FabricScenes`를 제거했다.
  - 명령 `EnhancedAddScene`, `EnhancedAddSceneResponse`, `EnhancedViewScene`, `EnhancedViewSceneResponse`를 제거했다.
  - `AddScene`, `ViewSceneResponse`, `RecallScene`의 `TransitionTime`을 밀리초 단위로 변경했다.
- revision `2`
  - `SceneInfoStruct`의 `CurrentScene`, `CurrentGroup`, `SceneValid`를 deprecated 처리했다.

### 기능

| bit | 코드 | 이름 | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `SN` | `SceneNames` | 선택 | 장면 이름 저장 지원 |

### 데이터 타입

#### `CopyModeBitmap`

| bit | 필드 | 적합성 | 설명 |
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

구조체에 `fabricScoped="true"`가 지정되어 있다.

| 필드 ID | 이름 | 타입 | 기본값 | 조건 |
|---|---|---|---|---|
| `0` | `SceneCount` | `uint8` | — | 필수 |
| `1` | `CurrentScene` | `uint8` | `0xFF` | `fabricSensitive="true"`, revision `2`에서 deprecated |
| `2` | `CurrentGroup` | `group-id` | `0` | `fabricSensitive="true"`, revision `2`에서 deprecated |
| `3` | `SceneValid` | `bool` | `false` | `fabricSensitive="true"`, revision `2`에서 deprecated |
| `4` | `RemainingCapacity` | `uint8` | — | 필수, 최대 `253` |

### 속성

| ID | 이름 | 타입 | 접근 | 적합성·특성 |
|---|---|---|---|---|
| `0x0000` | `DoNotUse` | 미지정 | read, `view` | 사용 금지 |
| `0x0001` | `SceneTableSize` | `uint16` | read, `view` | 필수, persistence=`fixed` |
| `0x0002` | `FabricSceneInfo` | `list`, 항목 `SceneInfoStruct` | read, `view` | 필수, `fabricScoped="true"` |

### 명령

모든 요청은 `commandToServer` 방향이며 `fabricScoped="true"`이다.

| ID | 요청 | 호출 권한 | 적합성 | 응답 |
|---|---|---|---|---|
| `0x00` | `AddScene` | `manage` | 필수 | `AddSceneResponse` |
| `0x01` | `ViewScene` | `operate` | 필수 | `ViewSceneResponse` |
| `0x02` | `RemoveScene` | `manage` | 필수 | `RemoveSceneResponse` |
| `0x03` | `RemoveAllScenes` | `manage` | 필수 | `RemoveAllScenesResponse` |
| `0x04` | `StoreScene` | `manage` | 필수 | `StoreSceneResponse` |
| `0x05` | `RecallScene` | `operate` | 필수 | XML의 response 값은 `Y` |
| `0x06` | `GetSceneMembership` | `operate` | 필수 | `GetSceneMembershipResponse` |
| `0x40` | `CopyScene` | `manage` | 선택 | `CopySceneResponse` |

#### 요청 필드

아래 목록의 숫자는 필드 ID이다. 별도 표시가 없으면 필수 필드이다.

| 요청 | 필드 |
|---|---|
| `AddScene` | `0`: `GroupID` (`group-id`), `1`: `SceneID` (`uint8`), `2`: `TransitionTime` (`uint32`), `3`: `SceneName` (`string`), `4`: `ExtensionFieldSetStructs` (`list`, 항목 `ExtensionFieldSetStruct`) |
| `ViewScene` | `0`: `GroupID` (`group-id`), `1`: `SceneID` (`uint8`) |
| `RemoveScene` | `0`: `GroupID` (`group-id`), `1`: `SceneID` (`uint8`) |
| `RemoveAllScenes` | `0`: `GroupID` (`group-id`) |
| `StoreScene` | `0`: `GroupID` (`group-id`), `1`: `SceneID` (`uint8`) |
| `RecallScene` | `0`: `GroupID` (`group-id`), `1`: `SceneID` (`uint8`), `2`: `TransitionTime` (`uint32`, 선택, nullable) |
| `GetSceneMembership` | `0`: `GroupID` (`group-id`) |
| `CopyScene` | `0`: `Mode` (`CopyModeBitmap`), `1`: `GroupIdentifierFrom` (`group-id`), `2`: `SceneIdentifierFrom` (`uint8`), `3`: `GroupIdentifierTo` (`group-id`), `4`: `SceneIdentifierTo` (`uint8`) |

공통 제약:

- `SceneID`, `SceneIdentifierFrom`, `SceneIdentifierTo`: 최대 `254`.
- `TransitionTime`: 최대 `60000000`, 단위는 밀리초.
- `SceneName`: 최대 길이 `16`.

#### 응답 필드

응답 방향은 `responseFromServer`이다.

| ID | 응답 | 필드 |
|---|---|---|
| `0x00` | `AddSceneResponse` | `0`: `Status`, `1`: `GroupID`, `2`: `SceneID` |
| `0x01` | `ViewSceneResponse` | `0`: `Status`, `1`: `GroupID`, `2`: `SceneID`, `3`: `TransitionTime`, `4`: `SceneName`, `5`: `ExtensionFieldSetStructs` |
| `0x02` | `RemoveSceneResponse` | `0`: `Status`, `1`: `GroupID`, `2`: `SceneID` |
| `0x03` | `RemoveAllScenesResponse` | `0`: `Status`, `1`: `GroupID` |
| `0x04` | `StoreSceneResponse` | `0`: `Status`, `1`: `GroupID`, `2`: `SceneID` |
| `0x06` | `GetSceneMembershipResponse` | `0`: `Status`, `1`: `Capacity`, `2`: `GroupID`, `3`: `SceneList` |
| `0x40` | `CopySceneResponse` | `0`: `Status`, `1`: `GroupIdentifierFrom`, `2`: `SceneIdentifierFrom` |

- `Status`의 타입은 `status`이다.
- `ViewSceneResponse`의 `TransitionTime`, `SceneName`, `ExtensionFieldSetStructs`는 `Status == SUCCESS`일 때 필수이다.
- `Capacity`는 필수 `uint8`이며 nullable이다.
- `SceneList`는 `uint8` 항목의 `list`이며 `Status == SUCCESS`일 때 필수이다.
- `CopySceneResponse`는 `CopyScene`을 지원할 때 필수이다.
- 응답의 장면 식별자, 전환 시간 및 이름에도 위의 해당 제약이 적용된다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/scene.xml`

### ZAP 메타데이터

| 항목 | 정의 |
|---|---|
| 이름 | `Scenes Management` |
| 클러스터 코드 | `0x0062` |
| domain | `General` |
| define | `SCENES_CLUSTER` |
| client / server | 모두 지원, `tick="false"`, `init="false"` |
| revision 전역 속성 | `0xFFFD`, 값 `2` |
| `SceneTableSize` | `0x0001`, `SCENE_TABLE_SIZE`, `int16u` |
| `FabricSceneInfo` | `0x0002`, `FABRIC_SCENE_INFO`, `array`, 항목 `SceneInfoStruct` |

파일 주석은 Alchemy 생성 파일이며 직접 편집하지 않도록 명시한다. 생성 원본은 `src/app_clusters/Scenes.adoc`, Git 표기는 `0.9-1.7-winter2027`, Alchemy 버전은 `v1.7.10`이다.

### 타입 표현

- `CopyModeBitmap`: `bitmap8`, `CopyAllScenes` mask=`0x01`.
- `AttributeValuePairStruct`:
  - `AttributeID`는 `attrib_id`.
  - 값 필드는 `int8u`, `int8s`, `int16u`, `int16s`, `int32u`, `int32s`, `int64u`, `int64s`.
  - 각 값 필드는 `optional="true"` 및 choice=`a`.
- `ExtensionFieldSetStruct`:
  - `ClusterID`는 `cluster_id`.
  - `AttributeValueList`는 `AttributeValuePairStruct` 배열.
- `SceneInfoStruct`:
  - `isFabricScoped="true"`.
  - `CurrentScene`, `CurrentGroup`, `SceneValid`에 `isFabricSensitive="true"` 지정.
  - `SceneValid` 기본값은 `0`으로 표현한다.

### 스펙과의 표현 차이

- 스펙의 `DoNotUse`는 SDK XML에 정의되어 있지 않다.
- 스펙에서 deprecated 처리한 `SceneInfoStruct` 필드는 SDK XML에 유지되어 있으며, 별도 deprecated 표시는 없다.
- `ViewSceneResponse`의 성공 시 필수 필드와 `GetSceneMembershipResponse`의 `SceneList`는 SDK XML에서 `optional="true"`로 표현한다.
- `CopyScene`의 `Mode`에는 최대값 `0x01`이 명시되어 있다.
- `manage` 명령에는 명시적인 접근 설정이 있다. `ViewScene`, `RecallScene`, `GetSceneMembership`에는 SDK XML 내 별도 접근 설정이 없다.
- 서버 응답 명령에는 `disableDefaultResponse="true"`가 지정되어 있다.

### CLI 메타데이터

다음은 XML의 `cli` 값이며, 전체 실행 인자 예시는 제공되지 않았다.

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

### 주요 파일

| 역할 | 파일 |
|---|---|
| 클러스터 처리 | `src/app/clusters/scenes-server/ScenesManagementCluster.h`<br>`src/app/clusters/scenes-server/ScenesManagementCluster.cpp` |
| codegen 통합 | `src/app/clusters/scenes-server/CodegenIntegration.h`<br>`src/app/clusters/scenes-server/CodegenIntegration.cpp` |
| 장면 저장소 | `src/app/clusters/scenes-server/SceneTable.h`<br>`src/app/clusters/scenes-server/SceneTableImpl.h`<br>`src/app/clusters/scenes-server/SceneTableImpl.cpp` |
| 장면 핸들러 | `src/app/clusters/scenes-server/SceneHandlerImpl.h`<br>`src/app/clusters/scenes-server/SceneHandlerImpl.cpp` |
| 확장 필드 집합 | `src/app/clusters/scenes-server/ExtensionFieldSets.h`<br>`src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h`<br>`src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp` |
| 속성 값 검증 | `src/app/clusters/scenes-server/AttributeValuePairValidator.h`<br>`src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h`<br>`src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp` |
| 다른 클러스터와의 통합 | `src/app/clusters/scenes-server/ScenesIntegrationDelegate.h` |
| Endpoint 인덱싱 | `src/app/clusters/scenes-server/CodegenEndpointToIndex.h` |
| 상수 | `src/app/clusters/scenes-server/Constants.h` |
| 하위 호환 헤더 | `src/app/clusters/scenes-server/scenes-server.h` |

### 클러스터 구성과 수명 주기

`ScenesManagementCluster`는 다음 인터페이스를 상속한다.

- `DefaultServerCluster`
- `FabricTable::Delegate`
- `scenes::ScenesIntegrationDelegate`

`Context`로 주입하는 의존성은 `groupDataProvider`, `fabricTable`, `features`, `sceneTableProvider`, `supportsCopyScene`이다.

| 메서드 | 동작 |
|---|---|
| `Startup` | 저장소와 데이터 모델로 장면 테이블을 초기화하고 fabric delegate를 등록한다. 기존 fabric마다 `UpdateFabricSceneInfo`를 호출한다. |
| `Shutdown` | fabric delegate를 제거한다. `ClusterShutdownType::kPermanentRemove`이면 영속 데이터를 삭제한다. |
| `ClearPersistentData` | 시작된 상태인지 확인한 후 `RemoveEndpoint`를 호출한다. |
| `OnFabricCommitted` | 해당 fabric의 `FabricSceneInfo`를 갱신한다. |
| `OnFabricRemoved` | 해당 fabric의 장면을 제거하고 메모리의 `SceneInfoStruct`를 정리한다. |
| `AcceptedCommands` / `GeneratedCommands` | 필수 명령과 응답을 제공하고, `mSupportCopyScenes`가 참이면 `CopyScene`과 `CopySceneResponse`를 추가한다. |
| `InvokeCommand` | 요청을 디코딩하여 각 `Handle...` 메서드로 전달한다. 알 수 없는 명령에는 `Status::UnsupportedCommand`를 반환한다. |

`ReadAttribute`는 `ClusterRevision`, `FeatureMap`, `SceneTableSize`, `FabricSceneInfo`를 처리한다. `FabricSceneInfo`를 읽을 때는 다른 fabric의 사용량을 반영하도록 각 항목의 `remainingCapacity`를 다시 계산한다.

### `FabricSceneInfo` 관리

`FabricSceneInfo`는 최대 `CHIP_CONFIG_MAX_FABRICS`개의 `SceneInfoStruct`를 보관한다.

`UpdateFabricSceneInfo`는 다음 값을 설정한다.

- `currentGroup = 0`
- `currentScene = 0xFF`
- `sceneValid = false`
- `sceneCount`: `GetFabricSceneCount` 결과
- `remainingCapacity`: `GetRemainingCapacity` 결과

갱신 후 `NotifyAttributeChanged`로 `FabricSceneInfo` 변경을 알린다. `RecallSceneParse`도 이 함수를 호출하므로, 제공된 구현에서는 장면 재현 후에도 `sceneValid`를 `true`로 설정하지 않는다.

### 명령 처리 흐름

| 처리 함수 | 주요 동작 |
|---|---|
| `HandleAddScene` | 전환 시간, 이름 길이, 장면 식별자를 검사한다. 지원 핸들러의 `SerializeAdd`로 확장 필드를 처리하고, 잔여 용량 확인 후 저장한다. `SceneNames`가 활성화된 경우에만 이름을 저장한다. |
| `HandleViewScene` | 장면을 읽고 지원 핸들러의 `Deserialize`로 응답용 확장 필드를 구성한다. 성공 시 이름, 전환 시간, 확장 필드 목록을 반환한다. |
| `HandleRemoveScene` | 장면 존재를 확인한 뒤 삭제하고 `FabricSceneInfo`를 갱신한다. |
| `HandleRemoveAllScenes` | 지정 그룹의 모든 장면을 삭제하고 `FabricSceneInfo`를 갱신한다. |
| `HandleStoreScene` / `StoreSceneParse` | 현재 클러스터 상태를 `SceneSaveEFS`로 수집하여 저장한다. 새 장면은 빈 이름과 전환 시간 `0`으로 시작한다. 기존 장면은 확장 필드를 다시 구성하며, `SceneNames` 미지원 시 이름을 비운다. |
| `HandleRecallScene` / `RecallSceneParse` | 저장된 장면을 읽고 `SceneApplyEFS`를 호출한다. 요청의 `TransitionTime`이 존재하고 null이 아니면 적용 시 전환 시간을 대체한다. |
| `HandleGetSceneMembership` | 잔여 용량과 지정 그룹의 장면 식별자 목록을 반환한다. |
| `HandleCopyScene` | 출발·도착 그룹과 식별자를 검사한 뒤 단일 장면 또는 그룹 내 장면들을 복사한다. 전체 복사에서는 각 장면 식별자를 유지하고 도착 그룹으로 변경한다. |

그룹 검사에서 `GroupID`가 `0`이 아니면 `HasEndpoint`로 해당 fabric·그룹에 Endpoint가 속하는지 확인한다. 검사에 실패하면 `Status::InvalidCommand` 또는 대응하는 `CHIP_ERROR`를 반환한다.

`HandleCopyScene`은 도착 장면이 이미 존재하면 새 슬롯을 위한 용량 검사를 생략한다. 전체 복사에서는 각 저장 후 `UpdateFabricSceneInfo`를 호출하므로 중간 실패 이전의 갱신이 반영된다.

#### 오류 변환

`ResponseStatus`의 명시적 변환은 다음과 같다.

| 오류 | 응답 상태 |
|---|---|
| `CHIP_ERROR_NOT_FOUND` | `Status::NotFound` |
| `CHIP_ERROR_NO_MEMORY` | `Status::ResourceExhausted` |
| `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)` | `Status::InvalidCommand` |
| 그 외 | `StatusIB(err).mStatus` |

`HandleRecallScene`은 별도로 성공과 `CHIP_ERROR_NOT_FOUND`를 처리하고, 나머지는 `StatusIB(err).mStatus`로 변환한다.

### 장면 저장소와 용량

`SceneTable<EFStype>`는 초기화, 장면 조회·저장·삭제, 그룹별 조회·삭제, 핸들러 등록, 확장 필드 저장·적용, fabric 및 Endpoint 제거를 정의한다.

`DefaultSceneTableImpl`은 `PersistentStorageDelegate`와 `app::Storage::FabricTableImpl`을 사용하여 여러 fabric의 장면을 영속 저장한다.

#### 저장 데이터

- `SceneStorageId`
  - `mGroupId`, `mSceneId`를 보관한다.
  - 기본값은 `kGlobalGroupSceneId`, `kUndefinedSceneId`이다.
  - `IsValid`는 `mSceneId != kUndefinedSceneId`를 검사한다.
- `SceneData`
  - `mName`, `mNameLength`
  - `mSceneTransitionTimeMs`
  - `mExtensionFieldSets`
- `SceneTableEntry`
  - `app::Storage::Data::TableEntry<SceneStorageId, SceneData>`의 별칭이다.

`SetName`은 최대 `kSceneNameMaxLength`까지 복사한다. 이름 길이가 `0`이면 저장 시 이름 필드를 생략한다. 전환 시간과 확장 필드 집합은 직렬화 대상에 포함된다.

#### 설정 상수

| 식별자 | 값 또는 설정 |
|---|---|
| `kMaxScenesPerEndpoint` | `CHIP_CONFIG_MAX_SCENES_TABLE_SIZE`, 컴파일 시 최소 `16` 확인 |
| `kMaxScenesPerFabric` | `(kMaxScenesPerEndpoint - 1) / 2` |
| `kSceneNameMaxLength` | `CHIP_CONFIG_SCENES_CLUSTER_MAXIMUM_NAME_LENGTH` |
| `kScenesMaxTransitionTime` | `60'000'000u` |
| `kMaxClustersPerScene` | `CHIP_CONFIG_SCENES_MAX_CLUSTERS_PER_SCENE` |
| `kMaxFieldBytesPerCluster` | `CHIP_CONFIG_SCENES_MAX_EXTENSION_FIELDSET_SIZE_PER_CLUSTER` |
| `kMaxAvPair` | `CHIP_CONFIG_SCENES_MAX_AV_PAIRS_EFS` |
| `Serializer::kEntryMaxBytes()` | `CHIP_CONFIG_SCENES_MAX_SERIALIZED_SCENE_SIZE_BYTES` |
| `Serializer::kFabricMaxBytes()` | `128` |
| `kGlobalSceneId` | `0` |
| `kGlobalSceneGroupId` | `0` |
| `kGlobalGroupSceneId` | `0x0000` |
| `kUndefinedSceneId` | `0xff` |

`SetTableSize`는 Endpoint 크기와 `(endpointSceneTableSize - 1) / 2`를 `FabricTableImpl::SetTableSize`에 전달한다.

저장 키는 다음 할당 함수를 사용한다.

- `DefaultStorageKeyAllocator::EndpointSceneCountKey`
- `DefaultStorageKeyAllocator::FabricSceneKey`
- `DefaultStorageKeyAllocator::FabricSceneDataKey`

### 확장 필드 집합

`ExtensionFieldSet`은 클러스터 하나의 데이터를 다음 멤버로 보관한다.

- `mID`: 클러스터 ID.
- `mBytesBuffer`: 직렬화된 데이터.
- `mUsedBytes`: 사용한 바이트 수.

TLV 직렬화에는 `TagEFS::kClusterID`, `TagEFS::kClusterFieldSetData`를 사용한다. `ExtensionFieldSetsImpl`은 이를 `TagEFS::kFieldSetArrayContainer` 배열로 저장한다.

| 메서드 | 동작 |
|---|---|
| `InsertFieldSet` | 잘못된 클러스터 ID와 빈 데이터를 거부한다. 동일한 `mID`가 있으면 덮어쓰고, 없으면 첫 빈 위치에 삽입한다. 공간 부족 시 `CHIP_ERROR_NO_MEMORY`를 반환한다. |
| `GetFieldSetAtPosition` | 유효 범위 밖 위치에 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. |
| `RemoveFieldAtPosition` | 삭제 후 배열을 압축한다. 범위 밖 위치는 성공으로 처리한다. |
| `Clear` | 저장된 필드를 지우고 개수를 `0`으로 만든다. |
| `Deserialize` | 저장 데이터를 모두 읽을 수 있어야 한다. 클러스터 수 한도를 초과하면 `CHIP_ERROR_BUFFER_TOO_SMALL`을 반환한다. |

`ExtensionFieldSet::Deserialize`는 바이트 데이터가 버퍼보다 크면 `CHIP_ERROR_BUFFER_TOO_SMALL`을 반환한다. OTA로 클러스터 수 한도가 줄어든 경우에도 확장 필드 집합을 잘라서 읽지 않으며, 소스 주석은 해당 장면 삭제가 필요하다고 설명한다.

### `SceneHandler` 계약

`SceneHandler`는 클러스터 상태와 장면 테이블을 연결한다.

| 메서드 | 역할 |
|---|---|
| `SupportsCluster` | Endpoint와 클러스터 조합의 지원 여부 판단 |
| `SerializeAdd` | `AddScene`의 확장 필드 직렬화 |
| `SerializeSave` | `StoreScene`을 위한 현재 상태 직렬화 |
| `Deserialize` | 저장된 데이터를 `ExtensionFieldSetStruct`로 복원 |
| `ApplyScene` | 저장된 상태를 `TransitionTimeMs`에 걸쳐 적용 |

계약상 하나의 Endpoint·클러스터 조합을 담당하는 핸들러는 하나여야 한다. 여러 핸들러가 같은 조합을 지원하면 어느 핸들러가 선택되는지는 인터페이스 계약에서 보장하지 않는다. 제공된 저장소 구현은 목록에서 처음 발견한 지원 핸들러를 호출한다.

- `SceneSaveEFS`: 데이터 모델의 서버 클러스터 목록을 순회하며 `SerializeSave`를 호출한다.
- `SceneApplyEFS`: 저장된 확장 필드를 순회하며 `ApplyScene`을 호출한다.
- `RegisterHandler`: 핸들러를 `mHandlerList` 앞에 추가한다.

#### `DefaultSceneHandlerImpl`

`DefaultSceneHandlerImpl`은 `SerializeAdd`와 `Deserialize`의 기본 구현을 제공한다.

- `SerializeAdd`
  1. 속성 값 쌍 개수가 `kMaxAvPair` 이하인지 검사한다.
  2. 각 값 쌍에 `mValidator.Validate`를 호출한다.
  3. 검증·보정된 목록을 TLV로 인코딩한다.
- `Deserialize`
  1. TLV 배열을 디코딩한다.
  2. 멤버 배열 `mAVPairs`의 용량을 검사한다.
  3. `clusterID`와 `attributeValueList`를 구성한다.

`SerializeSave`, `ApplyScene`은 제공하지 않으므로 `SerializeAdd` 출력과 호환되도록 구현해야 한다. `SupportsCluster`도 별도로 구현해야 한다.

`DecodeAttributeValueList` 결과는 원본 바이트 버퍼가 존재하고 변경되지 않는 동안만 유효하다.

### 속성 값 검증과 보정

`AttributeValuePairValidator::Validate`는 클러스터 경로와 수정 가능한 값 쌍을 받는다. `CodegenAttributeValuePairValidator`는 codegen 속성 메타데이터를 사용한다.

검증 순서:

1. `emberAfLocateAttributeMetadata`로 속성을 찾는다.
2. 메타데이터가 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
3. `IsExactlyOneValuePopulated`로 값 필드가 정확히 하나인지 검사한다.
4. `AttributeBaseType`에 맞는 값 필드가 설정되었는지 검사한다.
5. `CapAttributeValue`로 값을 보정한다.

| 속성 타입 | 사용하는 값 필드 |
|---|---|
| `ZCL_BOOLEAN_ATTRIBUTE_TYPE`, `ZCL_INT8U_ATTRIBUTE_TYPE` | `valueUnsigned8` |
| `ZCL_INT16U_ATTRIBUTE_TYPE` | `valueUnsigned16` |
| `ZCL_INT24U_ATTRIBUTE_TYPE`, `ZCL_INT32U_ATTRIBUTE_TYPE` | `valueUnsigned32` |
| `ZCL_INT40U_ATTRIBUTE_TYPE`, `ZCL_INT48U_ATTRIBUTE_TYPE`, `ZCL_INT56U_ATTRIBUTE_TYPE`, `ZCL_INT64U_ATTRIBUTE_TYPE` | `valueUnsigned64` |
| `ZCL_INT8S_ATTRIBUTE_TYPE` | `valueSigned8` |
| `ZCL_INT16S_ATTRIBUTE_TYPE` | `valueSigned16` |
| `ZCL_INT24S_ATTRIBUTE_TYPE`, `ZCL_INT32S_ATTRIBUTE_TYPE` | `valueSigned32` |
| `ZCL_INT40S_ATTRIBUTE_TYPE`, `ZCL_INT48S_ATTRIBUTE_TYPE`, `ZCL_INT56S_ATTRIBUTE_TYPE`, `ZCL_INT64S_ATTRIBUTE_TYPE` | `valueSigned64` |

- 값 개수 또는 필드 타입이 잘못되면 `CHIP_ERROR_INVALID_ARGUMENT`.
- 지원하지 않는 기반 타입이면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`.
- 최소·최대 메타데이터가 있으면 이를 사용하고, 없으면 타입과 nullable 여부에 따른 범위를 사용한다.
- nullable 속성의 범위 밖 값은 null로 설정한다.
- nullable이 아니면 최소·최대값으로 제한한다.
- boolean은 `uint8_t`로 표현하되 범위 계산에는 `bool`을 사용한다.
- 24·40·48·56비트 정수에는 `OddSizedInteger`를 사용한다.

### codegen 및 다른 클러스터와의 통합

`IntegrationDelegate::CreateRegistration`은 다음을 수행한다.

1. `Attributes::SceneTableSize::GetDefault`로 Endpoint의 테이블 크기를 읽는다.
2. `acceptedCommandList`에서 `CopyScene` 지원 여부를 확인한다.
3. `DefaultScenesManagementTableProvider`에 Endpoint와 크기를 설정한다.
4. 그룹 데이터 공급자, fabric 테이블, 기능 비트맵, 테이블 공급자를 사용해 `ScenesManagementCluster`를 생성한다.

등록 가능한 인스턴스 수는 고정 클러스터 수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합이다.

- `MatterScenesManagementClusterInitCallback`: 서버 등록.
- `MatterScenesManagementClusterShutdownCallback`: 서버 등록 해제.
- `MatterScenesManagementPluginServerInitCallback`: 빈 구현.
- `FindClusterOnEndpoint`: 클러스터가 없거나 초기화되지 않았으면 `nullptr` 반환.
- `ScenesServer::Instance`: 통합용 단일 인스턴스 제공.
- `RegisterSceneHandler`, `UnregisterSceneHandler`: 등록 상태를 확인하여 중복 등록·해제를 방지.

`ScenesIntegrationDelegate`는 `OnOff`, `LevelControl`, `ColorControl` 등에서 사용할 수 있는 다음 인터페이스를 정의한다.

- `StoreCurrentGlobalScene`
- `RecallGlobalScene`
- `GroupWillBeRemoved`

전역 장면은 그룹 `0`, 장면 `0`이다. `GroupWillBeRemoved` 구현은 대상 그룹의 장면들을 삭제한다.

`CodegenEndpointToIndex::EndpointIdToIndex`는 `emberAfGetClusterServerEndpointIndex`로 0 기반 인덱스를 얻고 `MaxIndexCount` 범위를 검사한다. `DefaultSceneHandlerImpl::TransitionTimeInterface`는 이와 같은 `Finder`를 사용하여 Endpoint별 이벤트 제어 객체에 callback을 설정한다.

### 구현상 주의사항

- **공유 저장소:** `GetSceneTableImpl`은 하나의 정적 `DefaultSceneTableImpl`을 재사용하며 호출마다 Endpoint와 테이블 크기를 설정한다. 소스 주석은 반환 포인터를 캐시하지 말고, 여러 Endpoint에서 사용할 때 호출을 thread-safe하게 처리하도록 명시한다.
- **공급자 계약:** `ScopedSceneTable`은 생성 시 `Take`, 소멸 시 `Release`를 호출한다. `Take`가 `nullptr`를 반환하면 `VerifyOrDie`가 실행된다.
- **설정 일치:** `SCENES_MANAGEMENT_TABLE_SIZE`가 설정된 경우 `kMaxScenesPerEndpoint` 이하인지 컴파일 시 검사한다. ZAP 값만 변경하지 말고 `CHIP_CONFIG`도 함께 맞추도록 주석에 명시되어 있다.
- **테이블 크기 반환:** 제공된 코드에서 `GetTableSize`는 `mCurrentTableSize`를 반환하지만, `SetTableSize` 본문에는 이 멤버를 갱신하는 대입이 없다.
- **`AddScene` 용량 검사:** `HandleAddScene`은 저장 전에 잔여 용량이 `0`이면 `Status::ResourceExhausted`를 반환한다. 이 경로에는 기존 장면 덮어쓰기를 구분하는 검사가 없다.
- **전환 시간 검사:** `HandleAddScene`은 최대 전환 시간을 직접 검사한다. 제공된 `HandleRecallScene`과 `RecallSceneParse` 본문에는 같은 최대값 검사가 없다.
- **그룹 제거 후 정보 갱신:** `GroupWillBeRemoved`는 그룹 장면을 삭제하지만, 해당 함수 안에서 `UpdateFabricSceneInfo`를 호출하지 않는다.
- **호환 헤더:** `src/app/clusters/scenes-server/scenes-server.h`는 하위 호환용이다. 새 코드는 `ScenesManagementCluster.h`를 직접 사용하도록 명시되어 있다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
