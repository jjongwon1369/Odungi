# Corpus Tier Expansion & Pipeline Generalization Plan

## 1. 목적

현재 구축된 C3 Corpus를 baseline으로 유지하면서, 동일한 Matter / connectedhomeip SSOT를 기반으로 C6, C12 Corpus까지 단계적으로 확장한다.

본 확장의 목적은 단순히 Corpus 파일 수를 늘리는 것이 아니라 다음 조건을 만족하는 **재현 가능한 다중 규모 Corpus**를 구축하는 것이다.

- 동일한 connectedhomeip Snapshot 사용
- 동일한 Corpus 생성 파이프라인 사용
- 동일한 Metadata 계약 사용
- 동일한 Validation 정책 사용
- 제품군 범위만 단계적으로 확장
- 각 Tier를 독립적으로 재생성 가능
- Tier 간 기존 정보가 보존되는지 검증 가능

Corpus Tier의 관계는 다음과 같이 정의한다.

```text
C3 ⊆ C6 ⊆ C12
```

단, 이는 전체 JSON Record가 byte-level로 동일하게 포함된다는 의미가 아니다.

Tier가 확장될 경우 다음 항목은 달라질 수 있다.

- `snapshot_id`
- `pipeline_hash`
- document의 `device_types`
- document의 `clusters`
- relation의 `via_entities`

따라서 Tier 포함 관계는 **Source / Hash / Semantic Relation / Association 보존**을 기준으로 검증한다.

계획 단계에서는 부분집합 관계만 전제한다. 실제 Build 이후 다음 조건이 모두 확인된 경우에만 strict subset을 선언한다.

```text
sources(C6) - sources(C3) ≠ ∅
sources(C12) - sources(C6) ≠ ∅
```

이 조건이 확인되면 최종 관계를 `C3 ⊂ C6 ⊂ C12`로 표기한다.

---

# 2. SSOT

모든 Tier는 동일한 connectedhomeip Commit을 사용한다.

```text
connectedhomeip commit
1ac132b5ecd42cb6c78772f2576ed6f7fc814183
```

실험 중 C3, C6, C12가 서로 다른 Commit을 사용해서는 안 된다.

connectedhomeip Repository는 프로젝트 내부에 복사하지 않고 기존 재현 계약과 동일하게 sibling Repository 구조를 사용한다.

```text
workspace/
├── Odungi/
└── connectedhomeip/
```

또는 환경변수를 통해 경로를 지정한다.

```text
CONNECTEDHOMEIP_PATH=/path/to/connectedhomeip
```

Snapshot에는 로컬 절대 경로를 저장하지 않는다.

예:

```json
{
  "repository": "project-chip/connectedhomeip",
  "commit_hash": "1ac132b5ecd42cb6c78772f2576ed6f7fc814183",
  "source_root_policy": {
    "environment_variable": "CONNECTEDHOMEIP_PATH",
    "fallback_layout": "sibling_repository"
  }
}
```

---

# 3. Corpus Tier 구성

## 3.1 C3 — Baseline

현재 구축된 Corpus를 C3 baseline으로 사용한다.

### 제품군

1. Laundry Washer
   - Device Type ID: `115`

2. Room Air Conditioner
   - Device Type ID: `114`

3. Refrigerator
   - Refrigerator: `112`
   - Temperature Controlled Cabinet: `113`

Refrigerator 제품군은 구조상 Refrigerator와 Temperature Controlled Cabinet을 함께 포함한다.

따라서:

```text
제품군: 3
Device Type: 4
```

현재 C3는 기존 테스트 13개를 통과한 상태이므로 파이프라인 일반화 전 baseline 결과를 보존한다.

---

## 3.2 C6

C3 전체 범위에 다음 3개 제품군을 추가한다.

### 추가 제품군

4. Robotic Vacuum Cleaner
   - Device Type ID: `116`

5. Dishwasher
   - Device Type ID: `117`

6. Air Purifier
   - Device Type ID: `45`

### C6 전체 제품군

```text
Laundry Washer
Room Air Conditioner
Refrigerator
Robotic Vacuum Cleaner
Dishwasher
Air Purifier
```

### C6 Device Type

```text
45   Air Purifier
112  Refrigerator
113  Temperature Controlled Cabinet
114  Room Air Conditioner
115  Laundry Washer
116  Robotic Vacuum Cleaner
117  Dishwasher
```

---

## 3.3 C12

C6 전체 범위에 다음 6개 제품군을 추가한다.

### 추가 제품군

7. Laundry Dryer
   - Device Type ID: `124`

8. Humidity Conditioner
   - Device Type ID: `125`

9. Microwave Oven
   - Device Type ID: `121`

10. Cooktop
    - Cooktop: `120`
    - Cook Surface: `119`

11. Extractor Hood
    - Device Type ID: `122`

12. Water Heater
    - Device Type ID: `1295`

### C12 전체 제품군

```text
Laundry Washer
Room Air Conditioner
Refrigerator
Robotic Vacuum Cleaner
Dishwasher
Air Purifier
Laundry Dryer
Humidity Conditioner
Microwave Oven
Cooktop
Extractor Hood
Water Heater
```

### C12 Device Type

```text
45    Air Purifier
112   Refrigerator
113   Temperature Controlled Cabinet
114   Room Air Conditioner
115   Laundry Washer
116   Robotic Vacuum Cleaner
117   Dishwasher
119   Cook Surface
120   Cooktop
121   Microwave Oven
122   Extractor Hood
124   Laundry Dryer
125   Humidity Conditioner
1295  Water Heater
```

---

# 4. 기본 확장 원칙

Corpus 파일 수를 인위적으로 맞추지 않는다.

예를 들어 다음과 같이 강제로 구성하지 않는다.

```text
C3  = 300 documents
C6  = 600 documents
C12 = 1200 documents
```

각 Tier의 실제 문서 수는 대상 Device Type, Cluster, Documentation, Definition, Implementation 등의 관계를 동일한 extraction rule로 탐색한 결과로 결정한다.

따라서 Tier별로 다음 값을 실제 결과로 측정한다.

- Unique Document 수
- Device Type 수
- Unique Cluster 수
- Entity 수
- Relation 수
- 문서 유형별 분포
- 제품군별 Source 수
- Token 수

공유되는 Source File은 제품마다 물리적으로 복제하지 않는다.

하나의 Document가 여러 Device Type 또는 Cluster와 연결되는 경우 Metadata의 다대다 관계로 표현한다.

## 4.1 Token Count 정책

Token Count를 Corpus Statistics에 기록할 경우 Tokenizer를 반드시 고정한다.

기록 항목:

- `tokenizer_name`
- `tokenizer_version`
- `tokenizer_configuration`
- `token_count`

Tokenizer가 아직 확정되지 않았다면 다음과 같이 기록한다.

```json
{
  "token_count": null,
  "tokenizer_status": "pending"
}
```

Tokenizer가 확정되기 전의 Token Count는 Tier 간 공식 비교 지표로 사용하지 않는다.

---

# 5. C6/C12 확장 전 선행 작업

현재 Corpus Pipeline에는 C3 전용 값과 정책이 하드코딩되어 있다.

따라서 C6/C12를 바로 추가하지 않는다.

먼저 기존 C3 Pipeline을 **Tier-independent Pipeline**으로 일반화한다.

전체 구현 순서는 다음과 같다.

```text
현재 C3 baseline 보존
        ↓
Pipeline Generalization
        ↓
Generic Pipeline으로 C3 재생성
        ↓
C3 Regression Validation
        ↓
C6 구축
        ↓
C12 구축
```

---

# 6. Tier Declaration

제품 범위를 Python 코드에 직접 하드코딩하지 않는다.

각 Tier는 별도의 declaration config를 가진다.

```text
corpus/
└── configs/
    ├── c3.json
    ├── c6.json
    └── c12.json
```

Tier Declaration은 최종 `scope.json` 전체를 직접 작성하는 파일이 아니다.

Tier가 **어떤 Device Type을 포함할 것인지**만 선언한다.

예:

```json
{
  "tier": "c6",
  "inherits": "c3",
  "add_device_types": [
    45,
    116,
    117
  ],
  "overrides": {}
}
```

---

# 7. Tier Config와 scope.json 분리

현재 Corpus Pipeline의 실제 `scope.json`에는 단순한 Device Type 목록보다 훨씬 많은 정보가 필요하다.

예:

- Device Type
- Device Type Definition Path
- Product Family
- Direct Cluster
- Base / Inherited Cluster
- Source Sets
- Implementation Rule
- Documentation Rule
- Example Rule
- Support Definition
- Related Device Type
- Inclusion / Exclusion Policy
- Product-specific Exception

따라서 다음 구조로 관리한다.

```text
Tier Declaration
        ↓
Scope Generator
        ↓
scope draft
        ↓
검토
        ↓
finalized scope.json
```

---

# 8. Scope Generator

새로운 Script를 추가한다.

```text
scripts/corpus/generate_scope.py
```

주요 역할:

1. Tier Declaration 읽기
2. Device Type ID → Device Type XML 찾기
3. Device Type XML 파싱
4. Direct Cluster 추출
5. Base / Inherited Cluster 추적
6. Related Device Type 정책 적용
7. Definition Path 결정
8. Source Rule 적용
9. Implementation Rule 적용
10. Example Rule 적용
11. Support Definition 적용
12. Product-specific Override 적용
13. `scope draft` 생성

최종 `scope.json`은 Generator 결과를 그대로 확정하지 않는다.

사람 또는 명시적인 정책 검토를 통과한 후 finalized 상태가 된다.

---

# 9. Product-specific Override

모든 Device Type을 하나의 규칙만으로 처리할 수 있다고 가정하지 않는다.

제품별 예외는 Python 코드 내부의 조건문으로 흩어놓지 않고 별도 정책으로 관리한다.

대표적인 예외:

```text
Refrigerator
└── Temperature Controlled Cabinet

Cooktop
└── Cook Surface
```

그 외 다음 항목도 명시적인 예외 대상이 될 수 있다.

- Parent / Child Device Type
- Support Definition
- Documentation 부재
- Example 부재
- Implementation 경로 예외
- 특정 Cluster 제외
- Feature / Requirement 조건
- Context-only Source

예외는 Tier Config 또는 공통 Override Config에 기록한다.

---

# 10. Coverage Matrix 역할

`coverage_matrix.csv`는 Extraction 결과물이 아니라 **Extraction의 확정 입력**이다.

Coverage에는 단순히 파일이 존재하는지 여부뿐 아니라 다음 검토 결정이 포함된다.

- `include`
- `exclude`
- `present`
- `missing`
- `not_applicable`
- requirement
- feature condition
- evidence 위치
- 예외 승인
- Source Role

따라서 Corpus 생성 Flow는 다음과 같다.

```text
Tier Declaration
        ↓
Device Type XML 분석
        ↓
scope draft
        ↓
coverage draft
        ↓
사람 또는 명시적 정책 검토
        ↓
include / exclude 확정
missing / not_applicable 확정
condition / requirement 검토
evidence 검토
exception 승인
        ↓
finalized scope.json
finalized coverage_matrix.csv
        ↓
Extraction
```

중요한 원칙:

> `extract_corpus.py`는 finalized `scope.json` 또는 `coverage_matrix.csv`를 암묵적으로 수정하지 않는다.

Extraction 과정에서 문제가 발견되면 다음과 같이 처리한다.

```text
Extraction
    ↓
Validation Error / Warning
    ↓
Scope / Coverage Review로 복귀
    ↓
명시적 수정
    ↓
새 Finalized Input으로 재실행
```

---

# 11. Tier별 완전 격리

C3, C6, C12의 산출물은 서로 완전히 분리한다.

```text
corpus/
├── README.md
├── corpus-plan.md
├── improvement.md
│
├── configs/
│   ├── c3.json
│   ├── c6.json
│   └── c12.json
│
└── tiers/
    ├── c3/
    │   ├── scope.json
    │   ├── coverage_matrix.csv
    │   │
    │   ├── raw/
    │   │
    │   ├── processed/
    │   │   └── documents.jsonl
    │   │
    │   └── metadata/
    │       ├── snapshot.json
    │       ├── corpus_manifest.csv
    │       ├── relations.jsonl
    │       ├── entities.jsonl
    │       ├── statistics.json
    │       ├── validation_report.json
    │       ├── source_licensing.json
    │       └── freeze_gate.json
    │
    ├── c6/
    │   └── ...
    │
    └── c12/
        └── ...
```

C3/C6/C12가 다음 항목을 공유하지 않는다.

- `raw/`
- `processed/`
- `metadata/`
- `snapshot.json`
- `manifest`
- `relations`
- `entities`
- validation 결과

이렇게 하여 한 Tier를 재생성하더라도 다른 Tier가 덮어써지지 않게 한다.

---

# 12. snapshot.json

`snapshot.json`은 Extraction 입력이 아니다.

다음 확정 입력과 Pipeline 정보로부터 생성되는 **Metadata Output**이다.

```text
finalized scope
+
finalized coverage
+
SSOT
+
pipeline information
+
extraction result
        ↓
metadata/snapshot.json
```

위치는 항상 다음으로 통일한다.

```text
tiers/<tier>/metadata/snapshot.json
```

예:

```text
tiers/c3/metadata/snapshot.json
tiers/c6/metadata/snapshot.json
tiers/c12/metadata/snapshot.json
```

Tier마다 Scope와 Coverage가 다르므로 하나의 공통 Snapshot을 사용하지 않는다.

Snapshot의 Source Root는 절대 로컬 경로가 아니라 논리적 규칙으로 기록한다.

## 12.1 Deterministic Reproduction 정책

동일한 SSOT Commit, 동일한 finalized Scope, 동일한 finalized Coverage, 동일한 Pipeline Version 및 동일한 설정으로 Corpus를 생성했을 때 결정적 산출물은 동일해야 한다.

따라서 Corpus의 결정적 Metadata에는 wall-clock timestamp를 포함하지 않는다.

다음 파일은 Deterministic Artifact로 취급한다.

```text
scope.json
coverage_matrix.csv
processed/documents.jsonl
metadata/entities.jsonl
metadata/relations.jsonl
metadata/corpus_manifest.csv
metadata/statistics.json
metadata/snapshot.json
metadata/validation_report.json
```

위 파일의 Identity 또는 Reproducibility Fingerprint에는 다음 값을 포함하지 않는다.

```text
현재 시각
generated_at
validation 실행 시각
로컬 파일 생성 시각
machine-specific absolute path
```

실행 시각과 같은 운영 정보가 필요하면 Corpus Artifact와 분리된 Run Log에만 기록한다.

```text
runs/
└── <run-id>/
    └── run_log.json
```

Run Log의 `run-id`, timestamp, 실행 시간 및 machine 정보는 Corpus의 결정적 재현성 판정 대상이 아니다.

동일 입력으로 Corpus를 재생성했을 때 Corpus Semantic Content, Stable Metadata 및 Reproducibility Fingerprint가 동일해야 한다.

---

# 13. Extraction Script 일반화

현재 `extract_corpus.py`는 고정 Corpus Root 대신 실행 시 Tier Root를 전달받도록 변경한다.

예:

```bash
python scripts/corpus/extract_corpus.py \
  --corpus-root corpus/tiers/c3
```

```bash
python scripts/corpus/extract_corpus.py \
  --corpus-root corpus/tiers/c6
```

```bash
python scripts/corpus/extract_corpus.py \
  --corpus-root corpus/tiers/c12
```

각 Corpus Root 내부의 확정 입력:

```text
scope.json
coverage_matrix.csv
```

을 사용하여 해당 Tier의:

```text
raw/
processed/
metadata/
```

를 생성한다.

---

# 14. C3 전용 Hardcoding 제거

현재 Pipeline에 존재하는 C3 전용 상수를 generic Pipeline에서 제거한다.

대상 예:

- Device Type 4개
- Unique Cluster 23개
- Device–Cluster Relation 개수
- C3 Document 예상 개수
- C3 Relation 예상 개수
- 고정 Snapshot Namespace
- 고정 Corpus Version
- 특정 Product 목록

다음과 같은 코드는 generic Pipeline에서 사용하지 않는다.

```python
EXPECTED_DEVICE_TYPES = 4
EXPECTED_CLUSTERS = 23
```

대신 finalized scope를 기준으로 계산한다.

```python
expected_device_types = len(scope_device_types)
expected_clusters = len(scope_clusters)
```

단, 기존 C3 수치는 **Regression Fixture**로 유지할 수 있다.

즉 다음 두 검증을 분리한다.

```text
Generic Validation
C3 Regression Validation
```

---

# 15. Metadata Binding 정책

모든 Document가 반드시 Device Type과 Cluster Binding을 동시에 가져야 하는 것은 아니다.

문서는 역할에 따라 다음과 같이 구분한다.

## 15.1 Direct Evidence Document

제품 또는 Cluster의 직접 근거로 포함된 문서는 다음 중 최소 하나의 Binding을 가진다.

```text
device_types
clusters
```

## 15.2 Context-only Document

다음과 같은 공통 문서는 Device Type / Cluster Binding이 없을 수 있다.

- Support Definition
- Shared Type Definition
- Common Reference
- Context-only Source

이 경우 반드시 포함 이유가 명시되어야 한다.

예:

```text
definition_kind
source_role
included_reason
```

Binding이 없다는 이유만으로 자동 Validation Failure로 처리하지 않는다.

---

# 16. Document 포함 관계

Tier 포함 관계는 전체 JSON Record 비교가 아니라 안정적인 항목을 기준으로 검사한다.

## Source Identity

```text
C3 source_path / document_id
⊆
C6
⊆
C12
```

## Raw Content

C3에 존재하는 동일 Source가 C6/C12에도 존재할 경우 다음 값이 동일해야 한다.

```text
raw bytes
content_hash
```

## Normalized Content

동일 Source의 다음 값도 유지되어야 한다.

```text
normalized text
normalized_hash
source_spans
```

---

# 17. Association 포함 관계

상위 Tier에서 하나의 Document가 새로운 Device Type 또는 Cluster와 추가로 연결될 수 있다.

따라서 전체 Metadata Equality를 요구하지 않는다.

대신 기존 Association이 삭제되지 않는지 검사한다.

```text
C3 document.device_types
⊆
C6 corresponding document.device_types
⊆
C12 corresponding document.device_types
```

동일하게:

```text
C3 document.clusters
⊆
C6 corresponding document.clusters
⊆
C12 corresponding document.clusters
```

기존 Association은 이유 없이 제거되어서는 안 된다.

---

# 18. Relation 포함 관계

`relation_id` 자체를 Tier 포함 관계의 Identity로 사용하지 않는다.

Tier가 확장되면서 `via_entities`, snapshot 관련 정보 또는 기타 비의미적 Metadata가 변경될 수 있으므로, 의미상 동일한 Relation인지 판단하기 위한 별도의 Stable Semantic Key를 사용한다.

## 18.1 Semantic Identity Contract

Relation의 Semantic Identity에는 다음 필드를 포함한다.

```text
relation_type
source_entity
target_entity
document_id
role
requirement
requirement_raw
condition
assertion_scope
```

다음 필드는 Semantic Identity에 포함하지 않는다.

```text
relation_id
snapshot_id
via_entities
generated_at
pipeline_version
run-specific metadata
```

`source_entity`, `target_entity`, `condition` 등은 객체일 수 있으므로 Python tuple에 객체를 그대로 넣지 않는다. Semantic Identity 대상 필드만 추출한 후 정렬된 Canonical JSON으로 직렬화한다.

```python
import json


def canonical_json(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def relation_semantic_key(relation):
    semantic = {
        "relation_type": relation["relation_type"],
        "source_entity": relation["source_entity"],
        "target_entity": relation["target_entity"],
        "document_id": relation["document_id"],
        "role": relation.get("role"),
        "requirement": relation.get("requirement"),
        "requirement_raw": relation.get("requirement_raw"),
        "condition": relation.get("condition"),
        "assertion_scope": relation.get("assertion_scope"),
    }
    return canonical_json(semantic)
```

Canonical Serialization 규칙 자체도 Pipeline Contract로 고정한다.

최소 조건:

```text
UTF-8
JSON object key 정렬
불필요한 whitespace 제거
동일한 null 표현
동일한 boolean / number serialization
```

Tier 포함 관계는 다음 Semantic Key Set을 기준으로 검증한다.

```text
semantic_relations(C3)
⊆
semantic_relations(C6)
⊆
semantic_relations(C12)
```

`via_entities`가 상위 Tier에서 증가하더라도 핵심 Assertion이 동일하면 동일한 Semantic Relation으로 판단한다. 반면 `role`, `requirement`, `condition`, `assertion_scope`처럼 의미 자체를 변경하는 값이 달라지면 서로 다른 Relation으로 판단한다.

장기적으로 Relation을 Atomic Assertion으로 재설계할 수 있지만, 이번 Corpus 확장에서는 기존 구조 변경을 최소화하기 위해 Stable Semantic Key 방식으로 구현한다.

---

# 19. Entities / Relations / Documents 계약

Corpus의 Downstream 계약을 `documents.jsonl` 하나로 한정하지 않는다.

각 Tier는 반드시 다음 세 가지 구조를 생성한다.

```text
processed/documents.jsonl

metadata/entities.jsonl

metadata/relations.jsonl
```

동일 Tier의 세 파일은 동일한 Scope와 Snapshot에서 생성되어야 한다.

---

# 20. C3 Regression Validation

Pipeline Generalization 이후 새로운 Generic Pipeline으로 C3를 다시 생성한다.

이때 모든 Hash가 기존 C3와 동일해야 하는 것은 아니다.

## 20.1 반드시 유지되어야 하는 Stable Invariants

다음 항목은 기존 C3 Baseline과 동일해야 한다.

- `document_id`
- `source_path`
- Raw Source Bytes
- `content_hash`
- Normalized Text
- `normalized_hash`
- `source_spans`
- Semantic Entity Identity
- Semantic Relation Assertion
- 기존 Source Set

## 20.2 변경되어도 정상인 값

다음 값은 Pipeline 변경으로 인해 달라질 수 있다.

- `pipeline_hash`
- `snapshot_id`
- `snapshot.json` 자체 Hash
- Pipeline Version

따라서 Regression Failure는 Stable Invariant에 차이가 발생했을 때만 판정한다.

기존 Pipeline 산출물에 timestamp가 포함되어 있었다면 Pipeline Generalization 과정에서 결정적 Artifact에서 제거한다. Legacy Timestamp 차이는 최초 Migration 비교에서만 허용할 수 있으며, 새 Generic Pipeline으로 생성된 Artifact에는 timestamp가 결정적 Metadata로 존재해서는 안 된다.

---

# 21. Expected Count 정책

C6/C12의 최종 파일 개수나 Relation 개수를 사전에 하드코딩하지 않는다.

다음은 실제 Build 결과로 계산한다.

- Document Count
- Entity Count
- Relation Count
- Source Role Distribution
- Document Type Distribution
- Product별 Source Count
- Token Count

반면 다음처럼 Scope 자체에서 결정되는 값은 Scope 기준으로 검증할 수 있다.

- Device Type 수
- Direct Cluster 수
- Unique Cluster 수
- Device–Cluster Requirement 수

즉:

```text
Scope-derived expectation
```

과

```text
Extraction-derived statistics
```

를 분리한다.

---

# 22. Metadata Compatibility

기존 Metadata 계약의 파일명을 유지한다.

새로운 `licensing_report.json` 등으로 변경하지 않는다.

각 Tier에서 기존 파일을 그대로 사용한다.

```text
metadata/source_licensing.json
metadata/freeze_gate.json
```

따라서:

```text
tiers/c3/metadata/source_licensing.json
tiers/c3/metadata/freeze_gate.json

tiers/c6/metadata/source_licensing.json
tiers/c6/metadata/freeze_gate.json

tiers/c12/metadata/source_licensing.json
tiers/c12/metadata/freeze_gate.json
```

형태로 관리한다.

Downstream Code가 기존 Metadata 계약을 그대로 사용할 수 있도록 파일 이름과 역할을 유지한다.

---

# 23. Readiness / Freeze Gate

Readiness의 공식 계약은 기존과 동일하게 다음 파일을 사용한다.

```text
metadata/freeze_gate.json
```

기존 Consumer와의 호환성을 유지하기 위해 기존 필드를 삭제하거나 이름을 변경하지 않는다.

기존 핵심 필드:

```text
ready_for_freeze
licensing_review
cross_review
blocking_checks
```

`build_ready`, `distribution_ready`와 같은 추가 상태가 필요하면 기존 Schema를 대체하지 않고 Additive Field로만 추가한다.

```json
{
  "ready_for_freeze": false,
  "licensing_review": "needs_review",
  "cross_review": "pending",
  "blocking_checks": [
    "licensing_review",
    "cross_review"
  ],
  "build_ready": true,
  "distribution_ready": false
}
```

기존 Consumer는 기존 필드만 읽어도 정상 동작해야 한다. 새 Consumer는 필요할 경우 `build_ready`, `distribution_ready` 필드를 추가로 사용할 수 있다.

## build_ready

Corpus 생성 및 기술 검증이 완료된 상태다.

조건:

- finalized scope
- finalized coverage
- extraction 성공
- normalization 성공
- manifest 생성
- entities / relations 생성
- source traceability 및 hash 검증 통과
- validation 통과
- reproducibility 통과
- Tier inclusion validation 통과

## distribution_ready

외부 배포 또는 Freeze가 가능한 상태다.

```text
build_ready
+
licensing_review 완료
+
cross_review 완료
```

최종 Freeze 판단에서는 기존 공식 필드인 `ready_for_freeze`를 계속 유지한다. 새 필드는 기존 Freeze 계약을 대체하지 않고 상태를 세분화하기 위한 보조 정보로 사용한다.

---

# 24. Licensing

C6/C12는 C3에 존재하지 않던 새로운 Source를 추가하므로 Tier별로 Source Licensing 결과를 다시 생성한다.

```text
metadata/source_licensing.json
```

을 각 Tier가 별도로 가진다.

C3의 Licensing 결과를 C6/C12에 그대로 복사해서는 안 된다.

각 Tier의 실제 Manifest를 기준으로 Licensing Coverage를 확인한다.

---

# 25. .gitignore 정책

기존 `corpus/.gitignore` 정책을 유지한다.

기존 규칙을 제거하고 단순히 다음과 같이 교체하지 않는다.

```text
/corpus/raw/
/corpus/processed/
```

대신 Tier 구조를 지원하도록 기존 정책을 확장한다.

예:

```gitignore
# ==================================================
# Tier-generated source payload
# ==================================================

/tiers/*/raw/**
!/tiers/*/raw/README.md


# ==================================================
# Tier-generated normalized payload
# ==================================================

/tiers/*/processed/**
!/tiers/*/processed/README.md


# ==================================================
# Derived artifacts that may contain source excerpts
# ==================================================

/tiers/*/metadata/relations.jsonl
/tiers/*/metadata/entities.jsonl
```

단, 기존 `.gitignore`의 README 또는 Placeholder 보존 규칙이 있다면 해당 정책을 우선 유지한다.

Git에서 관리할 대상:

```text
configs/*.json

tiers/*/scope.json
tiers/*/coverage_matrix.csv

tiers/*/metadata/snapshot.json
tiers/*/metadata/corpus_manifest.csv
tiers/*/metadata/statistics.json
tiers/*/metadata/validation_report.json
tiers/*/metadata/source_licensing.json
tiers/*/metadata/freeze_gate.json

scripts/corpus/*
corpus-plan.md
improvement.md
README.md
```

즉 Git에는 다음을 남긴다.

```text
Scope
Version
Rule
Manifest
Statistics
Validation
Licensing State
Freeze State
Reproduction Script
```

반면 재생성 가능한 원문 Payload 또는 원문 일부가 포함될 수 있는 대용량 Derived Artifact는 제외한다.

connectedhomeip는 sibling Repository가 원칙이므로 정상적인 환경에서는 프로젝트 `.gitignore`의 대상이 아니다.

다만 실수로 프로젝트 Root 내부에 Clone하는 것을 방지하려면 프로젝트 Root `.gitignore`에 방어적으로 다음을 둘 수 있다.

```gitignore
# connectedhomeip should normally be a sibling repository.
/connectedhomeip/
```

이 규칙은 connectedhomeip를 프로젝트 내부에 둘 것을 의미하지 않는다.

---

# 26. 구현 단계

## Phase 0 — C3 Baseline 보존

현재 정상 동작하는 C3를 기준선으로 보존한다.

작업:

1. 현재 C3 Build 결과 기록
2. 현재 Manifest 보존
3. Statistics 보존
4. Stable Source / Hash 정보 보존
5. 기존 13개 Test 통과 확인
6. C3 Regression Fixture 생성

---

## Phase 1 — Pipeline Generalization

C6/C12 확장 전에 파이프라인을 일반화한다.

작업:

1. Tier Declaration Schema 정의
2. Scope Generator 구현
3. Device Type XML Parser 구현
4. Direct Cluster 자동 추출
5. Base / Inherited Cluster 관계 생성
6. Related Device Type Policy 구현
7. Product Override 외부화
8. `corpus_root` Parameter 도입
9. C3 전용 Hardcoded Count 제거
10. Generic Validation 구현
11. Semantic Relation Key 구현
12. Tier별 Metadata Output 지원
13. Tier별 Snapshot 생성 지원

---

## Phase 2 — C3 Regression

Generic Pipeline으로 C3를 다시 생성한다.

Flow:

```text
c3 declaration
    ↓
scope draft
    ↓
coverage draft
    ↓
review
    ↓
finalized scope / coverage
    ↓
extraction
    ↓
validation
```

검증:

- Stable Document Identity 동일
- Raw Bytes 동일
- `content_hash` 동일
- `normalized_hash` 동일
- `source_spans` 동일
- Semantic Relation Assertion 동일
- 기존 Test 13개 통과

다음 값의 변경은 허용한다.

- `pipeline_hash`
- `snapshot_id`
- Snapshot Hash
- Timestamp
- Pipeline Version

C3 Regression이 통과한 뒤에만 C6로 진행한다.

---

## Phase 3 — C6 구축

추가 대상:

```text
Air Purifier
Robotic Vacuum Cleaner
Dishwasher
```

Flow:

```text
C6 declaration
        ↓
scope draft
        ↓
coverage draft
        ↓
manual / policy review
        ↓
finalized scope.json
finalized coverage_matrix.csv
        ↓
extraction
        ↓
normalization
        ↓
entities
        ↓
relations
        ↓
validation
        ↓
snapshot
        ↓
statistics
        ↓
licensing
        ↓
freeze gate
```

추가 검증:

```text
C3 source ⊆ C6 source

C3 stable hashes 보존

C3 association ⊆ C6 association

C3 semantic relation
⊆
C6 semantic relation
```

---

## Phase 4 — C12 구축

추가 대상:

```text
Laundry Dryer
Humidity Conditioner
Microwave Oven
Cooktop / Cook Surface
Extractor Hood
Water Heater
```

C6와 동일한 절차를 적용한다.

추가 검증:

```text
C6 source ⊆ C12 source

C6 stable hashes 보존

C6 association ⊆ C12 association

C6 semantic relation
⊆
C12 semantic relation
```

---

# 27. 최종 Tier 관계 검증

최종적으로 다음 관계를 확인한다.

## Source

```text
C3
⊆
C6
⊆
C12
```

## Raw / Normalized Content

기존 Source에 대해:

```text
content_hash(C3)
=
content_hash(C6)
=
content_hash(C12)
```

및:

```text
normalized_hash(C3)
=
normalized_hash(C6)
=
normalized_hash(C12)
```

## Association

```text
associations(C3)
⊆
associations(C6)
⊆
associations(C12)
```

## Semantic Relations

```text
semantic_relations(C3)
⊆
semantic_relations(C6)
⊆
semantic_relations(C12)
```

## Strict Expansion

다음 차집합이 모두 비어 있지 않은지 확인한다.

```text
sources(C6) - sources(C3) ≠ ∅
sources(C12) - sources(C6) ≠ ∅
```

이 검증까지 통과한 경우 최종적으로 `C3 ⊂ C6 ⊂ C12`를 선언한다.

---

# 28. 완료 조건

## Pipeline Generalization

- [ ] Tier Declaration Schema가 정의되었다.
- [ ] Scope Generator가 구현되었다.
- [ ] Device Type XML Parser가 구현되었다.
- [ ] Direct Cluster 관계를 자동 생성한다.
- [ ] Base / Inherited Cluster 관계를 처리한다.
- [ ] Product-specific Override가 외부 설정으로 분리되었다.
- [ ] `corpus_root` Parameter를 지원한다.
- [ ] C3 전용 Hardcoded Count가 Generic Code에서 제거되었다.
- [ ] Generic Validation이 구현되었다.
- [ ] Stable Semantic Relation Key가 구현되었다.
- [ ] Canonical JSON Serialization 계약이 고정되었다.
- [ ] Tier별 Snapshot 생성이 가능하다.
- [ ] 결정적 Artifact에 wall-clock timestamp가 포함되지 않는다.
- [ ] Run Log가 결정적 Artifact와 분리되었다.

## C3

- [ ] 기존 C3 Baseline이 보존되었다.
- [ ] Generic Pipeline으로 C3를 재생성했다.
- [ ] Stable Invariant Regression을 통과했다.
- [ ] 기존 Test 13개를 다시 통과했다.

## C6

- [ ] Scope Draft를 생성했다.
- [ ] Coverage Draft를 생성했다.
- [ ] Scope / Coverage Review를 완료했다.
- [ ] Scope / Coverage를 Finalize했다.
- [ ] Corpus Extraction을 완료했다.
- [ ] `documents.jsonl`을 생성했다.
- [ ] `entities.jsonl`을 생성했다.
- [ ] `relations.jsonl`을 생성했다.
- [ ] Validation을 통과했다.
- [ ] C3 → C6 포함 관계를 검증했다.

## C12

- [ ] Scope Draft를 생성했다.
- [ ] Coverage Draft를 생성했다.
- [ ] Scope / Coverage Review를 완료했다.
- [ ] Scope / Coverage를 Finalize했다.
- [ ] Corpus Extraction을 완료했다.
- [ ] `documents.jsonl`을 생성했다.
- [ ] `entities.jsonl`을 생성했다.
- [ ] `relations.jsonl`을 생성했다.
- [ ] Validation을 통과했다.
- [ ] C6 → C12 포함 관계를 검증했다.

## Metadata / Reproducibility

- [ ] 각 Tier에 `metadata/snapshot.json`이 생성되었다.
- [ ] 각 Tier에 `corpus_manifest.csv`가 생성되었다.
- [ ] 각 Tier에 `statistics.json`이 생성되었다.
- [ ] 각 Tier에 `validation_report.json`이 생성되었다.
- [ ] Snapshot에 절대 로컬 경로가 포함되지 않는다.
- [ ] `CONNECTEDHOMEIP_PATH` 또는 sibling layout으로 Source를 찾을 수 있다.
- [ ] 동일 Commit과 동일 Finalized Input으로 Corpus를 재생성할 수 있다.

## Git

- [ ] 기존 `corpus/.gitignore` 정책을 유지한다.
- [ ] `tiers/*/raw` Payload가 Git에서 제외된다.
- [ ] `tiers/*/processed` Payload가 Git에서 제외된다.
- [ ] Tier별 raw/processed README Placeholder가 Git에 유지된다.
- [ ] Source Excerpt를 포함할 수 있는 Derived Artifact가 정책에 따라 제외된다.
- [ ] Scope / Coverage / Snapshot / Manifest / Statistics / Validation은 추적된다.
- [ ] connectedhomeip는 sibling Repository 구조를 유지한다.

## Readiness

- [ ] Tier별 `source_licensing.json`이 존재한다.
- [ ] Tier별 `freeze_gate.json`이 존재한다.
- [ ] `build_ready` 상태가 판정된다.
- [ ] 기존 Freeze Gate 필드가 유지되고 새 Readiness 필드는 additive하게 추가된다.
- [ ] Licensing Review가 완료된다.
- [ ] Cross Review가 완료된다.
- [ ] `distribution_ready` 상태가 판정된다.

---

# 29. 최종 목표 구조

최종 Corpus Build Flow는 다음과 같다.

```text
                 Tier Declaration
                        │
                        ▼
                Device Type XML
                        │
                        ▼
                  Scope Draft
                        │
                        ▼
                Coverage Draft
                        │
                        ▼
                 Review / Policy
                        │
                        ▼
          Finalized Scope + Coverage
                        │
                        ▼
                    Extraction
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
        Documents    Entities    Relations
            │           │           │
            └───────────┼───────────┘
                        ▼
                    Validation
                        │
                        ▼
                     Snapshot
                        │
                        ▼
             Statistics / Licensing
                        │
                        ▼
                   Freeze Gate
```

이를 C3, C6, C12에 동일하게 적용한다.

```text
C3
└── Generic Pipeline

C6
└── Same Generic Pipeline

C12
└── Same Generic Pipeline
```

최종적으로 제품군 규모만 달라지고 Corpus 생성 원칙과 Pipeline 계약은 동일한 구조를 목표로 한다.

---

# 30. 구현 현황

2026-09-25 기준으로 Phase 0과 Phase 1의 기반 구현을 시작했다.

완료:

- C3/C6/C12 Tier Declaration 추가
- Tier 이름, declaration 경로, output root, SSOT commit, data-model 경로를 `configs/tiers.json` registry로 외부화
- 공통 base cluster와 related Device Type, C3 Cooler-only 예외를 외부 override로 분리
- Device Type XML 기반 deterministic `scope_draft.json` 생성기 추가
- `generate_scope.py --all`로 registry의 모든 Tier 초안 일괄 생성 지원
- 모든 scope draft를 `extraction_authorized=false`로 생성
- C3 전용 Device Type/Cluster/관계 개수 하드코딩을 generic validation에서 제거
- scope 기반 snapshot namespace와 corpus version 지원
- `--corpus-root` 기반 Tier 실행 인터페이스 추가
- Canonical JSON 기반 Relation Semantic Key 구현
- Source/Hash/Association/Semantic Relation Tier 비교 도구 추가
- finalized 입력 존재 여부를 확인하는 전체 Tier status/build orchestration 추가
- Tier payload `.gitignore`와 README placeholder 구조 추가
- 기존 C3 dry-run 결과 282 documents / 764 relations / 23 clusters 유지 확인
- Corpus pipeline test 15개 통과

아직 완료되지 않음:

- C6/C12 cluster source, implementation, documentation, example mapping 확정
- C6/C12 coverage draft 생성 및 검토
- Tier별 finalized `scope.json` / `coverage_matrix.csv`
- C3 legacy layout의 tier layout migration 검토
- C6/C12 실제 extraction과 inclusion report 생성
- Tier별 licensing review와 freeze gate 갱신

생성된 `scope_draft.json`은 upstream Device Type 관계를 확인하기 위한 초안이며, 검토되지 않은 상태에서는 Corpus extraction 입력으로 사용하지 않는다.

---

# 31. 구현 완료 결과 (2026-09-25)

사용자 승인에 따라 C3, C6, C12의 `scope.json`과 `coverage_matrix.csv`를 확정하고 실제 빌드를 완료했다.

| Tier | Documents | Relations | Unique Clusters | Validation | Deterministic rebuild |
|---|---:|---:|---:|---|---|
| C3 | 282 | 764 | 23 | 오류 0건 | pass |
| C6 | 317 | 1,059 | 29 | 오류 0건 | pass |
| C12 | 369 | 1,633 | 36 | 오류 0건 | pass |

추가 완료 사항:

- C3 → C6, C6 → C12 source inclusion 검증 통과
- 동일 source의 raw content hash 보존 검증 통과
- document association 및 semantic relation inclusion 검증 통과
- scope 확장으로 인접 source span이 병합되는 structured document는 하위 span의 완전 포함 여부로 검증
- 15개 pipeline regression test 통과
- 각 Tier의 snapshot, manifest, statistics, validation report 생성 완료

현재 corpus build와 재현성 검증은 완료됐다. 다만 기존 정책과 동일하게 licensing review, cross review, tokenizer/model 결정은 자동 승인하지 않았으며 formal `freeze_gate.json`의 build/distribution readiness 판정과 분리한다.
