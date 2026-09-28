---
entity: HEPA Filter Monitoring
ids: ['0x0071', '0x0072']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-server.h', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.h', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp', 'src/app/clusters/resource-monitoring-server/README.md', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp', 'data_model/1.7/clusters/ResourceMonitoring.xml', 'zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h', 'zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# HEPA Filter Monitoring

## 개요

`HEPA Filter Monitoring`은 장치의 HEPA 필터를 모니터링하는 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0071` |
| PICS 코드 | `HEPAFREMON` |
| SDK define | `HEPA_FILTER_MONITORING_CLUSTER` |
| SDK 도메인 | `Measurement & Sensing` |
| 생성 코드 네임스페이스 | `chip::app::Clusters::HepaFilterMonitoring` |
| 공통 구현 네임스페이스 | `chip::app::Clusters::ResourceMonitoring` |

`Resource Monitoring`은 자체 클러스터 ID가 없는 공통 의사 클러스터이며, 다른 클러스터의 별칭 구현에 사용된다. 제공된 정의에는 `HEPA Filter Monitoring`, `Activated Carbon Filter Monitoring`(`0x0072`), `Water Tank Level Monitoring`(`0x0079`)이 포함된다.

**버전 차이:** 제공된 스펙은 revision `2`이며 `Medium`을 포함하지만, SDK XML과 생성 메타데이터는 revision `1`이다. 제공된 구현에는 `Medium` 처리가 없다.

## 스펙

출처: `data_model/1.7/clusters/ResourceMonitoring.xml`

### 분류 및 revision

| 항목 | 값 |
|---|---|
| 정의 이름 | `Resource Monitoring Clusters` |
| revision | `2` |
| hierarchy | `base` |
| role | `application` |
| 공통 picsCode | `REPM` |
| scope | `Endpoint` |

- revision `1`: 최초 revision.
- revision `2`: `Medium` 추가.

### Feature

모든 Feature는 선택 사항이다.

| bit | code | name | 의미 |
|---|---|---|---|
| `0` | `CON` | `Condition` | 리소스 상태를 백분율로 모니터링 |
| `1` | `WRN` | `Warning` | 경고 표시 지원 |
| `2` | `REP` | `ReplacementProductList` | 교체 제품 목록 지정 지원 |

### 속성

모든 속성은 `view` 권한으로 읽을 수 있다.

| ID | 이름 | 스펙 타입 | 적합성 | 추가 접근·품질·제약 |
|---|---|---|---|---|
| `0x0000` | `Condition` | `percent` | `CON` 지원 시 필수 | 읽기 전용 |
| `0x0001` | `DegradationDirection` | `DegradationDirectionEnum` | `CON` 지원 시 필수 | 읽기 전용, `fixed` |
| `0x0002` | `ChangeIndication` | `ChangeIndicationEnum` | 필수 | 읽기 전용 |
| `0x0003` | `InPlaceIndicator` | `bool` | 선택 | 읽기 전용 |
| `0x0004` | `LastChangedTime` | `epoch-s` | 선택 | `operate` 권한 쓰기, nullable, `nonVolatile`, 기본값 `null` |
| `0x0005` | `ReplacementProductList` | `list` | `REP` 지원 시 필수 | 원소 타입 `ReplacementProductStruct`, 최대 `5`개, 읽기 전용, `fixed` |
| `0x0006` | `Medium` | `medium-type` | 아래 적합성 정의 참조 | 읽기 전용, `fixed` |

`Medium`의 적합성은 원문에서 `otherwiseConform` 아래 `provisionalConform`과 현재 revision이 `2` 이상인 경우의 `optionalConform`으로 표현되어 있다.

### 데이터 타입

#### `ChangeIndicationEnum`

| 값 | 이름 | 의미 | 적합성 |
|---|---|---|---|
| `0` | `OK` | 리소스 상태가 양호하며 개입 불필요 | 필수 |
| `1` | `Warning` | 리소스가 곧 소진되어 조만간 개입 필요 | `WRN` 지원 시 필수 |
| `2` | `Critical` | 리소스가 소진되어 즉시 개입 필요 | 필수 |

#### `DegradationDirectionEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Up` | 값이 증가하는 방향으로 리소스 열화를 표시 |
| `1` | `Down` | 값이 감소하는 방향으로 리소스 열화를 표시 |

#### `ProductIdentifierTypeEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `UPC` | 12자리 Universal Product Code |
| `1` | `GTIN-8` | 8자리 Global Trade Item Number |
| `2` | `EAN` | 13자리 European Article Number |
| `3` | `GTIN-14` | 14자리 Global Trade Item Number |
| `4` | `OEM` | Original Equipment Manufacturer 부품 번호 |

#### `ReplacementProductStruct`

| field ID | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `ProductIdentifierType` | `ProductIdentifierTypeEnum` | 필수 |
| `1` | `ProductIdentifierValue` | `string` | 필수, 최대 길이 `20` |

### 명령

| ID | 이름 | 방향 | 적합성 | 호출 권한 | response |
|---|---|---|---|---|---|
| `0x00` | `ResetCondition` | `commandToServer` | 선택 | `operate` | `Y` |

## SDK 정의

### XML 정의

출처: `src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml`

이 파일은 Alchemy 생성 파일로, 직접 수정하지 않도록 표시되어 있다. 생성 원본 경로는 `src/app_clusters/ResourceMonitoring.adoc`이다.

- `HEPA Filter Monitoring`의 클러스터 코드는 `0x0071`이다.
- client와 server가 모두 활성화되어 있으며, 두 역할의 `tick`과 `init`은 모두 `false`이다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="1"`로 정의된다.
- `CON`, `WRN`, `REP`의 bit와 이름은 제공된 스펙과 동일하다.
- `Medium`은 정의되어 있지 않다.

| ID | 이름 | define | SDK 타입 | SDK 제약·설정 |
|---|---|---|---|---|
| `0x0000` | `Condition` | `CONDITION` | `percent` | `CON` 지원 시 필수 |
| `0x0001` | `DegradationDirection` | `DEGRADATION_DIRECTION` | `DegradationDirectionEnum` | `CON` 지원 시 필수, `max="1"` |
| `0x0002` | `ChangeIndication` | `CHANGE_INDICATION` | `ChangeIndicationEnum` | 필수, `max="2"` |
| `0x0003` | `InPlaceIndicator` | `IN_PLACE_INDICATOR` | `boolean` | 선택 |
| `0x0004` | `LastChangedTime` | `LAST_CHANGED_TIME` | `epoch_s` | 선택, `writable="true"`, `isNullable="true"` |
| `0x0005` | `ReplacementProductList` | `REPLACEMENT_PRODUCT_LIST` | `array` | `REP` 지원 시 필수, `entryType="ReplacementProductStruct"`, `length="5"` |

모든 위 속성은 `side="server"`이다.

SDK XML의 `DegradationDirectionEnum`, `ChangeIndicationEnum`, `ProductIdentifierTypeEnum`은 `enum8`이며 `0x0071`, `0x0072`, `0x0079`에 연결된다.

`ReplacementProductStruct`는 각 클러스터에 별도로 선언된다. XML 주석은 각 구현 범위의 `ProductIdentifierTypeEnum`을 참조하기 때문에 구조체 정의를 중복한다고 설명한다.

- `ProductIdentifierType`: `ProductIdentifierTypeEnum`, `max="0x04"`.
- `ProductIdentifierValue`: `char_string`, `length="20"`.

### `ResetCondition`

SDK XML은 `ResetCondition`을 `source="client"`, `code="0x00"`, 선택 명령으로 정의한다. 설명에서는 초기 구성과 같은 완전한 리소스 가용성과 사용 준비 상태를 나타내도록 `Condition`과 `ChangeIndicator`를 재설정해야 한다고 명시한다.

> 원문 표기 차이: 명령 설명에는 `ChangeIndicator`가 등장하지만, 실제 속성 정의와 구현의 이름은 `ChangeIndication`이다.

### 생성 메타데이터

출처:

- `zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h`
- `zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h`

두 파일은 `src/controller/data_model/controller-clusters.matter`를 기반으로 생성되며, 모두 `kRevision = 1`이다.

`HepaFilterMonitoring` 메타데이터의 주요 설정:

- `kMandatoryMetadata`에는 `ChangeIndication::kMetadataEntry`만 포함된다.
- 모든 클러스터 고유 속성의 읽기 권한은 `Access::Privilege::kView`이다.
- `LastChangedTime`만 쓰기 권한 `Access::Privilege::kOperate`를 가진다.
- `ReplacementProductList`에는 `DataModel::AttributeQualityFlags::kListAttribute`가 설정된다.
- `ResetCondition` 호출 권한은 `Access::Privilege::kOperate`이다.
- `Events` 네임스페이스는 비어 있다.

## 구현

### 주요 구성 파일

| 파일 | 역할 |
|---|---|
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h` | `ResourceMonitoringCluster` 인터페이스와 상태 |
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp` | 속성 접근, 상태 갱신, 명령 처리, 영속 속성 로드 |
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h` | `Delegate` 및 초기화·재설정 확장 지점 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h` | 공통 enum, 속성·명령 메타데이터, `ReplacementProductStruct` |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp` | `ResetCondition`의 TLV 디코딩 |
| `src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h` | `ReplacementProductListManager` 인터페이스 |
| `src/app/clusters/resource-monitoring-server/CodegenIntegration.h` | 기존 사용 코드를 위한 `Instance` 래퍼 |
| `src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp` | 선택 속성 구성 및 codegen 등록·해제 |
| `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h` | 마이그레이션을 수행하는 하위 클래스 선언 |
| `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp` | `Startup` 시 저장소 마이그레이션 |
| `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h` | 마이그레이션 함수 선언 |
| `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp` | `LastChangedTime` 마이그레이션 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-server.h` | `CodegenIntegration.h` 포함 |

### 클래스와 초기화

`ResourceMonitoringCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 endpoint, cluster ID, 활성 Feature, 선택 속성 집합, `DegradationDirection`, `ResetCondition` 지원 여부를 받는다.

`OptionalAttributeSet`으로 지정하는 속성은 다음 두 개뿐이다.

- `ResourceMonitoring::Attributes::InPlaceIndicator::Id`
- `ResourceMonitoring::Attributes::LastChangedTime::Id`

`Condition`, `DegradationDirection`, `ReplacementProductList`의 노출 여부는 Feature로 결정된다.

| 상태 | 초기 설정 |
|---|---|
| `mCondition` | `100` |
| `mDegradationDirection` | 멤버 기본값은 `DegradationDirectionEnum::kDown`, 생성자 인자로 설정 |
| `mChangeIndication` | `ChangeIndicationEnum::kOk` |
| `mInPlaceIndicator` | `true` |
| `mLastChangedTime` | `DataModel::Nullable<uint32_t>` |
| `mReplacementProductListManager` | `nullptr` |

`SetDelegate`는 다음 순서로 동작한다.

1. `nullptr`이면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
2. `mDelegate`를 설정한다.
3. `Delegate::SetInstance`로 연결된 클러스터를 지정한다.
4. `Delegate::Init`을 호출하고 결과를 반환한다.

`Delegate::Init`은 순수 가상 함수이다. 호출자는 `Delegate`가 클러스터 인스턴스의 전체 수명 동안 유효하도록 보장해야 한다.

### 속성 목록과 읽기

`ResourceMonitoringCluster::Attributes`는 `HepaFilterMonitoring::Attributes::kMandatoryMetadata`에 다음 항목을 조건부로 추가한다.

| 조건 | 추가 속성 |
|---|---|
| `Feature::kCondition` | `Condition`, `DegradationDirection` |
| 선택 속성 집합에 포함 | `InPlaceIndicator`, `LastChangedTime` |
| `Feature::kReplacementProductList` | `ReplacementProductList` |

`ReadAttribute`는 각 상태 값과 `FeatureMap`을 인코딩하며, `ReplacementProductList`는 `ReadReplaceableProductList`에 위임한다.

`ClusterRevision` 읽기에서는 다음과 같이 처리한다.

- cluster ID가 `HepaFilterMonitoring::Id`이면 `HepaFilterMonitoring::kRevision`.
- 그 외에는 `ActivatedCarbonFilterMonitoring::kRevision`.

나머지 속성 ID에는 `Status::UnsupportedAttribute`를 반환한다.

### 쓰기와 상태 갱신

`WriteAttribute`는 `WriteImpl`의 결과에 대해 `NotifyAttributeChangedIfSuccess`를 호출한다.

`WriteImpl`이 처리하는 속성은 `LastChangedTime`뿐이다.

- `mContext`가 없으면 `Status::InvalidInState`.
- `AttributePersistence::DecodeAndStoreNativeEndianValue`로 디코딩 및 저장.
- 나머지 속성에는 `Status::UnsupportedWrite`.

애플리케이션용 갱신 함수의 동작은 다음과 같다.

| 함수 | 동작 |
|---|---|
| `UpdateCondition` | 값을 대입하고 변경 시 알림. 제공된 함수 본문에는 백분율 범위 검증이 없음 |
| `UpdateChangeIndication` | `Feature::kWarning` 없이 `ChangeIndicationEnum::kWarning`을 지정하면 `Status::InvalidValue`; 그 외에는 변경 시 알림 |
| `UpdateInPlaceIndicator` | 값을 대입하고 변경 시 알림 |
| `UpdateLastChangedTime` | context 확인 후 값을 변경하고 영속 저장. 저장 성공 시 알림 |

`UpdateLastChangedTime`은 동일한 값이면 저장 없이 `Status::Success`를 반환한다. 저장 실패 시 `Status::Failure`를 반환하지만, 메모리의 `mLastChangedTime`은 저장 시도 전에 갱신된다.

조회 함수로 `GetCondition`, `GetChangeIndication`, `GetDegradationDirection`, `GetInPlaceIndicator`, `GetLastChangedTime`을 제공한다. `HasFeature`와 `HasOptionalAttribute`는 각각 활성 Feature와 선택 속성 집합을 확인한다.

### `ResetCondition` 처리

`AcceptedCommands`는 `mResetConditionCommandSupported`가 참일 때만 `ResetCondition`을 명령 목록에 추가한다.

`InvokeCommand`의 처리 흐름:

1. `ResourceMonitoring::Commands::ResetCondition::Id` 확인.
2. `DecodableType::Decode` 호출.
3. `ResetCondition` 호출.
4. `mDelegate->OnResetCondition`에 위임.

알 수 없는 명령에는 `Status::UnsupportedCommand`를 반환한다. `DecodableType::Decode`는 TLV가 `TLV::kTLVType_Structure`인지 확인하고 컨테이너를 순회한다. 개별 명령 필드의 디코딩은 정의되어 있지 않다.

기본 `Delegate::OnResetCondition`의 처리 순서는 다음과 같다.

1. `PreResetCondition` 호출.
   - `Status::Success`가 아니면 속성을 재설정하지 않고 해당 상태를 반환한다.
2. `Feature::kCondition`이 활성화되어 있으면 `Condition` 재설정.
   - `DegradationDirectionEnum::kDown`: `100`.
   - `DegradationDirectionEnum::kUp`: `0`.
3. `ChangeIndication`을 `ChangeIndicationEnum::kOk`로 갱신.
4. 선택 속성 `LastChangedTime`이 있으면 `System::SystemClock().GetClock_RealTimeMS` 호출.
   - 성공하면 초 단위로 변환하여 `UpdateLastChangedTime` 호출.
   - 실패하면 `LastChangedTime`을 갱신하지 않음.
5. `PostResetCondition`의 결과 반환.

`PreResetCondition`과 `PostResetCondition`의 기본 구현은 `Status::Success`를 반환한다. `Delegate` 문서는 `OnResetCondition` 전체 재정의보다 두 확장 지점의 재정의를 권장한다.

**오류 처리 유의점:**

- `PostResetCondition` 실패 시 속성은 이미 갱신된 상태이다.
- 기본 `OnResetCondition`은 `UpdateCondition`, `UpdateChangeIndication`, `UpdateLastChangedTime`의 반환 상태를 검사하지 않는다.

### 교체 제품 목록

`SetReplacementProductListManagerInstance`로 `ReplacementProductListManager`를 연결한다.

`ReadReplaceableProductList`의 동작:

- 관리자가 없으면 `EncodeEmptyList`.
- 관리자가 있으면 `Reset`으로 `mIndex`를 `0`으로 설정.
- `Next`가 반환하는 `ReplacementProductStruct`를 순서대로 인코딩.
- `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`는 정상 종료로 처리.
- 나머지 오류는 반환.

`ReplacementProductListManager::kReplacementProductListMaxSize`는 `5u`이다. 제공된 읽기 루프 자체에는 항목 수 제한 검사가 없다.

공통 `ReplacementProductStruct` 구현:

- `HepaFilterMonitoring::Structs::ReplacementProductStruct::Type`을 private 상속한다.
- `kProductIdentifierValueMaxNameLength = 20u` 크기의 내부 버퍼를 사용한다.
- `SetProductIdentifierValue`는 빈 값이나 버퍼 크기 초과 시 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.
- 유효한 입력은 내부 버퍼로 복사한다.
- 내부 버퍼를 가리키는 span의 얕은 복사를 방지하기 위해 복사 생성자를 삭제한다.
- 대입 연산자는 setter를 통해 값을 복사한다.
- `kIsFabricScoped = false`이다.

### 공통 C++ 타입

`resource-monitoring-cluster-objects.h`는 XML 이름과 별도로 다음 C++ enum 멤버를 정의한다.

| 타입 | 멤버와 값 |
|---|---|
| `ChangeIndicationEnum` | `kOk = 0x00`, `kWarning = 0x01`, `kCritical = 0x02` |
| `DegradationDirectionEnum` | `kUp = 0x00`, `kDown = 0x01` |
| `Feature` | `kCondition = 0x1`, `kWarning = 0x2`, `kReplacementProductList = 0x4` |
| `ProductIdentifierTypeEnum` | `kUpc = 0x00`, `kGtin8 = 0x01`, `kEan = 0x02`, `kGtin14 = 0x03`, `kOem = 0x04` |

`ChangeIndicationEnum`과 `DegradationDirectionEnum`에는 `kUnknownEnumValue = UINT8_MAX`도 있다. 주석은 이를 알 수 없는 수신 enum 값의 처리용으로 설명하며, 전송해서는 안 된다고 명시한다.

공통 속성 메타데이터와 `ResetCondition` 메타데이터는 `ActivatedCarbonFilterMonitoring`의 생성 정의를 참조한다. 전역 속성 `GeneratedCommandList`, `AcceptedCommandList`, `AttributeList`, `FeatureMap`, `ClusterRevision`은 `Globals` 정의를 사용한다.

### 영속 저장 및 마이그레이션

`ResourceMonitoringCluster::Startup`은 다음 순서로 실행된다.

1. `DefaultServerCluster::Startup`.
2. `LoadPersistentAttributes`.
3. `CHIP_NO_ERROR` 반환.

`LoadPersistentAttributes`는 `AttributePersistence::LoadNativeEndianValue<uint32_t>`로 `LastChangedTime`을 로드한다. 이전 값을 찾지 못하면 `null`을 기본값으로 사용한다.

`CodegenResourceMonitoringCluster::Startup`은 기본 클래스의 `Startup` 전에 마이그레이션을 수행한다.

- 원본: `GetSafeAttributePersistenceProvider`가 반환한 `SafeAttributePersistenceProvider`.
- 대상: `context.attributeStorage`의 `AttributePersistenceProvider`.
- 원본 provider가 존재하면 `MigrateResourceMonitoringServerStorage` 호출.
- 마이그레이션 오류는 기록하고, 이후 `ResourceMonitoringCluster::Startup`을 계속 호출.

`MigrateResourceMonitoringServerStorage`의 대상 속성은 `LastChangedTime` 하나이다. `sizeof(uint32_t)`와 `isScalar = true`로 migration 데이터를 구성하고 `MigrateFromSafeToAttributePersistenceProvider`를 호출한다.

### codegen 통합

`Instance`는 `RegisteredServerCluster<CodegenResourceMonitoringCluster>`를 보유하고 속성의 `Update...` 및 `Get...` 호출을 내부 클러스터로 전달한다.

생성 시:

1. `ConstructOptionalAttributeSet`에서 `emberAfContainsServer`를 확인.
2. `emberAfContainsAttribute`로 `InPlaceIndicator`, `LastChangedTime` 포함 여부 확인.
3. 내부 클러스터 생성.
4. `SetDelegate` 호출.
5. `RegisterInstance`를 통해 `CodegenDataModelProvider::Instance().Registry().Register` 호출.

소멸 시 registry의 `Unregister`를 호출한다.

`Instance` 생성자는 `SetDelegate`의 반환값을 `TEMPORARY_RETURN_IGNORED`로 무시한다. 등록 오류의 로그 출력은 `CHIP_CODEGEN_CONFIG_ENABLE_CODEGEN_INTEGRATION_LOOKUP_ERRORS`에 의해 제어된다.

`Instance::Init`은 내부 `ResourceMonitoringCluster::Init`에 위임하며, 제공된 `ResourceMonitoringCluster::Init` 구현은 `CHIP_NO_ERROR`만 반환한다.

다음 callback은 제공된 구현에서 비어 있다.

- `MatterHepaFilterMonitoringClusterInitCallback`
- `MatterHepaFilterMonitoringClusterShutdownCallback`
- `MatterActivatedCarbonFilterMonitoringClusterInitCallback`
- `MatterActivatedCarbonFilterMonitoringClusterShutdownCallback`

## 관련 문서

### 사용 안내

출처: `src/app/clusters/resource-monitoring-server/README.md`

README는 다음 사용 절차를 안내한다.

1. `ResourceMonitoring::Instance`를 상속하는 클래스 작성.
2. `OnResetCondition` 구현.
3. 필요하면 `AppInit` 구현.
4. main 파일에서 인스턴스 생성.
5. 인스턴스의 `.Init()` 호출.

참조 대상으로 `examples/resource-monitoring-app/`의 `src/instances` 및 `include/instances` 디렉터리를 제시한다.

또한 Zap accessor 함수는 실제 속성 값을 반환하지 않으므로, 속성 접근에 인스턴스의 `Update...`와 `Get...` 함수를 사용하도록 명시한다.

### 별칭 클러스터 추가 안내

README에 기재된 절차:

1. 스펙을 `src/app/zap-templates/zcl/data-model/chip`의 XML로 작성.
2. `resource-monitoring-cluster-objects.h`의 `AliasedClusters`에 클러스터 ID 추가.
3. zap 코드 재생성.
4. `all-clusters-app/resource-monitoring` 예시에 새 클러스터 추가.

### 문서와 제공 코드의 차이

- README는 `ResourceMonitoring::Instance` 상속 클래스에서 `OnResetCondition`을 구현하도록 설명하지만, 제공된 코드의 재설정 확장 지점은 `Delegate`에 선언되어 있다.
- README의 선택적 `AppInit` 안내와 달리, 제공된 `Delegate`는 순수 가상 함수 `Init`을 선언한다.
- README가 참조하는 `resource-monitoring-server.h`는 제공된 코드에서 `CodegenIntegration.h`를 포함하는 역할만 한다.
- README의 추가 절차에 등장하는 `AliasedClusters`는 제공된 `resource-monitoring-cluster-objects.h`에 없다.
- 제공된 스펙의 revision `2` 및 `Medium` 정의는 SDK XML, 생성 메타데이터, 구현에 반영되어 있지 않다.

## 관련 페이지

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
