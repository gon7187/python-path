"""Рукописные уроки 73–80: аннотации типов и стандартная библиотека."""

from __future__ import annotations

from typing import Any


def _card(title: str, text: str, example: str, tip: str = "") -> dict[str, str]:
    return {"title": title, "text": text, "example": example, "tip": tip}


def _choice(
    lesson_id: str,
    prompt: str,
    options: list[str],
    answer: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{lesson_id}-choice",
        "kind": "choice",
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def _term(
    lesson_id: str,
    prompt: str,
    answers: list[str],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{lesson_id}-term",
        "kind": "input",
        "prompt": prompt,
        "answers": answers,
        "placeholder": "Введите ответ",
        "explanation": explanation,
    }


def _code(
    lesson_id: str,
    prompt: str,
    starter: str,
    tests: list[dict[str, Any]],
    reference: str,
    explanation: str,
    hint: str,
) -> dict[str, Any]:
    return {
        "id": f"{lesson_id}-code",
        "kind": "code",
        "prompt": prompt,
        "starter": starter,
        "tests": tests,
        "reference": reference,
        "explanation": explanation,
        "hint": hint,
    }


def _lesson(
    lesson_id: str,
    subtitle: str,
    theory: list[dict[str, str]],
    questions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": lesson_id,
        "subtitle": subtitle,
        "theory": theory,
        "questions": questions,
    }


LESSONS: list[dict[str, Any]] = [
    _lesson(
        "typing-models-annotations",
        "Подсказки типов для читателя и проверок",
        [
            _card(
                "Аннотация описывает контракт",
                "Аннотация — это пометка типа в заголовке функции. Запись `a: int` "
                "говорит, что в `a` ждут целое число, а `-> int` — что функция вернёт "
                "целое. Python не проверяет такие пометки при запуске, но читатель "
                "сразу видит, какие данные сюда приходят и что уйдут обратно.",
                "def add(a: int, b: int) -> int:\n"
                "    return a + b\n"
                "\n"
                "print(add(2, 3))\n"
                "# Вывод:\n"
                "# 5",
            ),
            _card(
                "Аннотация не мешает передать другой тип",
                "Пометка типа — обещание, а не запрет. В примере написано `int`, но "
                "строка тоже принимается: умножение повторяет её. Это удобно для "
                "чтения, однако защиту от неверных данных аннотация не даёт. "
                "Проверку значений всё равно пиши в коде.",
                "def double(value: int) -> int:\n"
                "    return value * 2\n"
                "\n"
                "print(double(3))\n"
                "print(double('да'))\n"
                "# Вывод:\n"
                "# 6\n"
                "# дада",
            ),
            _card(
                "Типичная ошибка: аннотация врёт о типе",
                "Здесь в заголовке обещан `str`, а функция возвращает число. Python "
                "промолчит: аннотации не проверяются во время работы. Заметь ошибку, "
                "сравнив `-> str` с настоящим результатом — в выводе число без "
                "кавычек. Такую нестыковку ловит линтер или внимательный читатель.",
                "def next_age(age: int) -> str:\n"
                "    return age + 1\n"
                "\n"
                "print(next_age(20))\n"
                "# Вывод:\n"
                "# 21",
                "Аннотация должна совпадать с тем, что функция реально возвращает.",
            ),
        ],
        [
            _choice(
                "typing-models-annotations",
                "Что выведет этот код?\n"
                "\n"
                "def greet(name: str) -> str:\n"
                "    return 'Привет, ' + name\n"
                "\n"
                "print(greet('Аня'))",
                ["Привет, Аня", "Привет, Анна", "Привет, name", "Привет, str"],
                "Привет, Аня",
                "Аннотация не меняет значение: функция склеивает «Привет, » и переданное имя.",
            ),
            _term(
                "typing-models-annotations",
                "Как называется пометка типа рядом с параметром функции?",
                ["аннотация", "аннотация типа", "type hint", "typehint"],
                "`a: int` — аннотация типа: подсказка для читателя и инструментов проверки.",
            ),
            _code(
                "typing-models-annotations",
                "Напиши `mean(values: list[float]) -> float`: верни среднее значение "
                "списка. Сохрани аннотации параметра и результата.",
                "def mean(values: list[float]) -> float:\n    # верни среднее значение\n    pass\n",
                [
                    {"kind": "call", "call": "mean([1, 2, 3])", "expected": 2.0},
                    {"kind": "call", "call": "mean([4, 6])", "expected": 5.0},
                    {"kind": "call", "call": "mean([0])", "expected": 0.0},
                ],
                "def mean(values: list[float]) -> float:\n    return sum(values) / len(values)\n",
                "Верно: аннотация обещает список чисел на входе и число на выходе, "
                "а сумма делится на количество.",
                "Среднее — это сумма всех значений, делённая на их количество.",
            ),
        ],
    ),
    _lesson(
        "typing-models-optional-union",
        "None и объединения типов",
        [
            _card(
                "int | None значит «число или ничего»",
                "Вертикальная черта объединяет типы. Запись `int | None` читается так: "
                "функция вернёт целое число или `None`. Такой контракт честно говорит, "
                "что результата может не быть. Вызывающий код обязан проверить "
                "значение, прежде чем считать с ним что-то.",
                "def first_or_none(items: list[int]) -> int | None:\n"
                "    if items:\n"
                "        return items[0]\n"
                "    return None\n"
                "\n"
                "print(first_or_none([7, 8]))\n"
                "print(first_or_none([]))\n"
                "# Вывод:\n"
                "# 7\n"
                "# None",
            ),
            _card(
                "get возвращает None для пропуска",
                "У словаря метод `get` не падает на отсутствующем ключе, а возвращает "
                "`None`. Это естественный способ получить необязательное значение. "
                "Сравни: обращение через квадратные скобки на пропуске бросило бы "
                "`KeyError`, а `get` спокойно отдаёт `None`.",
                "ages = {'Аня': 20, 'Ли': 25}\n"
                "print(ages.get('Аня'))\n"
                "print(ages.get('Бот'))\n"
                "# Вывод:\n"
                "# 20\n"
                "# None",
            ),
            _card(
                "Типичная ошибка: проверять значение вместо None",
                "Возраст `0` — настоящие данные, но в условии `if age:` он считается "
                "ложным. Программа молча подменяет ноль на «нет данных». Заметь это по "
                "пропавшему нулю в выводе. Когда отсутствие значит именно `None`, "
                "проверяй `age is None`, а не истинность значения.",
                "age = 0\n"
                "if age:\n"
                "    print('возраст', age)\n"
                "else:\n"
                "    print('нет данных')\n"
                "# Вывод:\n"
                "# нет данных",
                "Ноль и пустая строка тоже ложны — для None нужна отдельная проверка.",
            ),
        ],
        [
            _choice(
                "typing-models-optional-union",
                "Что выведет этот код?\n"
                "\n"
                "def find(users: dict[str, int], name: str) -> int | None:\n"
                "    return users.get(name)\n"
                "\n"
                "print(find({'Аня': 20}, 'Ли'))",
                ["None", "ноль", "False", "KeyError"],
                "None",
                "Для отсутствующего ключа get возвращает None, а не бросает KeyError.",
            ),
            _term(
                "typing-models-optional-union",
                "Что возвращает `dict.get`, если ключа в словаре нет?",
                ["None", "none", "null"],
                "`get` возвращает `None`, поэтому его удобно использовать для необязательных значений.",
            ),
            _code(
                "typing-models-optional-union",
                "Напиши `find_age(users: dict[str, int], name: str) -> int | None`: "
                "верни возраст через `.get`, а если имени нет — `None`.",
                "def find_age(users: dict[str, int], name: str) -> int | None:\n"
                "    # достань возраст через .get\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "find_age({'Аня': 20}, 'Аня')",
                        "expected": 20,
                    },
                    {"kind": "call", "call": "find_age({}, 'Ли')", "expected": None},
                    {
                        "kind": "call",
                        "call": "find_age({'Аня': 0}, 'Аня')",
                        "expected": 0,
                    },
                ],
                "def find_age(users: dict[str, int], name: str) -> int | None:\n"
                "    return users.get(name)\n",
                "Верно: get сразу даёт возраст или None, поэтому отдельная ветка не нужна.",
                "Не используй users[name] — на отсутствующем имени это KeyError.",
            ),
        ],
    ),
    _lesson(
        "typing-models-generic-collections",
        "list, dict, set и tuple с типами элементов",
        [
            _card(
                "Тип коллекции уточняют в квадратных скобках",
                "Для коллекций аннотация называет не только вид, но и тип элементов. "
                "`list[int]` — список целых, `dict[str, int]` — словарь, где ключи "
                "строки, а значения целые. Такая запись помогает не перепутать, что "
                "лежит внутри, ещё до запуска кода.",
                "scores: dict[str, int] = {'Аня': 10, 'Ли': 12}\n"
                "\n"
                "print(scores['Аня'])\n"
                "# Вывод:\n"
                "# 10",
            ),
            _card(
                "Аннотация объясняет цикл",
                "Когда структура подписана, цикл читается легче: из `dict[str, float]` "
                "приходят имя и цена. Типы элементов не меняют поведение кода, но "
                "служат документацией прямо в строке объявления. Особенно полезно, "
                "когда словарь большой.",
                "prices: dict[str, float] = {'хлеб': 40.5, 'сыр': 320.0}\n"
                "for name, price in prices.items():\n"
                "    print(name, price)\n"
                "# Вывод:\n"
                "# хлеб 40.5\n"
                "# сыр 320.0",
            ),
            _card(
                "Типичная ошибка: ждать, что аннотация преобразует данные",
                "Здесь написано `list[int]`, но в списке лежат строки. Аннотация — "
                "только пометка, она не превращает `'1'` в `1`. Заметь ошибку по "
                "кавычкам в выводе: числа в кавычках остались строками. Приводи типы "
                "явно через `int(...)`.",
                "values: list[int] = ['1', '2']\n\nprint(values)\n# Вывод:\n# ['1', '2']",
                "Аннотация не вызывает int() и не проверяет элементы.",
            ),
        ],
        [
            _choice(
                "typing-models-generic-collections",
                "Что выведет этот код?\n"
                "\n"
                "groups: dict[int, list[str]] = {}\n"
                "for word in ['дом', 'кот', 'лес', 'он']:\n"
                "    groups.setdefault(len(word), []).append(word)\n"
                "print(groups)",
                [
                    "{3: ['дом', 'кот', 'лес'], 2: ['он']}",
                    "{3: ['дом', 'кот'], 2: ['лес', 'он']}",
                    "{'дом': 3, 'кот': 3, 'лес': 3, 'он': 2}",
                    "{2: ['он'], 3: ['дом', 'кот', 'лес']}",
                ],
                "{3: ['дом', 'кот', 'лес'], 2: ['он']}",
                "setdefault заводит список для новой длины, а append добавляет слово в нужную группу.",
            ),
            _term(
                "typing-models-generic-collections",
                "Как записать тип словаря, где ключи — строки, а значения — целые?",
                ["dict[str, int]", "dict[str,int]"],
                "`dict[str, int]` уточняет тип ключей и значений внутри словаря.",
            ),
            _code(
                "typing-models-generic-collections",
                "Напиши `group_by_len(words: list[str]) -> dict[int, list[str]]`: "
                "сгруппируй слова по длине, сохранив порядок появления.",
                "def group_by_len(words: list[str]) -> dict[int, list[str]]:\n"
                "    # сгруппируй слова по длине\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "group_by_len(['да', 'нет', 'ок'])"
                        " == {2: ['да', 'ок'], 3: ['нет']}",
                        "expected": True,
                    },
                    {"kind": "call", "call": "group_by_len([]) == {}", "expected": True},
                    {
                        "kind": "call",
                        "call": "group_by_len(['кот']) == {3: ['кот']}",
                        "expected": True,
                    },
                ],
                "def group_by_len(words: list[str]) -> dict[int, list[str]]:\n"
                "    groups: dict[int, list[str]] = {}\n"
                "    for word in words:\n"
                "        groups.setdefault(len(word), []).append(word)\n"
                "    return groups\n",
                "Верно: ключ словаря — длина слова, а значение — список слов этой длины.",
                "setdefault(len(word), []) вернёт готовый список или создаст новый.",
            ),
        ],
    ),
    _lesson(
        "typing-models-dataclasses-enums",
        "Данные с именами и фиксированные состояния",
        [
            _card(
                "dataclass сам пишет служебные методы",
                "Декоратор `@dataclass` превращает описание полей в готовый класс: "
                "появляются `__init__`, сравнение и понятное представление. Тебе "
                "остаётся перечислить поля с типами. Это убирает шаблонный код у "
                "моделей данных вроде точки или задачи.",
                "from dataclasses import dataclass\n"
                "\n"
                "@dataclass\n"
                "class Point:\n"
                "    x: int\n"
                "    y: int\n"
                "\n"
                "print(Point(1, 2))\n"
                "# Вывод:\n"
                "# Point(x=1, y=2)",
            ),
            _card(
                "Enum фиксирует допустимые состояния",
                "`Enum` — это набор именованных постоянных значений. Вместо строки "
                "`'новая'`, которую легко опечатать, берут `Status.NEW`. У члена Enum "
                "есть `.name` и `.value`. Часто его кладут в dataclass как поле со "
                "значением по умолчанию.",
                "from dataclasses import dataclass\n"
                "from enum import Enum\n"
                "\n"
                "class Status(Enum):\n"
                "    NEW = 'новая'\n"
                "    DONE = 'готова'\n"
                "\n"
                "@dataclass\n"
                "class Task:\n"
                "    title: str\n"
                "    status: Status = Status.NEW\n"
                "\n"
                "task = Task('отчёт')\n"
                "print(task.title, task.status.value)\n"
                "# Вывод:\n"
                "# отчёт новая",
            ),
            _card(
                "Типичная ошибка: сравнивать Enum со строкой",
                "Член Enum не равен своему значению: `Status.NEW` — объект, а "
                "`'новая'` — строка. Сравнение молча даёт `False`, и ветка кода не "
                "срабатывает. Заметь это по `False` в выводе. Сравнивай с "
                "`Status.NEW` или доставай строку через `.value`.",
                "from enum import Enum\n"
                "\n"
                "class Status(Enum):\n"
                "    NEW = 'новая'\n"
                "\n"
                "print(Status.NEW == 'новая')\n"
                "# Вывод:\n"
                "# False",
                "Enum сравнивается с членом Enum, а не с его строковым значением.",
            ),
        ],
        [
            _choice(
                "typing-models-dataclasses-enums",
                "Что выведет этот код?\n"
                "\n"
                "from dataclasses import dataclass\n"
                "\n"
                "@dataclass\n"
                "class Task:\n"
                "    title: str\n"
                "    done: bool = False\n"
                "\n"
                "print(Task('b').done, Task('b', True).done)",
                ["False True", "True False", "False False", "True True"],
                "False True",
                "Без второго аргумента done остаётся False, а переданный True сохраняется.",
            ),
            _term(
                "typing-models-dataclasses-enums",
                "Каким декоратором создают класс данных с полями?",
                ["dataclass", "@dataclass", "dataclasses.dataclass"],
                "`@dataclass` генерирует для класса инициализатор и служебные методы.",
            ),
            _code(
                "typing-models-dataclasses-enums",
                "Опиши `@dataclass class Task` с полями `title: str` и "
                "`done: bool = False`, затем напиши `progress(tasks)`: верни строку "
                "`'выполнено X из Y'`.",
                "from dataclasses import dataclass\n"
                "\n"
                "\n"
                "@dataclass\n"
                "class Task:\n"
                "    title: str\n"
                "    done: bool = False\n"
                "\n"
                "\n"
                "def progress(tasks: list[Task]) -> str:\n"
                "    # посчитай выполненные задачи\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "progress([Task('a', True), Task('b')])",
                        "expected": "выполнено 1 из 2",
                    },
                    {"kind": "call", "call": "Task('c').done is False", "expected": True},
                    {"kind": "call", "call": "progress([])", "expected": "выполнено 0 из 0"},
                ],
                "from dataclasses import dataclass\n"
                "\n"
                "\n"
                "@dataclass\n"
                "class Task:\n"
                "    title: str\n"
                "    done: bool = False\n"
                "\n"
                "\n"
                "def progress(tasks: list[Task]) -> str:\n"
                "    done = 0\n"
                "    for task in tasks:\n"
                "        if task.done:\n"
                "            done += 1\n"
                "    return 'выполнено ' + str(done) + ' из ' + str(len(tasks))\n",
                "Верно: dataclass даёт поле done со значением False, а progress считает "
                "истинные флаги.",
                "Собери результат из строки, числа выполненных и общего количества.",
            ),
        ],
    ),
    _lesson(
        "stdlib-core-datetime",
        "date, datetime и timedelta",
        [
            _card(
                "date хранит календарный день",
                "Модуль `datetime` даёт тип `date` для дня без времени. Объект знает "
                "год, месяц и день, а печатается в привычном ISO-виде. Создавай его "
                "из чисел или из строки через `fromisoformat` — так код не зависит от "
                "порядка полей в тексте.",
                "from datetime import date\n"
                "\n"
                "d = date(2024, 3, 1)\n"
                "print(d)\n"
                "print(d.year, d.month, d.day)\n"
                "# Вывод:\n"
                "# 2024-03-01\n"
                "# 2024 3 1",
            ),
            _card(
                "Разность дат даёт дни",
                "Если вычесть одну дату из другой, получится интервал `timedelta`. У "
                "него есть атрибут `.days` — целое число дней. Это надёжнее ручного "
                "подсчёта: Python сам учитывает длину месяцев и високосный год.",
                "from datetime import date\n"
                "\n"
                "start = date.fromisoformat('2024-01-01')\n"
                "end = date.fromisoformat('2024-01-11')\n"
                "print((end - start).days)\n"
                "# Вывод:\n"
                "# 10",
            ),
            _card(
                "Типичная ошибка: перепутать даты местами",
                "Если вычесть раннюю дату из поздней наоборот, получится отрицательное "
                "число. Код не падает, но ответ бессмыслен. Заметь ошибку по минусу "
                "перед числом: для положительного интервала поздняя дата должна быть "
                "слева. Сверь порядок аргументов с условием.",
                "from datetime import date\n"
                "\n"
                "start = date.fromisoformat('2024-03-01')\n"
                "end = date.fromisoformat('2024-01-01')\n"
                "print((end - start).days)\n"
                "# Вывод:\n"
                "# -60",
                "Минус в ответе — сигнал, что даты стоят не в том порядке.",
            ),
        ],
        [
            _choice(
                "stdlib-core-datetime",
                "Что выведет этот код?\n"
                "\n"
                "from datetime import date\n"
                "\n"
                "a = date.fromisoformat('2024-05-01')\n"
                "b = date.fromisoformat('2024-05-11')\n"
                "print((b - a).days)",
                ["10", "11", "9", "1"],
                "10",
                "Разность дат считает дни между ними: от 1 мая до 11 мая проходит 10 дней.",
            ),
            _term(
                "stdlib-core-datetime",
                "Какой модуль стандартной библиотеки отвечает за дату и время?",
                ["datetime", "модуль datetime"],
                "`datetime` содержит `date`, `datetime`, `timedelta` и разбор ISO-строк.",
            ),
            _code(
                "stdlib-core-datetime",
                "Напиши `days_between(a, b)`: по двум ISO-датам верни число дней от "
                "`a` до `b`. Используй `from datetime import date`.",
                "from datetime import date\n"
                "\n"
                "\n"
                "def days_between(a, b):\n"
                "    # верни число дней между датами\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "days_between('2024-01-01', '2024-03-01')",
                        "expected": 60,
                    },
                    {
                        "kind": "call",
                        "call": "days_between('2024-05-05', '2024-05-05')",
                        "expected": 0,
                    },
                    {
                        "kind": "call",
                        "call": "days_between('2024-03-01', '2024-01-01')",
                        "expected": -60,
                    },
                ],
                "from datetime import date\n"
                "\n"
                "\n"
                "def days_between(a, b):\n"
                "    return (date.fromisoformat(b) - date.fromisoformat(a)).days\n",
                "Верно: fromisoformat разбирает строки, а разность дат даёт timedelta с днями.",
                "Сначала преврати обе строки в date, затем вычти раннюю из поздней.",
            ),
        ],
    ),
    _lesson(
        "stdlib-core-random",
        "Воспроизводимая псевдослучайность",
        [
            _card(
                "random выбирает значения",
                "Модуль `random` даёт псевдослучайные числа и выбор из коллекции. Если "
                "создать `random.Random(seed)` с одним и тем же seed, последовательность "
                "повторится. Это важно для тестов и примеров: результат можно проверить "
                "и воспроизвести.",
                "import random\n"
                "\n"
                "rng = random.Random(42)\n"
                "print(rng.choice(['камень', 'бумага', 'ножницы']))\n"
                "# Вывод:\n"
                "# ножницы",
            ),
            _card(
                "Перемешивай копию, а не исходник",
                "`shuffle` меняет список на месте и ничего не возвращает. Чтобы исходные "
                "данные остались нетронутыми, сначала сделай копию через `list(...)`, а "
                "потом перемешай её. Тогда порядок в `names` сохранится, а `order` "
                "станет случайным.",
                "import random\n"
                "\n"
                "names = ['Аня', 'Ли', 'Бот']\n"
                "rng = random.Random(7)\n"
                "order = list(names)\n"
                "rng.shuffle(order)\n"
                "print(order)\n"
                "print(names)\n"
                "# Вывод:\n"
                "# ['Бот', 'Аня', 'Ли']\n"
                "# ['Аня', 'Ли', 'Бот']",
            ),
            _card(
                "Типичная ошибка: copy = items не копирует список",
                "Присваивание даёт второе имя тому же списку. После `shuffle` меняется "
                "и `copy`, и `items`, хотя казалось, что копия отдельная. Заметь ошибку "
                "по изменившемуся исходнику. Настоящую копию создают через "
                "`list(items)` или `items[:]`.",
                "import random\n"
                "\n"
                "items = [1, 2, 3, 4]\n"
                "copy = items\n"
                "random.Random(7).shuffle(copy)\n"
                "print(items)\n"
                "# Вывод:\n"
                "# [4, 2, 1, 3]",
                "Присваивание не копирует данные — оно создаёт второе имя.",
            ),
        ],
        [
            _choice(
                "stdlib-core-random",
                "Что выведет этот код?\n"
                "\n"
                "import random\n"
                "\n"
                "a = random.Random(7).randint(1, 100)\n"
                "b = random.Random(7).randint(1, 100)\n"
                "print(a == b)",
                ["True", "False", "None", "ошибка"],
                "True",
                "Оба генератора созданы с одним seed 7, поэтому выдают одно и то же число.",
            ),
            _term(
                "stdlib-core-random",
                "Что передают в `random.Random`, чтобы последовательность повторялась?",
                ["seed", "зерно", "число seed"],
                "Seed — стартовое число генератора: одинаковый seed даёт одинаковую последовательность.",
            ),
            _code(
                "stdlib-core-random",
                "Напиши `shuffled(items, seed)`: верни перемешанную копию списка через "
                "`random.Random(seed)`, не меняя исходный список.",
                "import random\n"
                "\n"
                "\n"
                "def shuffled(items, seed):\n"
                "    # верни перемешанную копию\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "sorted(shuffled([3, 1, 2], 7))",
                        "expected": [1, 2, 3],
                    },
                    {"kind": "call", "call": "shuffled([], 7)", "expected": []},
                    {"kind": "call", "call": "shuffled([5], 7)", "expected": [5]},
                ],
                "import random\n"
                "\n"
                "\n"
                "def shuffled(items, seed):\n"
                "    result = list(items)\n"
                "    random.Random(seed).shuffle(result)\n"
                "    return result\n",
                "Верно: копия отделена от исходника, а seed делает перемешивание воспроизводимым.",
                "Сначала list(items), затем shuffle у нового списка.",
            ),
        ],
    ),
    _lesson(
        "stdlib-core-math-statistics",
        "math и statistics без сторонних пакетов",
        [
            _card(
                "math решает точечные расчёты",
                "Модуль `math` содержит корни, степени, округление и константы. Функции "
                "возвращают числа, а не печатают их, поэтому результат можно передать "
                "дальше. Для простой арифметики он не нужен, но для `sqrt` или `floor` "
                "это короткий и точный инструмент.",
                "import math\n\nprint(math.sqrt(16))\nprint(math.floor(3.7))\n# Вывод:\n# 4.0\n# 3",
            ),
            _card(
                "statistics считает среднее и медиану",
                "`statistics.mean` возвращает среднее арифметическое, а "
                "`statistics.median` — середину упорядоченного ряда. Для чётного "
                "количества медиана — среднее двух центральных значений. Эти функции "
                "сами заботятся о сумме и делении.",
                "import statistics\n"
                "\n"
                "scores = [2, 4, 4, 10]\n"
                "print(statistics.mean(scores))\n"
                "print(statistics.median(scores))\n"
                "# Вывод:\n"
                "# 5\n"
                "# 4.0",
            ),
            _card(
                "Типичная ошибка: делить среднее через //",
                "Оператор `//` отбрасывает дробную часть. Для `[1, 2]` настоящее среднее "
                "равно `1.5`, но целочисленное деление даёт `1`. Ошибка не бросается, "
                "просто число становится неточным. Заметь её по неверному результату и "
                "используй `/` или `statistics.mean`.",
                "scores = [1, 2]\n\nprint(sum(scores) // len(scores))\n# Вывод:\n# 1",
                "Для среднего нужно обычное деление, а не целочисленное.",
            ),
        ],
        [
            _choice(
                "stdlib-core-math-statistics",
                "Что выведет этот код?\n"
                "\n"
                "import statistics\n"
                "\n"
                "print(statistics.median([1, 3, 4, 10]))",
                ["3.5", "3.0", "4.0", "2.5"],
                "3.5",
                "В списке четыре значения, поэтому медиана — среднее двух центральных: (3 + 4) / 2.",
            ),
            _term(
                "stdlib-core-math-statistics",
                "Какая функция `statistics` считает среднее арифметическое?",
                ["statistics.mean", "mean", "mean()"],
                "`statistics.mean` суммирует значения и делит на их количество.",
            ),
            _code(
                "stdlib-core-math-statistics",
                "Напиши `stats(values)`: верни кортеж из среднего и медианы через "
                "модуль `statistics`.",
                "import statistics\n"
                "\n"
                "\n"
                "def stats(values):\n"
                "    # верни среднее и медиану\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "stats([1, 2, 3, 10]) == (4, 2.5)",
                        "expected": True,
                    },
                    {"kind": "call", "call": "stats([7]) == (7, 7)", "expected": True},
                    {"kind": "call", "call": "stats([2, 4]) == (3, 3.0)", "expected": True},
                ],
                "import statistics\n"
                "\n"
                "\n"
                "def stats(values):\n"
                "    return (statistics.mean(values), statistics.median(values))\n",
                "Верно: mean и median берут на себя расчёт, а кортеж сохраняет порядок "
                "«среднее, медиана».",
                "Верни именно кортеж: (statistics.mean(values), statistics.median(values)).",
            ),
        ],
    ),
    _lesson(
        "stdlib-core-decimal",
        "Decimal вместо float для денег",
        [
            _card(
                "Decimal хранит десятичные дроби точно",
                "Тип `Decimal` из модуля `decimal` представляет десятичное число без "
                "двоичных сюрпризов float. Для денег это важно: `0.10 + 0.20` должно "
                "дать ровно `0.30`. Создавай Decimal из строки, чтобы значение не "
                "испортилось ещё на входе.",
                "from decimal import Decimal\n"
                "\n"
                "print(Decimal('0.10') + Decimal('0.20'))\n"
                "# Вывод:\n"
                "# 0.30",
            ),
            _card(
                "quantize задаёт число знаков",
                "У Decimal есть метод `quantize`, который округляет до нужного разряда. "
                "Для цен передают `Decimal('0.01')` — так в результате всегда два знака "
                "после точки. Это удобно для чеков и отчётов, где важна единая форма "
                "записи.",
                "from decimal import Decimal\n"
                "\n"
                "price = Decimal('19.90')\n"
                "total = price * 3\n"
                "print(total)\n"
                "print(total.quantize(Decimal('0.01')))\n"
                "# Вывод:\n"
                "# 59.70\n"
                "# 59.70",
            ),
            _card(
                "Типичная ошибка: считать деньги во float",
                "Float хранит числа в двоичном виде и не может точно представить `0.1`. "
                "Сумма выглядит почти правильно, но в конце появляется хвост. Заметь "
                "ошибку по лишним цифрам в выводе. Для денег бери `Decimal` и создавай "
                "его из строки.",
                "print(0.1 + 0.2)\n# Вывод:\n# 0.30000000000000004",
                "Хвост после 0.3 — признак двоичного представления float.",
            ),
        ],
        [
            _choice(
                "stdlib-core-decimal",
                "Какой код создаст Decimal без потери точности?",
                [
                    "Decimal('0.10')",
                    "Decimal(0.10)",
                    "Decimal(10 / 100)",
                    "Decimal(float('0.10'))",
                ],
                "Decimal('0.10')",
                "Строка разбирается как десятичная запись, а float уже несёт двоичную погрешность.",
            ),
            _term(
                "stdlib-core-decimal",
                "Из какого типа данных создают Decimal для денег?",
                ["str", "строка", "string", "из строки"],
                "Decimal создают из строки: `Decimal('19.90')` сохраняет ровно два знака.",
            ),
            _code(
                "stdlib-core-decimal",
                "Напиши `total_price(prices)`: сложи строковые цены через `Decimal` и "
                "верни строку с двумя знаками после точки. Пустой список даёт `'0.00'`.",
                "from decimal import Decimal\n"
                "\n"
                "\n"
                "def total_price(prices):\n"
                "    # сложи цены и верни строку с двумя знаками\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "total_price(['0.10', '0.20'])",
                        "expected": "0.30",
                    },
                    {"kind": "call", "call": "total_price([])", "expected": "0.00"},
                    {"kind": "call", "call": "total_price(['1'])", "expected": "1.00"},
                ],
                "from decimal import Decimal\n"
                "\n"
                "\n"
                "def total_price(prices):\n"
                "    total = Decimal('0')\n"
                "    for price in prices:\n"
                "        total += Decimal(price)\n"
                "    return str(total.quantize(Decimal('0.01')))\n",
                "Верно: каждая цена разбирается в Decimal, сумма округляется до копеек и "
                "переводится в строку.",
                "Начни с Decimal('0'), прибавляй Decimal(price), затем quantize до 0.01.",
            ),
        ],
    ),
]
