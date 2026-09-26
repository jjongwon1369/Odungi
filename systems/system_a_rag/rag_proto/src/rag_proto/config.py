"""
rag_proto.config — 설정 로더 및 검증

경로는 configs/*.yaml에만 존재한다. (명세서 §01 원칙 4)
이 모듈 외의 어떤 코드도 yaml을 직접 읽지 않는다.

검증 실행:
    python -m rag_proto.config
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

try:  # .env가 있으면 환경변수로 읽어들인다 (API 키 등)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from .schema import CorpusPhase, config_hash

CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class Config:
    ssot: dict[str, Any]
    corpus: dict[str, Any]
    pipeline: dict[str, Any]

    @property
    def commit(self) -> str:
        return self.ssot["corpus"]["commit"]

    @property
    def phase(self) -> CorpusPhase:
        return CorpusPhase(self.ssot["phase"])

    @property
    def owner(self) -> str | None:
        return self.ssot.get("owner")

    @property
    def corpus_snapshot(self) -> str | None:
        return self.ssot["corpus"].get("snapshot_id")

    @property
    def corpus_version(self) -> str | None:
        v = self.ssot["corpus"].get("corpus_version")
        return str(v) if v is not None else None

    @property
    def source_mode(self) -> str:
        return self.corpus.get("source", "repo")

    @property
    def config_hash(self) -> str:
        return config_hash(self.pipeline)

    @property
    def repo_root(self) -> Path:
        return Path(self.corpus["repo_root"]).expanduser().resolve()


def load(config_dir: Path | None = None) -> Config:
    d = config_dir or CONFIG_DIR
    return Config(
        ssot=yaml.safe_load((d / "ssot.yaml").read_text(encoding="utf-8")),
        corpus=yaml.safe_load((d / "corpus.yaml").read_text(encoding="utf-8")),
        pipeline=yaml.safe_load((d / "pipeline.yaml").read_text(encoding="utf-8")),
    )


PARTICIPANTS_FILE = "participants.yaml"


def load_participants(config_dir: Path | None = None) -> list[dict]:
    """configs/participants.yaml의 참가자 LLM 목록. defaults를 각 항목에 채워서 돌려준다."""
    d = config_dir or CONFIG_DIR
    raw = yaml.safe_load((d / PARTICIPANTS_FILE).read_text(encoding="utf-8"))
    defaults = raw.get("defaults") or {}
    return [{**defaults, **p} for p in raw["participants"]]


def validate(cfg: Config) -> list[str]:
    """
    설정을 검사하고 문제 목록을 돌려준다.
    빈 리스트면 S1 착수 가능.
    """
    problems: list[str] = []

    commit = cfg.ssot["corpus"]["commit"]
    if not _SHA_RE.match(commit):
        problems.append(
            f"ssot.corpus.commit이 40자 소문자 16진수가 아닙니다: {commit!r}\n"
            "    → git rev-parse HEAD 결과를 그대로 넣으세요. 7자 축약형은 금지."
        )

    if cfg.phase is CorpusPhase.SAMPLE and not cfg.owner:
        problems.append("phase가 sample인데 owner가 비어 있습니다. 누구 샘플인지 기록하세요.")
    if cfg.phase is CorpusPhase.INTEGRATED and cfg.owner:
        problems.append("phase가 integrated면 owner는 비워야 합니다.")

    if cfg.pipeline["generation"]["model"].startswith("TODO"):
        problems.append(
            "pipeline.generation.model이 미정입니다.\n"
            "    → RAG와 LLM Wiki가 반드시 동일 모델이어야 비교가 성립합니다."
        )

    if cfg.source_mode == "team_corpus":
        tc = cfg.corpus.get("team_corpus") or {}
        docs_path = Path(tc.get("documents_path", "")).expanduser()
        if not docs_path.exists():
            problems.append(
                f"team_corpus.documents_path가 없습니다: {docs_path}\n"
                "    → documents.jsonl 은 저장소에 커밋되지 않습니다 (corpus/.gitignore).\n"
                "      코퍼스 담당자에게 받아 이 경로에 두세요."
            )
        if not cfg.corpus_snapshot:
            problems.append(
                "ssot.corpus.snapshot_id가 비어 있습니다.\n"
                "    → 같은 commit에서 Device Type 3/6/12개 코퍼스가 갈라지므로 snapshot_id가 필요합니다.\n"
                "      corpus/metadata/snapshot.json 의 snapshot_id 를 넣으세요."
            )
        return problems  # repo 모드 검사는 건너뛴다

    if not cfg.repo_root.exists():
        problems.append(
            f"corpus.repo_root가 존재하지 않습니다: {cfg.repo_root}\n"
            "    → git clone ... 후 ssot.yaml 의 commit 으로 checkout"
        )

    if not cfg.corpus.get("device_types"):
        problems.append(
            "corpus.device_types가 비어 있습니다.\n"
            "    → 코퍼스는 Device Type에서 출발해 참조 Cluster를 따라간다.\n"
            "      최소 1종(냉장고·세탁기·에어컨 중)은 있어야 한다. (명세서 §02 공통 규칙 4)"
        )

    dm_version = cfg.corpus.get("data_model_version")
    if not dm_version:
        problems.append(
            "corpus.data_model_version이 비어 있습니다.\n"
            "    → data_model/ 아래 1.3 / 1.4 / 1.4.1 / 1.4.2 / master 중 하나를 골라야 한다.\n"
            "      비워두면 같은 클러스터가 버전 수만큼 중복 색인된다."
        )
    elif cfg.repo_root.exists():
        dm_dir = cfg.repo_root / "data_model" / str(dm_version)
        if not dm_dir.exists():
            problems.append(
                f"data_model/{dm_version}/ 디렉토리가 없습니다: {dm_dir}\n"
                "    → git sparse-checkout set docs data_model src/app/clusters"
            )

    return problems


def main() -> int:
    cfg = load()
    problems = validate(cfg)

    print(f"commit       : {cfg.ssot['corpus']['commit']}")
    print(f"branch       : {cfg.ssot['corpus'].get('branch')}")
    print(f"snapshot     : {cfg.corpus_snapshot or '-'}")
    print(f"corpus ver   : {cfg.corpus_version or '-'}")
    print(f"source       : {cfg.source_mode}")
    print(f"phase        : {cfg.phase.value}  (owner={cfg.owner})")
    print(f"config_hash  : {cfg.config_hash}")
    print(f"repo_root    : {cfg.repo_root}")
    print()

    if not problems:
        print("설정 검증 통과. S1 착수 가능합니다.")
        return 0

    print(f"{len(problems)}건의 문제가 있습니다.\n")
    for i, p in enumerate(problems, 1):
        print(f"  [{i}] {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
