---
entity: Room Air Conditioner
ids: ['0x0072']
source_paths: ['data_model/1.7/device_types/RoomAirConditioner.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-5.6-luna
---

# Room Air Conditioner

## 스펙

- 정의 파일: `data_model/1.7/device_types/RoomAirConditioner.xml`
- Device Type ID: `0x0072`
- Device Type 이름: `Room Air Conditioner`
- Revision: `5`
- Classification:
  - Class: `simple`
  - Scope: `endpoint`

### Revision History

| Revision | Summary |
|---|---|
| `1` | Initial revision |
| `2` | Thermostat User Interface Configuration cluster added; Updated the Scenes cluster to Scenes Management with Cluster ID: `0x0062` |
| `3` | Added filter monitoring clusters |
| `4` | Added Groupcast condition requirement |
| `5` | Added Thermostat Mode cluster. |

### Condition Requirements

`Root Node` Device Type(`0x0016`)에 대해 다음 조건이 적용됩니다.

| Condition Requirement | Conformance |
|---|---|
| `GroupcastListenerCond` | `optionalConform` |

### Clusters

| Cluster ID | Cluster 이름 | Side | Conformance |
|---|---|---|---|
| `0x0003` | `Identify` | `server` | `mandatoryConform` |
| `0x0004` | `Groups` | `server` | `optionalConform` |
| `0x0006` | `On/Off` | `server` | `mandatoryConform` |
| `0x0062` | `Scenes Management` | `server` | `optionalConform` |
| `0x0063` | `Thermostat Mode` | `server` | `provisionalConform`; Revision `5` 이상에서 `optionalConform` |
| `0x0071` | `HEPA Filter Monitoring` | `server` | `optionalConform` |
| `0x0072` | `Activated Carbon Filter Monitoring` | `server` | `optionalConform` |
| `0x0201` | `Thermostat` | `server` | `mandatoryConform` |
| `0x0202` | `Fan Control` | `server` | `optionalConform` |
| `0x0204` | `Thermostat User Interface Configuration` | `server` | `optionalConform` |
| `0x0402` | `Temperature Measurement` | `server` | `optionalConform` |
| `0x0405` | `Relative Humidity Measurement` | `server` | `optionalConform` |

### Cluster별 세부 사항

#### `0x0006` — `On/Off`

- `DF` feature: `mandatoryConform`

#### `0x0063` — `Thermostat Mode`

- Cluster conformance:
  - 기본: `provisionalConform`
  - 현재 Revision이 `5` 이상인 경우: `optionalConform`

| Attribute Code | Attribute 이름 | Conformance | Constraint |
|---|---|---|---|
| `0x0002` | `StartUpMode` | `provisionalConform`, `disallowConform` | — |
| `0x0000` | `SupportedModes` | `provisionalConform`, `mandatoryConform` | 정의된 설명 없음 |

#### `0x0204` — `Thermostat User Interface Configuration`

| Attribute Code | Attribute 이름 | Conformance |
|---|---|---|
| `0x0001` | `KeypadLockout` | `optionalConform` |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [Groups `0x0004`](../clusters/0x0004-groups.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [Scenes Management `0x0062`](../clusters/0x0062-scenes-management.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
- [HEPA Filter Monitoring `0x0071`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Thermostat `0x0201`](../clusters/0x0201-thermostat.md)
- [Fan Control `0x0202`](../clusters/0x0202-fan-control.md)
- [Thermostat User Interface Configuration `0x0204`](../clusters/0x0204-thermostat-user-interface-configuration.md)
- [Temperature Measurement `0x0402`](../clusters/0x0402-temperature-measurement.md)
- [Relative Humidity Measurement `0x0405`](../clusters/0x0405-relative-humidity-measurement.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
