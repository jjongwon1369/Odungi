---
entity: Identify
ids: ['0x0003']
source_paths: ['data_model/1.7/clusters/Identify.xml', 'src/app/clusters/identify-server/CodegenIntegration.cpp', 'src/app/clusters/identify-server/CodegenIntegration.h', 'src/app/clusters/identify-server/IdentifyCluster.cpp', 'src/app/clusters/identify-server/IdentifyCluster.h', 'src/app/clusters/identify-server/IdentifyIntegrationDelegate.h', 'src/app/clusters/identify-server/README.md', 'src/app/clusters/identify-server/identify-server.h', 'src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Identify

## 개요

`Identify` 클러스터는 관리자가 특정 Node를 식별할 수 있도록 돕는다. 장치의 LED 점멸, 스피커 신호음, 화면의 QR 코드 표시 등에 사용할 수 있다.

- 클러스터 ID: `0x0003`
- 스펙 이름: `Identify Cluster`
- 리비전: `6`
- 범위: `Endpoint`
- 서버 구현: `chip::app::Clusters::IdentifyCluster`
- 애플리케이션 알림 인터페이스: `chip::app::Clusters::IdentifyDelegate`

현재 구현은 코드 기반 C++ 서버이며, 이전 ZAP/Ember 기반 구현과의 결합을 줄이도록 설계되었다. 기존 애플리케이션을 위한 `Identify` 호환 API도 제공한다.

## 스펙

출처: `data_model/1.7/clusters/Identify.xml`

### 분류

| 항목 | 값 |
|---|---|
| `id` | `0x0003` |
| `name` | `Identify Cluster` |
| `revision` | `6` |
| `hierarchy` | `base` |
| `role` | `utility` |
| `picsCode` | `I` |
| `scope` | `Endpoint` |

### 데이터 타입

아래 열거형 항목은 모두 필수로 정의되어 있다.

#### `EffectIdentifierEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `Blink` | 예: 조명을 한 번 켰다가 끈다. |
| `0x01` | `Breathe` | 예: 1초에 걸쳐 조명을 켰다가 끄는 동작을 15회 반복한다. |
| `0x02` | `Okay` | 예: 색상 조명은 1초 동안 녹색으로 표시하고, 비색상 조명은 두 번 점멸한다. |
| `0x0B` | `ChannelChange` | 예: 색상 조명은 8초 동안 주황색으로 표시한다. 비색상 조명은 0.5초 동안 최대 밝기, 이후 7.5초 동안 최소 밝기로 동작한다. |
| `0xFE` | `FinishEffect` | 현재 효과 시퀀스를 완료한 뒤 종료한다. 예: 진행 중인 1초 단위의 `Breathe` 동작을 완료한 뒤 종료한다. |
| `0xFF` | `StopEffect` | 가능한 한 빨리 효과를 종료한다. |

#### `EffectVariantEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `Default` | 기본 효과를 사용한다. |

#### `IdentifyTypeEnum`

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `None` | 식별 표시 없음 |
| `0x01` | `LightOutput` | 조명 제품의 광 출력 |
| `0x02` | `VisibleIndicator` | 일반적으로 작은 LED |
| `0x03` | `AudibleBeep` | 제공된 XML에 별도 설명 없음 |
| `0x04` | `Display` | 디스플레이 화면에 표시 |
| `0x05` | `Actuator` | 블라인드 동작이나 벽면 내장 릴레이 등의 액추에이터 기능으로 표시 |

### 속성

| ID | 이름 | 타입 | 접근 및 권한 | 적합성 | 품질 |
|---|---|---|---|---|---|
| `0x0000` | `IdentifyTime` | `uint16` | 읽기: `view`, 쓰기: `operate` | 필수 | `quieterReporting="true"` |
| `0x0001` | `IdentifyType` | `IdentifyTypeEnum` | 읽기: `view` | 필수 | — |

`IdentifyType`의 제약 설명은 제공된 XML에서 비어 있다.

### 명령

| ID | 이름 | 방향 | 호출 권한 | 적합성 | 응답 표기 |
|---|---|---|---|---|---|
| `0x00` | `Identify` | `commandToServer` | `manage` | 필수 | `response="Y"` |
| `0x40` | `TriggerEffect` | `commandToServer` | `manage` | 선택 | `response="Y"` |

명령 필드:

| 명령 | 필드 ID | 이름 | 타입 | 적합성 |
|---|---|---|---|---|
| `Identify` | `0` | `IdentifyTime` | `uint16` | 필수 |
| `TriggerEffect` | `0` | `EffectIdentifier` | `EffectIdentifierEnum` | 필수 |
| `TriggerEffect` | `1` | `EffectVariant` | `EffectVariantEnum` | 필수 |

`TriggerEffect`의 두 필드에는 제약 요소가 있지만, 설명은 비어 있다.

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | `CCB 2808` |
| `3` | `All Hubs` 변경 사항 |
| `4` | 새로운 데이터 모델 형식과 표기법 적용, `IdentifyType` 추가 |
| `5` | `Query` 기능 제거 |
| `6` | `IdentifyTime` 속성에 `Q` 품질 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml`

이 파일은 Alchemy가 생성한 XML이며, 직접 편집하지 않도록 표시되어 있다. 생성 원본은 `src/app_clusters/Identify.adoc`이다.

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| 이름 | `Identify` |
| 코드 | `0x0003` |
| 클러스터 도메인 | `General` |
| 매크로 식별자 | `IDENTIFY_CLUSTER` |
| client | 활성화, `tick="false"`, `init="false"` |
| server | 활성화, `tick="false"`, `init="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="6"`, `side="either"` |

`IdentifyTypeEnum`, `EffectIdentifierEnum`, `EffectVariantEnum`은 모두 `enum8`로 정의되며, 항목 이름과 값은 스펙 입력과 동일하다.

### 속성 및 명령 매핑

| 대상 | SDK 정의 |
|---|---|
| `IdentifyTime` | `code="0x0000"`, `define="IDENTIFY_TIME"`, `type="int16u"`, `side="server"`, `writable="true"` |
| `IdentifyType` | `code="0x0001"`, `define="IDENTIFY_TYPE"`, `type="IdentifyTypeEnum"`, `side="server"`, `max="0x05"` |
| `Identify` | `code="0x00"`, `source="client"`, 호출 권한 `manage` |
| `TriggerEffect` | `code="0x40"`, `source="client"`, `optional="true"`, 호출 권한 `manage` |

- `Identify`는 수신 장치의 식별 동작을 시작하거나 중지한다. 인수 `IdentifyTime`은 `id="0"`, `type="int16u"`이다.
- `TriggerEffect`는 조명 효과 등의 사용자 피드백을 지원한다.
  - `EffectIdentifier`: `id="0"`, `type="EffectIdentifierEnum"`
  - `EffectVariant`: `id="1"`, `type="EffectVariantEnum"`, `max="0x00"`

스펙의 `uint16`은 SDK XML에서 `int16u`로 표기된다. 스펙의 `quieterReporting="true"`는 제공된 SDK XML에는 별도로 표기되어 있지 않다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/identify-server/IdentifyCluster.h` | `IdentifyCluster`, `IdentifyDelegate`, `Config` 선언 |
| `src/app/clusters/identify-server/IdentifyCluster.cpp` | 속성 접근, 명령 처리, 타이머 및 보고 동작 구현 |
| `src/app/clusters/identify-server/IdentifyIntegrationDelegate.h` | 식별 진행 여부를 조회하는 통합 인터페이스 |
| `src/app/clusters/identify-server/CodegenIntegration.h` | 기존 `Identify` API 선언 |
| `src/app/clusters/identify-server/CodegenIntegration.cpp` | 기존 API와 새 클러스터 사이의 연결 및 등록 처리 |
| `src/app/clusters/identify-server/identify-server.h` | `app/clusters/identify-server/CodegenIntegration.h`를 포함하는 호환 헤더 |

### `IdentifyCluster` 구성

`IdentifyCluster`는 `DefaultServerCluster`, `TimerContext`, `IdentifyIntegrationDelegate`를 상속한다.

`Config` 생성자는 `EndpointId endpoint`와 `TimerDelegate & delegate`를 요구한다.

| 설정 메서드 | 설정 대상 | 기본값 |
|---|---|---|
| `WithIdentifyType` | `identifyType` | `Identify::IdentifyTypeEnum::kNone` |
| `WithDelegate` | `identifyDelegate` | `nullptr` |
| `WithEffectIdentifier` | `effectIdentifier` | `Identify::EffectIdentifierEnum::kBlink` |
| `WithEffectVariant` | `effectVariant` | `Identify::EffectVariantEnum::kDefault` |

생성 시 `mIdentifyTime`은 `0`으로 초기화된다. 사용자 정의 타이머가 필요하지 않으면 헤더 주석은 `DefaultTimerDelegate` 사용을 안내한다.

### 애플리케이션 인터페이스

`IdentifyDelegate`는 다음 가상 메서드를 제공한다.

| 메서드 | 역할 |
|---|---|
| `OnIdentifyStart` | 식별 시작 알림 |
| `OnIdentifyStop` | 식별 종료 알림 |
| `OnTriggerEffect` | 효과 실행 요청 |
| `IsTriggerEffectEnabled` | `TriggerEffect` 활성화 여부 반환 |

`IdentifyCluster`는 `GetEffectIdentifier`, `GetEffectVariant`, `GetIdentifyType`, `GetIdentifyTime`으로 현재 값을 제공한다.

`IdentifyIntegrationDelegate`는 `IsIdentifying`만 제공하는 별도 인터페이스다. 테스트에서의 모킹을 쉽게 하고 통합 지점을 명확히 하기 위해 분리되어 있다. `IdentifyCluster::IsIdentifying`은 `mIdentifyTime > 0`을 반환한다.

### 속성 접근

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 값 |
|---|---|
| `IdentifyTime` | `mIdentifyTime` |
| `IdentifyType` | `mIdentifyType` |
| `ClusterRevision` | `Identify::kRevision` |
| `FeatureMap` | `uint32_t` 값 `0` |

그 외 속성은 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`WriteAttribute`는 `IdentifyTime`만 처리한다. 값을 `uint16_t`로 디코딩한 뒤 `SetIdentifyTime(IdentifyTimeChangeSource::kClient, newIdentifyTime)`을 호출한다.

`Attributes`는 `AttributeListBuilder`를 통해 `Identify::Attributes::kMandatoryMetadata`를 추가한다.

### 식별 시간, 타이머 및 보고

`SetIdentifyTime`은 속성 변경, 시작·종료 콜백, 타이머 예약을 함께 처리한다.

1. 변경 유형을 결정한다.
   - 기존 값이나 새 값이 `0`이면 `DataModel::AttributeChangeType::kReportable`
   - 변경 원인이 `IdentifyTimeChangeSource::kTimer`가 아니면 `DataModel::AttributeChangeType::kReportable`
   - 나머지 타이머 변경은 `DataModel::AttributeChangeType::kQuiet`
2. `SetAttributeValue` 결과 실제 변경이 없으면 `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 반환한다.
3. delegate가 있으면 상태 전이에 따라 콜백을 호출한다.
   - `0` → 양수: `OnIdentifyStart`
   - 양수 → `0`: `OnIdentifyStop`
4. 새 값이 양수이면 `System::Clock::Seconds16(1)` 간격의 타이머를 시작하고, `0`이면 타이머를 취소한다.

`TimerFired`는 `mIdentifyTime > 0`일 때 값을 1 감소시킨다. `StopIdentifying`은 `IdentifyTimeChangeSource::kClient`로 값을 `0`으로 설정한다.

클라이언트 변경 또는 `0`과의 상태 전이에는 `Protocols::InteractionModel::Status::Success`를 반환한다. 그 외 타이머 감소에는 `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 반환한다.

구현 주석은 `IdentifyTime`의 보고 조건을 다음과 같이 설명한다.

- `0`에서 다른 값으로 변경되거나 그 반대인 경우
- 클라이언트가 쓰는 경우
- `Identify` 명령으로 설정하는 경우

### 명령 처리

#### `Identify`

`InvokeCommand`는 `Identify::Commands::Identify::DecodableType`으로 인수를 디코딩하고, `data.identifyTime`을 `IdentifyTimeChangeSource::kClient`로 설정한다.

#### `TriggerEffect`

인수를 디코딩한 뒤 `mEffectIdentifier`와 `mEffectVariant`를 먼저 갱신한다.

| 조건 | 동작 |
|---|---|
| `mIdentifyDelegate`가 없음 | 콜백 없이 `Success` 반환 |
| `mIdentifyTime == 0` | 즉시 `OnTriggerEffect` 호출 후 `Success` 반환 |
| 식별 중이며 `kFinishEffect` | `IdentifyTime`을 `1`로 설정 |
| 식별 중이며 `kStopEffect` | `IdentifyTime`을 `0`으로 설정 |
| 식별 중이며 그 외 효과 | `IdentifyTime`을 `0`으로 설정한 뒤 `OnTriggerEffect` 호출 |

식별 중 일반 효과를 처리할 때는 `SetIdentifyTime`이 `OnIdentifyStop`을 호출한 후 새 효과 콜백이 실행된다.

`AcceptedCommands`는 기본적으로 `Identify`만 제공한다. delegate가 존재하고 `IsTriggerEffectEnabled()`가 `true`이면 `TriggerEffect`도 포함한다. `InvokeCommand`에서 알 수 없는 명령 ID는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

### 기존 `Identify` API 호환 계층

`CodegenIntegration.h`의 `Identify`는 기존 codegen 기반 애플리케이션을 새 `IdentifyCluster` 구현에 연결한다. 헤더 주석은 신규 구현에서 `IdentifyCluster.h/.cpp`를 직접 사용하도록 안내한다.

- `onIdentifyStartCb`, `onIdentifyStopCb`, `onEffectIdentifierCb`는 `Identify *`를 받는 콜백이다.
- `mCluster`는 `chip::app::RegisteredServerCluster<chip::app::Clusters::IdentifyCluster>`이다.
- `timerDelegate`가 없으면 `sDefaultTimerDelegate`를 사용한다.
- 생성자는 `RegisterLegacyIdentify`로 목록에 추가하고 `CodegenDataModelProvider::Instance().Registry().Register(mCluster.Registration())`를 호출한다.
- 소멸자는 레지스트리에서 클러스터를 해제한 뒤 `UnregisterLegacyIdentify`를 호출한다.
- `firstLegacyIdentify`와 `nextIdentify`로 기존 인스턴스 목록을 관리한다.

`IdentifyLegacyDelegate`의 연결 동작:

| 메서드 | 기존 API에 전달하는 동작 |
|---|---|
| `OnIdentifyStart` | `mActive = true` 설정 후 `mOnIdentifyStart`가 있으면 호출 |
| `OnIdentifyStop` | `mActive = false` 설정 후 `mOnIdentifyStop`이 있으면 호출 |
| `OnTriggerEffect` | 효과 값을 `mCurrentEffectIdentifier`, `mEffectVariant`에 복사한 뒤 `mOnEffectIdentifier`가 있으면 호출 |
| `IsTriggerEffectEnabled` | 항상 `true` 반환 |

`FindIdentifyClusterOnEndpoint`는 기존 인스턴스 목록에서 endpoint를 찾아 해당 `IdentifyCluster` 포인터를 반환한다. 찾지 못하면 `nullptr`를 반환한다.

`MatterIdentifyClusterInitCallback`은 `CHIP_CODEGEN_CONFIG_ENABLE_CODEGEN_INTEGRATION_LOOKUP_ERRORS`가 활성화된 경우, 기존 인스턴스는 있지만 레지스트리 등록을 찾지 못한 상태를 로그로 알린다.

다음 콜백은 빈 구현이다.

- `MatterIdentifyClusterShutdownCallback`
- `MatterIdentifyPluginServerInitCallback`
- `MatterIdentifyPluginServerShutdownCallback`

## 관련 문서

### `src/app/clusters/identify-server/README.md`

코드 기반 서버의 통합 절차와 기존 API에서의 이전 방법을 설명한다.

권장 통합 순서는 다음과 같다.

1. `chip::app::Clusters::IdentifyDelegate`를 상속하고 식별 시작·종료·효과 처리 메서드를 구현한다.
2. 필요한 endpoint마다 delegate, 타이머 delegate, `IdentifyCluster`를 생성한다.
3. `RegisteredServerCluster`로 등록 객체를 구성한다.
4. 애플리케이션 초기화 중 `CodegenDataModelProvider::Instance().Registry().Register(...)`로 클러스터를 등록한다.

문서는 `MyIdentifyDelegate`, `gMyIdentifyDelegate`, `gTimerDelegate`, `gIdentifyCluster`, `ApplicationInit`을 사용하는 통합 코드를 제공한다.

기존 `Identify` API는 하위 호환성을 위해 유지되지만 사용을 권장하지 않는다. README는 새 API를 기존 API로 변환하는 호환 코드가 약 400바이트의 코드 크기 오버헤드를 유발한다고 설명하며, `IdentifyCluster`를 직접 생성하고 등록하는 방식으로 이전할 것을 권장한다.

## 관련 페이지

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md)
- [Cooktop](../device-types/cooktop.md)
- [Dishwasher](../device-types/dishwasher.md)
- [Extractor Hood](../device-types/extractor-hood.md)
- [Humidity Conditioner](../device-types/humidity-conditioner.md)
- [Laundry Dryer](../device-types/laundry-dryer.md)
- [Laundry Washer](../device-types/laundry-washer.md)
- [Microwave Oven](../device-types/microwave-oven.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Water Heater](../device-types/water-heater.md)
