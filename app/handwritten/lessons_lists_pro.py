"""Рукописные уроки раздела «Списки в работе»."""

from __future__ import annotations

from typing import Any

LESSONS: list[dict[str, Any]] = [
    {
        "id": "lists-pro-sorting",
        "subtitle": "sorted, key и reverse вместо путаницы с None",
        "theory": [
            {
                "title": "Две сортировки: sorted() и list.sort()",
                "text": (
                    "`sorted()` — встроенная функция: она возвращает новый список и не меняет "
                    "исходный. `list.sort()` — метод списка: он сортирует список на месте и "
                    "возвращает None. Поэтому выражение `x = x.sort()` затирает переменную: "
                    "в x окажется None, а не отсортированный список. Бери `sorted()`, когда "
                    "нужен новый объект, и `list.sort()`, когда список можно изменить."
                ),
                "example": (
                    "numbers = [3, 1, 2]\n"
                    "ordered = sorted(numbers)\n"
                    "print(ordered)\n"
                    "print(numbers)\n"
                    "numbers.sort()\n"
                    "print(numbers)"
                ),
                "tip": "Проверь, нужен ли тебе исходный порядок после сортировки.",
            },
            {
                "title": "Параметры key и reverse",
                "text": (
                    "`key` принимает функцию, по которой сравниваются элементы, а "
                    "`reverse=True` переворачивает порядок. `key=len` сортирует строки по "
                    "длине, `key=lambda item: item['age']` — по полю словаря. Ключ должен "
                    "возвращать сравнимые между собой значения, иначе Python бросит TypeError."
                ),
                "example": (
                    "words = ['python', 'c', 'java']\n"
                    "print(sorted(words, key=len))\n"
                    "print(sorted(words, reverse=True))"
                ),
                "tip": "Сортировка устойчива: элементы с одинаковым ключом сохраняют порядок.",
            },
            {
                "title": "Типичная ошибка: x = x.sort()",
                "text": (
                    "Метод `list.sort()` меняет список на месте и возвращает None. "
                    "Присваивание результата — классическая ошибка: `x = x.sort()` делает x "
                    "равным None, и следующий вызов вроде `len(x)` падает с TypeError. Если "
                    "результат нужен в новой переменной, используй `ordered = sorted(x)`."
                ),
                "example": (
                    "numbers = [3, 1, 2]\nresult = numbers.sort()\nprint(result)\nprint(numbers)"
                ),
                "tip": "None в переменной после сортировки — почти всегда забытое присваивание.",
            },
        ],
        "questions": [
            {
                "id": "lists-pro-sorting-choice",
                "kind": "choice",
                "prompt": "Что вернёт `list.sort()` после сортировки списка?",
                "options": [
                    "Новый отсортированный список",
                    "`list.sort()` вернёт None: список сортируется на месте",
                    "Отсортированный кортеж",
                ],
                "answer": "`list.sort()` вернёт None: список сортируется на месте",
                "explanation": (
                    "Метод списка сортирует на месте и возвращает None. Новый список "
                    "возвращает функция sorted()."
                ),
            },
            {
                "id": "lists-pro-sorting-term",
                "kind": "input",
                "prompt": (
                    "Какая функция возвращает новый отсортированный список, не меняя исходный?"
                ),
                "answers": ["sorted", "sorted()", "функция sorted", "сортировка"],
                "placeholder": "Введите имя функции",
                "explanation": (
                    "sorted() строит новый список, а list.sort() изменяет существующий."
                ),
            },
            {
                "id": "lists-pro-sorting-code",
                "kind": "code",
                "prompt": (
                    "Напиши `sort_by_length(words)`, которая возвращает новый список слов, "
                    "отсортированный по длине от короткого к длинному. Исходный список "
                    "меняться не должен. Используй параметр `key`."
                ),
                "starter": ("def sort_by_length(words):\n    # твой код\n    return words\n"),
                "tests": [
                    {
                        "kind": "call",
                        "call": "sort_by_length(['python', 'c', 'java'])",
                        "expected": ["c", "java", "python"],
                    },
                    {
                        "kind": "call",
                        "call": "sort_by_length(['one', 'three', 'two'])",
                        "expected": ["one", "two", "three"],
                    },
                    {"kind": "call", "call": "sort_by_length([])", "expected": []},
                ],
                "reference": "def sort_by_length(words):\n    return sorted(words, key=len)\n",
                "hint": "sorted(words, key=len) сортирует по длине и не меняет words.",
                "explanation": (
                    "Проверка пройдена: key=len задаёт длину как ключ сравнения, а sorted() "
                    "оставляет исходный список нетронутым."
                ),
            },
        ],
    }
]
