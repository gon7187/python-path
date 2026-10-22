import html
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_JS = REPO_ROOT / "app" / "static" / "app.js"
STYLES_CSS = REPO_ROOT / "app" / "static" / "styles.css"

# Грузит app.js в vm с заглушкой DOM и отдаёт splitQuestionPrompt + questionTemplate.
VM_SCRIPT = """
const fs = require('fs');
const vm = require('vm');
const [file, mode, payload] = process.argv.slice(1);
const stub = new Proxy(function () {}, {
  get: (target, key) => (typeof key === 'symbol' || key === 'then' ? undefined : stub),
  set: () => true,
  apply: () => stub,
  construct: () => stub,
});
process.on('unhandledRejection', () => {});
const context = vm.createContext({
  document: stub, window: stub, location: { hash: '' }, localStorage: stub,
  fetch: () => new Promise(() => {}), setTimeout: () => 0, clearTimeout: () => {},
  Element: class {}, console,
});
vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: 'app.js' });
if (mode === 'split') {
  const split = vm.runInContext('splitQuestionPrompt', context);
  console.log(JSON.stringify(JSON.parse(payload).map((prompt) => split(prompt))));
} else {
  const questionTemplate = vm.runInContext('questionTemplate', context);
  console.log(JSON.stringify(JSON.parse(payload).map((question) => questionTemplate(question, 1))));
}
"""


def _node() -> str | None:
    return shutil.which("node")


def _run_vm(mode: str, payload: object) -> Any:
    node = _node()
    if node is None:
        return None
    result = subprocess.run(
        [node, "-e", VM_SCRIPT, str(APP_JS), mode, json.dumps(payload, ensure_ascii=False)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _css_rules() -> list[tuple[str, str]]:
    return re.findall(r"([^{}]+)\{([^{}]*)\}", STYLES_CSS.read_text(encoding="utf-8"))


def _rule_bodies(selector: str) -> str:
    return "\n".join(body for sel, body in _css_rules() if selector in sel)


def _prompt_inner(rendered: str) -> str:
    match = re.search(r'<div class="question-prompt">(.*?)</div>', rendered, re.DOTALL)
    assert match, rendered
    return match.group(1)


def _code_bodies(rendered: str) -> list[str]:
    return [
        html.unescape(body)
        for body in re.findall(
            r'<pre class="code-example"><code>(.*?)</code></pre>', rendered, re.DOTALL
        )
    ]


def test_split_question_prompt_cases() -> None:
    cases = [
        ("Вопрос\nprint(1)", "Вопрос", "print(1)"),
        ("Вопрос\n\n  \nprint(1)\n", "Вопрос", "print(1)"),
        ("Вопрос\n`a = 1\nb = 2`", "Вопрос", "a = 1\nb = 2"),
        ("Вопрос\n`print('a`b')`", "Вопрос", "print('a`b')"),
        ("Вопрос `x`", "Вопрос `x`", ""),
        ("Вопрос\n", "Вопрос", ""),
        ("Вопрос\n  \n\n", "Вопрос", ""),
        ("", "", ""),
    ]
    splits = _run_vm("split", [prompt for prompt, _, _ in cases])
    if splits is None:
        source = APP_JS.read_text(encoding="utf-8")
        assert "function splitQuestionPrompt" in source
        assert "code.startsWith('`') && code.endsWith('`')" in source
        return
    for actual, (prompt, question, code) in zip(splits, cases, strict=True):
        assert actual == {"question": question, "code": code}, prompt


def test_split_function_is_pure_and_does_not_touch_question() -> None:
    # Первая строка уходит в rich(), поэтому бэктики в ней не снимаются, а код
    # рендерится через esc() — угловые скобки не должны становиться разметкой.
    rendered = _run_vm(
        "render",
        [
            {
                "id": "escape",
                "kind": "input",
                "prompt": "Найди ошибку\n`if a < b and c > d:`",
                "placeholder": "Ответ",
            }
        ],
    )
    if rendered is None:
        assert "esc(parts.code)" in APP_JS.read_text(encoding="utf-8")
        return
    html_out = rendered[0]
    assert html.unescape(_prompt_inner(html_out)) == "Найди ошибку"
    assert _code_bodies(html_out) == ["if a < b and c > d:"]
    assert "&lt; b and c &gt;" in html_out


def test_choice_and_input_split_prompt_code_questions_do_not() -> None:
    rendered = _run_vm(
        "render",
        [
            {
                "id": "choice",
                "kind": "choice",
                "prompt": "Что выведет код?\n\n`for i in range(2):\n    print(i)`",
                "options": ["1", "2"],
            },
            {
                "id": "code",
                "kind": "code",
                "prompt": "Напиши функцию\n\ndef f():\n    pass",
                "starter": "def f():\n    pass",
                "hint": "Подсказка",
            },
        ],
    )
    if rendered is None:
        source = APP_JS.read_text(encoding="utf-8")
        assert "question.kind === 'choice' || question.kind === 'input'" in source
        assert "rich(question.prompt)" in source
        return
    choice, code = rendered
    assert _code_bodies(choice) == ["for i in range(2):\n    print(i)"]
    assert html.unescape(_prompt_inner(code)) == "Напиши функцию\n\ndef f():\n    pass"
    assert "code-example" not in code


def test_multiline_option_keeps_original_data_value() -> None:
    option = "x = 1\ny = 2"
    rendered = _run_vm(
        "render",
        [{"id": "options", "kind": "choice", "prompt": "Какой вывод?", "options": [option]}],
    )
    if rendered is None:
        assert "option-multiline" in APP_JS.read_text(encoding="utf-8")
        return
    match = re.search(r'<button\b[^>]*\bdata-value="([^"]*)"[^>]*>', rendered[0])
    assert match, rendered[0]
    assert "option-multiline" in match.group(0)
    assert html.unescape(match.group(1)) == option


def test_option_multiline_css_is_monospace_pre_wrap_and_plain_option_is_not() -> None:
    multiline = _rule_bodies(".option-multiline")
    assert "Source Code Pro" in multiline
    assert "white-space: pre-wrap" in multiline
    plain = [body for selector, body in _css_rules() if re.search(r"\.option(?![\w-])", selector)]
    assert plain
    for body in plain:
        assert "pre-wrap" not in body
        assert "Source Code Pro" not in body
