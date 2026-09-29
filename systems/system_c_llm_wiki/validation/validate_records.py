#!/usr/bin/env python3
"""답변 레코드 검증기 — 이슈 #23 5절 체크리스트를 코드로 고정한다.

System A / B / C 어느 결과 폴더에나 돌아간다.

기대 격자(모델 × 문항 × 회차)를 **파일 내용이 아니라 밖에서** 받는다.
파일에서 역산하면 모델이나 회차가 통째로 빠졌을 때 "일치"로 통과해버린다.

검사 항목
  1. 팀 공용 AnswerRecord(pydantic)로 전 줄 파싱
  2. (qid, model, run) 중복 / 기대 격자 대비 누락
  3. 토큰 4열 == 호출기록(invocations.jsonl)의 턴별 합  — 불일치는 실패
  4. usage_raw 원본과 4열 대조 (provider별 필드 위치 확인)  — System C
  5. 출력 토큰 0 / 빈 답변
  6. 추론 강도(reasoning_applied)가 전 행에 적용됐는지          — System C
  7. 기권 문구 일치, status 분포

사용:
    python3 systems/system_c_llm_wiki/validation/validate_records.py \
        results/raw/<실험명>/system_c \
        --models-json systems/system_c_llm_wiki/agent/models.json \
        --questions benchmark/questions_v1.jsonl --runs 1
"""
from __future__ import annotations

import argparse
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
    "wiki_corpus_source", "wiki_corpus_snapshot",
    "questions_sha256", "agent_commit", "trace_path", "failed_attempts",
    "reasoning_effort", "reasoning_config", "reasoning_applied", "reasoning_note",
    "provider", "started_at", "finished_at", "page_evidence",
}
TOKEN_COLS = ("uncached_input", "cache_read", "cache_creation", "output")


class Report:
    def __init__(self) -> None:
        self.failed = False

    def ok(self, msg: str) -> None:
        print(f"[통과] {msg}")

    def bad(self, msg: str, details: list | None = None, show: int = 10) -> None:
        self.failed = True
        print(f"[실패] {msg}")
        for d in (details or [])[:show]:
            print(f"    {d}")
        if details and len(details) > show:
            print(f"    … 외 {len(details) - show}건")

    def note(self, msg: str) -> None:
        print(f"[참고] {msg}")

    def skip(self, msg: str) -> None:
        print(f"[건너뜀] {msg}")


def _read_jsonl(path: Path) -> list:
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append((i, json.loads(line)))
        except json.JSONDecodeError as exc:
            rows.append((i, {"__parse_error__": str(exc)}))
    return rows


def _key(rec: dict) -> tuple:
    return (rec.get("qid"), rec.get("model"), rec.get("run", 1))


def _tok(rec: dict, col: str) -> int:
    return (rec.get("tokens") or {}).get(col) or 0


def _raw_prompt_total(raw: dict | None) -> int | None:
    """usage_raw 에서 '전체 입력 토큰'을 꺼낸다. provider마다 이름이 다르다."""
    if not isinstance(raw, dict):
        return None
    for k in ("prompt_tokens", "input_tokens"):
        if isinstance(raw.get(k), int):
            return raw[k]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base_dir", help="results/raw/<실험명>/system_x")
    ap.add_argument("--models-json", default=None,
                    help="기대 모델 목록(models.json). 없으면 --models 나 파일 내용에서 추론")
    ap.add_argument("--models", default=None, help="쉼표로 구분한 기대 모델 목록")
    ap.add_argument("--questions", default=None,
                    help="기대 문항 파일(questions_v1.jsonl). 없으면 파일 내용에서 추론")
    ap.add_argument("--runs", default="1", help="기대 회차 (예: 1 또는 1,2,3)")
    ap.add_argument("--no-strict-tokens", action="store_true",
                    help="토큰 불일치를 경고로만 처리")
    args = ap.parse_args()

    base = Path(args.base_dir)
    answers = base / "answers.jsonl"
    if not answers.exists():
        print(f"[실패] {answers} 없음")
        return 1

    rep = Report()

    try:
        from rag_proto.schema import AnswerRecord
    except Exception as exc:  # noqa: BLE001
        print(f"[실패] 팀 공용 스키마를 불러오지 못함: {exc}")
        print("       pip install pydantic 후 다시 실행할 것.")
        return 1
    try:
        from run_agent import ABSTAIN_PHRASE
    except Exception:  # noqa: BLE001
        ABSTAIN_PHRASE = None

    # ---------- 1. 스키마 ----------
    raw_rows = _read_jsonl(answers)
    parse_errors = [f"{i}행: JSON 파싱 실패 — {r['__parse_error__']}"
                    for i, r in raw_rows if "__parse_error__" in r]
    rows = [(i, r) for i, r in raw_rows if "__parse_error__" not in r]
    print(f"레코드 {len(rows)}줄  ({answers})")
    if parse_errors:
        rep.bad(f"JSON 파싱 {len(parse_errors)}건", parse_errors)

    schema_errors = []
    for i, rec in rows:
        payload = {k: v for k, v in rec.items() if k not in EXTRA_FIELDS}
        try:
            AnswerRecord(**payload)
        except Exception as exc:  # noqa: BLE001
            first = str(exc).split("\n")
            schema_errors.append(f"{i}행 {rec.get('qid')}/{rec.get('model')}: "
                                 + " / ".join(x.strip() for x in first[1:3]))
    if schema_errors:
        rep.bad(f"AnswerRecord 검증 {len(schema_errors)}건", schema_errors)
    else:
        rep.ok("AnswerRecord 전 줄 검증")

    recs = [r for _, r in rows]

    # ---------- 2. 중복 / 누락 ----------
    counts = Counter(_key(r) for r in recs)
    dups = [f"{k} ×{n}" for k, n in counts.items() if n > 1]
    if dups:
        rep.bad(f"(qid, model, run) 중복 {len(dups)}건", dups)
    else:
        rep.ok("(qid, model, run) 중복 없음")

    # 기대 격자 — 파일 내용이 아니라 밖에서 받는다
    if args.models:
        exp_models = [m.strip() for m in args.models.split(",") if m.strip()]
        src_m = "--models"
    elif args.models_json:
        exp_models = sorted(json.loads(Path(args.models_json).read_text(encoding="utf-8")))
        src_m = args.models_json
    else:
        exp_models = sorted({r.get("model") for r in recs})
        src_m = "(파일 내용에서 추론 — 모델 통째 누락은 못 잡는다)"

    if args.questions:
        qp = Path(args.questions)
        exp_qids = [json.loads(l)["qid"] if "qid" in json.loads(l) else json.loads(l)["query_id"]
                    for l in qp.read_text(encoding="utf-8").splitlines() if l.strip()]
        src_q = args.questions
    else:
        exp_qids = sorted({r.get("qid") for r in recs})
        src_q = "(파일 내용에서 추론 — 문항 통째 누락은 못 잡는다)"

    exp_runs = [int(x) for x in str(args.runs).split(",") if x.strip()]
    print(f"기대 격자: 모델 {len(exp_models)} × 문항 {len(exp_qids)} × 회차 {len(exp_runs)} "
          f"= {len(exp_models) * len(exp_qids) * len(exp_runs)}")
    print(f"  모델 출처: {src_m}")
    print(f"  문항 출처: {src_q}")

    have = set(counts)
    missing = [(q, m, rn) for m in exp_models for q in exp_qids for rn in exp_runs
               if (q, m, rn) not in have]
    extra = [k for k in have
             if k[1] not in exp_models or k[0] not in exp_qids or k[2] not in exp_runs]
    if missing:
        rep.bad(f"누락 {len(missing)}건", [str(k) for k in missing])
    else:
        rep.ok("기대 격자 전부 존재")
    if extra:
        rep.bad(f"기대 격자 밖의 행 {len(extra)}건", [str(k) for k in extra])

    # ---------- 3·4. 토큰 ----------
    inv_files = sorted((base / "runs").glob("*/invocations.jsonl"))
    if inv_files:
        turn_sum: dict = defaultdict(int)
        raw_sum: dict = defaultdict(int)
        raw_seen: dict = defaultdict(bool)
        for f in inv_files:
            for _, d in _read_jsonl(f):
                if "__parse_error__" in d:
                    continue
                k = (d.get("qid"), d.get("model"), d.get("run", 1))
                turn_sum[k] += d.get("prompt_tokens") or 0
                rp = _raw_prompt_total(d.get("usage_raw"))
                if rp is not None:
                    raw_sum[k] += rp
                    raw_seen[k] = True

        mismatch, raw_mismatch = [], []
        for r in recs:
            k = _key(r)
            if k not in turn_sum:
                continue
            got = sum(_tok(r, c) for c in ("uncached_input", "cache_read", "cache_creation"))
            if got != turn_sum[k]:
                mismatch.append(f"{k}: 레코드 {got} vs 호출기록 {turn_sum[k]}")
            if raw_seen.get(k) and got != raw_sum[k]:
                raw_mismatch.append(f"{k}: 레코드 {got} vs usage_raw {raw_sum[k]}")

        covered = sum(1 for r in recs if _key(r) in turn_sum)
        if covered < len(recs):
            rep.note(f"호출기록이 {covered}/{len(recs)}행만 덮는다 — "
                     f"나머지는 토큰 대조에서 빠진다")
        label = f"토큰 4열 합 == 턴별 prompt_tokens 합 (대조 {covered}/{len(recs)}행)"
        if mismatch and not args.no_strict_tokens:
            rep.bad(f"{label} — 불일치 {len(mismatch)}건", mismatch)
        elif mismatch:
            rep.note(f"{label} — 불일치 {len(mismatch)}건 (경고 모드)")
            for m in mismatch[:5]:
                print(f"    {m}")
        else:
            rep.ok(label)

        if raw_seen:
            if raw_mismatch and not args.no_strict_tokens:
                rep.bad(f"토큰 4열 합 == usage_raw 원본 합 — 불일치 {len(raw_mismatch)}건",
                        raw_mismatch)
            elif not raw_mismatch:
                rep.ok(f"토큰 4열 합 == usage_raw 원본 합 (대조 {len(raw_seen)}건)")
        else:
            rep.skip("usage_raw 가 호출기록에 없어 원본 대조 불가 "
                     "(구버전 실행 결과. 재실행하면 기록된다)")
    else:
        rep.skip("invocations.jsonl 이 없어 토큰 대조 불가 (System A/B 는 해당 없음)")

    # ---------- 5. 빈 응답 ----------
    zero_out = [f"{_key(r)}" for r in recs if _tok(r, "output") == 0 and not r.get("error")]
    empty_ans = [f"{_key(r)}" for r in recs if not (r.get("answer") or "").strip()]
    if zero_out:
        rep.bad(f"출력 토큰 0인데 error 도 없는 행 {len(zero_out)}건", zero_out)
    else:
        rep.ok("출력 토큰 0인 행 없음")
    if empty_ans:
        rep.bad(f"answer 가 빈 행 {len(empty_ans)}건", empty_ans)

    # ---------- 6. 추론 강도 ----------
    if any("reasoning_applied" in r for r in recs):
        not_applied = [f"{_key(r)} (effort={r.get('reasoning_effort')})"
                       for r in recs if not r.get("reasoning_applied")]
        if not_applied:
            rep.bad(f"추론 강도가 적용되지 않은 행 {len(not_applied)}건", not_applied)
        else:
            efforts = Counter(r.get("reasoning_effort") for r in recs)
            rep.ok(f"추론 강도 전 행 적용 — {dict(efforts)}")
    else:
        rep.skip("reasoning_applied 필드 없음 (System A/B)")

    # ---------- 7. 기권 / status / config_hash ----------
    if ABSTAIN_PHRASE:
        n_ab = sum(1 for r in recs if ABSTAIN_PHRASE in (r.get("answer") or ""))
        near = [f"{_key(r)}" for r in recs
                if ABSTAIN_PHRASE not in (r.get("answer") or "")
                and "확인되지 않" in (r.get("answer") or "")]
        print(f"기권 {n_ab}건 (문구: {ABSTAIN_PHRASE!r})")
        if near:
            rep.note(f"문구가 미묘하게 다른 기권 후보 {len(near)}건 — 직접 확인할 것")
            for m in near[:5]:
                print(f"    {m}")

    cfgs = Counter(r.get("config_hash") for r in recs)
    if len(cfgs) > 1:
        rep.bad(f"config_hash 가 {len(cfgs)}종 섞여 있다",
                [f"{h}: {n}행" for h, n in cfgs.most_common()])
    else:
        rep.ok(f"config_hash 단일 — {next(iter(cfgs), None)}")

    if any("status" in r for r in recs):
        print("status:", dict(Counter(r.get("status") for r in recs)))

    print()
    print("=== 결과: " + ("실패 — 위 항목을 고칠 것" if rep.failed else "전 항목 통과") + " ===")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
