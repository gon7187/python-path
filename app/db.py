"""Минимальное SQLite-хранилище прогресса для локального single-user приложения."""

from __future__ import annotations

import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "python_path.db"


def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                xp INTEGER NOT NULL DEFAULT 0,
                streak INTEGER NOT NULL DEFAULT 0,
                last_activity TEXT
            );
            CREATE TABLE IF NOT EXISTS lesson_progress (
                lesson_id TEXT PRIMARY KEY,
                stars INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                total_count INTEGER NOT NULL,
                completed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                correct INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS exam_progress (
                module_id TEXT PRIMARY KEY,
                score INTEGER NOT NULL,
                total_count INTEGER NOT NULL,
                passed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS project_progress (
                project_id TEXT PRIMARY KEY,
                completed_at TEXT NOT NULL
            );
            INSERT OR IGNORE INTO profile (id, xp, streak, last_activity) VALUES (1, 0, 0, NULL);
            """
        )


def _touch_activity(conn: sqlite3.Connection) -> None:
    profile = conn.execute("SELECT streak, last_activity FROM profile WHERE id = 1").fetchone()
    today = date.today()
    last = date.fromisoformat(profile["last_activity"]) if profile["last_activity"] else None
    streak = profile["streak"]
    if last != today:
        streak = streak + 1 if last == today - timedelta(days=1) else 1
        conn.execute(
            "UPDATE profile SET streak = ?, last_activity = ? WHERE id = 1",
            (streak, today.isoformat()),
        )


def record_attempt(question_id: str, correct: bool) -> None:
    with connection() as conn:
        _touch_activity(conn)
        conn.execute(
            "INSERT INTO attempts (question_id, correct, created_at) VALUES (?, ?, ?)",
            (question_id, int(correct), datetime.now(UTC).isoformat()),
        )


def save_lesson(lesson_id: str, correct_count: int, total_count: int, xp: int) -> tuple[int, bool]:
    stars = (
        3 if correct_count == total_count else 2 if correct_count >= max(1, total_count - 1) else 1
    )
    with connection() as conn:
        _touch_activity(conn)
        previous = conn.execute(
            "SELECT stars FROM lesson_progress WHERE lesson_id = ?", (lesson_id,)
        ).fetchone()
        was_new = previous is None
        gained = xp if was_new else max(0, (stars - previous["stars"]) * 5)
        conn.execute(
            """
            INSERT INTO lesson_progress (lesson_id, stars, correct_count, total_count, completed_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(lesson_id) DO UPDATE SET
                stars = MAX(stars, excluded.stars),
                correct_count = excluded.correct_count,
                total_count = excluded.total_count,
                completed_at = excluded.completed_at
            """,
            (lesson_id, stars, correct_count, total_count, datetime.now(UTC).isoformat()),
        )
        if gained:
            conn.execute("UPDATE profile SET xp = xp + ? WHERE id = 1", (gained,))
    return gained, was_new


def save_exam(module_id: str, score: int, total_count: int) -> int:
    with connection() as conn:
        _touch_activity(conn)
        previous = conn.execute(
            "SELECT score FROM exam_progress WHERE module_id = ?", (module_id,)
        ).fetchone()
        previously_passed = previous is not None and previous["score"] / total_count >= 0.7
        gained = 50 if not previously_passed and score / total_count >= 0.7 else 0
        conn.execute(
            """
            INSERT INTO exam_progress (module_id, score, total_count, passed_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(module_id) DO UPDATE SET score = MAX(score, excluded.score), total_count = excluded.total_count, passed_at = excluded.passed_at
            """,
            (module_id, score, total_count, datetime.now(UTC).isoformat()),
        )
        if gained:
            conn.execute("UPDATE profile SET xp = xp + ? WHERE id = 1", (gained,))
    return gained


def save_project(project_id: str, xp: int) -> tuple[int, bool]:
    """Отмечает проект завершённым и начисляет награду только за первый проход."""
    with connection() as conn:
        _touch_activity(conn)
        previous = conn.execute(
            "SELECT project_id FROM project_progress WHERE project_id = ?", (project_id,)
        ).fetchone()
        was_new = previous is None
        conn.execute(
            "INSERT OR IGNORE INTO project_progress (project_id, completed_at) VALUES (?, ?)",
            (project_id, datetime.now(UTC).isoformat()),
        )
        if was_new:
            conn.execute("UPDATE profile SET xp = xp + ? WHERE id = 1", (xp,))
    return (xp if was_new else 0), was_new


def state() -> dict:
    with connection() as conn:
        profile = dict(
            conn.execute("SELECT xp, streak, last_activity FROM profile WHERE id = 1").fetchone()
        )
        lessons = {
            row["lesson_id"]: dict(row)
            for row in conn.execute(
                "SELECT lesson_id, stars, correct_count, total_count, completed_at FROM lesson_progress"
            )
        }
        exams = {
            row["module_id"]: dict(row)
            for row in conn.execute(
                "SELECT module_id, score, total_count, passed_at FROM exam_progress"
            )
        }
        projects = {
            row["project_id"]: dict(row)
            for row in conn.execute("SELECT project_id, completed_at FROM project_progress")
        }
        weak = [
            row["question_id"]
            for row in conn.execute(
                """
                SELECT question_id FROM attempts GROUP BY question_id
                HAVING SUM(correct) < COUNT(*) ORDER BY MAX(created_at) ASC LIMIT 10
                """
            )
        ]
    return {
        "profile": profile,
        "lessons": lessons,
        "exams": exams,
        "projects": projects,
        "weak_question_ids": weak,
    }
