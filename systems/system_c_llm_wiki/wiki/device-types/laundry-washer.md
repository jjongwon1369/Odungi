---
entity: Laundry Washer
ids: ['0x0073']
source_paths: ['data_model/1.7/device_types/LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-5.6-luna
---

# Laundry Washer

## 스펙

- **정의 파일:** `data_model/1.7/device_types/LaundryWasher.xml`
- **Device Type ID:** `0x0073`
- **Device Type Name:** `Laundry Washer`
- **Revision:** `2`
- **Classification:** `simple`
- **Scope:** `endpoint`

### Revision History

| Revision | Summary |
|---|---|
| `1` | `Initial revision` |
| `2` | `Mandate OperationCompletion Event` |

### 클러스터

| Cluster ID | Cluster Name | Side | Conformance |
|---|---|---|---|
| `0x0003` | `Identify` | `server` | Optional |
| `0x0006` | `On/Off` | `server` | Optional |
| `0x0051` | `Laundry Washer Mode` | `server` | Optional |
| `0x0053` | `Laundry Washer Controls` | `server` | Optional |
| `0x0056` | `Temperature Control` | `server` | Optional |
| `0x0060` | `Operational State` | `server` | Mandatory |

### 클러스터별 요구사항

#### `0x0003` — `Identify`

- `server` 측 클러스터
- Optional conformance

#### `0x0006` — `On/Off`

- `server` 측 클러스터
- Optional conformance
- Feature:
  - `DF`: Mandatory conformance

#### `0x0051` — `Laundry Washer Mode`

- `server` 측 클러스터
- Optional conformance
- Feature:
  - `DEPONOFF`: Disallowed conformance
- Attribute:
  - Code: `0x0002`
  - Name: `StartUpMode`
  - Disallowed conformance

#### `0x0053` — `Laundry Washer Controls`

- `server` 측 클러스터
- Optional conformance

#### `0x0056` — `Temperature Control`

- `server` 측 클러스터
- Optional conformance

#### `0x0060` — `Operational State`

- `server` 측 클러스터
- Mandatory conformance
- Event:
  - ID: `0x0001`
  - Name: `OperationCompletion`
  - Mandatory conformance

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
