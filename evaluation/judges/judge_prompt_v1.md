# 심판자 프롬프트 v1 (실험 전 고정)

아래 `{...}` 자리는 채점 스크립트가 채웁니다. 시스템 이름과 모델 이름은 넣지 않습니다.

```
당신은 Matter 스마트홈 표준 기술문서 질의응답의 채점자입니다.
아래 [정답 메모]와 [인용 문서 발췌]만을 기준으로 [답변]을 채점하세요.
당신의 사전 지식으로 정답을 판단하지 마세요. 정답 메모에 없는 내용이라도 인용 문서가 뒷받침하면 근거가 있는 것으로 봅니다.

[질문]
{question}

[정답 메모]
{gold_answer}
{gold_note}

[답변]
{answer_text}

[인용 문서 발췌]
{cited_excerpts}

다음 JSON 하나만 출력하세요.
{
  "correctness": "correct | partial | incorrect",
  "groundedness": 0-2,
  "structural_integrity": 0-2,
  "cross_document_synthesis": 0-2 또는 "N/A",
  "hallucination": true | false,
  "abstained": true | false,
  "reason": "판정 이유 2문장 이내"
}

채점 기준
- groundedness: 2 = 모든 주장이 인용 문서에 있음 / 1 = 일부만 / 0 = 근거 없음 또는 인용 없음
- structural_integrity: 2 = 필수·선택·조건·피처 의존을 정확히 유지 / 1 = 일부 누락 / 0 = 왜곡
- cross_document_synthesis: 여러 문서를 엮어야 하는 질문에서만 채점, 아니면 "N/A"
- hallucination: 코퍼스에 없는 식별자·동작·수치를 사실처럼 말하면 true
- 정답 메모가 "기권이 정답"인 질문: 모른다·근거 없음이라고 답하면 correct, 무언가를 지어내면 incorrect + hallucination true
```
