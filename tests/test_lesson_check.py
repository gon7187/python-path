from fastapi.testclient import TestClient

from app.main import app

ALLOWED_KEYS = {"question_id", "correct", "message", "explanation", "checks", "error_hint"}
FORBIDDEN_KEYS = {"answer", "answers", "reference", "tests"}

CORRECT_HELLO = [
    {"question_id": "hello-choice", "answer": "print('Привет')"},
    {"question_id": "hello-term", "answer": "строка"},
    {"question_id": "hello-code", "answer": "print('Я начинаю путь в Python!')"},
]


def _all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for item in value.values() for key in _all_keys(item)}
    if isinstance(value, list):
        return {key for item in value for key in _all_keys(item)}
    return set()


def _check(client: TestClient, question_id: str, answer: str) -> dict:
    response = client.post(
        "/api/lessons/hello/check",
        json={"question_id": question_id, "answer": answer},
    )
    assert response.status_code == 200
    return response.json()


def test_check_choice_returns_verdict_and_explanation() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        correct = _check(client, "hello-choice", "print('Привет')")
        wrong = _check(client, "hello-choice", "text('Привет')")
        client.post("/api/reset")

    assert correct["question_id"] == "hello-choice"
    assert correct["correct"] is True
    assert isinstance(correct["message"], str) and correct["message"]
    assert correct["explanation"]
    assert "checks" not in correct
    assert "error_hint" not in correct

    assert wrong["correct"] is False
    assert wrong["explanation"]


def test_check_input_accepts_known_alternatives() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        russian = _check(client, "hello-term", "строка")
        english = _check(client, "hello-term", "STRING")
        wrong = _check(client, "hello-term", "число")
        client.post("/api/reset")

    assert russian["correct"] is True
    assert english["correct"] is True
    assert wrong["correct"] is False


def test_check_code_returns_checks_for_pass_and_fail() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        passed = _check(client, "hello-code", "print('Я начинаю путь в Python!')")
        failed = _check(client, "hello-code", "print('другое')")
        client.post("/api/reset")

    assert passed["correct"] is True
    assert passed["explanation"]
    assert passed["checks"]
    assert all(item["passed"] is True for item in passed["checks"])

    assert failed["correct"] is False
    assert failed["checks"]
    assert all(item["passed"] is False for item in failed["checks"])
    assert "error_hint" not in failed


def test_check_code_runtime_error_returns_hint() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        response = _check(client, "hello-code", "print(1 / 0)")
        client.post("/api/reset")

    assert response["correct"] is False
    assert response["error_hint"]["title"] == "Деление на ноль"
    assert response["error_hint"]["original"].startswith("ZeroDivisionError:")
    assert response["error_hint"]["hint"]


def test_check_rejects_closed_unknown_and_foreign_question() -> None:
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


def test_check_records_attempt_but_keeps_xp_and_completion_for_submit() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        xp_before = client.get("/api/dashboard").json()["profile"]["xp"]

        wrong = _check(client, "hello-choice", "text('Привет')")
        assert wrong["correct"] is False
        practice = client.get("/api/practice").json()
        assert practice["is_review"] is True
        assert practice["question"]["id"] == "hello-choice"

        for payload in CORRECT_HELLO:
            verdict = _check(client, payload["question_id"], payload["answer"])
            assert verdict["correct"] is True

        dashboard = client.get("/api/dashboard").json()
        assert dashboard["profile"]["xp"] == xp_before
        assert dashboard["completed_lessons"] == 0
        assert dashboard["course"][0]["lessons"][0]["completed"] is False
        assert client.get("/api/lessons/variables").status_code == 403

        submitted = client.post("/api/lessons/hello/submit", json={"answers": CORRECT_HELLO})
        assert submitted.json()["passed"] is True
        assert submitted.json()["xp_gained"] == 35

        after_submit = client.get("/api/dashboard").json()
        assert after_submit["profile"]["xp"] == xp_before + 35
        assert after_submit["completed_lessons"] == 1

        _check(client, "hello-choice", "print('Привет')")
        assert client.get("/api/dashboard").json()["profile"]["xp"] == xp_before + 35
        client.post("/api/reset")


def test_check_response_uses_only_public_fields() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        responses = [
            _check(client, "hello-choice", "print('Привет')"),
            _check(client, "hello-term", "неверно"),
            _check(client, "hello-code", "if True print('Привет')"),
            _check(client, "hello-code", "print('Я начинаю путь в Python!')"),
        ]
        client.post("/api/reset")

    for payload in responses:
        assert set(payload) <= ALLOWED_KEYS
        assert not _all_keys(payload) & FORBIDDEN_KEYS
