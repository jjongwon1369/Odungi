`connectedhomeip/<original relative path>`에 고정 commit의 Git blob 바이트를 보존한다.
checkout의 newline 변환과 무관하며 encoding/formatting을 변경하지 않는다.
공유 파일은 한 번만 저장한다. 통합 파일의 Scope 밖 내용도 원본 보존을 위해 raw에는 남지만,
공통 입력 대상은 processed의 선택 span으로 제한한다. Hash와 경로는 metadata/corpus_manifest.csv에서 검증한다.
