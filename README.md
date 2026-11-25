# Self-hosted AI assistant

A private AI assistant that runs on infrastructure you control: local models served by Ollama,
Open WebUI as the front end, and a set of function-calling tools for web research, browser automation,
files, mail and engineering work. Reachable only over a Tailscale mesh with HTTPS.

Status: in development.

## Stack

| Layer | Component |
|-------|-----------|
| Inference | Ollama: Qwen3-30B-A3B (MoE, default), gpt-oss-20b |
| Front end | Open WebUI: chat history, voice chat, mobile access |
| Voice | Whisper (speech-to-text), neural TTS through a local OpenAI-compatible endpoint |
| Access | Tailscale mesh, HTTPS via `tailscale serve`, no public exposure |
| Tools | Open WebUI function-calling tools (this repository, `tools/`) |
| Startup | Task Scheduler runs `scripts/start-ai.ps1` at logon: services, then model warm-up |

## Tools

| Tool | What it does | Approval |
|------|--------------|----------|
| `web_search` | Web search (top 5 results, 300-character snippets) | no |
| `web_page` | Fetch a public page as text, capped at 1,800 characters, private addresses blocked | no |
| `workspace_files` | List/read files in one workspace directory; create new files | create only |
| `email_draft` | List, read and search mailboxes (IMAP, read-only select); save drafts | every call |
| `browser` | Drive a logged-in browser over CDP: tabs, open, read, click, type, key press | click/type/key |
| `calc_time` | Exact arithmetic (AST-evaluated, no `eval`) and current time | no |

Engineering help (code generation, debugging, code review) is plain chat with the model; code never leaves the machine.

Details: [docs/architecture.md](docs/architecture.md), [docs/tools.md](docs/tools.md),
[docs/security.md](docs/security.md), [docs/operations.md](docs/operations.md).

## Design rules

- Every state-changing action goes through a confirmation event; no popup or no answer means refuse (fail closed).
- Hard domain blocklist for social-media sites; the browser tool refuses password fields.
- Tool output is capped before it reaches the model: on CPU inference, prompt length is the dominant cost.
- Secrets live outside the repository and outside backups.

## Quick start

```powershell
# 1. Install Ollama and Open WebUI (uv/pip) under one root directory, pull the models
ollama pull qwen3:30b-a3b-instruct-2507-q4_K_M
ollama pull gpt-oss:20b

# 2. Import the files in tools/ as Open WebUI tools and attach them to the model

# 3. Optional: mailbox access
Copy-Item config\email.json.template D:\AI\secrets\email.json   # fill user, app password, IMAP host

# 4. Start everything
.\scripts\start-ai.ps1 -Root D:\AI
```

## Layout

```
tools/     Open WebUI tool sources (one file per tool)
scripts/   start-ai.ps1 (service start + warm-up), warm.py (prompt pre-read)
config/    email.json.template
docs/      architecture, tools, security, operations
```
