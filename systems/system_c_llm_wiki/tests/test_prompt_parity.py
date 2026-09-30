#!/usr/bin/env python3
"""프롬프트 일치 테스트. (9/30 팀 결정: A 영어 원문 사용)

A·B 와 공통이어야 하는 문장이 C 프롬프트에 글자 그대로 들어있는지 본다.
C 고유 차이는 규칙 3(인용 대상)과 규칙 5(제출 경로)뿐이어야 한다.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))

A_SOURCE = REPO / "systems/system_a_rag/rag_proto/src/rag_proto/s6_generate.py"


def _literal_from_source(path: Path, name: str) -> str:
    """A 의 소스에서 문자열 상수를 꺼낸다.

    모듈을 import 하지 않는다. s6_generate 는 pyyaml 등 A 쪽 의존성을 끌어오는데,
    C 만 돌리는 환경에는 그게 없을 수 있다. 프롬프트 대조에 A 의 런타임은 필요 없다.
    """
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{path.name} 에서 {name} 을 찾지 못했다")


A_PROMPT = _literal_from_source(A_SOURCE, "SYSTEM_PROMPT")
A_ABSTAIN = _literal_from_source(A_SOURCE, "ABSTAIN_PHRASE")

from run_agent import _build_system_prompt, ABSTAIN_PHRASE as C_ABSTAIN  # noqa: E402

C_PROMPT = _build_system_prompt()


def _lines(text):
    return [l for l in text.split("\n") if l.strip()]


def test_abstain_phrase_identical():
    assert A_ABSTAIN == C_ABSTAIN, (A_ABSTAIN, C_ABSTAIN)
    print(f"  ✓ 기권 문구 동일: {C_ABSTAIN!r}")


def test_abstain_phrase_appears_once_in_each():
    """기권 조건은 규칙 1에만. 두 번 나오면 별개 조건처럼 읽힌다. (#23 리뷰)"""
    assert A_PROMPT.count(A_ABSTAIN) == 1, A_PROMPT.count(A_ABSTAIN)
    assert C_PROMPT.count(C_ABSTAIN) == 1, C_PROMPT.count(C_ABSTAIN)
    print("  ✓ 기권 문구가 각 프롬프트에 정확히 1회")


def test_shared_sentences_are_verbatim():
    """머리말·규칙 1·2·4·맺음말은 A 원문과 글자 그대로 같아야 한다."""
    shared = [
        "You are a technical documentation assistant for the Matter smart home "
        "standard and the connectedhomeip SDK.",
        "Answer ONLY from the provided context. Follow these rules without exception:",
        "1. Never use knowledge outside the provided context. If the context does not "
        f'contain the answer, reply exactly: "{A_ABSTAIN}"',
        "2. Copy identifiers verbatim. Cluster names, attribute names, command names "
        "and hex IDs (e.g. OnOff, TemperatureSetpoint, 0x0201) must appear exactly as "
        "written in the context. Never translate, reformat or guess them.",
        "4. Be concise. Do not add caveats, summaries of your own process, or "
        "recommendations that are not in the context.",
        "Answer in the same language as the question.",
    ]
    a_flat = " ".join(A_PROMPT.split())
    c_flat = " ".join(C_PROMPT.split())
    for sent in shared:
        flat = " ".join(sent.split())
        assert flat in a_flat, f"A 에 없음: {flat[:60]}"
        assert flat in c_flat, f"C 에 없음: {flat[:60]}"
    print(f"  ✓ 공통 문장 {len(shared)}개가 A·C 양쪽에 글자 그대로")


def test_c_is_english_not_translated():
    """한국어 규칙 문장이 남아 있지 않은지. 기권 문구만 한국어다."""
    body = C_PROMPT.replace(C_ABSTAIN, "")
    hangul = [ch for ch in body if "가" <= ch <= "힣"]
    assert not hangul, f"한국어가 남아 있다: {''.join(hangul)[:40]}"
    print("  ✓ 기권 문구 외에는 한국어 없음")


def test_c_only_differences_are_rule3_and_rule5():
    c_rules = {l.split(".")[0]: l for l in _lines(C_PROMPT) if l[:1].isdigit()}
    a_rules = {l.split(".")[0]: l for l in _lines(A_PROMPT) if l[:1].isdigit()}
    assert set(a_rules) == {"1", "2", "3", "4"}, sorted(a_rules)
    assert set(c_rules) == {"1", "2", "3", "4", "5"}, sorted(c_rules)
    same = [k for k in ("1", "2", "4") if a_rules[k] != c_rules[k]]
    assert not same, f"공통 규칙이 다르다: {same}"
    assert "cited_pages" in c_rules["3"] and "chunk_id" in a_rules["3"]
    assert "submit_answer" in c_rules["5"]
    print("  ✓ 규칙 1·2·4 동일 / 3은 cited_pages / 5는 C 고유(제출 경로)")


def test_identifier_rules_parse_without_pyyaml():
    """pyyaml 이 없는 환경에서도 A 의 식별자 규칙을 같은 값으로 읽는가."""
    sys.path.insert(0, str(REPO / "systems" / "system_c_llm_wiki" / "agent"))
    import run_batch as rb
    text = rb.IDENTIFIER_CONFIG.read_text(encoding="utf-8")
    pats, stops = rb._parse_identifiers_block(text)
    assert list(pats) == list(rb.IDENTIFIER_PATTERNS), (pats, rb.IDENTIFIER_PATTERNS)
    assert list(stops) == list(rb.IDENTIFIER_STOPWORDS), (stops, rb.IDENTIFIER_STOPWORDS)
    assert pats, "식별자 패턴이 비었다"
    print(f"  ✓ pyyaml 없이도 같은 식별자 규칙 ({len(pats)}패턴 / {len(stops)}스톱워드)")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"프롬프트 일치 테스트 {len(fns)}개")
    for fn in fns:
        fn()
    print("전부 통과")
