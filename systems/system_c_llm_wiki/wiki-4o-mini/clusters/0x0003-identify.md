---
entity: Identify
ids: ['0x0003']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/identify-cluster.xml', 'src/app/clusters/identify-server/IdentifyCluster.h', 'src/app/clusters/identify-server/identify-server.h', 'src/app/clusters/identify-server/IdentifyIntegrationDelegate.h', 'src/app/clusters/identify-server/CodegenIntegration.h', 'src/app/clusters/identify-server/CodegenIntegration.cpp', 'src/app/clusters/identify-server/README.md', 'src/app/clusters/identify-server/IdentifyCluster.cpp', 'data_model/1.7/clusters/Identify.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요

Identify 클러스터는 관리자가 특정 노드를 식별하는 데 사용됩니다. 예를 들어, 장치의 LED를 깜빡이게 하거나 스피커에서 비프음을 발생시키거나 디스플레이에 QR 코드를 표시하는 데 사용할 수 있습니다.

이 디렉토리는 Matter Identify 클러스터 서버의 코드 기반 C++ 구현을 포함하고 있습니다. 이 구현(`IdentifyCluster.h`)은 유연성을 위해 설계되었으며, 이전 ZAP/Ember 기반 구현에서의 긴밀한 결합을 피합니다.

위임 패턴(`chip::app::Clusters::IdentifyDelegate`)을 사용하여 식별 시작 및 중지와 같은 클러스터 관련 이벤트를 애플리케이션에 알립니다.

## 스펙

카탈로그의 정리된 형식:

```xml
<cluster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="types types.xsd cluster cluster.xsd" id="0x0003" name="Identify Cluster" revision="6">
  ...
</cluster>
```
- **클러스터 ID**: 0x0003
- **속성**:
  - **IdentifyTime**: uint16 (읽기/쓰기 가능)
  - **IdentifyType**: IdentifyTypeEnum (읽기 가능)
- **명령**:
  - **Identify**: identifies the time (uint16)
  - **TriggerEffect**: triggers a specified effect (EffectIdentifierEnum, EffectVariantEnum)

## SDK 정의

```cpp
namespace chip::app::Clusters {

class IdentifyDelegate {
public:
    virtual ~IdentifyDelegate() = default;

    virtual void OnIdentifyStart(IdentifyCluster & cluster) = 0;
    virtual void OnIdentifyStop(IdentifyCluster & cluster) = 0;
    virtual void OnTriggerEffect(IdentifyCluster & cluster) = 0;
    virtual bool IsTriggerEffectEnabled() const = 0;
};

class IdentifyCluster {
public:
    struct Config {
        constexpr Config(EndpointId endpoint, TimerDelegate & delegate) : endpointId(endpoint), timerDelegate(delegate) {}
        ...
    };
    
    IdentifyCluster(const Config & config);
    ...
    void StopIdentifying();
};
} // namespace chip::app::Clusters
```

## 구현

Identify 클러스터의 구현은 다음과 같은 주요 구성 요소로 나눌 수 있습니다.

- **IdentifyCluster.h** 및 **IdentifyCluster.cpp**: 클러스터의 메인 구현.
- **IdentifyIntegrationDelegate.h**: identifiying 상태에 대한 정보를 제공하는 구조체.
- **CodegenIntegration.h** 및 **CodegenIntegration.cpp**: 기존 코드와의 하위 호환성을 위해 제공되는 레거시 API.

주요 메서드:

```cpp
DataModel::ActionReturnStatus IdentifyCluster::ReadAttribute(const DataModel::ReadAttributeRequest & request, AttributeValueEncoder & encoder);
DataModel::ActionReturnStatus IdentifyCluster::WriteAttribute(const DataModel::WriteAttributeRequest & request, AttributeValueDecoder & decoder);
std::optional<DataModel::ActionReturnStatus> IdentifyCluster::InvokeCommand(const DataModel::InvokeRequest & request, TLV::TLVReader & input_arguments, CommandHandler * handler);
```

## 예시

IdentifyCluster를 애플리케이션에 통합하려면 다음 단계를 따릅니다.

### 1. Delegate 구현

`chip::app::Clusters::IdentifyDelegate`를 상속하는 클래스를 생성하고 식별 이벤트를 처리하기 위해 가상 메서드를 구현합니다.

```cpp
class MyIdentifyDelegate : public chip::app::Clusters::IdentifyDelegate {
public:
    void OnIdentifyStart(chip::app::Clusters::IdentifyCluster & cluster) override {
        // 식별 시작 로직
    }
    ...
};
```

### 2. Delegates 및 Cluster 인스턴스화

델리게이트, 타이머 델리게이트 및 `IdentifyCluster`를 각 엔드포인트에 대해 인스턴스화합니다.

```cpp
MyIdentifyDelegate gMyIdentifyDelegate;
DefaultTimerDelegate gTimerDelegate;
chip::app::RegisteredServerCluster<chip::app::Clusters::IdentifyCluster> gIdentifyCluster(
    chip::app::Clusters::IdentifyCluster::Config(kYourEndpointId, gTimerDelegate)
        .WithIdentifyType(chip::app::Clusters::Identify::IdentifyTypeEnum::kVisibleIndicator)
        .WithDelegate(&gMyIdentifyDelegate));
```

### 3. 클러스터 등록

응용 프로그램 초기화 속에서 클러스터 인스턴스를 `CodegenDataModelProvider`에 등록합니다.

```cpp
void ApplicationInit() {
    CHIP_ERROR err = chip::app::CodegenDataModelProvider::Instance().Registry().Register(gIdentifyCluster.Registration());
    VerifyOrDie(err == CHIP_NO_ERROR);
}
```

## 관련 문서

- [IdentifyCluster.h](src/app/clusters/identify-server/IdentifyCluster.h)
- [IdentifyCluster.cpp](src/app/clusters/identify-server/IdentifyCluster.cpp)
- [Identify Integration Delegate](src/app/clusters/identify-server/IdentifyIntegrationDelegate.h)
- [Identify Cluster Spec](data_model/1.7/clusters/Identify.xml)