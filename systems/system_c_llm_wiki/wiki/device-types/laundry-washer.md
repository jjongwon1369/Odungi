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