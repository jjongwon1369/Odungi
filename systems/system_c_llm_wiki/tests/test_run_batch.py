#!/usr/bin/env python3
"""run_batch 병합·이어하기 테스트. (#23 리뷰 3·4번)"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))

import run_batch as rb  # noqa: E402


def rec(q, m, r=1, wiki="c3", tag="ok", status="ok", err=None, cfg="AAA"):
    d = {"qid": q, "model": m, "run": r, "wiki_label": wiki, "answer": tag,
         "status": status, "config_hash": cfg}
    if err:
        d["error"] = err
    return d


def test_committed_rows_survive_single_model_rerun():
    tmp = Path(tempfile.mkdtemp())
    answers, partial = tmp / "answers.jsonl", tmp / ".partial"
    partial.mkdir()
    with open(answers, "w") as f:
        for m in ("gpt-6-luna", "kimi-k3", "deepseek-flash"):
            for q in ("Q1", "Q2"):
                f.write(json.dumps(rec(q, m, tag="committed")) + "\n")
    with open(partial / "deepseek-flash.jsonl", "w") as f:
        for q in ("Q1", "Q2"):
            f.write(json.dumps(rec(q, "deepseek-flash", tag="rerun")) + "\n")
    total, kept, replaced, added = rb._upsert_answers(answers, partial)
    rows = [json.loads(l) for l in open(answers)]
    by = {}
    for r in rows:
        by.setdefault(r["model"], set()).add(r["answer"])
    assert total == 6 and replaced == 2 and added == 0, (total, kept, replaced, added)
    assert by["gpt-6-luna"] == {"committed"} and by["deepseek-flash"] == {"rerun"}
    print("  ✓ 커밋된 줄 보존 + 재실행분만 교체")


def test_two_wikis_in_one_run_label_do_not_collide():
    """같은 run label 에 위키 두 벌을 돌려도 서로 지우지 않는다."""
    tmp = Path(tempfile.mkdtemp())
    answers, partial = tmp / "answers.jsonl", tmp / ".partial"
    partial.mkdir()
    with open(answers, "w") as f:
        f.write(json.dumps(rec("Q1", "m", wiki="astra", tag="astra")) + "\n")
    with open(partial / "m.jsonl", "w") as f:
        f.write(json.dumps(rec("Q1", "m", wiki="c3", tag="c3")) + "\n")
    total, _, replaced, added = rb._upsert_answers(answers, partial)
    labels = {json.loads(l)["wiki_label"] for l in open(answers)}
    assert total == 2 and labels == {"astra", "c3"}, (total, labels)
    assert replaced == 0 and added == 1
    print("  ✓ wiki_label 이 다르면 별개 행")


def test_broken_last_line_does_not_stop_merge():
    tmp = Path(tempfile.mkdtemp())
    answers, partial = tmp / "answers.jsonl", tmp / ".partial"
    partial.mkdir()
    (partial / "m.jsonl").write_text(
        json.dumps(rec("Q1", "m")) + "\n" + '{"qid":"Q2","mo', encoding="utf-8")
    total, _, _, added = rb._upsert_answers(answers, partial)
    assert total == 1 and added == 1, total
    print("  ✓ 끊긴 마지막 줄은 건너뛰고 계속")


def test_error_rows_are_requeued_not_counted_done():
    tmp = Path(tempfile.mkdtemp())
    partial = tmp / ".partial"
    partial.mkdir()
    fa = tmp / "failed_attempts.jsonl"
    with open(partial / "m.jsonl", "w") as f:
        f.write(json.dumps(rec("Q1", "m")) + "\n")
        f.write(json.dumps(rec("Q2", "m", status="error", err="boom")) + "\n")
    plan = rb.preflight_resume(partial, ["m"], "AAA", fa, False)
    assert plan["m"] == {("Q1", "m", 1)}, plan
    moved = [json.loads(l) for l in open(fa)]
    assert len(moved) == 1 and moved[0]["qid"] == "Q2", moved
    print("  ✓ 오류 행은 완료로 세지 않고 failed_attempts 로 옮겨 재실행")


def test_config_change_blocks_before_any_call():
    tmp = Path(tempfile.mkdtemp())
    partial = tmp / ".partial"
    partial.mkdir()
    (partial / "m.jsonl").write_text(json.dumps(rec("Q1", "m", cfg="OLD")) + "\n",
                                     encoding="utf-8")
    try:
        rb.preflight_resume(partial, ["m"], "NEW", tmp / "fa.jsonl", False)
    except SystemExit as e:
        assert e.code == 3, e.code
        print("  ✓ 설정 불일치 → 첫 호출 전에 exit 3")
        return
    raise AssertionError("막지 않았다")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"run_batch 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
