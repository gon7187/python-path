import ast
from copy import deepcopy

from app.content import (
    EXAM_INPUT_CUES,
    EXAMS,
    LESSON_BY_ID,
    LESSONS,
    MODULES,
    QUESTION_BY_ID,
    public_question,
)
from app.evaluator import run_code
from app.exam_transfer import EXAM_TRANSFER_TESTS
from app.learning_design import (
    PUBLIC_TOOL_FIELDS,
    REVIEW_INTERVALS_DAYS,
    TOOL_CATALOG,
    audit_exam_coverage,
    audit_learning_pipeline,
    audit_projects,
)
from app.projects import PROJECTS


def test_full_course_has_151_progressive_lessons() -> None:
    assert len(MODULES) == 32
    assert len(LESSONS) == 151
    assert [lesson["order"] for lesson in LESSONS] == list(range(1, 152))
    assert len({lesson["id"] for lesson in LESSONS}) == 151
    lesson_question_ids = {question["id"] for lesson in LESSONS for question in lesson["questions"]}
    assert len(lesson_question_ids) == 585
    assert len(QUESTION_BY_ID) == 585 + sum(len(exam["question_ids"]) for exam in EXAMS.values())


def test_every_lesson_has_material_metadata_and_exercises() -> None:
    for lesson in LESSONS:
        assert len(lesson["theory"]) >= 4
        assert len(lesson["questions"]) in {3, 4}
        assert {"choice", "input", "code"} <= {question["kind"] for question in lesson["questions"]}
        assert lesson["concepts"]
        assert lesson["practices"]
        assert lesson["difficulty"] in range(1, 6)
        assert lesson["review_intervals_days"] == list(REVIEW_INTERVALS_DAYS)
        for question in lesson["questions"]:
            assert question["guide"]
            assert question["purpose"]
            assert question["focus_concepts"]
            assert "review_concepts" in question
            assert "mandatory" in question
            assert question["scaffold_level"]
        for question in lesson["questions"]:
            if question["kind"] == "code":
                assert len(question["hints"]) >= 2


def test_foundation_python_examples_match_their_declared_output() -> None:
    extended_start = next(
        index for index, lesson in enumerate(LESSONS) if lesson["id"] == "operators-arithmetic"
    )
    for lesson in LESSONS[:extended_start]:
        for card in lesson["theory"]:
            if card.get("language") != "python":
                continue
            assert "output" in card, lesson["id"]
            result = run_code(
                card["example"],
                [{"kind": "stdout", "expected": card["output"]}],
            )
            assert result["correct"], f"{lesson['id']}: {result}"


def test_every_question_has_a_safe_relevant_tool_reference() -> None:
    required_fields = {"name", "kind", "signature", "description", "example"}
    allowed_fields = set(PUBLIC_TOOL_FIELDS)

    for tool_id, tool in TOOL_CATALOG.items():
        assert tool_id
        assert required_fields <= tool.keys()
        assert tool["introduced_in"]

    for lesson in LESSONS:
        for question in lesson["questions"]:
            assert question["tool_help"], question["id"]
            for tool in question["tool_help"]:
                assert required_fields <= tool.keys(), question["id"]
                assert tool.keys() <= allowed_fields

    lower_help = QUESTION_BY_ID["warmup-methods-code"]["tool_help"]
    assert {tool["name"] for tool in lower_help} == {".lower()", "print()"}
    assert next(tool for tool in lower_help if tool["name"] == ".lower()") == {
        "name": ".lower()",
        "kind": "Метод строки",
        "signature": "text.lower()",
        "description": "Возвращает новую строку в нижнем регистре. Исходную строку не изменяет.",
        "example": "'PyThOn'.lower()  # 'python'",
    }
    strip_help = QUESTION_BY_ID["challenge-strings-strip"]["tool_help"]
    assert {tool["name"] for tool in strip_help} >= {".strip()", "print()"}


def test_public_tool_reference_uses_an_allowlist_and_hides_internal_ids() -> None:
    public = public_question(QUESTION_BY_ID["challenge-strings-strip"])
    assert "tool_ids" not in public
    assert public["tool_help"]
    assert all(set(tool) <= set(PUBLIC_TOOL_FIELDS) for tool in public["tool_help"])

    forbidden = {
        "answer",
        "answers",
        "explanation",
        "hint",
        "introduced_in",
        "reference_solution",
        "required_tokens",
        "solution",
        "test_inputs",
        "tests",
    }

    def nested_keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value) | {key for item in value.values() for key in nested_keys(item)}
        if isinstance(value, list):
            return {key for item in value for key in nested_keys(item)}
        return set()

    assert nested_keys(public).isdisjoint(forbidden)


def test_extended_lessons_use_four_learning_forms_and_balanced_review() -> None:
    extended_start = next(
        index for index, lesson in enumerate(LESSONS) if lesson["id"] == "operators-arithmetic"
    )
    extended_lessons = LESSONS[extended_start:]

    assert len(extended_lessons) == 108
    assert all(len(lesson["theory"]) >= 6 for lesson in extended_lessons)
    assert all(
        [question["kind"] for question in lesson["questions"]]
        == ["choice", "input", "parsons", "code"]
        for lesson in extended_lessons
    )
    code_questions = [lesson["questions"][-1] for lesson in extended_lessons]
    assert all(question["purpose"] == "topical_application" for question in code_questions)
    assert len({question["prompt"] for question in code_questions}) == 108
    assert len({question["starter"] for question in code_questions}) == 108
    assert all(question["reference_solution"] for question in code_questions)
    assert all(question["review_concepts"] for question in code_questions)
    assert all(question["retrieves"] == question["review_concepts"] for question in code_questions)
    assert all(
        len([test for test in question["tests"] if test["kind"] == "call"]) >= 2
        for question in code_questions
    )


def test_early_lessons_mix_predictions_and_small_traps() -> None:
    predict_ids = {"warmup-print-choice", "warmup-read-code-choice", "warmup-numbers-choice"}
    trap_ids = {
        "warmup-text-choice",
        "warmup-variables-choice",
        "warmup-names-choice",
        "warmup-types-choice",
        "warmup-length-choice",
        "warmup-fstring-choice",
    }

    assert all(
        QUESTION_BY_ID[question_id]["badge"] == "🔎 Предскажи" for question_id in predict_ids
    )
    assert all(QUESTION_BY_ID[question_id]["badge"] == "⚠️ Ловушка" for question_id in trap_ids)
    assert public_question(QUESTION_BY_ID["warmup-fstring-choice"])["badge"] == "⚠️ Ловушка"


def test_curriculum_linter_rejects_unknown_tools_before_their_lesson() -> None:
    assert audit_learning_pipeline(LESSONS) == []
    assert audit_projects(PROJECTS, LESSONS) == []
    assert audit_exam_coverage(EXAMS, LESSONS, QUESTION_BY_ID) == []


def test_exam_audit_rejects_a_hidden_tool_before_its_lesson() -> None:
    exams = deepcopy(EXAMS)
    questions = deepcopy(QUESTION_BY_ID)
    exam = exams["start"]
    delivery_id = next(
        delivery_id
        for source_id, delivery_id in zip(
            exam["source_question_ids"], exam["question_ids"], strict=True
        )
        if source_id == "var-code"
    )
    questions[delivery_id]["tests"].append(
        {"kind": "value", "call": "city.upper()", "expected": "КАЗАНЬ"}
    )

    errors = audit_exam_coverage(exams, LESSONS, questions)

    assert any(
        delivery_id in error and "method:upper раньше объяснения" in error for error in errors
    )


def test_function_and_control_flow_skills_are_split_into_microsteps() -> None:
    expected_order = [
        "conditions",
        "conditions-else",
        "for-loop",
        "for-accumulator",
        "while-loop",
        "while-break",
        "functions",
        "functions-parameters",
        "functions-return",
        "functions-greeting",
        "functions-keyword-arguments",
    ]
    actual = [lesson["id"] for lesson in LESSONS]
    positions = [actual.index(lesson_id) for lesson_id in expected_order]
    assert positions == sorted(positions)

    assert "return" not in LESSON_BY_ID["functions"]["questions"][2]["starter"]
    assert "return" not in LESSON_BY_ID["functions-parameters"]["questions"][2]["starter"]
    assert "return" in LESSON_BY_ID["functions-return"]["questions"][2]["starter"]
    assert "break" not in "\n".join(
        card["example"] for card in LESSON_BY_ID["while-loop"]["theory"]
    )
    assert "break" in "\n".join(card["example"] for card in LESSON_BY_ID["while-break"]["theory"])


def test_collections_tools_have_their_own_lesson_before_use() -> None:
    ids = [lesson["id"] for lesson in LESSONS]
    assert ids.index("lists") < ids.index("lists-append")
    assert ids.index("lists-append") < ids.index("strings-split")
    assert ids.index("strings-split") < ids.index("lists-sum")
    assert ids.index("dicts-sets") < ids.index("sets")
    assert ids.index("strings-strip") < ids.index("operators-arithmetic")


def test_foundation_lessons_end_with_cumulative_transfer() -> None:
    challenge_lessons = [
        lesson
        for lesson in LESSONS
        if lesson["id"]
        in {
            question_id.removeprefix("challenge-")
            for question_id in QUESTION_BY_ID
            if question_id.startswith("challenge-")
        }
    ]
    assert len(challenge_lessons) == 24
    for lesson in challenge_lessons:
        challenge = lesson["questions"][-1]
        assert challenge["id"] == f"challenge-{lesson['id']}"
        assert challenge["kind"] == "code"
        assert challenge["mandatory"] is True
        assert len(challenge["tests"]) >= 2


def test_every_exam_is_mixed_and_requires_practical_work() -> None:
    assert set(EXAMS) == {module["id"] for module in MODULES}
    lesson_question_ids = {question["id"] for lesson in LESSONS for question in lesson["questions"]}
    for exam in EXAMS.values():
        assert len(exam["question_ids"]) >= 6
        assert set(exam["question_ids"]).isdisjoint(lesson_question_ids)
        assert len(exam["source_question_ids"]) == len(exam["question_ids"])
        assert all(question_id in QUESTION_BY_ID for question_id in exam["question_ids"])
        assert exam["mandatory_question_ids"]
        assert set(exam["mandatory_question_ids"]) <= set(exam["question_ids"])
        kinds = {QUESTION_BY_ID[question_id]["kind"] for question_id in exam["question_ids"]}
        assert "choice" in kinds
        assert kinds & {"code", "parsons"}
        for question_id in exam["question_ids"]:
            question = QUESTION_BY_ID[question_id]
            public = public_question(question)
            assert "hint" not in public
            if question["kind"] == "code":
                ast.parse(question["starter"])


def test_exam_code_uses_unseen_behavioral_transfer_without_syntax_oracles() -> None:
    code_source_ids = {
        source_id
        for exam in EXAMS.values()
        for source_id in exam["source_question_ids"]
        if QUESTION_BY_ID[source_id]["kind"] == "code"
    }
    assert len(code_source_ids) == 118
    assert set(EXAM_TRANSFER_TESTS) == code_source_ids

    for exam in EXAMS.values():
        for source_id, delivery_id in zip(
            exam["source_question_ids"], exam["question_ids"], strict=True
        ):
            source = QUESTION_BY_ID[source_id]
            if source["kind"] != "code":
                continue
            delivery = QUESTION_BY_ID[delivery_id]
            transfer_tests = EXAM_TRANSFER_TESTS[source_id]
            assert transfer_tests
            assert all(test not in source["tests"] for test in transfer_tests)
            assert all(test in delivery["tests"] for test in transfer_tests)
            assert all(test["kind"] not in {"source", "ast"} for test in delivery["tests"])


def test_exam_recall_cards_keep_the_question_context_without_answer_leaks() -> None:
    for exam in EXAMS.values():
        for source_id, delivery_id in zip(
            exam["source_question_ids"], exam["question_ids"], strict=True
        ):
            source = QUESTION_BY_ID[source_id]
            delivery = QUESTION_BY_ID[delivery_id]
            if source["kind"] == "code":
                assert delivery["purpose"] == "exam_transfer"
                continue

            assert delivery["purpose"] == "exam_retrieval"
            assert source["explanation"] not in delivery["prompt"]
            if source["kind"] == "choice":
                assert source["prompt"] in delivery["prompt"]
                assert delivery["options"] == source["options"]
                assert delivery["answer"] == source["answer"]
            elif source["kind"] == "input":
                cue = EXAM_INPUT_CUES.get(source_id, {})
                assert cue.get("prompt", source["prompt"]) in delivery["prompt"]
                assert delivery["answers"] == cue.get("answers", source["answers"])
            else:
                assert source["prompt"] in delivery["prompt"]


def test_exam_audit_rejects_an_answer_named_in_an_input_prompt() -> None:
    exams = deepcopy(EXAMS)
    questions = deepcopy(QUESTION_BY_ID)
    exam = exams["databases"]
    delivery_id = next(
        delivery_id
        for source_id, delivery_id in zip(
            exam["source_question_ids"], exam["question_ids"], strict=True
        )
        if source_id == "databases-crud-term"
    )
    questions[delivery_id]["prompt"] += " Подсказка: CRUD."

    errors = audit_exam_coverage(exams, LESSONS, questions)

    assert any(
        delivery_id in error and "дословно называет принимаемый ответ" in error for error in errors
    )


def test_public_parsons_question_hides_the_solution_order() -> None:
    question = QUESTION_BY_ID["operators-arithmetic-parsons"]
    public = public_question(question)
    assert "blocks" in public
    assert "answer" not in public
