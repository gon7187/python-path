from fastapi.testclient import TestClient

from app.content import LESSONS
from app.db import save_lesson
from app.main import app


def test_lesson_unlocking_and_progression() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        dashboard = client.get("/api/dashboard").json()
        assert dashboard["total_lessons"] == 139
        course = client.get("/api/course").json()
        first_module = course["modules"][0]
        assert first_module["lessons"][0]["unlocked"] is True
        assert first_module["lessons"][1]["unlocked"] is False
        assert client.get("/api/lessons/warmup-print").status_code == 403

        response = client.post(
            "/api/lessons/warmup-route/submit",
            json={
                "answers": [
                    {
                        "question_id": "warmup-route-choice",
                        "answer": "Пример → повтор → маленькая практика",
                    },
                    {"question_id": "warmup-route-term", "answer": "print"},
                    {
                        "question_id": "warmup-route-code",
                        "answer": "print('Я готов учиться')",
                    },
                ]
            },
        )
        result = response.json()
        assert response.status_code == 200
        assert result["passed"] is True
        assert result["xp_gained"] == 12
        assert client.get("/api/lessons/warmup-print").status_code == 200
        client.post("/api/reset")


def test_extended_course_unlocks_after_foundation() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        target = next(lesson for lesson in LESSONS if lesson["id"] == "operators-arithmetic")
        target_index = LESSONS.index(target)
        for lesson in LESSONS[:target_index]:
            save_lesson(lesson["id"], 3, 3, lesson["xp"])

        response = client.get("/api/lessons/operators-arithmetic")
        assert response.status_code == 200
        assert response.json()["order"] == target["order"]

        code_check = client.post(
            "/api/code/check",
            json={
                "question_id": "operators-arithmetic-code",
                "answer": "def increment(value):\n    return value + 1\n",
            },
        )
        assert code_check.status_code == 200
        assert code_check.json()["correct"] is True
        client.post("/api/reset")
