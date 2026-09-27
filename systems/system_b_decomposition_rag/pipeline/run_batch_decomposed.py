"""
System B 본실험 배치 — 참가자 LLM × 반복 회차 × 문항.

System A의 배치 러너(rag_proto.run_eval.main_batch)를 그대로 쓰고 파이프라인만
DecompositionPipeline으로 바꾼다. 인자·이어하기·즉시 기록·검색 캐시 동작은 A와 같다.
결과 디렉터리 이름에 _batch_decomposed가 붙어 A 결과와 구분된다.

실행 (system_a_rag/rag_proto 디렉터리에서, 같은 venv):
    python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py --smoke
    python ../../system_b_decomposition_rag/pipeline/run_batch_decomposed.py \\
        --participants all --runs 3 --questions ../../../benchmark/questions_v1.jsonl
"""

from __future__ import annotations

import sys

from ask_decomposed import DecompositionPipeline  # rag_proto를 sys.path에 올린다

from rag_proto import run_eval  # noqa: E402
from rag_proto.config import load  # noqa: E402


def main() -> int:
    cfg = load()
    fake_llm = "--fake" in sys.argv or "--fake-llm" in sys.argv

    def factory(client, retriever):
        return DecompositionPipeline(cfg, fake_llm=fake_llm, retriever=retriever, client=client)

    return run_eval.main_batch(pipeline_factory=factory, tag="_decomposed")


if __name__ == "__main__":
    sys.exit(main())
