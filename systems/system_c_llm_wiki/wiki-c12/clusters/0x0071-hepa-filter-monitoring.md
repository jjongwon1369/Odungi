---
entity: HEPA Filter Monitoring
ids: ['0x0071', '0x0072', '0x0079']
source_paths: ['data_model/1.7/clusters/ResourceMonitoring.xml', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.h', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h', 'src/app/clusters/resource-monitoring-server/README.md', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h', 'src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-server.h', 'src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml', 'zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h', 'zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# HEPA Filter Monitoring

## 개요

`HEPA Filter Monitoring`은 장치의 HEPA 필터를 모니터링하는 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0071` |
| PICS 코드 | `HEPAFREMON` |
| 구현 네임스페이스 | `chip::app::Clusters::HepaFilterMonitoring` |
| 공통 구현 네임스페이스 | `chip::app::Clusters::ResourceMonitoring` |
| 스펙 revision | `2` |
| 제공된 SDK 및 생성 메타데이터 revision | `1` |

`Resource Monitoring`은 자체 클러스터 ID가 없는 pseudo cluster이며, 다른 클러스터의 별칭으로 사용된다. 제공된 스펙은 다음 클러스터를 공통 정의로 묶는다.

- `HEPA Filter Monitoring`: `0x0071`
- `Activated Carbon Filter Monitoring`: `0x0072`
- `Water Tank Level Monitoring`: `0x0079`

제공된 서버 구현은 `ResourceMonitoringCluster`를 중심으로 속성 접근, `ResetCondition`, 교체 제품 목록 및 영속 저장을 처리한다.

## 스펙

출처: `data_model/1.7/clusters/ResourceMonitoring.xml`

### 분류 및 revision

공통 정의 이름은 `Resource Monitoring Clusters`이다.

| 항목 | 값 |
|---|---|
| hierarchy | `base` |
| role | `application` |
| picsCode | `REPM` |
| scope | `Endpoint` |

| revision | 변경 내용 |
|---|---|
| `1` | 최초 정의 |
| `2` | `Medium` 속성 추가 |

### 기능

각 기능 자체는 선택 사항이다.

| bit | code | 이름 | 설명 |
|---|---|---|---|
| `0` | `CON` | `Condition` | 자원 상태를 백분율로 모니터링 |
| `1` | `WRN` | `Warning` | 경고 표시 지원 |
| `2` | `REP` | `ReplacementProductList` | 교체 제품 목록 지정 지원 |

### 데이터 타입

#### `ChangeIndicationEnum`

| 값 | 이름 | 의미 | 적합성 |
|---|---|---|---|
| `0` | `OK` | 자원 상태가 양호하며 조치가 필요하지 않음 | 필수 |
| `1` | `Warning` | 자원이 곧 소진되어 조치가 필요해질 예정 | `WRN` 지원 시 필수 |
| `2` | `Critical` | 자원이 소진되어 즉시 조치가 필요함 | 필수 |

#### `DegradationDirectionEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Up` | 값의 증가로 자원 열화를 나타냄 |
| `1` | `Down` | 값의 감소로 자원 열화를 나타냄 |

#### `ProductIdentifierTypeEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `UPC` | 12자리 Universal Product Code |
| `1` | `GTIN-8` | 8자리 Global Trade Item Number |
| `2` | `EAN` | 13자리 European Article Number |
| `3` | `GTIN-14` | 14자리 Global Trade Item Number |
| `4` | `OEM` | Original Equipment Manufacturer 부품 번호 |

#### `ReplacementProductStruct`

| 필드 ID | 이름 | 타입 | 적합성 및 제약 |
|---|---|---|---|
| `0` | `ProductIdentifierType` | `ProductIdentifierTypeEnum` | 필수 |
| `1` | `ProductIdentifierValue` | `string` | 필수, 최대 길이 `20` |

### 속성

모든 속성의 읽기 권한은 `view`이다.

| ID | 이름 | 타입 | 적합성 | 쓰기 및 품질·제약 |
|---|---|---|---|---|
| `0x0000` | `Condition` | `percent` | `CON` 지원 시 필수 | 읽기 전용 |
| `0x0001` | `DegradationDirection` | `DegradationDirectionEnum` | `CON` 지원 시 필수 | 읽기 전용, `fixed` |
| `0x0002` | `ChangeIndication` | `ChangeIndicationEnum` | 필수 | 읽기 전용 |
| `0x0003` | `InPlaceIndicator` | `bool` | 선택 | 읽기 전용 |
| `0x0004` | `LastChangedTime` | `epoch-s` | 선택 | 쓰기 권한 `operate`, `nullable`, `nonVolatile`, 기본값 `null` |
| `0x0005` | `ReplacementProductList` | `list` | `REP` 지원 시 필수 | 읽기 전용, `fixed`, 항목 타입 `ReplacementProductStruct`, 최대 `5`개 |
| `0x0006` | `Medium` | `medium-type` | 아래 적합성 정의 참조 | 읽기 전용, `fixed` |

`Medium`의 적합성은 `otherwiseConform` 안에 `provisionalConform`과 현재 revision이 `2` 이상일 때의 `optionalConform`으로 표현되어 있다.

### 명령

| ID | 이름 | 방향 | 호출 권한 | 적합성 | response |
|---|---|---|---|---|---|
| `0x00` | `ResetCondition` | `commandToServer` | `operate` | 선택 | `Y` |

제공된 XML에는 `ResetCondition`의 입력 필드와 이벤트 정의가 없다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml`

### 클러스터 구성

| 항목 | 값 |
|---|---|
| name | `HEPA Filter Monitoring` |
| domain | `Measurement & Sensing` |
| code | `0x0071` |
| define | `HEPA_FILTER_MONITORING_CLUSTER` |
| client | 활성화, `tick="false"`, `init="false"` |
| server | 활성화, `tick="false"`, `init="false"` |
| globalAttribute | `code="0xFFFD"`, `side="either"`, `value="1"` |

XML 주석은 이 파일이 Alchemy로 생성되었으며 직접 편집하지 않도록 명시한다. 생성 원본은 `src/app_clusters/ResourceMonitoring.adoc`이다.

### 속성 및 명령 매핑

모든 클러스터별 속성은 `side="server"`로 정의된다.

| ID | 이름 | define | SDK 타입 | 주요 설정 |
|---|---|---|---|---|
| `0x0000` | `Condition` | `CONDITION` | `percent` | `optional="true"`, `CON` 지원 시 필수 |
| `0x0001` | `DegradationDirection` | `DEGRADATION_DIRECTION` | `DegradationDirectionEnum` | `max="1"`, `optional="true"`, `CON` 지원 시 필수 |
| `0x0002` | `ChangeIndication` | `CHANGE_INDICATION` | `ChangeIndicationEnum` | `max="2"` |
| `0x0003` | `InPlaceIndicator` | `IN_PLACE_INDICATOR` | `boolean` | `optional="true"` |
| `0x0004` | `LastChangedTime` | `LAST_CHANGED_TIME` | `epoch_s` | `writable="true"`, `isNullable="true"`, `optional="true"` |
| `0x0005` | `ReplacementProductList` | `REPLACEMENT_PRODUCT_LIST` | `array` | `entryType="ReplacementProductStruct"`, `length="5"`, `REP` 지원 시 필수 |

`ResetCondition`은 `code="0x00"`, `source="client"`, `optional="true"`로 정의된다.

SDK XML의 명령 설명에는 초기 구성과 같은 자원 가용 상태로 되돌리기 위해 `Condition`과 `ChangeIndicator`를 재설정한다고 적혀 있다. 다만 실제 속성 정의와 구현에서 사용하는 이름은 `ChangeIndication`이다.

### 공통 데이터 타입

- `DegradationDirectionEnum`, `ChangeIndicationEnum`, `ProductIdentifierTypeEnum`은 `enum8`이다.
- 세 enum은 `0x0071`, `0x0072`, `0x0079`에 연결된다.
- `ReplacementProductStruct`는 각 클러스터에 대해 별도로 선언된다.
  - `ProductIdentifierType`: `ProductIdentifierTypeEnum`, `max="0x04"`
  - `ProductIdentifierValue`: `char_string`, `length="20"`

XML 주석에 따르면 구조체를 별도로 선언하는 이유는 `ProductIdentifierTypeEnum`이 각 구현의 네임스페이스에 속하기 때문이다.

### 생성 메타데이터

출처:

- `zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h`
- `zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h`

두 파일은 `src/controller/data_model/controller-clusters.matter`를 기반으로 생성되었으며, 각각 `kRevision = 1`을 정의한다.

`HepaFilterMonitoring`의 메타데이터는 다음과 같다.

- 모든 클러스터별 속성의 읽기 권한: `Access::Privilege::kView`
- `LastChangedTime`의 쓰기 권한: `Access::Privilege::kOperate`
- 나머지 속성의 쓰기 권한: `std::nullopt`
- `ReplacementProductList`의 품질 플래그: `DataModel::AttributeQualityFlags::kListAttribute`
- `kMandatoryMetadata`의 항목: `ChangeIndication::kMetadataEntry`
- `ResetCondition`의 호출 권한: `Access::Privilege::kOperate`
- `Events` 네임스페이스: 비어 있음

### 스펙과 제공된 SDK의 차이

| 항목 | 스펙 | 제공된 SDK 및 구현 |
|---|---|---|
| revision | `2` | SDK XML과 생성 메타데이터는 `1` |
| `Medium` | `0x0006`으로 정의 | SDK XML 및 제공된 속성 처리 코드에 정의 없음 |
| 재설정 대상 이름 | `ChangeIndication` | SDK XML 설명과 일부 주석에는 `ChangeIndicator`, 실제 코드는 `ChangeIndication` |

## 구현

### 주요 파일과 역할

| 파일 | 역할 |
|---|---|
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h` | 서버 클래스와 속성 접근 API 선언 |
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp` | 속성 처리, 명령 처리, 영속 데이터 로드 및 기본 재설정 동작 |
| `src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h` | 애플리케이션 초기화 및 재설정 확장 지점 |
| `src/app/clusters/resource-monitoring-server/CodegenIntegration.h` | 기존 `Instance` 인터페이스 |
| `src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp` | codegen 레지스트리 등록 및 선택 속성 구성 |
| `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h` | 저장소 마이그레이션을 수행하는 파생 클래스 |
| `src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp` | `Startup` 시 마이그레이션 실행 |
| `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h` | 마이그레이션 함수 선언 |
| `src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp` | `LastChangedTime` 마이그레이션 |
| `src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h` | 교체 제품 목록 반복 인터페이스 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h` | 공통 enum, 속성 메타데이터 참조, 구조체 및 명령 타입 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp` | `ResetCondition`의 TLV 디코딩 |
| `src/app/clusters/resource-monitoring-server/resource-monitoring-server.h` | `CodegenIntegration.h`를 포함하는 진입 헤더 |

### 클래스 구성 및 생명주기

`ResourceMonitoringCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 다음 구성을 받는다.

- `aEndpointId`
- `aClusterId`
- `enabledFeatures`
- `optionalAttributeSet`
- `aDegradationDirection`
- `aResetConditionCommandSupported`

`OptionalAttributeSet`에는 `InPlaceIndicator`와 `LastChangedTime`만 포함된다. `Condition`, `DegradationDirection`, `ReplacementProductList`의 노출 여부는 기능 비트로 결정된다.

`Instance`는 `RegisteredServerCluster<CodegenResourceMonitoringCluster>`를 `mCluster`로 보유하며 다음 순서로 동작한다.

1. `ConstructOptionalAttributeSet`에서 `emberAfContainsServer`를 확인한다.
2. `emberAfContainsAttribute`로 `InPlaceIndicator`와 `LastChangedTime`의 존재 여부를 확인한다.
3. `mCluster`를 생성한다.
4. `SetDelegate`를 호출한다.
5. `RegisterInstance`에서 `CodegenDataModelProvider::Instance().Registry().Register`를 호출한다.
6. 소멸자에서 `Unregister`를 호출한다.

`SetDelegate`는 `nullptr`에 대해 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다. 유효한 포인터이면 delegate의 `SetInstance`를 호출한 다음 `Init`을 실행한다. 호출자는 delegate가 클러스터 인스턴스보다 오래 유지되도록 해야 한다.

제공된 `Instance` 생성자는 `SetDelegate`의 반환값을 무시한다. 등록 실패 로그는 `CHIP_CODEGEN_CONFIG_ENABLE_CODEGEN_INTEGRATION_LOOKUP_ERRORS`가 활성화된 경우에만 출력된다.

`Instance::Init`은 내부 클러스터의 `Init`으로 전달되며, 제공된 `ResourceMonitoringCluster::Init`은 `CHIP_NO_ERROR`를 반환한다.

다음 콜백은 빈 구현이다.

- `MatterHepaFilterMonitoringClusterInitCallback`
- `MatterHepaFilterMonitoringClusterShutdownCallback`
- `MatterActivatedCarbonFilterMonitoringClusterInitCallback`
- `MatterActivatedCarbonFilterMonitoringClusterShutdownCallback`

### 내부 값과 enum

| 멤버 | 초기화 |
|---|---|
| `mCondition` | `100` |
| `mDegradationDirection` | 멤버 초기값은 `DegradationDirectionEnum::kDown`, 생성자에서 전달값으로 초기화 |
| `mChangeIndication` | `ChangeIndicationEnum::kOk` |
| `mInPlaceIndicator` | `true` |
| `mLastChangedTime` | `DataModel::Nullable<uint32_t>` |
| `mReplacementProductListManager` | `nullptr` |

공통 구현 enum은 다음 이름과 값을 사용한다.

| 타입 | 항목 |
|---|---|
| `ChangeIndicationEnum` | `kOk = 0x00`, `kWarning = 0x01`, `kCritical = 0x02`, `kUnknownEnumValue = UINT8_MAX` |
| `DegradationDirectionEnum` | `kUp = 0x00`, `kDown = 0x01`, `kUnknownEnumValue = UINT8_MAX` |
| `Feature` | `kCondition = 0x1`, `kWarning = 0x2`, `kReplacementProductList = 0x4` |
| `ProductIdentifierTypeEnum` | `kUpc = 0x00`, `kGtin8 = 0x01`, `kEan = 0x02`, `kGtin14 = 0x03`, `kOem = 0x04` |

`kUnknownEnumValue`는 알 수 없는 수신 enum 값을 처리하기 위한 보조 값이며, 주석은 이 값을 송신하지 않도록 명시한다.

### 속성 목록 및 읽기

`Attributes`는 `HepaFilterMonitoring::Attributes::kMandatoryMetadata`에 다음 조건부 항목을 추가한다.

| 속성 | 노출 조건 |
|---|---|
| `Condition` | `Feature::kCondition` |
| `DegradationDirection` | `Feature::kCondition` |
| `InPlaceIndicator` | `mOptionalAttributeSet`에 포함 |
| `LastChangedTime` | `mOptionalAttributeSet`에 포함 |
| `ReplacementProductList` | `Feature::kReplacementProductList` |

`ReadAttribute`는 내부 값 또는 전용 읽기 함수를 사용한다.

- `Condition`, `DegradationDirection`, `ChangeIndication`, `InPlaceIndicator`, `LastChangedTime`: 해당 멤버 인코딩
- `FeatureMap`: `mEnabledFeatures` 인코딩
- `ReplacementProductList`: `ReadReplaceableProductList` 호출
- `ClusterRevision`: 클러스터 ID가 `HepaFilterMonitoring::Id`이면 `HepaFilterMonitoring::kRevision`, 그 외에는 `ActivatedCarbonFilterMonitoring::kRevision` 인코딩
- 나머지 속성: `UnsupportedAttribute`

### 속성 쓰기와 애플리케이션 API

`WriteImpl`이 처리하는 속성은 `LastChangedTime`뿐이다.

- `mContext`가 없으면 `Status::InvalidInState`를 반환한다.
- `AttributePersistence::DecodeAndStoreNativeEndianValue`로 디코딩 및 저장한다.
- 다른 속성에는 `UnsupportedWrite`를 반환한다.

`WriteAttribute`는 `NotifyAttributeChangedIfSuccess`를 사용한다.

| 갱신 API | 동작 |
|---|---|
| `UpdateCondition` | 값을 대입하고 변경 시 통지. 제공된 함수에는 범위 검사 없음 |
| `UpdateChangeIndication` | `kWarning` 설정 시 `Feature::kWarning`이 없으면 `InvalidValue`; 값 변경 시 통지 |
| `UpdateInPlaceIndicator` | 값 변경 시 통지 |
| `UpdateLastChangedTime` | 컨텍스트 확인 후 값 변경 시 영속 저장, 저장 성공 후 통지 |

`UpdateLastChangedTime`은 값이 같으면 저장 없이 `Success`를 반환한다. 저장 실패 시 `Failure`를 반환하지만, 메모리의 `mLastChangedTime`은 저장 호출 전에 변경된다.

조회 API는 다음과 같으며, `Instance`에서도 내부 클러스터로 전달된다.

- `GetCondition`
- `GetChangeIndication`
- `GetDegradationDirection`
- `GetInPlaceIndicator`
- `GetLastChangedTime`

### 영속 저장 및 마이그레이션

`ResourceMonitoringCluster::Startup`은 다음 순서로 동작한다.

1. `DefaultServerCluster::Startup` 호출
2. `LoadPersistentAttributes` 호출
3. `CHIP_NO_ERROR` 반환

`LoadPersistentAttributes`는 `AttributePersistence::LoadNativeEndianValue<uint32_t>`로 `LastChangedTime`을 읽는다. 이전 값을 읽지 못하면 `null`을 기본값으로 사용한다.

`CodegenResourceMonitoringCluster::Startup`은 공통 `Startup` 호출 전에 저장소 마이그레이션을 수행한다.

- 원본: `GetSafeAttributePersistenceProvider()`가 반환하는 `SafeAttributePersistenceProvider`
- 대상: `context.attributeStorage`
- 원본 제공자가 있을 때만 `MigrateResourceMonitoringServerStorage` 호출
- 마이그레이션 오류는 `LogErrorOnFailure`로 기록하고 이후 공통 `Startup` 진행

`MigrateResourceMonitoringServerStorage`의 대상은 `LastChangedTime` 하나이다.

- 크기: `sizeof(uint32_t)`
- `isScalar`: `true`
- 버퍼 크기: `MaxAttrMigrationValueSize(attributesToUpdate)`
- 실제 이전 함수: `MigrateFromSafeToAttributePersistenceProvider`

`static_assert`로 `HepaFilterMonitoring`과 `ActivatedCarbonFilterMonitoring`의 `LastChangedTime` ID가 같은지 확인한다.

### `ResetCondition` 처리

`AcceptedCommands`는 `mResetConditionCommandSupported`가 참일 때만 `ResetCondition`을 등록한다.

`InvokeCommand`는 `ResetCondition`을 디코딩한 뒤 `ResetCondition`을 호출한다. 다른 명령에는 `Status::UnsupportedCommand`를 반환한다.

`DecodableType::Decode`는 입력이 `TLV::kTLVType_Structure`인지 확인하고 컨테이너를 순회한다. 별도의 명령 필드는 추출하지 않는다.

실제 재설정은 `mDelegate->OnResetCondition()`에 위임한다. 기본 `Delegate::OnResetCondition`의 순서는 다음과 같다.

1. `PreResetCondition` 호출
   - `Success`가 아니면 속성 재설정 없이 해당 상태 반환
2. `Feature::kCondition` 지원 시 `Condition` 재설정
   - `DegradationDirectionEnum::kDown`: `100`
   - `DegradationDirectionEnum::kUp`: `0`
3. `ChangeIndication`을 `ChangeIndicationEnum::kOk`로 변경
4. 선택 속성 `LastChangedTime` 지원 시 현재 시각 조회
   - `GetClock_RealTimeMS` 성공 시 초 단위로 변환하여 `UpdateLastChangedTime` 호출
   - 시각 조회 실패 시 갱신하지 않음
5. `PostResetCondition`의 결과 반환

`PreResetCondition`과 `PostResetCondition`의 기본 반환값은 `Success`이다. 기본 재설정 함수는 개별 `Update...` 호출의 반환값을 검사하지 않는다.

`Delegate::Init`은 순수 가상 함수이다. 애플리케이션은 `OnResetCondition` 전체를 재정의할 수 있지만, 헤더는 가능하면 `PreResetCondition`과 `PostResetCondition`을 사용하는 방식을 권장한다.

`PostResetCondition`이 실패해도 이미 변경된 속성은 되돌리지 않는다. 실패할 수 있는 사전 검사는 `PreResetCondition`에서 수행하도록 문서화되어 있다.

### 교체 제품 목록

`ReplacementProductListManager`는 다음 인터페이스를 제공한다.

- `kReplacementProductListMaxSize = 5u`
- `Reset`: `mIndex`를 `0`으로 설정
- `Next(ReplacementProductStruct & item)`: 다음 항목 제공
- 목록 종료 상태: `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`

`ReadReplaceableProductList`는 관리자가 없으면 빈 목록을 인코딩한다. 관리자가 있으면 `Reset` 이후 `Next`를 반복 호출하여 항목을 인코딩하고, `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 정상 종료로 처리한다.

제공된 읽기 루프에는 목록 항목 수를 직접 제한하는 검사가 없다.

`ReplacementProductStruct`는 `HepaFilterMonitoring::Structs::ReplacementProductStruct::Type`을 비공개 상속한다.

- 내부 버퍼 크기: `kProductIdentifierValueMaxNameLength = 20u`
- `SetProductIdentifierValue`는 빈 값 또는 버퍼 크기를 초과하는 값에 `CHIP_ERROR_INVALID_ARGUMENT`를 반환
- 유효한 값은 내부 버퍼에 복사
- 복사 생성자는 삭제됨
- 대입 연산자는 setter를 사용해 값 복사
- 생성 타입의 `Encode`를 공개

## 관련 문서

### 사용 안내

출처: `src/app/clusters/resource-monitoring-server/README.md`

README는 다음 사용 절차를 설명한다.

1. `ResourceMonitoring::Instance`를 상속하는 클래스 생성
2. `OnResetCondition` 구현
3. 필요하면 `AppInit` 구현
4. 주 파일에서 인스턴스 생성
5. 인스턴스의 `.Init()` 호출

참조 위치로 `examples/resource-monitoring-app/`의 `src/instances` 및 `include/instances` 디렉터리를 제시한다.

또한 Zap accessor 함수는 실제 값을 반환하지 않으므로, 속성 접근에는 인스턴스의 `Update...` 및 `Get...` 함수를 사용하도록 명시한다.

**문서와 제공된 구현의 차이:** README는 상속 클래스의 `OnResetCondition`과 `AppInit`을 설명하지만, 제공된 코드의 확장 인터페이스는 `Delegate::Init`, `Delegate::OnResetCondition`, `Delegate::PreResetCondition`, `Delegate::PostResetCondition`이다. 실제 `Instance` 생성자에서도 delegate를 연결한 뒤 레지스트리에 등록한다.

### 별칭 클러스터 추가 안내

README는 다음 절차를 제시한다.

1. 스펙을 `src/app/zap-templates/zcl/data-model/chip`의 XML로 작성
2. `resource-monitoring-cluster-objects.h`의 `AliasedClusters`에 클러스터 ID 추가
3. zap 코드 재생성
4. all-clusters-app/resource-monitoring 예제를 확장하여 새 클러스터 포함

제공된 `resource-monitoring-cluster-objects.h`에는 `AliasedClusters` 선언이 나타나지 않는다.

### 추가 참조

- `CodegenIntegration.h`의 생성자 설명은 기존 코드 유지 사례로 `examples/placeholder/linux/resource-monitoring-delegates.cpp`를 언급한다.
- `resource-monitoring-server.h`는 현재 `CodegenIntegration.h`를 포함한다.
- 예제 경로는 문서와 주석에 제시되어 있으나, 해당 예제 소스 본문은 제공되지 않았다.

## 관련 페이지

**사용 기기**

- [Air Purifier](../device-types/air-purifier.md) (사용 클러스터: HEPA Filter Monitoring `0x0071`, Activated Carbon Filter Monitoring `0x0072`)
- [Extractor Hood](../device-types/extractor-hood.md) (사용 클러스터: HEPA Filter Monitoring `0x0071`, Activated Carbon Filter Monitoring `0x0072`)
- [Humidity Conditioner](../device-types/humidity-conditioner.md) (사용 클러스터: Water Tank Level Monitoring `0x0079`)
- [Refrigerator](../device-types/refrigerator.md) (사용 클러스터: Activated Carbon Filter Monitoring `0x0072`)
- [Room Air Conditioner](../device-types/room-air-conditioner.md) (사용 클러스터: HEPA Filter Monitoring `0x0071`, Activated Carbon Filter Monitoring `0x0072`)
