---
entity: Refrigerator Alarm
ids: ['0x0057']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml', 'src/app/clusters/alarm-base-server/README.md', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h', 'src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp', 'src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp', 'src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h', 'data_model/1.7/clusters/RefrigeratorAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Refrigerator Alarm

## 개요

Refrigerator Alarm은 냉장고 알람 구성을 위한 클러스터이며, `Alarm Base`에서 파생된다. 제공된 정의에는 문 열림 알람인 `DoorOpen`, 알람 속성 `Mask`, `State`, `Supported`, 상태 변경 이벤트 `Notify`가 포함된다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0057` |
| 리비전 | `1` |
| 기반 클러스터 | `Alarm Base` |
| PICS 코드 | `REFALM` |
| 범위 | `Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/RefrigeratorAlarm.xml`

### 분류 및 리비전

- 이름: `Refrigerator Alarm Cluster`
- 클러스터 ID에 연결된 이름: `Refrigerator Alarm`
- 분류: `hierarchy="derived"`, `baseCluster="Alarm Base"`, `role="application"`
- 리비전 `1`: `Initial revision`

### 데이터 타입

`AlarmBitmap`에는 다음 필수 비트가 정의되어 있다.

| 이름 | 비트 | 적합성 | 의미 |
|---|---|---|---|
| `DoorOpen` | `0` | `mandatoryConform` | 냉장고 문이 제조사가 정의한 시간 동안 열린 상태 |

### 기능 및 명령 제한

| 구분 | 이름 | 비트 또는 ID | 적합성 |
|---|---|---|---|
| 기능 | `Reset` | 비트 `0`, 코드 `RESET` | `disallowConform` |
| 명령 | `ModifyEnabledAlarms` | `0x01` | `disallowConform` |

`Reset` 기능과 `ModifyEnabledAlarms` 명령은 이 클러스터에서 허용되지 않는다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/refrigerator-alarm.xml`

이 파일은 Alchemy가 생성한 XML이며, 직접 수정하지 않도록 표시되어 있다.

- 생성 원본: `src/app_clusters/RefrigeratorAlarm.adoc`
- Git: `0.9-fall2025`
- 클러스터 도메인: `Appliances`
- 클러스터 define: `REFRIGERATOR_ALARM_CLUSTER`
- 클라이언트와 서버 모두 활성화되어 있으며, 각각 `tick="false"`, `init="false"`로 선언되어 있다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="1"`로 정의된다.

### `AlarmBitmap`

| 타입 | 필드 | 마스크 |
|---|---|---|
| `bitmap32` | `DoorOpen` | `0x01` |

### 속성

모든 속성은 `side="server"`이며, 타입은 `AlarmBitmap`, 최댓값은 `0x00000001`이다.

| ID | 이름 | define |
|---|---|---|
| `0x0000` | `Mask` | `MASK` |
| `0x0002` | `State` | `STATE` |
| `0x0003` | `Supported` | `SUPPORTED` |

### `Notify` 이벤트

- ID: `0x00`
- 발생 측: `server`
- 우선순위: `info`
- 하나 이상의 알람 상태가 변경되면 생성해야 한다.

| 필드 ID | 이름 | 타입 | 최댓값 |
|---|---|---|---|
| `0` | `Active` | `AlarmBitmap` | `0x00000001` |
| `1` | `Inactive` | `AlarmBitmap` | `0x00000001` |
| `2` | `State` | `AlarmBitmap` | `0x00000001` |
| `3` | `Mask` | `AlarmBitmap` | `0x00000001` |

## 구현

### 클래스 구조

출처:

- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h`
- `src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp`

`chip::app::Clusters`의 `RefrigeratorAlarmCluster`는 `AlarmBaseCluster`를 상속한다.

- `Config`는 `AlarmBaseCluster::Config`의 별칭이다.
- 생성자는 `endpointId`, `{ RefrigeratorAlarm::Id, RefrigeratorAlarm::kRevision }`, `config`를 기반 클래스에 전달한다.
- 클러스터별 이벤트 생성을 위해 `SendNotifyEvent`를 재정의한다.

### 등록 및 초기화

출처:

- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.h`
- `src/app/clusters/refrigerator-alarm-server/CodegenIntegration.cpp`

`RefrigeratorAlarmClusterSlot`은 다음 요소를 보관한다.

- `LazyRegisteredServerCluster<RefrigeratorAlarmCluster>` 타입의 `cluster`
- `AlarmBase::Delegate` 타입의 `integrationDelegate`

저장소 `gRefrigeratorAlarmClusters`의 크기는 고정 클러스터 수와 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`의 합이다. `static_assert`로 고정 클러스터 수가 `MATTER_DM_REFRIGERATOR_ALARM_CLUSTER_SERVER_ENDPOINT_COUNT`와 일치하는지, 전체 크기가 `kEmberInvalidEndpointIndex` 이하인지 검사한다.

`RefrigeratorAlarmIntegrationDelegate::CreateRegistration`의 처리 순서는 다음과 같다.

1. `Supported::GetDefault`가 `Status::Success`를 반환하면 기본값을 `AlarmBase::AlarmMap`으로 변환한다. 실패하면 값 초기화된 `supported`를 유지한다.
2. 다음 설정으로 `RefrigeratorAlarmCluster::Config`를 구성한다.
   - `.delegate`: 해당 슬롯의 `integrationDelegate`
   - `.feature`: `BitFlags<AlarmBase::Feature>()`
   - `.supported`: 앞에서 준비한 값
   - `.supportsModifyEnabledAlarms`: `false`
3. `cluster.Create(endpointId, config)`로 클러스터를 생성한다.
4. `Mask::GetDefault`가 성공하면 `SetMask`로 기본값을 적용한다.
5. `State::GetDefault`가 성공하면 `SetState`로 기본값을 적용한다.
6. `Registration()`을 반환한다.

`FindRegistration`은 생성되지 않은 슬롯에 대해 `nullptr`를 반환하고, `ReleaseRegistration`은 `Destroy()`를 호출한다.

| 함수 | 역할 |
|---|---|
| `MatterRefrigeratorAlarmClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterRefrigeratorAlarmClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | 엔드포인트의 `RefrigeratorAlarmCluster` 조회 |
| `MatterRefrigeratorAlarmPluginServerInitCallback` | 빈 weak 콜백 |
| `MatterRefrigeratorAlarmPluginServerShutdownCallback` | 빈 weak 콜백 |

등록 시 `.fetchFeatureMap`과 `.fetchOptionalAttributes`는 모두 `false`이다.

### 속성 접근 API

`RefrigeratorAlarmServer::Instance()`는 정적 인스턴스를 반환한다.

`chip::app::Clusters::RefrigeratorAlarm`의 `Attributes` 접근 함수는 다음과 같이 `RefrigeratorAlarmServer`로 위임한다.

| 속성 | 읽기 함수 → 위임 대상 | 설정 함수 → 위임 대상 |
|---|---|---|
| `Mask` | `Mask::Get` → `GetMaskValue` | `Mask::Set` → `SetMaskValue` |
| `State` | `State::Get` → `GetStateValue` | `State::Set` → `SetStateValue` |
| `Supported` | `Supported::Get` → `GetSupportedValue` | 제공되지 않음 |

- 각 서버 접근 함수는 `FindClusterOnEndpoint`로 클러스터를 찾으며, 없으면 `Status::UnsupportedEndpoint`를 반환한다.
- 읽기 함수는 출력 포인터가 `nullptr`가 아닐 때만 값을 기록한다. 클러스터가 존재하면 출력 포인터가 `nullptr`여도 `Status::Success`를 반환한다.
- 설정 함수는 `SetMask` 또는 `SetState`의 반환값을 그대로 반환한다.
- `ToAlarmMap`과 `FromAlarmMap`은 `Raw()`를 사용해 `AlarmBase::AlarmMap`과 `BitMask<RefrigeratorAlarm::AlarmMap>` 사이를 변환한다.

이 API는 실행 중인 code-driven 서버 클러스터의 속성에 접근한다. ZAP/ember 속성 저장소의 시작 기본값은 `app-common/zap-generated/attributes/Accessors.h`의 생성된 `GetDefault` 함수로 읽는다.

`src/app/clusters/refrigerator-alarm-server/refrigerator-alarm-server.h`는 `app/clusters/refrigerator-alarm-server/CodegenIntegration.h`를 포함한다.

### `Notify` 이벤트 생성

`RefrigeratorAlarmCluster::SendNotifyEvent`는 `mContext`가 `nullptr`이면 이벤트를 생성하지 않고 반환한다.

그 외에는 `RefrigeratorAlarm::Events::Notify::Type`을 다음과 같이 구성한다. 각 값은 `Raw()`를 통해 `BitMask<RefrigeratorAlarm::AlarmBitmap>`으로 변환된다.

| 인자 | 이벤트 멤버 |
|---|---|
| `becameActive` | `.active` |
| `becameInactive` | `.inactive` |
| `newState` | `.state` |
| `mask` | `.mask` |

이후 `mContext->interactionContext.eventsGenerator.GenerateEvent(event, mPath.mEndpointId)`를 호출한다.

## 관련 문서

### `Alarm Base`와 고정 속성

출처: `src/app/clusters/alarm-base-server/README.md`

`Alarm Base`는 자체 클러스터 ID가 없는 가상 클러스터이며, `Dishwasher Alarm`과 `Refrigerator Alarm` 같은 알람 클러스터의 기반으로 사용된다. 구체적인 클러스터는 `AlarmBaseCluster`를 상속하고 클러스터별 이벤트 생성을 제공한다.

문서에서 설명하는 기반 클러스터의 고정 속성 정책은 다음과 같다.

- `Supported`와 `Latch`는 제품 구성으로 결정되는 고정 속성이다.
- 생성 시 `AlarmBaseCluster::Config`의 `.supported`, `.latch`에서 한 번 초기화된다.
- `mSupported`, `mLatch`라는 `const` 멤버에 저장된다.
- 읽기 전용 접근자 `GetSupported()`, `GetLatch()`를 제공하며, 해당 속성에 대한 `WriteAttribute`는 구현하지 않는다.
- 기존 `DishwasherAlarmServer`의 `SetSupportedValue()`와 `SetLatchValue()`는 고정 속성의 런타임 변경을 허용했기 때문에 마이그레이션 과정에서 제거되었다.

런타임 변경에는 `SetMask()` / `GetMask()`, `SetState()` / `GetState()`가 사용된다. 기반 클러스터의 `ResetLatchedAlarms()`는 `Reset` 기능이 활성화된 경우에만 해당하며, Refrigerator Alarm 스펙에서는 `Reset`이 허용되지 않는다.

제품의 고정 속성을 변경하려면 ZAP / `.matter` 데이터 모델 구성을 수정하고, `CodegenIntegration`이 의도한 기본값을 클러스터 생성 시 `AlarmBaseCluster::Config`에 전달하도록 해야 한다.

## 관련 페이지

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
