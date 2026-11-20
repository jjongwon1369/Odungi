---
entity: Laundry Washer Controls
ids: ['0x0053']
source_paths: ['data_model/1.7/clusters/LaundryWasherControls.xml', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h', 'src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Laundry Washer Controls

## 개요

Laundry Washer Controls는 세탁기와 같은 세탁 장치가 제공하는 기능을 원격으로 모니터링하고 제어하는 클러스터이다. `SPIN`은 여러 탈수 속도, `RINSE`는 여러 헹굼 설정을 지원한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | Laundry Washer Controls |
| 스펙 이름 | Laundry Washer Controls Cluster |
| 클러스터 ID | `0x0053` |
| 리비전 | `2` |
| 분류 | `hierarchy="base"`, `role="application"` |
| 범위 | `Endpoint` |
| PICS 코드 | `WASHERCTRL` |

## 스펙

출처: `data_model/1.7/clusters/LaundryWasherControls.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | Feature Map 적합성 조건 갱신 |

### 기능

| 비트 | 코드 | 이름 | 설명 |
|---|---|---|---|
| `0` | `SPIN` | `Spin` | 여러 탈수 속도 지원 |
| `1` | `RINSE` | `Rinse` | 여러 헹굼 설정 지원 |

두 기능에는 `optionalConform choice="a" more="true" min="1"`이 지정되어 있다. 같은 선택 그룹에서 최소 하나를 지원해야 하며, 둘 다 지원할 수 있다.

### 데이터 타입

`NumberOfRinsesEnum`의 각 항목은 `RINSE` 기능에 대해 필수이다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `None` | 해당 세탁 모드에서 헹굼을 수행하지 않음 |
| `1` | `Normal` | 제조사가 정한 일반 헹굼 수행 |
| `2` | `Extra` | 추가 헹굼 수행 |
| `3` | `Max` | 제조사가 정한 최대 횟수의 헹굼 수행 |

### 속성

| ID | 이름 | 타입 | 접근 권한 | 필수 조건 | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `list`, 항목 `string` | 읽기: `view` | `SPIN` | 최대 16개, 문자열별 최대 길이 64 |
| `0x0001` | `SpinSpeedCurrent` | `uint8` | 읽기: `view`, 쓰기: `operate` | `SPIN` | 최대값 15, nullable |
| `0x0002` | `NumberOfRinses` | `NumberOfRinsesEnum` | 읽기: `view`, 쓰기: `operate` | `RINSE` | 제약 요소가 `<desc/>`로만 제공됨 |
| `0x0003` | `SupportedRinses` | `list`, 항목 `NumberOfRinsesEnum` | 읽기: `view` | `RINSE` | 최대 4개 |

제공된 스펙 XML에는 명령과 이벤트 정의가 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| 클러스터 도메인 | `Appliances` |
| 클러스터 코드 | `0x0053` |
| 매크로 이름 | `LAUNDRY_WASHER_CONTROLS_CLUSTER` |
| 클라이언트 | 활성화, `init="false"`, `tick="false"` |
| 서버 | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="2"` |

`NumberOfRinsesEnum`은 `enum8`로 정의되며, 값은 `None=0x0`, `Normal=0x1`, `Extra=0x2`, `Max=0x3`이다.

### 속성 매핑

모든 속성은 `side="server"`, `optional="true"`로 선언되어 있으며, 해당 기능의 `mandatoryConform` 조건을 함께 가진다.

| ID | 이름 | `define` | SDK 타입 및 설정 |
|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `SPIN_SPEEDS` | `array`, `entryType="char_string"`, `length="16"` |
| `0x0001` | `SpinSpeedCurrent` | `SPIN_SPEED_CURRENT` | `int8u`, `max="15"`, `writable="true"`, `isNullable="true"` |
| `0x0002` | `NumberOfRinses` | `NUMBER_OF_RINSES` | `NumberOfRinsesEnum`, `writable="true"` |
| `0x0003` | `SupportedRinses` | `SUPPORTED_RINSES` | `array`, `entryType="NumberOfRinsesEnum"`, `length="4"` |

`SPIN`과 `RINSE`의 기능 비트 및 선택 조건은 스펙 XML과 동일하다. 이 SDK XML에는 `SpinSpeeds` 항목 문자열의 최대 길이 64가 별도로 명시되어 있지 않다.

### 생성 정보

파일 주석은 Alchemy가 생성한 XML이며 직접 편집하지 말 것을 명시한다.

- 원본: `src/app_clusters/LaundryWasherControls.adoc`
- Git: `0.9-summer2026-111-g467a7f9e9`
- Alchemy: `v1.6.10`

## 구현

### 파일 구성

| 경로 | 역할 |
|---|---|
| `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp` | 서버 등록·해제, 엔드포인트 조회 및 속성 접근 래퍼 |
| `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h` | 엔드포인트 기반 공개 API 선언 |
| `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp` | 속성 읽기·쓰기, 값 검증 및 목록 인코딩 |
| `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h` | 클러스터 클래스, 구성, 상태 및 변경 알림 |
| `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h` | 애플리케이션별 목록 제공 및 변경 콜백 인터페이스 |
| `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h` | `CodegenIntegration.h` 포함 |

### 클러스터 구성과 상태

`chip::app::Clusters::LaundryWasherControlsCluster`는 `DefaultServerCluster`를 상속한다.

`Config`는 다음 구성을 지원한다.

- `BitFlags<LaundryWasherControls::Feature>`와 `LaundryWasherControls::Delegate &`를 함께 전달한다.
- 기능만 전달하고, 이후 `SetDelegate`로 `Delegate`를 설정한다.

두 생성자 모두 `VerifyOrDie(mFeatures.HasAny())`로 기능 비트가 하나 이상 설정되어 있는지 검사한다.

| 상수 또는 상태 | 정의 |
|---|---|
| `kMaxSpinSpeedLength` | `64` |
| `kMaxSpinSpeedsLength` | `16` |
| `kMaxSupportedRinsesLength` | `4` |
| `mSpinSpeedCurrent` | `DataModel::Nullable<uint8_t>`, `{}`로 초기화 |
| `mNumberOfRinses` | `LaundryWasherControls::NumberOfRinsesEnum::kNone`으로 초기화 |

### 속성 읽기·쓰기

`ReadAttribute`는 다음 값을 반환한다.

| 속성 | 처리 |
|---|---|
| `ClusterRevision` | `kRevision` 인코딩 |
| `FeatureMap` | `mFeatures` 인코딩 |
| `SpinSpeeds` | `ReadSpinSpeeds` 호출 |
| `SpinSpeedCurrent` | `mSpinSpeedCurrent` 인코딩 |
| `NumberOfRinses` | `mNumberOfRinses` 인코딩 |
| `SupportedRinses` | `ReadSupportedRinses` 호출 |

그 외 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`WriteAttribute`는 `SpinSpeedCurrent`와 `NumberOfRinses`만 처리한다. 값을 디코딩한 뒤 각각 `SetSpinSpeedCurrent`, `SetNumberOfRinses`를 호출하며, 그 외 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`로 `kMandatoryMetadata`와 기능별 속성을 결합한다.

- `Feature::kSpin`: `SpinSpeedCurrent`, `SpinSpeeds`
- `Feature::kRinse`: `NumberOfRinses`, `SupportedRinses`

### 값 검증과 변경 콜백

#### `SetSpinSpeedCurrent`

1. `Feature::kSpin`이 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
2. `SpinSpeedIndexValidity`로 값을 검증한다.
   - null이면 검증에 성공한다.
   - null이 아닌데 `mDelegate`가 없으면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
   - 값이 `kMaxSpinSpeedsLength` 이상이면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
   - `GetSpinSpeedAtIndex`가 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환하면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`로 변환한다.
   - 그 외에는 `GetSpinSpeedAtIndex`의 결과를 반환한다.
3. `SetAttributeValue`가 변경을 나타내고 `mDelegate`가 있으면 `OnSpinSpeedCurrentChanged`를 호출한다.

#### `SetNumberOfRinses`

1. `Feature::kRinse`가 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
2. `NumberOfRinsesValidity`로 값을 검증한다.
   - `mDelegate`가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환한다.
   - `GetSupportedRinseAtIndex`가 성공하는 동안 최대 `kMaxSupportedRinsesLength`개 항목을 검사한다.
   - 요청한 값과 일치하는 항목이 있으면 성공한다.
   - 일치하는 항목을 찾지 못하면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환한다.
3. `SetAttributeValue`가 변경을 나타내고 `mDelegate`가 있으면 `OnNumberOfRinsesChanged`를 호출한다.

### 목록 제공과 변경 알림

`ReadSpinSpeeds`와 `ReadSupportedRinses`는 `Delegate`를 통해 목록을 읽고 `EncodeList`로 인코딩한다.

- `mDelegate`가 없으면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
- 각각 최대 `kMaxSpinSpeedsLength`, `kMaxSupportedRinsesLength`개 항목을 읽는다.
- `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`는 정상적인 목록 종료로 처리한다.
- 그 외 조회 오류와 인코딩 오류는 전파한다.

`SetDelegate`는 포인터를 저장한 뒤 활성화된 기능에 따라 다음 변경 알림을 호출한다.

- `Feature::kSpin`: `NotifySpinSpeedsAttributeChanged`
- `Feature::kRinse`: `NotifySupportedRinsesAttributeChanged`

이 알림 함수들은 각각 `NotifyAttributeChanged`를 호출한다. `Delegate`가 목록의 어느 인덱스에서든 이전과 다른 값을 반환하게 되는 경우에도 해당 알림 함수를 호출하도록 주석에 명시되어 있다.

### `Delegate` 계약

네임스페이스: `chip::app::Clusters::LaundryWasherControls`

| 메서드 | 계약 |
|---|---|
| `GetSpinSpeedAtIndex` | 0부터 시작하는 인덱스로 문자열 조회. 성공 시 `MutableCharSpan`에 데이터를 복사하고 길이를 갱신해야 함 |
| `GetSupportedRinseAtIndex` | 0부터 시작하는 인덱스로 `NumberOfRinsesEnum` 조회 |
| `OnSpinSpeedCurrentChanged` | `SpinSpeedCurrent` 변경 콜백. 기본 구현은 빈 함수 |
| `OnNumberOfRinsesChanged` | `NumberOfRinses` 변경 콜백. 기본 구현은 빈 함수 |

두 조회 메서드는 순수 가상 함수이며, 목록 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환해야 한다.

`Delegate`는 클러스터가 파괴될 때까지 유효해야 한다. 재귀 호출 가능성을 피하기 위해 다음 호출을 하지 않도록 명시되어 있다.

- `OnSpinSpeedCurrentChanged` 안에서 클러스터의 `SetSpinSpeedCurrent` 호출
- `OnNumberOfRinsesChanged` 안에서 클러스터의 `SetNumberOfRinses` 호출

### Codegen 통합과 수명 주기

서버 인스턴스 저장소는 `LazyRegisteredServerCluster<LaundryWasherControlsCluster>` 배열인 `gServers`이다.

- `kLaundryWasherControlsFixedClusterCount`: `LaundryWasherControls::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kLaundryWasherControlsMaxClusterCount`: `kLaundryWasherControlsFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

| 메서드 | 동작 |
|---|---|
| `CreateRegistration` | `featureMap`으로 `BitFlags<Feature>`와 `LaundryWasherControlsCluster::Config`를 만들고 서버 인스턴스 생성 |
| `FindRegistration` | 인스턴스가 생성되지 않았으면 `nullptr`, 생성되었으면 클러스터 반환 |
| `ReleaseRegistration` | 서버 인스턴스의 `Destroy` 호출 |

주요 콜백은 다음과 같다.

- `MatterLaundryWasherControlsPluginServerInitCallback`: 빈 구현.
- `MatterLaundryWasherControlsClusterInitCallback`: `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap=true`, `fetchOptionalAttributes=false`로 설정한다.
- `MatterLaundryWasherControlsClusterShutdownCallback`: `shutdownType`을 전달하여 `CodegenClusterIntegration::UnregisterServer` 호출.
- `FindClusterOnEndpoint`: `CodegenClusterIntegration::FindClusterOnEndpoint`로 조회하고 `LaundryWasherControlsCluster *`로 반환.

### 엔드포인트 기반 API

네임스페이스: `chip::app::Clusters::LaundryWasherControls::LaundryWasherControlsServer`

| API | 동작 |
|---|---|
| `SetDelegate` | 엔드포인트의 클러스터에 `Delegate` 설정. 클러스터가 없으면 오류 로그 기록 |
| `SetDefaultDelegate` | 하위 호환용 API. `VerifyOrDie(delegate != nullptr)` 검사 후 `SetDelegate` 호출 |
| `SetSpinSpeedCurrent` | 클러스터의 `SetSpinSpeedCurrent` 호출 |
| `GetSpinSpeedCurrent` | 클러스터의 현재 `SpinSpeedCurrent`를 출력 인자에 복사 |
| `SetNumberOfRinses` | 클러스터의 `SetNumberOfRinses` 호출 |
| `GetNumberOfRinses` | 클러스터의 현재 `NumberOfRinses`를 출력 인자에 복사 |

네 개의 속성 접근 API는 클러스터를 찾지 못하면 `CHIP_ERROR_NOT_FOUND`를 반환한다. 두 getter는 복사에 성공하면 `CHIP_NO_ERROR`를 반환한다.

헤더 주석은 `SetDelegate`를 `Server::Init` 호출 이후에만 사용할 수 있다고 명시하며, `SetDefaultDelegate` 대신 `SetDelegate` 사용을 권장한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
