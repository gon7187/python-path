"""Реестр рукописных уроков расширенного курса.

Каждый модуль пакета с именем ``lessons_*.py`` объявляет ``LESSONS`` —
список словарей уроков. Модули находятся автоматически при импорте пакета,
поэтому новый рукописный урок подключается добавлением одного файла, без
правок общих модулей.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Any

REQUIRED_KEYS = ("id", "theory", "questions")
ALLOWED_KEYS = frozenset({"id", "theory", "questions", "subtitle"})


def _lesson_modules() -> list[ModuleType]:
    """Импортирует все модули ``lessons_*`` пакета в стабильном порядке."""
    modules: list[ModuleType] = []
    for module_info in sorted(pkgutil.iter_modules(__path__), key=lambda info: info.name):
        if not module_info.name.startswith("lessons_"):
            continue
        modules.append(importlib.import_module(f"{__name__}.{module_info.name}"))
    return modules


def _validate_lesson(lesson: Any, module_name: str) -> str:
    """Проверяет форму урока и возвращает его id или бросает ValueError."""
    if not isinstance(lesson, dict):
        raise ValueError(f"Рукописный урок в {module_name} должен быть словарём: {lesson!r}")

    lesson_id = lesson.get("id")
    if not isinstance(lesson_id, str) or not lesson_id.strip():
        raise ValueError(f"Рукописный урок в {module_name} без корректного id: {lesson_id!r}")

    missing = [key for key in REQUIRED_KEYS if key not in lesson]
    if missing:
        raise ValueError(f"Рукописный урок {lesson_id}: отсутствуют обязательные ключи {missing}")

    extra = sorted(set(lesson) - ALLOWED_KEYS)
    if extra:
        raise ValueError(f"Рукописный урок {lesson_id}: лишние ключи {extra}")

    if not isinstance(lesson["theory"], list):
        raise ValueError(f"Рукописный урок {lesson_id}: theory должен быть списком карточек")
    if not isinstance(lesson["questions"], list):
        raise ValueError(f"Рукописный урок {lesson_id}: questions должен быть списком заданий")
    if "subtitle" in lesson and not isinstance(lesson["subtitle"], str):
        raise ValueError(f"Рукописный урок {lesson_id}: subtitle должен быть строкой")

    return lesson_id


def _build_registry() -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
    for module in _lesson_modules():
        lessons = getattr(module, "LESSONS", None)
        if not isinstance(lessons, list):
            raise ValueError(f"Модуль {module.__name__} должен объявлять LESSONS: list[dict]")
        for lesson in lessons:
            lesson_id = _validate_lesson(lesson, module.__name__)
            if lesson_id in registry:
                raise ValueError(
                    f"Рукописный урок {lesson_id} объявлен дважды: "
                    f"{owners[lesson_id]} и {module.__name__}"
                )
            registry[lesson_id] = lesson
            owners[lesson_id] = module.__name__
    return registry


HANDWRITTEN: dict[str, dict[str, Any]] = _build_registry()
