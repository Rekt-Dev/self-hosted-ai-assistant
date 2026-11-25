"""
title: Web search
description: Search the web.
"""
class Tools:
    def web_search(self, query: str) -> str:
        """Search the web. After searching, always open the best result with read_page and answer from the page. Never answer with links only."""
        try:
            from ddgs import DDGS
            rows = DDGS().text(query, max_results=5)
            return "\n".join("%s | %s | %s" % (r.get("title", ""), r.get("href", ""), (r.get("body", "") or "")[:300]) for r in rows) or "No results"
        except Exception as e:
            return "Error: " + str(e)
