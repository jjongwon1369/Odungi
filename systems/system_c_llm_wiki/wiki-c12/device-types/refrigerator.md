---
entity: Refrigerator
ids: ['0x0070']
source_paths: ['data_model/1.7/device_types/Refrigerator.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Refrigerator

## 개요

`Refrigerator`는 ID가 `0x0070`인 디바이스 타입이다. 현재 정의의 revision은 `3`이며, 분류는 `simple`, 범위는 `endpoint`이다.

## 스펙

출처: `data_model/1.7/device_types/Refrigerator.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Refrigerator` |
| 디바이스 타입 ID | `0x0070` |
| revision | `3` |
| class | `simple` |
| scope | `endpoint` |

### 개정 이력

| revision | 변경 사항 |
|---|---|
| `1` | 최초 개정 |
| `2` | `Cooler` 요구사항 추가 |
| `3` | 선택적 `Activated Carbon Filter Monitoring` 클러스터 추가 |

### 조건 요구사항

| 대상 디바이스 타입 | ID | 조건 | 요구 수준 |
|---|---|---|---|
| `Temperature Controlled Cabinet` | `0x0071` | `Cooler` | 필수 (`mandatoryConform`) |

### 클러스터 요구사항

모든 클러스터의 side는 `server`이다.

| 클러스터 ID | 이름 | 적합성 |
|---|---|---|
| `0x0003` | `Identify` | 선택 (`optionalConform`) |
| `0x0052` | `Refrigerator And Temperature Controlled Cabinet Mode` | 선택 (`optionalConform`) |
| `0x0057` | `Refrigerator Alarm` | 선택 (`optionalConform`) |
| `0x0072` | `Activated Carbon Filter Monitoring` | 현재 revision이 `3` 이상일 때 선택 (`optionalConform`) |

### 기능 및 속성 제한

`Refrigerator And Temperature Controlled Cabinet Mode` (`0x0052`)에는 다음 제한이 적용된다.

| 구분 | 식별자 | 코드 | 적합성 |
|---|---|---|---|
| 기능 | `DEPONOFF` | `DEPONOFF` | 금지 (`disallowConform`) |
| 속성 | `StartUpMode` | `0x0002` | 금지 (`disallowConform`) |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [Refrigerator Alarm `0x0057`](../clusters/0x0057-refrigerator-alarm.md)
- [Activated Carbon Filter Monitoring `0x0072`](../clusters/0x0071-hepa-filter-monitoring.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
