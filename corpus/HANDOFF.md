# Corpus Handoff

현재 전달본은 **Corpus v0.1 / v1.0 candidate**다. 기술 검증은 통과했지만
`licensing_review=needs_review`, `cross_review=pending`이므로 frozen v1.0이나 공개 재배포 승인본이 아니다.
최종 상태는 [freeze_gate.json](metadata/freeze_gate.json)을 기준으로 판단한다.

## 공통 입력

- `processed/documents.jsonl`: RAG와 LLM Wiki가 함께 사용하는 282개 정규화 문서
- `metadata/corpus_manifest.csv`: 282개 원본의 ID·경로·SHA-256·역할·revision
- `metadata/entities.jsonl`: 관계 target을 식별하는 Entity
- `metadata/relations.jsonl`: 764개 Device Type/Cluster/정의/구현 관계와 evidence
- `metadata/scope.json`, `coverage_matrix.csv`: 범위와 결손의 최종 기준
- `metadata/snapshot.json`: SSOT와 snapshot 식별자

SSOT는 `connectedhomeip`의 `master`에서 관찰한 commit
`1ac132b5ecd42cb6c78772f2576ed6f7fc814183`이다. branch 최신 상태가 아니라 이 commit을 사용한다.
범위는 3개 제품군, 4개 Device Type ID, 23개 고유 Cluster다.

## documents.jsonl 읽기

각 줄은 한 물리 원본에 대응하는 JSON 객체다. `document_id`, `snapshot_id`, `text`, `metadata`,
`source_spans[]`가 핵심이다. `source_role`과 `definition_kind`는 별개 축이며, 서로 다른 출처의
revision을 합치지 않는다. `source_spans`의 문자 offset은 LF로 통일한 Unicode code point 기준,
끝 미포함이다. `text`는 검색 chunk나 요약이 아니라 선택된 원문 구간이다.

## relations.jsonl 읽기

`relation_id`, `relation_type`, `source_entity`, `target_entity`, `document_id`, `role`,
`requirement`, `condition`, `assertion_scope`, `evidence`를 함께 읽는다. 같은 구현 파일을 여러
Device Type이 공유하면 파일을 복제하지 않고 하나의 `document_id`에 여러 relation을 연결한다.
optional/conditional 관계를 실제 기능 활성화로 해석하지 않는다.

764개 relation의 primary document는 모두 Corpus에 있다. 다만 Base 적용 근거 4건은
`upstream_reference_only`이며 `document_id=null`이다. 고정 checkout의
`src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py:1963`을 참조하므로
재생성·검증 시 해당 checkout이 필요하다.

## 변경과 재생성

Windows PowerShell에서 `connectedhomeip`와 project를 같은 workspace 아래에 별도로 clone한다.
project 디렉터리에서 다음과 같이 고정 commit을 checkout하고 절대 경로 환경변수를 설정한 뒤,
단일 build 명령을 실행한다.

```powershell
git -C ..\connectedhomeip checkout 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
$env:CONNECTEDHOMEIP_PATH = (Resolve-Path "..\connectedhomeip").Path
python scripts/corpus/build.py
```

`build.py`는 외부 checkout을 수정하지 않는다. 환경변수/경로, Git 저장소, clean 상태와 고정 HEAD,
`scope.json`을 확인한 뒤 기존 extraction/normalization/validation 구현을 호출한다. 정상 결과는 raw 282개,
normalized document 282개, relation 764개, 고유 cluster 23개, validation failure 0개다.

기존 산출물만 검증하려면 같은 환경변수를 유지한 상태에서 다음을 실행한다.

```powershell
python scripts/corpus/extract_corpus.py --source-repo $env:CONNECTEDHOMEIP_PATH --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --validate-only
python -m unittest discover -s scripts/corpus/tests -v
```

전체 재생성 명령은 [scripts/corpus/README.md](../scripts/corpus/README.md)에 있다. downstream 담당자는
raw, normalized text, ID, relation, scope를 직접 수정하지 않는다. 변경이 필요하면 Corpus 담당자에게
변경 이유, 대상 `document_id`/relation, 예상 scope 영향과 근거를 전달해 새 snapshot/version 검토를 요청한다.

## 보장과 비보장

Corpus 담당자는 고정 snapshot, scope, provenance, metadata, raw 무결성, identifier 보존과 결정적
재생성을 보장한다. RAG chunking·embedding·indexing·retrieval, Wiki 구조·컴파일·context 적합성,
답변 정확도와 benchmark 결과는 보장하지 않는다. 허용된 missing 21개는 추출 실패가 아니며,
상세 분류는 [missing_analysis.md](research/missing_analysis.md)에 있다.

전체 payload의 공개·재배포는 승인되지 않았다. 사용·공유 전
[licensing_review.md](research/licensing_review.md)와 [PUBLISHING.md](PUBLISHING.md)를 확인한다.
