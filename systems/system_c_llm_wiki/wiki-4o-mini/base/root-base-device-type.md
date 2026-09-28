---
entity: Root/Base Device Type
ids: []
source_paths: ['data_model/1.7/device_types/BaseDeviceType.xml', 'data_model/1.7/device_types/RootNodeDeviceType.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-4o-mini
---

## 개요
이 문서는 Base Device Type 및 Root Node Device Type의 Device Type 정의를 포함합니다. 두 Device Type 모두 특별한 조건 및 클러스터 구성을 요구합니다.

## 스펙

### Base Device Type
- **이름**: Base Device Type
- **버전**: 3
- **Revision History**:
  - 1: Initial revision
  - 2: Duplicate condition replaces Multiple condition
  - 3: Removed certification program conditions

- **조건**:
  - Ethernet
  - Wi-Fi
  - Thread
  - IP
  - TCP
  - UDP
  - IPv4
  - IPv6
  - LanguageLocale
  - TimeLocale
  - UnitLocale
  - SIT
  - LIT
  - Active
  - Node
  - App
  - Simple
  - Dynamic
  - Composed
  - Client
  - Server
  - Duplicate
  - BridgedPowerSourceInfo

- **클러스터**:
  - 클러스터 ID: 0x001D, 이름: Descriptor, 측: server
  - 클러스터 ID: 0x001E, 이름: Binding, 측: server
  - 클러스터 ID: 0x0040, 이름: Fixed Label, 측: server
  - 클러스터 ID: 0x0041, 이름: User Label, 측: server

### Root Node
- **이름**: Root Node
- **ID**: 0x0016
- **버전**: 5
- **Revision History**:
  - 1: Initial revision
  - 2: Added Power Source to device type; Deprecated Power Source Configuration
  - 3: Added restriction on Managed Device feature of Access Control cluster
  - 4: Added conditions and cluster requirements for Time Sync, TLS, and Power Source clusters
  - 5: Added conditions and cluster requirements for the Groupcast cluster

- **분류**: node
- **조건**:
  - CustomNetworkConfig
  - ManagedAclAllowed
  - TimeSyncCond
  - TimeSyncWithClientCond
  - TimeSyncWithNTPCCond
  - TimeSyncWithTZCond
  - TLSCertificatesCond
  - TLSClientCond
  - PowerSourceCond
  - ACLExtensionCond
  - GroupcastListenerCond
  - GroupcastSenderCond

- **클러스터**:
  - 클러스터 ID: 0x001F, 이름: Access Control, 측: server
  - 클러스터 ID: 0x0028, 이름: Basic Information, 측: server
  - 클러스터 ID: 0x002B, 이름: Localization Configuration, 측: server
  - 클러스터 ID: 0x002C, 이름: Time Format Localization, 측: server
  - 클러스터 ID: 0x002D, 이름: Unit Localization, 측: server
  - 클러스터 ID: 0x002E, 이름: Power Source Configuration, 측: server
  - 클러스터 ID: 0x0030, 이름: General Commissioning, 측: server
  - 클러스터 ID: 0x0031, 이름: Network Commissioning, 측: server
  - 클러스터 ID: 0x0032, 이름: Diagnostic Logs, 측: server
  - 클러스터 ID: 0x0033, 이름: General Diagnostics, 측: server
  - 클러스터 ID: 0x0034, 이름: Software Diagnostics, 측: server
  - 클러스터 ID: 0x0035, 이름: Thread Network Diagnostics, 측: server
  - 클러스터 ID: 0x0036, 이름: Wi-Fi Network Diagnostics, 측: server
  - 클러스터 ID: 0x0037, 이름: Ethernet Network Diagnostics, 측: server
  - 클러스터 ID: 0x0038, 이름: Time Synchronization, 측: server
  - 클러스터 ID: 0x0038, 이름: Time Synchronization, 측: client
  - 클러스터 ID: 0x003C, 이름: Administrator Commissioning, 측: server
  - 클러스터 ID: 0x003E, 이름: Operational Credentials, 측: server
  - 클러스터 ID: 0x003F, 이름: Group Key Management, 측: server
  - 클러스터 ID: 0x0046, 이름: ICD Management, 측: server
  - 클러스터 ID: 0x0065, 이름: Groupcast, 측: server
  - 클러스터 ID: 0x0801, 이름: TLS Certificate Management, 측: server
  - 클러스터 ID: 0x0802, 이름: TLS Client Management, 측: server

## 관련 문서
- None