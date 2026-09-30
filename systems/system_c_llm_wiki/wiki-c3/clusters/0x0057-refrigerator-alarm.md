---
entity: Refrigerator Alarm
ids: ['0x0057']
source_paths: ['data_model/1.7/clusters/RefrigeratorAlarm.xml', 'src/app/clusters/alarm-base-server/README.md', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h', 'src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h', 'src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Refrigerator Alarm

## 개요

`Refrigerator Alarm`은 냉장고 알람 구성을 위한 클러스터이며, 클러스터 ID는 `0x0057`이다. `Alarm Base`에서 파생되며, `DoorOpen` 알람을 정의한다.

구현은 `AlarmBaseCluster`를 상속하는 `RefrigeratorAlarmCluster`를 사용하고, 클러스터별 `Notify` 이벤트 생성을 제공한다. `Alarm Base` 자체는 고유 클러스터 ID가 없는 의사 클러스터이다.

## 스펙

출처: `data_model/1.7/clusters/RefrigeratorAlarm.xml`

### 기본 정의

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

| 구분 | 이름 | 식별자 | 적합성 |
|---|---|---|---|
| 기능 | `Reset` | bit `0`, code `RESET` | `disallowConform` |
| 명령 | `ModifyEnabledAlarms` | ID `0x01` | `disallowConform` |

`Reset`은 알람 재설정 기능이지만, 이 클러스터에서는 허용되지 않는다. `ModifyEnabledAlarms` 역시 허용되지 않는다.

### 데이터 타입

`AlarmBitmap`은 다음 비트를 정의한다.

| 이름 | bit | 적합성 | 의미 |
|---|---|---|---|
| `DoorOpen` | `0` | `mandatoryConform` | 냉장고 문이 제조업체에서 정의한 시간 동안 열려 있음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml`

### 클러스터 및 비트맵

| 항목 | 값 |
|---|---|
| 이름 | `Refrigerator Alarm` |
| domain | `Appliances` |
| code | `0x0057` |
| define | `REFRIGERATOR_ALARM_CLUSTER` |
| client / server | 모두 활성화, 각각 `tick="false"`, `init="false"` |
| globalAttribute | code `0xFFFD`, side `either`, value `1` |

`AlarmBitmap`의 기반 타입은 `bitmap32`이며, `DoorOpen`의 mask는 `0x01`이다.

### 속성

모든 속성은 side가 `server`이고 타입이 `AlarmBitmap`이다.

| code | 이름 | define | max |
|---|---|---|---|
| `0x0000` | `Mask` | `MASK` | `0x00000001` |
| `0x0002` | `State` | `STATE` | `0x00000001` |
| `0x0003` | `Supported` | `SUPPORTED` | `0x00000001` |

### 이벤트

`Notify`는 하나 이상의 알람 상태가 변경될 때 생성되어야 한다.

| 항목 | 값 |
|---|---|
| code | `0x00` |
| side | `server` |
| priority | `info` |

| 필드 id | 이름 | 타입 | max |
|---|---|---|---|
| `0` | `Active` | `AlarmBitmap` | `0x00000001` |
| `1` | `Inactive` | `AlarmBitmap` | `0x00000001` |
| `2` | `State` | `AlarmBitmap` | `0x00000001` |
| `3` | `Mask` | `AlarmBitmap` | `0x00000001` |

제공된 SDK XML에는 명령 정의가 없다.

## 구현

### 클래스 구조

출처:
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h`
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp`

`chip::app::Clusters`의 `RefrigeratorAlarmCluster`는 `AlarmBaseCluster`를 상속한다.

- `Config`는 `AlarmBaseCluster::Config`의 별칭이다.
- 생성자는 `endpointId`, `RefrigeratorAlarm::Id`, `RefrigeratorAlarm::kRevision`, `config`를 기반 클래스에 전달한다.
- `SendNotifyEvent`를 재정의하여 `RefrigeratorAlarm::Events::Notify::Type` 이벤트를 생성한다.

### 등록 및 초기화

출처: `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp`

`RefrigeratorAlarmClusterSlot`은 다음을 보관한다.

- `LazyRegisteredServerCluster<RefrigeratorAlarmCluster>` 타입의 `cluster`
- `AlarmBase::Delegate` 타입의 `integrationDelegate`

슬롯 배열 `gRefrigeratorAlarmClusters`의 크기는 고정 클러스터 수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합이다. `static_assert`로 다음을 검증한다.

- 고정 클러스터 수가 `MATTER_DM_REFRIGERATOR_ALARM_CLUSTER_SERVER_ENDPOINT_COUNT`와 일치한다.
- 최대 클러스터 수가 `kEmberInvalidEndpointIndex` 이하이다.

`RefrigeratorAlarmIntegrationDelegate`의 `CreateRegistration`은 다음 순서로 초기화한다.

1. `Supported::GetDefault`가 `Status::Success`를 반환하면 기본값을 `AlarmBase::AlarmMap`으로 변환한다. 실패하면 초기화된 빈 값을 유지한다.
2. `RefrigeratorAlarmCluster::Config`를 구성한다.
   - `.delegate`: 해당 슬롯의 `integrationDelegate`
   - `.feature`: 빈 `BitFlags<AlarmBase::Feature>()`
   - `.supported`: 앞서 준비한 값
   - `.supportsModifyEnabledAlarms`: `false`
3. 해당 슬롯에서 클러스터를 생성한다.
4. `Mask::GetDefault`가 성공하면 `SetMask`로 적용한다.
5. `State::GetDefault`가 성공하면 `SetState`로 적용한다.
6. 생성된 클러스터의 등록 정보를 반환한다.

| 함수 | 동작 |
|---|---|
| `MatterRefrigeratorAlarmClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterRefrigeratorAlarmClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | 지정한 Endpoint의 `RefrigeratorAlarmCluster` 조회 |
| `FindRegistration` | 클러스터가 생성되어 있으면 반환하고, 아니면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 슬롯의 클러스터에 `Destroy` 호출 |

등록 시 `.fetchFeatureMap`과 `.fetchOptionalAttributes`는 모두 `false`이다.

`MatterRefrigeratorAlarmPluginServerInitCallback`과 `MatterRefrigeratorAlarmPluginServerShutdownCallback`은 빈 weak 함수로 정의되어 있다.

### 속성 접근 API

출처:
- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h`
- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp`

`chip::app::Clusters::RefrigeratorAlarm`의 `Attributes`는 실행 중인 클러스터의 속성 접근 함수를 제공한다.

| 속성 | 접근 함수 | 위임 대상 |
|---|---|---|
| `Mask` | `Get`, `Set` | `GetMaskValue`, `SetMaskValue` |
| `State` | `Get`, `Set` | `GetStateValue`, `SetStateValue` |
| `Supported` | `Get` | `GetSupportedValue` |

위 함수들은 `RefrigeratorAlarmServer::Instance()`를 통해 접근한다.

- `GetMaskValue`, `GetStateValue`, `GetSupportedValue`는 클러스터의 `GetMask`, `GetState`, `GetSupported`를 호출한다.
- 클러스터를 찾지 못하면 `Status::UnsupportedEndpoint`를 반환한다.
- 조회 함수는 출력 포인터가 `nullptr`이면 값을 기록하지 않지만, 클러스터가 존재하면 `Status::Success`를 반환한다.
- `SetMaskValue`와 `SetStateValue`는 각각 `SetMask`와 `SetState`의 반환값을 전달한다.
- `ToAlarmMap`과 `FromAlarmMap`은 `Raw()` 값을 사용하여 `AlarmBase::AlarmMap`과 `BitMask<RefrigeratorAlarm::AlarmMap>` 사이를 변환한다.

시작 시점의 ZAP/ember 속성 저장소 기본값은 `app-common/zap-generated/attributes/Accessors.h`의 생성된 `GetDefault` 함수를 사용한다. 이는 실행 중인 클러스터에 접근하는 위 API와 구분된다.

`src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h`는 `app/clusters/refrigerator-alarm-server/CodegenIntegration.h`를 포함한다.

### `Notify` 이벤트 생성

`SendNotifyEvent`는 `mContext`가 `nullptr`이면 이벤트를 생성하지 않고 반환한다.

컨텍스트가 있으면 각 입력의 `Raw()` 값을 `BitMask<RefrigeratorAlarm::AlarmBitmap>`으로 변환하여 이벤트를 구성한다.

| 입력 | 이벤트 멤버 |
|---|---|
| `becameActive` | `active` |
| `becameInactive` | `inactive` |
| `newState` | `state` |
| `mask` | `mask` |

이후 `mContext->interactionContext.eventsGenerator.GenerateEvent(event, mPath.mEndpointId)`를 호출한다.

## 관련 문서

### `src/app/clusters/alarm-base-server/README.md`

`Alarm Base`와 파생 클러스터의 코드 기반 구현 및 고정 속성 정책을 설명한다.

- `Supported`와 `Latch`는 고정 속성이다.
  - `Supported`는 구현이 지원하는 알람을 나타낸다.
  - `Latch`는 `Reset` 기능이 있을 때 래치되는 알람 비트를 나타낸다.
- 값은 일반적으로 빌드 시 ZAP / 데이터 모델 기본값으로 결정되며, 서버 애플리케이션 API를 통해 런타임에 변경하지 않는다.
- `AlarmBaseCluster::Config`의 `.supported`, `.latch`에서 생성 시 한 번 초기화한다.
- `AlarmBaseCluster`의 `const` 멤버 `mSupported`, `mLatch`에 저장한다.
- 읽기 전용 접근자 `GetSupported()`와 `GetLatch()`를 제공하며, 해당 속성에 대한 `WriteAttribute`는 구현하지 않는다.

레거시 Ember 기반 `DishwasherAlarmServer`의 `SetSupportedValue()`와 `SetLatchValue()`는 고정 속성의 런타임 변경을 허용했기 때문에 `Alarm Base` 마이그레이션에서 제거되었다.

런타임 상태에는 `SetMask()` / `GetMask()`, `SetState()` / `GetState()`를 사용한다. `ResetLatchedAlarms()`는 `Reset` 기능이 활성화된 경우에 사용하며, `Refrigerator Alarm`의 스펙에서는 `Reset`이 허용되지 않는다.

제품의 `Supported` 또는 `Latch`를 변경하려면 ZAP / `.matter` 데이터 모델 설정을 수정하고, `CodegenIntegration`이 의도한 기본값을 클러스터 생성 시 `AlarmBaseCluster::Config`에 전달하도록 해야 한다.

## 관련 페이지

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
