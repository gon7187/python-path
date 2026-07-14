from app.content import EXAMS, LESSONS, MODULES, QUESTION_BY_ID


def test_full_course_has_139_progressive_lessons() -> None:
    assert len(MODULES) == 32
    assert len(LESSONS) == 139
    assert [lesson["order"] for lesson in LESSONS] == list(range(1, 140))
    assert len({lesson["id"] for lesson in LESSONS}) == 139


def test_every_lesson_has_material_and_exercises() -> None:
    assert len(QUESTION_BY_ID) == 417
    for lesson in LESSONS:
        assert len(lesson["theory"]) >= 4
        assert len(lesson["questions"]) == 3
        assert {question["kind"] for question in lesson["questions"]} == {
            "choice",
            "input",
            "code",
        }
        assert all(question["guide"] for question in lesson["questions"])


def test_extended_lessons_have_full_learning_scaffold() -> None:
    extended_lessons = LESSONS[31:]

    assert len(extended_lessons) == 108
    assert all(len(lesson["theory"]) >= 6 for lesson in extended_lessons)
    assert all(
        "шаг" in question["guide"].lower() or "пример" in question["guide"].lower()
        for lesson in extended_lessons
        for question in lesson["questions"]
    )


def test_every_module_has_a_valid_exam() -> None:
    assert set(EXAMS) == {module["id"] for module in MODULES}
    for exam in EXAMS.values():
        assert len(exam["question_ids"]) >= 4
        assert all(question_id in QUESTION_BY_ID for question_id in exam["question_ids"])
