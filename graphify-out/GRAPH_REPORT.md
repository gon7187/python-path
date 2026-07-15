# Graph Report - Python-Learn  (2026-07-15)

## Corpus Check
- Corpus is ~38,438 words - fits in a single context window. You may not need a graph.

## Summary
- 366 nodes · 690 edges · 20 communities (15 shown, 5 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_API обучения и прогресса|API обучения и прогресса]]
- [[_COMMUNITY_Педагогика и структура курса|Педагогика и структура курса]]
- [[_COMMUNITY_Проверка кода и песочница|Проверка кода и песочница]]
- [[_COMMUNITY_Сборка и аудит программы|Сборка и аудит программы]]
- [[_COMMUNITY_SQLite-прогресс ученика|SQLite-прогресс ученика]]
- [[_COMMUNITY_Мобильный интерфейс курса|Мобильный интерфейс курса]]
- [[_COMMUNITY_Архитектура PythonPath|Архитектура PythonPath]]
- [[_COMMUNITY_Базовый контент и экзамены|Базовый контент и экзамены]]
- [[_COMMUNITY_CI и правила вклада|CI и правила вклада]]
- [[_COMMUNITY_Расширенная программа курса|Расширенная программа курса]]
- [[_COMMUNITY_Микроуроки фундамента|Микроуроки фундамента]]
- [[_COMMUNITY_Спокойный старт|Спокойный старт]]
- [[_COMMUNITY_Учебные проекты|Учебные проекты]]
- [[_COMMUNITY_Изоляция тестовой базы|Изоляция тестовой базы]]
- [[_COMMUNITY_Безопасность публичного запуска|Безопасность публичного запуска]]
- [[_COMMUNITY_Python-пакет приложения|Python-пакет приложения]]
- [[_COMMUNITY_SPA-оболочка|SPA-оболочка]]
- [[_COMMUNITY_Сообщения об уязвимостях|Сообщения об уязвимостях]]
- [[_COMMUNITY_Шаблон отчёта об ошибке|Шаблон отчёта об ошибке]]
- [[_COMMUNITY_Шаблон предложения функции|Шаблон предложения функции]]

## God Nodes (most connected - your core abstractions)
1. `run_code()` - 25 edges
2. `PythonPath Learning Design Bible` - 19 edges
3. `save_lesson()` - 15 edges
4. `str` - 14 edges
5. `state()` - 13 edges
6. `esc()` - 13 edges
7. `render()` - 13 edges
8. `evaluate()` - 12 edges
9. `CI Curriculum Audit` - 12 edges
10. `connection()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Content Authoring Rules` --references--> `PythonPath Learning Design Bible`  [EXTRACTED]
  CONTRIBUTING.md → docs/LEARNING_DESIGN.md
- `Pull Request Quality Gate` --references--> `Lint Format Type and Test Quality Checks`  [INFERRED]
  CONTRIBUTING.md → .github/workflows/ci.yml
- `audit_learning_pipeline(LESSONS)` --implements--> `CI Curriculum Audit`  [INFERRED]
  CONTRIBUTING.md → docs/LEARNING_DESIGN.md
- `Local Single-User SQLite Progress` --shares_data_with--> `SQLite Progress Store`  [INFERRED]
  README.md → docs/ARCHITECTURE.md
- `test_early_lessons_mix_predictions_and_small_traps()` --calls--> `public_question()`  [EXTRACTED]
  tests/test_curriculum.py → app/content.py

## Hyperedges (group relationships)
- **Course Assembly Pipeline** — app_gentle_start_gentle_start_path, app_foundation_expansion_foundation_microsteps, app_extended_curriculum_extended_course_spec, app_learning_design_enrich_curriculum, app_content_course_catalog [EXTRACTED 1.00]
- **Adaptive Practice Feedback Loop** — app_db_record_attempt, app_db_attempt_snapshot, app_main_practice_priority, app_main_practice_questions, app_main_submit_practice [INFERRED 0.95]
- **Safe Execution Surfaces** — app_evaluator_safetyvisitor, app_evaluator_run_code, app_evaluator_evaluate, app_main_check_code, app_main_run_editor_code, app_main_run_sandbox, app_main_run_project, app_main_submit_project [EXTRACTED 1.00]
- **Public Execution Isolation Stack** — security_per_execution_isolation, security_resource_limits, security_job_control_audit, security_authenticated_storage [EXTRACTED 1.00]
- **CI Quality Suite** — ci_ruff, ci_pyright, ci_pytest [EXTRACTED 1.00]
- **Worked Example to Independent Transfer Progression** — learning_design_worked_examples, learning_design_mastery_ladder, learning_design_primm, learning_design_fading_scaffolding, learning_design_parsons_tasks, learning_design_behavioral_evaluation [EXTRACTED 1.00]

## Communities (20 total, 5 thin omitted)

### Community 0 - "API обучения и прогресса"
Cohesion: 0.08
Nodes (57): public_lesson(), bool, state(), Answer, available_practice_lessons(), check_code(), CodeCheck, CodeRun (+49 more)

### Community 1 - "Педагогика и структура курса"
Cohesion: 0.08
Nodes (49): One-Axis Complexity Progression, Mixed Checkpoints with Mandatory Code, 151-Lesson 32-Section Course Map, Gentle Start Microcourse, Syntax-to-Projects Curriculum Progression, Six Prerequisite-Gated Project Tools, Adaptive Completed-Lesson Practice, Explicit-Objective AST Structural Check (+41 more)

### Community 2 - "Проверка кода и песочница"
Cohesion: 0.09
Nodes (32): evaluate(), explain_runtime_error(), explain_syntax_error(), normalize(), Any, AST, str, Проверка ответов и безопасный мини-раннер учебного кода. (+24 more)

### Community 3 - "Сборка и аудит программы"
Cohesion: 0.10
Nodes (30): Assembled Course Catalog, public_question(), Extended Course Specification, Foundation Microstep Expansion, Gentle Start Learning Path, audit_learning_pipeline(), audit_projects(), _called_names() (+22 more)

### Community 4 - "SQLite-прогресс ученика"
Cohesion: 0.11
Nodes (29): _attempt_snapshot(), connection(), init_db(), bool, int, str, Question Attempt History, Минимальное SQLite-хранилище прогресса для локального single-user приложения. (+21 more)

### Community 5 - "Мобильный интерфейс курса"
Cohesion: 0.15
Nodes (28): api(), bindQuestionControls(), esc(), executionPanel(), isModuleCollapsed(), loading(), moduleCollapseStates(), questionTemplate() (+20 more)

### Community 6 - "Архитектура PythonPath"
Cohesion: 0.13
Nodes (21): Browser and Mobile UI, Course and Assignment Catalog, AST Curriculum Linter, Answer and Code Evaluator, FastAPI JSON API, Two-Second Child Python Runner, Project Progress and Prerequisite Gates, Intentional Single-User Design (+13 more)

### Community 7 - "Базовый контент и экзамены"
Cohesion: 0.16
Nodes (17): add_learning_scaffolds(), apply_foundation_expansion(), choice(), code(), default_guide(), Mixed Exam Catalog, lesson(), int (+9 more)

### Community 8 - "CI и правила вклада"
Cohesion: 0.13
Nodes (17): actions/checkout v4, Push and Pull Request CI Triggers, Pyright Type Check, pytest Test Suite, Python 3.12 and uv Locked Environment, Lint Format Type and Test Quality Checks, Read-Only Repository Contents Permission, Ruff Lint and Format Checks (+9 more)

### Community 9 - "Расширенная программа курса"
Cohesion: 0.31
Nodes (13): build_extended_course(), _code_task(), _example_language(), _lesson_theory(), _make_questions(), _parsons_data(), Any, str (+5 more)

### Community 10 - "Микроуроки фундамента"
Cohesion: 0.33
Nodes (9): _card(), _challenge(), _choice(), _code(), _input(), _lesson(), int, str (+1 more)

### Community 11 - "Спокойный старт"
Cohesion: 0.42
Nodes (8): _choice(), _code(), _input(), _lesson(), Any, str, Спокойный вход в курс: одна новая идея на один короткий урок., _theory()

### Community 12 - "Учебные проекты"
Cohesion: 0.29
Nodes (6): public_project(), Any, bool, str, Небольшие практические проекты с постепенным усложнением., Не выдаёт тесты и контрольные входные данные в браузер.

### Community 13 - "Изоляция тестовой базы"
Cohesion: 0.29
Nodes (6): Learner Progress Store, MonkeyPatch, Path, isolated_database(), Изолирует тесты от личного локального прогресса в приложении., Каждый тест получает собственную SQLite-базу и не трогает python_path.db.

### Community 14 - "Безопасность публичного запуска"
Cohesion: 0.33
Nodes (6): Authenticated Separate Storage, Job Queues Rate Limiting and Audit, Local-Only Trust Boundary, Per-Execution Containers or microVMs, Public Execution Isolation Requirements, CPU Memory Filesystem Network and Process Limits

## Knowledge Gaps
- **45 isolated node(s):** `int`, `bool`, `Row`, `Name`, `Import` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `public_question()` connect `Сборка и аудит программы` to `API обучения и прогресса`, `Базовый контент и экзамены`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `run_code()` connect `Проверка кода и песочница` to `API обучения и прогресса`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `get_exam()` connect `API обучения и прогресса` to `Сборка и аудит программы`, `SQLite-прогресс ученика`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **What connects `int`, `bool`, `Русский учебный план: мягкий старт, практика и контрольные точки.` to the rest of the system?**
  _92 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `API обучения и прогресса` be split into smaller, more focused modules?**
  _Cohesion score 0.07656341320864991 - nodes in this community are weakly interconnected._
- **Should `Педагогика и структура курса` be split into smaller, more focused modules?**
  _Cohesion score 0.07993197278911565 - nodes in this community are weakly interconnected._
- **Should `Проверка кода и песочница` be split into smaller, more focused modules?**
  _Cohesion score 0.08846153846153847 - nodes in this community are weakly interconnected._