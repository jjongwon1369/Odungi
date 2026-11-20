---
entity: Refrigerator Alarm
ids: ['0x0057']
source_paths: ['data_model/1.7/clusters/RefrigeratorAlarm.xml', 'src/app/clusters/alarm-base-server/README.md', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h', 'src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h', 'src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Refrigerator Alarm

## 개요

Refrigerator Alarm은 냉장고 알람 구성을 위한 클러스터이며, 클러스터 ID는 `0x0057`이다. `Alarm Base`를 기반으로 하며, 제조사가 정의한 시간 동안 문이 열려 있는 상태를 `DoorOpen`으로 표현한다.

구현은 `AlarmBaseCluster`를 상속하는 `RefrigeratorAlarmCluster`와 코드 생성 데이터 모델을 연결하는 `CodegenIntegration`으로 구성된다.

## 스펙

출처: `data_model/1.7/clusters/RefrigeratorAlarm.xml`

### 클러스터 정보

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Refrigerator Alarm Cluster` |
| 클러스터 ID / 이름 | `0x0057` / `Refrigerator Alarm` |
| revision | `1` |
| revision 이력 | `Initial revision` |
| hierarchy | `derived` |
| baseCluster | `Alarm Base` |
| role | `application` |
| picsCode | `REFALM` |
| scope | `Endpoint` |

### 기능 및 명령 제약

| 구분 | 식별자 | 비트 / ID | 적합성 |
|---|---|---|---|
| 기능 | `Reset` (`RESET`) | 비트 `0` | `disallowConform` |
| 명령 | `ModifyEnabledAlarms` | `0x01` | `disallowConform` |

`Reset`은 알람 재설정 기능을 의미하지만, 이 클러스터에서는 허용되지 않는다. `ModifyEnabledAlarms` 역시 허용되지 않는다.

### 데이터 타입

| 타입 | 필드 | 비트 | 적합성 | 의미 |
|---|---|---|---|---|
| `AlarmBitmap` | `DoorOpen` | `0` | `mandatoryConform` | 제조사가 정의한 시간 동안 문이 열려 있음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Refrigerator Alarm` |
| domain | `Appliances` |
| code | `0x0057` |
| define | `REFRIGERATOR_ALARM_CLUSTER` |
| client / server | 모두 `true`, 각각 `tick="false"`, `init="false"` |
| globalAttribute | code `0xFFFD`, side `either`, value `1` |

`AlarmBitmap`은 `bitmap32`이며, `DoorOpen`의 마스크는 `0x01`이다.

### 속성

모든 속성은 `server` 측에 정의되며, 타입은 `AlarmBitmap`, 최댓값은 `0x00000001`이다.

| code | name | define |
|---|---|---|
| `0x0000` | `Mask` | `MASK` |
| `0x0002` | `State` | `STATE` |
| `0x0003` | `Supported` | `SUPPORTED` |

### 이벤트

`Notify`는 하나 이상의 알람 상태가 변경될 때 생성되어야 한다.

| 항목 | 값 |
|---|---|
| code | `0x00` |
| side | `server` |
| priority | `info` |

| 필드 ID | 이름 | 타입 | 최댓값 |
|---|---|---|---|
| `0` | `Active` | `AlarmBitmap` | `0x00000001` |
| `1` | `Inactive` | `AlarmBitmap` | `0x00000001` |
| `2` | `State` | `AlarmBitmap` | `0x00000001` |
| `3` | `Mask` | `AlarmBitmap` | `0x00000001` |

이 SDK XML에는 명령 정의가 없다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h` | `RefrigeratorAlarmCluster` 선언과 기반 클래스 초기화 |
| `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp` | `SendNotifyEvent` 구현 |
| `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h` | `RefrigeratorAlarmServer`, 클러스터 조회 및 속성 접근 API 선언 |
| `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp` | 클러스터 등록·해제, 기본값 적용 및 속성 접근 구현 |
| `src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h` | `app/clusters/refrigerator-alarm-server/CodegenIntegration.h` 포함 |

### 클러스터 클래스

`chip::app::Clusters`의 `RefrigeratorAlarmCluster`는 `AlarmBaseCluster`를 상속한다.

- `Config`는 `AlarmBaseCluster::Config`의 별칭이다.
- 생성자는 `endpointId`, `{ RefrigeratorAlarm::Id, RefrigeratorAlarm::kRevision }`, `config`를 기반 클래스에 전달한다.
- 클러스터별 이벤트 생성을 위해 `SendNotifyEvent`를 재정의한다.

### 등록과 초기값

`RefrigeratorAlarmIntegrationDelegate::CreateRegistration`은 다음 순서로 클러스터를 구성한다.

1. `Supported::GetDefault`가 `Status::Success`를 반환하면 해당 값을 `AlarmBase::AlarmMap`으로 변환한다. 그렇지 않으면 `supported`는 빈 초기값을 유지한다.
2. `RefrigeratorAlarmCluster::Config`를 구성한다.
   - `.delegate`: 슬롯의 `integrationDelegate`
   - `.feature`: 빈 `BitFlags<AlarmBase::Feature>()`
   - `.supported`: 위에서 준비한 값
   - `.supportsModifyEnabledAlarms`: `false`
3. 슬롯의 `cluster.Create(endpointId, config)`를 호출한다.
4. `Mask::GetDefault`가 성공하면 `SetMask`를 호출한다.
5. `State::GetDefault`가 성공하면 `SetState`를 호출한다.
6. `Registration()`을 반환한다.

초기화 과정에서 호출하는 `SetMask`와 `SetState`의 반환값은 검사하지 않는다.

### 수명주기 및 조회

- `kRefrigeratorAlarmFixedClusterCount`는 `RefrigeratorAlarm::StaticApplicationConfig::kFixedClusterConfig.size()`로 결정된다.
- `kRefrigeratorAlarmMaxClusterCount`는 고정 클러스터 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `static_assert`로 고정 클러스터 수가 `MATTER_DM_REFRIGERATOR_ALARM_CLUSTER_SERVER_ENDPOINT_COUNT`와 일치하고, 최대 클러스터 수가 `kEmberInvalidEndpointIndex` 이하인지 검사한다.
- `gRefrigeratorAlarmClusters`의 각 `RefrigeratorAlarmClusterSlot`은 `LazyRegisteredServerCluster<RefrigeratorAlarmCluster>`와 `AlarmBase::Delegate`를 보유한다.

| 함수 | 동작 |
|---|---|
| `MatterRefrigeratorAlarmClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterRefrigeratorAlarmClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindRegistration` | 클러스터가 생성되어 있으면 포인터, 아니면 `nullptr` 반환 |
| `ReleaseRegistration` | 슬롯의 `cluster.Destroy()` 호출 |
| `FindClusterOnEndpoint` | `CodegenClusterIntegration::FindClusterOnEndpoint`를 통해 클러스터 조회 |

등록 시 `.fetchFeatureMap`과 `.fetchOptionalAttributes`는 모두 `false`이다.

`MatterRefrigeratorAlarmPluginServerInitCallback`과 `MatterRefrigeratorAlarmPluginServerShutdownCallback`은 본문이 비어 있는 `__attribute__((weak))` 함수로 제공된다.

### 속성 접근 API

`chip::app::Clusters::RefrigeratorAlarm::Attributes`의 API는 실행 중인 클러스터 값에 접근한다. ZAP/ember 속성 저장소의 시작 값을 읽으려면 `app-common/zap-generated/attributes/Accessors.h`의 `GetDefault` 함수를 사용한다.

| 속성 네임스페이스 | API | 위임 대상 |
|---|---|---|
| `Mask` | `Get` / `Set` | `GetMaskValue` / `SetMaskValue` |
| `State` | `Get` / `Set` | `GetStateValue` / `SetStateValue` |
| `Supported` | `Get` | `GetSupportedValue` |

위임은 `RefrigeratorAlarmServer::Instance()`를 통해 이루어진다. `Supported`의 변경 API는 제공되지 않는다.

`RefrigeratorAlarmServer`의 접근 함수는 다음과 같이 동작한다.

- `FindClusterOnEndpoint`로 클러스터를 찾지 못하면 `Status::UnsupportedEndpoint`를 반환한다.
- 읽기는 `GetMask()`, `GetState()`, `GetSupported()`를 사용한다.
- 읽기 출력 포인터가 `nullptr`이면 값을 기록하지 않지만, 클러스터가 존재하면 `Status::Success`를 반환한다.
- 쓰기는 `SetMask()` 또는 `SetState()`의 반환값을 그대로 반환한다.
- `ToAlarmMap`과 `FromAlarmMap`은 `Raw()`를 이용해 `AlarmBase::AlarmMap`과 `BitMask<RefrigeratorAlarm::AlarmMap>` 사이를 변환한다.

### `Notify` 이벤트 생성

`RefrigeratorAlarmCluster::SendNotifyEvent`는 `mContext`가 `nullptr`이면 즉시 반환한다. 그 외에는 `RefrigeratorAlarm::Events::Notify::Type`을 구성한다.

| 이벤트 멤버 | 입력 |
|---|---|
| `.active` | `becameActive.Raw()` |
| `.inactive` | `becameInactive.Raw()` |
| `.state` | `newState.Raw()` |
| `.mask` | `mask.Raw()` |

각 값은 `BitMask<RefrigeratorAlarm::AlarmBitmap>`으로 변환된다. 이후 `mContext->interactionContext.eventsGenerator.GenerateEvent(event, mPath.mEndpointId)`를 호출한다.

## 관련 문서

### `src/app/clusters/alarm-base-server/README.md`

`Alarm Base`는 자체 클러스터 ID가 없는 의사 클러스터이며, `Dishwasher Alarm`과 `Refrigerator Alarm` 같은 알람 클러스터의 기반이다. 구체적인 클러스터는 `AlarmBaseCluster`를 상속하고 클러스터별 이벤트 생성을 제공한다.

#### 고정 속성 `Supported`와 `Latch`

문서는 `Alarm Base`의 공통 규칙을 다음과 같이 설명한다.

- `Supported`와 `Latch`는 고정 속성이다.
- `Supported`는 구현이 지원하는 알람을 나타내며, `Latch`는 `Reset` 기능이 있을 때 래치되는 알람 비트를 나타낸다.
- 값은 일반적으로 빌드 시 ZAP 또는 데이터 모델 기본값으로 결정된다.
- 클러스터 생성 시 `AlarmBaseCluster::Config`의 `.supported`와 `.latch`에서 한 번 초기화된다.
- `mSupported`와 `mLatch`는 `const` 멤버로 저장된다.
- `GetSupported()`와 `GetLatch()`는 읽기 전용 접근자이다.
- 해당 속성에 대한 `WriteAttribute`는 구현하지 않는다.

이는 기반 클러스터에 대한 설명이다. 제공된 Refrigerator Alarm SDK XML에는 `Latch`가 정의되어 있지 않으며, 스펙에서 `Reset`은 허용되지 않는다.

#### 마이그레이션과 제품 구성

기존 Ember 기반 `DishwasherAlarmServer`의 `SetSupportedValue()`와 `SetLatchValue()`는 고정 속성의 런타임 변경을 허용했기 때문에 `Alarm Base` 마이그레이션에서 제거되었다.

공통 구현에서 변경 가능한 런타임 상태는 다음 API로 다룬다.

- `SetMask()` / `GetMask()`
- `SetState()` / `GetState()`
- `ResetLatchedAlarms()` — `Reset` 기능이 활성화된 경우

제품의 `Supported` 또는 `Latch`를 변경하려면 ZAP / `.matter` 데이터 모델 구성을 수정하고, `CodegenIntegration`이 의도한 기본값을 클러스터 생성 시 `AlarmBaseCluster::Config`에 전달하도록 해야 한다.

## 관련 페이지

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
