A/B/C 공통 원본 Corpus. 확정 Scope와 connectedhomeip의 고정 commit으로 Corpus v0.1을 생성한다.
v1.0 Freeze, RAG/Wiki 전처리, 평가 데이터 생성은 포함하지 않는다.

공개 저장소에는 원본·정규화 payload를 포함하지 않는다. [PUBLISHING.md](PUBLISHING.md)에 커밋 범위와 로컬 산출물의 관계를 명시했다.

최신 인계 계약은 [HANDOFF.md](HANDOFF.md), Freeze 준비 상태는 [freeze_gate.json](metadata/freeze_gate.json)이다.
Corpus 담당 범위의 최종 검토는 시스템별 전처리·성능·Context 적합성을 통과 조건으로 삼지 않는다.

- 범위: [corpus_scope.md](corpus_scope.md), [scope.json](metadata/scope.json)
- 실행 방법과 데이터 계약: [Extraction README](../scripts/corpus/README.md)
- 결과: [snapshot](metadata/snapshot.json), [manifest](metadata/corpus_manifest.csv),
  [statistics](metadata/statistics.json), [validation report](metadata/validation_report.json)
- 원본은 raw/connectedhomeip에, 파일별 정규화 문서는 processed/documents.jsonl에 저장한다.

Finalization 문서의 미실행 표시는 당시 이력이며, 이후 실행 상태는 snapshot/검증 보고서가 기록한다.
