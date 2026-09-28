---
entity: ModeBase
ids: []
source_paths: ['src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml', 'src/app/clusters/mode-base-server/Delegate.h', 'src/app/clusters/mode-base-server/AppDelegate.h', 'src/app/clusters/mode-base-server/mode-base-cluster-objects.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h', 'src/app/clusters/mode-base-server/CodegenIntegration.h', 'src/app/clusters/mode-base-server/CodegenIntegration.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp', 'src/app/clusters/mode-base-server/mode-base-server.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.h', 'data_model/1.7/clusters/ModeBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-4o-mini
---

## 개요
ModeBase 클러스터는 지원되는 모드 중에서 선택하는 기능을 제공하며, 기기에서 사용할 수 있는 모드의 리스트를 포함합니다. 

## 스펙
### ModeBase 클러스터
- **클러스터 ID**: 0x0050
- **명령 및 속성** 
  - 명령:
    - ChangeToMode
    - ChangeToModeResponse
    - ChangeToModeByCoreTag
  - 속성:
    - SupportedModes
    - CurrentMode
    - StartUpMode
    - OnMode
    - CoreModeTags

### 데이터 구조
- **ModeOptionStruct**
  - Label: String (최대 64 문자)
  - Mode: uint8
  - ModeTags: 리스트 (최대 8 개의 ModeTagStruct)

- **ModeTagStruct**
  - MfgCode: vendor-id
  - Value: enum16

### 상태 코드
- StatusCode:
  - kSuccess
  - kUnsupportedMode
  - kGenericFailure
  - kInvalidInMode

## SDK 정의
### ModeBaseCluster
`ModeBaseCluster` 클래스는 `DefaultServerCluster`를 상속하여 구현됩니다. 서버 클러스터의 동작을 정의하고, 관련된 명령 및 속성을 처리합니다.

#### 메서드
- `Startup(ServerClusterContext & context)`
- `UpdateCurrentMode(uint8_t aNewMode)`
- `UpdateStartUpMode(DataModel::Nullable<uint8_t> aNewStartUpMode)`
- `UpdateOnMode(DataModel::Nullable<uint8_t> aNewOnMode)`
- `ReportSupportedModesChange()`
- `IsSupportedMode(uint8_t mode)` 
- `GetModeValueByModeTag(uint16_t modeTag, uint8_t & value)`

### Delegate
`Delegate` 클래스는 `AppDelegate`를 상속하여 어플리케이션 특정 논리를 구현하는데 필요한 메서드를 정의합니다.

## 구현
ModeBase 클러스터의 구현은 여러 소스 파일로 나뉘어 있으며, 
`mode-base-server` 디렉터리에 포함된 파일들은 클러스터 초기화, 속성 관리 및 명령 처리와 관련된 기능을 포함합니다.

## 예시
```cpp
// ModeBaseCluster 예시 사용
ModeBaseCluster cluster(endpointId, clusterEntry, config);
cluster.Startup(context);

// 모드 변경 명령 처리
void HandleChangeToMode(uint8_t newMode) {
    Commands::ChangeToModeResponse::Type response;
    // 명령 유효성 검증 및 처리
    cluster.HandleChangeToMode(commandObj, commandPath, data);
}
```

## 관련 문서
- [Matter 프로젝트 문서](https://github.com/project-chip/connectedhomeip)
- [Connectivity Standards Alliance](https://www.csa-iot.org/)