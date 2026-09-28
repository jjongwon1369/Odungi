---
entity: Temperature Controlled Cabinet
ids: ['0x0071']
source_paths: ['data_model/1.7/device_types/TemperatureControlledCabinet.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
---

# Temperature Controlled Cabinet

## 개요

- **디바이스 타입 ID:** `0x0071`
- **이름:** Temperature Controlled Cabinet
- **리비전:** `6`
- **분류:** `simple`
- **범위:** `endpoint`

## 스펙

**출처:** `data_model/1.7/device_types/TemperatureControlledCabinet.xml`

### 조건

| 조건 | 설명 |
|---|---|
| `Cooler` | 디바이스에 냉각 기능이 있음 |
| `Heater` | 디바이스에 가열 기능이 있음 |

### 클러스터 구성

모든 클러스터의 `side`는 `server`이다.

| ID | 클러스터 이름 | 적합성 |
|---|---|---|
| `0x0048` | Oven Cavity Operational State | `Heater` 조건에서 선택 |
| `0x0049` | Oven Mode | `Heater` 조건에서 선택 |
| `0x0052` | Refrigerator And Temperature Controlled Cabinet Mode | `Cooler` 조건에서 선택 |
| `0x0056` | Temperature Control | 필수 |
| `0x0064` | Temperature Alarm | `otherwiseConform`에 `provisionalConform`, `optionalConform` 순서로 지정 |
| `0x0402` | Temperature Measurement | 선택 |

### 클러스터별 요구사항

#### Oven Cavity Operational State (`0x0048`)

| 구분 | ID | 이름 | 적합성 |
|---|---|---|---|
| 명령 | `0x0000` | `Pause` | 금지 |
| 명령 | `0x0003` | `Resume` | 금지 |
| 이벤트 | `0x0001` | `OperationCompletion` | 필수 |

#### Oven Mode (`0x0049`)

| 구분 | 코드 | 이름 | 적합성 |
|---|---|---|---|
| 기능 | `DEPONOFF` | — | 금지 |
| 속성 | `0x0002` | `StartUpMode` | 금지 |

#### Refrigerator And Temperature Controlled Cabinet Mode (`0x0052`)

| 구분 | 코드 | 이름 | 적합성 |
|---|---|---|---|
| 기능 | `DEPONOFF` | — | 금지 |
| 속성 | `0x0002` | `StartUpMode` | 금지 |

#### Temperature Control (`0x0056`)

| 구분 | 코드 | 적합성 |
|---|---|---|
| 기능 | `TN` | 필수 |
| 기능 | `TL` | 금지 |

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 가열 캐비닛으로 확장 |
| `3` | 조건에 대한 배타성 추가 |
| `4` | Oven Cavity Operational State 클러스터의 `OperationCompletion` 이벤트를 필수로 지정 |
| `5` | `TemperatureNumber` (`TN`)를 유일하게 유효한 온도 제어 모드로 지정 |
| `6` | Temperature Alarm 클러스터 추가 |

## 관련 페이지

**직접 클러스터**

- [Refrigerator And Temperature Controlled Cabinet Mode `0x0052`](../clusters/0x0052-refrigerator-and-temperature-controlled-cabinet-mode.md)
- [Temperature Control `0x0056`](../clusters/0x0056-temperature-control.md)
- [Temperature Alarm `0x0064`](../clusters/0x0064-temperature-alarm.md)
- [Temperature Measurement `0x0402`](../clusters/0x0402-temperature-measurement.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
