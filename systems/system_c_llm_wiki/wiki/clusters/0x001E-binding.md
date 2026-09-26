---
entity: Binding
ids: ['0x001E']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml', 'src/app/clusters/bindings/BindingManager.cpp', 'src/app/clusters/bindings/BindingCluster.h', 'src/app/clusters/bindings/binding-table.h', 'src/app/clusters/bindings/PendingNotificationMap.h', 'src/app/clusters/bindings/BindingManager.h', 'src/app/clusters/bindings/CodegenIntegration.cpp', 'src/app/clusters/bindings/PendingNotificationMap.cpp', 'src/app/clusters/bindings/README.md', 'src/app/clusters/bindings/BindingCluster.cpp', 'src/app/clusters/bindings/binding-table.cpp', 'data_model/1.7/clusters/Binding-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 클러스터 개요

- 클러스터 이름: `Binding Cluster`
- 클러스터 ID: `0x001E`
- 클러스터 revision: `1`
- classification:
  - hierarchy: `base`
  - role: `utility`
  - PICS code: `BIND`
  - scope: `Endpoint`
- 클러스터 ID 정의:
  - `0x001E`: `Binding`
- revision history:
  - revision `1`: `Initial revision`

### 목적

`Binding Cluster`는 바인딩 테이블을 지원하기 위해 Zigbee Device Object (ZDO)가 제공하던 지원 기능을 대체하기 위한 클러스터이다.

### 데이터 타입

#### `TargetStruct`

`TargetStruct`는 fabric-scoped 구조체이다.

| 필드 ID | 이름 | 타입 | 조건 |
|---|---|---|---|
| `1` | `Node` | `node-id` | `Endpoint`와 함께 사용 |
| `2` | `Group` | `group-id` | `Endpoint`와 함께 사용할 수 없음. 최솟값은 `1` |
| `3` | `Endpoint` | `endpoint-no` | `Group`과 함께 사용할 수 없음 |
| `4` | `Cluster` | `cluster-id` | 선택 사항 |

### 속성

#### `Binding`

- 속성 ID: `0x0000`
- 타입: `list`
- 기본값: `empty`
- 항목 타입: `TargetStruct`
- 접근:
  - 읽기: 허용
  - 쓰기: 허용
  - read privilege: `view`
  - write privilege: `manage`
  - fabric-scoped: `true`
- persistence: `nonVolatile`
- 적합성: mandatory

## SDK 정의

### `src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml`

#### `TargetStruct`

- 클러스터 코드: `0x001e`
- fabric-scoped: `true`

| fieldId | 이름 | 타입 | 선택 사항 | 제약 |
|---|---|---|---|---|
| `1` | `Node` | `node_id` | `true` |  |
| `2` | `Group` | `group_id` | `true` | `min="1"` |
| `3` | `Endpoint` | `endpoint_no` | `true` |  |
| `4` | `Cluster` | `cluster_id` | `true` |  |

#### `Binding`

- domain: `General`
- 이름: `Binding`
- 코드: `0x001e`
- define: `BINDING_CLUSTER`
- client: `true`
- server: `true`
- global attribute:
  - 코드: `0xFFFD`
  - side: `either`
  - value: `1`
- 속성:
  - 이름: `Binding`
  - 코드: `0x0000`
  - side: `server`
  - define: `BINDING_LIST`
  - 타입: `array`
  - 항목 타입: `TargetStruct`
  - writable: `true`
  - 접근 operation: `write`
  - role: `manage`
  - 적합성: mandatory

## 구현

### `BindingCluster`

구현 파일:

- `src/app/clusters/bindings/BindingCluster.h`
- `src/app/clusters/bindings/BindingCluster.cpp`

`BindingCluster`는 `DefaultServerCluster`를 상속한다.

#### `BindingCluster::Context`

- `Binding::Table & bindingTable`
- `Binding::Manager & bindingManager`
- `DeviceLayer::PlatformManager & platformManager`

#### 주요 메서드

- `ReadAttribute`
- `WriteAttribute`
- `ListAttributeWriteNotification`
- `Attributes`
- `IsValidBinding`
- `CheckValidBindingList`
- `NotifyBindingsChanged`
- `CreateBindingEntry`

생성자는 `ConcreteClusterPath::ConstExpr(endpointId, Binding::Id)`를 사용한다.

#### `Binding` 속성 읽기

`Binding::Attributes::Binding::Id`를 읽을 때 `bindingTable`의 항목 중 요청된 endpoint에 해당하는 항목을 목록으로 인코딩한다.

- `MATTER_UNICAST_BINDING`:
  - `node`: `nodeId`
  - `group`: 없음
  - `endpoint`: `remote`
  - `cluster`: `clusterId`
  - `fabricIndex`: `fabricIndex`
- `MATTER_MULTICAST_BINDING`:
  - `node`: 없음
  - `group`: `groupId`
  - `endpoint`: 없음
  - `cluster`: `clusterId`
  - `fabricIndex`: `fabricIndex`

다음 전역 속성도 지원한다.

- `Globals::Attributes::FeatureMap::Id`: `0`
- `Globals::Attributes::ClusterRevision::Id`: `Binding::kRevision`

그 외 속성은 `UnsupportedAttribute`를 반환한다.

#### `Binding` 속성 쓰기

`Binding::Attributes::Binding::Id`에 대해 다음 동작을 수행한다.

- 목록 operation이 아니거나 `ReplaceAll`인 경우:
  1. 새 목록을 디코딩한다.
  2. `CheckValidBindingList`로 유효성을 검사한다.
  3. 현재 accessing fabric과 endpoint에 해당하는 기존 항목을 제거한다.
  4. 기존 `MATTER_UNICAST_BINDING` 항목에 대해 `UnicastBindingRemoved`를 호출한다.
  5. 새 항목을 `CreateBindingEntry`로 추가한다.
  6. 목록 operation이 아니면 `NotifyBindingsChanged`를 호출한다.
- `AppendItem`인 경우:
  1. `TargetStruct`를 디코딩한다.
  2. `IsValidBinding`으로 유효성을 검사한다.
  3. `CreateBindingEntry`로 추가한다.
- 그 외 목록 operation은 `UnsupportedWrite`를 반환한다.

`ListAttributeWriteNotification`은 `kListWriteSuccess`일 때 `NotifyBindingsChanged`를 호출한다.

`NotifyBindingsChanged`는 `DeviceLayer::DeviceEventType::kBindingsChangedViaCluster` 이벤트를 게시하며, 이벤트에 `fabricIndex`를 포함한다.

### `Binding::TableEntry`

구현 파일:

- `src/app/clusters/bindings/binding-table.h`
- `src/app/clusters/bindings/binding-table.cpp`

`TableEntry`는 다음 정보를 표현한다.

- `type`
- `fabricIndex`
- `local`
- `clusterId`
- `remote`
- `nodeId` 또는 `groupId`

`clusterId`는 local endpoint의 simple descriptor에 있는 cluster ID와 일치하는 값으로, 특정 remote node에 바인딩된 endpoint 기능 부분을 나타내는 데 사용된다. 바인딩은 해당 `clusterId`뿐 아니라 다른 cluster ID를 사용하는 메시지도 전송할 수 있다.

#### `EntryType`

| 값 | 이름 | 설명 |
|---:|---|---|
| `0` | `MATTER_UNUSED_BINDING` | 현재 사용되지 않는 바인딩 |
| `1` | `MATTER_UNICAST_BINDING` | destination EUI64가 64-bit 식별자인 unicast 바인딩 |
| `3` | `MATTER_MULTICAST_BINDING` | group address가 64-bit 식별자인 multicast 바인딩 |

#### 생성 및 팩토리 메서드

- `TableEntry(FabricIndex fabric, NodeId node, EndpointId localEndpoint, EndpointId remoteEndpoint, std::optional<ClusterId> cluster)`
- `TableEntry(FabricIndex fabric, GroupId group, EndpointId localEndpoint, std::optional<ClusterId> cluster)`
- `TableEntry::ForNode`
- `TableEntry::ForGroup`

#### `Table`

- 최대 항목 수:
  - `CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC * CHIP_CONFIG_MAX_FABRICS`
- 상수:
  - `Table::kMaxBindingEntries`
- 주요 메서드:
  - `Add`
  - `GetAt`
  - `RemoveAt`
  - `Size`
  - `begin`
  - `end`
  - `SetPersistentStorage`
  - `LoadFromStorage`
  - `Table::GetInstance`

`Table`은 persistent storage에 바인딩 항목과 연결 목록 정보를 저장한다.

- storage version: `1`
- `kTagStorageVersion`: `1`
- `kTagHead`: `2`
- `kTagFabricIndex`: `1`
- `kTagLocalEndpoint`: `2`
- `kTagCluster`: `3`
- `kTagRemoteEndpoint`: `4`
- `kTagNodeId`: `5`
- `kTagGroupId`: `6`
- `kTagNextEntry`: `7`
- `kNextNullIndex`: `255`

`LoadFromStorage`는 저장된 version이 `kStorageVersion`과 다르면 `CHIP_ERROR_VERSION_MISMATCH`를 반환한다.

### `Binding::Manager`

구현 파일:

- `src/app/clusters/bindings/BindingManager.h`
- `src/app/clusters/bindings/BindingManager.cpp`

`Manager`는 unicast binding의 연결을 관리하고, binding이 통신 가능한 상태가 되었을 때 application에 알린다.

#### 연결 수립 시점

CASE 연결은 다음 시점에 시작될 수 있다.

- `Manager::Init` 중
  - 단, `mEstablishConnectionOnInit`이 `false`이면 비활성화된다.
- binding cluster가 unicast 항목을 추가할 때
- watched cluster가 변경되었고 unicast binding에 대한 활성 연결을 찾을 수 없을 때

연결 공간이 부족하면 LRU 방식으로 제거할 peer를 선택한다. `Manager`는 연결을 적극적으로 재수립하지 않으며, binding cluster 또는 watched cluster가 변경될 때 on-demand로 연결한다.

#### `ManagerInitParams`

- `FabricTable * mFabricTable`
- `CASESessionManager * mCASESessionManager`
- `PersistentStorageDelegate * mStorage`
- `bool mEstablishConnectionOnInit`

`Init`는 `mCASESessionManager`, `mFabricTable`, `mStorage`가 `nullptr`이 아닌지 확인한 뒤 binding table을 storage에서 로드한다. 초기화 중 로드에 실패하면 오류를 기록하고 계속 진행한다.

#### 콜백

`BoundDeviceChangedHandler`는 binding과 연결된 cluster가 변경되었을 때 호출된다.

```cpp
using BoundDeviceChangedHandler =
    void (*)(const TableEntry & binding,
             OperationalDeviceProxy * peer_device,
             void * context);
```

- unicast binding:
  - `peer_device`는 연결된 peer이다.
  - `group`은 비어 있다.
- multicast binding:
  - `peer_device`는 `nullptr`이다.

애플리케이션은 callback에서 peer로 보낼 콘텐츠를 결정한다. 전달된 `SessionHandler` 포인터를 보유해서는 안 된다.

#### 주요 메서드

- `RegisterBoundDeviceChangedHandler`
- `RegisterBoundDeviceContextReleaseHandler`
- `Init`
- `UnicastBindingCreated`
- `UnicastBindingRemoved`
- `FabricRemoved`
- `NotifyBoundClusterChanged`
- `AddBindingEntry`
- `GetBindingTable`
- `Manager::GetInstance`

`NotifyBoundClusterChanged`는 `(endpoint, cluster)` tuple에 연결된 모든 bound device에 알린다.

- 활성 session이 있는 unicast binding과 multicast binding:
  - `BoundDeviceChangedHandler`가 함수 반환 전에 호출된다.
- 활성 session이 없는 unicast binding:
  - notification을 대기열에 추가한다.
  - 새 session을 시작한다.
  - session이 수립되면 `BoundDeviceChangedHandler`를 호출한다.

`AddBindingEntry`는 `Table::Add`를 호출하고, 항목이 `MATTER_UNICAST_BINDING`이면 `UnicastBindingCreated`를 호출하여 peer에 대한 CASE session 수립을 시도한다.

#### Fabric 제거

`OnFabricRemoved`는 해당 `fabricIndex`의 binding table 항목을 제거한 뒤 `FabricRemoved`를 호출한다.

`FabricRemoved`는 다음을 수행한다.

- `mPendingNotificationMap.RemoveAllEntriesForFabric`
- `CASESessionManager::ReleaseSessionsForFabric`

### `PendingNotificationMap`

구현 파일:

- `src/app/clusters/bindings/PendingNotificationMap.h`
- `src/app/clusters/bindings/PendingNotificationMap.cpp`

`PendingNotificationMap`은 대기 중인 notification과 notification context를 관리한다.

- `kMaxPendingNotifications`: `Table::kMaxBindingEntries`
- `PendingNotificationEntry`
  - `mBindingEntryId`
  - `mContext`
- 주요 메서드:
  - `FindLRUConnectPeer`
  - `AddPendingNotification`
  - `RemoveEntry`
  - `RemoveAllEntriesForNode`
  - `RemoveAllEntriesForFabric`
  - `RegisterPendingNotificationContextReleaseHandler`
  - `NewPendingNotificationContext`

`PendingNotificationContext`는 consumer 수를 관리하며, consumer 수가 `0`이 되면 등록된 `PendingNotificationContextReleaseHandler`를 호출하고 자신을 삭제한다.

`FindLRUConnectPeer`는 `PendingNotificationMap`에 추가된 순서를 기준으로 peer별 마지막 출현 위치를 비교하여 LRU peer를 선택한다.

### Codegen 통합

구현 파일:

- `src/app/clusters/bindings/CodegenIntegration.cpp`

`MatterBindingClusterInitCallback`은 다음 설정으로 server cluster를 등록한다.

- `clusterId`: `Binding::Id`
- `fixedClusterInstanceCount`: `kBindingFixedClusterCount`
- `maxClusterInstanceCount`: `kBindingMaxClusterCount`
- `fetchFeatureMap`: `false`
- `fetchOptionalAttributes`: `false`

`IntegrationDelegate`는 다음 dependency를 주입하여 `BindingCluster`를 생성한다.

- `Binding::Table::GetInstance()`
- `Binding::Manager::GetInstance()`
- `DeviceLayer::PlatformMgr()`

`MatterBindingClusterShutdownCallback`은 `CodegenClusterIntegration::UnregisterServer`를 통해 server cluster를 해제한다.

### 주요 오류 처리

구현에서 사용되는 대표적인 오류는 다음과 같다.

- `CHIP_ERROR_INVALID_ARGUMENT`
- `CHIP_ERROR_INCORRECT_STATE`
- `CHIP_ERROR_NO_MEMORY`
- `CHIP_ERROR_NOT_FOUND`
- `CHIP_ERROR_VERSION_MISMATCH`
- `CHIP_ERROR_INVALID_TLV_TAG`
- `CHIP_IM_GLOBAL_STATUS(ResourceExhausted)`
- `CHIP_IM_GLOBAL_STATUS(ConstraintError)`
- `CHIP_IM_GLOBAL_STATUS(UnsupportedWrite)`
- `Protocols::InteractionModel::Status::UnsupportedAttribute`
- `Protocols::InteractionModel::Status::UnsupportedWrite`

## 관련 문서

### `src/app/clusters/bindings/README.md`

Binding table 크기는 기존 `MATTER_BINDING_TABLE_SIZE`에서 다음 식으로 변경되었다.

```text
CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC * CHIP_CONFIG_MAX_FABRICS
```

기존 값은 기본적으로 `src/app/util/config.h`에 정의되어 있었으며, 변경된 값은 `src/lib/core/CHIPConfig.h`에 정의되어 있다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
