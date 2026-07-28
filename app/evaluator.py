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
    print(json.dumps({'ok': all(item['passed'] for item in checks), 'checks': checks, 'stdout': output.getvalue()}, ensure_ascii=False))
except Exception as error:
    print(json.dumps({'ok': False, 'error': f'{type(error).__name__}: {error}', 'checks': [], 'stdout': output.getvalue()}, ensure_ascii=False))
"""


def normalize(value: Any) -> str:
    return str(value or "").strip().casefold()


def _check_source_requirements(tree: ast.AST, tests: list[dict]) -> str | None:
    for test in tests:
        if test.get("kind") != "source":
            continue
        if test.get("requires") == "unpacking":
            name = test.get("name")
            function = test.get("function")
            scope: ast.AST = tree
            if function:
                target_function = next(
                    (
                        node
                        for node in ast.walk(tree)
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and node.name == function
                    ),
                    None,
                )
                scope = ast.Module(
                    body=target_function.body if target_function else [], type_ignores=[]
                )
            has_unpacking = any(
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Name)
                and node.value.id == name
                and any(isinstance(target, (ast.Tuple, ast.List)) for target in node.targets)
                for node in ast.walk(scope)
            )
            uses_index = any(isinstance(node, ast.Subscript) for node in ast.walk(scope))
            if function:
                unpacking_values = {
                    id(node.value)
                    for node in ast.walk(scope)
                    if isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == name
                    and any(isinstance(target, (ast.Tuple, ast.List)) for target in node.targets)
                }
                uses_parameter_elsewhere = any(
                    isinstance(node, ast.Name)
                    and node.id == name
                    and id(node) not in unpacking_values
                    for node in ast.walk(scope)
                )
            else:
                uses_parameter_elsewhere = False
            if not has_unpacking or uses_index or uses_parameter_elsewhere:
                return "В этом задании нужна распаковка последовательности без индексов."
    return None


def run_code(source: str, tests: list[dict]) -> dict:
    """Выполняет небольшой фрагмент в отдельном Python-процессе с лимитом времени."""
    if len(source) > 5_000:
        return {
            "correct": False,
            "message": "Решение слишком длинное для этого задания.",
            "stdout": "",
            "stderr": "",
            "error": "Решение слишком длинное для этого задания.",
            "timed_out": False,
        }
    try:
        tree = ast.parse(source)
        SafetyVisitor().visit(tree)
    except (SyntaxError, ValueError) as error:
        error_text = f"{type(error).__name__}: {error}"
        return {
            "correct": False,
            "message": str(error),
            "stdout": "",
            "stderr": "",
            "error": error_text,
            "timed_out": False,
        }

    requirement_error = _check_source_requirements(tree, tests)
    if requirement_error:
        return {
            "correct": False,
            "message": requirement_error,
            "checks": [],
            "stdout": "",
            "stderr": "",
            "error": requirement_error,
            "timed_out": False,
        }

    runtime_tests = [test for test in tests if test.get("kind") != "source"]
    encoded_code = base64.b64encode(source.encode("utf-8")).decode("ascii")
    encoded_tests = base64.b64encode(
        json.dumps(runtime_tests, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")
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
        error_text = "TimeoutError: Код выполнялся слишком долго. Проверь условие цикла."
        return {
            "correct": False,
            "message": error_text,
            "stdout": "",
            "stderr": "",
            "error": error_text,
            "timed_out": True,
        }

    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {
            "correct": False,
            "message": "Не удалось проверить решение. Попробуй упростить код.",
            "stdout": "",
            "stderr": result.stderr,
            "error": "Не удалось проверить решение. Попробуй упростить код.",
            "timed_out": False,
        }

    run_result = {
        "stdout": payload.get("stdout", ""),
        "stderr": result.stderr,
        "error": payload.get("error"),
        "timed_out": False,
    }
    if payload.get("error"):
        return {
            "correct": False,
            "message": f"Почти: {payload['error']}",
            "checks": [],
            **run_result,
        }
    if payload.get("ok"):
        return {
            "correct": True,
            "message": "Все тесты пройдены!",
            "checks": payload["checks"],
            **run_result,
        }
    return {
        "correct": False,
        "message": "Не все тесты прошли. Сверь результат с условием.",
        "checks": payload.get("checks", []),
        **run_result,
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
