#!/usr/bin/env python3
"""answers.jsonl 을 팀 공용 AnswerRecord 로 검증한다. (이슈 #23 5절 체크리스트)

- 팀 공용 스키마(systems/system_a_rag/.../rag_proto/schema.py)로 전 줄을 파싱한다.
  System C 전용 필드는 AnswerRecord 에 없으므로 검증 전에 떼어낸다.
- (qid, model, run) 중복 / 누락을 본다.
- 토큰 4열이 invocations.jsonl 의 턴별 prompt_tokens 합과 맞는지 대조한다.
  (uncached_input + cache_read + cache_creation == Σ prompt_tokens)
- 기권 문구가 run_agent 의 상수와 글자 그대로 같은지 본다.

사용:
    python3 systems/system_c_llm_wiki/validation/validate_records.py \
        results/raw/test_low_0928/system_c
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_a_rag" / "rag_proto" / "src"))
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))

# AnswerRecord 에 없는 System C 전용 필드. 검증 전에 떼어낸다.
EXTRA_FIELDS = {
    "cited_pages", "turns", "status", "wiki_label", "wiki_build", "wiki_root",
    "questions_sha256", "agent_commit", "trace_path", "failed_attempts",
    "reasoning_effort", "provider", "started_at", "finished_at",
}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    base = Path(sys.argv[1])
    answers = base / "answers.jsonl"
    if not answers.exists():
        print(f"[실패] {answers} 없음")
        return 1

    try:
        from rag_proto.schema import AnswerRecord
    except Exception as exc:  # noqa: BLE001
        print(f"[실패] 팀 공용 스키마를 불러오지 못함: {exc}")
        print("       pip install pydantic pyyaml 후 다시 실행할 것.")
        return 1
    try:
        from run_agent import ABSTAIN_PHRASE
    except Exception:  # noqa: BLE001
        ABSTAIN_PHRASE = None

    rows = []
    errors = []
    for i, line in enumerate(answers.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        rows.append(rec)
        payload = {k: v for k, v in rec.items() if k not in EXTRA_FIELDS}
        try:
            AnswerRecord(**payload)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"  {i}행 {rec.get('qid')}/{rec.get('model')}: {exc}")

    print(f"레코드 {len(rows)}줄")
    if errors:
        print(f"[실패] AnswerRecord 검증 {len(errors)}건")
        for e in errors[:10]:
            print(e)
    else:
        print("[통과] AnswerRecord 전 줄 검증")

    # --- 중복 / 누락 ---
    keys = Counter((r["qid"], r.get("model"), r.get("run", 1)) for r in rows)
    dups = [k for k, n in keys.items() if n > 1]
    print(f"[{'실패' if dups else '통과'}] (qid, model, run) 중복 {len(dups)}건")
    for k in dups[:10]:
        print(f"  {k}")

    models = sorted({r.get("model") for r in rows})
    qids = sorted({r["qid"] for r in rows})
    runs = sorted({r.get("run", 1) for r in rows})
    expected = len(models) * len(qids) * len(runs)
    print(f"모델 {len(models)} × 질문 {len(qids)} × 회차 {len(runs)} = {expected} "
          f"({'일치' if expected == len(rows) else '불일치'})")
    if expected != len(rows):
        have = {(r["qid"], r.get("model"), r.get("run", 1)) for r in rows}
        missing = [(q, m, rn) for m in models for q in qids for rn in runs
                   if (q, m, rn) not in have]
        for k in missing[:10]:
            print(f"  누락: {k}")

    # --- 토큰 4열 대조 ---
    inv_sum: dict = defaultdict(int)
    inv_files = sorted((base / "runs").glob("*/invocations.jsonl"))
    for f in inv_files:
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            inv_sum[(d["qid"], d.get("model"), d.get("run", 1))] += d.get("prompt_tokens") or 0
    if inv_files:
        bad = []
        for r in rows:
            k = (r["qid"], r.get("model"), r.get("run", 1))
            if k not in inv_sum:
                continue
            t = r.get("tokens", {})
            got = sum((t.get(c) or 0) for c in
                      ("uncached_input", "cache_read", "cache_creation"))
            if got != inv_sum[k]:
                bad.append((k, got, inv_sum[k]))
        print(f"[{'실패' if bad else '통과'}] 토큰 4열 합 = 턴별 prompt_tokens 합 "
              f"(대조 {len(inv_sum)}건, 불일치 {len(bad)}건)")
        for k, a, b in bad[:10]:
            print(f"  {k}: 레코드 {a} vs 호출기록 {b}")
    else:
        print("[건너뜀] invocations.jsonl 이 없어 토큰 대조 불가")

    # --- 기권 문구 ---
    if ABSTAIN_PHRASE:
        n_abstain = sum(1 for r in rows if ABSTAIN_PHRASE in (r.get("answer") or ""))
        print(f"기권 {n_abstain}건 (문구: {ABSTAIN_PHRASE!r})")
        near = sum(1 for r in rows
                   if ABSTAIN_PHRASE not in (r.get("answer") or "")
                   and "확인되지 않" in (r.get("answer") or ""))
        if near:
            print(f"[주의] 문구가 미묘하게 다른 기권 후보 {near}건 — 직접 확인할 것")

    # --- status ---
    st = Counter(r.get("status") for r in rows)
    print("status:", dict(st))

    return 1 if (errors or dups or expected != len(rows)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
