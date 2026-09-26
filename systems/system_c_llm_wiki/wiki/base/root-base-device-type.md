---
entity: Root/Base Device Type
ids: []
source_paths: ['data_model/1.7/device_types/BaseDeviceType.xml', 'data_model/1.7/device_types/RootNodeDeviceType.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-5.6-luna
---

# Root/Base Device Type

## 스펙

### Base Device Type

- 파일: `data_model/1.7/device_types/BaseDeviceType.xml`
- `name`: `Base Device Type`
- `revision`: `3`

#### revisionHistory

| revision | summary |
|---|---|
| `1` | Initial revision |
| `2` | Duplicate condition replaces Multiple condition |
| `3` | Removed certification program conditions |

#### conditions

| condition | summary |
|---|---|
| `Ethernet` | The node supports an Ethernet LAN interface |
| `Wi-Fi` | The node supports a Wi-Fi interface |
| `Thread` | The node supports a Thread interface |
| `IP` | The node supports an IP interface |
| `TCP` | The node supports TCP on each IP interface |
| `UDP` | The node supports UDP on each IP interface |
| `IPv4` | The node supports IPv4 on each IP interface |
| `IPv6` | The node supports IPv6 on each IP interface |
| `LanguageLocale` | The node supports localization for conveying text to the user |
| `TimeLocale` | The node supports localization for conveying time to the user |
| `UnitLocale` | The node supports localization for conveying units of measure to the user |
| `SIT` | The node is a short idle time intermittently connected device |
| `LIT` | The node is a long idle time intermittently connected device |
| `Active` | The node is always able to communicate |
| `Node` | the device type is classified as a Node device type (see Data Model specification) |
| `App` | the device type is classified as an Application device type (see Data Model specification) |
| `Simple` | the device type is classified as a Simple device type (see Data Model specification) |
| `Dynamic` | the device type is classified as a Dynamic device type (see Data Model specification) |
| `Composed` | the device type is composed of 2 or more device types (see System Model specification) |
| `Client` | there exists a client application cluster on the endpoint |
| `Server` | there exists a server application cluster on the endpoint |
| `Duplicate` | the endpoint and at least one of its siblings have overlap in application device type(s) |
| `BridgedPowerSourceInfo` | the endpoint represents a Bridged Device, for which information about the state of its power source is available to the Bridge |

#### clusters

| ID | name | side | 적합성 |
|---|---|---|---|
| `0x001D` | `Descriptor` | `server` | 필수 |
| `0x001E` | `Binding` | `server` | `Simple` 및 `Client` 조건에서 필수 |
| `0x0040` | `Fixed Label` | `server` | 선택 |
| `0x0041` | `User Label` | `server` | 선택 |

- `Descriptor` (`0x001D`)
  - feature `TAGLIST`: `Duplicate` 조건에서 필수
- `Binding` (`0x001E`)
  - `Simple` AND `Client` 조건에서 필수

---

### Root Node Device Type

- 파일: `data_model/1.7/device_types/RootNodeDeviceType.xml`
- `id`: `0x0016`
- `name`: `Root Node`
- `revision`: `5`
- `classification`: `node`
- `scope`: `node`

#### revisionHistory

| revision | summary |
|---|---|
| `1` | Initial revision |
| `2` | Added Power Source to device type; Deprecated Power Source Configuration |
| `3` | Added restriction on Managed Device feature of Access Control cluster |
| `4` | Added conditions and cluster requirements for Time Sync, TLS, and Power Source clusters |
| `5` | Added conditions and cluster requirements for the Groupcast cluster |

#### conditions

| condition | summary |
|---|---|
| `CustomNetworkConfig` | The node only supports out-of-band-configured networking (e.g. rich user interface, manufacturer-specific means, custom commissioning flows, or future IP-compliant network technology not yet directly supported by `NetworkCommissioning` cluster). |
| `ManagedAclAllowed` | The node has at least one endpoint where some Device Type present on the endpoint has a Device Library element requirement table entry that sets this condition to true. |
| `TimeSyncCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to use Time Synchronization support. |
| `TimeSyncWithClientCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to use Time Synchronization support with Client cluster support, and the TimeSyncClient feature. |
| `TimeSyncWithNTPCCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to use Time Synchronization support with the NTPClient feature. |
| `TimeSyncWithTZCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to use Time Synchronization support with the TimeZone feature. |
| `TLSCertificatesCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to use TLS Certificate Management. Since TLS requires basic Time Sync support, this will include that dependency. |
| `TLSClientCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to use TLS Client Management. Since TLS requires basic Time Sync support, this will include that dependency. |
| `PowerSourceCond` | The node has at least one endpoint where some Device Type present on the endpoint needs to have Power Source be on the Root Node. |
| `ACLExtensionCond` | The node has at least one endpoint where some Device Type present on the endpoint needs the Access Control instance to have the Extension attribute. |
| `GroupcastListenerCond` | The node has at least one endpoint where some Device Type present on the endpoint needs the Groupcast Server cluster instance with the Listener feature. This condition SHALL be supported if any endpoint implements the Groups cluster server on an endpoint. |
| `GroupcastSenderCond` | The node has at least one endpoint where some Device Type present on the endpoint needs the Groupcast Server cluster instance with the Sender feature. This condition SHALL be supported if any endpoint implements the Bindings cluster server on an endpoint. |

#### clusters

| ID | name | side | 적합성 및 비고 |
|---|---|---|---|
| `0x001F` | `Access Control` | `server` | singleton, 필수 |
| `0x0028` | `Basic Information` | `server` | singleton, 필수 |
| `0x002B` | `Localization Configuration` | `server` | singleton, `LanguageLocale` 조건에서 필수 |
| `0x002C` | `Time Format Localization` | `server` | singleton, `TimeLocale` 조건에서 필수 |
| `0x002D` | `Unit Localization` | `server` | singleton, `UnitLocale` 조건에서 필수 |
| `0x002E` | `Power Source Configuration` | `server` | singleton, 선택 및 deprecated |
| `0x0030` | `General Commissioning` | `server` | singleton, 필수 |
| `0x0031` | `Network Commissioning` | `server` | `CustomNetworkConfig`가 아닌 경우 필수 |
| `0x0032` | `Diagnostic Logs` | `server` | singleton, 선택 |
| `0x0033` | `General Diagnostics` | `server` | singleton, 필수 |
| `0x0034` | `Software Diagnostics` | `server` | singleton, 선택 |
| `0x0035` | `Thread Network Diagnostics` | `server` | `Thread` 조건에서 선택 |
| `0x0036` | `Wi-Fi Network Diagnostics` | `server` | `Wi-Fi` 조건에서 선택 |
| `0x0037` | `Ethernet Network Diagnostics` | `server` | `Ethernet` 조건에서 선택 |
| `0x0038` | `Time Synchronization` | `server` | singleton, 조건에 따른 필수 또는 선택 |
| `0x0038` | `Time Synchronization` | `client` | singleton, `TimeSyncWithClientCond` 조건에 따른 필수 또는 선택 |
| `0x003C` | `Administrator Commissioning` | `server` | singleton, 필수 |
| `0x003E` | `Operational Credentials` | `server` | singleton, 필수 |
| `0x003F` | `Group Key Management` | `server` | singleton, 필수 |
| `0x0046` | `ICD Management` | `server` | singleton, `SIT` 또는 `LIT` 조건에서 필수 |
| `0x0065` | `Groupcast` | `server` | singleton, 조건에 따른 필수 또는 선택 |
| `0x0801` | `TLS Certificate Management` | `server` | singleton, `TLSCertificatesCond` 조건에서 필수 |
| `0x0802` | `TLS Client Management` | `server` | singleton, `TLSClientCond` 조건에서 필수 |

#### Access Control (`0x001F`)

- `singleton`: `true`
- 필수 cluster
- feature:
  - `MNGD`: `ManagedAclAllowed` 조건에서 선택
  - `AUX`: `GroupcastListenerCond` 조건에서 필수
- attribute:
  - `0x0001` `Extension`: `ACLExtensionCond` 조건에서 필수

#### Localization 및 Commissioning clusters

다음 clusters는 지정된 조건에 따라 적용됩니다.

- `Basic Information` (`0x0028`)
  - singleton
  - 필수
- `Localization Configuration` (`0x002B`)
  - singleton
  - `LanguageLocale` 조건에서 필수
- `Time Format Localization` (`0x002C`)
  - singleton
  - `TimeLocale` 조건에서 필수
- `Unit Localization` (`0x002D`)
  - singleton
  - `UnitLocale` 조건에서 필수
- `Power Source Configuration` (`0x002E`)
  - singleton
  - 선택
  - deprecated
- `General Commissioning` (`0x0030`)
  - singleton
  - 필수
- `Network Commissioning` (`0x0031`)
  - `CustomNetworkConfig` 조건이 아닌 경우 필수

#### Diagnostic clusters

- `Diagnostic Logs` (`0x0032`)
  - singleton
  - 선택
- `General Diagnostics` (`0x0033`)
  - singleton
  - 필수
- `Software Diagnostics` (`0x0034`)
  - singleton
  - 선택
- `Thread Network Diagnostics` (`0x0035`)
  - `Thread` 조건에서 선택
- `Wi-Fi Network Diagnostics` (`0x0036`)
  - `Wi-Fi` 조건에서 선택
- `Ethernet Network Diagnostics` (`0x0037`)
  - `Ethernet` 조건에서 선택

#### Time Synchronization (`0x0038`, `server`)

- `singleton`: `true`
- 다음 조건 중 하나에 해당하면 필수:
  - `TimeSyncCond`
  - `TimeSyncWithClientCond`
  - `TimeSyncWithNTPCCond`
  - `TimeSyncWithTZCond`
  - `TLSClientCond`
  - `TLSCertificatesCond`
- 위 조건에 해당하지 않으면 선택

features:

- `TSC`
  - `TimeSyncWithClientCond` 조건에서 필수
  - `TLSCertificatesCond` 또는 `TLSClientCond` 중 하나 이상을 선택할 수 있음
  - 그 외에는 선택
- `NTPC`
  - `TimeSyncWithNTPCCond` 조건에서 필수
  - `TLSCertificatesCond` 또는 `TLSClientCond` 중 하나 이상을 선택할 수 있음
  - 그 외에는 선택
- `TZ`
  - `TimeSyncWithTZCond` 조건에서 필수
  - 그 외에는 선택

#### Time Synchronization (`0x0038`, `client`)

- `singleton`: `true`
- `TimeSyncWithClientCond` 조건에서 필수
- 그 외에는 선택

features:

- `TSC`
  - `TimeSyncWithClientCond` 조건에서 필수
  - `TLSCertificatesCond` 또는 `TLSClientCond` 중 하나 이상을 선택할 수 있음
  - 그 외에는 선택
- `NTPC`
  - `TimeSyncWithNTPCCond` 조건에서 필수
  - `TLSCertificatesCond` 또는 `TLSClientCond` 중 하나 이상을 선택할 수 있음
  - 그 외에는 선택
- `TZ`
  - `TimeSyncWithTZCond` 조건에서 필수
  - 그 외에는 선택

#### 보안 및 그룹 관리 clusters

- `Administrator Commissioning` (`0x003C`)
  - singleton
  - 필수
- `Operational Credentials` (`0x003E`)
  - singleton
  - 필수
- `Group Key Management` (`0x003F`)
  - singleton
  - 필수
  - feature `GCAST`
    - `GroupcastListenerCond` 또는 `GroupcastSenderCond` 중 하나가 참이면 필수
    - 그 외에는 선택
- `TLS Certificate Management` (`0x0801`)
  - singleton
  - `TLSCertificatesCond` 조건에서 필수
  - 그 외에는 선택
- `TLS Client Management` (`0x0802`)
  - singleton
  - `TLSClientCond` 조건에서 필수
  - 그 외에는 선택

#### ICD Management (`0x0046`)

- `singleton`: `true`
- `SIT` 또는 `LIT` 조건에서 필수
- feature:
  - `LITS`: `LIT` 조건에서 필수

#### Groupcast (`0x0065`)

- `singleton`: `true`
- `GroupcastListenerCond` 조건에서 필수
- `GroupcastSenderCond` 조건에서 필수
- 위 조건에 해당하지 않으면 선택
- features:
  - `LN`: `GroupcastListenerCond` 조건에서 필수, 그 외에는 선택
  - `SD`: `GroupcastSenderCond` 조건에서 필수, 그 외에는 선택

## 관련 문서

- `data_model/1.7/device_types/BaseDeviceType.xml`
- `data_model/1.7/device_types/RootNodeDeviceType.xml`