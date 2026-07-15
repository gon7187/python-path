"""Небольшие практические проекты с постепенным усложнением."""

from __future__ import annotations

from typing import Any

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
        "checklist": [
            "Запросить имя с понятной подсказкой.",
            "Сохранить ответ в переменную name.",
            "Вывести приветствие с этим именем.",
        ],
        "starter": "name = input('Имя: ')\n# напиши приветствие\n",
        "test_inputs": ["Лена"],
        "input_example": ["Лена"],
        "tests": [{"kind": "stdout", "expected": "Имя: Лена\nПривет, Лена!"}],
        "scenarios": [
            {
                "name": "имя из примера",
                "inputs": ["Лена"],
                "tests": [{"kind": "stdout", "expected": "Имя: Лена\nПривет, Лена!"}],
            },
            {
                "name": "другое имя",
                "inputs": ["Макс"],
                "tests": [{"kind": "stdout", "expected": "Имя: Макс\nПривет, Макс!"}],
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
        "checklist": [
            "Получить цену и количество через input().",
            "Преобразовать оба ответа через int().",
            "Напечатать итог в формате «Итого: число».",
        ],
        "starter": "price = int(input('Цена: '))\ncount = int(input('Количество: '))\n# выведи итог\n",
        "test_inputs": ["120", "3"],
        "input_example": ["120", "3"],
        "tests": [{"kind": "stdout", "expected": "Цена: 120\nКоличество: 3\nИтого: 360"}],
        "scenarios": [
            {
                "name": "три товара",
                "inputs": ["120", "3"],
                "tests": [{"kind": "stdout", "expected": "Цена: 120\nКоличество: 3\nИтого: 360"}],
            },
            {
                "name": "другая цена и количество",
                "inputs": ["75", "2"],
                "tests": [{"kind": "stdout", "expected": "Цена: 75\nКоличество: 2\nИтого: 150"}],
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
        "checklist": [
            "Запросить пароль в переменную password.",
            "Сравнить его со строкой python.",
            "Показать один из двух понятных ответов.",
        ],
        "starter": "password = input('Пароль: ')\n# добавь if и else\n",
        "test_inputs": ["python"],
        "input_example": ["python"],
        "tests": [{"kind": "stdout", "expected": "Пароль: python\nДоступ открыт"}],
        "scenarios": [
            {
                "name": "верный пароль",
                "inputs": ["python"],
                "tests": [{"kind": "stdout", "expected": "Пароль: python\nДоступ открыт"}],
            },
            {
                "name": "неверный пароль",
                "inputs": ["secret"],
                "tests": [{"kind": "stdout", "expected": "Пароль: secret\nДоступ закрыт"}],
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
        "checklist": [
            "Получить фразу в переменную text.",
            "Разделить строку через text.split().",
            "Вывести количество слов с понятной подписью.",
        ],
        "starter": "text = input('Фраза: ')\nwords = text.split()\n# выведи количество слов\n",
        "test_inputs": ["учу Python каждый день"],
        "input_example": ["учу Python каждый день"],
        "tests": [{"kind": "stdout", "expected": "Фраза: учу Python каждый день\nСлов: 4"}],
        "scenarios": [
            {
                "name": "фраза из примера",
                "inputs": ["учу Python каждый день"],
                "tests": [
                    {
                        "kind": "stdout",
                        "expected": "Фраза: учу Python каждый день\nСлов: 4",
                    }
                ],
            },
            {
                "name": "короткая фраза",
                "inputs": ["два слова"],
                "tests": [{"kind": "stdout", "expected": "Фраза: два слова\nСлов: 2"}],
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
        "hints": [
            "Сначала отдельно прочитай значения contact['name'] и contact['city'].",
            "Соедини оба значения одной f-строкой и верни её через return.",
        ],
        "success": "Карточка контакта готова: данные из словаря стали понятным интерфейсом.",
    },
]

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
    }
    result = {key: value for key, value in project.items() if key not in hidden}
    if include_editor:
        result.update(
            {
                "starter": project["starter"],
                "hints": project["hints"],
                "checklist": project["checklist"],
                "input_example": project["input_example"],
            }
        )
    return result
