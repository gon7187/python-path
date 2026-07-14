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
        "min_lessons": 0,
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
        "min_lessons": 5,
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
        "min_lessons": 10,
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
        "min_lessons": 16,
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
        "min_lessons": 25,
        "xp": 65,
        "description": "Собери маленький отчёт: сколько оценок, какая сумма и среднее значение.",
        "skills": ["списки", "sum()", "len()"],
        "checklist": [
            "Оставить список scores как есть.",
            "Посчитать сумму и среднее через sum и len.",
            "Вывести среднее в формате «Среднее: число».",
        ],
        "starter": "scores = [5, 4, 5, 3]\ntotal = sum(scores)\naverage = total / len(scores)\n# выведи среднее\n",
        "test_inputs": [],
        "input_example": [],
        "tests": [{"kind": "stdout", "expected": "Среднее: 4.25"}],
        "hints": [
            "total и len(scores) уже готовы: осталось вывести average.",
            "В f-строке можно подставить average прямо в фигурные скобки.",
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
        "min_lessons": 40,
        "xp": 75,
        "description": "Заполни словарь с контактными данными и собери из него аккуратную карточку.",
        "skills": ["словари", "ключи", "f-строки"],
        "checklist": [
            "Оставить ключи name и city в словаре contact.",
            "Достать значения по ключам.",
            "Вывести одну строку с именем и городом.",
        ],
        "starter": "contact = {'name': 'Мира', 'city': 'Казань'}\n# выведи: Мира — Казань\n",
        "test_inputs": [],
        "input_example": [],
        "tests": [{"kind": "stdout", "expected": "Мира — Казань"}],
        "hints": [
            "Значение по ключу читается так: contact['name'].",
            "Собери обе части одной f-строкой: print(f\"{contact['name']} — {contact['city']}\").",
        ],
        "success": "Карточка контакта готова: данные из словаря стали понятным интерфейсом.",
    },
]

PROJECT_BY_ID = {project["id"]: project for project in PROJECTS}


def public_project(project: dict[str, Any], include_editor: bool = False) -> dict[str, Any]:
    """Не выдаёт тесты и контрольные входные данные в браузер."""
    hidden = {"tests", "test_inputs", "starter", "hints", "checklist", "input_example"}
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
