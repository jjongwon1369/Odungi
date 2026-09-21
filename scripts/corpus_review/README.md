# Corpus Freeze audit

프로젝트 루트에서 `python scripts/corpus_review/freeze_audit.py`를 실행한다.
Python 표준 라이브러리와 기존 Corpus 유틸리티를 사용한다. 연결된 connectedhomeip는 읽기 전용이다.

문서별 원본 연결/문자 보존/출처별 revision, 독립 통계, missing 검색 및 파일별 라이선스 표시를 검사하고
`corpus/metadata/freeze_audit.json`, `corpus/research/missing_analysis.md`만 갱신한다.
재현성 검사는 HANDOFF에 적힌 기존 `--validate-only` 명령으로 수행한다.

Scope, raw, processed, extraction script는 변경하지 않는다. 이 도구를 추출 pipeline 디렉터리 밖에 둔 이유는
기존 snapshot의 pipeline Hash를 바꾸지 않고 최종 검토하기 위해서다.
라이선스 표시 분류는 이용 권한 판정이 아니다. 팀원의 교차검토와 법적 권한을 자동 승인하지 않는다.
freeze_gate.json은 검토자의 최신 근거 확인 후 갱신하며, 이 도구가 ready 상태를 자동으로 올리지 않는다.
