---
entity: On/Off
ids: ['0x0006']
source_paths: ['data_model/1.7/clusters/OnOff.xml', 'src/app/clusters/on-off-server/OnOffCluster.cpp', 'src/app/clusters/on-off-server/OnOffCluster.h', 'src/app/clusters/on-off-server/OnOffDelegate.h', 'src/app/clusters/on-off-server/OnOffEffectDelegate.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.cpp', 'src/app/clusters/on-off-server/OnOffLightingCluster.h', 'src/app/clusters/on-off-server/on-off-server.h', 'src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# On/Off

## 개요

On/Off는 장치를 켜짐과 꺼짐 상태로 전환하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `On/Off` |
| 스펙 이름 | `On/Off Cluster` |
| 클러스터 ID | `0x0006` |
| 리비전 | `7` |
| 분류 | hierarchy: `base`, role: `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `OO` |

구현은 기본 기능을 제공하는 `OnOffCluster`와 조명 기능을 추가하는 `OnOffLightingCluster`로 나뉜다.

## 스펙

출처: `data_model/1.7/clusters/OnOff.xml`

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 조건 |
|---|---|---|---|---|
| `0` | `LT` | `Lighting` | 조명 애플리케이션 지원 | `OFFONLY`가 없을 때 선택 가능 |
| `1` | `DF` | `DeadFrontBehavior` | Dead Front 동작 지원 | `OFFONLY`가 없을 때 선택 가능 |
| `2` | `OFFONLY` | `OffOnly` | `OffOnly` 기능 지원 | `LT`와 `DF`가 모두 없을 때 선택 가능 |

`OFFONLY`는 `LT` 또는 `DF`와 함께 사용할 수 없다.

### 속성

모든 속성의 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 접근 | 적합성 | 품질 |
|---|---|---|---|---|---|
| `0x0000` | `OnOff` | `bool` | 읽기 | 필수 | `scene="true"`, `persistence="nonVolatile"` |
| `0x4000` | `GlobalSceneControl` | `bool` | 읽기 | `LT` 사용 시 필수 | — |
| `0x4001` | `OnTime` | `uint16` | 읽기, 쓰기: `operate` | `LT` 사용 시 필수 | `quieterReporting="true"` |
| `0x4002` | `OffWaitTime` | `uint16` | 읽기, 쓰기: `operate` | `LT` 사용 시 필수 | `quieterReporting="true"` |
| `0x4003` | `StartUpOnOff` | `StartUpOnOffEnum` | 읽기, 쓰기: `manage` | `LT` 사용 시 필수 | `nullable="true"`, `persistence="nonVolatile"` |

### 명령

모든 명령은 `direction="commandToServer"`, `response="Y"`이며 호출 권한은 `operate`이다.

| ID | 이름 | 적합성 | 필드 |
|---|---|---|---|
| `0x00` | `Off` | 필수 | 없음 |
| `0x01` | `On` | `OFFONLY`가 없을 때 필수 | 없음 |
| `0x02` | `Toggle` | `OFFONLY`가 없을 때 필수 | 없음 |
| `0x40` | `OffWithEffect` | `LT` 사용 시 필수 | `EffectIdentifier`, `EffectVariant` |
| `0x41` | `OnWithRecallGlobalScene` | `LT` 사용 시 필수 | 없음 |
| `0x42` | `OnWithTimedOff` | `LT` 사용 시 필수 | `OnOffControl`, `OnTime`, `OffWaitTime` |

#### 명령 필드

아래 필드는 모두 필수이다.

| 명령 | 필드 ID | 이름 | 타입 | 명시된 제약 |
|---|---|---|---|---|
| `OffWithEffect` | `0` | `EffectIdentifier` | `EffectIdentifierEnum` | 구체적인 제약 설명 없음 |
| `OffWithEffect` | `1` | `EffectVariant` | `enum8` | 구체적인 제약 설명 없음 |
| `OnWithTimedOff` | `0` | `OnOffControl` | `OnOffControlBitmap` | `0`부터 `1`까지 |
| `OnWithTimedOff` | `1` | `OnTime` | `uint16` | 최댓값 `0xFFFE` |
| `OnWithTimedOff` | `2` | `OffWaitTime` | `uint16` | 최댓값 `0xFFFE` |

### 데이터 타입

#### `StartUpOnOffEnum`

| 값 | 이름 | 동작 |
|---|---|---|
| `0` | `Off` | `OnOff`를 `FALSE`로 설정 |
| `1` | `On` | `OnOff`를 `TRUE`로 설정 |
| `2` | `Toggle` | 이전 `OnOff` 값을 반전 |

#### `EffectIdentifierEnum`

| 값 | 이름 |
|---|---|
| `0x00` | `DelayedAllOff` |
| `0x01` | `DyingLight` |

#### `DelayedAllOffEffectVariantEnum`

| 값 | 이름 | 효과 |
|---|---|---|
| `0x00` | `DelayedOffFastFade` | 0.8초 동안 서서히 꺼짐 |
| `0x01` | `NoFade` | 페이드 없음 |
| `0x02` | `DelayedOffSlowFade` | 0.8초 동안 50% 감광한 뒤 12초 동안 서서히 꺼짐 |

#### `DyingLightEffectVariantEnum`

| 값 | 이름 | 효과 |
|---|---|---|
| `0x00` | `DyingLightFadeOff` | 0.5초 동안 20% 밝게 한 뒤 1초 동안 서서히 꺼짐 |

#### `OnOffControlBitmap`

| 비트 | 이름 | 의미 |
|---|---|---|
| `0` | `AcceptOnlyWhenOn` | 켜진 상태에서만 명령 수락 |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가, CCB 1555 |
| `2` | ZLO 1.0: `StartUpOnOff` |
| `3` | Level Control 및 `Lighting` 기능과 함께 전역 속성 `FeatureMap` 지원 |
| `4` | 새로운 데이터 모델 형식과 표기법 |
| `5` | Dead Front 동작 및 관련 `FeatureMap` 항목 추가 |
| `6` | `OffOnly` 및 관련 `FeatureMap` 항목 추가 |
| `7` | `OnTime`, `OffWaitTime`에 Q 품질 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 이름 | `On/Off` |
| 도메인 | `General` |
| 코드 | `0x0006` |
| define | `ON_OFF_CLUSTER` |
| 전역 속성 | `code="0xFFFD"`, `value="7"`, `side="either"` |
| 클라이언트 | 지원, `init="false"`, `tick="false"` |
| 서버 | 지원, `init="false"`, `tick="false"` |

이 XML은 Alchemy가 생성한 파일이며 직접 수정하지 않도록 표시되어 있다. 생성 원본은 `src/app_clusters/OnOff.adoc`이다.

### 타입과 속성 매핑

다음 열거형은 모두 `enum8`로 정의된다.

- `StartUpOnOffEnum`: `Off="0x00"`, `On="0x01"`, `Toggle="0x02"`
- `EffectIdentifierEnum`: `DelayedAllOff="0x00"`, `DyingLight="0x01"`
- `DelayedAllOffEffectVariantEnum`: `DelayedOffFastFade="0x00"`, `NoFade="0x01"`, `DelayedOffSlowFade="0x02"`
- `DyingLightEffectVariantEnum`: `DyingLightFadeOff="0x00"`

`OnOffControlBitmap`은 `bitmap8`이며 `AcceptOnlyWhenOn`의 마스크는 `0x01`이다.

모든 속성은 `side="server"`로 정의된다.

| 이름 | define | SDK 타입 | 추가 설정 |
|---|---|---|---|
| `OnOff` | `ON_OFF` | `boolean` | — |
| `GlobalSceneControl` | `GLOBAL_SCENE_CONTROL` | `boolean` | `optional="true"` |
| `OnTime` | `ON_TIME` | `int16u` | `writable="true"`, `optional="true"` |
| `OffWaitTime` | `OFF_WAIT_TIME` | `int16u` | `writable="true"`, `optional="true"` |
| `StartUpOnOff` | `START_UP_ON_OFF` | `StartUpOnOffEnum` | `max="2"`, `isNullable="true"`, `writable="true"`, `optional="true"` |

`optional="true"`로 표시된 조명 속성에도 `LT` 사용 시 필수라는 적합성 조건이 함께 정의된다. `StartUpOnOff` 쓰기 권한은 `manage`이다.

### 명령 정의

모든 명령은 `source="client"`이다.

- `Off`는 필수이다.
- `On`, `Toggle`은 `optional="true"`이며, `OFFONLY`가 없을 때 필수이다.
- `OffWithEffect`, `OnWithRecallGlobalScene`, `OnWithTimedOff`는 `optional="true"`이며, `LT` 사용 시 필수이다.
- `OffWithEffect`의 `EffectIdentifier`에는 `max="0x01"`이 지정된다.
- `OnWithTimedOff`의 `OnOffControl`에는 `max="1"`이 지정된다.
- `OnWithTimedOff`의 `OnTime`, `OffWaitTime`은 `int16u`이며 각각 `max="0xFFFE"`이다.

SDK 설명에서 `OnWithTimedOff`는 지정한 시간 동안 켜짐을 유지하고, 이후 꺼진 경우 보호 대기 시간 동안 추가 `OnWithTimedOff` 명령이 장치를 다시 켜지 못하도록 하는 명령으로 설명된다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/on-off-server/OnOffCluster.h` | 기본 서버 클래스, 컨텍스트, 상태 접근 및 장면 처리 인터페이스 |
| `src/app/clusters/on-off-server/OnOffCluster.cpp` | 기본 속성·명령 처리, 영속화, 장면 전환 |
| `src/app/clusters/on-off-server/OnOffDelegate.h` | 시작 및 상태 변경 알림 인터페이스 |
| `src/app/clusters/on-off-server/OnOffEffectDelegate.h` | 조명 효과 처리 인터페이스 |
| `src/app/clusters/on-off-server/OnOffLightingCluster.h` | 조명 확장 클래스와 설정 |
| `src/app/clusters/on-off-server/OnOffLightingCluster.cpp` | 조명 명령, 시작 상태, 타이머, 전역 장면 처리 |
| `src/app/clusters/on-off-server/on-off-server.h` | 코드 생성 구현과의 하위 호환 헤더 |

### `OnOffCluster`

`chip::app::Clusters`에 정의되며 `DefaultServerCluster`와 `scenes::DefaultSceneHandlerImpl`을 상속한다. 이 클래스 자체는 `Lighting`을 지원하지 않는다.

#### 초기화와 기능 검증

`Context`는 다음 설정을 제공한다.

- `timerDelegate`: 타이머 처리 참조
- `featureMap`: 기본값 `{}`
- `defaults`: 영속 값이 없을 때 사용할 `Defaults`
- `Defaults`의 `onOff`: 기본 상태

공개 생성자가 허용하는 기능은 `Feature::kDeadFrontBehavior`, `Feature::kOffOnly`이다. 보호 생성자는 파생 클래스가 `supportedFeatures`를 지정할 수 있게 한다.

생성 시 `VerifyOrDie`로 다음을 검사한다.

1. 요청한 `featureMap`이 `supportedFeatures`에 포함되는가.
2. `Feature::kOffOnly`가 있으면 다른 기능이 없는가.

#### 시작과 상태 변경

`Startup`은 다음 순서로 동작한다.

1. `DefaultServerCluster::Startup` 호출
2. `AttributePersistence::LoadNativeEndianValue`로 `OnOff` 복원
3. 모든 delegate에 `OnOffStartup(mOnOff)` 전달

`SetOnOff`는 다음을 수행한다.

1. 대기 중인 장면 전환 타이머 취소
2. 값이 같으면 `CHIP_NO_ERROR` 반환
3. `mOnOff` 갱신 및 `NotifyAttributeChanged` 호출
4. `StoreNativeEndianValue`로 상태 저장
5. 모든 delegate에 `OnOnOffChanged(mOnOff)` 전달

저장 실패는 `LogErrorOnFailure`로 기록하며, 이 함수는 마지막에 `CHIP_NO_ERROR`를 반환한다.

상태 조회는 `GetOnOff`, 기능 조회는 `GetFeatureMap`으로 제공한다.

#### 속성과 명령

- `Attributes`는 `Attributes::kMandatoryMetadata`를 추가한다.
- `ReadAttribute`는 `ClusterRevision`, `FeatureMap`, `OnOff`를 처리한다.
- 그 외 읽기는 `UnsupportedAttribute`를 반환한다.
- `AcceptedCommands`는 `Feature::kOffOnly`가 있으면 `Off`만, 그 외에는 `Off`, `On`, `Toggle`을 제공한다.
- `InvokeCommand`는 각각 `SetOnOff(false)`, `SetOnOff(true)`, `SetOnOff(!mOnOff)`를 호출한다.
- 그 외 명령은 `UnsupportedCommand`를 반환한다.

`OffOnly` 명령 제한은 `InvokeCommand` 내부가 아니라 Interaction Model이 `AcceptedCommands` 목록을 확인하는 방식으로 처리된다.

### 상태 변경 delegate

`OnOffDelegate`는 `IntrusiveListNodeBase<IntrusiveMode::AutoUnlink>`를 상속한다.

| 함수 | 역할 |
|---|---|
| `OnOffStartup(bool on)` | 시작 시 확정된 상태 전달 |
| `OnOnOffChanged(bool on)` | `OnOff` 변경 전달; 하드웨어 상태를 새 값에 맞추기 위한 콜백 |

`OnOnOffChanged`는 시작 과정에서 호출되지 않는다. 여러 delegate를 `AddDelegate`와 `RemoveDelegate`로 관리할 수 있다.

### 장면 저장과 전환

- `SupportsCluster`는 endpoint와 `Clusters::OnOff::Id`가 모두 일치하는지 검사한다.
- `OnOffValidator::Validate`는 클러스터 ID와 `Attributes::OnOff::Id`를 검사한다.
- `SerializeSave`는 `OnOff`를 단일 `AttributeValuePairStruct`의 `valueUnsigned8`에 저장하고 `EncodeAttributeValueList`로 직렬화한다.
- `ApplyScene`은 역직렬화된 각 항목이 `Attributes::OnOff::Id`인지, `valueUnsigned8`이 있는지 검사한다.
- 값은 `static_cast<bool>`로 변환한다.
- `timeMs > 0`이면 기존 타이머를 취소하고 `SceneTransitionTimer::Start`로 적용을 지연한다.
- 그 외에는 `SetOnOff`로 즉시 적용한다.
- `SceneTransitionTimer::TimerFired`는 저장된 목표 값으로 `SetOnOff`를 호출한다.
- `IsSceneTransitionPending`은 장면 전환 타이머의 활성 상태를 반환한다.

소멸자는 장면 타이머를 취소하고 delegate 목록을 비운다.

### `OnOffLightingCluster`

`OnOffCluster`와 `TimerContext`를 상속하며 다음을 추가한다.

- `GlobalSceneControl`
- `OnTime`
- `OffWaitTime`
- `StartUpOnOff`
- 조명 명령과 타이머 처리

허용 기능은 `Feature::kLighting`, `Feature::kDeadFrontBehavior`이다.

#### 컨텍스트와 초기 상태

| 항목 | 설정 또는 초기값 |
|---|---|
| `timerDelegate` | 필수 참조 |
| `effectDelegate` | `OnOffEffectDelegate` 필수 참조 |
| `scenesIntegrationDelegate` | 기본값 `nullptr` |
| `featureMap` | 기본값 `OnOff::Feature::kLighting` |
| `startupType` | 기본값 `StartupType::kRegular` |
| `mGlobalSceneControl` | `true` |
| `mOnTime` | `0` |
| `mOffWaitTime` | `0` |

`Defaults`는 `onOff`와 nullable 타입의 `startupOnOff`를 제공한다.

#### 시작 상태와 OTA

`Startup`은 `OnOffCluster::Startup` 대신 `DefaultServerCluster::Startup`을 직접 호출한다. delegate에 최종 시작 상태를 전달하기 위한 처리이다.

1. 영속 저장소에서 `OnOff`, `StartUpOnOff` 복원
2. `mStartupType != StartupType::kOTA`이고 `StartUpOnOff`가 null이 아니면 시작 동작 적용
   - `StartUpOnOffEnum::kOff`: 꺼짐
   - `StartUpOnOffEnum::kOn`: 켜짐
   - `StartUpOnOffEnum::kToggle`: 이전 상태 반전
   - 그 외 값: 이전 상태 유지
3. 상태가 변경되면 `OnOff` 저장
4. 모든 delegate에 `OnOffStartup` 전달

`StartupType::kOTA`에서는 `StartUpOnOff` 동작을 적용하지 않고 복원한 `OnOff`를 유지한다.

#### 속성 접근과 보고

- `Attributes`는 네 조명 속성을 추가한 뒤 기본 속성 목록을 추가한다.
- `ReadAttribute`는 조명 속성을 처리하고 나머지는 `OnOffCluster::ReadAttribute`로 전달한다.
- `WriteAttribute`는 `WriteImpl` 결과에 `NotifyAttributeChangedIfSuccess`를 적용한다.
- `OnTime`, `OffWaitTime` 쓰기는 값이 같으면 `kWriteSuccessNoOp`를 반환하고, 변경되면 타이머를 갱신한다.
- `StartUpOnOff` 쓰기는 `DecodeAndStoreNativeEndianValue`를 사용한다.
- 그 외 쓰기는 `UnsupportedWrite`를 반환한다.

`SetOnTime`, `SetOffWaitTime`은 값이 변경되었을 때 다음 조건에서 속성 변경을 알린다.

- 이전 값과 새 값의 차이가 `kValueDeltaReportTrigger`인 `10`보다 큼
- 새 값이 `0`

`SetStartupOnOff`는 속성을 갱신하고, `mContext != nullptr`이면 영속 저장한다.

#### 기본 명령의 추가 동작

| 처리 함수 | 동작 |
|---|---|
| `HandleOff` | 꺼짐 처리, `OnTime`을 `0`으로 설정, 타이머 갱신 |
| `HandleOn` | 켜짐 처리, `GlobalSceneControl`을 `true`로 설정, `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정, 타이머 갱신 |
| `HandleToggle` | 현재 상태에 따라 `HandleOff` 또는 `HandleOn` 호출 |

`SetOnOffFromCommand`는 상태 변경이 없으면 바로 반환한다. 상태가 바뀌면 켤 때 `OffWaitTime`을, 끌 때 `OnTime`을 `0`으로 만든 뒤 `SetOnOff`를 호출한다.

#### `OffWithEffect`

`HandleOffWithEffect`는 명령을 디코딩한 뒤 다음과 같이 처리한다.

- `mGlobalSceneControl`이 `true`인 경우:
  1. `mScenesIntegrationDelegate`가 있으면 요청 fabric의 `StoreCurrentGlobalScene` 호출
  2. `mEffectDelegate.TriggerEffect` 호출
  3. 효과 처리 실패 시 해당 상태 반환
  4. `GlobalSceneControl`을 `false`로 설정
  5. 꺼짐 처리 및 `OnTime` 초기화
  6. 타이머 갱신
- 이미 `false`이면 `HandleOff` 호출

전역 장면 저장 오류는 기록한 뒤 처리를 계속한다.

#### `OnWithRecallGlobalScene`

`HandleOnWithRecallGlobalScene`은 다음과 같이 처리한다.

- `mGlobalSceneControl`이 `true`이면 아무 동작 없이 `Status::Success` 반환
- delegate가 있으면 요청 fabric의 `RecallGlobalScene` 호출
- 복원 실패 시 오류를 기록하고 켜짐 처리
- delegate가 없어도 켜짐 처리
- 이후 `GlobalSceneControl`을 `true`로 설정
- `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정
- 타이머 갱신

#### `OnWithTimedOff`

`HandleOnWithTimedOff`는 `onTime`, `offWaitTime`이 각각 `0xFFFE` 이하인지 검사한다. 위반하면 `Status::ConstraintError`를 반환한다.

`OnOffControlBitmap::kAcceptOnlyWhenOn`이 설정되어 있고 현재 꺼져 있으면 상태를 바꾸지 않고 `Status::Success`를 반환한다.

그 외에는 명령 수신 전 상태를 기준으로 처리한다.

| 이전 상태 | 처리 |
|---|---|
| 켜짐, `mOnTime > 0` | 기존 `mOnTime`과 요청 `onTime` 중 큰 값 사용; 요청 `offWaitTime` 적용 |
| 켜짐, `mOnTime == 0` | 요청 `onTime`, `offWaitTime` 적용 |
| 꺼짐, `mOffWaitTime > 0` | 요청 `onTime` 무시; 기존 `mOffWaitTime`과 요청 `offWaitTime` 중 작은 값 사용 |
| 꺼짐, `mOffWaitTime == 0` | 켜짐 처리, `GlobalSceneControl`을 `true`로 설정, 요청 시간 적용 |

마지막으로 `UpdateTimer`를 호출한다.

#### 타이머 동작

`UpdateTimer`는 기존 타이머를 취소하고 다음 조건에 따라 100ms 타이머를 시작한다.

- 켜져 있으면 `mOnTime`이 `0`도 `0xFFFF`도 아닐 때
- 꺼져 있으면 `mOffWaitTime`이 `0`도 `0xFFFF`도 아닐 때

`TimerFired`의 동작은 다음과 같다.

- 켜짐 상태:
  - `mOnTime` 감소
  - `0`이 아니면 타이머 재설정
  - `0`이면 `OnTime` 변경 알림, `OffWaitTime`을 `0`으로 설정하고 꺼짐 처리
- 꺼짐 상태:
  - `mOffWaitTime` 감소
  - `0`이 되면 `OffWaitTime` 변경 알림
  - 타이머 갱신

> `OnOffLightingCluster.h`의 `TIMED_OFF` 설명에는 시간이 `0`이 되면 켜진다고 적혀 있지만, 제공된 `OnOffLightingCluster.cpp`의 `TimerFired`에는 이 시점에 켜는 동작이 없다.

#### 다른 클러스터와의 상태 연동

`SetOnOffWithTimeReset`은 `SetOnOff` 호출 후 다음을 적용한다.

- `on == false`이고 `mOnTime != 0`이면 `OnTime`을 `0`으로 설정
- `on == true`, `mOnTime == 0`, `mOffWaitTime != 0`이면 `OffWaitTime`을 `0`으로 설정

각 변경 시 타이머를 갱신하고 해당 속성 변경을 알린다. 헤더의 요약 주석보다 `.cpp`의 켜짐 처리 조건이 더 구체적이다.

### `OnOffEffectDelegate`

`TriggerEffect`는 효과 ID를 기준으로 분기한다.

| 효과 ID | 호출 |
|---|---|
| `OnOff::EffectIdentifierEnum::kDelayedAllOff` | `TriggerDelayedAllOff` |
| `OnOff::EffectIdentifierEnum::kDyingLight` | `TriggerDyingLight` |
| 그 외 | `Protocols::InteractionModel::Status::InvalidCommand` 반환 |

`effectVariant`는 각 효과의 열거형으로 변환하여 전달한다.

`TriggerDelayedAllOff`와 `TriggerDyingLight`의 기본 구현은 모두 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다. 제공된 기본 구현에는 실제 페이드 동작이 없다.

### 하위 호환 헤더

`src/app/clusters/on-off-server/on-off-server.h`는 코드 생성 클러스터 구현과의 하위 호환만을 위한 헤더이며, 다음 파일을 포함한다.

```cpp
#include "codegen/on-off-server.h" // nogncheck
```

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
