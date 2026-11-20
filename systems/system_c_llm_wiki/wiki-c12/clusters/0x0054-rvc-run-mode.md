---
entity: RVC Run Mode
ids: ['0x0054']
source_paths: ['data_model/1.7/clusters/Mode_RVCRun.xml', 'src/app/zap-templates/zcl/data-model/chip/rvc-run-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# RVC Run Mode

## 개요

`RVC Run Mode`는 지원되는 모드 목록에서 장치 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0054` |
| 스펙 이름 | `RVC Run Mode Cluster` |
| 클러스터 이름 | `RVC Run Mode` |
| revision | `5` |
| 기반 클러스터 | `Mode Base` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `RVCRUNM` |
| SDK 도메인 | `Robots` |

## 스펙

출처: `data_model/1.7/clusters/Mode_RVCRun.xml`

### revision 이력

| revision | 변경 내용 |
|---|---|
| `1` | 최초 revision |
| `2` | non-Idle 모드 사이의 전환 제약 추가. `ChangeToModeResponse`에서 `InvalidInMode` 상태일 때 `StatusText` 제공 의무화. `OnMode`와 관련 feature map 비트 폐기 예정 처리. `Mapping` 모드 태그 추가 |
| `3` | `RVC Run Mode`가 non-Idle 모드일 때 청소 모드를 변경하는 제약 제거. 해당 변경을 지원하지 않는 장치의 `InvalidInMode` 응답은 계속 허용 |
| `4` | `DirectModeChange`의 provisional 상태 해제 |
| `5` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `disallowConform` | `OnOff` 클러스터와의 의존성. 이 스펙에서는 허용하지 않음 |
| `20` | `DIRECTMODECH` | `DirectModeChange` | `optionalConform` | non-Idle 상태에서 실행 모드 변경 지원 |

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
| `0x4000` | `Idle` |
| `0x4001` | `Cleaning` |
| `0x4002` | `Mapping` |

#### `StatusCodeEnum`

모든 항목은 `mandatoryConform`으로 선언된다.

| 값 | 이름 |
|---|---|
| `0x41` | `Stuck` |
| `0x42` | `DustBinMissing` |
| `0x43` | `DustBinFull` |
| `0x44` | `WaterTankEmpty` |
| `0x45` | `WaterTankMissing` |
| `0x46` | `WaterTankLidOpen` |
| `0x47` | `MopCleaningPadMissing` |
| `0x48` | `BatteryLow` |

#### `ModeOptionStruct`

| 필드 ID | 이름 | 적합성 | 명시된 제약 |
|---|---|---|---|
| `0` | `Label` | `mandatoryConform` | 없음 |
| `1` | `Mode` | `mandatoryConform` | 없음 |
| `2` | `ModeTags` | `mandatoryConform` | `1`~`8` |

제공된 스펙 조각에는 각 필드의 타입이 명시되어 있지 않다.

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 이 조각에 별도 명시 없음 |
| `0x0001` | `CurrentMode` | 이 조각에 별도 명시 없음 |
| `0x0002` | `StartUpMode` | `disallowConform` |
| `0x0003` | `OnMode` | `disallowConform` |

제공된 스펙 조각에는 명령 정의가 별도로 포함되어 있지 않다. `ChangeToModeResponse`, `StatusText`, `InvalidInMode` 관련 변경 사항은 revision 이력에 기재되어 있다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/rvc-run-mode-cluster.xml`

### 생성 정보와 클러스터 설정

이 XML은 Alchemy가 생성한 파일이며, 직접 편집하지 않도록 표시되어 있다.

| 항목 | 값 |
|---|---|
| 생성 원본 | `src/app_clusters/Mode_RVCRun.adoc` |
| Git | `0.9-1.7-winter2027` |
| Alchemy | `v1.7.10` |
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Robots` |
| 이름 | `RVC Run Mode` |
| 코드 | `0x0054` |
| define | `RVC_RUN_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `0xFFFD`, `side="either"`, `value="5"` |

### 기능

| 비트 | 코드 | 이름 | 적합성 및 성숙도 | 설명 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform`, `optionalConform` 선언 | 하나 이상의 core mode 지원 |
| `20` | `DIRECTMODECH` | `DirectModeChange` | `optionalConform` | non-Idle 상태에서 실행 모드 변경 지원 |

### 열거형

#### `StatusCode`

SDK는 스펙의 `StatusCodeEnum`과 다른 이름인 `StatusCode`를 사용한다. 타입은 `enum8`이며, 클러스터 코드 `0x0054`에 연결된다.

| 값 | 이름 |
|---|---|
| `0x41` | `Stuck` |
| `0x42` | `DustBinMissing` |
| `0x43` | `DustBinFull` |
| `0x44` | `WaterTankEmpty` |
| `0x45` | `WaterTankMissing` |
| `0x46` | `WaterTankLidOpen` |
| `0x47` | `MopCleaningPadMissing` |
| `0x48` | `BatteryLow` |

#### `ModeTag`

타입은 `enum16`이며, 클러스터 코드 `0x0054`에 연결된다. 아래 값은 SDK 원문의 표기를 유지한다.

| 구분 | 값 | 이름 |
|---|---|---|
| 기본 값 | `0x0000` | `Auto` |
| 기본 값 | `0x0001` | `Quick` |
| 기본 값 | `0x0002` | `Quiet` |
| 기본 값 | `0x0003` | `LowNoise` |
| 기본 값 | `0x0004` | `LowEnergy` |
| 기본 값 | `0x0005` | `Vacation` |
| 기본 값 | `0x0006` | `Min` |
| 기본 값 | `0x0007` | `Max` |
| 기본 값 | `0x0008` | `Night` |
| 기본 값 | `0x0009` | `Day` |
| 파생 클러스터 전용 값 | `0x4000` | `Idle` |
| 파생 클러스터 전용 값 | `0x4001` | `Cleaning` |
| 파생 클러스터 전용 값 | `0x4002` | `Mapping` |

SDK 주석은 기본 값의 namespace 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 지목한다. 코드 생성에서 중복 없이 자동 포함할 수 있을 때까지 기본 값을 중복 선언한다고 설명한다.

### 속성

모든 속성의 `side`는 `server`이다.

| 코드 | 이름 | define | 타입 | 길이 | 추가 조건 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, `entryType="ModeOptionStruct"` | `minLength="2"`, `length="255"` | — |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — | — |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, `entryType="enum16"` | `minLength="1"`, `length="16"` | `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 대한 `mandatoryConform`이 선언되어 있다.

`OnMode`는 코드 `0x0003`의 폐기 예정 속성이라는 주석만 있으며, 속성 정의는 포함되어 있지 않다. `StartUpMode` 정의도 제공된 SDK 조각에는 없다.

### 명령

| 코드 | 이름 | source | 응답 | 적합성 및 설정 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | `mandatoryConform` |
| `0x01` | `ChangeToModeResponse` | `server` | — | `mandatoryConform`, `disableDefaultResponse="true"` |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"` |

#### `ChangeToMode`

장치 모드를 변경한다.

| fieldId | 인자 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### `ChangeToModeResponse`

장치가 `ChangeToMode`를 수신하면 전송하는 응답이다.

| fieldId | 인자 | 타입 | 추가 조건 |
|---|---|---|---|
| `0` | `Status` | `enum8` | — |
| `1` | `StatusText` | `char_string` | `optional="true"`, `length="64"` |

SDK 인자 정의에서 `StatusText`는 선택 사항이다. 다만 스펙 revision 이력에는 `InvalidInMode` 상태일 때 반드시 제공해야 한다고 명시되어 있다.

#### `ChangeToModeByCoreTag`

태그 목록에 지정한 모드 태그 값을 포함하는 모드 중 하나로 장치 모드를 변경한다.

| fieldId | 인자 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

`otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 대한 `mandatoryConform`이 선언되어 있다.

### 스펙 조각과 SDK 조각의 차이

- 스펙에는 `OnOff` / `DEPONOFF`가 허용되지 않는 기능으로 선언되어 있으며, SDK 기능 목록에는 포함되어 있지 않다.
- SDK에는 스펙 조각에 없는 provisional 요소인 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`가 포함되어 있다.
- 상태 코드 열거형 이름은 스펙에서 `StatusCodeEnum`, SDK에서 `StatusCode`이다. 제시된 항목 이름과 값은 동일하다.
- 기본 `ModeTag` 값은 스펙에서 `0x00`~`0x09`, SDK에서 `0x0000`~`0x0009`로 표기된다.
- 스펙은 `StartUpMode`와 `OnMode`를 `disallowConform`으로 선언한다. SDK는 `StartUpMode`를 정의하지 않으며, `OnMode`는 폐기 예정이라는 주석으로만 남긴다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
