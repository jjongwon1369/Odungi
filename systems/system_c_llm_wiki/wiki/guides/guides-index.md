---
entity: all
ids: []
source_paths: ['docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md', 'docs/guides/matter_idl_tooling.md', 'docs/guides/writing_clusters.md']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-5.6-luna
---

## 개요

새로운 Matter 클러스터 및 디바이스 타입 개발의 목표는 다음과 같다.

1. 클러스터 구현 작성
2. ZAP가 적절한 Ember 계층을 생성할 수 있도록 코드와 지원 자료 작성
3. 코드의 정확성을 검증하고 새로운 기능의 인증을 지원하는 단위 테스트, 테스트 계획 및 자동화 스크립트 작성

단위 테스트, 테스트 계획 및 인증 테스트는 testing 섹션에서 다룬다. 이 문서는 SDK에서 클러스터와 디바이스 타입을 구현하는 방법에 집중한다.

### 개발 구성 요소

- **Cluster Definition**
  - XML로 정의한다.
  - 구조체, 열거형, 속성, 명령, 이벤트 등을 설명한다.
  - Matter specification을 코드로 직접 변환한 것이다.
  - 정의 위치: `src/app/zap-templates/zcl/data-model/chip/`
- **Cluster Implementation**
  - 클라이언트 측: codegen을 사용하고 glue code를 작성한다.
  - 서버 측: Ember 및/또는 `AttributeAccessInterface`, `CommandHandlerInterface`를 통한 C++ 구현
  - 구현 위치: `src/app/clusters/<your_cluster_name>`
  - 빌드 파일: `src/app/chip_data_model.gni`
  - 빌드 파일은 codegen 데이터를 사용해 클러스터 목록을 자동으로 구성한다.
  - ZAP에서 선택했을 때 코드가 이미지에 포함되도록 기존 예시를 따른다.
- **Device Type Definitions**
  - XML에서 conformance를 정의한다.
  - 정의 파일: `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml`

구체적인 정의 위치와 ZAP/Ember/SDK에 올바르게 반영하는 방법은 [How To Add New Device Types & Clusters](how_to_add_new_dts_and_clusters.md)를 참고한다.

생성된 출력은 [.matter parser tools](https://project-chip.github.io/connectedhomeip-doc/guides/matter_idl_tooling.html)를 사용해 specification과 비교하여 검증해야 한다.

### ZAP, Ember 및 Overrides

#### ZAP에서 클러스터 정의 확인

새 클러스터가 ZAP에서 사용되도록 하려면 XML과 glue code를 반영해야 한다.

[ZAP](../zap_and_codegen/zap_intro.md)의 소개 문서를 참고한다.

변경 후 `zaptool`을 실행하여 클러스터와 디바이스 타입이 표시되는지 확인한다.

```sh
./scripts/tools/zap/run_zaptool.sh <filename>
```

endpoint configuration을 열고 디바이스 타입 목록에 디바이스 타입이 표시되는지 확인한다.

그 다음 클러스터를 확인한다.

- XML의 `domain` 파라미터가 클러스터가 속한 그룹을 결정한다.
- 예상한 모든 속성, 명령 및 이벤트가 표시되어야 한다.
- 각 속성의 storage 옵션이 적절하게 설정되어야 한다.

#### Ember와 Overrides

- **Ember**
  - 디바이스의 endpoints, attributes, commands 등에 대한 설정과 접근에 사용되는 계층이다.
  - 빌드 과정에서 Ember 함수 시그니처와 기본값을 생성한다.
  - 클러스터 서버 코드는 초기화, 명령, 속성 접근 및 이벤트 생성을 위한 callback을 구현한다.
  - Interaction Model 계층은 클러스터에 대한 incoming interaction을 수신하면 Ember 함수를 호출한다.
- **Overrides**
  - Ember 계층은 컴파일 시 생성되지만, overrides는 런타임에 설치된다.
  - 속성 접근 또는 명령 처리를 할 때 Ember 계층보다 먼저 호출된다.
  - `AttributeAccessInterface` 및 `CommandHandlerInterface`를 사용한다.
  - 더 많은 제어를 제공하지만 구현이 더 복잡하다.
  - 단위 테스트가 가능하다.
  - ZAP에서 설정한 경우 두 방식 모두 Ember 계층으로 fall through할 수 있다.

### 클러스터 서버 초기화

메시지는 Matter core에서 시작하여 클러스터 초기화 코드까지 다음 흐름으로 전달된다.

- `EmberAfInitializeAttributes`
  - Ember attribute storage를 초기화한다.
  - ZAP에서 `RAM`으로 표시된 모든 속성에 대해 storage를 할당한다.
  - storage에 기본값을 설정한다.
- `Matter<Cluster>PluginServerCallback`
  - `.h` 파일은 생성 파일이다.
  - `.cpp` 구현은 서버 클러스터 코드에서 작성한다.
  - 클러스터 설정 및 override 등록에 사용한다.
- `chip::app::AttributeAccessInterfaceRegistry::Instance().Register`
  - 속성 읽기와 쓰기를 외부에서 처리하려는 경우 사용한다.

### 클러스터 서버 속성

속성 처리에는 다음 두 가지 메커니즘이 있다.

- Ember 계층
- Override

#### `RAM` storage 속성

ZAP 파일에서 storage가 **`RAM`**으로 표시된 속성은 다음과 같이 처리된다.

- storage가 자동으로 할당된다.
- Ember가 읽기와 쓰기를 처리한다.
- 생성된 `Accessors.h`에 각 속성에 대한 `Get` 및 `Set` 함수가 생성된다.
- 클러스터에 override를 등록할 수 있다.
- override에서 해당 속성을 처리하지 않으면 Ember storage로 fall through한다.
- access override 함수에서 항상 해당 속성을 encode하면 불필요하게 공간을 사용하게 된다.

#### `External` storage 속성

ZAP 파일에서 storage가 **`External`**로 표시된 속성은 다음과 같이 처리된다.

- storage가 할당되지 않는다.
- Ember storage로 fall through하지 않는다.
- 동작하려면 access override를 등록해야 한다.

#### Override를 통한 속성 읽기

`AttributeAccessInterface::Read()`에서 `aPath`를 분석하여 요청된 속성을 판별하고 값을 encode한다.

```cpp
CHIP_ERROR Read(const ConcreteReadAttributePath & aPath,
                AttributeValueEncoder & aEncoder)
{
    // Parse aPath to determine the requested attribute
    switch (aPath.mAttributeId)
    {
    case SomeAttribute::Id:
        // Just encode the value
        aEncoder.Encode(mSomeValue);
        break;
    }
    // Beware of lists - the need to use EncodeList to have chunking handled properly
    return CHIP_NO_ERROR;
```

list 속성은 chunking이 올바르게 처리되도록 `EncodeList`를 사용해야 한다.

#### Override를 통한 속성 쓰기

속성 쓰기는 읽기와 동일한 경로를 사용하지만 `AttributeAccessInterface::Write()`에서 처리된다.

속성 handler는 다음을 담당한다.

- 제약 조건 검사
- 속성 persistence

#### Attribute Persistence

`AttributeAccessInterface`를 사용하는 경우 persistence가 필요한 속성을 직접 관리해야 한다.

- `AttributePersistence`를 `AttributePersistenceProvider`와 함께 사용할 수 있다.
- 모든 타입의 값을 기본 `PersistenceProvider`에서 읽고 쓸 수 있는 API를 제공한다.
- 관련 파일: `src/app/AttributePersistence.h`
- 단위 테스트에서는 `TestPersistentStorageDelegate`와 `DefaultAttributePersistenceProvider`를 함께 사용할 수 있다.

#### Ember 계층의 속성 읽기와 쓰기

Ember 계층 함수에서는 Ember 계층이 encode와 decode를 처리한다.

- 단순한 속성에는 적합하다.
- 복잡한 속성 interaction에는 구현이 어려울 수 있다.
- 단위 테스트가 매우 어렵다.
- 속성 변경을 처리할 수 있도록 callback을 제공한다.

```cpp
void MatterPostAttributeChangeCallback(const chip::app::ConcreteAttributePath & attributePath,
                                       uint8_t type, uint16_t size, uint8_t * value)
```

이 callback은 여러 example에서 사용할 수 있도록 구현해야 한다.

### 클러스터 서버 명령

속성과 마찬가지로 명령에도 Ember 계층 방식과 override 방식이 있다.

#### Override

- 런타임에 등록된다.
- `InteractionModelEngine::RegisterCommandHandler`를 사용한다.
- `CommandHandlerInterface`를 구현한다.

#### Ember

- 정적으로 처리된다.
- `emberAf<ClusterName><CommandName>Callback`을 사용한다.

#### 명령 handler 구현

`CommandHandlerInterface`는 다음과 같이 사용할 수 있다.

- `HandleCommand` 함수를 사용하면 명령을 처리됨으로 설정할 수 있다.
- `HandleCommand`를 사용하지 않으면 명령 처리 여부를 직접 설정해야 한다.
- 처리되지 않은 명령은 기본적으로 Ember로 fall through한다.
- 명령이 전적으로 `CommandHandlerInterface`에서 처리되면 `src/app/common/templates/config-data.yaml`에 해당 명령의 Ember 생성을 비활성화한다.

Ember interface는 다음을 따른다.

- 명령을 처리했으면 `true`를 반환한다.
- `false`를 반환하면 invalid command response가 반환된다.

두 방식 모두 다음을 처리해야 한다.

- `AddResponse` 또는 `AddStatus`를 사용하여 caller에게 결과 반환
- specification에 따른 제약 조건 검사
- 적절한 status 또는 response 반환

`config-data.yaml`은 순수한 `CommandHandlerInterface` 구현을 사용하는 클러스터의 Ember command callback 생성을 끄는 데 사용된다.

### 이벤트와 속성 subscription

#### 속성 변경 reporting

Ember storage 계층을 사용하는 경우, 생성된 속성 `Get` 및 `Set` 함수가 변경 reporting을 처리한다.

`AttributeAccessInterface`를 사용하는 경우에는 속성이 변경되었음을 reporting engine에 알려야 한다.

- `MatterReportingAttributeChangeCallback`을 사용한다.

#### 이벤트

- Ember에서 이벤트를 직접 지원하지 않는다.
- `EventLogging.h`의 `LogEvent` 함수를 호출한다.
- `LogEvent`를 사용할 때 호출자는 Matter stack lock을 획득하거나 이벤트를 Matter event queue에 추가해야 한다.

### Dynamic Endpoints

ZAP configuration은 컴파일 시 정적으로 구성된다. 그러나 런타임에 dynamic endpoint를 등록할 수도 있으며 bridge에서 일반적으로 사용된다.

- `emberAfSetDynamicEndpoint`를 사용한다.
- 속성 등을 자체 storage에 저장한다면 dynamic endpoint와 static endpoint를 모두 고려해야 한다.

### 새로운 code-driven 클러스터 작성

새 클러스터 구현은 다음 단계로 진행한다.

1. Matter specification에 기반하여 클러스터 definition XML을 생성하거나 업데이트한다.
2. 클러스터의 C++ 로직과 데이터 관리를 구현한다.
3. 빌드 시스템에 필요한 파일을 추가한다.
4. 애플리케이션의 code generation configuration에 연결한다.
5. 단위 테스트와 integration test를 추가한다.

#### XML 정의

클러스터 XML은 다음 위치에 있다.

`src/app/zap-templates/zcl/data-model/chip`

XML 생성 및 업데이트 시에는 [Alchemy](https://github.com/project-chip/alchemy)를 사용하여 specification의 `asciidoc`을 파싱하는 것을 권장한다. XML 수동 편집은 오류가 발생하기 쉬우므로 권장하지 않는다.

XML을 준비한 후 다음 명령으로 code generation을 실행한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

#### C++ 파일 구조

클러스터 디렉터리를 다음 위치에 생성한다.

`src/app/clusters/<cluster-directory>/`

이 디렉터리에 클러스터 구현과 단위 테스트를 둔다.

ZAP 기반 지원을 위한 디렉터리 매핑은 `src/app/zap_cluster_list.json`의 `ServerDirectories` 키에 정의한다. 이 매핑은 클러스터의 `UPPER_SNAKE_CASE` define을 `src/app/clusters` 아래의 디렉터리 이름으로 연결한다.

일반적인 명명 규칙은 다음과 같다.

- 클러스터 디렉터리: `cluster-name-server`
- `ServerClusterInterface` 구현: `ClusterNameSnakeCluster.h/cpp`

#### 권장 구현 패턴

리소스가 제한된 디바이스의 flash 및 RAM 사용량을 줄이기 위해 combined implementation 패턴을 권장한다.

- 클러스터 로직, 데이터 storage 및 `ServerClusterInterface` 구현을 하나의 클래스에 포함한다.
- 일반적으로 `DefaultServerCluster`를 상속한다.
- 불필요한 boilerplate와 virtual function translation layer를 줄여 flash 사용량을 줄인다.
- [Basic Information](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/basic-information) 클러스터가 예시이다.

`ClusterLogic`을 사용하는 modular implementation은 기존 방식이며 새로운 클러스터에는 권장하지 않는다.

- `ClusterLogic`에 핵심 business logic을 분리한다.
- `ClusterImplementation`은 translation layer로 동작한다.
- 테스트 격리에는 유리하지만 flash와 RAM overhead가 증가한다.
- [Administrator Commissioning](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/administrator-commissioning-server) 클러스터가 legacy 예시이다.

`ClusterDriver` 또는 `Delegate`는 애플리케이션에 클러스터 interaction callback을 제공하는 선택적 interface이다. 혼동을 줄이기 위해 `Delegate`보다 `Driver`라는 용어를 권장한다.

### 클러스터 초기화와 configuration

새 code-driven 클러스터는 builder-style `Config` 패턴을 사용해야 한다. 이 패턴은 feature가 활성화되었을 때 필수 parameter가 누락되는 오류를 방지한다.

주요 원칙은 다음과 같다.

- 메인 클러스터 클래스 안에 startup state를 보관하는 중첩 `Config` struct 또는 class를 정의한다.
- 복잡한 configuration은 private member를 가진 `class`로 캡슐화한다.
- 간단한 configuration은 public member를 가진 `struct`를 사용할 수 있다.
- `With<Feature>(...)` 형태의 fluent builder API를 제공한다.
- builder method는 `Config` 객체에 대한 reference를 반환하여 chained call을 지원한다.
- feature map bit 설정과 연관 속성 초기화를 하나의 atomic operation으로 처리한다.
- conformance logic을 configuration API에 캡슐화한다.
- `EndpointId`는 `Config`에 저장하지 않고 클러스터 constructor에 직접 전달한다.
- `Config`에서 configuration 값을 추출하여 클러스터의 별도 member 변수에 저장한다.
- 변경되지 않는 configuration 값은 `const`로 선언할 수 있다.

주요 참고 구현은 [Level Control Cluster](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/level-control/LevelControlCluster.h)이다.

```cpp
class LevelControlCluster : public DefaultServerCluster ...
{
public:
    class Config
    {
    public:
        Config(TimerDelegate & timerDelegate, LevelControlDelegate & delegate) :
            mDelegate(delegate), mTimerDelegate(timerDelegate), mFeatureMap(0) {}

        // Automatically sets the Lighting feature and sets required attribute values
        Config & WithLighting(DataModel::Nullable<uint8_t> startUpCurrentLevel)
        {
            mFeatureMap.Set(LevelControl::Feature::kLighting);
            WithMinLevel(1);   // Spec mandates MinLevel=1 for Lighting feature
            WithMaxLevel(254); // Spec mandates MaxLevel=254 for Lighting feature
            mStartUpCurrentLevel = startUpCurrentLevel;
            return *this;
        }

        Config & WithMinLevel(uint8_t minLevel)
        {
            // ... implementation
            return *this;
        }

        Config & WithMaxLevel(uint8_t maxLevel)
        {
            // ... implementation
            return *this;
        }

    private:
        friend class LevelControlCluster;
        LevelControlDelegate & mDelegate;
        TimerDelegate & mTimerDelegate;
        BitMask<LevelControl::Feature> mFeatureMap;
        DataModel::Nullable<uint8_t> mStartUpCurrentLevel;
        // ... other members
    };

    LevelControlCluster(EndpointId endpoint, const Config & config);
};
```

### 애플리케이션 개발을 단순화하는 설계

클러스터는 가능한 많은 작업을 내부에서 처리하여 애플리케이션 개발자의 부담을 줄여야 한다.

- persistence(NVM), timer 및 복잡한 state machine을 클러스터 내부에서 처리한다.
- 애플리케이션에는 처리해야 할 중요한 이벤트나 변경만 알린다.
- 복잡한 로직이 필요한 경우 helper class 또는 default implementation을 제공한다.
- raw storage key나 개별 timer 관리와 같은 저수준 세부 사항을 애플리케이션으로 넘기지 않는다.

### Delegate/Driver를 통한 validation

애플리케이션이 클러스터 operation에 관여해야 하는 경우 delegate 또는 driver interface를 pre-check 용도로 사용한다.

- writable attribute에는 새 값이 적용되거나 persistence되기 전에 수락 또는 거부할 수 있는 callback을 제공한다.
- callback은 `Protocols::InteractionModel::Status`를 반환한다.
- `Success`가 아닌 status를 반환하면 애플리케이션이 변경을 거부한 것으로 처리한다.
- 클러스터는 애플리케이션 delegate를 호출하기 전에 specification에 정의된 range, constraint 및 state 검사를 수행한다.
- 값이 변경되지 않는 no-op operation은 delegate callback이나 change notification을 발생시키지 않는다.

각 mutable attribute에는 `On<AttributeName>Changed` callback을 제공한다.

- specification validation과 no-op guard 이후, 값이 commit되기 전에 호출한다.
- 현재 값이 아닌 **제안된 새 값**을 전달해야 한다.
- `true`는 변경을 수락한다.
- `false`는 변경을 거부한다.
- `Status` 반환 API에서는 `Protocols::InteractionModel::Status::Failure`를 사용한다.
- `CHIP_ERROR` 반환 API에서는 `CHIP_ERROR_INCORRECT_STATE`를 사용한다.
- 기본 구현은 `true`를 반환하여 애플리케이션이 필요한 callback만 override할 수 있도록 한다.

예시는 `boolean-state-configuration-delegate.h`의 다음 callback을 따른다.

```cpp
virtual bool OnCurrentSensitivityLevelChanged(uint8_t newValue) { return true; }
virtual bool OnAlarmsActiveChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnAlarmsSuppressedChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnAlarmsEnabledChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnSensorFaultChanged(chip::BitMask<SensorFaultBitmap> newValue) { return true; }
```

표준 처리 순서는 다음과 같다.

1. specification validation
2. no-op guard
3. delegate 호출
4. 값 commit
5. notification

```cpp
VerifyOrReturnError(level < mSupportedSensitivityLevels, CHIP_IM_GLOBAL_STATUS(ConstraintError));
VerifyOrReturnError(mCurrentSensitivityLevel != level, CHIP_NO_ERROR);

if (mDelegate != nullptr)
{
    VerifyOrReturnError(mDelegate->OnCurrentSensitivityLevelChanged(level), CHIP_ERROR_INCORRECT_STATE);
}

mCurrentSensitivityLevel = level;
NotifyAttributeChanged(CurrentSensitivityLevel::Id);
```

### Attribute accessor

클러스터 구현은 애플리케이션이 클러스터 state와 상호작용할 수 있도록 각 attribute에 public getter와 setter API를 제공해야 한다.

- 모든 attribute에 getter를 제공한다.
- 가능하면 getter는 값을 복사하여 반환한다.
- 내부 데이터에 대한 pointer나 reference 반환은 lifetime 문제를 만들 수 있으므로 피한다.
- mutable attribute에는 specification을 준수하는 setter를 제공한다.
- 여러 attribute를 atomic하게 변경해야 하는 경우 개별 setter 대신 상위 수준 API를 제공한다.
- setter는 attribute change notification도 발생시켜야 한다.

참고 구현은 [Boolean State Configuration](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/boolean-state-configuration-server/BooleanStateConfigurationCluster.h)이다.

### Attribute change notification

subscription이 올바르게 동작하려면 attribute 값이 변경될 때 시스템에 알려야 한다.

클러스터의 `Startup` method는 `ServerClusterContext`를 받는다. 다음을 사용하여 attribute를 dirty로 표시할 수 있다.

```cpp
interactionContext->dataModelChangeListener->MarkDirty(path)
```

이 클러스터가 관리하는 path에는 `NotifyAttributeChanged` helper를 사용할 수 있다.

쓰기 구현에서는 `WriteImpl`과 `NotifyAttributeChangedIfSuccess`를 함께 사용할 수 있다.

```cpp
DataModel::ActionReturnStatus SomeCluster::WriteAttribute(const DataModel::WriteAttributeRequest & request,
                                                          AttributeValueDecoder & decoder)
{
    // Delegate everything to WriteImpl. If write succeeds, notify that the attribute changed.
    return NotifyAttributeChangedIfSuccess(request.path.mAttributeId, WriteImpl(request, decoder));
}
```

notification이 없어야 하는 경우 `WriteImpl`은 다음을 반환해야 한다.

`ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`

no-op write는 다음을 발생시키면 안 된다.

- network attribute change notification
- application-level delegate 또는 driver callback

```cpp
VerifyOrReturnValue(mValue != newValue, ActionReturnStatus::FixedStatus::kWriteSuccessNoOp);
```

### Persistent Storage

- scalar attribute 값에는 `src/app/persistence/AttributePersistence.h`의 `AttributePersistence`를 사용한다.
- `ServerClusterContext`는 `AttributePersistenceProvider`를 제공한다.
- non-attribute 데이터에는 context가 제공하는 `PersistentStorageDelegate`를 사용한다.

### Feature와 optional item 처리

구현은 활성화된 feature와 optional item에 따라 사용 가능한 attribute 및 command를 올바르게 보고해야 한다.

- feature에 종속된 요소를 제어할 때 feature map을 사용한다.
- 순수하게 optional인 요소에는 boolean flag 또는 `BitFlags`를 사용한다.
- 서로 다른 feature 조합과 optional attribute/command 조합을 단위 테스트한다.

### 빌드 파일

`src/app/clusters/<cluster-directory>/` 아래에 다음 파일을 둔다.

#### `BUILD.gn`

`<cluster-directory>`라는 이름의 target을 정의한다. 일반적으로 `source_set`을 사용한다.

`src/app/chip_data_model.gni`에서 다음과 같이 dependency를 추가하여 참조한다.

```gn
deps += [ "${_app_root}/clusters/${cluster}" ]
```

따라서 기본 target 이름은 중요하다.

#### `app_config_dependent_sources.gni`

일반적으로 다음을 포함한다.

```gn
app_config_dependent_sources = [ "CodegenIntegration.cpp" ]
```

필요한 경우 `CodegenIntegration.h`와 같은 helper 또는 compatibility layer도 포함할 수 있다.

#### `app_config_dependent_sources.cmake`

`app_config_dependent_sources.gni`에 포함된 파일과 함께 `BUILD.gn`의 dependency가 가져오지만 CMake가 가져오지 않는 파일도 포함한다.

```cmake
TARGET_SOURCES(
  ${APP_TARGET}
  PRIVATE
    "${CLUSTER_DIR}/CodegenIntegration.cpp"
)

TARGET_SOURCES(
  ${APP_TARGET}
  PRIVATE
    "${CLUSTER_DIR}/BasicInformationCluster.cpp"
    "${CLUSTER_DIR}/BasicInformationCluster.h"
)
```

`chip_data_model.gni`와 `chip_data_model.cmake`는 이 파일들을 포함하고 Ember code-generated settings와 함께 하나의 source set으로 구성한다.

### Advanced `ServerClusterInterface`

일반적으로 `ReadAttribute`, `WriteAttribute`, `InvokeCommand`를 구현한다. 다음 method는 고급 사용 사례에 해당한다.

#### `ListAttributeWriteNotification`

큰 list attribute를 chunk 단위로 persistence하는 등 특별한 처리가 필요할 때 사용하는 callback이다. Binding cluster가 대표적인 사용 사례이며, 대부분의 클러스터에서는 기본 구현으로 충분하다.

#### `EventInfo`

non-default read permission이 필요한 event를 생성하는 경우 `EventInfo`를 구현해야 한다. 예를 들어 event에 `Administrator` privilege가 필요할 수 있다.

#### `AcceptedCommands`와 `GeneratedCommands`

REST API에 비유하면 다음과 같다.

- `AcceptedCommands`
  - server cluster가 처리할 수 있는 request
  - client에서 server로 전송되는 command
- `GeneratedCommands`
  - accepted command를 처리한 뒤 server cluster가 생성할 수 있는 response
  - server에서 client로 전송되는 command

두 목록은 Matter specification의 클러스터 정의를 기반으로 구성된다.

### Unit Testing

단위 테스트는 다음 위치에 둔다.

`src/app/clusters/<cluster-name>/tests/`

`chip::Testing::ClusterTester` utility를 사용한다. 이 API를 사용하면 encoder, handler 또는 raw TLV buffer를 직접 mock할 필요가 없다.

테스트 시 다음을 확인한다.

- mock delegate를 생성하여 클러스터 인스턴스에 주입한다.
- `Attributes()` 및 `AcceptedCommands()`가 올바른 metadata를 반환하는지 확인한다.
- `tester.ReadAttribute()`를 사용하여 `ReadAttribute`를 테스트한다.
- mock 데이터와 읽기 결과가 일치하는지 확인한다.
- `tester.Invoke()`를 사용하여 command를 테스트한다.
- delegate 응답에 따른 `Protocols::InteractionModel::Status`가 정확히 반환되는지 확인한다.
- `tester.GetDirtyList()`를 사용하여 변경된 state가 올바르게 dirty로 표시되는지 확인한다.
- no-op write에서는 dirty 표시가 발생하지 않는지 확인한다.

### Build 및 애플리케이션 통합

#### Build system 통합

`src/app/zap_cluster_list.json`에 새 클러스터를 추가하고 생성한 디렉터리를 가리키도록 한다.

#### `CodegenIntegration.cpp`

애플리케이션의 `.zap` 파일 configuration과 C++ 구현을 연결하려면 다음을 수행한다.

1. `CodegenIntegration.cpp`를 생성한다.
2. `app_config_dependent_sources.gni`와 `app_config_dependent_sources.cmake`를 생성한다.
3. code generator가 생성한 `<app/static-cluster-config/<cluster-name>.h>`를 사용하여 endpoint별 configuration을 초기화한다.
4. `CodegenIntegration.cpp`에 다음 callback을 구현한다.
   - `Matter<Cluster>ClusterInitCallback(EndpointId)`
   - `Matter<Cluster>ClusterShutdownCallback(EndpointId)`
5. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters` array에 클러스터를 추가한다.
6. `src/app/zap-templates/zcl/zcl.json` 및 `zcl-with-test-extensions.json`의 `attributeAccessInterfaceAttributes`에 list가 아닌 클러스터의 모든 attribute를 추가한다.
7. ZAP를 다시 생성한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

`attributeAccessInterfaceAttributes` 설정은 Ember framework가 클러스터 attribute용 memory를 할당하지 않도록 한다.

### 예시 애플리케이션 및 통합 테스트

- 클러스터 test coverage를 보장하는 단위 테스트를 작성한다.
- `all-clusters-app`과 같은 example application에 클러스터를 통합한다.
- `chip-tool` 또는 `matter-repl`을 사용하여 실제 환경에서 수동 검증을 수행한다.
- example application을 대상으로 end-to-end integration test를 작성한다.

## 관련 문서

- [How To Add New Device Types & Clusters](how_to_add_new_dts_and_clusters.md)
- [ZAP](../zap_and_codegen/zap_intro.md)
- [Code generation guide](../zap_and_codegen/code_generation.md)
- [The `.matter` IDL file format](docs/guides/matter_idl_tooling.md)
- [ClusterTester Helper Class Guide](../cluster_and_device_type_dev/cluster_tester.md)
- [AttributeAccessInterface](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h)
- [CommandHandlerInterface](https://github.com/project-chip/connectedhomeip/blob/master/src/app/CommandHandlerInterface.h)
- [AttributePersistence](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributePersistence.h)
- [Level Control Cluster](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/level-control/LevelControlCluster.h)
- [Basic Information](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/basic-information)
- [Administrator Commissioning](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/administrator-commissioning-server)
- [Boolean State Configuration](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/boolean-state-configuration-server/BooleanStateConfigurationCluster.h)
- `src/app/zap-templates/zcl/data-model/chip/`
- `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml`
- `src/app/chip_data_model.gni`
- `src/app/zap_cluster_list.json`
- `src/app/common/templates/config-data.yaml`
- `src/app/zap-templates/zcl/zcl.json`
- `src/app/zap-templates/zcl/zcl-with-test-extensions.json`
- `src/app/persistence/AttributePersistence.h`
- `data_model/clusters`
- `data_model/README.md`
- `matter/idl/README.md`