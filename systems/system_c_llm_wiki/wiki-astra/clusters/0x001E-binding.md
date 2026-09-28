---
entity: Binding
ids: ['0x001E']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml', 'src/app/clusters/bindings/BindingManager.cpp', 'src/app/clusters/bindings/BindingCluster.h', 'src/app/clusters/bindings/binding-table.h', 'src/app/clusters/bindings/PendingNotificationMap.h', 'src/app/clusters/bindings/BindingManager.h', 'src/app/clusters/bindings/CodegenIntegration.cpp', 'src/app/clusters/bindings/PendingNotificationMap.cpp', 'src/app/clusters/bindings/README.md', 'src/app/clusters/bindings/BindingCluster.cpp', 'src/app/clusters/bindings/binding-table.cpp', 'data_model/1.7/clusters/Binding-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Binding

## 개요

Binding은 바인딩 테이블을 지원하기 위한 클러스터로, SDK 설명에서는 Zigbee Device Object (ZDO)의 바인딩 테이블 지원을 대체하는 용도로 정의한다.

- 로컬 엔드포인트와 원격 노드 또는 그룹 간의 바인딩을 저장한다.
- `Binding` 속성은 `TargetStruct` 목록이며, fabric 범위로 관리되고 비휘발성으로 유지된다.
- 구현은 `BindingCluster`, `Manager`, `Table`, `PendingNotificationMap`으로 구성된다.
- `Manager`는 유니캐스트 대상의 CASE 연결을 관리하고, 통신 가능한 바인딩 대상을 애플리케이션 콜백에 전달한다. 전송할 내용은 애플리케이션이 결정한다.

## 스펙

출처: `data_model/1.7/clusters/Binding-Cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| XML 이름 | `Binding Cluster` |
| 클러스터 이름 | `Binding` |
| 클러스터 ID | `0x001E` |
| revision | `1` |
| revision 설명 | `Initial revision` |
| hierarchy | `base` |
| role | `utility` |
| picsCode | `BIND` |
| scope | `Endpoint` |

### `TargetStruct`

`TargetStruct`는 `fabricScoped="true"`인 구조체다.

| 필드 ID | 이름 | 타입 | 적합성 조건 및 제약 |
|---|---|---|---|
| `1` | `Node` | `node-id` | `Endpoint`를 조건으로 하는 `mandatoryConform` |
| `2` | `Group` | `group-id` | `Endpoint`의 부정을 조건으로 하는 `mandatoryConform`; 최솟값 `1` |
| `3` | `Endpoint` | `endpoint-no` | `Group`의 부정을 조건으로 하는 `mandatoryConform` |
| `4` | `Cluster` | `cluster-id` | `optionalConform` |

### `Binding` 속성

| 항목 | 정의 |
|---|---|
| ID | `0x0000` |
| 이름 | `Binding` |
| 타입 | `list` |
| 목록 항목 타입 | `TargetStruct` |
| 기본값 | `empty` |
| 읽기 | 허용, `readPrivilege="view"` |
| 쓰기 | 허용, `writePrivilege="manage"` |
| fabric 범위 | `fabricScoped="true"` |
| 저장 특성 | `persistence="nonVolatile"` |
| 적합성 | `mandatoryConform` |

속성의 `<constraint>`에는 빈 `<desc/>`만 있으며, 구체적인 목록 크기 제한은 이 스펙 조각에 기재되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml`

이 파일은 Alchemy가 생성한 XML이며, 직접 수정하지 않도록 표시되어 있다. 생성 원본은 `src/data_model/Binding-Cluster.adoc`이다.

### 클러스터 정의

| 항목 | 값 |
|---|---|
| domain | `General` |
| name | `Binding` |
| code | `0x001e` |
| define | `BINDING_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `code="0xFFFD"`, `side="either"`, `value="1"` |

스펙에서는 클러스터 ID를 `0x001E`, SDK XML에서는 `0x001e`로 표기한다.

### 구조체와 속성

SDK의 `TargetStruct`는 `isFabricScoped="true"`이며 다음 필드를 정의한다.

| fieldId | 이름 | 타입 | SDK 선언 |
|---|---|---|---|
| `1` | `Node` | `node_id` | `optional="true"` |
| `2` | `Group` | `group_id` | `optional="true"`, `min="1"` |
| `3` | `Endpoint` | `endpoint_no` | `optional="true"` |
| `4` | `Cluster` | `cluster_id` | `optional="true"` |

`Binding` 속성은 다음과 같이 정의된다.

- `side="server"`
- `code="0x0000"`
- `define="BINDING_LIST"`
- `type="array"`, `entryType="TargetStruct"`
- `writable="true"`
- 쓰기 접근: `op="write"`, `role="manage"`
- 적합성: `mandatoryConform`

스펙의 필드 간 조건부 적합성과 달리, SDK XML의 각 필드는 모두 `optional="true"`로 선언되어 있다.

## 구현

### 구성 요소

| 파일 | 역할 |
|---|---|
| `src/app/clusters/bindings/BindingCluster.h` | `BindingCluster` 인터페이스와 의존성 정의 |
| `src/app/clusters/bindings/BindingCluster.cpp` | 속성 읽기·쓰기, 항목 검증, 변경 이벤트 처리 |
| `src/app/clusters/bindings/BindingManager.h` | `Manager`, 초기화 매개변수, 애플리케이션 콜백 정의 |
| `src/app/clusters/bindings/BindingManager.cpp` | CASE 연결 및 바인딩 변경 알림 관리 |
| `src/app/clusters/bindings/binding-table.h` | `EntryType`, `TableEntry`, `Table` 정의 |
| `src/app/clusters/bindings/binding-table.cpp` | 테이블 추가·삭제, TLV 저장 및 복원 |
| `src/app/clusters/bindings/PendingNotificationMap.h` | 대기 알림과 컨텍스트 수명 관리 인터페이스 |
| `src/app/clusters/bindings/PendingNotificationMap.cpp` | 대기 알림 교체·삭제 및 LRU 대상 검색 |
| `src/app/clusters/bindings/CodegenIntegration.cpp` | 클러스터 인스턴스 생성·등록·해제 |

### `BindingCluster`

`BindingCluster`는 `DefaultServerCluster`를 상속한다. `Context`로 다음 의존성을 주입받는다.

- `Binding::Table & bindingTable`
- `Binding::Manager & bindingManager`
- `DeviceLayer::PlatformManager & platformManager`

타입 별칭은 다음과 같다.

- `TargetStructType`: `Binding::Structs::TargetStruct::Type`
- `DecodableBindingListType`: `Binding::Attributes::Binding::TypeInfo::DecodableType`

#### 속성 읽기

`ReadAttribute`는 다음을 처리한다.

| 속성 | 처리 |
|---|---|
| `Binding::Attributes::Binding::Id` | 요청 엔드포인트와 `entry.local`이 일치하는 항목을 목록으로 인코딩 |
| `Globals::Attributes::FeatureMap::Id` | `uint32_t` 값 `0` 반환 |
| `Globals::Attributes::ClusterRevision::Id` | `Binding::kRevision` 반환 |
| 그 외 | `Protocols::InteractionModel::Status::UnsupportedAttribute` 반환 |

목록 인코딩 시:

- `MATTER_UNICAST_BINDING`: `node`, `endpoint`, 선택적 `cluster`, `fabricIndex`를 설정하고 `group`은 `NullOptional`로 설정한다.
- `MATTER_MULTICAST_BINDING`: `group`, 선택적 `cluster`, `fabricIndex`를 설정하고 `node`, `endpoint`는 `NullOptional`로 설정한다.

`Attributes`는 `Binding::Attributes::kMandatoryMetadata`를 사용해 속성 목록을 구성한다.

#### 항목 검증

`IsValidBinding`의 실제 조건은 다음과 같다.

- `group`이 없고 `endpoint`, `node`가 있는 경우:
  - `cluster`가 없으면 유효하다.
  - `cluster`가 있으면 `mContext->provider.ClientClusters`로 로컬 엔드포인트의 클라이언트 클러스터 목록을 조회한다.
  - 조회가 실패하거나 일치하는 클러스터가 없으면 유효하지 않다.
- `endpoint`, `node`가 없고 `group`이 있으면 유효하다.

클라이언트 클러스터 검증 코드에는 검증의 적절성을 묻는 TODO가 남아 있다. 또한 `Group`의 최솟값 `1`은 스펙과 SDK XML에 정의되어 있지만, `IsValidBinding` 본문에서는 직접 검사하지 않는다.

`CheckValidBindingList`는 각 항목을 검증하고 다음 용량 조건을 확인한다.

```cpp
mClusterContext.bindingTable.Size() - oldListSize + listSize <= Binding::Table::kMaxBindingEntries
```

`oldListSize`는 현재 접근 fabric과 로컬 엔드포인트에 속한 기존 항목 수다.

- 항목 검증 실패: `CHIP_IM_GLOBAL_STATUS(ConstraintError)`
- 용량 초과: `CHIP_IM_GLOBAL_STATUS(ResourceExhausted)`

#### 속성 쓰기와 변경 통지

`WriteAttribute`는 `Binding::Attributes::Binding::Id`에 대해 다음 동작을 지원한다.

| 동작 | 처리 |
|---|---|
| 목록 연산이 아닌 쓰기 또는 `ReplaceAll` | 새 목록 검증 후, 현재 접근 fabric과 엔드포인트의 기존 항목을 삭제하고 새 항목 추가 |
| `AppendItem` | 항목을 디코딩·검증한 뒤 추가 |
| 그 외 | `CHIP_IM_GLOBAL_STATUS(UnsupportedWrite)` 반환 |

기존 유니캐스트 항목을 삭제하기 전에는 `UnicastBindingRemoved`를 호출해 해당 대기 알림을 제거한다.

`CreateBindingEntry`는 `group` 유무에 따라 `Binding::TableEntry`를 구성하고 `bindingManager.AddBindingEntry`에 전달한다.

`NotifyBindingsChanged`는 접근 fabric을 담은 `DeviceLayer::DeviceEventType::kBindingsChangedViaCluster` 이벤트를 `PostEvent`로 게시한다.

- 목록 연산이 아닌 쓰기에서는 `WriteAttribute`가 직접 변경 통지를 수행한다.
- 목록 쓰기는 `ListAttributeWriteNotification`에서 `DataModel::ListWriteOperation::kListWriteSuccess`를 받았을 때 통지한다.

### `TableEntry`와 `Table`

#### 항목 타입

| 식별자 | 값 | 의미 |
|---|---|---|
| `MATTER_UNUSED_BINDING` | `0` | 사용하지 않는 항목 |
| `MATTER_UNICAST_BINDING` | `1` | 원격 노드 대상 바인딩 |
| `MATTER_MULTICAST_BINDING` | `3` | 그룹 대상 바인딩 |

`TableEntry`는 다음 정보를 보관한다.

- `type`
- `fabricIndex`
- 로컬 엔드포인트 `local`
- 선택적 클러스터 ID `clusterId`
- 원격 엔드포인트 `remote`
- 공용체의 `nodeId` 또는 `groupId`

`ForNode`와 `ForGroup`으로 각각 유니캐스트·멀티캐스트 항목을 만들 수 있다. 그룹 항목의 `remote`는 `kInvalidEndpointId`로 설정된다.

#### 용량과 순회

`Table::kMaxBindingEntries`는 다음 식으로 정의된다.

```cpp
static_cast<size_t>(CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC) * CHIP_CONFIG_MAX_FABRICS
```

- `Size`는 용량이 아니라 활성 항목 수를 반환한다.
- `Iterator`는 `mNextIndex`를 따라 순회한다.
- `RemoveAt` 호출 후 반복자는 다음 항목으로 이동한다.
- 연결 종료 표시는 `kNextNullIndex = 255`다.
- `Table::GetInstance`는 `Manager::GetInstance().GetBindingTable()`을 반환한다.

#### 영속 저장

테이블은 `PersistentStorageDelegate`와 TLV를 사용한다.

| 저장 대상 | 저장 키 생성 |
|---|---|
| 목록 정보 | `DefaultStorageKeyAllocator::BindingTable()` |
| 개별 항목 | `DefaultStorageKeyAllocator::BindingTableEntry(index)` |

- `SaveListInfo`는 `kStorageVersion`과 목록의 시작 인덱스를 저장한다. `kStorageVersion`은 `1`이다.
- `SaveEntryToStorage`는 fabric, 로컬 엔드포인트, 선택적 클러스터, 노드 또는 그룹 정보, 다음 항목 인덱스를 저장한다.
- `Add`는 `MATTER_UNUSED_BINDING`을 거부하며, 빈 슬롯이 없으면 `CHIP_ERROR_NO_MEMORY`를 반환한다.
- 추가 중 저장 오류가 발생하면 새 슬롯의 `type`을 `MATTER_UNUSED_BINDING`으로 되돌린다.
- `RemoveAt`는 이전 항목 또는 목록 시작 정보의 저장 갱신이 성공한 뒤 삭제를 반영한다. 개별 저장 키 삭제 실패는 로그로 기록한다.
- `LoadFromStorage`는 저장 버전을 검사하며, 불일치 시 `CHIP_ERROR_VERSION_MISMATCH`를 반환한다.
- `LoadEntryFromStorage`는 고정 배열에 접근하기 전에 인덱스 범위를 검사한다.

### `Manager`

#### 초기화

`ManagerInitParams`의 기본값은 다음과 같다.

| 필드 | 기본값 |
|---|---|
| `mFabricTable` | `nullptr` |
| `mCASESessionManager` | `nullptr` |
| `mStorage` | `nullptr` |
| `mEstablishConnectionOnInit` | `true` |

`Init`는 세 포인터가 모두 유효한지 검사하고, 저장소와 fabric delegate를 설정한 뒤 `LoadFromStorage`를 호출한다.

- 필수 포인터가 없으면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
- 테이블 복원 실패는 로그로 기록하며, `Init` 자체는 `CHIP_NO_ERROR`를 반환한다.
- 복원이 성공하고 `mEstablishConnectionOnInit`이 `true`이면 기존 유니캐스트 항목의 연결을 시도한다.
- 초기 연결 실패는 무시하며, 필요할 때 다시 연결한다.

#### 바인딩 추가와 연결

`Manager::AddBindingEntry`는 `mBindingTable.Add`를 호출한다.

- `CHIP_ERROR_NO_MEMORY`는 `CHIP_IM_GLOBAL_STATUS(ResourceExhausted)`로 변환한다.
- 유니캐스트 항목이면 `UnicastBindingCreated`를 통해 연결을 시도한다.
- 항목 추가 후 연결만 실패한 경우에는 로그를 남기고 `CHIP_NO_ERROR`를 반환한다.

외부 `AddBindingEntry` 함수는 `Binding::Manager::GetInstance().AddBindingEntry(entry)`로 위임한다.

`EstablishConnection`은 `FindOrEstablishSession`을 사용한다. 동기적으로 기록된 오류가 `CHIP_ERROR_NO_MEMORY`이면 `FindLRUConnectPeer`로 대상을 찾고, 그 대상의 대기 알림을 제거한 뒤 재시도한다.

`HandleDeviceConnectionFailure`는 오류를 기록하지만 대기 항목을 제거하지 않는다. 이 재시도 처리에는 `TODO(#22173)`이 남아 있다.

#### 바인딩 대상 변경 알림

`NotifyBoundClusterChanged`는 다음 조건에 맞는 항목을 처리한다.

```cpp
iter->local == endpoint && (iter->clusterId.value_or(cluster) == cluster)
```

따라서 `clusterId`가 없는 항목도 요청된 `cluster`에 대해 일치한다.

- 유니캐스트: 대기 알림을 추가하고 연결을 요청한다.
- 멀티캐스트: `peer_device`에 `nullptr`를 전달하여 `mBoundDeviceChangedHandler`를 호출한다.
- 활성 세션이 있는 유니캐스트와 멀티캐스트는 함수 반환 전에 콜백이 호출된다.
- 활성 세션이 없는 유니캐스트는 세션이 수립된 뒤 콜백이 호출된다.

`HandleDeviceConnected`는 해당 peer의 대기 알림마다 `OperationalDeviceProxy`를 구성해 콜백을 호출하고, 처리한 노드의 대기 알림을 제거한다.

주요 콜백 등록 API:

- `RegisterBoundDeviceChangedHandler`
- `RegisterBoundDeviceContextReleaseHandler`

헤더는 전달된 `SessionHandler` 포인터를 핸들러가 보관해서는 안 된다고 명시한다.

#### fabric 제거

`OnFabricRemoved`는 해당 fabric의 테이블 항목을 삭제한 뒤 `FabricRemoved`를 호출한다.

`FabricRemoved`는:

1. `RemoveAllEntriesForFabric`으로 대기 알림을 제거한다.
2. `ReleaseSessionsForFabric`으로 해당 fabric의 세션을 해제한다.

세션 해제를 NOC cluster가 처리해야 한다는 `TODO(#18436)`이 남아 있다.

### `PendingNotificationMap`

`kMaxPendingNotifications`는 `Table::kMaxBindingEntries`와 같다.

- `AddPendingNotification`은 같은 `bindingEntryId`의 기존 알림을 먼저 제거하고 새 알림을 끝에 추가한다.
- 용량이 부족하면 `CHIP_ERROR_NO_MEMORY`를 반환한다.
- `RemoveEntry`, `RemoveAllEntriesForNode`, `RemoveAllEntriesForFabric`은 제거되는 알림의 컨텍스트 소비자 수를 감소시킨다.
- `FindLRUConnectPeer`는 같은 fabric과 노드를 하나의 peer로 묶고, 마지막 알림 위치가 가장 앞에 있는 peer를 선택한다. 대상이 없으면 `CHIP_ERROR_NOT_FOUND`를 반환한다.

`PendingNotificationContext`는 소비자 수를 관리한다. `DecrementConsumersNumber`로 소비자 수가 `0`이 되면 등록된 해제 핸들러를 호출하고 `Platform::Delete(this)`로 자신을 삭제한다.

### 코드 생성 통합

`CodegenIntegration.cpp`는 다음 개수만큼 `LazyRegisteredServerCluster<BindingCluster>`를 관리한다.

```cpp
kBindingFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT
```

- `IntegrationDelegate::CreateRegistration`: `BindingCluster::Context`를 구성해 인스턴스를 생성한다.
- `IntegrationDelegate::FindRegistration`: 생성된 인스턴스의 인터페이스를 반환한다.
- `IntegrationDelegate::ReleaseRegistration`: 인스턴스를 제거한다.
- `MatterBindingClusterInitCallback`: `CodegenClusterIntegration::RegisterServer`를 호출한다.
- `MatterBindingClusterShutdownCallback`: `CodegenClusterIntegration::UnregisterServer`를 호출한다.
- 등록 시 `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`다.
- `MatterBindingPluginServerInitCallback`과 `MatterBindingPluginServerShutdownCallback`의 본문은 비어 있다.

## 관련 문서

### 업그레이드 참고

출처: `src/app/clusters/bindings/README.md`

바인딩 테이블 크기 설정은 다음과 같이 변경되었다.

| 구분 | 설정 |
|---|---|
| 이전 | `MATTER_BINDING_TABLE_SIZE` |
| 변경 후 | `CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC * CHIP_CONFIG_MAX_FABRICS` |

이전 기본값 정의 위치는 `src/app/util/config.h`였으며, 변경 후 설정은 `src/lib/core/CHIPConfig.h`에 정의된다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
