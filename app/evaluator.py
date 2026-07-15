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
    "argparse",
    "asyncio",
    "bisect",
    "collections",
    "concurrent",
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
    "queue",
    "random",
    "re",
    "sqlite3",
    "statistics",
    "sys",
    "threading",
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
    "enable_load_extension",
    "load_extension",
    "new_event_loop",
    "open_connection",
    "run_in_executor",
    "start_server",
    "set_authorizer",
    "to_thread",
}
FORBIDDEN_IMPORT_MEMBERS = {
    "concurrent.futures": {"ProcessPoolExecutor"},
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
        forbidden = FORBIDDEN_IMPORT_MEMBERS.get(node.module, set())
        imported = {item.name for item in node.names}
        if imported & forbidden:
            raise ValueError("Запуск дочерних процессов недоступен в учебном редакторе.")
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
import argparse as real_argparse
import asyncio as real_asyncio
import ast
import base64
import builtins
import contextlib
import concurrent.futures as real_futures
import dataclasses as real_dataclasses
import enum as real_enum
import io
import json
import os
import queue as real_queue
import sqlite3 as real_sqlite3
import sys as real_sys
import tempfile
import threading as real_threading
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
    'TimeoutError': TimeoutError, 'ValueError': ValueError,
    'ZeroDivisionError': ZeroDivisionError,
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
    'argparse', 'asyncio', 'bisect', 'collections', 'concurrent', 'csv', 'dataclasses',
    'datetime', 'decimal', 'enum', 'functools', 'heapq', 'itertools', 'json', 'math',
    'pathlib', 'queue', 'random', 're', 'sqlite3', 'statistics', 'sys', 'threading',
    'typing',
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

    def as_posix(self):
        return self._logical.replace(os.sep, '/')

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

class SafeArgumentParser(real_argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        if kwargs.get('fromfile_prefix_chars'):
            raise ValueError('Чтение аргументов из файла недоступно в учебном редакторе.')
        kwargs['fromfile_prefix_chars'] = None
        kwargs['exit_on_error'] = False
        super().__init__(*args, **kwargs)

    def parse_known_args(self, args=None, namespace=None):
        # The editor has no real command line. Learners may pass a list explicitly.
        return super().parse_known_args([] if args is None else args, namespace)

    def exit(self, status=0, message=None):
        raise ValueError(message or f'Парсер завершился с кодом {status}.')

    def error(self, message):
        raise ValueError(f'Ошибка аргументов: {message}')

class SafeThreadPoolExecutor:
    def __init__(self, max_workers=None, thread_name_prefix='', initializer=None, initargs=()):
        workers = 4 if max_workers is None else int(max_workers)
        if not 1 <= workers <= 4:
            raise ValueError('В учебном редакторе можно запустить от 1 до 4 потоков.')
        self._executor = real_futures.ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix=thread_name_prefix,
            initializer=initializer,
            initargs=initargs,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._executor.__exit__(exc_type, exc_value, traceback)

    def submit(self, function, /, *args, **kwargs):
        return self._executor.submit(function, *args, **kwargs)

    def map(self, function, *iterables, timeout=None, chunksize=1):
        return self._executor.map(function, *iterables, timeout=timeout, chunksize=chunksize)

    def shutdown(self, wait=True, *, cancel_futures=False):
        return self._executor.shutdown(wait=wait, cancel_futures=cancel_futures)

class SafeThread:
    _active_count = 0
    _limit_lock = real_threading.Lock()

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        if group is not None:
            raise ValueError('group не поддерживается в учебном редакторе.')
        self._target = target
        self._args = tuple(args)
        self._kwargs = dict(kwargs or {})
        self._counted = False
        self._thread = real_threading.Thread(
            target=self._run_guarded,
            name=name,
            daemon=daemon,
        )

    def _run_guarded(self):
        try:
            return self.run()
        finally:
            with SafeThread._limit_lock:
                if self._counted:
                    SafeThread._active_count -= 1
                    self._counted = False

    def run(self):
        if self._target is not None:
            return self._target(*self._args, **self._kwargs)
        return None

    def start(self):
        with SafeThread._limit_lock:
            if SafeThread._active_count >= 4:
                raise RuntimeError('В учебном редакторе можно одновременно запустить до 4 потоков.')
            SafeThread._active_count += 1
            self._counted = True
        try:
            return self._thread.start()
        except BaseException:
            with SafeThread._limit_lock:
                SafeThread._active_count -= 1
                self._counted = False
            raise

    def join(self, timeout=None):
        return self._thread.join(timeout)

    def is_alive(self):
        return self._thread.is_alive()

    @property
    def name(self):
        return self._thread.name

    @name.setter
    def name(self, value):
        self._thread.name = value

    @property
    def daemon(self):
        return self._thread.daemon

    @daemon.setter
    def daemon(self, value):
        self._thread.daemon = value

    @property
    def ident(self):
        return self._thread.ident

    @property
    def native_id(self):
        return self._thread.native_id

def sqlite_authorizer(action, first, second, database, trigger):
    del database, trigger
    blocked_actions = {real_sqlite3.SQLITE_ATTACH, real_sqlite3.SQLITE_DETACH}
    blocked_functions = {'load_extension', 'readfile', 'writefile'}
    if action in blocked_actions:
        return real_sqlite3.SQLITE_DENY
    if action == real_sqlite3.SQLITE_FUNCTION and str(second).casefold() in blocked_functions:
        return real_sqlite3.SQLITE_DENY
    if action == real_sqlite3.SQLITE_PRAGMA and str(first).casefold() in {
        'data_store_directory', 'temp_store_directory'
    }:
        return real_sqlite3.SQLITE_DENY
    return real_sqlite3.SQLITE_OK

def safe_sqlite_connect(
    database=':memory:', timeout=5.0, detect_types=0, isolation_level='',
    check_same_thread=True, cached_statements=128,
):
    raw = os.fspath(database)
    if raw.startswith('file:'):
        raise ValueError('URI SQLite недоступны в учебном редакторе.')
    path = ':memory:' if raw == ':memory:' else virtual_path(raw)
    connection = real_sqlite3.connect(
        path,
        timeout=timeout,
        detect_types=detect_types,
        isolation_level=isolation_level,
        check_same_thread=check_same_thread,
        cached_statements=cached_statements,
    )
    connection.set_authorizer(sqlite_authorizer)
    return connection

safe_futures = types.SimpleNamespace(
    ThreadPoolExecutor=SafeThreadPoolExecutor,
    as_completed=real_futures.as_completed,
    wait=real_futures.wait,
    FIRST_COMPLETED=real_futures.FIRST_COMPLETED,
    FIRST_EXCEPTION=real_futures.FIRST_EXCEPTION,
    ALL_COMPLETED=real_futures.ALL_COMPLETED,
)
safe_concurrent = types.SimpleNamespace(futures=safe_futures)

SAFE_MODULE_OVERRIDES = {
    'argparse': types.SimpleNamespace(
        ArgumentParser=SafeArgumentParser,
        Namespace=real_argparse.Namespace,
    ),
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
    'queue': types.SimpleNamespace(
        Queue=real_queue.Queue,
        LifoQueue=real_queue.LifoQueue,
        PriorityQueue=real_queue.PriorityQueue,
        Empty=real_queue.Empty,
        Full=real_queue.Full,
    ),
    'sqlite3': types.SimpleNamespace(
        connect=safe_sqlite_connect,
        Row=real_sqlite3.Row,
        Error=real_sqlite3.Error,
        DatabaseError=real_sqlite3.DatabaseError,
        IntegrityError=real_sqlite3.IntegrityError,
        OperationalError=real_sqlite3.OperationalError,
        PARSE_DECLTYPES=real_sqlite3.PARSE_DECLTYPES,
        PARSE_COLNAMES=real_sqlite3.PARSE_COLNAMES,
    ),
    'sys': types.SimpleNamespace(
        argv=['program.py'],
        platform=real_sys.platform,
        version_info=real_sys.version_info,
    ),
    'threading': types.SimpleNamespace(
        Thread=SafeThread,
        Lock=real_threading.Lock,
        RLock=real_threading.RLock,
        Event=real_threading.Event,
        Semaphore=real_threading.Semaphore,
        current_thread=real_threading.current_thread,
    ),
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
    if name == 'concurrent.futures':
        return safe_futures if fromlist else safe_concurrent
    if root == 'concurrent':
        return safe_concurrent
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

def normalize_stdout_whitespace(value):
    # Preserve line order/count while ignoring accidental horizontal spacing.
    return '\n'.join(' '.join(line.split()) for line in str(value).strip().splitlines())

phase = 'learner_exec'
try:
    with contextlib.redirect_stdout(output):
        exec(compile(source, '<learner-code>', 'exec'), namespace, namespace)
    phase = 'hidden_test'
    checks = []
    for test in tests:
        if test['kind'] == 'stdout':
            actual = output.getvalue().replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')
            expected = str(test['expected']).replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')
            comparison = test.get('comparison', 'strict')
            if comparison == 'strict':
                passed = actual == expected
            elif comparison == 'whitespace':
                passed = normalize_stdout_whitespace(actual) == normalize_stdout_whitespace(expected)
            elif comparison == 'contains':
                passed = normalize_stdout_whitespace(expected) in normalize_stdout_whitespace(actual)
            else:
                raise ValueError(f'Неизвестный режим сравнения stdout: {comparison}')
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
            expected = test['expected']
            passed = actual == expected
        elif test['kind'] == 'source':
            normalized_source = source.replace('\r\n', '\n').replace('\r', '\n')
            required = [
                str(fragment).replace('\r\n', '\n').replace('\r', '\n')
                for fragment in test.get('required_tokens', [])
                if str(fragment)
            ]
            actual = all(fragment in normalized_source for fragment in required)
            expected = test.get('expected', True)
            passed = actual == expected
        else:
            actual = eval(test['call'], namespace, namespace)
            expected = test['expected']
            passed = actual == expected
        check = {
            'passed': passed,
            'kind': test['kind'],
            'actual': repr(actual),
            'expected': repr(expected),
        }
        if test['kind'] == 'source':
            check['required_tokens'] = required
        checks.append(check)
    print(json.dumps({'ok': all(item['passed'] for item in checks), 'checks': checks, 'output': output.getvalue()}, ensure_ascii=False))
except Exception as error:
    print(json.dumps({'ok': False, 'error': f'{type(error).__name__}: {error}', 'error_phase': phase, 'checks': [], 'output': output.getvalue()}, ensure_ascii=False))
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


def explain_failed_checks(checks: list[dict]) -> str:
    """Show the first concrete mismatch instead of a generic red result."""
    failed = [check for check in checks if not check.get("passed")]
    if not failed:
        return "Проверка не прошла, но несовпадение не удалось определить."
    source_only = all(check.get("kind") == "source" for check in failed)
    behavior_passed = any(check.get("kind") != "source" and check.get("passed") for check in checks)
    if source_only and behavior_passed:
        required = list(
            dict.fromkeys(
                str(token)
                for check in failed
                for token in check.get("required_tokens", ())
                if str(token)
            )
        )
        forms = ", ".join(f"`{token}`" for token in required)
        return (
            "По результатам код уже работает на контрольных примерах. "
            "Но цель именно этого урока — применить изучаемую форму"
            f": {forms}. Добавь её и проверь ещё раз."
        )
    check = failed[0]
    labels = {
        "stdout": "вывода",
        "call": "вызова",
        "value": "значения",
        "ast": "формы кода",
        "source": "заявленного синтаксиса",
    }
    label = labels.get(str(check.get("kind")), "результата")
    expected = str(check.get("expected", ""))[:180]
    actual = str(check.get("actual", ""))[:180]
    suffix = f" Ещё не прошло: {len(failed) - 1}." if len(failed) > 1 else ""
    return f"Не совпала проверка {label}: ожидалось {expected}, получено {actual}.{suffix}"


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
            [sys.executable, "-X", "utf8", "-I", "-c", program],
            capture_output=True,
            text=True,
            encoding="utf-8",
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
            "error_phase": payload.get("error_phase", "learner_exec"),
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
        "message": explain_failed_checks(payload.get("checks", [])),
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
        if result["correct"]:
            explanation = question["explanation"]
            result["explanation"] = explanation
            if explanation and explanation not in result["message"]:
                result["message"] = f"{result['message']} {explanation}"
        return result
    raise ValueError(f"Неизвестный тип задания: {kind}")
