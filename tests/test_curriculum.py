from app.content import EXAMS, LESSONS, MODULES, QUESTION_BY_ID


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
