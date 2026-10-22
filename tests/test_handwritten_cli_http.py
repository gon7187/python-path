import ast
import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_cli_http"
# Порядковый номер урока в курсе → (id рукописного урока, название в курсе)
EXPECTED_LESSONS = {
    97: ("cli-environment-argv", "Аргументы командной строки"),
    98: ("cli-environment-environment", "Переменные окружения"),
    99: ("cli-environment-venv", "Виртуальные окружения"),
    100: ("cli-environment-pyproject", "pyproject.toml"),
    101: ("http-api-request-response", "Запрос и ответ"),
    102: ("http-api-json-api", "JSON в API"),
    103: ("http-api-status-codes", "Коды статуса"),
    104: ("http-api-pagination", "Пагинация и лимиты"),
}
LESSON_IDS = [lesson_id for lesson_id, _ in EXPECTED_LESSONS.values()]
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARK = "# Вывод:"
UNDERSTANDING_WORDS = ("вывед", "напечата", "верн", "ошиб", "код", "результат", "значени")
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


def _check(expression: str) -> dict[str, Any]:
    """Проверка раннера: выражение после выполнения кода ученика должно быть True."""
    return {"kind": "call", "call": expression, "expected": True}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _parses(source: str) -> bool:
    try:
        ast.parse(source)
    except SyntaxError:
        return False
    return True


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


def test_c1_module_declares_eight_lessons() -> None:
    assert (APP_DIR / "handwritten" / "lessons_cli_http.py").is_file(), (
        "нет app/handwritten/lessons_cli_http.py"
    )
    lessons = getattr(importlib.import_module(MODULE_NAME), "LESSONS", None)
    assert isinstance(lessons, list), "модуль должен объявлять LESSONS"
    assert all(isinstance(lesson, dict) for lesson in lessons), lessons
    assert {lesson.get("id") for lesson in lessons} == set(LESSON_IDS)


def test_c1_registry_exposes_all_eight_ids() -> None:
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
def test_c2_lesson_passes_shared_handwritten_contract(lesson_id: str) -> None:
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
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"]), lesson_id

    assert len(code["tests"]) >= 2, lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_cards_go_what_how_then_typical_mistake(lesson_id: str) -> None:
    titles = [card["title"].casefold() for card in _lesson(lesson_id)["theory"]]
    assert any(word in titles[0] for word in ("что", "зачем")), (lesson_id, titles[0])
    assert "как" in titles[1], (lesson_id, titles[1])
    assert "ошиб" in titles[2], (lesson_id, titles[2])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_every_example_has_output_comment_with_real_output(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert OUTPUT_MARK in card["example"], (lesson_id, card["title"])
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        actual = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
        assert actual, (lesson_id, card["title"], "пример ничего не печатает")
        assert _declared_output(card["example"]) == actual, (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_asks_to_predict_choose_or_find_not_recall_name(lesson_id: str) -> None:
    head = _questions(lesson_id)[0]["prompt"].partition("\n")[0].casefold()
    assert any(word in head for word in UNDERSTANDING_WORDS), (lesson_id, head)
    assert not any(word in head for word in NAME_RECALL_WORDS), (lesson_id, head)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_predicted_output_choice_matches_real_run(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    head, _, body = choice["prompt"].partition("\n")
    if "выведет" not in head.casefold():
        pytest.skip("вопрос не про вывод кода")
    result = run_code(body, [])
    assert result["error"] is None, (lesson_id, result["error"])
    actual = result["stdout"].strip()
    assert actual, (lesson_id, "код из вопроса ничего не печатает")
    assert choice["answer"].strip() == actual, (lesson_id, actual)
    others = [option for option in choice["options"] if option != choice["answer"]]
    assert all(option.strip() != actual for option in others), (lesson_id, actual)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_options_share_shape_and_answer_does_not_stand_out(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    options = choice["options"]
    answer = choice["answer"]
    assert 3 <= len(options) <= 4, (lesson_id, options)
    assert len(set(options)) == len(options), (lesson_id, options)
    assert len({"`" in option for option in options}) == 1, (lesson_id, options)
    assert len({"\n" in option for option in options}) == 1, (lesson_id, options)

    lengths = [len(option) for option in options]
    longest, shortest = max(lengths), min(lengths)
    assert not (len(answer) == longest and lengths.count(longest) == 1), (lesson_id, answer)
    assert not (len(answer) == shortest and lengths.count(shortest) == 1), (lesson_id, answer)
    assert longest <= 2 * shortest, (lesson_id, lengths)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_rejects_example(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert card.get("run", True) in (True, False), (lesson_id, card["title"])
        assert _parses(card["example"]), (lesson_id, card["title"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"])
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k97_parse_args_pairs_flags_into_dict() -> None:
    code = _code_question("cli-environment-argv")
    result = run_code(
        code["reference"],
        [
            _check("parse_args(['--name', 'Аня', '--age', '20']) == {'name': 'Аня', 'age': '20'}"),
            _check("parse_args([]) == {}"),
        ],
    )
    assert result["correct"] is True, result


def test_k98_get_port_reads_port_with_default_and_fallback() -> None:
    code = _code_question("cli-environment-environment")
    result = run_code(
        code["reference"],
        [
            _check("get_port({'PORT': '9000'}) == 9000"),
            _check("get_port({}) == 8000"),
            _check("get_port({'PORT': 'abc'}) == 8000"),
        ],
    )
    assert result["correct"] is True, result


def test_k99_requirement_name_takes_package_name_from_line() -> None:
    code = _code_question("cli-environment-venv")
    result = run_code(
        code["reference"],
        [
            _check("requirement_name('fastapi>=0.110') == 'fastapi'"),
            _check("requirement_name('# комментарий') is None"),
            _check("requirement_name('httpx') == 'httpx'"),
        ],
    )
    assert result["correct"] is True, result


def test_k100_project_name_reads_name_from_project_section() -> None:
    code = _code_question("cli-environment-pyproject")
    result = run_code(
        code["reference"],
        [
            _check(r"""project_name('[project]\nname = "demo"\nversion = "1.0"') == 'demo'"""),
            _check(r"""project_name('[project]\nversion = "1.0"') is None"""),
        ],
    )
    assert result["correct"] is True, result


def test_k101_parse_status_line_returns_code_and_reason() -> None:
    code = _code_question("http-api-request-response")
    result = run_code(
        code["reference"],
        [_check("parse_status_line('HTTP/1.1 404 Not Found') == (404, 'Not Found')")],
    )
    assert result["correct"] is True, result


def test_k102_extract_titles_reads_items_from_json_body() -> None:
    code = _code_question("http-api-json-api")
    result = run_code(
        code["reference"],
        [
            _check(
                r"""extract_titles('{"items": [{"title": "a"}, {"title": "b"}]}') == ['a', 'b']"""
            ),
            _check(r"""extract_titles('{"total": 0}') == []"""),
        ],
    )
    assert result["correct"] is True, result


def test_k103_status_group_maps_code_to_group_name() -> None:
    code = _code_question("http-api-status-codes")
    result = run_code(
        code["reference"],
        [
            _check("status_group(201) == 'успех'"),
            _check("status_group(404) == 'ошибка клиента'"),
            _check("status_group(99) == 'неизвестно'"),
        ],
    )
    assert result["correct"] is True, result


def test_k104_paginate_counts_pages_from_one() -> None:
    code = _code_question("http-api-pagination")
    result = run_code(
        code["reference"],
        [
            _check("paginate([1, 2, 3, 4, 5], 2, 2) == [3, 4]"),
            _check("paginate([1, 2], 3, 2) == []"),
        ],
    )
    assert result["correct"] is True, result
