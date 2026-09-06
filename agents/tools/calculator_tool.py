import ast
import operator as op

from langchain_core.tools import tool


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Div) and right == 0:
            raise ValueError("Division by zero is not allowed.")

        return _ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](
            _evaluate(node.operand)
        )

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function.")

        function_name = node.func.id

        if function_name == "average":
            return _average(node)

        if function_name == "percentage":
            return _percentage(node)

        if function_name == "ratio":
            return _ratio(node)

        raise ValueError(f"Unsupported function: {function_name}")

    raise ValueError("Unsupported expression.")


def _get_arguments(node: ast.Call) -> list[float]:
    if node.keywords:
        raise ValueError("Keyword arguments are not supported.")

    if not node.args:
        raise ValueError("At least one argument is required.")

    return [_evaluate(argument) for argument in node.args]


def _average(node: ast.Call) -> float:
    values = _get_arguments(node)

    return sum(values) / len(values)


def _percentage(node: ast.Call) -> float:
    values = _get_arguments(node)

    if len(values) != 2:
        raise ValueError(
            "percentage() requires exactly two arguments: new_value, old_value."
        )

    new_value, old_value = values

    if old_value == 0:
        raise ValueError("Cannot calculate percentage from zero.")

    return ((new_value - old_value) / old_value) * 100


def _ratio(node: ast.Call) -> float:
    values = _get_arguments(node)

    if len(values) != 2:
        raise ValueError(
            "ratio() requires exactly two arguments: numerator, denominator."
        )

    numerator, denominator = values

    if denominator == 0:
        raise ValueError("Ratio denominator cannot be zero.")

    return numerator / denominator


@tool
def calculator(expression: str) -> float:
    """
    Perform mathematical calculations.

    Supports arithmetic operations such as addition, subtraction,
    multiplication, division, modulo, exponentiation, and parentheses.

    Also supports:
    - average(value1, value2, ...)
    - percentage(new_value, old_value)
    - ratio(numerator, denominator)
    """

    expression = expression.strip()

    if not expression:
        raise ValueError("Expression cannot be empty.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree)

    except SyntaxError as exc:
        raise ValueError("Invalid mathematical expression.") from exc

    if not isinstance(result, (int, float)):
        raise ValueError("Calculation did not produce a numeric result.")

    return result