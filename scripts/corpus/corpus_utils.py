"""Deterministic, read-only source discovery and shared corpus formats (stdlib only)."""
from __future__ import annotations

import csv
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

PINNED_COMMIT = "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SENTINELS = {"", "unverified", "not_applicable"}


class CorpusError(ValueError):
    """A failed invariant; never silently broaden scope or repair the source."""


def require(condition, message):
    if not condition:
        raise CorpusError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stable_id(prefix, value):
    return prefix + ":" + digest(canonical(value).encode("utf-8"))


def document_id(path):
    # Deliberately excludes snapshot, output directory, and content hash.
    return stable_id("doc", ["connectedhomeip", path])


def relative_path(value):
    p = PurePosixPath(value)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in value
            and ":" not in value and str(p) == value, f"Unsafe source path: {value}")
    return p


def canonical_text(data):
    # Source offsets in this project are code points in this decoded LF view.
    return data.decode("utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def jsonl_bytes(rows):
    return ("".join(canonical(row) + "\n" for row in rows)).encode("utf-8")


def csv_bytes(rows):
    require(bool(rows), "Empty manifest")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows({k: canonical(v) if isinstance(v, (dict, list)) else v for k, v in row.items()}
                     for row in rows)
    return stream.getvalue().encode("utf-8")


def pipeline_hash():
    files = sorted(Path(__file__).parent.glob("*.py"))
    return digest(b"".join(p.name.encode() + b"\0" + p.read_bytes() for p in files))


class Repository:
    def __init__(self, root, expected_commit=PINNED_COMMIT):
        self.root = Path(root).resolve()
        self.expected_commit = expected_commit
        require(self.root.is_dir(), f"Source repository does not exist: {self.root}")
        self.verify()
        self.entries = {}
        for record in self.git("ls-tree", "-rz", "--full-tree", "HEAD").split(b"\0"):
            if not record:
                continue
            info, name = record.split(b"\t", 1)
            mode, kind, oid = info.decode().split()
            self.entries[name.decode("utf-8")] = (mode, kind, oid)
        self.cache = {}

    def git(self, *args):
        command = ["git", "-c", f"safe.directory={self.root.as_posix()}",
                   "--no-optional-locks", "-C", str(self.root), *args]
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        require(result.returncode == 0, result.stderr.decode("utf-8", errors="replace").strip())
        return result.stdout

    def verify(self):
        head = self.git("rev-parse", "HEAD").decode().strip()
        require(head == self.expected_commit,
                f"Commit mismatch: expected {self.expected_commit}, found {head}; no checkout performed")
        remote = self.git("remote", "get-url", "origin").decode().strip()
        require(bool(re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)"
                                  r"[^/]+/connectedhomeip(?:\.git)?/?", remote)),
                "Repository identity mismatch: expected a GitHub connectedhomeip repository or fork")
        dirty = self.git("status", "--porcelain=v1", "--untracked-files=all")
        require(not dirty, "Source repository is dirty; refusing extraction: "
                + dirty.decode("utf-8", errors="replace")[:500])
        self.head, self.remote = head, remote
        self.branch = self.git("branch", "--show-current").decode().strip()

    def check_file(self, path):
        relative_path(path)
        item = self.entries.get(path)
        require(item is not None, f"Source file absent from pinned commit: {path}")
        require(item[0] in {"100644", "100755"} and item[1] == "blob",
                f"Unsupported symlink/submodule source: {path}")
        local = self.root / path
        require(local.is_file() and local.resolve().is_relative_to(self.root),
                f"Source file missing from checkout or escapes repository: {path}")

    def read_many(self, paths):
        paths = sorted(set(paths) - self.cache.keys())
        if not paths:
            return
        for path in paths:
            self.check_file(path)
        queries = "".join(self.entries[p][2] + "\n" for p in paths).encode("ascii")
        command = ["git", "-c", f"safe.directory={self.root.as_posix()}", "--no-optional-locks",
                   "-C", str(self.root), "cat-file", "--batch"]
        result = subprocess.run(command, input=queries, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        require(result.returncode == 0, "git cat-file --batch failed")
        stream = io.BytesIO(result.stdout)
        for path in paths:
            oid, kind, size = stream.readline().decode().split()
            require(oid == self.entries[path][2] and kind == "blob", f"Invalid Git blob: {path}")
            data = stream.read(int(size))
            require(len(data) == int(size) and stream.read(1) == b"\n", "Truncated Git batch")
            self.cache[path] = data

    def read(self, path):
        self.read_many([path])
        return self.cache[path]


class Selection:
    def __init__(self, repository, scope_path):
        self.repo = repository
        self.scope_path = Path(scope_path).resolve()
        self.coverage_path = self.scope_path.with_name("coverage_matrix.csv")
        self.scope = load_json(self.scope_path)
        require(self.scope["repository"]["commit_sha"] == PINNED_COMMIT == repository.head,
                "Scope does not match the fixed source commit")
        with self.coverage_path.open(encoding="utf-8", newline="") as f:
            self.coverage = list(csv.DictReader(f))
        self.included = [r for r in self.coverage if r["scope_decision"] == "include"]
        self.products = {int(p["id"], 0): p for p in self.scope["products"]}
        self.clusters = {int(c["cluster_id"], 0): c for c in self.scope["clusters"]}
        expected = self.scope["accepted_scope_counts"]
        require(len(self.clusters) == expected["unique_cluster_ids"] == 23, "Expected exactly 23 clusters")
        require(len(self.products) == expected["official_device_type_ids"] == 4, "Expected four Device Type IDs")
        cluster_rows = [r for r in self.included if r["relation_type"] == "requires_cluster"]
        require(len(cluster_rows) == expected["included_cluster_relations"], "Coverage row count mismatch")
        require({int(r["cluster_id"], 0) for r in cluster_rows} == set(self.clusters), "Scope/coverage cluster mismatch")
        for pid, product in self.products.items():
            for origin, field in [("direct", "direct_cluster_ids"), ("base", "base_cluster_ids")]:
                actual = {int(r["cluster_id"], 0) for r in cluster_rows
                          if int(r["device_type_id"], 0) == pid and r["relationship_origin"] == origin}
                require(actual == {int(i, 0) for i in product[field]}, f"Scope/coverage differs for {product['name']}")
        self.files = {}
        for group in self.scope["source_sets"]:
            for path in group.get("paths", []):
                self.add(path, group["source_role"], group["definition_kind"], "scope.source_sets")
        rules = self.scope["implementation_rules"]
        require(rules["recursive"] is False, "Recursive implementation selection not supported")
        for root in rules["component_roots"]:
            matches = [p for p in repository.entries if str(PurePosixPath(p).parent) == root
                       and any(fnmatch.fnmatchcase(PurePosixPath(p).name, g) for g in rules["include_patterns"])]
            require(matches, f"Empty scoped component: {root}")
            for path in matches:
                self.add(path, "implementation", "cluster", f"scope component {root}")
        for path in self.scope["support_definitions"]:
            if path not in self.files:
                role = "specification" if path.startswith("data_model/") else "implementation"
                self.add(path, role, "none", "scope.support_definitions")
        for row in self.included:
            require(row["commit_sha"] == repository.head, "Coverage commit mismatch")
            for key in ["specification_path", "sdk_definition_path", "documentation_path", "implementation_path",
                        "idl_path", "device_type_definition_path", "example_implementation_path"]:
                p = row[key]
                if p not in SENTINELS:
                    require(p in self.files, f"Scope inconsistency: Coverage {row['coverage_id']} refers to unselected {p}")
                    self.bind(p, row["device_type_id"], row["cluster_id"])
        # Explicit component/file associations, never keyword-based inclusion.
        for path in self.files:
            for row in cluster_rows:
                impl = row["implementation_path"]
                if impl not in SENTINELS and PurePosixPath(path).parent == PurePosixPath(impl).parent:
                    self.bind(path, row["device_type_id"], row["cluster_id"])
            if "/alarm-base-server/" in path or path.endswith("/AlarmBase.xml"):
                for row in cluster_rows:
                    if row["cluster_id"] in {"0x0057", "0x0064"}:
                        self.bind(path, row["device_type_id"], row["cluster_id"])
            if path.endswith("/ModeBase.xml") or path.endswith("/mode-base-cluster.xml"):
                for row in cluster_rows:
                    if row["cluster_id"] in {"0x0051", "0x0052", "0x0063"}:
                        self.bind(path, row["device_type_id"], row["cluster_id"])
            if path.endswith("/Label-Cluster.xml"):
                for row in cluster_rows:
                    if row["cluster_id"] in {"0x0040", "0x0041"}:
                        self.bind(path, row["device_type_id"], row["cluster_id"])
        for path in self.files:
            repository.check_file(path)
        repository.read_many(self.files)
        self.scope_hash = digest(self.scope_path.read_bytes())
        self.coverage_hash = digest(self.coverage_path.read_bytes())
        self.snapshot_id = stable_id("corpus-v0.1", [repository.head, self.scope_hash, self.coverage_hash, pipeline_hash()])

    def add(self, path, role, kind, reason):
        relative_path(path)
        require(role in self.scope["source_role_policy"]["allowed"], f"Unknown source role: {role}")
        if path not in self.files:
            self.files[path] = dict(source_role=role, definition_kind=kind, device_types=set(), clusters=set(), reasons=set())
        else:
            require(self.files[path]["source_role"] == role, f"Conflicting source roles: {path}")
        self.files[path]["reasons"].add(reason)

    def bind(self, path, device_id, cluster_id):
        if device_id not in SENTINELS:
            self.files[path]["device_types"].add(int(device_id, 0))
        if cluster_id not in SENTINELS:
            self.files[path]["clusters"].add(int(cluster_id, 0))

    def allowed_for_device(self, pid):
        p = self.products[pid]
        return {int(i, 0) for i in p["direct_cluster_ids"] + p["base_cluster_ids"]}


def writable_path(path, source_root=None):
    p = Path(path).resolve()
    require(p.is_relative_to(PROJECT_ROOT), f"Output must stay in current project: {p}")
    if source_root:
        src = Path(source_root).resolve()
        require(not p.is_relative_to(src) and not src.is_relative_to(p), "Output overlaps source repository")
    return p


def write_file(path, data, source_root=None):
    p = writable_path(path, source_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Only known generated paths are replaced; no directory deletion or stale-file removal.
    temporary = p.with_name(p.name + ".corpus-tmp")
    require(not temporary.exists(), f"Stale temporary output: {temporary}")
    temporary.write_bytes(data)
    temporary.replace(p)
