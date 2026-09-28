---
entity: AlarmBase
ids: []
source_paths: ['src/app/clusters/alarm-base-server/Delegate.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp', 'src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h', 'data_model/1.7/clusters/AlarmBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-4o-mini
---

## 개요
`AlarmBase` 클러스터는 알람 관리 기능을 제공하는 기본 클러스터입니다. 이 클러스터는 특정 알람의 상태를 관리하고, 클라이언트의 명령을 처리하여 알람을 수정하거나 리셋하는 기능을 지원합니다.

## 스펙
- 클러스터 ID: `0x0000`
- 속성:
  - `Mask`: 알람 비트맵 (읽기 전용)
  - `Latch`: 알람 비트맵 (읽기 전용, `RESET` 기능 필요)
  - `State`: 알람 비트맵 (읽기 전용)
  - `Supported`: 알람 비트맵 (읽기 전용, 고정된 지속성 제공)
- 명령:
  - `Reset`: 알람을 리셋하는 명령 (`RESET` 기능 필요)
  - `ModifyEnabledAlarms`: 활성화된 알람을 수정하는 명령
- 이벤트:
  - `Notify`: 알람 상태 변경 통보

## SDK 정의
### Delegate.h
```cpp
namespace chip::app::Clusters::AlarmBase {
class Delegate
{
public:
    virtual bool ModifyEnabledAlarms(AlarmMap mask) { return true; }
    virtual bool ResetAlarms(AlarmMap alarms) { return true; }
};
}
```

### AlarmBaseCluster.h
```cpp
class AlarmBaseCluster : public DefaultServerCluster
{
public:
    struct Config
    {
        AlarmBase::Delegate & delegate;
        BitMask<AlarmBase::Feature> feature{};
        AlarmBase::AlarmMap supported{};
        AlarmBase::AlarmMap latch{};
        bool supportsModifyEnabledAlarms = false;
    };

    AlarmBaseCluster(EndpointId endpointId, AlarmBase::ClusterEntry cluster, const Config & config);

    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                AttributeValueEncoder & encoder) override;

    // 기타 메소드 생략
};
```

### AlarmBaseCluster.cpp
```cpp
Status AlarmBaseCluster::SetMask(const AlarmMap & mask)
{
    VerifyOrReturnError(mSupported.HasAll(mask), Status::Failure);
    return SetAttributeValue(mMask, mask, Mask::Id);
}

std::optional<DataModel::ActionReturnStatus> AlarmBaseCluster::InvokeCommand(const DataModel::InvokeRequest & request,
                                                                             TLV::TLVReader & input_arguments,
                                                                             CommandHandler * handler)
{
    switch (request.path.mCommandId)
    {
    case Commands::Reset::Id:
        // 명령 처리 로직 생략
    }
}
```

## 구현
`AlarmBaseCluster`는 클러스터의 구현체로, 알람 상태를 관리하고 클라이언트의 명령을 처리합니다. `Delegate`인터페이스를 통해 알람 수정 및 리셋에 대한 사용자 정의 로직을 구현할 수 있습니다. 

## 예시
아래는 `Reset` 명령을 처리하는 코드 예시입니다:
```cpp
DataModel::ActionReturnStatus AlarmBaseCluster::HandleReset(const AlarmMap & alarms)
{
    if (!mDelegate.ResetAlarms(alarms))
    {
        return Status::Failure;
    }
    return ResetLatchedAlarms(alarms);
}
```

## 관련 문서
- [AlarmBase 스펙 문서](data_model/1.7/clusters/AlarmBase.xml)