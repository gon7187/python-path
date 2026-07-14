"""HTTP API and static-site entrypoint for Python Path."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.content import (
    EXAMS,
    LESSON_BY_ID,
    LESSONS,
    MODULES,
    QUESTION_BY_ID,
    public_lesson,
    public_question,
)
from app.db import DATABASE_PATH, connection, init_db, record_attempt, save_exam, save_lesson, state
from app.evaluator import evaluate

APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Python Path", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class Answer(BaseModel):
    question_id: str
    answer: Any = ""


class Submission(BaseModel):
    answers: list[Answer]


class CodeCheck(BaseModel):
    question_id: str
    answer: str


def status_for(lesson: dict, saved: dict) -> dict:
    index = next(index for index, item in enumerate(LESSONS) if item["id"] == lesson["id"])
    completed = lesson["id"] in saved
    previous_done = index == 0 or LESSONS[index - 1]["id"] in saved
    return {
        "completed": completed,
        "unlocked": completed or previous_done,
        "stars": saved.get(lesson["id"], {}).get("stars", 0),
    }


def course_payload() -> dict:
    snapshot = state()
    module_payloads = []
    for module in MODULES:
        module_lessons = [item for item in LESSONS if item["module_id"] == module["id"]]
        lessons = [
            {**public_lesson(item), **status_for(item, snapshot["lessons"])}
            for item in module_lessons
        ]
        complete_count = sum(item["completed"] for item in lessons)
        exam = snapshot["exams"].get(module["id"])
        module_payloads.append(
            {
                **module,
                "lessons": lessons,
                "completed": complete_count,
                "total": len(lessons),
                "exam": {
                    "available": complete_count == len(lessons),
                    "passed": bool(exam and exam["score"] / exam["total_count"] >= 0.7),
                    "score": exam["score"] if exam else None,
                },
            }
        )
    return {"modules": module_payloads}


def dashboard_payload() -> dict:
    snapshot = state()
    course = course_payload()
    completed = len(snapshot["lessons"])
    total = len(LESSONS)
    next_lesson = next(
        (
            item
            for item in LESSONS
            if status_for(item, snapshot["lessons"])["unlocked"]
            and item["id"] not in snapshot["lessons"]
        ),
        None,
    )
    achievements = [
        {
            "id": "first",
            "icon": "🌱",
            "title": "Первые шаги",
            "description": "Заверши первый урок",
            "unlocked": completed >= 1,
        },
        {
            "id": "trio",
            "icon": "⚡",
            "title": "Разогрев",
            "description": "Заверши 3 урока",
            "unlocked": completed >= 3,
        },
        {
            "id": "streak",
            "icon": "🔥",
            "title": "В ритме",
            "description": "Учись 3 дня подряд",
            "unlocked": snapshot["profile"]["streak"] >= 3,
        },
        {
            "id": "final",
            "icon": "🏁",
            "title": "Python-старт",
            "description": "Сдай финальный экзамен",
            "unlocked": bool(snapshot["exams"].get("realworld")),
        },
    ]
    return {
        "profile": snapshot["profile"],
        "completed_lessons": completed,
        "total_lessons": total,
        "progress_percent": round(completed / total * 100),
        "next_lesson": public_lesson(next_lesson) if next_lesson else None,
        "achievements": achievements,
        "course": course["modules"],
    }


def require_lesson(lesson_id: str) -> dict:
    lesson = LESSON_BY_ID.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    if not status_for(lesson, state()["lessons"])["unlocked"]:
        raise HTTPException(status_code=403, detail="Сначала заверши предыдущий урок")
    return lesson


def grade_answers(items: list[Answer], allowed_ids: set[str]) -> tuple[list[dict], int]:
    provided = {item.question_id: item.answer for item in items if item.question_id in allowed_ids}
    results = []
    correct_count = 0
    for question_id in allowed_ids:
        result = evaluate(QUESTION_BY_ID[question_id], provided.get(question_id, ""))
        record_attempt(question_id, result["correct"])
        correct_count += int(result["correct"])
        results.append({"question_id": question_id, **result})
    return results, correct_count


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/dashboard")
def dashboard() -> dict:
    return dashboard_payload()


@app.get("/api/course")
def course() -> dict:
    return course_payload()


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: str) -> dict:
    return public_lesson(require_lesson(lesson_id), include_questions=True)


@app.post("/api/lessons/{lesson_id}/submit")
def submit_lesson(lesson_id: str, submission: Submission) -> dict:
    lesson = require_lesson(lesson_id)
    question_ids = {question["id"] for question in lesson["questions"]}
    results, correct_count = grade_answers(submission.answers, question_ids)
    total = len(question_ids)
    passed = correct_count >= 2
    gained = 0
    if passed:
        gained, _ = save_lesson(lesson_id, correct_count, total, lesson["xp"])
    return {
        "passed": passed,
        "correct_count": correct_count,
        "total_count": total,
        "xp_gained": gained,
        "results": results,
        "message": "Урок пройден! Новый урок уже открыт."
        if passed
        else "Нужно минимум 2 верных ответа из 3. Попробуй ещё раз — это нормально.",
    }


@app.get("/api/practice")
def practice() -> dict:
    snapshot = state()
    candidate_ids = [item for item in snapshot["weak_question_ids"] if item in QUESTION_BY_ID]
    if not candidate_ids:
        candidate_ids = [
            question["id"]
            for item in LESSONS
            if status_for(item, snapshot["lessons"])["unlocked"]
            for question in item["questions"]
        ]
    if not candidate_ids:
        candidate_ids = [question["id"] for question in LESSONS[0]["questions"]]
    question = QUESTION_BY_ID[candidate_ids[0]]
    source = next(item for item in LESSONS if question in item["questions"])
    return {
        "question": public_question(question),
        "lesson_title": source["title"],
        "is_review": question["id"] in snapshot["weak_question_ids"],
    }


@app.post("/api/practice/submit")
def submit_practice(answer: Answer) -> dict:
    question = QUESTION_BY_ID.get(answer.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    result = evaluate(question, answer.answer)
    record_attempt(answer.question_id, result["correct"])
    gained = 5 if result["correct"] else 0
    if gained:
        with connection() as conn:
            conn.execute("UPDATE profile SET xp = xp + ? WHERE id = 1", (gained,))
    return {"xp_gained": gained, **result}


@app.post("/api/code/check")
def check_code(payload: CodeCheck) -> dict:
    question = QUESTION_BY_ID.get(payload.question_id)
    if not question or question["kind"] != "code":
        raise HTTPException(status_code=404, detail="Кодовое задание не найдено")
    return evaluate(question, payload.answer)


@app.get("/api/exams/{module_id}")
def get_exam(module_id: str) -> dict:
    exam = EXAMS.get(module_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Экзамен не найден")
    module_lessons = [item for item in LESSONS if item["module_id"] == module_id]
    saved = state()["lessons"]
    if not all(item["id"] in saved for item in module_lessons):
        raise HTTPException(status_code=403, detail="Экзамен откроется после всех уроков раздела")
    return {
        "module_id": module_id,
        "title": exam["title"],
        "description": exam["description"],
        "questions": [public_question(QUESTION_BY_ID[item]) for item in exam["question_ids"]],
    }


@app.post("/api/exams/{module_id}/submit")
def submit_exam(module_id: str, submission: Submission) -> dict:
    get_exam(module_id)
    exam = EXAMS[module_id]
    question_ids = set(exam["question_ids"])
    results, score = grade_answers(submission.answers, question_ids)
    total = len(question_ids)
    passed = score / total >= 0.7
    gained = save_exam(module_id, score, total) if passed else 0
    return {
        "passed": passed,
        "correct_count": score,
        "total_count": total,
        "xp_gained": gained,
        "results": results,
        "message": "Экзамен сдан! Раздел закреплён."
        if passed
        else "Пока не хватило 70%. Повтори ошибки в практике и возвращайся.",
    }


@app.post("/api/reset")
def reset_progress() -> dict:
    with connection() as conn:
        conn.execute("DELETE FROM lesson_progress")
        conn.execute("DELETE FROM attempts")
        conn.execute("DELETE FROM exam_progress")
        conn.execute("UPDATE profile SET xp = 0, streak = 0, last_activity = NULL WHERE id = 1")
    return {"ok": True}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "database": str(DATABASE_PATH.name)}
