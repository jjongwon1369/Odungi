# 평가 질문 40문항 (v1)

기준 코퍼스: Odungi corpus v1.0 후보 · connectedhomeip `1ac132b5` · Matter 1.7 · 4 디바이스 타입 · 23 클러스터

| 팀 유형 | 문항 수 |
| --- | --- |
| 식별자형 (`identifier`) | 12 |
| 의미형 (`semantic`) | 9 |
| 다중홉 (`multihop`) | 15 |
| 대조군 (`control`) | 4 |

- 정답은 평가 담당(박종원)이 따로 보관하고, 실험 뒤 공개합니다. 봉인 기록은 `prereg/test_v1_seal.md`.
- 시스템 입력은 `questions_v1.jsonl`을 쓰고, 답변의 `qid`는 `query_id`와 똑같이 적어 주세요.
- 저장 형식은 `answer_format.md`를 봐 주세요.


## 단순 조회

- **Q-simple-001** [식별자형] Fan Control 클러스터의 클러스터 ID는?
- **Q-simple-002** [식별자형] Operational State 클러스터의 클러스터 ID는?
- **Q-simple-003** [식별자형] Operational State 클러스터의 Resume 커맨드 ID는?
- **Q-simple-004** [식별자형] Fan Control 클러스터의 Step 커맨드 ID는?
- **Q-simple-005** [식별자형] Thermostat 클러스터의 SetpointRaiseLower 커맨드 ID는?
- **Q-simple-006** [식별자형] Identify 클러스터의 TriggerEffect 커맨드 ID는?
- **Q-simple-007** [식별자형] Laundry Washer Controls 클러스터의 NumberOfRinses 속성 ID는?
- **Q-simple-008** [식별자형] Thermostat 클러스터의 SystemMode 속성 ID는?
- **Q-simple-009** [식별자형] Operational State 클러스터가 정의하는 이벤트를 이벤트 ID와 함께 모두 나열하라.

## 복합 추론

- **Q-multihop-001** [다중홉] Room Air Conditioner와 Temperature Controlled Cabinet 디바이스 타입이 공통으로 포함하는 서버 클러스터는? 클러스터 ID와 함께.
- **Q-multihop-002** [다중홉] Refrigerator와 Room Air Conditioner 디바이스 타입이 공통으로 포함하는 서버 클러스터는? 클러스터 ID와 함께.
- **Q-multihop-003** [다중홉] Laundry Washer와 Temperature Controlled Cabinet 디바이스 타입이 공통으로 포함하는 서버 클러스터는? 클러스터 ID와 함께.
- **Q-multihop-004** [식별자형] Laundry Washer 디바이스 타입에 무조건 필수(M)인 서버 클러스터는? 클러스터 ID와 함께.
- **Q-multihop-005** [식별자형] Temperature Controlled Cabinet 디바이스 타입에 무조건 필수(M)인 서버 클러스터는? 클러스터 ID와 함께.
- **Q-multihop-006** [식별자형] Fan Control 클러스터의 속성 중 conformance가 MultiSpeed(SPD) 피처에 의존하는 것은? 속성 ID와 함께.
- **Q-multihop-007** [다중홉] 이 코퍼스의 4개 디바이스 타입 중 Activated Carbon Filter Monitoring 클러스터를 서버로 포함하는 것을 모두 나열하고, 각각의 conformance(필수/선택/조건)를 말하라.
- **Q-multihop-008** [다중홉] 이 코퍼스의 4개 디바이스 타입 중 Identify 클러스터를 서버로 포함하는 것을 모두 나열하고, 각각의 conformance(필수/선택/조건)를 말하라.
- **Q-multihop-009** [다중홉] Laundry Washer Mode 클러스터는 어떤 베이스 클러스터에서 파생되며, 그 베이스에서 물려받는 무조건 필수(M) 커맨드(요청·응답)는? 커맨드 ID와 함께.
- **Q-multihop-010** [의미형] Temperature Controlled Cabinet 디바이스 타입에서 Cooler 조건 또는 Heater 조건에 따라 요구되는 서버 클러스터를 조건별로 나누어 말하라. 클러스터 ID와 함께.

## 코드-문서 일치

- **Q-codedoc-001** [다중홉] SDK On/Off 서버 구현에서 기본 OnOffCluster가 처리하는 커맨드와, OnOffLightingCluster가 추가로 처리하는 커맨드를 구분해 말하라. 추가 커맨드들이 XML에서 어떤 피처에 묶여 있는지도 답하라.
- **Q-codedoc-002** [다중홉] SDK의 OperationalStateCluster 구현이 처리하는 요청 커맨드와 생성하는 응답 커맨드는? XML 정의의 커맨드 ID와 함께.
- **Q-codedoc-003** [다중홉] Laundry Washer Controls 클러스터에서 쓰기(write)가 가능한 속성은? XML 접근 권한과 SDK의 WriteAttribute 구현을 근거로 답하라.
- **Q-codedoc-004** [다중홉] Refrigerator Alarm 클러스터를 SDK로 구현했을 때 AcceptedCommandList에 나타나는 커맨드는? Alarm Base와의 관계, XML conformance, SDK 설정을 근거로 답하라.
- **Q-codedoc-005** [다중홉] Fan Control의 Step 커맨드는 어떤 피처가 있어야 지원되며, SDK 구현은 그 피처가 없을 때와 direction 값이 잘못됐을 때 각각 어떻게 동작하나?
- **Q-codedoc-006** [다중홉] Thermostat.xml에 정의된 요청 커맨드 중, 코퍼스에 포함된 SDK thermostat-server 구현에 처리 코드가 없는 것은? 각 커맨드의 XML conformance와 함께.
- **Q-codedoc-007** [다중홉] Thermostat 클러스터에서 atomicWrite 품질을 가진 속성은? SDK는 이 속성들의 원자적 쓰기를 어떤 커맨드로 처리하나?
- **Q-codedoc-008** [의미형] Temperature Control의 SetTemperature 커맨드를 SDK가 처리할 때 반환할 수 있는 오류 상태 코드를 경우별로 말하라 (TN 피처 / TL 피처).
- **Q-codedoc-009** [다중홉] HEPA Filter Monitoring과 Activated Carbon Filter Monitoring은 XML 정의 파일과 SDK 구현 클래스를 각각 어떻게 공유하나? 두 클러스터의 ID와 함께 답하라.
- **Q-codedoc-010** [다중홉] refrigerator-app 예제(.matter)의 엔드포인트별 디바이스 타입은? 캐비닛 엔드포인트의 Temperature Control featureMap 값은 어떤 피처를 뜻하나?

## 실무형

- **Q-practical-001** [의미형] 냉장고 문이 오래 열려 있을 때 알림을 보내려고 한다. 어느 클러스터의 어떤 알람 비트를 쓰면 되나?
- **Q-practical-002** [의미형] 에어컨 앱에 'HEPA 필터 교체 필요' 알림과 '교체 완료' 버튼을 넣으려 한다. 필요한 클러스터, 읽을 속성, 보낼 커맨드는?
- **Q-practical-003** [의미형] 세탁기 앱에서 '표준/울/급속' 같은 세탁 코스를 바꾸게 하려면 어느 클러스터의 어떤 커맨드와 속성을 쓰나?
- **Q-practical-004** [의미형] 세탁기 앱에 시작·일시정지·재개 버튼을 만든다. 어느 클러스터의 어떤 커맨드를 보내며, 이 클러스터는 Laundry Washer에서 필수인가?
- **Q-practical-005** [의미형] 냉동 캐비닛 온도를 '약/중/강' 단계로만 고르게 하려고 한다. Temperature Control의 어떤 피처를 켜고, 어떤 속성과 커맨드 필드를 쓰나?
- **Q-practical-006** [의미형] 에어컨 화면에 실내 습도를 표시하려면 어느 클러스터의 어떤 속성을 읽으면 되나? Room Air Conditioner에서 이 클러스터는 필수인가?
- **Q-practical-007** [의미형] 에어컨을 원격으로 냉방·난방·송풍 모드로 바꾸려면 어느 클러스터의 어떤 속성을 써야 하나?

## 대조군

- **Q-control-001** [대조군] Laundry Dryer 디바이스 타입에서 건조 온도를 설정하는 클러스터와 속성은 무엇인가?
- **Q-control-002** [대조군] Room Air Conditioner가 소비한 전력량(kWh)을 보고하는 클러스터와 속성은 무엇인가?
- **Q-control-003** [대조군] Room Air Conditioner 디바이스 타입 revision 6에서 새로 추가된 클러스터는 무엇인가?
- **Q-control-004** [대조군] 냉장고 제빙기의 얼음 잔량을 보고하는 Matter 클러스터는 무엇인가?
