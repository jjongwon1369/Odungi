---
entity: Laundry Washer
ids: ['0x0073']
source_paths: ['data_model/1.7/device_types/LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-4o-mini
---

## 개요
Laundry Washer는 세탁기의 기능을 정의하는 디바이스 타입입니다. 이 디바이스는 여러 클러스터로 구성되어 있으며, 세탁기의 작동 및 제어 기능을 제공하는데 중점을 두고 있습니다.

## 스펙
- **ID**: 0x0073
- **이름**: Laundry Washer
- **개정**: 2
- **개정 역사**:
  - **1**: 초기 개정
  - **2**: OperationCompletion 이벤트 의무화

## SDK 정의
### 클러스터
- **0x0003**: Identify (서버)
  - optionalConform
- **0x0006**: On/Off (서버)
  - optionalConform
  - 특징:
    - **DF**: 의무 준수
- **0x0051**: Laundry Washer Mode (서버)
  - optionalConform
  - 특징:
    - **DEPONOFF**: 준수 금지
  - 속성:
    - **0x0002**: StartUpMode
      - 준수 금지
- **0x0053**: Laundry Washer Controls (서버)
  - optionalConform
- **0x0056**: Temperature Control (서버)
  - optionalConform
- **0x0060**: Operational State (서버)
  - 의무 준수
  - 이벤트:
    - **0x0001**: OperationCompletion
      - 의무 준수

## 구현
Implementation details are not provided in the original document.

## 예시
Examples of usage are not provided in the original document.

## 관련 문서
No related documents are provided in the original document.