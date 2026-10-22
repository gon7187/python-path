"""Дополнительные регрессии песочницы: whitelist-импорты и фасад модулей."""

import pytest

from app.evaluator import run_code

IMPORT_REJECTED = "Этот учебный редактор не поддерживает импорт и системные операции."


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("from math import sqrt\nprint(sqrt(25))\n", "5.0"),
        ("from statistics import mean\nprint(mean([2, 4]))\n", "3"),
        ("from string import ascii_lowercase\nprint(ascii_lowercase[:3])\n", "abc"),
        ("from datetime import date\nprint(date(2024, 1, 2).isoformat())\n", "2024-01-02"),
        ("from decimal import Decimal\nprint(Decimal('1.5') + Decimal('2.5'))\n", "4.0"),
        ("from fractions import Fraction\nprint(Fraction(1, 2) + Fraction(1, 2))\n", "1"),
        ("from json import dumps\nprint(dumps({'a': 1}))\n", '{"a": 1}'),
        ("from collections import deque\nprint(deque([1, 2]).popleft())\n", "1"),
        ("from functools import reduce\nprint(reduce(lambda a, b: a + b, [1, 2, 3]))\n", "6"),
        ("from itertools import count\nprint(next(count(5)))\n", "5"),
        ("from re import findall\nprint(findall(r'\\d', 'a1b2'))\n", "['1', '2']"),
        ("from heapq import nlargest\nprint(nlargest(1, [1, 5, 2]))\n", "[5]"),
        ("from bisect import bisect_left\nprint(bisect_left([1, 3], 2))\n", "1"),
        ("from enum import Enum\nclass C(Enum):\n    A = 1\nprint(C.A.value)\n", "1"),
        (
            "from dataclasses import dataclass\n@dataclass\nclass P:\n    x: int\nprint(P(7).x)\n",
            "7",
        ),
        ("from random import Random\nprint(Random(0).randint(1, 1))\n", "1"),
        ("from typing import List\nprint(List is not None)\n", "True"),
    ],
)
def test_from_import_public_symbols_are_usable(code: str, expected: str) -> None:
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].strip() == expected


def test_facade_does_not_expose_modules() -> None:
    for module, name in (("json", "codecs"), ("re", "enum"), ("random", "os")):
        result = run_code(f"import {module}\nprint(hasattr({module}, '{name}'))\n", [])
        assert result["error"] is None
        assert result["stdout"].strip() == "False"


def test_import_works_inside_function() -> None:
    code = "def encode():\n    import json\n    return json.dumps({'a': 1})\nprint(encode())\n"
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].strip() == '{"a": 1}'


@pytest.mark.parametrize(
    "code",
    [
        "def load():\n    import os\n",
        "if True:\n    import sys\n",
        "import json, os\n",
        "import json as __builtins__\n",
        "from json import dumps as __import__\n",
        "from ..json import dumps\n",
        "from os import *\n",
        "import json.decoder\n",
    ],
)
def test_unsafe_import_forms_are_rejected_before_run(code: str) -> None:
    result = run_code("print('до запуска')\n" + code, [])
    assert result["correct"] is False
    assert "не поддерживает импорт" in result["error"] or "системные функции" in result["error"]
    assert result["stdout"] == ""


def test_facade_rejects_unknown_public_name_from_import() -> None:
    result = run_code("from json import codecs\nprint(codecs)\n", [])
    assert result["error"] is not None
    assert result["stdout"] == ""


def test_exception_hierarchy_available() -> None:
    code = (
        "for error in (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError):\n"
        "    assert issubclass(error, Exception)\n"
        "print(issubclass(LookupError, Exception), issubclass(ArithmeticError, Exception))\n"
    )
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].strip() == "True True"


def test_learner_main_guard_not_taken() -> None:
    result = run_code("if __name__ == '__main__':\n    print('main')\nprint(__name__)\n", [])
    assert result["error"] is None
    assert result["stdout"].strip() == "__learner__"
