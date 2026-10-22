import ast
import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_scope_comprehensions"
MODULE_PATH = APP_DIR / "handwritten" / "lessons_scope_comprehensions.py"
LESSON_SPECS = {
    "scope-legb": (41, "Правило LEGB"),
    "scope-mutable-default": (42, "Ловушка изменяемого default"),
    "scope-closures": (43, "Замыкания"),
    "scope-lambda-key": (44, "lambda и key"),
    "comprehensions-list-comprehension": (45, "List comprehension"),
    "comprehensions-comprehension-filter": (46, "Фильтр в генераторе"),
    "comprehensions-dict-comprehension": (47, "Dict и set comprehension"),
    "comprehensions-nested-comprehension": (48, "Вложенные генераторы"),
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


def _nodes(tree: ast.AST | None, node_type: type) -> list[Any]:
    if tree is None:
        return []
    return [node for node in ast.walk(tree) if isinstance(node, node_type)]


def _check_code_task(
    lesson_id: str, function_name: str, params: list[str], tests: list[dict]
) -> ast.Module:
    code = _lesson(lesson_id)["questions"][2]
    assert code["id"] == f"{lesson_id}-code"
    assert code["kind"] == "code"

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
    assert result["correct"] is True, (lesson_id, result["message"], result["checks"])
    return reference_tree


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
    prompt = choice["prompt"].casefold()
    assert any(word in prompt for word in UNDERSTANDING_WORDS), (lesson_id, choice["prompt"])

    options = choice["options"]
    has_ticks = ["`" in option for option in options]
    assert all(has_ticks) or not any(has_ticks), (lesson_id, "бэктики только у части вариантов")

    lengths = [len(option) for option in options]
    assert max(lengths) <= 1.6 * min(lengths), (lesson_id, "варианты разной длины")
    other_lengths = [len(option) for option in options if option != choice["answer"]]
    assert min(other_lengths) <= len(choice["answer"]) <= max(other_lengths), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_flag_matches_runner_capability(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert "run" not in card or card["run"] is False, (lesson_id, card["title"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"], "пример исполняется")
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k41_price_with_tax_reads_global_tax() -> None:
    tests = [
        {"kind": "call", "call": "price_with_tax(100)", "expected": 120.0},
        {"kind": "call", "call": "price_with_tax(0)", "expected": 0.0},
    ]
    tree = _check_code_task("scope-legb", "price_with_tax", ["price"], tests)

    tax_assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "TAX" for target in node.targets)
    ]
    assert tax_assignments, "reference должен объявлять глобальный TAX"
    assert isinstance(tax_assignments[0].value, ast.Constant), "TAX должен быть константой"
    assert tax_assignments[0].value.value == 0.2

    function = _function(tree, "price_with_tax")
    assert function is not None
    names = _nodes(function, ast.Name)
    assert any(name.id == "TAX" and isinstance(name.ctx, ast.Load) for name in names)
    assert not any(name.id == "TAX" and isinstance(name.ctx, ast.Store) for name in names)


def test_k42_add_item_has_no_mutable_default() -> None:
    tests = [
        {"kind": "call", "call": "add_item('a')", "expected": ["a"]},
        {"kind": "call", "call": "add_item('b')", "expected": ["b"]},
        {"kind": "call", "call": "add_item('c', ['x'])", "expected": ["x", "c"]},
    ]
    tree = _check_code_task("scope-mutable-default", "add_item", ["item", "basket"], tests)

    function = _function(tree, "add_item")
    assert function is not None
    assert len(function.args.defaults) == 1, "basket должен иметь одно значение по умолчанию"
    default = function.args.defaults[0]
    assert isinstance(default, ast.Constant) and default.value is None, "default должен быть None"


def test_k43_make_multiplier_returns_closure() -> None:
    tests = [
        {"kind": "call", "call": "make_multiplier(3)(4)", "expected": 12},
        {"kind": "call", "call": "make_multiplier(0)(9)", "expected": 0},
    ]
    tree = _check_code_task("scope-closures", "make_multiplier", ["k"], tests)

    function = _function(tree, "make_multiplier")
    assert function is not None
    inner = [
        node
        for node in ast.walk(function)
        if node is not function and isinstance(node, ast.FunctionDef | ast.Lambda)
    ]
    assert inner, "make_multiplier должен возвращать вложенную функцию"


def test_k44_by_last_letter_sorts_with_lambda_key() -> None:
    tests = [
        {
            "kind": "call",
            "call": "by_last_letter(['кот', 'дом', 'сад'])",
            "expected": ["сад", "дом", "кот"],
        },
        {"kind": "call", "call": "by_last_letter([])", "expected": []},
    ]
    tree = _check_code_task("scope-lambda-key", "by_last_letter", ["words"], tests)
    assert _nodes(tree, ast.Lambda), "reference должен использовать lambda"


def test_k45_squares_uses_list_comprehension() -> None:
    tests = [
        {"kind": "call", "call": "squares(4)", "expected": [1, 4, 9, 16]},
        {"kind": "call", "call": "squares(0)", "expected": []},
    ]
    tree = _check_code_task("comprehensions-list-comprehension", "squares", ["n"], tests)
    assert _nodes(_function(tree, "squares"), ast.ListComp), "нужен list comprehension"


def test_k46_evens_filters_inside_comprehension() -> None:
    tests = [
        {"kind": "call", "call": "evens([1, 2, 3, 4])", "expected": [2, 4]},
        {"kind": "call", "call": "evens([])", "expected": []},
    ]
    tree = _check_code_task("comprehensions-comprehension-filter", "evens", ["items"], tests)
    comprehensions = _nodes(_function(tree, "evens"), ast.ListComp)
    assert any(gen.ifs for comp in comprehensions for gen in comp.generators), (
        "нужен if в генераторе"
    )


def test_k47_initials_uses_set_comprehension() -> None:
    tests = [
        {
            "kind": "call",
            "call": "initials(['Аня', 'антон', 'Борис']) == {'а', 'б'}",
            "expected": True,
        },
        {"kind": "call", "call": "initials([]) == set()", "expected": True},
    ]
    tree = _check_code_task("comprehensions-dict-comprehension", "initials", ["words"], tests)
    assert _nodes(_function(tree, "initials"), ast.SetComp), "нужен set comprehension"


def test_k48_flatten_uses_nested_generators() -> None:
    tests = [
        {"kind": "call", "call": "flatten([[1, 2], [3], []])", "expected": [1, 2, 3]},
        {"kind": "call", "call": "flatten([])", "expected": []},
    ]
    tree = _check_code_task("comprehensions-nested-comprehension", "flatten", ["matrix"], tests)
    comprehensions = _nodes(_function(tree, "flatten"), ast.ListComp)
    assert any(len(comp.generators) >= 2 for comp in comprehensions), "нужны вложенные for"
