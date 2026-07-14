from app.content import EXAMS, LESSONS, MODULES, QUESTION_BY_ID, public_question


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
    assert QUESTION_BY_ID["warmup-variables-code"]["starter"] == "pet = 'кот'\nprint('pet')\n"


def test_tasks_only_use_syntax_already_explained() -> None:
    function_lesson_index = next(
        index for index, lesson in enumerate(LESSONS) if lesson["id"] == "functions"
    )
    early_starters = [
        question.get("starter", "")
        for lesson in LESSONS[:function_lesson_index]
        for question in lesson["questions"]
    ]
    all_starters = [
        question.get("starter", "") for lesson in LESSONS for question in lesson["questions"]
    ]

    assert all("def " not in starter for starter in early_starters)
    assert all("pass" not in starter for starter in all_starters)


def test_every_module_has_a_valid_exam() -> None:
    assert set(EXAMS) == {module["id"] for module in MODULES}
    for exam in EXAMS.values():
        assert len(exam["question_ids"]) >= 4
        assert all(question_id in QUESTION_BY_ID for question_id in exam["question_ids"])
