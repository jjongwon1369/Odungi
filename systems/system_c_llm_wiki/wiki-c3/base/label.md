---
entity: Label
ids: []
source_paths: ['data_model/1.7/clusters/Label-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Label

## 개요

`Label Cluster`는 `Endpoint` 범위의 `utility` 역할을 갖는 `base` 클러스터이다. `LabelStruct` 목록인 `LabelList`를 정의한다.

## 스펙

출처: `data_model/1.7/clusters/Label-Cluster.xml`

### 기본 정보

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Label Cluster` |
| 클러스터 식별자 이름 | `Label` |
| 클러스터 ID | 원문에 숫자 ID가 명시되지 않음 |
| 리비전 | `1` |
| 계층 | `base` |
| 역할 | `utility` |
| PICS 코드 | `LABEL` |
| 범위 | `Endpoint` |

### 리비전 이력

| 리비전 | 요약 |
|---|---|
| `1` | Initial revision |

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

## 관련 페이지

**파생 클러스터**

- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
