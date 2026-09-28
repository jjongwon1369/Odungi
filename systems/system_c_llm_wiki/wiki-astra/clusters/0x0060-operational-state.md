---
entity: Operational State
ids: ['0x0060']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateDelegate.h', 'src/app/clusters/operational-state-server/CodegenIntegration.h', 'src/app/clusters/operational-state-server/OperationalStateCluster.h', 'src/app/clusters/operational-state-server/CodegenIntegration.cpp', 'src/app/clusters/operational-state-server/README.md', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-cluster-objects.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-server.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp', 'data_model/1.7/clusters/OperationalState.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Operational State

## 개요

Operational State(`0x0060`)는 상태 머신을 사용하는 장치의 동작 상태를 원격으로 모니터링하고, 지원되는 경우 상태를 변경하는 클러스터다.

- 스펙 revision: `3`
- 분류: `hierarchy="base"`, `role="application"`, `scope="Endpoint"`
- PICS 코드: `OPSTATE`
- 기본 구현: `OperationalState::OperationalStateCluster`
- 기반 클래스: `DefaultServerCluster`
- 파생 구현: `RvcOperationalStateCluster`, `OvenCavityOperationalStateCluster`

구현은 code-driven 데이터 모델을 따른다. 새로운 코드는 `OperationalStateCluster::Delegate`를 직접 구현하고 클러스터를 생성하여 등록한다. 기존 `Instance`와 `OperationalState::Delegate`는 하위 호환 계층으로 제공된다.

## 스펙

출처: `data_model/1.7/clusters/OperationalState.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 최초 revision |
| `2` | 호환되는 모든 상태에서 `Pause`, `Resume` 사용 가능. 기본 및 파생 클러스터의 예약 범위 정의 |
| `3` | `CountdownTime`에 Q quality 적용 |

### 데이터 타입

#### OperationalStateEnum

모든 항목은 필수다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `Stopped` | 장치가 정지됨 |
| `0x01` | `Running` | 장치가 동작 중임 |
| `0x02` | `Paused` | 동작 도중 일시 정지됨 |
| `0x03` | `Error` | 장치에 오류가 있음 |

#### ErrorStateEnum

모든 항목은 필수다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `NoError` | 오류 상태가 아님 |
| `0x01` | `UnableToStartOrResume` | 동작을 시작하거나 재개할 수 없음 |
| `0x02` | `UnableToCompleteOperation` | 현재 동작을 완료하지 못함 |
| `0x03` | `CommandInvalidInState` | 현재 상태에서 명령을 처리할 수 없음 |

#### OperationalStateStruct

| 필드 ID | 이름 | 타입 | 조건 및 제약 |
|---|---|---|---|
| `0` | `OperationalStateID` | `OperationalStateEnum` | 필수, 기본값 `0` |
| `1` | `OperationalStateLabel` | `string` | `OperationalStateID`가 `0x80` 이상 `0xBF` 이하이면 필수. 최대 길이 `64` |

#### ErrorStateStruct

| 필드 ID | 이름 | 타입 | 조건 및 제약 |
|---|---|---|---|
| `0` | `ErrorStateID` | `ErrorStateEnum` | 필수, 기본값 `0` |
| `1` | `ErrorStateLabel` | `string` | `ErrorStateID`가 `0x80` 이상 `0xBF` 이하이면 필수. 기본값 `empty`, 최대 길이 `64` |
| `2` | `ErrorStateDetails` | `string` | 선택, 기본값 `empty`, 최대 길이 `64` |

### 속성

모든 속성은 읽기를 지원하며 `readPrivilege="view"`다.

| ID | 이름 | 타입 | 지원 | nullable | 기본값 및 제약 |
|---|---|---|---|---|---|
| `0x0000` | `PhaseList` | `list` | 필수 | 예 | 기본값 `MS`. `string` 항목 최대 `32`개, 항목별 최대 길이 `64` |
| `0x0001` | `CurrentPhase` | `uint8` | 필수 | 예 | 기본값 `MS` |
| `0x0002` | `CountdownTime` | `elapsed-s` | 선택 | 예 | 기본값 `null`, 최댓값 `259200`, `quieterReporting="true"` |
| `0x0003` | `OperationalStateList` | `list` | 필수 | 아니요 | 기본값 `MS`, 항목 타입 `OperationalStateStruct` |
| `0x0004` | `OperationalState` | `OperationalStateEnum` | 필수 | 아니요 | — |
| `0x0005` | `OperationalError` | `ErrorStateStruct` | 필수 | 아니요 | — |

`CurrentPhase`, `OperationalStateList`, `OperationalState`, `OperationalError`의 추가 제약은 제공된 XML에서 `<desc/>`로만 표현되어 있다.

### 명령

`commandToServer` 명령의 호출 권한은 `invokePrivilege="operate"`이며, 응답은 `OperationalCommandResponse`다.

| ID | 이름 | 방향 | 지원 조건 |
|---|---|---|---|
| `0x00` | `Pause` | `commandToServer` | `Resume` 지원 시 필수, 그 외 선택 |
| `0x01` | `Stop` | `commandToServer` | `Start` 지원 시 필수, 그 외 선택 |
| `0x02` | `Start` | `commandToServer` | 선택 |
| `0x03` | `Resume` | `commandToServer` | `Pause` 지원 시 필수, 그 외 선택 |
| `0x04` | `OperationalCommandResponse` | `responseFromServer` | 위 네 명령 중 하나라도 지원하면 필수 |

`Pause`, `Stop`, `Start`, `Resume`에는 정의된 입력 필드가 없다.

`OperationalCommandResponse`의 필드:

| 필드 ID | 이름 | 타입 | 지원 |
|---|---|---|---|
| `0` | `CommandResponseState` | `ErrorStateStruct` | 필수 |

### 이벤트

두 이벤트 모두 `readPrivilege="view"`다.

| ID | 이름 | priority | 지원 |
|---|---|---|---|
| `0x00` | `OperationalError` | `critical` | 필수 |
| `0x01` | `OperationCompletion` | `info` | 선택 |

| 이벤트 | 필드 ID | 이름 | 타입 | 조건 |
|---|---|---|---|---|
| `OperationalError` | `0` | `ErrorState` | `ErrorStateStruct` | 필수 |
| `OperationCompletion` | `0` | `CompletionErrorCode` | `enum8` | 필수 |
| `OperationCompletion` | `1` | `TotalOperationalTime` | `elapsed-s` | 선택, nullable |
| `OperationCompletion` | `2` | `PausedTime` | `elapsed-s` | 선택, nullable |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 이름 | `Operational State` |
| 클러스터 ID | `0x0060` |
| define | `OPERATIONAL_STATE_CLUSTER` |
| domain | `General` |
| 전역 속성 | `code="0xFFFD"`, `value="3"`, `side="either"` |
| client / server | 모두 활성화, `init="false"`, `tick="false"` |

파일은 Alchemy가 생성한 XML이며 직접 수정하지 않도록 명시되어 있다. 생성 정보에는 `src/app_clusters/OperationalState.adoc`와 `./connectedhomeip-spec/src/app_clusters/OperationalState_RVC.adoc`가 포함된다.

### 타입 및 속성 표현

- `OperationalStateEnum`, `ErrorStateEnum`은 `enum8`로 정의된다.
- `OperationalStateStruct`, `ErrorStateStruct`는 `0x0060`, `0x0061`, `0x0048`에서 공유한다.
- 구조체의 `OperationalStateID`, `ErrorStateID`는 SDK XML에서 `enum8`로 표현된다.
- `OperationalStateLabel`, `ErrorStateLabel`, `ErrorStateDetails`는 `char_string`, `optional="true"`, `length="64"`다.
  - 스펙의 특정 ID 범위에 따른 Label 필수 조건은 이 SDK XML의 `optional="true"` 표현과 구분해야 한다.

| ID | 이름 | define | SDK 타입 및 제약 |
|---|---|---|---|
| `0x0000` | `PhaseList` | `PHASE_LIST` | `array`, `entryType="char_string"`, nullable, `length="32"` |
| `0x0001` | `CurrentPhase` | `CURRENT_PHASE` | `int8u`, nullable |
| `0x0002` | `CountdownTime` | `COUNTDOWN_TIME` | `elapsed_s`, nullable, 선택, `max="259200"` |
| `0x0003` | `OperationalStateList` | `OPERATIONAL_STATE_LIST` | `array`, `entryType="OperationalStateStruct"` |
| `0x0004` | `OperationalState` | `OPERATIONAL_STATE` | `OperationalStateEnum`, `max="0x03"` |
| `0x0005` | `OperationalError` | `OPERATIONAL_ERROR` | `ErrorStateStruct` |

모든 속성은 `side="server"`다.

### 명령 및 이벤트 설명

- 장치가 원격 일시 정지, 정지, 시작, 재개를 지원하면 각각 `Pause`, `Stop`, `Start`, `Resume`을 지원해야 한다.
- 다른 명령이 하나라도 `AcceptedCommandList`에 포함되면 `OperationalCommandResponse`를 지원해야 한다.
- `OperationalCommandResponse`는 `disableDefaultResponse="true"`다.
- `OperationalError`는 보고할 오류 조건을 감지하면 생성한다.
- `OperationCompletion`은 성공 여부와 관계없이 전체 동작이 종료되면 생성하는 것이 권장된다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/operational-state-server/OperationalStateCluster.h` | 기본 클러스터, `Delegate`, `Config`, 애플리케이션 API 선언 |
| `src/app/clusters/operational-state-server/OperationalStateCluster.cpp` | 속성 처리, 상태 변경, 명령 처리, 이벤트 및 보고 로직 |
| `src/app/clusters/operational-state-server/RvcOperationalStateCluster.h` | `RvcOperationalStateCluster` 선언 |
| `src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp` | RVC 명령 목록, 상태 호환성, `GoHome` 처리 |
| `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h` | `OvenCavityOperationalStateCluster` 선언 |
| `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp` | Oven Cavity 생성자 및 명령 목록 |
| `src/app/clusters/operational-state-server/operational-state-cluster-objects.h` | 상태·오류 저장 객체 및 이벤트 래퍼 |
| `src/app/clusters/operational-state-server/OperationalStateDelegate.h` | 기존 `Instance`용 `Delegate` |
| `src/app/clusters/operational-state-server/CodegenIntegration.h` | `Instance`, `InstanceDelegateWrapper`, 등록 저장소 |
| `src/app/clusters/operational-state-server/CodegenIntegration.cpp` | 등록 수명 주기, API 전달, 플러그인 콜백 |
| `src/app/clusters/operational-state-server/operational-state-server.h` | 하위 호환 통합 헤더 |

### 기본 클래스와 구성

`OperationalStateCluster`는 `DefaultServerCluster`를 상속한다.

- 생성자는 `EndpointId`, `Delegate`, `Config`를 받는다.
- 호출자는 `Delegate`가 클러스터 객체보다 오래 유지되도록 해야 한다.
- `Config::optionalAttributes`는 선택 속성 노출을 제어한다.
- `OptionalAttributeSet`에 정의된 선택 속성은 `CountdownTime`이다.
- 파생 클래스는 보호된 생성자에 자신의 클러스터 ID와 revision을 전달한다.
- 헤더 주석에 명시된 revision은 `OperationalState`와 `RvcOperationalState`가 `3`, `OvenCavityOperationalState`가 `2`다.

상태 범위 구분 상수:

| 이름 | 값 |
|---|---|
| `DerivedClusterNumberSpaceStart` | `0x40` |
| `VendorNumberSpaceStart` | `0x80` |

### Delegate 인터페이스

`OperationalStateCluster::Delegate`의 순수 가상 함수:

| 함수 | 역할 |
|---|---|
| `GetCountdownTime` | nullable 카운트다운 값 제공 |
| `GetOperationalStateAtIndex` | 인덱스별 상태 제공 |
| `GetOperationalPhaseAtIndex` | 인덱스별 단계 이름 제공 |
| `HandlePauseStateCallback` | `Pause` 처리 |
| `HandleResumeStateCallback` | `Resume` 처리 |
| `HandleStartStateCallback` | `Start` 처리 |
| `HandleStopStateCallback` | `Stop` 처리 |

`HandleGoHomeCommandCallback`은 기본 구현을 제공하며, 오류를 `ErrorStateEnum::kUnknownEnumValue`로 설정한다. RVC에서 사용하려면 재정의한다.

### 속성 읽기와 목록

`ReadAttribute`의 동작:

- `ClusterRevision`: `mRevision` 반환.
- `FeatureMap`: `0` 반환.
- `PhaseList`:
  - 인덱스 `0` 조회 결과가 `CHIP_ERROR_NOT_FOUND`이면 null 반환.
  - 최대 `32`개 항목을 인코딩.
  - `CHIP_ERROR_NOT_FOUND`에서 목록 종료.
  - 단계 이름 버퍼 크기는 `kMaxPhaseNameLength = 64`.
- `CurrentPhase`: `mCurrentPhase` 반환.
- `CountdownTime`: `mDelegate.GetCountdownTime()`을 직접 호출하여 반환.
- `OperationalStateList`:
  - `GetOperationalStateAtIndex`로 목록 생성.
  - `CHIP_ERROR_NOT_FOUND`에서 종료.
  - `kMaxOperationalStateCount = 256`으로 반복 제한.
- `OperationalState`: `mOperationalState` 반환.
- `OperationalError`: `mOperationalError` 반환.
- 처리하지 않는 속성: `Status::UnsupportedAttribute`.

`Attributes`는 필수 메타데이터와 `mConfig.optionalAttributes`에 따라 선택한 `CountdownTime` 메타데이터를 결합한다.

### 상태 변경 API

| 함수 | 동작 |
|---|---|
| `SetCurrentPhase` | null이 아닌 값은 `IsSupportedPhase`로 검증. 지원하지 않으면 `CHIP_ERROR_INVALID_ARGUMENT`. 변경 시 카운트다운 갱신 |
| `SetOperationalState` | `OperationalStateEnum::kError` 또는 지원하지 않는 상태를 거부. 기존 오류를 `ErrorStateEnum::kNoError`로 초기화하고, 상태 또는 오류 변경 시 카운트다운 갱신 |
| `GetCurrentPhase` | 현재 단계 반환 |
| `GetCurrentOperationalState` | 현재 상태 반환 |
| `GetCurrentOperationalError` | 현재 오류의 ID, Label, Details 복사 |
| `ReportOperationalStateListChange` | `OperationalStateList` 변경 통지 |
| `ReportPhaseListChange` | `PhaseList` 변경 통지 후 카운트다운 갱신 |
| `IsSupportedPhase` | `GetOperationalPhaseAtIndex` 성공 여부 확인 |
| `IsSupportedOperationalState` | 최대 `256`개 상태를 조회하여 ID 일치 여부 확인 |

`SetOperationalState`에는 `uint8_t` 및 `OperationalStateEnum`을 받는 오버로드가 있다. 오류 상태 진입은 `OnOperationalErrorDetected`에서 처리한다.

### 오류 및 완료 이벤트

#### OnOperationalErrorDetected

1. 현재 상태가 `OperationalStateEnum::kError`가 아니면 변경하고 속성 변경을 통지한다.
2. 전달받은 오류가 현재 오류와 다르면 저장하고 `OperationalError` 변경을 통지한다.
3. 카운트다운을 갱신한다.
4. `mContext`가 있으면 `GenericErrorEvent`를 생성하여 현재 클러스터 ID와 endpoint로 이벤트를 발생시킨다.

#### OnOperationCompletionDetected

- `mContext`가 없으면 반환한다.
- `GenericOperationCompletionEvent`에 `aCompletionErrorCode`, `aTotalOperationalTime`, `aPausedTime`을 전달한다.
- 이벤트를 생성한 뒤 카운트다운을 갱신한다.
- 이 함수 자체에서 `OperationalState`를 변경하지는 않는다.

### CountdownTime 보고

`mCountdownTime`은 `QuieterReportingAttribute<uint32_t>`이며 초기값은 `DataModel::NullNullable`이다.

생성자에서 설정하는 정책:

- `QuieterReportingPolicyEnum::kMarkDirtyOnIncrement`
- `QuieterReportingPolicyEnum::kMarkDirtyOnChangeToFromZero`

`UpdateCountdownTime`은 `GetCountdownTime`으로 값을 가져오고 단조 시계 타임스탬프를 사용한다.

| 호출 경로 | 추가 변경 판정 |
|---|---|
| `UpdateCountdownTimeFromDelegate` | 이전 dirty 값과 새 값이 모두 null이 아니고, 값이 감소했으며 감소량이 `kDeltaToReport = 10`보다 크면 보고 대상으로 판정 |
| `UpdateCountdownTimeFromClusterLogic` | 이전 dirty 값과 새 값이 다르면 보고 대상으로 판정 |

`SetValue` 결과가 `AttributeDirtyState::kMustReport`이면 `CountdownTime` 속성 변경을 통지한다.

### 기본 명령 처리

`AcceptedCommands`는 `Pause`, `Stop`, `Start`, `Resume`을 모두 노출한다. `GeneratedCommands`는 `OperationalCommandResponse`를 노출하며, 파생 클러스터들도 같은 응답 명령 ID를 사용하는지 `static_assert`로 확인한다.

`InvokeCommand`의 분기:

| 명령 | 처리 함수 |
|---|---|
| `Pause`, `Resume` | `HandlePauseOrResumeState` |
| `Start`, `Stop` | `HandleStartOrStopState` |
| 그 외 | `HandleDerivedClusterCommand` |

기본 `HandleDerivedClusterCommand`는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

공통 처리:

- `input.VerifyEndOfContainer()`가 실패하면 `Protocols::InteractionModel::Status::InvalidCommand`를 반환한다.
- 오류 객체는 `ErrorStateEnum::kNoError`로 시작한다.
- 정상적인 명령 처리 경로에서는 `AddCommandResponse`가 오류 객체를 `response.commandResponseState`에 넣어 `handler->AddResponse`를 호출한다.
- 콜백 호출 자체로 기본 처리 함수가 상태를 자동 변경하지는 않는다.

#### Pause / Resume

- 현재 상태가 `OperationalStateEnum::kStopped` 또는 `OperationalStateEnum::kError`이면 `ErrorStateEnum::kCommandInvalidInState`.
- 상태 값이 `DerivedClusterNumberSpaceStart` 이상이고 `VendorNumberSpaceStart` 미만이면 파생 상태 호환성을 검사한다.
- 기본 `IsDerivedClusterStatePauseCompatible`, `IsDerivedClusterStateResumeCompatible`는 `false`를 반환한다.
- 오류가 없고 이미 목표 상태가 아니라면 해당 `Delegate` 콜백을 호출한다.

| 명령 | 이미 도달한 경우 콜백을 생략하는 상태 | 콜백 |
|---|---|---|
| `Pause` | `OperationalStateEnum::kPaused` | `HandlePauseStateCallback` |
| `Resume` | `OperationalStateEnum::kRunning` | `HandleResumeStateCallback` |

#### Start / Stop

| 명령 | 이미 도달한 경우 콜백을 생략하는 상태 | 콜백 |
|---|---|---|
| `Start` | `OperationalStateEnum::kRunning` | `HandleStartStateCallback` |
| `Stop` | `OperationalStateEnum::kStopped` | `HandleStopStateCallback` |

`HandleStartOrStopState`에는 위 목표 상태 비교 외의 상태 호환성 검사가 없다.

### 파생 클러스터

#### RvcOperationalStateCluster

`AcceptedCommands`는 `Pause`, `Resume`, `GoHome`을 노출한다.

| 검사 함수 | 호환되는 파생 상태 |
|---|---|
| `IsDerivedClusterStatePauseCompatible` | `RvcOperationalState::OperationalStateEnum::kSeekingCharger` |
| `IsDerivedClusterStateResumeCompatible` | `RvcOperationalState::OperationalStateEnum::kCharging`, `RvcOperationalState::OperationalStateEnum::kDocked` |

`HandleDerivedClusterCommand`는 `GoHome`을 `HandleGoHomeCommand`로 전달하며, 다른 명령에는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

`HandleGoHomeCommand`의 동작:

- 입력 컨테이너 종료 검증 실패: `Protocols::InteractionModel::Status::InvalidCommand`.
- `kCharging` 또는 `kDocked`: `ErrorStateEnum::kCommandInvalidInState`.
- `kSeekingCharger`: 콜백을 호출하지 않고 `kNoError` 응답.
- 그 외 오류가 없는 상태: `HandleGoHomeCommandCallback` 호출.
- 처리 결과는 `OperationalCommandResponse`로 전달.

#### OvenCavityOperationalStateCluster

- 생성자에 `OvenCavityOperationalState::Id`, `OvenCavityOperationalState::kRevision`을 전달한다.
- `AcceptedCommands`는 `Stop`, `Start`만 노출한다.

### 상태·오류 저장 객체

`operational-state-cluster-objects.h`의 크기 상수:

| 이름 | 값 |
|---|---|
| `kOperationalStateLabelMaxSize` | `64u` |
| `kOperationalErrorLabelMaxSize` | `64u` |
| `kOperationalErrorDetailsMaxSize` | `64u` |
| `kOperationalPhaseNameMaxSize` | `64u` |

- `GenericOperationalState`
  - 기본 상태는 `OperationalStateEnum::kStopped`.
  - `Set`은 Label을 내부 버퍼에 복사하고 버퍼 크기로 길이를 제한한다.
  - Label이 없으면 `NullOptional`로 설정한다.
- `GenericOperationalError`
  - `Set`은 Label과 Details를 각각 내부 버퍼에 복사하고 길이를 제한한다.
  - `IsEqual`은 오류 ID, 선택 필드 존재 여부, 문자열 내용을 비교한다.
- `GenericErrorEvent`, `GenericOperationCompletionEvent`
  - 생성 시 받은 클러스터 ID를 `GetClusterId`에서 반환한다.
  - 기본 이벤트 타입의 인코딩, 이벤트 ID, 우선순위, fabric-scoped 정보를 사용한다.

### 하위 호환 계층과 수명 주기

`OperationalState::Delegate`는 `OperationalStateCluster::Delegate`에 `SetInstance`, `GetInstance`를 추가한다.

- `SetInstance`는 `VerifyOrDie`로 기존 연결을 검사한다.
- `InstanceDelegateWrapper`는 `Instance`와 기존 `Delegate`의 연결 일관성을 검사하고 호출을 전달한다.
- 기존 `Delegate`가 없으면:
  - `GetCountdownTime`: `DataModel::NullNullable`
  - 목록 조회: `CHIP_ERROR_NOT_FOUND`
  - `HandlePauseStateCallback`, `HandleResumeStateCallback`, `HandleStartStateCallback`, `HandleStopStateCallback`: 수행 작업 없음
  - `HandleGoHomeCommandCallback`: `ErrorStateEnum::kUnknownEnumValue`

`RvcOperationalState::Delegate`의 `HandleStartStateCallback`, `HandleStopStateCallback`도 `ErrorStateEnum::kUnknownEnumValue`를 설정한다.

`OperationalState::Instance`의 동작:

- 단독 생성자는 `Platform::MakeUnique<detail::OperationalInstanceBase>`로 클러스터 저장소를 소유한다.
- `Init`은 `CodegenDataModelProvider::Instance().Registry().Register`로 등록하며, 이미 등록되었으면 `CHIP_NO_ERROR`를 반환한다.
- `Shutdown`은 등록된 경우 `Unregister`를 호출한다.
- 등록 상태에서 소멸하면 오류 로그를 남기고 `Shutdown`을 호출한다.
- 애플리케이션 API는 내부 `Cluster()`로 전달한다.
- `RvcOperationalState::Instance`, `OvenCavityOperationalState::Instance`는 `OperationalState::Instance`를 상속한다.
- 파생 저장소는 기반 `Instance`가 참조를 받기 전에 초기화되도록 별도의 기반 구조체에 배치된다.

새 코드는 `OperationalStateCluster` 또는 파생 클래스를 직접 생성하고 `ServerClusterInterfaceRegistry`에 등록하도록 안내되어 있다. `operational-state-server.h`는 기존 코드를 위한 통합 헤더다.

### 플러그인 콜백

제공된 `CodegenIntegration.cpp`에서 다음 함수들은 빈 구현이다.

| 클러스터 | 함수 |
|---|---|
| Operational State | `emberAfOperationalStateClusterServerInitCallback`, `MatterOperationalStateClusterServerShutdownCallback`, `MatterOperationalStateClusterServerAttributeChangedCallback` |
| RVC | `emberAfRvcOperationalStateClusterServerInitCallback`, `MatterRvcOperationalStateClusterServerShutdownCallback`, `MatterRvcOperationalStateClusterServerAttributeChangedCallback` |
| Oven Cavity | `emberAfOvenCavityOperationalStateClusterServerInitCallback`, `MatterOvenCavityOperationalStateClusterServerShutdownCallback`, `MatterOvenCavityOperationalStateClusterServerAttributeChangedCallback` |

다음 함수들은 `Protocols::InteractionModel::Status::Success`를 반환한다.

- `MatterOperationalStateClusterServerPreAttributeChangedCallback`
- `MatterRvcOperationalStateClusterServerPreAttributeChangedCallback`
- `MatterOvenCavityOperationalStateClusterServerPreAttributeChangedCallback`

## 관련 문서

출처: `src/app/clusters/operational-state-server/README.md`

### 애플리케이션 연동 안내

README는 기존 `Instance` 방식에 대해 다음 흐름을 제시한다.

1. `OperationalState::Delegate`를 상속하여 콜백을 구현한다.
2. `MatterOperationalStateClusterInitCallback`에서 `Delegate`와 `OperationalState::Instance`를 생성한다.
3. `SetOperationalState`로 `OperationalState::OperationalStateEnum::kStopped`를 설정한다.
4. `Init`을 호출한다.
5. `MatterOperationalStateClusterShutdownCallback`에서 `Instance`를 먼저 삭제하고 `Delegate`를 삭제한다.

새 코드에 대해서는 `OperationalStateCluster` 직접 사용을 권장한다. 구현 헤더는 새 애플리케이션이 `OperationalStateCluster::Delegate`를 직접 구현하도록 명시한다.

README의 주의 사항:

- 서버 초기화·종료 훅은 `Matter<ClusterName>ClusterInitCallback`, `Matter<ClusterName>ClusterShutdownCallback`이다.
- `Server`가 없는 `emberAf<ClusterName>ClusterInitCallback`, `emberAf<ClusterName>ClusterShutdownCallback`은 클라이언트 훅이므로 서버 초기화에 사용하지 않는다.
- 이 클러스터들에는 ZAP accessor 함수가 없으며, 속성 접근에는 인스턴스의 설정·조회 메서드를 사용한다.

> README는 해당 초기화·종료 함수의 weak no-op stub이 `CodegenIntegration.cpp`에 있다고 설명한다. 다만 제공된 `CodegenIntegration.cpp`에는 위에 정리한 `Server` 포함 콜백들이 있으며, README 예시의 `MatterOperationalStateClusterInitCallback`, `MatterOperationalStateClusterShutdownCallback` 정의나 weak 표시는 없다.

### 새 파생 클러스터 추가 절차

README가 제시하는 순서:

1. `src/app/zap-templates/zcl/data-model/chip/`에 클러스터 XML을 추가한다.
2. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters`에 클러스터를 추가한다.
3. `scripts/tools/zap/zap_regen_all.py`로 ZAP 및 py_matter_idl 출력을 재생성한다.
4. `RvcOperationalStateCluster`를 참고하여 `OperationalStateCluster`를 상속하고 `RegisteredServerCluster`로 등록한다.
5. all-clusters-app 예제에 새 클러스터를 추가한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
