\
# -*- coding: utf-8 -*-
"""
LLM Wiki 컴파일러 (System C) — v2
==================================

v1과 다른 점: corpus/metadata/scope.json 을 실시간으로 읽어서, 원본 파일들을
"엔티티"(클러스터 / 디바이스타입 / 공유 베이스) 단위로 그룹핑한 다음, 한
엔티티에 속한 spec/sdk/구현/문서 파일들을 다 모아서 "페이지 1개"로 컴파일한다.
(v1은 파일 하나=페이지 하나로 짜여있어서, 클러스터 하나가 5개 파일로
흩어져 5개 페이지가 되는 문제가 있었음.)

사용법:
    python3 compile_wiki.py --dry-run     # 그룹핑 결과만 확인 (API 호출 없음, 아무것도 쓰지 않음)
    python3 compile_wiki.py               # 실제 컴파일 (먼저 <wiki_root>/wiki_manifest.json 을 쓴다)
"""

import argparse
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. 설정
# ---------------------------------------------------------------------------

MODEL_PROVIDER = os.environ.get("WIKI_COMPILER_PROVIDER", "anthropic")
MODEL_NAME = os.environ.get("WIKI_COMPILER_MODEL", "TODO-내일-확정")

# 팀 공용 입력. corpus/HANDOFF.md: "RAG와 LLM Wiki가 함께 사용하는 282개 정규화 문서".
# 원본 전문(corpus/raw)이 아니라 이 파일을 읽어야 System A/B와 입력 범위가 같아진다.
CORPUS_DOCS = Path(os.environ.get("CORPUS_DOCS", "corpus/tiers/c3/processed/documents.jsonl"))
# 코퍼스 메타데이터. 컴파일 산출물에 snapshot_id 를 박아 위키가 어느 코퍼스에서 나왔는지
# 레코드와 대조할 수 있게 한다. (#23 1-4)
# 실제로 읽은 documents.jsonl 줄에서 채운다. load_documents() 가 설정한다.
CORPUS_SNAPSHOT_ID: str | None = None
# 실제로 읽은 documents.jsonl 파일 바이트의 sha256. load_documents() 가 설정한다.
# snapshot_id 는 라벨이라 본문이 달라도 같을 수 있다. A 가 색인한 파일과 같은지는
# 이 값으로만 대조할 수 있다. (#27 A 기준 점검)
CORPUS_DOCS_SHA256: str | None = None
# 위키 전체의 명세. 그룹핑 직후, 엔티티를 컴파일하기 전에 쓴다. run_batch 는 여기 적힌
# 페이지가 전부 있는지와 입력 sha256 을 보고 실행 여부를 정한다. (#27 A 기준 점검)
MANIFEST_NAME = "wiki_manifest.json"
MANIFEST_SCHEMA = 1
# 호출 단위 과금 기록. create() 가 돌아오는 즉시 한 줄씩 덧붙인다.
BUILD_CALLS_NAME = "build_calls.jsonl"
TOKEN_COLUMNS = ("uncached_input", "cache_creation", "cache_read", "output")

# 엔드포인트는 코드에 박는다. base_url 을 생략하면 SDK가 OPENAI_BASE_URL /
# ANTHROPIC_BASE_URL 환경변수를 읽어버려, 어느 엔드포인트로 컴파일한 위키인지
# 재현할 수 없다. 인자를 빼는 것은 고정이 아니라 환경변수 지배 허용이다. (#23 2절)
PROVIDER_BASE_URL = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com",
}
SCOPE_JSON = Path("corpus/metadata/scope.json")
# 기본 출력 위치. --wiki-root 로 바꿔서 여러 벌의 위키를 나란히 만들 수 있다
# (컴파일 모델별 비교 실험용).
WIKI_ROOT = Path(os.environ.get("WIKI_ROOT", "systems/system_c_llm_wiki/wiki"))

# 코드가 공유되는데 scope.json만 봐서는 자동으로 못 찾아내는 2개 예외.
# (mode-base-server, alarm-base-server 폴더는 특정 클러스터가 아니라
#  "ModeBase"/"AlarmBase"라는 공유 베이스 구현이라서 따로 지정해줌)
SHARED_IMPL_DIR_TO_BASE = {
    "src/app/clusters/mode-base-server": "ModeBase",
    "src/app/clusters/alarm-base-server": "AlarmBase",
}

# zzz_generated 밑 폴더명 -> 클러스터 이름 (scope.json generated_metadata_policy 참고)
GENERATED_DIR_TO_CLUSTER = {
    "HepaFilterMonitoring": "HEPA Filter Monitoring",
    "ActivatedCarbonFilterMonitoring": "Activated Carbon Filter Monitoring",
    "RelativeHumidityMeasurement": "Relative Humidity Measurement",
}

# cluster_base 관련 파일들의 stem이 제각각이라(ModeBase / mode-base-cluster 등)
# 같은 개체로 안 묶이는 문제를 막기 위한 정규화 테이블
CLUSTER_BASE_CANONICAL_NAME = {
    "ModeBase": "ModeBase",
    "AlarmBase": "AlarmBase",
    "Label-Cluster": "Label",
    "mode-base-cluster": "ModeBase",
    "alarm-base-cluster": "AlarmBase",
}

# 완전히 무시할 파일 (진짜 데이터가 아님)
SKIP_NAMES = {".DS_Store"}


# ---------------------------------------------------------------------------
# 1. LLM 호출 추상화 (v1과 동일 — 내일 모델 확정되면 여기만 채우면 됨)
# ---------------------------------------------------------------------------

# API가 "지금 잠깐 과부하야, 나중에 다시 해봐" 같은 일시적인 에러를 낼 때
# (503 UNAVAILABLE, 429 rate limit 등) 자동으로 몇 초 쉬었다가 재시도.
# 이런 에러는 우리 코드 문제가 아니라 서버 쪽 일시적인 상태라 재시도하면 대부분 풀림.
_TRANSIENT_ERROR_HINTS = (
    "503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "rate limit", "overloaded",
    # 큰 엔티티(수만 토큰 입력)에서 자주 나는 오류들. 재시도하면 대부분 성공한다.
    "timeout", "timed out", "APITimeout", "APIConnection", "Connection error",
    "502", "504", "Internal Server Error",
)


def _call_with_retries(fn, tries: int = 2, base_delay: int = 8, what: str = "API"):
    last_err = None
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            last_err = e
            is_transient = any(hint.lower() in str(e).lower() for hint in _TRANSIENT_ERROR_HINTS)
            if attempt == tries or not is_transient:
                raise
            delay = base_delay * attempt
            print(f"  [재시도 {attempt}/{tries - 1}] {what} 일시적 오류({e.__class__.__name__}) "
                  f"-> {delay}초 후 다시 시도...")
            time.sleep(delay)
    raise last_err  # 여기 도달하면 안 되지만 안전망


def _usage_raw(usage) -> dict | None:
    """SDK usage 객체를 그대로 dict 로 남긴다. (#23 1-3)

    4열로 접은 값만 남기면 나중에 "어디서 잘못 읽었나"를 되짚을 수 없다.
    실제로 cache_write 를 최상위에서 읽던 버그를 이 원본 없이는 사후 확인할 수 없었다.
    """
    if usage is None:
        return None
    for attr in ("model_dump", "to_dict", "dict"):
        fn = getattr(usage, attr, None)
        if callable(fn):
            try:
                return json.loads(json.dumps(fn(), default=str))
            except Exception:  # noqa: BLE001
                pass
    try:
        return json.loads(json.dumps(vars(usage), default=str))
    except Exception:  # noqa: BLE001
        return {"repr": str(usage)}


class TruncatedResponse(RuntimeError):
    """출력 상한·차단·거절로 본문이 온전하지 않은 응답. 페이지로 저장하지 않는다."""


def _max_output_tokens() -> int:
    """Anthropic max_tokens. 4096은 큰 엔티티에서 잘린 페이지를 만든다. (#23 리뷰)"""
    return int(os.environ.get("WIKI_COMPILER_MAX_TOKENS", "16000"))


def build_calls_path() -> Path:
    return WIKI_ROOT / BUILD_CALLS_NAME


def record_build_call(entity_key: str, attempt: int, cols: dict) -> None:
    """API 호출 하나를 즉시 기록한다. (#23 리뷰)

    create() 가 돌아온 호출은 이미 과금됐다. 페이지 저장 실패, --force 재컴파일,
    중간 Ctrl-C 로 이 기록이 사라지면 실제로 쓴 돈이 장부에서 빠진다.
    그래서 집계 파일(build_tokens.json)이 아니라 append-only 원장에 먼저 적는다.
    """
    path = build_calls_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "entity": entity_key,
        "attempt": attempt,
        "compiled_by": f"{MODEL_PROVIDER}/{MODEL_NAME}",
        **{c: cols.get(c) for c in TOKEN_COLUMNS},
        "api_shape": cols.get("api_shape"),
        "usage_raw": cols.get("usage_raw"),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def aggregate_build_calls(lines: list) -> tuple:
    """원장 줄들 → (합계 4열, 엔티티별 시도 수). 모든 시도를 더한다.

    --force 재컴파일도 과금되므로 시도를 덮어쓰지 않고 전부 더한다. (#23 리뷰)
    """
    totals = {c: 0 for c in TOKEN_COLUMNS}
    per_entity: dict = {}
    for d in lines:
        for c in TOKEN_COLUMNS:
            v = d.get(c)
            if isinstance(v, int):
                totals[c] += v
        e = per_entity.setdefault(d.get("entity"), {"attempts": 0,
                                                   **{c: 0 for c in TOKEN_COLUMNS}})
        e["attempts"] += 1
        for c in TOKEN_COLUMNS:
            v = d.get(c)
            if isinstance(v, int):
                e[c] += v
    return totals, per_entity


def write_build_tokens(ssot_commit: str) -> dict:
    """원장에서 집계해 build_tokens.json 을 원자적으로 쓴다."""
    ledger = build_calls_path()
    lines = []
    if ledger.exists():
        for i, raw in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                # 조용히 넘기면 과금분이 장부에서 빠진다. 멈추고 사람이 보게 한다.
                raise SystemExit(
                    f"[오류] {ledger}:{i} 를 읽을 수 없습니다 ({exc}). "
                    "이 줄도 과금된 호출이므로 임의로 버리지 않습니다."
                )
    totals, per_entity = aggregate_build_calls(lines)
    out = {
        "wiki_root": WIKI_ROOT.as_posix(),
        "compiled_by": f"{MODEL_PROVIDER}/{MODEL_NAME}",
        "corpus_source": CORPUS_DOCS.as_posix(),
        "corpus_snapshot": CORPUS_SNAPSHOT_ID,
        "ssot_commit": ssot_commit,
        "ledger": ledger.name,
        "calls": len(lines),
        "columns": list(TOKEN_COLUMNS),
        "note": ("A·B 와 같은 4열이다. uncached_input 은 캐시를 제외한 입력이므로 "
                 "provider 사이에 의미가 같다. 그래도 합산하지 말 것."),
        "totals": totals,
        "per_entity": per_entity,
    }
    tmp = WIKI_ROOT / "build_tokens.json.tmp"
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, WIKI_ROOT / "build_tokens.json")
    return out


def _count_prior_attempts() -> dict:
    """원장에서 엔티티별 기존 시도 수를 센다. 시도 번호를 이어 붙이기 위함."""
    path = build_calls_path()
    counts: dict = {}
    if not path.exists():
        return counts
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        counts[d.get("entity")] = counts.get(d.get("entity"), 0) + 1
    return counts


def call_llm(system_prompt: str, user_prompt: str, provider: str = None, model: str = None,
             entity_key: str = "-", attempt: int = 1):
    """(본문, 토큰 4열 dict)을 돌려준다. 위키 구축 비용을 기록하기 위함. (#23 3절)"""
    provider = provider or MODEL_PROVIDER
    model = model or MODEL_NAME

    if provider == "anthropic":
        import anthropic  # pip install anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("환경변수 ANTHROPIC_API_KEY 가 설정되어 있지 않음")
        client = anthropic.Anthropic(
            api_key=api_key, base_url=PROVIDER_BASE_URL["anthropic"])
        resp = _call_with_retries(
            lambda: client.messages.create(
                model=model,
                max_tokens=_max_output_tokens(),
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ),
            what="Anthropic API",
        )
        u = getattr(resp, "usage", None)
        cols = {
            # Anthropic input_tokens 는 캐시를 제외한 값이라 그대로 uncached_input 이다.
            "uncached_input": getattr(u, "input_tokens", None),
            "cache_creation": getattr(u, "cache_creation_input_tokens", None),
            "cache_read": getattr(u, "cache_read_input_tokens", None),
            "output": getattr(u, "output_tokens", None),
            "api_shape": "anthropic_messages",
            "usage_raw": _usage_raw(u),
        }
        record_build_call(entity_key, attempt, cols)   # 과금됐으니 먼저 적는다
        stop = getattr(resp, "stop_reason", None)
        if stop in ("max_tokens", "refusal"):
            raise TruncatedResponse(
                f"Anthropic stop_reason={stop} — 잘린/거절된 본문을 페이지로 저장하지 않습니다.")
        return resp.content[0].text, cols
    elif provider == "openai":
        from openai import OpenAI  # pip install openai
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("환경변수 OPENAI_API_KEY 가 설정되어 있지 않음")
        # 큰 엔티티는 입력이 수만 토큰이라 기본 타임아웃으로는 부족하다.
        timeout_s = float(os.environ.get("WIKI_COMPILER_TIMEOUT", "600"))
        client = OpenAI(
            api_key=api_key,
            base_url=PROVIDER_BASE_URL["openai"],   # 생략하면 env가 이긴다
            timeout=timeout_s,
            max_retries=3,
        )
        resp = _call_with_retries(
            lambda: client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            ),
            what="OpenAI API",
        )
        u = getattr(resp, "usage", None)
        det = getattr(u, "prompt_tokens_details", None) if u else None
        # 캐시 쓰기는 prompt_tokens_details 안에 있다. 최상위 usage 에서 읽으면
        # 항상 None 이 되어 캐시 쓰기 비용이 통째로 사라진다. (#23 1-3)
        cache_write = getattr(det, "cache_write_tokens", None) if det else None
        if cache_write is None:
            cache_write = getattr(u, "cache_write_tokens", None)   # 일부 게이트웨이 대비
        cache_read = getattr(det, "cached_tokens", None) if det else None
        prompt = getattr(u, "prompt_tokens", None)
        # OpenAI prompt_tokens 는 캐시를 포함한다. A 와 같은 4열로 만들려면 빼야 한다.
        uncached = (max(0, prompt - (cache_read or 0) - (cache_write or 0))
                    if isinstance(prompt, int) else None)
        cols = {
            "uncached_input": uncached,
            "cache_creation": cache_write,
            "cache_read": cache_read,
            "output": getattr(u, "completion_tokens", None),
            "api_shape": "openai_chat",
            "usage_raw": _usage_raw(u),
        }
        record_build_call(entity_key, attempt, cols)
        choice = (resp.choices or [None])[0]
        fr = getattr(choice, "finish_reason", None) if choice else None
        if fr in ("length", "content_filter"):
            raise TruncatedResponse(
                f"OpenAI finish_reason={fr} — 잘린/차단된 본문을 페이지로 저장하지 않습니다.")
        return choice.message.content, cols
    elif provider == "google":
        # 주의: google-generativeai(구 SDK)는 2026년에 지원 종료됨.
        # 새 SDK인 google-genai 를 써야 함: pip install -U google-genai
        from google import genai
        from google.genai import types
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("환경변수 GOOGLE_API_KEY 가 설정되어 있지 않음")
        client = genai.Client(api_key=api_key)
        resp = _call_with_retries(
            lambda: client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            ),
            what="Gemini API",
        )
        um = getattr(resp, "usage_metadata", None)
        prompt = getattr(um, "prompt_token_count", None) if um else None
        cached = getattr(um, "cached_content_token_count", None) if um else None
        cols = {
            "uncached_input": (max(0, prompt - (cached or 0))
                               if isinstance(prompt, int) else None),
            "cache_creation": None,       # Gemini 는 캐시 쓰기를 응답에 주지 않는다
            "cache_read": cached,
            "output": getattr(um, "candidates_token_count", None) if um else None,
            "api_shape": "google_genai",
            "usage_raw": _usage_raw(um),
        }
        record_build_call(entity_key, attempt, cols)
        return resp.text, cols
    else:
        raise ValueError(f"알 수 없는 provider: {provider}")


SYSTEM_PROMPT = """\
당신은 Matter(connectedhomeip) 기술 문서를 구조화된 Markdown 위키 페이지로 \
변환하는 전문 컴파일러입니다.

규칙:
1. 원문에 등장하는 모든 식별자(클러스터 ID 예: 0x0006, 속성/명령/이벤트 이름 \
   예: OnOff, LevelControl, 함수명, 파일 경로)는 절대 번역하거나 바꾸지 말고 \
   원문 그대로 복사하십시오.
2. 입력은 "역할(spec/sdk/impl/doc/example)"이 표시된 여러 조각으로 주어집니다. \
   이걸 종합해서 하나의 페이지로 만들되, 다음 섹션 구조를 따르십시오: \
   ## 개요 / ## 스펙 / ## SDK 정의 / ## 구현 / ## 예시 / ## 관련 문서 \
   (해당 역할의 입력이 없으면 그 섹션은 생략하십시오.)
3. 원문에 없는 내용을 추측해서 채우지 마십시오.
4. 마크다운 본문만 반환하십시오. 서두 인사말, 설명, 마무리 문구를 절대 \
   붙이지 마십시오.
"""


def build_user_prompt(entity_name: str, pieces: list) -> str:
    parts = [f"엔티티: {entity_name}\n"]
    for role, rel_path, text in pieces:
        parts.append(f"--- [{role}] {rel_path} ---\n{text}\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 2. scope.json 기반 레지스트리 구축
# ---------------------------------------------------------------------------


@dataclass
class Entity:
    key: str
    kind: str          # "cluster" | "device_type" | "base" | "example" | "documentation" | "misc"
    name: str
    ids: list = field(default_factory=list)
    files: list = field(default_factory=list)   # (role, rel_path, text)


def load_scope() -> dict:
    if not SCOPE_JSON.exists():
        print(f"[경고] {SCOPE_JSON} 가 없습니다.")
        return {}
    return json.loads(SCOPE_JSON.read_text(encoding="utf-8"))


def build_registry(scope: dict):
    """반환: path_to_entity(정확 경로 -> (entity_key, role)), dir_to_entity(구현 폴더 -> entity_key),
    entities(레지스트리). 역할(role)은 여기서 등록할 때 명시적으로 정해서 저장한다
    (파일명 패턴을 나중에 추측하지 않음 — 더 안전함)."""
    path_to_entity: dict = {}
    dir_to_entity: dict = {}
    entities: dict = {}
    # cluster_name -> entity_key : zzz_generated/ 밑의 파일들이 "클러스터 이름"
    # 문자열로만 식별될 때(예: ActivatedCarbonFilterMonitoring 폴더) 어떤
    # entity로 합쳐야 하는지 바로 찾기 위한 역방향 테이블.
    # entities.items()를 이름으로 되짚어 찾는 방식은, HEPA/Carbon Filter처럼
    # 여러 클러스터가 같은 entity(같은 specification_path)로 이미 합쳐진 경우
    # 그 entity.name이 먼저 등록된 클러스터 이름 하나로만 고정돼 있어서
    # 나중 클러스터 이름으로는 못 찾는 문제가 있었음 -> 클러스터별로 전부
    # 등록해두면 이 문제가 없어짐.
    cluster_name_to_key: dict = {}

    def get_or_create(key, kind, name):
        if key not in entities:
            entities[key] = Entity(key=key, kind=kind, name=name)
        return entities[key]

    # --- 클러스터 (spec / sdk / impl / doc) ---
    for c in scope.get("clusters", []):
        # 같은 spec/sdk/impl 경로를 공유하는 클러스터(예: HEPA/Carbon Filter)는
        # 자동으로 같은 entity_key로 묶임 (경로 자체를 key로 쓰기 때문)
        key = f"cluster:{c['specification_path']}"
        ent = get_or_create(key, "cluster", c["cluster_name"])
        if c["cluster_id"] not in ent.ids:
            ent.ids.append(c["cluster_id"])
        cluster_name_to_key[c["cluster_name"]] = key
        path_to_entity[c["specification_path"]] = (key, "spec")
        path_to_entity[c["sdk_definition_path"]] = (key, "sdk")
        if c.get("documentation_status") == "present":
            path_to_entity[c["documentation_path"]] = (key, "doc")
        # 키는 '/' 로 적는다. str() 은 Windows 에서 '\' 가 되어 SHARED_IMPL_DIR_TO_BASE
        # ('/' 표기)와 안 맞고, 공유 구현(mode-base-server 등)이 엉뚱한 클러스터로 간다. (#27 A 기준 점검)
        impl_dir = Path(c["implementation_path"]).parent.as_posix()
        if impl_dir not in SHARED_IMPL_DIR_TO_BASE:
            dir_to_entity.setdefault(impl_dir, key)

    # --- 공유 베이스 (ModeBase / AlarmBase / Label) ---
    # 주의: scope.json의 source_sets에는 definition_kind=="cluster_base"인 엔트리가
    # 2개 있을 수 있음 (예: source_role=="specification" 3개 경로 + source_role==
    # "sdk_codegen" mode-base-cluster.xml 1개). 이 둘을 "같은 베이스"로 묶으려면
    # 파일명(stem)이 제각각이어도(ModeBase vs mode-base-cluster) 정규화 테이블로
    # 같은 key를 만들어야 하고, role도 source_role을 보고 정확히 정해야 한다.
    for entry in scope.get("source_sets", []):
        if entry.get("definition_kind") == "cluster_base":
            role = "sdk" if entry.get("source_role") == "sdk_codegen" else "spec"
            for p in entry.get("paths", []):
                stem = Path(p).stem
                name = CLUSTER_BASE_CANONICAL_NAME.get(stem, stem)
                key = f"base:{name}"
                get_or_create(key, "base", name)
                path_to_entity[p] = (key, role)

    for impl_dir, base_name in SHARED_IMPL_DIR_TO_BASE.items():
        key = f"base:{base_name}"
        get_or_create(key, "base", base_name)
        dir_to_entity[impl_dir] = key

    # --- 디바이스 타입 ---
    for p in scope.get("products", []):
        key = f"device:{p['definition_path']}"
        ent = get_or_create(key, "device_type", p["name"])
        ent.ids.append(p["id"])
        path_to_entity[p["definition_path"]] = (key, "spec")

    # BaseDeviceType / RootNodeDeviceType -> 공용 base 취급
    for support_path in scope.get("support_definitions", []):
        if "device_types/BaseDeviceType.xml" in support_path or \
           "device_types/RootNodeDeviceType.xml" in support_path:
            key = "base:RootNodeAndBaseDeviceType"
            get_or_create(key, "base", "Root/Base Device Type")
            path_to_entity[support_path] = (key, "spec")
        elif support_path.endswith("matter-devices.xml"):
            key = "base:MatterDevicesRegistry"
            get_or_create(key, "base", "Matter Devices Registry (SDK)")
            path_to_entity[support_path] = (key, "sdk")

    return path_to_entity, dir_to_entity, entities, cluster_name_to_key


# ---------------------------------------------------------------------------
# 3. 원본 파일 하나를 엔티티에 배정
# ---------------------------------------------------------------------------


def classify(rel_path: Path, path_to_entity: dict, dir_to_entity: dict, entities: dict,
             cluster_name_to_key: dict):
    """반환: (entity_key, role) 또는 None(스킵)"""
    rel = rel_path.as_posix()

    if rel_path.name in SKIP_NAMES:
        return None

    if rel in path_to_entity:
        return path_to_entity[rel]

    parent = rel_path.parent.as_posix()   # dir_to_entity 키와 같은 '/' 표기 (#27 A 기준 점검)
    if parent in dir_to_entity:
        role = "doc" if rel_path.name == "README.md" else "impl"
        return dir_to_entity[parent], role

    if rel.startswith("zzz_generated/"):
        for dirname, cluster_name in GENERATED_DIR_TO_CLUSTER.items():
            if dirname in rel:
                # cluster_name_to_key로 직접 조회 (entities를 이름으로 역탐색하던
                # 방식은, HEPA/Carbon Filter처럼 여러 클러스터가 하나의 entity로
                # 합쳐진 경우 entity.name이 둘 중 하나로만 고정돼 있어서
                # 다른 쪽 클러스터 이름으로는 못 찾는 버그가 있었음)
                key = cluster_name_to_key.get(cluster_name)
                if key is not None:
                    return key, "generated"
        return "misc:generated", "generated"

    if rel.startswith("examples/"):
        return "examples:all", "example"

    if rel.startswith("docs/"):
        return "guides:all", "doc"

    return "misc:uncategorized", "misc"


# ---------------------------------------------------------------------------
# 4. 위키 경로 결정 (10단계에서 정한 구조)
# ---------------------------------------------------------------------------


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("/", "-")


def target_wiki_path(entity: Entity) -> Path:
    slug = slugify(entity.name)
    if entity.kind == "cluster":
        id_prefix = f"{entity.ids[0]}-" if entity.ids else ""
        return WIKI_ROOT / "clusters" / f"{id_prefix}{slug}.md"
    if entity.kind == "device_type":
        return WIKI_ROOT / "device-types" / f"{slug}.md"
    if entity.kind == "base":
        return WIKI_ROOT / "base" / f"{slug}.md"
    if entity.key == "examples:all":
        return WIKI_ROOT / "examples" / "examples-index.md"  # TODO: 세분화 필요시 추후 보완
    if entity.key == "guides:all":
        return WIKI_ROOT / "guides" / "guides-index.md"
    return WIKI_ROOT / "misc" / f"{slug}.md"


# ---------------------------------------------------------------------------
# 5. 메인 파이프라인
# ---------------------------------------------------------------------------


def load_documents() -> dict:
    """documents.jsonl → {상대경로: 본문}.

    metadata의 relative_path / source_path / raw_path 중 있는 것을 경로로 쓴다.
    corpus/raw/connectedhomeip/ 접두사가 붙어 있으면 떼어 상대경로로 맞춘다.
    """
    if not CORPUS_DOCS.exists():
        raise SystemExit(
            f"[오류] {CORPUS_DOCS} 가 없습니다.\n"
            "       티어 산출물은 git에 올라가지 않으므로 로컬에서 만들어야 합니다:\n"
            "         python3 scripts/corpus/build_tiers.py --tier c3\n"
            "       (상태 확인: --status-only / 자세한 내용은 corpus/HANDOFF.md)"
        )
    prefix = "corpus/raw/connectedhomeip/"
    docs: dict = {}
    snapshot_ids: set = set()
    # 한 번 읽은 바이트로 해시와 본문을 같이 얻는다. 따로 두 번 읽으면 그 사이에
    # 파일이 바뀌었을 때 manifest 의 sha256 이 실제로 컴파일한 본문과 어긋난다. (#27 A 기준 점검)
    raw = CORPUS_DOCS.read_bytes()
    global CORPUS_DOCS_SHA256
    CORPUS_DOCS_SHA256 = hashlib.sha256(raw).hexdigest()
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        meta = d.get("metadata", {})
        rel = meta.get("relative_path") or meta.get("source_path") or meta.get("raw_path")
        if not rel:
            continue
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
        docs[rel] = d.get("text", "")
        sid = d.get("snapshot_id")
        if sid:
            snapshot_ids.add(sid)
    # 실제로 읽은 줄의 snapshot_id 를 쓴다. snapshot.json 에서 베껴 오면
    # CORPUS_DOCS 만 바꿔도 라벨은 그대로여서 위키 출처가 거짓이 된다. (#23 리뷰)
    if len(snapshot_ids) > 1:
        raise SystemExit(
            f"[오류] {CORPUS_DOCS} 안에 snapshot_id 가 {len(snapshot_ids)}종 섞여 있습니다: "
            f"{sorted(snapshot_ids)}\n       한 코퍼스 스냅샷만으로 컴파일해야 합니다."
        )
    if not snapshot_ids:
        raise SystemExit(
            f"[오류] {CORPUS_DOCS} 줄에 snapshot_id 가 없습니다. "
            "코퍼스를 build_tiers.py 로 다시 만들어야 합니다."
        )
    global CORPUS_SNAPSHOT_ID
    CORPUS_SNAPSHOT_ID = next(iter(snapshot_ids))
    print(f"[정보] {CORPUS_DOCS} 에서 {len(docs)}개 문서를 읽음 "
          f"(총 {sum(len(t) for t in docs.values()):,}자) / snapshot {CORPUS_SNAPSHOT_ID}")
    return docs


def discover_and_group():
    scope = load_scope()
    path_to_entity, dir_to_entity, entities, cluster_name_to_key = build_registry(scope)

    docs = load_documents()

    n_files = 0
    for rel_str in sorted(docs):
        rel_path = Path(rel_str)
        result = classify(rel_path, path_to_entity, dir_to_entity, entities, cluster_name_to_key)
        if result is None:
            continue
        key, role = result
        if key not in entities:
            entities[key] = Entity(key=key, kind="misc", name=key.split(":")[-1])
        # 3번째 원소는 이제 파일 경로가 아니라 본문 텍스트다.
        entities[key].files.append((role, rel_path.as_posix(), docs[rel_str]))
        n_files += 1

    print(f"[정보] {n_files}개 파일을 {len(entities)}개 엔티티로 그룹핑함")
    return entities


# ---------------------------------------------------------------------------
# 5-1. 위키 manifest (#27 A 기준 점검)
# ---------------------------------------------------------------------------
# A 는 Retriever 가 색인 청크 수를 대조해, 색인이 빠진 폴더에서는 멈춘다. C 는 엔티티 하나가
# 컴파일에 실패하면 그 페이지만 조용히 빠지고, 출처 검사는 있는 페이지만 본다. 그래서 컴파일을
# 시작하기 전에 "이 위키에 있어야 할 페이지 전부"와 "무엇으로 만들었는지"를 먼저 적어 둔다.


def build_manifest(entities, docs_meta: dict, provider: str, model: str) -> dict:
    """그룹핑 결과 → manifest dict. API·파일을 건드리지 않는 순수 함수다.

    docs_meta: {"documents_path", "documents_sha256", "snapshot_id"}
    파일이 없는 엔티티는 main() 이 컴파일하지 않아 페이지가 생기지 않으므로 뺀다.
    (C3 에서는 0개. 넣으면 run_batch 가 영영 없는 페이지를 기다리며 멈춘다.)
    --only / --limit 와 무관하게 전체 엔티티로 만든다. 일부만 컴파일한 위키는 페이지가
    모자라 run_batch 가 막아야 맞다.
    """
    ents = list(entities.values()) if isinstance(entities, dict) else list(entities)
    ents = [e for e in ents if e.files]
    pages = sorted({target_wiki_path(e).relative_to(WIKI_ROOT).as_posix() for e in ents})
    return {
        "schema": MANIFEST_SCHEMA,
        "documents_path": docs_meta["documents_path"],
        "documents_sha256": docs_meta["documents_sha256"],
        "snapshot_id": docs_meta["snapshot_id"],
        "compile_provider": provider,
        "compile_model": model,
        # 페이지 수와 다르면 두 엔티티가 한 파일로 겹친 것이다(검사기가 잡는다).
        "entity_count": len(ents),
        "pages": pages,
    }


def manifest_path() -> Path:
    return WIKI_ROOT / MANIFEST_NAME


def read_manifest():
    """기존 manifest. 없으면 None, 깨졌으면 그 사실만 담은 dict (새 manifest 와 절대 같지 않다)."""
    path = manifest_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        return {"_unreadable": f"{exc.__class__.__name__}: {exc}"}


def manifest_conflict(prior, manifest: dict, existing_pages: list):
    """이미 있는 페이지를 건너뛰면 manifest 가 거짓이 되는 경우의 이유. 괜찮으면 None.

    main() 은 기존 페이지를 --force 없이 건너뛴다(이어하기). 그 페이지가 다른 입력·다른
    모델로 만든 것이면, 새 manifest 는 그 페이지들까지 이번 입력으로 만들었다고 적게 된다.
    manifest 는 첫 엔티티보다 먼저 쓰이므로, 고친 컴파일러로 이어하는 위키에는 항상 있다.
    """
    if not existing_pages:
        return None
    if prior is None:
        return f"manifest 없이 만들어진 페이지 {len(existing_pages)}개(예전 컴파일러 산출물)"
    diff = sorted(k for k in set(prior) | set(manifest) if prior.get(k) != manifest.get(k))
    if diff:
        return f"기존 {MANIFEST_NAME} 와 다른 항목 {diff}"
    return None


def write_manifest(manifest: dict) -> Path:
    """manifest 를 원자적으로 쓴다(임시 파일 + os.replace). 중간에 멈춰도 반쯤 쓴 파일이 남지 않는다."""
    path = manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(MANIFEST_NAME + ".tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def compile_entity(entity: Entity, dry_run: bool, ssot_commit: str, attempt: int = 1) -> Path:
    out_path = target_wiki_path(entity)

    if dry_run:
        file_list = ", ".join(f"[{r}]{p}" for r, p, _ in entity.files)
        print(f"[dry-run] {entity.key} ({len(entity.files)}개 파일) -> {out_path}")
        print(f"          {file_list}")
        return out_path, {}

    pieces = []
    source_paths = []
    for role, rel_path, text in entity.files:
        pieces.append((role, rel_path, text))
        source_paths.append(rel_path)

    body, usage = call_llm(SYSTEM_PROMPT, build_user_prompt(entity.name, pieces),
                           entity_key=entity.key, attempt=attempt)
    if not (body or "").strip():
        # 본문이 비면 페이지를 쓰지 않는다. 호출은 이미 원장에 남았다.
        raise TruncatedResponse("응답 본문이 비어 있습니다 — 페이지를 저장하지 않습니다.")

    frontmatter = (
        "---\n"
        f"entity: {entity.name}\n"
        f"ids: {entity.ids}\n"
        f"source_paths: {source_paths}\n"
        f"commit_hash: {ssot_commit}\n"
        f"doc_type: {entity.kind}\n"
        f"compiled_by: {MODEL_PROVIDER}/{MODEL_NAME}\n"
        f"corpus_source: {CORPUS_DOCS.as_posix()}\n"
        f"corpus_snapshot: {CORPUS_SNAPSHOT_ID}\n"
        "---\n\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(frontmatter + body, encoding="utf-8")
    print(f"[완료] {out_path}  (입력 {usage.get('uncached_input')} / "
          f"캐시쓰기 {usage.get('cache_creation')} / 캐시읽기 {usage.get('cache_read')} / "
          f"출력 {usage.get('output')})")
    return out_path, usage


def _safe_console() -> None:
    """Windows 기본 콘솔(cp949)에서 출력할 수 없는 문자가 있어도 멈추지 않게 한다.
    담지 못하는 문자는 '?' 로 바뀐다. (#27 동수님 리뷰 P1-1)"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


def main():
    _safe_console()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--wiki-root",
        help="출력 위키 디렉터리 (기본 systems/system_c_llm_wiki/wiki). "
             "컴파일 모델별로 다른 경로를 주면 여러 벌을 나란히 만들 수 있다.",
    )
    parser.add_argument(
        "--only",
        help="테스트용: 이 엔티티 key 하나만 실제로 컴파일 (예: --only 'base:Label'). "
             "먼저 --dry-run으로 key 목록을 확인한 뒤 쓰면 됨.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="테스트용: 최대 N개 엔티티만 컴파일 (API 호출 비용/시간 아끼고 싶을 때)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="결과 파일이 이미 있어도 다시 컴파일. 기본은 이미 만들어진 페이지는 건너뜀 "
             "(중간에 에러로 멈췄다가 재실행할 때 이미 끝난 것 다시 API 호출 안 하려고).",
    )
    args = parser.parse_args()

    if args.wiki_root:
        global WIKI_ROOT
        WIKI_ROOT = Path(args.wiki_root)

    scope = load_scope()
    ssot_commit = scope.get("ssot_commit") or scope.get("repository", {}).get("commit_sha", "UNKNOWN")

    entities = discover_and_group()
    if not entities:
        sys.exit(1)

    # 그룹핑 직후, 엔티티를 하나도 컴파일하기 전에 manifest 를 쓴다. 중간에 멈춘 위키도
    # "무엇이 빠졌는지"를 알 수 있어야 한다. --dry-run 은 아무것도 쓰지 않는다. (#27 A 기준 점검)
    if not args.dry_run:
        manifest = build_manifest(entities, {
            "documents_path": CORPUS_DOCS.as_posix(),
            "documents_sha256": CORPUS_DOCS_SHA256,
            "snapshot_id": CORPUS_SNAPSHOT_ID,
        }, MODEL_PROVIDER, MODEL_NAME)
        # 아래 루프가 --force 없이 건너뛸 페이지 (같은 조건: 있고 비어 있지 않음)
        existing = [p for p in manifest["pages"]
                    if (WIKI_ROOT / p).exists() and (WIKI_ROOT / p).stat().st_size > 0]
        reason = manifest_conflict(read_manifest(), manifest, existing)
        # 전체 --force 만 모든 페이지를 새로 만든다. --only/--limit 는 일부만 만든다.
        if reason and (not args.force or args.only or args.limit is not None):
            raise SystemExit(
                f"[오류] {WIKI_ROOT} 에 이미 있는 페이지 {len(existing)}개가 이번 입력·모델로 "
                f"만든 것인지 확인할 수 없습니다 — {reason}.\n"
                "       이대로 돌리면 그 페이지를 건너뛰고, 다른 입력으로 만든 페이지에 이번 "
                "manifest 가 붙습니다.\n"
                "       --only/--limit 없이 --force 로 전체를 다시 만들거나, 다른 --wiki-root 를 쓰세요."
            )
        if reason:
            # 여기까지 왔으면 --only/--limit 없는 전체 --force 다. 다시 만들 페이지와 manifest 에
            # 없는 페이지를 먼저 지운다. 지우지 않으면 컴파일에 실패한 엔티티의 옛 페이지가 남고,
            # 새 manifest 가 그 페이지를 이번 입력·모델로 만든 것처럼 보증한다. 먼저 지우고
            # manifest 를 쓰므로, 중간에 멈춰도 페이지가 빠진 상태가 되어 run_batch 가 막는다.
            # (#27 A 기준 점검)
            keep = set(manifest["pages"])
            stale = [p.relative_to(WIKI_ROOT).as_posix() for p in WIKI_ROOT.rglob("*.md")
                     if p.stem.lower() != "readme"
                     and (p.relative_to(WIKI_ROOT).as_posix() in existing
                          or p.relative_to(WIKI_ROOT).as_posix() not in keep)]
            for rel in stale:
                (WIKI_ROOT / rel).unlink()
            print(f"[정리] 전체 재구축 - 이전 페이지 {len(stale)}개를 지우고 다시 만든다")
        write_manifest(manifest)
        print(f"[manifest] {manifest_path()} — 페이지 {len(manifest['pages'])}개 / "
              f"입력 sha256 {CORPUS_DOCS_SHA256[:12]}... / {MODEL_PROVIDER}/{MODEL_NAME}")

    # 보기 좋게: 종류별로 정렬해서 출력/컴파일
    keys = sorted(entities, key=lambda k: (entities[k].kind, entities[k].name))

    if args.only:
        keys = [k for k in keys if k == args.only]
        if not keys:
            print(f"[경고] --only로 지정한 '{args.only}' 를 찾을 수 없음. "
                  f"--dry-run으로 실제 key 목록을 먼저 확인하세요.")
            sys.exit(1)

    if args.limit is not None:
        keys = keys[: args.limit]

    failed = []
    skipped = 0
    compiled = 0
    # 이미 원장(build_calls.jsonl)에 몇 번 적혔는지 = 이 엔티티의 다음 시도 번호
    prior_attempts = _count_prior_attempts()

    for key in keys:
        ent = entities[key]
        if not ent.files:
            continue

        out_path = target_wiki_path(ent)
        if not args.dry_run and not args.force and out_path.exists() and out_path.stat().st_size > 0:
            print(f"[건너뜀] {key} -> {out_path} (이미 존재함. 다시 만들려면 --force)")
            skipped += 1
            continue

        try:
            compile_entity(ent, dry_run=args.dry_run, ssot_commit=ssot_commit,
                           attempt=prior_attempts.get(key, 0) + 1)
            compiled += 1
        except Exception as e:
            # 한 엔티티가 완전히 실패해도 전체를 멈추지 않는다. 실패한 것만 --only 로 다시.
            print(f"[실패] {key}: {e.__class__.__name__}: {e}")
            failed.append(key)
        finally:
            # 엔티티마다 집계를 갱신한다. 중간에 Ctrl-C 가 나도 여기까지의 과금이 남는다.
            if not args.dry_run:
                write_build_tokens(ssot_commit)

    if args.dry_run:
        return

    # ---- 토큰: 원장에서 집계 (호출 단위로 이미 적혀 있다) ----
    bt = write_build_tokens(ssot_commit)
    t = bt["totals"]
    print(f"[토큰] {WIKI_ROOT / 'build_tokens.json'} — 호출 {bt['calls']}건 / "
          f"입력(캐시제외) {t['uncached_input']:,} / 캐시쓰기 {t['cache_creation']:,} / "
          f"캐시읽기 {t['cache_read']:,} / 출력 {t['output']:,}  (합산 금지)")
    print(f"       원장: {build_calls_path()}")

    print(f"\n[요약] 컴파일 {compiled}개 / 건너뜀 {skipped}개 / 실패 {len(failed)}개")
    if failed:
        print("실패한 엔티티:")
        for k in failed:
            print(f"  --only \"{k}\"")
        print("위 명령으로 하나씩 다시 시도하거나, 스크립트를 그냥 다시 실행하면 "
              "(이미 만들어진 페이지는 --force 없인 건너뛰니까) 실패했던 것만 자동으로 다시 시도됨.")
        sys.exit(1)


if __name__ == "__main__":
    main()
