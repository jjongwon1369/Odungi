---
entity: Refrigerator And Temperature Controlled Cabinet Mode
ids: ['0x0052']
source_paths: ['data_model/1.7/clusters/Mode_Refrigerator.xml', 'src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
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

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `ChangeToModeResponse` 명령에서 `InvalidInMode` 상태일 때 `StatusText` 제공 필수 |
| `3` | `OnOff` 기능, `StartUpMode`, `OnMode`를 허용하지 않도록 설정. 이전에는 Device Type에서 재정의 |
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
| `0x4000` | `RapidCool` |
| `0x4001` | `RapidFreeze` |

#### `ModeOptionStruct`

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | 별도 명시 없음 |
| `1` | `Mode` | 필수 | 별도 명시 없음 |
| `2` | `ModeTags` | 필수 | 항목 수 `1`~`8` |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 허용하지 않음 |
| `0x0003` | `OnMode` | 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml`

### 생성 정보 및 클러스터 설정

이 파일은 Alchemy로 생성되었으며, 직접 수정하지 않도록 명시되어 있다.

| 항목 | 값 |
|---|---|
| 생성 원본 | `src/app_clusters/Mode_Refrigerator.adoc` |
| Git | `0.9-1.7-winter2027` |
| Alchemy | `v1.7.10` |
| 설정 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| 클러스터 코드 | `0x0052` |
| 매크로 | `REFRIGERATOR_AND_TEMPERATURE_CONTROLLED_CABINET_MODE_CLUSTER` |
| client / server | 모두 `true`, 각각 `init="false"`, `tick="false"` |
| 전역 속성 | `0xFFFD`, `side="either"`, 값 `4` |

### 데이터 타입

`ModeTag`는 `enum16`으로 정의된다.

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
| `0x4000` | `RapidCool` | 파생 클러스터 전용 값 |
| `0x4001` | `RapidFreeze` | 파생 클러스터 전용 값 |

SDK 주석은 기반 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 가리킨다. 코드 생성에서 중복 없이 자동 포함할 수 있을 때까지 이 기준을 사용한다고 명시한다.

### 기능

| 비트 | 코드 | 이름 | 설명 | 성숙도 및 적합성 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 코어 모드 지원 | `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform` 및 `optionalConform` 명시 |

### 속성

모든 속성은 `side="server"`로 정의된다.

| 코드 | 이름 | 매크로 | 타입 | 길이 및 적합성 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, 항목 `ModeOptionStruct` | 최소 `2`, 최대 `255` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | 별도 제약 명시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, 항목 `enum16` | 최소 `1`, 최대 `16`; `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 대한 `mandatoryConform`이 명시되어 있다.

### 명령

| 코드 | 이름 | source | 응답 | 적합성 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수, `disableDefaultResponse="true"` |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"` |

#### `ChangeToMode`

장치 모드를 변경하는 명령이다.

| fieldId | 인자 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### `ChangeToModeResponse`

장치가 `ChangeToMode`를 수신했을 때 전송하는 응답이다.

| fieldId | 인자 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 별도 제약 명시 없음 |
| `1` | `StatusText` | `char_string` | 최대 길이 `64`, `optional="true"` |

스펙 리비전 이력에는 `InvalidInMode` 상태에서 `StatusText`를 반드시 제공해야 한다고 명시되어 있다.

#### `ChangeToModeByCoreTag`

태그 목록에 지정된 모드 태그 값이 포함된 모드 중 하나로 장치 모드를 변경한다.

| fieldId | 인자 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

`otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 대한 `mandatoryConform`이 명시되어 있다.

### 제공된 스펙과 SDK의 정의 범위 차이

- 스펙은 `OnOff`, `StartUpMode`, `OnMode`를 명시적으로 허용하지 않는다. 제공된 SDK XML에는 이 항목들이 선언되어 있지 않다.
- SDK XML에는 제공된 스펙 XML에 없는 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`가 `provisional`로 정의되어 있다.
- SDK XML은 `ChangeToMode`와 `ChangeToModeResponse`의 인자 및 타입을 정의한다. 제공된 스펙 XML에는 별도의 명령 정의가 없으며, 리비전 이력에서 `ChangeToModeResponse` 관련 변경 사항을 명시한다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
