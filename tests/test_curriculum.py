from collections import Counter

from app.content import EXAMS, LESSON_BY_ID, LESSONS, MODULES, QUESTION_BY_ID, public_question
from app.learning_design import REVIEW_INTERVALS_DAYS, audit_learning_pipeline, audit_projects
from app.projects import PROJECTS


def test_full_course_has_151_progressive_lessons() -> None:
    assert len(MODULES) == 32
    assert len(LESSONS) == 151
    assert [lesson["order"] for lesson in LESSONS] == list(range(1, 152))
    assert len({lesson["id"] for lesson in LESSONS}) == 151
    assert len(QUESTION_BY_ID) == 585


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
    assert all(
        lesson["questions"][-1]["prompt"].startswith("🔁 Накопительное повторение")
        for lesson in extended_lessons
    )
    starters = [lesson["questions"][-1]["starter"].splitlines()[0] for lesson in extended_lessons]
    frequencies = Counter(starters)
    assert len(frequencies) == 16
    assert set(frequencies.values()) <= {6, 7}
    assert all(left != right for left, right in zip(starters, starters[1:], strict=False))
    assert all(len(lesson["questions"][-1]["tests"]) >= 2 for lesson in extended_lessons)


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
    for exam in EXAMS.values():
        assert len(exam["question_ids"]) >= 6
        assert all(question_id in QUESTION_BY_ID for question_id in exam["question_ids"])
        assert exam["mandatory_question_ids"]
        assert set(exam["mandatory_question_ids"]) <= set(exam["question_ids"])
        kinds = {QUESTION_BY_ID[question_id]["kind"] for question_id in exam["question_ids"]}
        assert "choice" in kinds
        assert kinds & {"code", "parsons"}


def test_public_parsons_question_hides_the_solution_order() -> None:
    question = QUESTION_BY_ID["operators-arithmetic-parsons"]
    public = public_question(question)
    assert "blocks" in public
    assert "answer" not in public
