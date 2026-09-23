---
entity: Identify
ids: ['0x0003']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml', 'src/app/clusters/identify-server/IdentifyCluster.h', 'src/app/clusters/identify-server/identify-server.h', 'src/app/clusters/identify-server/IdentifyIntegrationDelegate.h', 'src/app/clusters/identify-server/CodegenIntegration.h', 'src/app/clusters/identify-server/CodegenIntegration.cpp', 'src/app/clusters/identify-server/README.md', 'src/app/clusters/identify-server/IdentifyCluster.cpp', 'data_model/1.7/clusters/Identify.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Identify

## 개요

`Identify` 클러스터는 관리자가 특정 `Node`를 식별할 수 있도록 사용됩니다. 예를 들어 디바이스의 LED를 깜박이거나, 스피커에서 비프음을 내거나, 디스플레이에 QR 코드를 표시할 수 있습니다.

- 클러스터 ID: `0x0003`
- 도메인: `General`
- 역할: `utility`
- 범위: `Endpoint`
- PICS 코드: `I`
- Revision: `6`
- 서버 및 클라이언트 지원
- 설명: 디바이스를 Identification mode로 전환하기 위한 Attributes와 commands를 제공합니다.

## 스펙

### Revision history

| Revision | Summary |
|---:|---|
| 1 | Mandatory global ClusterRevision attribute added |
| 2 | CCB 2808 |
| 3 | All Hubs changes |
| 4 | New data model format and notation; add IdentifyType |
| 5 | Removed Query feature |
| 6 | Added Q quality for IdentifyTime attribute |

### 데이터 타입

#### `IdentifyTypeEnum`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0x00` | `None` | No presentation. |
| `0x01` | `LightOutput` | Light output of a lighting product. |
| `0x02` | `VisibleIndicator` | Typically a small LED. |
| `0x03` | `AudibleBeep` |  |
| `0x04` | `Display` | Presentation will be visible on display screen. |
| `0x05` | `Actuator` | Presentation will be conveyed by actuator functionality such as through a window blind operation or in-wall relay. |

#### `EffectIdentifierEnum`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0x00` | `Blink` | e.g., Light is turned on/off once. |
| `0x01` | `Breathe` | e.g., Light is turned on/off over 1 second and repeated 15 times. |
| `0x02` | `Okay` | e.g., Colored light turns green for 1 second; non-colored light flashes twice. |
| `0x0B` | `ChannelChange` | e.g., Colored light turns orange for 8 seconds; non-colored light switches to the maximum brightness for 0.5s and then minimum brightness for 7.5s. |
| `0xFE` | `FinishEffect` | Complete the current effect sequence before terminating. |
| `0xFF` | `StopEffect` | Terminate the effect as soon as possible. |

#### `EffectVariantEnum`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0x00` | `Default` | Indicates the default effect is used |

### Attributes

| ID | 이름 | 타입 | 접근 | 권한 | 품질 |
|---:|---|---|---|---|---|
| `0x0000` | `IdentifyTime` | `uint16` | 읽기/쓰기 | 읽기: `view`, 쓰기: `operate` | `quieterReporting` |
| `0x0001` | `IdentifyType` | `IdentifyTypeEnum` | 읽기 | `view` |  |
| `0xFFFD` | `ClusterRevision` |  | 전역 Attribute |  | 값 `6` |

`IdentifyTime`과 `IdentifyType`은 Mandatory입니다.

### Commands

#### `Identify`

- Command ID: `0x00`
- 방향: `commandToServer`
- Invoke privilege: `manage`
- Conformance: Mandatory
- 설명: 수신 디바이스가 자신을 식별하기 시작하거나 중지합니다.

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `IdentifyTime` | `uint16` |

#### `TriggerEffect`

- Command ID: `0x40`
- 방향: `commandToServer`
- Invoke privilege: `manage`
- Conformance: Optional
- 설명: 특정 light effect와 같은 사용자 피드백을 지원합니다.

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `EffectIdentifier` | `EffectIdentifierEnum` |
| `1` | `EffectVariant` | `EffectVariantEnum` |

## SDK 정의

SDK 데이터 모델 정의는 `src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml`에 있습니다.

### 클러스터 정의

```xml
<cluster>
  <domain>General</domain>
  <name>Identify</name>
  <code>0x0003</code>
  <define>IDENTIFY_CLUSTER</define>
  <client tick="false" init="false">true</client>
  <server tick="false" init="false">true</server>
</cluster>
```

### Enum

- `IdentifyTypeEnum`: `enum8`
  - `None`: `0x00`
  - `LightOutput`: `0x01`
  - `VisibleIndicator`: `0x02`
  - `AudibleBeep`: `0x03`
  - `Display`: `0x04`
  - `Actuator`: `0x05`
- `EffectIdentifierEnum`: `enum8`
  - `Blink`: `0x00`
  - `Breathe`: `0x01`
  - `Okay`: `0x02`
  - `ChannelChange`: `0x0B`
  - `FinishEffect`: `0xFE`
  - `StopEffect`: `0xFF`
- `EffectVariantEnum`: `enum8`
  - `Default`: `0x00`

### SDK Attribute 및 Command

- Server Attribute `IdentifyTime`
  - ID: `0x0000`
  - 타입: `int16u`
  - Writable: `true`
- Server Attribute `IdentifyType`
  - ID: `0x0001`
  - 타입: `IdentifyTypeEnum`
  - 최대값: `0x05`
- Client Command `Identify`
  - ID: `0x00`
  - Field: `IdentifyTime`, 타입 `int16u`
  - Invoke privilege: `manage`
- Client Command `TriggerEffect`
  - ID: `0x40`
  - Optional
  - Field: `EffectIdentifier`, 타입 `EffectIdentifierEnum`
  - Field: `EffectVariant`, 타입 `EffectVariantEnum`
  - `EffectVariant` 최대값: `0x00`
  - Invoke privilege: `manage`

## 구현

### `IdentifyCluster`

구현 파일:

- `src/app/clusters/identify-server/IdentifyCluster.h`
- `src/app/clusters/identify-server/IdentifyCluster.cpp`

`IdentifyCluster`는 다음 클래스를 상속합니다.

```cpp
class IdentifyCluster : public DefaultServerCluster,
                        public TimerContext,
                        public IdentifyIntegrationDelegate
```

생성자 설정은 `IdentifyCluster::Config`를 사용합니다.

```cpp
IdentifyCluster cluster(
    IdentifyCluster::Config(kEndpointId, myTimerDelegate)
        .WithDelegate(&myIdentifyDelegate)
);
```

`Config`가 제공하는 설정 메서드는 다음과 같습니다.

- `WithIdentifyType(Identify::IdentifyTypeEnum type)`
- `WithDelegate(IdentifyDelegate * delegate)`
- `WithEffectIdentifier(Identify::EffectIdentifierEnum effect)`
- `WithEffectVariant(Identify::EffectVariantEnum variant)`

기본값은 다음과 같습니다.

- `identifyType`: `Identify::IdentifyTypeEnum::kNone`
- `identifyDelegate`: `nullptr`
- `effectIdentifier`: `Identify::EffectIdentifierEnum::kBlink`
- `effectVariant`: `Identify::EffectVariantEnum::kDefault`

### `IdentifyDelegate`

`IdentifyDelegate`는 애플리케이션에 Identification 상태 변경과 Effect 실행을 알립니다.

```cpp
class IdentifyDelegate
{
public:
    virtual void OnIdentifyStart(IdentifyCluster & cluster) = 0;
    virtual void OnIdentifyStop(IdentifyCluster & cluster) = 0;
    virtual void OnTriggerEffect(IdentifyCluster & cluster) = 0;
    virtual bool IsTriggerEffectEnabled() const = 0;
};
```

### `IdentifyTime` 처리

`SetIdentifyTime`은 다음 변경 원인을 구분합니다.

```cpp
enum class IdentifyTimeChangeSource
{
    kClient,
    kTimer,
};
```

동작은 다음과 같습니다.

- `IdentifyTime`이 `0`에서 양수로 변경되면 `OnIdentifyStart`를 호출합니다.
- `IdentifyTime`이 양수에서 `0`으로 변경되면 `OnIdentifyStop`을 호출합니다.
- `IdentifyTime`이 양수이면 `TimerDelegate::StartTimer`로 1초 타이머를 시작합니다.
- `IdentifyTime`이 `0`이면 타이머를 취소합니다.
- 타이머에 의한 중간 카운트다운 변경은 `kQuiet`로 처리됩니다.
- `0`과 양수 사이의 전환, 클라이언트 쓰기, `Identify` command에 의한 변경은 reportable로 처리됩니다.

`StopIdentifying()`은 `IdentifyTime`을 `0`으로 설정하여 Identification을 중지합니다.

```cpp
void StopIdentifying();
bool IsIdentifying() override { return mIdentifyTime > 0; }
```

### `TriggerEffect` 처리

`TriggerEffect` command 수신 시:

- `EffectIdentifier`와 `EffectVariant`를 저장합니다.
- `IdentifyDelegate`가 없으면 성공 상태를 반환합니다.
- Identification 중이 아니면 즉시 `OnTriggerEffect`를 호출합니다.
- `EffectIdentifier`가 `kFinishEffect`이면 현재 Identification을 `IdentifyTime` `1`로 설정합니다.
- `EffectIdentifier`가 `kStopEffect`이면 `IdentifyTime`을 `0`으로 설정합니다.
- 그 외의 Effect는 현재 Identification을 중지한 후 `OnTriggerEffect`를 호출합니다.

`AcceptedCommands`는 `IdentifyDelegate`가 존재하고 `IsTriggerEffectEnabled()`가 `true`를 반환할 때 `TriggerEffect`를 포함합니다.

### `IdentifyIntegrationDelegate`

파일:

- `src/app/clusters/identify-server/IdentifyIntegrationDelegate.h`

`IdentifyIntegrationDelegate`는 디바이스가 현재 Identification 중인지 확인하기 위한 인터페이스입니다.

```cpp
class IdentifyIntegrationDelegate
{
public:
    virtual bool IsIdentifying() = 0;
};
```

이 인터페이스는 테스트 시 mocking을 쉽게 하고 통합 지점을 명확하게 하기 위해 `IdentifyCluster`와 분리되어 있습니다.

### Codegen 호환 계층

파일:

- `src/app/clusters/identify-server/CodegenIntegration.h`
- `src/app/clusters/identify-server/CodegenIntegration.cpp`
- `src/app/clusters/identify-server/identify-server.h`

`CodegenIntegration.h`의 `Identify`는 기존 codegen 기반 구현과의 backward compatibility를 제공합니다. 내부적으로 새 code-driven 구현인 `IdentifyCluster`로 연결됩니다.

```cpp
struct Identify
{
    using onIdentifyStartCb    = void (*)(Identify *);
    using onIdentifyStopCb     = onIdentifyStartCb;
    using onEffectIdentifierCb = onIdentifyStartCb;
};
```

`Identify` 생성자는 다음 정보를 받습니다.

- `endpoint`
- `onIdentifyStart`
- `onIdentifyStop`
- `identifyType`
- `onEffectIdentifier`
- `effectIdentifier`
- `effectVariant`
- `timerDelegate`

생성 시 `IdentifyCluster`를 구성하고 `CodegenDataModelProvider::Instance().Registry().Register`를 통해 등록합니다. 소멸 시 클러스터를 unregister합니다.

`FindIdentifyClusterOnEndpoint(chip::EndpointId endpoint)`는 해당 Endpoint의 `IdentifyCluster`를 반환합니다.

기존 API 호환 계층은 약 `400 bytes`의 추가 code size overhead가 있으므로 사용이 권장되지 않습니다.

## 예시

### 새 code-driven 구현

```cpp
#include "app/clusters/identify-server/IdentifyCluster.h"

class MyIdentifyDelegate : public chip::app::Clusters::IdentifyDelegate
{
public:
    void OnIdentifyStart(chip::app::Clusters::IdentifyCluster & cluster) override
    {
        // 식별 시작 처리
    }

    void OnIdentifyStop(chip::app::Clusters::IdentifyCluster & cluster) override
    {
        // 식별 중지 처리
    }

    void OnTriggerEffect(chip::app::Clusters::IdentifyCluster & cluster) override
    {
        // 특정 Effect 처리
    }

    bool IsTriggerEffectEnabled() const override { return true; }
};
```

```cpp
#include "platform/DefaultTimerDelegate.h"
#include "app/server-cluster/ServerClusterInterfaceRegistry.h"

MyIdentifyDelegate gMyIdentifyDelegate;
DefaultTimerDelegate gTimerDelegate;

chip::app::RegisteredServerCluster<chip::app::Clusters::IdentifyCluster> gIdentifyCluster(
    chip::app::Clusters::IdentifyCluster::Config(kYourEndpointId, gTimerDelegate)
        .WithIdentifyType(chip::app::Clusters::Identify::IdentifyTypeEnum::kVisibleIndicator)
        .WithDelegate(&gMyIdentifyDelegate));
```

애플리케이션 초기화 시 `CodegenDataModelProvider`에 등록합니다.

```cpp
#include "data-model-providers/codegen/CodegenDataModelProvider.h"

void ApplicationInit()
{
    CHIP_ERROR err =
        chip::app::CodegenDataModelProvider::Instance().Registry().Register(
            gIdentifyCluster.Registration());
    VerifyOrDie(err == CHIP_NO_ERROR);
}
```

### Legacy 구현

Legacy API는 기존 ZAP-generated 패턴과의 호환성을 위해 제공되며, 사용은 권장되지 않습니다.

```cpp
#include <app/clusters/identify-server/identify-server.h>

void OnIdentifyStart(::Identify *) {}
void OnIdentifyStop(::Identify *) {}
void OnTriggerEffect(::Identify * identify) {}

static Identify gIdentify1 = {
    chip::EndpointId{ 1 },
    OnIdentifyStart,
    OnIdentifyStop,
    Clusters::Identify::IdentifyTypeEnum::kVisibleIndicator,
    OnTriggerEffect,
};
```

## 관련 문서

- `data_model/1.7/clusters/Identify.xml`
- `src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml`
- `src/app/clusters/identify-server/IdentifyCluster.h`
- `src/app/clusters/identify-server/IdentifyCluster.cpp`
- `src/app/clusters/identify-server/IdentifyIntegrationDelegate.h`
- `src/app/clusters/identify-server/CodegenIntegration.h`
- `src/app/clusters/identify-server/CodegenIntegration.cpp`
- `src/app/clusters/identify-server/identify-server.h`
- `src/app/clusters/identify-server/README.md`