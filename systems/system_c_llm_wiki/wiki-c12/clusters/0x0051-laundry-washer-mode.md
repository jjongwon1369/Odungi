---
entity: Laundry Washer Mode
ids: ['0x0051']
source_paths: ['data_model/1.7/clusters/Mode_LaundryWasher.xml', 'src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Laundry Washer Mode

## 개요

`Laundry Washer Mode`는 지원되는 옵션 목록에서 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다. `Mode Base`에서 파생되며, 클러스터 ID는 `0x0051`이다.

| 항목 | 값 |
|---|---|
| 스펙 이름 | `Laundry Washer Mode Cluster` |
| 클러스터 이름 | `Laundry Washer Mode` |
| 클러스터 ID | `0x0051` |
| 리비전 | `4` |
| 기반 클러스터 | `Mode Base` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `LWM` |

## 스펙

출처: `data_model/1.7/clusters/Mode_LaundryWasher.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `ChangeToModeResponse`의 상태가 `InvalidInMode`이면 `StatusText`를 반드시 제공하도록 변경 |
| `3` | `OnOff` 기능, `StartUpMode`, `OnMode`를 허용하지 않도록 설정. 이전에는 Device Type 재정의로 처리 |
| `4` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성 | 허용하지 않음 |

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
| `0x4000` | `Normal` |
| `0x4001` | `Delicate` |
| `0x4002` | `Heavy` |
| `0x4003` | `Whites` |

#### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | 별도 명시 없음 |
| `1` | `Mode` | 필수 | 별도 명시 없음 |
| `2` | `ModeTags` | 필수 | `1`–`8` |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 허용하지 않음 |
| `0x0003` | `OnMode` | 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml`

이 파일은 `src/app_clusters/Mode_LaundryWasher.adoc`에서 Alchemy로 생성되었으며, 직접 수정하지 않도록 표시되어 있다.

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `Appliances` |
| 이름 | `Laundry Washer Mode` |
| 코드 | `0x0051` |
| define | `LAUNDRY_WASHER_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="4"`, `side="either"` |
| 생성 Git 버전 | `0.9-1.7-winter2027` |
| Alchemy 버전 | `v1.7.10` |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 core mode 지원 | `provisional`, 선택적 |

### 데이터 타입

`ModeTag`는 `enum16`이며, 클러스터 코드 `0x0051`에 연결된다.

| 구분 | 값 | 이름 |
|---|---|---|
| 기반 값 | `0x0000` | `Auto` |
| 기반 값 | `0x0001` | `Quick` |
| 기반 값 | `0x0002` | `Quiet` |
| 기반 값 | `0x0003` | `LowNoise` |
| 기반 값 | `0x0004` | `LowEnergy` |
| 기반 값 | `0x0005` | `Vacation` |
| 기반 값 | `0x0006` | `Min` |
| 기반 값 | `0x0007` | `Max` |
| 기반 값 | `0x0008` | `Night` |
| 기반 값 | `0x0009` | `Day` |
| 파생 클러스터 전용 값 | `0x4000` | `Normal` |
| 파생 클러스터 전용 값 | `0x4001` | `Delicate` |
| 파생 클러스터 전용 값 | `0x4002` | `Heavy` |
| 파생 클러스터 전용 값 | `0x4003` | `Whites` |

SDK 주석은 기반 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조한다.

### 속성

모든 속성의 `side`는 `server`이다.

| 코드 | 이름 | define | 타입 | 길이 및 적합성 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, `entryType="ModeOptionStruct"` | `minLength="2"`, `length="255"` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | 별도 제약 명시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, `entryType="enum16"` | `minLength="1"`, `length="16"`, `optional="true"`, `apiMaturity="provisional"`; `COREMODES` 기능에 대한 필수 적합성 조건 포함 |

### 명령

| 코드 | 이름 | source | 응답 | 적합성 및 설정 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수, `disableDefaultResponse="true"` |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"`; `COREMODES` 기능에 대한 필수 적합성 조건 포함 |

#### ChangeToMode

장치의 모드를 변경한다.

| fieldId | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신하면 전송하는 응답이다.

| fieldId | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 별도 제약 명시 없음 |
| `1` | `StatusText` | `char_string` | `length="64"`, `optional="true"` |

SDK에서는 `StatusText`가 선택적으로 선언되어 있으나, 제공된 스펙의 리비전 이력은 `InvalidInMode` 상태에서 이를 반드시 제공하도록 명시한다.

#### ChangeToModeByCoreTag

주어진 모드 태그 값을 태그 목록에 포함하는 모드 중 하나로 장치 모드를 변경한다.

| fieldId | 이름 | 타입 | API 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

### 제공된 스펙과의 차이

- SDK에는 제공된 스펙 XML에 없는 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`가 `provisional`로 정의되어 있다.
- 스펙에서 허용하지 않는 `OnOff` 기능, `StartUpMode`, `OnMode`는 제공된 SDK XML에 선언되어 있지 않다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Laundry Dryer](../device-types/laundry-dryer.md)
- [Laundry Washer](../device-types/laundry-washer.md)
