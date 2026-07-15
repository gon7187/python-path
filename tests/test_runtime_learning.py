from datetime import UTC, datetime

import pytest

import app.db as database
import app.main as main
from app.content import EXAMS, LESSONS, MODULES, QUESTION_BY_ID
from app.evaluator import evaluate, run_code


def test_mandatory_input_challenge_has_a_real_test_scenario() -> None:
    question = QUESTION_BY_ID["challenge-strings-input"]

    assert question["test_inputs"] == ["  Казань  "]
    assert question["input_example"] == question["test_inputs"]
    result = evaluate(
        question,
        "city = input('Город: ').strip()\nprint(f'Маршрут: {city}')\n",
    )
    assert result["correct"] is True


def test_stdout_whitespace_comparison_is_opt_in() -> None:
    source = "print('Слов: ', 4)\n"
    flexible = run_code(
        source,
        [{"kind": "stdout", "expected": "Слов: 4", "comparison": "whitespace"}],
    )
    strict = run_code(source, [{"kind": "stdout", "expected": "Слов: 4"}])

    assert flexible["correct"] is True
    assert strict["correct"] is False
    assert "ожидалось" in strict["message"]
    assert "получено" in strict["message"]


def test_strict_stdout_keeps_meaningful_leading_spaces() -> None:
    result = run_code(
        "print(f'{42:>5} XP')\n",
        [{"kind": "stdout", "expected": "   42 XP"}],
    )

    assert result["correct"] is True


def test_stdout_contains_comparison_ignores_prompt_wording() -> None:
    source = "name = input('Как тебя зовут? ')\nprint(f'Привет, {name}!')\n"
    result = run_code(
        source,
        [{"kind": "stdout", "expected": "Привет, Лена!", "comparison": "contains"}],
        ["Лена"],
    )

    assert result["correct"] is True


def test_failed_code_check_is_not_hidden_by_success_explanation() -> None:
    question = {
        "kind": "code",
        "tests": [{"kind": "stdout", "expected": "42"}],
        "explanation": "Этот текст относится только к успеху.",
    }

    result = evaluate(question, "print(41)")

    assert result["correct"] is False
    assert "explanation" not in result
    assert "'42'" in result["message"]
    assert "'41'" in result["message"]


def test_public_feedback_hides_values_leaked_by_an_exception_in_a_hidden_test() -> None:
    internal = run_code(
        "def double(*args, **kwargs):\n    raise ValueError((args, kwargs))\n",
        [{"kind": "call", "call": "double(314159)", "expected": 628318}],
    )

    public = main.public_evaluation(internal)

    assert internal["error_phase"] == "hidden_test"
    assert "314159" in internal["message"]
    assert "314159" not in public["message"]
    assert "628318" not in public["message"]
    assert "error_phase" not in public


def test_successful_code_check_shows_the_learning_explanation() -> None:
    question = {
        "kind": "code",
        "tests": [{"kind": "stdout", "expected": "42"}],
        "explanation": "print() отправляет значение в консоль.",
    }

    result = evaluate(question, "print(42)")

    assert result["correct"] is True
    assert "Все тесты пройдены" in result["message"]
    assert "print() отправляет значение в консоль" in result["message"]


def test_runner_supports_isolated_sqlite() -> None:
    result = run_code(
        "import sqlite3\n"
        "connection = sqlite3.connect('study.db')\n"
        "connection.execute('CREATE TABLE scores (value INTEGER)')\n"
        "connection.execute('INSERT INTO scores VALUES (?)', (7,))\n"
        "print(connection.execute('SELECT value FROM scores').fetchone()[0])\n",
        [{"kind": "stdout", "expected": "7"}],
    )

    assert result["correct"] is True


def test_runner_supports_safe_threads_queues_and_thread_pool() -> None:
    result = run_code(
        "import queue\n"
        "import threading\n"
        "from concurrent.futures import ThreadPoolExecutor\n"
        "values = queue.Queue()\n"
        "thread = threading.Thread(target=lambda: values.put(5))\n"
        "thread.start()\n"
        "thread.join()\n"
        "with ThreadPoolExecutor(max_workers=2) as pool:\n"
        "    squares = list(pool.map(lambda number: number ** 2, [2, 3]))\n"
        "print(values.get(), squares)\n",
        [{"kind": "stdout", "expected": "5 [4, 9]"}],
    )

    assert result["correct"] is True


def test_runner_supports_safe_argparse_and_simulated_sys_argv() -> None:
    result = run_code(
        "import argparse\n"
        "import sys\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--level', type=int)\n"
        "args = parser.parse_args(['--level', '3'])\n"
        "print(args.level, sys.argv[0])\n",
        [{"kind": "stdout", "expected": "3 program.py"}],
    )

    assert result["correct"] is True


def test_runner_caps_threads_and_blocks_argparse_host_files() -> None:
    capped = run_code(
        "import threading\n"
        "gate = threading.Event()\n"
        "threads = [threading.Thread(target=gate.wait) for _ in range(5)]\n"
        "for thread in threads[:4]:\n"
        "    thread.start()\n"
        "try:\n"
        "    threads[4].start()\n"
        "except RuntimeError:\n"
        "    print('limit')\n"
        "gate.set()\n"
        "for thread in threads[:4]:\n"
        "    thread.join()\n",
        [{"kind": "stdout", "expected": "limit"}],
    )
    host_file = run_code(
        "import argparse\nargparse.ArgumentParser(fromfile_prefix_chars='@')\n",
        [],
    )

    assert capped["correct"] is True
    assert host_file["correct"] is False
    assert "из файла недоступно" in host_file["message"]


def test_runner_keeps_process_pool_unavailable() -> None:
    result = run_code("from concurrent.futures import ProcessPoolExecutor\n", [])

    assert result["correct"] is False
    assert "дочерних процессов" in result["message"]


def test_source_check_requires_each_declared_fragment_without_changing_case() -> None:
    tests = [
        {
            "kind": "source",
            "required_tokens": ["import json", "json.dumps("],
            "expected": True,
        }
    ]

    accepted = run_code("import json\nprint(json.dumps({'ok': True}))\n", tests)
    wrong_case = run_code("import json\nprint('JSON.dumps(')\n", tests)

    assert accepted["correct"] is True
    assert wrong_case["correct"] is False


def test_working_alternative_explains_why_the_lesson_still_requires_its_tool() -> None:
    result = run_code(
        "def subtotal(price, count):\n    return price + price + price\n",
        [
            {"kind": "call", "call": "subtotal(10, 3)", "expected": 30},
            {"kind": "source", "required_tokens": ["*"], "expected": True},
        ],
    )

    assert result["correct"] is False
    assert "код уже работает" in result["message"]
    assert "`*`" in result["message"]


def test_review_intervals_start_at_one_day() -> None:
    assert [main._review_interval_days(streak) for streak in range(1, 6)] == [1, 3, 7, 14, 30]


def test_mixed_selection_never_rotates_past_top_priority() -> None:
    questions = [
        {"id": "due", "kind": "choice"},
        {"id": "recent", "kind": "choice"},
    ]
    snapshot = {
        "weak_question_ids": [],
        "question_stats": {
            "recent": {
                "total_attempts": 1,
                "correct_streak": 1,
                "last_attempt_at": datetime.now(UTC).isoformat(),
            }
        },
    }

    selected = main._mixed_selection(questions, 1, snapshot)

    assert selected[0]["id"] == "due"


def test_assisted_answer_stays_in_review_until_two_independent_successes() -> None:
    database.init_db()
    database.record_attempt("question", True, hints_used=1)

    assisted = database.state()
    assert assisted["question_stats"]["question"]["correct_streak"] == 0
    assert "question" in assisted["weak_question_ids"]

    database.record_attempt("question", True)
    database.record_attempt("question", True)
    independent = database.state()
    assert independent["question_stats"]["question"]["correct_streak"] == 2
    assert "question" not in independent["weak_question_ids"]


def test_init_db_migrates_attempts_created_before_hint_tracking() -> None:
    with database.connection() as connection:
        connection.execute(
            """
            CREATE TABLE attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                correct INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

    database.init_db()

    with database.connection() as connection:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(attempts)")}
    assert "hints_used" in columns


def test_lesson_threshold_is_seventy_five_percent() -> None:
    assert main.required_lesson_answers(4) == 3
    assert main.required_lesson_answers(6) == 5


def test_next_module_waits_for_previous_exam() -> None:
    previous_module = MODULES[0]
    next_module = MODULES[1]
    previous_lessons = [
        lesson for lesson in LESSONS if lesson["module_id"] == previous_module["id"]
    ]
    first_next = next(lesson for lesson in LESSONS if lesson["module_id"] == next_module["id"])
    saved = {lesson["id"]: {"stars": 3} for lesson in previous_lessons}

    assert main.status_for(first_next, saved, {})["unlocked"] is False
    exams = {previous_module["id"]: {"score": 5, "total_count": 5}}
    assert main.status_for(first_next, saved, exams)["unlocked"] is True


def test_exam_delivery_can_shuffle_without_changing_question_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database.init_db()
    module = MODULES[0]
    module_lessons = [lesson for lesson in LESSONS if lesson["module_id"] == module["id"]]
    for lesson in module_lessons:
        database.save_lesson(lesson["id"], 4, 4, 0)

    class ReverseRandom:
        @staticmethod
        def shuffle(values: list) -> None:
            values.reverse()

    monkeypatch.setattr(main, "SystemRandom", ReverseRandom)
    payload = main.get_exam(module["id"])

    assert [item["id"] for item in payload["questions"]] == list(
        reversed(EXAMS[module["id"]]["question_ids"])
    )
    for question in payload["questions"]:
        source = QUESTION_BY_ID[question["id"]]
        if question["kind"] == "choice":
            assert question["options"] == list(reversed(source["options"]))


def test_lesson_choice_delivery_shuffles_a_copy_instead_of_putting_answer_first() -> None:
    class ReverseRandom:
        @staticmethod
        def shuffle(values: list) -> None:
            values.reverse()

    source = QUESTION_BY_ID["operators-arithmetic-choice"]
    original_options = list(source["options"])
    public = main.shuffled_public_question(source, ReverseRandom())

    assert public["options"] == list(reversed(original_options))
    assert source["options"] == original_options
    assert public["options"][0] != source["answer"]
