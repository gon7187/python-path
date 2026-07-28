"""Короткие подсказки к распространённым ошибкам Python."""

from __future__ import annotations

import re


def translate_error(error_text: str) -> dict[str, str]:
    """Возвращает понятную новичку подсказку, сохраняя исходную ошибку."""
    text = error_text or ""
    lower = text.casefold()
    title, hint = (
        "Неизвестная ошибка",
        "Прочитай текст ошибки и проверь последнюю изменённую строку кода.",
    )

    if "unexpected eof while parsing" in lower:
        title, hint = "Незаконченный код", "Проверь, закрыты ли скобки, кавычки и все блоки кода."
    elif "eol while scanning string literal" in lower or "unterminated string literal" in lower:
        title, hint = "Незакрытая строка", "Проверь, есть ли закрывающая кавычка у строки."
    elif "invalid character" in lower:
        title, hint = (
            "Недопустимый символ",
            "Проверь строку: в код случайно мог попасть необычный символ.",
        )
    elif "syntaxerror" in lower:
        title, hint = (
            "Синтаксическая ошибка",
            "Проверь знаки препинания, скобки, кавычки и написание команды.",
        )
    elif "expected an indented block" in lower or "unindent does not match" in lower:
        title, hint = (
            "Ошибка отступа",
            "После двоеточия добавь отступ в 4 пробела и выровняй строки блока.",
        )
    elif "taberror" in lower:
        title, hint = (
            "Смешаны табы и пробелы",
            "Используй для отступов только пробелы — по 4 на каждый уровень.",
        )
    elif "nameerror" in lower:
        name = re.search(r"name ['\"](.+?)['\"] is not defined", text)
        variable = f" «{name.group(1)}»" if name else ""
        title, hint = (
            "Неизвестное имя",
            f"Проверь написание{variable}: переменную нужно объявить до использования.",
        )
    elif "typeerror" in lower:
        title, hint = (
            "Неподходящий тип данных",
            "Проверь, какие значения участвуют в операции: строку и число нельзя сложить напрямую.",
        )
    elif "valueerror" in lower:
        title, hint = (
            "Некорректное значение",
            "Проверь формат значения и то, подходит ли оно для этой операции.",
        )
    elif "indexerror" in lower:
        title, hint = (
            "Индекс вне диапазона",
            "Проверь номер элемента: отсчёт в списке начинается с 0.",
        )
    elif "keyerror" in lower:
        title, hint = "Ключ не найден", "Проверь название ключа и убедись, что он есть в словаре."
    elif "attributeerror" in lower:
        title, hint = (
            "Нет такого свойства или метода",
            "Проверь название метода и подходит ли он для этого типа данных.",
        )
    elif "zerodivisionerror" in lower:
        title, hint = "Деление на ноль", "Перед делением убедись, что делитель не равен нулю."
    elif "modulenotfounderror" in lower:
        title, hint = (
            "Модуль не найден",
            "Проверь название модуля и его доступность в учебном редакторе.",
        )
    elif "importerror" in lower:
        title, hint = (
            "Ошибка импорта",
            "Проверь название модуля или объекта, который хочешь импортировать.",
        )
    elif "timeouterror" in lower or "слишком долго" in lower:
        title, hint = (
            "Время выполнения истекло",
            "Проверь условие цикла: оно должно когда-нибудь становиться ложным.",
        )

    return {"title": title, "hint": hint, "original": text}
