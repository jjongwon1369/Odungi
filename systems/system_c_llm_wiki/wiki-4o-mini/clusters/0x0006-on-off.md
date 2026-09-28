---
entity: On/Off
ids: ['0x0006']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml', 'src/app/clusters/on-off-server/on-off-server.h', 'src/app/clusters/on-off-server/OnOffDelegate.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.cpp', 'src/app/clusters/on-off-server/OnOffCluster.cpp', 'src/app/clusters/on-off-server/OnOffEffectDelegate.h', 'src/app/clusters/on-off-server/OnOffCluster.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.h', 'data_model/1.7/clusters/OnOff.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
On/Off 클러스터는 장치를 'On'(켜기) 및 'Off'(끄기) 상태 간에 전환하는 명령과 속성을 정의합니다. 이 클러스터는 일반적인 조명 제어와 상태 관리를 지원하기 위해 여러 기능을 제공합니다.

## 스펙
- **클러스터 ID**: 0x0006
- **속성**:
  - `OnOff`: boolean (0x0000)
  - `GlobalSceneControl`: boolean (0x4000, 선택적)
  - `OnTime`: unsigned int 16 (0x4001, 선택적)
  - `OffWaitTime`: unsigned int 16 (0x4002, 선택적)
  - `StartUpOnOff`: StartUpOnOffEnum (0x4003, 선택적)
- **명령**:
  - `Off`: client -> server (0x00)
  - `On`: client -> server (0x01, 선택적)
  - `Toggle`: client -> server (0x02, 선택적)
  - `OffWithEffect`: client -> server (0x40, 선택적)
  - `OnWithRecallGlobalScene`: client -> server (0x41, 선택적)
  - `OnWithTimedOff`: client -> server (0x42, 선택적)

## SDK 정의
**OnOff 클러스터 XML 정의:**
```xml
<configurator xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../../zcl.xsd">
  <domain name="General"/>
  <!-- Enums, Bitmaps, Cluster, Attributes and Commands Definitions go here -->
</configurator>
```

**헤더 파일 예시:**
- **on-off-server.h**
```cpp
#pragma once
#include "codegen/on-off-server.h" // nogncheck
```

**클래스 정의:**
```cpp
namespace chip::app::Clusters {
class OnOffDelegate { /* ... */ };
class OnOffCluster { /* ... */ };
class OnOffLightingCluster { /* ... */ };
}
```

## 구현
On/Off 클러스터의 구현 예시입니다.
- **OnOffCluster**: 이 클래스는 On/Off 상태를 관리하며, RTC(실행 시간을 카운트하는 타이머) 기능을 사용하여 상태 전환시 대기 시간을 관리합니다.
- **OnOffLightingCluster**: 이 클래스는 On/Off 클러스터에 조명 기능을 추가 implements 합니다.

### 함수 예시
```cpp
DataModel::ActionReturnStatus OnOffCluster::InvokeCommand(const DataModel::InvokeRequest & request, TLV::TLVReader & input_arguments, CommandHandler * handler) {
    // Command handling logic
}
```

## 예시
On/Off 클러스터를 사용하는 조명 시스템 예시:
```cpp
OnOffCluster myLightCluster(endpointId, context);
myLightCluster.SetOnOff(true); // Turn on
```

## 관련 문서
- [Matter GitHub Repository](https://github.com/project-chip)
- [Matter Specification](https://github.com/project-chip/connectedhomeip-spec)
- [Matter SDK Documentation](https://sdk.matter.org/docs)