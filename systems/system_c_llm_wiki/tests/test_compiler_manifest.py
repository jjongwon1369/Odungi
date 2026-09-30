#!/usr/bin/env python3
"""위키 manifest 와 재구축 위키 검사기 테스트. (#27 A 기준 점검)

A 는 색인이 빠진 폴더에서 Retriever 가 청크 수를 대조해 멈춘다. C 는 엔티티 하나가
컴파일에 실패해도 그 페이지만 빠진 채 통과했다. 그래서 컴파일러가 그룹핑 직후
wiki_manifest.json 을 쓰고, 검사기(validation/check_rebuilt_wiki.py)가 그것을 대조한다.

  컴파일러: manifest 순수 함수, 원자적 쓰기, --dry-run 은 아무것도 쓰지 않음,
            첫 엔티티보다 manifest 가 먼저, 예전 페이지 위에 manifest 를 덮지 않음,
            Windows 경로에서도 그룹핑이 같음
  검사기:   깨끗한 위키 통과 / 페이지 누락·입력 sha 불일치·코퍼스 밖 식별자·링크 라벨 오류 실패

API 는 부르지 않는다. 컴파일 경로는 call_llm 을 테스트용 함수로 바꿔 끼워서만 돈다.
실행: python3 systems/system_c_llm_wiki/tests/test_compiler_manifest.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path, PureWindowsPath

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "compiler"))
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "validation"))

import compile_wiki as cw  # noqa: E402
import check_rebuilt_wiki as chk  # noqa: E402

SNAP = "corpus-test:0123abcd"
COMMIT = "deadbeefcafe"
COMPILED_BY = ("openai", "gpt-6-astra")
MANIFEST_KEYS = ["schema", "documents_path", "documents_sha256", "snapshot_id",
                 "compile_provider", "compile_model", "entity_count", "pages"]

# 작은 C3 모양 코퍼스. 0x0071/0x0072 는 실제처럼 ResourceMonitoring.xml 하나를 공유한다.
DOCS = {
    "data_model/1.7/clusters/OnOff.xml":
        '<cluster id="0x0006" name="On/Off"><attribute id="0x0000" name="OnOff"/>'
        '<attribute id="0x4001" name="OnTime"/></cluster>',
    "src/app/clusters/on-off-server/on-off-server.cpp":
        "void OnOffServer::SetOnOff() {}",
    "data_model/1.7/clusters/Mode_LaundryWasher.xml":
        '<cluster id="0x0051" name="Laundry Washer Mode"><classification baseCluster="Mode Base"/></cluster>',
    "src/app/clusters/mode-base-server/ModeBaseCluster.cpp":
        "namespace ModeBase { class ModeBaseCluster { void ChangeToMode(); }; }",
    "data_model/1.7/clusters/ResourceMonitoring.xml":
        '<clusterIds><clusterId id="0x0071" name="HEPA Filter Monitoring"/>'
        '<clusterId id="0x0072" name="Activated Carbon Filter Monitoring"/></clusterIds>'
        '<attribute name="Condition"/>',
    "data_model/1.7/device_types/LaundryWasher.xml":
        '<deviceType id="0x0073" name="Laundry Washer"><cluster id="0x0006" name="On/Off" side="server"/>'
        '<cluster id="0x0051" name="Laundry Washer Mode" side="server"/>'
        '<cluster id="0x0072" name="Activated Carbon Filter Monitoring" side="server"/></deviceType>',
}


def _cluster(cid, name, spec, impl):
    return {"cluster_id": cid, "cluster_name": name, "specification_path": spec,
            "sdk_definition_path": f"src/app/zap-templates/zcl/data-model/chip/{cid}.xml",
            "implementation_path": impl, "documentation_status": "absent"}


SCOPE = {
    "repository": {"commit_sha": COMMIT},
    "clusters": [
        _cluster("0x0006", "On/Off", "data_model/1.7/clusters/OnOff.xml",
                 "src/app/clusters/on-off-server/on-off-server.cpp"),
        _cluster("0x0051", "Laundry Washer Mode", "data_model/1.7/clusters/Mode_LaundryWasher.xml",
                 "src/app/clusters/mode-base-server/ModeBaseCluster.cpp"),
        _cluster("0x0071", "HEPA Filter Monitoring", "data_model/1.7/clusters/ResourceMonitoring.xml",
                 "src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp"),
        _cluster("0x0072", "Activated Carbon Filter Monitoring",
                 "data_model/1.7/clusters/ResourceMonitoring.xml",
                 "src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp"),
    ],
    "products": [{"name": "Laundry Washer", "id": "0x0073",
                  "definition_path": "data_model/1.7/device_types/LaundryWasher.xml",
                  "direct_cluster_ids": ["0x0006", "0x0051", "0x0072"], "base_cluster_ids": []}],
    "source_sets": [], "support_definitions": [],
    "excluded_device_types": ["Laundry Dryer:0x007C"],
    "excluded_cabinet_clusters": ["0x0048"],
}

# 컴파일 모델이 썼다고 치는 본문. 식별자는 전부 DOCS 에 있고, 링크는 scope.json 과 맞는다.
# 링크 라벨 형식은 linker/crosslink_wiki.py 와 같다. 병합 페이지(0x0071)를 0x0072 로 가리키는
# 링크는 그 클러스터 자신의 이름을 쓰고, 병합 페이지의 기기 줄에는 실제로 쓰는 ID 를 붙인다
# (감사 #47 에서 고치기로 한 형식).
BODIES = {
    "clusters/0x0006-on-off.md": (
        "# On/Off\n\n## 스펙\n\n클러스터 `0x0006` On/Off. 속성 `OnOff` (`0x0000`), `OnTime` (`0x4001`).\n\n"
        "## 구현\n\n`OnOffServer::SetOnOff()` 가 값을 바꾼다.\n\n"
        "## 관련 페이지\n\n**사용 기기**\n\n- [Laundry Washer](../device-types/laundry-washer.md)\n"),
    "clusters/0x0051-laundry-washer-mode.md": (
        "# Laundry Washer Mode\n\n## 스펙\n\n클러스터 `0x0051` Laundry Washer Mode 는 Mode Base 를 따른다.\n\n"
        "## 관련 페이지\n\n**베이스 클러스터**\n\n- [ModeBase](../base/modebase.md)\n\n"
        "**사용 기기**\n\n- [Laundry Washer](../device-types/laundry-washer.md)\n"),
    "clusters/0x0071-hepa-filter-monitoring.md": (
        "# HEPA Filter Monitoring\n\n## 스펙\n\n`0x0071` HEPA Filter Monitoring 과 `0x0072` Activated Carbon "
        "Filter Monitoring 은 같은 정의를 쓴다. 속성 `Condition`.\n\n"
        "## 관련 페이지\n\n**사용 기기**\n\n- [Laundry Washer](../device-types/laundry-washer.md)"
        " (사용 클러스터: Activated Carbon Filter Monitoring `0x0072`)\n"),
    "base/modebase.md": (
        "# ModeBase\n\n## 구현\n\n`ModeBaseCluster` 가 `ChangeToMode` 를 처리한다.\n\n"
        "## 관련 페이지\n\n**파생 클러스터**\n\n"
        "- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)\n"),
    "device-types/laundry-washer.md": (
        "# Laundry Washer\n\n## 스펙\n\n기기 `0x0073` Laundry Washer 는 서버 클러스터 `0x0006`, `0x0051`, "
        "`0x0072` 를 둔다.\n\n"
        "## 관련 페이지\n\n**직접 클러스터**\n\n"
        "- [On/Off `0x0006`](../clusters/0x0006-on-off.md)\n"
        "- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)\n"
        "- [Activated Carbon Filter Monitoring `0x0072`](../clusters/0x0071-hepa-filter-monitoring.md)\n"),
}


# ---------------------------------------------------------------------------
# 도우미
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def cw_state(**overrides):
    """compile_wiki 전역을 바꿨다가 되돌린다. 다른 테스트 파일도 같은 모듈을 쓴다."""
    names = ["WIKI_ROOT", "CORPUS_DOCS", "SCOPE_JSON", "MODEL_PROVIDER", "MODEL_NAME",
             "CORPUS_SNAPSHOT_ID", "CORPUS_DOCS_SHA256", "call_llm", "Path"]
    saved = {n: getattr(cw, n) for n in names}
    try:
        for k, v in overrides.items():
            setattr(cw, k, v)
        yield
    finally:
        for k, v in saved.items():
            setattr(cw, k, v)


@contextlib.contextmanager
def quiet():
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out
    out.write(err.getvalue())


@contextlib.contextmanager
def argv(args):
    saved = sys.argv
    sys.argv = ["compile_wiki.py", *args]
    try:
        yield
    finally:
        sys.argv = saved


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_corpus(tmp: Path) -> dict:
    docs = tmp / "documents.jsonl"
    docs.write_text("".join(
        json.dumps({"snapshot_id": SNAP, "metadata": {"relative_path": rel}, "text": text},
                   ensure_ascii=False) + "\n"
        for rel, text in DOCS.items()), encoding="utf-8")
    scope = tmp / "scope.json"
    scope.write_text(json.dumps(SCOPE, ensure_ascii=False), encoding="utf-8")
    snap = tmp / "snapshot.json"
    snap.write_text(json.dumps({"snapshot_id": SNAP, "commit_hash": COMMIT}), encoding="utf-8")
    return {"docs": docs, "scope": scope, "snap": snap, "wiki": tmp / "wiki-c3"}


def frontmatter(e, source_paths, corpus_source) -> str:
    """compile_wiki.compile_entity 와 같은 모양의 프론트매터."""
    return ("---\n"
            f"entity: {e.name}\n"
            f"ids: {e.ids}\n"
            f"source_paths: {source_paths}\n"
            f"commit_hash: {COMMIT}\n"
            f"doc_type: {e.kind}\n"
            f"compiled_by: {COMPILED_BY[0]}/{COMPILED_BY[1]}\n"
            f"corpus_source: {corpus_source}\n"
            f"corpus_snapshot: {SNAP}\n"
            "---\n\n")


def build_clean_wiki(tmp: Path) -> dict:
    """컴파일러 코드(그룹핑·manifest·원장)로 위키를 만들고 본문만 BODIES 로 채운다."""
    fx = make_corpus(tmp)
    with cw_state(WIKI_ROOT=fx["wiki"], CORPUS_DOCS=fx["docs"], SCOPE_JSON=fx["scope"],
                  MODEL_PROVIDER=COMPILED_BY[0], MODEL_NAME=COMPILED_BY[1]), quiet():
        ents = cw.discover_and_group()
        manifest = cw.build_manifest(ents, {
            "documents_path": cw.CORPUS_DOCS.as_posix(),
            "documents_sha256": cw.CORPUS_DOCS_SHA256,
            "snapshot_id": cw.CORPUS_SNAPSHOT_ID,
        }, cw.MODEL_PROVIDER, cw.MODEL_NAME)
        cw.write_manifest(manifest)
        for e in ents.values():
            if not e.files:
                continue
            out = cw.target_wiki_path(e)
            rel = out.relative_to(fx["wiki"]).as_posix()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(frontmatter(e, [p for _, p, _ in e.files], cw.CORPUS_DOCS.as_posix())
                           + BODIES[rel], encoding="utf-8")
            cw.record_build_call(e.key, 1, {
                "uncached_input": 1000, "cache_creation": 0, "cache_read": 24, "output": 300,
                "api_shape": "openai_chat",
                "usage_raw": {"prompt_tokens": 1024, "completion_tokens": 300,
                              "prompt_tokens_details": {"cached_tokens": 24}}})
        cw.write_build_tokens(COMMIT)
    assert sorted(manifest["pages"]) == sorted(BODIES), manifest["pages"]
    fx["manifest"] = manifest
    return fx


def run_checker(fx: dict, *extra) -> tuple:
    args = [str(fx["wiki"]), str(fx["docs"]), "--scope-json", str(fx["scope"]),
            "--snapshot-json", str(fx["snap"]), "--expected-source", fx["docs"].as_posix(),
            "--expected-documents-sha256", sha256(fx["docs"]), "--expected-pages", "5", *extra]
    with quiet() as out:
        code = chk.main(args)
    return code, out.getvalue()


def fresh_clean() -> dict:
    return build_clean_wiki(Path(tempfile.mkdtemp()))


# ---------------------------------------------------------------------------
# 컴파일러
# ---------------------------------------------------------------------------

def test_build_manifest_is_pure_and_matches_interface():
    tmp = Path(tempfile.mkdtemp())
    ents = {
        "cluster:x": cw.Entity("cluster:x", "cluster", "On/Off", ["0x0006"], [("spec", "a.xml", "t")]),
        "base:ModeBase": cw.Entity("base:ModeBase", "base", "ModeBase", [], [("impl", "b.cpp", "t")]),
        "base:AlarmBase": cw.Entity("base:AlarmBase", "base", "AlarmBase", [], []),   # 파일 없음
    }
    meta = {"documents_path": "corpus/tiers/c3/processed/documents.jsonl",
            "documents_sha256": "ab" * 32, "snapshot_id": SNAP}
    outs = []
    for root in (tmp / "w1", Path("systems/system_c_llm_wiki/wiki-c3")):
        with cw_state(WIKI_ROOT=root):
            outs.append(cw.build_manifest(ents, meta, "openai", "gpt-6-astra"))
    m = outs[0]
    assert outs[0] == outs[1], "위키 경로에 따라 manifest 가 달라졌다"
    assert list(m) == MANIFEST_KEYS, list(m)
    assert m["schema"] == 1 and m["compile_provider"] == "openai" and m["compile_model"] == "gpt-6-astra"
    assert m["pages"] == ["base/modebase.md", "clusters/0x0006-on-off.md"], m["pages"]
    assert m["entity_count"] == 2, "파일 없는 엔티티는 페이지가 생기지 않으므로 빠져야 한다"
    assert m["documents_sha256"] == "ab" * 32 and m["snapshot_id"] == SNAP
    assert not any(tmp.iterdir()), "순수 함수가 파일을 만들었다"
    print("  ✓ build_manifest: 합의한 8개 키·순서, 상대 posix 경로 정렬, 빈 엔티티 제외, 파일 안 씀")


def test_write_manifest_is_atomic():
    tmp = Path(tempfile.mkdtemp())
    with cw_state(WIKI_ROOT=tmp / "wiki"):
        m = {"schema": 1, "pages": ["a/b.md"]}
        path = cw.write_manifest(m)
        assert path == tmp / "wiki" / "wiki_manifest.json"
        assert json.loads(path.read_text(encoding="utf-8")) == m
        assert cw.read_manifest() == m
        assert not (tmp / "wiki" / "wiki_manifest.json.tmp").exists(), "임시파일이 남았다"
        path.write_text("{깨진", encoding="utf-8")
        assert "_unreadable" in cw.read_manifest()
    print("  ✓ write_manifest 원자적 기록 (tmp + os.replace), 깨진 manifest 는 '_unreadable'")


def test_manifest_conflict_rules():
    new = {"schema": 1, "documents_sha256": "a" * 64, "pages": ["x.md"]}
    assert cw.manifest_conflict(None, new, []) is None, "빈 위키는 막을 이유가 없다"
    assert cw.manifest_conflict({"documents_sha256": "b"}, new, []) is None
    assert "manifest 없이" in cw.manifest_conflict(None, new, ["x.md"])
    assert cw.manifest_conflict(dict(new), new, ["x.md"]) is None, "같은 입력의 이어하기는 허용"
    r = cw.manifest_conflict({**new, "documents_sha256": "b" * 64}, new, ["x.md"])
    assert r and "documents_sha256" in r, r
    assert "_unreadable" in cw.manifest_conflict({"_unreadable": "x"}, new, ["x.md"])
    print("  ✓ manifest_conflict: 기존 페이지 + (manifest 없음 | 다른 입력 | 깨짐) 일 때만 막음")


def test_dry_run_writes_nothing():
    fx = make_corpus(Path(tempfile.mkdtemp()))
    calls = []
    with cw_state(CORPUS_DOCS=fx["docs"], SCOPE_JSON=fx["scope"],
                  call_llm=lambda *a, **k: calls.append(k)), \
            argv(["--dry-run", "--wiki-root", str(fx["wiki"])]), quiet() as out:
        cw.main()
    assert not fx["wiki"].exists(), f"--dry-run 이 {fx['wiki']} 를 만들었다"
    assert not calls, "--dry-run 이 call_llm 을 불렀다"
    assert out.getvalue().count("[dry-run]") == 5, out.getvalue()
    print("  ✓ --dry-run: manifest·원장·페이지 모두 안 씀, LLM 호출 0")


def test_manifest_written_before_first_entity():
    """manifest 는 첫 엔티티 컴파일보다 먼저 쓰인다. API 대신 바로 실패하는 함수를 끼운다."""
    fx = make_corpus(Path(tempfile.mkdtemp()))
    seen = []

    def offline(system_prompt, user_prompt, provider=None, model=None, entity_key="-", attempt=1):
        seen.append((entity_key, (fx["wiki"] / "wiki_manifest.json").exists()))
        raise RuntimeError("테스트: API 를 부르지 않는다")

    with cw_state(CORPUS_DOCS=fx["docs"], SCOPE_JSON=fx["scope"], MODEL_PROVIDER="openai",
                  MODEL_NAME="gpt-6-astra", call_llm=offline), \
            argv(["--wiki-root", str(fx["wiki"])]), quiet():
        try:
            cw.main()
            raise AssertionError("전부 실패했는데 exit 0")
        except SystemExit as exc:
            assert exc.code == 1, exc.code
    assert len(seen) == 5 and all(flag for _, flag in seen), seen
    m = json.loads((fx["wiki"] / "wiki_manifest.json").read_text(encoding="utf-8"))
    assert list(m) == MANIFEST_KEYS
    assert m["documents_path"] == fx["docs"].as_posix()
    assert m["documents_sha256"] == sha256(fx["docs"]), "파일 바이트의 sha256 이어야 한다"
    assert m["snapshot_id"] == SNAP
    assert (m["compile_provider"], m["compile_model"]) == ("openai", "gpt-6-astra")
    assert m["entity_count"] == 5 and m["pages"] == sorted(BODIES), m
    assert not any(fx["wiki"].rglob("*.md")), "실패한 엔티티의 페이지가 생겼다"
    print("  ✓ 실제 실행 경로: 엔티티 5개 모두 manifest 가 이미 있는 상태에서 호출, 값이 합의 형식과 같음")


def test_refuses_to_label_old_pages():
    """예전 컴파일러 페이지가 있는 폴더에 manifest 를 붙이지 않는다 (--force 전체 실행만 허용)."""
    fx = make_corpus(Path(tempfile.mkdtemp()))
    old = fx["wiki"] / "clusters" / "0x0006-on-off.md"
    old.parent.mkdir(parents=True)
    old.write_text("---\nentity: On/Off\ncompiled_by: openai/gpt-4o-mini\n---\n\n# On/Off\n", encoding="utf-8")
    calls = []

    def offline(*a, **k):
        calls.append(k.get("entity_key"))
        raise RuntimeError("테스트: API 를 부르지 않는다")

    for extra in ([], ["--force", "--only", "base:ModeBase"], ["--force", "--limit", "2"]):
        with cw_state(CORPUS_DOCS=fx["docs"], SCOPE_JSON=fx["scope"], call_llm=offline), \
                argv(["--wiki-root", str(fx["wiki"]), *extra]), quiet():
            try:
                cw.main()
                raise AssertionError(f"{extra}: 막지 않았다")
            except SystemExit as exc:
                assert isinstance(exc.code, str) and "manifest 없이" in exc.code, exc.code
        assert not (fx["wiki"] / "wiki_manifest.json").exists(), extra
    assert not calls, "막았어야 할 실행이 LLM 까지 갔다"
    with cw_state(CORPUS_DOCS=fx["docs"], SCOPE_JSON=fx["scope"], call_llm=offline), \
            argv(["--wiki-root", str(fx["wiki"]), "--force"]), quiet():
        try:
            cw.main()
        except SystemExit as exc:
            assert exc.code == 1, exc.code
    assert (fx["wiki"] / "wiki_manifest.json").exists() and len(calls) == 5
    print("  ✓ manifest 없는 예전 페이지: 기본·--force --only·--force --limit 는 막고, --force 전체만 진행")


def test_full_force_rebuild_removes_old_pages_first():
    """전체 --force 재구축은 옛 페이지와 manifest 밖 페이지를 먼저 지운다. 실패한 엔티티의 옛 페이지가
    남아 새 manifest 의 보증을 받는 일이 없어야 한다. (#27 A 기준 점검)"""
    fx = make_corpus(Path(tempfile.mkdtemp()))
    old = fx["wiki"] / "clusters" / "0x0006-on-off.md"
    old.parent.mkdir(parents=True)
    old.write_text("---\nentity: On/Off\ncompiled_by: openai/gpt-4o-mini\n---\n\n# On/Off\n", encoding="utf-8")
    stray = fx["wiki"] / "misc" / "stray.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("# stray\n", encoding="utf-8")

    def offline(*a, **k):
        raise RuntimeError("테스트: API 를 부르지 않는다")
    with cw_state(CORPUS_DOCS=fx["docs"], SCOPE_JSON=fx["scope"], call_llm=offline), \
            argv(["--wiki-root", str(fx["wiki"]), "--force"]), quiet():
        try:
            cw.main()
        except SystemExit as exc:
            assert exc.code == 1, exc.code
    assert not old.exists() and not stray.exists(), "옛 페이지나 manifest 밖 페이지가 남았다"
    assert (fx["wiki"] / "wiki_manifest.json").exists()
    print("  ✓ 전체 --force: 옛 페이지·manifest 밖 페이지를 먼저 지우고 manifest 를 씀(실패하면 페이지가 빠진 채로 남음)")


def test_windows_paths_group_like_posix():
    """str(Path.parent) 는 Windows 에서 '\\' 라 공유 구현 폴더가 엉뚱한 클러스터로 갔다. (감사 #143)"""
    with cw_state(Path=PureWindowsPath):
        p2e, d2e, ents, c2k = cw.build_registry(SCOPE)
        mode = cw.classify(PureWindowsPath("src/app/clusters/mode-base-server/ModeBaseCluster.cpp"),
                           p2e, d2e, ents, c2k)
        onoff = cw.classify(PureWindowsPath("src/app/clusters/on-off-server/on-off-server.cpp"),
                            p2e, d2e, ents, c2k)
    assert mode == ("base:ModeBase", "impl"), mode
    assert onoff == ("cluster:data_model/1.7/clusters/OnOff.xml", "impl"), onoff
    assert "src/app/clusters/mode-base-server" in d2e and not any("\\" in k for k in d2e), sorted(d2e)
    print("  ✓ Windows 경로: mode-base-server → base:ModeBase (예전 코드는 Laundry Washer Mode)")


# ---------------------------------------------------------------------------
# 검사기
# ---------------------------------------------------------------------------

def test_identifier_parser_matches_yaml():
    text = (REPO / "systems/system_a_rag/rag_proto/configs/pipeline.yaml").read_text(encoding="utf-8")
    pats, stops = chk.parse_identifiers_block(text)
    assert pats and stops, (pats, stops)
    try:
        import yaml  # type: ignore
    except ImportError:
        print("  ✓ pyyaml 없는 파서가 A 규칙을 읽음 (pyyaml 이 없어 대조는 건너뜀)")
        return
    ident = yaml.safe_load(text)["identifiers"]
    assert pats == ident["patterns"] and stops == ident["stopwords"], (pats, ident)
    print("  ✓ pyyaml 없는 파서 = yaml.safe_load (A pipeline.yaml identifiers)")


def test_checker_passes_clean_wiki():
    fx = fresh_clean()
    code, out = run_checker(fx)
    assert code == 0, out
    assert "RESULT: PASS" in out and "(a) manifest: PASS" in out and "(f) 상호링크: PASS" in out, out
    print("  ✓ 깨끗한 위키(컴파일러 코드로 만든 manifest·원장 + linker 형식 링크) → PASS, exit 0")


def test_checker_fails_missing_page():
    fx = fresh_clean()
    (fx["wiki"] / "clusters" / "0x0051-laundry-washer-mode.md").unlink()
    code, out = run_checker(fx)
    assert code == 1, out
    assert "(a) manifest: FAIL" in out and "clusters/0x0051-laundry-washer-mode.md" in out, out
    print("  ✓ manifest 에 있는 페이지가 없음 → (a) FAIL, exit 1")


def test_checker_fails_extra_page():
    fx = fresh_clean()
    (fx["wiki"] / "guides").mkdir()
    (fx["wiki"] / "guides" / "notes.md").write_text("# 메모\n", encoding="utf-8")
    code, out = run_checker(fx)
    assert code == 1 and "manifest 에 없는 페이지 1개" in out, out
    print("  ✓ manifest 에 없는 .md (에이전트 목차에 보임) → (a) FAIL")


def test_checker_fails_wrong_documents_sha():
    fx = fresh_clean()
    mpath = fx["wiki"] / "wiki_manifest.json"
    m = json.loads(mpath.read_text(encoding="utf-8"))
    m["documents_sha256"] = "0" * 64
    mpath.write_text(json.dumps(m), encoding="utf-8")
    code, out = run_checker(fx)
    assert code == 1 and "(a) manifest: FAIL" in out and "다른 입력으로 컴파일" in out, out
    # manifest 는 맞아도 저장소 파일이 A 의 색인 입력과 다르면 실패
    fx2 = fresh_clean()
    code2, out2 = run_checker(fx2, "--expected-documents-sha256", "f" * 64)
    assert code2 == 1 and "A 가 색인한 입력" in out2, out2
    print("  ✓ manifest documents_sha256 ≠ 코퍼스 파일, 코퍼스 파일 ≠ A 색인 입력 → 둘 다 (a) FAIL")


def test_checker_fails_out_of_corpus_identifier():
    fx = fresh_clean()
    page = fx["wiki"] / "clusters" / "0x0051-laundry-washer-mode.md"
    leak = "Heater 조건에는 `OvenCavityOperationalState` 가 붙는다."
    text = page.read_text(encoding="utf-8").replace("\n## 관련 페이지", f"\n{leak}\n\n## 관련 페이지")
    page.write_text(text, encoding="utf-8")
    ln = text.split("\n").index(leak) + 1
    code, out = run_checker(fx)
    assert code == 1, out
    assert "c_absent=1" in out and "OvenCavityOperationalState" in out, out
    assert f"clusters/0x0051-laundry-washer-mode.md:{ln}:" in out, out
    print(f"  ✓ 코퍼스 밖 식별자 → (c) FAIL, page:line 보고 (…laundry-washer-mode.md:{ln})")


def test_checker_fails_excluded_id():
    fx = fresh_clean()
    page = fx["wiki"] / "device-types" / "laundry-washer.md"
    text = page.read_text(encoding="utf-8").replace(
        "\n## 관련 페이지", "\n`0x007C` Laundry Dryer 도 같은 모드를 쓴다.\n\n## 관련 페이지")
    page.write_text(text, encoding="utf-8")
    code, out = run_checker(fx)
    assert code == 1 and "(d) 제외 ID 유출: FAIL" in out and "0x007C (excluded device type" in out, out
    print("  ✓ scope.json 제외 기기 ID(0x007C) → (d) FAIL")


def test_checker_fails_bad_links():
    """wiki-astra 에서 실제로 나온 링커 오류 두 가지 + 접두사 불일치 + 링크 없음."""
    cases = {
        # 병합 페이지 대표 이름을 다른 ID 에 붙임 (wiki-astra/device-types/refrigerator.md:71)
        "라벨 이름": ("[Activated Carbon Filter Monitoring `0x0072`]", "[HEPA Filter Monitoring `0x0072`]",
                  "scope.json 에서 0x0072 는 'Activated Carbon Filter Monitoring'"),
        # 병합 페이지라 링크를 떨굼 (wiki-astra/device-types/room-air-conditioner.md)
        "링크 누락": ("- [Activated Carbon Filter Monitoring `0x0072`]"
                  "(../clusters/0x0071-hepa-filter-monitoring.md)\n", "",
                  "링크가 없는 ID ['0x0072']"),
        "접두사": ("[On/Off `0x0006`]", "[On/Off `0x0051`]", "라벨 ID 0x0051 가 대상 clusters/0x0006-on-off.md"),
        # 병합 페이지 기기 줄 설명의 이름 오류
        "설명 이름": ("(사용 클러스터: Activated Carbon Filter Monitoring `0x0072`)",
                  "(사용 클러스터: HEPA Filter Monitoring `0x0072`)",
                  "설명 'HEPA Filter Monitoring `0x0072`'"),
    }
    for what, (old, new, expect) in cases.items():
        fx = fresh_clean()
        page = fx["wiki"] / ("clusters/0x0071-hepa-filter-monitoring.md" if what == "설명 이름"
                             else "device-types/laundry-washer.md")
        text = page.read_text(encoding="utf-8")
        assert old in text, what
        page.write_text(text.replace(old, new), encoding="utf-8")
        code, out = run_checker(fx)
        assert code == 1 and "(f) 상호링크: FAIL" in out and expect in out, (what, out)
    fx = fresh_clean()
    for p in fx["wiki"].rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        p.write_text(t[: t.find("\n## 관련 페이지")] + "\n", encoding="utf-8")
    code, out = run_checker(fx)
    assert code == 1 and "링크 섹션이 있는 페이지 0" in out, out
    print("  ✓ 링크 라벨 이름·ID 누락·접두사 불일치·설명 이름·링커 미실행 → (f) FAIL")


def test_checker_fails_mixed_compile_model():
    fx = fresh_clean()
    page = fx["wiki"] / "base" / "modebase.md"
    page.write_text(page.read_text(encoding="utf-8").replace(
        "compiled_by: openai/gpt-6-astra", "compiled_by: openai/gpt-4o-mini"), encoding="utf-8")
    code, out = run_checker(fx)
    assert code == 1 and "(b) 출처: FAIL" in out and "gpt-4o-mini" in out, out
    print("  ✓ 다른 모델로 만든 페이지가 섞임 → (b) FAIL")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"위키 manifest·검사기 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
