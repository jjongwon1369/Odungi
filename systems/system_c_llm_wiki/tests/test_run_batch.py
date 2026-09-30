#!/usr/bin/env python3
"""run_batch 병합·이어하기 테스트. (#23 리뷰 3·4번, #27 3차 리뷰 3, 동수님 리뷰 P1-2)"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))

import run_batch as rb  # noqa: E402


def rec(q, m, r=1, wiki="c3", tag="ok", status="ok", err=None, cfg="AAA", aid=None):
    d = {"qid": q, "model": m, "run": r, "wiki_label": wiki, "answer": tag,
         "status": status, "config_hash": cfg}
    if err:
        d["error"] = err
    if aid:
        d["attempt_id"] = aid
    return d


def write_lines(path, rows, tail=""):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows) + tail, encoding="utf-8")


def lines(path):
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


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


# ---- #27 3차 리뷰 3, 동수님 리뷰 P1-2 ----

def test_rerun_success_is_not_requeued_again():
    """다시 돌려 성공한 문항의 이전 오류 행을 이어하기마다 또 옮기지 않는다."""
    tmp = Path(tempfile.mkdtemp())
    partial, fa = tmp / ".partial", tmp / "failed_attempts.jsonl"
    partial.mkdir()
    write_lines(partial / "m.jsonl", [
        rec("Q1", "m", status="error", err="boom", aid="a1"),
        rec("Q1", "m", aid="a2"),                       # 재실행 성공
    ])
    write_lines(fa, [{"attempt": "resume-requeued", "qid": "Q1", "model": "m",
                      "run": 1, "attempt_id": "a1"}])
    for _ in range(2):
        plan = rb.preflight_resume(partial, ["m"], "AAA", fa, False)
        assert plan["m"] == {("Q1", "m", 1)}, plan
    assert len(lines(fa)) == 1, lines(fa)
    print("  ✓ 재실행 성공한 문항은 완료, 이전 오류 행을 다시 옮기지 않음")


def test_same_error_attempt_is_moved_once():
    tmp = Path(tempfile.mkdtemp())
    partial, fa = tmp / ".partial", tmp / "failed_attempts.jsonl"
    partial.mkdir()
    write_lines(partial / "m.jsonl", [rec("Q2", "m", status="error", err="boom", aid="a1")])
    for _ in range(3):
        plan = rb.preflight_resume(partial, ["m"], "AAA", fa, False)
        assert plan["m"] == set(), plan               # 매번 다시 돌릴 대상
    assert len(lines(fa)) == 1, lines(fa)
    print("  ✓ 같은 시도의 오류 행은 failed_attempts 에 한 번만")


def test_config_mismatch_writes_nothing():
    """exit 3 으로 멈출 때는 오류 행을 옮기지 않는다(멈춘 뒤 기록만 늘지 않게)."""
    tmp = Path(tempfile.mkdtemp())
    partial, fa = tmp / ".partial", tmp / "failed_attempts.jsonl"
    partial.mkdir()
    write_lines(partial / "a.jsonl", [rec("Q1", "a", status="error", err="boom", aid="a1")])
    write_lines(partial / "b.jsonl", [rec("Q1", "b", cfg="OLD")])
    try:
        rb.preflight_resume(partial, ["a", "b"], "AAA", fa, False)
    except SystemExit as e:
        assert e.code == 3 and not fa.exists(), (e.code, lines(fa))
        print("  ✓ 설정 불일치 exit 3 → failed_attempts 에 아무것도 안 씀")
        return
    raise AssertionError("막지 않았다")


def test_requeue_limited_to_questions_in_scope():
    tmp = Path(tempfile.mkdtemp())
    partial, fa = tmp / ".partial", tmp / "failed_attempts.jsonl"
    partial.mkdir()
    write_lines(partial / "m.jsonl", [
        rec("Q1", "m", status="error", err="boom", aid="a1"),
        rec("Q9", "m", status="error", err="boom", aid="a1"),
    ])
    rb.preflight_resume(partial, ["m"], "AAA", fa, False, scope_qids={"Q1"})
    moved = [json.loads(l)["qid"] for l in lines(fa)]
    assert moved == ["Q1"], moved
    print("  ✓ 이번에 돌릴 문항(--limit 등)의 오류 행만 옮김")


def test_requeued_error_text_is_redacted():
    tmp = Path(tempfile.mkdtemp())
    partial, fa = tmp / ".partial", tmp / "failed_attempts.jsonl"
    partial.mkdir()
    write_lines(partial / "m.jsonl", [
        rec("Q1", "m", status="error", err="401 key sk-proj-ABCD1234efgh", aid="a1")])
    rb.preflight_resume(partial, ["m"], "AAA", fa, False)
    text = fa.read_text(encoding="utf-8")
    assert "ABCD1234" not in text and "sk-[가림]" in text, text
    print("  ✓ 옮기는 오류 문자열의 키 가림")


def test_summary_rows_are_latest_per_key():
    """summary 는 키마다 마지막 줄만 센다. 끊긴 줄에서 멈추지 않는다. (동수님 리뷰 P1-2)"""
    tmp = Path(tempfile.mkdtemp())
    p = tmp / "m.jsonl"
    write_lines(p, [
        rec("Q1", "m", status="error", err="boom", aid="a1"),
        rec("Q1", "m", aid="a2"),
        rec("Q2", "m", aid="a2"),
    ], tail='{"qid":"Q3","mo')
    rows = list(rb._latest_rows(p, rb._record_key).values())
    assert len(rows) == 2 and all(r["status"] == "ok" for r in rows), rows
    print("  ✓ 재실행 행 중복 없이 2건, 끊긴 줄은 건너뜀")


def test_rerun_inside_partial_counts_keys_not_lines():
    """.partial 안에 같은 키가 두 줄이어도 유지·교체 수가 맞는다(예전에는 유지가 음수)."""
    tmp = Path(tempfile.mkdtemp())
    answers, partial = tmp / "answers.jsonl", tmp / ".partial"
    partial.mkdir()
    write_lines(answers, [rec("Q1", "m", tag="old"), rec("Q2", "m", tag="old")])
    write_lines(partial / "m.jsonl", [
        rec("Q1", "m", status="error", err="boom"),
        rec("Q1", "m", tag="new"),
    ])
    total, kept, replaced, added = rb._upsert_answers(answers, partial)
    assert (total, kept, replaced, added) == (2, 1, 1, 0), (total, kept, replaced, added)
    print("  ✓ 유지 1 / 교체 1 / 추가 0")


def test_append_after_torn_line_starts_on_new_line():
    """끊긴 마지막 줄 뒤에 이어 쓰면 새 레코드가 그 줄에 붙지 않는다."""
    tmp = Path(tempfile.mkdtemp())
    p = tmp / "m.jsonl"
    write_lines(p, [rec("Q1", "m")], tail='{"qid":"Q2","mo')
    rb._ensure_trailing_newline(p)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec("Q3", "m")) + "\n")
    got = rb._latest_rows(p, rb._record_key)
    assert {k[0] for k in got} == {"Q1", "Q3"}, got
    rb._ensure_trailing_newline(p)                   # 이미 줄바꿈이면 아무것도 안 함
    assert not p.read_text(encoding="utf-8").endswith("\n\n")
    print("  ✓ 끊긴 줄 뒤 이어 쓰기 → 새 레코드는 온전")


def test_torn_multibyte_line_is_skipped():
    """한글 중간에서 끊긴 줄도 건너뛴다. 파일 전체를 한 번에 디코딩하면 여기서 멈췄다."""
    tmp = Path(tempfile.mkdtemp())
    partial, fa = tmp / ".partial", tmp / "failed_attempts.jsonl"
    partial.mkdir()
    torn = '{"qid":"Q9","answer":"한'.encode("utf-8")[:-1]
    (partial / "m.jsonl").write_bytes(
        (json.dumps(rec("Q1", "m"), ensure_ascii=False) + "\n").encode("utf-8") + torn)
    fa.write_bytes(torn)
    plan = rb.preflight_resume(partial, ["m"], "AAA", fa, False)
    assert plan["m"] == {("Q1", "m", 1)}, plan
    total, _, _, added = rb._upsert_answers(tmp / "answers.jsonl", partial)
    assert total == 1 and added == 1, total
    print("  ✓ 한글 중간에서 끊긴 줄(.partial, failed_attempts) → 건너뛰고 계속")


# ---- run_batch() 전체: 호출 지점 배선 ----

def _run_batch_env(tmp: Path):
    """run_agent·코퍼스 검사를 가짜로 바꾸고 tmp 에서 run_batch() 를 부를 준비를 한다."""
    wiki = tmp / "wiki"
    wiki.mkdir()
    qpath = tmp / "questions.jsonl"
    write_lines(qpath, [{"query_id": "Q1", "question": "질문1"},
                        {"query_id": "Q2", "question": "질문2"}])
    model = next(k for k in rb._load_models() if not k.startswith("_"))
    calls: list = []
    outcomes: dict = {}

    def fake_agent(query, max_turns, verbose, model, wiki_root):
        qid = {"질문1": "Q1", "질문2": "Q2"}[query]
        calls.append(qid)
        status = outcomes[qid].pop(0)
        retry = status == "ok+retry"          # 429 재시도 기록이 붙은 정상 응답
        status = "ok" if retry else status
        return {"status": status, "answer": "답" if status == "ok" else "",
                "error": "응답이 온전하지 않음 (finish_reason=length)" if status == "error" else None,
                "turns": 1, "cited_pages": [], "retrieved": {"wiki_pages": []},
                "token_usage": {"prompt_tokens": 100, "cache_read": 0,
                                "cache_write": 0, "output_tokens": 10},
                "turn_details": [{"turn": 1, "calls": [], "prompt_tokens": 100,
                                  "cache_read": 0, "cache_write": 0, "output_tokens": 10}],
                "failed_attempts": ([{"attempt": 1, "error": "429 Too Many Requests",
                                      "wait_s": 5, "ts": 0}] if retry else []),
                "page_evidence": []}

    patches = {
        "run_agent": fake_agent,
        "_read_corpus_meta": lambda: {"corpus_snapshot": "corpus-c3:test",
                                      "corpus_version": "test"},
        "check_wiki_provenance": lambda *a: {"corpus_source": "test",
                                             "corpus_snapshot": "corpus-c3:test"},
        "_git_short_head": lambda: "test",
    }

    def go(max_turns=5, limit=None):
        saved = {k: getattr(rb, k) for k in patches}
        cwd = os.getcwd()
        try:
            for k, v in patches.items():
                setattr(rb, k, v)
            os.chdir(tmp)
            rb.run_batch([model], str(qpath), str(wiki), "c3", 1, "L", max_turns,
                         False, limit)
        finally:
            os.chdir(cwd)
            for k, v in saved.items():
                setattr(rb, k, v)

    run_dir = tmp / "results/raw/L/system_c/runs/c3_run1"
    return go, calls, outcomes, model, run_dir


def test_run_batch_resume_summary_and_exit3_end_to_end():
    tmp = Path(tempfile.mkdtemp())
    go, calls, outcomes, model, run_dir = _run_batch_env(tmp)
    partial = run_dir / ".partial" / f"{model}.jsonl"
    fa = run_dir / "failed_attempts.jsonl"
    answers = tmp / "results/raw/L/system_c/answers.jsonl"

    def requeued():
        return [r for r in rb._read_jsonl(fa) if r and r.get("attempt") == "resume-requeued"]

    def summary():
        return json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))["results"][model]

    # 1회: Q1 오류, Q2 정상
    outcomes.update(Q1=["error"], Q2=["ok"])
    go()
    assert calls == ["Q1", "Q2"] and summary()["err"] == 1, (calls, summary())

    # 한글 중간에서 끊긴 줄을 .partial 과 failed_attempts 끝에 남긴다
    torn = '{"qid":"Q3","answer":"한'.encode("utf-8")[:-1]
    with open(partial, "ab") as f:
        f.write(torn)
    with open(fa, "ab") as f:
        f.write(torn)

    # 2회: Q1 만 다시 돈다
    calls.clear()
    outcomes.update(Q1=["ok"])
    go()
    assert calls == ["Q1"], calls
    assert summary()["ok"] == 2 and summary()["err"] == 0, summary()
    rows = [r for r in rb._read_jsonl(answers) if r]
    assert len(rows) == 2 and all(r["status"] == "ok" for r in rows), rows
    assert [r["qid"] for r in requeued()] == ["Q1"], requeued()

    # 3회: 할 일 없음, 오류 행을 또 옮기지 않는다
    calls.clear()
    go()
    assert calls == [] and len(requeued()) == 1 and summary()["ok"] == 2, (calls, requeued())

    # 설정이 바뀌면 exit 3, models.json 사본과 failed_attempts 는 그대로
    (run_dir / "models.json").write_text("SENTINEL", encoding="utf-8")
    fa_before = fa.read_bytes()
    try:
        go(max_turns=6)
    except SystemExit as e:
        assert e.code == 3, e.code
    else:
        raise AssertionError("설정 변경을 막지 않았다")
    assert (run_dir / "models.json").read_text(encoding="utf-8") == "SENTINEL"
    assert fa.read_bytes() == fa_before and calls == []
    print("  ✓ run_batch(): Q1 만 재실행, summary ok 2/err 0, 재큐 1회, 끊긴 줄 무시, exit 3 은 아무것도 안 씀")


def test_run_batch_limit_scope_and_failed_attempts_append():
    # --limit 으로 돌린 실행은 범위 밖 문항의 오류 행을 옮기지 않는다
    tmp = Path(tempfile.mkdtemp())
    go, calls, outcomes, model, run_dir = _run_batch_env(tmp)
    fa = run_dir / "failed_attempts.jsonl"

    def requeued():
        return [r["qid"] for r in rb._read_jsonl(fa) if r and r.get("attempt") == "resume-requeued"]

    outcomes.update(Q1=["ok"], Q2=["error", "ok"])
    go()
    calls.clear()
    go(limit=1)
    assert calls == [] and requeued() == [], (calls, requeued())
    go()
    assert calls == ["Q2"] and requeued() == ["Q2"], (calls, requeued())

    # 재큐가 없는 실행에서도, 끊긴 마지막 줄 뒤에 쓰는 호출 기록은 새 줄에서 시작한다
    tmp = Path(tempfile.mkdtemp())
    go, calls, outcomes, model, run_dir = _run_batch_env(tmp)
    fa = run_dir / "failed_attempts.jsonl"
    outcomes.update(Q1=["ok+retry"], Q2=["ok+retry"])
    go(limit=1)
    with open(fa, "ab") as f:
        f.write('{"qid":"Q9","error":"응'.encode("utf-8")[:-1])
    go()
    retried = [r["qid"] for r in rb._read_jsonl(fa) if r and r.get("attempt") == 1]
    assert retried == ["Q1", "Q2"], retried
    print("  ✓ run_batch(): --limit 범위 밖 오류 행은 그대로, 끊긴 줄 뒤 호출 기록도 온전")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"run_batch 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
