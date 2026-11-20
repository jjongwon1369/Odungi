---
entity: Water Heater
ids: ['0x050F']
source_paths: ['data_model/1.7/device_types/WaterHeater.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Water Heater

## 개요

| 항목 | 값 |
|---|---|
| 이름 | Water Heater |
| Device Type ID | `0x050F` |
| Revision | `2` |
| 분류 | `simple` |
| 범위 | `endpoint` |
| 스펙 파일 | `data_model/1.7/device_types/WaterHeater.xml` |

## 스펙

### Revision 이력

| Revision | 변경 사항 |
|---|---|
| `1` | 최초 정의 |
| `2` | 선택 사항인 Thermostat Mode 및 Thermostat User Interface Configuration 클러스터 추가. Device Energy Management 클러스터에서 PowerAdjustment 또는 PowerRangeAdjustment 선택 추가. |

> Device Energy Management 관련 변경은 Revision 이력에만 기재되어 있으며, 제공된 XML의 클러스터 요구사항에는 해당 클러스터가 포함되어 있지 않다.

### 클러스터 요구사항

아래 클러스터의 `side`는 모두 `server`이다.

| ID | 이름 | 적합성 요구사항 |
|---|---|---|
| `0x0003` | Identify | 선택 |
| `0x0063` | Thermostat Mode | `otherwiseConform`: `provisionalConform`, 이후 현재 Revision이 `2` 이상일 때 선택 |
| `0x0094` | Water Heater Management | 필수 |
| `0x009E` | Water Heater Mode | 필수 |
| `0x0201` | Thermostat | 필수 |
| `0x0204` | Thermostat User Interface Configuration | 현재 Revision이 `2` 이상일 때 선택 |

### Thermostat Mode 속성 요구사항

| Code | 이름 | 적합성 요구사항 | 제약 |
|---|---|---|---|
| `0x0002` | StartUpMode | `otherwiseConform`: `provisionalConform`, 이후 `disallowConform` | 별도 기재 없음 |
| `0x0000` | SupportedModes | `otherwiseConform`: `provisionalConform`, 이후 `mandatoryConform` | `constraint` 내 `desc`가 비어 있음 |

### Thermostat 기능 요구사항

| Feature code | 적합성 요구사항 |
|---|---|
| `HEAT` | 필수 |

### 구성 Device Type

`composedDeviceTypes`에는 다음 Device Type과 클러스터 요구사항이 정의되어 있다.

| Device Type ID | Device Type 이름 |
|---|---|
| `0x0510` | Electrical Sensor |

| 클러스터 ID | 클러스터 이름 | 적합성 요구사항 |
|---|---|---|
| `0x0090` | Electrical Power Measurement | 필수 |
| `0x0091` | Electrical Energy Measurement | 필수 |

### 원문 구조 참고

제공된 XML에는 `composedDeviceTypes` 요소가 두 번 등장한다.

- 첫 번째 요소는 Electrical Sensor의 `deviceType`과 `clusterRequirements`를 포함한다.
- 두 번째 요소는 앞선 `clusters`의 여섯 클러스터를 직접 포함하며, 속성 및 기능 요구사항도 동일하게 반복한다.

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
- [Water Heater Management `0x0094`](../clusters/0x0094-water-heater-management.md)
- [Water Heater Mode `0x009E`](../clusters/0x009E-water-heater-mode.md)
- [Thermostat `0x0201`](../clusters/0x0201-thermostat.md)
- [Thermostat User Interface Configuration `0x0204`](../clusters/0x0204-thermostat-user-interface-configuration.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
