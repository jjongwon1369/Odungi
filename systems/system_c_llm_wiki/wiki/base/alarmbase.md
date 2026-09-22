---
entity: AlarmBase
ids: []
source_paths: ['src/app/clusters/alarm-base-server/Delegate.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.h', 'src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp', 'src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h', 'data_model/1.7/clusters/AlarmBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
---

## 개요

Alarm Base Cluster (`AlarmBase`)는 알람 관리 기능을 제공하는 기본 클러스터입니다.

- **Classification**: Base, Application (PICS: `ALARM`, Scope: Endpoint)
- **Revision**: 2

## 스펙

### Features

| Bit | Code | Name | Description | Conformance |
| --- | --- | --- | --- | --- |
| 0 | `RESET` | Reset | Supports the ability to reset alarms | Optional |

### Data Types

- **Bitmap**: `AlarmBitmap`

### Attributes

| ID | Name | Type | Access | Quality | Conformance |
| --- | --- | --- | --- | --- | --- |
| `0x0000` | `Mask` | `AlarmBitmap` | Read (View) | - | Mandatory |
| `0x0001` | `Latch` | `AlarmBitmap` | Read (View) | Fixed | Mandatory (`RESET`) |
| `0x0002` | `State` | `AlarmBitmap` | Read (View) | - | Mandatory |
| `0x0003` | `Supported` | `AlarmBitmap` | Read (View) | Fixed | Mandatory |

### Commands

#### Received Commands (Direction: `commandToServer`)

- **`0x00`: `Reset`**
  - **Access**: Invoke Privilege: `operate`
  - **Conformance**: Mandatory (`RESET`)
  - **Fields**:
    - `0`: `Alarms` (`AlarmBitmap`, Mandatory)

- **`0x01`: `ModifyEnabledAlarms`**
  - **Access**: Invoke Privilege: `operate`
  - **Conformance**: Optional
  - **Fields**:
    - `0`: `Mask` (`AlarmBitmap`, Mandatory)

### Events

- **`0x00`: `Notify`**
  - **Priority**: `info`
  - **Access**: Read Privilege: `view`
  - **Conformance**: Mandatory
  - **Fields**:
    - `0`: `Active` (`AlarmBitmap`, Mandatory)
    - `1`: `Inactive` (`AlarmBitmap`, Mandatory)
    - `2`: `State` (`AlarmBitmap`, Mandatory)
    - `3`: `Mask` (`AlarmBitmap`, Mandatory)

## 구현

### 주요 파일

- `src/app/clusters/alarm-base-server/Delegate.h`
- `src/app/clusters/alarm-base-server/AlarmBaseCluster.h`
- `src/app/clusters/alarm-base-server/AlarmBaseCluster.cpp`
- `src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h`

### 주요 클래스 및 타입

#### Delegate Interface (`chip::app::Clusters::AlarmBase::Delegate`)

`src/app/clusters/alarm-base-server/Delegate.h`에 정의된 응용 프로그램 위임 클래스입니다.

- `virtual bool ModifyEnabledAlarms(AlarmMap mask)`
- `virtual bool ResetAlarms(AlarmMap alarms)`

#### AlarmBaseCluster (`chip::app::Clusters::AlarmBaseCluster`)

`src/app/clusters/alarm-base-server/AlarmBaseCluster.h`에 정의된 서버 클러스터 기본 구현체입니다.

- **Config**:
  - `AlarmBase::Delegate & delegate`
  - `BitMask<AlarmBase::Feature> feature`
  - `AlarmBase::AlarmMap supported`
  - `AlarmBase::AlarmMap latch`
  - `bool supportsModifyEnabledAlarms`

- **Application-facing API**:
  - `AlarmBase::AlarmMap GetMask() const`
  - `AlarmBase::AlarmMap GetState() const`
  - `AlarmBase::AlarmMap GetSupported() const`
  - `AlarmBase::AlarmMap GetLatch() const`
  - `BitMask<AlarmBase::Feature> GetFeatures() const`
  - `Protocols::InteractionModel::Status SetMask(const AlarmBase::AlarmMap & mask)`
  - `Protocols::InteractionModel::Status SetState(const AlarmBase::AlarmMap & newState)`
  - `Protocols::InteractionModel::Status ResetLatchedAlarms(const AlarmBase::AlarmMap & alarms)`

- **Protected / Internal API**:
  - `virtual void SendNotifyEvent(AlarmBase::AlarmMap becameActive, AlarmBase::AlarmMap becameInactive, AlarmBase::AlarmMap newState, AlarmBase::AlarmMap mask) = 0`
  - `Protocols::InteractionModel::Status SetStateIgnoringLatch(const AlarmBase::AlarmMap & newState)`
  - `DataModel::ActionReturnStatus HandleReset(const AlarmBase::AlarmMap & alarms)`
  - `DataModel::ActionReturnStatus HandleModifyEnabledAlarms(const AlarmBase::AlarmMap & mask)`

#### Types 및 Objects

`src/app/clusters/alarm-base-server/alarm-base-cluster-objects.h`에 정의되어 있습니다.

- `ClusterEntry` struct (`ClusterId id`, `uint32_t revision`)
- `AlarmBitmap` enum (`uint32_t`)
- `AlarmMap` (`BitMask<AlarmBitmap>`)
- `Feature` (`DishwasherAlarm::Feature`)
- Attributes 및 Commands 별칭 정의 (`Mask`, `Latch`, `State`, `Supported`, `Reset`, `ModifyEnabledAlarms`, `Notify` 등)