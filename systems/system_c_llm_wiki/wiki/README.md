# System C — 컴파일된 위키

`compiler/compile_wiki.py` 가 공통 코퍼스로부터 생성한 위키 산출물.
이 폴더의 Markdown 은 직접 손으로 작성하지 않는다. 코퍼스나 컴파일 프롬프트가
바뀌면 재컴파일로 갱신한다.

## 구조

페이지는 **엔티티(기능) 단위**로 나뉜다. 한 엔티티에 대한 스펙·SDK 정의·구현
코드·문서가 한 페이지 안에 함께 들어간다.

```
wiki/
├── base/           공유 베이스 클러스터 (ModeBase, AlarmBase, Label 등)
├── clusters/       클러스터별 페이지. 파일명 = {클러스터ID}-{이름}.md
├── device-types/   기기 타입별 페이지 (세탁기, 냉장고, 에어컨, 온도제어캐비닛)
├── examples/       예제 앱 코드 모음
├── guides/         connectedhomeip 가이드 문서 모음
└── misc/           위 분류에 들어가지 않는 코퍼스 파일
```

## 페이지 형식

각 페이지는 YAML 프론트매터로 출처를 기록한다.

```yaml
---
entity: <엔티티 이름>
ids: [<클러스터 ID 목록>]
source_paths: [<코퍼스 내 원본 파일 경로 목록>]
commit_hash: <SSOT 커밋 해시>
doc_type: cluster | device_type | base | misc
---
```

본문은 입력에 존재하는 역할(spec / sdk / impl / doc / example)에 해당하는 섹션만
갖는다: `## 개요`, `## 스펙`, `## SDK 정의`, `## 구현`, `## 예시`, `## 관련 문서`.

## 검증

`validation/validate_wiki.py` 로 출처 · 식별자 보존 · 전체 토큰 수를 검사한다.
