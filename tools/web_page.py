"""
title: Read web page
description: Fetch the text of a public web page (read only).
"""
import os
import re
import socket
import ipaddress
import ssl
import urllib.request
from urllib.parse import urlparse


def _public(host):
    for info in socket.getaddrinfo(host, None):
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


class Tools:
    def read_page(self, url: str) -> str:
        """Fetch a public web page as plain text."""
        try:
            u = urlparse(url)
            if u.scheme not in ("http", "https") or not u.hostname:
                return "Error: only http or https addresses"
            if not _public(u.hostname):
                return "Error: private or local addresses are blocked"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                raw = r.read(600000).decode(r.headers.get_content_charset() or "utf-8", "replace")
            raw = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", raw)
            text = re.sub(r"(?s)<[^>]+>", " ", raw)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:int(os.environ.get("AI_PAGE_CHARS", "1800"))] or "(no text found)"
        except Exception as e:
            return "Error: " + str(e)
