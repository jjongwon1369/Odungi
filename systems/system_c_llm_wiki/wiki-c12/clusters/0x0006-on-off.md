---
entity: On/Off
ids: ['0x0006']
source_paths: ['data_model/1.7/clusters/OnOff.xml', 'src/app/clusters/on-off-server/OnOffCluster.cpp', 'src/app/clusters/on-off-server/OnOffCluster.h', 'src/app/clusters/on-off-server/OnOffDelegate.h', 'src/app/clusters/on-off-server/OnOffEffectDelegate.h', 'src/app/clusters/on-off-server/OnOffLightingCluster.cpp', 'src/app/clusters/on-off-server/OnOffLightingCluster.h', 'src/app/clusters/on-off-server/on-off-server.h', 'src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# On/Off

## 개요

`On/Off`는 장치를 `On`과 `Off` 상태 사이에서 전환하기 위한 속성과 명령을 제공한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `On/Off Cluster` |
| 클러스터 ID | `0x0006` |
| revision | `7` |
| 분류 | hierarchy=`base`, role=`application` |
| 범위 | `Endpoint` |
| PICS 코드 | `OO` |

제공된 구현은 다음과 같이 구분된다.

- `OnOffCluster`: 기본 상태 제어, 영속 저장, delegate 알림, scene 저장·적용을 제공한다. `Lighting`은 지원하지 않는다.
- `OnOffLightingCluster`: `OnOffCluster`를 확장하여 `Lighting` 속성, 효과 명령, 시간 제어, 시작 상태 처리를 제공한다.
- `OnOffDelegate`: 애플리케이션에 시작 상태와 상태 변경을 전달한다.
- `OnOffEffectDelegate`: 조명 효과 처리를 위한 인터페이스다.

## 스펙

출처: `data_model/1.7/clusters/OnOff.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가; CCB 1555 |
| `2` | ZLO 1.0: `StartUpOnOff` |
| `3` | Level Control 및 `Lighting` 기능과 함께 전역 속성 `FeatureMap` 지원 |
| `4` | 새로운 데이터 모델 형식과 표기법 |
| `5` | Dead Front 동작 및 관련 `FeatureMap` 항목 추가 |
| `6` | `OffOnly` 및 관련 `FeatureMap` 항목 추가 |
| `7` | `OnTime`, `OffWaitTime`에 Q quality 추가 |

### 기능

| bit | code | 이름 | 설명 | 선택 가능 조건 |
|---|---|---|---|---|
| `0` | `LT` | `Lighting` | 조명 애플리케이션 지원 동작 | `OFFONLY` 미사용 |
| `1` | `DF` | `DeadFrontBehavior` | Dead Front 동작 | `OFFONLY` 미사용 |
| `2` | `OFFONLY` | `OffOnly` | `OffOnly` 기능 지원 | `LT`, `DF` 모두 미사용 |

`OFFONLY`는 `LT` 또는 `DF`와 함께 사용할 수 없다.

### 데이터 타입

#### `DelayedAllOffEffectVariantEnum`

| 값 | 이름 | 동작 |
|---|---|---|
| `0x00` | `DelayedOffFastFade` | 0.8초 동안 서서히 꺼짐 |
| `0x01` | `NoFade` | 페이드 없음 |
| `0x02` | `DelayedOffSlowFade` | 0.8초 동안 50% 어두워진 후 12초 동안 서서히 꺼짐 |

#### `DyingLightEffectVariantEnum`

| 값 | 이름 | 동작 |
|---|---|---|
| `0x00` | `DyingLightFadeOff` | 0.5초 동안 20% 밝아진 후 1초 동안 서서히 꺼짐 |

#### `EffectIdentifierEnum`

| 값 | 이름 |
|---|---|
| `0x00` | `DelayedAllOff` |
| `0x01` | `DyingLight` |

#### `StartUpOnOffEnum`

| 값 | 이름 | 동작 |
|---|---|---|
| `0` | `Off` | `OnOff`를 `FALSE`로 설정 |
| `1` | `On` | `OnOff`를 `TRUE`로 설정 |
| `2` | `Toggle` | 이전 `OnOff`가 `FALSE`이면 `TRUE`, `TRUE`이면 `FALSE`로 전환 |

#### `OnOffControlBitmap`

| bit | 이름 | 의미 |
|---|---|---|
| `0` | `AcceptOnlyWhenOn` | `On` 상태일 때만 명령을 수락함을 나타냄 |

위 enum 항목과 bitmap 필드는 모두 필수로 정의되어 있다.

### 속성

모든 속성은 읽기를 지원하며 읽기 권한은 `view`다.

| ID | 이름 | 타입 | 쓰기 권한 | 필수 조건 | quality |
|---|---|---|---|---|---|
| `0x0000` | `OnOff` | `bool` | 쓰기 미정의 | 항상 | `scene="true"`, `persistence="nonVolatile"` |
| `0x4000` | `GlobalSceneControl` | `bool` | 쓰기 미정의 | `LT` | — |
| `0x4001` | `OnTime` | `uint16` | `operate` | `LT` | `quieterReporting="true"` |
| `0x4002` | `OffWaitTime` | `uint16` | `operate` | `LT` | `quieterReporting="true"` |
| `0x4003` | `StartUpOnOff` | `StartUpOnOffEnum` | `manage` | `LT` | `nullable="true"`, `persistence="nonVolatile"` |

`StartUpOnOff`의 constraint에는 빈 `desc`만 있으며, 제공된 스펙 XML에 추가 제약 설명은 없다.

### 명령

모든 명령은 `direction="commandToServer"`, `response="Y"`, `invokePrivilege="operate"`로 정의된다.

| ID | 이름 | 필수 조건 | 필드 |
|---|---|---|---|
| `0x00` | `Off` | 항상 | 없음 |
| `0x01` | `On` | `OFFONLY` 미사용 | 없음 |
| `0x02` | `Toggle` | `OFFONLY` 미사용 | 없음 |
| `0x40` | `OffWithEffect` | `LT` | `EffectIdentifier`, `EffectVariant` |
| `0x41` | `OnWithRecallGlobalScene` | `LT` | 없음 |
| `0x42` | `OnWithTimedOff` | `LT` | `OnOffControl`, `OnTime`, `OffWaitTime` |

#### 명령 필드

모든 필드는 필수다.

| 명령 | field ID | 이름 | 타입 | 제약 |
|---|---|---|---|---|
| `OffWithEffect` | `0` | `EffectIdentifier` | `EffectIdentifierEnum` | 빈 `desc` |
| `OffWithEffect` | `1` | `EffectVariant` | `enum8` | 빈 `desc` |
| `OnWithTimedOff` | `0` | `OnOffControl` | `OnOffControlBitmap` | `0`부터 `1`까지 |
| `OnWithTimedOff` | `1` | `OnTime` | `uint16` | 최대 `0xFFFE` |
| `OnWithTimedOff` | `2` | `OffWaitTime` | `uint16` | 최대 `0xFFFE` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/onoff-cluster.xml`

### 생성 정보와 클러스터 설정

- Alchemy가 생성한 XML이며 직접 편집하지 않도록 표시되어 있다.
- 생성 원본: `src/app_clusters/OnOff.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

| 항목 | 정의 |
|---|---|
| 이름 | `On/Off` |
| domain | `General` |
| code | `0x0006` |
| define | `ON_OFF_CLUSTER` |
| client | 활성화, `init="false"`, `tick="false"` |
| server | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | `side="either"`, code=`0xFFFD`, value=`7` |

### 타입 매핑

| 타입 | SDK 표현 |
|---|---|
| `StartUpOnOffEnum` | `enum8`: `Off`=`0x00`, `On`=`0x01`, `Toggle`=`0x02` |
| `EffectIdentifierEnum` | `enum8`: `DelayedAllOff`=`0x00`, `DyingLight`=`0x01` |
| `DelayedAllOffEffectVariantEnum` | `enum8`: `DelayedOffFastFade`=`0x00`, `NoFade`=`0x01`, `DelayedOffSlowFade`=`0x02` |
| `DyingLightEffectVariantEnum` | `enum8`: `DyingLightFadeOff`=`0x00` |
| `OnOffControlBitmap` | `bitmap8`: `AcceptOnlyWhenOn`의 mask=`0x01` |

### 속성 정의

모든 속성은 `side="server"`다.

| code | 이름 | define | SDK 타입 | 추가 설정 |
|---|---|---|---|---|
| `0x0000` | `OnOff` | `ON_OFF` | `boolean` | — |
| `0x4000` | `GlobalSceneControl` | `GLOBAL_SCENE_CONTROL` | `boolean` | `optional="true"` |
| `0x4001` | `OnTime` | `ON_TIME` | `int16u` | `writable="true"`, `optional="true"` |
| `0x4002` | `OffWaitTime` | `OFF_WAIT_TIME` | `int16u` | `writable="true"`, `optional="true"` |
| `0x4003` | `StartUpOnOff` | `START_UP_ON_OFF` | `StartUpOnOffEnum` | `max="2"`, `isNullable="true"`, `writable="true"`, `optional="true"`, 쓰기 권한 `manage` |

`optional="true"`로 표시된 위 속성에는 모두 `LT`에 대한 `mandatoryConform`이 함께 정의되어 있다.

### 명령 정의

- 모든 명령은 `source="client"`다.
- `Off`는 항상 필수다.
- `On`, `Toggle`은 `optional="true"`이지만 `OFFONLY` 미사용 시 필수다.
- `OffWithEffect`, `OnWithRecallGlobalScene`, `OnWithTimedOff`는 `optional="true"`이며 `LT` 사용 시 필수다.
- `OffWithEffect.EffectIdentifier`의 최대값은 `0x01`이다.
- `OnWithTimedOff.OnOffControl`의 최대값은 `1`이다.
- `OnWithTimedOff.OnTime`, `OnWithTimedOff.OffWaitTime`은 `int16u`이며 최대값은 `0xFFFE`다.

SDK 설명에서 `OnWithTimedOff`는 지정된 시간 동안 장치를 켜고, 이후 꺼졌을 때 보호 대기 시간 중 수신하는 추가 `OnWithTimedOff` 명령이 장치를 다시 켜지 못하도록 하는 명령이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/on-off-server/OnOffCluster.h` | 기본 클러스터 인터페이스, 설정, scene 타이머 선언 |
| `src/app/clusters/on-off-server/OnOffCluster.cpp` | 기본 속성·명령, 영속 저장, scene 처리 |
| `src/app/clusters/on-off-server/OnOffDelegate.h` | 시작 및 상태 변경 알림 인터페이스 |
| `src/app/clusters/on-off-server/OnOffEffectDelegate.h` | 조명 효과 처리 인터페이스 |
| `src/app/clusters/on-off-server/OnOffLightingCluster.h` | 조명 확장 인터페이스와 상태 선언 |
| `src/app/clusters/on-off-server/OnOffLightingCluster.cpp` | 조명 속성·명령, 시작 상태, 시간 제어 |
| `src/app/clusters/on-off-server/on-off-server.h` | codegen 구현에 대한 하위 호환 헤더 |

### `OnOffCluster`

`chip::app::Clusters`에 정의되며 `DefaultServerCluster`와 `scenes::DefaultSceneHandlerImpl`을 상속한다.

#### 설정과 기능 검증

`Context`는 다음 값을 제공한다.

- `timerDelegate`: `TimerDelegate` 참조
- `featureMap`: 기본값 `{}`
- `defaults`: `Defaults`이며 `onOff`를 포함

일반 생성자는 지원 기능을 `Feature::kDeadFrontBehavior`, `Feature::kOffOnly`로 지정한다. 파생 클래스용 생성자는 `supportedFeatures`를 별도로 받는다.

생성 시 `VerifyOrDie`로 다음을 검사한다.

1. `context.featureMap`이 `supportedFeatures`의 부분집합인지 확인한다.
2. `Feature::kOffOnly`가 설정되었다면 다른 기능이 없는지 확인한다.

#### 시작 및 상태 변경

`Startup`은 다음 순서로 처리한다.

1. `DefaultServerCluster::Startup` 호출
2. `AttributePersistence::LoadNativeEndianValue`로 `OnOff` 복원
3. 등록된 모든 delegate에 `OnOffStartup(mOnOff)` 호출

저장값이 없을 때 사용할 값으로 현재 `mOnOff`가 전달된다.

`SetOnOff(bool on)`은 다음 순서로 처리한다.

1. `mSceneTimer.Cancel()` 호출
2. 기존 상태와 같으면 `CHIP_NO_ERROR` 반환
3. `mOnOff` 변경 및 `NotifyAttributeChanged(Attributes::OnOff::Id)` 호출
4. `StoreNativeEndianValue`로 영속 저장 시도
5. 모든 delegate의 `OnOnOffChanged(mOnOff)` 호출

영속 저장 오류는 `LogErrorOnFailure`로 기록하며, 이 경로의 최종 반환값은 `CHIP_NO_ERROR`다. 상태가 같아도 scene 타이머 취소는 먼저 수행된다.

#### 속성 및 명령 처리

| 함수 | 동작 |
|---|---|
| `Attributes` | `Attributes::kMandatoryMetadata` 추가 |
| `ReadAttribute` | `ClusterRevision`에 `kRevision`, `FeatureMap`에 `mFeatureMap.Raw()`, `OnOff`에 `mOnOff` 인코딩 |
| `AcceptedCommands` | `Feature::kOffOnly`이면 `Off`만, 그렇지 않으면 `Off`, `On`, `Toggle` 반환 |
| `InvokeCommand` | `Off` → `SetOnOff(false)`, `On` → `SetOnOff(true)`, `Toggle` → `SetOnOff(!mOnOff)` |
| `GetOnOff` | 현재 `mOnOff` 반환 |
| `GetFeatureMap` | 현재 `mFeatureMap` 반환 |

지원하지 않는 읽기는 `UnsupportedAttribute`, 명령은 `UnsupportedCommand`를 반환한다.

`InvokeCommand` 내부에서 `OffOnly`를 다시 검사하지는 않는다. 코드 주석에 따르면 Interaction Model이 `AcceptedCommands` 목록으로 이를 검증한다.

### delegate 인터페이스

#### `OnOffDelegate`

`IntrusiveListNodeBase<IntrusiveMode::AutoUnlink>`를 상속한다.

| 함수 | 의미 |
|---|---|
| `OnOffStartup(bool on)` | 시작 시 결정된 상태 전달 |
| `OnOnOffChanged(bool on)` | `OnOff` 변경 알림. delegate가 하드웨어 상태를 새 값에 맞추도록 요구 |

`OnOnOffChanged`는 시작 처리의 일부로 호출되지 않는다.

`OnOffCluster`는 여러 delegate를 지원하며 `AddDelegate`, `RemoveDelegate`로 관리한다.

#### `OnOffEffectDelegate`

| 함수 | 기본 동작 |
|---|---|
| `TriggerEffect` | `effectId`에 따라 효과별 함수 호출 |
| `TriggerDelayedAllOff` | `UnsupportedCommand` 반환 |
| `TriggerDyingLight` | `UnsupportedCommand` 반환 |

`TriggerEffect`는 다음과 같이 분기한다.

- `OnOff::EffectIdentifierEnum::kDelayedAllOff`: `effectVariant`를 `OnOff::DelayedAllOffEffectVariantEnum`으로 변환하여 `TriggerDelayedAllOff` 호출
- `OnOff::EffectIdentifierEnum::kDyingLight`: `effectVariant`를 `OnOff::DyingLightEffectVariantEnum`으로 변환하여 `TriggerDyingLight` 호출
- 그 외: `InvalidCommand` 반환

기본 구현에는 실제 페이드 동작이 없다.

### scene 저장과 적용

`OnOffValidator::Validate`는 클러스터 ID가 `Clusters::OnOff::Id`, 속성 ID가 `Attributes::OnOff::Id`인지 검사한다.

| 함수 | 동작 |
|---|---|
| `SupportsCluster` | 클러스터 ID와 endpoint가 해당 인스턴스에 일치하는지 확인 |
| `SerializeSave` | `OnOff` 하나를 `AttributeValuePairStruct`의 `valueUnsigned8`에 저장하고 인코딩 |
| `ApplyScene` | 목록을 디코딩하고 `OnOff` 값 적용 |
| `IsSceneTransitionPending` | `mSceneTimer`의 활성 여부 반환 |

`ApplyScene`은 각 항목에 대해 다음을 검사한다.

- `attributeID == Attributes::OnOff::Id`
- `valueUnsigned8.HasValue()`

값은 `bool`로 변환한다. `timeMs > 0`이면 기존 scene 타이머를 취소하고 새 타이머를 시작하며, 그렇지 않으면 즉시 `SetOnOff`를 호출한다.

`SceneTransitionTimer::TimerFired`는 저장된 목표값으로 `SetOnOff`를 호출한다. 기본 클러스터 소멸자는 scene 타이머를 취소하고 delegate 목록을 비운다.

### `OnOffLightingCluster`

`OnOffCluster`와 `TimerContext`를 상속한다.

#### 설정과 초기값

| 항목 | 정의 또는 초기값 |
|---|---|
| 지원 기능 | `Feature::kLighting`, `Feature::kDeadFrontBehavior` |
| `Context.timerDelegate` | 필수 참조 |
| `Context.effectDelegate` | 필수 `OnOffEffectDelegate` 참조 |
| `Context.scenesIntegrationDelegate` | 기본값 `nullptr` |
| `Context.featureMap` | 기본값 `OnOff::Feature::kLighting` |
| `Context.startupType` | 기본값 `StartupType::kRegular` |
| `Defaults.onOff` | `bool onOff{}` |
| `Defaults.startupOnOff` | `DataModel::Nullable<OnOff::StartUpOnOffEnum>` |
| `mGlobalSceneControl` | `true` |
| `mOnTime` | `0` |
| `mOffWaitTime` | `0` |
| `kValueDeltaReportTrigger` | `10` |

조명용 속성 네 개를 기본 속성 목록에 추가하고, 스펙에 정의된 명령 여섯 개를 모두 수락 목록에 포함한다.

#### 시작 상태

`Startup`은 최종 상태를 delegate에 전달하기 위해 `OnOffCluster::Startup` 대신 `DefaultServerCluster::Startup`을 직접 호출한다.

1. 저장된 `OnOff`, `StartUpOnOff`를 읽는다.
2. `mStartupType != StartupType::kOTA`이고 `StartUpOnOff`가 null이 아니면 다음 동작을 적용한다.
   - `StartUpOnOffEnum::kOff`: 꺼짐
   - `StartUpOnOffEnum::kOn`: 켜짐
   - `StartUpOnOffEnum::kToggle`: 기존 상태 반전
   - 그 외: 기존 상태 유지
3. 상태가 변경되면 변경된 `OnOff`를 영속 저장한다.
4. 모든 delegate에 `OnOffStartup(mOnOff)`를 호출한다.

`StartupType::kOTA`에서는 `StartUpOnOff` 동작을 적용하지 않고 복원된 `OnOff`를 유지한다.

#### 속성 읽기·쓰기

- `ReadAttribute`는 `GlobalSceneControl`, `OnTime`, `OffWaitTime`, `StartUpOnOff`를 처리하고 나머지는 기본 클래스에 위임한다.
- `WriteAttribute`는 `WriteImpl` 결과를 `NotifyAttributeChangedIfSuccess`에 전달한다.
- `WriteImpl`:
  - `OnTime`, `OffWaitTime`: `uint16_t`로 디코딩하고 변경 시 `UpdateTimer` 호출
  - 동일한 값: `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp` 반환
  - `StartUpOnOff`: `DecodeAndStoreNativeEndianValue`로 디코딩 및 저장
  - 그 외: `UnsupportedWrite` 반환

직접 접근 API는 `GetOnTime`, `SetOnTime`, `GetOffWaitTime`, `SetOffWaitTime`, `GetStartupOnOff`, `SetStartupOnOff`다.

`SetOnTime`, `SetOffWaitTime`은 값이 바뀌었을 때 이전 값과의 차이가 `kValueDeltaReportTrigger`보다 크거나 새 값이 `0`이면 속성 변경을 알린다. 이후 값을 설정하고 `UpdateTimer`를 호출한다.

`SetStartupOnOff`는 값 변경을 반영하고, `mContext != nullptr`이면 영속 저장한다.

#### 기본 명령의 조명 부수 효과

| 처리 함수 | 동작 |
|---|---|
| `HandleOff` | `SetOnOffFromCommand(false)` 호출, `OnTime`을 `0`으로 설정, 타이머 갱신 |
| `HandleOn` | `SetOnOffFromCommand(true)` 호출, `GlobalSceneControl`을 `true`로 설정, `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정, 타이머 갱신 |
| `HandleToggle` | 현재 상태에 따라 `HandleOff` 또는 `HandleOn` 호출 |

`SetOnOffFromCommand`는 실제 상태 변경이 있을 때만 다음을 수행한다.

- 켜질 때 `SetOffWaitTime(0)`
- 꺼질 때 `SetOnTime(0)`
- 이후 `SetOnOff(on)` 호출

#### `OffWithEffect`

`HandleOffWithEffect`는 명령을 디코딩한 뒤 다음과 같이 처리한다.

- `mGlobalSceneControl == true`:
  1. `mScenesIntegrationDelegate`가 있으면 요청의 `fabricIndex`로 `StoreCurrentGlobalScene` 호출
  2. `mEffectDelegate.TriggerEffect` 호출
  3. 효과 처리 실패 시 해당 상태 반환
  4. `GlobalSceneControl`을 `false`로 설정
  5. `SetOnOffFromCommand(false)` 호출
  6. `OnTime`을 `0`으로 설정하고 타이머 갱신
- `mGlobalSceneControl == false`: `HandleOff` 호출

`StoreCurrentGlobalScene` 오류는 기록하고 처리를 계속한다.

#### `OnWithRecallGlobalScene`

`HandleOnWithRecallGlobalScene`은 다음과 같이 처리한다.

- `mGlobalSceneControl == true`이면 추가 동작 없이 `Success` 반환
- 그 외:
  - delegate가 있으면 요청의 `fabricIndex`로 `RecallGlobalScene` 호출
  - scene 복원 실패 또는 delegate 부재 시 `SetOnOffFromCommand(true)` 호출
  - `GlobalSceneControl`을 `true`로 설정
  - `OnTime == 0`이면 `OffWaitTime`을 `0`으로 설정
  - 타이머 갱신

scene 복원에 성공한 경우 이 함수에서 별도로 `SetOnOffFromCommand(true)`를 호출하지 않는다.

#### `OnWithTimedOff`

`HandleOnWithTimedOff`는 다음을 검증한다.

- `commandData.onTime <= 0xFFFE`
- `commandData.offWaitTime <= 0xFFFE`

범위를 초과하면 `ConstraintError`를 반환한다.

`OnOffControlBitmap::kAcceptOnlyWhenOn`이 설정되었는데 장치가 꺼져 있으면 상태를 변경하지 않고 `Success`를 반환한다.

꺼진 상태이고 `mOffWaitTime == 0`이면 `SetOnOff(true)`를 직접 호출하고 `GlobalSceneControl`을 `true`로 설정한다. 시간 값은 명령 수신 전 상태에 따라 다음과 같이 갱신한다.

| 수신 전 상태 | 처리 |
|---|---|
| 켜짐, `mOnTime > 0` | `OnTime`을 기존 값과 요청값의 최댓값으로 설정하고 `OffWaitTime`을 요청값으로 설정 |
| 켜짐, `mOnTime == 0` | `OnTime`, `OffWaitTime`을 요청값으로 설정 |
| 꺼짐, `mOffWaitTime > 0` | 요청의 `OnTime`은 무시하고 `OffWaitTime`을 기존 값과 요청값의 최솟값으로 설정 |
| 꺼짐, `mOffWaitTime == 0` | `OnTime`, `OffWaitTime`을 요청값으로 설정 |

마지막에 `UpdateTimer`를 호출한다.

#### 시간 제어 및 보고

`UpdateTimer`는 기존 타이머를 취소한 후 다음 조건에서 `100`ms 타이머를 시작한다.

- 켜진 상태: `mOnTime`이 `0`도 `0xFFFF`도 아님
- 꺼진 상태: `mOffWaitTime`이 `0`도 `0xFFFF`도 아님

`TimerFired`의 실제 동작은 다음과 같다.

| 상태 | 처리 |
|---|---|
| 켜짐 | `mOnTime` 감소. `0`이 아니면 타이머 재설정 |
| 켜짐에서 `mOnTime == 0` 도달 | `OnTime` 변경 알림, `SetOffWaitTime(0)`, `SetOnOff(false)` |
| 꺼짐 | `mOffWaitTime` 감소. `0` 도달 시 변경 알림 후 `UpdateTimer` 호출 |

감소 중에는 각 tick마다 변경을 알리지 않고 `0` 도달 시 알린다. 조명 클러스터 소멸자는 자신의 타이머를 취소한다.

> `OnOffLightingCluster.h`의 상태 설명 주석은 `TIMED_OFF`에서 `mOffWaitTime`이 `0`이 되면 켜진다고 설명하지만, 제공된 `TimerFired` 구현에는 이때 장치를 켜는 호출이 없다.

#### 다른 클러스터와의 연동

`SetOnOffWithTimeReset(bool on)`은 먼저 `SetOnOff(on)`을 호출하고 다음 조건을 처리한다.

- `on == false`이고 `mOnTime != 0`: `OnTime`을 `0`으로 설정하고 타이머 갱신 및 변경 알림
- `on == true`, `mOnTime == 0`, `mOffWaitTime != 0`: `OffWaitTime`을 `0`으로 설정하고 타이머 갱신 및 변경 알림

이 함수의 구현 주석은 Level Control 명령과의 연동 요구를 설명한다. 헤더의 요약과 달리, 실제 구현에서 켜질 때의 `OffWaitTime` 초기화에는 `mOnTime == 0` 조건이 있다.

### 하위 호환 헤더

`src/app/clusters/on-off-server/on-off-server.h`는 codegen 클러스터 구현과의 하위 호환만을 위해 다음 헤더를 포함한다.

```cpp
#include "codegen/on-off-server.h" // nogncheck
```

## 관련 페이지

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md)
- [Cook Surface](../device-types/cook-surface.md)
- [Cooktop](../device-types/cooktop.md)
- [Dishwasher](../device-types/dishwasher.md)
- [Humidity Conditioner](../device-types/humidity-conditioner.md)
- [Laundry Dryer](../device-types/laundry-dryer.md)
- [Laundry Washer](../device-types/laundry-washer.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
