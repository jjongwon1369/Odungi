---
entity: all
ids: []
source_paths: ['docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md', 'docs/guides/matter_idl_tooling.md', 'docs/guides/writing_clusters.md']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
---

# Matter 클러스터 및 디바이스 타입 개발

## 개요

새 클러스터 및 디바이스 타입 개발은 다음 작업을 포함한다.

1. 클러스터 정의와 구현 작성
2. ZAP이 적절한 Ember 계층을 생성하도록 코드와 지원 자료 구성
3. 코드의 정확성과 인증을 검증할 단위 테스트, 테스트 계획, 자동화 스크립트 작성

제공된 문서는 다음 범위를 다룬다.

| 문서 | 주요 내용 |
|---|---|
| `docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md` | XML 정의, ZAP 확인, Ember 및 override 기반 구현, 속성·명령·이벤트 처리 |
| `docs/guides/matter_idl_tooling.md` | `.matter` 형식, CSA XML 파싱, SDK와 스펙 비교, 디바이스 적합성 검사 |
| `docs/guides/writing_clusters.md` | code-driven 클러스터 설계, `ServerClusterInterface`, 빌드·애플리케이션 통합, 테스트 |

개발 흐름은 클러스터 정의 → C++ 구현 → 빌드 통합 → 애플리케이션 통합 → 테스트로 구성된다. ZAP 기반 정의와 생성 결과는 `.matter` 도구로 스펙과 비교할 수 있으나, 스펙 XML을 생성하는 scraper의 한계 때문에 비교 결과는 사람이 검증해야 한다.

## 관련 문서

### Implementing New Clusters & Device Types

출처: `docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md`

이 문서는 SDK에서 클러스터와 디바이스 타입을 구현하는 작업에 집중한다. 단위 테스트, 테스트 계획, 인증 테스트는 별도의 테스트 영역에서 다룬다.

#### 클러스터 및 디바이스 타입 정의

- **클러스터 정의**
  - XML로 구조체, 열거형, 속성, 명령, 이벤트 등을 기술한다.
  - 스펙을 코드로 직접 표현한다.
  - 위치: [src/app/zap-templates/zcl/data-model/chip/](https://github.com/project-chip/connectedhomeip/tree/master/src/app/zap-templates/zcl/data-model/chip)
- **클러스터 구현**
  - 클라이언트 측은 코드 생성 결과에 연결 코드를 작성한다.
  - 서버 측은 Ember 또는 `AttributeAccessInterface`, `CommandHandlerInterface`를 통해 C++로 구현한다.
  - 구현 위치: `src/app/clusters/<your_cluster_name>`
  - 빌드 파일: [src/app/chip_data_model.gni](https://github.com/project-chip/connectedhomeip/blob/master/src/app/chip_data_model.gni)
  - 빌드 파일은 코드 생성 데이터를 사용하여 클러스터 목록을 자동 구성한다. 기존 사례를 따라 ZAP에서 선택한 클러스터가 이미지에 포함되도록 한다.
- **디바이스 타입 정의**
  - XML에서 적합성 조건을 정의한다.
  - 위치: [src/app/zap-templates/zcl/data-model/chip/matter-devices.xml](https://github.com/project-chip/connectedhomeip/blob/master/src/app/zap-templates/zcl/data-model/chip/matter-devices.xml)

정의를 추가할 위치와 방법은 [How To Add New Device Types & Clusters](how_to_add_new_dts_and_clusters.md)를 참고한다.

#### ZAP에서 정의 확인

ZAP이 새 클러스터를 이해하고 디바이스에서 사용할 수 있도록 XML과 연결 코드를 구성한다.

![ZAP 컴파일 흐름](../zap_and_codegen/img/zap_compiler.png)

[ZAP 소개](../zap_and_codegen/zap_intro.md)를 참고한 뒤, 임의의 ZAP 파일로 도구를 실행한다.

```sh
./scripts/tools/zap/run_zaptool.sh <filename>
```

확인 항목:

1. endpoint 설정의 디바이스 타입 목록에 새 디바이스 타입이 표시되는지 확인한다.
2. 클러스터에 예상한 속성, 명령, 이벤트가 모두 있는지 확인한다.
   - XML의 `domain` 매개변수가 클러스터의 그룹을 결정한다.
3. 각 속성의 저장 옵션이 적절하게 설정되었는지 확인한다.

관련 화면:

- [디바이스 타입 목록](../zap_and_codegen/img/zap3.png)
- [클러스터 구성](../zap_and_codegen/img/zap4.png)
- [속성 저장 옵션](../zap_and_codegen/img/zap5.png)

#### Ember와 override

| 구분 | Ember | override |
|---|---|---|
| 구성 시점 | 컴파일 시 생성 | 실행 시 설치 |
| 주요 역할 | endpoint, 속성, 명령 등의 설정과 접근 | 속성 접근 또는 명령 처리를 Ember보다 먼저 처리 |
| 구현 방식 | 생성된 함수 시그니처와 기본 구현, 서버 콜백 | `AttributeAccessInterface`, `CommandHandlerInterface` |
| 특성 | 복잡한 속성 상호작용과 단위 테스트가 어려움 | 제어 범위가 넓고 단위 테스트가 가능하지만 더 복잡함 |
| 후속 처리 | Ember에서 처리 | ZAP 설정에 따라 Ember로 처리를 넘길 수 있음 |

Interaction Model 계층은 클러스터에 대한 interaction을 수신하면 Ember 함수를 호출한다. 서버 코드는 초기화, 명령, 속성 접근, 이벤트 생성을 위한 콜백을 구현한다.

#### 서버 초기화

![클러스터 초기화 흐름](img/cluster_initialization.png)

- `EmberAfInitializeAttributes`
  - ZAP에서 `RAM`으로 표시한 모든 속성의 Ember 저장소에 기본값을 설정한다.
- `Matter<Cluster>PluginServerCallback`
  - `.h`는 생성 파일이고 `.cpp` 구현은 서버 클러스터 코드에 작성한다.
  - 클러스터와 override를 설정하는 데 사용한다.
- `chip::app::AttributeAccessInterfaceRegistry::Instance().Register`
  - 속성 읽기와 쓰기를 외부에서 처리할 때 사용한다.

원문 다이어그램의 파란색 영역은 override할 수 있다.

#### 속성 저장과 접근

| ZAP 저장 옵션 | 저장소 | 접근 방식 |
|---|---|---|
| `RAM` | 자동 할당 | Ember가 읽기와 쓰기를 처리하며, 생성 파일 `Accessors.h`에 속성별 `Get`, `Set` 함수가 제공됨 |
| `External` | 할당하지 않음 | 접근 override 등록이 필요하며 Ember 저장소로 처리를 넘길 수 없음 |

`RAM` 속성에도 override를 등록할 수 있다. override에서 속성을 인코딩하지 않으면 저장소 처리로 넘어간다. 반대로 항상 override에서 인코딩하면 할당된 Ember 저장 공간을 낭비한다.

**읽기**

- [AttributeAccessInterface::Read()](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h#L424)를 구현한다.
- `ConcreteReadAttributePath`의 `aPath.mAttributeId`로 요청 속성을 판별한다.
- `SomeAttribute::Id`와 같은 속성 식별자에 따라 `AttributeValueEncoder`의 `aEncoder.Encode(mSomeValue)`로 값을 인코딩한다.
- 목록은 chunking 처리가 올바르게 이루어지도록 `EncodeList`를 사용해야 한다.

![속성 읽기 흐름](img/cluster_attribute_read.png)

**쓰기**

- 읽기와 같은 경로를 거쳐 `AttributeAccessInterface`의 `Write` 함수에 도달한다.
- [AttributeAccessInterface::Write()](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h#444)를 구현한다.
- 속성 핸들러가 제약 조건 검증과 영속성을 책임진다.

**영속성**

- `AttributeAccessInterface`를 사용하면 영속성이 필요한 속성을 직접 관리해야 한다.
- `AttributePersistenceProvider` 위에서 `AttributePersistence`를 사용할 수 있다.
- [src/app/AttributePersistence.h](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributePersistence.h)는 기본 `PersistenceProvider`에 여러 타입의 값을 읽고 쓰는 API를 제공한다.
- 단위 테스트에서는 `TestPersistentStorageDelegate`와 `DefaultAttributePersistenceProvider`를 조합할 수 있다.

**Ember 속성 변경 콜백**

Ember는 인코딩과 디코딩을 처리하고, 속성 변경에 대한 콜백을 제공한다.

```cpp
void MatterPostAttributeChangeCallback(const chip::app::ConcreteAttributePath & attributePath,
                                       uint8_t type, uint16_t size, uint8_t * value)
```

콜백은 여러 예제에서 사용할 수 있도록 구현해야 한다.

#### 명령 처리

![명령 처리 흐름](img/cluster_commands.png)

- **override**
  - 실행 시 `InteractionModelEngine::RegisterCommandHandler`로 등록한다.
  - `CommandHandlerInterface`를 구현한다.
  - `HandleCommand`를 사용하면 처리 여부가 설정된다.
  - 직접 처리하면 명령 처리 여부를 명시해야 하며, 처리하지 않은 경우 기본적으로 Ember로 넘어간다.
- **Ember**
  - 정적으로 구성한다.
  - `emberAf<ClusterName><CommandName>Callback`을 구현한다.
  - 처리했으면 `true`를 반환한다. `false`를 반환하면 유효하지 않은 명령 응답이 반환된다.
- **공통 책임**
  - 명령 핸들러의 `AddResponse` 또는 `AddStatus`로 호출자에게 응답한다.
  - 제약 조건을 검증하고 스펙에 맞는 상태 또는 응답을 반환한다.

명령을 전부 `CommandHandlerInterface`로 처리하는 클러스터는 [src/app/common/templates/config-data.yaml](https://github.com/project-chip/connectedhomeip/blob/master/src/app/common/templates/config-data.yaml)에 추가하여 Ember 명령 콜백 생성을 비활성화한다.

#### 속성 구독과 이벤트

- **속성 변경 보고**
  - 생성된 `Get`/`Set` 함수를 통해 Ember 저장소를 사용하면 자동으로 처리된다.
  - `AttributeAccessInterface`를 사용하면 `MatterReportingAttributeChangeCallback`으로 reporting engine에 변경을 알려야 한다.
- **이벤트**
  - 직접적인 Ember 지원은 없다.
  - `EventLogging.h`의 `LogEvent`를 호출한다.
  - `LogEvent`를 사용할 때 호출자는 Matter stack lock을 획득하거나 이벤트를 Matter event queue에 넣어야 한다.

#### Dynamic Endpoints

- ZAP 구성은 컴파일 시 정적으로 결정된다.
- 실행 시 `emberAfSetDynamicEndpoint`로 동적 endpoint를 등록할 수도 있다.
- 이 방식은 bridge에서 흔히 사용된다.
- 별도의 속성 저장소 등을 사용하는 경우 정적 endpoint뿐 아니라 동적 endpoint도 고려해야 한다.

### The `.matter` IDL file format

출처: `docs/guides/matter_idl_tooling.md`

#### 형식과 데이터 원천

`.matter` IDL은 데이터 구조, 클러스터 정의, endpoint 구성을 사람이 읽기 쉽게 표현한다. 기계와 사람이 모두 읽기 쉬운 형식을 바탕으로 ZAP 기반 클러스터 정의의 검증을 지원한다.

형식 상세: [matter/idl/README.md](../../scripts/py_matter_idl/matter/idl/README.md)

SDK는 `data_model/clusters`에 CSA XML 데이터 정의의 사본을 포함한다.

- 공식 Matter 스펙에 scraper를 실행하여 갱신한다.
- 갱신 안내: [data_model/README.md](../../data_model/README.md)
- scraper는 개발 중이므로 XML이 불완전하거나 오류를 포함할 수 있다.

#### CSA XML을 `.matter`로 변환

`matter-data-model-xml-parser`는 하나 이상의 CSA 데이터 모델 XML 파일을 파싱하여 `.matter` 형식으로 출력한다.

```sh
matter-data-model-xml-parser data_model/clusters/BooleanState.xml
```

| 인수 | 설명 |
|---|---|
| `-o/--output PATH` | STDOUT 대신 지정한 경로에 출력 |
| `--compare PATH` | 비교할 다른 `.matter` 파일을 읽음. `--compare-output`과 함께 사용해야 함 |
| `--compare-output PATH` | `--compare`의 클러스터 중 입력 XML에 대응하는 부분을 지정한 경로에 출력 |

`--compare`와 `--compare-output`을 함께 사용하면 주석을 제거하고 요소를 알파벳순으로 정렬하여 사람이 읽기 쉬운 비교 결과를 만든다.

#### SDK와 스펙 비교

비교에서는 다음 파일을 사용한다.

- `data_model/clusters/*.xml`: 공식 스펙 정의로 간주
- `src/controller/data_model/controller-clusters.matter`: SDK에 정의된 모든 클러스터 포함

```sh
matter-data-model-xml-parser \
     -o out/spec.matter                                             \
     --compare-output out/sdk.matter                                \
     --compare src/controller/data_model/controller-clusters.matter \
     data_model/clusters/DoorLock.xml                               \
  && diff out/{spec,sdk}.matter
```

scraper가 개발 중이므로 diff는 사람이 검증해야 한다. 도구 오류나 스펙의 Zigbee 전용 표시 등이 차이에 영향을 줄 수 있다.

#### 디바이스 적합성 검사

`matter-idl-lint`는 `.matterlint`에 표현된 규칙을 사용하여 기본적인 적합성을 검사한다.

규칙의 주요 원천:

- silabs XML 파일에서 미리 불러온 규칙: 필수 속성 존재 여부 검사
- 하드코딩된 규칙: 특정 endpoint의 필수 클러스터와 속성 등 검사

```sh
matter-idl-lint examples/window-app/common/window-app.matter
```

### Writing and Updating Clusters

출처: `docs/guides/writing_clusters.md`

이 문서는 새로운 code-driven 클러스터 구현을 위한 절차와 설계 지침을 설명한다.

#### XML 정의와 코드 생성

클러스터 XML은 `src/app/zap-templates/zcl/data-model/chip`에 위치하며, C++ 코드 생성의 입력으로 사용된다.

- [Alchemy](https://github.com/project-chip/alchemy)로 스펙의 `asciidoc`을 파싱하여 XML을 생성하거나 갱신한다.
- 오류가 발생하기 쉬우므로 XML 수동 편집은 권장하지 않는다.
- XML 준비 후 코드 생성을 실행한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

상세 절차: [code generation guide](../zap_and_codegen/code_generation.md)

#### 파일 구조와 구현 패턴

구현과 단위 테스트를 위한 디렉터리:

```text
src/app/clusters/<cluster-directory>/
```

[src/app/zap_cluster_list.json](https://github.com/project-chip/connectedhomeip/blob/master/src/app/zap_cluster_list.json)의 `ServerDirectories`는 클러스터의 `UPPER_SNAKE_CASE` define을 `src/app/clusters` 아래 디렉터리에 매핑한다.

권장 명명 방식:

- 디렉터리: `cluster-name-server`
- `ServerClusterInterface` 구현: `ClusterNameSnakeCluster.h/cpp`

**권장: 단일 클래스에 통합**

- 클러스터 로직, 데이터 저장, `ServerClusterInterface` 구현을 하나의 클래스에 포함한다.
- 흔히 `DefaultServerCluster`에서 파생한다.
- 상용구 코드와 가상 함수 변환 계층을 줄여 flash 사용량을 줄인다.
- 참고: [Basic Information](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/basic-information)

**새 구현에서 비권장: 로직과 변환 계층 분리**

- `ClusterLogic`에 핵심 로직을 두고 `ClusterImplementation`을 변환 계층으로 사용한다.
- 테스트를 위해 로직을 분리할 수 있지만 flash와 RAM 오버헤드가 발생한다.
- 기존 방식 참고: [Administrator Commissioning](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/administrator-commissioning-server)

선택적인 애플리케이션 콜백 인터페이스로 `ClusterDriver` 또는 `Delegate`를 사용할 수 있다. 원문은 중의적인 `Delegate`보다 `Driver`라는 용어를 권장한다.

#### builder-style Config

새 code-driven 클러스터는 feature 활성화와 필수 속성·매개변수 설정이 일치하도록 builder-style `Config` 패턴을 사용해야 한다.

주요 참조: [Level Control Cluster](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/level-control/LevelControlCluster.h)

설계 원칙:

- 클러스터 클래스 내부에 시작 상태를 담는 `Config`를 정의한다.
- 복잡한 구성은 비공개 멤버를 가진 `class`로 정의하여 builder 메서드 사용을 강제한다.
- 단순한 구성에는 공개 멤버를 가진 `struct`도 허용한다.
- `With<Feature>(...)` 메서드는 `Config` 참조를 반환하여 연쇄 호출을 지원한다.
- feature 설정 메서드는 `FeatureMap` 비트와 관련 속성을 함께 설정한다.
- 적합성 로직을 구성 API에 캡슐화한다.
- `EndpointId`는 `Config`에 저장하지 않고 클러스터 생성자에 직접 전달한다.
- 클러스터 내부에는 `Config` 자체 대신 구성값을 개별 멤버로 추출한다. 불변값은 `const`로 둘 수 있다.

원문의 `LevelControlCluster` 예시:

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

#### 애플리케이션 부담 최소화

클러스터는 가능한 많은 공통 작업을 내부에서 처리해야 한다.

- 영속성, 타이머, 복잡한 상태 머신을 클러스터 내부에 구현한다.
- 애플리케이션에는 대응이 필요한 중요한 이벤트나 변경만 알린다.
- 애플리케이션이 복잡한 로직을 구현해야 한다면 helper 클래스나 기본 구현을 제공한다.
- 원시 저장 키나 개별 타이머 관리 같은 저수준 세부사항을 애플리케이션에 떠넘기지 않는다.

#### 검증과 Delegate/Driver

애플리케이션이 쓰기나 명령에 관여해야 한다면 변경 전 검증 인터페이스를 사용한다.

1. 클러스터가 스펙에 정의된 범위, 제약 조건, 상태 제한을 먼저 검증한다.
2. 값이 바뀌지 않는 no-op 작업은 조기에 처리한다.
3. 내부 상태 반영이나 영속화 전에 애플리케이션이 변경을 승인하거나 거부하도록 한다.
4. 승인된 경우 상태를 반영하고 변경을 알린다.

원문에는 두 가지 콜백 반환 방식이 기술되어 있다.

| 문맥 | 반환 방식 | 거부 처리 |
|---|---|---|
| 일반적인 Delegate/Driver 검증 지침 | `Protocols::InteractionModel::Status` | `Success` 이외의 상태를 반환하면 작업을 실패시키고 해당 상태를 요청자에게 전달 |
| 속성별 `On<AttributeName>Changed` 지침 | `bool` | `false`이면 `Status` API는 `Protocols::InteractionModel::Status::Failure`, `CHIP_ERROR` API는 `CHIP_ERROR_INCORRECT_STATE`로 실패 |

속성별 콜백은 현재값이 아니라 **제안된 새 값**을 받아야 한다. 기본 구현은 `true`를 반환하여 필요한 콜백만 재정의할 수 있게 한다.

[Boolean State Configuration delegate](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/boolean-state-configuration-server/boolean-state-configuration-delegate.h)의 예:

```cpp
virtual bool OnCurrentSensitivityLevelChanged(uint8_t newValue) { return true; }
virtual bool OnAlarmsActiveChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnAlarmsSuppressedChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnAlarmsEnabledChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnSensorFaultChanged(chip::BitMask<SensorFaultBitmap> newValue) { return true; }
```

검증 → no-op 확인 → delegate 호출 → 반영 및 알림 순서:

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

#### 속성과 feature 처리

- 활성화된 feature와 선택 항목에 따라 제공되는 속성과 명령을 정확하게 보고한다.
- feature 종속 요소는 feature map으로 제어한다.
- 순수 선택 요소는 boolean 플래그 또는 `BitFlags`로 제어한다.
- feature 및 선택 속성·명령의 여러 조합을 단위 테스트로 검증한다.

**공개 접근 API**

- 모든 속성에 getter를 제공한다.
  - 예: `GetCurrentSensitivityLevel()`, `GetAlarmsActive()`
  - 가능하면 값을 복사하여 반환한다.
  - 내부 데이터의 포인터나 참조 반환은 수명 위험 때문에 피한다.
  - 불가피하면 즉시 사용하는 동안만 유효하며 저장하면 안 된다는 점을 문서화한다.
- 변경 가능한 모든 속성을 스펙에 맞게 수정하는 API를 제공한다.
  - 단순 속성 예: `SetCurrentSensitivityLevel()`
  - 여러 속성의 원자적 갱신이 필요하면 개별 setter 대신 상위 수준 API를 제공한다.
  - setter는 속성 변경 알림도 책임진다.

참고: [Boolean State Configuration](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/boolean-state-configuration-server/BooleanStateConfigurationCluster.h)

#### 속성 변경 알림

- `Startup`에서 `ServerClusterContext`를 받는다.
- context를 통해 `interactionContext->dataModelChangeListener->MarkDirty(path)`를 호출한다.
- 클러스터가 관리하는 경로에는 `NotifyAttributeChanged` helper를 사용할 수 있다.
- 쓰기 구현은 `WriteImpl`과 `NotifyAttributeChangedIfSuccess`를 조합할 수 있다.

```cpp
DataModel::ActionReturnStatus SomeCluster::WriteAttribute(const DataModel::WriteAttributeRequest & request,
                                                                  AttributeValueDecoder & decoder)
{
        // Delegate everything to WriteImpl. If write succeeds, notify that the attribute changed.
        return NotifyAttributeChangedIfSuccess(request.path.mAttributeId, WriteImpl(request, decoder));
}
```

알림이 필요 없는 경우 `WriteImpl`은 `ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 반환해야 한다.

```cpp
VerifyOrReturnValue(mValue != newValue, ActionReturnStatus::FixedStatus::kWriteSuccessNoOp);
```

no-op 쓰기는 다음을 발생시키면 안 된다.

- 네트워크 속성 변경 알림
- 애플리케이션 delegate/driver 콜백

관련 정의: [ActionReturnStatus.h](https://github.com/project-chip/connectedhomeip/blob/master/src/app/data-model-provider/ActionReturnStatus.h)

#### 영속성과 자원 사용

- **스칼라 속성**
  - `src/app/persistence/AttributePersistence.h`의 `AttributePersistence`를 사용한다.
  - `ServerClusterContext`가 `AttributePersistenceProvider`를 제공한다.
- **속성 이외의 데이터**
  - context가 제공하는 `PersistentStorageDelegate`를 사용한다.
- **flash/RAM 최적화**
  - 공통적이거나 큰 클러스터에서는 `C++` template으로 feature와 속성을 컴파일 시 선택하는 방식을 고려한다.

#### 고급 ServerClusterInterface 기능

주로 구현하는 메서드는 `ReadAttribute`, `WriteAttribute`, `InvokeCommand`이다.

| 메서드 | 용도 |
|---|---|
| `ListAttributeWriteNotification` | 큰 목록 속성을 chunk 단위로 영속화하는 등의 고급 처리. Binding cluster가 가능한 사례이며 대부분은 기본 구현으로 충분 |
| `EventInfo` | 기본값이 아닌 읽기 권한이 필요한 이벤트의 권한 정의. 예를 들어 `Administrator` 권한이 필요한 경우 구현해야 함 |
| `AcceptedCommands` | 서버가 처리할 수 있는 요청 명령: `client => server` |
| `GeneratedCommands` | 서버가 요청 처리 후 생성할 수 있는 응답 명령: `server => client` |

명령 목록은 Matter 스펙의 클러스터 정의에 따라 구성한다. 이벤트 접근 권한은 새 구현과 코드 리뷰에서 확인해야 한다.

#### 빌드 파일 구성

`src/app/clusters/<cluster-directory>/`에는 다음 빌드 구성이 필요하다.

**`BUILD.gn`**

- 일반적으로 `<cluster-directory>`라는 이름의 `source_set` target을 정의한다.
- `src/app/chip_data_model.gni`가 다음 의존성으로 참조하므로 기본 target 이름이 중요하다.

```gn
deps += [ "${_app_root}/clusters/${cluster}" ]
```

**`app_config_dependent_sources`**

`chip_data_model.gni`와 `chip_data_model.cmake`는 통합 지원 파일을 포함하여, 참조된 모든 소스를 `endpoint_config.h` 같은 애플리케이션별 Ember 생성 설정과 함께 하나의 source set으로 묶는다.

| 파일 | 포함 내용 |
|---|---|
| `app_config_dependent_sources.gni` | 일반적으로 `CodegenIntegration.cpp`와 필요한 helper·호환 계층. 해당하는 경우 `CodegenIntegration.h` 포함 |
| `app_config_dependent_sources.cmake` | `.gni`의 소스에 더해 `BUILD.gn` 의존성으로는 포함되지만 CMake의 `libCHIP` 빌드에는 없는 파일 포함 |

[src/app/clusters/basic-information](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/basic-information)의 예:

```gn
# BUILD.gn
import("//build_overrides/build.gni")
import("//build_overrides/chip.gni")

source_set("basic-information") {
   sources = [ ... ]
   public_deps = [ ... ]
}
```

```gn
# app_config_dependent_sources.gni
app_config_dependent_sources = [ "CodegenIntegration.cpp" ]
```

```cmake
# app_config_dependent_sources.cmake
# This block adds the codegen integration sources, similar to app_config_dependent_sources.gni
TARGET_SOURCES(
  ${APP_TARGET}
  PRIVATE
    "${CLUSTER_DIR}/CodegenIntegration.cpp"
)

# These are the things that BUILD.gn dependencies would pull
TARGET_SOURCES(
  ${APP_TARGET}
  PRIVATE
    "${CLUSTER_DIR}/BasicInformationCluster.cpp"
    "${CLUSTER_DIR}/BasicInformationCluster.h"
)
```

#### 애플리케이션 통합

1. `src/app/zap_cluster_list.json`에 새 클러스터와 구현 디렉터리의 매핑을 추가한다.
2. `CodegenIntegration.cpp`에 정적 생성 코드와 C++ 구현을 연결하는 로직을 작성한다.
3. `app_config_dependent_sources.gni`, `app_config_dependent_sources.cmake`에 통합 소스와 의존성을 추가한다.
4. 생성된 `<app/static-cluster-config/<cluster-name>.h`의 애플리케이션별 설정을 사용하여 endpoint별 클러스터를 초기화한다.
5. `CodegenIntegration.cpp`에 다음 콜백을 구현한다.
   - `Matter<Cluster>ClusterInitCallback(EndpointId)`
   - `Matter<Cluster>ClusterShutdownCallback(EndpointId)`
6. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters` 배열에 클러스터를 추가하여 콜백을 활성화한다.
7. Ember가 속성 메모리를 할당하지 않도록 `src/app/zap-templates/zcl/zcl.json`과 `zcl-with-test-extensions.json`의 `attributeAccessInterfaceAttributes`에 클러스터의 모든 non-list 속성을 추가한다.
8. ZAP을 다시 생성한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

#### 단위 테스트와 통합 테스트

단위 테스트 위치:

```text
src/app/clusters/<cluster-name>/tests/
```

`chip::Testing::ClusterTester`를 사용하면 encoder, handler, 원시 TLV buffer를 직접 mock할 필요를 줄일 수 있다.

상세 안내: [ClusterTester Helper Class Guide](../cluster_and_device_type_dev/cluster_tester.md)

| 검증 대상 | 방법 |
|---|---|
| 테스트 초기화 | mock delegate로 클러스터 인스턴스에 가짜 데이터 주입 |
| 메타데이터 | `Attributes()`와 `AcceptedCommands()`의 정확성 확인. 잘못되면 `ClusterTester`가 읽기와 명령 호출을 거부 |
| 속성 읽기 | `tester.ReadAttribute()`로 `ReadAttribute`를 검증하고 mock 데이터와 비교 |
| 명령 | `tester.Invoke()`로 실행하고 delegate 응답에 따른 `Protocols::InteractionModel::Status` 확인 |
| 변경 보고 | `tester.GetDirtyList()`로 상태 변경이 속성을 dirty로 표시하는지, no-op 쓰기는 표시하지 않는지 확인 |

실제 애플리케이션 검증:

- `all-clusters-app` 같은 예제 애플리케이션에 클러스터를 통합한다.
- `chip-tool` 또는 `matter-repl`로 수동 검증한다.
- 예제 애플리케이션을 대상으로 end-to-end 동작을 확인하는 통합 테스트를 작성한다.