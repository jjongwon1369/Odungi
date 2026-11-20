---
entity: AlarmBase
ids: []
source_paths: ['data_model/1.7/clusters/AlarmBase.xml', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.h', 'src/app/clusters/alarm-base-server/Delegate.h', 'src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# AlarmBase

## 개요

`AlarmBase`는 알람 속성, 명령 및 이벤트를 정의하는 기본 클러스터이다. `AlarmBaseCluster`는 `DefaultServerCluster`를 상속하는 코드 기반 구현으로, `DishwasherAlarm`, `RefrigeratorAlarm` 등의 파생 클러스터를 위한 기본 구현을 제공한다.

- 스펙 이름: `Alarm Base Cluster`
- 스펙 revision: `2`
- 분류: hierarchy=`base`, role=`application`
- PICS 코드: `ALARM`
- 범위: `Endpoint`
- 선택 기능: 알람 초기화를 지원하는 `Reset` (`RESET`)
- 제공된 XML의 `clusterId`에는 이름 `Alarm Base`만 있으며 숫자 ID는 지정되어 있지 않다.

## 스펙

출처: `data_model/1.7/clusters/AlarmBase.xml`

### 개정 이력

| revision | 변경 사항 |
|---|---|
| `1` | 최초 개정 |
| `2` | 이벤트 필드 ID를 SDK와 일치하도록 변경 |

### 기능 및 데이터 타입

| bit | code | name | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `RESET` | `Reset` | 선택 | 알람 초기화 지원 |

`AlarmBitmap`은 비트맵 타입으로 선언되어 있다. 제공된 XML에는 개별 비트 정의가 없다.

### 속성

모든 속성의 타입은 `AlarmBitmap`이며, 읽기 접근 권한은 `view`이다.

| ID | 이름 | 적합성 | persistence |
|---|---|---|---|
| `0x0000` | `Mask` | 필수 | 명시되지 않음 |
| `0x0001` | `Latch` | `RESET` 지원 시 필수 | `fixed` |
| `0x0002` | `State` | 필수 | 명시되지 않음 |
| `0x0003` | `Supported` | 필수 | `fixed` |

### 명령

두 명령 모두 direction=`commandToServer`, invokePrivilege=`operate`, response=`Y`로 선언되어 있다.

| ID | 이름 | 적합성 | 필수 필드 |
|---|---|---|---|
| `0x00` | `Reset` | `RESET` 지원 시 필수 | ID `0`: `Alarms` (`AlarmBitmap`) |
| `0x01` | `ModifyEnabledAlarms` | 선택 | ID `0`: `Mask` (`AlarmBitmap`) |

### 이벤트

`Notify`는 필수 이벤트이며 ID는 `0x00`, priority는 `info`, readPrivilege는 `view`이다.

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `Active` | `AlarmBitmap` | 필수 |
| `1` | `Inactive` | `AlarmBitmap` | 필수 |
| `2` | `State` | `AlarmBitmap` | 필수 |
| `3` | `Mask` | `AlarmBitmap` | 필수 |

## 구현

### 소스 구성

| 파일 | 주요 내용 |
|---|---|
| `src/app/clusters/alarm-base-server/AlarmBaseCluster.h` | `AlarmBaseCluster`, `Config`, 애플리케이션 API 및 이벤트 훅 선언 |
| `src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp` | 속성 읽기, 상태 갱신, 명령 처리 |
| `src/app/clusters/alarm-base-server/Delegate.h` | 명령 처리 전 장치 동작을 수행하거나 거부하는 `Delegate` |
| `src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h` | 공통 타입, `DishwasherAlarm` 정의의 별칭 및 속성 메타데이터 |

### 공통 타입과 정의 재사용

`chip::app::Clusters::AlarmBase`에 다음 타입이 정의되어 있다.

| 식별자 | 정의 |
|---|---|
| `ClusterEntry` | `ClusterId id`, `uint32_t revision`을 보관 |
| `AlarmBitmap` | 기반 타입이 `uint32_t`인 열거형. `kNone = 0` 정의 |
| `AlarmMap` | `BitMask<AlarmBitmap>`의 별칭 |
| `Feature` | `DishwasherAlarm::Feature`의 별칭 |
| `Commands` | `DishwasherAlarm::Commands`의 네임스페이스 별칭 |
| `Events` | `DishwasherAlarm::Events`의 네임스페이스 별칭 |

`Attributes`에서는 다음 `DishwasherAlarm::Attributes` 정의를 같은 이름의 별칭으로 사용한다.

- `Mask`, `Latch`, `State`, `Supported`
- `GeneratedCommandList`, `AcceptedCommandList`, `AttributeList`
- `FeatureMap`, `ClusterRevision`

`kMandatoryMetadata`는 `Mask::kMetadataEntry`, `State::kMetadataEntry`, `Supported::kMetadataEntry`로 구성된다.

### 생성 및 설정

`AlarmBaseCluster`는 `chip::app::Clusters`에 정의되어 있으며, 생성자는 `endpointId`, `cluster`, `config`를 받는다.

- `DefaultServerCluster`에는 `{ endpointId, cluster.id }`를 전달한다.
- `mClusterRevision`은 `cluster.revision`으로 초기화한다.
- 기능, 명령 지원 여부, delegate, latch 및 지원 비트맵은 `Config`에서 가져온다.
- `mMask`와 `mState`는 `{}`로 초기화된다.

| `Config` 필드 | 타입 | 기본값 |
|---|---|---|
| `delegate` | `AlarmBase::Delegate &` | 기본값 없음 |
| `feature` | `BitMask<AlarmBase::Feature>` | `{}` |
| `supported` | `AlarmBase::AlarmMap` | `{}` |
| `latch` | `AlarmBase::AlarmMap` | `{}` |
| `supportsModifyEnabledAlarms` | `bool` | `false` |

### 애플리케이션 API

| 함수 | 동작 |
|---|---|
| `GetMask()` | `mMask` 반환 |
| `GetState()` | `mState` 반환 |
| `GetSupported()` | `mSupported` 반환 |
| `GetLatch()` | `mLatch` 반환 |
| `GetFeatures()` | `mFeature` 반환 |
| `SetMask()` | 지원 비트 검증 후 `Mask` 갱신 및 필요 시 `State` 조정 |
| `SetState()` | latch 유지 규칙을 적용하여 상태 갱신 |
| `ResetLatchedAlarms()` | 지정된 비트를 상태에서 제거 |

`SetStateIgnoringLatch()`는 protected 함수로, mask 조정, 초기화 및 통합 초기 설정처럼 `Latch`가 상태 갱신을 막아서는 안 되는 경우에 사용한다. 헤더 주석은 애플리케이션에서 `SetState()` 또는 `ResetLatchedAlarms()`를 사용하도록 안내한다.

### `Mask` 갱신

`SetMask()`의 처리 순서는 다음과 같다.

1. `mSupported.HasAll(mask)`를 검사한다. 지원하지 않는 비트가 있으면 `Status::Failure`를 반환한다.
2. `SetAttributeValue(mMask, mask, Mask::Id)`로 `Mask`를 갱신한다. 변경이 없으면 `Status::Success`를 반환한다.
3. 현재 `State`에 새 `Mask`가 허용하지 않는 비트가 있으면 `mask & state`로 상태를 제한한다.
4. 제한된 상태는 `SetStateIgnoringLatch()`로 적용한다.

따라서 새 `Mask`에서 제외된 활성 비트는 `Latch`와 관계없이 제거된다. `Mask`만 바뀌고 `State`가 바뀌지 않는 경우에는 이 경로에서 `SendNotifyEvent()`를 호출하지 않는다.

### 상태 갱신과 latch 처리

`SetState()`는 `SetStateInternal(newState, false)`를 호출하고, `SetStateIgnoringLatch()`는 `SetStateInternal(newState, true)`를 호출한다.

`SetStateInternal()`은 다음 순서로 처리한다.

1. 요청 상태가 `mSupported`와 `mMask`에 모두 포함되는지 검사한다. 어느 하나라도 만족하지 않으면 `Status::Failure`를 반환한다.
2. `ignoreLatchState`가 `false`이고 `Feature::kReset`이 활성화되어 있으면, `GetLatch() & currentState`의 비트를 새 상태에 유지한다.
3. `SetAttributeValue(mState, finalNewState, State::Id)`로 상태를 갱신한다. 변경이 없으면 `Status::Success`를 반환한다.
4. 새로 활성화된 비트와 비활성화된 비트를 계산한다.
5. `SendNotifyEvent(becameActive, becameInactive, finalNewState, mMask)`를 호출한다.

`ResetLatchedAlarms()`는 요청 비트가 `mSupported`에 포함되는지 검사한 뒤, 현재 상태에서 해당 비트를 제거하고 `SetStateIgnoringLatch()`를 호출한다. 구현에는 요청 비트를 `Latch`에 포함된 비트로 제한하는 별도 검사가 없다.

### 속성 읽기 및 노출

`ReadAttribute()`는 다음 속성을 인코딩한다.

- `ClusterRevision::Id` → `mClusterRevision`
- `FeatureMap::Id` → `mFeature`
- `Mask::Id` → `mMask`
- `Latch::Id` → `mLatch`
- `State::Id` → `mState`
- `Supported::Id` → `mSupported`

나머지 ID에는 `Status::UnsupportedAttribute`를 반환한다.

`Attributes()`는 `AttributeListBuilder`를 사용하여 `kMandatoryMetadata`를 추가한다. `Latch::kMetadataEntry`는 `mFeature.Has(Feature::kReset)`이 참인 경우에만 추가한다.

### 명령 노출과 처리

`AcceptedCommands()`의 노출 조건은 다음과 같다.

| 명령 | 노출 조건 |
|---|---|
| `Commands::Reset::kMetadataEntry` | `mFeature.Has(Feature::kReset)` |
| `Commands::ModifyEnabledAlarms::kMetadataEntry` | `mSupportsModifyEnabledAlarms` |

`InvokeCommand()`는 명령 ID에 따라 `DecodableType`으로 입력을 디코딩한다.

- `Commands::Reset::Id`: `AlarmMap(data.alarms.Raw())`를 `HandleReset()`에 전달한다.
- `Commands::ModifyEnabledAlarms::Id`: `AlarmMap(data.mask.Raw())`를 `HandleModifyEnabledAlarms()`에 전달한다.
- 그 외: `Status::UnsupportedCommand`를 반환한다.

제공된 `InvokeCommand()` 내부에는 기능 활성화 여부나 `mSupportsModifyEnabledAlarms`를 다시 검사하는 코드가 없다.

| 처리 함수 | 지원 비트 검사 실패 | delegate 거부 | delegate 허용 후 처리 |
|---|---|---|---|
| `HandleReset()` | `Status::InvalidCommand` | `Status::Failure` | `ResetLatchedAlarms(alarms)` |
| `HandleModifyEnabledAlarms()` | `Status::InvalidCommand` | `Status::Failure` | `SetMask(mask)` |

### `Delegate`

`Delegate`는 수신 명령 처리 중 Matter 속성을 갱신하기 전에 호출된다. 두 메서드의 기본 구현은 모두 `true`를 반환한다.

| 메서드 | 호출 시점 | 용도 |
|---|---|---|
| `ModifyEnabledAlarms(AlarmMap mask)` | `Mask` 갱신 전 | 요청된 알람 활성화·억제 동작에 맞춰 하드웨어 또는 내부 정책을 조정하거나 요청을 거부 |
| `ResetAlarms(AlarmMap alarms)` | `State` 갱신 전 | 물리적·논리적 알람 상태를 해제하거나 요청을 거부 |

- `true`를 반환하면 클러스터가 후속 속성 갱신을 수행한다.
- `false`를 반환하면 클러스터는 `Status::Failure`를 반환하고 후속 속성 갱신을 수행하지 않는다.
- Matter 속성 모델만 사용하는 구현은 기본 동작처럼 무조건 `true`를 반환할 수 있다.
- 물리적 알람이나 하드웨어 latch 상태가 있는 제품은 이 훅에서 장치 측 동작을 수행하거나 거부할 수 있다.

### 이벤트 훅

`SendNotifyEvent()`는 protected 순수 가상 함수이다. `AlarmBaseCluster` 자체에는 구체적인 이벤트 전송 구현이 없다.

상태가 변경되면 다음 값을 전달한다.

| 인자 | 의미 |
|---|---|
| `becameActive` | 이전 상태에는 없고 새 상태에는 있는 비트 |
| `becameInactive` | 이전 상태에는 있고 새 상태에는 없는 비트 |
| `newState` | 갱신된 상태 |
| `mask` | 현재 `Mask` |

파생 구현은 `SendNotifyEvent()`를 구현해야 한다.