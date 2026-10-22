import ast
import importlib
from pathlib import Path
from typing import Any

import pytest

from app.evaluator import evaluate, run_code

APP_DIR = Path(__file__).resolve().parents[1] / "app"
MODULE_NAME = "app.handwritten.lessons_oop"
MODULE_PATH = APP_DIR / "handwritten" / "lessons_oop.py"
LESSON_SPECS = {
    "oop-design-init": (65, "Конструктор"),
    "oop-design-repr-str": (66, "__repr__ и __str__"),
    "oop-design-class-instance": (67, "Атрибуты класса и экземпляра"),
    "oop-design-composition": (68, "Композиция"),
    "oop-advanced-inheritance": (69, "Наследование"),
    "oop-advanced-properties": (70, "Свойства"),
    "oop-advanced-protocols": (71, "Абстракции и протоколы"),
    "oop-advanced-special-methods": (72, "Специальные методы"),
}
LESSON_IDS = list(LESSON_SPECS)
FORBIDDEN_PHRASES = (
    "Когда это применять",
    "Сформулируй правило своими словами",
    "Ориентир:",
    "относится к теме",
)
OUTPUT_MARKER = "# Вывод:"
PREDICT_WORDS = ("выведет", "напечатает")
UNDERSTANDING_WORDS = (
    "вывод",
    "выведет",
    "напечатает",
    "верн",
    "будет",
    "ошиб",
    "выбери",
    "найди",
    "какой код",
)
NAME_RECALL_WORDS = ("название", "называ")
FORM_FEATURES = {
    "обратные кавычки": lambda text: "`" in text,
    "точка в конце": lambda text: text.rstrip().endswith("."),
    "заглавная первая буква": lambda text: text[:1].isupper(),
    "скобки": lambda text: any(char in text for char in "()[]{}"),
}


def _registry() -> dict[str, dict[str, Any]]:
    try:
        return importlib.import_module("app.handwritten").HANDWRITTEN
    except Exception as error:
        raise AssertionError(f"app.handwritten не собирает реестр: {error!r}") from error


def _course() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    try:
        from app.content import LESSON_BY_ID, LESSONS
    except Exception as error:
        raise AssertionError(f"app.content не собирает курс: {error!r}") from error
    return LESSONS, LESSON_BY_ID


def _declared_lessons() -> list[dict[str, Any]]:
    assert MODULE_PATH.is_file(), f"нет файла {MODULE_PATH.name} в app/handwritten"
    try:
        lessons = importlib.import_module(MODULE_NAME).LESSONS
    except Exception as error:
        raise AssertionError(f"{MODULE_NAME} не импортируется: {error!r}") from error
    assert isinstance(lessons, list), "LESSONS должен быть списком уроков"
    assert all(isinstance(lesson, dict) for lesson in lessons), "каждый урок должен быть словарём"
    return lessons


def _lesson(lesson_id: str) -> dict[str, Any]:
    registry = _registry()
    assert lesson_id in registry, f"нет рукописного урока {lesson_id}"
    return registry[lesson_id]


def _cards(lesson_id: str) -> list[dict[str, Any]]:
    theory = _lesson(lesson_id).get("theory", [])
    assert len(theory) == 3, (lesson_id, "нужно ровно 3 карточки")
    assert all(isinstance(card, dict) for card in theory), lesson_id
    return theory


def _questions(lesson_id: str) -> list[dict[str, Any]]:
    questions = _lesson(lesson_id).get("questions", [])
    assert len(questions) == 3, (lesson_id, "нужно ровно 3 задания")
    assert all(isinstance(question, dict) for question in questions), lesson_id
    return questions


def _code_question(lesson_id: str) -> dict[str, Any]:
    code = _questions(lesson_id)[2]
    assert code.get("kind") == "code", lesson_id
    assert isinstance(code.get("reference"), str), lesson_id
    return code


def _call(call: str, expected: Any) -> dict[str, Any]:
    return {"kind": "call", "call": call, "expected": expected}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list | tuple):
        return [text for item in value for text in _strings(item)]
    return []


def _declared_output(example: str) -> list[str]:
    """Строки вывода из комментария «# Вывод:» — то, что пример должен напечатать."""
    lines = example.splitlines()
    marks = [index for index, line in enumerate(lines) if line.strip().startswith(OUTPUT_MARKER)]
    if not marks:
        return []
    start = marks[0]
    declared = []
    head = lines[start].strip()[len(OUTPUT_MARKER) :].strip()
    if head:
        declared.append(head)
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("#"):
            break
        text = stripped[1:].strip()
        if text:
            declared.append(text)
    return declared


def _parses(source: str) -> bool:
    try:
        ast.parse(source)
    except SyntaxError:
        return False
    return True


def _assert_calls(source: str, calls: list[dict[str, Any]]) -> None:
    result = run_code(source, calls)
    assert result["error"] is None, result["error"]
    assert result["correct"] is True, result["checks"]


def _assert_starter_stub(code: dict[str, Any], names: set[str]) -> None:
    starter = ast.parse(code.get("starter", ""))
    defined = {
        node.name for node in ast.walk(starter) if isinstance(node, ast.ClassDef | ast.FunctionDef)
    }
    assert names <= defined, (names, defined)
    assert any(isinstance(node, ast.Pass) for node in ast.walk(starter)), "starter без pass"


def _class_def(tree: ast.Module, name: str) -> ast.ClassDef:
    found = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name]
    assert found, f"нет class {name}"
    return found[0]


def _def(scope: ast.ClassDef | ast.Module, name: str) -> ast.FunctionDef:
    found = [node for node in scope.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert found, f"нет def {name}"
    return found[0]


def _params(function: ast.FunctionDef) -> list[str]:
    return [arg.arg for arg in function.args.args]


def _self_attributes(function: ast.FunctionDef) -> set[str]:
    return {
        target.attr
        for node in ast.walk(function)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
    }


def _class_attributes(cls: ast.ClassDef) -> dict[str, ast.expr]:
    attributes: dict[str, ast.expr] = {}
    for node in cls.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attributes[target.id] = node.value
    return attributes


def _is_super_init_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "__init__"
        and isinstance(node.func.value, ast.Call)
        and isinstance(node.func.value.func, ast.Name)
        and node.func.value.func.id == "super"
    )


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c1_lessons_module_declares_its_lesson(lesson_id: str) -> None:
    lessons = _declared_lessons()
    assert lesson_id in [lesson.get("id") for lesson in lessons], lesson_id


def test_c1_lessons_module_declares_exactly_eight_lessons() -> None:
    lessons = _declared_lessons()
    assert sorted(str(lesson.get("id")) for lesson in lessons) == sorted(LESSON_IDS)


def test_c1_registry_exposes_all_eight_ids() -> None:
    registry = _registry()
    missing = sorted(set(LESSON_IDS) - set(registry))
    assert not missing, f"нет в app.handwritten.HANDWRITTEN: {missing}"
    for lesson_id in LESSON_IDS:
        assert registry[lesson_id].get("id") == lesson_id, lesson_id


def test_c1_course_keeps_120_lessons_with_oop_orders_and_titles() -> None:
    lessons, lesson_by_id = _course()
    assert len(lessons) == 120
    assert [lesson["order"] for lesson in lessons] == list(range(1, 121))
    for lesson_id, (order, title) in LESSON_SPECS.items():
        assert lesson_id in lesson_by_id, lesson_id
        assert lesson_by_id[lesson_id]["order"] == order, lesson_id
        assert lesson_by_id[lesson_id]["title"] == title, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_has_three_cards_with_text_and_example(lesson_id: str) -> None:
    lesson = _lesson(lesson_id)
    assert lesson["id"] == lesson_id
    for card in _cards(lesson_id):
        for key in ("title", "text", "example"):
            assert isinstance(card.get(key), str) and card[key].strip(), (lesson_id, key)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_runnable_cards_execute_in_runner(lesson_id: str) -> None:
    for card in _cards(lesson_id):
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_questions_have_choice_input_code_ids(lesson_id: str) -> None:
    questions = _questions(lesson_id)
    assert [question.get("id") for question in questions] == [
        f"{lesson_id}-choice",
        f"{lesson_id}-term",
        f"{lesson_id}-code",
    ]
    assert [question.get("kind") for question in questions] == ["choice", "input", "code"]


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_choice_has_unique_options_and_answer_among_them(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    options = choice["options"]
    assert len(options) >= 3, lesson_id
    assert len(set(options)) == len(options), (lesson_id, "варианты повторяются")
    assert choice["answer"] in options, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_input_has_short_nonempty_answers(lesson_id: str) -> None:
    term = _questions(lesson_id)[1]
    answers = term["answers"]
    assert isinstance(answers, list) and answers, lesson_id
    for answer in answers:
        assert isinstance(answer, str) and answer.strip(), lesson_id
        assert len(answer) <= 40, (lesson_id, answer)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_every_question_has_explanation_and_code_has_hint(lesson_id: str) -> None:
    choice, term, code = _questions(lesson_id)
    for question in (choice, term, code):
        assert isinstance(question.get("explanation"), str), (lesson_id, question.get("id"))
        assert question["explanation"].strip(), (lesson_id, question.get("id"))
    assert isinstance(code.get("hint"), str) and code["hint"].strip(), lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_code_reference_passes_and_starter_fails(lesson_id: str) -> None:
    code = _code_question(lesson_id)
    assert isinstance(code.get("tests"), list) and len(code["tests"]) >= 2, lesson_id
    assert isinstance(code.get("starter"), str), lesson_id
    assert evaluate(code, code["reference"])["correct"] is True, lesson_id
    assert evaluate(code, code["starter"])["correct"] is False, lesson_id


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c2_lesson_has_no_generator_template_phrases(lesson_id: str) -> None:
    for text in _strings(_lesson(lesson_id)):
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in text, (lesson_id, phrase)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_third_card_is_typical_mistake(lesson_id: str) -> None:
    theory = _cards(lesson_id)
    assert "ошиб" in theory[2]["title"].casefold(), (lesson_id, theory[2]["title"])
    assert "ошиб" not in theory[0]["title"].casefold(), (lesson_id, theory[0]["title"])
    assert "ошиб" not in theory[1]["title"].casefold(), (lesson_id, theory[1]["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_every_example_declares_output(lesson_id: str) -> None:
    for card in _cards(lesson_id):
        assert OUTPUT_MARKER in card["example"], (lesson_id, card["title"])
        assert _declared_output(card["example"]), (lesson_id, card["title"], "вывод пустой")


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_declared_output_matches_real_stdout(lesson_id: str) -> None:
    for card in _cards(lesson_id):
        if card.get("run") is False:
            continue
        result = run_code(card["example"], [])
        assert result["error"] is None, (lesson_id, card["title"], result["error"])
        actual = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
        assert _declared_output(card["example"]) == actual, (lesson_id, card["title"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_asks_to_predict_or_find_not_recall_name(lesson_id: str) -> None:
    prompt = _questions(lesson_id)[0]["prompt"].casefold()
    assert any(word in prompt for word in UNDERSTANDING_WORDS), (lesson_id, prompt)
    assert not any(word in prompt for word in NAME_RECALL_WORDS), (lesson_id, prompt)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_predicted_output_choice_matches_real_run(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    head, _, body = choice["prompt"].partition("\n\n")
    if not any(word in head.casefold() for word in PREDICT_WORDS):
        return
    assert body.strip(), (lesson_id, "предсказание вывода без кода")
    result = run_code(body, [])
    assert result["error"] is None, (lesson_id, result["error"])
    assert result["stdout"].strip() == choice["answer"].strip(), (
        lesson_id,
        result["stdout"],
        choice["answer"],
    )


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c3_choice_answer_does_not_stand_out_by_form_or_length(lesson_id: str) -> None:
    choice = _questions(lesson_id)[0]
    options = choice["options"]
    answer = choice["answer"]
    assert 3 <= len(options) <= 4, (lesson_id, options)

    for name, feature in FORM_FEATURES.items():
        values = [feature(option) for option in options]
        if len(set(values)) > 1:
            assert values.count(feature(answer)) > 1, (lesson_id, name, answer)

    lengths = [len(option) for option in options]
    assert max(lengths) <= 1.6 * min(lengths), (lesson_id, lengths)
    others = [len(option) for option in options if option != answer]
    assert min(others) <= len(answer) <= max(others), (lesson_id, answer)


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_run_false_only_where_runner_rejects_example(lesson_id: str) -> None:
    for card in _cards(lesson_id):
        flag = card.get("run", True)
        assert flag in (True, False), (lesson_id, card["title"], flag)
        result = run_code(card["example"], [])
        if flag is False:
            assert result["error"] is not None, (lesson_id, card["title"], "пример исполняется")
            assert result["error"].startswith("ValueError"), (lesson_id, result["error"])
        else:
            assert result["error"] is None, (lesson_id, card["title"], result["error"])


@pytest.mark.parametrize("lesson_id", LESSON_IDS)
def test_c4_every_example_is_real_python_even_without_run(lesson_id: str) -> None:
    for card in _cards(lesson_id):
        assert _parses(card["example"]), (lesson_id, card["title"])


def test_k65_point_distance_to_origin_and_x() -> None:
    code = _code_question("oop-design-init")
    tree = ast.parse(code["reference"])
    point = _class_def(tree, "Point")
    assert _params(_def(point, "__init__")) == ["self", "x", "y"]
    assert _params(_def(point, "distance_to_origin")) == ["self"]
    _assert_starter_stub(code, {"Point"})
    _assert_calls(
        code["reference"],
        [
            _call("Point(3, 4).distance_to_origin()", 5.0),
            _call("Point(0, 0).x", 0),
        ],
    )


def test_k66_money_str_and_repr() -> None:
    code = _code_question("oop-design-repr-str")
    tree = ast.parse(code["reference"])
    money = _class_def(tree, "Money")
    assert _params(_def(money, "__init__")) == ["self", "amount", "currency"]
    _def(money, "__str__")
    _def(money, "__repr__")
    _assert_starter_stub(code, {"Money"})
    _assert_calls(
        code["reference"],
        [
            _call("str(Money(100, 'RUB'))", "100 RUB"),
            _call("repr(Money(5, 'USD'))", "Money(5, 'USD')"),
        ],
    )


def test_k67_cat_species_is_class_attribute_and_name_is_instance_attribute() -> None:
    code = _code_question("oop-design-class-instance")
    tree = ast.parse(code["reference"])
    cat = _class_def(tree, "Cat")
    species = _class_attributes(cat).get("species")
    assert isinstance(species, ast.Constant) and species.value == "кошка", (
        "species не атрибут класса"
    )
    init = _def(cat, "__init__")
    assert _params(init) == ["self", "name"]
    assert "name" in _self_attributes(init), "name должен быть атрибутом экземпляра"
    _assert_starter_stub(code, {"Cat"})
    _assert_calls(
        code["reference"],
        [
            _call("Cat('Мурка').species", "кошка"),
            _call("Cat('Барсик').name", "Барсик"),
        ],
    )


def test_k68_car_composes_engine_without_inheritance() -> None:
    code = _code_question("oop-design-composition")
    tree = ast.parse(code["reference"])
    engine = _class_def(tree, "Engine")
    assert _params(_def(engine, "__init__")) == ["self", "power"]
    car = _class_def(tree, "Car")
    assert _params(_def(car, "__init__")) == ["self", "engine"]
    assert "engine" in _self_attributes(_def(car, "__init__")), "Car должен хранить engine"
    assert not car.bases, "Car не должен наследовать Engine: здесь композиция"
    _def(car, "describe")
    _assert_starter_stub(code, {"Engine", "Car"})
    _assert_calls(
        code["reference"],
        [_call("Car(Engine(150)).describe()", "Машина с двигателем 150 л.с.")],
    )


def test_k69_dog_inherits_animal_and_calls_super_init() -> None:
    code = _code_question("oop-advanced-inheritance")
    tree = ast.parse(code["reference"])
    animal = _class_def(tree, "Animal")
    assert _params(_def(animal, "__init__")) == ["self", "name"]
    dog = _class_def(tree, "Dog")
    assert len(dog.bases) == 1 and isinstance(dog.bases[0], ast.Name), "Dog должен наследовать"
    assert dog.bases[0].id == "Animal", "Dog должен наследовать Animal"
    assert any(_is_super_init_call(node) for node in ast.walk(dog)), "нужен super().__init__()"
    _def(dog, "speak")
    _assert_starter_stub(code, {"Animal", "Dog"})
    _assert_calls(
        code["reference"],
        [
            _call("Dog('Шарик').speak()", "Шарик: Гав"),
            _call("Dog('Шарик').name", "Шарик"),
        ],
    )


def test_k70_temperature_fahrenheit_is_property() -> None:
    code = _code_question("oop-advanced-properties")
    tree = ast.parse(code["reference"])
    temperature = _class_def(tree, "Temperature")
    assert _params(_def(temperature, "__init__")) == ["self", "celsius"]
    fahrenheit = _def(temperature, "fahrenheit")
    assert any(
        isinstance(decorator, ast.Name) and decorator.id == "property"
        for decorator in fahrenheit.decorator_list
    ), "fahrenheit должен быть @property"
    _assert_starter_stub(code, {"Temperature"})
    _assert_calls(
        code["reference"],
        [
            _call("Temperature(100).fahrenheit", 212.0),
            _call("Temperature(0).fahrenheit", 32.0),
        ],
    )


def test_k71_total_area_works_by_duck_typing() -> None:
    code = _code_question("oop-advanced-protocols")
    tree = ast.parse(code["reference"])
    square = _class_def(tree, "Square")
    assert _params(_def(square, "__init__")) == ["self", "side"]
    _def(square, "area")
    rect = _class_def(tree, "Rect")
    assert _params(_def(rect, "__init__")) == ["self", "w", "h"]
    _def(rect, "area")
    total_area = _def(tree, "total_area")
    assert _params(total_area) == ["shapes"]
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "isinstance"
        for node in ast.walk(total_area)
    ), "total_area не должен проверять класс через isinstance"
    _assert_starter_stub(code, {"Square", "Rect", "total_area"})
    _assert_calls(
        code["reference"],
        [
            _call("total_area([Square(2), Rect(2, 3)])", 10),
            _call("total_area([])", 0),
        ],
    )


def test_k72_vector_add_and_eq() -> None:
    code = _code_question("oop-advanced-special-methods")
    tree = ast.parse(code["reference"])
    vector = _class_def(tree, "Vector")
    assert _params(_def(vector, "__init__")) == ["self", "x", "y"]
    _def(vector, "__add__")
    _def(vector, "__eq__")
    _assert_starter_stub(code, {"Vector"})
    _assert_calls(
        code["reference"],
        [
            _call("(Vector(1, 2) + Vector(3, 4)) == Vector(4, 6)", True),
            _call("(Vector(0, 0) == Vector(0, 1)) is False", True),
        ],
    )
