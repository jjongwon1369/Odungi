---
entity: Cook Surface
ids: ['0x0077']
source_paths: ['data_model/1.7/device_types/CookSurface.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Cook Surface

## 개요

`Cook Surface`는 `endpoint` 범위의 `simple` 장치 유형이다.

| 항목 | 값 |
|---|---|
| 장치 유형 ID | `0x0077` |
| 이름 | `Cook Surface` |
| 리비전 | `2` |
| 분류 | `simple` |
| 범위 | `endpoint` |

## 스펙

출처: `data_model/1.7/device_types/CookSurface.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `TemperatureLevel (TL)`을 유일하게 유효한 온도 제어 모드로 지정 |

### 클러스터 구성

모든 클러스터의 역할은 `server`이다.

| 클러스터 ID | 이름 | 적합성 |
|---|---|---|
| `0x0006` | `On/Off` | 선택 |
| `0x0056` | `Temperature Control` | 선택 그룹 `a`: 그룹 내 최소 하나 이상 필요 |
| `0x0402` | `Temperature Measurement` | 선택 그룹 `a`: 그룹 내 최소 하나 이상 필요 |

`Temperature Control`과 `Temperature Measurement`에는 각각 `optionalConform`의 `choice="a"`, `more="true"`, `min="1"`이 지정되어 있다. 따라서 두 클러스터 중 하나 이상을 지원해야 하며, 둘 다 지원할 수 있다.

### 기능 요구사항

해당 클러스터를 지원할 때 적용되는 기능 요구사항은 다음과 같다.

| 클러스터 | 기능 코드 | 요구사항 |
|---|---|---|
| `On/Off` (`0x0006`) | `OFFONLY` | 필수 (`mandatoryConform`) |
| `Temperature Control` (`0x0056`) | `TL` | 필수 (`mandatoryConform`) |
| `Temperature Control` (`0x0056`) | `TN` | 허용되지 않음 (`disallowConform`) |

## 관련 페이지

**직접 클러스터**

- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [Temperature Control `0x0056`](../clusters/0x0056-temperature-control.md)
- [Temperature Measurement `0x0402`](../clusters/0x0402-temperature-measurement.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
