---
entity: Root/Base Device Type
ids: []
source_paths: ['data_model/1.7/device_types/BaseDeviceType.xml', 'data_model/1.7/device_types/RootNodeDeviceType.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# Root/Base Device Type

## 개요

제공된 스펙은 `Base Device Type`과 `Root Node`의 정의를 포함한다.

| 항목 | `Base Device Type` | `Root Node` |
|---|---|---|
| Device Type ID | 원문에 명시되지 않음 | `0x0016` |
| 리비전 | `3` | `5` |
| 분류 | 원문에 명시되지 않음 | `class="node"`, `scope="node"` |
| 정의 범위 | 조건 및 클러스터 요구사항 | 분류, 리비전 이력 및 `GroupcastListenerCond` 조건 |

## 스펙

### Base Device Type

출처: `data_model/1.7/device_types/BaseDeviceType.xml`

#### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | `Multiple` 조건을 `Duplicate` 조건으로 대체 |
| `3` | 인증 프로그램 조건 제거 |

#### 조건

| 조건 이름 | 의미 |
|---|---|
| `Ethernet` | 노드가 Ethernet LAN 인터페이스를 지원한다. |
| `Wi-Fi` | 노드가 Wi-Fi 인터페이스를 지원한다. |
| `Thread` | 노드가 Thread 인터페이스를 지원한다. |
| `IP` | 노드가 IP 인터페이스를 지원한다. |
| `TCP` | 노드가 각 IP 인터페이스에서 TCP를 지원한다. |
| `UDP` | 노드가 각 IP 인터페이스에서 UDP를 지원한다. |
| `IPv4` | 노드가 각 IP 인터페이스에서 IPv4를 지원한다. |
| `IPv6` | 노드가 각 IP 인터페이스에서 IPv6를 지원한다. |
| `LanguageLocale` | 노드가 사용자에게 텍스트를 전달하기 위한 현지화를 지원한다. |
| `TimeLocale` | 노드가 사용자에게 시간을 전달하기 위한 현지화를 지원한다. |
| `UnitLocale` | 노드가 사용자에게 측정 단위를 전달하기 위한 현지화를 지원한다. |
| `SIT` | 노드가 짧은 유휴 시간의 간헐적 연결 장치이다. |
| `LIT` | 노드가 긴 유휴 시간의 간헐적 연결 장치이다. |
| `Active` | 노드가 항상 통신할 수 있다. |
| `Node` | 장치 유형이 Node 장치 유형으로 분류된다. Data Model specification을 참조한다. |
| `App` | 장치 유형이 Application 장치 유형으로 분류된다. Data Model specification을 참조한다. |
| `Simple` | 장치 유형이 Simple 장치 유형으로 분류된다. Data Model specification을 참조한다. |
| `Dynamic` | 장치 유형이 Dynamic 장치 유형으로 분류된다. Data Model specification을 참조한다. |
| `Composed` | 장치 유형이 둘 이상의 장치 유형으로 구성된다. System Model specification을 참조한다. |
| `Client` | 엔드포인트에 클라이언트 애플리케이션 클러스터가 존재한다. |
| `Server` | 엔드포인트에 서버 애플리케이션 클러스터가 존재한다. |
| `Duplicate` | 엔드포인트와 하나 이상의 형제 엔드포인트 사이에 애플리케이션 장치 유형이 중복된다. |
| `BridgedPowerSourceInfo` | 엔드포인트가 Bridged Device를 나타내며, Bridge가 해당 장치의 전원 상태 정보를 이용할 수 있다. |

#### 클러스터 요구사항

모든 클러스터는 `side="server"`로 정의된다.

| 클러스터 ID | 클러스터 이름 | 적합성 요구사항 |
|---|---|---|
| `0x001D` | `Descriptor` | 필수 |
| `0x001E` | `Binding` | `Simple`과 `Client` 조건을 모두 만족하면 필수 |
| `0x0040` | `Fixed Label` | 선택 |
| `0x0041` | `User Label` | 선택 |

#### 기능 요구사항

| 클러스터 | 기능 코드 | 적합성 요구사항 |
|---|---|---|
| `Descriptor` | `TAGLIST` | `Duplicate` 조건을 만족하면 필수 |

### Root Node

출처: `data_model/1.7/device_types/RootNodeDeviceType.xml`

- Device Type ID: `0x0016`
- 이름: `Root Node`
- 리비전: `5`
- 분류: `class="node"`, `scope="node"`

#### 리비전 이력

| 리비전 | 변경 사항 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 장치 유형에 `Power Source` 추가, `Power Source Configuration` 사용 중단 처리 |
| `3` | `Access Control` 클러스터의 `Managed Device` 기능에 대한 제한 추가 |
| `4` | `Time Sync`, `TLS`, `Power Source` 클러스터에 대한 조건 및 클러스터 요구사항 추가 |
| `5` | `Groupcast` 클러스터에 대한 조건 및 클러스터 요구사항 추가 |

#### 조건

| 조건 이름 | 의미 및 요구사항 |
|---|---|
| `GroupcastListenerCond` | 노드에 하나 이상의 엔드포인트가 있고, 해당 엔드포인트에 존재하는 어떤 Device Type이 `Listener` 기능을 갖춘 `Groupcast` 서버 클러스터 인스턴스를 필요로 한다. 어느 엔드포인트에서든 `Groups` 클러스터 서버를 구현하면 이 조건을 반드시 지원해야 한다(`SHALL`). |

제공된 `RootNodeDeviceType.xml`에는 클러스터 요구사항을 직접 정의하는 `<clusters>` 요소가 없다. 리비전 이력에 언급된 클러스터의 상세 요구사항은 제공된 본문에 명시되어 있지 않다.