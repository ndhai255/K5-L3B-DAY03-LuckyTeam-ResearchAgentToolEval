from __future__ import annotations

import ast
import operator
from typing import Any

# Các toán tử toán học an toàn
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Toán tử hoặc cú pháp không được hỗ trợ: {type(node).__name__}")


def calculate(expression: str) -> dict[str, Any]:
    """Tính toán biểu thức số học một cách an toàn."""
    if not expression or not expression.strip():
        return {"status": "error", "error": "Biểu thức trống"}

    expr = expression.strip()
    try:
        parsed = ast.parse(expr, mode="eval")
        result = _eval_node(parsed.body)
        return {
            "status": "ok",
            "expression": expr,
            "result": result,
        }
    except ZeroDivisionError:
        return {"status": "error", "error": "Lỗi chia cho số 0 (Division by zero)"}
    except Exception as e:
        return {"status": "error", "error": f"Lỗi tính toán: {str(e)}"}