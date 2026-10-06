"""시스템 출력 → score_l1.py 입력 변환

받는 형식
  A/B (RAG)  : rag_proto AnswerRecord v0.3  {qid, system, query_mode, answer, citations[{chunk_id, source_path}],
                                              retrieved{...}, tokens{uncached_input, cache_creation, cache_read, output}, error}
  C (Wiki)   : run_agent.py 결과            {query, answer, cited_pages[], retrieved{wiki_pages}, token_usage{prompt_tokens,
                                              cache_read, cache_write, output_tokens}}  + 실행 스크립트가 붙인 qid
  한 줄에 한 답변(jsonl) 또는 JSON 배열 모두 가능.

내보내는 형식 (score_l1.py)
  {query_id, system, model, run_id, answer_text, cited_sources{S1: path}, answer_status, tokens{4열}, error}

인용 규칙
  RAG : 답변 본문의 [chunk_id] → [S1], [S2] … 로 바꾸고 S번호 → source_path
  Wiki: 본문에 표지가 없으면 cited_pages 전체를 답변 끝의 [S1][S2]… 로 붙인다 (답변 전체에 대한 인용)

사용
  python eval/adapt_records.py runs/xxx/answers.jsonl --system A --model gpt-6-luna --run 1 -o results/raw/A_luna_run1.jsonl
"""
import argparse, json, pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8")

SYSTEM_MAP = {"rag": "A", "wiki": "C"}
ABSTAIN_PHRASE = "제공된 문서에서 확인되지 않음"   # rag_proto s6_generate.py 와 같은 문구


def load(path):
    text = pathlib.Path(path).read_text(encoding="utf-8").strip()
    if text.startswith("["):
        return json.loads(text)
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def tokens4(r):
    t = r.get("tokens")
    if isinstance(t, dict) and "uncached_input" in t:
        return {k: int(t.get(k, 0) or 0) for k in ("uncached_input", "cache_creation", "cache_read", "output")}
    u = r.get("token_usage") or {}
    prompt, read = int(u.get("prompt_tokens", 0) or 0), int(u.get("cache_read", 0) or 0)
    return {"uncached_input": max(prompt - read, 0), "cache_creation": int(u.get("cache_write", 0) or 0),
            "cache_read": read, "output": int(u.get("output_tokens", 0) or 0)}


def convert(r, system=None, model=None, run=None):
    qid = r.get("query_id") or r.get("qid")
    if not qid:
        raise ValueError(f"qid 없음: {str(r)[:120]}")
    text = r.get("answer_text", r.get("answer")) or ""
    cited, cited_chunks, citation_error = {}, {}, None
    is_wiki = r.get("system") == "wiki" or system == "C" or "cited_pages" in r
    markup_leak = False
    if is_wiki and "</answer>" in text:
        # 모델이 도구 호출 표기(</answer><parameter name="cited_pages">[...])를 답 본문에 흘린 경우 (run_c3_0930 8건).
        # 표기 뒤쪽은 답이 아니므로 잘라낸다 — 페이지 ID 속 16진 값(0x0057 등)이 식별자로 채점되지 않게.
        # 흘린 cited_pages는 모델이 밝힌 인용이므로, cited_pages 칸이 비어 있을 때만 인용으로 복구한다.
        cut = text.index("</answer>")
        tail, text = text[cut:], text[:cut].rstrip()
        markup_leak = True
        if not r.get("cited_pages"):
            leaked = re.findall(r'"([a-z-]+/[^"\s]+)"', tail)
            if leaked:
                r = dict(r, cited_pages=leaked)
    if r.get("citations") and not is_wiki:                   # RAG (A·B)
        # citations = LLM에 넘긴 상위 청크 전부. 실제 인용은 본문의 [chunk_id] 표기로만 판단한다 (태이님 B2)
        by_chunk = {c["chunk_id"]: c["source_path"] for c in r["citations"]}
        order = list(dict.fromkeys(m for m in re.findall(r"\[([^\[\]\s]+)\]", text) if m in by_chunk))
        for i, cid in enumerate(order, 1):
            text = text.replace(f"[{cid}]", f"[S{i}]")
            cited[f"S{i}"], cited_chunks[f"S{i}"] = by_chunk[cid], cid
    elif is_wiki and (r.get("cited_pages") or r.get("citations")):   # Wiki (C)
        # PR #27부터 C도 citations에 {chunk_id: 페이지ID}를 넣는다 → 페이지 ID 기준으로 읽는다
        pages = list(dict.fromkeys(r.get("cited_pages") or [c["chunk_id"] for c in r["citations"]]))
        cited = {f"S{i}": p for i, p in enumerate(pages, 1)}
        if pages and not re.search(r"\[S\d+\]", text):
            text = text.rstrip() + " " + "".join(f"[S{i}]" for i in range(1, len(pages) + 1))
    elif r.get("cited_sources"):
        cited = r["cited_sources"]
    # 검색 결과에 없는 청크 ID 표기(dangling)는 [인용오류]로 바꾼다 — 청크 ID의 소문자 이름 조각이
    # 식별자로 잡히지 않게 하고(B5), 심판에게 시스템 흔적을 숨긴다(B4)
    text, n_bad = re.subn(r"\[[A-Za-z0-9_.\-]+__\d{4}\]", "[인용오류]", text)
    err = r.get("error")
    if err and str(err).startswith("dangling_citations"):     # 답변은 정상, 인용만 문제 (B7)
        citation_error, err = str(err), None
    if n_bad and not citation_error:
        citation_error = f"dangling_citations: {n_bad}"
    status = r.get("answer_status") or ("error" if err else "answered")
    partial_abstain = False
    if status == "answered" and ABSTAIN_PHRASE in text:     # 기권 문구 (B6)
        # 답 전체가 기권 문구뿐일 때만 기권. 일부만 답하고 나머지에 문구를 쓴 부분 답변은 정상 채점한다
        rest = re.sub(r"\[[^\]]*\]|[\s\"'.,:;!?·()\-*]", "", text.replace(ABSTAIN_PHRASE, ""))
        if len(rest) <= 5:
            status = "abstained"
        else:
            partial_abstain = True
    sysname = system or r.get("system")
    sysname = SYSTEM_MAP.get(sysname, sysname)
    if sysname == "A" and r.get("query_mode") == "decomposed":
        sysname = "B"
    mdl = model or r.get("model")
    rn = run if run is not None else r.get("run")
    return {"query_id": qid, "system": sysname, "model": mdl, "run": rn,
            "run_id": r.get("run_id") or f"{sysname}_{mdl}_run{rn}",
            "answer_text": text, "cited_sources": cited, "answer_status": status,
            "cited_chunks": cited_chunks, "citation_error": citation_error, "partial_abstain": partial_abstain,
            "markup_leak": markup_leak,
            "tokens": tokens4(r), "error": err,
            "retrieved": r.get("retrieved"), "config_hash": r.get("config_hash")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--system", help="A / B / C (레코드 값 덮어쓰기)")
    ap.add_argument("--model")
    ap.add_argument("--run", type=int)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    out, n = pathlib.Path(a.out), 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fp:
        for p in a.inputs:
            for r in load(p):
                fp.write(json.dumps(convert(r, a.system, a.model, a.run), ensure_ascii=False) + "\n")
                n += 1
    print(f"{n}건 → {out}")


if __name__ == "__main__":
    main()
