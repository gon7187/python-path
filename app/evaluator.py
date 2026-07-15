"""Проверка ответов и безопасный мини-раннер учебного кода."""

from __future__ import annotations

import ast
import base64
import json
import subprocess
import sys
from typing import Any

FORBIDDEN_NODES = (ast.Global, ast.Nonlocal)
SAFE_IMPORT_ROOTS = {
    "asyncio",
    "bisect",
    "collections",
    "csv",
    "datetime",
    "dataclasses",
    "decimal",
    "functools",
    "heapq",
    "itertools",
    "json",
    "math",
    "enum",
    "pathlib",
    "random",
    "re",
    "statistics",
    "typing",
}
SAFE_DUNDER_ATTRIBUTES = {
    "__add__",
    "__call__",
    "__contains__",
    "__enter__",
    "__eq__",
    "__exit__",
    "__getitem__",
    "__hash__",
    "__init__",
    "__iter__",
    "__len__",
    "__next__",
    "__repr__",
    "__setitem__",
    "__str__",
}
SAFE_DUNDER_NAMES = {"__name__"}
FORBIDDEN_ATTRIBUTES = {
    "create_subprocess_exec",
    "create_subprocess_shell",
    "get_event_loop",
    "new_event_loop",
    "open_connection",
    "run_in_executor",
    "start_server",
    "to_thread",
}
FORBIDDEN_NAMES = {
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "exit",
    "help",
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
        if node.id in FORBIDDEN_NAMES or (
            node.id.startswith("__") and node.id not in SAFE_DUNDER_NAMES
        ):
            raise ValueError("В учебном редакторе нельзя использовать системные функции.")

    def visit_Import(self, node: ast.Import) -> None:
        roots = {item.name.split(".", 1)[0] for item in node.names}
        self._check_imports(roots)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level or not node.module:
            raise ValueError("Относительные импорты недоступны в учебном редакторе.")
        self._check_imports({node.module.split(".", 1)[0]})

    @staticmethod
    def _check_imports(roots: set[str]) -> None:
        blocked = roots - SAFE_IMPORT_ROOTS
        if blocked:
            allowed = ", ".join(sorted(SAFE_IMPORT_ROOTS))
            raise ValueError(
                f"Модуль {', '.join(sorted(blocked))} пока недоступен. Разрешены: {allowed}."
            )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in FORBIDDEN_ATTRIBUTES:
            raise ValueError("Сетевые, процессные и системные операции недоступны.")
        if node.attr.startswith("_") and node.attr not in SAFE_DUNDER_ATTRIBUTES:
            raise ValueError("Служебные атрибуты недоступны в учебном редакторе.")
        self.generic_visit(node)


RUNNER = r"""
import asyncio as real_asyncio
import ast
import base64
import builtins
import contextlib
import dataclasses as real_dataclasses
import enum as real_enum
import io
import json
import os
import tempfile
import types
import typing as real_typing

SAFE_BUILTINS = {
    '__build_class__': builtins.__build_class__, 'abs': abs, 'all': all, 'any': any,
    'bin': bin, 'bool': bool, 'callable': callable, 'classmethod': classmethod,
    'chr': chr, 'complex': complex, 'dict': dict, 'divmod': divmod,
    'enumerate': enumerate, 'filter': filter, 'float': float, 'format': format,
    'frozenset': frozenset, 'hex': hex, 'id': id, 'int': int, 'isinstance': isinstance,
    'iter': iter, 'len': len, 'list': list,
    'map': map, 'max': max, 'min': min, 'object': object, 'ord': ord, 'pow': pow,
    'next': next, 'print': print, 'property': property,
    'range': range, 'repr': repr, 'reversed': reversed, 'round': round, 'set': set,
    'slice': slice, 'sorted': sorted, 'staticmethod': staticmethod, 'str': str,
    'sum': sum, 'super': super, 'tuple': tuple, 'type': type, 'zip': zip,
    'EOFError': EOFError, 'Exception': Exception, 'KeyError': KeyError,
    'RuntimeError': RuntimeError, 'StopIteration': StopIteration, 'TypeError': TypeError,
    'ValueError': ValueError, 'ZeroDivisionError': ZeroDivisionError,
}
source = base64.b64decode(CODE).decode('utf-8')
tests = json.loads(base64.b64decode(TESTS).decode('utf-8'))
inputs = json.loads(base64.b64decode(INPUTS).decode('utf-8'))
namespace = {'__builtins__': SAFE_BUILTINS, '__name__': '__learner__'}
output = io.StringIO()
input_values = iter(inputs)
virtual_directory = tempfile.TemporaryDirectory(prefix='python-path-')
real_import = builtins.__import__

SAFE_IMPORT_ROOTS = {
    'asyncio', 'bisect', 'collections', 'csv', 'dataclasses', 'datetime', 'decimal',
    'enum', 'functools', 'heapq', 'itertools', 'json', 'math', 'pathlib', 'random',
    're', 'statistics', 'typing',
}

def virtual_path(filename):
    raw = os.fspath(filename)
    if os.path.isabs(raw):
        raise ValueError('Используй относительный путь внутри виртуальной папки.')
    normalized = os.path.normpath(raw)
    if normalized == '..' or normalized.startswith('..' + os.sep):
        raise ValueError('Учебный файл должен находиться внутри виртуальной папки.')
    return os.path.join(virtual_directory.name, normalized)

class VirtualPath:
    def __init__(self, *parts):
        self._logical = os.path.join(*(os.fspath(part) for part in parts)) if parts else '.'
        virtual_path(self._logical)

    def __truediv__(self, child):
        return VirtualPath(self._logical, child)

    def __str__(self):
        return self._logical

    @property
    def name(self):
        return os.path.basename(self._logical)

    @property
    def suffix(self):
        return os.path.splitext(self.name)[1]

    @property
    def parent(self):
        return VirtualPath(os.path.dirname(self._logical) or '.')

    def exists(self):
        return os.path.exists(virtual_path(self._logical))

    def mkdir(self, parents=False, exist_ok=False):
        path = virtual_path(self._logical)
        if parents:
            os.makedirs(path, exist_ok=exist_ok)
        else:
            os.mkdir(path)

    def read_text(self, encoding='utf-8'):
        with builtins.open(virtual_path(self._logical), encoding=encoding) as file:
            return file.read()

    def write_text(self, data, encoding='utf-8'):
        path = virtual_path(self._logical)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with builtins.open(path, 'w', encoding=encoding) as file:
            return file.write(data)

SAFE_MODULE_OVERRIDES = {
    'asyncio': types.SimpleNamespace(
        create_task=real_asyncio.create_task,
        gather=real_asyncio.gather,
        run=real_asyncio.run,
        sleep=real_asyncio.sleep,
        wait_for=real_asyncio.wait_for,
    ),
    'dataclasses': types.SimpleNamespace(
        dataclass=real_dataclasses.dataclass,
        field=real_dataclasses.field,
    ),
    'enum': types.SimpleNamespace(Enum=real_enum.Enum),
    'pathlib': types.SimpleNamespace(Path=VirtualPath),
    'typing': types.SimpleNamespace(
        Any=real_typing.Any,
        Callable=real_typing.Callable,
        Iterable=real_typing.Iterable,
        Iterator=real_typing.Iterator,
        Literal=real_typing.Literal,
        Optional=real_typing.Optional,
        Protocol=real_typing.Protocol,
        TypeVar=real_typing.TypeVar,
        Union=real_typing.Union,
    ),
}

def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split('.', 1)[0]
    if level or root not in SAFE_IMPORT_ROOTS:
        raise ImportError(f'Модуль {root} недоступен в учебном редакторе.')
    if root in SAFE_MODULE_OVERRIDES:
        return SAFE_MODULE_OVERRIDES[root]
    return real_import(name, globals, locals, fromlist, level)

def virtual_open(filename, mode='r', encoding=None, newline=None):
    if not isinstance(filename, str) or os.path.isabs(filename):
        raise ValueError('Используй простое относительное имя учебного файла.')
    normalized = os.path.normpath(filename)
    if any(flag in mode for flag in ('b', '+')) or not set(mode) <= set('rwaxt'):
        raise ValueError('Поддерживаются только текстовые режимы r, w, a и x.')
    path = virtual_path(normalized)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return builtins.open(path, mode, encoding=encoding or 'utf-8', newline=newline)

def editor_input(prompt=''):
    # Имитирует терминал: показывает приглашение и подставляет следующую строку.
    if prompt:
        print(str(prompt), end='')
    try:
        value = next(input_values)
    except StopIteration as error:
        raise EOFError('Для input() не хватает строки в поле «Данные для input()».') from error
    print(value)
    return value

SAFE_BUILTINS['input'] = editor_input
SAFE_BUILTINS['open'] = virtual_open
SAFE_BUILTINS['__import__'] = restricted_import
try:
    with contextlib.redirect_stdout(output):
        exec(compile(source, '<learner-code>', 'exec'), namespace, namespace)
    checks = []
    for test in tests:
        if test['kind'] == 'stdout':
            actual = output.getvalue().strip()
        elif test['kind'] == 'ast':
            tree = ast.parse(source)
            if test['feature'] == 'keyword_call':
                expected_keywords = set(test.get('keywords', []))
                actual = any(
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == test.get('function')
                    and expected_keywords <= {item.arg for item in node.keywords if item.arg}
                    for node in ast.walk(tree)
                )
            else:
                actual = False
        else:
            actual = eval(test['call'], namespace, namespace)
        checks.append({'passed': actual == test['expected'], 'actual': repr(actual), 'expected': repr(test['expected'])})
    print(json.dumps({'ok': all(item['passed'] for item in checks), 'checks': checks, 'output': output.getvalue()}, ensure_ascii=False))
except Exception as error:
    print(json.dumps({'ok': False, 'error': f'{type(error).__name__}: {error}', 'checks': [], 'output': output.getvalue()}, ensure_ascii=False))
"""


def normalize(value: Any) -> str:
    return str(value or "").strip().casefold()


def explain_syntax_error(error: SyntaxError) -> str:
    """Translate common parser messages into a concrete next step for a beginner."""
    line = error.lineno or "?"
    message = (error.msg or "").lower()
    if "expected ':'" in message:
        advice = "В конце строки, которая открывает блок, не хватает двоеточия `:`."
    elif "was never closed" in message or "unexpected eof" in message:
        advice = "Открывающая скобка или кавычка осталась без пары. Проверь конец строки."
    elif "unexpected indent" in message:
        advice = "У строки появился отступ, хотя перед ней не открыт блок с двоеточием."
    elif "expected an indented block" in message:
        advice = "После двоеточия нужна строка с отступом в четыре пробела."
    elif "unterminated string" in message:
        advice = "Текст начался кавычкой, но не закончился такой же кавычкой."
    else:
        advice = "Python не смог прочитать форму строки. Сверь скобки, кавычки и двоеточия."
    return f"Строка {line}: {advice}"


def explain_runtime_error(raw_error: str) -> str:
    explanations = {
        "NameError:": "Python встретил имя, которому ещё не присвоено значение.",
        "TypeError:": "Операция получила значение неподходящего типа.",
        "ValueError:": "Тип подходит, но само значение нельзя обработать этой операцией.",
        "IndexError:": "Такого номера элемента нет в последовательности.",
        "KeyError:": "В словаре нет запрошенного ключа.",
        "ZeroDivisionError:": "На ноль делить нельзя — проверь делитель до операции.",
        "EOFError:": "Для очередного input() не хватает строки в поле ввода.",
    }
    prefix = next((item for item in explanations if raw_error.startswith(item)), None)
    if not prefix:
        return f"Код остановился: {raw_error}"
    return f"{explanations[prefix]} Техническая деталь: {raw_error}"


def run_code(source: str, tests: list[dict], inputs: list[str] | None = None) -> dict:
    """Выполняет небольшой фрагмент в отдельном Python-процессе с лимитом времени."""
    if len(source) > 5_000:
        return {"correct": False, "message": "Решение слишком длинное для этого задания."}
    input_values = [str(value) for value in inputs or []]
    if len(input_values) > 20 or any(len(value) > 500 for value in input_values):
        return {
            "correct": False,
            "message": "Для запуска можно передать до 20 строк, каждая не длиннее 500 символов.",
        }
    try:
        SafetyVisitor().visit(ast.parse(source))
    except SyntaxError as error:
        return {"correct": False, "message": explain_syntax_error(error)}
    except ValueError as error:
        return {"correct": False, "message": str(error)}

    encoded_code = base64.b64encode(source.encode("utf-8")).decode("ascii")
    encoded_tests = base64.b64encode(json.dumps(tests, ensure_ascii=False).encode("utf-8")).decode(
        "ascii"
    )
    encoded_inputs = base64.b64encode(
        json.dumps(input_values, ensure_ascii=False).encode("utf-8")
    ).decode("ascii")
    program = (
        RUNNER.replace("CODE", repr(encoded_code))
        .replace("TESTS", repr(encoded_tests))
        .replace("INPUTS", repr(encoded_inputs))
    )
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
        return {
            "correct": False,
            "message": explain_runtime_error(payload["error"]),
            "checks": [],
            "output": payload.get("output", ""),
        }
    if payload.get("ok"):
        return {
            "correct": True,
            "message": "Код выполнился." if not tests else "Все тесты пройдены!",
            "checks": payload["checks"],
            "output": payload.get("output", ""),
        }
    return {
        "correct": False,
        "message": "Не все тесты прошли. Сверь результат с условием.",
        "checks": payload.get("checks", []),
        "output": payload.get("output", ""),
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
    if kind == "parsons":
        if isinstance(answer, str):
            try:
                submitted = json.loads(answer)
            except json.JSONDecodeError:
                submitted = []
        else:
            submitted = answer
        correct = isinstance(submitted, list) and submitted == question["answer"]
        return {"correct": correct, "message": question["explanation"]}
    if kind == "code":
        result = run_code(str(answer or ""), question["tests"], question.get("test_inputs"))
        result["explanation"] = question["explanation"]
        return result
    raise ValueError(f"Неизвестный тип задания: {kind}")
