"""Human-first rules and automated checks for the learning sequence.

The content files stay intentionally simple dictionaries.  This module adds the
pedagogical metadata used by practice selection and provides a small curriculum
linter.  The linter is deliberately independent from FastAPI so CI can import it
without starting the application or touching the learner database.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from typing import Any

REVIEW_INTERVALS_DAYS = (1, 3, 7, 14, 30)


# These are stable concept identifiers, not display strings.  A lesson may review
# several old concepts, but introduces at most one threshold idea at a time.
FOUNDATION_CONCEPTS: dict[str, tuple[str, ...]] = {
    "warmup-route": ("learning.route", "io.print"),
    "warmup-print": ("io.print-call",),
    "warmup-text": ("value.string",),
    "warmup-read-code": ("syntax.comment",),
    "warmup-variables": ("data.variable",),
    "warmup-names": ("naming.snake-case",),
    "warmup-numbers": ("value.integer", "operator.arithmetic"),
    "warmup-types": ("type.string-vs-number",),
    "warmup-length": ("builtin.len",),
    "warmup-fstring": ("string.f-string",),
    "warmup-input": ("builtin.input",),
    "warmup-convert": ("conversion.int",),
    "warmup-boolean": ("value.boolean",),
    "warmup-compare": ("operator.comparison",),
    "warmup-indent": ("syntax.indentation",),
    "warmup-errors": ("debug.name-error",),
    "warmup-methods": ("method.string-lower",),
    "strings-strip": ("method.string-strip",),
    "warmup-recap-one": ("review.dialogue",),
    "warmup-recap-two": ("review.counter",),
    "hello": ("transfer.print",),
    "variables": ("transfer.variables",),
    "strings-input": ("transfer.input",),
    "conditions": ("condition.if",),
    "conditions-else": ("condition.else",),
    "for-loop": ("loop.for-range",),
    "for-accumulator": ("assignment.accumulator",),
    "while-loop": ("loop.while",),
    "while-break": ("loop.break",),
    "functions": ("function.call",),
    "functions-parameters": ("function.parameter",),
    "functions-return": ("function.return",),
    "functions-greeting": ("function.compose",),
    "functions-keyword-arguments": ("function.keyword-argument",),
    "lists": ("collection.list-index",),
    "lists-append": ("method.list-append",),
    "strings-split": ("method.string-split",),
    "lists-sum": ("builtin.sum",),
    "dicts-sets": ("collection.dictionary",),
    "sets": ("collection.set",),
    "files": ("file.context-manager",),
    "exceptions": ("error.try-except",),
    "classes": ("object.class",),
}


FOUNDATION_PREREQUISITES: dict[str, tuple[str, ...]] = {
    "warmup-print": ("io.print",),
    "warmup-variables": ("value.string",),
    "warmup-numbers": ("data.variable",),
    "warmup-length": ("value.string",),
    "warmup-fstring": ("data.variable", "value.string"),
    "warmup-input": ("data.variable", "string.f-string"),
    "warmup-convert": ("builtin.input", "value.integer"),
    "warmup-compare": ("value.boolean",),
    "warmup-methods": ("value.string",),
    "strings-strip": ("value.string",),
    "conditions": ("operator.comparison", "syntax.indentation"),
    "conditions-else": ("condition.if",),
    "for-loop": ("syntax.indentation", "value.integer"),
    "for-accumulator": ("loop.for-range", "operator.arithmetic"),
    "while-loop": ("operator.comparison", "syntax.indentation"),
    "while-break": ("loop.while", "condition.if"),
    "functions": ("io.print", "syntax.indentation"),
    "functions-parameters": ("function.call", "data.variable"),
    "functions-return": ("function.parameter", "operator.arithmetic"),
    "functions-greeting": ("function.return", "string.f-string"),
    "functions-keyword-arguments": ("function.parameter", "function.call"),
    "lists": ("data.variable", "builtin.len"),
    "lists-append": ("collection.list-index",),
    "strings-split": ("value.string", "builtin.len"),
    "lists-sum": ("collection.list-index", "operator.arithmetic"),
    "dicts-sets": ("data.variable",),
    "sets": ("collection.list-index",),
    "files": ("value.string", "syntax.indentation"),
    "exceptions": ("conversion.int", "syntax.indentation"),
    "classes": ("data.variable", "syntax.indentation"),
}


# The linter tracks syntax and callable tools that are especially easy to expose
# accidentally through starters, distractors, hints, or hidden tests.
FEATURE_INTRODUCTIONS: dict[str, str] = {
    "syntax:assignment": "warmup-variables",
    "syntax:arithmetic": "warmup-numbers",
    "syntax:f-string": "warmup-fstring",
    "syntax:boolean": "warmup-boolean",
    "syntax:comparison": "warmup-compare",
    "syntax:comment": "warmup-read-code",
    "call:print": "warmup-route",
    "call:len": "warmup-length",
    "call:input": "warmup-input",
    "call:int": "warmup-convert",
    "call:bool": "warmup-boolean",
    "method:lower": "warmup-methods",
    "method:strip": "strings-strip",
    "syntax:if": "conditions",
    "syntax:else": "conditions-else",
    "syntax:for": "for-loop",
    "call:range": "for-loop",
    "syntax:augassign": "for-accumulator",
    "syntax:while": "while-loop",
    "syntax:break": "while-break",
    "syntax:function": "functions",
    "call:say_hello": "functions",
    "syntax:parameter": "functions-parameters",
    "call:greet": "functions-parameters",
    "syntax:return": "functions-return",
    "syntax:list": "lists",
    "syntax:subscript": "lists",
    "call:list": "lists",
    "method:append": "lists-append",
    "call:append": "lists-append",
    "method:split": "strings-split",
    "call:sum": "lists-sum",
    "syntax:dict": "dicts-sets",
    "method:get": "dicts-sets",
    "call:set": "sets",
    "syntax:set": "sets",
    "call:open": "files",
    "method:read": "files",
    "method:write": "files",
    "syntax:with": "files",
    "syntax:try": "exceptions",
    "syntax:class": "classes",
    "call:round": "operators-floating-point",
    "call:discount": "operators-integer-division",
    "method:replace": "strings-pro-search-replace",
    "method:join": "strings-pro-split-join",
    "call:enumerate": "tuples-slices-zip-enumerate",
    "call:zip": "tuples-slices-zip-enumerate",
    "method:pop": "lists-pro-stacks-queues",
    "method:remove": "lists-pro-mutation",
    "method:items": "mappings-dict-loops",
    "call:sorted": "lists-pro-sorting",
    "method:sort": "scope-lambda-key",
    "syntax:match": "flow-advanced-match",
    "syntax:default-parameter": "functions-pro-defaults",
    "syntax:keyword-argument": "functions-keyword-arguments",
    "call:connect": "functions-pro-keyword-args",
    "syntax:vararg": "functions-pro-varargs",
    "syntax:lambda": "scope-lambda-key",
    "syntax:list-comprehension": "comprehensions-list-comprehension",
    "syntax:dict-comprehension": "comprehensions-dict-comprehension",
    "call:iter": "iterators-iterable",
    "call:next": "iterators-iterable",
    "syntax:yield": "iterators-yield",
    "syntax:import": "modules-imports",
    "method:sqrt": "modules-imports",
    "call:Path": "modules-stdlib-imports",
    "call:main": "modules-main-guard",
    "syntax:raise": "errors-debug-raise",
    "call:ValueError": "errors-debug-raise",
    "method:__init__": "oop-design-init",
    "call:super": "oop-advanced-inheritance",
    "syntax:decorator": "oop-advanced-properties",
    "call:timedelta": "stdlib-core-datetime",
    "method:choice": "stdlib-core-random",
    "method:mean": "stdlib-core-math-statistics",
    "call:Decimal": "stdlib-core-decimal",
    "call:Counter": "stdlib-productivity-collections",
    "method:combinations": "stdlib-productivity-itertools",
    "method:heappush": "stdlib-productivity-heapq-bisect",
    "method:fullmatch": "regex-validation",
    "method:sub": "regex-substitution",
    "call:make_user": "testing-fixtures",
    "method:level_up": "testing-fixtures",
    "call:FakeClock": "testing-mocks",
    "method:execute": "databases-parameters",
    "call:ThreadPoolExecutor": "concurrency-thread-pool",
    "method:map": "concurrency-thread-pool",
    "method:put": "concurrency-queues",
    "syntax:async": "async-coroutines",
    "syntax:await": "async-coroutines",
    "method:sleep": "async-coroutines",
    "method:create_task": "async-tasks",
    "call:fetch": "async-tasks",
    "method:gather": "async-gather-timeouts",
    "call:Task": "capstones-task-manager",
}


def enrich_curriculum(lessons: list[dict[str, Any]]) -> None:
    """Attach consistent metadata and a spaced-review plan to every lesson."""
    concept_history: list[tuple[str, ...]] = []
    concepts_by_lesson_id: dict[str, tuple[str, ...]] = {}
    for index, lesson in enumerate(lessons):
        explicit = tuple(lesson.get("concepts") or FOUNDATION_CONCEPTS.get(lesson["id"], ()))
        if not explicit:
            explicit = (f"topic.{lesson['id']}",)
        lesson["concepts"] = list(explicit)

        raw_prerequisites = tuple(
            lesson.get("prerequisites")
            or FOUNDATION_PREREQUISITES.get(lesson["id"], ())
            or (concept_history[-1] if concept_history else ())
        )
        prerequisites = tuple(
            concept
            for prerequisite in raw_prerequisites
            for concept in concepts_by_lesson_id.get(prerequisite, (prerequisite,))
        )
        lesson["prerequisites"] = list(prerequisites)

        review_concepts: list[str] = []
        for offset in REVIEW_INTERVALS_DAYS:
            previous_index = index - offset
            if previous_index >= 0:
                review_concepts.extend(concept_history[previous_index][:1])
        lesson["practices"] = list(
            dict.fromkeys([*lesson.get("practices", ()), *explicit, *review_concepts])
        )
        lesson.setdefault("difficulty", min(5, 1 + index // 30))
        lesson["review_intervals_days"] = list(REVIEW_INTERVALS_DAYS)
        lesson.setdefault("estimated_minutes", lesson.get("duration", 10))
        lesson.setdefault(
            "learning_objectives",
            [f"Объяснить и применить концепт {concept}" for concept in explicit],
        )

        for question in lesson["questions"]:
            kind = question["kind"]
            purpose = {
                "choice": "predict_or_recognize",
                "input": "free_recall",
                "parsons": "ordering_and_tracing",
                "code": "guided_or_independent_application",
            }[kind]
            question.setdefault("purpose", purpose)
            question.setdefault("focus_concepts", list(explicit))
            question.setdefault("review_concepts", review_concepts[:2])
            question.setdefault("mandatory", kind == "code")
            question.setdefault(
                "scaffold_level",
                {"choice": "worked", "input": "recall", "parsons": "faded", "code": "independent"}[
                    kind
                ],
            )
            question.setdefault("requires", list(dict.fromkeys([*prerequisites, *explicit])))
            question.setdefault("retrieves", list(question["review_concepts"]))
            question.setdefault("scaffold", question["scaffold_level"])
            if kind == "code" and "hints" not in question:
                detailed_guide = question.get("guide", "")
                direct_hint = question.get("hint", "")
                question["guide"] = (
                    "Сначала назови входные данные и ожидаемый результат. Запусти заготовку, "
                    "прочитай фактический вывод или ошибку и измени только один ближайший шаг."
                )
                question["hints"] = list(
                    dict.fromkeys(
                        filter(
                            None,
                            (
                                "Сравни условие, заготовку и фактический вывод. Какая одна строка отвечает за различие?",
                                detailed_guide,
                                direct_hint,
                            ),
                        )
                    )
                )
        concept_history.append(explicit)
        concepts_by_lesson_id[lesson["id"]] = explicit


def _features_from_tree(tree: ast.AST) -> set[str]:
    features: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                features.add(f"call:{node.func.id}")
            elif isinstance(node.func, ast.Attribute):
                features.add(f"method:{node.func.attr}")
            if node.keywords:
                features.add("syntax:keyword-argument")
        if isinstance(node, ast.Assign):
            features.add("syntax:assignment")
        elif isinstance(node, ast.BinOp):
            features.add("syntax:arithmetic")
        elif isinstance(node, ast.JoinedStr):
            features.add("syntax:f-string")
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            features.add("syntax:boolean")
        elif isinstance(node, ast.Compare):
            features.add("syntax:comparison")
        elif isinstance(node, ast.Subscript):
            features.add("syntax:subscript")
        if isinstance(node, ast.If):
            features.add("syntax:if")
            if node.orelse:
                features.add("syntax:else")
        elif isinstance(node, ast.For):
            features.add("syntax:for")
        elif isinstance(node, ast.While):
            features.add("syntax:while")
        elif isinstance(node, ast.Break):
            features.add("syntax:break")
        elif isinstance(node, ast.AugAssign):
            features.add("syntax:augassign")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            features.add("syntax:function")
            if node.args.args:
                features.add("syntax:parameter")
            if node.args.defaults:
                features.add("syntax:default-parameter")
            if node.args.vararg or node.args.kwarg:
                features.add("syntax:vararg")
            if node.decorator_list:
                features.add("syntax:decorator")
            if isinstance(node, ast.AsyncFunctionDef):
                features.add("syntax:async")
        elif isinstance(node, ast.Return):
            features.add("syntax:return")
        elif isinstance(node, ast.List):
            features.add("syntax:list")
        elif isinstance(node, ast.Dict):
            features.add("syntax:dict")
        elif isinstance(node, ast.Set):
            features.add("syntax:set")
        elif isinstance(node, ast.With):
            features.add("syntax:with")
        elif isinstance(node, ast.Try):
            features.add("syntax:try")
        elif isinstance(node, ast.ClassDef):
            features.add("syntax:class")
            if node.decorator_list:
                features.add("syntax:decorator")
        elif isinstance(node, ast.Match):
            features.add("syntax:match")
        elif isinstance(node, ast.Lambda):
            features.add("syntax:lambda")
        elif isinstance(node, ast.ListComp):
            features.add("syntax:list-comprehension")
        elif isinstance(node, (ast.DictComp, ast.SetComp)):
            features.add("syntax:dict-comprehension")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            features.add("syntax:import")
        elif isinstance(node, (ast.Yield, ast.YieldFrom)):
            features.add("syntax:yield")
        elif isinstance(node, ast.Raise):
            features.add("syntax:raise")
        elif isinstance(node, ast.Await):
            features.add("syntax:await")
    return features


def _parse_features(source: str) -> set[str]:
    try:
        return _features_from_tree(ast.parse(source))
    except (SyntaxError, ValueError, TypeError):
        return set()


def _defined_names(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return set()
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def _called_names(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return set()
    return {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def _inline_snippets(value: str) -> Iterable[str]:
    for snippet in re.findall(r"`([^`]+)`", value or ""):
        # A lone {name} in prose describes an f-string placeholder, not a set literal.
        if re.fullmatch(r"\{[A-Za-z_][A-Za-z0-9_]*\}", snippet):
            continue
        yield snippet


def _lesson_feature_surfaces(lesson: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for card_index, card in enumerate(lesson["theory"], start=1):
        if card.get("language", "python") == "python":
            yield f"theory[{card_index}]", card.get("example", "")
        for snippet in _inline_snippets(card.get("text", "")):
            yield f"theory[{card_index}].text", snippet
        for snippet in _inline_snippets(card.get("tip", "")):
            yield f"theory[{card_index}].tip", snippet

    for question in lesson["questions"]:
        question_id = question["id"]
        if question.get("starter"):
            yield f"question[{question_id}].starter", question["starter"]
        for test_index, test in enumerate(question.get("tests", []), start=1):
            if test.get("call"):
                yield f"question[{question_id}].test[{test_index}]", test["call"]
        for field in ("prompt", "guide", "hint", "explanation"):
            for snippet in _inline_snippets(question.get(field, "")):
                yield f"question[{question_id}].{field}", snippet
        for hint_index, hint in enumerate(question.get("hints", ()), start=1):
            for snippet in _inline_snippets(hint):
                yield f"question[{question_id}].hints[{hint_index}]", snippet
        for option_index, option in enumerate(question.get("options", []), start=1):
            if re.fullmatch(r"\{[A-Za-z_][A-Za-z0-9_]*\}", option):
                continue
            if _parse_features(option):
                yield f"question[{question_id}].option[{option_index}]", option


def audit_learning_pipeline(lessons: list[dict[str, Any]]) -> list[str]:
    """Return actionable curriculum violations; an empty list means CI may pass."""
    errors: list[str] = []
    lesson_index = {lesson["id"]: index for index, lesson in enumerate(lessons)}
    introduced_concepts: set[str] = set()

    for index, lesson in enumerate(lessons):
        for field in (
            "concepts",
            "practices",
            "difficulty",
            "estimated_minutes",
            "learning_objectives",
        ):
            if field not in lesson or lesson[field] in (None, [], ""):
                errors.append(f"{lesson['id']}: отсутствует metadata.{field}")
        if "prerequisites" not in lesson:
            errors.append(f"{lesson['id']}: отсутствует metadata.prerequisites")

        missing = set(lesson.get("prerequisites", ())) - introduced_concepts
        if missing:
            errors.append(
                f"{lesson['id']}: предпосылки ещё не введены: {', '.join(sorted(missing))}"
            )

        for surface, source in _lesson_feature_surfaces(lesson):
            if "pass" in source.split():
                errors.append(f"{lesson['id']} {surface}: незнакомая заглушка pass")
            source_features = _parse_features(source)
            if any(line.lstrip().startswith("#") for line in source.splitlines()):
                source_features.add("syntax:comment")
            for feature in sorted(source_features & FEATURE_INTRODUCTIONS.keys()):
                introduction_id = FEATURE_INTRODUCTIONS[feature]
                introduction_index = lesson_index.get(introduction_id)
                if introduction_index is None:
                    errors.append(
                        f"{lesson['id']} {surface}: {feature} ссылается на отсутствующий урок {introduction_id}"
                    )
                elif index < introduction_index:
                    errors.append(
                        f"{lesson['id']} {surface}: {feature} раньше объяснения в {introduction_id}"
                    )

        for question in lesson["questions"]:
            local_names = _defined_names(question.get("starter", ""))
            registered_calls = {
                feature.removeprefix("call:")
                for feature in FEATURE_INTRODUCTIONS
                if feature.startswith("call:")
            }
            for test_index, test in enumerate(question.get("tests", ()), start=1):
                unknown_calls = _called_names(test.get("call", "")) - local_names - registered_calls
                if unknown_calls:
                    errors.append(
                        f"{question['id']} test[{test_index}]: тест вызывает необъяснённое имя "
                        f"{', '.join(sorted(unknown_calls))}"
                    )
            for option_index, option in enumerate(question.get("options", ()), start=1):
                option_features = _parse_features(option)
                option_local_names = _defined_names(option)
                unknown_option_tools = {
                    feature
                    for feature in option_features
                    if feature.startswith(("call:", "method:"))
                    and feature not in FEATURE_INTRODUCTIONS
                    and feature.split(":", 1)[1] not in option_local_names
                }
                if unknown_option_tools:
                    errors.append(
                        f"{question['id']} option[{option_index}]: незарегистрированный инструмент "
                        f"{', '.join(sorted(unknown_option_tools))}"
                    )
            for field in (
                "purpose",
                "focus_concepts",
                "review_concepts",
                "requires",
                "retrieves",
                "mandatory",
                "scaffold_level",
                "scaffold",
            ):
                if field not in question:
                    errors.append(f"{question['id']}: отсутствует metadata.{field}")
        introduced_concepts.update(lesson.get("concepts", ()))

    return errors


def audit_projects(projects: list[dict[str, Any]], lessons: list[dict[str, Any]]) -> list[str]:
    """Check that projects unlock after every tool used by starters and hidden tests."""
    errors: list[str] = []
    lesson_index = {lesson["id"]: index for index, lesson in enumerate(lessons)}
    for project in projects:
        project_id = project["id"]
        prerequisite_ids = project.get("requires_lesson_ids", [])
        missing_ids = set(prerequisite_ids) - lesson_index.keys()
        if missing_ids:
            errors.append(
                f"{project_id}: отсутствуют prerequisite lessons {', '.join(sorted(missing_ids))}"
            )
            continue
        unlock_index = max((lesson_index[item] for item in prerequisite_ids), default=-1)
        sources = [("starter", project.get("starter", ""))]
        tests = project.get("tests", [])
        scenarios = project.get("scenarios", [])
        for scenario_index, scenario in enumerate(scenarios, start=1):
            for test_index, test in enumerate(scenario.get("tests", []), start=1):
                if test.get("call"):
                    sources.append((f"scenario[{scenario_index}].test[{test_index}]", test["call"]))
        for test_index, test in enumerate(tests, start=1):
            if test.get("call"):
                sources.append((f"test[{test_index}]", test["call"]))

        local_names = _defined_names(project.get("starter", ""))
        for surface, source in sources:
            for feature in _parse_features(source):
                introduction_id = FEATURE_INTRODUCTIONS.get(feature)
                if introduction_id and lesson_index[introduction_id] > unlock_index:
                    errors.append(
                        f"{project_id} {surface}: {feature} раньше prerequisite {introduction_id}"
                    )
            if surface != "starter":
                registered_calls = {
                    feature.removeprefix("call:")
                    for feature in FEATURE_INTRODUCTIONS
                    if feature.startswith("call:")
                }
                unknown_calls = _called_names(source) - local_names - registered_calls
                if unknown_calls:
                    errors.append(
                        f"{project_id} {surface}: тест вызывает неизвестное имя "
                        f"{', '.join(sorted(unknown_calls))}"
                    )

        scenario_count = len(scenarios) if scenarios else len(tests)
        if scenario_count < 2:
            errors.append(f"{project_id}: нужно минимум два поведенческих сценария")
    return errors
