"""Регрессии тематической практики расширенного курса."""

from __future__ import annotations

import ast
import json

from app.advanced_practice import TOPICAL_TASKS
from app.content import public_question
from app.evaluator import run_code
from app.exam_transfer import EXAM_TRANSFER_TESTS
from app.extended_curriculum import COURSE_UNITS, EXTRA_EXAMS, EXTRA_LESSONS


def _code_question(lesson: dict) -> dict:
    return next(question for question in lesson["questions"] if question["kind"] == "code")


def test_every_extended_lesson_has_unique_topical_code() -> None:
    expected_keys = {
        (unit["id"], lesson_spec[0]) for unit in COURSE_UNITS for lesson_spec in unit["lessons"]
    }
    assert len(EXTRA_LESSONS) == 108
    assert set(TOPICAL_TASKS) == expected_keys

    questions = [_code_question(lesson) for lesson in EXTRA_LESSONS]
    assert len({question["id"] for question in questions}) == 108
    assert len({question["prompt"] for question in questions}) == 108
    assert len({question["starter"] for question in questions}) == 108
    assert len({tuple(question["hints"]) for question in questions}) == 108

    for lesson, question in zip(EXTRA_LESSONS, questions, strict=True):
        assert set(lesson["concepts"]) & set(question["focus_concepts"]), lesson["id"]
        assert question["purpose"] == "topical_application"
        assert question["mandatory"] is True
        assert len(question["hints"]) == 4
        assert len([test for test in question["tests"] if test["kind"] == "call"]) >= 2
        assert any(test["kind"] == "source" for test in question["tests"])
        assert question["reference_solution"]
        ast.parse(question["starter"])


def test_all_reference_solutions_pass_the_real_runner() -> None:
    for key, blueprint in TOPICAL_TASKS.items():
        question_id = f"{key[0]}-{key[1]}-code"
        tests = [
            *(
                {"kind": "call", "call": call, "expected": expected}
                for call, expected in blueprint.cases
            ),
            {
                "kind": "source",
                "required_tokens": list(blueprint.required_tokens),
                "expected": True,
            },
            *EXAM_TRANSFER_TESTS[question_id],
        ]
        result = run_code(blueprint.solution, tests)
        assert result["correct"], f"{key}: {result}"


def test_theory_examples_are_explicit_and_python_examples_have_output() -> None:
    python_cards = []
    format_cards = []
    for lesson in EXTRA_LESSONS:
        card = lesson["theory"][0]
        assert card["example_status"] in {"self-contained", "format-example"}
        if card["language"] == "python":
            python_cards.append(card)
            assert card["example_status"] == "self-contained"
            assert "output" in card
            ast.parse(card["example"])
            result = run_code(
                card["example"],
                [{"kind": "stdout", "expected": card["output"]}],
            )
            assert result["correct"], f"{lesson['id']}: {result}"
        else:
            format_cards.append(card)
            assert card["example_status"] == "format-example"

    assert len(python_cards) == 90
    assert len(format_cards) == 18


def test_exams_cover_all_four_module_concepts_with_mandatory_code() -> None:
    lessons_by_module: dict[str, list[dict]] = {}
    questions_by_id = {}
    for lesson in EXTRA_LESSONS:
        lessons_by_module.setdefault(lesson["module_id"], []).append(lesson)
        questions_by_id.update({question["id"]: question for question in lesson["questions"]})

    assert len(EXTRA_EXAMS) == 27
    for module_id, exam in EXTRA_EXAMS.items():
        module_lessons = lessons_by_module[module_id]
        expected_code_ids = {_code_question(lesson)["id"] for lesson in module_lessons}
        assert len(exam["question_ids"]) == 8
        assert set(exam["mandatory_question_ids"]) == expected_code_ids
        assert expected_code_ids <= set(exam["question_ids"])
        covered = {
            concept
            for question_id in expected_code_ids
            for concept in questions_by_id[question_id]["focus_concepts"]
        }
        assert covered == {lesson["concepts"][0] for lesson in module_lessons}


def test_recall_accepts_natural_method_forms_and_scaffolds_do_not_leak_answers() -> None:
    replace_lesson = next(
        lesson for lesson in EXTRA_LESSONS if lesson["id"] == "strings-pro-search-replace"
    )
    term = next(question for question in replace_lesson["questions"] if question["kind"] == "input")
    assert {"replace", "replace()", ".replace()", "метод replace"} <= set(term["answers"])

    by_id = {lesson["id"]: lesson for lesson in EXTRA_LESSONS}
    dotted_term = next(
        question
        for question in by_id["async-gather-timeouts"]["questions"]
        if question["kind"] == "input"
    )
    assert {"asyncio.gather", "asyncio.gather()", "gather", "gather()"} <= set(
        dotted_term["answers"]
    )
    elif_term = next(
        question
        for question in by_id["flow-advanced-elif"]["questions"]
        if question["kind"] == "input"
    )
    assert "elif()" not in elif_term["answers"]

    for lesson_id, impossible_form in {
        "operators-booleans": "and()",
        "flow-advanced-match": "match()",
        "flow-advanced-break-continue": "continue()",
        "iterators-yield": "yield()",
        "modules-imports": "import()",
        "errors-debug-raise": "raise()",
        "errors-debug-finally": "finally()",
        "scope-lambda-key": "lambda()",
        "testing-unit-tests": "assert()",
        "async-coroutines": "await()",
    }.items():
        question = next(item for item in by_id[lesson_id]["questions"] if item["kind"] == "input")
        assert impossible_form not in question["answers"]

    pyproject_term = next(
        item for item in by_id["cli-environment-pyproject"]["questions"] if item["kind"] == "input"
    )
    assert {"pyproject.toml", "pyproject"} <= set(pyproject_term["answers"])
    assert {"pyproject.toml()", "toml", "toml()"}.isdisjoint(pyproject_term["answers"])

    for lesson in EXTRA_LESSONS:
        for question in lesson["questions"]:
            if question["kind"] == "code":
                public = public_question(question)
                assert "reference_solution" not in public
                assert question["reference_solution"] not in json.dumps(
                    public["tool_help"], ensure_ascii=False
                )
                continue
            assert public_question(question)["tool_help"] == []


def test_parsons_block_ids_do_not_reveal_the_order() -> None:
    for lesson in EXTRA_LESSONS:
        question = next(
            question for question in lesson["questions"] if question["kind"] == "parsons"
        )
        block_ids = [block["id"] for block in question["blocks"]]
        assert len(block_ids) == len(set(block_ids))
        assert all("-block-h" in block_id for block_id in block_ids)


def test_parsons_tasks_use_their_topic_instead_of_one_generic_script() -> None:
    block_sequences = []
    permutations_by_length: dict[int, set[tuple[int, ...]]] = {}
    topical_frames = set()
    for lesson in EXTRA_LESSONS:
        question = next(item for item in lesson["questions"] if item["kind"] == "parsons")
        texts = tuple(block["text"] for block in question["blocks"])
        block_sequences.append(texts)
        assert "Определи, какие входные значения нужны строке." not in texts
        answer = question["answer"]
        permutation = tuple(answer.index(block["id"]) for block in question["blocks"])
        permutations_by_length.setdefault(len(answer), set()).add(permutation)
        if question["prompt"].startswith("Собери тематическую цепочку"):
            topical_frames.add(tuple(sorted(text.split(" — ", 1)[0] for text in texts)))

    assert len(set(block_sequences)) == len(EXTRA_LESSONS)
    assert len(permutations_by_length[4]) >= 18
    assert len(topical_frames) == 4


def test_shell_reference_cards_are_not_labelled_as_python() -> None:
    by_id = {lesson["id"]: lesson for lesson in EXTRA_LESSONS}
    for lesson_id in ("quality-format-lint", "quality-git"):
        question = next(item for item in by_id[lesson_id]["questions"] if item["kind"] == "code")
        assert question["tool_help"][0]["language"] == "shell"
