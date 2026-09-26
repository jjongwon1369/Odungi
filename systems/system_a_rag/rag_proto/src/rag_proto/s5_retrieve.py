"""
rag_proto.s5_retrieve — S5. 하이브리드 검색 + 재순위

질의 → BM25 top-N + 벡터 top-N → RRF 융합 → 재순위 → top-k

공식 API (확인 완료, BAAI/bge-reranker-v2-m3 README):
    from FlagEmbedding import FlagReranker
    reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
    scores = reranker.compute_score([[q, p1], [q, p2]], normalize=True)

주의 — compute_score는 쌍이 하나면 float, 여럿이면 list를 돌려준다.
      normalize=True를 주면 sigmoid를 거쳐 0~1로 들어온다. 우리는 항상 켠다.

단계별 후보를 전부 남긴다. 나중에 "어느 경로가 정답 청크를 물어왔는가"를
분석하기 위한 필수 데이터다. (명세서 §04 S5)

실행:
    python -m rag_proto.s5_retrieve "질문"
    python -m rag_proto.s5_retrieve "질문" --fake
"""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass, field

from .config import Config, load
from .s3_embed import BGEM3Embedder, Embedder, HashEmbedder, load_chunks
from .s4_index import search as vector_search

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
_CAMEL_RE = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")


def tokenize(text: str) -> list[str]:
    """
    BM25용 토크나이저.

    식별자를 통째로 유지하면서 CamelCase 조각도 함께 넣는다.
    TemperatureSetpoint → ["temperaturesetpoint", "temperature", "setpoint"]
    이렇게 해야 "temperature setpoint"라고 물어도, 식별자를 정확히 적어도 둘 다 걸린다.
    """
    tokens: list[str] = []
    for raw in _TOKEN_RE.findall(text):
        tokens.append(raw.lower())
        parts = _CAMEL_RE.findall(raw)
        if len(parts) > 1:
            tokens.extend(p.lower() for p in parts)
    return tokens


@dataclass
class Candidate:
    chunk_id: str
    text: str
    source_path: str
    metadata: dict = field(default_factory=dict)
    rerank_score: float | None = None


@dataclass
class RetrievalResult:
    """단계별 후보를 전부 보존한다. 답변 JSON의 retrieved 블록이 된다."""
    bm25: list[str]
    vector: list[str]
    fused: list[str]
    reranked: list[str]
    candidates: list[Candidate]
    # 실제 검색에 걸린 시간. CachedRetriever가 결과를 재사용해도 이 값을 그대로
    # 넘겨서, 답변 레코드의 검색 지연이 캐시 덕에 0ms로 찍히지 않게 한다.
    elapsed_ms: int = 0


def where_matches(metadata: dict, where: dict | None) -> bool:
    """
    Chroma의 where 절과 같은 의미로 로컬 메타데이터를 평가한다.

    BM25는 Chroma를 거치지 않으므로, 벡터 검색과 동일한 스코프 제약을
    받으려면 이 함수로 별도 평가해야 한다. $and/$or/$eq/$ne/$in/$nin과
    평문 등치({"key": "value"})를 지원한다. device_type처럼 리스트 값인
    필드는 "값이 리스트 안에 있으면 매치"로 취급한다.
    """
    if not where:
        return True
    if "$and" in where:
        return all(where_matches(metadata, cond) for cond in where["$and"])
    if "$or" in where:
        return any(where_matches(metadata, cond) for cond in where["$or"])

    for key, cond in where.items():
        value = metadata.get(key)
        values = value if isinstance(value, list) else [value]
        if isinstance(cond, dict):
            op, operand = next(iter(cond.items()))
            if op == "$eq":
                ok = operand in values
            elif op == "$ne":
                ok = operand not in values
            elif op == "$in":
                ok = any(v in operand for v in values)
            elif op == "$nin":
                ok = not any(v in operand for v in values)
            else:
                raise ValueError(f"지원하지 않는 where 연산자: {op}")
        else:
            ok = cond in values
        if not ok:
            return False
    return True


class BM25Index:
    def __init__(self, chunks: list[dict]):
        from rank_bm25 import BM25Okapi

        self.chunks = chunks
        self.ids = [c["chunk_id"] for c in chunks]
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])

    def search(self, query: str, k: int, where: dict | None = None) -> list[str]:
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: -scores[i])
        results: list[str] = []
        for i in order:
            if scores[i] <= 0:
                break
            if not where_matches(self.chunks[i], where):
                continue
            results.append(self.ids[i])
            if len(results) >= k:
                break
        return results


def reciprocal_rank_fusion(rankings: list[list[str]], rrf_k: int = 60) -> list[str]:
    """
    RRF: 각 순위표에서 1/(rrf_k + rank)를 더한다.
    점수 스케일이 다른 BM25와 코사인 유사도를 순위만으로 섞을 수 있다.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, start=1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (rrf_k + rank)
    return sorted(scores, key=lambda c: -scores[c])


class Reranker:
    def __init__(self, model_name: str, device: str = "auto"):
        from FlagEmbedding import FlagReranker

        self.model = FlagReranker(model_name, use_fp16=(device != "cpu"))

    def score(self, query: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        raw = self.model.compute_score(
            [[query, p] for p in passages], normalize=True
        )
        # 쌍이 하나면 float를 돌려준다
        return [float(raw)] if isinstance(raw, (int, float)) else [float(s) for s in raw]


class FakeReranker:
    """모델 없이 배관을 확인할 때 쓴다. 융합 순서를 그대로 유지한다."""

    def score(self, query: str, passages: list[str]) -> list[float]:
        n = len(passages)
        return [1.0 - i / max(n, 1) for i in range(n)]


class Retriever:
    def __init__(self, cfg: Config, fake: bool = False):
        self.cfg = cfg
        self.chunks = load_chunks()
        self.by_id = {c["chunk_id"]: c for c in self.chunks}
        self.bm25 = BM25Index(self.chunks)
        self.embedder: Embedder = HashEmbedder() if fake else BGEM3Embedder(cfg)
        self._check_index_dim()
        r = cfg.pipeline["retrieval"]
        self.reranker = (
            FakeReranker()
            if fake
            else Reranker(r["reranker_model"], cfg.pipeline["embedding"].get("device", "auto"))
        )

    def _check_index_dim(self) -> None:
        """
        질의 임베더와 색인의 차원이 맞는지 미리 본다.

        안 맞으면 Chroma가 InvalidArgumentError만 던져 원인을 알 수 없다.
        실제로 --fake(256차원)로 질의하면서 실제 모델(1024차원)로 만든 색인을
        조회해 전 문항이 실패한 적이 있다.
        """
        import json

        from .s3_embed import MANIFEST_PATH

        if not MANIFEST_PATH.exists():
            return
        indexed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        indexed_dim = indexed.get("dim")
        if indexed_dim and indexed_dim != self.embedder.dim:
            raise RuntimeError(
                f"차원 불일치: 색인은 {indexed_dim}차원({indexed.get('model')}),"
                f" 질의 임베더는 {self.embedder.dim}차원({self.embedder.name})입니다.\n"
                "  → 검색은 실제로 하고 LLM만 가짜로 쓰려면 --fake 대신 --fake-llm 을 쓰세요.\n"
                "  → 전부 가짜로 돌리려면 s3_embed --fake 부터 다시 실행하세요."
            )

    def retrieve(self, query: str, where: dict | None = None) -> RetrievalResult:
        r = self.cfg.pipeline["retrieval"]
        started = time.perf_counter()

        bm25_ids = self.bm25.search(query, r["bm25_k"], where=where)

        qvec = self.embedder.encode([query])[0]
        vector_hits = vector_search(self.cfg, qvec, r["vector_k"], where=where)
        vector_ids = [cid for cid, *_ in vector_hits]

        fused_ids = reciprocal_rank_fusion(
            [bm25_ids, vector_ids], rrf_k=r.get("rrf_k", 60)
        )

        # 재순위는 상위 후보에만 건다. 전체에 걸면 느리고 이득도 없다.
        pool = fused_ids[: max(r["bm25_k"], r["vector_k"])]
        passages = [self.by_id[cid]["text"] for cid in pool if cid in self.by_id]
        pool = [cid for cid in pool if cid in self.by_id]

        scores = self.reranker.score(query, passages)
        order = sorted(range(len(pool)), key=lambda i: -scores[i])[: r["rerank_top_k"]]

        candidates = [
            Candidate(
                chunk_id=pool[i],
                text=self.by_id[pool[i]]["text"],
                source_path=self.by_id[pool[i]]["source_path"],
                metadata=self.by_id[pool[i]],
                rerank_score=round(scores[i], 6),
            )
            for i in order
        ]

        return RetrievalResult(
            bm25=bm25_ids,
            vector=vector_ids,
            fused=fused_ids,
            reranked=[c.chunk_id for c in candidates],
            candidates=candidates,
            elapsed_ms=int((time.perf_counter() - started) * 1000),
        )


class CachedRetriever:
    """
    같은 질의의 검색 결과를 재사용한다.

    검색(BM25+벡터+재순위)은 결정적이라 참가자 LLM이나 반복 회차가 달라도 결과가
    같다. 본실험은 7모델 × 3회라 캐시 없이 돌리면 같은 검색을 21번씩 반복하고,
    이 노트북에선 재순위가 질의당 ~50초라 840건이면 ~12시간이 걸린다.
    System B는 하위질의 문자열 단위로 재사용된다.
    """

    def __init__(self, retriever: "Retriever"):
        self.retriever = retriever
        self._cache: dict[tuple[str, str], RetrievalResult] = {}
        self.hits = 0
        self.misses = 0

    def retrieve(self, query: str, where: dict | None = None) -> RetrievalResult:
        key = (query, json.dumps(where, sort_keys=True, ensure_ascii=False) if where else "")
        cached = self._cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        result = self.retriever.retrieve(query, where=where)
        self._cache[key] = result
        return result


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print('사용법: python -m rag_proto.s5_retrieve "질문"')
        return 1

    query = args[0]
    retriever = Retriever(load(), fake="--fake" in sys.argv)
    result = retriever.retrieve(query)

    print(f"질의        : {query}")
    print(f"BM25        : {len(result.bm25)}건  {result.bm25[:5]}")
    print(f"벡터        : {len(result.vector)}건  {result.vector[:5]}")
    print(f"융합        : {len(result.fused)}건  {result.fused[:5]}")
    print(f"재순위 top-k: {result.reranked}\n")

    for c in result.candidates:
        print(f"[{c.chunk_id}] score={c.rerank_score}  {c.source_path}")
        print(f"    {c.text[:110].replace(chr(10), ' ')}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
