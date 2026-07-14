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


def test_editor_runs_code_with_simulated_input() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/code/run",
            json={
                "question_id": "warmup-input-code",
                "answer": "name = input('Имя: ')\nprint(f'Привет, {name}!')\n",
                "inputs": ["Мира"],
            },
        )
        result = response.json()
        assert response.status_code == 200
        assert result["correct"] is True
        assert result["output"] == "Имя: Мира\nПривет, Мира!\n"


def test_free_sandbox_runs_code_without_a_lesson_question() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/sandbox/run",
            json={
                "answer": "name = input('Имя: ')\nprint(name.upper())\n",
                "inputs": ["мира"],
            },
        )
        result = response.json()
        assert response.status_code == 200
        assert result["correct"] is True
        assert result["output"] == "Имя: мира\nМИРА\n"


def test_projects_are_progressive_and_run_in_the_sandbox() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        projects = client.get("/api/projects").json()["projects"]
        assert len(projects) == 6
        assert projects[0]["unlocked"] is True
        assert projects[1]["unlocked"] is False

        project = client.get("/api/projects/greeting-card").json()
        assert project["starter"].startswith("name = input")
        assert "tests" not in project

        source = "name = input('Имя: ')\nprint(f'Привет, {name}!')\n"
        run = client.post(
            "/api/projects/greeting-card/run",
            json={"answer": source, "inputs": ["Мира"]},
        ).json()
        assert run["correct"] is True
        assert run["output"] == "Имя: Мира\nПривет, Мира!\n"

        submission = client.post(
            "/api/projects/greeting-card/submit", json={"answer": source}
        ).json()
        assert submission["correct"] is True
        assert submission["xp_gained"] == 25
        client.post("/api/reset")


def test_practice_sessions_are_guided_and_repeat_errors() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")

        session = client.get("/api/practice/session?mode=guided").json()
        assert session["title"] == "По текущему шагу"
        assert [question["kind"] for question in session["questions"]] == [
            "choice",
            "input",
            "code",
        ]
        assert all(question["guide"] for question in session["questions"])
        assert session["available_modules"][0]["id"] == "gentle-start"

        client.post(
            "/api/practice/submit",
            json={"question_id": "warmup-route-choice", "answer": "неверный ответ"},
        )
        review = client.get("/api/practice/session?mode=review").json()
        assert review["title"] == "Повторяем ошибки"
        assert review["questions"][0]["id"] == "warmup-route-choice"

        module_session = client.get(
            "/api/practice/session?mode=module&module_id=gentle-start"
        ).json()
        assert module_session["title"].startswith("Тема:")
        assert {question["lesson_title"] for question in module_session["questions"]} == {
            "Как проходить урок"
        }
        client.post("/api/reset")


def test_legacy_progress_continues_past_new_gentle_start() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        for lesson_id in ("hello", "variables"):
            lesson = next(item for item in LESSONS if item["id"] == lesson_id)
            save_lesson(lesson_id, 2, 3, lesson["xp"])

        dashboard = client.get("/api/dashboard").json()
        assert dashboard["next_lesson"]["id"] == "strings-input"
        client.post("/api/reset")
