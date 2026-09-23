#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Wiki 상호링크 생성기 (System C)
====================================
컴파일된 위키 페이지들 사이에 "## 관련 페이지" 섹션을 추가한다.
scope.json 에서 관계를 추론하며, API 호출 없이 순수 로컬 파일 처리다.

사용법 (리포 루트에서):
    python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py --dry-run
    python3 systems/system_c_llm_wiki/linker/crosslink_wiki.py
"""

import argparse
import json
import re
from pathlib import Path

SCOPE_JSON = Path("corpus/metadata/scope.json")
WIKI_ROOT = Path("systems/system_c_llm_wiki/wiki")

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
        impl_dir = str(Path(c["implementation_path"]).parent)

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
    """wiki 페이지 본문에서 baseCluster: Label 또는 hierarchy: derived + Label 패턴 탐지."""
    derived = set()
    seen_pages: set[Path] = set()
    for cid, info in cluster_info.items():
        page = cluster_page(info["rep_id"], info["rep_name"])
        if page in seen_pages or not page.exists():
            continue
        seen_pages.add(page)
        text = page.read_text(encoding="utf-8")
        if re.search(r"baseCluster[`'\s:]*Label", text, re.IGNORECASE):
            derived.add(cid)
    return derived


# ---------------------------------------------------------------------------
# 섹션 조립 / 파일 업데이트
# ---------------------------------------------------------------------------

def build_section(groups: dict) -> str:
    """groups: {그룹명: [(label, rel_path), ...]}  →  마크다운 섹션 문자열"""
    lines = [f"\n{SECTION_HEADER}\n"]
    for group, items in groups.items():
        if not items:
            continue
        lines.append(f"**{group}**\n")
        for label, path in items:
            lines.append(f"- [{label}]({path})")
        lines.append("")
    return "\n".join(lines)


def upsert_section(page: Path, section_md: str, dry_run: bool) -> bool:
    """기존 관련 페이지 섹션을 교체하거나 없으면 추가. 변경 여부 반환."""
    content = page.read_text(encoding="utf-8")
    stripped = re.sub(
        rf"\n{re.escape(SECTION_HEADER)}.*",
        "",
        content,
        flags=re.DOTALL,
    )
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

    groups: dict = {}

    # 1) 베이스 클러스터
    base_name = info.get("uses_base")
    if not base_name and cid in label_derived:
        base_name = "Label"
    # merged entity: 다른 ID도 같은 base를 쓰는지 확인
    if not base_name:
        for other_id, other in cluster_info.items():
            if other["rep_id"] == cid and other.get("uses_base"):
                base_name = other["uses_base"]
                break
    if base_name:
        bp = base_page(base_name)
        if bp.exists():
            groups["베이스 클러스터"] = [(base_name, rel(page, bp))]

    # 2) 사용 기기 — merged entity의 모든 ID를 합산
    devices: list[str] = []
    seen_d: set = set()
    for any_id, any_info in cluster_info.items():
        if any_info["rep_id"] == cid:
            for dname in cluster_devices.get(any_id, []):
                if dname not in seen_d:
                    seen_d.add(dname)
                    devices.append(dname)
    if devices:
        groups["사용 기기"] = []
        for dname in sorted(devices):
            dp = device_page(dname)
            if dp.exists():
                groups["사용 기기"].append((dname, rel(page, dp)))

    if not any(v for v in groups.values()):
        return False

    return upsert_section(page, build_section(groups), dry_run)


def link_device_page(dname: str, dinfo: dict, cluster_info: dict,
                     dry_run: bool) -> bool:
    page = device_page(dname)
    if not page.exists():
        return False

    def cluster_items(ids):
        seen_pages: set = set()
        result = []
        for cid in ids:
            info = cluster_info.get(cid)
            if not info:
                continue
            cp = cluster_page(info["rep_id"], info["rep_name"])
            if cp in seen_pages:
                continue  # 병합 클러스터 중복 방지
            seen_pages.add(cp)
            if cp.exists():
                result.append((f"{info['rep_name']} `{cid}`", rel(page, cp)))
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

    seen_pages: set = set()
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
        if cp in seen_pages:
            continue
        seen_pages.add(cp)
        if cp.exists():
            derived.append((f"{info['rep_name']} `{cid}`", rel(page, cp)))

    if not derived:
        return False

    return upsert_section(page, build_section({"파생 클러스터": derived}), dry_run)


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="파일을 수정하지 않고 변경될 페이지 목록만 출력")
    args = parser.parse_args()

    scope = json.loads(SCOPE_JSON.read_text(encoding="utf-8"))
    cluster_info, device_info, cluster_devices = build_graph(scope)
    label_derived = detect_label_derived(cluster_info)

    prefix = "[dry-run] " if args.dry_run else ""
    updated = 0

    # 클러스터 페이지
    for cid in sorted(cluster_info):
        if link_cluster_page(cid, cluster_info, cluster_devices, label_derived, args.dry_run):
            info = cluster_info[cid]
            print(f"{prefix}[링크] {cluster_page(info['rep_id'], info['rep_name']).name}")
            updated += 1

    # 기기 타입 페이지
    for dname, dinfo in device_info.items():
        if link_device_page(dname, dinfo, cluster_info, args.dry_run):
            print(f"{prefix}[링크] {device_page(dname).name}")
            updated += 1

    # 베이스 클러스터 페이지
    for bname in ["ModeBase", "AlarmBase", "Label"]:
        if link_base_page(bname, cluster_info, label_derived, args.dry_run):
            print(f"{prefix}[링크] {base_page(bname).name}")
            updated += 1

    action = "변경 예정" if args.dry_run else "업데이트 완료"
    print(f"\n[요약] {action} {updated}개 페이지")


if __name__ == "__main__":
    main()
