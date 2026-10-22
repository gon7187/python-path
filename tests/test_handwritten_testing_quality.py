import ast
import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_testing_quality"
MODULE_PATH = APP_DIR / "handwritten" / "lessons_testing_quality.py"
LESSON_SPECS = {
    "testing-unit-tests": (89, "Юнит-тесты"),
    "testing-fixtures": (90, "Подготовка данных"),
    "testing-parametrize": (91, "Параметризация"),
    "testing-mocks": (92, "Тестовые двойники"),
    "quality-pep8": (93, "Стиль кода"),
    "quality-format-lint": (94, "Форматтер и линтер"),
    "quality-docstrings": (95, "Документация"),
    "quality-git": (96, "Git-цикл"),
}
LESSON_IDS = list(LESSON_SPECS)
RUNNER_MODULES = frozenset(
    {
        "json",
        "re",
        "math",
        "statistics",
        "itertools",
        "functools",
        "collections",
        "datetime",
        "decimal",
        "fractions",
        "dataclasses",
        "enum",
        "heapq",
        "bisect",
        "random",
    }
)
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARKER = "# Вывод:"
UNDERSTANDING_WORDS = (
    "вывод",
    "выведет",
    "вернёт",
    "напечатает",
    "будет",
    "ошиб",
    "выбери",
    "найди",
    "какой код",
)


def _lessons_by_id() -> dict[str, dict[str, Any]]:
    assert MODULE_PATH.is_file(), f"нет файла {MODULE_PATH.name} в app/handwritten"
    lessons = importlib.import_module(MODULE_NAME).LESSONS
    assert isinstance(lessons, list), "LESSONS должен быть списком уроков"
    return {lesson.get("id"): lesson for lesson in lessons}


def _lesson(lesson_id: str) -> dict[str, Any]:
    lessons = _lessons_by_id()
    assert lesson_id in lessons, f"в {MODULE_NAME} нет урока {lesson_id}"
    return lessons[lesson_id]


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _expected_output(example: str) -> list[str] | None:
    lines = example.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith(OUTPUT_MARKER):
            continue
        expected: list[str] = []
        inline = line.strip()[len(OUTPUT_MARKER) :].strip()
        if inline:
            expected.append(inline)
        for comment in lines[index + 1 :]:
            stripped = comment.strip()
            if not stripped.startswith("#"):
                break
            expected.append(stripped[1:].strip())
        return expected
    return None


def _outside_runner(example: str) -> bool:
    for node in ast.walk(ast.parse(example)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"open", "input"}:
                return True
            continue
        elif isinstance(node, ast.AsyncFunctionDef | ast.Await):
            return True
        else:
            continue
        if any(name.split(".")[0] not in RUNNER_MODULES for name in names):
            return True
    return False


def _function(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    return next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


def _param_names(function: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in function.args.args]


def _nodes(tree: ast.AST, node_type: type) -> list[Any]:
    return [node for node in ast.walk(tree) if isinstance(node, node_type)]


def _call(call: str, expected: Any) -> dict[str, Any]:
    return {"kind": "call", "call": call, "expected": expected}


def _check_task(
    lesson_id: str, name: str, params: list[str], tests: list[dict[str, Any]]
) -> ast.Module:
    code = _lesson(lesson_id)["questions"][2]
    assert code["id"] == f"{lesson_id}-code", lesson_id
    assert code["kind"] == "code", lesson_id

    reference = ast.parse(code["reference"])
    reference_function = _function(reference, name)
    assert reference_function is not None, (lesson_id, f"в reference нет {name}")
    assert _param_names(reference_function) == params, lesson_id

    starter = ast.parse(code["starter"])
    starter_function = _function(starter, name)
    assert starter_function is not None, (lesson_id, f"в starter нет {name}")
    assert _param_names(starter_function) == params, lesson_id
    assert _nodes(starter_function, ast.Pass), (lesson_id, "в starter нет pass")

    result = run_code(code["reference"], tests)
    assert result["error"] is None, (lesson_id, result["error"])
    assert result["correct"] is True, (lesson_id, result["checks"])
    return reference


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c1_module_declares_each_lesson(lesson_id: str) -> None:
    assert lesson_id in _lessons_by_id(), lesson_id


def test_c1_registry_and_course_keep_numbers_titles_and_120_lessons() -> None:
    from app.content import LESSON_BY_ID, LESSONS

    registry = importlib.import_module("app.handwritten").HANDWRITTEN
    for lesson_id, (order, title) in LESSON_SPECS.items():
        assert lesson_id in registry, lesson_id
        assert LESSON_BY_ID[lesson_id]["order"] == order, lesson_id
        assert LESSON_BY_ID[lesson_id]["title"] == title, lesson_id
    assert len(LESSONS) == 120


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_passes_handwritten_contract(lesson_id: str) -> None:
    lesson = _lesson(lesson_id)
    assert lesson["id"] == lesson_id

    theory = lesson["theory"]
    assert isinstance(theory, list) and len(theory) == 3, lesson_id
    for card in theory:
        for key in ("title", "text", "example"):
            assert isinstance(card.get(key), str) and card[key].strip(), (lesson_id, key)
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])

    questions = lesson["questions"]
    assert [question["id"] for question in questions] == [
        f"{lesson_id}-choice",
        f"{lesson_id}-term",
        f"{lesson_id}-code",
    ]
    assert [question["kind"] for question in questions] == ["choice", "input", "code"]
    choice, term, code = questions

    assert len(set(choice["options"])) >= 3, lesson_id
    assert choice["answer"] in choice["options"], lesson_id
    assert choice["explanation"].strip(), lesson_id

    assert isinstance(term["answers"], list) and term["answers"], lesson_id
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"])
    assert term["explanation"].strip(), lesson_id

    assert len(code["tests"]) >= 2, lesson_id
    assert code["hint"].strip(), lesson_id
    assert code["explanation"].strip(), lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_and_examples_check_understanding(lesson_id: str) -> None:
    lesson = _lesson(lesson_id)
    theory = lesson["theory"]

    typical_error = theory[2]
    assert "ошиб" in f"{typical_error['title']} {typical_error['text']}".casefold(), lesson_id

    for card in theory:
        expected = _expected_output(card["example"])
        assert expected, (lesson_id, card["title"], "нет комментария «# Вывод:» с выводом")
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        actual = [line.rstrip() for line in result["stdout"].splitlines()]
        assert actual == [line.rstrip() for line in expected], (lesson_id, card["title"])

    choice = lesson["questions"][0]
    prompt = choice["prompt"]
    assert any(word in prompt.casefold() for word in UNDERSTANDING_WORDS), prompt

    options = choice["options"]
    has_ticks = ["`" in option for option in options]
    assert all(has_ticks) or not any(has_ticks), (lesson_id, "бэктики только у части вариантов")

    lengths = [len(option) for option in options]
    assert max(lengths) <= 1.6 * min(lengths), (lesson_id, "варианты разной длины")
    other_lengths = [len(option) for option in options if option != choice["answer"]]
    assert min(other_lengths) <= len(choice["answer"]) <= max(other_lengths), lesson_id

    code = prompt.split("\n\n", 1)[1]
    result = run_code(code, [])
    assert result["error"] is None, (lesson_id, result["error"])
    assert result["stdout"].strip() == choice["answer"], (lesson_id, result["stdout"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_flag_matches_runner_capability(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert "run" not in card or card["run"] is False, (lesson_id, card["title"])
        outside = _outside_runner(card["example"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert outside, (lesson_id, card["title"], "пример укладывается в раннер")
            assert result["error"] is not None, (lesson_id, card["title"], "пример исполняется")
        else:
            assert not outside, (lesson_id, card["title"], "пример раннер не исполнит")
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k89_is_palindrome_ignores_case_and_test_has_asserts() -> None:
    tests = [
        _call("is_palindrome('Шалаш') is True", True),
        _call("is_palindrome('кот') is False", True),
        _call("test_is_palindrome()", None),
    ]
    tree = _check_task("testing-unit-tests", "is_palindrome", ["s"], tests)
    test_function = _function(tree, "test_is_palindrome")
    assert test_function is not None, "в reference нет test_is_palindrome"
    assert len(_nodes(test_function, ast.Assert)) >= 3, "нужно минимум три assert"


def test_k90_make_cart_returns_new_empty_cart_each_call() -> None:
    tests = [
        _call("make_cart() == {'items': [], 'total': 0}", True),
        _call("(make_cart() is not make_cart()) is True", True),
    ]
    _check_task("testing-fixtures", "make_cart", [], tests)


def test_k91_failed_cases_returns_inputs_that_break_expectation() -> None:
    tests = [
        _call("failed_cases(abs, [(-1, 1), (2, 2), (3, -3)]) == [3]", True),
        _call("failed_cases(abs, []) == []", True),
    ]
    _check_task("testing-parametrize", "failed_cases", ["func", "cases"], tests)


def test_k92_welcome_sends_greeting_through_fake_and_returns_true() -> None:
    fake_send_check = "(lambda log: (welcome('Аня', log.append), log)[1])([]) == ['Привет, Аня!']"
    tests = [
        _call(fake_send_check, True),
        _call("welcome('Аня', lambda text: None) is True", True),
    ]
    _check_task("testing-mocks", "welcome", ["name", "send"], tests)


def test_k93_average_speed_rounds_to_one_digit() -> None:
    tests = [
        _call("average_speed(120, 1.5) == 80.0", True),
        _call("average_speed(10, 4) == 2.5", True),
    ]
    tree = _check_task("quality-pep8", "average_speed", ["distance_km", "hours"], tests)
    function = _function(tree, "average_speed")
    assert function is not None, "в reference нет average_speed"
    rounds = [
        call
        for call in _nodes(function, ast.Call)
        if isinstance(call.func, ast.Name) and call.func.id == "round"
    ]
    assert len(rounds) == 1 and len(rounds[0].args) == 2, "нужен round(..., 1)"


def test_k94_unused_names_returns_sorted_defined_minus_used() -> None:
    tests = [
        _call("unused_names(['a', 'b', 'c'], ['a']) == ['b', 'c']", True),
        _call("unused_names(['b', 'a'], []) == ['a', 'b']", True),
    ]
    _check_task("quality-format-lint", "unused_names", ["defined", "used"], tests)


def test_k95_celsius_to_f_has_docstring_with_example() -> None:
    tests = [
        _call("celsius_to_f(100) == 212.0", True),
        _call("celsius_to_f(0) == 32.0", True),
    ]
    tree = _check_task("quality-docstrings", "celsius_to_f", ["c"], tests)
    function = _function(tree, "celsius_to_f")
    assert function is not None, "в reference нет celsius_to_f"
    docstring = ast.get_docstring(function)
    assert docstring is not None, "нужна докстринга"
    assert "celsius_to_f(" in docstring, "в докстринге нужен пример вызова"
    reference = _lesson("quality-docstrings")["questions"][2]["reference"]
    assert '"""' in reference, "докстринга должна быть в тройных кавычках"


def test_k96_commit_message_ok_checks_first_line_length_and_dot() -> None:
    tests = [
        _call("commit_message_ok('Добавить поиск') is True", True),
        _call("commit_message_ok('') is False", True),
        _call("commit_message_ok('Фикс.') is False", True),
        _call("commit_message_ok('а' * 50) is True", True),
        _call("commit_message_ok('а' * 51) is False", True),
        _call("commit_message_ok('\\nВторая строка') is False", True),
    ]
    _check_task("quality-git", "commit_message_ok", ["msg"], tests)
