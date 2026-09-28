---
entity: Laundry Washer
ids: ['0x0073']
source_paths: ['data_model/1.7/device_types/LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
---

# Laundry Washer

## 개요

`Laundry Washer`는 ID가 `0x0073`인 디바이스 타입이다. 분류는 `simple`, 적용 범위는 `endpoint`이며, 현재 리비전은 `2`이다.

## 스펙

출처: `data_model/1.7/device_types/LaundryWasher.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Laundry Washer` |
| 디바이스 타입 ID | `0x0073` |
| 리비전 | `2` |
| 분류 | `simple` |
| 범위 | `endpoint` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `OperationCompletion` 이벤트 필수화 |

### 클러스터 구성

모든 클러스터의 역할은 `server`이다. 선택 클러스터의 추가 요구사항은 해당 클러스터를 지원하는 경우 적용된다.

| 클러스터 ID | 클러스터 이름 | 지원 요구사항 | 추가 요구사항 |
|---|---|---|---|
| `0x0003` | `Identify` | 선택 | — |
| `0x0006` | `On/Off` | 선택 | `DF` 기능 필수 |
| `0x0051` | `Laundry Washer Mode` | 선택 | `DEPONOFF` 기능 및 `StartUpMode` 속성 금지 |
| `0x0053` | `Laundry Washer Controls` | 선택 | — |
| `0x0056` | `Temperature Control` | 선택 | — |
| `0x0060` | `Operational State` | 필수 | `OperationCompletion` 이벤트 필수 |

### 기능·속성·이벤트 제약

| 소속 클러스터 | 종류 | 코드 또는 ID | 이름 | 요구사항 |
|---|---|---|---|---|
| `On/Off` | 기능 | `DF` | — | 필수 |
| `Laundry Washer Mode` | 기능 | `DEPONOFF` | — | 금지 |
| `Laundry Washer Mode` | 속성 | `0x0002` | `StartUpMode` | 금지 |
| `Operational State` | 이벤트 | `0x0001` | `OperationCompletion` | 필수 |

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
