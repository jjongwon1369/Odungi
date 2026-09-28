---
entity: all
ids: []
source_paths: ['examples/chef/README.md', 'examples/laundry-washer-app/nxp/CMakeLists.txt', 'examples/laundry-washer-app/nxp/README.md', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter', 'examples/laundry-washer-app/nxp/zap/laundry-washer-app.zap', 'examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp', 'examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp', 'examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h', 'examples/all-clusters-app/all-clusters-common/all-clusters-app.matter', 'examples/all-clusters-app/all-clusters-common/all-clusters-app.zap', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h', 'examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h', 'examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter', 'examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap', 'examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.matter', 'examples/refrigerator-app/refrigerator-common/refrigerator-app.zap', 'examples/refrigerator-app/linux/README.md', 'examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h', 'examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-5.6-luna
---

## 개요

입력에는 다음 Matter 예시가 포함되어 있습니다.

- `examples/chef`
  - ZAP 기반 데이터 모델로 여러 디바이스 타입을 생성하는 샘플 애플리케이션
  - `chef.py`를 사용해 ZAP 아티팩트 생성, 빌드, 플래시 수행
  - `devices` 폴더에 디바이스 타입별 `.zap` 파일 저장
- `examples/laundry-washer-app/nxp`
  - NXP SDK 기반 Laundry Washer 프로토타입
  - 디바이스 커미셔닝과 Laundry Washer 관련 클러스터 제어를 시연
- `examples/refrigerator-app/linux`
  - Raspberry Pi 및 NXP i.MX 8M Mini EVK 대상 Linux Refrigerator 예시
  - Wi-Fi, Thread, BLE, Pigweed RPC 및 디바이스 트레이싱 지원
- `examples/chef/devices`
  - `rootnode_roomairconditioner_9cf3607804`
  - `rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680`
  등의 복합 디바이스 데이터 모델 예시

## 예시

### `examples/chef`

#### 주요 목적

Chef app은 다음을 목적으로 합니다.

1. Matter 디바이스 타입의 커버리지 확대
2. 데이터 모델을 쉽게 구성할 수 있는 샘플 애플리케이션 제공

Chef는 shell app을 기반으로 하며, 빌드 시점에 ZAP 파일에 정의된 데이터 모델을 처리합니다. 이 작업은 통합 빌드 스크립트인 `chef.py`가 수행합니다.

ZAP 처리 중 생성되는 아티팩트는 임시 `out` 폴더에 저장되며, CI/CD에서는 `zzz_generated`의 아티팩트를 사용합니다. 사용 가능한 디바이스 타입별 `.zap` 파일은 `devices` 폴더에 있습니다.

#### 기본 빌드 절차

```sh
chef.py
chef.py -u
chef.py -gzbf -t <platform> -d lighting
chef.py -h
```

`chef.py`를 처음 실행하면 `config.yaml`이 생성됩니다. `IDF_PATH` 및 `ZEPHYR_BASE`와 같은 SDK 환경 변수가 있으면 해당 값을 기본값으로 사용합니다.

`config.yaml`의 `TTY`에는 플랫폼이 시리얼 포트로 디바이스를 열거할 때 사용하는 경로를 설정합니다.

```yaml
TTY: /dev/ttyACM0
```

예시 명령:

```sh
chef.py -gzbf -t <platform> -d lighting
```

이 명령은 `devices/lighting.zap`을 ZAP GUI로 열고, 데이터 모델 편집 후 ZAP 아티팩트를 생성합니다. 생성된 아티팩트는 `zap-generated` 폴더에 배치되고, 빌드 및 대상 디바이스 플래시가 수행됩니다.

#### 폴더 구조

| 경로 또는 이름 | 설명 |
| --- | --- |
| `<platform>` | 플랫폼별 빌드 시스템과 `main.cpp` |
| `common` | 여러 플랫폼에서 공유하는 소스 코드 |
| `devices` | Matter 데이터 모델을 정의하는 `.zap` 파일 |
| `out` | ZAP 생성 아티팩트를 저장하는 임시 폴더 |
| `sample_app_util` | 새 디바이스 타입 파일명 생성 가이드와 스크립트 |
| `config.yaml` | `chef.py`의 SDK 및 TTY 경로 설정 |
| `chef.py` | 샘플 생성 메인 스크립트 |

`common`에는 `LightingManager` 및 `LockManager`와 같은 공통 기능을 포함할 수 있습니다. 애플리케이션은 관련 클러스터 설정의 존재 여부를 동적으로 식별해야 하며, 해당 클러스터 없이 빌드되는 사용 사례를 중단해서는 안 됩니다.

#### Linux 런타임 옵션

Chef 및 여러 Linux 샘플은 다음 런타임 옵션을 지원합니다.

- `--discriminator <discriminator>`: 커미셔닝 중 디바이스가 광고하는 12-bit unsigned 값
- `--passcode <passcode>`: 커미셔닝 중 proof of possession으로 사용하는 27-bit unsigned 값
- `--secured-device-port <port>`: 보안 디바이스 메시지 수신 포트
  - 기본값: `5540`
- `--KVS <filepath>`: Key Value Store 항목을 저장할 파일

도움말은 다음 명령으로 확인할 수 있습니다.

```sh
<generated-linux-binary> -h
```

#### CI/CD

Chef CI 작업은 다음 workflow에 정의되어 있습니다.

```text
.github/workflows/chef.yaml
```

CI 작업은 다음과 같이 실행됩니다.

```sh
./examples/chef/chef.py --ci -t $PLATFORM
```

`--ci`는 `cicd_config.json`의 `ci_allow_list`에 지정되어 있고 `/devices`에도 존재하는 모든 디바이스를 빌드합니다.

플랫폼별 빌드가 끝나면 `bundle_$PLATFORM` 함수가 빌드 결과를 `_CD_STAGING_DIR`로 복사하거나 이동합니다. `bundle_esp32`가 참조 구현입니다.

새 플랫폼 추가 시 다음 작업이 필요합니다.

1. `bundle_$PLATFORM` 함수 구현
2. 해당 플랫폼 이미지에서 `ci_allow_list`의 예시들이 빌드되는지 확인
3. `.github/workflows/chef.yaml`에 새 job 추가
4. CD 사용 시 `cd_platforms`에 플랫폼 추가

CI 컨테이너에서의 예시:

```sh
docker run -it --mount source=$(pwd),target=/workspace,type=bind \
  ghcr.io/project-chip/chip-build-$PLATFORM:$VERSION
```

```sh
chown -R $(whoami) /workspace
cd /workspace
source ./scripts/bootstrap.sh
source ./scripts/activate.sh
./examples/chef/chef.py --ci -t $PLATFORM
```

CD용 설정 예시:

```json
"$PLATFORM": {
    "output_archive_prefix_1": ["option_1", "option_2"],
    "output_archive_prefix_2": []
}
```

`linux` 설정 예시:

```json
"linux": {
    "linux_x86": ["--cpu_type", "x64"],
    "linux_arm64_ipv6only": ["--cpu_type", "arm64", "--ipv6only"]
}
```

#### 새 디바이스 타입 추가

새 Chef 디바이스는 다음 절차로 추가합니다.

```sh
python sample_app_util.py zap <zap_file> --rename-file
scripts/tools/zap_regen_all.py
```

새 파일은 다음 경로에 저장합니다.

```text
examples/chef/devices
```

`zzz_generated`와 `examples/chef/devices`를 커밋해야 하며, ZAP 템플릿 workflow가 이를 검사합니다.

#### Manufacturer Extensions / Custom Clusters

`rootnode_onofflight_meisample*` 디바이스는 다음 파일에 정의된 Sample MEI cluster를 사용하는 예시입니다.

```text
src/app/zap-templates/zcl/data-model/chip/sample-mei-cluster.xml
```

Sample MEI에는 다음 항목이 있습니다.

- boolean attribute `flip-flop`
- 인자가 없는 `ping` command
- 두 개의 `uint8` 인자를 받고 합계를 반환하는 `add-arguments` command/response 쌍

테스트 예시:

```sh
chip-tool pairing onnetwork 1 20202021
chip-tool samplemei add-arguments 1 1 10 20
chip-tool samplemei write flip-flop 0 1 1
chip-tool samplemei read flip-flop 1 1
```

### `examples/laundry-washer-app/nxp`

NXP Laundry Washer 예시는 Project CHIP과 NXP SDK를 기반으로 하며, 디바이스 커미셔닝과 여러 클러스터 제어를 보여줍니다.

지원 플랫폼:

| 플랫폼 | 문서 |
| --- | --- |
| RW61x (Zephyr OS) | `docs/platforms/nxp/nxp_zephyr_guide.md` |
| RW61x (FreeRTOS OS) | `docs/platforms/nxp/nxp_rw61x_guide.md` |
| RT1170 | `docs/platforms/nxp/nxp_rt1170_guide.md` |
| RT1060 | `docs/platforms/nxp/nxp_rt1060_guide.md` |

환경 설정, 빌드 및 테스트는 다음 문서를 참조합니다.

- FreeRTOS:
  - `docs/platforms/nxp/nxp_examples_freertos_platforms.md`
- Zephyr:
  - `docs/platforms/nxp/nxp_zephyr_guide.md`

Matter-over-WiFi + Thread Border Router 구성은 이 애플리케이션에서 지원되지 않습니다.

#### 데이터 모델

`examples/laundry-washer-app/nxp/zap/laundry-washer-app.matter`에는 다음 주요 클러스터가 정의되어 있습니다.

| Cluster | ID |
| --- | ---: |
| `Identify` | `3` |
| `Groups` | `4` |
| `OnOff` | `6` |
| `Descriptor` | `29` |
| `Binding` | `30` |
| `AccessControl` | `31` |
| `BasicInformation` | `40` |
| `OtaSoftwareUpdateProvider` | `41` |
| `OtaSoftwareUpdateRequestor` | `42` |
| `LocalizationConfiguration` | `43` |
| `UnitLocalization` | `45` |
| `GeneralCommissioning` | `48` |
| `NetworkCommissioning` | `49` |
| `DiagnosticLogs` | `50` |
| `GeneralDiagnostics` | `51` |
| `SoftwareDiagnostics` | `52` |
| `WiFiNetworkDiagnostics` | `54` |
| `AdministratorCommissioning` | `60` |
| `OperationalCredentials` | `62` |
| `GroupKeyManagement` | `63` |
| `UserLabel` | `65` |
| `LaundryWasherMode` | `81` |
| `LaundryWasherControls` | `83` |
| `TemperatureControl` | `86` |
| `OperationalState` | `96` |

`endpoint 0`은 `ma_rootdevice` 및 `ma_otarequestor`를 사용하고, `endpoint 1`은 `ma_laundry_washer`를 사용합니다.

`endpoint 1`에서 활성화된 주요 클러스터는 다음과 같습니다.

- `Identify`
- `Groups`
- `OnOff`
- `Descriptor`
- `Binding`
- `UserLabel`
- `LaundryWasherMode`
- `LaundryWasherControls`
- `TemperatureControl`
- `OperationalState`

#### `LaundryWasherMode`

`LaundryWasherMode`의 주요 mode는 다음과 같습니다.

| 식별자 | 값 |
| --- | ---: |
| `kAuto` | `0` |
| `kQuick` | `1` |
| `kQuiet` | `2` |
| `kLowNoise` | `3` |
| `kLowEnergy` | `4` |
| `kVacation` | `5` |
| `kMin` | `6` |
| `kMax` | `7` |
| `kNight` | `8` |
| `kDay` | `9` |
| `kNormal` | `16384` |
| `kDelicate` | `16385` |
| `kHeavy` | `16386` |
| `kWhites` | `16387` |

지원 command는 다음과 같습니다.

```text
ChangeToMode
ChangeToModeByCoreTag
```

#### `LaundryWasherControls`

`LaundryWasherControls`는 다음 attribute 및 feature를 사용합니다.

- `spinSpeeds`
- `spinSpeedCurrent`
- `numberOfRinses`
- `supportedRinses`
- `kSpin`
- `kRinse`

`NumberOfRinsesEnum` 값:

```text
kNone = 0
kNormal = 1
kExtra = 2
kMax = 3
```

#### `TemperatureControl`

`TemperatureControl`은 다음 attribute를 제공합니다.

- `temperatureSetpoint`
- `minTemperature`
- `maxTemperature`
- `step`
- `selectedTemperatureLevel`
- `supportedTemperatureLevels`

command:

```text
SetTemperature
```

feature:

```text
kTemperatureNumber
kTemperatureLevel
kTemperatureStep
```

#### `OperationalState`

`OperationalState`의 상태는 다음과 같습니다.

```text
kStopped = 0
kRunning = 1
kPaused = 2
kError = 3
```

command:

```text
Pause
Stop
Start
Resume
```

event:

```text
OperationalError
OperationCompletion
```

### NXP `CMakeLists.txt`

파일:

```text
examples/laundry-washer-app/nxp/CMakeLists.txt
```

주요 설정은 다음과 같습니다.

- `CHIP_ROOT` 계산
- `COMMON_KCONFIG_ENV_SETTINGS` 설정
- `zzz_generated`를 `GEN_DIR`로 설정
- `ALL_CLUSTERS_COMMON_DIR` 및 NXP 공통 디렉터리 연결
- `McuxSDK 3.0.0` 로드
- `chip_data_model.cmake` 포함
- NXP 공통 애플리케이션 파일 포함
- `main.cpp`, `AppTask.cpp`, `DeviceCallbacks.cpp`, `ZclCallbacks.cpp` 및 delegate 소스 추가

Wi-Fi 또는 Thread가 활성화되면 다음 데이터 모델이 구성됩니다.

```cmake
chip_configure_data_model(app
    INCLUDE_SERVER
    ZAP_FILE ${NXP_EXAMPLE_ZAP_DIR}/laundry-washer-app.zap
)
```

다음 구성은 지원되지 않습니다.

```text
CONFIG_CHIP_ETHERNET
CONFIG_CHIP_WIFI + CONFIG_NET_L2_OPENTHREAD
```

### `LaundryWasherModeDelegate`

헤더 파일:

```text
examples/all-clusters-app/all-clusters-common/include/laundry-washer-mode.h
```

구현 파일:

```text
examples/laundry-washer-app/nxp/common/main/laundry-washer-mode.cpp
```

`LaundryWasherModeDelegate`는 `ModeBase::Delegate`를 상속합니다.

정적 mode 값:

```cpp
const uint8_t ModeNormal   = 0;
const uint8_t ModeDelicate = 1;
const uint8_t ModeHeavy    = 2;
const uint8_t ModeWhites   = 3;
```

정적 mode label 및 tag:

```text
Normal
Delicate
Heavy
Whites
```

각 mode에 연결된 tag는 다음과 같습니다.

- `Normal`
  - `ModeTag::kNormal`
- `Delicate`
  - `ModeTag::kDelicate`
  - `ModeBase::ModeTag::kNight`
  - `ModeBase::ModeTag::kQuiet`
- `Heavy`
  - `ModeBase::ModeTag::kMax`
  - `ModeTag::kHeavy`
- `Whites`
  - `ModeTag::kWhites`

주요 함수:

```cpp
CHIP_ERROR Init();
void HandleChangeToMode(uint8_t mode, ModeBase::Commands::ChangeToModeResponse::Type & response);
CHIP_ERROR GetModeLabelByIndex(uint8_t modeIndex, MutableCharSpan & label);
CHIP_ERROR GetModeValueByIndex(uint8_t modeIndex, uint8_t & value);
CHIP_ERROR GetModeTagsByIndex(uint8_t modeIndex, DataModel::List<ModeTagStructType> & tags);
ModeBase::Instance * Instance();
void Shutdown();
```

`HandleChangeToMode`는 다음 상태를 반환합니다.

```cpp
response.status = to_underlying(ModeBase::StatusCode::kSuccess);
```

`MatterLaundryWasherModeClusterInitCallback`은 `endpointId == 1`인지 확인한 뒤 `LaundryWasherModeDelegate`와 `ModeBase::Instance`를 생성합니다.

### `LaundryWasherControlDelegate`

헤더 파일:

```text
examples/all-clusters-app/all-clusters-common/include/laundry-washer-controls-delegate-impl.h
```

구현 파일:

```text
examples/all-clusters-app/all-clusters-common/src/laundry-washer-controls-delegate-impl.cpp
```

정적으로 정의된 `spinSpeedsNameOptions`:

```text
Off
Low
Medium
High
```

정적으로 정의된 `supportRinsesOptions`:

```text
NumberOfRinsesEnum::kNormal
NumberOfRinsesEnum::kExtra
```

주요 함수:

```cpp
CHIP_ERROR GetSpinSpeedAtIndex(size_t index, MutableCharSpan & spinSpeed);
CHIP_ERROR GetSupportedRinseAtIndex(size_t index, NumberOfRinsesEnum & supportedRinse);
```

유효하지 않은 index는 다음 오류를 반환합니다.

```cpp
CHIP_ERROR_PROVIDER_LIST_EXHAUSTED
```

### `DeviceCallbacks`

파일:

```text
examples/laundry-washer-app/nxp/common/main/DeviceCallbacks.cpp
examples/laundry-washer-app/nxp/common/main/include/DeviceCallbacks.h
```

`LaundryWasherApp::DeviceCallbacks`는 `chip::NXP::App::CommonDeviceCallbacks`를 상속합니다.

attribute 변경은 다음 함수로 전달됩니다.

```cpp
void LaundryWasherApp::DeviceCallbacks::PostAttributeChangeCallback(
    EndpointId endpointId,
    ClusterId clusterId,
    AttributeId attributeId,
    uint8_t type,
    uint16_t size,
    uint8_t * value);
```

`clusterId`가 `Clusters::OnOff::Id`이면 `OnOnOffPostAttributeChangeCallback`을 호출합니다.

`OnOff::Attributes::OnOff::Id` 값이 `true`이면 `LaundryWasherMode::Instance()`에서 `GetOnMode()`를 가져와 현재 mode를 갱신합니다.

### `ZclCallbacks`

파일:

```text
examples/laundry-washer-app/nxp/common/main/ZclCallbacks.cpp
```

`MatterPostAttributeChangeCallback`은 attribute 변경을 `CHIPDeviceManagerCallbacks`로 전달합니다.

`LaundryWasherControls` 초기화 시 다음 delegate가 등록됩니다.

```cpp
LaundryWasherControlsServer::SetDefaultDelegate(
    endpoint,
    &LaundryWasherControlDelegate::getLaundryWasherControlDelegate());
```

### Chef 디바이스 데이터 모델

#### `rootnode_roomairconditioner_9cf3607804`

파일:

```text
examples/chef/devices/rootnode_roomairconditioner_9cf3607804.matter
examples/chef/devices/rootnode_roomairconditioner_9cf3607804.zap
```

주요 endpoint:

| Endpoint | Device type | ID |
| ---: | --- | ---: |
| `0` | `ma_rootdevice` | `22` |
| `1` | `ma_room_airconditioner` | `114` |
| `2` | `ma_tempsensor` | `770` |
| `3` | `ma_humiditysensor` | `775` |

`endpoint 1`의 주요 클러스터:

- `Identify`
- `Groups`
- `OnOff`
- `Descriptor`
- `Thermostat`
- `FanControl`
- `ThermostatUserInterfaceConfiguration`

`endpoint 2`는 `TemperatureMeasurement`를 사용합니다.

`endpoint 3`은 `RelativeHumidityMeasurement`를 사용합니다.

#### `rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680`

파일:

```text
examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.matter
examples/chef/devices/rootnode_refrigerator_temperaturecontrolledcabinet_temperaturecontrolledcabinet_ffdb696680.zap
```

주요 endpoint:

| Endpoint | Device type | ID |
| ---: | --- | ---: |
| `0` | `ma_rootdevice` | `22` |
| `1` | `ma_refrigerator` | `112` |
| `2` | `ma_temperature_controlled_cabinet` | `113` |
| `3` | `ma_temperature_controlled_cabinet` | `113` |
| `4` | `ma_fan` | `43` |

주요 클러스터:

- `RefrigeratorAndTemperatureControlledCabinetMode`
- `RefrigeratorAlarm`
- `TemperatureControl`
- `TemperatureMeasurement`
- `FanControl`

`endpoint 2` 및 `endpoint 3`은 서로 다른 `TemperatureControl` 기본값을 사용합니다.

- `endpoint 2`
  - `temperatureSetpoint = 200`
  - `minTemperature = 200`
  - `maxTemperature = 400`
  - `step = 10`
- `endpoint 3`
  - `temperatureSetpoint = -1800`
  - `minTemperature = -1800`
  - `maxTemperature = -1500`
  - `step = 10`

#### `refrigerator-app`

파일:

```text
examples/refrigerator-app/refrigerator-common/refrigerator-app.matter
examples/refrigerator-app/refrigerator-common/refrigerator-app.zap
```

`refrigerator-app`은 다음과 같은 계층형 endpoint 구성을 사용합니다.

- `endpoint 0`
  - `ma_rootdevice`
- `endpoint 1`
  - `ma_refrigerator`
- `endpoint 2`
  - `ma_temperature_controlled_cabinet`
- `endpoint 3`
  - `ma_temperature_controlled_cabinet`

주요 클러스터:

- `RefrigeratorAndTemperatureControlledCabinetMode`
- `RefrigeratorAlarm`
- `TemperatureControl`
- `TemperatureMeasurement`

### `refrigerator-app` Linux 빌드 및 실행

문서:

```text
examples/refrigerator-app/linux/README.md
```

대상 플랫폼:

- Raspberry Pi
- NXP i.MX 8M Mini EVK

#### 빌드

필요한 패키지:

```sh
sudo apt-get install git gcc g++ python pkg-config libssl-dev \
  libdbus-1-dev libglib2.0-dev ninja-build python3-venv \
  python3-dev unzip
```

빌드 절차:

```sh
cd ~/connectedhomeip/examples/refrigerator-app/linux
git submodule update --init
source third_party/connectedhomeip/scripts/activate.sh
gn gen out/debug
ninja -C out/debug
```

생성된 결과를 삭제하려면 다음을 실행합니다.

```sh
rm -rf out/
```

Pigweed RPC를 활성화한 빌드:

```sh
gn gen out/debug --args='import("//with_pw_rpc.gni")'
ninja -C out/debug
```

#### 명령줄 옵션

- `--wifi`
  - Wi-Fi management 기능 활성화
  - Wi-Fi 커미셔닝에 필요
- `--thread`
  - Thread management 기능 활성화
  - `ot-br-posix` dbus daemon 필요
- `--ble-controller <selector>`
  - BLE 광고 및 연결에 사용할 Bluetooth controller 선택

#### Raspberry Pi 실행

```sh
sudo out/debug/chip-refrigerator-app --ble-controller 1
```

예시에서는 `hci1`을 사용하기 위해 `--ble-controller 1`을 전달합니다.

#### Pigweed RPC Console

RPC가 활성화된 빌드에서는 `chip_rpc` Python interactive console이 설치됩니다.

```sh
pip3 install out/debug/chip_rpc_console_wheels/*.whl
```

실행:

```sh
chip-console -s localhost:33000 -o /<YourFolder>/pw_log.out
```

#### Device Tracing

Device tracing은 RPC가 활성화된 빌드에서 사용할 수 있습니다.

```sh
./{PIGWEED_REPO}/pw_trace_tokenized/py/pw_trace_tokenized/get_trace.py \
  -s localhost:33000 \
  -o {OUTPUT_FILE} \
  -t {ELF_FILE} \
  {PIGWEED_REPO}/pw_trace_tokenized/pw_trace_protos/trace_rpc.proto
```

### `AppSupportedTemperatureLevelsDelegate`

헤더 파일:

```text
examples/refrigerator-app/refrigerator-common/include/static-supported-temperature-levels.h
```

구현 파일:

```text
examples/refrigerator-app/refrigerator-common/src/static-supported-temperature-levels.cpp
```

`TemperatureControl`의 정적 temperature level 옵션:

```text
Hot
Warm
Freezing
```

`endpoint 2` 및 `endpoint 3`에 동일한 옵션 목록을 등록합니다.

```cpp
EndpointPair(2, AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions,
             MATTER_ARRAY_SIZE(AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions));

EndpointPair(3, AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions,
             MATTER_ARRAY_SIZE(AppSupportedTemperatureLevelsDelegate::temperatureLevelOptions));
```

주요 함수:

```cpp
uint8_t Size() override;
CHIP_ERROR Next(MutableCharSpan & item) override;
```

유효한 endpoint가 아니거나 목록을 모두 소비한 경우 다음 오류를 반환합니다.

```cpp
CHIP_ERROR_PROVIDER_LIST_EXHAUSTED
```

## 관련 문서

- [NXP Zephyr Guide](../../../docs/platforms/nxp/nxp_zephyr_guide.md)
- [NXP RW61x (FreeRTOS) Guide](../../../docs/platforms/nxp/nxp_rw61x_guide.md)
- [NXP RT1170 Guide](../../../docs/platforms/nxp/nxp_rt1170_guide.md)
- [NXP RT1060 Guide](../../../docs/platforms/nxp/nxp_rt1060_guide.md)
- [CHIP NXP Examples Guide for FreeRTOS platforms](../../../docs/platforms/nxp/nxp_examples_freertos_platforms.md)
- [NXP Zephyr Application](../../../docs/platforms/nxp/nxp_zephyr_guide.md)
- [Linux BLE Settings](/platforms/linux/ble_settings.md)
- [NEW_CHEF_DEVICES.md](NEW_CHEF_DEVICES.md)
- `examples/chef/sample_app_util/README`
- `integrations/cloudbuild/README`
- `.github/workflows/chef.yaml`
- `integrations/cloudbuild/chef.yaml`
- `cicd_config.json`