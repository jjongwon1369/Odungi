---
entity: AlarmBase
ids: []
source_paths: ['src/app/clusters/alarm-base-server/Delegate.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp', 'src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h', 'data_model/1.7/clusters/AlarmBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
---

# AlarmBase

## 개요

`AlarmBase`는 알람 비트맵, 활성 상태, 래치 및 알람 초기화를 다루는 기반 클러스터이다.

- 스펙의 이름은 `Alarm Base Cluster`이며, revision은 `2`이다.
- `AlarmBaseCluster`는 `DefaultServerCluster`를 상속하는 코드 기반 구현으로, `DishwasherAlarm`, `RefrigeratorAlarm` 등의 파생 구현을 위한 기반을 제공한다.
- 애플리케이션은 `Delegate`를 통해 명령에 따른 장치 동작을 승인하거나 거부할 수 있다.
- 상태 변경에 따른 이벤트 처리는 파생 클래스가 `SendNotifyEvent()`로 구현한다.

## 스펙

출처: `data_model/1.7/clusters/AlarmBase.xml`

### 분류 및 revision

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Alarm Base Cluster` |
| `clusterId` 이름 | `Alarm Base` |
| revision | `2` |
| `hierarchy` | `base` |
| `role` | `application` |
| `picsCode` | `ALARM` |
| `scope` | `Endpoint` |

원문에는 숫자 클러스터 ID가 지정되어 있지 않다.

| revision | 변경 내용 |
|---|---|
| `1` | 최초 revision |
| `2` | 이벤트 필드 ID를 SDK와 일치하도록 변경 |

### 기능 및 데이터 타입

| bit | code | name | 지원 조건 | 설명 |
|---|---|---|---|---|
| `0` | `RESET` | `Reset` | 선택 | 알람 초기화 지원 |

`AlarmBitmap`은 비트맵 타입으로 선언되어 있다. 개별 알람 비트는 제공된 XML에 정의되어 있지 않다.

### 속성

모든 속성의 타입은 `AlarmBitmap`이며, 읽기 권한은 `view`이다. 쓰기 접근은 선언되어 있지 않다.

| ID | 이름 | 지원 조건 | `persistence` |
|---|---|---|---|
| `0x0000` | `Mask` | 필수 | 별도 지정 없음 |
| `0x0001` | `Latch` | `RESET` 지원 시 필수 | `fixed` |
| `0x0002` | `State` | 필수 | 별도 지정 없음 |
| `0x0003` | `Supported` | 필수 | `fixed` |

### 명령

두 명령 모두 `direction="commandToServer"`, `response="Y"`이며, 호출 권한은 `operate`이다.

| ID | 이름 | 지원 조건 | 필수 필드 |
|---|---|---|---|
| `0x00` | `Reset` | `RESET` 지원 시 필수 | ID `0`: `Alarms`, 타입 `AlarmBitmap` |
| `0x01` | `ModifyEnabledAlarms` | 선택 | ID `0`: `Mask`, 타입 `AlarmBitmap` |

### 이벤트

`Notify`는 필수 이벤트이며, ID는 `0x00`, 우선순위는 `info`, 읽기 권한은 `view`이다.

| 필드 ID | 이름 | 타입 | 지원 조건 |
|---|---|---|---|
| `0` | `Active` | `AlarmBitmap` | 필수 |
| `1` | `Inactive` | `AlarmBitmap` | 필수 |
| `2` | `State` | `AlarmBitmap` | 필수 |
| `3` | `Mask` | `AlarmBitmap` | 필수 |

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/alarm-base-server/Delegate.h` | 명령 처리 시 호출하는 애플리케이션 훅 |
| `src/app/clusters/alarm-base-server/AlarmBaseCluster.h` | `AlarmBaseCluster`, `Config`, 애플리케이션 API 선언 |
| `src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp` | 속성 읽기, 명령 처리, 상태 변경 구현 |
| `src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h` | 공통 타입, 별칭, 속성 메타데이터 정의 |

### 공통 타입과 별칭

`chip::app::Clusters::AlarmBase`에서 다음 타입을 정의한다.

- `ClusterEntry`: `ClusterId id`와 `uint32_t revision`을 보관한다.
- `AlarmBitmap`: 기반 타입이 `uint32_t`인 열거형이며, `kNone = 0`을 정의한다.
- `AlarmMap`: `BitMask<AlarmBitmap>`의 별칭이다.

파생 클러스터의 정의 중 다음 항목을 재사용한다.

| 항목 | 원본 |
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

`AlarmBaseCluster`는 `chip::app::Clusters`에 정의되며, 생성자는 다음 인자를 받는다.

```cpp
AlarmBaseCluster(EndpointId endpointId, AlarmBase::ClusterEntry cluster, const Config & config);
```

| `Config` 필드 | 타입 | 기본값 |
|---|---|---|
| `delegate` | `AlarmBase::Delegate &` | 기본값 없음 |
| `feature` | `BitMask<AlarmBase::Feature>` | `{}` |
| `supported` | `AlarmBase::AlarmMap` | `{}` |
| `latch` | `AlarmBase::AlarmMap` | `{}` |
| `supportsModifyEnabledAlarms` | `bool` | `false` |

생성자는 `endpointId`와 `cluster.id`를 `DefaultServerCluster`에 전달하고, `cluster.revision`을 `mClusterRevision`에 저장한다. `mMask`와 `mState`는 `{}`로 초기화된다.

### 속성 읽기 및 목록

`ReadAttribute()`는 다음 속성을 인코딩한다.

| 속성 | 반환 대상 |
|---|---|
| `ClusterRevision` | `mClusterRevision` |
| `FeatureMap` | `mFeature` |
| `Mask` | `mMask` |
| `Latch` | `mLatch` |
| `State` | `mState` |
| `Supported` | `mSupported` |

그 외에는 `Status::UnsupportedAttribute`를 반환한다.

`Attributes()`는 `AttributeListBuilder`를 사용하여 `kMandatoryMetadata`를 추가하고, `Feature::kReset`이 설정된 경우에만 `Latch::kMetadataEntry`를 추가한다. `ReadAttribute()`의 `Latch` 분기 자체에는 이 기능 조건 검사가 없다.

### 애플리케이션 API

| 함수 | 동작 |
|---|---|
| `GetMask()` | `mMask` 반환 |
| `GetState()` | `mState` 반환 |
| `GetSupported()` | `mSupported` 반환 |
| `GetLatch()` | `mLatch` 반환 |
| `GetFeatures()` | `mFeature` 반환 |
| `SetMask()` | 활성화할 알람 비트맵 설정 및 필요 시 상태 조정 |
| `SetState()` | 지원 범위, 마스크, 래치를 고려하여 상태 설정 |
| `ResetLatchedAlarms()` | 요청된 알람 비트를 상태에서 제거 |

이 API의 `SetMask()`와 `ResetLatchedAlarms()`는 `Delegate`를 직접 호출하지 않는다. `Delegate` 호출은 명령 처리 경로에 있다.

### `SetMask()`

1. `mask`의 모든 비트가 `mSupported`에 포함되는지 검사한다. 포함되지 않으면 `Status::Failure`를 반환한다.
2. `SetAttributeValue(mMask, mask, Mask::Id)`로 값을 갱신한다. 변경이 없으면 `Status::Success`를 반환한다.
3. 현재 상태에 새 마스크 밖의 비트가 있으면 `state = mask & state`로 제한한다.
4. 제한한 상태는 `SetStateIgnoringLatch()`로 반영한다.

따라서 마스크 조정으로 제거되는 활성 비트는 `Latch`에 의해 유지되지 않는다.

### 상태 변경과 이벤트 훅

`SetState()`는 `SetStateInternal(newState, false)`를 호출한다. 보호된 함수인 `SetStateIgnoringLatch()`는 `SetStateInternal(newState, true)`를 호출한다.

`SetStateInternal()`의 처리 순서는 다음과 같다.

1. 요청한 상태의 모든 비트가 `mSupported`와 `mMask`에 포함되는지 검사한다. 조건을 만족하지 않으면 `Status::Failure`를 반환한다.
2. `ignoreLatchState`가 `false`이고 `Feature::kReset`이 설정되어 있으면, `GetLatch() & currentState`의 비트를 새 상태에 유지한다.
3. `SetAttributeValue(mState, finalNewState, State::Id)`로 상태를 갱신한다. 변경이 없으면 `Status::Success`를 반환하며 이벤트 훅을 호출하지 않는다.
4. 변경이 있으면 새로 활성화된 비트를 `becameActive`, 비활성화된 비트를 `becameInactive`로 계산한다.
5. `SendNotifyEvent(becameActive, becameInactive, finalNewState, mMask)`를 호출한다.

`SendNotifyEvent()`는 순수 가상 함수이므로 실제 이벤트 전송은 파생 클래스가 구현해야 한다.

`SetStateIgnoringLatch()`는 마스크 조정, 초기화 및 통합 초기 설정처럼 `Latch`가 상태 갱신을 막아서는 안 되는 경우를 위한 함수이다. 헤더 주석은 애플리케이션에서 `SetState()` 또는 `ResetLatchedAlarms()`를 사용하도록 안내한다.

### `ResetLatchedAlarms()`

- 요청된 `alarms`가 `mSupported` 범위를 벗어나면 `Status::Failure`를 반환한다.
- 현재 상태에서 `alarms`의 비트를 제거한다.
- 결과를 `SetStateIgnoringLatch()`로 반영한다.

구현은 제거 대상을 `mLatch`와 교집합으로 제한하지 않고, 요청된 지원 비트를 현재 상태에서 제거한다.

### 명령 목록과 디스패치

`AcceptedCommands()`는 다음 조건에 따라 명령을 추가한다.

| 조건 | 추가하는 명령 |
|---|---|
| `mFeature.Has(Feature::kReset)` | `Commands::Reset::kMetadataEntry` |
| `mSupportsModifyEnabledAlarms` | `Commands::ModifyEnabledAlarms::kMetadataEntry` |

`InvokeCommand()`는 명령을 디코딩하여 다음과 같이 전달한다.

| 명령 ID | 디코딩 타입 | 처리 |
|---|---|---|
| `Commands::Reset::Id` | `Commands::Reset::DecodableType` | `HandleReset(AlarmMap(data.alarms.Raw()))` |
| `Commands::ModifyEnabledAlarms::Id` | `Commands::ModifyEnabledAlarms::DecodableType` | `HandleModifyEnabledAlarms(AlarmMap(data.mask.Raw()))` |

디코딩 오류는 반환되며, 그 외의 명령 ID에는 `Status::UnsupportedCommand`를 반환한다.

`InvokeCommand()`와 두 처리 함수에는 `Feature::kReset` 또는 `mSupportsModifyEnabledAlarms`를 다시 확인하는 분기가 없다.

### `Delegate`와 명령 처리 결과

`Delegate`는 속성 갱신 전에 장치 측 동작을 수행하거나 요청을 거부하기 위한 훅이다. 기본 구현은 두 함수 모두 `true`를 반환한다.

| 훅 | 호출 시점 | 용도 |
|---|---|---|
| `ModifyEnabledAlarms(AlarmMap mask)` | `Mask` 갱신 전 | 요청한 알람 활성화·억제 동작을 장치에 적용하거나 거부 |
| `ResetAlarms(AlarmMap alarms)` | `State` 갱신 전 | 물리적·논리적 알람 상태 해제를 수행하거나 거부 |

명령 처리 순서는 다음과 같다.

| 처리 함수 | 지원하지 않는 비트 포함 | 훅의 반환값이 `false` | 훅의 반환값이 `true` |
|---|---|---|---|
| `HandleReset()` | `Status::InvalidCommand` | `Status::Failure` | `ResetLatchedAlarms(alarms)` |
| `HandleModifyEnabledAlarms()` | `Status::InvalidCommand` | `Status::Failure` | `SetMask(mask)` |

지원 범위 검증은 훅 호출보다 먼저 수행한다. 훅이 요청을 거부하면 클러스터는 해당 명령에 따른 속성 갱신을 수행하지 않는다.

주석은 물리적 알람, 경보 표시 장치 또는 래치된 하드웨어 상태가 있는 제품에서 이러한 훅으로 장치 동작을 먼저 처리하도록 안내한다. Matter 속성 모델만 사용하는 구현은 기본 동작처럼 무조건 `true`를 반환할 수 있다.