---
entity: Refrigerator And Temperature Controlled Cabinet Mode
ids: ['0x0052']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml', 'data_model/1.7/clusters/Mode_Refrigerator.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Refrigerator And Temperature Controlled Cabinet Mode

## 개요

지원되는 옵션 목록에서 장치 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0052` |
| 스펙 이름 | `Refrigerator And Temperature Controlled Cabinet Mode Cluster` |
| SDK 이름 | `Refrigerator And Temperature Controlled Cabinet Mode` |
| 리비전 | `4` |
| 기반 클러스터 | `Mode Base` |
| 계층 / 역할 / 범위 | `derived` / `application` / `Endpoint` |
| PICS 코드 | `TCCM` |
| SDK 도메인 | `Appliances` |

## 스펙

출처: `data_model/1.7/clusters/Mode_Refrigerator.xml`

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `ChangeToModeResponse`의 상태가 `InvalidInMode`이면 `StatusText`를 반드시 제공하도록 변경 |
| `3` | `OnOff` 기능, `StartUpMode`, `OnMode`를 허용하지 않도록 변경. 이전에는 Device Type에서 재정의 |
| `4` | 기반 클러스터의 최신 버전 채택 |

### 기능 제약

| 비트 | 코드 | 이름 | 적합성 |
|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | 허용하지 않음 |

`OnOff`는 `OnOff` 클러스터와의 의존성을 나타내는 기능이지만, 이 클러스터에서는 허용되지 않는다.

### 데이터 타입

#### ModeTag

기본 태그와 클러스터별 태그를 포함한다. 스펙과 SDK의 값 표기는 다음과 같다.

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
| `RapidCool` | `0x4000` | `0x4000` |
| `RapidFreeze` | `0x4001` | `0x4001` |

#### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 명시된 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | — |
| `1` | `Mode` | 필수 | — |
| `2` | `ModeTags` | 필수 | 항목 수 `1`~`8` |

제공된 스펙 조각에는 각 필드의 타입이 명시되어 있지 않다.

### 속성 적합성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 필수 |
| `0x0001` | `CurrentMode` | 필수 |
| `0x0002` | `StartUpMode` | 허용하지 않음 |
| `0x0003` | `OnMode` | 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/refrigerator-and-temperature-controlled-cabinet-mode-cluster.xml`

### 생성 정보 및 클러스터 설정

- Alchemy로 생성된 XML이며 직접 편집하지 않도록 표시되어 있다.
- 생성 원본: `src/app_clusters/Mode_Refrigerator.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`
- 클러스터 매크로: `REFRIGERATOR_AND_TEMPERATURE_CONTROLLED_CABINET_MODE_CLUSTER`
- `client`와 `server` 모두 활성화되어 있으며, 각각 `init="false"`, `tick="false"`로 설정되어 있다.
- 전역 속성 `0xFFFD`는 `side="either"`, `value="4"`로 정의된다.

### ModeTag 정의

`ModeTag`는 클러스터 `0x0052`에 연결된 `enum16`이다.

- 기본 값: `Auto`, `Quick`, `Quiet`, `LowNoise`, `LowEnergy`, `Vacation`, `Min`, `Max`, `Night`, `Day`
- 클러스터별 값: `RapidCool`, `RapidFreeze`

SDK 주석은 기본 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조한다.

### 기능

| 비트 | 코드 | 이름 | 설명 | 성숙도 / 적합성 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 코어 모드 지원 | `provisional`, 선택 사항 |

### 속성

모든 아래 속성은 `server` 측에 정의된다.

| 코드 | 이름 | 매크로 | 타입 | 길이 제약 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, 항목 타입 `ModeOptionStruct` | `minLength="2"`, `length="255"` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, 항목 타입 `enum16` | `minLength="1"`, `length="16"` |

`CoreModeTags`에는 `optional="true"`와 `apiMaturity="provisional"`이 지정되어 있다. 적합성 정의에서는 `COREMODES` 기능에 대해 필수로 지정한다.

### 명령

| 코드 | 이름 | 송신 측 | 응답 | 적합성 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | `optional="true"`, `provisional`; `COREMODES` 기능에 대해 필수 |

#### ChangeToMode

장치의 모드를 변경한다.

| 필드 ID | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신하면 전송한다. `disableDefaultResponse="true"`로 정의된다.

| 필드 ID | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | — |
| `1` | `StatusText` | `char_string` | `length="64"`, `optional="true"` |

스펙 리비전 이력에는 `InvalidInMode` 상태에 대해 `StatusText`를 반드시 제공해야 한다고 명시되어 있다.

#### ChangeToModeByCoreTag

주어진 모드 태그 값을 태그 목록에 포함하는 모드 중 하나로 장치 모드를 변경한다.

| 필드 ID | 이름 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `provisional` |

### 제공된 스펙과의 정의 범위 차이

- 스펙 조각은 `OnOff`, `StartUpMode`, `OnMode`를 허용하지 않는다고 명시한다.
- SDK 조각은 `CoreModes`, `CoreModeTags`, `ChangeToModeByCoreTag`를 `provisional`로 정의한다.
- 제공된 스펙 조각에는 이 코어 모드 관련 정의가 나타나지 않는다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Refrigerator](../device-types/refrigerator.md)
- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
