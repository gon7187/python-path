import contextlib
import io
import re
from pathlib import Path

from app import extended_curriculum
from app.content import EXAMS, LESSONS, MODULES, QUESTION_BY_ID
from app.evaluator import evaluate, normalize
from app.extended_curriculum import EXTRA_LESSONS, build_extended_course
from app.lessons_1_12 import LESSONS_1_12
from app.lessons_13_25 import LESSONS_13_25

LESSONS_1_12_IDENTITY = [
    ("hello", "start", 1),
    ("variables", "start", 2),
    ("strings-input", "start", 3),
    ("conditions", "logic", 4),
    ("for-loop", "logic", 5),
    ("while-loop", "logic", 6),
    ("functions", "structures", 7),
    ("lists", "structures", 8),
    ("dicts-sets", "structures", 9),
    ("files", "realworld", 10),
    ("exceptions", "realworld", 11),
    ("classes", "realworld", 12),
]

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


def test_lessons_1_12_are_reworked_and_keep_their_identity() -> None:
    assert [
        (lesson["id"], lesson["module_id"], lesson["order"]) for lesson in LESSONS_1_12
    ] == LESSONS_1_12_IDENTITY
    assert LESSONS[:12] == LESSONS_1_12


def test_lessons_1_12_have_beginner_theory_and_three_questions() -> None:
    for lesson in LESSONS_1_12:
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


def test_reference_solutions_for_lessons_1_12_pass_the_runner() -> None:
    for lesson in LESSONS_1_12:
        code_question = lesson["questions"][2]
        result = evaluate(code_question, code_question["reference"])
        assert result["correct"] is True, (lesson["order"], result)


def test_theory_examples_for_lessons_1_12_run_cleanly(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    for lesson in LESSONS_1_12:
        for card in lesson["theory"]:
            example = card["example"].split("# Вывод:")[0].strip()
            expected = "\n".join(
                line[2:] for line in card["example"].split("# Вывод:")[1].strip().splitlines()
            )
            namespace: dict = {}
            with contextlib.redirect_stdout(output := io.StringIO()):
                exec(example, namespace)
            assert output.getvalue().strip() == expected.strip(), (lesson["id"], card["title"])


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
    conditions_term = QUESTION_BY_ID["conditions-term"]
    assert "\n" in conditions_term["prompt"]
    assert (
        conditions_term["prompt"]
        == "Что выведет этот код?\n\nif 3 > 5:\n    print('да')\nelse:\n    print('нет')"
    )

    starters = {
        "conditions-code": "temperature = 22\n# твой код\n",
        "for-loop-code": "# Напиши цикл\n",
        "while-loop-code": "start = 5\n# твой код\n",
    }
    for question_id, starter in starters.items():
        question = QUESTION_BY_ID[question_id]
        assert "def " not in question["prompt"]
        assert "def " not in question["starter"]
        assert question["starter"] == starter

    styles = Path("app/static/styles.css").read_text(encoding="utf-8")
    assert re.search(r"\.question-prompt\s*\{[^}]*white-space:\s*pre-wrap", styles)

    assert QUESTION_BY_ID["conditions-code"]["tests"] == [
        {"kind": "stdout", "expected": "Возьми куртку"}
    ]
    assert QUESTION_BY_ID["for-loop-code"]["tests"] == [
        {"kind": "stdout", "expected": "1\n2\n3\n4\n5"}
    ]
    assert QUESTION_BY_ID["while-loop-code"]["tests"] == [
        {"kind": "stdout", "expected": "5\n4\n3\n2\n1\nПуск!"}
    ]


def test_extended_questions_are_fair_and_exams_are_mixed() -> None:
    extended_lessons = [lesson for lesson in LESSONS if lesson["order"] >= 13]
    choice_positions = [
        question["options"].index(question["answer"])
        for lesson in extended_lessons
        for question in lesson["questions"]
        if question["kind"] == "choice"
    ]
    assert len(set(choice_positions)) > 1
    assert all(0 <= position < 3 for position in choice_positions)
    assert (
        sum(
            len(question["answers"]) > 1
            for lesson in extended_lessons
            for question in lesson["questions"]
            if question["kind"] == "input"
        )
        >= 10
    )
    extended_modules = {lesson["module_id"] for lesson in extended_lessons}
    for module_id in extended_modules:
        question_ids = EXAMS[module_id]["question_ids"]
        assert len(question_ids) == len(set(question_ids)) == 4
        assert {QUESTION_BY_ID[question_id]["kind"] for question_id in question_ids} == {
            "choice",
            "input",
            "code",
        }

    term_question = next(
        question
        for lesson in extended_lessons
        for question in lesson["questions"]
        if question["kind"] == "input" and len(question["answers"]) > 1
    )
    assert all(
        normalize(answer) not in normalize(term_question["placeholder"])
        for answer in term_question["answers"]
    )

    keyword, synonyms = "sorted", ("сортировка",)
    answers = next(
        question["answers"]
        for lesson in extended_lessons
        for question in lesson["questions"]
        if question["kind"] == "input" and keyword in question["answers"]
    )
    assert normalize(f"  {synonyms[0].upper()}  ") in {normalize(answer) for answer in answers}


def test_extended_generation_is_deterministic_and_handles_short_modules(monkeypatch) -> None:
    first = build_extended_course()
    second = build_extended_course()
    assert first == second

    monkeypatch.setattr(
        extended_curriculum,
        "COURSE_UNITS",
        [
            {
                **extended_curriculum.COURSE_UNITS[0],
                "lessons": extended_curriculum.COURSE_UNITS[0]["lessons"][:1],
            }
        ],
    )
    monkeypatch.setattr(
        extended_curriculum, "TASK_CYCLES", [extended_curriculum.TASK_CYCLES[0][:1]]
    )
    _, _, exams = build_extended_course()
    assert len(next(iter(exams.values()))["question_ids"]) == 3
