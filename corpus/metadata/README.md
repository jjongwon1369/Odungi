확정 입력: `scope.json`, `coverage_matrix.csv`. 실행으로 수정하지 않는다.

생성 산출물:

- `snapshot.json`: commit, Scope/Coverage/pipeline Hash, corpus_version=0.1, frozen=false
- `corpus_manifest.csv`: 고유 원본 파일별 ID·역할·Revision·원본 SHA-256
- `entities.jsonl`, `relations.jsonl`: 출처·제품·Cluster·구현·endpoint 관계와 근거
- `statistics.json`: 파일/문서/관계/그룹별 수, bytes, 문자 수. tokenizer 결정 전 Token은 null
- `validation_report.json`: 무결성·Scope·Identifier·원본 위치·독립 재생성 검사 결과
- `freeze_audit.json`: 최종 통계 대조·provenance 예외·missing 분류·파일별 라이선스 표시 기록
- `freeze_gate.json`: 검토 대상 Hash와 항목별 상태; 미확인 이용 권한/근거 예외/팀 교차검토를 자동 승인하지 않음

source_role별 Definition과 출처별 Revision을 합치지 않는다.
공유 파일은 여러 제품 집계에 나타날 수 있지만 물리 원본은 한 번만 저장한다.
