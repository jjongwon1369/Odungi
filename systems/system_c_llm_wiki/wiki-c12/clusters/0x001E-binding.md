---
entity: Binding
ids: ['0x001E']
source_paths: ['data_model/1.7/clusters/Binding-Cluster.xml', 'src/app/clusters/bindings/BindingCluster.cpp', 'src/app/clusters/bindings/BindingCluster.h', 'src/app/clusters/bindings/BindingManager.cpp', 'src/app/clusters/bindings/BindingManager.h', 'src/app/clusters/bindings/CodegenIntegration.cpp', 'src/app/clusters/bindings/PendingNotificationMap.cpp', 'src/app/clusters/bindings/PendingNotificationMap.h', 'src/app/clusters/bindings/README.md', 'src/app/clusters/bindings/binding-table.cpp', 'src/app/clusters/bindings/binding-table.h', 'src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Binding

## 개요

`Binding`은 바인딩 테이블을 관리하는 클러스터이다. SDK 설명에서는 바인딩 테이블을 지원하던 Zigbee Device Object (ZDO)의 기능을 대체하는 용도로 설명한다.

- 클러스터 ID: 스펙 `0x001E`, SDK `0x001e`
- 리비전: `1`
- 바인딩 대상: 개별 노드의 엔드포인트 또는 그룹
- 주요 속성: `TargetStruct` 목록인 `Binding`
- 구현 구성:
  - `BindingCluster`: 속성 읽기·쓰기와 입력 검증
  - `Binding::Manager`: 유니캐스트 연결과 애플리케이션 콜백 관리
  - `Binding::Table`: 바인딩 항목과 영구 저장소 관리
  - `PendingNotificationMap`: 연결 대기 중인 알림과 컨텍스트 수명 관리

## 스펙

출처: `data_model/1.7/clusters/Binding-Cluster.xml`

### 클러스터 정의

| 항목 | 값 |
|---|---|
| XML 클러스터 이름 | `Binding Cluster` |
| 클러스터 이름 | `Binding` |
| ID | `0x001E` |
| revision | `1` |
| revisionHistory | `Initial revision` |
| hierarchy | `base` |
| role | `utility` |
| picsCode | `BIND` |
| scope | `Endpoint` |

### `TargetStruct`

`TargetStruct`는 `fabricScoped="true"`인 구조체이다.

| 필드 ID | 이름 | 타입 | 적합성 조건 | 제약 |
|---|---|---|---|---|
| `1` | `Node` | `node-id` | `Endpoint`가 있으면 필수 | — |
| `2` | `Group` | `group-id` | `Endpoint`가 없으면 필수 | 최솟값 `1` |
| `3` | `Endpoint` | `endpoint-no` | `Group`이 없으면 필수 | — |
| `4` | `Cluster` | `cluster-id` | 선택 | — |

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
| 패브릭 범위 | `fabricScoped="true"` |
| 영속성 | `persistence="nonVolatile"` |

제공된 XML에는 명령과 이벤트 정의가 없다. `Binding`의 목록 제약에는 빈 `desc`만 있으며, 수치로 된 최대 항목 수는 명시되지 않는다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml`

이 파일은 Alchemy 생성 파일이며, 주석에 `DO NOT EDIT`가 명시되어 있다. 생성 원본 경로는 `src/data_model/Binding-Cluster.adoc`이다.

### 클러스터 및 속성 메타데이터

| 항목 | SDK 정의 |
|---|---|
| 클러스터 이름 | `Binding` |
| 클러스터 코드 | `0x001e` |
| domain | `General` |
| define | `BINDING_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | 코드 `0xFFFD`, `side="either"`, 값 `1` |
| 속성 이름 | `Binding` |
| 속성 코드 | `0x0000` |
| 속성 define | `BINDING_LIST` |
| 속성 위치 | `side="server"` |
| 속성 타입 | `array`, `entryType="TargetStruct"` |
| 쓰기 | `writable="true"`, 권한 `manage` |
| 적합성 | 필수 |

### `TargetStruct` 매핑

SDK의 `TargetStruct`는 `isFabricScoped="true"`이며, 다음 필드가 모두 `optional="true"`로 선언된다.

| fieldId | 이름 | SDK 타입 | 추가 제약 |
|---|---|---|---|
| `1` | `Node` | `node_id` | — |
| `2` | `Group` | `group_id` | `min="1"` |
| `3` | `Endpoint` | `endpoint_no` | — |
| `4` | `Cluster` | `cluster_id` | — |

스펙 XML의 필드 간 조건부 필수 관계는 이 SDK XML의 `optional` 선언만으로는 표현되지 않는다. 제공된 서버 구현은 `IsValidBinding`에서 필드 조합을 검사한다.

## 구현

### 서버 클래스와 의존성

출처:

- `src/app/clusters/bindings/BindingCluster.h`
- `src/app/clusters/bindings/BindingCluster.cpp`

`BindingCluster`는 `DefaultServerCluster`를 상속하며, 생성 시 `endpointId`와 `Binding::Id`로 클러스터 경로를 구성한다.

`Context`로 주입받는 의존성은 다음과 같다.

| 멤버 | 타입 |
|---|---|
| `bindingTable` | `Binding::Table &` |
| `bindingManager` | `Binding::Manager &` |
| `platformManager` | `DeviceLayer::PlatformManager &` |

사용하는 타입 별칭:

```cpp
using TargetStructType         = Binding::Structs::TargetStruct::Type;
using DecodableBindingListType = Binding::Attributes::Binding::TypeInfo::DecodableType;
```

### 바인딩 검증

`BindingCluster::IsValidBinding`은 다음 조합을 허용한다.

- 유니캐스트:
  - `entry.group`이 없다.
  - `entry.endpoint`와 `entry.node`가 있다.
  - `entry.cluster`가 없으면 유효하다.
  - `entry.cluster`가 있으면 `mContext->provider.ClientClusters`로 조회한 로컬 엔드포인트의 클라이언트 클러스터 중 일치하는 항목이 있어야 한다.
- 멀티캐스트:
  - `entry.endpoint`와 `entry.node`가 없다.
  - `entry.group`이 있다.

클라이언트 클러스터 조회 실패 또는 허용되지 않는 필드 조합은 검증 실패로 처리한다. 클라이언트 클러스터 검증 부분에는 검증의 적절성을 확인하는 `TODO`가 남아 있다.

`BindingCluster::CheckValidBindingList`는 다음을 수행한다.

1. 각 항목을 `IsValidBinding`으로 검사한다. 실패하면 `ConstraintError`를 반환한다.
2. 목록 순회 후 디코딩 상태를 검사한다.
3. 현재 엔드포인트와 접근 패브릭에 속한 기존 항목 수를 계산한다.
4. 교체 후 전체 항목 수가 `Binding::Table::kMaxBindingEntries`를 넘으면 `ResourceExhausted`를 반환한다.

용량 검사는 다음 계산에 기반한다.

```cpp
mClusterContext.bindingTable.Size() - oldListSize + listSize <= Binding::Table::kMaxBindingEntries
```

### 속성 읽기

`BindingCluster::ReadAttribute`의 처리 대상은 다음과 같다.

| 속성 식별자 | 동작 |
|---|---|
| `Binding::Attributes::Binding::Id` | 요청 엔드포인트와 `entry.local`이 같은 항목을 목록으로 인코딩 |
| `Globals::Attributes::FeatureMap::Id` | `uint32_t` 값 `0` 인코딩 |
| `Globals::Attributes::ClusterRevision::Id` | `Binding::kRevision` 인코딩 |
| 그 외 | `UnsupportedAttribute` 반환 |

바인딩 항목은 다음과 같이 변환된다.

| 테이블 항목 타입 | 인코딩되는 주요 필드 |
|---|---|
| `Binding::MATTER_UNICAST_BINDING` | `node`, `endpoint`, 선택적 `cluster`, `fabricIndex`; `group`은 `NullOptional` |
| `Binding::MATTER_MULTICAST_BINDING` | `group`, 선택적 `cluster`, `fabricIndex`; `node`와 `endpoint`는 `NullOptional` |

`BindingCluster::Attributes`는 `AttributeListBuilder`를 사용하여 `Binding::Attributes::kMandatoryMetadata`를 추가한다.

### 속성 쓰기와 변경 통지

`BindingCluster::WriteAttribute`는 `Binding::Attributes::Binding::Id`에 대해 다음 쓰기를 지원한다.

| 쓰기 형태 | 처리 |
|---|---|
| 목록 연산이 아닌 쓰기 또는 `ReplaceAll` | 전체 목록 디코딩·검증 후, 현재 접근 패브릭과 엔드포인트의 기존 항목을 제거하고 새 항목 추가 |
| `AppendItem` | 단일 `TargetStructType` 디코딩·검증 후 추가 |
| 그 외 목록 연산 또는 속성 | `UnsupportedWrite` 반환 |

전체 교체에서 유니캐스트 항목을 제거하기 전에는 `UnicastBindingRemoved`를 호출한다. 새 항목은 `CreateBindingEntry`가 `Binding::TableEntry`로 변환한 뒤 `bindingManager.AddBindingEntry`에 전달한다.

변경 통지는 다음 경로에서 발생한다.

- 목록 연산이 아닌 쓰기: 새 항목 추가 루프 이후 `NotifyBindingsChanged` 호출
- 목록 쓰기 성공: `ListAttributeWriteNotification`이 `DataModel::ListWriteOperation::kListWriteSuccess`를 받으면 호출

`NotifyBindingsChanged`는 접근 패브릭의 `fabricIndex`를 담은 `DeviceLayer::DeviceEventType::kBindingsChangedViaCluster` 이벤트를 `platformManager.PostEvent`로 게시한다.

전체 교체는 사전 검증 후 기존 항목을 제거하고 새 항목을 순차적으로 추가한다. 제공된 함수에는 이 전체 과정을 되돌리는 롤백 처리가 없다.

### 연결 및 애플리케이션 알림 관리

출처:

- `src/app/clusters/bindings/BindingManager.h`
- `src/app/clusters/bindings/BindingManager.cpp`

`Binding::Manager`는 `chip::FabricTable::Delegate`를 상속한다. `GetInstance`는 정적 인스턴스 `sBindingManager`를 반환하며, `GetBindingTable`은 내부 테이블을 제공한다.

#### 초기화

`ManagerInitParams`의 구성:

| 멤버 | 타입 | 기본값 |
|---|---|---|
| `mFabricTable` | `FabricTable *` | `nullptr` |
| `mCASESessionManager` | `CASESessionManager *` | `nullptr` |
| `mStorage` | `PersistentStorageDelegate *` | `nullptr` |
| `mEstablishConnectionOnInit` | `bool` | `true` |

`Manager::Init`은 세 포인터가 모두 유효한지 검사한다. 누락된 경우 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.

초기화 과정에서는 영구 저장소를 설정하고 패브릭 위임자를 등록한 뒤 `LoadFromStorage`를 호출한다. 저장소 로드 실패는 로그로 기록하며, 이 경우에도 `Init`은 `CHIP_NO_ERROR`를 반환한다.

로드에 성공하고 `mEstablishConnectionOnInit`이 `true`이면 기존 유니캐스트 항목에 대해 연결을 시도한다.

#### 항목 추가와 연결

- `Manager::AddBindingEntry`는 먼저 `mBindingTable.Add`를 호출한다.
- 테이블 공간 부족으로 발생한 `CHIP_ERROR_NO_MEMORY`는 `ResourceExhausted`로 변환한다.
- 유니캐스트 항목이면 `UnicastBindingCreated`를 통해 연결을 시도한다.
- 항목 추가 후 연결이 실패해도 오류를 로그로 남기고 `CHIP_NO_ERROR`를 반환한다. 연결은 필요할 때 다시 시도한다.
- 네임스페이스 수준의 `AddBindingEntry`는 `Binding::Manager::GetInstance().AddBindingEntry`에 위임한다.

`Manager::EstablishConnection`은 `FindOrEstablishSession`을 사용한다. 동기 연결 실패가 `CHIP_ERROR_NO_MEMORY`이면 `FindLRUConnectPeer`로 선택한 피어의 대기 알림을 제거한 후 재시도한다.

각 연결 요청은 별도의 `ConnectionCallback`을 사용하며, 성공·실패 콜백 실행 후 해당 객체를 삭제한다. 연결 실패와 재시도 로직에는 `TODO(#22173)`이 남아 있다.

#### 변경 알림과 콜백

`RegisterBoundDeviceChangedHandler`로 등록하는 콜백 타입:

```cpp
using BoundDeviceChangedHandler = void (*)(const TableEntry & binding, OperationalDeviceProxy * peer_device, void * context);
```

`Manager::NotifyBoundClusterChanged`는 다음 조건에 맞는 항목을 순회한다.

```cpp
iter->local == endpoint && (iter->clusterId.value_or(cluster) == cluster)
```

따라서 `clusterId`가 없는 항목도 전달된 `cluster`에 대해 일치한다.

- 유니캐스트: 대기 알림을 등록하고 연결을 요청한다. 연결이 준비되면 `OperationalDeviceProxy`와 함께 콜백을 호출한다.
- 멀티캐스트: `peer_device`에 `nullptr`를 전달하여 콜백을 호출한다.
- 헤더 설명상 활성 세션이 있는 유니캐스트와 멀티캐스트의 콜백은 함수 반환 전에 호출된다.
- 전송할 내용은 애플리케이션이 결정한다.

컨텍스트 해제 콜백은 `RegisterBoundDeviceContextReleaseHandler`로 등록한다.

#### 패브릭 제거

`OnFabricRemoved`는 해당 `fabricIndex`의 테이블 항목을 제거한 후 `FabricRemoved`를 호출한다.

`FabricRemoved`는 해당 패브릭의 대기 알림을 제거하고 `ReleaseSessionsForFabric`을 호출한다. 이 세션 해제 책임과 관련하여 `TODO(#18436)`이 남아 있다.

### 대기 알림과 컨텍스트 수명

출처:

- `src/app/clusters/bindings/PendingNotificationMap.h`
- `src/app/clusters/bindings/PendingNotificationMap.cpp`

`PendingNotificationMap`의 최대 대기 알림 수는 다음과 같다.

```cpp
static constexpr uint8_t kMaxPendingNotifications = Table::kMaxBindingEntries;
```

주요 동작:

| 함수 | 동작 |
|---|---|
| `AddPendingNotification` | 같은 `bindingEntryId`의 기존 알림을 제거한 후 새 알림을 끝에 추가 |
| `RemoveEntry` | 지정된 바인딩 항목의 알림 제거 |
| `RemoveAllEntriesForNode` | 지정된 `ScopedNodeId`의 알림 제거 |
| `RemoveAllEntriesForFabric` | 지정된 패브릭의 알림 제거 |
| `FindLRUConnectPeer` | 피어별 마지막 등장 위치를 비교하여 가장 오래된 피어 선택 |

`AddPendingNotification`은 용량이 가득 차면 `CHIP_ERROR_NO_MEMORY`를 반환한다. `FindLRUConnectPeer`는 후보가 없으면 `CHIP_ERROR_NOT_FOUND`를 반환한다.

`PendingNotificationContext`는 소비자 수를 관리한다.

- 알림이 컨텍스트를 참조하면 `IncrementConsumersNumber`를 호출한다.
- 참조를 제거하면 `DecrementConsumersNumber`를 호출한다.
- 소비자 수가 `0`이 되면 등록된 `PendingNotificationContextReleaseHandler`를 호출하고 컨텍스트 객체를 삭제한다.

### 바인딩 테이블과 영구 저장

출처:

- `src/app/clusters/bindings/binding-table.h`
- `src/app/clusters/bindings/binding-table.cpp`

#### 항목 타입과 데이터

| `EntryType` | 값 | 의미 |
|---|---|---|
| `MATTER_UNUSED_BINDING` | `0` | 사용하지 않는 항목 |
| `MATTER_UNICAST_BINDING` | `1` | 유니캐스트 바인딩 |
| `MATTER_MULTICAST_BINDING` | `3` | 멀티캐스트 바인딩 |

`TableEntry`에는 다음 정보가 저장된다.

- `type`
- `fabricIndex`
- 로컬 엔드포인트 `local`
- 선택적 `clusterId`
- 원격 엔드포인트 `remote`
- 공용체의 `nodeId` 또는 `groupId`

`TableEntry::ForNode`와 `TableEntry::ForGroup`으로 각 대상 유형의 항목을 생성할 수 있다. 그룹 항목의 `remote`는 `kInvalidEndpointId`로 설정된다.

#### 용량과 순회

```cpp
static constexpr size_t kMaxBindingEntries =
    static_cast<size_t>(CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC) * CHIP_CONFIG_MAX_FABRICS;
```

`Table`은 고정 배열과 다음 항목 인덱스를 사용하여 목록을 구성한다.

- `Size`는 최대 용량이 아니라 활성 항목 수를 반환한다.
- `RemoveAt`은 호출 후 반복자를 다음 항목으로 이동시킨다.
- `GetNextAvaiableIndex`는 사용하지 않는 항목을 검색한다.
- 목록 종료 표식인 `kNextNullIndex`는 `255`이다.
- `Table::GetInstance`는 `Manager::GetInstance().GetBindingTable()`에 위임한다.

#### 저장 형식과 오류 처리

저장은 TLV 구조체를 사용하며, `kStorageVersion`은 `1`이다.

| 저장 대상 | 저장 키 생성 함수 | 주요 내용 |
|---|---|---|
| 목록 정보 | `DefaultStorageKeyAllocator::BindingTable()` | `kTagStorageVersion`, `kTagHead` |
| 개별 항목 | `DefaultStorageKeyAllocator::BindingTableEntry(index)` | `kTagFabricIndex`, `kTagLocalEndpoint`, 선택적 `kTagCluster`, 대상 정보, `kTagNextEntry` |

대상 정보에는 유니캐스트의 `kTagRemoteEndpoint`와 `kTagNodeId`, 또는 멀티캐스트의 `kTagGroupId`가 포함된다.

- `Table::Add`는 `MATTER_UNUSED_BINDING` 입력을 거부하고, 빈 슬롯이 없으면 `CHIP_ERROR_NO_MEMORY`를 반환한다.
- 추가 중 저장이 실패하면 새 슬롯의 `type`을 `MATTER_UNUSED_BINDING`으로 되돌린다.
- `LoadFromStorage`는 저장 버전이 다르면 `CHIP_ERROR_VERSION_MISMATCH`를 반환한다.
- `LoadEntryFromStorage`는 고정 배열에 접근하기 전에 `index < kMaxBindingEntries`를 검사한다.
- `RemoveAt`은 앞 항목의 연결 또는 목록 머리 정보를 저장한 뒤 항목 저장 키를 삭제한다. 키 삭제만 실패한 경우에는 로그를 남기고 메모리상의 제거를 진행한다.

### 코드 생성 통합

출처: `src/app/clusters/bindings/CodegenIntegration.cpp`

`gServers`는 `LazyRegisteredServerCluster<BindingCluster>` 배열이다.

- `kBindingFixedClusterCount`: `Binding::StaticApplicationConfig::kFixedClusterConfig.size()`
- `kBindingMaxClusterCount`: `kBindingFixedClusterCount + CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`

`IntegrationDelegate`는 클러스터 인스턴스 생성·조회·해제를 담당한다. 생성 시 다음 의존성을 주입한다.

- `Binding::Table::GetInstance()`
- `Binding::Manager::GetInstance()`
- `DeviceLayer::PlatformMgr()`

| 콜백 | 동작 |
|---|---|
| `MatterBindingClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출 |
| `MatterBindingClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `MatterBindingPluginServerInitCallback` | 빈 구현 |
| `MatterBindingPluginServerShutdownCallback` | 빈 구현 |

등록 시 `fetchFeatureMap`과 `fetchOptionalAttributes`는 모두 `false`로 설정된다.

## 관련 문서

### 업그레이드 참고 사항

출처: `src/app/clusters/bindings/README.md`

바인딩 테이블 크기 설정이 다음과 같이 변경되었다.

| 구분 | 설정 |
|---|---|
| 이전 | `MATTER_BINDING_TABLE_SIZE` |
| 변경 후 | `CHIP_CONFIG_MAX_BINDING_ENTRIES_PER_FABRIC * CHIP_CONFIG_MAX_FABRICS` |

이전 기본 정의 위치는 `src/app/util/config.h`이며, 변경된 설정의 정의 위치는 `src/lib/core/CHIPConfig.h`이다.

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
