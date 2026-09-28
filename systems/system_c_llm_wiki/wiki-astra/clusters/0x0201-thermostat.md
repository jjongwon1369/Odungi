---
entity: Thermostat
ids: ['0x0201']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml', 'src/app/clusters/thermostat-server/ThermostatDelegate.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.h', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp', 'src/app/clusters/thermostat-server/CodegenIntegration.h', 'src/app/clusters/thermostat-server/ThermostatDelegate.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SetpointRange.h', 'src/app/clusters/thermostat-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp', 'src/app/clusters/thermostat-server/Setpoint.h', 'src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/Setpoint.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h', 'src/app/clusters/thermostat-server/Setpoints.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.h', 'src/app/clusters/thermostat-server/Temperature.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h', 'src/app/clusters/thermostat-server/AttributeAccessorShim.h', 'src/app/clusters/thermostat-server/DelegateResolution.h', 'src/app/clusters/thermostat-server/ThermostatCluster.h', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterRead.cpp', 'src/app/clusters/thermostat-server/SetpointLimits.h', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h', 'src/app/clusters/thermostat-server/AttributeAccessorShim.cpp', 'src/app/clusters/thermostat-server/Setpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp', 'data_model/1.7/clusters/Thermostat.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Thermostat

## 개요

`Thermostat`은 온도 조절기의 기능을 구성하고 제어하는 인터페이스다. 난방·냉방 설정값, 운전 모드, 재실 상태, 프리셋, 스케줄, 제안 및 센서 스케줄을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0201` |
| 스펙 이름 | `Thermostat Cluster` |
| SDK 이름 | `Thermostat` |
| Revision | `12` |
| 도메인 | `HVAC` |
| 분류 | `hierarchy="base"`, `role="application"`, `scope="Endpoint"` |
| PICS | `TSTAT` |
| SDK define | `THERMOSTAT_CLUSTER` |
| 구현 네임스페이스 | `chip::app::Clusters::Thermostat` |

스펙 XML, SDK XML, C++ 구현은 구분해서 읽어야 한다. 제공된 자료에는 폐기 상태, 일부 필드 이름, 제약 표현 및 실제 처리 동작의 차이가 있다.

## 스펙

출처: `data_model/1.7/clusters/Thermostat.xml`

### Feature

| bit | code | name | 조건 및 의미 |
|---|---|---|---|
| `0` | `HEAT` | `Heating` | 난방 장치 관리. `AUTO`이면 필수 |
| `1` | `COOL` | `Cooling` | 냉방 장치 관리. `AUTO`이면 필수 |
| `2` | `OCC` | `Occupancy` | 재실·비재실 설정값 지원. 선택 |
| `3` | `SCH` | `ScheduleConfiguration` | `obsoleteConform` |
| `4` | `SB` | `Setback` | `obsoleteConform` |
| `5` | `AUTO` | `AutoMode` | `SystemMode`의 `Auto` 지원. 선택 |
| `6` | `LTNE` | `LocalTemperatureNotExposed` | `LocalTemperature` 값 비노출. 선택 |
| `7` | `MSCH` | `MatterScheduleConfiguration` | 확장 스케줄 지원. 선택 |
| `8` | `PRES` | `Presets` | 설정값 프리셋 지원. 선택 |
| `9` | `TEVT` | `Events` | `otherwiseConform`에 `provisionalConform`, `optionalConform` |
| `10` | `TSUGGEST` | `ThermostatSuggestions` | `PRES` 조건에서 선택 |
| `11` | `SENSORS` | `ThermostatSensors` | 센서 스케줄 지원. `provisionalConform` |

`AUTO`가 아닌 경우에도 `HEAT`, `COOL` 중 하나 이상이 필요하도록 선택 조건이 정의되어 있다.

### 속성

아래 표의 읽기 권한은 모두 `view`다. 쓰기 열의 `—`는 스펙 XML에 쓰기 접근이 선언되지 않았음을 뜻한다. 별도 표시가 없는 조건의 “선택”은 `optionalConform`이다.

#### 온도·설정값·운전 상태

| ID | 이름 | 스펙 타입 | 쓰기 | 조건·기본값·제약 |
|---|---|---|---|---|
| `0x0000` | `LocalTemperature` | `temperature` | — | 필수, nullable |
| `0x0001` | `OutdoorTemperature` | `temperature` | — | 선택, nullable, 기본값 `null` |
| `0x0002` | `Occupancy` | `OccupancyBitmap` | — | `OCC` 필수 |
| `0x0003` | `AbsMinHeatSetpointLimit` | `temperature` | — | `HEAT` 선택, 기본값 `700`, fixed |
| `0x0004` | `AbsMaxHeatSetpointLimit` | `temperature` | — | `HEAT` 선택, 기본값 `3000`, fixed |
| `0x0005` | `AbsMinCoolSetpointLimit` | `temperature` | — | `COOL` 선택, 기본값 `1600`, fixed |
| `0x0006` | `AbsMaxCoolSetpointLimit` | `temperature` | — | `COOL` 선택, 기본값 `3200`, fixed |
| `0x0010` | `LocalTemperatureCalibration` | `SignedTemperature` | `manage` | `LTNE`가 아닐 때 선택, 기본값 `0` |
| `0x0011` | `OccupiedCoolingSetpoint` | `temperature` | `operate` | `COOL` 필수, 기본값 `2600` |
| `0x0012` | `OccupiedHeatingSetpoint` | `temperature` | `operate` | `HEAT` 필수, 기본값 `2000` |
| `0x0013` | `UnoccupiedCoolingSetpoint` | `temperature` | `operate` | `COOL` 및 `OCC` 필수, 기본값 `2600` |
| `0x0014` | `UnoccupiedHeatingSetpoint` | `temperature` | `operate` | `HEAT` 및 `OCC` 필수, 기본값 `2000` |
| `0x0015` | `MinHeatSetpointLimit` | `temperature` | `manage` | `HEAT` 선택, 기본값은 `AbsMinHeatSetpointLimit` |
| `0x0016` | `MaxHeatSetpointLimit` | `temperature` | `manage` | `HEAT` 선택, 기본값은 `AbsMaxHeatSetpointLimit` |
| `0x0017` | `MinCoolSetpointLimit` | `temperature` | `manage` | `COOL` 선택, 기본값은 `AbsMinCoolSetpointLimit` |
| `0x0018` | `MaxCoolSetpointLimit` | `temperature` | `manage` | `COOL` 선택, 기본값은 `AbsMaxCoolSetpointLimit` |
| `0x0019` | `MinSetpointDeadBand` | `SignedTemperature` | 선택적 쓰기, `manage` | `AUTO` 필수, `0`–`127`, 기본값 `20` |
| `0x001A` | `RemoteSensing` | `RemoteSensingBitmap` | `manage` | 선택, 기본값 `0` |
| `0x001B` | `ControlSequenceOfOperation` | `ControlSequenceOfOperationEnum` | `manage` | 필수 |
| `0x001C` | `SystemMode` | `SystemModeEnum` | `manage` | 필수 |
| `0x001E` | `ThermostatRunningMode` | `ThermostatRunningModeEnum` | — | `TEVT` 및 `AUTO`이면 필수, 그 외 `AUTO`에서 선택, 기본값 `0` |
| `0x0023` | `TemperatureSetpointHold` | `TemperatureSetpointHoldEnum` | `manage` | 선택, 기본값 `0` |
| `0x0024` | `TemperatureSetpointHoldDuration` | `uint16` | `manage` | 선택, nullable, `1`–`1440`, 기본값 `null` |
| `0x0029` | `ThermostatRunningState` | `RelayStateBitmap` | — | 선택 |
| `0x0030` | `SetpointChangeSource` | `SetpointChangeSourceEnum` | — | 선택, 기본값 `0` |
| `0x0031` | `SetpointChangeAmount` | `int16s` | — | 선택, nullable, 기본값 `null` |
| `0x0032` | `SetpointChangeSourceTimestamp` | `epoch-s` | — | 선택, 기본값 `MS` |
| `0x003A` | `EmergencyHeatDelta` | `UnsignedTemperature` | `manage` | 선택, 기본값 `255` |
| `0x0052` | `SetpointHoldExpiryTimestamp` | `epoch-s` | — | 선택, nullable, 기본값 `null` |
| `0x0057` | `CriticalFreezeProtection` | `bool` | — | provisional 및 `HEAT` 선택 조건, 기본값 `false` |
| `0x0058` | `CriticalOverheatProtection` | `bool` | — | provisional 및 `COOL` 선택 조건, 기본값 `false` |

`LocalTemperatureCalibration`부터 `SystemMode`까지 위 표의 쓰기 가능 속성, `TemperatureSetpointHold`, `TemperatureSetpointHoldDuration`, `EmergencyHeatDelta`, `SetpointHoldExpiryTimestamp`, 두 Critical Protection 속성에는 `persistence="nonVolatile"`이 선언되어 있다.

#### AC 관련 속성

모두 선택 속성이다.

| ID | 이름 | 타입 | 쓰기 | 기본값 |
|---|---|---|---|---|
| `0x0040` | `ACType` | `ACTypeEnum` | `manage` | `0` |
| `0x0041` | `ACCapacity` | `uint16` | `manage` | `0` |
| `0x0042` | `ACRefrigerantType` | `ACRefrigerantTypeEnum` | `manage` | `0` |
| `0x0043` | `ACCompressorType` | `ACCompressorTypeEnum` | `manage` | `0` |
| `0x0044` | `ACErrorCode` | `ACErrorCodeBitmap` | `manage` | `0` |
| `0x0045` | `ACLouverPosition` | `ACLouverPositionEnum` | `manage` | `0` |
| `0x0046` | `ACCoilTemperature` | `temperature` | — | `null`, nullable |
| `0x0047` | `ACCapacityFormat` | `ACCapacityFormatEnum` | `manage` | `0` |

`ACErrorCode`, `ACCoilTemperature`를 제외한 위 속성에는 `persistence="nonVolatile"`이 선언되어 있다.

#### 프리셋·스케줄·제안·센서

| ID | 이름 | 타입 또는 목록 항목 타입 | 조건 | 제약·접근 |
|---|---|---|---|---|
| `0x0048` | `PresetTypes` | `PresetTypeStruct` 목록 | `PRES` 필수 | `1`–`7`개, fixed |
| `0x0049` | `ScheduleTypes` | `ScheduleTypeStruct` 목록 | `MSCH` 필수 | `1`–`3`개, fixed |
| `0x004A` | `NumberOfPresets` | `uint8` | `PRES` 필수 | 최소 `1`, fixed |
| `0x004B` | `NumberOfSchedules` | `uint8` | `MSCH` 필수 | 최소 `1`, fixed |
| `0x004C` | `NumberOfScheduleTransitions` | `uint8` | `MSCH` 필수 | 최소 `1`, fixed |
| `0x004D` | `NumberOfScheduleTransitionPerDay` | `uint8` | `MSCH` 필수 | 최소 `1`, nullable, fixed |
| `0x004E` | `ActivePresetHandle` | `octstr` | `PRES` 필수 | 최대 길이 `16`, nullable |
| `0x004F` | `ActiveScheduleHandle` | `octstr` | `MSCH` 필수 | 최대 길이 `16`, nullable |
| `0x0050` | `Presets` | `PresetStruct` 목록 | `PRES` 필수 | 최대 `NumberOfPresets`개, 쓰기 `manage`, atomicWrite |
| `0x0051` | `Schedules` | `ScheduleStruct` 목록 | `MSCH` 필수 | 최대 `NumberOfSchedules`개, 쓰기 `manage`, atomicWrite |
| `0x0053` | `MaxThermostatSuggestions` | `uint8` | `TSUGGEST` 필수 | 최소 `5`, fixed |
| `0x0054` | `ThermostatSuggestions` | `ThermostatSuggestionStruct` 목록 | `TSUGGEST` 필수 | 최대 `MaxThermostatSuggestions`개 |
| `0x0055` | `CurrentThermostatSuggestion` | `ThermostatSuggestionStruct` | `TSUGGEST` 필수 | nullable |
| `0x0056` | `ThermostatSuggestionNotFollowingReason` | `ThermostatSuggestionNotFollowingReasonBitmap` | `TSUGGEST` 필수 | nullable |
| `0x0059` | `Sensors` | `ThermostatSensorStruct` 목록 | provisional, `SENSORS` 필수 조건 | 최대 `32`개 |
| `0x005A` | `AvailableSensorHandles` | `octstr` 목록 | provisional, `SENSORS` 필수 조건 | 최대 `32`개, 항목 최대 길이 `16`, 쓰기 `manage` |
| `0x005B` | `EnabledSensorHandles` | `octstr` 목록 | provisional, `SENSORS` 필수 조건 | 최대 `32`개, 항목 최대 길이 `16`, 쓰기 `manage` |
| `0x005C` | `NumberOfSensorScheduleTransitions` | `uint8` | provisional, `SENSORS` 필수 조건 | fixed |
| `0x005D` | `SensorSchedule` | `SensorScheduleTransitionStruct` 목록 | provisional, `SENSORS` 필수 조건 | 최대 `NumberOfSensorScheduleTransitions`개, 쓰기 `manage`, atomicWrite |

`ActivePresetHandle`, `ActiveScheduleHandle`, `Presets`, `Schedules`, `ThermostatSuggestions`, `AvailableSensorHandles`, `EnabledSensorHandles`, `SensorSchedule`에는 `persistence="nonVolatile"`이 선언되어 있다.

#### obsolete 속성

| ID | 이름 | 타입 |
|---|---|---|
| `0x0007` | `PICoolingDemand` | `uint8` |
| `0x0008` | `PIHeatingDemand` | `uint8` |
| `0x0009` | `HVACSystemTypeConfiguration` | `HVACSystemTypeBitmap` |
| `0x0020` | `StartOfWeek` | `StartOfWeekEnum` |
| `0x0021` | `NumberOfWeeklyTransitions` | `uint8` |
| `0x0022` | `NumberOfDailyTransitions` | `uint8` |
| `0x0025` | `ThermostatProgrammingOperationMode` | `ProgrammingOperationModeBitmap` |
| `0x0034` | `OccupiedSetback` | `UnsignedTemperature` |
| `0x0035` | `OccupiedSetbackMin` | `UnsignedTemperature` |
| `0x0036` | `OccupiedSetbackMax` | `UnsignedTemperature` |
| `0x0037` | `UnoccupiedSetback` | `UnsignedTemperature` |
| `0x0038` | `UnoccupiedSetbackMin` | `UnsignedTemperature` |
| `0x0039` | `UnoccupiedSetbackMax` | `UnsignedTemperature` |

### 데이터 타입

숫자 별칭은 `SignedTemperature` → `int8`, `TemperatureDifference` → `int16`, `UnsignedTemperature` → `uint8`로 선언되어 있다.

#### enum

아래 값은 스펙 XML의 표기다.

| 타입 | 값과 항목 |
|---|---|
| `SystemModeEnum` | `0`: `Off`, `1`: `Auto`, `3`: `Cool`, `4`: `Heat`, `5`: `EmergencyHeat`, `6`: `Precooling`, `7`: `FanOnly`, `8`: `Dry`, `9`: `Sleep` |
| `ThermostatRunningModeEnum` | `0`: `Off`, `3`: `Cool`, `4`: `Heat` |
| `ControlSequenceOfOperationEnum` | `0`: `CoolingOnly`, `1`: `CoolingWithReheat`, `2`: `HeatingOnly`, `3`: `HeatingWithReheat`, `4`: `CoolingAndHeating`, `5`: `CoolingAndHeatingWithReheat` |
| `TemperatureSetpointHoldEnum` | `0`: `SetpointHoldOff`, `1`: `SetpointHoldOn` |
| `SetpointRaiseLowerModeEnum` | `0`: `Heat`, `1`: `Cool`, `2`: `Both` |
| `SetpointChangeSourceEnum` | `0`: `Manual`, `1`: `Schedule`, `2`: `External` |
| `PresetScenarioEnum` | `1`: `Occupied`, `2`: `Unoccupied`, `3`: `Sleep`, `4`: `Wake`, `5`: `Vacation`, `6`: `GoingToSleep`, `254`: `UserDefined` |
| `StartOfWeekEnum` | `0`: `Sunday`, `1`: `Monday`, `2`: `Tuesday`, `3`: `Wednesday`, `4`: `Thursday`, `5`: `Friday`, `6`: `Saturday` |
| `ACCapacityFormatEnum` | `0`: `BTUh` |
| `ACCompressorTypeEnum` | `0`: `Unknown`, `1`: `T1`, `2`: `T2`, `3`: `T3` |
| `ACLouverPositionEnum` | `1`: `Closed`, `2`: `Open`, `3`: `Quarter`, `4`: `Half`, `5`: `ThreeQuarters` |
| `ACRefrigerantTypeEnum` | `0`: `Unknown`, `1`: `R22`, `2`: `R410a`, `3`: `R407c` |
| `ACTypeEnum` | `0`: `Unknown`, `1`: `CoolingFixed`, `2`: `HeatPumpFixed`, `3`: `CoolingInverter`, `4`: `HeatPumpInverter` |

#### bitmap

| 타입 | bit와 필드 |
|---|---|
| `ACErrorCodeBitmap` | `0`: `CompressorFail`, `1`: `RoomSensorFail`, `2`: `OutdoorSensorFail`, `3`: `CoilSensorFail`, `4`: `FanFail` |
| `HVACSystemTypeBitmap` | `0x00`–`0x01`: `CoolingStage`, `0x02`–`0x03`: `HeatingStage`, `4`: `HeatingIsHeatPump`, `5`: `HeatingUsesFuel` |
| `OccupancyBitmap` | `0`: `Occupied` |
| `PresetTypeFeaturesBitmap` | `0`: `Automatic`, `1`: `SupportsNames` |
| `ProgrammingOperationModeBitmap` | `0`: `ScheduleActive`, `1`: `AutoRecovery`, `2`: `Economy` |
| `RelayStateBitmap` | `0`: `Heat`, `1`: `Cool`, `2`: `Fan`, `3`: `HeatStage2`, `4`: `CoolStage2`, `5`: `FanStage2`, `6`: `FanStage3` |
| `RemoteSensingBitmap` | `0`: `LocalTemperature`, `1`: `OutdoorTemperature`, `2`: `Occupancy` |
| `ScheduleDayOfWeekBitmap` | `0`: `Sunday`, `1`: `Monday`, `2`: `Tuesday`, `3`: `Wednesday`, `4`: `Thursday`, `5`: `Friday`, `6`: `Saturday`, `7`: `Away` |
| `ScheduleModeBitmap` | `0`: `HeatSetpointPresent`, `1`: `CoolSetpointPresent` |
| `ScheduleTypeFeaturesBitmap` | `0`: `SupportsPresets`, `1`: `SupportsSetpoints`, `2`: `SupportsNames`, `3`: `SupportsOff` |
| `ThermostatSuggestionNotFollowingReasonBitmap` | `0`: `DemandResponseEvent`, `1`: `OngoingHold`, `2`: `Schedule`, `3`: `Occupancy`, `4`: `VacationMode`, `5`: `TimeOfUseCostSavings`, `6`: `PreCoolingOrPreHeating`, `7`: `ConflictingSuggestions` |

`ScheduleTypeFeaturesBitmap`은 `SupportsPresets`, `SupportsSetpoints` 중 하나 이상을 요구하며, `SupportsPresets`는 `PRES` 조건을 가진다.

#### struct

필드 앞 숫자는 field ID다.

| 타입 | 필드 구성 |
|---|---|
| `PresetStruct` | `0` `PresetHandle`: nullable `octstr`, 최대 `16`; `1` `PresetScenario`: `PresetScenarioEnum`; `2` `Name`: 선택·nullable `string`, 최대 `64`; `3` `CoolingSetpoint`: `COOL` 필수, 기본값 `2600`; `4` `HeatingSetpoint`: `HEAT` 필수, 기본값 `2000`; `5` `BuiltIn`: nullable `bool`, 기본값 `false` |
| `PresetTypeStruct` | `0` `PresetScenario`; `1` `NumberOfPresets`: `uint8`, 기본값 `0`; `2` `PresetTypeFeatures`: `PresetTypeFeaturesBitmap`, 기본값 `0` |
| `ScheduleStruct` | `0` `ScheduleHandle`: nullable `octstr`, 최대 `16`; `1` `SystemMode`; `2` `Name`: 선택 `string`, 최대 `64`; `3` `PresetHandle`: 선택 `octstr`, 최대 `16`; `4` `Transitions`: `ScheduleTransitionStruct` 목록, `1`–`NumberOfScheduleTransitions`개; `5` `BuiltIn`: nullable `bool`, 기본값 `false` |
| `ScheduleTransitionStruct` | `0` `DayOfWeek`; `1` `TransitionTime`: `uint16`, 최대 `1439`; `2` `PresetHandle`: `PRES`에서 선택, 최대 `16`; `3` `SystemMode`: 선택; `4` `CoolingSetpoint`: `COOL`에서 선택; `5` `HeatingSetpoint`: `HEAT`에서 선택 |
| `ScheduleTypeStruct` | `0` `SystemMode`; `1` `NumberOfSchedules`: `uint8`, 기본값 `0`, 속성 `NumberOfSchedules` 이하; `2` `ScheduleTypeFeatures`: `ScheduleTypeFeaturesBitmap`, 기본값 `0` |
| `SensorScheduleTransitionStruct` | `0` `DayOfWeek`; `1` `TransitionTime`: `uint16`, 최대 `1439`; `2` `EnabledSensorHandles`: `octstr` 목록, 최대 `32`개, 항목 최대 길이 `16` |
| `ThermostatSensorStruct` | `0` `Name`: `string`, 최대 `64`; `1` `SensorHandle`: `octstr`, 최대 `16`; `2` `Cluster`: `cluster-id`; `3` `Endpoint`: 선택 `endpoint-no`; `4` `Node`: `node-id`; `5` `FabricIndex`: `fabric-idx` |
| `ThermostatSuggestionStruct` | `0` `UniqueID`: `uint8`; `1` `PresetHandle`: `octstr`, 최대 `16`; `2` `EffectiveTime`: `epoch-s`; `3` `ExpirationTime`: `epoch-s` |
| `WeeklyScheduleTransitionStruct` | `0` `TransitionTime`: `uint16`, 최대 `1439`; `1` `HeatSetpoint`: nullable `temperature`; `2` `CoolSetpoint`: nullable `temperature` |

`ThermostatSensorStruct`의 `Node`, `FabricIndex`는 `Endpoint`가 있으면 필수다. XML에서 `<desc/>`로만 표시된 추가 제약의 상세 내용은 제공되지 않았다.

### 명령

| ID | 이름 | 방향 | 권한·조건 | 필드 |
|---|---|---|---|---|
| `0x00` | `SetpointRaiseLower` | `commandToServer` | `operate`, 필수 | `Mode`, `Amount` |
| `0x05` | `SetActiveScheduleRequest` | `commandToServer` | `operate`, `MSCH` 필수 | `ScheduleHandle`, 최대 길이 `16` |
| `0x06` | `SetActivePresetRequest` | `commandToServer` | `operate`, `PRES` 필수 | nullable `PresetHandle`, 최대 길이 `16` |
| `0x07` | `AddThermostatSuggestion` | `commandToServer` | `manage`, `TSUGGEST` 필수 | `PresetHandle`, nullable `EffectiveTime`, `ExpirationInMinutes` |
| `0x02` | `AddThermostatSuggestionResponse` | `responseFromServer` | `TSUGGEST` 필수 | `UniqueID` |
| `0x08` | `RemoveThermostatSuggestion` | `commandToServer` | `manage`, `TSUGGEST` 필수 | `UniqueID` |

- `SetpointRaiseLower.Mode`는 `SetpointRaiseLowerModeEnum`, `Amount`는 `int8`이다.
- `AddThermostatSuggestion.ExpirationInMinutes`는 `uint16`, 범위는 `30`–`1440`이다.
- `AddThermostatSuggestion`의 응답은 `AddThermostatSuggestionResponse`다.

다음 주간 스케줄 명령은 모두 `obsoleteConform`이다.

| ID | 이름 | 방향 | 필드 |
|---|---|---|---|
| `0x01` | `SetWeeklySchedule` | `commandToServer` | `NumberOfTransitionsForSequence`, `DayOfWeekForSequence`, `ModeForSequence`, `Transitions` |
| `0x02` | `GetWeeklySchedule` | `commandToServer` | `DaysToReturn`, `ModeToReturn` |
| `0x03` | `ClearWeeklySchedule` | `commandToServer` | 없음 |
| `0x00` | `GetWeeklyScheduleResponse` | `responseFromServer` | `NumberOfTransitionsForSequence`, `DayOfWeekForSequence`, `ModeForSequence`, `Transitions` |

`Transitions`는 최대 `10`개의 `WeeklyScheduleTransitionStruct`다.

### 이벤트

모든 이벤트는 `priority="info"`, 읽기 권한 `view`이며 provisional 조건을 포함한다.

| 스펙 ID | 이름 | 필수 조건 | 필드 |
|---|---|---|---|
| `0x00` | `SystemModeChange` | `TEVT` | 선택 `PreviousSystemMode`, `CurrentSystemMode` |
| `0x01` | `LocalTemperatureChange` | `TEVT` 및 `LTNE` 아님 | nullable `CurrentLocalTemperature` |
| `0x02` | `OccupancyChange` | `TEVT` 및 `OCC` | 선택 `PreviousOccupancy`, `CurrentOccupancy` |
| `0x03` | `SetpointChange` | `TEVT` | `SystemMode`, `Occupancy`, 선택 `PreviousSetpoint`, `CurrentSetpoint` |
| `0x04` | `RunningStateChange` | `TEVT` | 선택 `PreviousRunningState`, `CurrentRunningState` |
| `0x05` | `RunningModeChange` | `TEVT` 및 `AUTO` | 선택 `PreviousRunningMode`, `CurrentRunningMode` |
| `0x06` | `ActiveScheduleChange` | `TEVT` 및 `MSCH` | 선택·nullable `PreviousScheduleHandle`, nullable `CurrentScheduleHandle` |
| `0x07` | `ActivePresetChange` | `TEVT` 및 `PRES` | 선택·nullable `PreviousPresetHandle`, nullable `CurrentPresetHandle` |

`SetpointChange.SystemMode`는 `Heat`, `Cool`로 제한된다. `Occupancy` 필드는 `OCC`에서 필수이며 기본값은 `1`이다. 이벤트의 핸들 필드는 최대 길이 `16`이다.

### Revision 변경 사항

- Revision `6`: `LTNE` 도입.
- Revision `7`: 온도 보정·deadband 제약 갱신, `Presets`, `MatterScheduleConfiguration` 도입.
- Revision `8`: `ControlSequenceOfOperation` 쓰기 관련 설명 추가.
- Revision `9`: `AlarmMask`, `AlarmCodeBitmap` 제거.
- Revision `10`: Zigbee 관련 요소 및 P quality 제거, `ThermostatProgrammingOperationMode`, `Setback` 관련 변경.
- Revision `11`: 제안 및 이벤트 추가.
- Revision `12`: `TemperatureSetpointHoldDuration` 최소값 `1`, Critical Protection 속성, 센서 스케줄 지원 추가.

Revision `10` 이력에는 `ProgrammingOperationModeBitmap` 제거가 기록되어 있지만, 제공된 XML의 `dataTypes`에는 해당 정의가 남아 있다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml`

### 생성 정보

- Alchemy 생성 파일이며 `DO NOT EDIT`로 표시된다.
- 생성 원본: `src/app_clusters/Thermostat.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`
- 생성 파라미터에 `provisional-policy=loose`가 포함된다.
- client와 server가 모두 활성화되어 있고, 각각 `tick="false"`, `init="false"`다.
- 전역 속성 `0xFFFD`의 값은 `12`다.

### 타입 표현

SDK XML은 스펙의 `uint8`, `uint16`, `octstr`, `string`, `epoch-s` 등에 대응하는 타입을 각각 `int8u`, `int16u`, `octet_string`, `char_string`, `epoch_s`로 표기한다.

| SDK 타입 | 기반 타입 |
|---|---|
| 모든 enum 정의 | `enum8` |
| `ACErrorCodeBitmap` | `bitmap32` |
| `HVACSystemTypeBitmap`, `OccupancyBitmap`, `ProgrammingOperationModeBitmap`, `RemoteSensingBitmap`, `ScheduleDayOfWeekBitmap`, `ScheduleModeBitmap` | `bitmap8` |
| `ScheduleTypeFeaturesBitmap`, `RelayStateBitmap`, `PresetTypeFeaturesBitmap`, `ThermostatSuggestionNotFollowingReasonBitmap` | `bitmap16` |

`Presets`, `Schedules`, `SensorSchedule`에는 `mustUseAtomicWrite="true"`가 선언되어 있다.

### SDK에 추가된 atomic 명령

제공된 스펙 XML의 `commands`에는 아래 두 명령이 없지만, SDK XML에는 정의되어 있다.

| ID | 이름 | source | 인자 |
|---|---|---|---|
| `0xFE` | `AtomicRequest` | `client` | `RequestType`: `AtomicRequestTypeEnum`; `AttributeRequests`: `attrib_id` 배열; 선택 `Timeout`: `int16u` |
| `0xFD` | `AtomicResponse` | `server` | `StatusCode`: `status`; `AttributeStatus`: `AtomicAttributeStatusStruct` 배열; 선택 `Timeout`: `int16u` |

`AtomicRequest`의 응답은 `AtomicResponse`다. 두 명령의 인자는 원문에서 모두 `id="0"`으로 표기되어 있다.

### 스펙과 SDK의 표현 차이

| 항목 | 스펙 XML | SDK XML |
|---|---|---|
| 속성 `0x0047` | `ACCapacityFormat` | `ACCapacityformat` |
| `SCH`, `SB` 및 구형 관련 요소 | `obsoleteConform` | `deprecateConform` 또는 이를 포함한 `otherwiseConform` |
| 사용자 설정값 제한의 기본값 | 대응하는 `AbsMinHeatSetpointLimit`, `AbsMaxHeatSetpointLimit`, `AbsMinCoolSetpointLimit`, `AbsMaxCoolSetpointLimit` 참조 | `700`, `3000`, `1600`, `3200` |
| `PresetStruct.CoolingSetpoint`, `PresetStruct.HeatingSetpoint` | 각각 `COOL`, `HEAT`에서 필수 | `optional="true"`, 기본값 `0x0A28`, `0x07D0` |
| `ThermostatSensorStruct.Node`, `ThermostatSensorStruct.FabricIndex` | `Endpoint`가 있으면 필수 | `optional="true"` |
| `SetpointChange.Occupancy` | `OCC`에서 필수 | `optional="true"` |
| `Presets`, `Schedules`, `ThermostatSuggestions`, `SensorSchedule` 목록 길이 | 관련 용량 속성을 참조 | `length="255"` |
| `SensorScheduleTransitionStruct.EnabledSensorHandles` | 최대 `32`개, 각 항목 최대 길이 `16` | `array="true"`, `type="octet_string"`, `length="32"` |
| 이벤트 ID 표기 | `0x00`–`0x07` | `0x0000`–`0x0007` |

이 차이는 각 입력의 정의를 그대로 구분한 것이며, SDK의 선택 필드 표현만으로 스펙의 조건부 필수 요구가 사라지는 것은 아니다.

## 구현

### 구성 방식과 등록

주요 파일:

- `src/app/clusters/thermostat-server/ThermostatCluster.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.cpp`
- `src/app/clusters/thermostat-server/DelegateResolution.h`
- `src/app/clusters/thermostat-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-server/CodegenIntegration.cpp`

`ThermostatCluster`는 `ThermostatClusterBase`, `AtomicWriteSession::Delegate`를 상속하는 가변 인자 클래스 템플릿이다. 전달된 delegate 타입으로 기능 처리 객체를 컴파일 시점에 구성한다.

| 구성 요소 | 대응 delegate |
|---|---|
| 기본 기능 | `Thermostat::Delegate` |
| 난방 설정값 | `ThermostatHeatingSetpoints::Delegate` |
| 냉방 설정값 | `ThermostatCoolingSetpoints::Delegate` |
| deadband | `ThermostatAutoSetpoints::Delegate` |
| Hold | `ThermostatHold::Delegate` |
| 프리셋 | `ThermostatPresets::Delegate` |
| 제안 | `ThermostatSuggestions::Delegate` |
| 재실 | `ThermostatOccupancy::Delegate` |
| 센서 | `ThermostatSensors::Delegate` |

구성 제약:

- `Thermostat::Delegate`가 반드시 필요하다.
- `kHasHeating || kHasCooling`이 참이어야 한다.
- `kHasSuggestions`이면 `kHasPresets`도 참이어야 한다.
- `kRequiresAtomicWrite`는 `kHasPresets || kHasSensors`다.
- 비활성 기능의 멤버 타입에는 `std::monostate`가 사용된다.
- `FullFeaturedThermostatCluster`는 위 delegate 타입을 모두 포함하는 별칭이다.

`detail::FindDelegate`는 인자 순서대로 첫 번째 일치 delegate를 찾는다. `detail::MakeFeature`, `detail::MakeAtomicWriteSession`, `detail::kArgsHasDelegate`가 조건부 구성을 담당한다.

등록 관련 API:

- `ServerInit`: 최소 하나의 delegate를 요구하며 `CodegenClusterIntegration::RegisterServer`를 호출한다.
- `ServerShutdown`: `CodegenClusterIntegration::UnregisterServer`를 호출한다.
- `FindClusterOnEndpoint`: 구성된 인스턴스를 endpoint로 검색한다.
- `ClusterStorage`: `LazyRegisteredServerCluster` 배열에 인스턴스를 보관한다.
- `kThermostatEndpointCount`: `kThermostatFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`.

`BaseIntegrationDelegate::GetOptionalAttributes`는 `emberAfContainsAttribute`와 기능 비트를 함께 확인한다. 난방·냉방 관련 속성, `LocalTemperatureCalibration`, `ThermostatRunningMode`, Critical Protection 속성에는 해당 기능 조건이 적용된다.

### delegate와 선택 속성

파일:

- `src/app/clusters/thermostat-server/ThermostatDelegate.h`
- `src/app/clusters/thermostat-server/ThermostatDelegate.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterAttributes.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp`

`Delegate`는 온도, `SystemMode`, `ControlSequenceOfOperation`, 운전 모드·상태 및 `FabricTable` 접근을 제공한다.

기본 동작:

- `Delegate::Startup`: `CHIP_NO_ERROR`.
- `Delegate::Shutdown`: 동작 없음.
- `Delegate::GetOutdoorTemperature`, `Delegate::GetRemoteSensing`: `Status::UnsupportedAttribute`.
- `GetLocalTemperatureCalibration`: `0`.
- `SetLocalTemperatureCalibration`: `changed = false`, `Status::Success`.

`OptionalAttributes`의 모든 플래그는 기본적으로 `false`다. `AppendOptionalAttributes`는 `entry.enabled`인 항목의 metadata만 추가한다.

### 기본 속성 읽기·쓰기

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterRead.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.cpp`

| 처리 대상 | 구현 동작 |
|---|---|
| `ClusterRevision` | `Thermostat::kRevision` 인코딩 |
| `FeatureMap` | `mFeatures` 인코딩 |
| `LocalTemperature` 읽기 | `Feature::kLocalTemperatureNotExposed`이면 null |
| `RemoteSensing` 읽기 | `Feature::kLocalTemperatureNotExposed`이면 `RemoteSensingBitmap::kLocalTemperature` 제거 |
| `RemoteSensing` 쓰기 | 위 기능이 활성화된 상태에서 `RemoteSensingBitmap::kLocalTemperature`를 설정하면 `Status::ConstraintError` |
| `LocalTemperatureCalibration` 쓰기 | `int16_t`로 디코딩한 뒤 `int8_t` 범위를 검사 |
| `ControlSequenceOfOperation` 쓰기 | 값을 적용하지 않고 `Status::Success` |
| `SystemMode` 쓰기 | 알려지지 않은 enum이면 `Status::InvalidValue`; 그 외 `SetSystemMode` 호출 |
| `Schedules` 읽기 | `TODO`로 표시되어 있으며 빈 목록 반환 |
| 처리하지 않는 기본 속성 | `Status::UnsupportedAttribute` |

`SetSystemMode`는 `Auto`, `Cool`, `Heat`, `EmergencyHeat`, `Precooling`에 대응하는 기능 지원 여부를 검사한다. 지원하지 않으면 `Status::ConstraintError`다.

`SetRunningMode`는 `Off`, `Cool`, `Heat`를 검사하고, `SetRunningState`는 난방·냉방 relay bit와 기능 지원 여부를 검사한다. delegate가 변경을 보고하면 속성 변경을 알리고 해당 이벤트 생성 함수를 호출한다.

### 설정값 모델과 기본 상수

파일:

- `src/app/clusters/thermostat-server/Temperature.h`
- `src/app/clusters/thermostat-server/Setpoint.h`
- `src/app/clusters/thermostat-server/Setpoint.cpp`
- `src/app/clusters/thermostat-server/SetpointLimits.h`
- `src/app/clusters/thermostat-server/SetpointRange.h`
- `src/app/clusters/thermostat-server/Setpoints.h`
- `src/app/clusters/thermostat-server/Setpoints.cpp`
- `src/app/clusters/thermostat-server/SetpointAttributes.h`
- `src/app/clusters/thermostat-server/SetpointAttributes.cpp`

`temperature`는 `int16_t` 별칭이다.

| 상수 | 값 |
|---|---|
| `kDefaultAbsMinHeatSetpointLimit` | `700` |
| `kDefaultAbsMaxHeatSetpointLimit` | `3000` |
| `kDefaultAbsMinCoolSetpointLimit` | `1600` |
| `kDefaultAbsMaxCoolSetpointLimit` | `3200` |
| `kDefaultDeadBand` | `200` |
| `kDefaultHeatingSetpoint` | `2000` |
| `kDefaultCoolingSetpoint` | `2600` |
| `kDefaultLocalTemperatureCalibration` | `0` |
| `kMinDeadBand` | `0` |
| `kMaxDeadBand` | `127` |
| `kMaxTemperatureSetpointHoldDurationMin` | `1440` |

모델 구성:

- `Setpoint`: 속성 ID와 온도 접근 인터페이스를 묶는다.
- `AbsoluteSetpoint`: 항상 온도값을 가진다.
- `OptionalSetpoint`: 명시적 값이 없으면 참조하는 `AbsoluteSetpoint`의 온도를 반환한다.
- `SetpointLimits`: 최소·최대값 검사와 `Clamp`를 제공한다.
- `SetpointRange`: `heating`, `cooling`을 보관한다.
- `Setpoints`: 절대 제한, 사용자 제한, `occupiedRange`, `unoccupiedRange`, `deadBand`를 보관한다.
- `SetpointAttributes`: 변경된 속성 ID를 `uint32_t` 비트맵으로 추적한다. ID가 `32` 미만이어야 하며 임의 속성용 범용 클래스가 아니다.

`Setpoints::Valid`는 지원 기능에 따라 제한 범위, 설정값 범위 및 deadband를 검사한다. `Setpoints::Fix`는 사용자 제한과 설정값을 보정하고, 최종 검증에 실패하면 `Status::ConstraintError`를 반환한다.

보정 과정은 변경된 난방 또는 냉방 값을 가능한 한 유지하면서 반대편 값을 조정한다. 반대편 제한을 넘으면 제한 경계와 deadband에 맞추어 양쪽 값을 조정한다.

### 설정값 처리와 `SetpointRaiseLower`

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp`

`ThermostatSetpointsBase::InvokeCommand`의 처리 순서:

1. `SetpointRaiseLower` 요청을 디코딩한다.
2. `mCluster.IsOccupied()`에 따라 설정값 범위를 선택한다.
3. `request_data.amount * 10`으로 내부 온도 증감량을 계산한다.
4. `request_data.mode`에 따라 지원되는 난방·냉방 값을 선택한다.
5. 알 수 없는 모드이거나 조정 대상이 없으면 `Status::InvalidCommand`.
6. `Setpoints::ClampMode::kClamp`로 `ChangeRange`를 호출한다.
7. 성공하면 `SaveSetpoints`를 호출한다.

직접 속성 쓰기는 `Setpoints::ClampMode::kDontClamp`를 사용한다. 최초 입력값이 사용자 제한 밖이면 `Status::ConstraintError`가 반환되며, 이후 관련 값의 정합성 보정은 `Fix`가 수행한다.

난방·냉방 처리 객체는 다음을 수행한다.

- 선택 속성이 없는 절대 제한은 기본 상수를 사용한다.
- 재실 설정값은 delegate에서 읽고, `occupancySupported`이면 비재실 설정값도 읽는다.
- 절대 제한 및 Critical Protection 속성 쓰기는 `Status::UnsupportedWrite`.
- 저장 전 `changedSetpoints.Valid()` 검사.
- delegate가 `changed = false`를 반환하면 해당 변경 플래그 제거.
- 저장 성공 후 변경된 속성을 알림.

`GenerateSetpointEvent`는 네 설정값 속성만 이벤트로 변환한다. 제한 속성 ID로 호출되더라도 switch에 대응 항목이 없어 이벤트가 생성되지 않는다.

`ThermostatAutoSetpoints`의 deadband 처리:

- `LoadDeadband`: `kMinDeadBand * 10`부터 `kMaxDeadBand * 10`까지 검사.
- 읽기: 내부 값을 `10`으로 나누고 `int8_t`로 인코딩.
- 쓰기: `kMinDeadBand`–`kMaxDeadBand`를 검사하지만, 유효한 값도 적용하지 않고 `Status::Success`.

`ThermostatCluster::WriteAttribute`에서 활성 설정값의 쓰기가 성공하면 `mPresets.SetActivePreset(DataModel::NullNullable)`로 활성 프리셋을 해제한다.

### Hold와 재실

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterHold.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHold.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp`

`ThermostatHold`는 다음 속성을 delegate에 연결한다.

- `TemperatureSetpointHold`
- `TemperatureSetpointHoldDuration`
- `SetpointHoldExpiryTimestamp`

알 수 없는 `TemperatureSetpointHoldEnum`은 `Status::InvalidValue`다. `TemperatureSetpointHoldDuration`은 null이 아닐 때 최대값만 검사한다.

`ThermostatOccupancy::IsOccupied`는 `OccupancyBitmap::kOccupied`를 검사한다. `SetOccupancy`는 delegate가 변경을 보고하면 `Occupancy` 속성 변경을 알린다. 제공된 함수 본문에는 `GenerateOccupancyChangeEvent` 호출이 없다.

재실 delegate가 없는 경우 `ThermostatClusterBase::IsOccupied`는 `true`를 반환한다.

### atomic write

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp`

`AtomicWriteSession`은 `State::Closed`, `State::Open`, 요청자 `ScopedNodeId`, 대상 속성 목록 및 타이머를 관리한다.

| 단계 | 동작 |
|---|---|
| `BuildAttributeStatuses` | 빈 목록, 중복 ID, 디코딩 실패, 지원하지 않는 속성은 `Status::InvalidCommand`; 메모리 할당 실패는 `Status::ResourceExhausted` |
| `BeginAtomicWrite` | `Timeout` 필수. 동일 요청자의 기존 세션은 `Status::InvalidInState` |
| 대상 검사 | `Presets`, `Schedules`, `SensorSchedule`만 atomic 대상으로 처리. 이미 편집 중인 대상은 `Status::Busy` |
| timeout 결정 | 요청 timeout과 대상별 최대 timeout 합계 중 작은 값 사용 |
| 시작 | `OnAtomicWriteBegin` 및 타이머 시작. 실패하면 rollback 호출 후 reset |
| `CommitAtomicWrite` | `OnAtomicWritePrecommit` 성공 시 `OnAtomicWriteCommit`, 이후 reset 및 응답 |
| `RollbackAtomicWrite` | reset 후 `OnAtomicWriteRollback`, 응답 |
| `TimerFired` | `Rollback` |
| `OnFabricRemoved` | 해당 fabric의 열린 세션이면 `Rollback` |
| `Shutdown` | `ResetAtomicWrite`, fabric delegate 제거 |

subject 기반 `InAtomicWrite`는 `Access::AuthMode::kCase`와 요청자 `ScopedNodeId` 일치를 요구한다.

구현상 구분할 사항:

- `InAtomicWrite(CommandHandler * commandObj, AtomicAttributes & attributeStatuses)`는 열린 상태와 속성 집합만 검사하며, 전달된 `commandObj`로 요청자를 비교하지 않는다.
- `CommitAtomicWrite`는 precommit 실패 시에도 reset하지만, 해당 경로에서 `OnAtomicWriteRollback`을 호출하지 않는다.
- `ThermostatCluster::WriteAttribute`는 프리셋·센서 처리 이후, 동일 subject의 열린 atomic write 중 일반 속성 쓰기에 `Status::InvalidInState`를 반환한다.

### 프리셋

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterPresets.h`
- `src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp`
- `src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp`

`Presets`는 편집 세션 소유자가 읽을 때 pending 목록을 반환하고, 그 외에는 현재 목록을 반환한다.

쓰기:

- 열린 대상 세션이 없으면 `InvalidInState`.
- 다른 요청자의 세션이면 `Busy`.
- `ReplaceAll`은 pending 목록을 비운 뒤 항목을 추가한다.
- `AppendItem`은 항목을 추가한다.
- 그 외 목록 연산은 `CHIP_ERROR_NOT_IMPLEMENTED`.

`AppendPendingPreset`은 다음을 검사한다.

- 핸들 길이와 `PresetScenario`.
- null 핸들의 신규 프리셋은 Built-in일 수 없음.
- 기존 핸들은 현재 `Presets`에 존재해야 함.
- pending 목록에 동일 핸들이 중복될 수 없음.
- 기존 프리셋과 `BuiltIn` 값이 일치해야 함.
- 시나리오 지원 여부와 `SupportsNames`.
- 전체 및 시나리오별 용량.

`PrecommitPresets`는 Built-in 프리셋 삭제와 활성 프리셋 누락을 검사한다. 설정값 제한 적용 코드는 임시 복사본만 변경한다는 `TODO`가 명시되어 있다.

`SetActivePreset`은 존재하지 않는 핸들에 `Status::InvalidCommand`를 반환한다. 성공하면 `ActivePresetHandle` 변경 알림과 `GenerateActivePresetChangeEvent`를 호출한다.

`CommitPendingPresets`에서 신규 프리셋의 고유 핸들을 할당하는 책임은 delegate에 있다.

### 제안

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp`
- `src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp`

`AddThermostatSuggestion`의 검증 및 처리:

1. 핸들 길이가 `kThermostatSuggestionPresetHandleSize`를 넘으면 `Status::ConstraintError`.
2. `ExpirationInMinutes`가 `30`–`1440` 밖이면 `Status::ConstraintError`.
3. Matter epoch 시각을 얻지 못하면 `Status::InvalidInState`.
4. 프리셋이 없으면 `Status::NotFound`.
5. 목록이 가득 차면 `Status::ResourceExhausted`.
6. `EffectiveTime`이 현재 시각보다 `24`시간 넘게 미래이면 `Status::InvalidCommand`.
7. 만료된 제안을 제거하고 고유 ID를 얻는다.
8. null `EffectiveTime`은 현재 시각으로 대체한다.
9. `ExpirationTime`을 계산해 delegate 목록에 추가한다.
10. 변경 알림, 재평가 및 `AddThermostatSuggestionResponse`를 수행한다.

용량 검사는 만료된 제안 제거보다 먼저 수행된다.

`RemoveThermostatSuggestion`은 `UniqueID`로 항목을 찾아 제거하며, 없으면 `Status::NotFound`다. 성공하면 목록 변경을 알리고 만료 항목 정리와 재평가를 수행한다.

`ReEvaluateCurrentSuggestion`은 재평가 전후의 null 여부 또는 `UniqueID`가 달라지면 `CurrentThermostatSuggestion` 변경을 알린다. 활성 프리셋 핸들이 달라지면 `ActivePresetHandle` 변경도 알린다. 현재 제안 선택과 만료 후 재평가 책임은 delegate 계약에 포함되어 있다.

### 센서 및 센서 스케줄

파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSensors.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp`
- `src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp`
- `src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp`

센서 목록 쓰기 제약:

| 속성 | 검증 |
|---|---|
| `AvailableSensorHandles` | 최대 `32`개, 각 핸들 최대 `16`, `Sensors`에 구성된 핸들, 중복 금지 |
| `EnabledSensorHandles` | 최대 `32`개, 각 핸들 최대 `16`, `AvailableSensorHandles`에 존재, 중복 금지 |

두 속성은 `ReplaceAll`, `AppendItem`을 처리하고 다른 목록 연산에는 `Status::UnsupportedWrite`를 반환한다.

`AvailableSensorHandles` 전체 교체로 제거된 핸들은 `EnabledSensorHandles`에서도 제거된다. delegate가 변경을 보고하면 해당 속성 변경 알림을 생성한다.

`SensorSchedule`:

- 편집 중인 subject는 pending 목록을 읽는다.
- 열린 atomic write가 없으면 `Status::InvalidInState`.
- 다른 요청자의 편집이면 `Status::Busy`.
- `ReplaceAll`, `AppendItem`을 지원한다.
- `DayOfWeek`는 `Away`가 설정되지 않아야 하고, `0`이 아니며, `0x7F` 밖의 비트가 없어야 한다.
- `TransitionTime`은 `1439` 이하여야 한다.
- 각 `EnabledSensorHandles`는 사용 가능한 핸들이며 길이·개수·중복 제약을 만족해야 한다.
- 전환 개수가 `NumberOfSensorScheduleTransitions`에 도달하면 추가 시 `ResourceExhausted`.
- `PrecommitSensorSchedule`은 같은 시각에 요일이 겹치는 전환을 `Status::ConstraintError`로 거부한다.

commit은 `CommitPendingSensorScheduleTransitions`를 호출하고 속성 변경을 알린다. rollback은 pending 목록을 비운다.

### 가변 길이 멤버의 소유권

| 구조체 | 소유 저장소 및 동작 |
|---|---|
| `PresetStructWithOwnedMembers` | `kPresetHandleSize = 16`, `kPresetNameSize = 64`; 핸들·이름을 내부 저장소로 복사. 초과 시 `CHIP_ERROR_NO_MEMORY` |
| `ThermostatSuggestionStructWithOwnedMembers` | `kThermostatSuggestionPresetHandleSize = 16`; 핸들 복사, 시간 접근에 `System::Clock::Seconds32` 사용 |
| `ThermostatSensorStructWithOwnedMembers` | 이름 `64`, 핸들 `16`; 초과 시 `CHIP_ERROR_INVALID_STRING_LENGTH`; 복사 생성자는 삭제되고 복사 대입은 제공 |
| `SensorScheduleTransitionStructWithOwnedMembers` | 최대 `32`개 핸들, 각 최대 `16`; 목록 초과는 `CHIP_ERROR_INVALID_LIST_LENGTH`, 핸들 초과는 `CHIP_ERROR_INVALID_STRING_LENGTH` |

`SensorScheduleTransitionStructWithOwnedMembers::RefreshEnabledSensorsList`는 각 `ByteSpan`을 내부 저장소에 다시 연결한다. `SetEnabledSensorHandles`, `GetEnabledSensorHandles`는 각각 `SetEnabledSensors`, `GetEnabledSensors`를 호출하는 인터페이스도 제공한다.

### 이벤트 생성

파일: `src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp`

모든 `Generate...Event` 함수는 `Feature::kEvents`가 없으면 즉시 반환한다.

- `mContext`가 있으면 `mContext->interactionContext.eventsGenerator.GenerateEvent`를 사용한다.
- 없으면 `LogEvent`를 사용하고 실패를 기록한다.
- `GenerateSetpointChangeEvent`는 `occupancy`를 `MakeOptional(occupancy)`로 설정한다.
- 제공된 `GenerateLocalTemperatureChangeEvent`에는 `LTNE` 검사나 유의미한 변화량 판정이 없다.
- `SetLocalTemperature`는 delegate가 변경을 보고할 때 해당 이벤트 생성 함수를 호출한다.

### 호환성 계층

파일:

- `src/app/clusters/thermostat-server/AttributeAccessorShim.h`
- `src/app/clusters/thermostat-server/AttributeAccessorShim.cpp`

기존 Ember 기반 호출을 위한 호환 API다.

- `FindClusterOnEndpoint<FullFeaturedThermostatCluster>`로 인스턴스를 찾는다.
- 필요한 인스턴스가 없으면 `Status::UnsupportedEndpoint`.
- `LocalTemperature::Set`은 `MarkAttributeDirty::kNo`를 `DataModel::AttributeChangeType::kQuiet`로 매핑한다.
- `AbsMinHeatSetpointLimit::Set`, `AbsMaxHeatSetpointLimit::Set`, `OccupiedCoolingSetpoint::Set`, `OccupiedHeatingSetpoint::Set`은 `Status::UnsupportedWrite`.
- `FeatureMap::Set`은 인스턴스 존재를 확인하지만 기능 변경 호출이 주석 처리되어 있어 값을 적용하지 않는다.
- `PICoolingDemand`, `PIHeatingDemand`는 endpoint별 저장소가 아닌 파일 내부 변수에 값을 보관한다.

### 스펙·정의와 구현을 구분해야 하는 지점

| 항목 | 제공된 자료에서 확인되는 차이 |
|---|---|
| `TemperatureSetpointHoldDuration` | 스펙·SDK 최소값은 `1`이지만 `ThermostatHold::WriteAttribute` 본문은 최대값만 검사 |
| `SetpointHoldExpiryTimestamp` | 스펙·SDK에서는 읽기 전용이나 `ThermostatHold::WriteAttribute`에 쓰기 처리 분기가 존재 |
| `LocalTemperatureCalibration` | SDK 최소값은 `-127`; 기본 쓰기 구현은 `std::numeric_limits<int8_t>::min()`을 사용 |
| `MinSetpointDeadBand` | 유효한 쓰기는 성공하지만 값은 적용하지 않음 |
| `ControlSequenceOfOperation` | 속성 쓰기는 성공하지만 무시됨. 직접 `SetControlSequenceOfOperation` 호출은 delegate에 전달 |
| `Schedules` | SDK·스펙 정의는 있으나 기본 읽기 구현은 빈 목록을 반환하는 `TODO` |
| `PrecommitPresets` | 설정값 clamp가 pending 저장소가 아닌 임시 복사본에만 적용된다는 `TODO` |
| `OccupancyChange` | 생성 함수는 있으나 제공된 `ThermostatOccupancy::SetOccupancy`에는 호출이 없음 |
| `LocalTemperatureChange` | SDK 설명은 유의미한 온도 변화 시 생성이나 제공된 생성 경로에는 변화량 임계값 검사가 없음 |
| atomic commit 요청 검사 | 속성 집합을 받는 `InAtomicWrite` overload는 요청자 비교를 수행하지 않음 |

이 표는 제공된 함수 본문과 정의의 차이를 기록한 것이다. 외부 접근 검사나 미제공 코드의 동작까지 단정하지 않는다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
