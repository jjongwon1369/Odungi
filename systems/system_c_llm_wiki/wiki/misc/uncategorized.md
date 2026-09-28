---
entity: uncategorized
ids: []
source_paths: ['data_model/README.md', 'src/app/SpecificationDefinedRevisions.h', 'src/app/server-cluster/DefaultServerCluster.h', 'data_model/1.7/spec_tag', 'data_model/1.7/scraper_version', 'data_model/1.7/spec_sha']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-5.6-luna
---

## 개요

`data_model` 폴더는 Matter 클러스터의 기계 판독 가능한 표현을 포함합니다.

- 인증 테스트와 문서화에 사용됩니다.
- 특정 revision의 공식 specification data model을 나타냅니다.
- `data_model tiger team (DMTT)`가 관리하며 새로운 공식 specification 또는 specification ballot이 릴리스될 때 업데이트됩니다.
- `zap` 또는 SDK codegen에는 사용되지 않습니다.
- 클러스터 또는 device type implementer가 수동으로 수정해서는 안 됩니다.

현재 `data_model/1.7`의 메타데이터는 다음과 같습니다.

| 항목 | 값 |
|---|---|
| `spec_tag` | `0.9-1.7-winter2027` |
| `scraper_version` | `alchemy version: v1.7.10` |
| `spec_sha` | `214e40c9d51cfe89050eae68ca5b76238fcfa332` |

## 스펙

### Data Model 버전 선택

테스트 실행 중 testing infrastructure의 `basic_composition.py`는 DUT와 통신합니다.

1. endpoint 0의 `BasicInformation` cluster에서 DUT의 활성 `SpecificationVersion` attribute를 읽습니다.
2. `spec_parsing.py`의 `dm_from_spec_version()`을 통해 revision number를 명시적인 `prebuilt` version directory에 매핑합니다.
3. 예를 들어 `1.6` directory를 사용하여 test harness가 장치가 선언한 specification baseline에 대해 검증하도록 합니다.

### Data Model Errata Engine

`next` 기능을 개발하거나 안정적으로 체크인된 XML에 대해 Interaction Data Model (IDM) 테스트가 실패하도록 만드는 specification typo를 수정할 때 XML을 직접 편집해서는 안 됩니다.

대신 declarative errata overlay 파일인 `errata_future.yaml`을 사용합니다.

새 overlay entry를 추가하거나 새로운 override key를 지원하도록 engine의 core capabilities를 확장하는 방법은 [Data Model Errata Guide](../docs/guides/data_model_errata.md)를 참고합니다.

### 현재 specification revision directory 업데이트

기존 `data_model` directory의 파일을 revision 또는 alchemy release에 맞게 업데이트할 때는 다음 script를 사용합니다.

```text
scripts/spec_xml/generate_spec_xml.py
```

주요 절차는 다음과 같습니다.

1. 원하는 sha/tag/branch의 specification repository를 checkout합니다.

   ```text
   https://github.com/CHIP-Specifications/connectedhomeip-spec
   ```

2. include level을 결정합니다.
   - current ballot includes
   - no in-progress includes
   - all in-progress includes

   `Current`를 사용해 파일을 생성하는 경우 script 내부의 include list를 ballot email과 대조해야 합니다.

3. `scripts/spec_xml/generate_spec_xml.py`를 실행하고 모든 파일 변경 사항을 체크인합니다.
4. `scripts/spec_xml/spec_revision_diff_summary.py`를 사용하여 서로 다른 두 directory의 data model 파일 차이 요약을 생성할 수 있습니다.
5. 요약과 생성된 ID 파일에서 provisional marking이 예상대로인지 확인합니다.
6. specification SHA와 scraper version을 모두 업데이트하는 경우, 변경 원인을 검토자가 구분할 수 있도록 가능하면 두 개의 별도 commit으로 나눕니다.
7. PR을 push하기 전에 `build_python.sh`를 실행하고 virtual environment를 활성화한 뒤 `src/python_testing`의 모든 `TestSpec*` 테스트를 실행합니다.

### 새로운 revision의 Data Model 파일 추가

새로운 Data Model 파일도 다음 script로 생성합니다.

```text
scripts/spec_xml/generate_spec_xml.py
```

PR 작성 시 권장되는 commit 순서는 다음과 같습니다.

- 이전 revision을 새 directory 이름으로 복사한 commit을 첫 번째 commit으로 추가합니다.
- 이전 revision과 동일한 alchemy release를 사용하는 commit을 추가합니다.
- alchemy revision 변경이 필요한 경우 별도 commit으로 분리합니다.
- `scripts/spec_xml/spec_revision_diff_summary.py`로 revision 간 차이 요약을 생성하여 PR 설명에 사용할 수 있습니다.

새 revision 추가 절차는 다음과 같습니다.

1. 마지막 revision directory를 새 directory 이름으로 복사하고 commit합니다.
2. 원하는 sha/tag/branch의 specification repository를 checkout합니다.

   ```text
   https://github.com/CHIP-Specifications/connectedhomeip-spec
   ```

3. include level을 결정합니다.
4. `scripts/spec_xml/generate_spec_xml.py`로 새 Data Model 파일을 생성합니다.
5. `build_python.sh`를 실행하고 `src/python_testing`의 모든 `TestSpec*` 테스트를 실행합니다.
6. 오류가 발생하면 specification에서 수정하거나 specification repository의 errata file을 업데이트합니다.
7. 파일 생성이 올바르게 완료되면 모든 변경 사항을 commit합니다.
8. `scripts/spec_xml/spec_revision_diff_summary.py`로 PR 설명을 생성합니다.
9. 다음 항목을 확인합니다.
   - 예상되는 provisional element가 계속 provisional로 표시되는지 확인
   - 예상하지 않은 provisional element가 없는지 확인
   - cluster와 device type 변경에 revision update가 동반되는지 확인
   - 두 revision 간 모든 변경이 예상된 것인지 확인

SDK와 parsing support를 새 revision에 맞게 업데이트하려면 다음 파일을 갱신합니다.

- `src/python_testing/matter_testing_infrastructure/BUILD.gn`
  - 새 파일의 zip을 생성하고 포함하도록 업데이트합니다.
- `src/python_testing/matter_testing_infrastructure/data_model_xmls.gni`
  - `generate_spec_xml.py` 실행 시 file list가 갱신됩니다.
- `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py`
  - `PrebuiltDataModelDirectory` enum에 새 directory를 추가합니다.
  - `dm_from_spec_version`을 업데이트합니다.
- `src/python_testing/TestSpecParsingDeviceType.py`
- `src/python_testing/TestSpecParsingSelection.py`
- `src/python_testing/TestSpecParsingSupport.py`
- `src/app/SpecificationDefinedRevisions.h`
- `.github/workflows/check-data-model-directory-updates.yaml`

## SDK 정의

### `src/app/SpecificationDefinedRevisions.h`

`chip::Revision` namespace는 SDK가 기준으로 사용하는 revision 및 specification version을 정의합니다.

```cpp
namespace chip {
namespace Revision {

inline constexpr InteractionModelRevision kInteractionModelRevision = 12;
inline constexpr uint8_t kInteractionModelRevisionTag               = 0xFF;

inline constexpr uint16_t kDataModelRevision = 22;

inline constexpr uint32_t kSpecificationVersion = 0x01070000;

} // namespace Revision
} // namespace chip
```

| 식별자 | 값 | 설명 |
|---|---:|---|
| `kInteractionModelRevision` | `12` | interaction model revision을 식별하는 monotonic number |
| `kInteractionModelRevisionTag` | `0xFF` | interaction model revision tag |
| `kDataModelRevision` | `22` | Node가 인증된 Data Model revision을 식별하는 monotonic number |
| `kSpecificationVersion` | `0x01070000` | Node가 인증된 specification version |

참조 specification 섹션:

- `Interaction Model Specification` chapter의 `8.1.1. "Revision History"`
- `Data Model Specification` chapter의 `7.1.1. "Revision History"`
- `Service and Device Management` chapter의 `11.1.5.22. "SpecificationVersion Attribute"`

### `DefaultServerCluster`

파일:

```text
src/app/server-cluster/DefaultServerCluster.h
```

`DefaultServerCluster`는 `ServerClusterInterface`의 대부분의 method에 대한 구현을 제공하여 spec-compliant class 구현을 단순화합니다.

주요 특성:

- 생성 시 설정된 단일 `ConcreteClusterPath`를 처리합니다.
- data version을 유지합니다.
- `IncreaseDataVersion`을 제공합니다.
- data version을 specification에 맞게 random value로 초기화합니다.
- 대부분의 virtual method에 default implementation을 제공합니다.
- `ReadAttribute`는 `featuremap`과 revision을 처리해야 하므로 예외적으로 default implementation 대상이 아닙니다.

```cpp
class DefaultServerCluster : public ServerClusterInterface
```

생성자:

```cpp
DefaultServerCluster(const ConcreteClusterPath & path) : mPath(path) {}

constexpr DefaultServerCluster(ConcreteClusterPath && path) :
    mPath(std::move(path)),
    mDataVersion(0)
{}
```

`constexpr` 생성자에서는 초기화가 필요하므로 `mDataVersion`을 `0`으로 초기화하며, 실제 data version은 startup 시 초기화됩니다.

## 구현

### `ServerClusterInterface` 구현

`DefaultServerCluster`는 다음 method를 제공합니다.

```cpp
CHIP_ERROR Startup(ServerClusterContext & context) override;
void Shutdown(ClusterShutdownType) override;
```

- `Startup`은 cluster마다 한 번만 초기화할 수 있습니다.
- 이미 초기화된 object에서 호출하면 `CHIP_ERROR_ALREADY_INITIALIZED`로 실패합니다.
- `Shutdown`을 호출하면 object를 de-initialize할 수 있습니다.

```cpp
[[nodiscard]] Span<const ConcreteClusterPath> GetPaths() const override
{
    return { &mPath, 1 };
}

[[nodiscard]] DataVersion GetDataVersion(const ConcreteClusterPath &) const override
{
    return mDataVersion;
}

[[nodiscard]] BitFlags<DataModel::ClusterQualityFlags>
GetClusterFlags(const ConcreteClusterPath &) const override;
```

### Attribute 처리

모든 attribute에 대한 write는 기본적으로 unsupported write 오류를 반환합니다.

```cpp
DataModel::ActionReturnStatus WriteAttribute(
    const DataModel::WriteAttributeRequest & request,
    AttributeValueDecoder & decoder) override;
```

non-global attribute 지원이 필요한 경우 `Attributes`를 구현해야 합니다. 기본 구현은 API contract에 필요한 global attribute만 반환합니다.

```cpp
CHIP_ERROR Attributes(
    const ConcreteClusterPath & path,
    ReadOnlyBufferBuilder<DataModel::AttributeEntry> & builder) override;
```

event readability가 필요한 경우 `EventInfo`를 사용할 수 있습니다.

```cpp
CHIP_ERROR EventInfo(
    const ConcreteEventPath & path,
    DataModel::EventEntry & eventInfo) override
{
    eventInfo.readPrivilege = Access::Privilege::kView;
    return CHIP_NO_ERROR;
}
```

### Command 처리

cluster가 command를 지원하는 경우 다음 method를 구현해야 합니다.

```cpp
std::optional<DataModel::ActionReturnStatus> InvokeCommand(
    const DataModel::InvokeRequest & request,
    chip::TLV::TLVReader & input_arguments,
    CommandHandler * handler) override;
```

기본 구현은 `UnsupportedCommand` 오류를 반환합니다.

Accepted command 목록은 다음 method로 제공합니다.

```cpp
CHIP_ERROR AcceptedCommands(
    const ConcreteClusterPath & path,
    ReadOnlyBufferBuilder<DataModel::AcceptedCommandEntry> & builder) override;
```

기본 구현은 list item을 생성하지 않는 `NOOP`입니다.

command가 반환 값을 생성하는 경우 generated command 목록을 제공합니다.

```cpp
CHIP_ERROR GeneratedCommands(
    const ConcreteClusterPath & path,
    ReadOnlyBufferBuilder<CommandId> & builder) override;
```

이 method의 기본 구현도 list item을 생성하지 않는 `NOOP`입니다.

global attribute 전체 목록은 다음 static method로 제공합니다.

```cpp
static Span<const DataModel::AttributeEntry> GlobalAttributes();
```

이는 `7.13 Global Elements / Table 93: Global Attributes`에 정의된 global attribute를 반환합니다.

### Data version 및 attribute 변경 알림

내부 상태:

```cpp
const ConcreteClusterPath mPath;
ServerClusterContext * mContext = nullptr;
DataVersion mDataVersion;
```

`IsStarted`는 context 존재 여부를 반환합니다.

```cpp
bool IsStarted() const { return mContext != nullptr; }
```

`IncreaseDataVersion`은 data version을 증가시킵니다.

```cpp
void IncreaseDataVersion() { mDataVersion++; }
```

특정 attribute가 변경되었음을 표시하려면 `NotifyAttributeChanged`를 사용합니다.

```cpp
void NotifyAttributeChanged(
    AttributeId attributeId,
    DataModel::AttributeChangeType type =
        DataModel::AttributeChangeType::kReportable);
```

이 method는 다음 작업을 수행합니다.

- cluster data version을 증가시킵니다.
- `ServerClusterContext`가 있으면 attribute 변경을 알립니다.

`SetAttributeValue`는 값이 실제로 변경된 경우에만 값을 업데이트하고 `NotifyAttributeChanged`를 호출하는 일반적인 패턴을 제공합니다.

```cpp
template <typename T, typename U,
          typename = std::enable_if_t<std::is_convertible_v<U, T>>>
bool SetAttributeValue(
    T & dest,
    const U & value,
    AttributeId attributeId,
    DataModel::AttributeChangeType type =
        DataModel::AttributeChangeType::kReportable);
```

`DataModel::Nullable<T>`에 대해서는 null 설정 및 non-null 값 설정을 지원합니다.

```cpp
template <typename T>
bool SetAttributeValue(
    DataModel::Nullable<T> & dest,
    decltype(DataModel::NullNullable),
    AttributeId attributeId,
    DataModel::AttributeChangeType type =
        DataModel::AttributeChangeType::kReportable);
```

```cpp
template <typename T, typename U,
          typename = std::enable_if_t<std::is_convertible_v<U, T>>>
bool SetAttributeValue(
    DataModel::Nullable<T> & dest,
    const U & value,
    AttributeId attributeId,
    DataModel::AttributeChangeType type =
        DataModel::AttributeChangeType::kReportable);
```

변경 값이 기존 값과 같으면 `false`를 반환하고 변경하지 않습니다. 값이 변경되면 `true`를 반환합니다.

성공한 status에 대해서만 attribute 변경을 알리려면 다음 method를 사용합니다.

```cpp
DataModel::ActionReturnStatus NotifyAttributeChangedIfSuccess(
    AttributeId attributeId,
    DataModel::ActionReturnStatus status,
    DataModel::AttributeChangeType type =
        DataModel::AttributeChangeType::kReportable);
```

`type`을 사용하면 cluster revision을 증가시키지만 report를 발생시키지 않는 변경을 표시할 수 있습니다. 이 method는 입력받은 `status`를 반환합니다.

## 예시

### 기존 revision 업데이트

```text
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.3
IN_PROGRESS=None
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

### 새 revision 추가

```text
ALCHEMY=/path/to/alchemy
SPEC_ROOT=/path/to/spec/repo
DM_DIR=1.5
IN_PROGRESS=Current
./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
```

### Python 테스트 실행

다음 예시는 chip root에서 실행하는 경로를 전제로 합니다.

```text
. scripts/activate.sh
VENV=out/py
./scripts/build_python.sh -i $VENV
source $VENV/bin/activate
python3 src/python_testing/TestSpecParsingSupport.py
python3 src/python_testing/TestSpecParsingSelection.py
python3 src/python_testing/TestSpecParsingDeviceType.py
```

## 관련 문서

- [Data Model Errata Guide](../docs/guides/data_model_errata.md)
- `https://github.com/CHIP-Specifications/connectedhomeip-spec`
- `scripts/spec_xml/generate_spec_xml.py`
- `scripts/spec_xml/spec_revision_diff_summary.py`
- `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py`
- `src/app/SpecificationDefinedRevisions.h`
- `.github/workflows/check-data-model-directory-updates.yaml`