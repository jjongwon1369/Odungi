---
entity: Dishwasher Alarm
ids: ['0x005D']
source_paths: ['data_model/1.7/clusters/DishwasherAlarm.xml', 'src/app/clusters/dishwasher-alarm-server/CodegenIntegration.cpp', 'src/app/clusters/dishwasher-alarm-server/CodegenIntegration.h', 'src/app/clusters/dishwasher-alarm-server/DishwasherAlarmCluster.cpp', 'src/app/clusters/dishwasher-alarm-server/DishwasherAlarmCluster.h', 'src/app/clusters/dishwasher-alarm-server/dishwasher-alarm-delegate.h', 'src/app/clusters/dishwasher-alarm-server/dishwasher-alarm-server.h', 'src/app/zap-templates/zcl/data-model/chip/dishwasher-alarm-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Dishwasher Alarm

## 개요

Dishwasher Alarm은 식기세척기 알람을 구성하기 위한 속성과 명령을 제공하는 클러스터이다. 급수, 배수, 도어, 온도 및 수위 이상을 비트맵으로 표현한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x005D` |
| 스펙 이름 | `Dishwasher Alarm Cluster` |
| 클러스터 이름 | `Dishwasher Alarm` |
| 리비전 | `1` |
| 기반 클러스터 | `Alarm Base` |
| PICS 코드 | `DISHALM` |
| 범위 | `Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/DishwasherAlarm.xml`

### 분류 및 리비전

- `hierarchy`: `derived`
- `baseCluster`: `Alarm Base`
- `role`: `application`
- `scope`: `Endpoint`
- 리비전 `1`: `Initial revision`

### AlarmBitmap

| 비트 | 이름 | 의미 |
|---|---|---|
| `0` | `InflowError` | 급수 이상 |
| `1` | `DrainError` | 배수 이상 |
| `2` | `DoorError` | 도어 또는 도어 잠금 이상 |
| `3` | `TempTooLow` | 정상 온도에 도달하지 못함 |
| `4` | `TempTooHigh` | 온도가 너무 높음 |
| `5` | `WaterLevelError` | 수위 이상 |

적합성 조건은 다음과 같이 기술되어 있다.

- `DoorError`: `optionalConform`에 `choice="a"`, `more="true"`, `min="1"`이 지정되어 있다.
- 나머지 비트: `otherwiseConform` 내부에 `provisionalConform`과 동일한 `optionalConform` 조건이 지정되어 있다.

제공된 스펙 조각에는 속성, 명령 및 이벤트의 개별 정의가 포함되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/dishwasher-alarm-cluster.xml`

이 파일은 Alchemy로 생성되었으며, 주석에 직접 편집하지 않도록 명시되어 있다. 생성 원본 경로는 `src/app_clusters/DishwasherAlarm.adoc`이다.

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 이름 | `Dishwasher Alarm` |
| 도메인 | `Appliances` |
| 코드 | `0x005D` |
| define | `DISHWASHER_ALARM_CLUSTER` |
| 클라이언트 | 활성화, `tick="false"`, `init="false"` |
| 서버 | 활성화, `tick="false"`, `init="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

### AlarmBitmap

SDK의 `AlarmBitmap`은 `bitmap32`이다.

| 필드 | 마스크 |
|---|---|
| `InflowError` | `0x01` |
| `DrainError` | `0x02` |
| `DoorError` | `0x04` |
| `TempTooLow` | `0x08` |
| `TempTooHigh` | `0x10` |
| `WaterLevelError` | `0x20` |

### 기능

| 비트 | 코드 | 이름 | 지원 조건 | 의미 |
|---|---|---|---|---|
| `0` | `RESET` | `Reset` | 선택 사항 | 알람 재설정 지원 |

### 속성

모든 속성은 `side="server"`, 타입은 `AlarmBitmap`, 최댓값은 `0x0000003F`이다.

| ID | 이름 | define | 조건 |
|---|---|---|---|
| `0x0000` | `Mask` | `MASK` | 별도 선택 조건 없음 |
| `0x0001` | `Latch` | `LATCH` | `optional="true"`이며, `RESET` 지원 시 `mandatoryConform` |
| `0x0002` | `State` | `STATE` | 별도 선택 조건 없음 |
| `0x0003` | `Supported` | `SUPPORTED` | 별도 선택 조건 없음 |

### 명령

두 명령 모두 `source="client"`, `optional="true"`로 정의된다. 인자의 타입은 `AlarmBitmap`, 최댓값은 `0x0000003F`이다.

| 코드 | 이름 | 인자 | 조건 | 동작 |
|---|---|---|---|---|
| `0x00` | `Reset` | `fieldId="0"`, `Alarms` | `RESET` 지원 시 `mandatoryConform` | 가능한 경우 활성 알람과 래치된 알람을 재설정 |
| `0x01` | `ModifyEnabledAlarms` | `fieldId="0"`, `Mask` | `optionalConform` | 서버에서 알람을 활성화하거나 억제하도록 요청 |

### Notify 이벤트

`Notify`는 하나 이상의 알람 상태가 변경될 때 생성되어야 한다.

| 항목 | 값 |
|---|---|
| 코드 | `0x00` |
| 발생 측 | `server` |
| 우선순위 | `info` |
| 적합성 | `mandatoryConform` |

모든 필드의 타입은 `AlarmBitmap`, 최댓값은 `0x0000003F`이다.

| 필드 ID | 이름 |
|---|---|
| `0` | `Active` |
| `1` | `Inactive` |
| `2` | `State` |
| `3` | `Mask` |

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/dishwasher-alarm-server/CodegenIntegration.cpp` | 클러스터 등록·해제, 초기값 적용, delegate 연결, 속성 접근 구현 |
| `src/app/clusters/dishwasher-alarm-server/CodegenIntegration.h` | 통합 API와 `DishwasherAlarmServer` 선언 |
| `src/app/clusters/dishwasher-alarm-server/DishwasherAlarmCluster.cpp` | `Notify` 이벤트 생성 |
| `src/app/clusters/dishwasher-alarm-server/DishwasherAlarmCluster.h` | `AlarmBaseCluster` 파생 클래스 정의 |
| `src/app/clusters/dishwasher-alarm-server/dishwasher-alarm-delegate.h` | 애플리케이션별 알람 처리 인터페이스 |
| `src/app/clusters/dishwasher-alarm-server/dishwasher-alarm-server.h` | `app/clusters/dishwasher-alarm-server/CodegenIntegration.h`를 포함하는 헤더 |

### DishwasherAlarmCluster

`chip::app::Clusters`의 `DishwasherAlarmCluster`는 `AlarmBaseCluster`를 상속한다.

- `Config`는 `AlarmBaseCluster::Config`의 별칭이다.
- 생성자는 `endpointId`, `DishwasherAlarm::Id`, `DishwasherAlarm::kRevision`, `config`를 기반 클래스에 전달한다.
- `SetStateIgnoringLatch`는 기반 클래스의 `AlarmBaseCluster::SetStateIgnoringLatch`를 호출한다.
- `SendNotifyEvent`를 재정의하여 Dishwasher Alarm 전용 이벤트를 생성한다.

### 등록 및 초기화

클러스터 저장 공간은 다음 값으로 결정된다.

- `kDishwasherAlarmFixedClusterCount`: `DishwasherAlarm::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kDishwasherAlarmMaxClusterCount`: `kDishwasherAlarmFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`

`static_assert`로 고정 개수가 `MATTER_DM_DISHWASHER_ALARM_CLUSTER_SERVER_ENDPOINT_COUNT`와 일치하는지, 최대 개수가 `kEmberInvalidEndpointIndex` 이하인지 검사한다.

`gDishwasherAlarmClusters`의 각 `DishwasherAlarmClusterSlot`은 다음을 보관한다.

- `LazyRegisteredServerCluster<DishwasherAlarmCluster>`
- `DishwasherAlarmIntegrationDelegateWrapper`

`DishwasherAlarmIntegrationDelegate`의 `CreateRegistration`은 다음 순서로 동작한다.

1. `featureMap`으로 `BitFlags<DishwasherAlarm::Feature>`를 구성한다.
2. `Supported::GetDefault`와 `Latch::GetDefault`가 `Status::Success`를 반환하면 해당 초기값을 사용한다. 성공하지 않으면 각 값은 값 초기화된 상태로 유지된다.
3. `EndpointHasModifyEnabledAlarmsCommand`로 `ModifyEnabledAlarms` 지원 여부를 확인한다.
4. delegate, 기능, 지원 알람, 래치 및 명령 지원 여부를 담은 `DishwasherAlarmCluster::Config`로 클러스터를 생성한다.
5. `Mask::GetDefault`와 `State::GetDefault`가 성공하면 각각 `SetMask`와 `SetState`로 적용한다.
6. 등록 객체를 반환한다.

`EndpointHasModifyEnabledAlarmsCommand`는 `emberAfFindServerCluster`로 서버 클러스터를 찾고, `acceptedCommandList`를 `kInvalidCommandId`까지 검사한다. 클러스터나 명령 목록이 없으면 `false`를 반환한다.

| 함수 | 역할 |
|---|---|
| `MatterDishwasherAlarmClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterDishwasherAlarmClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | 엔드포인트의 클러스터 조회 |
| `FindRegistration` | 클러스터가 생성되어 있으면 해당 인터페이스 반환, 아니면 `nullptr` |
| `ReleaseRegistration` | 클러스터의 `Destroy` 호출 |

등록 시 `fetchFeatureMap`은 `true`, `fetchOptionalAttributes`는 `false`이다.

`MatterDishwasherAlarmPluginServerInitCallback`과 `MatterDishwasherAlarmPluginServerShutdownCallback`은 빈 `__attribute__((weak))` 함수로 정의된다.

### delegate 연결

`DishwasherAlarm::Delegate`는 애플리케이션별 동작을 위한 인터페이스이다.

| 콜백 | 의미 | 반환값 |
|---|---|---|
| `ModifyEnabledAlarmsCallback` | `Mask` 변경 전 알림 | `true`이면 변경 허용, `false`이면 변경하지 않음 |
| `ResetAlarmsCallback` | 가능한 경우 활성 알람 재설정 | `true`이면 재설정 허용, `false`이면 재설정하지 않음 |

`Delegate`는 `EndpointId`를 받는 생성자와 기본 생성자를 제공하며, `mEndpoint`의 기본값은 `0`이다.

`DishwasherAlarmIntegrationDelegateWrapper`는 필수 `AlarmBase::Delegate&`와 선택적인 애플리케이션 delegate 사이를 연결한다.

- `SetDefaultDelegate`는 엔드포인트 슬롯의 애플리케이션 delegate를 설정한다.
- `GetDelegate`는 저장된 delegate를 반환하며, 인덱스가 범위를 벗어나면 `nullptr`를 반환한다.
- delegate가 있으면 `ModifyEnabledAlarms`와 `ResetAlarms`를 각각 `ModifyEnabledAlarmsCallback`과 `ResetAlarmsCallback`으로 전달한다.
- 전달할 때 `Raw()` 값을 `BitMask<DishwasherAlarm::AlarmBitmap>`으로 변환한다.
- delegate가 없으면 두 메서드는 `true`를 반환하여 클러스터의 속성 갱신을 허용한다.

### 속성 접근 및 서버 API

`DishwasherAlarmServer::Instance()`는 정적 `instance`를 반환한다.

아래 상태 반환 API는 먼저 `FindClusterOnEndpoint`로 클러스터를 조회하며, 없으면 `Status::UnsupportedEndpoint`를 반환한다.

| API | 처리 |
|---|---|
| `GetMaskValue` | `GetMask` 값을 변환하여 반환 |
| `GetLatchValue` | `HasResetFeature` 확인 후 `GetLatch` 값 반환. 기능이 없으면 `Status::UnsupportedAttribute` |
| `GetStateValue` | `GetState` 값을 변환하여 반환 |
| `GetSupportedValue` | `GetSupported` 값을 변환하여 반환 |
| `SetMaskValue` | 입력값을 변환하여 `SetMask` 호출 |
| `SetStateValue` | 기본적으로 `SetState` 호출. `ignoreLatchState`가 `true`이면 `SetStateIgnoringLatch` 호출 |
| `ResetLatchedAlarms` | 입력값을 변환하여 클러스터의 `ResetLatchedAlarms` 호출 |

- 조회 API는 출력 포인터가 `nullptr`이면 값을 기록하지 않는다. 앞선 검사가 성공하면 `Status::Success`를 반환한다.
- `ignoreLatchState`의 기본값은 `false`이다.
- `HasResetFeature`는 클러스터가 없으면 `false`, 있으면 `GetFeatures().Has(Feature::kReset)` 결과를 반환한다.
- `ToAlarmMap`과 `FromAlarmMap`은 `Raw()`를 통해 `AlarmBase::AlarmMap`과 `BitMask<DishwasherAlarm::AlarmMap>` 사이를 변환한다.

`Attributes` 네임스페이스는 실행 중인 클러스터의 속성 접근을 제공한다.

| 네임스페이스 | 제공 함수 |
|---|---|
| `Mask` | `Get`, `Set` |
| `Latch` | `Get` |
| `State` | `Get`, `Set` |
| `Supported` | `Get` |

이 함수들은 `DishwasherAlarmServer::Instance()`에 처리를 위임한다. ZAP/ember 속성 저장소의 시작 값을 읽을 때는 `app-common/zap-generated/attributes/Accessors.h`의 생성된 `GetDefault` 함수를 사용하도록 명시되어 있다.

### Notify 이벤트 생성

`DishwasherAlarmCluster::SendNotifyEvent`는 `mContext`가 `nullptr`이면 즉시 반환한다. 그렇지 않으면 `DishwasherAlarm::Events::Notify::Type`을 다음과 같이 구성한다.

| 구현 필드 | 입력 |
|---|---|
| `active` | `becameActive.Raw()` |
| `inactive` | `becameInactive.Raw()` |
| `state` | `newState.Raw()` |
| `mask` | `mask.Raw()` |

각 입력은 `BitMask<DishwasherAlarm::AlarmBitmap>`으로 변환된다. 이후 `mContext->interactionContext.eventsGenerator.GenerateEvent(event, mPath.mEndpointId)`를 호출한다.

제공된 구현 조각에는 `AlarmBaseCluster`의 내부 상태 변경·래치 처리 및 이벤트 호출 조건에 대한 구현 본문은 포함되어 있지 않다.

## 관련 페이지

**사용 기기**

- [Dishwasher](../device-types/dishwasher.md)
