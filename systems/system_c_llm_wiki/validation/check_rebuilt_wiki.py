#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재구축한 System C 위키 검사기 (읽기 전용) — check_rebuilt_wiki.py
================================================================

위키와 코퍼스에는 아무것도 쓰지 않고, 네트워크·LLM API 도 부르지 않는다.
쓰는 파일은 --json-out 으로 준 보고서 하나뿐이다. (#27 A 기준 점검)

System A 는 색인 청크 수나 코퍼스 라벨이 어긋나면 검색기가 멈춘다. C 의 위키는 컴파일 모델이
쓴 결과물이라, A 와 같은 입력(C3 documents.jsonl)에서 나왔는지, 입력 밖 지식이 섞이지 않았는지를
run_batch 전에 따로 확인해야 한다. 옛 wiki-astra 는 corpus/raw 로 만들어져 이 검사에서 FAIL 이다.

검사 (하나라도 FAIL 이면 exit 1)
  (a) manifest   wiki_manifest.json 이 있고, 적힌 페이지가 전부 있고 그 밖의 페이지(.md)는 없다.
                 documents_sha256 = 저장소 documents.jsonl 의 sha256 = A 가 색인한 파일의 sha256.
                 documents_path / snapshot_id 가 기대값과 같고, entity_count = 페이지 수.
  (b) 출처       모든 페이지 프론트매터에 corpus_source / corpus_snapshot 이 있고 기대값과 같다.
                 commit_hash = SSOT 커밋, compiled_by = manifest 의 컴파일 모델 = 기대 컴파일 모델.
  (c) 코퍼스 밖 식별자
                 A 의 pipeline.yaml 규칙(re.ASCII, 같은 스톱워드)으로, 에이전트가 읽는 본문
                 (run_agent._strip_frontmatter 와 같게 프론트매터를 뗀 것)에서 식별자를 뽑는다.
                 컴파일 모델이 받은 입력(documents.jsonl 본문 + 상대경로 + scope.json 이름·ID)
                 어디에도 없으면(대소문자를 무시해도 없음 = absent) 실패. page:line 으로 보고한다.
                 나머지 분류는 참고: hex_reformatted(같은 값, 자릿수만 다름), case_variant(대소문자만
                 다름, 불변식 1), substring_only(더 긴 토큰 안에만 있음 = 잘림·파생).
       (c2) 코퍼스 본문에 없는 버전·개정 표기 (참고)
       (c3) 코퍼스에 있는 hex ID 인데, 그 줄의 이름이 코퍼스에서 같은 ID 의 ±250자 안에 한 번도
            안 나오는 줄 (ID 를 다른 개체에 붙임. 예: C3 의 0x0048 은 Thermostat.PresetTypes 인데
            옛 위키는 캐비닛의 Oven Cavity Operational State 로 적었다). 휴리스틱이라 사람이 본다.
  (d) 제외 ID 유출
                 scope.json excluded_device_types / excluded_cabinet_clusters 의 ID 가 본문에 있고,
                 (c) 가 absent 로 보거나 (c3) 가 그 줄을 짚으면 유출로 센다.
  (e) 구축 원장  build_calls.jsonl + build_tokens.json 이 있다. 호출마다 4열(uncached_input,
                 cache_creation, cache_read, output)이 따로 정수로 있고 usage_raw 가 있다. 합계는
                 원장을 다시 더한 값과 같고, 출처는 기대값과 같다. 합산 필드가 있으면 실패.
  (f) 상호링크   '## 관련 페이지' 가 있는 페이지가 1개 이상이고 링크 대상이 전부 있다.
                 라벨 'Name `0xNNNN`' 의 ID 는 대상 페이지 ID 접두사와 같아야 한다. 컴파일러가
                 한 페이지로 합친 클러스터(예: 0x0071/0x0072 가 ResourceMonitoring.xml 공유)는 대상
                 프론트매터 ids 안이면 된다. 라벨 이름(과 링크 뒤 설명의 '이름 `0xNNNN`')은
                 scope.json 의 그 ID 이름과 같아야 한다. 기기 페이지는 scope.json 의 직접·베이스
                 클러스터 ID 를 빠짐없이 링크해야 한다.
  참고 (종료 코드와 무관)
  (g) 커버리지   각 페이지 source_paths 문서의 식별자 중 본문에 남은 비율
  (h) 도달성     run_agent 의 "<하위폴더>/<파일명>" page_id 충돌, 깊이 1 이 아닌 페이지

사용법 (리포 루트에서. 기본값은 전부 저장소 기준 경로라 다른 위치에서 돌려도 같다):
    python3 systems/system_c_llm_wiki/validation/check_rebuilt_wiki.py systems/system_c_llm_wiki/wiki-c3
    python3 systems/system_c_llm_wiki/validation/check_rebuilt_wiki.py <wiki_root> [documents.jsonl] \\
        [--pipeline-yaml ...] [--scope-json ...] [--snapshot-json ...] \\
        [--expected-snapshot ...] [--expected-commit ...] [--expected-documents-sha256 ...] \\
        [--expected-compiled-by openai/gpt-6-astra] [--max-lines 3] [--json-out report.json]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# 저장소 루트 기준으로 잡는다. 실행 위치 기준이면 다른 디렉터리에서 돌렸을 때 기본 파일을
# 못 찾는다. (run_batch.REPO_ROOT 와 같은 방식)
REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_SOURCE = "corpus/tiers/c3/processed/documents.jsonl"
DOCS_DEFAULT = REPO_ROOT / EXPECTED_SOURCE
SNAPSHOT_JSON_DEFAULT = REPO_ROOT / "corpus/tiers/c3/metadata/snapshot.json"
# tier c3 사본. products/clusters/source_sets 는 corpus/metadata/scope.json 과 같고 excluded_* 도 있다.
SCOPE_JSON_DEFAULT = REPO_ROOT / "corpus/tiers/c3/scope.json"
PIPELINE_YAML_DEFAULT = REPO_ROOT / "systems/system_a_rag/rag_proto/configs/pipeline.yaml"
# System A 가 색인한 documents.jsonl 의 sha256. run_batch.A_DOCUMENTS_SHA256 과 같은 값이다.
A_DOCUMENTS_SHA256 = "71c40454c6695fc6fd13aade191e1a21dfd11e5311def31f1f07adddf1618359"
# 팀이 정한 위키 컴파일 모델 (rag_proto CLAUDE.md: gpt-6-astra 는 C 위키 구축 전용)
EXPECTED_COMPILED_BY = "openai/gpt-6-astra"
MANIFEST_NAME = "wiki_manifest.json"        # compile_wiki.MANIFEST_NAME
MANIFEST_SCHEMA = 1
TOKEN_COLUMNS = ("uncached_input", "cache_creation", "cache_read", "output")
SECTION_HEADER = "## 관련 페이지"            # linker/crosslink_wiki.SECTION_HEADER
VERSION_RES = [
    re.compile(r"\bMatter\s*(?:v|version\s*)?\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE),
    re.compile(r"\b(?:revision|rev\.?)\s*\d+\b", re.IGNORECASE),
    re.compile(r"\b(?:spec(?:ification)?)\s*(?:v|version\s*)?\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE),
]


def _safe_console() -> None:
    """Windows 기본 콘솔(cp949)에서 출력할 수 없는 문자가 있어도 멈추지 않게 한다.
    담지 못하는 문자는 '?' 로 바뀐다. (#27 동수님 리뷰 P1-1)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _norm_hex(h: str) -> str:
    """0x002d / 0X002D → 0x002D (scope.json 표기)."""
    return "0x" + h[2:].upper()


def slugify(name: str) -> str:
    """compile_wiki.slugify / crosslink_wiki.slugify 와 같다."""
    return name.lower().replace(" ", "-").replace("/", "-")


# ---------------------------------------------------------------------------
# 식별자 규칙 (A 의 pipeline.yaml, rag_proto.extract_identifiers 처럼 re.ASCII)
# ---------------------------------------------------------------------------

def parse_identifiers_block(text: str) -> tuple:
    """pyyaml 없이 `identifiers:` 블록만 읽는다. run_batch._parse_identifiers_block 과 같은 규칙.

    run_batch 를 import 하면 run_agent 까지 불러오므로 검사기에는 옮겨 둔다.
    대상은 다음 모양뿐이다:

        identifiers:
          patterns:
            - '...'
          stopwords:
            - "..."
    """
    pats: list = []
    stops: list = []
    section = None       # "patterns" | "stopwords"
    in_block = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0:
            in_block = stripped.startswith("identifiers:")
            section = None
            continue
        if not in_block:
            continue
        if stripped.startswith("patterns:"):
            section = "patterns"
            continue
        if stripped.startswith("stopwords:"):
            section = "stopwords"
            continue
        if stripped.startswith("- ") and section:
            item = stripped[2:].split("#", 1)[0].strip()
            if len(item) >= 2 and item[0] == item[-1] and item[0] in "'\"":
                item = item[1:-1]
            (pats if section == "patterns" else stops).append(item)
    return pats, stops


def load_identifier_rules(pipeline_yaml: Path):
    """A 설정에서 patterns/stopwords 를 읽는다. 못 읽으면 멈춘다.

    폴백 규칙으로 넘기면 A 와 규칙이 어긋나도 드러나지 않는다. (run_batch 와 같은 방침, #23 리뷰)
    """
    try:
        text = pipeline_yaml.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"[오류] {pipeline_yaml} 를 읽지 못했습니다 ({exc}).\n"
                         "       A 와 같은 규칙으로 식별자를 세야 하므로 폴백으로 넘기지 않습니다.")
    try:
        import yaml  # type: ignore
        ident = (yaml.safe_load(text) or {}).get("identifiers") or {}
        pats = list(ident.get("patterns") or [])
        stops = list(ident.get("stopwords") or [])
        src = f"{pipeline_yaml} (pyyaml)"
    except ImportError:
        pats, stops = parse_identifiers_block(text)   # pyyaml 없는 환경
        src = f"{pipeline_yaml} (pyyaml 없음, 최소 파서)"
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"[오류] {pipeline_yaml} 파싱 실패 ({exc}).")
    if not pats:
        raise SystemExit(f"[오류] {pipeline_yaml} 의 identifiers.patterns 가 비어 있습니다.")
    return [re.compile(p, re.ASCII) for p in pats], set(stops), src


def extract(text: str, pats, stop) -> set:
    out = set()
    for p in pats:
        out.update(m.group(0) for m in p.finditer(text))
    return out - stop


# ---------------------------------------------------------------------------
# 위키 읽기 (run_agent / run_batch 와 같은 규칙)
# ---------------------------------------------------------------------------

def strip_frontmatter(text: str) -> tuple:
    """run_agent._strip_frontmatter 와 같은 자르기. (본문, 떼어 낸 줄 수)"""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            head = text[: end + 4]
            rest = text[end + 4:]
            body = rest.lstrip("\n")
            removed = head.count("\n") + (len(rest) - len(body))
            return body, removed
    return text, 0


def parse_frontmatter(text: str) -> dict:
    """run_batch._get_wiki_provenance 와 같은 규칙 + source_paths / ids / commit_hash."""
    if not text.startswith("---") or text.count("---") < 2:
        return {}
    head = text.split("---", 2)[1]
    found = {}
    for line in head.split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        if k in ("corpus_source", "corpus_snapshot", "commit_hash", "compiled_by", "entity",
                 "doc_type", "source_paths", "ids"):
            found[k] = v.strip() if k in ("source_paths", "ids") else v.strip().strip('"').strip("'")
    for k in ("source_paths", "ids"):
        if k in found:
            try:
                found[k] = ast.literal_eval(found[k])
            except Exception:  # noqa: BLE001
                found[k] = None
    return found


def wiki_pages(root: Path) -> list:
    """에이전트 목차(run_agent._build_toc)에 오르는 파일: README 를 뺀 모든 .md."""
    return [p for p in sorted(root.rglob("*.md")) if p.stem.lower() != "readme"]


# ---------------------------------------------------------------------------
# 코퍼스
# ---------------------------------------------------------------------------

def load_corpus(docs_path: Path, scope_path: Path | None):
    """documents.jsonl → ({상대경로: 본문}, snapshot_id 집합, scope.json 이름·ID 목록, scope dict)."""
    if not docs_path.exists():
        raise SystemExit(f"[오류] {docs_path} 가 없습니다. "
                         "python3 scripts/corpus/build_tiers.py --tier c3 로 먼저 만드세요.")
    prefix = "corpus/raw/connectedhomeip/"
    docs: dict = {}
    snapshots: set = set()
    for line in docs_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        meta = d.get("metadata", {})
        rel = meta.get("relative_path") or meta.get("source_path") or meta.get("raw_path") or ""
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
        docs[rel] = d.get("text", "")
        if d.get("snapshot_id"):
            snapshots.add(d["snapshot_id"])
    scope: dict = {}
    scope_strings: list = []
    if scope_path and scope_path.exists():
        scope = json.loads(scope_path.read_text(encoding="utf-8"))
        # 컴파일 모델은 엔티티 이름을, 에이전트는 목차의 페이지 ID(hex 포함)를 받는다.
        for c in scope.get("clusters", []):
            scope_strings += [c.get("cluster_name", ""), c.get("cluster_id", "")]
        for p in scope.get("products", []):
            scope_strings += [p.get("name", ""), p.get("id", "")]
    return docs, snapshots, scope_strings, scope


def read_expected_labels(snapshot_json: Path) -> tuple:
    """corpus/tiers/c3/metadata/snapshot.json → (snapshot_id, commit_hash). run_batch 와 같은 출처."""
    try:
        data = json.loads(snapshot_json.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"[오류] {snapshot_json} 을 읽을 수 없습니다 ({exc}). "
                         "--expected-snapshot / --expected-commit 으로 직접 주세요.")
    return data.get("snapshot_id"), data.get("commit_hash")


# ---------------------------------------------------------------------------
# (a) manifest
# ---------------------------------------------------------------------------

def check_manifest(root: Path, pages: list, docs_path: Path, exp_source: str,
                   exp_snapshot: str, a_sha: str | None):
    """반환: (문제 목록, 정보 dict, manifest 또는 None)."""
    problems: list = []
    docs_sha = file_sha256(docs_path)
    info = {"documents_sha256_repo": docs_sha}
    # 저장소 파일 자체가 A 의 색인 입력과 다르면 manifest 가 맞아도 A 와 같은 입력이 아니다.
    if a_sha and docs_sha != a_sha:
        problems.append(f"저장소 {docs_path.name} sha256 {docs_sha[:12]}... 이 "
                        f"A 가 색인한 입력 {a_sha[:12]}... 과 다르다")
    path = root / MANIFEST_NAME
    if not path.exists():
        problems.append(f"{MANIFEST_NAME} 없음 (고친 compile_wiki.py 로 만든 위키가 아니다)")
        return problems, info, None
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        problems.append(f"{MANIFEST_NAME} 을 읽지 못함 ({exc})")
        return problems, info, None
    if not isinstance(m, dict):
        problems.append(f"{MANIFEST_NAME} 이 객체가 아니다")
        return problems, info, None
    if m.get("schema") != MANIFEST_SCHEMA:
        problems.append(f"schema={m.get('schema')!r} != {MANIFEST_SCHEMA}")
    listed = m.get("pages") or []
    if not listed:
        problems.append("manifest 의 pages 가 비어 있다")
    if len(set(listed)) != len(listed):
        problems.append("manifest 의 pages 에 중복이 있다")
    # 크기 0 은 컴파일러도 '없음'으로 본다(다시 만들 대상).
    missing = [pg for pg in listed if not (root / pg).is_file() or (root / pg).stat().st_size == 0]
    if missing:
        problems.append(f"manifest 에는 있는데 없거나 빈 페이지 {len(missing)}개: {missing[:5]}")
    on_disk = {p.relative_to(root).as_posix() for p in pages}
    extra = sorted(on_disk - set(listed))
    if extra:
        # 에이전트 목차는 rglob 이라 이런 파일도 그대로 읽을 수 있다.
        problems.append(f"manifest 에 없는 페이지 {len(extra)}개(에이전트가 읽게 된다): {extra[:5]}")
    if m.get("entity_count") != len(listed):
        problems.append(f"entity_count {m.get('entity_count')!r} != 페이지 {len(listed)} "
                        "(두 엔티티가 한 파일로 겹쳤다)")
    if m.get("documents_path") != exp_source:
        problems.append(f"documents_path {m.get('documents_path')!r} != {exp_source!r}")
    if m.get("documents_sha256") != docs_sha:
        problems.append(f"documents_sha256 {str(m.get('documents_sha256'))[:12]}... != "
                        f"저장소 {docs_path.name} {docs_sha[:12]}... (다른 입력으로 컴파일)")
    if m.get("snapshot_id") != exp_snapshot:
        problems.append(f"snapshot_id {m.get('snapshot_id')!r} != {exp_snapshot!r}")
    for k in ("compile_provider", "compile_model"):
        if not m.get(k):
            problems.append(f"{k} 없음")
    info.update({"pages": len(listed), "missing": missing, "extra": extra,
                 "compiled_by": f"{m.get('compile_provider')}/{m.get('compile_model')}"})
    return problems, info, m


# ---------------------------------------------------------------------------
# (b) 출처
# ---------------------------------------------------------------------------

def check_provenance(pages, root, exp_source, exp_snapshot, exp_commit, exp_compiled: list):
    """exp_compiled: [(설명, 값)] — manifest 의 컴파일 모델, 기대 컴파일 모델."""
    problems = []
    values = defaultdict(lambda: defaultdict(int))
    for p in pages:
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        rel = p.relative_to(root).as_posix()
        for key, exp in (("corpus_source", exp_source), ("corpus_snapshot", exp_snapshot),
                         ("commit_hash", exp_commit)):
            v = fm.get(key)
            values[key][v if v is not None else "<missing>"] += 1
            if v is None:
                problems.append((rel, key, "missing"))
            elif v != exp:
                problems.append((rel, key, f"{v!r} != expected {exp!r}"))
        cb = fm.get("compiled_by")
        values["compiled_by"][cb if cb is not None else "<missing>"] += 1
        for what, exp in exp_compiled:
            if cb != exp:
                problems.append((rel, "compiled_by", f"{cb!r} != {what} {exp!r}"))
    return problems, {k: dict(v) for k, v in values.items()}


# ---------------------------------------------------------------------------
# (c) 코퍼스 밖 식별자 / (c2) 버전 표기 / (c3) hex-이름 짝 / (d) 제외 ID
# ---------------------------------------------------------------------------

def classify_identifier(ident: str, ref_ids: set, ref_ids_lower: set, ref_text: str,
                        ref_text_lower: str, ref_hex_values: set) -> str:
    if ident in ref_ids:
        return "exact"
    if ident.lower().startswith("0x"):
        try:
            if int(ident, 16) in ref_hex_values:
                if ident.lower() in ref_ids_lower:
                    return "case_variant"
                return "hex_reformatted"
        except ValueError:
            pass
    if ident.lower() in ref_ids_lower:
        return "case_variant"
    if ident in ref_text:
        return "substring_only"
    if ident.lower() in ref_text_lower:
        return "case_variant"
    return "absent"


def check_identifiers(pages, root, docs, scope_strings, pats, stop):
    # 컴파일 모델이 받은 것 = 본문 + '--- [role] 경로 ---' 머리의 경로 + 엔티티 이름(scope.json)
    ref_parts = list(docs.values()) + list(docs.keys()) + scope_strings
    ref_text = "\n".join(ref_parts)
    ref_text_lower = ref_text.lower()
    ref_ids = extract(ref_text, pats, stop)
    ref_ids_lower = {i.lower() for i in ref_ids}
    ref_hex_values = set()
    for m in re.finditer(r"\b0x[0-9A-Fa-f]+\b", ref_text, re.ASCII):
        try:
            ref_hex_values.add(int(m.group(0), 16))
        except ValueError:
            pass
    in_text_only = extract("\n".join(docs.values()), pats, stop)

    findings = defaultdict(lambda: defaultdict(list))   # 분류 -> 식별자 -> [(페이지, 줄, 문맥)]
    per_page_body_ids = {}
    version_hits = defaultdict(list)
    ref_ws = re.sub(r"\s+", " ", ref_text_lower)
    for p in pages:
        body, offset = strip_frontmatter(p.read_text(encoding="utf-8"))
        rel = p.relative_to(root).as_posix()
        page_ids = set()
        for ln, line in enumerate(body.split("\n"), start=offset + 1):
            ids = extract(line, pats, stop)
            page_ids |= ids
            for ident in ids:
                cls = classify_identifier(ident, ref_ids, ref_ids_lower, ref_text,
                                          ref_text_lower, ref_hex_values)
                if cls != "exact":
                    findings[cls][ident].append((rel, ln, line.strip()[:160]))
            for rx in VERSION_RES:
                for m in rx.finditer(line):
                    phrase = re.sub(r"\s+", " ", m.group(0))
                    if phrase.lower() not in ref_ws:
                        version_hits[phrase].append((rel, ln, line.strip()[:160]))
        per_page_body_ids[rel] = page_ids
    path_only = {i for i in ref_ids if i not in in_text_only}
    return findings, version_hits, per_page_body_ids, len(ref_ids), path_only


_HEX4 = re.compile(r"\b0x[0-9A-Fa-f]{4}\b", re.ASCII)
_HEX_ANY = re.compile(r"\b0x[0-9A-Fa-f]+\b", re.ASCII)
_BACKTICK = re.compile(r"`([^`]{3,80})`")
_TITLE = re.compile(r"\b[A-Z][A-Za-z0-9/]*(?:[ \-][A-Z][A-Za-z0-9/]*)+\b", re.ASCII)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _compact(s: str) -> str:
    return _NON_ALNUM.sub("", s.lower())


def check_hex_name_pairs(pages, root, docs, pats, stop, window: int = 250):
    """(c3) 코퍼스에 있는 hex ID 라도 코퍼스가 한 번도 붙이지 않은 개체에 붙을 수 있다.

    hex ID 와 이름(백틱 안 문자열, Title Case 구, CamelCase 식별자)이 함께 있는 위키 줄마다,
    그 이름 중 하나라도 documents.jsonl 본문에서 같은 값의 hex ID ±window 자 안에 나오면 지지된 짝이다.
    """
    ref = "\n\x00\n".join(docs.values())
    positions = defaultdict(list)
    for m in _HEX_ANY.finditer(ref):
        try:
            positions[int(m.group(0), 16)].append(m.start())
        except ValueError:
            pass
    win_cache: dict = {}

    def windows(val):
        if val not in win_cache:
            win_cache[val] = [_compact(ref[max(0, p - window): p + window]) for p in positions[val]]
        return win_cache[val]

    pair_cache: dict = {}
    unsupported = defaultdict(list)   # hex -> [(페이지, 줄, 이름들, 문맥)]
    for p in pages:
        body, offset = strip_frontmatter(p.read_text(encoding="utf-8"))
        rel = p.relative_to(root).as_posix()
        for ln, line in enumerate(body.split("\n"), start=offset + 1):
            hexes = _HEX4.findall(line)
            if not hexes:
                continue
            names = set(_BACKTICK.findall(line)) | set(_TITLE.findall(line)) | extract(line, pats, stop)
            names = {n for n in names if not _HEX_ANY.fullmatch(n.strip()) and len(_compact(n)) >= 4}
            if not names:
                continue
            for h in set(hexes):
                val = int(h, 16)
                if not positions.get(val):
                    continue          # (c) 가 이미 absent / hex_reformatted 로 보고한다
                key = (val, frozenset(_compact(n) for n in names))
                if key not in pair_cache:
                    cn = [c for c in key[1] if c]
                    pair_cache[key] = any(any(c in w for c in cn) for w in windows(val))
                if not pair_cache[key]:
                    unsupported[h].append((rel, ln, sorted(names)[:6], line.strip()[:160]))
    return unsupported


def check_excluded(pages, root, scope: dict, unsupported_pairs):
    """(d) 코퍼스 담당자가 뺀 ID(scope.json excluded_*). 있는 것만으로는 유출이 아니다
    (예: 0x0048 은 C3 에서 Thermostat 속성 ID). 짝이 지지되지 않거나 코퍼스에 없을 때 유출이다.
    사람이 모든 출현을 볼 수 있게 전부 나열한다."""
    excluded = {}
    for item in scope.get("excluded_device_types", []):
        name, _, hid = str(item).rpartition(":")
        excluded[_norm_hex(hid)] = f"excluded device type {name}"
    for hid in scope.get("excluded_cabinet_clusters", []):
        excluded[_norm_hex(str(hid))] = "excluded cabinet cluster"
    hits = defaultdict(list)
    for p in pages:
        body, offset = strip_frontmatter(p.read_text(encoding="utf-8"))
        rel = p.relative_to(root).as_posix()
        for ln, line in enumerate(body.split("\n"), start=offset + 1):
            for h in _HEX4.findall(line):
                hu = _norm_hex(h)
                if hu in excluded:
                    flagged = any(o[0] == rel and o[1] == ln for o in unsupported_pairs.get(h, []))
                    hits[f"{hu} ({excluded[hu]})"].append(
                        (rel, ln, "UNSUPPORTED-PAIR" if flagged else "", line.strip()[:140]))
    return hits


# ---------------------------------------------------------------------------
# (e) 구축 원장
# ---------------------------------------------------------------------------

def check_ledger(root: Path, exp_source, exp_snapshot, n_pages, manifest_compiled_by=None):
    problems, info = [], {}
    ledger = root / "build_calls.jsonl"
    agg = root / "build_tokens.json"
    lines = []
    if not ledger.exists():
        problems.append(f"{ledger.name} missing")
    else:
        for i, raw in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                d = json.loads(raw)
            except json.JSONDecodeError as exc:
                problems.append(f"{ledger.name}:{i} unreadable ({exc})")
                continue
            lines.append(d)
            miss = [c for c in TOKEN_COLUMNS if c not in d]
            if miss:
                problems.append(f"{ledger.name}:{i} missing columns {miss}")
            bad = [c for c in TOKEN_COLUMNS if c in d and d[c] is not None and not isinstance(d[c], int)]
            if bad:
                problems.append(f"{ledger.name}:{i} non-integer columns {bad}")
            if d.get("uncached_input") is None or d.get("output") is None:
                problems.append(f"{ledger.name}:{i} uncached_input/output is null")
            if d.get("usage_raw") is None:
                problems.append(f"{ledger.name}:{i} usage_raw missing")
            # 4열을 한 필드로 합친 값은 두지 않는다 (불변식 2)
            summed = [k for k in d if k in ("total_tokens", "tokens_total", "input_total")]
            if summed:
                problems.append(f"{ledger.name}:{i} has summed field(s) {summed}")
        n_ent = len({d.get("entity") for d in lines})
        info["ledger_calls"] = len(lines)
        info["entities_in_ledger"] = n_ent
        if lines and n_ent < n_pages:
            problems.append(f"ledger covers {n_ent} entities < {n_pages} pages")
    if not agg.exists():
        problems.append(f"{agg.name} missing")
    else:
        try:
            a = json.loads(agg.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{agg.name} unreadable ({exc})")
            a = {}
        if a:
            if list(a.get("columns", [])) != list(TOKEN_COLUMNS):
                problems.append(f"{agg.name} columns={a.get('columns')} != {list(TOKEN_COLUMNS)}")
            totals = a.get("totals", {})
            if set(totals) != set(TOKEN_COLUMNS):
                problems.append(f"{agg.name} totals keys={sorted(totals)}")
            if lines:
                re_sum = {c: sum(d.get(c) or 0 for d in lines if isinstance(d.get(c), int))
                          for c in TOKEN_COLUMNS}
                if re_sum != {c: totals.get(c) for c in TOKEN_COLUMNS}:
                    problems.append(f"{agg.name} totals {totals} != ledger re-sum {re_sum}")
            if a.get("corpus_source") != exp_source:
                problems.append(f"{agg.name} corpus_source={a.get('corpus_source')!r}")
            if a.get("corpus_snapshot") != exp_snapshot:
                problems.append(f"{agg.name} corpus_snapshot={a.get('corpus_snapshot')!r}")
            # 같은 실행이 쓴 두 파일이므로 컴파일 모델이 같아야 한다.
            if manifest_compiled_by and a.get("compiled_by") != manifest_compiled_by:
                problems.append(f"{agg.name} compiled_by={a.get('compiled_by')!r} != "
                                f"manifest {manifest_compiled_by!r}")
            info["totals"] = totals
            info["compiled_by"] = a.get("compiled_by")
    return problems, info


# ---------------------------------------------------------------------------
# (f) 상호링크
# ---------------------------------------------------------------------------

_LINK = re.compile(r"^\s*[-*]\s+\[(?P<label>[^\]]+)\]\((?P<target>[^)\s]+)\)")
# "클러스터 이름 `0xNNNN`" 짝. 이름은 scope.json cluster_name 에 쓰이는 글자만 (C3 23개 전부 해당)
_LABEL_ID = re.compile(r"(?P<name>[A-Za-z0-9][A-Za-z0-9/ .&\-]*?)\s*`(?P<id>0x[0-9A-Fa-f]{4})`",
                       re.ASCII)
_PAGE_ID_PREFIX = re.compile(r"^(0x[0-9A-Fa-f]{4})-", re.ASCII)


def check_links(pages, root: Path, scope: dict):
    """(f) 링커(crosslink_wiki.py)가 붙인 '## 관련 페이지'.

    링커는 LLM 이 아니라 scope.json 으로 목록을 만든다. 그래서 틀리면 모든 재구축 위키가
    같은 오류를 물려받는다. 실제로 병합 페이지의 대표 이름을 다른 ID 에 붙였다
    ('HEPA Filter Monitoring `0x0072`', 0x0072 는 Activated Carbon), RAC 의 0x0072 링크는 빠졌다.
    """
    cluster_names = {_norm_hex(c["cluster_id"]): c["cluster_name"] for c in scope.get("clusters", [])}
    product_names = {_norm_hex(p["id"]): p["name"] for p in scope.get("products", [])}
    root_r = root.resolve()
    problems = []                 # (페이지, 줄, 내용)
    linked_ids: dict = {}         # 페이지 -> 라벨에 적힌 ID 집합
    header_ln: dict = {}          # 페이지 -> '## 관련 페이지' 줄 번호
    n_links = 0
    fm_cache: dict = {}
    for p in pages:
        text = p.read_text(encoding="utf-8")
        idx = text.find("\n" + SECTION_HEADER)
        if idx == -1:
            continue
        rel = p.relative_to(root).as_posix()
        first_ln = text[: idx + 1].count("\n") + 1       # 머리줄의 줄 번호
        header_ln[rel] = first_ln
        ids_here = linked_ids.setdefault(rel, set())
        for off, line in enumerate(text[idx + 1:].split("\n")):
            m = _LINK.match(line)
            if not m:
                continue
            n_links += 1
            ln = first_ln + off
            label, target = m.group("label"), m.group("target")
            tgt = (p.parent / target).resolve()
            try:
                tgt_rel = tgt.relative_to(root_r).as_posix()
            except ValueError:
                problems.append((rel, ln, f"위키 밖을 가리키는 링크 {target}"))
                continue
            if not tgt.is_file():
                problems.append((rel, ln, f"깨진 링크 {target}"))
                continue
            # 링크 뒤 설명(병합 페이지의 '(사용 클러스터: 이름 `0xNNNN`, …)')도 이름이 맞아야 한다.
            for mm in _LABEL_ID.finditer(line[m.end():]):
                nid, nname = _norm_hex(mm.group("id")), mm.group("name").strip()
                if cluster_names.get(nid) != nname:
                    problems.append((rel, ln, f"설명 '{nname} `{nid}`' — scope.json 에서 {nid} 는 "
                                              f"{cluster_names.get(nid)!r}"))
            pairs = [(mm.group("name").strip(), _norm_hex(mm.group("id")))
                     for mm in _LABEL_ID.finditer(label)]
            if not pairs:
                continue                                   # 기기·베이스 링크는 ID 가 없다
            if tgt_rel not in fm_cache:
                fm_cache[tgt_rel] = parse_frontmatter(tgt.read_text(encoding="utf-8"))
            tids = {_norm_hex(i) for i in (fm_cache[tgt_rel].get("ids") or [])
                    if isinstance(i, str) and i.lower().startswith("0x")}
            pm = _PAGE_ID_PREFIX.match(tgt.stem)
            prefix = _norm_hex(pm.group(1)) if pm else None
            # 기기 ID(0x0070~0x0073)와 클러스터 ID(0x0071/0x0072)가 겹치므로 대상 폴더로 고른다.
            names = product_names if tgt_rel.startswith("device-types/") else cluster_names
            for name, cid in pairs:
                ids_here.add(cid)
                if cid != prefix and cid not in tids:
                    problems.append((rel, ln, f"라벨 ID {cid} 가 대상 {tgt_rel} 와 다르다 "
                                              f"(접두사 {prefix}, ids {sorted(tids)})"))
                exp_name = names.get(cid)
                if exp_name is None:
                    problems.append((rel, ln, f"라벨 ID {cid} 가 scope.json 에 없다"))
                elif name != exp_name:
                    problems.append((rel, ln, f"라벨 '{name} `{cid}`' — scope.json 에서 {cid} 는 "
                                              f"'{exp_name}'"))
    # 기기 페이지: scope.json 의 직접·베이스 클러스터를 빠짐없이 링크해야 한다.
    for prod in scope.get("products", []):
        dp = root / "device-types" / f"{slugify(prod['name'])}.md"
        if not dp.is_file():
            continue                                       # 빠진 페이지는 (a) 가 잡는다
        rel = dp.relative_to(root).as_posix()
        if rel not in linked_ids:
            problems.append((rel, 1, f"'{SECTION_HEADER}' 섹션이 없다"))
            continue
        want = {_norm_hex(i) for i in list(prod.get("direct_cluster_ids", []))
                + list(prod.get("base_cluster_ids", []))}
        miss = sorted(want - linked_ids[rel])
        if miss:
            problems.append((rel, header_ln[rel],
                             f"scope.json 직접·베이스 클러스터 중 링크가 없는 ID {miss}"))
    return problems, {"linked_pages": len(linked_ids), "links": n_links}


# ---------------------------------------------------------------------------
# (g) 커버리지 / (h) 도달성 — 참고
# ---------------------------------------------------------------------------

def check_coverage(pages, root, docs, per_page_body_ids, pats, stop):
    rows = []
    for p in pages:
        rel = p.relative_to(root).as_posix()
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        srcs = fm.get("source_paths") or []
        known = [s for s in srcs if s in docs]
        unknown = [s for s in srcs if s not in docs]
        src_ids = set()
        for s in known:
            src_ids |= extract(docs[s], pats, stop)
        hit = src_ids & per_page_body_ids.get(rel, set())
        rows.append({
            "page": rel, "source_docs": len(srcs), "source_docs_not_in_corpus": len(unknown),
            "source_ids": len(src_ids), "kept": len(hit),
            "recall": (len(hit) / len(src_ids)) if src_ids else None,
            "unknown_examples": unknown[:3],
        })
    wiki_all = set().union(*per_page_body_ids.values()) if per_page_body_ids else set()
    corpus_all = extract("\n".join(docs.values()), pats, stop)
    return rows, {
        "corpus_identifiers": len(corpus_all),
        "wiki_body_identifiers_in_corpus": len(corpus_all & wiki_all),
        "global_recall": len(corpus_all & wiki_all) / len(corpus_all) if corpus_all else None,
        "missing_examples": sorted(corpus_all - wiki_all)[:40],
    }


def check_reachability(root: Path):
    ids = defaultdict(list)
    for p in wiki_pages(root):
        ids[f"{p.parent.name}/{p.stem}"].append(p.relative_to(root).as_posix())
    collisions = {k: v for k, v in ids.items() if len(v) > 1}
    odd_depth = [v[0] for v in ids.values() if v and v[0].count("/") != 1]
    return collisions, odd_depth, len(ids)


# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    _safe_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wiki_root", type=Path)
    ap.add_argument("documents_jsonl", type=Path, nargs="?", default=DOCS_DEFAULT,
                    help=f"기본 {EXPECTED_SOURCE} (저장소 기준)")
    ap.add_argument("--pipeline-yaml", type=Path, default=PIPELINE_YAML_DEFAULT,
                    help="A 의 configs/pipeline.yaml (식별자 규칙). 못 읽으면 멈춘다.")
    ap.add_argument("--scope-json", type=Path, default=SCOPE_JSON_DEFAULT)
    ap.add_argument("--snapshot-json", type=Path, default=SNAPSHOT_JSON_DEFAULT,
                    help="기대 snapshot_id / commit_hash 를 읽을 파일 (run_batch 와 같은 출처)")
    ap.add_argument("--expected-source", default=EXPECTED_SOURCE)
    ap.add_argument("--expected-snapshot", default=None)
    ap.add_argument("--expected-commit", default=None)
    ap.add_argument("--expected-documents-sha256", default=A_DOCUMENTS_SHA256,
                    help="A 가 색인한 documents.jsonl 의 sha256. 빈 문자열이면 이 대조를 건너뛴다.")
    ap.add_argument("--expected-compiled-by", default=EXPECTED_COMPILED_BY,
                    help="모든 페이지의 compiled_by. 빈 문자열이면 manifest 와의 일치만 본다.")
    ap.add_argument("--max-lines", type=int, default=3, help="식별자마다 출력할 출현 수")
    ap.add_argument("--expected-pages", type=int, default=34,
                    help="참고용. compile_wiki.py 가 C3 를 묶는 엔티티 수 (2026-09-30 기준 34)")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    root = args.wiki_root
    if not root.is_dir():
        print(f"[오류] 위키 폴더 {root} 가 없습니다", file=sys.stderr)
        return 1
    exp_snapshot, exp_commit = args.expected_snapshot, args.expected_commit
    if not exp_snapshot or not exp_commit:
        snap, commit = read_expected_labels(args.snapshot_json)
        exp_snapshot = exp_snapshot or snap
        exp_commit = exp_commit or commit
    pats, stop, rules_src = load_identifier_rules(args.pipeline_yaml)
    docs, doc_snapshots, scope_strings, scope = load_corpus(args.documents_jsonl, args.scope_json)
    pages = wiki_pages(root)
    report: dict = {"wiki_root": str(root), "documents": str(args.documents_jsonl),
                    "identifier_rules": rules_src, "pages": len(pages),
                    "expected": {"source": args.expected_source, "snapshot": exp_snapshot,
                                 "commit": exp_commit, "compiled_by": args.expected_compiled_by,
                                 "documents_sha256": args.expected_documents_sha256}}

    print(f"== 위키 {root}  ({len(pages)}페이지)")
    print(f"== 코퍼스 {args.documents_jsonl}: 문서 {len(docs)}개, "
          f"{sum(len(t) for t in docs.values()):,}자, 파일 안 snapshot_id = {sorted(doc_snapshots)}")
    if doc_snapshots != {exp_snapshot}:
        print(f"   [WARN] documents.jsonl snapshot != 기대값 {exp_snapshot}")
    print(f"== 식별자 규칙: {rules_src} (re.ASCII), stopwords={sorted(stop)}")

    # (a)
    man_problems, man_info, manifest = check_manifest(
        root, pages, args.documents_jsonl, args.expected_source, exp_snapshot,
        args.expected_documents_sha256 or None)
    a_ok = not man_problems
    print(f"\n(a) manifest: {'PASS' if a_ok else 'FAIL'}  "
          f"(페이지 {man_info.get('pages', '-')}, 컴파일 {man_info.get('compiled_by', '-')})")
    for pr in man_problems:
        print(f"    - {pr}")
    report["a_manifest"] = {"pass": a_ok, "problems": man_problems, "info": man_info}

    # (b)
    manifest_cb = man_info.get("compiled_by") if manifest else None
    exp_cb = []
    if manifest_cb:
        exp_cb.append(("manifest", manifest_cb))
    if args.expected_compiled_by and args.expected_compiled_by != manifest_cb:
        exp_cb.append(("expected", args.expected_compiled_by))
    prov_problems, prov_values = check_provenance(pages, root, args.expected_source,
                                                  exp_snapshot, exp_commit, exp_cb)
    b_ok = not prov_problems
    print(f"\n(b) 출처: {'PASS' if b_ok else 'FAIL'}  ({len(prov_problems)}건)")
    for k, v in prov_values.items():
        print(f"    {k}: {v}")
    by_key = defaultdict(int)
    for _, key, _ in prov_problems:
        by_key[key] += 1
    if prov_problems:
        print(f"    항목별: {dict(by_key)}; 처음 3건: {prov_problems[:3]}")
    report["b_provenance"] = {"pass": b_ok, "values": prov_values,
                              "problems": [list(x) for x in prov_problems]}

    # (c)
    findings, version_hits, per_page_ids, n_ref, path_only = check_identifiers(
        pages, root, docs, scope_strings, pats, stop)
    n_absent = len(findings.get("absent", {}))
    print(f"\n(c) 본문 식별자 vs 컴파일 입력: {'PASS' if n_absent == 0 else 'FAIL'}  "
          f"(참조 식별자 {n_ref}개, 그중 경로·scope 이름에만 있는 것 {len(path_only)}개)")
    for cls in ("absent", "hex_reformatted", "case_variant", "substring_only"):
        items = findings.get(cls, {})
        occ = sum(len(v) for v in items.values())
        print(f"    {cls:16s}: {len(items):4d} identifiers, {occ:5d} occurrences")
    for cls in ("absent", "hex_reformatted", "case_variant"):
        items = findings.get(cls, {})
        if not items:
            continue
        print(f"  -- {cls} --")
        hexes = sorted(i for i in items if i.lower().startswith("0x"))
        others = sorted((i for i in items if not i.lower().startswith("0x")),
                        key=lambda i: -len(items[i]))
        for ident in hexes + others:
            occ = items[ident]
            print(f"    {ident}  x{len(occ)} in {len({o[0] for o in occ})} page(s)")
            for pg, ln, ctx in occ[: args.max_lines]:
                print(f"        {pg}:{ln}: {ctx}")
    if version_hits:
        print(f"  -- (c2) 코퍼스 본문에 없는 버전·개정 표기 (참고): {len(version_hits)} --")
        for phrase, occ in sorted(version_hits.items(), key=lambda kv: -len(kv[1])):
            print(f"    {phrase!r} x{len(occ)}")
            for pg, ln, ctx in occ[: args.max_lines]:
                print(f"        {pg}:{ln}: {ctx}")
    report["c_identifiers"] = {
        "pass": n_absent == 0,
        **{cls: {i: [list(o) for o in occ] for i, occ in items.items()}
           for cls, items in findings.items()}}
    report["c2_versions"] = {k: [list(o) for o in v] for k, v in version_hits.items()}

    unsupported = check_hex_name_pairs(pages, root, docs, pats, stop)
    n_unsup = sum(len(v) for v in unsupported.values())
    print(f"  -- (c3) 코퍼스에 있는 hex ID 인데 코퍼스가 그 옆에 둔 적 없는 이름과 붙은 줄 (검토): "
          f"{len(unsupported)} IDs, {n_unsup} lines --")
    for h in sorted(unsupported, key=lambda k: -len(unsupported[k])):
        occ = unsupported[h]
        print(f"    {h} x{len(occ)}")
        for pg, ln, names, ctx in occ[: args.max_lines]:
            print(f"        {pg}:{ln}: {ctx}")
    report["c3_unsupported_pairs"] = {h: [list(map(str, o)) for o in v] for h, v in unsupported.items()}

    # (d)
    excl = check_excluded(pages, root, scope, unsupported)
    excl_ids = {k.split(" ")[0] for k in excl}
    n_excl_leak = sum(1 for occ in excl.values() for o in occ if o[2]) + sum(
        1 for i in findings.get("absent", {}) if _norm_hex(i) in excl_ids)
    d_ok = n_excl_leak == 0
    print(f"\n(d) 제외 ID 유출: {'PASS' if d_ok else 'FAIL'}  (유출 {n_excl_leak}건)")
    for k, occ in excl.items():
        flagged = sum(1 for o in occ if o[2])
        print(f"    {k}: {len(occ)} lines, {flagged} with unsupported pair")
        for pg, ln, flag, ctx in occ[: max(args.max_lines, 4)]:
            print(f"        {pg}:{ln}: {flag} {ctx}")
    report["d_excluded"] = {"pass": d_ok, "leaks": n_excl_leak,
                            "hits": {k: [list(map(str, o)) for o in v] for k, v in excl.items()}}

    # (e)
    led_problems, led_info = check_ledger(root, args.expected_source, exp_snapshot, len(pages),
                                          manifest_cb)
    e_ok = not led_problems
    print(f"\n(e) 구축 원장: {'PASS' if e_ok else 'FAIL'}  {led_info}")
    for pr in led_problems[:10]:
        print(f"    - {pr}")
    report["e_ledger"] = {"pass": e_ok, "problems": led_problems, "info": led_info}

    # (f)
    link_problems, link_info = check_links(pages, root, scope)
    if link_info["linked_pages"] == 0:
        link_problems.insert(0, ("-", 0, f"'{SECTION_HEADER}' 가 있는 페이지가 없다 — "
                                        "WIKI_ROOT=<이 위키> 로 linker/crosslink_wiki.py 를 돌릴 것"))
    f_ok = not link_problems
    print(f"\n(f) 상호링크: {'PASS' if f_ok else 'FAIL'}  (링크 섹션이 있는 페이지 "
          f"{link_info['linked_pages']}, 링크 {link_info['links']}개, 문제 {len(link_problems)}건)")
    for pg, ln, msg in link_problems[:20]:
        print(f"    - {pg}:{ln}: {msg}")
    report["f_links"] = {"pass": f_ok, "info": link_info,
                         "problems": [list(x) for x in link_problems]}

    # (g)
    cov_rows, cov_global = check_coverage(pages, root, docs, per_page_ids, pats, stop)
    recall = cov_global["global_recall"]
    print(f"\n(g) 커버리지 (참고): 코퍼스 식별자 중 위키 본문에 있는 것 "
          f"{cov_global['wiki_body_identifiers_in_corpus']}/{cov_global['corpus_identifiers']} "
          f"= {recall:.1%}" if recall is not None else "\n(g) 커버리지 (참고): 코퍼스 식별자 없음")
    low = sorted((r for r in cov_rows if r["recall"] is not None), key=lambda r: r["recall"])[:6]
    for r in low:
        print(f"    {r['page']}: kept {r['kept']}/{r['source_ids']} = {r['recall']:.1%} "
              f"(source docs {r['source_docs']}, not in corpus {r['source_docs_not_in_corpus']})")
    nic = sum(r["source_docs_not_in_corpus"] for r in cov_rows)
    if nic:
        ex = [e for r in cov_rows for e in r["unknown_examples"]][:4]
        print(f"    documents.jsonl 에 없는 프론트매터 source_paths: {nic} (예 {ex})")
    report["g_coverage"] = {"global": cov_global, "pages": cov_rows}

    # (h)
    collisions, odd, n_ids = check_reachability(root)
    print(f"\n(h) 도달성 (참고): page_id {n_ids}개 (참고 기대값 {args.expected_pages}), "
          f"충돌={collisions or '없음'}, 깊이 1 이 아닌 페이지={odd or '없음'}")
    if n_ids != args.expected_pages:
        print(f"    [WARN] 페이지 수 {n_ids} != {args.expected_pages}: 실패한 엔티티의 문서는 C 가 읽을 수 없다")
    report["h_reachability"] = {"collisions": collisions, "odd_depth": odd, "page_ids": n_ids}

    ok = a_ok and b_ok and n_absent == 0 and d_ok and e_ok and f_ok
    summary = (f"a={'ok' if a_ok else 'fail'}, b={'ok' if b_ok else 'fail'}, c_absent={n_absent}, "
               f"c3_unsupported_lines={n_unsup} (검토), d_excluded_leaks={n_excl_leak}, "
               f"e={'ok' if e_ok else 'fail'}, f={'ok' if f_ok else 'fail'}")
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}  ({summary})")
    report["result"] = {"pass": ok, "summary": summary}
    if args.json_out:
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"보고서 -> {args.json_out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
