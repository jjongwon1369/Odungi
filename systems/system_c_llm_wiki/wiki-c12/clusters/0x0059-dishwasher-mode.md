---
entity: Dishwasher Mode
ids: ['0x0059']
source_paths: ['data_model/1.7/clusters/Mode_Dishwasher.xml', 'src/app/zap-templates/zcl/data-model/chip/dishwasher-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Dishwasher Mode

## 개요

Dishwasher Mode는 지원되는 옵션 목록에서 기기 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0059` |
| 스펙 이름 | `Dishwasher Mode Cluster` |
| 클러스터 이름 | `Dishwasher Mode` |
| 리비전 | `4` |
| 기반 클러스터 | `Mode Base` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `DISHM` |

## 스펙

출처: `data_model/1.7/clusters/Mode_Dishwasher.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `ChangeToModeResponse` 명령에서 `InvalidInMode` 상태일 때 `StatusText` 제공을 필수로 지정 |
| `3` | `OnOff` 기능을 허용하지 않도록 변경. 이전에는 Device Type 재정의로 처리됨. `StartUpMode`와 `OnMode`도 허용하지 않도록 변경. 이전에는 잠정 상태였음 |
| `4` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성 | 허용하지 않음 |

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
| `0x4001` | `Heavy` |
| `0x4002` | `Light` |

#### `ModeOptionStruct`

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | 별도 명시 없음 |
| `1` | `Mode` | 필수 | 별도 명시 없음 |
| `2` | `ModeTags` | 필수 | `1`~`8` |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 허용하지 않음 |
| `0x0003` | `OnMode` | 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/dishwasher-mode-cluster.xml`

### 정의 및 생성 정보

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| 이름 | `Dishwasher Mode` |
| 코드 | `0x0059` |
| 매크로 정의 | `DISHWASHER_MODE_CLUSTER` |
| client | 활성화, `init="false"`, `tick="false"` |
| server | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | 코드 `0xFFFD`, 값 `4`, `side="either"` |
| 생성 원본 | `src/app_clusters/Mode_Dishwasher.adoc` |
| Git | `0.9-1.7-winter2027` |
| Alchemy | `v1.7.10` |

이 XML은 Alchemy로 생성되었으며 직접 수정하지 않도록 명시되어 있다.

### 기능

| 비트 | 코드 | 이름 | 설명 | 상태 및 적합성 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 core mode 지원 | `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform`, `optionalConform` 명시 |

제공된 스펙 조각에는 `CoreModes`가 없지만, SDK에는 잠정 기능으로 정의되어 있다.

### 데이터 타입

SDK의 `ModeTag`는 `enum16`이며 클러스터 코드 `0x0059`에 연결된다.

| 값 | 이름 | 구분 |
|---|---|---|
| `0x0000` | `Auto` | 기반 값 |
| `0x0001` | `Quick` | 기반 값 |
| `0x0002` | `Quiet` | 기반 값 |
| `0x0003` | `LowNoise` | 기반 값 |
| `0x0004` | `LowEnergy` | 기반 값 |
| `0x0005` | `Vacation` | 기반 값 |
| `0x0006` | `Min` | 기반 값 |
| `0x0007` | `Max` | 기반 값 |
| `0x0008` | `Night` | 기반 값 |
| `0x0009` | `Day` | 기반 값 |
| `0x4000` | `Normal` | 파생 클러스터 전용 값 |
| `0x4001` | `Heavy` | 파생 클러스터 전용 값 |
| `0x4002` | `Light` | 파생 클러스터 전용 값 |

SDK 주석은 기반 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조한다.

### 속성

모든 속성은 `side="server"`로 정의된다.

| 코드 | 이름 | 매크로 정의 | 타입 | 길이 | 상태 및 적합성 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, 항목 `ModeOptionStruct` | 최소 `2`, 최대 `255` | 선택 속성 표시 없음 |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — | 선택 속성 표시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, 항목 `enum16` | 최소 `1`, 최대 `16` | `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 따른 `mandatoryConform`이 명시되어 있다.

스펙에서 허용하지 않는 `StartUpMode`와 `OnMode`는 제공된 SDK 속성 목록에 없다.

### 명령

| 코드 | 이름 | source | 응답 | 상태 및 적합성 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수, `disableDefaultResponse="true"` |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"` |

#### `ChangeToMode`

기기의 모드를 변경하는 명령이다.

| fieldId | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### `ChangeToModeResponse`

기기가 `ChangeToMode` 명령을 수신하면 보내는 응답이다.

| fieldId | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 선택 필드 표시 없음 |
| `1` | `StatusText` | `char_string` | 최대 길이 `64`, `optional="true"` |

SDK에서 `StatusText`는 선택 필드로 표시되지만, 스펙 리비전 이력은 `InvalidInMode` 상태일 때 이를 반드시 제공하도록 명시한다.

#### `ChangeToModeByCoreTag`

지정한 모드 태그 값이 태그 목록에 포함된 모드 중 하나로 기기 모드를 변경한다.

| fieldId | 이름 | 타입 | 상태 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

명령의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 따른 `mandatoryConform`이 명시되어 있다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Dishwasher](../device-types/dishwasher.md)
