---
entity: Groups
ids: ['0x0004']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml', 'src/app/clusters/groups-server/GroupsClusterImpl.cpp', 'src/app/clusters/groups-server/StubbedGroupsCluster.h', 'src/app/clusters/groups-server/GroupsCluster.h', 'src/app/clusters/groups-server/CodegenIntegration.cpp', 'src/app/clusters/groups-server/GroupsClusterImpl.h', 'src/app/clusters/groups-server/StubbedGroupsCluster.cpp', 'src/app/clusters/groups-server/GroupsClusterContext.h', 'data_model/1.7/clusters/Groups.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Groups

## 개요

`Groups`는 서버 엔드포인트의 그룹 구성과 멤버십 관리를 위한 속성 및 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0004` |
| 도메인 | `General` |
| 스펙 revision | `5` |
| 분류 | hierarchy=`base`, role=`utility` |
| 범위 | `Endpoint` |
| PICS 코드 | `G` |

revision `5`부터 `Groupcast`로 대체하기 위한 사용 중단 절차가 시작되었다. 구현은 전체 명령을 지원하는 `GroupsClusterImpl`과 호환성 전용 `StubbedGroupsCluster`로 나뉘며, 애플리케이션에서는 `GroupsCluster` 별칭을 사용한다.

## 스펙

출처: `data_model/1.7/clusters/Groups.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가; CCB 1745 2100 |
| `2` | CCB 2289 |
| `3` | CCB 2310 2704 |
| `4` | 새로운 데이터 모델 형식 및 표기법 |
| `5` | `Groupcast`로 대체하기 위한 `Groups` 사용 중단 절차 시작 |

### 기능 및 데이터 타입

| 구분 | 이름 | 위치 | 적합성 | 설명 |
|---|---|---|---|---|
| 기능 | `GroupNames` | bit `0`, code `GN` | 선택 | 그룹 이름 저장 기능 |
| `NameSupportBitmap` 비트 | `GroupNames` | bit `7` | 필수 | 그룹 이름 저장 지원 표시 |

### 속성

| ID | 이름 | 타입 | 접근 | 영속성 | 적합성 |
|---|---|---|---|---|---|
| `0x0000` | `NameSupport` | `NameSupportBitmap` | 읽기, `view` | `fixed` | 필수 |

### 요청 명령

모든 요청 명령은 `commandToServer` 방향이며, 필수이고 `fabricScoped="true"`이다. 아래 필드도 모두 필수이다.

| ID | 명령 | 호출 권한 | 필드: ID / 이름 / 타입 및 제약 | 응답 |
|---|---|---|---|---|
| `0x00` | `AddGroup` | `manage` | `0`: `GroupID`, `group-id`, 최소 `1`<br>`1`: `GroupName`, `string`, 최대 길이 `16` | `AddGroupResponse` |
| `0x01` | `ViewGroup` | `operate` | `0`: `GroupID`, `group-id`, 최소 `1` | `ViewGroupResponse` |
| `0x02` | `GetGroupMembership` | `operate` | `0`: `GroupList`, `list`, 항목 타입 `group-id`, 항목 최소 `1` | `GetGroupMembershipResponse` |
| `0x03` | `RemoveGroup` | `manage` | `0`: `GroupID`, `group-id`, 최소 `1` | `RemoveGroupResponse` |
| `0x04` | `RemoveAllGroups` | `manage` | 없음 | `Y` |
| `0x05` | `AddGroupIfIdentifying` | `manage` | `0`: `GroupID`, `group-id`, 최소 `1`<br>`1`: `GroupName`, `string`, 최대 길이 `16` | `Y` |

### 응답 명령

모든 응답 명령은 `responseFromServer` 방향이며, 명령과 필드 모두 필수이다.

| ID | 명령 | 필드: ID / 이름 / 타입 및 제약 |
|---|---|---|
| `0x00` | `AddGroupResponse` | `0`: `Status`, `enum8`<br>`1`: `GroupID`, `group-id`, 최소 `1` |
| `0x01` | `ViewGroupResponse` | `0`: `Status`, `enum8`<br>`1`: `GroupID`, `group-id`, 최소 `1`<br>`2`: `GroupName`, `string`, 최대 길이 `16` |
| `0x02` | `GetGroupMembershipResponse` | `0`: `Capacity`, `uint8`, nullable<br>`1`: `GroupList`, `list`, 항목 타입 `group-id`, 항목 최소 `1` |
| `0x03` | `RemoveGroupResponse` | `0`: `Status`, `enum8`<br>`1`: `GroupID`, `group-id`, 최소 `1` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml`

이 파일은 `src/app_clusters/Groups.adoc`에서 Alchemy로 생성되었으며, 직접 편집하지 않도록 표시되어 있다.

### 클러스터 및 속성 정의

| 항목 | SDK 정의 |
|---|---|
| 이름 / 코드 | `Groups` / `0x0004` |
| define | `GROUPS_CLUSTER` |
| 클라이언트 및 서버 | 모두 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | `0xFFFD`, `side="either"`, 값 `5` |
| 기능 | `GroupNames`, bit `0`, code `GN`, `optionalConform` |
| 비트맵 | `NameSupportBitmap`, 타입 `bitmap8` |
| 비트맵 필드 | `GroupNames`, mask `0x80` |
| 서버 속성 | `NameSupport`, `0x0000`, define `GROUP_NAME_SUPPORT`, 타입 `NameSupportBitmap`, max `0x80` |

### 명령 정의

SDK는 스펙과 동일한 요청 명령 6개와 응답 명령 4개를 정의한다. 모든 명령은 `mandatoryConform`이고, 모든 요청은 `isFabricScoped="true"`이다.

| 스펙 타입 | SDK 타입 |
|---|---|
| `group-id` | `group_id` |
| `string` | `char_string` |
| `uint8` | `int8u` |
| `list`의 `group-id` 항목 | `group_id`, `array="true"` |

- 개별 `GroupID` 필드는 `min="1"`이다.
- `GroupName`은 `length="16"`이다.
- `Capacity`는 `isNullable="true"`이다.
- SDK의 `GroupList`에는 `array="true"`가 있으며, 스펙의 항목 최소값 제약은 이 XML에 명시되어 있지 않다.
- `AddGroup`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying`은 `invoke` 접근에 `manage` 역할을 명시한다.
- `ViewGroup`, `GetGroupMembership`의 접근 역할은 SDK XML에 별도로 명시되어 있지 않다.
- 응답 명령 4개에는 모두 `disableDefaultResponse="true"`가 설정되어 있다.

### CLI 메타데이터

| 명령 | `cli` |
|---|---|
| `AddGroup` | `zcl groups add` |
| `ViewGroup` | `zcl groups view` |
| `GetGroupMembership` | `zcl groups get` |
| `RemoveGroup` | `zcl groups remove` |
| `RemoveAllGroups` | `zcl groups rmall` |
| `AddGroupIfIdentifying` | `zcl groups add-if-id` |

`GetGroupMembership`의 `cliFunctionName`은 `zclGroupsGetCommand`이다.

## 구현

### 구현 선택 및 공통 컨텍스트

출처:
- `src/app/clusters/groups-server/GroupsCluster.h`
- `src/app/clusters/groups-server/GroupsClusterContext.h`
- `src/app/clusters/groups-server/GroupsClusterImpl.h`
- `src/app/clusters/groups-server/StubbedGroupsCluster.h`

`GroupsCluster`는 `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER`에 따라 선택된다.

| 조건 | `GroupsCluster` 대상 |
|---|---|
| `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER` 활성화 | `StubbedGroupsCluster` |
| 그 외 | `GroupsClusterImpl` |

소스 주석은 `Groupcast`가 활성화된 빌드에서 호환성 전용 구현을 사용한다고 설명한다. 두 클래스 모두 `DefaultServerCluster`를 상속하고 `GroupsClusterContext`를 `Context`로 사용한다.

| `GroupsClusterContext` 멤버 | 타입 | 용도 |
|---|---|---|
| `groupDataProvider` | `Credentials::GroupDataProvider &` | 그룹 데이터 접근 |
| `scenesIntegration` | `scenes::ScenesIntegrationDelegate *` | 장면 연동, 기본값 `nullptr` |
| `identifyIntegration` | `IdentifyIntegrationDelegate *` | 식별 상태 연동, 기본값 `nullptr` |

`StubbedGroupsCluster`는 `groupDataProvider`만 사용한다. `GroupsClusterContext.h`에서는 장면 구현에 대한 링크 의존성을 피하기 위해 `ScenesIntegrationDelegate`를 전방 선언한다.

### 속성 및 명령 목록

출처:
- `src/app/clusters/groups-server/GroupsClusterImpl.cpp`
- `src/app/clusters/groups-server/StubbedGroupsCluster.cpp`

두 구현의 `Attributes`는 `Attributes::kMandatoryMetadata`를 추가한다. `AcceptedCommands`는 요청 명령 6개를, `GeneratedCommands`는 응답 명령 4개를 등록한다.

| 속성 | `GroupsClusterImpl::ReadAttribute` | `StubbedGroupsCluster::ReadAttribute` |
|---|---|---|
| `ClusterRevision` | 전체 명령 지원의 마지막 revision인 `4`를 강제 반환 | `kRevision` 반환 |
| `FeatureMap` | `Feature::kGroupNames` | `Feature::kGroupNames` |
| `NameSupport` | `NameSupportBitmap::kGroupNames` | `NameSupportBitmap::kGroupNames` |
| 그 외 | `Status::UnsupportedAttribute` | `Status::UnsupportedAttribute` |

`StubbedGroupsCluster`는 `static_assert`로 `Groups::kRevision >= 5`를 검사한다.

스펙 및 SDK XML에서 `GroupNames` 기능은 선택 사항이지만, 두 구현은 이를 항상 반환한다. 구현 주석에는 필수 적합성이라고 기재되어 있어, 제공된 XML 정의와 차이가 있다.

### `GroupsClusterImpl` 명령 처리

`InvokeCommand`는 `request.GetAccessingFabricIndex()`로 접근 중인 fabric을 얻고, 대상 엔드포인트로 `mPath.mEndpointId`를 사용한다. 지원하지 않는 명령은 `Status::UnsupportedCommand`를 반환한다.

#### `AddGroup`

`GroupsClusterImpl::AddGroup`의 처리 순서는 다음과 같다.

1. `IsValidGroupId(groupID)`와 `GroupDataProvider::GroupInfo::kGroupNameMax`를 검사한다. 위반 시 `Status::ConstraintError`를 반환한다.
2. `KeyExists`로 해당 fabric의 그룹에 연결된 키 세트가 존재하는지 검사한다. 없으면 `Status::UnsupportedAccess`를 반환한다.
3. `GetGroupInfo`로 기존 정보를 조회한다.
   - 기존 정보가 있으면 `SetName`만 호출하여 `HasAuxiliaryAcl` 같은 기존 플래그를 보존한다.
   - `CHIP_ERROR_NOT_FOUND`이면 새 `GroupInfo`를 만든다.
   - 그 외 오류는 `Status::Failure`로 처리한다.
4. `SetGroupInfo`와 `AddEndpoint`를 호출한다.
   - 실패하면 `Status::ResourceExhausted`를 반환한다.
   - `AddEndpoint` 실패 시 `RemoveGroupInfo`로 최선형 복구를 시도한다.
5. `NotifyGroupTableChanged`와 필요한 보조 접근 제어 알림을 처리하고 `Status::Success`를 반환한다.

`InvokeCommand`는 결과를 `AddGroupResponse`의 `status`와 `groupID`에 담아 응답한다.

`KeyExists`는 `IterateGroupKeys`로 그룹 키를 순회하고, 일치하는 `group_id`에 대해 `GetKeySet`이 성공하면 `true`를 반환한다.

#### `ViewGroup`

- 잘못된 그룹 ID는 `Status::ConstraintError`로 처리한다.
- `HasEndpoint`가 거짓이거나 `GetGroupInfo`가 실패하면 `Status::NotFound`로 처리한다.
- 성공하면 저장된 이름을 `ViewGroupResponse`로 반환한다.
- 실패 응답에서는 이름을 빈 문자열로 설정한다.

#### `GetGroupMembership`

- `IterateEndpoints` 실패 시 `Status::Failure`를 반환한다.
- `GroupMembershipResponse::Encode`는 대상 엔드포인트의 매핑만 인코딩한다.
- 요청 `GroupList`가 비어 있으면 모든 소속 그룹을 반환한다.
- 요청 `GroupList`가 비어 있지 않으면 해당 목록에 포함된 소속 그룹만 반환한다.
- `Capacity`는 `kCapacityUnknown`으로 인코딩되며 null이다. 이는 추가 그룹을 등록할 수 있는지 알 수 없음을 의미한다.

#### `RemoveGroup`

- 그룹 ID가 유효하지 않으면 `Status::ConstraintError`를 반환한다.
- 엔드포인트 매핑이 없거나 `RemoveEndpoint`가 실패하면 `Status::NotFound`를 반환한다.
- 삭제 성공 후 `mScenesIntegration`이 있으면 `GroupWillBeRemoved`를 호출한다. 이 호출의 실패는 로그로 남긴다.
- `NotifyGroupTableChanged`를 호출하고 `RemoveGroupResponse`로 `Status::Success`를 응답한다.
- 필요한 경우 보조 접근 제어 알림을 발생시킨다.

#### `RemoveAllGroups`

- `mScenesIntegration`이 있으면 대상 엔드포인트의 각 그룹에 대해 `GroupWillBeRemoved`를 호출한다.
- `scenes::kGlobalSceneGroupId`에 대해서도 `GroupWillBeRemoved`를 호출한다.
- 장면 연동을 위한 `IterateEndpoints`가 실패하면 `Status::Failure`를 반환한다.
- `RemoveEndpoint(fabricIndex, mPath.mEndpointId)`로 모든 매핑을 삭제한다. 삭제 오류는 로그로 남기며, 이후 `Status::Success`를 반환한다.
- `NotifyGroupTableChanged`와 필요한 보조 접근 제어 알림을 처리한다.

#### `AddGroupIfIdentifying`

- 요청을 디코딩한 뒤 `mIdentifyIntegration`과 `IsIdentifying()`을 확인한다.
- 식별 연동이 없거나 식별 중이 아니면 그룹을 추가하지 않고 `Status::Success`를 반환한다.
- 식별 중이면 `AddGroup`을 호출한다.
- `AddGroupResponse` 구조체가 아니라 처리 상태를 반환한다.

### 변경 알림

`NotifyGroupTableChanged`는 컨텍스트가 있을 때 다음 경로에 `DataModel::AttributeChangeType::kReportable` 변경 알림을 전달한다.

- 엔드포인트: `kRootEndpointId`
- 클러스터: `GroupKeyManagement::Id`
- 속성: `GroupKeyManagement::Attributes::GroupTable::Id`

추가 또는 삭제 처리에서 `ConsumeAuxAclNotificationNeeded()`가 참이면 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출한다.

### `StubbedGroupsCluster` 명령 처리

revision `5` 이상을 위한 호환성 구현이며, 그룹 추가 및 조회 명령은 실패한다.

| 명령 | 처리 |
|---|---|
| `AddGroup` | 즉시 `Status::InvalidInState` 반환 |
| `ViewGroup` | 즉시 `Status::InvalidInState` 반환 |
| `GetGroupMembership` | 즉시 `Status::InvalidInState` 반환 |
| `AddGroupIfIdentifying` | 즉시 `Status::InvalidInState` 반환 |
| `RemoveGroup` | 요청 디코딩, 그룹 ID 및 매핑 확인, 매핑 삭제 후 `RemoveGroupResponse` 생성 |
| `RemoveAllGroups` | 대상 엔드포인트의 모든 매핑 삭제 시도 후 `Status::Success` 반환 |
| 그 외 | `Status::UnsupportedCommand` 반환 |

`RemoveGroup`은 유효하지 않은 ID에 `Status::ConstraintError`, 매핑 부재나 삭제 실패에 `Status::NotFound`, 성공에 `Status::Success`를 사용한다.

`RemoveAllGroups`는 삭제 실패를 로그로 남기지만 반환 상태는 `Status::Success`이다. 두 삭제 명령은 필요한 경우 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출한다.

제공된 `StubbedGroupsCluster.cpp`에는 장면 연동이나 `NotifyGroupTableChanged` 호출이 없다.

### 코드 생성 통합 및 수명 주기

출처: `src/app/clusters/groups-server/CodegenIntegration.cpp`

- `kGroupsFixedClusterCount`는 `Groups::StaticApplicationConfig::kFixedClusterConfig.size()`이다.
- `kGroupsMaxClusterCount`는 고정 인스턴스 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `gServers`는 `LazyRegisteredServerCluster<GroupsCluster>` 배열이다.

`IntegrationDelegate`의 역할은 다음과 같다.

| 함수 | 처리 |
|---|---|
| `CreateRegistration` | `Credentials::GetGroupDataProvider()`를 얻고 `VerifyOrDie`로 확인한 뒤 인스턴스 생성 |
| `FindRegistration` | 생성된 인스턴스의 인터페이스 반환, 미생성 시 `nullptr` |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy` 호출 |

조건부 연동은 다음과 같다.

- `MATTER_DM_PLUGIN_SCENES_MANAGEMENT`: `ScenesManagement::FindClusterOnEndpoint(endpointId)`로 `scenesIntegration` 설정
- `ZCL_USING_IDENTIFY_CLUSTER_SERVER`: `FindIdentifyClusterOnEndpoint(endpointId)`로 `identifyIntegration` 설정

`MatterGroupsClusterInitCallback`은 `CodegenClusterIntegration::RegisterServer`를 호출하며, `fetchFeatureMap`과 `fetchOptionalAttributes`를 모두 `false`로 설정한다.

`MatterGroupsClusterShutdownCallback`은 `CodegenClusterIntegration::UnregisterServer`를 호출한다. `MatterGroupsPluginServerInitCallback`과 `MatterGroupsPluginServerShutdownCallback`의 본문은 비어 있다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
