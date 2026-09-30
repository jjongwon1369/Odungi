#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Wiki 상호링크 생성기 (System C)
====================================
컴파일된 위키 페이지들 사이에 "## 관련 페이지" 섹션을 추가한다.
scope.json 에서 관계를 추론하며, API 호출 없이 순수 로컬 파일 처리다.
컴파일 LLM 이 만든 구조가 아니라 scope.json 관계를 옮겨 적는 결정적 단계다.

컴파일 직후, run_batch 전에 돌린다. 페이지 바이트가 바뀌므로 run_batch 가 남기는
위키 해시도 링크를 넣은 뒤의 페이지로 정해져야 한다. (#27 A 기준 점검)

사용법 (리포 루트에서, --wiki-root 는 compile_wiki.py 에 준 값과 같게):
    python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --wiki-root systems/system_c_llm_wiki/wiki-c3 --dry-run
    python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --wiki-root systems/system_c_llm_wiki/wiki-c3
    python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --wiki-root systems/system_c_llm_wiki/wiki-c3 --check
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCOPE_JSON = Path("corpus/metadata/scope.json")
DEFAULT_WIKI_ROOT = Path("systems/system_c_llm_wiki/wiki")
# 대상 위키. main() 이 --wiki-root > 환경변수 WIKI_ROOT > 기본값 순으로 다시 정한다.
# 아래 경로 헬퍼는 모두 이 전역을 호출 시점에 읽는다 (컴파일 모델별 비교용)
WIKI_ROOT = Path(os.environ.get("WIKI_ROOT") or DEFAULT_WIKI_ROOT)

# compile_wiki.py 와 동일
SHARED_IMPL_DIR_TO_BASE = {
    "src/app/clusters/mode-base-server": "ModeBase",
    "src/app/clusters/alarm-base-server": "AlarmBase",
}

SECTION_HEADER = "## 관련 페이지"


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("/", "-")


def cluster_page(rep_id: str, rep_name: str) -> Path:
    """클러스터 위키 파일 경로. rep_id/rep_name은 merged entity의 대표값."""
    return WIKI_ROOT / "clusters" / f"{rep_id}-{slugify(rep_name)}.md"


def device_page(name: str) -> Path:
    return WIKI_ROOT / "device-types" / f"{slugify(name)}.md"


def base_page(name: str) -> Path:
    return WIKI_ROOT / "base" / f"{slugify(name)}.md"


def rel(from_page: Path, to_page: Path) -> str:
    """wiki 페이지는 모두 한 단계 깊이(wiki/xxx/page.md)이므로 ../folder/file.md."""
    return f"../{to_page.parent.name}/{to_page.name}"


def cluster_label(cid: str, cluster_info: dict) -> str:
    """링크 라벨은 그 ID 자신의 scope.json 이름과 ID다. 병합 페이지의 대표 이름
    (rep_name)을 다른 ID와 짝지으면 'HEPA Filter Monitoring `0x0072`' 같은
    틀린 사실이 페이지에 들어간다. (#27 A 기준 점검)"""
    return f"{cluster_info[cid]['name']} `{cid}`"


def page_ids(rep_id: str, cluster_info: dict) -> list[str]:
    """한 클러스터 페이지가 다루는 ID들 (scope.json 순서). 병합 페이지면 2개 이상."""
    return [cid for cid, info in cluster_info.items() if info["rep_id"] == rep_id]


def split_section(text: str) -> tuple[str, str]:
    """(본문, 관련 페이지 섹션). 섹션이 없으면 두 번째 값은 빈 문자열."""
    i = text.find("\n" + SECTION_HEADER)
    if i < 0:
        return text, ""
    return text[:i], text[i:]


# ---------------------------------------------------------------------------
# 관계 그래프 구축
# ---------------------------------------------------------------------------

def build_graph(scope: dict):
    """
    반환값:
      cluster_info  : id → {name, spec_path, rep_id, uses_base}
      device_info   : name → {id, direct:[ids], base:[ids]}
      cluster_devices: id → [device_names]
    """
    # spec_path 공유 클러스터는 같은 페이지(병합) → spec_path 최초 등록 ID가 대표
    spec_to_rep: dict[str, str] = {}   # spec_path → rep cluster_id
    spec_to_rep_name: dict[str, str] = {}

    cluster_info: dict = {}

    for c in scope.get("clusters", []):
        cid = c["cluster_id"]
        sp = c["specification_path"]
        # as_posix: Windows 에서 str() 은 역슬래시라 '/' 로 쓴 키와 안 맞아
        # ModeBase/AlarmBase 링크가 조용히 빠진다 (#27 A 기준 점검)
        impl_dir = Path(c["implementation_path"]).parent.as_posix()

        uses_base = SHARED_IMPL_DIR_TO_BASE.get(impl_dir)

        if sp not in spec_to_rep:
            spec_to_rep[sp] = cid
            spec_to_rep_name[sp] = c["cluster_name"]

        cluster_info[cid] = {
            "name": c["cluster_name"],
            "spec_path": sp,
            "rep_id": spec_to_rep[sp],
            "rep_name": spec_to_rep_name[sp],
            "uses_base": uses_base,
        }

    # 기기 → 클러스터
    device_info: dict = {}
    for p in scope.get("products", []):
        device_info[p["name"]] = {
            "id": p["id"],
            "direct": p.get("direct_cluster_ids", []),
            "base": p.get("base_cluster_ids", []),
        }

    # 클러스터 → 기기 (역방향)
    cluster_devices: dict = {}
    for dname, di in device_info.items():
        for cid in di["direct"] + di["base"]:
            cluster_devices.setdefault(cid, []).append(dname)

    return cluster_info, device_info, cluster_devices


def detect_label_derived(cluster_info: dict) -> set:
    """wiki 페이지 본문에서 baseCluster: Label 또는 hierarchy: derived + Label 패턴 탐지.

    페이지 단위 판정이므로 병합 페이지면 그 페이지의 ID 전부를 넣는다. 대표 ID만
    넣으면 Label 페이지의 '파생 클러스터' 목록에서 나머지 ID가 빠진다. 이미 붙은
    관련 페이지 섹션은 빼고 본문만 본다 (재실행해도 결과가 같게)."""
    derived = set()
    page_is_derived: dict[Path, bool] = {}
    for cid, info in cluster_info.items():
        page = cluster_page(info["rep_id"], info["rep_name"])
        if page not in page_is_derived:
            body = split_section(page.read_text(encoding="utf-8"))[0] if page.exists() else ""
            page_is_derived[page] = bool(
                re.search(r"baseCluster[`'\s:]*Label", body, re.IGNORECASE))
        if page_is_derived[page]:
            derived.add(cid)
    return derived


# ---------------------------------------------------------------------------
# 섹션 조립 / 파일 업데이트
# ---------------------------------------------------------------------------

def build_section(groups: dict) -> str:
    """groups: {그룹명: [(label, rel_path[, 뒤에 붙일 설명]), ...]}  →  마크다운 섹션 문자열"""
    lines = [f"\n{SECTION_HEADER}\n"]
    for group, items in groups.items():
        if not items:
            continue
        lines.append(f"**{group}**\n")
        for label, path, *note in items:
            lines.append(f"- [{label}]({path}){note[0] if note else ''}")
        lines.append("")
    return "\n".join(lines)


def upsert_section(page: Path, section_md: str, dry_run: bool) -> bool:
    """기존 관련 페이지 섹션을 교체하거나 없으면 추가. 변경 여부 반환."""
    content = page.read_text(encoding="utf-8")
    stripped = split_section(content)[0]
    new_content = stripped.rstrip() + "\n" + section_md
    if content == new_content:
        return False
    if not dry_run:
        page.write_text(new_content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# 페이지 유형별 처리
# ---------------------------------------------------------------------------

def link_cluster_page(cid: str, cluster_info: dict, cluster_devices: dict,
                      label_derived: set, dry_run: bool) -> bool:
    info = cluster_info[cid]
    # merged entity는 대표 ID로만 처리 (중복 방지)
    if info["rep_id"] != cid:
        return False

    page = cluster_page(info["rep_id"], info["rep_name"])
    if not page.exists():
        return False

    ids_on_page = page_ids(cid, cluster_info)
    groups: dict = {}

    # 1) 베이스 클러스터
    base_name = info.get("uses_base")
    if not base_name and cid in label_derived:
        base_name = "Label"
    # merged entity: 다른 ID도 같은 base를 쓰는지 확인
    if not base_name:
        for other_id in ids_on_page:
            if cluster_info[other_id].get("uses_base"):
                base_name = cluster_info[other_id]["uses_base"]
                break
    if base_name:
        bp = base_page(base_name)
        if bp.exists():
            groups["베이스 클러스터"] = [(base_name, rel(page, bp))]

    # 2) 사용 기기 — merged entity의 모든 ID를 합산하되, 병합 페이지면 기기마다
    #    실제로 쓰는 ID를 붙인다. 안 붙이면 HEPA/Activated Carbon 공유 페이지에서
    #    Refrigerator 가 0x0071 도 쓰는 것처럼 읽힌다 (#27 A 기준 점검)
    device_ids: dict[str, list[str]] = {}
    for any_id in ids_on_page:
        for dname in cluster_devices.get(any_id, []):
            used = device_ids.setdefault(dname, [])
            if any_id not in used:
                used.append(any_id)
    if device_ids:
        groups["사용 기기"] = []
        for dname in sorted(device_ids):
            dp = device_page(dname)
            if not dp.exists():
                continue
            note = ""
            if len(ids_on_page) > 1:
                note = " (사용 클러스터: " + ", ".join(
                    cluster_label(i, cluster_info) for i in device_ids[dname]) + ")"
            groups["사용 기기"].append((dname, rel(page, dp), note))

    if not any(v for v in groups.values()):
        return False

    return upsert_section(page, build_section(groups), dry_run)


def link_device_page(dname: str, dinfo: dict, cluster_info: dict,
                     dry_run: bool) -> bool:
    page = device_page(dname)
    if not page.exists():
        return False

    def cluster_items(ids):
        # 같은 페이지를 가리키더라도 ID마다 한 줄 (Room Air Conditioner 는 0x0071 과
        # 0x0072 를 둘 다 쓴다). 페이지 기준으로 거르면 두 번째 ID가 빠진다 (#27 A 기준 점검)
        seen_ids: set = set()
        result = []
        for cid in ids:
            info = cluster_info.get(cid)
            if not info or cid in seen_ids:
                continue
            seen_ids.add(cid)
            cp = cluster_page(info["rep_id"], info["rep_name"])
            if cp.exists():
                result.append((cluster_label(cid, cluster_info), rel(page, cp)))
        return result

    groups: dict = {}
    direct = cluster_items(dinfo["direct"])
    if direct:
        groups["직접 클러스터"] = direct
    base_cls = cluster_items(dinfo["base"])
    if base_cls:
        groups["베이스 클러스터"] = base_cls

    if not any(v for v in groups.values()):
        return False

    return upsert_section(page, build_section(groups), dry_run)


def link_base_page(base_name: str, cluster_info: dict, label_derived: set,
                   dry_run: bool) -> bool:
    page = base_page(base_name)
    if not page.exists():
        return False

    # 기기 페이지와 같은 규칙: 라벨은 자기 이름과 ID, 병합 페이지라도 ID마다 한 줄
    derived = []
    for cid in sorted(cluster_info.keys()):
        info = cluster_info[cid]
        match = (
            (base_name == "ModeBase" and info.get("uses_base") == "ModeBase") or
            (base_name == "AlarmBase" and info.get("uses_base") == "AlarmBase") or
            (base_name == "Label" and cid in label_derived)
        )
        if not match:
            continue
        cp = cluster_page(info["rep_id"], info["rep_name"])
        if cp.exists():
            derived.append((cluster_label(cid, cluster_info), rel(page, cp)))

    if not derived:
        return False

    return upsert_section(page, build_section({"파생 클러스터": derived}), dry_run)


def link_all(scope: dict, dry_run: bool) -> int:
    """WIKI_ROOT 아래 페이지에 섹션을 넣는다. 바뀐(dry-run 이면 바뀔) 페이지 수 반환."""
    cluster_info, device_info, cluster_devices = build_graph(scope)
    label_derived = detect_label_derived(cluster_info)

    prefix = "[dry-run] " if dry_run else ""
    updated = 0

    # 클러스터 페이지
    for cid in sorted(cluster_info):
        if link_cluster_page(cid, cluster_info, cluster_devices, label_derived, dry_run):
            info = cluster_info[cid]
            print(f"{prefix}[링크] {cluster_page(info['rep_id'], info['rep_name']).name}")
            updated += 1

    # 기기 타입 페이지
    for dname, dinfo in device_info.items():
        if link_device_page(dname, dinfo, cluster_info, dry_run):
            print(f"{prefix}[링크] {device_page(dname).name}")
            updated += 1

    # 베이스 클러스터 페이지
    for bname in ["ModeBase", "AlarmBase", "Label"]:
        if link_base_page(bname, cluster_info, label_derived, dry_run):
            print(f"{prefix}[링크] {base_page(bname).name}")
            updated += 1

    return updated


# ---------------------------------------------------------------------------
# 점검 (--check) — 페이지를 고치지 않고 읽기만 한다
# ---------------------------------------------------------------------------

# 링크 라벨과 기기 줄 설명 안의 "클러스터 이름 `0xNNNN`" 짝
LABEL_RE = re.compile(r"(?:\[|: |, )([^\[\]():,`]+?) `(0x[0-9A-Fa-f]{4})`")
LINK_RE = re.compile(r"\]\(([^)]+)\)")
DEVICE_LINE_RE = re.compile(r"^- \[([^\]]+)\]\(\.\./device-types/[^)]+\)(.*)$", re.MULTILINE)


def check_links(scope: dict) -> tuple[list[str], int]:
    """링커가 쓴 섹션을 scope.json 과 대조한다. 반환: (문제 목록, 섹션이 있는 페이지 수)

    - 라벨 '이름 `0xNNNN`' 의 이름이 scope.json 에서 그 ID의 cluster_name 과 같은가
    - 기기 페이지가 scope.json 의 직접/베이스 클러스터 ID를 빠짐없이 걸었는가
    - 병합 페이지의 기기 줄에 그 기기가 실제로 쓰는 ID가 붙었는가
    - 링크 대상 파일이 있는가
    섹션이 있는 페이지가 0개면 링커를 돌리지 않은 위키로 보고 문제로 센다. (#27 A 기준 점검)
    """
    cluster_info, device_info, _ = build_graph(scope)
    problems: list[str] = []
    sections: dict[Path, str] = {}

    for page in sorted(WIKI_ROOT.rglob("*.md")):
        sec = split_section(page.read_text(encoding="utf-8"))[1]
        if not sec:
            continue
        sections[page] = sec
        name = page.relative_to(WIKI_ROOT).as_posix()
        for label, cid in LABEL_RE.findall(sec):
            info = cluster_info.get(cid)
            if info is None:
                problems.append(f"{name}: scope.json 에 없는 ID '{label} `{cid}`'")
            elif label != info["name"]:
                problems.append(f"{name}: '{label} `{cid}`' 인데 scope.json 이름은 '{info['name']}'")
        for target in LINK_RE.findall(sec):
            if not (page.parent / target).exists():
                problems.append(f"{name}: 링크 대상 파일 없음 {target}")

    # 기기 페이지: scope.json 의 ID가 빠지거나 남는지
    for dname, di in device_info.items():
        page = device_page(dname)
        if not page.exists():
            continue
        expected = {cid for cid in di["direct"] + di["base"]
                    if cid in cluster_info and cluster_page(
                        cluster_info[cid]["rep_id"], cluster_info[cid]["rep_name"]).exists()}
        found = {cid for _, cid in LABEL_RE.findall(sections.get(page, ""))}
        name = page.relative_to(WIKI_ROOT).as_posix()
        if expected - found:
            problems.append(f"{name}: 링크 빠진 ID {sorted(expected - found)}")
        if found - expected:
            problems.append(f"{name}: scope.json 에 없는 링크 ID {sorted(found - expected)}")

    # 병합 클러스터 페이지: 기기 줄의 ID == 그 기기가 실제로 쓰는 ID
    for cid, info in cluster_info.items():
        ids_on_page = page_ids(cid, cluster_info)
        if info["rep_id"] != cid or len(ids_on_page) < 2:
            continue
        page = cluster_page(info["rep_id"], info["rep_name"])
        sec = sections.get(page)
        if not sec:
            continue
        name = page.relative_to(WIKI_ROOT).as_posix()
        for dname, rest in DEVICE_LINE_RE.findall(sec):
            di = device_info.get(dname)
            if di is None:
                problems.append(f"{name}: scope.json 에 없는 기기 '{dname}'")
                continue
            tagged = {i for _, i in LABEL_RE.findall(rest)}
            uses = set(di["direct"] + di["base"]) & set(ids_on_page)
            if tagged != uses:
                problems.append(f"{name}: {dname} 줄의 ID {sorted(tagged)} 인데 "
                                f"실제로 쓰는 ID는 {sorted(uses)}")

    if not sections:
        problems.append("관련 페이지 섹션이 있는 페이지가 0개 (링커를 돌리지 않은 위키)")
    return problems, len(sections)


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def _safe_console() -> None:
    """compile_wiki.py 와 같은 가드. --check 는 LLM 이 쓴 페이지의 글자를 그대로
    출력하므로, cp949 콘솔이 담지 못하는 문자가 있어도 멈추지 않게 한다."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv=None) -> int:
    _safe_console()
    parser = argparse.ArgumentParser(
        description="scope.json 관계로 위키 페이지에 '## 관련 페이지' 섹션을 넣는다 (API 호출 없음).")
    parser.add_argument("--wiki-root",
                        help="대상 위키 디렉터리. compile_wiki.py --wiki-root 와 같은 값을 준다. "
                             "없으면 환경변수 WIKI_ROOT, 그것도 없으면 systems/system_c_llm_wiki/wiki")
    parser.add_argument("--dry-run", action="store_true",
                        help="파일을 수정하지 않고 변경될 페이지 목록만 출력")
    parser.add_argument("--check", action="store_true",
                        help="고치지 않고 라벨이 scope.json 이름과 맞는지, 빠진 링크가 없는지만 "
                             "점검 (문제가 있으면 종료 코드 1)")
    args = parser.parse_args(argv)

    # 대상 위키를 정해 전역에 둔다. 경로 헬퍼가 모두 이 값을 읽으므로 무엇보다 먼저.
    # 예전에는 환경변수만 봐서, 빠뜨리면 기본 wiki/ 를 말없이 고쳤다 (#27 A 기준 점검)
    global WIKI_ROOT
    if args.wiki_root:
        WIKI_ROOT, source = Path(args.wiki_root), "--wiki-root"
    elif os.environ.get("WIKI_ROOT"):
        WIKI_ROOT, source = Path(os.environ["WIKI_ROOT"]), "환경변수 WIKI_ROOT"
    else:
        WIKI_ROOT, source = DEFAULT_WIKI_ROOT, "기본값"
    print(f"[대상] {WIKI_ROOT.as_posix()} ({source})")
    if not WIKI_ROOT.is_dir():
        print(f"[오류] 위키 디렉터리가 없습니다: {WIKI_ROOT.as_posix()}")
        return 2
    if not SCOPE_JSON.exists():
        print(f"[오류] {SCOPE_JSON.as_posix()} 가 없습니다. 리포 루트에서 실행하세요.")
        return 2
    if source == "기본값" and not (args.dry_run or args.check):
        print("[주의] --wiki-root 를 주지 않아 기본 위키를 고칩니다. 재구축한 위키라면 "
              "compile_wiki.py 에 준 --wiki-root 를 같이 주세요.")

    scope = json.loads(SCOPE_JSON.read_text(encoding="utf-8"))

    if args.check:
        problems, linked = check_links(scope)
        for p in problems:
            print(f"  [문제] {p}")
        print(f"\n[점검] 관련 페이지 섹션 {linked}개 페이지, 문제 {len(problems)}건")
        return 1 if problems else 0

    updated = link_all(scope, args.dry_run)
    action = "변경 예정" if args.dry_run else "업데이트 완료"
    print(f"\n[요약] {action} {updated}개 페이지")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
