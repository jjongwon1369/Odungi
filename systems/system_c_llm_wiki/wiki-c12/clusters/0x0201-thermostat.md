---
entity: Thermostat
ids: ['0x0201']
source_paths: ['data_model/1.7/clusters/Thermostat.xml', 'src/app/clusters/thermostat-server/AttributeAccessorShim.cpp', 'src/app/clusters/thermostat-server/AttributeAccessorShim.h', 'src/app/clusters/thermostat-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-server/CodegenIntegration.h', 'src/app/clusters/thermostat-server/DelegateResolution.h', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/Setpoint.cpp', 'src/app/clusters/thermostat-server/Setpoint.h', 'src/app/clusters/thermostat-server/SetpointAttributes.cpp', 'src/app/clusters/thermostat-server/SetpointAttributes.h', 'src/app/clusters/thermostat-server/SetpointLimits.h', 'src/app/clusters/thermostat-server/SetpointRange.h', 'src/app/clusters/thermostat-server/Setpoints.cpp', 'src/app/clusters/thermostat-server/Setpoints.h', 'src/app/clusters/thermostat-server/Temperature.h', 'src/app/clusters/thermostat-server/ThermostatCluster.h', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAtomic.h', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterAttributes.h', 'src/app/clusters/thermostat-server/ThermostatClusterBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterHold.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterHold.h', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterPresets.h', 'src/app/clusters/thermostat-server/ThermostatClusterRead.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSensors.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp', 'src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h', 'src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp', 'src/app/clusters/thermostat-server/ThermostatDelegate.cpp', 'src/app/clusters/thermostat-server/ThermostatDelegate.h', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp', 'src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h', 'src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Thermostat

## 개요

`Thermostat`은 온도 조절기의 기능을 구성하고 제어하는 클러스터다. 난방·냉방 설정값, 점유 상태, 운전 모드, 프리셋, 스케줄, 제안, 센서 스케줄링을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0201` |
| 스펙 이름 | `Thermostat Cluster` |
| 클러스터 이름 | `Thermostat` |
| revision | `12` |
| 도메인 | `HVAC` |
| 분류 | hierarchy=`base`, role=`application` |
| PICS 코드 | `TSTAT` |
| 범위 | `Endpoint` |

제공된 구현은 `ThermostatCluster`와 기능별 `Delegate`를 조합하는 구조다. 스펙·SDK에 정의된 기능과 제공된 코드에서 실제 처리하는 범위는 구분해야 한다. 특히 `Schedules` 읽기는 빈 목록을 반환하는 TODO 상태다.

## 스펙

출처: `data_model/1.7/clusters/Thermostat.xml`

### 기능

| bit | code | name | 기능 및 적합성 |
|---|---|---|---|
| `0` | `HEAT` | `Heating` | 난방 장치 관리. `AUTO` 사용 시 필수이며, 그 외에는 `COOL`과 함께 최소 하나 선택 |
| `1` | `COOL` | `Cooling` | 냉방 장치 관리. `AUTO` 사용 시 필수이며, 그 외에는 `HEAT`과 함께 최소 하나 선택 |
| `2` | `OCC` | `Occupancy` | 점유·비점유 설정값 지원. 선택 |
| `3` | `SCH` | `ScheduleConfiguration` | `obsoleteConform` |
| `4` | `SB` | `Setback` | `obsoleteConform` |
| `5` | `AUTO` | `AutoMode` | `Auto` 모드 지원. 선택 |
| `6` | `LTNE` | `LocalTemperatureNotExposed` | `LocalTemperature` 속성으로 로컬 온도 값을 노출하지 않음. 선택 |
| `7` | `MSCH` | `MatterScheduleConfiguration` | 향상된 스케줄 지원. 선택 |
| `8` | `PRES` | `Presets` | 설정값 프리셋 지원. 선택 |
| `9` | `TEVT` | `Events` | 이벤트 지원. `otherwiseConform`에 `provisionalConform`, `optionalConform` 정의 |
| `10` | `TSUGGEST` | `ThermostatSuggestions` | 제안 지원. `PRES` 조건의 선택 기능 |
| `11` | `SENSORS` | `ThermostatSensors` | 센서 스케줄링 지원. `provisionalConform` |

### 속성

아래 표의 모든 속성은 읽기 권한이 `view`다.

- `R`: 읽기.
- `RW`: 읽기·쓰기. 괄호는 쓰기 권한.
- `W 선택`: 쓰기 지원이 선택 사항.
- `nullable`, `fixed`, `nonVolatile`, `atomicWrite`는 원문의 품질 표시다.
- `—`는 해당 표 항목에 별도로 기재할 값이 없음을 뜻한다.
- 원문에서 `<desc/>`만 제공한 제약은 구체적인 규칙으로 확장하지 않는다.

#### 온도, 설정값 및 운전 상태

| ID | 이름 | 타입 | 접근 | 적합성 | 기본값·품질·명시적 제약 |
|---|---|---|---|---|---|
| `0x0000` | `LocalTemperature` | `temperature` | R | 필수 | `nullable` |
| `0x0001` | `OutdoorTemperature` | `temperature` | R | 선택 | `null`, `nullable` |
| `0x0002` | `Occupancy` | `OccupancyBitmap` | R | `OCC` 필수 | — |
| `0x0003` | `AbsMinHeatSetpointLimit` | `temperature` | R | `HEAT` 선택 | `700`, `fixed` |
| `0x0004` | `AbsMaxHeatSetpointLimit` | `temperature` | R | `HEAT` 선택 | `3000`, `fixed` |
| `0x0005` | `AbsMinCoolSetpointLimit` | `temperature` | R | `COOL` 선택 | `1600`, `fixed` |
| `0x0006` | `AbsMaxCoolSetpointLimit` | `temperature` | R | `COOL` 선택 | `3200`, `fixed` |
| `0x0010` | `LocalTemperatureCalibration` | `SignedTemperature` | RW (`manage`) | `LTNE` 미사용 시 선택 | `0`, `nonVolatile` |
| `0x0011` | `OccupiedCoolingSetpoint` | `temperature` | RW (`operate`) | `COOL` 필수 | `2600`, `nonVolatile` |
| `0x0012` | `OccupiedHeatingSetpoint` | `temperature` | RW (`operate`) | `HEAT` 필수 | `2000`, `nonVolatile` |
| `0x0013` | `UnoccupiedCoolingSetpoint` | `temperature` | RW (`operate`) | `COOL` 및 `OCC` 필수 | `2600`, `nonVolatile` |
| `0x0014` | `UnoccupiedHeatingSetpoint` | `temperature` | RW (`operate`) | `HEAT` 및 `OCC` 필수 | `2000`, `nonVolatile` |
| `0x0015` | `MinHeatSetpointLimit` | `temperature` | RW (`manage`) | `HEAT` 선택 | 기본값 `AbsMinHeatSetpointLimit`, `nonVolatile` |
| `0x0016` | `MaxHeatSetpointLimit` | `temperature` | RW (`manage`) | `HEAT` 선택 | 기본값 `AbsMaxHeatSetpointLimit`, `nonVolatile` |
| `0x0017` | `MinCoolSetpointLimit` | `temperature` | RW (`manage`) | `COOL` 선택 | 기본값 `AbsMinCoolSetpointLimit`, `nonVolatile` |
| `0x0018` | `MaxCoolSetpointLimit` | `temperature` | RW (`manage`) | `COOL` 선택 | 기본값 `AbsMaxCoolSetpointLimit`, `nonVolatile` |
| `0x0019` | `MinSetpointDeadBand` | `SignedTemperature` | R, W 선택 (`manage`) | `AUTO` 필수 | `20`, `nonVolatile`, `0`–`127` |
| `0x001A` | `RemoteSensing` | `RemoteSensingBitmap` | RW (`manage`) | 선택 | `0`, `nonVolatile` |
| `0x001B` | `ControlSequenceOfOperation` | `ControlSequenceOfOperationEnum` | RW (`manage`) | 필수 | `nonVolatile` |
| `0x001C` | `SystemMode` | `SystemModeEnum` | RW (`manage`) | 필수 | `nonVolatile` |
| `0x001E` | `ThermostatRunningMode` | `ThermostatRunningModeEnum` | R | `TEVT` 및 `AUTO`이면 필수, 그 외 `AUTO` 조건에서 선택 | `0` |
| `0x0023` | `TemperatureSetpointHold` | `TemperatureSetpointHoldEnum` | RW (`manage`) | 선택 | `0`, `nonVolatile` |
| `0x0024` | `TemperatureSetpointHoldDuration` | `uint16` | RW (`manage`) | 선택 | `null`, `nullable`, `nonVolatile`, `1`–`1440` |
| `0x0029` | `ThermostatRunningState` | `RelayStateBitmap` | R | 선택 | — |
| `0x0030` | `SetpointChangeSource` | `SetpointChangeSourceEnum` | R | 선택 | `0` |
| `0x0031` | `SetpointChangeAmount` | `int16s` | R | 선택 | `null`, `nullable` |
| `0x0032` | `SetpointChangeSourceTimestamp` | `epoch-s` | R | 선택 | `MS` |
| `0x003A` | `EmergencyHeatDelta` | `UnsignedTemperature` | RW (`manage`) | 선택 | `255`, `nonVolatile` |
| `0x0052` | `SetpointHoldExpiryTimestamp` | `epoch-s` | R | 선택 | `null`, `nullable`, `nonVolatile` |

#### AC 관련 속성

모두 선택 속성이다.

| ID | 이름 | 타입 | 접근 | 기본값·품질 |
|---|---|---|---|---|
| `0x0040` | `ACType` | `ACTypeEnum` | RW (`manage`) | `0`, `nonVolatile` |
| `0x0041` | `ACCapacity` | `uint16` | RW (`manage`) | `0`, `nonVolatile` |
| `0x0042` | `ACRefrigerantType` | `ACRefrigerantTypeEnum` | RW (`manage`) | `0`, `nonVolatile` |
| `0x0043` | `ACCompressorType` | `ACCompressorTypeEnum` | RW (`manage`) | `0`, `nonVolatile` |
| `0x0044` | `ACErrorCode` | `ACErrorCodeBitmap` | RW (`manage`) | `0` |
| `0x0045` | `ACLouverPosition` | `ACLouverPositionEnum` | RW (`manage`) | `0`, `nonVolatile` |
| `0x0046` | `ACCoilTemperature` | `temperature` | R | `null`, `nullable` |
| `0x0047` | `ACCapacityFormat` | `ACCapacityFormatEnum` | RW (`manage`) | `0`, `nonVolatile` |

#### 프리셋 및 스케줄

| ID | 이름 | 타입 또는 목록 항목 타입 | 접근 | 적합성 | 품질·제약 |
|---|---|---|---|---|---|
| `0x0048` | `PresetTypes` | `list` / `PresetTypeStruct` | R | `PRES` 필수 | `fixed`, 항목 수 `1`–`7` |
| `0x0049` | `ScheduleTypes` | `list` / `ScheduleTypeStruct` | R | `MSCH` 필수 | `fixed`, 항목 수 `1`–`3` |
| `0x004A` | `NumberOfPresets` | `uint8` | R | `PRES` 필수 | `fixed`, 최소 `1` |
| `0x004B` | `NumberOfSchedules` | `uint8` | R | `MSCH` 필수 | `fixed`, 최소 `1` |
| `0x004C` | `NumberOfScheduleTransitions` | `uint8` | R | `MSCH` 필수 | `fixed`, 최소 `1` |
| `0x004D` | `NumberOfScheduleTransitionPerDay` | `uint8` | R | `MSCH` 필수 | `nullable`, `fixed`, 최소 `1` |
| `0x004E` | `ActivePresetHandle` | `octstr` | R | `PRES` 필수 | `nullable`, `nonVolatile`, 최대 길이 `16` |
| `0x004F` | `ActiveScheduleHandle` | `octstr` | R | `MSCH` 필수 | `nullable`, `nonVolatile`, 최대 길이 `16` |
| `0x0050` | `Presets` | `list` / `PresetStruct` | RW (`manage`) | `PRES` 필수 | `nonVolatile`, `atomicWrite`, 최대 항목 수 `NumberOfPresets` |
| `0x0051` | `Schedules` | `list` / `ScheduleStruct` | RW (`manage`) | `MSCH` 필수 | `nonVolatile`, `atomicWrite`, 최대 항목 수 `NumberOfSchedules` |

#### 제안, 보호 및 센서

| ID | 이름 | 타입 또는 목록 항목 타입 | 접근 | 적합성 | 기본값·품질·제약 |
|---|---|---|---|---|---|
| `0x0053` | `MaxThermostatSuggestions` | `uint8` | R | `TSUGGEST` 필수 | `fixed`, 최소 `5` |
| `0x0054` | `ThermostatSuggestions` | `list` / `ThermostatSuggestionStruct` | R | `TSUGGEST` 필수 | `nonVolatile`, 최대 항목 수 `MaxThermostatSuggestions` |
| `0x0055` | `CurrentThermostatSuggestion` | `ThermostatSuggestionStruct` | R | `TSUGGEST` 필수 | `nullable` |
| `0x0056` | `ThermostatSuggestionNotFollowingReason` | `ThermostatSuggestionNotFollowingReasonBitmap` | R | `TSUGGEST` 필수 | `nullable` |
| `0x0057` | `CriticalFreezeProtection` | `bool` | R | `provisionalConform`, `HEAT` 선택 | `false`, `nonVolatile` |
| `0x0058` | `CriticalOverheatProtection` | `bool` | R | `provisionalConform`, `COOL` 선택 | `false`, `nonVolatile` |
| `0x0059` | `Sensors` | `list` / `ThermostatSensorStruct` | R | `provisionalConform`, `SENSORS` 필수 | 최대 항목 수 `32` |
| `0x005A` | `AvailableSensorHandles` | `list` / `octstr` | RW (`manage`) | `provisionalConform`, `SENSORS` 필수 | `nonVolatile`, 최대 `32`개, 항목 최대 길이 `16` |
| `0x005B` | `EnabledSensorHandles` | `list` / `octstr` | RW (`manage`) | `provisionalConform`, `SENSORS` 필수 | `nonVolatile`, 최대 `32`개, 항목 최대 길이 `16` |
| `0x005C` | `NumberOfSensorScheduleTransitions` | `uint8` | R | `provisionalConform`, `SENSORS` 필수 | `fixed` |
| `0x005D` | `SensorSchedule` | `list` / `SensorScheduleTransitionStruct` | RW (`manage`) | `provisionalConform`, `SENSORS` 필수 | `nonVolatile`, `atomicWrite`, 최대 항목 수 `NumberOfSensorScheduleTransitions` |

#### 폐기된 속성

다음 속성은 스펙 XML에서 `obsoleteConform`으로 표시된다.

| ID | 이름 | 타입 | 접근 | 품질·명시적 제약 |
|---|---|---|---|---|
| `0x0007` | `PICoolingDemand` | `uint8` | R | `0`–`100` |
| `0x0008` | `PIHeatingDemand` | `uint8` | R | `0`–`100` |
| `0x0009` | `HVACSystemTypeConfiguration` | `HVACSystemTypeBitmap` | R, W 선택 (`manage`) | — |
| `0x0020` | `StartOfWeek` | `StartOfWeekEnum` | R | `fixed` |
| `0x0021` | `NumberOfWeeklyTransitions` | `uint8` | R | `fixed` |
| `0x0022` | `NumberOfDailyTransitions` | `uint8` | R | `fixed` |
| `0x0025` | `ThermostatProgrammingOperationMode` | `ProgrammingOperationModeBitmap` | RW (`manage`) | — |
| `0x0034` | `OccupiedSetback` | `UnsignedTemperature` | RW (`manage`) | `nullable`, `nonVolatile`, `OccupiedSetbackMin`–`OccupiedSetbackMax` |
| `0x0035` | `OccupiedSetbackMin` | `UnsignedTemperature` | R | `nullable`, `fixed`, 최대 `OccupiedSetbackMax` |
| `0x0036` | `OccupiedSetbackMax` | `UnsignedTemperature` | R | `nullable`, `fixed`, `OccupiedSetbackMin`–`254` |
| `0x0037` | `UnoccupiedSetback` | `UnsignedTemperature` | RW (`manage`) | `nullable`, `nonVolatile`, `UnoccupiedSetbackMin`–`UnoccupiedSetbackMax` |
| `0x0038` | `UnoccupiedSetbackMin` | `UnsignedTemperature` | R | `nullable`, `fixed`, 최대 `UnoccupiedSetbackMax` |
| `0x0039` | `UnoccupiedSetbackMax` | `UnsignedTemperature` | R | `nullable`, `fixed`, `UnoccupiedSetbackMin`–`254` |

### 데이터 타입

#### 수치 타입

| 이름 | 기반 타입 |
|---|---|
| `SignedTemperature` | `int8` |
| `TemperatureDifference` | `int16` |
| `UnsignedTemperature` | `uint8` |

#### 열거형

| 타입 | 값과 이름 |
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

주요 조건은 다음과 같다.

- `SystemModeEnum.Auto`는 `AUTO`에서 필수다.
- `Cool`, `Precooling`은 `COOL`, `Heat`, `EmergencyHeat`는 `HEAT` 조건으로 정의된다.
- `SetpointRaiseLowerModeEnum.Both`는 `HEAT` 또는 `COOL`에서 필수다.
- `SetpointHoldOff`는 스케줄을 따르고, `SetpointHoldOn`은 스케줄 전환과 관계없이 현재 설정값을 유지한다.
- `SetpointChangeSourceEnum.Schedule`은 `MSCH` 조건이다.

#### 비트맵

| 타입 | bit 또는 범위와 필드 |
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

`ScheduleTypeFeaturesBitmap`의 `SupportsPresets`와 `SupportsSetpoints`는 최소 하나를 선택하는 그룹이며, `SupportsPresets`에는 `PRES` 조건이 있다.

#### 구조체

필드 앞 숫자는 원문의 field ID다.

| 구조체 | 필드 |
|---|---|
| `PresetStruct` | `0` `PresetHandle`: `octstr`, 필수·nullable·최대 `16`; `1` `PresetScenario`: `PresetScenarioEnum`, 필수; `2` `Name`: `string`, 선택·nullable·최대 `64`, 기본값 `null`; `3` `CoolingSetpoint`: `temperature`, `COOL` 필수, 기본값 `2600`; `4` `HeatingSetpoint`: `temperature`, `HEAT` 필수, 기본값 `2000`; `5` `BuiltIn`: `bool`, 필수·nullable, 기본값 `false` |
| `PresetTypeStruct` | `0` `PresetScenario`: `PresetScenarioEnum`; `1` `NumberOfPresets`: `uint8`, 기본값 `0`; `2` `PresetTypeFeatures`: `PresetTypeFeaturesBitmap`, 기본값 `0`. 모두 필수 |
| `ScheduleStruct` | `0` `ScheduleHandle`: `octstr`, 필수·nullable·최대 `16`; `1` `SystemMode`: `SystemModeEnum`, 필수; `2` `Name`: `string`, 선택·최대 `64`; `3` `PresetHandle`: `octstr`, 선택·최대 `16`; `4` `Transitions`: `ScheduleTransitionStruct` 목록, 필수, 기본값 `empty`, 항목 수 `1`–`NumberOfScheduleTransitions`; `5` `BuiltIn`: `bool`, 필수·nullable, 기본값 `false` |
| `ScheduleTransitionStruct` | `0` `DayOfWeek`: `ScheduleDayOfWeekBitmap`, 필수; `1` `TransitionTime`: `uint16`, 필수·최대 `1439`; `2` `PresetHandle`: `octstr`, `PRES` 조건의 선택·최대 `16`; `3` `SystemMode`: `SystemModeEnum`, 선택; `4` `CoolingSetpoint`: `temperature`, `COOL` 조건의 선택; `5` `HeatingSetpoint`: `temperature`, `HEAT` 조건의 선택 |
| `ScheduleTypeStruct` | `0` `SystemMode`: `SystemModeEnum`; `1` `NumberOfSchedules`: `uint8`, 기본값 `0`, 최대 `NumberOfSchedules` 속성 값; `2` `ScheduleTypeFeatures`: `ScheduleTypeFeaturesBitmap`, 기본값 `0`. 모두 필수 |
| `SensorScheduleTransitionStruct` | `0` `DayOfWeek`: `ScheduleDayOfWeekBitmap`; `1` `TransitionTime`: `uint16`, 최대 `1439`; `2` `EnabledSensorHandles`: `octstr` 목록, 최대 `32`개, 각 항목 최대 `16`. 모두 필수 |
| `ThermostatSensorStruct` | `0` `Name`: `string`, 필수·최대 `64`; `1` `SensorHandle`: `octstr`, 필수·최대 `16`; `2` `Cluster`: `cluster-id`, 필수; `3` `Endpoint`: `endpoint-no`, 선택; `4` `Node`: `node-id`, `Endpoint` 존재 시 필수; `5` `FabricIndex`: `fabric-idx`, `Endpoint` 존재 시 필수 |
| `ThermostatSuggestionStruct` | `0` `UniqueID`: `uint8`; `1` `PresetHandle`: `octstr`, 최대 `16`; `2` `EffectiveTime`: `epoch-s`; `3` `ExpirationTime`: `epoch-s`. 모두 필수 |
| `WeeklyScheduleTransitionStruct` | `0` `TransitionTime`: `uint16`, 최대 `1439`; `1` `HeatSetpoint`: `temperature`, nullable; `2` `CoolSetpoint`: `temperature`, nullable. 모두 필수 |

### 명령

#### `commandToServer`

| ID | 이름 | 권한 | 적합성 | 필드 | response |
|---|---|---|---|---|---|
| `0x00` | `SetpointRaiseLower` | `operate` | 필수 | `0` `Mode`: `SetpointRaiseLowerModeEnum`; `1` `Amount`: `int8` | `Y` |
| `0x01` | `SetWeeklySchedule` | `manage` | `obsoleteConform` | `0` `NumberOfTransitionsForSequence`: `uint8`; `1` `DayOfWeekForSequence`: `ScheduleDayOfWeekBitmap`; `2` `ModeForSequence`: `ScheduleModeBitmap`; `3` `Transitions`: `WeeklyScheduleTransitionStruct` 목록, 최대 `10` | `Y` |
| `0x02` | `GetWeeklySchedule` | `operate` | `obsoleteConform` | `0` `DaysToReturn`: `ScheduleDayOfWeekBitmap`; `1` `ModeToReturn`: `ScheduleModeBitmap` | `GetWeeklyScheduleResponse` |
| `0x03` | `ClearWeeklySchedule` | `manage` | `obsoleteConform` | 없음 | `Y` |
| `0x05` | `SetActiveScheduleRequest` | `operate` | `MSCH` 필수 | `0` `ScheduleHandle`: `octstr`, 최대 `16` | `Y` |
| `0x06` | `SetActivePresetRequest` | `operate` | `PRES` 필수 | `0` `PresetHandle`: `octstr`, nullable·최대 `16` | `Y` |
| `0x07` | `AddThermostatSuggestion` | `manage` | `TSUGGEST` 필수 | `0` `PresetHandle`: `octstr`, 최대 `16`; `1` `EffectiveTime`: `epoch-s`, nullable; `2` `ExpirationInMinutes`: `uint16`, `30`–`1440` | `AddThermostatSuggestionResponse` |
| `0x08` | `RemoveThermostatSuggestion` | `manage` | `TSUGGEST` 필수 | `0` `UniqueID`: `uint8` | `Y` |

위 명령의 필드는 모두 필수이며, nullable 여부는 필드 생략 가능 여부와 별개다.

#### `responseFromServer`

| ID | 이름 | 적합성 | 필드 |
|---|---|---|---|
| `0x00` | `GetWeeklyScheduleResponse` | `obsoleteConform` | `NumberOfTransitionsForSequence`, `DayOfWeekForSequence`, `ModeForSequence`, `Transitions`. 타입·field ID는 `SetWeeklySchedule`과 동일 |
| `0x02` | `AddThermostatSuggestionResponse` | `TSUGGEST` 필수 | `0` `UniqueID`: `uint8`, 필수 |

### 이벤트

모두 priority=`info`, readPrivilege=`view`이며, `otherwiseConform`에 `provisionalConform`과 아래 필수 조건이 정의된다.

| ID | 이름 | 필수 조건 | 필드 |
|---|---|---|---|
| `0x00` | `SystemModeChange` | `TEVT` | `0` `PreviousSystemMode`: `SystemModeEnum`, 선택; `1` `CurrentSystemMode`: `SystemModeEnum`, 필수 |
| `0x01` | `LocalTemperatureChange` | `TEVT` 및 `LTNE` 미사용 | `0` `CurrentLocalTemperature`: `temperature`, 필수·nullable |
| `0x02` | `OccupancyChange` | `TEVT` 및 `OCC` | `0` `PreviousOccupancy`: `OccupancyBitmap`, 선택; `1` `CurrentOccupancy`: `OccupancyBitmap`, 필수 |
| `0x03` | `SetpointChange` | `TEVT` | `0` `SystemMode`: `SystemModeEnum`, 필수, `Heat` 또는 `Cool`; `1` `Occupancy`: `OccupancyBitmap`, `OCC` 필수, 기본값 `1`; `2` `PreviousSetpoint`: `temperature`, 선택; `3` `CurrentSetpoint`: `temperature`, 필수 |
| `0x04` | `RunningStateChange` | `TEVT` | `0` `PreviousRunningState`: `RelayStateBitmap`, 선택; `1` `CurrentRunningState`: `RelayStateBitmap`, 필수 |
| `0x05` | `RunningModeChange` | `TEVT` 및 `AUTO` | `0` `PreviousRunningMode`: `ThermostatRunningModeEnum`, 선택; `1` `CurrentRunningMode`: `ThermostatRunningModeEnum`, 필수 |
| `0x06` | `ActiveScheduleChange` | `TEVT` 및 `MSCH` | `0` `PreviousScheduleHandle`: `octstr`, 선택·nullable; `1` `CurrentScheduleHandle`: `octstr`, 필수·nullable. 둘 다 최대 `16` |
| `0x07` | `ActivePresetChange` | `TEVT` 및 `PRES` | `0` `PreviousPresetHandle`: `octstr`, 선택·nullable; `1` `CurrentPresetHandle`: `octstr`, 필수·nullable. 둘 다 최대 `16` |

### revision 이력의 주요 변경

- revision `6`: `LTNE` 도입.
- revision `7`: 로컬 온도 보정 및 최소 설정값 간격 제약 갱신, `Presets`와 `MatterScheduleConfiguration` 도입.
- revision `8`: `ControlSequenceOfOperation` 쓰기 관련 설명 추가.
- revision `9`: `AlarmMask`, `AlarmCodeBitmap` 제거.
- revision `10`: Zigbee 관련 요소 및 `P` 품질 제거, `ThermostatProgrammingOperationMode`와 `Setback` 관련 요소 사용 중단.
- revision `11`: 제안 및 이벤트 추가.
- revision `12`: `TemperatureSetpointHoldDuration` 최소값 `1`, 보호 속성 및 센서 스케줄링 추가.

revision `10` 설명에는 `ProgrammingOperationModeBitmap` 제거가 기재되어 있지만, 제공된 XML의 `dataTypes`에는 해당 타입이 남아 있다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-cluster.xml`

### 생성 정보 및 클러스터 메타데이터

- Alchemy 생성 파일이며 직접 편집하지 않도록 표시되어 있다.
- 생성 원본: `src/app_clusters/Thermostat.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`
- 생성 매개변수에 `provisional-policy=loose` 포함.
- 클러스터 define: `THERMOSTAT_CLUSTER`
- client와 server 모두 활성화되며, 각각 `tick="false"`, `init="false"`.
- 전역 속성 `0xFFFD` 값: `12`.

### 타입 표현

| 스펙 표현 | SDK XML 표현 |
|---|---|
| `uint8` | `int8u` |
| `uint16` | `int16u` |
| `int8` | `int8s` |
| `bool` | `boolean` |
| `octstr` | `octet_string` |
| `string` | `char_string` |
| `epoch-s` | `epoch_s` |
| `list` | 속성은 `array`와 `entryType`, 구조체 필드는 `array="true"` |

열거형은 `enum8`로 정의된다. 비트맵의 기반 타입은 다음과 같다.

| 기반 타입 | 비트맵 |
|---|---|
| `bitmap8` | `HVACSystemTypeBitmap`, `OccupancyBitmap`, `ProgrammingOperationModeBitmap`, `RemoteSensingBitmap`, `ScheduleDayOfWeekBitmap`, `ScheduleModeBitmap` |
| `bitmap16` | `ScheduleTypeFeaturesBitmap`, `RelayStateBitmap`, `PresetTypeFeaturesBitmap`, `ThermostatSuggestionNotFollowingReasonBitmap` |
| `bitmap32` | `ACErrorCodeBitmap` |

### 원자적 쓰기 명령

스펙 입력의 클러스터 명령 목록에는 없지만 SDK XML에는 다음 명령이 명시되어 있다.

| ID | 이름 | source | 필드 |
|---|---|---|---|
| `0xFE` | `AtomicRequest` | `client` | `RequestType`: `AtomicRequestTypeEnum`; `AttributeRequests`: `attrib_id` 배열; `Timeout`: `int16u`, 선택 |
| `0xFD` | `AtomicResponse` | `server` | `StatusCode`: `status`; `AttributeStatus`: `AtomicAttributeStatusStruct` 배열; `Timeout`: `int16u`, 선택 |

`AtomicRequest`의 response는 `AtomicResponse`다. 원문의 두 명령은 각 `arg`에 모두 `id="0"`을 사용하므로, 이를 별도의 field ID로 보정하지 않는다.

`Presets`, `Schedules`, `SensorSchedule`에는 `mustUseAtomicWrite="true"`가 지정된다.

### 스펙 입력과 구분되는 정의

| 항목 | 스펙 XML | SDK XML |
|---|---|---|
| `0x0047` 속성 이름 | `ACCapacityFormat` | `ACCapacityformat` |
| `SCH` | `obsoleteConform` | `deprecateConform` |
| `SB` 및 일부 이전 속성·명령 | `obsoleteConform` | `optionalConform` 또는 기존 기능 조건과 `deprecateConform`을 유지 |
| `LocalTemperatureCalibration` | `SignedTemperature` / `int8` | `int8s`, `min="-127"` |
| `MinSetpointDeadBand` 쓰기 | 선택 | `writable="true"` |
| 사용자 설정값 한계 기본값 | 대응하는 절대 한계 속성 참조 | `700`, `3000`, `1600`, `3200`을 직접 지정 |
| `NumberOfScheduleTransitionPerDay` | nullable, 최소 `1` | nullable, 최소 `1`, 최대 `254` |
| `Presets`, `Schedules`, `SensorSchedule` 최대 항목 수 | 각각 대응하는 개수 속성 참조 | `length="255"` |
| `ThermostatSensorStruct.Node`, `ThermostatSensorStruct.FabricIndex` | `Endpoint` 존재 시 필수 | `optional="true"` |

`PresetStruct.CoolingSetpoint`와 `PresetStruct.HeatingSetpoint`는 SDK 구조체에서 `optional="true"`로 표현된다. 스펙의 필수 여부는 각각 `COOL`, `HEAT` 조건이다.

## 구현

### 구성과 기능 선택

주요 파일:

- `src/app/clusters/thermostat-server/ThermostatCluster.h`
- `src/app/clusters/thermostat-server/DelegateResolution.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterBase.cpp`
- `src/app/clusters/thermostat-server/ThermostatDelegate.h`
- `src/app/clusters/thermostat-server/ThermostatDelegate.cpp`

`ThermostatCluster`는 `ThermostatClusterBase`와 `AtomicWriteSession::Delegate`를 상속하는 가변 인자 클래스 템플릿이다.

| 컴파일 시점 플래그 | 판별하는 인터페이스 |
|---|---|
| `kHasHeating` | `ThermostatHeatingSetpoints::Delegate` |
| `kHasCooling` | `ThermostatCoolingSetpoints::Delegate` |
| `kHasPresets` | `ThermostatPresets::Delegate` |
| `kHasHold` | `ThermostatHold::Delegate` |
| `kHasSuggestions` | `ThermostatSuggestions::Delegate` |
| `kHasOccupancy` | `ThermostatOccupancy::Delegate` |
| `kHasSensors` | `ThermostatSensors::Delegate` |

- `Thermostat::Delegate`가 필요하다.
- `kHasHeating` 또는 `kHasCooling` 중 하나 이상이 참이어야 한다.
- `kHasSuggestions`가 참이면 `kHasPresets`도 참이어야 한다.
- `kRequiresAtomicWrite`는 `kHasPresets || kHasSensors`다.
- `ThermostatSetpoints`는 별도로 `ThermostatAutoSetpoints::Delegate`에서 `kHasAuto`를 판별한다.
- 비활성 기능 멤버는 `std::monostate`로 구성된다.
- `FullFeaturedThermostatCluster`는 기본, 난방, 냉방, 자동 설정값, 유지, 프리셋, 제안, 점유, 센서 인터페이스를 모두 포함하는 별칭이다.

`detail::FindDelegate`는 인자 순서대로 `std::is_base_of_v`를 검사하여 처음 일치하는 인터페이스를 반환한다. 일치 항목이 없으면 컴파일 시점 assertion이 발생한다. `detail::MakeFeature`와 `detail::MakeAtomicWriteSession`은 활성화 여부에 따라 실제 객체 또는 `std::monostate`를 생성한다.

#### 수명주기와 요청 분배

`Startup` 순서는 다음과 같다.

1. `ThermostatClusterBase::Startup`
2. `mDelegate.Startup`
3. 필요한 경우 `mAtomicWriteSession.Startup`
4. `mSetpoints.Startup`
5. 필요한 경우 `mHold.Startup`

제공된 `ThermostatCluster::Shutdown`은 `mDelegate.Shutdown`, 필요한 경우 `mAtomicWriteSession.Shutdown`, `ThermostatClusterBase::Shutdown`을 호출한다.

요청 분배 순서는 다음과 같다.

- 읽기: `mSetpoints` → `mHold` → `mOccupancy` → `mPresets` → `mSuggestions` → `mSensors` → 기본 처리.
- 쓰기: `mPresets` → `mSensors` → 원자적 쓰기 상태 검사 → `mSetpoints` → `mHold` → 기본 처리.
- 명령: `mSetpoints` → `mAtomicWriteSession` → `mPresets` → `mSuggestions` → 기본 처리.

설정값 속성 쓰기가 성공하고 `IsActiveSetpoint`가 참이면 `mPresets.SetActivePreset(DataModel::NullNullable)`을 호출한다. 이 동작은 해당 속성 쓰기 경로에 있으며, `SetpointRaiseLower` 명령 경로와 동일하다고 가정하지 않는다.

### 코드 생성 통합 및 선택 속성

관련 파일:

- `src/app/clusters/thermostat-server/CodegenIntegration.h`
- `src/app/clusters/thermostat-server/CodegenIntegration.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterAttributes.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAttributes.cpp`

`ServerInit`은 최소 하나의 인터페이스 인자를 요구하며 `CodegenClusterIntegration::RegisterServer`를 호출한다.

- `kThermostatFixedClusterCount`: `Thermostat::StaticApplicationConfig::kFixedClusterConfig.size()`.
- `kThermostatEndpointCount`: 고정 개수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합.
- 등록 설정은 `fetchFeatureMap = true`, `fetchOptionalAttributes = false`.
- `BaseIntegrationDelegate::GetOptionalAttributes`가 `emberAfContainsAttribute`와 기능 비트를 사용해 선택 속성을 결정한다.
- `ClusterStorage`는 `LazyRegisteredServerCluster` 배열을 보유한다.
- `IntegrationDelegate::CreateRegistration`은 `ThermostatClusterBase::Config`를 구성하고 인터페이스 인자가 있을 때 클러스터를 생성한다.
- `FindClusterOnEndpoint`는 생성된 인스턴스의 endpoint를 비교한다.
- `ServerShutdown`은 `CodegenClusterIntegration::UnregisterServer`를 호출한다.
- `GetDefaultTimerDelegate`는 함수 내부의 정적 `DefaultTimerDelegate`를 반환한다.

`OptionalAttributes`의 필드는 모두 기본값이 `false`다. `AppendOptionalAttributes`는 `enabled`인 항목의 메타데이터만 추가한다.

다음 콜백은 빈 weak 정의로 제공된다.

- `MatterThermostatClusterInitCallback`
- `MatterThermostatPluginServerInitCallback`
- `MatterThermostatClusterShutdownCallback`

### 기본 속성 처리

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterRead.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterWrite.cpp`

#### 읽기

- `ClusterRevision`: `Thermostat::kRevision`을 인코딩한다.
- `FeatureMap`: `mFeatures`를 인코딩한다.
- `LocalTemperature`: `Feature::kLocalTemperatureNotExposed`이면 null을 반환한다.
- `RemoteSensing`: 같은 기능이 설정되어 있으면 `RemoteSensingBitmap::kLocalTemperature`를 제거한 뒤 반환한다.
- `Schedules`: TODO 주석과 함께 빈 목록을 반환한다.
- 처리하지 않는 속성: `Status::UnsupportedAttribute`.

#### 쓰기와 내부 setter

| 경로 | 동작 |
|---|---|
| `LocalTemperatureCalibration` 속성 쓰기 | `int16_t`로 디코딩한 뒤 `int8_t` 범위를 검사하고 `Delegate`에 전달 |
| `MinSetpointDeadBand` 속성 쓰기 | `0`–`127`을 검사하지만 값은 변경하지 않고 `Status::Success` 반환 |
| `RemoteSensing` 속성 쓰기 | `LTNE` 상태에서 `RemoteSensingBitmap::kLocalTemperature`가 설정되면 `Status::ConstraintError` |
| `ControlSequenceOfOperation` 속성 쓰기 | 값을 적용하지 않고 `Status::Success` 반환 |
| `SetControlSequenceOfOperation` | 내부 API는 `mDelegate.SetControlSequenceOfOperation`을 호출하고 변경 시 알림 |
| `SystemMode` 속성 쓰기 | 알려지지 않은 열거형이면 `Status::InvalidValue`; 그 외 `SetSystemMode` 호출 |
| `SetSystemMode` | `Auto`, `Cool`, `Heat`, `EmergencyHeat`, `Precooling`의 기능 조건 검사. 부적합하면 `Status::ConstraintError` |
| `SetRunningMode` | `Off`, 지원되는 `Cool` 또는 `Heat`만 허용 |
| `SetRunningState` | 난방·냉방 릴레이 비트가 해당 기능 없이 설정되면 `Status::ConstraintError` |

`SetSystemMode`, `SetLocalTemperature`, `SetRunningMode`, `SetRunningState`는 `Delegate`가 실제 변경을 보고하면 속성 알림과 해당 이벤트 생성 함수를 호출한다.

기본 `Delegate` 구현에서:

- `GetOutdoorTemperature`, `GetRemoteSensing`은 `Status::UnsupportedAttribute`.
- `GetLocalTemperatureCalibration`은 `0`.
- `SetLocalTemperatureCalibration`은 `changed = false`로 두고 `Status::Success`.
- 기본 `IsOccupied`는 `true`.

### 설정값 모델과 보정

관련 파일:

- `src/app/clusters/thermostat-server/Temperature.h`
- `src/app/clusters/thermostat-server/Setpoint.h`
- `src/app/clusters/thermostat-server/Setpoint.cpp`
- `src/app/clusters/thermostat-server/SetpointAttributes.h`
- `src/app/clusters/thermostat-server/SetpointAttributes.cpp`
- `src/app/clusters/thermostat-server/SetpointLimits.h`
- `src/app/clusters/thermostat-server/SetpointRange.h`
- `src/app/clusters/thermostat-server/Setpoints.h`
- `src/app/clusters/thermostat-server/Setpoints.cpp`

#### 기본값

`temperature`는 `int16_t`의 별칭이다.

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

`ThermostatAutoSetpoints::ReadAttribute`는 내부 간격을 `10`으로 나누어 `MinSetpointDeadBand`로 노출한다. 따라서 속성 기본값 `20`과 내부 기본값 `200`은 서로 다른 표현이다.

#### 모델

- `Setpoint`: 속성 ID와 온도 접근 인터페이스. `Mode`는 난방 속성에 `SystemModeEnum::kHeat`, 냉방 속성에 `SystemModeEnum::kCool`, 그 외에 `SystemModeEnum::kOff`를 반환한다.
- `AbsoluteSetpoint`: 항상 온도 값을 보유한다.
- `OptionalSetpoint`: 재정의 값이 없으면 참조하는 `AbsoluteSetpoint`의 온도를 반환한다. `ClearTemperature`는 재정의를 제거한다.
- `SetpointLimits`: `minimum`, `maximum`, `IsValid`, `Valid`, `Clamp`를 제공한다.
- `SetpointRange`: `heating`, `cooling`을 함께 보유한다.
- `SetpointAttributes`: 속성 ID를 비트 위치로 사용하는 변경 집합이다. ID가 `32` 미만이라는 전제에 의존하며 범용 속성 추적기가 아니다.

#### 검증 및 보정

`Setpoints::Valid`는 지원 기능에 따라 다음을 검사한다.

- 절대 한계와 사용자 한계의 최소·최대 순서.
- 명시된 사용자 한계가 절대 한계 내부인지 여부.
- 점유·비점유 설정값이 사용자 한계 내부인지 여부.
- `autoSupported`일 때 냉방 값과 난방 값의 차이가 `deadBand` 이상인지 여부.

`Setpoints::Fix`는 다음 순서로 보정한다.

1. `FixUserLimits`: 사용자 한계를 절대 한계에 맞추고 최소·최대 역전을 조정.
2. `FixUserLimitDeadband`: 자동 모드의 사용자 한계 간격 조정.
3. `FixRange`: 점유 설정값 및 필요한 경우 비점유 설정값 조정.
4. 보정된 속성을 `changedAttributes`에 병합.
5. 재검증 후 `Status::Success` 또는 `Status::ConstraintError` 반환.

난방 측을 변경한 경우 냉방 측을 올리고, 냉방 측을 변경한 경우 난방 측을 내리는 방향으로 간격을 맞춘다. 반대편 한계를 넘으면 경계값에 맞춘 뒤 변경 측도 조정한다.

`ChangeRange`는:

- 두 입력이 모두 없으면 `Status::ConstraintError`.
- `ClampMode::kClamp`이면 사용자 한계로 제한.
- `ClampMode::kDontClamp`이면 범위 밖 입력을 거부.
- 변경 후 `Fix`를 수행.

`ChangeLimits`는 최소·최대를 동시에 제공하면 `Status::InvalidCommand`, 절대 한계 밖이면 `Status::ConstraintError`를 반환한다.

### 설정값 속성 및 `SetpointRaiseLower`

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSetpointsBase.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHeatingSetpoints.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.h`
- `src/app/clusters/thermostat-server/ThermostatClusterCoolingSetpoints.cpp`

`ThermostatHeatingSetpoints`와 `ThermostatCoolingSetpoints`는 각각 해당 속성을 읽고, `Setpoints`에 로드하고, 검증된 변경을 `Delegate`에 저장한다.

- 점유 설정값의 getter와 setter는 순수 가상 함수다.
- 선택 한계 및 비점유 설정값의 기본 구현은 `Status::UnsupportedAttribute`.
- 절대 한계가 선택 속성으로 활성화되지 않으면 기본 상수를 사용한다.
- 절대 한계와 `CriticalFreezeProtection`, `CriticalOverheatProtection` 쓰기는 `Status::UnsupportedWrite`.
- 보호 상태의 기본 getter는 `false`와 `Status::Success`를 반환한다.
- 속성 쓰기는 `ClampMode::kDontClamp`를 사용한다.
- 저장 시 `changed`가 거짓인 속성은 변경 집합에서 제거한다.
- `GenerateSetpointEvent`는 네 점유·비점유 설정값에 대해서만 이벤트를 생성한다.

`SetpointRaiseLower` 처리 흐름:

1. 현재 점유 상태에 맞는 `SetpointRange` 선택.
2. `request_data.amount * 10`으로 내부 변경량 계산.
3. `Heat`, `Cool`, `Both`에 따라 지원되는 설정값 선택.
4. 알 수 없는 모드 또는 변경 가능한 설정값이 없으면 `Status::InvalidCommand`.
5. `ClampMode::kClamp`로 변경·보정한 뒤 `SaveSetpoints` 수행.

`ThermostatAutoSetpoints::LoadDeadband`는 내부 값이 `kMinDeadBand * 10`–`kMaxDeadBand * 10`인지 검사한다. 유효한 `MinSetpointDeadBand` 쓰기는 호환성을 위해 성공 처리하지만 적용하지 않는다.

### 원자적 쓰기

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.h`
- `src/app/clusters/thermostat-server/ThermostatClusterAtomic.cpp`

`AtomicWriteSession`은 `State::Closed` 또는 `State::Open`, 대상 속성 목록, `ScopedNodeId`, 타이머를 관리한다.

| 단계 | 처리 |
|---|---|
| `BuildAttributeStatuses` | 비어 있는 목록, 중복 ID, 디코딩 오류, 알려지지 않은 속성을 거부 |
| `BeginAtomicWrite` | `Timeout` 존재 확인, `Presets`·`Schedules`·`SensorSchedule` 대상 검사, 충돌 속성에 `Status::Busy` |
| 제한 시간 | 요청 시간과 대상별 `GetMaxAtomicWriteTimeout` 합계 중 작은 값 사용 |
| 시작 | `OnAtomicWriteBegin` 호출 후 타이머 시작. 실패하면 rollback 및 reset |
| `CommitAtomicWrite` | 대상 목록 확인 → `OnAtomicWritePrecommit` → 성공 시 `OnAtomicWriteCommit` → reset → 응답 |
| `RollbackAtomicWrite` | 대상 목록 확인 → reset → `OnAtomicWriteRollback` → 응답 |
| `TimerFired` | `Rollback` 수행 |
| `OnFabricRemoved` | 해당 fabric의 세션이면 `Rollback` 수행 |
| `Shutdown` | `ResetAtomicWrite` 후 fabric delegate 제거 |

`Access::SubjectDescriptor`를 받는 `InAtomicWrite`는 `Access::AuthMode::kCase`와 소유 `ScopedNodeId` 일치를 검사한다.

제공된 구현의 확인 범위는 구분해야 한다.

- `InAtomicWrite(CommandHandler *, AtomicAttributes &)`는 열린 상태와 속성 집합 일치를 검사하지만, 함수 본문에서 `commandObj`를 사용하지 않는다.
- `CommitAtomicWrite`는 precommit 실패 시 명시적인 rollback 호출 없이 세션을 reset한다.
- `Shutdown`의 reset도 `Rollback`과 별도 경로다.
- 클러스터의 일반 쓰기 차단 검사보다 `mPresets.WriteAttribute`와 `mSensors.WriteAttribute`가 먼저 실행된다.

### 프리셋

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterPresets.h`
- `src/app/clusters/thermostat-server/ThermostatClusterPresets.cpp`

`ThermostatPresets::Delegate`가 실제 목록, pending 목록, 활성 핸들을 관리한다.

- 원자적 쓰기 소유자가 `Presets`를 읽으면 pending 목록을 반환한다.
- 그 외 읽기는 확정 목록을 반환한다.
- 열린 원자적 쓰기 없이 수정하면 `InvalidInState`.
- 다른 노드가 수정 중이면 `Busy`.
- `ReplaceAll` 또는 목록 전체 쓰기는 pending 목록을 비운 뒤 추가한다.
- `AppendItem`을 지원하며, 그 외 목록 연산은 `CHIP_ERROR_NOT_IMPLEMENTED`.

`AppendPendingPreset`의 주요 검사는 다음과 같다.

- 유효한 `PresetScenario` 및 핸들 크기.
- null 핸들의 새 프리셋은 built-in일 수 없음.
- 비-null 핸들은 기존 확정 목록에 존재해야 함.
- pending 목록의 핸들 중복 금지.
- 기존 항목과 `BuiltIn` 일치.
- 해당 시나리오 지원 및 `SupportsNames` 조건.
- 전체 개수와 시나리오별 개수 제한.

`PrecommitPresets`는 built-in 프리셋 제거를 `Status::ConstraintError`로, 활성 프리셋 제거를 `Status::InvalidInState`로 거부한다.

설정값 제한을 적용하는 코드는 `pendingPreset` 임시 복사본만 수정한다는 TODO가 있다. 따라서 해당 코드만으로 저장된 pending 목록에 보정이 반영된다고 볼 수 없다.

`SetActivePreset`는 존재하지 않는 비-null 핸들에 `Status::InvalidCommand`를 반환한다. 성공하면 `ActivePresetHandle` 변경 알림과 `GenerateActivePresetChangeEvent`를 호출한다.

새 프리셋의 고유 핸들 할당은 `CommitPendingPresets` 구현 책임이다.

### 센서 및 센서 스케줄

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSensors.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSensors.cpp`

`AvailableSensorHandles`와 `EnabledSensorHandles` 쓰기는 전체 교체와 `AppendItem`을 지원한다.

| 대상 | 검사 및 효과 |
|---|---|
| `AvailableSensorHandles` | 최대 `32`개, 핸들 최대 `16`, `Sensors`에 존재, 중복 금지 |
| `EnabledSensorHandles` | 최대 `32`개, 핸들 최대 `16`, `AvailableSensorHandles`에 존재, 중복 금지 |
| 가용 센서 전체 교체 | 제거된 가용 센서를 `EnabledSensorHandles`에서도 제거 |
| 그 외 목록 연산 | `Status::UnsupportedWrite` |

`SensorSchedule`은 원자적 쓰기를 요구한다. 소유자는 pending 목록을 읽으며, 열린 세션이 없으면 `Status::InvalidInState`, 다른 소유자이면 `Status::Busy`를 반환한다.

`AppendPendingSensorScheduleTransition`은 다음을 검사한다.

- `DayOfWeek`에 `Away`가 없어야 한다.
- 요일 비트가 하나 이상 설정되어야 한다.
- `0x7F` 밖의 비트가 없어야 한다.
- `TransitionTime`은 최대 `1439`.
- 센서 핸들은 최대 `32`개이며 각 길이는 최대 `16`.
- 모든 핸들이 가용 센서에 속하고 중복되지 않아야 한다.
- 전환 개수가 `NumberOfSensorScheduleTransitions`를 넘으면 `ResourceExhausted`.

`PrecommitSensorSchedule`은 같은 `TransitionTime`을 가지면서 요일 비트가 겹치는 전환을 `Status::ConstraintError`로 거부한다.

### 제안

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.h`
- `src/app/clusters/thermostat-server/ThermostatClusterSuggestions.cpp`

`AddThermostatSuggestion`의 검증 및 처리 순서는 다음과 같다.

1. `PresetHandle` 크기 검사.
2. `ExpirationInMinutes`가 `30`–`1440`인지 검사.
3. Matter epoch 시간 조회 실패 시 `Status::InvalidInState`.
4. 프리셋이 없으면 `Status::NotFound`.
5. 목록이 최대 개수에 도달했으면 `Status::ResourceExhausted`.
6. 비-null `EffectiveTime`이 현재 시간보다 24시간 넘게 미래이면 `Status::InvalidCommand`.
7. 만료된 제안 제거.
8. `GetUniqueID`로 ID 할당.
9. null `EffectiveTime`은 현재 시간 사용.
10. 만료 시각 계산 후 목록 추가, 속성 알림, 현재 제안 재평가.
11. `AddThermostatSuggestionResponse`에 `UniqueID` 반환.

목록 용량 검사가 만료 항목 제거보다 먼저 수행된다는 점에 유의해야 한다.

`RemoveThermostatSuggestion`은 `UniqueID`를 찾아 제거하고, 만료 항목 정리 및 `ReEvaluateCurrentSuggestion`을 수행한다.

`ReEvaluateCurrentSuggestion`은 전후 null 상태와 `UniqueID`를 비교하여 `CurrentThermostatSuggestion` 변경을 알린다. 활성 프리셋 핸들이 바뀌면 `ActivePresetHandle`도 알린다.

현재 제안의 선택, 미적용 사유 설정, 만료 추적 및 다음 제안 재평가는 `ThermostatSuggestions::Delegate::ReEvaluateCurrentSuggestion`의 책임으로 설명되어 있다.

### 설정값 유지 및 점유

관련 파일:

- `src/app/clusters/thermostat-server/ThermostatClusterHold.h`
- `src/app/clusters/thermostat-server/ThermostatClusterHold.cpp`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.h`
- `src/app/clusters/thermostat-server/ThermostatClusterOccupancy.cpp`

`ThermostatHold`는 `TemperatureSetpointHold`, `TemperatureSetpointHoldDuration`, `SetpointHoldExpiryTimestamp`를 `Delegate`에 연결한다.

- 알 수 없는 `TemperatureSetpointHold` 값은 `Status::InvalidValue`.
- `TemperatureSetpointHoldDuration`은 nullable이며, 명시적인 코드 검사는 `1440` 초과 여부다.
- 스펙·SDK의 최소값 `1`에 대응하는 하한 검사는 제공된 `ThermostatHold::WriteAttribute` 본문에 없다.
- `SetpointHoldExpiryTimestamp`는 스펙·SDK에서 읽기 전용이지만, 제공된 내부 `WriteAttribute`에는 이를 처리하는 분기가 있다.

`ThermostatOccupancy::IsOccupied`는 `OccupancyBitmap::kOccupied`를 검사한다. `SetOccupancy`는 실제 변경 시 속성 알림을 보내지만, 해당 함수 본문에는 `GenerateOccupancyChangeEvent` 호출이 없다.

### 이벤트 생성

출처: `src/app/clusters/thermostat-server/ThermostatClusterEvents.cpp`

다음 함수가 정의되어 있다.

- `GenerateSystemModeChangeEvent`
- `GenerateLocalTemperatureChangeEvent`
- `GenerateOccupancyChangeEvent`
- `GenerateSetpointChangeEvent`
- `GenerateRunningStateChangeEvent`
- `GenerateRunningModeChangeEvent`
- `GenerateActiveScheduleChangeEvent`
- `GenerateActivePresetChangeEvent`

공통 처리:

1. `Feature::kEvents`가 없으면 반환.
2. `mContext`가 있으면 `mContext->interactionContext.eventsGenerator.GenerateEvent` 사용.
3. 그렇지 않으면 `LogEvent` 사용 및 실패 로그 기록.

각 생성 함수 자체의 기능 검사는 `Feature::kEvents`뿐이다. 예를 들어 `GenerateLocalTemperatureChangeEvent` 본문에는 `LTNE` 검사나 유의미한 변화량 판정이 없다.

### 소유 저장소 구조체

관련 파일:

- `src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/PresetStructWithOwnedMembers.cpp`
- `src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/SensorScheduleTransitionStructWithOwnedMembers.cpp`
- `src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/ThermostatSensorStructWithOwnedMembers.cpp`
- `src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.h`
- `src/app/clusters/thermostat-server/ThermostatSuggestionStructWithOwnedMembers.cpp`

이 구조체들은 생성된 구조체 타입을 protected 상속하고, 문자열·핸들 데이터를 내부 버퍼에 복사한다. `Encode`와 `kIsFabricScoped`를 공개한다.

| 구조체 | 저장소 및 동작 |
|---|---|
| `PresetStructWithOwnedMembers` | `kPresetHandleSize = 16`, `kPresetNameSize = 64`. 초과 길이는 `CHIP_ERROR_NO_MEMORY`. `Name`의 미존재·null·값 상태를 구분 |
| `SensorScheduleTransitionStructWithOwnedMembers` | `kMaxEnabledSensorsPerTransition = 32`, `kMaxSensorHandleSize = 16`. 초과 개수는 `CHIP_ERROR_INVALID_LIST_LENGTH`, 초과 길이는 `CHIP_ERROR_INVALID_STRING_LENGTH` |
| `ThermostatSensorStructWithOwnedMembers` | `kThermostatSensorNameMaxSize = 64`, `kThermostatSensorHandleMaxSize = 16`. 초과 길이는 `CHIP_ERROR_INVALID_STRING_LENGTH` |
| `ThermostatSuggestionStructWithOwnedMembers` | `kThermostatSuggestionPresetHandleSize = 16`. 초과 길이는 `CHIP_ERROR_NO_MEMORY`. 시간 getter·setter는 `System::Clock::Seconds32` 사용 |

`SensorScheduleTransitionStructWithOwnedMembers`와 `ThermostatSensorStructWithOwnedMembers`는 동일 타입 복사 생성자가 삭제되어 있으나 복사 대입은 제공한다.

### 이전 속성 접근 API 호환 계층

관련 파일:

- `src/app/clusters/thermostat-server/AttributeAccessorShim.h`
- `src/app/clusters/thermostat-server/AttributeAccessorShim.cpp`

이 계층은 Ember 기반 접근 함수를 직접 호출하던 예제 애플리케이션의 이전 버전 호환용이다. 주석에는 생성된 클러스터 API 또는 `all-devices`로 이전한 뒤 제거할 계획이 명시되어 있다.

| 대상 | 동작 |
|---|---|
| `ControlSequenceOfOperation`, `SystemMode` | `Get`, `Set`을 클러스터 API로 연결 |
| `LocalTemperature` | nullable `Get`; `Set`의 `MarkAttributeDirty::kNo`를 `DataModel::AttributeChangeType::kQuiet`로 변환 |
| `ThermostatRunningMode`, `ThermostatRunningState` | 각각 `SetRunningMode`, `SetRunningState`로 연결 |
| `AbsMinHeatSetpointLimit`, `AbsMaxHeatSetpointLimit` | `GetSetpoints`에서 읽기; `Set`은 `Status::UnsupportedWrite` |
| `OccupiedCoolingSetpoint`, `OccupiedHeatingSetpoint` | `GetSetpoints`에서 읽기; 이 shim의 `Set`은 `Status::UnsupportedWrite` |
| `FeatureMap` | endpoint에 클러스터가 있으면 `Status::Success`; 실제 변경 호출은 주석 처리 |
| `PICoolingDemand`, `PIHeatingDemand` | 각각 파일 내부 변수에 저장. endpoint별 분리 없이 `Get`, `Set` 수행 |

클러스터를 조회하는 shim은 `Thermostat::FindClusterOnEndpoint<FullFeaturedThermostatCluster>`를 사용하며, 찾지 못하면 `Status::UnsupportedEndpoint`를 반환한다.

`PICoolingDemand`와 `PIHeatingDemand`는 주석에서 `ThermostaticRadiatorValveManager`의 이전 사용을 위한 사용 중단 속성으로 설명된다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Water Heater](../device-types/water-heater.md)
