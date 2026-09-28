---
entity: Fan Control
ids: ['0x0202']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fan-control-cluster.xml', 'src/app/clusters/fan-control-server/FanControlCluster.cpp', 'src/app/clusters/fan-control-server/CodegenIntegration.h', 'src/app/clusters/fan-control-server/CodegenIntegration.cpp', 'src/app/clusters/fan-control-server/README.md', 'src/app/clusters/fan-control-server/fan-control-delegate.h', 'src/app/clusters/fan-control-server/fan-control-server.h', 'src/app/clusters/fan-control-server/FanControlCluster.h', 'data_model/1.7/clusters/FanControl.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Fan Control 클러스터는 팬 장치를 제어하기 위한 인터페이스를 제공합니다. 팬 모드, 속도, 공기 흐름 방향, 바람 모드 및 흔들림 동작을 설정할 수 있습니다.

이 디렉토리는 Matter Fan Control 클러스터 서버(`FanControlCluster.h`)의 코드 기반 C++ 구현을 포함하고 있습니다. 이 구현은 유연성을 위해 설계되었으며, 이전의 ZAP/Ember 기반 구현에서 발생하는 긴밀한 결합을 피합니다. 

델리게이트 패턴(`chip::app::Clusters::FanControl::Delegate`)을 사용하여 팬 모드, 속도 또는 다른 설정이 수정될 때 클러스터 관련 이벤트 및 상태 변경에 대해 애플리케이션에 알립니다.

## 스펙
- **클러스터 ID**: 0x0202
- **클러스터 이름**: Fan Control
- **속성**:
  - `FanMode` (0x0000): FanModeEnum
  - `FanModeSequence` (0x0001): FanModeSequenceEnum
  - `PercentSetting` (0x0002): percent
  - `PercentCurrent` (0x0003): percent
  - `SpeedMax` (0x0004): uint8
  - `SpeedSetting` (0x0005): uint8
  - `SpeedCurrent` (0x0006): uint8
  - `RockSupport` (0x0007): RockBitmap
  - `RockSetting` (0x0008): RockBitmap
  - `WindSupport` (0x0009): WindBitmap
  - `WindSetting` (0x000A): WindBitmap
  - `AirflowDirection` (0x000B): AirflowDirectionEnum
- **명령**:
  - `Step` (0x00): StepDirectionEnum

## SDK 정의
### FanControlCluster.h
`FanControlCluster`는 `DefaultServerCluster`를 상속하며, 다음과 같은 기능을 제공합니다:
- 팬 모드 및 해당 속성을 설정하고 검색하는 메소드.
- 팬 속도를 제어하기 위한 명령을 처리하는 메소드.

### FanControlDelegate.h
`Delegate` 클래스는 팬 제어 클러스터의 애플리케이션 특정 로직을 구현하는 방법을 정의합니다. 이 클래스는 팬의 상태 변화와 관련된 여러 메소드를 포함합니다.

## 구현
### FanControlCluster.cpp
이 파일은 `FanControlCluster`의 구체적인 구현을 포함하고 있으며, STARTUP 및 명령 처리와 관련된 메소드가 포함되어 있습니다. 팬 모드, 속도, 및 프로퍼티 변경에 대한 변경사항을 관리합니다.

### CodegenIntegration.h / CodegenIntegration.cpp
이 파일들은 ZAP 구동의 정적 클러스터와의 호환성을 위한 브리지를 제공합니다. 이는 Attribute storage와 데이터 모델을 `FanControlCluster`에 연결합니다.

## 예시
다음은 `FanControlCluster`를 애플리케이션에 통합하는 방법의 예입니다.

### 1. Delegate 구현
```cpp
#include <app/clusters/fan-control-server/fan-control-delegate.h>

class MyFanControlDelegate : public chip::app::Clusters::FanControl::Delegate
{
public:
    MyFanControlDelegate(chip::EndpointId endpoint) : Delegate(endpoint) {}

    chip::Protocols::InteractionModel::Status HandleStep(
        chip::app::Clusters::FanControl::StepDirectionEnum aDirection,
        bool aWrap,
        bool aLowestOff) override
    {
        // Step command 로직 처리
        return chip::Protocols::InteractionModel::Status::Success;
    }

    void OnFanDriveStateChanged(const chip::app::Clusters::FanControl::FanDriveState & newState) override
    {
        // 팬 상태 변경에 반응
    }
};
```

### 2. Delegate 및 클러스터 인스턴스화
```cpp
#include "app/clusters/fan-control-server/FanControlCluster.h"

MyFanControlDelegate gMyFanDelegate(kYourEndpointId);

chip::app::RegisteredServerCluster<chip::app::Clusters::FanControlCluster> gFanControlCluster(
    chip::app::Clusters::FanControlCluster::Config(kYourEndpointId, gMyFanDelegate)
        .WithFanModeSequence(chip::app::Clusters::FanControl::FanModeSequenceEnum::kOffLowHigh)
        .WithSpeedMax(10)
        .WithStep()
);
```

### 3. 클러스터 등록
애플리케이션 초기화 루틴에서 클러스터 인스턴스를 `CodegenDataModelProvider`에 등록합니다.
```cpp
#include "data-model-providers/codegen/CodegenDataModelProvider.h"

void ApplicationInit()
{
    // ... 다른 초기화
    CHIP_ERROR err = chip::app::CodegenDataModelProvider::Instance().Registry().Register(gFanControlCluster.Registration());
    VerifyOrDie(err == CHIP_NO_ERROR);
    // ...
}
```

## 관련 문서
- [Fan Control Cluster Specification](https://www.example.com)
- [Matter GitHub Repository](https://github.com/project-chip)

이 문서는 Matter Fan Control 클러스터의 구현 및 사용법을 설명합니다.