import ast
import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_typing_stdlib"
MODULE_PATH = APP_DIR / "handwritten" / "lessons_typing_stdlib.py"
ANNOTATIONS_ID = "typing-models-annotations"
OPTIONAL_ID = "typing-models-optional-union"
COLLECTIONS_ID = "typing-models-generic-collections"
DATACLASS_ID = "typing-models-dataclasses-enums"
DATETIME_ID = "stdlib-core-datetime"
RANDOM_ID = "stdlib-core-random"
STATS_ID = "stdlib-core-math-statistics"
DECIMAL_ID = "stdlib-core-decimal"
# Порядковый номер урока в курсе → (id рукописного урока, название в курсе)
LESSON_SPECS = {
    ANNOTATIONS_ID: (73, "Аннотации типов"),
    OPTIONAL_ID: (74, "Необязательные значения"),
    COLLECTIONS_ID: (75, "Типы коллекций"),
    DATACLASS_ID: (76, "dataclass и Enum"),
    DATETIME_ID: (77, "Дата и время"),
    RANDOM_ID: (78, "Случайные значения"),
    STATS_ID: (79, "Математика и статистика"),
    DECIMAL_ID: (80, "Точность денег"),
}
LESSON_IDS = list(LESSON_SPECS)
ALLOWED_KEYS = frozenset({"id", "theory", "questions", "subtitle"})
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
NAME_RECALL_WORDS = ("название", "называ")


def _lessons_by_id() -> dict[str, dict[str, Any]]:
    assert MODULE_PATH.is_file(), f"нет файла {MODULE_PATH.name} в app/handwritten"
    lessons = importlib.import_module(MODULE_NAME).LESSONS
    assert isinstance(lessons, list), "LESSONS должен быть списком уроков"
    return {lesson.get("id"): lesson for lesson in lessons}


def _lesson(lesson_id: str) -> dict[str, Any]:
    lessons = _lessons_by_id()
    assert lesson_id in lessons, f"в {MODULE_NAME} нет урока {lesson_id}"
    return lessons[lesson_id]


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


def _stdout(expected: str) -> dict[str, Any]:
    return {"kind": "stdout", "expected": expected}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _declared_output(example: str) -> list[str]:
    """Строки вывода из комментария «# Вывод:» — то, что пример должен напечатать."""
    lines = example.splitlines()
    marks = [index for index, line in enumerate(lines) if line.strip().startswith(OUTPUT_MARKER)]
    if not marks:
        return []
    start = marks[0]
    declared = []
    head = lines[start].strip()[len(OUTPUT_MARKER) :].strip()
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


def _function(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    return next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


def _class(tree: ast.AST, name: str) -> ast.ClassDef | None:
    return next(
        (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == name),
        None,
    )


def _param_names(function: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in function.args.args]


def _annotation_text(node: ast.expr | None) -> str | None:
    return None if node is None else ast.unparse(node)


def _imported_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def _check_code_task(
    lesson_id: str, function_name: str, params: list[str], tests: list[dict[str, Any]]
) -> tuple[ast.Module, ast.FunctionDef]:
    code = _code_question(lesson_id)
    assert code["id"] == f"{lesson_id}-code", lesson_id

    reference_tree = ast.parse(code["reference"])
    reference_function = _function(reference_tree, function_name)
    assert reference_function is not None, (lesson_id, function_name)
    assert _param_names(reference_function) == params, lesson_id

    starter_function = _function(ast.parse(code["starter"]), function_name)
    assert starter_function is not None, (lesson_id, function_name)
    assert _param_names(starter_function) == params, lesson_id
    assert any(isinstance(node, ast.Pass) for node in ast.walk(starter_function)), (
        lesson_id,
        "starter без pass",
    )

    result = run_code(code["reference"], tests)
    assert result["error"] is None, (lesson_id, result["error"])
    assert result["correct"] is True, (lesson_id, result["message"], result["checks"])
    return reference_tree, reference_function


def _assert_contract(lesson_id: str, lesson: dict[str, Any]) -> None:
    assert lesson["id"] == lesson_id
    assert set(lesson) <= ALLOWED_KEYS, (lesson_id, sorted(set(lesson) - ALLOWED_KEYS))

    theory = lesson["theory"]
    assert isinstance(theory, list) and len(theory) == 3, lesson_id
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
    assert choice["explanation"].strip(), lesson_id

    assert isinstance(term["answers"], list) and term["answers"], lesson_id
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"])
    assert all(len(answer) <= 40 for answer in term["answers"]), lesson_id
    assert term["explanation"].strip(), lesson_id

    assert len(code["tests"]) >= 2, lesson_id
    assert code["hint"].strip(), lesson_id
    assert code["explanation"].strip(), lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


def test_c1_module_declares_eight_lessons() -> None:
    lessons = _lessons_by_id()
    assert sorted(lessons) == sorted(LESSON_IDS)


def test_c1_registry_exposes_all_eight_ids() -> None:
    registry = importlib.import_module("app.handwritten").HANDWRITTEN
    missing = sorted(set(LESSON_IDS) - set(registry))
    assert not missing, f"нет в реестре app.handwritten.HANDWRITTEN: {missing}"
    for lesson_id in LESSON_IDS:
        assert registry[lesson_id]["id"] == lesson_id


def test_c1_course_keeps_120_lessons_with_expected_titles() -> None:
    from app.content import LESSON_BY_ID, LESSONS

    assert len(LESSONS) == 120
    for lesson_id, (order, title) in LESSON_SPECS.items():
        assert lesson_id in LESSON_BY_ID, lesson_id
        assert LESSON_BY_ID[lesson_id]["order"] == order, lesson_id
        assert LESSON_BY_ID[lesson_id]["title"] == title, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_passes_handwritten_contract(lesson_id: str) -> None:
    _assert_contract(lesson_id, _lesson(lesson_id))


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_every_example_has_output_comment(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert OUTPUT_MARKER in card["example"], (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_output_comment_matches_real_stdout(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert _declared_output(card["example"]) == _lines(result["stdout"]), (
            lesson_id,
            card["title"],
        )


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_third_card_is_typical_mistake(lesson_id: str) -> None:
    assert "ошиб" in _lesson(lesson_id)["theory"][2]["title"].casefold(), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_asks_to_predict_or_find_not_recall_name(lesson_id: str) -> None:
    prompt = _questions(lesson_id)[0]["prompt"].casefold()
    assert any(word in prompt for word in UNDERSTANDING_WORDS), (lesson_id, prompt)
    assert not any(word in prompt for word in NAME_RECALL_WORDS), (lesson_id, prompt)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_predicted_output_matches_answer(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    prompt = choice["prompt"]
    if "выведет" not in prompt.casefold():
        return
    assert "\n\n" in prompt, (lesson_id, "в вопросе нет полного кода")
    code = prompt.split("\n\n", 1)[1]
    result = run_code(code, [])
    assert result["error"] is None, (lesson_id, result["error"])
    assert _lines(result["stdout"]) == _lines(choice["answer"]), (lesson_id, prompt)


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
    assert len({"\n" in option for option in options}) == 1, (lesson_id, options)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_rejects_example(lesson_id: str) -> None:
    for card in _lesson(lesson_id)["theory"]:
        assert card.get("run", True) in (True, False), (lesson_id, card["title"])
        result = run_code(card["example"], [])
        if card.get("run") is False:
            assert result["error"] is not None, (lesson_id, card["title"])
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


def test_k73_mean_is_annotated_and_averages_values() -> None:
    _, function = _check_code_task(
        ANNOTATIONS_ID,
        "mean",
        ["values"],
        [_call("mean([1, 2, 3]) == 2.0", True)],
    )
    assert _annotation_text(function.args.args[0].annotation) == "list[float]", ANNOTATIONS_ID
    assert _annotation_text(function.returns) == "float", ANNOTATIONS_ID


def test_k74_find_age_returns_none_for_missing_name_via_get() -> None:
    tree, function = _check_code_task(
        OPTIONAL_ID,
        "find_age",
        ["users", "name"],
        [
            _call("find_age({'Аня': 20}, 'Аня') == 20", True),
            _call("find_age({}, 'Ли') is None", True),
        ],
    )
    assert _annotation_text(function.args.args[0].annotation) == "dict[str, int]", OPTIONAL_ID
    assert _annotation_text(function.args.args[1].annotation) == "str", OPTIONAL_ID
    assert _annotation_text(function.returns) == "int | None", OPTIONAL_ID
    assert any(isinstance(node, ast.Attribute) and node.attr == "get" for node in ast.walk(tree)), (
        OPTIONAL_ID,
        "нет вызова .get",
    )


def test_k75_group_by_len_returns_dict_of_lists() -> None:
    _, function = _check_code_task(
        COLLECTIONS_ID,
        "group_by_len",
        ["words"],
        [_call("group_by_len(['да', 'нет', 'ок']) == {2: ['да', 'ок'], 3: ['нет']}", True)],
    )
    assert _annotation_text(function.args.args[0].annotation) == "list[str]", COLLECTIONS_ID
    assert _annotation_text(function.returns) == "dict[int, list[str]]", COLLECTIONS_ID


def test_k76_task_dataclass_and_progress_counts_done() -> None:
    tree, _ = _check_code_task(
        DATACLASS_ID,
        "progress",
        ["tasks"],
        [
            _call("progress([Task('a', True), Task('b')]) == 'выполнено 1 из 2'", True),
            _call("Task('c').done is False", True),
        ],
    )
    assert "dataclasses.dataclass" in _imported_names(tree), DATACLASS_ID
    task = _class(tree, "Task")
    assert task is not None, DATACLASS_ID
    assert any(ast.unparse(decorator) == "dataclass" for decorator in task.decorator_list), (
        DATACLASS_ID,
        "у Task нет декоратора @dataclass",
    )
    fields: dict[str, ast.AnnAssign] = {}
    for node in task.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            fields[node.target.id] = node
    assert "title" in fields and "done" in fields, DATACLASS_ID
    assert _annotation_text(fields["title"].annotation) == "str", DATACLASS_ID
    assert _annotation_text(fields["done"].annotation) == "bool", DATACLASS_ID
    assert _annotation_text(fields["done"].value) == "False", DATACLASS_ID


def test_k77_days_between_counts_days_with_date() -> None:
    tree, _ = _check_code_task(
        DATETIME_ID,
        "days_between",
        ["a", "b"],
        [
            _call("days_between('2024-01-01', '2024-03-01') == 60", True),
            _call("days_between('2024-05-05', '2024-05-05') == 0", True),
        ],
    )
    assert "datetime.date" in _imported_names(tree), DATETIME_ID


def test_k78_shuffled_uses_seeded_random_and_keeps_input() -> None:
    tree, _ = _check_code_task(
        RANDOM_ID,
        "shuffled",
        ["items", "seed"],
        [_call("sorted(shuffled([3, 1, 2], 7)) == [1, 2, 3]", True)],
    )
    assert "random" in _imported_names(tree), RANDOM_ID
    assert any(
        isinstance(node, ast.Attribute) and node.attr == "Random" for node in ast.walk(tree)
    ), (
        RANDOM_ID,
        "нет random.Random(seed)",
    )
    untouched = run_code(
        _code_question(RANDOM_ID)["reference"]
        + "\nitems = [3, 1, 2]\nshuffled(items, 7)\nprint(items)\n",
        [_stdout("[3, 1, 2]")],
    )
    assert untouched["correct"] is True, (RANDOM_ID, untouched)


def test_k79_stats_returns_mean_and_median() -> None:
    tree, _ = _check_code_task(
        STATS_ID,
        "stats",
        ["values"],
        [_call("stats([1, 2, 3, 10]) == (4, 2.5)", True)],
    )
    assert "statistics" in _imported_names(tree), STATS_ID


def test_k80_total_price_sums_decimal_strings_with_two_digits() -> None:
    tree, _ = _check_code_task(
        DECIMAL_ID,
        "total_price",
        ["prices"],
        [
            _call("total_price(['0.10', '0.20']) == '0.30'", True),
            _call("total_price([]) == '0.00'", True),
        ],
    )
    assert "decimal.Decimal" in _imported_names(tree), DECIMAL_ID
