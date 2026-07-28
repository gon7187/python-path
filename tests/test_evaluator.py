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


def test_code_runner_can_require_unpacking_assignment() -> None:
    tests = [
        {"kind": "source", "requires": "unpacking", "name": "profile"},
        {"kind": "call", "call": "describe(('Лена', 3, True))", "expected": "Лена: 3, готов"},
    ]
    indexed = (
        "def describe(profile):\n"
        "    status = 'готов' if profile[2] else 'не готов'\n"
        "    return f'{profile[0]}: {profile[1]}, {status}'\n"
    )
    unpacked = (
        "def describe(profile):\n"
        "    name, level, is_ready = profile\n"
        "    status = 'готов' if is_ready else 'не готов'\n"
        "    return f'{name}: {level}, {status}'\n"
    )
    bypass = (
        "def describe(profile):\n"
        "    unused, also_unused = 1, 2\n"
        "    status = 'готов' if profile[2] else 'не готов'\n"
        "    return f'{profile[0]}: {profile[1]}, {status}'\n"
    )
    alias_bypass = (
        "def describe(profile):\n"
        "    name, level, is_ready = profile\n"
        "    alias = profile\n"
        "    status = 'готов' if alias[2] else 'не готов'\n"
        "    return f'{alias[0]}: {alias[1]}, {status}'\n"
    )

    rejected = run_code(indexed, tests)
    accepted = run_code(unpacked, tests)
    bypassed = run_code(bypass, tests)
    alias_bypassed = run_code(alias_bypass, tests)

    assert rejected["correct"] is False
    assert "распаков" in rejected["message"].casefold()
    assert bypassed["correct"] is False
    assert alias_bypassed["correct"] is False
    assert accepted["correct"] is True


def test_code_runner_unpacking_restricted_to_function() -> None:
    tests = [
        {
            "kind": "source",
            "requires": "unpacking",
            "name": "profile",
            "function": "describe",
        },
        {"kind": "call", "call": "describe(('Лена', 3, True))", "expected": "Лена: 3, готов"},
    ]
    bypass = (
        "def unused(profile):\n"
        "    name, level, is_ready = profile\n"
        "\n"
        "def describe(profile):\n"
        "    values = dict(enumerate(profile))\n"
        "    status = 'готов' if values.get(2) else 'не готов'\n"
        '    return f"{values.get(0)}: {values.get(1)}, {status}"\n'
    )
    unpacked = (
        "def describe(profile):\n"
        "    name, level, is_ready = profile\n"
        "    status = 'готов' if is_ready else 'не готов'\n"
        "    return f'{name}: {level}, {status}'\n"
    )

    assert run_code(bypass, tests)["correct"] is False
    assert run_code(unpacked, tests)["correct"] is True
