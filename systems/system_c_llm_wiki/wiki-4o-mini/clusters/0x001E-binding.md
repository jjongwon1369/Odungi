---
entity: Binding
ids: ['0x001E']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/binding-cluster.xml', 'src/app/clusters/bindings/BindingManager.cpp', 'src/app/clusters/bindings/BindingCluster.h', 'src/app/clusters/bindings/binding-table.h', 'src/app/clusters/bindings/PendingNotificationMap.h', 'src/app/clusters/bindings/BindingManager.h', 'src/app/clusters/bindings/CodegenIntegration.cpp', 'src/app/clusters/bindings/PendingNotificationMap.cpp', 'src/app/clusters/bindings/README.md', 'src/app/clusters/bindings/BindingCluster.cpp', 'src/app/clusters/bindings/binding-table.cpp', 'data_model/1.7/clusters/Binding-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-4o-mini
---

## 개요
Binding Cluster는 Zigbee Device Object (ZDO)의 지원을 대체하기 위해 설계되었으며 바인딩 테이블을 지원합니다.

## 스펙
```xml
<cluster xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="types types.xsd cluster cluster.xsd" id="0x001E" name="Binding Cluster" revision="1">
  <revisionHistory>
    <revision revision="1" summary="Initial revision"/>
  </revisionHistory>
  <clusterIds>
    <clusterId id="0x001E" name="Binding"/>
  </clusterIds>
  <classification hierarchy="base" role="utility" picsCode="BIND" scope="Endpoint"/>
  <dataTypes>
    <struct name="TargetStruct">
      <field id="1" name="Node" type="node-id">
        <mandatoryConform>
          <field name="Endpoint"/>
        </mandatoryConform>
      </field>
      <field id="2" name="Group" type="group-id">
        <mandatoryConform>
          <notTerm>
            <field name="Endpoint"/>
          </notTerm>
        </mandatoryConform>
        <constraint>
          <min value="1"/>
        </constraint>
      </field>
      <field id="3" name="Endpoint" type="endpoint-no">
        <mandatoryConform>
          <notTerm>
            <field name="Group"/>
          </notTerm>
        </mandatoryConform>
      </field>
      <field id="4" name="Cluster" type="cluster-id">
        <optionalConform/>
      </field>
      <access fabricScoped="true"/>
    </struct>
  </dataTypes>
  <attributes>
    <attribute id="0x0000" name="Binding" type="list" default="empty">
      <entry type="TargetStruct"/>
      <access read="true" write="true" readPrivilege="view" writePrivilege="manage" fabricScoped="true"/>
      <quality persistence="nonVolatile"/>
      <mandatoryConform/>
      <constraint>
        <desc/>
      </constraint>
    </attribute>
  </attributes>
</cluster>
```

## SDK 정의
클러스터 관리자는 `BindingCluster` 및 관련 매니저를 통해 바인딩 작성을 처리하며, 모든 바인딩은 클러스터 내 `TargetStruct` 타입을 사용하여 표현됩니다.

## 구현
`BindingManager`는 바인딩 테이블을 생성 및 관리하며, 새로운 바인딩이 생성될 때 고객에게 알림을 보냅니다. 바인딩의 추가 및 삭제는 다음과 같은 메서드로 호출됩니다.
```cpp
CHIP_ERROR Manager::AddBindingEntry(const Binding::TableEntry & entry);
CHIP_ERROR Manager::UnicastBindingCreated(uint8_t fabricIndex, NodeId nodeId);
CHIP_ERROR Manager::UnicastBindingRemoved(uint8_t bindingEntryId);
```

## 예시
Binding Cluster의 바인딩을 사용하여 unicast 및 multicast 바인딩을 설정하는 방법은 다음과 같습니다.
```cpp
Binding::TableEntry entry(fabricIndex, node, localEndpoint, remoteEndpoint, clusterId);
Binding::Manager::GetInstance().AddBindingEntry(entry);
```

## 관련 문서
- [Binding-Cluster.xml](spec/data_model/1.7/clusters/Binding-Cluster.xml)
- [BindingManager.cpp](impl/src/app/clusters/bindings/BindingManager.cpp)
- [BindingCluster.h](impl/src/app/clusters/bindings/BindingCluster.h)
- [README.md](doc/src/app/clusters/bindings/README.md)