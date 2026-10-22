import importlib
import re
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_files_errors"
PATHLIB_ID = "files-data-pathlib"
TEXT_FILES_ID = "files-data-text-files"
JSON_ID = "files-data-json"
CSV_ID = "files-data-csv"
EXCEPTION_TYPES_ID = "errors-debug-exception-types"
RAISE_ID = "errors-debug-raise"
FINALLY_ID = "errors-debug-finally"
DEBUGGING_ID = "errors-debug-debugging"
# Порядковый номер урока в курсе → (id рукописного урока, название в курсе)
EXPECTED_LESSONS = {
    57: (PATHLIB_ID, "Пути через pathlib"),
    58: (TEXT_FILES_ID, "Текстовые файлы"),
    59: (JSON_ID, "JSON"),
    60: (CSV_ID, "CSV-таблицы"),
    61: (EXCEPTION_TYPES_ID, "Типы исключений"),
    62: (RAISE_ID, "raise и валидация"),
    63: (FINALLY_ID, "try, except, else, finally"),
    64: (DEBUGGING_ID, "Отладка"),
}
LESSON_IDS = [lesson_id for lesson_id, _ in EXPECTED_LESSONS.values()]
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARK = "# Вывод:"
PREDICTION_WORDS = ("выведет", "вывод", "верн", "ошиб", "напечата", "результат")
NAME_RECALL_WORDS = ("название", "называ", "термин")


def _registry() -> dict[str, dict[str, Any]]:
    return importlib.import_module("app.handwritten").HANDWRITTEN


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


def _output_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


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
    match = re.search(r"`([^`]+)`", prompt)
    assert match, f"в вопросе нет кода в бэктиках: {prompt}"
    return match.group(1)


def test_c1_module_declares_eight_lessons() -> None:
    assert (APP_DIR / "handwritten" / "lessons_files_errors.py").is_file(), (
        "нет app/handwritten/lessons_files_errors.py"
    )
    lessons = getattr(importlib.import_module(MODULE_NAME), "LESSONS", None)
    assert isinstance(lessons, list), "модуль должен объявлять LESSONS"
    assert all(isinstance(lesson, dict) for lesson in lessons), lessons
    assert sorted(lesson.get("id") for lesson in lessons) == sorted(LESSON_IDS)


def test_c1_registry_exposes_all_eight_ids() -> None:
    registry = _registry()
    missing = sorted(set(LESSON_IDS) - set(registry))
    assert not missing, f"нет в реестре app.handwritten.HANDWRITTEN: {missing}"


def test_c1_course_keeps_120_lessons_with_expected_titles() -> None:
    from app.content import LESSON_BY_ID, LESSONS

    assert len(LESSONS) == 120
    for order, (lesson_id, title) in EXPECTED_LESSONS.items():
        assert lesson_id in LESSON_BY_ID, lesson_id
        assert LESSON_BY_ID[lesson_id]["order"] == order, lesson_id
        assert LESSON_BY_ID[lesson_id]["title"] == title, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_meets_handwritten_contract(lesson_id: str) -> None:
    lesson = _lesson(lesson_id)
    assert lesson["id"] == lesson_id

    theory = lesson["theory"]
    assert len(theory) == 3, lesson_id
    for card in theory:
        for key in ("title", "text", "example"):
            assert isinstance(card.get(key), str) and card[key].strip(), (lesson_id, key)
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])

    choice, term, code = _questions(lesson_id)
    assert [choice["id"], term["id"], code["id"]] == [
        f"{lesson_id}-choice",
        f"{lesson_id}-term",
        f"{lesson_id}-code",
    ]
    assert [choice["kind"], term["kind"], code["kind"]] == ["choice", "input", "code"]

    assert len(set(choice["options"])) >= 3, lesson_id
    assert choice["answer"] in choice["options"], lesson_id

    assert isinstance(term["answers"], list) and term["answers"], lesson_id
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"])

    assert len(code["tests"]) >= 2, lesson_id
    assert isinstance(code["starter"], str), lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_three_cards_end_with_typical_mistake(lesson_id: str) -> None:
    theory = _lesson(lesson_id)["theory"]
    assert len(theory) == 3, lesson_id
    assert "ошиб" in theory[2]["title"].casefold(), (lesson_id, theory[2]["title"])


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
        actual = _output_lines(result["stdout"])
        assert _declared_output(card["example"]) == actual, (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_asks_to_predict_or_find_not_recall_name(lesson_id: str) -> None:
    prompt = _questions(lesson_id)[0]["prompt"].casefold()
    assert any(word in prompt for word in PREDICTION_WORDS), (lesson_id, prompt)
    assert not any(word in prompt for word in NAME_RECALL_WORDS), (lesson_id, prompt)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_prediction_matches_real_run_of_question_code(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    if "выведет" not in choice["prompt"].casefold():
        return
    result = run_code(_prompt_code(choice["prompt"]), [])
    if result["error"] is None:
        assert _output_lines(choice["answer"]) == _output_lines(result["stdout"]), (
            lesson_id,
            result["stdout"],
        )
    else:
        error_name = result["error"].split(":", 1)[0]
        assert error_name in choice["answer"], (lesson_id, result["error"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_answer_does_not_stand_out(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    options = choice["options"]
    answer = choice["answer"]
    others = [option for option in options if option != answer]
    assert 3 <= len(options) <= 4, (lesson_id, options)

    lengths = [len(option) for option in options]
    longest, shortest = max(lengths), min(lengths)
    assert not (len(answer) == longest and lengths.count(longest) == 1), (lesson_id, answer)
    assert not (len(answer) == shortest and lengths.count(shortest) == 1), (lesson_id, answer)
    assert longest <= 2 * shortest, (lesson_id, lengths)

    has_ticks = "`" in answer
    assert all(("`" in option) == has_ticks for option in others), (lesson_id, answer)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_rejects_example(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert card.get("run", True) in (True, False), (lesson_id, card["title"])
        compile(card["example"], "<example>", "exec")
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"])
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k57_split_name_returns_stem_and_suffix() -> None:
    code = _code_question(PATHLIB_ID)
    result = run_code(
        code["reference"],
        [
            _call("list(split_name('report.final.pdf'))", ["report.final", ".pdf"]),
            _call("list(split_name('README'))", ["README", ""]),
        ],
    )
    assert result["correct"] is True, result


def test_k58_count_lines_skips_empty_lines() -> None:
    code = _code_question(TEXT_FILES_ID)
    result = run_code(
        code["reference"],
        [
            _call("count_lines('a\\n\\nb\\n')", 2),
            _call("count_lines('')", 0),
        ],
    )
    assert result["correct"] is True, result


def test_k59_user_name_reads_name_or_guest() -> None:
    code = _code_question(JSON_ID)
    assert re.search(r"^\s*(import json|from json import)", code["reference"], re.M), code[
        "reference"
    ]
    result = run_code(
        code["reference"],
        [
            _call('user_name(\'{"name": "Аня"}\')', "Аня"),
            _call("user_name('{}')", "Гость"),
        ],
    )
    assert result["correct"] is True, result


def test_k60_parse_csv_builds_dicts_from_header() -> None:
    code = _code_question(CSV_ID)
    result = run_code(
        code["reference"],
        [
            _call(
                "parse_csv('name,age\\nАня,20\\nЛи,30')",
                [{"name": "Аня", "age": "20"}, {"name": "Ли", "age": "30"}],
            ),
        ],
    )
    assert result["correct"] is True, result


def test_k61_safe_int_returns_none_on_value_error() -> None:
    code = _code_question(EXCEPTION_TYPES_ID)
    result = run_code(
        code["reference"],
        [
            _call("safe_int('42')", 42),
            _call("safe_int('сорок')", None),
        ],
    )
    assert result["correct"] is True, result


def test_k62_check_age_raises_and_describe_returns_message() -> None:
    code = _code_question(RAISE_ID)
    assert "raise ValueError(" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call("check_age(30)", 30),
            _call("describe(30)", "ok"),
            _call("describe(-1)", "возраст не может быть отрицательным"),
        ],
    )
    assert result["correct"] is True, result


def test_k63_divide_steps_lists_taken_branches() -> None:
    code = _code_question(FINALLY_ID)
    result = run_code(
        code["reference"],
        [
            _call("divide_steps(4, 2)", ["try", "else", "finally"]),
            _call("divide_steps(1, 0)", ["try", "except", "finally"]),
        ],
    )
    assert result["correct"] is True, result


def test_k64_debugging_starter_is_broken_and_reference_fixes_average() -> None:
    code = _code_question(DEBUGGING_ID)
    assert re.search(r"def average\(items\)", code["starter"]), code["starter"]
    calls = [
        _call("average([1, 2, 3])", 2),
        _call("average([])", 0),
    ]
    starter = run_code(code["starter"], calls)
    assert starter["correct"] is False, starter
    reference = run_code(code["reference"], calls)
    assert reference["correct"] is True, reference
