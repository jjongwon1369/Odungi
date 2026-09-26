# 답변 저장 형식 (9/29 회의 확정용 제안)

**기본은 태이님이 정한 `AnswerRecord` v0.3을 그대로 씁니다** (`systems/system_a_rag/rag_proto/src/rag_proto/schema.py`).
세 시스템이 같은 형식으로 저장하면 채점 스크립트가 바로 읽습니다.

## 추가 제안 (필드 3개)

본 실험은 참가자 LLM 7개 × 반복 3회라서, 한 줄만 보고 어떤 모델의 몇 회차인지 알 수 있어야 합니다.

| 필드 | 예 | 이유 |
|---|---|---|
| `model` | `gpt-6-luna` | 참가자 LLM 7개 구분 |
| `run` | `1` | 반복 1~3회차 구분 |
| `qid` | `Q-simple-001` | `benchmark/questions_v1.jsonl`의 `query_id`와 **똑같이** |

## 시스템별 참고

- **System B (분해형 RAG)**: `query_mode: "decomposed"`로 저장하면 A와 구분됩니다.
- **System C (LLM Wiki)**: `run_agent.py` 결과에 `qid`, `model`, `run`만 붙이면 됩니다. `cited_pages`, `retrieved.wiki_pages`, `token_usage`는 지금 형식 그대로 읽을 수 있습니다.
- 토큰은 합치지 말고 4열(입력·캐시 생성·캐시 읽기·출력) 그대로 남깁니다.
- 모르는 질문은 지어내지 말고 모른다고 답하게 합니다. 대조군 문항이 이걸 봅니다.
- 실패한 질문도 빠뜨리지 말고 `error`에 메시지를 남겨 한 줄로 저장합니다.
- 본 실험은 코드를 커밋한 뒤 그 커밋으로 돌리고, `config_hash`를 남깁니다.
