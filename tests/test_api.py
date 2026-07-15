from fastapi.testclient import TestClient

from app.content import EXAMS, LESSONS, QUESTION_BY_ID
from app.db import save_lesson
from app.main import app


def test_lesson_unlocking_and_progression() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        dashboard = client.get("/api/dashboard").json()
        assert dashboard["total_lessons"] == 151
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
            total = len(lesson["questions"])
            save_lesson(lesson["id"], total, total, lesson["xp"])

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
        assert projects[0]["unlocked"] is False
        assert projects[1]["unlocked"] is False

        prerequisite = next(item for item in LESSONS if item["id"] == "warmup-input")
        save_lesson(prerequisite["id"], 3, 3, prerequisite["xp"])

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
        assert all(item["correct"] for item in submission["scenarios"])
        assert submission["xp_gained"] == 25

        hardcoded = client.post(
            "/api/projects/greeting-card/submit",
            json={"answer": "input('Имя: ')\nprint('Привет, Лена!')\n"},
        ).json()
        assert hardcoded["correct"] is False
        client.post("/api/reset")


def test_practice_sessions_are_guided_and_repeat_errors() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")

        session = client.get("/api/practice/session?mode=guided").json()
        assert session["title"] == "Пробный первый шаг"
        assert [question["kind"] for question in session["questions"]] == [
            "choice",
            "input",
            "code",
        ]
        assert all(question["guide"] for question in session["questions"])
        assert session["available_modules"][0]["id"] == "gentle-start"

        first = LESSONS[0]
        save_lesson(first["id"], 3, 3, first["xp"])

        client.post(
            "/api/practice/submit",
            json={"question_id": "warmup-route-choice", "answer": "неверный ответ"},
        )
        review = client.get("/api/practice/session?mode=review").json()
        assert review["title"] == "Повторяем ошибки"
        assert review["questions"][0]["id"] == "warmup-route-choice"

        for _ in range(2):
            client.post(
                "/api/practice/submit",
                json={
                    "question_id": "warmup-route-choice",
                    "answer": "Пример → повтор → маленькая практика",
                },
            )
        repaired = client.get("/api/practice/session?mode=review").json()
        assert repaired["title"] == "Чистое повторение"

        module_session = client.get(
            "/api/practice/session?mode=module&module_id=gentle-start"
        ).json()
        assert module_session["title"].startswith("Тема:")
        assert {question["lesson_title"] for question in module_session["questions"]} == {
            "Как проходить урок"
        }
        client.post("/api/reset")


def test_lesson_cannot_pass_by_skipping_mandatory_code() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        response = client.post(
            "/api/lessons/warmup-route/submit",
            json={
                "answers": [
                    {
                        "question_id": "warmup-route-choice",
                        "answer": "Пример → повтор → маленькая практика",
                    },
                    {"question_id": "warmup-route-term", "answer": "print"},
                    {"question_id": "warmup-route-code", "answer": ""},
                ]
            },
        ).json()
        assert response["correct_count"] == 2
        assert response["mandatory_passed"] is False
        assert response["passed"] is False


def test_exam_requires_practical_questions_even_above_score_threshold() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        for lesson in (item for item in LESSONS if item["module_id"] == "start"):
            total = len(lesson["questions"])
            save_lesson(lesson["id"], total, total, lesson["xp"])

        exam = EXAMS["start"]
        answers = []
        for question_id in exam["question_ids"]:
            question = QUESTION_BY_ID[question_id]
            if question["kind"] == "choice":
                answer = question["answer"]
            elif question["kind"] == "input":
                answer = question["answers"][0]
            elif question_id == "var-code":
                answer = "city = 'Казань'\nprint(f'Город: {city}')\n"
            else:
                answer = ""
            answers.append({"question_id": question_id, "answer": answer})

        result = client.post("/api/exams/start/submit", json={"answers": answers}).json()
        assert result["correct_count"] == 5
        assert result["mandatory_passed"] is False
        assert result["passed"] is False


def test_module_practice_interleaves_completed_lessons() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        for lesson in LESSONS[:3]:
            total = len(lesson["questions"])
            save_lesson(lesson["id"], total, total, lesson["xp"])
        session = client.get(
            "/api/practice/session?mode=module&module_id=gentle-start&limit=6"
        ).json()
        assert len({question["lesson_title"] for question in session["questions"]}) > 1


def test_legacy_progress_continues_past_new_gentle_start() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        for lesson_id in ("hello", "variables"):
            lesson = next(item for item in LESSONS if item["id"] == lesson_id)
            save_lesson(lesson_id, 2, 3, lesson["xp"])

        dashboard = client.get("/api/dashboard").json()
        assert dashboard["next_lesson"]["id"] == "strings-input"
        client.post("/api/reset")
