# -*- coding: utf-8 -*-
"""
컴파일 모델별 위키 비교
=======================
같은 코퍼스를 서로 다른 LLM으로 컴파일한 위키들이 내용상 얼마나 다른지 정량 비교한다.
"컴파일 모델 등급이 위키 품질을 좌우하는가"를 판단하는 근거 데이터.

비교 축:
  1. 규모       — 페이지 수, 총 토큰, 페이지당 평균/최소/최대
  2. 구조 준수  — 지정한 섹션(## 개요 / ## 스펙 / ...)을 얼마나 지켰는가
  3. 식별자 보존 — 원본 대비 식별자를 얼마나 살렸는가 (핵심 품질 지표)
  4. 내용 중첩  — 같은 페이지끼리 어휘가 얼마나 겹치는가 (Jaccard)

사용법 (리포 루트에서):
    python3 systems/system_c_llm_wiki/validation/compare_wikis.py \
        systems/system_c_llm_wiki/wiki \
        systems/system_c_llm_wiki/wiki-gpt-6-luna \
        systems/system_c_llm_wiki/wiki-gpt-6-sol \
        systems/system_c_llm_wiki/wiki-gpt-6-astra
"""
import json
import os
import re
import sys
from pathlib import Path

# 식별자 보존율의 기준은 **컴파일러가 실제로 읽은 본문**이다.
# corpus/raw 원본을 기준으로 삼으면, documents.jsonl 에서 정당하게 빠진 식별자까지
# '누락'으로 세어 보존율이 실제보다 낮게 나온다. (#23 리뷰 5번)
CORPUS_DOCS = Path(os.environ.get(
    "CORPUS_DOCS", "corpus/tiers/c3/processed/documents.jsonl"))


def load_corpus_texts() -> dict:
    """documents.jsonl → {상대경로: 본문}. 위키 프론트매터의 source_paths 와 맞춘다."""
    if not CORPUS_DOCS.exists():
        raise SystemExit(
            f"[오류] {CORPUS_DOCS} 가 없습니다.\n"
            "       python3 scripts/corpus/build_tiers.py --tier c3 로 먼저 만드세요.\n"
            "       (식별자 보존율은 컴파일러가 실제로 읽은 본문을 기준으로 셉니다.)"
        )
    prefix = "corpus/raw/connectedhomeip/"
    out = {}
    for line in CORPUS_DOCS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        m = d.get("metadata", {})
        rel = m.get("relative_path") or m.get("source_path") or m.get("raw_path")
        if not rel:
            continue
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
        out[rel] = d.get("text", "")
    return out


CORPUS_TEXTS = load_corpus_texts()
SECTIONS = ["## 개요", "## 스펙", "## SDK 정의", "## 구현", "## 예시", "## 관련 문서"]
ID_PATTERNS = [re.compile(r"\b0x[0-9A-Fa-f]{4}\b"),
               re.compile(r'name="([A-Za-z][A-Za-z0-9_]{2,})"')]


def tok(t: str) -> int:
    a = sum(1 for c in t if ord(c) < 128)
    return int(a / 4 + (len(t) - a) / 1.5)


def split_fm(text: str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:]


def origin_ids(src_list):
    found = set()
    for rel in src_list:
        t = CORPUS_TEXTS.get(rel)
        if t:
            for pat in ID_PATTERNS:
                for m in pat.finditer(t):
                    found.add(m.group(1) if m.groups() else m.group(0))
    return found


def words(text: str):
    return set(re.findall(r"[A-Za-z0-9_]{3,}", text.lower()))


def load(root: Path):
    pages = {}
    for p in sorted(root.rglob("*.md")):
        if p.name == "README.md":
            continue
        raw = p.read_text(encoding="utf-8", errors="ignore")
        fm, body = split_fm(raw)
        try:
            src = json.loads(fm.get("source_paths", "[]").replace("'", '"'))
        except Exception:
            src = []
        pages[str(p.relative_to(root))] = {
            "raw": raw, "body": body, "fm": fm, "src": src,
            "tokens": tok(raw),
            "sections": [s for s in SECTIONS if s in body],
        }
    return pages


def main():
    roots = [Path(a) for a in sys.argv[1:]]
    if len(roots) < 2:
        sys.exit("위키 경로를 2개 이상 지정하세요.")
    wikis = {}
    for r in roots:
        if not r.exists():
            print(f"[건너뜀] {r} 없음")
            continue
        pg = load(r)
        model = next((v["fm"].get("compiled_by", "?") for v in pg.values()), "?")
        wikis[r.name] = {"pages": pg, "model": model}

    names = list(wikis)
    W = max(len(n) for n in names) + 2

    print("=" * 84)
    print("1) 규모 비교")
    print("=" * 84)
    print(f"{'위키':<{W}}{'모델':<26}{'페이지':>7}{'총토큰':>10}{'평균':>8}{'최대':>8}")
    print("-" * 84)
    for n in names:
        pg = wikis[n]["pages"]
        ts = [v["tokens"] for v in pg.values()]
        print(f"{n:<{W}}{wikis[n]['model']:<26}{len(pg):>7}{sum(ts):>10,}"
              f"{sum(ts)//max(len(ts),1):>8,}{max(ts):>8,}")

    print()
    print("=" * 84)
    print("2) 섹션 구조 준수 (페이지당 평균 섹션 수 / 섹션별 등장 페이지 수)")
    print("=" * 84)
    print(f"{'위키':<{W}}{'평균':>6}  " + "".join(f"{s.replace('## ',''):>10}" for s in SECTIONS))
    print("-" * 84)
    for n in names:
        pg = wikis[n]["pages"]
        avg = sum(len(v["sections"]) for v in pg.values()) / max(len(pg), 1)
        counts = [sum(1 for v in pg.values() if s in v["sections"]) for s in SECTIONS]
        print(f"{n:<{W}}{avg:>6.1f}  " + "".join(f"{c:>10}" for c in counts))

    print()
    print("=" * 84)
    print("3) 식별자 보존율 (원본 대비)")
    print("=" * 84)
    print(f"{'위키':<{W}}{'보존율':>8}{'보존/전체':>16}{'60%미만 페이지':>16}")
    print("-" * 84)
    for n in names:
        pg = wikis[n]["pages"]
        kept = total = 0
        low = 0
        for v in pg.values():
            oid = origin_ids(v["src"])
            if not oid:
                continue
            k = sum(1 for i in oid if i in v["raw"])
            kept += k
            total += len(oid)
            if k / len(oid) < 0.6:
                low += 1
        pct = kept / total * 100 if total else 0
        print(f"{n:<{W}}{pct:>7.1f}%{f'{kept:,}/{total:,}':>16}{low:>16}")

    print()
    print("=" * 84)
    print("4) 내용 중첩도 — 기준 위키 대비 Jaccard 유사도 (1.0 = 동일)")
    print("=" * 84)
    base = names[0]
    bp = wikis[base]["pages"]
    print(f"기준: {base} ({wikis[base]['model']})\n")
    print(f"{'위키':<{W}}{'평균유사도':>12}{'공통페이지':>12}{'가장 다른 페이지':>34}")
    print("-" * 84)
    for n in names[1:]:
        pg = wikis[n]["pages"]
        common = set(bp) & set(pg)
        sims = []
        for k in common:
            a, b = words(bp[k]["body"]), words(pg[k]["body"])
            sims.append((len(a & b) / len(a | b) if (a | b) else 1.0, k))
        if not sims:
            continue
        avg = sum(s for s, _ in sims) / len(sims)
        worst = min(sims)
        print(f"{n:<{W}}{avg:>11.3f}{len(common):>12}   {worst[1][:28]:<28}{worst[0]:>.3f}")

    print()
    print("=" * 84)
    print("판정 가이드")
    print("=" * 84)
    print("  Jaccard 0.8 이상  → 내용 거의 동일. 컴파일 모델 등급 영향 작음")
    print("  Jaccard 0.5~0.8   → 표현/상세도 차이 있음. 질의 정확도로 추가 확인 필요")
    print("  Jaccard 0.5 미만  → 내용 자체가 다름. 고성능 모델 사용 근거 확보")
    print("  식별자 보존율은 높을수록 좋음 (원문 식별자를 빠뜨리지 않았다는 뜻)")


if __name__ == "__main__":
    main()
