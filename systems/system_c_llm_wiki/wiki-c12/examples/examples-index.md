---
entity: all
ids: []
source_paths: ['examples/all-clusters-app/all-clusters-common/all-clusters-app.matter', 'examples/all-clusters-app/all-clusters-common/all-clusters-app.zap', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h', 'examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp', 'examples/chef/README.md', 'examples/chef/devices/rootnode_dishwasher_cc105034fe.matter', 'examples/chef/devices/rootnode_dishwasher_cc105034fe.zap', 'examples/chef/devices/rootnode_laundrydryer_01796fe396.matter', 'examples/chef/devices/rootnode_laundrydryer_01796fe396.zap', 'examples/chef/devices/rootnode_microwaveoven_37420684d3.matter', 'examples/chef/devices/rootnode_microwaveoven_37420684d3.zap', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap', 'examples/chef/devices/rootnode_roboticvacuumcleaner_1807ff0c49.matter', 'examples/chef/devices/rootnode_roboticvacuumcleaner_1807ff0c49.zap', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap', 'examples/chef/devices/rootnode_waterheater_21bd13d651.matter', 'examples/chef/devices/rootnode_waterheater_21bd13d651.zap', 'examples/laundry-washer-app/nxp/CMakeLists.txt', 'examples/laundry-washer-app/nxp/README.md', 'examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h', 'examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap', 'examples/refrigerator-app/linux/README.md', 'examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.matter', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.zap', 'examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# all

## 개요

제공된 예시는 ZAP 데이터 모델, 자동 생성된 Matter IDL, 애플리케이션 delegate 및 콜백, 빌드·실행 안내로 구성된다.

- `all-clusters-app`: 여러 클러스터의 정의와 엔드포인트별 ZAP 설정.
- `chef`: ZAP 데이터 모델을 선택하여 샘플 애플리케이션을 생성·빌드하는 도구와 가전 기기별 구성.
- `laundry-washer-app`: NXP 세탁기 예제의 데이터 모델, 모드 처리, 속성 변경 전달 및 delegate 등록.
- `refrigerator-app`: Linux 냉장고 예제와 엔드포인트별 온도 단계 목록 제공.

`.matter` 파일에는 ZAP이 자동 생성했으며 열람과 코드 검토 용도라는 주석이 있다. 클러스터의 전체 선언과 개별 엔드포인트의 `server cluster`, `handle command`, `emits event` 구성은 구분해서 읽어야 한다.

## 예시

### 1. ZAP 설정과 IDL의 공통 구성

#### ZAP 메타데이터

제공된 `.zap` 조각의 공통 설정은 다음과 같다.

| 항목 | 값 |
|---|---|
| `fileFormat` | `2` |
| `featureLevel` | `107` |
| `creator` | `"zap"` |
| `commandDiscovery` | `"1"` |
| `defaultResponsePolicy` | `"always"` |
| `manufacturerCodes` | `"0x1002"` |

`all-clusters-app`, `chef`, `refrigerator-app`의 패키지 참조:

| `path` | `type` | `category` | `version` |
|---|---|---|---|
| `../../../src/app/zap-templates/zcl/zcl.json` | `zcl-properties` | `matter` | `1` |
| `../../../src/app/zap-templates/app-templates.json` | `gen-templates-json` | `matter` | `chip-v1` |

NXP 세탁기 ZAP의 패키지 참조:

- `../../../../src/app/zap-templates/zcl/zcl.json`
- `../../../../src/app/zap-templates/app-templates.json`

각 패키지의 `pathRelativity`는 `relativeToZap`이다.

#### 공통 속성

제공된 IDL 클러스터에는 다음 읽기 전용 속성이 반복된다. IDL과 ZAP의 대소문자 표기를 각각 유지한다.

| ID | IDL 이름 | ZAP 이름 | IDL 형식 |
|---|---|---|---|
| `65528` | `generatedCommandList` | `GeneratedCommandList` | `command_id[]` |
| `65529` | `acceptedCommandList` | `AcceptedCommandList` | `command_id[]` |
| `65531` | `attributeList` | `AttributeList` | `attrib_id[]` |
| `65532` | `featureMap` | `FeatureMap` | `bitmap32` |
| `65533` | `clusterRevision` | `ClusterRevision` | `int16u` |

ZAP 속성에는 `storageOption`, `defaultValue`, `reportable`, `minInterval`, `maxInterval`, `reportableChange`가 기록되어 있다. 제공된 설정에는 `RAM`, `NVM`, `External`이 사용된다.

#### 공통 구조체

```text
struct SemanticTagStruct {
  nullable vendor_id mfgCode = 0;
  enum8 namespaceID = 1;
  enum8 tag = 2;
  optional nullable char_string<64> label = 3;
}
```

`Thermostat`의 원자적 쓰기 명령에 사용되는 공통 정의:

```text
enum AtomicRequestTypeEnum : enum8 {
  kBeginWrite = 0;
  kCommitWrite = 1;
  kRollbackWrite = 2;
}
struct AtomicAttributeStatusStruct {
  attrib_id attributeID = 0;
  status statusCode = 1;
}
```

### 2. 제공된 IDL의 클러스터 목록

아래 목록은 제공된 파일 전체에서 확인되는 클러스터 선언이다. 선언이 존재한다는 사실만으로 모든 예제의 엔드포인트에 해당 클러스터가 구성되어 있다고 보지는 않는다.

| 클러스터 | ID | `revision` | 주요 속성·명령·이벤트 |
|---|---|---|---|
| `Identify` | `3` | `6` | `identifyTime`, `identifyType`, `Identify`, `TriggerEffect` |
| `Groups` | `4` | `5` | `nameSupport`, `AddGroup`, `ViewGroup`, `GetGroupMembership`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying` |
| `OnOff` | `6` | `7` | `onOff`, `globalSceneControl`, `onTime`, `offWaitTime`, `startUpOnOff`, `Off`, `On`, `Toggle`, `OffWithEffect`, `OnWithRecallGlobalScene`, `OnWithTimedOff` |
| `Descriptor` | `29` | `3` | `deviceTypeList`, `serverList`, `clientList`, `partsList`, `tagList`, `endpointUniqueID` |
| `Binding` | `30` | `1` | `TargetStruct`, `binding` |
| `FixedLabel` | `64` | `1` | `LabelStruct`, 읽기 전용 `labelList` |
| `UserLabel` | `65` | `1` | `LabelStruct`, `access(write: manage)`가 지정된 `labelList` |
| `LaundryDryerControls` | `74` | `1` | `DrynessLevelEnum`, `supportedDrynessLevels`, `selectedDrynessLevel` |
| `LaundryWasherMode` | `81` | `4` | `supportedModes`, `currentMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `RefrigeratorAndTemperatureControlledCabinetMode` | `82` | `4` | `supportedModes`, `currentMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `LaundryWasherControls` | `83` | `2` | `spinSpeeds`, `spinSpeedCurrent`, `numberOfRinses`, `supportedRinses` |
| `RvcRunMode` | `84` | `5` | `supportedModes`, `currentMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `RvcCleanMode` | `85` | `6` | `supportedModes`, `currentMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `TemperatureControl` | `86` | `1` | `temperatureSetpoint`, `minTemperature`, `maxTemperature`, `step`, `selectedTemperatureLevel`, `supportedTemperatureLevels`, `SetTemperature` |
| `RefrigeratorAlarm` | `87` | `1` | `mask`, `state`, `supported`, `Notify` |
| `DishwasherMode` | `89` | `4` | `supportedModes`, `currentMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `DishwasherAlarm` | `93` | `1` | `mask`, `latch`, `state`, `supported`, `Reset`, `ModifyEnabledAlarms`, `Notify` |
| `MicrowaveOvenMode` | `94` | `3` | `supportedModes`, `currentMode`, `coreModeTags` |
| `MicrowaveOvenControl` | `95` | `1` | `cookTime`, `maxCookTime`, `powerSetting`, `SetCookingParameters`, `AddMoreTime` |
| `OperationalState` | `96` | `3` | `phaseList`, `currentPhase`, `countdownTime`, `operationalStateList`, `operationalState`, `operationalError`, `Pause`, `Stop`, `Start`, `Resume` |
| `RvcOperationalState` | `97` | `3` | `phaseList`, `currentPhase`, `countdownTime`, `operationalStateList`, `operationalState`, `operationalError`, `Pause`, `Resume`, `GoHome` |
| `ScenesManagement` | `98` | `2` | `sceneTableSize`, `fabricSceneInfo`, `AddScene`, `ViewScene`, `RemoveScene`, `RemoveAllScenes`, `StoreScene`, `RecallScene`, `GetSceneMembership`, `CopyScene` |
| `ThermostatMode` | `99` | `1` | `supportedModes`, `currentMode`, `startUpMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `HepaFilterMonitoring` | `113` | `1` | `condition`, `degradationDirection`, `changeIndication`, `inPlaceIndicator`, `lastChangedTime`, `replacementProductList`, `ResetCondition` |
| `ActivatedCarbonFilterMonitoring` | `114` | `1` | `condition`, `degradationDirection`, `changeIndication`, `inPlaceIndicator`, `lastChangedTime`, `replacementProductList`, `ResetCondition` |
| `WaterHeaterManagement` | `148` | `2` | `provisional`; `heaterTypes`, `heatDemand`, `tankVolume`, `estimatedHeatRequired`, `tankPercentage`, `boostState`, `Boost`, `CancelBoost`, `BoostStarted`, `BoostEnded` |
| `WaterHeaterMode` | `158` | `2` | `supportedModes`, `currentMode`, `coreModeTags`, `ChangeToMode`, `ChangeToModeByCoreTag` |
| `Thermostat` | `513` | `12` | 온도 설정점, 운전 모드, 일정, 프리셋, 센서, 제안 및 `AtomicRequest` |
| `FanControl` | `514` | `7` | `fanMode`, `fanModeSequence`, `percentSetting`, `percentCurrent`, `speedMax`, `speedSetting`, `speedCurrent`, `rockSupport`, `rockSetting`, `windSupport`, `windSetting`, `airflowDirection`, `Step` |
| `ThermostatUserInterfaceConfiguration` | `516` | `2` | `temperatureDisplayMode`, `keypadLockout`, `scheduleProgrammingVisibility` |
| `Humidistat` | `517` | `1` | `provisional`; `supportedModes`, `mode`, `systemState`, `userSetpoint`, `SetSettings` |
| `TemperatureMeasurement` | `1026` | `6` | `measuredValue`, `minMeasuredValue`, `maxMeasuredValue`, `tolerance` |
| `RelativeHumidityMeasurement` | `1029` | `3` | `measuredValue`, `minMeasuredValue`, `maxMeasuredValue`, `tolerance` |

#### 모드 클러스터의 공통 데이터

`ModeTagStruct`는 `optional vendor_id mfgCode = 0`과 `enum16 value = 1`을 포함한다. `ModeOptionStruct`는 다음 필드를 포함한다.

```text
char_string<64> label = 0;
int8u mode = 1;
ModeTagStruct modeTags[] = 2;
```

모드 변경 명령이 선언된 클러스터의 요청·응답:

| 항목 | ID | 필드 |
|---|---|---|
| `ChangeToMode` | `0` | `ChangeToModeRequest`: `int8u newMode = 0` |
| `ChangeToModeResponse` | `1` | `enum8 status = 0`, `optional char_string<64> statusText = 1` |
| `ChangeToModeByCoreTag` | `2` | `ChangeToModeByCoreTagRequest`: `enum16 newModeTag = 0` |

`ChangeToModeByCoreTag`는 지정된 태그 값을 태그 목록에 포함하는 모드로 변경한다. `coreModeTags`는 `provisional readonly attribute optional enum16 coreModeTags[] = 4`로 선언되어 있다.

공통 `ModeTag` 값은 `kAuto = 0`, `kQuick = 1`, `kQuiet = 2`, `kLowNoise = 3`, `kLowEnergy = 4`, `kVacation = 5`, `kMin = 6`, `kMax = 7`, `kNight = 8`, `kDay = 9`이다.

| 클러스터 | 추가 `ModeTag` 값 |
|---|---|
| `LaundryWasherMode` | `kNormal = 16384`, `kDelicate = 16385`, `kHeavy = 16386`, `kWhites = 16387` |
| `RefrigeratorAndTemperatureControlledCabinetMode` | `kRapidCool = 16384`, `kRapidFreeze = 16385` |
| `RvcRunMode` | `kIdle = 16384`, `kCleaning = 16385`, `kMapping = 16386` |
| `RvcCleanMode` | `kDeepClean = 16384`, `kVacuum = 16385`, `kMop = 16386`, `kVacuumThenMop = 16387` |
| `DishwasherMode` | `kNormal = 16384`, `kHeavy = 16385`, `kLight = 16386` |
| `MicrowaveOvenMode` | `kNormal = 16384`, `kDefrost = 16385` |
| `ThermostatMode` | `kOff = 16384`, `kCool = 16385`, `kHeat = 16386`, `kEmergencyHeat = 16387` |
| `WaterHeaterMode` | `kOff = 16384`, `kManual = 16385`, `kTimed = 16386` |

이들 `Feature`에는 `kCoreModes = 0x2`가 선언되어 있다. `RvcRunMode`와 `RvcCleanMode`에는 `kDirectModeChange = 0x100000`도 선언되어 있다.

#### 세탁·온도 제어

`LaundryWasherControls`:

| 속성 | ID | 선언 |
|---|---|---|
| `spinSpeeds` | `0` | `readonly attribute optional char_string spinSpeeds[]` |
| `spinSpeedCurrent` | `1` | `attribute optional nullable int8u spinSpeedCurrent` |
| `numberOfRinses` | `2` | `attribute optional NumberOfRinsesEnum numberOfRinses` |
| `supportedRinses` | `3` | `readonly attribute optional NumberOfRinsesEnum supportedRinses[]` |

- `Feature`: `kSpin = 0x1`, `kRinse = 0x2`.
- `NumberOfRinsesEnum`: `kNone = 0`, `kNormal = 1`, `kExtra = 2`, `kMax = 3`.
- `LaundryDryerControls`의 `DrynessLevelEnum`: `kLow = 0`, `kNormal = 1`, `kExtra = 2`, `kMax = 3`.
- `selectedDrynessLevel`은 `nullable`이며 `supportedDrynessLevels`는 읽기 전용 목록이다.

`TemperatureControl`:

```text
bitmap Feature : bitmap32 {
  kTemperatureNumber = 0x1;
  kTemperatureLevel = 0x2;
  kTemperatureStep = 0x4;
}

request struct SetTemperatureRequest {
  optional temperature targetTemperature = 0;
  optional int8u targetTemperatureLevel = 1;
}

command SetTemperature(SetTemperatureRequest): DefaultSuccess = 0;
```

#### 운전 상태와 알람

`OperationalState`와 `RvcOperationalState`는 다음 구조체와 이벤트를 공유하는 형태로 선언된다.

- `ErrorStateStruct`
  - `enum8 errorStateID = 0`
  - `optional char_string<64> errorStateLabel = 1`
  - `optional char_string<64> errorStateDetails = 2`
- `OperationalStateStruct`
  - `enum8 operationalStateID = 0`
  - `optional char_string<64> operationalStateLabel = 1`
- `critical event OperationalError = 0`
  - `ErrorStateStruct errorState = 0`
- `info event OperationCompletion = 1`
  - `enum8 completionErrorCode = 0`
  - `optional nullable elapsed_s totalOperationalTime = 1`
  - `optional nullable elapsed_s pausedTime = 2`
- `OperationalCommandResponse = 4`
  - `ErrorStateStruct commandResponseState = 0`

| 클러스터 | 명령과 ID |
|---|---|
| `OperationalState` | `Pause = 0`, `Stop = 1`, `Start = 2`, `Resume = 3` |
| `RvcOperationalState` | `Pause = 0`, `Resume = 3`, `GoHome = 128` |

`GoHome`은 현재 상태에서 가능하면 충전 도크 탐색을 시작한다. `OperationalState`의 각 원격 제어 명령에는 해당 원격 동작을 지원하는 기기라면 명령을 지원해야 한다는 주석이 있다.

`RefrigeratorAlarm`과 `DishwasherAlarm`의 `Notify = 0`은 `AlarmBitmap` 형식의 `active = 0`, `inactive = 1`, `state = 2`, `mask = 3`을 포함하는 `info` 이벤트이다.

| 클러스터 | `AlarmBitmap` |
|---|---|
| `RefrigeratorAlarm` | `kDoorOpen = 0x1` |
| `DishwasherAlarm` | `kInflowError = 0x1`, `kDrainError = 0x2`, `kDoorError = 0x4`, `kTempTooLow = 0x8`, `kTempTooHigh = 0x10`, `kWaterLevelError = 0x20` |

`DishwasherAlarm`은 `kReset = 0x1`을 선언한다. `Reset(ResetRequest)`은 `alarms`를 받아 가능한 활성·래치 알람을 초기화하며, `ModifyEnabledAlarms(ModifyEnabledAlarmsRequest)`는 `mask`를 받아 알람 활성화 또는 억제를 요청한다.

#### `Thermostat`

`Thermostat`의 `Feature`:

```text
kHeating = 0x1;
kCooling = 0x2;
kOccupancy = 0x4;
kScheduleConfiguration = 0x8;
kSetback = 0x10;
kAutoMode = 0x20;
kLocalTemperatureNotExposed = 0x40;
kMatterScheduleConfiguration = 0x80;
kPresets = 0x100;
kEvents = 0x200;
kThermostatSuggestions = 0x400;
kThermostatSensors = 0x800;
```

| 명령 | ID | 요청 | 응답 |
|---|---|---|---|
| `SetpointRaiseLower` | `0` | `SetpointRaiseLowerRequest` | `DefaultSuccess` |
| `SetWeeklySchedule` | `1` | `SetWeeklyScheduleRequest` | `DefaultSuccess` |
| `GetWeeklySchedule` | `2` | `GetWeeklyScheduleRequest` | `GetWeeklyScheduleResponse` |
| `ClearWeeklySchedule` | `3` | 없음 | `DefaultSuccess` |
| `SetActiveScheduleRequest` | `5` | `SetActiveScheduleRequestRequest` | `DefaultSuccess` |
| `SetActivePresetRequest` | `6` | `SetActivePresetRequestRequest` | `DefaultSuccess` |
| `AddThermostatSuggestion` | `7` | `AddThermostatSuggestionRequest` | `AddThermostatSuggestionResponse` |
| `RemoveThermostatSuggestion` | `8` | `RemoveThermostatSuggestionRequest` | `DefaultSuccess` |
| `AtomicRequest` | `254` | `AtomicRequestRequest` | `AtomicResponse` |

`SetWeeklySchedule`, `ClearWeeklySchedule`, `AddThermostatSuggestion`, `RemoveThermostatSuggestion`에는 `access(invoke: manage)`가 지정되어 있다.

- 일정: `ScheduleTransitionStruct`, `ScheduleStruct`, `ScheduleTypeStruct`, `WeeklyScheduleTransitionStruct`.
- 프리셋: `PresetStruct`, `PresetTypeStruct`.
- 센서: `ThermostatSensorStruct`, `SensorScheduleTransitionStruct`.
- 제안: `ThermostatSuggestionStruct`, `ThermostatSuggestionNotFollowingReasonBitmap`.

`AtomicRequestRequest`는 `requestType`, `attributeRequests[]`, 선택적 `timeout`을 포함한다. `AtomicResponse = 253`은 `statusCode`, `attributeStatus[]`, 선택적 `timeout`을 반환한다.

다음 이벤트는 모두 `provisional info event`로 선언된다.

| 이벤트 | ID |
|---|---|
| `SystemModeChange` | `0` |
| `LocalTemperatureChange` | `1` |
| `OccupancyChange` | `2` |
| `SetpointChange` | `3` |
| `RunningStateChange` | `4` |
| `RunningModeChange` | `5` |
| `ActiveScheduleChange` | `6` |
| `ActivePresetChange` | `7` |

`criticalFreezeProtection`, `criticalOverheatProtection`, `sensors`, `availableSensorHandles`, `enabledSensorHandles`, `numberOfSensorScheduleTransitions`, `sensorSchedule` 속성도 `provisional`로 표시되어 있다.

### 3. `all-clusters-app`

출처:

- `examples/all-clusters-app/all-clusters-common/all-clusters-app.matter`
- `examples/all-clusters-app/all-clusters-common/all-clusters-app.zap`

제공된 IDL에는 동일한 `OnOff = 6` 선언이 두 번 등장한다. 끝부분의 `endpoint 0`에는 다음 기기 유형이 선언된다.

```text
device type ma_rootdevice = 22, version 5;
device type ma_powersource = 17, version 1;
```

#### ZAP 엔드포인트

모든 제공된 엔드포인트 항목은 `profileId = 259`, `networkId = 0`, `parentEndpointIdentifier = null`이다.

| `endpointId` | `endpointTypeIndex` | `endpointTypeName` | 제공된 클러스터 구성 |
|---|---|---|---|
| `0` | `0` | `MA-rootdevice` | `Groups`, `Descriptor`, `Binding`, `Fixed Label`, `User Label`, `Relative Humidity Measurement` |
| `1` | `1` | `MA-onofflight` | 조명, 가전 모드·제어, 알람, 운전 상태, 필터, 온도·습도 관련 서버와 `On/Off` 클라이언트 |
| `2` | `2` | `MA-onofflight` | `Identify`, `Groups`, `On/Off`, `Descriptor`, `Scenes Management` 서버 |
| `3` | `3` | `MA-genericswitch` | `Identify`, `Descriptor` 서버; `Identify`, `TriggerEffect` 명령 |
| `4` | `4` | `MA-genericswitch` | `Identify`, `Descriptor` 서버; 제공된 `Identify` 항목에는 명령 목록이 없음 |
| `65534` | `5` | `Anonymous Endpoint Type` | `Descriptor` 서버 |

엔드포인트 `1`의 `On/Off` 클라이언트에는 `Off`, `On`, `Toggle`이 활성화되어 있다. 서버에는 여기에 `OffWithEffect`, `OnWithRecallGlobalScene`, `OnWithTimedOff`가 추가된다.

#### 주요 기본값과 저장 설정

| 대상 | ZAP 설정 |
|---|---|
| 엔드포인트 `1`의 `OnOff` | `NVM`, `"0x00"` |
| 엔드포인트 `1`의 `StartUpOnOff` | `NVM`, `"0xFF"` |
| 엔드포인트 `2`의 `OnOff` | `RAM`, `"0x00"` |
| 엔드포인트 `2`의 `StartUpOnOff` | `RAM`, `""` |
| `On/Off`의 `FeatureMap` | `"0x0001"` |
| `Groups`의 `FeatureMap` | `"0"` |
| `Laundry Washer Controls`의 `FeatureMap` | `"3"` |
| `Temperature Control`의 `FeatureMap` | `"2"` |
| `Temperature Control`의 `SelectedTemperatureLevel` | `RAM`, `"0"` |
| `Refrigerator Alarm` | `Mask = "1"`, `State = "0"`, `Supported = "1"` |
| `Dishwasher Alarm` | `Mask = "1"`, `Latch = "3"`, `State = "0"`, `Supported = "47"` |
| `Scenes Management` | `SceneTableSize = "16"`, `FeatureMap = "1"` |
| `Thermostat`의 `FeatureMap` | `"0x0F23"` |
| `Thermostat Mode`의 `FeatureMap` | `External`, `"2"` |
| `Fan Control` | `SpeedMax = "100"`, `FeatureMap = "0x3F"` |
| `Humidistat` | `UserSetpoint = "40"`, `MinSetpoint = "30"`, `MaxSetpoint = "60"`, `Step = "5"`, `FeatureMap = "1023"` |
| `Temperature Measurement` | `MinMeasuredValue = "0x8000"`, `MaxMeasuredValue = "0x8000"` |
| `Relative Humidity Measurement` | `MinMeasuredValue = "0"`, `MaxMeasuredValue = "0x2710"` |

`Thermostat Mode`에는 `ChangeToModeByCoreTag`와 `CoreModeTags`가 포함된다. 반면 제공된 다른 모드 클러스터의 ZAP 명령 목록은 주로 `ChangeToMode`와 `ChangeToModeResponse`로 구성된다.

`Thermostat`의 ZAP 이벤트 목록에는 `SystemModeChange`, `LocalTemperatureChange`, `SetpointChange`, `RunningStateChange`, `RunningModeChange`, `ActivePresetChange`가 포함된다.

### 4. 세탁기 공통 delegate

#### `LaundryWasherControlDelegate`

출처:

- `examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h`
- `examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp`

참조 헤더:

- `app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h`
- `app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h`
- `app/util/config.h`

`LaundryWasherControlDelegate`는 `Delegate`를 상속하며, 정적 `instance`를 `getLaundryWasherControlDelegate()`로 반환한다.

| 정적 배열 | 값 |
|---|---|
| `spinSpeedsNameOptions` | `"Off"_span`, `"Low"_span`, `"Medium"_span`, `"High"_span` |
| `supportRinsesOptions` | `NumberOfRinsesEnum::kNormal`, `NumberOfRinsesEnum::kExtra` |

| 함수 | 동작 |
|---|---|
| `GetSpinSpeedAtIndex(size_t index, MutableCharSpan & spinSpeed)` | 범위를 확인한 뒤 `chip::CopyCharSpanToMutableCharSpan`으로 문자열을 복사하고 결과를 반환 |
| `GetSupportedRinseAtIndex(size_t index, NumberOfRinsesEnum & supportedRinse)` | 범위를 확인한 뒤 열거형 값을 대입하고 `CHIP_NO_ERROR` 반환 |

두 함수 모두 `index >= MATTER_ARRAY_SIZE(...)`이면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.

#### `LaundryWasherModeDelegate`

출처: `examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h`

`app/clusters/mode-base-server/mode-base-server.h`를 포함하며 `ModeBase::Delegate`를 상속한다.

| 상수 | 값 | `label` | 태그 |
|---|---|---|---|
| `ModeNormal` | `0` | `"Normal"_span` | `ModeTag::kNormal` |
| `ModeDelicate` | `1` | `"Delicate"_span` | `ModeTag::kDelicate`, `ModeBase::ModeTag::kNight`, `ModeBase::ModeTag::kQuiet` |
| `ModeHeavy` | `2` | `"Heavy"_span` | `ModeBase::ModeTag::kMax`, `ModeTag::kHeavy` |
| `ModeWhites` | `3` | `"Whites"_span` | `ModeTag::kWhites` |

태그 배열은 `modeTagsNormal`, `modeTagsDelicate`, `modeTagsHeavy`, `modeTagsWhites`이며, 각 항목의 `mfgCode`는 `{}`이다. `kModeOptions[4]`는 `detail::Structs::ModeOptionStruct::Type`과 `DataModel::List<const ModeTagStructType>`을 사용한다.

선언된 override:

```cpp
CHIP_ERROR Init() override;
void HandleChangeToMode(uint8_t mode, ModeBase::Commands::ChangeToModeResponse::Type & response) override;
CHIP_ERROR GetModeLabelByIndex(uint8_t modeIndex, MutableCharSpan & label) override;
CHIP_ERROR GetModeValueByIndex(uint8_t modeIndex, uint8_t & value) override;
CHIP_ERROR GetModeTagsByIndex(uint8_t modeIndex, DataModel::List<ModeTagStructType> & tags) override;
```

네임스페이스 함수 `ModeBase::Instance * Instance()`와 `void Shutdown()`도 선언된다.

### 5. NXP `laundry-washer-app`

#### 파일 구성과 빌드 연결

출처:

- `examples/laundry-washer-app/nxp/CMakeLists.txt`
- `examples/laundry-washer-app/nxp/README.md`
- `examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp`
- `examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp`
- `examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h`
- `examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp`
- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter`
- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap`

제공된 `CMakeLists.txt` 조각은 `target_include_directories(app`에 다음 경로를 추가한다.

- `${ALL_CLUSTERS_COMMON_DIR}/include`
- `${NXP_EXAMPLE_DIR}/main/include`

`target_sources(app`에는 다음 파일이 포함된다.

- `${NXP_EXAMPLE_DIR}/main/DeviceCallbacks.cpp`
- `${NXP_EXAMPLE_DIR}/main/ZclCallbacks.cpp`
- `${NXP_EXAMPLE_DIR}/main/laundry-washer-mode.cpp`
- `${ALL_CLUSTERS_COMMON_DIR}/src/laundry-washer-controls-delegate-impl.cpp`

#### 엔드포인트 데이터 모델

| 엔드포인트 | 기기 유형 |
|---|---|
| `0` | `ma_rootdevice = 22, version 5`; `ma_otarequestor = 18, version 1` |
| `1` | `ma_laundry_washer = 115, version 1` |

엔드포인트 `1`의 서버 클러스터:

- `Identify`
- `OnOff`
- `Descriptor`
- `Binding`
- `UserLabel`
- `LaundryWasherMode`
- `LaundryWasherControls`
- `TemperatureControl`
- `OperationalState`

주요 구성:

| 클러스터 | 구성 |
|---|---|
| `OnOff` | `onOff`는 `persist`, 기본값 `0`; `startUpOnOff`는 `persist`, 기본값 `0xFF`; `featureMap = 2` |
| `LaundryWasherMode` | `supportedModes`, `currentMode`는 `callback`; `clusterRevision = 0x0004`; `ChangeToMode` 처리 |
| `LaundryWasherControls` | 네 개의 전용 속성이 IDL에서 `callback`; `featureMap = 3` |
| `TemperatureControl` | `selectedTemperatureLevel`은 `ram`; `supportedTemperatureLevels`는 `callback`; `featureMap = 2`; `SetTemperature` 처리 |
| `OperationalState` | `Pause`, `Stop`, `Start`, `Resume` 처리; `OperationalError`, `OperationCompletion` 발생 |

IDL에 `Groups` 선언은 있지만 제공된 엔드포인트 `1`의 서버 구성에는 없다.

#### 속성 변경 전달

`MatterPostAttributeChangeCallback()`은 다음 순서로 변경 정보를 전달한다.

1. `chip::DeviceManager::CHIPDeviceManager::GetInstance().GetCHIPDeviceManagerCallbacks()` 호출.
2. 반환된 `cb`가 `nullptr`이 아니면 `cb->PostAttributeChangeCallback()` 호출.
3. `path.mEndpointId`, `path.mClusterId`, `path.mAttributeId`, `type`, `size`, `value` 전달.

`LaundryWasherApp::DeviceCallbacks::PostAttributeChangeCallback()`은 변경 정보를 기록하고, `Clusters::OnOff::Id`에 대해 `OnOnOffPostAttributeChangeCallback()`을 호출한다.

`OnOnOffPostAttributeChangeCallback()`의 처리 조건:

- `attributeId`가 `Clusters::OnOff::Attributes::OnOff::Id`.
- `value != nullptr`.
- `*value == true`.
- `LaundryWasherMode::Instance()`가 `nullptr`이 아님.
- `GetOnMode()` 결과가 null이 아님.

조건을 만족하면 `UpdateCurrentMode(mode.Value())`를 호출한다.

`DeviceCallbacks.h`에는 `OnIdentifyPostAttributeChangeCallback()` 선언도 있지만, 제공된 구현 조각에는 해당 함수의 본문이 없다.

`LaundryWasherApp::DeviceCallbacks::GetDefaultInstance()`는 정적 `sDeviceCallbacks`를 반환한다. 구현의 `chip::NXP::App::GetDeviceCallbacks()`는 이 인스턴스를 반환하며, 헤더 끝에는 별도의 `GetDeviceCallbacks()` 선언이 있다.

#### `LaundryWasherControls` delegate 등록

```cpp
void emberAfLaundryWasherControlsClusterInitCallback(EndpointId endpoint)
{
    LaundryWasherControlsServer::SetDefaultDelegate(endpoint, &LaundryWasherControlDelegate::getLaundryWasherControlDelegate());
}
```

#### 모드 처리와 수명 관리

`examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp`의 동작:

| 함수 | 동작 |
|---|---|
| `LaundryWasherModeDelegate::Init()` | `CHIP_NO_ERROR` 반환 |
| `LaundryWasherModeDelegate::HandleChangeToMode()` | `response.status = to_underlying(ModeBase::StatusCode::kSuccess)` 지정 |
| `GetModeLabelByIndex()` | 범위 확인 후 모드 라벨 복사 |
| `GetModeValueByIndex()` | 범위 확인 후 모드 값 대입 |
| `GetModeTagsByIndex()` | 범위와 출력 목록 크기를 확인하고 `std::copy` 및 `tags.reduce_size()` 수행 |
| `LaundryWasherMode::Instance()` | `gLaundryWasherModeInstance` 반환 |
| `LaundryWasherMode::Shutdown()` | 인스턴스와 delegate를 삭제하고 포인터를 `nullptr`로 지정 |

`GetModeTagsByIndex()`는 출력 목록의 크기가 부족하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. 세 인덱스 조회 함수는 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.

초기화 핵심 코드:

```cpp
void MatterLaundryWasherModeClusterInitCallback(chip::EndpointId endpointId)
{
    VerifyOrDie(endpointId == 1); // this cluster is only enabled for endpoint 1.
    VerifyOrDie(gLaundryWasherModeDelegate == nullptr && gLaundryWasherModeInstance == nullptr);
    gLaundryWasherModeDelegate = new LaundryWasherMode::LaundryWasherModeDelegate;
    gLaundryWasherModeInstance = new ModeBase::Instance(gLaundryWasherModeDelegate, 0x1, LaundryWasherMode::Id, 0);
    TEMPORARY_RETURN_IGNORED gLaundryWasherModeInstance->Init();
}
```

`MatterLaundryWasherModeClusterShutdownCallback()`도 엔드포인트 `1`을 검사한다. 인스턴스가 있으면 먼저 `gLaundryWasherModeInstance->Shutdown()`을 호출하고, 이후 `LaundryWasherMode::Shutdown()`을 호출한다.

제공된 `HandleChangeToMode()` 본문은 성공 상태만 지정한다. 실제 세탁 동작을 실행하는 코드는 이 본문에 없다.

#### 지원 플랫폼

| 플랫폼 | README에서 참조하는 경로 |
|---|---|
| RW61x, Zephyr OS | `../../../docs/platforms/nxp/nxp_zephyr_guide.md` |
| RW61x, FreeRTOS OS | `../../../docs/platforms/nxp/nxp_rw61x_guide.md` |
| RT1170 | `../../../docs/platforms/nxp/nxp_rt1170_guide.md` |
| RT1060 | `../../../docs/platforms/nxp/nxp_rt1060_guide.md` |

환경 구성·빌드·테스트 안내는 `../../../docs/platforms/nxp/nxp_examples_freertos_platforms.md`와 `../../../docs/platforms/nxp/nxp_zephyr_guide.md`를 참조한다.

이 애플리케이션은 Matter-over-WiFi + Thread Border Router 구성을 지원하지 않는다고 명시되어 있다.

### 6. Chef 기기별 데이터 모델

각 예제의 `endpoint 0`에는 `ma_rootdevice = 22, version 5`가 선언된다.

#### 식기세척기

출처:

- `examples/chef/devices/rootnode_dishwasher_cc105034fe.matter`
- `examples/chef/devices/rootnode_dishwasher_cc105034fe.zap`

엔드포인트 `1`은 `ma_dishwasher = 117, version 2`이다. ZAP의 `deviceTypeName`과 `endpointTypeName`은 `MA-dishwasher`이다.

| 서버 클러스터 | 주요 구성 |
|---|---|
| `Identify` | `Identify`, `TriggerEffect` 처리 |
| `OnOff` | `onOff = 0`, `featureMap = 2`; `Off`, `On`, `Toggle` 처리 |
| `Descriptor` | 기본 목록 및 공통 속성은 `callback` |
| `TemperatureControl` | `temperatureSetpoint = 5000`, `minTemperature = 4900`, `maxTemperature = 8200`, `step = 100`, `featureMap = 5` |
| `DishwasherMode` | `ChangeToMode` 처리; `clusterRevision = 0x0004` |
| `DishwasherAlarm` | `mask = 0`, `latch = 3`, `state = 0`, `supported = 0x3F`, `featureMap = 1`; `Reset`, `ModifyEnabledAlarms`, `Notify` |
| `OperationalState` | `Pause`, `Stop`, `Start`, `Resume`; `OperationalError`, `OperationCompletion` |

ZAP에서 `DishwasherAlarm`의 `Mask`, `Latch`, `State`, `Supported`, `FeatureMap`은 `RAM`이다. IDL의 대응 엔드포인트 속성은 `callback`으로 표시되어 있다.

#### 세탁 건조기

출처:

- `examples/chef/devices/rootnode_laundrydryer_01796fe396.matter`
- `examples/chef/devices/rootnode_laundrydryer_01796fe396.zap`

엔드포인트 `1`은 `ma_laundry_dryer = 124, version 1`이다.

서버 클러스터:

- `Identify`
- `OnOff`
- `Descriptor`
- `LaundryDryerControls`
- `LaundryWasherMode`
- `TemperatureControl`
- `OperationalState`

`OnOff`은 `featureMap = 2`이고 `Off`, `On`, `Toggle`을 처리한다. `LaundryWasherMode`는 `ChangeToMode`를 처리한다. `TemperatureControl`은 온도 단계 방식으로 구성되며 `featureMap = 2`이다.

ZAP의 `deviceTypeName`은 `MA-laundry-dryer`이지만 엔드포인트 유형의 `name`과 `endpointTypeName`은 `MA-dishwasher`로 기록되어 있다.

#### 전자레인지

출처:

- `examples/chef/devices/rootnode_microwaveoven_37420684d3.matter`
- `examples/chef/devices/rootnode_microwaveoven_37420684d3.zap`

엔드포인트 `1`은 `ma_microwave_oven = 121, version 2`이며, ZAP의 `parentEndpointIdentifier`는 `0`이다.

서버 클러스터는 `Identify`, `Descriptor`, `MicrowaveOvenMode`, `MicrowaveOvenControl`, `OperationalState`, `FanControl`이다. `FixedLabel` 선언은 존재하지만 엔드포인트 `1`의 서버 구성에는 없다.

`MicrowaveOvenControl`:

| 명령 | ID | 요청 필드 |
|---|---|---|
| `SetCookingParameters` | `0` | 선택적 `cookMode`, `cookTime`, `powerSetting`, `wattSettingIndex`, `startAfterSetting` |
| `AddMoreTime` | `1` | `elapsed_s timeToAdd = 0` |

- `Feature`: `kPowerAsNumber = 0x1`, `kPowerInWatts = 0x2`, `kPowerNumberLimits = 0x4`.
- 엔드포인트에는 `cookTime`, `maxCookTime`, `powerSetting`, `minPower`, `maxPower`, `powerStep`, `wattRating`이 구성되어 있다.
- `supportedWatts`, `selectedWattIndex`는 IDL에 `provisional` 속성으로 선언되지만 해당 엔드포인트 구성에는 없다.
- `Identify`는 `Identify` 명령만 처리한다.
- `FanControl`은 `fanModeSequence = 2`, `speedMax = 10`, `rockSupport = 0x03`, `windSupport = 0x03`, `featureMap = 63`이며 `Step`을 처리한다.

#### 냉장고와 두 온도 제어 캐비닛

출처:

- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter`
- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap`

| 엔드포인트 | 기기 유형 | 서버 클러스터 | ZAP `parentEndpointIdentifier` |
|---|---|---|---|
| `1` | `ma_refrigerator = 112, version 1` | `Descriptor`, `RefrigeratorAndTemperatureControlledCabinetMode`, `RefrigeratorAlarm` | `null` |
| `2` | `ma_temperature_controlled_cabinet = 113, version 1` | `Descriptor`, `TemperatureControl`, `TemperatureMeasurement` | `1` |
| `3` | `ma_temperature_controlled_cabinet = 113, version 1` | `Descriptor`, `TemperatureControl`, `TemperatureMeasurement` | `1` |

`TemperatureControl`의 기본값:

| 속성 | 엔드포인트 `2` | 엔드포인트 `3` |
|---|---|---|
| `temperatureSetpoint` | `200` | `-1800` |
| `minTemperature` | `200` | `-1800` |
| `maxTemperature` | `400` | `-1500` |
| `step` | `10` | `10` |
| `featureMap` | `5` | `5` |

두 캐비닛 모두 `SetTemperature`를 처리하며 `Descriptor.tagList`를 포함한다. `TemperatureMeasurement`는 `minMeasuredValue = -4000`, `maxMeasuredValue = 2000`으로 구성된다.

엔드포인트 `1`:

- `RefrigeratorAndTemperatureControlledCabinetMode`: `ChangeToMode` 처리.
- `RefrigeratorAlarm`: `Notify` 발생, `mask = 0x1`, `state = 0`, `supported = 0x1`, `featureMap = 0`.

#### 로봇 청소기

출처:

- `examples/chef/devices/rootnode_roboticvacuumcleaner_1807ff0c49.matter`
- `examples/chef/devices/rootnode_roboticvacuumcleaner_1807ff0c49.zap`

IDL의 엔드포인트 `1`은 `ma_robotic_vacuum_cleaner = 116, version 1`이다. ZAP의 `deviceTypes`에는 `MA-powersource` 코드 `17`과 `MA-robotic-vacuum-cleaner` 코드 `116`이 함께 있으며, 두 버전 모두 `1`이다.

| 서버 클러스터 | 명령·이벤트 |
|---|---|
| `Identify` | `Identify`, `TriggerEffect` |
| `Descriptor` | 기본 목록 및 공통 속성 |
| `RvcRunMode` | `ChangeToMode`; `clusterRevision = 0x0005` |
| `RvcCleanMode` | `ChangeToMode`; `clusterRevision = 0x0006` |
| `RvcOperationalState` | `Pause`, `Resume`, `GoHome`; `OperationalError`, `OperationCompletion` |

`Groups` 선언은 있지만 제공된 엔드포인트 `1` 서버 구성에는 없다.

#### 실내 에어컨

출처:

- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter`
- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap`

엔드포인트 `1`은 `ma_room_airconditioner = 114, version 5`이다.

서버 클러스터는 `Identify`, `Groups`, `OnOff`, `Descriptor`, `Thermostat`, `FanControl`, `ThermostatUserInterfaceConfiguration`이다.

`Thermostat`의 엔드포인트 기본값:

| 속성 | 기본값 | IDL 저장 표시 |
|---|---|---|
| `localTemperature` | `2800` | `ram` |
| `absMinHeatSetpointLimit` | `0` | `ram` |
| `absMaxHeatSetpointLimit` | `3500` | `ram` |
| `absMinCoolSetpointLimit` | `1000` | `ram` |
| `absMaxCoolSetpointLimit` | `4000` | `ram` |
| `occupiedCoolingSetpoint` | `2300` | `persist` |
| `occupiedHeatingSetpoint` | `2000` | `persist` |
| `minHeatSetpointLimit` | `500` | `persist` |
| `maxHeatSetpointLimit` | `3000` | `persist` |
| `minCoolSetpointLimit` | `1500` | `persist` |
| `maxCoolSetpointLimit` | `3500` | `persist` |
| `controlSequenceOfOperation` | `0x04` | `persist` |
| `systemMode` | `0x01` | `persist` |
| `ACLouverPosition` | `1` | `persist` |
| `featureMap` | `3` | `ram` |

이 엔드포인트의 `Thermostat` 처리 명령은 `SetpointRaiseLower`이다.

추가 구성:

- `OnOff`: `onOff`은 `persist`, 기본값 `0`; `featureMap = 2`.
- `FanControl`: `fanModeSequence = 2`, `speedMax = 100`, `rockSupport = 0x01`, `featureMap = 53`; `Step` 처리.
- `ThermostatUserInterfaceConfiguration`: `temperatureDisplayMode = 0x00`, `keypadLockout = 0x00`.
- `TemperatureMeasurement`, `RelativeHumidityMeasurement`는 선언되어 있지만 이 엔드포인트의 서버 구성에는 없다.

#### 온수기

출처:

- `examples/chef/devices/rootnode_waterheater_21bd13d651.matter`
- `examples/chef/devices/rootnode_waterheater_21bd13d651.zap`

엔드포인트 `1`은 `ma_waterheater = 1295, version 2`이며 ZAP의 `parentEndpointIdentifier`는 `0`이다.

서버 클러스터:

- `Identify`: `Identify` 처리.
- `Descriptor`.
- `WaterHeaterManagement`: `Boost`, `CancelBoost` 처리; `BoostStarted`, `BoostEnded` 발생.
- `WaterHeaterMode`: `ChangeToMode` 처리.
- `Thermostat`: `SetpointRaiseLower` 처리.

`WaterHeaterBoostInfoStruct`:

```text
elapsed_s duration = 0;
optional boolean oneShot = 1;
optional boolean emergencyBoost = 2;
optional temperature temporarySetpoint = 3;
optional percent targetPercentage = 4;
optional percent targetReheat = 5;
```

`BoostRequest`와 `BoostStarted`는 `boostInfo`를 포함한다. `BoostEnded`에는 필드가 없다. `Boost`, `CancelBoost`에는 `access(invoke: manage)`가 지정된다.

`WaterHeaterManagement`의 `Feature`는 `kEnergyManagement = 0x1`, `kTankPercent = 0x2`이며 ZAP의 `FeatureMap` 기본값은 `"3"`이다.

`Thermostat` 기본값:

| 속성 | 값 |
|---|---|
| `localTemperature` | `2000` |
| `absMinHeatSetpointLimit` | `700` |
| `absMaxHeatSetpointLimit` | `8000` |
| `occupiedHeatingSetpoint` | `5500` |
| `minHeatSetpointLimit` | `700` |
| `maxHeatSetpointLimit` | `8000` |
| `controlSequenceOfOperation` | `2` |
| `systemMode` | `4` |
| `thermostatRunningState` | `0` |
| `featureMap` | `1` |

### 7. Chef 생성·빌드·배포

출처: `examples/chef/README.md`

Chef는 Matter 기기 유형의 적용 범위를 넓히고 데이터 모델을 쉽게 구성할 수 있는 샘플을 제공한다. shell app을 시작점으로 사용하며, `chef.py`가 빌드 중 ZAP 파일을 처리한다.

- 기기 데이터 모델: `devices`.
- 자동 생성 ZAP 산출물의 임시 위치: `out`.
- CI/CD에서 사용하는 산출물: `zzz_generated`.
- 플랫폼 공통 코드: `common`.
- 플랫폼별 빌드 시스템과 `main.cpp`: `<platform>`.
- 도구 체인·직렬 포트 설정: `config.yaml`.
- 새 기기 이름 생성 안내와 스크립트: `sample_app_util`.

#### 첫 샘플 빌드

1. 대상 플랫폼 도구 체인을 설치한다.
2. `chef.py`를 처음 실행하여 `config.yaml`을 생성한다.
3. SDK 경로와 `TTY`를 설정한다. `IDF_PATH`, `ZEPHYR_BASE`가 있으면 기본값으로 사용한다.
4. `chef.py -u`로 ZAP과 선택된 플랫폼의 도구 체인을 갱신한다.
5. 다음 명령으로 `devices/lighting.zap`을 열고 생성·빌드·플래시를 수행한다.
6. `chef.py -h`로 사용 가능한 명령을 확인한다.

```shell
chef.py -gzbf -t <platform> -d lighting
```

README의 `TTY` 예:

| 플랫폼·환경 | 경로 |
|---|---|
| ESP32 macOS | `/dev/tty.usbmodemXXXXXXX` |
| ESP32 Linux | `/dev/ttyACM0` |
| NRFCONNECT macOS | `/dev/tty.usbserial-XXXXX` |
| NRFCONNECT Linux | `/dev/ttyUSB0` |

#### Linux 런타임 옵션

다음은 Chef 빌드 옵션이 아니라 생성된 Linux 애플리케이션의 런타임 옵션이다.

| 옵션 | 설명 |
|---|---|
| `--discriminator <discriminator>` | 커미셔닝 중 광고하는 12-bit unsigned integer |
| `--passcode <passcode>` | 커미셔닝 중 소유 증명에 사용하는 27-bit unsigned integer |
| `--spake2p-verifier-base64` | verifier 계산에 `--passcode`를 제공하지 않을 때 필요한 옵션 |
| `--secured-device-port <port>` | 보안 메시지 수신 포트; 기본값 `5540` |
| `--KVS <filepath>` | Key Value Store 저장 파일 |
| `-h`, `--help` | 도움말 출력 후 종료 |

#### CI/CD

- CI 작업: `.github/workflows/chef.yaml`.
- CI 실행 옵션: `--ci -t $PLATFORM`.
- 빌드 대상: `cicd_config.json`의 `ci_allow_list`에 지정되고 `/devices`에도 존재하는 기기.
- 플랫폼별 이미지: `chip-build` 기반, 도구 체인은 `/opt`에 위치.
- `bundle_$PLATFORM`은 빌드 산출물을 `_CD_STAGING_DIR`로 복사하거나 이동한다.
- 참고 함수: `bundle_esp32`.

로컬 CI 실행 예:

```shell
docker run -it --mount source=$(pwd),target=/workspace,type=bind ghcr.io/project-chip/chip-build-$PLATFORM:$VERSION
```

컨테이너 내부:

```shell
chown -R $(whoami) /workspace
cd /workspace
source ./scripts/bootstrap.sh
source ./scripts/activate.sh
./examples/chef/chef.py --ci -t $PLATFORM
```

플랫폼 추가 시 `bundle_$PLATFORM`을 구현하고, 컨테이너에서 빌드와 패키징을 확인한 뒤 Chef workflow에 작업을 추가한다. README의 작업 예시는 `actions/checkout@v3`, `./.github/actions/checkout-submodules-and-bootstrap`, `./scripts/run_in_build_env.sh`를 사용한다.

CD 관련 항목:

- `integrations/cloudbuild/`의 `chef.yaml`.
- 이미지 `chip-build-vscode`.
- 이미지 정의 `docker/images/chip-build-vscode/Dockerfile`.
- 플랫폼 목록 `cicd_config.json`의 `cd_platforms`.

```json
"linux": {
    "linux_x86": ["--cpu_type", "x64"],
    "linux_arm64_ipv6only": ["--cpu_type", "arm64", "--ipv6only"]
},
```

로컬 CD 실행 예:

```shell
docker run -it --mount source=$(pwd),target=/workspace,type=bind ghcr.io/project-chip/chip-build-vscode:$VERSION
```

```shell
chown -R $(whoami) /workspace
cd /workspace
source ./scripts/bootstrap.sh
source ./scripts/activate.sh
./examples/chef/chef.py --build_all --keep_going
```

#### 새 기기 추가

- 새 유형 작성 안내: `NEW_CHEF_DEVICES.md`.
- `python sample_app_util.py zap <zap_file> --rename-file`로 파일 이름을 변경하고 `examples/chef/devices`에 배치.
- 상세 안내: `examples/chef/sample_app_util/`의 `README`.
- `scripts/tools/zap_regen_all.py` 실행 후 `zzz_generated`와 `examples/chef/devices` 커밋.
- 검증 workflow: `.github/workflows/zap_templates.yaml`.
- 저장소에 추가한 모든 기기는 CD에서 빌드된다.

#### 제조사 확장 예

`rootnode_onofflight_meisample*`은 다음 파일에 정의된 `Sample MEI`를 사용한다.

`src/app/zap-templates/zcl/data-model/chip/sample-mei-cluster.xml`

구성:

- boolean 속성 `flip-flop`.
- 인자 없는 `ping`.
- 두 `uint8` 인자의 합을 응답하는 `add-arguments` 명령·응답 쌍.

```shell
chip-tool pairing onnetwork 1 20202021
chip-tool samplemei add-arguments 1 1 10 20
chip-tool samplemei write flip-flop 0 1 1
chip-tool samplemei read flip-flop 1 1
```

### 8. `refrigerator-app`

#### 엔드포인트와 온도 단계 방식

출처:

- `examples/refrigerator-app/refrigerator-common/refrigerator-app.matter`
- `examples/refrigerator-app/refrigerator-common/refrigerator-app.zap`

| 엔드포인트 | 기기 유형 | 서버 클러스터 |
|---|---|---|
| `0` | `ma_rootdevice = 22, version 5` | 제공된 IDL 블록에 서버 구성 없음 |
| `1` | `ma_refrigerator = 112, version 1` | `Descriptor` |
| `2` | `ma_temperature_controlled_cabinet = 113, version 1` | `Descriptor`, `TemperatureControl` |
| `3` | `ma_temperature_controlled_cabinet = 113, version 1` | `Descriptor`, `TemperatureControl` |

엔드포인트 `2`, `3`:

- `Descriptor.tagList` 포함.
- `selectedTemperatureLevel`: IDL에서 `ram`, ZAP에서 `RAM`.
- `supportedTemperatureLevels`: IDL에서 `callback`, ZAP에서 `External`.
- `featureMap = 2`.
- `SetTemperature` 처리.

ZAP의 모든 제공된 엔드포인트에서 `parentEndpointIdentifier = null`이다. 이는 캐비닛의 `parentEndpointIdentifier = 1`을 지정한 Chef 냉장고 예제와 다르다.

#### `AppSupportedTemperatureLevelsDelegate`

출처:

- `examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h`
- `examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp`

참조 헤더:

- `app/clusters/temperature-control-server/supported-temperature-levels-manager.h`
- `app/util/config.h`

`AppSupportedTemperatureLevelsDelegate`는 `SupportedTemperatureLevelsIteratorDelegate`를 상속한다.

내부 `EndpointPair`:

| 필드 | 형식 |
|---|---|
| `mEndpointId` | `EndpointId` |
| `mTemperatureLevels` | `CharSpan *` |
| `mSize` | `uint8_t` |

정적 온도 단계:

```cpp
CharSpan AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions[] = { "Hot"_span, "Warm"_span, "Freezing"_span };
```

`supportedOptionsByEndpoints`의 크기는 `MATTER_DM_TEMPERATURE_CONTROL_CLUSTER_SERVER_ENDPOINT_COUNT`이며, 엔드포인트 `2`와 `3`에 같은 `temperatureLevelOptions`를 연결한다.

| 함수 | 동작 |
|---|---|
| `Size()` | `mEndpoint`와 일치하는 `EndpointPair`의 `mSize` 반환; 없으면 `0` |
| `Next(MutableCharSpan & item)` | 일치하는 엔드포인트에서 `mIndex` 항목을 복사; 성공하면 `mIndex++` 후 `CHIP_NO_ERROR` 반환 |

`Next()`는 복사 오류 발생 시 `ChipLogError`로 기록하고 해당 오류를 반환한다. 다음 항목이 없거나 일치하는 엔드포인트가 없으면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.

#### Linux 빌드와 실행

출처: `examples/refrigerator-app/linux/README.md`

문서의 시험 환경:

- Ubuntu for Raspberry Pi Server 20.04 LTS, aarch64.
- Ubuntu for Raspberry Pi Desktop 20.10, aarch64.

도구 설치:

```shell
sudo apt-get install git gcc g++ python pkg-config libssl-dev libdbus-1-dev libglib2.0-dev ninja-build python3-venv python3-dev unzip
```

빌드:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
git submodule update --init
source third_party/connectedhomeip/scripts/activate.sh
gn gen out/debug
ninja -C out/debug
```

생성된 실행 파일·라이브러리·오브젝트 삭제:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
rm -rf out/
```

pigweed RPC 빌드:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
git submodule update --init
source third_party/connectedhomeip/scripts/activate.sh
gn gen out/debug --args='import("//with_pw_rpc.gni")'
ninja -C out/debug
```

런타임 옵션:

| 옵션 | 설명 |
|---|---|
| `--wifi` | WiFi 관리 기능 활성화; WiFi 커미셔닝에 필요 |
| `--thread` | Thread 관리 기능 활성화; 실행 중인 ot-br-posix dbus daemon 필요 |
| `--ble-controller <selector>` | BLE 광고·연결에 사용할 Bluetooth controller 선택 |

Raspberry Pi 4 실행 예:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
sudo out/debug/chip-refrigerator-app --ble-controller 1
```

README는 Raspberry Pi 4, ARM64용 Ubuntu 20.04 이상, USB Bluetooth Dongle을 전제 조건으로 제시한다. Ubuntu server에서는 `pi-bluetooth` 설치가 필요하다고 안내한다.

Echo handler를 사용할 경우:

```shell
gn gen out/debug --args='chip_app_use_echo=true'
ninja -C out/debug
```

RPC console 설치·실행:

```shell
pip3 install out/debug/chip_rpc_console_wheels/*.whl
chip-console -s localhost:33000 -o /<YourFolder>/pw_log.out
```

Device tracing은 RPC 활성화 빌드를 사용한다.

```shell
./{PIGWEED_REPO}/pw_trace_tokenized/py/pw_trace_tokenized/get_trace.py -s localhost:33000 \
 -o {OUTPUT_FILE} -t {ELF_FILE} {PIGWEED_REPO}/pw_trace_tokenized/pw_trace_protos/trace_rpc.proto
```

README의 추가 참조:

- NXP i.MX 8M Mini EVK 교차 빌드: `../../../docs/platforms/nxp/nxp_imx8m_linux_examples.md`.
- Bluetooth controller 선택: `/platforms/linux/ble_settings.md`.

### 9. 원문 간 차이와 확인 범위

제공된 `.matter`와 `.zap`에는 다음 차이가 있다. 값이나 이름을 하나로 보정하지 않고 출처별로 구분한다.

| 대상 | `.matter` | `.zap` |
|---|---|---|
| `all-clusters-app`의 `HepaFilterMonitoring`, `ActivatedCarbonFilterMonitoring` | `revision 1` | `ClusterRevision` 기본값 `"0x0002"` |
| Chef 로봇 청소기의 `Identify` | `revision 6`; 엔드포인트 속성은 `callback` | `ClusterRevision = "0x0005"`; `IdentifyTime`, `IdentifyType`은 `RAM` |
| Chef 로봇 청소기의 `RvcOperationalState` | `revision 3` | `ClusterRevision = "1"` |
| Chef 냉장고 엔드포인트 `2`의 `TemperatureMeasurement` | `revision 6` | `ClusterRevision = "0x0005"` |
| Chef 건조기 기기 유형 | `ma_laundry_dryer = 124` | `deviceTypeName = "MA-laundry-dryer"`이나 `endpointTypeName = "MA-dishwasher"` |
| Chef 로봇 청소기 엔드포인트 `1`의 기기 유형 | `ma_robotic_vacuum_cleaner = 116` | `deviceTypes`에 코드 `17`과 `116` 포함 |
| NXP 세탁기의 `Identify` | `revision 6` | `ClusterRevision = "0x0005"` |
| NXP 세탁기의 `spinSpeedCurrent`, `numberOfRinses` | 엔드포인트에서 `callback` | 대응 `SpinSpeedCurrent`, `NumberOfRinses`는 `RAM` |
| Chef 건조기의 `selectedDrynessLevel` | 엔드포인트에서 `callback` | `SelectedDrynessLevel`은 `RAM` |
| Chef 실내 에어컨의 `fanMode` | 엔드포인트에서 `callback` | `FanMode`는 `NVM` |

또한 다음 구분이 필요하다.

- IDL에 선언된 `ChangeToModeByCoreTag`가 모든 예제의 `handle command` 또는 ZAP 명령 목록에 포함되는 것은 아니다.
- `ScenesManagement`는 제공된 IDL에서 일반 `cluster`로 선언되지만 ZAP의 `Scenes Management`에는 `apiMaturity = "provisional"`이 기록되어 있다.
- ZAP의 `defaultValue = null`과 `defaultValue = ""`는 서로 다른 원문 값이다.
- delegate 본문, 콜백 연결, 엔드포인트 구성에서 직접 확인되지 않는 런타임 동작은 이 페이지에서 추가로 가정하지 않는다.