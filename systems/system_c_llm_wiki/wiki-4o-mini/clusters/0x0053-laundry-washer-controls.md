---
entity: Laundry Washer Controls
ids: ['0x0053']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h', 'data_model/1.7/clusters/LaundryWasherControls.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Laundry Washer Controls 클러스터는 세탁 장치의 다양한 기능을 원격으로 모니터링하고 제어할 수 있도록 지원합니다. 이 클러스터는 세탁기와 같은 장치의 여러 기능에 대한 접근을 허용합니다.

## 스펙
- **클러스터 ID**: 0x0053
- **이름**: Laundry Washer Controls
- **설명**: 이 클러스터는 세탁 장치의 다양한 기능을 원격으로 모니터링하고 제어합니다.

### 특성
- **SPIN**: 여러 회전 속도를 지원합니다.
- **RINSE**: 여러 헹굼 사이클을 지원합니다.

### 데이터 타입
- **NumberOfRinsesEnum**
  - `0x0`: None - 헹굼 사이클을 수행하지 않음
  - `0x1`: Normal - 일반 헹굼 사이클 수행
  - `0x2`: Extra - 추가 헹굼 사이클 수행
  - `0x3`: Max - 최대 헹굼 사이클 수행

### 속성
- `SpinSpeeds`: 배열(String) (최대 16개, 각 문자열 최대 길이 64)
- `SpinSpeedCurrent`: 현재 회전 속도 (int8u, 0에서 15)
- `NumberOfRinses`: 헹굼 횟수 (NumberOfRinsesEnum)
- `SupportedRinses`: 배열(NumberOfRinsesEnum) (최대 4개)

## SDK 정의
### 헤더 파일
```cpp
#pragma once

#include "laundry-washer-controls-delegate.h"
#include <app/data-model/Nullable.h>
#include <app/server-cluster/DefaultServerCluster.h>
#include <clusters/LaundryWasherControls/Attributes.h>
```

### 클러스터 클래스
```cpp
class LaundryWasherControlsCluster : public DefaultServerCluster
{
    // ...
    
    CHIP_ERROR SetSpinSpeedCurrent(DataModel::Nullable<uint8_t> spinSpeedCurrent);
    CHIP_ERROR SetNumberOfRinses(LaundryWasherControls::NumberOfRinsesEnum numberOfRinses);
    DataModel::Nullable<uint8_t> GetSpinSpeedCurrent() const { return mSpinSpeedCurrent; }
    LaundryWasherControls::NumberOfRinsesEnum GetNumberOfRinses() const { return mNumberOfRinses; }

    // ...
};
```

## 구현
```cpp
void SetDelegate(EndpointId endpoint, Delegate & delegate);
CHIP_ERROR SetSpinSpeedCurrent(EndpointId endpointId, DataModel::Nullable<uint8_t> spinSpeedCurrent);
CHIP_ERROR GetSpinSpeedCurrent(EndpointId endpointId, DataModel::Nullable<uint8_t> & spinSpeedCurrent);
CHIP_ERROR SetNumberOfRinses(EndpointId endpointId, NumberOfRinsesEnum newNumberOfRinses);
CHIP_ERROR GetNumberOfRinses(EndpointId endpointId, NumberOfRinsesEnum & numberOfRinses);
```

## 예시
```cpp
LaundryWasherControlsCluster * cluster = FindClusterOnEndpoint(endpoint);
if (cluster != nullptr)
{
    cluster->SetSpinSpeedCurrent(spinSpeed);
    cluster->SetNumberOfRinses(numberOfRinses);
}
```

## 관련 문서
- [LaundryWasherControlsCluster.h](src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h)
- [LaundryWasherControlsCluster.cpp](src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp)
- [Laundry Washer Controls Specification](data_model/1.7/clusters/LaundryWasherControls.xml)