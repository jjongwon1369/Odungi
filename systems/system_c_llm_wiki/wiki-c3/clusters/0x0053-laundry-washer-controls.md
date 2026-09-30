---
entity: Laundry Washer Controls
ids: ['0x0053']
source_paths: ['data_model/1.7/clusters/LaundryWasherControls.xml', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h', 'src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Laundry Washer Controls

## 개요

Laundry Washer Controls는 세탁기와 같은 세탁 장치의 기능을 원격으로 모니터링하고 제어하는 클러스터이다. 여러 탈수 속도를 지원하는 `SPIN`과 여러 헹굼 주기를 지원하는 `RINSE`를 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0053` |
| 스펙 이름 | `Laundry Washer Controls Cluster` |
| 클러스터 이름 | `Laundry Washer Controls` |
| 리비전 | `2` |
| 분류 | hierarchy: `base`, role: `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `WASHERCTRL` |

## 스펙

출처: `data_model/1.7/clusters/LaundryWasherControls.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | Feature Map 적합성 조건 갱신 |

### Feature

| 비트 | 코드 | 이름 | 기능 |
|---|---|---|---|
| `0` | `SPIN` | `Spin` | 여러 탈수 속도 지원 |
| `1` | `RINSE` | `Rinse` | 여러 헹굼 주기 지원 |

두 Feature는 동일한 선택 그룹 `a`에 속하며, `min="1"`, `more="true"` 조건에 따라 하나 이상을 지원해야 한다.

### 데이터 타입

`NumberOfRinsesEnum`의 각 항목은 `RINSE` 지원 시 필수이다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `None` | 해당 세탁 모드에서 헹굼을 수행하지 않음 |
| `1` | `Normal` | 제조업체가 정한 일반 헹굼 수행 |
| `2` | `Extra` | 추가 헹굼 수행 |
| `3` | `Max` | 제조업체가 정한 최대 횟수의 헹굼 수행 |

### 속성

| ID | 이름 | 타입 | 접근 권한 | 필수 조건 | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `list`, 항목 `string` | 읽기: `view` | `SPIN` | 최대 16개, 각 문자열 최대 길이 64 |
| `0x0001` | `SpinSpeedCurrent` | `uint8` | 읽기: `view`, 쓰기: `operate` | `SPIN` | nullable, 최댓값 15 |
| `0x0002` | `NumberOfRinses` | `NumberOfRinsesEnum` | 읽기: `view`, 쓰기: `operate` | `RINSE` | 제공된 XML의 `<desc/>`에 구체적인 제약 설명 없음 |
| `0x0003` | `SupportedRinses` | `list`, 항목 `NumberOfRinsesEnum` | 읽기: `view` | `RINSE` | 최대 4개 |

제공된 스펙 XML에는 명령과 이벤트 정의가 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| domain | `Appliances` |
| name | `Laundry Washer Controls` |
| code | `0x0053` |
| define | `LAUNDRY_WASHER_CONTROLS_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `code="0xFFFD"`, `value="2"`, `side="either"` |

`NumberOfRinsesEnum`은 `enum8`이며, `None`, `Normal`, `Extra`, `Max`에 각각 `0x0`, `0x1`, `0x2`, `0x3`을 할당한다.

### 속성 매핑

모든 속성은 `side="server"`, `optional="true"`로 선언되지만, 대응하는 Feature를 지원하면 `mandatoryConform`에 따라 필수이다.

| ID | 이름 | define | SDK 타입 | 추가 설정 |
|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `SPIN_SPEEDS` | `array`, `entryType="char_string"` | `length="16"`, `SPIN` |
| `0x0001` | `SpinSpeedCurrent` | `SPIN_SPEED_CURRENT` | `int8u` | `max="15"`, `writable="true"`, `isNullable="true"`, `SPIN` |
| `0x0002` | `NumberOfRinses` | `NUMBER_OF_RINSES` | `NumberOfRinsesEnum` | `writable="true"`, `RINSE` |
| `0x0003` | `SupportedRinses` | `SUPPORTED_RINSES` | `array`, `entryType="NumberOfRinsesEnum"` | `length="4"`, `RINSE` |

스펙의 `SpinSpeeds` 문자열 최대 길이 64는 이 SDK XML의 속성 선언에는 명시되어 있지 않다.

### 생성 정보

이 XML은 Alchemy로 생성되었으며 직접 수정하지 않도록 표시되어 있다.

- 원본: `src/app_clusters/LaundryWasherControls.adoc`
- Git: `0.9-summer2026-111-g467a7f9e9`
- Alchemy: `v1.6.10`

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h` | `LaundryWasherControlsCluster`, `Config`, 상태 및 공개 API 정의 |
| `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp` | 속성 읽기·쓰기, 값 검증, 목록 인코딩 |
| `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h` | 애플리케이션별 `Delegate` 인터페이스 |
| `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h` | Endpoint 기반 접근 API 선언 |
| `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp` | 서버 등록·해제 및 Endpoint 기반 API 구현 |
| `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h` | `CodegenIntegration.h` 포함 |

### 클래스와 초기 설정

`chip::app::Clusters::LaundryWasherControlsCluster`는 `DefaultServerCluster`를 상속한다.

`Config`는 Feature 집합과 `Delegate`를 받거나, Feature 집합만 받아 `mDelegate`를 `nullptr`로 초기화한다. 두 생성자는 모두 `VerifyOrDie(mFeatures.HasAny())`로 Feature 비트가 하나 이상 설정되어 있는지 검사한다.

| 항목 | 선언 또는 값 |
|---|---|
| 탈수 속도 문자열 버퍼 길이 | `kMaxSpinSpeedLength = 64` |
| 탈수 속도 목록 최대 길이 | `kMaxSpinSpeedsLength = 16` |
| 지원 헹굼 목록 최대 길이 | `kMaxSupportedRinsesLength = 4` |
| 탈수 속도 상태 | `DataModel::Nullable<uint8_t> mSpinSpeedCurrent{}` |
| 헹굼 상태 초기값 | `LaundryWasherControls::NumberOfRinsesEnum::kNone` |

### 속성 접근

`ReadAttribute`는 다음과 같이 처리한다.

| 속성 | 처리 |
|---|---|
| `ClusterRevision` | `kRevision` 인코딩 |
| `FeatureMap` | `mFeatures` 인코딩 |
| `SpinSpeeds` | `ReadSpinSpeeds` 호출 |
| `SpinSpeedCurrent` | `mSpinSpeedCurrent` 인코딩 |
| `NumberOfRinses` | `mNumberOfRinses` 인코딩 |
| `SupportedRinses` | `ReadSupportedRinses` 호출 |

그 외 속성은 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`WriteAttribute`는 `SpinSpeedCurrent`와 `NumberOfRinses`만 디코딩하여 각각 `SetSpinSpeedCurrent`, `SetNumberOfRinses`에 전달한다. 그 외에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`로 `kMandatoryMetadata`와 Feature별 속성을 결합한다.

- `Feature::kSpin`: `SpinSpeedCurrent`, `SpinSpeeds`
- `Feature::kRinse`: `NumberOfRinses`, `SupportedRinses`

### 값 검증과 변경 콜백

#### `SetSpinSpeedCurrent`

1. `Feature::kSpin`이 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
2. `SpinSpeedIndexValidity`로 값을 검사한다.
   - null은 허용한다.
   - null이 아닌 경우 `mDelegate`가 없으면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
   - 값이 `kMaxSpinSpeedsLength` 이상이면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
   - `GetSpinSpeedAtIndex`가 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환하면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`로 변환한다.
   - 그 외 조회 결과는 그대로 반환한다.
3. `SetAttributeValue`가 변경을 나타내고 `mDelegate`가 있으면 `OnSpinSpeedCurrentChanged`를 호출한다.

#### `SetNumberOfRinses`

1. `Feature::kRinse`가 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
2. `NumberOfRinsesValidity`로 값을 검사한다.
   - `mDelegate`가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환한다.
   - 최대 `kMaxSupportedRinsesLength`개의 항목을 `GetSupportedRinseAtIndex`로 조회한다.
   - 성공적으로 조회한 항목 중 요청 값이 있으면 허용한다.
   - 조회 오류로 탐색이 중단되거나 일치하는 값이 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환한다.
3. `SetAttributeValue`가 변경을 나타내고 `mDelegate`가 있으면 `OnNumberOfRinsesChanged`를 호출한다.

### 목록 제공과 `Delegate`

`Delegate`는 `chip::app::Clusters::LaundryWasherControls`에 정의된다.

| 메서드 | 계약 |
|---|---|
| `GetSpinSpeedAtIndex(size_t index, MutableCharSpan & spinSpeed)` | 0부터 시작하는 인덱스의 문자열을 복사한다. 성공 시 `spinSpeed` 길이를 복사한 데이터 길이로 갱신해야 한다. |
| `GetSupportedRinseAtIndex(size_t index, NumberOfRinsesEnum & supportedRinse)` | 0부터 시작하는 인덱스의 지원 헹굼 값을 반환한다. |
| `OnSpinSpeedCurrentChanged(DataModel::Nullable<uint8_t> spinSpeedCurrent)` | `SpinSpeedCurrent` 변경 콜백. 기본 구현은 비어 있다. |
| `OnNumberOfRinsesChanged(NumberOfRinsesEnum numberOfRinses)` | `NumberOfRinses` 변경 콜백. 기본 구현은 비어 있다. |

두 조회 메서드는 순수 가상 함수이며, 목록 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환해야 한다.

`ReadSpinSpeeds`와 `ReadSupportedRinses`는 다음 공통 동작을 수행한다.

- `mDelegate`가 없으면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
- `EncodeList`로 각 목록을 최대 길이까지 인코딩한다.
- `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`는 정상적인 목록 종료로 처리한다.
- 그 외 조회 오류와 인코딩 오류는 전파한다.

무한 재귀 가능성을 피하기 위해 `OnSpinSpeedCurrentChanged`에서 `SetSpinSpeedCurrent`를, `OnNumberOfRinsesChanged`에서 `SetNumberOfRinses`를 호출하지 않아야 한다.

### `Delegate` 수명과 목록 변경 알림

`Delegate`는 클러스터가 파괴될 때까지 유효해야 한다.

클러스터의 `SetDelegate`는 포인터를 교체한 뒤 활성화된 Feature에 따라 다음 알림을 호출한다.

- `Feature::kSpin`: `NotifySpinSpeedsAttributeChanged`
- `Feature::kRinse`: `NotifySupportedRinsesAttributeChanged`

`Delegate`가 목록의 어느 인덱스에서든 이전과 다른 값을 반환하게 되면, 대응하는 알림 메서드를 호출해야 한다. 두 메서드는 해당 속성 ID로 `NotifyAttributeChanged`를 호출한다.

### 서버 등록과 해제

`CodegenIntegration.cpp`는 다음 크기로 `gServers`를 구성한다.

- `kLaundryWasherControlsFixedClusterCount`: `LaundryWasherControls::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kLaundryWasherControlsMaxClusterCount`: `kLaundryWasherControlsFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- 저장 타입: `LazyRegisteredServerCluster<LaundryWasherControlsCluster>`

`IntegrationDelegate`의 동작은 다음과 같다.

| 메서드 | 동작 |
|---|---|
| `CreateRegistration` | `featureMap`으로 `BitFlags<Feature>`와 `LaundryWasherControlsCluster::Config`를 구성하고 인스턴스를 생성한 뒤 등록 정보를 반환 |
| `FindRegistration` | 인스턴스가 생성되지 않았으면 `nullptr`, 생성되었으면 클러스터 포인터 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy` 호출 |

- `MatterLaundryWasherControlsPluginServerInitCallback`: 빈 구현이다.
- `MatterLaundryWasherControlsClusterInitCallback`: `CodegenClusterIntegration::RegisterServer`를 호출한다. `fetchFeatureMap = true`, `fetchOptionalAttributes = false`로 설정한다.
- `MatterLaundryWasherControlsClusterShutdownCallback`: `shutdownType`을 전달하여 `CodegenClusterIntegration::UnregisterServer`를 호출한다.
- `FindClusterOnEndpoint`: `CodegenClusterIntegration::FindClusterOnEndpoint`의 결과를 `LaundryWasherControlsCluster *`로 변환한다.

### Endpoint 기반 API

`chip::app::Clusters::LaundryWasherControls::LaundryWasherControlsServer`는 다음 API를 제공한다.

| API | 동작 |
|---|---|
| `SetDelegate` | Endpoint의 클러스터에 `Delegate`를 설정한다. 클러스터가 없으면 오류 로그를 남긴다. |
| `SetDefaultDelegate` | 하위 호환용 포인터 API. `VerifyOrDie(delegate != nullptr)` 검사 후 `SetDelegate`를 호출한다. |
| `SetSpinSpeedCurrent` | 클러스터의 `SetSpinSpeedCurrent`에 위임한다. |
| `GetSpinSpeedCurrent` | 클러스터의 `GetSpinSpeedCurrent` 결과를 출력 인자에 저장한다. |
| `SetNumberOfRinses` | 클러스터의 `SetNumberOfRinses`에 위임한다. |
| `GetNumberOfRinses` | 클러스터의 `GetNumberOfRinses` 결과를 출력 인자에 저장한다. |

`SetDelegate`는 헤더 주석상 `Server::Init` 호출 후에만 사용할 수 있다. `SetDefaultDelegate` 대신 `SetDelegate` 사용이 권장된다.

네 개의 속성 접근 API는 Endpoint에서 클러스터를 찾지 못하면 `CHIP_ERROR_NOT_FOUND`를 반환한다. 두 getter는 클러스터를 찾으면 값을 복사하고 `CHIP_NO_ERROR`를 반환한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
