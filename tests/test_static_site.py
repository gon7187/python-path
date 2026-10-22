import re

from fastapi.testclient import TestClient

from app.main import app


def _served_js() -> str:
    with TestClient(app) as client:
        response = client.get("/static/app.js")
    assert response.status_code == 200
    return response.text


def test_c9_index_html_is_served_at_root() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'id="view"' in response.text
    assert 'src="/static/app.js"' in response.text


def test_c9_app_js_is_served_as_static_file() -> None:
    with TestClient(app) as client:
        response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "function renderLesson" in response.text


def test_c9_app_js_calls_lesson_check_and_submit_endpoints() -> None:
    js = _served_js()

    assert re.search(r"/api/lessons/\$\{[^}]+\}/check", js)
    assert re.search(r"/api/lessons/\$\{[^}]+\}/submit", js)


def test_c9_app_js_has_step_marker_and_one_based_numbering() -> None:
    js = _served_js()

    assert "Шаг " in js
    assert "Задание ${number}" in js
    assert "Задание 0" not in js
    assert ".map(questionTemplate)" not in js
    assert not re.search(r"questionTemplate\([^)]*,\s*(index|i|idx)\s*\)", js)


def test_c9_app_js_has_no_minimum_two_correct_phrase() -> None:
    js = _served_js()

    assert "минимум 2 правильных" not in js
