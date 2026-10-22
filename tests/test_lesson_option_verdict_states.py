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


def _rule_matches(css: str, selector: str) -> list[re.Match[str]]:
    matches = []
    for match in RULE.finditer(css):
        parts = [part.strip() for part in match.group(1).split(",")]
        if selector in parts:
            matches.append(match)
    return matches


def _rule_body(css: str, selector: str) -> str:
    return "\n".join(match.group(2) for match in _rule_matches(css, selector))


def _declarations(body: str) -> list[tuple[str, str]]:
    pairs = []
    for item in body.split(";"):
        if ":" in item:
            prop, value = item.split(":", 1)
            pairs.append((prop.strip(), value.strip()))
    return pairs


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
    for prop, value in _declarations(body):
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


def test_c1_selected_option_is_neutral_blue_not_green() -> None:
    body = _rule_body(_styles(), ".option.selected")

    assert body.strip(), "нет правила .option.selected в styles.css"
    assert "green" not in _families(body)
    assert "blue" in _families_of(body, "border")
    assert "blue" in _families_of(body, "background")


def test_c2_is_right_is_green_and_is_wrong_is_red_in_styles() -> None:
    css = _styles()
    right = _rule_body(css, ".option.is-right")
    wrong = _rule_body(css, ".option.is-wrong")

    assert right.strip(), "нет правила .option.is-right в styles.css"
    assert "green" in _families(right)
    assert "red" not in _families(right)
    assert wrong.strip(), "нет правила .option.is-wrong в styles.css"
    assert "red" in _families(wrong)
    assert "green" not in _families(wrong)


def test_c2_verdict_rules_come_after_selected_rule_so_they_win_the_cascade() -> None:
    css = _styles()
    selected = _rule_matches(css, ".option.selected")
    verdicts = _rule_matches(css, ".option.is-right") + _rule_matches(css, ".option.is-wrong")

    assert selected, "нет правила .option.selected в styles.css"
    assert verdicts, "нет правил .option.is-right / .option.is-wrong в styles.css"
    assert all(match.start() > selected[-1].start() for match in verdicts)


def test_c2_check_marks_selected_option_is_right_or_is_wrong() -> None:
    body = _js_with_helpers(_app_js(), "applyVerdictUi")

    assert "is-right" in body
    assert "is-wrong" in body
    assert "selected" in body


def test_c2_new_choice_clears_option_verdict_marks() -> None:
    body = _js_with_helpers(_app_js(), "syncAnswer")

    assert "is-right" in body
    assert "is-wrong" in body


def test_c3_all_three_option_states_have_rules_in_styles() -> None:
    css = _styles()

    for selector in (".option.selected", ".option.is-right", ".option.is-wrong"):
        assert _rule_body(css, selector).strip(), f"нет правила {selector} в styles.css"


def test_c3_choice_click_only_moves_selected_class_in_practice_and_exam() -> None:
    body = _js_function(_app_js(), "bindQuestionControls")

    assert "classList.add('selected')" in body
    assert "classList.remove('selected')" in body
    assert "is-right" not in body
    assert "is-wrong" not in body


def test_c3_practice_and_exam_share_option_markup_and_binding() -> None:
    js = _app_js()

    assert 'class="option"' in _js_function(js, "questionTemplate")
    for name in ("renderPractice", "renderExam"):
        body = _js_function(js, name)
        assert "questionTemplate(" in body
        assert "bindQuestionControls(" in body
