---
entity: HEPA Filter Monitoring
ids: ['0x0071', '0x0072']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/resource-monitoring-cluster.xml', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-server.h', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.h', 'src/app/clusters/resource-monitoring-server/CodegenIntegration.cpp', 'src/app/clusters/resource-monitoring-server/README.md', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringDelegate.h', 'src/app/clusters/resource-monitoring-server/CodegenResourceMonitoringCluster.cpp', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.cpp', 'src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.h', 'src/app/clusters/resource-monitoring-server/replacement-product-list-manager.h', 'src/app/clusters/resource-monitoring-server/MigrateResourceMonitoringServerStorage.h', 'src/app/clusters/resource-monitoring-server/resource-monitoring-cluster-objects.cpp', 'data_model/1.7/clusters/ResourceMonitoring.xml', 'zzz_generated/app-common/clusters/ActivatedCarbonFilterMonitoring/Metadata.h', 'zzz_generated/app-common/clusters/HepaFilterMonitoring/Metadata.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
`HEPA Filter Monitoring` 클러스터는 장치 내 HEPA 필터의 상태를 모니터링하기 위한 속성과 명령을 제공합니다. 이 클러스터의 ID는 `0x0071`입니다.

## 스펙
- 클러스터 이름: HEPA Filter Monitoring
- 도메인: Measurement & Sensing
- 설명: 필터의 상태를 모니터링하기 위한 속성과 명령
- 클러스터 코드: `0x0071`
- 지원하는 기능:
  - `CON`: Resource의 조건을 백분율로 모니터링
  - `WRN`: 경고 표시 지원
  - `REP`: 교체 제품 목록 지정 지원

### 속성
- **Condition (`0x0000`)**: 필터의 상태(백분율) (선택적)
- **DegradationDirection (`0x0001`)**: 자원의 상태 저하 방향 (선택적)
- **ChangeIndication (`0x0002`)**: 변경 표시 (필수)
- **InPlaceIndicator (`0x0003`)**: 필터의 현재 설치 여부 (선택적)
- **LastChangedTime (`0x0004`)**: 마지막 업데이트 시간 (선택적)
- **ReplacementProductList (`0x0005`)**: 교체 제품 목록 (선택적)

### 명령
- **ResetCondition (`0x00`)**: 필터의 상태 및 변경 표시 속성을 리셋합니다.

## SDK 정의
### Enums
- **DegradationDirectionEnum**
  - `0`: Up
  - `1`: Down
  
- **ChangeIndicationEnum**
  - `0`: OK
  - `1`: Warning
  - `2`: Critical

- **ProductIdentifierTypeEnum**
  - `0`: UPC
  - `1`: GTIN-8
  - `2`: EAN
  - `3`: GTIN-14
  - `4`: OEM

### Structs
- **ReplacementProductStruct**
  - `ProductIdentifierType`: ProductIdentifierTypeEnum
  - `ProductIdentifierValue`: char_string (최대 20자)

## 구현
`ResourceMonitoringCluster` 구현은 다양한 상태와 속성을 관리하며, 리셋 명령을 처리합니다. 각 업데이트 메서드는 필터의 상태에 맞춰 다양한 동작을 수행합니다.

### 예시 코드
```cpp
class ResourceMonitoringCluster : public DefaultServerCluster {
public:
    ResourceMonitoringCluster(EndpointId aEndpointId, ClusterId aClusterId,
                              const BitFlags<ResourceMonitoring::Feature> enabledFeatures,
                              OptionalAttributeSet optionalAttributeSet,
                              ResourceMonitoring::Attributes::DegradationDirection::TypeInfo::Type aDegradationDirection,
                              bool aResetConditionCommandSupported);
    
    CHIP_ERROR Startup(ServerClusterContext & context) override;
    
    // 상태 업데이트 메서드
    Protocols::InteractionModel::Status UpdateCondition(uint8_t newCondition);
    // ...
    
    // 명령 처리
    std::optional<DataModel::ActionReturnStatus> InvokeCommand(const DataModel::InvokeRequest & request,
                                                               chip::TLV::TLVReader & input_arguments,
                                                               CommandHandler * handler) override;
    // ...
};
```

## 관련 문서
- [Resource Monitoring and its aliases](src/app/clusters/resource-monitoring-server/README.md)