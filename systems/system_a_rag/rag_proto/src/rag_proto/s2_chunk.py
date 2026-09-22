"""
rag_proto.s2_chunk — S2. 청킹

data/corpus.jsonl → data/chunks.jsonl (청크 1건 = 1줄)

명세서 §04 S2. source_type별로 규칙이 다르다.
  - prose : 마크다운 헤딩 단위 1차 분할 → 초과분만 문단 기준 재분할
  - code  : 펜스 코드 블록은 절대 쪼개지 않는다

핵심 불변식(§01 원칙 3): 원문 식별자 집합 ⊆ 청크 식별자 집합.
S2가 식별자를 하나라도 삼키면 그 뒤 모든 단계가 오염된다.

실행:
    python -m rag_proto.s2_chunk
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config, load
from .schema import Chunk, CorpusDoc, SourceType, extract_identifiers

IN_PATH = Path("data/corpus.jsonl")
OUT_PATH = Path("data/chunks.jsonl")

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def count_tokens(text: str) -> int:
    """
    토큰 수 추정. tiktoken이 있으면 쓰고, 없으면 문자 기반으로 근사한다.
    한글은 영문보다 토큰 밀도가 높으므로 가중치를 다르게 준다.
    """
    try:
        import tiktoken

        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        hangul = sum(1 for c in text if "\uac00" <= c <= "\ud7a3")
        return int(hangul * 0.7 + (len(text) - hangul) / 4) + 1


@dataclass
class Segment:
    """헤딩 또는 코드 블록으로 구분된 원문 조각."""
    heading_path: list[str]
    source_type: SourceType
    lines: list[str] = field(default_factory=list)
    line_start: int = 0

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def line_end(self) -> int:
        return self.line_start + len(self.lines) - 1


def split_segments(text: str) -> list[Segment]:
    """
    마크다운을 헤딩 계층과 코드 블록으로 쪼갠다.
    코드 블록은 별도 Segment가 되며 이후 절대 분할되지 않는다.
    """
    segments: list[Segment] = []
    stack: list[str] = []
    current = Segment(heading_path=[], source_type=SourceType.PROSE, line_start=1)
    in_fence = False
    fence_marker = ""

    def flush(seg: Segment) -> None:
        if seg.text.strip():
            segments.append(seg)

    for idx, line in enumerate(text.splitlines(), start=1):
        fence = _FENCE_RE.match(line)

        if in_fence:
            current.lines.append(line)
            if fence and line.strip().startswith(fence_marker):
                in_fence = False
                flush(current)
                current = Segment(list(stack), SourceType.PROSE, line_start=idx + 1)
            continue

        if fence:
            flush(current)
            fence_marker = fence.group(1)
            in_fence = True
            current = Segment(list(stack), SourceType.CODE, [line], line_start=idx)
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            flush(current)
            level = len(heading.group(1))
            title = heading.group(2).strip()
            stack = stack[: level - 1] + [title]
            current = Segment(list(stack), SourceType.PROSE, line_start=idx)
            continue

        current.lines.append(line)

    flush(current)
    return segments


def split_prose(text: str, target: int, overlap: int) -> list[str]:
    """
    문단 경계로 자르고 overlap만큼 겹친다.
    한 문단이 통째로 target을 넘으면 그대로 둔다 — 문장 중간을 자르면
    식별자가 쪼개질 위험이 있고, 그게 토큰 상한보다 중요하다.
    """
    if count_tokens(text) <= target:
        return [text]

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    buf: list[str] = []

    for para in paragraphs:
        candidate = buf + [para]
        if buf and count_tokens("\n\n".join(candidate)) > target:
            pieces.append("\n\n".join(buf))
            tail = buf[-1]
            buf = [tail, para] if count_tokens(tail) <= overlap else [para]
        else:
            buf = candidate

    if buf:
        pieces.append("\n\n".join(buf))
    return pieces


def _el_label(el: "ET.Element") -> str:
    """<attribute id="0x0000" name="TemperatureSetpoint"> → 'attribute TemperatureSetpoint (0x0000)'"""
    parts = [el.tag]
    name = el.get("name")
    if name:
        parts.append(name)
    el_id = el.get("id") or el.get("code")
    label = " ".join(parts)
    return f"{label} ({el_id})" if el_id else label


def _serialize(el: "ET.Element") -> str:
    import xml.etree.ElementTree as ET

    return ET.tostring(el, encoding="unicode").strip()


def split_xml_segments(text: str, target: int, max_depth: int = 2) -> list[Segment]:
    """
    Data Model XML을 구조 단위로 쪼갠다.

    루트의 직계 자식(<attributes>, <commands>, <clusters> ...)을 1차 단위로 하고,
    그것이 target을 넘으면 손자(<attribute>, <command> ...)로 한 단계 더 내려간다.
    <attribute> 하나가 두 청크로 갈라지지 않는 것을 최우선으로 한다.

    텍스트는 ET로 재직렬화되므로 들여쓰기가 원본과 달라질 수 있으나,
    식별자와 속성값은 바이트 단위로 보존된다. verify_identifiers가 이를 검증한다.
    """
    import xml.etree.ElementTree as ET

    root = None
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        # 팀 코퍼스 documents.jsonl 의 text 는 "선택된 원문 발췌"라 루트가 없거나
        # 여러 최상위 엘리먼트가 이어진 형태일 수 있다 (processed/README.md).
        # 가짜 루트로 감싸 다시 시도한다.
        try:
            root = ET.fromstring(f"<_excerpt>{text}</_excerpt>")
        except ET.ParseError:
            root = None

    if root is None:
        # 그래도 안 되면 산문처럼 문단 단위로 자른다. 통째로 한 청크가 되는 것보다 낫다.
        return [
            Segment([], SourceType.DATAMODEL_XML, part.splitlines(), 1)
            for part in split_prose(text, target, 0)
        ]

    segments: list[Segment] = []

    def walk(el: "ET.Element", path: list[str], depth: int) -> None:
        block = _serialize(el)
        children = list(el)
        too_big = count_tokens(block) > target
        if too_big and children and depth < max_depth:
            for child in children:
                walk(child, path + [_el_label(child)], depth + 1)
        else:
            segments.append(
                Segment(path, SourceType.DATAMODEL_XML, block.splitlines(), 1)
            )

    is_wrapper = root.tag == "_excerpt"
    root_label = _el_label(root)
    for child in root:
        path = [_el_label(child)] if is_wrapper else [root_label, _el_label(child)]
        walk(child, path, 1)

    if not segments:  # 자식이 없는 문서
        segments.append(
            Segment([root_label], SourceType.DATAMODEL_XML, text.splitlines(), 1)
        )
    return segments


_CPP_BLOCK_END_RE = re.compile(r"^\}")
# .zap은 pretty-printed JSON이라 닫는 중괄호가 항상 들여쓰기돼 있다. 열 위치와
# 무관하게 중괄호만(+선택적 쉼표) 있는 줄을 객체 경계로 인정한다.
_JSON_BLOCK_END_RE = re.compile(r"^\s*\},?\s*$")


def split_code_segments(
    text: str, target: int, block_end_re: re.Pattern[str] = _CPP_BLOCK_END_RE
) -> list[Segment]:
    """
    코드/구조화 텍스트를 최상위 블록 단위로 쪼갠다.
    닫는 중괄호 줄을 블록의 끝으로 보고, 그 경계에서만 자른다.
    중괄호 중간을 자르면 식별자가 맥락을 잃는다.

    C++는 열에 붙은 닫는 중괄호(^})만 최상위 경계로 인정한다.
    .zap(JSON)은 pretty-print로 들여쓰기가 깊어 열에 붙는 중괄호가 파일 끝
    하나뿐이므로, 들여쓰기 유무와 무관하게 중괄호만 있는 줄이면 경계로 인정한다
    (`block_end_re=_JSON_BLOCK_END_RE`).
    """
    lines = text.splitlines()
    segments: list[Segment] = []
    buf: list[str] = []
    start = 1

    for idx, line in enumerate(lines, start=1):
        buf.append(line)
        if block_end_re.match(line) and count_tokens("\n".join(buf)) >= target:
            segments.append(Segment([], SourceType.CODE, list(buf), start))
            buf, start = [], idx + 1

    if any(l.strip() for l in buf):
        segments.append(Segment([], SourceType.CODE, buf, start))
    return segments


def chunk_document(doc: CorpusDoc, cfg: Config) -> list[Chunk]:
    chunking = cfg.pipeline["chunking"]
    target = chunking["target_tokens"]
    overlap = chunking["overlap_tokens"]
    min_chars = chunking.get("min_chunk_chars", 50)
    prepend = chunking.get("prepend_heading_context", True)

    id_cfg = cfg.pipeline["identifiers"]
    patterns = id_cfg["patterns"]
    stopwords = id_cfg.get("stopwords", [])

    chunks: list[Chunk] = []
    seq = 0

    # source_type별로 다른 파서를 쓴다. (명세서 §04 S2)
    if doc.source_type is SourceType.DATAMODEL_XML:
        segments = split_xml_segments(doc.text, target)
        # 팀 코퍼스의 XML 발췌는 <cluster> 루트가 잘려 있어 경로에 클러스터명이 없다.
        # 메타데이터의 cluster 를 앞에 붙여 청크 단독으로도 소속을 알 수 있게 한다.
        if doc.cluster:
            for s in segments:
                if not s.heading_path or not s.heading_path[0].startswith(("cluster ", "deviceType ")):
                    s.heading_path = [f"cluster {doc.cluster}"] + s.heading_path
    elif doc.source_type in (SourceType.CODE, SourceType.IDL):
        # .matter IDL 은 최상위 cluster/endpoint 블록의 닫는 중괄호가 열에 붙어
        # 있어 C++ 분할기 그대로 쓴다. .zap(JSON)은 pretty-print로 들여쓰기가
        # 깊어 열에 붙는 중괄호가 파일 끝 하나뿐이라 전용 경계 패턴을 쓴다.
        block_end_re = (
            _JSON_BLOCK_END_RE if doc.source_path.endswith(".zap") else _CPP_BLOCK_END_RE
        )
        segments = split_code_segments(doc.text, target, block_end_re)
        if doc.source_type is SourceType.IDL:
            for s in segments:
                s.source_type = SourceType.IDL
    else:
        segments = split_segments(doc.text)

    for seg in segments:
        # 구조 단위(XML 엘리먼트, 코드 블록)는 이미 완결된 덩어리라 재분할하지 않는다
        parts = (
            [seg.text]
            if seg.source_type in (SourceType.CODE, SourceType.DATAMODEL_XML, SourceType.IDL)
            else split_prose(seg.text, target, overlap)
        )

        for part in parts:
            body = part
            if prepend and seg.heading_path:
                body = " > ".join(seg.heading_path) + "\n\n" + part

            # 식별자는 헤딩이 붙은 최종 본문에서 뽑는다.
            # 마크다운 헤딩은 split_segments에서 heading_path로 빠지므로,
            # part만 보면 "## AttributeAccessInterface" 같은 제목형 식별자를 놓친다.
            ids = extract_identifiers(body, patterns, stopwords)

            # 초단문은 버리되, 식별자가 들어 있으면 버리지 않는다.
            # 길이 필터가 식별자를 삼키면 §01 원칙 3(식별자 무손실)이 깨진다.
            too_short = len(part.strip()) < min_chars
            if too_short and not ids and seg.source_type not in (SourceType.CODE, SourceType.IDL):
                continue

            chunks.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}__{seq:04d}",
                    doc_id=doc.doc_id,
                    source_path=doc.source_path,
                    source_type=seg.source_type,
                    heading_path=seg.heading_path,
                    device_type=doc.device_type,
                    cluster=doc.cluster,
                    line_start=seg.line_start,
                    line_end=seg.line_end,
                    identifiers=ids,
                    text=body,
                    n_tokens=count_tokens(body),
                    corpus_commit=doc.corpus_commit,
                    corpus_phase=doc.corpus_phase,
                    corpus_snapshot=doc.corpus_snapshot,
                    corpus_version=doc.corpus_version,
                    owner=doc.owner,
                )
            )
            seq += 1

    return chunks


def verify_identifiers(
    docs: list[CorpusDoc], chunks: list[Chunk], cfg: Config
) -> dict[str, list[str]]:
    """
    명세서 §04 S2 수용 기준: 원문 식별자 누락 0건.
    문서별로 사라진 식별자를 돌려준다. 빈 dict여야 통과.
    """
    id_cfg = cfg.pipeline["identifiers"]
    patterns, stopwords = id_cfg["patterns"], id_cfg.get("stopwords", [])

    by_doc: dict[str, set[str]] = {}
    for c in chunks:
        by_doc.setdefault(c.doc_id, set()).update(c.identifiers)

    missing: dict[str, list[str]] = {}
    for d in docs:
        original = set(extract_identifiers(d.text, patterns, stopwords))
        lost = sorted(original - by_doc.get(d.doc_id, set()))
        if lost:
            missing[d.doc_id] = lost
    return missing


def read_corpus(path: Path = IN_PATH) -> list[CorpusDoc]:
    with path.open(encoding="utf-8") as f:
        return [CorpusDoc(**json.loads(line)) for line in f if line.strip()]


def write(chunks: list[Chunk], out_path: Path = OUT_PATH) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.model_dump(mode="json"), ensure_ascii=False) + "\n")


def report(chunks: list[Chunk], missing: dict[str, list[str]]) -> None:
    tokens = sorted(c.n_tokens for c in chunks)
    by_type: dict[str, int] = {}
    for c in chunks:
        by_type[c.source_type.value] = by_type.get(c.source_type.value, 0) + 1

    def pct(p: float) -> int:
        return tokens[min(int(len(tokens) * p), len(tokens) - 1)] if tokens else 0

    short = sum(1 for c in chunks if len(c.text) < 50)
    print(f"청크 수     : {len(chunks)}")
    print(f"타입별      : {by_type}")
    print(f"토큰 분포   : p50={pct(0.5)} p90={pct(0.9)} max={tokens[-1] if tokens else 0}")
    print(f"초단문 비율 : {short / len(chunks) * 100:.1f}%" if chunks else "초단문 비율 : -")
    print(f"식별자 누락 : {'없음' if not missing else f'{len(missing)}개 문서'}")

    for doc_id, lost in list(missing.items())[:5]:
        print(f"  ! {doc_id}: {lost[:8]}")


def find_duplicate_chunk_ids(chunks: list[Chunk]) -> list[str]:
    """
    chunk_id 중복 검사.

    Chroma는 중복 id를 DuplicateIDError로 거부하므로 S4에서야 터진다.
    임베딩까지 마친 뒤 실패하면 수 분을 날리므로 여기서 먼저 잡는다.
    실제로 .h와 .cpp가 같은 doc_id를 갖는 버그가 이렇게 드러났다.
    """
    seen: set[str] = set()
    dups: set[str] = set()
    for c in chunks:
        (dups if c.chunk_id in seen else seen).add(c.chunk_id)
    return sorted(dups)


def main() -> int:
    cfg = load()
    docs = read_corpus()
    chunks = [c for d in docs for c in chunk_document(d, cfg)]
    missing = verify_identifiers(docs, chunks, cfg)
    dups = find_duplicate_chunk_ids(chunks)

    write(chunks)
    report(chunks, missing)

    if dups:
        print(f"\n실패: chunk_id 중복 {len(dups)}건")
        for d in dups[:5]:
            print(f"  ! {d}")
        print("  → S4에서 DuplicateIDError로 터집니다. doc_id 생성 규칙을 확인하세요.")

    print(f"\n{OUT_PATH} 기록 완료")
    return 1 if (missing or dups) else 0


if __name__ == "__main__":
    sys.exit(main())
