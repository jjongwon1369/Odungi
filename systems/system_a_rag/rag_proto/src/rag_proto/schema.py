"""
rag_proto.schema — 데이터 계약 (동결 대상)

명세서 §05. 이 파일의 스키마는 프로젝트 종료까지 유지한다.
내부 구현(청킹 방식, 리트리버 조합)은 얼마든지 바뀌어도 되지만,
Chunk와 AnswerRecord의 필드는 RAG와 LLM Wiki가 공유하므로 임의 변경 금지.

변경이 필요하면 명세서 버전을 올리고 팀 합의를 거칠 것.
"""

from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "0.3"


# --------------------------------------------------------------------------
# 열거형
# --------------------------------------------------------------------------

class SourceType(str, Enum):
    """
    팀 코퍼스 documents.jsonl의 (source_role, doc_type) → source_type 매핑:
      specification/xml, sdk_codegen/xml → DATAMODEL_XML
      documentation/md                    → PROSE
      implementation·example/cpp·h·cmake  → CODE
      example/matter·zap                  → IDL
    """
    PROSE = "prose"
    DATAMODEL_XML = "datamodel_xml"
    IDL = "idl"
    CODE = "code"
    SPEC_PDF = "spec_pdf"


class CorpusPhase(str, Enum):
    SAMPLE = "sample"          # 개인별 임의 샘플. 비교 실험에 사용 금지
    INTEGRATED = "integrated"  # 통합 정리본. 이후 수치만 논문에 인용


class SystemName(str, Enum):
    RAG = "rag"
    WIKI = "wiki"


class QueryMode(str, Enum):
    SIMPLE = "simple"
    DECOMPOSED = "decomposed"


class QueryTier(str, Enum):
    """질의 유형. 기본안 배분: 식별자형 8 / 의미형 6 / 다중홉 4 / 대조군 2"""
    IDENTIFIER = "identifier"   # 특정 속성·커맨드 이름을 직접 묻는 질문
    SEMANTIC = "semantic"       # 개념·절차를 묻는 질문
    MULTIHOP = "multihop"       # 두 문서 이상을 엮어야 답이 나오는 질문
    CONTROL = "control"         # 코퍼스에 없는 내용. 환각 검증용 대조군


# --------------------------------------------------------------------------
# 코퍼스 / 청크
# --------------------------------------------------------------------------

class CorpusDoc(BaseModel):
    """S1 출력. 문서 1건 = corpus.jsonl 1줄"""
    doc_id: str
    source_path: str                       # repo_root 기준 상대 경로
    source_type: SourceType
    heading_path: list[str] = Field(default_factory=list)
    device_type: list[str] = Field(default_factory=list)
    cluster: str | None = None             # Phase 1에서는 null 허용
    text: str
    n_chars: int
    corpus_commit: str
    corpus_phase: CorpusPhase
    corpus_snapshot: str | None = None   # 팀 snapshot_id (corpus-v0.1:...)
    corpus_version: str | None = None    # 팀 corpus_version (0.1, 1.0 ...)
    owner: str | None = None               # Phase 1 전용


class Chunk(BaseModel):
    """S2 출력. 청크 1건 = chunks.jsonl 1줄"""
    chunk_id: str
    doc_id: str
    source_path: str
    source_type: SourceType
    heading_path: list[str] = Field(default_factory=list)
    device_type: list[str] = Field(default_factory=list)
    cluster: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    identifiers: list[str] = Field(default_factory=list)
    text: str
    n_tokens: int
    corpus_commit: str
    corpus_phase: CorpusPhase
    corpus_snapshot: str | None = None   # 팀 snapshot_id (corpus-v0.1:...)
    corpus_version: str | None = None    # 팀 corpus_version (0.1, 1.0 ...)
    owner: str | None = None

    @field_validator("chunk_id")
    @classmethod
    def _no_whitespace(cls, v: str) -> str:
        # chunk_id는 생성 답변에 [chunk_id] 형태로 박히므로 공백이 있으면 파싱이 깨진다
        if re.search(r"\s", v):
            raise ValueError(f"chunk_id에 공백을 쓸 수 없습니다: {v!r}")
        return v


# --------------------------------------------------------------------------
# 답변 (System A / B 공통)
# --------------------------------------------------------------------------

class Citation(BaseModel):
    chunk_id: str
    source_path: str
    rerank_score: float | None = None


class RetrievedCandidates(BaseModel):
    """
    단계별 후보를 전부 남긴다. 나중에 "어느 경로가 정답 청크를 물어왔는가"를
    분석하기 위한 필수 데이터. (명세서 §04 S5)
    LLM Wiki는 bm25/vector/fused를 비우고 wiki_pages에 열람 이력을 넣는다.
    """
    bm25: list[str] = Field(default_factory=list)
    vector: list[str] = Field(default_factory=list)
    fused: list[str] = Field(default_factory=list)
    reranked: list[str] = Field(default_factory=list)
    wiki_pages: list[str] = Field(default_factory=list)


class TokenUsage(BaseModel):
    """
    4열 분리 기록. 절대 합산 필드로 바꾸지 말 것.

    베이스라인 논문(arXiv 2605.18490)은 위키 ingest 토큰을 한 필드에 뭉쳐
    기록한 탓에 비용 가설의 절반을 판정하지 못했다. 캐시 읽기는 기본 입력
    요율의 약 10%로 과금되므로 액면 합산은 청구액을 자릿수 단위로 과대 계상한다.
    논문이 복제 연구자에게 남긴 방법론 노트가 바로 이 4열 기록이다.
    """
    uncached_input: int = 0
    cache_creation: int = 0
    cache_read: int = 0
    output: int = 0

    def billable_equivalent(self, cache_read_rate: float = 0.1) -> float:
        """청구 환산 입력 토큰. 비교 리포트에서만 쓰고 원자료는 4열 그대로 보존한다."""
        return (
            self.uncached_input
            + self.cache_creation
            + self.cache_read * cache_read_rate
        )


class LatencyMs(BaseModel):
    retrieve: int = 0
    rerank: int = 0
    generate: int = 0
    total: int = 0


class AnswerRecord(BaseModel):
    """
    runs/<ts>/answers.jsonl 1줄. RAG와 LLM Wiki가 동일 스키마로 출력한다.
    평가 스크립트는 이 파일 하나만 읽는다.
    """
    schema_version: str = SCHEMA_VERSION
    qid: str
    system: SystemName
    query_mode: QueryMode = QueryMode.SIMPLE
    question: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved: RetrievedCandidates = Field(default_factory=RetrievedCandidates)
    identifiers_in_answer: list[str] = Field(default_factory=list)
    latency_ms: LatencyMs = Field(default_factory=LatencyMs)
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    corpus_commit: str
    corpus_phase: CorpusPhase
    corpus_snapshot: str | None = None   # 팀 snapshot_id (corpus-v0.1:...)
    corpus_version: str | None = None    # 팀 corpus_version (0.1, 1.0 ...)
    config_hash: str
    error: str | None = None


# --------------------------------------------------------------------------
# 질의셋
# --------------------------------------------------------------------------

class EvalQuery(BaseModel):
    """data/queries.jsonl 1줄. Phase 1에서는 gold 필드를 비워두어도 된다."""
    qid: str
    tier: QueryTier
    question: str
    gold_answer: str | None = None
    gold_identifiers: list[str] = Field(default_factory=list)
    gold_doc_ids: list[str] = Field(default_factory=list)
    note: str | None = None


# --------------------------------------------------------------------------
# 헬퍼
# --------------------------------------------------------------------------

def extract_identifiers(
    text: str,
    patterns: list[str],
    stopwords: list[str] | None = None,
) -> list[str]:
    """
    식별자 무손실 검증의 기반. 각 단계 출력에 이 함수를 적용해 집합을 비교한다.
    패턴은 pipeline.yaml의 identifiers.patterns에서 주입한다.
    """
    stop = set(stopwords or [])
    found: list[str] = []
    seen: set[str] = set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            tok = m.group(0)
            if tok in stop or tok in seen:
                continue
            seen.add(tok)
            found.append(tok)
    return sorted(found)


def config_hash(pipeline_config: dict[str, Any]) -> str:
    """
    pipeline.yaml 내용의 해시. 답변 JSON에 기록해
    "어떤 설정으로 낸 수치인가"를 사후 추적한다.
    """
    canonical = json.dumps(pipeline_config, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def parse_cited_chunk_ids(answer: str, pattern: str) -> list[str]:
    """답변 본문에서 [chunk_id]를 추출한다. citation 무결성 검사의 입력."""
    return list(dict.fromkeys(re.findall(pattern, answer)))


def find_dangling_citations(record: AnswerRecord, pattern: str) -> list[str]:
    """
    답변이 인용한 chunk_id 중 실제 검색 결과에 없는 것.
    명세서 §08 DoD: 이 함수의 반환이 항상 빈 리스트여야 한다.
    """
    cited = set(parse_cited_chunk_ids(record.answer, pattern))
    available = {c.chunk_id for c in record.citations}
    available |= set(record.retrieved.reranked)
    return sorted(cited - available)
