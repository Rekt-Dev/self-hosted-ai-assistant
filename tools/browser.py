"""
title: Browser
description: Drive an authenticated browser session over CDP. Actions need user approval.
"""
from urllib.parse import urlparse

import os
CDP = os.environ.get("AI_CDP_URL", "http://127.0.0.1:9222")
import time
import asyncio

BLOCKED = ("facebook.com", "fb.com", "fb.me", "instagram.com", "messenger.com", "whatsapp.com", "whatsapp.net", "meta.com", "threads.net")
_state = {"i": 0}


def _host(url):
    return (urlparse(url).hostname or "").lower()


def _is(url, names):
    h = _host(url)
    return any(h == b or h.endswith("." + b) for b in names)


def _blocked(url):
    """Hard-blocked sites: no automation on social-media properties."""
    return _is(url, BLOCKED)


async def _ok(ev, msg):
    if ev is None:
        return False
    try:
        r = await ev({"type": "confirmation", "data": {"title": "Approval needed", "message": msg}})
    except Exception:
        return False
    return r is True or (isinstance(r, dict) and r.get("confirmed") is True)


async def _page(pw):
    b = await pw.chromium.connect_over_cdp(CDP)
    pages = [p for c in b.contexts for p in c.pages if not p.url.startswith("devtools")]
    if not pages:
        pages = [await b.contexts[0].new_page()]
    i = min(_state["i"], len(pages) - 1)
    return pages[i], pages


async def _text(p, n=3000):
    t = await p.evaluate("document.body ? document.body.innerText : ''")
    return ("%s | %s\n%s" % (await p.title(), p.url, " ".join(t.split())))[:n]


class Tools:
    async def browser_tabs(self) -> str:
        """List open browser tabs."""
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as pw:
                p, pages = await _page(pw)
                return "\n".join("%d | %s | %s" % (i, await q.title(), q.url) for i, q in enumerate(pages))
        except Exception as e:
            return "Error: " + str(e)

    async def browser_switch(self, index: int) -> str:
        """Switch to a tab by number."""
        _state["i"] = int(index)
        return "Switched to tab %d" % int(index)

    async def browser_open(self, url: str) -> str:
        """Open a web address in the current tab and read it."""
        from playwright.async_api import async_playwright
        try:
            if _blocked(url):
                return "Blocked: automation on social-media sites is not allowed."
            async with async_playwright() as pw:
                p, pages = await _page(pw)
                await p.goto(url, wait_until="domcontentloaded", timeout=30000)
                return await _text(p)
        except Exception as e:
            return "Error: " + str(e)

    async def browser_read(self) -> str:
        """Read the current page: text and clickable items."""
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as pw:
                p, pages = await _page(pw)
                if _blocked(p.url):
                    return "Blocked: automation on social-media sites is not allowed."
                items = await p.evaluate("Array.from(document.querySelectorAll('a,button,input,[role=button]')).slice(0,40).map(e=>(e.innerText||e.value||e.placeholder||e.ariaLabel||'').trim().slice(0,40)).filter(Boolean).join(' | ')")
                return (await _text(p, 2500)) + "\nClickable: " + items
        except Exception as e:
            return "Error: " + str(e)

    async def browser_click(self, text: str, __event_call__=None) -> str:
        """Click the item with this visible text. Needs approval."""
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as pw:
                p, pages = await _page(pw)
                if _blocked(p.url):
                    return "Blocked: automation on social-media sites is not allowed."
                if not await _ok(__event_call__, "Click '%s' on %s ?" % (text, p.url)):
                    return "Not approved by the user. Nothing was done."
                await p.get_by_text(text, exact=False).first.click(timeout=10000)
                await p.wait_for_timeout(1500)
                return await _text(p, 2000)
        except Exception as e:
            return "Error: " + str(e)

    async def browser_type(self, field: str, value: str, __event_call__=None) -> str:
        """Type into a field (label or placeholder). Needs approval. Never passwords."""
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as pw:
                p, pages = await _page(pw)
                if _blocked(p.url):
                    return "Blocked: automation on social-media sites is not allowed."
                if not await _ok(__event_call__, "Type '%s' into '%s' on %s ?" % (value[:120], field, p.url)):
                    return "Not approved by the user. Nothing was done."
                loc = p.get_by_label(field).first
                if await loc.count() == 0:
                    loc = p.get_by_placeholder(field).first
                if (await loc.get_attribute("type") or "").lower() == "password":
                    return "Refused: the model never types passwords."
                await loc.fill(value, timeout=10000)
                return "Typed."
        except Exception as e:
            return "Error: " + str(e)

    async def browser_press(self, key: str, __event_call__=None) -> str:
        """Press a key (for example Enter). Needs approval."""
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as pw:
                p, pages = await _page(pw)
                if _blocked(p.url):
                    return "Blocked: automation on social-media sites is not allowed."
                if not await _ok(__event_call__, "Press '%s' on %s ?" % (key, p.url)):
                    return "Not approved by the user. Nothing was done."
                await p.keyboard.press(key)
                await p.wait_for_timeout(1500)
                return await _text(p, 2000)
        except Exception as e:
            return "Error: " + str(e)
