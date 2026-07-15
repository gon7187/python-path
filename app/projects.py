"""Небольшие практические проекты с постепенным усложнением."""

from __future__ import annotations

from typing import Any

from app.learning_design import public_tool_help, tool_reference_cards

PROJECTS: list[dict[str, Any]] = [
    {
        "id": "greeting-card",
        "order": 1,
        "title": "Именная открытка",
        "subtitle": "Первый инструмент: программа спрашивает имя и здоровается.",
        "icon": "👋",
        "level": "Старт",
        "requires_lesson_ids": ["warmup-input"],
        "xp": 25,
        "description": "Собери короткую программу с input(), переменной и f-строкой.",
        "skills": ["input()", "переменные", "f-строки"],
        "tool_ids": ["input", "f-string", "print"],
        "checklist": [
            "Запросить имя с понятной подсказкой.",
            "Сохранить ответ в переменную name.",
            "Вывести приветствие с этим именем.",
        ],
        "starter": "name = input('Имя: ')\n# напиши приветствие\n",
        "test_inputs": ["Лена"],
        "input_example": ["Лена"],
        "tests": [{"kind": "stdout", "expected": "Привет, Лена!", "comparison": "contains"}],
        "scenarios": [
            {
                "name": "имя из примера",
                "inputs": ["Лена"],
                "tests": [
                    {"kind": "stdout", "expected": "Привет, Лена!", "comparison": "contains"}
                ],
            },
            {
                "name": "другое имя",
                "inputs": ["Макс"],
                "tests": [
                    {"kind": "stdout", "expected": "Привет, Макс!", "comparison": "contains"}
                ],
            },
        ],
        "hints": [
            "input(...) возвращает текст — его можно сразу сохранить в name.",
            "Для подстановки имени используй print(f'Привет, {name}!').",
        ],
        "success": "Открытка готова: программа получила данные и показала персональный ответ.",
    },
    {
        "id": "purchase-calculator",
        "order": 2,
        "title": "Калькулятор покупки",
        "subtitle": "Считаем стоимость нескольких одинаковых товаров.",
        "icon": "🧮",
        "level": "База",
        "requires_lesson_ids": ["warmup-convert"],
        "xp": 35,
        "description": "Преврати текстовый ввод в числа, умножь цену на количество и покажи итог.",
        "skills": ["int()", "умножение", "f-строки"],
        "tool_ids": ["input", "int", "multiply", "f-string", "print"],
        "checklist": [
            "Получить цену и количество через input().",
            "Преобразовать оба ответа через int().",
            "Напечатать итог в формате «Итого: число».",
        ],
        "starter": "price = int(input('Цена: '))\ncount = int(input('Количество: '))\n# выведи итог\n",
        "test_inputs": ["120", "3"],
        "input_example": ["120", "3"],
        "tests": [{"kind": "stdout", "expected": "Итого: 360", "comparison": "contains"}],
        "scenarios": [
            {
                "name": "три товара",
                "inputs": ["120", "3"],
                "tests": [{"kind": "stdout", "expected": "Итого: 360", "comparison": "contains"}],
            },
            {
                "name": "другая цена и количество",
                "inputs": ["75", "2"],
                "tests": [{"kind": "stdout", "expected": "Итого: 150", "comparison": "contains"}],
            },
        ],
        "hints": [
            "После int(...) price и count уже числа: их можно умножать.",
            "Сначала вычисли price * count, затем подставь результат в f-строку.",
        ],
        "success": "Калькулятор посчитал итог и понятно показал его пользователю.",
    },
    {
        "id": "access-checker",
        "order": 3,
        "title": "Проверка доступа",
        "subtitle": "Принимаем решение через if и else.",
        "icon": "🔐",
        "level": "Логика",
        "requires_lesson_ids": ["conditions-else"],
        "xp": 45,
        "description": "Сделай мини-проверку пароля: правильный открывает доступ, любой другой — нет.",
        "skills": ["условия", "==", "ветка else"],
        "tool_ids": ["if", "else", "comparison", "print"],
        "checklist": [
            "Запросить пароль в переменную password.",
            "Сравнить его со строкой python.",
            "Показать один из двух понятных ответов.",
        ],
        "starter": "password = input('Пароль: ')\n# добавь if и else\n",
        "test_inputs": ["python"],
        "input_example": ["python"],
        "tests": [{"kind": "stdout", "expected": "Доступ открыт", "comparison": "contains"}],
        "scenarios": [
            {
                "name": "верный пароль",
                "inputs": ["python"],
                "tests": [
                    {"kind": "stdout", "expected": "Доступ открыт", "comparison": "contains"}
                ],
            },
            {
                "name": "неверный пароль",
                "inputs": ["secret"],
                "tests": [
                    {"kind": "stdout", "expected": "Доступ закрыт", "comparison": "contains"}
                ],
            },
        ],
        "hints": [
            "Сравнение пишется двумя знаками: password == 'python'.",
            "После if и else поставь двоеточие и не забудь отступ в четыре пробела.",
        ],
        "success": "Проверка доступа работает: условие выбирает нужный сценарий.",
    },
    {
        "id": "word-counter",
        "order": 4,
        "title": "Счётчик слов",
        "subtitle": "Разбираем текст и получаем полезную цифру.",
        "icon": "📝",
        "level": "Строки",
        "requires_lesson_ids": ["strings-split"],
        "xp": 55,
        "description": "Программа получает фразу, делит её на слова и сообщает количество слов.",
        "skills": ["split()", "списки", "len()"],
        "tool_ids": ["split", "len", "f-string", "print"],
        "checklist": [
            "Получить фразу в переменную text.",
            "Разделить строку через text.split().",
            "Вывести количество слов с понятной подписью.",
        ],
        "starter": "text = input('Фраза: ')\nwords = text.split()\n# выведи количество слов\n",
        "test_inputs": ["учу Python каждый день"],
        "input_example": ["учу Python каждый день"],
        "tests": [
            {
                "kind": "stdout",
                "expected": "Слов: 4",
                "comparison": "contains",
            }
        ],
        "scenarios": [
            {
                "name": "фраза из примера",
                "inputs": ["учу Python каждый день"],
                "tests": [
                    {
                        "kind": "stdout",
                        "expected": "Слов: 4",
                        "comparison": "contains",
                    }
                ],
            },
            {
                "name": "короткая фраза",
                "inputs": ["два слова"],
                "tests": [
                    {
                        "kind": "stdout",
                        "expected": "Слов: 2",
                        "comparison": "contains",
                    }
                ],
            },
        ],
        "hints": [
            "words — это список слов, поэтому len(words) даст нужное число.",
            "Результат удобно показать так: print(f'Слов: {len(words)}').",
        ],
        "success": "Счётчик превратил живой текст в полезный результат.",
    },
    {
        "id": "score-summary",
        "order": 5,
        "title": "Сводка оценок",
        "subtitle": "Считаем сумму и среднее по списку.",
        "icon": "📊",
        "level": "Коллекции",
        "requires_lesson_ids": ["functions-return", "lists-sum"],
        "xp": 65,
        "description": "Собери функцию отчёта: она принимает список и возвращает среднее значение.",
        "skills": ["функции", "списки", "sum()", "len()"],
        "tool_ids": ["sum", "len", "division", "return"],
        "checklist": [
            "Оставить имя функции average_score и параметр scores.",
            "Посчитать сумму через sum и количество через len.",
            "Вернуть среднее значение через return.",
        ],
        "starter": "def average_score(scores):\n    total = sum(scores)\n    # верни среднее значение\n    return 0\n",
        "test_inputs": [],
        "input_example": [],
        "tests": [
            {"kind": "call", "call": "average_score([5, 4, 5, 3])", "expected": 4.25},
            {"kind": "call", "call": "average_score([2, 4])", "expected": 3.0},
        ],
        "scenarios": [
            {
                "name": "четыре оценки",
                "inputs": [],
                "tests": [
                    {
                        "kind": "call",
                        "call": "average_score([5, 4, 5, 3])",
                        "expected": 4.25,
                    }
                ],
            },
            {
                "name": "две другие оценки",
                "inputs": [],
                "tests": [{"kind": "call", "call": "average_score([2, 4])", "expected": 3.0}],
            },
        ],
        "hints": [
            "total уже готов. Подумай, на какое количество элементов его разделить.",
            "Функция должна вернуть вычисление, а не печатать один заранее известный ответ.",
        ],
        "success": "Сводка готова: список превратился в понятную метрику.",
    },
    {
        "id": "contact-card",
        "order": 6,
        "title": "Карточка контакта",
        "subtitle": "Собираем и красиво показываем данные из словаря.",
        "icon": "📇",
        "level": "Данные",
        "requires_lesson_ids": ["functions-return", "dicts-sets"],
        "xp": 75,
        "description": "Напиши функцию, которая собирает аккуратную карточку из любого словаря контакта.",
        "skills": ["функции", "словари", "ключи", "f-строки"],
        "tool_ids": ["dict", "index", "f-string", "return"],
        "checklist": [
            "Оставить функцию format_contact(contact).",
            "Достать name и city по ключам.",
            "Вернуть одну строку с именем и городом.",
        ],
        "starter": "def format_contact(contact):\n    # верни: имя — город\n    return ''\n",
        "test_inputs": [],
        "input_example": [],
        "tests": [
            {
                "kind": "call",
                "call": "format_contact({'name': 'Мира', 'city': 'Казань'})",
                "expected": "Мира — Казань",
            },
            {
                "kind": "call",
                "call": "format_contact({'name': 'Лев', 'city': 'Тула'})",
                "expected": "Лев — Тула",
            },
        ],
        "scenarios": [
            {
                "name": "контакт из Казани",
                "inputs": [],
                "tests": [
                    {
                        "kind": "call",
                        "call": "format_contact({'name': 'Мира', 'city': 'Казань'})",
                        "expected": "Мира — Казань",
                    }
                ],
            },
            {
                "name": "контакт из Тулы",
                "inputs": [],
                "tests": [
                    {
                        "kind": "call",
                        "call": "format_contact({'name': 'Лев', 'city': 'Тула'})",
                        "expected": "Лев — Тула",
                    }
                ],
            },
        ],
        "hints": [
            "Сначала отдельно прочитай значения contact['name'] и contact['city'].",
            "Соедини оба значения одной f-строкой и верни её через return.",
        ],
        "success": "Карточка контакта готова: данные из словаря стали понятным интерфейсом.",
    },
]

PROJECTS.extend(
    [
        {
            "id": "notes-json-vault",
            "order": 7,
            "title": "Хранилище заметок",
            "subtitle": "Записываем структуру в JSON и читаем её обратно.",
            "icon": "🗃️",
            "level": "Файлы и JSON",
            "requires_lesson_ids": ["files-data-json"],
            "xp": 90,
            "description": (
                "Заверши функцию, которая сохраняет список заметок в учебный файл и "
                "возвращает восстановленные данные."
            ),
            "skills": ["with open()", "json.dump()", "json.load()", "return"],
            "tool_ids": ["import", "with-open", "json-dump", "json-load", "return"],
            "checklist": [
                "Оставить запись notes в notes.json через json.dump().",
                "Открыть тот же файл для чтения в отдельном блоке with.",
                "Вернуть результат json.load(file), а не имя файла или исходный список.",
            ],
            "starter": (
                "import json\n\n"
                "def save_notes(notes):\n"
                "    with open('notes.json', 'w', encoding='utf-8') as file:\n"
                "        json.dump(notes, file, ensure_ascii=False)\n"
                "    with open('notes.json', encoding='utf-8') as file:\n"
                "        # прочитай JSON из file и верни данные\n"
                "        return []\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {
                    "kind": "call",
                    "call": "save_notes([{'title': 'Идея', 'done': False}])",
                    "expected": [{"title": "Идея", "done": False}],
                },
                {"kind": "call", "call": "save_notes([])", "expected": []},
            ],
            "scenarios": [
                {
                    "name": "одна заметка",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "save_notes([{'title': 'Идея', 'done': False}])",
                            "expected": [{"title": "Идея", "done": False}],
                        }
                    ],
                },
                {
                    "name": "пустое хранилище",
                    "inputs": [],
                    "tests": [{"kind": "call", "call": "save_notes([])", "expected": []}],
                },
            ],
            "hints": [
                "json.dump(data, file) записывает Python-структуру в открытый файл.",
                "json.load(file) читает JSON из файла и возвращает список или словарь Python.",
                "Во втором блоке with замени только return [] на возврат результата json.load(file).",
            ],
            "success": "Заметки прошли полный путь: Python → JSON-файл → Python.",
        },
        {
            "id": "oop-wallet",
            "order": 8,
            "title": "Кошелёк расходов",
            "subtitle": "Объект хранит данные и сам строит итоговый отчёт.",
            "icon": "👛",
            "level": "ООП",
            "requires_lesson_ids": ["oop-design-init"],
            "xp": 105,
            "description": "Заверши методы класса Wallet: посчитай сумму и собери подпись владельца.",
            "skills": ["class", "__init__", "методы", "sum()", "f-строки"],
            "tool_ids": ["class", "init", "sum", "f-string", "return"],
            "checklist": [
                "Не менять __init__: owner и amounts уже сохранены в self.",
                "В total() вернуть сумму всех self.amounts.",
                "В label() вызвать total() и вернуть строку «Имя: сумма ₽».",
            ],
            "starter": (
                "class Wallet:\n"
                "    def __init__(self, owner, amounts):\n"
                "        self.owner = owner\n"
                "        self.amounts = amounts\n\n"
                "    def total(self):\n"
                "        # верни сумму расходов\n"
                "        return 0\n\n"
                "    def label(self):\n"
                "        # верни подпись владельца и итог\n"
                "        return ''\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {"kind": "call", "call": "Wallet('Аня', [120, 80]).total()", "expected": 200},
                {
                    "kind": "call",
                    "call": "Wallet('Лев', [50, 25]).label()",
                    "expected": "Лев: 75 ₽",
                },
            ],
            "scenarios": [
                {
                    "name": "сумма нескольких расходов",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "Wallet('Аня', [120, 80]).total()",
                            "expected": 200,
                        }
                    ],
                },
                {
                    "name": "подпись другого владельца",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "Wallet('Лев', [50, 25]).label()",
                            "expected": "Лев: 75 ₽",
                        }
                    ],
                },
            ],
            "hints": [
                "sum(self.amounts) возвращает сумму чисел, сохранённых в объекте.",
                "Внутри другого метода текущий объект вызывает свой метод так: self.total().",
                "Собери label одной f-строкой из self.owner и результата self.total().",
            ],
            "success": "Класс теперь не просто хранит данные, а отвечает за расчёт и представление.",
        },
        {
            "id": "testing-normalizer",
            "order": 9,
            "title": "Лаборатория тестов",
            "subtitle": "Исправляем ожидания и проверяем поведение через assert.",
            "icon": "🧪",
            "level": "Тестирование",
            "requires_lesson_ids": ["testing-unit-tests"],
            "xp": 115,
            "description": (
                "Функция уже нормализует имя. Исправь два ожидаемых результата так, чтобы "
                "проверки действительно описывали её поведение."
            ),
            "skills": ["assert", "тест-кейс", "strip()", "lower()"],
            "tool_ids": ["assert", "strip", "lower", "comparison", "return"],
            "checklist": [
                "Прочитать normalize_username() и предсказать оба результата.",
                "Исправить только значения справа от == в двух assert.",
                "Не удалять проверки и оставить return 2 после них.",
            ],
            "starter": (
                "def normalize_username(text):\n"
                "    return text.strip().lower()\n\n"
                "def verify_normalizer():\n"
                "    assert normalize_username(' Py ') == 'PY'\n"
                "    assert normalize_username('  АНЯ  ') == 'АНЯ'\n"
                "    return 2\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {"kind": "call", "call": "verify_normalizer()", "expected": 2},
                {"kind": "call", "call": "normalize_username('  Max  ')", "expected": "max"},
            ],
            "scenarios": [
                {
                    "name": "две встроенные проверки",
                    "inputs": [],
                    "tests": [{"kind": "call", "call": "verify_normalizer()", "expected": 2}],
                },
                {
                    "name": "новое имя",
                    "inputs": [],
                    "tests": [
                        {"kind": "call", "call": "normalize_username('  Max  ')", "expected": "max"}
                    ],
                },
            ],
            "hints": [
                "assert проверяет, что выражение справа и слева от == действительно совпадает.",
                "strip() уберёт пробелы по краям, затем lower() вернёт строчную копию.",
                "Для ' Py ' ожидается 'py'; проделай тот же прогноз для кириллического имени.",
            ],
            "success": "Тесты теперь фиксируют реальное правило нормализации и проходят на новых данных.",
        },
        {
            "id": "cli-router",
            "order": 10,
            "title": "Маршрутизатор CLI",
            "subtitle": "Отделяем обработку аргументов от системного запуска программы.",
            "icon": "⌨️",
            "level": "Модули и CLI",
            "requires_lesson_ids": ["modules-main-guard", "cli-environment-argv"],
            "xp": 125,
            "description": "Заверши чистую функцию dispatch(args), которую легко запускать и тестировать.",
            "skills": ["аргументы CLI", "списки", "условия", "функции"],
            "tool_ids": [
                "list",
                "index",
                "len",
                "if",
                "else",
                "comparison",
                "f-string",
                "return",
            ],
            "checklist": [
                "Для пустого args оставить готовую строку «Справка».",
                "Для команды hello взять имя из args[1] или использовать «мир».",
                "Для остальных команд вернуть «Неизвестная команда».",
            ],
            "starter": (
                "def dispatch(args):\n"
                "    if not args:\n"
                "        return 'Справка'\n"
                "    command = args[0]\n"
                "    if command == 'hello':\n"
                "        # возьми имя или запасное значение и верни приветствие\n"
                "        return ''\n"
                "    return 'Неизвестная команда'\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {"kind": "call", "call": "dispatch([])", "expected": "Справка"},
                {
                    "kind": "call",
                    "call": "dispatch(['hello', 'Мира'])",
                    "expected": "Привет, Мира!",
                },
                {"kind": "call", "call": "dispatch(['hello'])", "expected": "Привет, мир!"},
            ],
            "scenarios": [
                {
                    "name": "имя передано",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "dispatch(['hello', 'Мира'])",
                            "expected": "Привет, Мира!",
                        }
                    ],
                },
                {
                    "name": "имя не передано",
                    "inputs": [],
                    "tests": [
                        {"kind": "call", "call": "dispatch(['hello'])", "expected": "Привет, мир!"}
                    ],
                },
                {
                    "name": "пустая команда",
                    "inputs": [],
                    "tests": [{"kind": "call", "call": "dispatch([])", "expected": "Справка"}],
                },
            ],
            "hints": [
                "len(args) показывает, есть ли после команды отдельное имя.",
                "Внутри ветки hello сделай обычные if/else: при len(args) > 1 возьми args[1], иначе сохрани 'мир'.",
                "Верни f-строку с выбранным name внутри ветки hello; остальные return уже готовы.",
            ],
            "success": "Ядро CLI обрабатывает разные аргументы и остаётся удобным для тестирования.",
        },
        {
            "id": "local-api-summary",
            "order": 11,
            "title": "Разбор ответа API",
            "subtitle": "Работаем с локальным словарём так же, как с полученным JSON.",
            "icon": "🌐",
            "level": "API без сети",
            "requires_lesson_ids": ["http-api-json-api", "comprehensions-list-comprehension"],
            "xp": 135,
            "description": "Собери краткую сводку из безопасного локального ответа API.",
            "skills": ["JSON-словарь", "get()", "len()", "list comprehension"],
            "tool_ids": ["get", "len", "list-comprehension", "dict", "return"],
            "checklist": [
                "Получить items через payload.get('items', []).",
                "Собрать titles из каждого item с запасным текстом «Без названия».",
                "Вернуть словарь с count и titles.",
            ],
            "starter": (
                "def summarize_response(payload):\n"
                "    items = payload.get('items', [])\n"
                "    # собери список названий\n"
                "    titles = []\n"
                "    # верни count и titles в словаре\n"
                "    return {}\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {
                    "kind": "call",
                    "call": "summarize_response({'items': [{'title': 'Урок'}, {'title': 'Практика'}]})",
                    "expected": {"count": 2, "titles": ["Урок", "Практика"]},
                },
                {
                    "kind": "call",
                    "call": "summarize_response({'items': [{}]})",
                    "expected": {"count": 1, "titles": ["Без названия"]},
                },
            ],
            "scenarios": [
                {
                    "name": "два объекта",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "summarize_response({'items': [{'title': 'Урок'}, {'title': 'Практика'}]})",
                            "expected": {"count": 2, "titles": ["Урок", "Практика"]},
                        }
                    ],
                },
                {
                    "name": "нет title",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "summarize_response({'items': [{}]})",
                            "expected": {"count": 1, "titles": ["Без названия"]},
                        }
                    ],
                },
            ],
            "hints": [
                "item.get('title', 'Без названия') безопасно читает необязательное поле.",
                "Список строится так: [выражение for item in items].",
                "После titles верни {'count': len(items), 'titles': titles}.",
            ],
            "success": "Ответ API преобразован в устойчивую структуру для интерфейса.",
        },
        {
            "id": "sqlite-query-builder",
            "order": 12,
            "title": "Безопасный SQLite-запрос",
            "subtitle": "Отделяем SQL-шаблон от пользовательских значений.",
            "icon": "🗄️",
            "level": "Базы данных",
            "requires_lesson_ids": ["databases-parameters"],
            "xp": 145,
            "description": (
                "Собери данные для параметризованного INSERT. Реальную БД редактор не открывает, "
                "поэтому проверяется безопасная форма запроса и параметров."
            ),
            "skills": ["SQLite", "плейсхолдер ?", "параметры", "булево значение"],
            "tool_ids": ["sql-parameters", "default-parameter", "int", "dict", "return"],
            "checklist": [
                "Не подставлять title внутрь SQL через f-строку.",
                "Оставить два плейсхолдера ? для title и done.",
                "Вернуть словарь с sql и списком params; done преобразовать через int().",
            ],
            "starter": (
                "def build_insert(title, done=False):\n"
                "    sql = 'INSERT INTO tasks (title, done) VALUES (?, ?)'\n"
                "    # подготовь список параметров отдельно от SQL\n"
                "    params = []\n"
                "    return {'sql': sql, 'params': params}\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {
                    "kind": "call",
                    "call": "build_insert('Купить хлеб')",
                    "expected": {
                        "sql": "INSERT INTO tasks (title, done) VALUES (?, ?)",
                        "params": ["Купить хлеб", 0],
                    },
                },
                {
                    "kind": "call",
                    "call": "build_insert('Готово', done=True)",
                    "expected": {
                        "sql": "INSERT INTO tasks (title, done) VALUES (?, ?)",
                        "params": ["Готово", 1],
                    },
                },
            ],
            "scenarios": [
                {
                    "name": "новая задача",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "build_insert('Купить хлеб')",
                            "expected": {
                                "sql": "INSERT INTO tasks (title, done) VALUES (?, ?)",
                                "params": ["Купить хлеб", 0],
                            },
                        }
                    ],
                },
                {
                    "name": "выполненная задача",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "build_insert('Готово', done=True)",
                            "expected": {
                                "sql": "INSERT INTO tasks (title, done) VALUES (?, ?)",
                                "params": ["Готово", 1],
                            },
                        }
                    ],
                },
            ],
            "hints": [
                "Плейсхолдер ? занимает место значения, которое драйвер получит отдельно.",
                "int(False) даёт 0, int(True) — 1: это удобно для поля SQLite done.",
                "Нужный params: [title, int(done)]. SQL-строку при этом не меняй.",
            ],
            "success": "Запрос отделён от данных и готов к безопасной передаче SQLite-драйверу.",
        },
        {
            "id": "job-scheduler",
            "order": 13,
            "title": "Планировщик очереди",
            "subtitle": "Кладём работы в настоящую Queue и безопасно забираем их по одной.",
            "icon": "🧵",
            "level": "Конкурентность",
            "requires_lesson_ids": ["concurrency-queues"],
            "xp": 155,
            "description": (
                "Наполни потокобезопасную очередь и раздай задачи исполнителям по кругу. "
                "Результат остаётся детерминированным, поэтому правило легко проверить тестами."
            ),
            "skills": ["queue.Queue", "put()/get()", "empty()", "остаток %"],
            "tool_ids": [
                "import",
                "queue",
                "queue-put",
                "queue-get",
                "queue-empty",
                "while",
                "modulo",
                "append",
                "dict",
                "return",
            ],
            "checklist": [
                "Положить каждую работу в Queue через put().",
                "Пока очередь не пуста, забирать следующую работу через get().",
                "После каждой работы циклически менять worker через остаток %.",
                "Добавить словарь worker/job в plan и вернуть весь список.",
            ],
            "starter": (
                "from queue import Queue\n\n"
                "def schedule_jobs(jobs, workers):\n"
                "    tasks = Queue()\n"
                "    for job in jobs:\n"
                "        tasks.put(job)\n"
                "    plan = []\n"
                "    worker = 0\n"
                "    while not tasks.empty():\n"
                "        job = tasks.get()\n"
                "        # добавь worker/job и выбери следующего исполнителя\n"
                "        plan.append({})\n"
                "        worker = 0\n"
                "    return plan\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {
                    "kind": "call",
                    "call": "schedule_jobs(['A', 'B', 'C'], 2)",
                    "expected": [
                        {"worker": 0, "job": "A"},
                        {"worker": 1, "job": "B"},
                        {"worker": 0, "job": "C"},
                    ],
                },
                {
                    "kind": "call",
                    "call": "schedule_jobs(['A'], 3)",
                    "expected": [{"worker": 0, "job": "A"}],
                },
            ],
            "scenarios": [
                {
                    "name": "двое исполнителей",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "schedule_jobs(['A', 'B', 'C'], 2)",
                            "expected": [
                                {"worker": 0, "job": "A"},
                                {"worker": 1, "job": "B"},
                                {"worker": 0, "job": "C"},
                            ],
                        }
                    ],
                },
                {
                    "name": "одна работа",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "schedule_jobs(['A'], 3)",
                            "expected": [{"worker": 0, "job": "A"}],
                        }
                    ],
                },
            ],
            "hints": [
                "Queue.put(item) добавляет работу, Queue.get() забирает самую раннюю.",
                "tasks.empty() возвращает True, когда в очереди больше ничего нет.",
                "В append передай {'worker': worker, 'job': job}.",
                "После append вычисли worker = (worker + 1) % workers.",
            ],
            "success": "Планировщик использует настоящую потокобезопасную очередь и распределяет работу предсказуемо.",
        },
        {
            "id": "async-batch",
            "order": 14,
            "title": "Асинхронная партия",
            "subtitle": "Запускаем несколько корутин и собираем результаты в прежнем порядке.",
            "icon": "⚡",
            "level": "Async",
            "requires_lesson_ids": ["async-gather-timeouts"],
            "xp": 170,
            "description": "Заверши collect_scores(): дождись всей группы через asyncio.gather().",
            "skills": ["async def", "await", "asyncio.gather()", "asyncio.run()"],
            "tool_ids": [
                "import",
                "async-def",
                "await",
                "asyncio-sleep",
                "asyncio-gather",
                "asyncio-run",
                "list-comprehension",
                "return",
            ],
            "checklist": [
                "Оставить fetch_score(): она имитирует неблокирующее ожидание.",
                "Собрать корутины fetch_score(value) для каждого value.",
                "Вернуть await asyncio.gather(*tasks), сохранив порядок результатов.",
            ],
            "starter": (
                "import asyncio\n\n"
                "async def fetch_score(value):\n"
                "    await asyncio.sleep(0)\n"
                "    return value * 2\n\n"
                "async def collect_scores(values):\n"
                "    tasks = [fetch_score(value) for value in values]\n"
                "    # дождись всей группы и верни результаты\n"
                "    return []\n\n"
                "def run_scores(values):\n"
                "    return asyncio.run(collect_scores(values))\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {"kind": "call", "call": "run_scores([2, 5])", "expected": [4, 10]},
                {"kind": "call", "call": "run_scores([])", "expected": []},
            ],
            "scenarios": [
                {
                    "name": "две корутины",
                    "inputs": [],
                    "tests": [{"kind": "call", "call": "run_scores([2, 5])", "expected": [4, 10]}],
                },
                {
                    "name": "пустая партия",
                    "inputs": [],
                    "tests": [{"kind": "call", "call": "run_scores([])", "expected": []}],
                },
            ],
            "hints": [
                "asyncio.gather(*tasks) принимает несколько awaitable-объектов и ждёт их вместе.",
                "Оператор * распаковывает список tasks в отдельные аргументы gather().",
                "В collect_scores замени return [] на return await asyncio.gather(*tasks).",
            ],
            "success": "Асинхронная группа выполняется совместно и возвращает упорядоченный результат.",
        },
        {
            "id": "release-capstone",
            "order": 15,
            "title": "Финал: менеджер задач",
            "subtitle": "Соединяем класс, коллекции, методы и JSON в один законченный инструмент.",
            "icon": "🏁",
            "level": "Capstone",
            "requires_lesson_ids": ["capstones-release"],
            "xp": 220,
            "description": "Заверши TaskBoard: добавляй задачи, отмечай выполненные и экспортируй JSON.",
            "skills": ["ООП", "списки и словари", "циклы", "JSON", "декомпозиция"],
            "tool_ids": [
                "import",
                "class",
                "init",
                "append",
                "index",
                "for",
                "json-dumps",
                "return",
            ],
            "checklist": [
                "В add() добавлять словарь title/done в self.tasks.",
                "В complete() менять done выбранной задачи на True.",
                "В export() возвращать JSON-строку через json.dumps(..., ensure_ascii=False).",
                "Не менять build_board(): она проверяет взаимодействие всех методов.",
            ],
            "starter": (
                "import json\n\n"
                "class TaskBoard:\n"
                "    def __init__(self):\n"
                "        self.tasks = []\n\n"
                "    def add(self, title):\n"
                "        # добавь новую невыполненную задачу\n"
                "        return None\n\n"
                "    def complete(self, index):\n"
                "        # измени done выбранной задачи\n"
                "        return None\n\n"
                "    def export(self):\n"
                "        # верни JSON без ASCII-экранирования кириллицы\n"
                "        return '[]'\n\n"
                "def build_board(titles, completed_indexes):\n"
                "    board = TaskBoard()\n"
                "    for title in titles:\n"
                "        board.add(title)\n"
                "    for index in completed_indexes:\n"
                "        board.complete(index)\n"
                "    return board.export()\n"
            ),
            "test_inputs": [],
            "input_example": [],
            "tests": [
                {
                    "kind": "call",
                    "call": "build_board(['Урок'], [0])",
                    "expected": '[{"title": "Урок", "done": true}]',
                },
                {
                    "kind": "call",
                    "call": "build_board(['Код', 'Тест'], [1])",
                    "expected": (
                        '[{"title": "Код", "done": false}, {"title": "Тест", "done": true}]'
                    ),
                },
            ],
            "scenarios": [
                {
                    "name": "одна выполненная задача",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "build_board(['Урок'], [0])",
                            "expected": '[{"title": "Урок", "done": true}]',
                        }
                    ],
                },
                {
                    "name": "две задачи с разным статусом",
                    "inputs": [],
                    "tests": [
                        {
                            "kind": "call",
                            "call": "build_board(['Код', 'Тест'], [1])",
                            "expected": (
                                '[{"title": "Код", "done": false}, {"title": "Тест", "done": true}]'
                            ),
                        }
                    ],
                },
            ],
            "hints": [
                "append() добавляет в self.tasks словарь {'title': title, 'done': False}.",
                "В complete() обратись к self.tasks[index]['done'] и присвой True.",
                "json.dumps(self.tasks, ensure_ascii=False) вернёт строку с читаемой кириллицей.",
                "Проверяй методы по одному, затем запускай оба сценария build_board().",
            ],
            "success": "Финальный инструмент связывает модель данных, поведение, циклы и сериализацию.",
        },
    ]
)

# Эти решения не отправляются в браузер. Они служат исполняемой спецификацией:
# тесты прогоняют каждый проект по всем сценариям и гарантируют, что задание
# действительно решаемо описанными в курсе средствами.
PROJECT_REFERENCE_SOLUTIONS = {
    "greeting-card": "name = input('Имя: ')\nprint(f'Привет, {name}!')\n",
    "purchase-calculator": (
        "price = int(input('Цена: '))\n"
        "count = int(input('Количество: '))\n"
        "print(f'Итого: {price * count}')\n"
    ),
    "access-checker": (
        "password = input('Пароль: ')\n"
        "if password == 'python':\n"
        "    print('Доступ открыт')\n"
        "else:\n"
        "    print('Доступ закрыт')\n"
    ),
    "word-counter": (
        "text = input('Фраза: ')\nwords = text.split()\nprint(f'Слов: {len(words)}')\n"
    ),
    "score-summary": (
        "def average_score(scores):\n    total = sum(scores)\n    return total / len(scores)\n"
    ),
    "contact-card": (
        "def format_contact(contact):\n    return f\"{contact['name']} — {contact['city']}\"\n"
    ),
    "notes-json-vault": (
        "import json\n\n"
        "def save_notes(notes):\n"
        "    with open('notes.json', 'w', encoding='utf-8') as file:\n"
        "        json.dump(notes, file, ensure_ascii=False)\n"
        "    with open('notes.json', encoding='utf-8') as file:\n"
        "        return json.load(file)\n"
    ),
    "oop-wallet": (
        "class Wallet:\n"
        "    def __init__(self, owner, amounts):\n"
        "        self.owner = owner\n"
        "        self.amounts = amounts\n\n"
        "    def total(self):\n"
        "        return sum(self.amounts)\n\n"
        "    def label(self):\n"
        "        return f'{self.owner}: {self.total()} ₽'\n"
    ),
    "testing-normalizer": (
        "def normalize_username(text):\n"
        "    return text.strip().lower()\n\n"
        "def verify_normalizer():\n"
        "    assert normalize_username(' Py ') == 'py'\n"
        "    assert normalize_username('  АНЯ  ') == 'аня'\n"
        "    return 2\n"
    ),
    "cli-router": (
        "def dispatch(args):\n"
        "    if not args:\n"
        "        return 'Справка'\n"
        "    if args[0] == 'hello':\n"
        "        if len(args) > 1:\n"
        "            name = args[1]\n"
        "        else:\n"
        "            name = 'мир'\n"
        "        return f'Привет, {name}!'\n"
        "    return 'Неизвестная команда'\n"
    ),
    "local-api-summary": (
        "def summarize_response(payload):\n"
        "    items = payload.get('items', [])\n"
        "    titles = [item.get('title', 'Без названия') for item in items]\n"
        "    return {'count': len(items), 'titles': titles}\n"
    ),
    "sqlite-query-builder": (
        "def build_insert(title, done=False):\n"
        "    sql = 'INSERT INTO tasks (title, done) VALUES (?, ?)'\n"
        "    return {'sql': sql, 'params': [title, int(done)]}\n"
    ),
    "job-scheduler": (
        "from queue import Queue\n\n"
        "def schedule_jobs(jobs, workers):\n"
        "    tasks = Queue()\n"
        "    for job in jobs:\n"
        "        tasks.put(job)\n"
        "    plan = []\n"
        "    worker = 0\n"
        "    while not tasks.empty():\n"
        "        plan.append({'worker': worker, 'job': tasks.get()})\n"
        "        worker = (worker + 1) % workers\n"
        "    return plan\n"
    ),
    "async-batch": (
        "import asyncio\n\n"
        "async def fetch_score(value):\n"
        "    await asyncio.sleep(0)\n"
        "    return value * 2\n\n"
        "async def collect_scores(values):\n"
        "    tasks = [fetch_score(value) for value in values]\n"
        "    return await asyncio.gather(*tasks)\n\n"
        "def run_scores(values):\n"
        "    return asyncio.run(collect_scores(values))\n"
    ),
    "release-capstone": (
        "import json\n\n"
        "class TaskBoard:\n"
        "    def __init__(self):\n"
        "        self.tasks = []\n\n"
        "    def add(self, title):\n"
        "        self.tasks.append({'title': title, 'done': False})\n\n"
        "    def complete(self, index):\n"
        "        self.tasks[index]['done'] = True\n\n"
        "    def export(self):\n"
        "        return json.dumps(self.tasks, ensure_ascii=False)\n\n"
        "def build_board(titles, completed_indexes):\n"
        "    board = TaskBoard()\n"
        "    for title in titles:\n"
        "        board.add(title)\n"
        "    for index in completed_indexes:\n"
        "        board.complete(index)\n"
        "    return board.export()\n"
    ),
}

PROJECT_OPENING_HINT = (
    "Сначала пройди контрольный список сверху: назови входные данные, требуемый результат "
    "и проверь, какая часть заготовки уже готова. Пока не меняй несколько мест сразу."
)

for project in PROJECTS:
    project["reference_solution"] = PROJECT_REFERENCE_SOLUTIONS[project["id"]]
    project["hints"] = [PROJECT_OPENING_HINT, *project["hints"]]
    project["tool_help"] = tool_reference_cards(project["tool_ids"])

PROJECT_BY_ID = {project["id"]: project for project in PROJECTS}


def public_project(project: dict[str, Any], include_editor: bool = False) -> dict[str, Any]:
    """Не выдаёт тесты и контрольные входные данные в браузер."""
    hidden = {
        "tests",
        "scenarios",
        "test_inputs",
        "starter",
        "hints",
        "checklist",
        "input_example",
        "tool_ids",
        "tool_help",
        "reference_solution",
    }
    result = {key: value for key, value in project.items() if key not in hidden}
    if include_editor:
        result.update(
            {
                "starter": project["starter"],
                "hints": project["hints"],
                "checklist": project["checklist"],
                "input_example": project["input_example"],
                "tool_help": public_tool_help(project["tool_help"]),
            }
        )
    return result
