---
entity: Groups
ids: ['0x0004']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml', 'src/app/clusters/groups-server/GroupsClusterImpl.cpp', 'src/app/clusters/groups-server/StubbedGroupsCluster.h', 'src/app/clusters/groups-server/GroupsCluster.h', 'src/app/clusters/groups-server/CodegenIntegration.cpp', 'src/app/clusters/groups-server/GroupsClusterImpl.h', 'src/app/clusters/groups-server/StubbedGroupsCluster.cpp', 'src/app/clusters/groups-server/GroupsClusterContext.h', 'data_model/1.7/clusters/Groups.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

`Groups`는 그룹 구성 및 그룹 멤버십 조작을 위한 클러스터입니다.

- 클러스터 ID: `0x0004`
- 도메인: `General`
- 역할: `utility`
- 범위: `Endpoint`
- 현재 스펙 revision: `5`
- `revision 5`에서 `Groupcast`를 우선하는 `Groups` 클러스터의 deprecation이 시작되었습니다.
- SDK 구현은 `GroupsClusterImpl`과 revision `5` 이상을 위한 호환 전용 `StubbedGroupsCluster`로 나뉩니다.
- 빌드 설정에 따라 `GroupsCluster` alias가 사용할 구현이 선택됩니다.

## 스펙

### 기능

| bit | code | name | 설명 | 적합성 |
|---:|---|---|---|---|
| `0` | `GN` | `GroupNames` | 그룹에 이름을 저장하는 기능 | optional |

### 데이터 타입

#### `NameSupportBitmap`

| bit | name | 설명 | 적합성 |
|---:|---|---|---|
| `7` | `GroupNames` | 그룹에 이름을 저장하는 기능 | mandatory |

### 속성

#### `NameSupport`

| ID | 타입 | 접근 | 품질 | 적합성 |
|---|---|---|---|---|
| `0x0000` | `NameSupportBitmap` | read, `view` | `persistence="fixed"` | mandatory |

### 명령

#### 서버로 보내는 명령

| ID | 명령 | 응답 | 접근 | 필드 |
|---|---|---|---|---|
| `0x00` | `AddGroup` | `AddGroupResponse` | `manage`, fabric-scoped | `GroupID`, `GroupName` |
| `0x01` | `ViewGroup` | `ViewGroupResponse` | `operate`, fabric-scoped | `GroupID` |
| `0x02` | `GetGroupMembership` | `GetGroupMembershipResponse` | `operate`, fabric-scoped | `GroupList` |
| `0x03` | `RemoveGroup` | `RemoveGroupResponse` | `manage`, fabric-scoped | `GroupID` |
| `0x04` | `RemoveAllGroups` | `Y` | `manage`, fabric-scoped | 없음 |
| `0x05` | `AddGroupIfIdentifying` | `Y` | `manage`, fabric-scoped | `GroupID`, `GroupName` |

#### `AddGroup`

- `GroupID`
  - field ID: `0`
  - 타입: `group-id`
  - 최솟값: `1`
- `GroupName`
  - field ID: `1`
  - 타입: `string`
  - 최대 길이: `16`

#### `ViewGroup`

- `GroupID`
  - field ID: `0`
  - 타입: `group-id`
  - 최솟값: `1`

#### `GetGroupMembership`

- `GroupList`
  - field ID: `0`
  - 타입: `list`
  - 항목 타입: `group-id`
  - 항목 최솟값: `1`

#### `RemoveGroup`

- `GroupID`
  - field ID: `0`
  - 타입: `group-id`
  - 최솟값: `1`

#### `AddGroupIfIdentifying`

- `GroupID`
  - field ID: `0`
  - 타입: `group-id`
  - 최솟값: `1`
- `GroupName`
  - field ID: `1`
  - 타입: `string`
  - 최대 길이: `16`

### 서버 응답 명령

#### `AddGroupResponse`

| ID | 필드 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | - |
| `1` | `GroupID` | `group-id` | 최솟값 `1` |

#### `ViewGroupResponse`

| ID | 필드 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | - |
| `1` | `GroupID` | `group-id` | 최솟값 `1` |
| `2` | `GroupName` | `string` | 최대 길이 `16` |

#### `GetGroupMembershipResponse`

| ID | 필드 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Capacity` | `uint8` | nullable |
| `1` | `GroupList` | `list` | 항목 타입 `group-id`, 최솟값 `1` |

#### `RemoveGroupResponse`

| ID | 필드 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | - |
| `1` | `GroupID` | `group-id` | 최솟값 `1` |

### revision 이력

| revision | 내용 |
|---:|---|
| `1` | 필수 global `ClusterRevision` 속성 추가 |
| `2` | `CCB 2289` |
| `3` | `CCB 2310 2704` |
| `4` | 새로운 data model 형식 및 표기 |
| `5` | `Groupcast`를 대신하는 `Groups` 클러스터 deprecation 시작 |

## SDK 정의

### 생성 데이터 모델

파일: `src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml`

- 클러스터 이름: `Groups`
- 클러스터 코드: `0x0004`
- 도메인: `General`
- define: `GROUPS_CLUSTER`
- 클라이언트: 활성화
- 서버: 활성화
- global attribute:
  - ID: `0xFFFD`
  - value: `5`

### SDK 기능 및 속성

- 기능:
  - `GroupNames`
  - bit: `0`
  - code: `GN`
- bitmap:
  - `NameSupportBitmap`
  - 타입: `bitmap8`
  - `GroupNames` mask: `0x80`
- 속성:
  - `NameSupport`
  - code: `0x0000`
  - define: `GROUP_NAME_SUPPORT`
  - 타입: `NameSupportBitmap`
  - max: `0x80`

SDK 데이터 모델에는 다음 명령과 응답이 정의되어 있습니다.

- `AddGroup` (`0x00`) → `AddGroupResponse`
- `ViewGroup` (`0x01`) → `ViewGroupResponse`
- `GetGroupMembership` (`0x02`) → `GetGroupMembershipResponse`
- `RemoveGroup` (`0x03`) → `RemoveGroupResponse`
- `RemoveAllGroups` (`0x04`)
- `AddGroupIfIdentifying` (`0x05`)
- `AddGroupResponse` (`0x00`)
- `ViewGroupResponse` (`0x01`)
- `GetGroupMembershipResponse` (`0x02`)
- `RemoveGroupResponse` (`0x03`)

CLI 정의:

| 명령 | CLI |
|---|---|
| `AddGroup` | `zcl groups add` |
| `ViewGroup` | `zcl groups view` |
| `GetGroupMembership` | `zcl groups get` |
| `RemoveGroup` | `zcl groups remove` |
| `RemoveAllGroups` | `zcl groups rmall` |
| `AddGroupIfIdentifying` | `zcl groups add-if-id` |

`GetGroupMembership`의 codegen 함수 이름은 `zclGroupsGetCommand`입니다.

## 구현

### 구현 파일

- `src/app/clusters/groups-server/GroupsClusterImpl.h`
- `src/app/clusters/groups-server/GroupsClusterImpl.cpp`
- `src/app/clusters/groups-server/StubbedGroupsCluster.h`
- `src/app/clusters/groups-server/StubbedGroupsCluster.cpp`
- `src/app/clusters/groups-server/GroupsCluster.h`
- `src/app/clusters/groups-server/GroupsClusterContext.h`
- `src/app/clusters/groups-server/CodegenIntegration.cpp`

### `GroupsClusterImpl`

`GroupsClusterImpl`은 그룹 멤버십을 클러스터 명령으로 관리하는 전체 구현입니다.

주요 인터페이스:

- `Attributes`
- `AcceptedCommands`
- `GeneratedCommands`
- `ReadAttribute`
- `InvokeCommand`

내부 상태:

- `Credentials::GroupDataProvider & mGroupDataProvider`
- `scenes::ScenesIntegrationDelegate * mScenesIntegration`
- `IdentifyIntegrationDelegate * mIdentifyIntegration`

생성 시 `GroupsClusterContext`에서 다음을 전달받습니다.

- `groupDataProvider`
- `scenesIntegration`
- `identifyIntegration`

#### 속성 처리

`ReadAttribute`는 다음 속성을 처리합니다.

- `ClusterRevision`
  - legacy full command support를 위해 revision `4`를 반환합니다.
  - revision `5+`에서는 `Groupcast`를 선호하며 `Groups`는 backwards compatibility를 위한 stubbed implementation으로 취급됩니다.
- `FeatureMap`
  - `Feature::kGroupNames`를 반환합니다.
- `NameSupport`
  - `NameSupportBitmap::kGroupNames`를 반환합니다.
- 그 외 속성
  - `Status::UnsupportedAttribute`

#### 허용 및 생성 명령

`AcceptedCommands`는 다음 명령을 등록합니다.

- `AddGroup`
- `ViewGroup`
- `GetGroupMembership`
- `RemoveGroup`
- `RemoveAllGroups`
- `AddGroupIfIdentifying`

`GeneratedCommands`는 다음 응답을 등록합니다.

- `AddGroupResponse`
- `ViewGroupResponse`
- `GetGroupMembershipResponse`
- `RemoveGroupResponse`

#### `AddGroup`

`AddGroup`은 다음을 수행합니다.

1. `GroupID`가 유효한지 확인합니다.
2. `GroupName` 길이가 `GroupDataProvider::GroupInfo::kGroupNameMax` 이하인지 확인합니다.
3. `KeyExists`를 통해 해당 `GroupID`에 연결된 키가 존재하는지 확인합니다.
4. 기존 `GroupInfo`가 있으면 이름을 갱신하고, 없으면 새 `GroupInfo`를 생성합니다.
5. `mGroupDataProvider.SetGroupInfo`로 그룹 정보를 저장합니다.
6. `mGroupDataProvider.AddEndpoint`로 현재 endpoint를 그룹에 추가합니다.
7. `NotifyGroupTableChanged`를 호출합니다.
8. 필요한 경우 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출합니다.

실패 시 다음 `Status`가 사용됩니다.

- `Status::ConstraintError`
- `Status::UnsupportedAccess`
- `Status::Failure`
- `Status::ResourceExhausted`
- `Status::Success`

#### `ViewGroup`

`ViewGroup`은 다음 조건을 확인합니다.

- `IsValidGroupId`
- `mGroupDataProvider.HasEndpoint`
- `mGroupDataProvider.GetGroupInfo`

성공하면 `ViewGroupResponse::Type`에 다음을 담아 응답합니다.

- `status`
- `groupID`
- `groupName`

그룹을 찾지 못하면 `Status::NotFound`를 반환하고 `groupName`은 빈 문자열로 처리합니다.

#### `GetGroupMembership`

`GetGroupMembership`은 `mGroupDataProvider.IterateEndpoints`로 endpoint의 그룹 매핑을 순회합니다.

`GroupMembershipResponse::Encode`는 다음 규칙을 사용합니다.

- `GroupList`가 비어 있으면 해당 endpoint가 속한 모든 그룹 ID를 반환합니다.
- `GroupList`가 비어 있지 않으면 요청 목록에 포함된 그룹 ID만 반환합니다.
- `Capacity`는 `kCapacityUnknown`으로 인코딩됩니다.
- `GroupMembershipResponse::GetCommandId()`는 `Commands::GetGroupMembershipResponse::Id`를 반환합니다.
- `GroupMembershipResponse::GetClusterId()`는 `Groups::Id`를 반환합니다.

#### `RemoveGroup`

`RemoveGroup`은 다음을 수행합니다.

1. `IsValidGroupId`로 `GroupID`를 확인합니다.
2. `mGroupDataProvider.HasEndpoint`로 현재 endpoint의 멤버십을 확인합니다.
3. `mGroupDataProvider.RemoveEndpoint`로 멤버십을 제거합니다.
4. `mScenesIntegration`이 있으면 `GroupWillBeRemoved`를 호출합니다.
5. `NotifyGroupTableChanged`를 호출합니다.
6. 필요한 경우 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출합니다.

응답은 `RemoveGroupResponse::Type`으로 생성되며 `status`와 `groupID`를 포함합니다.

#### `RemoveAllGroups`

`RemoveAllGroups`는 현재 fabric과 endpoint에 대한 모든 그룹 매핑을 제거합니다.

- `mScenesIntegration`이 있으면 관련 그룹에 대해 `GroupWillBeRemoved`를 호출합니다.
- `scenes::kGlobalSceneGroupId`에도 `GroupWillBeRemoved`를 호출합니다.
- `mGroupDataProvider.RemoveEndpoint`를 호출합니다.
- `NotifyGroupTableChanged`를 호출합니다.
- 필요한 경우 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출합니다.

#### `AddGroupIfIdentifying`

`AddGroupIfIdentifying`는 endpoint가 identifying 중일 때만 `AddGroup`을 수행합니다.

- `mIdentifyIntegration`이 없거나 `IsIdentifying()`이 false이면 `Status::Success`로 종료합니다.
- identifying 중이면 `AddGroup`을 호출합니다.
- 이 명령은 스펙에서 response `Y`이므로 구조체 응답 대신 status를 반환합니다.

### `StubbedGroupsCluster`

`StubbedGroupsCluster`는 revision `5` 이상에서 사용하는 호환 전용 구현입니다.

```cpp
static_assert(Groups::kRevision >= 5, ...);
```

`Groupcast`가 그룹 멤버십을 소유하므로 그룹을 추가하거나 조회하는 명령은 `Status::InvalidInState`를 반환합니다.

`Status::InvalidInState`를 반환하는 명령:

- `AddGroup`
- `ViewGroup`
- `GetGroupMembership`
- `AddGroupIfIdentifying`

다음 명령은 계속 처리됩니다.

#### `RemoveGroup`

- `GroupID`를 디코딩합니다.
- `IsValidGroupId`를 확인합니다.
- `mGroupDataProvider.HasEndpoint`를 확인합니다.
- `mGroupDataProvider.RemoveEndpoint`로 현재 endpoint의 그룹 멤버십을 제거합니다.
- `RemoveGroupResponse::Type`을 생성합니다.
- 필요한 경우 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출합니다.

#### `RemoveAllGroups`

- `mGroupDataProvider.RemoveEndpoint`를 호출해 현재 endpoint의 모든 그룹 멤버십을 제거합니다.
- 오류가 발생해도 로그를 기록한 뒤 `Status::Success`를 반환합니다.
- 필요한 경우 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출합니다.

### `GroupsCluster` alias 선택

파일: `src/app/clusters/groups-server/GroupsCluster.h`

빌드 설정 `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER`에 따라 alias가 선택됩니다.

```cpp
#if CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER
using GroupsCluster = StubbedGroupsCluster;
#else
using GroupsCluster = GroupsClusterImpl;
#endif
```

- `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER`가 활성화되면 `StubbedGroupsCluster`
- 그렇지 않으면 `GroupsClusterImpl`

두 구현 모두 `GroupsCluster::Context` 형태로 생성할 수 있으므로 호출자는 실제 구현 클래스를 직접 알 필요가 없습니다.

### `GroupsClusterContext`

`GroupsClusterContext`는 두 구현에 공통으로 사용되는 생성 인자입니다.

```cpp
struct GroupsClusterContext
{
    Credentials::GroupDataProvider & groupDataProvider;
    scenes::ScenesIntegrationDelegate * scenesIntegration = nullptr;
    IdentifyIntegrationDelegate * identifyIntegration     = nullptr;
};
```

- `StubbedGroupsCluster`는 `groupDataProvider`만 사용합니다.
- `GroupsClusterImpl`은 `groupDataProvider`, `scenesIntegration`, `identifyIntegration`을 사용합니다.
- `scenesIntegration`이 `nullptr`이면 scenes 지원이 없습니다.
- `identifyIntegration`이 `nullptr`이면 identify 지원이 없습니다.

### Codegen 통합

파일: `src/app/clusters/groups-server/CodegenIntegration.cpp`

주요 구성:

- `kGroupsFixedClusterCount`
- `kGroupsMaxClusterCount`
- `LazyRegisteredServerCluster<GroupsCluster> gServers`
- `IntegrationDelegate`
- `MatterGroupsClusterInitCallback`
- `MatterGroupsClusterShutdownCallback`
- `MatterGroupsPluginServerInitCallback`
- `MatterGroupsPluginServerShutdownCallback`

`IntegrationDelegate::CreateRegistration`은 다음을 수행합니다.

1. `Credentials::GetGroupDataProvider()`로 `GroupDataProvider`를 가져옵니다.
2. 선택된 `GroupsCluster`를 endpoint에 생성합니다.
3. `GroupsCluster::Context`를 전달합니다.
4. 선택적으로 `ScenesManagement::FindClusterOnEndpoint`와 `FindIdentifyClusterOnEndpoint`를 연결합니다.

등록 시 사용되는 클러스터 ID는 `Groups::Id`입니다.

## 관련 문서