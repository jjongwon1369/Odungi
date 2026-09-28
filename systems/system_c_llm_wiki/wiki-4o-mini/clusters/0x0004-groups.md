---
entity: Groups
ids: ['0x0004']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/groups-cluster.xml', 'src/app/clusters/groups-server/GroupsClusterImpl.cpp', 'src/app/clusters/groups-server/StubbedGroupsCluster.h', 'src/app/clusters/groups-server/GroupsCluster.h', 'src/app/clusters/groups-server/CodegenIntegration.cpp', 'src/app/clusters/groups-server/GroupsClusterImpl.h', 'src/app/clusters/groups-server/StubbedGroupsCluster.cpp', 'src/app/clusters/groups-server/GroupsClusterContext.h', 'data_model/1.7/clusters/Groups.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
이 문서는 Groups 클러스터의 속성 및 명령을 설명합니다. 이 클러스터는 그룹 구성을 위한 명령 및 속성을 제공합니다.

## 스펙
### 클러스터 ID
- **ID**: 0x0004
- **이름**: Groups
- **버전**: 5

### 속성
- **NameSupport** (0x0000, NameSupportBitmap): 그룹 이름 저장 가능 여부를 나타냅니다.

### 명령
1. **AddGroup** (0x00)
   - 그룹 ID와 이름을 사용하여 그룹을 추가합니다.
2. **ViewGroup** (0x01)
   - 그룹 ID를 사용하여 그룹 정보를 조회합니다.
3. **GetGroupMembership** (0x02)
   - 그룹 멤버십을 조회합니다.
4. **RemoveGroup** (0x03)
   - 특정 그룹에서 멤버십을 제거합니다.
5. **RemoveAllGroups** (0x04)
   - 모든 그룹 멤버십을 제거합니다.
6. **AddGroupIfIdentifying** (0x05)
   - 엔드포인트가 자신을 식별하는 경우에만 그룹을 추가합니다.

## SDK 정의
### GroupsClusterContext
```cpp
struct GroupsClusterContext
{
    Credentials::GroupDataProvider & groupDataProvider;
    scenes::ScenesIntegrationDelegate * scenesIntegration = nullptr; 
    IdentifyIntegrationDelegate * identifyIntegration     = nullptr;
};
```

### GroupsClusterImpl
```cpp
class GroupsClusterImpl : public DefaultServerCluster
{
public:
    using Context = GroupsClusterContext;

    GroupsClusterImpl(EndpointId endpointId, const Context & context);
    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;
    std::optional<DataModel::ActionReturnStatus> InvokeCommand(const DataModel::InvokeRequest & request, TLV::TLVReader & input_arguments, CommandHandler * handler) override;

private:
    Protocols::InteractionModel::Status AddGroup(GroupId groupID, CharSpan groupName, const chip::Access::SubjectDescriptor & subjectDescriptor);
};
```

## 구현
### GroupsClusterImpl.cpp
이 파일에서는 `GroupsClusterImpl`의 주요 동작을 구현합니다. 명령 처리 및 속성 인코딩 기능이 포함되어 있습니다.

### StubbedGroupsCluster
`StubbedGroupsCluster`는 Groups 클러스터의 호환성만을 위한 구현입니다.

## 예시
`AddGroup` 명령을 사용하여 그룹을 추가하는 예제:
```cpp
Groups::Commands::AddGroup::DecodableType request_data;
// request_data 설정
auto status = mClusterImpl.AddGroup(request_data.groupID, request_data.groupName, subjectDescriptor);
```

## 관련 문서
- [ZCL Specification](https://www.zigbee.org/zigbee-for-developers/technical-documents/)
- [Matter GitHub Repository](https://github.com/project-chip/connectedhomeip)