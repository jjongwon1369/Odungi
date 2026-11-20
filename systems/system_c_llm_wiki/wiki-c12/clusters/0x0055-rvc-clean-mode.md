---
entity: RVC Clean Mode
ids: ['0x0055']
source_paths: ['data_model/1.7/clusters/Mode_RVCClean.xml', 'src/app/zap-templates/zcl/data-model/chip/rvc-clean-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# RVC Clean Mode

## 개요

RVC Clean Mode는 지원되는 옵션 목록에서 모드를 선택하기 위한 속성과 명령을 제공한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0055` |
| 스펙 이름 | `RVC Clean Mode Cluster` |
| 클러스터 이름 | `RVC Clean Mode` |
| 리비전 | `6` |
| 기반 클러스터 | `Mode Base` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `RVCCLEANM` |
| SDK 도메인 | `Robots` |

## 스펙

출처: `data_model/1.7/clusters/Mode_RVCClean.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `RVC Run Mode` 클러스터가 non-Idle 모드일 때 청소 모드 변경 제약 추가. `ChangeToModeResponse`의 `InvalidInMode` 상태에서 `StatusText` 제공 필수화. `OnMode` 속성과 관련 feature map 비트 사용 중단 |
| `3` | non-Idle 모드에서 청소 모드 변경 제약 제거. 해당 변경을 지원하지 않는 장치에는 `InvalidInMode` 응답을 계속 허용 |
| `4` | `Vacuum then Mop` 청소 모드 추가 |
| `5` | `DirectModeChange`의 provisional 상태 해제 |
| `6` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 적합성 | 설명 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `disallowConform` | `OnOff` 클러스터 의존성 |
| `20` | `DIRECTMODECH` | `DirectModeChange` | `optionalConform` | non-Idle 상태에서 청소 모드 변경 지원 |

### 데이터 타입

#### ModeTag

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
| `0x4000` | `DeepClean` |
| `0x4001` | `Vacuum` |
| `0x4002` | `Mop` |
| `0x4003` | `Vacuum then Mop` |

#### StatusCodeEnum

| 값 | 이름 | 적합성 |
|---|---|---|
| `0x40` | `CleaningInProgress` | `mandatoryConform` |

#### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | `mandatoryConform` | 별도 명시 없음 |
| `1` | `Mode` | `mandatoryConform` | 별도 명시 없음 |
| `2` | `ModeTags` | `mandatoryConform` | 항목 수 `1`–`8` |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 이 파일에서 별도 명시 없음 |
| `0x0001` | `CurrentMode` | 이 파일에서 별도 명시 없음 |
| `0x0002` | `StartUpMode` | `disallowConform` |
| `0x0003` | `OnMode` | `disallowConform` |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/rvc-clean-mode-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| 이름 | `RVC Clean Mode` |
| 코드 | `0x0055` |
| define | `RVC_CLEAN_MODE_CLUSTER` |
| 클라이언트 | 활성화, `init="false"`, `tick="false"` |
| 서버 | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | `0xFFFD`, 값 `6`, `side="either"` |

이 파일은 Alchemy로 생성되었으며, 원문에 `DO NOT EDIT`가 명시되어 있다.

- 생성 원본: `src/app_clusters/Mode_RVCClean.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

### 기능

| 비트 | 코드 | 이름 | 적합성 및 성숙도 | 설명 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform`, `optionalConform` 명시 | 하나 이상의 core mode 지원 |
| `20` | `DIRECTMODECH` | `DirectModeChange` | `optionalConform` | non-Idle 상태에서 청소 모드 변경 지원 |

### 열거형

#### StatusCode

타입: `enum8`

| 값 | 이름 |
|---|---|
| `0x40` | `CleaningInProgress` |

스펙의 열거형 이름은 `StatusCodeEnum`이며, SDK 정의에서는 `StatusCode`를 사용한다.

#### ModeTag

타입: `enum16`

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
| `0x4000` | `DeepClean` |
| `0x4001` | `Vacuum` |
| `0x4002` | `Mop` |
| `0x4003` | `VacuumThenMop` |

- 기본 값의 네임스페이스 기준 정의는 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`로 안내되어 있다.
- `0x4003`의 이름은 스펙에서 `Vacuum then Mop`, SDK에서 `VacuumThenMop`이다.

### 속성

모든 속성은 `side="server"`로 정의되어 있다.

| 코드 | 이름 | define | 타입 | 길이 및 조건 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, 항목 타입 `ModeOptionStruct` | 최소 `2`, 최대 `255` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | 별도 명시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, 항목 타입 `enum16` | 최소 `1`, 최대 `16`; `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 따른 `mandatoryConform`이 명시되어 있다.

SDK 파일은 주석으로 `OnMode`(`0x0003`)가 deprecated임을 표시한다. `StartUpMode` 속성 정의는 제공된 SDK 파일에 없다.

### 명령

| 코드 | 이름 | source | 응답 | 적합성 및 설정 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | `mandatoryConform` |
| `0x01` | `ChangeToModeResponse` | `server` | — | `mandatoryConform`, `disableDefaultResponse="true"` |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"` |

#### ChangeToMode

장치의 모드를 변경한다.

| fieldId | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신했을 때 전송한다.

| fieldId | 이름 | 타입 | 조건 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 선택 지정 없음 |
| `1` | `StatusText` | `char_string` | `optional="true"`, 최대 길이 `64` |

스펙 리비전 이력에는 `InvalidInMode` 상태에서 `StatusText`를 제공해야 한다고 명시되어 있다.

#### ChangeToModeByCoreTag

지정한 모드 태그 값이 태그 목록에 포함된 모드 중 하나로 장치 모드를 변경한다.

| fieldId | 이름 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

`otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 따른 `mandatoryConform`이 명시되어 있다.

### 제공된 스펙과 SDK의 차이

- SDK의 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`는 제공된 스펙 XML에 없으며, SDK에서 provisional로 표시된다.
- 스펙은 `OnOff` 기능과 `StartUpMode`, `OnMode` 속성을 `disallowConform`으로 명시한다. SDK에는 해당 기능과 속성의 정의가 없으며, `OnMode`에 대한 deprecated 주석만 있다.
- 상태 열거형 이름과 `0x4003` 모드 태그 이름은 두 입력에서 다르므로 각각의 원문 식별자를 유지한다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Robotic Vacuum Cleaner](../device-types/robotic-vacuum-cleaner.md)
