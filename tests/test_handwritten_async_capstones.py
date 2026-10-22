import importlib
import importlib.util
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

MODULE_NAME = "app.handwritten.lessons_async_capstones"
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARK = "# Вывод:"
PREDICT_PREFIX = "Что выведет"
UNDERSTANDING_WORDS = ("вывед", "верн", "ошибк", "код", "результат", "значени")
NAME_RECALL_WORDS = ("название", "называ")
# Порядковый номер урока в курсе → (id рукописного урока, название в курсе)
EXPECTED_LESSONS = {
    113: ("async-coroutines", "Coroutine"),
    114: ("async-tasks", "Задачи"),
    115: ("async-gather-timeouts", "gather и таймауты"),
    116: ("async-async-design", "Асинхронный дизайн"),
    117: ("capstones-task-manager", "Проект: менеджер задач"),
    118: ("capstones-notes-app", "Проект: заметки"),
    119: ("capstones-api-client", "Проект: API-клиент"),
    120: ("capstones-release", "Финальная сборка"),
}
LESSON_IDS = [lesson_id for lesson_id, _ in EXPECTED_LESSONS.values()]


def _registry() -> dict[str, dict[str, Any]]:
    assert importlib.util.find_spec("app.handwritten") is not None, "нет пакета app.handwritten"
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


def _check_reference(lesson_id: str, calls: list[dict[str, Any]]) -> None:
    code = _code_question(lesson_id)
    result = run_code(code["reference"], calls)
    assert result["correct"] is True, (lesson_id, result)


def _assert_contract(lesson_id: str) -> None:
    lesson = _lesson(lesson_id)
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
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


def test_c1_module_declares_all_eight_lessons() -> None:
    assert importlib.util.find_spec(MODULE_NAME) is not None, f"нет модуля {MODULE_NAME}"
    lessons = getattr(importlib.import_module(MODULE_NAME), "LESSONS", None)
    assert isinstance(lessons, list), "модуль должен объявлять LESSONS"
    assert all(isinstance(lesson, dict) for lesson in lessons), lessons
    assert {lesson["id"] for lesson in lessons} == set(LESSON_IDS)


def test_c1_registry_contains_all_eight_ids() -> None:
    registry = _registry()
    missing = sorted(set(LESSON_IDS) - set(registry))
    assert not missing, f"нет в реестре app.handwritten.HANDWRITTEN: {missing}"


def test_c1_course_keeps_120_lessons_with_expected_orders_and_titles() -> None:
    from app.content import LESSON_BY_ID, LESSONS

    assert len(LESSONS) == 120
    for order, (lesson_id, title) in EXPECTED_LESSONS.items():
        assert lesson_id in LESSON_BY_ID, lesson_id
        assert LESSON_BY_ID[lesson_id]["order"] == order, lesson_id
        assert LESSON_BY_ID[lesson_id]["title"] == title, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_meets_handwritten_contract(lesson_id: str) -> None:
    _assert_contract(lesson_id)


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
def test_c3_third_card_is_typical_mistake(lesson_id: str) -> None:
    assert "ошиб" in _lesson(lesson_id)["theory"][2]["title"].casefold(), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_asks_to_predict_or_find_not_recall_name(lesson_id: str) -> None:
    prompt = _questions(lesson_id)[0]["prompt"].casefold()
    assert any(word in prompt for word in UNDERSTANDING_WORDS), (lesson_id, prompt)
    assert not any(word in prompt for word in NAME_RECALL_WORDS), (lesson_id, prompt)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_predicted_output_matches_choice_answer(lesson_id: str) -> None:
    """Если вопрос просит предсказать вывод, код из вопроса должен напечатать верный вариант."""
    choice = _questions(lesson_id)[0]
    if not choice["prompt"].startswith(PREDICT_PREFIX):
        return
    _, _, code = choice["prompt"].partition("\n")
    result = run_code(code, [{"kind": "stdout", "expected": choice["answer"]}])
    assert result["correct"] is True, (lesson_id, result)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_options_are_plausible_and_same_shape(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    options = choice["options"]
    answer = choice["answer"]
    others = [option for option in options if option != answer]
    assert 3 <= len(options) <= 4, (lesson_id, options)
    assert len(set(options)) == len(options), (lesson_id, options)

    lengths = [len(option) for option in options]
    longest, shortest = max(lengths), min(lengths)
    assert not (len(answer) == longest and lengths.count(longest) == 1), (lesson_id, answer)
    assert not (len(answer) == shortest and lengths.count(shortest) == 1), (lesson_id, answer)
    assert longest <= 2 * shortest, (lesson_id, lengths)

    has_ticks = "`" in answer
    assert any(("`" in option) == has_ticks for option in others), (lesson_id, answer)
    has_newline = "\n" in answer
    assert any(("\n" in option) == has_newline for option in others), (lesson_id, answer)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_rejects_example(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert card.get("run", True) in (True, False), (lesson_id, card["title"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"])
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k113_steps_yields_numbered_lines_from_one_to_n() -> None:
    _check_reference(
        "async-coroutines",
        [
            _call("list(steps('загрузка', 2))", ["загрузка: шаг 1", "загрузка: шаг 2"]),
            _call("hasattr(steps('загрузка', 1), '__next__')", True),
        ],
    )


def test_k114_round_robin_takes_one_value_from_each_generator_in_turn() -> None:
    _check_reference(
        "async-tasks",
        [_call("round_robin([iter('ab'), iter('xyz')])", ["a", "x", "b", "y", "z"])],
    )


def test_k115_gather_results_marks_ok_or_timeout_in_input_order() -> None:
    _check_reference(
        "async-gather-timeouts",
        [_call("gather_results([1, 5, 2], 3)", ["ok", "timeout", "ok"])],
    )


def test_k116_total_time_is_max_when_concurrent_and_sum_otherwise() -> None:
    _check_reference(
        "async-async-design",
        [
            _call("total_time([1, 2, 3], True)", 3),
            _call("total_time([1, 2, 3], False)", 6),
            _call("total_time([], True)", 0),
        ],
    )


def test_k117_task_manager_pending_lists_unfinished_in_add_order() -> None:
    _check_reference(
        "capstones-task-manager",
        [
            _call(
                "(lambda tm: (tm.add('a'), tm.add('b'), tm.done('a'), tm.pending())[3])"
                "(TaskManager())",
                ["b"],
            )
        ],
    )


def test_k118_search_notes_matches_title_or_text_case_insensitively() -> None:
    _check_reference(
        "capstones-notes-app",
        [
            _call(
                "search_notes([{'title': 'Покупки', 'text': 'хлеб'}, "
                "{'title': 'Идеи', 'text': 'бот'}], 'ХЛЕБ')",
                ["Покупки"],
            )
        ],
    )


def test_k119_fetch_all_collects_pages_until_first_empty() -> None:
    _check_reference(
        "capstones-api-client",
        [_call("fetch_all(lambda n: [[1, 2], [3], []][n - 1])", [1, 2, 3])],
    )


def test_k120_release_notes_skips_empty_sections() -> None:
    _check_reference(
        "capstones-release",
        [
            _call(
                "release_notes(['feat: поиск', 'fix: вход', 'feat: экспорт'])",
                "Новое:\n- поиск\n- экспорт\nИсправлено:\n- вход",
            ),
            _call("release_notes(['fix: вход'])", "Исправлено:\n- вход"),
        ],
    )
