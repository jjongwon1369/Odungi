---
entity: Water Heater Mode
ids: ['0x009E']
source_paths: ['data_model/1.7/clusters/Mode_WaterHeater.xml', 'src/app/clusters/mode-base-server/README.md', 'src/app/zap-templates/zcl/data-model/chip/water-heater-mode-cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Water Heater Mode

## 개요

Water Heater Mode는 지원하는 옵션 목록에서 장치 모드를 선택하기 위한 속성과 명령을 제공하는 클러스터이다. 클러스터 ID는 `0x009E`이며, `Mode Base`에서 파생된다.

`Mode Base`는 자체 클러스터 ID가 없고 다른 클러스터의 기반으로만 사용되는 가상 클러스터이다.

| 항목 | 값 |
|---|---|
| 스펙 이름 | `Water Heater Mode Cluster` |
| 클러스터 이름 | `Water Heater Mode` |
| 클러스터 ID | `0x009E` |
| 리비전 | `2` |
| 기반 클러스터 | `Mode Base` |
| 분류 | `derived` |
| 역할 | `application` |
| 범위 | `Endpoint` |
| PICS 코드 | `WHM` |
| SDK 도메인 | `Energy Management` |

## 스펙

출처: `data_model/1.7/clusters/Mode_WaterHeater.xml`

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 기반 클러스터의 최신 버전 채택 |

### 기능

| 비트 | 코드 | 이름 | 설명 | 적합성 |
|---|---|---|---|---|
| `0` | `DEPONOFF` | `OnOff` | `OnOff` 클러스터와의 의존성 | `disallowConform`: 허용하지 않음 |

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
| `0x4000` | `Off` |
| `0x4001` | `Manual` |
| `0x4002` | `Timed` |

#### ModeOptionStruct

| 필드 ID | 이름 | 적합성 | 제약 |
|---|---|---|---|
| `0` | `Label` | 필수 | 제공된 스펙 조각에 명시되지 않음 |
| `1` | `Mode` | 필수 | 제공된 스펙 조각에 명시되지 않음 |
| `2` | `ModeTags` | 필수 | `1`~`8` |

### 속성

| ID | 이름 | 적합성 |
|---|---|---|
| `0x0000` | `SupportedModes` | 제공된 스펙 조각에 별도 명시 없음 |
| `0x0001` | `CurrentMode` | 제공된 스펙 조각에 별도 명시 없음 |
| `0x0002` | `StartUpMode` | `disallowConform`: 허용하지 않음 |
| `0x0003` | `OnMode` | `disallowConform`: 허용하지 않음 |

## SDK 정의

출처: `src/app/zap-templates/zcl/data-model/chip/water-heater-mode-cluster.xml`

이 파일은 `src/app_clusters/Mode_WaterHeater.adoc`에서 Alchemy로 생성되었으며, 직접 편집하지 않도록 표시되어 있다.

### 클러스터 설정

| 항목 | 값 |
|---|---|
| 도메인 | `Energy Management` |
| 이름 | `Water Heater Mode` |
| 코드 | `0x009E` |
| 매크로 | `WATER_HEATER_MODE_CLUSTER` |
| 클라이언트 | 활성화, `init="false"`, `tick="false"` |
| 서버 | 활성화, `init="false"`, `tick="false"` |
| 전역 속성 | `code="0xFFFD"`, `value="2"`, `side="either"` |

### 기능

| 비트 | 코드 | 이름 | 설명 | 상태 |
|---|---|---|---|---|
| `1` | `COREMODES` | `CoreModes` | 하나 이상의 핵심 모드 지원 | `apiMaturity="provisional"`, `optionalConform` |

제공된 스펙 조각에는 `CoreModes`가 없지만, SDK 정의에는 provisional 기능으로 포함되어 있다.

### ModeTag

SDK의 `ModeTag` 타입은 `enum16`이다.

| 스펙 값 | SDK 값 | 이름 |
|---|---|---|
| `0x00` | `0x0000` | `Auto` |
| `0x01` | `0x0001` | `Quick` |
| `0x02` | `0x0002` | `Quiet` |
| `0x03` | `0x0003` | `LowNoise` |
| `0x04` | `0x0004` | `LowEnergy` |
| `0x05` | `0x0005` | `Vacation` |
| `0x06` | `0x0006` | `Min` |
| `0x07` | `0x0007` | `Max` |
| `0x08` | `0x0008` | `Night` |
| `0x09` | `0x0009` | `Day` |
| `0x4000` | `0x4000` | `Off` |
| `0x4001` | `0x4001` | `Manual` |
| `0x4002` | `0x4002` | `Timed` |

SDK 주석은 기본 값의 네임스페이스 기준 정의로 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`의 `enum class ModeTag`를 참조한다. `Off`, `Manual`, `Timed`는 파생 클러스터 전용 값이다.

### 속성

모든 속성의 `side`는 `server`이다.

| 코드 | 이름 | 매크로 | 타입 | 길이 / 제약 |
|---|---|---|---|---|
| `0x0000` | `SupportedModes` | `SUPPORTED_MODES` | `array`, `entryType="ModeOptionStruct"` | `minLength="2"`, `length="255"` |
| `0x0001` | `CurrentMode` | `CURRENT_MODE` | `int8u` | 별도 명시 없음 |
| `0x0004` | `CoreModeTags` | `CORE_MODE_TAGS` | `array`, `entryType="enum16"` | `minLength="1"`, `length="16"` |

`CoreModeTags`에는 `optional="true"`와 `apiMaturity="provisional"`이 지정되어 있으며, 적합성 조건은 `COREMODES` 기능에 대해 필수를 명시한다. `StartUpMode`와 `OnMode`는 제공된 SDK 정의에 포함되어 있지 않다.

### 명령

| 코드 | 이름 | 발신 측 | 응답 | 적합성 |
|---|---|---|---|---|
| `0x00` | `ChangeToMode` | `client` | `ChangeToModeResponse` | 필수 |
| `0x01` | `ChangeToModeResponse` | `server` | — | 필수 |
| `0x02` | `ChangeToModeByCoreTag` | `client` | `ChangeToModeResponse` | provisional, `COREMODES` 기능에 대해 필수 |

#### ChangeToMode

장치 모드를 변경한다.

| 필드 ID | 이름 | 타입 |
|---|---|---|
| `0` | `NewMode` | `int8u` |

#### ChangeToModeResponse

장치가 `ChangeToMode`를 수신했을 때 전송하는 응답이다. `disableDefaultResponse="true"`가 지정되어 있다.

| 필드 ID | 이름 | 타입 | 조건 |
|---|---|---|---|
| `0` | `Status` | `enum8` | 선택 표시 없음 |
| `1` | `StatusText` | `char_string` | `optional="true"`, `length="64"` |

원문에서 `StatusText`에는 `lenght="64"`도 함께 기재되어 있다.

#### ChangeToModeByCoreTag

지정한 모드 태그 값을 태그 목록에 포함하는 모드 중 하나로 장치 모드를 변경한다.

| 필드 ID | 이름 | 타입 | 상태 |
|---|---|---|---|
| `0` | `NewModeTag` | `enum16` | `apiMaturity="provisional"` |

명령에는 `optional="true"`와 `apiMaturity="provisional"`이 지정되어 있으며, 적합성 조건은 `COREMODES` 기능에 대해 필수를 명시한다.

## 관련 문서

### Mode Base 사용 안내

출처: `src/app/clusters/mode-base-server/README.md`

`Mode Base` 파생 클러스터를 사용하기 위한 절차는 다음과 같다.

1. `ModeBase::Delegate`를 상속하는 클래스를 작성한다.
2. 다음 메서드를 구현한다.
   - `GetModeLabelByIndex`
   - `GetModeValueByIndex`
   - `GetModeTagsByIndex`
   - `HandleChangeToMode`
3. 필요에 따라 `Init`을 구현한다.
4. `.c` 또는 `.cpp` 번역 단위에서 `ModeBase::Instance`를 상속하는 클래스의 인스턴스를 생성한다.
5. 루트 `Server::Init()` 이후 인스턴스의 `.Init()`을 호출한다.
   - 인스턴스 생성과 초기화는 `emberAf<ClusterName>ClusterInitCallback`에서 수행할 수도 있다.
6. `chip_device_project_config_include` 파일에 다음 정의를 추가한다.

```c
#define MATTER_DM_PLUGIN_MODE_BASE
```

예제에서 해당 설정 파일은 `CHIPProjectAppConfig.h`이다.

메서드 및 생성자에 대한 자세한 설명은 `mode-base-server.h`를 참조한다. 클러스터별 열거형은 해당 클러스터 네임스페이스에서 접근할 수 있다.

**속성 접근:** 이 클러스터들에는 Zap 접근자 함수가 없다. 인스턴스의 `Update...` 및 `Get...` 함수를 사용한다.

### 문서에서 참조하는 예제

메모리에 데이터를 저장하는 단순한 구현은 `examples/all-clusters-app/all-clusters-common`의 `src` 및 `include` 디렉터리에 있는 `<alias name>-mode.*` 파일을 참조한다.

### 새 파생 클러스터 추가 절차

스펙에 새로운 `Mode Base` 파생 클러스터가 정의된 후에는 다음 절차를 따른다.

1. 유사한 파일을 참고하여 스펙을 `src/app/zap-templates/zcl/data-model/chip`의 XML로 작성한다.
2. zap 코드를 다시 생성한다.
3. all-clusters-app 예제에 새 클러스터를 추가한다.

## 관련 페이지

**베이스 클러스터**

- [ModeBase](../base/modebase.md)

**사용 기기**

- [Water Heater](../device-types/water-heater.md)
