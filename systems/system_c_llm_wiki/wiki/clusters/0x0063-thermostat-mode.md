---
entity: Thermostat Mode
ids: ['0x0063']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml', 'src/app/clusters/mode-base-server/README.md', 'data_model/1.7/clusters/Mode_Thermostat.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

# Thermostat Mode

## 스펙

- 클러스터: `Thermostat Mode Cluster`
- 클러스터 ID: `0x0063`
- 클러스터 이름: `Thermostat Mode`
- Revision: `1`
- Classification:
  - hierarchy: `derived`
  - baseCluster: `Mode Base`
  - role: `application`
  - picsCode: `TSTATM`
  - scope: `Endpoint`

### 기능

| Bit | Code | Name | Summary | 적합성 |
|---:|---|---|---|---|
| 0 | `DEPONOFF` | `OnOff` | Dependency with the OnOff cluster | disallow |
| 1 | `COREMODES` | `CoreModes` | — | — |

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
| `0x4000` | `Off` |
| `0x4001` | `Cool` |
| `0x4002` | `Heat` |
| `0x4003` | `EmergencyHeat` |

#### `ModeOptionStruct`

| Field ID | 이름 | 적합성 | 제약 |
|---:|---|---|---|
| `0` | `Label` | mandatory | — |
| `1` | `Mode` | mandatory | — |
| `2` | `ModeTags` | mandatory | `1`부터 `8` 사이 |

### 속성

| ID | 이름 | 비고 |
|---|---|---|
| `0x0000` | `SupportedModes` | — |
| `0x0001` | `CurrentMode` | — |
| `0x0002` | `StartUpMode` | — |
| `0x0003` | `OnMode` | disallow |
| `0x0004` | `CoreModeTags` | — |

## SDK 정의

정의 파일:

`src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml`

### 클러스터

- Domain: `HVAC`
- Name: `Thermostat Mode`
- Code: `0x0063`
- Define: `THERMOSTAT_MODE_CLUSTER`
- 설명: `Mode Base` 클러스터에서 파생되며, thermostat devices를 위한 추가 mode tags와 namespaced enumerated values를 정의합니다.
- Client: 지원
- Server: 지원
- Global attribute:
  - Code: `0xFFFD`
  - Side: `either`
  - Value: `1`

### 기능

| Bit | Code | Name | Summary | API maturity |
|---:|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | One or more core modes are supported | `provisional` |

### 데이터 타입

#### `ModeTag`

`enum16` 타입이며 클러스터 코드는 `0x0063`입니다.

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
| `0x4000` | `Off` |
| `0x4001` | `Cool` |
| `0x4002` | `Heat` |
| `0x4003` | `EmergencyHeat` |

#### `ModeOptionStruct`

| Field ID | 이름 | 타입 | 제약 |
|---:|---|---|---|
| `0` | `Label` | `char_string` | length `64` |
| `1` | `Mode` | `int8u` | — |
| `2` | `ModeTags` | `ModeTagStruct` 배열 | length `8`, minLength `1` |

#### `ModeTagStruct`

| Field ID | 이름 | 타입 | 비고 |
|---:|---|---|---|
| `0` | `MfgCode` | `vendor_id` | optional |
| `1` | `Value` | `enum16` | — |

### 속성

| Code | 이름 | Define | 타입 | 비고 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `ModeOptionStruct` 배열 | length `255`, minLength `2`, server |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | server |
| `0x0002` | `StartUpMode` | `START_UP_MODE` | `int8u` | nullable, writable, optional, server |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `enum16` 배열 | length `16`, minLength `1`, optional, provisional, server |

`CoreModeTags`는 `COREMODES` 기능이 사용될 때 mandatory conform입니다.

### 명령

#### `ChangeToMode`

- Code: `0x00`
- Source: `client`
- Response: `ChangeToModeResponse`
- 설명: device modes를 변경하는 데 사용됩니다.

인자:

| Field ID | 이름 | 타입 |
|---:|---|---|
| `0` | `NewMode` | `int8u` |

#### `ChangeToModeResponse`

- Code: `0x01`
- Source: `server`
- Default response: disabled
- 설명: `ChangeToMode` 명령을 수신한 device가 전송합니다.

인자:

| Field ID | 이름 | 타입 | 비고 |
|---:|---|---|---|
| `0` | `Status` | `enum8` | — |
| `1` | `StatusText` | `char_string` | optional, length `64` |

#### `ChangeToModeByCoreTag`

- Code: `0x02`
- Source: `client`
- Response: `ChangeToModeResponse`
- Optional: `true`
- API maturity: `provisional`
- 설명: 주어진 mode tag value를 포함하는 tag list를 가진 mode 중 하나로 device의 mode를 변경하는 데 사용됩니다.
- `COREMODES` 기능이 사용될 때 mandatory conform입니다.

인자:

| Field ID | 이름 | 타입 | API maturity |
|---:|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

## 구현

`Mode Base`는 pseudo cluster이며 cluster ID가 없습니다. 다른 클러스터가 파생되는 용도로만 존재합니다.

### `Mode Base` 파생 클러스터 사용

1. `ModeBase::Delegate` 클래스를 상속하는 클래스를 생성합니다.
2. 다음 메서드를 구현합니다.
   - `GetModeLabelByIndex`
   - `GetModeValueByIndex`
   - `GetModeTagsByIndex`
   - `HandleChangeToMode`
3. 필요한 경우 `Init` 함수를 구현합니다.
4. 일부 translation unit(`.c` 또는 `.cpp` 파일)에서 `ModeBase::Instance` 상속 클래스를 인스턴스화합니다.
5. root `Server::Init()` 이후 인스턴스의 `.Init()` 함수를 호출합니다.
6. 또는 `emberAf<ClusterName>ClusterInitCallback` 함수에서 마지막 두 단계를 수행할 수 있습니다.
7. `chip_device_project_config_include` 파일에 다음을 추가합니다.

```c
#define MATTER_DM_PLUGIN_MODE_BASE
```

예제에서는 이 파일이 `CHIPProjectAppConfig.h`입니다.

> Note: 이 클러스터의 Zap accessor functions는 존재하지 않습니다. 속성에 접근할 때 인스턴스의 `Update...` 및 `Get...` functions를 사용합니다.

### 새로운 파생 클러스터 추가

1. 스펙을 `src/app/zap-templates/zcl/data-model/chip`의 XML로 변환합니다.
2. Zap code를 재생성합니다.
3. `all-clusters-app` 예제에 새 클러스터를 추가합니다.

## 관련 문서

- `src/app/clusters/mode-base-server/README.md`
- `src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml`
- `data_model/1.7/clusters/Mode_Thermostat.xml`
- `mode-base-server.h`
- `examples/all-clusters-app/all-clusters-common`
- `CHIPProjectAppConfig.h`

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
