"""Build and validate the Corpus from CONNECTEDHOMEIP_PATH."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from corpus_utils import (CorpusError, PINNED_COMMIT, PROJECT_ROOT, Repository,
                          load_json, require)


ENVIRONMENT_VARIABLE = "CONNECTEDHOMEIP_PATH"
SCOPE = PROJECT_ROOT / "corpus/metadata/scope.json"
OUTPUT = PROJECT_ROOT / "corpus/raw"
SNAPSHOT = PROJECT_ROOT / "corpus/metadata/snapshot.json"
STATISTICS = PROJECT_ROOT / "corpus/metadata/statistics.json"
VALIDATION_REPORT = PROJECT_ROOT / "corpus/metadata/validation_report.json"
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


def verify_generated_results() -> dict[str, int]:
    statistics = load_json(STATISTICS)
    report = load_json(VALIDATION_REPORT)
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


def main() -> int:
    try:
        print(f"[1/4] Reading {ENVIRONMENT_VARIABLE}", flush=True)
        source = source_path_from_environment()

        print(f"[2/4] Verifying connectedhomeip repository at {source}", flush=True)
        repository = Repository(source)
        require(repository.head == PINNED_COMMIT, "Connectedhomeip HEAD verification failed")

        print(f"[3/4] Loading scope from {SCOPE}", flush=True)
        scope = load_json(SCOPE)
        require(scope.get("repository", {}).get("commit_sha") == PINNED_COMMIT,
                "scope.json does not reference the pinned connectedhomeip commit")

        print("[4/4] Running the existing extraction, normalization, generation, and validation pipeline", flush=True)
        command = [
            sys.executable,
            str(Path(__file__).with_name("extract_corpus.py")),
            "--source-repo", str(source),
            "--scope", str(SCOPE),
            "--output", str(OUTPUT),
            "--snapshot", str(SNAPSHOT),
        ]
        result = subprocess.run(command, cwd=PROJECT_ROOT)
        require(result.returncode == 0, f"Corpus pipeline exited with code {result.returncode}")

        summary = verify_generated_results()
        print("Corpus build completed successfully:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (CorpusError, OSError, ValueError, KeyError) as exc:
        print("Corpus build failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
