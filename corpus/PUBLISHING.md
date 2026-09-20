# 공개 저장소의 수록 범위

이 저장소에는 Corpus 구축 코드, 확정 Scope, 검토 문서, manifest·통계·출처별 권한 기록을 공유한다.
로컬 Corpus v0.1의 수집 범위를 변경한 것이 아니다.

다음 산출물은 `.gitignore`로 공개 커밋에서 제외하고 로컬에 유지한다.

- `raw/connectedhomeip/`: 원본 payload
- `processed/documents.jsonl`: 정규화 본문
- `metadata/relations.jsonl`, `entities.jsonl`, `freeze_audit.json`: 원문 발췌가 포함될 수 있는 상세 기록과 연결 Entity

라이선스 분류는 `research/licensing_review.md`와 `metadata/source_licensing.json`에 기록했다.
reference_only / needs_review 자료를 포함한 전체 payload는 공개 재배포 승인을 받지 않았다.
공유한 Hash·통계·검증 보고서는 로컬에서 생성·검증한 snapshot의 기록이며,
공개 Git checkout에 payload까지 모두 들어 있다는 뜻이 아니다.
HANDOFF 등의 제외 산출물 경로는 로컬 생성 후 사용할 수 있다.

재생성에는 별도로 준비한 고정 connectedhomeip checkout 및 적용 가능한 이용 권한이 필요하다.
소스 저장소에는 쓰지 않는다. 상세 명령은 `HANDOFF.md`를 참고한다.
공개 배포용 payload 구성을 바꾸려면 이용 조건과 Scope/version 영향을 별도로 검토해야 한다.
