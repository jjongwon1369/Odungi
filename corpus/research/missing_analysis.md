# Coverage missing 분석

고정 commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`. Scope와 기존 CSV 상태는 변경하지 않았다.

분류 결과: documentation_missing 20, unavailable_source 1, expected_missing 0, not_implemented 0, scope_issue 0.

`expected_missing`은 원래 대상이 아닌 자료를 기대한 경우, `not_implemented`는 미구현을 명시적으로 입증한 경우에만 사용한다.
허용된 결손이라는 사실 자체를 expected_missing으로 바꾸지 않는다. 검색 부재는 전역 미구현의 증거가 아니다.

| Coverage | Device Type / Cluster | 분류 | 실제 근거 및 이유 |
|---|---|---|---|
| C005 | Refrigerator / Descriptor | documentation_missing | `src/app/clusters/descriptor/DescriptorCluster.cpp` 존재; `src/app/clusters/descriptor/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C007 | Refrigerator / Fixed Label | documentation_missing | `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp` 존재; `src/app/clusters/fixed-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C008 | Refrigerator / User Label | documentation_missing | `src/app/clusters/user-label-server/UserLabelCluster.cpp` 존재; `src/app/clusters/user-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C010 | Room Air Conditioner / Groups | documentation_missing | `src/app/clusters/groups-server/GroupsClusterImpl.cpp` 존재; `src/app/clusters/groups-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C011 | Room Air Conditioner / On/Off | documentation_missing | `src/app/clusters/on-off-server/OnOffCluster.cpp` 존재; `src/app/clusters/on-off-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C012 | Room Air Conditioner / Scenes Management | documentation_missing | `src/app/clusters/scenes-server/ScenesManagementCluster.cpp` 존재; `src/app/clusters/scenes-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C016 | Room Air Conditioner / Thermostat | documentation_missing | `src/app/clusters/thermostat-server/ThermostatClusterBase.cpp` 존재; `src/app/clusters/thermostat-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C021 | Room Air Conditioner / Descriptor | documentation_missing | `src/app/clusters/descriptor/DescriptorCluster.cpp` 존재; `src/app/clusters/descriptor/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C023 | Room Air Conditioner / Fixed Label | documentation_missing | `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp` 존재; `src/app/clusters/fixed-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C024 | Room Air Conditioner / User Label | documentation_missing | `src/app/clusters/user-label-server/UserLabelCluster.cpp` 존재; `src/app/clusters/user-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C026 | Laundry Washer / On/Off | documentation_missing | `src/app/clusters/on-off-server/OnOffCluster.cpp` 존재; `src/app/clusters/on-off-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C028 | Laundry Washer / Laundry Washer Controls | documentation_missing | `src/app/clusters/laundry-washer-controls-server/LaundryWasherControlsCluster.cpp` 존재; `src/app/clusters/laundry-washer-controls-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C029 | Laundry Washer / Temperature Control | documentation_missing | `src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp` 존재; `src/app/clusters/temperature-control-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C031 | Laundry Washer / Descriptor | documentation_missing | `src/app/clusters/descriptor/DescriptorCluster.cpp` 존재; `src/app/clusters/descriptor/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C033 | Laundry Washer / Fixed Label | documentation_missing | `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp` 존재; `src/app/clusters/fixed-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C034 | Laundry Washer / User Label | documentation_missing | `src/app/clusters/user-label-server/UserLabelCluster.cpp` 존재; `src/app/clusters/user-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C038 | Temperature Controlled Cabinet / Temperature Control | documentation_missing | `src/app/clusters/temperature-control-server/TemperatureControlCluster.cpp` 존재; `src/app/clusters/temperature-control-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C039 | Temperature Controlled Cabinet / Temperature Alarm | unavailable_source | `data_model/1.7/clusters/TemperatureAlarm.xml:60–67`의 provisional 정의, `src/app/zap-templates/zcl/data-model/chip/matter-devices.xml:3263`의 include만 확인. concrete SDK/구현/IDL은 지정 검색 범위에서 발견되지 않음. |
| C041 | Temperature Controlled Cabinet / Descriptor | documentation_missing | `src/app/clusters/descriptor/DescriptorCluster.cpp` 존재; `src/app/clusters/descriptor/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C043 | Temperature Controlled Cabinet / Fixed Label | documentation_missing | `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp` 존재; `src/app/clusters/fixed-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |
| C044 | Temperature Controlled Cabinet / User Label | documentation_missing | `src/app/clusters/user-label-server/UserLabelCluster.cpp` 존재; `src/app/clusters/user-label-server/*.md` 비재귀 검색 0건. 독립 가이드 부재이며 구현 부재가 아니다. |

C039는 documentation_missing도 동반하지만 주 분류는 unavailable_source다. 공통 Alarm Base를 concrete Temperature Alarm 구현으로 대체하지 않는다.
검색 범위·파일 수·모든 검색 hit 및 행별 근거는 [freeze_audit.json](../metadata/freeze_audit.json)의 missing_analysis에 기록했다.
현재 21행에서 Scope 자체의 모순은 확인하지 못했다. 분류는 이 commit과 명시된 검색 범위에 한정한다.
