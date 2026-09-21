# Corpus v0.1 extraction

Python 3.10+ 표준 라이브러리와 Git만 사용한다. 외부 패키지 설치나 SDK 빌드는 필요 없다.
프로젝트 루트에서 실행한다. 참조 checkout은 읽기 전용이며 checkout/fetch/reset/config를 실행하지 않는다.
origin은 GitHub의 connectedhomeip 또는 그 fork인지 검사하고, 실제 정체성은 고정 commit과 추적 파일로 확인한다.
dirty checkout, 다른 commit, 누락 경로, Scope/Coverage 불일치에서 실패한다.

```powershell
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --dry-run
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --validate-only
python -m unittest discover -s scripts/corpus/tests -v
```

`--dry-run`은 실제 선택·정규화·관계 생성을 메모리에서 수행하고 보고서만 stdout으로 출력한다. 파일은 쓰지 않는다.
일반 실행은 산출물을 생성하고 전체 검증 및 독립된 두 임시 디렉터리 재생성을 실행한다.
`--validate-only`는 기존 산출물을 고치지 않고 검사하며 `validation_report.json`만 갱신한다.
실패는 exit code 1, 통과 또는 알려진 경고만 있으면 0이다.
출력은 현재 프로젝트 안의 `<corpus-root>/raw`, `<corpus-root>/metadata/<snapshot>.json` 배치로 제한한다.
재실행은 알려진 산출물만 교체한다. raw에 Scope 밖 파일이 있으면 삭제하지 않고 실패한다.

## 결정성과 원본

- Raw는 `git cat-file --batch`에서 읽은 **고정 commit의 blob 바이트**다. Windows checkout의 autocrlf 결과를 원본으로 삼지 않는다.
  Git blob과 raw SHA-256을 직접 비교한다. encoding/newline/formatting을 변경하지 않는다.
- `document_id = "doc:" + SHA256(canonical_JSON(["connectedhomeip", source_path]))`.
  source_path는 저장소 상대 POSIX 경로다. canonical JSON은 UTF-8, 키 정렬, 공백 없는 separators다.
  commit·내용·출력 위치가 바뀌어도 source+path가 같으면 ID는 같다. content_hash는 별도다.
- snapshot_id는 commit, scope.json 바이트 Hash, Coverage CSV 바이트 Hash, pipeline 소스 Hash로 결정한다.
  pipeline Hash는 이 디렉터리의 Python 모듈 파일명+바이트를 정렬하여 해시한다. 테스트/README는 제외한다.
- relation_id는 commit과 정렬된 assertion 객체로 결정한다. 출처·근거·조건이 다른 주장은 합치지 않는다.
- 파일·Entity·Relation 출력 순서를 고정한다. 시각·임시 디렉터리·절대 경로를 산출물에 넣지 않는다.
- 같은 bytes가 서로 다른 허용 경로에 있으면 문서 ID는 다르며 duplicate hash 경고로 남긴다.
  같은 물리 source path는 한 번만 복사하고 여러 관계가 같은 ID를 참조한다.

## 정규화 경계

UTF-8 strict decoding(BOM 제거), CRLF/CR→LF, Scope에 따른 정확한 원문 절취만 한다.
원문의 표현·Identifier를 변경하지 않는다. XML/IDL/ZAP 조각을 LF로 연결하므로 정규화 본문 자체가
완전한 standalone XML/JSON/IDL이라는 보장은 없다. 완전한 문서는 raw에서 제공한다.
조각은 검색 chunk가 아니라 한 물리 파일의 선택 구간이며 **한 파일에 한 normalized record**를 만든다.

- 사양 XML: 선택 Cluster ID·Device Type과 조건/공통 정의를 보존한다. Cabinet Heater Cluster와
  ResourceMonitoring의 Water Tank ID는 제외한다. Root는 classification/revision/GroupcastListenerCond 문맥만 보존한다.
- SDK XML: 선택 Device Type·Cluster code와 공유 타입, global attribute를 보존한다.
  SDK Device Type의 Cluster include는 해당 제품의 선택 Cluster로 제한한다.
- `.matter`: 선택 Cluster 전체 선언, 파일 안에서 참조된 global 타입의 의존 폐쇄,
  선택 Device Type의 endpoint/server block, root endpoint의 선언 문맥만 보존한다.
- `.zap`: 선택 endpointType의 제품 metadata, 선택 Cluster 설정, endpoint 부모 관계를 보존한다.
  all-clusters 예제는 선택 Cluster 설정의 근거로 사용하며 그 endpoint를 제품 선언으로 간주하지 않는다.
- 허용 CPP/H와 Markdown은 전체 파일을 포함한다. CMake는 지정 delegate의 sources/include 연결 줄만 절취한다.
  include/import/link를 따라 추가 파일을 수집하지 않는다.

`source_spans`의 char_start/end는 **UTF-8을 decode하고 LF로 통일한 원본 view의 Unicode code point offset**이다.
끝은 exclusive이고 line_start/end는 1-based inclusive다. ZAP는 JSONPath locator도 제공한다.
본문은 각 span의 원문을 순서대로 LF로 연결한 결과와 정확히 같아야 한다.
Identifier inventory는 선택한 원본 span에서 추출한 영문 식별자·정수·hex ID의 빈도표와 본문을 비교한다.
이는 이름/값 보존 검사이며 사양 적합성이나 실제 실행 동작의 검증이 아니다.

## Metadata와 관계

최신 요청에 맞춰 manifest에서 물리 형식 필드를 `doc_type`으로 제공한다.
taxonomy의 이전 `content_kind` 명칭과 중복 저장하지 않는다. source_role과 definition_kind는 별개 축이다.
`source_revision.artifact`에는 commit, declarations에는 출처별 Entity revision과 locator를 기록한다.
숫자 Revision 차이를 오류로 승격하지 않는다. C++가 생성 kRevision을 사용하는 관계도 별도 보존한다.

`device_types`/`clusters`는 파일의 범위 관련성을 나타낸다. 공유 파일은 여러 그룹에서 집계되며 합계가
고유 파일 수보다 클 수 있다. 이 배열은 해당 예제가 모든 제품/기능을 구현한다는 주장이 아니다.
관계의 assertion_scope, via_entities, requirement, conformance AST/raw, evidence를 함께 읽어야 한다.
`uses_shared_implementation`의 component 파일 membership 파생 근거를 기록하며 직접 제품 구현으로 표시하지 않는다.
Scope에 없는 기반 적용 parser 파일은 `storage=upstream_reference_only` 근거로만 기록한다.
그 파일은 고정 commit에서 존재/Hash/근거 줄을 검증하지만 raw/manifest에는 추가하지 않는다.

`scope.json`의 execution=false 등은 Finalization 당시의 이력이다. 이번 명시적 실행 요청은 snapshot의
execution_authority에 기록하고, 확정 Scope 파일은 수정하지 않는다.

## 검증과 Freeze

검증은 source commit/clean 상태, 경로, manifest/raw Hash, 중복 ID/Hash, metadata, 관계 참조/주장,
Coverage 42개 Device→Cluster/23개 고유 Cluster, 원문 위치, Identifier, 통계 및 두 독립 재생성을 검사한다.
원본 손상·Identifier 변경·중복 ID를 임시 산출물에 주입하여 실패 탐지도 테스트한다.
`validation_report.json`은 각 검사에 status/message/details를 제공한다.

v0.1은 frozen=false다. 기존 21개 Coverage missing 행은 허용된 결손이고 추출 파일 누락과 구별한다.
Temperature Alarm concrete SDK/구현/IDL, 9개 component의 독립 Markdown 부재를 숨기지 않는다.
Freeze 전에는 기존 이용/공유 조건 검토, 의미적 revision 차이 및 예제 기능 활성 상태 검토, 팀 교차 검토,
tokenizer/model 결정 및 이후 Context 적합성 확인이 남는다. 이 파이프라인은 RAG/Wiki/평가 데이터를 만들지 않는다.
