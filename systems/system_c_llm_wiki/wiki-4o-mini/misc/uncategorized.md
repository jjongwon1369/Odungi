---
entity: uncategorized
ids: []
source_paths: ['data_model/README.md', 'src/app/SpecificationDefinedRevisions.h', 'src/app/server-cluster/DefaultServerCluster.h', 'data_model/1.7/spec_tag', 'data_model/1.7/scraper_version', 'data_model/1.7/spec_sha']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: misc
compiled_by: openai/gpt-4o-mini
---

## 개요

이 폴더는 Matter 클러스터의 기계 읽기 가능 표현을 포함하고 있습니다. 이 파일들은 현재 인증 테스트 및 문서화에 사용되고 있으며, 데이터 모델 파일은 특정 리비전의 공식 사양 데이터 모델을 나타냅니다. 이 디렉토리의 파일들은 데이터 모델 타이거 팀(DMTT)에서 유지 관리하며, 새로운 공식 사양이나 사양 투표가 발표될 때 업데이트됩니다.

데이터 모델 파일은 zap이나 SDK 코드 생성에 사용되지 않으며, 클러스터 또는 장치 유형 구현자가 수동으로 업데이트해서는 안 됩니다.

## SDK 정의

```cpp
namespace chip {
namespace Revision {

/**
 * A monothonic number identifying the interaction model revision.
 *
 * See section 8.1.1. "Revision History" in the "Interaction Model
 * Specification" chapter of the core Matter specification.
 */
inline constexpr InteractionModelRevision kInteractionModelRevision = 12;
inline constexpr uint8_t kInteractionModelRevisionTag               = 0xFF;

/**
 * A monotonic number identifying the revision number of the Data Model against
 * which the Node is certified.
 *
 * See section 7.1.1. "Revision History" in the "Data Model Specification"
 * chapter of the core Matter specification.
 */
inline constexpr uint16_t kDataModelRevision = 22;

/*
 * A number identifying the specification version against which the
 * Node is certified.
 *
 * See section 11.1.5.22. "SpecificationVersion Attribute" in "Service and
 * Device Management" chapter of the core Matter specification.
 */
inline constexpr uint32_t kSpecificationVersion = 0x01070000;

} // namespace Revision
} // namespace chip
```

## 구현

### DefaultServerCluster.h

```cpp
class DefaultServerCluster : public ServerClusterInterface
{
public:
    DefaultServerCluster(const ConcreteClusterPath & path) : mPath(path) {}

    CHIP_ERROR Startup(ServerClusterContext & context) override;
    void Shutdown(ClusterShutdownType) override;

    [[nodiscard]] Span<const ConcreteClusterPath> GetPaths() const override { return { &mPath, 1 }; }

    [[nodiscard]] DataVersion GetDataVersion(const ConcreteClusterPath &) const override { return mDataVersion; }
    [[nodiscard]] BitFlags<DataModel::ClusterQualityFlags> GetClusterFlags(const ConcreteClusterPath &) const override;

    DataModel::ActionReturnStatus WriteAttribute(const DataModel::WriteAttributeRequest & request,
                                                 AttributeValueDecoder & decoder) override;

    CHIP_ERROR EventInfo(const ConcreteEventPath & path, DataModel::EventEntry & eventInfo) override;
    std::optional<DataModel::ActionReturnStatus> InvokeCommand(const DataModel::InvokeRequest & request,
                                                               chip::TLV::TLVReader & input_arguments,
                                                               CommandHandler * handler) override;

    static Span<const DataModel::AttributeEntry> GlobalAttributes();

protected:
    const ConcreteClusterPath mPath;
    ServerClusterContext * mContext = nullptr;

private:
    DataVersion mDataVersion; // will be random-initialized as per spec
};
```

## 예시

### 데이터 모델 파일 업데이트

1. 스크립트 실행:
   ```bash
   ALCHEMY=/path/to/alchemy
   SPEC_ROOT=/path/to/spec/repo
   DM_DIR=1.5
   IN_PROGRESS=Current
   ./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
   ```

### 데이터 모델 파일 추가

1. 마지막 리비전을 복사하여 새로운 디렉토리 이름에 커밋
2. 새 데이터 모델 파일 생성:
   ```bash
   ./scripts/spec_xml/generate_spec_xml.py --scraper $ALCHEMY --spec-root $SPEC_ROOT --include-in-progress $IN_PROGRESS --output-dir data_model/$DM_DIR
   ```

## 관련 문서

- [Data Model Errata Guide](../docs/guides/data_model_errata.md)