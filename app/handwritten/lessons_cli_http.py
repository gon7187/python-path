"""Рукописные уроки 97–104: командная строка, окружение и HTTP API."""

from __future__ import annotations

from typing import Any


def _card(title: str, text: str, example: str, tip: str = "", run: bool = True) -> dict[str, Any]:
    card: dict[str, Any] = {"title": title, "text": text, "example": example, "tip": tip}
    if not run:
        card["run"] = False
    return card


def _choice(
    lesson_id: str,
    prompt: str,
    options: list[str],
    answer: str,
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{lesson_id}-choice",
        "kind": "choice",
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def _term(
    lesson_id: str,
    prompt: str,
    answers: list[str],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{lesson_id}-term",
        "kind": "input",
        "prompt": prompt,
        "answers": answers,
        "placeholder": "Введите ответ",
        "explanation": explanation,
    }


def _code(
    lesson_id: str,
    prompt: str,
    starter: str,
    tests: list[dict[str, Any]],
    reference: str,
    explanation: str,
    hint: str,
) -> dict[str, Any]:
    return {
        "id": f"{lesson_id}-code",
        "kind": "code",
        "prompt": prompt,
        "starter": starter,
        "tests": tests,
        "reference": reference,
        "explanation": explanation,
        "hint": hint,
    }


def _lesson(
    lesson_id: str,
    subtitle: str,
    theory: list[dict[str, Any]],
    questions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": lesson_id,
        "subtitle": subtitle,
        "theory": theory,
        "questions": questions,
    }


LESSONS: list[dict[str, Any]] = [
    _lesson(
        "cli-environment-argv",
        "Разбираем флаги без argparse",
        [
            _card(
                "Что такое аргументы командной строки",
                "Аргументы — это слова, которые ты передаёшь программе при запуске. "
                "Например, `python app.py --name Аня` получает два аргумента: `--name` "
                "и `Аня`. Они уже лежат в списке `sys.argv`, но `sys.argv[0]` — это имя "
                "самого файла, а не флаг. Аргументы позволяют менять поведение программы "
                "без правки кода.",
                "args = ['--name', 'Аня', '--age', '20']\n"
                "print(args[0])\n"
                "print(args[1])\n"
                "# Вывод:\n"
                "# --name\n"
                "# Аня",
                "Первое слово команды — имя программы, его пропускают при разборе.",
            ),
            _card(
                "Как собрать пары ключ — значение",
                "Флаги удобно хранить в словаре: ключом станет имя без дефисов, а "
                "значением — следующее слово. Проходи по списку шагом 2: на чётном месте "
                "стоит ключ, на нечётном — значение. `removeprefix('--')` убирает только "
                "ведущие дефисы и не трогает остальной текст.",
                "args = ['--name', 'Аня', '--age', '20']\n"
                "pairs = {}\n"
                "for index in range(0, len(args), 2):\n"
                "    key = args[index].removeprefix('--')\n"
                "    pairs[key] = args[index + 1]\n"
                "print(pairs)\n"
                "# Вывод:\n"
                "# {'name': 'Аня', 'age': '20'}",
                "Проверь, что длина списка чётная: иначе последнему ключу не хватит значения.",
            ),
            _card(
                "Типичная ошибка: разбирать имя программы как флаг",
                "Если начать цикл с нулевого элемента, первым ключом станет `app.py`, а все "
                "пары сдвинутся. Заметить это легко: выведи `args[0]` и `args[1:]`. Если в "
                "первом элементе нет ведущих дефисов, перед разбором отбрось имя программы. "
                "В реальном скрипте для этого берут `sys.argv[1:]`.",
                "args = ['app.py', '--name', 'Аня']\n"
                "print(args[0])\n"
                "print(args[1:])\n"
                "# Вывод:\n"
                "# app.py\n"
                "# ['--name', 'Аня']",
                "Начинай разбор с элемента, который действительно похож на флаг.",
            ),
        ],
        [
            _choice(
                "cli-environment-argv",
                "Что выведет код?\n\n"
                "args = ['--name', 'Аня', '--age', '20']\n"
                "pairs = {}\n"
                "for index in range(0, len(args), 2):\n"
                "    key = args[index].removeprefix('--')\n"
                "    pairs[key] = args[index + 1]\n"
                "print(pairs)",
                [
                    "{'name': 'Аня', 'age': '20'}",
                    "{'--name': 'Аня', '--age': '20'}",
                    "{'name': 'Аня', 'age': 20}",
                    "{'имя': 'Аня', 'возраст': '20'}",
                ],
                "{'name': 'Аня', 'age': '20'}",
                "`removeprefix('--')` убирает дефисы, поэтому ключи становятся `name` и `age`.",
            ),
            _term(
                "cli-environment-argv",
                "Что нужно отбросить у флага, чтобы получить имя параметра?",
                ["--", "два дефиса", "префикс --", "дефисы"],
                "Флаг `--name` превращается в имя `name` после удаления ведущих дефисов.",
            ),
            _code(
                "cli-environment-argv",
                "Напиши `parse_args(argv)`: она получает список пар `--ключ значение` и "
                "возвращает словарь. Имя программы в список уже не входит. Если значение "
                "для последнего флага отсутствует, этот флаг пропусти.",
                "def parse_args(argv):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "parse_args(['--name', 'Аня', '--age', '20'])",
                        "expected": {"name": "Аня", "age": "20"},
                    },
                    {"kind": "call", "call": "parse_args([])", "expected": {}},
                    {"kind": "call", "call": "parse_args(['--debug'])", "expected": {}},
                ],
                "def parse_args(argv):\n"
                "    result = {}\n"
                "    index = 0\n"
                "    while index + 1 < len(argv):\n"
                "        key = argv[index].removeprefix('--')\n"
                "        result[key] = argv[index + 1]\n"
                "        index += 2\n"
                "    return result\n",
                "Пустой список даёт пустой словарь, а непарный последний флаг просто "
                "не попадает в результат.",
                "Иди по списку шагом 2 и проверяй, что рядом с ключом есть значение.",
            ),
        ],
    ),
    _lesson(
        "cli-environment-environment",
        "Настройки, которые не лежат в коде",
        [
            _card(
                "Что такое переменные окружения",
                "Переменные окружения — это пары «имя — значение», которые программа "
                "получает от системы или терминала. Так передают адрес API, режим работы "
                "и номер порта, не записывая их в исходники. В Python окружение удобно "
                "представить обычным словарём: значения в нём чаще всего строки.",
                "env = {'APP_MODE': 'dev'}\nprint(env['APP_MODE'])\n# Вывод:\n# dev",
                "Секреты храни в окружении или отдельном хранилище, а не в репозитории.",
            ),
            _card(
                "Как взять значение с запасным вариантом",
                "Метод `get` возвращает значение по ключу, а если ключа нет — второй "
                "аргумент. Это защищает от `KeyError` при запуске без переменной. Число "
                "из окружения приходит строкой, поэтому перед использованием его приводят "
                "через `int`. Запасное значение тоже лучше держать строкой и приводить "
                "вместе с основным.",
                "env = {}\nraw = env.get('PORT', '8000')\nprint(int(raw))\n# Вывод:\n# 8000",
                "`get` не меняет словарь: он только возвращает найденное или запасное значение.",
            ),
            _card(
                "Типичная ошибка: падать на нечисловом порте",
                "Если в переменной оказалось `abc`, прямой `int` бросит `ValueError` и "
                "остановит программу. Заметить проблему можно по traceback с `ValueError` "
                "и названием `int`. Надёжный вариант — проверить строку через `isdigit` "
                "или поймать `ValueError` и вернуть значение по умолчанию.",
                "env = {'PORT': 'abc'}\n"
                "raw = env.get('PORT', '8000')\n"
                "print(raw if raw.isdigit() else '8000')\n"
                "# Вывод:\n"
                "# 8000",
                "Не доверяй строке из окружения: проверь её до преобразования в число.",
            ),
        ],
        [
            _choice(
                "cli-environment-environment",
                "Что выведет код?\n\nenv = {'PORT': '9000'}\nprint(int(env.get('PORT', '8000')))",
                ["9000", "8000", "None", "ошибка"],
                "9000",
                "Ключ `PORT` есть, поэтому `get` вернул `'9000'`, а `int` сделал из него число.",
            ),
            _term(
                "cli-environment-environment",
                "Каким методом словаря берут значение с запасным вариантом?",
                ["get", "get()", "метод get", "env.get"],
                "`env.get('PORT', '8000')` вернёт запасное значение, если ключа нет.",
            ),
            _code(
                "cli-environment-environment",
                "Напиши `get_port(env)`: верни `int(env['PORT'])`, если значение "
                "преобразуется в число. Если ключа нет или значение нечисловое, верни "
                "`8000`.",
                "def get_port(env):\n    pass\n",
                [
                    {"kind": "call", "call": "get_port({'PORT': '9000'})", "expected": 9000},
                    {"kind": "call", "call": "get_port({})", "expected": 8000},
                    {"kind": "call", "call": "get_port({'PORT': 'abc'})", "expected": 8000},
                ],
                "def get_port(env):\n"
                "    try:\n"
                "        return int(env.get('PORT', '8000'))\n"
                "    except (TypeError, ValueError):\n"
                "        return 8000\n",
                "Пустое окружение и строка `abc` дают запасной порт `8000`, а `9000` "
                "превращается в число.",
                "Сначала возьми значение через `get`, затем попробуй `int` и обработай ошибку.",
            ),
        ],
    ),
    _lesson(
        "cli-environment-venv",
        "Отдельные пакеты для каждого проекта",
        [
            _card(
                "Что такое виртуальное окружение",
                "Виртуальное окружение — это отдельная папка с интерпретатором и пакетами "
                "для одного проекта. Оно не даёт зависимостям разных проектов мешать друг "
                "другу. Обычно папку называют `.venv` и создают командой `python -m venv`. "
                "Внутри неё уже есть свой `python` и свой `pip`.",
                "import subprocess\n"
                "\n"
                "subprocess.run(['python', '-m', 'venv', '.venv'], check=True)\n"
                "print('окружение готово')\n"
                "# Вывод:\n"
                "# окружение готово",
                "Добавь `.venv` в `.gitignore`: это локальная папка, а не часть проекта.",
                run=False,
            ),
            _card(
                "Как ставить зависимости внутри окружения",
                "После создания окружения команды запускают его интерпретатором: "
                "`.venv/bin/python` на Linux и macOS или `.venv\\Scripts\\python` на "
                "Windows. Тогда `pip` ставит пакеты именно в `.venv`, а не в системный "
                "Python. В примере установка идёт из файла `requirements.txt`.",
                "import subprocess\n"
                "\n"
                "subprocess.run(\n"
                "    ['.venv/bin/python', '-m', 'pip', 'install', '-r', 'requirements.txt'],\n"
                "    check=True,\n"
                ")\n"
                "print('зависимости установлены')\n"
                "# Вывод:\n"
                "# зависимости установлены",
                "В командах проекта указывай путь к Python из `.venv`, чтобы не зависеть от активации.",
                run=False,
            ),
            _card(
                "Типичная ошибка: ставить пакеты в системный Python",
                "Если интерпретатор находится вне `.venv`, пакеты попадут в глобальное "
                "окружение и могут сломать другой проект. Заметить это просто: выведи путь "
                "к текущему Python и проверь, есть ли в нём `.venv`. Значение `False` "
                "означает, что окружение не активировано или выбрано неверно.",
                "python_path = '/usr/bin/python'\n"
                "print('/.venv/' in python_path)\n"
                "# Вывод:\n"
                "# False",
                "Перед установкой пакетов проверяй путь интерпретатора, а не только имя команды.",
            ),
        ],
        [
            _choice(
                "cli-environment-venv",
                "Что выведет код?\n\n"
                "lines = ['fastapi>=0.110', '# комментарий', 'httpx', 'flask']\n"
                "names = []\n"
                "for line in lines:\n"
                "    if not line.startswith('#'):\n"
                "        names.append(line.split('>=')[0])\n"
                "print(names)",
                [
                    "['fastapi', 'httpx', 'flask']",
                    "['fastapi', 'flask']",
                    "['fastapi>=0.110', 'httpx', 'flask']",
                    "['# комментарий', 'httpx', 'flask']",
                ],
                "['fastapi', 'httpx', 'flask']",
                "Строка с решёткой пропускается, а версия отрезается по `>=`.",
            ),
            _term(
                "cli-environment-venv",
                "Какая папка обычно хранит пакеты виртуального окружения проекта?",
                [".venv", "venv", "папка .venv", "виртуальное окружение"],
                "Папка `.venv` создаётся командой `python -m venv .venv`.",
            ),
            _code(
                "cli-environment-venv",
                "Напиши `requirement_name(line)`: верни имя пакета из строки "
                "`requirements.txt` без версии и лишних пробелов. Для пустой строки и "
                "комментария верни `None`.",
                "def requirement_name(line):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "requirement_name('fastapi>=0.110')",
                        "expected": "fastapi",
                    },
                    {"kind": "call", "call": "requirement_name('# комментарий')", "expected": None},
                    {"kind": "call", "call": "requirement_name('httpx')", "expected": "httpx"},
                    {
                        "kind": "call",
                        "call": "requirement_name('  uvicorn==0.29  ')",
                        "expected": "uvicorn",
                    },
                ],
                "import re\n"
                "\n"
                "\n"
                "def requirement_name(line):\n"
                "    text = line.strip()\n"
                "    if not text or text.startswith('#'):\n"
                "        return None\n"
                "    return re.split(r'[<>=!~;\\s]', text, maxsplit=1)[0]\n",
                "Комментарий и пустая строка дают `None`, а имя отделяется от версии по "
                "символу сравнения или пробелу.",
                "Сначала обрежь пробелы, потом проверь комментарий, а версию отрежь регуляркой.",
            ),
        ],
    ),
    _lesson(
        "cli-environment-pyproject",
        "Один файл с настройками проекта",
        [
            _card(
                "Что такое pyproject.toml",
                "`pyproject.toml` — файл с настройками проекта: именем, версией, "
                "зависимостями и параметрами инструментов. Секции записывают в квадратных "
                "скобках, а значения — парами `ключ = значение`. Имя проекта ищут в секции "
                "`[project]`, потому что именно её читают установщики пакетов.",
                "import tomllib\n"
                "\n"
                'text = \'[project]\\nname = "demo"\\nversion = "1.0"\'\n'
                "data = tomllib.loads(text)\n"
                "print(data['project']['name'])\n"
                "# Вывод:\n"
                "# demo",
                "Для чтения TOML в стандартной библиотеке Python 3.11 есть модуль `tomllib`.",
                run=False,
            ),
            _card(
                "Как найти name в нужной секции",
                "Построчный разбор хранит текущую секцию в переменной. Когда строка "
                "начинается с `[`, секция меняется. Строку с `name` учитывай только тогда, "
                "когда текущая секция равна `[project]`. Значение после `=` очищают от "
                "пробелов и кавычек.",
                'text = \'[project]\\nname = "demo"\\nversion = "1.0"\'\n'
                "section = ''\n"
                "for line in text.splitlines():\n"
                "    line = line.strip()\n"
                "    if line.startswith('['):\n"
                "        section = line\n"
                "    elif section == '[project]' and line.startswith('name'):\n"
                "        print(line.split('=')[1].strip().strip('\"'))\n"
                "# Вывод:\n"
                "# demo",
                "Сравнивай секцию целиком: `[project]` и `[tool.demo]` — разные места.",
            ),
            _card(
                "Типичная ошибка: взять name из чужой секции",
                "Поиск всех строк с `name` без проверки секции находит и имя инструмента. "
                "Тогда программа считает названием проекта совсем другое значение. "
                "Заметить ошибку можно по выводу: имя приходит из `[tool.demo]`, хотя "
                "`[project]` остался без `name`. Всегда отслеживай текущую секцию.",
                'text = \'[project]\\nversion = "1.0"\\n\\n[tool.demo]\\nname = "чужое имя"\'\n'
                "name = None\n"
                "for line in text.splitlines():\n"
                "    if line.startswith('name'):\n"
                "        name = line.split('=')[1].strip().strip('\"')\n"
                "print(name)\n"
                "# Вывод:\n"
                "# чужое имя",
                "Если `name` нашёлся, но проект называется иначе, проверь границы секции.",
            ),
        ],
        [
            _choice(
                "cli-environment-pyproject",
                "Что выведет код?\n\n"
                "text = '[project]\\nname = \"demo\"'\n"
                "inside = False\n"
                "for line in text.splitlines():\n"
                "    if line == '[project]':\n"
                "        inside = True\n"
                "    elif inside and line.startswith('name'):\n"
                "        print(line.split('=')[1].strip().strip('\"'))",
                ["demo", "project", "name", "пусто"],
                "demo",
                "После заголовка `[project]` флаг `inside` включает разбор строки с `name`.",
            ),
            _term(
                "cli-environment-pyproject",
                "В какой секции pyproject.toml находится name проекта?",
                ["project", "[project]", "секция project", "[project] project"],
                "Установщики читают имя проекта из секции `[project]`.",
            ),
            _code(
                "cli-environment-pyproject",
                "Напиши `project_name(text)`: верни значение `name` из секции `[project]` "
                "простого TOML. Если `name` в этой секции нет, верни `None`. Кавычки и "
                "пробелы вокруг значения убери.",
                "def project_name(text):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": 'project_name(\'[project]\\nname = "demo"\\nversion = "1.0"\')',
                        "expected": "demo",
                    },
                    {
                        "kind": "call",
                        "call": "project_name('[project]\\nversion = \"1.0\"')",
                        "expected": None,
                    },
                    {
                        "kind": "call",
                        "call": "project_name('[tool.demo]\\nname = \"чужое\"')",
                        "expected": None,
                    },
                ],
                "def project_name(text):\n"
                "    section = None\n"
                "    for raw_line in text.splitlines():\n"
                "        line = raw_line.strip()\n"
                "        if not line or line.startswith('#'):\n"
                "            continue\n"
                "        if line.startswith('[') and line.endswith(']'):\n"
                "            section = line[1:-1]\n"
                "            continue\n"
                "        if section == 'project' and '=' in line:\n"
                "            key, value = line.split('=', 1)\n"
                "            if key.strip() == 'name':\n"
                "                return value.strip().strip('\"').strip(\"'\")\n"
                "    return None\n",
                "Имя из `[tool.demo]` не считается: функция смотрит только на секцию `project`.",
                "Запоминай заголовок текущей секции и проверяй его перед чтением `name`.",
            ),
        ],
    ),
    _lesson(
        "http-api-request-response",
        "Что клиент отправляет и что получает",
        [
            _card(
                "Что такое HTTP-запрос и ответ",
                "Клиент отправляет запрос: метод, путь и версию протокола. Сервер отвечает "
                "строкой статуса, заголовками и телом. Метод `GET` просит данные, `POST` "
                "отправляет их на сервер. Строка запроса и ответа — это обычный текст, "
                "который можно разобрать по пробелам.",
                "request = 'GET /tasks HTTP/1.1'\n"
                "method, path, version = request.split()\n"
                "print(method)\n"
                "print(path)\n"
                "# Вывод:\n"
                "# GET\n"
                "# /tasks",
                "Сначала читай контракт API, потом собирай запрос.",
            ),
            _card(
                "Как отделить заголовки от тела",
                "Ответ разделён пустой строкой на две части. В первой находятся строка "
                "статуса и заголовки, во второй — тело. `split('\\n\\n', 1)` делит текст "
                "только по первому такому разделителю, поэтому тело остаётся целым. Первую "
                "строку разбирают отдельно: из неё берут код и причину.",
                "response = 'HTTP/1.1 200 OK\\nContent-Type: application/json\\n\\n{\"ok\": true}'\n"
                "head, body = response.split('\\n\\n', 1)\n"
                "print(head.splitlines()[0])\n"
                "print(body)\n"
                "# Вывод:\n"
                "# HTTP/1.1 200 OK\n"
                '# {"ok": true}',
                "Заголовки и тело разделяет именно пустая строка, а не любой перенос.",
            ),
            _card(
                "Типичная ошибка: судить об успехе по телу",
                "Тело есть даже у ответа с ошибкой: сервер часто присылает текст причины. "
                "Если проверять только `if body`, ответ `404` покажется успешным. Заметить "
                "это можно, когда одинаковый код печатает «успех» и для `200`, и для `404`. "
                "Сначала смотри на код статуса, и только потом разбирай тело.",
                "response = 'HTTP/1.1 404 Not Found\\n\\nНет задачи'\n"
                "body = response.split('\\n\\n')[1]\n"
                "print('успех' if body else 'ошибка')\n"
                "# Вывод:\n"
                "# успех",
                "Проверяй статус до чтения тела, иначе ошибка выглядит как успех.",
            ),
        ],
        [
            _choice(
                "http-api-request-response",
                "Что выведет код?\n\n"
                "line = 'HTTP/1.1 404 Not Found'\n"
                "parts = line.split(' ', 2)\n"
                "print(parts[1], parts[2])",
                ["404 Not Found", "200 Not Found", "404 No Content", "HTTP 404 Not"],
                "404 Not Found",
                "`split(' ', 2)` оставляет причину одним куском: `404` и `Not Found`.",
            ),
            _term(
                "http-api-request-response",
                "Какой метод HTTP обычно просит данные у сервера?",
                ["GET", "get", "GET-запрос", "метод GET"],
                "Метод `GET` запрашивает данные и не должен менять состояние сервера.",
            ),
            _code(
                "http-api-request-response",
                "Напиши `parse_status_line(line)`: верни кортеж из кода числа и причины. "
                "Строка `HTTP/1.1 404 Not Found` даёт `(404, 'Not Found')`. Если причины "
                "нет, верни пустую строку.",
                "def parse_status_line(line):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": (
                            "parse_status_line('HTTP/1.1 404 Not Found') == (404, 'Not Found')"
                        ),
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": (
                            "parse_status_line('HTTP/1.1 204 No Content') == (204, 'No Content')"
                        ),
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "parse_status_line('HTTP/1.1 500') == (500, '')",
                        "expected": True,
                    },
                ],
                "def parse_status_line(line):\n"
                "    parts = line.split()\n"
                "    return int(parts[1]), ' '.join(parts[2:])\n",
                "Код стал числом, а причина собрана обратно из оставшихся слов.",
                "Раздели строку по пробелам и возьми второй элемент для кода.",
            ),
        ],
    ),
    _lesson(
        "http-api-json-api",
        "Разбираем данные ответа",
        [
            _card(
                "Что такое JSON в API",
                "JSON — текстовый формат обмена данными. Объект в нём похож на словарь "
                "Python, но ключи и строки всегда в двойных кавычках, а логические значения "
                "записаны как `true` и `false`. Модуль `json` превращает такой текст в "
                "словари и списки, с которыми уже удобно работать в коде.",
                "import json\n"
                "\n"
                "body = '{\"done\": false}'\n"
                "data = json.loads(body)\n"
                "print(data['done'])\n"
                "# Вывод:\n"
                "# False",
                "`json.loads` читает строку, а `json.dumps` делает строку из объекта.",
            ),
            _card(
                "Как достать заголовки из списка items",
                "Сервер часто кладёт коллекцию в поле `items`. После `json.loads` это "
                "обычный список словарей. Пройди по нему и возьми нужное поле у каждого "
                "элемента. Если поля `items` нет, используй пустой список, чтобы не "
                "получить `KeyError`.",
                "import json\n"
                "\n"
                'body = \'{"items": [{"title": "a"}, {"title": "b"}]}\'\n'
                "data = json.loads(body)\n"
                "titles = [item['title'] for item in data['items']]\n"
                "print(titles)\n"
                "# Вывод:\n"
                "# ['a', 'b']",
                "Проверяй структуру ответа до обращения к вложенным полям.",
            ),
            _card(
                "Типичная ошибка: путать JSON со словарём Python",
                "JSON не понимает одинарные кавычки, `True` и `None`. Если передать в "
                "`json.loads` привычное представление словаря, появится `JSONDecodeError`. "
                "Заметить это можно по сообщению парсера: оно указывает на неверный символ "
                "в начале строки.",
                "import json\n"
                "\n"
                "body = \"{'done': False}\"\n"
                "try:\n"
                "    json.loads(body)\n"
                "except json.JSONDecodeError:\n"
                "    print('не JSON')\n"
                "# Вывод:\n"
                "# не JSON",
                "Сначала проверь, что перед тобой действительно JSON, а не repr словаря.",
            ),
        ],
        [
            _choice(
                "http-api-json-api",
                "Что выведет код?\n\n"
                "import json\n"
                'body = \'{"items": [{"title": "a"}, {"title": "b"}]}\'\n'
                "print(len(json.loads(body)['items']))",
                ["2", "1", "3", "0"],
                "2",
                "В поле `items` лежат два объекта, поэтому длина списка равна двум.",
            ),
            _term(
                "http-api-json-api",
                "Каким модулем Python разбирают JSON из ответа API?",
                ["json", "модуль json", "import json", "библиотека json"],
                "Строку JSON превращает в объекты функция `json.loads` из модуля `json`.",
            ),
            _code(
                "http-api-json-api",
                "Напиши `extract_titles(body)`: разбери JSON-строку и верни список значений "
                "`title` из поля `items`. Если поля `items` нет, верни пустой список. "
                "Используй `import json`.",
                "def extract_titles(body):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": ('extract_titles(\'{"items": [{"title": "a"}, {"title": "b"}]}\')'),
                        "expected": ["a", "b"],
                    },
                    {"kind": "call", "call": "extract_titles('{\"total\": 0}')", "expected": []},
                    {
                        "kind": "call",
                        "call": "extract_titles('{\"items\": []}')",
                        "expected": [],
                    },
                ],
                "import json\n"
                "\n"
                "\n"
                "def extract_titles(body):\n"
                "    data = json.loads(body)\n"
                "    items = data.get('items') or []\n"
                "    return [item['title'] for item in items if 'title' in item]\n",
                "Ответ без `items` даёт пустой список, а каждый объект с `title` добавляет "
                "своё название.",
                "Разбери строку через `json.loads`, затем возьми `data.get('items', [])`.",
            ),
        ],
    ),
    _lesson(
        "http-api-status-codes",
        "Один взгляд на итог запроса",
        [
            _card(
                "Что такое код статуса",
                "Код статуса — трёхзначное число в первой строке ответа. Он сообщает общий "
                "итог запроса до разбора тела. Первая цифра задаёт группу: `2` — успех, "
                "`3` — перенаправление, `4` — ошибка клиента, `5` — ошибка сервера. Поэтому "
                "код удобно проверять целой группой, а не перечислять каждое число.",
                "code = 201\nprint(code // 100)\n# Вывод:\n# 2",
                "`201 Created` — тоже успех, хотя это не `200 OK`.",
            ),
            _card(
                "Как разложить коды по группам",
                "Деление на 100 отбрасывает две последние цифры и даёт номер группы. "
                "Дальше сравни номер с `2`, `3`, `4` и `5`. Так один и тот же код `201` и "
                "`204` попадают в успех, а `404` и `400` — в ошибки клиента. Проверяй "
                "группу, если важен общий смысл ответа.",
                "codes = [200, 301, 404, 503]\n"
                "for code in codes:\n"
                "    print(code, code // 100)\n"
                "# Вывод:\n"
                "# 200 2\n"
                "# 301 3\n"
                "# 404 4\n"
                "# 503 5",
                "Группа отвечает на вопрос «кто виноват и что делать», а точный код уточняет детали.",
            ),
            _card(
                "Типичная ошибка: считать успехом только 200",
                "Если сравнивать код с `200`, то `201` и `204` ошибочно попадут в ветку "
                "ошибки. Заметить это легко по ответу: сервер создал запись, а программа "
                "сообщает о проблеме. Проверяй всю группу через `code // 100 == 2`. "
                "Точные коды оставь для случаев, когда важен конкретный оттенок успеха.",
                "code = 201\n"
                "if code == 200:\n"
                "    print('успех')\n"
                "else:\n"
                "    print('ошибка')\n"
                "# Вывод:\n"
                "# ошибка",
                "Если успешный запрос считается ошибкой, проверь, не сравниваешь ли ты только с 200.",
            ),
        ],
        [
            _choice(
                "http-api-status-codes",
                "Что выведет код?\n\ncode = 301\nprint(code // 100)",
                ["3", "2", "4", "30"],
                "3",
                "`301` — перенаправление, поэтому целочисленное деление на 100 даёт `3`.",
            ),
            _term(
                "http-api-status-codes",
                "Какая группа у кода 503?",
                ["5xx", "5", "ошибка сервера", "5хх"],
                "Код `503` начинается с пятёрки, значит это ошибка сервера.",
            ),
            _code(
                "http-api-status-codes",
                "Напиши `status_group(code)`: верни `'успех'` для 2xx, "
                "`'перенаправление'` для 3xx, `'ошибка клиента'` для 4xx, "
                "`'ошибка сервера'` для 5xx и `'неизвестно'` для остальных кодов.",
                "def status_group(code):\n    pass\n",
                [
                    {"kind": "call", "call": "status_group(201)", "expected": "успех"},
                    {
                        "kind": "call",
                        "call": "status_group(404)",
                        "expected": "ошибка клиента",
                    },
                    {"kind": "call", "call": "status_group(99)", "expected": "неизвестно"},
                    {
                        "kind": "call",
                        "call": "status_group(503)",
                        "expected": "ошибка сервера",
                    },
                ],
                "def status_group(code):\n"
                "    group = code // 100\n"
                "    if group == 2:\n"
                "        return 'успех'\n"
                "    if group == 3:\n"
                "        return 'перенаправление'\n"
                "    if group == 4:\n"
                "        return 'ошибка клиента'\n"
                "    if group == 5:\n"
                "        return 'ошибка сервера'\n"
                "    return 'неизвестно'\n",
                "Код `201` относится к группе 2, `404` — к группе 4, а `99` не попадает "
                "ни в одну известную группу.",
                "Сначала получи группу через `code // 100`, затем сравни её с 2, 3, 4 и 5.",
            ),
        ],
    ),
    _lesson(
        "http-api-pagination",
        "Большой список маленькими страницами",
        [
            _card(
                "Что такое пагинация",
                "Пагинация — это выдача большого списка частями. Клиент просит номер "
                "страницы и размер порции, а сервер возвращает только нужный кусок. Так "
                "ответ остаётся небольшим, а приложение не ждёт загрузки всех данных. "
                "Номер страницы обычно начинают с единицы.",
                "items = [1, 2, 3, 4, 5]\n"
                "page, size = 1, 2\n"
                "start = (page - 1) * size\n"
                "print(items[start:start + size])\n"
                "# Вывод:\n"
                "# [1, 2]",
                "Номер страницы и размер порции — разные числа, не путай их.",
            ),
            _card(
                "Как пройти по всем страницам",
                "Индекс первого элемента страницы считают как `(page - 1) * size`. Срез "
                "`items[start:start + size]` берёт не больше `size` элементов: последняя "
                "страница может быть короче. Если индекс вышел за конец списка, срез "
                "вернёт пустой список без ошибки. Поэтому можно спокойно доходить до "
                "страницы, которой уже нет.",
                "items = [1, 2, 3, 4, 5]\n"
                "size = 2\n"
                "for page in range(1, 4):\n"
                "    start = (page - 1) * size\n"
                "    print(items[start:start + size])\n"
                "# Вывод:\n"
                "# [1, 2]\n"
                "# [3, 4]\n"
                "# [5]",
                "Последняя страница не обязана быть полной.",
            ),
            _card(
                "Типичная ошибка: умножать номер страницы без вычитания",
                "Если посчитать `start = page * size`, первая страница начнётся с индекса "
                "2 и первые элементы пропадут. Заметить это можно по второй странице: она "
                "начнётся слишком поздно и вернёт меньше данных. Проверь границу между "
                "страницами: последний элемент первой и первый элемент второй должны идти "
                "подряд.",
                "items = [1, 2, 3, 4, 5]\n"
                "page, size = 2, 2\n"
                "start = page * size\n"
                "print(items[start:start + size])\n"
                "# Вывод:\n"
                "# [5]",
                "Нумерация с единицы требует вычесть её до умножения на размер.",
            ),
        ],
        [
            _choice(
                "http-api-pagination",
                "Что выведет код?\n\n"
                "items = [1, 2, 3, 4, 5]\n"
                "page = 2\n"
                "size = 2\n"
                "start = (page - 1) * size\n"
                "print(items[start:start + size])",
                ["[3, 4]", "[1, 2]", "[5]", "[2, 3]"],
                "[3, 4]",
                "Для второй страницы индекс старта равен `(2 - 1) * 2 == 2`, срез берёт "
                "элементы `3` и `4`.",
            ),
            _term(
                "http-api-pagination",
                "С какого индекса начинается вторая страница при size = 2?",
                ["2", "индекс 2", "2 (третий элемент)", "два"],
                "При нумерации страниц с единицы вторая страница начинается с индекса 2.",
            ),
            _code(
                "http-api-pagination",
                "Напиши `paginate(items, page, size)`: верни кусок списка для страницы с "
                "номером `page`. Страницы считаются с единицы. Если страница за пределами "
                "списка, верни пустой список.",
                "def paginate(items, page, size):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "paginate([1, 2, 3, 4, 5], 2, 2)",
                        "expected": [3, 4],
                    },
                    {"kind": "call", "call": "paginate([1, 2], 3, 2)", "expected": []},
                    {"kind": "call", "call": "paginate([1, 2, 3], 2, 2)", "expected": [3]},
                ],
                "def paginate(items, page, size):\n"
                "    start = (page - 1) * size\n"
                "    return items[start:start + size]\n",
                "Вторая страница начинается с индекса 2 и берёт два элемента; неполная "
                "последняя страница возвращается короче.",
                "Вычисли `start = (page - 1) * size` и верни срез нужной длины.",
            ),
        ],
    ),
]
