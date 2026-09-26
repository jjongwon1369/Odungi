"""Build configured finalized tiers and validate adjacent tier inclusion."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from corpus_utils import CorpusError, PROJECT_ROOT, load_json, require
from generate_scope import DEFAULT_REGISTRY, load_registry


def tier_root(registry_path: Path, entry: dict) -> Path:
    root = (registry_path.parent / entry["output_root"]).resolve()
    require(root.is_relative_to(PROJECT_ROOT), f"Tier root escapes project: {root}")
    return root


def buildable_status(root: Path) -> dict:
    scope_path = root / "scope.json"
    coverage_path = root / "coverage_matrix.csv"
    if not scope_path.is_file() or not coverage_path.is_file():
        return {"buildable": False, "reason": "finalized scope.json and coverage_matrix.csv are required"}
    scope = load_json(scope_path)
    state = str(scope.get("state", ""))
    if not state.startswith("finalized"):
        return {"buildable": False, "reason": f"scope state is not finalized: {state!r}"}
    if scope.get("draft") is True or scope.get("extraction_authorized") is False:
        return {"buildable": False, "reason": "scope still denies extraction"}
    return {"buildable": True, "reason": "finalized inputs present"}


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    require(result.returncode == 0, "Command failed: " + " ".join(command))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    value.add_argument("--tier", action="append", help="Configured tier to build; defaults to registry order")
    value.add_argument("--status-only", action="store_true")
    value.add_argument("--skip-inclusion", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        registry_path, registry, entries = load_registry(args.registry)
        selected = args.tier or list(entries)
        unknown = [tier for tier in selected if tier not in entries]
        require(not unknown, f"Unknown configured tiers: {unknown}")
        statuses = []
        for tier in selected:
            root = tier_root(registry_path, entries[tier])
            status = buildable_status(root)
            statuses.append({"tier": tier, "root": root.relative_to(PROJECT_ROOT).as_posix(), **status})
        if args.status_only:
            print(json.dumps(statuses, indent=2, ensure_ascii=False))
            return 0
        blocked = [item for item in statuses if not item["buildable"]]
        require(not blocked, "Unbuildable tiers: " + json.dumps(blocked, ensure_ascii=False))
        environment_variable = registry["repository"].get("environment_variable", "CONNECTEDHOMEIP_PATH")
        require(bool(os.environ.get(environment_variable, "").strip()), f"{environment_variable} is not set")
        for item in statuses:
            run([sys.executable, str(Path(__file__).with_name("build.py")),
                 "--corpus-root", str(PROJECT_ROOT / item["root"])])
        if not args.skip_inclusion:
            for lower, upper in zip(statuses, statuses[1:]):
                run([sys.executable, str(Path(__file__).with_name("compare_tiers.py")),
                     "--lower-root", str(PROJECT_ROOT / lower["root"]),
                     "--upper-root", str(PROJECT_ROOT / upper["root"])])
        return 0
    except (CorpusError, OSError, ValueError, KeyError) as exc:
        print("Tier build failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
