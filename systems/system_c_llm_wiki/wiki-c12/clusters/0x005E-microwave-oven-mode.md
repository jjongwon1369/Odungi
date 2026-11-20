---
entity: Microwave Oven Mode
ids: ['0x005E']
source_paths: ['data_model/1.7/clusters/Mode_MicrowaveOven.xml', 'src/app/zap-templates/zcl/data-model/chip/microwave-oven-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Microwave Oven Mode

## 개요

`Microwave Oven Mode`는 지원되는 옵션 목록에서 모드를 선택하기 위한 클러스터이다. `Mode Base`에서 파생되며, 클러스터 ID는 `0x005E`, 리비전은 `3`이다.

제공된 스펙에서는 `ChangeToMode`와 `ChangeToModeResponse`를 허용하지 않는다. SDK 정의에는 스펙 조각에 없는 provisional 기능 `CoreModes`와 속성 `CoreModeTags`가 포함되어 있다.

## 스펙

출처: `data_model/1.7/clusters/Mode_MicrowaveOven.xml`

### 기본 정보

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Microwave Oven Mode Cluster` |
| 클러스터 ID 이름 | `Microwave Oven Mode` |
| 클러스터 ID | `0x005E` |
| 리비전 | `3` |
| 계층 | `derived` |
| 기반 클러스터 | `Mode Base` |
| 역할 | `application` |
| PICS 코드 | `MWOM` |
| 범위 | `Endpoint` |

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `OnOff` 기능을 허용하지 않도록 변경 |
| `3` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성 | `disallowConform`: 허용하지 않음 |

### 데이터 타입

`ModeTag` 열거형은 다음 값을 정의한다. SDK의 값 표기도 함께 표시한다.

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
| `Normal` | `0x4000` | `0x4000` |
| `Defrost` | `0x4001` | `0x4001` |

### 속성

| ID | 이름 | 제공된 스펙의 적합성 표기 |
|---|---|---|
| `0x0000` | `SupportedModes` | 별도 표기 없음 |
| `0x0001` | `CurrentMode` | 별도 표기 없음 |
| `0x0002` | `StartUpMode` | `disallowConform`: 허용하지 않음 |
| `0x0003` | `OnMode` | `disallowConform`: 허용하지 않음 |

### 명령

| ID | 이름 | 적합성 |
|---|---|---|
| `0x00` | `ChangeToMode` | `disallowConform`: 허용하지 않음 |
| `0x01` | `ChangeToModeResponse` | `disallowConform`: 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/microwave-oven-mode-cluster.xml`

### 기본 설정

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| 이름 | `Microwave Oven Mode` |
| 코드 | `0x005E` |
| define | `MICROWAVE_OVEN_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | 코드 `0xFFFD`, 값 `3`, `side="either"` |

### 데이터 타입

`ModeTag`는 클러스터 `0x005E`에 연결된 `enum16`이다.

- `Auto`부터 `Day`까지는 기반 값이다.
- `Normal`과 `Defrost`는 파생 클러스터 전용 값이다.
- SDK 주석은 기반 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조한다.

### 기능

| 비트 | 코드 | 이름 | 설명 | API 성숙도 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 코어 모드 지원 | `provisional` |

`CoreModes`의 적합성은 `otherwiseConform` 아래에 `provisionalConform`과 `optionalConform`으로 정의되어 있다.

### 속성

모든 속성은 `side="server"`로 정의된다.

| 코드 | 이름 | define | 타입 | 항목 타입 | 길이 제약 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array` | `ModeOptionStruct` | `minLength="2"`, `length="255"` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — | — |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array` | `enum16` | `minLength="1"`, `length="16"` |

`CoreModeTags`에는 다음 조건이 지정되어 있다.

- `optional="true"`
- `apiMaturity="provisional"`
- `otherwiseConform` 아래에 `provisionalConform` 및 `COREMODES`를 조건으로 하는 `mandatoryConform`

제공된 SDK XML에는 `StartUpMode`, `OnMode`, `ChangeToMode`, `ChangeToModeResponse` 정의가 없다.

### 생성 정보

이 XML은 Alchemy가 생성한 파일이며, 주석에 직접 수정하지 않도록 명시되어 있다.

| 항목 | 값 |
|---|---|
| 생성 원본 | `src/app_clusters/Mode_MicrowaveOven.adoc` |
| Git | `0.9-1.7-winter2027` |
| Alchemy | `v1.7.10` |

### 스펙과 SDK의 차이

- 스펙은 비트 `0`의 `OnOff` 기능을 명시적으로 금지한다. SDK XML에는 해당 기능이 선언되어 있지 않다.
- SDK는 비트 `1`의 `CoreModes` 기능과 `0x0004`의 `CoreModeTags` 속성을 provisional로 정의한다. 제공된 스펙 조각에는 이 정의가 없다.
- 두 입력의 클러스터 ID는 `0x005E`이고, 리비전 값은 `3`이다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Microwave Oven](../device-types/microwave-oven.md)
