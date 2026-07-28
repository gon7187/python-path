from pathlib import Path

from app.content import EXAMS, LESSONS, MODULES, QUESTION_BY_ID
from app.evaluator import evaluate
from app.extended_curriculum import EXTRA_LESSONS
from app.lessons_13_25 import LESSONS_13_25

LESSONS_13_25_IDENTITY = [
    ("operators-arithmetic", "operators", 13),
    ("operators-integer-division", "operators", 14),
    ("operators-booleans", "operators", 15),
    ("operators-floating-point", "operators", 16),
    ("strings-pro-indexes", "strings-pro", 17),
    ("strings-pro-search-replace", "strings-pro", 18),
    ("strings-pro-split-join", "strings-pro", 19),
    ("strings-pro-formatting", "strings-pro", 20),
    ("tuples-slices-tuples", "tuples-slices", 21),
    ("tuples-slices-unpacking", "tuples-slices", 22),
    ("tuples-slices-slices", "tuples-slices", 23),
    ("tuples-slices-zip-enumerate", "tuples-slices", 24),
    ("lists-pro-list-methods", "lists-pro", 25),
]


def test_full_course_has_120_progressive_lessons() -> None:
    assert len(MODULES) == 31
    assert len(LESSONS) == 120
    assert [lesson["order"] for lesson in LESSONS] == list(range(1, 121))
    assert len({lesson["id"] for lesson in LESSONS}) == 120


def test_every_lesson_has_material_and_exercises() -> None:
    assert len(QUESTION_BY_ID) == 360
    for lesson in LESSONS:
        assert len(lesson["theory"]) == 3
        assert len(lesson["questions"]) == 3
        assert {question["kind"] for question in lesson["questions"]} == {
            "choice",
            "input",
            "code",
        }


def test_every_module_has_a_valid_exam() -> None:
    assert set(EXAMS) == {module["id"] for module in MODULES}
    for exam in EXAMS.values():
        assert len(exam["question_ids"]) >= 4
        assert all(question_id in QUESTION_BY_ID for question_id in exam["question_ids"])


def test_lessons_13_25_are_handwritten_and_keep_their_identity() -> None:
    assert [
        (lesson["id"], lesson["module_id"], lesson["order"]) for lesson in LESSONS_13_25
    ] == LESSONS_13_25_IDENTITY
    assert [lesson["order"] for lesson in EXTRA_LESSONS] == list(range(26, 121))
    assert LESSONS[12:25] == LESSONS_13_25


def test_lessons_13_25_have_beginner_theory_and_three_questions() -> None:
    for lesson in LESSONS_13_25:
        cards = lesson["theory"]
        assert len(cards) == 3
        assert len({card["title"] for card in cards}) == 3
        assert len({card["example"] for card in cards}) == 3
        assert 600 <= sum(len(card["text"]) for card in cards) <= 900
        assert all("# Вывод:" in card["example"] for card in cards)
        assert any(
            "ошиб" in (card["title"] + card["text"] + card["tip"]).casefold() for card in cards
        )

        questions = lesson["questions"]
        assert [question["kind"] for question in questions] == ["choice", "input", "code"]
        assert isinstance(questions[1]["answers"], list)
        assert questions[1]["answers"]
        assert all(isinstance(answer, str) and answer for answer in questions[1]["answers"])


def test_reference_solutions_for_lessons_13_25_pass_the_runner() -> None:
    for lesson in LESSONS_13_25:
        code_question = lesson["questions"][2]
        result = evaluate(code_question, code_question["reference"])
        assert result["correct"] is True, (lesson["order"], result)


def test_lessons_four_to_six_do_not_require_future_topics() -> None:
    if_result = QUESTION_BY_ID["if-result"]
    assert "\n" in if_result["prompt"]
    assert (
        if_result["prompt"]
        == "Что выведет этот код?\n\nif 3 > 5:\n    print('да')\nelse:\n    print('нет')"
    )

    for question_id in ("if-code", "for-code", "while-code"):
        question = QUESTION_BY_ID[question_id]
        assert "def " not in question["prompt"]
        assert "def " not in question["starter"]
        assert "[" not in question["prompt"]
        assert "[" not in question["starter"]

    styles = Path("app/static/styles.css").read_text(encoding="utf-8")
    assert ".question-prompt" in styles
    assert "white-space: pre-wrap" in styles

    assert QUESTION_BY_ID["if-code"]["tests"] == [{"kind": "stdout", "expected": "Возьми куртку"}]
    assert QUESTION_BY_ID["for-code"]["tests"] == [{"kind": "stdout", "expected": "1\n2\n3\n4\n5"}]
    assert QUESTION_BY_ID["while-code"]["tests"] == [
        {"kind": "stdout", "expected": "5\n4\n3\n2\n1\nПуск!"}
    ]
