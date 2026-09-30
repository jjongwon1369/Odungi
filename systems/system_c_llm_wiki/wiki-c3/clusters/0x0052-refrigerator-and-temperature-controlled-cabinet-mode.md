---
entity: Refrigerator And Temperature Controlled Cabinet Mode
ids: ['0x0052']
source_paths: ['data_model/1.7/clusters/Mode_Refrigerator.xml', 'src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Refrigerator And Temperature Controlled Cabinet Mode

## 개요

지원되는 옵션 목록에서 모드를 선택하기 위한 속성과 명령을 정의하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Refrigerator And Temperature Controlled Cabinet Mode` |
| 클러스터 ID | `0x0052` |
| 리비전 | `4` |
| 기반 클러스터 | `Mode Base` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `TCCM` |

## 스펙

출처: `data_model/1.7/clusters/Mode_Refrigerator.xml`

스펙의 클러스터 정의 이름은 `Refrigerator And Temperature Controlled Cabinet Mode Cluster`이다.

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `ChangeToModeResponse`에서 상태가 `InvalidInMode`이면 `StatusText`를 반드시 제공하도록 변경 |
| `3` | 기존 Device Type 재정의 대신 클러스터에서 `OnOff` 기능, `StartUpMode`, `OnMode`를 허용하지 않도록 설정 |
| `4` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성 | 허용하지 않음 (`disallowConform`) |

### 데이터 타입

#### ModeTag

| 이름 | 값 |
|---|---|
| `Auto` | `0x00` |
| `Quick` | `0x01` |
| `Quiet` | `0x02` |
| `LowNoise` | `0x03` |
| `LowEnergy` | `0x04` |
| `Vacation` | `0x05` |
| `Min` | `0x06` |
| `Max` | `0x07` |
| `Night` | `0x08` |
| `Day` | `0x09` |
| `RapidCool` | `0x4000` |
| `RapidFreeze` | `0x4001` |

#### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | 별도 명시 없음 |
| `1` | `Mode` | 필수 | 별도 명시 없음 |
| `2` | `ModeTags` | 필수 | `1`~`8` |

제공된 스펙 조각에는 각 필드의 타입이 명시되어 있지 않다.

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 허용하지 않음 |
| `0x0003` | `OnMode` | 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml`

### 생성 및 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 생성 도구 | Alchemy `v1.7.10` |
| 생성 원본 | `src/app_clusters/Mode_Refrigerator.adoc` |
| Git | `0.9-1.7-winter2027` |
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| 클러스터 코드 | `0x0052` |
| define | `REFRIGERATOR_AND_TEMPERATURE_CONTROLLED_CABINET_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | 코드 `0xFFFD`, 값 `4`, `side="either"` |

이 XML은 Alchemy로 생성되었으며 직접 수정하지 않도록 표시되어 있다.

### 기능

| 비트 | 코드 | 이름 | 설명 | 성숙도 및 적합성 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 core mode 지원 | `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform`과 `optionalConform` 명시 |

### 데이터 타입

SDK의 `ModeTag`는 클러스터 `0x0052`에 연결된 `enum16`이다.

| 이름 | SDK 값 | 구분 |
|---|---|---|
| `Auto` | `0x0000` | 기반 값 |
| `Quick` | `0x0001` | 기반 값 |
| `Quiet` | `0x0002` | 기반 값 |
| `LowNoise` | `0x0003` | 기반 값 |
| `LowEnergy` | `0x0004` | 기반 값 |
| `Vacation` | `0x0005` | 기반 값 |
| `Min` | `0x0006` | 기반 값 |
| `Max` | `0x0007` | 기반 값 |
| `Night` | `0x0008` | 기반 값 |
| `Day` | `0x0009` | 기반 값 |
| `RapidCool` | `0x4000` | 파생 클러스터 전용 값 |
| `RapidFreeze` | `0x4001` | 파생 클러스터 전용 값 |

SDK 주석은 기반 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 지목한다. 코드 생성에서 중복 없이 자동 포함할 수 있을 때까지 해당 값을 중복 정의한다고 설명한다.

### 속성

모든 속성은 `side="server"`이다.

| 코드 | 이름 | define | 타입 | 길이 제약 | 선택 여부 및 성숙도 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, `entryType="ModeOptionStruct"` | `minLength="2"`, `length="255"` | 선택 표시 없음 |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — | 선택 표시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, `entryType="enum16"` | `minLength="1"`, `length="16"` | `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 대한 `mandatoryConform`이 명시되어 있다.

### 명령

| 코드 | 이름 | source | 응답 | 적합성 및 성숙도 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform` 및 `COREMODES` 기능에 대한 `mandatoryConform` 명시 |

#### ChangeToMode

장치의 모드를 변경한다.

| fieldId | 인자 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신했을 때 전송하는 응답이다. `disableDefaultResponse="true"`로 정의되어 있다.

| fieldId | 인자 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 선택 표시 없음 |
| `1` | `StatusText` | `char_string` | `length="64"`, `optional="true"` |

스펙 리비전 이력에는 `InvalidInMode` 상태일 때 `StatusText`를 반드시 제공해야 한다고 명시되어 있다.

#### ChangeToModeByCoreTag

태그 목록에 지정된 모드 태그 값이 포함된 모드 중 하나로 장치 모드를 변경한다.

| fieldId | 인자 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

### 제공된 스펙과 SDK의 표현 차이

- 스펙은 `OnOff`, `StartUpMode`, `OnMode`를 명시적으로 허용하지 않는다. SDK 조각에는 이 항목들이 포함되어 있지 않다.
- SDK에는 제공된 스펙 조각에 없는 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`가 `provisional`로 정의되어 있다.
- SDK는 `SupportedModes`와 `CurrentMode`의 타입 및 명령 인자를 구체적으로 정의한다. 제공된 스펙 조각에는 해당 세부 정의가 없다.
- `ModeTag`의 기반 값은 스펙에서 `0x00`~`0x09`, SDK에서 `0x0000`~`0x0009`로 표기되어 있으며 수치상 동일하다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
