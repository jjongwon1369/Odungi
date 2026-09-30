---
entity: Binding
ids: ['0x001E']
source_paths: ['data_model/1.7/clusters/Binding-Cluster.xml', 'src/app/clusters/bindings/BindingCluster.cpp', 'src/app/clusters/bindings/BindingCluster.h', 'src/app/clusters/bindings/BindingManager.cpp', 'src/app/clusters/bindings/BindingManager.h', 'src/app/clusters/bindings/CodegenIntegration.cpp', 'src/app/clusters/bindings/PendingNotificationMap.cpp', 'src/app/clusters/bindings/PendingNotificationMap.h', 'src/app/clusters/bindings/README.md', 'src/app/clusters/bindings/binding-table.cpp', 'src/app/clusters/bindings/binding-table.h', 'src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Binding

## 개요

`Binding`은 바인딩 테이블을 제공하는 클러스터다. SDK 설명에서는 Zigbee Device Object (ZDO)의 바인딩 테이블 지원을 대체하기 위한 클러스터로 정의한다.

구현은 로컬 엔드포인트와 원격 노드 또는 그룹 간의 바인딩을 저장하며, 다음 구성 요소로 나뉜다.

- `BindingCluster`: `Binding` 속성의 읽기·쓰기와 입력 검증.
- `Binding::Table`: 바인딩 항목 관리 및 영구 저장.
- `Binding::Manager`: 유니캐스트 연결 관리와 애플리케이션 알림.
- `PendingNotificationMap`: 연결 대기 중인 알림과 컨텍스트 수명 관리.

## 스펙

출처: `data_model/1.7/clusters/Binding-Cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Binding Cluster` |
| 클러스터 식별자 이름 | `Binding` |
| 클러스터 ID | `0x001E` |
| revision | `1` |
| revision 이력 | `Initial revision` |
| hierarchy | `base` |
| role | `utility` |
| picsCode | `BIND` |
| scope | `Endpoint` |

### `TargetStruct`

`TargetStruct`는 `fabricScoped="true"`인 구조체다.

| 필드 ID | 이름 | 타입 | 적합성 조건 및 제약 |
|---|---|---|---|
| `1` | `Node` | `node-id` | `Endpoint`가 있으면 필수 |
| `2` | `Group` | `group-id` | `Endpoint`가 없으면 필수. 최솟값 `1` |
| `3` | `Endpoint` | `endpoint-no` | `Group`이 없으면 필수 |
| `4` | `Cluster` | `cluster-id` | 선택 사항 |

### `Binding` 속성

| 항목 | 정의 |
|---|---|
| ID | `0x0000` |
| 이름 | `Binding` |
| 타입 | `list` |
| 항목 타입 | `TargetStruct` |
| 기본값 | `empty` |
| 적합성 | 필수 |
| 읽기 | 허용, `readPrivilege="view"` |
| 쓰기 | 허용, `writePrivilege="manage"` |
| 범위 | `fabricScoped="true"` |
| 영속성 | `persistence="nonVolatile"` |

제공된 XML의 속성 제약에는 비어 있는 `desc`만 있으며, 구체적인 목록 크기는 명시되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml`

### 클러스터 및 속성

| 항목 | SDK 정의 |
|---|---|
| 이름 | `Binding` |
| code | `0x001e` |
| domain | `General` |
| define | `BINDING_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `code="0xFFFD"`, `side="either"`, `value="1"` |

`Binding` 속성은 다음과 같이 정의된다.

- `side="server"`
- `code="0x0000"`
- `define="BINDING_LIST"`
- `type="array"`, `entryType="TargetStruct"`
- `writable="true"`
- 쓰기 접근 권한: `role="manage"`
- `mandatoryConform`

### `TargetStruct` 표현

`TargetStruct`는 `isFabricScoped="true"`이며, 다음 필드를 가진다.

| fieldId | 이름 | SDK 타입 | 설정 |
|---|---|---|---|
| `1` | `Node` | `node_id` | `optional="true"` |
| `2` | `Group` | `group_id` | `optional="true"`, `min="1"` |
| `3` | `Endpoint` | `endpoint_no` | `optional="true"` |
| `4` | `Cluster` | `cluster_id` | `optional="true"` |

스펙의 조건부 필수 규칙과 달리 SDK XML에서는 네 필드 모두 `optional="true"`로 표현된다. 필드 조합에 대한 구현 검증은 `BindingCluster::IsValidBinding`에서 수행한다.

파일에는 Alchemy로 생성되었으며 직접 수정하지 말라는 주석이 있다. 생성 원본은 `src/data_model/Binding-Cluster.adoc`이다.

## 구현

### `BindingCluster`

출처:

- `src/app/clusters/bindings/BindingCluster.h`
- `src/app/clusters/bindings/BindingCluster.cpp`

`BindingCluster`는 `DefaultServerCluster`를 상속한다. `Context`를 통해 다음 의존성을 주입받는다.

| 멤버 | 타입 |
|---|---|
| `bindingTable` | `Binding::Table &` |
| `bindingManager` | `Binding::Manager &` |
| `platformManager` | `DeviceLayer::PlatformManager &` |

사용하는 타입 별칭은 다음과 같다.

```cpp
using TargetStructType         = Binding::Structs::TargetStruct::Type;
using DecodableBindingListType = Binding::Attributes::Binding::TypeInfo::DecodableType;
```

#### 바인딩 검증

`BindingCluster::IsValidBinding`은 다음 조합을 허용한다.

- 유니캐스트:
  - `entry.group`이 없고 `entry.endpoint`, `entry.node`가 있어야 한다.
  - `entry.cluster`가 없으면 유효하다.
  - `entry.cluster`가 있으면 `mContext->provider.ClientClusters`로 얻은 로컬 엔드포인트의 클라이언트 클러스터 중 일치하는 값이 있어야 한다.
- 멀티캐스트:
  - `entry.endpoint`, `entry.node`가 없고 `entry.group`이 있어야 한다.

`IsValidBinding` 자체에는 `Group`의 최솟값을 검사하는 코드가 없다. 또한 클라이언트 클러스터를 통한 검증에는 정확성을 확인하는 `TODO` 주석이 있다.

`BindingCluster::CheckValidBindingList`는 다음을 검사한다.

1. 모든 항목에 대해 `IsValidBinding` 호출.
2. 목록 순회 상태 확인.
3. 현재 접근 fabric과 로컬 엔드포인트의 기존 항목을 대체한 뒤 전체 테이블 용량을 초과하는지 확인.

용량 검사식은 다음과 같다.

```cpp
mClusterContext.bindingTable.Size() - oldListSize + listSize <= Binding::Table::kMaxBindingEntries
```

유효하지 않은 항목은 `ConstraintError`, 용량 초과는 `ResourceExhausted`로 반환한다.

#### 속성 읽기

`BindingCluster::ReadAttribute`의 동작은 다음과 같다.

| 속성 | 동작 |
|---|---|
| `Binding::Attributes::Binding::Id` | 요청 엔드포인트와 `entry.local`이 일치하는 항목을 목록으로 인코딩 |
| `Globals::Attributes::FeatureMap::Id` | `uint32_t` 값 `0` 반환 |
| `Globals::Attributes::ClusterRevision::Id` | `Binding::kRevision` 반환 |
| 그 외 | `UnsupportedAttribute` 반환 |

바인딩 항목의 인코딩은 유형별로 다르다.

- `Binding::MATTER_UNICAST_BINDING`: `node`, `endpoint` 설정, `group`은 `NullOptional`.
- `Binding::MATTER_MULTICAST_BINDING`: `group` 설정, `node`, `endpoint`는 `NullOptional`.
- 두 유형 모두 `cluster`, `fabricIndex`를 포함한다.

이 함수의 반복문에서 직접 검사하는 범위 조건은 로컬 엔드포인트 일치 여부다.

#### 속성 쓰기

`BindingCluster::WriteAttribute`는 `Binding::Attributes::Binding::Id`에 대해 다음 작업을 지원한다.

| 작업 | 처리 |
|---|---|
| 목록 연산이 아닌 쓰기 또는 `ReplaceAll` | 새 목록 디코딩·검증 → 현재 접근 fabric과 엔드포인트의 기존 항목 제거 → 새 항목 추가 |
| `AppendItem` | 단일 항목 디코딩 → `IsValidBinding` 검사 → 항목 추가 |
| 그 외 목록 연산 | `UnsupportedWrite` 반환 |
| 그 외 속성 | `UnsupportedWrite` 반환 |

기존 유니캐스트 항목을 제거하기 전에는 `UnicastBindingRemoved`를 호출한다.

`BindingCluster::CreateBindingEntry`는 `entry.group` 유무에 따라 `Binding::TableEntry`를 생성하고, `mClusterContext.bindingManager.AddBindingEntry`에 전달한다.

#### 변경 알림 및 속성 메타데이터

- 목록 연산이 아닌 전체 쓰기에서는 새 항목 추가 루프 후 `NotifyBindingsChanged`를 호출한다.
- 목록 쓰기에서는 `ListAttributeWriteNotification`이 `DataModel::ListWriteOperation::kListWriteSuccess`를 받으면 알림을 보낸다.
- `NotifyBindingsChanged`는 접근 fabric의 `fabricIndex`를 담은 `DeviceLayer::DeviceEventType::kBindingsChangedViaCluster` 이벤트를 `PostEvent`로 게시한다.
- `Attributes`는 `Binding::Attributes::kMandatoryMetadata`를 `AttributeListBuilder`에 추가한다.

### `Binding::Table`과 `TableEntry`

출처:

- `src/app/clusters/bindings/binding-table.h`
- `src/app/clusters/bindings/binding-table.cpp`

#### 항목 구조

`EntryType`은 다음 값을 정의한다.

| 이름 | 값 |
|---|---|
| `MATTER_UNUSED_BINDING` | `0` |
| `MATTER_UNICAST_BINDING` | `1` |
| `MATTER_MULTICAST_BINDING` | `3` |

`TableEntry`에는 `type`, `fabricIndex`, `local`, `clusterId`, `remote`와 `nodeId` 또는 `groupId`를 저장하는 union이 있다.

- `clusterId` 타입은 `std::optional<chip::ClusterId>`다.
- `TableEntry::ForNode`는 유니캐스트 항목을 생성한다.
- `TableEntry::ForGroup`은 멀티캐스트 항목을 생성한다.
- 멀티캐스트 생성자는 `remote`를 `kInvalidEndpointId`로 설정한다.

#### 용량과 주요 API

```cpp
static constexpr size_t kMaxBindingEntries =
    static_cast<size_t>(CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC) * CHIP_CONFIG_MAX_FABRICS;
```

| API | 역할 |
|---|---|
| `Add` | 항목 추가 및 저장 |
| `GetAt` | 인덱스에 해당하는 항목 반환 |
| `RemoveAt` | 항목 제거 후 전달된 반복자를 다음 항목으로 이동 |
| `Size` | 용량이 아닌 활성 항목 수 반환 |
| `SetPersistentStorage` | 저장소 설정 |
| `LoadFromStorage` | 저장된 목록 복원 |
| `GetInstance` | `Manager::GetInstance().GetBindingTable()` 반환 |

내부적으로 고정 배열 `mBindingTable`과 다음 인덱스 배열 `mNextIndex`를 사용한다. 목록 끝 표시는 `kNextNullIndex = 255`다.

#### 영구 저장

- 저장 형식은 TLV 구조체이며, `kStorageVersion = 1`이다.
- 목록 정보에는 저장 버전과 첫 항목 인덱스를 저장한다.
- 각 항목에는 fabric, 로컬 엔드포인트, 선택적 클러스터, 목적지 정보, 다음 항목 인덱스를 저장한다.
- 저장 키는 `DefaultStorageKeyAllocator::BindingTable()`과 `DefaultStorageKeyAllocator::BindingTableEntry(index)`로 얻는다.
- `LoadFromStorage`는 버전 불일치 시 `CHIP_ERROR_VERSION_MISMATCH`를 반환한다.
- `LoadEntryFromStorage`는 배열 접근 전에 `index < kMaxBindingEntries`를 검사한다.

`Table::Add`는 `MATTER_UNUSED_BINDING` 입력을 거부하고, 빈 슬롯이 없으면 `CHIP_ERROR_NO_MEMORY`를 반환한다. 저장 실패 시 새 슬롯의 `type`을 `MATTER_UNUSED_BINDING`으로 되돌린다.

`Table::RemoveAt`은 이전 항목 또는 목록 머리의 저장 정보 갱신에 성공하면 제거가 반영된 것으로 취급한다. 이후 항목 저장 키 삭제가 실패하면 오류를 로그로 기록한다.

### `Binding::Manager`

출처:

- `src/app/clusters/bindings/BindingManager.h`
- `src/app/clusters/bindings/BindingManager.cpp`

`Manager`는 `chip::FabricTable::Delegate`를 상속하며, 바인딩 테이블과 대기 알림을 관리한다.

#### 초기화

`ManagerInitParams`는 다음 설정을 가진다.

| 멤버 | 기본값 |
|---|---|
| `mFabricTable` | `nullptr` |
| `mCASESessionManager` | `nullptr` |
| `mStorage` | `nullptr` |
| `mEstablishConnectionOnInit` | `true` |

`Manager::Init`은 세 포인터가 모두 설정되어 있는지 검사하고, 저장소와 fabric delegate를 등록한 뒤 `LoadFromStorage`를 호출한다.

- 로드 실패는 로그로 기록하며, 이 경우에도 `Init`은 `CHIP_NO_ERROR`를 반환한다.
- 로드 성공 후 `mEstablishConnectionOnInit`이 `true`이면 기존 유니캐스트 항목의 연결을 시도한다.
- 초기 연결 실패는 무시하며, 필요할 때 다시 연결할 수 있도록 한다.

#### 항목 추가와 연결

`Manager::AddBindingEntry`는 다음 순서로 처리한다.

1. `mBindingTable.Add` 호출.
2. `CHIP_ERROR_NO_MEMORY`를 `ResourceExhausted`로 변환.
3. 유니캐스트 항목이면 `UnicastBindingCreated` 호출.
4. 연결 실패는 로그로 기록하되, 항목 추가가 성공했다면 `CHIP_NO_ERROR` 반환.

외부의 `AddBindingEntry` 함수는 `Binding::Manager::GetInstance().AddBindingEntry`로 위임한다.

`EstablishConnection`은 `FindOrEstablishSession`을 호출한다. 동기적으로 `CHIP_ERROR_NO_MEMORY`가 발생하면 `FindLRUConnectPeer`로 선택한 peer의 대기 항목을 제거하고 다시 시도한다. 해당 재시도 로직에는 현재 구현과의 정합성에 관한 `TODO(#22173)` 주석이 있다.

#### 바인딩 대상 변경 알림

`Manager::NotifyBoundClusterChanged`는 다음 조건에 맞는 항목을 처리한다.

```cpp
iter->local == endpoint && (iter->clusterId.value_or(cluster) == cluster)
```

즉, 로컬 엔드포인트가 일치하고 `clusterId`가 없거나 요청된 `cluster`와 일치해야 한다.

- 유니캐스트: 대기 알림을 등록하고 연결을 요청한다.
- 멀티캐스트: `peer_device`에 `nullptr`를 전달하여 핸들러를 호출한다.
- 활성 세션이 있는 유니캐스트와 멀티캐스트는 함수가 반환되기 전에 핸들러가 호출된다.
- 활성 세션이 없는 유니캐스트는 연결 완료 후 핸들러가 호출된다.

애플리케이션은 `RegisterBoundDeviceChangedHandler`로 다음 콜백을 등록한다.

```cpp
using BoundDeviceChangedHandler = void (*)(const TableEntry & binding, OperationalDeviceProxy * peer_device, void * context);
```

전송할 내용은 애플리케이션이 결정한다. 헤더 주석은 전달된 `SessionHandler` 포인터를 핸들러가 보관해서는 안 된다고 명시한다.

`RegisterBoundDeviceContextReleaseHandler`는 알림 컨텍스트가 더 이상 필요하지 않을 때 호출할 해제 핸들러를 등록한다.

#### 제거 처리

- `UnicastBindingRemoved`: 해당 바인딩 인덱스의 대기 알림 제거.
- `OnFabricRemoved`: 해당 fabric의 테이블 항목 제거 후 `FabricRemoved` 호출.
- `FabricRemoved`: 해당 fabric의 대기 알림 제거 및 `ReleaseSessionsForFabric` 호출.

### `PendingNotificationMap`

출처:

- `src/app/clusters/bindings/PendingNotificationMap.h`
- `src/app/clusters/bindings/PendingNotificationMap.cpp`

`PendingNotificationMap`은 바인딩 인덱스와 `PendingNotificationContext`를 연결한다.

- 최대 대기 알림 수는 `Table::kMaxBindingEntries`와 같다.
- `AddPendingNotification`은 같은 `bindingEntryId`의 기존 알림을 먼저 제거하고 새 알림을 끝에 추가한다.
- 용량이 가득 차면 `CHIP_ERROR_NO_MEMORY`를 반환한다.
- `RemoveEntry`, `RemoveAllEntriesForNode`, `RemoveAllEntriesForFabric`으로 항목을 제거한다.
- `FindLRUConnectPeer`는 동일한 fabric과 노드를 가진 유니캐스트 항목을 묶고, 각 peer의 마지막 알림 중 가장 앞에 있는 peer를 선택한다. 대상이 없으면 `CHIP_ERROR_NOT_FOUND`를 반환한다.

`PendingNotificationContext`는 소비자 수를 관리한다. `DecrementConsumersNumber`로 수가 `0`이 되면 등록된 해제 핸들러를 호출하고 자신을 삭제한다.

### 코드 생성 통합

출처: `src/app/clusters/bindings/CodegenIntegration.cpp`

- `kBindingFixedClusterCount`는 `Binding::StaticApplicationConfig::kFixedClusterConfig.size()`에서 얻는다.
- `kBindingMaxClusterCount`는 고정 개수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.
- `gServers`는 `LazyRegisteredServerCluster<BindingCluster>` 배열이다.
- `IntegrationDelegate`는 `Binding::Table::GetInstance()`, `Binding::Manager::GetInstance()`, `DeviceLayer::PlatformMgr()`를 주입하여 서버를 생성한다.

| 콜백 | 처리 |
|---|---|
| `MatterBindingClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterBindingClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `MatterBindingPluginServerInitCallback` | 빈 구현 |
| `MatterBindingPluginServerShutdownCallback` | 빈 구현 |

서버 등록 시 `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`다.

## 관련 문서

### 업그레이드 참고 사항

출처: `src/app/clusters/bindings/README.md`

바인딩 테이블 크기 설정은 다음과 같이 변경되었다.

| 구분 | 설정 |
|---|---|
| 이전 | `MATTER_BINDING_TABLE_SIZE` |
| 변경 후 | `CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC * CHIP_CONFIG_MAX_FABRICS` |

이전 값의 기본 정의 위치는 `src/app/util/config.h`였으며, 변경된 설정의 정의 위치는 `src/lib/core/CHIPConfig.h`다.

## 관련 페이지

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
