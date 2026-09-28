---
entity: Refrigerator Alarm
ids: ['0x0057']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml', 'src/app/clusters/alarm-base-server/README.md', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp', 'src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h', 'data_model/1.7/clusters/RefrigeratorAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Refrigerator Alarm은 냉장고의 알람을 구성하는 속성과 명령을 포함하는 클러스터입니다. 이 클러스터는 어플라이언스 도메인에 속하며, 클러스터 ID는 0x0057입니다.

## 스펙
Refrigerator Alarm 클러스터는 다음과 같은 속성 및 이벤트를 정의합니다.

### 속성
- **Mask** (`0x0000`): 알람 비트 마스크 (유형: AlarmBitmap)
- **State** (`0x0002`): 현재 알람 상태 (유형: AlarmBitmap)
- **Supported** (`0x0003`): 지원되는 알람 (유형: AlarmBitmap)
- **고유 속성** (`0xFFFD`): 모든 측에 대해 적용 (값: 1)

### 이벤트
- **Notify** (`0x00`): 하나 이상의 알람 상태가 변경될 때 발생합니다.
  - **Active**: 현재 활성화된 알람 비트 (유형: AlarmBitmap)
  - **Inactive**: 현재 비활성화된 알람 비트 (유형: AlarmBitmap)
  - **State**: 현재 알람 상태 (유형: AlarmBitmap)
  - **Mask**: 알람 비트 마스크 (유형: AlarmBitmap)

## SDK 정의
Refrigerator Alarm 클러스터에 대한 SDK에서는 다음과 같은 인터페이스가 정의되어 있습니다.

### 클래스: `RefrigeratorAlarmServer`
- **정적 메서드**
  - `static RefrigeratorAlarmServer & Instance()`: Singleton 인스턴스를 반환합니다.
  - `GetMaskValue(chip::EndpointId endpoint, chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> * mask)`: 알람 비트 마스크를 가져옵니다.
  - `GetStateValue(chip::EndpointId endpoint, chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> * state)`: 현재 알람 상태를 가져옵니다.
  - `GetSupportedValue(chip::EndpointId endpoint, chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> * supported)`: 지원되는 알람을 가져옵니다.
  - `SetMaskValue(chip::EndpointId endpoint, const chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> mask)`: 알람 마스크를 설정합니다.
  - `SetStateValue(chip::EndpointId endpoint, chip::BitMask<chip::app::Clusters::RefrigeratorAlarm::AlarmMap> newState)`: 알람 상태를 설정합니다.

### 속성 네임스페이스
- **Namespace: `Attributes`**
  - **Mask**
    - `Get(EndpointId endpoint, BitMask<AlarmMap> * value)`
    - `Set(EndpointId endpoint, BitMask<AlarmMap> value)`
  - **State**
    - `Get(EndpointId endpoint, BitMask<AlarmMap> * value)`
    - `Set(EndpointId endpoint, BitMask<AlarmMap> value)`
  - **Supported**
    - `Get(EndpointId endpoint, BitMask<AlarmMap> * value)`

## 구현
Refrigerator Alarm 클러스터는 `AlarmBaseCluster`를 상속받으며, 사용자가 정의한 `RefrigeratorAlarmCluster`를 통해 알람 상태와 이벤트를 관리합니다.

### 주요 구현 파일
- **RefrigeratorAlarmCluster.h**: 클러스터의 기본 정의가 포함됩니다.
- **RefrigeratorAlarmCluster.cpp**: 클러스터의 주요 기능 및 이벤트 처리 함수가 구현됩니다.
- **CodegenIntegration.h/cpp**: 클러스터 인스턴스의 등록 및 관리 기능이 포함됩니다.
- **refrigerator-alarm-server.h**: 구현 세부 정보를 포함하는 헤더 파일입니다.

## 예시
Refrigerator Alarm 클러스터를 사용하려면 클러스터 인스턴스를 생성하고, 이벤트를 관리하는 데 필요한 함수를 호출하여 활성화합니다. 예를 들어, 알람 상태를 변경하려면 `SetStateValue` 함수를 사용합니다.

```cpp
RefrigeratorAlarmServer::Instance().SetStateValue(endpointId, newState);
```

## 관련 문서
- [Alarm Base and its derivations](src/app/clusters/alarm-base-server/README.md)
- [Refrigerator Alarm XML specification](data_model/1.7/clusters/RefrigeratorAlarm.xml)