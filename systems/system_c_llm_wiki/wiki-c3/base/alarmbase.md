---
entity: AlarmBase
ids: []
source_paths: ['data_model/1.7/clusters/AlarmBase.xml', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.h', 'src/app/clusters/alarm-base-server/Delegate.h', 'src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# AlarmBase

## 개요

`AlarmBase`는 알람 클러스터의 기반 모델이다. 스펙의 이름은 `Alarm Base Cluster`이며, 구현 클래스 `AlarmBaseCluster`는 `DefaultServerCluster`를 상속하는 코드 기반 구현이다.

- `Mask`, `State`, `Supported`를 통해 알람 마스크, 상태, 지원 비트를 관리한다.
- 선택 기능 `RESET`을 지원하면 `Latch`와 `Reset`을 제공한다.
- `AlarmBaseCluster`는 `DishwasherAlarm`, `RefrigeratorAlarm` 등의 파생 구현을 위한 기반 클래스다.
- 상태 변경 시 호출되는 `SendNotifyEvent`는 순수 가상 함수로, 파생 클래스에서 구현해야 한다.

## 스펙

출처: `data_model/1.7/clusters/AlarmBase.xml`

### 분류 및 리비전

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Alarm Base Cluster` |
| `clusterId` 이름 | `Alarm Base` |
| 숫자 클러스터 ID | 입력 XML에 지정되지 않음 |
| 리비전 | `2` |
| `hierarchy` | `base` |
| `role` | `application` |
| `picsCode` | `ALARM` |
| `scope` | `Endpoint` |

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 이벤트 필드 ID를 SDK와 일치하도록 변경 |

### 기능 및 데이터 타입

| 비트 | 코드 | 이름 | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `RESET` | `Reset` | 선택 | 알람 리셋 지원 |

`AlarmBitmap`은 비트맵 타입으로 선언되어 있다. 기반 XML에는 개별 비트 정의가 없다.

### 속성

모든 속성의 타입은 `AlarmBitmap`이며, 읽기 권한은 `view`다. 쓰기 접근은 선언되어 있지 않다.

| ID | 이름 | 적합성 | `persistence` |
|---|---|---|---|
| `0x0000` | `Mask` | 필수 | 지정되지 않음 |
| `0x0001` | `Latch` | `RESET` 지원 시 필수 | `fixed` |
| `0x0002` | `State` | 필수 | 지정되지 않음 |
| `0x0003` | `Supported` | 필수 | `fixed` |

### 명령

두 명령 모두 `direction="commandToServer"`, `response="Y"`이며, 호출 권한은 `operate`다.

| ID | 이름 | 적합성 | 필드 ID | 필드 이름 | 타입 | 필드 적합성 |
|---|---|---|---|---|---|---|
| `0x00` | `Reset` | `RESET` 지원 시 필수 | `0` | `Alarms` | `AlarmBitmap` | 필수 |
| `0x01` | `ModifyEnabledAlarms` | 선택 | `0` | `Mask` | `AlarmBitmap` | 필수 |

### 이벤트

`Notify`는 ID `0x00`의 필수 이벤트이며, 우선순위는 `info`, 읽기 권한은 `view`다.

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `Active` | `AlarmBitmap` | 필수 |
| `1` | `Inactive` | `AlarmBitmap` | 필수 |
| `2` | `State` | `AlarmBitmap` | 필수 |
| `3` | `Mask` | `AlarmBitmap` | 필수 |

## 구현

### 소스 파일

| 경로 | 내용 |
|---|---|
| `src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp` | 속성 읽기, 상태 변경, 명령 처리 |
| `src/app/clusters/alarm-base-server/AlarmBaseCluster.h` | `AlarmBaseCluster`, `Config`, 애플리케이션 API |
| `src/app/clusters/alarm-base-server/Delegate.h` | 명령 처리 전 애플리케이션 훅 |
| `src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h` | 공통 타입, 별칭, 속성 메타데이터 |

### 공통 타입과 메타데이터

`chip::app::Clusters::AlarmBase`에 다음 타입이 정의된다.

- `ClusterEntry`: `ClusterId id`와 `uint32_t revision`을 보관한다.
- `AlarmBitmap`: 기반 타입이 `uint32_t`인 열거형으로, `kNone = 0`을 정의한다.
- `AlarmMap`: `BitMask<AlarmBitmap>`의 별칭이다.

공통 정의는 `DishwasherAlarm`의 생성 정의를 재사용한다.

| 이름 | 참조 대상 |
|---|---|
| `Feature` | `DishwasherAlarm::Feature` |
| `Commands` | `DishwasherAlarm::Commands` |
| `Events` | `DishwasherAlarm::Events` |
| `Mask` | `DishwasherAlarm::Attributes::Mask` |
| `Latch` | `DishwasherAlarm::Attributes::Latch` |
| `State` | `DishwasherAlarm::Attributes::State` |
| `Supported` | `DishwasherAlarm::Attributes::Supported` |

`GeneratedCommandList`, `AcceptedCommandList`, `AttributeList`, `FeatureMap`, `ClusterRevision`도 각각 `DishwasherAlarm::Attributes`의 동일 이름을 참조한다.

`kMandatoryMetadata`에는 `Mask::kMetadataEntry`, `State::kMetadataEntry`, `Supported::kMetadataEntry`가 포함된다.

### 생성 및 설정

생성자:

```cpp
AlarmBaseCluster(EndpointId endpointId, AlarmBase::ClusterEntry cluster, const Config & config);
```

`DefaultServerCluster`에는 `endpointId`와 `cluster.id`를 전달하고, 리비전은 `cluster.revision`에서 가져온다.

| `Config` 멤버 | 타입 | 기본값 |
|---|---|---|
| `delegate` | `AlarmBase::Delegate &` | 기본값 없음 |
| `feature` | `BitMask<AlarmBase::Feature>` | `{}` |
| `supported` | `AlarmBase::AlarmMap` | `{}` |
| `latch` | `AlarmBase::AlarmMap` | `{}` |
| `supportsModifyEnabledAlarms` | `bool` | `false` |

`mMask`와 `mState`는 `{}`로 초기화된다. `mFeature`, `mClusterRevision`, `mSupportsModifyEnabledAlarms`, `mLatch`, `mSupported`는 생성 후 변경되지 않는 멤버다.

### 속성 읽기와 지원 목록

- `ReadAttribute`는 `ClusterRevision`, `FeatureMap`, `Mask`, `Latch`, `State`, `Supported`를 인코딩한다. 그 외에는 `Status::UnsupportedAttribute`를 반환한다.
- `Attributes`는 `kMandatoryMetadata`를 추가하고, `Feature::kReset`이 설정된 경우에만 `Latch::kMetadataEntry`를 추가한다.
- `AcceptedCommands`는 다음 조건에 따라 명령 메타데이터를 추가한다.
  - `Feature::kReset` 설정: `Commands::Reset::kMetadataEntry`
  - `mSupportsModifyEnabledAlarms` 설정: `Commands::ModifyEnabledAlarms::kMetadataEntry`

### 애플리케이션 API

조회 함수는 `GetMask`, `GetState`, `GetSupported`, `GetLatch`, `GetFeatures`다.

#### `SetMask`

1. 요청 비트가 모두 `mSupported`에 포함되는지 확인한다. 아니면 `Status::Failure`를 반환한다.
2. `SetAttributeValue`로 `mMask`를 갱신한다. 변경이 없으면 `Status::Success`로 종료한다.
3. 기존 `mState`에 새 마스크가 허용하지 않는 비트가 있으면 `mask & state`를 계산하여 `SetStateIgnoringLatch`를 호출한다.

따라서 마스크에서 제외된 활성 비트는 `Latch`와 관계없이 해제된다. `Mask`만 바뀌고 `State`는 바뀌지 않으면 이 경로에서 `SendNotifyEvent`를 호출하지 않는다.

#### `SetState`와 `SetStateInternal`

`SetState`는 `SetStateInternal(newState, false)`를 호출한다.

`SetStateInternal`의 처리 순서는 다음과 같다.

1. 요청 비트가 모두 `mSupported`와 `mMask`에 포함되는지 검사한다. 위반하면 `Status::Failure`를 반환한다.
2. `ignoreLatchState`가 `false`이고 `Feature::kReset`이 설정되어 있으면, 기존 상태 중 `GetLatch() & currentState`에 해당하는 비트를 유지한다.
3. `SetAttributeValue`로 `mState`를 갱신한다. 변경이 없으면 `Status::Success`로 종료한다.
4. 새로 활성화된 비트와 비활성화된 비트를 계산한다.
5. `SendNotifyEvent(becameActive, becameInactive, finalNewState, mMask)`를 호출한다.

#### `ResetLatchedAlarms`

- 요청 비트가 모두 `mSupported`에 포함되지 않으면 `Status::Failure`를 반환한다.
- 현재 상태에서 요청 비트를 지운 뒤 `SetStateIgnoringLatch`를 호출한다.
- 제공된 구현은 요청 비트를 `mLatch`에 포함된 비트로 제한하지 않는다.

`SetStateIgnoringLatch`는 보호된 함수이며, `SetStateInternal(newState, true)`를 호출한다. 주석에서는 마스크 조정, 리셋, 통합 초기화에 사용하며, 애플리케이션은 대신 `SetState` 또는 `ResetLatchedAlarms`를 사용하도록 안내한다.

### 명령 처리와 `Delegate`

`InvokeCommand`는 명령을 디코딩하여 다음 처리 함수로 전달한다.

| 명령 | 디코딩 타입 | 전달 |
|---|---|---|
| `Reset` | `Commands::Reset::DecodableType` | `HandleReset(AlarmMap(data.alarms.Raw()))` |
| `ModifyEnabledAlarms` | `Commands::ModifyEnabledAlarms::DecodableType` | `HandleModifyEnabledAlarms(AlarmMap(data.mask.Raw()))` |

디코딩 오류는 반환되며, 알 수 없는 명령에는 `Status::UnsupportedCommand`를 반환한다.

| 처리 함수 | 지원 비트 검증 실패 | 애플리케이션 훅 | 훅이 `false`인 경우 | 훅이 `true`인 경우 |
|---|---|---|---|---|
| `HandleReset` | `Status::InvalidCommand` | `mDelegate.ResetAlarms(alarms)` | `Status::Failure` | `ResetLatchedAlarms(alarms)` |
| `HandleModifyEnabledAlarms` | `Status::InvalidCommand` | `mDelegate.ModifyEnabledAlarms(mask)` | `Status::Failure` | `SetMask(mask)` |

`Delegate`의 두 가상 함수는 기본적으로 `true`를 반환한다.

```cpp
virtual bool ModifyEnabledAlarms(AlarmMap mask) { return true; }
virtual bool ResetAlarms(AlarmMap alarms) { return true; }
```

훅은 클러스터가 Matter 속성을 갱신하기 전에 호출된다. 애플리케이션은 하드웨어 알람, 표시 장치, 래치 상태 등의 변경을 먼저 수행하거나 요청을 거절할 수 있다. 훅이 `false`를 반환하면 클러스터는 후속 속성 갱신을 수행하지 않는다.

`Delegate` 주석에서는 선택적 애플리케이션 훅으로 설명하지만, `Config`의 `delegate` 멤버 자체는 참조이므로 생성 시 제공해야 한다. 직접 호출하는 `SetMask`, `SetState`, `ResetLatchedAlarms`에는 `Delegate` 호출이 없다.

### 이벤트 확장 지점

```cpp
virtual void SendNotifyEvent(AlarmBase::AlarmMap becameActive,
                             AlarmBase::AlarmMap becameInactive,
                             AlarmBase::AlarmMap newState,
                             AlarmBase::AlarmMap mask) = 0;
```

`AlarmBaseCluster`는 상태가 실제로 변경될 때 이 함수를 호출한다. 제공된 코드에는 파생 클래스의 이벤트 전송 구현은 포함되어 있지 않다.