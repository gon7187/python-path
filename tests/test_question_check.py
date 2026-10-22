from fastapi.testclient import TestClient

from app.main import app

FORBIDDEN_KEYS = {"answer", "answers", "reference", "tests"}


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for item in value.values() for key in _all_keys(item)}
    if isinstance(value, list):
        return {key for item in value for key in _all_keys(item)}
    return set()


def test_c1_check_returns_verdict_explanation_and_error_hint() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        correct = client.post(
            "/api/lessons/hello/check",
            json={"question_id": "hello-choice", "answer": "print('Привет')"},
        )
        wrong = client.post(
            "/api/lessons/hello/check",
            json={"question_id": "hello-term", "answer": "неверно"},
        )
        broken_code = client.post(
            "/api/lessons/hello/check",
            json={"question_id": "hello-code", "answer": "if True print('Привет')"},
        )
        client.post("/api/reset")

    assert correct.status_code == 200
    assert correct.json()["question_id"] == "hello-choice"
    assert correct.json()["correct"] is True
    assert isinstance(correct.json()["message"], str)
    assert correct.json()["explanation"]

    assert wrong.status_code == 200
    assert wrong.json()["question_id"] == "hello-term"
    assert wrong.json()["correct"] is False
    assert wrong.json()["explanation"]

    assert broken_code.status_code == 200
    assert broken_code.json()["correct"] is False
    assert broken_code.json()["error_hint"]["title"] == "Синтаксическая ошибка"
    assert broken_code.json()["error_hint"]["original"].startswith("SyntaxError:")


def test_c2_check_rejects_closed_lesson_and_unknown_ids() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        closed = client.post(
            "/api/lessons/variables/check",
            json={"question_id": "variables-term", "answer": "переменная"},
        )
        unknown_lesson = client.post(
            "/api/lessons/no-such-lesson/check",
            json={"question_id": "hello-choice", "answer": "print('Привет')"},
        )
        foreign_question = client.post(
            "/api/lessons/hello/check",
            json={"question_id": "variables-term", "answer": "переменная"},
        )
        client.post("/api/reset")

    assert closed.status_code == 403
    assert unknown_lesson.status_code == 404
    assert foreign_question.status_code == 404


def test_c3_check_records_attempt_without_xp_or_completion() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        xp_before = client.get("/api/dashboard").json()["profile"]["xp"]

        wrong = client.post(
            "/api/lessons/hello/check",
            json={"question_id": "hello-choice", "answer": "text('Привет')"},
        )
        assert wrong.status_code == 200
        assert wrong.json()["correct"] is False
        practice = client.get("/api/practice").json()
        assert practice["is_review"] is True
        assert practice["question"]["id"] == "hello-choice"

        all_correct = [
            {"question_id": "hello-choice", "answer": "print('Привет')"},
            {"question_id": "hello-term", "answer": "строка"},
            {"question_id": "hello-code", "answer": "print('Я начинаю путь в Python!')"},
        ]
        for payload in all_correct:
            response = client.post("/api/lessons/hello/check", json=payload)
            assert response.status_code == 200
            assert response.json()["correct"] is True

        dashboard = client.get("/api/dashboard").json()
        assert dashboard["profile"]["xp"] == xp_before
        assert dashboard["completed_lessons"] == 0
        assert dashboard["course"][0]["lessons"][0]["completed"] is False

        submitted = client.post("/api/lessons/hello/submit", json={"answers": all_correct})
        assert submitted.json()["passed"] is True
        assert client.get("/api/dashboard").json()["completed_lessons"] == 1
        client.post("/api/reset")


def test_c4_check_response_hides_solution() -> None:
    payloads = [
        {"question_id": "hello-choice", "answer": "print('Привет')"},
        {"question_id": "hello-term", "answer": "неверно"},
        {"question_id": "hello-code", "answer": "if True print('Привет')"},
        {"question_id": "hello-code", "answer": "print('Я начинаю путь в Python!')"},
    ]
    with TestClient(app) as client:
        client.post("/api/reset")
        responses = [client.post("/api/lessons/hello/check", json=payload) for payload in payloads]
        client.post("/api/reset")

    for response in responses:
        assert response.status_code == 200
        assert not _all_keys(response.json()) & FORBIDDEN_KEYS
