---
entity: Fixed Label
ids: ['0x0040']
source_paths: ['src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml', 'src/app/clusters/fixed-label-server/FixedLabelCluster.cpp', 'src/app/clusters/fixed-label-server/FixedLabelCluster.h', 'src/app/clusters/fixed-label-server/CodegenIntegration.cpp', 'data_model/1.7/clusters/FixedLabel-Cluster.xml']
commit_hash: 1ac132b5ecd42cb6c78772f2576ed6f7fc814183
doc_type: cluster
---

## 개요
Fixed Label 클러스터는 장치가 엔드포인트에 0개 이상의 읽기 전용(read-only) 레이블을 태그할 수 있는 기능을 제공합니다. 이 클러스터는 유틸리티 역할을 수행하며 엔드포인트 범위에서 정의됩니다.

## 스펙
### 클러스터 식별자
*   **ID**: `0x0040`
*   **Name**: `Fixed Label`
*   **Revision**: 1
*   **PICS Code**: `FLABEL`

### 속성 (Attributes)
| ID | 이름 | 타입 | 액세스 | 필수 여부 | 품질 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x0000` | `LabelList` | `list[LabelStruct]` | Read | 필수 | Non-Volatile |

### 데이터 구조 (Data Structures)
#### LabelStruct
| 필드 ID | 이름 | 타입 | 길이 | 설명 |
| :--- | :--- | :--- | :--- | :--- |
| 0 | `Label` | `char_string` | 16 | 레이블 명칭 |
| 1 | `Value` | `char_string` | 16 | 레이블 값 |

## SDK 정의
### ZAP 템플릿
*   **파일 경로**: `src/app/zap-templates/zcl/data-model/chip/fixed-label-cluster.xml`
*   **클러스터 정의**:
    *   `Name`: `Fixed Label`
    *   `Code`: `0x0040`
    *   `Define`: `FIXED_LABEL_CLUSTER`
*   **구조체 정의**: `LabelStruct` (Cluster code `0x0040`, `0x0041`에서 공용)
*   **글로벌 속성**: `ClusterRevision` (코드 `0xFFFD`, 기본값 1)

## 구현
### 서버 구현 (C++)
*   **파일 경로**: `src/app/clusters/fixed-label-server/FixedLabelCluster.cpp`, `FixedLabelCluster.h`
*   **주요 클래스**: `FixedLabelCluster`
    *   `DefaultServerCluster`를 상속받아 구현됩니다.
    *   `ReadAttribute` 함수를 통해 `LabelList`, `ClusterRevision`, `FeatureMap` 속성 읽기 요청을 처리합니다.
    *   `ReadLabelList` 내부 함수에서 `DeviceLayer::DeviceInfoProvider`의 `IterateFixedLabel(endpoint)`를 호출하여 실제 레이블 데이터를 순회하며 인코딩합니다.

### 통합 및 초기화
*   **파일 경로**: `src/app/clusters/fixed-label-server/CodegenIntegration.cpp`
*   **초기화 콜백**: `MatterFixedLabelClusterInitCallback(EndpointId endpointId)`
    *   `CodegenClusterIntegration::RegisterServer`를 통해 해당 엔드포인트에 클러스터 서버를 등록합니다.
    *   `IntegrationDelegate`를 사용하여 `FixedLabelCluster` 인스턴스의 생성 및 해제를 관리합니다.
*   **서버 인스턴스 관리**: `LazyRegisteredServerCluster<FixedLabelCluster>`를 사용하여 정적 및 동적 엔드포인트 수에 맞춰 서버 인스턴스를 관리합니다.

## 관련 문서
*   `src/data_model/FixedLabel-Cluster.adoc`
*   `src/data_model/UserLabel-Cluster.adoc` (LabelStruct 공유)