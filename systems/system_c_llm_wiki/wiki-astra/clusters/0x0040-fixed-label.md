---
entity: Fixed Label
ids: ['0x0040']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml', 'src/app/clusters/fixed-label-server/FixedLabelCluster.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.h', 'src/app/clusters/fixed-label-server/CodegenIntegration.cpp', 'data_model/1.7/clusters/FixedLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Fixed Label

## 개요

Fixed Label은 엔드포인트에 0개 이상의 읽기 전용 레이블을 부여하는 클러스터이다. 클러스터 ID는 `0x0040`이며, 레이블 목록은 `LabelList` 속성으로 제공된다.

## 스펙

출처: `data_model/1.7/clusters/FixedLabel-Cluster.xml`

### 클러스터 정의

| 항목 | 값 |
|---|---|
| 이름 | `Fixed Label Cluster` |
| 클러스터 ID / 이름 | `0x0040` / `Fixed Label` |
| revision | `1` |
| 개정 이력 | `1`: `Initial revision` |
| hierarchy | `derived` |
| baseCluster | `Label` |
| role | `utility` |
| picsCode | `FLABEL` |
| scope | `Endpoint` |

### 속성

| ID | 이름 | 타입 | 항목 타입 | 기본값 | 접근 | 영속성 | 적합성 |
|---|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | `empty` | 읽기, `readPrivilege="view"` | `nonVolatile` | 필수 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml`

이 파일은 Alchemy로 생성되었으며, 직접 수정하지 않도록 명시되어 있다. 원본 경로는 `src/data_model/FixedLabel-Cluster.adoc`이다.

### 클러스터 설정

| 항목 | 값 |
|---|---|
| configurator domain | `CHIP` |
| 클러스터 domain | `General` |
| name | `Fixed Label` |
| code | `0x0040` |
| define | `FIXED_LABEL_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `code="0xFFFD"`, `side="either"`, `value="1"` |

### LabelStruct

`LabelStruct`는 클러스터 코드 `0x0040`과 `0x0041`에 연결되어 있다.

| fieldId | 이름 | 타입 | length |
|---|---|---|---|
| `0` | `Label` | `char_string` | `16` |
| `1` | `Value` | `char_string` | `16` |

### LabelList

| 항목 | 값 |
|---|---|
| code | `0x0000` |
| name | `LabelList` |
| define | `LABEL_LIST` |
| side | `server` |
| type | `array` |
| entryType | `LabelStruct` |

## 구현

### FixedLabelCluster

출처:
- `src/app/clusters/fixed-label-server/FixedLabelCluster.h`
- `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp`

`chip::app::Clusters` 네임스페이스의 `FixedLabelCluster`는 `DefaultServerCluster`를 상속한다.

생성자는 `EndpointId endpoint`와 `DeviceLayer::DeviceInfoProvider & deviceInfoProvider`를 받는다. `DefaultServerCluster`를 `{ endpoint, FixedLabel::Id }`로 초기화하고, 공급자 참조를 `mDeviceInfoProvider`에 보관한다.

### 속성 읽기

`FixedLabelCluster::ReadAttribute`는 `request.path.mAttributeId`에 따라 처리한다.

| 분기 | 동작 |
|---|---|
| `LabelList::Id` | `ReadLabelList(mPath.mEndpointId, encoder, mDeviceInfoProvider)` 호출 |
| `ClusterRevision::Id` | `FixedLabel::kRevision` 인코딩 |
| `FeatureMap::Id` | `encoder.Encode<uint32_t>(0)` 호출 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

`ReadLabelList`의 처리 흐름은 다음과 같다.

1. `provider.IterateFixedLabel(endpoint)`로 반복자를 얻고 `AutoRelease`로 관리한다.
2. `it.IsNull()`이면 `encoder.EncodeEmptyList()`를 반환한다.
3. 그렇지 않으면 `encoder.EncodeList` 내부에서 `FixedLabel::Structs::LabelStruct::Type fixedlabel`을 사용한다.
4. `it->Next(fixedlabel)`이 반환하는 각 항목을 `encod.Encode(fixedlabel)`로 인코딩한다.
5. 인코딩 오류는 `ReturnErrorOnFailure`로 반환하며, 반복이 끝나면 `CHIP_NO_ERROR`를 반환한다.

### 속성 메타데이터

`FixedLabelCluster::Attributes`는 전달받은 `builder`로 `AttributeListBuilder`를 생성하고 다음 호출 결과를 반환한다.

```cpp
listBuilder.Append(Span(FixedLabel::Attributes::kMandatoryMetadata), {});
```

### 코드 생성 통합

출처: `src/app/clusters/fixed-label-server/CodegenIntegration.cpp`

클러스터 인스턴스 저장 공간은 다음 값으로 구성된다.

- `kFixedLabelFixedClusterCount`: `FixedLabel::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kFixedLabelMaxClusterCount`: `kFixedLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: 크기가 `kFixedLabelMaxClusterCount`인 `LazyRegisteredServerCluster<FixedLabelCluster>` 배열

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 상속한다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | `DeviceLayer::GetDeviceInfoProvider()`의 결과가 `nullptr`이 아닌지 `VerifyOrDie`로 확인한 뒤, 해당 `gServers` 항목을 생성하고 `Registration()` 반환 |
| `FindRegistration` | 해당 항목이 생성되지 않았으면 `nullptr`, 생성되었으면 `Cluster()`의 주소 반환 |
| `ReleaseRegistration` | 해당 항목의 `Destroy()` 호출 |

### 수명 주기 콜백

- `MatterFixedLabelClusterInitCallback`
  - `CodegenClusterIntegration::RegisterServer`로 등록한다.
  - `clusterId`는 `FixedLabel::Id`이다.
  - 인스턴스 수 설정에 `kFixedLabelFixedClusterCount`와 `kFixedLabelMaxClusterCount`를 사용한다.
  - `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`이다.
- `MatterFixedLabelClusterShutdownCallback`
  - `CodegenClusterIntegration::UnregisterServer`에 등록 식별 정보, `integrationDelegate`, `shutdownType`을 전달한다.
- `MatterFixedLabelPluginServerInitCallback`
  - 함수 본문이 비어 있다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
