---
entity: Groups
ids: ['0x0004']
source_paths: ['data_model/1.7/clusters/Groups.xml', 'src/app/clusters/groups-server/CodegenIntegration.cpp', 'src/app/clusters/groups-server/GroupsCluster.h', 'src/app/clusters/groups-server/GroupsClusterContext.h', 'src/app/clusters/groups-server/GroupsClusterImpl.cpp', 'src/app/clusters/groups-server/GroupsClusterImpl.h', 'src/app/clusters/groups-server/StubbedGroupsCluster.cpp', 'src/app/clusters/groups-server/StubbedGroupsCluster.h', 'src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Groups

## 개요

`Groups`는 서버 엔드포인트의 그룹 구성과 멤버십 관리를 위한 속성 및 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Groups` |
| 클러스터 ID | `0x0004` |
| 스펙 revision | `5` |
| 분류 | hierarchy: `base`, role: `utility` |
| 범위 | `Endpoint` |
| PICS 코드 | `G` |

revision `5`부터 `Groupcast`로 대체하기 위한 사용 중단 절차가 시작된다. 제공된 구현은 빌드 설정에 따라 전체 명령을 지원하는 `GroupsClusterImpl`과 호환성 전용 `StubbedGroupsCluster` 중 하나를 선택한다.

## 스펙

출처: `data_model/1.7/clusters/Groups.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가; CCB 1745 2100 |
| `2` | CCB 2289 |
| `3` | CCB 2310 2704 |
| `4` | 새로운 데이터 모델 형식 및 표기 적용 |
| `5` | `Groupcast`로 대체하기 위한 `Groups` 사용 중단 절차 시작 |

### 기능 및 데이터 타입

| 종류 | 이름 | 비트 | 적합성 | 설명 |
|---|---|---|---|---|
| 기능 | `GroupNames` | `0` | 선택 | 그룹 이름 저장 기능. 코드: `GN` |
| `NameSupportBitmap` 비트 필드 | `GroupNames` | `7` | 필수 | 그룹 이름 저장 지원 표시 |

기능의 `GroupNames`와 `NameSupportBitmap`의 `GroupNames`는 서로 다른 비트 위치를 사용한다.

### 속성

| ID | 이름 | 타입 | 접근 | 영속성 | 적합성 |
|---|---|---|---|---|---|
| `0x0000` | `NameSupport` | `NameSupportBitmap` | 읽기, `view` | `fixed` | 필수 |

### 서버 수신 명령

모든 명령은 `commandToServer` 방향이며 필수이다. 호출은 모두 `fabricScoped="true"`로 정의된다.

필드 표기는 `필드 ID: 이름 — 타입 및 제약`이며, 나열된 필드는 모두 필수이다.

| ID | 명령 | 호출 권한 | 필드 | 응답 |
|---|---|---|---|---|
| `0x00` | `AddGroup` | `manage` | `0: GroupID` — `group-id`, 최솟값 `1`<br>`1: GroupName` — `string`, 최대 길이 `16` | `AddGroupResponse` |
| `0x01` | `ViewGroup` | `operate` | `0: GroupID` — `group-id`, 최솟값 `1` | `ViewGroupResponse` |
| `0x02` | `GetGroupMembership` | `operate` | `0: GroupList` — `list`, 항목 타입 `group-id`, 항목 최솟값 `1` | `GetGroupMembershipResponse` |
| `0x03` | `RemoveGroup` | `manage` | `0: GroupID` — `group-id`, 최솟값 `1` | `RemoveGroupResponse` |
| `0x04` | `RemoveAllGroups` | `manage` | 없음 | `Y` |
| `0x05` | `AddGroupIfIdentifying` | `manage` | `0: GroupID` — `group-id`, 최솟값 `1`<br>`1: GroupName` — `string`, 최대 길이 `16` | `Y` |

### 서버 응답 명령

모든 응답은 `responseFromServer` 방향이며 필수이다. 나열된 필드도 모두 필수이다.

| ID | 응답 | 필드 |
|---|---|---|
| `0x00` | `AddGroupResponse` | `0: Status` — `enum8`<br>`1: GroupID` — `group-id`, 최솟값 `1` |
| `0x01` | `ViewGroupResponse` | `0: Status` — `enum8`<br>`1: GroupID` — `group-id`, 최솟값 `1`<br>`2: GroupName` — `string`, 최대 길이 `16` |
| `0x02` | `GetGroupMembershipResponse` | `0: Capacity` — `uint8`, nullable<br>`1: GroupList` — `list`, 항목 타입 `group-id`, 항목 최솟값 `1` |
| `0x03` | `RemoveGroupResponse` | `0: Status` — `enum8`<br>`1: GroupID` — `group-id`, 최솟값 `1` |

`Status`의 구체적인 허용 값은 제공된 스펙 XML에 나열되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml`

### 기본 정의

| 항목 | 정의 |
|---|---|
| 이름 | `Groups` |
| 도메인 | `General` |
| 코드 | `0x0004` |
| define | `GROUPS_CLUSTER` |
| client / server | 모두 활성화, 각각 `init="false"`, `tick="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="5"` |
| 기능 | `GroupNames`, bit `0`, code `GN`, 선택 |

이 파일은 Alchemy로 생성되었으며 직접 편집하지 않도록 표시되어 있다. 생성 원본은 `src/app_clusters/Groups.adoc`이다.

### 타입 및 속성 표현

- `NameSupportBitmap`
  - 기본 타입: `bitmap8`
  - `GroupNames` 마스크: `0x80`
- `NameSupport`
  - `side="server"`
  - `code="0x0000"`
  - `define="GROUP_NAME_SUPPORT"`
  - 타입: `NameSupportBitmap`
  - `max="0x80"`

스펙과 SDK XML의 타입 표현은 다음과 같다.

| 스펙 표현 | SDK 표현 | 사용 위치 |
|---|---|---|
| `group-id` | `group_id` | `GroupID`, `GroupList` 항목 |
| `string` | `char_string` | `GroupName` |
| `uint8` | `int8u` | `Capacity` |
| `list` | `array="true"` | `GroupList` |

`GroupName`은 `length="16"`, `Capacity`는 `isNullable="true"`로 정의된다. SDK XML의 `GroupList`에는 스펙 XML과 달리 항목의 `min="1"`이 명시되어 있지 않다.

### 명령 메타데이터

서버 수신 명령은 `source="client"` 및 `isFabricScoped="true"`로 정의된다. 응답 명령은 `source="server"` 및 `disableDefaultResponse="true"`로 정의된다.

| 명령 | SDK 설명 | CLI 메타데이터 |
|---|---|---|
| `AddGroup` | 서버 엔드포인트를 특정 그룹에 추가 | `zcl groups add` |
| `ViewGroup` | 특정 그룹의 이름을 `ViewGroupResponse`로 요청 | `zcl groups view` |
| `GetGroupMembership` | 서버 엔드포인트의 그룹 멤버십 조회 | `zcl groups get` |
| `RemoveGroup` | 특정 그룹에서 서버 엔드포인트의 멤버십 제거 | `zcl groups remove` |
| `RemoveAllGroups` | 서버 엔드포인트의 모든 그룹 연결 제거 | `zcl groups rmall` |
| `AddGroupIfIdentifying` | 엔드포인트가 식별 중일 때만 그룹에 추가 | `zcl groups add-if-id` |

- `GetGroupMembership`의 `cliFunctionName`은 `zclGroupsGetCommand`이다.
- `AddGroup`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying`에는 `manage` 호출 권한이 명시되어 있다.
- `ViewGroup`, `GetGroupMembership`에는 SDK XML 내 별도의 접근 권한 요소가 없다. 스펙 XML에는 `operate`가 명시되어 있다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/groups-server/CodegenIntegration.cpp` | 서버 인스턴스 생성, 등록, 조회 및 해제 |
| `src/app/clusters/groups-server/GroupsCluster.h` | 빌드 설정에 따른 `GroupsCluster` 별칭 선택 |
| `src/app/clusters/groups-server/GroupsClusterContext.h` | 두 구현이 공유하는 생성 컨텍스트 |
| `src/app/clusters/groups-server/GroupsClusterImpl.h` | 전체 구현 클래스 선언 |
| `src/app/clusters/groups-server/GroupsClusterImpl.cpp` | 전체 구현의 속성 읽기 및 명령 처리 |
| `src/app/clusters/groups-server/StubbedGroupsCluster.h` | 호환성 전용 구현 클래스 선언 |
| `src/app/clusters/groups-server/StubbedGroupsCluster.cpp` | 호환성 전용 구현의 속성 읽기 및 명령 처리 |

### 구현 선택과 공통 컨텍스트

`GroupsCluster.h`는 `chip::app::Clusters`에서 다음 별칭을 정의한다.

| 조건 | `GroupsCluster` |
|---|---|
| `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER` 활성화 | `StubbedGroupsCluster` |
| 그 외 | `GroupsClusterImpl` |

원문 주석은 `Groupcast`가 활성화된 빌드에서 호환성 전용 구현을 사용한다고 설명한다. 애플리케이션에는 구체적인 클래스 대신 `GroupsCluster` 별칭 사용을 권장한다.

두 클래스는 모두 `DefaultServerCluster`를 상속하고 `Context`를 `GroupsClusterContext`의 별칭으로 사용한다.

| 멤버 | 타입 | 용도 |
|---|---|---|
| `groupDataProvider` | `Credentials::GroupDataProvider &` | 그룹 데이터 접근 |
| `scenesIntegration` | `scenes::ScenesIntegrationDelegate *` | 기본값 `nullptr`; 이 경우 scenes 연동 없음 |
| `identifyIntegration` | `IdentifyIntegrationDelegate *` | 기본값 `nullptr`; 이 경우 identify 연동 없음 |

`StubbedGroupsCluster`는 `groupDataProvider`만 사용한다. `ScenesIntegrationDelegate`는 호환성 전용 구현에 scenes 구현 및 링크 의존성을 끌어오지 않도록 전방 선언된다.

### 서버 등록과 수명 주기

`CodegenIntegration.cpp`는 다음 크기로 서버 저장 공간을 구성한다.

- `kGroupsFixedClusterCount`: `Groups::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kGroupsMaxClusterCount`: `kGroupsFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: `LazyRegisteredServerCluster<GroupsCluster>` 배열

`IntegrationDelegate`의 동작:

- `CreateRegistration`
  - `Credentials::GetGroupDataProvider()`를 호출하고 결과가 `nullptr`이 아닌지 `VerifyOrDie`로 확인한다.
  - `GroupsCluster::Context`를 구성하여 인스턴스를 생성한다.
  - `MATTER_DM_PLUGIN_SCENES_MANAGEMENT`가 정의되면 `ScenesManagement::FindClusterOnEndpoint(endpointId)`를 연결한다.
  - `ZCL_USING_IDENTIFY_CLUSTER_SERVER`가 정의되면 `FindIdentifyClusterOnEndpoint(endpointId)`를 연결한다.
- `FindRegistration`: 생성된 인스턴스를 반환하며, 생성되지 않았으면 `nullptr`을 반환한다.
- `ReleaseRegistration`: 인스턴스의 `Destroy()`를 호출한다.

| 콜백 | 동작 |
|---|---|
| `MatterGroupsClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false` |
| `MatterGroupsClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 및 `shutdownType` 전달 |
| `MatterGroupsPluginServerInitCallback` | 빈 함수 |
| `MatterGroupsPluginServerShutdownCallback` | 빈 함수 |

### 속성 및 명령 목록

두 구현 모두:

- `Attributes`에서 `Attributes::kMandatoryMetadata`를 추가한다.
- `AcceptedCommands`에서 여섯 수신 명령을 모두 노출한다.
- `GeneratedCommands`에서 `AddGroupResponse`, `ViewGroupResponse`, `GetGroupMembershipResponse`, `RemoveGroupResponse`를 노출한다.

`ReadAttribute`의 반환값은 다음과 같다.

| 속성 | `GroupsClusterImpl` | `StubbedGroupsCluster` |
|---|---|---|
| `ClusterRevision` | `4`로 고정 | `kRevision` |
| `FeatureMap` | `Feature::kGroupNames` | `Feature::kGroupNames` |
| `NameSupport` | `NameSupportBitmap::kGroupNames` | `NameSupportBitmap::kGroupNames` |
| 그 외 | `Status::UnsupportedAttribute` | `Status::UnsupportedAttribute` |

`StubbedGroupsCluster.cpp`는 `static_assert`로 `Groups::kRevision >= 5`를 요구한다.

> 스펙 및 SDK XML에서 기능 `GroupNames`는 선택 사항이다. 반면 두 구현은 `Feature::kGroupNames`를 고정 반환하며, 구현 주석은 이를 필수라고 설명한다. XML 정의와 구현 주석을 구분해서 읽어야 한다.

### `GroupsClusterImpl` 명령 처리

`InvokeCommand`는 `request.GetAccessingFabricIndex()`로 접근 중인 fabric을 확인한다. 명령 인자를 디코딩하는 경우 이 fabric 값을 전달한다.

#### `AddGroup`

내부 `AddGroup` 함수는 다음 순서로 처리한다.

1. `IsValidGroupId(groupID)`와 이름 길이를 검증한다.
   - 이름 길이 상한은 `GroupDataProvider::GroupInfo::kGroupNameMax`이다.
   - 검증 실패 시 `Status::ConstraintError`를 반환한다.
2. `KeyExists`로 해당 그룹에 연결된 키 세트가 존재하는지 확인한다.
   - `IterateGroupKeys`로 순회하며 `GetKeySet` 성공 여부를 확인한다.
   - 키를 확인할 수 없으면 `Status::UnsupportedAccess`를 반환한다.
3. `GetGroupInfo`로 기존 정보를 조회한다.
   - 기존 그룹이면 `SetName`으로 이름만 갱신하여 `HasAuxiliaryAcl` 등 다른 정보를 보존한다.
   - `CHIP_ERROR_NOT_FOUND`이면 새 `GroupInfo`를 구성한다.
   - 그 밖의 오류는 `Status::Failure`로 처리한다.
4. `SetGroupInfo`와 `AddEndpoint`를 수행한다.
   - 실패 시 `Status::ResourceExhausted`를 반환한다.
   - `AddEndpoint` 실패 시 `RemoveGroupInfo`로 최선 노력의 되돌리기를 수행한다.
5. 그룹 테이블 변경 및 필요한 보조 접근 제어 알림을 처리하고 `Status::Success`를 반환한다.

명령 응답은 요청의 `groupID`와 처리 결과를 담은 `AddGroupResponse`이다.

#### `ViewGroup`

- 유효하지 않은 그룹 ID: `Status::ConstraintError`
- `HasEndpoint` 실패 또는 `GetGroupInfo` 오류: `Status::NotFound`
- 정상 조회: `Status::Success`

`ViewGroupResponse`에 상태, 그룹 ID, 이름을 담는다. 실패한 경우 이름은 빈 문자열로 설정한다.

#### `GetGroupMembership`

- `IterateEndpoints(fabricIndex)`가 실패하면 `Status::Failure`를 반환한다.
- 현재 엔드포인트에 해당하는 그룹만 응답한다.
- 요청의 `GroupList`가 비어 있으면 모든 소속 그룹을 반환한다.
- 요청의 `GroupList`가 비어 있지 않으면 요청 목록에도 포함된 소속 그룹만 반환한다.
- `GroupMembershipResponse::Encode`는 `Capacity`를 null로 인코딩한다. 이는 추가 그룹을 수용할 수 있는지 알 수 없음을 나타낸다.

#### `RemoveGroup`

- 그룹 ID를 검증하고 현재 엔드포인트의 멤버십을 확인한다.
- 유효하지 않은 ID는 `Status::ConstraintError`, 멤버십 부재 또는 `RemoveEndpoint` 실패는 `Status::NotFound`로 처리한다.
- 제거 성공 후 `mScenesIntegration`이 있으면 `GroupWillBeRemoved`를 호출한다.
- 그룹 테이블 변경을 알리고 `Status::Success`를 담은 `RemoveGroupResponse`를 반환한다.
- 필요한 경우 보조 접근 제어 변경 이벤트를 발생시킨다.

#### `RemoveAllGroups`

- scenes 연동이 있으면 현재 엔드포인트의 각 그룹 및 `scenes::kGlobalSceneGroupId`에 대해 `GroupWillBeRemoved`를 호출한다.
- scenes 처리를 위한 `IterateEndpoints` 실패 시 `Status::Failure`를 반환한다.
- `RemoveEndpoint(fabricIndex, mPath.mEndpointId)`로 해당 엔드포인트의 그룹 연결을 제거한다.
- 제거 오류는 로그에 기록하며, 이후 그룹 테이블 변경 및 필요한 보조 접근 제어 알림을 처리하고 `Status::Success`를 반환한다.

#### `AddGroupIfIdentifying`

- `mIdentifyIntegration`이 없거나 `IsIdentifying()`이 거짓이면 그룹을 추가하지 않고 `Status::Success`를 반환한다.
- 식별 중이면 내부 `AddGroup`을 호출한다.
- `AddGroupResponse` 구조체 대신 상태를 직접 반환한다.

지원하지 않는 명령 ID에는 `Status::UnsupportedCommand`를 반환한다.

### `StubbedGroupsCluster` 명령 처리

호환성 전용 구현은 명령 목록을 유지하지만, 그룹 추가 및 조회 명령의 실행은 제한한다.

| 명령 | 처리 |
|---|---|
| `AddGroup` | 인자 디코딩 없이 `Status::InvalidInState` 반환 |
| `ViewGroup` | 인자 디코딩 없이 `Status::InvalidInState` 반환 |
| `GetGroupMembership` | 인자 디코딩 없이 `Status::InvalidInState` 반환 |
| `AddGroupIfIdentifying` | 인자 디코딩 없이 `Status::InvalidInState` 반환 |
| `RemoveGroup` | ID 및 멤버십 검증 후 `RemoveEndpoint` 수행, `RemoveGroupResponse` 반환 |
| `RemoveAllGroups` | 엔드포인트의 그룹 연결 제거, 오류는 로그에 기록하고 `Status::Success` 반환 |
| 그 외 | `Status::UnsupportedCommand` 반환 |

`RemoveGroup`의 상태는 전체 구현과 마찬가지로 검증 실패 시 `Status::ConstraintError`, 멤버십 부재 또는 제거 실패 시 `Status::NotFound`, 성공 시 `Status::Success`이다.

이 구현에는 scenes 연동과 `NotifyGroupTableChanged` 호출이 없다. `RemoveGroup` 및 `RemoveAllGroups`에서는 필요한 경우 보조 접근 제어 변경 이벤트를 발생시킨다.

### 변경 알림

전체 구현의 `NotifyGroupTableChanged`는 `context`가 있을 때 다음 속성에 대해 `DataModel::AttributeChangeType::kReportable` 알림을 전달한다.

- 엔드포인트: `kRootEndpointId`
- 클러스터: `GroupKeyManagement::Id`
- 속성: `GroupKeyManagement::Attributes::GroupTable::Id`

두 구현은 관련 변경 후 `ConsumeAuxAclNotificationNeeded()`가 참이면 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출한다. 전체 구현의 호출 지점은 `AddGroup`, `RemoveGroup`, `RemoveAllGroups`이며, 호환성 전용 구현의 호출 지점은 `RemoveGroup`, `RemoveAllGroups`이다.

## 관련 페이지

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
