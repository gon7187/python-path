import importlib
import re
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_productivity_regex"
# Порядковый номер урока в курсе → (id рукописного урока, название в курсе)
EXPECTED_LESSONS = {
    81: ("stdlib-productivity-collections", "collections"),
    82: ("stdlib-productivity-itertools", "itertools"),
    83: ("stdlib-productivity-functools", "functools"),
    84: ("stdlib-productivity-heapq-bisect", "heapq и bisect"),
    85: ("regex-patterns", "Шаблоны re"),
    86: ("regex-groups", "Группы и именование"),
    87: ("regex-validation", "Валидация формата"),
    88: ("regex-substitution", "Замена и разделение"),
}
COLLECTIONS_ID = "stdlib-productivity-collections"
ITERTOOLS_ID = "stdlib-productivity-itertools"
FUNCTOOLS_ID = "stdlib-productivity-functools"
HEAPQ_ID = "stdlib-productivity-heapq-bisect"
PATTERNS_ID = "regex-patterns"
GROUPS_ID = "regex-groups"
VALIDATION_ID = "regex-validation"
SUBSTITUTION_ID = "regex-substitution"
LESSON_IDS = [lesson_id for lesson_id, _ in EXPECTED_LESSONS.values()]
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARK = "# Вывод:"
PREDICT_WORDS = ("выведет", "напечатает")


def _registry() -> dict[str, dict[str, Any]]:
    try:
        return importlib.import_module("app.handwritten").HANDWRITTEN
    except Exception as error:
        pytest.fail(f"реестр app.handwritten не импортируется: {error!r}")


def _course() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    try:
        content = importlib.import_module("app.content")
    except Exception as error:
        pytest.fail(f"app.content не импортируется: {error!r}")
    return content.LESSONS, content.LESSON_BY_ID


def _lesson(lesson_id: str) -> dict[str, Any]:
    registry = _registry()
    assert lesson_id in registry, f"нет рукописного урока {lesson_id}"
    return registry[lesson_id]


def _questions(lesson_id: str) -> list[dict[str, Any]]:
    questions = _lesson(lesson_id)["questions"]
    assert len(questions) == 3, lesson_id
    return questions


def _code_question(lesson_id: str) -> dict[str, Any]:
    code = _questions(lesson_id)[2]
    assert code["kind"] == "code", lesson_id
    return code


def _call(call: str, expected: Any) -> dict[str, Any]:
    return {"kind": "call", "call": call, "expected": expected}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _declared_output(example: str) -> list[str]:
    """Строки вывода из комментария «# Вывод:» — то, что пример должен напечатать."""
    lines = example.splitlines()
    marks = [index for index, line in enumerate(lines) if line.strip().startswith(OUTPUT_MARK)]
    if not marks:
        return []
    start = marks[0]
    declared = []
    head = lines[start].strip()[len(OUTPUT_MARK) :].strip()
    if head:
        declared.append(head)
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("#"):
            break
        text = stripped[1:].strip()
        if text:
            declared.append(text)
    return declared


def _prompt_code(prompt: str) -> str:
    """Код вопроса «Что выведет этот код?»: всё после первой строки."""
    head, _, code = prompt.partition("\n")
    assert any(word in head.casefold() for word in PREDICT_WORDS), prompt
    return code


def _assert_starter_signature(code: dict[str, Any], name: str) -> None:
    assert re.search(rf"^def {name}\(", code["starter"], re.MULTILINE), code["starter"]
    assert re.search(r"^\s+pass\s*$", code["starter"], re.MULTILINE), code["starter"]


def _assert_contract(lesson_id: str, lesson: dict[str, Any]) -> None:
    assert lesson["id"] == lesson_id

    theory = lesson["theory"]
    assert len(theory) == 3, lesson_id
    for card in theory:
        for key in ("title", "text", "example"):
            assert isinstance(card.get(key), str) and card[key].strip(), (lesson_id, key)
    for card in theory:
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

    assert isinstance(term["answers"], list) and term["answers"], lesson_id
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"])

    assert len(code["tests"]) >= 2, lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


def test_c1_module_declares_eight_lessons_with_expected_ids() -> None:
    module_file = APP_DIR / "handwritten" / "lessons_productivity_regex.py"
    assert module_file.is_file(), "нет app/handwritten/lessons_productivity_regex.py"
    lessons = getattr(importlib.import_module(MODULE_NAME), "LESSONS", None)
    assert isinstance(lessons, list), "модуль должен объявлять LESSONS"
    assert all(isinstance(lesson, dict) for lesson in lessons), lessons
    assert sorted(lesson["id"] for lesson in lessons) == sorted(LESSON_IDS)


def test_c1_registry_exposes_all_eight_ids() -> None:
    registry = _registry()
    missing = sorted(set(LESSON_IDS) - set(registry))
    assert not missing, f"нет в реестре app.handwritten.HANDWRITTEN: {missing}"


def test_c1_course_keeps_120_lessons_with_expected_titles() -> None:
    lessons, lesson_by_id = _course()
    assert len(lessons) == 120
    for order, (lesson_id, title) in EXPECTED_LESSONS.items():
        assert lesson_id in lesson_by_id, lesson_id
        assert lesson_by_id[lesson_id]["order"] == order, lesson_id
        assert lesson_by_id[lesson_id]["title"] == title, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_meets_handwritten_contract(lesson_id: str) -> None:
    _assert_contract(lesson_id, _lesson(lesson_id))


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_course_uses_handwritten_theory_and_questions(lesson_id: str) -> None:
    _, lesson_by_id = _course()
    handwritten = _lesson(lesson_id)
    assert lesson_by_id[lesson_id]["theory"] == handwritten["theory"], lesson_id
    assert lesson_by_id[lesson_id]["questions"] == handwritten["questions"], lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_code_task_has_signature_starter_hint_and_explanation(lesson_id: str) -> None:
    code = _code_question(lesson_id)
    assert code["prompt"].strip(), lesson_id
    assert code["hint"].strip(), lesson_id
    assert code["explanation"].strip(), lesson_id
    assert re.search(r"^def \w+\(", code["starter"], re.MULTILINE), code["starter"]
    assert re.search(r"^\s+pass\s*$", code["starter"], re.MULTILINE), code["starter"]


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_every_example_has_output_comment(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert OUTPUT_MARK in card["example"], (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_output_comment_matches_real_stdout(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        actual = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
        assert _declared_output(card["example"]) == actual, (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_cards_go_what_how_then_typical_mistake(lesson_id: str) -> None:
    theory = _lesson(lesson_id)["theory"]
    assert theory[0]["title"].strip(), lesson_id
    assert theory[1]["title"].strip(), lesson_id
    assert "ошиб" in theory[2]["title"].casefold(), (lesson_id, theory[2]["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_predicts_output_of_runnable_code(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    result = run_code(_prompt_code(choice["prompt"]), [])
    assert result["error"] is None, (lesson_id, result["error"])
    output = result["stdout"].strip()
    assert output, lesson_id
    assert choice["answer"].strip() == output, (lesson_id, choice["answer"], output)
    for option in choice["options"]:
        if option != choice["answer"]:
            assert option.strip() != output, (lesson_id, option)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_options_do_not_stand_out(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    options = choice["options"]
    answer = choice["answer"]
    others = [option for option in options if option != answer]
    assert 3 <= len(options) <= 4, (lesson_id, options)
    assert all("\n" not in option for option in options), (lesson_id, options)

    lengths = [len(option) for option in options]
    longest, shortest = max(lengths), min(lengths)
    assert not (len(answer) == longest and lengths.count(longest) == 1), (lesson_id, answer)
    assert not (len(answer) == shortest and lengths.count(shortest) == 1), (lesson_id, answer)
    assert longest <= 2 * shortest, (lesson_id, lengths)

    has_ticks = "`" in answer
    assert any(("`" in option) == has_ticks for option in others), (lesson_id, answer)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_rejects_example(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert card.get("run", True) in (True, False), (lesson_id, card["title"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"])
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k81_top_words_returns_most_common_words() -> None:
    code = _code_question(COLLECTIONS_ID)
    _assert_starter_signature(code, "top_words")
    assert "Counter" in code["reference"], code["reference"]
    assert "most_common" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [_call("top_words('a b a c a b', 2)", ["a", "b"])],
    )
    assert result["correct"] is True, result


def test_k82_pairs_returns_two_item_combinations() -> None:
    code = _code_question(ITERTOOLS_ID)
    _assert_starter_signature(code, "pairs")
    assert "combinations" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call("pairs([1, 2, 3]) == [(1, 2), (1, 3), (2, 3)]", True),
            _call("pairs([1]) == []", True),
        ],
    )
    assert result["correct"] is True, result


def test_k83_product_multiplies_all_numbers_and_gives_one_for_empty() -> None:
    code = _code_question(FUNCTOOLS_ID)
    _assert_starter_signature(code, "product")
    assert "reduce" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call("product([2, 3, 4])", 24),
            _call("product([])", 1),
        ],
    )
    assert result["correct"] is True, result


def test_k84_smallest_returns_n_smallest_sorted() -> None:
    code = _code_question(HEAPQ_ID)
    _assert_starter_signature(code, "smallest")
    assert "nsmallest" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [_call("smallest([5, 1, 4, 2], 2)", [1, 2])],
    )
    assert result["correct"] is True, result


def test_k85_find_numbers_returns_all_integers_as_int() -> None:
    code = _code_question(PATTERNS_ID)
    _assert_starter_signature(code, "find_numbers")
    assert "findall" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call("find_numbers('в 2024 году 12 месяцев')", [2024, 12]),
            _call("find_numbers('нет')", []),
        ],
    )
    assert result["correct"] is True, result


def test_k86_parse_date_returns_named_groups_or_none() -> None:
    code = _code_question(GROUPS_ID)
    _assert_starter_signature(code, "parse_date")
    assert "(?P<" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call(
                "parse_date('дата: 2024-05-17')",
                {"year": 2024, "month": 5, "day": 17},
            ),
            _call("parse_date('без даты')", None),
        ],
    )
    assert result["correct"] is True, result


def test_k87_is_phone_checks_whole_text_with_fullmatch() -> None:
    code = _code_question(VALIDATION_ID)
    _assert_starter_signature(code, "is_phone")
    assert "fullmatch" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call("is_phone('+7 999 123-45-67')", True),
            _call("is_phone('89991234567')", False),
        ],
    )
    assert result["correct"] is True, result


def test_k88_normalize_spaces_collapses_whitespace_and_trims_edges() -> None:
    code = _code_question(SUBSTITUTION_ID)
    _assert_starter_signature(code, "normalize_spaces")
    assert "sub(" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [_call(r"normalize_spaces('  a \t b\n c ')", "a b c")],
    )
    assert result["correct"] is True, result
