---
entity: Laundry Dryer Controls
ids: ['0x004A']
source_paths: ['data_model/1.7/clusters/LaundryDryerControls.xml', 'src/app/clusters/laundry-dryer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-dryer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-dryer-controls-server/LaundryDryerControlsCluster.cpp', 'src/app/clusters/laundry-dryer-controls-server/LaundryDryerControlsCluster.h', 'src/app/clusters/laundry-dryer-controls-server/laundry-dryer-controls-delegate.h', 'src/app/clusters/laundry-dryer-controls-server/laundry-dryer-controls-server.h', 'src/app/zap-templates/zcl/data-model/chip/laundry-dryer-controls-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Laundry Dryer Controls

## 개요

`Laundry Dryer Controls`는 건조기 장치의 동작과 관련된 옵션에 접근하는 클러스터이다. 지원하는 건조 수준을 `SupportedDrynessLevels`로 제공하고, 선택한 건조 수준을 `SelectedDrynessLevel`로 관리한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x004A` |
| 스펙 이름 | `Laundry Dryer Controls Cluster` |
| 리비전 | `1` |
| PICS 코드 | `DRYERCTRL` |
| 계층 / 역할 / 범위 | `base` / `application` / `Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/LaundryDryerControls.xml`

### 리비전

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 리비전 (`Initial revision`) |

### DrynessLevelEnum

모든 항목은 필수이다.

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Low` | 선택한 모드에서 낮은 건조 수준 |
| `1` | `Normal` | 선택한 모드에서 일반적인 건조 수준 |
| `2` | `Extra` | 선택한 모드에서 추가적인 건조 수준 |
| `3` | `Max` | 선택한 모드에서 최대 건조 수준 |

### 속성

| ID | 이름 | 타입 | 필수 여부 | 접근 권한 | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedDrynessLevels` | `list`, 항목 타입 `DrynessLevelEnum` | 필수 | 읽기: `view` | 항목 수 `1`~`4` |
| `0x0001` | `SelectedDrynessLevel` | `DrynessLevelEnum` | 필수 | 읽기: `view`, 쓰기: `operate` | `nullable="true"` |

`SelectedDrynessLevel`의 스펙 XML에는 빈 `<desc/>` 제약 요소가 있으며, 구체적인 제약 설명은 제공되지 않는다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/laundry-dryer-controls-cluster.xml`

### 클러스터 메타데이터

| 항목 | 정의 |
|---|---|
| 설정 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| 이름 | `Laundry Dryer Controls` |
| 코드 | `0x004A` |
| 매크로 식별자 | `LAUNDRY_DRYER_CONTROLS_CLUSTER` |
| `client` | `true`, `init="false"`, `tick="false"` |
| `server` | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="1"` |

### 열거형 및 속성 매핑

`DrynessLevelEnum`은 `enum8`이며, 값은 `Low=0x0`, `Normal=0x1`, `Extra=0x2`, `Max=0x3`이다.

| 코드 | 이름 | `define` | SDK 정의 |
|---|---|---|---|
| `0x0000` | `SupportedDrynessLevels` | `SUPPORTED_DRYNESS_LEVELS` | `side="server"`, `type="array"`, `entryType="DrynessLevelEnum"`, `length="4"`, `minLength="1"` |
| `0x0001` | `SelectedDrynessLevel` | `SELECTED_DRYNESS_LEVEL` | `side="server"`, `type="DrynessLevelEnum"`, `writable="true"`, `isNullable="true"`, `min="0x00"`, `max="0x03"` |

이 XML에는 Alchemy가 생성한 파일이므로 직접 편집하지 말라는 주석이 있다. 생성 원본 경로는 `src/app_clusters/LaundryDryerControls.adoc`이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/laundry-dryer-controls-server/LaundryDryerControlsCluster.h` | `LaundryDryerControlsCluster` 선언 |
| `src/app/clusters/laundry-dryer-controls-server/LaundryDryerControlsCluster.cpp` | 속성 접근, 검증, 영속화 구현 |
| `src/app/clusters/laundry-dryer-controls-server/laundry-dryer-controls-delegate.h` | 애플리케이션별 `Delegate` 인터페이스 |
| `src/app/clusters/laundry-dryer-controls-server/CodegenIntegration.h` | 코드 생성 통합 API 선언 |
| `src/app/clusters/laundry-dryer-controls-server/CodegenIntegration.cpp` | 클러스터 등록·해제 및 delegate 연결 |
| `src/app/clusters/laundry-dryer-controls-server/laundry-dryer-controls-server.h` | `app/clusters/laundry-dryer-controls-server/CodegenIntegration.h`를 포함하는 헤더 |

### LaundryDryerControlsCluster

`chip::app::Clusters`의 `LaundryDryerControlsCluster`는 `DefaultServerCluster`를 상속한다.

- 생성자는 `EndpointId endpointId`와 `LaundryDryerControls::Delegate & delegate`를 받는다.
- 호출자는 클러스터 인스턴스가 존재하는 동안 delegate의 수명을 보장해야 한다.
- 선택값은 `DataModel::Nullable<LaundryDryerControls::DrynessLevelEnum>` 타입의 `mSelectedDrynessLevel`에 보관한다.
- `Attributes`는 `LaundryDryerControls::Attributes::kMandatoryMetadata`를 사용하며, 선택적 속성은 추가하지 않는다.

### Delegate와 지원 수준 조회

`chip::app::Clusters::LaundryDryerControls`의 `Delegate`는 다음 순수 가상 함수를 제공한다.

```cpp
virtual CHIP_ERROR GetSupportedDrynessLevelAtIndex(size_t index, DrynessLevelEnum & supportedDryness) = 0;
```

- `index`는 `0`부터 시작한다.
- 목록 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.
- `EncodeSupportedDrynessLevels`는 delegate에서 항목을 순서대로 받아 인코딩한다.
  - `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`이면 정상적으로 목록을 종료한다.
  - 그 외 오류는 반환한다.
- `IsSupportedDrynessLevel`은 목록을 순회하여 값의 포함 여부를 확인한다. 일치 항목을 찾기 전에 오류가 발생하거나 목록이 끝나면 `false`를 반환한다.

### 속성 읽기와 쓰기

| 함수 | 처리 |
|---|---|
| `ReadAttribute` | `ClusterRevision`은 `LaundryDryerControls::kRevision`, `FeatureMap`은 `0`, `SupportedDrynessLevels`는 delegate 목록, `SelectedDrynessLevel`은 현재 저장값을 인코딩 |
| `WriteAttribute` | `SelectedDrynessLevel`을 nullable 값으로 디코딩한 뒤 `SetSelectedDrynessLevel` 호출 |
| `GetSelectedDrynessLevel` | 현재 `mSelectedDrynessLevel` 반환 |

각 읽기·쓰기 분기에서 처리하지 않는 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`SetSelectedDrynessLevel`의 동작은 다음과 같다.

1. `null`은 선택 해제로 처리하며 항상 유효하다.
2. 비-null 값은 `IsSupportedDrynessLevel` 검증을 통과해야 한다. 실패하면 `Status::ConstraintError`를 반환한다.
3. `SetAttributeValue`를 사용하여 실제 값이 변경된 경우에만 갱신하고 변경을 알린다.
4. 값이 변경되고 `mContext != nullptr`이면 영속화를 시도한다.
5. 영속화 실패는 로그로 남기며, 반환값은 `Status::Success`이다.

### 영속화와 Startup

`Startup`은 `DefaultServerCluster::Startup` 성공 후 `LoadPersistentAttributes`를 호출한다.

- `SelectedDrynessLevel`은 `AttributePersistence`의 `StoreNativeEndianValue`와 `LoadNativeEndianValue`로 저장·복원한다.
- 저장 경로는 endpoint, `LaundryDryerControls::Id`, `SelectedDrynessLevel::Id`로 구성한 `ConcreteAttributePath`이다.
- `Startup` 이전의 설정은 메모리 값만 갱신한다.
- 복원 시 현재 메모리 값을 기본값으로 사용한다. 저장값이 없으면 시작 전 설정값을 유지하고, 저장값이 있으면 해당 값으로 대체한다.
- 복원 실패 시 기본값을 유지하고 로그를 남긴다.

### 코드 생성 통합과 수명주기

`CodegenIntegration.cpp`는 `gClusters`에 `IntegrationDelegateWrapper`와 `LazyRegisteredServerCluster<LaundryDryerControlsCluster>`를 함께 보관한다.

- `kLaundryDryerControlsFixedClusterCount`는 `LaundryDryerControls::StaticApplicationConfig::kFixedClusterConfig.size()`이다.
- `kLaundryDryerControlsMaxClusterCount`는 고정 개수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `static_assert`로 고정 개수와 `MATTER_DM_LAUNDRY_DRYER_CONTROLS_CLUSTER_SERVER_ENDPOINT_COUNT`의 일치 여부 및 최대 개수 제한을 확인한다.

| 함수 | 동작 |
|---|---|
| `MatterLaundryDryerControlsPluginServerInitCallback` | 빈 구현 |
| `MatterLaundryDryerControlsClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false` |
| `MatterLaundryDryerControlsClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer`에 `shutdownType` 전달 |
| `FindClusterOnEndpoint` | 코드 생성 통합 계층에서 클러스터를 조회하여 `LaundryDryerControlsCluster *` 반환 |

`IntegrationDelegate`는 `CreateRegistration`에서 서버를 생성하고, `FindRegistration`에서 생성된 서버를 조회하며, `ReleaseRegistration`에서 서버를 파괴한다.

### delegate 등록 및 호환 API

`LaundryDryerControlsServer`는 다음 API를 제공한다.

| API | 동작 및 조건 |
|---|---|
| `SetDelegate` | `emberAfGetClusterServerEndpointIndex`로 endpoint의 슬롯을 찾아 delegate 연결 |
| `SetDefaultDelegate` | 하위 호환 API. `SetDelegate` 사용을 권장하며, `VerifyOrDie`로 `nullptr`를 거부 |
| `SetSelectedDrynessLevel` | 클러스터 조회 후 `DataModel::MakeNullable`로 변환한 값을 클래스의 setter에 전달 |
| `GetSelectedDrynessLevel` | 클러스터 조회 후 nullable 선택값을 출력 인자에 대입 |

- `SetDelegate`는 클러스터 생성 전후 모두 호출할 수 있다.
- 등록한 delegate는 endpoint의 클러스터가 파괴될 때까지 유효해야 한다.
- `SetDelegate`에서 유효한 슬롯을 찾지 못하면 오류를 기록하고 반환한다.
- `SetSelectedDrynessLevel`과 `GetSelectedDrynessLevel`은 클러스터를 찾지 못하면 `Status::Failure`를 반환한다.
- 통합 계층의 `SetSelectedDrynessLevel`은 `DrynessLevelEnum`을 받으며, 클래스의 setter는 nullable 값을 받는다.

### delegate 미등록 시 동작

`IntegrationDelegateWrapper`에 실제 delegate가 없으면 `GetSupportedDrynessLevelAtIndex`는 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.

따라서 `SupportedDrynessLevels`는 빈 목록으로 읽히며, 비-null `SelectedDrynessLevel` 설정은 모두 `ConstraintError`로 실패한다. 이 빈 목록 동작은 스펙의 항목 수 제약 `1`~`4`와 구분해야 한다.

## 관련 페이지

**사용 기기**

- [Laundry Dryer](../device-types/laundry-dryer.md)
