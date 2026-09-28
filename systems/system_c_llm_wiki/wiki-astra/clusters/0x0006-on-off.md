---
entity: On/Off
ids: ['0x0006']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml', 'src/app/clusters/on-off-server/on-off-server.h', 'src/app/clusters/on-off-server/OnOffDelegate.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.cpp', 'src/app/clusters/on-off-server/OnOffCluster.cpp', 'src/app/clusters/on-off-server/OnOffEffectDelegate.h', 'src/app/clusters/on-off-server/OnOffCluster.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.h', 'data_model/1.7/clusters/OnOff.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# On/Off

## 개요

On/Off는 장치를 `On`과 `Off` 상태 사이에서 전환하기 위한 속성과 명령을 제공하는 클러스터다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0006` |
| 스펙 이름 | `On/Off Cluster` |
| 리비전 | `7` |
| SDK 도메인 | `General` |
| SDK define | `ON_OFF_CLUSTER` |
| 분류 | hierarchy: `base`, role: `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `OO` |

구현은 기본 동작을 제공하는 `OnOffCluster`와 조명 관련 속성·명령을 추가하는 `OnOffLightingCluster`로 나뉜다. 애플리케이션의 상태 반영과 조명 효과 처리는 각각 `OnOffDelegate`, `OnOffEffectDelegate`를 통해 연동한다.

## 스펙

출처: `data_model/1.7/clusters/OnOff.xml`

### 리비전 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가; CCB 1555 |
| `2` | ZLO 1.0: `StartUpOnOff` |
| `3` | `FeatureMap` 전역 속성 지원 및 Level Control, `Lighting` 관련 변경 |
| `4` | 새로운 데이터 모델 형식과 표기법 |
| `5` | `DeadFrontBehavior` 및 관련 `FeatureMap` 항목 추가 |
| `6` | `OffOnly` 및 관련 `FeatureMap` 항목 추가 |
| `7` | `OnTime`, `OffWaitTime`에 Q 품질 추가 |

### 기능

| bit | code | name | 설명 | 선택 가능 조건 |
|---|---|---|---|---|
| `0` | `LT` | `Lighting` | 조명 애플리케이션 지원 동작 | `OFFONLY`가 없을 때 |
| `1` | `DF` | `DeadFrontBehavior` | Dead Front 동작 | `OFFONLY`가 없을 때 |
| `2` | `OFFONLY` | `OffOnly` | `OffOnly` 기능 지원 | `LT`와 `DF`가 모두 없을 때 |

`OFFONLY`는 `LT`, `DF`와 함께 사용할 수 없다.

### 데이터 타입

#### 열거형

| 타입 | 이름 | 값 | 의미 |
|---|---|---|---|
| `StartUpOnOffEnum` | `Off` | `0` | `OnOff`를 `FALSE`로 설정 |
| `StartUpOnOffEnum` | `On` | `1` | `OnOff`를 `TRUE`로 설정 |
| `StartUpOnOffEnum` | `Toggle` | `2` | 이전 `OnOff` 값을 반전 |
| `EffectIdentifierEnum` | `DelayedAllOff` | `0x00` | Delayed All Off 효과 |
| `EffectIdentifierEnum` | `DyingLight` | `0x01` | Dying Light 효과 |
| `DelayedAllOffEffectVariantEnum` | `DelayedOffFastFade` | `0x00` | 0.8초 동안 페이드하여 꺼짐 |
| `DelayedAllOffEffectVariantEnum` | `NoFade` | `0x01` | 페이드 없음 |
| `DelayedAllOffEffectVariantEnum` | `DelayedOffSlowFade` | `0x02` | 0.8초 동안 50% 어둡게 한 뒤 12초 동안 페이드하여 꺼짐 |
| `DyingLightEffectVariantEnum` | `DyingLightFadeOff` | `0x00` | 0.5초 동안 20% 밝게 한 뒤 1초 동안 페이드하여 꺼짐 |

#### 비트맵

| 타입 | 이름 | bit | 의미 |
|---|---|---|---|
| `OnOffControlBitmap` | `AcceptOnlyWhenOn` | `0` | `On` 상태일 때만 명령 수락 |

### 속성

모든 속성의 읽기 권한은 `view`다.

| ID | 이름 | 스펙 타입 | 쓰기 권한 | 필수 조건 | 품질 |
|---|---|---|---|---|---|
| `0x0000` | `OnOff` | `bool` | 쓰기 접근 없음 | 항상 필수 | `scene="true"`, `persistence="nonVolatile"` |
| `0x4000` | `GlobalSceneControl` | `bool` | 쓰기 접근 없음 | `LT` | — |
| `0x4001` | `OnTime` | `uint16` | `operate` | `LT` | `quieterReporting="true"` |
| `0x4002` | `OffWaitTime` | `uint16` | `operate` | `LT` | `quieterReporting="true"` |
| `0x4003` | `StartUpOnOff` | `StartUpOnOffEnum` | `manage` | `LT` | `nullable="true"`, `persistence="nonVolatile"` |

### 명령

모든 명령은 `direction="commandToServer"`, `response="Y"`이며 호출 권한은 `operate`다.

| ID | 이름 | 필수 조건 | 필드 |
|---|---|---|---|
| `0x00` | `Off` | 항상 필수 | 없음 |
| `0x01` | `On` | `OFFONLY`가 없을 때 | 없음 |
| `0x02` | `Toggle` | `OFFONLY`가 없을 때 | 없음 |
| `0x40` | `OffWithEffect` | `LT` | `EffectIdentifier`, `EffectVariant` |
| `0x41` | `OnWithRecallGlobalScene` | `LT` | 없음 |
| `0x42` | `OnWithTimedOff` | `LT` | `OnOffControl`, `OnTime`, `OffWaitTime` |

#### 명령 필드

| 명령 | field ID | 이름 | 타입 | 제약 |
|---|---|---|---|---|
| `OffWithEffect` | `0` | `EffectIdentifier` | `EffectIdentifierEnum` | 입력 XML의 제약 설명은 비어 있음 |
| `OffWithEffect` | `1` | `EffectVariant` | `enum8` | 입력 XML의 제약 설명은 비어 있음 |
| `OnWithTimedOff` | `0` | `OnOffControl` | `OnOffControlBitmap` | `0`부터 `1`까지 |
| `OnWithTimedOff` | `1` | `OnTime` | `uint16` | 최대 `0xFFFE` |
| `OnWithTimedOff` | `2` | `OffWaitTime` | `uint16` | 최대 `0xFFFE` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml`

### 생성 정보와 클러스터 설정

- Alchemy가 생성한 XML이며 직접 수정하지 않도록 표시되어 있다.
- 생성 원본: `src/app_clusters/OnOff.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`
- 클라이언트와 서버가 모두 활성화되어 있으며 각각 `init="false"`, `tick="false"`다.
- 전역 속성 `0xFFFD`는 `side="either"`, 값은 `7`로 정의된다.
- 기능 비트와 적합성 조건은 스펙의 `LT`, `DF`, `OFFONLY` 정의와 동일하다.

### 타입 표현

| 스펙 타입 | SDK XML 타입 |
|---|---|
| `bool` | `boolean` |
| `uint16` | `int16u` |
| `StartUpOnOffEnum` | `enum8` 기반 |
| `EffectIdentifierEnum` | `enum8` 기반 |
| `DelayedAllOffEffectVariantEnum` | `enum8` 기반 |
| `DyingLightEffectVariantEnum` | `enum8` 기반 |
| `OnOffControlBitmap` | `bitmap8` 기반 |

SDK XML에서 `StartUpOnOffEnum`의 `Off`, `On`, `Toggle` 값은 각각 `0x00`, `0x01`, `0x02`다. `AcceptOnlyWhenOn`의 마스크는 `0x01`이다.

### 속성 정의

모든 속성은 `side="server"`다.

| 이름 | define | 타입 | 추가 설정 |
|---|---|---|---|
| `OnOff` | `ON_OFF` | `boolean` | — |
| `GlobalSceneControl` | `GLOBAL_SCENE_CONTROL` | `boolean` | `optional="true"`, `LT`에서 필수 |
| `OnTime` | `ON_TIME` | `int16u` | `writable="true"`, `optional="true"`, `LT`에서 필수 |
| `OffWaitTime` | `OFF_WAIT_TIME` | `int16u` | `writable="true"`, `optional="true"`, `LT`에서 필수 |
| `StartUpOnOff` | `START_UP_ON_OFF` | `StartUpOnOffEnum` | `max="2"`, `isNullable="true"`, `writable="true"`, `optional="true"`, 쓰기 권한 `manage`, `LT`에서 필수 |

`optional="true"`로 표시된 항목도 해당 `mandatoryConform` 조건에서는 필수다.

### 명령 정의와 제약

모든 명령의 `source`는 `client`다.

- `Off`: 장치를 끈다.
- `On`: 장치를 켠다.
- `Toggle`: 장치 상태를 반전한다.
- `OffWithEffect`: 페이드 효과를 사용하여 장치를 끈다.
  - `EffectIdentifier`: `EffectIdentifierEnum`, 최대 `0x01`.
  - `EffectVariant`: `enum8`.
- `OnWithRecallGlobalScene`: 장치가 꺼질 때의 설정을 호출한다.
- `OnWithTimedOff`: 지정한 시간 동안 장치를 켜며, 이후 장치가 꺼졌을 때 보호 시간 동안 수신한 `OnWithTimedOff`가 다시 켜지 못하도록 한다.
  - `OnOffControl`: `OnOffControlBitmap`, 최대 `1`.
  - `OnTime`, `OffWaitTime`: `int16u`, 최대 `0xFFFE`.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/on-off-server/on-off-server.h` | 기존 codegen 클러스터 구현과의 하위 호환용 헤더. `codegen/on-off-server.h`를 포함 |
| `src/app/clusters/on-off-server/OnOffCluster.h` | 기본 서버 클러스터, delegate 등록, 상태 접근, 장면 처리 인터페이스 |
| `src/app/clusters/on-off-server/OnOffCluster.cpp` | 기본 속성·명령, 영속화, 장면 저장 및 적용 |
| `src/app/clusters/on-off-server/OnOffLightingCluster.h` | 조명 기능용 컨텍스트, 속성 접근, 타이머 및 명령 처리 인터페이스 |
| `src/app/clusters/on-off-server/OnOffLightingCluster.cpp` | 조명 시작 동작, 시간 제어, 효과 및 전역 장면 명령 처리 |
| `src/app/clusters/on-off-server/OnOffDelegate.h` | 시작 상태 및 `OnOff` 변경 통지 인터페이스 |
| `src/app/clusters/on-off-server/OnOffEffectDelegate.h` | 조명 효과 처리 인터페이스 |

구현 클래스의 네임스페이스는 `chip::app::Clusters`다.

### OnOffCluster

`OnOffCluster`는 `DefaultServerCluster`와 `scenes::DefaultSceneHandlerImpl`을 상속한다. 구현 크기를 작게 유지하기 위해 `Lighting`은 지원하지 않는다.

#### 구성과 기능 검증

`Context`는 다음 항목을 제공한다.

- `timerDelegate`: `TimerDelegate` 참조.
- `featureMap`: 기본값 `{}`.
- `defaults`: 영속 저장 값이 없을 때 사용할 `Defaults`.
  - `onOff`: 기본 `OnOff` 값.

기본 생성자가 허용하는 기능은 `Feature::kDeadFrontBehavior`, `Feature::kOffOnly`다. 생성 시 다음 조건을 `VerifyOrDie`로 검증한다.

1. 요청한 `featureMap`이 지원 기능의 부분집합이어야 한다.
2. `Feature::kOffOnly`가 있으면 다른 기능이 없어야 한다.

#### 시작과 상태 변경

`Startup`은 다음 순서로 처리한다.

1. `DefaultServerCluster::Startup` 호출.
2. `AttributePersistence::LoadNativeEndianValue`로 `OnOff` 복원.
3. 등록된 모든 delegate에 `OnOffStartup(mOnOff)` 호출.

`SetOnOff(bool on)`은 다음을 수행한다.

1. 대기 중인 장면 전환 타이머 취소.
2. 현재 값과 같으면 변경 없이 성공 반환.
3. `mOnOff` 변경 및 `NotifyAttributeChanged` 호출.
4. `AttributePersistence::StoreNativeEndianValue`로 저장 시도.
5. 모든 delegate에 `OnOnOffChanged(mOnOff)` 호출.

저장 실패는 로그로 기록하며, 이후 delegate 통지는 계속 진행한다.

#### 속성과 명령

- `Attributes`는 `Attributes::kMandatoryMetadata`를 추가한다.
- `ReadAttribute`는 `ClusterRevision`, `FeatureMap`, `OnOff`를 처리한다.
- 그 외 읽기는 `Status::UnsupportedAttribute`를 반환한다.
- `AcceptedCommands`:
  - `Feature::kOffOnly`: `Off`만 제공.
  - 그 외: `Off`, `On`, `Toggle` 제공.
- `InvokeCommand`는 각 명령을 `SetOnOff(false)`, `SetOnOff(true)`, `SetOnOff(!mOnOff)`로 처리한다.
- 미지원 명령은 `Status::UnsupportedCommand`를 반환한다.

`OffOnly` 명령 제한은 Interaction Model이 `AcceptedCommands` 목록을 확인하여 처리하도록 되어 있다.

### OnOffDelegate

`OnOffDelegate`는 `IntrusiveListNodeBase<IntrusiveMode::AutoUnlink>`를 상속한다. `AddDelegate`, `RemoveDelegate`로 여러 delegate를 관리한다.

| 함수 | 역할 |
|---|---|
| `OnOffStartup(bool on)` | 클러스터 시작 시 결정된 상태 전달. 조명에서는 시작 설정이 적용된 상태를 전달 |
| `OnOnOffChanged(bool on)` | `OnOff` 변경 통지. delegate는 하드웨어 상태를 새 값에 맞춰야 함 |

`OnOnOffChanged`는 시작 처리의 일부로 호출되지 않는다.

### 장면 저장과 적용

- `SupportsCluster`는 클러스터 ID와 엔드포인트가 모두 일치하는지 검사한다.
- `OnOffValidator::Validate`는 클러스터가 `Clusters::OnOff::Id`이고 속성이 `Attributes::OnOff::Id`인지 확인한다.
- `SerializeSave`는 `OnOff`를 `valueUnsigned8`에 넣어 `EncodeAttributeValueList`로 직렬화한다.
- `ApplyScene`은 다음을 검사한다.
  - 대상 엔드포인트와 클러스터 일치.
  - 속성 ID가 `Attributes::OnOff::Id`.
  - `valueUnsigned8` 값 존재.
- `timeMs > 0`이면 `SceneTransitionTimer`로 지연 적용하고, 그렇지 않으면 `SetOnOff`로 즉시 적용한다.
- `IsSceneTransitionPending`으로 장면 전환 타이머의 활성 상태를 확인한다.

### OnOffLightingCluster

`OnOffLightingCluster`는 `OnOffCluster`와 `TimerContext`를 상속한다. 생성 시 허용하는 기능 집합은 `Feature::kLighting`, `Feature::kDeadFrontBehavior`다.

#### 구성과 초기 상태

| 항목 | 정의 또는 기본값 |
|---|---|
| `timerDelegate` | 필수 `TimerDelegate` 참조 |
| `effectDelegate` | 필수 `OnOffEffectDelegate` 참조 |
| `scenesIntegrationDelegate` | 기본값 `nullptr` |
| `featureMap` | 기본값 `OnOff::Feature::kLighting` |
| `startupType` | 기본값 `StartupType::kRegular` |
| `defaults.onOff` | `bool onOff{}` |
| `defaults.startupOnOff` | `DataModel::Nullable<OnOff::StartUpOnOffEnum>` |
| `mGlobalSceneControl` | `true` |
| `mOnTime` | `0` |
| `mOffWaitTime` | `0` |

#### 시작 동작과 영속화

`Startup`은 올바른 시작 상태를 delegate에 전달하기 위해 `OnOffCluster::Startup` 대신 `DefaultServerCluster::Startup`을 직접 호출한다.

1. 저장된 `OnOff`와 `StartUpOnOff`를 읽는다. 저장 값이 없으면 생성 시 기본값을 유지한다.
2. `mStartupType != StartupType::kOTA`이고 `StartUpOnOff`가 null이 아니면 다음을 적용한다.
   - `StartUpOnOffEnum::kOff`: `false`.
   - `StartUpOnOffEnum::kOn`: `true`.
   - `StartUpOnOffEnum::kToggle`: 이전 상태 반전.
   - 그 외 값: 이전 상태 유지.
3. 시작 동작으로 `OnOff`가 바뀌면 변경 상태를 저장한다.
4. 모든 delegate에 `OnOffStartup(mOnOff)`를 호출한다.

`StartupType::kOTA`에서는 `StartUpOnOff` 동작을 적용하지 않고 복원된 `OnOff`를 유지한다.

`SetStartupOnOff`는 값을 변경하고, `mContext`가 있으면 저장한다. 속성 쓰기 경로에서는 `DecodeAndStoreNativeEndianValue`를 사용한다.

#### 속성 읽기와 쓰기

기본 속성에 `GlobalSceneControl`, `OnTime`, `OffWaitTime`, `StartUpOnOff`를 추가한다.

- `ReadAttribute`는 조명 속성을 처리하고 나머지는 `OnOffCluster::ReadAttribute`로 위임한다.
- `WriteAttribute`는 `WriteImpl` 결과를 `NotifyAttributeChangedIfSuccess`에 전달한다.
- `OnTime`, `OffWaitTime` 쓰기:
  - 값을 디코딩한다.
  - 기존 값과 같으면 `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`.
  - 변경되면 값을 갱신하고 `UpdateTimer`를 호출한다.
- 그 외 지원하지 않는 쓰기는 `Status::UnsupportedWrite`다.

`SetOnTime`, `SetOffWaitTime`은 값이 변경될 때 타이머를 갱신한다. 변경 폭이 `kValueDeltaReportTrigger`인 `10`보다 크거나 새 값이 `0`이면 속성 변경을 통지한다.

#### 기본 명령의 조명 부수 동작

| 처리 함수 | 동작 |
|---|---|
| `HandleOff` | `SetOnOffFromCommand(false)` 호출, `OnTime`을 `0`으로 설정, 타이머 갱신 |
| `HandleOn` | `SetOnOffFromCommand(true)` 호출, `GlobalSceneControl`을 `true`로 설정, `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정, 타이머 갱신 |
| `HandleToggle` | 현재 켜져 있으면 `HandleOff`, 아니면 `HandleOn` 호출 |

`SetOnOffFromCommand`는 실제 상태가 바뀔 때만 전이 처리를 수행한다. 켤 때는 `OffWaitTime`을, 끌 때는 `OnTime`을 `0`으로 만든 뒤 `SetOnOff`를 호출한다.

#### OffWithEffect

`HandleOffWithEffect`는 명령을 디코딩한 뒤 `GlobalSceneControl`에 따라 처리한다.

- `true`인 경우:
  1. `scenesIntegrationDelegate`가 있으면 요청의 `fabricIndex`로 `StoreCurrentGlobalScene` 호출. 실패는 로그로 기록한다.
  2. `TriggerEffect` 호출. 실패하면 해당 상태를 반환한다.
  3. `GlobalSceneControl`을 `false`로 변경.
  4. `SetOnOffFromCommand(false)` 호출.
  5. `OnTime`을 `0`으로 설정하고 타이머 갱신.
- `false`인 경우: `HandleOff` 호출.

#### OnWithRecallGlobalScene

`HandleOnWithRecallGlobalScene`의 동작은 다음과 같다.

- `GlobalSceneControl == true`이면 명령을 버리고 `Status::Success`를 반환한다.
- 그 외에는 `scenesIntegrationDelegate`가 있으면 `RecallGlobalScene`을 호출한다.
- 호출 실패 시 오류를 기록하고 장치를 켠다.
- delegate가 없어도 장치를 켠다.
- 이후 `GlobalSceneControl`을 `true`로 설정한다.
- `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정하고 타이머를 갱신한다.

#### OnWithTimedOff

`HandleOnWithTimedOff`는 먼저 다음을 검사한다.

- `commandData.onTime`, `commandData.offWaitTime`이 `0xFFFE`를 초과하면 `Status::ConstraintError`.
- `OnOffControlBitmap::kAcceptOnlyWhenOn`이 설정되어 있고 현재 꺼져 있으면 명령을 버리고 `Status::Success`.

현재 꺼져 있고 `OffWaitTime == 0`이면 `SetOnOff(true)`로 켜기를 시도하고 `GlobalSceneControl`을 `true`로 설정한다. 시간 갱신은 명령 수신 전 상태를 기준으로 한다.

| 수신 전 상태 | `OnTime` 처리 | `OffWaitTime` 처리 |
|---|---|---|
| 켜짐, `OnTime > 0` | 기존 값과 수신 값 중 큰 값 | 수신 값 |
| 켜짐, `OnTime == 0` | 수신 값 | 수신 값 |
| 꺼짐, `OffWaitTime > 0` | 수신 값 무시 | 기존 값과 수신 값 중 작은 값 |
| 꺼짐, `OffWaitTime == 0` | 수신 값 | 수신 값 |

마지막으로 `UpdateTimer`를 호출한다.

#### 타이머

`OnTime`, `OffWaitTime`은 1/10초 단위다.

`UpdateTimer`는 기존 타이머를 취소한 뒤 현재 상태에 따라 필요한 타이머를 100ms 간격으로 시작한다.

- 켜져 있으면 `OnTime`이 `0`도 `0xFFFF`도 아닐 때.
- 꺼져 있으면 `OffWaitTime`이 `0`도 `0xFFFF`도 아닐 때.

`TimerFired`는 다음과 같이 동작한다.

- 켜진 상태:
  - `OnTime` 감소.
  - `0`에 도달하면 속성 변경 통지.
  - `OffWaitTime`을 `0`으로 만들고 `SetOnOff(false)` 호출.
- 꺼진 상태:
  - `OffWaitTime` 감소.
  - `0`에 도달하면 속성 변경 통지.
  - 타이머 갱신.

> `src/app/clusters/on-off-server/OnOffLightingCluster.h`의 상태 설명 주석은 `TIMED_OFF`에서 시간이 `0`이 되면 켜진다고 적고 있다. 그러나 제공된 `TimerFired` 구현에는 이때 장치를 켜는 호출이 없다.

#### 다른 클러스터와의 시간 초기화 연동

`SetOnOffWithTimeReset(bool on)`은 `SetOnOff` 호출 후 다음 조건을 적용한다.

- `on == false`이고 `OnTime != 0`: `OnTime`을 `0`으로 설정.
- `on == true`, `OnTime == 0`, `OffWaitTime != 0`: `OffWaitTime`을 `0`으로 설정.

시간 값이 변경되면 타이머 갱신과 속성 변경 통지를 수행한다.

> 헤더 설명은 켤 때 `OffWaitTime`을 초기화한다고 요약하지만, 실제 구현에는 `OnTime == 0` 조건이 있다.

### OnOffEffectDelegate

`TriggerEffect(OnOff::EffectIdentifierEnum effectId, uint8_t effectVariant)`는 효과 ID에 따라 분기한다.

| 효과 ID | 호출 |
|---|---|
| `OnOff::EffectIdentifierEnum::kDelayedAllOff` | `TriggerDelayedAllOff` |
| `OnOff::EffectIdentifierEnum::kDyingLight` | `TriggerDyingLight` |
| 그 외 | `Status::InvalidCommand` 반환 |

`effectVariant`는 해당 효과의 열거형으로 변환되어 전달된다. 기본 `TriggerDelayedAllOff`, `TriggerDyingLight` 구현은 모두 `Status::UnsupportedCommand`를 반환한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
