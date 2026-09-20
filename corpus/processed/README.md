`documents.jsonl`은 원본 파일당 한 record를 저장한다.
UTF-8 decoding, newline 통일, 확정 Scope에 따른 정확한 원문 절취와 provenance 연결만 수행한다.
source_spans는 LF로 통일한 원본 view의 1-based 줄 범위와 Unicode offset을 기록한다.
본문은 완전한 XML/JSON 문서가 아닌 원문 발췌 모음일 수 있다. 완전한 원본은 raw에 있다.
요약·RAG chunk·Wiki·embedding은 포함하지 않는다.
