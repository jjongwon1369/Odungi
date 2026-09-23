---
entity: Fixed Label
ids: ['0x0040']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml', 'src/app/clusters/fixed-label-server/FixedLabelCluster.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.h', 'src/app/clusters/fixed-label-server/CodegenIntegration.cpp', 'data_model/1.7/clusters/FixedLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Fixed Label

## 스펙

- 클러스터: `Fixed Label Cluster`
- 클러스터 ID: `0x0040`
- 클러스터 이름: `Fixed Label`
- revision: `1`
- classification:
  - hierarchy: `derived`
  - baseCluster: `Label`
  - role: `utility`
  - picsCode: `FLABEL`
  - scope: `Endpoint`
- revision history:
  - revision `1`: `Initial revision`

### 속성

| ID | 이름 | 타입 | 기본값 | 접근 권한 | 품질 | 적합성 |
|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `empty` | read: `true`, readPrivilege: `view` | `nonVolatile` | mandatory |

- `LabelList`의 entry type: `LabelStruct`

## SDK 정의

### 파일

`src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml`

### `LabelStruct`

- 클러스터 코드:
  - `0x0040`
  - `0x0041`
- 필드:
  - `fieldId="0"`: `Label`
    - type: `char_string`
    - length: `16`
  - `fieldId="1"`: `Value`
    - type: `char_string`
    - length: `16`

### 클러스터

- domain: `General`
- name: `Fixed Label`
- code: `0x0040`
- define: `FIXED_LABEL_CLUSTER`
- description: The Fixed Label Cluster provides a feature for the device to tag an endpoint with zero or more read only labels.
- client: `true`
- server: `true`
- global attribute:
  - code: `0xFFFD`
  - side: `either`
  - value: `1`
- attribute:
  - side: `server`
  - code: `0x0000`
  - name: `LabelList`
  - define: `LABEL_LIST`
  - type: `array`
  - entryType: `LabelStruct`

## 구현

### 파일

- `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp`
- `src/app/clusters/fixed-label-server/FixedLabelCluster.h`
- `src/app/clusters/fixed-label-server/CodegenIntegration.cpp`

### `FixedLabelCluster`

`FixedLabelCluster`는 `DefaultServerCluster`를 상속하며, `DeviceLayer::DeviceInfoProvider`를 통해 `LabelList`를 제공합니다.

```cpp
class FixedLabelCluster : public DefaultServerCluster
{
public:
    FixedLabelCluster(EndpointId endpoint, DeviceLayer::DeviceInfoProvider & deviceInfoProvider);

    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request,
                                                AttributeValueEncoder & encoder) override;
    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;

private:
    DeviceLayer::DeviceInfoProvider & mDeviceInfoProvider;
};
```

생성자는 `EndpointId endpoint`와 `DeviceLayer::DeviceInfoProvider & deviceInfoProvider`를 받으며, `DefaultServerCluster`를 `FixedLabel::Id`로 초기화합니다.

### `ReadLabelList`

`ReadLabelList`는 `provider.IterateFixedLabel(endpoint)`를 통해 `LabelStruct` 항목을 순회합니다.

- iterator가 null이면 `encoder.EncodeEmptyList()`를 반환합니다.
- iterator가 유효하면 각 `fixedlabel`을 인코딩합니다.
- 각 항목은 `FixedLabel::Structs::LabelStruct::Type`으로 처리됩니다.

### `FixedLabelCluster::ReadAttribute`

다음 속성을 처리합니다.

- `LabelList::Id`
  - `ReadLabelList`를 호출합니다.
- `ClusterRevision::Id`
  - `FixedLabel::kRevision`을 인코딩합니다.
- `FeatureMap::Id`
  - `uint32_t` 값 `0`을 인코딩합니다.
- 그 외 속성
  - `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환합니다.

### `FixedLabelCluster::Attributes`

`AttributeListBuilder`를 사용하여 `FixedLabel::Attributes::kMandatoryMetadata`를 추가합니다.

### Codegen 통합

`CodegenIntegration.cpp`는 `FixedLabelCluster`의 서버 클러스터 등록 및 해제를 담당합니다.

- 고정 클러스터 수:
  - `FixedLabel::StaticApplicationConfig::kFixedClusterConfig.size()`
- 최대 클러스터 수:
  - `kFixedLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- 서버 저장소:
  - `LazyRegisteredServerCluster<FixedLabelCluster> gServers[kFixedLabelMaxClusterCount]`

#### `IntegrationDelegate`

- `CreateRegistration`
  - `DeviceLayer::GetDeviceInfoProvider()`를 가져옵니다.
  - `gServers[clusterInstanceIndex].Create`를 호출합니다.
- `FindRegistration`
  - 구성된 서버 클러스터가 없으면 `nullptr`을 반환합니다.
- `ReleaseRegistration`
  - `gServers[clusterInstanceIndex].Destroy()`를 호출합니다.

#### 초기화 및 종료 콜백

- `MatterFixedLabelClusterInitCallback(EndpointId endpointId)`
  - `CodegenClusterIntegration::RegisterServer`를 호출합니다.
  - `clusterId`: `FixedLabel::Id`
  - `fetchFeatureMap`: `false`
  - `fetchOptionalAttributes`: `false`
- `MatterFixedLabelClusterShutdownCallback(EndpointId endpointId, MatterClusterShutdownType shutdownType)`
  - `CodegenClusterIntegration::UnregisterServer`를 호출합니다.
- `MatterFixedLabelPluginServerInitCallback()`
  - 빈 구현입니다.