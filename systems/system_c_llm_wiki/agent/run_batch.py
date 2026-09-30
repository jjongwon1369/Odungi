# -*- coding: utf-8 -*-
"""
LLM Wiki 배치 평가 러너 (System C) — run_batch.py
==================================================

benchmark/questions_v1.jsonl의 질문을 7개 모델로 실행하고
팀 공용 AnswerRecord v0.3 형식으로 results/raw/<run_label>/system_c/answers.jsonl을 출력한다.

사용법 (리포 루트에서):
    set -a; . ./.env.local; set +a

    # 스모크 테스트 (2문항, 전 모델)
    python3 systems/system_c_llm_wiki/agent/run_batch.py \\
        --wiki-root systems/system_c_llm_wiki/wiki-astra \\
        --wiki-label astra --models all --limit 2 --run-label smoke_test

    # 본실행
    python3 systems/system_c_llm_wiki/agent/run_batch.py \\
        --wiki-root systems/system_c_llm_wiki/wiki-astra \\
        --wiki-label astra --models all --run-label test_low_0928
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_agent import run_agent, ABSTAIN_PHRASE, MAX_OUTPUT_TOKENS, _build_system_prompt, _load_models, reset_interval_wait, get_interval_wait_s, redact

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
SCHEMA_VERSION = "0.3"
CORPUS_COMMIT = "1ac132b5ecd42cb6c78772f2576ed6f7fc814183"
CORPUS_PHASE = "integrated"
# 위키 컴파일러가 읽어야 하는 입력. 위키 프론트매터의 corpus_source 와 대조한다. (#23 1-4)
# 경로는 저장소 루트 기준으로 잡는다. 실행 위치 기준이면 다른 디렉터리에서 돌렸을 때
# 조용히 못 읽고, snapshot 대조를 건너뛴 채 통과한다. (#23 리뷰)
REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_CORPUS_SOURCE = os.environ.get(
    "CORPUS_DOCS", "corpus/tiers/c3/processed/documents.jsonl")
SNAPSHOT_JSON = REPO_ROOT / "corpus/tiers/c3/metadata/snapshot.json"
IDENTIFIER_CONFIG_DEFAULT = REPO_ROOT / "systems/system_a_rag/rag_proto/configs/pipeline.yaml"
REASONING_EFFORT_LABEL = "light"


# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _config_hash(cfg: dict) -> str:
    canonical = json.dumps(cfg, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _git_short_head() -> str:
    """현재 커밋. 커밋되지 않은 변경이 있으면 -dirty를 붙인다. (#23 3절)

    깨끗한 커밋에서 돌렸는지 레코드만 보고 알 수 있어야 재현이 성립한다.
    """
    cwd = Path(__file__).parent
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=cwd,
        ).stdout.strip()
        if not head:
            return "unknown"
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, cwd=cwd,
        ).stdout.strip()
        return f"{head}-dirty" if dirty else head
    except Exception:
        return "unknown"


def _read_corpus_meta() -> dict:
    """corpus/tiers/c3/metadata/snapshot.json에서 corpus_snapshot, corpus_version을 읽는다."""
    try:
        data = json.loads(SNAPSHOT_JSON.read_text(encoding="utf-8"))
        meta = {
            "corpus_snapshot": data.get("snapshot_id"),
            "corpus_version": data.get("corpus_version"),
        }
    except Exception as exc:  # noqa: BLE001
        # 여기서 None 을 돌려주면 아래 snapshot 대조가 통째로 건너뛰어진다. (#23 리뷰)
        raise SystemExit(
            f"[오류] {SNAPSHOT_JSON} 을 읽을 수 없습니다 ({exc}).\n"
            "       코퍼스 스냅샷을 확인하지 못한 채로는 실행하지 않습니다."
        )
    if not meta["corpus_snapshot"]:
        raise SystemExit(f"[오류] {SNAPSHOT_JSON} 에 snapshot_id 가 없습니다.")
    return meta


def _get_wiki_build(wiki_root: Path) -> str:
    """위키 페이지 프론트매터의 compiled_by를 읽는다."""
    for md_file in sorted(wiki_root.rglob("*.md")):
        if md_file.stem.lower() == "readme":
            continue
        text = md_file.read_text(encoding="utf-8")
        if text.startswith("---"):
            for line in text.split("\n"):
                if line.startswith("compiled_by:"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
    return "unknown"


def _get_wiki_provenance(wiki_root: Path) -> tuple:
    """위키 페이지 프론트매터의 corpus_source / corpus_snapshot 을 모은다. (#23 1-4)

    반환: (corpus_source 집합, corpus_snapshot 집합, 둘 중 하나라도 없는 페이지 수)
    """
    sources: set = set()
    snapshots: set = set()
    missing = 0
    for md_file in sorted(wiki_root.rglob("*.md")):
        if md_file.stem.lower() == "readme":
            continue
        text = md_file.read_text(encoding="utf-8")
        if not text.startswith("---") or text.count("---") < 2:
            missing += 1
            continue
        head = text.split("---", 2)[1]
        found = {}
        for line in head.split("\n"):
            for key in ("corpus_source", "corpus_snapshot"):
                if line.startswith(key + ":"):
                    found[key] = line.split(":", 1)[1].strip().strip('"').strip("'")
        if "corpus_source" in found:
            sources.add(found["corpus_source"])
        if found.get("corpus_snapshot") and found["corpus_snapshot"] != "UNKNOWN":
            snapshots.add(found["corpus_snapshot"])
        if "corpus_source" not in found or not found.get("corpus_snapshot"):
            missing += 1
    return sources, snapshots, missing


def check_wiki_provenance(wiki_root: Path, expected_source: str,
                          expected_snapshot: str | None,
                          allow_mismatch: bool) -> dict:
    """위키가 실제로 어떤 코퍼스로 컴파일됐는지 확인한다. (#23 1-4)

    레코드의 corpus_version / corpus_snapshot 은 코퍼스 메타데이터를 그대로 베껴 쓴다.
    위키가 다른 입력으로 만들어져 있어도 "c3로 돌렸다"고 적히게 된다 — 실제로 그랬다.
    그래서 실행 전에 위키 프론트매터를 직접 보고, 경로와 snapshot_id 둘 다 대조한다.
    """
    sources, snapshots, missing = _get_wiki_provenance(wiki_root)
    problems = []
    if missing:
        problems.append(f"출처 정보가 없는 페이지 {missing}개(구버전 컴파일)")
    if sources - {expected_source}:
        problems.append(f"다른 경로로 컴파일된 페이지: {sorted(sources - {expected_source})}")
    if not snapshots:
        problems.append("위키에 corpus_snapshot 이 하나도 없다(전부 UNKNOWN 또는 누락)")
    if expected_snapshot and snapshots - {expected_snapshot}:
        problems.append(
            f"snapshot 불일치 — 레코드에 적을 값 {expected_snapshot} / "
            f"위키에 박힌 값 {sorted(snapshots)}"
        )
    if not problems:
        print(f"[확인] 위키 출처 = {expected_source} / {expected_snapshot} (전 페이지 일치)")
        return {"corpus_source": expected_source, "corpus_snapshot": expected_snapshot}

    msg = (
        f"[경고] {wiki_root} 의 출처가 이번 실행이 기록할 값과 다르다 — "
        + " / ".join(problems) + "\n"
        f"        이대로 돌리면 레코드에는 {expected_snapshot} 로 적히지만 실제 입력은 다르다.\n"
        f"        위키를 --force 로 재컴파일하거나, 의도한 것이면 --allow-corpus-mismatch 를 붙일 것."
    )
    if not allow_mismatch:
        print(msg, file=sys.stderr)
        raise SystemExit(2)
    print(msg + "\n        (--allow-corpus-mismatch 로 계속 진행)", file=sys.stderr)
    return {
        "corpus_source": ",".join(sorted(sources)) or "unknown",
        "corpus_snapshot": ",".join(sorted(snapshots)) or "unknown",
    }


def _wiki_pages_digest(wiki_root: Path) -> str:
    """위키 페이지 경로+내용의 해시. 위키가 바뀌면 config_hash 도 바뀐다. (#23 리뷰)"""
    h = hashlib.sha256()
    for md in sorted(wiki_root.rglob("*.md")):
        h.update(md.relative_to(wiki_root).as_posix().encode("utf-8"))
        h.update(b"\0")
        h.update(md.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _tool_defs_digest() -> str:
    """도구 정의(list_pages / read_page / submit_answer) 해시."""
    try:
        from run_agent import _tools_responses, _tools_chat, _tools_anthropic
        blob = json.dumps(
            [_tools_responses(), _tools_chat(), _tools_anthropic()],
            sort_keys=True, ensure_ascii=False, default=str)
    except Exception:  # noqa: BLE001
        from run_agent import _tools_responses
        blob = json.dumps(_tools_responses(), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _safe_console() -> None:
    """Windows 기본 콘솔(cp949)처럼 출력 인코딩이 모든 문자를 담지 못해도 멈추지 않게 한다.
    담지 못하는 문자는 '?' 로 바뀐다. (#27 동수님 리뷰 P1-1)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def _ensure_trailing_newline(path: Path) -> None:
    """끝이 줄바꿈이 아닌(끊긴 마지막 줄이 있는) 파일에 이어 쓰기 전에 줄을 끊는다.
    그러지 않으면 새 레코드가 끊긴 줄에 붙어 함께 깨진다. (#27 3차 리뷰)"""
    try:
        if path.exists() and path.stat().st_size > 0:
            with open(path, "rb") as f:
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    with open(path, "a", encoding="utf-8") as g:
                        g.write("\n")
    except OSError:
        pass


def _read_jsonl(path: Path):
    """jsonl 의 줄마다 dict 를 돌려준다. 끊기거나 깨진 줄은 None.

    바이트로 읽어 줄마다 따로 디코딩한다. 파일 전체를 한 번에 디코딩하면 한글 중간에서
    끊긴 마지막 줄 하나 때문에 UnicodeDecodeError 로 전부 못 읽는다. "\\n" 으로만 나누므로
    본문 속 U+2028 같은 문자에서 줄이 갈리지도 않는다. (#27 3차 리뷰)"""
    if not path.exists():
        return
    for raw in path.read_bytes().split(b"\n"):
        raw = raw.strip()
        if not raw:
            continue
        try:
            rec = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            yield None
            continue
        yield rec if isinstance(rec, dict) else None


def _latest_rows(path: Path, key_fn) -> dict:
    """추가 전용 jsonl 에서 키마다 마지막 줄만 남긴다. 깨진 줄은 건너뛴다.

    .partial 은 추가 전용이라, 다시 돌려 성공한 행 앞에 이전 오류 행이 그대로 남는다.
    줄을 모두 세면 오류 행이 두 번 세지고 이어하기마다 다시 옮겨진다. (#27 3차 리뷰 3, 동수님 리뷰 P1-2)"""
    latest: dict = {}
    for rec in _read_jsonl(path):
        if rec is None:
            continue
        try:
            k = key_fn(rec)
        except (KeyError, TypeError):
            continue
        latest[k] = rec
    return latest


def _record_key(rec: dict) -> tuple:
    # wiki_label 을 넣는다. 같은 질문·모델이라도 다른 위키로 돌린 건 다른 행이다. (#23 리뷰)
    return (rec.get("qid"), rec.get("model"), rec.get("run", 1), rec.get("wiki_label"))


def _upsert_answers(answers_path: Path, partial_dir: Path) -> tuple:
    """기존 answers.jsonl 위에 이번 실행의 partial 결과를 덮어씌운다. (#23 3절)

    - 이번 run 폴더의 .partial 만 재생한다. 예전에는 runs/*/.partial 전체를 폴더
      이름 순으로 재생해서, 같은 run label 안에 위키를 두 벌 돌리면 이름이 뒤에 오는
      폴더의 행이 남았다. (#23 리뷰)
    - 키에 wiki_label 을 넣는다. 같은 (qid, model, run) 이라도 위키가 다르면 다른 행이다.
    - .partial 마지막 줄이 끊겨 있어도 멈추지 않고 그 줄만 건너뛴다. 예전에는 이후
      모든 병합이 JSONDecodeError 로 실패했다.
    - 임시파일 → os.replace 로 원자적으로 쓴다.
    """
    records: dict = {}
    order: list = []
    skipped_broken = 0

    def put(rec: dict) -> str:
        k = _record_key(rec)
        seen = k in records
        if not seen:
            order.append(k)
        records[k] = rec
        return "replaced" if seen else "added"

    def feed(path: Path, count_ops: bool) -> tuple:
        nonlocal skipped_broken
        rep = add = 0
        for rec in _read_jsonl(path):
            if rec is None:
                skipped_broken += 1
                continue
            op = put(rec)
            if count_ops:
                if op == "replaced":
                    rep += 1
                else:
                    add += 1
        return rep, add

    feed(answers_path, False)                     # 커밋돼 있는 줄 포함
    before = set(records)
    touched: set = set()
    for partial_path in sorted(partial_dir.glob("*.jsonl")):
        touched |= set(_latest_rows(partial_path, _record_key))
        feed(partial_path, True)
    # 키 단위로 센다. 줄 단위로 세면 .partial 안의 재실행 줄 때문에 '유지'가 음수가 됐다.
    replaced = len(touched & before)
    added = len(touched - before)

    tmp = answers_path.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for k in order:
            f.write(json.dumps(records[k], ensure_ascii=False) + "\n")
    os.replace(tmp, answers_path)
    if skipped_broken:
        print(f"[경고] 깨진 줄 {skipped_broken}개를 건너뛰었다 (끊긴 마지막 줄 등)",
              file=sys.stderr)
    return len(records), len(before - touched), replaced, added


def _partition_partial(path: Path, cfg_hash: str) -> tuple:
    """(다시 돌릴 필요 없는 키, 다시 돌릴 오류 행, 설정이 다른 행) 로 나눈다."""
    keep: set = set()
    error_rows: list = []
    stale: dict = {}
    # 키마다 마지막 줄만 본다. 다시 돌려 성공한 행 앞에 남은 이전 오류 행은 이미 처리됐다.
    # 예전에는 모든 줄을 세서 같은 오류 행을 이어하기마다 다시 옮겼다. (#27 3차 리뷰 3)
    latest = _latest_rows(path, lambda r: (r["qid"], r["model"], r["run"]))
    for key, r in latest.items():
        row_cfg = r.get("config_hash")
        if cfg_hash and row_cfg and row_cfg != cfg_hash:
            stale[row_cfg] = stale.get(row_cfg, 0) + 1
            continue
        if r.get("status") == "error" or r.get("error"):
            error_rows.append(r)      # 완료로 세지 않고 다시 돌린다
            continue
        keep.add(key)
    return keep, error_rows, stale


def _already_requeued(failed_attempts_path: Path) -> set:
    """이미 failed_attempts.jsonl 로 옮긴 (qid, model, run, attempt_id)."""
    done: set = set()
    for r in _read_jsonl(failed_attempts_path):
        if r is not None and r.get("attempt") == "resume-requeued":
            done.add((r.get("qid"), r.get("model"), r.get("run"), r.get("attempt_id")))
    return done


def preflight_resume(partial_dir: Path, models: list, cfg_hash: str,
                     failed_attempts_path: Path,
                     allow_config_change: bool,
                     scope_qids: set | None = None) -> dict:
    """첫 API 호출 전에 선택한 모든 모델의 partial 을 검사한다. (#23 리뷰)

    예전에는 이 검사가 모델 루프 안에 있어서, 뒤 모델에서 exit 3 이 나기 전에
    앞 모델들이 이미 과금되는 호출을 다 해버렸다.
    오류 행은 failed_attempts.jsonl 로 옮겨 과금 기록을 남기고 다시 돌린다.
    (#27 3차 리뷰 3) 설정 불일치 검사를 기록보다 먼저 해서, exit 3 으로 멈출 때는 아무것도
    쓰지 않는다. 이번에 실제로 다시 돌릴 문항(scope_qids)의 오류 행만 옮기고, 이미 옮긴
    시도(같은 attempt_id)는 다시 옮기지 않는다. A 의 run_eval._prepare_resume 과 같은 방식이다.
    """
    plan: dict = {}
    stale_all: dict = {}
    errors_by_model: dict = {}
    for model_name in models:
        path = partial_dir / f"{model_name}.jsonl"
        keep, error_rows, stale = _partition_partial(path, cfg_hash)
        plan[model_name] = keep
        errors_by_model[model_name] = error_rows
        for h, n in stale.items():
            stale_all[h] = stale_all.get(h, 0) + n

    if stale_all:
        detail = ", ".join(f"{h}×{n}" for h, n in sorted(stale_all.items()))
        msg = (
            f"[경고] 기존 결과에 지금과 다른 설정으로 만든 행이 있다 — "
            f"현재 {cfg_hash} / 기존 {detail}\n"
            f"        설정이 바뀐 뒤 이어서 돌리면 한 파일에 조건이 섞인다.\n"
            f"        새 --run-label 로 처음부터 돌리거나, 의도한 것이면 "
            f"--allow-config-change 를 붙일 것."
        )
        if not allow_config_change:
            print(msg, file=sys.stderr)
            raise SystemExit(3)
        print(msg + "\n        (--allow-config-change: 해당 행은 다시 돌린다)", file=sys.stderr)

    already = _already_requeued(failed_attempts_path)
    moved = 0
    for model_name, error_rows in errors_by_model.items():
        todo = [r for r in error_rows
                if (scope_qids is None or r.get("qid") in scope_qids)
                and (r.get("qid"), r.get("model"), r.get("run"), r.get("attempt_id")) not in already]
        if not todo:
            continue
        # 과금 기록을 버리지 않고 옮긴다
        _ensure_trailing_newline(failed_attempts_path)
        with open(failed_attempts_path, "a", encoding="utf-8") as f:
            for r in todo:
                f.write(json.dumps({
                    "attempt": "resume-requeued",
                    "qid": r.get("qid"), "model": r.get("model"), "run": r.get("run"),
                    "error": redact(r.get("error") or r.get("status") or "")[:500],
                    "tokens": r.get("tokens"),
                    "attempt_id": r.get("attempt_id"),
                    "ts": time.time(),
                }, ensure_ascii=False) + "\n")
        moved += len(todo)
        print(f"  [재실행 예정] {model_name}: 오류 행 {len(todo)}개", file=sys.stderr)

    total_done = sum(len(v) for v in plan.values())
    print(f"[이어하기] 완료 {total_done}건 / 오류 재실행 {moved}건", file=sys.stderr)
    return plan


def _sort_models_kimi_first(models: list[str]) -> list[str]:
    """kimi-k3를 맨 앞으로 옮긴다 (RPM 제한으로 가장 오래 걸림)."""
    if "kimi-k3" in models:
        rest = [m for m in models if m != "kimi-k3"]
        return ["kimi-k3"] + rest
    return models


# ---------------------------------------------------------------------------
# AnswerRecord 생성
# ---------------------------------------------------------------------------

# A·B와 동일하게 마침표 없는 문구를 기준으로, 답변에 포함되어 있으면 기권으로 본다.
# 기권 문구는 run_agent(프롬프트)와 같은 상수를 본다.
# System A/B의 s6_generate.ABSTAIN_PHRASE와도 글자 그대로 같아야 한다.
ABSTAIN_TEXT = ABSTAIN_PHRASE


# 식별자 추출 규칙. 하드코딩하지 않고 System A의 configs/pipeline.yaml 을 런타임에 읽는다.
# 같은 패턴·같은 스톱워드·같은 정렬이어야 A·B·C의 식별자 무손실 지표를 대조할 수 있다. (#23 3절)
# re.ASCII: 유니코드 \b는 한글도 단어 문자로 봐서 "0x0202입니다"를 놓친다.
# (rag_proto.schema.extract_identifiers 와 동일한 동작 — pydantic 의존을 피하려고 여기서 재현한다.)
_ic = os.environ.get("IDENTIFIER_CONFIG", "").strip()
IDENTIFIER_CONFIG = Path(_ic) if _ic else IDENTIFIER_CONFIG_DEFAULT
def _parse_identifiers_block(text: str) -> tuple:
    """pyyaml 없이 `identifiers:` 블록만 읽는다.

    C 만 돌리는 환경에는 A 의 의존성(pyyaml)이 없을 수 있다. 그렇다고 폴백 규칙을
    쓰면 A 와 어긋나도 드러나지 않으므로, A 의 설정 파일 자체를 최소 파서로 읽는다.
    대상은 다음 모양뿐이다:

        identifiers:
          patterns:
            - '...'
          stopwords:
            - "..."
    """
    pats: list = []
    stops: list = []
    section = None       # "patterns" | "stopwords"
    in_block = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0:
            in_block = stripped.startswith("identifiers:")
            section = None
            continue
        if not in_block:
            continue
        if stripped.startswith("patterns:"):
            section = "patterns"
            continue
        if stripped.startswith("stopwords:"):
            section = "stopwords"
            continue
        if stripped.startswith("- ") and section:
            item = stripped[2:].split("#", 1)[0].strip()
            if len(item) >= 2 and item[0] == item[-1] and item[0] in "'\"":
                item = item[1:-1]
            (pats if section == "patterns" else stops).append(item)
    return pats, stops


def _load_identifier_rules() -> tuple:
    """System A 설정에서 patterns/stopwords 를 읽는다. 못 읽으면 멈춘다. (#23 리뷰)"""
    try:
        text = IDENTIFIER_CONFIG.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            f"[오류] {IDENTIFIER_CONFIG} 를 읽지 못했습니다 ({exc}).\n"
            "       A 와 같은 규칙으로 식별자를 세야 하므로 폴백으로 넘기지 않습니다."
        )
    pats = stops = None
    try:
        import yaml  # type: ignore
        cfg = yaml.safe_load(text) or {}
        ident = cfg.get("identifiers") or {}
        pats = list(ident.get("patterns") or [])
        stops = list(ident.get("stopwords") or [])
    except ImportError:
        pats, stops = _parse_identifiers_block(text)   # pyyaml 없는 환경
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"[오류] {IDENTIFIER_CONFIG} 파싱 실패 ({exc}).")
    if not pats:
        raise SystemExit(
            f"[오류] {IDENTIFIER_CONFIG} 의 identifiers.patterns 가 비어 있습니다."
        )
    return pats, stops


IDENTIFIER_PATTERNS, IDENTIFIER_STOPWORDS = _load_identifier_rules()


def _extract_identifiers(text: str) -> list:
    stop = set(IDENTIFIER_STOPWORDS)
    found: list = []
    seen: set = set()
    for pat in IDENTIFIER_PATTERNS:
        for m in re.finditer(pat, text or "", re.ASCII):
            tok = m.group(0)
            if tok in stop or tok in seen:
                continue
            seen.add(tok)
            found.append(tok)
    return sorted(found)   # 공용 helper 와 같은 순서


def _build_citations(result: dict, wiki_root: str) -> list:
    """cited_pages를 공용 Citation 형식으로 옮긴다. (#23 3절)

    RAG의 chunk_id 자리에 위키 페이지 ID가, source_path에 그 페이지 파일이 들어간다.
    재순위 단계가 없으므로 rerank_score는 None.
    """
    root = wiki_root.rstrip("/")
    return [
        {
            "chunk_id": pid,
            "source_path": f"{root}/{pid}.md",
            "rerank_score": None,
        }
        for pid in (result.get("cited_pages") or [])
    ]


def _to_answer_record(
    q: dict,
    result: dict,
    *,
    model: str,
    run: int,
    wiki_label: str,
    wiki_build: str,
    wiki_root: str,
    questions_sha256: str,
    agent_commit: str,
    trace_path: str,
    elapsed_ms: int,
    status: str,
    error: str | None,
    corpus_meta: dict,
    cfg_hash: str,
    attempt_id: str,
) -> dict:
    tu = result.get("token_usage", {})
    prompt = tu.get("prompt_tokens")
    cache_read = tu.get("cache_read")
    cache_write = tu.get("cache_write")
    output = tu.get("output_tokens")

    # 공용 TokenUsage 스키마는 네 칸 모두 int(기본 0)이므로 None은 0으로 통일한다.
    prompt = prompt or 0
    cache_read = cache_read or 0
    cache_write = cache_write or 0
    output = output or 0
    # prompt는 모든 provider에서 캐시 포함 전체 입력이므로 읽기·쓰기를 모두 뺀다.
    uncached_input = max(0, prompt - cache_read - cache_write)

    answer = result.get("answer", "")
    abstained = ABSTAIN_TEXT in answer

    return {
        # ---- v0.3 기존 필드 (변경 금지) ----
        "schema_version": SCHEMA_VERSION,
        "qid": q["query_id"],
        "model": model,
        "run": run,
        "system": "wiki",
        "query_mode": "simple",
        "question": q["question"],
        "answer": answer,
        "citations": _build_citations(result, wiki_root),
        "retrieved": {
            "bm25": [],
            "vector": [],
            "fused": [],
            "reranked": [],
            "wiki_pages": result.get("retrieved", {}).get("wiki_pages", []),
        },
        "identifiers_in_answer": _extract_identifiers(answer),
        "latency_ms": {
            "retrieve": 0,
            "rerank": 0,
            "generate": 0,
            "total": elapsed_ms,
        },
        "tokens": {
            "uncached_input": uncached_input,
            "cache_creation": cache_write,
            "cache_read": cache_read,
            "output": output,
        },
        "corpus_commit": CORPUS_COMMIT,
        "corpus_phase": CORPUS_PHASE,
        "corpus_snapshot": corpus_meta.get("corpus_snapshot"),
        "corpus_version": corpus_meta.get("corpus_version"),
        "config_hash": cfg_hash,
        "error": error,
        # ---- v0.3 추가 필드 (system-c 전용) ----
        "cited_pages": result.get("cited_pages", []),
        "turns": result.get("turns", 0),
        "wiki_build": wiki_build,
        "wiki_label": wiki_label,
        "attempt_id": attempt_id,
        "wiki_corpus_source": corpus_meta.get("wiki_corpus_source"),
        "wiki_corpus_snapshot": corpus_meta.get("wiki_corpus_snapshot"),
        # 실제로 전송된 경우에만 라벨을 남긴다 (전송 안 됐는데 low로 기록되는 것 방지)
        "reasoning_effort": REASONING_EFFORT_LABEL if result.get("reasoning_applied") else None,
        "reasoning_config": result.get("reasoning_config_sent"),
        "reasoning_applied": result.get("reasoning_applied", False),
        "abstained": abstained,
        "status": status,
        "trace_path": trace_path,
        "wiki_pages_evidence": result.get("page_evidence", []),
        "questions_sha256": questions_sha256,
        "agent_commit": agent_commit,
    }


# ---------------------------------------------------------------------------
# 배치 실행
# ---------------------------------------------------------------------------

def run_batch(
    models_list: list[str],
    questions_path: str,
    wiki_root: str,
    wiki_label: str,
    run: int,
    run_label: str,
    max_turns: int,
    verbose: bool,
    limit: int | None,
    allow_corpus_mismatch: bool = False,
    allow_config_change: bool = False,
) -> None:
    # ---- 프리플라이트: 위키 출처 확인 (폴더를 만들기 전에 막는다) ----
    _corpus_meta_pre = _read_corpus_meta()
    wiki_provenance = check_wiki_provenance(
        Path(wiki_root), EXPECTED_CORPUS_SOURCE,
        _corpus_meta_pre.get("corpus_snapshot"), allow_corpus_mismatch
    )

    # ---- 출력 디렉토리 구조 ----
    base_dir = Path("results") / "raw" / run_label / "system_c"
    run_dir = base_dir / "runs" / f"{wiki_label}_run{run}"
    partial_dir = run_dir / ".partial"
    for d in [base_dir, run_dir, partial_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # ---- 메타데이터 수집 ----
    questions_sha256 = _file_sha256(questions_path)
    wiki_build = _get_wiki_build(Path(wiki_root))
    agent_commit = _git_short_head()
    corpus_meta = {
        **_corpus_meta_pre,
        "wiki_corpus_source": wiki_provenance["corpus_source"],
        "wiki_corpus_snapshot": wiki_provenance["corpus_snapshot"],
    }

    # ---- 질문 로드 ----
    questions: list[dict] = []
    with open(questions_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    if limit:
        questions = questions[:limit]

    # ---- trace 경로 (run_dir 기준 상대 경로) ----
    invocations_path = run_dir / "invocations.jsonl"
    failed_attempts_path = run_dir / "failed_attempts.jsonl"
    # trace_path는 results/raw/<run_label>/ 기준
    trace_path_rel = str(
        (run_dir / "invocations.jsonl").relative_to(Path("results") / "raw" / run_label)
    )

    # ---- models.json 로드 (사본은 이어하기 검사를 통과한 뒤에 쓴다) ----
    models_db = _load_models()

    # ---- kimi-k3 먼저 ----
    ordered_models = _sort_models_kimi_first(models_list)

    # ---- config_hash ----
    # 나눠 돌려도 같은 해시가 나와야 한다. 그래서 "이번에 고른 모델"이 아니라
    # models.json 전체를 넣는다. 예전에는 DeepSeek만 따로 돌리면 해시가 달라져
    # 검증기의 단일 해시 검사에서 떨어지고 이어하기가 exit 3 으로 멈췄다. (#23 리뷰)
    # run_label 도 뺀다 — 같은 조건인데 폴더 이름만 달라도 해시가 바뀌면
    # 나눠 돌린 결과를 합칠 수 없다.
    cfg = {
        "wiki_root": wiki_root,
        "wiki_label": wiki_label,
        "wiki_build": wiki_build,
        # 위키 본문도 넣는다. 같은 컴파일러로 다시 만든 위키의 행이 섞이는 것을 막는다.
        "wiki_pages_sha256": _wiki_pages_digest(Path(wiki_root)),
        "max_turns": max_turns,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "system_prompt_sha256": hashlib.sha256(
            _build_system_prompt().encode("utf-8")
        ).hexdigest(),
        "abstain_phrase": ABSTAIN_PHRASE,
        "tool_defs_sha256": _tool_defs_digest(),
        "identifier_rules": {"patterns": list(IDENTIFIER_PATTERNS),
                             "stopwords": list(IDENTIFIER_STOPWORDS)},
        "models": models_db,
    }
    cfg_hash = _config_hash(cfg)

    # 이번 실행을 구분하는 값. invocations 줄과 레코드에 함께 적어, 같은 폴더에
    # 다시 돌렸을 때 이전 시도의 호출 기록과 섞이지 않게 한다. (#23 리뷰)
    started_at = datetime.now(timezone.utc).isoformat()
    attempt_id = hashlib.sha256(
        f"{cfg_hash}|{run_label}|{run}|{started_at}".encode("utf-8")
    ).hexdigest()[:12]
    print(f"[실행] config_hash={cfg_hash} attempt_id={attempt_id}", file=sys.stderr)

    # ---- 첫 API 호출 전에 전 모델 이어하기 검사 ----
    resume_plan = preflight_resume(
        partial_dir, ordered_models, cfg_hash, failed_attempts_path, allow_config_change,
        scope_qids={q["query_id"] for q in questions},
    )

    # ---- models.json 스냅샷 저장 ----
    # 이어하기 검사가 exit 3 으로 멈추면 기존 사본을 덮어쓰지 않도록 검사 뒤로 옮겼다. (#27 3차 리뷰)
    (run_dir / "models.json").write_text(
        json.dumps(models_db, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary_models: dict[str, dict] = {}

    # invocations / failed_attempts 파일 열기 (append 모드)
    _ensure_trailing_newline(invocations_path)
    _ensure_trailing_newline(failed_attempts_path)
    inv_f = open(invocations_path, "a", encoding="utf-8")
    fail_f = open(failed_attempts_path, "a", encoding="utf-8")

    try:
        for model_name in ordered_models:
            partial_path = partial_dir / f"{model_name}.jsonl"
            done = resume_plan.get(model_name, set())   # 선행 검사 결과 (#23 리뷰)

            ok = err = abstained_count = 0
            model_start = time.time()

            print(
                f"\n[모델 시작] {model_name} ({len(questions)}문항 중 {len(done)}개 기존)",
                file=sys.stderr,
            )

            _ensure_trailing_newline(partial_path)
            with open(partial_path, "a", encoding="utf-8") as out_f:
                for i, q in enumerate(questions, 1):
                    qid = q["query_id"]
                    if (qid, model_name, run) in done:
                        print(f"  [건너뜀] {qid}", file=sys.stderr)
                        continue

                    print(
                        f"  [{i}/{len(questions)}] {qid} ...",
                        end=" ", flush=True, file=sys.stderr,
                    )
                    t0 = time.time()
                    reset_interval_wait()
                    error = None
                    result: dict = {}
                    q_status = "ok"

                    try:
                        result = run_agent(
                            query=q["question"],
                            max_turns=max_turns,
                            verbose=verbose,
                            model=model_name,
                            wiki_root=wiki_root,
                        )
                        q_status = result.get("status", "ok")
                        # 잘림·거절·호출 실패로 status=error 가 돌아오면 사유도 함께 남긴다.
                        if q_status == "error" and result.get("error"):
                            error = result["error"]
                            print(f"ERR({error[:60]})", file=sys.stderr)
                    except Exception as e:
                        q_status = "error"
                        error = redact(f"{e.__class__.__name__}: {e}")
                        print(f"ERR({error[:60]})", file=sys.stderr)
                        # 재시도 기록뿐 아니라 최종 실패도 남긴다. (#23 3절)
                        result.setdefault("failed_attempts", []).append({
                            "attempt": "final",
                            "error": error[:500],
                            "wait_s": 0,
                            "ts": time.time(),
                        })

                    # Kimi 호출 간격 대기(min_interval_s)는 A·B처럼 지연에서 제외한다
                    elapsed_ms = int((time.time() - t0 - get_interval_wait_s()) * 1000)

                    record = _to_answer_record(
                        q, result,
                        model=model_name,
                        run=run,
                        wiki_label=wiki_label,
                        wiki_build=wiki_build,
                        wiki_root=wiki_root,
                        questions_sha256=questions_sha256,
                        agent_commit=agent_commit,
                        trace_path=trace_path_rel,
                        elapsed_ms=elapsed_ms,
                        status=q_status if not error else "error",
                        error=error,
                        corpus_meta=corpus_meta,
                        cfg_hash=cfg_hash,
                        attempt_id=attempt_id,
                    )

                    # append to partial
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out_f.flush()

                    # invocations.jsonl: 턴별 1줄
                    for td in result.get("turn_details", []):
                        inv_line = {
                            "attempt_id": attempt_id,
                            "qid": qid,
                            "model": model_name,
                            "run": run,
                            "turn": td["turn"],
                            "tool_calls": [c["tool"] for c in td.get("calls", [])],
                            "arguments": [c["args"] for c in td.get("calls", [])],
                            "result_len": [c["result_len"] for c in td.get("calls", [])],
                            "sha256": [c["sha256"] for c in td.get("calls", [])],
                            "prompt_tokens": td.get("prompt_tokens"),
                            "cache_read": td.get("cache_read"),
                            "cache_write": td.get("cache_write"),
                            "output_tokens": td.get("output_tokens"),
                            "finish_reason": td.get("finish_reason"),
                            "usage_raw": td.get("usage_raw"),
                        }
                        inv_f.write(json.dumps(inv_line, ensure_ascii=False) + "\n")
                    inv_f.flush()

                    # failed_attempts.jsonl
                    for fa in result.get("failed_attempts", []):
                        fa_line = {"qid": qid, "model": model_name, "run": run, **fa}
                        fail_f.write(json.dumps(fa_line, ensure_ascii=False) + "\n")
                    fail_f.flush()

                    if error:
                        err += 1
                    else:
                        ok += 1
                        if record.get("abstained"):
                            abstained_count += 1

                    status_str = "OK" if not error else f"ERR"
                    tok = record["tokens"]
                    print(
                        f"{status_str} turns={record['turns']} "
                        f"({elapsed_ms/1000:.1f}s)",
                        file=sys.stderr,
                    )

            model_elapsed = time.time() - model_start
            summary_models[model_name] = {
                "ok": ok, "err": err, "abstained": abstained_count,
                "elapsed_s": round(model_elapsed, 1),
            }
            print(
                f"[모델 완료] {model_name}: ok={ok} err={err} abstained={abstained_count} "
                f"({model_elapsed:.0f}s)",
                file=sys.stderr,
            )

    finally:
        inv_f.close()
        fail_f.close()

    # ---- answers.jsonl 갱신: 업서트 ----
    # .partial/ 은 .gitignore 대상이다. 그래서 "partial만 모아 새로 쓰기"를 하면
    # 클론받은 곳에서 한 모델만 재실행할 때 커밋돼 있던 다른 모델 줄이 전부 사라진다.
    # 기존 answers.jsonl을 읽어두고 (qid, model, run) 단위로 이번 결과만 갈아끼운다. (#23 3절)
    answers_path = base_dir / "answers.jsonl"
    merged, kept, replaced, added = _upsert_answers(answers_path, partial_dir)
    print(
        f"[병합] {answers_path} — 총 {merged}줄 "
        f"(유지 {kept} / 교체 {replaced} / 신규 {added})",
        file=sys.stderr,
    )

    finished_at = datetime.now(timezone.utc).isoformat()

    # ---- summary 통계: partial 파일에서 키마다 마지막 행으로 재집계 (재개 실행 포함) ----
    # 줄을 모두 세면 다시 돌려 성공한 행과 이전 오류 행이 둘 다 세지고, 끊긴 마지막 줄 하나로
    # 배치 전체가 마지막에 실패했다. answers.jsonl 과 같은 키로 최신 행만 센다. (#27 동수님 리뷰 P1-2)
    final_results: dict[str, dict] = {}
    for model_name in ordered_models:
        partial_path = partial_dir / f"{model_name}.jsonl"
        if partial_path.exists():
            records = list(_latest_rows(partial_path, _record_key).values())
            final_results[model_name] = {
                "ok": sum(1 for r in records if not r.get("error")),
                "err": sum(1 for r in records if r.get("error")),
                "abstained": sum(1 for r in records if r.get("abstained")),
                "elapsed_s": summary_models.get(model_name, {}).get("elapsed_s", 0),
            }
        else:
            final_results[model_name] = summary_models.get(
                model_name, {"ok": 0, "err": 0, "abstained": 0, "elapsed_s": 0}
            )

    # ---- summary.json ----
    summary = {
        "run_label": run_label,
        "wiki_label": wiki_label,
        "wiki_build": wiki_build,
        "wiki_root": wiki_root,
        "ssot_commit": CORPUS_COMMIT,
        "corpus_snapshot": corpus_meta.get("corpus_snapshot"),
        "corpus_version": corpus_meta.get("corpus_version"),
        "wiki_corpus_source": corpus_meta.get("wiki_corpus_source"),
        "wiki_corpus_snapshot": corpus_meta.get("wiki_corpus_snapshot"),
        "questions_sha256": questions_sha256,
        "reasoning_effort": REASONING_EFFORT_LABEL,
        "models": ordered_models,
        "results": final_results,
        "agent_commit": agent_commit,
        "started_at": started_at,
        "finished_at": finished_at,
        "total_records": merged,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- README.md ----
    _write_readme(base_dir, summary, models_db)

    print(
        f"\n[배치 완료] {merged}줄 → {answers_path}\n"
        f"  summary: {run_dir / 'summary.json'}",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# README.md 자동 생성
# ---------------------------------------------------------------------------

def _write_readme(base_dir: Path, summary: dict, models_db: dict) -> None:
    lines = [
        f"# System C — LLM Wiki · {summary['run_label']}",
        "",
        "`answers.jsonl`이 채점 대상입니다. 한 줄이 (qid, model, run) 하나입니다.",
        "",
        "## 실행 조건",
        f"- 위키: `{summary['wiki_root']}` (compiled_by: {summary['wiki_build']})",
        f"- SSOT: `{summary['ssot_commit']}`",
        f"- 코퍼스: `{summary['corpus_version']}` `{summary['corpus_snapshot']}`",
        f"- 질문셋 SHA-256: `{summary['questions_sha256']}`",
        f"- 코드 커밋: `{summary['agent_commit']}`",
        f"- 추론 강도: {summary['reasoning_effort']} (effort=low)",
        f"- 출력 상한: max_tokens=16000",
        f"- temperature: 보내지 않음",
        "",
        "## 참가자 모델",
        "",
        "| 모델 | provider | reasoning_applied | 비고 |",
        "| --- | --- | --- | --- |",
    ]
    for m in summary["models"]:
        cfg = models_db.get(m, {})
        provider = cfg.get("provider", "?")
        has_reason = bool(cfg.get("reasoning_config"))
        note = ""
        if m == "deepseek-flash":
            note = "DeepSeek-V4.1-Flash (V4 Flash, 9/10 교체)"
        elif m == "kimi-k3":
            note = f"RPM 3/min → min_interval_s={cfg.get('min_interval_s', '?')}"
        lines.append(f"| {m} | {provider} | {has_reason} | {note} |")

    lines += [
        "",
        "## 결과",
        "",
        "| 모델 | ok | err | abstained |",
        "| --- | --- | --- | --- |",
    ]
    for m, r in summary.get("results", {}).items():
        lines.append(f"| {m} | {r['ok']} | {r['err']} | {r['abstained']} |")

    lines += [
        "",
        f"시작: {summary['started_at']}  완료: {summary['finished_at']}",
    ]

    (base_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    _safe_console()
    parser = argparse.ArgumentParser(description="LLM Wiki 배치 평가 러너")
    parser.add_argument(
        "--models", default="all",
        help="쉼표 구분 모델 목록 또는 'all' (models.json 기준)"
    )
    parser.add_argument(
        "--wiki-root", default="systems/system_c_llm_wiki/wiki",
        help="위키 루트 디렉토리"
    )
    parser.add_argument(
        "--wiki-label", default="",
        help="위키 레이블 (예: astra)"
    )
    parser.add_argument(
        "--run", type=int, default=1,
        help="실행 회차 (기본 1)"
    )
    parser.add_argument(
        "--run-label", required=True,
        help="출력 상위 폴더 이름. 필수 — 기본값을 두면 새 실행이 기존 결과 폴더에 섞인다 (#23 3절)"
    )
    parser.add_argument(
        "--questions", default="benchmark/questions_v1.jsonl",
        help="질문셋 JSONL"
    )
    parser.add_argument(
        "--max-turns", type=int, default=30,
        help="에이전트 최대 턴 수 (기본 30)"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="테스트용: 첫 N문항만"
    )
    parser.add_argument(
        "--allow-corpus-mismatch", action="store_true",
        help="위키가 지정 코퍼스로 컴파일된 게 아니어도 강행 (#23 1-4)"
    )
    parser.add_argument(
        "--allow-config-change", action="store_true",
        help="기존 partial 과 config_hash 가 달라도 이어서 실행 (#23 3절)"
    )
    args = parser.parse_args()

    # 모델 목록 결정
    all_models = list(_load_models().keys())
    if args.models.strip().lower() == "all":
        models_list = all_models
    else:
        models_list = [m.strip() for m in args.models.split(",") if m.strip()]
        unknown = [m for m in models_list if m not in all_models]
        if unknown:
            print(f"[오류] models.json에 없는 모델: {unknown}", file=sys.stderr)
            sys.exit(1)

    wiki_label = args.wiki_label or Path(args.wiki_root).name

    run_batch(
        models_list=models_list,
        questions_path=args.questions,
        wiki_root=args.wiki_root,
        wiki_label=wiki_label,
        run=args.run,
        run_label=args.run_label,
        max_turns=args.max_turns,
        verbose=args.verbose,
        limit=args.limit,
        allow_corpus_mismatch=args.allow_corpus_mismatch,
        allow_config_change=args.allow_config_change,
    )


if __name__ == "__main__":
    main()
