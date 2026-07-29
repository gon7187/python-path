"""Русский учебный план: 120 уроков, практика и контрольные точки."""

from __future__ import annotations

from app.extended_curriculum import EXTRA_EXAMS, EXTRA_LESSONS, EXTRA_MODULES
from app.lessons_1_12 import LESSONS_1_12
from app.lessons_13_25 import LESSONS_13_25

MODULES = [
    {
        "id": "start",
        "title": "Старт: говорим с Python",
        "description": "Первая программа, переменные и f-строки.",
        "color": "mint",
        "icon": "🌱",
    },
    {
        "id": "logic",
        "title": "Логика и повторения",
        "description": "Условия и циклы: программа начинает думать.",
        "color": "sky",
        "icon": "🧠",
    },
    {
        "id": "structures",
        "title": "Функции и данные",
        "description": "Собираем код в блоки и работаем с коллекциями.",
        "color": "violet",
        "icon": "🧩",
    },
    {
        "id": "realworld",
        "title": "Python в деле",
        "description": "Файлы, ошибки и первые собственные классы.",
        "color": "sun",
        "icon": "🚀",
    },
]

LESSONS = list(LESSONS_1_12)

MODULES.extend(EXTRA_MODULES)
LESSONS.extend(LESSONS_13_25)
LESSONS.extend(EXTRA_LESSONS)


EXAMS = {
    "start": {
        "title": "Мини-экзамен: основы",
        "description": "Проверь, уверенно ли ты пишешь первые программы.",
        "question_ids": [
            "hello-choice",
            "variables-term",
            "strings-input-choice",
            "hello-code",
            "variables-code",
        ],
    },
    "logic": {
        "title": "Мини-экзамен: логика",
        "description": "Условия и циклы в одном коротком забеге.",
        "question_ids": [
            "conditions-choice",
            "for-loop-choice",
            "while-loop-term",
            "for-loop-code",
            "while-loop-code",
        ],
    },
    "structures": {
        "title": "Мини-экзамен: структуры",
        "description": "Функции, списки и словари — твой новый инструментарий.",
        "question_ids": [
            "functions-choice",
            "lists-term",
            "dicts-sets-choice",
            "functions-code",
            "dicts-sets-code",
        ],
    },
    "realworld": {
        "title": "Финальный экзамен",
        "description": "Закрепи навыки, которые используют в реальных программах.",
        "question_ids": [
            "files-choice",
            "exceptions-choice",
            "classes-term",
            "exceptions-code",
            "classes-code",
        ],
    },
    **EXTRA_EXAMS,
}

LESSON_BY_ID = {item["id"]: item for item in LESSONS}
QUESTION_BY_ID = {question["id"]: question for item in LESSONS for question in item["questions"]}


def public_question(question: dict) -> dict:
    return {
        key: value
        for key, value in question.items()
        if key not in {"answer", "answers", "tests", "reference"}
    }


def public_lesson(item: dict, include_questions: bool = False) -> dict:
    output = {key: value for key, value in item.items() if key not in {"questions", "theory"}}
    if include_questions:
        output["theory"] = item["theory"]
        output["questions"] = [public_question(question) for question in item["questions"]]
    return output
