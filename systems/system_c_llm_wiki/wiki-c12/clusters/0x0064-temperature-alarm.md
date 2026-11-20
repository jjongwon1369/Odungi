---
entity: Temperature Alarm
ids: ['0x0064']
source_paths: ['data_model/1.7/clusters/TemperatureAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Temperature Alarm

## 개요

`Temperature Alarm`은 온도 측정값이 임계값을 초과하거나 미만일 때 알람을 활성화하는 클러스터이다. `Alarm Base`를 기반으로 하며, 임계값 조정 기능을 선택적으로 지원한다.

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

| 비트 | 코드 | 이름 | 기능 | 적합성 조건 |
|---|---|---|---|---|
| `20` | `OVER` | `OverTemperature` | 온도 측정값이 임계값을 초과할 때 알람 활성화 | 선택, 그룹 `a` |
| `21` | `UNDER` | `UnderTemperature` | 온도 측정값이 임계값 미만일 때 알람 활성화 | 선택, 그룹 `a` |
| `22` | `MAJOR` | `MajorThreshold` | 주요 임계값 지원 | 선택 |
| `23` | `MINOR` | `MinorThreshold` | 경미 임계값 지원 | `MAJOR` 조건에서 선택 |
| `24` | `OCRIADJ` | `OverCriticalAdjustable` | 상한 임계 임계값 조정 | `OVER` 조건에서 선택 |
| `25` | `OMAJADJ` | `OverMajorAdjustable` | 상한 주요 임계값 조정 | `OVER` 및 `MAJOR` 조건에서 선택 |
| `26` | `OMINADJ` | `OverMinorAdjustable` | 상한 경미 임계값 조정 | `OVER` 및 `MINOR` 조건에서 선택 |
| `27` | `UMINADJ` | `UnderMinorAdjustable` | 하한 경미 임계값 조정 | `UNDER` 및 `MINOR` 조건에서 선택 |
| `28` | `UMAJADJ` | `UnderMajorAdjustable` | 하한 주요 임계값 조정 | `UNDER` 및 `MAJOR` 조건에서 선택 |
| `29` | `UCRIADJ` | `UnderCriticalAdjustable` | 하한 임계 임계값 조정 | `UNDER` 조건에서 선택 |

그룹 `a`는 `choice="a"`, `more="true"`, `min="1"`로 정의되어 있으므로, `OVER`와 `UNDER` 중 하나 이상을 지원해야 한다.

### 데이터 타입

#### AlarmBitmap

모든 비트 필드는 `mandatoryConform`으로 정의된다.

| 비트 | 이름 | 의미 |
|---|---|---|
| `0` | `CriticalOverTemperatureAlarm` | 측정 온도가 임계 수준의 상한 임계값을 초과함 |
| `1` | `MajorOverTemperatureAlarm` | 측정 온도가 주요 수준의 상한 임계값을 초과함 |
| `2` | `MinorOverTemperatureAlarm` | 측정 온도가 경미 수준의 상한 임계값을 초과함 |
| `3` | `MinorUnderTemperatureAlarm` | 측정 온도가 경미 수준의 하한 임계값 미만임 |
| `4` | `MajorUnderTemperatureAlarm` | 측정 온도가 주요 수준의 하한 임계값 미만임 |
| `5` | `CriticalUnderTemperatureAlarm` | 측정 온도가 임계 수준의 하한 임계값 미만임 |

### 속성

모든 속성의 타입은 `temperature`이며, 접근 설정은 `read="true"`, `readPrivilege="view"`이다.

| ID | 이름 | 필수 지원 조건 |
|---|---|---|
| `0x0080` | `CriticalOverTemperatureThreshold` | `OVER` |
| `0x0081` | `MajorOverTemperatureThreshold` | `OVER` 및 `MAJOR` |
| `0x0082` | `MinorOverTemperatureThreshold` | `OVER` 및 `MINOR` |
| `0x0083` | `MinorUnderTemperatureThreshold` | `UNDER` 및 `MINOR` |
| `0x0084` | `MajorUnderTemperatureThreshold` | `UNDER` 및 `MAJOR` |
| `0x0085` | `CriticalUnderTemperatureThreshold` | `UNDER` |

#### 속성 값 제약

아래 참조 대상은 모두 속성이다.

| 속성 | 제약 |
|---|---|
| `CriticalOverTemperatureThreshold` | 최솟값: `CriticalUnderTemperatureThreshold`, `MajorOverTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값에 `1`을 더한 값 |
| `MajorOverTemperatureThreshold` | 최솟값: `MajorUnderTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값에 `1`을 더한 값 |
| `MinorOverTemperatureThreshold` | 최솟값: `MinorUnderTemperatureThreshold`에 `1`을 더한 값 |
| `MinorUnderTemperatureThreshold` | 최댓값: `MinorOverTemperatureThreshold`에서 `1`을 뺀 값 |
| `MajorUnderTemperatureThreshold` | 최댓값: `MajorOverTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값에서 `1`을 뺀 값 |
| `CriticalUnderTemperatureThreshold` | 최댓값: `CriticalOverTemperatureThreshold`, `MajorUnderTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값에서 `1`을 뺀 값 |

### 명령

#### SetTemperatureAlarmThresholds

| 항목 | 값 |
|---|---|
| 명령 ID | `0x80` |
| 이름 | `SetTemperatureAlarmThresholds` |
| 방향 | `commandToServer` |
| 응답 설정 | `response="Y"` |
| 호출 권한 | `invokePrivilege="operate"` |

`OCRIADJ`, `OMAJADJ`, `OMINADJ`, `UMINADJ`, `UMAJADJ`, `UCRIADJ` 중 하나 이상이 지원되면 이 명령은 필수이다.

##### 필드

모든 필드의 타입은 `temperature`이다. 각 필드는 해당 기능 조건에서 선택적이며, 공통으로 `choice="b"`, `more="true"`, `min="1"`이 지정되어 있어 그룹 `b`에서 하나 이상을 포함해야 한다.

| ID | 이름 | 기능 조건 | 원문에 명시된 기본값 |
|---|---|---|---|
| `0` | `CriticalOverTemperatureThreshold` | `OCRIADJ` | — |
| `1` | `MajorOverTemperatureThreshold` | `OMAJADJ` | — |
| `2` | `MinorOverTemperatureThreshold` | `OMINADJ` | `32765` |
| `3` | `MinorUnderTemperatureThreshold` | `UMINADJ` | `-27314` |
| `4` | `MajorUnderTemperatureThreshold` | `UMAJADJ` | — |
| `5` | `CriticalUnderTemperatureThreshold` | `UCRIADJ` | — |

##### 필드 값 제약

아래 참조 대상은 모두 명령 필드이다.

| 필드 | 제약 |
|---|---|
| `CriticalOverTemperatureThreshold` | 최솟값: `CriticalUnderTemperatureThreshold`, `MajorOverTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값에 `1`을 더한 값 |
| `MajorOverTemperatureThreshold` | 최솟값: `MajorUnderTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값에 `1`을 더한 값 |
| `MinorOverTemperatureThreshold` | 최솟값: `MinorUnderTemperatureThreshold`에 `1`을 더한 값 |
| `MinorUnderTemperatureThreshold` | 최댓값: `MinorOverTemperatureThreshold`에서 `1`을 뺀 값 |
| `MajorUnderTemperatureThreshold` | 최댓값: `MajorOverTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값에서 `1`을 뺀 값 |
| `CriticalUnderTemperatureThreshold` | 최댓값: `CriticalOverTemperatureThreshold`, `MajorUnderTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값에서 `1`을 뺀 값 |

## 관련 페이지

**사용 기기**

- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
