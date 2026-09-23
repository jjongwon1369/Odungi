---
entity: Refrigerator
ids: ['0x0070']
source_paths: ['data_model/1.7/device_types/Refrigerator.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-5.6-luna
---

## 스펙

- 정의 파일: `data_model/1.7/device_types/Refrigerator.xml`
- Device Type:
  - 이름: `Refrigerator`
  - ID: `0x0070`
  - Revision: `3`
  - Classification: `simple`
  - Scope: `endpoint`

### Revision History

| Revision | Summary |
|---:|---|
| `1` | Initial revision |
| `2` | Added Cooler requirement |
| `3` | Added optional Activated Carbon Filter Monitoring cluster |

### Condition Requirements

`Temperature Controlled Cabinet` (`0x0071`)에 대해 다음 조건을 요구합니다.

| Condition | Requirement |
|---|---|
| `Cooler` | Mandatory |

### 클러스터

| Cluster ID | Cluster | Side | Conformance | 제한 사항 |
|---|---|---|---|---|
| `0x0003` | `Identify` | `server` | Optional | 없음 |
| `0x0052` | `Refrigerator And Temperature Controlled Cabinet Mode` | `server` | Optional | `DEPONOFF` feature disallowed; `StartUpMode` attribute (`0x0002`) disallowed |
| `0x0057` | `Refrigerator Alarm` | `server` | Optional | 없음 |
| `0x0072` | `Activated Carbon Filter Monitoring` | `server` | Optional when revision is greater than or equal to `3` | 없음 |

### `Refrigerator And Temperature Controlled Cabinet Mode` 제한 사항

- Feature `DEPONOFF`: `disallowConform`
- Attribute `StartUpMode` (`0x0002`): `disallowConform`

### `Activated Carbon Filter Monitoring` 적용 조건

`Activated Carbon Filter Monitoring` 클러스터는 revision `3` 이상에서 optional conform입니다.