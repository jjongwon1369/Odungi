"""Generate a deterministic Device Type/Cluster scope draft for human review."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

from corpus_utils import (CorpusError, PROJECT_ROOT, Repository,
                          json_bytes, load_json, require, writable_path, write_file)


CONFIG_ROOT = PROJECT_ROOT / "corpus/configs"
DEFAULT_REGISTRY = CONFIG_ROOT / "tiers.json"


def load_registry(path: Path = DEFAULT_REGISTRY) -> tuple[Path, dict, dict[str, dict]]:
    path = Path(path).resolve()
    registry = load_json(path)
    require(registry.get("schema_version") == "1.0", "Unsupported tier registry schema")
    entries = registry.get("tiers")
    require(isinstance(entries, list) and entries, "Tier registry has no tiers")
    by_name = {}
    for entry in entries:
        name = entry.get("name")
        require(isinstance(name, str) and name, "Tier registry entry has no name")
        require(name not in by_name, f"Duplicate tier registry entry: {name}")
        require(entry.get("declaration") and entry.get("output_root"), f"Incomplete tier registry entry: {name}")
        by_name[name] = entry
    return path, registry, by_name


def declaration_path(tier: str, registry_path: Path = DEFAULT_REGISTRY) -> Path:
    require(tier and tier.replace("_", "").isalnum(), f"Invalid tier name: {tier!r}")
    registry_path, _, entries = load_registry(registry_path)
    require(tier in entries, f"Unknown configured tier: {tier}")
    return registry_path.parent / entries[tier]["declaration"]


def resolve_product_families(tier: str, seen: tuple[str, ...] = (),
                             registry_path: Path = DEFAULT_REGISTRY) -> list[dict]:
    require(tier not in seen, "Tier inheritance cycle: " + " -> ".join((*seen, tier)))
    declaration = load_json(declaration_path(tier, registry_path))
    require(declaration.get("schema_version") == "1.0", f"Unsupported declaration schema: {tier}")
    require(declaration.get("tier") == tier, f"Tier name mismatch in {tier}.json")
    parent = declaration.get("inherits")
    inherited = resolve_product_families(parent, (*seen, tier), registry_path) if parent else []
    added = declaration.get("add_product_families")
    require(isinstance(added, list) and added, f"Invalid add_product_families in {tier}.json")
    for family in added:
        require(isinstance(family.get("name"), str) and family["name"], f"Unnamed product family in {tier}.json")
        ids = family.get("device_types")
        require(isinstance(ids, list) and ids and all(isinstance(value, int) for value in ids),
                f"Invalid product family Device Types in {tier}.json")
    names = [family["name"] for family in inherited + added]
    require(len(names) == len(set(names)), f"Duplicate product family in {tier}.json")
    device_ids = [value for family in inherited + added for value in family["device_types"]]
    require(len(device_ids) == len(set(device_ids)), f"Duplicate Device Type assignment in {tier}.json")
    return inherited + added


def resolve_device_types(tier: str, seen: tuple[str, ...] = (),
                         registry_path: Path = DEFAULT_REGISTRY) -> list[int]:
    families = resolve_product_families(tier, seen, registry_path)
    return [value for family in families for value in family["device_types"]]


def device_type_index(repository: Repository, data_model_directory: str) -> dict[int, str]:
    prefix = data_model_directory.rstrip("/") + "/device_types/"
    result = {}
    for path in sorted(p for p in repository.entries if p.startswith(prefix) and p.endswith(".xml")):
        root = ET.fromstring(repository.read(path).decode("utf-8-sig"))
        raw_id = root.attrib.get("id")
        if not raw_id:
            continue
        device_id = int(raw_id, 0)
        require(device_id not in result, f"Duplicate Device Type ID 0x{device_id:04X}")
        result[device_id] = path
    return result


def product_draft(repository: Repository, path: str, base_clusters: list[int], override: dict) -> dict:
    root = ET.fromstring(repository.read(path).decode("utf-8-sig"))
    excluded = set(override.get("exclude_direct_cluster_ids", []))
    direct = sorted({int(node.attrib["id"], 0) for node in root.findall("./clusters/cluster")} - excluded)
    result = {
        "base_cluster_ids": [f"0x{value:04X}" for value in sorted(base_clusters)],
        "definition_path": path,
        "direct_cluster_ids": [f"0x{value:04X}" for value in direct],
        "id": f"0x{int(root.attrib['id'], 0):04X}",
        "name": root.attrib["name"],
        "revision": root.attrib.get("revision"),
    }
    if override.get("product_role"):
        result["product_role"] = override["product_role"]
    if override.get("scope_profile"):
        result["scope_profile"] = override["scope_profile"]
    if excluded:
        result["excluded_direct_cluster_ids"] = [f"0x{value:04X}" for value in sorted(excluded)]
    return result


def build_draft(repository: Repository, tier: str, registry_path: Path = DEFAULT_REGISTRY) -> dict:
    registry_path, registry, entries = load_registry(registry_path)
    require(tier in entries, f"Unknown configured tier: {tier}")
    declaration = load_json(declaration_path(tier, registry_path))
    overrides = load_json(registry_path.parent / registry["default_overrides"])
    require(overrides.get("schema_version") == "1.0", "Unsupported overrides schema")
    families = resolve_product_families(tier, registry_path=registry_path)
    requested = [value for family in families for value in family["device_types"]]
    related = overrides.get("related_device_types", {})
    for device_id in tuple(requested):
        for related_id in related.get(str(device_id), []):
            require(related_id in requested,
                    f"Tier {tier} must explicitly include related Device Type {related_id} for {device_id}")
    data_model_directory = registry["data_model_directory"].rstrip("/")
    index = device_type_index(repository, data_model_directory)
    missing = [value for value in requested if value not in index]
    require(not missing, f"Device Type IDs absent from {data_model_directory}: {missing}")
    base = overrides.get("common_base_cluster_ids", [])
    device_overrides = overrides.get("device_type_overrides", {})
    products = [product_draft(repository, index[value], base, device_overrides.get(str(value), {}))
                for value in requested]
    return {
        "draft": True,
        "extraction_authorized": False,
        "corpus_version": declaration["corpus_version"],
        "repository": {"commit_sha": repository.head, "name": registry["repository"]["name"]},
        "schema_version": "1.0-draft",
        "snapshot_namespace": declaration["snapshot_namespace"],
        "tier": tier,
        "products": products,
        "product_families": families,
        "counts": {
            "device_types": len(products),
            "product_families": len(families),
            "direct_device_cluster_relations": sum(len(item["direct_cluster_ids"]) for item in products),
            "unique_direct_clusters": len({cluster for item in products for cluster in item["direct_cluster_ids"]}),
        },
        "review_required": [
            "cluster source mapping",
            "implementation/documentation/example evidence",
            "include/exclude and missing/not_applicable decisions",
            "feature conditions and requirements",
            "product-specific exceptions",
        ],
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    target = value.add_mutually_exclusive_group(required=True)
    target.add_argument("--tier")
    target.add_argument("--all", action="store_true", help="Generate every tier in the registry")
    value.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    value.add_argument("--source-repo")
    value.add_argument("--output", type=Path)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        registry_path, registry, entries = load_registry(args.registry)
        environment_variable = registry["repository"].get("environment_variable", "CONNECTEDHOMEIP_PATH")
        source = args.source_repo or os.environ.get(environment_variable, "").strip()
        require(bool(source), "--source-repo or CONNECTEDHOMEIP_PATH is required")
        expected_commit = registry["repository"]["commit_sha"]
        repository = Repository(source, expected_commit=expected_commit)
        tiers = list(entries) if args.all else [args.tier]
        require(not (args.all and args.output), "--output is only valid with one --tier")
        results = []
        for tier in tiers:
            require(tier in entries, f"Unknown configured tier: {tier}")
            draft = build_draft(repository, tier, registry_path)
            configured_root = (registry_path.parent / entries[tier]["output_root"]).resolve()
            output = args.output or configured_root / "scope_draft.json"
            output = writable_path(output, repository.root)
            write_file(output, json_bytes(draft), repository.root)
            results.append({"tier": tier, "output": output.relative_to(PROJECT_ROOT).as_posix(), **draft["counts"]})
        print(json.dumps(results, indent=2))
        return 0
    except (CorpusError, OSError, ValueError, KeyError, ET.ParseError) as exc:
        print("Scope draft generation failed: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
