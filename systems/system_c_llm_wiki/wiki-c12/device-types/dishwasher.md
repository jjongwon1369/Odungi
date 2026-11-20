---
entity: Dishwasher
ids: ['0x0075']
source_paths: ['data_model/1.7/device_types/Dishwasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Dishwasher

## 개요

`Dishwasher`는 `endpoint` 범위의 `simple` 디바이스 타입이다.

| 항목 | 값 |
|---|---|
| 디바이스 타입 이름 | `Dishwasher` |
| 디바이스 타입 ID | `0x0075` |
| 리비전 | `2` |
| 분류 | `simple` |
| 범위 | `endpoint` |

## 스펙

출처: `data_model/1.7/device_types/Dishwasher.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `OperationCompletion` 이벤트 필수화 |

### 클러스터 구성

모든 클러스터의 역할은 `server`이다. 선택 클러스터의 세부 요구사항은 해당 클러스터를 포함할 때 적용된다.

| 클러스터 ID | 클러스터 이름 | 적합성 | 세부 요구사항 |
|---|---|---|---|
| `0x0003` | `Identify` | 선택 | — |
| `0x0006` | `On/Off` | 선택 | `DF` 기능 필수 |
| `0x0056` | `Temperature Control` | 선택 | — |
| `0x0059` | `Dishwasher Mode` | 선택 | `DEPONOFF` 기능 및 `StartUpMode` 속성 금지 |
| `0x005D` | `Dishwasher Alarm` | 선택 | — |
| `0x0060` | `Operational State` | 필수 | `OperationCompletion` 이벤트 필수 |

### 세부 적합성 요구사항

| 소속 클러스터 | 종류 | 식별자 | 이름 또는 기능 코드 | 적합성 |
|---|---|---|---|---|
| `On/Off` | 기능 | — | `DF` | 필수 (`mandatoryConform`) |
| `Dishwasher Mode` | 기능 | — | `DEPONOFF` | 금지 (`disallowConform`) |
| `Dishwasher Mode` | 속성 | `0x0002` | `StartUpMode` | 금지 (`disallowConform`) |
| `Operational State` | 이벤트 | `0x0001` | `OperationCompletion` | 필수 (`mandatoryConform`) |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [Temperature Control `0x0056`](../clusters/0x0056-temperature-control.md)
- [Dishwasher Mode `0x0059`](../clusters/0x0059-dishwasher-mode.md)
- [Dishwasher Alarm `0x005D`](../clusters/0x005D-dishwasher-alarm.md)
- [Operational State `0x0060`](../clusters/0x0060-operational-state.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
