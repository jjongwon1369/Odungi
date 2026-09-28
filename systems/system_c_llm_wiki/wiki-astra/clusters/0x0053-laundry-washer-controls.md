---
entity: Laundry Washer Controls
ids: ['0x0053']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h', 'data_model/1.7/clusters/LaundryWasherControls.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Laundry Washer Controls

## 개요

Laundry Washer Controls는 세탁기와 같은 세탁 장치의 기능을 원격으로 모니터링하고 제어하는 클러스터이다. 여러 탈수 속도를 지원하는 `SPIN`과 여러 헹굼 주기를 지원하는 `RINSE`를 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0053` |
| 스펙 이름 | Laundry Washer Controls Cluster |
| revision | `2` |
| hierarchy | `base` |
| role | `application` |
| scope | `Endpoint` |
| picsCode | `WASHERCTRL` |

## 스펙

출처: `data_model/1.7/clusters/LaundryWasherControls.xml`

### 변경 이력

| revision | 내용 |
|---|---|
| `1` | 최초 정의 |
| `2` | Feature Map 적합성 조건 변경 |

### 기능

| bit | code | name | 설명 |
|---|---|---|---|
| `0` | `SPIN` | `Spin` | 여러 탈수 속도 지원 |
| `1` | `RINSE` | `Rinse` | 여러 헹굼 주기 지원 |

두 기능은 `choice="a"`, `more="true"`, `min="1"` 조건을 공유하므로, 하나 이상을 지원해야 한다.

### NumberOfRinsesEnum

각 항목은 `RINSE` 지원 시 필수이다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `None` | 헹굼 주기를 수행하지 않음 |
| `1` | `Normal` | 제조업체가 정한 일반 헹굼 주기 수행 |
| `2` | `Extra` | 추가 헹굼 주기 수행 |
| `3` | `Max` | 제조업체가 정한 최대 횟수의 헹굼 주기 수행 |

### 속성

모든 속성의 읽기 권한은 `view`이며, 쓰기 가능한 속성의 쓰기 권한은 `operate`이다.

| ID | 이름 | 스펙 타입 | 접근 | 필수 조건 | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `list`, 항목 `string` | 읽기 | `SPIN` | 최대 16개, 항목별 최대 길이 64 |
| `0x0001` | `SpinSpeedCurrent` | `uint8` | 읽기/쓰기 | `SPIN` | 최댓값 15, nullable |
| `0x0002` | `NumberOfRinses` | `NumberOfRinsesEnum` | 읽기/쓰기 | `RINSE` | 제공된 XML의 제약 설명은 비어 있음 |
| `0x0003` | `SupportedRinses` | `list`, 항목 `NumberOfRinsesEnum` | 읽기 | `RINSE` | 최대 4개 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml`

### 클러스터 구성

| 항목 | 정의 |
|---|---|
| configurator domain | `CHIP` |
| cluster domain | `Appliances` |
| name | Laundry Washer Controls |
| code | `0x0053` |
| define | `LAUNDRY_WASHER_CONTROLS_CLUSTER` |
| client / server | 모두 `true`, 각각 `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="2"`, `side="either"` |

이 XML은 Alchemy가 생성한 파일이며 직접 수정하지 않도록 명시되어 있다.

- 생성 원본: `src/app_clusters/LaundryWasherControls.adoc`
- Git: `0.9-summer2026-111-g467a7f9e9`
- Alchemy: `v1.6.10`

### 타입 및 속성 매핑

`NumberOfRinsesEnum`은 `enum8`로 정의되며, 항목은 `None=0x0`, `Normal=0x1`, `Extra=0x2`, `Max=0x3`이다.

| 이름 | define | SDK 타입 | 추가 정의 |
|---|---|---|---|
| `SpinSpeeds` | `SPIN_SPEEDS` | `array`, `entryType="char_string"` | `length="16"` |
| `SpinSpeedCurrent` | `SPIN_SPEED_CURRENT` | `int8u` | `max="15"`, `writable="true"`, `isNullable="true"` |
| `NumberOfRinses` | `NUMBER_OF_RINSES` | `NumberOfRinsesEnum` | `writable="true"` |
| `SupportedRinses` | `SUPPORTED_RINSES` | `array`, `entryType="NumberOfRinsesEnum"` | `length="4"` |

네 속성 모두 `side="server"`, `optional="true"`로 선언되지만, `mandatoryConform`에 따라 `SPIN` 또는 `RINSE` 지원 시 필수이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h` | `LaundryWasherControlsCluster`, `Config`, 속성 API 및 길이 제한 선언 |
| `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp` | 속성 읽기/쓰기, 값 검증, 목록 인코딩 구현 |
| `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h` | 애플리케이션별 `Delegate` 인터페이스 |
| `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h` | 엔드포인트별 API 선언 |
| `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp` | 클러스터 등록·해제·조회 및 API 전달 |
| `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h` | `CodegenIntegration.h` 포함 |

### LaundryWasherControlsCluster 구성

`chip::app::Clusters`의 `LaundryWasherControlsCluster`는 `DefaultServerCluster`를 상속한다. 생성 시 `endpointId`와 `LaundryWasherControls::Id`를 사용한다.

`Config`는 다음 구성을 지원한다.

- `BitFlags<LaundryWasherControls::Feature>`와 `LaundryWasherControls::Delegate &` 전달
- 기능만 전달하고 `mDelegate`를 `nullptr`로 초기화

두 생성자 모두 `VerifyOrDie(mFeatures.HasAny())`로 하나 이상의 기능 설정을 요구한다.

| 상수 또는 멤버 | 정의 |
|---|---|
| `kMaxSpinSpeedLength` | `64` |
| `kMaxSpinSpeedsLength` | `16` |
| `kMaxSupportedRinsesLength` | `4` |
| `mSpinSpeedCurrent` | `DataModel::Nullable<uint8_t>`, `{}`로 초기화 |
| `mNumberOfRinses` | `LaundryWasherControls::NumberOfRinsesEnum::kNone`으로 초기화 |

### 속성 접근

`ReadAttribute`는 다음 값을 반환한다.

- `ClusterRevision`: `kRevision`
- `FeatureMap`: `mFeatures`
- `SpinSpeeds`: `ReadSpinSpeeds`로 목록 인코딩
- `SpinSpeedCurrent`: `mSpinSpeedCurrent`
- `NumberOfRinses`: `mNumberOfRinses`
- `SupportedRinses`: `ReadSupportedRinses`로 목록 인코딩

그 외에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`WriteAttribute`는 `SpinSpeedCurrent`와 `NumberOfRinses`만 디코딩하여 각각 `SetSpinSpeedCurrent`와 `SetNumberOfRinses`에 전달한다. 다른 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`로 `kMandatoryMetadata`와 기능별 속성을 조합한다.

- `Feature::kSpin`: `SpinSpeedCurrent`, `SpinSpeeds`
- `Feature::kRinse`: `NumberOfRinses`, `SupportedRinses`

### 값 검증 및 변경 처리

#### SetSpinSpeedCurrent

1. `Feature::kSpin`이 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
2. `SpinSpeedIndexValidity`로 값을 검증한다.
   - null은 `CHIP_NO_ERROR`로 허용한다.
   - null이 아닌 경우 `mDelegate`가 없거나 값이 `kMaxSpinSpeedsLength` 이상이면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
   - `GetSpinSpeedAtIndex`가 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환하면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`로 변환한다.
   - 그 밖의 반환값은 그대로 전달한다.
3. `SetAttributeValue`로 값이 변경되고 `mDelegate`가 있으면 `OnSpinSpeedCurrentChanged`를 호출한다.

따라서 `Feature::kSpin`이 설정되어 있으면, `Delegate`가 없어도 null 설정은 검증을 통과한다.

#### SetNumberOfRinses

1. `Feature::kRinse`가 없으면 `CHIP_IM_GLOBAL_STATUS(UnsupportedAttribute)`를 반환한다.
2. `NumberOfRinsesValidity`로 값을 검증한다.
   - `mDelegate`가 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환한다.
   - `GetSupportedRinseAtIndex`가 성공하는 동안 최대 `kMaxSupportedRinsesLength`개를 검사한다.
   - 일치하는 값이 있으면 `CHIP_NO_ERROR`, 없으면 `CHIP_IM_GLOBAL_STATUS(InvalidInState)`를 반환한다.
3. `SetAttributeValue`로 값이 변경되고 `mDelegate`가 있으면 `OnNumberOfRinsesChanged`를 호출한다.

### 목록 읽기

| 함수 | 데이터 제공 함수 | 최대 항목 수 |
|---|---|---|
| `ReadSpinSpeeds` | `GetSpinSpeedAtIndex` | `kMaxSpinSpeedsLength` |
| `ReadSupportedRinses` | `GetSupportedRinseAtIndex` | `kMaxSupportedRinsesLength` |

두 함수 모두 다음과 같이 동작한다.

- `mDelegate`가 없으면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
- 인덱스 `0`부터 항목을 읽어 `EncodeList`로 인코딩한다.
- `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`는 목록의 정상 종료로 처리한다.
- 그 외 조회 오류와 인코딩 오류는 반환한다.

`ReadSpinSpeeds`는 각 항목을 읽을 때 `kMaxSpinSpeedLength` 크기의 버퍼를 사용한다.

### Delegate 계약

`chip::app::Clusters::LaundryWasherControls`의 `Delegate`는 다음 메서드를 정의한다.

| 메서드 | 계약 |
|---|---|
| `GetSpinSpeedAtIndex` | 0부터 시작하는 인덱스의 문자열을 `MutableCharSpan`에 복사하고, 성공 시 복사한 데이터 길이로 갱신해야 함 |
| `GetSupportedRinseAtIndex` | 0부터 시작하는 인덱스의 `NumberOfRinsesEnum` 값을 반환 |
| `OnSpinSpeedCurrentChanged` | `SpinSpeedCurrent` 변경 콜백, 기본 구현은 비어 있음 |
| `OnNumberOfRinsesChanged` | `NumberOfRinses` 변경 콜백, 기본 구현은 비어 있음 |

두 조회 메서드는 순수 가상 함수이며, 목록 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환해야 한다.

무한 재귀 가능성을 피하기 위해 다음 호출을 하지 않아야 한다.

- `OnSpinSpeedCurrentChanged` 내부에서 클러스터의 `SetSpinSpeedCurrent` 호출
- `OnNumberOfRinsesChanged` 내부에서 클러스터의 `SetNumberOfRinses` 호출

`Delegate`는 클러스터가 소멸할 때까지 유효해야 한다.

### 목록 변경 알림

`LaundryWasherControlsCluster::SetDelegate`는 `mDelegate`를 교체한 뒤, 지원하는 기능에 따라 다음 알림을 호출한다.

- `Feature::kSpin`: `NotifySpinSpeedsAttributeChanged`
- `Feature::kRinse`: `NotifySupportedRinsesAttributeChanged`

각 알림은 `NotifyAttributeChanged`에 해당 속성 ID를 전달한다. `Delegate`가 목록의 어느 인덱스에서든 이전과 다른 값을 반환하게 될 때 해당 알림을 호출하도록 명시되어 있다.

### Codegen 통합 및 수명주기

`CodegenIntegration.cpp`는 다음 크기로 `gServers`를 구성한다.

- `kLaundryWasherControlsFixedClusterCount`: `LaundryWasherControls::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kLaundryWasherControlsMaxClusterCount`: `kLaundryWasherControlsFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- 저장 타입: `LazyRegisteredServerCluster<LaundryWasherControlsCluster>`

`IntegrationDelegate`는 다음을 수행한다.

- `CreateRegistration`: `featureMap`으로 `Config`를 만들고 `Delegate` 없이 클러스터 생성
- `FindRegistration`: 생성된 클러스터 반환, 미생성 상태이면 `nullptr` 반환
- `ReleaseRegistration`: 해당 인스턴스의 `Destroy` 호출

| 함수 | 동작 |
|---|---|
| `MatterLaundryWasherControlsPluginServerInitCallback` | 비어 있는 구현 |
| `MatterLaundryWasherControlsClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterLaundryWasherControlsClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | `CodegenClusterIntegration::FindClusterOnEndpoint`로 조회 후 `LaundryWasherControlsCluster *`로 반환 |

등록 시 `fetchFeatureMap`은 `true`, `fetchOptionalAttributes`는 `false`이다.

### 엔드포인트별 API

다음 API는 `chip::app::Clusters::LaundryWasherControls::LaundryWasherControlsServer`에 정의된다.

| API | 동작 |
|---|---|
| `SetDelegate` | 엔드포인트의 클러스터에 `Delegate` 설정. 클러스터가 없으면 오류 로그 기록 |
| `SetDefaultDelegate` | 하위 호환 API. `VerifyOrDie(delegate != nullptr)` 검사 후 `SetDelegate` 호출 |
| `SetSpinSpeedCurrent` | 클러스터의 `SetSpinSpeedCurrent` 호출 |
| `GetSpinSpeedCurrent` | 클러스터의 `GetSpinSpeedCurrent` 결과를 출력 인수에 저장 |
| `SetNumberOfRinses` | 클러스터의 `SetNumberOfRinses` 호출 |
| `GetNumberOfRinses` | 클러스터의 `GetNumberOfRinses` 결과를 출력 인수에 저장 |

- 엔드포인트별 `SetDelegate`는 `Server::Init` 호출 이후에만 호출할 수 있다.
- `SetDefaultDelegate` 대신 `SetDelegate` 사용이 권장된다.
- 네 속성 설정·조회 API는 클러스터를 찾지 못하면 `CHIP_ERROR_NOT_FOUND`를 반환한다.
- 두 조회 API는 정상적으로 값을 저장하면 `CHIP_NO_ERROR`를 반환한다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
