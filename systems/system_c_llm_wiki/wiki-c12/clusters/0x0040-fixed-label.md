---
entity: Fixed Label
ids: ['0x0040']
source_paths: ['data_model/1.7/clusters/FixedLabel-Cluster.xml', 'src/app/clusters/fixed-label-server/CodegenIntegration.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.h', 'src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Fixed Label

## 개요

Fixed Label은 Endpoint에 0개 이상의 읽기 전용 레이블을 부여하는 클러스터이다.

- 클러스터 ID: `0x0040`
- 스펙 이름: `Fixed Label Cluster`
- 기본 클러스터: `Label`
- 리비전: `1`
- 레이블 목록 속성: `LabelList`
- 구현은 `DeviceLayer::DeviceInfoProvider`에서 Endpoint별 레이블을 읽는다.

## 스펙

출처: `data_model/1.7/clusters/FixedLabel-Cluster.xml`

### 클러스터 정의

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Fixed Label Cluster` |
| 클러스터 ID 및 이름 | `0x0040` / `Fixed Label` |
| `revision` | `1` |
| `hierarchy` | `derived` |
| `baseCluster` | `Label` |
| `role` | `utility` |
| `picsCode` | `FLABEL` |
| `scope` | `Endpoint` |

리비전 `1`의 이력은 `Initial revision`이다.

### 속성

| ID | 이름 | 타입 | 항목 타입 | 기본값 | 접근 | 영속성 | 적합성 |
|---|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | `empty` | 읽기, `readPrivilege="view"` | `nonVolatile` | 필수 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 도메인 | `General` |
| 이름 | `Fixed Label` |
| 코드 | `0x0040` |
| 정의 식별자 | `FIXED_LABEL_CLUSTER` |
| `client` | `true`, `init="false"`, `tick="false"` |
| `server` | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

### `LabelStruct`

`LabelStruct`는 클러스터 코드 `0x0040`과 `0x0041`에 연결되어 있다.

| `fieldId` | 이름 | 타입 | `length` |
|---|---|---|---|
| `0` | `Label` | `char_string` | `16` |
| `1` | `Value` | `char_string` | `16` |

### `LabelList`

| 항목 | 값 |
|---|---|
| `side` | `server` |
| `code` | `0x0000` |
| `name` | `LabelList` |
| `define` | `LABEL_LIST` |
| `type` | `array` |
| `entryType` | `LabelStruct` |

스펙의 `list` 속성은 SDK XML에서 `array`로 정의된다.

## 구현

### `FixedLabelCluster`

출처:

- `src/app/clusters/fixed-label-server/FixedLabelCluster.h`
- `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp`

`chip::app::Clusters`의 `FixedLabelCluster`는 `DefaultServerCluster`를 상속한다.

생성자는 `EndpointId endpoint`와 `DeviceLayer::DeviceInfoProvider & deviceInfoProvider`를 받는다. 기반 클래스는 `{ endpoint, FixedLabel::Id }`로 초기화하며, 공급자 참조는 `mDeviceInfoProvider`에 보관한다.

### 속성 읽기

`FixedLabelCluster::ReadAttribute`는 `request.path.mAttributeId`에 따라 처리한다.

| 속성 식별자 | 처리 |
|---|---|
| `LabelList::Id` | `ReadLabelList(mPath.mEndpointId, encoder, mDeviceInfoProvider)` 호출 |
| `ClusterRevision::Id` | `FixedLabel::kRevision` 인코딩 |
| `FeatureMap::Id` | `encoder.Encode<uint32_t>(0)` 호출 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

`ReadLabelList`의 처리 순서는 다음과 같다.

1. `provider.IterateFixedLabel(endpoint)`로 반복자를 얻고 `AutoRelease`로 관리한다.
2. `it.IsNull()`이면 `encoder.EncodeEmptyList()`를 반환한다.
3. 반복자가 있으면 `encoder.EncodeList`를 호출한다.
4. `it->Next(fixedlabel)`로 얻은 `FixedLabel::Structs::LabelStruct::Type` 항목을 `encod.Encode(fixedlabel)`로 인코딩한다.
5. 인코딩 오류는 `ReturnErrorOnFailure`로 반환하며, 정상 완료 시 `CHIP_NO_ERROR`를 반환한다.

### 속성 메타데이터

`FixedLabelCluster::Attributes`는 `AttributeListBuilder`를 생성하고 다음 호출로 필수 속성 메타데이터를 추가한다.

```cpp
listBuilder.Append(Span(FixedLabel::Attributes::kMandatoryMetadata), {});
```

### 등록 및 해제

출처: `src/app/clusters/fixed-label-server/CodegenIntegration.cpp`

서버 인스턴스 용량은 다음과 같이 구성된다.

- `kFixedLabelFixedClusterCount`: `FixedLabel::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kFixedLabelMaxClusterCount`: `kFixedLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: `LazyRegisteredServerCluster<FixedLabelCluster>` 배열이며 크기는 `kFixedLabelMaxClusterCount`

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

| 메서드 | 동작 |
|---|---|
| `CreateRegistration` | `DeviceLayer::GetDeviceInfoProvider()` 결과를 `VerifyOrDie`로 검사하고, 해당 `gServers` 항목을 생성한 뒤 `Registration()` 반환 |
| `FindRegistration` | `IsConstructed()`가 거짓이면 `nullptr`, 그렇지 않으면 `Cluster()`의 주소 반환 |
| `ReleaseRegistration` | 해당 `gServers` 항목의 `Destroy()` 호출 |

콜백별 동작은 다음과 같다.

- `MatterFixedLabelClusterInitCallback`
  - `CodegenClusterIntegration::RegisterServer`를 호출한다.
  - `clusterId`는 `FixedLabel::Id`이다.
  - `fixedClusterInstanceCount`와 `maxClusterInstanceCount`에 위 용량 값을 전달한다.
  - `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`이다.
- `MatterFixedLabelClusterShutdownCallback`
  - `CodegenClusterIntegration::UnregisterServer`를 호출한다.
  - Endpoint, 클러스터 ID, 인스턴스 용량과 `shutdownType`을 전달한다.
- `MatterFixedLabelPluginServerInitCallback`
  - 함수 본문이 비어 있다.

## 관련 페이지

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
