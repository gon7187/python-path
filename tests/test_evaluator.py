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


def test_code_runner_supports_expected_value_error_handling() -> None:
    result = run_code(
        "try:\n    number = int('кот')\n    print(number)\nexcept ValueError:\n    print('Нужны цифры')\n",
        [{"kind": "stdout", "expected": "Нужны цифры"}],
    )
    assert result["correct"] is True


def test_code_runner_blocks_unsafe_imports() -> None:
    result = run_code("import os\n", [])
    assert result["correct"] is False
    assert "Модуль os" in result["message"]


def test_code_runner_supports_allowlisted_modules_and_virtual_files() -> None:
    result = run_code(
        "from pathlib import Path\n"
        "import math\n"
        "path = Path('answer.txt')\n"
        "path.write_text(str(math.sqrt(81)))\n"
        "print(path.read_text())\n",
        [{"kind": "stdout", "expected": "9.0"}],
    )
    assert result["correct"] is True


def test_code_runner_supports_safe_async_examples() -> None:
    result = run_code(
        "import asyncio\n"
        "async def main():\n"
        "    await asyncio.sleep(0)\n"
        "    return 'готово'\n"
        "print(asyncio.run(main()))\n",
        [{"kind": "stdout", "expected": "готово"}],
    )
    assert result["correct"] is True


def test_parsons_answer_checks_order() -> None:
    question = {
        "kind": "parsons",
        "answer": ["line-1", "line-2"],
        "explanation": "Порядок важен.",
    }
    assert evaluate(question, '["line-1", "line-2"]')["correct"] is True
    assert evaluate(question, '["line-2", "line-1"]')["correct"] is False


def test_syntax_error_points_to_the_next_step() -> None:
    result = run_code("if True\n    print('да')\n", [])
    assert result["correct"] is False
    assert "двоеточия" in result["message"]
    assert "Строка 1" in result["message"]


def test_choice_answer_is_normalized() -> None:
    question = {"kind": "choice", "answer": "Bool", "explanation": "ok"}
    assert evaluate(question, " bool ")["correct"] is True
