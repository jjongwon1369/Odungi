---
entity: Room Air Conditioner
ids: ['0x0072']
source_paths: ['data_model/1.7/device_types/RoomAirConditioner.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
---

# Room Air Conditioner

## 개요

| 항목 | 값 |
|---|---|
| 디바이스 타입 | Room Air Conditioner |
| 디바이스 타입 ID | `0x0072` |
| 리비전 | `5` |
| 분류 | `simple` |
| 범위 | `endpoint` |
| 스펙 파일 | `data_model/1.7/device_types/RoomAirConditioner.xml` |

## 스펙

### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | Thermostat User Interface Configuration 추가. Scenes를 클러스터 ID `0x0062`의 Scenes Management로 변경 |
| `3` | 필터 모니터링 클러스터 추가 |
| `4` | Groupcast 조건 요구사항 추가 |
| `5` | Thermostat Mode 추가 |

### 조건 요구사항

| 대상 디바이스 타입 | ID | 조건 | 적합성 |
|---|---|---|---|
| Root Node | `0x0016` | `GroupcastListenerCond` | 선택 (`optionalConform`) |

### 클러스터 구성

모든 클러스터의 `side`는 `server`이다.

| 클러스터 ID | 클러스터 이름 | 적합성 | 추가 요구사항 |
|---|---|---|---|
| `0x0003` | Identify | 필수 | — |
| `0x0004` | Groups | 선택 | — |
| `0x0006` | On/Off | 필수 | `DF` 기능 필수 |
| `0x0062` | Scenes Management | 선택 | — |
| `0x0063` | Thermostat Mode | 아래 적합성 정의 참조 | `StartUpMode`, `SupportedModes` 요구사항 |
| `0x0071` | HEPA Filter Monitoring | 선택 | — |
| `0x0072` | Activated Carbon Filter Monitoring | 선택 | — |
| `0x0201` | Thermostat | 필수 | — |
| `0x0202` | Fan Control | 선택 | — |
| `0x0204` | Thermostat User Interface Configuration | 선택 | `KeypadLockout` 선택 |
| `0x0402` | Temperature Measurement | 선택 | — |
| `0x0405` | Relative Humidity Measurement | 선택 | — |

### Thermostat Mode 적합성

Thermostat Mode (`0x0063`)의 적합성은 다음과 같이 정의되어 있다.

```xml
<otherwiseConform>
  <provisionalConform/>
  <optionalConform>
    <greaterOrEqualTerm>
      <revision value="current"/>
      <revision value="5"/>
    </greaterOrEqualTerm>
  </optionalConform>
</otherwiseConform>
```

`otherwiseConform`에는 `provisionalConform`과 현재 리비전이 `5` 이상인 경우의 `optionalConform`이 순서대로 포함된다.

#### 속성 요구사항

| 속성 코드 | 속성 이름 | 적합성 정의 |
|---|---|---|
| `0x0002` | `StartUpMode` | `otherwiseConform`에 `provisionalConform`, `disallowConform` 순서로 정의 |
| `0x0000` | `SupportedModes` | `otherwiseConform`에 `provisionalConform`, `mandatoryConform` 순서로 정의 |

`SupportedModes`에는 `<constraint><desc/></constraint>`가 있으나, 구체적인 제약 설명은 제공되지 않는다.

### Thermostat User Interface Configuration 속성

| 속성 코드 | 속성 이름 | 적합성 |
|---|---|---|
| `0x0001` | `KeypadLockout` | 선택 (`optionalConform`) |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [Groups `0x0004`](../clusters/0x0004-groups.md)
- [On/Off `0x0006`](../clusters/0x0006-on-off.md)
- [Scenes Management `0x0062`](../clusters/0x0062-scenes-management.md)
- [Thermostat Mode `0x0063`](../clusters/0x0063-thermostat-mode.md)
- [HEPA Filter Monitoring `0x0071`](../clusters/0x0071-hepa-filter-monitoring.md)
- [Thermostat `0x0201`](../clusters/0x0201-thermostat.md)
- [Fan Control `0x0202`](../clusters/0x0202-fan-control.md)
- [Thermostat User Interface Configuration `0x0204`](../clusters/0x0204-thermostat-user-interface-configuration.md)
- [Temperature Measurement `0x0402`](../clusters/0x0402-temperature-measurement.md)
- [Relative Humidity Measurement `0x0405`](../clusters/0x0405-relative-humidity-measurement.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
