"""Compare two built Corpus tiers using stable inclusion contracts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from corpus_utils import (CorpusError, PROJECT_ROOT, canonical, json_bytes,
                          relation_semantic_key, require, writable_path, write_file)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_manifest(root: Path) -> dict[str, dict]:
    with (root / "metadata/corpus_manifest.csv").open(encoding="utf-8", newline="") as stream:
        return {row["source_path"]: row for row in csv.DictReader(stream)}


def spans_preserved(lower_spans: list[dict], upper_spans: list[dict]) -> bool:
    """Return whether every lower raw-source interval is covered by the upper tier.

    Scope-sensitive XML/JSON documents merge adjacent selected intervals as a
    tier expands.  Exact span-array or normalized-text equality would therefore
    reject a valid superset even though the pinned raw bytes are unchanged.
    """
    for lower in lower_spans:
        if not any(
            upper["source_path"] == lower["source_path"]
            and upper["char_start"] <= lower["char_start"]
            and upper["char_end"] >= lower["char_end"]
            for upper in upper_spans
        ):
            return False
    return True


def compare_tiers(lower_root: Path, upper_root: Path) -> dict:
    lower_manifest = read_manifest(lower_root)
    upper_manifest = read_manifest(upper_root)
    lower_docs = {row["document_id"]: row for row in read_jsonl(lower_root / "processed/documents.jsonl")}
    upper_docs = {row["document_id"]: row for row in read_jsonl(upper_root / "processed/documents.jsonl")}
    lower_relations = {relation_semantic_key(row) for row in read_jsonl(lower_root / "metadata/relations.jsonl")}
    upper_relations = {relation_semantic_key(row) for row in read_jsonl(upper_root / "metadata/relations.jsonl")}

    lower_sources = set(lower_manifest)
    upper_sources = set(upper_manifest)
    missing_sources = sorted(lower_sources - upper_sources)
    new_sources = sorted(upper_sources - lower_sources)
    content_mismatches = sorted(
        path for path in lower_sources & upper_sources
        if lower_manifest[path]["content_hash"] != upper_manifest[path]["content_hash"]
    )

    missing_documents = sorted(set(lower_docs) - set(upper_docs))
    normalized_mismatches = []
    expanded_documents = []
    association_removals = []
    for document_id in sorted(set(lower_docs) & set(upper_docs)):
        lower = lower_docs[document_id]
        upper = upper_docs[document_id]
        normalized_equal = all([
            lower["text"] == upper["text"],
            lower["metadata"]["normalized_hash"] == upper["metadata"]["normalized_hash"],
            canonical(lower["source_spans"]) == canonical(upper["source_spans"]),
        ])
        if not normalized_equal and not spans_preserved(lower["source_spans"], upper["source_spans"]):
            normalized_mismatches.append(document_id)
        elif not normalized_equal:
            expanded_documents.append(document_id)
        for field in ("device_types", "clusters"):
            removed = sorted(set(lower["metadata"].get(field, [])) - set(upper["metadata"].get(field, [])))
            if removed:
                association_removals.append({"document_id": document_id, "field": field, "removed": removed})

    missing_relations = sorted(lower_relations - upper_relations)
    checks = {
        "source_inclusion": {"status": "pass" if not missing_sources else "fail", "missing": missing_sources},
        "strict_source_expansion": {"status": "pass" if new_sources else "fail", "new_source_count": len(new_sources)},
        "raw_content_preservation": {"status": "pass" if not content_mismatches else "fail",
                                     "mismatches": content_mismatches},
        "document_inclusion": {"status": "pass" if not missing_documents else "fail", "missing": missing_documents},
        "normalized_content_preservation": {
            "status": "pass" if not normalized_mismatches else "fail",
            "mismatches": normalized_mismatches,
            "scope_expanded_documents": expanded_documents,
        },
        "association_inclusion": {
            "status": "pass" if not association_removals else "fail",
            "removals": association_removals,
        },
        "semantic_relation_inclusion": {
            "status": "pass" if not missing_relations else "fail",
            "missing_count": len(missing_relations),
            "missing_keys": missing_relations,
        },
    }
    return {
        "schema_version": "1.0",
        "lower_root": lower_root.relative_to(PROJECT_ROOT).as_posix(),
        "upper_root": upper_root.relative_to(PROJECT_ROOT).as_posix(),
        "status": "fail" if any(item["status"] == "fail" for item in checks.values()) else "pass",
        "checks": checks,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--lower-root", type=Path, required=True)
    value.add_argument("--upper-root", type=Path, required=True)
    value.add_argument("--output", type=Path)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        lower = writable_path(args.lower_root)
        upper = writable_path(args.upper_root)
        require(lower != upper, "Tier roots must be different")
        report = compare_tiers(lower, upper)
        output = args.output or upper / "metadata/tier_inclusion_report.json"
        write_file(output, json_bytes(report))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if report["status"] == "fail" else 0
    except (CorpusError, OSError, ValueError, KeyError) as exc:
        print("Tier comparison failed: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
