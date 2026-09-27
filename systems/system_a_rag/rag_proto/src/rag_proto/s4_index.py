"""
rag_proto.s4_index — S4. 벡터DB 색인

data/chunks.jsonl + data/embeddings.npy → data/chroma/

공식 API (확인 완료, Chroma 문서):
    client = chromadb.PersistentClient(path="...")
    col = client.get_or_create_collection(name=..., metadata={"hnsw:space": "cosine"})
    col.add(ids=[...], embeddings=[[...]], documents=[...], metadatas=[{...}])
    col.query(query_embeddings=[[...]], n_results=k,
              include=["metadatas", "documents", "distances"], where={...})

주의 1 — 메타데이터는 스칼라만 받는다.
    Chroma 메타데이터 값은 str / int / float / bool 만 허용된다.
    우리 스키마의 device_type, heading_path, identifiers는 리스트라 그대로 넣으면 터진다.
    구분자로 이어붙여 저장하고 읽을 때 되돌린다. (flatten_metadata / unflatten_metadata)

주의 2 — 컬렉션 차원은 첫 add에서 고정된다.
    이후 다른 차원을 넣으면 InvalidDimensionException이 난다.
    임베딩 모델을 바꾸면 컬렉션을 지우고 다시 만들어야 한다. (--reset)

실행:
    python -m rag_proto.s4_index
    python -m rag_proto.s4_index --reset
    python -m rag_proto.s4_index --allow-fake   # 가짜 임베딩 배관 확인용
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .config import Config, load
from .s3_embed import IDS_PATH, VEC_PATH, load_chunks

SEP = "|"
LIST_FIELDS = ("device_type", "heading_path", "identifiers")
BATCH = 500


def flatten_metadata(chunk: dict) -> dict[str, Any]:
    """리스트·None을 Chroma가 받는 스칼라로 바꾼다."""
    meta: dict[str, Any] = {
        "doc_id": chunk["doc_id"],
        "source_path": chunk["source_path"],
        "source_type": chunk["source_type"],
        "corpus_commit": chunk["corpus_commit"],
        "corpus_phase": chunk["corpus_phase"],
        "corpus_snapshot": chunk.get("corpus_snapshot") or "",
        "corpus_version": chunk.get("corpus_version") or "",
        "cluster": chunk.get("cluster") or "",
        "owner": chunk.get("owner") or "",
        "line_start": chunk.get("line_start") or 0,
        "line_end": chunk.get("line_end") or 0,
        "n_tokens": chunk.get("n_tokens") or 0,
    }
    for field in LIST_FIELDS:
        values = chunk.get(field) or []
        # 앞뒤로 구분자를 붙여 where_document 부분일치 시 경계가 흐려지지 않게 한다
        meta[field] = SEP + SEP.join(values) + SEP if values else ""
    return meta


def unflatten_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """검색 결과를 우리 스키마 형태로 되돌린다."""
    out = dict(meta)
    for field in LIST_FIELDS:
        raw = meta.get(field) or ""
        out[field] = [v for v in raw.split(SEP) if v]
    out["cluster"] = meta.get("cluster") or None
    out["owner"] = meta.get("owner") or None
    return out


def get_collection(cfg: Config, reset: bool = False):
    import chromadb
    from chromadb.config import Settings

    vs = cfg.pipeline["vectorstore"]
    client = chromadb.PersistentClient(
        path=vs["persist_dir"],
        settings=Settings(anonymized_telemetry=False),
    )
    if reset:
        try:
            client.delete_collection(vs["collection"])
        except Exception:
            pass
    return client.get_or_create_collection(
        name=vs["collection"],
        metadata={"hnsw:space": vs.get("distance", "cosine")},
    )


def check_manifest(allow_fake: bool = False) -> dict:
    """
    가짜 임베딩이 실험에 섞이는 것을 막는다.

    S3가 --fake로 실패하거나 중단된 뒤 이전 벡터가 남아 있으면, S4는 그것이
    언제 무엇으로 만들어진 건지 알 수 없어 그대로 색인해버린다. 실제로
    S3 실패 직후 S4가 256차원 가짜 벡터를 색인한 사고가 있었다.
    """
    from .s3_embed import MANIFEST_PATH

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"{MANIFEST_PATH}가 없습니다. S3를 먼저 실행하세요."
        )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    if manifest.get("is_fake") and not allow_fake:
        raise RuntimeError(
            f"가짜 임베딩({manifest.get('model')})은 색인할 수 없습니다.\n"
            "  실제 실험용이면 python -m rag_proto.s3_embed 를 모델과 함께 실행하세요.\n"
            "  배관 확인 목적이면 --allow-fake 를 붙이세요."
        )
    return manifest


def index(cfg: Config, reset: bool = False, allow_fake: bool = False) -> dict:
    manifest = check_manifest(allow_fake)
    chunks = load_chunks()
    vectors = np.load(VEC_PATH)
    ids: list[str] = json.loads(IDS_PATH.read_text(encoding="utf-8"))

    if len(chunks) != len(ids) or vectors.shape[0] != len(ids):
        raise ValueError(
            f"개수 불일치: chunks={len(chunks)} ids={len(ids)} vectors={vectors.shape[0]}\n"
            "S2와 S3를 다시 실행하세요."
        )

    by_id = {c["chunk_id"]: c for c in chunks}
    col = get_collection(cfg, reset=reset)

    for start in range(0, len(ids), BATCH):
        sl = slice(start, start + BATCH)
        batch_ids = ids[sl]
        col.upsert(
            ids=batch_ids,
            embeddings=[v.tolist() for v in vectors[sl]],
            documents=[by_id[i]["text"] for i in batch_ids],
            metadatas=[flatten_metadata(by_id[i]) for i in batch_ids],
        )

    return {
        "indexed": len(ids),
        "dim": int(vectors.shape[1]),
        "count": col.count(),
        "embedder": manifest.get("model"),
        "is_fake": bool(manifest.get("is_fake")),
    }


def search(cfg: Config, query_vector: np.ndarray, k: int, where: dict | None = None):
    """벡터 검색. 반환은 (chunk_id, score, metadata, document) 목록."""
    col = get_collection(cfg)
    res = col.query(
        query_embeddings=[query_vector.tolist()],
        n_results=k,
        where=where or None,
        include=["metadatas", "documents", "distances"],
    )
    out = []
    for cid, dist, meta, doc in zip(
        res["ids"][0], res["distances"][0], res["metadatas"][0], res["documents"][0]
    ):
        # cosine space에서 distance는 1 - similarity
        out.append((cid, 1.0 - float(dist), unflatten_metadata(meta), doc))
    return out


def main() -> int:
    cfg = load()
    try:
        stats = index(
            cfg,
            reset="--reset" in sys.argv,
            allow_fake="--allow-fake" in sys.argv,
        )
    except (RuntimeError, FileNotFoundError) as e:
        print(e)
        return 1

    for k, v in stats.items():
        print(f"{k:10s}: {v}")

    if stats["count"] != stats["indexed"]:
        print("\n경고: 색인 건수와 컬렉션 건수가 다릅니다.")
        print("      이전 색인이 남아 있을 수 있습니다. --reset 후 재실행하세요.")
        return 1
    print(f"\n{cfg.pipeline['vectorstore']['persist_dir']} 색인 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
