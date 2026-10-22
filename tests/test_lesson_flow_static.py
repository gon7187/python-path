import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def _app_js() -> str:
    return Path("app/static/app.js").read_text(encoding="utf-8")


def _styles() -> str:
    return Path("app/static/styles.css").read_text(encoding="utf-8")


def test_lesson_builds_interleaved_card_question_steps() -> None:
    js = _app_js()

    assert "function buildLessonSteps" in js
    assert "Math.max(lesson.theory.length, lesson.questions.length)" in js
    assert "steps.push({ kind: 'card'" in js
    assert "steps.push({ kind: 'question'" in js
    assert js.index("steps.push({ kind: 'card'") < js.index("steps.push({ kind: 'question'")


def test_progress_bar_has_segments_and_step_caption() -> None:
    js = _app_js()

    assert "lesson-progress" in js
    assert "progress-seg" in js
    assert "aria-valuenow" in js
    assert "Шаг ${state.index + 1} из ${total}" in js
    assert "← К маршруту" in js


def test_each_question_checks_immediately_via_lesson_check() -> None:
    js = _app_js()

    assert re.search(r"/api/lessons/\$\{[^}]+\}/check", js)
    assert "data-lesson-check" in js
    assert "JSON.stringify({ question_id: questionId, answer })" in js
    assert "showVerdict" in js
    assert "error_hint" in js
    assert "check-list" in js


def test_only_correct_answer_shows_next() -> None:
    js = _app_js()

    assert "if (next) next.hidden = !result.correct;" in js
    assert "data-step-next" in js
    assert "clearVerdict" in js


def test_answers_survive_navigation() -> None:
    js = _app_js()

    assert "answers: {}" in js
    assert "syncAnswer(question.id, field.value)" in js
    assert "field.value = state.answers[question.id]" in js
    assert "syncAnswer(question.id, button.dataset.value)" in js


def test_final_step_auto_submits_and_renders_summary() -> None:
    js = _app_js()

    assert re.search(r"/api/lessons/\$\{[^}]+\}/submit", js)
    assert "submitLesson()" in js
    assert "Урок пройден" in js
    assert "+${result.xp_gained} XP" in js
    assert "next_lesson" in js
    assert "Следующий урок" in js
    assert "Пройти заново" in js
    assert "refreshDashboard()" in js


def test_example_run_button_is_controlled_by_run_flag() -> None:
    js = _app_js()

    assert "▶ Запустить пример" in js
    assert "card.run !== false" in js
    assert "data-run-example" in js
    assert "/api/code/run" in js


def test_numbering_is_one_based_on_lesson_practice_and_exam() -> None:
    js = _app_js()

    assert "Задание ${number}" in js
    assert "questionTemplate(question, step.questionIndex + 1" in js
    assert "questionTemplate(question, 1)" in js
    assert "questionTemplate(question, index + 1)" in js
    assert "Задание 0" not in js
    assert ".map(questionTemplate)" not in js
    assert "минимум 2 правильных" not in js


def test_bulk_lesson_form_is_gone() -> None:
    js = _app_js()

    assert "Проверить урок" not in js
    assert "lesson-form" not in js
    assert "lesson.questions.map(questionTemplate)" not in js


def test_step_styles_fit_mobile_and_keep_nav_on_one_row() -> None:
    css = _styles()
    blocks = re.findall(r"([^{}]+)\{([^{}]*)\}", css)
    nav = [body for selector, body in blocks if selector.strip().startswith(".step-nav")]

    assert nav
    assert any("display: flex" in body and "flex-wrap: nowrap" in body for body in nav)
    assert any(".step-nav .button[hidden]" in selector for selector, _ in blocks)
    assert re.search(r"@media \(max-width: 760px\)[^{]*\{[^}]*\.step-nav", css)


def test_served_app_js_contains_step_flow_contract() -> None:
    with TestClient(app) as client:
        index = client.get("/")
        script = client.get("/static/app.js")

    assert index.status_code == 200
    assert 'id="view"' in index.text
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
    assert "function renderLesson" in script.text
    assert "Шаг " in script.text
    assert re.search(r"/api/lessons/\$\{[^}]+\}/check", script.text)
    assert re.search(r"/api/lessons/\$\{[^}]+\}/submit", script.text)
