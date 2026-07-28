import pytest

from app.error_hints import translate_error


@pytest.mark.parametrize(
    ("error_text", "title"),
    [
        ("SyntaxError: invalid syntax", "Синтаксическая ошибка"),
        ("SyntaxError: unexpected EOF while parsing", "Незаконченный код"),
        ("SyntaxError: EOL while scanning string literal", "Незакрытая строка"),
        ("SyntaxError: invalid character '№'", "Недопустимый символ"),
        ("IndentationError: expected an indented block", "Ошибка отступа"),
        ("IndentationError: unindent does not match any outer indentation level", "Ошибка отступа"),
        ("TabError: inconsistent use of tabs and spaces in indentation", "Смешаны табы и пробелы"),
        ("TypeError: unsupported operand type(s)", "Неподходящий тип данных"),
        ("ValueError: invalid literal for int()", "Некорректное значение"),
        ("IndexError: list index out of range", "Индекс вне диапазона"),
        ("KeyError: 'name'", "Ключ не найден"),
        (
            "AttributeError: 'str' object has no attribute 'append'",
            "Нет такого свойства или метода",
        ),
        ("ZeroDivisionError: division by zero", "Деление на ноль"),
        ("ImportError: cannot import name 'thing'", "Ошибка импорта"),
        ("ModuleNotFoundError: No module named 'thing'", "Модуль не найден"),
        ("TimeoutError: Код выполнялся слишком долго", "Время выполнения истекло"),
        ("RuntimeError: something unusual", "Неизвестная ошибка"),
    ],
)
def test_translate_error_categories(error_text: str, title: str) -> None:
    result = translate_error(error_text)

    assert result["title"] == title
    assert result["hint"]
    assert result["original"] == error_text


def test_translate_error_extracts_name_from_name_error() -> None:
    result = translate_error("NameError: name 'total_sum' is not defined")

    assert result["title"] == "Неизвестное имя"
    assert "total_sum" in result["hint"]
