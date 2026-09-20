# Corpus 이용 조건 기록

검토 대상은 Corpus v0.1의 282개 원본과 고정 commit
`1ac132b5ecd42cb6c78772f2576ed6f7fc814183`의 LICENSE/NOTICE다.
이 문서는 출처와 표시된 조건의 기록이며 법적 권한 승인서가 아니다.
**전체 raw의 재배포·공개 Repository 포함 여부는 needs_review로 보류한다.**

## 출처 및 원문 근거

- [고정 LICENSE](https://github.com/project-chip/connectedhomeip/blob/1ac132b5ecd42cb6c78772f2576ed6f7fc814183/LICENSE): Apache License 2.0.
  로컬 `connectedhomeip/LICENSE:89–126`의 재배포 조건을 읽었다.
- [고정 NOTICE](https://github.com/project-chip/connectedhomeip/blob/1ac132b5ecd42cb6c78772f2576ed6f7fc814183/NOTICE):
  SDK 권리와 Matter 적합성/인증/상표 사용 권리는 같지 않으며, NOTICE를 SDK 사본에 포함하도록 명시한다.
- [Apache 공식 원문](https://www.apache.org/licenses/LICENSE-2.0)의 4절도 확인했다.
  적용 대상의 재배포에는 라이선스 사본, 관련 고지 보존, 수정 표시, 해당 NOTICE 전달 등의 조건이 있다.
  이것만으로 모든 파일의 별도 표시를 덮어쓸 수 있다고 판단하지 않는다.
- 사양 XML의 별도 표시 예:
  [TemperatureAlarm.xml](https://github.com/project-chip/connectedhomeip/blob/1ac132b5ecd42cb6c78772f2576ed6f7fc814183/data_model/1.7/clusters/TemperatureAlarm.xml),
  로컬 `data_model/1.7/clusters/TemperatureAlarm.xml:3–19,53`.
  내부 목적 사용, 조직 외 사용·공개·변환 제한 및 고지 유지 조건이 명시되어 있다.
  공개 GitHub에서 내려받을 수 있다는 사실은 Corpus 재공개 허가의 근거로 삼지 않는다.

LICENSE/NOTICE는 현재 282개 Corpus 파일의 범위 밖이다. 검토용 경로·commit·Hash는
[freeze_audit.json](../metadata/freeze_audit.json)의 licensing_sources에 기록했다.
Scope를 바꾸거나 raw 파일을 추가하지 않았다. 재배포 패키지 구성 시 고지 전달 방법의 별도 확인이 필요하다.

## 전 파일 점검 결과

| 실제 파일 표시 | 수 | 현재 판단 |
|---|---:|---|
| Apache-2.0 명시 고지 발견 | 217 | 해당 조건 충족을 전제로 검토할 수 있음. 배포 승인 자체는 아님 |
| CSA 문서별 제한 고지 | 31 | needs_review: 현재 고지로 전체 공개/재배포를 승인할 수 없음 |
| 파일 자체에서 명시 라이선스 미검출 | 34 | needs_review: 저장소 LICENSE 적용 범위·생성물 출처 확인 필요 |

282개 각각의 source_path, document_id, content_hash, 분류와 근거 줄은
freeze_audit.json의 license_inventory.rows에 있다. 자동 표시는 원문 검토를 돕는 분류다.
고지 미검출은 무라이선스 또는 자유 이용 가능 판정이 아니다. 해당 34개에는 README, 버전 marker,
IDL/ZAP, 생성 Metadata 및 `src/app/clusters/laundry-washer-controls-server/laundry-washer-controls-server.h`가 포함된다.

외부 PDF/별도 웹 문서를 Corpus에 수집한 항목은 0개다. 포함 파일은 모두 connectedhomeip checkout에서 왔다.
하지만 저장소 안의 CSA 사양 XML은 별도 표시가 있으므로 동일한 조건으로 일괄 취급하지 않는다.
이번 검토에 사용한 Apache 웹 페이지는 Corpus 문서로 추가하지 않았다.

## 배포 판단과 남은 확인

| 대상 행위 | 상태 | 필요한 근거 |
|---|---|---|
| 전체 raw 원본의 조직 외 재배포 | needs_review | CSA 대상 문서의 별도 허가/적용 계약과 조직 경계 확인 |
| 공개 Repository에 전체 raw 포함 | needs_review / 현재 승인 불가 | 공개를 허용하는 추가 권한 확인; 단순 공개 저장소 출처는 불충분 |
| Apache 표시 파일만 별도 배포 | 조건부 검토 | 정확한 대상 목록, LICENSE/NOTICE/저작권 고지 전달, 별도 권리 확인 |
| 사양 XML의 정규화·발췌본 이용/공유 | needs_review | 변환 제한과 현재 이용 권한의 관계 확인 |
| 파일별 고지 없는 34개 이용/배포 | needs_review | root LICENSE 적용 및 생성물/원문 출처 확인 |

라이선스 검토 기록 작성은 완료했지만 **이용·배포 권한 확인 Gate는 통과하지 않았다**.
검토 담당자는 적용 조직·이용 범위·권한 문서·대상 snapshot·결론을 남겨야 한다.
확인 전 Scope에서 파일을 임의 제거하거나 라이선스 문구를 바꾸지 않는다.

## 2026-09-20 source별 최종 상태 기록

282개 각 source의 결정은 [source_licensing.json](../metadata/source_licensing.json)에 기록했다.
각 record는 document_id, source_path/URL, 고정 commit/Hash, status, 이유,
LICENSE 4절·NOTICE·파일별 이용 조건의 위치를 포함한다.
앞의 표는 최초 검토 이력이며, 이번 상태 분류는 아래와 같다.

| 상태 | 수 | 결정 |
|---|---:|---|
| redistributable | 217 | 명시적 Apache-2.0 적용 근거가 있는 source. LICENSE/NOTICE/저작권 고지 보존과 해당 수정 고지 등 조건 준수가 전제 |
| reference_only | 31 | 별도 CSA 제한이 있는 사양 XML. 출처 참조만 허용 대상으로 관리하며 raw 또는 normalized 재배포 허가를 추정하지 않음 |
| needs_review | 34 | 파일별 명시 고지 미확인. root LICENSE 적용 및 생성물 출처에 대한 추가 근거 필요 |

`redistributable`은 조건부 source 분류이며 현재 전체 배포 패키지의 승인 또는 포괄적인 특허/상표 허가가 아니다.
`reference_only`는 현재 로컬 raw에서 해당 파일을 제거했다는 뜻이 아니다. 기존 Corpus는 그대로이며
조직 내부 변환·보관 권한도 별도 확인이 필요하다. 현재 전체 raw 공개 배포는 승인하지 않는다.

**변경 제안만 기록:** 공개 배포를 추진한다면 reference_only 31개는 원문 payload 대신 출처 기록으로
제공하고 needs_review 34개는 권한 확인 전 배포에서 보류하는 별도 패키지 방식을 검토해야 한다.
LICENSE/NOTICE 전달도 준비해야 한다. raw/normalized 수록 범위를 실제 바꾸는 결정에는 Scope 검토,
새 snapshot과 version 검토가 필요하므로 이번에는 적용하지 않았다.
licensing_review Gate는 source 분류 작성 완료와 별개로 `needs_review`를 유지한다.
