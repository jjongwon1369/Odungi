# Matter / connectedhomeip Corpus

> **Corpus Version:** 0.1 (`1.0 candidate`)
>
> **SSOT Commit:** `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
>
> **Product Families:** 3
>
> **Device Types:** 4
>
> **Unique Clusters:** 23
>
> **Documents:** 282 raw / 282 normalized
>
> **Relations:** 764
>
> **Freeze Status:** blocked — `ready_for_freeze=false`

## Overview

Matter `connectedhomeip`의 고정 snapshot에서 만든 A/B/C 공통 입력 Corpus다. 단일 RAG,
분해형 RAG, LLM Wiki가 서로 다른 원본을 사용하지 않도록 **동일한 원본을 고정하고 처리 방식만
다르게 한다**. 현재 데이터는 기술 검증을 통과했지만 이용 조건과 실제 팀 교차검토가 끝나지 않아
공식 Corpus v1.0이 아니라 **v1.0 candidate**다.

상세 설명은 [CORPUS_V1.md](CORPUS_V1.md), 공개·재배포 경계는
[PUBLISHING.md](PUBLISHING.md), 데이터셋 요약은 [DATASET_CARD.md](DATASET_CARD.md)를 참고한다.

## Scope

- Laundry Washer (`0x0073`)
- Room Air Conditioner (`0x0072`)
- Refrigerator (`0x0070`)
- Temperature Controlled Cabinet (`0x0071`, Refrigerator 보조 범위, Cooler-only)

이는 3개 제품군, 4개 Device Type ID, 23개 고유 Cluster다. 확정 범위는
[corpus_scope.md](corpus_scope.md)와 [scope.json](metadata/scope.json)이 결정한다.

## Dataset Summary

| 항목 | 값 |
|---|---:|
| Raw files | 282 |
| Normalized documents | 282 |
| Relations | 764 |
| Entities | 342 |
| Unique clusters | 23 |
| Raw bytes | 3,884,956 |
| Normalized characters | 2,144,062 |

제품별 관련 파일 수(Washer 113, Room AC 209, Refrigerator 99, Cabinet 81)는 공유 문서를
각 제품 관계에 연결한 수이므로 합계가 282보다 크다. 물리 원본은 경로별로 한 번만 저장한다.

## Directory Structure

```text
corpus/
├── raw/connectedhomeip/          # 고정 Git blob 원본 282개(로컬 payload)
├── processed/documents.jsonl     # 파일별 정규화 문서 282개(로컬 payload)
├── metadata/                     # scope, manifest, 관계, 통계, 검증, freeze gate
├── research/                     # 범위·결손·revision·라이선스 검토 근거
├── CORPUS_V1.md                  # 상세 사용자/담당자 설명서
├── DATASET_CARD.md               # 데이터셋 카드
├── CHANGELOG.md                  # 버전 변경 기록
├── HANDOFF.md                    # RAG/LLM Wiki 담당자 인계서
└── PUBLISHING.md                 # 공개·재배포 경계
scripts/corpus/                   # 추출·정규화·검증 CLI와 테스트
```

원문 payload 및 원문 발췌를 포함할 수 있는 상세 산출물 일부는 `.gitignore` 정책상 공개 커밋에서
제외될 수 있다. 경로가 문서에 있다는 사실이 공개 저장소에 payload가 포함된다는 뜻은 아니다.

## How to Reproduce

Python 3.10+, Git, 고정 commit의 clean `../connectedhomeip` checkout이 필요하다. 프로젝트 루트에서 실행한다.

```powershell
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --dry-run
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json
python scripts/corpus/extract_corpus.py --source-repo ../connectedhomeip --scope corpus/metadata/scope.json --output corpus/raw --snapshot corpus/metadata/snapshot.json --validate-only
python -m unittest discover -s scripts/corpus/tests -v
```

재생성 전에 [licensing_review.md](research/licensing_review.md)의 이용 조건을 확인해야 한다.
CLI의 정확한 계약과 실패 조건은 [scripts/corpus/README.md](../scripts/corpus/README.md)에 있다.

## Metadata

- [snapshot.json](metadata/snapshot.json): commit, scope/coverage/pipeline hash, snapshot ID
- [corpus_manifest.csv](metadata/corpus_manifest.csv): 원본별 ID, 경로, 역할, revision, SHA-256
- `processed/documents.jsonl`: 정규화 본문, metadata, 원문 위치
- `entities.jsonl`, `relations.jsonl`: Device Type/Cluster/정의/구현 관계와 evidence
- [statistics.json](metadata/statistics.json): 물리 파일과 다중 제품·Cluster 연결 통계
- [coverage_matrix.csv](metadata/coverage_matrix.csv): 포함·결손·제외 감사 뷰

## Validation

2026-09-22 재검증 결과 14 PASS / 3 warning이며 실패는 0이다. raw↔manifest, SHA-256,
문서·관계 ID 중복, source span, identifier 보존, 관계 target, 23/23 Cluster coverage,
source revision, 2회 결정적 재생성이 모두 통과했다. 13개 단위 테스트도 통과했다.

warning은 허용된 coverage gap 21개, revision 의미 정합성 미평가, tokenizer 미결정이다.
자세한 기계 판독 결과는 [validation_report.json](metadata/validation_report.json)에 있다.

## Version

현재 snapshot은 `corpus_version=0.1`, `frozen=false`다. `1.0 candidate` 문서 정리는 데이터 변경이
아니며 `version.json`과 Git tag는 만들지 않았다. 다음 두 blocker가 실제 기록으로 해소된 뒤에만
`ready_for_freeze=true`, `status=frozen`, `corpus_version=1.0`으로 전환할 수 있다.

- `licensing_review=needs_review`
- `cross_review=pending`

권장 tag 이름은 `corpus-v1.0`이지만 사용자가 최종 확인한 뒤 직접 생성해야 한다.

## Handoff

RAG/LLM Wiki 담당자는 [HANDOFF.md](HANDOFF.md)를 먼저 읽고 `documents.jsonl`을 공통 입력으로,
`relations.jsonl`을 관계·provenance 보조 자료로 사용한다. Corpus 수정이 필요하면 downstream에서
조용히 고치지 말고 Corpus 담당자에게 scope/snapshot/version 검토를 요청한다.
