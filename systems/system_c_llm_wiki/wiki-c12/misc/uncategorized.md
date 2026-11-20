---
entity: uncategorized
ids: []
source_paths: ['data_model/1.7/scraper_version', 'data_model/1.7/spec_sha', 'data_model/1.7/spec_tag', 'data_model/README.md', 'src/app/SpecificationDefinedRevisions.h', 'src/app/server-cluster/DefaultServerCluster.h']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# uncategorized

## 개요

제공된 자료는 Matter 데이터 모델 XML의 버전 정보와 관리 절차, SDK의 리비전 상수, `DefaultServerCluster`의 기본 동작을 다룬다.

### 데이터 모델 버전 정보

| 원본 경로 | 값 |
|---|---|
| `data_model/1.7/scraper_version` | `alchemy version: v1.7.10` |
| `data_model/1.7/spec_sha` | `214e40c9d51cfe89050eae68ca5b76238fcfa332` |
| `data_model/1.7/spec_tag` | `0.9-1.7-winter2027` |

### 데이터 모델 XML의 용도와 관리

출처: `data_model/README.md`

- Matter 클러스터를 기계가 읽을 수 있는 형태로 표현하며, 특정 리비전의 공식 스펙 데이터 모델을 나타낸다.
- 인증 테스트와 문서화에 사용된다.
- data model tiger team(DMTT)이 관리하며, 새로운 공식 스펙 또는 스펙 ballot이 공개되면 갱신한다.
- zap 또는 SDK codegen에는 사용하지 않는다.
- 클러스터 또는 디바이스 타입 구현자가 XML을 직접 수정해서는 안 된다.

#### 테스트에서 데이터 모델 버전을 선택하는 방식

1. 테스트 인프라의 `basic_composition.py`가 실제 Matter 디바이스(DUT)와 통신한다.
2. endpoint 0의 `BasicInformation` 클러스터에서 활성 `SpecificationVersion` 속성을 읽는다.
3. `spec_parsing.py`의 `dm_from_spec_version()`이 해당 값을 명시적인 `prebuilt` 버전 디렉터리(예: `1.6`)로 매핑한다.
4. 테스트 하네스는 DUT가 선언한 스펙 기준에 맞춰 검증한다.

#### Data Model Errata Engine

`next` 기능을 개발하거나, 저장소의 안정 XML을 기준으로 Interaction Data Model(IDM) 테스트 실패를 유발하는 스펙 오타를 수정할 때는 XML을 직접 편집하지 않는다. 대신 선언적 errata overlay 파일인 `errata_future.yaml`을 사용한다.

새 overlay 항목을 추가하거나 새로운 override key를 지원하도록 엔진을 확장하는 방법은 [Data Model Errata Guide](../docs/guides/data_model_errata.md)를 참조한다.

### 기존 데이터 모델 리비전 갱신

`data_model`에 이미 있는 리비전이나 alchemy release를 갱신할 때는 `scripts/spec_xml/generate_spec_xml.py`를 사용한다. 사용법은 해당 스크립트의 `--help`로 확인한다.

1. [스펙 저장소](https://github.com/CHIP-Specifications/connectedhomeip-spec)를 원하는 sha/tag/branch로 checkout한다.
2. 현재 ballot의 include, 진행 중인 항목 제외, 진행 중인 모든 항목 포함 중 원하는 include 수준을 결정한다.
   - `Current`를 사용하면 스크립트의 include 목록을 ballot 이메일과 대조한다.
3. 스크립트를 실행하고 생성된 모든 변경 사항을 커밋한다.

```sh
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.3
IN_PROGRESS=None
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

4. `scripts/spec_xml/spec_revision_diff_summary.py`로 두 디렉터리의 데이터 모델 차이를 요약할 수 있다.
5. 요약과 생성된 ID 파일을 확인하여 provisional 표시가 예상과 일치하는지 검토한다.
6. spec SHA와 scraper version을 모두 변경한다면, 변경 원인을 구분할 수 있도록 두 커밋으로 나누는 것이 권장된다.
7. PR을 push하기 전에 `build_python.sh`를 실행하고 venv를 활성화한 뒤, `src/python_testing`의 모든 `TestSpec*` 테스트를 실행한다.

다음 명령은 chip 루트에서 실행하는 경로를 기준으로 한다. `VENV`는 원하는 경로로 설정한다.

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

1. 직전 리비전 디렉터리를 새 디렉터리 이름으로 복사하고 첫 커밋으로 남긴다.
2. 스펙 저장소를 원하는 sha/tag/branch로 checkout하고 include 수준을 결정한다.
   - `Current`를 사용하면 include 목록을 ballot 이메일과 대조한다.
3. 이전 리비전과 동일한 alchemy release로 새 데이터 모델을 생성한다.
   - alchemy revision 변경이 필요하면 가능한 한 별도 커밋으로 분리한다.

```sh
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.5
IN_PROGRESS=Current
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

4. `build_python.sh` 실행과 venv 활성화 후 `src/python_testing`의 모든 `TestSpec*` 테스트를 실행한다.
5. 오류가 있으면 스펙 자체 또는 스펙 저장소의 errata 파일에서 수정하는 것을 우선한다.
6. 정상적으로 생성된 모든 변경 사항을 커밋한다.
7. `scripts/spec_xml/spec_revision_diff_summary.py`로 PR 설명에 사용할 차이 요약을 생성한다.

요약과 생성된 ID 파일에서는 다음을 확인한다.

- 예상한 모든 provisional 요소에 표시가 유지되는지
- 예상하지 못한 provisional 요소가 없는지
- 클러스터와 디바이스 타입 변경에 리비전 갱신이 동반되는지
- 두 리비전 사이의 모든 변경이 예상한 것인지

#### 새 리비전 연결 지점

| 파일 | 필요한 변경 |
|---|---|
| `src/python_testing/matter_testing_infrastructure/BUILD.gn` | 새 파일의 zip을 생성하고 포함하도록 갱신 |
| `src/python_testing/matter_testing_infrastructure/data_model_xmls.gni` | 파일 목록은 `generate_spec_xml.py` 실행 과정에서 갱신됨 |
| `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py` | `PrebuiltDataModelDirectory` enum에 새 디렉터리를 추가하고 `dm_from_spec_version` 갱신 |
| `src/python_testing/TestSpecParsingDeviceType.py` | 새 데이터 모델의 단위 테스트 추가 |
| `src/python_testing/TestSpecParsingSelection.py` | 새 데이터 모델의 단위 테스트 추가 |
| `src/python_testing/TestSpecParsingSupport.py` | 새 데이터 모델의 단위 테스트 추가 |
| `src/app/SpecificationDefinedRevisions.h` | SDK가 사용하는 스펙 리비전 갱신 |
| `.github/workflows/check-data-model-directory-updates.yaml` | GitHub CI 데이터 모델 리비전 검사기에 새 데이터 모델 추가 |

### SDK 리비전 상수

출처: `src/app/SpecificationDefinedRevisions.h`

다음 상수는 `chip::Revision`에 정의되어 있다.

| 식별자 | 타입 | 값 | 의미 |
|---|---|---|---|
| `kInteractionModelRevision` | `InteractionModelRevision` | `12` | Interaction Model 리비전을 식별하는 단조 증가 번호 |
| `kInteractionModelRevisionTag` | `uint8_t` | `0xFF` | 원문에 별도의 의미 설명 없음 |
| `kDataModelRevision` | `uint16_t` | `22` | Node가 인증받은 Data Model 리비전을 식별하는 단조 증가 번호 |
| `kSpecificationVersion` | `uint32_t` | `0x01070000` | Node가 인증받은 스펙 버전을 식별하는 번호 |

헤더 주석에서 참조하는 core Matter specification 항목은 다음과 같다.

- `kInteractionModelRevision`: “Interaction Model Specification”의 8.1.1. “Revision History”
- `kDataModelRevision`: “Data Model Specification”의 7.1.1. “Revision History”
- `kSpecificationVersion`: “Service and Device Management”의 11.1.5.22. “SpecificationVersion Attribute”

### `DefaultServerCluster` 기본 동작

출처: `src/app/server-cluster/DefaultServerCluster.h`

`chip::app::DefaultServerCluster`는 `ServerClusterInterface`를 상속하며, 스펙을 준수하는 클래스 구현을 돕기 위해 대부분의 메서드에 기본 동작을 제공한다.

- 생성 시 지정한 단일 `ConcreteClusterPath`를 처리한다.
- 데이터 버전을 유지하며, 스펙에 맞게 임의 값으로 초기화한다.
- `IncreaseDataVersion`을 제공한다.
- featuremap과 revision을 처리해야 하는 `ReadAttribute`는 기본 구현 제공 대상에서 제외된다.
- `constexpr` 생성자는 `mDataVersion`을 `0`으로 초기화하며, 실제 데이터 버전 초기화는 startup에서 수행된다.

#### 수명 주기와 조회

| 메서드 | 동작 |
|---|---|
| `Startup` | 클러스터당 한 번의 초기화만 허용하며, 이미 초기화되었다면 `CHIP_ERROR_ALREADY_INITIALIZED`로 실패 |
| `Shutdown` | 객체의 초기화 상태 해제 |
| `GetPaths` | `mPath` 하나를 포함하는 `Span<const ConcreteClusterPath>` 반환 |
| `GetDataVersion` | `mDataVersion` 반환 |
| `GetClusterFlags` | 헤더에 선언되어 있으며, 제공된 코드에는 본문이 없음 |
| `IsStarted` | `mContext != nullptr` 여부 반환 |

#### 속성·이벤트·명령의 기본 처리

| 메서드 | 기본 동작 및 재정의 조건 |
|---|---|
| `WriteAttribute` | 모든 속성 쓰기에 대해 unsupported write 오류 반환 |
| `Attributes` | API 계약에서 요구하는 전역 속성만 반환. 비전역 속성이 필요하면 구현 |
| `EventInfo` | `eventInfo.readPrivilege`를 `Access::Privilege::kView`로 설정하고 `CHIP_NO_ERROR` 반환. 이벤트 읽기 가능 여부를 별도로 처리해야 하면 구현 |
| `InvokeCommand` | `UnsupportedCommand` 오류 반환. 클러스터가 명령을 지원하면 구현 |
| `AcceptedCommands` | 목록 항목을 생성하지 않는 NOOP. 명령을 지원하면 구현 |
| `GeneratedCommands` | 목록 항목을 생성하지 않는 NOOP. 반환값이 있는 명령을 지원하면 구현 |
| `GlobalAttributes` | `7.13 Global Elements / Table 93: Global Attributes`에 정의된 모든 전역 속성 반환 |

#### 속성 변경과 데이터 버전

- `IncreaseDataVersion()`은 `mDataVersion`을 증가시킨다.
- `NotifyAttributeChanged`는 데이터 버전을 증가시키고, 클러스터 context가 있으면 속성 변경을 알린다.
- `SetAttributeValue`는 값이 달라질 때만 값을 갱신하고 `NotifyAttributeChanged`를 호출한다.
  - 변경되면 `true`, 변경되지 않으면 `false`를 반환한다.
  - 일반 값, `DataModel::Nullable<T>`의 `DataModel::NullNullable` 설정, 비-null 값 설정을 처리하는 overload가 제공된다.
- `NotifyAttributeChangedIfSuccess`는 `status`가 성공일 때 속성 변경을 알리고, 전달받은 `status`를 반환한다.
  - `type`을 통해 report를 발생시키지 않는 변경도 지정할 수 있다.
- 변경 알림 관련 `type`의 기본값은 `DataModel::AttributeChangeType::kReportable`이다.