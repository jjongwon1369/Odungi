---
entity: Operational State
ids: ['0x0060']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateDelegate.h', 'src/app/clusters/operational-state-server/CodegenIntegration.h', 'src/app/clusters/operational-state-server/OperationalStateCluster.h', 'src/app/clusters/operational-state-server/CodegenIntegration.cpp', 'src/app/clusters/operational-state-server/README.md', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-cluster-objects.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-server.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp', 'data_model/1.7/clusters/OperationalState.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

`Operational State` 클러스터(`0x0060`)는 상태 머신이 동작의 일부인 디바이스의 operational state를 원격으로 모니터링하고, 지원되는 경우 변경할 수 있도록 합니다.

Matter SDK에서는 `OperationalState::OperationalStateCluster`가 `DefaultServerCluster`를 확장하는 code-driven 구현으로 제공됩니다. 다음 derived cluster의 기본 로직으로 사용할 수 있습니다.

- `Operational State`
- `RvcOperationalState`
- `OvenCavityOperationalState`

새 애플리케이션은 `OperationalStateCluster`를 직접 사용하는 것이 권장됩니다. `OperationalState::Instance`, `RvcOperationalState::Instance`, `OvenCavityOperationalState::Instance`는 기존 codegen API와의 호환성을 위한 wrapper입니다.

## 스펙

### 클러스터

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Operational State Cluster` |
| 클러스터 ID | `0x0060` |
| revision | `3` |
| hierarchy | `base` |
| role | `application` |
| PICS | `OPSTATE` |
| scope | `Endpoint` |

revision history:

- revision `1`: Initial revision
- revision `2`: `Pause` 및 `Resume` 명령을 모든 compatible state에서 사용할 수 있도록 변경하고 base/derived cluster의 reserved range 정의
- revision `3`: `CountdownTime` attribute를 Q quality로 변경

### 데이터 타입

#### `ErrorStateEnum`

| 값 | 항목 | 설명 |
|---|---|---|
| `0x00` | `NoError` | 디바이스가 error state가 아님 |
| `0x01` | `UnableToStartOrResume` | 디바이스가 operation을 start 또는 resume할 수 없음 |
| `0x02` | `UnableToCompleteOperation` | 디바이스가 현재 operation을 완료할 수 없음 |
| `0x03` | `CommandInvalidInState` | 현재 state에서 command를 처리할 수 없음 |

#### `OperationalStateEnum`

| 값 | 항목 | 설명 |
|---|---|---|
| `0x00` | `Stopped` | 디바이스가 중지됨 |
| `0x01` | `Running` | 디바이스가 동작 중 |
| `0x02` | `Paused` | operation 중 일시 정지됨 |
| `0x03` | `Error` | 디바이스가 error state임 |

#### `ErrorStateStruct`

| Field ID | 이름 | 타입 | 조건 |
|---:|---|---|---|
| `0` | `ErrorStateID` | `ErrorStateEnum` | 필수, 기본값 `0` |
| `1` | `ErrorStateLabel` | `string` | `ErrorStateID`가 `0x80`~`0xBF`인 경우 필수, 최대 길이 `64` |
| `2` | `ErrorStateDetails` | `string` | 선택, 최대 길이 `64` |

#### `OperationalStateStruct`

| Field ID | 이름 | 타입 | 조건 |
|---:|---|---|---|
| `0` | `OperationalStateID` | `OperationalStateEnum` | 필수, 기본값 `0` |
| `1` | `OperationalStateLabel` | `string` | `OperationalStateID`가 `0x80`~`0xBF`인 경우 필수, 최대 길이 `64` |

### Attributes

| ID | 이름 | 타입 | 조건 |
|---|---|---|---|
| `0x0000` | `PhaseList` | `list` of `string` | 필수, nullable, 최대 32개, 각 항목 최대 길이 `64` |
| `0x0001` | `CurrentPhase` | `uint8` | 필수, nullable |
| `0x0002` | `CountdownTime` | `elapsed-s` | 선택, nullable, quieter reporting, 최대 `259200` |
| `0x0003` | `OperationalStateList` | `list` of `OperationalStateStruct` | 필수 |
| `0x0004` | `OperationalState` | `OperationalStateEnum` | 필수 |
| `0x0005` | `OperationalError` | `ErrorStateStruct` | 필수 |

### Commands

모든 client-to-server command의 `invokePrivilege`는 `operate`입니다.

| ID | 이름 | 방향 | 응답 | 조건 |
|---|---|---|---|---|
| `0x00` | `Pause` | `commandToServer` | `OperationalCommandResponse` | 지원 시 필수이며, 미지원 시 `Resume`이 필수 |
| `0x01` | `Stop` | `commandToServer` | `OperationalCommandResponse` | 지원 시 필수이며, 미지원 시 `Start`가 필수 |
| `0x02` | `Start` | `commandToServer` | `OperationalCommandResponse` | 선택 |
| `0x03` | `Resume` | `commandToServer` | `OperationalCommandResponse` | 지원 시 필수이며, 미지원 시 `Pause`가 필수 |
| `0x04` | `OperationalCommandResponse` | `responseFromServer` | - | `Pause`, `Stop`, `Start`, `Resume` 중 하나를 지원하는 경우 필수 |

`OperationalCommandResponse`의 field:

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `CommandResponseState` | `ErrorStateStruct` |

### Events

| ID | 이름 | priority | 조건 |
|---|---|---|---|
| `0x00` | `OperationalError` | `critical` | 필수 |
| `0x01` | `OperationCompletion` | `info` | 선택 |

`OperationalError`의 field:

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `ErrorState` | `ErrorStateStruct` |

`OperationCompletion`의 fields:

| Field ID | 이름 | 타입 | 조건 |
|---:|---|---|---|
| `0` | `CompletionErrorCode` | `enum8` | 필수 |
| `1` | `TotalOperationalTime` | `elapsed-s` | 선택, nullable |
| `2` | `PausedTime` | `elapsed-s` | 선택, nullable |

## SDK 정의

### XML 정의

SDK 데이터 모델 정의 파일:

`src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml`

정의된 enum:

- `OperationalStateEnum` (`enum8`)
  - `Stopped` = `0x00`
  - `Running` = `0x01`
  - `Paused` = `0x02`
  - `Error` = `0x03`
- `ErrorStateEnum` (`enum8`)
  - `NoError` = `0x00`
  - `UnableToStartOrResume` = `0x01`
  - `UnableToCompleteOperation` = `0x02`
  - `CommandInvalidInState` = `0x03`

정의된 struct:

- `OperationalStateStruct`
  - `OperationalStateID`
  - 선택 field `OperationalStateLabel`, 최대 길이 `64`
- `ErrorStateStruct`
  - `ErrorStateID`
  - 선택 field `ErrorStateLabel`, 최대 길이 `64`
  - 선택 field `ErrorStateDetails`, 최대 길이 `64`

XML에서 `OperationalStateStruct`와 `ErrorStateStruct`는 다음 cluster code에 공통으로 연결됩니다.

- `0x0060`
- `0x0061`
- `0x0048`

`Operational State` cluster 정의:

- cluster code: `0x0060`
- define: `OPERATIONAL_STATE_CLUSTER`
- client: 지원
- server: 지원
- global attribute:
  - `0xFFFD` = `3`

## 구현

### 기본 클래스

주요 헤더:

`src/app/clusters/operational-state-server/OperationalStateCluster.h`

주요 구현:

`src/app/clusters/operational-state-server/OperationalStateCluster.cpp`

`OperationalState::OperationalStateCluster`는 `DefaultServerCluster`를 상속하며, 다음 API를 제공합니다.

```cpp
CHIP_ERROR SetCurrentPhase(const DataModel::Nullable<uint8_t> & aPhase);
CHIP_ERROR SetOperationalState(uint8_t aOpState);
CHIP_ERROR SetOperationalState(OperationalStateEnum aOpState);

DataModel::Nullable<uint8_t> GetCurrentPhase() const;
uint8_t GetCurrentOperationalState() const;
void GetCurrentOperationalError(GenericOperationalError & error) const;

void UpdateCountdownTimeFromDelegate();

void OnOperationalErrorDetected(const Structs::ErrorStateStruct::Type & aError);
void OnOperationCompletionDetected(
    uint8_t aCompletionErrorCode,
    const Optional<DataModel::Nullable<uint32_t>> & aTotalOperationalTime = NullOptional,
    const Optional<DataModel::Nullable<uint32_t>> & aPausedTime = NullOptional);

void ReportOperationalStateListChange();
void ReportPhaseListChange();

bool IsSupportedPhase(uint8_t aPhase);
bool IsSupportedOperationalState(uint8_t aState);
```

`Config`에서는 optional attribute를 설정할 수 있습니다.

```cpp
struct Config
{
    OptionalAttributeSet optionalAttributes;
};
```

현재 optional attribute는 `CountdownTime`입니다.

### `OperationalStateCluster::Delegate`

애플리케이션은 `OperationalStateCluster::Delegate`를 상속하고 다음 virtual method를 구현해야 합니다.

```cpp
virtual app::DataModel::Nullable<uint32_t> GetCountdownTime() = 0;

virtual CHIP_ERROR GetOperationalStateAtIndex(
    size_t index,
    GenericOperationalState & operationalState) = 0;

virtual CHIP_ERROR GetOperationalPhaseAtIndex(
    size_t index,
    MutableCharSpan & operationalPhase) = 0;

virtual void HandlePauseStateCallback(
    GenericOperationalError & err) = 0;

virtual void HandleResumeStateCallback(
    GenericOperationalError & err) = 0;

virtual void HandleStartStateCallback(
    GenericOperationalError & err) = 0;

virtual void HandleStopStateCallback(
    GenericOperationalError & err) = 0;
```

RVC 전용 `GoHome` 처리를 위해 다음 callback을 override할 수 있습니다.

```cpp
virtual void HandleGoHomeCommandCallback(GenericOperationalError & err)
```

기본 구현은 `ErrorStateEnum::kUnknownEnumValue`를 반환하여 unsupported 상태를 나타냅니다.

### Attribute 처리

`ReadAttribute`는 다음 attribute를 처리합니다.

- `PhaseList`
- `CurrentPhase`
- `CountdownTime`
- `OperationalStateList`
- `OperationalState`
- `OperationalError`

`PhaseList`는 최대 `32`개 항목을 읽으며, `GetOperationalPhaseAtIndex`가 `CHIP_ERROR_NOT_FOUND`를 반환하면 목록을 종료합니다.

`OperationalStateList`는 최대 `256`개의 state를 순회합니다. `OperationalStateID`가 `uint8_t`이므로 최대 state 수를 `256`으로 제한합니다.

`SetCurrentPhase`는 `aPhase`가 null이 아니면서 `IsSupportedPhase`가 false인 경우 `CHIP_ERROR_INVALID_ARGUMENT`를 반환합니다.

`SetOperationalState`는 다음 상태를 거부합니다.

- `OperationalStateEnum::kError`
- `IsSupportedOperationalState(aOpState)`가 false인 state

`SetOperationalState`로 상태가 변경되거나 오류가 `NoError`로 초기화되면 `CountdownTime` 갱신이 수행됩니다.

### Command 처리

`InvokeCommand`는 다음 command를 처리합니다.

- `Pause`
- `Resume`
- `Stop`
- `Start`

모든 command는 fieldless command이며, trailing payload가 있으면 `InvalidCommand`를 반환합니다.

`OperationalCommandResponse`는 각 accepted command에 대해 생성되며, `CommandResponseState`에 `GenericOperationalError`를 담습니다.

기본 처리 규칙:

- 현재 상태가 `Stopped` 또는 `Error`이면 `Pause`와 `Resume`은 `CommandInvalidInState`
- `Pause` 또는 `Resume` 실행 시 target state가 현재 상태와 다를 때만 delegate callback 호출
- `Start` 또는 `Stop` 실행 시 target state가 현재 상태와 다를 때만 delegate callback 호출
- callback 처리 후 `OperationalCommandResponse` 반환

기본 `AcceptedCommands`는 다음과 같습니다.

```cpp
OperationalState::Commands::Pause::kMetadataEntry
OperationalState::Commands::Stop::kMetadataEntry
OperationalState::Commands::Start::kMetadataEntry
OperationalState::Commands::Resume::kMetadataEntry
```

`GeneratedCommands`에는 다음 command가 등록됩니다.

```cpp
OperationalState::Commands::OperationalCommandResponse::Id
```

### Error 및 Completion 이벤트

`OnOperationalErrorDetected`는 다음 작업을 수행합니다.

1. 현재 `OperationalState`가 `OperationalStateEnum::kError`가 아니면 `Error`로 변경
2. `OperationalError`가 변경된 경우 attribute 변경 통지
3. `CountdownTime` 갱신
4. `GenericErrorEvent` 생성 및 event 생성

`OnOperationCompletionDetected`는 `GenericOperationCompletionEvent`를 생성하고 event를 생성한 뒤 `CountdownTime`을 갱신합니다.

### Derived cluster

#### `RvcOperationalStateCluster`

헤더:

`src/app/clusters/operational-state-server/RvcOperationalStateCluster.h`

구현:

`src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp`

`RvcOperationalStateCluster`는 `OperationalState::OperationalStateCluster`를 상속합니다.

추가 accepted command:

```cpp
RvcOperationalState::Commands::Pause::kMetadataEntry
RvcOperationalState::Commands::Resume::kMetadataEntry
RvcOperationalState::Commands::GoHome::kMetadataEntry
```

`GoHome` 처리:

- payload가 있으면 `InvalidCommand`
- 현재 상태가 `Charging` 또는 `Docked`이면 `CommandInvalidInState`
- 현재 상태가 `SeekingCharger`가 아니고 오류가 없으면 `HandleGoHomeCommandCallback` 호출
- `OperationalCommandResponse` 반환

`Pause` compatible derived state:

```cpp
RvcOperationalState::OperationalStateEnum::kSeekingCharger
```

`Resume` compatible derived states:

```cpp
RvcOperationalState::OperationalStateEnum::kCharging
RvcOperationalState::OperationalStateEnum::kDocked
```

#### `OvenCavityOperationalStateCluster`

헤더:

`src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h`

구현:

`src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp`

`OvenCavityOperationalStateCluster`의 accepted command는 다음과 같습니다.

```cpp
OvenCavityOperationalState::Commands::Stop::kMetadataEntry
OvenCavityOperationalState::Commands::Start::kMetadataEntry
```

### Backward compatibility wrapper

관련 헤더:

- `src/app/clusters/operational-state-server/OperationalStateDelegate.h`
- `src/app/clusters/operational-state-server/CodegenIntegration.h`
- `src/app/clusters/operational-state-server/CodegenIntegration.cpp`
- `src/app/clusters/operational-state-server/operational-state-server.h`

기존 `Instance` API는 다음 lifecycle method를 제공합니다.

```cpp
CHIP_ERROR Init();
void Shutdown();
void SetDelegate(Delegate * aDelegate);
Delegate * GetDelegate() const;
```

`Init()`는 `CodegenDataModelProvider::Instance().Registry().Register`를 통해 cluster를 등록합니다. `Shutdown()`은 registry에서 cluster를 unregister합니다.

`Instance`는 다음 application-facing API를 underlying `OperationalStateCluster`로 전달합니다.

- `SetCurrentPhase`
- `SetOperationalState`
- `GetCurrentPhase`
- `GetCurrentOperationalState`
- `GetCurrentOperationalError`
- `UpdateCountdownTimeFromDelegate`
- `OnOperationalErrorDetected`
- `OnOperationCompletionDetected`
- `ReportOperationalStateListChange`
- `ReportPhaseListChange`
- `IsSupportedPhase`
- `IsSupportedOperationalState`

`CodegenIntegration.cpp`에는 다음 callback의 no-op stub이 제공됩니다.

- `emberAfOperationalStateClusterServerInitCallback`
- `MatterOperationalStateClusterServerShutdownCallback`
- `MatterOperationalStateClusterServerAttributeChangedCallback`
- `MatterOperationalStateClusterServerPreAttributeChangedCallback`
- `emberAfRvcOperationalStateClusterServerInitCallback`
- `MatterRvcOperationalStateClusterServerShutdownCallback`
- `MatterRvcOperationalStateClusterServerAttributeChangedCallback`
- `MatterRvcOperationalStateClusterServerPreAttributeChangedCallback`
- `emberAfOvenCavityOperationalStateClusterServerInitCallback`
- `MatterOvenCavityOperationalStateClusterServerShutdownCallback`
- `MatterOvenCavityOperationalStateClusterServerAttributeChangedCallback`
- `MatterOvenCavityOperationalStateClusterServerPreAttributeChangedCallback`

### 내부 객체

파일:

`src/app/clusters/operational-state-server/operational-state-cluster-objects.h`

주요 객체:

- `GenericOperationalState`
- `GenericOperationalError`
- `GenericErrorEvent`
- `GenericOperationCompletionEvent`

크기 제한 상수:

```cpp
kOperationalStateLabelMaxSize
kOperationalErrorLabelMaxSize
kOperationalErrorDetailsMaxSize
kOperationalPhaseNameMaxSize
```

### 새로운 derived cluster 추가

1. `src/app/zap-templates/zcl/data-model/chip/`에 cluster XML 추가
2. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters`에 cluster 추가
3. `scripts/tools/zap/zap_regen_all.py`로 ZAP 및 `py_matter_idl` 출력 재생성
4. `RvcOperationalStateCluster`를 참고하여 `OperationalStateCluster` subclass 작성
5. `RegisteredServerCluster`를 통해 등록
6. all-clusters-app example에 새 cluster 추가

## 예시

### `OperationalState::Instance` 초기화

애플리케이션 delegate 파일에서 server-side init hook을 override합니다.

```cpp
void MatterOperationalStateClusterInitCallback(chip::EndpointId endpointId)
{
    // Create delegate and instance, then call Init().
    gDelegate = new MyOperationalStateDelegate;
    gInstance  = new OperationalState::Instance(gDelegate, endpointId);
    gInstance->SetOperationalState(to_underlying(OperationalState::OperationalStateEnum::kStopped));
    gInstance->Init();
}

void MatterOperationalStateClusterShutdownCallback(chip::EndpointId endpointId,
                                                    MatterClusterShutdownType)
{
    delete gInstance;  gInstance  = nullptr;
    delete gDelegate;  gDelegate  = nullptr;
}
```

서버 cluster 초기화에는 다음 server-side hook을 사용해야 합니다.

- `Matter<ClusterName>ClusterInitCallback`
- `Matter<ClusterName>ClusterShutdownCallback`

`emberAf<ClusterName>ClusterInitCallback` 및 `emberAf<ClusterName>ClusterShutdownCallback`은 client-side hook이므로 server cluster 초기화에 사용하지 않습니다.

ZAP accessor function은 제공되지 않으므로 attribute에는 `Instance`의 `Set…` 및 `Get…` method를 사용합니다.

## 관련 문서

- `src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml`
- `data_model/1.7/clusters/OperationalState.xml`
- `src/app/clusters/operational-state-server/README.md`
- `src/app/clusters/operational-state-server/OperationalStateCluster.h`
- `src/app/clusters/operational-state-server/OperationalStateCluster.cpp`
- `src/app/clusters/operational-state-server/OperationalStateDelegate.h`
- `src/app/clusters/operational-state-server/CodegenIntegration.h`
- `src/app/clusters/operational-state-server/CodegenIntegration.cpp`
- `src/app/clusters/operational-state-server/RvcOperationalStateCluster.h`
- `src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp`
- `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h`
- `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp`
- `src/app/clusters/operational-state-server/operational-state-cluster-objects.h`
- `src/app/clusters/operational-state-server/operational-state-server.h`

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
