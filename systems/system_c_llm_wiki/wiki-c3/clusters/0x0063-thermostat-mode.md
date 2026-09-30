---
entity: Thermostat Mode
ids: ['0x0063']
source_paths: ['data_model/1.7/clusters/Mode_Thermostat.xml', 'src/app/clusters/mode-base-server/README.md', 'src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Thermostat Mode

## 개요

`Thermostat Mode`는 `Mode Base`에서 파생된 클러스터로, thermostat 장치용 추가 모드 태그와 네임스페이스가 지정된 열거형 값을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0063` |
| 스펙 이름 | `Thermostat Mode Cluster` |
| 클러스터 이름 | `Thermostat Mode` |
| 리비전 | `1` |
| 기반 클러스터 | `Mode Base` |
| 분류 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `TSTATM` |
| SDK 도메인 | `HVAC` |

`Mode Base`는 파생 클러스터를 위해 존재하는 가상 클러스터이며, 자체 클러스터 ID는 없다.

## 스펙

출처: `data_model/1.7/clusters/Mode_Thermostat.xml`

### 리비전 이력

| 리비전 | 요약 |
|---|---|
| `1` | Initial Release |

### 기능

| 비트 | 코드 | 이름 | 정의 |
|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터 의존성. `disallowConform`으로 허용되지 않음 |
| `1` | `COREMODES` | `CoreModes` | 기능 선언 |

### ModeTag

SDK의 값 표기는 자릿수가 다른 경우에도 원문 그대로 병기한다. SDK에서 `ModeTag`의 타입은 `enum16`이다.

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
| `Off` | `0x4000` | `0x4000` |
| `Cool` | `0x4001` | `0x4001` |
| `Heat` | `0x4002` | `0x4002` |
| `EmergencyHeat` | `0x4003` | `0x4003` |

### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | — |
| `1` | `Mode` | 필수 | — |
| `2` | `ModeTags` | 필수 | `1`–`8` |

### 속성

| ID | 이름 | 스펙 조각의 명시 사항 |
|---|---|---|
| `0x0000` | `SupportedModes` | 속성 선언 |
| `0x0001` | `CurrentMode` | 속성 선언 |
| `0x0002` | `StartUpMode` | 속성 선언 |
| `0x0003` | `OnMode` | `disallowConform`으로 허용되지 않음 |
| `0x0004` | `CoreModeTags` | 속성 선언 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml`

### 클러스터 설정

| 항목 | 값 |
|---|---|
| 클러스터 매크로 | `THERMOSTAT_MODE_CLUSTER` |
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `HVAC` |
| client | 활성화, `init="false"`, `tick="false"` |
| server | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `side="either"`, `value="1"` |

이 XML은 Alchemy가 생성한 파일이며, 직접 수정하지 않도록 명시되어 있다.

- 원본: `src/app_clusters/Mode_Thermostat.adoc`
- 생성 매개변수: `zap attribute=in-progress provisional-policy=loose force connectedhomeip-spec/src/app_clusters/Mode_Thermostat.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

### 기능

`CoreModes`는 하나 이상의 core mode 지원을 나타낸다.

| 비트 | 코드 | 이름 | API 성숙도 | 적합성 선언 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | `provisional` | `otherwiseConform` 안에 `provisionalConform`, `optionalConform` |

### 구조체

#### ModeOptionStruct

| 필드 ID | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Label` | `char_string` | 최대 길이 `64` |
| `1` | `Mode` | `int8u` | — |
| `2` | `ModeTags` | `ModeTagStruct` 배열 | 최소 길이 `1`, 최대 길이 `8` |

#### ModeTagStruct

| 필드 ID | 이름 | 타입 | 선택 여부 |
|---|---|---|---|
| `0` | `MfgCode` | `vendor_id` | 선택 |
| `1` | `Value` | `enum16` | 선택으로 표시되지 않음 |

### 속성

모든 속성의 `side`는 `server`이다.

| 코드 | 이름 | 매크로 | 타입 | 제약 및 설정 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `ModeOptionStruct` 배열 | 최소 길이 `2`, 최대 길이 `255` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — |
| `0x0002` | `StartUpMode` | `START_UP_MODE` | `int8u` | nullable, 쓰기 가능, 선택 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `enum16` 배열 | 최소 길이 `1`, 최대 길이 `16`, `optional="true"`, `apiMaturity="provisional"` |

- `StartUpMode`는 `optionalConform`을 선언한다.
- `CoreModeTags`는 `otherwiseConform` 안에 `provisionalConform`과 `COREMODES`에 대한 `mandatoryConform`을 선언한다.
- 제공된 SDK XML에는 `OnMode` 속성이 정의되어 있지 않다.

### 명령

| 코드 | 이름 | source | 응답 | 설명 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 장치 모드 변경 |
| `0x01` | `ChangeToModeResponse` | `server` | — | `ChangeToMode` 수신에 대한 장치 응답 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | 지정된 모드 태그 값을 태그 목록에 포함하는 모드 중 하나로 변경 |

#### 명령 필드

| 명령 | 필드 ID | 이름 | 타입 | 설정 |
|---|---|---|---|---|
| `ChangeToMode` | `0` | `NewMode` | `int8u` | — |
| `ChangeToModeResponse` | `0` | `Status` | `enum8` | — |
| `ChangeToModeResponse` | `1` | `StatusText` | `char_string` | 선택, 최대 길이 `64` |
| `ChangeToModeByCoreTag` | `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

- `ChangeToModeResponse`는 `disableDefaultResponse="true"`로 정의된다.
- `ChangeToModeByCoreTag`는 `optional="true"`, `apiMaturity="provisional"`로 정의된다.
- `ChangeToModeByCoreTag`는 `otherwiseConform` 안에 `provisionalConform`과 `COREMODES`에 대한 `mandatoryConform`을 선언한다.

## 관련 문서

### Mode Base 파생 클러스터 사용 안내

출처: `src/app/clusters/mode-base-server/README.md`

이 문서는 `Mode Base` 파생 클러스터에 대해 다음 절차를 안내한다.

1. `ModeBase::Delegate`를 상속하는 클래스를 생성한다.
2. 다음 메서드를 구현한다.
   - `GetModeLabelByIndex`
   - `GetModeValueByIndex`
   - `GetModeTagsByIndex`
   - `HandleChangeToMode`
3. 필요하면 `Init`을 구현한다.
4. `.c` 또는 `.cpp` 번역 단위에서 `ModeBase::Instance`를 상속한 클래스의 인스턴스를 생성한다.
5. 루트 `Server::Init()` 이후 인스턴스의 `.Init()`을 호출한다.
   - 인스턴스 생성과 초기화는 `emberAf<ClusterName>ClusterInitCallback`에서 수행할 수도 있다.
6. `chip_device_project_config_include` 파일에 다음 정의를 추가한다.

   ```c
   #define MATTER_DM_PLUGIN_MODE_BASE
   ```

예제에서 해당 설정 파일은 `CHIPProjectAppConfig.h`이다.

**속성 접근:** 이 클러스터들에는 Zap 접근자 함수가 없다. 인스턴스의 `Update...` 및 `Get...` 함수를 사용한다.

### 참조 위치

- `mode-base-server.h`: 메서드 및 생성자 문서.
- `examples/all-clusters-app/all-clusters-common`의 `src`와 `include` 디렉터리에 있는 `<alias name>-mode.*`: 모든 데이터를 메모리에 저장하는 단순 예제.
- 클러스터별 열거형: 해당 클러스터 네임스페이스에서 접근.

### 새 파생 클러스터 추가 절차

문서는 스펙에 새 `Mode Base` 파생 클러스터가 정의된 뒤 다음 작업을 수행하도록 안내한다.

1. `src/app/zap-templates/zcl/data-model/chip`에 스펙을 XML로 작성한다.
2. zap 코드를 다시 생성한다.
3. `all-clusters-app` 예제에 새 클러스터를 추가한다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
