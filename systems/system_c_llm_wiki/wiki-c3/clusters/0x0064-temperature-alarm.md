---
entity: Temperature Alarm
ids: ['0x0064']
source_paths: ['data_model/1.7/clusters/TemperatureAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Temperature Alarm

## 개요

Temperature Alarm은 온도 측정값이 임계값을 초과하거나 미만일 때 알람을 지원하는 클러스터이다. `Alarm Base`에서 파생되며, 임계값 조정 기능을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Temperature Alarm Cluster` |
| 클러스터 ID | `0x0064` |
| 클러스터 ID 이름 | `Temperature Alarm` |
| 리비전 | `1` |
| 적합성 | `provisionalConform` |
| 계층 | `derived` |
| 기반 클러스터 | `Alarm Base` |
| 역할 | `application` |
| PICS 코드 | `TEMPALM` |
| 범위 | `Endpoint` |

## 스펙

출처: `data_model/1.7/clusters/TemperatureAlarm.xml`

### 리비전 이력

| 리비전 | 요약 |
|---|---|
| `1` | Initial revision |

### 기능

모든 기능은 선택 사항이며, 아래 조건을 따른다. `OVER`와 `UNDER`는 `choice="a" more="true" min="1"`로 묶여 있어 하나 이상을 지원해야 한다.

| 비트 | 코드 | 이름 | 설명 | 선택 조건 |
|---|---|---|---|---|
| `20` | `OVER` | `OverTemperature` | 온도 측정값이 임계값을 초과할 때 알람 활성화 지원 | `OVER`, `UNDER` 중 하나 이상 |
| `21` | `UNDER` | `UnderTemperature` | 온도 측정값이 임계값 미만일 때 알람 활성화 지원 | `OVER`, `UNDER` 중 하나 이상 |
| `22` | `MAJOR` | `MajorThreshold` | 알람의 major 임계값 지원 | 별도 조건 없음 |
| `23` | `MINOR` | `MinorThreshold` | 알람의 minor 임계값 지원 | `MAJOR` |
| `24` | `OCRIADJ` | `OverCriticalAdjustable` | 상한 critical 온도 임계값 조정 지원 | `OVER` |
| `25` | `OMAJADJ` | `OverMajorAdjustable` | 상한 major 온도 임계값 조정 지원 | `OVER` AND `MAJOR` |
| `26` | `OMINADJ` | `OverMinorAdjustable` | 상한 minor 온도 임계값 조정 지원 | `OVER` AND `MINOR` |
| `27` | `UMINADJ` | `UnderMinorAdjustable` | 하한 minor 온도 임계값 조정 지원 | `UNDER` AND `MINOR` |
| `28` | `UMAJADJ` | `UnderMajorAdjustable` | 하한 major 온도 임계값 조정 지원 | `UNDER` AND `MAJOR` |
| `29` | `UCRIADJ` | `UnderCriticalAdjustable` | 하한 critical 온도 임계값 조정 지원 | `UNDER` |

### 데이터 타입

#### `AlarmBitmap`

모든 비트 필드는 `mandatoryConform`으로 정의된다.

| 비트 | 이름 | 의미 |
|---|---|---|
| `0` | `CriticalOverTemperatureAlarm` | 측정 온도가 critical 임계값을 초과함 |
| `1` | `MajorOverTemperatureAlarm` | 측정 온도가 major 임계값을 초과함 |
| `2` | `MinorOverTemperatureAlarm` | 측정 온도가 minor 임계값을 초과함 |
| `3` | `MinorUnderTemperatureAlarm` | 측정 온도가 minor 임계값 미만임 |
| `4` | `MajorUnderTemperatureAlarm` | 측정 온도가 major 임계값 미만임 |
| `5` | `CriticalUnderTemperatureAlarm` | 측정 온도가 critical 임계값 미만임 |

### 속성

모든 속성의 타입은 `temperature`이며, 접근 설정은 `read="true" readPrivilege="view"`이다. 각 속성은 아래 기능 조건에서 필수이다.

| ID | 이름 | 필수 조건 |
|---|---|---|
| `0x0080` | `CriticalOverTemperatureThreshold` | `OVER` |
| `0x0081` | `MajorOverTemperatureThreshold` | `OVER` AND `MAJOR` |
| `0x0082` | `MinorOverTemperatureThreshold` | `OVER` AND `MINOR` |
| `0x0083` | `MinorUnderTemperatureThreshold` | `UNDER` AND `MINOR` |
| `0x0084` | `MajorUnderTemperatureThreshold` | `UNDER` AND `MAJOR` |
| `0x0085` | `CriticalUnderTemperatureThreshold` | `UNDER` |

#### 속성 제약

아래 식에서 참조하는 이름은 모두 속성 이름이다. `maxOf`는 참조 값 중 최댓값, `minOf`는 참조 값 중 최솟값을 나타낸다.

| 속성 | 경계 | 제약값 |
|---|---|---|
| `CriticalOverTemperatureThreshold` | 최솟값 | `maxOf(CriticalUnderTemperatureThreshold, MajorOverTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MajorOverTemperatureThreshold` | 최솟값 | `maxOf(MajorUnderTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MinorOverTemperatureThreshold` | 최솟값 | `MinorUnderTemperatureThreshold + 1` |
| `MinorUnderTemperatureThreshold` | 최댓값 | `MinorOverTemperatureThreshold - 1` |
| `MajorUnderTemperatureThreshold` | 최댓값 | `minOf(MajorOverTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |
| `CriticalUnderTemperatureThreshold` | 최댓값 | `minOf(CriticalOverTemperatureThreshold, MajorUnderTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |

### 명령

#### `SetTemperatureAlarmThresholds`

| 항목 | 값 |
|---|---|
| ID | `0x80` |
| 방향 | `commandToServer` |
| 응답 설정 | `response="Y"` |
| 호출 권한 | `invokePrivilege="operate"` |
| 필수 조건 | `OCRIADJ` OR `OMAJADJ` OR `OMINADJ` OR `UMINADJ` OR `UMAJADJ` OR `UCRIADJ` |

각 필드의 타입은 `temperature`이다. 필드는 해당 기능 조건에 따라 선택 사항이며, 모두 `choice="b" more="true" min="1"`로 묶여 있어 하나 이상을 포함해야 한다.

| 필드 ID | 이름 | 선택 조건 | 기본값 |
|---|---|---|---|
| `0` | `CriticalOverTemperatureThreshold` | `OCRIADJ` | 명시되지 않음 |
| `1` | `MajorOverTemperatureThreshold` | `OMAJADJ` | 명시되지 않음 |
| `2` | `MinorOverTemperatureThreshold` | `OMINADJ` | `32765` |
| `3` | `MinorUnderTemperatureThreshold` | `UMINADJ` | `-27314` |
| `4` | `MajorUnderTemperatureThreshold` | `UMAJADJ` | 명시되지 않음 |
| `5` | `CriticalUnderTemperatureThreshold` | `UCRIADJ` | 명시되지 않음 |

#### 명령 필드 제약

아래 식에서 참조하는 이름은 모두 명령 필드 이름이다.

| 필드 | 경계 | 제약값 |
|---|---|---|
| `CriticalOverTemperatureThreshold` | 최솟값 | `maxOf(CriticalUnderTemperatureThreshold, MajorOverTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MajorOverTemperatureThreshold` | 최솟값 | `maxOf(MajorUnderTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MinorOverTemperatureThreshold` | 최솟값 | `MinorUnderTemperatureThreshold + 1` |
| `MinorUnderTemperatureThreshold` | 최댓값 | `MinorOverTemperatureThreshold - 1` |
| `MajorUnderTemperatureThreshold` | 최댓값 | `minOf(MajorOverTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |
| `CriticalUnderTemperatureThreshold` | 최댓값 | `minOf(CriticalOverTemperatureThreshold, MajorUnderTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |

## 관련 페이지

**사용 기기**

- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
