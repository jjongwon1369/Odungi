"""Build and validate the Corpus from CONNECTEDHOMEIP_PATH."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from corpus_utils import (CorpusError, PINNED_COMMIT, PROJECT_ROOT, Repository,
                          load_json, require)


ENVIRONMENT_VARIABLE = "CONNECTEDHOMEIP_PATH"
LEGACY_CORPUS_ROOT = PROJECT_ROOT / "corpus"
EXPECTED = {
    "unique_file_count": 282,
    "normalized_document_count": 282,
    "relation_count": 764,
    "extracted_unique_clusters": 23,
}


def source_path_from_environment() -> Path:
    value = os.environ.get(ENVIRONMENT_VARIABLE, "").strip()
    require(bool(value), f"{ENVIRONMENT_VARIABLE} is not set")
    path = Path(value).expanduser()
    require(path.is_absolute(), f"{ENVIRONMENT_VARIABLE} must be an absolute path: {value}")
    path = path.resolve()
    require(path.is_dir(), f"{ENVIRONMENT_VARIABLE} does not exist or is not a directory: {path}")
    return path


def corpus_paths(root: Path) -> dict[str, Path]:
    root = root.resolve()
    legacy = root == LEGACY_CORPUS_ROOT.resolve()
    metadata = root / "metadata"
    return {
        "root": root,
        "scope": metadata / "scope.json" if legacy else root / "scope.json",
        "output": root / "raw",
        "snapshot": metadata / "snapshot.json",
        "statistics": metadata / "statistics.json",
        "validation_report": metadata / "validation_report.json",
    }


def verify_generated_results(paths: dict[str, Path], expect_c3_baseline: bool) -> dict[str, int]:
    statistics = load_json(paths["statistics"])
    report = load_json(paths["validation_report"])
    if expect_c3_baseline:
        for key, expected in EXPECTED.items():
            require(statistics.get(key) == expected,
                    f"Unexpected {key}: expected {expected}, found {statistics.get(key)!r}")
    summary = report.get("summary")
    require(isinstance(summary, dict), "Validation report has no summary")
    failures = summary.get("fail", 0)
    require(failures == 0, f"Validation reported {failures} failure(s)")
    require(report.get("status") in {"pass", "warning"},
            f"Unexpected validation status: {report.get('status')!r}")
    return {
        "raw_files": statistics["unique_file_count"],
        "normalized_documents": statistics["normalized_document_count"],
        "relations": statistics["relation_count"],
        "unique_clusters": statistics["extracted_unique_clusters"],
        "validation_failures": failures,
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--corpus-root", type=Path, default=LEGACY_CORPUS_ROOT,
                       help="Tier root containing scope.json and coverage_matrix.csv")
    value.add_argument("--expect-c3-baseline", action="store_true",
                       help="Enforce the preserved C3 regression counts")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        paths = corpus_paths(args.corpus_root)
        expect_c3 = args.expect_c3_baseline or paths["root"] == LEGACY_CORPUS_ROOT.resolve()
        print(f"[1/4] Reading {ENVIRONMENT_VARIABLE}", flush=True)
        source = source_path_from_environment()

        print(f"[2/4] Verifying connectedhomeip repository at {source}", flush=True)
        repository = Repository(source)
        require(repository.head == PINNED_COMMIT, "Connectedhomeip HEAD verification failed")

        print(f"[3/4] Loading scope from {paths['scope']}", flush=True)
        scope = load_json(paths["scope"])
        require(scope.get("repository", {}).get("commit_sha") == PINNED_COMMIT,
                "scope.json does not reference the pinned connectedhomeip commit")

        print("[4/4] Running the existing extraction, normalization, generation, and validation pipeline", flush=True)
        command = [
            sys.executable,
            str(Path(__file__).with_name("extract_corpus.py")),
            "--source-repo", str(source),
            "--scope", str(paths["scope"]),
            "--output", str(paths["output"]),
            "--snapshot", str(paths["snapshot"]),
        ]
        result = subprocess.run(command, cwd=PROJECT_ROOT)
        require(result.returncode == 0, f"Corpus pipeline exited with code {result.returncode}")

        summary = verify_generated_results(paths, expect_c3)
        print("Corpus build completed successfully:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (CorpusError, OSError, ValueError, KeyError) as exc:
        print("Corpus build failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
