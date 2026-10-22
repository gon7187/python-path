import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.content import LESSONS, QUESTION_BY_ID, public_question
from app.db import save_lesson
from app.evaluator import evaluate
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[1]
CHOICE_ORDER_SCRIPT = (
    "import json\n"
    "from app.content import QUESTION_BY_ID, public_question\n"
    "orders = {\n"
    "    qid: public_question(question)['options']\n"
    "    for qid, question in QUESTION_BY_ID.items()\n"
    "    if question['kind'] == 'choice'\n"
    "}\n"
    "print(json.dumps(orders, ensure_ascii=False))\n"
)


def _choice_questions() -> list[dict]:
    return [question for question in QUESTION_BY_ID.values() if question["kind"] == "choice"]


def test_c1_public_choice_options_are_a_deterministic_permutation() -> None:
    questions = _choice_questions()
    assert questions, "в курсе нет вопросов с выбором"
    for question in questions:
        original = list(question["options"])
        first = public_question(question)["options"]
        second = public_question(question)["options"]
        assert first == second, question["id"]
        assert sorted(first) == sorted(original), question["id"]
        assert question["options"] == original, question["id"]
    assert any(
        public_question(question)["options"] != question["options"] for question in questions
    )


def test_c1_choice_order_is_stable_across_processes() -> None:
    outputs = []
    for hash_seed in ("0", "1"):
        result = subprocess.run(
            [sys.executable, "-c", CHOICE_ORDER_SCRIPT],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONHASHSEED": hash_seed},
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1]


def test_c2_correct_option_is_first_in_at_most_half_of_choice_questions() -> None:
    questions = _choice_questions()
    assert questions, "в курсе нет вопросов с выбором"
    first_is_correct = [
        question["id"]
        for question in questions
        if public_question(question)["options"][0] == question["answer"]
    ]
    assert len(first_is_correct) * 2 <= len(questions), (
        f"верный вариант первый в {len(first_is_correct)} из {len(questions)} вопросов"
    )


def test_c3_evaluator_accepts_only_the_correct_value_in_any_position() -> None:
    for question in _choice_questions():
        for option in public_question(question)["options"]:
            correct = evaluate(question, option)["correct"]
            assert correct is (option == question["answer"]), (question["id"], option)


def test_c3_lesson_check_and_submit_grade_choice_by_value() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        lesson = client.get("/api/lessons/hello").json()
        choice = next(question for question in lesson["questions"] if question["kind"] == "choice")
        correct_value = QUESTION_BY_ID[choice["id"]]["answer"]
        wrong_value = next(option for option in choice["options"] if option != correct_value)

        right = client.post(
            "/api/lessons/hello/check",
            json={"question_id": choice["id"], "answer": correct_value},
        )
        wrong = client.post(
            "/api/lessons/hello/check",
            json={"question_id": choice["id"], "answer": wrong_value},
        )
        assert right.json()["correct"] is True
        assert wrong.json()["correct"] is False

        submitted = client.post(
            "/api/lessons/hello/submit",
            json={
                "answers": [
                    {"question_id": choice["id"], "answer": correct_value},
                    {"question_id": "hello-term", "answer": "строка"},
                    {"question_id": "hello-code", "answer": "print('Я начинаю путь в Python!')"},
                ]
            },
        ).json()
        results = {item["question_id"]: item["correct"] for item in submitted["results"]}
        assert results[choice["id"]] is True
        client.post("/api/reset")


def test_c3_exam_grades_choice_by_value() -> None:
    module_id = "start"
    with TestClient(app) as client:
        client.post("/api/reset")
        for lesson in LESSONS:
            if lesson["module_id"] == module_id:
                save_lesson(lesson["id"], 3, 3, lesson["xp"])

        exam = client.get(f"/api/exams/{module_id}").json()
        choices = [question for question in exam["questions"] if question["kind"] == "choice"]
        assert choices, "в экзамене нет вопросов с выбором"
        answers = []
        for question in choices:
            answers.append(
                {"question_id": question["id"], "answer": QUESTION_BY_ID[question["id"]]["answer"]}
            )
        submitted = client.post(f"/api/exams/{module_id}/submit", json={"answers": answers}).json()
        results = {item["question_id"]: item["correct"] for item in submitted["results"]}
        for question in choices:
            assert results[question["id"]] is True, question["id"]
        client.post("/api/reset")
