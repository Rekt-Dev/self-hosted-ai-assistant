# Architecture

```
client browser --HTTPS (tailscale serve)--> Open WebUI :8080 --> Ollama :11434 --> models
                                                         |
                                                         +--> tools (Python, run inside Open WebUI)
                                                                 |- web_search / web_page  (outbound HTTPS)
                                                                 |- workspace_files        (one directory)
                                                                 |- email_draft            (IMAP)
                                                                 |- browser                (CDP, 127.0.0.1)
                                                                 `- calc_time
```

## Models

- Default: Qwen3-30B-A3B instruct (MoE, 4-bit). Only about 3B parameters are active per token, which makes a 30B model usable without a GPU.
- Alternate: gpt-oss-20b.
- One model resident at a time (`OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=-1`), context 49,152 tokens.

## Latency model

Prompt processing, not generation, dominates: every tool result is fed back into the prompt and re-read.
Three measures bring a web-grounded question from about 6 minutes to under 1 minute (47 s measured):

1. `scripts/warm.py` pre-reads the fixed system prompt and tool schemas once, so the first message does not pay for them.
2. Tool output is capped (`web_page` 1,800 characters, search snippets 300).
3. Background generations (titles, tags, follow-ups, autocomplete, query generation) are disabled.

A rule in the search tool description (open the best result, never answer with links only) avoids link-only answers.

## Network

Open WebUI binds on all interfaces on the host, which is only reachable over the tailnet; HTTPS comes from `tailscale serve`.
The browser tool talks to a local browser instance on `127.0.0.1` over the Chrome DevTools Protocol.
