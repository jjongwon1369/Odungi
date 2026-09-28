---
entity: Laundry Washer Mode
ids: ['0x0051']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml', 'data_model/1.7/clusters/Mode_LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Laundry Washer Mode 클러스터는 지원되는 모드 목록에서 선택하기 위한 속성과 명령을 정의합니다. 해당 클러스터는 다양한 세탁기 작동 모드를 지원하도록 설계되었습니다.

## 스펙
### Laundry Washer Mode Cluster
- **ID**: 0x0051
- **이름**: Laundry Washer Mode
- **분류**: Derived
- **기본 클러스터**: Mode Base
- **기능**:
  - **OnOff**: OnOff 클러스터와의 종속성 (비허용)

### ModeTag Enum
- **0x0000**: Auto
- **0x0001**: Quick
- **0x0002**: Quiet
- **0x0003**: LowNoise
- **0x0004**: LowEnergy
- **0x0005**: Vacation
- **0x0006**: Min
- **0x0007**: Max
- **0x0008**: Night
- **0x0009**: Day
- **0x4000**: Normal
- **0x4001**: Delicate
- **0x4002**: Heavy
- **0x4003**: Whites

## SDK 정의
### 클러스터 정의
- **클러스터 코드**: LAUNDRY_WASHER_MODE_CLUSTER
- **클라이언트**: true
- **서버**: true
- **설명**: Attributes and commands for selecting a mode from a list of supported options.

### 속성
- **SupportedModes**: 배열, 입력 타입: ModeOptionStruct, 최대 길이: 255 (최소 길이: 2)
- **CurrentMode**: int8u
- **CoreModeTags**: 배열, 입력 타입: enum16, 최대 길이: 16 (최소 길이: 1, 비선택)

### 명령
- **ChangeToMode**
  - **소스**: client
  - **코드**: 0x00
  - **인자**: NewMode (type: int8u)

- **ChangeToModeResponse**
  - **소스**: server
  - **코드**: 0x01
  - **인자**: Status (type: enum8), StatusText (type: char_string, 길이: 64, 선택)

- **ChangeToModeByCoreTag**
  - **소스**: client
  - **코드**: 0x02
  - **인자**: NewModeTag (type: enum16, 비선택)

## 구현
이 클러스터를 구현하기 위해서는 속성과 명령을 정의하고 해당 모드 선택 기능을 지원해야 합니다. 클러스터의 각 속성과 명령은 SDK가 정의한 형식 및 제약 조건을 충족해야 합니다.

## 예시
다양한 모드 옵션을 제공하고, 사용자가 선호하는 모드로 변경할 수 있는 예시로는 다음과 같은 것이 있습니다:

1. 사용자가 세탁기에서 "Quiet" 모드를 선택하는 경우:
   - **ChangeToMode** 명령과 함께 NewMode 인자로 해당 모드 값을 전송.
   
2. 세탁기가 "Heavy" 모드를 지원하고 이를 현재 모드로 설정하기 위해 사용자가 CoreModeTags를 통해 변경 요청을 하는 경우:
   - **ChangeToModeByCoreTag** 명령과 함께 NewModeTag 인자로 해당 태그 값을 전송.

## 관련 문서
- [Connectivity Standards Alliance](https://www.csa-iot.org)