import ast
import importlib
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_db_concurrency"
MODULE_PATH = APP_DIR / "handwritten" / "lessons_db_concurrency.py"
# id рукописного урока → (порядковый номер в курсе, название в курсе)
LESSON_SPECS = {
    "databases-relational": (105, "Реляционная модель"),
    "databases-crud": (106, "CRUD"),
    "databases-parameters": (107, "Параметры SQL"),
    "databases-transactions": (108, "Транзакции"),
    "concurrency-threads-processes": (109, "Потоки и процессы"),
    "concurrency-thread-pool": (110, "Пул потоков"),
    "concurrency-locks": (111, "Гонки и блокировки"),
    "concurrency-queues": (112, "Очереди задач"),
}
LESSON_IDS = list(LESSON_SPECS)
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARKER = "# Вывод:"
# Вопросы на понимание: предсказание вывода, выбор кода или поиск ошибки
CHOICE_FORMS = (
    "что выведет",
    "какой код",
    "какой вариант",
    "найди ошибку",
    "какая ошибка",
    "в чём ошибка",
    "в чем ошибка",
)
# Вопросы на узнавание названия темы, которые не нужны
RECALL_FORMS = ("как называется", "что такое", "название")
CODE_MARKS = ("(", "=", "[", "{", "\n")


def _registry() -> dict[str, dict[str, Any]]:
    return importlib.import_module("app.handwritten").HANDWRITTEN


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


def _choice_code(prompt: str) -> str | None:
    """Код вопроса идёт после пустой строки: «Что выведет код?\\n\\n<код>»."""
    _, separator, code = prompt.partition("\n\n")
    return code if separator and code.strip() else None


def _run_plain(code: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Запускает пример обычным Python: нужно для карточек, которые раннер не покажет."""
    return subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )


def _holds(expression: str) -> dict[str, Any]:
    """Проверка «выражение истинно».

    Раннер сравнивает результат с expected после JSON, а JSON превращает кортежи
    и числовые ключи словаря в другие значения. Поэтому сравнение делаем внутри
    выражения.
    """
    return {"kind": "call", "call": expression, "expected": True}


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


def _nodes(tree: ast.AST | None, node_type: type) -> list[Any]:
    if tree is None:
        return []
    return [node for node in ast.walk(tree) if isinstance(node, node_type)]


def _check_code_task(
    lesson_id: str, function_name: str, params: list[str], tests: list[dict[str, Any]]
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
    assert run_code(code["starter"], tests)["correct"] is False, (lesson_id, "starter проходит")
    return reference_tree


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c1_module_declares_all_eight_lessons(lesson_id: str) -> None:
    assert lesson_id in _lessons_by_id(), (lesson_id, "нет в LESSONS файла")


def test_c1_module_declares_exactly_the_eight_lessons() -> None:
    assert sorted(_lessons_by_id()) == sorted(LESSON_IDS)


def test_c1_registry_exposes_all_eight_ids() -> None:
    registry = _registry()
    missing = sorted(set(LESSON_IDS) - set(registry))
    assert not missing, f"нет в реестре app.handwritten.HANDWRITTEN: {missing}"


def test_c1_course_keeps_120_lessons_with_expected_numbers_and_titles() -> None:
    from app.content import LESSON_BY_ID, LESSONS

    registry = _registry()
    assert len(LESSONS) == 120
    for lesson_id, (order, title) in LESSON_SPECS.items():
        assert lesson_id in registry, lesson_id
        assert lesson_id in LESSON_BY_ID, lesson_id
        lesson = LESSON_BY_ID[lesson_id]
        assert lesson["order"] == order, lesson_id
        assert lesson["title"] == title, lesson_id


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
def test_c3_examples_print_declared_output(lesson_id: str, tmp_path: Path) -> None:
    for card in _lesson(lesson_id)["theory"]:
        expected = _declared_output(card["example"])
        assert expected, (lesson_id, card["title"], "нет «# Вывод:» с выводом")
        if card.get("run") is False:
            completed = _run_plain(card["example"], tmp_path)
            assert completed.returncode == 0, (lesson_id, card["title"], completed.stderr)
            actual = completed.stdout
        else:
            actual = run_code(card["example"], [])["stdout"]
        actual_lines = [line.rstrip() for line in actual.splitlines()]
        assert actual_lines == [line.rstrip() for line in expected], (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_third_card_is_typical_error(lesson_id: str) -> None:
    typical_error = _lesson(lesson_id)["theory"][2]
    assert "ошиб" in f"{typical_error['title']} {typical_error['text']}".casefold(), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_checks_understanding_not_recall(lesson_id: str, tmp_path: Path) -> None:
    choice = _lesson(lesson_id)["questions"][0]
    prompt = choice["prompt"].casefold()
    assert any(form in prompt for form in CHOICE_FORMS), (lesson_id, choice["prompt"])
    assert not any(form in prompt for form in RECALL_FORMS), (lesson_id, choice["prompt"])

    options = choice["options"]
    if "что выведет" in prompt:
        code = _choice_code(choice["prompt"])
        assert code, (lesson_id, "в вопросе нет кода после пустой строки")
        completed = _run_plain(code, tmp_path)
        assert completed.returncode == 0, (lesson_id, completed.stderr)
        assert completed.stdout.strip() == choice["answer"].strip(), (lesson_id, completed.stdout)
    else:
        has_code_in_prompt = _choice_code(choice["prompt"]) is not None
        has_code_in_options = all(any(mark in option for mark in CODE_MARKS) for option in options)
        assert has_code_in_prompt or has_code_in_options, (lesson_id, "нет кода для проверки")

    assert 3 <= len(options) <= 4, (lesson_id, len(options))
    assert len(set(options)) == len(options), lesson_id

    has_ticks = ["`" in option for option in options]
    assert all(has_ticks) or not any(has_ticks), (lesson_id, "бэктики только у части вариантов")
    has_lines = ["\n" in option for option in options]
    assert all(has_lines) or not any(has_lines), (lesson_id, "многострочный только часть")

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


def test_k105_user_totals_joins_orders_by_user_id() -> None:
    tests = [
        _holds(
            "user_totals([{'id': 1, 'name': 'Аня'}], "
            "[{'user_id': 1, 'sum': 100}, {'user_id': 1, 'sum': 50}]) == [('Аня', 150)]"
        ),
        _holds(
            "user_totals([{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Борис'}], "
            "[{'user_id': 1, 'sum': 100}, {'user_id': 1, 'sum': 50}]) "
            "== [('Аня', 150), ('Борис', 0)]"
        ),
        _holds("user_totals([], []) == []"),
    ]
    _check_code_task("databases-relational", "user_totals", ["users", "orders"], tests)


def test_k106_crud_apply_returns_new_dict() -> None:
    tests = [
        _holds("apply({}, ('create', 1, 'a')) == {1: 'a'}"),
        _holds("apply({1: 'a'}, ('update', 1, 'b')) == {1: 'b'}"),
        _holds("apply({1: 'a'}, ('delete', 1)) == {}"),
        _holds("(lambda db: (apply(db, ('create', 2, 'b')), db)[1])({1: 'a'}) == {1: 'a'}"),
        _holds("(lambda db: (apply(db, ('delete', 1)), db)[1])({1: 'a'}) == {1: 'a'}"),
    ]
    _check_code_task("databases-crud", "apply", ["db", "op"], tests)


def test_k107_parameters_build_query_keeps_values_out_of_sql() -> None:
    tests = [
        _holds(
            "build_query('users', {'city': 'Москва', 'age': 20}) "
            "== ('SELECT * FROM users WHERE age = ? AND city = ?', (20, 'Москва'))"
        ),
        _holds("build_query('users', {}) == ('SELECT * FROM users', ())"),
        _holds("'Москва' not in build_query('users', {'city': 'Москва'})[0]"),
    ]
    _check_code_task("databases-parameters", "build_query", ["table", "filters"], tests)


def test_k108_transactions_transfer_all_or_nothing() -> None:
    tests = [
        {
            "kind": "call",
            "call": "transfer({'a': 100, 'b': 0}, 'a', 'b', 30)",
            "expected": {"a": 70, "b": 30},
        },
        {
            "kind": "call",
            "call": "transfer({'a': 10, 'b': 0}, 'a', 'b', 30)",
            "expected": {"a": 10, "b": 0},
        },
        _holds(
            "(lambda b: (transfer(b, 'a', 'b', 30), b)[1])({'a': 100, 'b': 0}) == {'a': 100, 'b': 0}"
        ),
        _holds(
            "(lambda b: (transfer(b, 'a', 'b', 30), b)[1])({'a': 10, 'b': 0}) == {'a': 10, 'b': 0}"
        ),
    ]
    _check_code_task(
        "databases-transactions", "transfer", ["balances", "src", "dst", "amount"], tests
    )


def test_k109_threads_split_chunks_keeps_order() -> None:
    tests = [
        {
            "kind": "call",
            "call": "split_chunks([1, 2, 3, 4, 5], 2)",
            "expected": [[1, 2, 3], [4, 5]],
        },
        {"kind": "call", "call": "split_chunks([], 3)", "expected": [[], [], []]},
    ]
    _check_code_task("concurrency-threads-processes", "split_chunks", ["items", "n"], tests)


def test_k110_thread_pool_map_keeps_input_order() -> None:
    tests = [
        {"kind": "call", "call": "pool_map(lambda x: x * 2, [1, 2, 3], 2)", "expected": [2, 4, 6]},
        {"kind": "call", "call": "pool_map(lambda x: x * 2, [1, 2, 3], 1)", "expected": [2, 4, 6]},
        {"kind": "call", "call": "pool_map(lambda x: x * 2, [1, 2, 3], 3)", "expected": [2, 4, 6]},
        {"kind": "call", "call": "pool_map(lambda x: x * 2, [], 2)", "expected": []},
    ]
    _check_code_task("concurrency-thread-pool", "pool_map", ["func", "items", "workers"], tests)


def test_k111_locks_withdraw_checks_and_debits_in_one_step() -> None:
    lesson = _lesson("concurrency-locks")
    code = lesson["questions"][2]
    tests = [
        {
            "kind": "call",
            "call": "(lambda a: [a.withdraw(70) is True, a.withdraw(70) is False, "
            "a.balance == 30])(Account(100))",
            "expected": [True, True, True],
        },
        {
            "kind": "call",
            "call": "(lambda a: [a.withdraw(101) is False, a.balance])(Account(100))",
            "expected": [True, 100],
        },
        {
            "kind": "call",
            "call": "(lambda a: [a.withdraw(100) is True, a.balance])(Account(100))",
            "expected": [True, 0],
        },
    ]

    reference_account = _class(ast.parse(code["reference"]), "Account")
    assert reference_account is not None, "reference должен объявлять класс Account"
    init = _function(reference_account, "__init__")
    assert init is not None and _param_names(init) == ["self", "balance"]
    withdraw = _function(reference_account, "withdraw")
    assert withdraw is not None and _param_names(withdraw) == ["self", "amount"]

    starter_account = _class(ast.parse(code["starter"]), "Account")
    assert starter_account is not None, "starter должен объявлять класс Account"
    assert _nodes(starter_account, ast.Pass), "starter без pass"

    result = run_code(code["reference"], tests)
    assert result["error"] is None, result["error"]
    assert result["correct"] is True, (result["message"], result["checks"])
    assert run_code(code["starter"], tests)["correct"] is False, "starter проходит"


def test_k112_queues_process_queue_requeues_marked_tasks_once() -> None:
    tests = [
        {
            "kind": "call",
            "call": "process_queue(['a', 'b!', 'c'])",
            "expected": ["a", "c", "b"],
        },
        {"kind": "call", "call": "process_queue(['b!'])", "expected": ["b"]},
        {"kind": "call", "call": "process_queue([])", "expected": []},
    ]
    tree = _check_code_task("concurrency-queues", "process_queue", ["tasks"], tests)
    assert any(isinstance(node, ast.Name) and node.id == "deque" for node in ast.walk(tree)), (
        "reference должен использовать collections.deque"
    )
