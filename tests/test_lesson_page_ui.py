import re
from pathlib import Path


def _app_js() -> str:
    return Path("app/static/app.js").read_text(encoding="utf-8")


def _styles() -> str:
    return Path("app/static/styles.css").read_text(encoding="utf-8")


def test_c1_lesson_page_shows_one_step_with_progress() -> None:
    js = _app_js()

    assert re.search(r"Шаг (\$\{[^}]+\}|\d+) из (\$\{[^}]+\}|\d+)", js)
    assert "progress" in js
    assert "← К маршруту" in js
    assert "lesson.title" in js
    assert "Проверить урок" not in js


def test_c2_step_card_uses_rich_and_has_navigation() -> None:
    js = _app_js()

    assert re.search(r"rich\([^)]*\btitle\b", js)
    assert re.search(r"rich\([^)]*\btext\b", js)
    assert re.search(r"rich\([^)]*\btip\b", js)
    assert re.search(r"<pre[^\n]*example", js)
    assert "Дальше" in js
    assert "← Назад" in js


def test_c3_step_question_checks_answer_and_shows_verdict() -> None:
    js = _app_js()

    assert re.search(r"Задание \$\{[^}]+\}", js)
    assert re.search(r"/api/lessons/\$\{[^}]+\}/check", js)
    assert "explanation" in js
    assert "error_hint" in js
    assert "checks" in js
    assert "Дальше" in js
    assert "← Назад" in js


def test_c4_code_step_keeps_editor_run_and_hint() -> None:
    js = _app_js()

    assert "code-editor" in js
    assert "▶ Запустить" in js
    assert "/api/code/run" in js
    assert "Нужна подсказка?" in js
    assert "'Tab'" in js
    assert "'Enter'" in js
    assert re.search(r"/api/lessons/\$\{[^}]+\}/check", js)


def test_c5_final_submit_and_summary_screen() -> None:
    js = _app_js()

    assert re.search(r"/api/lessons/\$\{[^}]+\}/submit", js)
    assert "Урок пройден" in js
    assert re.search(r"\+\$\{[^}]+\} XP", js)
    assert "Следующий урок" in js
    assert "К маршруту" in js
    assert "Пройти заново" in js
    assert "next_lesson" in js
    assert "refreshDashboard()" in js


def test_c6_example_card_has_run_button_driven_by_run_flag() -> None:
    js = _app_js()

    assert "▶ Запустить пример" in js
    assert re.search(r"\.run\b", js)
    assert "/api/code/run" in js


def test_c7_exercise_numbering_starts_at_one_and_no_minimum_phrase() -> None:
    js = _app_js()

    assert ".map(questionTemplate)" not in js
    assert not re.search(r"questionTemplate\([^)]*,\s*(index|i|idx)\s*\)", js)
    assert re.search(r"questionTemplate\([^)]*\+ ?1\)", js)
    assert "Задание 0" not in js

    for path in Path("app").rglob("*"):
        if path.suffix in {".py", ".js", ".html"}:
            text = path.read_text(encoding="utf-8")
            assert "минимум 2 правильных" not in text, path


def test_c8_step_styles_fit_375px_without_fixed_wide_widths() -> None:
    css = _styles()
    blocks = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
    step_bodies = [body for selector, body in blocks if ".step" in selector]

    assert step_bodies
    assert any(re.search(r"display:\s*flex", body) for body in step_bodies)
    for body in step_bodies:
        for width in re.findall(r"(?<!max-)(?:min-)?width:\s*(\d+)px", body):
            assert int(width) <= 375
