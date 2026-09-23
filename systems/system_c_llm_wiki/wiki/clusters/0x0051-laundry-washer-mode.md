---
entity: Laundry Washer Mode
ids: ['0x0051']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml', 'data_model/1.7/clusters/Mode_LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 클러스터 개요

- 클러스터: `Laundry Washer Mode Cluster`
- 클러스터 ID: `0x0051`
- 버전: `revision="4"`
- 분류: `derived`
- 기반 클러스터: `Mode Base`
- 역할: `application`
- PICS 코드: `LWM`
- 범위: `Endpoint`

### Revision History

| Revision | Summary |
|---|---|
| 1 | Initial revision |
| 2 | `ChangeToModeResponse` command: `StatusText` must be provided for `InvalidInMode` status |
| 3 | Set `OnOff` feature, `StartUpMode`, and `OnMode` as disallowed (previously a Device Type override) |
| 4 | Adopt latest version of base cluster |

### Features

| Bit | Code | Name | Summary | 적합성 |
|---:|---|---|---|---|
| 0 | `DEPONOFF` | `OnOff` | Dependency with the OnOff cluster | Disallowed |

### 데이터 타입

#### `ModeTag`

| 값 | 이름 |
|---|---|
| `0x00` | `Auto` |
| `0x01` | `Quick` |
| `0x02` | `Quiet` |
| `0x03` | `LowNoise` |
| `0x04` | `LowEnergy` |
| `0x05` | `Vacation` |
| `0x06` | `Min` |
| `0x07` | `Max` |
| `0x08` | `Night` |
| `0x09` | `Day` |
| `0x4000` | `Normal` |
| `0x4001` | `Delicate` |
| `0x4002` | `Heavy` |
| `0x4003` | `Whites` |

#### `ModeOptionStruct`

| ID | 필드 | 적합성 | 제약 |
|---:|---|---|---|
| 0 | `Label` | Mandatory | — |
| 1 | `Mode` | Mandatory | — |
| 2 | `ModeTags` | Mandatory | 값의 개수는 `1` 이상 `8` 이하 |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | Mandatory |
| `0x0001` | `CurrentMode` | Mandatory |
| `0x0002` | `StartUpMode` | Disallowed |
| `0x0003` | `OnMode` | Disallowed |

## SDK 정의

### 원본

`src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml`

### 클러스터 정의

| 항목 | 값 |
|---|---|
| Domain | `Appliances` |
| Name | `Laundry Washer Mode` |
| Code | `0x0051` |
| Define | `LAUNDRY_WASHER_MODE_CLUSTER` |
| Client | 지원 |
| Server | 지원 |
| 설명 | Attributes and commands for selecting a mode from a list of supported options. |

### Feature

| Bit | Code | Name | Summary | API maturity |
|---:|---|---|---|---|
| 1 | `COREMODES` | `CoreModes` | One or more core modes are supported | `provisional` |

`CoreModes` Feature가 적용되는 경우 `CoreModeTags`와 `ChangeToModeByCoreTag`의 적합성이 요구됩니다.

### `ModeTag`

| 값 | 이름 |
|---|---|
| `0x0000` | `Auto` |
| `0x0001` | `Quick` |
| `0x0002` | `Quiet` |
| `0x0003` | `LowNoise` |
| `0x0004` | `LowEnergy` |
| `0x0005` | `Vacation` |
| `0x0006` | `Min` |
| `0x0007` | `Max` |
| `0x0008` | `Night` |
| `0x0009` | `Day` |
| `0x4000` | `Normal` |
| `0x4001` | `Delicate` |
| `0x4002` | `Heavy` |
| `0x4003` | `Whites` |

### 속성

| ID | 이름 | Define | 방향 | 타입 | 제약 및 적합성 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | server | `array` of `ModeOptionStruct` | 길이 최대 `255`, 최소 길이 `2` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | server | `int8u` | — |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | server | `array` of `enum16` | 길이 최대 `16`, 최소 길이 `1`, optional, `COREMODES` Feature에 mandatory |

전역 속성:

| ID | 값 | 방향 |
|---|---:|---|
| `0xFFFD` | `4` | either |

### 명령

#### `ChangeToMode`

- 방향: `client`
- Command ID: `0x00`
- 응답: `ChangeToModeResponse`
- 설명: This command is used to change device modes.
- 적합성: Mandatory

| Field ID | 이름 | 타입 |
|---:|---|---|
| 0 | `NewMode` | `int8u` |

#### `ChangeToModeResponse`

- 방향: `server`
- Command ID: `0x01`
- `disableDefaultResponse="true"`
- 설명: This command is sent by the device on receipt of the `ChangeToMode` command.
- 적합성: Mandatory

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| 0 | `Status` | `enum8` | — |
| 1 | `StatusText` | `char_string` | 최대 길이 `64`, optional |

#### `ChangeToModeByCoreTag`

- 방향: `client`
- Command ID: `0x02`
- 응답: `ChangeToModeResponse`
- 선택 사항: `optional`
- API maturity: `provisional`
- 설명: This command is used to change the mode of the device to one of the modes with a tag list that includes the given mode tag value.
- `COREMODES` Feature에 대해 mandatory

| Field ID | 이름 | 타입 | API maturity |
|---:|---|---|---|
| 0 | `NewModeTag` | `enum16` | `provisional` |

