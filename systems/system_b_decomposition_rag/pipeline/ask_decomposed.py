"""
System B — 분해형 RAG 엔드포인트.

질문 1개 → 하위질의 분해 → 하위질의마다 System A의 Retriever로 검색
→ 근거 병합(chunk_id 중복은 최고 점수만 채택) → 생성.

AnswerRecord는 System A와 완전히 같은 스키마를 쓴다. A/B 구분은
query_mode 필드(simple vs decomposed)만으로 한다 — 스키마 변경 없음
(CLAUDE.md: "B는 A의 검색 재사용", "query_mode 필드로 구분").
별도 청킹·색인을 만들지 않고 A가 이미 만든 data/chroma, data/chunks.jsonl을
그대로 쓴다.

실행 (system_a_rag/rag_proto와 같은 venv 필요 — FlagEmbedding, chromadb 등):
    python ask_decomposed.py "질문"
    python ask_decomposed.py "질문" --fake-llm   # 검색은 실제, 분해·생성만 가짜
    python ask_decomposed.py "질문" --fake        # 전부 가짜
    python ask_decomposed.py "질문" --json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# System A(rag_proto)를 그대로 재사용한다. 이 파일이
# systems/system_b_decomposition_rag/pipeline/ 에 있으므로, 형제 폴더인
# systems/system_a_rag/rag_proto/src 를 sys.path에 추가한다.
_RAG_PROTO_SRC = Path(__file__).resolve().parents[2] / "system_a_rag" / "rag_proto" / "src"
if str(_RAG_PROTO_SRC) not in sys.path:
    sys.path.insert(0, str(_RAG_PROTO_SRC))
_DECOMPOSITION_DIR = Path(__file__).resolve().parent.parent / "decomposition"
if str(_DECOMPOSITION_DIR) not in sys.path:
    sys.path.insert(0, str(_DECOMPOSITION_DIR))

from rag_proto.config import Config, load  # noqa: E402
from rag_proto.s5_retrieve import Candidate, Retriever  # noqa: E402
from rag_proto.s6_generate import generate, make_client  # noqa: E402
from rag_proto.schema import (  # noqa: E402
    AnswerRecord,
    Citation,
    LatencyMs,
    QueryMode,
    RetrievedCandidates,
    SystemName,
    TokenUsage,
    extract_identifiers,
    find_dangling_citations,
)

from decompose import make_decomposer  # noqa: E402


def merge_candidates(per_subq_candidates: list[list[Candidate]], top_k: int) -> list[Candidate]:
    """
    하위질의별 재순위 후보를 병합한다.

    같은 chunk_id가 여러 하위질의에서 나오면 점수를 더하지 않고 최댓값만
    취한다 — 합산하면 하위질의 개수가 많을수록 같은 청크가 유리해져
    실제 관련성과 무관하게 점수가 부풀려진다. 병합 후 점수 내림차순 top_k.
    """
    best: dict[str, Candidate] = {}
    for candidates in per_subq_candidates:
        for c in candidates:
            cur = best.get(c.chunk_id)
            if cur is None or (c.rerank_score or 0.0) > (cur.rerank_score or 0.0):
                best[c.chunk_id] = c
    ranked = sorted(best.values(), key=lambda c: -(c.rerank_score or 0.0))
    return ranked[:top_k]


def add_usage(a: TokenUsage, b: TokenUsage | None) -> TokenUsage:
    """호출 여러 번의 토큰을 열별로 더한다. 4열은 각자 유지 — 열끼리 합치지 않는다."""
    if b is None:
        return a
    return TokenUsage(**{k: getattr(a, k) + getattr(b, k) for k in TokenUsage.model_fields})


class DecompositionPipeline:
    def __init__(
        self,
        cfg: Config,
        fake: bool = False,
        fake_llm: bool | None = None,
        retriever=None,
        client=None,
    ):
        # retriever/client를 넘기면 그대로 쓴다(배치 실행에서 CachedRetriever 공유).
        # 분해 LLM은 생성과 같은 참가자 LLM을 쓴다 — 모델 변수를 한 시스템 안에서 섞지 않는다.
        self.cfg = cfg
        self.fake_retrieval = fake
        self.fake_llm = fake if fake_llm is None else fake_llm
        self.retriever = retriever or Retriever(cfg, fake=self.fake_retrieval)
        self.client = client or make_client(cfg, fake=self.fake_llm)
        self.decomposer = make_decomposer(fake=self.fake_llm, client=None if self.fake_llm else self.client)
        self.last_subqueries: list[str] = []

    @property
    def fake(self) -> bool:
        return self.fake_retrieval or self.fake_llm

    @property
    def query_mode(self) -> QueryMode:
        return QueryMode.DECOMPOSED

    def ask(self, question: str, qid: str = "ad-hoc", run: int = 1) -> AnswerRecord:
        gen_cfg = self.cfg.pipeline["generation"]
        id_cfg = self.cfg.pipeline["identifiers"]
        max_subq = self.cfg.pipeline["query"]["decompose_max_subq"]
        rerank_top_k = self.cfg.pipeline["retrieval"]["rerank_top_k"]

        t0 = time.perf_counter()
        subqueries, decompose_usage = self.decomposer.decompose(question, max_subq)
        decompose_ms = int((time.perf_counter() - t0) * 1000)
        self.last_subqueries = subqueries

        bm25_all: list[str] = []
        vector_all: list[str] = []
        fused_all: list[str] = []
        per_subq_candidates: list[list[Candidate]] = []
        retrieve_ms = 0
        for subq in subqueries:
            result = self.retriever.retrieve(subq)
            # 캐시로 재사용돼도 실제 검색 시간을 합산한다(하위질의는 순차 검색)
            retrieve_ms += result.elapsed_ms
            bm25_all.extend(result.bm25)
            vector_all.extend(result.vector)
            fused_all.extend(result.fused)
            per_subq_candidates.append(result.candidates)

        candidates = merge_candidates(per_subq_candidates, rerank_top_k)

        t1 = time.perf_counter()
        answer, generate_usage = generate(question, candidates, self.client)
        # LatencyMs엔 분해 칸이 없어(동결 스키마) 분해도 LLM 호출이므로 generate에 포함한다
        generate_ms = decompose_ms + int((time.perf_counter() - t1) * 1000)
        usage = add_usage(generate_usage, decompose_usage)

        record = AnswerRecord(
            qid=qid,
            model=self.client.name,
            run=run,
            system=SystemName.RAG,
            query_mode=QueryMode.DECOMPOSED,
            question=question,
            answer=answer,
            citations=[
                Citation(chunk_id=c.chunk_id, source_path=c.source_path, rerank_score=c.rerank_score)
                for c in candidates
            ],
            retrieved=RetrievedCandidates(
                bm25=bm25_all,
                vector=vector_all,
                fused=fused_all,
                reranked=[c.chunk_id for c in candidates],
            ),
            identifiers_in_answer=extract_identifiers(
                answer, id_cfg["patterns"], id_cfg.get("stopwords", [])
            ),
            latency_ms=LatencyMs(
                retrieve=retrieve_ms,
                generate=generate_ms,
                total=retrieve_ms + generate_ms,
            ),
            tokens=usage,
            corpus_commit=self.cfg.commit,
            corpus_phase=self.cfg.phase,
            corpus_snapshot=self.cfg.corpus_snapshot,
            corpus_version=self.cfg.corpus_version,
            config_hash=self.cfg.config_hash,
        )

        dangling = find_dangling_citations(record, gen_cfg["citation_pattern"])
        if dangling:
            record.error = f"dangling_citations: {dangling}"
        return record


def print_human(record: AnswerRecord, fake: bool, subqueries: list[str]) -> None:
    if fake:
        print("!! 가짜 모드입니다. 답변 품질은 무의미합니다.\n")

    print(f"질의   : {record.question}")
    print(f"하위질의: {subqueries}\n")
    print(f"답변   : {record.answer}\n")
    print("근거   :")
    for c in record.citations:
        print(f"  [{c.chunk_id}] score={c.rerank_score}  {c.source_path}")

    lat = record.latency_ms
    print(f"\n지연   : 검색 {lat.retrieve}ms + 생성 {lat.generate}ms = {lat.total}ms")
    t = record.tokens
    print(
        f"토큰   : uncached={t.uncached_input} cache_creation={t.cache_creation} "
        f"cache_read={t.cache_read} output={t.output}"
    )
    if record.identifiers_in_answer:
        print(f"식별자 : {record.identifiers_in_answer}")
    if record.error:
        print(f"\n오류   : {record.error}")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print('사용법: python ask_decomposed.py "질문"')
        return 1

    fake = "--fake" in sys.argv
    fake_llm = fake or "--fake-llm" in sys.argv
    pipeline = DecompositionPipeline(load(), fake=fake, fake_llm=fake_llm)
    record = pipeline.ask(args[0])

    if "--json" in sys.argv:
        payload = record.model_dump(mode="json")
        payload["subqueries"] = pipeline.last_subqueries
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(record, pipeline.fake, pipeline.last_subqueries)
    return 1 if record.error else 0


if __name__ == "__main__":
    sys.exit(main())
