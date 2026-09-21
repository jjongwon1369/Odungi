# Corpus v1.0 Freeze 검토 체크리스트

검토 대상은 [snapshot.json](../metadata/snapshot.json)의 Corpus v0.1이다.
Freeze 준비 검토 자료는 작성했지만 **ready_for_freeze=false**다.
tag 생성·Scope 수정·성능평가를 수행하지 않았다.

| 확인 항목 | 상태 | 근거 |
|---|---|---|
| Scope 확정 | pass | scope.json, coverage_matrix.csv; 기존 Hash 유지; 3개 제품군/4개 ID |
| SSOT 확정 | pass | 고정 commit 1ac132b5ecd42cb6c78772f2576ed6f7fc814183; master; clean checkout |
| Coverage 검토 | pass | 23개 Cluster/42개 제품→Cluster 관계; 포함 59행/제외 감사 32행 |
| missing 사유 검토 | pass | missing_analysis.md; documentation_missing 20, unavailable_source 1 |
| 전체 통계 | pass | freeze_audit.json의 독립 재집계가 statistics.json의 모든 요구 필드와 일치 |
| Source/Revision 기록 | pass | 282개 manifest/metadata 대조; 출처별 artifact/declarations 보존; 오류·성능 판정 없음 |
| Manifest 일치 | pass | 282개 document_id→manifest→raw→source→commit 연결 확인 |
| relations 구조·참조 유효성 | pass | 764개 primary document, Entity 참조 및 evidence Hash/commit/줄 범위 검증 |
| upstream exception review | pass | R005/R008/R011/R014를 external_reference_only로 확정; 고정 checkout 접근 필요. upstream_exceptions.md 참조. 내부 문서 연결로 위장하지 않음 |
| raw hash 검증 | pass | 282개 raw가 고정 Git blob 및 manifest SHA-256과 동일 |
| normalization 검증 | pass | 282개 문서/755개 원본 span; 선택 원문과 전체 본문 문자 대조 |
| Identifier preservation | pass | lexical inventory 191,531회 + 선택 원문 전체 문자 보존 검사; 의미 평가 아님 |
| deterministic rebuild | pass | 독립 2회 및 실제 산출물의 288개 파일 비교 일치 |
| licensing review | needs_review | source별 redistributable 217 / reference_only 31 / needs_review 34; 현재 전체 raw 배포 승인 아님 |
| 팀원 1인 이상 교차검토 | pending | 사용자 응답: 검토 기록 없음. 자동 검사/AI 검토를 팀원 서명으로 대체하지 않음 |

## 남은 Gate 처리

1. **이용 조건:** licensing_review.md의 파일별 조건과 이용·변환·공유 범위를 확인한 담당자,
   적용 권한 문서, 대상 snapshot, 결론을 남긴다. 전체 raw 공개 가능으로 자동 판단하지 않는다.
2. **Provenance 예외:** 4개 Base 적용 근거는 pinned upstream
   `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py:1963`에서 검증 가능하지만
   Corpus document_id가 없다. 2026-09-20 검토에서 external_reference_only로 유지하도록 결정했다.
   임의 파일 추가나 존재하지 않는 document_id 생성 없이, 외부 참조임을 보존하는 검토 항목으로 통과 처리했다.
3. **팀 교차검토:** 최소 1명의 팀원이 이 snapshot과 audit 자료를 검토하고 검토자·대상 snapshot_id·
   점검 항목·결론·근거 링크를 기록한다. 미확인 항목이 있으면 Gate를 계속 보류한다.

기존 validation_report의 warning 3개와 이 Freeze Gate는 목적이 다르다.
missing은 분류·근거 확인 후 허용된 결손으로 유지하며, semantic 평가/tokenizer/Context 적합성은
이번 담당 범위의 통과 조건으로 삼지 않는다. RAG/Wiki 담당자의 시스템 판단을 대신하지 않는다.

최종 기계 판독 상태와 근거 Hash는 [freeze_gate.json](../metadata/freeze_gate.json)에 있다.
입력 snapshot 또는 검토 대상이 변경되면 과거 pass/서명을 재사용하지 말고 해당 항목을 다시 확인한다.

## Reviewer section — 실제 팀원 작성용

현재 상태: **pending**. 템플릿 생성은 교차검토 통과가 아니다.

- Reviewer 이름 / 소속: 미작성
- 검토일: 미작성
- 검토 대상 snapshot_id: 미작성 (metadata/snapshot.json의 값을 그대로 기록)
- SSOT commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- 검토 대상 freeze_gate.json 또는 검토 자료의 Hash: 미작성
- 근거 링크 / 검토 기록 위치: 미작성

| Reviewer 확인 항목 | pass / fail / needs_review | 확인한 경로·document_id·근거 및 의견 |
|---|---|---|
| Scope 이해 가능 여부 | 미작성 | |
| provenance 추적 가능 여부 — 외부 근거 4건의 경계 포함 | 미작성 | |
| Device Type / Cluster 관계 이해 가능 여부 | 미작성 | |
| source_role / definition_kind 구분 명확성 | 미작성 | |
| 출처별 Revision 정보 확인 가능 여부 | 미작성 | |
| raw → normalized → source 역추적 가능 여부 | 미작성 | |
| handoff 문서 충분성 | 미작성 | |

- 종합 결정: 미작성
- 수정 요청 / 미해결 사항: 미작성
- Reviewer 확인 서명 또는 검토 링크: 미작성

최소 1명의 실제 팀원이 모든 항목과 근거를 작성해야 cross_review를 pass로 바꿀 수 있다.
실패/미확인 항목은 해결 기록이 있어야 한다. 빈 칸이나 이 자동 문서 생성은 동의로 취급하지 않는다.
**리뷰 제외:** RAG chunking, embedding, retrieval, Wiki structure/compilation, Context 적합성 및 성능평가.
