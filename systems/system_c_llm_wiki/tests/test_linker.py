#!/usr/bin/env python3
"""상호링크 생성기(crosslink_wiki.py) 테스트. (#27 A 기준 점검)

실제 위키가 아니라 임시 폴더의 합성 scope.json 과 페이지로 확인한다:
  1. 링크 라벨이 그 ID 자신의 scope.json 이름과 ID다 ('HEPA Filter Monitoring `0x0072`' 금지)
  2. 페이지를 공유하는 두 ID(HEPA 0x0071 / Activated Carbon 0x0072)가 둘 다 걸린다
  3. 병합 페이지의 기기 줄에 그 기기가 실제로 쓰는 ID가 붙는다
  4. --wiki-root 로 준 폴더만 고친다 (환경변수·기본 wiki/ 는 그대로)
  5. 두 번 돌려도 결과가 같다
  6. Windows 경로에서도 ModeBase 묶음이 같다

실행: python3 systems/system_c_llm_wiki/tests/test_linker.py
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager, redirect_stdout
from pathlib import Path, PureWindowsPath

REPO = Path(__file__).resolve().parents[3]
LINKER = REPO / "systems" / "system_c_llm_wiki" / "linker" / "crosslink_wiki.py"
sys.path.insert(0, str(LINKER.parent))

import crosslink_wiki as cl  # noqa: E402

# 실제 scope.json 과 같은 모양의 최소 합성본. HEPA/Activated Carbon 은 spec 파일을 공유해
# 한 페이지(0x0071-hepa-filter-monitoring.md)로 합쳐진다. 기기 ID 0x0072 가 클러스터 ID
# 0x0072 와 숫자가 같은 것도 실제와 같게 둔다.
SCOPE = {
    "clusters": [
        {"cluster_id": "0x0003", "cluster_name": "Identify",
         "specification_path": "dm/clusters/Identify.xml",
         "implementation_path": "src/app/clusters/identify-server/IdentifyCluster.cpp"},
        {"cluster_id": "0x001D", "cluster_name": "Descriptor",
         "specification_path": "dm/clusters/Descriptor-Cluster.xml",
         "implementation_path": "src/app/clusters/descriptor/DescriptorCluster.cpp"},
        {"cluster_id": "0x0051", "cluster_name": "Laundry Washer Mode",
         "specification_path": "dm/clusters/Mode_LaundryWasher.xml",
         "implementation_path": "src/app/clusters/mode-base-server/ModeBaseCluster.cpp"},
        {"cluster_id": "0x0071", "cluster_name": "HEPA Filter Monitoring",
         "specification_path": "dm/clusters/ResourceMonitoring.xml",
         "implementation_path": "src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp"},
        {"cluster_id": "0x0072", "cluster_name": "Activated Carbon Filter Monitoring",
         "specification_path": "dm/clusters/ResourceMonitoring.xml",
         "implementation_path": "src/app/clusters/resource-monitoring-server/ResourceMonitoringCluster.cpp"},
    ],
    "products": [
        {"name": "Room Air Conditioner", "id": "0x0072",
         "direct_cluster_ids": ["0x0003", "0x0071", "0x0072"], "base_cluster_ids": ["0x001D"]},
        {"name": "Refrigerator", "id": "0x0070",
         "direct_cluster_ids": ["0x0003", "0x0072"], "base_cluster_ids": ["0x001D"]},
        {"name": "Laundry Washer", "id": "0x0073",
         "direct_cluster_ids": ["0x0051"], "base_cluster_ids": ["0x001D"]},
    ],
}
NAMES = {c["cluster_id"]: c["cluster_name"] for c in SCOPE["clusters"]}
PAGES = [
    "clusters/0x0003-identify.md",
    "clusters/0x001D-descriptor.md",
    "clusters/0x0051-laundry-washer-mode.md",
    "clusters/0x0071-hepa-filter-monitoring.md",
    "device-types/room-air-conditioner.md",
    "device-types/refrigerator.md",
    "device-types/laundry-washer.md",
    "base/modebase.md",
]
MERGED = "clusters/0x0071-hepa-filter-monitoring.md"
# 옛 링커가 실제로 남긴 틀린 섹션 (wiki-astra/device-types/refrigerator.md:71 과 같은 꼴)
OLD_FRIDGE_SECTION = (
    "\n## 관련 페이지\n\n**직접 클러스터**\n\n"
    "- [Identify `0x0003`](../clusters/0x0003-identify.md)\n"
    "- [HEPA Filter Monitoring `0x0072`](../clusters/0x0071-hepa-filter-monitoring.md)\n"
)
# 테스트 쪽에서 따로 쓰는 라벨 정규식 (링커의 LABEL_RE 를 믿지 않고 대조)
PAIR = re.compile(r"(?:\[|: |, )([A-Za-z/ ]+?) `(0x[0-9A-F]{4})`")


def make_wiki(root: Path, *, old_fridge=False) -> Path:
    for rel in PAGES:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {p.stem}\n\n본문 {p.stem}.\n", encoding="utf-8")
    if old_fridge:
        p = root / "device-types/refrigerator.md"
        p.write_text(p.read_text(encoding="utf-8").rstrip() + "\n" + OLD_FRIDGE_SECTION,
                     encoding="utf-8")
    return root


@contextmanager
def wiki_root(root: Path):
    """경로 헬퍼가 읽는 전역 WIKI_ROOT 를 잠시 바꾼다. 링커의 [링크] 출력은 삼킨다."""
    old = cl.WIKI_ROOT
    cl.WIKI_ROOT = root
    try:
        with redirect_stdout(io.StringIO()):
            yield root
    finally:
        cl.WIKI_ROOT = old


def section(root: Path, rel: str) -> str:
    return cl.split_section((root / rel).read_text(encoding="utf-8"))[1]


def snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*.md"))}


def linked(*, old_fridge=False) -> Path:
    root = make_wiki(Path(tempfile.mkdtemp()) / "wiki", old_fridge=old_fridge)
    with wiki_root(root):
        cl.link_all(SCOPE, dry_run=False)
    return root


def run_cli(cwd: Path, *args, env_wiki_root=None, encoding=None):
    env = {k: v for k, v in os.environ.items() if k != "WIKI_ROOT"}
    if env_wiki_root is not None:
        env["WIKI_ROOT"] = env_wiki_root
    if encoding:
        env["PYTHONIOENCODING"] = encoding
    p = subprocess.run([sys.executable, str(LINKER), *args], capture_output=True,
                       cwd=str(cwd), env=env)
    return p.returncode, (p.stdout + p.stderr).decode(encoding or "utf-8", errors="replace")


def test_labels_are_own_name_and_id():
    root = linked()
    pairs = []
    for rel in PAGES:
        pairs += PAIR.findall(section(root, rel))
    assert pairs, "라벨이 하나도 없다"
    wrong = [(n, c) for n, c in pairs if NAMES.get(c) != n]
    assert not wrong, wrong
    fridge = section(root, "device-types/refrigerator.md")
    assert ("- [Activated Carbon Filter Monitoring `0x0072`]"
            "(../clusters/0x0071-hepa-filter-monitoring.md)") in fridge, fridge
    assert "HEPA Filter Monitoring `0x0072`" not in fridge, fridge
    assert "`0x0071`" not in fridge, "Refrigerator 는 0x0071 을 안 쓴다"
    print(f"  ✓ 라벨 {len(pairs)}개 전부 scope.json 이름·ID와 일치 (Refrigerator 는 Activated Carbon `0x0072`)")


def test_shared_page_keeps_both_ids():
    root = linked()
    rac = section(root, "device-types/room-air-conditioner.md")
    for line in ("- [HEPA Filter Monitoring `0x0071`](../clusters/0x0071-hepa-filter-monitoring.md)",
                 "- [Activated Carbon Filter Monitoring `0x0072`](../clusters/0x0071-hepa-filter-monitoring.md)"):
        assert line in rac, (line, rac)
    # 순서는 scope.json 의 direct_cluster_ids 순서 그대로
    assert rac.index("`0x0003`") < rac.index("`0x0071`") < rac.index("`0x0072`") < rac.index("`0x001D`")
    print("  ✓ 페이지를 공유하는 0x0071·0x0072 가 Room Air Conditioner 에 둘 다 걸림")


def test_merged_page_tags_device_ids():
    root = linked()
    merged = section(root, MERGED)
    assert ("- [Refrigerator](../device-types/refrigerator.md) "
            "(사용 클러스터: Activated Carbon Filter Monitoring `0x0072`)") in merged, merged
    assert ("- [Room Air Conditioner](../device-types/room-air-conditioner.md) "
            "(사용 클러스터: HEPA Filter Monitoring `0x0071`, "
            "Activated Carbon Filter Monitoring `0x0072`)") in merged, merged
    # 병합이 아닌 페이지는 예전과 같은 모양 (기기 이름만)
    ident = section(root, "clusters/0x0003-identify.md")
    assert "사용 클러스터" not in ident, ident
    assert "- [Refrigerator](../device-types/refrigerator.md)\n" in ident, ident
    print("  ✓ 병합 페이지의 기기 줄에 실제로 쓰는 ID만 붙음 (비병합 페이지는 그대로)")


def test_base_links_unchanged_shape():
    root = linked()
    assert "- [ModeBase](../base/modebase.md)" in section(root, "clusters/0x0051-laundry-washer-mode.md")
    base = section(root, "base/modebase.md")
    assert "- [Laundry Washer Mode `0x0051`](../clusters/0x0051-laundry-washer-mode.md)" in base, base
    print("  ✓ ModeBase 베이스/파생 링크")


def test_label_base_lists_every_id_of_merged_page():
    """Label 파생 판정은 페이지 단위라, 병합 페이지면 두 ID가 다 파생 목록에 오른다."""
    scope = {"clusters": [
        {"cluster_id": "0x0040", "cluster_name": "Fixed Label", "specification_path": "dm/Labels.xml",
         "implementation_path": "src/app/clusters/fixed-label-server/X.cpp"},
        {"cluster_id": "0x0041", "cluster_name": "User Label", "specification_path": "dm/Labels.xml",
         "implementation_path": "src/app/clusters/user-label-server/X.cpp"}],
        "products": []}
    root = Path(tempfile.mkdtemp()) / "wiki"
    for rel, body in (("clusters/0x0040-fixed-label.md", "baseCluster: `Label`"),
                      ("base/label.md", "Label 베이스")):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(f"# t\n\n{body}\n", encoding="utf-8")
    with wiki_root(root):
        assert cl.detect_label_derived(cl.build_graph(scope)[0]) == {"0x0040", "0x0041"}
        cl.link_all(scope, dry_run=False)
    base = section(root, "base/label.md")
    assert "- [Fixed Label `0x0040`](../clusters/0x0040-fixed-label.md)" in base, base
    assert "- [User Label `0x0041`](../clusters/0x0040-fixed-label.md)" in base, base
    print("  ✓ Label 파생 목록이 병합 페이지의 두 ID를 각자 이름으로 담음")


def test_stale_wrong_label_is_replaced():
    root = linked(old_fridge=True)
    text = (root / "device-types/refrigerator.md").read_text(encoding="utf-8")
    assert "HEPA Filter Monitoring `0x0072`" not in text, text
    assert text.count(cl.SECTION_HEADER) == 1, text
    assert text.startswith("# refrigerator\n\n본문 refrigerator.\n"), "본문이 바뀌었다"
    print("  ✓ 옛 링커가 남긴 틀린 섹션을 통째로 교체 (본문은 그대로)")


def test_idempotent():
    root = linked(old_fridge=True)
    before = snapshot(root)
    with wiki_root(root):
        again = cl.link_all(SCOPE, dry_run=False)
        dry = cl.link_all(SCOPE, dry_run=True)
    assert again == 0 and dry == 0, (again, dry)
    assert snapshot(root) == before, "두 번째 실행에서 바이트가 바뀌었다"
    print("  ✓ 두 번 돌려도 바뀐 페이지 0개, 바이트 동일")


def test_check_flags_old_output_and_passes_new():
    root = make_wiki(Path(tempfile.mkdtemp()) / "wiki", old_fridge=True)
    # 옛 링커 출력: RAC 는 0x0071 만, 병합 페이지 기기 줄엔 ID 표시 없음
    rac = root / "device-types/room-air-conditioner.md"
    rac.write_text(rac.read_text(encoding="utf-8").rstrip() + "\n"
                   "\n## 관련 페이지\n\n**직접 클러스터**\n\n"
                   "- [Identify `0x0003`](../clusters/0x0003-identify.md)\n"
                   "- [HEPA Filter Monitoring `0x0071`](../clusters/0x0071-hepa-filter-monitoring.md)\n"
                   "\n**베이스 클러스터**\n\n- [Descriptor `0x001D`](../clusters/0x001D-descriptor.md)\n",
                   encoding="utf-8")
    mp = root / MERGED
    mp.write_text(mp.read_text(encoding="utf-8").rstrip() + "\n"
                  "\n## 관련 페이지\n\n**사용 기기**\n\n"
                  "- [Refrigerator](../device-types/refrigerator.md)\n", encoding="utf-8")
    with wiki_root(root):
        problems, n = cl.check_links(SCOPE)
        joined = "\n".join(problems)
        assert "'HEPA Filter Monitoring `0x0072`' 인데 scope.json 이름은 'Activated Carbon Filter Monitoring'" in joined, joined
        assert "room-air-conditioner.md: 링크 빠진 ID ['0x0072']" in joined, joined
        assert "Refrigerator 줄의 ID [] 인데 실제로 쓰는 ID는 ['0x0072']" in joined, joined
        cl.link_all(SCOPE, dry_run=False)
        problems, n = cl.check_links(SCOPE)
        assert problems == [], problems
        assert n == len(PAGES), n
    # 링커를 돌리지 않은 위키는 섹션 0개로 걸린다
    with wiki_root(make_wiki(Path(tempfile.mkdtemp()) / "wiki")):
        problems, n = cl.check_links(SCOPE)
    assert n == 0 and any("0개" in p for p in problems), problems
    print("  ✓ --check 가 옛 출력의 틀린 라벨·빠진 ID·ID 없는 기기 줄을 잡고, 새 출력은 0건")


def cli_tree() -> Path:
    """리포 루트처럼 생긴 임시 폴더: scope.json + 기본 wiki/ + 다른 위키 두 벌."""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "corpus/metadata").mkdir(parents=True)
    (tmp / "corpus/metadata/scope.json").write_text(json.dumps(SCOPE), encoding="utf-8")
    for rel in ("systems/system_c_llm_wiki/wiki", "wiki-env", "wiki-flag"):
        make_wiki(tmp / rel)
    return tmp


def test_wiki_root_flag_targets_only_given_folder():
    tmp = cli_tree()
    default, env_w, flag_w = (tmp / "systems/system_c_llm_wiki/wiki", tmp / "wiki-env",
                              tmp / "wiki-flag")
    snaps = {w: snapshot(w) for w in (default, env_w, flag_w)}

    # 플래그가 환경변수보다 우선
    rc, out = run_cli(tmp, "--wiki-root", "wiki-flag", env_wiki_root="wiki-env")
    assert rc == 0, out
    assert "[대상] wiki-flag (--wiki-root)" in out, out
    assert snapshot(flag_w) != snaps[flag_w], "--wiki-root 폴더가 안 바뀌었다"
    assert snapshot(env_w) == snaps[env_w], "환경변수 폴더를 건드렸다"
    assert snapshot(default) == snaps[default], "기본 wiki/ 를 건드렸다"

    # 플래그가 없으면 환경변수
    rc, out = run_cli(tmp, env_wiki_root="wiki-env")
    assert rc == 0 and "[대상] wiki-env (환경변수 WIKI_ROOT)" in out, out
    assert snapshot(env_w) != snaps[env_w]
    assert snapshot(default) == snaps[default], "기본 wiki/ 를 건드렸다"

    # 둘 다 없으면 기본값이지만 말없이 고치지 않는다
    rc, out = run_cli(tmp, "--dry-run")
    assert rc == 0 and "[대상] systems/system_c_llm_wiki/wiki (기본값)" in out, out
    assert snapshot(default) == snaps[default], "--dry-run 이 파일을 바꿨다"
    rc, out = run_cli(tmp)
    assert rc == 0 and "[주의]" in out, out

    # 없는 폴더는 0개 갱신으로 넘어가지 않고 멈춘다
    before = snapshot(flag_w)
    rc, out = run_cli(tmp, "--wiki-root", "wiki-typo")
    assert rc == 2 and "[오류]" in out, out
    assert snapshot(flag_w) == before
    print("  ✓ --wiki-root > WIKI_ROOT > 기본값, 준 폴더만 고침, 없는 폴더는 종료 코드 2")


def test_cli_check_exit_codes():
    tmp = cli_tree()
    rc, out = run_cli(tmp, "--wiki-root", "wiki-flag", "--check")
    assert rc == 1 and "섹션이 있는 페이지가 0개" in out, out
    run_cli(tmp, "--wiki-root", "wiki-flag")
    rc, out = run_cli(tmp, "--wiki-root", "wiki-flag", "--check")
    assert rc == 0 and "문제 0건" in out, out
    print("  ✓ --check 종료 코드: 링크 전 1, 링크 후 0")


def test_windows_paths_group_like_posix():
    """Windows 에서는 Path(...).parent 가 역슬래시라 str() 키가 안 맞았다."""
    impl = "src/app/clusters/mode-base-server/ModeBaseCluster.cpp"
    assert str(PureWindowsPath(impl).parent) not in cl.SHARED_IMPL_DIR_TO_BASE  # 옛 방식은 빠짐
    old = cl.Path
    cl.Path = PureWindowsPath
    try:
        info = cl.build_graph(SCOPE)[0]
    finally:
        cl.Path = old
    assert info["0x0051"]["uses_base"] == "ModeBase", info["0x0051"]
    assert info["0x0003"]["uses_base"] is None
    print("  ✓ Windows 경로에서도 0x0051 이 ModeBase 로 묶임 (as_posix)")


def test_cp949_console():
    tmp = cli_tree()
    # LLM 이 쓴 페이지에 cp949 가 못 담는 글자가 있어도 --check 출력이 멈추지 않아야 한다
    p = tmp / "wiki-flag/device-types/refrigerator.md"
    p.write_text(p.read_text(encoding="utf-8") +
                 "\n## 관련 페이지\n\n- [Identify — old `0x0003`](../clusters/0x0003-identify.md)\n",
                 encoding="utf-8")
    for args in (("--help",), ("--wiki-root", "wiki-flag", "--check"),
                 ("--wiki-root", "wiki-flag")):
        rc, out = run_cli(tmp, *args, encoding="cp949")
        assert "UnicodeEncodeError" not in out and "Traceback" not in out, (args, out[-500:])
        assert rc in (0, 1), (args, rc, out[-500:])
    print("  ✓ cp949 콘솔에서 --help·--check·링크 실행이 끝까지 감")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"상호링크 생성기 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
