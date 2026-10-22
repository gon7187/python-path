import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
SORTING_ID = "lists-pro-sorting"
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
PROBE_LESSON = """LESSONS = [
    {
        "id": "lists-pro-stacks-queues",
        "theory": [{"title": "Проба", "text": "Проба", "example": "x = 1", "tip": ""}],
        "questions": [],
    }
]
"""


def _registry() -> dict[str, dict]:
    assert importlib.util.find_spec("app.handwritten") is not None, "нет пакета app.handwritten"
    return importlib.import_module("app.handwritten").HANDWRITTEN


def _registry_ids() -> list[str]:
    try:
        return sorted(_registry())
    except Exception:
        return []


def _course_by_id() -> dict[str, dict]:
    from app.content import LESSON_BY_ID

    return LESSON_BY_ID


def _generated_by_id() -> dict[str, dict]:
    from app.extended_curriculum import build_extended_course

    _, lessons, _ = build_extended_course()
    return {lesson["id"]: lesson for lesson in lessons}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _copy_app(tmp_path: Path) -> Path:
    """Копия пакета app без рукописных модулей, чтобы тест управлял реестром сам."""
    assert (APP_DIR / "handwritten").is_dir(), "нет пакета app/handwritten"
    shutil.copytree(
        APP_DIR, tmp_path / "app", ignore=shutil.ignore_patterns("__pycache__", "static")
    )
    for module in (tmp_path / "app" / "handwritten").glob("lessons_*.py"):
        module.unlink()
    return tmp_path


def _run_python(root: Path, code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def _assert_contract(lesson_id: str, lesson: dict) -> None:
    assert lesson["id"] == lesson_id

    theory = lesson["theory"]
    assert len(theory) == 3, lesson_id
    for card in theory:
        for key in ("title", "text", "example"):
            assert isinstance(card.get(key), str) and card[key].strip(), (lesson_id, key)
    for card in theory:
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])

    questions = lesson["questions"]
    assert [question["id"] for question in questions] == [
        f"{lesson_id}-choice",
        f"{lesson_id}-term",
        f"{lesson_id}-code",
    ]
    assert [question["kind"] for question in questions] == ["choice", "input", "code"]
    choice, term, code = questions

    assert len(set(choice["options"])) >= 3, lesson_id
    assert choice["answer"] in choice["options"], lesson_id

    assert isinstance(term["answers"], list) and term["answers"], lesson_id
    assert all(isinstance(answer, str) and answer.strip() for answer in term["answers"])

    assert len(code["tests"]) >= 2, lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id

    for text in _strings(lesson):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


def test_c1_handwritten_package_exposes_registry_dict() -> None:
    assert (APP_DIR / "handwritten" / "__init__.py").is_file()
    registry = _registry()
    assert isinstance(registry, dict)
    assert registry, "реестр app/handwritten пуст"
    for lesson_id, lesson in registry.items():
        assert isinstance(lesson_id, str)
        assert isinstance(lesson, dict)
        assert lesson.get("id") == lesson_id


def test_c1_new_lessons_module_is_discovered_without_edits(tmp_path: Path) -> None:
    root = _copy_app(tmp_path)
    (root / "app" / "handwritten" / "lessons_zz_probe.py").write_text(
        PROBE_LESSON, encoding="utf-8"
    )
    result = _run_python(
        root, "import app.handwritten as registry; print(*sorted(registry.HANDWRITTEN))"
    )
    assert result.returncode == 0, result.stderr
    assert "lists-pro-stacks-queues" in result.stdout.split(), result.stdout


def test_c2_handwritten_lesson_replaces_theory_questions_and_subtitle() -> None:
    registry = _registry()
    assert registry, "реестр app/handwritten пуст"
    lessons = _course_by_id()
    for lesson_id, handwritten in registry.items():
        assert lesson_id in lessons, lesson_id
        lesson = lessons[lesson_id]
        assert lesson["theory"] == handwritten["theory"], lesson_id
        assert lesson["questions"] == handwritten["questions"], lesson_id
        if "subtitle" in handwritten:
            assert lesson["subtitle"] == handwritten["subtitle"], lesson_id


def test_c2_skeleton_and_question_ids_come_from_generator() -> None:
    registry = _registry()
    assert registry, "реестр app/handwritten пуст"
    lessons = _course_by_id()
    generated = _generated_by_id()
    for lesson_id, handwritten in registry.items():
        assert lesson_id in generated, lesson_id
        lesson = lessons[lesson_id]
        reference = generated[lesson_id]
        for key in ("id", "module_id", "order", "title", "duration", "xp"):
            assert lesson[key] == reference[key], (lesson_id, key)
        assert [question["id"] for question in lesson["questions"]] == [
            question["id"] for question in reference["questions"]
        ], lesson_id
        if "subtitle" not in handwritten:
            assert lesson["subtitle"] == reference["subtitle"], lesson_id


def test_c2_lessons_without_handwritten_version_stay_generated() -> None:
    registry = _registry()
    assert registry, "реестр app/handwritten пуст"
    lessons = _course_by_id()
    for lesson_id, reference in _generated_by_id().items():
        if lesson_id in registry:
            continue
        assert lessons[lesson_id] == reference, lesson_id


def test_c2_exam_question_ids_resolve_in_full_course() -> None:
    from app.content import EXAMS, LESSONS

    assert len(LESSONS) == 120
    question_ids = {question["id"] for lesson in LESSONS for question in lesson["questions"]}
    for exam_id, exam in EXAMS.items():
        for question_id in exam["question_ids"]:
            assert question_id in question_ids, (exam_id, question_id)


BAD_REGISTRY_CASES = [
    pytest.param(
        {
            "lessons_zz_bad.py": 'LESSONS = [{"id": "no-such-lesson", "theory": [], "questions": []}]\n'
        },
        "no-such-lesson",
        id="unknown-id",
    ),
    pytest.param(
        {
            "lessons_zz_first.py": f'LESSONS = [{{"id": "{SORTING_ID}", "theory": [], "questions": []}}]\n',
            "lessons_zz_second.py": f'LESSONS = [{{"id": "{SORTING_ID}", "theory": [], "questions": []}}]\n',
        },
        SORTING_ID,
        id="duplicate-id",
    ),
    pytest.param(
        {"lessons_zz_bad.py": f'LESSONS = [{{"id": "{SORTING_ID}", "theory": []}}]\n'},
        SORTING_ID,
        id="missing-key",
    ),
    pytest.param(
        {
            "lessons_zz_bad.py": (
                f'LESSONS = [{{"id": "{SORTING_ID}", "theory": [], "questions": [], "bonus": 1}}]\n'
            )
        },
        SORTING_ID,
        id="extra-key",
    ),
]


@pytest.mark.parametrize(("files", "lesson_id"), BAD_REGISTRY_CASES)
def test_c3_bad_registry_fails_loudly_on_content_import(
    tmp_path: Path, files: dict[str, str], lesson_id: str
) -> None:
    root = _copy_app(tmp_path)
    for filename, source in files.items():
        (root / "app" / "handwritten" / filename).write_text(source, encoding="utf-8")
    result = _run_python(root, "import app.content")
    assert result.returncode != 0, result.stdout
    assert "ValueError" in result.stderr, result.stderr
    assert lesson_id in result.stderr, result.stderr


@pytest.mark.parametrize("lesson_id", _registry_ids())
def test_c4_handwritten_lesson_meets_contract(lesson_id: str) -> None:
    _assert_contract(lesson_id, _registry()[lesson_id])


def test_c5_sorting_lesson_is_order_26_and_registered() -> None:
    assert SORTING_ID in _registry()
    lesson = _course_by_id()[SORTING_ID]
    assert lesson["order"] == 26
    assert lesson["module_id"] == "lists-pro"
    assert lesson["title"] == "Сортировка"


def test_c5_sorting_theory_covers_sorted_sort_key_reverse_and_typo() -> None:
    theory_text = " ".join(_strings(_registry()[SORTING_ID]["theory"]))
    assert "sorted()" in theory_text
    assert "list.sort()" in theory_text
    assert "key" in theory_text
    assert "reverse" in theory_text
    assert "x = x.sort()" in theory_text


def test_c5_sorting_choice_and_term_are_about_sorting() -> None:
    choice, term, _ = _registry()[SORTING_ID]["questions"]
    assert "sort" in choice["answer"].casefold()
    assert any(
        "sort" in answer.casefold() or "сортир" in answer.casefold() for answer in term["answers"]
    )


def test_c5_sorting_code_task_sorts_by_key_not_sum_items() -> None:
    lesson = _registry()[SORTING_ID]
    code = lesson["questions"][2]
    assert "sum_items" not in " ".join(_strings(lesson))
    assert "сортир" in code["prompt"].casefold() or "sort" in code["prompt"].casefold()
    assert re.search(r"key\s*=", code["reference"]), code["reference"]


def test_c5_sorting_lesson_passes_handwritten_contract() -> None:
    _assert_contract(SORTING_ID, _registry()[SORTING_ID])


def test_c6_course_keeps_120_lessons_and_360_questions() -> None:
    from app.content import LESSONS, QUESTION_BY_ID

    assert len(LESSONS) == 120
    assert [lesson["order"] for lesson in LESSONS] == list(range(1, 121))
    assert sum(len(lesson["questions"]) for lesson in LESSONS) == 360
    assert len(QUESTION_BY_ID) == 360
