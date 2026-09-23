---
entity: Temperature Controlled Cabinet
ids: ['0x0071']
source_paths: ['data_model/1.7/device_types/TemperatureControlledCabinet.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 디바이스 타입

- 이름: `Temperature Controlled Cabinet`
- ID: `0x0071`
- Revision: `6`
- Classification: `simple`
- Scope: `endpoint`

### Revision History

| Revision | Summary |
|---|---|
| `1` | Initial revision |
| `2` | Extension to heating cabinets |
| `3` | Added exclusivity for conditions |
| `4` | Mandate `OperationCompletion` Event for `Oven Cavity Operational State` cluster |
| `5` | Made `TemperatureNumber (TN)` the only valid temperature control mode |
| `6` | Added `Temperature Alarm` cluster |

### Conditions

| Condition | Summary |
|---|---|
| `Cooler` | The device has cooling functionality. |
| `Heater` | The device has heating functionality. |

### 클러스터

#### `0x0048` — `Oven Cavity Operational State`

- Side: `server`
- 조건: `Heater`인 경우 선택 사항
- Commands:
  - `0x0000` — `Pause`: 사용 불가
  - `0x0003` — `Resume`: 사용 불가
- Events:
  - `0x0001` — `OperationCompletion`: 필수

#### `0x0049` — `Oven Mode`

- Side: `server`
- 조건: `Heater`인 경우 선택 사항
- Features:
  - `DEPONOFF`: 사용 불가
- Attributes:
  - `0x0002` — `StartUpMode`: 사용 불가

#### `0x0052` — `Refrigerator And Temperature Controlled Cabinet Mode`

- Side: `server`
- 조건: `Cooler`인 경우 선택 사항
- Features:
  - `DEPONOFF`: 사용 불가
- Attributes:
  - `0x0002` — `StartUpMode`: 사용 불가

#### `0x0056` — `Temperature Control`

- Side: `server`
- 필수 클러스터
- Features:
  - `TN`: 필수
  - `TL`: 사용 불가

#### `0x0064` — `Temperature Alarm`

- Side: `server`
- 잠정적 선택 사항

#### `0x0402` — `Temperature Measurement`

- Side: `server`
- 선택 사항