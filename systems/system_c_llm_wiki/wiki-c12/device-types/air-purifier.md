---
entity: Air Purifier
ids: ['0x002D']
source_paths: ['data_model/1.7/device_types/AirPurifier.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Air Purifier

## 개요

`Air Purifier`는 ID가 `0x002D`인 디바이스 타입이다. 제공된 정의의 revision은 `4`이며, 분류는 `simple`, 적용 범위는 `endpoint`이다.

## 스펙

출처: `data_model/1.7/device_types/AirPurifier.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Air Purifier` |
| 디바이스 타입 ID | `0x002D` |
| revision | `4` |
| class | `simple` |
| scope | `endpoint` |

### revision 이력

| revision | 변경 사항 |
|---|---|
| `1` | 최초 정의 |
| `2` | `On/Off` 클러스터 추가 |
| `3` | Groupcast 조건 요구사항 추가 |
| `4` | 선택적 `Humidity Conditioner` 디바이스 타입 요구사항 추가 |

`Humidity Conditioner` 관련 변경은 revision 이력에 기재되어 있으나, 제공된 XML 본문에는 해당 요구사항의 상세 정의가 없다.

### 조건 요구사항

| 대상 디바이스 타입 ID | 대상 디바이스 타입 | 조건 이름 | 적합성 |
|---|---|---|---|
| `0x0016` | `Root Node` | `GroupcastListenerCond` | 선택 (`optionalConform`) |

### 클러스터 요구사항

모든 클러스터의 역할은 `server`이다.

| 클러스터 ID | 클러스터 이름 | 역할 | 적합성 |
|---|---|---|---|
| `0x0003` | `Identify` | `server` | 필수 (`mandatoryConform`) |
| `0x0004` | `Groups` | `server` | 선택 (`optionalConform`) |
| `0x0006` | `On/Off` | `server` | 선택 (`optionalConform`) |
| `0x0071` | `HEPA Filter Monitoring` | `server` | 선택 (`optionalConform`) |
| `0x0072` | `Activated Carbon Filter Monitoring` | `server` | 선택 (`optionalConform`) |
| `0x0202` | `Fan Control` | `server` | 필수 (`mandatoryConform`) |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [Groups `0x0004`](../clusters/0x0004-groups.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [HEPA Filter Monitoring `0x0071`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Activated Carbon Filter Monitoring `0x0072`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Fan Control `0x0202`](../clusters/0x0202-fan-control.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
