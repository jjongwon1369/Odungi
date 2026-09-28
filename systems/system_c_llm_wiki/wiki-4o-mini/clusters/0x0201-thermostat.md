---
entity: Thermostat
ids: ['0x0201']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml', 'src/app/clusters/thermostat-server/ThermostatDelegate.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.h', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp', 'src/app/clusters/thermostat-server/CodegenIntegration.h', 'src/app/clusters/thermostat-server/ThermostatDelegate.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SetpointRange.h', 'src/app/clusters/thermostat-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp', 'src/app/clusters/thermostat-server/Setpoint.h', 'src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/Setpoint.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h', 'src/app/clusters/thermostat-server/Setpoints.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.h', 'src/app/clusters/thermostat-server/Temperature.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h', 'src/app/clusters/thermostat-server/AttributeAccessorShim.h', 'src/app/clusters/thermostat-server/DelegateResolution.h', 'src/app/clusters/thermostat-server/ThermostatCluster.h', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterRead.cpp', 'src/app/clusters/thermostat-server/SetpointLimits.h', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h', 'src/app/clusters/thermostat-server/AttributeAccessorShim.cpp', 'src/app/clusters/thermostat-server/Setpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp', 'data_model/1.7/clusters/Thermostat.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Thermostat 클러스터는 온도 조절 장치를 구성하고 제어하는 인터페이스를 제공합니다. 이 클러스터는 난방, 냉방, 점유 상태 및 예약 기능을 포함하여 사용자 환경을 최적화하는 데 필요한 다양한 기능을 지원합니다.

## 스펙
- 클러스터 ID: `0x0201`
- 관련된 기능:
  - Heating (`0x00`)
  - Cooling (`0x01`)
  - Occupancy (`0x02`)
  - ScheduleConfiguration (`0x03`)
  - Setback (`0x04`)
  - AutoMode (`0x05`)
  - LocalTemperatureNotExposed (`0x06`)
  - MatterScheduleConfiguration (`0x07`)
  - Presets (`0x08`)
  - Events (`0x09`)
  - ThermostatSuggestions (`0x10`)
  - ThermostatSensors (`0x11`)

## SDK 정의
- 속성:
  - `LocalTemperature` (온도)
  - `OutdoorTemperature` (온도)
  - `Occupancy` (BitMap)
  - `AbsMinHeatSetpointLimit` (온도)
  - `AbsMaxHeatSetpointLimit` (온도)
  - `AbsMinCoolSetpointLimit` (온도)
  - `AbsMaxCoolSetpointLimit` (온도)
  - `OccupiedCoolingSetpoint` (온도)
  - `OccupiedHeatingSetpoint` (온도)
  - `UnoccupiedCoolingSetpoint` (온도)
  - `UnoccupiedHeatingSetpoint` (온도)
  - `MinHeatSetpointLimit` (온도)
  - `MaxHeatSetpointLimit` (온도)
  - `MinCoolSetpointLimit` (온도)
  - `MaxCoolSetpointLimit` (온도)
  - `MinSetpointDeadBand` (온도)
  - `RemoteSensing` (BitMap)
  - `ControlSequenceOfOperation` (열거형)
  - `SystemMode` (열거형)
  - `ThermostatRunningMode` (열거형)
  - `TemperatureSetpointHold` (열거형)
  - `TemperatureSetpointHoldDuration` (정수)
  
- 명령:
  - `SetpointRaiseLower`
  - `SetWeeklySchedule`
  - `GetWeeklySchedule`
  - `ClearWeeklySchedule`
  - `SetActiveScheduleRequest`
  - `SetActivePresetRequest`

- 이벤트:
  - `SystemModeChange`
  - `LocalTemperatureChange`
  - `OccupancyChange`
  - `SetpointChange`
  - `RunningStateChange`
  - `RunningModeChange`
  - `ActiveScheduleChange`
  - `ActivePresetChange`

## 구현
Thermostat 클러스터는 ThermostatClusterBase 클래스를 상속하고, 다양한 속성과 명령을 처리하기 위해 Delegate 클래스를 구현합니다. 각 기능은 객체 지향적으로 구분되어 있으며, 특정 기능을 활성화하는 delegate를 사용하여 지원됩니다.

## 예시
예를 들어, `SetpointRaiseLower` 명령을 사용하여 현재 온도 설정을 증가시키거나 감소시킬 수 있습니다.

```cpp
Thermostat::Request::SetpointRaiseLower::DecodableType commandData;
commandData.mode = SetpointRaiseLowerModeEnum::kHeat;
commandData.amount = 2;

// 명령을 호출하여 온도를 조절합니다.
thermostatCluster.InvokeCommand(commandData);
```

## 관련 문서
- [Matter Cluster Spec](https://github.com/project-chip/connectedhomeip/tree/master/docs/spec)
- [Thermostat Cluster Implementation](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/thermostat-server)