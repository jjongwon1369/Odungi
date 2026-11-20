---
entity: Label
ids: []
source_paths: ['data_model/1.7/clusters/Label-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Label

## 개요

`Label Cluster`는 `Endpoint` 범위의 `utility` 역할을 갖는 `base` 클러스터이다.

| 항목 | 정의 |
|---|---|
| 엔티티 | `Label` |
| 클러스터 이름 | `Label Cluster` |
| 리비전 | `1` |
| 계층 | `base` |
| 역할 | `utility` |
| PICS 코드 | `LABEL` |
| 범위 | `Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/Label-Cluster.xml`

### 클러스터 식별자

`clusterId`의 이름은 `Label`이다. 원문에는 숫자 클러스터 ID가 지정되어 있지 않다.

### 리비전 이력

| 리비전 | 설명 |
|---|---|
| `1` | Initial revision |

### 데이터 타입

#### `LabelStruct`

| 필드 ID | 이름 | 타입 | 필수 여부 | 기본값 | 제약 |
|---|---|---|---|---|---|
| `0` | `Label` | `string` | 필수 | `empty` | 최대 길이 `16` |
| `1` | `Value` | `string` | 필수 | `empty` | 최대 길이 `16` |

### 속성

| 속성 ID | 이름 | 타입 | 항목 타입 | 필수 여부 |
|---|---|---|---|---|
| `0x0000` | `LabelList` | `list` | `LabelStruct` | 필수 |

## 관련 페이지

**파생 클러스터**

- [User Label `0x0041`](../clusters/0x0041-user-label.md)
