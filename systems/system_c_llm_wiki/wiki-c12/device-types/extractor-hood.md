---
entity: Extractor Hood
ids: ['0x007A']
source_paths: ['data_model/1.7/device_types/ExtractorHood.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Extractor Hood

## 개요

`Extractor Hood`는 디바이스 타입 ID가 `0x007A`인 디바이스 타입이다. 분류는 `simple`이며 적용 범위는 `endpoint`이다.

## 스펙

출처: `data_model/1.7/device_types/ExtractorHood.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Extractor Hood` |
| 디바이스 타입 ID | `0x007A` |
| 리비전 | `1` |
| 분류 | `simple` |
| 범위 | `endpoint` |

### 리비전 이력

| 리비전 | 요약 |
|---|---|
| `1` | Initial revision |

### 클러스터 구성

모든 클러스터의 역할은 `server`이다.

| 클러스터 ID | 클러스터 이름 | 적합성 |
|---|---|---|
| `0x0003` | `Identify` | 선택 (`optionalConform`) |
| `0x0071` | `HEPA Filter Monitoring` | 선택 (`optionalConform`) |
| `0x0072` | `Activated Carbon Filter Monitoring` | 선택 (`optionalConform`) |
| `0x0202` | `Fan Control` | 필수 (`mandatoryConform`) |

### `Fan Control` 기능 제약

| 기능 코드 | 적합성 |
|---|---|
| `RCK` | 허용하지 않음 (`disallowConform`) |
| `WND` | 허용하지 않음 (`disallowConform`) |
| `DIR` | 허용하지 않음 (`disallowConform`) |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [HEPA Filter Monitoring `0x0071`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Activated Carbon Filter Monitoring `0x0072`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Fan Control `0x0202`](../clusters/0x0202-fan-control.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
