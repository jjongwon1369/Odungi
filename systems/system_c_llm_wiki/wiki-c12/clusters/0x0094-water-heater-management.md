---
entity: Water Heater Management
ids: ['0x0094']
source_paths: ['data_model/1.7/clusters/WaterHeaterManagement.xml', 'src/app/clusters/water-heater-management-server/CodegenIntegration.cpp', 'src/app/clusters/water-heater-management-server/CodegenIntegration.h', 'src/app/clusters/water-heater-management-server/Delegate.cpp', 'src/app/clusters/water-heater-management-server/Delegate.h', 'src/app/clusters/water-heater-management-server/WaterHeaterManagementCluster.cpp', 'src/app/clusters/water-heater-management-server/WaterHeaterManagementCluster.h', 'src/app/clusters/water-heater-management-server/WaterHeaterManagementTestEventTriggerHandler.h', 'src/app/clusters/water-heater-management-server/water-heater-management-server.h', 'src/app/zap-templates/zcl/data-model/chip/water-heater-management-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Water Heater Management

## 개요

Water Heater Management는 클라이언트가 온수 가열 장치의 동작을 제어하여 에너지 관리에 활용할 수 있도록 하는 클러스터다. 탱크의 열원과 가열 요구 상태를 제공하며, `Boost` 및 `CancelBoost`로 일시적인 가열 동작을 제어한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Water Heater Management` |
| 스펙의 클러스터 이름 | `Water Heater Management Cluster` |
| 클러스터 ID | `0x0094` |
| 리비전 | `2` |
| 도메인 | `Energy Management` |
| 분류 | hierarchy: `base`, role: `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `EWATERHTR` |

## 스펙

출처: `data_model/1.7/clusters/WaterHeaterManagement.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 이벤트 추가 및 데이터 타입 단순화 |

### 기능

두 기능 모두 선택 사항이다.

| 비트 | 코드 | 이름 | 설명 |
|---|---|---|---|
| `0` | `EM` | `EnergyManagement` | 탱크의 에너지 관리 제어 지원 |
| `1` | `TP` | `TankPercent` | 탱크 내 온수 비율 모니터링 지원 |

### 데이터 타입

#### `BoostStateEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0` | `Inactive` | 현재 `Boost`가 활성화되지 않음 |
| `1` | `Active` | 현재 `Boost`가 활성화됨 |

두 항목 모두 필수다.

#### `WaterHeaterHeatSourceBitmap`

| 비트 | 이름 | 의미 |
|---|---|---|
| `0` | `ImmersionElement1` | 침수형 가열 요소 1 |
| `1` | `ImmersionElement2` | 침수형 가열 요소 2 |
| `2` | `HeatPump` | 히트 펌프 가열 |
| `3` | `Boiler` | 가스 또는 기름 등의 보일러 가열 |
| `4` | `Other` | 기타 가열 방식 |

모든 비트 필드는 필수로 정의되어 있다.

#### `WaterHeaterBoostInfoStruct`

| 필드 ID | 이름 | 타입 | 필수 여부 및 조건 | 기본값 / 제약 |
|---|---|---|---|---|
| `0` | `Duration` | `elapsed-s` | 필수 | 최솟값 `1` |
| `1` | `OneShot` | `bool` | 선택. `TP` 지원 시 `TargetReheat`와 선택 그룹 `a` 공유 | 기본값 `false` |
| `2` | `EmergencyBoost` | `bool` | 선택 | 기본값 `false` |
| `3` | `TemporarySetpoint` | `temperature` | 선택 | 제약의 `desc`는 비어 있음 |
| `4` | `TargetPercentage` | `percent` | `TargetReheat`가 있으면 필수. 그 외에는 `TP` 지원 시 선택 | — |
| `5` | `TargetReheat` | `percent` | `TP` 지원 시 선택. `OneShot`과 선택 그룹 `a` 공유 | 최댓값 `TargetPercentage` |

`TP` 지원 시 선택 그룹 `a`의 `max="1"`에 따라 `OneShot`과 `TargetReheat`는 최대 하나만 포함할 수 있다.

### 속성

모든 속성은 읽기를 지원하며, 읽기 권한은 `view`다.

| ID | 이름 | 타입 | 필수 여부 | 추가 조건 |
|---|---|---|---|---|
| `0x0000` | `HeaterTypes` | `WaterHeaterHeatSourceBitmap` | 필수 | persistence: `fixed` |
| `0x0001` | `HeatDemand` | `WaterHeaterHeatSourceBitmap` | 필수 | — |
| `0x0002` | `TankVolume` | `uint16` | `EM` 지원 시 필수 | — |
| `0x0003` | `EstimatedHeatRequired` | `energy-mWh` | `EM` 지원 시 필수 | 최솟값 `0` |
| `0x0004` | `TankPercentage` | `percent` | `TP` 지원 시 필수 | — |
| `0x0005` | `BoostState` | `BoostStateEnum` | 필수 | — |

### 명령

두 명령 모두 필수이며, 방향은 `commandToServer`, 호출 권한은 `manage`다. XML의 `response` 값은 `Y`다.

| ID | 이름 | 필드 |
|---|---|---|
| `0x00` | `Boost` | 필수 필드 `BoostInfo`: ID `0`, 타입 `WaterHeaterBoostInfoStruct` |
| `0x01` | `CancelBoost` | 없음 |

### 이벤트

두 이벤트 모두 필수이며, 우선순위는 `info`, 읽기 권한은 `view`다.

| ID | 이름 | 필드 |
|---|---|---|
| `0x00` | `BoostStarted` | 필수 필드 `BoostInfo`: ID `0`, 타입 `WaterHeaterBoostInfoStruct` |
| `0x01` | `BoostEnded` | 없음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/water-heater-management-cluster.xml`

### 생성 정보 및 클러스터 설정

- Alchemy로 생성된 XML이며, 직접 수정하지 않도록 표시되어 있다.
- 생성 원본: `src/app_clusters/WaterHeaterManagement.adoc`
- 생성 매개변수: `in-progress`
- Git: `1.4-prerelease-ipr-69-ge15ff5700`
- 클러스터 매크로: `WATER_HEATER_MANAGEMENT_CLUSTER`
- 클러스터, 데이터 타입 및 명령의 `apiMaturity`: `provisional`
- 클라이언트와 서버 모두 활성화되어 있으며, 각각 `init="false"`, `tick="false"`로 설정되어 있다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="2"`로 정의되어 있다.

### 데이터 타입 표현

스펙과 SDK XML은 일부 타입의 표기가 다르다.

| 대상 | 스펙 타입 | SDK 타입 |
|---|---|---|
| `Duration` | `elapsed-s` | `elapsed_s` |
| `OneShot`, `EmergencyBoost` | `bool` | `boolean` |
| `TankVolume` | `uint16` | `int16u` |
| `EstimatedHeatRequired` | `energy-mWh` | `energy_mwh` |

`WaterHeaterHeatSourceBitmap`의 기반 타입은 `bitmap8`이다.

| 필드 | 마스크 |
|---|---|
| `ImmersionElement1` | `0x01` |
| `ImmersionElement2` | `0x02` |
| `HeatPump` | `0x04` |
| `Boiler` | `0x08` |
| `Other` | `0x10` |

`BoostStateEnum`의 기반 타입은 `enum8`이며, `Inactive`는 `0x00`, `Active`는 `0x01`이다.

`WaterHeaterBoostInfoStruct`는 스펙과 동일한 필드 ID와 이름을 사용한다.

- `Duration`에는 `min="1"`이 지정되어 있다.
- 나머지 필드는 모두 `optional="true"`다.
- `OneShot`과 `EmergencyBoost`의 기본값은 `0`이다.
- 스펙의 선택 그룹과 `TargetReheat`에 대한 `TargetPercentage` 상한 관계는 제공된 SDK 구조체 정의에 명시되어 있지 않다.

### 속성 정의

모든 속성은 `side="server"`로 정의되어 있다.

| ID | 이름 | `define` | SDK 타입 | 기본값 | 명시된 범위 |
|---|---|---|---|---|---|
| `0x0000` | `HeaterTypes` | `HEATER_TYPES` | `WaterHeaterHeatSourceBitmap` | `0x00` | `0x00`–`0x1F` |
| `0x0001` | `HeatDemand` | `HEAT_DEMAND` | `WaterHeaterHeatSourceBitmap` | `0x00` | `0x00`–`0x1F` |
| `0x0002` | `TankVolume` | `TANK_VOLUME` | `int16u` | `0` | — |
| `0x0003` | `EstimatedHeatRequired` | `ESTIMATED_HEAT_REQUIRED` | `energy_mwh` | `0` | 최솟값 `0` |
| `0x0004` | `TankPercentage` | `TANK_PERCENTAGE` | `percent` | `0` | — |
| `0x0005` | `BoostState` | `BOOST_STATE` | `BoostStateEnum` | `0` | `0x00`–`0x01` |

`TankVolume`, `EstimatedHeatRequired`, `TankPercentage`는 `optional="true"`로 표시되어 있지만, 각각 `EM`, `EM`, `TP` 기능 지원 시 필수라는 적합성 조건도 포함한다.

### 명령 및 이벤트 정의

- `Boost` (`0x00`): 클라이언트가 가열 장치에 `Boost` 상태 진입을 요청한다. 인자는 `BoostInfo`다.
- `CancelBoost` (`0x01`): 진행 중인 `Boost` 동작의 취소를 요청한다.
- 두 명령 모두 `source="client"`, `optional="false"`이며 호출 권한은 `manage`다.

SDK 이벤트 ID는 다음과 같이 표기되어 있다.

| ID | 이름 | 발생 조건 |
|---|---|---|
| `0x0000` | `BoostStarted` | `Boost` 명령이 수락될 때마다 발생해야 함 |
| `0x0001` | `BoostEnded` | `BoostState`가 `Active`에서 `Inactive`로 전환될 때마다 발생해야 함 |

두 이벤트 모두 `side="server"`, `priority="info"`다. `BoostStarted`는 `BoostInfo` 필드를 포함한다.

## 구현

구현의 주요 클래스는 `chip::app::Clusters::WaterHeaterManagement` 네임스페이스에 있다.

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/water-heater-management-server/CodegenIntegration.cpp` | `Instance`의 등록, 등록 해제 및 소멸 처리 |
| `src/app/clusters/water-heater-management-server/CodegenIntegration.h` | 기존 `Instance` API를 유지하는 호환 래퍼 |
| `src/app/clusters/water-heater-management-server/Delegate.cpp` | 이벤트 생성 요청 전달 |
| `src/app/clusters/water-heater-management-server/Delegate.h` | 장치 제어, 속성 조회 및 이벤트 생성 인터페이스 |
| `src/app/clusters/water-heater-management-server/WaterHeaterManagementCluster.cpp` | 속성 읽기, 명령 처리, 이벤트 생성 및 메타데이터 목록 구현 |
| `src/app/clusters/water-heater-management-server/WaterHeaterManagementCluster.h` | `WaterHeaterManagementCluster` 선언 |
| `src/app/clusters/water-heater-management-server/WaterHeaterManagementTestEventTriggerHandler.h` | 테스트 트리거 값과 처리기 정의 |
| `src/app/clusters/water-heater-management-server/water-heater-management-server.h` | 하위 호환용 헤더 |

### `WaterHeaterManagementCluster`의 구성과 수명

`WaterHeaterManagementCluster`는 `DefaultServerCluster`를 상속한다.

생성자는 `EndpointId aEndpointId`, `Delegate & aDelegate`, `Feature aFeature`를 받아 다음을 수행한다.

- `DefaultServerCluster`를 `{ aEndpointId, WaterHeaterManagement::Id }`로 초기화한다.
- `mDelegate`와 `BitMask<Feature>` 타입의 `mFeature`를 설정한다.
- `mDelegate.SetEndpointId(aEndpointId)`를 호출한다.
- `mDelegate.SetCluster(this)`로 역참조를 연결한다.

소멸자는 `mDelegate.SetCluster(nullptr)`로 연결을 해제한다. `HasFeature(Feature aFeature)`는 `mFeature.Has(aFeature)`를 반환한다.

### `Instance` 호환 래퍼

`Instance`는 `RegisteredServerCluster<WaterHeaterManagementCluster>` 타입의 `mCluster`를 보유한다. 기존 애플리케이션이 `Instance`를 생성하고 `Init()`, `Shutdown()`, `HasFeature()`를 계속 사용할 수 있도록 한다.

- `Instance::Init()`:
  - `CodegenDataModelProvider::Instance().Registry().Register(mCluster.Registration())`로 등록한다.
  - 결과가 `CHIP_NO_ERROR`이면 `mRegistered`를 `true`로 설정한다.
  - 등록 결과를 반환한다.
- `Instance::Shutdown()`:
  - `mRegistered`가 `false`이면 바로 반환한다.
  - `mRegistered`를 `false`로 바꾼 뒤 `Unregister(&mCluster.Cluster())`를 호출한다.
  - 등록 해제 실패 시 엔드포인트 ID와 오류를 기록한다.
- `Instance::~Instance()`는 등록된 상태일 때 `Shutdown()`을 호출한다.
- `HasFeature()`는 내부 클러스터의 `HasFeature()`로 위임한다.
- 복사 생성자, 이동 생성자 및 복사 대입 연산자는 삭제되어 있다.

`water-heater-management-server.h`는 하위 호환을 위해 `app/clusters/water-heater-management-server/CodegenIntegration.h`를 포함한다.

### `Delegate`의 장치 제어 계약

`Delegate`는 다음 순수 가상 함수를 통해 실제 장치 동작을 위임받는다.

#### `HandleBoost()`

```cpp
virtual Protocols::InteractionModel::Status HandleBoost(
    uint32_t duration,
    Optional<bool> oneShot,
    Optional<bool> emergencyBoost,
    Optional<int16_t> temporarySetpoint,
    Optional<Percent> targetPercentage,
    Optional<Percent> targetReheat) = 0;
```

헤더 주석에 기술된 동작은 다음과 같다.

| 인자 | 의미 |
|---|---|
| `duration` | `BOOST` 상태를 유지할 시간(초). 종료 후 이전 `OFF`, `MANUAL`, `TIMED` 등의 모드로 복귀 |
| `oneShot` | 지정된 온수량이 목표 온도에 처음 도달하면 `BOOST`를 자동 취소할지 지정 |
| `emergencyBoost` | 가능한 한 빠른 가열 요청. 여러 열원을 동시에 활성화할 수 있음 |
| `temporarySetpoint` | `BOOST` 동안 일반 설정 온도를 대신할 목표 온도 |
| `targetPercentage` | `TankPercent` 지원 시 가열할 탱크 내 물의 비율 |
| `targetReheat` | 목표 비율의 가열을 완료한 뒤 재가열을 시작할 온수 비율 |

`BOOST` 진입은 현재 모드가 `OFF`이거나 `TIMED`의 비가열 시간대인 경우에도 가열 요구를 발생시킬 수 있다. 명령을 수락하면 `Success`, 그렇지 않으면 적절한 오류를 반환하도록 명시되어 있다.

#### `HandleCancelBoost()`

`HandleCancelBoost()`는 `BOOST`에서 이전 모드로 복귀하는 동작을 담당한다. 반환 타입은 `Protocols::InteractionModel::Status`다.

### 속성 읽기와 노출 목록

`ReadAttribute()`는 다음 값을 `encoder.Encode()`로 인코딩한다.

| 속성 | 값의 출처 |
|---|---|
| `HeaterTypes` | `mDelegate.GetHeaterTypes()` |
| `HeatDemand` | `mDelegate.GetHeatDemand()` |
| `TankVolume` | `mDelegate.GetTankVolume()` |
| `EstimatedHeatRequired` | `mDelegate.GetEstimatedHeatRequired()` |
| `TankPercentage` | `mDelegate.GetTankPercentage()` |
| `BoostState` | `mDelegate.GetBoostState()` |
| `FeatureMap` | `mFeature` |
| `ClusterRevision` | `WaterHeaterManagement::kRevision` |

그 외의 속성 ID에는 `Protocols::InteractionModel::Status::UnsupportedAttribute`를 반환한다.

`Delegate`의 속성 조회 함수 반환 타입은 다음과 같다.

| 함수 | 반환 타입 |
|---|---|
| `GetHeaterTypes()` | `BitMask<WaterHeaterHeatSourceBitmap>` |
| `GetHeatDemand()` | `BitMask<WaterHeaterHeatSourceBitmap>` |
| `GetTankVolume()` | `uint16_t` |
| `GetEstimatedHeatRequired()` | `Energy_mWh` |
| `GetTankPercentage()` | `Percent` |
| `GetBoostState()` | `BoostStateEnum` |

`Attributes()`는 `AttributeListBuilder`를 사용하여 `WaterHeaterManagement::Attributes::kMandatoryMetadata`에 다음 조건부 항목을 추가한다.

- `Feature::kEnergyManagement`: `TankVolume::kMetadataEntry`, `EstimatedHeatRequired::kMetadataEntry`
- `Feature::kTankPercent`: `TankPercentage::kMetadataEntry`

기능별 노출 조건은 `Attributes()`에서 적용되며, 제공된 `ReadAttribute()`의 각 속성 분기에는 별도의 기능 검사가 없다.

### 명령 디코딩 및 검증

`InvokeCommand()`는 명령 ID에 따라 `Commands::Boost::DecodableType` 또는 `Commands::CancelBoost::DecodableType`으로 입력을 디코딩한다.

- 디코딩 오류는 `ReturnErrorOnFailure`로 반환한다.
- 디코딩 성공 후 `HandleBoost()` 또는 `HandleCancelBoost()`를 호출한다.
- 지원하지 않는 명령에는 `Protocols::InteractionModel::Status::UnsupportedCommand`를 반환한다.

`AcceptedCommands()`는 `Commands::Boost::kMetadataEntry`와 `Commands::CancelBoost::kMetadataEntry`를 반환한다.

#### `HandleBoost()`의 검증

`Feature::kTankPercent` 지원 시 다음 조건을 검사한다.

| 거부 조건 | 반환값 |
|---|---|
| `targetPercentage`가 존재하며 `100` 초과 | `Status::InvalidCommand` |
| `targetReheat`가 존재하며 `100` 초과 | `Status::InvalidCommand` |
| `targetReheat`가 있지만 `targetPercentage`가 없음 | `Status::InvalidCommand` |
| `targetReheat`와 `oneShot`이 모두 존재 | `Status::InvalidCommand` |

`oneShot`은 값이 `false`인지와 관계없이 `HasValue()`로 존재 여부를 검사한다.

`Feature::kTankPercent`를 지원하지 않으면 `targetPercentage` 또는 `targetReheat`가 존재하는 요청을 `Status::InvalidCommand`로 거부한다.

검증을 통과하면 모든 인자를 `mDelegate.HandleBoost()`로 전달하고 그 결과를 반환한다. 결과가 `Status::Success`가 아니면 오류 로그를 남긴다.

제공된 `HandleBoost()` 본문에는 다음 검사가 명시적으로 구현되어 있지 않다.

- `duration`의 최솟값 `1`
- `targetReheat`가 `targetPercentage` 이하인지 여부
- `temporarySetpoint`의 제약

이는 해당 함수 본문에 대한 관찰이며, 제공되지 않은 디코딩 구현이나 구체적인 `Delegate` 구현의 검증 여부는 확인할 수 없다.

#### `HandleCancelBoost()`의 처리

`mDelegate.HandleCancelBoost()`를 호출하고 결과를 반환한다. 결과가 `Status::Success`가 아니면 오류를 기록한다.

### 이벤트 생성

`Delegate::GenerateBoostStartedEvent()`와 `Delegate::GenerateBoostEndedEvent()`는 연결된 `WaterHeaterManagementCluster`로 이벤트 생성 요청을 전달한다.

- `mCluster == nullptr`이면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.
- 클러스터의 이벤트 생성 함수는 `mContext != nullptr`인지 확인하며, 아니면 `CHIP_ERROR_INCORRECT_STATE`를 반환한다.

`WaterHeaterManagementCluster::GenerateBoostStartedEvent()`는 `Events::BoostStarted::Type`을 생성하고 다음 필드를 설정한다.

| 이벤트 필드 | 전달 값 |
|---|---|
| `event.boostInfo.duration` | `durationSecs` |
| `event.boostInfo.oneShot` | `oneShot` |
| `event.boostInfo.emergencyBoost` | `emergencyBoost` |
| `event.boostInfo.temporarySetpoint` | `temporarySetpoint` |
| `event.boostInfo.targetPercentage` | `targetPercentage` |
| `event.boostInfo.targetReheat` | `targetReheat` |

`GenerateBoostEndedEvent()`는 `Events::BoostEnded::Type`을 생성한다.

두 함수 모두 `mContext->interactionContext.eventsGenerator.GenerateEvent(event, mPath.mEndpointId)`를 호출한다. 반환 결과에 값이 없으면 `CHIP_ERROR_INTERNAL`, 성공하면 `CHIP_NO_ERROR`를 반환한다.

제공된 명령 처리 함수는 이벤트 생성 함수를 직접 호출하지 않는다. 구체적인 `Delegate` 구현이 사용할 수 있도록 이벤트 생성 헬퍼가 제공되어 있다.

### 테스트 이벤트 트리거

`WaterHeaterManagementTrigger`는 `chip` 네임스페이스에 정의된 `uint64_t` 기반 열거형이다. 주석에 따르면 트리거 값은 제조사 정의 비밀값인 `enableKey`와 함께 General Diagnostic 클러스터의 `TestEventTrigger` 명령으로 전송한다.

| 이름 | 값 | 시뮬레이션 내용 |
|---|---|---|
| `kBasicInstallationTestEvent` | `0x0094'0000'0000'0000` | 물 온도 20°C, 목표 온도 60°C, `OFF` 모드의 100L 탱크 설치 |
| `kBasicInstallationTestEventClear` | `0x0094'0000'0000'0001` | 설치 시뮬레이션 종료 |
| `kWaterTemperature20CTestEvent` | `0x0094'0000'0000'0002` | 탱크 내 물 전체가 20°C |
| `kWaterTemperature61CTestEvent` | `0x0094'0000'0000'0003` | 탱크 내 물 전체가 61°C |
| `kWaterTemperature66CTestEvent` | `0x0094'0000'0000'0004` | 탱크 내 물 전체가 66°C |
| `kManualModeTestEvent` | `0x0094'0000'0000'0005` | Water Heater Mode를 `MANUAL`로 설정 |
| `kOffModeTestEvent` | `0x0094'0000'0000'0006` | Water Heater Mode를 `OFF`로 설정 |
| `kDrawOffHotWaterTestEvent` | `0x0094'0000'0000'0007` | 탱크 용량의 25%에 해당하는 온수를 배출하고 20°C 물로 대체 |

`WaterHeaterManagementTestEventTriggerHandler`는 `TestEventTriggerHandler`를 상속한다. `HandleEventTrigger()`는 다음 순서로 처리한다.

1. `clearEndpointInEventTrigger(eventTrigger)`로 엔드포인트 정보를 제거한다.
2. `HandleWaterHeaterManagementTestEventTrigger(eventTrigger)`를 호출한다.
3. 결과가 `true`이면 `CHIP_NO_ERROR`, `false`이면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.

`TestEventTrigger`를 활성화한 애플리케이션은 `HandleWaterHeaterManagementTestEventTrigger(uint64_t eventTrigger)`를 구현해야 한다.

## 관련 페이지

**사용 기기**

- [Water Heater](../device-types/water-heater.md)
