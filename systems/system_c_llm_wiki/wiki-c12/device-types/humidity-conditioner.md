---
entity: Humidity Conditioner
ids: ['0x007D']
source_paths: ['data_model/1.7/device_types/HumidityConditioner.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Humidity Conditioner

## 개요

`Humidity Conditioner`는 장치 유형 ID가 `0x007D`인 장치 유형이다. 분류는 `simple`이며, 범위는 `endpoint`이다.

## 스펙

출처: `data_model/1.7/device_types/HumidityConditioner.xml`

### 장치 유형 정의

| 항목 | 값 |
|---|---|
| `name` | `Humidity Conditioner` |
| `id` | `0x007D` |
| `revision` | `1` |
| `class` | `simple` |
| `scope` | `endpoint` |

### 개정 이력

| `revision` | `summary` |
|---|---|
| `1` | `Initial revision` |

### 클러스터 구성

모든 클러스터의 `side`는 `server`이다.

| 클러스터 ID | 이름 | 적합성 |
|---|---|---|
| `0x0003` | `Identify` | 필수 (`mandatoryConform`) |
| `0x0006` | `On/Off` | 필수 (`mandatoryConform`) |
| `0x0079` | `Water Tank Level Monitoring` | 선택 (`optionalConform`) |
| `0x0202` | `Fan Control` | 선택 (`optionalConform`) |
| `0x0205` | `Humidistat` | `otherwiseConform` 내에 `provisionalConform`, `mandatoryConform` 순서로 정의 |
| `0x0405` | `Relative Humidity Measurement` | 선택 (`optionalConform`) |

### `On/Off` 기능 요구사항

| 기능 코드 | 적합성 |
|---|---|
| `LT` | 금지 (`disallowConform`) |
| `DF` | 필수 (`mandatoryConform`) |

### `Humidistat` 적합성 정의

원문의 적합성 구조는 다음과 같다.

```xml
<otherwiseConform>
  <provisionalConform/>
  <mandatoryConform/>
</otherwiseConform>
```

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [Water Tank Level Monitoring `0x0079`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Fan Control `0x0202`](../clusters/0x0202-fan-control.md)
- [Humidistat `0x0205`](../clusters/0x0205-humidistat.md)
- [Relative Humidity Measurement `0x0405`](../clusters/0x0405-relative-humidity-measurement.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
