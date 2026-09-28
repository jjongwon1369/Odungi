---
entity: Room Air Conditioner
ids: ['0x0072']
source_paths: ['data_model/1.7/device_types/RoomAirConditioner.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-4o-mini
---

## 개요
Room Air Conditioner는 온도 조절, 팬 제어 및 필터 모니터링을 포함한 여러 기능을 제공하는 장치입니다. 이 장치는 사용자 인터페이스를 통해 설정을 조정할 수 있으며, 그룹 방송 기능을 지원합니다.

## 스펙
- **Device Type ID**: 0x0072
- **Name**: Room Air Conditioner
- **Revision**: 5

### Revision History
1. Initial revision
2. Thermostat User Interface Configuration cluster added; Updated the Scenes cluster to Scenes Management with Cluster ID: 0x0062
3. Added filter monitoring clusters
4. Added Groupcast condition requirement
5. Added Thermostat Mode cluster.

### Condition Requirements
- **Root Node** (ID: 0x0016)
  - **GroupcastListenerCond**: optionalConform

### Clusters
- **Identify** (ID: 0x0003, Side: server) 
  - mandatoryConform
- **Groups** (ID: 0x0004, Side: server) 
  - optionalConform
- **On/Off** (ID: 0x0006, Side: server) 
  - mandatoryConform
  - Features:
    - DF: mandatoryConform
- **Scenes Management** (ID: 0x0062, Side: server) 
  - optionalConform
- **Thermostat Mode** (ID: 0x0063, Side: server) 
  - otherwiseConform
    - provisionalConform
    - optionalConform
      - greaterOrEqualTerm:
        - revision value: current
        - revision value: 5
  - Attributes:
    - **StartUpMode** (Code: 0x0002)
      - otherwiseConform
        - provisionalConform
        - disallowConform
    - **SupportedModes** (Code: 0x0000)
      - otherwiseConform
        - provisionalConform
        - mandatoryConform
- **HEPA Filter Monitoring** (ID: 0x0071, Side: server) 
  - optionalConform
- **Activated Carbon Filter Monitoring** (ID: 0x0072, Side: server) 
  - optionalConform
- **Thermostat** (ID: 0x0201, Side: server) 
  - mandatoryConform
- **Fan Control** (ID: 0x0202, Side: server) 
  - optionalConform
- **Thermostat User Interface Configuration** (ID: 0x0204, Side: server) 
  - optionalConform
  - Attributes:
    - **KeypadLockout** (Code: 0x0001)
      - optionalConform
- **Temperature Measurement** (ID: 0x0402, Side: server) 
  - optionalConform
- **Relative Humidity Measurement** (ID: 0x0405, Side: server) 
  - optionalConform

## 관련 문서
- Connectivity Standards Alliance IPR Policy
- www.csa-iot.org 