---
entity: uncategorized
ids: []
source_paths: ['data_model/1.7/scraper_version', 'data_model/1.7/spec_sha', 'data_model/1.7/spec_tag', 'data_model/README.md', 'src/app/SpecificationDefinedRevisions.h', 'src/app/server-cluster/DefaultServerCluster.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c3/processed/documents.jsonl
corpus_snapshot: corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e
---

# uncategorized

## 개요

제공된 자료는 Matter 데이터 모델 XML의 버전 정보와 관리 절차, SDK의 리비전 상수, 서버 클러스터 기본 클래스인 `DefaultServerCluster`를 다룬다.

### 데이터 모델 버전 정보

| 원본 경로 | 값 |
|---|---|
| `data_model/1.7/scraper_version` | `alchemy version: v1.7.10` |
| `data_model/1.7/spec_sha` | `214e40c9d51cfe89050eae68ca5b76238fcfa332` |
| `data_model/1.7/spec_tag` | `0.9-1.7-winter2027` |

### 데이터 모델 XML의 용도와 관리

출처: `data_model/README.md`  
문서 메타데이터: `orphan: true`

`data_model` 디렉터리는 Matter 클러스터의 기계 판독 가능한 표현을 포함한다.

- 데이터 모델 XML은 특정 리비전의 공식 스펙 데이터 모델을 나타내며, 인증 테스트와 문서에 사용된다.
- Data Model Tiger Team(DMTT)이 관리하며, 새로운 공식 스펙 또는 스펙 투표안이 발표되면 갱신한다.
- 이 파일들은 `zap`이나 SDK 코드 생성에 사용되지 않는다.
- 클러스터 또는 디바이스 타입 구현자가 XML을 수동으로 수정해서는 안 된다.

#### 테스트의 데이터 모델 버전 선택

1. 테스트 인프라의 `basic_composition.py`가 실제 Matter 디바이스(DUT)와 통신한다.
2. endpoint 0의 `BasicInformation` 클러스터에서 활성 `SpecificationVersion` 속성을 읽는다.
3. `spec_parsing.py`의 `dm_from_spec_version()`이 이 값을 명시적인 `prebuilt` 버전 디렉터리(예: `1.6`)에 매핑한다.
4. 테스트 하네스는 DUT가 선언한 스펙 기준에 맞춰 검증한다.

#### Data Model Errata Engine

“next” 기능을 개발하거나, 체크인된 안정 버전 XML을 기준으로 Interaction Data Model(IDM) 테스트를 실패하게 만드는 스펙 오타를 수정할 때는 XML을 직접 편집하지 않는다. 대신 선언적 정오표 오버레이 파일인 `errata_future.yaml`을 사용한다.

새 오버레이 항목 추가와 새로운 재정의 키를 지원하기 위한 엔진 확장 방법은 [Data Model Errata Guide](../docs/guides/data_model_errata.md)를 참조한다.

### 기존 데이터 모델 리비전 갱신

기존 디렉터리의 스펙 리비전 또는 `alchemy` 릴리스를 갱신할 때는 `scripts/spec_xml/generate_spec_xml.py`를 사용한다. 사용법은 `--help`로 확인할 수 있다.

1. [스펙 저장소](https://github.com/CHIP-Specifications/connectedhomeip-spec)를 원하는 SHA, 태그 또는 브랜치로 체크아웃한다.
2. 포함 수준을 결정한다.
   - 현재 투표안의 포함 항목
   - 진행 중인 항목 제외
   - 진행 중인 항목 전체 포함
3. `Current`를 사용하는 경우 스크립트의 포함 목록을 투표 안내 이메일과 대조한다.
4. 생성 스크립트를 실행하고 모든 파일 변경을 체크인한다.

```sh
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.3
IN_PROGRESS=None
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

생성 후에는 다음을 확인한다.

- `scripts/spec_xml/spec_revision_diff_summary.py`로 두 디렉터리의 데이터 모델 차이 요약을 생성한다.
- 요약과 생성된 ID 파일에서 잠정적(provisional) 표시가 예상대로 유지되는지 확인한다.
- 스펙 SHA와 scraper 버전을 함께 갱신한다면, 변경 원인을 구분할 수 있도록 두 커밋으로 나누는 것이 권장된다.
- PR을 푸시하기 전에 `build_python.sh`를 실행하고 가상 환경을 활성화한 뒤 `src/python_testing`의 모든 `TestSpec*` 테스트를 실행한다.

다음 명령은 저장소 루트에서 실행하는 경로를 기준으로 한다.

```sh
. scripts/activate.sh
VENV=out/py
./scripts/build_python.sh -i $VENV
source $VENV/bin/activate
python3 src/python_testing/TestSpecParsingSupport.py
python3 src/python_testing/TestSpecParsingSelection.py
python3 src/python_testing/TestSpecParsingDeviceType.py
```

### 새 데이터 모델 리비전 추가

새 리비전도 `scripts/spec_xml/generate_spec_xml.py`로 생성한다.

#### 생성 및 검토 절차

1. 직전 리비전 디렉터리를 새 디렉터리 이름으로 복사하고 첫 번째 커밋으로 기록한다.
2. 스펙 저장소를 원하는 SHA, 태그 또는 브랜치로 체크아웃한다.
3. 포함 수준을 결정한다. `Current`를 사용한다면 포함 목록을 투표 안내 이메일과 대조한다.
4. 직전 리비전과 동일한 `alchemy` 릴리스로 새 데이터를 생성하여 별도 커밋을 만든다.
5. `alchemy` 리비전 변경이 필요하다면 가능한 한 별도 커밋으로 분리한다.

```sh
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.5
IN_PROGRESS=Current
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

6. `build_python.sh`를 실행하고 가상 환경을 활성화한 뒤 `src/python_testing`의 모든 `TestSpec*` 테스트를 실행한다.
7. 오류가 있으면 스펙 자체 또는 스펙 저장소의 정오표 파일에서 수정하는 것을 우선한다.
8. 올바르게 생성된 모든 변경을 커밋한다.
9. `scripts/spec_xml/spec_revision_diff_summary.py`로 차이 요약을 생성하여 PR 설명에 활용한다.

요약과 생성된 ID 파일의 검토 항목은 다음과 같다.

- 예상한 모든 잠정적 요소가 계속 잠정적으로 표시되는가?
- 예상하지 않은 잠정적 요소가 없는가?
- 클러스터와 디바이스 타입의 변경에 리비전 갱신이 동반되는가?
- 두 리비전 사이의 모든 변경이 예상한 내용인가?

#### 파싱 지원, SDK 및 CI 갱신

| 대상 | 필요한 변경 |
|---|---|
| `src/python_testing/matter_testing_infrastructure/BUILD.gn` | 새 파일의 zip 생성 및 포함 설정 추가 |
| `src/python_testing/matter_testing_infrastructure/data_model_xmls.gni` | 파일 목록은 `generate_spec_xml.py` 실행 과정에서 갱신됨 |
| `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py` | `PrebuiltDataModelDirectory` enum에 새 디렉터리를 추가하고 `dm_from_spec_version` 갱신 |
| `src/python_testing/TestSpecParsingDeviceType.py` | 새 데이터 모델 단위 테스트 추가 |
| `src/python_testing/TestSpecParsingSelection.py` | 새 데이터 모델 단위 테스트 추가 |
| `src/python_testing/TestSpecParsingSupport.py` | 새 데이터 모델 단위 테스트 추가 |
| `src/app/SpecificationDefinedRevisions.h` | SDK를 새 스펙 리비전으로 갱신 |
| `.github/workflows/check-data-model-directory-updates.yaml` | CI 데이터 모델 리비전 검사에 새 파일 추가 |

### SDK 리비전 상수

출처: `src/app/SpecificationDefinedRevisions.h`  
네임스페이스: `chip::Revision`

| 식별자 | 타입 | 값 | 원문 설명 또는 참조 |
|---|---|---|---|
| `kInteractionModelRevision` | `InteractionModelRevision` | `12` | Interaction Model 리비전을 식별하는 단조 증가 값. 코어 스펙 8.1.1 “Revision History” 참조 |
| `kInteractionModelRevisionTag` | `uint8_t` | `0xFF` | 별도 설명 없음 |
| `kDataModelRevision` | `uint16_t` | `22` | Node가 인증받은 Data Model 리비전을 식별하는 단조 증가 값. 코어 스펙 7.1.1 “Revision History” 참조 |
| `kSpecificationVersion` | `uint32_t` | `0x01070000` | Node가 인증받은 스펙 버전. 코어 스펙 11.1.5.22 “SpecificationVersion Attribute” 참조 |

모든 상수는 `inline constexpr`로 선언되어 있다.

### `DefaultServerCluster`

출처: `src/app/server-cluster/DefaultServerCluster.h`  
네임스페이스: `chip::app`  
상속 대상: `ServerClusterInterface`

`DefaultServerCluster`는 스펙을 준수하는 클래스를 쉽게 작성하도록 `ServerClusterInterface`의 대부분 메서드에 기본 구현을 제공한다.

- 생성 시 설정된 단일 `ConcreteClusterPath`를 처리한다.
- 데이터 버전을 유지하며 `IncreaseDataVersion`을 제공한다.
- 데이터 버전은 스펙에 맞게 임의 값으로 초기화된다.
- `ReadAttribute`는 기본 구현 대상에서 제외된다. 해당 메서드는 featuremap과 revision을 처리해야 한다.

#### 생성과 상태

- `DefaultServerCluster(const ConcreteClusterPath & path)`는 `mPath`를 초기화한다.
- `constexpr DefaultServerCluster(ConcreteClusterPath && path)`는 `std::move(path)`로 `mPath`를 초기화한다.
  - 이 생성자에서 `mDataVersion`은 `constexpr` 초기화 요구 때문에 `0`으로 설정된다.
  - 실제 데이터 버전 초기화는 시작 시 수행된다.
- `mPath`는 `const ConcreteClusterPath`이다.
- `mContext`는 처음에 `nullptr`이다.
- `IsStarted()`는 `mContext != nullptr`를 반환한다.

#### 인터페이스 기본 동작

| 메서드 | 동작 |
|---|---|
| `Startup` | 클러스터당 한 번의 초기화만 허용한다. 이미 초기화된 객체에는 `CHIP_ERROR_ALREADY_INITIALIZED`로 실패한다 |
| `Shutdown` | 객체를 초기화 해제한다 |
| `GetPaths` | `mPath` 하나를 포함하는 `Span<const ConcreteClusterPath>`를 반환한다 |
| `GetDataVersion` | `mDataVersion`을 반환한다 |
| `GetClusterFlags` | 선언이 제공되며, 본문은 입력에 포함되어 있지 않다 |
| `WriteAttribute` | 모든 속성 쓰기에 대해 지원되지 않는 쓰기 오류를 반환하는 기본 동작을 제공한다 |
| `Attributes` | API 계약에서 요구하는 전역 속성만 반환한다. 비전역 속성을 지원하려면 구현해야 한다 |
| `EventInfo` | `eventInfo.readPrivilege`를 `Access::Privilege::kView`로 설정하고 `CHIP_NO_ERROR`를 반환한다 |
| `InvokeCommand` | 기본적으로 `UnsupportedCommand` 오류를 반환한다 |
| `AcceptedCommands` | 기본적으로 목록 항목을 생성하지 않는 NOOP이다 |
| `GeneratedCommands` | 기본적으로 목록 항목을 생성하지 않는 NOOP이다 |
| `GlobalAttributes` | 스펙 `7.13 Global Elements / Table 93: Global Attributes`의 모든 전역 속성을 반환하는 정적 메서드이다 |

`EventInfo`는 이벤트 읽기 가능성이 관련될 때 구현한다. `InvokeCommand`와 `AcceptedCommands`는 클러스터가 명령을 지원할 때, `GeneratedCommands`는 값을 반환하는 명령을 지원할 때 구현한다.

#### 데이터 버전과 속성 변경 알림

`IncreaseDataVersion()`은 `mDataVersion`을 증가시킨다.

`NotifyAttributeChanged`는 지정한 속성의 값이 변경되었음을 표시한다.

- 클러스터 데이터 버전을 증가시킨다.
- 클러스터 컨텍스트가 있으면 속성 변경을 알린다.
- `type`의 기본값은 `DataModel::AttributeChangeType::kReportable`이다.

`SetAttributeValue`는 값 변경과 알림을 결합하는 세 가지 오버로드를 제공한다.

| 대상 | 변경 조건과 동작 |
|---|---|
| 일반 `T` | `dest != value`인 경우 값을 대입하고 `NotifyAttributeChanged`를 호출한다 |
| `DataModel::Nullable<T>`와 `DataModel::NullNullable` | `dest`가 null이 아닌 경우 `SetNull()`을 호출하고 변경을 알린다 |
| `DataModel::Nullable<T>`와 값 | `dest != static_cast<T>(value)`인 경우 `SetNonNull(value)`를 호출하고 변경을 알린다 |

변경이 없으면 `false`, 새 값으로 변경되면 `true`를 반환한다. 값을 받는 오버로드는 `std::enable_if_t<std::is_convertible_v<U, T>>`로 변환 가능성을 제한한다.

`NotifyAttributeChangedIfSuccess`는 `status`가 성공일 때만 속성 변경을 알리고, 전달받은 `status`를 반환한다. `type`은 `NotifyAttributeChanged`에 전달되며, 보고를 유발하지 않는 변경을 나타내는 데 사용할 수 있다.