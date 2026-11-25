# Security

- **Exposure:** no public listener. Access over a Tailscale mesh only; HTTPS terminated by `tailscale serve`.
- **Approval gate:** state-changing and mailbox actions emit a confirmation event. The helper fails closed: no UI, an exception or no answer means refuse.
- **SSRF guard:** `web_page` blocks private, loopback, link-local, reserved and multicast addresses after DNS resolution.
- **Filesystem:** the workspace tool is confined by `realpath` prefix checks.
- **Secrets:** mailbox credentials are an app password in a file outside the repository (`secrets/` is git-ignored) and excluded from backups.
- **Browser:** dedicated profile, domain blocklist, passwords never typed.
- **Prompt injection:** page and mail content is data. Anything that changes state still needs the human approval above, regardless of what the content says.
