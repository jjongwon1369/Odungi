---
entity: Relative Humidity Measurement
ids: ['0x0405']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h', 'src/app/clusters/relative-humidity-measurement-server/README.md', 'data_model/1.7/clusters/WaterContentMeasurement.xml', 'zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Relative Humidity Measurement

## 개요

상대 습도 측정 설정과 측정값 보고를 위한 클러스터이다. 제공된 구현은 code-driven 방식이며, 측정값은 `SetMeasuredValue`로 갱신한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Relative Humidity Measurement` |
| 클러스터 ID | `0x0405` |
| PICS 코드 | `RH` |
| SDK 도메인 | `Measurement & Sensing` |
| 구현 클래스 | `chip::app::Clusters::RelativeHumidityMeasurementCluster` |

`MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`는 시작 시 설정하는 고정 속성이며, 제공된 문서에 따르면 런타임에 변경할 수 없다.

## 스펙

출처: `data_model/1.7/clusters/WaterContentMeasurement.xml`

### 분류 및 리비전

| 항목 | 값 |
|---|---|
| 스펙 그룹 이름 | `Water Content Measurement Clusters` |
| 리비전 | `5` |
| hierarchy | `base` |
| role | `application` |
| scope | `Endpoint` |

### 속성

모든 속성은 `uint16` 타입이며, 읽기 접근 권한은 `view`이다.

| ID | 이름 | 필수 여부 | nullable | persistence | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | 필수 | 허용 | 별도 지정 없음 | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 |
| `0x0001` | `MinMeasuredValue` | 필수 | 허용 | `fixed` | 최대 `9999` |
| `0x0002` | `MaxMeasuredValue` | 필수 | 허용 | `fixed` | `MinMeasuredValue + 1` 이상, `10000` 이하 |
| `0x0003` | `Tolerance` | 선택 | 허용 표시 없음 | `fixed` | 최대 `2048` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | `CCB 2241` |
| `3` | 새로운 데이터 모델 형식 및 표기법 적용 |
| `4` | `P` quality 제거 |
| `5` | `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 `F` quality 추가 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml`

### 클러스터 설정

- 클러스터 코드: `0x0405`
- 매크로: `RELATIVE_HUMIDITY_MEASUREMENT_CLUSTER`
- client와 server 모두 활성화되어 있다.
- client 설정: `tick="false"`, `init="false"`
- server 설정: `tick="false"`, `tickFrequency="half"`, `init="false"`
- 전역 속성 `0xFFFD`: `side="either"`, `value="3"`

이 XML은 Alchemy로 생성되었으며, 원본으로 `src/app_clusters/WaterContentMeasurement.adoc`가 명시되어 있다. 생성 주석에는 `DO NOT EDIT`와 Git 값 `0.9.2-summer2025-124-g2b25c360b`가 포함되어 있다.

### 서버 속성 정의

| ID | 이름 | define | 타입 | nullable | XML 제약 | 선택 여부 |
|---|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | `RELATIVE_HUMIDITY_MEASURED_VALUE` | `int16u` | `true` | `max="10000"` | 선택 표시 없음 |
| `0x0001` | `MinMeasuredValue` | `RELATIVE_HUMIDITY_MIN_MEASURED_VALUE` | `int16u` | `true` | `max="0x270F"` | 선택 표시 없음 |
| `0x0002` | `MaxMeasuredValue` | `RELATIVE_HUMIDITY_MAX_MEASURED_VALUE` | `int16u` | `true` | `min="0x0001"`, `max="0x2710"` | 선택 표시 없음 |
| `0x0003` | `Tolerance` | `RELATIVE_HUMIDITY_TOLERANCE` | `int16u` | 별도 지정 없음 | `max="0x0800"` | `optionalConform` |

### 생성 메타데이터

출처: `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h`

- 생성 기준 파일은 `src/controller/data_model/controller-clusters.matter`이다.
- `RelativeHumidityMeasurement::kRevision`은 `3`이다.
- 각 속성의 `kMetadataEntry`는 읽기 권한을 `Access::Privilege::kView`로 정의하고, 쓰기 권한에는 `std::nullopt`를 사용한다.
- `kMandatoryMetadata`에는 다음 세 항목이 포함된다.
  - `MeasuredValue::kMetadataEntry`
  - `MinMeasuredValue::kMetadataEntry`
  - `MaxMeasuredValue::kMetadataEntry`
- `Tolerance::kMetadataEntry`는 별도로 정의된다.
- `Commands`와 `Events` 네임스페이스는 비어 있다.

**리비전 차이:** 제공된 스펙은 리비전 `5`이지만, SDK XML과 생성 메타데이터는 `3`을 사용한다. 구현의 `ReadAttribute`도 `RelativeHumidityMeasurement::kRevision`을 반환하므로, 제공된 메타데이터 기준 반환값은 `3`이다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h` | 클래스, `Config`, 속성 접근 API 선언 |
| `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp` | 설정 검증, 속성 읽기 및 목록 구성, 측정값 갱신 |
| `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h` | endpoint 기반 조회 및 갱신 함수 선언 |
| `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp` | ZAP/Codegen 등록, 해제 및 호환 계층 구현 |

### 클래스와 설정

`RelativeHumidityMeasurementCluster`는 `DefaultServerCluster`를 상속한다. 생성자는 `EndpointId`만 받거나, `EndpointId`와 `const Config &`를 받는다. `EndpointId`만 전달하면 `Config{}`를 사용한다.

`Config`의 구성은 다음과 같다.

| 구성원 | 용도 |
|---|---|
| `minMeasuredValue` | `DataModel::Nullable<uint16_t>` 타입의 최소 측정값 |
| `maxMeasuredValue` | `DataModel::Nullable<uint16_t>` 타입의 최대 측정값 |
| `mOptionalAttributeSet` | 선택 속성 활성화 상태 |
| `mTolerance` | 허용 오차 값이며 생성자에서 `0`으로 초기화 |

`WithTolerance(uint16_t value)`는 `mTolerance`를 설정하고, `mOptionalAttributeSet`에서 `RelativeHumidityMeasurement::Attributes::Tolerance::Id`를 활성화한 뒤 `*this`를 반환한다.

### 생성 시 검증

구현은 다음 상수를 사용한다.

| 상수 | 값 |
|---|---|
| `kMinMeasuredValueMax` | `9999` |
| `kMeasuredValueMax` | `10000` |
| `kMaxTolerance` | `2048` |

생성자는 `VerifyOrDie`로 다음 조건을 검증한다.

- `minMeasuredValue`가 null이 아니면 `9999` 이하이어야 한다.
- 두 경계가 모두 null이 아니면 `maxMeasuredValue >= minMeasuredValue + 1`이어야 한다.
- `maxMeasuredValue`가 null이 아니면 `10000` 이하이어야 한다.
- `Tolerance::Id`가 활성화되어 있으면 `mTolerance <= 2048`이어야 한다.

`minMeasuredValue`가 null인 경우에는 생성자에서 `maxMeasuredValue >= 1`을 별도로 검사하지 않는다.

### 속성 읽기와 목록

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 대상 |
|---|---|
| `ClusterRevision::Id` | `RelativeHumidityMeasurement::kRevision` |
| `FeatureMap::Id` | `uint32_t` 값 `0` |
| `MeasuredValue::Id` | `mMeasuredValue` |
| `MinMeasuredValue::Id` | `mMinMeasuredValue` |
| `MaxMeasuredValue::Id` | `mMaxMeasuredValue` |
| `Tolerance::Id` | `mTolerance` |

그 밖의 속성에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용해 `kMandatoryMetadata`와 선택 속성 `Tolerance::kMetadataEntry`를 결합한다. 선택 속성의 포함 여부는 `mOptionalAttributeSet`에 따른다.

### 측정값 갱신

`SetMeasuredValue(DataModel::Nullable<uint16_t> measuredValue)`의 동작은 다음과 같다.

1. null이 아닌 값에 대해 `IsValueInHumidityRange`를 호출한다.
2. 값이 `10000`을 초과하면 거부한다.
3. `mMinMeasuredValue`가 null이 아니면 해당 값 이상인지 확인한다.
4. `mMaxMeasuredValue`가 null이 아니면 해당 값 이하인지 확인한다.
5. 검증 실패 시 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
6. 검증을 통과하거나 입력이 null이면 `SetAttributeValue(mMeasuredValue, measuredValue, MeasuredValue::Id)`를 호출하고 `CHIP_NO_ERROR`를 반환한다.

현재 값과 경계값은 `GetMeasuredValue`, `GetMinMeasuredValue`, `GetMaxMeasuredValue`로 조회한다.

### ZAP/Codegen 통합

인스턴스는 `LazyRegisteredServerCluster<RelativeHumidityMeasurementCluster>` 타입의 `gServers`에 저장된다.

- `kRelativeHumidityFixedClusterCount`는 `RelativeHumidityMeasurement::StaticApplicationConfig::kFixedClusterConfig.size()`로 계산한다.
- `kRelativeHumidityMaxClusterCount`는 고정 인스턴스 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.

`IntegrationDelegate::CreateRegistration`은 다음 순서로 설정을 구성한다.

1. `MinMeasuredValue::GetDefaultOr`와 `MaxMeasuredValue::GetDefaultOr`로 Ember 속성 저장소의 기본값을 읽는다. 기본값이 없으면 `DataModel::NullNullable`을 사용한다.
2. 두 값이 모두 null이 아니면서 `maxMeasuredValue < minMeasuredValue + 1`이면 두 값을 모두 null로 바꾼다. 코드 주석은 ZAP 기본값 `0/0`을 예로 든다.
3. `optionalAttributeBits`에서 `Tolerance::Id`가 활성화되어 있으면 `Tolerance::GetDefaultOr`로 값을 읽는다. 기본값이 없으면 `0`을 사용하고 `config.WithTolerance(tolerance)`를 호출한다.
4. `gServers[clusterInstanceIndex].Create(endpointId, config)`로 인스턴스를 생성한다.

주요 통합 함수는 다음과 같다.

| 함수 | 동작 |
|---|---|
| `MatterRelativeHumidityMeasurementClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true` |
| `MatterRelativeHumidityMeasurementClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `FindClusterOnEndpoint` | 지정 endpoint의 클러스터를 조회하며, 없으면 `nullptr` 반환 |
| `SetMeasuredValue` | endpoint의 클러스터를 찾아 측정값 갱신. 없으면 `CHIP_ERROR_NOT_FOUND` 반환 |
| `IntegrationDelegate::FindRegistration` | 인스턴스가 생성되어 있으면 반환하고, 아니면 `nullptr` 반환 |
| `IntegrationDelegate::ReleaseRegistration` | 해당 인스턴스의 `Destroy()` 호출 |

endpoint 기반 `FindClusterOnEndpoint`와 `SetMeasuredValue`는 `chip::app::Clusters::RelativeHumidityMeasurement` 네임스페이스에 정의되어 있다.

## 관련 문서

### 사용 안내

출처: `src/app/clusters/relative-humidity-measurement-server/README.md`

문서의 주요 사용 절차는 다음과 같다.

1. `.cpp` 파일의 전역 또는 정적 범위에 `RegisteredServerCluster`를 선언한다.
2. 범위와 선택 속성이 필요하면 생성 시 `Config`를 전달한다. 문서의 설정값은 `minMeasuredValue`가 `0`, `maxMeasuredValue`가 `10000`, `WithTolerance(100)`이다.
3. 애플리케이션 초기화 시 `chip::app::CodegenDataModelProvider::Instance().Registry().Register(gHumidityCluster.Registration())`로 등록한다.
4. 센서 측정값이 들어오면 Matter task context에서 `SetMeasuredValue`를 호출한다. 별도 스레드에서는 `ScheduleWork`를 사용한다.
5. ZAP/Codegen 방식에서는 `CodegenIntegration.h`의 endpoint 기반 API를 사용한다. `MatterRelativeHumidityMeasurementClusterInitCallback`이 자동 인스턴스 생성을 담당한다.

문서는 `MeasuredValue`, `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`의 Ember attribute accessors를 더 이상 사용할 수 없다고 명시한다. 테스트나 동적 endpoint에서 경계값과 허용 오차를 지정할 때도 생성 시 `Config`를 전달해야 한다.

## 관련 페이지

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
