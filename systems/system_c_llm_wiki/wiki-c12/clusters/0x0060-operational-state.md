---
entity: Operational State
ids: ['0x0060']
source_paths: ['data_model/1.7/clusters/OperationalState.xml', 'src/app/clusters/operational-state-server/CodegenIntegration.cpp', 'src/app/clusters/operational-state-server/CodegenIntegration.h', 'src/app/clusters/operational-state-server/OperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateCluster.h', 'src/app/clusters/operational-state-server/OperationalStateDelegate.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-cluster-objects.h', 'src/app/clusters/operational-state-server/operational-state-server.h', 'src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Operational State

## 개요

`Operational State`는 상태 머신을 사용하는 장치의 동작 상태를 원격으로 모니터링하고, 지원되는 경우 변경하기 위한 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Operational State Cluster` |
| 클러스터 ID | `0x0060` |
| revision | `3` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `OPSTATE` |
| scope | `Endpoint` |

`OperationalStateCluster`는 기본 서버 구현이며, `RvcOperationalStateCluster`와 `OvenCavityOperationalStateCluster`의 기반으로 사용된다. 기존 코드와의 호환성을 위해 `Instance` 및 `Delegate` 래퍼도 제공된다.

## 스펙

출처: `data_model/1.7/clusters/OperationalState.xml`

### revision 이력

| revision | 변경 내용 |
|---|---|
| `1` | 최초 정의 |
| `2` | 호환되는 모든 상태에서 `Pause`와 `Resume` 사용 가능. 기본 및 파생 클러스터의 예약 범위 정의 |
| `3` | `CountdownTime` 속성을 Q quality로 변경 |

### 열거형

모든 항목은 필수이다.

| 타입 | 값 | 이름 | 의미 |
|---|---|---|---|
| `OperationalStateEnum` | `0x00` | `Stopped` | 장치가 정지한 상태 |
| `OperationalStateEnum` | `0x01` | `Running` | 장치가 동작 중인 상태 |
| `OperationalStateEnum` | `0x02` | `Paused` | 동작 도중 일시 중지한 상태 |
| `OperationalStateEnum` | `0x03` | `Error` | 장치에 오류가 발생한 상태 |
| `ErrorStateEnum` | `0x00` | `NoError` | 오류 상태가 아님 |
| `ErrorStateEnum` | `0x01` | `UnableToStartOrResume` | 동작을 시작하거나 재개할 수 없음 |
| `ErrorStateEnum` | `0x02` | `UnableToCompleteOperation` | 현재 동작을 완료하지 못함 |
| `ErrorStateEnum` | `0x03` | `CommandInvalidInState` | 현재 상태에서 명령을 처리할 수 없음 |

### 구조체

#### `ErrorStateStruct`

| 필드 ID | 이름 | 타입 | 기본값 | 요구 조건 및 제약 |
|---|---|---|---|---|
| `0` | `ErrorStateID` | `ErrorStateEnum` | `0` | 필수 |
| `1` | `ErrorStateLabel` | `string` | `empty` | `ErrorStateID`가 `0x80` 이상 `0xBF` 이하이면 필수. 최대 길이 `64` |
| `2` | `ErrorStateDetails` | `string` | `empty` | 선택. 최대 길이 `64` |

#### `OperationalStateStruct`

| 필드 ID | 이름 | 타입 | 기본값 | 요구 조건 및 제약 |
|---|---|---|---|---|
| `0` | `OperationalStateID` | `OperationalStateEnum` | `0` | 필수 |
| `1` | `OperationalStateLabel` | `string` | 명시 없음 | `OperationalStateID`가 `0x80` 이상 `0xBF` 이하이면 필수. 최대 길이 `64` |

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 필수 여부 | nullable | 기본값 | 제약 및 quality |
|---|---|---|---|---|---|---|
| `0x0000` | `PhaseList` | `list` (`string`) | 필수 | 허용 | `MS` | 최대 `32`개, 항목당 최대 길이 `64` |
| `0x0001` | `CurrentPhase` | `uint8` | 필수 | 허용 | `MS` | `<desc/>`만 제공됨 |
| `0x0002` | `CountdownTime` | `elapsed-s` | 선택 | 허용 | `null` | 최댓값 `259200`, `quieterReporting="true"` |
| `0x0003` | `OperationalStateList` | `list` (`OperationalStateStruct`) | 필수 | 명시 없음 | `MS` | `<desc/>`만 제공됨 |
| `0x0004` | `OperationalState` | `OperationalStateEnum` | 필수 | 명시 없음 | 명시 없음 | `<desc/>`만 제공됨 |
| `0x0005` | `OperationalError` | `ErrorStateStruct` | 필수 | 명시 없음 | 명시 없음 | `<desc/>`만 제공됨 |

### 명령

`Pause`, `Stop`, `Start`, `Resume`는 입력 필드가 없으며, 호출 권한은 `operate`이다.

| ID | 이름 | 방향 | 지원 조건 | 응답 |
|---|---|---|---|---|
| `0x00` | `Pause` | `commandToServer` | `Resume` 지원 시 필수, 그 외 선택 | `OperationalCommandResponse` |
| `0x01` | `Stop` | `commandToServer` | `Start` 지원 시 필수, 그 외 선택 | `OperationalCommandResponse` |
| `0x02` | `Start` | `commandToServer` | 선택 | `OperationalCommandResponse` |
| `0x03` | `Resume` | `commandToServer` | `Pause` 지원 시 필수, 그 외 선택 | `OperationalCommandResponse` |
| `0x04` | `OperationalCommandResponse` | `responseFromServer` | 위 네 명령 중 하나라도 지원하면 필수 | — |

`OperationalCommandResponse`의 필드:

| 필드 ID | 이름 | 타입 | 필수 여부 |
|---|---|---|---|
| `0` | `CommandResponseState` | `ErrorStateStruct` | 필수 |

### 이벤트

두 이벤트의 읽기 권한은 `view`이다.

| ID | 이름 | 우선순위 | 필수 여부 |
|---|---|---|---|
| `0x00` | `OperationalError` | `critical` | 필수 |
| `0x01` | `OperationCompletion` | `info` | 선택 |

#### `OperationalError` 필드

| 필드 ID | 이름 | 타입 | 필수 여부 |
|---|---|---|---|
| `0` | `ErrorState` | `ErrorStateStruct` | 필수 |

#### `OperationCompletion` 필드

| 필드 ID | 이름 | 타입 | 필수 여부 | nullable |
|---|---|---|---|---|
| `0` | `CompletionErrorCode` | `enum8` | 필수 | 명시 없음 |
| `1` | `TotalOperationalTime` | `elapsed-s` | 선택 | 허용 |
| `2` | `PausedTime` | `elapsed-s` | 선택 | 허용 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml`

### ZAP 정의

| 항목 | 정의 |
|---|---|
| configurator domain | `CHIP` |
| 클러스터 domain | `General` |
| name | `Operational State` |
| code | `0x0060` |
| define | `OPERATIONAL_STATE_CLUSTER` |
| client | 활성화, `init="false"`, `tick="false"` |
| server | 활성화, `init="false"`, `tick="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="3"` |

이 파일은 Alchemy 생성물이며 `DO NOT EDIT`로 표시되어 있다. 생성 주석의 Source는 `src/app_clusters/OperationalState.adoc`이다.

### 타입 및 속성 매핑

- `OperationalStateEnum`과 `ErrorStateEnum`은 `enum8`로 정의되며, 항목 이름과 값은 스펙 정의와 같다.
- `OperationalStateStruct`와 `ErrorStateStruct`는 `0x0060` 및 `0x0061`에 연결된다.
- 구조체의 `OperationalStateID`와 `ErrorStateID`는 `enum8`이며 기본값은 `0`이다.
- `OperationalStateLabel`, `ErrorStateLabel`, `ErrorStateDetails`는 길이 `64`의 `char_string`이며 `optional="true"`로 정의된다.
- 스펙의 상태 ID 범위에 따른 label 필수 조건은 SDK 구조체 정의에 직접 표현되어 있지 않다.

| 속성 | define | SDK 타입 및 제약 |
|---|---|---|
| `PhaseList` | `PHASE_LIST` | `array`, `entryType="char_string"`, `isNullable="true"`, `length="32"` |
| `CurrentPhase` | `CURRENT_PHASE` | `int8u`, `isNullable="true"` |
| `CountdownTime` | `COUNTDOWN_TIME` | `elapsed_s`, `max="259200"`, `isNullable="true"`, `optional="true"` |
| `OperationalStateList` | `OPERATIONAL_STATE_LIST` | `array`, `entryType="OperationalStateStruct"` |
| `OperationalState` | `OPERATIONAL_STATE` | `OperationalStateEnum`, `max="0x03"` |
| `OperationalError` | `OPERATIONAL_ERROR` | `ErrorStateStruct` |

### 명령 및 이벤트 정의

- `Pause`, `Stop`, `Start`, `Resume`는 `source="client"` 및 `optional="true"`로 정의되며, 스펙과 같은 명령 간 지원 조건을 포함한다.
- 각 명령의 설명은 해당 원격 제어 기능을 장치가 지원하면 명령도 지원해야 한다고 규정한다.
- `OperationalCommandResponse`는 `source="server"`, `optional="true"`, `disableDefaultResponse="true"`이다. 다른 명령을 하나라도 지원하면 필수라는 조건도 포함한다.
- `OperationalError`는 보고 가능한 오류 조건이 감지되면 생성된다.
- `OperationCompletion`은 성공 여부와 관계없이 전체 동작이 종료될 때 생성하는 것이 권고된다.
- `TotalOperationalTime`과 `PausedTime`은 SDK에서 `elapsed_s`이며, 선택 및 nullable 필드이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/operational-state-server/OperationalStateCluster.h` | 기본 클러스터, `Config`, `Delegate`, 애플리케이션 API 선언 |
| `src/app/clusters/operational-state-server/OperationalStateCluster.cpp` | 속성 처리, 명령 처리, 이벤트 생성, 보고 정책 구현 |
| `src/app/clusters/operational-state-server/OperationalStateDelegate.h` | 기존 `Instance` 바인딩을 지원하는 `Delegate` |
| `src/app/clusters/operational-state-server/CodegenIntegration.h` | 기존 코드 호환용 `Instance` 및 delegate 래퍼 선언 |
| `src/app/clusters/operational-state-server/CodegenIntegration.cpp` | 등록·해제, API 전달, 플러그인 콜백 구현 |
| `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h` | `OvenCavityOperationalStateCluster` 선언 |
| `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp` | 파생 클러스터 생성 및 수락 명령 정의 |
| `src/app/clusters/operational-state-server/RvcOperationalStateCluster.h` | `RvcOperationalStateCluster` 선언 |
| `src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp` | 파생 상태 호환성 및 `GoHome` 처리 |
| `src/app/clusters/operational-state-server/operational-state-cluster-objects.h` | 상태·오류 저장 객체 및 이벤트 래퍼 |
| `src/app/clusters/operational-state-server/operational-state-server.h` | 기존 코드 호환용 통합 헤더 |

### 기본 구조 및 설정

`OperationalStateCluster`는 `DefaultServerCluster`를 상속한다.

- 생성자는 `EndpointId`, `Delegate &`, `Config`를 받는다.
- 호출자는 `Delegate`가 클러스터 객체보다 오래 유지되도록 보장해야 한다.
- `Config::optionalAttributes`로 선택 속성 노출을 구성한다.
- `OptionalAttributeSet`에 포함된 선택 속성은 `OperationalState::Attributes::CountdownTime::Id`이다.
- 기본 클러스터 생성자는 `OperationalState::Id`와 `OperationalState::kRevision`을 사용한다.
- 파생 클러스터용 생성자는 별도의 `ClusterId`와 revision을 받는다.
- 헤더 주석에 따르면 `OperationalState`와 `RvcOperationalState`는 revision `3`, `OvenCavityOperationalState`는 revision `2`이다.

상태 번호 공간의 구현 상수:

| 상수 | 값 |
|---|---|
| `DerivedClusterNumberSpaceStart` | `0x40` |
| `VendorNumberSpaceStart` | `0x80` |
| `kMaxPhaseNameLength` | `64` |
| `kMaxOperationalStateCount` | `256` |

`mOperationalState`의 초기값은 `0`, `mOperationalError`는 `ErrorStateEnum::kNoError`, `mCountdownTime`은 `DataModel::NullNullable`이다.

### `Delegate` 인터페이스

`OperationalStateCluster::Delegate`는 다음 순수 가상 메서드를 제공한다.

| 메서드 | 역할 |
|---|---|
| `GetCountdownTime` | nullable 남은 시간 제공 |
| `GetOperationalStateAtIndex` | 인덱스별 동작 상태 제공 |
| `GetOperationalPhaseAtIndex` | 인덱스별 단계 이름 제공 |
| `HandlePauseStateCallback` | `Pause` 처리 |
| `HandleResumeStateCallback` | `Resume` 처리 |
| `HandleStartStateCallback` | `Start` 처리 |
| `HandleStopStateCallback` | `Stop` 처리 |

`HandleGoHomeCommandCallback`은 기본 구현이 있으며, `ErrorStateEnum::kUnknownEnumValue`를 설정한다. RVC용 delegate에서 재정의할 수 있다.

### 상태 및 단계 API

| API | 동작 |
|---|---|
| `SetCurrentPhase` | null이 아닌 단계가 지원되지 않으면 `CHIP_ERROR_INVALID_ARGUMENT`. 값이 변경되면 `CountdownTime` 갱신 |
| `SetOperationalState` | `OperationalStateEnum::kError` 또는 미지원 상태이면 `CHIP_ERROR_INVALID_ARGUMENT`. 유효한 상태 설정 시 기존 오류를 `ErrorStateEnum::kNoError`로 해제 |
| `GetCurrentPhase` | 현재 단계 반환 |
| `GetCurrentOperationalState` | 현재 동작 상태 반환 |
| `GetCurrentOperationalError` | 현재 오류를 출력 객체에 복사 |
| `IsSupportedPhase` | `GetOperationalPhaseAtIndex` 성공 여부로 판단 |
| `IsSupportedOperationalState` | delegate의 상태 목록에서 ID 검색 |
| `ReportOperationalStateListChange` | `OperationalStateList` 변경 알림 |
| `ReportPhaseListChange` | `PhaseList` 변경 알림 및 `CountdownTime` 갱신 |

`SetOperationalState`는 `uint8_t` 및 `OperationalStateEnum`을 받는 오버로드를 제공한다. 오류 상태로 전환할 때는 `OnOperationalErrorDetected`를 사용한다.

`IsSupportedOperationalState`의 검색은 최대 `256`개로 제한된다.

### 속성 읽기 및 노출

`ReadAttribute`의 주요 처리:

| 속성 | 처리 |
|---|---|
| `ClusterRevision` | `mRevision` 인코딩 |
| `FeatureMap` | `uint32_t` 값 `0` 인코딩 |
| `PhaseList` | 인덱스 `0` 조회가 `CHIP_ERROR_NOT_FOUND`이면 null. 그 외 최대 `32`개를 목록으로 인코딩 |
| `CurrentPhase` | `mCurrentPhase` 인코딩 |
| `CountdownTime` | `mDelegate.GetCountdownTime()`의 반환값 직접 인코딩 |
| `OperationalStateList` | delegate에서 최대 `256`개를 조회하여 인코딩 |
| `OperationalState` | `mOperationalState` 인코딩 |
| `OperationalError` | `mOperationalError` 인코딩 |

목록 순회에서 `CHIP_ERROR_NOT_FOUND`는 정상 종료로 처리하고, 다른 오류는 반환한다. 처리하지 않는 속성은 `Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 필수 메타데이터와 `mConfig.optionalAttributes`에 따라 선택된 `CountdownTime` 메타데이터를 결합한다.

### `CountdownTime` 보고 정책

`mCountdownTime`은 `QuieterReportingAttribute<uint32_t>`를 사용한다. 생성자에서 다음 정책을 설정한다.

- `QuieterReportingPolicyEnum::kMarkDirtyOnIncrement`
- `QuieterReportingPolicyEnum::kMarkDirtyOnChangeToFromZero`

`UpdateCountdownTime`은 delegate의 현재 값을 가져오고 단조 증가 타임스탬프와 함께 보고 필요성을 판단한다.

| 갱신 경로 | 추가 변경 판정 |
|---|---|
| `UpdateCountdownTimeFromDelegate` | 마지막 dirty 값과 새 값이 모두 null이 아니고, 감소량이 `kDeltaToReport = 10`보다 큰 경우 |
| `UpdateCountdownTimeFromClusterLogic` | 마지막 dirty 값과 새 값이 다른 경우 |

`SetValue`가 `AttributeDirtyState::kMustReport`를 반환하면 `CountdownTime`에 대해 `NotifyAttributeChanged`를 호출한다.

### 오류 및 완료 이벤트

#### `OnOperationalErrorDetected`

1. 현재 상태가 `OperationalStateEnum::kError`가 아니면 전환하고 속성 변경을 알린다.
2. 전달된 오류가 현재 오류와 다르면 저장하고 `OperationalError` 변경을 알린다.
3. `CountdownTime`을 갱신한다.
4. `mContext`가 있으면 `GenericErrorEvent`를 생성한다.

상태나 오류 값이 이미 같더라도, `mContext`가 있으면 이벤트 생성 단계는 수행한다.

#### `OnOperationCompletionDetected`

- `mContext`가 없으면 즉시 반환한다.
- `GenericOperationCompletionEvent`를 생성한 뒤 `CountdownTime`을 갱신한다.
- `aTotalOperationalTime`과 `aPausedTime`의 타입은 `Optional<DataModel::Nullable<uint32_t>>`이며 기본값은 `NullOptional`이다.
- 이 함수에서 동작 상태를 직접 변경하지는 않는다.

### 기본 명령 처리

`AcceptedCommands`는 `Pause`, `Stop`, `Start`, `Resume`를 모두 노출한다. 이는 명령을 선택적으로 정의하는 스펙 및 SDK XML과 구분되는 현재 기본 구현의 동작이다.

`GeneratedCommands`는 `OperationalCommandResponse`를 노출한다. 기본 및 두 파생 클러스터의 해당 응답 ID가 같은지 `static_assert`로 검사한다.

`InvokeCommand`는 다음과 같이 분기한다.

| 명령 | 처리 함수 |
|---|---|
| `Pause`, `Resume` | `HandlePauseOrResumeState` |
| `Start`, `Stop` | `HandleStartOrStopState` |
| 그 외 | `HandleDerivedClusterCommand` |

모든 기본 명령 처리 함수는 `VerifyEndOfContainer`로 필드 없는 입력을 확인한다. 검증 실패 시 `Protocols::InteractionModel::Status::InvalidCommand`를 반환한다.

#### `Pause`와 `Resume`

- 현재 상태가 `OperationalStateEnum::kStopped` 또는 `OperationalStateEnum::kError`이면 `ErrorStateEnum::kCommandInvalidInState`를 설정한다.
- 상태가 `DerivedClusterNumberSpaceStart` 이상 `VendorNumberSpaceStart` 미만이면 파생 상태 호환성 검사를 수행한다.
  - `Pause`: `IsDerivedClusterStatePauseCompatible`
  - `Resume`: `IsDerivedClusterStateResumeCompatible`
- 기본 클래스의 두 호환성 메서드는 `false`를 반환한다.
- `Pause` 대상이 이미 `OperationalStateEnum::kPaused`이면 delegate 호출 없이 성공 응답한다.
- `Resume` 대상이 이미 `OperationalStateEnum::kRunning`이면 delegate 호출 없이 성공 응답한다.
- 오류가 없고 위의 무동작 조건에 해당하지 않으면 해당 delegate 콜백을 호출한다.

#### `Start`와 `Stop`

- `Start` 대상이 이미 `OperationalStateEnum::kRunning`이면 delegate를 호출하지 않는다.
- `Stop` 대상이 이미 `OperationalStateEnum::kStopped`이면 delegate를 호출하지 않는다.
- 그 외에는 각각 `HandleStartStateCallback` 또는 `HandleStopStateCallback`을 호출한다.

`AddCommandResponse`는 `GenericOperationalError`를 `response.commandResponseState`에 넣어 `handler->AddResponse`로 전달한다. 위 명령 처리 함수 자체는 상태 변경을 직접 수행하지 않는다.

### 파생 클러스터

#### `OvenCavityOperationalStateCluster`

- `OperationalState::OperationalStateCluster`를 상속한다.
- 생성 시 `OvenCavityOperationalState::Id`와 `OvenCavityOperationalState::kRevision`을 전달한다.
- `AcceptedCommands`에는 `Stop`과 `Start`만 포함한다.

#### `RvcOperationalStateCluster`

- 생성 시 `RvcOperationalState::Id`와 `RvcOperationalState::kRevision`을 전달한다.
- `AcceptedCommands`에는 `Pause`, `Resume`, `GoHome`을 포함한다.
- `IsDerivedClusterStatePauseCompatible`은 `RvcOperationalState::OperationalStateEnum::kSeekingCharger`에서만 `true`이다.
- `IsDerivedClusterStateResumeCompatible`은 다음 상태에서 `true`이다.
  - `RvcOperationalState::OperationalStateEnum::kCharging`
  - `RvcOperationalState::OperationalStateEnum::kDocked`

`HandleGoHomeCommand`의 처리:

| 조건 | 결과 |
|---|---|
| 입력 검증 실패 | `Protocols::InteractionModel::Status::InvalidCommand` |
| `RvcOperationalState::OperationalStateEnum::kCharging` 또는 `RvcOperationalState::OperationalStateEnum::kDocked` | `ErrorStateEnum::kCommandInvalidInState` |
| 이미 `RvcOperationalState::OperationalStateEnum::kSeekingCharger` | delegate 호출 없이 성공 응답 |
| 그 외 | `HandleGoHomeCommandCallback` 호출 |

지원하지 않는 파생 명령은 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

### 상태·오류 저장 객체

`operational-state-cluster-objects.h`는 다음 크기 상수를 정의한다.

| 상수 | 값 |
|---|---|
| `kOperationalStateLabelMaxSize` | `64u` |
| `kOperationalErrorLabelMaxSize` | `64u` |
| `kOperationalErrorDetailsMaxSize` | `64u` |
| `kOperationalPhaseNameMaxSize` | `64u` |

- `GenericOperationalState`
  - 기본 상태는 `OperationalStateEnum::kStopped`이다.
  - `Set`은 label을 내부 버퍼로 복사하며 버퍼 크기를 초과하는 부분은 잘린다.
  - label이 없으면 `operationalStateLabel`을 `NullOptional`로 설정한다.
  - 복사 생성자와 대입 연산자는 내부 버퍼로 데이터를 복사한다.
- `GenericOperationalError`
  - label과 details를 각각 내부 버퍼로 복사한다.
  - 없는 선택 필드는 `NullOptional`로 설정한다.
  - `IsEqual`은 ID, 선택 필드 존재 여부, 문자열 내용을 비교한다.
- `GenericErrorEvent`와 `GenericOperationCompletionEvent`
  - 기본 이벤트 타입의 인코딩 및 우선순위 기능을 사용한다.
  - 전달받은 `ClusterId`를 보관하여 파생 클러스터에서도 사용할 수 있다.

### 기존 코드 호환 계층

새 코드는 `OperationalStateCluster` 또는 파생 클래스를 직접 생성하고 `ServerClusterInterfaceRegistry`에 등록하도록 안내되어 있다. delegate 역시 `OperationalStateCluster::Delegate`를 직접 구현하는 방식이 권장된다.

#### `Instance` 수명 관리

- 독립 생성자는 `detail::OperationalInstanceBase`를 생성하여 클러스터 저장소를 소유한다.
- 파생용 생성자는 외부 클러스터, `ServerClusterRegistration`, `detail::InstanceDelegateWrapper` 참조를 사용한다. 파생 클래스는 저장소가 래퍼보다 오래 유지되도록 해야 한다.
- `Init`은 `CodegenDataModelProvider::Instance().Registry().Register`로 등록한다. 이미 등록되어 있으면 `CHIP_NO_ERROR`를 반환한다.
- `Shutdown`은 등록되어 있을 때만 `Unregister`를 호출한다.
- 등록된 상태에서 소멸하면 오류를 기록하고 `Shutdown`을 수행한다.
- 소멸 시 delegate의 `Instance` 연결도 해제한다.
- 애플리케이션 API는 기반 `Cluster()`로 전달된다.

`RvcOperationalState::Instance`와 `OvenCavityOperationalState::Instance`는 `OperationalState::Instance`를 상속한다. 각각 `detail::RvcInstanceBase`, `detail::OvenInstanceBase`가 클러스터 및 등록 저장소를 먼저 초기화하도록 구성되어 있다.

#### delegate 연결

`OperationalState::Delegate`는 `SetInstance`와 `GetInstance`를 추가한다. `VerifyOrDie`를 사용하여 서로 다른 `Instance`에 동시에 연결되지 않도록 검사한다.

`detail::InstanceDelegateWrapper`는 기존 delegate 호출을 전달하며, delegate가 없으면 다음과 같이 동작한다.

| 메서드 | 동작 |
|---|---|
| `GetCountdownTime` | `DataModel::NullNullable` 반환 |
| `GetOperationalStateAtIndex` | `CHIP_ERROR_NOT_FOUND` 반환 |
| `GetOperationalPhaseAtIndex` | `CHIP_ERROR_NOT_FOUND` 반환 |
| `HandlePauseStateCallback`, `HandleResumeStateCallback`, `HandleStartStateCallback`, `HandleStopStateCallback` | 추가 처리 없음 |
| `HandleGoHomeCommandCallback` | `ErrorStateEnum::kUnknownEnumValue` 설정 |

기존 `RvcOperationalState::Delegate`의 `HandleStartStateCallback`과 `HandleStopStateCallback`도 `OperationalState::ErrorStateEnum::kUnknownEnumValue`를 설정한다.

### 플러그인 콜백

애플리케이션이 직접 객체를 생성하고 등록하므로 다음 콜백은 빈 구현이다.

| 대상 | 초기화 | 종료 | 속성 변경 |
|---|---|---|---|
| `OperationalState` | `emberAfOperationalStateClusterServerInitCallback` | `MatterOperationalStateClusterServerShutdownCallback` | `MatterOperationalStateClusterServerAttributeChangedCallback` |
| `RvcOperationalState` | `emberAfRvcOperationalStateClusterServerInitCallback` | `MatterRvcOperationalStateClusterServerShutdownCallback` | `MatterRvcOperationalStateClusterServerAttributeChangedCallback` |
| `OvenCavityOperationalState` | `emberAfOvenCavityOperationalStateClusterServerInitCallback` | `MatterOvenCavityOperationalStateClusterServerShutdownCallback` | `MatterOvenCavityOperationalStateClusterServerAttributeChangedCallback` |

다음 사전 속성 변경 콜백은 모두 `Protocols::InteractionModel::Status::Success`를 반환한다.

- `MatterOperationalStateClusterServerPreAttributeChangedCallback`
- `MatterRvcOperationalStateClusterServerPreAttributeChangedCallback`
- `MatterOvenCavityOperationalStateClusterServerPreAttributeChangedCallback`

## 관련 페이지

**사용 기기**

- [Dishwasher](../device-types/dishwasher.md)
- [Laundry Dryer](../device-types/laundry-dryer.md)
- [Laundry Washer](../device-types/laundry-washer.md)
- [Microwave Oven](../device-types/microwave-oven.md)
