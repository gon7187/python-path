"""Дополнительные поведенческие сценарии для экзаменационного переноса.

Ключи реестра — исходные ``id`` code-вопросов из 32 экзаменов курса.
Сценарии намеренно не содержат проверок исходного текста или AST: экзамен
должен подтверждать, что решение работает на новых данных, а не узнаёт
единственную форму ответа из урока.
"""

from __future__ import annotations

EXAM_TRANSFER_TESTS: dict[str, list[dict[str, object]]] = {
    # Мягкий старт и базовый курс. У старых сценарных заданий без параметров
    # дополнительные проверки наблюдают новое свойство состояния или вывода.
    "warmup-types-code": [
        {"kind": "stdout", "expected": "пит", "comparison": "contains"},
    ],
    "warmup-recap-two-code": [
        {"kind": "value", "call": "score * 2", "expected": 8},
    ],
    "var-code": [
        {"kind": "value", "call": "city.lower()", "expected": "казань"},
    ],
    "challenge-strings-input": [
        {"kind": "value", "call": "city + '!'", "expected": "Казань!"},
    ],
    "for-code": [
        {"kind": "value", "call": "last ** 2", "expected": 9},
    ],
    "challenge-while-break": [
        {"kind": "value", "call": "number + 10", "expected": 15},
    ],
    "challenge-functions-greeting": [
        {
            "kind": "call",
            "call": "welcome('  Мира  ')",
            "expected": "Добро пожаловать, Мира!",
        },
    ],
    "challenge-sets": [
        {
            "kind": "call",
            "call": "unique_count([0, 0, -1, -1, 2])",
            "expected": 3,
        },
    ],
    "exception-code": [
        {"kind": "stdout", "expected": "цифры", "comparison": "contains"},
    ],
    "challenge-classes": [
        {
            "kind": "call",
            "call": "Badge().title + '!'",
            "expected": "Первые шаги!",
        },
    ],
    # Операторы и выражения.
    "operators-arithmetic-code": [
        {"kind": "call", "call": "subtotal(12.5, 4)", "expected": 50.0},
    ],
    "operators-integer-division-code": [
        {"kind": "call", "call": "leftover_minutes(181)", "expected": 1},
    ],
    "operators-booleans-code": [
        {"kind": "call", "call": "can_enter(30, True)", "expected": True},
    ],
    "operators-floating-point-code": [
        {"kind": "call", "call": "rounded_sum(2.222, 1.111)", "expected": 3.33},
    ],
    # Строки глубже.
    "strings-pro-indexes-code": [
        {"kind": "call", "call": "inner_code('курс')", "expected": "урс"},
    ],
    "strings-pro-search-replace-code": [
        {
            "kind": "call",
            "call": "normalize_decimal('0,25 руб,')",
            "expected": "0.25 руб.",
        },
    ],
    "strings-pro-split-join-code": [
        {"kind": "call", "call": "join_tags([])", "expected": ""},
    ],
    "strings-pro-formatting-code": [
        {"kind": "call", "call": "format_xp(7)", "expected": "    7 XP"},
    ],
    # Кортежи, срезы и списки.
    "tuples-slices-tuples-code": [
        {"kind": "call", "call": "list(make_point(0, -4))", "expected": [0, -4]},
    ],
    "tuples-slices-unpacking-code": [
        {
            "kind": "call",
            "call": "swap_point((True, None))",
            "expected": [None, True],
        },
    ],
    "tuples-slices-slices-code": [
        {
            "kind": "call",
            "call": "every_second([1, 2, 3, 4, 5, 6])",
            "expected": [1, 3, 5],
        },
    ],
    "tuples-slices-zip-enumerate-code": [
        {
            "kind": "call",
            "call": "numbered_names(['Май', 'Июнь', 'Июль'])",
            "expected": [[1, "Май"], [2, "Июнь"], [3, "Июль"]],
        },
    ],
    "lists-pro-list-methods-code": [
        {
            "kind": "call",
            "call": "add_task(['а', 'б'], 'в')",
            "expected": ["а", "б", "в"],
        },
    ],
    "lists-pro-sorting-code": [
        {
            "kind": "call",
            "call": "descending([2, 2, -1])",
            "expected": [2, 2, -1],
        },
    ],
    "lists-pro-stacks-queues-code": [
        {"kind": "call", "call": "take_last([1, 2, 3])", "expected": 3},
    ],
    "lists-pro-mutation-code": [
        {
            "kind": "call",
            "call": "remove_negatives([0, -2, 5, -1])",
            "expected": [0, 5],
        },
    ],
    # Словари, множества и управление потоком.
    "mappings-dict-basics-code": [
        {
            "kind": "call",
            "call": "display_name({'name': '', 'role': 'admin'})",
            "expected": "",
        },
    ],
    "mappings-dict-loops-code": [
        {
            "kind": "call",
            "call": "setting_lines({'a': 1, 'ready': False, 'note': None})",
            "expected": ["a=1", "ready=False", "note=None"],
        },
    ],
    "mappings-dict-merge-code": [
        {
            "kind": "call",
            "call": "merge_config({'x': 1}, {'x': 2, 'y': 3})",
            "expected": {"x": 2, "y": 3},
        },
    ],
    "mappings-sets-code": [
        {
            "kind": "call",
            "call": "shared_skills(['sql', 'python', 'git'], ['git', 'python'])",
            "expected": ["git", "python"],
        },
    ],
    "flow-advanced-elif-code": [
        {"kind": "call", "call": "grade(89)", "expected": "B"},
    ],
    "flow-advanced-match-code": [
        {"kind": "call", "call": "command_message('START')", "expected": "Неизвестно"},
    ],
    "flow-advanced-break-continue-code": [
        {
            "kind": "call",
            "call": "non_negative([0, -1, 2, -3])",
            "expected": [0, 2],
        },
    ],
    "flow-advanced-loop-else-code": [
        {
            "kind": "call",
            "call": "find_position(['x', 'y', 'x'], 'x')",
            "expected": 0,
        },
    ],
    # Функции, области видимости и comprehensions.
    "functions-pro-parameters-code": [
        {"kind": "call", "call": "move(0, -9)", "expected": [0, -9]},
    ],
    "functions-pro-defaults-code": [
        {
            "kind": "call",
            "call": "greet('Мир', 'Здравствуйте')",
            "expected": "Здравствуйте, Мир",
        },
    ],
    "functions-pro-keyword-args-code": [
        {
            "kind": "call",
            "call": "connect(timeout=1, host='api')",
            "expected": "api:1",
        },
    ],
    "functions-pro-varargs-code": [
        {
            "kind": "call",
            "call": "report('а', 'б', prefix='Итог')",
            "expected": "Итог: а, б",
        },
    ],
    "scope-legb-code": [
        {"kind": "call", "call": "show()[0]", "expected": "локально"},
    ],
    "scope-mutable-default-code": [
        {
            "kind": "call",
            "call": "add_item('z', ['x', 'y'])",
            "expected": ["x", "y", "z"],
        },
    ],
    "scope-closures-code": [
        {"kind": "call", "call": "multiplier(0)(999)", "expected": 0},
    ],
    "scope-lambda-key-code": [
        {
            "kind": "call",
            "call": "youngest_first([{'age': 8}, {'age': 3}, {'age': 5}])",
            "expected": [{"age": 3}, {"age": 5}, {"age": 8}],
        },
    ],
    "comprehensions-list-comprehension-code": [
        {
            "kind": "call",
            "call": "squares([-2, 0, 5])",
            "expected": [4, 0, 25],
        },
    ],
    "comprehensions-comprehension-filter-code": [
        {
            "kind": "call",
            "call": "even_squares([-4, -3, 0, 5])",
            "expected": [16, 0],
        },
    ],
    "comprehensions-dict-comprehension-code": [
        {
            "kind": "call",
            "call": "word_lengths(['', 'ёж'])",
            "expected": {"": 0, "ёж": 2},
        },
    ],
    "comprehensions-nested-comprehension-code": [
        {
            "kind": "call",
            "call": "all_pairs([1], [True, False])",
            "expected": [[1, True], [1, False]],
        },
    ],
    # Итераторы, генераторы и модули.
    "iterators-iterable-code": [
        {"kind": "call", "call": "first_two((9, 8, 7))", "expected": [9, 8]},
    ],
    "iterators-stop-iteration-code": [
        {
            "kind": "call",
            "call": "next_or(iter([None]), 'запас')",
            "expected": None,
        },
    ],
    "iterators-yield-code": [
        {"kind": "call", "call": "list(count_up(1))", "expected": [0]},
    ],
    "iterators-generator-expression-code": [
        {"kind": "call", "call": "square_total([-2, 4])", "expected": 20},
    ],
    "modules-imports-code": [
        {"kind": "call", "call": "square_root(16)", "expected": 4.0},
    ],
    "modules-main-guard-code": [
        {"kind": "call", "call": "should_start('')", "expected": False},
    ],
    "modules-packages-code": [
        {
            "kind": "call",
            "call": "import_path('pkg', 'sub.mod')",
            "expected": "pkg.sub.mod",
        },
    ],
    "modules-stdlib-imports-code": [
        {
            "kind": "call",
            "call": "child_path('root', 'file.txt')",
            "expected": "root/file.txt",
        },
    ],
    # Файлы, форматы и ошибки.
    "files-data-pathlib-code": [
        {
            "kind": "call",
            "call": "note_path('friday')",
            "expected": "notes/friday.txt",
        },
    ],
    "files-data-text-files-code": [
        {
            "kind": "call",
            "call": "save_and_read('transfer.txt', 'строка\\n2')",
            "expected": "строка\n2",
        },
    ],
    "files-data-json-code": [
        {
            "kind": "call",
            "call": "json_roundtrip({'nested': [1, None]})",
            "expected": {"nested": [1, None]},
        },
    ],
    "files-data-csv-code": [
        {
            "kind": "call",
            "call": "parse_scores(['name,score', 'Маша,0', 'Петя,-2'])",
            "expected": {"Маша": 0, "Петя": -2},
        },
    ],
    "errors-debug-exception-types-code": [
        {"kind": "call", "call": "parse_integer('  -7  ')", "expected": -7},
    ],
    "errors-debug-raise-code": [
        {"kind": "call", "call": "age_result(0)", "expected": 0},
    ],
    "errors-debug-finally-code": [
        {
            "kind": "call",
            "call": "parse_with_log('')",
            "expected": [0, ["Готово"]],
        },
    ],
    "errors-debug-debugging-code": [
        {
            "kind": "call",
            "call": "debug_value([1, 2])",
            "expected": "value=[1, 2]",
        },
    ],
    # ООП и типизация.
    "oop-design-init-code": [
        {"kind": "call", "call": "Task('Новая').title", "expected": "Новая"},
    ],
    "oop-design-repr-str-code": [
        {
            "kind": "call",
            "call": 'repr(Task("O\'Reilly"))',
            "expected": 'Task("O\'Reilly")',
        },
    ],
    "oop-design-class-instance-code": [
        {
            "kind": "call",
            "call": "Task('План').default_priority",
            "expected": "normal",
        },
    ],
    "oop-design-composition-code": [
        {
            "kind": "call",
            "call": "project_titles(['A', 'B', 'C'])",
            "expected": ["A", "B", "C"],
        },
    ],
    "oop-advanced-inheritance-code": [
        {"kind": "call", "call": "TimedTask('Ревью', 0).minutes", "expected": 0},
    ],
    "oop-advanced-properties-code": [
        {"kind": "call", "call": "Progress(5, 2).ratio", "expected": 2.5},
    ],
    "oop-advanced-protocols-code": [
        {"kind": "call", "call": "list(Countdown(1))", "expected": [1]},
    ],
    "oop-advanced-special-methods-code": [
        {"kind": "call", "call": "len(Box(['x']))", "expected": 1},
    ],
    "typing-models-annotations-code": [
        {"kind": "call", "call": "typed_total([-2, 5, 10])", "expected": 13},
    ],
    "typing-models-optional-union-code": [
        {
            "kind": "call",
            "call": "find_user({2: 'Лев', 3: 'Катя'}, 3)",
            "expected": "Катя",
        },
    ],
    "typing-models-generic-collections-code": [
        {
            "kind": "call",
            "call": "add_score({'А': 1}, 'А', 9)",
            "expected": {"А": 9},
        },
    ],
    "typing-models-dataclasses-enums-code": [
        {
            "kind": "call",
            "call": "user_label('Катя', 0)",
            "expected": "Катя · 0",
        },
    ],
    # Стандартная библиотека и регулярные выражения.
    "stdlib-core-datetime-code": [
        {
            "kind": "call",
            "call": "after_days('2025-12-31', 1)",
            "expected": "2026-01-01",
        },
    ],
    "stdlib-core-random-code": [
        {
            "kind": "call",
            "call": "seeded_choice([1, 2, 3, 4], 0)",
            "expected": 4,
        },
    ],
    "stdlib-core-math-statistics-code": [
        {"kind": "call", "call": "average([1, 2])", "expected": 1.5},
    ],
    "stdlib-core-decimal-code": [
        {"kind": "call", "call": "exact_total('2.50', 4)", "expected": "10.00"},
    ],
    "stdlib-productivity-collections-code": [
        {
            "kind": "call",
            "call": "word_counts(['a', 'b', 'a', 'a'])",
            "expected": {"a": 3, "b": 1},
        },
    ],
    "stdlib-productivity-itertools-code": [
        {
            "kind": "call",
            "call": "pair_labels(['a', 'b', 'c', 'd'])",
            "expected": ["a+b", "a+c", "a+d", "b+c", "b+d", "c+d"],
        },
    ],
    "stdlib-productivity-functools-code": [
        {"kind": "call", "call": "fib(10)", "expected": 55},
    ],
    "stdlib-productivity-heapq-bisect-code": [
        {
            "kind": "call",
            "call": "priority_order([[2, 'z'], [1, 'b'], [1, 'a']])",
            "expected": ["a", "b", "z"],
        },
    ],
    "regex-patterns-code": [
        {"kind": "call", "call": "is_iso_date('1999-12-31')", "expected": True},
    ],
    "regex-groups-code": [
        {
            "kind": "call",
            "call": "parse_metric('items: 007')",
            "expected": {"name": "items", "value": 7},
        },
    ],
    "regex-validation-code": [
        {"kind": "call", "call": "valid_postal_code('000000')", "expected": True},
    ],
    "regex-substitution-code": [
        {
            "kind": "call",
            "call": "collapse_spaces('\\tPython \\n path  ')",
            "expected": "Python path",
        },
    ],
    # Тестирование, качество и CLI.
    "testing-unit-tests-code": [
        {"kind": "call", "call": "check_discount(50, 45.0)", "expected": True},
    ],
    "testing-fixtures-code": [
        {
            "kind": "call",
            "call": "level_up_scenario(lambda: {'level': -1})",
            "expected": 0,
        },
    ],
    "testing-parametrize-code": [
        {
            "kind": "call",
            "call": "run_cases(lambda value: value ** 2, [[2, 4], [-3, 9], [0, 1]])",
            "expected": [True, True, False],
        },
    ],
    "testing-mocks-code": [
        {
            "kind": "call",
            "call": "deadline(FakeClock('1999-12-31'))",
            "expected": "1999-12-31 + 7 дней",
        },
    ],
    "quality-pep8-code": [
        {"kind": "call", "call": "total_score([-2, 10, 1])", "expected": 9},
    ],
    "quality-format-lint-code": [
        {
            "kind": "call",
            "call": "lint_commands('src/app')",
            "expected": ["ruff format src/app", "ruff check src/app"],
        },
    ],
    "quality-docstrings-code": [
        {"kind": "call", "call": "total([0, -3, 8])", "expected": 5},
    ],
    "quality-git-code": [
        {
            "kind": "call",
            "call": "commit_commands('docs/guide.md', 'Исправить текст')",
            "expected": [
                "git status",
                "git add docs/guide.md",
                "git commit -m 'Исправить текст'",
            ],
        },
    ],
    "cli-environment-argv-code": [
        {
            "kind": "call",
            "call": "input_argument(['--input=archive.zip'])",
            "expected": "archive.zip",
        },
    ],
    "cli-environment-environment-code": [
        {"kind": "call", "call": "api_url({'API_URL': ''})", "expected": ""},
    ],
    "cli-environment-venv-code": [
        {
            "kind": "call",
            "call": "activation_command('macos')",
            "expected": "source .venv/bin/activate",
        },
    ],
    "cli-environment-pyproject-code": [
        {
            "kind": "call",
            "call": "project_name({'project': {'name': ''}})",
            "expected": "",
        },
    ],
    # HTTP, базы данных и конкурентность.
    "http-api-request-response-code": [
        {
            "kind": "call",
            "call": "request_line('patch', '/api/v1/items/7')",
            "expected": "PATCH /api/v1/items/7 HTTP/1.1",
        },
    ],
    "http-api-json-api-code": [
        {
            "kind": "call",
            "call": "task_payload('', True)",
            "expected": {"title": "", "done": True},
        },
    ],
    "http-api-status-codes-code": [
        {"kind": "call", "call": "status_group(301)", "expected": "other"},
    ],
    "http-api-pagination-code": [
        {
            "kind": "call",
            "call": "page(list(range(6)), 2, 4)",
            "expected": [4, 5],
        },
    ],
    "databases-relational-code": [
        {
            "kind": "call",
            "call": "row_to_task([0, '', 2])",
            "expected": {"id": 0, "title": "", "done": True},
        },
    ],
    "databases-crud-code": [
        {
            "kind": "call",
            "call": "task_query(0)",
            "expected": "SELECT id, title FROM tasks WHERE done = 0",
        },
    ],
    "databases-parameters-code": [
        {"kind": "call", "call": "select_by_id(2)", "expected": "Тесты"},
    ],
    "databases-transactions-code": [
        {
            "kind": "call",
            "call": "transfer({'A': 5}, 'A', 'C', 5)",
            "expected": {"A": 0, "C": 5},
        },
    ],
    "concurrency-threads-processes-code": [
        {"kind": "call", "call": "worker_kind('network')", "expected": "sequential"},
    ],
    "concurrency-thread-pool-code": [
        {
            "kind": "call",
            "call": "pool_map(lambda value: value + 10, [-1, 0, 2])",
            "expected": [9, 10, 12],
        },
    ],
    "concurrency-locks-code": [
        {
            "kind": "call",
            "call": "apply_updates(-10, [5, 5, -1])",
            "expected": -1,
        },
    ],
    "concurrency-queues-code": [
        {
            "kind": "call",
            "call": "process_queue([1, None, 3])",
            "expected": [1, None, 3],
        },
    ],
    # Асинхронность и итоговые проекты курса.
    "async-coroutines-code": [
        {"kind": "call", "call": "asyncio.run(fetch(-4))", "expected": -8},
    ],
    "async-tasks-code": [
        {
            "kind": "call",
            "call": "asyncio.run(run_pair(-1, 3))",
            "expected": [-2, 6],
        },
    ],
    "async-gather-timeouts-code": [
        {
            "kind": "call",
            "call": "asyncio.run(gather_squares([-2, 0, 4]))",
            "expected": [4, 0, 16],
        },
    ],
    "async-async-design-code": [
        {
            "kind": "call",
            "call": "asyncio.run(polite_total([-5, 2, 10]))",
            "expected": 7,
        },
    ],
    "capstones-task-manager-code": [
        {
            "kind": "call",
            "call": "toggle_task({'title': 'Новая'})",
            "expected": {"title": "Новая", "done": True},
        },
    ],
    "capstones-notes-app-code": [
        {
            "kind": "call",
            "call": "notes_roundtrip([{'title': '', 'tags': ['a']}])",
            "expected": [{"title": "", "tags": ["a"]}],
        },
    ],
    "capstones-api-client-code": [
        {"kind": "call", "call": "weather_result(200, {})", "expected": None},
    ],
    "capstones-release-code": [
        {
            "kind": "call",
            "call": "missing_release_files([])",
            "expected": ["src", "tests", "pyproject.toml", "README.md"],
        },
    ],
}


EXAM_TRANSFER_TEST_COUNT = sum(len(tests) for tests in EXAM_TRANSFER_TESTS.values())


def transfer_tests_for(source_question_id: str) -> list[dict[str, object]]:
    """Вернуть независимые копии переносных проверок для исходного вопроса."""
    return [dict(test) for test in EXAM_TRANSFER_TESTS.get(source_question_id, ())]
