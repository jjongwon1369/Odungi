---
entity: HEPA Filter Monitoring
ids: ['0x0071', '0x0072']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-server.h', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.h', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp', 'src/app/clusters/resource-monitoring-server/README.md', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp', 'data_model/1.7/clusters/ResourceMonitoring.xml', 'zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h', 'zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 개요

**HEPA Filter Monitoring**은 디바이스의 HEPA 필터를 모니터링하기 위한 속성과 명령을 제공하는 Resource Monitoring aliased cluster입니다.

- Cluster ID: `0x0071`
- Define: `HEPA_FILTER_MONITORING_CLUSTER`
- Domain: `Measurement & Sensing`
- Description: `Attributes and commands for monitoring HEPA filters in a device`
- Client: 지원
- Server: 지원
- PICS Code: `HEPAFREMON`
- Classification: `base` / `application`
- Scope: `Endpoint`

`Resource Monitoring`은 자체 Cluster ID가 없는 pseudo cluster이며, 다른 클러스터에 alias로 통합됩니다.

## 스펙

스펙 파일: `data_model/1.7/clusters/ResourceMonitoring.xml`

### Feature

| Bit | Code | Name | 설명 | Conformance |
|---:|---|---|---|---|
| 0 | `CON` | `Condition` | 리소스의 상태를 백분율로 모니터링 | Optional |
| 1 | `WRN` | `Warning` | 경고 표시 지원 | Optional |
| 2 | `REP` | `ReplacementProductList` | 교체 제품 목록 지정 지원 | Optional |

### Attributes

| ID | Name | Type | Access | Quality | Conformance |
|---|---|---|---|---|---|
| `0x0000` | `Condition` | `percent` | Read (`view`) | - | `CON` Feature에서 Mandatory |
| `0x0001` | `DegradationDirection` | `DegradationDirectionEnum` | Read (`view`) | `fixed` | `CON` Feature에서 Mandatory |
| `0x0002` | `ChangeIndication` | `ChangeIndicationEnum` | Read (`view`) | - | Mandatory |
| `0x0003` | `InPlaceIndicator` | `bool` | Read (`view`) | - | Optional |
| `0x0004` | `LastChangedTime` | `epoch-s` | Read (`view`), Write (`operate`) | Nullable, `nonVolatile` | Optional |
| `0x0005` | `ReplacementProductList` | `list` | Read (`view`) | `fixed` | `REP` Feature에서 Mandatory |
| `0x0006` | `Medium` | `medium-type` | Read (`view`) | `fixed` | Revision 2 이상에서 Optional, provisional |

`ReplacementProductList`의 최대 항목 수는 5개입니다.

`LastChangedTime`의 기본값은 `null`이며, `epoch-s` 형식입니다.

### `ChangeIndicationEnum`

| 값 | Name | 의미 | Conformance |
|---:|---|---|---|
| 0 | `OK` | 리소스 상태가 양호하며 조치가 필요하지 않음 | Mandatory |
| 1 | `Warning` | 리소스가 곧 소진되어 조치가 필요함 | `WRN` Feature에서 Mandatory |
| 2 | `Critical` | 리소스가 소진되어 즉시 조치가 필요함 | Mandatory |

### `DegradationDirectionEnum`

| 값 | Name | 의미 |
|---:|---|---|
| 0 | `Up` | 리소스 성능 저하가 증가하는 값으로 표시됨 |
| 1 | `Down` | 리소스 성능 저하가 감소하는 값으로 표시됨 |

### `ProductIdentifierTypeEnum`

| 값 | Name | 설명 |
|---:|---|---|
| 0 | `UPC` | 12자리 Universal Product Code |
| 1 | `GTIN-8` | 8자리 Global Trade Item Number |
| 2 | `EAN` | 13자리 European Article Number |
| 3 | `GTIN-14` | 14자리 Global Trade Item Number |
| 4 | `OEM` | Original Equipment Manufacturer 부품 번호 |

### `ReplacementProductStruct`

| Field ID | Name | Type | 제약 |
|---:|---|---|---|
| 0 | `ProductIdentifierType` | `ProductIdentifierTypeEnum` | - |
| 1 | `ProductIdentifierValue` | `string` | 최대 길이 20 |

### Commands

| ID | Name | Direction | Access | Conformance |
|---|---|---|---|---|
| `0x00` | `ResetCondition` | `commandToServer` | Invoke (`operate`) | Optional |

`ResetCondition`은 `Condition` 및 `ChangeIndicator` attributes를 초기 구성 상태의 완전한 리소스 가용성과 사용 준비 상태로 재설정합니다.

## SDK 정의

SDK XML 파일: `src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml`

### Cluster 정의

```xml
<name>HEPA Filter Monitoring</name>
<code>0x0071</code>
<define>HEPA_FILTER_MONITORING_CLUSTER</define>
```

글로벌 attribute로 `0xFFFD`가 정의되어 있으며 값은 `1`입니다.

### Attributes

| ID | Name | Define | SDK Type | 특성 |
|---|---|---|---|---|
| `0x0000` | `Condition` | `CONDITION` | `percent` | `CON` Feature 필요 |
| `0x0001` | `DegradationDirection` | `DEGRADATION_DIRECTION` | `DegradationDirectionEnum` | `CON` Feature 필요, 최대값 `1` |
| `0x0002` | `ChangeIndication` | `CHANGE_INDICATION` | `ChangeIndicationEnum` | 최대값 `2` |
| `0x0003` | `InPlaceIndicator` | `IN_PLACE_INDICATOR` | `boolean` | Optional |
| `0x0004` | `LastChangedTime` | `LAST_CHANGED_TIME` | `epoch_s` | Writable, Nullable, Optional |
| `0x0005` | `ReplacementProductList` | `REPLACEMENT_PRODUCT_LIST` | `array` | `ReplacementProductStruct`, 길이 `5`, `REP` Feature 필요 |

SDK XML에는 `Medium` attribute가 정의되어 있지 않습니다.

### Commands

| ID | Name | Source | 특성 |
|---|---|---|---|
| `0x00` | `ResetCondition` | `client` | Optional |

## 구현

주요 구현 파일:

- `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp`
- `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h`
- `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h`
- `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp`
- `src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h`
- `src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h`

### 공통 구현 구조

`ResourceMonitoringCluster`는 `DefaultServerCluster`를 상속하며, `HEPA Filter Monitoring`과 `Activated Carbon Filter Monitoring`의 공통 구현으로 사용됩니다.

생성자는 다음 값을 받습니다.

- `EndpointId`
- `ClusterId`
- 활성화된 `ResourceMonitoring::Feature`
- `OptionalAttributeSet`
- `DegradationDirectionEnum`
- `ResetCondition` 지원 여부

`ResourceMonitoring::Instance`는 `CodegenResourceMonitoringCluster`를 `RegisteredServerCluster`로 감싸고 delegate를 연결합니다.

### Attribute 읽기와 쓰기

`ResourceMonitoringCluster::ReadAttribute`는 다음 attribute를 처리합니다.

- `ResourceMonitoring::Attributes::Condition::Id`
- `ResourceMonitoring::Attributes::FeatureMap::Id`
- `ResourceMonitoring::Attributes::DegradationDirection::Id`
- `ResourceMonitoring::Attributes::ChangeIndication::Id`
- `ResourceMonitoring::Attributes::InPlaceIndicator::Id`
- `ResourceMonitoring::Attributes::LastChangedTime::Id`
- `ResourceMonitoring::Attributes::ReplacementProductList::Id`
- `ResourceMonitoring::Attributes::ClusterRevision::Id`

`LastChangedTime`은 `ResourceMonitoringCluster::WriteImpl`에서 쓰기를 지원하며, `AttributePersistence`를 통해 저장됩니다. 그 외 쓰기가 지원되지 않는 attribute에는 `UnsupportedWrite`가 반환됩니다.

`ResourceMonitoringCluster::Attributes`는 다음 조건에 따라 optional attribute 목록을 구성합니다.

- `Condition` 및 `DegradationDirection`: `Feature::kCondition`
- `ReplacementProductList`: `Feature::kReplacementProductList`
- `InPlaceIndicator`: `OptionalAttributeSet`
- `LastChangedTime`: `OptionalAttributeSet`

HEPA 구현의 mandatory metadata는 `HepaFilterMonitoring::Attributes::kMandatoryMetadata`를 사용합니다.

### Attribute 업데이트 API

`ResourceMonitoringCluster` 및 `ResourceMonitoring::Instance`는 다음 API를 제공합니다.

```cpp
UpdateCondition(uint8_t newCondition)
UpdateChangeIndication(ResourceMonitoring::ChangeIndicationEnum newChangeIndication)
UpdateInPlaceIndicator(bool newInPlaceIndicator)
UpdateLastChangedTime(DataModel::Nullable<uint32_t> newLastChangedTime)
```

조회 API는 다음과 같습니다.

```cpp
GetCondition()
GetChangeIndication()
GetDegradationDirection()
GetInPlaceIndicator()
GetLastChangedTime()
```

`UpdateChangeIndication`에 `kWarning`을 전달했을 때 `ResourceMonitoring::Feature::kWarning`이 활성화되지 않은 경우 `Status::InvalidValue`를 반환합니다.

`UpdateCondition`과 `UpdateInPlaceIndicator`는 값이 변경된 경우 attribute 변경을 알립니다. HEPA 관련 attribute ID가 `ActivatedCarbonFilterMonitoring`과 동일한지 `static_assert`로 확인합니다.

### `ResetCondition` 처리

`ResourceMonitoringCluster::InvokeCommand`는 `ResourceMonitoring::Commands::ResetCondition::Id`를 수신하면 `ResetCondition`을 호출합니다.

`Delegate::OnResetCondition`의 기본 동작은 다음과 같습니다.

1. `PreResetCondition()` 호출
2. `Condition` Feature가 지원되는 경우 `DegradationDirection`에 따라 `Condition` 재설정
   - `DegradationDirectionEnum::kDown`: `Condition`을 `100`으로 설정
   - `DegradationDirectionEnum::kUp`: `Condition`을 `0`으로 설정
3. `ChangeIndication`을 `ChangeIndicationEnum::kOk`로 설정
4. `LastChangedTime`이 지원되는 경우 현재 Unix time을 설정
5. `PostResetCondition()` 호출

`PreResetCondition()`이 `Status::Success`가 아니면 reset을 수행하지 않습니다. 기본 구현의 `PreResetCondition()`과 `PostResetCondition()`은 모두 `Status::Success`를 반환합니다.

애플리케이션은 다음 메서드를 재정의할 수 있습니다.

```cpp
Init()
OnResetCondition()
PreResetCondition()
PostResetCondition()
```

`Delegate::Init()`은 순수 가상 함수이며 SDK 사용자가 구현해야 합니다.

### `ReplacementProductList`

`ReplacementProductListManager`가 목록을 관리합니다.

- 최대 목록 크기: `5`
- 목록 순회 메서드: `Next(ReplacementProductStruct & item)`
- 순회 초기화 메서드: `Reset()`
- 목록 관리자가 없으면 빈 목록을 반환

`ResourceMonitoring::ReplacementProductStruct`는 `HepaFilterMonitoring::Structs::ReplacementProductStruct::Type`을 기반으로 하며, `ProductIdentifierValue`를 내부 버퍼에 복사합니다.

```cpp
static constexpr size_t kProductIdentifierValueMaxNameLength = 20u;
```

`SetProductIdentifierValue`는 다음 경우 `CHIP_ERROR_INVALID_ARGUMENT`를 반환합니다.

- 입력이 비어 있는 경우
- 입력 크기가 `kProductIdentifierValueMaxNameLength`를 초과하는 경우

### Persistent attribute

`LastChangedTime`은 `AttributePersistence`를 통해 저장되고 시작 시 `LoadPersistentAttributes()`에서 복원됩니다.

`CodegenResourceMonitoringCluster::Startup`은 `SafeAttributePersistenceProvider`에서 `AttributePersistenceProvider`로 저장소 마이그레이션을 수행한 뒤 `ResourceMonitoringCluster::Startup`을 호출합니다.

마이그레이션 대상은 다음입니다.

```cpp
HepaFilterMonitoring::Attributes::LastChangedTime::Id
```

### Codegen integration

`CodegenIntegration.cpp`에는 다음 callback이 정의되어 있습니다.

```cpp
void MatterActivatedCarbonFilterMonitoringClusterInitCallback(EndpointId)
void MatterHepaFilterMonitoringClusterInitCallback(EndpointId)
void MatterActivatedCarbonFilterMonitoringClusterShutdownCallback(EndpointId, MatterClusterShutdownType)
void MatterHepaFilterMonitoringClusterShutdownCallback(EndpointId, MatterClusterShutdownType)
```

`ResourceMonitoring::Instance` 생성 시 다음 작업이 수행됩니다.

1. `ResourceMonitoringCluster` 생성
2. `SetDelegate` 호출
3. `CodegenDataModelProvider`의 registry에 인스턴스 등록

소멸 시 registry에서 인스턴스를 해제합니다.

### 생성된 metadata

파일:

- `zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h`

현재 생성된 `HepaFilterMonitoring::kRevision`은 `1`입니다.

`HepaFilterMonitoring::Attributes::kMandatoryMetadata`에는 다음 attribute만 포함됩니다.

```cpp
ChangeIndication::kMetadataEntry
```

`HepaFilterMonitoring::Commands::ResetCondition::kMetadataEntry`는 `operate` privilege로 정의되어 있습니다.

## 관련 문서

- `src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml`
- `data_model/1.7/clusters/ResourceMonitoring.xml`
- `src/app/clusters/resource-monitoring-server/README.md`
- `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h`
- `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp`
- `src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h`
- `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h`
- `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp`
- `src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h`
- `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h`
- `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp`
- `src/app/clusters/resource-monitoring-server/CodegenIntegration.h`
- `src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp`
- `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h`
- `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp`
- `zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h`
- `zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h`

## 관련 페이지

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
