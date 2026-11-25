"""
title: Calc and time
description: Exact math and the current time.
"""
import ast, os, operator as op, math
from datetime import datetime
from zoneinfo import ZoneInfo

_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
        ast.Pow: op.pow, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
        ast.USub: op.neg, ast.UAdd: op.pos}


def _ev(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
        a, b = _ev(n.left), _ev(n.right)
        if isinstance(n.op, ast.Pow) and abs(b) > 1000:
            raise ValueError("exponent too large")
        return _OPS[type(n.op)](a, b)
    if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
        return _OPS[type(n.op)](_ev(n.operand))
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "sqrt" and len(n.args) == 1:
        return math.sqrt(_ev(n.args[0]))
    raise ValueError("unsupported expression")


class Tools:
    def calculate(self, expression: str) -> str:
        """Exact arithmetic. Use for any math. Example: 5753*1600037"""
        try:
            return str(_ev(ast.parse(expression.replace(",", "").strip(), mode="eval").body))
        except Exception as e:
            return "Error: " + str(e)

    def now(self) -> str:
        """Current date and time in the configured time zone."""
        return datetime.now(ZoneInfo(os.environ.get("AI_TZ", "UTC"))).strftime("%a %d-%m-%Y %H:%M")
