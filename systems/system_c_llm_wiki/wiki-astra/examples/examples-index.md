---
entity: all
ids: []
source_paths: ['examples/chef/README.md', 'examples/laundry-washer-app/nxp/CMakeLists.txt', 'examples/laundry-washer-app/nxp/README.md', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap', 'examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp', 'examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h', 'examples/all-clusters-app/all-clusters-common/all-clusters-app.matter', 'examples/all-clusters-app/all-clusters-common/all-clusters-app.zap', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h', 'examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.matter', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.zap', 'examples/refrigerator-app/linux/README.md', 'examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h', 'examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
---

# all — Matter 예제 애플리케이션과 데이터 모델

## 개요

이 페이지는 Chef, NXP Laundry Washer, all-clusters-app, refrigerator-app 예제의 빌드 절차, ZAP 데이터 모델, 엔드포인트 구성 및 애플리케이션 delegate를 정리한다.

- **Chef**: Matter 디바이스 유형의 적용 범위를 넓히고, 데이터 모델을 쉽게 구성할 수 있는 샘플 애플리케이션을 제공한다.
- **NXP Laundry Washer**: Project CHIP과 NXP SDK를 기반으로 디바이스 커미셔닝과 클러스터 제어를 보여주는 세탁기 프로토타입이다.
- **all-clusters-app**: 제공된 데이터 모델에 다양한 제어·측정·진단·테스트 클러스터가 구성되어 있다.
- **refrigerator-app**: 온도 제어 엔드포인트와 정적인 온도 단계 목록을 사용하는 냉장고 예제이다.
- **Chef 디바이스 모델**: 실내 에어컨 모델과 냉장고·온도 제어 보관함·팬의 복합 모델이 포함되어 있다.

제공된 `.matter` 파일은 ZAP이 자동 생성한 IDL이며, 열람 및 코드 검토용이다. 클러스터의 전체 선언과 엔드포인트에서 실제 선택한 속성·명령·이벤트는 구분해서 읽어야 한다.

## 예시

### 1. Chef

출처: `examples/chef/README.md`

#### 데이터 모델과 디렉터리

Chef는 shell app을 출발점으로 사용하며, 통합 빌드 스크립트 `chef.py`가 빌드 중 ZAP 파일의 데이터 모델을 처리한다.

| 경로 또는 식별자 | 역할 |
|---|---|
| `<platform>` | 지원 플랫폼별 빌드 시스템과 `main.cpp` |
| `common` | 플랫폼 간 공통 코드 |
| `devices` | 사용 가능한 디바이스 데이터 모델. Matter 1.0 기준 `.zap` 파일 사용 |
| `out` | ZAP 생성 산출물을 배치하는 임시 폴더 |
| `zzz_generated` | CI/CD에서 사용하는 생성 산출물 |
| `sample_app_util` | 새 디바이스 유형의 파일 이름 생성을 위한 지침과 스크립트 |
| `config.yaml` | `chef.py` 설정. Matter 1.0 기준 toolchain 및 TTY 경로 |
| `chef.py` | 샘플 생성용 기본 스크립트 |

새 플랫폼을 포팅할 때는 `<platform>`의 소스 코드를 최소화하고, 플랫폼 비종속 코드는 `common`에 둔다.

`common`에는 `LightingManager`, `LockManager` 같은 기능별 코드를 둘 수 있다. 단, 관련 클러스터 구성의 존재를 동적으로 확인해야 하며, 해당 클러스터 없이 Chef를 빌드하는 사용 사례를 깨뜨려서는 안 된다.

#### 첫 샘플 빌드

1. 대상 플랫폼의 toolchain을 설치한다.
2. `chef.py`를 처음 실행하여 `config.yaml`을 생성한다.
   - `IDF_PATH`가 있으면 esp32의 기본 SDK 경로로 사용한다.
   - `ZEPHYR_BASE`가 있으면 nrfconnect의 기본 SDK 경로로 사용한다.
3. `config.yaml`의 SDK 경로와 `TTY`를 수정한다.
4. `chef.py -u`로 zap과, 지원되는 플랫폼에서는 toolchain을 갱신한다.
5. `chef.py -gzbf -t <platform> -d lighting`을 실행한다.
6. 전체 옵션은 `chef.py -h`로 확인한다.

TTY 예시:

```yaml
# ESP32 macOS
TTY: /dev/tty.usbmodemXXXXXXX

# ESP32 Linux
TTY: /dev/ttyACM0

# NRFCONNECT macOS
TTY: /dev/tty.usbserial-XXXXX

# NRFCONNECT Linux
TTY: /dev/ttyUSB0
```

빌드 명령:

```shell
chef.py -u
chef.py -gzbf -t <platform> -d lighting
chef.py -h
```

`chef.py -gzbf -t <platform> -d lighting`은 다음 순서로 동작한다.

1. ZAP GUI에서 `devices/lighting.zap`을 연다.
2. 데이터 모델 편집을 허용한다.
3. zap 산출물을 생성하여 `zap-generated`에 배치한다.
4. 빌드한다.
5. 대상 장치에 바이너리를 플래시한다.

원문은 일반 생성 산출물 위치를 `out`으로 설명하고, 위 명령의 절차에서는 `zap-generated`를 명시한다.

#### Linux 런타임 옵션

다음 옵션은 생성된 Linux 바이너리의 **런타임 옵션**이며, `chef.py`의 빌드 옵션과 다르다.

| 옵션 | 설명 |
|---|---|
| `--discriminator <discriminator>` | 커미셔닝 중 장치가 광고하는 값과 일치하는 12비트 unsigned integer |
| `--passcode <passcode>` | 커미셔닝 중 소유 증명에 사용하는 27비트 unsigned integer |
| `--spake2p-verifier-base64` | verifier 계산에 `--passcode`를 제공하지 않으면 필요 |
| `--secured-device-port <port>` | 보안 디바이스 메시지 수신 포트. 16비트 unsigned integer, 기본값 `5540` |
| `--KVS <filepath>` | Key Value Store 항목 저장 파일 |
| `-h, --help` | 도움말 출력 후 종료 |

#### CI

- 워크플로: `.github/workflows/chef.yaml`
- 이미지: `chip-build` 기반 플랫폼별 이미지
- toolchain 위치: `/opt`
- 실행 옵션: `--ci -t $PLATFORM`
- 빌드 대상: `cicd_config.json`의 `ci_allow_list`에 있고 `/devices`에도 존재하는 디바이스

각 예제 빌드가 끝나면 `bundle_$PLATFORM`을 호출한다. 이 함수는 빌드 출력 파일을 `_CD_STAGING_DIR`로 복사하거나 이동해야 한다. 일반적으로 플래시에 필요한 최소 파일 집합을 취급하며, `bundle_esp32`를 참고한다.

새 플랫폼 추가 절차:

1. `bundle_$PLATFORM`을 구현한다.
2. 플랫폼 이미지 컨테이너에서 `ci_allow_list`의 예제들이 빌드되는지 확인한다.
3. 빌드와 번들 생성이 확인되면 Chef 워크플로에 작업을 추가한다.
4. `$PLATFORM`을 새 플랫폼으로, `$VERSION`을 워크플로의 이미지 버전으로 치환한다.

로컬 확인:

```shell
docker run -it --mount source=$(pwd),target=/workspace,type=bind ghcr.io/project-chip/chip-build-$PLATFORM:$VERSION
```

컨테이너 내부:

```shell
chown -R $(whoami) /workspace
cd /workspace
source ./scripts/bootstrap.sh
source ./scripts/activate.sh
./examples/chef/chef.py --ci -t $PLATFORM
```

워크플로 예시:

```yaml
chef_$PLATFORM:
    name: Chef - $PLATFORM CI Examples
    runs-on: ubuntu-latest
    if: github.actor != 'restyled-io[bot]'

    container:
        image: ghcr.io/project-chip/chip-build-$PLATFORM:$VERSION
        options: --user root

    steps:
        - name: Checkout
          uses: actions/checkout@v3
        - name: Checkout submodules & Bootstrap
          uses: ./.github/actions/checkout-submodules-and-bootstrap
          with:
              platform: $PLATFORM
        - name: CI Examples $PLATFORM
          shell: bash
          run: |
              ./scripts/run_in_build_env.sh "./examples/chef/chef.py --ci -t $PLATFORM"
```

#### CD

CI가 활성화된 플랫폼은 `integrations/cloudbuild/`의 `chef.yaml`에 통합할 수 있다.

- CD 이미지: `chip-build-vscode`
- 이미지 소스: `docker/images/chip-build-vscode/Dockerfile`
- 이 이미지는 개별 toolchain 이미지들을 결합한다.
- 새 플랫폼 통합 전 toolchain을 `chip-build-vscode`로 복사하고 `chef.yaml`의 이미지 버전을 갱신한다.
- `cicd_config.json`의 `cd_platforms`에 플랫폼을 추가한다.

원문 구성 형식:

```json
"$PLATFORM": {
    "output_archive_prefix_1": ["option_1", "option_2"],
    "output_archive_prefix_2": [],
}
```

`linux` 구성:

```json
"linux": {
    "linux_x86": ["--cpu_type", "x64"],
    "linux_arm64_ipv6only": ["--cpu_type", "arm64", "--ipv6only"]
},
```

각 옵션 배열은 해당 대상의 빌드 명령에 추가된다. 원문의 설명에는 출력 접두사가 `linux_x86`, `linux_arm_64_ipv6only`로 적혀 있어, 구성 키 `linux_arm64_ipv6only`와 표기가 다르다.

로컬 확인:

```shell
docker run -it --mount source=$(pwd),target=/workspace,type=bind ghcr.io/project-chip/chip-build-vscode:$VERSION
```

컨테이너 내부:

```shell
chown -R $(whoami) /workspace
cd /workspace
source ./scripts/bootstrap.sh
source ./scripts/activate.sh
./examples/chef/chef.py --build_all --keep_going
```

`integrations/cloudbuild/`의 `README`에 설명된 Google Cloud Build local builder도 사용할 수 있다.

#### 새 디바이스 추가

새 디바이스 유형 생성은 [NEW_CHEF_DEVICES.md](NEW_CHEF_DEVICES.md)를 참고한다.

1. 다음 명령으로 파일 이름을 변경하고 새 파일을 `examples/chef/devices`에 배치한다.

   ```shell
   python sample_app_util.py zap <zap_file> --rename-file
   ```

2. 생성 파일을 갱신한다.

   ```shell
   scripts/tools/zap_regen_all.py
   ```

3. `zzz_generated`와 `examples/chef/devices`를 커밋한다.

이 과정은 `.github/workflows/zap_templates.yaml`에 의해 검증된다. 저장소에 추가되는 모든 디바이스는 CD에서 빌드된다.

#### 제조사 확장과 Custom Clusters

`rootnode_onofflight_meisample*`은 제조사 정의 기능을 사용하는 예제이다. `Sample MEI` 클러스터 정의 위치:

```text
src/app/zap-templates/zcl/data-model/chip/sample-mei-cluster.xml
```

| 항목 | 정의 |
|---|---|
| `flip-flop` | boolean 속성 |
| `ping` | 인자가 없는 명령 |
| `add-arguments` | 두 `uint8` 인자를 받고, 응답 명령으로 합을 반환하는 명령/응답 쌍 |

시험 명령:

```shell
# commissioning of on-network chef device
chip-tool pairing onnetwork 1 20202021
# tests command to sum arguments: returns 30
chip-tool samplemei add-arguments 1 1 10 20
# sets Flip-Flop to false
chip-tool samplemei write flip-flop 0 1 1
# reads Flip-Flop
chip-tool samplemei read flip-flop 1 1
```

### 2. ZAP 및 IDL의 공통 구성

제공된 `.zap` 파일은 다음 메타데이터를 사용한다.

| 키 | 값 |
|---|---|
| `fileFormat` | `2` |
| `featureLevel` | `107` |
| `creator` | `"zap"` |
| `commandDiscovery` | `"1"` |
| `defaultResponsePolicy` | `"always"` |
| `manufacturerCodes` | `"0x1002"` |
| `profileId` | `259` |
| `networkId` | `0` |

패키지 경로:

| 대상 | 원문 경로 |
|---|---|
| NXP Laundry Washer | `../../../../src/app/zap-templates/zcl/zcl.json` |
| NXP Laundry Washer | `../../../../src/app/zap-templates/app-templates.json` |
| all-clusters-app, Chef 디바이스, refrigerator-app | `../../../src/app/zap-templates/zcl/zcl.json` |
| all-clusters-app, Chef 디바이스, refrigerator-app | `../../../src/app/zap-templates/app-templates.json` |

패키지 `pathRelativity`는 `"relativeToZap"`이다. 데이터 패키지는 `"zcl-properties"`, 템플릿 패키지는 `"gen-templates-json"`이고, 템플릿 버전은 `"chip-v1"`이다.

#### 공통 전역 속성

IDL과 ZAP은 속성 이름의 대소문자 및 표기가 다르다.

| IDL 이름 | ZAP 이름 | ID | IDL 타입 |
|---|---|---:|---|
| `generatedCommandList` | `GeneratedCommandList` | 65528 | `command_id[]` |
| `acceptedCommandList` | `AcceptedCommandList` | 65529 | `command_id[]` |
| `attributeList` | `AttributeList` | 65531 | `attrib_id[]` |
| `featureMap` | `FeatureMap` | 65532 | `bitmap32` |
| `clusterRevision` | `ClusterRevision` | 65533 | `int16u` |

클러스터 선언에 존재하더라도 엔드포인트 구성에 모든 항목이 명시되는 것은 아니다.

#### 공통 전역 타입

제공된 IDL에는 다음 전역 타입들이 반복해서 선언된다.

- 열거형: `AreaTypeTag`, `AtomicRequestTypeEnum`, `CertificationTypeEnum`, `LandmarkTag`, `LocationTag`, `MeasurementTypeEnum`, `MediumType`, `PositionTag`, `PowerThresholdSourceEnum`, `RelativePositionTag`, `SoftwareVersionCertificationStatusEnum`, `StreamUsageEnum`, `TariffPriceTypeEnum`, `TariffUnitEnum`, `TestGlobalEnum`, `ThreeLevelAutoEnum`, `WebRTCEndReasonEnum`
- 비트맵: `TestGlobalBitmap`
- 구조체: `CurrencyStruct`, `PriceStruct`, `MeasurementAccuracyRangeStruct`, `MeasurementAccuracyStruct`, `AtomicAttributeStatusStruct`, `ICECandidateStruct`, `ICEServerStruct`, `LocationDescriptorStruct`, `PowerThresholdStruct`, `SemanticTagStruct`, `TestGlobalStruct`, `ViewportStruct`, `WebRTCSessionStruct`

`WebRTCSessionStruct`는 `fabric_scoped`이며, `fabricIndex`의 필드 번호는 `254`이다.

### 3. NXP Laundry Washer

#### 지원 플랫폼

출처: `examples/laundry-washer-app/nxp/README.md`

| 플랫폼 | 안내 |
|---|---|
| RW61x (Zephyr OS) | [NXP Zephyr Guide](../../../docs/platforms/nxp/nxp_zephyr_guide.md) |
| RW61x (FreeRTOS OS) | [NXP RW61x (FreeRTOS) Guide](../../../docs/platforms/nxp/nxp_rw61x_guide.md) |
| RT1170 | [NXP RT1170 Guide](../../../docs/platforms/nxp/nxp_rt1170_guide.md) |
| RT1060 | [NXP RT1060 Guide](../../../docs/platforms/nxp/nxp_rt1060_guide.md) |

환경 설정, 빌드 및 시험은 다음 문서를 사용한다.

- [CHIP NXP Examples Guide for FreeRTOS platforms](../../../docs/platforms/nxp/nxp_examples_freertos_platforms.md)
- [NXP Zephyr Application](../../../docs/platforms/nxp/nxp_zephyr_guide.md)

Matter-over-WiFi + Thread Border Router 구성은 지원하지 않는다.

#### CMake 구성

출처: `examples/laundry-washer-app/nxp/CMakeLists.txt`

| 항목 | 구성 |
|---|---|
| CMake 최소 버전 | `3.30` |
| `CMAKE_EXPORT_COMPILE_COMMANDS` | `ON` |
| 프로젝트 | `chip-nxp-laundry-washer-app-example` |
| SDK 조회 | `find_package(McuxSDK 3.0.0)` |
| Kconfig 루트 | `${CMAKE_CURRENT_SOURCE_DIR}/Kconfig` |
| 애플리케이션 설정 | `${CMAKE_CURRENT_SOURCE_DIR}/prj.conf` |
| 외부 모듈 | `${CHIP_ROOT}/config/nxp/chip-cmake-freertos` |
| 데이터 모델 구성 파일 | `${CHIP_ROOT}/src/app/chip_data_model.cmake` |
| NXP 공통 애플리케이션 | `${EXAMPLE_PLATFORM_NXP_COMMON_DIR}/app_common.cmake` |

- `CHIP_ROOT`가 지정되면 `get_filename_component`로 절대 경로로 변환한다.
- 지정되지 않으면 `${CMAKE_CURRENT_SOURCE_DIR}/../../../`의 `REALPATH`를 사용한다.
- `COMMON_KCONFIG_ENV_SETTINGS`에 `CHIP_ROOT=${CHIP_ROOT}`를 설정한다.
- `CONF_FILE_NAME`이 있으면 `${CHIP_ROOT}/examples/platform/nxp/config/${CONF_FILE_NAME}`을 `CONF_FILE` 앞에 추가한다.
- 애플리케이션의 `prj.conf`는 다시 `CONF_FILE` 맨 앞에 추가한다.
- `CONFIG_CHIP_EXTERNAL_TARGETS`에 `McuxSDK`를 추가한다.
- `NXP_SDK_RECONFIG_CMAKE_DIR`가 없으면 `${NXP_MATTER_SUPPORT_DIR}/examples/platform/${CONFIG_CHIP_NXP_PLATFORM_FAMILY}`을 사용한다.
- `${NXP_SDK_RECONFIG_CMAKE_DIR}/nxp_sdk_reconfig.cmake`를 포함한다.

경로 변수:

| 변수 | 원문 경로 |
|---|---|
| `GEN_DIR` | `${CHIP_ROOT}/zzz_generated/` |
| `NXP_EXAMPLE_DIR` | `${CMAKE_CURRENT_SOURCE_DIR}/common` |
| `NXP_EXAMPLE_ZAP_DIR` | `${CMAKE_CURRENT_SOURCE_DIR}/zap` |
| `ALL_CLUSTERS_COMMON_DIR` | `${CHIP_ROOT}/examples/all-clusters-app/all-clusters-common` |
| `EXAMPLE_PLATFORM_NXP_COMMON_DIR` | `${CHIP_ROOT}/examples/platform/nxp/common` |
| `NXP_MATTER_SUPPORT_DIR` | `${CHIP_ROOT}/third_party/nxp/nxp_matter_support` |

`app`의 include 경로:

```text
${ALL_CLUSTERS_COMMON_DIR}/include
${NXP_EXAMPLE_DIR}/main/include
${GEN_DIR}/app-common
```

`target_sources`에 포함되는 파일:

```text
${NXP_EXAMPLE_DIR}/main/main.cpp
${NXP_EXAMPLE_DIR}/main/AppTask.cpp
${NXP_EXAMPLE_DIR}/main/DeviceCallbacks.cpp
${NXP_EXAMPLE_DIR}/main/ZclCallbacks.cpp
${NXP_EXAMPLE_DIR}/main/laundry-washer-mode.cpp
${ALL_CLUSTERS_COMMON_DIR}/src/binding-handler.cpp
${ALL_CLUSTERS_COMMON_DIR}/src/laundry-washer-controls-delegate-impl.cpp
${ALL_CLUSTERS_COMMON_DIR}/src/static-supported-temperature-levels.cpp
${ALL_CLUSTERS_COMMON_DIR}/src/operational-state-delegate-impl.cpp
```

네트워크 구성 분기:

| 조건 | 동작 |
|---|---|
| `CONFIG_CHIP_ETHERNET` | `FATAL_ERROR`: `Ethernet configuration is not supported in this application.` |
| `CONFIG_CHIP_WIFI AND CONFIG_NET_L2_OPENTHREAD` | `FATAL_ERROR`: `WiFi + Thread (Border Router) configuration is not supported in this application.` |
| `CONFIG_CHIP_WIFI AND NOT CONFIG_NET_L2_OPENTHREAD` | `chip_configure_data_model` 호출 |
| `CONFIG_NET_L2_OPENTHREAD AND NOT CONFIG_CHIP_WIFI` | `chip_configure_data_model` 호출 |

두 데이터 모델 구성 분기는 동일한 호출을 사용한다.

```cmake
chip_configure_data_model(app
    INCLUDE_SERVER
    ZAP_FILE ${NXP_EXAMPLE_ZAP_DIR}/laundry-washer-app.zap
)
```

#### 엔드포인트

출처:

- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter`
- `examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap`

| endpoint | IDL 디바이스 유형 | 코드 | version |
|---:|---|---:|---:|
| 0 | `ma_rootdevice` | 22 | 5 |
| 0 | `ma_otarequestor` | 18 | 1 |
| 1 | `ma_laundry_washer` | 115 | 1 |

ZAP의 디바이스 이름은 각각 `MA-rootdevice`, `MA-otarequestor`, `MA-laundry-washer`이다. 두 엔드포인트의 `parentEndpointIdentifier`는 `null`이다.

**endpoint 0**의 서버 클러스터:

`Descriptor`, `AccessControl`, `BasicInformation`, `OtaSoftwareUpdateRequestor`, `LocalizationConfiguration`, `UnitLocalization`, `GeneralCommissioning`, `NetworkCommissioning`, `DiagnosticLogs`, `GeneralDiagnostics`, `SoftwareDiagnostics`, `WiFiNetworkDiagnostics`, `AdministratorCommissioning`, `OperationalCredentials`, `GroupKeyManagement`

`OtaSoftwareUpdateProvider`는 binding cluster로 선언되어 있고, ZAP에서 `side: "client"`인 활성 클러스터이다.

**endpoint 1**의 서버 클러스터:

| 클러스터 | ID | IDL revision | 구성된 처리 명령 |
|---|---:|---:|---|
| `Identify` | 3 | 6 | `Identify`, `TriggerEffect` |
| `Groups` | 4 | 5 | `AddGroup`, `ViewGroup`, `GetGroupMembership`, `RemoveGroup`, `RemoveAllGroups`, `AddGroupIfIdentifying` |
| `OnOff` | 6 | 7 | `Off`, `On`, `Toggle`, `OffWithEffect`, `OnWithRecallGlobalScene`, `OnWithTimedOff` |
| `Descriptor` | 29 | 3 | 없음 |
| `Binding` | 30 | 1 | 없음 |
| `UserLabel` | 65 | 1 | 없음 |
| `LaundryWasherMode` | 81 | 4 | `ChangeToMode` |
| `LaundryWasherControls` | 83 | 2 | 없음 |
| `TemperatureControl` | 86 | 1 | `SetTemperature` |
| `OperationalState` | 96 | 3 | `Pause`, `Stop`, `Start`, `Resume` |

#### `LaundryWasherMode`

IDL 속성:

| 이름 | ID | 타입 | 한정자 |
|---|---:|---|---|
| `supportedModes` | 0 | `ModeOptionStruct[]` | `readonly` |
| `currentMode` | 1 | `int8u` | `readonly` |
| `coreModeTags` | 4 | `enum16[]` | `provisional readonly optional` |

`Feature`에는 `kCoreModes = 0x2`가 선언된다.

```text
ChangeToMode(ChangeToModeRequest): ChangeToModeResponse = 0
ChangeToModeByCoreTag(ChangeToModeByCoreTagRequest): ChangeToModeResponse = 2
```

- `ChangeToModeRequest`: `int8u newMode = 0`
- `ChangeToModeByCoreTagRequest`: `enum16 newModeTag = 0`
- `ChangeToModeResponse = 1`: `enum8 status = 0`, `optional char_string<64> statusText = 1`

endpoint 1에는 `supportedModes`, `currentMode`가 구성되어 있고, `ChangeToMode`만 처리 명령으로 선택되어 있다. `clusterRevision` 기본값은 `0x0004`이다.

모드 옵션은 `examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h`에서 정적으로 정의한다.

| 상수 | 값 | `label` | `modeTags` |
|---|---:|---|---|
| `ModeNormal` | 0 | `"Normal"_span` | `ModeTag::kNormal` |
| `ModeDelicate` | 1 | `"Delicate"_span` | `ModeTag::kDelicate`, `ModeBase::ModeTag::kNight`, `ModeBase::ModeTag::kQuiet` |
| `ModeHeavy` | 2 | `"Heavy"_span` | `ModeBase::ModeTag::kMax`, `ModeTag::kHeavy` |
| `ModeWhites` | 3 | `"Whites"_span` | `ModeTag::kWhites` |

`LaundryWasherModeDelegate`는 `ModeBase::Delegate`를 상속한다. `kModeOptions[4]`의 각 항목은 `label`, `mode`, `modeTags`로 구성되고, 태그의 `mfgCode`는 `{}`이다.

출처: `examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp`

| 함수 | 제공된 코드의 동작 |
|---|---|
| `LaundryWasherModeDelegate::Init` | `CHIP_NO_ERROR` 반환 |
| `LaundryWasherModeDelegate::HandleChangeToMode` | `response.status`를 `to_underlying(ModeBase::StatusCode::kSuccess)`로 설정 |
| `LaundryWasherModeDelegate::GetModeLabelByIndex` | `kModeOptions`의 label을 `chip::CopyCharSpanToMutableCharSpan`으로 복사 |
| `LaundryWasherModeDelegate::GetModeValueByIndex` | 선택 항목의 `mode`를 `value`에 대입 |
| `LaundryWasherModeDelegate::GetModeTagsByIndex` | `std::copy`로 태그를 복사하고 `tags.reduce_size` 호출 |
| `LaundryWasherMode::Instance` | `gLaundryWasherModeInstance` 반환 |
| `LaundryWasherMode::Shutdown` | instance와 delegate 삭제 후 포인터를 `nullptr`로 설정 |

세 인덱스 조회 함수는 범위를 벗어나면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다. `GetModeTagsByIndex`는 출력 목록의 크기가 부족하면 `CHIP_ERROR_INVALID_ARGUMENT`를 반환한다.

초기화:

```cpp
void MatterLaundryWasherModeClusterInitCallback(chip::EndpointId endpointId)
{
    VerifyOrDie(endpointId == 1); // this cluster is only enabled for endpoint 1.
    VerifyOrDie(gLaundryWasherModeDelegate == nullptr && gLaundryWasherModeInstance == nullptr);
    gLaundryWasherModeDelegate = new LaundryWasherMode::LaundryWasherModeDelegate;
    gLaundryWasherModeInstance = new ModeBase::Instance(gLaundryWasherModeDelegate, 0x1, LaundryWasherMode::Id, 0);
    TEMPORARY_RETURN_IGNORED gLaundryWasherModeInstance->Init();
}
```

`MatterLaundryWasherModeClusterShutdownCallback`도 `endpointId == 1`을 확인한다. instance가 있으면 instance의 `Shutdown`을 호출한 뒤 `LaundryWasherMode::Shutdown`으로 객체를 해제한다.

`HandleChangeToMode`의 제공된 본문에는 `NewMode`에 따른 추가 비즈니스 로직이 없다.

#### `LaundryWasherControls`

IDL 정의:

| 속성 | ID | 타입 | 한정자 |
|---|---:|---|---|
| `spinSpeeds` | 0 | `char_string[]` | `readonly optional` |
| `spinSpeedCurrent` | 1 | `int8u` | `optional nullable` |
| `numberOfRinses` | 2 | `NumberOfRinsesEnum` | `optional` |
| `supportedRinses` | 3 | `NumberOfRinsesEnum[]` | `readonly optional` |

- `kSpin = 0x1`
- `kRinse = 0x2`
- endpoint 1의 `featureMap` 기본값은 `3`이다.

`NumberOfRinsesEnum`:

```text
kNone = 0
kNormal = 1
kExtra = 2
kMax = 3
```

공통 delegate 파일:

- `examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h`
- `examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp`

`LaundryWasherControlDelegate`는 `Delegate`를 상속하고 옵션을 정적으로 정의한다.

| 목록 | 순서대로 정의된 항목 |
|---|---|
| `spinSpeedsNameOptions` | `"Off"_span`, `"Low"_span`, `"Medium"_span`, `"High"_span` |
| `supportRinsesOptions` | `NumberOfRinsesEnum::kNormal`, `NumberOfRinsesEnum::kExtra` |

- `GetSpinSpeedAtIndex`는 문자열을 `chip::CopyCharSpanToMutableCharSpan`으로 복사한다.
- `GetSupportedRinseAtIndex`는 해당 열거형을 `supportedRinse`에 대입하고 `CHIP_NO_ERROR`를 반환한다.
- 두 함수 모두 목록의 끝을 넘으면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.
- `getLaundryWasherControlDelegate`는 정적 `instance`의 참조를 반환한다.

등록 위치: `examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp`

```cpp
void emberAfLaundryWasherControlsClusterInitCallback(EndpointId endpoint)
{
    LaundryWasherControlsServer::SetDefaultDelegate(endpoint, &LaundryWasherControlDelegate::getLaundryWasherControlDelegate());
}
```

#### `OperationalState`

endpoint 1은 다음 readonly 속성을 구성한다.

| 속성 | ID | 타입 |
|---|---:|---|
| `phaseList` | 0 | `nullable char_string[]` |
| `currentPhase` | 1 | `nullable int8u` |
| `countdownTime` | 2 | `optional nullable elapsed_s` |
| `operationalStateList` | 3 | `OperationalStateStruct[]` |
| `operationalState` | 4 | `OperationalStateEnum` |
| `operationalError` | 5 | `ErrorStateStruct` |

`OperationalStateEnum`은 `kStopped = 0`, `kRunning = 1`, `kPaused = 2`, `kError = 3`이다.

`ErrorStateEnum`은 `kNoError = 0`, `kUnableToStartOrResume = 1`, `kUnableToCompleteOperation = 2`, `kCommandInvalidInState = 3`이다.

| 명령 | ID | 응답 |
|---|---:|---|
| `Pause` | 0 | `OperationalCommandResponse` |
| `Stop` | 1 | `OperationalCommandResponse` |
| `Start` | 2 | `OperationalCommandResponse` |
| `Resume` | 3 | `OperationalCommandResponse` |

`OperationalCommandResponse = 4`는 `ErrorStateStruct commandResponseState = 0`을 포함한다.

구성된 이벤트:

- `OperationalError = 0`
  - 우선순위: `critical`
  - `ErrorStateStruct errorState = 0`
- `OperationCompletion = 1`
  - 우선순위: `info`
  - `enum8 completionErrorCode = 0`
  - `optional nullable elapsed_s totalOperationalTime = 1`
  - `optional nullable elapsed_s pausedTime = 2`

#### `OnOff` 변경 전달과 모드 갱신

관련 파일:

- `examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp`
- `examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp`
- `examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h`

처리 흐름:

1. `MatterPostAttributeChangeCallback`이 다음 호출로 DeviceManager의 콜백을 얻는다.
   ```cpp
   chip::DeviceManager::CHIPDeviceManager::GetInstance().GetCHIPDeviceManagerCallbacks()
   ```
2. 콜백이 `nullptr`가 아니면 `PostAttributeChangeCallback`에 `path.mEndpointId`, `path.mClusterId`, `path.mAttributeId`, `type`, `size`, `value`를 전달한다.
3. `LaundryWasherApp::DeviceCallbacks::PostAttributeChangeCallback`이 변경 정보를 로그로 기록한다.
4. `clusterId`가 `Clusters::OnOff::Id`이면 `OnOnOffPostAttributeChangeCallback`을 호출한다.
5. `attributeId`가 `Clusters::OnOff::Attributes::OnOff::Id`이고 `value != nullptr`, `*value == true`이면 모드 instance를 조회한다.
6. instance가 있고 `GetOnMode()`의 결과가 null이 아니면 `UpdateCurrentMode(mode.Value())`를 호출한다.

```cpp
if ((value != nullptr) && (*value == true))
{
    ModeBase::Instance * modeInstance = LaundryWasherMode::Instance();

    if (modeInstance != nullptr)
    {
        DataModel::Nullable<uint8_t> mode = modeInstance->GetOnMode();
        if (mode.IsNull() == false)
        {
            modeInstance->UpdateCurrentMode(mode.Value());
        }
    }
}
```

`LaundryWasherApp::DeviceCallbacks`는 `chip::NXP::App::CommonDeviceCallbacks`를 상속한다. `GetDefaultInstance`는 함수 내부의 정적 `sDeviceCallbacks`를 반환한다.

헤더에는 `OnIdentifyPostAttributeChangeCallback`도 선언되지만, 제공된 `.cpp`에는 해당 함수 본문이 없다.

### 4. `TemperatureControl` 사용 비교

`TemperatureControl = 86`의 IDL `revision`은 `1`이다.

| Feature | 값 |
|---|---|
| `kTemperatureNumber` | `0x1` |
| `kTemperatureLevel` | `0x2` |
| `kTemperatureStep` | `0x4` |

모든 전용 속성은 `readonly optional`이다.

| 속성 | ID | 타입 |
|---|---:|---|
| `temperatureSetpoint` | 0 | `temperature` |
| `minTemperature` | 1 | `temperature` |
| `maxTemperature` | 2 | `temperature` |
| `step` | 3 | `temperature` |
| `selectedTemperatureLevel` | 4 | `int8u` |
| `supportedTemperatureLevels` | 5 | `char_string[]` |

```text
SetTemperature(SetTemperatureRequest): DefaultSuccess = 0
```

`SetTemperatureRequest`:

```text
optional temperature targetTemperature = 0
optional int8u targetTemperatureLevel = 1
```

| 예제 | endpoint | 선택된 전용 속성 | `featureMap` 기본값 |
|---|---|---|---|
| NXP Laundry Washer | 1 | `selectedTemperatureLevel`, `supportedTemperatureLevels` | `2` |
| all-clusters-app | 1 | `selectedTemperatureLevel`, `supportedTemperatureLevels` | `2` |
| refrigerator-app | 2, 3 | `selectedTemperatureLevel`, `supportedTemperatureLevels` | `2` |
| Chef 냉장고 복합 모델 | 2, 3 | `temperatureSetpoint`, `minTemperature`, `maxTemperature`, `step` | `5` |

모든 행의 엔드포인트에는 `SetTemperature`가 처리 명령으로 구성되어 있다.

### 5. refrigerator-app

#### 엔드포인트 구성

출처:

- `examples/refrigerator-app/refrigerator-common/refrigerator-app.matter`
- `examples/refrigerator-app/refrigerator-common/refrigerator-app.zap`

| endpoint | 디바이스 유형 | 코드 | version | 서버 구성 |
|---:|---|---:|---:|---|
| 0 | `ma_rootdevice` | 22 | 5 | 노드 관리 클러스터 |
| 1 | `ma_refrigerator` | 112 | 1 | `Descriptor` |
| 2 | `ma_temperature_controlled_cabinet` | 113 | 1 | `Descriptor`, `TemperatureControl` |
| 3 | `ma_temperature_controlled_cabinet` | 113 | 1 | `Descriptor`, `TemperatureControl` |

ZAP에서 모든 `parentEndpointIdentifier`는 `null`이다.

endpoint 0의 서버 클러스터:

`Descriptor`, `AccessControl`, `BasicInformation`, `UnitLocalization`, `GeneralCommissioning`, `NetworkCommissioning`, `GeneralDiagnostics`, `WiFiNetworkDiagnostics`, `AdministratorCommissioning`, `OperationalCredentials`, `GroupKeyManagement`

- `UnitLocalization.featureMap` 기본값: `1`
- `WiFiNetworkDiagnostics.featureMap` 기본값: `3`
- `AdministratorCommissioning.featureMap` 기본값: `0`
- 처리하는 `AdministratorCommissioning` 명령: `OpenCommissioningWindow`, `RevokeCommissioning`
- `GeneralDiagnostics.testEventTriggersEnabled` 기본값: `false`

#### 정적 온도 단계 delegate

출처:

- `examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h`
- `examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp`

`AppSupportedTemperatureLevelsDelegate`는 `SupportedTemperatureLevelsIteratorDelegate`를 상속한다.

`EndpointPair`는 다음 필드를 갖는다.

```cpp
EndpointId mEndpointId;
CharSpan * mTemperatureLevels;
uint8_t mSize;
```

정적 온도 단계:

```cpp
CharSpan AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions[] = { "Hot"_span, "Warm"_span, "Freezing"_span };
```

`supportedOptionsByEndpoints`의 크기는 `MATTER_DM_TEMPERATURE_CONTROL_CLUSTER_SERVER_ENDPOINT_COUNT`이며, endpoint `2`와 `3`을 동일한 `temperatureLevelOptions`에 연결한다.

| 함수 | 동작 |
|---|---|
| `AppSupportedTemperatureLevelsDelegate::Size` | `mEndpoint`와 일치하는 항목의 `mSize` 반환. 없으면 `0` 반환 |
| `AppSupportedTemperatureLevelsDelegate::Next` | 일치하는 endpoint의 `mIndex` 항목을 `item`으로 복사 |

`Next`의 처리:

1. `endpointPair.mEndpointId == mEndpoint`인 항목을 찾는다.
2. `endpointPair.mSize > mIndex`이면 `CopyCharSpanToMutableCharSpan`을 호출한다.
3. 복사 실패 시 `ChipLogError`로 기록하고 해당 오류를 반환한다.
4. 복사 성공 시 `mIndex`를 증가시키고 `CHIP_NO_ERROR`를 반환한다.
5. 일치하는 다음 항목이 없으면 `CHIP_ERROR_PROVIDER_LIST_EXHAUSTED`를 반환한다.

원문에는 엔드포인트별 옵션을 구성하라는 `TODO`가 있다.

#### Linux 빌드

출처: `examples/refrigerator-app/linux/README.md`

문서의 시험 환경:

- Ubuntu for Raspberry Pi Server 20.04 LTS (aarch64)
- Ubuntu for Raspberry Pi Desktop 20.10 (aarch64)

x64 호스트에서 교차 컴파일하여 NXP i.MX 8M Mini EVK에서 실행하는 절차는 [README document](../../../docs/platforms/nxp/nxp_imx8m_linux_examples.md)를 참고한다.

toolchain 설치:

```shell
sudo apt-get install git gcc g++ python pkg-config libssl-dev libdbus-1-dev libglib2.0-dev ninja-build python3-venv python3-dev unzip
```

빌드:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
git submodule update --init
source third_party/connectedhomeip/scripts/activate.sh
gn gen out/debug
ninja -C out/debug
```

생성된 실행 파일·라이브러리·객체 파일 삭제:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
rm -rf out/
```

pigweed RPC 활성화 빌드:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
git submodule update --init
source third_party/connectedhomeip/scripts/activate.sh
gn gen out/debug --args='import("//with_pw_rpc.gni")'
ninja -C out/debug
```

#### 런타임 및 Raspberry Pi 4

| 옵션 | 설명 |
|---|---|
| `--wifi` | WiFi 관리 기능 활성화. WiFi 커미셔닝에 필요 |
| `--thread` | Thread 관리 기능 활성화. 실행 중인 ot-br-posix dbus daemon 필요 |
| `--ble-controller <selector>` | BLE 광고 및 연결에 사용할 Bluetooth controller 선택 |

전제 조건:

- Raspberry Pi 4
- ARM64용 Ubuntu 20.04 이상 이미지
- USB Bluetooth Dongle
  - Ubuntu desktop의 Bluetooth 광고가 CHIP BLE 연결을 방해할 수 있다.
  - Ubuntu server에서는 APT로 `pi-bluetooth`를 설치한다.

Echo 시험을 위한 빌드:

```shell
gn gen out/debug --args='chip_app_use_echo=true'
ninja -C out/debug
```

실행:

```shell
cd ~/connectedhomeip/examples/refrigerator-app/linux
sudo out/debug/chip-refrigerator-app --ble-controller [bluetooth device number]
# In this example, the device we want to use is hci1
sudo out/debug/chip-refrigerator-app --ble-controller 1
```

실행 후 노트북이나 워크스테이션의 `ChipDeviceController`로 시험한다. controller 선택은 [Linux BLE Settings](/platforms/linux/ble_settings.md)를 참고한다.

#### RPC Console과 tracing

RPC 활성화 빌드를 수행하면 `chip_rpc` Python interactive console이 venv에 설치된다. wheel 파일은 `out/debug/chip_rpc_console_wheels`에 생성된다.

재빌드 없이 설치:

```shell
pip3 install out/debug/chip_rpc_console_wheels/*.whl
```

콘솔 실행:

```shell
chip-console -s localhost:33000 -o /<YourFolder>/pw_log.out
```

Device tracing은 RPC 활성화 빌드가 필요하다.

```shell
./{PIGWEED_REPO}/pw_trace_tokenized/py/pw_trace_tokenized/get_trace.py -s localhost:33000 \
 -o {OUTPUT_FILE} -t {ELF_FILE} {PIGWEED_REPO}/pw_trace_tokenized/pw_trace_protos/trace_rpc.proto
```

### 6. Chef 냉장고 복합 모델

출처:

- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter`
- `examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap`

#### 구성 및 부모 관계

| endpoint | IDL 디바이스 유형 | 코드 | version | `parentEndpointIdentifier` |
|---:|---|---:|---:|---|
| 0 | `ma_rootdevice` | 22 | 5 | `null` |
| 1 | `ma_refrigerator` | 112 | 1 | `null` |
| 2 | `ma_temperature_controlled_cabinet` | 113 | 1 | `1` |
| 3 | `ma_temperature_controlled_cabinet` | 113 | 1 | `1` |
| 4 | `ma_fan` | 43 | 5 | `2` |

endpoint `2`, `3`은 `1`의 하위 엔드포인트이며, endpoint `4`는 `2`의 하위 엔드포인트로 ZAP에 설정되어 있다.

endpoint 0의 서버 클러스터:

`Descriptor`, `AccessControl`, `BasicInformation`, `UnitLocalization`, `GeneralCommissioning`, `NetworkCommissioning`, `GeneralDiagnostics`, `WiFiNetworkDiagnostics`, `AdministratorCommissioning`, `OperationalCredentials`, `GroupKeyManagement`

`AdministratorCommissioning.featureMap` 기본값은 `0x1`이며, `OpenCommissioningWindow`, `OpenBasicCommissioningWindow`, `RevokeCommissioning`을 처리한다.

#### 냉장고와 온도 제어 보관함

| endpoint | 서버 클러스터 |
|---:|---|
| 1 | `Descriptor`, `RefrigeratorAndTemperatureControlledCabinetMode`, `RefrigeratorAlarm` |
| 2, 3 | `Descriptor`, `TemperatureControl`, `TemperatureMeasurement` |
| 4 | `Identify`, `Descriptor`, `FanControl` |

endpoint 1의 `RefrigeratorAndTemperatureControlledCabinetMode = 82`:

- IDL `revision 4`
- `supportedModes`, `currentMode` 구성
- `clusterRevision` 기본값 `0x0004`
- 처리 명령 `ChangeToMode`
- 전용 모드 태그 `kRapidCool = 16384`, `kRapidFreeze = 16385`

endpoint 1의 `RefrigeratorAlarm = 87`:

- IDL `revision 1`
- `mask` 기본값 `0x1`
- `state` 기본값 `0`
- `supported` 기본값 `0x1`
- `featureMap` 기본값 `0`
- 이벤트 `Notify = 0`
- `Notify` 필드: `active`, `inactive`, `state`, `mask`
- `AlarmBitmap` 항목: `kDoorOpen = 0x1`

온도 설정 기본값:

| 속성 | endpoint 2 | endpoint 3 |
|---|---:|---:|
| `temperatureSetpoint` | 200 | -1800 |
| `minTemperature` | 200 | -1800 |
| `maxTemperature` | 400 | -1500 |
| `step` | 10 | 10 |
| `TemperatureControl.featureMap` | 5 | 5 |
| `minMeasuredValue` | -4000 | -4000 |
| `maxMeasuredValue` | 2000 | 2000 |

두 보관함의 `Descriptor`에는 `tagList`가 구성되어 있다.

#### 팬

endpoint 4의 `FanControl = 514`:

| 속성 | 기본값 |
|---|---|
| `fanModeSequence` | `2` |
| `speedMax` | `10` |
| `rockSupport` | `0x03` |
| `windSupport` | `0x03` |
| `featureMap` | `63` |

`fanMode`, `percentSetting`, `percentCurrent`, `speedSetting`, `speedCurrent`, `rockSetting`, `windSetting`, `airflowDirection`도 구성되어 있다.

처리 명령은 `Step`이다. IDL `StepRequest`는 다음 필드를 포함한다.

```text
StepDirectionEnum direction = 0
optional boolean wrap = 1
optional boolean lowestOff = 2
```

### 7. Chef 실내 에어컨 모델

출처:

- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter`
- `examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap`

#### 엔드포인트

| endpoint | IDL 디바이스 유형 | 코드 | version | `parentEndpointIdentifier` |
|---:|---|---:|---:|---|
| 0 | `ma_rootdevice` | 22 | 5 | `null` |
| 1 | `ma_room_airconditioner` | 114 | 5 | `null` |
| 2 | `ma_tempsensor` | 770 | 1 | `1` |
| 3 | `ma_humiditysensor` | 775 | 1 | `1` |

endpoint 0의 서버 클러스터:

`Descriptor`, `AccessControl`, `BasicInformation`, `GeneralCommissioning`, `NetworkCommissioning`, `DiagnosticLogs`, `GeneralDiagnostics`, `AdministratorCommissioning`, `OperationalCredentials`, `GroupKeyManagement`

endpoint 1에는 `Identify`, `Groups`, `OnOff`, `Descriptor`, `Thermostat`, `FanControl`, `ThermostatUserInterfaceConfiguration`이 구성되어 있다.

`OnOff`는 다음 구성을 사용한다.

- `onOff`: `persist`, 기본값 `0`
- `featureMap`: 기본값 `2`
- `clusterRevision`: 기본값 `0x0007`
- 처리 명령: `Off`, `On`, `Toggle`

#### `Thermostat`

`Thermostat = 513`, IDL `revision 12`이다.

| 속성 | IDL 저장 방식 | 기본값 |
|---|---|---|
| `localTemperature` | `ram` | `2800` |
| `absMinHeatSetpointLimit` | `ram` | `0` |
| `absMaxHeatSetpointLimit` | `ram` | `3500` |
| `absMinCoolSetpointLimit` | `ram` | `1000` |
| `absMaxCoolSetpointLimit` | `ram` | `4000` |
| `occupiedCoolingSetpoint` | `persist` | `2300` |
| `occupiedHeatingSetpoint` | `persist` | `2000` |
| `minHeatSetpointLimit` | `persist` | `500` |
| `maxHeatSetpointLimit` | `persist` | `3000` |
| `minCoolSetpointLimit` | `persist` | `1500` |
| `maxCoolSetpointLimit` | `persist` | `3500` |
| `controlSequenceOfOperation` | `persist` | `0x04` |
| `systemMode` | `persist` | `0x01` |
| `ACLouverPosition` | `persist` | `1` |
| `featureMap` | `ram` | `3` |

처리 명령:

```text
SetpointRaiseLower(SetpointRaiseLowerRequest): DefaultSuccess = 0
```

`SetpointRaiseLowerRequest`는 `SetpointRaiseLowerModeEnum mode = 0`, `int8s amount = 1`로 구성된다.

#### `FanControl`과 사용자 인터페이스

| `FanControl` 속성 | 기본값 |
|---|---|
| `fanModeSequence` | `2` |
| `speedMax` | `100` |
| `rockSupport` | `0x01` |
| `featureMap` | `53` |

`fanMode`, `percentSetting`, `percentCurrent`, `speedSetting`, `speedCurrent`, `rockSetting`, `airflowDirection`도 구성되고, `Step`을 처리한다.

`ThermostatUserInterfaceConfiguration = 516`은 다음 두 전용 속성을 구성한다.

- `temperatureDisplayMode`: 기본값 `0x00`
- `keypadLockout`: 기본값 `0x00`

#### 센서

| endpoint | 클러스터 | ZAP `MeasuredValue` 기본값 | `minMeasuredValue` | `maxMeasuredValue` |
|---:|---|---:|---:|---:|
| 2 | `TemperatureMeasurement = 1026` | 2800 | 1500 | 4500 |
| 3 | `RelativeHumidityMeasurement = 1029` | 6500 | 3000 | 10000 |

두 센서 엔드포인트 모두 `Identify`, `Descriptor`를 포함하며 `Identify`, `TriggerEffect`를 처리한다.

세부 저장 방식은 원문 파일별로 다르다. ZAP에서 `MeasuredValue`는 `RAM`과 기본값을 갖지만, IDL에서는 `measuredValue`가 `callback`으로 선언되어 있다.

### 8. all-clusters-app

출처:

- `examples/all-clusters-app/all-clusters-common/all-clusters-app.matter`
- `examples/all-clusters-app/all-clusters-common/all-clusters-app.zap`

#### 디바이스 유형

| endpoint | 디바이스 유형과 version |
|---:|---|
| 0 | `ma_rootdevice = 22, version 5`, `ma_powersource = 17, version 1` |
| 1 | `ma_powersource = 17, version 1`, `ma_onofflight = 256, version 4` |
| 2 | `ma_powersource = 17, version 1`, `ma_onofflight = 256, version 4` |
| 3 | `ma_genericswitch = 15, version 3` |
| 4 | `ma_genericswitch = 15, version 3` |
| 65534 | `ma_secondary_network_interface = 25, version 1` |

ZAP에서 모든 엔드포인트의 `parentEndpointIdentifier`는 `null`이다.

- endpoint 0: binding cluster `OtaSoftwareUpdateProvider`
- endpoint 1: binding cluster `OnOff`

#### 클러스터 배치

아래 ID는 제공된 IDL의 표기를 유지한다.

| 클러스터 | ID | 서버 endpoint |
|---|---:|---|
| `Identify` | 3 | 1, 2, 3, 4 |
| `Groups` | 4 | 0, 1, 2 |
| `OnOff` | 6 | 1, 2 |
| `LevelControl` | 8 | 1 |
| `Descriptor` | 29 | 0, 1, 2, 3, 4, 65534 |
| `Binding` | 30 | 0, 1 |
| `AccessControl` | 31 | 0 |
| `Actions` | 37 | 1 |
| `BasicInformation` | 40 | 0 |
| `OtaSoftwareUpdateRequestor` | 42 | 0 |
| `LocalizationConfiguration` | 43 | 0 |
| `TimeFormatLocalization` | 44 | 0 |
| `UnitLocalization` | 45 | 0 |
| `PowerSourceConfiguration` | 46 | 0 |
| `PowerSource` | 47 | 0, 1, 2 |
| `GeneralCommissioning` | 48 | 0 |
| `NetworkCommissioning` | 49 | 0, 65534 |
| `DiagnosticLogs` | 50 | 0 |
| `GeneralDiagnostics` | 51 | 0 |
| `SoftwareDiagnostics` | 52 | 0 |
| `ThreadNetworkDiagnostics` | 53 | 0 |
| `WiFiNetworkDiagnostics` | 54 | 0 |
| `EthernetNetworkDiagnostics` | 55 | 0 |
| `TimeSynchronization` | 56 | 0 |
| `Switch` | 59 | 1, 3, 4 |
| `AdministratorCommissioning` | 60 | 0 |
| `OperationalCredentials` | 62 | 0 |
| `GroupKeyManagement` | 63 | 0 |
| `FixedLabel` | 64 | 0, 1 |
| `UserLabel` | 65 | 0, 1 |
| `BooleanState` | 69 | 1 |
| `OvenCavityOperationalState` | 72 | 1 |
| `OvenMode` | 73 | 1 |
| `LaundryDryerControls` | 74 | 1 |
| `ModeSelect` | 80 | 1 |
| `LaundryWasherMode` | 81 | 1 |
| `RefrigeratorAndTemperatureControlledCabinetMode` | 82 | 1 |
| `LaundryWasherControls` | 83 | 1 |
| `RvcRunMode` | 84 | 1 |
| `RvcCleanMode` | 85 | 1 |
| `TemperatureControl` | 86 | 1 |
| `RefrigeratorAlarm` | 87 | 1 |
| `DishwasherMode` | 89 | 1 |
| `AirQuality` | 91 | 1 |
| `SmokeCoAlarm` | 92 | 1 |
| `DishwasherAlarm` | 93 | 1 |
| `MicrowaveOvenMode` | 94 | 1 |
| `OperationalState` | 96 | 1 |
| `RvcOperationalState` | 97 | 1 |
| `ScenesManagement` | 98 | 1, 2 |
| `ThermostatMode` | 99 | 1 |
| `HepaFilterMonitoring` | 113 | 1 |
| `ActivatedCarbonFilterMonitoring` | 114 | 1 |
| `BooleanStateConfiguration` | 128 | 1 |
| `ValveConfigurationAndControl` | 129 | 1 |
| `EnergyPreference` | 155 | 1 |
| `WindowCovering` | 258 | 1 |
| `PumpConfigurationAndControl` | 512 | 1 |
| `Thermostat` | 513 | 1 |
| `FanControl` | 514 | 1 |
| `ThermostatUserInterfaceConfiguration` | 516 | 1 |
| `Humidistat` | 517 | 1 |
| `ColorControl` | 768 | 1 |
| `BallastConfiguration` | 769 | 1 |
| `DynamicLighting` | 773 | 1 |
| `IlluminanceMeasurement` | 1024 | 1 |
| `TemperatureMeasurement` | 1026 | 1 |
| `PressureMeasurement` | 1027 | 1 |
| `FlowMeasurement` | 1028 | 1 |
| `RelativeHumidityMeasurement` | 1029 | 0, 1 |
| `OccupancySensing` | 1030 | 1, 2 |
| `CarbonMonoxideConcentrationMeasurement` | 1036 | 1 |
| `CarbonDioxideConcentrationMeasurement` | 1037 | 1 |
| `NitrogenDioxideConcentrationMeasurement` | 1043 | 1 |
| `OzoneConcentrationMeasurement` | 1045 | 1 |
| `Pm25ConcentrationMeasurement` | 1066 | 1 |
| `FormaldehydeConcentrationMeasurement` | 1067 | 1 |
| `Pm1ConcentrationMeasurement` | 1068 | 1 |
| `Pm10ConcentrationMeasurement` | 1069 | 1 |
| `TotalVolatileOrganicCompoundsConcentrationMeasurement` | 1070 | 1 |
| `RadonConcentrationMeasurement` | 1071 | 4 |