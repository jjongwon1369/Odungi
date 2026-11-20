---
entity: User Label
ids: ['0x0041']
source_paths: ['data_model/1.7/clusters/UserLabel-Cluster.xml', 'src/app/clusters/user-label-server/CodegenIntegration.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.h', 'src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# User Label

## 개요

User Label은 엔드포인트에 0개 이상의 레이블을 지정하는 클러스터이다. `Label`을 기반으로 하며, `LabelList`를 통해 레이블 목록을 읽고 쓸 수 있다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `User Label` |
| 스펙 이름 | `User Label Cluster` |
| 클러스터 ID | `0x0041` |
| 리비전 | `1` |
| 기반 클러스터 | `Label` |
| 범위 | `Endpoint` |
| PICS 코드 | `ULABEL` |

## 스펙

출처: `data_model/1.7/clusters/UserLabel-Cluster.xml`

### 분류 및 리비전

- `hierarchy`: `derived`
- `baseCluster`: `Label`
- `role`: `utility`
- `scope`: `Endpoint`
- 리비전 `1`: `Initial revision`

### 속성

| ID | 이름 | 타입 | 항목 타입 | 기본값 | 필수 여부 | 읽기 권한 | 쓰기 권한 | 영속성 |
|---|---|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | `empty` | 필수 | `view` | `manage` | `nonVolatile` |

`LabelList`는 읽기와 쓰기를 모두 허용한다. 제공된 XML의 `constraint`에는 구체적인 제약 설명이 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml`

### 클러스터 정의

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `General` |
| 이름 | `User Label` |
| 코드 | `0x0041` |
| define | `USER_LABEL_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |

전역 속성 `0xFFFD`는 `side="either"`, `value="1"`로 정의된다.

### `LabelList`

| 항목 | 값 |
|---|---|
| code | `0x0000` |
| name | `LabelList` |
| define | `LABEL_LIST` |
| side | `server` |
| type | `array` |
| entryType | `LabelStruct` |
| writable | `true` |
| 쓰기 권한 | `manage` |

이 XML은 Alchemy로 생성되었으며, 원본 경로는 `src/data_model/UserLabel-Cluster.adoc`으로 표시되어 있다.

## 구현

### 클래스와 의존성

출처: `src/app/clusters/user-label-server/UserLabelCluster.h`

`chip::app::Clusters`의 `UserLabelCluster`는 다음을 상속한다.

- `DefaultServerCluster`
- `chip::FabricTable::Delegate`

`Context`는 다음 참조를 보유한다.

| 멤버 | 타입 | 용도 |
|---|---|---|
| `deviceInfoProvider` | `DeviceLayer::DeviceInfoProvider &` | 레이블 목록 조회·저장·추가·삭제 |
| `fabricTable` | `chip::FabricTable &` | Fabric delegate 등록 및 남은 Fabric 수 확인 |

생성자는 `DefaultServerCluster`에 `{ endpoint, UserLabel::Id }`를 전달한다.

레이블 항목의 크기 제한은 다음과 같다.

```cpp
static constexpr size_t kMaxLabelSize = 16;
static constexpr size_t kMaxValueSize = 16;
```

### 속성 읽기

출처: `src/app/clusters/user-label-server/UserLabelCluster.cpp`

`UserLabelCluster::ReadAttribute`는 다음과 같이 처리한다.

| 속성 | 처리 |
|---|---|
| `LabelList::Id` | `ReadLabelList` 호출 |
| `ClusterRevision::Id` | `UserLabel::kRevision` 인코딩 |
| `FeatureMap::Id` | `uint32_t` 값 `0` 인코딩 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

`ReadLabelList`는 `provider.IterateUserLabel(endpoint)`로 얻은 반복자를 `AutoRelease`로 관리한다. 반복자가 없으면 `encoder.EncodeEmptyList()`를 호출하고, 있으면 `Next`로 읽은 `UserLabel::Structs::LabelStruct::Type` 항목을 순서대로 인코딩한다.

### 속성 쓰기와 제약 검사

`UserLabelCluster::WriteAttribute`는 `LabelList::Id`에 대해서만 쓰기를 처리한다. `WriteLabelList`가 성공하면 `NotifyAttributeChangedIfSuccess`를 통해 속성 변경을 알린다. 다른 속성에는 `Protocols::InteractionModel::Status::UnsupportedWrite`를 반환한다.

`IsValidLabelEntry`는 다음 조건을 검사하며, 빈 `label`과 `value`도 허용한다.

- `entry.label.size() <= UserLabelCluster::kMaxLabelSize`
- `entry.value.size() <= UserLabelCluster::kMaxValueSize`

#### 전체 목록 쓰기

`path.IsListItemOperation()`이 거짓이면 다음 순서로 처리한다.

1. `LabelList::TypeInfo::DecodableType`으로 디코딩한다.
2. 각 항목에 `IsValidLabelEntry`를 적용한다.
3. 항목을 `DeviceLayer::kMaxUserLabelListLength` 크기의 배열에 수집한다.
4. 반복자의 상태를 확인한다.
5. `provider.SetUserLabelList(endpoint, Span(labels.data(), numLabels))`를 호출한다.

| 조건 | 반환 오류 |
|---|---|
| 항목의 크기 제약 위반 | `CHIP_IM_GLOBAL_STATUS(ConstraintError)` |
| 배열 용량 초과 | `CHIP_ERROR_NO_MEMORY` |

#### 항목 추가

`path.mListOp`가 `ConcreteDataAttributePath::ListOperation::AppendItem`이면 다음 순서로 처리한다.

1. `Structs::LabelStruct::DecodableType`으로 디코딩한다.
2. `IsValidLabelEntry`로 검사한다.
3. `provider.AppendUserLabel(endpoint, entry)`를 호출한다.

크기 제약 위반에는 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다. `AppendUserLabel`이 `CHIP_ERROR_NO_MEMORY`를 반환하면 `CHIP_IM_GLOBAL_STATUS(ResourceExhausted)`로 변환한다.

그 외 목록 항목 작업은 `CHIP_ERROR_UNSUPPORTED_CHIP_FEATURE`를 반환한다.

### 속성 메타데이터

`UserLabelCluster::Attributes`는 `AttributeListBuilder`를 사용하여 `UserLabel::Attributes::kMandatoryMetadata`를 추가한다. 추가 메타데이터 인수는 빈 목록이다.

### 생명주기와 Fabric 제거

- `UserLabelCluster::Startup`은 `DefaultServerCluster::Startup` 성공 후 `mContext.fabricTable.AddFabricDelegate(this)`를 호출한다.
- `UserLabelCluster::Shutdown`은 `RemoveFabricDelegate(this)` 호출 후 `DefaultServerCluster::Shutdown`을 호출한다.
- `UserLabelCluster::OnFabricRemoved`는 `mContext.fabricTable.FabricCount() == 0`일 때만 레이블 삭제를 수행한다.
  - `mContext.deviceInfoProvider.ClearUserLabelList(mPath.mEndpointId)`로 해당 엔드포인트의 목록을 삭제한다.
  - 삭제 실패 시 `ChipLogError`로 기록한다.

### 코드 생성 통합

출처: `src/app/clusters/user-label-server/CodegenIntegration.cpp`

서버 인스턴스 수와 저장소는 다음과 같이 정의된다.

- `kUserLabelFixedClusterCount`: `UserLabel::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kUserLabelMaxClusterCount`: `kUserLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: `LazyRegisteredServerCluster<UserLabelCluster>` 배열

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | `DeviceLayer::GetDeviceInfoProvider()`의 결과를 `VerifyOrDie`로 확인하고, 해당 provider와 `Server::GetInstance().GetFabricTable()`을 사용하여 인스턴스를 생성한 뒤 등록 정보를 반환 |
| `FindRegistration` | 인스턴스가 생성되어 있으면 클러스터를 반환하고, 아니면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

등록 및 해제 콜백은 다음과 같다.

- `MatterUserLabelClusterInitCallback`
  - `CodegenClusterIntegration::RegisterServer`를 호출한다.
  - 클러스터 ID로 `UserLabel::Id`를 사용한다.
  - `fetchFeatureMap`과 `fetchOptionalAttributes`를 모두 `false`로 지정한다.
- `MatterUserLabelClusterShutdownCallback`
  - `CodegenClusterIntegration::UnregisterServer`에 `shutdownType`을 전달한다.
- `MatterUserLabelPluginServerInitCallback`
  - 본문이 비어 있다.

## 관련 페이지

**베이스 클러스터**

- [Label](../base/label.md)

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md)
- [Cook Surface](../device-types/cook-surface.md)
- [Cooktop](../device-types/cooktop.md)
- [Dishwasher](../device-types/dishwasher.md)
- [Extractor Hood](../device-types/extractor-hood.md)
- [Humidity Conditioner](../device-types/humidity-conditioner.md)
- [Laundry Dryer](../device-types/laundry-dryer.md)
- [Laundry Washer](../device-types/laundry-washer.md)
- [Microwave Oven](../device-types/microwave-oven.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
- [Water Heater](../device-types/water-heater.md)
