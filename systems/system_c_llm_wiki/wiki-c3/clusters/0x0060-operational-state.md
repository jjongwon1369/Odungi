---
entity: Operational State
ids: ['0x0060']
source_paths: ['data_model/1.7/clusters/OperationalState.xml', 'src/app/clusters/operational-state-server/CodegenIntegration.cpp', 'src/app/clusters/operational-state-server/CodegenIntegration.h', 'src/app/clusters/operational-state-server/OperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OperationalStateCluster.h', 'src/app/clusters/operational-state-server/OperationalStateDelegate.h', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h', 'src/app/clusters/operational-state-server/README.md', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp', 'src/app/clusters/operational-state-server/RvcOperationalStateCluster.h', 'src/app/clusters/operational-state-server/operational-state-cluster-objects.h', 'src/app/clusters/operational-state-server/operational-state-server.h', 'src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Operational State

## 개요

Operational State(`0x0060`)는 상태 머신을 사용하는 장치의 동작 상태를 원격으로 모니터링하고, 지원되는 경우 변경하는 클러스터다.

- 스펙 이름: `Operational State Cluster`
- 리비전: `3`
- 분류: `hierarchy="base"`, `role="application"`, `scope="Endpoint"`
- PICS 코드: `OPSTATE`
- 구현 클래스: `OperationalState::OperationalStateCluster`
- 기반 클래스: `DefaultServerCluster`
- 파생 구현: `RvcOperationalStateCluster`, `OvenCavityOperationalStateCluster`

구현은 code-driven 데이터 모델을 사용한다. 새 코드는 `OperationalStateCluster`와 `OperationalStateCluster::Delegate`를 직접 사용하며, 기존 코드용으로 `Instance` 및 `OperationalState::Delegate` 호환 계층을 제공한다.

## 스펙

출처: `data_model/1.7/clusters/OperationalState.xml`

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 정의 |
| `2` | `Pause`, `Resume`을 호환되는 모든 상태에서 사용할 수 있도록 변경하고, 기본/파생 클러스터의 예약 범위 정의 |
| `3` | `CountdownTime` 속성을 Q quality로 변경 |

### 데이터 타입

#### `OperationalStateEnum`

모든 항목이 필수다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `Stopped` | 장치가 정지됨 |
| `0x01` | `Running` | 장치가 동작 중임 |
| `0x02` | `Paused` | 동작 중 일시 정지됨 |
| `0x03` | `Error` | 장치가 오류 상태임 |

#### `ErrorStateEnum`

모든 항목이 필수다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `NoError` | 오류 상태가 아님 |
| `0x01` | `UnableToStartOrResume` | 동작을 시작하거나 재개할 수 없음 |
| `0x02` | `UnableToCompleteOperation` | 현재 동작을 완료하지 못함 |
| `0x03` | `CommandInvalidInState` | 현재 상태에서 명령을 처리할 수 없음 |

#### `OperationalStateStruct`

| 필드 ID | 이름 | 타입 | 적합성 및 제약 | 기본값 |
|---|---|---|---|---|
| `0` | `OperationalStateID` | `OperationalStateEnum` | 필수 | `0` |
| `1` | `OperationalStateLabel` | `string` | `OperationalStateID`가 `0x80` 이상 `0xBF` 이하이면 필수; 최대 길이 `64` | 명시 없음 |

#### `ErrorStateStruct`

| 필드 ID | 이름 | 타입 | 적합성 및 제약 | 기본값 |
|---|---|---|---|---|
| `0` | `ErrorStateID` | `ErrorStateEnum` | 필수 | `0` |
| `1` | `ErrorStateLabel` | `string` | `ErrorStateID`가 `0x80` 이상 `0xBF` 이하이면 필수; 최대 길이 `64` | `empty` |
| `2` | `ErrorStateDetails` | `string` | 선택; 최대 길이 `64` | `empty` |

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`다.

| ID | 이름 | 타입 | 적합성 | 품질 및 제약 | 기본값 |
|---|---|---|---|---|---|
| `0x0000` | `PhaseList` | `list` of `string` | 필수 | nullable; 최대 `32`개, 항목 최대 길이 `64` | `MS` |
| `0x0001` | `CurrentPhase` | `uint8` | 필수 | nullable | `MS` |
| `0x0002` | `CountdownTime` | `elapsed-s` | 선택 | nullable; `quieterReporting="true"`; 최댓값 `259200` | `null` |
| `0x0003` | `OperationalStateList` | `list` of `OperationalStateStruct` | 필수 | 제약 설명 본문 없음 | `MS` |
| `0x0004` | `OperationalState` | `OperationalStateEnum` | 필수 | 제약 설명 본문 없음 | 명시 없음 |
| `0x0005` | `OperationalError` | `ErrorStateStruct` | 필수 | 제약 설명 본문 없음 | 명시 없음 |

`CurrentPhase`, `OperationalStateList`, `OperationalState`, `OperationalError`의 제약은 제공된 XML에서 `<desc/>`로만 표시되어 있다.

### 명령

`Pause`, `Stop`, `Start`, `Resume`은 필드가 없는 `commandToServer` 명령이며, 호출 권한은 `operate`, 응답은 `OperationalCommandResponse`다.

| ID | 이름 | 적합성 |
|---|---|---|
| `0x00` | `Pause` | `Resume` 지원 시 필수, 그 외 선택 |
| `0x01` | `Stop` | `Start` 지원 시 필수, 그 외 선택 |
| `0x02` | `Start` | 선택 |
| `0x03` | `Resume` | `Pause` 지원 시 필수, 그 외 선택 |
| `0x04` | `OperationalCommandResponse` | 위 네 명령 중 하나라도 지원하면 필수 |

`OperationalCommandResponse`의 방향은 `responseFromServer`다.

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `CommandResponseState` | `ErrorStateStruct` | 필수 |

### 이벤트

두 이벤트의 읽기 권한은 `view`다.

| ID | 이름 | 우선순위 | 적합성 |
|---|---|---|---|
| `0x00` | `OperationalError` | `critical` | 필수 |
| `0x01` | `OperationCompletion` | `info` | 선택 |

| 이벤트 | 필드 ID | 필드 이름 | 타입 | 적합성 및 품질 |
|---|---|---|---|---|
| `OperationalError` | `0` | `ErrorState` | `ErrorStateStruct` | 필수 |
| `OperationCompletion` | `0` | `CompletionErrorCode` | `enum8` | 필수 |
| `OperationCompletion` | `1` | `TotalOperationalTime` | `elapsed-s` | 선택, nullable |
| `OperationCompletion` | `2` | `PausedTime` | `elapsed-s` | 선택, nullable |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/operational-state-cluster.xml`

### 클러스터 메타데이터

- 이름: `Operational State`
- 코드: `0x0060`
- 정의 매크로: `OPERATIONAL_STATE_CLUSTER`
- 클러스터 domain: `General`
- client/server 모두 활성화되어 있으며, 각각 `init="false"`, `tick="false"`로 설정됨
- 전역 속성 `0xFFFD`: `side="either"`, `value="3"`

이 XML은 Alchemy로 생성되었으며, 원문에 `DO NOT EDIT`가 명시되어 있다. 생성 소스는 `src/app_clusters/OperationalState.adoc`다.

### 타입 및 속성 매핑

`OperationalStateEnum`, `ErrorStateEnum`은 `enum8`로 정의되며, 항목 이름과 값은 스펙과 같다.

| 정의 | SDK 표현 |
|---|---|
| `OperationalStateStruct.OperationalStateID` | `enum8`, 기본값 `0` |
| `OperationalStateStruct.OperationalStateLabel` | `char_string`, `optional="true"`, 길이 `64` |
| `ErrorStateStruct.ErrorStateID` | `enum8`, 기본값 `0` |
| `ErrorStateStruct.ErrorStateLabel` | `char_string`, `optional="true"`, 길이 `64` |
| `ErrorStateStruct.ErrorStateDetails` | `char_string`, `optional="true"`, 길이 `64` |

스펙의 라벨 필드에는 `0x80`부터 `0xBF`까지의 조건부 필수 규칙이 있지만, 제공된 SDK 구조체 정의에는 `optional="true"`로 표현되어 있다.

| ID | 속성 | define | SDK 타입 및 설정 |
|---|---|---|---|
| `0x0000` | `PhaseList` | `PHASE_LIST` | `array`, `entryType="char_string"`, nullable, `length="32"` |
| `0x0001` | `CurrentPhase` | `CURRENT_PHASE` | `int8u`, nullable |
| `0x0002` | `CountdownTime` | `COUNTDOWN_TIME` | `elapsed_s`, nullable, 선택, `max="259200"` |
| `0x0003` | `OperationalStateList` | `OPERATIONAL_STATE_LIST` | `array`, `entryType="OperationalStateStruct"` |
| `0x0004` | `OperationalState` | `OPERATIONAL_STATE` | `OperationalStateEnum`, `max="0x03"` |
| `0x0005` | `OperationalError` | `OPERATIONAL_ERROR` | `ErrorStateStruct` |

제공된 SDK XML의 `CountdownTime`에는 스펙 XML의 `quieterReporting="true"`에 해당하는 명시적 설정이 없다. 구현에서는 `QuieterReportingAttribute<uint32_t>`를 사용한다.

### 명령과 이벤트

- `Pause`, `Stop`, `Start`, `Resume`은 `source="client"`, `optional="true"`이며, 스펙과 같은 적합성 조건을 포함한다.
- SDK 설명은 해당 원격 동작을 지원하는 장치가 대응 명령을 지원해야 한다고 명시한다.
- `OperationalCommandResponse`는 `source="server"`, `optional="true"`, `disableDefaultResponse="true"`다. 다른 명령 중 하나라도 지원하면 필수라는 조건도 포함한다.
- `OperationalError`는 보고 가능한 오류 조건이 감지되면 생성되는 이벤트로 설명된다.
- `OperationCompletion`은 성공 여부와 무관하게 전체 동작이 종료될 때 생성하는 것이 권장된다.
- 시간 필드는 SDK에서 `elapsed_s`로 표현된다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/operational-state-server/OperationalStateCluster.h` | 기본 클러스터, `Delegate`, `Config`, 애플리케이션 API 선언 |
| `src/app/clusters/operational-state-server/OperationalStateCluster.cpp` | 속성, 명령, 이벤트, 보고 처리 |
| `src/app/clusters/operational-state-server/RvcOperationalStateCluster.h` | `RvcOperationalStateCluster` 선언 |
| `src/app/clusters/operational-state-server/RvcOperationalStateCluster.cpp` | RVC 명령 목록, 상태 호환성, `GoHome` 처리 |
| `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.h` | `OvenCavityOperationalStateCluster` 선언 |
| `src/app/clusters/operational-state-server/OvenCavityOperationalStateCluster.cpp` | 파생 클러스터 생성과 명령 목록 |
| `src/app/clusters/operational-state-server/OperationalStateDelegate.h` | 기존 `Instance`와 연결되는 delegate 호환 계층 |
| `src/app/clusters/operational-state-server/CodegenIntegration.h` | `Instance` 래퍼, delegate 어댑터, 등록 저장소 |
| `src/app/clusters/operational-state-server/CodegenIntegration.cpp` | 등록 수명주기, API 전달, 플러그인 콜백 스텁 |
| `src/app/clusters/operational-state-server/operational-state-cluster-objects.h` | 상태·오류 저장 객체 및 이벤트 래퍼 |
| `src/app/clusters/operational-state-server/operational-state-server.h` | 이전 코드 호환용 통합 헤더 |

### 기본 클래스와 설정

`OperationalStateCluster`는 `DefaultServerCluster`를 상속한다.

- 공개 생성자는 endpoint, `Delegate &`, `Config`를 받는다.
- delegate는 클러스터 객체보다 오래 살아 있어야 한다.
- 보호된 생성자는 파생 클러스터의 `ClusterId`와 revision을 별도로 받는다.
- `Config.optionalAttributes`는 `CountdownTime`의 노출 여부를 설정한다.
- `ReadAttribute`는 `ClusterRevision`에 `mRevision`, `FeatureMap`에 `0`을 반환한다.
- 헤더 주석에 따르면 `OperationalState`, `RvcOperationalState`의 revision은 `3`, `OvenCavityOperationalState`는 `2`다.

상태 범위 경계는 다음과 같다.

```cpp
static constexpr uint8_t DerivedClusterNumberSpaceStart = 0x40;
static constexpr uint8_t VendorNumberSpaceStart         = 0x80;
```

### `Delegate` 인터페이스

`OperationalStateCluster::Delegate`의 필수 구현 메서드:

| 메서드 | 역할 |
|---|---|
| `GetCountdownTime` | nullable 카운트다운 값 제공 |
| `GetOperationalStateAtIndex` | 인덱스별 상태 제공 |
| `GetOperationalPhaseAtIndex` | 인덱스별 단계 이름 제공 |
| `HandlePauseStateCallback` | `Pause` 처리 |
| `HandleResumeStateCallback` | `Resume` 처리 |
| `HandleStartStateCallback` | `Start` 처리 |
| `HandleStopStateCallback` | `Stop` 처리 |

`HandleGoHomeCommandCallback`은 기본 구현을 제공하며, `ErrorStateEnum::kUnknownEnumValue`를 설정한다. RVC delegate에서 재정의할 수 있다.

### 속성 조회와 변경

#### 조회

`ReadAttribute`의 주요 동작:

- `PhaseList`: 첫 인덱스 조회가 `CHIP_ERROR_NOT_FOUND`이면 null을 인코딩한다. 목록은 최대 `32`개까지 읽는다.
- `OperationalStateList`: 최대 `kMaxOperationalStateCount = 256`개까지 순회한다. 이 상한은 종료되지 않는 delegate 순회도 제한한다.
- 목록 조회 중 `CHIP_ERROR_NOT_FOUND`이면 정상 종료하고, 다른 오류는 전달한다.
- `CountdownTime`: 캐시가 아니라 `mDelegate.GetCountdownTime()`의 반환값을 인코딩한다.
- `CurrentPhase`, `OperationalState`, `OperationalError`: 내부 저장값을 인코딩한다.
- 처리하지 않는 속성은 `Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 필수 메타데이터와 `mConfig.optionalAttributes`에 따라 선택된 `CountdownTime`을 조합한다.

#### 변경 및 지원 여부 확인

| API | 동작 |
|---|---|
| `SetCurrentPhase` | null이 아닌 값이 지원되지 않으면 `CHIP_ERROR_INVALID_ARGUMENT`; 값이 변경되면 카운트다운 갱신 |
| `SetOperationalState` | `OperationalStateEnum::kError` 또는 미지원 상태를 거부; 기존 오류를 `ErrorStateEnum::kNoError`로 해제하고 필요한 변경 통지 수행 |
| `GetCurrentPhase` | 현재 단계 반환 |
| `GetCurrentOperationalState` | 현재 상태 반환 |
| `GetCurrentOperationalError` | 현재 오류를 출력 인자에 복사 |
| `IsSupportedPhase` | 해당 인덱스의 `GetOperationalPhaseAtIndex` 성공 여부 확인 |
| `IsSupportedOperationalState` | 상태 목록에서 `operationalStateID` 검색 |
| `ReportOperationalStateListChange` | `OperationalStateList` 변경 통지 |
| `ReportPhaseListChange` | `PhaseList` 변경 통지 및 카운트다운 갱신 |

`SetOperationalState`로 오류 상태를 직접 설정할 수 없으며, 오류 감지는 `OnOperationalErrorDetected`로 처리한다.

### `CountdownTime` 보고

`mCountdownTime`은 `QuieterReportingAttribute<uint32_t>`이며 초기값은 `DataModel::NullNullable`다. 생성자는 다음 정책을 설정한다.

- `QuieterReportingPolicyEnum::kMarkDirtyOnIncrement`
- `QuieterReportingPolicyEnum::kMarkDirtyOnChangeToFromZero`

`UpdateCountdownTime`은 delegate에서 최신 값을 가져오고 monotonic timestamp와 함께 `SetValue`에 전달한다.

| 갱신 경로 | 추가 보고 판정 조건 |
|---|---|
| `UpdateCountdownTimeFromDelegate` | 이전 dirty 값과 새 값이 모두 null이 아니고, 새 값이 감소했으며 감소량이 `kDeltaToReport = 10`보다 큰 경우 |
| `UpdateCountdownTimeFromClusterLogic` | `candidate.lastDirtyValue != candidate.newValue`인 경우 |

`SetValue`가 `AttributeDirtyState::kMustReport`를 반환하면 `CountdownTime`의 변경을 통지한다.

### 명령 처리

기본 `AcceptedCommands`는 `Pause`, `Stop`, `Start`, `Resume`을 모두 반환한다. 스펙의 선택적 적합성과 별개로 제공된 기본 구현의 목록은 고정되어 있다.

`GeneratedCommands`는 `OperationalCommandResponse`를 반환한다. 기본 클러스터와 두 파생 클러스터가 같은 응답 ID를 사용하는지 `static_assert`로 확인한다.

명령 처리 공통 사항:

- 필드가 없는 명령에서 `VerifyEndOfContainer()`가 실패하면 `Protocols::InteractionModel::Status::InvalidCommand`를 반환한다.
- 정상 처리 경로에서는 `GenericOperationalError`를 `commandResponseState`에 넣어 `OperationalCommandResponse`를 보낸다.
- 명령 처리 함수 자체가 상태를 직접 변경하지는 않으며, 필요한 경우 delegate 콜백을 호출한다.
- 기본 `HandleDerivedClusterCommand`는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

#### `Pause` / `Resume`

`HandlePauseOrResumeState`가 공통 처리한다.

| 현재 상태 또는 조건 | 처리 |
|---|---|
| `OperationalStateEnum::kStopped` 또는 `OperationalStateEnum::kError` | `ErrorStateEnum::kCommandInvalidInState` |
| `DerivedClusterNumberSpaceStart` 이상, `VendorNumberSpaceStart` 미만 | 파생 상태 호환성 검사; 비호환이면 `ErrorStateEnum::kCommandInvalidInState` |
| `Pause` 요청 시 이미 `OperationalStateEnum::kPaused` | 콜백 없이 `ErrorStateEnum::kNoError` 응답 |
| `Resume` 요청 시 이미 `OperationalStateEnum::kRunning` | 콜백 없이 `ErrorStateEnum::kNoError` 응답 |
| 그 외 오류 없는 경우 | 대응 delegate 콜백 호출 |

기본 `IsDerivedClusterStatePauseCompatible`, `IsDerivedClusterStateResumeCompatible`은 모두 `false`를 반환한다.

#### `Start` / `Stop`

`HandleStartOrStopState`가 공통 처리한다.

- `Start`: 이미 `OperationalStateEnum::kRunning`이면 콜백을 호출하지 않는다.
- `Stop`: 이미 `OperationalStateEnum::kStopped`이면 콜백을 호출하지 않는다.
- 그 외에는 각각 `HandleStartStateCallback`, `HandleStopStateCallback`을 호출한다.

이 처리 함수에는 `Pause` / `Resume`과 같은 별도의 오류 상태 거부 검사가 없다.

### 오류와 완료 이벤트

#### `OnOperationalErrorDetected`

1. 필요하면 상태를 `OperationalStateEnum::kError`로 변경하고 통지한다.
2. 기존 오류와 다르면 오류를 저장하고 `OperationalError` 속성 변경을 통지한다.
3. 카운트다운을 갱신한다.
4. `mContext`가 있으면 `GenericErrorEvent`를 생성한다.

상태나 오류 내용이 이전과 같아도, `mContext`가 있으면 이벤트 생성 경로를 실행한다.

#### `OnOperationCompletionDetected`

- `mContext`가 없으면 즉시 반환한다.
- `GenericOperationCompletionEvent`를 생성한 뒤 카운트다운을 갱신한다.
- `aTotalOperationalTime`, `aPausedTime`은 `Optional<DataModel::Nullable<uint32_t>>`이며 기본값은 `NullOptional`이다.
- 이 함수에는 동작 상태를 변경하는 코드가 없다.

### 파생 클러스터

| 클래스 | `AcceptedCommands` |
|---|---|
| `OperationalStateCluster` | `Pause`, `Stop`, `Start`, `Resume` |
| `RvcOperationalStateCluster` | `Pause`, `Resume`, `GoHome` |
| `OvenCavityOperationalStateCluster` | `Stop`, `Start` |

#### `RvcOperationalStateCluster`

- `Pause` 호환 파생 상태: `RvcOperationalState::OperationalStateEnum::kSeekingCharger`
- `Resume` 호환 파생 상태:
  - `RvcOperationalState::OperationalStateEnum::kCharging`
  - `RvcOperationalState::OperationalStateEnum::kDocked`

`HandleGoHomeCommand`의 동작:

| 현재 상태 | 처리 |
|---|---|
| `RvcOperationalState::OperationalStateEnum::kCharging` 또는 `RvcOperationalState::OperationalStateEnum::kDocked` | `ErrorStateEnum::kCommandInvalidInState` |
| `RvcOperationalState::OperationalStateEnum::kSeekingCharger` | 콜백 없이 `ErrorStateEnum::kNoError` 응답 |
| 그 외 | `HandleGoHomeCommandCallback` 호출 |

알 수 없는 파생 명령은 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

#### `OvenCavityOperationalStateCluster`

자체 ID와 revision을 기본 생성자에 전달하고, `AcceptedCommands`를 `Stop`, `Start`로 제한한다. 제공된 소스에는 추가 상태 호환성 또는 명령 처리 재정의가 없다.

### 상태·오류 저장 객체

`operational-state-cluster-objects.h`는 다음 상수를 정의한다.

- `kOperationalStateLabelMaxSize = 64u`
- `kOperationalErrorLabelMaxSize = 64u`
- `kOperationalErrorDetailsMaxSize = 64u`
- `kOperationalPhaseNameMaxSize = 64u`

`GenericOperationalState`, `GenericOperationalError`는 라벨과 상세 문자열을 내부 버퍼로 복사한다.

- 버퍼보다 긴 입력은 `std::min`으로 복사 길이를 제한한다.
- 선택 값이 없으면 대응 필드를 `NullOptional`로 설정한다.
- 복사 생성과 대입에서도 `Set`을 통해 내부 버퍼에 다시 복사한다.
- `GenericOperationalError::IsEqual`은 ID, 선택 필드의 존재 여부, 문자열 내용을 비교한다.

`GenericErrorEvent`, `GenericOperationCompletionEvent`는 전달받은 `ClusterId`를 저장하고 `GetClusterId`로 반환하여 파생 클러스터의 이벤트에도 사용된다.

### 기존 `Instance` 호환 계층

`CodegenIntegration.h`와 `CodegenIntegration.cpp`의 `Instance`는 기본 클러스터의 API를 전달하고 등록 수명주기를 관리한다.

- 단독 생성자는 `detail::OperationalInstanceBase`를 소유한다.
- `Init`은 `CodegenDataModelProvider::Instance().Registry().Register`를 호출한다. 이미 등록되었으면 `CHIP_NO_ERROR`를 반환한다.
- `Shutdown`은 등록 상태에서만 `Unregister`를 호출한다.
- 소멸 시 아직 등록되어 있으면 오류 로그를 남기고 `Shutdown`을 실행한다.
- 소멸자는 delegate의 `Instance` 연결도 해제한다.
- 파생 객체가 저장소를 제공하는 생성자에서는 클러스터와 등록 저장소가 해당 객체보다 오래 살아 있어야 한다.

`RvcOperationalState::Instance`, `OvenCavityOperationalState::Instance`는 모두 `OperationalState::Instance`를 상속한다.

`OperationalState::Delegate`는 `SetInstance`와 보호된 `GetInstance`를 추가한다. `detail::InstanceDelegateWrapper`는 `VerifyOrDie`로 delegate와 `Instance`의 연결 불변식을 검사한다.

delegate가 없을 때 어댑터의 동작:

- `GetCountdownTime`: `DataModel::NullNullable`
- `GetOperationalStateAtIndex`, `GetOperationalPhaseAtIndex`: `CHIP_ERROR_NOT_FOUND`
- `HandlePauseStateCallback`, `HandleResumeStateCallback`, `HandleStartStateCallback`, `HandleStopStateCallback`: 아무 작업도 하지 않음
- `HandleGoHomeCommandCallback`: `ErrorStateEnum::kUnknownEnumValue` 설정

기존 `RvcOperationalState::Delegate`의 `HandleStartStateCallback`, `HandleStopStateCallback`도 기본적으로 `ErrorStateEnum::kUnknownEnumValue`를 설정한다.

### 플러그인 콜백 스텁

`CodegenIntegration.cpp`의 다음 콜백은 비어 있다.

| 구분 | 초기화 | 종료 | 속성 변경 |
|---|---|---|---|
| 기본 | `emberAfOperationalStateClusterServerInitCallback` | `MatterOperationalStateClusterServerShutdownCallback` | `MatterOperationalStateClusterServerAttributeChangedCallback` |
| RVC | `emberAfRvcOperationalStateClusterServerInitCallback` | `MatterRvcOperationalStateClusterServerShutdownCallback` | `MatterRvcOperationalStateClusterServerAttributeChangedCallback` |
| Oven Cavity | `emberAfOvenCavityOperationalStateClusterServerInitCallback` | `MatterOvenCavityOperationalStateClusterServerShutdownCallback` | `MatterOvenCavityOperationalStateClusterServerAttributeChangedCallback` |

다음 콜백은 모두 `Protocols::InteractionModel::Status::Success`를 반환한다.

- `MatterOperationalStateClusterServerPreAttributeChangedCallback`
- `MatterRvcOperationalStateClusterServerPreAttributeChangedCallback`
- `MatterOvenCavityOperationalStateClusterServerPreAttributeChangedCallback`

소스 주석은 수명주기를 애플리케이션이 제어하도록 이 콜백들을 비워 둔다고 설명한다.

## 관련 문서

### 사용 안내

출처: `src/app/clusters/operational-state-server/README.md`

문서는 다음 사용 방식을 설명한다.

- 새 코드는 기존 `Instance` 대신 `OperationalStateCluster`를 직접 사용한다.
- 기존 호환 방식에서는 `OperationalState::Delegate`를 상속하고 콜백을 구현한다.
- 서버 초기화에는 `Matter<ClusterName>ClusterInitCallback`을 사용한다.
- 서버 종료에는 `Matter<ClusterName>ClusterShutdownCallback`을 사용한다.
- `Server` 한정자가 없는 `emberAf<ClusterName>ClusterInitCallback`, `emberAf<ClusterName>ClusterShutdownCallback`은 client-side 훅이므로 서버 초기화에 사용하지 않는다.
- 이 클러스터의 ZAP accessor 함수는 존재하지 않으며, 속성 접근에는 인스턴스의 `Set…`, `Get…` 메서드를 사용한다.

문서의 초기화 코드에서는 `MatterOperationalStateClusterInitCallback`에서 delegate와 `OperationalState::Instance`를 생성하고, `OperationalStateEnum::kStopped`를 설정한 뒤 `Init`을 호출한다. 종료 코드는 `MatterOperationalStateClusterShutdownCallback`에서 인스턴스를 먼저 삭제하고 delegate를 삭제한다.

### 문서와 제공 소스의 차이

README는 `Matter<ClusterName>ClusterInitCallback` 및 `Matter<ClusterName>ClusterShutdownCallback`의 weak no-op 스텁을 `CodegenIntegration.cpp`가 제공한다고 설명한다.

그러나 제공된 `CodegenIntegration.cpp`에서 확인되는 함수는 `emberAfOperationalStateClusterServerInitCallback`, `MatterOperationalStateClusterServerShutdownCallback` 등의 `Server` 포함 콜백이다. README에 제시된 `MatterOperationalStateClusterInitCallback`, `MatterOperationalStateClusterShutdownCallback`의 정의는 이 소스 조각에 없다.

또한 신규 delegate에 대해서는 `OperationalStateDelegate.h`와 `OperationalStateCluster.h`가 `OperationalStateCluster::Delegate`를 직접 구현하도록 명시한다.

### 새 파생 클러스터 추가 절차

README에 제시된 절차:

1. 스펙에 파생 클러스터를 정의한 뒤 `src/app/zap-templates/zcl/data-model/chip/`에 클러스터 XML을 추가한다.
2. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters`에 추가한다.
3. `scripts/tools/zap/zap_regen_all.py`로 ZAP 및 py_matter_idl 출력을 다시 생성한다.
4. `RvcOperationalStateCluster`를 참고하여 `OperationalStateCluster`를 상속하고 `RegisteredServerCluster`를 통해 등록한다.
5. all-clusters-app 예제를 새 클러스터로 확장한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
