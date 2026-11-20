---
entity: RVC Operational State
ids: ['0x0061']
source_paths: ['data_model/1.7/clusters/OperationalState_RVC.xml', 'src/app/clusters/operational-state-server/README.md', 'src/app/zap-templates/zcl/data-model/chip/operational-state-rvc-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# RVC Operational State

## 개요

`RVC Operational State`는 로봇 청소기의 동작 상태를 원격으로 모니터링하고, 지원되는 경우 상태를 변경하는 클러스터이다. `Operational State`를 기반으로 하는 파생 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `RVC Operational State` |
| 스펙 이름 | `RVC Operational State Cluster` |
| 클러스터 ID | `0x0061` |
| 리비전 | `3` |
| 기반 클러스터 | `Operational State` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `RVCOPSTATE` |

## 스펙

출처: `data_model/1.7/clusters/OperationalState_RVC.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 모든 호환 상태에서 `Pause`, `Resume` 사용 허용. `Start`, `Stop` 폐기 예정 처리. `GoHome` 추가 |
| `3` | 여러 동작 상태와 오류 추가 |

### OperationalStateEnum

| 값 | 이름 | 적합성 | 의미 |
|---|---|---|---|
| `0x00` | `Stopped` | 필수 | 장치가 정지한 상태 |
| `0x01` | `Running` | 필수 | 장치가 동작 중인 상태 |
| `0x02` | `Paused` | 필수 | 동작 도중 일시 정지한 상태 |
| `0x03` | `Error` | 필수 | 오류 상태 |
| `0x40` | `SeekingCharger` | 필수 | 충전 도크로 이동 중인 상태 |
| `0x41` | `Charging` | 필수 | 충전 중인 상태 |
| `0x42` | `Docked` | 필수 | 도크에 있으나 충전하지 않는 상태 |
| `0x43` | `EmptyingDustBin` | 선택 | 도크 등으로 자체 먼지통을 자동으로 비우는 상태 |
| `0x44` | `CleaningMop` | 선택 | 도크 등에서 자체 물걸레 장치를 자동으로 세척하는 상태 |
| `0x45` | `FillingWaterTank` | 선택 | 도크 등에서 물걸레 작업용 깨끗한 물탱크를 자동으로 채우는 상태 |
| `0x46` | `UpdatingMaps` | 선택 | 지도를 갱신하기 위해 수집 데이터를 처리하는 상태 |

### ErrorStateEnum

아래 항목은 모두 `mandatoryConform`으로 정의되어 있다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `NoError` | 오류 상태가 아님 |
| `0x01` | `UnableToStartOrResume` | 동작을 시작하거나 재개할 수 없음 |
| `0x02` | `UnableToCompleteOperation` | 현재 동작을 완료하지 못함 |
| `0x03` | `CommandInvalidInState` | 현재 상태에서 명령을 처리할 수 없음 |
| `0x40` | `FailedToFindChargingDock` | 충전 도크를 찾거나 도달하지 못함 |
| `0x41` | `Stuck` | 장치가 갇혀 수동 개입이 필요함 |
| `0x42` | `DustBinMissing` | 먼지통이 없음을 감지함 |
| `0x43` | `DustBinFull` | 먼지통이 가득 찼음을 감지함 |
| `0x44` | `WaterTankEmpty` | 깨끗한 물탱크가 비었음을 감지함 |
| `0x45` | `WaterTankMissing` | 깨끗한 물탱크가 없음을 감지함 |
| `0x46` | `WaterTankLidOpen` | 물탱크 뚜껑이 열렸음을 감지함 |
| `0x47` | `MopCleaningPadMissing` | 청소 패드가 없음을 감지함 |
| `0x48` | `LowBattery` | 배터리가 부족하여 동작을 시작하거나 계속할 수 없음 |
| `0x49` | `CannotReachTargetArea` | 장애물 때문에 요청받은 작업 영역으로 이동할 수 없음. 예: `ServiceArea`의 `SelectedAreas`로 지정한 영역으로 가는 경로가 닫힌 문이나 물체로 막힘 |
| `0x4A` | `DirtyWaterTankFull` | 오수 탱크가 가득 찼음을 감지함 |
| `0x4B` | `DirtyWaterTankMissing` | 오수 탱크가 없음을 감지함 |
| `0x4C` | `WheelsJammed` | 하나 이상의 바퀴가 물체에 걸렸음을 감지함 |
| `0x4D` | `BrushJammed` | 브러시가 물체에 걸렸음을 감지함 |
| `0x4E` | `NavigationSensorObscured` | LiDAR, 적외선 센서, 카메라 등의 센서가 가려져 청소가 필요함 |

### 명령

| ID | 이름 | 제공된 스펙 XML의 정의 |
|---|---|---|
| `0x00` | `Pause` | 명령 선언 |
| `0x01` | `Stop` | `disallowConform`: 허용하지 않음 |
| `0x02` | `Start` | `disallowConform`: 허용하지 않음 |
| `0x03` | `Resume` | 명령 선언 |
| `0x04` | `OperationalCommandResponse` | 명령 선언 |
| `0x80` | `GoHome` | 선택 지원. 방향은 `commandToServer`, 응답은 `OperationalCommandResponse`, 호출 권한은 `operate` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/operational-state-rvc-cluster.xml`

이 파일은 Alchemy로 생성되었으며, 원문에 직접 수정하지 않도록 명시되어 있다. 생성 원본은 `src/app_clusters/OperationalState_RVC.adoc`이다.

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Robots` |
| 이름 | `RVC Operational State` |
| 코드 | `0x0061` |
| define | `OPERATIONAL_STATE_RVC_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="3"` |

### 열거형

`OperationalStateEnum`과 `ErrorStateEnum`은 모두 `enum8`이며, `0x0061`에 연결된다.

- 스펙에 나열된 상태 및 오류 항목을 SDK XML에도 정의한다.
- ZAP XML 제약으로 인해 기반 `OperationalStateCluster`의 값을 각 파생 클러스터에 복사한다.
- 파생 클러스터 전용 값은 `0x40`부터 시작한다.
- SDK의 다음 오류 값은 스펙과 달리 소문자 16진수 표기를 사용한다.

| 이름 | SDK 원문 값 |
|---|---|
| `DirtyWaterTankFull` | `0x4a` |
| `DirtyWaterTankMissing` | `0x4b` |
| `WheelsJammed` | `0x4c` |
| `BrushJammed` | `0x4d` |
| `NavigationSensorObscured` | `0x4e` |

### 속성

모든 속성은 `side="server"`로 정의되어 있다.

| 코드 | 이름 | define | 타입 | 제약 및 선택성 |
|---|---|---|---|---|
| `0x0000` | `PhaseList` | `PHASE_LIST` | `array`, 항목 타입 `char_string` | `isNullable="true"`, `length="32"` |
| `0x0001` | `CurrentPhase` | `CURRENT_PHASE` | `int8u` | `isNullable="true"` |
| `0x0002` | `CountdownTime` | `COUNTDOWN_TIME` | `elapsed_s` | `max="259200"`, `isNullable="true"`, `optional="true"`, `optionalConform` |
| `0x0003` | `OperationalStateList` | `OPERATIONAL_STATE_LIST` | `array`, 항목 타입 `OperationalStateStruct` | 추가 제약 표기 없음 |
| `0x0004` | `OperationalState` | `OPERATIONAL_STATE` | `enum8` | 추가 제약 표기 없음 |
| `0x0005` | `OperationalError` | `OPERATIONAL_ERROR` | `ErrorStateStruct` | 추가 제약 표기 없음 |

`OperationalState`는 SDK XML에서 `enum8`로 선언된다. 관련 주석은 기반 클러스터와 파생 클러스터의 값을 모두 허용하기 위한 타입 선택이라고 설명한다.

### 명령

| 코드 | 이름 | source | 응답 | 정의 및 동작 |
|---|---|---|---|---|
| `0x00` | `Pause` | `client` | `OperationalCommandResponse` | 원격 일시 정지를 지원하는 장치는 지원해야 함. `Resume`을 지원하면 필수이며, 그렇지 않으면 선택 |
| `0x03` | `Resume` | `client` | `OperationalCommandResponse` | 원격 재개를 지원하는 장치는 지원해야 함. `Pause`를 지원하면 필수이며, 그렇지 않으면 선택 |
| `0x04` | `OperationalCommandResponse` | `server` | — | `optional="true"`, `disableDefaultResponse="true"` |
| `0x80` | `GoHome` | `client` | `OperationalCommandResponse` | 선택 지원. 현재 상태에서 가능하면 충전 도크 탐색을 시작해야 함 |

`Stop`의 `0x01`과 `Start`의 `0x02`는 폐기 예정이라는 주석만 있으며, SDK XML에 해당 명령 요소는 없다.

#### OperationalCommandResponse

| fieldId | 인자 | 타입 |
|---|---|---|
| `0` | `CommandResponseState` | `ErrorStateStruct` |

지원 조건은 원문에서 다음과 같이 표현된다.

- 설명문: 이 클러스터의 다른 명령 중 하나라도 지원하여 `AcceptedCommandList`에 나열되면 `OperationalCommandResponse`를 지원해야 한다.
- `mandatoryConform`의 `orTerm`: `Pause`, `Stop`, `Start`, `Resume`을 나열한다. 이 목록에는 `GoHome`이 없다.

### 이벤트

두 이벤트 모두 `side="server"`이다.

| 코드 | 이름 | priority | 선택성 | 발생 조건 |
|---|---|---|---|---|
| `0x00` | `OperationalError` | `critical` | 선택 표기 없음 | 보고 가능한 오류 조건이 감지되면 발생 |
| `0x01` | `OperationCompletion` | `info` | `optional="true"`, `optionalConform` | 성공 여부와 관계없이 전체 동작이 끝나면 발생하는 것이 권장됨 |

#### OperationalError 필드

| id / fieldId | 이름 | 타입 |
|---|---|---|
| `0` / `0` | `ErrorState` | `ErrorStateStruct` |

#### OperationCompletion 필드

| id / fieldId | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` / `0` | `CompletionErrorCode` | `enum8` | 추가 제약 표기 없음 |
| `1` / `1` | `TotalOperationalTime` | `elapsed_s` | `isNullable="true"`, `optional="true"` |
| `2` / `2` | `PausedTime` | `elapsed_s` | `isNullable="true"`, `optional="true"` |

## 관련 문서

### Operational State 공통 안내

출처: `src/app/clusters/operational-state-server/README.md`

#### 구조와 사용 방식

- 기반 `Operational State` 클러스터의 ID는 `0x0060`이다.
- `OperationalState::OperationalStateCluster`는 `DefaultServerCluster`를 확장하며, 코드 주도 데이터 모델 패턴을 따른다.
- 이 기반 클러스터는 `RVC Operational State`, `Oven Cavity Operational State`를 포함한 파생 클러스터의 공통 로직을 제공한다.
- 각 파생 클러스터의 네임스페이스에 있는 `Instance`는 기반 `OperationalStateCluster`를 감싸는 레거시 호환 래퍼이다. 신규 코드는 `OperationalStateCluster`를 직접 사용하도록 안내한다.
- 애플리케이션은 `OperationalState::Delegate`를 상속하고 가상 콜백 메서드를 구현한 뒤, 해당 delegate를 `Instance` 또는 클러스터 클래스에 전달해야 한다.

#### 초기화와 종료

서버 측 초기화·종료에는 다음 훅을 사용한다.

- `Matter<ClusterName>ClusterInitCallback`
- `Matter<ClusterName>ClusterShutdownCallback`

README의 기반 클러스터 예시는 다음 순서로 초기화한다.

1. `MatterOperationalStateClusterInitCallback`에서 delegate와 `OperationalState::Instance`를 생성한다.
2. `SetOperationalState(to_underlying(OperationalState::OperationalStateEnum::kStopped))`로 초기 상태를 설정한다.
3. `Init()`을 호출한다.
4. `MatterOperationalStateClusterShutdownCallback`에서 instance와 delegate를 삭제하고 포인터를 `nullptr`로 설정한다.

`CodegenIntegration.cpp`는 이 함수들의 weak no-op stub을 제공하므로, 사용자 정의 상태가 필요하지 않은 애플리케이션도 별도 정의 없이 링크할 수 있다.

**주의 사항:**

- `Server` 한정자가 없는 `emberAf<ClusterName>ClusterInitCallback`, `emberAf<ClusterName>ClusterShutdownCallback`은 클라이언트 측 훅이다. 서버 클러스터 초기화에 사용하면 안 된다.
- 이 클러스터들에는 ZAP accessor 함수가 없다. 속성 접근에는 instance의 `Set…`, `Get…` 메서드를 사용한다.

#### 새로운 파생 클러스터 추가 절차

README는 스펙에 새 파생 클러스터가 정의된 이후의 절차를 다음과 같이 안내한다.

1. 클러스터 XML을 `src/app/zap-templates/zcl/data-model/chip/`에 추가한다.
2. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters`에 클러스터를 추가한다.
3. `scripts/tools/zap/zap_regen_all.py`로 ZAP 및 `py_matter_idl` 출력을 재생성한다.
4. `RvcOperationalStateCluster`를 참고하여 `OperationalStateCluster`를 상속하고, `RegisteredServerCluster`로 등록한다.
5. `all-clusters-app` 예시에 새 클러스터를 추가한다.

## 관련 페이지

**사용 기기**

- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
