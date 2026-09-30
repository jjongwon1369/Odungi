---
entity: HEPA Filter Monitoring
ids: ['0x0071', '0x0072']
source_paths: ['data_model/1.7/clusters/ResourceMonitoring.xml', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.h', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h', 'src/app/clusters/resource-monitoring-server/README.md', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h', 'src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-server.h', 'src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml', 'zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h', 'zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# HEPA Filter Monitoring

## 개요

`HEPA Filter Monitoring`은 장치의 HEPA 필터 상태를 감시하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0071` |
| PICS 코드 | `HEPAFREMON` |
| 구현 네임스페이스 | `HepaFilterMonitoring` |
| 공통 구현 | `ResourceMonitoring` |
| 스펙 revision | `2` |
| 제공된 SDK 및 생성 메타데이터 revision | `1` |

`Resource Monitoring`은 자체 클러스터 ID가 없는 의사 클러스터이며, 다른 클러스터의 별칭으로 사용된다. 제공된 정의와 구현은 `HEPA Filter Monitoring` 및 `Activated Carbon Filter Monitoring`(`0x0072`)이 공유한다.

## 스펙

출처: `data_model/1.7/clusters/ResourceMonitoring.xml`

### 분류 및 revision

공통 정의의 이름은 `Resource Monitoring Clusters`이다.

| 분류 항목 | 값 |
|---|---|
| hierarchy | `base` |
| role | `application` |
| picsCode | `REPM` |
| scope | `Endpoint` |

- revision `1`: 최초 정의.
- revision `2`: `Medium` 속성 추가.

### 기능

모든 기능은 선택 사항이다.

| bit | code | name | 기능 |
|---|---|---|---|
| `0` | `CON` | `Condition` | 자원 상태를 백분율로 감시 |
| `1` | `WRN` | `Warning` | 경고 표시 지원 |
| `2` | `REP` | `ReplacementProductList` | 교체 제품 목록 제공 |

### 데이터 타입

#### `ChangeIndicationEnum`

| 값 | 이름 | 의미 | 적합성 |
|---|---|---|---|
| `0` | `OK` | 상태가 양호하며 조치가 필요하지 않음 | 필수 |
| `1` | `Warning` | 자원이 곧 소진되어 조치가 필요해질 예정 | `WRN` 사용 시 필수 |
| `2` | `Critical` | 자원이 소진되어 즉시 조치가 필요함 | 필수 |

#### `DegradationDirectionEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Up` | 값이 증가하는 방향으로 자원 열화를 표시 |
| `1` | `Down` | 값이 감소하는 방향으로 자원 열화를 표시 |

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

### 속성

모든 속성의 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 적합성 | 추가 조건 |
|---|---|---|---|---|
| `0x0000` | `Condition` | `percent` | `CON` 사용 시 필수 | 읽기 전용 |
| `0x0001` | `DegradationDirection` | `DegradationDirectionEnum` | `CON` 사용 시 필수 | 읽기 전용, `fixed` |
| `0x0002` | `ChangeIndication` | `ChangeIndicationEnum` | 필수 | 읽기 전용 |
| `0x0003` | `InPlaceIndicator` | `bool` | 선택 | 읽기 전용 |
| `0x0004` | `LastChangedTime` | `epoch-s` | 선택 | 쓰기 권한 `operate`, nullable, 기본값 `null`, `nonVolatile` |
| `0x0005` | `ReplacementProductList` | `list` | `REP` 사용 시 필수 | 항목 타입 `ReplacementProductStruct`, 최대 `5`개, 읽기 전용, `fixed` |
| `0x0006` | `Medium` | `medium-type` | 아래 적합성 참조 | 읽기 전용, `fixed` |

`Medium`의 적합성은 `otherwiseConform` 아래에 `provisionalConform`과 현재 revision이 `2` 이상일 때의 `optionalConform`으로 표현되어 있다.

### 명령

| ID | 이름 | 방향 | 호출 권한 | 적합성 | response |
|---|---|---|---|---|---|
| `0x00` | `ResetCondition` | `commandToServer` | `operate` | 선택 | `Y` |

제공된 XML에 `ResetCondition`의 입력 필드는 정의되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml`

### 클러스터 설정

- 이름: `HEPA Filter Monitoring`
- domain: `Measurement & Sensing`
- code: `0x0071`
- define: `HEPA_FILTER_MONITORING_CLUSTER`
- client와 server 모두 활성화되어 있으며, 각각 `tick="false"`, `init="false"`로 설정된다.
- `globalAttribute`의 code `0xFFFD`는 `side="either"`, `value="1"`로 정의된다.

### 속성 매핑

| 이름 | define | SDK 타입 | 주요 설정 |
|---|---|---|---|
| `Condition` | `CONDITION` | `percent` | `optional="true"`, `CON` 사용 시 필수 |
| `DegradationDirection` | `DEGRADATION_DIRECTION` | `DegradationDirectionEnum` | `max="1"`, `CON` 사용 시 필수 |
| `ChangeIndication` | `CHANGE_INDICATION` | `ChangeIndicationEnum` | 필수, `max="2"` |
| `InPlaceIndicator` | `IN_PLACE_INDICATOR` | `boolean` | 선택 |
| `LastChangedTime` | `LAST_CHANGED_TIME` | `epoch_s` | 선택, writable, nullable |
| `ReplacementProductList` | `REPLACEMENT_PRODUCT_LIST` | `array` | `entryType="ReplacementProductStruct"`, `length="5"`, `REP` 사용 시 필수 |

`DegradationDirectionEnum`, `ChangeIndicationEnum`, `ProductIdentifierTypeEnum`은 `enum8`로 정의된다.

`ReplacementProductStruct`는 두 별칭 클러스터에 대해 별도로 선언된다. 원문의 설명에 따르면 각 클러스터 범위의 `ProductIdentifierTypeEnum`을 참조하기 때문이다.

- `ProductIdentifierType`: `max="0x04"`
- `ProductIdentifierValue`: `char_string`, `length="20"`

`ResetCondition`은 `source="client"`, code `0x00`, 선택 명령으로 정의된다.

### 생성 메타데이터

출처:

- `zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h`
- `zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h`

두 파일 모두 다음 내용을 정의한다.

- `kRevision = 1`
- `kMandatoryMetadata`에는 `ChangeIndication::kMetadataEntry`만 포함.
- 속성 읽기 권한은 `Access::Privilege::kView`.
- `LastChangedTime`의 쓰기 권한은 `Access::Privilege::kOperate`.
- `ReplacementProductList`에는 `DataModel::AttributeQualityFlags::kListAttribute` 적용.
- `ResetCondition`의 호출 권한은 `Access::Privilege::kOperate`.
- `Events` 네임스페이스는 비어 있음.

### 스펙과 제공된 SDK의 차이

- 스펙은 revision `2`이며 `Medium`을 포함한다.
- 제공된 SDK XML과 생성 메타데이터는 revision `1`이며 `Medium`을 포함하지 않는다.
- SDK XML의 `ResetCondition` 설명에는 `ChangeIndicator`라는 식별자가 사용되지만, 실제 속성 정의와 구현에서 사용하는 이름은 `ChangeIndication`이다.

## 구현

### 주요 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h` | `ResourceMonitoringCluster` 인터페이스 및 상태 |
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp` | 속성 처리, 영속화, 명령 및 기본 초기화 동작 |
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h` | 애플리케이션용 `Delegate` 인터페이스 |
| `src/app/clusters/resource-monitoring-server/CodegenIntegration.h` | 기존 코드용 `Instance` 래퍼 |
| `src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp` | 등록, 등록 해제 및 선택 속성 구성 |
| `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h` | 영속 저장소 마이그레이션을 수행하는 파생 클래스 |
| `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp` | `Startup` 시 마이그레이션 실행 |
| `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h` | 저장소 마이그레이션 함수 선언 |
| `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp` | `LastChangedTime` 마이그레이션 |
| `src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h` | 교체 제품 목록 반복 인터페이스 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h` | 공통 타입, 속성 및 명령 정의 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp` | `ResetCondition` 디코딩 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-server.h` | `CodegenIntegration.h` 포함 |

### 생성 및 수명 관리

`ResourceMonitoringCluster`는 `DefaultServerCluster`를 상속하며, 생성 시 다음 구성을 받는다.

- `aEndpointId`, `aClusterId`
- `enabledFeatures`
- `optionalAttributeSet`
- `aDegradationDirection`
- `aResetConditionCommandSupported`

`OptionalAttributeSet`은 `InPlaceIndicator`와 `LastChangedTime`만 포함한다. `Condition`, `DegradationDirection`, `ReplacementProductList`의 노출 여부는 기능 설정으로 결정된다.

`Instance`의 생성 흐름은 다음과 같다.

1. `ConstructOptionalAttributeSet`이 `emberAfContainsServer`를 검증한다.
2. `emberAfContainsAttribute`로 선택 속성 존재 여부를 확인한다.
3. `mCluster`를 생성한다.
4. `SetDelegate`를 호출한다.
5. `RegisterInstance`가 `CodegenDataModelProvider::Instance().Registry().Register`를 호출한다.

`SetDelegate`는 `nullptr`이면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. 정상 포인터이면 `Delegate`에 인스턴스를 연결하고 `Init`을 호출한다. `Instance` 생성자는 이 반환값을 `TEMPORARY_RETURN_IGNORED`로 처리한다.

호출자는 `Delegate`가 클러스터 인스턴스의 수명 동안 유효하도록 보장해야 한다. `Instance::~Instance`는 등록을 해제한다.

현재 `ResourceMonitoringCluster::Init`은 `CHIP_NO_ERROR`만 반환한다. 실제 기본 시작 처리와 영속 속성 로드는 `Startup`에서 수행된다.

다음 콜백의 본문은 비어 있다.

- `MatterHepaFilterMonitoringClusterInitCallback`
- `MatterHepaFilterMonitoringClusterShutdownCallback`
- `MatterActivatedCarbonFilterMonitoringClusterInitCallback`
- `MatterActivatedCarbonFilterMonitoringClusterShutdownCallback`

### 초기 상태와 속성 접근

| 상태 | 초기값 또는 설정 방식 |
|---|---|
| `mCondition` | `100` |
| `mDegradationDirection` | 생성자 인수로 설정 |
| `mChangeIndication` | `ChangeIndicationEnum::kOk` |
| `mInPlaceIndicator` | `true` |
| `mLastChangedTime` | nullable 상태, 시작 시 영속 값 로드 |
| `mReplacementProductListManager` | `nullptr` |

속성 갱신과 조회에는 다음 함수를 제공한다.

| 갱신 함수 | 조회 함수 |
|---|---|
| `UpdateCondition` | `GetCondition` |
| `UpdateChangeIndication` | `GetChangeIndication` |
| `UpdateInPlaceIndicator` | `GetInPlaceIndicator` |
| `UpdateLastChangedTime` | `GetLastChangedTime` |
| — | `GetDegradationDirection` |

- `UpdateCondition`과 `UpdateInPlaceIndicator`는 값이 변경되면 `NotifyAttributeChanged`를 호출한다.
- 제공된 `UpdateCondition` 본문에는 백분율 범위 검사가 없다.
- `UpdateChangeIndication`은 `Feature::kWarning`이 비활성화된 상태에서 `ChangeIndicationEnum::kWarning`을 설정하면 `Status::InvalidValue`를 반환한다.
- `WriteImpl`은 `LastChangedTime`만 처리하며, 다른 속성에는 `Status::UnsupportedWrite`를 반환한다.
- `WriteAttribute`는 `NotifyAttributeChangedIfSuccess`를 통해 성공 시 변경을 통지한다.
- `ReadAttribute`는 개별 속성과 `FeatureMap`, `ClusterRevision`을 처리한다.
- `HEPA Filter Monitoring`의 `ClusterRevision` 읽기는 `HepaFilterMonitoring::kRevision`을 반환한다.
- 제공된 속성 목록 구성과 읽기 구현에는 `Medium` 처리가 없다.

### 영속화 및 마이그레이션

`LastChangedTime`은 `AttributePersistence`를 통해 저장하고 로드한다.

- `UpdateLastChangedTime`은 `mContext`가 없으면 `Status::InvalidInState`를 반환한다.
- 값이 같으면 저장 없이 `Status::Success`를 반환한다.
- 값이 다르면 메모리 값을 먼저 갱신한 뒤 `StoreNativeEndianValue`를 호출한다.
- 저장 실패 시 `Status::Failure`를 반환하며, 제공된 본문에는 메모리 값 복구 처리가 없다.
- 저장 성공 후 변경을 통지한다.
- `LoadPersistentAttributes`는 이전 값을 읽을 수 없으면 `null`을 기본값으로 사용한다.

`CodegenResourceMonitoringCluster::Startup`은 다음 순서로 동작한다.

1. `GetSafeAttributePersistenceProvider`로 기존 저장소를 얻는다.
2. 기존 저장소가 있으면 `MigrateResourceMonitoringServerStorage`를 호출한다.
3. 마이그레이션 실패를 `LogErrorOnFailure`로 기록한다.
4. `ResourceMonitoringCluster::Startup`을 호출한다.

마이그레이션 대상은 `LastChangedTime` 하나이며, `sizeof(uint32_t)`와 `isScalar = true`로 기술된다. `MigrateFromSafeToAttributePersistenceProvider`가 실제 이전을 수행한다.

### `ResetCondition` 처리

`AcceptedCommands`는 `mResetConditionCommandSupported`가 참일 때만 `ResetCondition`을 공개한다.

`InvokeCommand`는 명령을 디코딩한 뒤 `ResetCondition`을 호출하며, 최종 처리는 `mDelegate->OnResetCondition()`에 위임한다. 다른 명령에는 `Status::UnsupportedCommand`를 반환한다.

`DecodableType::Decode`는 입력이 `TLV::kTLVType_Structure`인지 확인하고 컨테이너를 순회한다. 별도의 명령 필드는 추출하지 않는다.

기본 `Delegate::OnResetCondition`의 처리 순서는 다음과 같다.

1. `PreResetCondition`을 호출한다. `Success`가 아니면 속성을 변경하지 않고 종료한다.
2. `Feature::kCondition`이 활성화되어 있으면:
   - `DegradationDirectionEnum::kDown`: `Condition`을 `100`으로 설정.
   - `DegradationDirectionEnum::kUp`: `Condition`을 `0`으로 설정.
3. `ChangeIndication`을 `ChangeIndicationEnum::kOk`로 설정한다.
4. `LastChangedTime`이 선택 속성으로 활성화되어 있고 실시간 시계 조회에 성공하면 현재 Unix 시간을 초 단위로 저장한다.
5. `PostResetCondition`의 결과를 반환한다.

기본 `PreResetCondition`과 `PostResetCondition`은 모두 `Success`를 반환한다. `PostResetCondition`이 실패해도 이미 수행한 속성 변경을 되돌리지는 않는다. 기본 처리에서는 각 속성 갱신 함수의 반환값을 검사하지 않는다.

`Delegate::Init`은 순수 가상 함수이다. 헤더는 기본 동작 전체를 바꾸는 `OnResetCondition` 재정의보다 `PreResetCondition`과 `PostResetCondition` 활용을 권장한다.

### 교체 제품 목록

`SetReplacementProductListManagerInstance`로 `ReplacementProductListManager`를 연결한다.

`ReadReplaceableProductList`는 다음과 같이 동작한다.

- 관리자가 없으면 빈 목록을 인코딩한다.
- 관리자가 있으면 `Reset`으로 반복 위치를 초기화한다.
- `Next`로 항목을 받아 인코딩한다.
- `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`는 정상적인 목록 종료로 처리한다.
- 그 밖의 오류는 반환한다.

`kReplacementProductListMaxSize = 5u`로 최대 크기를 정의하지만, 제공된 읽기 루프에는 항목 수를 직접 제한하는 검사가 없다.

`ReplacementProductStruct`의 주요 특성은 다음과 같다.

- `HepaFilterMonitoring::Structs::ReplacementProductStruct::Type`을 private 상속한다.
- `kProductIdentifierValueMaxNameLength = 20u` 크기의 내부 버퍼를 사용한다.
- `SetProductIdentifierValue`는 빈 값 또는 버퍼 크기를 초과하는 값을 `CHIP_ERROR_INVALID_ARGUMENT`로 거부한다.
- 유효한 값은 내부 버퍼로 복사한다.
- 내부 버퍼를 가리키는 span의 얕은 복사를 막기 위해 복사 생성자를 삭제한다.
- 대입 연산자는 식별자 타입과 값을 복사한다.

## 관련 문서

### 사용 안내

출처: `src/app/clusters/resource-monitoring-server/README.md`

README는 다음 사용 절차를 안내한다.

1. `ResourceMonitoring::Instance`를 상속하는 클래스를 만든다.
2. `OnResetCondition`을 구현한다.
3. 필요하면 `AppInit`을 구현한다.
4. 메인 파일에서 인스턴스를 생성한다.
5. `.Init()`을 호출한다.

참조 대상으로 `examples/resource-monitoring-app/`의 `src/instances` 및 `include/instances` 디렉터리와 `resource-monitoring-server.h`를 제시한다.

**속성 접근 주의:** README에 따르면 이 클러스터의 Zap accessor 함수는 실제 값을 반환하지 않는다. 인스턴스의 `Update...` 및 `Get...` 함수를 사용해야 한다.

**제공된 구현과의 차이:** README의 상속 및 초기화 안내와 달리, 제공된 코드에서는 `Delegate`가 `Init`, `OnResetCondition`, `PreResetCondition`, `PostResetCondition`을 제공한다. 제공된 `Instance` 정의에는 `AppInit`이나 `OnResetCondition`이 없다.

### 별칭 클러스터 추가 안내

README는 다음 절차를 제시한다.

1. 스펙을 `src/app/zap-templates/zcl/data-model/chip` 아래의 XML로 작성한다.
2. `resource-monitoring-cluster-objects.h`의 `AliasedClusters`에 클러스터 ID를 추가한다.
3. zap 코드를 다시 생성한다.
4. `all-clusters-app/resource-monitoring` 예제를 확장한다.

다만 제공된 `resource-monitoring-cluster-objects.h` 본문에는 `AliasedClusters` 정의가 없다.

## 관련 페이지

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md) (사용 클러스터: Activated Carbon Filter Monitoring `0x0072`)
- [Room Air Conditioner](../device-types/room-air-conditioner.md) (사용 클러스터: HEPA Filter Monitoring `0x0071`, Activated Carbon Filter Monitoring `0x0072`)
