---
entity: uncategorized
ids: []
source_paths: ['data_model/README.md', 'src/app/SpecificationDefinedRevisions.h', 'src/app/server-cluster/DefaultServerCluster.h', 'data_model/1.7/spec_tag', 'data_model/1.7/scraper_version', 'data_model/1.7/spec_sha']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-6-astra
---

# uncategorized

## 개요

입력 자료는 Matter 데이터 모델 XML의 관리·검증 절차, SDK의 리비전 상수, 서버 클러스터 기본 클래스 및 `data_model/1.7`의 생성 기준 정보를 포함한다.

### 데이터 모델 XML 관리 — `data_model/README.md`

`data_model`에는 Matter 클러스터를 기계가 읽을 수 있도록 표현한 XML 파일이 있다.

- 인증 테스트와 문서화에 사용하며, 특정 리비전의 공식 스펙 데이터 모델을 나타낸다.
- data model tiger team(DMTT)이 관리하며, 새로운 공식 스펙이나 스펙 ballot이 발표되면 갱신한다.
- zap 또는 SDK codegen에는 사용하지 않는다.
- 클러스터 또는 디바이스 타입 구현자가 XML을 직접 수정해서는 안 된다.

#### 테스트 대상 데이터 모델 선택

1. 테스트 인프라의 `basic_composition.py`가 실제 Matter 디바이스(DUT)와 통신한다.
2. endpoint 0의 `BasicInformation` 클러스터에서 활성 `SpecificationVersion` 속성을 읽는다.
3. `spec_parsing.py`의 `dm_from_spec_version()`이 이 값을 명시적인 `prebuilt` 버전 디렉터리(예: `1.6`)에 매핑한다.
4. 테스트 하네스는 DUT가 선언한 스펙 기준에 맞춰 디바이스를 검증한다.

#### Data Model Errata Engine

"next" 기능 개발이나 스펙 오타 때문에 안정 버전으로 체크인된 XML을 사용하는 Interaction Data Model(IDM) 테스트가 실패하는 경우, XML을 직접 수정하지 않고 선언적 errata overlay 파일인 `errata_future.yaml`을 사용한다.

새 overlay 항목 추가 및 새로운 override key를 지원하기 위한 엔진 확장은 [Data Model Errata Guide](../docs/guides/data_model_errata.md)를 참조한다.

#### 기존 리비전 갱신

기존 `data_model` 디렉터리의 스펙 리비전이나 alchemy 릴리스를 갱신할 때는 `scripts/spec_xml/generate_spec_xml.py`를 사용한다. 사용법은 `--help`로 확인한다.

1. [스펙 저장소](https://github.com/CHIP-Specifications/connectedhomeip-spec)를 원하는 sha/tag/branch로 체크아웃한다.
2. 포함 범위를 결정한다.
   - 현재 ballot의 include
   - 진행 중인 include 제외
   - 진행 중인 include 전체 포함
3. `"Current"`를 사용한다면 스크립트의 include 목록을 ballot 이메일과 대조한다.
4. 생성 스크립트를 실행하고 모든 파일 변경을 체크인한다.

```sh
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.3
IN_PROGRESS=None
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

생성 후 확인 사항:

- `scripts/spec_xml/spec_revision_diff_summary.py`로 두 디렉터리의 데이터 모델 차이를 요약한다.
- 요약과 생성된 ID 파일에서 provisional 표시가 예상과 일치하는지 확인한다.
- 스펙 SHA와 scraper 버전을 모두 변경한다면, 변경 원인을 구분할 수 있도록 두 커밋으로 나누는 것이 좋다.
- PR을 올리기 전에 `build_python.sh`를 실행하고 venv를 활성화한 뒤, `src/python_testing`의 모든 `TestSpec*` 테스트를 실행한다.

저장소 루트에서 실행하는 테스트 명령은 다음과 같다. `VENV`는 원하는 경로로 설정한다.

```sh
. scripts/activate.sh
VENV=out/py
./scripts/build_python.sh -i $VENV
source $VENV/bin/activate
python3 src/python_testing/TestSpecParsingSupport.py
python3 src/python_testing/TestSpecParsingSelection.py
python3 src/python_testing/TestSpecParsingDeviceType.py
```

#### 새 리비전 추가

새 데이터 모델 파일도 `scripts/spec_xml/generate_spec_xml.py`로 생성한다.

권장 커밋 구성:

1. 직전 리비전 디렉터리를 새 디렉터리 이름으로 복사한 변경을 첫 커밋으로 만든다.
2. 직전 리비전과 동일한 alchemy 릴리스로 생성한 변경을 별도 커밋으로 추가한다.
3. alchemy 리비전 변경이 필요하면 가능한 한 별도 커밋으로 분리한다.

생성 절차:

1. 직전 리비전 디렉터리를 복사하고 커밋한다.
2. 스펙 저장소를 원하는 sha/tag/branch로 체크아웃한다.
3. include 범위를 결정하고, `"Current"`라면 ballot 이메일과 대조한다.
4. 새 데이터 모델 파일을 생성한다.

```sh
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.5
IN_PROGRESS=Current
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

5. `build_python.sh` 실행 및 venv 활성화 후 `src/python_testing`의 모든 `TestSpec*` 테스트를 실행한다.
6. 오류가 있으면 스펙 자체 또는 스펙 저장소의 errata 파일에서 수정하는 것을 우선한다.
7. 올바르게 생성된 모든 변경을 커밋한다.
8. `scripts/spec_xml/spec_revision_diff_summary.py`로 PR 설명에 사용할 차이 요약을 생성한다.

검토 항목:

- 예상한 provisional 요소가 모두 provisional로 표시되어 있는가?
- 예상하지 않은 provisional 요소가 없는가?
- 클러스터와 디바이스 타입 변경에 리비전 갱신이 수반되는가?
- 두 리비전 사이의 모든 변경이 예상한 것인가?
- 요약과 생성된 ID 파일의 provisional 표시가 올바른가?

새 리비전을 연동할 때 갱신할 파일은 다음과 같다.

| 파일 | 갱신 내용 |
|---|---|
| `src/python_testing/matter_testing_infrastructure/BUILD.gn` | 새 파일의 zip을 생성하고 포함하도록 갱신 |
| `src/python_testing/matter_testing_infrastructure/data_model_xmls.gni` | 파일 목록은 `generate_spec_xml.py` 실행 과정에서 갱신됨 |
| `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py` | `PrebuiltDataModelDirectory` enum에 새 디렉터리를 추가하고 `dm_from_spec_version` 갱신 |
| `src/python_testing/TestSpecParsingDeviceType.py` | 새 데이터 모델의 단위 테스트 추가 |
| `src/python_testing/TestSpecParsingSelection.py` | 새 데이터 모델의 단위 테스트 추가 |
| `src/python_testing/TestSpecParsingSupport.py` | 새 데이터 모델의 단위 테스트 추가 |
| `src/app/SpecificationDefinedRevisions.h` | SDK가 사용하는 스펙 리비전 갱신 |
| `.github/workflows/check-data-model-directory-updates.yaml` | GitHub CI 데이터 모델 리비전 검사에 새 파일 추가 |

### 리비전 상수 — `src/app/SpecificationDefinedRevisions.h`

상수는 `chip` 내부의 `Revision` namespace에 정의되어 있다.

| 식별자 | 타입 | 값 | 의미 및 원문 참조 |
|---|---|---|---|
| `kInteractionModelRevision` | `InteractionModelRevision` | `12` | Interaction Model 리비전을 식별하는 단조 증가 수. core Matter specification의 “Interaction Model Specification”, 8.1.1. “Revision History” 참조 |
| `kInteractionModelRevisionTag` | `uint8_t` | `0xFF` | 원문에 별도 의미 설명 없음 |
| `kDataModelRevision` | `uint16_t` | `22` | Node가 인증받은 Data Model 리비전을 식별하는 단조 증가 수. “Data Model Specification”, 7.1.1. “Revision History” 참조 |
| `kSpecificationVersion` | `uint32_t` | `0x01070000` | Node가 인증받은 스펙 버전. “Service and Device Management”, 11.1.5.22. “SpecificationVersion Attribute” 참조 |

### 서버 클러스터 기본 클래스 — `src/app/server-cluster/DefaultServerCluster.h`

`chip` 내부의 `app` namespace에 있는 `DefaultServerCluster`는 `ServerClusterInterface`를 상속하며, 스펙을 준수하는 클래스 구현을 돕기 위해 대부분의 메서드에 기본 구현을 제공한다.

주요 특성:

- 생성 시 지정한 단일 `ConcreteClusterPath`를 처리한다.
- 데이터 버전을 유지하고 `IncreaseDataVersion`을 제공한다.
- 데이터 버전은 스펙에 맞게 임의 값으로 초기화한다.
- `ReadAttribute`는 featuremap과 revision 처리가 필요하므로 기본 구현 대상에서 제외된다.
- `constexpr` 생성자의 `mDataVersion(0)`은 초기화 요구를 충족하기 위한 값이며, 실제 데이터 버전 초기화는 startup에서 수행한다.

#### 생명주기와 조회

| 메서드 | 동작 |
|---|---|
| `Startup` | 클러스터당 한 번만 초기화할 수 있다. 이미 초기화되었으면 `CHIP_ERROR_ALREADY_INITIALIZED`로 실패한다. |
| `Shutdown` | 객체를 초기화 해제한다. |
| `GetPaths` | `mPath` 하나를 포함하는 `Span<const ConcreteClusterPath>`를 반환한다. |
| `GetDataVersion` | `mDataVersion`을 반환한다. |
| `GetClusterFlags` | override 선언이 제공되며, 입력에는 함수 본문이 없다. |
| `IsStarted` | `mContext != nullptr` 여부를 반환한다. |
| `IncreaseDataVersion` | `mDataVersion`을 증가시킨다. |

#### 속성·이벤트·명령의 기본 처리

| 메서드 | 기본 동작 또는 재정의 조건 |
|---|---|
| `WriteAttribute` | 모든 속성 쓰기에 대해 지원하지 않는 쓰기 오류를 반환한다. |
| `Attributes` | API 계약에서 요구하는 전역 속성만 반환한다. 전역 속성 이외의 속성을 지원할 때 구현해야 한다. |
| `EventInfo` | `eventInfo.readPrivilege`를 `Access::Privilege::kView`로 설정하고 `CHIP_NO_ERROR`를 반환한다. 이벤트 읽기 권한 처리가 필요한 경우 구현한다. |
| `InvokeCommand` | `UnsupportedCommand` 오류를 반환한다. 클러스터가 명령을 지원하면 구현해야 한다. |
| `AcceptedCommands` | 목록 항목을 생성하지 않는 NOOP이다. 명령을 지원하면 구현해야 한다. |
| `GeneratedCommands` | 목록 항목을 생성하지 않는 NOOP이다. 값을 반환하는 명령을 지원하면 구현해야 한다. |
| `GlobalAttributes` | 스펙의 `7.13 Global Elements / Table 93: Global Attributes`에 정의된 모든 전역 속성을 반환한다. |

#### 속성 변경과 알림

`NotifyAttributeChanged`는 특정 속성의 값 변경을 표시한다.

- 클러스터 데이터 버전을 증가시킨다.
- 클러스터 context가 있으면 속성 변경을 알린다.
- 기본 변경 타입은 `DataModel::AttributeChangeType::kReportable`이다.

`SetAttributeValue`는 값이 실제로 변경될 때만 값을 갱신하고 `NotifyAttributeChanged`를 호출한다. 변경했으면 `true`, 변경하지 않았으면 `false`를 반환한다.

제공되는 overload는 다음을 처리한다.

- 일반 값의 비교와 대입
- `DataModel::Nullable<T>`를 `DataModel::NullNullable`로 변경: `IsNull()` 확인 후 `SetNull()` 호출
- `DataModel::Nullable<T>`를 비-null 값으로 변경: `static_cast<T>(value)`와 비교 후 `SetNonNull(value)` 호출

`NotifyAttributeChangedIfSuccess`는 `status`가 성공일 때 속성 변경을 표시하고, 전달받은 `status`를 반환한다. `type`은 `NotifyAttributeChanged` 호출에 사용되며, 보고를 발생시키지 않는 변경도 표시할 수 있다.

### `data_model/1.7` 생성 기준

| 파일 | 원문 값 |
|---|---|
| `data_model/1.7/spec_tag` | `0.9-1.7-winter2027` |
| `data_model/1.7/scraper_version` | `alchemy version: v1.7.10` |
| `data_model/1.7/spec_sha` | `214e40c9d51cfe89050eae68ca5b76238fcfa332` |