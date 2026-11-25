# Tools

All tools are single Python files in the Open WebUI tool format (`class Tools`). Environment variables:

| Variable | Used by | Default |
|----------|---------|---------|
| `AI_WORKSPACE` | workspace_files | `./workspace` |
| `AI_EMAIL_CFG` | email_draft | `./secrets/email.json` |
| `AI_TZ` | calc_time | `UTC` |
| `AI_PAGE_CHARS` | web_page | `1800` |
| `AI_CDP_URL` | browser | `http://127.0.0.1:9222` |

## web_page
Resolves the host first and refuses private, loopback, link-local, reserved and multicast addresses (SSRF guard).
Strips script/style/noscript, collapses whitespace, caps the output.

## workspace_files
Every path is resolved with `realpath` and must stay inside the workspace root. Writing creates new files only and requires approval.

## email_draft
IMAP with `BODY.PEEK` and read-only mailbox selection, so reading never changes flags. Drafts are appended to the Drafts folder; the tool never sends.
Each call asks for approval first. Sending (reply and compose) is planned behind the same approval gate.

## browser
Playwright over CDP against a dedicated, logged-in browser profile. Click, type and key press need approval.
Social-media domains are hard-blocked and password fields are refused.

## calc_time
Arithmetic is evaluated from the AST with an operator whitelist and an exponent limit; no `eval`.
