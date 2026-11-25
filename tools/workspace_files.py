"""
title: Workspace files
description: Files inside one workspace directory only.
"""
import os

ROOT = os.path.realpath(os.environ.get("AI_WORKSPACE", "./workspace"))


def _safe(sub):
    p = os.path.realpath(os.path.join(ROOT, sub or ""))
    if p != ROOT and not p.startswith(ROOT + os.sep):
        raise ValueError("outside workspace")
    return p


async def _ok(ev, msg):
    if ev is None:
        return False
    try:
        r = await ev({"type": "confirmation", "data": {"title": "Approval needed", "message": msg}})
    except Exception:
        return False
    return r is True or (isinstance(r, dict) and r.get("confirmed") is True)


class Tools:
    def list_files(self, subpath: str = "") -> str:
        """List workspace files."""
        try:
            return "\n".join(sorted(os.listdir(_safe(subpath)))) or "(empty)"
        except Exception as e:
            return "Error: " + str(e)

    def read_file(self, path: str) -> str:
        """Read workspace file."""
        try:
            with open(_safe(path), "r", encoding="utf-8", errors="replace") as fh:
                return fh.read(20000)
        except Exception as e:
            return "Error: " + str(e)

    async def write_file(self, path: str, content: str, __event_call__=None) -> str:
        """Create workspace file."""
        try:
            p = _safe(path)
            if not await _ok(__event_call__, "Create the file '%s' in the workspace?" % path):
                return "Not approved by the user. Nothing was done."
            if os.path.exists(p):
                return "Error: file exists"
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(content)
            return "Saved " + path
        except Exception as e:
            return "Error: " + str(e)
