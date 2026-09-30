---
entity: Thermostat
ids: ['0x0201']
source_paths: ['data_model/1.7/clusters/Thermostat.xml', 'src/app/clusters/thermostat-server/AttributeAccessorShim.cpp', 'src/app/clusters/thermostat-server/AttributeAccessorShim.h', 'src/app/clusters/thermostat-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-server/CodegenIntegration.h', 'src/app/clusters/thermostat-server/DelegateResolution.h', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/Setpoint.cpp', 'src/app/clusters/thermostat-server/Setpoint.h', 'src/app/clusters/thermostat-server/SetpointAttributes.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.h', 'src/app/clusters/thermostat-server/SetpointLimits.h', 'src/app/clusters/thermostat-server/SetpointRange.h', 'src/app/clusters/thermostat-server/Setpoints.cpp', 'src/app/clusters/thermostat-server/Setpoints.h', 'src/app/clusters/thermostat-server/Temperature.h', 'src/app/clusters/thermostat-server/ThermostatCluster.h', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.h', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterHold.h', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.h', 'src/app/clusters/thermostat-server/ThermostatClusterRead.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h', 'src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp', 'src/app/clusters/thermostat-server/ThermostatDelegate.cpp', 'src/app/clusters/thermostat-server/ThermostatDelegate.h', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h', 'src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Thermostat

## 개요

`Thermostat`은 온도 조절기의 기능을 구성하고 제어하는 인터페이스다. 난방·냉방 설정점, 점유 상태, 동작 모드, 프리셋, 스케줄, 제안 및 센서 스케줄을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Thermostat Cluster` |
| 클러스터 식별자 | `Thermostat` |
| 클러스터 ID | `0x0201` |
| revision | `12` |
| domain | `HVAC` |
| hierarchy / role | `base` / `application` |
| scope | `Endpoint` |
| picsCode | `TSTAT` |
| SDK define | `THERMOSTAT_CLUSTER` |

제공된 구현은 `ThermostatCluster`를 중심으로 delegate 타입에 따라 기능을 구성한다. 스펙·SDK 정의와 실제 구현 동작은 구분해서 기술한다.

## 스펙

출처: `data_model/1.7/clusters/Thermostat.xml`

### 기능

| bit | code | name | 기능 및 적합성 |
|---|---|---|---|
| `0` | `HEAT` | `Heating` | 난방 장치 관리. `AUTO` 사용 시 필수 |
| `1` | `COOL` | `Cooling` | 냉방 장치 관리. `AUTO` 사용 시 필수 |
| `2` | `OCC` | `Occupancy` | 점유·비점유 설정점 지원. 선택 |
| `3` | `SCH` | `ScheduleConfiguration` | `obsoleteConform` |
| `4` | `SB` | `Setback` | `obsoleteConform` |
| `5` | `AUTO` | `AutoMode` | `Auto` 모드 지원. 선택 |
| `6` | `LTNE` | `LocalTemperatureNotExposed` | `LocalTemperature`에 온도 값을 노출하지 않음. 선택 |
| `7` | `MSCH` | `MatterScheduleConfiguration` | 확장 스케줄 지원. 선택 |
| `8` | `PRES` | `Presets` | 설정점 프리셋 지원. 선택 |
| `9` | `TEVT` | `Events` | 이벤트 지원. `provisionalConform`, `optionalConform` |
| `10` | `TSUGGEST` | `ThermostatSuggestions` | 제안 지원. `PRES` 조건의 선택 기능 |
| `11` | `SENSORS` | `ThermostatSensors` | 센서 스케줄 지원. `provisionalConform` |

`AUTO`를 사용하지 않는 경우에도 `HEAT`, `COOL` 중 최소 하나를 선택하는 조건이 있다.

### 속성

아래 표의 읽기는 모두 `view` 권한이다. 쓰기 열의 `operate`, `manage`는 쓰기 권한이며, `—`는 XML에 쓰기 접근이 정의되지 않았음을 뜻한다. 기본값이 명시되지 않은 경우 임의로 보충하지 않는다.

#### 온도·설정점·동작 모드

| ID | 이름 | 타입 | 쓰기 | 적합성 | 기본값·제약·품질 |
|---|---|---|---|---|---|
| `0x0000` | `LocalTemperature` | `temperature` | — | 필수 | nullable |
| `0x0001` | `OutdoorTemperature` | `temperature` | — | 선택 | `null`, nullable |
| `0x0002` | `Occupancy` | `OccupancyBitmap` | — | `OCC` 필수 | — |
| `0x0003` | `AbsMinHeatSetpointLimit` | `temperature` | — | `HEAT` 선택 | `700`, fixed |
| `0x0004` | `AbsMaxHeatSetpointLimit` | `temperature` | — | `HEAT` 선택 | `3000`, fixed |
| `0x0005` | `AbsMinCoolSetpointLimit` | `temperature` | — | `COOL` 선택 | `1600`, fixed |
| `0x0006` | `AbsMaxCoolSetpointLimit` | `temperature` | — | `COOL` 선택 | `3200`, fixed |
| `0x0010` | `LocalTemperatureCalibration` | `SignedTemperature` | `manage` | `LTNE` 미사용 시 선택 | `0`, nonVolatile |
| `0x0011` | `OccupiedCoolingSetpoint` | `temperature` | `operate` | `COOL` 필수 | `2600`, nonVolatile |
| `0x0012` | `OccupiedHeatingSetpoint` | `temperature` | `operate` | `HEAT` 필수 | `2000`, nonVolatile |
| `0x0013` | `UnoccupiedCoolingSetpoint` | `temperature` | `operate` | `COOL` 및 `OCC` 필수 | `2600`, nonVolatile |
| `0x0014` | `UnoccupiedHeatingSetpoint` | `temperature` | `operate` | `HEAT` 및 `OCC` 필수 | `2000`, nonVolatile |
| `0x0015` | `MinHeatSetpointLimit` | `temperature` | `manage` | `HEAT` 선택 | 기본값 `AbsMinHeatSetpointLimit`, nonVolatile |
| `0x0016` | `MaxHeatSetpointLimit` | `temperature` | `manage` | `HEAT` 선택 | 기본값 `AbsMaxHeatSetpointLimit`, nonVolatile |
| `0x0017` | `MinCoolSetpointLimit` | `temperature` | `manage` | `COOL` 선택 | 기본값 `AbsMinCoolSetpointLimit`, nonVolatile |
| `0x0018` | `MaxCoolSetpointLimit` | `temperature` | `manage` | `COOL` 선택 | 기본값 `AbsMaxCoolSetpointLimit`, nonVolatile |
| `0x0019` | `MinSetpointDeadBand` | `SignedTemperature` | 선택적 `manage` | `AUTO` 필수 | `20`, `0`–`127`, nonVolatile |
| `0x001A` | `RemoteSensing` | `RemoteSensingBitmap` | `manage` | 선택 | `0`, nonVolatile |
| `0x001B` | `ControlSequenceOfOperation` | `ControlSequenceOfOperationEnum` | `manage` | 필수 | nonVolatile |
| `0x001C` | `SystemMode` | `SystemModeEnum` | `manage` | 필수 | nonVolatile |
| `0x001E` | `ThermostatRunningMode` | `ThermostatRunningModeEnum` | — | `TEVT` 및 `AUTO`이면 필수, 그 외 `AUTO` 조건에서 선택 | `0` |
| `0x0023` | `TemperatureSetpointHold` | `TemperatureSetpointHoldEnum` | `manage` | 선택 | `0`, nonVolatile |
| `0x0024` | `TemperatureSetpointHoldDuration` | `uint16` | `manage` | 선택 | `null`, nullable, `1`–`1440`, nonVolatile |
| `0x0029` | `ThermostatRunningState` | `RelayStateBitmap` | — | 선택 | — |
| `0x0030` | `SetpointChangeSource` | `SetpointChangeSourceEnum` | — | 선택 | `0` |
| `0x0031` | `SetpointChangeAmount` | `int16s` | — | 선택 | `null`, nullable |
| `0x0032` | `SetpointChangeSourceTimestamp` | `epoch-s` | — | 선택 | `MS` |
| `0x003A` | `EmergencyHeatDelta` | `UnsignedTemperature` | `manage` | 선택 | `255`, nonVolatile |
| `0x0052` | `SetpointHoldExpiryTimestamp` | `epoch-s` | — | 선택 | `null`, nullable, nonVolatile |

설정점 한계 등 여러 속성의 추가 제약은 XML에서 `<desc/>`로만 표시된다. 제공된 조각에는 해당 설명 본문이 없다.

#### AC 관련 속성

모두 선택 속성이다.

| ID | 이름 | 타입 | 쓰기 | 기본값·품질 |
|---|---|---|---|---|
| `0x0040` | `ACType` | `ACTypeEnum` | `manage` | `0`, nonVolatile |
| `0x0041` | `ACCapacity` | `uint16` | `manage` | `0`, nonVolatile |
| `0x0042` | `ACRefrigerantType` | `ACRefrigerantTypeEnum` | `manage` | `0`, nonVolatile |
| `0x0043` | `ACCompressorType` | `ACCompressorTypeEnum` | `manage` | `0`, nonVolatile |
| `0x0044` | `ACErrorCode` | `ACErrorCodeBitmap` | `manage` | `0` |
| `0x0045` | `ACLouverPosition` | `ACLouverPositionEnum` | `manage` | `0`, nonVolatile |
| `0x0046` | `ACCoilTemperature` | `temperature` | — | `null`, nullable |
| `0x0047` | `ACCapacityFormat` | `ACCapacityFormatEnum` | `manage` | `0`, nonVolatile |

#### 프리셋·스케줄·제안

| ID | 이름 | 타입 / 목록 항목 타입 | 쓰기 | 적합성 | 제약·품질 |
|---|---|---|---|---|---|
| `0x0048` | `PresetTypes` | `list` / `PresetTypeStruct` | — | `PRES` 필수 | `1`–`7`개, fixed |
| `0x0049` | `ScheduleTypes` | `list` / `ScheduleTypeStruct` | — | `MSCH` 필수 | `1`–`3`개, fixed |
| `0x004A` | `NumberOfPresets` | `uint8` | — | `PRES` 필수 | 최소 `1`, fixed |
| `0x004B` | `NumberOfSchedules` | `uint8` | — | `MSCH` 필수 | 최소 `1`, fixed |
| `0x004C` | `NumberOfScheduleTransitions` | `uint8` | — | `MSCH` 필수 | 최소 `1`, fixed |
| `0x004D` | `NumberOfScheduleTransitionPerDay` | `uint8` | — | `MSCH` 필수 | 최소 `1`, nullable, fixed |
| `0x004E` | `ActivePresetHandle` | `octstr` | — | `PRES` 필수 | 최대 길이 `16`, nullable, nonVolatile |
| `0x004F` | `ActiveScheduleHandle` | `octstr` | — | `MSCH` 필수 | 최대 길이 `16`, nullable, nonVolatile |
| `0x0050` | `Presets` | `list` / `PresetStruct` | `manage` | `PRES` 필수 | 최대 `NumberOfPresets`개, atomicWrite, nonVolatile |
| `0x0051` | `Schedules` | `list` / `ScheduleStruct` | `manage` | `MSCH` 필수 | 최대 `NumberOfSchedules`개, atomicWrite, nonVolatile |
| `0x0053` | `MaxThermostatSuggestions` | `uint8` | — | `TSUGGEST` 필수 | 최소 `5`, fixed |
| `0x0054` | `ThermostatSuggestions` | `list` / `ThermostatSuggestionStruct` | — | `TSUGGEST` 필수 | 최대 `MaxThermostatSuggestions`개, nonVolatile |
| `0x0055` | `CurrentThermostatSuggestion` | `ThermostatSuggestionStruct` | — | `TSUGGEST` 필수 | nullable |
| `0x0056` | `ThermostatSuggestionNotFollowingReason` | `ThermostatSuggestionNotFollowingReasonBitmap` | — | `TSUGGEST` 필수 | nullable |

#### 보호·센서 속성

다음 항목에는 `provisionalConform`이 포함된다.

| ID | 이름 | 타입 / 목록 항목 타입 | 쓰기 | 기능 조건 | 제약·품질 |
|---|---|---|---|---|---|
| `0x0057` | `CriticalFreezeProtection` | `bool` | — | `HEAT` 선택 | `false`, nonVolatile |
| `0x0058` | `CriticalOverheatProtection` | `bool` | — | `COOL` 선택 | `false`, nonVolatile |
| `0x0059` | `Sensors` | `list` / `ThermostatSensorStruct` | — | `SENSORS` 필수 | 최대 `32`개 |
| `0x005A` | `AvailableSensorHandles` | `list` / `octstr` | `manage` | `SENSORS` 필수 | 최대 `32`개, 항목 최대 길이 `16`, nonVolatile |
| `0x005B` | `EnabledSensorHandles` | `list` / `octstr` | `manage` | `SENSORS` 필수 | 최대 `32`개, 항목 최대 길이 `16`, nonVolatile |
| `0x005C` | `NumberOfSensorScheduleTransitions` | `uint8` | — | `SENSORS` 필수 | fixed |
| `0x005D` | `SensorSchedule` | `list` / `SensorScheduleTransitionStruct` | `manage` | `SENSORS` 필수 | 최대 `NumberOfSensorScheduleTransitions`개, atomicWrite, nonVolatile |

#### `obsoleteConform` 속성

| ID | 이름 | 타입 | 쓰기 | 제약·품질 |
|---|---|---|---|---|
| `0x0007` | `PICoolingDemand` | `uint8` | — | `0`–`100` |
| `0x0008` | `PIHeatingDemand` | `uint8` | — | `0`–`100` |
| `0x0009` | `HVACSystemTypeConfiguration` | `HVACSystemTypeBitmap` | 선택적 `manage` | — |
| `0x0020` | `StartOfWeek` | `StartOfWeekEnum` | — | fixed |
| `0x0021` | `NumberOfWeeklyTransitions` | `uint8` | — | fixed |
| `0x0022` | `NumberOfDailyTransitions` | `uint8` | — | fixed |
| `0x0025` | `ThermostatProgrammingOperationMode` | `ProgrammingOperationModeBitmap` | `manage` | — |
| `0x0034` | `OccupiedSetback` | `UnsignedTemperature` | `manage` | `OccupiedSetbackMin`–`OccupiedSetbackMax`, nullable, nonVolatile |
| `0x0035` | `OccupiedSetbackMin` | `UnsignedTemperature` | — | 최대 `OccupiedSetbackMax`, nullable, fixed |
| `0x0036` | `OccupiedSetbackMax` | `UnsignedTemperature` | — | `OccupiedSetbackMin`–`254`, nullable, fixed |
| `0x0037` | `UnoccupiedSetback` | `UnsignedTemperature` | `manage` | `UnoccupiedSetbackMin`–`UnoccupiedSetbackMax`, nullable, nonVolatile |
| `0x0038` | `UnoccupiedSetbackMin` | `UnsignedTemperature` | — | 최대 `UnoccupiedSetbackMax`, nullable, fixed |
| `0x0039` | `UnoccupiedSetbackMax` | `UnsignedTemperature` | — | `UnoccupiedSetbackMin`–`254`, nullable, fixed |

### 데이터 타입

#### 수치 타입

| 이름 | 기반 타입 |
|---|---|
| `SignedTemperature` | `int8` |
| `TemperatureDifference` | `int16` |
| `UnsignedTemperature` | `uint8` |

#### 열거형

| 타입 | 값과 항목 |
|---|---|
| `SystemModeEnum` | `0`: `Off`, `1`: `Auto`, `3`: `Cool`, `4`: `Heat`, `5`: `EmergencyHeat`, `6`: `Precooling`, `7`: `FanOnly`, `8`: `Dry`, `9`: `Sleep` |
| `ThermostatRunningModeEnum` | `0`: `Off`, `3`: `Cool`, `4`: `Heat` |
| `ControlSequenceOfOperationEnum` | `0`: `CoolingOnly`, `1`: `CoolingWithReheat`, `2`: `HeatingOnly`, `3`: `HeatingWithReheat`, `4`: `CoolingAndHeating`, `5`: `CoolingAndHeatingWithReheat` |
| `SetpointRaiseLowerModeEnum` | `0`: `Heat`, `1`: `Cool`, `2`: `Both` |
| `TemperatureSetpointHoldEnum` | `0`: `SetpointHoldOff`, `1`: `SetpointHoldOn` |
| `SetpointChangeSourceEnum` | `0`: `Manual`, `1`: `Schedule`, `2`: `External` |
| `PresetScenarioEnum` | `1`: `Occupied`, `2`: `Unoccupied`, `3`: `Sleep`, `4`: `Wake`, `5`: `Vacation`, `6`: `GoingToSleep`, `254`: `UserDefined` |
| `StartOfWeekEnum` | `0`: `Sunday`, `1`: `Monday`, `2`: `Tuesday`, `3`: `Wednesday`, `4`: `Thursday`, `5`: `Friday`, `6`: `Saturday` |
| `ACCapacityFormatEnum` | `0`: `BTUh` |
| `ACCompressorTypeEnum` | `0`: `Unknown`, `1`: `T1`, `2`: `T2`, `3`: `T3` |
| `ACLouverPositionEnum` | `1`: `Closed`, `2`: `Open`, `3`: `Quarter`, `4`: `Half`, `5`: `ThreeQuarters` |
| `ACRefrigerantTypeEnum` | `0`: `Unknown`, `1`: `R22`, `2`: `R410a`, `3`: `R407c` |
| `ACTypeEnum` | `0`: `Unknown`, `1`: `CoolingFixed`, `2`: `HeatPumpFixed`, `3`: `CoolingInverter`, `4`: `HeatPumpInverter` |

- `SystemModeEnum`의 `Auto`는 `AUTO` 조건에서 필수다. 난방·냉방 관련 항목에는 각각 `HEAT`, `COOL` 조건이 있다.
- `SetpointRaiseLowerModeEnum`의 `Both`는 `HEAT` 또는 `COOL` 조건에서 필수다.
- `SetpointChangeSourceEnum`의 `Schedule`은 `MSCH` 조건의 선택 항목이다.
- `TemperatureSetpointHoldEnum`의 `SetpointHoldOff`는 스케줄을 따르고, `SetpointHoldOn`은 스케줄 전환과 무관하게 현재 설정점을 유지한다.

#### 비트맵

| 타입 | bit 또는 범위와 항목 |
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

`ScheduleTypeFeaturesBitmap`의 `SupportsPresets`, `SupportsSetpoints`에는 최소 하나를 선택하는 조건이 있으며, `SupportsPresets`는 `PRES`를 조건으로 한다.

#### 구조체

| 구조체 | 필드 ID와 이름 | 주요 제약 |
|---|---|---|
| `PresetStruct` | `0` `PresetHandle`, `1` `PresetScenario`, `2` `Name`, `3` `CoolingSetpoint`, `4` `HeatingSetpoint`, `5` `BuiltIn` | `PresetHandle`: nullable, 최대 `16`; `Name`: 선택·nullable, 최대 `64`, 기본값 `null`; 설정점은 각각 `COOL`, `HEAT` 조건에서 필수, 기본값 `2600`, `2000`; `BuiltIn`: nullable, 기본값 `false` |
| `PresetTypeStruct` | `0` `PresetScenario`, `1` `NumberOfPresets`, `2` `PresetTypeFeatures` | 모두 필수. 뒤의 두 필드 기본값 `0` |
| `ScheduleStruct` | `0` `ScheduleHandle`, `1` `SystemMode`, `2` `Name`, `3` `PresetHandle`, `4` `Transitions`, `5` `BuiltIn` | `ScheduleHandle`: nullable, 최대 `16`; `Name`: 선택, 최대 `64`; `PresetHandle`: 선택, 최대 `16`; `Transitions`: `ScheduleTransitionStruct` 목록, `1`–`NumberOfScheduleTransitions`개, 기본값 `empty`; `BuiltIn`: nullable, 기본값 `false` |
| `ScheduleTransitionStruct` | `0` `DayOfWeek`, `1` `TransitionTime`, `2` `PresetHandle`, `3` `SystemMode`, `4` `CoolingSetpoint`, `5` `HeatingSetpoint` | `TransitionTime` 최대 `1439`; `PresetHandle`은 `PRES` 조건의 선택 필드, 최대 `16`; `SystemMode` 선택; 설정점은 각각 `COOL`, `HEAT` 조건의 선택 필드 |
| `ScheduleTypeStruct` | `0` `SystemMode`, `1` `NumberOfSchedules`, `2` `ScheduleTypeFeatures` | 모두 필수. `NumberOfSchedules` 최대값은 같은 이름의 속성, 기본값 `0`; `ScheduleTypeFeatures` 기본값 `0` |
| `SensorScheduleTransitionStruct` | `0` `DayOfWeek`, `1` `TransitionTime`, `2` `EnabledSensorHandles` | 모두 필수. 시간 최대 `1439`; 핸들 최대 `32`개, 항목 최대 길이 `16` |
| `ThermostatSensorStruct` | `0` `Name`, `1` `SensorHandle`, `2` `Cluster`, `3` `Endpoint`, `4` `Node`, `5` `FabricIndex` | 이름 최대 `64`, 핸들 최대 `16`; `Endpoint` 선택; `Endpoint`가 있으면 `Node`, `FabricIndex` 필수 |
| `ThermostatSuggestionStruct` | `0` `UniqueID`, `1` `PresetHandle`, `2` `EffectiveTime`, `3` `ExpirationTime` | 모두 필수. `UniqueID`: `uint8`; 핸들 최대 `16`; 시간 타입 `epoch-s` |
| `WeeklyScheduleTransitionStruct` | `0` `TransitionTime`, `1` `HeatSetpoint`, `2` `CoolSetpoint` | 모두 필수. 시간 최대 `1439`; 설정점 nullable |

### 명령

#### `commandToServer`

| ID | 이름 | 권한 | 적합성 | 필드 | response |
|---|---|---|---|---|---|
| `0x00` | `SetpointRaiseLower` | `operate` | 필수 | `0` `Mode`: `SetpointRaiseLowerModeEnum`; `1` `Amount`: `int8` | `Y` |
| `0x01` | `SetWeeklySchedule` | `manage` | obsolete | `0` `NumberOfTransitionsForSequence`; `1` `DayOfWeekForSequence`; `2` `ModeForSequence`; `3` `Transitions` | `Y` |
| `0x02` | `GetWeeklySchedule` | `operate` | obsolete | `0` `DaysToReturn`: `ScheduleDayOfWeekBitmap`; `1` `ModeToReturn`: `ScheduleModeBitmap` | `GetWeeklyScheduleResponse` |
| `0x03` | `ClearWeeklySchedule` | `manage` | obsolete | なし | `Y` |
| `0x05` | `SetActiveScheduleRequest` | `operate` | `MSCH` 必須 | `0` `ScheduleHandle`: `octstr`、最大 `16` | `Y` |
| `0x06` | `SetActivePresetRequest` | `operate` | `PRES` 필수 | `0` `PresetHandle`: nullable `octstr`, 최대 `16` | `Y` |
| `0x07` | `AddThermostatSuggestion` | `manage` | `TSUGGEST` 필수 | `0` `PresetHandle`: 최대 `16`; `1` `EffectiveTime`: nullable `epoch-s`; `2` `ExpirationInMinutes`: `uint16`, `30`–`1440` | `AddThermostatSuggestionResponse` |
| `0x08` | `RemoveThermostatSuggestion` | `manage` | `TSUGGEST` 필수 | `0` `UniqueID`: `uint8` | `Y` |

`SetWeeklySchedule`의 `Transitions`는 `WeeklyScheduleTransitionStruct` 목록이며 최대 `10`개다.

#### `responseFromServer`

| ID | 이름 | 적합성 | 필드 |
|---|---|---|---|
| `0x00` | `GetWeeklyScheduleResponse` | obsolete | `NumberOfTransitionsForSequence`, `DayOfWeekForSequence`, `ModeForSequence`, `Transitions`; `SetWeeklySchedule`과 같은 필드 구성 |
| `0x02` | `AddThermostatSuggestionResponse` | `TSUGGEST` 필수 | `0` `UniqueID`: `uint8` |

### 이벤트

모든 이벤트의 priority는 `info`, 읽기 권한은 `view`이며 `provisionalConform`을 포함한다.

| ID | 이름 | 기능 조건 | 필드 |
|---|---|---|---|
| `0x00` | `SystemModeChange` | `TEVT` | `0` `PreviousSystemMode` 선택; `1` `CurrentSystemMode` 필수 |
| `0x01` | `LocalTemperatureChange` | `TEVT` 및 `LTNE` 미사용 | `0` `CurrentLocalTemperature` 필수·nullable |
| `0x02` | `OccupancyChange` | `TEVT` 및 `OCC` | `0` `PreviousOccupancy` 선택; `1` `CurrentOccupancy` 필수 |
| `0x03` | `SetpointChange` | `TEVT` | `0` `SystemMode` 필수, `Heat` 또는 `Cool`; `1` `Occupancy`는 `OCC` 조건에서 필수, 기본값 `1`; `2` `PreviousSetpoint` 선택; `3` `CurrentSetpoint` 필수 |
| `0x04` | `RunningStateChange` | `TEVT` | `0` `PreviousRunningState` 선택; `1` `CurrentRunningState` 필수 |
| `0x05` | `RunningModeChange` | `TEVT` 및 `AUTO` | `0` `PreviousRunningMode` 선택; `1` `CurrentRunningMode` 필수 |
| `0x06` | `ActiveScheduleChange` | `TEVT` 및 `MSCH` | `0` `PreviousScheduleHandle` 선택·nullable; `1` `CurrentScheduleHandle` 필수·nullable. 각각 최대 `16` |
| `0x07` | `ActivePresetChange` | `TEVT` 및 `PRES` | `0` `PreviousPresetHandle` 선택·nullable; `1` `CurrentPresetHandle` 필수·nullable. 각각 최대 `16` |

### 최근 revision 변경

- revision `7`: 보정·deadband 제약 갱신, `Presets`, `MatterScheduleConfiguration` 도입.
- revision `8`: `ControlSequenceOfOperation` 쓰기 관련 설명 추가.
- revision `9`: `AlarmMask`, `AlarmCodeBitmap` 제거.
- revision `10`: Zigbee 관련 요소와 `P` 품질 제거, `ThermostatProgrammingOperationMode`, `Setback` 및 관련 요소의 사용 중단.
- revision `11`: 제안 및 이벤트 지원 추가.
- revision `12`: `TemperatureSetpointHoldDuration` 최소값 `1`, 보호 속성 및 센서 스케줄 지원 추가.

revision `10` 설명에는 `ProgrammingOperationModeBitmap` 제거가 기록되어 있지만, 제공된 XML의 데이터 타입 정의에는 해당 비트맵이 남아 있다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml`

### 생성 정보와 클러스터 메타데이터

- 생성 도구: `Alchemy`
- 원본: `src/app_clusters/Thermostat.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`
- 생성 주석에 `DO NOT EDIT`가 명시되어 있다.
- client와 server 모두 활성화되어 있으며 `tick="false"`, `init="false"`다.
- globalAttribute `0xFFFD` 값은 `12`다.

### 타입 표현

| 스펙 표현 | SDK 표현 |
|---|---|
| `uint8`, `uint16` | `int8u`, `int16u` |
| `int8` | `int8s` |
| `bool` | `boolean` |
| `octstr` | `octet_string` |
| `string` | `char_string` |
| `epoch-s` | `epoch_s` |
| `cluster-id`, `endpoint-no`, `node-id`, `fabric-idx` | `cluster_id`, `endpoint_no`, `node_id`, `fabric_idx` |
| `list` 및 `entry` | 속성의 `array` / `entryType`, 필드의 `array="true"` |
| nullable | `isNullable="true"` |
| atomicWrite | `mustUseAtomicWrite="true"` |

열거형은 `enum8`이다. 비트맵 크기는 다음과 같다.

- `bitmap32`: `ACErrorCodeBitmap`
- `bitmap16`: `ScheduleTypeFeaturesBitmap`, `RelayStateBitmap`, `PresetTypeFeaturesBitmap`, `ThermostatSuggestionNotFollowingReasonBitmap`
- `bitmap8`: `HVACSystemTypeBitmap`, `OccupancyBitmap`, `ProgrammingOperationModeBitmap`, `RemoteSensingBitmap`, `ScheduleDayOfWeekBitmap`, `ScheduleModeBitmap`

### 원자적 쓰기 명령

SDK XML에는 스펙 조각의 명령 목록에 없는 다음 명령이 추가되어 있다.

| code | source | 이름 | 인자 |
|---|---|---|---|
| `0xFE` | `client` | `AtomicRequest` | `RequestType`: `AtomicRequestTypeEnum`; `AttributeRequests`: `attrib_id` 배열; `Timeout`: 선택적 `int16u` |
| `0xFD` | `server` | `AtomicResponse` | `StatusCode`: `status`; `AttributeStatus`: `AtomicAttributeStatusStruct` 배열; `Timeout`: 선택적 `int16u` |

`AtomicRequest`의 response는 `AtomicResponse`다.

### 스펙과 구분해야 하는 정의

- 속성 `0x0047`의 이름은 스펙에서 `ACCapacityFormat`, SDK에서 **`ACCapacityformat`**이다. 대소문자를 통일하지 않는다.
- 스펙에서 `obsoleteConform`인 여러 항목은 SDK에서 `deprecateConform` 또는 기능 조건과 결합된 `otherwiseConform`으로 남아 있다.
- `LocalTemperatureCalibration`은 SDK에서 `int8s`, `min="-127"`이다.
- `TemperatureSetpointHoldDuration`은 SDK에서도 nullable이며 `min="1"`, `max="1440"`이다.
- `ThermostatSensorStruct`의 `Endpoint`, `Node`, `FabricIndex`는 SDK 필드에서 `optional="true"`다. 스펙의 `Node`, `FabricIndex`에는 `Endpoint`에 따른 필수 조건이 있다.
- `Presets`, `Schedules`, `SensorSchedule`의 SDK 목록 길이는 `255`로 표현되지만, 스펙의 최대 개수는 각각 대응하는 개수 속성을 참조한다.
- `TEVT`, `SENSORS`, 보호 속성, 센서 속성 및 이벤트에는 `apiMaturity="provisional"` 표시가 있다.
- SDK 이벤트 설명은 `LocalTemperatureChange`를 온도가 유의하게 변경될 때 발생하는 이벤트로 기술하지만, 유의한 변경의 수치 기준은 제공하지 않는다.

## 구현

### 구성과 delegate 선택

주요 파일:

- `src/app/clusters/thermostat-server/ThermostatCluster.h`
- `src/app/clusters/thermostat-server/DelegateResolution.h`
- `src/app/clusters/thermostat-server/ThermostatDelegate.h`
- `src/app/clusters/thermostat-server/ThermostatDelegate.cpp`

`ThermostatCluster`는 `ThermostatClusterBase`와 `AtomicWriteSession::Delegate`를 상속한다. `Delegates...`에 포함된 기반 인터페이스로 기능 객체의 포함 여부를 결정한다.

| 컴파일 시 플래그 | 대응 delegate |
|---|---|
| `kHasHeating` | `ThermostatHeatingSetpoints::Delegate` |
| `kHasCooling` | `ThermostatCoolingSetpoints::Delegate` |
| `kHasPresets` | `ThermostatPresets::Delegate` |
| `kHasHold` | `ThermostatHold::Delegate` |
| `kHasSuggestions` | `ThermostatSuggestions::Delegate` |
| `kHasOccupancy` | `ThermostatOccupancy::Delegate` |
| `kHasSensors` | `ThermostatSensors::Delegate` |

- `Thermostat::Delegate`가 필요하다.
- 난방 또는 냉방 delegate가 최소 하나 필요하다.
- `kHasSuggestions`가 참이면 `kHasPresets`도 참이어야 한다.
- `kRequiresAtomicWrite`는 `kHasPresets || kHasSensors`다.
- `ThermostatSetpoints`는 별도로 `ThermostatAutoSetpoints::Delegate`를 확인하여 `kHasAuto`를 결정한다.
- 기능 객체가 비활성화되면 `std::monostate`를 사용한다.
- `FullFeaturedThermostatCluster`는 기본·난방·냉방·자동 설정점·유지·프리셋·제안·점유·센서 delegate 타입을 포함하는 별칭이다.

`detail::FindDelegate`는 인자 순서대로 `std::is_base_of_v`를 검사하여 첫 일치 항목을 반환한다. 일치 항목이 없으면 컴파일 시 assertion이 발생한다. `ConstructFeature`, `MakeFeature`, `MakeAtomicWriteSession`, `kArgsHasDelegate`가 조건부 구성을 지원한다.

기본 `Delegate`는 온도, 모드, 실행 상태, 원격 감지 및 `FabricTable` 접근을 제공한다. 기본 `GetOutdoorTemperature`, `GetRemoteSensing`은 `Status::UnsupportedAttribute`를 반환한다. 기본 온도 보정 getter는 `0`, setter는 변경 없이 성공을 반환한다.

### 등록과 선택 속성

관련 파일:

- `src/app/clusters/thermostat-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-server/CodegenIntegration.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterAttributes.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp`

등록 흐름:

1. `ServerInit`이 `IntegrationDelegate`를 만든다.
2. `CodegenClusterIntegration::RegisterServer`에 endpoint, `Thermostat::Id`, 인스턴스 개수를 전달한다.
3. `CreateRegistration`이 `featureMap`을 `BitFlags<Thermostat::Feature>`로 변환한다.
4. `GetOptionalAttributes`가 기능 조건 및 `emberAfContainsAttribute`로 선택 속성을 결정한다.
5. `ThermostatClusterBase::Config`에 선택 속성과 `GetDefaultTimerDelegate`를 넣어 인스턴스를 생성한다.

`kThermostatEndpointCount`는 `kThermostatFixedClusterCount`와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합이다. `ClusterStorage`는 `LazyRegisteredServerCluster` 배열을 보관한다.

- `FindRegistration`: 미생성 인스턴스이면 `nullptr`.
- `FindClusterOnEndpoint`: 생성된 인스턴스의 endpoint를 검색.
- `ReleaseRegistration`: `Destroy` 호출.
- `ServerShutdown`: `CodegenClusterIntegration::UnregisterServer` 호출.

`OptionalAttributes`의 모든 플래그는 기본값 `false`다. `AppendOptionalAttributes`는 `enabled`인 항목의 metadata만 추가한다.

`MatterThermostatClusterInitCallback`, `MatterThermostatPluginServerInitCallback`, `MatterThermostatClusterShutdownCallback`은 비어 있는 weak 함수로 제공된다.

### 생명주기와 요청 분배

`ThermostatCluster::Startup`은 다음 순서로 실행된다.

1. `ThermostatClusterBase::Startup`
2. `mDelegate.Startup`
3. 필요한 경우 `mAtomicWriteSession.Startup`
4. `mSetpoints.Startup`
5. 필요한 경우 `mHold.Startup`

제공된 `Shutdown`은 `mDelegate.Shutdown`, 필요한 경우 `mAtomicWriteSession.Shutdown`, `ThermostatClusterBase::Shutdown`을 호출한다. 해당 함수 본문에는 `mSetpoints.Shutdown`, `mHold.Shutdown` 호출이 없다.

요청 분배는 다음과 같다.

- `ReadAttribute`: 설정점 → 유지 → 점유 → 프리셋 → 제안 → 센서 → 기본 처리.
- `WriteAttribute`: 프리셋 → 센서 → 원자적 쓰기 상태 검사 → 설정점 → 유지 → 기본 처리.
- `InvokeCommand`: 설정점 → 원자적 쓰기 → 프리셋 → 제안 → 기본 처리.

활성 설정점 속성 쓰기가 성공하면 프리셋 기능이 있는 경우 `SetActivePreset(DataModel::NullNullable)`를 호출한다. `SetpointRaiseLower`는 별도의 명령 경로에서 처리된다.

### 기본 읽기·쓰기와 상태 변경

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterRead.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp`

| 대상 | 구현 동작 |
|---|---|
| `ClusterRevision` | `Thermostat::kRevision` 인코딩 |
| `FeatureMap` | `mFeatures` 인코딩 |
| `LocalTemperature` | `Feature::kLocalTemperatureNotExposed`이면 `EncodeNull` |
| `RemoteSensing` 읽기 | `Feature::kLocalTemperatureNotExposed`이면 `RemoteSensingBitmap::kLocalTemperature` 제거 |
| `RemoteSensing` 쓰기 | 위 기능 사용 중 `RemoteSensingBitmap::kLocalTemperature`가 설정되면 `Status::ConstraintError` |
| `LocalTemperatureCalibration` 쓰기 | `int16_t`로 decode 후 `int8_t` 범위 검사 |
| `ControlSequenceOfOperation` 쓰기 요청 | 값을 적용하지 않고 `Status::Success` 반환 |
| `SetControlSequenceOfOperation` 직접 호출 | delegate setter를 호출하고 변경 시 알림 |
| `SystemMode` 쓰기 | 알 수 없는 enum은 `Status::InvalidValue`; 이후 `SetSystemMode` 수행 |
| `Schedules` 읽기 | TODO 상태로 빈 목록 반환 |
| 처리하지 않는 기본 속성 | `Status::UnsupportedAttribute` |

`SetSystemMode`는 `Auto`, `Cool`, `Heat`, `EmergencyHeat`, `Precooling`에 필요한 기능을 검사한다. 기능 조건을 충족하지 않거나 지원하지 않는 값이면 `Status::ConstraintError`다.

`SetRunningMode`, `SetRunningState`도 난방·냉방 관련 값과 기능의 일치 여부를 검사한다. delegate가 변경을 보고하면 속성 변경을 알리고 대응 이벤트 생성 함수를 호출한다.

### 설정점 모델과 보정

관련 파일:

- `src/app/clusters/thermostat-server/Temperature.h`
- `src/app/clusters/thermostat-server/Setpoint.h`
- `src/app/clusters/thermostat-server/Setpoint.cpp`
- `src/app/clusters/thermostat-server/SetpointLimits.h`
- `src/app/clusters/thermostat-server/SetpointRange.h`
- `src/app/clusters/thermostat-server/Setpoints.h`
- `src/app/clusters/thermostat-server/Setpoints.cpp`
- `src/app/clusters/thermostat-server/SetpointAttributes.h`
- `src/app/clusters/thermostat-server/SetpointAttributes.cpp`

`temperature`는 `int16_t`다.

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

- `Setpoint`: 속성 ID와 온도 접근 인터페이스. `Mode`는 난방 관련 ID에 `SystemModeEnum::kHeat`, 냉방 관련 ID에 `SystemModeEnum::kCool`, 그 외에 `SystemModeEnum::kOff`를 반환한다.
- `AbsoluteSetpoint`: 항상 온도 값을 가진다.
- `OptionalSetpoint`: override가 없으면 참조하는 `AbsoluteSetpoint` 값을 반환한다. `ClearTemperature`로 override를 해제한다.
- `SetpointLimits`: `Minimum`, `Maximum`, `IsValid`, `Valid`, `Clamp` 제공.
- `SetpointRange`: `heating`, `cooling` 보관.
- `Setpoints`: 절대 한계, 사용자 한계, 점유·비점유 범위 및 `deadBand` 보관.

`Setpoints::Valid`는 지원 기능에 따라 다음을 검사한다.

- 최소 한계가 최대 한계 이하인지.
- 명시적 사용자 한계가 절대 한계 내에 있는지.
- 점유 설정점과 필요한 비점유 설정점이 사용자 한계 내에 있는지.
- 자동 모드에서 냉방 값과 난방 값 사이의 간격이 `deadBand` 이상인지.

`Fix`는 `FixUserLimits`, `FixUserLimitDeadband`, `FixRange`로 보정을 수행하고 보정된 속성을 `changedAttributes`에 합친다. 최종 검증 결과에 따라 `Status::Success` 또는 `Status::ConstraintError`를 반환한다.

보정은 사용자가 변경한 쪽을 가능한 한 유지하고 반대쪽을 이동한다. 반대쪽 한계 때문에 유지할 수 없으면 양쪽을 조정한다.

`SetpointAttributes`는 ID를 bit 위치로 사용하는 `uint32_t` 맵이다. ID가 `32` 미만이라는 전제에 의존하므로 범용 속성 변경 추적기가 아니다. `FirstDirtyAttribute`는 최초 기록된 속성을 보관하며, 해당 속성을 지울 때 다른 남은 속성으로 재선정하지 않는다.

### 설정점 속성 처리와 `SetpointRaiseLower`

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp`

난방·냉방 delegate는 점유 설정점 getter/setter를 필수로 구현한다. 선택 한계 및 비점유 설정점의 기본 메서드는 `Status::UnsupportedAttribute`를 반환한다. 보호 상태 getter 기본 구현은 `false`와 `Status::Success`를 반환한다.

- 절대 한계가 선택 속성으로 활성화되지 않으면 기본 상수를 사용한다.
- 속성 쓰기는 `Setpoints::ClampMode::kDontClamp`를 사용한다.
- 절대 한계 및 보호 속성 쓰기는 `Status::UnsupportedWrite`다.
- `SaveSetpoints`는 유효성 검사 후 변경 속성만 delegate에 저장한다.
- delegate가 실제 변경이 없다고 보고하면 해당 변경 bit를 제거한다.
- 성공 후 `NotifyAttributesChanged`가 변경 속성을 알린다.
- `GenerateSetpointEvent`는 네 점유·비점유 설정점에 대해서만 `SetpointChange`를 생성한다.

`SetpointRaiseLower` 처리:

1. `IsOccupied`에 따라 대상 범위를 선택한다.
2. `request_data.amount * 10`을 내부 온도 증감량으로 사용한다.
3. `Heat`, `Cool`, `Both`에 따라 지원되는 설정점을 선택한다.
4. 선택 가능한 설정점이 없거나 mode가 유효하지 않으면 `Status::InvalidCommand`.
5. `ChangeRange`에 `Setpoints::ClampMode::kClamp`를 전달한다.
6. 보정 성공 시 `SaveSetpoints`를 호출한다.

`ThermostatAutoSetpoints::LoadDeadband`는 내부 값을 `kMinDeadBand * 10`–`kMaxDeadBand * 10` 범위로 검사한다. 읽을 때는 `deadband / 10`을 `int8_t`로 노출한다. `MinSetpointDeadBand` 쓰기는 범위를 검사하지만, 호환성을 위해 값을 변경하지 않고 성공을 반환한다.

### 유지 및 점유

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterHold.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHold.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp`

`ThermostatHold`는 `TemperatureSetpointHold`, `TemperatureSetpointHoldDuration`, `SetpointHoldExpiryTimestamp`를 delegate로 처리한다.

- 알 수 없는 `TemperatureSetpointHold` 값은 `Status::InvalidValue`.
- `TemperatureSetpointHoldDuration`은 null을 허용하고 `1440` 초과를 거부한다.
- 제공된 쓰기 함수에는 최소값 `1` 검사 없이 `0`이 delegate에 전달되는 경로가 있다.
- 스펙·SDK에서 읽기 전용인 `SetpointHoldExpiryTimestamp`에 대해서도 내부 `WriteAttribute` 분기가 존재한다. 이것만으로 외부 접근 제어까지 쓰기를 허용한다고 단정할 수는 없다.

`ThermostatOccupancy::SetOccupancy`는 delegate 변경 시 `NotifyAttributeChanged`를 호출한다. 제공된 함수에는 `GenerateOccupancyChangeEvent` 호출이 없다.

점유 기능이 없는 `ThermostatClusterBase::IsOccupied`는 `true`를 반환한다.

### 프리셋

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterPresets.h`
- `src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp`

`Presets` 편집은 원자적 쓰기 세션을 요구한다.

- 세션이 없으면 `InvalidInState`.
- 다른 주체의 세션이면 `Busy`.
- 세션 소유자의 읽기에는 pending 목록을 반환하고, 그 외에는 확정 목록을 반환한다.
- 전체 교체와 `AppendItem`을 처리한다.
- 그 외 목록 연산은 `CHIP_ERROR_NOT_IMPLEMENTED`.

`AppendPendingPreset`는 다음을 검사한다.

- 핸들 크기와 `PresetScenario` 유효성.
- null 핸들인 신규 프리셋이 built-in으로 지정되지 않았는지.
- non-null 핸들이 확정 목록에 존재하는지.
- pending 목록에 같은 핸들이 중복되지 않는지.
- 기존 항목과 `BuiltIn`이 일치하는지.
- 해당 시나리오와 이름 지원 여부.
- 전체 개수 및 시나리오별 개수 제한.

`PrecommitPresets`는 built-in 프리셋 제거를 `Status::ConstraintError`로, 활성 프리셋 제거를 `Status::InvalidInState`로 거부한다.

설정점 clamp 코드도 있으나, 원문 TODO는 **임시 복사본만 수정하여 실제 pending 목록에는 적용되지 않는다**고 명시한다.

`SetActivePreset`는 non-null 핸들이 확정 목록에 없으면 `Status::InvalidCommand`를 반환한다. 성공하면 delegate를 갱신하고 `ActivePresetHandle` 변경 및 `ActivePresetChange` 이벤트를 알린다.

새 프리셋의 고유 핸들 할당과 확정 저장은 `CommitPendingPresets` 구현 책임이다.

### 원자적 쓰기 세션

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp`

`AtomicWriteSession`은 `State::Closed`, `State::Open`, 속성 ID 목록, `ScopedNodeId`, 타이머 및 `FabricTable` delegate를 관리한다.

| 처리 | 동작 |
|---|---|
| `BuildAttributeStatuses` | 비어 있는 목록, 중복 ID, decode 오류, 알 수 없는 속성을 거부 |
| `BeginAtomicWrite` | `Presets`, `Schedules`, `SensorSchedule`을 대상 후보로 처리. `Timeout` 필수 |
| timeout 계산 | 요청값과 대상 속성별 최대 timeout 합 중 작은 값 |
| `OnAtomicWriteBegin` | pending 상태 준비 |
| 시작 실패 또는 타이머 실패 | rollback 후 상태 초기화 |
| `CommitAtomicWrite` | precommit 성공 시 commit, 이후 상태 초기화 및 응답 |
| `RollbackAtomicWrite` | 상태 초기화 후 rollback callback 및 응답 |
| `TimerFired` | `Rollback` 호출 |
| `OnFabricRemoved` | 해당 fabric의 세션이면 `Rollback` 호출 |
| `Shutdown` | `ResetAtomicWrite` 후 fabric delegate 해제 |

주체 기반 `InAtomicWrite`는 `Access::AuthMode::kCase`와 `ScopedNodeId` 일치를 검사한다.

다만 `CommitAtomicWrite`, `RollbackAtomicWrite`가 사용하는 `InAtomicWrite(CommandHandler * commandObj, AtomicAttributes & attributeStatuses)` 구현은 열린 상태와 속성 목록 일치만 검사하며, 전달된 `commandObj`로 소유자를 비교하지 않는다.

또한 제공된 `CommitAtomicWrite`는 precommit 실패 시 상태를 초기화하지만 rollback callback을 호출하지 않는다.

### 센서와 센서 스케줄

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSensors.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp`

`AvailableSensorHandles`, `EnabledSensorHandles`는 전체 교체와 `AppendItem`을 지원한다.

공통 검사:

- 최대 `32`개.
- 핸들 최대 길이 `16`.
- 중복 핸들 금지.

추가 검사와 동작:

- `AvailableSensorHandles` 항목은 `Sensors`에 구성된 핸들이어야 한다.
- `EnabledSensorHandles` 항목은 `AvailableSensorHandles`에 있어야 한다.
- 사용 가능 목록에서 제거된 핸들은 활성 목록에서도 제거된다.
- 지원하지 않는 목록 연산은 `Status::UnsupportedWrite`.

`SensorSchedule`은 소유자가 일치하는 원자적 쓰기 세션에서만 수정할 수 있다. 세션 소유자는 pending 스케줄을 읽는다.

`AppendPendingSensorScheduleTransition` 검사:

1. `DayOfWeek`의 `Away` bit 금지.
2. 요일 bit가 최소 하나 있어야 하며 `0x7F` 밖의 bit 금지.
3. `TransitionTime` 최대 `1439`.
4. 센서 핸들의 길이·개수·중복·사용 가능 여부 검사.
5. `NumberOfSensorScheduleTransitions` 개수 제한 검사.

`PrecommitSensorSchedule`는 같은 시간에 겹치는 요일을 가진 두 전환을 `Status::ConstraintError`로 거부한다. 확정 저장은 `CommitPendingSensorScheduleTransitions`에 위임한다.

### 제안

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp`

`AddThermostatSuggestion` 처리 순서:

1. `PresetHandle` 길이 및 `ExpirationInMinutes`의 `30`–`1440` 범위를 검사.
2. `GetClock_MatterEpochS` 실패 시 `Status::InvalidInState`.
3. 프리셋이 없으면 `Status::NotFound`.
4. 제안 개수 제한에 도달하면 `Status::ResourceExhausted`.
5. `EffectiveTime`이 현재 시각보다 24시간 넘게 미래이면 `Status::InvalidCommand`.
6. 만료된 제안을 제거.
7. `GetUniqueID`로 ID를 얻고 목록에 추가.
8. 속성 변경을 알리고 `ReEvaluateCurrentSuggestion` 수행.
9. `AddThermostatSuggestionResponse` 반환.

`EffectiveTime`이 null이면 현재 시각을 사용한다. 만료 시각은 적용 시각에 `ExpirationInMinutes`를 더하여 계산한다.

개수 제한 검사는 만료 항목 제거보다 먼저 수행된다.

`RemoveThermostatSuggestion`은 `UniqueID`로 검색하며, 없으면 `Status::NotFound`다. 제거 후 만료 항목 정리와 재평가를 수행한다.

재평가의 실제 선택 정책과 만료 추적은 delegate 책임이다. 구현은 재평가 전후의 null 상태와 `UniqueID`를 비교해 `CurrentThermostatSuggestion` 변경을 알리고, 활성 핸들이 바뀌면 `ActivePresetHandle` 변경을 알린다.

### 이벤트 생성

출처: `src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp`

각 `Generate…Event` 함수는 먼저 `Feature::kEvents`를 확인한다.

- `mContext`가 있으면 `interactionContext.eventsGenerator.GenerateEvent`를 사용한다.
- 없으면 `LogEvent`를 사용하고 실패를 로그로 남긴다.

제공된 구현에서 구분할 사항:

- `GenerateLocalTemperatureChangeEvent` 자체는 `Feature::kLocalTemperatureNotExposed`를 검사하지 않는다.
- `SetLocalTemperature`는 delegate가 변경을 보고하면 이벤트 생성 함수를 호출하며, 별도의 유의한 변화량 임계값 검사는 보이지 않는다.
- `GenerateSetpointChangeEvent`는 `occupancy`를 항상 `MakeOptional`로 설정한다.
- 이벤트 생성 함수의 존재와 모든 상태 변경 경로에서의 호출 여부는 동일하지 않다. 예를 들어 `ThermostatOccupancy::SetOccupancy`에는 이벤트 호출이 없다.

### 소유 저장소를 가진 구조체

| 구현 파일 | 타입과 동작 |
|---|---|
| `src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h` / `src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp` | `PresetStructWithOwnedMembers`: `kPresetHandleSize = 16`, `kPresetNameSize = 64`. 핸들·이름을 내부 버퍼로 복사. 크기 초과 시 `CHIP_ERROR_NO_MEMORY` |
| `src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h` / `src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp` | `SensorScheduleTransitionStructWithOwnedMembers`: `kMaxEnabledSensorsPerTransition = 32`, `kMaxSensorHandleSize = 16`. 목록·decode 목록·span 입력 지원. 개수 초과는 `CHIP_ERROR_INVALID_LIST_LENGTH`, 길이 초과는 `CHIP_ERROR_INVALID_STRING_LENGTH` |
| `src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h` / `src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp` | `ThermostatSensorStructWithOwnedMembers`: `kThermostatSensorNameMaxSize = 64`, `kThermostatSensorHandleMaxSize = 16`. 이름·핸들 내부 복사. 길이 초과는 `CHIP_ERROR_INVALID_STRING_LENGTH` |
| `src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h` / `src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp` | `ThermostatSuggestionStructWithOwnedMembers`: `kThermostatSuggestionPresetHandleSize = 16`. 핸들 내부 복사, 시간 접근에 `System::Clock::Seconds32` 사용 |

이 타입들은 대응 `Structs` 타입을 protected 상속하고 `Encode`, `kIsFabricScoped`를 노출한다.

`SensorScheduleTransitionStructWithOwnedMembers`, `ThermostatSensorStructWithOwnedMembers`는 같은 타입의 복사 생성자가 삭제되어 있지만 복사 대입은 제공한다.

### 이전 속성 접근 API 호환 계층

관련 파일:

- `src/app/clusters/thermostat-server/AttributeAccessorShim.h`
- `src/app/clusters/thermostat-server/AttributeAccessorShim.cpp`

이 계층은 Ember 접근 함수를 직접 사용하던 예제 앱과의 호환용이다. 원문 TODO는 생성된 클러스터 API 사용 또는 `all-devices` 이전 후 제거할 예정이라고 설명한다.

| 대상 | 동작 |
|---|---|
| `ControlSequenceOfOperation`, `SystemMode` | `Get`, `Set`을 클러스터 메서드로 전달 |
| `LocalTemperature` | nullable `Get`; `Set`에서 `MarkAttributeDirty::kNo`를 `DataModel::AttributeChangeType::kQuiet`로 변환 |
| `ThermostatRunningMode` | `SetRunningMode`로 전달 |
| `ThermostatRunningState` | `SetRunningState`로 전달 |
| `AbsMinHeatSetpointLimit`, `AbsMaxHeatSetpointLimit` | `GetSetpoints`로 읽기, `Set`은 `UnsupportedWrite` |
| `OccupiedCoolingSetpoint`, `OccupiedHeatingSetpoint` | `GetSetpoints`로 읽기, `Set`은 `UnsupportedWrite` |
| `FeatureMap` | 클러스터 존재 확인 후 실제 기능 변경 없이 `Success` |
| `PICoolingDemand`, `PIHeatingDemand` | 각각 `piCoolingDemand`, `piHeatingDemand` 정적 변수에 저장. endpoint별 저장이 아님 |

클러스터 조회가 필요한 접근은 `Thermostat::FindClusterOnEndpoint<FullFeaturedThermostatCluster>`를 사용하며, 찾지 못하면 `Protocols::InteractionModel::Status::UnsupportedEndpoint`를 반환한다.

### 구현 범위와 확인된 차이

- `Schedules` 읽기는 빈 목록을 반환하는 TODO다. 제공된 코드만으로 `MatterScheduleConfiguration` 전체 구현을 확인할 수 없다.
- `TemperatureSetpointHoldDuration`의 최소값 `1`은 스펙·SDK에 있지만 제공된 유지 쓰기 함수는 상한만 검사한다.
- SDK의 `LocalTemperatureCalibration` 최소값은 `-127`이나, 기본 쓰기 함수의 직접 범위 검사는 `int8_t` 전체 범위를 사용한다.
- `ControlSequenceOfOperation`, `MinSetpointDeadBand`, shim의 `FeatureMap`은 성공 응답이 실제 값 변경을 의미하지 않는 경로가 있다.
- 프리셋 precommit의 설정점 보정은 원문 TODO대로 임시 복사본만 수정한다.
- 원자적 쓰기의 소유자 검사와 실패 정리는 오버로드 및 처리 경로에 따라 다르므로, 일반적인 트랜잭션 보장을 추가로 가정하지 않는다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
