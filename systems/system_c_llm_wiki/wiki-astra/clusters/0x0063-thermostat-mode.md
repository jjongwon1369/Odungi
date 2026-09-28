---
entity: Thermostat Mode
ids: ['0x0063']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml', 'src/app/clusters/mode-base-server/README.md', 'data_model/1.7/clusters/Mode_Thermostat.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Thermostat Mode

## 개요

Thermostat Mode는 Mode Base에서 파생된 클러스터로, thermostat 장치를 위한 추가 모드 태그와 네임스페이스 열거 값을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 ID | `0x0063` |
| 스펙 이름 | `Thermostat Mode Cluster` |
| 클러스터 이름 | `Thermostat Mode` |
| revision | `1` |
| 기반 클러스터 | `Mode Base` |
| SDK 도메인 | `HVAC` |
| PICS 코드 | `TSTATM` |
| 범위 | `Endpoint` |

Mode Base 자체는 클러스터 ID가 없는 의사 클러스터이며, 다른 클러스터가 이를 상속하기 위한 용도로 존재한다.

## 스펙

출처: `data_model/1.7/clusters/Mode_Thermostat.xml`

### 분류 및 revision

- `hierarchy`: `derived`
- `baseCluster`: `Mode Base`
- `role`: `application`
- `picsCode`: `TSTATM`
- `scope`: `Endpoint`
- revision `1`: `Initial Release`

### 기능

| bit | code | name | 스펙 정의 |
|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터 의존성. `disallowConform`으로 금지 |
| `1` | `COREMODES` | `CoreModes` | 기능 선언 |

### ModeTag

스펙과 SDK에 정의된 이름은 동일하다. 값의 표기는 각 원문을 그대로 유지한다.

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

| 필드 ID | 이름 | 적합성 및 제약 |
|---|---|---|
| `0` | `Label` | 필수 |
| `1` | `Mode` | 필수 |
| `2` | `ModeTags` | 필수, 항목 수 `1`–`8` |

### 속성

| ID | 이름 | 스펙 XML의 명시 사항 |
|---|---|---|
| `0x0000` | `SupportedModes` | 속성 선언 |
| `0x0001` | `CurrentMode` | 속성 선언 |
| `0x0002` | `StartUpMode` | 속성 선언 |
| `0x0003` | `OnMode` | `disallowConform`으로 금지 |
| `0x0004` | `CoreModeTags` | 속성 선언 |

제공된 스펙 XML에는 명령 정의가 포함되어 있지 않다.

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/thermostat-mode-cluster.xml`

### 클러스터 메타데이터

| 항목 | 값 |
|---|---|
| configurator 도메인 | `CHIP` |
| 클러스터 도메인 | `HVAC` |
| 클러스터 이름 | `Thermostat Mode` |
| 클러스터 코드 | `0x0063` |
| define | `THERMOSTAT_MODE_CLUSTER` |
| client | `true`, `init="false"`, `tick="false"` |
| server | `true`, `init="false"`, `tick="false"` |
| 전역 속성 | 코드 `0xFFFD`, `side="either"`, 값 `1` |

이 XML은 Alchemy로 생성되었으며, 직접 수정하지 않도록 명시되어 있다.

- Source: `src/app_clusters/Mode_Thermostat.adoc`
- Parameters: `zap attribute=in-progress provisional-policy=loose force connectedhomeip-spec/src/app_clusters/Mode_Thermostat.adoc`
- Git: `0.9-1.7-winter2027`
- Alchemy: `v1.7.10`

### 기능

| bit | code | name | 설명 | 성숙도 및 적합성 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 core mode 지원 | `apiMaturity="provisional"`; `otherwiseConform`에 `provisionalConform`과 `optionalConform` 선언 |

SDK XML에는 `DEPONOFF` 기능과 `OnMode` 속성이 정의되어 있지 않다.

### 데이터 타입

`ModeTag`는 `enum16`이며, 클러스터 코드 `0x0063`에 연결된다. 열거 항목은 스펙 섹션의 표와 같다.

#### ModeOptionStruct

| fieldId | 이름 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Label` | `char_string` | `length="64"` |
| `1` | `Mode` | `int8u` | — |
| `2` | `ModeTags` | `ModeTagStruct` 배열 | `minLength="1"`, `length="8"` |

#### ModeTagStruct

| fieldId | 이름 | 타입 | 선택 여부 |
|---|---|---|---|
| `0` | `MfgCode` | `vendor_id` | `optional="true"` |
| `1` | `Value` | `enum16` | 선택 표시 없음 |

두 구조체 모두 클러스터 코드 `0x0063`에 연결된다.

### 속성

모든 속성의 `side`는 `server`이다.

| 코드 | 이름 | define | 타입 | 제약 및 설정 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `ModeOptionStruct` 배열 | `minLength="2"`, `length="255"` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | — |
| `0x0002` | `StartUpMode` | `START_UP_MODE` | `int8u` | `isNullable="true"`, `writable="true"`, `optional="true"`; `optionalConform` |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `enum16` 배열 | `minLength="1"`, `length="16"`, `optional="true"`, `apiMaturity="provisional"` |

`CoreModeTags`의 `otherwiseConform`에는 `provisionalConform`과 `COREMODES` 기능에 따른 `mandatoryConform`이 선언되어 있다.

### 명령

| 코드 | 이름 | source | 응답 | 설명 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 장치 모드를 변경 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 장치가 `ChangeToMode`를 수신했을 때 전송 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | 지정한 모드 태그 값을 태그 목록에 포함하는 모드 중 하나로 변경 |

#### ChangeToMode

| fieldId | 인자 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

`disableDefaultResponse="true"`로 정의된다.

| fieldId | 인자 | 타입 | 제약 |
|---|---|---|---|
| `0` | `Status` | `enum8` | — |
| `1` | `StatusText` | `char_string` | `optional="true"`, `length="64"` |

#### ChangeToModeByCoreTag

- `optional="true"`, `apiMaturity="provisional"`로 정의된다.
- `otherwiseConform`에 `provisionalConform`과 `COREMODES` 기능에 따른 `mandatoryConform`이 선언되어 있다.

| fieldId | 인자 | 타입 | 성숙도 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

## 관련 문서

### Mode Base 사용 안내

출처: `src/app/clusters/mode-base-server/README.md`

Mode Base 파생 클러스터를 사용하는 절차는 다음과 같다.

1. `ModeBase::Delegate`를 상속하는 클래스를 작성한다.
2. 다음 메서드를 구현한다.
   - `GetModeLabelByIndex`
   - `GetModeValueByIndex`
   - `GetModeTagsByIndex`
   - `HandleChangeToMode`
3. 필요하면 `Init` 함수를 구현한다.
4. `.c` 또는 `.cpp` 번역 단위에서 `ModeBase::Instance`를 상속한 클래스의 인스턴스를 생성한다.
5. 루트 `Server::Init()` 이후 인스턴스의 `.Init()`을 호출한다.
   - 인스턴스 생성과 초기화는 대신 `emberAf<ClusterName>ClusterInitCallback`에서 수행할 수 있다.
6. `chip_device_project_config_include` 파일에 `#define MATTER_DM_PLUGIN_MODE_BASE`를 추가한다.
   - 예제에서 이 파일은 `CHIPProjectAppConfig.h`이다.

메서드와 생성자의 상세 설명은 `mode-base-server.h`를 참조한다. 클러스터별 열거형은 해당 클러스터 네임스페이스에서 접근할 수 있다.

**속성 접근:** 이 클러스터들에는 Zap accessor 함수가 없다. 인스턴스의 `Update...` 및 `Get...` 함수를 사용한다.

### 문서에서 참조하는 예제

메모리에 모든 데이터를 저장하는 간단한 예제는 `examples/all-clusters-app/all-clusters-common`의 `src` 및 `include` 디렉터리에 있는 `<alias name>-mode.*` 파일을 참조한다.

### 새로운 파생 클러스터 추가 절차

스펙에 Mode Base 파생 클러스터가 정의된 이후 다음 절차를 따른다.

1. 스펙을 `src/app/zap-templates/zcl/data-model/chip`의 XML로 작성한다.
2. zap 코드를 다시 생성한다.
3. all-clusters-app 예제에 새 클러스터를 추가한다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Room Air Conditioner](../device-types/room-air-conditioner.md)
