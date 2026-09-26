---
entity: Temperature Alarm
ids: ['0x0064']
source_paths: ['data_model/1.7/clusters/TemperatureAlarm.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
compiled_by: openai/gpt-5.6-luna
---

## 스펙

### 원문

`data_model/1.7/clusters/TemperatureAlarm.xml`

### 클러스터 정보

| 항목 | 값 |
|---|---|
| Cluster name | `Temperature Alarm Cluster` |
| Cluster ID | `0x0064` |
| Revision | `1` |
| Cluster ID name | `Temperature Alarm` |
| Conformance | Provisional |
| Hierarchy | `derived` |
| Base cluster | `Alarm Base` |
| Role | `application` |
| PICS code | `TEMPALM` |
| Scope | `Endpoint` |

### 기능

| Bit | Code | Name | Summary | Conformance |
|---:|---|---|---|---|
| 20 | `OVER` | `OverTemperature` | Supports activating alarms when a temperature measurement goes over a threshold | Optional, `min="1"` |
| 21 | `UNDER` | `UnderTemperature` | Supports activating alarms when a temperature measurement goes under a threshold | Optional, `min="1"` |
| 22 | `MAJOR` | `MajorThreshold` | Supports the major threshold for alarms | Optional |
| 23 | `MINOR` | `MinorThreshold` | Supports the minor threshold for alarms | `MAJOR` 필요 |
| 24 | `OCRIADJ` | `OverCriticalAdjustable` | Supports the ability to adjust the over critical temperature threshold | `OVER` 필요 |
| 25 | `OMAJADJ` | `OverMajorAdjustable` | Supports the ability to adjust the over major temperature threshold | `OVER` 및 `MAJOR` 필요 |
| 26 | `OMINADJ` | `OverMinorAdjustable` | Supports the ability to adjust the over minor temperature threshold | `OVER` 및 `MINOR` 필요 |
| 27 | `UMINADJ` | `UnderMinorAdjustable` | Supports the ability to adjust the under minor temperature threshold | `UNDER` 및 `MINOR` 필요 |
| 28 | `UMAJADJ` | `UnderMajorAdjustable` | Supports the ability to adjust the under major temperature threshold | `UNDER` 및 `MAJOR` 필요 |
| 29 | `UCRIADJ` | `UnderCriticalAdjustable` | Supports the ability to adjust the under critical temperature threshold | `UNDER` 필요 |

### 데이터 타입

#### `AlarmBitmap`

| Bit | Name | 설명 | Conformance |
|---:|---|---|---|
| 0 | `CriticalOverTemperatureAlarm` | 측정된 온도가 critical threshold보다 높음 | Mandatory |
| 1 | `MajorOverTemperatureAlarm` | 측정된 온도가 major threshold보다 높음 | Mandatory |
| 2 | `MinorOverTemperatureAlarm` | 측정된 온도가 minor threshold보다 높음 | Mandatory |
| 3 | `MinorUnderTemperatureAlarm` | 측정된 온도가 minor threshold보다 낮음 | Mandatory |
| 4 | `MajorUnderTemperatureAlarm` | 측정된 온도가 major threshold보다 낮음 | Mandatory |
| 5 | `CriticalUnderTemperatureAlarm` | 측정된 온도가 critical threshold보다 낮음 | Mandatory |

### 속성

모든 속성의 타입은 `temperature`이며, 읽기 권한은 `view`입니다.

| ID | Name | Conformance | 제약 조건 |
|---|---|---|---|
| `0x0080` | `CriticalOverTemperatureThreshold` | `OVER` 필요 | `CriticalUnderTemperatureThreshold`, `MajorOverTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값보다 `1` 이상이어야 함 |
| `0x0081` | `MajorOverTemperatureThreshold` | `OVER` 및 `MAJOR` 필요 | `MajorUnderTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값보다 `1` 이상이어야 함 |
| `0x0082` | `MinorOverTemperatureThreshold` | `OVER` 및 `MINOR` 필요 | `MinorUnderTemperatureThreshold`보다 `1` 이상이어야 함 |
| `0x0083` | `MinorUnderTemperatureThreshold` | `UNDER` 및 `MINOR` 필요 | `MinorOverTemperatureThreshold`보다 `1` 이하여야 함 |
| `0x0084` | `MajorUnderTemperatureThreshold` | `UNDER` 및 `MAJOR` 필요 | `MajorOverTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값보다 `1` 이하여야 함 |
| `0x0085` | `CriticalUnderTemperatureThreshold` | `UNDER` 필요 | `CriticalOverTemperatureThreshold`, `MajorUnderTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값보다 `1` 이하여야 함 |

#### 속성 제약 조건

- `CriticalOverTemperatureThreshold`의 최솟값:

  ```text
  max(
    CriticalUnderTemperatureThreshold,
    MajorOverTemperatureThreshold,
    MinorOverTemperatureThreshold
  ) + 1
  ```

- `MajorOverTemperatureThreshold`의 최솟값:

  ```text
  max(
    MajorUnderTemperatureThreshold,
    MinorOverTemperatureThreshold
  ) + 1
  ```

- `MinorOverTemperatureThreshold`의 최솟값:

  ```text
  MinorUnderTemperatureThreshold + 1
  ```

- `MinorUnderTemperatureThreshold`의 최댓값:

  ```text
  MinorOverTemperatureThreshold - 1
  ```

- `MajorUnderTemperatureThreshold`의 최댓값:

  ```text
  min(
    MajorOverTemperatureThreshold,
    MinorUnderTemperatureThreshold
  ) - 1
  ```

- `CriticalUnderTemperatureThreshold`의 최댓값:

  ```text
  min(
    CriticalOverTemperatureThreshold,
    MajorUnderTemperatureThreshold,
    MinorUnderTemperatureThreshold
  ) - 1
  ```

### 명령

#### `SetTemperatureAlarmThresholds`

| 항목 | 값 |
|---|---|
| Command ID | `0x80` |
| Direction | `commandToServer` |
| Response | `Y` |
| Invoke privilege | `operate` |
| Conformance | `OCRIADJ`, `OMAJADJ`, `OMINADJ`, `UMINADJ`, `UMAJADJ`, `UCRIADJ` 중 하나 이상 필요 |

#### 필드

| ID | Name | Type | Default | 선택 조건 | 제약 조건 |
|---:|---|---|---|---|---|
| 0 | `CriticalOverTemperatureThreshold` | `temperature` | — | `OCRIADJ` | `CriticalUnderTemperatureThreshold`, `MajorOverTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값보다 `1` 이상 |
| 1 | `MajorOverTemperatureThreshold` | `temperature` | — | `OMAJADJ` | `MajorUnderTemperatureThreshold`, `MinorOverTemperatureThreshold` 중 최댓값보다 `1` 이상 |
| 2 | `MinorOverTemperatureThreshold` | `temperature` | `32765` | `OMINADJ` | `MinorUnderTemperatureThreshold`보다 `1` 이상 |
| 3 | `MinorUnderTemperatureThreshold` | `temperature` | `-27314` | `UMINADJ` | `MinorOverTemperatureThreshold`보다 `1` 이하 |
| 4 | `MajorUnderTemperatureThreshold` | `temperature` | — | `UMAJADJ` | `MajorOverTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값보다 `1` 이하 |
| 5 | `CriticalUnderTemperatureThreshold` | `temperature` | — | `UCRIADJ` | `CriticalOverTemperatureThreshold`, `MajorUnderTemperatureThreshold`, `MinorUnderTemperatureThreshold` 중 최솟값보다 `1` 이하 |

각 필드는 `optionalConform`이며 `choice="b"`, `more="true"`, `min="1"` 조건을 사용합니다.

#### 명령 필드 제약 조건

- `CriticalOverTemperatureThreshold`:

  ```text
  max(
    CriticalUnderTemperatureThreshold,
    MajorOverTemperatureThreshold,
    MinorOverTemperatureThreshold
  ) + 1
  ```

- `MajorOverTemperatureThreshold`:

  ```text
  max(
    MajorUnderTemperatureThreshold,
    MinorOverTemperatureThreshold
  ) + 1
  ```

- `MinorOverTemperatureThreshold`:

  ```text
  MinorUnderTemperatureThreshold + 1
  ```

- `MinorUnderTemperatureThreshold`:

  ```text
  MinorOverTemperatureThreshold - 1
  ```

- `MajorUnderTemperatureThreshold`:

  ```text
  min(
    MajorOverTemperatureThreshold,
    MinorUnderTemperatureThreshold
  ) - 1
  ```

- `CriticalUnderTemperatureThreshold`:

  ```text
  min(
    CriticalOverTemperatureThreshold,
    MajorUnderTemperatureThreshold,
    MinorUnderTemperatureThreshold
  ) - 1
  ```

## 관련 페이지

**사용 기기**

- [Temperature Controlled Cabinet](../device-types/temperature-controlled-cabinet.md)
