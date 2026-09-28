---
entity: Thermostat User Interface Configuration
ids: ['0x0204']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-user-interface-configuration-cluster.xml', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.h', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationCluster.h', 'src/app/clusters/thermostat-user-interface-configuration-server/CodegenIntegration.cpp', 'src/app/clusters/thermostat-user-interface-configuration-server/README.md', 'src/app/clusters/thermostat-user-interface-configuration-server/ThermostatUserInterfaceConfigurationDelegate.h', 'data_model/1.7/clusters/ThermostatUserInterfaceConfiguration.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
`ThermostatUserInterfaceConfigurationCluster`는 코드 기반 서버 클러스터로, 클러스터 인스턴스에 속성 값을 저장하고 응용 프로그램 접근을 위한 타입별 getter 및 setter를 제공합니다. `Config`는 초기 값을 제공합니다.

## 스펙
```xml
<cluster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="types types.xsd cluster cluster.xsd" id="0x0204" name="Thermostat User Interface Configuration Cluster" revision="2">
  <revisionHistory>
    <revision revision="1" summary="Mandatory global ClusterRevision attribute added"/>
    <revision revision="2" summary="New data model format and notation, added &quot;Conversion of Temperature Values for Display&quot; section"/>
  </revisionHistory>
  <clusterIds>
    <clusterId id="0x0204" name="Thermostat User Interface Configuration"/>
  </clusterIds>
  <classification hierarchy="base" role="application" picsCode="TSUIC" scope="Endpoint"/>
  <dataTypes>
    <enum name="KeypadLockoutEnum">
      <item value="0" name="NoLockout" summary="All functionality available to the user">
        <mandatoryConform/>
      </item>
      <item value="1" name="Lockout1" summary="Level 1 reduced functionality">
        <mandatoryConform/>
      </item>
      <item value="2" name="Lockout2" summary="Level 2 reduced functionality">
        <mandatoryConform/>
      </item>
      <item value="3" name="Lockout3" summary="Level 3 reduced functionality">
        <mandatoryConform/>
      </item>
      <item value="4" name="Lockout4" summary="Level 4 reduced functionality">
        <mandatoryConform/>
      </item>
      <item value="5" name="Lockout5" summary="Least functionality available to the user">
        <mandatoryConform/>
      </item>
    </enum>
    <enum name="ScheduleProgrammingVisibilityEnum">
      <item value="0" name="ScheduleProgrammingPermitted" summary="Local schedule programming functionality is enabled at the thermostat">
        <mandatoryConform/>
      </item>
      <item value="1" name="ScheduleProgrammingDenied" summary="Local schedule programming functionality is disabled at the thermostat">
        <mandatoryConform/>
      </item>
    </enum>
    <enum name="TemperatureDisplayModeEnum">
      <item value="0" name="Celsius" summary="Temperature displayed in °C">
        <mandatoryConform/>
      </item>
      <item value="1" name="Fahrenheit" summary="Temperature displayed in °F">
        <mandatoryConform/>
      </item>
    </enum>
  </dataTypes>
  <attributes>
    <attribute id="0x0000" name="TemperatureDisplayMode" type="TemperatureDisplayModeEnum">
      <access read="true" write="true" readPrivilege="view" writePrivilege="operate"/>
      <mandatoryConform/>
    </attribute>
    <attribute id="0x0001" name="KeypadLockout" type="KeypadLockoutEnum">
      <access read="true" write="true" readPrivilege="view" writePrivilege="manage"/>
      <mandatoryConform/>
    </attribute>
    <attribute id="0x0002" name="ScheduleProgrammingVisibility" type="ScheduleProgrammingVisibilityEnum">
      <default>
        <enum default="ScheduleProgrammingPermitted"/>
      </default>
      <access read="true" write="true" readPrivilege="view" writePrivilege="manage"/>
      <optionalConform/>
    </attribute>
  </attributes>
</cluster>
```

## SDK 정의
```cpp
class ThermostatUserInterfaceConfigurationCluster : public DefaultServerCluster
{
public:
    using OptionalAttributeSet = app::OptionalAttributeSet<ThermostatUserInterfaceConfiguration::Attributes::ScheduleProgrammingVisibility::Id>;

    struct Config
    {
        Config() :
            temperatureDisplayMode(ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum::kCelsius),
            keypadLockout(ThermostatUserInterfaceConfiguration::KeypadLockoutEnum::kNoLockout),
            scheduleProgrammingVisibility(
                ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum::kScheduleProgrammingPermitted)
        {}

        ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum temperatureDisplayMode;
        ThermostatUserInterfaceConfiguration::KeypadLockoutEnum keypadLockout;
        ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum scheduleProgrammingVisibility;
        OptionalAttributeSet optionalAttributes{};
    };

    ThermostatUserInterfaceConfigurationCluster(EndpointId endpointId, const Config & config = {});
    
    DataModel::ActionReturnStatus ReadAttribute(const DataModel::ReadAttributeRequest & request, AttributeValueEncoder & encoder) override;
    DataModel::ActionReturnStatus WriteAttribute(const DataModel::WriteAttributeRequest & request, AttributeValueDecoder & decoder) override;
    CHIP_ERROR Attributes(const ConcreteClusterPath & path, ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;
    
    void SetDelegate(ThermostatUserInterfaceConfiguration::Delegate * delegate) { mDelegate = delegate; }
    
    ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum GetTemperatureDisplayMode() const { return mTemperatureDisplayMode; }
    ThermostatUserInterfaceConfiguration::KeypadLockoutEnum GetKeypadLockout() const { return mKeypadLockout; }
    ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum GetScheduleProgrammingVisibility() const { return mScheduleProgrammingVisibility; }

protected:
    ThermostatUserInterfaceConfiguration::Delegate * mDelegate = nullptr;
    const OptionalAttributeSet mOptionalAttributes;
    ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum mTemperatureDisplayMode;
    ThermostatUserInterfaceConfiguration::KeypadLockoutEnum mKeypadLockout;
    ThermostatUserInterfaceConfiguration::ScheduleProgrammingVisibilityEnum mScheduleProgrammingVisibility;
};
```

## 구현
```cpp
void MatterThermostatUserInterfaceConfigurationClusterInitCallback(EndpointId endpointId)
{
    IntegrationDelegate integrationDelegate;

    CodegenClusterIntegration::RegisterServer(
        {
            .endpointId                = endpointId,
            .clusterId                 = ThermostatUserInterfaceConfiguration::Id,
            .fixedClusterInstanceCount = kFixedClusterCount,
            .maxClusterInstanceCount   = kMaxClusterCount,
            .fetchFeatureMap           = false,
            .fetchOptionalAttributes   = true,
        },
        integrationDelegate);
}
```

## 예시
```cpp
class ThermostatUiDelegate : public chip::app::Clusters::ThermostatUserInterfaceConfiguration::Delegate
{
public:
    void OnTemperatureDisplayModeChanged(
        chip::app::Clusters::ThermostatUserInterfaceConfiguration::TemperatureDisplayModeEnum value) override
    {
        ChipLogProgress(AppServer, "Temperature display mode changed to %u", static_cast<unsigned>(value));
    }
};

CHIP_ERROR AttachThermostatUiDelegate(chip::EndpointId endpointId)
{
    auto * cluster = chip::app::Clusters::ThermostatUserInterfaceConfiguration::FindClusterOnEndpoint(endpointId);
    VerifyOrReturnError(cluster != nullptr, CHIP_ERROR_NOT_FOUND);
    cluster->SetDelegate(&gThermostatUiDelegate);
    return CHIP_NO_ERROR;
}
```

## 관련 문서
- [클러스터 개발 가이드](../../../../docs/guides/writing_clusters.md)