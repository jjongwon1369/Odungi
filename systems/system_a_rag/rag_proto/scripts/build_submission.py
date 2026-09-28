"""
평가 담당 제출용 폴더를 만든다(종원님 답변 A3: answers.jsonl 필수 + summary·invocations·failed_attempts + 색인 chunks.jsonl).
원본 runs/ 폴더는 건드리지 않고, 복사본에 키 조각·계정 식별자 가림(run_eval._redact와 같은 규칙)을 적용한다.
사용 (팀 rag_proto 폴더에서):
  PYTHONPATH=src python scripts/build_submission.py <출력 루트> --a <A 결과 폴더>... --b <B 결과 폴더>...
"""
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

from rag_proto.s3_embed import IN_PATH as CHUNKS_PATH

args = sys.argv[1:]
OUT = Path(args[0])
A_DIRS = [Path(x) for x in args[args.index("--a") + 1:args.index("--b")]]
B_DIRS = [Path(x) for x in args[args.index("--b") + 1:]]
KEY_LIKE = re.compile(r"\b(sk|ak|org)-[A-Za-z0-9_\-*.]{4,}")


def redact(text: str) -> tuple[str, int]:
    n = len(KEY_LIKE.findall(text))
    return KEY_LIKE.sub(lambda m: f"{m.group(1)}-[가림]", text), n


def jl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


if OUT.exists():
    shutil.rmtree(OUT)
masked = 0
report = {}
for sysname, dirs in (("system_a", A_DIRS), ("system_b", B_DIRS)):
    root = OUT / sysname
    (root / "runs").mkdir(parents=True)
    rows = []
    for d in dirs:
        rows += jl(d / "answers.jsonl")
        sub = root / "runs" / d.name
        sub.mkdir()
        for name in ("summary.json", "invocations.jsonl", "failed_attempts.jsonl", "participants.yaml"):
            src = d / name
            if src.exists():
                text, n = redact(src.read_text(encoding="utf-8"))
                masked += n
                (sub / name).write_text(text, encoding="utf-8")
    keys = [(r["qid"], r["model"], r["run"]) for r in rows]
    dup = [k for k, c in Counter(keys).items() if c > 1]
    assert not dup, f"{sysname}: 중복 (qid, model, run) {dup[:5]}"
    text, n = redact("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    masked += n
    (root / "answers.jsonl").write_text(text, encoding="utf-8")
    report[sysname] = {
        "rows": len(rows),
        "per_model": dict(Counter(r["model"] for r in rows)),
        "failed_rows": sum(1 for r in rows if not r.get("answer")),
        "query_mode": sorted({r["query_mode"] for r in rows}),
    }
idx = OUT / "index"
idx.mkdir()
shutil.copy(CHUNKS_PATH, idx / "chunks.jsonl")
report["index"] = {"chunks": sum(1 for _ in open(idx / "chunks.jsonl", encoding="utf-8"))}
report["masked_strings"] = masked
leftover = [str(p) for p in OUT.rglob("*") if p.is_file() and p.suffix in (".jsonl", ".json", ".yaml")
            and KEY_LIKE.search(p.read_text(encoding="utf-8"))]
report["leftover_key_like"] = leftover
print(json.dumps(report, ensure_ascii=False, indent=1))
