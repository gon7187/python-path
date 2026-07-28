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


def test_code_runner_blocks_imports() -> None:
    result = run_code("import os\n", [])
    assert result["correct"] is False
    assert "не поддерживает импорт" in result["message"]


def test_choice_answer_is_normalized() -> None:
    question = {"kind": "choice", "answer": "Bool", "explanation": "ok"}
    assert evaluate(question, " bool ")["correct"] is True
