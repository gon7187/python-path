"""Проверки рукописных уроков 33–40: цепочки elif, match, циклы и параметры функций."""

import ast
import importlib
import re
from types import ModuleType
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

MODULE_NAME = "app.handwritten.lessons_flow_functions"
FLOW_LESSONS = [
    (33, "flow-advanced-elif", "Цепочки elif"),
    (34, "flow-advanced-match", "match/case"),
    (35, "flow-advanced-break-continue", "break и continue"),
    (36, "flow-advanced-loop-else", "else у цикла"),
    (37, "functions-pro-parameters", "Параметры"),
    (38, "functions-pro-defaults", "Значения по умолчанию"),
    (39, "functions-pro-keyword-args", "Именованные аргументы"),
    (40, "functions-pro-varargs", "*args и **kwargs"),
]
LESSON_IDS = [lesson_id for _, lesson_id, _ in FLOW_LESSONS]
ELIF_ID = "flow-advanced-elif"
MATCH_ID = "flow-advanced-match"
BREAK_ID = "flow-advanced-break-continue"
LOOP_ELSE_ID = "flow-advanced-loop-else"
RECT_ID = "functions-pro-parameters"
DEFAULTS_ID = "functions-pro-defaults"
KEYWORD_ID = "functions-pro-keyword-args"
VARARGS_ID = "functions-pro-varargs"

MARKER = "# Вывод:"
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
PREDICT_WORDS = ("выведет", "будет", "верн", "ошиб", "результат")
# Темы, которые раннер учебного редактора не покажет: файлы, системные функции, импорт, потоки, asyncio.
RUNNER_BLOCKED_TOPIC = re.compile(
    r"\bopen\(|\binput\(|\bimport\b|\basync\b|\bawait\b|\bthreading\b|\bThread\(|\bos\b"
    r"|\bsqlite3\b|\bunittest\b|\bargparse\b"
)


def _import_or_fail(name: str) -> ModuleType:
    try:
        return importlib.import_module(name)
    except Exception as error:
        raise AssertionError(f"модуль {name} не импортируется: {error!r}") from error


def _handwritten_lesson(lesson_id: str) -> dict[str, Any]:
    registry = _import_or_fail("app.handwritten").HANDWRITTEN
    assert lesson_id in registry, f"нет рукописного урока {lesson_id}"
    return registry[lesson_id]


def _cards(lesson_id: str) -> list[dict[str, Any]]:
    return _handwritten_lesson(lesson_id).get("theory", [])


def _question(lesson_id: str, suffix: str) -> dict[str, Any]:
    question_id = f"{lesson_id}-{suffix}"
    matches = [
        question
        for question in _handwritten_lesson(lesson_id).get("questions", [])
        if question.get("id") == question_id
    ]
    assert matches, f"нет задания {question_id}"
    return matches[0]


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _parse(source: str) -> ast.Module:
    try:
        return ast.parse(source)
    except SyntaxError as error:
        raise AssertionError(f"код не разбирается: {error}") from error


def _function(source: str, name: str) -> ast.FunctionDef:
    for node in _parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"в решении нет функции {name}")


def _positional(node: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args]


def _has_node(source: str, node_type: type, check: Any = lambda node: True) -> bool:
    return any(isinstance(node, node_type) and check(node) for node in ast.walk(_parse(source)))


def _call_tests(pairs: list[tuple[str, Any]]) -> list[dict[str, Any]]:
    return [{"kind": "call", "call": call, "expected": expected} for call, expected in pairs]


def _assert_reference_passes(lesson_id: str, pairs: list[tuple[str, Any]]) -> None:
    reference = _question(lesson_id, "code")["reference"]
    result = run_code(reference, _call_tests(pairs))
    assert result["correct"] is True, (result["message"], result["error"], result.get("checks"))


def _declared_output(example: str) -> list[str]:
    """Собирает вывод, объявленный комментариями «# Вывод:» и продолжающими их строками."""
    lines = example.splitlines()
    declared: list[str] = []
    for index, line in enumerate(lines):
        if MARKER not in line:
            continue
        tail = line.split(MARKER, 1)[1].strip()
        if tail:
            declared.append(tail)
        for follow in lines[index + 1 :]:
            stripped = follow.strip()
            if not stripped.startswith("#") or MARKER in follow:
                break
            declared.append(stripped.lstrip("#").strip())
    return [item for item in declared if item]


def _printed_lines(stdout: str) -> list[str]:
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def test_c1_module_declares_flow_and_function_lessons() -> None:
    module = _import_or_fail(MODULE_NAME)
    lessons = getattr(module, "LESSONS", None)
    assert isinstance(lessons, list), "модуль должен объявлять LESSONS"
    assert {lesson.get("id") for lesson in lessons} == set(LESSON_IDS)
    assert len(lessons) == len(LESSON_IDS)

    registry = _import_or_fail("app.handwritten").HANDWRITTEN
    assert set(LESSON_IDS) <= set(registry)

    content = _import_or_fail("app.content")
    assert len(content.LESSONS) == 120
    for order, lesson_id, title in FLOW_LESSONS:
        assert lesson_id in content.LESSON_BY_ID, lesson_id
        lesson = content.LESSON_BY_ID[lesson_id]
        assert (lesson["order"], lesson["title"]) == (order, title), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_has_three_cards_questions_and_checked_code_task(lesson_id: str) -> None:
    lesson = _handwritten_lesson(lesson_id)
    assert lesson.get("id") == lesson_id

    theory = lesson.get("theory")
    assert isinstance(theory, list) and len(theory) == 3, lesson_id
    for card in theory:
        for key in ("title", "text", "example"):
            assert isinstance(card.get(key), str) and card[key].strip(), (lesson_id, key)
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])

    questions = lesson.get("questions", [])
    assert [question.get("id") for question in questions] == [
        f"{lesson_id}-choice",
        f"{lesson_id}-term",
        f"{lesson_id}-code",
    ]
    assert [question.get("kind") for question in questions] == ["choice", "input", "code"]
    choice, term, code = questions

    assert len(set(choice["options"])) >= 3, lesson_id
    assert choice["answer"] in choice["options"], lesson_id
    assert isinstance(choice.get("explanation"), str) and choice["explanation"].strip()

    assert isinstance(term["answers"], list) and len(term["answers"]) >= 2, lesson_id
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"])
    assert isinstance(term.get("explanation"), str) and term["explanation"].strip()

    assert len(code["tests"]) >= 2, lesson_id
    for key in ("hint", "explanation"):
        assert isinstance(code.get(key), str) and code[key].strip(), (lesson_id, key)
    starter_tree = _parse(code["starter"])
    assert any(isinstance(node, ast.FunctionDef) for node in starter_tree.body), lesson_id
    assert any(isinstance(node, ast.Pass) for node in ast.walk(starter_tree)), lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_predicts_output_with_alike_options(lesson_id: str) -> None:
    choice = _question(lesson_id, "choice")
    prompt = choice["prompt"].casefold()
    assert any(word in prompt for word in PREDICT_WORDS), (lesson_id, choice["prompt"])

    options = choice["options"]
    answer = choice["answer"]
    assert 3 <= len(options) <= 4, lesson_id
    assert len(set(options)) == len(options), lesson_id
    assert len({"`" in option for option in options}) == 1, (lesson_id, "оформление вариантов")
    lengths = [len(option) for option in options]
    assert max(lengths) <= 2 * min(lengths), (lesson_id, lengths)
    assert not (len(answer) == max(lengths) and lengths.count(len(answer)) == 1), lesson_id
    assert not (len(answer) == min(lengths) and lengths.count(len(answer)) == 1), lesson_id

    cards = _cards(lesson_id)
    assert len(cards) == 3, lesson_id
    for card in cards:
        assert MARKER in card["example"], (lesson_id, card["title"])
    for card in cards:
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])
        declared = _declared_output(card["example"])
        assert declared == _printed_lines(result["stdout"]), (lesson_id, card["title"])

    last_card = cards[2]
    assert "ошиб" in f"{last_card['title']} {last_card['text']}".casefold(), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_cannot_run(lesson_id: str) -> None:
    for card in _cards(lesson_id):
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"])
            assert RUNNER_BLOCKED_TOPIC.search(card["example"]), (lesson_id, card["title"])
        else:
            assert card.get("run", True) is True, (lesson_id, card["title"])
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k33_grade_is_elif_chain_with_border_checks() -> None:
    reference = _question(ELIF_ID, "code")["reference"]
    assert _positional(_function(reference, "grade")) == ["score"]
    assert _has_node(
        reference,
        ast.If,
        lambda node: len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If),
    ), "в reference нет цепочки elif"
    _assert_reference_passes(
        ELIF_ID,
        [
            ("grade(90)", "отлично"),
            ("grade(89)", "хорошо"),
            ("grade(75)", "хорошо"),
            ("grade(74)", "зачёт"),
            ("grade(50)", "зачёт"),
            ("grade(49)", "незачёт"),
        ],
    )


def test_k34_command_matches_split_text() -> None:
    reference = _question(MATCH_ID, "code")["reference"]
    assert _positional(_function(reference, "command")) == ["text"]
    assert _has_node(reference, ast.Match), "в reference нет match"
    _assert_reference_passes(
        MATCH_ID,
        [
            ("command('go север')", "Иду: север"),
            ("command('stop')", "Стоп"),
            ("command('go')", "Не понял"),
            ("command('jump')", "Не понял"),
        ],
    )


def test_k35_first_long_breaks_on_first_match() -> None:
    reference = _question(BREAK_ID, "code")["reference"]
    assert _positional(_function(reference, "first_long")) == ["words", "n"]
    assert _has_node(reference, ast.Break), "в reference нет break"
    _assert_reference_passes(
        BREAK_ID,
        [
            ("first_long(['да', 'привет', 'кот'], 3)", "привет"),
            ("first_long(['да'], 3)", None),
        ],
    )


def test_k36_find_index_uses_for_else() -> None:
    reference = _question(LOOP_ELSE_ID, "code")["reference"]
    assert _positional(_function(reference, "find_index")) == ["items", "target"]
    assert _has_node(reference, ast.For, lambda node: bool(node.orelse)), (
        "в reference нет else у цикла"
    )
    _assert_reference_passes(
        LOOP_ELSE_ID,
        [
            ("find_index(['a', 'b'], 'b')", 1),
            ("find_index([], 'x')", -1),
        ],
    )


def test_k37_rect_area_multiplies_width_and_height() -> None:
    reference = _question(RECT_ID, "code")["reference"]
    assert _positional(_function(reference, "rect_area")) == ["width", "height"]
    _assert_reference_passes(
        RECT_ID,
        [
            ("rect_area(3, 4)", 12),
            ("rect_area(0, 5)", 0),
        ],
    )


def test_k38_greet_has_default_greeting() -> None:
    node = _function(_question(DEFAULTS_ID, "code")["reference"], "greet")
    assert _positional(node) == ["name", "greeting"]
    assert len(node.args.defaults) == 1
    assert isinstance(node.args.defaults[0], ast.Constant)
    assert node.args.defaults[0].value == "Привет"
    _assert_reference_passes(
        DEFAULTS_ID,
        [
            ("greet('Аня')", "Привет, Аня!"),
            ("greet('Аня', 'Здравствуй')", "Здравствуй, Аня!"),
        ],
    )


def test_k39_make_user_takes_age_and_city_by_keyword() -> None:
    node = _function(_question(KEYWORD_ID, "code")["reference"], "make_user")
    assert _positional(node) == ["name"]
    assert [arg.arg for arg in node.args.kwonlyargs] == ["age", "city"]
    _assert_reference_passes(
        KEYWORD_ID,
        [
            ("make_user('Аня', age=20)", {"name": "Аня", "age": 20, "city": "Москва"}),
            ("make_user('Ли', age=30, city='Казань')['city']", "Казань"),
        ],
    )


def test_k40_summary_collects_varargs_and_kwargs() -> None:
    node = _function(_question(VARARGS_ID, "code")["reference"], "summary")
    assert node.args.vararg is not None and node.args.vararg.arg == "scores"
    assert node.args.kwarg is not None and node.args.kwarg.arg == "meta"
    _assert_reference_passes(
        VARARGS_ID,
        [
            (
                "summary(3, 5, 4, subject='python')",
                {"count": 3, "best": 5, "subject": "python"},
            ),
            ("summary()", {"count": 0, "best": None}),
        ],
    )
