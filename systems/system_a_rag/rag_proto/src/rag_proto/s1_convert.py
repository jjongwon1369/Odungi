"""
rag_proto.s1_convert — S1. 문서 변환

저장소 스냅샷 → data/corpus.jsonl (문서 1건 = 1줄)

명세서 §04 S1. 원문을 보존하되, 코퍼스에 무엇을 넣을지 확정하고 기록한다.
구조 분해(청킹)는 S2의 일이다.

v0.4 — 입력을 팀 코퍼스 documents.jsonl 로 전환했다 (source: team_corpus).
       repo 모드는 개인 샘플 확인용으로만 남긴다.

v0.3 — 거르는 축을 폴더에서 Device Type으로 바꿨다.

  대상 Device Type XML을 읽고 → 그것이 참조하는 <cluster id="0x...">를 수집 →
  같은 id를 가진 Cluster XML을 코퍼스에 포함시킨다.

  클러스터 파일명은 이름에서 유추할 수 없다.
  ("Refrigerator And Temperature Controlled Cabinet Mode" → Mode_Refrigerator.xml)
  그래서 파일명이 아니라 루트 엘리먼트의 id 속성으로 매칭한다.

실행:
    python -m rag_proto.s1_convert
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from .config import Config, load, validate
from .schema import CorpusDoc, SourceType

OUT_PATH = Path("data/corpus.jsonl")

# XML 앞머리의 CSA 저작권 고지. 모든 파일에 동일하게 들어 있어
# 제거하지 않으면 전 청크가 같은 법률 문구로 채워진다.
_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_XML_DECL_RE = re.compile(r"^\s*<\?xml[^>]*\?>\s*", re.DOTALL)


def strip_xml_boilerplate(text: str) -> str:
    """XML 선언과 주석을 걷어내고 본문만 남긴다."""
    text = _XML_DECL_RE.sub("", text)
    text = _XML_COMMENT_RE.sub("", text)
    return text.strip()


# C++ 파일 앞머리의 아파치 라이선스 헤더.
# XML의 CSA 고지와 같은 문제다. 모든 .cpp/.h에 동일하게 붙어 있어
# 제거하지 않으면 청크 수십 개가 순수 법률 문구로 채워지고,
# 서로 거의 동일해 어떤 질의에도 비슷한 점수를 받으며 후보 목록을 오염시킨다.
_C_BLOCK_HEADER_RE = re.compile(r"\A\s*/\*.*?\*/\s*", re.DOTALL)
_C_LINE_HEADER_RE = re.compile(r"\A(?:[ \t]*//[^\n]*\n)+")
_LICENSE_HINT_RE = re.compile(r"copyright|licensed under|SPDX-License", re.IGNORECASE)


def strip_code_license(text: str) -> str:
    """
    파일 첫머리의 라이선스 주석만 제거한다.

    Copyright / Licensed under / SPDX-License 가 들어 있을 때만 지운다.
    설명용 주석으로 시작하는 파일을 실수로 잘라내지 않기 위한 조건이다.
    """
    for pattern in (_C_BLOCK_HEADER_RE, _C_LINE_HEADER_RE):
        m = pattern.match(text)
        if m and _LICENSE_HINT_RE.search(m.group(0)):
            return text[m.end() :].lstrip("\n")
    return text


def read_xml_root(path: Path) -> ET.Element | None:
    try:
        return ET.parse(path).getroot()
    except Exception:
        return None


def build_cluster_index(dm_root: Path) -> dict[str, Path]:
    """클러스터 id(0x0056) → 파일 경로. 파일명이 아니라 id로 매칭한다."""
    index: dict[str, Path] = {}
    for path in sorted((dm_root / "clusters").glob("*.xml")):
        root = read_xml_root(path)
        if root is None:
            continue
        cid = (root.get("id") or "").lower()
        if cid:
            index[cid] = path
    return index


def referenced_cluster_ids(device_type_path: Path) -> list[str]:
    """Device Type XML이 요구하는 클러스터 id 목록."""
    root = read_xml_root(device_type_path)
    if root is None:
        return []
    ids = []
    for el in root.iter("cluster"):
        cid = (el.get("id") or "").lower()
        if cid:
            ids.append(cid)
    return sorted(set(ids))


def select_files(cfg: Config) -> list[tuple[Path, SourceType, dict]]:
    """
    수집 대상을 확정한다. 반환은 (경로, source_type, 메타) 목록.
    이 함수가 "무엇을 코퍼스에 넣을지"를 결정하는 유일한 곳이다.
    """
    root = cfg.repo_root
    c = cfg.corpus
    dm_root = root / "data_model" / c["data_model_version"]
    srcs = c.get("sources", {})
    selected: list[tuple[Path, SourceType, dict]] = []
    seen: set[Path] = set()

    def add(path: Path, stype: SourceType, meta: dict) -> None:
        if path.exists() and path not in seen:
            seen.add(path)
            selected.append((path, stype, meta))

    # 1) Device Type XML
    dt_names: list[str] = c.get("device_types", [])
    dt_paths: list[tuple[str, Path]] = []
    if srcs.get("device_types", {}).get("enabled", True):
        for name in dt_names:
            p = dm_root / "device_types" / f"{name}.xml"
            dt_paths.append((name, p))
            add(p, SourceType.DATAMODEL_XML, {"device_type": [name], "cluster": None})

    # 2) Device Type이 참조하는 Cluster XML
    if srcs.get("clusters", {}).get("enabled", True):
        cluster_index = build_cluster_index(dm_root)
        wanted: dict[str, list[str]] = {}  # cluster id → 요구한 device type들

        if c.get("follow_cluster_references", True):
            for name, p in dt_paths:
                for cid in referenced_cluster_ids(p):
                    wanted.setdefault(cid, []).append(name)

        for cid, owners in sorted(wanted.items()):
            path = cluster_index.get(cid)
            if path is None:
                continue
            croot = read_xml_root(path)
            cname = croot.get("name") if croot is not None else None
            add(path, SourceType.DATAMODEL_XML, {"device_type": sorted(set(owners)), "cluster": cname})

        for stem in c.get("extra_clusters", []):
            add(dm_root / "clusters" / f"{stem}.xml", SourceType.DATAMODEL_XML,
                {"device_type": [], "cluster": stem})

    # 3) Namespace XML
    ns_cfg = srcs.get("namespaces", {})
    if ns_cfg.get("enabled", True):
        keys = [k.lower() for k in ns_cfg.get("name_filter", [])]
        for p in sorted((dm_root / "namespaces").glob("*.xml")):
            if not keys or any(k in p.stem.lower() for k in keys):
                add(p, SourceType.DATAMODEL_XML, {"device_type": [], "cluster": None})

    # 4) C++ 구현. 클러스터 이름 슬러그와 겹치는 디렉토리만
    cpp_cfg = srcs.get("cpp", {})
    if cpp_cfg.get("enabled", True):
        cpp_root = root / cpp_cfg.get("root", "src/app/clusters")
        slugs = _cluster_slugs(selected)
        exts = tuple(cpp_cfg.get("extensions", [".cpp", ".h"]))
        if cpp_root.exists():
            for p in sorted(cpp_root.rglob("*")):
                if not p.is_file() or p.suffix not in exts:
                    continue
                rel = str(p.relative_to(cpp_root)).lower()
                if any(s in rel for s in slugs):
                    add(p, SourceType.CODE, {"device_type": [], "cluster": None})

    # 5) 산문 문서. 대상 기기를 언급하는 것만
    doc_cfg = srcs.get("docs", {})
    if doc_cfg.get("enabled", True):
        doc_root = root / doc_cfg.get("root", "docs")
        keywords = [k.lower() for k in doc_cfg.get("keyword_filter", [])]
        limit = doc_cfg.get("max_files")
        hits = 0
        for pattern in doc_cfg.get("include", ["**/*.md"]):
            for p in sorted(doc_root.glob(pattern)):
                if limit and hits >= limit:
                    break
                if not p.is_file():
                    continue
                try:
                    body = p.read_text(encoding="utf-8", errors="replace").lower()
                except OSError:
                    continue
                if keywords and not any(k in body for k in keywords):
                    continue
                add(p, SourceType.PROSE, {"device_type": [], "cluster": None})
                hits += 1

    return selected


def _cluster_slugs(selected) -> list[str]:
    """'Temperature Control Cluster' → 'temperature-control'. C++ 디렉토리 매칭용."""
    slugs = set()
    for _, stype, meta in selected:
        name = meta.get("cluster")
        if not name:
            continue
        s = name.lower().replace(" cluster", "").strip()
        slugs.add(re.sub(r"[^a-z0-9]+", "-", s).strip("-"))
    return sorted(s for s in slugs if len(s) > 3)


def infer_device_types(cfg: Config, path: Path, meta: dict) -> list[str]:
    if meta.get("device_type"):
        return meta["device_type"]
    lowered = str(path).lower()
    return sorted(
        dt
        for dt, hints in (cfg.corpus.get("device_type_hints") or {}).items()
        if any(h.lower() in lowered for h in hints)
    )


def make_doc_id(rel_path: Path) -> str:
    """
    경로에서 안정적인 doc_id를 만든다.

    확장자를 반드시 남긴다. 떼어내면 thermostat-server.h 와
    thermostat-server.cpp 가 같은 doc_id가 되고, chunk_id가 충돌해
    Chroma가 DuplicateIDError로 거부한다.
    """
    parts = list(rel_path.parts[:-1]) + [rel_path.name]
    raw = "_".join(parts)
    return re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")


def convert(cfg: Config) -> list[CorpusDoc]:
    """설정의 source 값에 따라 입력 경로를 고른다."""
    if cfg.corpus.get("source", "repo") == "team_corpus":
        return convert_from_team_corpus(cfg)
    return convert_from_repo(cfg)


# ── team_corpus 모드 ───────────────────────────────────────────

_DOC_TYPE_TO_SOURCE = {
    "xml": SourceType.DATAMODEL_XML,
    "md": SourceType.PROSE,
    "cpp": SourceType.CODE,
    "h": SourceType.CODE,
    "cmake": SourceType.CODE,
    "matter": SourceType.IDL,
    "zap": SourceType.IDL,
}


def _load_device_type_names(scope_path: Path | None) -> dict[str, str]:
    """scope.json의 products[] 에서 '0x0070' → 'Refrigerator' 매핑을 만든다."""
    if not scope_path or not scope_path.exists():
        return {}
    try:
        scope = json.loads(scope_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    names = {}
    for p in scope.get("products", []):
        names[str(p.get("id", "")).lower()] = p.get("name", "").replace(" ", "")
    return names


def _load_cluster_names(scope_path: Path | None) -> dict[str, str]:
    if not scope_path or not scope_path.exists():
        return {}
    try:
        scope = json.loads(scope_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    return {
        str(c.get("cluster_id", "")).lower(): c.get("cluster_name", "")
        for c in scope.get("clusters", [])
    }


def _resolve_source_type(meta: dict, role_map: dict) -> SourceType | None:
    role = meta.get("source_role", "")
    doc_type = (meta.get("doc_type") or "").lower()
    mapped = role_map.get(role)
    if mapped and mapped != "by_doc_type":
        return SourceType(mapped)
    return _DOC_TYPE_TO_SOURCE.get(doc_type)


def convert_from_team_corpus(cfg: Config) -> list[CorpusDoc]:
    """
    팀 코퍼스 documents.jsonl 을 CorpusDoc 으로 옮긴다.

    레코드 구조 (scripts/corpus/extract_corpus.py 기준):
      { document_id, snapshot_id, text, metadata{...}, source_spans[...] }
    metadata 에 source_role, definition_kind, doc_type, source_path, commit_hash,
    device_types(hex), clusters(hex), content_hash 가 들어 있다.

    text 는 "선택된 원문 발췌"라서 완전한 XML 문서가 아닐 수 있다.
    (processed/README.md) S2의 XML 파서가 이를 감안해야 한다.
    """
    tc = cfg.corpus["team_corpus"]
    docs_path = Path(tc["documents_path"])
    scope_path = Path(tc["scope_path"]) if tc.get("scope_path") else None
    role_map = tc.get("role_map", {})
    dt_names = _load_device_type_names(scope_path)
    cl_names = _load_cluster_names(scope_path)

    strip_xml = cfg.corpus.get("strip_xml_comments", True)
    strip_code = cfg.corpus.get("strip_code_license", True)

    docs: list[CorpusDoc] = []
    skipped: dict[str, int] = {}

    with docs_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            meta = rec.get("metadata") or {}

            stype = _resolve_source_type(meta, role_map)
            if stype is None:
                key = f"{meta.get('source_role')}/{meta.get('doc_type')}"
                skipped[key] = skipped.get(key, 0) + 1
                continue

            text = rec.get("text", "")
            if stype is SourceType.DATAMODEL_XML and strip_xml:
                text = strip_xml_boilerplate(text)
            elif stype is SourceType.CODE and strip_code:
                text = strip_code_license(text)
            if not text.strip():
                continue

            source_path = meta.get("source_path", "")
            device_types = [
                dt_names.get(str(d).lower(), str(d)) for d in meta.get("device_types", [])
            ]
            clusters = meta.get("clusters", [])
            cluster = cl_names.get(str(clusters[0]).lower(), str(clusters[0])) if len(clusters) == 1 else None

            # document_id 는 "doc:<sha256>" 형태. chunk_id 에 콜론이 들어가면
            # 인용 표기 [chunk_id] 파싱이 깨질 수 있어 경로 기반 id 를 chunk_id/doc_id
            # 로 쓰되, 원본 document_id 와 source_spans 는 upstream_document_id /
            # source_spans 필드에 그대로 보존해 원문 역추적이 가능하게 한다.
            docs.append(
                CorpusDoc(
                    doc_id=make_doc_id(Path(source_path)),
                    source_path=source_path,
                    source_type=stype,
                    heading_path=list(Path(source_path).parts[:-1]),
                    device_type=sorted(set(device_types)),
                    cluster=cluster,
                    text=text,
                    n_chars=len(text),
                    corpus_commit=meta.get("commit_hash") or cfg.commit,
                    corpus_phase=cfg.phase,
                    corpus_snapshot=rec.get("snapshot_id") or cfg.corpus_snapshot,
                    corpus_version=cfg.corpus_version,
                    owner=cfg.owner,
                    upstream_document_id=rec.get("document_id"),
                    source_spans=rec.get("source_spans"),
                )
            )

    if skipped:
        print(f"매핑되지 않아 건너뛴 문서: {skipped}")
    return docs


# ── repo 모드 (개인 샘플, 폐기 예정) ──────────────────────────

def convert_from_repo(cfg: Config) -> list[CorpusDoc]:
    docs: list[CorpusDoc] = []
    strip_xml = cfg.corpus.get("strip_xml_comments", True)
    strip_code = cfg.corpus.get("strip_code_license", True)

    for path, stype, meta in select_files(cfg):
        rel = path.relative_to(cfg.repo_root)
        text = path.read_text(encoding="utf-8", errors="replace")

        if stype is SourceType.DATAMODEL_XML and strip_xml:
            text = strip_xml_boilerplate(text)
        elif stype is SourceType.CODE and strip_code:
            text = strip_code_license(text)

        docs.append(
            CorpusDoc(
                doc_id=make_doc_id(rel),
                source_path=str(rel),
                source_type=stype,
                heading_path=list(rel.parts[:-1]),
                device_type=infer_device_types(cfg, rel, meta),
                cluster=meta.get("cluster"),
                text=text,
                n_chars=len(text),
                corpus_commit=cfg.commit,
                corpus_phase=cfg.phase,
                corpus_snapshot=cfg.corpus_snapshot,
                corpus_version=cfg.corpus_version,
                owner=cfg.owner,
            )
        )
    return docs


def write(docs: list[CorpusDoc], out_path: Path = OUT_PATH) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d.model_dump(mode="json"), ensure_ascii=False) + "\n")


def report(cfg: Config, docs: list[CorpusDoc]) -> None:
    by_type: dict[str, int] = {}
    for d in docs:
        by_type[d.source_type.value] = by_type.get(d.source_type.value, 0) + 1
    covered = sorted({dt for d in docs for dt in d.device_type})
    clusters = sorted({d.cluster for d in docs if d.cluster})

    print(f"commit      : {cfg.commit}")
    print(f"snapshot    : {cfg.corpus_snapshot or '-'}  (corpus v{cfg.corpus_version or '-'})")
    print(f"source      : {cfg.corpus.get('source', 'repo')}")
    print(f"phase       : {cfg.phase.value} (owner={cfg.owner})")
    print(f"문서 수     : {len(docs)}")
    print(f"총 문자 수  : {sum(d.n_chars for d in docs):,}")
    print(f"타입별      : {by_type}")
    print(f"대상 기기   : {covered or '없음'}")
    print(f"클러스터    : {len(clusters)}종")
    for name in clusters[:12]:
        print(f"  - {name}")
    if len(clusters) > 12:
        print(f"  ... 외 {len(clusters) - 12}종")

    if not covered:
        print("\n경고: 대상 기기 관련 문서가 없습니다. corpus.yaml의 device_types를 확인하세요.")


def main() -> int:
    cfg = load()
    problems = validate(cfg)
    if problems:
        print("설정 검증 실패. python -m rag_proto.config 로 확인하세요.")
        for p in problems:
            print(f"  - {p.splitlines()[0]}")
        return 1

    docs = convert(cfg)
    write(docs)
    report(cfg, docs)
    print(f"\n{OUT_PATH} 기록 완료")
    return 0 if docs else 1


if __name__ == "__main__":
    sys.exit(main())
