---
entity: Temperature Control
ids: ['0x0056']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/temperature-control-cluster.xml', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.h', 'src/app/clusters/temperature-control-server/temperature-control-server.h', 'src/app/clusters/temperature-control-server/CodegenIntegration.h', 'src/app/clusters/temperature-control-server/CodegenIntegration.cpp', 'src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp', 'src/app/clusters/temperature-control-server/supported-temperature-levels-manager.h', 'data_model/1.7/clusters/TemperatureControl.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Temperature Control 클러스터는 온도 조정 및 온도 보고를 위한 속성과 명령을 제공합니다.

## 스펙
**클러스터 ID**: `0x0056`  
**이름**: Temperature Control  
**도메인**: Appliances  
**설명**: Attributes and commands for configuring the temperature control, and reporting temperature.

**특징들**:
- **TemperatureNumber (TN)**: Use actual temperature numbers
- **TemperatureLevel (TL)**: Use temperature levels
- **TemperatureStep**: Use step control with temperature numbers (requires TN)

### 속성
- **TemperatureSetpoint (`0x0000`)**: 설정 온도 (optional, type: `temperature`)
- **MinTemperature (`0x0001`)**: 최소 온도 (optional, type: `temperature`)
- **MaxTemperature (`0x0002`)**: 최대 온도 (optional, type: `temperature`)
- **Step (`0x0003`)**: 단계 조정 (optional, type: `temperature`)
- **SelectedTemperatureLevel (`0x0004`)**: 선택된 온도 레벨 (optional, type: `int8u`, max: 31)
- **SupportedTemperatureLevels (`0x0005`)**: 지원되는 온도 레벨의 리스트 (optional, type: `array`, entryType: `char_string`, length: 32)

### 명령
- **SetTemperature (`0x00`)**: 설정 온도를 지정하는 명령.
  - 인자:
    - **TargetTemperature** (optional, type: `temperature`)
    - **TargetTemperatureLevel** (optional, type: `int8u`)

## SDK 정의
### TemperatureControlCluster.h
```cpp
class TemperatureControlCluster : public DefaultServerCluster {
public:
    struct StartupConfiguration {
        int16_t temperatureSetpoint{};
        int16_t minTemperature{};
        int16_t maxTemperature{};
        int16_t step{};
        uint8_t selectedTemperatureLevel{};
    };
    // Server cluster implementation
    ...
}
```

### TemperatureControlCluster.cpp
```cpp
std::optional<DataModel::ActionReturnStatus> TemperatureControlCluster::InvokeCommand(const DataModel::InvokeRequest & request,
                                                               TLV::TLVReader & input_arguments, CommandHandler * handler) {
    switch (request.path.mCommandId) {
    case Commands::SetTemperature::Id: {
        ...
    }
    ...
}
```

## 구현
### CodegenIntegration.h
```cpp
namespace chip::app::Clusters::TemperatureControl {
    TemperatureControlCluster * FindClusterOnEndpoint(EndpointId endpointId);
    CHIP_ERROR SetTemperatureSetpoint(EndpointId endpointId, int16_t temperatureSetpoint);
    ...
}
```

### CodegenIntegration.cpp
```cpp
void MatterTemperatureControlClusterInitCallback(EndpointId endpointId) {
    ...
}

void MatterTemperatureControlClusterShutdownCallback(EndpointId endpointId, MatterClusterShutdownType shutdownType) {
    ...
}
```

## 예시
### 명령을 호출하는 방법
```cpp
TemperatureControl::SetTemperatureSetpoint(endpointId, targetTemperature);
TemperatureControl::SetSelectedTemperatureLevel(endpointId, selectedTemperatureLevel);
```

## 관련 문서
- [TemperatureControl.xml](data_model/1.7/clusters/TemperatureControl.xml)
- [TemperatureControlCluster.h](src/app/clusters/temperature-control-server/TemperatureControlCluster.h)
- [TemperatureControlCluster.cpp](src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp)