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
  5. 출력 토큰 0 / 빈 답변 / 생성 시간(latency_ms.generate)      — 생성 시간은 System C
  6. 추론 강도(reasoning_applied)가 전 행에 적용됐는지          — System C
  7. 기권 문구 일치, status 분포

행 판정은 System A 규칙을 따른다 (#27 A 기준 점검). A 의 run_eval._is_retryable 처럼
error 가 있고 answer 가 빈 행만 재실행 대상이고, 답변이 있는 행은 채점 대상이다.
  [실패] error + 빈 answer(A 크래시·GenerationError), status error, status max_turns(구버전),
         오류 없이 빈 answer, 출력 토큰 0, System C 행의 generate 0
  [참고] error + answer(A/B dangling_citations), no_submit(도구 없이 텍스트로 답한 행),
         읽지 않은 페이지 인용, 답변 속 도구 호출 표기

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
    "attempt_id",
    "provider", "started_at", "finished_at", "page_evidence",
    # run_batch 가 쓰는 C 전용 필드. partial_answer 는 오류 행의 중간 텍스트다. (#27 A 기준 점검)
    "abstained", "wiki_pages_evidence", "partial_answer",
}
TOKEN_COLS = ("uncached_input", "cache_read", "cache_creation", "output")
# 답변에 섞여 나온 도구 호출 표기. 9/28 sonnet Q-codedoc-004 는 submit_answer 인자 안에
# '</answer>\n<parameter name="cited_pages">…' 를 써서 cited_pages 가 비었다. (#27 A 기준 점검)
TOOL_MARKUP = ("<parameter", "</answer>", "<invoke", "</invoke>")


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

    def note(self, msg: str, details: list | None = None, show: int = 10) -> None:
        # 실패에서 참고로 내린 항목도 어느 행인지는 보여준다. (#27 A 기준 점검)
        print(f"[참고] {msg}")
        for d in (details or [])[:show]:
            print(f"    {d}")
        if details and len(details) > show:
            print(f"    … 외 {len(details) - show}건")

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


def _is_retryable(rec: dict) -> bool:
    """A 의 run_eval._is_retryable 과 같은 기준. (#27 A 기준 점검)

    크래시 행(답변 없음 + error)만 재실행 대상이다. dangling_citations 처럼 답변이 있는
    오류 행은 정상 생성이라 채점한다. 예전에는 error 가 있으면 전부 실패로 두어 A/B 의
    dangling 행(9/28 A 2건, B 1건)까지 재실행을 요구했다.
    """
    return bool(rec.get("error")) and not rec.get("answer")


def _err_detail(rec: dict) -> str:
    s = f"{_key(rec)}: {str(rec.get('error') or rec.get('status'))[:80]}"
    if rec.get("answer"):
        # 구버전 run_batch 는 Anthropic 경로의 중간 서술을 오류 행 answer 에 남겼다. A 규칙
        # (error + answer = 정상 줄)으로 읽으면 서술이 답변으로 채점된다. (#27 A 기준 점검)
        s += f"  [answer {len(rec['answer'])}자 남음 - 새 run_batch 는 비우고 partial_answer 에 둔다]"
    return s


def _cols_from_raw(raw: dict | None) -> dict | None:
    """usage_raw 에서 4열을 모두 다시 계산한다. (#23 리뷰)

    입력 합계만 비교하면 열 배분이 틀린 경우(#23의 캐시 쓰기 누락)와 output 오류를
    잡지 못한다. 응답 형태마다 필드 위치가 다르므로 형태별로 나눈다.

      Anthropic : uncached = input_tokens (캐시 제외), creation/read 는 전용 필드
      Responses : input_tokens 는 캐시 포함 → 읽기·쓰기를 빼서 uncached 계산
      Chat      : prompt_tokens 는 캐시 포함 → 같은 방식
    """
    if not isinstance(raw, dict):
        return None

    def g(*names):
        for n in names:
            v = raw.get(n)
            if isinstance(v, int):
                return v
        return None

    # Anthropic
    if "input_tokens" in raw and ("cache_creation_input_tokens" in raw
                                  or "cache_read_input_tokens" in raw):
        return {
            "uncached_input": g("input_tokens"),
            "cache_creation": g("cache_creation_input_tokens") or 0,
            "cache_read": g("cache_read_input_tokens") or 0,
            "output": g("output_tokens"),
        }

    det = raw.get("input_tokens_details") or raw.get("prompt_tokens_details") or {}
    if not isinstance(det, dict):
        det = {}
    cache_read = det.get("cached_tokens")
    if not isinstance(cache_read, int):
        cache_read = g("prompt_cache_hit_tokens", "cached_tokens") or 0
    cache_write = det.get("cache_write_tokens")
    if not isinstance(cache_write, int):
        cache_write = g("cache_write_tokens") or 0
    prompt = g("prompt_tokens", "input_tokens")
    if prompt is None:
        return None
    return {
        "uncached_input": max(0, prompt - cache_read - cache_write),
        "cache_creation": cache_write,
        "cache_read": cache_read,
        "output": g("completion_tokens", "output_tokens"),
    }


def _safe_console() -> None:
    """Windows 기본 콘솔(cp949)에서 출력할 수 없는 문자가 있어도 멈추지 않게 한다.
    담지 못하는 문자는 '?' 로 바뀐다. (#27 동수님 리뷰 P1-1)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main() -> int:
    _safe_console()
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base_dir", help="results/raw/<실험명>/system_x")
    ap.add_argument("--models-json", default=None,
                    help="기대 모델 목록(models.json). --models 와 둘 중 하나는 필수")
    ap.add_argument("--models", default=None, help="쉼표로 구분한 기대 모델 목록")
    ap.add_argument("--questions", default=None,
                    help="기대 문항 파일(questions_v1.jsonl). 필수")
    ap.add_argument("--infer-grid-from-file", action="store_true",
                    help="기대 격자를 결과 파일 내용에서 역산(모델·문항 통째 누락을 못 잡는다). "
                         "확인용으로만 쓸 것")
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
    parse_errors = [f"{i}행: JSON 파싱 실패 - {r['__parse_error__']}"
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

    # 기대 격자 - 파일 내용이 아니라 밖에서 받는다
    if args.models:
        exp_models = [m.strip() for m in args.models.split(",") if m.strip()]
        src_m = "--models"
    elif args.models_json:
        exp_models = sorted(json.loads(Path(args.models_json).read_text(encoding="utf-8")))
        src_m = args.models_json
    elif args.infer_grid_from_file:
        exp_models = sorted({r.get("model") for r in recs})
        src_m = "(파일 내용에서 추론 - 모델 통째 누락은 못 잡는다)"
    else:
        print("[실패] 기대 모델 목록이 없습니다. --models-json 또는 --models 를 주세요.\n"
              "       (확인용으로 파일 내용에서 역산하려면 --infer-grid-from-file)")
        return 2

    if args.questions:
        qp = Path(args.questions)
        exp_qids = [json.loads(l)["qid"] if "qid" in json.loads(l) else json.loads(l)["query_id"]
                    for l in qp.read_text(encoding="utf-8").splitlines() if l.strip()]
        src_q = args.questions
    elif args.infer_grid_from_file:
        exp_qids = sorted({r.get("qid") for r in recs})
        src_q = "(파일 내용에서 추론 - 문항 통째 누락은 못 잡는다)"
    else:
        print("[실패] 기대 문항 파일이 없습니다. --questions 를 주세요.\n"
              "       (확인용으로 파일 내용에서 역산하려면 --infer-grid-from-file)")
        return 2

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
    # 오류 행은 토큰·빈답·추론 판정에서 한 번만 센다. 여러 항목에서 중복으로
    # 실패로 잡히면 무엇이 문제인지 흐려진다. (#23 리뷰)
    # 재실행 대상은 A 기준이다: error 가 있고 answer 가 빈 행(_is_retryable). System C 의
    # status error 는 새 run_batch 에서 answer 가 늘 비어 있으므로 같은 행이다. (#27 A 기준 점검)
    err_rows = [r for r in recs if _is_retryable(r) or r.get("status") == "error"]
    # max_turns 는 새 run_batch 가 오류 행(answer '')으로 바꾼다. 남아 있으면 구버전 결과다.
    turn_rows = [r for r in recs if r.get("status") == "max_turns" and not _is_retryable(r)]
    err_keys = {_key(r) for r in err_rows + turn_rows}
    good = [r for r in recs if _key(r) not in err_keys]
    if err_rows:
        rep.bad(f"오류 행 {len(err_rows)}건 - 재실행 필요 (error 가 있고 answer 가 빈 행, "
                f"System C 는 status error 포함)", [_err_detail(r) for r in err_rows])
    else:
        rep.ok("오류 행 없음")
    if turn_rows:
        rep.bad(f"max_turns 로 끝난 행 {len(turn_rows)}건 - 구버전 결과. 새 run_batch 는 "
                f"오류 행(answer '')으로 남겨 재실행한다", [f"{_key(r)}" for r in turn_rows])
    # error 가 있지만 답변이 있는 행. A/B 의 dangling_citations 행이 여기 든다. A 는 이 행을
    # 다시 돌리지 않고 채점한다(results/raw/test_low_0928/system_a/README.md '채점할 때 참고').
    answered_err = [r for r in good if r.get("error")]
    if answered_err:
        rep.note(f"error 가 있지만 답변이 있는 행 {len(answered_err)}건 - 채점 대상 정상 줄, "
                 f"재실행하지 않는다 (A 의 dangling_citations 행과 같다)",
                 [f"{_key(r)}: {str(r.get('error'))[:80]}" for r in answered_err])

    inv_files = sorted((base / "runs").glob("*/invocations.jsonl"))
    if inv_files:
        # attempt_id 가 있으면 같은 시도의 줄만 본다. 같은 폴더에 다시 돌렸을 때
        # 이전 시도의 호출 기록이 함께 더해져 전부 거짓 불일치가 됐다. (#23 리뷰)
        turn_sum: dict = defaultdict(int)
        raw_cols: dict = defaultdict(lambda: {c: 0 for c in TOKEN_COLS})
        raw_seen: dict = {}
        other_attempts = 0
        row_attempt = {_key(r): r.get("attempt_id") for r in recs}
        for f in inv_files:
            for _, d in _read_jsonl(f):
                if "__parse_error__" in d:
                    continue
                k = (d.get("qid"), d.get("model"), d.get("run", 1))
                want = next((a for kk, a in row_attempt.items()
                             if kk[:3] == k and a), None)
                if want and d.get("attempt_id") and d["attempt_id"] != want:
                    other_attempts += 1
                    continue
                turn_sum[k] += d.get("prompt_tokens") or 0
                cols = _cols_from_raw(d.get("usage_raw"))
                if cols:
                    raw_seen[k] = True
                    for c in TOKEN_COLS:
                        v = cols.get(c)
                        if isinstance(v, int):
                            raw_cols[k][c] += v
        if other_attempts:
            rep.note(f"다른 attempt_id 의 호출 기록 {other_attempts}줄은 대조에서 제외 "
                     f"(과금분이므로 별도 집계 대상)")

        covered = sum(1 for r in good if _key(r)[:3] in turn_sum)
        if covered == 0:
            rep.skip(f"이 폴더의 호출 기록이 답변 행을 덮지 않아 토큰 대조 불가 "
                     f"(0/{len(good)}행) - System A/B 는 해당 없음")
        else:
            if covered < len(good):
                rep.note(f"호출기록이 {covered}/{len(good)}행만 덮는다")
            mismatch, raw_mismatch = [], []
            for r in good:
                k = _key(r)[:3]
                if k not in turn_sum:
                    continue
                got = sum(_tok(r, c) for c in
                          ("uncached_input", "cache_read", "cache_creation"))
                if got != turn_sum[k]:
                    mismatch.append(f"{k}: 레코드 {got} vs 호출기록 {turn_sum[k]}")
                if raw_seen.get(k):
                    for c in TOKEN_COLS:
                        want = raw_cols[k][c]
                        have = _tok(r, c)
                        if have != want:
                            raw_mismatch.append(
                                f"{k}.{c}: 레코드 {have} vs usage_raw {want}")
            label = f"토큰 입력 합 == 턴별 prompt_tokens 합 (대조 {covered}/{len(good)}행)"
            if mismatch:
                if args.no_strict_tokens:
                    rep.note(f"{label} - 불일치 {len(mismatch)}건 (경고 모드)")
                    for m in mismatch[:5]:
                        print(f"    {m}")
                else:
                    rep.bad(f"{label} - 불일치 {len(mismatch)}건", mismatch)
            else:
                rep.ok(label)

            if raw_seen:
                lab2 = f"4열 전부 == usage_raw 재계산 (대조 {len(raw_seen)}행)"
                if raw_mismatch:
                    # 경고 모드에서도 반드시 보여준다. 예전에는 아무것도 안 나왔다. (#23 리뷰)
                    if args.no_strict_tokens:
                        rep.note(f"{lab2} - 불일치 {len(raw_mismatch)}건 (경고 모드)")
                        for m in raw_mismatch[:10]:
                            print(f"    {m}")
                    else:
                        rep.bad(f"{lab2} - 불일치 {len(raw_mismatch)}건", raw_mismatch)
                else:
                    rep.ok(lab2)
            else:
                rep.skip("usage_raw 가 호출기록에 없어 4열 재계산 대조 불가 "
                         "(구버전 실행 결과. 재실행하면 기록된다)")
    else:
        rep.skip("invocations.jsonl 이 없어 토큰 대조 불가 (System A/B 는 해당 없음)")

    # ---------- 5. 빈 응답 / 생성 시간 / 제출 / 인용 ----------
    zero_out = [f"{_key(r)}" for r in good if _tok(r, "output") == 0]
    empty_ans = [f"{_key(r)}" for r in good if not (r.get("answer") or "").strip()]
    if zero_out:
        rep.bad(f"출력 토큰 0인 행 {len(zero_out)}건 (오류 행 제외)", zero_out)
    else:
        rep.ok("출력 토큰 0인 행 없음")
    if empty_ans:
        # A 는 빈 답변을 GenerationError 로 오류 행(answer '')으로 남겨 재실행한다. 오류 없이
        # 빈 답이 남았다면 기록기가 이 규칙을 지키지 않은 것이다. (#27 A 기준 점검)
        rep.bad(f"answer 가 빈 행 {len(empty_ans)}건 (오류 행 제외)", empty_ans)

    # System C 행은 LLM 호출 시간(턴별 api_ms 합)을 latency_ms.generate 에 남긴다. A 는 s6 생성
    # 시간을 같은 칸에 남기므로, 0이면 두 시스템의 생성 시간을 비교할 수 없다. A/B 행에는
    # 적용하지 않는다. (#27 A 기준 점검)
    if any(r.get("system") == "wiki" for r in recs):
        wiki_rows = [r for r in good if r.get("system") == "wiki"
                     and r.get("status") in ("ok", "no_submit")]
        no_gen = [f"{_key(r)}" for r in wiki_rows
                  if not (r.get("latency_ms") or {}).get("generate")]
        if no_gen:
            rep.bad(f"latency_ms.generate 가 0이거나 없는 System C 행 {len(no_gen)}건 "
                    f"(status ok/no_submit)", no_gen)
        else:
            rep.ok(f"System C 행 latency_ms.generate 기록됨 ({len(wiki_rows)}행)")
    else:
        rep.skip("latency_ms.generate 검사는 System C 전용 (System A/B 는 해당 없음)")

    no_sub = [f"{_key(r)}" for r in good if r.get("status") == "no_submit"]
    if any("status" in r for r in recs):
        if no_sub:
            # submit_answer 없이 텍스트로 끝난 행은 인용 없는 답변으로 채점한다. A 도 [chunk_id]
            # 없는 평문 답변을 그대로 채점하고 다시 돌리지 않는다. 실패로 두면 이 행만 골라
            # 다시 돌리게 되어 C 에만 추가 시도가 생긴다. (#27 A 기준 점검)
            rep.note(f"submit_answer 없이 텍스트로 끝난 행 {len(no_sub)}건 - "
                     f"인용 없는 답변으로 채점, 재실행하지 않는다", no_sub)
        else:
            rep.ok("전 행이 submit_answer 로 제출됨")

    # 읽지 않은 페이지를 인용한 행
    if any("cited_pages" in r for r in recs):
        bad_cite = []
        for r in good:
            read = set((r.get("retrieved") or {}).get("wiki_pages") or [])
            cited = set(r.get("cited_pages") or [])
            extra = cited - read
            if extra:
                bad_cite.append(f"{_key(r)}: {sorted(extra)}")
        if bad_cite:
            # A/B 의 dangling_citations 와 같은 성격이다. A 는 답변을 그대로 두고 표시만 하며
            # 다시 돌리지 않는다. 근거성은 cited_pages 가 아니라 retrieved.wiki_pages(실제로
            # 읽은 페이지) 기준으로 볼 것. (#27 A 기준 점검)
            rep.note(f"read_page 로 읽지 않은 페이지를 인용한 행 {len(bad_cite)}건 - "
                     f"채점 대상 정상 줄, 재실행하지 않는다 (A/B 의 dangling_citations 에 해당)",
                     bad_cite)
        else:
            rep.ok("인용 페이지가 모두 열람 기록 안에 있음")

    # 답변 속 도구 호출 표기. 모델이 만든 답이므로 재실행하지 않고 표시만 한다. 채점 전에
    # 걷어낼지는 채점 담당이 A/B 의 태그 처리와 같은 규칙으로 정한다. (#27 A 기준 점검)
    leaked = []
    for r in good:
        hits = [m for m in TOOL_MARKUP if m in (r.get("answer") or "")]
        if hits:
            leaked.append(f"{_key(r)}: {hits}")
    if leaked:
        rep.note(f"답변에 도구 호출 표기가 섞인 행 {len(leaked)}건 - 채점 대상, 재실행하지 않는다",
                 leaked)
    else:
        rep.ok("답변에 도구 호출 표기 없음")

    # ---------- 6. 추론 강도 ----------
    if any("reasoning_applied" in r for r in recs):
        not_applied = [f"{_key(r)} (effort={r.get('reasoning_effort')})"
                       for r in good if not r.get("reasoning_applied")]
        if not_applied:
            rep.bad(f"추론 강도가 적용되지 않은 행 {len(not_applied)}건 (오류 행 제외)",
                    not_applied)
        else:
            efforts = Counter(r.get("reasoning_effort") for r in good)
            rep.ok(f"추론 강도 전 행 적용 - {dict(efforts)}")
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
            rep.note(f"문구가 미묘하게 다른 기권 후보 {len(near)}건 - 직접 확인할 것")
            for m in near[:5]:
                print(f"    {m}")

    cfgs = Counter(r.get("config_hash") for r in recs)
    if len(cfgs) > 1:
        rep.bad(f"config_hash 가 {len(cfgs)}종 섞여 있다",
                [f"{h}: {n}행" for h, n in cfgs.most_common()])
    else:
        rep.ok(f"config_hash 단일 - {next(iter(cfgs), None)}")

    if any("status" in r for r in recs):
        print("status:", dict(Counter(r.get("status") for r in recs)))

    print()
    print("=== 결과: " + ("실패 - 위 항목을 고칠 것" if rep.failed else "전 항목 통과") + " ===")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
