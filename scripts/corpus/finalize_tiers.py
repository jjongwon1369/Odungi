"""Materialize approved tier scope/coverage inputs from the reviewed configuration."""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET

from corpus_utils import (CorpusError, PROJECT_ROOT, Repository, canonical,
                          json_bytes, load_json, require, writable_path, write_file)
from generate_scope import DEFAULT_REGISTRY, build_draft, load_registry


BASELINE_SCOPE = PROJECT_ROOT / "corpus/metadata/scope.json"
BASELINE_COVERAGE = PROJECT_ROOT / "corpus/metadata/coverage_matrix.csv"
SENTINEL = "unverified"


def coverage_input(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def coverage_bytes(fieldnames: list[str], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fieldnames} for row in rows)
    return stream.getvalue().encode("utf-8")


def xml_root(repository: Repository, path: str) -> ET.Element:
    return ET.fromstring(repository.read(path).decode("utf-8-sig"))


def cluster_indexes(repository: Repository, data_model_directory: str) -> tuple[dict[int, dict], dict[int, dict]]:
    specification = {}
    prefix = data_model_directory.rstrip("/") + "/clusters/"
    for path in sorted(p for p in repository.entries if p.startswith(prefix) and p.endswith(".xml")):
        root = xml_root(repository, path)
        for node in root.findall("./clusterIds/clusterId"):
            raw_id = node.attrib.get("id")
            if raw_id:
                cluster_id = int(raw_id, 0)
                require(cluster_id not in specification, f"Duplicate specification cluster ID 0x{cluster_id:04X}")
                specification[cluster_id] = {
                    "path": path,
                    "name": node.attrib.get("name", root.attrib.get("name", "")),
                    "revision": root.attrib.get("revision", SENTINEL),
                }
    sdk = {}
    sdk_prefix = "src/app/zap-templates/zcl/data-model/chip/"
    for path in sorted(p for p in repository.entries if p.startswith(sdk_prefix) and p.endswith(".xml")):
        text = repository.read(path).decode("utf-8-sig")
        codes = {int(value, 0) for value in re.findall(r"<code>(0x[0-9A-Fa-f]+)</code>", text)}
        revision = next(iter(re.findall(r'<globalAttribute[^>]+code="0xFFFD"[^>]+value="([^"]+)"', text)), SENTINEL)
        for cluster_id in codes:
            sdk.setdefault(cluster_id, {"path": path, "revision": revision})
    return specification, sdk


def conformance(node: ET.Element) -> tuple[str, str]:
    items = [child for child in node if child.tag.endswith("Conform")]
    require(items, f"Cluster {node.attrib.get('id')} has no conformance declaration")
    names = [child.tag for child in items]
    raw = "; ".join(ET.tostring(child, encoding="unicode").strip() for child in items)
    if any(name == "mandatoryConform" for name in names):
        requirement = "required"
    elif any(name == "provisionalConform" for name in names):
        requirement = "provisional"
    elif any(name == "optionalConform" for name in names):
        requirement = "optional"
    elif any(name == "disallowConform" for name in names):
        requirement = "disallowed"
    else:
        requirement = "conditional"
    return requirement, raw


def append_unique(values: list, additions: list) -> None:
    known = set(values)
    for value in additions:
        if value not in known:
            values.append(value)
            known.add(value)


def add_source_path(scope: dict, role: str, kind: str, path: str) -> None:
    if path in {"", "unverified", "not_applicable"}:
        return
    group = next((item for item in scope["source_sets"]
                  if item["source_role"] == role and item["definition_kind"] == kind
                  and "paths" in item), None)
    if group is None:
        group = {"source_role": role, "definition_kind": kind, "paths": []}
        scope["source_sets"].append(group)
    append_unique(group["paths"], [path])


def relative_zap(path: str) -> str:
    return path[:-7] + ".zap" if path.endswith(".matter") else SENTINEL


def make_cluster(cluster_id: int, spec: dict, sdk: dict, source: dict, idl_path: str) -> dict:
    return {
        "cluster_id": f"0x{cluster_id:04X}",
        "cluster_name": spec["name"],
        "specification_path": spec["path"],
        "specification_revision": spec["revision"],
        "sdk_definition_path": sdk["path"],
        "sdk_revision": sdk["revision"],
        "implementation_path": source["implementation_path"],
        "implementation_scope": source["implementation_scope"],
        "documentation_path": source["documentation_path"],
        "documentation_status": "present" if source["documentation_path"] != SENTINEL else "missing",
        "idl_path": idl_path,
        "idl_scope": "device_example" if idl_path != SENTINEL else SENTINEL,
    }


def blank_row(fieldnames: list[str]) -> dict:
    return {field: SENTINEL for field in fieldnames}


def cluster_row(fieldnames: list[str], product: dict, node: ET.Element, cluster: dict,
                origin: str, coverage_id: str, commit: str, data_model_version: str,
                related: str = SENTINEL) -> dict:
    requirement, condition = conformance(node)
    documentation = cluster["documentation_path"]
    idl = cluster["idl_path"]
    row = blank_row(fieldnames)
    row.update({
        "coverage_id": coverage_id,
        "discovery_row_id": "D-" + coverage_id,
        "discovery_status": "present",
        "scope_decision": "include",
        "device_type_name": product["name"],
        "device_type_id": product["id"],
        "related_device_type": related,
        "relation_type": "requires_cluster",
        "relationship_origin": origin,
        "endpoint_requirement": "server on endpoint implementing this Device Type; conditional support retained",
        "cluster_name": cluster["cluster_name"],
        "cluster_id": cluster["cluster_id"],
        "server_client_role": node.attrib.get("side", "server"),
        "requirement": requirement,
        "feature_condition": condition,
        "specification_path": cluster["specification_path"],
        "specification_revision": cluster["specification_revision"],
        "device_type_definition_path": product["definition_path"],
        "device_type_revision": product["revision"],
        "sdk_definition_path": cluster["sdk_definition_path"],
        "sdk_revision": cluster["sdk_revision"],
        "documentation_path": documentation,
        "documentation_kind": "cluster_implementation_guide" if documentation != SENTINEL else SENTINEL,
        "implementation_path": cluster["implementation_path"],
        "implementation_scope": cluster["implementation_scope"],
        "implementation_revision": commit,
        "idl_path": idl,
        "idl_scope": cluster["idl_scope"],
        "evidence_location": canonical([{"path": product["definition_path"],
                                          "selector": f'/deviceType/clusters/cluster[@id="{cluster["cluster_id"]}"]'}]),
        "status": "present" if documentation != SENTINEL and idl != SENTINEL else "missing",
        "relation_status": "present",
        "specification_status": "present",
        "sdk_status": "present",
        "implementation_status": "present",
        "documentation_status": "present" if documentation != SENTINEL else "missing",
        "idl_status": "present" if idl != SENTINEL else "missing",
        "revision_comparison": "source_specific_revision_preserved",
        "documentation_search_scope": "[]",
        "resolution": "Approved deterministic tier expansion mapping",
        "commit_sha": commit,
        "data_model_version": data_model_version.split("/")[-1],
        "notes": "Generated from approved tier declaration and pinned source evidence; runtime conformance not asserted.",
    })
    return row


def auxiliary_row(fieldnames: list[str], product: dict, relation_type: str, coverage_id: str,
                  commit: str, data_model_version: str) -> dict:
    row = blank_row(fieldnames)
    row.update({
        "coverage_id": coverage_id,
        "discovery_row_id": "D-" + coverage_id,
        "discovery_status": "present",
        "scope_decision": "include",
        "device_type_name": product["name"],
        "device_type_id": product["id"],
        "relation_type": relation_type,
        "relationship_origin": "device_type",
        "endpoint_requirement": "endpoint-scoped Device Type" if relation_type == "requires_endpoint" else SENTINEL,
        "device_type_definition_path": product["definition_path"],
        "device_type_revision": product["revision"],
        "evidence_location": canonical([{"path": product["definition_path"], "selector": "/deviceType/classification"}]),
        "status": "present",
        "relation_status": "present",
        "commit_sha": commit,
        "data_model_version": data_model_version.split("/")[-1],
        "notes": "Generated from approved tier declaration and pinned source evidence.",
    })
    return row


def materialize(repository: Repository, tier: str, registry_path: Path, output_root: Path) -> dict:
    registry_path, registry, entries = load_registry(registry_path)
    declaration = load_json(registry_path.parent / entries[tier]["declaration"])
    draft = build_draft(repository, tier, registry_path)
    baseline_scope = load_json(BASELINE_SCOPE)
    fieldnames, baseline_rows = coverage_input(BASELINE_COVERAGE)
    if tier == "c3":
        scope = copy.deepcopy(baseline_scope)
        rows = copy.deepcopy(baseline_rows)
    else:
        scope = copy.deepcopy(baseline_scope)
        rows = copy.deepcopy(baseline_rows)

    scope["scope_version"] = f"scope-{tier}-v1.0"
    scope["state"] = "finalized_scope_not_frozen_corpus"
    scope["tier"] = tier
    scope["corpus_version"] = declaration["corpus_version"]
    scope["snapshot_namespace"] = declaration["snapshot_namespace"]
    scope["execution"]["extraction_authorized"] = True
    scope["finalized_on"] = declaration["finalized_on"]

    baseline_products = {item["id"]: item for item in baseline_scope["products"]}
    products = []
    for item in draft["products"]:
        if item["id"] in baseline_products:
            products.append(copy.deepcopy(baseline_products[item["id"]]))
        else:
            products.append({
                "name": item["name"],
                "id": item["id"],
                "product_role": item.get("product_role", "primary_product"),
                "definition_path": item["definition_path"],
                "revision": item["revision"],
                "direct_cluster_ids": item["direct_cluster_ids"],
                "base_cluster_ids": item["base_cluster_ids"],
            })
    scope["products"] = products

    data_model_directory = registry["data_model_directory"]
    spec_index, sdk_index = cluster_indexes(repository, data_model_directory)
    source_overrides = load_json(registry_path.parent / registry["source_overrides"])
    cluster_sources = source_overrides["new_cluster_sources"]
    device_examples = source_overrides["device_examples"]
    clusters = {item["cluster_id"]: copy.deepcopy(item) for item in baseline_scope["clusters"]}
    product_by_id = {int(item["id"], 0): item for item in products}
    cluster_to_examples: dict[int, list[str]] = {}
    for product_id, product in product_by_id.items():
        idl = device_examples.get(str(product_id), SENTINEL)
        for raw_id in product["direct_cluster_ids"] + product["base_cluster_ids"]:
            if idl != SENTINEL:
                cluster_to_examples.setdefault(int(raw_id, 0), []).append(idl)
    for cluster_id in sorted({int(raw, 0) for product in products
                              for raw in product["direct_cluster_ids"] + product["base_cluster_ids"]}):
        key = f"0x{cluster_id:04X}"
        if key in clusters:
            continue
        require(cluster_id in spec_index and cluster_id in sdk_index, f"Missing source definition for {key}")
        require(key in cluster_sources, f"Missing approved source override for {key}")
        idl = sorted(cluster_to_examples.get(cluster_id, [SENTINEL]))[0]
        clusters[key] = make_cluster(cluster_id, spec_index[cluster_id], sdk_index[cluster_id],
                                     cluster_sources[key], idl)
    scope["clusters"] = [clusters[key] for key in sorted(clusters, key=lambda value: int(value, 0))
                         if any(key in product["direct_cluster_ids"] + product["base_cluster_ids"] for product in products)]

    existing_product_ids = {item["id"] for item in baseline_scope["products"]}
    base_path = f"{data_model_directory}/device_types/BaseDeviceType.xml"
    base_root = xml_root(repository, base_path)
    base_nodes = {int(node.attrib["id"], 0): node for node in base_root.findall("./clusters/cluster")}
    for product in products:
        if product["id"] in existing_product_ids:
            continue
        product_id = int(product["id"], 0)
        root = xml_root(repository, product["definition_path"])
        direct_nodes = {int(node.attrib["id"], 0): node for node in root.findall("./clusters/cluster")}
        family = next(family for family in draft["product_families"] if product_id in family["device_types"])
        related_ids = [value for value in family["device_types"] if value != product_id]
        related = ";".join(f"{product_by_id[value]['name']}:0x{value:04X}" for value in related_ids) or SENTINEL
        for origin, raw_ids, nodes in [("direct", product["direct_cluster_ids"], direct_nodes),
                                       ("base", product["base_cluster_ids"], base_nodes)]:
            for raw_id in raw_ids:
                cluster_id = int(raw_id, 0)
                require(cluster_id in nodes, f"{product['name']} {origin} cluster absent from source: {raw_id}")
                coverage_id = f"T-{product_id:04X}-{cluster_id:04X}-{origin}"
                rows.append(cluster_row(fieldnames, product, nodes[cluster_id], clusters[f"0x{cluster_id:04X}"],
                                        origin, coverage_id, repository.head, data_model_directory, related))
        rows.append(auxiliary_row(fieldnames, product, "inherits_requirements",
                                  f"T-{product_id:04X}-inherits", repository.head, data_model_directory))
        rows.append(auxiliary_row(fieldnames, product, "requires_endpoint",
                                  f"T-{product_id:04X}-endpoint", repository.head, data_model_directory))

    for product in products:
        add_source_path(scope, "specification", "device_type", product["definition_path"])
    for cluster in scope["clusters"]:
        add_source_path(scope, "specification", "cluster", cluster["specification_path"])
        add_source_path(scope, "sdk_codegen", "cluster", cluster["sdk_definition_path"])
        add_source_path(scope, "documentation", "none", cluster["documentation_path"])
        add_source_path(scope, "example", "none", cluster["idl_path"])
        root = str(PurePosixPath(cluster["implementation_path"]).parent)
        if cluster["implementation_path"] not in {SENTINEL, "not_applicable"}:
            append_unique(scope["implementation_rules"]["component_roots"], [root])
        if cluster["documentation_path"] not in {SENTINEL, "not_applicable"}:
            append_unique(scope["support_documentation"], [cluster["documentation_path"]])
        if cluster["idl_path"] not in {SENTINEL, "not_applicable"}:
            append_unique(scope["example_rules"]["artifacts"], [cluster["idl_path"], relative_zap(cluster["idl_path"])])
            add_source_path(scope, "example", "none", relative_zap(cluster["idl_path"]))

    cluster_rows = [row for row in rows if row["scope_decision"] == "include" and row["relation_type"] == "requires_cluster"]
    included = [row for row in rows if row["scope_decision"] == "include"]
    excluded = [row for row in rows if row["scope_decision"] != "include"]
    scope["accepted_scope_counts"] = {
        "primary_products": len(draft["product_families"]),
        "official_device_type_ids": len(products),
        "unique_cluster_ids": len(scope["clusters"]),
        "included_cluster_relations": len(cluster_rows),
        "additional_provenance_relations": len(included) - len(cluster_rows),
        "excluded_audit_rows": len(excluded),
    }
    scope["coverage_status_counts"] = {
        key: sum(1 for row in rows if row["status"] == key) for key in ("present", "missing", "not_applicable", "unverified")
    }
    scope["validation_summary"] = {
        "reference_head_matches": True,
        "reference_worktree_clean": True,
        "coverage_rows": len(rows),
        "selected_cluster_relations": len(cluster_rows),
        "unique_cluster_ids": len(scope["clusters"]),
        "semantic_conformance_validated": False,
    }

    output_root = writable_path(output_root, repository.root)
    write_file(output_root / "scope.json", json_bytes(scope), repository.root)
    write_file(output_root / "coverage_matrix.csv", coverage_bytes(fieldnames, rows), repository.root)
    return {"tier": tier, "products": len(products), "clusters": len(scope["clusters"]),
            "coverage_rows": len(rows), "cluster_relations": len(cluster_rows)}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    value.add_argument("--source-repo", required=True)
    value.add_argument("--tier", action="append")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        registry_path, registry, entries = load_registry(args.registry)
        repository = Repository(args.source_repo, expected_commit=registry["repository"]["commit_sha"])
        selected = args.tier or list(entries)
        results = []
        for tier in selected:
            require(tier in entries, f"Unknown configured tier: {tier}")
            output_root = (registry_path.parent / entries[tier]["output_root"]).resolve()
            results.append(materialize(repository, tier, registry_path, output_root))
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0
    except (CorpusError, OSError, ValueError, KeyError, ET.ParseError) as exc:
        print("Tier finalization failed: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
