---
entity: Refrigerator And Temperature Controlled Cabinet Mode
ids: ['0x0052']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml', 'data_model/1.7/clusters/Mode_Refrigerator.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Refrigerator And Temperature Controlled Cabinet Mode

## 스펙

- **Cluster ID:** `0x0052`
- **이름:** `Refrigerator And Temperature Controlled Cabinet Mode Cluster`
- **Revision:** `4`
- **분류:** `derived`
- **Base cluster:** `Mode Base`
- **Role:** `application`
- **PICS code:** `TCCM`
- **Scope:** `Endpoint`

### Revision history

| Revision | Summary |
|---|---|
| `1` | Initial revision |
| `2` | `ChangeToModeResponse` command: `StatusText` must be provided for `InvalidInMode` status |
| `3` | Set `OnOff` feature, `StartUpMode`, and `OnMode` as disallowed (previously a Device Type override) |
| `4` | Adopt latest version of base cluster |

### Features

| Bit | Code | 이름 | 설명 | 적합성 |
|---:|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | Dependency with the `OnOff` cluster | Disallowed |

### 데이터 타입

#### `ModeTag`

| Value | Name |
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
| `0x4000` | `RapidCool` |
| `0x4001` | `RapidFreeze` |

#### `ModeOptionStruct`

| Field ID | 이름 | 적합성 | 제약 |
|---:|---|---|---|
| `0` | `Label` | Mandatory | — |
| `1` | `Mode` | Mandatory | — |
| `2` | `ModeTags` | Mandatory | `1`부터 `8`까지 |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | Mandatory |
| `0x0001` | `CurrentMode` | Mandatory |
| `0x0002` | `StartUpMode` | Disallowed |
| `0x0003` | `OnMode` | Disallowed |

## SDK 정의

- **소스 파일:** `src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml`
- **Domain:** `Appliances`
- **Cluster 이름:** `Refrigerator And Temperature Controlled Cabinet Mode`
- **Cluster code:** `0x0052`
- **Define:** `REFRIGERATOR_AND_TEMPERATURE_CONTROLLED_CABINET_MODE_CLUSTER`
- **Client:** 지원
- **Server:** 지원
- **설명:** Attributes and commands for selecting a mode from a list of supported options.

### Features

| Bit | Code | 이름 | 설명 | API maturity |
|---:|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | One or more core modes are supported | `provisional` |

`COREMODES` feature에는 `provisionalConform` 및 `optionalConform`이 정의되어 있습니다.

### 전역 속성

| Side | Code | Value |
|---|---|---:|
| either | `0xFFFD` | `4` |

### 데이터 타입

#### `ModeTag`

`enum16` 타입입니다.

| Value | Name |
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
| `0x4000` | `RapidCool` |
| `0x4001` | `RapidFreeze` |

### 속성

| Side | Code | 이름 | 타입 | 세부 사항 |
|---|---|---|---|---|
| server | `0x0000` | `SupportedModes` | `array` | `ModeOptionStruct` 배열, 길이 `255`, 최소 길이 `2` |
| server | `0x0001` | `CurrentMode` | `int8u` | — |
| server | `0x0004` | `CoreModeTags` | `array` | `enum16` 배열, 길이 `16`, 최소 길이 `1`, optional, `COREMODES` feature 필요 |

`CoreModeTags`는 `provisional` API maturity로 정의되어 있으며, `COREMODES` feature에 대해 `mandatoryConform`이 적용됩니다.

### 명령

#### `ChangeToMode`

- **Command code:** `0x00`
- **Source:** client
- **Response:** `ChangeToModeResponse`
- **적합성:** Mandatory
- **설명:** This command is used to change device modes.

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `NewMode` | `int8u` |

#### `ChangeToModeResponse`

- **Command code:** `0x01`
- **Source:** server
- **Default response:** 비활성화
- **적합성:** Mandatory
- **설명:** This command is sent by the device on receipt of the `ChangeToMode` command.

| Field ID | 이름 | 타입 | 세부 사항 |
|---:|---|---|---|
| `0` | `Status` | `enum8` | — |
| `1` | `StatusText` | `char_string` | optional, 길이 `64` |

#### `ChangeToModeByCoreTag`

- **Command code:** `0x02`
- **Source:** client
- **Response:** `ChangeToModeResponse`
- **적합성:** optional
- **API maturity:** `provisional`
- **설명:** This command is used to change the mode of the device to one of the modes with a tag list that includes the given mode tag value.

| Field ID | 이름 | 타입 | API maturity |
|---:|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

`ChangeToModeByCoreTag`는 `COREMODES` feature에 대해 `mandatoryConform`이 적용됩니다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
