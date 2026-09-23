---
entity: Label
ids: []
source_paths: ['data_model/1.7/clusters/Label-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 클러스터 개요

- 클러스터 이름: `Label Cluster`
- 클러스터 식별자: `Label`
- Revision: `1`
- 계층: `base`
- 역할: `utility`
- PICS 코드: `LABEL`
- 범위: `Endpoint`

### Revision History

| Revision | Summary |
|---|---|
| `1` | `Initial revision` |

### 데이터 타입

#### `LabelStruct`

| Field ID | 이름 | 타입 | 기본값 | 필수 | 제약 조건 |
|---:|---|---|---|---|---|
| `0` | `Label` | `string` | `empty` | 예 | `maxLength` `16` |
| `1` | `Value` | `string` | `empty` | 예 | `maxLength` `16` |

### 속성

#### `LabelList`

- Attribute ID: `0x0000`
- 타입: `list`
- Entry 타입: `LabelStruct`
- 필수: 예