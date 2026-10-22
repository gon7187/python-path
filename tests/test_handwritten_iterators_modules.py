import ast
import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, normalize, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_iterators_modules"
MODULE_PATH = APP_DIR / "handwritten" / "lessons_iterators_modules.py"
LESSON_SPECS = {
    "iterators-iterable": (49, "Iterable и iterator"),
    "iterators-stop-iteration": (50, "Конец итерации"),
    "iterators-yield": (51, "Генераторы с yield"),
    "iterators-generator-expression": (52, "Генераторное выражение"),
    "modules-imports": (53, "Импорт модулей"),
    "modules-main-guard": (54, "Точка входа"),
    "modules-packages": (55, "Пакеты"),
    "modules-stdlib-imports": (56, "Стандартная библиотека"),
}
LESSON_IDS = list(LESSON_SPECS)
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
OUTPUT_QUESTION_WORDS = ("выведет", "напечатает", "вывод")
MAIN_GUARDS = ("__name__ == '__main__'", "'__main__' == __name__")


def _lessons_by_id() -> dict[str, dict[str, Any]]:
    assert MODULE_PATH.is_file(), f"нет файла {MODULE_PATH.name} в app/handwritten"
    lessons = getattr(importlib.import_module(MODULE_NAME), "LESSONS", None)
    assert isinstance(lessons, list), "LESSONS должен быть списком уроков"
    for lesson in lessons:
        assert isinstance(lesson, dict), lesson
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
    """Возвращает строки вывода из комментария «# Вывод:» или None, если его нет."""
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


def _callee(call: ast.Call) -> str | None:
    return call.func.id if isinstance(call.func, ast.Name) else None


def _check_code_task(
    lesson_id: str, function_name: str, params: list[str], tests: list[dict]
) -> ast.Module:
    code = _lesson(lesson_id)["questions"][2]
    assert code["id"] == f"{lesson_id}-code", lesson_id
    assert code["kind"] == "code", lesson_id

    reference_tree = ast.parse(code["reference"])
    reference_function = _function(reference_tree, function_name)
    assert reference_function is not None, (lesson_id, function_name)
    assert _param_names(reference_function) == params, lesson_id

    starter_function = _function(ast.parse(code["starter"]), function_name)
    assert starter_function is not None, (lesson_id, function_name)
    assert _param_names(starter_function) == params, lesson_id
    assert _nodes(starter_function, ast.Pass), (lesson_id, "starter без pass")

    result = run_code(code["reference"], tests)
    assert result["error"] is None, (lesson_id, result["error"])
    assert result["correct"] is True, (lesson_id, result["message"], result.get("checks"))
    return reference_tree


def test_c1_module_declares_the_eight_lessons() -> None:
    lessons = _lessons_by_id()
    assert sorted(lessons) == sorted(LESSON_IDS)


def test_c1_registry_and_course_expose_lessons_in_order() -> None:
    from app.content import LESSON_BY_ID, LESSONS

    registry = importlib.import_module("app.handwritten").HANDWRITTEN
    for lesson_id, (order, title) in LESSON_SPECS.items():
        assert lesson_id in registry, lesson_id
        assert lesson_id in LESSON_BY_ID, lesson_id
        lesson = LESSON_BY_ID[lesson_id]
        assert lesson["order"] == order, lesson_id
        assert lesson["title"] == title, lesson_id
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
    assert all(len(answer) <= 80 for answer in term["answers"]), (lesson_id, "ответ не короткий")
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
def test_c3_choice_checks_understanding(lesson_id: str) -> None:
    choice = _lesson(lesson_id)["questions"][0]
    prompt = choice["prompt"].casefold()
    assert any(word in prompt for word in UNDERSTANDING_WORDS), (lesson_id, choice["prompt"])

    options = choice["options"]
    assert 3 <= len(options) <= 4, lesson_id

    has_ticks = ["`" in option for option in options]
    assert all(has_ticks) or not any(has_ticks), (lesson_id, "бэктики только у части вариантов")

    lengths = [len(option) for option in options]
    assert max(lengths) <= 1.6 * min(lengths), (lesson_id, "варианты разной длины")
    other_lengths = [len(option) for option in options if option != choice["answer"]]
    assert min(other_lengths) <= len(choice["answer"]) <= max(other_lengths), lesson_id

    if any(word in prompt for word in OUTPUT_QUESTION_WORDS):
        code = choice["prompt"].partition("\n")[2]
        result = run_code(code, [])
        if result["error"] is None:
            assert normalize(result["stdout"]) == normalize(choice["answer"]), (
                lesson_id,
                result["stdout"],
            )
        else:
            answer = choice["answer"].casefold()
            assert "ошиб" in answer or "error" in answer, (lesson_id, choice["answer"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_examples_have_real_output_and_card_order(lesson_id: str) -> None:
    theory = _lesson(lesson_id)["theory"]

    typical_error = theory[2]
    assert "ошиб" in f"{typical_error['title']} {typical_error['text']}".casefold(), lesson_id

    for card in theory:
        expected = _expected_output(card["example"])
        assert expected is not None, (lesson_id, card["title"], "нет комментария «# Вывод:»")
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        actual = [line.rstrip() for line in result["stdout"].splitlines()]
        assert actual == [line.rstrip() for line in expected], (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_flag_matches_runner_capability(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert "run" not in card or card["run"] is False, (lesson_id, card["title"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"], "пример исполняется")
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k49_take_reads_first_items_with_iter_and_next() -> None:
    tests = [
        {"kind": "call", "call": "take('abc', 2)", "expected": ["a", "b"]},
        {"kind": "call", "call": "take((c for c in 'abc'), 2)", "expected": ["a", "b"]},
        {"kind": "call", "call": "take(range(10), 3)", "expected": [0, 1, 2]},
        {"kind": "call", "call": "take([1], 5)", "expected": [1]},
    ]
    tree = _check_code_task("iterators-iterable", "take", ["iterable", "n"], tests)
    function = _function(tree, "take")
    assert function is not None
    called = {_callee(call) for call in _nodes(function, ast.Call)}
    assert {"iter", "next"} <= called, "нужны iter() и next()"
    assert not _nodes(function, ast.Slice), "срезы в этом задании запрещены"


def test_k50_safe_next_returns_default_on_stop_iteration() -> None:
    tests = [
        {
            "kind": "call",
            "call": "(lambda it: [safe_next(it, 0), safe_next(it, 0)])(iter([1]))",
            "expected": [1, 0],
        },
    ]
    _check_code_task("iterators-stop-iteration", "safe_next", ["iterator", "default"], tests)


def test_k51_countdown_is_generator_with_yield() -> None:
    tests = [
        {"kind": "call", "call": "list(countdown(3))", "expected": [3, 2, 1]},
        {"kind": "call", "call": "list(countdown(0))", "expected": []},
    ]
    tree = _check_code_task("iterators-yield", "countdown", ["n"], tests)
    function = _function(tree, "countdown")
    assert function is not None
    assert _nodes(function, ast.Yield), "countdown должен использовать yield"


def test_k52_total_length_sums_generator_expression() -> None:
    tests = [
        {"kind": "call", "call": "total_length(['ab', 'cde'])", "expected": 5},
        {"kind": "call", "call": "total_length([])", "expected": 0},
    ]
    tree = _check_code_task("iterators-generator-expression", "total_length", ["words"], tests)
    function = _function(tree, "total_length")
    assert function is not None
    sums = [call for call in _nodes(function, ast.Call) if _callee(call) == "sum"]
    assert any(call.args and isinstance(call.args[0], ast.GeneratorExp) for call in sums), (
        "нужен sum по генераторному выражению"
    )


def test_k53_circle_area_imports_math_and_rounds() -> None:
    tests = [
        {"kind": "call", "call": "circle_area(1)", "expected": 3.14},
        {"kind": "call", "call": "circle_area(2)", "expected": 12.57},
    ]
    tree = _check_code_task("modules-imports", "circle_area", ["r"], tests)
    imported = [alias.name for node in _nodes(tree, ast.Import) for alias in node.names]
    assert "math" in imported, "нужен import math"


def test_k54_main_is_called_only_under_main_guard() -> None:
    tests = [
        {"kind": "call", "call": "main()", "expected": "Готово"},
        {"kind": "stdout", "expected": ""},
    ]
    tree = _check_code_task("modules-main-guard", "main", [], tests)

    top_level_calls = [
        stmt.value
        for stmt in tree.body
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
    ]
    assert not any(_callee(call) == "main" for call in top_level_calls), (
        "main() не должен вызываться вне if __name__"
    )

    guards = [node for node in _nodes(tree, ast.If) if ast.unparse(node.test) in MAIN_GUARDS]
    assert any(_callee(call) == "main" for guard in guards for call in _nodes(guard, ast.Call)), (
        "main() должен стоять под if __name__ == '__main__'"
    )


def test_k55_module_path_maps_dotted_name_to_file() -> None:
    tests = [
        {"kind": "call", "call": "module_path('app.utils.text')", "expected": "app/utils/text.py"},
        {"kind": "call", "call": "module_path('main')", "expected": "main.py"},
    ]
    _check_code_task("modules-packages", "module_path", ["dotted"], tests)


def test_k56_most_common_word_uses_counter() -> None:
    tests = [
        {"kind": "call", "call": "most_common_word('кот Кот пёс')", "expected": "кот"},
    ]
    tree = _check_code_task("modules-stdlib-imports", "most_common_word", ["text"], tests)
    imported = [
        (node.module, alias.name) for node in _nodes(tree, ast.ImportFrom) for alias in node.names
    ]
    assert ("collections", "Counter") in imported, "нужен from collections import Counter"
