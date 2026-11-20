---
entity: Robotic Vacuum Cleaner
ids: ['0x0074']
source_paths: ['data_model/1.7/device_types/RoboticVacuumCleaner.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: device_type
compiled_by: openai/gpt-6-astra
corpus_source: corpus/tiers/c12/processed/documents.jsonl
corpus_snapshot: corpus-c12:4dd5f8b69bb7a8a3183d8babf8135891122d79d2fb2596431e53c0c11da1f2ad
---

# Robotic Vacuum Cleaner

## 개요

| 항목 | 값 |
|---|---|
| 디바이스 타입 이름 | Robotic Vacuum Cleaner |
| 디바이스 타입 ID | `0x0074` |
| 리비전 | `4` |
| 분류 | `simple` |
| 범위 | `endpoint` |

## 스펙

출처: `data_model/1.7/device_types/RoboticVacuumCleaner.xml`

### 클러스터 구성

모든 클러스터의 역할은 `server`이다.

| 클러스터 ID | 클러스터 이름 | 지원 요구사항 |
|---|---|---|
| `0x0003` | Identify | 필수 |
| `0x0054` | RVC Run Mode | 필수 |
| `0x0055` | RVC Clean Mode | 선택 |
| `0x0061` | RVC Operational State | 필수 |
| `0x0150` | Service Area | 선택 |

### 이벤트 요구사항

| 소속 클러스터 | 이벤트 ID | 이벤트 이름 | 지원 요구사항 |
|---|---|---|---|
| RVC Operational State (`0x0061`) | `0x0001` | OperationCompletion | 필수 |

### 리비전 이력

| 리비전 | 변경 내용 |
|---|---|
| `1` | 최초 리비전 |
| `2` | 클러스터 사용 제약과 참고 정보 추가. 모든 제약을 해당 클러스터 스펙으로 이동한 뒤 요소 요구사항 섹션 제거 |
| `3` | Service Area 클러스터 지원 추가 |
| `4` | OperationCompletion 이벤트 필수화 |

## 관련 페이지

**직접 클러스터**

- [Identify `0x0003`](../clusters/0x0003-identify.md)
- [RVC Run Mode `0x0054`](../clusters/0x0054-rvc-run-mode.md)
- [RVC Clean Mode `0x0055`](../clusters/0x0055-rvc-clean-mode.md)
- [RVC Operational State `0x0061`](../clusters/0x0061-rvc-operational-state.md)
- [Service Area `0x0150`](../clusters/0x0150-service-area.md)

**베이스 클러스터**

- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)
- [Binding `0x001E`](../clusters/0x001E-binding.md)
- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)
- [User Label `0x0041`](../clusters/0x0041-user-label.md)
