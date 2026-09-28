---
entity: Thermostat Mode
ids: ['0x0063']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml', 'src/app/clusters/mode-base-server/README.md', 'data_model/1.7/clusters/Mode_Thermostat.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Thermostat Mode 클러스터는 Mode Base 클러스터에서 파생된 클러스터로, 온도조절 장치에 대해 추가적인 모드 태그 및 이름이 지정된 열거형 값을 정의합니다.

## 스펙
### Thermostat Mode Cluster
- **Cluster ID**: 0x0063
- **Classification**: Derived from Mode Base
- **Features**:
  - **OnOff**: Dependency with the OnOff cluster (disallowed conform)
  - **CoreModes**

#### Data Types
- **enum ModeTag**:
  - Auto: 0x0000
  - Quick: 0x0001
  - Quiet: 0x0002
  - LowNoise: 0x0003
  - LowEnergy: 0x0004
  - Vacation: 0x0005
  - Min: 0x0006
  - Max: 0x0007
  - Night: 0x0008
  - Day: 0x0009
  - Off: 0x4000
  - Cool: 0x4001
  - Heat: 0x4002
  - EmergencyHeat: 0x4003

- **struct ModeOptionStruct**:
  - Label (char_string, length=64)
  - Mode (int8u)
  - ModeTags (array of ModeTagStruct, length=8, minLength=1)

### Attributes
- **SupportedModes** (0x0000): Array of ModeOptionStruct (length=255, minLength=2)
- **CurrentMode** (0x0001): int8u
- **StartUpMode** (0x0002): int8u, nullable=True, writable=True, optional=True
- **CoreModeTags** (0x0004): Array of enum16 (length=16, minLength=1, optional=True)

### Commands
- **ChangeToMode** (0x00): 
  - Description: This command is used to change device modes.
  - Arg: NewMode (int8u)

- **ChangeToModeResponse** (0x01): 
  - Description: This command is sent by the device on receipt of the ChangeToMode command.
  - Args: Status (enum8), StatusText (char_string, optional, length=64)

- **ChangeToModeByCoreTag** (0x02, optional): 
  - Description: This command is used to change the mode of the device to one of the modes with a tag list that includes the given mode tag value.
  - Arg: NewModeTag (enum16, apiMaturity=provisional)

## SDK 정의
### Mode Base 및 별칭
Mode Base는 클러스터 ID가 없는 가상 클러스터로, 다른 클러스터에서 파생되기 위해 존재합니다.

### Mode Base 파생 클러스터 사용 방법
1. `ModeBase::Delegate` 클래스를 상속하는 클래스를 생성합니다.
2. `GetModeLabelByIndex`, `GetModeValueByIndex`, `GetModeTagsByIndex`, `HandleChangeToMode` 메소드를 구현합니다.
3. 선택적으로 `Init` 함수를 구현합니다.
4. `.c` 또는 `.cpp` 파일에서 `ModeBase::Instance`를 상속한 클래스를 인스턴스화합니다.
5. `Server::Init()` 호출 후 인스턴스의 `.Init()` 함수를 호출합니다.
6. 혹은 마지막 두 단계를 `emberAf<ClusterName>ClusterInitCallback` 함수에서 수행할 수 있습니다.
7. `chip_device_project_config_include` 파일에 `#define MATTER_DM_PLUGIN_MODE_BASE`를 추가합니다.

**중요**: 이러한 클러스터에 대한 Zap 접근자 함수는 존재하지 않습니다. 인스턴스의 `Update...`와 `Get...` 함수를 사용하여 속성에 접근합니다.

### 새로운 파생 클러스터 추가 방법
1. 스펙을 XML로 변환하여 `src/app/zap-templates/zcl/data-model/chip`에 추가합니다.
2. Zap 코드를 재생성합니다.
3. 모든 클러스터 앱 예제에 새 클러스터를 포함시키도록 확장합니다.

## 구현
(해당 역할에 대한 구현 정보는 제공되지 않았습니다.)

## 예시
(해당 역할에 대한 예시 정보는 제공되지 않았습니다.)

## 관련 문서
- `src/app/clusters/mode-base-server/README.md`
- `src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml`