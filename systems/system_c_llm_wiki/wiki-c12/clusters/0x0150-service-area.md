---
entity: Service Area
ids: ['0x0150']
source_paths: ['data_model/1.7/clusters/ServiceArea.xml', 'src/app/clusters/service-area-server/CodegenIntegration.cpp', 'src/app/clusters/service-area-server/CodegenIntegration.h', 'src/app/clusters/service-area-server/README.md', 'src/app/clusters/service-area-server/ServiceAreaCluster.cpp', 'src/app/clusters/service-area-server/ServiceAreaCluster.h', 'src/app/clusters/service-area-server/service-area-cluster-objects.h', 'src/app/clusters/service-area-server/service-area-delegate.h', 'src/app/clusters/service-area-server/service-area-server.h', 'src/app/clusters/service-area-server/service-area-storage-delegate.cpp', 'src/app/clusters/service-area-server/service-area-storage-delegate.h', 'src/app/zap-templates/zcl/data-model/chip/service-area-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Service Area

## 개요

Service Area는 장치가 동작할 영역을 제어하고, 현재 작업 중인 영역을 조회하는 인터페이스를 제공한다. 지원 영역과 선택 영역을 관리하며, 선택적으로 지도와 영역별 진행 상태를 지원한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Service Area` |
| 스펙 이름 | `Service Area Cluster` |
| 클러스터 ID | `0x0150` |
| revision | `2` |
| hierarchy | `base` |
| role | `application` |
| picsCode | `SEAR` |
| scope | `Endpoint` |

구현은 다음 네 클래스를 중심으로 구성된다.

- `ServiceAreaCluster`: `DefaultServerCluster`를 상속하는 code-driven 구현.
- `Instance`: 기존 애플리케이션과의 호환성을 위한 `ServiceAreaCluster` 래퍼.
- `StorageDelegate`: 리스트 속성의 저장소 관리.
- `Delegate`: 장치별 동작 정책과 명령 처리 로직.

새 코드는 `ServiceAreaCluster`를 직접 사용하는 것이 권장된다.

## 스펙

출처: `data_model/1.7/clusters/ServiceArea.xml`

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 최초 정의 |
| `2` | `InitialTimeEstimate`를 `EstimatedTime`으로 변경 |

### 기능

모든 기능은 선택 사항이다.

| bit | code | name | 의미 |
|---|---|---|---|
| `0` | `SELRUN` | `SelectWhileRunning` | 동작 중 선택 영역 변경 허용 |
| `1` | `PROG` | `ProgressReporting` | 진행 상태 보고 지원 |
| `2` | `MAPS` | `Maps` | 지도 지원 |

### 속성

모든 속성은 읽기 가능하며 `readPrivilege="view"`이다.

| ID | 이름 | 타입 / 항목 타입 | 기본값 | 적합성 및 제약 |
|---|---|---|---|---|
| `0x0000` | `SupportedAreas` | `list` / `AreaStruct` | `MS` | 필수, 최대 `255`개 |
| `0x0001` | `SupportedMaps` | `list` / `MapStruct` | `MS` | `MAPS` 지원 시 필수, 최대 `255`개 |
| `0x0002` | `SelectedAreas` | `list` / `uint32` | `empty` | 필수 |
| `0x0003` | `CurrentArea` | `uint32` | `null` | nullable, `describedConform` |
| `0x0004` | `EstimatedEndTime` | `epoch-s` | `null` | nullable, `CurrentArea`에 대한 `optionalConform`, `quieterReporting="true"` |
| `0x0005` | `Progress` | `list` / `ProgressStruct` | `empty` | `PROG` 지원 시 필수, 최대 `255`개 |

`SelectedAreas`, `CurrentArea`에는 내용이 비어 있는 `<desc/>` 제약이 포함되어 있다. 제공된 XML만으로 그 제약의 상세 내용을 확인할 수 없다.

### 데이터 구조

| 구조체 | field id | 필드 | 타입 | 필수 여부 | nullable / 제약 |
|---|---|---|---|---|---|---|
| `AreaInfoStruct` | `0` | `LocationInfo` | `LocationDescriptorStruct` | 필수 | nullable |
| `AreaInfoStruct` | `1` | `LandmarkInfo` | `LandmarkInfoStruct` | 필수 | nullable |
| `AreaStruct` | `0` | `AreaID` | `uint32` | 필수 | 기본값 `MS` |
| `AreaStruct` | `1` | `MapID` | `uint32` | 필수 | nullable, 기본값 `MS` |
| `AreaStruct` | `2` | `AreaInfo` | `AreaInfoStruct` | 필수 | 기본값 `MS` |
| `LandmarkInfoStruct` | `0` | `LandmarkTag` | `tag` | 필수 | — |
| `LandmarkInfoStruct` | `1` | `RelativePositionTag` | `tag` | 필수 | nullable |
| `MapStruct` | `0` | `MapID` | `uint32` | 필수 | 기본값 `MS` |
| `MapStruct` | `1` | `Name` | `string` | 필수 | 최대 길이 `64`, 기본값 `MS` |
| `ProgressStruct` | `0` | `AreaID` | `uint32` | 필수 | 기본값 `MS` |
| `ProgressStruct` | `1` | `Status` | `OperationalStatusEnum` | 필수 | 기본값 `MS` |
| `ProgressStruct` | `2` | `TotalOperationalTime` | `elapsed-s` | 선택 | nullable, 기본값 `MS` |
| `ProgressStruct` | `3` | `EstimatedTime` | `elapsed-s` | 선택 | nullable, 기본값 `MS` |

### 상태 열거형

#### `OperationalStatusEnum`

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `Pending` | 해당 영역에서 아직 시작하지 않았거나, 완료하지 않았지만 현재 작업 중이지 않음 |
| `0x01` | `Operating` | 해당 영역에서 작업 중 |
| `0x02` | `Skipped` | `SkipArea`, 외부 명령, 제조사별 사유 또는 작업 실패로 해당 영역을 건너뜀 |
| `0x03` | `Completed` | 해당 영역의 작업 완료 |

#### `SelectAreasStatus`

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `Success` | `NewAreas`의 영역에서 동작이 허용되고 가능하며, `SelectedAreas`를 `NewAreas`로 설정 |
| `0x01` | `UnsupportedArea` | `NewAreas`의 항목 중 하나 이상이 `SupportedAreas`에 없음 |
| `0x02` | `InvalidInMode` | 장치의 현재 모드에서 요청 처리 불가 |
| `0x03` | `InvalidSet` | 영역 집합이 유효하지 않음. 예를 들어 장치가 스스로 이동할 수 없는 서로 다른 층의 영역 |

#### `SkipAreaStatus`

| 값 | 이름 | 의미 |
|---|---|---|
| `0x00` | `Success` | 건너뛰기가 허용되고 가능하거나, 마지막 가용 영역에서 동작하던 장치가 정지함 |
| `0x01` | `InvalidAreaList` | `SelectedAreas`가 비어 있음 |
| `0x02` | `InvalidInMode` | 현재 모드에서 처리 불가. 예를 들어 `CurrentArea`가 `null`이거나 장치가 동작 중이지 않음 |
| `0x03` | `InvalidSkippedArea` | `SkippedArea`가 `SupportedAreas`의 항목과 일치하지 않음 |

### 명령

| ID | 이름 | 방향 | 응답 | 적합성 |
|---|---|---|---|---|
| `0x00` | `SelectAreas` | `commandToServer` | `SelectAreasResponse` | 필수 |
| `0x01` | `SelectAreasResponse` | `responseFromServer` | — | 필수 |
| `0x02` | `SkipArea` | `commandToServer` | `SkipAreaResponse` | `CurrentArea` 또는 `Progress`에 대한 `optionalConform` |
| `0x03` | `SkipAreaResponse` | `responseFromServer` | — | `SkipArea` 지원 시 필수 |

`SelectAreas`와 `SkipArea`의 호출 권한은 `invokePrivilege="operate"`이다.

| 명령 | field id | 필드 | 타입 | 제약 |
|---|---|---|---|---|
| `SelectAreas` | `0` | `NewAreas` | `list`, 항목 `uint32` | 필수 |
| `SelectAreasResponse` | `0` | `Status` | `SelectAreasStatus` | 필수 |
| `SelectAreasResponse` | `1` | `StatusText` | `string` | 필수, 최대 길이 `256` |
| `SkipArea` | `0` | `SkippedArea` | `uint32` | 필수 |
| `SkipAreaResponse` | `0` | `Status` | `SkipAreaStatus` | 필수 |
| `SkipAreaResponse` | `1` | `StatusText` | `string` | 필수, 최대 길이 `256` |

`NewAreas`와 `SkippedArea`의 상세 제약도 XML에서는 빈 `<desc/>`로 표시되어 있다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/service-area-cluster.xml`

### ZAP 메타데이터

| 항목 | 정의 |
|---|---|
| configurator domain | `CHIP` |
| cluster domain | `General` |
| name | `Service Area` |
| code | `0x0150` |
| define | `SERVICE_AREA_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| globalAttribute | `side="either"`, `code="0xFFFD"`, `value="2"` |

파일 주석에는 Alchemy가 생성한 XML이며 직접 편집하지 말라고 명시되어 있다. 생성 원본은 `src/app_clusters/ServiceArea.adoc`이다.

### 타입 표현

스펙의 이름과 ID를 유지하면서 SDK XML에서는 다음 타입 표현을 사용한다.

| 스펙 표현 | SDK XML 표현 |
|---|---|
| `uint32` | `int32u` |
| 속성의 `list` | `array`, `entryType`으로 항목 타입 지정 |
| `elapsed-s` | `elapsed_s` |
| `epoch-s` | `epoch_s` |
| `MapStruct.Name`의 `string` | `char_string`, `length="64"` |
| 응답의 `StatusText` | `long_char_string`, `length="256"` |
| `LandmarkInfoStruct.LandmarkTag`의 `tag` | `LandmarkTag` |
| `LandmarkInfoStruct.RelativePositionTag`의 `tag` | `RelativePositionTag` |

- `OperationalStatusEnum`, `SelectAreasStatus`, `SkipAreaStatus`는 `enum8`이다.
- `ProgressStruct.Status`와 두 응답의 `Status`에는 `max="0x03"`이 지정되어 있다.
- `ProgressStruct.TotalOperationalTime`과 `ProgressStruct.EstimatedTime`은 `optional="true"`, `isNullable="true"`이다.
- 모든 클러스터 속성은 `side="server"`로 정의된다.
- `SelectAreas`, `SkipArea`는 `source="client"`이다.
- `SelectAreasResponse`, `SkipAreaResponse`는 `source="server"`이며 `disableDefaultResponse="true"`이다.
- `SelectAreas.NewAreas`는 `type="int32u"`, `array="true"`로 표현된다.

## 구현

### 파일 구성

| 파일 | 역할 |
|---|---|
| `src/app/clusters/service-area-server/ServiceAreaCluster.h` | `ServiceAreaCluster` 인터페이스와 내부 상태 선언 |
| `src/app/clusters/service-area-server/ServiceAreaCluster.cpp` | 속성 읽기, 명령 처리, 검증, 상태 변경과 알림 |
| `src/app/clusters/service-area-server/CodegenIntegration.h` | 호환성 래퍼 `Instance` 선언 |
| `src/app/clusters/service-area-server/CodegenIntegration.cpp` | ZAP 구성 연동, 등록, API 전달 |
| `src/app/clusters/service-area-server/service-area-cluster-objects.h` | 크기 제한과 구조체 래퍼 |
| `src/app/clusters/service-area-server/service-area-delegate.h` | 장치별 정책 인터페이스 |
| `src/app/clusters/service-area-server/service-area-storage-delegate.h` | 저장소 인터페이스 |
| `src/app/clusters/service-area-server/service-area-storage-delegate.cpp` | 기본 검색과 일부 기본 삭제 구현 |
| `src/app/clusters/service-area-server/service-area-server.h` | 이전 include 경로의 호환성 유지 |

`service-area-server.h`는 `app/clusters/service-area-server/CodegenIntegration.h`를 포함한다. 새 코드는 `ServiceAreaCluster.h`를 직접 사용하도록 안내한다.

### `ServiceAreaCluster` 구성

생성자는 다음 정보를 받는다.

- `EndpointId endpointId`
- `StorageDelegate & storageDelegate`
- `Delegate & delegate`
- `BitMask<ServiceArea::Feature> feature`
- `OptionalAttributeSet optionalAttributes = {}`

`StorageDelegate`와 `Delegate`는 클러스터보다 오래 유지되어야 한다.

내부 저장 상태는 다음과 같이 분리된다.

| 데이터 | 저장 위치 |
|---|---|
| `SupportedAreas`, `SupportedMaps`, `SelectedAreas`, `Progress` | `mStorageDelegate` |
| `CurrentArea` | `mCurrentArea` |
| `EstimatedEndTime` | `mEstimatedEndTime` |
| 기능 구성 | `const BitMask<ServiceArea::Feature> mFeature` |
| 선택 속성 구성 | `const OptionalAttributeSet mOptionalAttributes` |

`HasFeature`는 `mFeature.Has(feature)`를 반환한다. 기능 구성은 시작 시 설정되며 장치와 클라이언트 모두에 대해 읽기 전용으로 설명되어 있다.

### 속성과 명령 노출

`OptionalAttributeSet`의 대상은 다음 네 속성이다.

- `ServiceArea::Attributes::SupportedMaps::Id`
- `ServiceArea::Attributes::CurrentArea::Id`
- `ServiceArea::Attributes::EstimatedEndTime::Id`
- `ServiceArea::Attributes::Progress::Id`

`Attributes`는 `AttributeListBuilder`로 필수 속성과 활성화된 선택 속성을 결합한다.

- `Feature::kMaps`가 없으면 `SupportedMaps`를 제외한다.
- `Feature::kProgressReporting`이 없으면 `Progress`를 제외한다.

`SupportsSkipArea`는 다음 중 하나가 성립하면 `true`이다.

1. `CurrentArea`가 선택 속성 집합에 설정되어 있다.
2. `Feature::kProgressReporting`이 있고 `Progress`가 선택 속성 집합에 설정되어 있다.

`AcceptedCommands`는 항상 `SelectAreas`를 포함하며, `SupportsSkipArea`가 `true`이면 `SkipArea`도 포함한다.

`ReadAttribute`는 다음을 처리한다.

- `ClusterRevision`: `ServiceArea::kRevision` 인코딩.
- `FeatureMap`: `mFeature.Raw()`를 `uint32_t`로 인코딩.
- 리스트 속성: `ReadSupportedAreas`, `ReadSupportedMaps`, `ReadSelectedAreas`, `ReadProgress`.
- 단일 값: `GetCurrentArea`, `GetEstimatedEndTime`.
- 그 외: `Protocols::InteractionModel::Status::UnsupportedAttribute`.

리스트 읽기는 항목이 없으면 `EncodeEmptyList`를 호출하고, 그렇지 않으면 인덱스로 순회하면서 `EncodeList`로 인코딩한다.

`InvokeCommand`는 `DataModel::Decode` 후 해당 처리 함수를 호출한다. 지원하지 않는 명령과 비활성화된 `SkipArea`에는 `Status::UnsupportedCommand`를 반환한다.

### `Instance` 초기화와 등록

`Instance`는 `RegisteredServerCluster<ServiceAreaCluster> mCluster`를 보유하고 공개 속성 API를 `mCluster.Cluster()`에 전달한다. 복사 생성과 복사 대입은 삭제되어 있다.

생성 시:

1. `BuildOptionalAttributes`가 `emberAfContainsAttribute`로 엔드포인트에 구성된 선택 속성을 확인한다.
2. `ServiceAreaCluster`를 구성한다.
3. `aDelegate->SetInstance(this)`를 호출한다.

`Instance::Init()`의 실제 호출 순서는 다음과 같다.

1. `emberAfContainsServer`로 엔드포인트에 클러스터가 활성화되어 있는지 확인.
2. 활성화되어 있지 않으면 `CHIP_ERROR_INVALID_ARGUMENT` 반환.
3. 이미 등록되었으면 `CHIP_NO_ERROR` 반환.
4. `mStorageDelegate->Init()` 호출.
5. `mDelegate->Init()` 호출.
6. `CodegenDataModelProvider::Instance().Registry().Register(mCluster.Registration())` 호출.
7. `mRegistered = true` 설정.

소멸 시 `mRegistered`가 `true`이면 로그를 남기고 `Unregister(&mCluster.Cluster())`를 호출한다.

다음 ZAP 생성 콜백은 빈 구현이다.

- `MatterServiceAreaClusterInitCallback`
- `MatterServiceAreaClusterShutdownCallback`

소스 주석은 애플리케이션이 이 콜백을 통해서가 아니라 `Instance`를 직접 생성하고 `Init()`으로 등록한다고 설명한다.

### 명령 처리

#### `HandleSelectAreasCmd`

처리 흐름은 다음과 같다.

1. `req.newAreas.ComputeSize`로 항목 수를 확인한다.
   - 실패하면 `Status::InvalidCommand`.
   - `kMaxNumSelectedAreas` 초과 시 `SelectAreasStatus::kInvalidSet`.
2. 중복 영역을 건너뛰며 입력을 수집한다.
3. 각 영역에 대해 `mStorageDelegate.IsSupportedArea`를 확인한다.
   - 지원하지 않는 영역이면 `SelectAreasStatus::kUnsupportedArea`와 빈 `StatusText`.
4. 입력 순회 오류는 `Status::InvalidCommand`로 반환한다.
5. `matchesCurrentSelectedAreas`가 유지되면 변경 없이 `SelectAreasStatus::kSuccess`를 응답한다.
6. `mDelegate.IsSetSelectedAreasAllowed`를 호출한다.
   - 거절하면 `SelectAreasStatus::kInvalidInMode`와 delegate의 설명을 응답한다.
7. `mDelegate.IsValidSelectAreasSet`으로 전체 집합의 유효성을 확인한다.
   - 거절하면 delegate가 설정한 상태와 설명을 응답한다.
8. `ClearSelectedAreasRaw` 후 중복을 제거한 영역을 `AddSelectedAreaRaw`로 추가한다.
9. `NotifySelectedAreasChanged` 후 `SelectAreasStatus::kSuccess`를 응답한다.

응답은 `Commands::SelectAreasResponse::Type`과 `handler->AddResponse`를 사용한다.

#### `HandleSkipAreaCmd`

| 조건 | 처리 |
|---|---|
| `GetNumberOfSelectedAreas() == 0` | `SkipAreaStatus::kInvalidAreaList`, 빈 `StatusText` |
| `req.skippedArea`가 지원 영역이 아님 | `SkipAreaStatus::kInvalidSkippedArea`, 빈 `StatusText` |
| `mDelegate.HandleSkipArea`가 실패 | `SkipAreaStatus::kInvalidInMode`, delegate의 설명 |
| delegate 처리 성공 | `SkipAreaStatus::kSuccess`, 빈 `StatusText` |

응답은 `Commands::SkipAreaResponse::Type`과 `handler->AddResponse`를 사용한다.

### 공개 속성 API

아래 API는 `ServiceAreaCluster`와 `Instance`에서 제공된다.

| 대상 | 조회 | 변경 |
|---|---|---|
| `SupportedAreas` | `GetNumberOfSupportedAreas`, `GetSupportedAreaByIndex`, `GetSupportedAreaById` | `AddSupportedArea`, `ModifySupportedArea`, `ClearSupportedAreas`, `RemoveSupportedArea` |
| `SupportedMaps` | `GetNumberOfSupportedMaps`, `GetSupportedMapByIndex`, `GetSupportedMapById` | `AddSupportedMap`, `RenameSupportedMap`, `ClearSupportedMaps`, `RemoveSupportedMap` |
| `SelectedAreas` | `GetNumberOfSelectedAreas`, `GetSelectedAreaByIndex` | `AddSelectedArea`, `ClearSelectedAreas`, `RemoveSelectedAreas` |
| `CurrentArea` | `GetCurrentArea` | `SetCurrentArea` |
| `EstimatedEndTime` | `GetEstimatedEndTime` | `SetEstimatedEndTime` |
| `Progress` | `GetNumberOfProgressElements`, `GetProgressElementByIndex`, `GetProgressElementById` | `AddPendingProgressElement`, `SetProgressStatus`, `SetProgressTotalOperationalTime`, `SetProgressEstimatedTime`, `ClearProgress`, `RemoveProgressElement` |
| 기능 | `HasFeature` | — |

### 영역과 지도 검증

#### `SupportedAreas`

`IsValidSupportedArea`는 다음을 검사한다.

- `areaInfo.locationInfo`와 `areaInfo.landmarkInfo`가 동시에 `null`이면 거절한다.
- `locationInfo`가 있고 `locationName`이 비어 있다면, `floorNumber`, `areaType`, `landmarkInfo` 중 하나 이상이 `null`이 아니어야 한다.
- `Feature::kMaps`가 있고 지원 지도가 하나 이상이면 `mapID`는 `null`이 아니며 지원 지도를 가리켜야 한다.
- 그 외에는 `mapID`가 `null`이어야 한다.

`IsUniqueSupportedArea`는 `areaID` 및 영역 설명의 중복을 검사한다.

- 지원 지도가 있으면 `mapID`와 영역 정보의 조합을 비교한다.
- 지원 지도가 없으면 `mapID`를 무시하고 영역 정보를 비교한다.
- 비교에는 `AreaStructureWrapper::IsEqualConfig::kIgnoreAreaID`와 `AreaStructureWrapper::IsEqualConfig::kIgnoreMapId`를 사용한다.

`AddSupportedArea`는 변경 허용 정책, 최대 개수, 유효성, 고유성을 확인한 후 저장하고 알린다. `ModifySupportedArea`는 기존 항목을 찾고 검증하며, `mapID`가 바뀌면 변경 허용 정책을 확인하고 `HandleSupportedAreasUpdated`를 호출한다.

`HandleSupportedAreasUpdated`의 실제 구현은 `SupportedAreas`를 기준으로 다음을 정리한다.

- 지원 영역이 없으면 `SelectedAreas`와 `Progress`를 비우고 `CurrentArea`를 `null`로 설정.
- 더 이상 지원되지 않는 `SelectedAreas` 항목 제거.
- 지원되지 않는 `CurrentArea`를 `null`로 설정.
- 지원되지 않는 영역의 `Progress` 항목 제거.

#### `SupportedMaps`

- `AddSupportedMap`: 최대 개수, 비어 있지 않은 이름, 이름과 `mapID`의 고유성을 검사한다.
- `RenameSupportedMap`: 대상 존재 여부, 비어 있지 않은 이름, 다른 지도와 이름이 중복되지 않는지 검사한다.
- `ClearSupportedMaps`: `IsSupportedMapChangeAllowed` 확인 후 저장소를 비우고 `ClearSupportedAreas`를 호출한다.
- `RemoveSupportedMap`: 지도를 삭제하고, 남은 지도가 없으면 `ClearSupportedAreas`를 호출한다. 지도가 남아 있으면 삭제된 지도에 속한 영역을 제거하고 관련 상태를 정리한다.

### 현재 영역, 예상 시간과 진행 상태

- `AddSelectedArea`는 최대 개수, 지원 영역 여부, 중복 여부, `IsSetSelectedAreasAllowed`를 확인한다.
- `SetCurrentArea`는 `null`이 아닌 값이 지원 영역인지 확인한다.
- `CurrentArea`를 `null`로 설정하면 `EstimatedEndTime`도 `null`로 설정한다.
- `CurrentArea`가 `null`인 동안 `SetEstimatedEndTime`은 `null`이 아닌 값을 거절한다.
- `GetEstimatedEndTime`은 현재 영역의 작업이 완료될 것으로 예상되는 epoch 초 단위 시간을 반환하도록 설명되어 있다.

`ReportEstimatedEndTimeChange`는 값이 동일하면 보고하지 않으며, 값이 변경된 경우 다음 조건에서 보고한다.

- `null`에서 변경되거나 `null`로 변경됨.
- `0`에서 변경되거나 `0`으로 변경됨.
- 값이 감소함.

`Progress` 처리:

- `AddPendingProgressElement`는 최대 개수, 지원 영역 여부, `areaID` 고유성을 확인하고 `OperationalStatusEnum::kPending`으로 추가한다.
- `SetProgressStatus`는 상태가 동일하면 변경하지 않는다.
- 새 상태가 `OperationalStatusEnum::kCompleted` 또는 `OperationalStatusEnum::kSkipped`가 아니면 `totalOperationalTime.ClearValue()`를 호출한다.
- `SetProgressTotalOperationalTime`은 상태가 위 두 값 중 하나가 아닐 때 `null`이 아닌 시간을 거절한다.
- `SetProgressEstimatedTime`은 해당 항목을 찾아 `estimatedTime.Emplace(aEstimatedTime)`로 갱신한다.

속성 알림 함수는 각각 `NotifyAttributeChanged`에 대응하는 속성 ID를 전달한다.

- `NotifySupportedAreasChanged`
- `NotifySupportedMapsChanged`
- `NotifySelectedAreasChanged`
- `NotifyCurrentAreaChanged`
- `NotifyEstimatedEndTimeChanged`
- `NotifyProgressChanged`

### `Delegate`

| 메서드 | 역할 / 기본 구현 |
|---|---|
| `Init` | 애플리케이션 초기화. 기본값은 `CHIP_NO_ERROR` |
| `IsSetSelectedAreasAllowed` | 현재 상태에서 선택 영역 변경이 허용되는지 검사하는 순수 가상 함수 |
| `IsValidSelectAreasSet` | 선택 영역 집합 전체가 유효하고 도달 가능한지 검사하는 순수 가상 함수 |
| `HandleSkipArea` | 건너뛰기 처리. 기본 구현은 설명을 설정하고 `false` 반환 |
| `IsSupportedAreasChangeAllowed` | 지원 영역 변경 허용 정책을 제공하는 순수 가상 함수 |
| `IsSupportedMapChangeAllowed` | 지원 지도 변경 허용 정책을 제공하는 순수 가상 함수 |
| `GetInstance` | 연결된 `Instance` 포인터 반환 |
| `SetInstance` | `Instance` 포인터 설정 |

실패 시 `statusText` 또는 `skipStatusText`를 반드시 설정해야 한다. 주석은 `CopyCharSpanToMutableCharSpanWithTruncation`을 사용하거나, 복사가 실패할 수 있다면 `.reduce_size(0)`으로 길이를 비워 초기화되지 않은 메모리 사용을 방지하도록 안내한다.

`IsValidSelectAreasSet`의 계약:

- 호출자는 중복이 없고 각 영역이 지원 영역임을 보장한다.
- 유효하지 않은 집합은 `InvalidSet`과 제조사 정의 오류 설명을 제공한다.
- 동작 중 `SelectAreas`가 허용되고 선택 영역이 없어지는 경우 장치를 정지해야 한다.

`HandleSkipArea`가 요청을 수락하면 장치별 구현은 해당 영역의 작업 중지, 구현된 경우 `Progress`의 건너뛰기 상태 갱신, 남은 `SelectedAreas`에서의 작업 진행, 모든 영역을 완료하거나 건너뛴 경우의 정지를 담당한다.

### `StorageDelegate`

리스트별 저장, 조회, 추가, 수정, 삭제를 위한 가상 인터페이스를 제공한다. 일반적인 입력 검증은 클러스터 계층에서 수행하지만, 저장소 주석은 추가 시 최대 개수를 재확인하고 수정 시 ID와 인덱스의 일치를 재확인하도록 권고한다.

| 대상 | 저장소 변경 API |
|---|---|
| `SupportedAreas` | `AddSupportedAreaRaw`, `ModifySupportedAreaRaw`, `ClearSupportedAreasRaw`, `RemoveSupportedAreaRaw` |
| `SupportedMaps` | `AddSupportedMapRaw`, `ModifySupportedMapRaw`, `ClearSupportedMapsRaw`, `RemoveSupportedMapRaw` |
| `SelectedAreas` | `AddSelectedAreaRaw`, `ClearSelectedAreasRaw`, `RemoveSelectedAreasRaw` |
| `Progress` | `AddProgressElementRaw`, `ModifyProgressElementRaw`, `ClearProgressRaw`, `RemoveProgressElementRaw` |

기본 구현의 특징:

- `GetSupportedAreaById`, `GetSupportedMapById`, `GetProgressElementById`는 인덱스 기반 선형 검색을 수행한다.
- `IsSupportedArea`, `IsSupportedMap`, `IsSelectedArea`, `IsProgressElement`는 존재 여부를 검사한다.
- `RemoveSupportedAreaRaw`, `RemoveSupportedMapRaw`는 기본적으로 `false`를 반환한다.
- 선택 속성의 저장소 메서드에도 순수 가상 함수가 포함되어 있다. 이를 위한 기본 구현 추가 여부는 소스의 TODO로 남아 있다.

### 구조체 래퍼와 제한값

출처: `src/app/clusters/service-area-server/service-area-cluster-objects.h`

| 상수 | 값 |
|---|---|
| `kMaxNumSupportedAreas` | `255` |
| `kMaxNumSupportedMaps` | `255` |
| `kMaxNumSelectedAreas` | `255` |
| `kMaxNumProgressElements` | `255` |
| `kMaxSizeStatusText` | `256` |
| `kAreaNameMaxSize` | `128u` |
| `kMapNameMaxSize` | `64u` |

`AreaStructureWrapper`:

- `chip::app::Clusters::ServiceArea::Structs::AreaStruct::Type`을 상속한다.
- 기본값은 `areaID = 0`, `mapID = null`, `locationInfo = null`, `landmarkInfo = null`이다.
- 이름을 내부 버퍼에 복사하며 `kAreaNameMaxSize`를 초과하면 잘라낸다.
- 복사 생성과 대입에서 깊은 복사를 수행한다.
- `SetAreaId`, `SetMapId`, `SetLocationInfoNull`, `SetLocationInfo`, `SetLandmarkInfoNull`, `SetLandmarkInfo`, `IsNameEqual`, `IsEqual`, `GetName`을 제공한다.
- `IsEqualConfig`의 `kIgnoreAreaID = 0x1`, `kIgnoreMapId = 0x2`로 비교 대상을 조정한다.

`MapStructureWrapper`:

- `chip::app::Clusters::ServiceArea::Structs::MapStruct::Type`을 상속한다.
- `Set`에서 이름을 내부 버퍼에 깊은 복사하며 `kMapNameMaxSize`를 초과하면 잘라낸다.
- `IsNameEqual`, `GetName`을 제공한다.
- 필드 조합의 유효성 검사는 이 래퍼 자체에서 수행하지 않는다.

### 제공 소스의 주석과 구현 차이

다음 사항은 제공된 코드에서 직접 확인되는 차이이다.

- `Delegate::Init`과 `StorageDelegate::Init` 주석은 등록 후 호출된다고 설명하지만, `Instance::Init()`은 두 초기화 함수를 호출한 뒤 등록한다.
- `HandleSupportedAreasUpdated`의 헤더 주석 일부는 `SelectedAreas`를 기준으로 설명하지만, 실제 구현은 `SupportedAreas` 포함 여부를 검사한다.
- `Delegate::HandleSkipArea` 주석은 호출 전에 `CurrentArea`가 `null`이 아님을 보장한다고 설명하지만, `HandleSkipAreaCmd`에는 그 검사가 없다.
- `HandleSkipAreaCmd`는 `InvalidSkippedArea`에 빈 `StatusText`를 반환한다. 같은 소스의 주석과 delegate 계약은 `Success`, `InvalidAreaList` 이외의 오류에 제조사 정의 설명을 요구한다.
- `HandleSelectAreasCmd`의 기존 선택 목록 비교에서는 `ignoredIndex`가 `0`으로 초기화된 뒤 증가하지 않는다. 따라서 이 코드를 일반적인 전체 목록 동등성 검사로 설명할 수 없다.
- `AddSelectedArea`는 저장소 추가 결과를 바로 반환하며 `NotifySelectedAreasChanged`를 호출하지 않는다.
- `SetProgressStatus`의 주석은 `TotalOperationalTime`을 `null`로 설정한다고 설명하지만, 실제 코드는 `totalOperationalTime.ClearValue()`를 호출한다.

## 관련 문서

### `src/app/clusters/service-area-server/README.md`

문서 제목: **The Service Area Cluster**

이 문서는 클래스별 책임과 기존 `Instance` 기반 사용 절차를 설명한다.

1. `ServiceArea::StorageDelegate`를 상속하고 필요한 가상 메서드를 구현한다.
2. `ServiceArea::Delegate`를 상속하고 필요한 가상 메서드를 구현한다.
3. `.c` 또는 `.cpp` 번역 단위에서 delegate 객체를 생성한다.
4. delegate 객체를 사용해 `Instance`를 생성한다.
5. 루트 `Server::Init()` 이후 `Instance`의 `Init()`을 호출한다.

문서는 마지막 두 단계를 `emberAfServiceAreaClusterInitCallback`에서 수행하는 방법도 언급한다. 이는 제공된 `CodegenIntegration.cpp`의 빈 콜백 `MatterServiceAreaClusterInitCallback`과 이름이 다르므로 구분해야 한다.

추가 안내:

- `StorageDelegate`의 메서드는 직접 사용하지 않도록 안내한다.
- `Delegate`는 `GetInstance()`를 통해 `Instance`의 속성 API에 접근할 수 있다.
- 기존 `rvc-app` 같은 애플리케이션은 `ServiceArea::Instance`와 `Instance::Init()`을 계속 사용할 수 있다.
- 신규 구현에는 `ServiceAreaCluster` 직접 사용을 권장한다.

## 관련 페이지

**사용 기기**

- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
