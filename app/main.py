"""HTTP API and static-site entrypoint for Python Path."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from math import ceil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
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
from app.db import (
    DATABASE_PATH,
    connection,
    init_db,
    record_attempt,
    save_exam,
    save_lesson,
    save_project,
    state,
)
from app.evaluator import evaluate, run_code
from app.learning_design import REVIEW_INTERVALS_DAYS
from app.projects import PROJECT_BY_ID, PROJECTS, public_project

APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Python Path", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

QUESTION_LESSON = {question["id"]: lesson for lesson in LESSONS for question in lesson["questions"]}
CONCEPT_LESSON_ID: dict[str, str] = {}
for curriculum_lesson in LESSONS:
    for curriculum_concept in curriculum_lesson["concepts"]:
        CONCEPT_LESSON_ID.setdefault(curriculum_concept, curriculum_lesson["id"])


class Answer(BaseModel):
    question_id: str
    answer: Any = ""


class Submission(BaseModel):
    answers: list[Answer]


class CodeCheck(BaseModel):
    question_id: str
    answer: str


class CodeRun(CodeCheck):
    inputs: list[str] = []


class ProjectSubmission(BaseModel):
    answer: str


class ProjectRun(ProjectSubmission):
    inputs: list[str] = []


class SandboxRun(ProjectRun):
    """Свободный запуск в той же безопасной среде, что задания и проекты."""


def status_for(lesson: dict, saved: dict) -> dict:
    index = next(index for index, item in enumerate(LESSONS) if item["id"] == lesson["id"])
    completed = lesson["id"] in saved
    previous_done = index == 0 or LESSONS[index - 1]["id"] in saved
    prerequisite_lesson_ids = {
        CONCEPT_LESSON_ID[concept]
        for concept in lesson["prerequisites"]
        if concept in CONCEPT_LESSON_ID
    }
    prerequisites_done = all(lesson_id in saved for lesson_id in prerequisite_lesson_ids)
    return {
        "completed": completed,
        "unlocked": completed or (previous_done and prerequisites_done),
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


def next_lesson_for(snapshot: dict) -> dict | None:
    """Выбирает продолжение, не отправляя старого ученика в новый вводный блок."""
    unlocked = [
        item
        for item in LESSONS
        if status_for(item, snapshot["lessons"])["unlocked"]
        and item["id"] not in snapshot["lessons"]
    ]
    if not unlocked:
        return None

    has_legacy_progress = any(
        lesson["module_id"] != "gentle-start" and lesson["id"] in snapshot["lessons"]
        for lesson in LESSONS
    )
    has_gentle_start_progress = any(
        lesson["module_id"] == "gentle-start" and lesson["id"] in snapshot["lessons"]
        for lesson in LESSONS
    )
    if has_legacy_progress and not has_gentle_start_progress:
        legacy_unlocked = [item for item in unlocked if item["module_id"] != "gentle-start"]
        if legacy_unlocked:
            return legacy_unlocked[0]
    return unlocked[0]


def dashboard_payload() -> dict:
    snapshot = state()
    course = course_payload()
    completed = len(snapshot["lessons"])
    total = len(LESSONS)
    next_lesson = next_lesson_for(snapshot)
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


def grade_answers(items: list[Answer], allowed_ids: list[str]) -> tuple[list[dict], int]:
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
    lesson = require_lesson(lesson_id)
    payload = public_lesson(lesson, include_questions=True)
    total = len(lesson["questions"])
    payload["pass_requirements"] = {
        "required_correct": max(2, ceil(total * 0.65)),
        "mandatory_question_ids": [
            question["id"] for question in lesson["questions"] if question.get("mandatory")
        ],
    }
    return payload


@app.post("/api/lessons/{lesson_id}/submit")
def submit_lesson(lesson_id: str, submission: Submission) -> dict:
    lesson = require_lesson(lesson_id)
    question_ids = [question["id"] for question in lesson["questions"]]
    results, correct_count = grade_answers(submission.answers, question_ids)
    total = len(question_ids)
    required_correct = max(2, ceil(total * 0.65))
    result_by_id = {result["question_id"]: result for result in results}
    mandatory_ids = [
        question["id"] for question in lesson["questions"] if question.get("mandatory")
    ]
    mandatory_passed = all(result_by_id[question_id]["correct"] for question_id in mandatory_ids)
    passed = correct_count >= required_correct and mandatory_passed
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
        else (
            f"Нужно решить обязательную практику и набрать {required_correct} из {total}. "
            "Посмотри вывод кода, исправь один шаг и попробуй снова."
        ),
        "required_correct": required_correct,
        "mandatory_passed": mandatory_passed,
    }


def available_practice_lessons(snapshot: dict) -> list[dict]:
    """Normal practice only contains completed lessons, never the next open topic."""
    return [lesson for lesson in LESSONS if lesson["id"] in snapshot["lessons"]]


def current_practice_lesson(lessons: list[dict], snapshot: dict) -> dict:
    del snapshot
    return lessons[-1]


def practice_modules(lessons: list[dict]) -> list[dict]:
    lesson_module_ids = {lesson["module_id"] for lesson in lessons}
    return [
        {"id": module["id"], "title": module["title"], "icon": module["icon"]}
        for module in MODULES
        if module["id"] in lesson_module_ids
    ]


def _practice_priority(question: dict, snapshot: dict) -> tuple[int, float, int, str]:
    """Due/weak questions first, then least practiced and least recently seen."""
    stats = snapshot["question_stats"].get(question["id"], {})
    total_attempts = int(stats.get("total_attempts", 0))
    streak = int(stats.get("correct_streak", 0))
    interval = REVIEW_INTERVALS_DAYS[min(streak, len(REVIEW_INTERVALS_DAYS) - 1)]
    last_raw = stats.get("last_attempt_at")
    if last_raw:
        last = datetime.fromisoformat(last_raw)
        due_at = last + timedelta(days=interval)
        overdue_seconds = (datetime.now(UTC) - due_at).total_seconds()
        due_rank = 0 if overdue_seconds >= 0 else 1
    else:
        overdue_seconds = float("inf")
        due_rank = 0
    weak_rank = 0 if question["id"] in snapshot["weak_question_ids"] else 1
    return (weak_rank + due_rank, -overdue_seconds, total_attempts, last_raw or "")


def _mixed_selection(questions: list[dict], limit: int, snapshot: dict) -> list[dict]:
    """Interleave formats and rotate ties instead of returning question zero forever."""
    if not questions:
        return []
    ranked = sorted(questions, key=lambda item: _practice_priority(item, snapshot))
    total_attempts = sum(
        int(snapshot["question_stats"].get(item["id"], {}).get("total_attempts", 0))
        for item in questions
    )
    kinds = ("choice", "input", "parsons", "code")
    selected: list[dict] = []
    for kind in kinds:
        candidates = [item for item in ranked if item["kind"] == kind]
        if candidates:
            selected.append(candidates[total_attempts % len(candidates)])
        if len(selected) >= limit:
            return selected
    selected.extend(item for item in ranked if item not in selected)
    return selected[:limit]


def practice_questions(
    mode: str, module_id: str | None, limit: int, snapshot: dict
) -> tuple[list[dict], str, str, str]:
    """Собирает небольшую осмысленную серию вместо случайного одиночного вопроса."""
    completed_lessons = available_practice_lessons(snapshot)
    # Before the first completion, guided mode doubles as the first-lesson onboarding.
    lessons = completed_lessons or ([LESSONS[0]] if mode == "guided" else [])
    if not lessons:
        raise HTTPException(status_code=409, detail="Сначала заверши первый урок маршрута")
    current = current_practice_lesson(lessons, snapshot)
    all_questions = [question for lesson in lessons for question in lesson["questions"]]

    if mode == "guided":
        questions = current["questions"]
        return (
            questions[:limit],
            "Закрепляем последний урок" if completed_lessons else "Пробный первый шаг",
            f"Закрепляем уже изученную тему «{current['title']}»: вспомнить, восстановить и применить.",
            "Сначала опирайся на пример из урока. В этой серии не будет ничего из будущих тем.",
        )

    if mode == "review":
        weak_ids = set(snapshot["weak_question_ids"])
        weak = [question for question in all_questions if question["id"] in weak_ids]
        if weak:
            filler = sorted(
                (question for question in all_questions if question not in weak),
                key=lambda item: _practice_priority(item, snapshot),
            )
            return (
                (weak + filler)[:limit],
                "Повторяем ошибки",
                "Здесь только уже встречавшиеся сложные места. Ошибка — повод потренировать навык, а не оценка.",
                "Прочитай план к каждому заданию и решай его заново, не пытаясь вспомнить прежний ответ.",
            )
        return (
            _mixed_selection(all_questions, limit, snapshot),
            "Чистое повторение",
            "Пока нет ошибок для разбора — закрепим текущий шаг без спешки.",
            "После первых ошибок этот режим будет подбирать их автоматически.",
        )

    if mode == "mixed":
        questions = _mixed_selection(all_questions, limit, snapshot)
        return (
            questions,
            "Смешанная серия",
            "Небольшая серия из уже открытых тем: сначала вспомни правило, потом назови его и примени в коде.",
            "Темы могут отличаться, но каждая уже есть в твоём маршруте. Не спеши и читай план задания.",
        )

    if mode == "module":
        if not module_id:
            raise HTTPException(status_code=422, detail="Выбери тему для тренировки")
        module_lessons = [lesson for lesson in lessons if lesson["module_id"] == module_id]
        if not module_lessons:
            raise HTTPException(status_code=403, detail="Эта тема ещё не открыта в маршруте")
        module = next(item for item in MODULES if item["id"] == module_id)
        return (
            _mixed_selection(
                [question for lesson in module_lessons for question in lesson["questions"]],
                limit,
                snapshot,
            ),
            f"Тема: {module['title']}",
            "Чередуем задания из всех завершённых уроков выбранного раздела, а не повторяем только последний.",
            "Если нужен пример, вернись к карточке урока: практика проверяет понимание, а не память наизусть.",
        )

    raise HTTPException(status_code=422, detail="Неизвестный режим практики")


@app.get("/api/practice/session")
def practice_session(
    mode: str = "guided",
    module_id: str | None = None,
    limit: int = Query(default=4, ge=1, le=6),
) -> dict:
    snapshot = state()
    questions, title, description, tip = practice_questions(mode, module_id, limit, snapshot)
    practice_lessons = available_practice_lessons(snapshot) or [LESSONS[0]]
    return {
        "mode": mode,
        "title": title,
        "description": description,
        "tip": tip,
        "questions": [
            {**public_question(question), "lesson_title": QUESTION_LESSON[question["id"]]["title"]}
            for question in questions
        ],
        "available_modules": practice_modules(practice_lessons),
        "weak_count": len(
            [
                question_id
                for question_id in snapshot["weak_question_ids"]
                if question_id in QUESTION_BY_ID
            ]
        ),
    }


@app.get("/api/practice")
def practice() -> dict:
    """Сохраняет совместимость со старым экраном и внешними клиентами API."""
    session = practice_session()
    question = session["questions"][0]
    return {
        "question": question,
        "lesson_title": question["lesson_title"],
        "is_review": session["mode"] == "review",
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


def project_status(project: dict, index: int, snapshot: dict) -> dict:
    completed = project["id"] in snapshot["projects"]
    previous_complete = index == 0 or PROJECTS[index - 1]["id"] in snapshot["projects"]
    missing_lesson_ids = [
        lesson_id
        for lesson_id in project["requires_lesson_ids"]
        if lesson_id not in snapshot["lessons"]
    ]
    return {
        "completed": completed,
        "unlocked": completed or (previous_complete and not missing_lesson_ids),
        "missing_prerequisites": [LESSON_BY_ID[item]["title"] for item in missing_lesson_ids],
    }


def project_payload(include_editor_id: str | None = None) -> list[dict]:
    snapshot = state()
    payload = []
    for index, project in enumerate(PROJECTS):
        include_editor = project["id"] == include_editor_id
        payload.append(
            {
                **public_project(project, include_editor=include_editor),
                "prerequisite_titles": [
                    LESSON_BY_ID[lesson_id]["title"] for lesson_id in project["requires_lesson_ids"]
                ],
                **project_status(project, index, snapshot),
            }
        )
    return payload


def require_project(project_id: str) -> dict:
    project = PROJECT_BY_ID.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    index = PROJECTS.index(project)
    if not project_status(project, index, state())["unlocked"]:
        raise HTTPException(
            status_code=403, detail="Сначала заверши предыдущий проект и нужные уроки"
        )
    return project


@app.get("/api/projects")
def get_projects() -> dict:
    return {"projects": project_payload()}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> dict:
    require_project(project_id)
    return next(item for item in project_payload(project_id) if item["id"] == project_id)


@app.post("/api/projects/{project_id}/run")
def run_project(project_id: str, payload: ProjectRun) -> dict:
    require_project(project_id)
    return run_code(payload.answer, [], payload.inputs)


@app.post("/api/projects/{project_id}/submit")
def submit_project(project_id: str, payload: ProjectSubmission) -> dict:
    project = require_project(project_id)
    scenarios = project.get("scenarios") or [
        {
            "name": "основная проверка",
            "inputs": project.get("test_inputs", []),
            "tests": project["tests"],
        }
    ]
    scenario_results = [
        {
            "name": scenario["name"],
            **run_code(payload.answer, scenario["tests"], scenario.get("inputs", [])),
        }
        for scenario in scenarios
    ]
    correct = all(item["correct"] for item in scenario_results)
    first_failed = next((item for item in scenario_results if not item["correct"]), None)
    failure_message = (
        first_failed["message"] if first_failed else "Не удалось завершить проверку проекта."
    )
    result = {
        "correct": correct,
        "message": "Все сценарии проекта прошли." if correct else failure_message,
        "checks": [
            {**check, "scenario": scenario["name"]}
            for scenario in scenario_results
            for check in scenario.get("checks", [])
        ],
        "output": "\n".join(
            f"[{scenario['name']}]\n{scenario.get('output', '').rstrip()}"
            for scenario in scenario_results
            if scenario.get("output")
        ),
        "scenarios": [
            {"name": item["name"], "correct": item["correct"]} for item in scenario_results
        ],
    }
    gained = 0
    if result["correct"]:
        gained, _ = save_project(project_id, project["xp"])
    return {
        **result,
        "xp_gained": gained,
        "message": project["success"] if result["correct"] else result["message"],
    }


@app.post("/api/code/run")
def run_editor_code(payload: CodeRun) -> dict:
    """Запускает код с введёнными учеником строками без раскрытия тестов задания."""
    question = QUESTION_BY_ID.get(payload.question_id)
    if not question or question["kind"] != "code":
        raise HTTPException(status_code=404, detail="Кодовое задание не найдено")
    return run_code(payload.answer, [], payload.inputs)


@app.post("/api/sandbox/run")
def run_sandbox(payload: SandboxRun) -> dict:
    return run_code(payload.answer, [], payload.inputs)


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
    question_ids = list(exam["question_ids"])
    results, score = grade_answers(submission.answers, question_ids)
    total = len(question_ids)
    mandatory_ids = exam.get("mandatory_question_ids", [])
    result_by_id = {result["question_id"]: result for result in results}
    mandatory_passed = bool(mandatory_ids) and all(
        result_by_id[question_id]["correct"] for question_id in mandatory_ids
    )
    passed = score / total >= 0.7 and mandatory_passed
    gained = save_exam(module_id, score, total) if passed else 0
    return {
        "passed": passed,
        "correct_count": score,
        "total_count": total,
        "xp_gained": gained,
        "results": results,
        "message": "Экзамен сдан! Раздел закреплён."
        if passed
        else (
            "Нужно не менее 70% и все обязательные практические задания. "
            "Повтори отмеченные навыки в практике и возвращайся."
        ),
        "mandatory_passed": mandatory_passed,
    }


@app.post("/api/reset")
def reset_progress() -> dict:
    with connection() as conn:
        conn.execute("DELETE FROM lesson_progress")
        conn.execute("DELETE FROM attempts")
        conn.execute("DELETE FROM exam_progress")
        conn.execute("DELETE FROM project_progress")
        conn.execute("UPDATE profile SET xp = 0, streak = 0, last_activity = NULL WHERE id = 1")
    return {"ok": True}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "database": str(DATABASE_PATH.name)}
