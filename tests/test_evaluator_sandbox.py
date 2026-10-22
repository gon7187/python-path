import pytest

from app.evaluator import run_code

IMPORT_REJECTED = "Этот учебный редактор не поддерживает импорт и системные операции."
ALLOWED_MODULES = [
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
]


def _run(code: str) -> dict:
    return run_code(code, [])


def test_c1_json_import_prints_dumps() -> None:
    result = _run("import json\nprint(json.dumps({'a': 1}))\n")
    assert result["error"] is None
    assert result["stdout"].strip() == '{"a": 1}'


def test_c1_collections_from_import_counter() -> None:
    result = _run("from collections import Counter\nprint(Counter('aab')['a'])\n")
    assert result["error"] is None
    assert result["stdout"].strip() == "2"


def test_c1_itertools_import_as_alias() -> None:
    result = _run("import itertools as it\nprint(list(it.islice(it.count(), 3)))\n")
    assert result["error"] is None
    assert result["stdout"].strip() == "[0, 1, 2]"


@pytest.mark.parametrize("module", ALLOWED_MODULES)
def test_c1_whitelisted_module_plain_and_alias_import(module: str) -> None:
    result = _run(f"import {module}\nimport {module} as alias\n")
    assert result["error"] is None


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("from math import sqrt\nprint(sqrt(16))\n", "4.0"),
        ("from enum import Enum\nclass Color(Enum):\n    RED = 1\nprint(Color.RED.value)\n", "1"),
        (
            "from heapq import heappush, heappop\nh = []\nheappush(h, 3)\nheappush(h, 1)\n"
            "print(heappop(h))\n",
            "1",
        ),
        (
            "from dataclasses import dataclass\n@dataclass\nclass Point:\n    x: int\n"
            "print(Point(2).x)\n",
            "2",
        ),
    ],
)
def test_c1_from_import_of_whitelisted_names(code: str, expected: str) -> None:
    result = _run(code)
    assert result["error"] is None
    assert result["stdout"].strip() == expected


@pytest.mark.parametrize(
    "code",
    [
        "import os\n",
        "import sys\n",
        "import subprocess\n",
        "import importlib\n",
        "from os import path\n",
        "import json.decoder\n",
        "from . import x\n",
        "from json import *\n",
        "import json, os\n",
    ],
)
def test_c2_forbidden_imports_rejected_before_run(code: str) -> None:
    result = _run("print('до запуска')\n" + code)
    assert result["correct"] is False
    assert IMPORT_REJECTED in result["error"]
    assert result["stdout"] == ""


def test_c3_module_attribute_for_submodule_is_error() -> None:
    result = _run("import json\nprint(json.codecs)\n")
    assert result["stdout"] == ""
    assert result["error"] is not None
    assert result["error"].startswith("AttributeError:")


def test_c3_re_module_does_not_expose_enum() -> None:
    result = _run("import re\nprint(re.enum)\n")
    assert result["stdout"] == ""
    assert result["error"] is not None
    assert result["error"].startswith("AttributeError:")


def test_c3_random_module_does_not_expose_os() -> None:
    result = _run("import random\nprint(random.os)\n")
    assert result["stdout"] == ""
    assert result["error"] is not None
    assert result["error"].startswith("AttributeError:")


def test_c3_from_import_of_submodule_name_fails() -> None:
    result = _run("from json import codecs\nprint(codecs)\n")
    assert result["stdout"] == ""
    assert result["error"] is not None


def test_c4_try_except_zero_division() -> None:
    result = _run("try:\n    1 / 0\nexcept ZeroDivisionError:\n    print('ok')\n")
    assert result["error"] is None
    assert result["stdout"].strip() == "ok"


def test_c4_raise_value_error_reports_message() -> None:
    result = _run("raise ValueError('плохо')\n")
    assert result["error"] == "ValueError: плохо"


@pytest.mark.parametrize(
    "name",
    [
        "Exception",
        "ValueError",
        "TypeError",
        "KeyError",
        "IndexError",
        "ZeroDivisionError",
        "AttributeError",
        "StopIteration",
        "RuntimeError",
        "NotImplementedError",
        "ArithmeticError",
        "LookupError",
        "isinstance",
        "issubclass",
        "reversed",
        "map",
        "filter",
        "iter",
        "next",
        "repr",
        "divmod",
        "pow",
        "chr",
        "ord",
        "frozenset",
        "super",
        "object",
        "property",
        "staticmethod",
        "classmethod",
        "hasattr",
        "callable",
    ],
)
def test_c4_builtin_name_is_available(name: str) -> None:
    result = _run(f"print({name} is not None)\n")
    assert result["error"] is None
    assert result["stdout"].strip() == "True"


def test_c4_builtin_functions_behave() -> None:
    code = (
        "print(isinstance(1, int), list(reversed([1, 2])), list(map(str, [1])), "
        "list(filter(None, [0, 1])), next(iter([5])), repr('a'), divmod(7, 2), pow(2, 3), "
        "chr(65), ord('A'), frozenset([1]) == {1}, hasattr(1, 'real'), callable(len), "
        "issubclass(bool, int))\n"
    )
    result = _run(code)
    assert result["error"] is None
    expected = "True [2, 1] ['1'] [1] 5 'a' (3, 1) 8 A 65 True True True True"
    assert result["stdout"].strip() == expected


def test_c5_subclass_with_super_init_runs() -> None:
    code = (
        "class Learner:\n"
        "    def __init__(self, name):\n"
        "        self.name = name\n"
        "\n"
        "class Student(Learner):\n"
        "    def __init__(self, name):\n"
        "        super().__init__(name)\n"
        "\n"
        "    def __repr__(self):\n"
        "        return f'Student({self.name})'\n"
        "\n"
        "print(repr(Student('Ира')), Student.__name__)\n"
    )
    result = _run(code)
    assert result["error"] is None
    assert result["stdout"].strip() == "Student(Ира) Student"


def test_c5_allowed_dunder_methods_work() -> None:
    code = (
        "class Box:\n"
        "    def __init__(self, items):\n"
        "        self.items = items\n"
        "\n"
        "    def __str__(self):\n"
        "        return 'Коробка'\n"
        "\n"
        "    def __repr__(self):\n"
        "        return 'Box()'\n"
        "\n"
        "    def __eq__(self, other):\n"
        "        return len(self) == len(other)\n"
        "\n"
        "    def __lt__(self, other):\n"
        "        return len(self) < len(other)\n"
        "\n"
        "    def __len__(self):\n"
        "        return len(self.items)\n"
        "\n"
        "    def __iter__(self):\n"
        "        return iter(self.items)\n"
        "\n"
        "    def __enter__(self):\n"
        "        return self\n"
        "\n"
        "    def __exit__(self, *args):\n"
        "        return False\n"
        "\n"
        "class Countdown:\n"
        "    def __init__(self, start):\n"
        "        self.current = start\n"
        "\n"
        "    def __iter__(self):\n"
        "        return self\n"
        "\n"
        "    def __next__(self):\n"
        "        if self.current == 0:\n"
        "            raise StopIteration\n"
        "        self.current -= 1\n"
        "        return self.current + 1\n"
        "\n"
        "box = Box([1, 2])\n"
        "with box as opened:\n"
        "    print(str(box), repr(box), len(box), box == Box([3, 4]), box < Box([1, 2, 3]), "
        "list(opened))\n"
        "print(list(Countdown(3)))\n"
    )
    result = _run(code)
    assert result["error"] is None
    assert result["stdout"].splitlines() == ["Коробка Box() 2 True True [1, 2]", "[3, 2, 1]"]


def test_c5_dunder_name_is_learner_module_name() -> None:
    result = _run("print(__name__)\n")
    assert result["error"] is None
    assert result["stdout"].strip() == "__learner__"


def test_c5_main_guard_is_accepted_but_not_taken() -> None:
    result = _run("if __name__ == '__main__':\n    print('main')\nprint(__name__)\n")
    assert result["error"] is None
    assert result["stdout"].strip() == "__learner__"


@pytest.mark.parametrize(
    "snippet",
    [
        "print((1).__class__)\n",
        "def f():\n    pass\nprint(f.__globals__)\n",
        "print(object.__subclasses__())\n",
        "class C:\n    pass\nprint(C().__dict__)\n",
        "class C:\n    pass\nprint(C.__bases__)\n",
        "class C:\n    pass\nprint(C.__mro__)\n",
        "def f():\n    pass\nprint(f.__code__)\n",
        "print(__builtins__)\n",
        "print(object()._private)\n",
    ],
)
def test_c5_forbidden_dunder_and_private_names_rejected(snippet: str) -> None:
    result = _run("print('до запуска')\n" + snippet)
    assert result["correct"] is False
    assert result["error"] is not None
    assert result["stdout"] == ""


@pytest.mark.parametrize(
    "name",
    [
        "open",
        "eval",
        "exec",
        "compile",
        "input",
        "getattr",
        "setattr",
        "globals",
        "vars",
        "breakpoint",
        "__import__",
    ],
)
def test_c6_forbidden_builtin_names_still_rejected(name: str) -> None:
    result = _run(f"print('до запуска')\nprint({name})\n")
    assert result["correct"] is False
    assert result["error"] is not None
    assert result["stdout"] == ""


def test_c6_async_def_still_rejected() -> None:
    result = _run("print('до запуска')\nasync def f():\n    return 1\n")
    assert result["correct"] is False
    assert result["error"] is not None
    assert result["stdout"] == ""


def test_c6_infinite_loop_times_out() -> None:
    result = _run("while True:\n    pass\n")
    assert result["correct"] is False
    assert result["timed_out"] is True
