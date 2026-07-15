from fastapi.testclient import TestClient

from app.content import EXAM_SOURCE_QUESTION_ID, EXAMS, LESSONS, MODULES, QUESTION_BY_ID
from app.db import save_exam, save_lesson
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
        target_module_index = next(
            index for index, module in enumerate(MODULES) if module["id"] == target["module_id"]
        )
        previous_module = MODULES[target_module_index - 1]
        save_exam(previous_module["id"], 8, 8)

        response = client.get("/api/lessons/operators-arithmetic")
        assert response.status_code == 200
        assert response.json()["order"] == target["order"]

        code_check = client.post(
            "/api/code/check",
            json={
                "question_id": "operators-arithmetic-code",
                "answer": "def subtotal(price, count):\n    return price * count\n",
            },
        )
        assert code_check.status_code == 200
        assert code_check.json()["correct"] is True
        client.post("/api/reset")


def test_editor_runs_code_with_simulated_input() -> None:
    with TestClient(app) as client:
        target = next(lesson for lesson in LESSONS if lesson["id"] == "warmup-input")
        for lesson in LESSONS[: LESSONS.index(target)]:
            total = len(lesson["questions"])
            save_lesson(lesson["id"], total, total, lesson["xp"])
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


def test_public_run_endpoints_hide_internal_execution_phase() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        failing = "raise ValueError('моя ошибка')\n"

        sandbox = client.post("/api/sandbox/run", json={"answer": failing, "inputs": []})
        editor = client.post(
            "/api/code/run",
            json={"question_id": "warmup-route-code", "answer": failing, "inputs": []},
        )
        prerequisite = next(item for item in LESSONS if item["id"] == "warmup-input")
        save_lesson(prerequisite["id"], 3, 3, prerequisite["xp"])
        project = client.post(
            "/api/projects/greeting-card/run", json={"answer": failing, "inputs": []}
        )

        for response in (sandbox, editor, project):
            assert response.status_code == 200
            payload = response.json()
            assert payload["correct"] is False
            assert "error_phase" not in payload
        client.post("/api/reset")


def test_projects_are_progressive_and_run_in_the_sandbox() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        projects = client.get("/api/projects").json()["projects"]
        assert len(projects) == 15
        assert projects[0]["unlocked"] is False
        assert projects[1]["unlocked"] is False

        prerequisite = next(item for item in LESSONS if item["id"] == "warmup-input")
        save_lesson(prerequisite["id"], 3, 3, prerequisite["xp"])

        project = client.get("/api/projects/greeting-card").json()
        assert project["starter"].startswith("name = input")
        assert "tests" not in project
        assert "tool_ids" not in project
        assert "reference_solution" not in project
        assert {tool["name"] for tool in project["tool_help"]} == {
            "input()",
            "f-строка",
            "print()",
        }
        assert "tool_help" not in projects[0]

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
        assert all(
            bool(question["tool_help"]) == (question["kind"] == "code")
            for question in session["questions"]
        )
        assert all("tool_ids" not in question for question in session["questions"])
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


def test_direct_question_endpoints_cannot_skip_locked_lessons_or_award_xp() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        future_id = "strings-pro-search-replace-code"

        practice = client.post(
            "/api/practice/submit",
            json={
                "question_id": future_id,
                "answer": "def normalize_decimal(text):\n    return text\n",
            },
        )
        check = client.post(
            "/api/code/check",
            json={
                "question_id": future_id,
                "answer": "def normalize_decimal(text):\n    return text\n",
            },
        )
        run = client.post(
            "/api/code/run",
            json={"question_id": future_id, "answer": "print('обход')", "inputs": []},
        )

        assert practice.status_code == check.status_code == run.status_code == 403
        assert client.get("/api/dashboard").json()["profile"]["xp"] == 0


def test_code_check_feedback_does_not_expose_hidden_test_oracle() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        response = client.post(
            "/api/code/check",
            json={"question_id": "warmup-route-code", "answer": "print('другой текст')"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["correct"] is False
        assert payload["checks"]
        assert all(set(check) <= {"passed", "kind"} for check in payload["checks"])
        assert "Я готов учиться" not in payload["message"]


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
            elif EXAM_SOURCE_QUESTION_ID[question_id] == "var-code":
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


def test_dashboard_surfaces_required_exam_at_a_module_boundary() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        first_module = MODULES[0]
        module_lessons = [lesson for lesson in LESSONS if lesson["module_id"] == first_module["id"]]
        for lesson in module_lessons:
            total = len(lesson["questions"])
            save_lesson(lesson["id"], total, total, lesson["xp"])

        dashboard = client.get("/api/dashboard").json()
        assert dashboard["next_lesson"] is None
        assert dashboard["next_exam"] == {
            "module_id": first_module["id"],
            "module_title": first_module["title"],
            "title": EXAMS[first_module["id"]]["title"],
        }
        assert dashboard["course"][0]["exam"] == {
            "available": True,
            "passed": False,
            "score": None,
        }

        save_exam(first_module["id"], 8, 8)
        after_exam = client.get("/api/dashboard").json()
        assert after_exam["next_exam"] is None
        assert after_exam["next_lesson"] is not None
        client.post("/api/reset")
