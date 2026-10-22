import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_lists_mappings"
STACKS_ID = "lists-pro-stacks-queues"
MUTATION_ID = "lists-pro-mutation"
DICT_BASICS_ID = "mappings-dict-basics"
DICT_LOOPS_ID = "mappings-dict-loops"
DICT_MERGE_ID = "mappings-dict-merge"
SETS_ID = "mappings-sets"
# Порядковый номер урока в курсе → (id рукописного урока, название в курсе)
EXPECTED_LESSONS = {
    27: (STACKS_ID, "Стек и очередь"),
    28: (MUTATION_ID, "Изменение во время обхода"),
    29: (DICT_BASICS_ID, "Создание словарей"),
    30: (DICT_LOOPS_ID, "Обход словаря"),
    31: (DICT_MERGE_ID, "Объединение словарей"),
    32: (SETS_ID, "Операции множеств"),
}
LESSON_IDS = [lesson_id for lesson_id, _ in EXPECTED_LESSONS.values()]
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARK = "# Вывод:"
UNDERSTANDING_WORDS = (
    "вывод",
    "выведет",
    "верн",
    "напечата",
    "результат",
    "ошибк",
    "код",
    "значени",
)
NAME_RECALL_WORDS = ("название", "называ")


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


def test_c1_module_declares_six_lessons() -> None:
    assert (APP_DIR / "handwritten" / "lessons_lists_mappings.py").is_file(), (
        "нет app/handwritten/lessons_lists_mappings.py"
    )
    lessons = getattr(importlib.import_module(MODULE_NAME), "LESSONS", None)
    assert isinstance(lessons, list), "модуль должен объявлять LESSONS"
    assert all(isinstance(lesson, dict) for lesson in lessons), lessons
    assert {lesson["id"] for lesson in lessons} == set(LESSON_IDS)


def test_c1_registry_exposes_all_six_ids() -> None:
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
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


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


def test_k27_undo_returns_new_list_without_last_n() -> None:
    code = _code_question(STACKS_ID)
    assert "pop(" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [_call("undo(['a', 'b', 'c'], 2)", ["a"]), _call("undo(['a'], 5)", [])],
    )
    assert result["correct"] is True, result
    untouched = run_code(
        code["reference"] + "\nactions = ['a', 'b', 'c']\nundo(actions, 2)\nprint(actions)\n",
        [{"kind": "stdout", "expected": "['a', 'b', 'c']"}],
    )
    assert untouched["correct"] is True, untouched


def test_k28_without_negatives_returns_new_list_and_keeps_input() -> None:
    code = _code_question(MUTATION_ID)
    result = run_code(
        code["reference"],
        [_call("without_negatives([1, -2, 3])", [1, 3])],
    )
    assert result["correct"] is True, result
    untouched = run_code(
        code["reference"] + "\nitems = [1, -2, 3]\nwithout_negatives(items)\nprint(items)\n",
        [{"kind": "stdout", "expected": "[1, -2, 3]"}],
    )
    assert untouched["correct"] is True, untouched


def test_k29_word_lengths_builds_dict_of_lengths() -> None:
    code = _code_question(DICT_BASICS_ID)
    assert "{" in code["reference"] or "dict(" in code["reference"], code["reference"]
    result = run_code(
        code["reference"],
        [
            _call("word_lengths(['кот', 'слон'])", {"кот": 3, "слон": 4}),
            _call("word_lengths([])", {}),
        ],
    )
    assert result["correct"] is True, result


def test_k30_expensive_walks_dict_items_above_limit() -> None:
    code = _code_question(DICT_LOOPS_ID)
    assert "items()" in code["reference"], code["reference"]
    prices = "{'чай': 50, 'торт': 300, 'сыр': 200}"
    result = run_code(
        code["reference"],
        [
            _call(f"expensive({prices}, 100)", ["сыр", "торт"]),
            _call(f"expensive({prices}, 1000)", []),
        ],
    )
    assert result["correct"] is True, result


def test_k31_merge_settings_overrides_defaults_and_keeps_inputs() -> None:
    code = _code_question(DICT_MERGE_ID)
    assert any(marker in code["reference"] for marker in ("**", "update(", "|")), code["reference"]
    result = run_code(
        code["reference"],
        [
            _call(
                "merge_settings({'theme': 'light', 'lang': 'ru'}, {'theme': 'dark'})",
                {"theme": "dark", "lang": "ru"},
            )
        ],
    )
    assert result["correct"] is True, result
    untouched = run_code(
        code["reference"]
        + "\ndefaults = {'theme': 'light', 'lang': 'ru'}\nuser = {'theme': 'dark'}\n"
        + "merge_settings(defaults, user)\nprint(defaults, user)\n",
        [{"kind": "stdout", "expected": "{'theme': 'light', 'lang': 'ru'} {'theme': 'dark'}"}],
    )
    assert untouched["correct"] is True, untouched


def test_k32_compare_sets_returns_common_and_only_a() -> None:
    code = _code_question(SETS_ID)
    reference = code["reference"]
    assert any(marker in reference for marker in ("&", "intersection(")), reference
    assert any(marker in reference for marker in ("-", "difference(")), reference
    result = run_code(
        reference,
        [_call("compare_sets({1, 2, 3}, {2, 3, 4}) == ([2, 3], [1])", True)],
    )
    assert result["correct"] is True, result
