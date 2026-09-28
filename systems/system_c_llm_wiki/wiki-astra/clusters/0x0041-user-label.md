---
entity: User Label
ids: ['0x0041']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml', 'src/app/clusters/user-label-server/CodegenIntegration.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.cpp', 'src/app/clusters/user-label-server/UserLabelCluster.h', 'data_model/1.7/clusters/UserLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# User Label

## 개요

User Label은 엔드포인트에 0개 이상의 레이블을 지정하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `User Label` |
| 클러스터 ID | `0x0041` |
| 리비전 | `1` |
| 기반 클러스터 | `Label` |
| 범위 | `Endpoint` |
| PICS 코드 | `ULABEL` |

## 스펙

출처: `data_model/1.7/clusters/UserLabel-Cluster.xml`

### 분류

- 이름: `User Label Cluster`
- 계층: `derived`
- 기반 클러스터: `Label`
- 역할: `utility`
- 리비전 이력: `1` — `Initial revision`

### 속성

| ID | 이름 | 타입 | 항목 타입 | 기본값 | 필수 여부 | 읽기 권한 | 쓰기 권한 | 영속성 |
|---|---|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | `empty` | 필수 | `view` | `manage` | `nonVolatile` |

`LabelList`는 읽기와 쓰기를 모두 지원한다. 제공된 스펙 XML의 `constraint`에는 구체적인 제약 설명이 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/user-label-cluster.xml`

### 클러스터 설정

| 항목 | 값 |
|---|---|
| 클러스터 도메인 | `General` |
| 이름 | `User Label` |
| 코드 | `0x0041` |
| 정의 매크로 | `USER_LABEL_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

### 속성 정의

| 코드 | 이름 | 정의 매크로 | 타입 | 항목 타입 | 위치 | 쓰기 |
|---|---|---|---|---|---|---|
| `0x0000` | `LabelList` | `LABEL_LIST` | `array` | `LabelStruct` | `server` | `writable="true"`, 권한 `manage` |

이 XML은 Alchemy가 생성한 파일이며 직접 수정하지 않도록 명시되어 있다. 생성 원본은 `src/data_model/UserLabel-Cluster.adoc`이다.

## 구현

### 클래스 및 의존성

출처: `src/app/clusters/user-label-server/UserLabelCluster.h`

`chip::app::Clusters`의 `UserLabelCluster`는 다음을 상속한다.

- `DefaultServerCluster`
- `chip::FabricTable::Delegate`

`Context`는 다음 참조를 보관한다.

| 멤버 | 타입 | 용도 |
|---|---|---|
| `deviceInfoProvider` | `DeviceLayer::DeviceInfoProvider &` | 레이블 목록 읽기·저장·추가·삭제 |
| `fabricTable` | `chip::FabricTable &` | Fabric 삭제 통지 등록 및 남은 Fabric 수 확인 |

생성자는 `DefaultServerCluster`에 `{ endpoint, UserLabel::Id }`를 전달한다.

### 속성 읽기

출처: `src/app/clusters/user-label-server/UserLabelCluster.cpp`

`UserLabelCluster::ReadAttribute`의 처리는 다음과 같다.

| 속성 | 처리 |
|---|---|
| `LabelList::Id` | `ReadLabelList` 호출 |
| `ClusterRevision::Id` | `UserLabel::kRevision` 인코딩 |
| `FeatureMap::Id` | `uint32_t` 값 `0` 인코딩 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

`ReadLabelList`는 `IterateUserLabel(endpoint)`로 반복자를 얻고 `AutoRelease`로 관리한다. 반복자가 없으면 `EncodeEmptyList()`를 호출한다. 반복자가 있으면 `Next(userlabel)`로 항목을 순회하며 `EncodeList`를 통해 인코딩한다.

### 속성 쓰기 및 제약

`UserLabelCluster::WriteAttribute`는 `LabelList::Id`만 처리한다. `WriteLabelList` 결과를 `NotifyAttributeChangedIfSuccess`에 전달하며, 그 외 속성에는 `Protocols::InteractionModel::Status::UnsupportedWrite`를 반환한다.

`IsValidLabelEntry`는 다음 조건을 검사한다.

| 필드 | 제약 |
|---|---|
| `label` | `size() <= UserLabelCluster::kMaxLabelSize`, `kMaxLabelSize = 16` |
| `value` | `size() <= UserLabelCluster::kMaxValueSize`, `kMaxValueSize = 16` |

빈 `label`과 `value`는 허용한다. 제약을 위반하면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.

#### 전체 목록 쓰기

`path.IsListItemOperation()`이 거짓인 경우:

1. `LabelList::TypeInfo::DecodableType`으로 디코딩한다.
2. 각 항목의 유효성을 검사한다.
3. `DeviceLayer::kMaxUserLabelListLength` 크기의 배열에 항목을 담는다.
4. 용량을 초과하면 `CHIP_ERROR_NO_MEMORY`를 반환한다.
5. 반복자 상태를 확인한 뒤 `SetUserLabelList(endpoint, Span(labels.data(), numLabels))`를 호출한다.

제공된 코드에는 `DeviceLayer::kMaxUserLabelListLength`의 수치가 포함되어 있지 않다.

#### 단일 항목 추가

`path.mListOp`가 `ConcreteDataAttributePath::ListOperation::AppendItem`인 경우:

1. `Structs::LabelStruct::DecodableType`으로 디코딩한다.
2. 항목의 유효성을 검사한다.
3. `AppendUserLabel(endpoint, entry)`를 호출한다.
4. `CHIP_ERROR_NO_MEMORY`는 `CHIP_IM_GLOBAL_STATUS(ResourceExhausted)`로 변환한다.

그 외 목록 항목 연산은 `CHIP_ERROR_UNSUPPORTED_CHIP_FEATURE`를 반환한다.

### 속성 메타데이터

`UserLabelCluster::Attributes`는 `AttributeListBuilder`를 사용하여 `UserLabel::Attributes::kMandatoryMetadata`를 추가한다.

### 시작·종료 및 Fabric 삭제

- `UserLabelCluster::Startup`
  - `DefaultServerCluster::Startup(context)`를 호출한다.
  - 성공하면 `mContext.fabricTable.AddFabricDelegate(this)`를 호출한다.
- `UserLabelCluster::Shutdown`
  - `mContext.fabricTable.RemoveFabricDelegate(this)`를 호출한다.
  - 이어서 `DefaultServerCluster::Shutdown(shutdownType)`을 호출한다.
- `UserLabelCluster::OnFabricRemoved`
  - `mContext.fabricTable.FabricCount() == 0`일 때만 정리한다.
  - `ClearUserLabelList(mPath.mEndpointId)`로 해당 엔드포인트의 레이블 목록을 삭제한다.
  - 삭제 실패 시 오류 로그를 남긴다.

### 코드 생성 통합

출처: `src/app/clusters/user-label-server/CodegenIntegration.cpp`

인스턴스 수와 저장소는 다음과 같이 구성된다.

- `kUserLabelFixedClusterCount`: `UserLabel::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kUserLabelMaxClusterCount`: `kUserLabelFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`
- `gServers`: `LazyRegisteredServerCluster<UserLabelCluster>` 배열

`IntegrationDelegate`는 등록 객체의 생성·조회·해제를 담당한다.

| 함수 | 동작 |
|---|---|
| `CreateRegistration` | `DeviceLayer::GetDeviceInfoProvider()`가 `nullptr`이 아닌지 `VerifyOrDie`로 확인하고, `deviceInfoProvider`와 `Server::GetInstance().GetFabricTable()`을 전달하여 인스턴스 생성 |
| `FindRegistration` | 인스턴스가 생성되어 있으면 클러스터 포인터 반환, 아니면 `nullptr` 반환 |
| `ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

콜백 동작은 다음과 같다.

- `MatterUserLabelClusterInitCallback`: `CodegenClusterIntegration::RegisterServer`로 `UserLabel::Id`를 등록한다. `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`이다.
- `MatterUserLabelClusterShutdownCallback`: `CodegenClusterIntegration::UnregisterServer`로 등록을 해제하며 `shutdownType`을 전달한다.
- `MatterUserLabelPluginServerInitCallback`: 본문이 비어 있다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
