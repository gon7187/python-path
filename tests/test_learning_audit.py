from app.content import LESSONS
from app.evaluator import run_code
from app.learning_design import (
    LESSON_TOOL_IDS,
    QUESTION_TOOL_IDS,
    audit_exam_coverage,
    audit_learning_pipeline,
    audit_projects,
)
from app.projects import PROJECT_BY_ID, PROJECTS, public_project


def _reference() -> dict[str, str]:
    return {
        "name": "print()",
        "kind": "Встроенная функция",
        "signature": "print(value)",
        "description": "Показывает значение.",
        "example": "print('ok')",
    }


def _question(question_id: str, kind: str = "choice") -> dict[str, object]:
    question: dict[str, object] = {
        "id": question_id,
        "kind": kind,
        "tool_help": [_reference()],
        "purpose": "recognize",
        "focus_concepts": ["demo"],
        "review_concepts": [],
        "requires": [],
        "retrieves": [],
        "mandatory": False,
        "scaffold_level": "worked",
        "scaffold": "worked",
    }
    if kind == "parsons":
        question["blocks"] = [
            {"id": "one", "text": "text = 'PYTHON'"},
            {"id": "two", "text": "print(text.lower())"},
        ]
    return question


def _lesson(
    lesson_id: str,
    order: int,
    *,
    theory: list[dict[str, str]] | None = None,
    questions: list[dict[str, object]] | None = None,
    module_id: str = "demo",
) -> dict[str, object]:
    return {
        "id": lesson_id,
        "module_id": module_id,
        "order": order,
        "title": lesson_id,
        "subtitle": lesson_id,
        "theory": theory or [],
        "questions": questions or [],
        "concepts": ["demo"],
        "practices": ["demo"],
        "prerequisites": [],
        "difficulty": 1,
        "estimated_minutes": 5,
        "learning_objectives": ["Проверить аудит"],
    }


def test_projects_cover_the_course_with_real_scenarios_and_progressive_hints() -> None:
    assert len(PROJECTS) == 15
    assert [project["order"] for project in PROJECTS] == list(range(1, 16))
    assert all(len(project["scenarios"]) >= 2 for project in PROJECTS)
    assert all(len(project["hints"]) >= 2 for project in PROJECTS)
    assert audit_projects(PROJECTS, LESSONS) == []


def test_every_project_reference_solution_passes_every_scenario() -> None:
    for project in PROJECTS:
        solution = project["reference_solution"]
        assert "reference_solution" not in public_project(project, include_editor=True)

        main_result = run_code(solution, project["tests"], project["test_inputs"])
        assert main_result["correct"], (project["id"], "основная проверка", main_result)

        for scenario in project["scenarios"]:
            result = run_code(solution, scenario["tests"], scenario.get("inputs", []))
            assert result["correct"], (project["id"], scenario["name"], result)


def test_input_projects_compare_the_result_instead_of_echoed_prompts() -> None:
    for project_id in (
        "greeting-card",
        "purchase-calculator",
        "access-checker",
        "word-counter",
    ):
        project = PROJECT_BY_ID[project_id]
        tests = [*project["tests"]]
        for scenario in project["scenarios"]:
            tests.extend(scenario["tests"])
        assert all(test["comparison"] == "contains" for test in tests)


def test_queue_project_uses_the_concurrency_api_it_teaches() -> None:
    project = PROJECT_BY_ID["job-scheduler"]
    assert "from queue import Queue" in project["starter"]
    assert "tasks.put(" in project["starter"]
    assert "tasks.get(" in project["starter"]
    assert {"queue", "queue-put", "queue-get", "queue-empty"} <= set(project["tool_ids"])


def test_foundation_cumulative_questions_have_precise_tool_mappings() -> None:
    assert QUESTION_TOOL_IDS["warmup-methods-code"] == ("lower", "print")
    assert QUESTION_TOOL_IDS["file-code"] == ("f-string", "return")
    assert LESSON_TOOL_IDS["strings-pro-split-join"] == ("split", "join")


def test_late_code_help_names_the_actual_callable_apis() -> None:
    questions = {
        question["id"]: question
        for lesson in LESSONS
        for question in lesson["questions"]
        if question["kind"] == "code"
    }

    assert {tool["name"] for tool in questions["files-data-csv-code"]["tool_help"]} >= {
        "csv.reader()",
        "next()",
        "int()",
    }
    assert {
        tool["name"] for tool in questions["stdlib-productivity-heapq-bisect-code"]["tool_help"]
    } >= {"heapq.heappush()", "heapq.heappop()"}
    assert {tool["name"] for tool in questions["cli-environment-argv-code"]["tool_help"]} >= {
        "argparse.ArgumentParser()"
    }
    assert {tool["name"] for tool in questions["concurrency-locks-code"]["tool_help"]} >= {
        "threading.Lock()"
    }


def test_audit_reads_parsons_block_objects_and_catches_premature_methods() -> None:
    lessons = [
        _lesson(
            "warmup-route",
            1,
            questions=[_question("premature-parsons", "parsons")],
        ),
        _lesson("warmup-methods", 2),
    ]

    errors = audit_learning_pipeline(lessons)  # type: ignore[arg-type]

    assert any("method:lower раньше объяснения" in error for error in errors)


def test_audit_reports_invalid_examples_explicitly_declared_as_python() -> None:
    lessons = [
        _lesson(
            "warmup-route",
            1,
            theory=[
                {
                    "title": "Сломанный пример",
                    "text": "Этот код должен разбираться.",
                    "example": "def broken(",
                    "language": "python",
                }
            ],
        )
    ]

    errors = audit_learning_pipeline(lessons)  # type: ignore[arg-type]

    assert any("объявлен как Python, но не разбирается" in error for error in errors)


def test_audit_rejects_an_undocumented_callable_in_reference_solution() -> None:
    question = _question("mystery-code", "code")
    question.update(
        {
            "starter": "def solve():\n    return None\n",
            "reference_solution": "def solve():\n    return mystery_api()\n",
            "tests": [{"kind": "call", "call": "solve()", "expected": 1}],
            "focus_concepts": ["demo"],
        }
    )
    lessons = [_lesson("warmup-route", 1, questions=[question])]

    errors = audit_learning_pipeline(lessons)  # type: ignore[arg-type]

    assert any(
        "call:mystery_api" in error and "без справочной карточки" in error for error in errors
    )


def test_audit_rejects_an_exact_tool_name_in_the_first_hint() -> None:
    question = _question("leaky-hint-code", "code")
    question.update(
        {
            "starter": "print('')\n",
            "hints": ["Используй print() и передай строку."],
            "tests": [{"kind": "stdout", "expected": "ok"}],
            "focus_concepts": ["demo"],
        }
    )
    lessons = [_lesson("warmup-route", 1, questions=[question])]

    errors = audit_learning_pipeline(lessons)  # type: ignore[arg-type]

    assert any("первая подсказка сразу называет инструмент print()" in error for error in errors)


def test_audit_rejects_conditional_expression_until_it_has_its_own_lesson() -> None:
    question = _question("conditional-expression-code", "code")
    question.update(
        {
            "starter": "result = 'да' if ready else 'нет'\n",
            "hints": ["Сначала опиши две ветки словами."],
            "tests": [{"kind": "stdout", "expected": "да"}],
            "focus_concepts": ["demo"],
        }
    )
    lessons = [_lesson("warmup-route", 1, questions=[question])]

    errors = audit_learning_pipeline(lessons)  # type: ignore[arg-type]

    assert any("syntax:conditional-expression" in error for error in errors)


def test_exam_audit_rejects_questions_from_another_module() -> None:
    lessons = [
        _lesson(
            "first",
            1,
            questions=[_question("first-code", "code")],
            module_id="first-module",
        ),
        _lesson(
            "second",
            2,
            questions=[_question("second-code", "code")],
            module_id="second-module",
        ),
    ]
    exams = {
        "first-module": {
            "question_ids": ["first-code", "second-code"],
            "mandatory_question_ids": ["first-code"],
        }
    }

    errors = audit_exam_coverage(exams, lessons)  # type: ignore[arg-type]

    assert any("вопросы из другого модуля second-code" in error for error in errors)
