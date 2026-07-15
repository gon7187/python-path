# Graph Report - Python-Learn  (2026-07-15)

## Corpus Check
- 31 files · ~65,838 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 644 nodes · 1133 edges · 40 communities (35 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a5869c5d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]

## God Nodes (most connected - your core abstractions)
1. `run_code()` - 47 edges
2. `audit_learning_pipeline()` - 24 edges
3. `str` - 22 edges
4. `PythonPath Learning Design Bible` - 19 edges
5. `save_lesson()` - 18 edges
6. `audit_projects()` - 18 edges
7. `Библия обучения PythonPath` - 18 edges
8. `evaluate()` - 17 edges
9. `str` - 16 edges
10. `public_question()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_all_reference_solutions_pass_the_real_runner()` --calls--> `run_code()`  [EXTRACTED]
  tests/test_advanced_curriculum.py → app/evaluator.py
- `test_theory_examples_are_explicit_and_python_examples_have_output()` --calls--> `run_code()`  [EXTRACTED]
  tests/test_advanced_curriculum.py → app/evaluator.py
- `test_foundation_python_examples_match_their_declared_output()` --calls--> `run_code()`  [EXTRACTED]
  tests/test_curriculum.py → app/evaluator.py
- `test_public_feedback_hides_values_leaked_by_an_exception_in_a_hidden_test()` --calls--> `run_code()`  [EXTRACTED]
  tests/test_runtime_learning.py → app/evaluator.py
- `test_runner_caps_threads_and_blocks_argparse_host_files()` --calls--> `run_code()`  [EXTRACTED]
  tests/test_runtime_learning.py → app/evaluator.py

## Hyperedges (group relationships)
- **Course Assembly Pipeline** — app_gentle_start_gentle_start_path, app_foundation_expansion_foundation_microsteps, app_extended_curriculum_extended_course_spec, app_learning_design_enrich_curriculum, app_content_course_catalog [EXTRACTED 1.00]
- **Adaptive Practice Feedback Loop** — app_db_record_attempt, app_db_attempt_snapshot, app_main_practice_priority, app_main_practice_questions, app_main_submit_practice [INFERRED 0.95]
- **Safe Execution Surfaces** — app_evaluator_safetyvisitor, app_evaluator_run_code, app_evaluator_evaluate, app_main_check_code, app_main_run_editor_code, app_main_run_sandbox, app_main_run_project, app_main_submit_project [EXTRACTED 1.00]
- **Public Execution Isolation Stack** — security_per_execution_isolation, security_resource_limits, security_job_control_audit, security_authenticated_storage [EXTRACTED 1.00]
- **CI Quality Suite** — ci_ruff, ci_pyright, ci_pytest [EXTRACTED 1.00]
- **Worked Example to Independent Transfer Progression** — learning_design_worked_examples, learning_design_mastery_ladder, learning_design_primm, learning_design_fading_scaffolding, learning_design_parsons_tasks, learning_design_behavioral_evaluation [EXTRACTED 1.00]

## Communities (40 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (33): init_db(), Learner Progress Store, Answer, check_code(), CodeCheck, CodeRun, get_project(), get_projects() (+25 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (49): One-Axis Complexity Progression, Mixed Checkpoints with Mandatory Code, 151-Lesson 32-Section Course Map, Gentle Start Microcourse, Syntax-to-Projects Curriculum Progression, Six Prerequisite-Gated Project Tools, Adaptive Completed-Lesson Practice, Explicit-Objective AST Structural Check (+41 more)

### Community 2 - "Community 2"
Cohesion: 0.21
Nodes (16): Выполняет небольшой фрагмент в отдельном Python-процессе с лимитом времени., Выполняет небольшой фрагмент в отдельном Python-процессе с лимитом времени., run_code(), Safe Learner Code Sandbox, Virtual Learner Filesystem, test_code_runner_blocks_unsafe_imports(), test_code_runner_checks_function(), test_code_runner_explains_when_input_value_is_missing() (+8 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (56): audit_exam_coverage(), audit_learning_pipeline(), audit_projects(), _call_like_features(), _called_names(), Curriculum Metadata Schema, _defined_names(), enrich_curriculum() (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (24): _attempt_snapshot(), connection(), bool, int, str, Question Attempt History, Минимальное SQLite-хранилище прогресса для локального single-user приложения., Отмечает проект завершённым и начисляет награду только за первый проход. (+16 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (36): Adaptive Practice Pipeline, Exam Gating Policy, api(), bindHintControls(), bindQuestionControls(), esc(), executionPanel(), isModuleCollapsed() (+28 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (21): Browser and Mobile UI, Course and Assignment Catalog, AST Curriculum Linter, Answer and Code Evaluator, FastAPI JSON API, Two-Second Child Python Runner, Project Progress and Prerequisite Gates, Intentional Single-User Design (+13 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (27): add_learning_scaffolds(), apply_foundation_expansion(), build_exam_variants(), choice(), code(), default_guide(), Mixed Exam Catalog, _exam_starter() (+19 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (17): actions/checkout v4, Push and Pull Request CI Triggers, Pyright Type Check, pytest Test Suite, Python 3.12 and uv Locked Environment, Lint Format Type and Test Quality Checks, Read-Only Repository Contents Permission, Ruff Lint and Format Checks (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (34): build_topical_code_task(), _function(), Any, str, Тематические executable-задачи для 108 уроков расширенного курса.  В отличие от, Вернуть внутреннюю спецификацию; используется только проверками курса., Собрать публичную code-задачу с тематическими опорами без готового ответа., Авторская спецификация одной тематической задачи. (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (9): _card(), _challenge(), _choice(), _code(), _input(), _lesson(), int, str (+1 more)

### Community 11 - "Community 11"
Cohesion: 0.42
Nodes (8): _choice(), _code(), _input(), _lesson(), Any, str, Спокойный вход в курс: одна новая идея на один короткий урок., _theory()

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (37): 10.1. Открытие проекта, 10.2. Поддержка в проекте, 10.3. Приёмка проекта, 10. Проекты, 11. Сложность и темп, 12.1. Чек-лист нового урока, 12.2. Чек-лист модуля, 12. Авторский процесс (+29 more)

### Community 13 - "Community 13"
Cohesion: 0.29
Nodes (6): MonkeyPatch, Path, isolated_database(), MonkeyPatch, Изолирует тесты от личного локального прогресса в приложении., Каждый тест получает собственную SQLite-базу и не трогает python_path.db.

### Community 14 - "Community 14"
Cohesion: 0.33
Nodes (6): Authenticated Separate Storage, Job Queues Rate Limiting and Audit, Local-Only Trust Boundary, Per-Execution Containers or microVMs, Public Execution Isolation Requirements, CPU Memory Filesystem Network and Process Limits

### Community 20 - "Community 20"
Cohesion: 0.08
Nodes (21): Assembled Course Catalog, public_question(), Extended Course Specification, Foundation Microstep Expansion, Gentle Start Learning Path, _code_question(), Регрессии тематической практики расширенного курса., test_all_reference_solutions_pass_the_real_runner() (+13 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (15): code:powershell (git clone https://github.com/gon7187/python-path.git), code:powershell (uv run uvicorn app.main:app --host 0.0.0.0 --port 8000), code:powershell (uv run ruff check app tests), code:text (app/), Python Path, Безопасность учебного раннера, Быстрый старт, Возможности (+7 more)

### Community 22 - "Community 22"
Cohesion: 0.20
Nodes (9): API, code:mermaid (flowchart LR), Frontend, Архитектура Python Path, Компоненты, Контент, Проверка кода, Прогресс (+1 more)

### Community 23 - "Community 23"
Cohesion: 0.25
Nodes (7): code:powershell (uv sync --extra dev), code:powershell (uv run ruff check app tests), Вклад в Python Path, Коммиты и PR, Локальная разработка, Перед pull request, Правила для контента

### Community 24 - "Community 24"
Cohesion: 0.40
Nodes (4): Как повторить, Окружение, Что ожидалось, Что произошло

### Community 25 - "Community 25"
Cohesion: 0.40
Nodes (4): Почему, Проверка, Скриншоты / заметки, Что изменилось

### Community 26 - "Community 26"
Cohesion: 0.50
Nodes (3): Карта курса, Мастерская проектов, Принципы сложности

### Community 27 - "Community 27"
Cohesion: 0.50
Nodes (3): Альтернативы, Идея, Предлагаемое решение

### Community 28 - "Community 28"
Cohesion: 0.50
Nodes (3): Security policy, Сообщить о проблеме, Учебный раннер

### Community 29 - "Community 29"
Cohesion: 0.13
Nodes (21): public_project(), Any, bool, str, Не выдаёт тесты и контрольные входные данные в браузер., Не выдаёт тесты и контрольные входные данные в браузер., Не выдаёт тесты и контрольные входные данные в браузер., _lesson() (+13 more)

### Community 30 - "Community 30"
Cohesion: 0.10
Nodes (22): Spaced Review Plan, available_practice_lessons(), current_practice_lesson(), _mixed_selection(), practice(), practice_modules(), _practice_priority(), practice_questions() (+14 more)

### Community 31 - "Community 31"
Cohesion: 0.10
Nodes (13): MonkeyPatch, test_exam_delivery_can_shuffle_without_changing_question_identity(), test_public_feedback_hides_values_leaked_by_an_exception_in_a_hidden_test(), test_runner_caps_threads_and_blocks_argparse_host_files(), test_runner_keeps_process_pool_unavailable(), test_runner_supports_isolated_sqlite(), test_runner_supports_safe_argparse_and_simulated_sys_argv(), test_runner_supports_safe_threads_queues_and_thread_pool() (+5 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (19): public_lesson(), bool, state(), course(), course_payload(), dashboard(), dashboard_payload(), _exam_passed() (+11 more)

### Community 33 - "Community 33"
Cohesion: 0.24
Nodes (14): get_exam(), get_lesson(), grade_answers(), Any, int, str, Перемешать варианты только в копии, не меняя авторский каталог., A lesson is mastered at 75%, with at least two correct answers. (+6 more)

### Community 34 - "Community 34"
Cohesion: 0.20
Nodes (6): AST, SafetyVisitor, Attribute, Import, ImportFrom, Name

### Community 35 - "Community 35"
Cohesion: 0.22
Nodes (10): evaluate(), normalize(), Any, Возвращает единый результат для выбора, текста и кода., Возвращает единый результат для выбора, текста и кода., test_choice_answer_is_normalized(), test_parsons_answer_checks_order(), test_failed_code_check_is_not_hidden_by_success_explanation() (+2 more)

### Community 36 - "Community 36"
Cohesion: 0.24
Nodes (9): explain_failed_checks(), explain_runtime_error(), explain_syntax_error(), str, Проверка ответов и безопасный мини-раннер учебного кода., Translate common parser messages into a concrete next step for a beginner., Translate common parser messages into a concrete next step for a beginner., Show the first concrete mismatch instead of a generic red result. (+1 more)

### Community 37 - "Community 37"
Cohesion: 0.33
Nodes (5): object, str, Дополнительные поведенческие сценарии для экзаменационного переноса.  Ключи реес, Вернуть независимые копии переносных проверок для исходного вопроса., transfer_tests_for()

### Community 38 - "Community 38"
Cohesion: 0.50
Nodes (3): Answer, Q: How are question hints generated, exposed, and rendered across lessons, practice, exams, and projects?, Source Nodes

### Community 39 - "Community 39"
Cohesion: 0.50
Nodes (3): Answer, Q: Есть ли в курсе бесполезные подсказки или функции и конструкции, которые появляются до объяснения?, Source Nodes

## Knowledge Gaps
- **121 isolated node(s):** `int`, `bool`, `Row`, `Name`, `Import` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_code()` connect `Community 2` to `Community 0`, `Community 34`, `Community 35`, `Community 36`, `Community 20`, `Community 29`, `Community 31`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `public_question()` connect `Community 20` to `Community 32`, `Community 33`, `Community 0`, `Community 3`, `Community 7`, `Community 30`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `Extended Course Specification` connect `Community 20` to `Community 9`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **What connects `Тематические executable-задачи для 108 уроков расширенного курса.  В отличие от`, `Авторская спецификация одной тематической задачи.`, `Собрать обычную функцию и компилируемую, но незавершённую заготовку.` to the rest of the system?**
  _230 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07993197278911565 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.08045977011494253 - nodes in this community are weakly interconnected._