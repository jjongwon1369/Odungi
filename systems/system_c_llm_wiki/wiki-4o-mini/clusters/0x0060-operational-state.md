---
entity: Operational State
ids: ['0x0060']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateDelegate.h', 'src/app/clusters/operational-state-server/CodegenIntegration.h', 'src/app/clusters/operational-state-server/OperationalStateCluster.h', 'src/app/clusters/operational-state-server/CodegenIntegration.cpp', 'src/app/clusters/operational-state-server/README.md', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-cluster-objects.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-server.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp', 'data_model/1.7/clusters/OperationalState.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Operational State 클러스터(`0x0060`)는 운영 상태에 대한 기본 논리를 구현하는 코드 기반 클러스터입니다. 이 클러스터는 RVC 운영 상태 및 오븐 캐비티 운영 상태와 같은 파생 클러스터를 지원합니다. 코드 기반 데이터 모델 패턴을 따르며 `OperationalState::OperationalStateCluster`로 구현되고 `DefaultServerCluster`를 확장합니다.

## 스펙
### 클러스터 정보
- ID: `0x0060`
- 이름: Operational State Cluster
- 개정: 3

### 데이터 타입
- `ErrorStateEnum`
  - `0x00`: NoError
  - `0x01`: UnableToStartOrResume
  - `0x02`: UnableToCompleteOperation
  - `0x03`: CommandInvalidInState
- `OperationalStateEnum`
  - `0x00`: Stopped
  - `0x01`: Running
  - `0x02`: Paused
  - `0x03`: Error

### 구조체
- `ErrorStateStruct`
  - `ErrorStateID`: `ErrorStateEnum`
  - `ErrorStateLabel`: 문자열
  - `ErrorStateDetails`: 문자열
- `OperationalStateStruct`
  - `OperationalStateID`: `OperationalStateEnum`
  - `OperationalStateLabel`: 문자열

### 어트리뷰트
- `PhaseList` : 리스트, 최대 32개 항목
- `CurrentPhase` : uint8
- `CountdownTime` : elapsed-s (최대 259200)
- `OperationalStateList` : 리스트
- `OperationalState` : `OperationalStateEnum`
- `OperationalError` : `ErrorStateStruct`

### 명령어
- `Pause`: server에 명령
- `Stop`: server에 명령
- `Start`: server에 명령
- `Resume`: server에 명령
- `OperationalCommandResponse`: server의 응답

### 이벤트
- `OperationalError`: critical
- `OperationCompletion`: info

## SDK 정의
- `OperationalState::OperationalStateCluster` 클래스를 사용하여 클러스터를 초기화.
- `OperationalState::Delegate`를 사용하여 운영 상태에 대한 상태 목록 및 명령 콜백을 처리할 여러 가상 메서드를 구현하는 클래스 생성.

## 구현
### C++ 코드 예시
```cpp
#include "OperationalStateCluster.h"
// 생략된 기타 인클루드...

namespace chip {
namespace app {
namespace Clusters {

class MyOperationalStateDelegate : public OperationalState::Delegate {
    // 가상 메서드 구현...
};

void MatterOperationalStateClusterInitCallback(chip::EndpointId endpointId) {
    gDelegate = new MyOperationalStateDelegate;
    gInstance  = new OperationalState::Instance(gDelegate, endpointId);
    gInstance->SetOperationalState(to_underlying(OperationalState::OperationalStateEnum::kStopped));
    gInstance->Init();
}

void MatterOperationalStateClusterShutdownCallback(chip::EndpointId endpointId) {
    delete gInstance;  gInstance  = nullptr;
    delete gDelegate;  gDelegate  = nullptr;
}

} // namespace Clusters
} // namespace app
} // namespace chip
```

## 예시
- `OperationalState::RvcOperationalStateCluster` 및 `OperationalState::OvenCavityOperationalStateCluster`와 같은 파생된 클러스터를 만들기 위해 `OperationalStateCluster`를 상속받고 `RegisteredServerCluster`를 사용하여 클러스터를 등록.

## 관련 문서
- [OperationalStateCluster.h](src/app/clusters/operational-state-server/OperationalStateCluster.h)
- [RvcOperationalStateCluster.h](src/app/clusters/operational-state-server/RvcOperationalStateCluster.h)
- [OvenCavityOperationalStateCluster.h](src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h)
- [OperationalState.xml](data_model/1.7/clusters/OperationalState.xml)