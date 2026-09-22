---
entity: ModeBase
ids: []
source_paths: ['src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml', 'src/app/clusters/mode-base-server/Delegate.h', 'src/app/clusters/mode-base-server/AppDelegate.h', 'src/app/clusters/mode-base-server/mode-base-cluster-objects.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.h', 'src/app/clusters/mode-base-server/CodegenIntegration.h', 'src/app/clusters/mode-base-server/CodegenIntegration.cpp', 'src/app/clusters/mode-base-server/MigrateModeBaseServerStorage.cpp', 'src/app/clusters/mode-base-server/mode-base-server.h', 'src/app/clusters/mode-base-server/ModeBaseCluster.h', 'data_model/1.7/clusters/ModeBase.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
---

## 개요

`ModeBase` 클러스터는 지원되는 옵션 목록에서 특정 모드를 선택하고 제어하기 위한 범용적인 베이스(Base) 클러스터 사양입니다. 이 클러스터는 직접 인스턴스화되기보다는 세탁기 모드, 냉장고 모드, 로봇 청소기 모드 등 다양한 어플리케이션 도메인별 모드 클러스터의 부모 레이아웃 역할을 수행합니다.

---

## 스펙

### 기능 (Features)
| 코드 | 이름 | 비트 | 설명 |
| :--- | :--- | :--- | :--- |
| `DEPONOFF` | `OnOff` | 0 | `OnOff` 클러스터와의 의존성 기능 |
| `COREMODES` | `CoreModes` | 1 | 하나 이상의 코어 모드 지원 기능 |

### 데이터 유형 (Data Types)

#### Struct `ModeOptionStruct`
| ID | 필드명 | 타입 | 제약 조건 / 품질 |
| :--- | :--- | :--- | :--- |
| 0 | `Label` | `string` | 최대 64글자, 고정(fixed) |
| 1 | `Mode` | `uint8` | 고정(fixed) |
| 2 | `ModeTags` | `list` [`ModeTagStruct`] | 최대 8개 항목, 고정(fixed) |

#### Struct `ModeTagStruct`
| ID | 필드명 | 타입 | 설명 / 제약 조건 |
| :--- | :--- | :--- | :--- |
| 0 | `MfgCode` | `vendor-id` | 제조업체 코드 (선택 사항) |
| 1 | `Value` | `enum16` | 태그 값 |

### 속성 (Attributes)
| ID | 이름 | 타입 | 읽기/쓰기 | 필수 여부 (Conform) | 품질 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x0000` | `SupportedModes` | `list` [`ModeOptionStruct`] | `Read` | 필수 | fixed, 2~255개 항목 |
| `0x0001` | `CurrentMode` | `uint8` | `Read` | 필수 | nonVolatile |
| `0x0002` | `StartUpMode` | `uint8` | `Read / Write` | 선택 | nullable, nonVolatile |
| `0x0003` | `OnMode` | `uint8` | `Read / Write` | `DEPONOFF` 기능 활성화 시 필수 | nullable, nonVolatile |
| `0x0004` | `CoreModeTags` | `list` [`enum16`] | `Read` | `COREMODES` 기능 활성화 시 필수 | fixed, 1~16개 항목 |

### 명령 (Commands)

#### 0x00: `ChangeToMode`
* **방향:** Client -> Server
* **응답:** `ChangeToModeResponse`
* **인수:**
  * `0` `NewMode` (`uint8`): 새로 적용하려는 모드 값

#### 0x01: `ChangeToModeResponse`
* **방향:** Server -> Client
* **인수:**
  * `0` `Status` (`enum8`): 처리 결과 코드
  * `1` `StatusText` (`string`): 최대 64글자, 상태에 대한 설명 텍스트

#### 0x02: `ChangeToModeByCoreTag`
* **방향:** Client -> Server
* **응답:** `ChangeToModeResponse`
* **인수:**
  * `0` `NewModeTag` (`enum16`): 새로 적용하려는 코어 모드 태그 값

---

## SDK 정의

### XML 정의
`src/app/zap-templates/zcl/data-model/chip/mode-base-cluster.xml`에서 `ModeTagStruct`와 `ModeOptionStruct`가 다음 파생 클러스터들을 지원하도록 매핑되어 있습니다:
* Laundry Washer Mode (`0x0051`)
* Refrigerator and temperature controlled cabinet Mode (`0x0052`)
* RVC Run Mode (`0x0054`)
* RVC Clean Mode (`0x0055`)
* Dishwasher Mode (`0x0059`)
* Microwave Oven Mode (`0x005E`)
* Oven Mode (`0x0049`)
* Energy EVSE Mode (`0x009D`)
* Water Heater Mode (`0x009E`)
* Device Energy Management Mode (`0x009F`)

### 구조체 및 열거형
`src/app/clusters/mode-base-server/mode-base-cluster-objects.h` 파일에 아래와 같이 열거형이 정의되어 있습니다.

```cpp
enum class ModeTag : uint16_t
{
    kAuto      = 0x0,
    kQuick     = 0x1,
    kQuiet     = 0x2,
    kLowNoise  = 0x3,
    kLowEnergy = 0x4,
    kVacation  = 0x5,
    kMin       = 0x6,
    kMax       = 0x7,
    kNight     = 0x8,
    kDay       = 0x9,
};

enum class StatusCode : uint8_t
{
    kSuccess         = 0x0,
    kUnsupportedMode = 0x1,
    kGenericFailure  = 0x2,
    kInvalidInMode   = 0x3,
};

enum class Feature : uint32_t
{
    kOnOff     = 0x1,
    kCoreModes = to_underlying(ThermostatMode::Feature::kCoreModes),
};
```

---

## 구현

### 주요 소스 파일 구조
`ModeBase` 서버 컴포넌트는 `src/app/clusters/mode-base-server/` 디렉터리에 구현되어 있습니다.

* **`AppDelegate.h`**: 응용 프로그램 레벨에서 구현해야 하는 비즈니스 로직 가상 인터페이스 클래스 `AppDelegate`가 기술되어 있습니다.
  * `GetModeLabelByIndex()`, `GetModeValueByIndex()`, `GetModeTagsByIndex()`: 지원되는 모드 속성 목록 생성용 인터페이스
  * `HandleChangeToMode()`: 클라이언트로부터 `ChangeToMode` 수신 시 장치 상태 전환 및 응답 생성 로직 인터페이스
  * `GetCoreModeTagByIndex()`, `HandleChangeToModeByCoreTag()`: 코어 태그 지원용 가상 함수 인터페이스

* **`Delegate.h`**: SDK 내에서 `Instance` 포인터 접근을 관리하기 위해 `AppDelegate`를 확장한 가상 클래스입니다.

* **`ModeBaseCluster.h` / `ModeBaseCluster.cpp`**: 클러스터 속성 읽기/쓰기 및 명령 호출 흐름을 직접 구현한 핵심 클래스입니다.
  * `Startup()`: 데이터 모델 로드 시 호출되며 KVS(Key-Value Store)에서 영속 저장된 속성들을 복구하고 `StartUpMode` 및 `OnMode` 전환 조건 등을 검증 및 반영합니다.
  * `HandleChangeToMode()`: SDK 내부 명령 처리기로, 변경하려는 모드가 지원되는 모드인지 판별하고 `AppDelegate`에 전환을 요청합니다.
  * `HandleChangeToModeByCoreTag()`: 코어 모드 태그를 받아 우선순위 모드를 매핑한 후 전환 작업을 수행합니다.

* **`CodegenIntegration.h` / `CodegenIntegration.cpp`**: 코드 생성 구조(Codegen)와의 매핑 및 모드 클러스터 라이프사이클 관리를 담당하는 `Instance` 클래스를 선언 및 정의합니다.
  * `Instance` 인스턴스는 전역 `gModeBaseInstances` 목록에 등록되어 관리됩니다.
  * `Init()`에서 해당 엔드포인트의 속성 지원 여부(`StartUpMode`, `OnMode`, `kCoreModes`, `kOnOff` 등)를 검증하고 데이터 모델 프로바이더 등록 및 내부 `mCluster` 생성을 완료합니다.

* **`MigrateModeBaseServerStorage.h` / `MigrateModeBaseServerStorage.cpp`**: 이전 SafeAttributePersistence 저장 매커니즘에서 새로운 `AttributePersistenceProvider`로의 마이그레이션을 처리합니다.
  * 마이그레이션 대상 속성: `CurrentMode`, `StartUpMode`, `OnMode`

* **`mode-base-server.h`**: 최종 모드 서버 모듈을 연동하기 위한 메인 헤더 파일입니다.