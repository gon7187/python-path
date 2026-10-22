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


@pytest.mark.parametrize(
    "code",
    [
        # Formatter.get_field разбирает цепочку атрибутов из строки и обходит AST.
        (
            "import string, json\n"
            "loader = string.Formatter().get_field("
            "'0.__init__.__globals__[__builtins__][__import__]',"
            " [json.JSONDecoder], {})[0]\n"
            "print(loader('os').getcwd())\n"
        ),
        "import string\nprint(string.Formatter)\n",
        "from string import Formatter\n",
        "print('{0.__init__.__globals__}'.format(object))\n",
        "print('{0.__init__.__globals__}'.format_map([object]))\n",
        "print('{0.__class__}'.format(1))\n",
        "template = '{0.__class__}'\nprint(template.format(1))\n",
        # get_type_hints вычисляет строковые аннотации через eval.
        (
            "import typing\n"
            "def f(x: '().__class__.__base__.__subclasses__()'):\n"
            "    pass\n"
            "print(typing.get_type_hints(f))\n"
        ),
        "import typing\nprint(typing.ForwardRef)\n",
        "from typing import get_type_hints\n",
        "import functools\nprint(functools.singledispatch)\n",
    ],
)
def test_string_and_annotation_based_attribute_bypass_rejected(code: str) -> None:
    result = run_code("print('до запуска')\n" + code, [])
    assert result["correct"] is False
    assert result["error"] is not None
    assert result["stdout"] == ""


def test_safe_literal_format_still_works() -> None:
    code = (
        "print('{} {}'.format(1, 2))\n"
        "print('{name}!'.format(name='ok'))\n"
        "print('{0:{1}}'.format(5, '>4'))\n"
    )
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].splitlines() == ["1 2", "ok!", "   5"]


def test_typing_public_types_are_still_available() -> None:
    result = run_code("import typing\nprint(typing.List, typing.Optional)\n", [])
    assert result["error"] is None
    assert "typing.List" in result["stdout"]


@pytest.mark.parametrize(
    "code",
    [
        # Class-паттерн читает keyword-атрибуты по строкам из AST, а не через
        # ast.Attribute: так можно добраться до __class__, __mro__,
        # __subclasses__ и __globals__ и получить настоящий import.
        (
            "match 1:\n"
            "    case int(__class__=cls):\n"
            "        match cls:\n"
            "            case object(__mro__=mro):\n"
            "                base = mro[-1]\n"
            "                match base:\n"
            "                    case object(__subclasses__=subs):\n"
            "                        for c in subs():\n"
            "                            if c.__name__ == 'BuiltinImporter':\n"
            "                                match c:\n"
            "                                    case object(load_module=load):\n"
            "                                        match load:\n"
            "                                            case object(__globals__=g):\n"
            "                                                real = g['__builtins__']['__import__']\n"
            "                                                print(real('os').getcwd())\n"
        ),
        "match 1:\n    case int(__class__=cls):\n        print(cls)\n",
        "match print:\n    case object(__self__=module):\n        print(module)\n",
        "match print:\n    case object(__doc__=doc):\n        print(doc)\n",
        # Связанный метод format, вытащенный паттерном, обходит проверку
        # шаблона в visit_Call: имя атрибута приходит из строки.
        (
            "match 'x':\n"
            "    case str(format=bound):\n"
            "        print(bound('{0.__init__.__globals__}', object))\n"
        ),
        (
            "match 'x':\n"
            "    case str(format_map=bound):\n"
            "        print(bound('{0.__class__}', [1]))\n"
        ),
        # Служебные имена нельзя связывать и через pattern-matching.
        "match 1:\n    case __builtins__:\n        print('bound')\n",
        "match {'a': 1}:\n    case {**__builtins__}:\n        print('bound')\n",
        "try:\n    raise ValueError('x')\nexcept ValueError as __builtins__:\n    pass\n",
        "def __builtins__(value):\n    return value\n",
        "class __builtins__:\n    pass\n",
        "__name__ = 'os'\nprint(__name__)\n",
    ],
)
def test_pattern_and_binding_bypasses_rejected(code: str) -> None:
    result = run_code("print('до запуска')\n" + code, [])
    assert result["correct"] is False
    assert result["error"] is not None
    assert result["stdout"] == ""


@pytest.mark.parametrize(
    "code",
    [
        # enum.pickle_by_enum_name возвращает настоящий builtins.getattr.
        (
            "from enum import Enum, pickle_by_enum_name\n"
            "import json\n"
            "class E(Enum):\n"
            "    A = 1\n"
            "g = pickle_by_enum_name(E.A, None)[0]\n"
            "print(g(json.dumps, '__globals__')['__builtins__']['__import__']('os').getcwd())\n"
        ),
        "import enum\nprint(enum.pickle_by_enum_name)\n",
        # wraps/update_wrapper вызывают getattr по строкам из assigned/updated.
        (
            "import functools, json\n"
            "class Sink:\n"
            "    pass\n"
            "sink = Sink()\n"
            "functools.update_wrapper("
            "sink, json.dumps, assigned=('__globals__',), updated=())\n"
            "print(sink.__globals__['__builtins__']['__import__']('os').getcwd())\n"
        ),
        (
            "import functools, json\n"
            "class Sink:\n"
            "    pass\n"
            "sink = Sink()\n"
            "functools.wraps(json.dumps, assigned=('__globals__',))(sink)\n"
        ),
        (
            "from functools import update_wrapper\n"
            "import json\n"
            "class Sink:\n"
            "    pass\n"
            "sink = Sink()\n"
            "update_wrapper(sink, json.dumps, ('__globals__',), ())\n"
        ),
        # make_dataclass позволяет объявить поле __traceback__, а replace()
        # затем достаёт из исключения traceback -> frame -> реальные builtins.
        (
            "from dataclasses import make_dataclass, replace\n"
            "D = make_dataclass("
            "'D', [('__traceback__', object)], bases=(Exception,))\n"
            "class E(D):\n"
            "    def __init__(self, *args, **kwargs):\n"
            "        traceback = kwargs['__traceback__']\n"
            "        real = traceback.tb_frame.f_back.f_globals['__builtins__']\n"
            "        print(real.open('/etc/hostname').read())\n"
            "caught = None\n"
            "try:\n"
            "    raise E()\n"
            "except E as error:\n"
            "    caught = error\n"
            "replace(caught)\n"
        ),
        "import dataclasses\nprint(dataclasses.make_dataclass)\n",
        "from dataclasses import make_dataclass\n",
        # EnumType.mro(EnumType) содержит настоящий type.
        (
            "import enum\n"
            "type_ = enum.EnumType.mro(enum.EnumType)[1]\n"
            "D = type_('D', (Exception,), {'__match_args__': ('__traceback__',)})\n"
            "caught = None\n"
            "try:\n"
            "    raise D()\n"
            "except D as error:\n"
            "    caught = error\n"
            "match caught:\n"
            "    case D(traceback):\n"
            "        real = traceback.tb_frame.f_back.f_globals['__builtins__']\n"
            "        print(real.open('/etc/hostname').read())\n"
        ),
        "import enum\nprint(enum.EnumType)\n",
        "from enum import EnumType\n",
        "import enum\nprint(enum.global_enum)\n",
        "from enum import global_enum\n",
        # typing.Type/get_origin и метаклассы из typing тоже дают type.
        "import typing\nprint(typing.get_origin(typing.Type))\n",
        "import typing\nprint(typing.Type)\n",
        "class Meta(typing.Type):\n    pass\n",
        "from typing import Type\n",
        "from typing import ABCMeta\n",
        "from typing import NamedTupleMeta\n",
        # TypedDict создаёт __annotations__ с dunder-полями; dataclass.fields
        # затем отдаёт метакласс через Field.default.
        (
            "from typing import TypedDict\n"
            "from dataclasses import dataclass, fields\n"
            "T = TypedDict('T', {'__class__': object})\n"
            "meta = fields(dataclass(T))[0].default\n"
            "type_ = meta.mro(meta)[1]\n"
            "D = type_('D', (Exception,), {'__match_args__': ('__traceback__',)})\n"
            "caught = None\n"
            "try:\n"
            "    raise D()\n"
            "except D as error:\n"
            "    caught = error\n"
            "match caught:\n"
            "    case D(traceback):\n"
            "        real = traceback.tb_frame.f_back.f_globals['__builtins__']\n"
            "        print(real.open('/etc/hostname').read())\n"
        ),
        "import typing\nprint(typing.TypedDict)\n",
        # Кадр генератора, которым управляет функция стандартной библиотеки,
        # отдаёт f_builtins через публичные gi_frame/f_back.
        (
            "import statistics\n"
            "holder = {}\n"
            "def gen():\n"
            "    back = holder['g'].gi_frame.f_back\n"
            "    print(back.f_builtins['open']('/etc/hostname').read())\n"
            "    yield 1\n"
            "generator = gen()\n"
            "holder['g'] = generator\n"
            "statistics.mean(generator)\n"
        ),
        # format-строка тоже не должна доставать публичные имена кадров.
        (
            "def gen():\n"
            "    yield 1\n"
            "generator = gen()\n"
            "print('{0.gi_frame.f_back.f_builtins}'.format(generator))\n"
        ),
    ],
)
def test_import_and_reflection_bypasses_rejected(code: str) -> None:
    result = run_code("print('до запуска')\n" + code, [])
    assert result["correct"] is False
    assert result["error"] is not None
    assert result["stdout"] == ""


def test_destructor_output_does_not_spoof_runner_result() -> None:
    code = (
        "class SecondVoice:\n"
        "    def __del__(self):\n"
        '        print(\'{"ok": true, "checks": [], "stdout": "подделка"}\')\n'
        "second_voice = SecondVoice()\n"
        "print('настоящий')\n"
    )
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].strip() == "настоящий"


def test_generators_still_work_without_frame_introspection() -> None:
    code = (
        "def countdown(start):\n"
        "    while start > 0:\n"
        "        yield start\n"
        "        start -= 1\n"
        "print(list(countdown(3)))\n"
        "print(sum(statistics.mean([1, 2, 3]) for _ in range(1)))\n"
    )
    # statistics импортируется отдельно, чтобы не смешивать проверки.
    code = "import statistics\n" + code
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].splitlines() == ["[3, 2, 1]", "2"]


def test_functools_wraps_does_not_leak_real_update_wrapper() -> None:
    result = run_code("import functools\nprint(functools.wraps(lambda: None).func)\n", [])
    assert result["error"] is not None
    assert result["stdout"] == ""


def test_functools_wraps_still_works_for_decorators() -> None:
    code = (
        "import functools\n"
        "def traced(function):\n"
        "    @functools.wraps(function)\n"
        "    def wrapper(*args, **kwargs):\n"
        "        return function(*args, **kwargs)\n"
        "    return wrapper\n"
        "@traced\n"
        "def double(value):\n"
        "    return value * 2\n"
        "print(double(3), double.__name__)\n"
    )
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].strip() == "6 double"


def test_public_class_patterns_still_work() -> None:
    code = (
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Point:\n"
        "    x: int\n"
        "    y: int\n"
        "match Point(2, 3):\n"
        "    case Point(x=2, y=value):\n"
        "        print(value)\n"
        "match {'name': 'Ира'}:\n"
        "    case {'name': name}:\n"
        "        print(name)\n"
    )
    result = run_code(code, [])
    assert result["error"] is None
    assert result["stdout"].splitlines() == ["3", "Ира"]
