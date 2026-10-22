"""Рукописные уроки 89–96: тестирование, качество кода и Git-цикл."""

from __future__ import annotations

from typing import Any


def _card(title: str, text: str, example: str, tip: str = "", run: bool = True) -> dict[str, Any]:
    card: dict[str, Any] = {"title": title, "text": text, "example": example, "tip": tip}
    if not run:
        card["run"] = False
    return card


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
        "testing-unit-tests",
        "Одна функция — несколько проверок",
        [
            _card(
                "Юнит-тест проверяет маленькую единицу",
                "Юнит-тест — это короткая проверка одной функции или одного правила. "
                "Главный инструмент — `assert`: он проверяет условие и падает с "
                "`AssertionError`, если условие ложно. Если условие истинно, тест идёт "
                "дальше. Один тест должен отвечать на один вопрос: «эта функция делает "
                "то, что обещает?».",
                "def double(x):\n"
                "    return x * 2\n"
                "\n"
                "assert double(3) == 6\n"
                "print('тест прошёл')\n"
                "# Вывод:\n"
                "# тест прошёл",
                "Проверяй результат функции, а не то, как она написана внутри.",
            ),
            _card(
                "Как пользоваться: собери проверки в тестовую функцию",
                "Не пиши проверки вразброс. Собери их в функцию с именем, которое "
                "начинается на `test_`. Внутри поставь несколько `assert`: обычный "
                "случай, границу и противоположный случай. Так один запуск проверяет "
                "сразу несколько сценариев, а имя функции говорит, что именно "
                "проверяется.",
                "def is_even(n):\n"
                "    return n % 2 == 0\n"
                "\n"
                "def test_is_even():\n"
                "    assert is_even(4) is True\n"
                "    assert is_even(7) is False\n"
                "    assert is_even(0) is True\n"
                "\n"
                "test_is_even()\n"
                "print('все проверки прошли')\n"
                "# Вывод:\n"
                "# все проверки прошли",
                "Добавь хотя бы один граничный случай: 0, пустую строку или пустой список.",
            ),
            _card(
                "Типичная ошибка: тест без assert ничего не проверяет",
                "Если просто вызвать функцию и не сравнить результат, тест пройдёт даже "
                "при сломанной логике. В примере `add(2, 2)` выполняется, а печать "
                "сообщает об успехе. Заметить ошибку можно так: спроси, какое условие "
                "должно стать ложным, если код сломается. Если такого условия нет, тест "
                "ничего не доказывает.",
                "def add(a, b):\n"
                "    return a + b\n"
                "\n"
                "add(2, 2)\n"
                "print('тест прошёл')\n"
                "# Вывод:\n"
                "# тест прошёл",
                "В каждом тесте нужна проверка, которая умеет упасть.",
            ),
        ],
        [
            _choice(
                "testing-unit-tests",
                "Что выведет код?\n\n"
                "def square(n):\n"
                "    return n * n\n"
                "\n"
                "assert square(3) == 9\n"
                "assert square(-2) == 4\n"
                "print(square(4))",
                ["16", "25", "36", "49"],
                "16",
                "Функция возвращает квадрат числа, поэтому `square(4)` даёт 16. "
                "Проверки до печати проходят, ошибки нет.",
            ),
            _term(
                "testing-unit-tests",
                "Какое ключевое слово проверяет условие в тесте?",
                ["assert", "оператор assert", "assert.", "ассерт"],
                "`assert` проверяет условие и падает, если оно ложно.",
            ),
            _code(
                "testing-unit-tests",
                "Напиши `is_palindrome(s)`, которая без учёта регистра проверяет, "
                "читается ли строка одинаково в обе стороны, и `test_is_palindrome()` "
                "с минимум тремя `assert`.",
                "def is_palindrome(s):\n    pass\n\n\ndef test_is_palindrome():\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "is_palindrome('Шалаш') is True",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "is_palindrome('кот') is False",
                        "expected": True,
                    },
                    {"kind": "call", "call": "test_is_palindrome()", "expected": None},
                    {"kind": "call", "call": "is_palindrome('') is True", "expected": True},
                ],
                "def is_palindrome(s):\n"
                "    cleaned = s.lower().replace(' ', '')\n"
                "    return cleaned == cleaned[::-1]\n"
                "\n"
                "\n"
                "def test_is_palindrome():\n"
                "    assert is_palindrome('Шалаш') is True\n"
                "    assert is_palindrome('кот') is False\n"
                "    assert is_palindrome('А роза упала на лапу Азора') is True\n",
                "`is_palindrome` приводит строку к нижнему регистру, убирает пробелы и "
                "сравнивает её с перевёрнутой копией. `test_is_palindrome` проверяет "
                "палиндром, не-палиндром и фразу с пробелами.",
                "Для переворота строки используй срез `[::-1]`, а регистр выровняй "
                "через `lower()`.",
            ),
        ],
    ),
    _lesson(
        "testing-fixtures",
        "Готовим данные до проверки",
        [
            _card(
                "Фикстура готовит данные до проверки",
                "Фикстура — это данные и настройка, которые нужны тесту до действия. "
                "Вместо того чтобы собирать словарь заново в каждом тесте, ты вызываешь "
                "маленькую фабрику. Она возвращает готовый объект: пользователя, "
                "корзину, настройки. Так тест занимается проверкой, а не повторяет "
                "подготовку.",
                "def make_user():\n"
                "    return {'name': 'Аня', 'level': 1}\n"
                "\n"
                "user = make_user()\n"
                "user['level'] += 1\n"
                "print(user['level'])\n"
                "# Вывод:\n"
                "# 2",
                "Держи фикстуру маленькой: только те поля, которые нужны тесту.",
            ),
            _card(
                "Как пользоваться: arrange, act, assert",
                "Раздели тест на три шага. Arrange — подготовь данные через фабрику. "
                "Act — выполни одно действие. Assert — проверь результат. В примере "
                "фабрика `make_cart` создаёт пустую корзину, потом ты добавляешь товар и "
                "считаешь сумму. Второй вызов `make_cart()` возвращает новую корзину, "
                "поэтому первый товар туда не попадает.",
                "def make_cart():\n"
                "    return {'items': [], 'total': 0}\n"
                "\n"
                "cart = make_cart()\n"
                "cart['items'].append('хлеб')\n"
                "cart['total'] += 60\n"
                "print(cart)\n"
                "print(make_cart())\n"
                "# Вывод:\n"
                "# {'items': ['хлеб'], 'total': 60}\n"
                "# {'items': [], 'total': 0}",
                "Каждый вызов фабрики должен возвращать свежий объект.",
            ),
            _card(
                "Типичная ошибка: общий список в значении по умолчанию",
                "Если фабрика принимает `items=[]`, этот список создаётся один раз и "
                "остаётся общим для всех вызовов. Второй тест неожиданно видит товар из "
                "первого. Заметить легко: вызови фабрику дважды и измени результат "
                "первого вызова. Если второй результат тоже изменился, данные общие. "
                "Исправление — создавать список внутри функции.",
                "def make_cart(items=[]):\n"
                "    return {'items': items, 'total': 0}\n"
                "\n"
                "first = make_cart()\n"
                "first['items'].append('хлеб')\n"
                "print(make_cart())\n"
                "# Вывод:\n"
                "# {'items': ['хлеб'], 'total': 0}",
                "Сравни два вызова фабрики до и после изменения первого результата.",
            ),
        ],
        [
            _choice(
                "testing-fixtures",
                "Что выведет код?\n\n"
                "def make_cart():\n"
                "    return {'items': [], 'total': 0}\n"
                "\n"
                "first = make_cart()\n"
                "first['items'].append('хлеб')\n"
                "print(len(make_cart()['items']))",
                ["0", "1", "2", "3"],
                "0",
                "Каждый вызов `make_cart` создаёт новый словарь и новый список, поэтому "
                "хлеб остался только в `first`.",
            ),
            _term(
                "testing-fixtures",
                "Как называют подготовленные данные, которые тест использует до действия?",
                ["фикстура", "fixture", "фикстуры", "тестовая фикстура"],
                "Фикстура — это данные и настройка, подготовленные для теста заранее.",
            ),
            _code(
                "testing-fixtures",
                "Напиши фабрику `make_cart()`, которая при каждом вызове возвращает новую "
                "пустую корзину `{'items': [], 'total': 0}`.",
                "def make_cart():\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "make_cart() == {'items': [], 'total': 0}",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "(make_cart() is not make_cart()) is True",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "make_cart()['items'] is not make_cart()['items']",
                        "expected": True,
                    },
                ],
                "def make_cart():\n    return {'items': [], 'total': 0}\n",
                "Фабрика возвращает новый словарь и новый список при каждом вызове, "
                "поэтому тесты не делят данные друг с другом.",
                "Создавай словарь прямо внутри функции, а не выноси его в глобальную переменную.",
            ),
        ],
    ),
    _lesson(
        "testing-parametrize",
        "Один тест для набора примеров",
        [
            _card(
                "Параметризация: один тест, много входов",
                "Параметризация — это когда одно правило проверяется на таблице "
                "примеров. Ты описываешь пары «вход — ожидание» и прогоняешь их в цикле. "
                "Код теста не копируется, а данные меняются. Если один пример сломался, "
                "видно, какой именно вход не прошёл.",
                "def is_even(n):\n"
                "    return n % 2 == 0\n"
                "\n"
                "cases = [(2, True), (3, False), (4, True)]\n"
                "for value, expected in cases:\n"
                "    assert is_even(value) is expected\n"
                "print('3 случая проверены')\n"
                "# Вывод:\n"
                "# 3 случая проверены",
                "Начни с трёх-четырёх пар: обычный вход, граница и неверный случай.",
            ),
            _card(
                "Как пользоваться: собирай все неудачи, а не первую",
                "Иногда удобно не останавливаться на первом `assert`, а собрать список "
                "входов, где результат не совпал с ожиданием. Тогда один запуск "
                "показывает всю картину. В примере `square(3)` вернул 9 вместо 10, "
                "поэтому в списке оказался вход 3. Пустой список означает, что все "
                "примеры прошли.",
                "def square(n):\n"
                "    return n * n\n"
                "\n"
                "cases = [(2, 4), (3, 10), (4, 16)]\n"
                "failed = [value for value, expected in cases if square(value) != expected]\n"
                "print(failed)\n"
                "# Вывод:\n"
                "# [3]",
                "Для отладки возвращай входы, а для финальной проверки — assert на пустой список.",
            ),
            _card(
                "Типичная ошибка: неверное ожидание в таблице",
                "Параметризация показывает не только ошибки кода, но и ошибки данных. В "
                "примере для входа 3 ожидается 5, хотя `double(3)` возвращает 6. Тест "
                "падает, хотя функция работает верно. Заметить это можно по списку "
                "неудач: проверь ожидание для каждого входа вручную. Исправляй таблицу, "
                "а не функцию.",
                "def double(n):\n"
                "    return n * 2\n"
                "\n"
                "cases = [(2, 4), (3, 5)]\n"
                "failed = [value for value, expected in cases if double(value) != expected]\n"
                "print(failed)\n"
                "# Вывод:\n"
                "# [3]",
                "Сначала пересчитай ожидаемый результат на бумаге или в отдельной ячейке.",
            ),
        ],
        [
            _choice(
                "testing-parametrize",
                "Что выведет код?\n\n"
                "def triple(n):\n"
                "    return n * 3\n"
                "\n"
                "cases = [(1, 3), (2, 5), (3, 9)]\n"
                "failed = [value for value, expected in cases if triple(value) != expected]\n"
                "print(failed)",
                ["[2]", "[1]", "[3]", "[]"],
                "[2]",
                "Для входа 2 ожидание 5, но `triple(2)` возвращает 6, поэтому в списке "
                "неудач оказался только вход 2.",
            ),
            _term(
                "testing-parametrize",
                "Как называют описание одного теста сразу для набора входов?",
                ["параметризация", "параметризованный тест", "parametrize", "параметризация теста"],
                "Параметризация прогоняет один и тот же тест на нескольких наборах данных.",
            ),
            _code(
                "testing-parametrize",
                "Напиши `failed_cases(func, cases)`: `cases` — пары «вход, ожидание», а "
                "функция возвращает список входов, на которых `func(вход)` не равен "
                "ожидаемому значению.",
                "def failed_cases(func, cases):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "failed_cases(abs, [(-1, 1), (2, 2), (3, -3)]) == [3]",
                        "expected": True,
                    },
                    {"kind": "call", "call": "failed_cases(abs, []) == []", "expected": True},
                    {
                        "kind": "call",
                        "call": "failed_cases(abs, [(0, 1)]) == [0]",
                        "expected": True,
                    },
                ],
                "def failed_cases(func, cases):\n"
                "    return [value for value, expected in cases if func(value) != expected]\n",
                "Функция сравнивает результат с ожиданием для каждой пары и собирает "
                "только те входы, где значения разошлись.",
                "Распакуй пару в цикле: `for value, expected in cases`.",
            ),
        ],
    ),
    _lesson(
        "testing-mocks",
        "Изолируем внешние зависимости",
        [
            _card(
                "Тестовый двойник заменяет внешний сервис",
                "Двойник — это подставной объект, который ведёт себя как настоящая "
                "зависимость, но не ходит в сеть и не ждёт ответа. В тесте ты передаёшь "
                "двойник вместо реальной отправки сообщения. Так проверка становится "
                "быстрой и предсказуемой, а настоящий сервис не нужен.",
                "def send(text):\n"
                "    print('настоящая отправка:', text)\n"
                "\n"
                "def welcome(name, send):\n"
                "    send(f'Привет, {name}!')\n"
                "\n"
                "welcome('Аня', send)\n"
                "# Вывод:\n"
                "# настоящая отправка: Привет, Аня!",
                "Двойник полезен там, где настоящая зависимость медленная или нестабильная.",
            ),
            _card(
                "Как пользоваться: фейк-список записывает вызовы",
                "Самый простой двойник — функция, которая складывает аргументы в "
                "список. Ты передаёшь `log.append` вместо отправки. После вызова "
                "проверяешь, что в списке ровно одно сообщение и текст совпадает. Так "
                "тест видит, что функция действительно позвала зависимость с нужными "
                "данными.",
                "def welcome(name, send):\n"
                "    send(f'Привет, {name}!')\n"
                "    return True\n"
                "\n"
                "log = []\n"
                "welcome('Аня', log.append)\n"
                "print(log)\n"
                "# Вывод:\n"
                "# ['Привет, Аня!']",
                "Проверяй и сам факт вызова, и переданный текст.",
            ),
            _card(
                "Типичная ошибка: сверять не тот текст сообщения",
                "Двойник записывает точный текст, поэтому забытое имя сразу видно. В "
                "примере ожидание `['Привет!']` не совпадает с настоящим сообщением "
                "`['Привет, Аня!']`, и сравнение даёт `False`. Заметить ошибку можно, "
                "если напечатать список вызовов и сверить его с требованием. Не подгоняй "
                "двойник под неверное ожидание.",
                "def welcome(name, send):\n"
                "    send(f'Привет, {name}!')\n"
                "    return True\n"
                "\n"
                "log = []\n"
                "welcome('Аня', log.append)\n"
                "print(log == ['Привет!'])\n"
                "# Вывод:\n"
                "# False",
                "Сначала посмотри, что именно записал двойник, потом пиши ожидание.",
            ),
        ],
        [
            _choice(
                "testing-mocks",
                "Что выведет код?\n\n"
                "def welcome(name, send):\n"
                "    send(f'Привет, {name}!')\n"
                "    return True\n"
                "\n"
                "log = []\n"
                "welcome('Ира', log.append)\n"
                "print(log)",
                ["['Привет, Ира!']", "['Привет!']", "['Привет, Аня!']", "['Привет, Ира']"],
                "['Привет, Ира!']",
                "Фейк-список записал ровно тот текст, который передала функция: `Привет, Ира!`.",
            ),
            _term(
                "testing-mocks",
                "Как называют подставной объект, который заменяет зависимость в тесте?",
                ["двойник", "тестовый двойник", "mock", "мок", "фейк", "fake"],
                "Тестовый двойник ведёт себя как зависимость, но не выполняет настоящую работу.",
            ),
            _code(
                "testing-mocks",
                "Напиши `welcome(name, send)`: она вызывает `send` с текстом "
                "`Привет, <name>!` и возвращает `True`.",
                "def welcome(name, send):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "(lambda log: (welcome('Аня', log.append), log)[1])([])"
                        " == ['Привет, Аня!']",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "welcome('Аня', lambda text: None) is True",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "(lambda log: (welcome('', log.append), log)[1])([])"
                        " == ['Привет, !']",
                        "expected": True,
                    },
                ],
                "def welcome(name, send):\n    send(f'Привет, {name}!')\n    return True\n",
                "Функция не печатает сама, а передаёт готовый текст в `send`. Двойник в "
                "тесте записывает этот текст в список.",
                "Собери сообщение через f-строку и не забудь вернуть `True`.",
            ),
        ],
    ),
    _lesson(
        "quality-pep8",
        "PEP 8 и читаемость",
        [
            _card(
                "Стиль кода помогает читать, а не украшает",
                "PEP 8 — это договорённости о том, как писать код, чтобы его одинаково "
                "понимала команда. Пробелы вокруг операторов, понятные имена и короткие "
                "строки снижают нагрузку на глаза. Код с хорошим стилем легче проверять "
                "и исправлять. Смысл программы от стиля не меняется.",
                "def average_speed(distance_km, hours):\n"
                "    return round(distance_km / hours, 1)\n"
                "\n"
                "print(average_speed(120, 1.5))\n"
                "# Вывод:\n"
                "# 80.0",
                "Сначала запусти автоформаттер, а спорные случаи обсуждай с командой.",
            ),
            _card(
                "Как пользоваться: имя объясняет смысл",
                "Имена `distance_km` и `hours` говорят, что подавать в функцию. Внутри "
                "видно формулу, а `round(..., 1)` задаёт точность. Такую функцию можно "
                "прочитать без комментария. Сравни с именами `d` и `h`: они работают, но "
                "заставляют угадывать смысл. Выбирай имена по смыслу, даже если строка "
                "становится чуть длиннее.",
                "def total_price(price, quantity):\n"
                "    discount = 0.1 if quantity >= 10 else 0\n"
                "    return round(price * quantity * (1 - discount), 2)\n"
                "\n"
                "print(total_price(250, 10))\n"
                "# Вывод:\n"
                "# 2250.0",
                "Имя должно отвечать на вопрос «что здесь лежит?», а не быть самым коротким.",
            ),
            _card(
                "Типичная ошибка: короткие имена и слипшиеся операторы",
                "Код `f(d,h)` работает, но читателю приходится расшифровывать каждую "
                "букву. Ошибка стиля не ломает программу, поэтому её легко не заметить. "
                "Проверь себя: сможет ли коллега понять функцию за пять секунд без "
                "запуска? Если нет, переименуй параметры и расставь пробелы. Линтер тоже "
                "подскажет проблемные места.",
                "def f(d,h):\n    return round(d/h,1)\n\nprint(f(120,1.5))\n# Вывод:\n# 80.0",
                "Прочитай функцию вслух: если приходится объяснять имена, переименуй их.",
            ),
        ],
        [
            _choice(
                "quality-pep8",
                "Что выведет код?\n\n"
                "def average_speed(distance_km, hours):\n"
                "    return round(distance_km / hours, 1)\n"
                "\n"
                "print(average_speed(120, 1.5))",
                ["80.0", "40.0", "120.0", "72.0"],
                "80.0",
                "120 километров за 1,5 часа дают 80 километров в час. `round` с одним "
                "знаком после запятой оставляет `80.0`.",
            ),
            _term(
                "quality-pep8",
                "Как называется свод правил оформления кода на Python?",
                ["PEP 8", "PEP8", "pep 8", "pep8"],
                "PEP 8 описывает отступы, имена, пробелы и другие договорённости о стиле.",
            ),
            _code(
                "quality-pep8",
                "В starter есть работающая, но нечитаемая функция. Перепиши её как "
                "`average_speed(distance_km, hours)`: понятные имена, пробелы вокруг "
                "операторов и результат `round(distance_km / hours, 1)`.",
                "def average_speed(distance_km, hours):\n"
                "    d=distance_km;h=hours\n"
                "    if h:\n"
                "        return round(d/h)\n"
                "    else:\n"
                "        pass\n",
                [
                    {
                        "kind": "call",
                        "call": "average_speed(120, 1.5) == 80.0",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "average_speed(10, 4) == 2.5",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "average_speed(0, 2) == 0.0",
                        "expected": True,
                    },
                ],
                "def average_speed(distance_km, hours):\n"
                "    return round(distance_km / hours, 1)\n",
                "Понятные имена и один знак после запятой делают функцию короткой и предсказуемой.",
                "Замени `d` и `h` на имена параметров и передай в `round` второй аргумент `1`.",
            ),
        ],
    ),
    _lesson(
        "quality-format-lint",
        "ruff format и ruff check",
        [
            _card(
                "Форматтер и линтер решают разные задачи",
                "Форматтер приводит внешний вид к единому шаблону: отступы, пробелы, "
                "кавычки. Линтер ищет подозрительные места в логике: неиспользуемые "
                "имена, забытые импорты, опасные сравнения. `ruff format` не заменяет "
                "`ruff check`. Запускай обе команды: одна выравнивает код, другая ищет "
                "возможные ошибки.",
                "import subprocess\n"
                "import tempfile\n"
                "from pathlib import Path\n"
                "\n"
                "with tempfile.TemporaryDirectory() as folder:\n"
                "    sample = Path(folder) / 'sample.py'\n"
                "    sample.write_text('x=1\\n', encoding='utf-8')\n"
                "    subprocess.run(['ruff', 'format', sample], capture_output=True, check=True)\n"
                "    print(sample.read_text(encoding='utf-8').strip())\n"
                "    result = subprocess.run(['ruff', 'check', sample], capture_output=True)\n"
                "    print(result.returncode)\n"
                "# Вывод:\n"
                "# x = 1\n"
                "# 0",
                "Форматтер не ищет логические ошибки, а линтер не переставляет пробелы.",
                run=False,
            ),
            _card(
                "Как пользоваться: проверка до коммита",
                "Удобный цикл такой: сначала форматтер, потом линтер, потом тесты. Если "
                "форматтер что-то изменил, просмотри diff. Если линтер нашёл имя, "
                "исправь причину, а не отключай правило. В примере обе команды "
                "запускаются в режиме проверки и возвращают код 0, когда замечаний нет.",
                "import subprocess\n"
                "import tempfile\n"
                "from pathlib import Path\n"
                "\n"
                "with tempfile.TemporaryDirectory() as folder:\n"
                "    sample = Path(folder) / 'sample.py'\n"
                "    sample.write_text('x = 1\\n', encoding='utf-8')\n"
                "    fmt = subprocess.run(['ruff', 'format', '--check', sample], capture_output=True)\n"
                "    lint = subprocess.run(['ruff', 'check', sample], capture_output=True)\n"
                "    print(fmt.returncode, lint.returncode)\n"
                "# Вывод:\n"
                "# 0 0",
                "Проверяй код теми же командами, что и CI, чтобы не спорить о стиле вручную.",
                run=False,
            ),
            _card(
                "Типичная ошибка: ждать от форматтера работы линтера",
                "После `ruff format` код выглядит аккуратно, но неиспользуемый импорт "
                "остаётся. Если на этом остановиться, `ruff check` упадёт в CI. Заметить "
                "ошибку просто: запусти обе команды по отдельности. Форматтер отвечает "
                "за вид, линтер — за подозрительные конструкции. Не путай их "
                "результаты.",
                "import subprocess\n"
                "import tempfile\n"
                "from pathlib import Path\n"
                "\n"
                "with tempfile.TemporaryDirectory() as folder:\n"
                "    sample = Path(folder) / 'sample.py'\n"
                "    sample.write_text('import os\\n\\nx=1\\n', encoding='utf-8')\n"
                "    subprocess.run(['ruff', 'format', sample], capture_output=True, check=True)\n"
                "    print(sample.read_text(encoding='utf-8').strip())\n"
                "    check = subprocess.run(['ruff', 'check', sample], capture_output=True)\n"
                "    print(check.returncode)\n"
                "# Вывод:\n"
                "# import os\n"
                "#\n"
                "# x = 1\n"
                "# 1",
                "После форматтера всегда запускай линтер и тесты.",
                run=False,
            ),
        ],
        [
            _choice(
                "quality-format-lint",
                "Что выведет код?\n\n"
                "defined = ['total', 'temp']\n"
                "used = ['total']\n"
                "print(sorted(set(defined) - set(used)))",
                ["['temp']", "['total']", "['used']", "['defined']"],
                "['temp']",
                "Разность множеств оставляет имя `temp`: оно определено, но не "
                "используется. `sorted` возвращает его списком.",
            ),
            _term(
                "quality-format-lint",
                "Как называют инструмент, который ищет в коде подозрительные конструкции?",
                ["линтер", "linter", "статический анализатор", "ruff check"],
                "Линтер анализирует код и предупреждает о подозрительных местах, не меняя его.",
            ),
            _code(
                "quality-format-lint",
                "Напиши `unused_names(defined, used)`: она возвращает отсортированный "
                "список имён, которые определены, но не используются.",
                "def unused_names(defined, used):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "unused_names(['a', 'b', 'c'], ['a']) == ['b', 'c']",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "unused_names(['b', 'a'], []) == ['a', 'b']",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "unused_names([], ['a']) == []",
                        "expected": True,
                    },
                ],
                "def unused_names(defined, used):\n    return sorted(set(defined) - set(used))\n",
                "Множества убирают повторы и позволяют найти разность, а `sorted` "
                "возвращает предсказуемый порядок.",
                "Преврати оба списка в множества и вычти использованные имена из определённых.",
            ),
        ],
    ),
    _lesson(
        "quality-docstrings",
        "Docstring, типы и понятные имена",
        [
            _card(
                "Докстринга объясняет контракт функции",
                "Докстринга — это строка сразу после `def`, взятая в тройные кавычки. "
                "Она отвечает, что функция делает, что принимает и что возвращает. В "
                "отличие от комментария, докстринга хранится вместе с функцией и "
                "доступна инструментам. Хорошая докстринга помогает понять код до "
                "запуска.",
                "def celsius_to_f(c):\n"
                '    """Перевести градусы Цельсия в Фаренгейт."""\n'
                "    return c * 9 / 5 + 32\n"
                "\n"
                "print(celsius_to_f(0))\n"
                "# Вывод:\n"
                "# 32.0",
                "Пиши в докстринге смысл и ограничения, а не пересказ каждой строки.",
            ),
            _card(
                "Как пользоваться: покажи пример вызова",
                "Короткий пример в докстринге делает контракт проверяемым. Напиши "
                "вызов и ожидаемый результат: `word_count('привет мир') -> 2`. Если "
                "функцию потом изменят, пример напомнит, что должно остаться верным. В "
                "примере докстринга занимает несколько строк, а результат считается "
                "по-настоящему.",
                "def word_count(text):\n"
                '    """Посчитать слова в строке.\n'
                "\n"
                "    Пример: word_count('привет мир') -> 2\n"
                '    """\n'
                "    return len(text.split())\n"
                "\n"
                "print(word_count('привет мир'))\n"
                "# Вывод:\n"
                "# 2",
                "Один короткий пример полезнее длинного описания.",
            ),
            _card(
                "Типичная ошибка: докстринга врёт о результате",
                "Устаревшая докстринга хуже отсутствующей: она уверенно говорит "
                "неправду. В примере написано, что слов будет 3, а функция возвращает 2. "
                "Заметить это можно, если запустить пример из докстринги. Держи "
                "документацию рядом с кодом и обновляй её в том же изменении.",
                "def word_count(text):\n"
                '    """Посчитать слова. Пример: word_count(\'привет мир\') -> 3."""\n'
                "    return len(text.split())\n"
                "\n"
                "print(word_count('привет мир'))\n"
                "# Вывод:\n"
                "# 2",
                "Запускай примеры из докстринг или проверяй их тестами.",
            ),
        ],
        [
            _choice(
                "quality-docstrings",
                "Что выведет код?\n\n"
                "def double(n):\n"
                '    """Вернуть удвоенное число."""\n'
                "    return n * 2\n"
                "\n"
                "print(double(4))",
                ["8", "4", "2", "0"],
                "8",
                "Докстринга ничего не печатает и не меняет результат: функция удваивает "
                "4 и возвращает 8.",
            ),
            _term(
                "quality-docstrings",
                "Как называют строку документации сразу после `def`?",
                ["докстринга", "docstring", "докстринг", "строка документации"],
                "Докстринга — это строковый литерал в начале функции, описывающий её контракт.",
            ),
            _code(
                "quality-docstrings",
                "Напиши `celsius_to_f(c)`, которая переводит градусы Цельсия в "
                "Фаренгейт. Добавь докстрингу в тройных кавычках с примером вызова.",
                "def celsius_to_f(c):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "celsius_to_f(100) == 212.0",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "celsius_to_f(0) == 32.0",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "celsius_to_f(-40) == -40.0",
                        "expected": True,
                    },
                ],
                "def celsius_to_f(c):\n"
                '    """Перевести градусы Цельсия в Фаренгейт.\n'
                "\n"
                "    Пример: celsius_to_f(100) -> 212.0\n"
                '    """\n'
                "    return c * 9 / 5 + 32\n",
                "Докстринга объясняет назначение функции и показывает пример вызова. "
                "Формула перевода: градусы Цельсия умножить на 9/5 и прибавить 32.",
                "Не забудь тройные кавычки сразу после `def` и строку с примером "
                "`celsius_to_f(100)`.",
            ),
        ],
    ),
    _lesson(
        "quality-git",
        "Статус, маленькие коммиты и история",
        [
            _card(
                "Git сохраняет историю маленькими шагами",
                "Git записывает изменения в коммиты: `git add` готовит файлы, `git "
                "commit` сохраняет шаг, а `git log` показывает историю. Маленький "
                "коммит легче понять, проверить и откатить. История становится рассказом "
                "о том, как развивался проект.",
                "import subprocess\n"
                "import tempfile\n"
                "from pathlib import Path\n"
                "\n"
                "with tempfile.TemporaryDirectory() as folder:\n"
                "    def git(*args):\n"
                "        return subprocess.run(\n"
                "            ['git', *args], cwd=folder, capture_output=True, text=True, check=True\n"
                "        )\n"
                "\n"
                "    git('init', '--quiet')\n"
                "    git('config', 'user.email', 'test@example.com')\n"
                "    git('config', 'user.name', 'Тест')\n"
                "    Path(folder, 'hello.py').write_text('print(1)\\n', encoding='utf-8')\n"
                "    git('add', 'hello.py')\n"
                "    git('commit', '--quiet', '-m', 'Добавить приветствие')\n"
                "    print(git('log', '--format=%s').stdout.strip())\n"
                "# Вывод:\n"
                "# Добавить приветствие",
                "Один коммит — одна законченная мысль.",
                run=False,
            ),
            _card(
                "Как пользоваться: цикл status → add → commit",
                "Начни со `git status --short`: так видно изменённые файлы. Добавь "
                "только то, что относится к шагу. Затем сделай коммит с коротким "
                "сообщением в повелительном наклонении: «Добавить поиск». Первая строка "
                "не должна быть пустой, длиннее 50 символов или заканчиваться точкой. "
                "Проверить сообщение можно до коммита.",
                "import subprocess\n"
                "import tempfile\n"
                "from pathlib import Path\n"
                "\n"
                "with tempfile.TemporaryDirectory() as folder:\n"
                "    def git(*args):\n"
                "        return subprocess.run(\n"
                "            ['git', *args], cwd=folder, capture_output=True, text=True, check=True\n"
                "        )\n"
                "\n"
                "    git('init', '--quiet')\n"
                "    git('config', 'user.email', 'test@example.com')\n"
                "    git('config', 'user.name', 'Тест')\n"
                "    Path(folder, 'service.py').write_text('limit = 10\\n', encoding='utf-8')\n"
                "    print(git('status', '--short').stdout.strip())\n"
                "    git('add', 'service.py')\n"
                "    print(git('status', '--short').stdout.strip())\n"
                "    git('commit', '--quiet', '-m', 'Добавить лимит')\n"
                "    print(git('log', '--format=%s').stdout.strip())\n"
                "# Вывод:\n"
                "# ?? service.py\n"
                "# A  service.py\n"
                "# Добавить лимит",
                "Сообщение коммита отвечает на вопрос «что сделать?», а не «что я делал».",
                run=False,
            ),
            _card(
                "Типичная ошибка: расплывчатый коммит с точкой",
                "Сообщение «Исправил баг.» не говорит, что именно исправлено, и "
                "заканчивается точкой. В истории такой коммит трудно найти. Заметить "
                "ошибку можно через `git log --format=%s`: если по строке нельзя "
                "понять изменение, сообщение плохое. Пиши конкретное действие без точки в "
                "конце, например «Исправить расчёт скидки».",
                "import subprocess\n"
                "import tempfile\n"
                "\n"
                "with tempfile.TemporaryDirectory() as folder:\n"
                "    def git(*args):\n"
                "        return subprocess.run(\n"
                "            ['git', *args], cwd=folder, capture_output=True, text=True, check=True\n"
                "        )\n"
                "\n"
                "    git('init', '--quiet')\n"
                "    git('config', 'user.email', 'test@example.com')\n"
                "    git('config', 'user.name', 'Тест')\n"
                "    git('commit', '--quiet', '--allow-empty', '-m', 'Исправил баг.')\n"
                "    git('commit', '--quiet', '--allow-empty', '-m', 'Исправить расчёт скидки')\n"
                "    print(git('log', '--format=%s').stdout.strip())\n"
                "# Вывод:\n"
                "# Исправить расчёт скидки\n"
                "# Исправил баг.",
                "Проверь сообщение по трём правилам: не пусто, до 50 символов, без точки.",
                run=False,
            ),
        ],
        [
            _choice(
                "quality-git",
                "Что выведет код?\n\n"
                "message = 'Добавить поиск'\n"
                "print(len(message.splitlines()[0]))",
                ["14", "13", "15", "50"],
                "14",
                "В строке «Добавить поиск» 14 символов: восемь букв, пробел и пять букв. "
                "Первая строка здесь совпадает со всей строкой.",
            ),
            _term(
                "quality-git",
                "Какая команда Git показывает изменённые файлы перед коммитом?",
                ["git status", "git status --short", "status", "git status -s"],
                "`git status` показывает состояние рабочей папки и индекса.",
            ),
            _code(
                "quality-git",
                "Напиши `commit_message_ok(msg)`: она проверяет первую строку сообщения "
                "коммита. Строка должна быть непустой, не длиннее 50 символов и не "
                "заканчиваться точкой.",
                "def commit_message_ok(msg):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "commit_message_ok('Добавить поиск') is True",
                        "expected": True,
                    },
                    {"kind": "call", "call": "commit_message_ok('') is False", "expected": True},
                    {
                        "kind": "call",
                        "call": "commit_message_ok('Фикс.') is False",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "commit_message_ok('а' * 50) is True",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "commit_message_ok('а' * 51) is False",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "commit_message_ok('\\nВторая строка') is False",
                        "expected": True,
                    },
                ],
                "def commit_message_ok(msg):\n"
                "    lines = msg.splitlines()\n"
                "    first_line = lines[0] if lines else ''\n"
                "    return bool(first_line) and len(first_line) <= 50 and not first_line.endswith('.')\n",
                "Функция берёт первую строку, проверяет её длину и последний символ. "
                "Пустое сообщение тоже отклоняется.",
                "Сначала получи первую строку через `splitlines()`, затем проверь её "
                "длину и точку в конце.",
            ),
        ],
    ),
]
