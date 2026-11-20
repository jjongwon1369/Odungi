---
entity: Thermostat Mode
ids: ['0x0063']
source_paths: ['data_model/1.7/clusters/Mode_Thermostat.xml', 'src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Thermostat Mode

## 개요

Thermostat Mode는 `Mode Base`에서 파생된 클러스터로, thermostat 장치를 위한 추가 모드 태그와 네임스페이스가 지정된 열거형 값을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0063` |
| 클러스터 이름 | `Thermostat Mode` |
| 스펙 이름 | `Thermostat Mode Cluster` |
| 리비전 | `1` |
| 기반 클러스터 | `Mode Base` |
| 분류 | `hierarchy="derived"`, `role="application"` |
| 범위 | `Endpoint` |
| PICS 코드 | `TSTATM` |
| SDK 도메인 | `HVAC` |

## 스펙

출처: `data_model/1.7/clusters/Mode_Thermostat.xml`

### 리비전 이력

| 리비전 | 요약 |
|---|---|
| `1` | `Initial Release` |

### 기능

| 비트 | 코드 | 이름 | 정의 |
|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성. `disallowConform`으로 허용되지 않음 |
| `1` | `COREMODES` | `CoreModes` | 기능 선언 |

### ModeTag

스펙과 SDK는 같은 이름과 수치의 값을 정의하지만, 일부 값의 16진수 표기가 다르다. 아래에는 각 원문의 표기를 유지했다.

| 이름 | 스펙 값 | SDK 값 |
|---|---|---|
| `Auto` | `0x00` | `0x0000` |
| `Quick` | `0x01` | `0x0001` |
| `Quiet` | `0x02` | `0x0002` |
| `LowNoise` | `0x03` | `0x0003` |
| `LowEnergy` | `0x04` | `0x0004` |
| `Vacation` | `0x05` | `0x0005` |
| `Min` | `0x06` | `0x0006` |
| `Max` | `0x07` | `0x0007` |
| `Night` | `0x08` | `0x0008` |
| `Day` | `0x09` | `0x0009` |
| `Off` | `0x4000` | `0x4000` |
| `Cool` | `0x4001` | `0x4001` |
| `Heat` | `0x4002` | `0x4002` |
| `EmergencyHeat` | `0x4003` | `0x4003` |

### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | `mandatoryConform` | 별도 명시 없음 |
| `1` | `Mode` | `mandatoryConform` | 별도 명시 없음 |
| `2` | `ModeTags` | `mandatoryConform` | `1`~`8` |

### 속성

| ID | 이름 | 스펙 조각의 명시 사항 |
|---|---|---|
| `0x0000` | `SupportedModes` | 속성 선언 |
| `0x0001` | `CurrentMode` | 속성 선언 |
| `0x0002` | `StartUpMode` | 속성 선언 |
| `0x0003` | `OnMode` | `disallowConform`으로 허용되지 않음 |
| `0x0004` | `CoreModeTags` | 속성 선언 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml`

### 생성 정보 및 클러스터 설정

- Alchemy로 생성된 XML이며, 원문에 `DO NOT EDIT`가 명시되어 있다.
- 생성 원본: `src/app_clusters/Mode_Thermostat.adoc`
- 생성 매개변수:

  ```text
  zap attribute=in-progress provisional-policy=loose force connectedhomeip-spec/src/app_clusters/Mode_Thermostat.adoc
  ```

- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

| 항목 | 정의 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 매크로 | `THERMOSTAT_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

### 기능

`CoreModes`는 하나 이상의 핵심 모드 지원을 나타낸다.

| 비트 | 코드 | 이름 | API 성숙도 | 적합성 정의 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | `provisional` | `otherwiseConform` 안에 `provisionalConform`, `optionalConform` |

스펙에서 허용되지 않는 `OnOff` 기능과 `OnMode` 속성은 제공된 SDK 정의에 포함되어 있지 않다.

### 데이터 타입

#### ModeTag

- 타입: `enum16`
- 연결 클러스터: `0x0063`
- 항목과 값은 위의 `ModeTag` 표 참조.

#### ModeOptionStruct

| 필드 ID | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Label` | `char_string` | `length="64"` |
| `1` | `Mode` | `int8u` | 별도 명시 없음 |
| `2` | `ModeTags` | `ModeTagStruct` 배열 | `array="true"`, `minLength="1"`, `length="8"` |

#### ModeTagStruct

| 필드 ID | 이름 | 타입 | 선택 여부 |
|---|---|---|---|
| `0` | `MfgCode` | `vendor_id` | `optional="true"` |
| `1` | `Value` | `enum16` | 선택 표시 없음 |

### 속성

아래 속성은 모두 `side="server"`로 정의된다.

| ID | 이름 | 매크로 | 타입 | 제약 및 설정 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `ModeOptionStruct` 배열 | `minLength="2"`, `length="255"` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | 별도 명시 없음 |
| `0x0002` | `StartUpMode` | `START_UP_MODE` | `int8u` | `isNullable="true"`, `writable="true"`, `optional="true"`, `optionalConform` |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `enum16` 배열 | `minLength="1"`, `length="16"`, `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES`를 조건으로 하는 `mandatoryConform`이 포함된다.

### 명령

| 코드 | 이름 | source | 응답 | 용도 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 장치 모드 변경 |
| `0x01` | `ChangeToModeResponse` | `server` | — | `ChangeToMode` 수신 시 장치가 전송하는 응답 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | 지정된 모드 태그 값을 태그 목록에 포함하는 모드 중 하나로 변경 |

#### ChangeToMode

| 필드 ID | 인자 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

`disableDefaultResponse="true"`로 정의된다.

| 필드 ID | 인자 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 별도 명시 없음 |
| `1` | `StatusText` | `char_string` | `optional="true"`, `length="64"` |

#### ChangeToModeByCoreTag

- `optional="true"`, `apiMaturity="provisional"`로 정의된다.
- `otherwiseConform`에는 `provisionalConform`과 `COREMODES`를 조건으로 하는 `mandatoryConform`이 포함된다.

| 필드 ID | 인자 | 타입 | API 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
- [Water Heater](../device-types/water-heater.md)
