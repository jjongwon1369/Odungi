# 평가 질문 v1 봉인 기록

| 항목 | 내용 |
| --- | --- |
| 봉인일 | 2026-09-26 |
| 대상 | 평가 질문 40문항의 정답 파일 (`test_v1.jsonl`, 평가 담당 보관) |
| SHA-256 | `1db412d7e26ba33a47a922b64b0739879e3912b908c0d8a507c514307e537ead` |
| 기준 코퍼스 | connectedhomeip `1ac132b5ecd42cb6c78772f2576ed6f7fc814183` · data_model/1.7 · 4 device types · 23 clusters |
| 공개 시점 | 본 실험 종료 후 원본 파일 공개 |

정답 파일은 실험이 끝날 때까지 공개하지 않는다. 공개 후 누구나 같은 SHA-256 값이 나오는지 확인해
정답이 실험 도중 바뀌지 않았음을 검증할 수 있다.

```powershell
Get-FileHash test_v1.jsonl -Algorithm SHA256
```

질문 원문은 `benchmark/questions_v1.jsonl`에 공개한다.
