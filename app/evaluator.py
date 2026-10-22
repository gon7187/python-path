"""Проверка ответов и безопасный мини-раннер учебного кода."""

from __future__ import annotations

import ast
import base64
import json
import re
import secrets
import string
import subprocess
import sys
from typing import Any

IMPORT_REJECTED = "Этот учебный редактор не поддерживает импорт и системные операции."
SYSTEM_NAMES_REJECTED = "В учебном редакторе нельзя использовать системные функции."
ATTRIBUTE_REJECTED = "Служебные атрибуты недоступны в учебном редакторе."

FORBIDDEN_NODES = (ast.Global, ast.Nonlocal, ast.AsyncFunctionDef)
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

ALLOWED_MODULES = frozenset(
    {
        "json",
        "re",
        "math",
        "statistics",
        "itertools",
        "functools",
        "collections",
        "string",
        "datetime",
        "decimal",
        "fractions",
        "dataclasses",
        "enum",
        "heapq",
        "bisect",
        "random",
        "typing",
    }
)

ALLOWED_DUNDER_ATTRIBUTES = frozenset(
    {
        "__init__",
        "__str__",
        "__repr__",
        "__eq__",
        "__lt__",
        "__len__",
        "__iter__",
        "__next__",
        "__enter__",
        "__exit__",
        "__name__",
    }
)

# Имена внутри разрешённых модулей, которые не попадают в фасад: они умеют
# разбирать строки как код/цепочки атрибутов и открывают обход AST-проверки.
# Formatter.get_field разбирает '0.__init__.__globals__' из строки, а
# get_type_hints вычисляет строковые аннотации через eval.
MODULE_DENIED_NAMES: dict[str, frozenset[str]] = {
    "string": frozenset({"Formatter"}),
    # Type/get_origin/ABCMeta/NamedTupleMeta дают настоящий type, а через
    # его mro или вызов можно создать класс с любыми dunder-атрибутами.
    "typing": frozenset(
        {
            "ABCMeta",
            "ForwardRef",
            "NamedTupleMeta",
            "Type",
            "TypeAliasType",
            "TypedDict",
            "get_origin",
            "get_type_hints",
        }
    ),
    "functools": frozenset({"singledispatch", "singledispatchmethod"}),
    # Возвращает настоящий builtins.getattr, которым можно прочитать
    # __globals__/__class__ в обход AST.
    # EnumType/EnumMeta — метаклассы, их mro содержит type.
    "enum": frozenset({"EnumMeta", "EnumType", "global_enum", "pickle_by_enum_name"}),
    # Позволяет создать dataclass с полями вида __traceback__/__globals__;
    # dataclasses.replace/asdict затем читают служебные атрибуты экземпляра.
    "dataclasses": frozenset({"make_dataclass"}),
}

# Публичные имена кадров/генераторов дают f_builtins и f_globals без
# dunder-атрибутов: генератор, управляемый функцией стандартной библиотеки,
# видит её кадр через gi_frame.f_back.
FORBIDDEN_FRAME_ATTRIBUTES = frozenset(
    {
        "ag_await",
        "ag_code",
        "ag_frame",
        "ag_running",
        "cr_await",
        "cr_code",
        "cr_frame",
        "cr_origin",
        "cr_running",
        "f_back",
        "f_builtins",
        "f_code",
        "f_globals",
        "f_lasti",
        "f_lineno",
        "f_locals",
        "f_trace",
        "gi_code",
        "gi_frame",
        "gi_running",
        "gi_suspended",
        "gi_yieldfrom",
        "tb_frame",
        "tb_lasti",
        "tb_lineno",
        "tb_next",
    }
)

FORBIDDEN_ATTRIBUTE_NAMES = (
    frozenset(name for names in MODULE_DENIED_NAMES.values() for name in names)
    | FORBIDDEN_FRAME_ATTRIBUTES
)

FORMAT_METHODS = frozenset({"format", "format_map"})
WRAPPER_METHODS = frozenset({"update_wrapper", "wraps"})
WRAPPER_NAME_ARGUMENTS = {"update_wrapper": 2, "wraps": 1}


def _format_field_name_is_safe(field_name: str, depth: int) -> bool:
    """Проверяет цепочку атрибутов в поле строки формата.

    ``str.format`` умеет разбирать ``{0.__init__.__globals__}`` без узла
    ``ast.Attribute``, поэтому ограничение dunder-атрибутов нужно повторить
    для имён, которые извлекаются из шаблона.
    """
    parts = re.split(r"(?=[.\[])", field_name)
    root = parts[0].strip()
    if root.startswith("_"):
        return False
    for part in parts[1:]:
        if part.startswith("."):
            attribute = part[1:].strip()
            if not attribute:
                return False
            if attribute in FORBIDDEN_ATTRIBUTE_NAMES:
                return False
            if attribute.startswith("_") and attribute not in ALLOWED_DUNDER_ATTRIBUTES:
                return False
        elif part.startswith("["):
            key = part[1:-1] if part.endswith("]") else part[1:]
            key = key.strip()
            if len(key) >= 2 and key[0] == key[-1] and key[0] in {"'", '"'}:
                key = key[1:-1]
            if key in FORBIDDEN_ATTRIBUTE_NAMES or key.startswith("_"):
                return False
            if "{" in key and not _format_template_is_safe(key, depth + 1):
                return False
        else:
            return False
    return True


def _format_template_is_safe(template: str, depth: int = 0) -> bool:
    """Возвращает True, если шаблон формата не достаёт служебные атрибуты."""
    if depth > 5:
        return False
    try:
        fields = list(string.Formatter().parse(template))
    except (ValueError, TypeError):
        return False
    for _, field_name, format_spec, _ in fields:
        if field_name is None:
            continue
        if not _format_field_name_is_safe(field_name, depth):
            return False
        if format_spec and not _format_template_is_safe(format_spec, depth + 1):
            return False
    return True


class SafetyVisitor(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, FORBIDDEN_NODES):
            raise ValueError(IMPORT_REJECTED)
        return super().visit(node)

    @staticmethod
    def _check_attribute_name(attribute: str, *, allow_format: bool = False) -> None:
        """Единая проверка имени, по которому идёт доступ к атрибуту.

        Ограничение применяется не только к ``ast.Attribute``, но и к именам,
        которые Python извлекает сам: поля format-строк и keyword-атрибуты
        class-паттернов ``match``. Иначе ``case object(__globals__=x):``
        получает служебный атрибут без узла ``ast.Attribute``.
        """
        if attribute in FORMAT_METHODS:
            if not allow_format:
                raise ValueError(ATTRIBUTE_REJECTED)
        elif attribute == "Formatter":
            raise ValueError(IMPORT_REJECTED)
        elif attribute in FORBIDDEN_ATTRIBUTE_NAMES:
            raise ValueError(ATTRIBUTE_REJECTED)
        if attribute.startswith("_") and attribute not in ALLOWED_DUNDER_ATTRIBUTES:
            raise ValueError(ATTRIBUTE_REJECTED)

    @staticmethod
    def _check_binding_name(name: str) -> None:
        """Запрещает связывать служебные имена через параметры/match."""
        if name.startswith("__") and name not in ALLOWED_DUNDER_ATTRIBUTES:
            raise ValueError(SYSTEM_NAMES_REJECTED)
        if name == "__name__":
            raise ValueError(SYSTEM_NAMES_REJECTED)

    @staticmethod
    def _check_definition_name(name: str) -> None:
        """Имя def/class — не доступ к атрибуту: методы вроде __post_init__
        безопасны, но глобальные __builtins__/__name__ подменять нельзя."""
        if name in {"__builtins__", "__name__"}:
            raise ValueError(SYSTEM_NAMES_REJECTED)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in FORBIDDEN_NAMES:
            raise ValueError(SYSTEM_NAMES_REJECTED)
        if node.id == "__name__":
            if not isinstance(node.ctx, ast.Load):
                raise ValueError(SYSTEM_NAMES_REJECTED)
            return
        if node.id.startswith("__"):
            raise ValueError(SYSTEM_NAMES_REJECTED)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self._check_attribute_name(node.attr, allow_format=getattr(node, "_format_checked", False))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in FORMAT_METHODS:
            value = function.value
            if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
                raise ValueError(ATTRIBUTE_REJECTED)
            if not _format_template_is_safe(value.value):
                raise ValueError(ATTRIBUTE_REJECTED)
            setattr(function, "_format_checked", True)
        self._check_wrapper_call(node)
        self.generic_visit(node)

    def _check_wrapper_call(self, node: ast.Call) -> None:
        """Не даёт передать служебные имена в assigned/updated обёрток.

        ``functools.wraps``/``update_wrapper`` вызывают ``getattr`` по строкам
        из ``assigned``; ``('__globals__',)`` превращает обёртку в чтение
        globals в обход AST.
        """
        function = node.func
        name: str | None = None
        if isinstance(function, ast.Attribute):
            name = function.attr
        elif isinstance(function, ast.Name):
            name = function.id
        if name not in WRAPPER_METHODS:
            return
        first_name_index = WRAPPER_NAME_ARGUMENTS[name]
        name_indices = {first_name_index, first_name_index + 1}
        for index, argument in enumerate(node.args):
            if index in name_indices:
                self._check_wrapper_names(argument)
        for keyword in node.keywords:
            if keyword.arg in {"assigned", "updated"}:
                self._check_wrapper_names(keyword.value)

    def _check_wrapper_names(self, value: ast.expr) -> None:
        if not isinstance(value, (ast.Tuple, ast.List)):
            # Не литерал: значение проверит безопасная обёртка во время
            # выполнения, не отказывая заранее в обычных вызовах.
            return
        for element in value.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                self._check_attribute_name(element.value)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_definition_name(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_definition_name(node.name)
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        self._check_binding_name(node.arg)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name:
            self._check_binding_name(node.name)
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name:
            self._check_binding_name(node.name)
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name:
            self._check_binding_name(node.name)
        self.generic_visit(node)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest:
            self._check_binding_name(node.rest)
        self.generic_visit(node)

    def visit_MatchClass(self, node: ast.MatchClass) -> None:
        # ``case C(__class__=x)`` читает атрибут по строке из kwd_attrs,
        # не создавая ast.Attribute. Проверяем такие имена так же строго.
        for attribute in node.kwd_attrs:
            self._check_attribute_name(attribute)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name not in ALLOWED_MODULES:
                raise ValueError(IMPORT_REJECTED)
            self._check_import_alias(alias)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level != 0 or node.module not in ALLOWED_MODULES:
            raise ValueError(IMPORT_REJECTED)
        denied = MODULE_DENIED_NAMES.get(node.module, frozenset())
        for alias in node.names:
            if alias.name == "*" or alias.name.startswith("_") or alias.name in denied:
                raise ValueError(IMPORT_REJECTED)
            self._check_import_alias(alias)

    @staticmethod
    def _check_import_alias(alias: ast.alias) -> None:
        if alias.asname and (alias.asname in FORBIDDEN_NAMES or alias.asname.startswith("__")):
            raise ValueError(SYSTEM_NAMES_REJECTED)


RUNNER = r"""
import base64
import builtins
import contextlib
import functools as _real_functools
import io
import json
import types

ALLOWED_MODULES = ALLOWED_MODULES_DATA
DENIED_MODULE_NAMES = DENIED_NAMES_DATA

_real_import = builtins.__import__
# wraps не должен копировать __dict__/__annotations__: через них можно
# подменить метаданные dataclass и прочитать служебные атрибуты экземпляра.
_WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__')


def _reject_wrapper_customization(assigned, updated):
    if assigned is not None or updated is not None:
        raise TypeError('В учебном редакторе wraps не принимает assigned/updated.')


def _safe_update_wrapper(wrapper, wrapped, assigned=None, updated=None):
    _reject_wrapper_customization(assigned, updated)
    return _real_functools.update_wrapper(
        wrapper, wrapped, assigned=_WRAPPER_ASSIGNMENTS, updated=()
    )


def _safe_wraps(wrapped, assigned=None, updated=None):
    _reject_wrapper_customization(assigned, updated)

    def decorator(wrapper):
        _real_functools.update_wrapper(
            wrapper, wrapped, assigned=_WRAPPER_ASSIGNMENTS, updated=()
        )
        return wrapper

    return decorator


_FACADE_OVERRIDES = {
    ('functools', 'update_wrapper'): _safe_update_wrapper,
    ('functools', 'wraps'): _safe_wraps,
}


def _build_facade(module_name):
    module = _real_import(module_name)
    denied = DENIED_MODULE_NAMES.get(module_name, ())
    public = {}
    for name, value in vars(module).items():
        if name.startswith('_') or name in denied:
            continue
        if isinstance(value, types.ModuleType):
            continue
        public[name] = _FACADE_OVERRIDES.get((module_name, name), value)
    return types.SimpleNamespace(**public)


_facades = {}


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level != 0 or name not in ALLOWED_MODULES:
        raise ImportError('Этот учебный редактор не поддерживает импорт и системные операции.')
    if name not in _facades:
        _facades[name] = _build_facade(name)
    return _facades[name]


SAFE_BUILTINS = {
    '__build_class__': builtins.__build_class__, '__import__': _safe_import,
    'abs': abs, 'all': all, 'any': any,
    'bool': bool, 'dict': dict, 'enumerate': enumerate, 'float': float, 'int': int,
    'len': len, 'list': list, 'max': max, 'min': min, 'print': print, 'range': range,
    'round': round, 'set': set, 'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple,
    'zip': zip,
    'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
    'KeyError': KeyError, 'IndexError': IndexError, 'ZeroDivisionError': ZeroDivisionError,
    'AttributeError': AttributeError, 'StopIteration': StopIteration,
    'RuntimeError': RuntimeError, 'NotImplementedError': NotImplementedError,
    'ArithmeticError': ArithmeticError, 'LookupError': LookupError,
    'isinstance': isinstance, 'issubclass': issubclass, 'reversed': reversed, 'map': map,
    'filter': filter, 'iter': iter, 'next': next, 'repr': repr, 'divmod': divmod,
    'pow': pow, 'chr': chr, 'ord': ord, 'frozenset': frozenset, 'super': super,
    'object': object, 'property': property, 'staticmethod': staticmethod,
    'classmethod': classmethod, 'hasattr': hasattr, 'callable': callable,
}
source = base64.b64decode(CODE_DATA).decode('utf-8')
tests = json.loads(base64.b64decode(TESTS_DATA).decode('utf-8'))
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
    print(RESULT_TOKEN + json.dumps({'ok': all(item['passed'] for item in checks), 'checks': checks, 'stdout': output.getvalue()}, ensure_ascii=False))
except Exception as error:
    print(RESULT_TOKEN + json.dumps({'ok': False, 'error': f'{type(error).__name__}: {error}', 'checks': [], 'stdout': output.getvalue()}, ensure_ascii=False))
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
    denied_names = {module: tuple(sorted(names)) for module, names in MODULE_DENIED_NAMES.items()}
    result_token = "__LEARNER_RESULT_" + secrets.token_hex(16) + "__"
    program = (
        RUNNER.replace("CODE_DATA", repr(encoded_code))
        .replace("TESTS_DATA", repr(encoded_tests))
        .replace("ALLOWED_MODULES_DATA", repr(tuple(sorted(ALLOWED_MODULES))))
        .replace("DENIED_NAMES_DATA", repr(denied_names))
        .replace("RESULT_TOKEN", repr(result_token))
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
        result_line = next(
            line for line in result.stdout.splitlines() if line.startswith(result_token)
        )
        payload = json.loads(result_line.removeprefix(result_token))
    except (json.JSONDecodeError, StopIteration):
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
