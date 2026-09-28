---
entity: Laundry Washer Mode
ids: ['0x0051']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml', 'data_model/1.7/clusters/Mode_LaundryWasher.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Laundry Washer Mode

## 개요

Laundry Washer Mode는 지원되는 옵션 목록에서 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0051` |
| 스펙 이름 | `Laundry Washer Mode Cluster` |
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
| `2` | `ChangeToModeResponse`의 상태가 `InvalidInMode`이면 `StatusText`를 반드시 제공하도록 변경 |
| `3` | `OnOff` 기능, `StartUpMode`, `OnMode`를 허용하지 않도록 변경. 이전에는 Device Type에서 재정의 |
| `4` | 기반 클러스터의 최신 버전 반영 |

### 기능 제한

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성 | 허용하지 않음 |

### 데이터 타입

#### ModeTag

스펙과 SDK의 값 표기는 아래와 같다. 기본 값의 16진수 자릿수는 각 원문의 표기를 유지한다.

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
| `Delicate` | `0x4001` | `0x4001` |
| `Heavy` | `0x4002` | `0x4002` |
| `Whites` | `0x4003` | `0x4003` |

#### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 명시된 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | — |
| `1` | `Mode` | 필수 | — |
| `2` | `ModeTags` | 필수 | `1`~`8` |

제공된 스펙 조각에는 이 필드들의 타입이 명시되어 있지 않다.

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 허용하지 않음 |
| `0x0003` | `OnMode` | 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/laundry-washer-mode-cluster.xml`

### 생성 정보 및 클러스터 설정

- Alchemy가 생성한 XML이며 직접 수정하지 않도록 표시되어 있다.
- 생성 원본: `src/app_clusters/Mode_LaundryWasher.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

| 항목 | 정의 |
|---|---|
| 이름 | `Laundry Washer Mode` |
| 코드 | `0x0051` |
| 매크로 | `LAUNDRY_WASHER_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="4"`, `side="either"` |

### ModeTag 정의

SDK는 `ModeTag`를 `enum16`으로 정의하고 `0x0051`에 연결한다.

- 기본 값: `Auto`, `Quick`, `Quiet`, `LowNoise`, `LowEnergy`, `Vacation`, `Min`, `Max`, `Night`, `Day`
- 파생 클러스터 전용 값: `Normal`, `Delicate`, `Heavy`, `Whites`
- 기본 값의 네임스페이스 기준 정의는 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조하도록 주석에 명시되어 있다.

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 / 성숙도 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 핵심 모드 지원 | 선택적, `provisional` |

### 속성

모든 아래 속성은 `side="server"`이다.

| 코드 | 이름 | define | 타입 | 길이 | 적합성 / 성숙도 |
|---|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, `entryType="ModeOptionStruct"` | `minLength="2"`, `length="255"` | `optional` 표기 없음 |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — | `optional` 표기 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, `entryType="enum16"` | `minLength="1"`, `length="16"` | `optional="true"`, `provisional`; `COREMODES` 조건에서 필수 |

### 명령

| 코드 | 이름 | source | 응답 | 적합성 / 성숙도 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `provisional`; `COREMODES` 조건에서 필수 |

#### ChangeToMode

장치의 모드를 변경한다.

| fieldId | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신하면 전송하는 응답이다. `disableDefaultResponse="true"`로 정의되어 있다.

| fieldId | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | — |
| `1` | `StatusText` | `char_string` | `length="64"`, `optional="true"` |

스펙의 리비전 이력에는 `InvalidInMode` 상태일 때 `StatusText`를 반드시 제공해야 한다고 명시되어 있다.

#### ChangeToModeByCoreTag

태그 목록에 지정된 모드 태그 값이 포함된 모드 중 하나로 장치의 모드를 변경한다.

| fieldId | 이름 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

### 제공된 스펙과 SDK의 정의 범위 차이

- 스펙 조각은 `OnOff`, `StartUpMode`, `OnMode`를 명시적으로 허용하지 않는다. SDK XML에는 이 항목들이 선언되어 있지 않다.
- SDK XML에는 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`가 `provisional`로 정의되어 있다. 제공된 스펙 조각에는 이 항목들이 나타나지 않는다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Laundry Washer](../device-types/laundry-washer.md)
