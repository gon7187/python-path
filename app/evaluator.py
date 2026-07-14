"""Проверка ответов и безопасный мини-раннер учебного кода."""

from __future__ import annotations

import ast
import base64
import json
import subprocess
import sys
from typing import Any

FORBIDDEN_NODES = (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.AsyncFunctionDef)
FORBIDDEN_NAMES = {
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "exit",
    "help",
    "input",
    "open",
    "quit",
    "vars",
    "globals",
    "locals",
    "getattr",
    "setattr",
    "delattr",
}


class SafetyVisitor(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, FORBIDDEN_NODES):
            raise ValueError("Этот учебный редактор не поддерживает импорт и системные операции.")
        return super().visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in FORBIDDEN_NAMES or node.id.startswith("__"):
            raise ValueError("В учебном редакторе нельзя использовать системные функции.")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("_"):
            raise ValueError("Служебные атрибуты недоступны в учебном редакторе.")
        self.generic_visit(node)


RUNNER = r"""
import base64
import builtins
import contextlib
import io
import json

SAFE_BUILTINS = {
    '__build_class__': builtins.__build_class__, 'abs': abs, 'all': all, 'any': any,
    'bool': bool, 'dict': dict, 'enumerate': enumerate, 'float': float, 'int': int,
    'len': len, 'list': list, 'max': max, 'min': min, 'print': print, 'range': range,
    'round': round, 'set': set, 'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple,
    'zip': zip,
}
source = base64.b64decode(CODE).decode('utf-8')
tests = json.loads(base64.b64decode(TESTS).decode('utf-8'))
namespace = {'__builtins__': SAFE_BUILTINS, '__name__': '__learner__'}
output = io.StringIO()
try:
    with contextlib.redirect_stdout(output):
        exec(compile(source, '<learner-code>', 'exec'), namespace, namespace)
    checks = []
    for test in tests:
        if test['kind'] == 'stdout':
            actual = output.getvalue().strip()
        else:
            actual = eval(test['call'], namespace, namespace)
        checks.append({'passed': actual == test['expected'], 'actual': repr(actual), 'expected': repr(test['expected'])})
    print(json.dumps({'ok': all(item['passed'] for item in checks), 'checks': checks}, ensure_ascii=False))
except Exception as error:
    print(json.dumps({'ok': False, 'error': f'{type(error).__name__}: {error}', 'checks': []}, ensure_ascii=False))
"""


def normalize(value: Any) -> str:
    return str(value or "").strip().casefold()


def run_code(source: str, tests: list[dict]) -> dict:
    """Выполняет небольшой фрагмент в отдельном Python-процессе с лимитом времени."""
    if len(source) > 5_000:
        return {"correct": False, "message": "Решение слишком длинное для этого задания."}
    try:
        SafetyVisitor().visit(ast.parse(source))
    except (SyntaxError, ValueError) as error:
        return {"correct": False, "message": str(error)}

    encoded_code = base64.b64encode(source.encode("utf-8")).decode("ascii")
    encoded_tests = base64.b64encode(json.dumps(tests, ensure_ascii=False).encode("utf-8")).decode(
        "ascii"
    )
    program = RUNNER.replace("CODE", repr(encoded_code)).replace("TESTS", repr(encoded_tests))
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-c", program],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"correct": False, "message": "Код выполнялся слишком долго. Проверь условие цикла."}

    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {
            "correct": False,
            "message": "Не удалось проверить решение. Попробуй упростить код.",
        }

    if payload.get("error"):
        return {"correct": False, "message": f"Почти: {payload['error']}", "checks": []}
    if payload.get("ok"):
        return {"correct": True, "message": "Все тесты пройдены!", "checks": payload["checks"]}
    return {
        "correct": False,
        "message": "Не все тесты прошли. Сверь результат с условием.",
        "checks": payload.get("checks", []),
    }


def evaluate(question: dict, answer: Any) -> dict:
    """Возвращает единый результат для выбора, текста и кода."""
    kind = question["kind"]
    if kind == "choice":
        correct = normalize(answer) == normalize(question["answer"])
        return {"correct": correct, "message": question["explanation"]}
    if kind == "input":
        correct = normalize(answer) in {normalize(item) for item in question["answers"]}
        return {"correct": correct, "message": question["explanation"]}
    if kind == "code":
        result = run_code(str(answer or ""), question["tests"])
        result["explanation"] = question["explanation"]
        return result
    raise ValueError(f"Неизвестный тип задания: {kind}")
