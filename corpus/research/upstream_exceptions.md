# Upstream evidence 최종 결정

2026-09-20 검토. 대상은 snapshot.json의 기존 Corpus v0.1이다.
**4건 모두 external_reference_only로 유지한다.** scope_exception_include 또는 scope_out은 선택하지 않았다.
현재 Corpus의 Scope, raw, normalized, manifest, relations를 수정할 필요가 없다.
이 결정의 pass는 모든 evidence가 Corpus 내부에 있다는 의미가 아니라, 명시적 외부 참조 처리 검토가 완료됐다는 의미다.

## 공통 출처 및 근거

- commit: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- source path: `src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py`
- [고정 원문 1961–1964행](https://github.com/project-chip/connectedhomeip/blob/1ac132b5ecd42cb6c78772f2576ed6f7fc814183/src/python_testing/matter_testing_infrastructure/matter/testing/spec_parsing.py#L1961-L1964)
- 1963행은 각 Device Type의 server_clusters에 Base의 server_clusters를 합치는 코드다.
- 원문 SHA-256: `a040caeab50c841eae60fcb9b27ed14c45e25477859911844a3abfd2e60bc931`
- Corpus 내부의 직접 근거는 `data_model/1.7/device_types/BaseDeviceType.xml`이며, 외부 parser는 적용 방식의 보조 근거다.

| Coverage | 관련 Entity / 관계 | 현재 Corpus 밖에 있는 이유 | 재현 필수성 | 결정과 근거 |
|---|---|---|---|---|
| R005 | Laundry Washer (device_type 0x0073) → BaseDeviceType, inherits_requirements | 확정 allowlist가 Python testing infrastructure를 포함하지 않음 | 현재 재생성/검증에서 원문 접근 필수; normalized 입력 포함은 불필요 | external_reference_only. 위 parser:1963의 Base 적용 근거를 고정 참조로 유지 |
| R008 | Room Air Conditioner (device_type 0x0072) → BaseDeviceType, inherits_requirements | 동일한 allowlist 경계 | 현재 재생성/검증에서 원문 접근 필수; normalized 입력 포함은 불필요 | external_reference_only. 위 parser:1963의 Base 적용 근거를 고정 참조로 유지 |
| R011 | Refrigerator (device_type 0x0070) → BaseDeviceType, inherits_requirements | 동일한 allowlist 경계 | 현재 재생성/검증에서 원문 접근 필수; normalized 입력 포함은 불필요 | external_reference_only. 위 parser:1963의 Base 적용 근거를 고정 참조로 유지 |
| R014 | Temperature Controlled Cabinet (device_type 0x0071) → BaseDeviceType, inherits_requirements | 동일한 allowlist 경계 | 현재 재생성/검증에서 원문 접근 필수; normalized 입력 포함은 불필요 | external_reference_only. 위 parser:1963의 Base 적용 근거를 고정 참조로 유지 |

4건은 물리 upstream 파일 하나를 공유한다. source/target Entity, relation_id, primary document_id,
URL·commit·Hash·결정은 [upstream_exception_decisions.json](../metadata/upstream_exception_decisions.json)에 건별로 기록했다.

## 재현 경계

`scripts/corpus/extract_corpus.py`의 Graph.evidence와 build는 이 원문을 읽어 Hash를 만들며,
`scripts/corpus/validate_corpus.py`도 같은 commit의 원문과 근거 위치를 확인한다.
따라서 **현재 파이프라인을 그대로 재생성하려면 전체 pinned checkout에서 이 파일에 접근할 수 있어야 한다**.
parser를 실행하거나 normalized 실험 입력에 포함할 필요는 없다.
기존 Corpus를 읽는 데 외부 코드를 실행할 필요도 없다. 다운스트림 시스템 동작은 평가하지 않았다.

기존 `storage=upstream_reference_only`, `document_id=null`을 유지한다. 가짜 Corpus document_id를 부여하지 않는다.
전체 checkout 없이 자체 완결적인 재생성 패키지를 요구하게 된다면 이 파일의 제한적 포함을
`scope_exception_include` 변경안으로 별도 검토해야 한다. 이는 현재 요구가 아니므로 적용하지 않는다.
