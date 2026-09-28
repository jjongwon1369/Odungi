"""7개 모델에 대해 '도구 호출 + 추론 강도(light)'가 동시에 되는지, 토큰 4열이 나오는지 확인한다.

실행: cd <repo root> && (set -a; . ./.env.local; set +a; python3 systems/system_c_llm_wiki/agent/probe_api.py)
"""
import json, os, ssl, certifi, urllib.request, urllib.error, pathlib

CTX = ssl.create_default_context(cafile=certifi.where())
ROOT = pathlib.Path(__file__).parent
MODELS = json.loads((ROOT / "models.json").read_text())

PROMPT = "위키에 어떤 페이지가 있는지 list_pages 도구로 확인해줘."
DESC = "위키 페이지 목록을 반환한다"
SCHEMA = {"type": "object", "properties": {}}


def post(url, headers, payload, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": {"message": str(e)}}


def probe_anthropic(cfg, key):
    rc = cfg.get("reasoning_config") or {}
    payload = {
        "model": cfg["model_id"], "max_tokens": 2048,
        "tools": [{"name": "list_pages", "description": DESC, "input_schema": SCHEMA}],
        "messages": [{"role": "user", "content": PROMPT}],
        **rc,
    }
    code, d = post("https://api.anthropic.com/v1/messages",
                   {"x-api-key": key, "anthropic-version": "2023-06-01",
                    "content-type": "application/json"}, payload)
    if code != 200:
        return code, d, False, [None] * 4
    tool = any(b.get("type") == "tool_use" for b in d.get("content", []))
    u = d.get("usage", {})
    return code, d, tool, [u.get("input_tokens"), u.get("output_tokens"),
                           u.get("cache_read_input_tokens"),
                           u.get("cache_creation_input_tokens")]


def probe_responses(cfg, key, base):
    """OpenAI Responses API — 도구와 추론을 함께 쓸 수 있는지 확인."""
    rc = cfg.get("reasoning_config") or {}
    effort = rc.get("reasoning_effort")
    payload = {
        "model": cfg["model_id"], "input": PROMPT,
        "tools": [{"type": "function", "name": "list_pages",
                   "description": DESC, "parameters": SCHEMA}],
    }
    if effort:
        payload["reasoning"] = {"effort": effort}
    code, d = post(base.rstrip("/") + "/responses",
                   {"Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"}, payload)
    if code != 200:
        return code, d, False, [None] * 4
    tool = any(o.get("type") == "function_call" for o in d.get("output", []))
    u = d.get("usage", {})
    itd = u.get("input_tokens_details") or {}
    return code, d, tool, [u.get("input_tokens"), u.get("output_tokens"),
                           itd.get("cached_tokens"), u.get("cache_write_tokens")]


def probe_chat(cfg, key, base):
    rc = cfg.get("reasoning_config") or {}
    payload = {
        "model": cfg["model_id"],
        "messages": [{"role": "user", "content": PROMPT}],
        "tools": [{"type": "function", "function": {
            "name": "list_pages", "description": DESC, "parameters": SCHEMA}}],
        **rc,
    }
    code, d = post(base.rstrip("/") + "/chat/completions",
                   {"Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"}, payload)
    if code != 200:
        return code, d, False, [None] * 4
    msg = (d.get("choices") or [{}])[0].get("message", {})
    u = d.get("usage", {})
    pd = u.get("prompt_tokens_details") or {}
    return code, d, bool(msg.get("tool_calls")), [
        u.get("prompt_tokens"), u.get("completion_tokens"),
        pd.get("cached_tokens"), u.get("cache_write_tokens")]


print(f"{'모델':<18} {'API':<12} {'상태':<8} {'도구':<5} 토큰4열 [입력,출력,캐시읽기,캐시쓰기]")
print("-" * 92)

result = {}
for name, cfg in MODELS.items():
    key = os.environ.get(cfg["key_env"], "")
    if not key:
        print(f"{name:<18} {'-':<12} KEY없음"); continue
    base = (os.environ.get(cfg["base_url_env"]) if cfg.get("base_url_env")
            else "https://api.openai.com/v1")

    if cfg["provider"] == "anthropic":
        api = "messages"
        code, d, tool, cols = probe_anthropic(cfg, key)
    elif "api.openai.com" in base:
        api = "responses"
        code, d, tool, cols = probe_responses(cfg, key, base)
        if code != 200 or not tool:
            api = "chat(fallback)"
            code, d, tool, cols = probe_chat(cfg, key, base)
    else:
        api = "chat"
        code, d, tool, cols = probe_chat(cfg, key, base)

    ok = "OK" if code == 200 else str(code)
    print(f"{name:<18} {api:<12} {ok:<8} {'O' if tool else 'X':<5} {cols}")
    if code != 200:
        print(f"{'':<18} └ {str(d.get('error', {}).get('message', ''))[:110]}")
    result[name] = {"api": api, "http": code, "tool_calling": tool, "token_columns": cols}

(ROOT / "probe_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print("\n저장: systems/system_c_llm_wiki/agent/probe_result.json")
