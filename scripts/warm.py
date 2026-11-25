"""Pre-reads the fixed start of every chat (system prompt + tool schemas) so the first real message is fast."""
import json, os, sqlite3, sys, urllib.request

ROOT = os.environ.get("AI_ROOT", r"D:\AI")
DB = os.path.join(ROOT, "webui-data", "webui.db")
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen3:30b-a3b-instruct-2507-q4_K_M"

c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
params, meta = c.execute("select params, meta from model where id=?", (MODEL,)).fetchone()
system = json.loads(params)["system"]
tools = []
for tid in json.loads(meta)["toolIds"]:
    for f in json.loads(c.execute("select specs from tool where id=?", (tid,)).fetchone()[0]):
        tools.append({"type": "function", "function": f})
body = {"model": MODEL, "stream": False, "tools": tools, "keep_alive": -1,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": "hi"}],
        "options": {"num_predict": 1}}
req = urllib.request.Request("http://127.0.0.1:11434/api/chat", json.dumps(body).encode(),
                             {"Content-Type": "application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=900).read())
print("warm-up done: read", r.get("prompt_eval_count"), "tokens in", round(r.get("total_duration", 0) / 1e9, 1), "s")
