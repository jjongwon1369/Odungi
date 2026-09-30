---
entity: all
ids: []
source_paths: ['examples/all-clusters-app/all-clusters-common/all-clusters-app.matter', 'examples/all-clusters-app/all-clusters-common/all-clusters-app.zap', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h', 'examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp', 'examples/chef/README.md', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap', 'examples/laundry-washer-app/nxp/CMakeLists.txt', 'examples/laundry-washer-app/nxp/README.md', 'examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h', 'examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap', 'examples/refrigerator-app/linux/README.md', 'examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.matter', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.zap', 'examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# all

## 개요

제공된 예제는 ZAP 데이터 모델, 자동 생성 IDL, 애플리케이션 delegate 및 callback, 빌드·실행 안내를 포함한다.

| 예제 | 제공 내용 |
|---|---|
| all-clusters-app | 여러 클러스터의 IDL과 ZAP 설정, 세탁 모드 및 세탁 제어 delegate |
| Chef | ZAP 기반 예제 생성 절차, 냉장고·온도 제어 캐비닛 및 실내 에어컨 데이터 모델 |
| NXP Laundry Washer | 세탁기 데이터 모델, 클러스터 초기화·종료, 속성 변경 callback, 플랫폼 안내 |
| Linux Refrigerator | 냉장고 데이터 모델, 정적 온도 단계 delegate, Linux 빌드·실행·RPC 안내 |

`.matter` 파일의 주석은 해당 IDL이 ZAP으로 자동 생성되었으며 열람·코드 검토용임을 명시한다. 클러스터 선언에 포함된 항목과 개별 endpoint에서 실제로 설정한 속성·명령은 구분한다.

## 예시

### 1. 공통 ZAP 설정과 IDL

#### ZAP 메타데이터

제공된 `.zap` 조각은 다음 설정을 공유한다.

| 키 | 값 |
|---|---|
| `fileFormat` | `2` |
| `featureLevel` | `107` |
| `creator` | `"zap"` |
| `commandDiscovery` | `"1"` |
| `defaultResponsePolicy` | `"always"` |
| `manufacturerCodes` | `"0x1002"` |

패키지 설정:

| `type` | `category` | `version` | `path` |
|---|---|---|---|
| `zcl-properties` | `matter` | `1` | `../../../src/app/zap-templates/zcl/zcl.json` |
| `gen-templates-json` | `matter` | `"chip-v1"` | `../../../src/app/zap-templates/app-templates.json` |

NXP Laundry Washer의 패키지 경로는 각각 다음과 같다.

- `../../../../src/app/zap-templates/zcl/zcl.json`
- `../../../../src/app/zap-templates/app-templates.json`

`pathRelativity`는 `relativeToZap`이다.

#### 공통 속성

제공된 IDL의 클러스터 선언은 다음 `readonly` 속성을 포함한다. ZAP 속성 이름은 IDL 이름과 대소문자가 다르므로 각각 원문 표기를 유지한다.

| IDL 이름 | ZAP 이름 | ID | IDL 타입 |
|---|---|---:|---|
| `generatedCommandList` | `GeneratedCommandList` | 65528 | `command_id[]` |
| `acceptedCommandList` | `AcceptedCommandList` | 65529 | `command_id[]` |
| `attributeList` | `AttributeList` | 65531 | `attrib_id[]` |
| `featureMap` | `FeatureMap` | 65532 | `bitmap32` |
| `clusterRevision` | `ClusterRevision` | 65533 | `int16u` |

개별 ZAP 조각에 이 속성들이 모두 나열되는 것은 아니다.

#### 공통 구조체

```text
struct SemanticTagStruct {
  nullable vendor_id mfgCode = 0;
  enum8 namespaceID = 1;
  enum8 tag = 2;
  optional nullable char_string<64> label = 3;
}
```

`Thermostat`의 원자적 쓰기에 사용되는 정의:

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

### 2. all-clusters-app 데이터 모델

출처:

- `examples/all-clusters-app/all-clusters-common/all-clusters-app.matter`
- `examples/all-clusters-app/all-clusters-common/all-clusters-app.zap`

#### 클러스터 목록

아래 ID와 `revision`은 IDL 선언의 값이다. 입력에서 동일하게 반복된 `OnOff` 선언은 한 번만 정리한다.

| 클러스터 | ID | `revision` | 선언된 명령 |
|---|---:|---:|---|
| `Identify` | 3 | 6 | `Identify`, `TriggerEffect` |
| `Groups` | 4 | 5 | `AddGroup`, `ViewGroup`, `GetGroupMembership`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying` |
| `OnOff` | 6 | 7 | `Off`, `On`, `Toggle`, `OffWithEffect`, `OnWithRecallGlobalScene`, `OnWithTimedOff` |
| `Descriptor` | 29 | 3 | 없음 |
| `Binding` | 30 | 1 | 없음 |
| `FixedLabel` | 64 | 1 | 없음 |
| `UserLabel` | 65 | 1 | 없음 |
| `LaundryWasherMode` | 81 | 4 | `ChangeToMode`, `ChangeToModeByCoreTag` |
| `RefrigeratorAndTemperatureControlledCabinetMode` | 82 | 4 | `ChangeToMode`, `ChangeToModeByCoreTag` |
| `LaundryWasherControls` | 83 | 2 | 없음 |
| `TemperatureControl` | 86 | 1 | `SetTemperature` |
| `RefrigeratorAlarm` | 87 | 1 | 없음 |
| `OperationalState` | 96 | 3 | `Pause`, `Stop`, `Start`, `Resume` |
| `ScenesManagement` | 98 | 2 | `AddScene`, `ViewScene`, `RemoveScene`, `RemoveAllScenes`, `StoreScene`, `RecallScene`, `GetSceneMembership`, `CopyScene` |
| `ThermostatMode` | 99 | 1 | `ChangeToMode`, `ChangeToModeByCoreTag` |
| `HepaFilterMonitoring` | 113 | 1 | `ResetCondition` |
| `ActivatedCarbonFilterMonitoring` | 114 | 1 | `ResetCondition` |
| `Thermostat` | 513 | 12 | `SetpointRaiseLower`, `SetWeeklySchedule`, `GetWeeklySchedule`, `ClearWeeklySchedule`, `SetActiveScheduleRequest`, `SetActivePresetRequest`, `AddThermostatSuggestion`, `RemoveThermostatSuggestion`, `AtomicRequest` |
| `FanControl` | 514 | 7 | `Step` |
| `ThermostatUserInterfaceConfiguration` | 516 | 2 | 없음 |
| `TemperatureMeasurement` | 1026 | 6 | 없음 |
| `RelativeHumidityMeasurement` | 1029 | 3 | 없음 |

#### 기본 제어·구성 클러스터

| 클러스터 | 공통 속성을 제외한 IDL 속성 |
|---|---|
| `Identify` | `identifyTime = 0`, `identifyType = 1` |
| `Groups` | `nameSupport = 0` |
| `OnOff` | `onOff = 0`, `globalSceneControl = 16384`, `onTime = 16385`, `offWaitTime = 16386`, `startUpOnOff = 16387` |
| `Descriptor` | `deviceTypeList = 0`, `serverList = 1`, `clientList = 2`, `partsList = 3`, `tagList = 4`, `endpointUniqueID = 5` |
| `Binding` | `binding = 0` |
| `FixedLabel` | `labelList = 0` |
| `UserLabel` | `labelList = 0` |

- `Identify`의 `Identify`와 `TriggerEffect`는 `access(invoke: manage)`를 지정한다.
- `Groups` 명령은 모두 `fabric command`이다. `AddGroup`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying`에는 `access(invoke: manage)`가 지정된다.
- `OnOff`의 `startUpOnOff`는 `optional nullable StartUpOnOffEnum`이며 `access(write: manage)`를 지정한다.
- `Descriptor`의 `tagList`와 `endpointUniqueID`는 `optional`이다.
- `Binding`의 `TargetStruct`는 `fabric_scoped`이며 `node`, `group`, `endpoint`, `cluster`, `fabricIndex`를 포함한다.
- `FixedLabel`의 `labelList`는 `readonly`이고, `UserLabel`의 `labelList`는 `access(write: manage)`를 지정한다. 두 클러스터의 `LabelStruct`는 `char_string<16>` 타입의 `label`과 `value`를 포함한다.

주요 비트맵:

| 클러스터 | 비트맵 | 항목 |
|---|---|---|
| `Groups` | `Feature` | `kGroupNames = 0x1` |
| `Groups` | `NameSupportBitmap` | `kGroupNames = 0x80` |
| `OnOff` | `Feature` | `kLighting = 0x1`, `kDeadFrontBehavior = 0x2`, `kOffOnly = 0x4` |
| `OnOff` | `OnOffControlBitmap` | `kAcceptOnlyWhenOn = 0x1` |
| `Descriptor` | `Feature` | `kTagList = 0x1` |

#### 모드 클러스터

`LaundryWasherMode`, `RefrigeratorAndTemperatureControlledCabinetMode`, `ThermostatMode`는 다음 구조를 사용한다.

| 항목 | 정의 |
|---|---|
| `ModeTagStruct` | `optional vendor_id mfgCode = 0`, `enum16 value = 1` |
| `ModeOptionStruct` | `char_string<64> label = 0`, `int8u mode = 1`, `ModeTagStruct modeTags[] = 2` |
| `supportedModes = 0` | `readonly ModeOptionStruct[]` |
| `currentMode = 1` | `readonly int8u` |
| `coreModeTags = 4` | `provisional readonly optional enum16[]` |
| `Feature` | `kCoreModes = 0x2` |

`ThermostatMode`에는 `optional nullable int8u startUpMode = 2`도 있다.

| 명령 | ID | 요청 | 응답 |
|---|---:|---|---|
| `ChangeToMode` | 0 | `ChangeToModeRequest`: `int8u newMode = 0` | `ChangeToModeResponse` |
| `ChangeToModeByCoreTag` | 2 | `ChangeToModeByCoreTagRequest`: `enum16 newModeTag = 0` | `ChangeToModeResponse` |

`ChangeToModeResponse = 1`은 `enum8 status = 0`과 `optional char_string<64> statusText = 1`을 포함한다.

공통 `ModeTag` 값은 `kAuto = 0`, `kQuick = 1`, `kQuiet = 2`, `kLowNoise = 3`, `kLowEnergy = 4`, `kVacation = 5`, `kMin = 6`, `kMax = 7`, `kNight = 8`, `kDay = 9`이다.

| 클러스터 | 추가 `ModeTag` |
|---|---|
| `LaundryWasherMode` | `kNormal = 16384`, `kDelicate = 16385`, `kHeavy = 16386`, `kWhites = 16387` |
| `RefrigeratorAndTemperatureControlledCabinetMode` | `kRapidCool = 16384`, `kRapidFreeze = 16385` |
| `ThermostatMode` | `kOff = 16384`, `kCool = 16385`, `kHeat = 16386`, `kEmergencyHeat = 16387` |

#### LaundryWasherControls

| 속성 | ID | 타입 및 한정자 |
|---|---:|---|
| `spinSpeeds` | 0 | `readonly optional char_string[]` |
| `spinSpeedCurrent` | 1 | `optional nullable int8u` |
| `numberOfRinses` | 2 | `optional NumberOfRinsesEnum` |
| `supportedRinses` | 3 | `readonly optional NumberOfRinsesEnum[]` |

- `Feature`: `kSpin = 0x1`, `kRinse = 0x2`.
- `NumberOfRinsesEnum`: `kNone = 0`, `kNormal = 1`, `kExtra = 2`, `kMax = 3`.

#### TemperatureControl

| 속성 | ID | 타입 및 한정자 |
|---|---:|---|
| `temperatureSetpoint` | 0 | `readonly optional temperature` |
| `minTemperature` | 1 | `readonly optional temperature` |
| `maxTemperature` | 2 | `readonly optional temperature` |
| `step` | 3 | `readonly optional temperature` |
| `selectedTemperatureLevel` | 4 | `readonly optional int8u` |
| `supportedTemperatureLevels` | 5 | `readonly optional char_string[]` |

`Feature`는 `kTemperatureNumber = 0x1`, `kTemperatureLevel = 0x2`, `kTemperatureStep = 0x4`를 정의한다.

```text
request struct SetTemperatureRequest {
  optional temperature targetTemperature = 0;
  optional int8u targetTemperatureLevel = 1;
}

command SetTemperature(SetTemperatureRequest): DefaultSuccess = 0;
```

#### RefrigeratorAlarm과 OperationalState

`RefrigeratorAlarm`:

- `AlarmBitmap`: `kDoorOpen = 0x1`.
- `readonly` 속성: `mask = 0`, `state = 2`, `supported = 3`.
- `info event Notify = 0`: `AlarmBitmap` 타입의 `active = 0`, `inactive = 1`, `state = 2`, `mask = 3`.

`OperationalState`:

| 속성 | ID | 타입 및 한정자 |
|---|---:|---|
| `phaseList` | 0 | `readonly nullable char_string[]` |
| `currentPhase` | 1 | `readonly nullable int8u` |
| `countdownTime` | 2 | `readonly optional nullable elapsed_s` |
| `operationalStateList` | 3 | `readonly OperationalStateStruct[]` |
| `operationalState` | 4 | `readonly OperationalStateEnum` |
| `operationalError` | 5 | `readonly ErrorStateStruct` |

- `OperationalStateEnum`: `kStopped = 0`, `kRunning = 1`, `kPaused = 2`, `kError = 3`.
- `ErrorStateEnum`: `kNoError = 0`, `kUnableToStartOrResume = 1`, `kUnableToCompleteOperation = 2`, `kCommandInvalidInState = 3`.
- `Pause = 0`, `Stop = 1`, `Start = 2`, `Resume = 3`은 `OperationalCommandResponse = 4`를 반환한다.
- `OperationalCommandResponse`에는 `ErrorStateStruct commandResponseState = 0`이 있다.

| 이벤트 | ID | 우선순위 | 필드 |
|---|---:|---|---|
| `OperationalError` | 0 | `critical` | `ErrorStateStruct errorState = 0` |
| `OperationCompletion` | 1 | `info` | `enum8 completionErrorCode = 0`, `optional nullable elapsed_s totalOperationalTime = 1`, `optional nullable elapsed_s pausedTime = 2` |

#### ScenesManagement

- `readonly int16u sceneTableSize = 1`.
- `readonly SceneInfoStruct fabricSceneInfo[] = 2`.
- `Feature`: `kSceneNames = 0x1`.
- `CopyModeBitmap`: `kCopyAllScenes = 0x1`.
- `AttributeValuePairStruct`는 `attributeID`와 선택적 정수 값 필드 `valueUnsigned8`, `valueSigned8`, `valueUnsigned16`, `valueSigned16`, `valueUnsigned32`, `valueSigned32`, `valueUnsigned64`, `valueSigned64`를 포함한다.
- `ExtensionFieldSetStruct`는 `clusterID`와 `attributeValueList`를 포함한다.
- `SceneInfoStruct`는 `fabric_scoped`이다. `currentScene`, `currentGroup`, `sceneValid`는 `fabric_sensitive`이다.

모든 명령은 `fabric command`이다.

| 명령 | ID | 응답 | `access(invoke: manage)` |
|---|---:|---|---|
| `AddScene` | 0 | `AddSceneResponse` | 지정 |
| `ViewScene` | 1 | `ViewSceneResponse` | 미지정 |
| `RemoveScene` | 2 | `RemoveSceneResponse` | 지정 |
| `RemoveAllScenes` | 3 | `RemoveAllScenesResponse` | 지정 |
| `StoreScene` | 4 | `StoreSceneResponse` | 지정 |
| `RecallScene` | 5 | `DefaultSuccess` | 미지정 |
| `GetSceneMembership` | 6 | `GetSceneMembershipResponse` | 미지정 |
| `CopyScene` | 64 | `CopySceneResponse` | 지정 |

#### 필터 모니터링

`HepaFilterMonitoring`과 `ActivatedCarbonFilterMonitoring`은 다음 속성 및 명령 구성을 공유한다.

| 속성 | ID | 타입 및 한정자 |
|---|---:|---|
| `condition` | 0 | `readonly optional percent` |
| `degradationDirection` | 1 | `readonly optional DegradationDirectionEnum` |
| `changeIndication` | 2 | `readonly ChangeIndicationEnum` |
| `inPlaceIndicator` | 3 | `readonly optional boolean` |
| `lastChangedTime` | 4 | `optional nullable epoch_s` |
| `replacementProductList` | 5 | `readonly optional ReplacementProductStruct[]` |

- `Feature`: `kCondition = 0x1`, `kWarning = 0x2`, `kReplacementProductList = 0x4`.
- `ChangeIndicationEnum`: `kOK = 0`, `kWarning = 1`, `kCritical = 2`.
- `DegradationDirectionEnum`: `kUp = 0`, `kDown = 1`.
- `ProductIdentifierTypeEnum`: `kUPC`, `kGTIN8`, `kEAN`, `kGTIN14`, `kOEM`.
- `ReplacementProductStruct`는 `productIdentifierType`과 `char_string<20> productIdentifierValue`를 포함한다.
- `ResetCondition(): DefaultSuccess = 0`이 선언된다.

#### Thermostat

`Thermostat`의 `Feature`:

| 항목 | 값 |
|---|---|
| `kHeating` | `0x1` |
| `kCooling` | `0x2` |
| `kOccupancy` | `0x4` |
| `kScheduleConfiguration` | `0x8` |
| `kSetback` | `0x10` |
| `kAutoMode` | `0x20` |
| `kLocalTemperatureNotExposed` | `0x40` |
| `kMatterScheduleConfiguration` | `0x80` |
| `kPresets` | `0x100` |
| `kEvents` | `0x200` |
| `kThermostatSuggestions` | `0x400` |
| `kThermostatSensors` | `0x800` |

속성은 온도 측정, 냉난방 설정값 및 제한값, 동작 모드, 일정, preset, 제안, 센서 구성을 포함한다.

| 범주 | 주요 IDL 속성 |
|---|---|
| 측정·요구량 | `localTemperature`, `outdoorTemperature`, `occupancy`, `PICoolingDemand`, `PIHeatingDemand` |
| 설정값 | `occupiedCoolingSetpoint`, `occupiedHeatingSetpoint`, `unoccupiedCoolingSetpoint`, `unoccupiedHeatingSetpoint` |
| 제어·동작 | `controlSequenceOfOperation`, `systemMode`, `thermostatRunningMode`, `thermostatRunningState` |
| 유지 | `temperatureSetpointHold`, `temperatureSetpointHoldDuration`, `setpointHoldExpiryTimestamp` |
| preset·일정 | `presetTypes`, `scheduleTypes`, `activePresetHandle`, `activeScheduleHandle`, `presets`, `schedules` |
| 제안 | `maxThermostatSuggestions`, `thermostatSuggestions`, `currentThermostatSuggestion`, `thermostatSuggestionNotFollowingReason` |
| `provisional` 속성 | `criticalFreezeProtection`, `criticalOverheatProtection`, `sensors`, `availableSensorHandles`, `enabledSensorHandles`, `numberOfSensorScheduleTransitions`, `sensorSchedule` |

관련 구조체는 `ScheduleTransitionStruct`, `ScheduleStruct`, `PresetStruct`, `PresetTypeStruct`, `ScheduleTypeStruct`, `SensorScheduleTransitionStruct`, `ThermostatSensorStruct`, `ThermostatSuggestionStruct`, `WeeklyScheduleTransitionStruct`이다.

| 명령 | ID | 응답 |
|---|---:|---|
| `SetpointRaiseLower` | 0 | `DefaultSuccess` |
| `SetWeeklySchedule` | 1 | `DefaultSuccess` |
| `GetWeeklySchedule` | 2 | `GetWeeklyScheduleResponse` |
| `ClearWeeklySchedule` | 3 | `DefaultSuccess` |
| `SetActiveScheduleRequest` | 5 | `DefaultSuccess` |
| `SetActivePresetRequest` | 6 | `DefaultSuccess` |
| `AddThermostatSuggestion` | 7 | `AddThermostatSuggestionResponse` |
| `RemoveThermostatSuggestion` | 8 | `DefaultSuccess` |
| `AtomicRequest` | 254 | `AtomicResponse` |

`SetWeeklySchedule`, `ClearWeeklySchedule`, `AddThermostatSuggestion`, `RemoveThermostatSuggestion`은 `access(invoke: manage)`를 지정한다.

`AtomicRequestRequest`는 `requestType`, `attributeRequests`, 선택적 `timeout`을 포함한다. `AtomicResponse = 253`은 `statusCode`, `attributeStatus`, 선택적 `timeout`을 포함한다.

선언된 이벤트는 모두 `provisional info`이다.

| 이벤트 | ID |
|---|---:|
| `SystemModeChange` | 0 |
| `LocalTemperatureChange` | 1 |
| `OccupancyChange` | 2 |
| `SetpointChange` | 3 |
| `RunningStateChange` | 4 |
| `RunningModeChange` | 5 |
| `ActiveScheduleChange` | 6 |
| `ActivePresetChange` | 7 |

#### FanControl 및 측정·사용자 인터페이스

`FanControl` 속성:

- `fanMode = 0`, `fanModeSequence = 1`
- `percentSetting = 2`, `percentCurrent = 3`
- `speedMax = 4`, `speedSetting = 5`, `speedCurrent = 6`
- `rockSupport = 7`, `rockSetting = 8`
- `windSupport = 9`, `windSetting = 10`
- `airflowDirection = 11`

`Feature`는 `kMultiSpeed = 0x1`, `kAuto = 0x2`, `kRocking = 0x4`, `kWind = 0x8`, `kStep = 0x10`, `kAirflowDirection = 0x20`이다.

```text
request struct StepRequest {
  StepDirectionEnum direction = 0;
  optional boolean wrap = 1;
  optional boolean lowestOff = 2;
}

command Step(StepRequest): DefaultSuccess = 0;
```

`ThermostatUserInterfaceConfiguration`:

| 속성 | ID | 타입 | 쓰기 권한 지정 |
|---|---:|---|---|
| `temperatureDisplayMode` | 0 | `TemperatureDisplayModeEnum` | 별도 지정 없음 |
| `keypadLockout` | 1 | `KeypadLockoutEnum` | `access(write: manage)` |
| `scheduleProgrammingVisibility` | 2 | `optional ScheduleProgrammingVisibilityEnum` | `access(write: manage)` |

`TemperatureMeasurement`와 `RelativeHumidityMeasurement`는 `readonly nullable` 속성 `measuredValue = 0`, `minMeasuredValue = 1`, `maxMeasuredValue = 2`를 선언한다. 전자는 `temperature`, 후자는 `int16u`를 사용한다. 두 클러스터 모두 `readonly optional int16u tolerance = 3`을 포함한다.

#### all-clusters-app endpoint 설정

ZAP endpoint 매핑:

| `endpointId` | `endpointTypeIndex` | `endpointTypeName` |
|---:|---:|---|
| 0 | 0 | `MA-rootdevice` |
| 1 | 1 | `MA-onofflight` |
| 2 | 2 | `MA-onofflight` |
| 3 | 3 | `MA-genericswitch` |
| 4 | 4 | `MA-genericswitch` |
| 65534 | 5 | `Anonymous Endpoint Type` |

모두 `profileId = 259`, `networkId = 0`, `parentEndpointIdentifier = null`이다.

제공된 IDL의 `endpoint 0`에는 다음 device type이 있다.

```text
device type ma_rootdevice = 22, version 5;
device type ma_powersource = 17, version 1;
```

ZAP 조각에 나타난 구성:

| `endpointId` | 설정된 클러스터 |
|---:|---|
| 0 | `Groups`, `Descriptor`, `Binding`, `Fixed Label`, `User Label`, `Relative Humidity Measurement` |
| 1 | 목록의 모든 IDL 클러스터에 대응하는 server 설정과 `On/Off` client 설정 |
| 2 | `Identify`, `Groups`, `On/Off`, `Descriptor`, `Scenes Management` |
| 3 | `Identify`, `Descriptor` |
| 4 | `Identify`, `Descriptor` |
| 65534 | `Descriptor` |

주요 설정 차이:

- endpoint `1`의 `On/Off` client는 `Off`, `On`, `Toggle`을 송신하도록 설정되어 있다.
- endpoint `1`과 `2`의 `On/Off` server에는 여섯 명령이 모두 설정되어 있다.
- endpoint `1`의 `OnOff`, `StartUpOnOff`는 `NVM`, endpoint `2`의 동일 속성은 `RAM`이다.
- endpoint `1`의 `Laundry Washer Mode` 및 `Refrigerator And Temperature Controlled Cabinet Mode`에는 `ChangeToMode`와 `ChangeToModeResponse`가 나열되어 있다.
- `Thermostat Mode`에는 `ChangeToModeByCoreTag`와 `CoreModeTags`도 설정되어 있다.
- endpoint `4`의 `Identify` 조각에는 속성만 제공되며 명령 목록은 없다.
- `Scenes Management`의 `apiMaturity`는 `"provisional"`이다.

endpoint `1`의 주요 ZAP 기본값:

| 클러스터 | 속성 | `defaultValue` | `storageOption` |
|---|---|---|---|
| `On/Off` | `FeatureMap` | `"0x0001"` | `RAM` |
| `Laundry Washer Controls` | `FeatureMap` | `"3"` | `RAM` |
| `Temperature Control` | `SelectedTemperatureLevel` | `"0"` | `RAM` |
| `Temperature Control` | `FeatureMap` | `"2"` | `RAM` |
| `Refrigerator Alarm` | `Mask`, `State`, `Supported` | 각각 `"1"`, `"0"`, `"1"` | `RAM` |
| `Operational State` | `FeatureMap` | `"0"` | `RAM` |
| `Scenes Management` | `SceneTableSize` | `"16"` | `RAM` |
| `Scenes Management` | `FeatureMap` | `"1"` | `RAM` |
| `Thermostat` | `FeatureMap` | `"0x0F23"` | `RAM` |
| `Thermostat Mode` | `FeatureMap` | `"2"` | `External` |
| `Fan Control` | `FeatureMap` | `"0x3F"` | `RAM` |
| `Fan Control` | `SpeedMax` | `"100"` | `RAM` |

### 3. 세탁기 delegate와 NXP 애플리케이션

#### LaundryWasherControlDelegate

출처:

- `examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h`
- `examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp`

`LaundryWasherControlDelegate`는 `Delegate`를 상속하며 선택지를 정적으로 제공한다.

| 배열 | 값 |
|---|---|
| `spinSpeedsNameOptions` | `"Off"_span`, `"Low"_span`, `"Medium"_span`, `"High"_span` |
| `supportRinsesOptions` | `NumberOfRinsesEnum::kNormal`, `NumberOfRinsesEnum::kExtra` |

| 함수 | 동작 |
|---|---|
| `GetSpinSpeedAtIndex(size_t index, MutableCharSpan & spinSpeed)` | 범위를 검사한 뒤 `chip::CopyCharSpanToMutableCharSpan`의 결과를 반환 |
| `GetSupportedRinseAtIndex(size_t index, NumberOfRinsesEnum & supportedRinse)` | 범위를 검사한 뒤 값을 대입하고 `CHIP_NO_ERROR` 반환 |
| `getLaundryWasherControlDelegate()` | 정적 `instance`의 참조 반환 |

두 조회 함수는 `index`가 `MATTER_ARRAY_SIZE`로 확인한 배열 크기 이상이면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.

#### LaundryWasherModeDelegate

출처:

- `examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h`
- `examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp`

`LaundryWasherModeDelegate`는 `ModeBase::Delegate`를 상속한다.

| 상수 | 값 | `label` | `modeTags` |
|---|---:|---|---|
| `ModeNormal` | 0 | `"Normal"_span` | `ModeTag::kNormal` |
| `ModeDelicate` | 1 | `"Delicate"_span` | `ModeTag::kDelicate`, `ModeBase::ModeTag::kNight`, `ModeBase::ModeTag::kQuiet` |
| `ModeHeavy` | 2 | `"Heavy"_span` | `ModeBase::ModeTag::kMax`, `ModeTag::kHeavy` |
| `ModeWhites` | 3 | `"Whites"_span` | `ModeTag::kWhites` |

각 태그의 `mfgCode`는 `{}`로 초기화된다. `kModeOptions[4]`가 위 항목을 보관한다.

| 함수 | 제공된 동작 |
|---|---|
| `Init()` | `CHIP_NO_ERROR` 반환 |
| `HandleChangeToMode` | `response.status`를 `to_underlying(ModeBase::StatusCode::kSuccess)`로 설정 |
| `GetModeLabelByIndex` | `kModeOptions`의 `label` 복사 |
| `GetModeValueByIndex` | `kModeOptions`의 `mode` 대입 |
| `GetModeTagsByIndex` | 버퍼 크기 검사 후 `std::copy`, `tags.reduce_size` 수행 |
| `LaundryWasherMode::Instance()` | `gLaundryWasherModeInstance` 반환 |
| `LaundryWasherMode::Shutdown()` | instance와 delegate를 삭제하고 포인터를 `nullptr`로 설정 |

세 조회 함수는 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다. `GetModeTagsByIndex`는 출력 목록의 크기가 부족하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.

초기화 callback은 endpoint와 중복 초기화를 검사한다.

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

`MatterLaundryWasherModeClusterShutdownCallback`도 `endpointId == 1`을 검사한다. instance가 있으면 `Shutdown()`을 호출한 뒤 `LaundryWasherMode::Shutdown()`으로 자원을 해제한다.

#### 속성 변경 전달과 delegate 등록

출처:

- `examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp`
- `examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp`
- `examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h`

속성 변경 흐름:

1. `MatterPostAttributeChangeCallback`이 `CHIPDeviceManager::GetInstance().GetCHIPDeviceManagerCallbacks()`를 호출한다.
2. 반환 포인터가 `nullptr`이 아니면 `PostAttributeChangeCallback`에 `path.mEndpointId`, `path.mClusterId`, `path.mAttributeId`, `type`, `size`, `value`를 전달한다.
3. `LaundryWasherApp::DeviceCallbacks::PostAttributeChangeCallback`은 변경 정보를 기록하고 `Clusters::OnOff::Id`를 `OnOnOffPostAttributeChangeCallback`으로 전달한다.
4. `Clusters::OnOff::Attributes::OnOff::Id`에 대해 `value != nullptr`이고 `*value == true`이면 `LaundryWasherMode::Instance()`를 조회한다.
5. instance가 있고 `GetOnMode()`의 결과가 null이 아니면 `UpdateCurrentMode(mode.Value())`를 호출한다.

`LaundryWasherApp::DeviceCallbacks`는 `chip::NXP::App::CommonDeviceCallbacks`를 상속한다. `GetDefaultInstance()`는 함수 내부 정적 `sDeviceCallbacks`를 반환한다.

`OnIdentifyPostAttributeChangeCallback`은 헤더에 선언되어 있지만 제공된 소스 조각에는 구현이 없다.

`LaundryWasherControls` delegate 등록:

```cpp
void emberAfLaundryWasherControlsClusterInitCallback(EndpointId endpoint)
{
    LaundryWasherControlsServer::SetDefaultDelegate(endpoint, &LaundryWasherControlDelegate::getLaundryWasherControlDelegate());
}
```

#### NXP Laundry Washer 데이터 모델

출처:

- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter`
- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap`

| endpoint | device type | ID | version |
|---:|---|---:|---:|
| 0 | `ma_rootdevice` | 22 | 5 |
| 0 | `ma_otarequestor` | 18 | 1 |
| 1 | `ma_laundry_washer` | 115 | 1 |

endpoint `1`의 server 구성:

| 클러스터 | IDL endpoint 설정 |
|---|---|
| `Identify` | `Identify`, `TriggerEffect` 처리 |
| `OnOff` | 여섯 명령 모두 처리; `onOff`와 `startUpOnOff`는 `persist` |
| `Descriptor` | 목록 및 공통 속성을 `callback`으로 제공 |
| `Binding` | `binding`과 공통 속성을 `callback`으로 제공 |
| `UserLabel` | `labelList`와 공통 속성을 `callback`으로 제공 |
| `LaundryWasherMode` | `supportedModes`, `currentMode`는 `callback`; `ChangeToMode` 처리 |
| `LaundryWasherControls` | 네 개별 속성 모두 `callback`; `featureMap default = 3` |
| `TemperatureControl` | `selectedTemperatureLevel`은 `ram`; `supportedTemperatureLevels`는 `callback`; `featureMap default = 2`; `SetTemperature` 처리 |
| `OperationalState` | `Pause`, `Stop`, `Start`, `Resume` 처리; `OperationalError`, `OperationCompletion` 발생 설정 |

`OnOff`의 기본값:

| 속성 | 저장 방식 | 기본값 |
|---|---|---|
| `onOff` | `persist` | `0` |
| `globalSceneControl` | `ram` | `1` |
| `onTime` | `ram` | `0` |
| `offWaitTime` | `ram` | `0` |
| `startUpOnOff` | `persist` | `0xFF` |
| `featureMap` | `ram` | `2` |
| `clusterRevision` | `ram` | `0x0007` |

ZAP의 endpoint `1`은 `endpointTypeName = "Anonymous Endpoint Type"`이며 device type 이름은 `MA-laundry-washer`이다. 두 endpoint 모두 `profileId = 259`, `networkId = 0`, `parentEndpointIdentifier = null`이다.

#### 빌드 연결 및 지원 플랫폼

출처:

- `examples/laundry-washer-app/nxp/CMakeLists.txt`
- `examples/laundry-washer-app/nxp/README.md`

제공된 CMake 조각의 `target_include_directories(app ...)`에는 다음이 포함된다.

- `${ALL_CLUSTERS_COMMON_DIR}/include`
- `${NXP_EXAMPLE_DIR}/main/include`

`target_sources(app ...)`에는 다음이 포함된다.

- `${NXP_EXAMPLE_DIR}/main/DeviceCallbacks.cpp`
- `${NXP_EXAMPLE_DIR}/main/ZclCallbacks.cpp`
- `${NXP_EXAMPLE_DIR}/main/laundry-washer-mode.cpp`
- `${ALL_CLUSTERS_COMMON_DIR}/src/laundry-washer-controls-delegate-impl.cpp`

지원 플랫폼과 안내 경로:

| 플랫폼 | 안내 |
|---|---|
| RW61x (Zephyr OS) | `../../../docs/platforms/nxp/nxp_zephyr_guide.md` |
| RW61x (FreeRTOS OS) | `../../../docs/platforms/nxp/nxp_rw61x_guide.md` |
| RT1170 | `../../../docs/platforms/nxp/nxp_rt1170_guide.md` |
| RT1060 | `../../../docs/platforms/nxp/nxp_rt1060_guide.md` |

FreeRTOS 공통 안내는 `../../../docs/platforms/nxp/nxp_examples_freertos_platforms.md`이다.

> 이 애플리케이션은 Matter-over-WiFi + Thread Border Router 구성을 지원하지 않는다.

### 4. Chef 냉장고·온도 제어 캐비닛

출처:

- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter`
- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap`

#### endpoint 구성

| endpoint | device type | ID | version | ZAP `parentEndpointIdentifier` |
|---:|---|---:|---:|---|
| 0 | `ma_rootdevice` | 22 | 5 | `null` |
| 1 | `ma_refrigerator` | 112 | 1 | `null` |
| 2 | `ma_temperature_controlled_cabinet` | 113 | 1 | `1` |
| 3 | `ma_temperature_controlled_cabinet` | 113 | 1 | `1` |

- endpoint `1`: `Descriptor`, `RefrigeratorAndTemperatureControlledCabinetMode`, `RefrigeratorAlarm`.
- endpoint `2`, `3`: `Descriptor`, `TemperatureControl`, `TemperatureMeasurement`.
- endpoint `1`은 `ChangeToMode`를 처리하고 `Notify` 발생을 설정한다.
- endpoint `2`, `3`은 `SetTemperature`를 처리한다.
- IDL에 `Identify`와 `FanControl` 선언도 있지만, 제공된 endpoint 블록에는 해당 server 구성이 없다.

#### 온도 기본값

다음 값은 IDL endpoint 설정의 원문 값이다.

| 클러스터 | 속성 | endpoint 2 | endpoint 3 | 저장 방식 |
|---|---|---:|---:|---|
| `TemperatureControl` | `temperatureSetpoint` | 200 | -1800 | `ram` |
| `TemperatureControl` | `minTemperature` | 200 | -1800 | `ram` |
| `TemperatureControl` | `maxTemperature` | 400 | -1500 | `ram` |
| `TemperatureControl` | `step` | 10 | 10 | `ram` |
| `TemperatureControl` | `featureMap` | 5 | 5 | `ram` |
| `TemperatureMeasurement` | `minMeasuredValue` | -4000 | -4000 | `ram` |
| `TemperatureMeasurement` | `maxMeasuredValue` | 2000 | 2000 | `ram` |

`measuredValue`는 `callback`으로 제공한다. 두 캐비닛의 `Descriptor`에는 `tagList`가 설정되어 있다.

### 5. Chef 실내 에어컨

출처:

- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter`
- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap`

| endpoint | device type | ID | version |
|---:|---|---:|---:|
| 0 | `ma_rootdevice` | 22 | 5 |
| 1 | `ma_room_airconditioner` | 114 | 5 |

endpoint `1`의 ZAP device type 이름은 `MA-room-airconditioner`이다.

#### server 구성

| 클러스터 | 처리 명령 | IDL `featureMap` 기본값 |
|---|---|---|
| `Identify` | `Identify`, `TriggerEffect` | 명시되지 않음 |
| `Groups` | `AddGroup`, `ViewGroup`, `GetGroupMembership`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying` | `0` |
| `OnOff` | `Off`, `On`, `Toggle` | `2` |
| `Descriptor` | 없음 | 명시되지 않음 |
| `Thermostat` | `SetpointRaiseLower` | `3` |
| `FanControl` | `Step` | `53` |
| `ThermostatUserInterfaceConfiguration` | 없음 | 명시되지 않음 |

`TemperatureMeasurement`와 `RelativeHumidityMeasurement`는 클러스터 선언에 있으나 제공된 endpoint `1` 블록에는 server 설정이 없다.

#### Thermostat 기본값

| 속성 | 저장 방식 | 기본값 |
|---|---|---|
| `localTemperature` | `ram` | `2800` |
| `absMinHeatSetpointLimit` | `ram` | `0` |
| `absMaxHeatSetpointLimit` | `ram` | `3500` |
| `absMinCoolSetpointLimit` | `ram` | `1000` |
| `absMaxCoolSetpointLimit` | `ram` | `4000` |
| `occupiedCoolingSetpoint` | `persist` | `2300` |
| `occupiedHeatingSetpoint` | `persist` | `2000` |
| `minHeatSetpointLimit` | `persist` | `500` |
| `maxHeatSetpointLimit` | `persist` | `3000` |
| `minCoolSetpointLimit` | `persist` | `1500` |
| `maxCoolSetpointLimit` | `persist` | `3500` |
| `controlSequenceOfOperation` | `persist` | `0x04` |
| `systemMode` | `persist` | `0x01` |
| `ACLouverPosition` | `persist` | `1` |

`FanControl`의 IDL endpoint 설정:

- `fanModeSequence`: `ram`, 기본값 `2`.
- `speedMax`: `ram`, 기본값 `100`.
- `rockSupport`: `ram`, 기본값 `0x01`.
- `fanMode`, `percentSetting`, `percentCurrent`, `speedSetting`, `speedCurrent`, `rockSetting`, `airflowDirection`: `callback`.
- `ThermostatUserInterfaceConfiguration`의 `temperatureDisplayMode`와 `keypadLockout`: `ram`, 기본값 `0x00`.

### 6. Refrigerator 애플리케이션과 온도 단계 delegate

#### 데이터 모델

출처:

- `examples/refrigerator-app/refrigerator-common/refrigerator-app.matter`
- `examples/refrigerator-app/refrigerator-common/refrigerator-app.zap`

| endpoint | device type | ID | version | server 클러스터 |
|---:|---|---:|---:|---|
| 0 | `ma_rootdevice` | 22 | 5 | 제공된 블록에 없음 |
| 1 | `ma_refrigerator` | 112 | 1 | `Descriptor` |
| 2 | `ma_temperature_controlled_cabinet` | 113 | 1 | `Descriptor`, `TemperatureControl` |
| 3 | `ma_temperature_controlled_cabinet` | 113 | 1 | `Descriptor`, `TemperatureControl` |

endpoint `2`, `3`은 다음 설정을 공유한다.

```text
server cluster TemperatureControl {
    ram      attribute selectedTemperatureLevel;
    callback attribute supportedTemperatureLevels;
    callback attribute generatedCommandList;
    callback attribute acceptedCommandList;
    callback attribute attributeList;
    ram      attribute featureMap default = 2;
    callback attribute clusterRevision;

    handle command SetTemperature;
  }
```

Chef 냉장고 예제와 달리 이 ZAP의 모든 endpoint는 `parentEndpointIdentifier = null`이다.

#### AppSupportedTemperatureLevelsDelegate

출처:

- `examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h`
- `examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp`

`AppSupportedTemperatureLevelsDelegate`는 `SupportedTemperatureLevelsIteratorDelegate`를 상속한다.

`EndpointPair` 구성:

| 필드 | 타입 |
|---|---|
| `mEndpointId` | `EndpointId` |
| `mTemperatureLevels` | `CharSpan *` |
| `mSize` | `uint8_t` |

정적 온도 단계:

```cpp
CharSpan AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions[] = { "Hot"_span, "Warm"_span, "Freezing"_span };
```

`supportedOptionsByEndpoints`는 endpoint `2`와 `3`을 동일한 `temperatureLevelOptions` 배열에 연결한다. 배열 크기는 `MATTER_DM_TEMPERATURE_CONTROL_CLUSTER_SERVER_ENDPOINT_COUNT`로 선언된다.

| 함수 | 동작 |
|---|---|
| `Size()` | `mEndpoint`와 일치하는 항목의 `mSize` 반환; 일치하는 항목이 없으면 `0` 반환 |
| `Next(MutableCharSpan & item)` | 해당 endpoint의 `mIndex` 위치 문자열을 복사하고 성공 시 `mIndex` 증가 |

`Next`의 오류 처리:

- `CopyCharSpanToMutableCharSpan`이 실패하면 `ChipLogError`로 기록하고 해당 오류를 반환한다.
- 일치하는 endpoint 또는 다음 항목이 없으면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.
- 복사 성공 시 `CHIP_NO_ERROR`를 반환한다.

#### Linux 빌드 및 실행

출처: `examples/refrigerator-app/linux/README.md`

문서의 테스트 환경은 다음과 같다.

- Ubuntu for Raspberry Pi Server 20.04 LTS (aarch64)
- Ubuntu for Raspberry Pi Desktop 20.10 (aarch64)

도구 설치:

```shell
sudo apt-get install git gcc g++ python pkg-config libssl-dev libdbus-1-dev libglib2.0-dev ninja-build python3-venv python3-dev unzip
```

일반 빌드:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
git submodule update --init
source third_party/connectedhomeip/scripts/activate.sh
gn gen out/debug
ninja -C out/debug
```

pigweed RPC 포함 빌드:

```shell
gn gen out/debug --args='import("//with_pw_rpc.gni")'
ninja -C out/debug
```

Echo handler 활성화:

```shell
gn gen out/debug --args='chip_app_use_echo=true'
ninja -C out/debug
```

실행 예:

```shell
sudo out/debug/chip-refrigerator-app --ble-controller 1
```

| 옵션 | 설명 |
|---|---|
| `--wifi` | WiFi 관리 기능 활성화; WiFi commissioning에 필요 |
| `--thread` | Thread 관리 기능 활성화; `ot-br-posix` dbus daemon 실행 필요 |
| `--ble-controller <selector>` | BLE 광고와 연결에 사용할 Bluetooth controller 선택 |

Raspberry Pi 4 실행 안내는 ARM64 Ubuntu 20.04 이상과 USB Bluetooth Dongle을 전제한다. Ubuntu server에서는 `pi-bluetooth`를 APT로 설치하도록 안내한다.

RPC console:

```shell
pip3 install out/debug/chip_rpc_console_wheels/*.whl
chip-console -s localhost:33000 -o /<YourFolder>/pw_log.out
```

RPC를 활성화한 빌드에서 tracing JSON을 얻는 명령:

```shell
./{PIGWEED_REPO}/pw_trace_tokenized/py/pw_trace_tokenized/get_trace.py -s localhost:33000 \
 -o {OUTPUT_FILE} -t {ELF_FILE} {PIGWEED_REPO}/pw_trace_tokenized/pw_trace_protos/trace_rpc.proto
```

추가 안내 경로:

- NXP i.MX 8M Mini EVK 교차 컴파일: `../../../docs/platforms/nxp/nxp_imx8m_linux_examples.md`
- Bluetooth controller 선택: `/platforms/linux/ble_settings.md`

### 7. Chef 생성·빌드·CI/CD 절차

출처: `examples/chef/README.md`

Chef는 Matter device type의 범위를 늘리고 데이터 모델을 쉽게 구성할 수 있는 샘플 애플리케이션을 제공한다. shell app을 기반으로 하며 `chef.py`가 빌드 시 ZAP 데이터 모델을 처리한다.

#### 폴더와 파일

| 경로 또는 이름 | 역할 |
|---|---|
| `<platform>` | 플랫폼별 빌드 시스템과 `main.cpp` |
| `common` | 플랫폼 공통 코드; `LightingManager`, `LockManager` 등의 기능 코드 |
| `devices` | 사용 가능한 `.zap` 데이터 모델 |
| `out` | 자동 생성 ZAP 산출물의 임시 위치 |
| `zzz_generated` | CI/CD에서 사용하는 산출물 |
| `sample_app_util` | 새 device type 파일 이름 생성 지침과 스크립트 |
| `config.yaml` | toolchain 및 TTY 경로 설정 |
| `chef.py` | 샘플 생성 스크립트 |

`common`의 기능 코드는 관련 클러스터 구성의 존재를 동적으로 확인하고, 해당 클러스터 없이 빌드되는 경우도 유지하도록 안내한다.

#### 첫 샘플 빌드

1. 대상 플랫폼의 toolchain을 설치한다.
2. `chef.py`를 처음 실행하여 `config.yaml`을 생성한다.
3. `config.yaml`의 SDK 및 TTY 경로를 설정한다.
4. `chef.py -u`로 ZAP과 지원되는 플랫폼의 toolchain을 갱신한다.
5. 아래 명령으로 `devices/lighting.zap`을 편집하고 생성·빌드·flash를 수행한다.

```shell
chef.py -gzbf -t <platform> -d lighting
```

6. 전체 옵션은 `chef.py -h`로 확인한다.

초기 설정은 `IDF_PATH`와 `ZEPHYR_BASE` 환경 변수가 있으면 기본값으로 사용한다.

TTY 예:

| 대상 | 경로 |
|---|---|
| ESP32 macOS | `/dev/tty.usbmodemXXXXXXX` |
| ESP32 Linux | `/dev/ttyACM0` |
| NRFCONNECT macOS | `/dev/tty.usbserial-XXXXX` |
| NRFCONNECT Linux | `/dev/ttyUSB0` |

#### Linux 런타임 옵션

빌드 시 `chef.py` 옵션과 구분한다.

| 옵션 | 설명 |
|---|---|
| `--discriminator <discriminator>` | commissioning 광고 값에 대응하는 12-bit unsigned integer |
| `--passcode <passcode>` | commissioning 소유 증명용 27-bit unsigned integer |
| `--spake2p-verifier-base64` | verifier 계산용 passcode를 제공하지 않는 경우 필요한 옵션 |
| `--secured-device-port <port>` | 보안 메시지 수신 포트; 기본값 `5540` |
| `--KVS <filepath>` | Key Value Store 파일 |
| `-h`, `--help` | 생성된 Linux binary의 도움말 출력 |

#### CI

- workflow: `.github/workflows/chef.yaml`
- 플랫폼별 이미지의 기반: `chip-build`
- 이미지 내부 toolchain 위치: `/opt`
- 실행 옵션: `--ci -t $PLATFORM`
- 대상 목록: `cicd_config.json`의 `ci_allow_list`; `/devices`에도 존재하는 장치를 빌드한다.
- `bundle_$PLATFORM`은 빌드 산출물을 `_CD_STAGING_DIR`로 복사하거나 이동한다.
- 참고 함수: `bundle_esp32`

로컬 CI 재현:

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

새 플랫폼은 `bundle_$PLATFORM`을 구현하고 컨테이너 빌드·번들을 확인한 뒤 workflow job을 추가한다.

#### CD

- 빌드 설정 위치: `integrations/cloudbuild/`의 `chef.yaml`
- 사용 이미지: `chip-build-vscode`
- 이미지 정의: `docker/images/chip-build-vscode/Dockerfile`
- 플랫폼 목록: `cicd_config.json`의 `cd_platforms`

Linux 설정 예:

```json
"linux": {
    "linux_x86": ["--cpu_type", "x64"],
    "linux_arm64_ipv6only": ["--cpu_type", "arm64", "--ipv6only"]
},
```

로컬 CD 빌드:

```shell
docker run -it --mount source=$(pwd),target=/workspace,type=bind ghcr.io/project-chip/chip-build-vscode:$VERSION
```

컨테이너 내부:

```shell
chown -R $(whoami) /workspace
cd /workspace
source ./scripts/bootstrap.sh
source ./scripts/activate.sh
./examples/chef/chef.py --build_all --keep_going
```

#### 새 장치와 제조사 확장

새 장치 추가 절차:

```shell
python sample_app_util.py zap <zap_file> --rename-file
scripts/tools/zap_regen_all.py
```

생성된 `examples/chef/devices`와 `zzz_generated`를 커밋한다. 관련 workflow는 `.github/workflows/zap_templates.yaml`이며, 저장소에 추가한 모든 장치는 CD에서 빌드한다. 추가 안내는 `NEW_CHEF_DEVICES.md`와 `examples/chef/sample_app_util/`의 `README`에 있다.

제조사 확장 예제 `rootnode_onofflight_meisample*`는 다음 파일의 Sample MEI cluster를 사용한다.

`src/app/zap-templates/zcl/data-model/chip/sample-mei-cluster.xml`

- boolean 속성: `flip-flop`
- 인자가 없는 명령: `ping`
- 두 uint8 인자의 합을 반환하는 명령·응답: `add-arguments`

원문 테스트 명령:

```shell
chip-tool pairing onnetwork 1 20202021
chip-tool samplemei add-arguments 1 1 10 20
chip-tool samplemei write flip-flop 0 1 1
chip-tool samplemei read flip-flop 1 1
```

### 8. 입력 파일 간 차이

다음 차이는 각 파일의 값을 그대로 유지한다. 제공된 자료만으로 런타임의 최종 값이나 차이의 원인을 단정하지 않는다.

| 대상 | IDL 또는 소스 | ZAP 또는 다른 입력 |
|---|---|---|
| all-clusters-app의 `HepaFilterMonitoring`, `ActivatedCarbonFilterMonitoring` | `revision 1` | `ClusterRevision` 기본값 `"0x0002"` |
| Chef 냉장고의 endpoint `2` `TemperatureMeasurement` | 클러스터 선언 `revision 6` | `ClusterRevision` 기본값 `"0x0005"` |
| Chef 실내 에어컨 및 NXP Laundry Washer의 `Identify` | 클러스터 선언 `revision 6`; endpoint 속성은 `callback` | `IdentifyTime`, `IdentifyType`은 `RAM`; `ClusterRevision` 기본값 `"0x0005"` |
| Chef 냉장고의 `RefrigeratorAlarm` | `mask`, `state`, `supported`, `featureMap`, `clusterRevision`은 `callback` | 대응 속성은 `RAM` |
| Chef 실내 에어컨의 `FanControl` | `fanMode` 등 여러 속성이 `callback` | `FanMode`는 `NVM`, 여러 속성은 `RAM` |
| NXP Laundry Washer의 `LaundryWasherControls` | `spinSpeedCurrent`, `numberOfRinses`는 `callback` | `SpinSpeedCurrent`, `NumberOfRinses`는 `RAM` |
| NXP Laundry Washer의 `OnOff` 연동 | 소스는 `GetOnMode()`를 조회 | 제공된 `LaundryWasherMode` IDL에는 `onMode` 속성이 선언되어 있지 않음 |
| Chef README의 Linux archive 이름 | JSON 키는 `linux_arm64_ipv6only` | 설명 문구는 `linux_arm_64_ipv6only` |

IDL의 전체 클러스터 선언, endpoint의 `handle command` 및 속성 설정, ZAP의 `isEnabled`·`included`·`storageOption`, C++ callback 동작은 서로 다른 정보이므로 하나로 치환하지 않는다.