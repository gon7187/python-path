import html
import json
import re
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_JS = REPO_ROOT / "app" / "static" / "app.js"
STYLES_CSS = REPO_ROOT / "app" / "static" / "styles.css"

# Грузит app.js в vm с заглушкой DOM и рисует questionTemplate для каждого вопроса.
RENDER_SCRIPT = """
const fs = require('fs');
const vm = require('vm');
const [file, payload] = process.argv.slice(1);
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
const questionTemplate = vm.runInContext('questionTemplate', context);
const rendered = JSON.parse(payload).map((question) => questionTemplate(question, 1));
console.log(JSON.stringify(rendered));
"""


def _app_js() -> str:
    return APP_JS.read_text(encoding="utf-8")


def _css_rules() -> list[tuple[str, str]]:
    css = STYLES_CSS.read_text(encoding="utf-8")
    return re.findall(r"([^{}]+)\{([^{}]*)\}", css)


def _render(questions: list[dict]) -> list[str] | None:
    node = shutil.which("node")
    if node is None:
        return None
    result = subprocess.run(
        [node, "-e", RENDER_SCRIPT, str(APP_JS), json.dumps(questions, ensure_ascii=False)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _prompt_inner(rendered: str) -> str:
    match = re.search(r'<div class="question-prompt">(.*?)</div>', rendered, re.DOTALL)
    assert match, rendered
    return match.group(1)


def _code_bodies(rendered: str) -> list[str]:
    bodies = re.findall(r'<pre class="code-example"><code>(.*?)</code></pre>', rendered, re.DOTALL)
    return [html.unescape(body) for body in bodies]


def _option_tags(rendered: str) -> list[tuple[str, str]]:
    options = []
    for tag in re.findall(r'<button\b[^>]*\bdata-value="[^"]*"[^>]*>', rendered):
        value = re.search(r'data-value="([^"]*)"', tag)
        assert value, tag
        options.append((tag, html.unescape(value.group(1))))
    return options


def _applied_style(tag: str) -> str:
    chunks = []
    classes = re.search(r'class="([^"]*)"', tag)
    for cls in classes.group(1).split() if classes else []:
        for selector, body in _css_rules():
            if re.search(rf"\.{re.escape(cls)}(?![\w-])", selector):
                chunks.append(body)
    style = re.search(r'style="([^"]*)"', tag)
    if style:
        chunks.append(style.group(1))
    return "\n".join(chunks)


def _assert_source_has_code_block_template() -> None:
    js = _app_js()
    count = len(re.findall(r'<pre class="code-example"><code>\$\{esc\(', js))
    assert count >= 2, "в questionTemplate нет блока кода с esc() для prompt"


def test_c1_choice_prompt_first_line_is_text_and_rest_is_code_block() -> None:
    question = {
        "id": "c1-choice",
        "kind": "choice",
        "prompt": 'Что выведет код?\n\n\nx = `y`\nprint(x < 2 and "a" in x)\n\n',
        "options": ["1", "2"],
    }
    rendered = _render([question])
    if rendered is None:
        _assert_source_has_code_block_template()
        return
    html_out = rendered[0]
    assert html.unescape(_prompt_inner(html_out)) == "Что выведет код?"
    assert _code_bodies(html_out) == ['x = `y`\nprint(x < 2 and "a" in x)']


def test_c1_input_prompt_strips_wrapping_backticks_from_code_block() -> None:
    question = {
        "id": "c1-input",
        "kind": "input",
        "prompt": "Что выведет код?\n`for i in range(2):\n    print(i)`",
        "placeholder": "Введите ответ",
    }
    rendered = _render([question])
    if rendered is None:
        _assert_source_has_code_block_template()
        return
    html_out = rendered[0]
    assert html.unescape(_prompt_inner(html_out)) == "Что выведет код?"
    assert _code_bodies(html_out) == ["for i in range(2):\n    print(i)"]


def test_c1_first_line_keeps_inline_code_rendering() -> None:
    question = {
        "id": "c1-rich",
        "kind": "input",
        "prompt": "Какой тип у `x`?\nx = 1",
        "placeholder": "Введите ответ",
    }
    rendered = _render([question])
    if rendered is None:
        _assert_source_has_code_block_template()
        return
    html_out = rendered[0]
    assert '<code class="inline-code">x</code>' in _prompt_inner(html_out)
    assert _code_bodies(html_out) == ["x = 1"]


def test_c2_single_line_prompt_has_no_code_block() -> None:
    questions = [
        {
            "id": "c2-line",
            "kind": "choice",
            "prompt": "Что выведет `print(1)`?",
            "options": ["1", "2"],
        },
        {
            "id": "c2-trailing",
            "kind": "input",
            "prompt": "Что выведет код?\n\n",
            "placeholder": "Введите ответ",
        },
    ]
    rendered = _render(questions)
    if rendered is None:
        assert "rich(question.prompt)" in _app_js()
        return
    single, trailing = rendered
    assert '<code class="inline-code">print(1)</code>' in _prompt_inner(single)
    assert "code-example" not in single
    assert html.unescape(_prompt_inner(trailing)) == "Что выведет код?"
    assert "code-example" not in trailing


def test_c2_code_question_prompt_is_rendered_whole() -> None:
    question = {
        "id": "c2-code",
        "kind": "code",
        "prompt": "Напиши функцию\n\ndef f():\n    pass",
        "starter": "def f():\n    pass",
        "hint": "Подсказка",
    }
    rendered = _render([question])
    if rendered is None:
        assert 'class="code-editor"' in _app_js()
        return
    html_out = rendered[0]
    assert html.unescape(_prompt_inner(html_out)) == "Напиши функцию\n\ndef f():\n    pass"
    assert "code-example" not in html_out
    assert 'class="code-editor"' in html_out


def test_c3_multiline_option_is_monospace_pre_wrap_and_single_line_is_not() -> None:
    question = {
        "id": "c3-choice",
        "kind": "choice",
        "prompt": "Какой вывод?",
        "options": ["x = 1\ny = 2", "print(x)"],
    }
    rendered = _render([question])
    if rendered is None:
        assert (
            any(
                "pre-wrap" in body and "Source Code Pro" in body and ".option" in selector
                for selector, body in _css_rules()
            )
            or "white-space: pre-wrap" in _app_js()
        )
        return
    options = _option_tags(rendered[0])
    multi = [tag for tag, value in options if value == "x = 1\ny = 2"]
    single = [tag for tag, value in options if value == "print(x)"]
    assert len(multi) == 1 and len(single) == 1, rendered[0]
    multi_style = _applied_style(multi[0])
    assert "pre-wrap" in multi_style
    assert "Source Code Pro" in multi_style or "monospace" in multi_style
    single_style = _applied_style(single[0])
    assert "pre-wrap" not in single_style
    assert "Source Code Pro" not in single_style


def test_c4_split_logic_table_and_option_css_rules() -> None:
    cases = [
        ("Вопрос\nprint(1)", "Вопрос", ["print(1)"]),
        ("Вопрос\n\n  \nprint(1)\n", "Вопрос", ["print(1)"]),
        ("Вопрос\n`a = 1\nb = 2`", "Вопрос", ["a = 1\nb = 2"]),
        ("Вопрос `x`", 'Вопрос <code class="inline-code">x</code>', []),
        ("Вопрос\n", "Вопрос", []),
    ]
    questions = [
        {"id": f"c4-{index}", "kind": "choice", "prompt": prompt, "options": ["1", "2"]}
        for index, (prompt, _, _) in enumerate(cases)
    ]
    rendered = _render(questions)
    if rendered is None:
        _assert_source_has_code_block_template()
        return
    for html_out, (prompt, prompt_html, bodies) in zip(rendered, cases, strict=True):
        assert _prompt_inner(html_out) == prompt_html, prompt
        assert _code_bodies(html_out) == bodies, prompt
