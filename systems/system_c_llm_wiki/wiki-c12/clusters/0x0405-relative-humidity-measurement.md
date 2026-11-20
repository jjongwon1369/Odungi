---
entity: Relative Humidity Measurement
ids: ['0x0405']
source_paths: ['data_model/1.7/clusters/WaterContentMeasurement.xml', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp', 'src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h', 'src/app/clusters/relative-humidity-measurement-server/README.md', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp', 'src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h', 'src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml', 'zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Relative Humidity Measurement

## 개요

`Relative Humidity Measurement`는 상대 습도 측정 설정과 측정값 보고를 위한 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0405` |
| PICS 코드 | `RH` |
| 스펙 분류 | hierarchy: `base`, role: `application`, scope: `Endpoint` |
| SDK 도메인 | `Measurement & Sensing` |
| 구현 클래스 | `chip::app::Clusters::RelativeHumidityMeasurementCluster` |

구현은 code-driven 방식을 사용한다. `MeasuredValue`, `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`의 Ember attribute accessors는 더 이상 제공되지 않으며, 측정값은 `SetMeasuredValue`로 갱신한다.

## 스펙

출처: `data_model/1.7/clusters/WaterContentMeasurement.xml`

`Water Content Measurement Clusters`의 revision은 `5`이며, 해당 파일에서 `Relative Humidity Measurement`를 정의한다.

### 속성

모든 속성은 `uint16`이며, 읽기 권한은 `view`이다.

| ID | 이름 | 적합성 | nullable | persistence | 제약 |
|---|---|---|---|---|---|
| `0x0000` | `MeasuredValue` | 필수 | true | 별도 지정 없음 | `MinMeasuredValue` 이상, `MaxMeasuredValue` 이하 |
| `0x0001` | `MinMeasuredValue` | 필수 | true | `fixed` | 최대 `9999` |
| `0x0002` | `MaxMeasuredValue` | 필수 | true | `fixed` | `MinMeasuredValue + 1` 이상, `10000` 이하 |
| `0x0003` | `Tolerance` | 선택 | 별도 지정 없음 | `fixed` | 최대 `2048` |

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 필수 전역 속성 `ClusterRevision` 추가 |
| `2` | `CCB 2241` |
| `3` | 새로운 데이터 모델 형식과 표기법 적용 |
| `4` | `P` quality 제거 |
| `5` | `MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`에 `F` quality 추가 |

제공된 스펙 XML에는 명령 및 이벤트 정의가 없다.

## SDK 정의

### ZAP 데이터 모델

출처: `src/app/zap-templates/zcl/data-model/chip/relative-humidity-measurement-cluster.xml`

| 항목 | 정의 |
|---|---|
| 클러스터 이름 | `Relative Humidity Measurement` |
| 클러스터 코드 | `0x0405` |
| define | `RELATIVE_HUMIDITY_MEASUREMENT_CLUSTER` |
| client | 활성화, `tick="false"`, `init="false"` |
| server | 활성화, `tick="false"`, `tickFrequency="half"`, `init="false"` |
| 전역 속성 | `side="either"`, `code="0xFFFD"`, `value="3"` |

속성은 모두 `side="server"`, `type="int16u"`로 정의된다.

| 이름 | define | nullable | SDK에 명시된 범위 | 적합성 |
|---|---|---|---|---|
| `MeasuredValue` | `RELATIVE_HUMIDITY_MEASURED_VALUE` | true | 최대 `10000` | 선택 표시 없음 |
| `MinMeasuredValue` | `RELATIVE_HUMIDITY_MIN_MEASURED_VALUE` | true | 최대 `0x270F` | 선택 표시 없음 |
| `MaxMeasuredValue` | `RELATIVE_HUMIDITY_MAX_MEASURED_VALUE` | true | 최소 `0x0001`, 최대 `0x2710` | 선택 표시 없음 |
| `Tolerance` | `RELATIVE_HUMIDITY_TOLERANCE` | 별도 지정 없음 | 최대 `0x0800` | `optionalConform` |

이 파일은 Alchemy로 생성되었으며, 원본으로 `src/app_clusters/WaterContentMeasurement.adoc`를 명시한다.

### 생성된 메타데이터

출처: `zzz_generated/app-common/clusters/RelativeHumidityMeasurement/Metadata.h`

- `src/controller/data_model/controller-clusters.matter`를 기반으로 생성된다.
- `chip::app::Clusters::RelativeHumidityMeasurement::kRevision`은 `3`이다.
- 각 속성의 `kMetadataEntry`는 읽기 권한을 `Access::Privilege::kView`로 지정하고, 쓰기 권한은 `std::nullopt`로 지정한다.
- `kMandatoryMetadata`에는 다음 세 항목이 포함된다.
  - `MeasuredValue::kMetadataEntry`
  - `MinMeasuredValue::kMetadataEntry`
  - `MaxMeasuredValue::kMetadataEntry`
- `Tolerance::kMetadataEntry`는 정의되어 있지만 `kMandatoryMetadata`에는 포함되지 않는다.
- `Commands`와 `Events` 네임스페이스는 비어 있다.

### 스펙과 SDK의 차이

- 스펙 XML의 revision은 `5`이지만, SDK XML의 `0xFFFD` 값과 생성된 `kRevision`은 `3`이다.
- 스펙은 `MeasuredValue`와 `MaxMeasuredValue`에 속성 간 관계 제약을 정의한다. SDK XML은 이 관계 대신 개별 속성의 수치 범위를 명시한다.
- 스펙의 `persistence="fixed"`는 제공된 SDK XML에 명시되어 있지 않다. 구현과 README에서는 해당 속성을 시작 시 설정하고 런타임에는 변경하지 않는 방식으로 취급한다.

## 구현

### 클래스와 구성

출처:

- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.h`
- `src/app/clusters/relative-humidity-measurement-server/RelativeHumidityMeasurementCluster.cpp`

`RelativeHumidityMeasurementCluster`는 `DefaultServerCluster`를 상속한다.

| 구성 요소 | 역할 |
|---|---|
| `Config` | 생성 시 측정 범위와 선택 속성 설정 전달 |
| `minMeasuredValue` | nullable 최소 측정값 |
| `maxMeasuredValue` | nullable 최대 측정값 |
| `WithTolerance(uint16_t value)` | `mTolerance` 설정 및 `Tolerance` 선택 속성 활성화 |
| `OptionalAttributeSet` | `RelativeHumidityMeasurement::Attributes::Tolerance::Id`의 포함 여부 관리 |

`EndpointId`만 받는 생성자는 `Config{}`를 사용하는 생성자로 위임한다. `Config`는 `mTolerance`를 `0`으로 초기화하며, `WithTolerance` 호출 시 해당 속성을 활성화한다.

### 생성 시 검증

생성자는 다음 조건을 `VerifyOrDie`로 검증한다.

- `minMeasuredValue`가 null이 아니면 `9999` 이하이다.
- `minMeasuredValue`와 `maxMeasuredValue`가 모두 null이 아니면 `maxMeasuredValue >= minMeasuredValue + 1`이다.
- `maxMeasuredValue`가 null이 아니면 `10000` 이하이다.
- `Tolerance`가 활성화되어 있으면 `mTolerance <= 2048`이다.

검증 후 구성값을 `mMinMeasuredValue`, `mMaxMeasuredValue`, `mTolerance`에 저장한다.

### 속성 읽기와 목록

`ReadAttribute`는 다음 값을 인코딩한다.

| 속성 | 반환 값 |
|---|---|
| `ClusterRevision` | `RelativeHumidityMeasurement::kRevision` |
| `FeatureMap` | `uint32_t` 값 `0` |
| `MeasuredValue` | `mMeasuredValue` |
| `MinMeasuredValue` | `mMinMeasuredValue` |
| `MaxMeasuredValue` | `mMaxMeasuredValue` |
| `Tolerance` | `mTolerance` |

처리 대상이 아닌 속성은 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Attributes`는 `AttributeListBuilder`를 사용하여 `kMandatoryMetadata`와 활성화된 선택 속성을 목록에 추가한다. 선택 속성 후보는 `Tolerance::kMetadataEntry`이다.

### 측정값 갱신

`SetMeasuredValue(DataModel::Nullable<uint16_t> measuredValue)`의 동작은 다음과 같다.

1. null 값은 범위 검사를 생략한다.
2. null이 아닌 값은 `IsValueInHumidityRange`로 검사한다.
   - `10000` 이하이어야 한다.
   - `mMinMeasuredValue`가 null이 아니면 그 이상이어야 한다.
   - `mMaxMeasuredValue`가 null이 아니면 그 이하이어야 한다.
3. 범위를 벗어나면 `CHIP_IM_GLOBAL_STATUS(ConstraintError)`를 반환한다.
4. 유효한 값은 `SetAttributeValue(mMeasuredValue, measuredValue, MeasuredValue::Id)`로 반영하고 `CHIP_NO_ERROR`를 반환한다.

조회용 함수는 `GetMeasuredValue`, `GetMinMeasuredValue`, `GetMaxMeasuredValue`이다.

### ZAP/Codegen 통합

출처:

- `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.h`
- `src/app/clusters/relative-humidity-measurement-server/CodegenIntegration.cpp`

서버 인스턴스는 `LazyRegisteredServerCluster<RelativeHumidityMeasurementCluster>` 배열인 `gServers`에서 관리한다.

- `kRelativeHumidityFixedClusterCount`는 `RelativeHumidityMeasurement::StaticApplicationConfig::kFixedClusterConfig.size()`이다.
- `kRelativeHumidityMaxClusterCount`는 고정 인스턴스 수에 `CHIP_DEVICE_CONFIG_DYNAMIC_ENDPOINT_COUNT`를 더한 값이다.

`IntegrationDelegate::CreateRegistration`은 다음 순서로 구성한다.

1. `MinMeasuredValue::GetDefaultOr`와 `MaxMeasuredValue::GetDefaultOr`로 Ember attribute store의 기본값을 읽는다. 기본값이 없으면 `DataModel::NullNullable`을 사용한다.
2. 두 값이 모두 null이 아니면서 `maxMeasuredValue < minMeasuredValue + 1`이면 두 값을 모두 null로 변경한다. 코드 주석은 ZAP 기본값 `0/0`을 예로 든다.
3. 선택 속성에 `Tolerance::Id`가 있으면 `Tolerance::GetDefaultOr`로 값을 읽는다. 기본값은 `0`이며, `config.WithTolerance(tolerance)`로 적용한다.
4. 해당 `gServers` 항목을 생성하고 등록 정보를 반환한다.

| 함수 | 동작 |
|---|---|
| `MatterRelativeHumidityMeasurementClusterInitCallback` | `CodegenClusterIntegration::RegisterServer` 호출. `fetchFeatureMap`은 `false`, `fetchOptionalAttributes`는 `true` |
| `MatterRelativeHumidityMeasurementClusterShutdownCallback` | `CodegenClusterIntegration::UnregisterServer` 호출 |
| `IntegrationDelegate::FindRegistration` | 생성된 인스턴스를 반환하며, 생성되지 않았으면 `nullptr` 반환 |
| `IntegrationDelegate::ReleaseRegistration` | 해당 인스턴스의 `Destroy` 호출 |
| `FindClusterOnEndpoint` | 지정한 `EndpointId`에 등록된 인스턴스를 조회하며, 없으면 `nullptr` 반환 |
| `SetMeasuredValue` | 지정한 `EndpointId`의 인스턴스에 갱신을 위임하며, 인스턴스가 없으면 `CHIP_ERROR_NOT_FOUND` 반환 |

마지막 두 함수는 `chip::app::Clusters::RelativeHumidityMeasurement` 네임스페이스에 제공된다.

## 관련 문서

### 사용 가이드

`src/app/clusters/relative-humidity-measurement-server/README.md`

문서에서 안내하는 사용 순서는 다음과 같다.

1. `.cpp` 파일의 전역 또는 정적 범위에 `RegisteredServerCluster`를 선언한다.
2. 필요한 경우 `Config`로 최소·최대 범위와 `Tolerance`를 설정한다.
3. 애플리케이션 초기화에서 `chip::app::CodegenDataModelProvider::Instance().Registry().Register`에 `gHumidityCluster.Registration()`을 전달한다.
4. 센서 측정값이 들어오면 Matter task context에서 `SetMeasuredValue`를 호출한다. 별도 스레드에서 호출할 경우 `ScheduleWork`를 사용한다.

ZAP/Codegen 기반 애플리케이션은 `CodegenIntegration.h`와 `CodegenIntegration.cpp`의 호환 계층을 사용한다. 측정값 갱신에는 `chip::app::Clusters::RelativeHumidityMeasurement::SetMeasuredValue`를 사용할 수 있다.

`MinMeasuredValue`, `MaxMeasuredValue`, `Tolerance`는 시작 시 한 번 설정하는 fixed 속성이며 런타임에는 변경할 수 없다. 테스트나 동적 엔드포인트에서 코드로 설정해야 하는 경우 생성 시 `Config`를 전달한다.

## 관련 페이지

**사용 기기**

- [Humidity Conditioner](../device-types/humidity-conditioner.md)
- [Room Air Conditioner](../device-types/room-air-conditioner.md)
