---
entity: Temperature Alarm
ids: ['0x0064']
source_paths: ['data_model/1.7/clusters/TemperatureAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Temperature Alarm Cluster는 온도 측정이 특정 임계값을 초과하거나 미만일 때 경고를 알리기 위한 기능을 제공합니다. 이 클러스터는 Alarm Base를 상속받아 사용됩니다.

## 스펙
- 클러스터 ID: `0x0064`
- 클러스터 이름: Temperature Alarm
- 리비전: 1

### 기능
- **OverTemperature**: 온도 측정이 임계값을 초과할 때 알람 활성화
- **UnderTemperature**: 온도 측정이 임계값 이하일 때 알람 활성화
- **MajorThreshold**: 주요 임계값 지원
- **MinorThreshold**: 최소 임계값 지원
- **OverCriticalAdjustable**: 과도한 임계 온도 조정 기능
- **OverMajorAdjustable**: 과도한 주요 온도 조정 기능
- **OverMinorAdjustable**: 과도한 최소 온도 조정 기능
- **UnderMinorAdjustable**: 부족한 최소 온도 조정 기능
- **UnderMajorAdjustable**: 부족한 주요 온도 조정 기능
- **UnderCriticalAdjustable**: 부족한 임계 온도 조정 기능

### 데이터 타입
- **AlarmBitmap**:
  - CriticalOverTemperatureAlarm (bit 0): 측정된 온도가 임계값을 초과
  - MajorOverTemperatureAlarm (bit 1): 측정된 온도가 주요 임계값을 초과
  - MinorOverTemperatureAlarm (bit 2): 측정된 온도가 최소 임계값을 초과
  - MinorUnderTemperatureAlarm (bit 3): 측정된 온도가 최소 임계값 이하
  - MajorUnderTemperatureAlarm (bit 4): 측정된 온도가 주요 임계값 이하
  - CriticalUnderTemperatureAlarm (bit 5): 측정된 온도가 임계값 이하

## SDK 정의
### 속성
- **CriticalOverTemperatureThreshold** (id: `0x0080`): 과도한 온도 임계값
- **MajorOverTemperatureThreshold** (id: `0x0081`): 주요 온도 임계값
- **MinorOverTemperatureThreshold** (id: `0x0082`): 최소 온도 임계값
- **MinorUnderTemperatureThreshold** (id: `0x0083`): 부족한 최소 온도 임계값
- **MajorUnderTemperatureThreshold** (id: `0x0084`): 부족한 주요 온도 임계값
- **CriticalUnderTemperatureThreshold** (id: `0x0085`): 부족한 임계 온도

### 명령어
- **SetTemperatureAlarmThresholds** (id: `0x80`): 온도 경고 임계값 설정 명령어

## 구현
Temperature Alarm Cluster는 클러스터 ID `0x0064`를 사용하며, 해당 클러스터는 온도와 관련된 경고 임계값을 설정하고 조정하는 기능을 구현합니다. 각 속성과 명령어는 필드의 제약 조건 및 해당 기능에 대한 요구 사항을 포함 합니다.

## 예시
```xml
<command id="0x80" name="SetTemperatureAlarmThresholds">
  ...
</command>
```

## 관련 문서
- [Connectivity Standards Alliance](https://www.csa-iot.org)