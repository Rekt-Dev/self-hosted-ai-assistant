"""
title: Email (read and draft only)
description: Read mail and save drafts in configured mailboxes. Never sends.
"""
import imaplib, json, os, email
from email.message import EmailMessage
from email.header import decode_header, make_header

CFG = os.environ.get("AI_EMAIL_CFG", "./secrets/email.json")


def _conn(account):
    if not os.path.exists(CFG):
        raise RuntimeError("Email is not configured yet")
    cfg = json.load(open(CFG, encoding="utf-8"))["accounts"]
    if account not in cfg:
        raise RuntimeError("Unknown account. Use one of: " + ", ".join(cfg))
    c = cfg[account]
    if not c.get("app_password"):
        raise RuntimeError("Account '%s' has no app password yet" % account)
    m = imaplib.IMAP4_SSL(c.get("imap_host", "imap.gmail.com"))
    m.login(c["user"], c["app_password"])
    return m, c


async def _ok(ev, msg):
    """Ask the user for approval. Fails closed: no popup or no answer = refuse."""
    if ev is None:
        return False
    try:
        r = await ev({"type": "confirmation", "data": {"title": "Approval needed", "message": msg}})
    except Exception:
        return False
    return r is True or (isinstance(r, dict) and r.get("confirmed") is True)


def _h(v):
    return str(make_header(decode_header(v or "")))


class Tools:
    async def email_list(self, account: str = "primary", count: int = 5, __event_call__=None) -> str:
        """List newest emails. Account: a name from the email config."""
        if not await _ok(__event_call__, "Open mailbox '%s' and list the newest %s emails?" % (account, count)):
            return "Not approved by the user. Nothing was done."
        try:
            m, c = _conn(account)
            m.select("INBOX", readonly=True)
            _, d = m.search(None, "ALL")
            out = []
            for i in d[0].split()[-int(count):][::-1]:
                _, x = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                h = email.message_from_bytes(x[0][1])
                out.append("%s | %s | %s | %s" % (i.decode(), _h(h["From"]), _h(h["Subject"]), h["Date"]))
            m.logout()
            return "\n".join(out) or "Inbox empty"
        except Exception as e:
            return "Error: " + str(e)

    async def email_read(self, id: str, account: str = "primary", __event_call__=None) -> str:
        """Read one email by id."""
        if not await _ok(__event_call__, "Read email %s in mailbox '%s'?" % (id, account)):
            return "Not approved by the user. Nothing was done."
        try:
            m, c = _conn(account)
            m.select("INBOX", readonly=True)
            _, x = m.fetch(id.encode(), "(BODY.PEEK[])")
            msg = email.message_from_bytes(x[0][1])
            body = ""
            for p in msg.walk():
                if p.get_content_type() == "text/plain":
                    body = p.get_payload(decode=True).decode(p.get_content_charset() or "utf-8", "replace")
                    break
            m.logout()
            return body[:4000] or "(no text body)"
        except Exception as e:
            return "Error: " + str(e)

    async def email_search(self, text: str, account: str = "primary", __event_call__=None) -> str:
        """Search subjects for text, last results."""
        if not await _ok(__event_call__, "Search mailbox '%s' for '%s'?" % (account, text)):
            return "Not approved by the user. Nothing was done."
        try:
            m, c = _conn(account)
            m.select("INBOX", readonly=True)
            _, d = m.search(None, "SUBJECT", '"%s"' % text.replace('"', ""))
            out = []
            for i in d[0].split()[-8:][::-1]:
                _, x = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                h = email.message_from_bytes(x[0][1])
                out.append("%s | %s | %s | %s" % (i.decode(), _h(h["From"]), _h(h["Subject"]), h["Date"]))
            m.logout()
            return "\n".join(out) or "No match"
        except Exception as e:
            return "Error: " + str(e)

    async def email_draft(self, to: str, subject: str, body: str, account: str = "primary", __event_call__=None) -> str:
        """Save a draft. NOT sent."""
        if not await _ok(__event_call__, "Save a DRAFT (not sent) to %s in '%s' with subject '%s'?" % (to, account, subject)):
            return "Not approved by the user. Nothing was done."
        try:
            m, c = _conn(account)
            msg = EmailMessage()
            msg["To"], msg["Subject"], msg["From"] = to, subject, c["user"]
            msg.set_content(body)
            m.append("[Gmail]/Drafts", r"\Draft", None, msg.as_bytes())
            m.logout()
            return "Draft saved (not sent)"
        except Exception as e:
            return "Error: " + str(e)
