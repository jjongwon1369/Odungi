# Corpus v0.1 실행 결과

고정 commit `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`와 기존 scope-v1.0을 사용했다.
Scope JSON과 Coverage CSV는 변경하지 않았다. Finalization의 실행 금지 표시는 당시 단계의 기록이며,
이번 Corpus Extraction Pipeline 요청에 따라 구현·dry-run·실제 생성·검증을 수행했다.
connectedhomeip는 읽기 전용으로 사용했고 Corpus v1.0 Freeze는 수행하지 않았다.

구현/재실행: [scripts/corpus/README.md](../../scripts/corpus/README.md).
기계 판독 결과: [snapshot](../metadata/snapshot.json), [statistics](../metadata/statistics.json),
[validation](../metadata/validation_report.json), [manifest](../metadata/corpus_manifest.csv).

## 실행 결과

최종 dry-run과 실제 실행의 선택 파일·문서·관계 수는 같았다.

| 항목 | 결과 |
|---|---:|
| 고유 원본 파일 | 282 |
| 정규화 문서 | 282 |
| 관계 | 764 |
| Entity | 342 |
| 고유 Cluster | 23 / 23 |
| Device Type → Cluster 관계 | 42 |
| 원본 바이트 | 3,884,956 |
| 정규화 문자 | 2,144,062 |
| 원본 위치 span | 755 |
| 검사한 Identifier 출현 횟수 | 191,531 |
| 누락된 추출 대상 파일 / 범위 밖 파일 | 0 / 0 |

| Device Type | 관련 파일 수 |
|---|---:|
| Laundry Washer (0x0073) | 113 |
| Room Air Conditioner (0x0072) | 209 |
| Refrigerator (0x0070) | 99 |
| Temperature Controlled Cabinet (0x0071) | 81 |

관련 파일 수는 중복 집계다. 공유 Cluster·framework·예제 정의는 여러 제품과 관련될 수 있으며,
이 값은 해당 제품을 선언한 endpoint 수나 완성된 제품 구현 수가 아니다.

| source_role | 파일 수 |
|---|---:|
| specification | 34 |
| sdk_codegen | 23 |
| implementation | 185 |
| documentation | 17 |
| example | 20 |
| generated_definition | 3 |

구현 185개는 비재귀 component CPP/H 183개와 명시된 지원 파일 2개다.
specification에는 사양 XML 외에 고정된 spec_sha/spec_tag/scraper_version 파일도 포함한다.
따라서 source_role 수를 XML 파일 수와 동일하게 해석하지 않는다.

## 검증

- 검증 보고서: **pass 14 / warning 3 / fail 0**.
- 단위·통합 테스트: **13개 통과**.
- 두 임시 디렉터리에서 독립 재생성하고 실제 산출물까지 비교했다. 288개 파일의 바이트 Hash가 일치했다.
  document_id set, relation set, raw SHA-256, normalized_hash도 일치했다.
- 원본은 checkout newline 변환 전의 고정 Git blob과 동일하다.
- Identifier 검사는 선택 원본 구간과 정규화 본문의 lexical inventory를 비교한다. 의미적 적합성 평가는 아니다.
- 잘못된 commit, dirty source, 존재하지 않는 파일, 중복 ID, Hash 손상, Identifier 변경,
  공유 구현 중복 방지, UTF-8/newline/원본 위치, Heater/범위 밖 ID 제외, 출처별 revision을 테스트했다.
- SDK Device Type에 있는 Temperature Alarm include는 보존한다. 독립적인 SDK Cluster 정의가 있다는 뜻은 아니다.

시작/종료 Scope Hash:

- scope.json: `eec94fc3153e226dc48f244dd9153a29cba72254b97a88b3f51f8e4b76dd75f7`
- coverage_matrix.csv: `bbf336ef82ab0b1dc3956b9eb107036ee75b42c9d574b5a85fd53584e0bf60ba`

## 경고와 Freeze 전 작업

1. 확정 Scope에서 허용한 missing 21행을 유지한다. 20행은 9개 component의 독립 Markdown 부재이며,
   1행은 Temperature Alarm의 concrete SDK/implementation/IDL 부재를 포함한다. 추출 과정의 파일 유실은 없다.
   not_applicable 32행도 기존 감사 기록에 남긴다.
2. 사양·SDK·예제·구현의 출처별 revision을 보존했지만 의미적 정합성, 실제 Feature 활성 상태,
   런타임 동작을 판정하지 않았다. 숫자 차이 자체는 오류가 아니다.
3. tokenizer/model을 정하지 않았으므로 Token 수는 null이다.

v1.0 Freeze 전에는 기존 이용·보관·공유 조건 확인, revision 차이의 의미 검토 및 팀 교차 검토,
tokenizer/model 결정과 후속 Context 적합성 점검이 남는다.
이번에는 RAG chunking, embedding, Wiki compilation, benchmark/Gold Answer 생성을 수행하지 않았다.
