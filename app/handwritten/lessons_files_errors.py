"""Рукописные уроки 57–64: файлы, форматы данных и работа с ошибками."""

from __future__ import annotations

from typing import Any


def _card(
    title: str,
    text: str,
    example: str,
    tip: str = "",
    *,
    run: bool = True,
) -> dict[str, Any]:
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


LESSONS: list[dict[str, Any]] = [
    {
        "id": "files-data-pathlib",
        "theory": [
            _card(
                "Path — это путь как объект",
                "Строка с путём не умеет ничего, кроме хранения символов. `Path` из модуля "
                "`pathlib` знает, где папка, а где имя файла, и умеет соединять части пути. "
                "Оператор `/` склеивает части правильно для любой системы: на Linux и на "
                "Windows получится рабочий путь. Начни с двух строк — и больше не думай о "
                "слешах вручную.",
                "from pathlib import Path\n"
                "\n"
                "folder = Path('notes')\n"
                "file = folder / 'today.txt'\n"
                "print(file.as_posix())\n"
                "# Вывод:\n"
                "# notes/today.txt",
                run=False,
            ),
            _card(
                "Имя, основа и расширение",
                "У пути есть готовые части: `name` — имя файла, `stem` — имя без последнего "
                "расширения, `suffix` — само расширение вместе с точкой. Их не нужно "
                "вырезать срезами и считать позиции точек. Это удобно, когда файл "
                "переименовывают или раскладывают по папкам: код читает части пути, а не "
                "угадывает их по длине строки.",
                "from pathlib import Path\n"
                "\n"
                "path = Path('data') / 'report.final.pdf'\n"
                "print(path.name)\n"
                "print(path.stem)\n"
                "print(path.suffix)\n"
                "# Вывод:\n"
                "# report.final.pdf\n"
                "# report.final\n"
                "# .pdf",
                run=False,
            ),
            _card(
                "Типичная ошибка: склеивать путь строкой",
                "Ручная склейка через `+` и жёсткий слеш прячет разделитель внутри строки. "
                "Пока путь один, это незаметно, но на другой системе разделитель другой, а "
                "смесь `/` и `\\` в проекте трудно увидеть глазами. Признак ошибки — слеш "
                "зашит в строку рядом с именем файла. Замени склейку на `Path(...) / 'имя'`, "
                "и путь соберётся по правилам системы.",
                "folder = 'notes'\n"
                "name = 'today.txt'\n"
                "path = folder + '/' + name\n"
                "print(path)\n"
                "# Вывод:\n"
                "# notes/today.txt",
            ),
        ],
        "questions": [
            _choice(
                "files-data-pathlib",
                "Что выведет код?\n\n"
                "`filename = 'report.final.pdf'\n"
                "print('.' + filename.rsplit('.', 1)[1])`",
                [".pdf", ".final", "pdf", "report"],
                ".pdf",
                "`rsplit('.', 1)` режет строку по последней точке, поэтому вторая часть — "
                "`.pdf` вместе с точкой.",
            ),
            _term(
                "files-data-pathlib",
                "Как называется часть пути без расширения: у файла `report.pdf` это `report`?",
                ["stem", "стем", "основа имени", "имя без расширения"],
                "Свойство `Path.stem` возвращает имя без последнего расширения.",
            ),
            _code(
                "files-data-pathlib",
                "Напиши `split_name(filename)`, которая возвращает пару (имя без расширения, "
                "расширение) как строки. Работай с последней точкой: у `report.final.pdf` "
                "расширение `.pdf`, а у `README` расширения нет.",
                "def split_name(filename):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "list(split_name('report.final.pdf'))",
                        "expected": ["report.final", ".pdf"],
                    },
                    {
                        "kind": "call",
                        "call": "list(split_name('README'))",
                        "expected": ["README", ""],
                    },
                    {
                        "kind": "call",
                        "call": "list(split_name('.gitignore'))",
                        "expected": [".gitignore", ""],
                    },
                ],
                "def split_name(filename):\n"
                "    index = filename.rfind('.')\n"
                "    if index <= 0:\n"
                "        return filename, ''\n"
                "    return filename[:index], filename[index:]\n",
                "Путь без расширения возвращается целиком, а расширение начинается с "
                "последней точки. Точка в начале имени расширением не считается.",
                "Найди последнюю точку через `rfind('.')`. Если её нет или она стоит первой, "
                "расширение пустое.",
            ),
        ],
    },
    {
        "id": "files-data-text-files",
        "theory": [
            _card(
                "Файл открывают через with",
                "`open` возвращает файл, но его нужно закрыть, иначе данные могут не "
                "записаться. Конструкция `with` закрывает файл сама, даже если внутри "
                "случилась ошибка. В скобках указывают режим и кодировку: `encoding='utf-8'` "
                "нужен для русского текста. Это самая короткая привычка, которая спасает от "
                "половины проблем с файлами. В примере файл сначала создаётся, а потом "
                "читается — так видно, что `with` закрывает его в обоих случаях.",
                "with open('note.txt', 'w', encoding='utf-8') as file:\n"
                "    file.write('Привет')\n"
                "\n"
                "with open('note.txt', encoding='utf-8') as file:\n"
                "    text = file.read()\n"
                "\n"
                "print(text)\n"
                "# Вывод:\n"
                "# Привет",
                run=False,
            ),
            _card(
                "Запись и чтение по строкам",
                "Режим `'w'` создаёт файл или очищает старый, поэтому запись лучше делать "
                "осознанно. После записи файл можно прочитать построчно: цикл `for line in "
                "file` отдаёт строки вместе с `\\n`, и `strip()` убирает лишние пробелы по "
                "краям. Так удобно обрабатывать списки и журналы, не загружая весь файл в "
                "память.",
                "with open('note.txt', 'w', encoding='utf-8') as file:\n"
                "    file.write('первая строка\\nвторая строка\\n')\n"
                "\n"
                "with open('note.txt', encoding='utf-8') as file:\n"
                "    for line in file:\n"
                "        print(line.strip())\n"
                "# Вывод:\n"
                "# первая строка\n"
                "# вторая строка",
                run=False,
            ),
            _card(
                "Типичная ошибка: забыть encoding",
                "Без `encoding` Python берёт кодировку системы. Если она не совпадает с той, "
                "в которой записан файл, русский текст ломается: чтение падает с "
                "`UnicodeDecodeError` или выдаёт кракозябры. Ошибка вылезает не сразу, поэтому "
                "её трудно связать с открытием файла. В примере неверная кодировка указана "
                "явно (`ascii`), чтобы поломка воспроизвелась на любом компьютере; без "
                "параметра то же случится там, где система ждёт не UTF-8. Замечай `open` без "
                "кодировки и добавляй `encoding='utf-8'` сразу.",
                "from pathlib import Path\n"
                "\n"
                "Path('note.txt').write_text('Привет', encoding='utf-8')\n"
                "\n"
                "try:\n"
                "    with open('note.txt', encoding='ascii') as file:\n"
                "        text = file.read()\n"
                "except UnicodeDecodeError:\n"
                "    text = 'UnicodeDecodeError'\n"
                "\n"
                "print(text)\n"
                "# Вывод:\n"
                "# UnicodeDecodeError",
                run=False,
            ),
        ],
        "questions": [
            _choice(
                "files-data-text-files",
                "Что выведет код?\n\n"
                "`text = 'a\\n\\nb\\n'\n"
                "print(len([line for line in text.splitlines() if line]))`",
                ["2", "3", "1", "0"],
                "2",
                "`splitlines()` даёт три строки, но пустая строка отбрасывается условием, "
                "поэтому остаются `a` и `b`.",
            ),
            _term(
                "files-data-text-files",
                "Какая конструкция гарантированно закрывает файл даже при ошибке?",
                ["with", "with open", "контекстный менеджер", "менеджер контекста"],
                "`with open(...) as file` закрывает файл автоматически на выходе из блока.",
            ),
            _code(
                "files-data-text-files",
                "Напиши `count_lines(text)`, которая считает непустые строки текста файла. "
                "Содержимое приходит строкой, поэтому `open` не нужен. Строка из одних "
                "пробелов тоже пустая.",
                "def count_lines(text):\n    pass\n",
                [
                    {"kind": "call", "call": "count_lines('a\\n\\nb\\n')", "expected": 2},
                    {"kind": "call", "call": "count_lines('')", "expected": 0},
                    {"kind": "call", "call": "count_lines(' \\n\\n')", "expected": 0},
                ],
                "def count_lines(text):\n"
                "    return sum(1 for line in text.splitlines() if line.strip())\n",
                "`splitlines()` разбивает текст на строки, а `line.strip()` отбрасывает "
                "пустые и пробельные строки.",
                "Пройди по `text.splitlines()` и увеличь счётчик, если `line.strip()` не пуст.",
            ),
        ],
    },
    {
        "id": "files-data-json",
        "theory": [
            _card(
                "JSON — общий язык данных",
                "JSON хранит словари, списки, строки, числа и логические значения в тексте. "
                "`json.loads` превращает такую строку в обычные объекты Python, а "
                "`json.dumps` делает обратное. Поэтому JSON понимают почти все языки и "
                "сервисы. Начни с `loads`: если получился словарь, дальше работаешь с ним как "
                "с обычным `dict`.",
                "import json\n"
                "\n"
                'data = json.loads(\'{"done": true, "count": 3}\')\n'
                "print(data['count'])\n"
                "# Вывод:\n"
                "# 3",
            ),
            _card(
                "Словарь в JSON и обратно",
                "`json.dumps` собирает строку из словаря. Параметр `ensure_ascii=False` "
                "оставляет русские буквы читаемыми, а не превращает их в `\\u...`. Обратное "
                "преобразование делает `json.loads`, после чего можно достать вложенный "
                "список по ключу. Так данные переживают запись в файл и передачу по сети.",
                "import json\n"
                "\n"
                "order = {'user': 'Аня', 'items': ['книга', 'ручка']}\n"
                "raw = json.dumps(order, ensure_ascii=False)\n"
                "print(raw)\n"
                "print(json.loads(raw)['items'][0])\n"
                "# Вывод:\n"
                '# {"user": "Аня", "items": ["книга", "ручка"]}\n'
                "# книга",
            ),
            _card(
                "Типичная ошибка: путать JSON с dict",
                "JSON похож на словарь, но требует двойные кавычки и не понимает одинарные. "
                "Строка `{'name': 'Аня'}` — это Python-код, а не JSON, и `json.loads` "
                "бросит `JSONDecodeError`. Заметить просто: ошибка появляется на разборе "
                "строки, ещё до доступа к полям. Проверяй кавычки в исходном тексте.",
                "import json\n"
                "\n"
                "raw = \"{'name': 'Аня'}\"\n"
                "try:\n"
                "    data = json.loads(raw)\n"
                "except json.JSONDecodeError:\n"
                "    data = None\n"
                "print(data)\n"
                "# Вывод:\n"
                "# None",
            ),
        ],
        "questions": [
            _choice(
                "files-data-json",
                "Что выведет код?\n\n"
                "`import json\n"
                'raw = \'{"name": "Аня", "age": 20}\'\n'
                "data = json.loads(raw)\n"
                "print(len(data), data['name'])`",
                ["2 Аня", "1 Аня", "2 20", "Аня 2"],
                "2 Аня",
                "`loads` вернул словарь с двумя ключами, поэтому `len(data)` равно 2, а имя "
                "лежит в ключе `name`.",
            ),
            _term(
                "files-data-json",
                "Какая функция модуля `json` превращает строку в объекты Python?",
                ["json.loads", "loads", "json loads", "loads()"],
                "`json.loads` читает JSON из строки; `json.load` — из файла.",
            ),
            _code(
                "files-data-json",
                "Напиши `user_name(raw)`: разбери JSON-строку через `json` и верни значение "
                "ключа `name`. Если ключа нет, верни `'Гость'`. Импорт `json` добавь в решение.",
                "import json\n\n\ndef user_name(raw):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": 'user_name(\'{"name": "Аня"}\')',
                        "expected": "Аня",
                    },
                    {"kind": "call", "call": "user_name('{}')", "expected": "Гость"},
                    {
                        "kind": "call",
                        "call": "user_name('{\"age\": 20}')",
                        "expected": "Гость",
                    },
                ],
                "import json\n"
                "\n"
                "\n"
                "def user_name(raw):\n"
                "    data = json.loads(raw)\n"
                "    return data.get('name', 'Гость')\n",
                "`json.loads` возвращает словарь, а `get` с запасным значением закрывает "
                "случай без ключа `name`.",
                "После `json.loads` используй `data.get('name', 'Гость')`.",
            ),
        ],
    },
    {
        "id": "files-data-csv",
        "theory": [
            _card(
                "CSV — таблица из строк",
                "CSV хранит таблицу текстом: первая строка обычно содержит заголовки, "
                "остальные — данные, а разделителем чаще всего служит запятая. Каждая строка "
                "разбивается на ячейки, и все значения приходят строками, даже числа. Понимая "
                "это, легко прочитать таблицу без специальных библиотек: раздели строки и "
                "ячейки.",
                "text = 'name,age\\nАня,20\\nЛи,30'\n"
                "lines = text.splitlines()\n"
                "print(lines[0].split(','))\n"
                "# Вывод:\n"
                "# ['name', 'age']",
            ),
            _card(
                "Заголовок превращается в ключи",
                "Если взять первую строку как список заголовков, а каждую следующую — как "
                "список значений, `zip` соединит их попарно. `dict` превращает пары в "
                "словарь, и дальше строку таблицы можно читать по имени колонки: "
                "`row['name']`. Так получается список словарей — удобная форма для "
                "дальнейшей обработки.",
                "text = 'name,age\\nАня,20\\nЛи,30'\n"
                "lines = text.splitlines()\n"
                "header = lines[0].split(',')\n"
                "for line in lines[1:]:\n"
                "    row = dict(zip(header, line.split(',')))\n"
                "    print(row['name'], row['age'])\n"
                "# Вывод:\n"
                "# Аня 20\n"
                "# Ли 30",
            ),
            _card(
                "Типичная ошибка: заголовок попал в данные",
                "Если обработать все строки подряд, первая строка с названиями колонок тоже "
                "станет записью. В результате в отчёте появляется строка `name age` или "
                "попытка сложить число со словом. Заметить легко: проверь, сколько записей "
                "получилось, и сравни с числом строк данных. Заголовок всегда отделяют от "
                "`lines[1:]`.",
                "text = 'name,age\\nАня,20'\n"
                "rows = [line.split(',') for line in text.splitlines()]\n"
                "for row in rows:\n"
                "    print(row[0], row[1])\n"
                "# Вывод:\n"
                "# name age\n"
                "# Аня 20",
            ),
        ],
        "questions": [
            _choice(
                "files-data-csv",
                "Что выведет код?\n\n"
                "`text = 'name,age\\nАня,20\\nЛи,30'\n"
                "header = text.splitlines()[0].split(',')\n"
                "row = text.splitlines()[1].split(',')\n"
                "print(dict(zip(header, row)))`",
                [
                    "{'name': 'Аня', 'age': '20'}",
                    "{'name': 'Ли', 'age': '30'}",
                    "{'age': '20', 'name': 'Аня'}",
                    "{'name': 'Аня', 'age': '30'}",
                ],
                "{'name': 'Аня', 'age': '20'}",
                "Заголовки и значения соединяются по порядку: `name` получает `Аня`, а "
                "`age` — строку `20`.",
            ),
            _term(
                "files-data-csv",
                "Какой символ чаще всего разделяет ячейки в CSV?",
                ["запятая", ",", "comma", "запятая ,"],
                "CSV расшифровывается как comma-separated values — значения через запятую.",
            ),
            _code(
                "files-data-csv",
                "Напиши `parse_csv(text)`: раздели CSV с заголовком на список словарей. "
                "Разделитель — запятая, значения остаются строками. Для пустого текста верни "
                "пустой список.",
                "def parse_csv(text):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "parse_csv('name,age\\nАня,20\\nЛи,30')",
                        "expected": [
                            {"name": "Аня", "age": "20"},
                            {"name": "Ли", "age": "30"},
                        ],
                    },
                    {"kind": "call", "call": "parse_csv('')", "expected": []},
                    {
                        "kind": "call",
                        "call": "parse_csv('name,age')",
                        "expected": [],
                    },
                ],
                "def parse_csv(text):\n"
                "    lines = [line for line in text.splitlines() if line.strip()]\n"
                "    if not lines:\n"
                "        return []\n"
                "    header = lines[0].split(',')\n"
                "    return [dict(zip(header, line.split(','))) for line in lines[1:]]\n",
                "Первая строка даёт заголовки, остальные — значения. `zip` и `dict` "
                "собирают из них пары ключ-значение.",
                "Отдели заголовок, затем для каждой строки данных вызови "
                "`dict(zip(header, line.split(',')))`.",
            ),
        ],
    },
    {
        "id": "errors-debug-exception-types",
        "theory": [
            _card(
                "Тип исключения объясняет причину",
                "Исключение — это сигнал, что операция не может продолжиться. По его типу "
                "видно, какое предположение оказалось неверным: `ValueError` — значение не "
                "подходит, `TypeError` — не тот тип, `KeyError` — нет ключа. Обрабатывай "
                "именно тот тип, который ожидаешь, а не всё подряд. Тогда настоящая ошибка не "
                "спрячется.",
                "values = ['42', 'сорок']\n"
                "for text in values:\n"
                "    try:\n"
                "        print(int(text))\n"
                "    except ValueError:\n"
                "        print('ValueError')\n"
                "# Вывод:\n"
                "# 42\n"
                "# ValueError",
            ),
            _card(
                "Как читать ошибку в консоли",
                "Последняя строка traceback называет тип и сообщение, а строки выше показывают "
                "место вызова. Начни с типа: он подсказывает, где искать. В примере "
                "отсутствующий ключ даёт `KeyError`, и это ожидаемо. Если вместо `KeyError` "
                "появился `TypeError`, значит, проблема раньше — например, в данных оказался "
                "не словарь.",
                "data = {'name': 'Аня'}\n"
                "try:\n"
                "    print(data['age'])\n"
                "except KeyError:\n"
                "    print('KeyError')\n"
                "# Вывод:\n"
                "# KeyError",
            ),
            _card(
                "Типичная ошибка: ловить всё подряд",
                "`except Exception` перехватывает и ожидаемую ошибку, и опечатку в коде. "
                "Программа продолжает работать, но неправильный результат выглядит как "
                "нормальный: в примере `double('семь')` вернул 0, хотя это не число. "
                "Замечай широкий `except` и сужай его до `ValueError`. Если ошибку не ждёшь — "
                "дай ей всплыть.",
                "def double(text):\n"
                "    try:\n"
                "        return int(text) * 2\n"
                "    except Exception:\n"
                "        return 0\n"
                "\n"
                "print(double('7'))\n"
                "print(double('семь'))\n"
                "# Вывод:\n"
                "# 14\n"
                "# 0",
            ),
        ],
        "questions": [
            _choice(
                "errors-debug-exception-types",
                "Что выведет код?\n\n"
                "`def to_int(text):\n"
                "    try:\n"
                "        return int(text)\n"
                "    except ValueError:\n"
                "        return 0\n"
                "\n"
                "print(to_int('12') + to_int('x'))`",
                ["12", "13", "0", "x"],
                "12",
                "Для `'12'` функция вернула 12, для `'x'` сработал `except` и вернул 0. Сумма "
                "равна 12.",
            ),
            _term(
                "errors-debug-exception-types",
                "Какое исключение бросает `int('abc')`?",
                ["ValueError", "value error", "вельюэррор", "ошибка значения"],
                "Строка не является числом, поэтому `int` бросает `ValueError`.",
            ),
            _code(
                "errors-debug-exception-types",
                "Напиши `safe_int(text)`: верни результат `int(text)`, а при `ValueError` — "
                "`None`. Другие ошибки не перехватывай.",
                "def safe_int(text):\n    pass\n",
                [
                    {"kind": "call", "call": "safe_int('42')", "expected": 42},
                    {"kind": "call", "call": "safe_int('сорок')", "expected": None},
                    {"kind": "call", "call": "safe_int('')", "expected": None},
                ],
                "def safe_int(text):\n"
                "    try:\n"
                "        return int(text)\n"
                "    except ValueError:\n"
                "        return None\n",
                "`int` принимает только подходящую строку. Узкий `except ValueError` "
                "возвращает `None` и не прячет остальные ошибки.",
                "Оберни `int(text)` в `try`, а в `except ValueError` верни `None`.",
            ),
        ],
    },
    {
        "id": "errors-debug-raise",
        "theory": [
            _card(
                "raise сообщает о нарушении правила",
                "Иногда значение технически допустимо, но нарушает правило программы: "
                "возраст не может быть отрицательным. Молча вернуть `None` или напечатать "
                "предупреждение мало — вызывающий код продолжит работу с плохими данными. "
                "`raise ValueError('...')` останавливает выполнение и объясняет причину. "
                "Проверяй вход на границе функции.",
                "def check_age(age):\n"
                "    if age < 0:\n"
                "        raise ValueError('возраст не может быть отрицательным')\n"
                "    return age\n"
                "\n"
                "print(check_age(20))\n"
                "# Вывод:\n"
                "# 20",
            ),
            _card(
                "Ошибку можно поймать и показать",
                "Брошенное исключение не обязано завершать программу: вызывающий код может "
                "поймать его через `try/except`. В примере `check_age(-1)` бросает "
                "`ValueError`, а `except` получает объект ошибки и печатает его сообщение. "
                "Так проверка остаётся строгой, но интерфейс показывает понятный текст вместо "
                "traceback.",
                "def check_age(age):\n"
                "    if age < 0:\n"
                "        raise ValueError('возраст не может быть отрицательным')\n"
                "    return age\n"
                "\n"
                "try:\n"
                "    check_age(-1)\n"
                "except ValueError as error:\n"
                "    print(error)\n"
                "# Вывод:\n"
                "# возраст не может быть отрицательным",
            ),
            _card(
                "Типичная ошибка: сообщать об ошибке через print",
                "Если функция просто печатает текст и возвращает `None`, вызывающий код не "
                "узнает, что данные плохие. В примере `check_age(-1)` печатает "
                "предупреждение, но возвращает `None` — и это уходит дальше как обычный "
                "результат. Замечай функции, которые сообщают об ошибке только печатью. "
                "Бросай исключение, чтобы ошибку нельзя было не заметить.",
                "def check_age(age):\n"
                "    if age < 0:\n"
                "        print('возраст не может быть отрицательным')\n"
                "        return None\n"
                "    return age\n"
                "\n"
                "print(check_age(-1))\n"
                "# Вывод:\n"
                "# возраст не может быть отрицательным\n"
                "# None",
            ),
        ],
        "questions": [
            _choice(
                "errors-debug-raise",
                "Что выведет код?\n\n"
                "`def check_age(age):\n"
                "    if age < 0:\n"
                "        raise ValueError('мало')\n"
                "    return age\n"
                "\n"
                "print(check_age(-1))`",
                ["ValueError", "TypeError", "KeyError", "IndexError"],
                "ValueError",
                "Отрицательный возраст попадает в ветку с `raise ValueError`, и программа "
                "завершается этим исключением.",
            ),
            _term(
                "errors-debug-raise",
                "Какая команда явно бросает исключение?",
                ["raise", "рейз", "raise ValueError", "команда raise"],
                "`raise` запускает исключение вручную, например `raise ValueError('текст')`.",
            ),
            _code(
                "errors-debug-raise",
                "Напиши `check_age(age)`: при отрицательном возрасте бросай "
                "`ValueError('возраст не может быть отрицательным')`, иначе возвращай "
                "возраст. Напиши `describe(age)`: верни текст ошибки через `str(error)` или "
                "`'ok'`, если ошибки нет.",
                "def check_age(age):\n    pass\n\n\ndef describe(age):\n    pass\n",
                [
                    {"kind": "call", "call": "check_age(30)", "expected": 30},
                    {"kind": "call", "call": "describe(30)", "expected": "ok"},
                    {
                        "kind": "call",
                        "call": "describe(-1)",
                        "expected": "возраст не может быть отрицательным",
                    },
                ],
                "def check_age(age):\n"
                "    if age < 0:\n"
                "        raise ValueError('возраст не может быть отрицательным')\n"
                "    return age\n"
                "\n"
                "\n"
                "def describe(age):\n"
                "    try:\n"
                "        check_age(age)\n"
                "    except ValueError as error:\n"
                "        return str(error)\n"
                "    return 'ok'\n",
                "`check_age` проверяет вход и бросает `ValueError`, а `describe` ловит его и "
                "возвращает текст ошибки.",
                "В `check_age` добавь условие `age < 0` с `raise`, а в `describe` оберни "
                "вызов в `try/except ValueError`.",
            ),
        ],
    },
    {
        "id": "errors-debug-finally",
        "theory": [
            _card(
                "Ветки try, except, else и finally",
                "`try` содержит рискованную операцию. `except` срабатывает при ошибке, "
                "`else` — только если ошибки не было, а `finally` — всегда, независимо от "
                "исхода. Такое разделение делает сценарии явными: успех и авария не "
                "смешиваются. Начни с `try/except`, а `else` и `finally` добавляй, когда они "
                "действительно нужны.",
                "try:\n"
                "    number = int('42')\n"
                "except ValueError:\n"
                "    number = 0\n"
                "else:\n"
                "    print('разбор прошёл')\n"
                "finally:\n"
                "    print('готово')\n"
                "# Вывод:\n"
                "# разбор прошёл\n"
                "# готово",
            ),
            _card(
                "else отделяет успех от обработки",
                "Код в `try` должен быть коротким: только то, что может дать ожидаемую "
                "ошибку. Всё, что делается после успеха, лучше вынести в `else`. Тогда "
                "`except` не поймает ошибку из лишнего кода. В примере деление идёт в `try`, "
                "а возврат результата — в `else`, поэтому ветки легко проверить отдельно.",
                "def divide(a, b):\n"
                "    try:\n"
                "        result = a / b\n"
                "    except ZeroDivisionError:\n"
                "        return 'на ноль делить нельзя'\n"
                "    else:\n"
                "        return result\n"
                "\n"
                "print(divide(6, 3))\n"
                "print(divide(1, 0))\n"
                "# Вывод:\n"
                "# 2.0\n"
                "# на ноль делить нельзя",
            ),
            _card(
                "Типичная ошибка: return в finally",
                "`finally` выполняется всегда, и `return` внутри него перекрывает всё, что "
                "функция собиралась вернуть или бросить. В примере ошибка `int('сорок')` "
                "исчезает: `finally` возвращает 0, и снаружи видно нормальный результат. "
                "Замечай `return` в `finally` — обычно там должны быть только очистка и "
                "закрытие ресурсов.",
                "def parse(text):\n"
                "    try:\n"
                "        return int(text)\n"
                "    finally:\n"
                "        return 0\n"
                "\n"
                "print(parse('сорок'))\n"
                "# Вывод:\n"
                "# 0",
            ),
        ],
        "questions": [
            _choice(
                "errors-debug-finally",
                "Что выведет код?\n\n"
                "`def check(text):\n"
                "    try:\n"
                "        int(text)\n"
                "    except ValueError:\n"
                "        print('except')\n"
                "    else:\n"
                "        print('else')\n"
                "    finally:\n"
                "        print('finally')\n"
                "\n"
                "check('5')`",
                ["else\nfinally", "try\nelse", "try\nexcept", "except\nfinally"],
                "else\nfinally",
                "`int('5')` проходит без ошибки, поэтому выполняется `else`, а `finally` "
                "выполняется всегда.",
            ),
            _term(
                "errors-debug-finally",
                "Какой блок выполняется всегда, даже если была ошибка?",
                ["finally", "финали", "блок finally", "final"],
                "Блок `finally` выполняют при любом исходе, поэтому там освобождают ресурсы.",
            ),
            _code(
                "errors-debug-finally",
                "Напиши `divide_steps(a, b)`, которая возвращает список пройденных веток. "
                "Сначала добавь `'try'`, затем `'else'` при успешном делении или `'except'` "
                "при `ZeroDivisionError`, а в конце всегда `'finally'`.",
                "def divide_steps(a, b):\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "divide_steps(4, 2)",
                        "expected": ["try", "else", "finally"],
                    },
                    {
                        "kind": "call",
                        "call": "divide_steps(1, 0)",
                        "expected": ["try", "except", "finally"],
                    },
                    {
                        "kind": "call",
                        "call": "divide_steps(0, 5)",
                        "expected": ["try", "else", "finally"],
                    },
                ],
                "def divide_steps(a, b):\n"
                "    steps = []\n"
                "    try:\n"
                "        steps.append('try')\n"
                "        a / b\n"
                "    except ZeroDivisionError:\n"
                "        steps.append('except')\n"
                "    else:\n"
                "        steps.append('else')\n"
                "    finally:\n"
                "        steps.append('finally')\n"
                "    return steps\n",
                "Список заполняется по мере прохождения веток: `try` всегда первый, "
                "`finally` всегда последний.",
                "Заведи список `steps`, добавляй метки в каждой ветке и верни его в конце.",
            ),
        ],
    },
    {
        "id": "errors-debug-debugging",
        "theory": [
            _card(
                "Отладка начинается с наблюдения",
                "Не угадывай, что лежит в переменной, — посмотри. `print` с f-строкой "
                "показывает значение и имя сразу: `f'{total=}'` печатает `total=6`. Это "
                "быстрее, чем мысленно прокручивать код. Сначала выведи входные данные и "
                "промежуточный результат, и место ошибки сузится.",
                "def average(items):\n"
                "    total = sum(items)\n"
                "    print(f'{total=}, {len(items)=}')\n"
                "    return total / len(items)\n"
                "\n"
                "print(average([2, 4]))\n"
                "# Вывод:\n"
                "# total=6, len(items)=2\n"
                "# 3.0",
            ),
            _card(
                "Минимальный пример повторяет ошибку",
                "Большой набор данных прячет причину. Сократи вход до самого маленького, на "
                "котором ошибка всё ещё воспроизводится, и проверь границы: пустой список, "
                "ноль, один элемент. В примере обычный список работает, а пустой даёт "
                "`ZeroDivisionError` — значит, дело в делении на `len(items)`. Так гипотеза "
                "становится проверяемой.",
                "def average(items):\n"
                "    return sum(items) / len(items)\n"
                "\n"
                "for items in ([1, 2, 3], []):\n"
                "    try:\n"
                "        print(items, average(items))\n"
                "    except ZeroDivisionError:\n"
                "        print(items, 'ZeroDivisionError')\n"
                "# Вывод:\n"
                "# [1, 2, 3] 2.0\n"
                "# [] ZeroDivisionError",
            ),
            _card(
                "Типичная ошибка: off-by-one в делителе",
                "Лишняя единица в делителе не роняет программу, а тихо портит результат: "
                "среднее становится меньше. Заметить это можно только сравнением с ручным "
                "расчётом на простом примере. Всегда проверяй формулу на маленьких числах и "
                "на границе. В примере сумма 6 делится на 4 вместо 3, поэтому выходит 1.5 "
                "вместо 2.0.",
                "def average(items):\n"
                "    return sum(items) / (len(items) + 1)\n"
                "\n"
                "print(average([1, 2, 3]))\n"
                "# Вывод:\n"
                "# 1.5",
            ),
        ],
        "questions": [
            _choice(
                "errors-debug-debugging",
                "Что выведет код?\n\n"
                "`def average(items):\n"
                "    return sum(items) / (len(items) + 1)\n"
                "\n"
                "print(average([1, 2, 3]))`",
                ["1.5", "2.0", "2.5", "3.0"],
                "1.5",
                "Сумма равна 6, а делитель — 3 + 1 = 4. Результат 6 / 4 = 1.5.",
            ),
            _term(
                "errors-debug-debugging",
                "Какой простой способ увидеть значение переменной во время выполнения?",
                ["print", "принт", "print()", "вывести через print"],
                "`print` или f-строка с `=` показывает значение в нужном месте программы.",
            ),
            _code(
                "errors-debug-debugging",
                "Перед тобой сломанная `average(items)`: на пустом списке она падает с "
                "`ZeroDivisionError`. Почини функцию так, чтобы для пустого списка она "
                "возвращала 0, а для остальных считала обычное среднее.",
                "def average(items):\n    return sum(items) / len(items)\n",
                [
                    {"kind": "call", "call": "average([1, 2, 3])", "expected": 2},
                    {"kind": "call", "call": "average([])", "expected": 0},
                    {"kind": "call", "call": "average([5, 5])", "expected": 5},
                ],
                "def average(items):\n"
                "    if not items:\n"
                "        return 0\n"
                "    return sum(items) / len(items)\n",
                "Пустой список — граничный случай: до деления проверь `if not items` и верни 0.",
                "Добавь в начало функции проверку пустого списка и ранний `return 0`.",
            ),
        ],
    },
]
