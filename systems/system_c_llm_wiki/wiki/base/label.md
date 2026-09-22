---
entity: Label
ids: []
source_paths: ['data_model/1.7/clusters/Label-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
---

## 개요
* Cluster Name: Label Cluster
* Revision: 1
* Classification:
  * Hierarchy: base
  * Role: utility
  * PICS Code: LABEL
  * Scope: Endpoint

## 스펙
### Data Types
#### LabelStruct (Struct)
| Field ID | Field Name | Type | Default | Constraint | Conformance |
| --- | --- | --- | --- | --- | --- |
| 0 | Label | string | empty | maxLength 16 | Mandatory |
| 1 | Value | string | empty | maxLength 16 | Mandatory |

### Attributes
| ID | Name | Type | Conformance |
| --- | --- | --- | --- |
| 0x0000 | LabelList | list[LabelStruct] | Mandatory |