---
entity: Identify
ids: ['0x0003']
source_paths: ['data_model/1.7/clusters/Identify.xml', 'src/app/clusters/identify-server/CodegenIntegration.cpp', 'src/app/clusters/identify-server/CodegenIntegration.h', 'src/app/clusters/identify-server/IdentifyCluster.cpp', 'src/app/clusters/identify-server/IdentifyCluster.h', 'src/app/clusters/identify-server/IdentifyIntegrationDelegate.h', 'src/app/clusters/identify-server/README.md', 'src/app/clusters/identify-server/identify-server.h', 'src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Identify

## 개요

`Identify`는 관리자가 특정 Node를 식별하도록 돕는 클러스터다. 장치의 LED 점멸, 스피커 소리, 디스플레이의 QR 코드 표시 등에 사용할 수 있다.

- 클러스터 ID: `0x0003`
- 스펙 이름: `Identify Cluster`
- 리비전: `6`
- 범위: `Endpoint`
- 구현 방식: `IdentifyCluster` 기반의 코드 중심 C++ 서버
- 애플리케이션 연동: `chip::app::Clusters::IdentifyDelegate`를 통해 식별 시작·중지 및 효과 실행을 전달한다.

## 스펙

출처: `data_model/1.7/clusters/Identify.xml`

### 클러스터 분류

| 항목 | 값 |
|---|---|
| `id` | `0x0003` |
| `name` | `Identify Cluster` |
| `clusterId`의 `name` | `Identify` |
| `revision` | `6` |
| `hierarchy` | `base` |
| `role` | `utility` |
| `picsCode` | `I` |
| `scope` | `Endpoint` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | CCB 2808 |
| `3` | All Hubs 변경 |
| `4` | 새로운 데이터 모델 형식과 표기법 도입, `IdentifyType` 추가 |
| `5` | `Query` 기능 제거 |
| `6` | `IdentifyTime` 속성에 Q 품질 추가 |

### 데이터 타입

아래 열거형의 모든 항목은 `mandatoryConform`으로 정의된다.

#### `EffectIdentifierEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `Blink` | 예: 조명을 한 번 켰다가 끈다. |
| `0x01` | `Breathe` | 예: 1초 동안 조명을 켰다가 끄는 동작을 15회 반복한다. |
| `0x02` | `Okay` | 예: 색상 조명은 1초 동안 녹색으로 표시하고, 비색상 조명은 두 번 점멸한다. |
| `0x0B` | `ChannelChange` | 예: 색상 조명은 8초 동안 주황색으로 표시한다. 비색상 조명은 0.5초 동안 최대 밝기, 이후 7.5초 동안 최소 밝기로 표시한다. |
| `0xFE` | `FinishEffect` | 현재 효과 시퀀스를 완료한 뒤 종료한다. 예: 진행 중인 1초의 `Breathe` 동작을 완료한 뒤 종료한다. |
| `0xFF` | `StopEffect` | 가능한 한 빨리 효과를 종료한다. |

#### `EffectVariantEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `Default` | 기본 효과를 사용한다. |

#### `IdentifyTypeEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `None` | 표시하지 않는다. |
| `0x01` | `LightOutput` | 조명 제품의 광출력을 사용한다. |
| `0x02` | `VisibleIndicator` | 일반적으로 작은 LED를 사용한다. |
| `0x03` | `AudibleBeep` | XML에 별도 설명이 없다. |
| `0x04` | `Display` | 디스플레이 화면에 표시한다. |
| `0x05` | `Actuator` | 블라인드 동작이나 벽 매립형 릴레이 등 액추에이터 기능으로 표시한다. |

### 속성

| ID | 이름 | 타입 | 적합성 | 접근 권한 | 품질 |
|---|---|---|---|---|---|
| `0x0000` | `IdentifyTime` | `uint16` | 필수 | 읽기: `view`, 쓰기: `operate` | `quieterReporting="true"` |
| `0x0001` | `IdentifyType` | `IdentifyTypeEnum` | 필수 | 읽기: `view` | 별도 지정 없음 |

`IdentifyType`에는 `constraint`가 있으나, 제공된 XML의 `desc`는 비어 있다.

### 명령

| ID | 이름 | 방향 | 적합성 | 호출 권한 | `response` |
|---|---|---|---|---|---|
| `0x00` | `Identify` | `commandToServer` | 필수 | `manage` | `Y` |
| `0x40` | `TriggerEffect` | `commandToServer` | 선택 | `manage` | `Y` |

#### `Identify` 필드

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `IdentifyTime` | `uint16` | 필수 |

#### `TriggerEffect` 필드

| 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|
| `0` | `EffectIdentifier` | `EffectIdentifierEnum` | 필수 |
| `1` | `EffectVariant` | `EffectVariantEnum` | 필수 |

두 필드 모두 `constraint`가 있으나, 제공된 XML의 `desc`는 비어 있다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml`

이 파일은 Alchemy가 생성한 XML이며, 원문에 직접 편집하지 않도록 명시되어 있다. 생성 원본은 `src/app_clusters/Identify.adoc`이다.

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| configurator의 domain | `CHIP` |
| 클러스터 domain | `General` |
| 이름 | `Identify` |
| 코드 | `0x0003` |
| define | `IDENTIFY_CLUSTER` |
| client | `true`, `tick="false"`, `init="false"` |
| server | `true`, `tick="false"`, `init="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="6"` |

### 타입 및 속성 매핑

`IdentifyTypeEnum`, `EffectIdentifierEnum`, `EffectVariantEnum`은 모두 `enum8`로 정의되며, 항목 이름과 값은 스펙 XML과 같다.

| 코드 | 이름 | define | SDK 타입 | 설정 |
|---|---|---|---|---|
| `0x0000` | `IdentifyTime` | `IDENTIFY_TIME` | `int16u` | `side="server"`, `writable="true"` |
| `0x0001` | `IdentifyType` | `IDENTIFY_TYPE` | `IdentifyTypeEnum` | `side="server"`, `max="0x05"` |

스펙에서 `uint16`인 `IdentifyTime`은 SDK XML에서 `int16u`로 표현된다.

### 명령 정의

| 코드 | 이름 | 인자 | 설정 |
|---|---|---|---|
| `0x00` | `Identify` | `IdentifyTime`: `int16u`, ID `0` | `source="client"`, 호출 권한 `manage` |
| `0x40` | `TriggerEffect` | `EffectIdentifier`: `EffectIdentifierEnum`, ID `0`; `EffectVariant`: `EffectVariantEnum`, ID `1` | `source="client"`, `optional="true"`, 호출 권한 `manage` |

- `Identify`: 수신 장치의 식별 동작을 시작하거나 중지한다.
- `TriggerEffect`: 특정 조명 효과 등의 사용자 피드백을 지원한다.
- `EffectVariant`에는 `max="0x00"`이 지정되어 있다.
- `TriggerEffect`에는 `optionalConform`도 명시되어 있다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/identify-server/IdentifyCluster.h` | `IdentifyCluster`, `IdentifyDelegate`, `Config` 및 공개 인터페이스 선언 |
| `src/app/clusters/identify-server/IdentifyCluster.cpp` | 속성 접근, 명령 처리, 식별 시간 및 타이머 관리 |
| `src/app/clusters/identify-server/IdentifyIntegrationDelegate.h` | 식별 진행 여부를 조회하는 통합 인터페이스 |
| `src/app/clusters/identify-server/CodegenIntegration.h` | 레거시 `Identify` 구조체와 콜백 타입 선언 |
| `src/app/clusters/identify-server/CodegenIntegration.cpp` | 레거시 API 연결, 인스턴스 검색 및 등록 관리 |
| `src/app/clusters/identify-server/identify-server.h` | `app/clusters/identify-server/CodegenIntegration.h`를 포함하는 호환 헤더 |

### `IdentifyCluster` 구성

`chip::app::Clusters::IdentifyCluster`는 `DefaultServerCluster`, `TimerContext`, `IdentifyIntegrationDelegate`를 상속한다.

`Config` 생성자는 `EndpointId endpoint`와 `TimerDelegate & delegate`를 필수로 받는다.

| 설정 메서드 | 대상 필드 | 기본값 |
|---|---|---|
| `WithIdentifyType` | `identifyType` | `Identify::IdentifyTypeEnum::kNone` |
| `WithDelegate` | `identifyDelegate` | `nullptr` |
| `WithEffectIdentifier` | `effectIdentifier` | `Identify::EffectIdentifierEnum::kBlink` |
| `WithEffectVariant` | `effectVariant` | `Identify::EffectVariantEnum::kDefault` |

생성 시 `mIdentifyTime`은 `0`으로 초기화된다. 사용자 정의 타이머가 필요하지 않으면 헤더 설명에 따라 `DefaultTimerDelegate`를 사용할 수 있다.

### 애플리케이션 콜백

`IdentifyDelegate`는 다음 순수 가상 메서드를 제공한다.

| 메서드 | 역할 |
|---|---|
| `OnIdentifyStart` | 식별 시작 알림 |
| `OnIdentifyStop` | 식별 중지 알림 |
| `OnTriggerEffect` | 효과 실행 요청. 전달된 `IdentifyCluster`에서 효과 정보를 조회할 수 있다. |
| `IsTriggerEffectEnabled` | `TriggerEffect` 활성화 여부 반환 |

### 속성 접근

`ReadAttribute`의 처리 대상은 다음과 같다.

| 속성 | 반환값 |
|---|---|
| `Attributes::IdentifyTime::Id` | `mIdentifyTime` |
| `Attributes::IdentifyType::Id` | `mIdentifyType` |
| `Attributes::ClusterRevision::Id` | `Identify::kRevision` |
| `Attributes::FeatureMap::Id` | `uint32_t` 값 `0` |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` |

`WriteAttribute`는 `Attributes::IdentifyTime::Id`만 처리한다.

1. 입력을 `uint16_t`로 디코딩한다.
2. `SetIdentifyTime(IdentifyTimeChangeSource::kClient, newIdentifyTime)`을 호출한다.
3. 그 외 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용하여 `Identify::Attributes::kMandatoryMetadata`를 추가한다.

### 식별 시간과 보고 처리

`SetIdentifyTime`은 값 갱신, 보고 유형, 시작·중지 콜백 및 타이머를 관리한다.

| 조건 | 처리 |
|---|---|
| 이전 값이 `0`이거나 새 값이 `0` | `DataModel::AttributeChangeType::kReportable` |
| 변경 원인이 `IdentifyTimeChangeSource::kTimer`가 아님 | `DataModel::AttributeChangeType::kReportable` |
| 타이머에 의한 그 외 변경 | `DataModel::AttributeChangeType::kQuiet` |
| 실제 값 변경 없음 | `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 즉시 반환 |
| `0`에서 양수로 변경 | delegate가 있으면 `OnIdentifyStart` 호출 |
| 양수에서 `0`으로 변경 | delegate가 있으면 `OnIdentifyStop` 호출 |
| 변경 후 값이 양수 | `System::Clock::Seconds16(1)` 간격으로 `StartTimer` 호출 |
| 변경 후 값이 `0` | `CancelTimer` 호출 |

실제 변경과 타이머 처리가 이루어진 뒤, 클라이언트 변경 또는 `0`과의 전환에는 `Protocols::InteractionModel::Status::Success`를 반환한다. 그 외에는 `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 반환한다.

관련 메서드:

- `TimerFired`: `mIdentifyTime > 0`일 때 `IdentifyTimeChangeSource::kTimer`로 시간을 `1` 감소시킨다.
- `StopIdentifying`: `IdentifyTimeChangeSource::kClient`로 시간을 `0`으로 설정한다.
- `IsIdentifying`: `mIdentifyTime > 0`을 반환한다.
- `GetIdentifyTime`, `GetIdentifyType`, `GetEffectIdentifier`, `GetEffectVariant`: 현재 값을 반환한다.

### 명령 처리

#### `Identify`

`InvokeCommand`는 `Identify::Commands::Identify::DecodableType`으로 입력을 디코딩한 뒤, `data.identifyTime`을 `SetIdentifyTime`에 전달한다. 변경 원인은 `IdentifyTimeChangeSource::kClient`이다.

#### `TriggerEffect`

입력을 디코딩한 뒤 `mEffectIdentifier`와 `mEffectVariant`를 먼저 갱신한다.

| 상태 또는 효과 | 처리 |
|---|---|
| `mIdentifyDelegate`가 없음 | `Protocols::InteractionModel::Status::Success` 반환 |
| `mIdentifyTime == 0` | `OnTriggerEffect`를 즉시 호출하고 성공 반환 |
| 식별 중이며 `Identify::EffectIdentifierEnum::kFinishEffect` | 식별 시간을 `1`로 설정 |
| 식별 중이며 `Identify::EffectIdentifierEnum::kStopEffect` | 식별 시간을 `0`으로 설정 |
| 식별 중이며 그 외 효과 | 식별 시간을 `0`으로 설정한 뒤 `OnTriggerEffect` 호출 |

마지막 경우에는 `SetIdentifyTime`의 반환값을 반환한다. 식별 시간이 양수에서 `0`으로 바뀌면 `OnTriggerEffect`보다 먼저 `OnIdentifyStop`이 호출된다.

그 외 명령 ID에는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

#### 수락 명령 목록

`AcceptedCommands`는 delegate 구성에 따라 목록을 선택한다.

- `mIdentifyDelegate`가 있고 `IsTriggerEffectEnabled()`가 참이면 `kAcceptedCommandsWithTriggerEffect`를 사용한다. 목록에는 `Identify`와 `TriggerEffect`가 포함된다.
- 그 외에는 `Identify`만 포함하는 `kAcceptedCommands`를 사용한다.

### 통합 인터페이스

`IdentifyIntegrationDelegate`는 순수 가상 메서드 `IsIdentifying`를 제공한다.

이 인터페이스는 현재 식별 진행 여부가 필요한 코드를 클러스터 자체와 분리하여, 모킹을 통한 단위 테스트를 쉽게 하고 통합 지점을 명확하게 하기 위해 정의되어 있다.

### 레거시 호환 계층

`CodegenIntegration.h`의 `Identify` 구조체는 기존 코드 생성 기반 구현을 새로운 `IdentifyCluster` 구현에 연결한다. 헤더는 새 구현에서 `IdentifyCluster.h/.cpp`를 직접 사용할 것을 안내한다.

#### 콜백과 상태

- `onIdentifyStartCb`: `void (*)(Identify *)`
- `onIdentifyStopCb`, `onEffectIdentifierCb`: `onIdentifyStartCb`의 별칭
- `mActive`: 초기값 `false`
- `nextIdentify`: 레거시 인스턴스 연결 목록의 다음 포인터
- `mCluster`: `chip::app::RegisteredServerCluster<chip::app::Clusters::IdentifyCluster>`

생성자의 선택 인자 기본값은 다음과 같다.

| 인자 | 기본값 |
|---|---|
| `onEffectIdentifier` | `nullptr` |
| `effectIdentifier` | `chip::app::Clusters::Identify::EffectIdentifierEnum::kBlink` |
| `effectVariant` | `chip::app::Clusters::Identify::EffectVariantEnum::kDefault` |
| `timerDelegate` | `nullptr` |

`timerDelegate`가 없으면 `sDefaultTimerDelegate`를 사용한다.

#### 등록과 검색

- `RegisterLegacyIdentify`: `firstLegacyIdentify` 연결 목록의 앞에 인스턴스를 추가한다.
- `UnregisterLegacyIdentify`: 연결 목록에서 인스턴스를 제거한다.
- `GetLegacyIdentifyInstance`: endpoint가 일치하는 레거시 인스턴스를 검색한다.
- `FindIdentifyClusterOnEndpoint`: 레거시 인스턴스의 `mCluster.Cluster()`를 반환한다. 일치하는 인스턴스가 없으면 `nullptr`를 반환한다.
- `Identify::Identify`: 레거시 목록에 추가하고 `CodegenDataModelProvider::Instance().Registry().Register(mCluster.Registration())`로 등록한다.
- `Identify::~Identify`: 레지스트리 등록을 해제하고 레거시 목록에서 제거한다.

생성자 주석에 따르면 endpoint가 아직 시작되지 않았어도 등록할 수 있으며, endpoint가 시작되고 컨텍스트가 설정되면 클러스터도 시작된다.

#### `IdentifyLegacyDelegate`

| 메서드 | 레거시 연결 동작 |
|---|---|
| `OnIdentifyStart` | `mActive = true` 설정 후, 존재하면 `mOnIdentifyStart` 호출 |
| `OnIdentifyStop` | `mActive = false` 설정 후, 존재하면 `mOnIdentifyStop` 호출 |
| `OnTriggerEffect` | `mCurrentEffectIdentifier`, `mEffectVariant` 갱신 후, 존재하면 `mOnEffectIdentifier` 호출 |
| `IsTriggerEffectEnabled` | 항상 `true` 반환 |

#### 초기화 및 종료 콜백

- `MatterIdentifyClusterInitCallback`: `CHIP_CODEGEN_CONFIG_ENABLE_CODEGEN_INTEGRATION_LOOKUP_ERRORS`가 활성화되어 있을 때, 레거시 인스턴스는 있으나 레지스트리에 클러스터가 없는 상태를 로그로 알린다.
- `MatterIdentifyClusterShutdownCallback`: 빈 구현이다.
- `MatterIdentifyPluginServerInitCallback`, `MatterIdentifyPluginServerShutdownCallback`: 레거시용 빈 구현이다.

## 관련 문서

### `src/app/clusters/identify-server/README.md`

코드 중심 구현의 사용법과 레거시 API에서의 이전 방법을 설명한다.

권장 통합 순서:

1. `chip::app::Clusters::IdentifyDelegate`를 상속하고 `OnIdentifyStart`, `OnIdentifyStop`, `OnTriggerEffect`, `IsTriggerEffectEnabled`를 구현한다.
2. 필요한 endpoint마다 delegate, 타이머 delegate 및 `IdentifyCluster`를 생성한다.
3. `RegisteredServerCluster`로 등록을 구성한다.
4. 애플리케이션 초기화에서 `CodegenDataModelProvider::Instance().Registry().Register`를 호출한다.

문서의 `MyIdentifyDelegate`와 `gIdentifyCluster` 사용 코드에서는 `DefaultTimerDelegate`, `WithIdentifyType`, `WithDelegate`를 사용하고, `ApplicationInit`에서 등록 결과를 검사한다.

레거시 API에 대해서는 다음을 명시한다.

- `CodegenIntegration.h`와 `CodegenIntegration.cpp`는 기존 ZAP 생성 패턴과의 호환성을 제공한다.
- 기존 패턴은 새 API를 이전 API로 연결하기 위한 추가 코드로 인해 약 400바이트의 코드 크기 부담이 발생한다.
- 레거시 방식은 권장되지 않으며, `IdentifyCluster`를 직접 생성하고 명시적으로 등록하는 방식으로의 이전을 권장한다.
- 기존 `Identify` 구조체 방식은 호환 계층에서 등록하므로 애플리케이션의 명시적 등록이 필요하지 않았다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
