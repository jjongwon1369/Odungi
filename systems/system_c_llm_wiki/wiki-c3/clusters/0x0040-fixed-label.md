---
entity: Fixed Label
ids: ['0x0040']
source_paths: ['data_model/1.7/clusters/FixedLabel-Cluster.xml', 'src/app/clusters/fixed-label-server/CodegenIntegration.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.h', 'src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Fixed Label

## 개요

Fixed Label은 장치의 엔드포인트에 0개 이상의 읽기 전용 라벨을 부여하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0040` |
| 스펙 이름 | `Fixed Label Cluster` |
| 클러스터 이름 | `Fixed Label` |
| 리비전 | `1` |
| 기반 클러스터 | `Label` |
| 적용 범위 | `Endpoint` |
| PICS 코드 | `FLABEL` |

## 스펙

출처: `data_model/1.7/clusters/FixedLabel-Cluster.xml`

### 분류 및 리비전

- `hierarchy`: `derived`
- `baseCluster`: `Label`
- `role`: `utility`
- `scope`: `Endpoint`
- 리비전 `1`: `Initial revision`

### 속성

| ID | 이름 | 타입 | 항목 타입 | 기본값 | 접근 | 영속성 | 적합성 |
|---|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | `empty` | 읽기, `readPrivilege="view"` | `nonVolatile` | `mandatoryConform` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 클러스터 도메인 | `General` |
| 이름 | `Fixed Label` |
| 코드 | `0x0040` |
| 정의 식별자 | `FIXED_LABEL_CLUSTER` |

`client`와 `server`는 모두 `true`이며, 각각 `init="false"`, `tick="false"`로 선언되어 있다.

### `LabelStruct`

`LabelStruct`는 클러스터 코드 `0x0040`과 `0x0041`에 연결되어 있다.

| `fieldId` | 이름 | 타입 | `length` |
|---|---|---|---|
| `0` | `Label` | `char_string` | `16` |
| `1` | `Value` | `char_string` | `16` |

### 속성 선언

| 코드 | 이름 | 정의 식별자 | 타입 | 항목 타입 | 대상 |
|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `LABEL_LIST` | `array` | `LabelStruct` | `server` |

전역 속성 `0xFFFD`는 `side="either"`, `value="1"`로 선언되어 있다.

## 구현

### `FixedLabelCluster`

출처: `src/app/clusters/fixed-label-server/FixedLabelCluster.h`  
출처: `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp`

`chip::app::Clusters`의 `FixedLabelCluster`는 `DefaultServerCluster`를 상속한다.

- 생성자는 `EndpointId endpoint`와 `DeviceLayer::DeviceInfoProvider & deviceInfoProvider`를 받는다.
- `DefaultServerCluster`를 `{ endpoint, FixedLabel::Id }`로 초기화한다.
- 제공자 참조를 `mDeviceInfoProvider`에 보관한다.
- `ReadAttribute`와 `Attributes`를 재정의한다.

### 속성 읽기

`FixedLabelCluster::ReadAttribute`는 `request.path.mAttributeId`에 따라 처리한다.

| 속성 식별자 | 처리 |
|---|---|
| `LabelList::Id` | `ReadLabelList(mPath.mEndpointId, encoder, mDeviceInfoProvider)` 호출 |
| `ClusterRevision::Id` | `FixedLabel::kRevision` 인코딩 |
| `FeatureMap::Id` | `encoder.Encode<uint32_t>(0)` 호출 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

`ReadLabelList`의 처리 흐름은 다음과 같다.

1. `provider.IterateFixedLabel(endpoint)`로 반복자를 얻고 `AutoRelease`로 관리한다.
2. `it.IsNull()`이면 `encoder.EncodeEmptyList()`를 반환한다.
3. 그 외에는 `encoder.EncodeList` 내부에서 `FixedLabel::Structs::LabelStruct::Type fixedlabel`을 사용한다.
4. `it->Next(fixedlabel)`이 성공하는 동안 `encod.Encode(fixedlabel)`로 각 항목을 인코딩한다.
5. 인코딩 오류는 `ReturnErrorOnFailure`로 반환하며, 반복을 완료하면 `CHIP_NO_ERROR`를 반환한다.

### 속성 목록

`FixedLabelCluster::Attributes`는 `AttributeListBuilder`를 생성하고 다음 호출로 속성 메타데이터를 추가한다.

```cpp
return listBuilder.Append(Span(FixedLabel::Attributes::kMandatoryMetadata), {});
```

### 서버 등록 및 해제

출처: `src/app/clusters/fixed-label-server/CodegenIntegration.cpp`

서버 인스턴스 저장소는 다음과 같이 구성된다.

```cpp
constexpr size_t kFixedLabelFixedClusterCount = FixedLabel::StaticApplicationConfig::kFixedClusterConfig.size();
constexpr size_t kFixedLabelMaxClusterCount   = kFixedLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT;

LazyRegisteredServerCluster<FixedLabelCluster> gServers[kFixedLabelMaxClusterCount];
```

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

| 메서드 | 동작 |
|---|---|
| `CreateRegistration` | `DeviceLayer::GetDeviceInfoProvider()`의 결과가 `nullptr`가 아닌지 `VerifyOrDie`로 확인하고, 해당 `gServers` 항목을 생성한 뒤 `Registration()` 반환 |
| `FindRegistration` | `IsConstructed()`가 거짓이면 `nullptr`, 그 외에는 `Cluster()`의 주소 반환 |
| `ReleaseRegistration` | 해당 `gServers` 항목의 `Destroy()` 호출 |

콜백별 동작은 다음과 같다.

- `MatterFixedLabelClusterInitCallback`
  - `CodegenClusterIntegration::RegisterServer`를 호출한다.
  - `clusterId`는 `FixedLabel::Id`이다.
  - `fixedClusterInstanceCount`와 `maxClusterInstanceCount`에 각각 `kFixedLabelFixedClusterCount`와 `kFixedLabelMaxClusterCount`를 전달한다.
  - `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`이다.
- `MatterFixedLabelClusterShutdownCallback`
  - `CodegenClusterIntegration::UnregisterServer`를 호출한다.
  - 엔드포인트, 클러스터 ID, 인스턴스 수 설정과 함께 `shutdownType`을 전달한다.
- `MatterFixedLabelPluginServerInitCallback`
  - 함수 본문이 비어 있다.

## 관련 페이지

**베이스 클러스터**

- [Label](../base/label.md)

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
