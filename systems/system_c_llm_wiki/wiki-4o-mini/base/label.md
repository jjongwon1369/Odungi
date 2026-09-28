---
entity: Label
ids: []
source_paths: ['data_model/1.7/clusters/Label-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-4o-mini
---

## 개요
Label 클러스터는 Label과 Value를 포함하는 데이터 구조를 정의합니다. 이 클러스터는 주로 유틸리티 역할을 하며, Endpoint 범위 내에서 사용됩니다.

## 스펙
- 클러스터 이름: Label Cluster
- 버전: 1
- 클러스터 ID: Label

### 데이터 구조
#### LabelStruct
- **Label**: string (기본값: "empty", 최대 길이: 16)
- **Value**: string (기본값: "empty", 최대 길이: 16)

### 속성
- **LabelList**
  - ID: 0x0000
  - 타입: list
  - 항목 타입: LabelStruct
  - 필수 준수: 예