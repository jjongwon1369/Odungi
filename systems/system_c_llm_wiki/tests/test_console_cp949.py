#!/usr/bin/env python3
"""Windows 기본 콘솔(cp949) 테스트. (#27 동수님 리뷰 P1-1)

도움말과 출력에 cp949 가 담지 못하는 문자(— 등)가 있어, 가드가 없으면
PYTHONIOENCODING=cp949 에서 UnicodeEncodeError 로 멈춘다. 가드를 지우면 이 테스트가 실패한다.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYS_C = REPO / "systems" / "system_c_llm_wiki"
CORPUS_DOCS = REPO / "corpus/tiers/c3/processed/documents.jsonl"


def run_cp949(*args):
    env = {**os.environ, "PYTHONIOENCODING": "cp949"}
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True,
                       cwd=str(REPO), env=env)
    return p.returncode, (p.stdout + p.stderr).decode("cp949", errors="replace")


def test_cli_help_does_not_crash():
    for script in ("agent/run_agent.py", "agent/run_batch.py",
                   "validation/validate_records.py"):
        rc, out = run_cp949(SYS_C / script, "--help")
        assert rc == 0 and "UnicodeEncodeError" not in out, (script, out[-500:])
    print("  ✓ run_agent·run_batch·validate_records --help 가 cp949 에서 끝까지 실행")


def test_compare_wikis_does_not_crash():
    if not CORPUS_DOCS.exists():
        print("  - compare_wikis 건너뜀: documents.jsonl 없음")
        return
    rc, out = run_cp949(SYS_C / "validation/compare_wikis.py",
                        SYS_C / "wiki", SYS_C / "wiki-astra")
    assert "UnicodeEncodeError" not in out, out[-500:]
    print("  ✓ compare_wikis 가 cp949 에서 끝까지 실행")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"cp949 콘솔 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
