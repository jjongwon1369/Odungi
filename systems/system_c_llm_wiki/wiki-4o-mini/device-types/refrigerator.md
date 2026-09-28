---
entity: Refrigerator
ids: ['0x0070']
source_paths: ['data_model/1.7/device_types/Refrigerator.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-4o-mini
---

## 개요
Refrigerator는 온도 조절이 가능한 캐비닛으로, 여러 클러스터를 통해 다양한 기능을 지원합니다.

## 스펙
- **Device Type ID**: 0x0070
- **Name**: Refrigerator
- **Revision**: 3
- **Revision History**:
  - Revision 1: Initial revision
  - Revision 2: Added Cooler requirement
  - Revision 3: Added optional Activated Carbon Filter Monitoring cluster

## SDK 정의
### 조건 요구 사항
- **Device Type**: 0x0071 (Temperature Controlled Cabinet)
  - **Condition Requirement**: Cooler
    - **Mandatory Conform**: 적용

### 클러스터
- **Cluster ID**: 0x0003
  - **Name**: Identify
  - **Side**: Server
  - **Conform**: Optional

- **Cluster ID**: 0x0052
  - **Name**: Refrigerator And Temperature Controlled Cabinet Mode
  - **Side**: Server
  - **Conform**: Optional
  - **Features**:
    - **Feature Code**: DEPONOFF
      - **Disallow Conform**: 적용
  - **Attributes**:
    - **Attribute Code**: 0x0002
      - **Name**: StartUpMode
      - **Disallow Conform**: 적용

- **Cluster ID**: 0x0057
  - **Name**: Refrigerator Alarm
  - **Side**: Server
  - **Conform**: Optional

- **Cluster ID**: 0x0072
  - **Name**: Activated Carbon Filter Monitoring
  - **Side**: Server
  - **Conform**: Optional
  - **Greater or Equal Term**:
    - **Revision Value**: current
    - **Revision Value**: 3

## 구현
해당 정보는 구현 섹션에서 다루고 있지 않습니다.

## 예시
해당 정보는 예시 섹션에서 다루고 있지 않습니다.

## 관련 문서
해당 정보는 관련 문서 섹션에서 다루고 있지 않습니다.