from app.evaluator import evaluate, run_code


def test_code_runner_checks_function() -> None:
    result = run_code(
        "def double(number):\n    return number * 2\n",
        [{"kind": "call", "call": "double(4)", "expected": 8}],
    )
    assert result["correct"] is True


def test_code_runner_supports_simple_class() -> None:
    result = run_code(
        "class Badge:\n    def label(self, name):\n        return f'Награда: {name}'\n",
        [{"kind": "call", "call": "Badge().label('Старт')", "expected": "Награда: Старт"}],
    )
    assert result["correct"] is True


def test_code_runner_simulates_input_and_returns_console_output() -> None:
    result = run_code(
        "name = input('Имя: ')\nprint(f'Привет, {name}!')\n",
        [{"kind": "stdout", "expected": "Имя: Лена\nПривет, Лена!"}],
        ["Лена"],
    )
    assert result["correct"] is True
    assert result["output"] == "Имя: Лена\nПривет, Лена!\n"


def test_code_runner_explains_when_input_value_is_missing() -> None:
    result = run_code("name = input('Имя: ')\n", [], [])
    assert result["correct"] is False
    assert "не хватает строки" in result["message"]


def test_code_runner_supports_core_learning_builtins() -> None:
    result = run_code(
        "print(isinstance(3, int))\nprint(type('текст'))\n",
        [{"kind": "stdout", "expected": "True\n<class 'str'>"}],
    )
    assert result["correct"] is True


def test_code_runner_blocks_imports() -> None:
    result = run_code("import os\n", [])
    assert result["correct"] is False
    assert "не поддерживает импорт" in result["message"]


def test_choice_answer_is_normalized() -> None:
    question = {"kind": "choice", "answer": "Bool", "explanation": "ok"}
    assert evaluate(question, " bool ")["correct"] is True
