# System C — LLM Wiki · run_c3_0930

`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.

## 실행 조건
- 위키: `systems/system_c_llm_wiki/wiki-c3` (compiled_by: openai/gpt-6-astra)
- SSOT: `1ac132b5ecd42cb6c78772f2576ed6f7fc814183`
- 코퍼스: `0.1-c3` `corpus-c3:2f00a8077e434eb6657fb661112012abeceba70c0d1e0633e73f6b7b9c7afb8e`
- 질문셋 SHA-256: `9be6a33eb122d892ee8f6f6fb0ddfd1b40f1bda8ebedbe36e6d199a3105389a2`
- 코드 커밋: `4652547`
- 추론 강도: light (effort=low)
- 출력 상한: max_tokens=16000
- temperature: 보내지 않음
- 클라이언트: 재시도 5회, 타임아웃 SDK 기본값(연결 5초·응답 600초) - System A 와 같음
- 지연: `latency_ms.generate` = LLM 호출 시간 합(System A 의 generate 와 같은 뜻), 호출 간격 대기 제외
- 위키 입력 sha256: `71c40454c6695fc6fd13aade191e1a21dfd11e5311def31f1f07adddf1618359` (System A 색인 입력과 같아야 함)
- SDK: {'python': '3.14.3', 'openai': '3.19.0', 'anthropic': '1.9.0', 'httpx': '0.28.1', 'httpx2': '2.13.0'}

## System A 와의 설계상 차이 (고치지 않고 적는 것)
- 문맥을 검색 top-5 로 한 번에 받지 않고 도구(list_pages·read_page)로 읽고 submit_answer 로 제출한다. 최대 30턴, 턴마다 출력 상한 16000.
- `citations` 는 모델에게 준 문맥이다. A 는 재순위 top-5(늘 5개), C 는 read_page 로 읽은 페이지 전부(개수가 문항마다 다르다). 모델이 고른 인용은 A 는 답변 속 [chunk_id], C 는 `cited_pages` 다.
- GPT 3종은 Responses API 로 부른다(A 는 Chat Completions). 도구와 effort 를 함께 쓰려면 Responses 가 필요하다.
- 목차(list_pages)에 페이지 ID 가 보이고, 클러스터 페이지 ID 에는 hex ID 가 들어 있다.
- 위키는 openai/gpt-6-astra(참가자 아님)가 C3 발췌를 읽어 만든다. A 는 XML 주석·라이선스 머리말을 지운 뒤 청킹한다.
- C 는 문항마다 SDK 클라이언트를 새로 만든다(A 는 참가자마다 하나). 그래서 C 의 generate 에는 문항마다 연결 수립 시간이 한 번 들어간다.
- 페이지 사이 링크(## 관련 페이지)는 scope.json 에서 만든다.
- Kimi 호출 간격: C 는 호출마다 21초, A 는 문항마다 50초. 둘 다 지연에서 뺀다.

## 참가자 모델

| 모델 | provider | reasoning_applied | 비고 |
| --- | --- | --- | --- |
| kimi-k3 | openai_compatible | True | RPM 3/min → min_interval_s=21 |
| gpt-6-luna | openai | True |  |
| gpt-6-sol | openai | True |  |
| gpt-5.6-sol | openai | True |  |
| claude-sonnet-5 | anthropic | True |  |
| claude-opus-5-5 | anthropic | True |  |
| deepseek-flash | openai_compatible | True | DeepSeek-V4.1-Flash (V4 Flash, 9/10 교체) |

## 결과

| 모델 | ok | err | abstained |
| --- | --- | --- | --- |
| kimi-k3 | 40 | 0 | 4 |
| gpt-6-luna | 40 | 0 | 4 |
| gpt-6-sol | 40 | 0 | 4 |
| gpt-5.6-sol | 40 | 0 | 4 |
| claude-sonnet-5 | 40 | 0 | 4 |
| claude-opus-5-5 | 40 | 0 | 4 |
| deepseek-flash | 40 | 0 | 4 |

시작: 2026-09-30T08:42:33.332905+00:00  완료: 2026-09-30T09:54:58.248151+00:00
