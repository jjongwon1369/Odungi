---
entity: Matter Devices Registry (SDK)
ids: []
source_paths: ['src/app/zap-templates/zcl/data-model/chip/matter-devices.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: base
compiled_by: openai/gpt-4o-mini
---

## 개요
Matter Devices Registry는 Matter의 다양한 디바이스 유형과 그와 관련된 클러스터 정보를 정의합니다. 이 문서에서는 여러 디바이스 타입에 대한 상세한 정보를 제공하며, 각 디바이스의 클러스터 및 속성 정보를 포함하고 있습니다.

## SDK 정의
- **디바이스 유형 이름**: DISH_WASHER
- **도메인**: CHIP
- **프로파일 ID**: `0x0103`
- **장치 ID**: `0x0075`
- **클러스터 정보**:
  - **Descriptor**: 클러스터의 설명.
  - **Device Energy Management**: 디바이스 에너지 관리 클러스터.
  - **Electrical Alarm**: 전기 알람 관련 클러스터.
  
각 디바이스 타입은 일관된 방식으로 정의되어 있으며, `deviceType` 요소가 그것을 구성하고 있습니다.

## 구현
### 디바이스 예
각 디바이스의 최소 구현 요구 사항을 정의합니다. 예를 들어, `MA-onofflight`의 경우 다음과 같은 클러스터를 포함합니다:
- **Binding**
- **Descriptor**
- **On/Off**: `ON_OFF` 속성을 포함하며, `Off`, `On`, `Toggle` 커맨드를 요구합니다.

### 클러스터 요구 사항
클러스터는 기능, 속성, 및 명령에 대해 필수 및 선택적 요구 사항을 정의합니다. 예를 들어, `Level Control`은 `CURRENT_LEVEL`, `MAX_LEVEL`, `MIN_LEVEL` 속성을 요구합니다.

## 예시
다음은 Matter의 다양한 디바이스 정의 중 일부입니다.

### MA-generic
- **디바이스 타입**: Generic Switch
- **클러스터**:
  - **Descriptor**
  - **Fixed Label**
  - **Identify**

### MA-dishwasher
- **디바이스 타입**: Dishwasher
- **클러스터**:
  - **Descriptor**
  - **On/Off**
  - **Operational State**

## 관련 문서
- Matter Specification: [https://matter.specification.url](https://matter.specification.url)
- Matter SDK Documentation: [https://matter.sdk.documentation.url](https://matter.sdk.documentation.url)