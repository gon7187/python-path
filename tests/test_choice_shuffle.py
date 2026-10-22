import random

from fastapi.testclient import TestClient

from app.content import EXAMS, LESSONS, QUESTION_BY_ID, public_question
from app.db import save_lesson
from app.main import app


def _choice_questions() -> list[dict]:
    return [question for question in QUESTION_BY_ID.values() if question["kind"] == "choice"]


def test_public_choice_options_follow_the_declared_deterministic_shuffle() -> None:
    questions = _choice_questions()
    assert questions, "в курсе нет вопросов с выбором"
    for question in questions:
        original = list(question["options"])
        expected = list(original)
        random.Random(question["id"]).shuffle(expected)

        first = public_question(question)["options"]
        second = public_question(question)["options"]

        assert first == expected, question["id"]
        assert first == second, question["id"]
        assert sorted(first) == sorted(original), question["id"]
        assert question["options"] == original, question["id"]


def test_non_choice_payloads_are_not_touched() -> None:
    for question in QUESTION_BY_ID.values():
        if question["kind"] == "choice":
            continue
        payload = public_question(question)
        for key, value in question.items():
            if key in {"answer", "answers", "tests", "reference"}:
                assert key not in payload, question["id"]
            else:
                assert payload[key] == value, (question["id"], key)


def test_lesson_and_exam_endpoints_expose_the_shuffled_order() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        for lesson in LESSONS:
            save_lesson(lesson["id"], 3, 3, lesson["xp"])

        first_is_correct = 0
        total = 0
        for lesson in LESSONS:
            payload = client.get(f"/api/lessons/{lesson['id']}").json()
            for question in payload["questions"]:
                if question["kind"] != "choice":
                    continue
                total += 1
                source = QUESTION_BY_ID[question["id"]]
                assert question["options"] == public_question(source)["options"], question["id"]
                if question["options"][0] == source["answer"]:
                    first_is_correct += 1

        assert total == len(_choice_questions())
        assert first_is_correct * 2 <= total, (
            f"верный вариант первый в {first_is_correct} из {total} вопросов"
        )

        for module_id, exam in EXAMS.items():
            for lesson in LESSONS:
                if lesson["module_id"] == module_id:
                    save_lesson(lesson["id"], 3, 3, lesson["xp"])
            payload = client.get(f"/api/exams/{module_id}").json()
            assert payload["questions"], module_id
            for question in payload["questions"]:
                if question["kind"] != "choice":
                    continue
                source = QUESTION_BY_ID[question["id"]]
                assert question["options"] == public_question(source)["options"], question["id"]

        client.post("/api/reset")
