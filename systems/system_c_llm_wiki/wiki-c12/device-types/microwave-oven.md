---
entity: Microwave Oven
ids: ['0x0079']
source_paths: ['data_model/1.7/device_types/MicrowaveOven.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Microwave Oven

## 개요

`Microwave Oven`은 ID가 `0x0079`인 디바이스 타입이다. 분류는 `simple`, 범위는 `endpoint`이며, 현재 리비전은 `2`이다.

## 스펙

출처: `data_model/1.7/device_types/MicrowaveOven.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Microwave Oven` |
| 디바이스 타입 ID | `0x0079` |
| 리비전 | `2` |
| 분류 | `simple` |
| 범위 | `endpoint` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `OperationCompletion` 이벤트 필수화 |

### 클러스터 구성

모든 클러스터의 역할은 `server`이다.

| 클러스터 ID | 이름 | 적합성 |
|---|---|---|
| `0x0003` | `Identify` | 선택 |
| `0x005E` | `Microwave Oven Mode` | 필수 |
| `0x005F` | `Microwave Oven Control` | 필수 |
| `0x0060` | `Operational State` | 필수 |
| `0x0202` | `Fan Control` | 선택 |

### Operational State 요구 사항

| 종류 | ID / 코드 | 이름 | 적합성 |
|---|---|---|---|
| 속성 | `0x0002` | `CountdownTime` | 필수 |
| 이벤트 | `0x0001` | `OperationCompletion` | 필수 |

### Fan Control 제약

`Fan Control`은 선택 클러스터이나, 다음 기능은 허용되지 않는다.

| 기능 코드 | 적합성 |
|---|---|
| `WND` | 금지 (`disallowConform`) |
| `DIR` | 금지 (`disallowConform`) |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [Microwave Oven Mode `0x005E`](../clusters/0x005E-microwave-oven-mode.md)
- [Microwave Oven Control `0x005F`](../clusters/0x005F-microwave-oven-control.md)
- [Operational State `0x0060`](../clusters/0x0060-operational-state.md)
- [Fan Control `0x0202`](../clusters/0x0202-fan-control.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
