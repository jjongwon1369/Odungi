---
entity: Laundry Washer Controls
ids: ['0x0053']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h', 'data_model/1.7/clusters/LaundryWasherControls.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Laundry Washer Controls

## 개요

`Laundry Washer Controls`는 세탁 장치에서 제공하는 다양한 기능을 원격으로 모니터링하고 제어하기 위한 클러스터입니다.

- Cluster ID: `0x0053`
- Define: `LAUNDRY_WASHER_CONTROLS_CLUSTER`
- Domain: `Appliances`
- 역할: Client 및 Server
- Scope: Endpoint
- PICS Code: `WASHERCTRL`

## 스펙

### 클러스터 정보

- Revision: `2`
- Revision history:
  - Revision `1`: `Initial revision`
  - Revision `2`: `Updated Feature Map Conformance`

### Features

| Bit | Code | Name | Summary |
|---:|---|---|---|
| 0 | `SPIN` | `Spin` | Multiple spin speeds supported |
| 1 | `RINSE` | `Rinse` | Multiple rinse cycles supported |

`SPIN` 및 `RINSE`는 각각 선택적 Feature이며, 선택된 Feature에 따라 관련 Attribute가 지원됩니다.

### Data type

#### `NumberOfRinsesEnum`

| 값 | 항목 | 설명 |
|---:|---|---|
| `0` | `None` | This laundry washer mode does not perform rinse cycles |
| `1` | `Normal` | This laundry washer mode performs normal rinse cycles determined by the manufacturer |
| `2` | `Extra` | This laundry washer mode performs an extra rinse cycle |
| `3` | `Max` | This laundry washer mode performs the maximum number of rinse cycles determined by the manufacturer |

모든 `NumberOfRinsesEnum` 항목은 `RINSE` Feature에 종속됩니다.

### Attributes

| ID | 이름 | 타입 | 접근 | 제약 및 조건 |
|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | list of string | Read | `SPIN` 필수, 최대 16개, 각 문자열 최대 64자 |
| `0x0001` | `SpinSpeedCurrent` | `uint8` | Read/Write | `SPIN` 필수, `nullable`, 최댓값 `15` |
| `0x0002` | `NumberOfRinses` | `NumberOfRinsesEnum` | Read/Write | `RINSE` 필수 |
| `0x0003` | `SupportedRinses` | list of `NumberOfRinsesEnum` | Read | `RINSE` 필수, 최대 4개 |

`SpinSpeedCurrent`의 Write 권한은 `operate`이며, 나머지 Read 권한은 `view`입니다.

## SDK 정의

### 생성 파일

경로: `src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml`

SDK에서 정의하는 주요 항목은 다음과 같습니다.

- `NumberOfRinsesEnum`
  - `None`: `0x0`
  - `Normal`: `0x1`
  - `Extra`: `0x2`
  - `Max`: `0x3`
- Cluster:
  - Name: `Laundry Washer Controls`
  - Code: `0x0053`
  - Define: `LAUNDRY_WASHER_CONTROLS_CLUSTER`
- Global Attribute:
  - `0xFFFD`
  - Revision: `2`

SDK Attribute 정의:

| Code | Name | Define | 타입 | 속성 |
|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `SPIN_SPEEDS` | `array` of `char_string` | Optional, length `16`, `SPIN` Feature |
| `0x0001` | `SpinSpeedCurrent` | `SPIN_SPEED_CURRENT` | `int8u` | Optional, writable, nullable, max `15`, `SPIN` Feature |
| `0x0002` | `NumberOfRinses` | `NUMBER_OF_RINSES` | `NumberOfRinsesEnum` | Optional, writable, `RINSE` Feature |
| `0x0003` | `SupportedRinses` | `SUPPORTED_RINSES` | `array` of `NumberOfRinsesEnum` | Optional, length `4`, `RINSE` Feature |

## 구현

### 구현 파일

- `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h`
- `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp`
- `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h`
- `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h`
- `src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp`
- `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h`

### `LaundryWasherControlsCluster`

`LaundryWasherControlsCluster`는 `DefaultServerCluster`를 상속합니다.

주요 내부 상수:

```cpp
kMaxSpinSpeedLength       = 64;
kMaxSpinSpeedsLength      = 16;
kMaxSupportedRinsesLength = 4;
```

#### `Config`

```cpp
Config(BitFlags<LaundryWasherControls::Feature> features, LaundryWasherControls::Delegate & delegate);
explicit Config(BitFlags<LaundryWasherControls::Feature> features);
```

- `features`에는 최소 하나의 Feature가 설정되어야 합니다.
- Feature가 하나도 설정되지 않으면 `VerifyOrDie`가 호출됩니다.
- `delegate` 없이 생성할 수 있지만, Spin speed 또는 Number of rinses 설정 시 delegate가 필요합니다.
- `GetFeatures()`는 설정된 Feature를 반환합니다.
- `GetDelegate()`는 설정된 `LaundryWasherControls::Delegate`를 반환합니다.

#### Attribute 처리

`ReadAttribute`는 다음 Attribute를 처리합니다.

- `ClusterRevision::Id`
- `FeatureMap::Id`
- `SpinSpeeds::Id`
- `SpinSpeedCurrent::Id`
- `NumberOfRinses::Id`
- `SupportedRinses::Id`

지원되지 않는 Attribute에는 `UnsupportedAttribute`를 반환합니다.

`WriteAttribute`는 다음 Attribute를 처리합니다.

- `SpinSpeedCurrent::Id`
- `NumberOfRinses::Id`

그 외 Attribute에 대한 Write는 `UnsupportedAttribute`를 반환합니다.

`Attributes`는 Feature에 따라 Optional Attribute를 구성합니다.

- `SPIN`이 활성화된 경우:
  - `SpinSpeedCurrent`
  - `SpinSpeeds`
- `RINSE`가 활성화된 경우:
  - `NumberOfRinses`
  - `SupportedRinses`

### 값 설정 및 검증

#### `SetSpinSpeedCurrent`

```cpp
CHIP_ERROR SetSpinSpeedCurrent(DataModel::Nullable<uint8_t> spinSpeedCurrent);
```

- `SPIN` Feature가 없으면 `UnsupportedAttribute`를 반환합니다.
- 값이 null이면 허용됩니다.
- 값이 null이 아니면 다음 조건을 검증합니다.
  - 값이 `kMaxSpinSpeedsLength`보다 작아야 합니다.
  - `mDelegate->GetSpinSpeedAtIndex()`에서 유효한 Spin speed를 반환해야 합니다.
- 유효하지 않은 값에는 `ConstraintError`를 반환합니다.
- 값이 변경되고 `mDelegate`가 설정되어 있으면 `OnSpinSpeedCurrentChanged`를 호출합니다.

#### `SetNumberOfRinses`

```cpp
CHIP_ERROR SetNumberOfRinses(LaundryWasherControls::NumberOfRinsesEnum numberOfRinses);
```

- `RINSE` Feature가 없으면 `UnsupportedAttribute`를 반환합니다.
- `mDelegate`가 제공하는 `SupportedRinses` 목록에 `numberOfRinses`가 포함되어야 합니다.
- 지원되지 않는 값에는 `InvalidInState`를 반환합니다.
- 값이 변경되고 `mDelegate`가 설정되어 있으면 `OnNumberOfRinsesChanged`를 호출합니다.

### Getter

```cpp
DataModel::Nullable<uint8_t> GetSpinSpeedCurrent() const;
LaundryWasherControls::NumberOfRinsesEnum GetNumberOfRinses() const;
```

### 변경 알림

```cpp
void NotifySpinSpeedsAttributeChanged();
void NotifySupportedRinsesAttributeChanged();
```

- `NotifySpinSpeedsAttributeChanged()`는 `SpinSpeeds` Attribute의 변경을 데이터 모델에 알립니다.
- `NotifySupportedRinsesAttributeChanged()`는 `SupportedRinses` Attribute의 변경을 데이터 모델에 알립니다.
- `SetDelegate` 호출 시 해당 Feature가 활성화되어 있으면 관련 알림이 자동으로 발생합니다.

### `Delegate`

경로: `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h`

애플리케이션별 로직은 `LaundryWasherControls::Delegate`를 구현하여 제공합니다.

필수 구현 메서드:

```cpp
virtual CHIP_ERROR GetSpinSpeedAtIndex(size_t index, MutableCharSpan & spinSpeed) = 0;
virtual CHIP_ERROR GetSupportedRinseAtIndex(size_t index, NumberOfRinsesEnum & supportedRinse) = 0;
```

- `GetSpinSpeedAtIndex`
  - `index` 위치의 Spin speed 문자열을 반환합니다.
  - 첫 번째 항목의 index는 `0`입니다.
  - 목록 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환해야 합니다.
  - 성공 시 `spinSpeed`의 길이를 복사된 데이터 길이로 갱신해야 합니다.
- `GetSupportedRinseAtIndex`
  - `index` 위치의 `NumberOfRinsesEnum` 값을 반환합니다.
  - 목록 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환해야 합니다.

선택적 callback:

```cpp
virtual void OnSpinSpeedCurrentChanged(DataModel::Nullable<uint8_t> spinSpeedCurrent) {}
virtual void OnNumberOfRinsesChanged(NumberOfRinsesEnum numberOfRinses) {}
```

callback 내부에서 각각 `SetSpinSpeedCurrent()` 또는 `SetNumberOfRinses()`를 호출하면 무한 재귀가 발생할 수 있습니다.

### Codegen 연동

`CodegenIntegration.cpp`는 `CodegenClusterIntegration`을 사용하여 Server cluster를 등록하고 해제합니다.

주요 함수:

```cpp
void MatterLaundryWasherControlsPluginServerInitCallback();
void MatterLaundryWasherControlsClusterInitCallback(EndpointId endpointId);
void MatterLaundryWasherControlsClusterShutdownCallback(
    EndpointId endpointId,
    MatterClusterShutdownType shutdownType);
```

`MatterLaundryWasherControlsClusterInitCallback`은 다음 설정으로 Server를 등록합니다.

- `clusterId`: `LaundryWasherControls::Id`
- `fetchFeatureMap`: `true`
- `fetchOptionalAttributes`: `false`
- 고정 Cluster 수: `LaundryWasherControls::StaticApplicationConfig::kFixedClusterConfig.size()`
- 최대 Cluster 수: 고정 Cluster 수 + `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`

### Server API

네임스페이스:

```cpp
chip::app::Clusters::LaundryWasherControls::LaundryWasherControlsServer
```

Delegate 설정:

```cpp
void SetDelegate(EndpointId endpoint, Delegate & delegate);
void SetDefaultDelegate(EndpointId endpoint, Delegate * delegate);
```

- `SetDefaultDelegate`는 이전 호환성을 위해 유지됩니다.
- `SetDefaultDelegate`의 `delegate`는 `nullptr`이면 안 됩니다.
- Delegate는 해당 Endpoint의 Cluster가 제거될 때까지 유효해야 합니다.
- `SetDelegate`는 `Server::Init` 이후에 호출할 수 있습니다.

Attribute API:

```cpp
CHIP_ERROR SetSpinSpeedCurrent(
    EndpointId endpointId,
    DataModel::Nullable<uint8_t> spinSpeedCurrent);

CHIP_ERROR GetSpinSpeedCurrent(
    EndpointId endpointId,
    DataModel::Nullable<uint8_t> & spinSpeedCurrent);

CHIP_ERROR SetNumberOfRinses(
    EndpointId endpointId,
    NumberOfRinsesEnum newNumberOfRinses);

CHIP_ERROR GetNumberOfRinses(
    EndpointId endpointId,
    NumberOfRinsesEnum & numberOfRinses);
```

Cluster 검색:

```cpp
LaundryWasherControlsCluster * FindClusterOnEndpoint(EndpointId endpoint);
```

Endpoint에서 Cluster를 찾지 못하면 Set API와 Get API는 `CHIP_ERROR_NOT_FOUND`를 반환합니다. `SetDelegate`는 오류를 로그로 기록합니다.

### 기본 상태

`LaundryWasherControlsCluster`의 초기 상태는 다음과 같습니다.

```cpp
mSpinSpeedCurrent = {};
mNumberOfRinses   = LaundryWasherControls::NumberOfRinsesEnum::kNone;
```

### 목록 읽기

`SpinSpeeds`와 `SupportedRinses`는 `Delegate`에서 목록을 순차적으로 읽어 List Attribute로 인코딩합니다.

- `SpinSpeeds`
  - 최대 `kMaxSpinSpeedsLength`개 항목을 읽습니다.
  - 각 문자열 버퍼 크기는 `kMaxSpinSpeedLength`입니다.
- `SupportedRinses`
  - 최대 `kMaxSupportedRinsesLength`개 항목을 읽습니다.
- `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`가 반환되면 목록의 끝으로 처리하고 성공합니다.
- 그 외 오류는 반환됩니다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
