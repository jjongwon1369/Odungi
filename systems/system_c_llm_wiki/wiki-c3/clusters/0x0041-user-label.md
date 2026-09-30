---
entity: User Label
ids: ['0x0041']
source_paths: ['data_model/1.7/clusters/UserLabel-Cluster.xml', 'src/app/clusters/user-label-server/CodegenIntegration.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.h', 'src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# User Label

## 개요

User Label은 엔드포인트에 0개 이상의 레이블을 지정하는 클러스터이다. `Label`을 기반으로 하며, `LabelList`를 통해 레이블 목록을 읽고 쓸 수 있다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | User Label |
| 클러스터 ID | `0x0041` |
| 리비전 | `1` |
| 기반 클러스터 | `Label` |
| 범위 | `Endpoint` |
| PICS 코드 | `ULABEL` |

## 스펙

출처: `data_model/1.7/clusters/UserLabel-Cluster.xml`

### 분류

- XML 클러스터 이름: `User Label Cluster`
- `hierarchy`: `derived`
- `baseCluster`: `Label`
- `role`: `utility`
- `scope`: `Endpoint`
- 리비전 `1`: `Initial revision`

### 속성

| ID | 이름 | 타입 | 항목 타입 | 기본값 | 필수 여부 |
|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | `empty` | 필수 |

`LabelList`의 접근 및 저장 특성은 다음과 같다.

| 항목 | 값 |
|---|---|
| 읽기 | 허용, `readPrivilege="view"` |
| 쓰기 | 허용, `writePrivilege="manage"` |
| 영속성 | `persistence="nonVolatile"` |

제공된 XML의 `constraint`에는 구체적인 제약 설명이 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `General` |
| 이름 | User Label |
| 코드 | `0x0041` |
| 매크로 | `USER_LABEL_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

### 속성 정의

| 항목 | 값 |
|---|---|
| 이름 | `LabelList` |
| 코드 | `0x0000` |
| 매크로 | `LABEL_LIST` |
| 위치 | `server` |
| 타입 | `array` |
| 항목 타입 | `LabelStruct` |
| 쓰기 가능 여부 | `writable="true"` |
| 쓰기 권한 | `manage` |

이 XML은 Alchemy로 생성되었으며 `DO NOT EDIT`가 명시되어 있다. 생성 원본은 `src/data_model/UserLabel-Cluster.adoc`이다.

## 구현

### 클래스와 의존성

출처: `src/app/clusters/user-label-server/UserLabelCluster.h`

`chip::app::Clusters`의 `UserLabelCluster`는 다음을 상속한다.

- `DefaultServerCluster`
- `chip::FabricTable::Delegate`

`Context`에는 다음 참조가 포함된다.

| 멤버 | 타입 | 용도 |
|---|---|---|
| `deviceInfoProvider` | `DeviceLayer::DeviceInfoProvider &` | 레이블 목록 조회, 저장, 추가 및 삭제 |
| `fabricTable` | `chip::FabricTable &` | Fabric delegate 등록 및 Fabric 개수 확인 |

생성자는 전달받은 `endpoint`와 `UserLabel::Id`로 `DefaultServerCluster`를 초기화한다.

레이블 항목 크기 제한은 다음과 같다.

| 상수 | 값 |
|---|---|
| `kMaxLabelSize` | `16` |
| `kMaxValueSize` | `16` |

### 속성 읽기

출처: `src/app/clusters/user-label-server/UserLabelCluster.cpp`

`UserLabelCluster::ReadAttribute`는 다음과 같이 처리한다.

| 속성 | 처리 |
|---|---|
| `LabelList::Id` | `ReadLabelList` 호출 |
| `ClusterRevision::Id` | `UserLabel::kRevision` 인코딩 |
| `FeatureMap::Id` | `uint32_t` 값 `0` 인코딩 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

`ReadLabelList`는 `provider.IterateUserLabel(endpoint)`로 반복자를 얻고 `AutoRelease`로 관리한다.

- 반복자가 null이면 `encoder.EncodeEmptyList()`를 반환한다.
- 그렇지 않으면 `encoder.EncodeList` 안에서 각 `UserLabel::Structs::LabelStruct::Type` 항목을 인코딩한다.
- 항목 인코딩 오류는 즉시 반환한다.

### 속성 쓰기와 검증

`UserLabelCluster::WriteAttribute`는 `LabelList::Id`만 처리한다. 쓰기 결과를 `NotifyAttributeChangedIfSuccess`에 전달하며, 그 외 속성에는 `Protocols::InteractionModel::Status::UnsupportedWrite`를 반환한다.

`IsValidLabelEntry`는 다음 조건을 검사한다.

- `entry.label.size() <= UserLabelCluster::kMaxLabelSize`
- `entry.value.size() <= UserLabelCluster::kMaxValueSize`

빈 `label`과 `value`는 허용한다.

#### 전체 목록 쓰기

`WriteLabelList`에서 `!path.IsListItemOperation()`이면 다음 순서로 처리한다.

1. `LabelList::TypeInfo::DecodableType`으로 입력을 디코딩한다.
2. 각 항목을 검증하고 `DeviceLayer::kMaxUserLabelListLength` 크기의 배열에 저장한다.
3. 반복자의 최종 상태를 확인한다.
4. `provider.SetUserLabelList(endpoint, Span(labels.data(), numLabels))`를 호출한다.

오류 처리는 다음과 같다.

| 조건 | 반환값 |
|---|---|
| 항목 크기 제한 위반 | `CHIP_IM_GLOBAL_STATUS(ConstraintError)` |
| 배열 용량 초과 | `CHIP_ERROR_NO_MEMORY` |
| 디코딩 또는 반복 오류 | 해당 오류 |

#### 항목 추가

`path.mListOp == ConcreteDataAttributePath::ListOperation::AppendItem`이면 다음과 같이 처리한다.

1. `Structs::LabelStruct::DecodableType`으로 항목을 디코딩한다.
2. `IsValidLabelEntry`로 검증한다.
3. `provider.AppendUserLabel(endpoint, entry)`를 호출한다.

항목 검증 실패 시 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다. `AppendUserLabel`이 `CHIP_ERROR_NO_MEMORY`를 반환하면 `CHIP_IM_GLOBAL_STATUS(ResourceExhausted)`로 변환한다.

그 밖의 목록 항목 연산은 `CHIP_ERROR_UNSUPPORTED_CHIP_FEATURE`를 반환한다.

### 속성 메타데이터

`UserLabelCluster::Attributes`는 `AttributeListBuilder`를 사용하여 `UserLabel::Attributes::kMandatoryMetadata`를 추가한다. 추가 메타데이터 인수는 빈 목록이다.

### 수명주기와 Fabric 제거

- `UserLabelCluster::Startup`
  - `DefaultServerCluster::Startup(context)`를 호출한다.
  - 성공하면 `mContext.fabricTable.AddFabricDelegate(this)`를 호출한다.
- `UserLabelCluster::Shutdown`
  - `mContext.fabricTable.RemoveFabricDelegate(this)`를 호출한다.
  - 이후 `DefaultServerCluster::Shutdown(shutdownType)`을 호출한다.
- `UserLabelCluster::OnFabricRemoved`
  - `mContext.fabricTable.FabricCount() == 0`일 때만 삭제를 수행한다.
  - `mContext.deviceInfoProvider.ClearUserLabelList(mPath.mEndpointId)`로 해당 엔드포인트의 레이블 목록을 삭제한다.
  - 삭제 실패 시 오류를 기록한다.

### Codegen 통합

출처: `src/app/clusters/user-label-server/CodegenIntegration.cpp`

서버 인스턴스 저장소는 다음과 같이 구성된다.

| 식별자 | 정의 |
|---|---|
| `kUserLabelFixedClusterCount` | `UserLabel::StaticApplicationConfig::kFixedClusterConfig.size()` |
| `kUserLabelMaxClusterCount` | `kUserLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT` |
| `gServers` | `LazyRegisteredServerCluster<UserLabelCluster>` 배열 |

`IntegrationDelegate`는 `CodegenClusterIntegration::Delegate`를 구현한다.

- `CreateRegistration`
  - `DeviceLayer::GetDeviceInfoProvider()`로 공급자를 얻고 `VerifyOrDie`로 null이 아님을 확인한다.
  - `deviceInfoProvider`와 `Server::GetInstance().GetFabricTable()`을 `UserLabelCluster::Context`에 전달하여 인스턴스를 생성한다.
  - 생성한 인스턴스의 `Registration()`을 반환한다.
- `FindRegistration`
  - 인스턴스가 생성되지 않았으면 `nullptr`를 반환한다.
  - 생성되었으면 `Cluster()`의 주소를 반환한다.
- `ReleaseRegistration`
  - 해당 인스턴스의 `Destroy()`를 호출한다.

| 콜백 | 동작 |
|---|---|
| `MatterUserLabelClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterUserLabelClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer`에 `shutdownType` 전달 |
| `MatterUserLabelPluginServerInitCallback` | 빈 구현 |

등록 시 `clusterId`는 `UserLabel::Id`이며, `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`로 설정된다.

## 관련 페이지

**베이스 클러스터**

- [Label](../base/label.md)

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
