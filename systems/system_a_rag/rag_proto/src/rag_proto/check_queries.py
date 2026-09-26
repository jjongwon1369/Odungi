"""
rag_proto.check_queries — 질의셋 사전 검증

data/queries.jsonl의 각 문항이 실제로 코퍼스에서 답할 수 있는지 확인한다.

왜 필요한가:
  이전에 docs/만으로 코퍼스를 만들었을 때, 질문에 답할 자료가 하나도 없다는 사실을
  리랭커 점수가 0.001로 나온 뒤에야 알았다. 질의셋을 먼저 검증하면 실험을 돌리기
  전에 잡을 수 있다.

검사 항목:
  1. gold_identifiers가 chunks.jsonl 어딘가에 실제로 존재하는가
  2. gold_doc_ids가 corpus.jsonl에 실제로 존재하는가
  3. control 문항이 정말 코퍼스에 없는 내용을 묻는가 (있으면 대조군 자격 상실)
  4. tier 배분이 의도대로인가

실행:
    python -m rag_proto.check_queries
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from .schema import EvalQuery, QueryTier

QUERIES_PATH = Path("data/queries.jsonl")
CHUNKS_PATH = Path("data/chunks.jsonl")
CORPUS_PATH = Path("data/corpus.jsonl")

EXPECTED_TIERS = {
    QueryTier.IDENTIFIER: 8,
    QueryTier.SEMANTIC: 6,
    QueryTier.MULTIHOP: 4,
    QueryTier.CONTROL: 2,
}


def load_queries(path: Path = QUERIES_PATH) -> list[EvalQuery]:
    """
    두 형식을 모두 읽는다.
      - data/queries.jsonl (개인 20문항): qid + gold 필드
      - Odungi benchmark/questions_v1.jsonl (팀 40문항): query_id, gold 없음
        (정답은 평가 담당이 따로 보관). qid에 query_id를 그대로 넣어야
        채점 스크립트가 답변을 문항과 짝지을 수 있다.
    """
    queries: list[EvalQuery] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if "qid" not in rec and "query_id" in rec:
                rec["qid"] = rec.pop("query_id")
            queries.append(EvalQuery(**rec))
    return queries


def load_corpus_index() -> tuple[set[str], set[str], str]:
    """(모든 식별자, 모든 doc_id, 전체 텍스트 소문자)를 돌려준다."""
    identifiers: set[str] = set()
    doc_ids: set[str] = set()
    blobs: list[str] = []

    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            identifiers.update(c.get("identifiers") or [])
            blobs.append(c.get("text", ""))

    with CORPUS_PATH.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                doc_ids.add(json.loads(line)["doc_id"])

    return identifiers, doc_ids, "\n".join(blobs).lower()


def check(queries: list[EvalQuery]) -> tuple[list[str], list[str]]:
    """(치명적 문제, 경고)를 돌려준다."""
    identifiers, doc_ids, corpus_text = load_corpus_index()
    errors: list[str] = []
    warnings: list[str] = []

    counts = Counter(q.tier for q in queries)
    for tier, expected in EXPECTED_TIERS.items():
        got = counts.get(tier, 0)
        if got != expected:
            warnings.append(f"{tier.value} 문항이 {got}건입니다 (계획 {expected}건)")

    seen_ids: set[str] = set()
    for q in queries:
        if q.qid in seen_ids:
            errors.append(f"{q.qid}: qid 중복")
        seen_ids.add(q.qid)

        if q.tier is QueryTier.CONTROL:
            # 대조군은 코퍼스에 없어야 한다
            if q.gold_identifiers:
                errors.append(f"{q.qid}: 대조군인데 gold_identifiers가 있습니다")
            continue

        if not q.gold_identifiers:
            warnings.append(f"{q.qid}: gold_identifiers가 비어 있어 자동 채점 불가")

        missing_ids = [i for i in q.gold_identifiers if i not in identifiers]
        if missing_ids:
            # 식별자 집합에 없더라도 원문에는 있을 수 있다.
            # 추출 정규식이 CamelCase 2덩어리 이상만 잡으므로
            # On, Off, Toggle 같은 단일 단어 식별자는 걸러지지 않는다.
            # 이건 코퍼스 부재가 아니라 지표의 한계이므로 경고로 구분한다.
            absent = [i for i in missing_ids if i.lower() not in corpus_text]
            unextractable = [i for i in missing_ids if i not in absent]

            if absent:
                errors.append(
                    f"{q.qid}: 코퍼스에 존재하지 않는 식별자 {absent}\n"
                    f"       → 이 질문은 현재 코퍼스로 답할 수 없습니다"
                )
            if unextractable:
                warnings.append(
                    f"{q.qid}: 원문에는 있으나 식별자로 추출되지 않음 {unextractable}\n"
                    f"         → 식별자 인용 정확도 자동 채점에서 빠집니다"
                )

        missing_docs = [d for d in q.gold_doc_ids if d not in doc_ids]
        if missing_docs:
            errors.append(f"{q.qid}: 코퍼스에 없는 doc_id {missing_docs}")

        if q.tier is QueryTier.MULTIHOP and len(q.gold_doc_ids) < 2:
            warnings.append(
                f"{q.qid}: multihop인데 gold_doc_ids가 {len(q.gold_doc_ids)}건입니다"
            )

    return errors, warnings


def main() -> int:
    if not CHUNKS_PATH.exists():
        print(f"{CHUNKS_PATH}가 없습니다. S1·S2를 먼저 실행하세요.")
        return 1

    queries = load_queries()
    errors, warnings = check(queries)

    counts = Counter(q.tier.value for q in queries)
    print(f"문항 수  : {len(queries)}")
    print(f"유형 배분: {dict(counts)}")
    print()

    for w in warnings:
        print(f"  [경고] {w}")
    for e in errors:
        print(f"  [오류] {e}")

    if errors:
        print(f"\n{len(errors)}건의 오류. 질의셋 또는 코퍼스를 고쳐야 합니다.")
        return 1
    print("질의셋 검증 통과. 모든 문항이 현재 코퍼스로 답할 수 있습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
