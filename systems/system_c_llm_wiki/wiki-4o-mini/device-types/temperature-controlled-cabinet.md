---
entity: Temperature Controlled Cabinet
ids: ['0x0071']
source_paths: ['data_model/1.7/device_types/TemperatureControlledCabinet.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-4o-mini
---

## 개요
Temperature Controlled Cabinet는 냉각 및 가열 기능을 갖춘 장치로, 다양한 온도 환경을 제공하는 데 사용됩니다.

## 스펙
- **Device Type ID**: 0x0071
- **이름**: Temperature Controlled Cabinet
- **Revision**: 6
- **Revision History**:
  - 1: Initial revision
  - 2: Extension to heating cabinets
  - 3: Added exclusivity for conditions
  - 4: Mandate OperationCompletion Event for Oven Cavity Operational State cluster
  - 5: Made TemperatureNumber (TN) the only valid temperature control mode
  - 6: Added Temperature Alarm cluster

## SDK 정의
### Conditions
- **Cooler**: The device has cooling functionality.
- **Heater**: The device has heating functionality.

### Clusters
- **Oven Cavity Operational State (0x0048)**: 
  - **Commands**:
    - **Pause (0x0000)**: Disallowed conform
    - **Resume (0x0003)**: Disallowed conform
  - **Events**:
    - **OperationCompletion (0x0001)**: Mandatory conform

- **Oven Mode (0x0049)**: 
  - **Features**:
    - DEPONOFF: Disallowed conform
  - **Attributes**:
    - **StartUpMode (0x0002)**: Disallowed conform

- **Refrigerator And Temperature Controlled Cabinet Mode (0x0052)**:
  - **Features**:
    - DEPONOFF: Disallowed conform
  - **Attributes**:
    - **StartUpMode (0x0002)**: Disallowed conform

- **Temperature Control (0x0056)**:
  - **Features**:
    - **TN**: Mandatory conform
    - **TL**: Disallowed conform

- **Temperature Alarm (0x0064)**:
  - **Otherwise Conform**: Provisional and optional conform

- **Temperature Measurement (0x0402)**:
  - **Optional Conform**

## 구현
구현 세부사항은 원문에 포함되어 있지 않으므로 생략합니다.

## 예시
예시 세부사항은 원문에 포함되어 있지 않으므로 생략합니다.

## 관련 문서
관련 문서 세부사항은 원문에 포함되어 있지 않으므로 생략합니다.