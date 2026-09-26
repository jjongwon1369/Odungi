"""
rag_proto.ask — 단일 질의 엔드포인트

질의 1개 → 6단계 관통 → 답변 JSON 1건

명세서 §08 DoD: 이 명령이 로컬에서 1분 내에 끝나야 한다.
발표 시연도 이 명령 하나로 끝난다.

실행:
    python -m rag_proto.ask "질문"
    python -m rag_proto.ask "질문" --fake-llm  # 검색은 실제, LLM만 가짜 (API 키 없을 때)
    python -m rag_proto.ask "질문" --fake      # 검색·LLM 모두 가짜 (색인도 --fake 여야 함)
    python -m rag_proto.ask "질문" --json      # 답변 JSON 전체 출력
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from .config import Config, load
from .s5_retrieve import Retriever
from .s6_generate import generate, make_client
from .schema import (
    AnswerRecord,
    Citation,
    CorpusPhase,
    LatencyMs,
    QueryMode,
    RetrievedCandidates,
    SystemName,
    extract_identifiers,
    find_dangling_citations,
)


class Pipeline:
    """
    검색기와 LLM을 한 번만 로드해 재사용한다. run_eval이 이걸 쓴다.

    가짜 모드가 둘로 나뉜다. 색인은 실제 임베더로 만들어두고 LLM만 없는 상황이
    흔하기 때문이다(API 키 대기 중). 이때 fake_retrieval까지 켜면 질의 벡터
    차원이 색인과 달라 Chroma가 InvalidArgumentError를 낸다.
    """

    def __init__(self, cfg: Config, fake: bool = False, fake_llm: bool | None = None):
        self.cfg = cfg
        self.fake_retrieval = fake
        self.fake_llm = fake if fake_llm is None else fake_llm
        self.retriever = Retriever(cfg, fake=self.fake_retrieval)
        self.client = make_client(cfg, fake=self.fake_llm)

    @property
    def fake(self) -> bool:
        return self.fake_retrieval or self.fake_llm

    def ask(self, question: str, qid: str = "ad-hoc", run: int = 1) -> AnswerRecord:
        gen_cfg = self.cfg.pipeline["generation"]
        id_cfg = self.cfg.pipeline["identifiers"]

        t0 = time.perf_counter()
        result = self.retriever.retrieve(question)
        t1 = time.perf_counter()

        answer, usage = generate(question, result.candidates, self.client)
        t2 = time.perf_counter()

        record = AnswerRecord(
            qid=qid,
            model=self.client.name,
            run=run,
            system=SystemName.RAG,
            query_mode=QueryMode(self.cfg.pipeline["query"]["mode"]),
            question=question,
            answer=answer,
            citations=[
                Citation(
                    chunk_id=c.chunk_id,
                    source_path=c.source_path,
                    rerank_score=c.rerank_score,
                )
                for c in result.candidates
            ],
            retrieved=RetrievedCandidates(
                bm25=result.bm25,
                vector=result.vector,
                fused=result.fused,
                reranked=result.reranked,
            ),
            identifiers_in_answer=extract_identifiers(
                answer, id_cfg["patterns"], id_cfg.get("stopwords", [])
            ),
            latency_ms=LatencyMs(
                retrieve=int((t1 - t0) * 1000),
                generate=int((t2 - t1) * 1000),
                total=int((t2 - t0) * 1000),
            ),
            tokens=usage,
            corpus_commit=self.cfg.commit,
            corpus_phase=self.cfg.phase,
            corpus_snapshot=self.cfg.corpus_snapshot,
            corpus_version=self.cfg.corpus_version,
            config_hash=self.cfg.config_hash,
        )

        # 명세서 §08 DoD: dangling citation 0건
        dangling = find_dangling_citations(record, gen_cfg["citation_pattern"])
        if dangling:
            record.error = f"dangling_citations: {dangling}"
        return record


def print_human(record: AnswerRecord, fake: bool) -> None:
    if fake:
        print("!! 가짜 모드입니다. 답변 품질은 무의미합니다.\n")

    print(f"질의   : {record.question}\n")
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
        print('사용법: python -m rag_proto.ask "질문"')
        return 1

    fake = "--fake" in sys.argv
    fake_llm = fake or "--fake-llm" in sys.argv
    pipeline = Pipeline(load(), fake=fake, fake_llm=fake_llm)
    record = pipeline.ask(args[0])

    if "--json" in sys.argv:
        print(json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2))
    else:
        print_human(record, pipeline.fake)
    return 1 if record.error else 0


if __name__ == "__main__":
    sys.exit(main())
