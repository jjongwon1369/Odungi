---
entity: Identify
ids: ['0x0003']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml', 'src/app/clusters/identify-server/IdentifyCluster.h', 'src/app/clusters/identify-server/identify-server.h', 'src/app/clusters/identify-server/IdentifyIntegrationDelegate.h', 'src/app/clusters/identify-server/CodegenIntegration.h', 'src/app/clusters/identify-server/CodegenIntegration.cpp', 'src/app/clusters/identify-server/README.md', 'src/app/clusters/identify-server/IdentifyCluster.cpp', 'data_model/1.7/clusters/Identify.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Identify

## 개요

`Identify`는 관리자가 특정 Node를 식별할 수 있도록 장치를 식별 상태로 전환하는 클러스터이다. LED 점멸, 스피커 소리, 화면의 QR 코드 표시 등에 사용할 수 있다.

- 클러스터 ID: `0x0003`
- 스펙 revision: `6`
- 범위: `Endpoint`
- 서버 구현: `chip::app::Clusters::IdentifyCluster`
- 애플리케이션 연동: `chip::app::Clusters::IdentifyDelegate`를 통해 식별 시작·종료 및 효과 실행을 전달한다.
- 기존 ZAP 기반 애플리케이션을 위한 `Identify` 호환 계층도 제공한다.

## 스펙

출처: `data_model/1.7/clusters/Identify.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| name | `Identify Cluster` |
| 클러스터 이름 | `Identify` |
| id | `0x0003` |
| revision | `6` |
| hierarchy | `base` |
| role | `utility` |
| picsCode | `I` |
| scope | `Endpoint` |

### 속성

| ID | 이름 | 타입 | 필수 여부 | 접근 권한 | 품질 |
|---|---|---|---|---|---|
| `0x0000` | `IdentifyTime` | `uint16` | 필수 | 읽기: `view`, 쓰기: `operate` | `quieterReporting="true"` |
| `0x0001` | `IdentifyType` | `IdentifyTypeEnum` | 필수 | 읽기: `view` | — |

### 명령

두 명령 모두 방향은 `commandToServer`, `response`는 `Y`, 호출 권한은 `manage`이다.

| ID | 이름 | 필수 여부 | 필드 |
|---|---|---|---|
| `0x00` | `Identify` | 필수 | `0`: `IdentifyTime` (`uint16`, 필수) |
| `0x40` | `TriggerEffect` | 선택 | `0`: `EffectIdentifier` (`EffectIdentifierEnum`, 필수), `1`: `EffectVariant` (`EffectVariantEnum`, 필수) |

### 데이터 타입

각 열거형에 나열된 항목은 모두 필수이다.

#### IdentifyTypeEnum

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `None` | 식별 표시 없음 |
| `0x01` | `LightOutput` | 조명 제품의 광출력 |
| `0x02` | `VisibleIndicator` | 일반적으로 작은 LED |
| `0x03` | `AudibleBeep` | 원문에 별도 설명 없음 |
| `0x04` | `Display` | 화면을 통한 표시 |
| `0x05` | `Actuator` | 블라인드 동작이나 벽 내부 릴레이 등 액추에이터 기능을 통한 표시 |

#### EffectIdentifierEnum

아래 조명 동작은 원문에 제시된 효과의 예이다.

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `Blink` | 조명을 한 번 켰다가 끈다. |
| `0x01` | `Breathe` | 1초에 걸쳐 조명을 켰다가 끄는 동작을 15회 반복한다. |
| `0x02` | `Okay` | 컬러 조명은 1초간 녹색으로 표시하고, 비컬러 조명은 두 번 점멸한다. |
| `0x0B` | `ChannelChange` | 컬러 조명은 8초간 주황색으로 표시한다. 비컬러 조명은 0.5초간 최대 밝기, 이후 7.5초간 최소 밝기로 표시한다. |
| `0xFE` | `FinishEffect` | 현재 효과 시퀀스를 마친 뒤 종료한다. 예를 들어 진행 중인 1초의 호흡 효과를 완료하고 종료한다. |
| `0xFF` | `StopEffect` | 가능한 한 빨리 효과를 종료한다. |

#### EffectVariantEnum

| 값 | 이름 | 설명 |
|---|---|---|
| `0x00` | `Default` | 기본 효과 사용 |

### revision 이력

| revision | 변경 내용 |
|---|---|
| `1` | 필수 전역 `ClusterRevision` 속성 추가 |
| `2` | `CCB 2808` |
| `3` | `All Hubs` 변경 |
| `4` | 새 데이터 모델 형식 및 표기 도입, `IdentifyType` 추가 |
| `5` | `Query` 기능 제거 |
| `6` | `IdentifyTime` 속성에 `Q` 품질 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml`

### 생성 정보

이 XML은 Alchemy가 생성한 파일이며 직접 수정하지 않도록 명시되어 있다.

- 원본: `src/app_clusters/Identify.adoc`
- Git: `0.9-fall2025-1625-gde7544db8`
- Alchemy: `v1.5.47`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| configurator domain | `CHIP` |
| cluster domain | `General` |
| name | `Identify` |
| code | `0x0003` |
| define | `IDENTIFY_CLUSTER` |
| client | 활성화, `tick="false"`, `init="false"` |
| server | 활성화, `tick="false"`, `init="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="6"` |

### 속성 정의

| code | name | define | type | 추가 설정 |
|---|---|---|---|---|
| `0x0000` | `IdentifyTime` | `IDENTIFY_TIME` | `int16u` | `side="server"`, `writable="true"` |
| `0x0001` | `IdentifyType` | `IDENTIFY_TYPE` | `IdentifyTypeEnum` | `side="server"`, `max="0x05"` |

### 명령 및 열거형 정의

- `Identify`:
  - `source="client"`, `code="0x00"`
  - 수신 장치의 식별 동작을 시작하거나 중지한다.
  - 인수: `id="0"`, `IdentifyTime`, `int16u`
  - 접근: `op="invoke"`, `privilege="manage"`
- `TriggerEffect`:
  - `source="client"`, `code="0x40"`, `optional="true"`, `optionalConform`
  - 조명 효과 등 사용자 피드백을 제공한다.
  - 인수 `id="0"`: `EffectIdentifier`, `EffectIdentifierEnum`
  - 인수 `id="1"`: `EffectVariant`, `EffectVariantEnum`, `max="0x00"`
  - 접근: `op="invoke"`, `privilege="manage"`

`IdentifyTypeEnum`, `EffectIdentifierEnum`, `EffectVariantEnum`은 모두 `enum8`이며, 항목 이름과 값은 위 스펙 정의와 동일하다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/identify-server/IdentifyCluster.h` | `IdentifyDelegate`, `IdentifyCluster`, `Config` 선언 |
| `src/app/clusters/identify-server/IdentifyCluster.cpp` | 속성 접근, 명령 처리, 타이머 및 상태 전환 |
| `src/app/clusters/identify-server/IdentifyIntegrationDelegate.h` | 식별 상태 조회 인터페이스 |
| `src/app/clusters/identify-server/CodegenIntegration.h` | 기존 `Identify` API와 조회 함수 선언 |
| `src/app/clusters/identify-server/CodegenIntegration.cpp` | 호환 콜백 연결, 등록 및 해제 |
| `src/app/clusters/identify-server/identify-server.h` | `app/clusters/identify-server/CodegenIntegration.h` 포함 |

### IdentifyCluster 구성

`IdentifyCluster`는 `DefaultServerCluster`, `TimerContext`, `IdentifyIntegrationDelegate`를 상속한다.

`Config` 생성자에는 `EndpointId endpoint`와 `TimerDelegate & delegate`가 필요하다.

| 설정 필드 | 기본값 | 설정 메서드 |
|---|---|---|
| `endpointId` | 생성자 인수 | — |
| `timerDelegate` | 생성자 인수 | — |
| `identifyType` | `Identify::IdentifyTypeEnum::kNone` | `WithIdentifyType` |
| `identifyDelegate` | `nullptr` | `WithDelegate` |
| `effectIdentifier` | `Identify::EffectIdentifierEnum::kBlink` | `WithEffectIdentifier` |
| `effectVariant` | `Identify::EffectVariantEnum::kDefault` | `WithEffectVariant` |

생성 시 `mIdentifyTime`은 `0`으로 초기화된다. 사용자 정의 타이머가 필요하지 않으면 `DefaultTimerDelegate`를 사용할 수 있다.

### 애플리케이션 및 통합 인터페이스

`IdentifyDelegate`는 다음 순수 가상 메서드를 제공한다.

| 메서드 | 역할 |
|---|---|
| `OnIdentifyStart` | 식별 시작 통지 |
| `OnIdentifyStop` | 식별 종료 통지 |
| `OnTriggerEffect` | 효과 실행 요청 |
| `IsTriggerEffectEnabled` | `TriggerEffect` 지원 여부 반환 |

콜백은 `IdentifyCluster & cluster`를 받는다. 애플리케이션은 `GetEffectIdentifier`, `GetEffectVariant`, `GetIdentifyType`, `GetIdentifyTime`으로 현재 값을 조회할 수 있다.

`IdentifyIntegrationDelegate`는 `IsIdentifying`만 제공한다. 식별 상태 조회를 클러스터에서 분리하여 모킹을 쉽게 하고 통합 지점을 명확하게 한다. `IdentifyCluster::IsIdentifying`은 `mIdentifyTime > 0`을 반환한다.

### 속성 처리

- `ReadAttribute`:
  - `Attributes::IdentifyTime::Id`: `mIdentifyTime`
  - `Attributes::IdentifyType::Id`: `mIdentifyType`
  - `Attributes::ClusterRevision::Id`: `Identify::kRevision`
  - `Attributes::FeatureMap::Id`: `uint32_t` 값 `0`
  - 그 외: `Protocols::InteractionModel::Status::UnsupportedAttribute`
- `WriteAttribute`:
  - `Attributes::IdentifyTime::Id`만 처리한다.
  - 값을 `uint16_t`로 디코딩하고 `SetIdentifyTime(IdentifyTimeChangeSource::kClient, newIdentifyTime)`을 호출한다.
  - 그 외에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.
- `Attributes`는 `Identify::Attributes::kMandatoryMetadata`를 사용하여 목록을 구성한다.

### IdentifyTime 상태 전환과 보고

`SetIdentifyTime`은 클라이언트 쓰기, 명령 호출, 타이머 카운트다운에 따른 변경을 처리한다.

1. 변경 유형을 결정한다.
   - 새 값 또는 기존 값이 `0`이거나 변경 출처가 `IdentifyTimeChangeSource::kTimer`가 아니면 `DataModel::AttributeChangeType::kReportable`
   - 그 외 타이머 감소는 `DataModel::AttributeChangeType::kQuiet`
2. `SetAttributeValue`가 실제 변경이 없음을 반환하면 `DataModel::ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`으로 즉시 종료한다.
3. delegate가 있으면 상태 전환에 따라 콜백을 호출한다.
   - `0`에서 양수: `OnIdentifyStart`
   - 양수에서 `0`: `OnIdentifyStop`
4. 값이 양수이면 `StartTimer(this, System::Clock::Seconds16(1))`을 호출하고, `0`이면 `CancelTimer(this)`를 호출한다.

`TimerFired`는 `mIdentifyTime`이 양수일 때 값을 `1` 감소시킨다. `StopIdentifying`은 `IdentifyTimeChangeSource::kClient`로 값을 `0`으로 설정한다.

구현 주석은 스펙 section 5.1을 인용하여, `0`과의 전환·클라이언트 쓰기·`Identify` 명령 설정을 보고 대상으로 설명한다.

### 명령 처리

`InvokeCommand`는 입력을 디코딩한 뒤 다음과 같이 처리한다.

#### Identify

`data.identifyTime`을 `SetIdentifyTime(IdentifyTimeChangeSource::kClient, data.identifyTime)`에 전달한다.

#### TriggerEffect

먼저 `data.effectIdentifier`와 `data.effectVariant`를 각각 `mEffectIdentifier`, `mEffectVariant`에 저장한다.

| 조건 | 처리 |
|---|---|
| `mIdentifyDelegate`가 없음 | `Success` 반환 |
| `mIdentifyTime == 0` | `OnTriggerEffect` 호출 후 `Success` 반환 |
| 식별 중이며 `kFinishEffect` | `IdentifyTime`을 `1`로 설정 |
| 식별 중이며 `kStopEffect` | `IdentifyTime`을 `0`으로 설정 |
| 식별 중이며 그 외 효과 | `IdentifyTime`을 `0`으로 설정한 뒤 `OnTriggerEffect` 호출 |

그 외 명령은 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

`AcceptedCommands`는 기본적으로 `Identify`만 제공한다. `mIdentifyDelegate`가 존재하고 `IsTriggerEffectEnabled()`가 참이면 `TriggerEffect`도 포함한다. `InvokeCommand` 내부에서는 `IsTriggerEffectEnabled()`를 별도로 검사하지 않는다.

### 기존 API 호환 계층

`CodegenIntegration.h`의 `Identify`는 기존 codegen 기반 API를 `IdentifyCluster`로 연결한다.

- 콜백 타입: `onIdentifyStartCb`, `onIdentifyStopCb`, `onEffectIdentifierCb`
- 내부 클러스터: `chip::app::RegisteredServerCluster<chip::app::Clusters::IdentifyCluster> mCluster`
- `timerDelegate`가 `nullptr`이면 `sDefaultTimerDelegate` 사용
- 생성자에서 `RegisterLegacyIdentify` 및 `CodegenDataModelProvider::Instance().Registry().Register` 호출
- 소멸자에서 registry 등록 해제 및 `UnregisterLegacyIdentify` 호출
- `firstLegacyIdentify`와 `nextIdentify`로 기존 인스턴스 목록 관리

`IdentifyLegacyDelegate`의 연결 동작은 다음과 같다.

| 메서드 | 호환 계층 동작 |
|---|---|
| `OnIdentifyStart` | `mActive = true`, `mOnIdentifyStart`가 있으면 호출 |
| `OnIdentifyStop` | `mActive = false`, `mOnIdentifyStop`이 있으면 호출 |
| `OnTriggerEffect` | `mCurrentEffectIdentifier`, `mEffectVariant` 갱신 후 `mOnEffectIdentifier`가 있으면 호출 |
| `IsTriggerEffectEnabled` | 항상 `true` 반환 |

`FindIdentifyClusterOnEndpoint`는 기존 인스턴스 목록에서 endpoint에 해당하는 `IdentifyCluster`를 반환하며, 찾지 못하면 `nullptr`을 반환한다.

`MatterIdentifyClusterInitCallback`은 `CHIP_CODEGEN_CONFIG_ENABLE_CODEGEN_INTEGRATION_LOOKUP_ERRORS`가 활성화된 경우 기존 인스턴스는 있으나 registry 등록이 없는 상태를 로그로 알린다. 다음 함수는 빈 구현이다.

- `MatterIdentifyClusterShutdownCallback`
- `MatterIdentifyPluginServerInitCallback`
- `MatterIdentifyPluginServerShutdownCallback`

## 관련 문서

### src/app/clusters/identify-server/README.md

`IdentifyCluster`의 통합 절차와 기존 API에서의 마이그레이션을 설명한다.

권장 통합 순서:

1. `chip::app::Clusters::IdentifyDelegate`를 상속하여 네 가상 메서드를 구현한다.
2. 필요한 endpoint마다 delegate, 타이머 delegate, `IdentifyCluster`를 생성한다.
3. `RegisteredServerCluster`로 등록을 구성한다.
4. 애플리케이션 초기화 시 `CodegenDataModelProvider::Instance().Registry().Register`를 호출한다.

문서는 `CodegenIntegration.h`와 `CodegenIntegration.cpp`의 호환 계층 사용을 권장하지 않는다. 새 API를 기존 API로 변환하는 코드 때문에 약 400바이트의 추가 코드 크기가 발생한다고 설명하며, `IdentifyCluster`를 직접 생성하고 등록하는 방식으로의 전환을 권장한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
