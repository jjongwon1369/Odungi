---
entity: Laundry Washer
ids: ['0x0073']
source_paths: ['data_model/1.7/device_types/LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Laundry Washer

## 개요

`Laundry Washer`는 ID가 `0x0073`인 디바이스 타입이다. 현재 revision은 `2`이며, 분류는 `simple`, 범위는 `endpoint`이다.

## 스펙

출처: `data_model/1.7/device_types/LaundryWasher.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Laundry Washer` |
| 디바이스 타입 ID | `0x0073` |
| revision | `2` |
| class | `simple` |
| scope | `endpoint` |

### revision 이력

| revision | 변경 내용 |
|---|---|
| `1` | 최초 revision |
| `2` | `OperationCompletion` 이벤트 필수화 |

### 클러스터 요구사항

모든 클러스터의 side는 `server`이다.

| 클러스터 ID | 이름 | 적합성 | 추가 요구사항 |
|---|---|---|---|
| `0x0003` | `Identify` | 선택 | — |
| `0x0006` | `On/Off` | 선택 | 기능 `DF` 필수 |
| `0x0051` | `Laundry Washer Mode` | 선택 | 기능 `DEPONOFF` 금지, 속성 `StartUpMode` (`0x0002`) 금지 |
| `0x0053` | `Laundry Washer Controls` | 선택 | — |
| `0x0056` | `Temperature Control` | 선택 | — |
| `0x0060` | `Operational State` | 필수 | 이벤트 `OperationCompletion` (`0x0001`) 필수 |

### 세부 제약

- `On/Off`를 포함하는 경우 기능 `DF`가 필수이다.
- `Laundry Washer Mode`에서는 기능 `DEPONOFF`와 속성 `StartUpMode` (`0x0002`)가 허용되지 않는다.
- `Operational State`와 해당 클러스터의 `OperationCompletion` 이벤트 (`0x0001`)는 필수이다.

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)
- [Laundry Washer Controls `0x0053`](../clusters/0x0053-laundry-washer-controls.md)
- [Temperature Control `0x0056`](../clusters/0x0056-temperature-control.md)
- [Operational State `0x0060`](../clusters/0x0060-operational-state.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
