---
entity: all
ids: []
source_paths: ['docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md', 'docs/guides/matter_idl_tooling.md', 'docs/guides/writing_clusters.md']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# all

## 개요

Matter(connectedhomeip)의 클러스터 및 디바이스 타입 개발과 `.matter` 기반 검증을 종합한 문서이다.

개발의 주요 단계는 다음과 같다.

1. Matter 스펙을 바탕으로 클러스터 및 디바이스 타입 XML을 정의한다.
2. 클러스터의 로직과 데이터 관리를 구현한다.
3. ZAP 코드 생성과 빌드 시스템에 연결한다.
4. 애플리케이션의 엔드포인트 구성과 클러스터 초기화를 연결한다.
5. 단위 테스트, 통합 테스트 및 스펙 비교로 동작과 정의를 검증한다.

제공된 문서는 Ember 및 override 기반 구현과 `ServerClusterInterface` 기반의 code-driven 구현을 각각 설명한다. `Writing and Updating Clusters`는 새로운 code-driven 클러스터에 통합 구현 방식과 builder-style `Config`를 권장한다.

## 관련 문서

### Implementing New Clusters & Device Types

원문: `docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md`

클러스터 구현, ZAP/Ember 코드 생성을 위한 정의 및 연결 코드, 정확성과 인증을 입증할 테스트 자료가 개발 대상이다. 이 문서는 그중 SDK의 클러스터 및 디바이스 타입 구현에 집중한다.

#### 정의 및 빌드 연결

| 대상 | 설명 | 위치 |
| --- | --- | --- |
| 클러스터 정의 | 구조체, enum, 속성, 명령, 이벤트 등을 XML로 표현 | `src/app/zap-templates/zcl/data-model/chip/` |
| 클라이언트 구현 | 코드 생성 결과에 연결 코드를 작성 | 코드 생성 기반 |
| 서버 구현 | Ember 및/또는 `AttributeAccessInterface`, `CommandHandlerInterface`를 사용한 C++ 구현 | `src/app/clusters/<your_cluster_name>` |
| 클러스터 빌드 | 코드 생성 데이터를 사용해 클러스터 목록을 구성 | `src/app/chip_data_model.gni` |
| 디바이스 타입 정의 | XML로 적합성 조건을 정의 | `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml` |

정의 추가 위치와 절차는 [How To Add New Device Types & Clusters](how_to_add_new_dts_and_clusters.md)를 참고한다. 생성 결과는 [.matter parser tools](https://project-chip.github.io/connectedhomeip-doc/guides/matter_idl_tooling.html)로 스펙과 비교해야 한다.

#### ZAP에서 확인할 사항

[ZAP](../zap_and_codegen/zap_intro.md) 소개 문서를 참고하고, 다음 명령으로 구성을 연다.

```sh
./scripts/tools/zap/run_zaptool.sh <filename>
```

확인 항목:

- 엔드포인트 구성의 디바이스 타입 목록에 새 디바이스 타입이 표시되는지 확인한다.
- 클러스터가 XML의 `domain`에 해당하는 그룹에 표시되는지 확인한다.
- 예상한 속성, 명령, 이벤트가 모두 있는지 확인한다.
- 각 속성의 저장 옵션이 올바른지 확인한다.

#### Ember와 override

| 구분 | Ember | override |
| --- | --- | --- |
| 구성 시점 | 컴파일 시 생성 | 실행 시 등록 |
| 주요 역할 | 엔드포인트, 속성, 명령 등의 설정과 접근 | 속성 접근 및 명령 처리의 사용자 정의 |
| 인터페이스 | 생성된 함수와 서버 콜백 | `AttributeAccessInterface`, `CommandHandlerInterface` |
| 처리 순서 | override가 처리하지 않은 경우 사용 가능 | Ember보다 먼저 호출 |
| 테스트 | 단위 테스트가 매우 어려움 | 단위 테스트 가능 |

빌드는 Ember 함수 시그니처와 기본 구현을 생성한다. 클러스터 서버는 초기화, 명령, 속성 접근, 이벤트 생성에 필요한 콜백을 구현한다. Interaction Model은 수신한 클러스터 상호작용을 Ember 함수로 전달한다.

override는 더 많은 제어를 제공하지만 복잡도가 높다. ZAP에서 설정된 경우 Ember로 처리를 넘길 수 있다.

#### 서버 초기화와 속성 저장

- `EmberAfInitializeAttributes`: ZAP에서 `RAM`으로 지정한 속성 저장소에 기본값을 설정한다.
- `Matter<Cluster>PluginServerCallback`: 헤더는 생성되며, `.cpp` 구현은 서버 클러스터 코드에 작성한다. 클러스터 및 override 설정에 사용한다.
- `chip::app::AttributeAccessInterfaceRegistry::Instance().Register`: 외부에서 속성 읽기와 쓰기를 처리할 때 사용한다.

| ZAP 저장 옵션 | 저장소 | 읽기·쓰기 | override 동작 |
| --- | --- | --- | --- |
| `RAM` | 자동 할당 | Ember가 처리하며 `Accessors.h`에 `Get`, `Set` 함수 생성 | override에서 인코딩하지 않으면 저장소로 처리를 넘길 수 있음 |
| `External` | 할당하지 않음 | access override 등록 필요 | Ember 저장소로 처리를 넘길 수 없음 |

`RAM` 속성을 override에서 항상 인코딩하면 할당된 Ember 저장 공간이 낭비된다.

#### 속성 읽기, 쓰기 및 영속성

- [`AttributeAccessInterface::Read()`](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h#L424)는 `aPath.mAttributeId`로 속성을 구분하고 `aEncoder.Encode(mSomeValue)`와 같은 방식으로 값을 인코딩한다.
- 목록은 청크 처리가 올바르게 이루어지도록 `EncodeList`를 사용해야 한다.
- 쓰기는 읽기와 같은 경로를 거쳐 [`AttributeAccessInterface::Write()`](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h#444)에 도달한다.
- 속성 핸들러는 제약 조건 검사와 영속성 처리를 책임진다.

이 문서는 영속성 관련 구성으로 다음을 제시한다.

- `AttributePersistence`와 `AttributePersistenceProvider`
- [`src/app/AttributePersistence.h`](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributePersistence.h)
- 단위 테스트용 `TestPersistentStorageDelegate`와 `DefaultAttributePersistenceProvider` 조합

Ember 경로에서는 인코딩과 디코딩을 Ember가 처리한다. 단순한 속성에는 적합하지만 복잡한 속성 간 상호작용을 구현하기는 어려울 수 있다.

속성 변경 콜백은 여러 예제에서 사용할 수 있도록 구현해야 한다.

```cpp
void MatterPostAttributeChangeCallback(const chip::app::ConcreteAttributePath & attributePath,
                                       uint8_t type, uint16_t size, uint8_t * value)
```

#### 명령 처리

**override 경로**

- `CommandHandlerInterface`를 구현한다.
- `InteractionModelEngine::RegisterCommandHandler`로 실행 시 등록한다.
- `HandleCommand`를 사용하면 처리 여부가 설정된다.
- 직접 처리할 때는 명령 처리 여부를 지정해야 하며, 처리하지 않으면 기본적으로 Ember로 넘어간다.
- 전적으로 `CommandHandlerInterface`로 처리하는 클러스터는 `src/app/common/templates/config-data.yaml`에 추가하여 Ember 명령 콜백 생성을 비활성화한다.

**Ember 경로**

- 정적 콜백 `emberAf<ClusterName><CommandName>Callback`을 사용한다.
- 처리했으면 `true`를 반환한다.
- `false`를 반환하면 유효하지 않은 명령 응답이 반환된다.

두 경로 모두 다음 책임이 있다.

- `AddResponse` 또는 `AddStatus`로 호출자에게 결과를 반환한다.
- 제약 조건을 검사한다.
- 스펙에 맞는 상태 또는 응답을 반환한다.

#### 구독, 이벤트 및 동적 엔드포인트

- 생성된 `Get`/`Set` 함수를 통해 Ember 저장소를 사용하면 속성 변경 보고가 처리된다.
- `AttributeAccessInterface`를 사용하면 `MatterReportingAttributeChangeCallback`으로 변경 사실을 보고 엔진에 알려야 한다.
- 이벤트에는 직접적인 Ember 지원이 없다. `EventLogging.h`의 `LogEvent`를 호출한다.
- `LogEvent`를 사용할 때 호출자는 Matter 스택 잠금을 획득하거나 이벤트를 Matter 이벤트 큐에 넣어야 한다.
- ZAP 구성은 컴파일 시 고정되지만, `emberAfSetDynamicEndpoint`로 실행 시 동적 엔드포인트를 등록할 수 있다.
- 동적 엔드포인트는 브리지에서 흔히 사용한다. 자체 속성 저장소는 정적 엔드포인트뿐 아니라 동적 엔드포인트도 고려해야 한다.

### The `.matter` IDL file format

원문: `docs/guides/matter_idl_tooling.md`

`.matter`는 데이터 구조, 클러스터 정의, 엔드포인트 구성을 사람이 읽을 수 있게 표현하는 IDL 형식이다. ZAP 기반 클러스터 정의를 검증하는 도구의 기반으로 사용된다.

형식 상세: [matter/idl/README.md](../../scripts/py_matter_idl/matter/idl/README.md)

#### CSA XML 정의 파싱

SDK의 `data_model/clusters`에는 공식 Matter 스펙을 스크래핑한 CSA XML 데이터 정의 사본이 있다. 갱신 방법은 [data_model/README.md](../../data_model/README.md)에 설명되어 있다.

> 스크래퍼는 개발 중이므로 XML이 불완전하거나 오류를 포함할 수 있다.

`matter-data-model-xml-parser`는 하나 이상의 CSA XML 파일을 `.matter`로 변환한다.

```sh
matter-data-model-xml-parser data_model/clusters/BooleanState.xml
```

| 인자 | 설명 |
| --- | --- |
| `-o/--output PATH` | STDOUT 대신 지정한 경로에 출력 |
| `--compare PATH` | 비교할 `.matter` 파일을 읽음. `--compare-output`과 함께 사용해야 함 |
| `--compare-output PATH` | `--compare`에서 읽은 클러스터 중 입력 XML에 대응하는 부분을 지정 경로에 출력 |

`--compare`와 `--compare-output`을 함께 사용하면 주석을 제거하고 요소를 알파벳순으로 정렬하여 비교하기 쉬운 출력을 생성한다.

#### SDK와 스펙 비교

비교에서는 다음을 사용한다.

- 스펙 정의: `data_model/clusters/*.xml`
- SDK의 전체 클러스터 정의: `src/controller/data_model/controller-clusters.matter`

```sh
matter-data-model-xml-parser \
     -o out/spec.matter                                             \
     --compare-output out/sdk.matter                                \
     --compare src/controller/data_model/controller-clusters.matter \
     data_model/clusters/DoorLock.xml                               \
  && diff out/{spec,sdk}.matter
```

스크래퍼가 개발 중이므로 차이 결과는 사람이 검토해야 한다. 도구 오류나 스펙의 Zigbee 전용 표시 등이 차이의 원인일 수 있다.

#### 디바이스 구성 lint

`matter-idl-lint`는 `.matterlint`로 표현한 기본 적합성 규칙을 검사한다.

규칙에는 다음이 포함된다.

- silabs XML에서 미리 읽어온 필수 속성 규칙
- 특정 엔드포인트의 필수 클러스터 및 속성 등에 대한 하드코딩된 규칙

```sh
matter-idl-lint examples/window-app/common/window-app.matter
```

### Writing and Updating Clusters

원문: `docs/guides/writing_clusters.md`

새로운 code-driven 클러스터의 정의, C++ 구현, 빌드 및 애플리케이션 통합, 테스트를 설명한다.

#### XML 정의와 코드 생성

클러스터 XML은 `src/app/zap-templates/zcl/data-model/chip`에 둔다.

- [Alchemy](https://github.com/project-chip/alchemy)로 스펙의 `asciidoc`를 파싱하여 XML을 생성하거나 갱신한다.
- XML 수동 편집은 오류 가능성 때문에 권장하지 않는다.
- XML 준비 후 코드 생성을 실행한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

상세: [code generation guide](../zap_and_codegen/code_generation.md)

#### 디렉터리와 구현 구조

- 구현 및 단위 테스트 디렉터리: `src/app/clusters/<cluster-directory>/`
- ZAP 서버 디렉터리 매핑: `src/app/zap_cluster_list.json`의 `ServerDirectories`
- 매핑 대상: 클러스터의 `UPPER_SNAKE_CASE` define과 `src/app/clusters` 아래 디렉터리 이름
- 권장 디렉터리 이름: `cluster-name-server`
- `ServerClusterInterface` 구현 파일 이름: `ClusterNameSnakeCluster.h/cpp`

**권장: 통합 구현**

클러스터 로직, 데이터 저장소, `ServerClusterInterface` 구현을 하나의 클래스에 둔다. 보통 `DefaultServerCluster`를 상속한다. 불필요한 연결 코드와 가상 함수 변환 계층을 줄여 flash 사용량을 줄인다.

참조: [Basic Information](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/basic-information)

**새 클러스터에 비권장: 분리된 구현**

`ClusterLogic`에 로직을 두고 `ClusterImplementation`이 변환 계층을 담당하는 방식은 테스트 격리에는 도움이 되었지만 flash와 RAM 오버헤드가 있다.

기존 사례: [Administrator Commissioning](https://github.com/project-chip/connectedhomeip/tree/master/src/app/clusters/administrator-commissioning-server)

애플리케이션 콜백이 필요하면 선택적으로 `ClusterDriver` 또는 `Delegate`를 제공한다. 문서는 `Delegate`의 다의성을 피하기 위해 `Driver`라는 용어를 권장한다.

#### builder-style `Config`

새 code-driven 클러스터는 feature와 필수 매개변수가 함께 설정되도록 builder-style `Config`를 사용해야 한다.

참조: [Level Control Cluster](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/level-control/LevelControlCluster.h)

원칙:

- 클러스터 클래스 내부에 `Config`를 정의한다.
- 복잡한 구성은 private 멤버가 있는 `class`로 만들어 builder 메서드 사용을 강제한다.
- 단순한 구성은 public 멤버가 있는 `struct`도 허용한다.
- `With<Feature>(...)`는 `Config` 참조를 반환하여 연쇄 호출을 지원한다.
- feature 설정 메서드는 `FeatureMap` 비트와 관련 속성을 함께 초기화한다.
- `EndpointId`는 `Config`가 아니라 클러스터 생성자에 직접 전달한다.
- 클러스터는 `Config` 자체를 저장하지 않고 값을 개별 멤버로 추출한다. 변경되지 않는 값에는 `const`를 사용할 수 있다.

원문의 `LevelControlCluster` 예에서 `WithLighting`은 다음을 함께 수행한다.

- `LevelControl::Feature::kLighting` 설정
- `WithMinLevel(1)` 호출
- `WithMaxLevel(254)` 호출
- `mStartUpCurrentLevel` 설정

#### 애플리케이션 부담과 검증 순서

클러스터는 영속성, 타이머, 복잡한 상태 머신 등 공통 로직을 내부에서 처리해야 한다. 애플리케이션에는 대응이 필요한 중요한 이벤트나 변경을 알리고, 복잡한 연동에는 helper나 기본 구현을 제공한다.

쓰기 및 명령에 애플리케이션 판단이 필요하면 delegate/driver를 사전 검사로 사용한다.

1. 클러스터가 스펙의 범위, 제약 조건, 상태 제한을 검사한다.
2. 값이 바뀌지 않는 no-op을 조기에 처리한다.
3. delegate/driver에 제안된 새 값을 전달한다.
4. 허용된 경우에만 상태를 반영하고 변경을 알린다.

일반 검증 지침은 콜백이 `Protocols::InteractionModel::Status`를 반환하도록 한다. `Success`가 아닌 상태는 작업을 거부하며, 클러스터는 해당 상태를 요청자에게 전달해야 한다.

별도로 속성별 콜백 지침은 `On<AttributeName>Changed`의 `bool` 반환 방식을 설명한다.

- `true`: 변경 허용
- `false`: 변경 거부
- `Status` 반환 API의 거부 결과: `Protocols::InteractionModel::Status::Failure`
- `CHIP_ERROR` 반환 API의 거부 결과: `CHIP_ERROR_INCORRECT_STATE`
- 기본 콜백 구현: `true` 반환

이는 원문에 함께 제시된 두 반환 방식이며, 속성별 사례는 [Boolean State Configuration delegate](https://github.com/project-chip/connectedhomeip/blob/master/src/app/clusters/boolean-state-configuration-server/boolean-state-configuration-delegate.h)를 참고한다.

#### 속성 API와 변경 보고

- feature 종속 요소는 feature map으로 제어한다.
- 순수 선택 요소는 boolean 또는 `BitFlags`로 제어한다.
- 활성화된 feature와 선택 요소에 맞게 사용 가능한 속성 및 명령을 보고한다.
- 모든 속성에 public getter를 제공한다.
- 변경 가능한 속성에는 스펙에 맞는 setter 또는 원자적 변경을 수행하는 상위 API를 제공한다.
- getter는 가능하면 값 복사를 반환한다.
- 내부 데이터의 포인터나 참조 반환이 불가피하면 즉시 사용만 가능하며 저장해서는 안 된다는 수명 제한을 문서화한다.

API 사례: `GetCurrentSensitivityLevel()`, `GetAlarmsActive()`, `SetCurrentSensitivityLevel()`

변경 보고:

- `Startup`은 `ServerClusterContext`를 받는다.
- `interactionContext->dataModelChangeListener->MarkDirty(path)`로 변경을 알린다.
- 해당 클러스터가 관리하는 경로에는 `NotifyAttributeChanged` helper를 사용할 수 있다.
- 쓰기는 `WriteImpl`과 `NotifyAttributeChangedIfSuccess`로 구성할 수 있다.
- 알림을 보내지 않아야 하는 no-op 쓰기는 `ActionReturnStatus::FixedStatus::kWriteSuccessNoOp`를 반환한다.

```cpp
VerifyOrReturnValue(mValue != newValue, ActionReturnStatus::FixedStatus::kWriteSuccessNoOp);
```

no-op 쓰기는 네트워크 속성 변경 알림과 애플리케이션 delegate/driver 콜백을 모두 발생시키지 않아야 한다.

#### 영속성 및 고급 인터페이스

| 항목 | 지침 |
| --- | --- |
| 스칼라 속성 영속성 | `src/app/persistence/AttributePersistence.h`의 `AttributePersistence` 사용 |
| 속성 영속성 공급자 | `ServerClusterContext`가 `AttributePersistenceProvider` 제공 |
| 일반 데이터 저장 | 컨텍스트가 제공하는 `PersistentStorageDelegate` 사용 |
| flash/RAM 최적화 | 필요하면 `C++` 템플릿으로 feature와 속성을 컴파일 시 선택 |
| `ListAttributeWriteNotification` | 큰 목록을 청크 단위로 영속화하는 등의 고급 처리용. 대부분의 클러스터에는 기본 구현으로 충분 |
| `EventInfo` | 이벤트 읽기에 기본값 이외의 권한이 필요하면 구현 |
| `AcceptedCommands` | 서버가 처리할 수 있는 `client => server` 명령 |
| `GeneratedCommands` | 서버가 생성할 수 있는 `server => client` 응답 명령 |

`EventInfo`는 예를 들어 `Administrator` 권한이 필요한 이벤트의 접근 제한에 사용된다. 새 클러스터마다 이벤트 권한을 검토해야 한다.

#### 빌드 파일 구성

| 파일 | 역할 |
| --- | --- |
| `BUILD.gn` | 보통 `<cluster-directory>` 이름의 `source_set` 정의 |
| `app_config_dependent_sources.gni` | 일반적으로 `CodegenIntegration.cpp`와 필요한 helper/호환 계층 나열 |
| `app_config_dependent_sources.cmake` | `.gni`의 파일과, `BUILD.gn` 의존성이 제공하지만 CMake의 `libCHIP` 빌드에는 없는 추가 파일 포함 |

`src/app/chip_data_model.gni`는 다음 형태로 의존성을 추가하므로 기본 타깃 이름이 중요하다.

```gn
deps += [ "${_app_root}/clusters/${cluster}" ]
```

`chip_data_model.gni`와 `chip_data_model.cmake`는 애플리케이션 종속 소스와 `endpoint_config.h` 등의 Ember 생성 설정을 하나의 source set으로 묶는다.

#### 애플리케이션 통합

1. `src/app/zap_cluster_list.json`에 클러스터와 디렉터리 매핑을 추가한다.
2. `CodegenIntegration.cpp`를 작성한다.
3. `app_config_dependent_sources.gni`와 `app_config_dependent_sources.cmake`에 통합 소스와 의존성을 추가한다.
4. 생성된 `<app/static-cluster-config/<cluster-name>.h`의 애플리케이션별 정적 구성으로 각 엔드포인트의 클러스터를 초기화한다.
5. 다음 콜백을 구현한다.
   - `Matter<Cluster>ClusterInitCallback(EndpointId)`
   - `Matter<Cluster>ClusterShutdownCallback(EndpointId)`
6. `src/app/common/templates/config-data.yaml`의 `CodeDrivenClusters`에 클러스터를 추가한다.
7. `src/app/zap-templates/zcl/zcl.json`과 `zcl-with-test-extensions.json`의 `attributeAccessInterfaceAttributes`에 해당 클러스터의 모든 비목록 속성을 추가한다. 이를 통해 Ember의 속성 메모리 할당을 방지한다.
8. ZAP 재생성을 실행한다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

#### 단위 테스트와 통합 테스트

단위 테스트 위치: `src/app/clusters/<cluster-name>/tests/`

`chip::Testing::ClusterTester`를 사용하면 encoder, handler, 원시 TLV 버퍼를 수동으로 mock할 필요가 줄어든다.

상세: [ClusterTester Helper Class Guide](../cluster_and_device_type_dev/cluster_tester.md)

검증 항목:

- mock delegate로 테스트 데이터를 주입한다.
- `Attributes()`와 `AcceptedCommands()`의 메타데이터를 확인한다. 잘못된 메타데이터는 `ClusterTester`의 읽기나 명령 호출 거부로 이어진다.
- `tester.ReadAttribute()`로 속성 값을 확인한다.
- `tester.Invoke()`로 명령 처리와 `Protocols::InteractionModel::Status` 결과를 확인한다.
- `tester.GetDirtyList()`로 실제 변경의 보고 여부와 no-op의 미보고 여부를 확인한다.
- feature 및 선택 속성·명령의 여러 조합을 검사한다.

클러스터를 `all-clusters-app`과 같은 예제 애플리케이션에 통합하고, `chip-tool` 또는 `matter-repl`로 수동 검증한다. 별도의 통합 테스트로 예제 애플리케이션에 대한 종단 간 기능도 검증한다.