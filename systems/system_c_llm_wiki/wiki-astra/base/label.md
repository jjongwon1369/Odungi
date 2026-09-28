---
entity: Label
ids: []
source_paths: ['data_model/1.7/clusters/Label-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
---

# Label

## 개요

`Label Cluster`는 `Endpoint` 범위의 `utility` 역할을 가진 기본(`base`) 클러스터이다. 제공된 스펙의 revision은 `1`이며, `LabelStruct` 목록을 담는 `LabelList` 속성을 정의한다.

## 스펙

출처: `data_model/1.7/clusters/Label-Cluster.xml`

### 클러스터 정의

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Label Cluster` |
| 식별 이름 | `Label` |
| 클러스터 ID | 원문에 수치 ID가 명시되지 않음 |
| revision | `1` |
| hierarchy | `base` |
| role | `utility` |
| picsCode | `LABEL` |
| scope | `Endpoint` |

### 개정 이력

| revision | summary |
|---|---|
| `1` | `Initial revision` |

### 데이터 타입

#### LabelStruct

| 필드 ID | 이름 | 타입 | 필수 여부 | 기본값 | 제약 |
|---|---|---|---|---|---|
| `0` | `Label` | `string` | 필수 | `empty` | `maxLength`: `16` |
| `1` | `Value` | `string` | 필수 | `empty` | `maxLength`: `16` |

### 속성

| 속성 ID | 이름 | 타입 | 항목 타입 | 필수 여부 |
|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | 필수 |