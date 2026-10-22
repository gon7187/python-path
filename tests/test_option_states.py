"""Состояния варианта ответа: нейтральный выбор и отметка проверки.

До проверки выбранный вариант не должен выглядеть как верный: он подсвечен
нейтральным синим. Зелёный/красный появляются только после «Проверить»
(классы ``is-right`` / ``is-wrong``) и снимаются при выборе другого варианта.
Правила общие для урока, практики и экзамена.
"""

import re
from pathlib import Path

COMMENT = re.compile(r"/\*.*?\*/", re.S)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
COLOR_VAR = re.compile(r"var\(--(green|blue|red)(?:-dark)?\)")
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def _app_js() -> str:
    return Path("app/static/app.js").read_text(encoding="utf-8")


def _styles() -> str:
    return COMMENT.sub("", Path("app/static/styles.css").read_text(encoding="utf-8"))


def _rules(css: str, selector: str) -> list[re.Match[str]]:
    found = []
    for match in RULE.finditer(css):
        parts = [part.strip() for part in match.group(1).split(",")]
        if selector in parts:
            found.append(match)
    return found


def _body(css: str, selector: str) -> str:
    return "\n".join(match.group(2) for match in _rules(css, selector))


def _declarations(body: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in body.split(";"):
        if ":" not in item:
            continue
        prop, value = item.split(":", 1)
        result[prop.strip()] = value.strip()
    return result


def _hex_family(code: str) -> str | None:
    if len(code) == 3:
        code = "".join(char * 2 for char in code)
    red, green, blue = (int(code[index : index + 2], 16) for index in (0, 2, 4))
    if green >= red and green >= blue and green - red >= 10:
        return "green"
    if blue >= red and blue >= green and blue - red >= 10:
        return "blue"
    if red >= green and red >= blue and red - green >= 10:
        return "red"
    return None


def _families(value: str) -> set[str]:
    found = set(COLOR_VAR.findall(value))
    for code in HEX.findall(value):
        family = _hex_family(code)
        if family:
            found.add(family)
    return found


def _families_of(body: str, prefix: str) -> set[str]:
    found: set[str] = set()
    for prop, value in _declarations(body).items():
        if prop.startswith(prefix):
            found |= _families(value)
    return found


def _js_function(js: str, name: str) -> str:
    start = js.index(f"function {name}(")
    return js[start : js.index("\n}", start) + 2]


def _js_with_helpers(js: str, name: str, seen: set[str] | None = None) -> str:
    seen = set() if seen is None else seen
    seen.add(name)
    body = _js_function(js, name)
    for callee in sorted(set(re.findall(r"\b(\w+)\(", body))):
        if callee not in seen and f"function {callee}(" in js:
            body += "\n" + _js_with_helpers(js, callee, seen)
    return body


def test_selected_unchecked_option_is_neutral_blue() -> None:
    body = _body(_styles(), ".option.selected")

    assert body.strip(), "нет правила .option.selected"
    assert "green" not in _families(body), "непроверенный выбор не должен быть зелёным"
    assert "blue" in _families_of(body, "border"), "рамка выбранного варианта должна быть синей"
    assert "blue" in _families_of(body, "background"), "фон выбранного варианта должен быть синим"


def test_checked_option_has_green_or_red_verdict_rules() -> None:
    css = _styles()
    right = _body(css, ".option.is-right")
    wrong = _body(css, ".option.is-wrong")

    assert right.strip(), "нет правила .option.is-right"
    assert "green" in _families(right)
    assert "red" not in _families(right)

    assert wrong.strip(), "нет правила .option.is-wrong"
    assert "red" in _families(wrong)
    assert "green" not in _families(wrong)


def test_verdict_rules_override_neutral_selection() -> None:
    css = _styles()
    selected = _rules(css, ".option.selected")
    verdicts = _rules(css, ".option.is-right") + _rules(css, ".option.is-wrong")

    assert selected, "нет правила .option.selected"
    assert verdicts, "нет правил .option.is-right / .option.is-wrong"
    assert all(match.start() > selected[-1].start() for match in verdicts), (
        "правила вердикта должны идти после .option.selected, чтобы выигрывать каскад"
    )


def test_check_marks_only_the_selected_option() -> None:
    body = _js_with_helpers(_app_js(), "applyVerdictUi")

    assert "result.correct" in body
    assert "is-right" in body
    assert "is-wrong" in body
    assert "classList.contains('selected')" in body, (
        "отметка проверки должна ставиться только выбранному варианту"
    )
    assert "classList.add(correct ? 'is-right' : 'is-wrong')" in body


def test_new_choice_clears_previous_verdict_marks() -> None:
    body = _js_with_helpers(_app_js(), "syncAnswer")

    assert "clearVerdict" in body
    assert "is-right" in body
    assert "is-wrong" in body
    assert "classList.remove('is-right', 'is-wrong')" in body, (
        "при смене ответа старые отметки проверки должны сниматься со всех вариантов"
    )


def test_practice_and_exam_choice_binding_moves_selected_only() -> None:
    body = _js_function(_app_js(), "bindQuestionControls")

    assert "classList.add('selected')" in body
    assert "classList.remove('selected')" in body
    assert "is-right" not in body, "в практике/экзамене выбор не должен отмечаться как верный"
    assert "is-wrong" not in body, "в практике/экзамене выбор не должен отмечаться как неверный"
