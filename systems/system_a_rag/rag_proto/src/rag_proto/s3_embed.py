"""
rag_proto.s3_embed — S3. 임베딩

data/chunks.jsonl → data/embeddings.npy + data/embedding_ids.json

공식 API (확인 완료, BAAI/bge-m3 README):
    from FlagEmbedding import BGEM3FlagModel
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
    vecs = model.encode(texts, batch_size=12, max_length=8192)['dense_vecs']

encode()는 dict를 돌려주며 dense_vecs / lexical_weights / colbert_vecs 키를 가진다.
우리는 dense만 쓴다. 희소 검색은 BM25가 담당한다(S5).

모델 없이도 S3→S4→S5 배관을 검증할 수 있도록 HashEmbedder를 함께 둔다.
검색 품질은 못 보지만 차원 불일치, 메타데이터 누락 같은 구조적 오류는 잡힌다.

실행:
    python -m rag_proto.s3_embed
    python -m rag_proto.s3_embed --fake    # 모델 없이 배관만 확인
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Protocol

import numpy as np

from .config import Config, load

IN_PATH = Path("data/chunks.jsonl")
VEC_PATH = Path("data/embeddings.npy")
IDS_PATH = Path("data/embedding_ids.json")
MANIFEST_PATH = Path("data/embedding_manifest.json")


class Embedder(Protocol):
    dim: int
    name: str

    def encode(self, texts: list[str]) -> np.ndarray: ...


class BGEM3Embedder:
    """공식 FlagEmbedding 래퍼. 모델 구조·가중치는 전부 라이브러리가 담당한다."""

    name = "BAAI/bge-m3"
    dim = 1024

    def __init__(self, cfg: Config):
        from FlagEmbedding import BGEM3FlagModel

        emb = cfg.pipeline["embedding"]
        self.name = emb["model"]
        self.batch_size = emb.get("batch_size", 12)
        self.max_length = emb.get("max_length", 8192)
        self.normalize = emb.get("normalize", True)

        device = emb.get("device", "auto")
        use_fp16 = device != "cpu"  # CPU에서 fp16은 오히려 느리거나 미지원

        self.model = BGEM3FlagModel(self.name, use_fp16=use_fp16)

    def encode(self, texts: list[str]) -> np.ndarray:
        out = self.model.encode(
            texts,
            batch_size=self.batch_size,
            max_length=self.max_length,
        )
        vecs = np.asarray(out["dense_vecs"], dtype=np.float32)
        if self.normalize:
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            vecs = vecs / np.clip(norms, 1e-12, None)
        self.dim = vecs.shape[1]
        return vecs


class HashEmbedder:
    """
    결정적 가짜 임베더. 모델 다운로드 없이 파이프라인 배관을 검증한다.
    같은 텍스트는 항상 같은 벡터를 내므로 캐시·색인 동작도 그대로 확인된다.
    검색 품질은 무의미하다. 절대 실험에 쓰지 말 것.
    """

    name = "fake-hash"

    def __init__(self, dim: int = 256):
        self.dim = dim

    def encode(self, texts: list[str]) -> np.ndarray:
        vecs = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            seed = int.from_bytes(hashlib.sha256(t.encode()).digest()[:8], "big")
            vecs[i] = np.random.default_rng(seed).normal(size=self.dim)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        return vecs / np.clip(norms, 1e-12, None)


class EmbeddingCache:
    """
    청크 텍스트 해시를 키로 하는 캐시.
    청킹 규칙만 바꿨을 때 전체 재계산을 피한다. (명세서 §04 S3)
    모델명을 키에 섞어 모델 교체 시 캐시가 섞이지 않게 한다.
    """

    def __init__(self, cache_dir: Path, model_name: str):
        self.dir = Path(cache_dir) / model_name.replace("/", "_")
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, text: str) -> Path:
        return self.dir / f"{hashlib.sha256(text.encode()).hexdigest()}.npy"

    def get(self, text: str) -> np.ndarray | None:
        p = self._path(text)
        return np.load(p) if p.exists() else None

    def put(self, text: str, vec: np.ndarray) -> None:
        np.save(self._path(text), vec)


def load_chunks(path: Path = IN_PATH) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def embed_all(
    chunks: list[dict], embedder: Embedder, cache: EmbeddingCache | None = None
) -> tuple[np.ndarray, list[str], dict]:
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]

    vectors: list[np.ndarray | None] = [None] * len(texts)
    todo_idx: list[int] = []

    if cache:
        for i, t in enumerate(texts):
            hit = cache.get(t)
            if hit is not None:
                vectors[i] = hit
            else:
                todo_idx.append(i)
    else:
        todo_idx = list(range(len(texts)))

    started = time.perf_counter()
    if todo_idx:
        fresh = embedder.encode([texts[i] for i in todo_idx])
        for slot, i in enumerate(todo_idx):
            vectors[i] = fresh[slot]
            if cache:
                cache.put(texts[i], fresh[slot])
    elapsed = time.perf_counter() - started

    matrix = np.vstack([v for v in vectors if v is not None]).astype(np.float32)

    stats = {
        "total": len(texts),
        "cache_hits": len(texts) - len(todo_idx),
        "computed": len(todo_idx),
        "dim": int(matrix.shape[1]),
        "elapsed_sec": round(elapsed, 2),
        "model": embedder.name,
    }
    return matrix, ids, stats


def main() -> int:
    fake = "--fake" in sys.argv
    cfg = load()

    chunks = load_chunks()
    if not chunks:
        print("data/chunks.jsonl이 비어 있습니다. S2를 먼저 실행하세요.")
        return 1

    embedder: Embedder = HashEmbedder() if fake else BGEM3Embedder(cfg)
    cache = (
        None
        if fake
        else EmbeddingCache(cfg.pipeline["embedding"]["cache_dir"], embedder.name)
    )

    matrix, ids, stats = embed_all(chunks, embedder, cache)

    VEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(VEC_PATH, matrix)
    IDS_PATH.write_text(json.dumps(ids, ensure_ascii=False), encoding="utf-8")

    # 어떤 임베더로 만든 벡터인지 남긴다.
    # S4가 이걸 읽어 가짜 임베딩이 실험에 섞이는 것을 막는다.
    MANIFEST_PATH.write_text(
        json.dumps({**stats, "is_fake": fake}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if fake:
        print("!! 가짜 임베더 모드입니다. 검색 품질은 무의미합니다.\n")
    for k, v in stats.items():
        print(f"{k:12s}: {v}")

    # 수용 기준: 임베딩 누락 0건, 차원 일관성
    if matrix.shape[0] != len(chunks):
        print(f"\n실패: 청크 {len(chunks)}건 중 {matrix.shape[0]}건만 임베딩됨")
        return 1
    print(f"\n{VEC_PATH} 기록 완료 ({matrix.shape[0]}×{matrix.shape[1]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
