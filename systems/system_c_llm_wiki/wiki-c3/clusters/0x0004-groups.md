---
entity: Groups
ids: ['0x0004']
source_paths: ['data_model/1.7/clusters/Groups.xml', 'src/app/clusters/groups-server/CodegenIntegration.cpp', 'src/app/clusters/groups-server/GroupsCluster.h', 'src/app/clusters/groups-server/GroupsClusterContext.h', 'src/app/clusters/groups-server/GroupsClusterImpl.cpp', 'src/app/clusters/groups-server/GroupsClusterImpl.h', 'src/app/clusters/groups-server/StubbedGroupsCluster.cpp', 'src/app/clusters/groups-server/StubbedGroupsCluster.h', 'src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Groups

## 개요

`Groups`는 서버 Endpoint의 그룹 구성과 멤버십 관리를 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Groups` |
| 스펙 이름 | `Groups Cluster` |
| 클러스터 ID | `0x0004` |
| 제공된 스펙 revision | `5` |
| 분류 | hierarchy: `base`, role: `utility` |
| 범위 | `Endpoint` |
| PICS 코드 | `G` |

revision `5`부터 `Groupcast`로의 전환을 위해 `Groups`의 사용 중단 절차가 시작된다. 제공된 구현은 빌드 설정에 따라 전체 명령을 지원하는 `GroupsClusterImpl` 또는 호환성 전용 `StubbedGroupsCluster`를 선택한다.

## 스펙

출처: `data_model/1.7/clusters/Groups.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가; CCB 1745 2100 |
| `2` | CCB 2289 |
| `3` | CCB 2310 2704 |
| `4` | 새로운 데이터 모델 형식과 표기법 도입 |
| `5` | `Groupcast`를 대안으로 `Groups` 사용 중단 절차 시작 |

### 기능과 데이터 타입

| 기능 | 코드 | 비트 | 적합성 | 설명 |
|---|---|---|---|---|
| `GroupNames` | `GN` | `0` | 선택 | 그룹 이름 저장 기능 |

`NameSupportBitmap`은 다음 비트 필드를 정의한다.

| 필드 | 비트 | 적합성 | 설명 |
|---|---|---|---|
| `GroupNames` | `7` | 필수 | 그룹 이름 저장 기능 |

기능의 `GroupNames` 비트와 `NameSupportBitmap`의 `GroupNames` 비트는 위치가 서로 다르다.

### 속성

| ID | 이름 | 타입 | 접근 | 영속성 | 적합성 |
|---|---|---|---|---|---|
| `0x0000` | `NameSupport` | `NameSupportBitmap` | 읽기, `view` | `fixed` | 필수 |

### 서버 수신 명령

아래 명령은 모두 `commandToServer` 방향이며 필수이다. 모두 `fabricScoped="true"`로 정의된다.

| ID | 명령 | 호출 권한 | 응답 |
|---|---|---|---|
| `0x00` | `AddGroup` | `manage` | `AddGroupResponse` |
| `0x01` | `ViewGroup` | `operate` | `ViewGroupResponse` |
| `0x02` | `GetGroupMembership` | `operate` | `GetGroupMembershipResponse` |
| `0x03` | `RemoveGroup` | `manage` | `RemoveGroupResponse` |
| `0x04` | `RemoveAllGroups` | `manage` | `Y` |
| `0x05` | `AddGroupIfIdentifying` | `manage` | `Y` |

#### 요청 필드

아래 필드는 모두 필수이다. `RemoveAllGroups`에는 요청 필드가 없다.

| 명령 | 필드 ID | 이름 | 타입 | 제약 |
|---|---|---|---|---|
| `AddGroup` | `0` | `GroupID` | `group-id` | 최솟값 `1` |
| `AddGroup` | `1` | `GroupName` | `string` | 최대 길이 `16` |
| `ViewGroup` | `0` | `GroupID` | `group-id` | 최솟값 `1` |
| `GetGroupMembership` | `0` | `GroupList` | `list` | 각 항목은 `group-id`, 최솟값 `1` |
| `RemoveGroup` | `0` | `GroupID` | `group-id` | 최솟값 `1` |
| `AddGroupIfIdentifying` | `0` | `GroupID` | `group-id` | 최솟값 `1` |
| `AddGroupIfIdentifying` | `1` | `GroupName` | `string` | 최대 길이 `16` |

### 서버 응답 명령

아래 명령은 모두 `responseFromServer` 방향이며, 명령과 각 필드 모두 필수이다.

| ID | 명령 | 필드 ID | 이름 | 타입 | 제약 |
|---|---|---|---|---|---|
| `0x00` | `AddGroupResponse` | `0` | `Status` | `enum8` | 구체적인 값 제약은 제공된 XML에 없음 |
| `0x00` | `AddGroupResponse` | `1` | `GroupID` | `group-id` | 최솟값 `1` |
| `0x01` | `ViewGroupResponse` | `0` | `Status` | `enum8` | 구체적인 값 제약은 제공된 XML에 없음 |
| `0x01` | `ViewGroupResponse` | `1` | `GroupID` | `group-id` | 최솟값 `1` |
| `0x01` | `ViewGroupResponse` | `2` | `GroupName` | `string` | 최대 길이 `16` |
| `0x02` | `GetGroupMembershipResponse` | `0` | `Capacity` | `uint8` | nullable |
| `0x02` | `GetGroupMembershipResponse` | `1` | `GroupList` | `list` | 각 항목은 `group-id`, 최솟값 `1` |
| `0x03` | `RemoveGroupResponse` | `0` | `Status` | `enum8` | 구체적인 값 제약은 제공된 XML에 없음 |
| `0x03` | `RemoveGroupResponse` | `1` | `GroupID` | `group-id` | 최솟값 `1` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| 이름 | `Groups` |
| 도메인 | `General` |
| 코드 | `0x0004` |
| define | `GROUPS_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="5"` |

파일은 `Alchemy`로 생성되었으며 직접 수정하지 않도록 표시되어 있다. 생성 원본은 `src/app_clusters/Groups.adoc`이고, 기록된 버전은 Git `0.9-1.7-winter2027`, Alchemy `v1.7.10`이다.

### 기능·속성·타입 표현

- `GroupNames` 기능은 스펙과 동일하게 비트 `0`, 코드 `GN`, 선택 적합성으로 정의된다.
- `NameSupportBitmap`의 기본 타입은 `bitmap8`이다.
- `NameSupportBitmap`의 `GroupNames` 필드 마스크는 `0x80`이다.
- `NameSupport`는 서버 속성으로 정의된다.
  - 코드: `0x0000`
  - define: `GROUP_NAME_SUPPORT`
  - 타입: `NameSupportBitmap`
  - 최댓값: `0x80`

| 스펙 표현 | SDK XML 표현 |
|---|---|
| `group-id` | `group_id` |
| `string`, 최대 길이 `16` | `char_string`, `length="16"` |
| `uint8`, nullable | `int8u`, `isNullable="true"` |
| `list`의 `group-id` 항목 | `type="group_id"`, `array="true"` |

SDK XML의 `GroupList`에는 항목별 `min="1"`이 명시되어 있지 않지만, 제공된 스펙 XML에는 각 항목의 최솟값 `1`이 명시되어 있다.

### 명령과 CLI 메타데이터

| 명령 | 코드 | CLI |
|---|---|---|
| `AddGroup` | `0x00` | `zcl groups add` |
| `ViewGroup` | `0x01` | `zcl groups view` |
| `GetGroupMembership` | `0x02` | `zcl groups get` |
| `RemoveGroup` | `0x03` | `zcl groups remove` |
| `RemoveAllGroups` | `0x04` | `zcl groups rmall` |
| `AddGroupIfIdentifying` | `0x05` | `zcl groups add-if-id` |

- 요청 명령은 모두 `source="client"`, `isFabricScoped="true"`이며 필수이다.
- `GetGroupMembership`의 `cliFunctionName`은 `zclGroupsGetCommand`이다.
- `AddGroup`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying`에는 `manage` 호출 권한이 명시되어 있다.
- `ViewGroup`, `GetGroupMembership`에는 SDK XML 내 별도 접근 권한 요소가 없다. 스펙 XML에는 `operate`가 명시되어 있다.
- `AddGroupResponse`, `ViewGroupResponse`, `GetGroupMembershipResponse`, `RemoveGroupResponse`는 모두 `source="server"`, `disableDefaultResponse="true"`이며 필수이다.
- SDK XML의 `RemoveAllGroups`, `AddGroupIfIdentifying`에는 `response` 속성이 없다. 스펙 XML에는 `response="Y"`가 명시되어 있다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/groups-server/CodegenIntegration.cpp` | 서버 인스턴스 생성·등록·해제 |
| `src/app/clusters/groups-server/GroupsCluster.h` | 빌드 설정에 따른 `GroupsCluster` 별칭 선택 |
| `src/app/clusters/groups-server/GroupsClusterContext.h` | 공통 생성 컨텍스트 |
| `src/app/clusters/groups-server/GroupsClusterImpl.h` | 전체 구현 인터페이스 |
| `src/app/clusters/groups-server/GroupsClusterImpl.cpp` | 전체 속성 읽기 및 명령 처리 |
| `src/app/clusters/groups-server/StubbedGroupsCluster.h` | 호환성 전용 구현 인터페이스 |
| `src/app/clusters/groups-server/StubbedGroupsCluster.cpp` | 호환성 전용 속성 읽기 및 제한된 명령 처리 |

### 구현 선택과 공통 컨텍스트

`GroupsCluster.h`는 `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER`에 따라 별칭을 선택한다.

| 조건 | `GroupsCluster`가 가리키는 클래스 |
|---|---|
| `CHIP_CONFIG_USE_STUBBED_GROUPS_CLUSTER` 활성화 | `StubbedGroupsCluster` |
| 그 외 | `GroupsClusterImpl` |

원문 주석은 `Groupcast`를 활성화한 빌드에서 호환성 전용 구현을 사용한다고 설명한다. 애플리케이션은 구체적인 클래스 대신 `GroupsCluster` 별칭을 사용하도록 안내되어 있다.

두 클래스는 `DefaultServerCluster`를 상속하고 `Context`를 `GroupsClusterContext`의 별칭으로 정의한다.

| `GroupsClusterContext` 멤버 | 타입 | 기본값·용도 |
|---|---|---|
| `groupDataProvider` | `Credentials::GroupDataProvider &` | 필수 그룹 데이터 제공자 |
| `scenesIntegration` | `scenes::ScenesIntegrationDelegate *` | `nullptr`이면 scenes 지원 없음 |
| `identifyIntegration` | `IdentifyIntegrationDelegate *` | `nullptr`이면 identify 지원 없음 |

`StubbedGroupsCluster`는 `groupDataProvider`만 사용한다. `ScenesIntegrationDelegate`는 공통 컨텍스트 헤더에서 전방 선언되어, 해당 헤더를 통해 scenes 구현이 포함·링크되지 않도록 한다.

### 서버 등록과 수명 관리

`CodegenIntegration.cpp`는 다음 값으로 서버 저장 공간을 구성한다.

- `kGroupsFixedClusterCount`: `Groups::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kGroupsMaxClusterCount`: `kGroupsFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: `LazyRegisteredServerCluster<GroupsCluster>` 배열

`IntegrationDelegate`의 주요 동작은 다음과 같다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | `Credentials::GetGroupDataProvider()`를 조회하고 `VerifyOrDie`로 null이 아님을 확인한 뒤 서버 생성 |
| `FindRegistration` | 서버가 생성되지 않았으면 `nullptr`, 생성되었으면 클러스터 반환 |
| `ReleaseRegistration` | 해당 서버의 `Destroy()` 호출 |

조건부 통합은 다음과 같다.

- `MATTER_DM_PLUGIN_SCENES_MANAGEMENT`가 정의되면 `ScenesManagement::FindClusterOnEndpoint(endpointId)`를 연결한다.
- `ZCL_USING_IDENTIFY_CLUSTER_SERVER`가 정의되면 `FindIdentifyClusterOnEndpoint(endpointId)`를 연결한다.

수명 관리 콜백:

- `MatterGroupsClusterInitCallback`: `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`.
- `MatterGroupsClusterShutdownCallback`: `CodegenClusterIntegration::UnregisterServer` 호출.
- `MatterGroupsPluginServerInitCallback`, `MatterGroupsPluginServerShutdownCallback`: 빈 구현.

### 공통 속성 및 명령 목록

두 구현 모두 다음 인터페이스를 제공한다.

- `Attributes`: `Attributes::kMandatoryMetadata` 추가
- `AcceptedCommands`: 요청 명령 6개 등록
- `GeneratedCommands`: 응답 명령 4개 등록
- `ReadAttribute`: 속성 읽기
- `InvokeCommand`: 명령 처리

`StubbedGroupsCluster`도 동일한 명령 목록을 등록하지만 일부 명령의 실행은 거부한다.

| 속성 | `GroupsClusterImpl` | `StubbedGroupsCluster` |
|---|---|---|
| `ClusterRevision` | `4`로 고정 | `kRevision` |
| `FeatureMap` | `Feature::kGroupNames` | `Feature::kGroupNames` |
| `NameSupport` | `NameSupportBitmap::kGroupNames` | `NameSupportBitmap::kGroupNames` |
| 그 외 | `Status::UnsupportedAttribute` | `Status::UnsupportedAttribute` |

`StubbedGroupsCluster`에는 `Groups::kRevision >= 5`를 확인하는 `static_assert`가 있다.

> 제공된 스펙과 SDK XML에서 `GroupNames` 기능은 선택이지만, 두 구현은 항상 `Feature::kGroupNames`를 반환한다. 구현 주석의 필수 적합성 설명과 XML의 기능 적합성 표기는 구분해야 한다.

### `GroupsClusterImpl` 명령 처리

#### `AddGroup`

`InvokeCommand`는 요청을 디코딩하고 내부 `AddGroup`의 결과를 `AddGroupResponse`에 담아 반환한다.

내부 `AddGroup`의 처리 순서:

1. `IsValidGroupId(groupID)`와 `GroupDataProvider::GroupInfo::kGroupNameMax`를 이용해 입력을 검증한다. 실패하면 `Status::ConstraintError`.
2. `KeyExists`로 그룹에 연결된 키 세트가 존재하는지 확인한다. 없으면 `Status::UnsupportedAccess`.
3. `GetGroupInfo`로 기존 정보를 조회한다.
   - 조회 성공: `SetName`으로 이름만 변경하여 `HasAuxiliaryAcl` 같은 기존 플래그를 보존한다.
   - `CHIP_ERROR_NOT_FOUND`: 새 `GroupDataProvider::GroupInfo`를 구성한다.
   - 그 외 오류: `Status::Failure`.
4. `SetGroupInfo`를 호출한다. 실패하면 `Status::ResourceExhausted`.
5. `AddEndpoint`를 호출한다. 실패하면 `RemoveGroupInfo`를 통한 되돌리기를 시도하고 `Status::ResourceExhausted`.
6. 그룹 테이블 변경을 알리고, 필요하면 보조 접근 제어 변경 이벤트를 발생시킨다.
7. `Status::Success`를 반환한다.

`KeyExists`는 `IterateGroupKeys`로 순회하면서 `group_id`가 일치하고 `GetKeySet`이 성공하는 항목을 찾는다.

#### `ViewGroup`

- 그룹 ID가 유효하지 않으면 `Status::ConstraintError`.
- `HasEndpoint`가 거짓이거나 `GetGroupInfo`가 실패하면 `Status::NotFound`.
- 성공하면 그룹 이름을 포함한 `ViewGroupResponse`를 반환한다.
- 실패 응답의 이름은 빈 문자열로 설정한다.

#### `GetGroupMembership`

- `IterateEndpoints` 실패 시 `Status::Failure`.
- `GroupMembershipResponse::Encode`가 응답을 인코딩한다.
- `Capacity`는 추가 그룹 수용 가능 여부를 알 수 없다는 의미의 null 값이다.
- 현재 Endpoint의 매핑만 응답에 포함한다.
- 요청 `GroupList`가 비어 있으면 해당 Endpoint가 속한 모든 그룹을 포함한다.
- 요청 `GroupList`가 비어 있지 않으면 목록에 일치하는 그룹만 포함한다.

#### `RemoveGroup`

- 그룹 ID가 유효하지 않으면 `Status::ConstraintError`.
- 해당 Endpoint 매핑이 없거나 `RemoveEndpoint`가 실패하면 `Status::NotFound`.
- 제거 성공 시 `scenesIntegration`이 있으면 `GroupWillBeRemoved`를 호출한다. 해당 호출의 오류는 로그로 남긴다.
- 그룹 테이블 변경을 알리고 `Status::Success`를 포함한 `RemoveGroupResponse`를 반환한다.
- 필요하면 보조 접근 제어 변경 이벤트를 발생시킨다.

#### `RemoveAllGroups`

- `scenesIntegration`이 있으면 현재 Endpoint에 연결된 각 그룹과 `scenes::kGlobalSceneGroupId`에 대해 `GroupWillBeRemoved`를 호출한다.
- 이 과정에서 `IterateEndpoints`가 실패하면 `Status::Failure`.
- `RemoveEndpoint(fabricIndex, mPath.mEndpointId)`로 해당 fabric의 Endpoint 연결을 모두 제거한다.
- 제거 오류는 로그로 남기며, 이후 그룹 테이블 변경 알림과 필요한 보조 접근 제어 변경 이벤트를 처리한다.
- 최종 반환값은 `Status::Success`이다.

#### `AddGroupIfIdentifying`

- 요청 디코딩 후 `identifyIntegration`이 없거나 `IsIdentifying()`이 거짓이면 추가 작업 없이 `Status::Success`.
- 식별 중이면 내부 `AddGroup`을 호출한다.
- `AddGroupResponse` 구조체 대신 처리 상태를 반환한다.

등록되지 않은 명령 ID는 `Status::UnsupportedCommand`를 반환한다.

### 변경 알림과 연동

`NotifyGroupTableChanged`는 컨텍스트가 있을 때 다음 속성 경로에 대해 `DataModel::AttributeChangeType::kReportable` 변경을 알린다.

- Endpoint: `kRootEndpointId`
- 클러스터: `GroupKeyManagement::Id`
- 속성: `GroupKeyManagement::Attributes::GroupTable::Id`

`ConsumeAuxAclNotificationNeeded()`가 참이면 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출한다. 이 처리는 전체 구현의 그룹 추가·제거 경로와 호환성 전용 구현의 그룹 제거 경로에 포함된다.

### `StubbedGroupsCluster` 명령 처리

이 구현은 revision `5` 이상을 위한 호환성 전용 구현이다.

| 명령 | 동작 |
|---|---|
| `AddGroup` | `Status::InvalidInState` |
| `ViewGroup` | `Status::InvalidInState` |
| `GetGroupMembership` | `Status::InvalidInState` |
| `AddGroupIfIdentifying` | `Status::InvalidInState` |
| `RemoveGroup` | 요청 디코딩, 그룹 ID와 Endpoint 매핑 검증 후 제거하고 `RemoveGroupResponse` 반환 |
| `RemoveAllGroups` | 해당 fabric의 Endpoint 연결을 모두 제거하고 `Status::Success` 반환 |
| 그 외 | `Status::UnsupportedCommand` |

추가 동작:

- `RemoveGroup`은 유효하지 않은 그룹 ID에 `Status::ConstraintError`, 매핑 부재 또는 제거 실패에 `Status::NotFound`, 성공에 `Status::Success`를 반환한다.
- `RemoveAllGroups`는 제거 실패를 로그로 남기지만 최종적으로 `Status::Success`를 반환한다.
- 두 제거 경로는 필요하면 `AccessControl::EmitAuxiliaryAccessUpdated`를 호출한다.
- 제공된 호환성 전용 구현에는 scenes 연동이나 `NotifyGroupTableChanged` 호출이 없다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
