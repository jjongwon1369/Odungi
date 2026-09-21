# Corpus Scope Finalization — scope-v1.0

상태: **범위·데이터 모델 확정, Corpus 추출 및 v1.0 Freeze 미실행**.
기계 판독 설정은 [metadata/scope.json](metadata/scope.json), 관계/자료 Coverage는
[metadata/coverage_matrix.csv](metadata/coverage_matrix.csv)를 사용한다.

## 1. 고정 기준과 권위

- Repository: connectedhomeip, 관찰 branch master.
- Commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`.
- 정의 baseline: `data_model/1.7`. 다른 버전 디렉터리는 Core에 섞지 않는다.
- 사양 모델 원본: `data_model/1.7/spec_sha`의 `214e40c9d51cfe89050eae68ca5b76238fcfa332`.
- spec tag: `0.9-1.7-winter2027`. **개발 Snapshot을 선택한 것이며 정식 배포 사양이라는 뜻은 아니다.**
- SDK 요구/선언은 같은 checkout의 `src/app/zap-templates/zcl/data-model/chip`에서 별도 기록한다.

사양 XML은 선택 baseline의 요구 정의 기준, SDK XML은 codegen 선언 기준,
예제는 해당 구성 기준, C++는 구현 근거다. 상충하는 내용을 한 값으로 정정·통합하지 않는다.
범위 선택은 이후 성능 결과를 보고 바꾸지 않으며 변경 시 scope 버전과 사유를 남긴다.

## 2. 최종 제품군과 Cluster 수

| 제품/Device Type | ID | 포함 직접 Cluster | Base 포함 고유 Cluster |
|---|---|---:|---:|
| Laundry Washer | 0x0073 | 6 | 10 |
| Room Air Conditioner | 0x0072 | 12 | 16 |
| Refrigerator | 0x0070 | 4 | 8 |
| Temperature Controlled Cabinet, Cooler-only 보조 범위 | 0x0071 | 4 | 8 |
| 냉장고 제품군 전체, 위 두 Device Type의 합집합 | 0x0070 + 0x0071 | 7 | 11 |

**3개 제품군 / 4개 공식 Device Type ID / 전체 고유 Cluster ID 23개**다.
공통 Base 4종은 각 Device Type에서 관계를 추적하지만 원본 파일은 중복 수집하지 않는다.
직접/상속 관계의 합은 42행이다. Mode Base·Alarm Base·Label처럼 숫자 Cluster ID가 없는
지원 정의, Root Node의 제한된 조건 문맥, endpoint 관계는 위 Cluster 수에서 제외한다.

Air Purifier, Dishwasher, Laundry Dryer는 이번 scope에서 제외한다.
Discovery 기록은 CSV에 제외 감사 행으로 남기되 해당 후보 때문에 수집 범위를 넓히지 않는다.

## 3. Device Type별 포함 범위

### Laundry Washer

Device Type 정의: `data_model/1.7/device_types/LaundryWasher.xml`(revision 2),
SDK `matter-devices.xml`의 deviceId=0x0073 요소.

| 직접 Cluster | ID | 요구 |
|---|---|---|
| Identify | 0x0003 | optional |
| On/Off | 0x0006 | optional; 포함 시 DF mandatory |
| Laundry Washer Mode | 0x0051 | optional; DEPONOFF/StartUpMode disallowed |
| Laundry Washer Controls | 0x0053 | optional |
| Temperature Control | 0x0056 | optional |
| Operational State | 0x0060 | mandatory; OperationCompletion mandatory |

각 Cluster의 사양 XML, SDK XML, CPP/H 구현 entry point와 같은 component의 직접 파일까지 포함한다.
정확한 경로는 scope.json의 clusters 항목과 CSV를 따른다.
핵심 구현은 `laundry-washer-controls-server/LaundryWasherControlsCluster.cpp`,
`operational-state-server/OperationalStateCluster.cpp`, `mode-base-server/ModeBaseCluster.cpp`이다
(모두 `src/app/clusters/` 아래).

예제는 `examples/laundry-washer-app/nxp/zap/laundry-washer-app.{zap,matter}`와
`nxp/common/main/laundry-washer-mode.cpp`, `DeviceCallbacks.cpp`, `ZclCallbacks.cpp`만 명시적으로 포함한다.
이 파일의 대응 header와 Controls delegate에 한해 scope.json의 예외 allowlist를 적용한다.
`examples/laundry-washer-app/nxp/CMakeLists.txt:78,92`는 all-clusters-common의 include와
`src/laundry-washer-controls-delegate-impl.cpp` 재사용을 확인하는 근거다.
이 CPP/H와 `include/laundry-washer-mode.h`만 추가하며 all-clusters-common 전체로 확장하지 않는다.
SDK 전체·RTOS·NXP 하드웨어·main/AppTask로 탐색을 확대하지 않는다.
예제 Device Type revision 1을 revision 2로 고치지 않는다.

### Room Air Conditioner

Device Type 정의: `data_model/1.7/device_types/RoomAirConditioner.xml`(revision 5),
SDK `matter-devices.xml`의 deviceId=0x0072 요소.

| 직접 Cluster | ID | 요구 |
|---|---|---|
| Identify | 0x0003 | mandatory |
| Groups | 0x0004 | optional |
| On/Off | 0x0006 | mandatory; DF mandatory |
| Scenes Management | 0x0062 | optional |
| Thermostat Mode | 0x0063 | otherwise/provisional + revision >= 5 optional 조건 보존 |
| HEPA Filter Monitoring | 0x0071 | optional |
| Activated Carbon Filter Monitoring | 0x0072 | optional |
| Thermostat | 0x0201 | mandatory |
| Fan Control | 0x0202 | optional |
| Thermostat User Interface Configuration | 0x0204 | optional |
| Temperature Measurement | 0x0402 | optional |
| Relative Humidity Measurement | 0x0405 | optional |

Thermostat은 `src/app/clusters/thermostat-server`의 직접 CPP/H 분할 구현을 함께 포함한다.
다른 Cluster도 CSV의 명시 component 루트까지만 포함한다.
예제는 `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.{zap,matter}`다.
이 예제의 AC endpoint 1과 온도/습도 endpoint 2/3은 분리된 구성으로 기록한다.
선택 IDL에 없는 Optional Cluster의 선언은 지정 all-clusters IDL의 해당 Cluster 부분만 참조한다.

Root Node GroupcastListenerCond는 `RootNodeDeviceType.xml`의 조건 해석에 필요한 부분까지 포함한다.
Groupcast·Access Control·commissioning 등의 Root Cluster 구현으로 확장하지 않는다.
Groups가 있다는 이유로 전체 노드 구현을 scope에 가져오지 않는다.

### Refrigerator + Temperature Controlled Cabinet

정의: `data_model/1.7/device_types/Refrigerator.xml`(revision 3) 및
`TemperatureControlledCabinet.xml`(revision 6), SDK의 대응 Device Type 요소.

냉장고 직접 Cluster: Identify(0x0003), Refrigerator And Temperature Controlled Cabinet Mode(0x0052),
Refrigerator Alarm(0x0057), Activated Carbon Filter Monitoring(0x0072).
모두 optional이며 Carbon Filter에는 revision >= 3 조건, Mode에는 금지 조건이 있다.

Cabinet은 연구 프로필 **Cooler=true, Heater=false**로 범위를 제한한다.

| Cabinet 직접 관계 | ID | 이번 처리 |
|---|---|---|
| Refrigerator And Temperature Controlled Cabinet Mode | 0x0052 | Cooler 조건의 optional, 포함 |
| Temperature Control | 0x0056 | mandatory, TN mandatory/TL disallowed, 포함 |
| Temperature Alarm | 0x0064 | provisional/optional 선언, specification-only로 포함 |
| Temperature Measurement | 0x0402 | optional, 포함 |
| Oven Cavity Operational State | 0x0048 | Heater-only, not_applicable로 제외 |
| Oven Mode | 0x0049 | Heater-only, not_applicable로 제외 |

관계 근거를 분리한다.

- Refrigerator.xml:68–71: Cabinet의 Cooler 조건 mandatory.
- SDK matter-devices.xml:3055–3060: tree / 최소 1개의 Cabinet endpoint.
- Chef `rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap`:
  endpoints 2·3의 parentEndpointIdentifier=1. `.matter`는 endpoint별 선언 근거다.
- 전용 `examples/refrigerator-app/refrigerator-common/refrigerator-app.zap`:
  Cabinet의 부모 값은 null이다. 이 예제도 Revision·구성 차이 분석용으로 보존한다.

Chef에 추가로 있는 Fan endpoint 4의 존재는 원본 topology 문맥으로 확인할 수 있지만
Fan Device Type을 별도 후보로 확장하지 않는다. 냉장고 기능 Corpus에서 그 예제 Fan 구현을 따라가지 않는다.
전용 예제의 `refrigerator-common/src/static-supported-temperature-levels.cpp`는
구형 구성/온도 선택 근거로만 포함한다.

Temperature Alarm은 선택 검색 범위에 concrete SDK/IDL/구현이 없으므로 missing을 명시한다.
Refrigerator Alarm이나 Alarm Base가 곧 Temperature Alarm 구현이라고 주장하지 않는다.

## 4. Base와 공유 정의/구현

BaseDeviceType.xml의 Descriptor(0x001D), Binding(0x001E), Fixed Label(0x0040), User Label(0x0041)을
네 Device Type에 공통으로 포함한다. Binding은 Simple AND Client 조건을 그대로 유지한다.
optional/conditional 선언을 포함하는 것과 실제 장치가 기능을 활성화했다는 주장은 다르다.

1-hop Cluster 기반 정의: `ModeBase.xml`, `AlarmBase.xml`, `Label-Cluster.xml`.
Mode 계열의 alias 연결은 `src/app/clusters/mode-base-server/mode-base-cluster-objects.h`를 포함한다.
알람은 `refrigerator-alarm-server` + `alarm-base-server`, 필터는 `resource-monitoring-server`를 포함한다.

- cluster_shared: 동일 Cluster를 여러 장치에서 쓰는 구현.
- framework_shared: 여러 Cluster alias/파생 Cluster가 공유하는 기반 구현 또는 공통 계약.
- device_specific: scope에 지정한 예제 delegate/연결 코드. 제품 완성도를 뜻하지 않는다.
- 재사용 Controls delegate는 예제 파일이지만 implementation_scope=cluster_shared다.
- unverified: 구현 mapping 근거가 없는 경우.

물리 파일은 Snapshot+path당 한 번만 수집하고 관계만 여러 개 둔다.
동일 내용을 Device Type별로 복제하거나 shared 기반을 불필요 중복으로 삭제하지 않는다.

## 5. Traversal 종료 및 파일 선택 규칙

1. 직접 required/optional/conditional/provisional Cluster는 모두 포함하되 Cooler-only 분기를 적용한다.
2. 명시된 related Device Type은 1-hop, allowlist는 Cabinet뿐이다. Root는 조건 정의 문맥만 허용한다.
3. Base Device Type은 1-hop 포함한다. 적용 조건을 재귀적으로 만족시키기 위한 추가 장치를 생성하지 않는다.
4. Cluster의 명시적 baseCluster도 1-hop, Mode Base/Alarm Base/Label만 포함한다.
   역방향으로 다른 alias/Device Type을 추가하지 않는다.
5. scope.json의 20개 component 루트에서 **바로 아래 CPP/H만** 포함한다.
   Thermostat의 분할 파일, delegate/header, CodegenIntegration은 포함하되 하위 tests와 다른 디렉터리는 자동 탐색하지 않는다.
   현재 checkout 기준 이 규칙에 맞는 구현 후보는 183파일이며 실제 추출 수/Token 수는 아니다.
6. 바깥 include는 추적을 멈춘다. 공통 계약 예외는 `src/app/server-cluster/DefaultServerCluster.h` 한 파일이다.
   lib/platform/third_party/build 구현, 광범위한 generated client 코드로 확장하지 않는다.
7. 생성 Metadata는 scope.json에 열거한 HEPA/Carbon/RelativeHumidity의 Metadata.h만 Revision 근거로 포함한다.
8. 예제는 지정 `.zap/.matter`와 delegate allowlist만 사용한다. links/imports/build dependency를 따라가지 않는다.
   CMakeLists는 지정된 delegate 연결의 근거 구간만 허용하고 build graph를 실행하거나 순회하지 않는다.
9. whole raw 원본은 추후 보존하되 통합 XML/IDL/ZAP의 공통 입력은 선택 Entity와 필요한 공통 정의를 기준으로 절취한다.
   예: ResourceMonitoring의 다른 ID나 all-clusters의 무관한 Cluster는 자동 포함하지 않는다.
   절취 규칙은 A/B/C 공통이며 원본 위치 매핑을 필수로 한다.
10. 필요한 공통 정의의 경계를 안전하게 정할 수 없으면 추출 검증을 실패시킨다. 조용한 누락/전체 파일 fallback을 금지한다.
11. 아직 이 규칙을 실행하지 않았다. 추출 구현 때 결정적 선택자와 재현성 검증을 구현해야 한다.

## 6. Coverage 판정과 승인된 결손

CSV 91행: **present 38 / missing 21 / not_applicable 32 / unverified 0**.

- 선택 Cluster 관계 42행: present 21, missing 21.
- 새 Base/endpoint/related/shared 관계 17행: present.
- scope 제외 감사 행 32행: not_applicable.

missing 20행은 중복된 관계에 걸친 9개 component의 독립 Markdown 가이드 부재다.
나머지 1행은 Temperature Alarm이다. source_taxonomy.md에 검색 범위를 기록했다.
이 결손은 **명시적으로 허용한 불완전 Coverage**다. 정의·구현 자료가 있는 Cluster 자체를 제거하지 않으며
해당 자료가 존재한다고 전제하는 평가 질문을 만들지 않는다.
이 표의 unverified 0과 아래 의미적/실행 관련 미해결 사항을 혼동하지 않는다.

## 7. Revision과 Freeze gate

Revision 차이만으로 제외하지 않는다. [revision_analysis.md](research/revision_analysis.md)의 비교를 유지한다.
출처별 원본 값·Commit·Entity Revision을 별도로 기록하며 비교 질문에는 대상 출처/버전을 명시한다.

아직 Corpus v1.0 Freeze를 막는 작업:

- 사양 XML 등의 변환·보관·공유 이용 조건과 실행 범위 확인.
- Extraction Script 및 통합 파일의 결정적 절취/원본 위치 매핑 구현.
- 원본·정규화 Hash, Identifier 보존, Manifest, 2회 재생성 검증.
- Token 집계와 실제 Wiki Context 적합성 점검(이 단계에는 실행하지 않음).
- 차이 사례의 의미적 정합성 검토와 팀 교차 검토, 평가 근거 사용 범위 점검.

**다음 단계 Extraction Script 구현을 시작할 준비는 됐다.** 구현 입력은 이 scope와 고정 SHA다.
다만 이번 요청은 구현/실행을 허가하지 않으므로 Script를 작성하지 않았고 Corpus도 추출하지 않았다.

## 8. Finalization 검증 기록

2026-09-18에 다음을 확인했다.

- CSV 91개 고유 coverage_id, 기존 Discovery 74행과 unverified 37행의 처리 이력 보존.
- 42개 포함 Cluster 관계 / 23개 고유 ID / 냉장고 제품군 고유 11개 집계와 scope.json 일치.
- CSV의 실제 파일 경로 440건, 추가 source_sets 경로, 근거 행 범위, 사양/SDK 선언 Revision 대조.
- JSON 설정 및 문서 JSON 예시, Markdown 링크·코드 블록 검증.
- connectedhomeip HEAD 유지 및 작업 트리 clean 재확인.
- Extraction Script 없음, raw/processed에는 기존 README만 존재.

의미적 정합성·실행 동작·실제 Token/Context는 이 검증에 포함하지 않았다.
