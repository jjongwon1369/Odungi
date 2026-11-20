---
entity: Cooktop
ids: ['0x0078']
source_paths: ['data_model/1.7/device_types/Cooktop.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Cooktop

## 개요

`Cooktop`은 디바이스 타입 ID가 `0x0078`인 디바이스 타입이다. 분류는 `simple`이며, 적용 범위는 `endpoint`이다.

## 스펙

출처: `data_model/1.7/device_types/Cooktop.xml`

### 기본 정의

| 항목 | 값 |
|---|---|
| 이름 | `Cooktop` |
| 디바이스 타입 ID | `0x0078` |
| 리비전 | `1` |
| 분류 | `simple` |
| 범위 | `endpoint` |

### 리비전 이력

| 리비전 | 요약 |
|---|---|
| `1` | Initial revision |

### 클러스터 요구사항

| 클러스터 ID | 이름 | 역할 | 요구사항 |
|---|---|---|---|
| `0x0003` | `Identify` | `server` | 선택 |
| `0x0006` | `On/Off` | `server` | 필수 |

### 기능 요구사항

| 클러스터 ID | 클러스터 이름 | 기능 코드 | 요구사항 |
|---|---|---|---|
| `0x0006` | `On/Off` | `OFFONLY` | 필수 |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
