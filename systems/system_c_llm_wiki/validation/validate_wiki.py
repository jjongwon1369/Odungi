# -*- coding: utf-8 -*-
"""
LLM Wiki 검증 스크립트 (System C)
=================================

validation/README.md 에 정의된 3가지를 검사한다:
  1. 출처 검증      — 모든 페이지가 source_paths / commit_hash 프론트매터를 갖는가
  2. 식별자 보존 검증 — 원본에 있던 식별자(클러스터 ID, 속성/명령 이름 등)가
                       컴파일된 페이지에 그대로 남아있는가
  3. 정보 누락 + 토큰 — 위키 전체 토큰 수를 추정하고, 정적 전체주입 방식으로
                       context에 들어갈 수 있는지 판정

사용법:
    python3 systems/system_c_llm_wiki/validation/validate_wiki.py
    (리포 루트에서 실행)
"""

import json
import re
import sys
from pathlib import Path

CORPUS_RAW = Path("corpus/raw/connectedhomeip")
WIKI_ROOT = Path("systems/system_c_llm_wiki/wiki")

# 정적 전체주입이 가능한지 판단할 기준선 (모델별 context window)
CONTEXT_BUDGETS = [
    ("128K 모델", 128_000),
    ("200K 모델", 200_000),
    ("1M 모델", 1_000_000),
]
# 위키 외에 질문/지시문/답변 여유분으로 남겨둘 몫
RESERVED_TOKENS = 8_000

# 원본에서 뽑아낼 식별자 패턴
ID_PATTERNS = [
    re.compile(r'\b0x[0-9A-Fa-f]{4}\b'),          # 클러스터/속성 ID
    re.compile(r'name="([A-Za-z][A-Za-z0-9_]{2,})"'),  # XML name 속성
]


def estimate_tokens(text: str) -> int:
    """대략적인 토큰 수 추정. 영문/기호는 ~4자당 1토큰, 한글 등 비ASCII는 ~1.5자당 1토큰."""
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    other_chars = len(text) - ascii_chars
    return int(ascii_chars / 4 + other_chars / 1.5)


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    block = text[3:end]
    body = text[end + 4:]
    fm = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body


def extract_identifiers(text: str):
    found = set()
    for pat in ID_PATTERNS:
        for m in pat.finditer(text):
            found.add(m.group(1) if m.groups() else m.group(0))
    return found


def main():
    pages = sorted(p for p in WIKI_ROOT.rglob("*.md") if p.name != "README.md")
    if not pages:
        print(f"[오류] {WIKI_ROOT} 에 검증할 페이지가 없습니다.")
        sys.exit(1)

    print(f"검증 대상 페이지: {len(pages)}개\n")
    print("=" * 78)
    print("1) 출처 검증 + 2) 식별자 보존 검증")
    print("=" * 78)

    total_tokens = 0
    no_frontmatter = []
    low_coverage = []
    rows = []

    for page in pages:
        raw = page.read_text(encoding="utf-8", errors="ignore")
        total_tokens += estimate_tokens(raw)
        fm, body = parse_frontmatter(raw)

        if not fm or "source_paths" not in fm or "commit_hash" not in fm:
            no_frontmatter.append(page)
            rows.append((page.name, "프론트매터 없음", "-", "-"))
            continue

        # 프론트매터의 source_paths 파싱 (파이썬 리스트 리터럴 형태로 저장돼 있음)
        try:
            src_list = json.loads(fm["source_paths"].replace("'", '"'))
        except Exception:
            src_list = []

        # 원본 식별자 수집
        origin_ids = set()
        for rel in src_list:
            f = CORPUS_RAW / rel
            if f.exists():
                origin_ids |= extract_identifiers(
                    f.read_text(encoding="utf-8", errors="ignore"))

        if not origin_ids:
            rows.append((page.name, "OK", "원본 식별자 0개", "-"))
            continue

        kept = {i for i in origin_ids if i in raw}
        missing = origin_ids - kept
        pct = len(kept) / len(origin_ids) * 100
        rows.append((page.name, "OK", f"{len(kept)}/{len(origin_ids)}", f"{pct:.0f}%"))
        if pct < 60:
            low_coverage.append((page, pct, sorted(missing)[:8]))

    w = max(len(r[0]) for r in rows) + 2
    print(f"{'페이지'.ljust(w)} {'출처':<14} {'식별자 보존':<16} 비율")
    print("-" * 78)
    for name, src, ids, pct in rows:
        print(f"{name.ljust(w)} {src:<14} {ids:<16} {pct}")

    print()
    print("=" * 78)
    print("3) 전체 토큰 수 / 정적 전체주입 수용 가능 여부")
    print("=" * 78)
    print(f"위키 전체 추정 토큰 수: 약 {total_tokens:,} 토큰 "
          f"(페이지 {len(pages)}개, 질문·지시문 여유분 {RESERVED_TOKENS:,} 토큰 별도)")
    print()
    needed = total_tokens + RESERVED_TOKENS
    for label, budget in CONTEXT_BUDGETS:
        verdict = "가능" if needed <= budget else "불가 — 초과"
        print(f"  {label:<10} (context {budget:>9,}) : {verdict} "
              f"(필요 {needed:,})")

    print()
    print("=" * 78)
    print("요약")
    print("=" * 78)
    print(f"  전체 페이지          : {len(pages)}개")
    print(f"  프론트매터 누락      : {len(no_frontmatter)}개")
    print(f"  식별자 보존율 60% 미만: {len(low_coverage)}개")
    if no_frontmatter:
        print("\n  [경고] 프론트매터 없는 페이지:")
        for p in no_frontmatter:
            print(f"    - {p}")
    if low_coverage:
        print("\n  [경고] 식별자 보존율이 낮은 페이지 (원본 대비 누락 많음):")
        for p, pct, miss in low_coverage:
            print(f"    - {p.name} ({pct:.0f}%) 누락 예시: {', '.join(miss)}")

    if no_frontmatter or low_coverage:
        sys.exit(1)
    print("\n  전체 검증 통과")


if __name__ == "__main__":
    main()
