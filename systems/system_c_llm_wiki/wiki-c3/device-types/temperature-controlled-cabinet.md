---
entity: Temperature Controlled Cabinet
ids: ['0x0071']
source_paths: ['data_model/1.7/device_types/TemperatureControlledCabinet.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Temperature Controlled Cabinet

## 개요

`Temperature Controlled Cabinet`은 endpoint 범위의 `simple` 디바이스 타입이다. 냉각 기능과 가열 기능에 대한 조건을 정의하며, `Temperature Control` 서버 클러스터를 필수로 요구한다.

| 항목 | 값 |
|---|---|
| 디바이스 타입 ID | `0x0071` |
| 이름 | `Temperature Controlled Cabinet` |
| 리비전 | `6` |
| 분류 | `simple` |
| 범위 | `endpoint` |

## 스펙

출처: `data_model/1.7/device_types/TemperatureControlledCabinet.xml`

### 조건

| 조건 | 설명 |
|---|---|
| `Cooler` | 디바이스에 냉각 기능이 있음 |
| `Heater` | 디바이스에 가열 기능이 있음 |

### 클러스터 요구사항

모든 클러스터의 역할은 `server`이다.

| 클러스터 ID | 클러스터 이름 | 적합성 요구사항 |
|---|---|---|
| `0x0052` | `Refrigerator And Temperature Controlled Cabinet Mode` | `Cooler` 조건에서 선택 사항 |
| `0x0056` | `Temperature Control` | 필수 |
| `0x0064` | `Temperature Alarm` | `otherwiseConform` 내에 `provisionalConform`, `optionalConform` 순으로 정의 |
| `0x0402` | `Temperature Measurement` | 선택 사항 |

### 기능 및 속성 제약

| 클러스터 | 구분 | 식별자 | 요구사항 |
|---|---|---|---|
| `Refrigerator And Temperature Controlled Cabinet Mode` | 기능 | `DEPONOFF` | 허용하지 않음 |
| `Refrigerator And Temperature Controlled Cabinet Mode` | 속성 | `StartUpMode` (`0x0002`) | 허용하지 않음 |
| `Temperature Control` | 기능 | `TN` | 필수 |
| `Temperature Control` | 기능 | `TL` | 허용하지 않음 |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 가열 캐비닛으로 확장 |
| `3` | 조건의 상호 배타성 추가 |
| `4` | `Oven Cavity Operational State` 클러스터의 `OperationCompletion` 이벤트 필수화 |
| `5` | `TemperatureNumber` (`TN`)를 유일하게 유효한 온도 제어 모드로 지정 |
| `6` | `Temperature Alarm` 클러스터 추가 |

리비전 이력에는 조건의 상호 배타성과 `OperationCompletion` 이벤트 필수화가 기록되어 있으나, 제공된 XML의 현재 조건 및 클러스터 정의에는 해당 제약이나 이벤트 요구사항이 명시되어 있지 않다.

## 관련 페이지

**직접 클러스터**

- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [Temperature Control `0x0056`](../clusters/0x0056-temperature-control.md)
- [Temperature Alarm `0x0064`](../clusters/0x0064-temperature-alarm.md)
- [Temperature Measurement `0x0402`](../clusters/0x0402-temperature-measurement.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
