"""Изолирует тесты от личного локального прогресса в приложении."""

from pathlib import Path

import pytest

import app.db as database
import app.main as main


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Каждый тест получает собственную SQLite-базу и не трогает python_path.db."""
    test_database = tmp_path / "python_path.test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    monkeypatch.setattr(main, "DATABASE_PATH", test_database)
