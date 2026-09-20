# connectedhomeip Repository 구조 조사

조사일: 2026-09-17. 범위: 로컬 checkout의 파일·선언·관계 확인만 수행한 Corpus Scope Discovery.
Corpus 추출, 빌드, 생성기 실행, RAG/Wiki 전처리는 수행하지 않았다.

## 1. 조사 Snapshot

| 항목 | 확인 결과 |
|---|---|
| 로컬 경로 | C:/Users/USER/OneDrive/Desktop/connectedhomeip |
| HEAD SHA | 1ac132b5ecd42cb6c78772f2576ed6f7fc814183 |
| Branch | master |
| HEAD와 정확히 일치하는 tag | 없음: git tag --points-at HEAD 결과가 비어 있음 |
| HEAD Commit 시각 | 2026-09-17T12:56:54Z |
| 작업 트리 | 조사 시작·검증 시 git status --porcelain 출력 없음 |
| 조사 Data Model | data_model/1.7 — 최종 Corpus 버전 선정/Freeze가 아님 |
| SDK Specification 값 | src/app/SpecificationDefinedRevisions.h:53의 0x01070000 |
| XML 원본 spec SHA | data_model/1.7/spec_sha:1의 214e40c9d51cfe89050eae68ca5b76238fcfa332 |
| XML 원본 spec tag | data_model/1.7/spec_tag:1의 0.9-1.7-winter2027 |
| Scraper | data_model/1.7/scraper_version:1의 alchemy version: v1.7.10 |

Git 조회에는 --no-optional-locks와 명령 단위 safe.directory 설정을 사용했다.
참조 저장소와 global Git 설정은 수정하지 않았다. checkout/fetch/submodule 초기화도 수행하지 않았다.
이 문서와 CSV의 source path는 모두 위 connectedhomeip 루트 기준이며 행 번호는 해당 SHA 기준이다.

**버전 주의:** 1.7 디렉터리 존재나 SDK 값만으로 정식 배포 사양이라고 판정하지 않는다.
spec_tag에는 위와 같은 문자열이 있으며 provisional 선언도 있다.
루트 SPECIFICATION_VERSION:1은 1.2.0으로 다른 값을 가진다.
이 파일의 사용 목적 및 외부 사양 원문과의 완전한 대응은 unverified다.
최종 baseline은 구현·예제 Revision과 대조하여 별도로 선택해야 한다.

## 2. 실제 Repository 구조

아래는 확인한 주요 디렉터리다. 전체 파일 목록을 복사한 것은 아니다.

    connectedhomeip/
    ├── data_model/        버전별 사양 모델 XML과 ID JSON
    ├── src/
    │   ├── app/
    │   │   ├── clusters/  서버 구현, 공통 기반 클래스, delegate, tests
    │   │   ├── zap-templates/zcl/  SDK 코드 생성용 정의와 설정
    │   │   └── SpecificationDefinedRevisions.h
    │   ├── controller/   controller와 생성 클라이언트 코드
    │   ├── python_testing/
    │   ├── platform/
    │   └── lib/
    ├── examples/          앱 구성(.zap/.matter), 연결 코드, README
    ├── docs/              개발·IDL·코드 생성·예제 문서
    ├── scripts/           IDL 도구, ZAP 도구, 사양 XML 생성 도구
    ├── zzz_generated/     체크인된 생성 코드
    ├── config/
    ├── build/
    ├── build_overrides/
    ├── credentials/
    ├── integrations/
    └── third_party/       이번 조사 제외

data_model에는 1.0, 1.1, 1.2, 1.3, 1.4, 1.4.1, 1.4.2, 1.5, 1.5.1, 1.6, 1.6.1, 1.7이 있다.
각 버전을 합쳐 단일 모델로 취급하지 않는다. 1.7 아래에는 clusters, device_types, globals,
namespaces 및 spec_sha/spec_tag/scraper_version이 실제로 있다.

## 3. 정의·구조화 자료의 위치와 역할

| 계층 | 실제 source path | 확인 내용 |
|---|---|---|
| 사양 모델 설명 | data_model/README.md:7–16 | certification/testing/documentation용이며 ZAP/SDK codegen용이 아님 |
| Device Type 정의 | data_model/1.7/device_types/Refrigerator.xml:60 등 | ID, Revision, Cluster 역할 및 conformance |
| Device Type ID 목록 | data_model/1.7/device_types/device_type_ids.json | 구조화 ID 목록 |
| 공통 Device Type | data_model/1.7/device_types/BaseDeviceType.xml | Descriptor, 조건부 Binding, Fixed/User Label |
| Root Node | data_model/1.7/device_types/RootNodeDeviceType.xml | 노드 수준 요구; 이번 CSV의 직접 장치 행과 별개 |
| Cluster 사양 모델 | data_model/1.7/clusters/LaundryWasherControls.xml 등 | 이름·ID·속성·명령 및 조건 |
| SDK Device Type 정의 | src/app/zap-templates/zcl/data-model/chip/matter-devices.xml | 여러 Device Type이 한 XML에 들어 있음 |
| SDK Cluster 정의 | src/app/zap-templates/zcl/data-model/chip/washer-controls-cluster.xml 등 | code/name 및 codegen 입력 |
| ZAP 설정 JSON | src/app/zap-templates/zcl/zcl.json | SDK ZCL 구성 |
| 앱 ZAP 구성 | examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap | 앱에서 선택한 endpoint/cluster 구성 |
| 앱 IDL | examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter | 선언과 endpoint별 server cluster 구성 |
| 조합 장치 구성 | examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap 및 .matter | Room AC와 별도 센서 endpoint |
| 생성 C++ Metadata | zzz_generated/app-common/clusters/Actions/Metadata.h 등 | 생성 산출물; 독립 수작업 구현과 구별 |

SDK Device Type 근거 위치는 matter-devices.xml에서 Room AC:2789, Air Purifier:2866,
Dishwasher:2932, Refrigerator:3049, Laundry Washer:3089, Laundry Dryer:3133(typeName 행)이다.
세부 Cluster별 사양 XML·SDK XML 경로는 coverage_matrix.csv에 별도로 기록했다.

.matter는 사람이 읽을 수 있는 IDL이며 .zap은 앱 구성이다.
둘 다 Device Type의 모든 선택 Cluster를 반드시 포함하는 목록은 아니다.
근거: docs/guides/matter_idl_tooling.md:1–7, examples/chef/README.md:7–15.
해당 IDL 문서의 data_model/clusters 예시 경로는 현재 버전별 배치와 맞지 않으므로 그대로 사용하지 않는다.

## 4. C/C++ 구현 구조

| 기능 | 실제 구현 근거 | 범위 주의 |
|---|---|---|
| Laundry Washer Controls | src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp:27,49 | ReadAttribute/WriteAttribute; 장치 완성도 검증은 아님 |
| Temperature Control | src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp:142 | SetTemperature 명령 처리 |
| Refrigerator Alarm | src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.cpp:25 | Notify 이벤트 생성 |
| Alarm 공통 기반 | src/app/clusters/refrigerator-alarm-server/RefrigeratorAlarmCluster.h:26 및 alarm-base-server/AlarmBaseCluster.cpp | RefrigeratorAlarmCluster가 AlarmBaseCluster를 상속 |
| Mode 계열 | src/app/clusters/mode-base-server/ModeBaseCluster.cpp 및 mode-base-cluster-objects.h:61–69 | Laundry/냉장고/Thermostat 등 alias가 공통 구현 사용 |
| Operational State | src/app/clusters/operational-state-server/OperationalStateCluster.cpp | Oven Cavity 등 파생 구현과 연결 |
| Thermostat | src/app/clusters/thermostat-server/ThermostatClusterBase.cpp, ThermostatClusterRead.cpp, ThermostatClusterWrite.cpp | 구현이 여러 파일에 분산됨 |
| Fan Control | src/app/clusters/fan-control-server/FanControlCluster.cpp | FanControl 구현 |
| 필터 모니터링 | src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp 및 CodegenIntegration.cpp | HEPA/Activated Carbon 공통 기반 |
| 앱 delegate | examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp:39 | 예제 모드 변경 핸들러; 실제 세탁 하드웨어 동작 보장은 아님 |

CodegenIntegration.cpp, 호환 wrapper, delegate, 기반 클래스를 함께 추적해야 한다.
Cluster 이름과 같은 디렉터리가 항상 독립적으로 존재하는 구조가 아니다.
전체 빌드 성공, 실제 하드웨어 동작, 전체 사양 준수는 모두 unverified다.

## 5. Documentation

- docs/cluster_and_device_type_dev/cluster_and_device_type_dev.md: Cluster 정의·구현 및 Device Type codegen 위치.
- docs/guides/writing_clusters.md: 구현 개발 가이드.
- docs/guides/matter_idl_tooling.md: IDL 형식과 도구; 일부 경로 예시는 현재 구조와 차이 있음.
- docs/zap_and_codegen/zap_intro.md: ZAP/codegen 설명.
- docs/ids_and_codes/spec_device_types.md:45–48 및 spec_clusters.md: 이름·ID 참조표. 상세 기능 설명 문서와 구별한다.
- docs/examples/refrigerator.md, laundry_washer.md: 예제 문서 인덱스이며 기능 설명 본문 자체는 아님.
- examples/refrigerator-app/linux/README.md: 냉장고 앱 빌드·실행 안내.
- examples/laundry-washer-app/nxp/README.md:5–8: 세탁기 prototype 및 플랫폼 안내.
- examples/air-purifier-app/air-purifier-common/README.md: Fan/Filter 등 PICS 목록.
- src/app/clusters/{mode-base-server,operational-state-server,alarm-base-server,fan-control-server,resource-monitoring-server}/README.md: Cluster 또는 공통 기반 구현 설명.

모든 Cluster에 상세 prose가 확보된 것은 아니다. CSV의 documentation_path가 unverified이면
상세 관련 문서를 아직 확보하지 못한 것이며 저장소 전체에 문서가 없다는 뜻은 아니다.

## 6. 조사 범위·검색 기준

실제 파일 목록과 XML 내용에서 ID·역할·conformance를 읽고, 동일 숫자 ID의 Cluster XML 및
.matter 선언을 대조했다. C++ 파일에서는 구현 본문과 공유 기반/alias 연결을 확인했다.
CSV에는 정의 경로, 요구 조건의 행, IDL 선언 행, 선택한 예제의 해당 Device endpoint 번호를 기록했다.
Base 요구의 적용 근거는 src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py:1963–1964이다.

Temperature Alarm(0x0064)은 사양 모델과 Device Type 참조를 확인했지만,
src/app/zap-templates/zcl/data-model/chip의 직접 Cluster 정의와
src/app/clusters의 TemperatureAlarm/Temperature Alarm 구현 검색에서는 대응 근거를 확보하지 못했다.
선택 예제 및 all-clusters IDL에도 해당 선언을 확인하지 못했다.
프로젝트 전체의 미구현으로 단정하지 않고 unverified로 기록했다.

외부 사양 저장소/웹 문서는 조사하지 않았다. Source XML의 주석에 있는
src/app_clusters/*.adoc 경로는 이 checkout의 파일 경로로 간주하지 않는다.

## 7. PLAN에 반영할 사항과 후속 확인

1. 사양 XML과 SDK XML을 별도 출처 계층으로 구분하고, baseline 디렉터리와 코드 Revision 대응을 고정해야 한다.
2. Refrigerator만으로 냉각 기능 범위가 완결되지 않는다. Temperature Controlled Cabinet와 endpoint 관계를 범위에 포함해야 한다.
3. Base Device Type의 공통 요구와 Root Node 의존을 장치별 직접 Cluster 목록과 분리해야 한다.
4. Mode/Alarm/Resource Monitoring 같은 공유 기반 구현은 단순 중복으로 제외하면 안 된다.
5. 예제 .matter/.zap은 선택된 구성이다. 모든 Required/Optional Cluster 목록의 대체 근거가 아니다.
6. docs/와 examples/의 README·ID 표는 사양 기능 설명과 Coverage 수준이 다르다.
7. data_model/1.7 XML 머리말에는 별도 이용 조건이 있다(예: device_types/Refrigerator.xml:3–18).
   루트 LICENSE만 보고 모든 자료의 재배포·변환 조건이 동일하다고 가정하지 않는다.
   후속 추출·공유 범위에 대한 이용 조건 확인은 미완료이며 이번에는 경로·관계만 기록했다.
8. 2~3개의 가전 제품 범위를 선택하더라도 냉장고의 보조 Device Type까지 세면 공식 ID 수는 늘어난다.
   제품군 수와 Device Type ID 수를 구분하도록 계획을 보완할 필요가 있다.

이번 단계에서 corpus-plan.md 자체나 Corpus 범위 설정/SSOT는 변경·확정하지 않았다.

## 8. 산출물 검증

- CSV 74행의 Device Type/Cluster/역할 조합이 모두 유일하다.
- 기록한 실제 source path의 파일 존재를 확인했다(unverified 값 제외).
- 요구 조건의 행 번호와 Cluster ID, IDL 선언 행의 숫자 ID를 대조했다.
- 각 행의 사양 XML 및 SDK XML 내부 Cluster ID가 CSV ID와 일치함을 확인했다.
- 주요 .zap 및 JSON 파일을 실제로 읽어 구조를 확인했다.
- status는 present/unverified만 사용했으며 허용된 네 값 이외의 값은 없다.
- 참조 checkout의 Git 작업 트리가 변경되지 않았음을 다시 확인했다.

검증 범위는 파일·식별자·근거 연결의 일관성이다. 사양과 구현의 완전한 의미적 일치,
모든 feature 조합, 런타임 동작, 빌드 성공을 검증한 것은 아니다.
