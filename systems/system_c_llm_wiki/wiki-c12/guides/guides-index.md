---
entity: all
ids: []
source_paths: ['docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md', 'docs/guides/matter_idl_tooling.md', 'docs/guides/writing_clusters.md']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Matter 클러스터 및 디바이스 타입 개발

## 개요

새 클러스터와 디바이스 타입 개발은 다음 작업을 포함한다.

1. Matter 스펙에 따른 클러스터 및 디바이스 타입 정의
2. 클러스터 로직과 데이터 관리 구현
3. ZAP이 적절한 Ember 계층을 생성하도록 코드 및 지원 파일 구성
4. 빌드 시스템과 애플리케이션 통합
5. 단위 테스트, 테스트 계획 및 자동화 스크립트 작성

제공된 문서는 다음 내용을 다룬다.

- **Ember 및 override 기반 개발**: XML 정의, 속성 저장소, 명령 처리, 이벤트 및 동적 엔드포인트
- **code-driven 클러스터 개발**: `ServerClusterInterface` 기반 구현, `Config` 구성, 변경 알림, 영속성, 빌드 및 애플리케이션 통합
- **정의 검증 도구**: `.matter` 변환, 스펙과 SDK 비교, 디바이스 적합성 검사

## 관련 문서

### 원문 문서

| 문서 | 경로 | 주요 내용 |
|---|---|---|
| Implementing New Clusters & Device Types | `docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md` | XML 정의, ZAP, Ember, override 및 디바이스 타입 개발 |
| The `.matter` IDL file format | `docs/guides/matter_idl_tooling.md` | CSA XML 파싱, `.matter` 비교 및 lint |
| Writing and Updating Clusters | `docs/guides/writing_clusters.md` | code-driven 클러스터 구현과 통합 지침 |

### 클러스터 및 디바이스 타입 정의

클러스터 XML은 구조체, 열거형, 속성, 명령, 이벤트 등을 정의하며, 스펙을 코드 정의로 옮기는 역할을 한다.

- 클러스터 정의 위치: `src/app/zap-templates/zcl/data-model/chip/`
- 디바이스 타입 적합성 정의: `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml`
- 클라이언트 측: 코드 생성 결과와 애플리케이션 연결 코드 사용
- 서버 측: C++ 구현 사용

`docs/guides/writing_clusters.md`는 스펙의 `asciidoc`을 [Alchemy](https://github.com/project-chip/alchemy)로 파싱하여 XML을 생성하거나 갱신하도록 안내한다. XML 수동 편집은 오류 가능성 때문에 권장하지 않는다.

XML 준비 후 코드 생성 명령:

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

정의 추가 절차는 [How To Add New Device Types & Clusters](how_to_add_new_dts_and_clusters.md), 코드 생성은 [code generation guide](../zap_and_codegen/code_generation.md)를 참고한다. 생성 결과는 `.matter` 도구를 사용하여 스펙과 대조해야 한다.

### ZAP에서 정의 확인

ZAP이 새 클러스터를 이해하려면 XML과 연결 코드가 필요하다.

```sh
./scripts/tools/zap/run_zaptool.sh <filename>
```

확인 사항:

1. 엔드포인트 설정의 디바이스 타입 목록에 새 디바이스 타입이 나타나는지 확인한다.
2. XML의 `domain`이 지정한 그룹에 클러스터가 나타나는지 확인한다.
3. 예상한 속성, 명령, 이벤트가 모두 있는지 확인한다.
4. 각 속성의 저장소 옵션이 올바른지 확인한다.

ZAP 소개는 [ZAP](../zap_and_codegen/zap_intro.md)을 참고한다.

### Ember 및 override 기반 구현

#### 역할과 호출 관계

Ember는 디바이스의 엔드포인트, 속성, 명령 등을 설정하고 접근하는 계층이다.

- 빌드 시 Ember 함수 시그니처와 기본 구현이 생성된다.
- 클러스터 서버는 초기화, 명령, 속성 접근, 이벤트 생성을 위한 콜백을 구현한다.
- Interaction Model 계층은 수신한 클러스터 상호작용을 Ember 함수로 전달한다.

override는 컴파일 시 생성되는 Ember 계층과 달리 런타임에 설치된다.

- 속성 접근: `AttributeAccessInterface`
- 명령 처리: `CommandHandlerInterface`
- override는 Ember보다 먼저 호출된다.
- 더 많은 제어가 가능하고 단위 테스트가 가능하지만 구현은 더 복잡하다.
- ZAP 설정에 따라 Ember 계층으로 처리를 넘길 수 있다.

서버 구현 위치는 `src/app/clusters/<your_cluster_name>`이며, `src/app/chip_data_model.gni`는 코드 생성 데이터를 사용하여 클러스터 목록을 구성한다.

#### 서버 초기화

| 식별자 | 역할 |
|---|---|
| `EmberAfInitializeAttributes` | ZAP에서 `RAM`으로 지정한 속성 저장소에 기본값 설정 |
| `Matter<Cluster>PluginServerCallback` | 생성된 `.h` 선언에 대응하는 서버 측 `.cpp` 구현에서 클러스터와 override 초기화 |
| `chip::app::AttributeAccessInterfaceRegistry::Instance().Register` | 외부에서 속성 읽기와 쓰기를 처리하기 위한 override 등록 |

초기화 흐름은 원문의 `img/cluster_initialization.png`에 제시되어 있다.

#### 속성 저장소

| ZAP 저장소 옵션 | 동작 | override 사용 시 주의점 |
|---|---|---|
| `RAM` | 저장소가 자동 할당되며 Ember가 읽기와 쓰기 처리 | override에서 값을 인코딩하지 않으면 저장소로 처리가 넘어갈 수 있음 |
| `External` | 저장소가 할당되지 않으며 Ember 저장소로 처리가 넘어가지 않음 | 속성 접근 override 등록 필요 |

`RAM` 속성에는 생성 파일 `Accessors.h`에 `Get` 및 `Set` 함수가 제공된다. 해당 속성을 override에서 항상 인코딩하면 할당된 Ember 저장소가 낭비된다.

#### 속성 읽기, 쓰기 및 영속성

- `AttributeAccessInterface::Read()`:
  - `aPath.mAttributeId`를 확인하여 요청 속성을 식별한다.
  - `aEncoder.Encode(mSomeValue)`로 값을 인코딩한다.
  - 목록은 청크 처리를 위해 `EncodeList`를 사용해야 한다.
- `AttributeAccessInterface::Write()`:
  - 읽기와 같은 경로로 전달되지만 `Write`에서 처리된다.
  - 핸들러가 제약 조건 검사와 속성 영속성을 담당한다.

`AttributeAccessInterface`를 사용하면 영속성이 필요한 속성을 직접 관리해야 한다.

- `AttributePersistence`와 `AttributePersistenceProvider` 사용
- 문서에 제시된 API 경로: `src/app/AttributePersistence.h`
- 단위 테스트: `TestPersistentStorageDelegate`와 `DefaultAttributePersistenceProvider` 조합 사용 가능

Ember 계층은 인코딩과 디코딩을 처리하지만 복잡한 속성 상호작용과 단위 테스트에는 어려움이 있다. 속성 변경 콜백은 다음과 같다.

```cpp
void MatterPostAttributeChangeCallback(const chip::app::ConcreteAttributePath & attributePath,
                                       uint8_t type, uint16_t size, uint8_t * value)
```

콜백은 여러 예제에서 사용할 수 있도록 구현해야 한다.

#### 명령 처리

| 방식 | 등록 및 구현 |
|---|---|
| override | 런타임에 `InteractionModelEngine::RegisterCommandHandler`로 등록하고 `CommandHandlerInterface` 구현 |
| Ember | 정적 콜백 `emberAf<ClusterName><CommandName>Callback` 구현 |

`CommandHandlerInterface` 사용 시:

- `HandleCommand`는 명령 처리 여부 설정을 지원한다.
- 직접 처리하는 경우 명령 처리 여부를 명시해야 한다.
- 처리되지 않은 명령은 기본적으로 Ember로 넘어간다.
- 명령을 전부 이 인터페이스에서 처리하면 `src/app/common/templates/config-data.yaml`에 등록하여 Ember 명령 콜백 생성을 비활성화한다.

Ember 콜백은 처리했으면 `true`, 유효하지 않은 명령 응답을 반환해야 하면 `false`를 반환한다.

두 방식 모두 다음 책임이 있다.

- `AddResponse` 또는 `AddStatus`로 호출자에게 응답
- 제약 조건 검사
- 스펙에 맞는 상태 또는 응답 반환

#### 변경 보고, 이벤트 및 동적 엔드포인트

- 생성된 `Get`/`Set` 함수로 Ember 저장소를 사용하면 속성 변경 보고가 처리된다.
- `AttributeAccessInterface` 사용 시 `MatterReportingAttributeChangeCallback`으로 보고 엔진에 변경을 알려야 한다.
- 이벤트에는 직접적인 Ember 지원이 없다.
  - `EventLogging.h`의 `LogEvent` 사용
  - 호출자는 Matter 스택 잠금을 획득하거나 이벤트를 Matter 이벤트 큐에 넣어야 한다.
- ZAP 설정은 컴파일 시 정적이지만, `emberAfSetDynamicEndpoint`로 런타임 동적 엔드포인트를 등록할 수 있다.
  - 브리지에서 흔히 사용한다.
  - 자체 속성 저장소는 정적 엔드포인트와 동적 엔드포인트를 모두 고려해야 한다.

### code-driven 클러스터 구현

#### 파일 구조와 권장 패턴

클러스터 구현과 단위 테스트는 `src/app/clusters/<cluster-directory>/`에 둔다.

권장 명명 규칙:

- 디렉터리: `cluster-name-server`
- `ServerClusterInterface` 구현: `ClusterNameSnakeCluster.h/cpp`

ZAP 기반 디렉터리 매핑은 `src/app/zap_cluster_list.json`의 `ServerDirectories`에서 관리한다. 클러스터의 `UPPER_SNAKE_CASE` 정의를 `src/app/clusters` 아래 디렉터리에 연결한다.

권장 구현은 로직, 데이터 저장소, `ServerClusterInterface` 구현을 하나의 클래스에 결합하는 방식이다. 보통 `DefaultServerCluster`에서 파생하며, 중간 변환 계층과 불필요한 코드를 줄여 flash 및 RAM 사용량을 낮춘다.

| 패턴 | 지침 | 참고 구현 |
|---|---|---|
| 결합 구현 | 신규 클러스터에 권장 | `src/app/clusters/basic-information` |
| `ClusterLogic`와 `ClusterImplementation` 분리 | 테스트 격리는 가능하지만 flash 및 RAM 오버헤드 때문에 신규 구현에는 비권장 | `src/app/clusters/administrator-commissioning-server` |
| `ClusterDriver` 또는 `Delegate` | 애플리케이션 콜백을 위한 선택적 인터페이스 | 용어 혼동을 줄이기 위해 `Driver` 권장 |

#### builder-style `Config`

새 code-driven 클러스터는 feature와 필수 매개변수가 일관되게 초기화되도록 builder-style `Config` 패턴을 사용해야 한다.

기준 구현: `src/app/clusters/level-control/LevelControlCluster.h`

핵심 원칙:

- 클러스터 내부에 중첩 `Config`를 정의한다.
- 복잡한 설정은 private 멤버를 가진 `class`로 구성한다.
- 단순한 설정은 public 멤버를 가진 `struct`도 허용한다.
- `With<Feature>(...)`는 `Config` 참조를 반환하여 연쇄 호출을 지원한다.
- 메서드는 `FeatureMap` 설정과 관련 필수 속성 초기화를 함께 수행한다.
- `EndpointId`는 `Config`가 아니라 클러스터 생성자에 직접 전달한다.
- 클러스터는 `Config` 자체를 저장하지 않고 값을 개별 멤버로 추출한다. 불변 설정은 `const`로 둘 수 있다.

원문의 `LevelControlCluster` 예시에서 `WithLighting`은 다음을 함께 수행한다.

```cpp
Config & WithLighting(DataModel::Nullable<uint8_t> startUpCurrentLevel)
{
    mFeatureMap.Set(LevelControl::Feature::kLighting);
    WithMinLevel(1);   // Spec mandates MinLevel=1 for Lighting feature
    WithMaxLevel(254); // Spec mandates MaxLevel=254 for Lighting feature
    mStartUpCurrentLevel = startUpCurrentLevel;
    return *this;
}
```

생성자는 다음 형태이다.

```cpp
LevelControlCluster(EndpointId endpoint, const Config & config);
```

#### 애플리케이션 부담 최소화

클러스터는 가능한 한 공통 로직을 내부에서 처리해야 한다.

- 영속성, 타이머, 복잡한 상태 머신을 클러스터에 구현한다.
- 애플리케이션에는 대응이 필요한 중요한 이벤트나 변경만 알린다.
- 애플리케이션에 복잡한 로직이 필요하면 helper 클래스나 기본 구현을 제공한다.
- 원시 저장소 키나 개별 타이머 관리 같은 저수준 세부사항을 애플리케이션에 넘기지 않는다.

#### 속성 및 feature 처리

- feature 의존 요소는 feature map으로 제어한다.
- 순수 선택 요소는 boolean 플래그 또는 `BitFlags`로 제어한다.
- 활성화한 feature와 선택 요소에 따라 사용 가능한 속성과 명령을 정확히 보고한다.
- 다양한 feature 및 선택 속성·명령 조합을 단위 테스트한다.

각 속성에는 애플리케이션용 공개 접근 API를 제공해야 한다.

- getter 예: `GetCurrentSensitivityLevel()`, `GetAlarmsActive()`
- setter 예: `SetCurrentSensitivityLevel()`

getter는 가능한 한 값을 복사하여 반환한다. 내부 데이터의 포인터나 참조 반환이 불가피하면 즉시 사용만 가능하며 저장해서는 안 된다는 수명 제약을 문서화한다.

변경 가능한 속성에는 스펙을 준수하는 setter를 제공한다. 여러 속성을 원자적으로 변경해야 한다면 개별 setter 대신 상위 수준 API를 제공한다. setter는 속성 변경 알림도 담당한다.

참고 구현: `src/app/clusters/boolean-state-configuration-server/BooleanStateConfigurationCluster.h`

#### 쓰기 검증과 delegate

처리 순서는 다음과 같다.

1. 클러스터가 스펙의 범위, 제약 조건, 상태 제한을 검증한다.
2. 값이 바뀌지 않는 no-op을 조기에 처리한다.
3. 애플리케이션 delegate의 사전 검증을 호출한다.
4. 허용된 값을 반영하고 변경을 알린다.

원문에는 두 가지 콜백 반환 형태가 제시되어 있다.

| 문맥 | 반환 및 거부 처리 |
|---|---|
| 일반적인 delegate 사전 검증 지침 | `Protocols::InteractionModel::Status` 반환. `Success`가 아니면 작업을 거부하고 해당 상태를 호출자에게 전달 |
| 속성별 `On<AttributeName>Changed` 예시 | `true`는 허용, `false`는 거부. 거부 시 `Protocols::InteractionModel::Status::Failure` 또는 `CHIP_ERROR_INCORRECT_STATE` 반환 |

속성별 콜백은 현재 값이 아니라 **제안된 새 값**을 받아야 한다. 기본 구현은 `true`를 반환하여 애플리케이션이 필요한 콜백만 재정의할 수 있게 한다.

`src/app/clusters/boolean-state-configuration-server/boolean-state-configuration-delegate.h`의 예:

```cpp
virtual bool OnCurrentSensitivityLevelChanged(uint8_t newValue) { return true; }
virtual bool OnAlarmsActiveChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnAlarmsSuppressedChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnAlarmsEnabledChanged(chip::BitMask<AlarmModeBitmap> newValue) { return true; }
virtual bool OnSensorFaultChanged(chip::BitMask<SensorFaultBitmap> newValue) { return true; }
```

#### 속성 변경 알림

`Startup`은 `ServerClusterContext`를 받는다. 이 컨텍스트를 통해 다음 호출로 변경을 표시할 수 있다.

```cpp
interactionContext->dataModelChangeListener->MarkDirty(path)
```

클러스터가 관리하는 속성에는 `NotifyAttributeChanged` helper를 사용할 수 있다.

쓰기 구현은 `WriteImpl`과 `NotifyAttributeChangedIfSuccess`를 조합할 수 있다.

```cpp
DataModel::ActionReturnStatus SomeCluster::WriteAttribute(const DataModel::WriteAttributeRequest & request,
                                                                  AttributeValueDecoder & decoder)
{
        // Delegate everything to WriteImpl. If write succeeds, notify that the attribute changed.
        return NotifyAttributeChangedIfSuccess(request.path.mAttributeId, WriteImpl(request, decoder));
}
```

알림을 보내지 않아야 하는 경우 `WriteImpl`은 `ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 반환해야 한다.

```cpp
VerifyOrReturnValue(mValue != newValue, ActionReturnStatus::FixedStatus::kWriteSuccessNoOp);
```

**no-op 쓰기는 네트워크 속성 변경 알림과 애플리케이션 delegate/driver 콜백을 모두 발생시키면 안 된다.**

#### 영속성과 자원 사용

code-driven 구현 문서의 영속성 지침:

- 스칼라 속성: `src/app/persistence/AttributePersistence.h`의 `AttributePersistence`
- 속성 저장 공급자: `ServerClusterContext`가 제공하는 `AttributePersistenceProvider`
- 속성 외 데이터: 컨텍스트가 제공하는 `PersistentStorageDelegate`

공통 또는 큰 클러스터에서는 C++ 템플릿으로 feature와 속성을 컴파일 시 선택하여 flash 및 RAM 사용량을 줄이는 방법을 고려할 수 있다.

#### 고급 `ServerClusterInterface` 메서드

일반적인 구현 메서드는 `ReadAttribute`, `WriteAttribute`, `InvokeCommand`이다.

| 메서드 | 용도 |
|---|---|
| `ListAttributeWriteNotification` | 큰 목록 속성의 청크 단위 저장 등 특수 처리. 대부분의 클러스터는 기본 구현으로 충분 |
| `EventInfo` | 이벤트 읽기에 기본값이 아닌 권한이 필요하면 구현. 예: `Administrator` |
| `AcceptedCommands` | 서버가 처리하는 `client => server` 명령 목록 |
| `GeneratedCommands` | 서버가 생성하는 `server => client` 응답 명령 목록 |

이벤트 접근 권한은 새 클러스터 구현과 코드 검토에서 확인해야 한다.

### 빌드 및 애플리케이션 통합

#### 빌드 파일

`src/app/clusters/<cluster-directory>/`에는 다음 빌드 구성이 필요하다.

| 파일 | 역할 |
|---|---|
| `BUILD.gn` | 일반적으로 `<cluster-directory>` 이름의 `source_set` 정의 |
| `app_config_dependent_sources.gni` | 보통 `CodegenIntegration.cpp` 및 필요한 helper/호환 계층 포함 |
| `app_config_dependent_sources.cmake` | `.gni`의 소스와 함께, `BUILD.gn` 의존성에서는 포함되지만 CMake에서는 포함되지 않는 소스 추가 |

`src/app/chip_data_model.gni`는 다음 형태로 의존성을 추가하므로 기본 타깃 이름이 중요하다.

```gn
deps += [ "${_app_root}/clusters/${cluster}" ]
```

`chip_data_model.gni`와 `chip_data_model.cmake`는 애플리케이션별 생성 설정인 `endpoint_config.h` 등과 관련 소스를 하나의 소스 집합으로 묶는다.

`src/app/clusters/basic-information`의 통합 파일 예:

```gn
app_config_dependent_sources = [ "CodegenIntegration.cpp" ]
```

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

#### 애플리케이션 연결 절차

1. `src/app/zap_cluster_list.json`에 클러스터 디렉터리 매핑을 추가한다.
2. `CodegenIntegration.cpp`를 작성한다.
3. `app_config_dependent_sources.gni`와 `app_config_dependent_sources.cmake`에 통합 소스와 의존성을 추가한다.
4. 생성 헤더 `<app/static-cluster-config/<cluster-name>.h`의 애플리케이션별 설정으로 엔드포인트별 클러스터를 초기화한다.
5. 다음 콜백을 구현한다.
   - `Matter<Cluster>ClusterInitCallback(EndpointId)`
   - `Matter<Cluster>ClusterShutdownCallback(EndpointId)`
6. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters` 배열에 클러스터를 추가한다.
7. `src/app/zap-templates/zcl/zcl.json`과 `zcl-with-test-extensions.json`의 `attributeAccessInterfaceAttributes`에 클러스터의 모든 비목록 속성을 추가한다. 이는 Ember의 속성 메모리 할당을 방지하기 위한 외부 처리 설정이다.
8. ZAP 코드를 재생성한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

### 테스트

#### 단위 테스트

테스트 위치: `src/app/clusters/<cluster-name>/tests/`

`chip::Testing::ClusterTester`는 인코더, 핸들러, 원시 TLV 버퍼를 수동으로 모킹할 필요를 줄인다.

| 검증 대상 | 방법 |
|---|---|
| 테스트 설정 | mock delegate로 클러스터에 테스트 데이터 주입 |
| 메타데이터 | `Attributes()`와 `AcceptedCommands()`의 정확성 확인 |
| 읽기 | `tester.ReadAttribute()`로 읽고 mock 데이터와 비교 |
| 명령 | `tester.Invoke()`로 호출하고 `Protocols::InteractionModel::Status` 확인 |
| 변경 보고 | `tester.GetDirtyList()`로 변경 속성 표시 확인 |
| no-op | 변경 표시와 delegate/driver 콜백이 발생하지 않는지 확인 |

메타데이터가 올바르지 않으면 `ClusterTester`가 읽기나 명령 호출을 거부한다.

자세한 내용은 [ClusterTester Helper Class Guide](../cluster_and_device_type_dev/cluster_tester.md)를 참고한다.

#### 예제 애플리케이션 및 통합 테스트

- `all-clusters-app` 같은 예제 애플리케이션에 클러스터를 통합한다.
- `chip-tool` 또는 `matter-repl`로 수동 검증한다.
- 예제 애플리케이션을 대상으로 종단 간 동작을 확인하는 통합 테스트를 작성한다.

### `.matter` IDL 및 정의 검증

#### 형식과 데이터 출처

`.matter`는 데이터 구조, 클러스터 정의, 엔드포인트 구성을 사람이 읽을 수 있도록 표현하는 IDL 형식이다. 사람과 기계 모두 읽기 쉽게 설계되었으며 ZAP 기반 정의 검증 도구의 기반이다.

형식 설명: [matter/idl/README.md](../../scripts/py_matter_idl/matter/idl/README.md)

SDK의 CSA XML 정의는 `data_model/clusters`에 있다. 공식 Matter 스펙을 대상으로 scraper를 실행하여 갱신한다.

**주의:** scraper는 개발 중이므로 XML이 불완전하거나 오류를 포함할 수 있다.

갱신 안내: [data_model/README.md](../../data_model/README.md)

#### CSA XML을 `.matter`로 변환

`matter-data-model-xml-parser`는 하나 이상의 CSA XML 파일을 `.matter`로 변환한다.

```sh
matter-data-model-xml-parser data_model/clusters/BooleanState.xml
```

| 인자 | 기능 |
|---|---|
| `-o/--output PATH` | STDOUT 대신 지정 경로에 결과 저장 |
| `--compare PATH` | 비교할 `.matter` 파일 읽기. `--compare-output`과 함께 사용해야 함 |
| `--compare-output PATH` | `--compare` 입력 중 XML과 대응하는 클러스터 부분집합을 지정 경로에 출력 |

`--compare`와 `--compare-output`을 함께 사용하면 주석 제거와 요소의 알파벳순 정렬을 통해 읽기 쉬운 diff를 얻을 수 있다.

#### 스펙과 SDK 비교

비교에 사용하는 입력:

- `data_model/clusters/*.xml`: 공식 스펙 정의로 간주
- `src/controller/data_model/controller-clusters.matter`: SDK에 정의된 모든 클러스터

```sh
matter-data-model-xml-parser \
     -o out/spec.matter                                             \
     --compare-output out/sdk.matter                                \
     --compare src/controller/data_model/controller-clusters.matter \
     data_model/clusters/DoorLock.xml                               \
  && diff out/{spec,sdk}.matter
```

scraper가 개발 중이므로 diff는 사람이 검토해야 한다. 도구 오류나 스펙의 Zigbee 전용 표식 등이 차이의 원인일 수 있다.

#### 디바이스 `.matter` lint

`matter-idl-lint`는 `.matterlint`에 표현된 규칙으로 기본 적합성을 검사한다.

규칙 출처:

- silabs XML에서 미리 로드한 규칙: 필수 속성 존재 여부 검사
- 하드코딩된 규칙: 특정 엔드포인트의 필수 클러스터와 속성 등 검사

```sh
matter-idl-lint examples/window-app/common/window-app.matter
```