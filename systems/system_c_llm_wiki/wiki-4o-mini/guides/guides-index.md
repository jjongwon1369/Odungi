---
entity: all
ids: []
source_paths: ['docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md', 'docs/guides/matter_idl_tooling.md', 'docs/guides/writing_clusters.md']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-4o-mini
---

## 개요

이 문서는 새로운 클러스터 및 디바이스 타입을 구현하는 과정을 설명합니다. 클러스터 구현, ZAP을 통한 코드 생성을 위한 지원 자료 작성, 단위 테스트 및 인증을 수행하는 데 필요한 단계가 포함되어 있습니다.

## 스펙

- **클러스터 정의**
  - XML
  - 구조체, 열거형, 속성, 명령, 이벤트 등을 설명
  - 사양을 코드로 직접 변환
  - [src/app/zap-templates/zcl/data-model/chip/](https://github.com/project-chip/connectedhomeip/tree/master/src/app/zap-templates/zcl/data-model/chip)

- **클러스터 구현**
  - 클라이언트 측 - 코드 생성, 당신이 연결
  - 서버 측 - cpp 구현을 통해 Ember 및 / 또는
    [AttributeAccessInterface](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h) 및
    [CommandHandlerInterface](https://github.com/project-chip/connectedhomeip/blob/master/src/app/CommandHandlerInterface.h)
  - `src/app/clusters/<your_cluster_name>`
  - 빌드 파일:
    [src/app/chip_data_model.gni](https://github.com/project-chip/connectedhomeip/blob/master/src/app/chip_data_model.gni)
  - 빌드 파일은 코드 생성기에서 클러스터 목록을 자동으로 채우기 위해 사용됩니다.

- **디바이스 타입 정의**
  - XML 정의로 적합성 정의
  - [src/app/zap-templates/zcl/data-model/chip/matter-devices.xml](https://github.com/project-chip/connectedhomeip/blob/master/src/app/zap-templates/zcl/data-model/chip/matter-devices.xml)

### ZAP, Ember 및 오버라이드

- 목표: ZAP이 새로운 클러스터를 이해하여 디바이스에서 사용할 수 있도록 함 (XML 및 연결)

### 클러스터 정의 및 ZAP

[ZAP](../zap_and_codegen/zap_intro.md)에서 ZAP의 소개를 참조하십시오. 변경 사항을 구현한 후 클러스터와 디바이스 타입은 ZAP에서 표시되어야 하며, 이는 zaptool을 사용하여 확인할 수 있습니다.

```bash
./scripts/tools/zap/run_zaptool.sh <filename>
```

클러스터 및 디바이스 타입이 ZAP에 올바르게 구현되었는지 확인하려면 엔드포인트 구성을 열고 디바이스 타입이 디바이스 타입 목록에 나타나는지 확인합니다.

다음으로 클러스터를 확인하십시오. XML의 "domain" 매개변수는 클러스터가 속하는 그룹을 조정합니다. 해당 클러스터의 모든 속성, 명령 및 이벤트가 있어야 합니다.

마지막으로 속성이 적절히 스토리지 옵션이 설정되었는지 확인하십시오.

### 클러스터 구현 - Ember 및 오버라이드

- Ember: 디바이스의 엔드포인트 / 속성 / 명령 등을 설정 및 액세스하기 위한 레이어

  - 빌드는 Ember 함수 시그니처와 기본값을 생성합니다.
  - 클러스터 서버 코드는 초기화, 명령, 속성 액세스 및 이벤트 생성을 위한 콜백을 구현합니다.
  - 상호 작용 모델 레이어는 클러스터에 대한 수신 상호 작용을 처리할 때 Ember 함수를 호출합니다.

- 오버라이드
  - Ember 레이어는 컴파일 시간에 _생성_된 반면 오버라이드는 런타임에 _설치_됩니다.
  - 오버라이드는 속성 액세스나 명령 처리를 위한 Ember 레이어보다 먼저 호출됩니다.
  - 훨씬 더 많은 제어를 허용하지만 더 복잡합니다.
  - **단위 테스트 가능**
  - 이러한 두 가지는 ZAP에서 설정된 경우 Ember 레이어로 넘어가는 것을 허용합니다.

### 클러스터 서버 초기화

다음 다이어그램은 Matter 코어로 들어오는 메시지가 클러스터 초기화 코드로 끝나는 흐름을 보여줍니다.

- EmberAfInitializeAttributes: Ember 속성 스토리지 - zap에서 "RAM"으로 표시된 모든 속성에 대해 기본값을 설정합니다.
- Matter<Cluster>PluginServerCallback - .h는 생성된 파일이며, .cpp 구현은 서버 클러스터 코드에서 수행됩니다. 이를 사용하여 클러스터를 설정하고 chip::app::AttributeAccessInterfaceRegistry::Instance().Register에서 오버라이드를 설정합니다.

파란색 섹션은 오버라이드할 수 있습니다.

### 클러스터 서버 속성

**두 가지 메커니즘**
- Ember 레이어
- 오버라이드

**ZAP 파일 및 구현**
- zap 파일에서 **“RAM”** 스토리지로 표시된 속성에 대해
  - 스토리지가 자동으로 할당되고 Ember가 읽기/쓰기를 처리합니다.
  - Accessors.h에서 각 속성에 대한 "Get" 및 "Set" 함수가 생성됩니다.
  - 클러스터에 오버라이드를 등록할 수 있습니다. 오버라이드에서 속성을 인코딩하려고 시도하지 않으면 스토리지로 넘어갑니다.

- zap 파일에서 **“External”** 스토리지로 표시된 속성에 대해
  - 스토리지가 할당되지 않으며, Ember 스토리지로 넘어가지 않습니다.
  - 이들이 작동하려면 액세스 오버라이드를 등록해야 합니다.

## SDK 정의

### `.matter` IDL 파일 형식

`.matter` IDL 파일 형식은 데이터 구조, 클러스터 정의 및 엔드포인트 구성의 사람 친화적인 표현을 위해 설계되었습니다.

SDK에는 `data_model/clusters`에 CSA XML 데이터 정의의 복사본이 포함되어 있습니다.

스크립트 `matter-data-model-xml-parser`는 하나 이상의 CSA 데이터 모델 XML 파일을 파싱하고 그 내용을 `.matter` 형식으로 출력할 수 있는 기능을 가지고 있습니다.

### `.matter` 파일을 사양에 대해 비교하기

도구의 인수를 결합하면 SDK와 사양 간의 차이를 얻을 수 있습니다.

```bash
matter-data-model-xml-parser \
     -o out/spec.matter                                             \
     --compare-output out/sdk.matter                                \
     --compare src/controller/data_model/controller-clusters.matter \
     data_model/clusters/DoorLock.xml                               \
  && diff out/{spec,sdk}.matter
```

## 구현

### 클러스터 정의 (XML)

클러스터는 Matter 사양에 기반하여 정의됩니다. 그에 대한 C++ 코드는 `src/app/zap-templates/zcl/data-model/chip`에 위치한 XML 정의에서 생성됩니다.

- **XML 생성:** 클러스터 XML을 만들거나 업데이트하려면, [Alchemy](https://github.com/project-chip/alchemy)를 사용하여 사양의 `asciidoc`를 파싱합니다.
- **코드 생성 실행:** XML이 준비되면 코드 생성 스크립트를 실행합니다. 일반적으로 다음과 같이 실행하면 충분합니다.

```bash
./scripts/run_in_build_env.sh 'scripts/tools/zap_regen_all.py'
```

### C++ 구현

클러스터의 새 디렉토리를 `src/app/clusters/<cluster-directory>/`에 생성합니다. 이 디렉토리는 클러스터 구현과 그 단위 테스트를 포함합니다.

#### 파일 구조

- **명칭 규칙**
  - 클러스터 디렉토리 이름은 `cluster-name-server`로 설정
  - `ClusterNameSnakeCluster.h/cpp`로 `ServerClusterInterface` 구현

### 추천 구현 패턴

자원 제약이 있는 디바이스에서 플래시와 RAM 사용을 최적화하기 위해 **결합된 구현** 패턴을 추천합니다. 구현을 별도로 분리하는 것은 불필요한 오버헤드를 초래합니다.

다음은 기본 JSON 구조를 기반으로 한 코드 스니펫입니다.

### 구현 세부사항

#### 속성 및 기능 처리

구현은 활성화된 기능 및 선택적 항목에 따라 사용 가능한 속성과 명령을 올바르게 보고해야 합니다.

- 기능 맵을 사용하여 기능에 따라 요소를 제어합니다.
- 순수 선택적 요소에 대해서는 부울 플래그 또는 `BitFlags`를 사용합니다.

#### 단위 테스트

단위 테스트는 `src/app/clusters/<cluster-name>/tests/`에 위치해야 합니다.

## 예시

- 클러스터 테스트 범위 보장을 위한 단위 테스트를 작성합니다.
- 클러스터를 예제 애플리케이션인 `all-clusters-app`에 통합하여 실제 시나리오에서 테스트합니다.
- 통합 테스트를 추가하여 예제 애플리케이션에 대한 클러스터의 종단 간 기능을 검증합니다.

## 관련 문서

- [How To Add New Device Types & Clusters](how_to_add_new_dts_and_clusters.md)
- [ZAP](../zap_and_codegen/zap_intro.md)
- [AttributeAccessInterface](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributeAccessInterface.h)
- [CommandHandlerInterface](https://github.com/project-chip/connectedhomeip/blob/master/src/app/CommandHandlerInterface.h)
- [AttributePersistence](https://github.com/project-chip/connectedhomeip/blob/master/src/app/AttributePersistence.h)
- [ClusterTester Helper Class Guide](../cluster_and_device_type_dev/cluster_tester.md)
- [code generation guide](../zap_and_codegen/code_generation.md)