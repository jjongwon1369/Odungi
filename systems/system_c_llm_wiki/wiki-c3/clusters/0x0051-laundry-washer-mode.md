---
entity: Laundry Washer Mode
ids: ['0x0051']
source_paths: ['data_model/1.7/clusters/Mode_LaundryWasher.xml', 'src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Laundry Washer Mode

## 개요

Laundry Washer Mode는 지원되는 옵션 목록에서 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0051` |
| 스펙 이름 | `Laundry Washer Mode Cluster` |
| 클러스터 이름 | `Laundry Washer Mode` |
| 리비전 | `4` |
| 기반 클러스터 | `Mode Base` |
| 계층 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `LWM` |
| SDK 도메인 | `Appliances` |

## 스펙

출처: `data_model/1.7/clusters/Mode_LaundryWasher.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `ChangeToModeResponse`에서 상태가 `InvalidInMode`이면 `StatusText`를 반드시 제공하도록 변경 |
| `3` | `OnOff` 기능, `StartUpMode`, `OnMode`를 금지하도록 변경. 이전에는 Device Type 재정의로 처리 |
| `4` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 종속성 | 금지 |

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
| `2` | `ModeTags` | 필수 | 항목 수 `1`~`8` |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 금지 |
| `0x0003` | `OnMode` | 금지 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml`

이 파일은 Alchemy로 생성되었으며 직접 수정하지 않도록 표시되어 있다.

| 항목 | 값 |
|---|---|
| 생성 원본 | `src/app_clusters/Mode_LaundryWasher.adoc` |
| Git | `0.9-1.7-winter2027` |
| Alchemy | `v1.7.10` |
| 클러스터 코드 | `0x0051` |
| 매크로 | `LAUNDRY_WASHER_MODE_CLUSTER` |
| 클라이언트 | 활성화, `init="false"`, `tick="false"` |
| 서버 | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | 코드 `0xFFFD`, 값 `4`, `side="either"` |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 및 성숙도 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 core mode 지원 | 선택 사항, `provisional` |

`CoreModes`는 제공된 SDK 정의에 포함되어 있지만, 제공된 스펙 조각에는 명시되어 있지 않다.

### 데이터 타입

`ModeTag`는 클러스터 `0x0051`에 연결된 `enum16`이다.

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
| `0x4001` | `Delicate` | 파생 클러스터 전용 값 |
| `0x4002` | `Heavy` | 파생 클러스터 전용 값 |
| `0x4003` | `Whites` | 파생 클러스터 전용 값 |

SDK 주석은 기반 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조한다.

### 속성

모든 속성은 `side="server"`로 정의되어 있다.

| 코드 | 이름 | 매크로 | 타입 | 길이 및 조건 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, 항목 타입 `ModeOptionStruct` | 최소 `2`, 최대 `255` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | 별도 제약 명시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, 항목 타입 `enum16` | 최소 `1`, 최대 `16`; `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 적합성 정의에는 `COREMODES` 기능에 따른 필수 조건이 포함되어 있다. `StartUpMode`와 `OnMode`는 제공된 SDK 속성 목록에 없다.

### 명령

| 코드 | 이름 | 발신 측 | 응답 | 적합성 및 설정 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수, `disableDefaultResponse="true"` |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `apiMaturity="provisional"`; `COREMODES` 기능에 따른 필수 조건 포함 |

#### ChangeToMode

장치의 모드를 변경한다.

| 필드 ID | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신했을 때 전송하는 응답이다.

| 필드 ID | 이름 | 타입 | 조건 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 선택 사항으로 표시되지 않음 |
| `1` | `StatusText` | `char_string` | 최대 길이 `64`, `optional="true"` |

SDK에서 `StatusText`는 선택 사항으로 표시되어 있지만, 스펙 리비전 이력에는 `InvalidInMode` 상태일 때 반드시 제공해야 한다고 명시되어 있다.

#### ChangeToModeByCoreTag

태그 목록에 지정된 모드 태그 값이 포함된 모드 중 하나로 장치 모드를 변경한다.

| 필드 ID | 이름 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
