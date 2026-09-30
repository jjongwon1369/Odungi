import json, os, ssl, certifi, urllib.request, urllib.error, pathlib

CTX = ssl.create_default_context(cafile=certifi.where())

ROOT = pathlib.Path(__file__).parent
models = json.loads((ROOT / "models.json").read_text())
PROMPT = "위키에 어떤 페이지가 있는지 list_pages 도구로 확인해줘."
DESC = "위키 페이지 목록을 반환한다"

def post(url, headers, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read() or b"{}")
        except Exception: return e.code, {}
    except Exception as e:
        return 0, {"error": {"message": str(e)}}

for name, cfg in models.items():
    key = os.environ.get(cfg["key_env"], "")
    if not key:
        print(f"{name:18} KEY 없음 ({cfg['key_env']})"); continue
    rc = cfg.get("reasoning_config") or {}
    if cfg["provider"] == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        h = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        pl = {"model": cfg["model_id"], "max_tokens": 1024,
              "tools": [{"name": "list_pages", "description": DESC,
                         "input_schema": {"type": "object", "properties": {}}}],
              "messages": [{"role": "user", "content": PROMPT}], **rc}
        code, d = post(url, h, pl)
        tool = any(b.get("type") == "tool_use" for b in d.get("content", [])) if code == 200 else False
        u = d.get("usage", {}) if code == 200 else {}
        cols = [u.get("input_tokens"), u.get("output_tokens"),
                u.get("cache_read_input_tokens"), u.get("cache_creation_input_tokens")]
    else:
        # models.json 의 base_url 만 쓴다. 폴백 금지 — 다른 provider 키가
        # api.openai.com 으로 전송될 수 있다. (#23)
        base = cfg.get("base_url")
        if not base:
            print(f"{name:18} base_url없음 — models.json 확인"); continue
        url = base.rstrip("/") + "/chat/completions"
        h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        pl = {"model": cfg["model_id"], "messages": [{"role": "user", "content": PROMPT}],
              "tools": [{"type": "function", "function": {"name": "list_pages", "description": DESC,
                         "parameters": {"type": "object", "properties": {}}}}], **rc}
        code, d = post(url, h, pl)
        msg = (d.get("choices") or [{}])[0].get("message", {}) if code == 200 else {}
        tool = bool(msg.get("tool_calls"))
        u = d.get("usage", {}) if code == 200 else {}
        pd = u.get("prompt_tokens_details") or {}
        cols = [u.get("prompt_tokens"), u.get("completion_tokens"),
                pd.get("cached_tokens"), u.get("cache_write_tokens")]
    st = "OK" if code == 200 else f"HTTP {code} {str(d.get('error', {}).get('message', ''))[:60]}"
    print(f"{name:18} {st:34} 도구={'O' if tool else 'X'}  토큰4열={cols}")
