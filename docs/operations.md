# Operations

## Start-up
Task Scheduler runs `scripts/start-ai.ps1` at logon: Ollama, Open WebUI, then `warm.py`.

## Backups and rollback
- Before every change to tools, prompts or settings, copy `webui.db` to a dated file (`webui.db.bak-YYYYMMDD-<topic>`).
- Rollback: stop Open WebUI, copy the backup over `webui.db`, start again.
- Tool sources are versioned in this repository; the database holds the imported copy.

## Measuring
Per-step timings come from the Ollama server log (one line per model call). A web-grounded question is two model calls plus the tool round trips.

## Known limits
- Without a GPU, prompts are read at roughly 17 tokens/s, so output caps matter more than model choice.
- Open WebUI keeps the tool code from when a chat was opened; start a new chat after editing a tool.
