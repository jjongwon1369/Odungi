---
entity: Root/Base Device Type
ids: []
source_paths: ['data_model/1.7/device_types/BaseDeviceType.xml', 'data_model/1.7/device_types/RootNodeDeviceType.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
---

# Root/Base Device Type

## 개요

제공된 스펙은 `Base Device Type`과 `Root Node`의 조건, 클러스터 및 기능 요구사항을 정의한다.

| 항목 | `Base Device Type` | `Root Node` |
|---|---|---|
| 원본 | `data_model/1.7/device_types/BaseDeviceType.xml` | `data_model/1.7/device_types/RootNodeDeviceType.xml` |
| `id` | 명시되지 않음 | `0x0016` |
| `revision` | `3` | `5` |
| `classification` | 명시되지 않음 | `class="node"`, `scope="node"` |

## 스펙

### Base Device Type

출처: `data_model/1.7/device_types/BaseDeviceType.xml`

#### 변경 이력

| `revision` | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `Multiple` 조건을 `Duplicate` 조건으로 대체 |
| `3` | 인증 프로그램 조건 제거 |

#### 조건

| 조건 | 의미 |
|---|---|
| `Ethernet` | 노드가 Ethernet LAN 인터페이스를 지원한다. |
| `Wi-Fi` | 노드가 Wi-Fi 인터페이스를 지원한다. |
| `Thread` | 노드가 Thread 인터페이스를 지원한다. |
| `IP` | 노드가 IP 인터페이스를 지원한다. |
| `TCP` | 노드가 각 IP 인터페이스에서 TCP를 지원한다. |
| `UDP` | 노드가 각 IP 인터페이스에서 UDP를 지원한다. |
| `IPv4` | 노드가 각 IP 인터페이스에서 IPv4를 지원한다. |
| `IPv6` | 노드가 각 IP 인터페이스에서 IPv6를 지원한다. |
| `LanguageLocale` | 사용자에게 텍스트를 전달하기 위한 현지화를 지원한다. |
| `TimeLocale` | 사용자에게 시간을 전달하기 위한 현지화를 지원한다. |
| `UnitLocale` | 사용자에게 측정 단위를 전달하기 위한 현지화를 지원한다. |
| `SIT` | 노드가 짧은 유휴 시간의 간헐적 연결 장치이다. |
| `LIT` | 노드가 긴 유휴 시간의 간헐적 연결 장치이다. |
| `Active` | 노드가 항상 통신할 수 있다. |
| `Node` | 장치 유형이 Node 장치 유형으로 분류된다. Data Model specification 참조. |
| `App` | 장치 유형이 Application 장치 유형으로 분류된다. Data Model specification 참조. |
| `Simple` | 장치 유형이 Simple 장치 유형으로 분류된다. Data Model specification 참조. |
| `Dynamic` | 장치 유형이 Dynamic 장치 유형으로 분류된다. Data Model specification 참조. |
| `Composed` | 장치 유형이 둘 이상의 장치 유형으로 구성된다. System Model specification 참조. |
| `Client` | 엔드포인트에 클라이언트 애플리케이션 클러스터가 존재한다. |
| `Server` | 엔드포인트에 서버 애플리케이션 클러스터가 존재한다. |
| `Duplicate` | 해당 엔드포인트와 하나 이상의 형제 엔드포인트 사이에 애플리케이션 장치 유형이 중복된다. |
| `BridgedPowerSourceInfo` | 엔드포인트가 Bridged Device를 나타내며, Bridge에서 해당 장치의 전원 상태 정보를 사용할 수 있다. |

#### 클러스터 요구사항

| ID | 이름 | `side` | 요구사항 |
|---|---|---|---|
| `0x001D` | `Descriptor` | `server` | 필수 |
| `0x001E` | `Binding` | `server` | `Simple`과 `Client`가 모두 참이면 필수 |
| `0x0040` | `Fixed Label` | `server` | 선택 |
| `0x0041` | `User Label` | `server` | 선택 |

#### 기능 요구사항

| 클러스터 | 기능 `code` | 요구사항 |
|---|---|---|
| `Descriptor` | `TAGLIST` | `Duplicate`가 참이면 필수 |

### Root Node

출처: `data_model/1.7/device_types/RootNodeDeviceType.xml`

- `id`: `0x0016`
- `name`: `Root Node`
- `revision`: `5`
- `classification`: `class="node"`, `scope="node"`

#### 변경 이력

| `revision` | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 장치 유형에 `Power Source` 추가, `Power Source Configuration` 사용 중단 지정 |
| `3` | `Access Control` 클러스터의 Managed Device 기능에 대한 제한 추가 |
| `4` | Time Sync, TLS 및 `Power Source` 클러스터에 대한 조건과 클러스터 요구사항 추가 |
| `5` | `Groupcast` 클러스터에 대한 조건과 클러스터 요구사항 추가 |

#### 조건

아래에서 엔드포인트의 장치 유형에 관한 조건은, 노드의 하나 이상의 엔드포인트에 해당 요구사항을 가진 장치 유형이 존재함을 의미한다.

| 조건 | 의미 |
|---|---|
| `CustomNetworkConfig` | 노드가 대역 외 방식으로 구성되는 네트워킹만 지원한다. 예: 풍부한 사용자 인터페이스, 제조사별 방식, 사용자 정의 커미셔닝 흐름, 또는 `NetworkCommissioning` 클러스터가 아직 직접 지원하지 않는 미래의 IP 호환 네트워크 기술. |
| `ManagedAclAllowed` | 엔드포인트의 장치 유형에 이 조건을 참으로 설정하는 Device Library 요소 요구사항 표 항목이 있다. |
| `TimeSyncCond` | 엔드포인트의 장치 유형이 `Time Synchronization` 지원을 필요로 한다. |
| `TimeSyncWithClientCond` | 엔드포인트의 장치 유형이 클라이언트 클러스터 지원 및 `TimeSyncClient` 기능을 포함한 `Time Synchronization` 지원을 필요로 한다. |
| `TimeSyncWithNTPCCond` | 엔드포인트의 장치 유형이 `NTPClient` 기능을 포함한 `Time Synchronization` 지원을 필요로 한다. |
| `TimeSyncWithTZCond` | 엔드포인트의 장치 유형이 `TimeZone` 기능을 포함한 `Time Synchronization` 지원을 필요로 한다. |
| `TLSCertificatesCond` | 엔드포인트의 장치 유형이 `TLS Certificate Management`를 필요로 한다. TLS에 필요한 기본 Time Sync 지원 의존성도 포함한다. |
| `TLSClientCond` | 엔드포인트의 장치 유형이 `TLS Client Management`를 필요로 한다. TLS에 필요한 기본 Time Sync 지원 의존성도 포함한다. |
| `PowerSourceCond` | 엔드포인트의 장치 유형이 `Root Node`에 `Power Source`가 있어야 함을 요구한다. |
| `ACLExtensionCond` | 엔드포인트의 장치 유형이 `Access Control` 인스턴스에 `Extension` 속성이 있어야 함을 요구한다. |
| `GroupcastListenerCond` | 엔드포인트의 장치 유형이 `Listener` 기능을 갖춘 `Groupcast` 서버 클러스터 인스턴스를 필요로 한다. 어떤 엔드포인트든 `Groups` 클러스터 서버를 구현하면 이 조건을 반드시 지원해야 한다. |
| `GroupcastSenderCond` | 엔드포인트의 장치 유형이 `Sender` 기능을 갖춘 `Groupcast` 서버 클러스터 인스턴스를 필요로 한다. 어떤 엔드포인트든 `Bindings` 클러스터 서버를 구현하면 이 조건을 반드시 지원해야 한다. |

> `GroupcastSenderCond` 설명의 `Bindings`는 원문 표기이다. `Base Device Type` 클러스터 목록에는 `Binding`으로 표기되어 있다.

#### 클러스터 요구사항

`singleton="true"` 열의 `—`는 해당 `quality`가 제공된 XML에 명시되지 않았음을 뜻한다.

| ID | 이름 | `side` | `singleton="true"` | 요구사항 |
|---|---|---|---|---|
| `0x001F` | `Access Control` | `server` | 명시 | 필수 |
| `0x0028` | `Basic Information` | `server` | 명시 | 필수 |
| `0x002B` | `Localization Configuration` | `server` | 명시 | `LanguageLocale`이 참이면 필수 |
| `0x002C` | `Time Format Localization` | `server` | 명시 | `TimeLocale`이 참이면 필수 |
| `0x002D` | `Unit Localization` | `server` | 명시 | `UnitLocale`이 참이면 필수 |
| `0x002E` | `Power Source Configuration` | `server` | 명시 | `otherwiseConform`에 `optionalConform`, `deprecateConform` 순으로 정의 |
| `0x0030` | `General Commissioning` | `server` | 명시 | 필수 |
| `0x0031` | `Network Commissioning` | `server` | — | `CustomNetworkConfig`가 거짓이면 필수 |
| `0x0032` | `Diagnostic Logs` | `server` | 명시 | 선택 |
| `0x0033` | `General Diagnostics` | `server` | 명시 | 필수 |
| `0x0034` | `Software Diagnostics` | `server` | 명시 | 선택 |
| `0x0035` | `Thread Network Diagnostics` | `server` | — | `Thread`가 참일 때 선택 |
| `0x0036` | `Wi-Fi Network Diagnostics` | `server` | — | `Wi-Fi`가 참일 때 선택 |
| `0x0037` | `Ethernet Network Diagnostics` | `server` | — | `Ethernet`이 참일 때 선택 |
| `0x0038` | `Time Synchronization` | `server` | 명시 | 아래 시간 동기화 조건 중 하나라도 참이면 필수, 그 외 선택 |
| `0x0038` | `Time Synchronization` | `client` | 명시 | `TimeSyncWithClientCond`가 참이면 필수, 그 외 선택 |
| `0x003C` | `Administrator Commissioning` | `server` | 명시 | 필수 |
| `0x003E` | `Operational Credentials` | `server` | 명시 | 필수 |
| `0x003F` | `Group Key Management` | `server` | 명시 | 필수 |
| `0x0046` | `ICD Management` | `server` | 명시 | `SIT` 또는 `LIT`가 참이면 필수 |
| `0x0065` | `Groupcast` | `server` | 명시 | `GroupcastListenerCond` 또는 `GroupcastSenderCond`가 참이면 필수, 그 외 선택 |
| `0x0801` | `TLS Certificate Management` | `server` | 명시 | `TLSCertificatesCond`가 참이면 필수, 그 외 선택 |
| `0x0802` | `TLS Client Management` | `server` | 명시 | `TLSClientCond`가 참이면 필수, 그 외 선택 |

`Time Synchronization`의 `server`를 필수로 만드는 조건은 다음과 같다.

- `TimeSyncCond`
- `TimeSyncWithClientCond`
- `TimeSyncWithNTPCCond`
- `TimeSyncWithTZCond`
- `TLSClientCond`
- `TLSCertificatesCond`

> 조건부 요구사항에 별도의 대체 규칙이 없는 경우, 위 표도 조건이 거짓일 때의 요구사항을 추가하지 않는다. 또한 `PowerSourceCond`와 변경 이력의 `Power Source` 언급은 존재하지만, 제공된 `RootNodeDeviceType.xml`의 `clusters`에는 `Power Source` 항목이 없다.

#### Access Control 기능 및 속성

| 종류 | 식별자 | 요구사항 |
|---|---|---|
| 기능 | `MNGD` | `ManagedAclAllowed`가 참일 때 선택 |
| 기능 | `AUX` | `GroupcastListenerCond`가 참이면 필수 |
| 속성 | `Extension`, `code="0x0001"` | `ACLExtensionCond`가 참이면 필수 |

#### Time Synchronization 기능

제공된 XML은 `server`와 `client` 양쪽에 동일한 기능 적합성 규칙을 정의한다. 각 기능의 `otherwiseConform` 분기 순서는 다음과 같다.

| 기능 `code` | 첫 번째 분기 | 두 번째 분기 | 마지막 분기 |
|---|---|---|---|
| `TSC` | `TimeSyncWithClientCond`가 참이면 필수 | `TLSCertificatesCond` 또는 `TLSClientCond`가 참이면 `optionalConform choice="a" more="true" min="1"` | 선택 |
| `NTPC` | `TimeSyncWithNTPCCond`가 참이면 필수 | `TLSCertificatesCond` 또는 `TLSClientCond`가 참이면 `optionalConform choice="a" more="true" min="1"` | 선택 |
| `TZ` | `TimeSyncWithTZCond`가 참이면 필수 | 해당 없음 | 선택 |

`TSC`와 `NTPC`의 TLS 조건부 선택 분기는 같은 `choice="a"`를 사용하며, `min="1"`, `more="true"`가 지정되어 있다.

#### 그 밖의 기능 요구사항

| 클러스터 | 기능 `code` | 요구사항 |
|---|---|---|
| `Group Key Management` | `GCAST` | `GroupcastListenerCond` 또는 `GroupcastSenderCond`가 참이면 필수, 그 외 선택 |
| `ICD Management` | `LITS` | `LIT`가 참이면 필수 |
| `Groupcast` | `LN` | `GroupcastListenerCond`가 참이면 필수, 그 외 선택 |
| `Groupcast` | `SD` | `GroupcastSenderCond`가 참이면 필수, 그 외 선택 |