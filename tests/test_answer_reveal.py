import json
import re
import shutil
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from app.content import EXAMS, LESSONS, QUESTION_BY_ID
from app.db import save_lesson
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_JS = REPO_ROOT / "app" / "static" / "app.js"
STYLES_CSS = REPO_ROOT / "app" / "static" / "styles.css"

# Вызывает showVerdict из app.js с заглушкой DOM и возвращает className и innerHTML узла результата.
VERDICT_SCRIPT = """
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
const rendered = JSON.parse(payload).map((result) => {
  const fields = { className: '', innerHTML: '' };
  const node = new Proxy(fields, {
    get: (target, key) => (key in target ? target[key] : stub),
    set: (target, key, value) => { target[key] = value; return true; },
  });
  const document = new Proxy(function () {}, {
    get: (target, key) => (key === 'querySelector' ? () => node : stub),
    set: () => true,
    apply: () => stub,
    construct: () => stub,
  });
  const context = vm.createContext({
    document, window: stub, location: { hash: '' }, localStorage: stub,
    fetch: () => new Promise(() => {}), setTimeout: () => 0, clearTimeout: () => {},
    Element: class {}, console,
  });
  vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: 'app.js' });
  context.showVerdict('q', result);
  return { className: fields.className, innerHTML: fields.innerHTML };
});
console.log(JSON.stringify(rendered));
"""

WRONG_LESSON_ANSWERS = [
    ("hello-choice", "text('Привет')"),
    ("hello-term", "неверно"),
    ("hello-code", "if True print('Привет')"),
]
NEUTRAL_MESSAGE = "Пока неверно. Перечитай код и попробуй ещё раз."


def _explanation(question_id: str) -> str:
    explanation = QUESTION_BY_ID[question_id]["explanation"]
    assert explanation.strip(), question_id
    return explanation


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def _assert_hides_explanation(body: dict, question_id: str) -> None:
    explanation = _explanation(question_id)
    assert body["correct"] is False, question_id
    assert not body.get("explanation"), question_id
    assert isinstance(body.get("message"), str) and body["message"].strip(), question_id
    assert body["message"] != explanation, question_id
    assert all(explanation not in text for text in _strings(body)), question_id


def _css_rules() -> list[tuple[str, str]]:
    css = STYLES_CSS.read_text(encoding="utf-8")
    return re.findall(r"([^{}]+)\{([^{}]*)\}", css)


def _margin_bottom(body: str) -> float | None:
    longhand = re.findall(r"margin-bottom:\s*(-?\d+(?:\.\d+)?)px", body)
    if longhand:
        return float(longhand[-1])
    shorthand = re.findall(r"(?<![\w-])margin:\s*([^;]+)", body)
    if not shorthand:
        return None
    sides = shorthand[-1].split()
    # margin: all | vertical horizontal | top horizontal bottom | top right bottom left
    bottom_index = {1: 0, 2: 0, 3: 2, 4: 2}.get(len(sides))
    if bottom_index is None:
        return None
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)px", sides[bottom_index])
    return float(match.group(1)) if match else None


def _render_verdicts(results: list[dict]) -> list[dict] | None:
    node = shutil.which("node")
    if node is None:
        return None
    result = subprocess.run(
        [node, "-e", VERDICT_SCRIPT, str(APP_JS), json.dumps(results, ensure_ascii=False)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_c1_wrong_lesson_check_hides_explanation_for_choice_input_and_code() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        wrong = {
            question_id: client.post(
                "/api/lessons/hello/check", json={"question_id": question_id, "answer": answer}
            )
            for question_id, answer in WRONG_LESSON_ANSWERS
        }
        correct = client.post(
            "/api/lessons/hello/check",
            json={"question_id": "hello-choice", "answer": "print('Привет')"},
        )
        client.post("/api/reset")

    for question_id, response in wrong.items():
        assert response.status_code == 200, question_id
        _assert_hides_explanation(response.json(), question_id)

    assert correct.status_code == 200
    assert correct.json()["correct"] is True
    assert correct.json()["explanation"] == _explanation("hello-choice")


def test_c2_wrong_practice_and_code_check_hide_explanation() -> None:
    with TestClient(app) as client:
        client.post("/api/reset")
        wrong_practice = {
            question_id: client.post(
                "/api/practice/submit", json={"question_id": question_id, "answer": answer}
            )
            for question_id, answer in WRONG_LESSON_ANSWERS
        }
        wrong_code = client.post(
            "/api/code/check", json={"question_id": "hello-code", "answer": "def broken(:"}
        )
        correct_practice = client.post(
            "/api/practice/submit",
            json={"question_id": "hello-choice", "answer": "print('Привет')"},
        )
        correct_code = client.post(
            "/api/code/check",
            json={"question_id": "hello-code", "answer": "print('Я начинаю путь в Python!')"},
        )
        client.post("/api/reset")

    for question_id, response in wrong_practice.items():
        assert response.status_code == 200, question_id
        _assert_hides_explanation(response.json(), question_id)

    assert wrong_code.status_code == 200
    _assert_hides_explanation(wrong_code.json(), "hello-code")

    assert correct_practice.status_code == 200
    assert correct_practice.json()["correct"] is True
    assert correct_practice.json()["explanation"] == _explanation("hello-choice")

    assert correct_code.status_code == 200
    assert correct_code.json()["correct"] is True
    assert correct_code.json()["explanation"] == _explanation("hello-code")


def test_c3_lesson_and_exam_grading_keep_explanation_per_question() -> None:
    module_id = "start"
    exam_question_ids = EXAMS[module_id]["question_ids"]
    with TestClient(app) as client:
        client.post("/api/reset")

        lesson = client.post(
            "/api/lessons/hello/submit",
            json={
                "answers": [
                    {"question_id": qid, "answer": ans} for qid, ans in WRONG_LESSON_ANSWERS
                ]
            },
        )
        for item in LESSONS:
            if item["module_id"] == module_id:
                total = len(item["questions"])
                save_lesson(item["id"], total, total, item["xp"])
        exam = client.post(
            f"/api/exams/{module_id}/submit",
            json={"answers": [{"question_id": qid, "answer": ""} for qid in exam_question_ids]},
        )
        client.post("/api/reset")

    assert lesson.status_code == 200
    assert exam.status_code == 200
    for response, expected_ids in (
        (lesson, [qid for qid, _ in WRONG_LESSON_ANSWERS]),
        (exam, exam_question_ids),
    ):
        results = response.json()["results"]
        assert {item["question_id"] for item in results} == set(expected_ids)
        for item in results:
            explanation = _explanation(item["question_id"])
            assert item.get("message"), item["question_id"]
            assert explanation in (item.get("explanation"), item.get("message")), item[
                "question_id"
            ]


def test_c4_wrong_verdict_shows_neutral_phrase_without_empty_paragraphs() -> None:
    cases = [
        {"correct": False, "message": NEUTRAL_MESSAGE},
        {"correct": False, "message": ""},
        {
            "correct": False,
            "message": NEUTRAL_MESSAGE,
            "checks": [{"passed": False, "expected": "1", "actual": "2"}],
            "error_hint": {
                "title": "Синтаксическая ошибка",
                "hint": "Проверь код",
                "original": "SyntaxError: x",
            },
        },
        {"correct": True, "message": "Все тесты пройдены!", "explanation": "Так работает print."},
        {"correct": False, "message": NEUTRAL_MESSAGE, "explanation": "Секретное объяснение"},
    ]
    rendered = _render_verdicts(cases)
    if rendered is None:
        js = APP_JS.read_text(encoding="utf-8")
        assert "↺ Пока неверно" in js
        assert "✓ Верно" in js
        return

    plain, empty, with_hint, correct, leaked = rendered
    assert "no" in plain["className"].split()
    assert "↺ Пока неверно" in plain["innerHTML"]
    assert NEUTRAL_MESSAGE in plain["innerHTML"]
    assert not re.search(r"<p>\s*</p>", plain["innerHTML"])

    assert "↺ Пока неверно" in empty["innerHTML"]
    assert not re.search(r"<p>\s*</p>", empty["innerHTML"])

    assert "Синтаксическая ошибка" in with_hint["innerHTML"]
    assert "Ожидалось" in with_hint["innerHTML"]
    assert not re.search(r"<p>\s*</p>", with_hint["innerHTML"])

    assert "ok" in correct["className"].split()
    assert "✓ Верно" in correct["innerHTML"]
    assert "Так работает print." in correct["innerHTML"]

    assert "↺ Пока неверно" in leaked["innerHTML"]
    assert "Секретное объяснение" not in leaked["innerHTML"]


def test_c5_question_code_block_has_gap_below_before_options() -> None:
    values = [
        _margin_bottom(body)
        for selector, body in _css_rules()
        if re.search(r"\.question-card\b[^,{]*\.code-example\b", selector)
    ]
    values = [value for value in values if value is not None]
    assert values, "нет правила отступа снизу для блока кода внутри .question-card"
    assert values[-1] >= 12


def test_c5_theory_code_block_margin_is_unchanged() -> None:
    bodies = [body for selector, body in _css_rules() if selector.strip() == ".code-example"]
    assert bodies
    assert any(re.search(r"margin:\s*14px\s+0\s+0\b", body) for body in bodies)
