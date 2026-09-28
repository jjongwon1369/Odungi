---
entity: Scenes Management
ids: ['0x0062']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/scene.xml', 'src/app/clusters/scenes-server/SceneHandlerImpl.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.h', 'src/app/clusters/scenes-server/SceneTableImpl.h', 'src/app/clusters/scenes-server/CodegenAttributeValuePairValidator.cpp', 'src/app/clusters/scenes-server/SceneHandlerImpl.cpp', 'src/app/clusters/scenes-server/scenes-server.h', 'src/app/clusters/scenes-server/ExtensionFieldSets.h', 'src/app/clusters/scenes-server/CodegenIntegration.h', 'src/app/clusters/scenes-server/CodegenIntegration.cpp', 'src/app/clusters/scenes-server/Constants.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.h', 'src/app/clusters/scenes-server/CodegenEndpointToIndex.h', 'src/app/clusters/scenes-server/SceneTable.h', 'src/app/clusters/scenes-server/AttributeValuePairValidator.h', 'src/app/clusters/scenes-server/ExtensionFieldSetsImpl.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.cpp', 'src/app/clusters/scenes-server/ScenesManagementCluster.h', 'src/app/clusters/scenes-server/SceneTableImpl.cpp', 'src/app/clusters/scenes-server/ScenesIntegrationDelegate.h', 'data_model/1.7/clusters/Scenes.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Scenes Management Cluster는 장치 내의 장면을 구성하고 조작하는 기능을 제공합니다. 이 클러스터는 장면 추가, 보기, 제거, 저장 및 장면 멤버십을 관리하는 명령을 포함합니다.

## 스펙
### 클러스터 ID
- **0x0062**: Scenes Management

### 데이터 타입
- **CopyModeBitmap**: 
    - **CopyAllScenes**: 모든 장면을 복사하는 옵션.
- **AttributeValuePairStruct**: 
    - `AttributeID`: 속성 ID
    - `ValueUnsigned8`, `ValueSigned8`, `ValueUnsigned16`, `ValueSigned16`, `ValueUnsigned32`, `ValueSigned32`, `ValueUnsigned64`, `ValueSigned64`: 다양한 정수형 값.
- **ExtensionFieldSetStruct**: 
    - `ClusterID`: 클러스터 ID
    - `AttributeValueList`: 속성 값 목록
- **SceneInfoStruct**: 
    - `SceneCount`: 장면 수
    - `CurrentScene`: 현재 장면
    - `CurrentGroup`: 현재 그룹
    - `SceneValid`: 장면 유효성
    - `RemainingCapacity`: 남은 용량

### 명령
- **AddScene**: 새로운 장면 추가.
- **ViewScene**: 요청된 장면의 세부정보 반환.
- **RemoveScene**: 특정 장면 제거.
- **RemoveAllScenes**: 특정 그룹의 모든 장면 제거.
- **StoreScene**: 요청된 장면을 저장.
- **RecallScene**: 특정 장면을 불러오기.
- **GetSceneMembership**: 특정 그룹 내의 장면 식별자 요청.
- **CopyScene**: 장면을 효율적으로 복사.

## SDK 정의
- **DefaultSceneHandlerImpl**: 장면을 추가 및 보기 명령에서 EFS를 처리하기 위한 기본 구현체.
- **SceneTable**: 장면 정보를 저장하는 구조체로, 장면의 정보와 상태를 관리.
- **ScenesManagementCluster**: 장면 관리를 위한 클러스터 클래스.

## 구현
### 주요 클래스 및 함수
- **DefaultSceneTableImpl**
    - `Init`: 퍼시스턴트 스토리지 초기화.
    - `GetSceneTableEntry`: 장면 테이블에서 장면 정보 가져오기.
    - `SetSceneTableEntry`: 장면 테이블에 장면 정보 저장.
    - `SceneSaveEFS`: 장면 정보를 EFS로 저장.
    - `SceneApplyEFS`: 저장된 EFS를 장면에 적용.

### 예외 처리
- 명령 처리 중 발생하는 오류를 `ResponseStatus`를 통해 명시.

## 예시
### 명령 처리 예시
```cpp
AddSceneResponse::Type HandleAddScene(FabricIndex fabricIndex, const AddScene::DecodableType & req) {
    // 장면 추가 명령 처리 로직
}
```
### 장면 저장 예시
```cpp
CHIP_ERROR SceneSaveEFS(SceneTableEntry & scene) {
    // EFS로 장면 정보 저장 로직
}
```

## 관련 문서
- [Matter 클러스터 문서](https://github.com/project-chip/connectedhomeip)
- 스펙 문서 및 구현 파일: `src/app/clusters/scenes-server/*.h`, `src/app/clusters/scenes-server/*.cpp`