---
entity: Laundry Washer Controls
ids: ['0x0053']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h', 'src/app/clusters/laundry-washer-controls-server/CodegenIntegration.cpp', 'src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp', 'src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h', 'data_model/1.7/clusters/LaundryWasherControls.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
---

## 개요

Laundry Washer Controls 클러스터는 세탁기 등의 세탁 기기에서 제공하는 다양한 제어 기능(예: 탈수 속도 제어, 헹굼 횟수 설정 등)을 원격으로 모니터링하고 제어할 수 있도록 지원합니다.

* **클러스터 ID:** `0x0053`
* **도메인:** `Appliances` / `CHIP`
* **PICS 코드:** `WASHERCTRL`
* **범위(Scope):** `Endpoint`

---

## 스펙

### 피처 (Features)

| 비트 | 코드 | 이름 (Name) | 설명 (Summary) | 적합성 (Conformance) |
|---|---|---|---|---|
| 0 | `SPIN` | Spin | 다중 탈수 속도 지원 | `optionalConform choice="a" more="true" min="1"` |
| 1 | `RINSE` | Rinse | 다중 헹굼 사이클 지원 | `optionalConform choice="a" more="true" min="1"` |

### 데이터 타입 (Data Types)

#### NumberOfRinsesEnum
`enum8` 기반의 열거형 타입으로, 헹굼 주기의 설정을 나타냅니다.

| 값 (Value) | 이름 (Name) | 설명 (Summary) | 적합성 (Conformance) |
|---|---|---|---|
| `0x0` / `0` | `None` | 헹굼 사이클을 수행하지 않음 | `RINSE` 피처 활성 시 필수 |
| `0x1` / `1` | `Normal` | 제조사가 정의한 일반적인 헹굼 사이클을 수행함 | `RINSE` 피처 활성 시 필수 |
| `0x2` / `2` | `Extra` | 추가 헹굼 사이클을 한 번 더 수행함 | `RINSE` 피처 활성 시 필수 |
| `0x3` / `3` | `Max` | 제조사가 정의한 최대 횟수의 헹굼 사이클을 수행함 | `RINSE` 피처 활성 시 필수 |

### 속성 (Attributes)

| ID | 이름 (Name) | 타입 (Type) | 제약 조건 (Constraint) | 품질 (Quality) | 권한 (Access) | 적합성 (Conformance) |
|---|---|---|---|---|---|---|
| `0x0000` | `SpinSpeeds` | `list` [ `string` ] | maxCount: 16, maxLength: 64 | - | Read (View) | `SPIN` 피처 필수 |
| `0x0001` | `SpinSpeedCurrent` | `uint8` | max: 15 | Nullable | Read (View), Write (Operate) | `SPIN` 피처 필수 |
| `0x0002` | `NumberOfRinses` | `NumberOfRinsesEnum` | - | - | Read (View), Write (Operate) | `RINSE` 피처 필수 |
| `0x0003` | `SupportedRinses` | `list` [ `NumberOfRinsesEnum` ] | maxCount: 4 | - | Read (View) | `RINSE` 피처 필수 |

---

## SDK 정의

### ZCL XML 정의
`src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml` 파일 내의 정의는 다음과 같습니다.

* **정의 매크로:** `LAUNDRY_WASHER_CONTROLS_CLUSTER`
* **글로벌 속성:** `0xFFFD` (ClusterRevision, 기본값 2)

---

## 구현

### 서버 클래스 (`LaundryWasherControlsCluster`)
`src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.h`에 선언된 서버 구현체입니다.

```cpp
namespace chip::app::Clusters {

class LaundryWasherControlsCluster : public DefaultServerCluster
{
    constexpr static uint8_t kMaxSpinSpeedLength       = 64;
    constexpr static uint8_t kMaxSpinSpeedsLength      = 16;
    constexpr static uint8_t kMaxSupportedRinsesLength = 4;

public:
    struct Config
    {
        Config(BitFlags<LaundryWasherControls::Feature> features, LaundryWasherControls::Delegate & delegate);
        explicit Config(BitFlags<LaundryWasherControls::Feature> features);

        BitFlags<LaundryWasherControls::Feature> GetFeatures() const;
        LaundryWasherControls::Delegate * GetDelegate() const;
    };

    LaundryWasherControlsCluster(EndpointId endpointId, const Config & config);

    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request, AttributeValueEncoder & encoder) override;
    DataModel::ActionReturnStatus WriteAttribute(const DataModel::WriteAttributeRequest & request, AttributeValueDecoder & decoder) override;
    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

    void SetDelegate(LaundryWasherControls::Delegate & delegate);
    CHIP_ERROR SetSpinSpeedCurrent(DataModel::Nullable<uint8_t> spinSpeedCurrent);
    CHIP_ERROR SetNumberOfRinses(LaundryWasherControls::NumberOfRinsesEnum numberOfRinses);
    DataModel::Nullable<uint8_t> GetSpinSpeedCurrent() const;
    LaundryWasherControls::NumberOfRinsesEnum GetNumberOfRinses() const;

    void NotifySpinSpeedsAttributeChanged();
    void NotifySupportedRinsesAttributeChanged();
};

} // namespace chip::app::Clusters
```

### 델리게이트 인터페이스 (`Delegate`)
`src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-delegate.h`에 정의되어 있으며, 디바이스의 특정 세탁 세부 로직을 연결할 때 사용합니다.

```cpp
namespace chip::app::Clusters::LaundryWasherControls {

class Delegate
{
public:
    virtual ~Delegate() = default;

    // 인덱스 기반 스핀 속도 문자열 취득
    virtual CHIP_ERROR GetSpinSpeedAtIndex(size_t index, MutableCharSpan & spinSpeed) = 0;

    // 인덱스 기반 지원 헹굼 모드 취득
    virtual CHIP_ERROR GetSupportedRinseAtIndex(size_t index, NumberOfRinsesEnum & supportedRinse) = 0;

    // 속성 값 변경 시 콜백
    virtual void OnSpinSpeedCurrentChanged(DataModel::Nullable<uint8_t> spinSpeedCurrent) {}
    virtual void OnNumberOfRinsesChanged(NumberOfRinsesEnum numberOfRinses) {}
};

} // namespace chip::app::Clusters::LaundryWasherControls
```

### Codegen 및 통합 API (`CodegenIntegration`)
`src/app/clusters/laundry-washer-controls-server/CodegenIntegration.h`는 엔드포인트 단위로 대리자 등록 및 속성 관리를 위한 C 스타일 및 C++ 통합 API를 제공합니다.

```cpp
namespace chip::app::Clusters::LaundryWasherControls::LaundryWasherControlsServer {

void SetDelegate(EndpointId endpoint, Delegate & delegate);
void SetDefaultDelegate(EndpointId endpoint, Delegate * delegate); // 하위 호환성 유지용

CHIP_ERROR SetSpinSpeedCurrent(EndpointId endpointId, DataModel::Nullable<uint8_t> spinSpeedCurrent);
CHIP_ERROR GetSpinSpeedCurrent(EndpointId endpointId, DataModel::Nullable<uint8_t> & spinSpeedCurrent);

CHIP_ERROR SetNumberOfRinses(EndpointId endpointId, NumberOfRinsesEnum newNumberOfRinses);
CHIP_ERROR GetNumberOfRinses(EndpointId endpointId, NumberOfRinsesEnum & numberOfRinses);

} // namespace chip::app::Clusters::LaundryWasherControls::LaundryWasherControlsServer
```