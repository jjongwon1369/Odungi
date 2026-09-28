---
entity: Refrigerator And Temperature Controlled Cabinet Mode
ids: ['0x0052']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml', 'data_model/1.7/clusters/Mode_Refrigerator.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Refrigerator And Temperature Controlled Cabinet Mode 클러스터는 지원되는 모드 목록에서 모드를 선택하는 데 필요한 속성과 명령을 제공합니다.

## 스펙
- **클러스터 ID**: 0x0052
- **클러스터 이름**: Refrigerator And Temperature Controlled Cabinet Mode
- **기본 클러스터**: Mode Base
- **기능**: One or more core modes are supported
- **지원하는 모드**: 
  - Auto (0x0000)
  - Quick (0x0001)
  - Quiet (0x0002)
  - LowNoise (0x0003)
  - LowEnergy (0x0004)
  - Vacation (0x0005)
  - Min (0x0006)
  - Max (0x0007)
  - Night (0x0008)
  - Day (0x0009)
  - RapidCool (0x4000)
  - RapidFreeze (0x4001)

## SDK 정의
### 열거형
#### ModeTag
- **값**: 
  - 0x0000 - Auto
  - 0x0001 - Quick
  - 0x0002 - Quiet
  - 0x0003 - LowNoise
  - 0x0004 - LowEnergy
  - 0x0005 - Vacation
  - 0x0006 - Min
  - 0x0007 - Max
  - 0x0008 - Night
  - 0x0009 - Day
  - 0x4000 - RapidCool
  - 0x4001 - RapidFreeze

### 속성
- **SupportedModes**: array, ModeOptionStruct, length=255, minLength=2
- **CurrentMode**: int8u
- **CoreModeTags**: array, enum16, length=16, minLength=1, optional=true

### 명령
- **ChangeToMode**
  - **소스**: client
  - **응답**: ChangeToModeResponse
  - **설명**: 이 명령은 장치 모드를 변경하는 데 사용됩니다.
  - **인수**: 
    - NewMode (type: int8u)

- **ChangeToModeResponse**
  - **소스**: server
  - **설명**: ChangeToMode 명령 수신 후 장치에서 전송되는 명령입니다.
  - **인수**: 
    - Status (type: enum8)
    - StatusText (type: char_string, length=64, optional=true)

- **ChangeToModeByCoreTag**
  - **소스**: client
  - **응답**: ChangeToModeResponse
  - **설명**: 이 명령은 장치의 모드를 주어진 모드 태그 값을 포함하는 태그 목록 중 하나로 변경하는 데 사용됩니다.
  - **인수**: 
    - NewModeTag (type: enum16)

## 구현
Refrigerator And Temperature Controlled Cabinet Mode 클러스터는 기기에서 지원하는 다양한 모드를 선택하고 변경하는 기능을 제공합니다. 이는 냉장고와 온도 조절 캐비닛의 운영에 유용합니다. 명령과 속성이 잘 정의되어 있어, 호환되는 장치 간에 일관된 동작을 보장합니다.

## 예시
- 특정 모드로 전환하기 위해 ChangeToMode 명령을 사용하고, 이에 응답하기 위해 ChangeToModeResponse 명령을 통해 장치 상태를 전달합니다.

## 관련 문서
- [Mode Base 클러스터 문서](<linked_document_url>)
- [Connected Home over IP 사양](<linked_document_url>)