---
entity: Temperature Alarm
ids: ['0x0064']
source_paths: ['data_model/1.7/clusters/TemperatureAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
---

# Temperature Alarm

## 개요

`Temperature Alarm`은 측정 온도가 임계값을 초과하거나 미만일 때 알람을 활성화하는 클러스터이다. `Alarm Base`에서 파생되며, 임계값 단계와 임계값 조정 기능을 정의한다.

| 항목 | 값 |
|---|---|
| 클러스터 이름 | `Temperature Alarm Cluster` |
| 클러스터 ID 이름 | `Temperature Alarm` |
| 클러스터 ID | `0x0064` |
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

| 비트 | 코드 | 이름 | 설명 | 적합성 조건 |
|---|---|---|---|---|
| `20` | `OVER` | `OverTemperature` | 측정 온도가 임계값을 초과할 때 알람 활성화 지원 | 선택 그룹 `a` |
| `21` | `UNDER` | `UnderTemperature` | 측정 온도가 임계값 미만일 때 알람 활성화 지원 | 선택 그룹 `a` |
| `22` | `MAJOR` | `MajorThreshold` | 주요 임계값 지원 | 선택 |
| `23` | `MINOR` | `MinorThreshold` | 경미 임계값 지원 | `MAJOR` 조건에서 선택 |
| `24` | `OCRIADJ` | `OverCriticalAdjustable` | 상한 임계 단계 온도 임계값 조정 지원 | `OVER` 조건에서 선택 |
| `25` | `OMAJADJ` | `OverMajorAdjustable` | 상한 주요 단계 온도 임계값 조정 지원 | `OVER` 및 `MAJOR` 조건에서 선택 |
| `26` | `OMINADJ` | `OverMinorAdjustable` | 상한 경미 단계 온도 임계값 조정 지원 | `OVER` 및 `MINOR` 조건에서 선택 |
| `27` | `UMINADJ` | `UnderMinorAdjustable` | 하한 경미 단계 온도 임계값 조정 지원 | `UNDER` 및 `MINOR` 조건에서 선택 |
| `28` | `UMAJADJ` | `UnderMajorAdjustable` | 하한 주요 단계 온도 임계값 조정 지원 | `UNDER` 및 `MAJOR` 조건에서 선택 |
| `29` | `UCRIADJ` | `UnderCriticalAdjustable` | 하한 임계 단계 온도 임계값 조정 지원 | `UNDER` 조건에서 선택 |

선택 그룹 `a`는 `min="1"`, `more="true"`이므로 `OVER`와 `UNDER` 중 하나 이상을 지원해야 한다.

### 데이터 타입

#### AlarmBitmap

모든 비트 필드는 `mandatoryConform`으로 정의되어 있다.

| 비트 | 이름 | 의미 |
|---|---|---|
| `0` | `CriticalOverTemperatureAlarm` | 측정 온도가 임계 단계 상한 임계값을 초과함 |
| `1` | `MajorOverTemperatureAlarm` | 측정 온도가 주요 단계 상한 임계값을 초과함 |
| `2` | `MinorOverTemperatureAlarm` | 측정 온도가 경미 단계 상한 임계값을 초과함 |
| `3` | `MinorUnderTemperatureAlarm` | 측정 온도가 경미 단계 하한 임계값 미만임 |
| `4` | `MajorUnderTemperatureAlarm` | 측정 온도가 주요 단계 하한 임계값 미만임 |
| `5` | `CriticalUnderTemperatureAlarm` | 측정 온도가 임계 단계 하한 임계값 미만임 |

### 속성

모든 속성의 타입은 `temperature`이며, 접근은 `read="true"`, `readPrivilege="view"`로 정의되어 있다.

| ID | 이름 | 필수 조건 |
|---|---|---|
| `0x0080` | `CriticalOverTemperatureThreshold` | `OVER` |
| `0x0081` | `MajorOverTemperatureThreshold` | `OVER` 및 `MAJOR` |
| `0x0082` | `MinorOverTemperatureThreshold` | `OVER` 및 `MINOR` |
| `0x0083` | `MinorUnderTemperatureThreshold` | `UNDER` 및 `MINOR` |
| `0x0084` | `MajorUnderTemperatureThreshold` | `UNDER` 및 `MAJOR` |
| `0x0085` | `CriticalUnderTemperatureThreshold` | `UNDER` |

#### 속성 제약

아래 식의 참조 대상은 속성이다. `maxOf`는 참조 값 중 최댓값, `minOf`는 최솟값을 나타낸다.

| 속성 | 제약 |
|---|---|
| `CriticalOverTemperatureThreshold` | ≥ `maxOf(CriticalUnderTemperatureThreshold, MajorOverTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MajorOverTemperatureThreshold` | ≥ `maxOf(MajorUnderTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MinorOverTemperatureThreshold` | ≥ `MinorUnderTemperatureThreshold + 1` |
| `MinorUnderTemperatureThreshold` | ≤ `MinorOverTemperatureThreshold - 1` |
| `MajorUnderTemperatureThreshold` | ≤ `minOf(MajorOverTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |
| `CriticalUnderTemperatureThreshold` | ≤ `minOf(CriticalOverTemperatureThreshold, MajorUnderTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |

### 명령

#### SetTemperatureAlarmThresholds

| 항목 | 값 |
|---|---|
| ID | `0x80` |
| 이름 | `SetTemperatureAlarmThresholds` |
| 방향 | `commandToServer` |
| 응답 지정 | `response="Y"` |
| 호출 권한 | `invokePrivilege="operate"` |

`OCRIADJ`, `OMAJADJ`, `OMINADJ`, `UMINADJ`, `UMAJADJ`, `UCRIADJ` 중 하나 이상을 지원하면 이 명령은 필수이다.

##### 필드

모든 필드의 타입은 `temperature`이다. 각 필드는 해당 기능 조건에서 선택 사항이며, 선택 그룹 `b`에 속한다. 그룹은 `min="1"`, `more="true"`로 정의되어 있어 하나 이상의 필드가 필요하다.

| ID | 이름 | 기능 조건 | 기본값 |
|---|---|---|---|
| `0` | `CriticalOverTemperatureThreshold` | `OCRIADJ` | 명시되지 않음 |
| `1` | `MajorOverTemperatureThreshold` | `OMAJADJ` | 명시되지 않음 |
| `2` | `MinorOverTemperatureThreshold` | `OMINADJ` | `32765` |
| `3` | `MinorUnderTemperatureThreshold` | `UMINADJ` | `-27314` |
| `4` | `MajorUnderTemperatureThreshold` | `UMAJADJ` | 명시되지 않음 |
| `5` | `CriticalUnderTemperatureThreshold` | `UCRIADJ` | 명시되지 않음 |

##### 필드 제약

아래 식의 참조 대상은 명령 필드이다.

| 필드 | 제약 |
|---|---|
| `CriticalOverTemperatureThreshold` | ≥ `maxOf(CriticalUnderTemperatureThreshold, MajorOverTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MajorOverTemperatureThreshold` | ≥ `maxOf(MajorUnderTemperatureThreshold, MinorOverTemperatureThreshold) + 1` |
| `MinorOverTemperatureThreshold` | ≥ `MinorUnderTemperatureThreshold + 1` |
| `MinorUnderTemperatureThreshold` | ≤ `MinorOverTemperatureThreshold - 1` |
| `MajorUnderTemperatureThreshold` | ≤ `minOf(MajorOverTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |
| `CriticalUnderTemperatureThreshold` | ≤ `minOf(CriticalOverTemperatureThreshold, MajorUnderTemperatureThreshold, MinorUnderTemperatureThreshold) - 1` |

## 관련 페이지

**사용 기기**

- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
