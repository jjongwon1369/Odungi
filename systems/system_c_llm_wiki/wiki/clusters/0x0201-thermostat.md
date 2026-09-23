---
entity: Thermostat
ids: ['0x0201']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml', 'src/app/clusters/thermostat-server/ThermostatDelegate.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.h', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp', 'src/app/clusters/thermostat-server/CodegenIntegration.h', 'src/app/clusters/thermostat-server/ThermostatDelegate.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SetpointRange.h', 'src/app/clusters/thermostat-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp', 'src/app/clusters/thermostat-server/Setpoint.h', 'src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/Setpoint.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h', 'src/app/clusters/thermostat-server/Setpoints.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.h', 'src/app/clusters/thermostat-server/Temperature.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h', 'src/app/clusters/thermostat-server/AttributeAccessorShim.h', 'src/app/clusters/thermostat-server/DelegateResolution.h', 'src/app/clusters/thermostat-server/ThermostatCluster.h', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterRead.cpp', 'src/app/clusters/thermostat-server/SetpointLimits.h', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h', 'src/app/clusters/thermostat-server/AttributeAccessorShim.cpp', 'src/app/clusters/thermostat-server/Setpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp', 'data_model/1.7/clusters/Thermostat.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

- 클러스터: `Thermostat`
- 도메인: `HVAC`
- Cluster ID: `0x0201`
- Define: `THERMOSTAT_CLUSTER`
- PICS: `TSTAT`
- 스펙 revision: `12`
- 설명: 온도 조절기의 기능을 구성하고 제어하기 위한 인터페이스
- Client 및 Server를 모두 지원한다.
- 주요 기능:
  - `Heating` (`HEAT`)
  - `Cooling` (`COOL`)
  - `Occupancy` (`OCC`)
  - `AutoMode` (`AUTO`)
  - `LocalTemperatureNotExposed` (`LTNE`)
  - `MatterScheduleConfiguration` (`MSCH`)
  - `Presets` (`PRES`)
  - `Events` (`TEVT`)
  - `ThermostatSuggestions` (`TSUGGEST`)
  - `ThermostatSensors` (`SENSORS`)
- `ThermostatSuggestions` (`TSUGGEST`)는 `Presets` (`PRES`) 기능을 요구한다.
- SDK 생성 정보:
  - Git: `0.9-1.7-winter2027`
  - Alchemy: `v1.7.10`
  - 원본: `src/app_clusters/Thermostat.adoc`

## 스펙

### Features

| Bit | Code | Name | 설명 |
|---:|---|---|---|
| 0 | `HEAT` | `Heating` | 난방 장치 관리 |
| 1 | `COOL` | `Cooling` | 냉방 장치 관리 |
| 2 | `OCC` | `Occupancy` | `Occupied` 및 `Unoccupied` setpoint 지원 |
| 3 | `SCH` | `ScheduleConfiguration` | obsolete |
| 4 | `SB` | `Setback` | obsolete |
| 5 | `AUTO` | `AutoMode` | `SystemMode`의 `Auto` 지원 |
| 6 | `LTNE` | `LocalTemperatureNotExposed` | `LocalTemperature` 값을 노출하지 않음 |
| 7 | `MSCH` | `MatterScheduleConfiguration` | 향상된 schedule 지원 |
| 8 | `PRES` | `Presets` | setpoint preset 지원 |
| 9 | `TEVT` | `Events` | 이벤트 지원 |
| 10 | `TSUGGEST` | `ThermostatSuggestions` | suggestion 지원 |
| 11 | `SENSORS` | `ThermostatSensors` | sensor scheduling 지원 |

`HEAT` 또는 `COOL`이 사용되는 경우 `AUTO`에 대한 적합성 조건이 적용된다. `TEVT` 및 `SENSORS`는 provisional 기능이다.

### Attributes

| ID | Name | Type | 주요 조건 |
|---|---|---|---|
| `0x0000` | `LocalTemperature` | `temperature` | nullable, mandatory |
| `0x0001` | `OutdoorTemperature` | `temperature` | nullable, optional |
| `0x0002` | `Occupancy` | `OccupancyBitmap` | `OCC` 필요 |
| `0x0003` | `AbsMinHeatSetpointLimit` | `temperature` | `HEAT`, 기본값 `700` |
| `0x0004` | `AbsMaxHeatSetpointLimit` | `temperature` | `HEAT`, 기본값 `3000` |
| `0x0005` | `AbsMinCoolSetpointLimit` | `temperature` | `COOL`, 기본값 `1600` |
| `0x0006` | `AbsMaxCoolSetpointLimit` | `temperature` | `COOL`, 기본값 `3200` |
| `0x0007` | `PICoolingDemand` | `int8u` | obsolete |
| `0x0008` | `PIHeatingDemand` | `int8u` | obsolete |
| `0x0009` | `HVACSystemTypeConfiguration` | `HVACSystemTypeBitmap` | obsolete |
| `0x0010` | `LocalTemperatureCalibration` | `int8s` | `LTNE`가 없을 때 optional |
| `0x0011` | `OccupiedCoolingSetpoint` | `temperature` | `COOL`, 기본값 `2600` |
| `0x0012` | `OccupiedHeatingSetpoint` | `temperature` | `HEAT`, 기본값 `2000` |
| `0x0013` | `UnoccupiedCoolingSetpoint` | `temperature` | `COOL` 및 `OCC` |
| `0x0014` | `UnoccupiedHeatingSetpoint` | `temperature` | `HEAT` 및 `OCC` |
| `0x0015` | `MinHeatSetpointLimit` | `temperature` | `HEAT` |
| `0x0016` | `MaxHeatSetpointLimit` | `temperature` | `HEAT` |
| `0x0017` | `MinCoolSetpointLimit` | `temperature` | `COOL` |
| `0x0018` | `MaxCoolSetpointLimit` | `temperature` | `COOL` |
| `0x0019` | `MinSetpointDeadBand` | `int8s` | `AUTO`, 범위 `0`~`127` |
| `0x001A` | `RemoteSensing` | `RemoteSensingBitmap` | optional |
| `0x001B` | `ControlSequenceOfOperation` | `ControlSequenceOfOperationEnum` | mandatory |
| `0x001C` | `SystemMode` | `SystemModeEnum` | mandatory |
| `0x001E` | `ThermostatRunningMode` | `ThermostatRunningModeEnum` | `AUTO` 또는 `TEVT` 조건 |
| `0x0020` | `StartOfWeek` | `StartOfWeekEnum` | obsolete |
| `0x0021` | `NumberOfWeeklyTransitions` | `int8u` | obsolete |
| `0x0022` | `NumberOfDailyTransitions` | `int8u` | obsolete |
| `0x0023` | `TemperatureSetpointHold` | `TemperatureSetpointHoldEnum` | optional |
| `0x0024` | `TemperatureSetpointHoldDuration` | `int16u` | nullable, `1`~`1440` |
| `0x0025` | `ThermostatProgrammingOperationMode` | `ProgrammingOperationModeBitmap` | obsolete |
| `0x0029` | `ThermostatRunningState` | `RelayStateBitmap` | optional |
| `0x0030` | `SetpointChangeSource` | `SetpointChangeSourceEnum` | optional |
| `0x0031` | `SetpointChangeAmount` | `int16s` | nullable, optional |
| `0x0032` | `SetpointChangeSourceTimestamp` | `epoch_s` | optional |
| `0x0034`~`0x0039` | `OccupiedSetback`, `OccupiedSetbackMin`, `OccupiedSetbackMax`, `UnoccupiedSetback`, `UnoccupiedSetbackMin`, `UnoccupiedSetbackMax` | `int8u` | obsolete |
| `0x003A` | `EmergencyHeatDelta` | `int8u` | optional |
| `0x0040` | `ACType` | `ACTypeEnum` | optional |
| `0x0041` | `ACCapacity` | `int16u` | optional |
| `0x0042` | `ACRefrigerantType` | `ACRefrigerantTypeEnum` | optional |
| `0x0043` | `ACCompressorType` | `ACCompressorTypeEnum` | optional |
| `0x0044` | `ACErrorCode` | `ACErrorCodeBitmap` | optional |
| `0x0045` | `ACLouverPosition` | `ACLouverPositionEnum` | optional |
| `0x0046` | `ACCoilTemperature` | `temperature` | nullable, optional |
| `0x0047` | `ACCapacityFormat` | `ACCapacityFormatEnum` | optional |
| `0x0048` | `PresetTypes` | list of `PresetTypeStruct` | `PRES` |
| `0x0049` | `ScheduleTypes` | list of `ScheduleTypeStruct` | `MSCH` |
| `0x004A` | `NumberOfPresets` | `int8u` | `PRES`, 최소 `1` |
| `0x004B` | `NumberOfSchedules` | `int8u` | `MSCH`, 최소 `1` |
| `0x004C` | `NumberOfScheduleTransitions` | `int8u` | `MSCH`, 최소 `1` |
| `0x004D` | `NumberOfScheduleTransitionPerDay` | `int8u` | `MSCH`, nullable |
| `0x004E` | `ActivePresetHandle` | `octet_string` | `PRES`, nullable, 최대 16 bytes |
| `0x004F` | `ActiveScheduleHandle` | `octet_string` | `MSCH`, nullable, 최대 16 bytes |
| `0x0050` | `Presets` | list of `PresetStruct` | `PRES`, atomic write |
| `0x0051` | `Schedules` | list of `ScheduleStruct` | `MSCH`, atomic write |
| `0x0052` | `SetpointHoldExpiryTimestamp` | `epoch_s` | nullable, optional |
| `0x0053` | `MaxThermostatSuggestions` | `int8u` | `TSUGGEST`, 최소 `5` |
| `0x0054` | `ThermostatSuggestions` | list of `ThermostatSuggestionStruct` | `TSUGGEST` |
| `0x0055` | `CurrentThermostatSuggestion` | `ThermostatSuggestionStruct` | nullable, `TSUGGEST` |
| `0x0056` | `ThermostatSuggestionNotFollowingReason` | `ThermostatSuggestionNotFollowingReasonBitmap` | nullable, `TSUGGEST` |
| `0x0057` | `CriticalFreezeProtection` | `boolean` | provisional, `HEAT` |
| `0x0058` | `CriticalOverheatProtection` | `boolean` | provisional, `COOL` |
| `0x0059` | `Sensors` | list of `ThermostatSensorStruct` | provisional, `SENSORS`, 최대 32 |
| `0x005A` | `AvailableSensorHandles` | list of `octet_string` | provisional, `SENSORS`, 최대 32 |
| `0x005B` | `EnabledSensorHandles` | list of `octet_string` | provisional, `SENSORS`, 최대 32 |
| `0x005C` | `NumberOfSensorScheduleTransitions` | `int8u` | provisional, `SENSORS` |
| `0x005D` | `SensorSchedule` | list of `SensorScheduleTransitionStruct` | provisional, `SENSORS`, atomic write |

### 주요 Data Types

#### Enum

- `SystemModeEnum`
  - `Off = 0x00`
  - `Auto = 0x01`
  - `Cool = 0x03`
  - `Heat = 0x04`
  - `EmergencyHeat = 0x05`
  - `Precooling = 0x06`
  - `FanOnly = 0x07`
  - `Dry = 0x08`
  - `Sleep = 0x09`
- `ThermostatRunningModeEnum`: `Off`, `Cool`, `Heat`
- `ControlSequenceOfOperationEnum`: `CoolingOnly`, `CoolingWithReheat`, `HeatingOnly`, `HeatingWithReheat`, `CoolingAndHeating`, `CoolingAndHeatingWithReheat`
- `TemperatureSetpointHoldEnum`: `SetpointHoldOff`, `SetpointHoldOn`
- `SetpointRaiseLowerModeEnum`: `Heat`, `Cool`, `Both`
- `StartOfWeekEnum`: `Sunday`~`Saturday`
- `PresetScenarioEnum`: `Occupied`, `Unoccupied`, `Sleep`, `Wake`, `Vacation`, `GoingToSleep`, `UserDefined`
- `SetpointChangeSourceEnum`: `Manual`, `Schedule`, `External`
- `ACCapacityFormatEnum`: `BTUh`
- `ACCompressorTypeEnum`: `Unknown`, `T1`, `T2`, `T3`
- `ACLouverPositionEnum`: `Closed`, `Open`, `Quarter`, `Half`, `ThreeQuarters`
- `ACRefrigerantTypeEnum`: `Unknown`, `R22`, `R410a`, `R407c`
- `ACTypeEnum`: `Unknown`, `CoolingFixed`, `HeatPumpFixed`, `CoolingInverter`, `HeatPumpInverter`

#### Bitmap

- `OccupancyBitmap`: `Occupied`
- `RemoteSensingBitmap`: `LocalTemperature`, `OutdoorTemperature`, `Occupancy`
- `RelayStateBitmap`: `Heat`, `Cool`, `Fan`, `HeatStage2`, `CoolStage2`, `FanStage2`, `FanStage3`
- `ScheduleDayOfWeekBitmap`: `Sunday`, `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Away`
- `ScheduleModeBitmap`: `HeatSetpointPresent`, `CoolSetpointPresent`
- `ScheduleTypeFeaturesBitmap`: `SupportsPresets`, `SupportsSetpoints`, `SupportsNames`, `SupportsOff`
- `PresetTypeFeaturesBitmap`: `Automatic`, `SupportsNames`
- `ThermostatSuggestionNotFollowingReasonBitmap`: `DemandResponseEvent`, `OngoingHold`, `Schedule`, `Occupancy`, `VacationMode`, `TimeOfUseCostSavings`, `PreCoolingOrPreHeating`, `ConflictingSuggestions`
- `ACErrorCodeBitmap`: `CompressorFail`, `RoomSensorFail`, `OutdoorSensorFail`, `CoilSensorFail`, `FanFail`
- `HVACSystemTypeBitmap`: `CoolingStage`, `HeatingStage`, `HeatingIsHeatPump`, `HeatingUsesFuel`
- `ProgrammingOperationModeBitmap`: `ScheduleActive`, `AutoRecovery`, `Economy`

#### Struct

- `PresetStruct`
  - `PresetHandle`: 최대 16 bytes, nullable
  - `PresetScenario`
  - `Name`: 최대 64 bytes, nullable, optional
  - `CoolingSetpoint`
  - `HeatingSetpoint`
  - `BuiltIn`
- `PresetTypeStruct`
  - `PresetScenario`
  - `NumberOfPresets`
  - `PresetTypeFeatures`
- `ScheduleStruct`
  - `ScheduleHandle`
  - `SystemMode`
  - `Name`
  - `PresetHandle`
  - `Transitions`
  - `BuiltIn`
- `ScheduleTransitionStruct`
  - `DayOfWeek`
  - `TransitionTime`: 최대 `1439`
  - `PresetHandle`
  - `SystemMode`
  - `CoolingSetpoint`
  - `HeatingSetpoint`
- `ScheduleTypeStruct`
  - `SystemMode`
  - `NumberOfSchedules`
  - `ScheduleTypeFeatures`
- `SensorScheduleTransitionStruct`
  - `DayOfWeek`
  - `TransitionTime`: 최대 `1439`
  - `EnabledSensorHandles`: 최대 32개
- `ThermostatSensorStruct`
  - `Name`: 최대 64 bytes
  - `SensorHandle`: 최대 16 bytes
  - `Cluster`
  - `Endpoint`
  - `Node`
  - `FabricIndex`
- `ThermostatSuggestionStruct`
  - `UniqueID`
  - `PresetHandle`: 최대 16 bytes
  - `EffectiveTime`
  - `ExpirationTime`
- `WeeklyScheduleTransitionStruct`
  - `TransitionTime`: 최대 `1439`
  - nullable `HeatSetpoint`
  - nullable `CoolSetpoint`

### Commands

| ID | 방향 | Command | 설명 |
|---|---|---|---|
| `0x00` | client → server | `SetpointRaiseLower` | setpoint을 올리거나 내림 |
| `0x01` | client → server | `SetWeeklySchedule` | weekly schedule 갱신, obsolete |
| `0x02` | client → server | `GetWeeklySchedule` | weekly schedule 조회, obsolete |
| `0x00` | server → client | `GetWeeklyScheduleResponse` | weekly schedule 응답, obsolete |
| `0x02` | server → client | `AddThermostatSuggestionResponse` | `AddThermostatSuggestion` 응답 |
| `0x03` | client → server | `ClearWeeklySchedule` | weekly schedule 삭제, obsolete |
| `0x05` | client → server | `SetActiveScheduleRequest` | active schedule 설정, `MSCH` |
| `0x06` | client → server | `SetActivePresetRequest` | active preset 설정, `PRES` |
| `0x07` | client → server | `AddThermostatSuggestion` | suggestion 추가, `TSUGGEST` |
| `0x08` | client → server | `RemoveThermostatSuggestion` | suggestion 삭제, `TSUGGEST` |

`SetpointRaiseLower`의 필드는 다음과 같다.

- `Mode`: `SetpointRaiseLowerModeEnum`
- `Amount`: `int8`

`AddThermostatSuggestion`의 필드는 다음과 같다.

- `PresetHandle`
- `EffectiveTime`
- `ExpirationInMinutes`: `30`~`1440`

### Events

| ID | Event | 조건 |
|---|---|---|
| `0x0000` | `SystemModeChange` | `SystemMode` 변경, `TEVT` |
| `0x0001` | `LocalTemperatureChange` | `LocalTemperature`가 크게 변경, `TEVT` 및 `LTNE` 미사용 |
| `0x0002` | `OccupancyChange` | `Occupancy` 변경, `TEVT` 및 `OCC` |
| `0x0003` | `SetpointChange` | setpoint 변경, `TEVT` |
| `0x0004` | `RunningStateChange` | `ThermostatRunningState` 변경, `TEVT` |
| `0x0005` | `RunningModeChange` | `ThermostatRunningMode` 변경, `TEVT` 및 `AUTO` |
| `0x0006` | `ActiveScheduleChange` | `ActiveScheduleHandle` 변경, `TEVT` 및 `MSCH` |
| `0x0007` | `ActivePresetChange` | `ActivePresetHandle` 변경, `TEVT` 및 `PRES` |

## SDK 정의

### 생성 파일

- `src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml`
- 원본 spec: `src/app_clusters/Thermostat.adoc`
- Cluster:
  - `name="Thermostat"`
  - `domain="HVAC"`
  - `code="0x0201"`
  - `define="THERMOSTAT_CLUSTER"`
- Global attribute:
  - `0xFFFD`
  - 값 `12`

### SDK 타입 정의

SDK는 다음 타입을 생성한다.

- Enum:
  - `SystemModeEnum`
  - `ThermostatRunningModeEnum`
  - `StartOfWeekEnum`
  - `ControlSequenceOfOperationEnum`
  - `TemperatureSetpointHoldEnum`
  - `SetpointRaiseLowerModeEnum`
  - `ACCapacityFormatEnum`
  - `ACCompressorTypeEnum`
  - `ACLouverPositionEnum`
  - `ACRefrigerantTypeEnum`
  - `ACTypeEnum`
  - `SetpointChangeSourceEnum`
  - `PresetScenarioEnum`
- Bitmap:
  - `ACErrorCodeBitmap`
  - `HVACSystemTypeBitmap`
  - `OccupancyBitmap`
  - `ProgrammingOperationModeBitmap`
  - `ScheduleTypeFeaturesBitmap`
  - `RelayStateBitmap`
  - `RemoteSensingBitmap`
  - `ScheduleDayOfWeekBitmap`
  - `ScheduleModeBitmap`
  - `PresetTypeFeaturesBitmap`
  - `ThermostatSuggestionNotFollowingReasonBitmap`
- Struct:
  - `SensorScheduleTransitionStruct`
  - `ThermostatSensorStruct`
  - `ThermostatSuggestionStruct`
  - `WeeklyScheduleTransitionStruct`
  - `ScheduleTypeStruct`
  - `PresetStruct`
  - `PresetTypeStruct`
  - `ScheduleStruct`
  - `ScheduleTransitionStruct`

## 구현

### 주요 구현 파일

- `src/app/clusters/thermostat-server/ThermostatCluster.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.cpp`
- `src/app/clusters/thermostat-server/ThermostatDelegate.h`
- `src/app/clusters/thermostat-server/ThermostatDelegate.cpp`
- `src/app/clusters/thermostat-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-server/CodegenIntegration.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterHold.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHold.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterPresets.h`
- `src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSensors.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp`

### `ThermostatCluster`

`ThermostatCluster<Delegates...>`는 delegate 타입을 기반으로 기능을 compile-time에 구성하는 variadic template이다.

주요 compile-time 플래그:

- `kHasHeating`
- `kHasCooling`
- `kHasPresets`
- `kHasHold`
- `kHasSuggestions`
- `kHasOccupancy`
- `kHasSensors`
- `kRequiresAtomicWrite`

제약 조건:

- `Thermostat::Delegate`가 반드시 포함되어야 한다.
- `ThermostatHeatingSetpoints::Delegate` 또는 `ThermostatCoolingSetpoints::Delegate` 중 하나 이상이 필요하다.
- `kHasSuggestions`가 활성화되면 `kHasPresets`도 활성화되어야 한다.

모든 기능이 포함된 별칭은 다음과 같다.

```cpp
using FullFeaturedThermostatCluster =
    ThermostatCluster<Thermostat::Delegate, ThermostatHeatingSetpoints::Delegate,
                      ThermostatCoolingSetpoints::Delegate, ThermostatAutoSetpoints::Delegate,
                      ThermostatHold::Delegate, ThermostatPresets::Delegate,
                      ThermostatSuggestions::Delegate, ThermostatOccupancy::Delegate,
                      ThermostatSensors::Delegate>;
```

### Delegate 인터페이스

`Thermostat::Delegate`는 기본 thermostat 동작을 제공한다.

필수 인터페이스에는 다음이 포함된다.

- `GetFabricTable()`
- `GetLocalTemperature()`
- `SetLocalTemperature()`
- `GetSystemMode()`
- `SetSystemMode()`
- `GetControlSequenceOfOperation()`
- `SetControlSequenceOfOperation()`
- `GetRunningMode()`
- `SetRunningMode()`
- `GetRunningState()`
- `SetRunningState()`
- `SetRemoteSensing()`

기본 구현에서 다음 메서드는 `Status::UnsupportedAttribute`를 반환한다.

- `Delegate::GetOutdoorTemperature()`
- `Delegate::GetRemoteSensing()`
- 난방 및 냉방 setpoint limit 관련 일부 getter/setter
- `ThermostatAutoSetpoints::Delegate::GetMinDeadband()`

### Setpoint 처리

`Setpoints`는 다음 상태를 관리한다.

- `absoluteHeatLimits`
- `absoluteCoolLimits`
- `userHeatLimits`
- `userCoolLimits`
- `occupiedRange`
- `unoccupiedRange`
- `deadBand`

기본값:

- `kDefaultAbsMinHeatSetpointLimit = 700`
- `kDefaultAbsMaxHeatSetpointLimit = 3000`
- `kDefaultAbsMinCoolSetpointLimit = 1600`
- `kDefaultAbsMaxCoolSetpointLimit = 3200`
- `kDefaultDeadBand = 200`
- `kDefaultHeatingSetpoint = 2000`
- `kDefaultCoolingSetpoint = 2600`
- `kDefaultLocalTemperatureCalibration = 0`
- `kMinDeadBand = 0`
- `kMaxDeadBand = 127`
- `kMaxTemperatureSetpointHoldDurationMin = 1440`

`Setpoints::Valid()`는 다음을 검증한다.

- absolute limit의 minimum이 maximum 이하인지 여부
- user limit가 absolute limit 범위 내에 있는지 여부
- occupied 및 unoccupied setpoint가 user limit 범위 내에 있는지 여부
- `AUTO` 사용 시 heat/cool deadband 충족 여부

`Setpoints::Fix()`는 필요한 경우 다음 값을 자동 조정한다.

- user limit
- heat/cool deadband
- occupied range
- unoccupied range

### `SetpointRaiseLower`

`ThermostatSetpointsBase::InvokeCommand()`는 `SetpointRaiseLower`를 처리한다.

- `Mode::kHeat`: 난방 setpoint 조정
- `Mode::kCool`: 냉방 setpoint 조정
- `Mode::kBoth`: 지원되는 난방 및 냉방 setpoint 조정
- `Amount`는 `temperature` 단위로 변환할 때 `request_data.amount * 10`을 사용한다.
- 변경 시 `Setpoints::ClampMode::kClamp`로 limit 범위에 맞춘다.
- 유효한 setpoint가 없으면 `Status::InvalidCommand`를 반환한다.

### Attribute 접근

`ThermostatClusterBase::ReadAttribute()`는 다음을 직접 처리한다.

- `ClusterRevision`
- `FeatureMap`
- `LocalTemperature`
- `OutdoorTemperature`
- `SystemMode`
- `ThermostatRunningMode`
- `ThermostatRunningState`
- `RemoteSensing`
- `ControlSequenceOfOperation`
- `LocalTemperatureCalibration`
- `Schedules`

`LTNE`가 활성화된 경우 `LocalTemperature`는 null로 encode되며, `RemoteSensing`에서 `LocalTemperature` bit가 제거된다.

`ThermostatClusterBase::WriteAttribute()`는 다음을 처리한다.

- `LocalTemperatureCalibration`
- `MinSetpointDeadBand`
- `RemoteSensing`
- `ControlSequenceOfOperation`
- `SystemMode`

`ControlSequenceOfOperation`에 대한 write는 호환성을 위해 유효한 요청이면 실제 변경 없이 `Status::Success`를 반환한다.

### Events 생성

`TEVT`가 활성화된 경우 attribute 변경 시 다음 메서드가 이벤트를 생성한다.

- `GenerateSystemModeChangeEvent()`
- `GenerateLocalTemperatureChangeEvent()`
- `GenerateOccupancyChangeEvent()`
- `GenerateSetpointChangeEvent()`
- `GenerateRunningStateChangeEvent()`
- `GenerateRunningModeChangeEvent()`
- `GenerateActiveScheduleChangeEvent()`
- `GenerateActivePresetChangeEvent()`

이벤트는 `mContext`가 있으면 `eventsGenerator.GenerateEvent()`를 사용하고, 그렇지 않으면 `LogEvent()`를 사용한다.

### Presets 및 Atomic Write

`Presets`는 `AtomicWriteSession`을 통해 원자적 목록 변경을 지원한다.

Atomic write 단계:

1. `OnAtomicWriteBegin()`
   - pending preset 목록 초기화
2. `WriteAttribute()`
   - `Presets` 목록을 `ReplaceAll` 또는 `AppendItem`으로 pending 목록에 기록
3. `OnAtomicWritePrecommit()`
   - built-in preset 유지 여부 검증
   - `ActivePresetHandle` 존재 여부 검증
   - preset 수 및 scenario별 수 검증
4. `OnAtomicWriteCommit()`
   - `CommitPendingPresets()` 실행
5. `OnAtomicWriteRollback()`
   - pending preset 목록 삭제

`SetActivePreset()`은 지정된 `PresetHandle`이 `Presets` 목록에 존재하는지 확인한 뒤 `ActivePresetHandle`을 변경한다.

### Suggestions

`ThermostatSuggestions`는 다음을 검증한다.

- `PresetHandle` 최대 길이: 16 bytes
- `ExpirationInMinutes`: `30`~`1440`
- Matter epoch 시간이 동기화되어 있는지 여부
- 지정된 `PresetHandle`이 `Presets`에 존재하는지 여부
- suggestion 목록의 최대 수
- `EffectiveTime`이 현재 시간보다 24시간 이상 미래인지 여부

`AddThermostatSuggestion` 처리 후:

- 새 `UniqueID` 생성
- `ThermostatSuggestions` attribute 변경 통지
- `CurrentThermostatSuggestion` 재평가
- `AddThermostatSuggestionResponse` 응답 전송

`RemoveThermostatSuggestion` 처리 후:

- `UniqueID`로 suggestion 검색
- suggestion 제거
- 만료된 suggestion 제거
- `CurrentThermostatSuggestion` 재평가

### Sensors

`ThermostatSensors`는 다음 목록을 제공한다.

- `Sensors`
- `AvailableSensorHandles`
- `EnabledSensorHandles`
- `SensorSchedule`

검증 규칙:

- sensor handle 최대 길이: 16 bytes
- 목록 최대 길이: 32
- `AvailableSensorHandles`의 handle은 `Sensors`에 구성되어 있어야 한다.
- `EnabledSensorHandles`의 handle은 `AvailableSensorHandles`에 있어야 한다.
- 중복 handle은 허용되지 않는다.
- `AvailableSensorHandles`에서 제거된 handle은 `EnabledSensorHandles`에서도 제거된다.
- `SensorSchedule`의 `DayOfWeek`에는 `Away` bit를 설정할 수 없다.
- `DayOfWeek`에는 최소 하나의 day bit가 설정되어야 한다.
- `TransitionTime`은 `1439` 이하여야 한다.
- `EnabledSensorHandles`는 `AvailableSensorHandles`에 존재해야 한다.
- 동일한 시간과 겹치는 day를 가진 transition은 허용되지 않는다.
- transition 수는 `NumberOfSensorScheduleTransitions`를 초과할 수 없다.

`SensorSchedule`은 `AtomicWriteSession`을 통해 다음 단계를 수행한다.

- `OnAtomicWriteBegin()`
- `OnAtomicWritePrecommit()`
- `OnAtomicWriteCommit()`
- `OnAtomicWriteRollback()`

### Owned Members

다음 타입은 문자열 또는 byte array의 소유 저장소를 관리한다.

- `PresetStructWithOwnedMembers`
  - `kPresetHandleSize = 16`
  - `kPresetNameSize = 64`
- `ThermostatSuggestionStructWithOwnedMembers`
  - `kThermostatSuggestionPresetHandleSize = 16`
- `ThermostatSensorStructWithOwnedMembers`
  - `kThermostatSensorNameMaxSize = 64`
  - `kThermostatSensorHandleMaxSize = 16`
- `SensorScheduleTransitionStructWithOwnedMembers`
  - `kMaxEnabledSensorsPerTransition = 32`
  - `kMaxSensorHandleSize = 16`

### Codegen Integration

`ServerInit()`은 다음 설정으로 server cluster를 등록한다.

- `clusterId`: `Thermostat::Id`
- `fixedClusterInstanceCount`: `kThermostatFixedClusterCount`
- `maxClusterInstanceCount`: `kThermostatEndpointCount`
- `fetchFeatureMap`: `true`
- `fetchOptionalAttributes`: `false`

optional attribute 활성화 여부는 `BaseIntegrationDelegate::GetOptionalAttributes()`에서 endpoint의 attribute table과 feature map을 함께 확인하여 결정한다.

### Backward Compatibility Shim

`AttributeAccessorShim.h` 및 `AttributeAccessorShim.cpp`는 기존 Ember 기반 호출을 위한 호환 계층이다.

지원 namespace 예시:

- `ControlSequenceOfOperation`
- `LocalTemperature`
- `SystemMode`
- `ThermostatRunningMode`
- `ThermostatRunningState`
- `AbsMinHeatSetpointLimit`
- `AbsMaxHeatSetpointLimit`
- `OccupiedCoolingSetpoint`
- `OccupiedHeatingSetpoint`
- `FeatureMap`
- `PICoolingDemand`
- `PIHeatingDemand`

## 관련 문서

- `data_model/1.7/clusters/Thermostat.xml`
- `src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml`
- `src/app/clusters/thermostat-server/ThermostatCluster.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.h`
- `src/app/clusters/thermostat-server/ThermostatDelegate.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterPresets.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSensors.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.h`
- `src/app/clusters/thermostat-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-server/AttributeAccessorShim.h`