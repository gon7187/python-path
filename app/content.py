"""Русский учебный план: 12 уроков, практика и контрольные точки."""

from __future__ import annotations

from app.extended_curriculum import EXTRA_EXAMS, EXTRA_LESSONS, EXTRA_MODULES


def theory(title: str, text: str, example: str, tip: str = "") -> dict:
    return {"title": title, "text": text, "example": example, "tip": tip}


def choice(
    question_id: str, prompt: str, options: list[str], answer: str, explanation: str
) -> dict:
    return {
        "id": question_id,
        "kind": "choice",
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def text(question_id: str, prompt: str, answers: list[str], explanation: str) -> dict:
    return {
        "id": question_id,
        "kind": "input",
        "prompt": prompt,
        "answers": answers,
        "placeholder": "Введите ответ",
        "explanation": explanation,
    }


def code(
    question_id: str, prompt: str, starter: str, tests: list[dict], explanation: str, hint: str
) -> dict:
    return {
        "id": question_id,
        "kind": "code",
        "prompt": prompt,
        "starter": starter,
        "tests": tests,
        "explanation": explanation,
        "hint": hint,
    }


def lesson(
    lesson_id: str,
    module_id: str,
    order: int,
    title: str,
    subtitle: str,
    duration: int,
    xp: int,
    theory_cards: list[dict],
    questions: list[dict],
) -> dict:
    return {
        "id": lesson_id,
        "module_id": module_id,
        "order": order,
        "title": title,
        "subtitle": subtitle,
        "duration": duration,
        "xp": xp,
        "theory": theory_cards,
        "questions": questions,
    }


MODULES = [
    {
        "id": "start",
        "title": "Старт: говорим с Python",
        "description": "Первая программа, переменные, типы и ввод данных.",
        "color": "mint",
        "icon": "🌱",
    },
    {
        "id": "logic",
        "title": "Логика и повторения",
        "description": "Условия и циклы: программа начинает думать.",
        "color": "sky",
        "icon": "🧠",
    },
    {
        "id": "structures",
        "title": "Функции и данные",
        "description": "Собираем код в блоки и работаем с коллекциями.",
        "color": "violet",
        "icon": "🧩",
    },
    {
        "id": "realworld",
        "title": "Python в деле",
        "description": "Файлы, ошибки и первые собственные классы.",
        "color": "sun",
        "icon": "🚀",
    },
]


LESSONS = [
    lesson(
        "hello",
        "start",
        1,
        "Знакомство с Python",
        "Запускаем первую программу",
        7,
        20,
        [
            theory(
                "Программа — точная инструкция",
                "Python выполняет команды сверху вниз. Одна строка обычно описывает одно действие.",
                "print('Привет, мир!')",
                "После print обязательно ставь круглые скобки.",
            ),
            theory(
                "Текст любит кавычки",
                "Текст в одинарных или двойных кавычках называется строкой (str).",
                'print("Я учу Python")',
            ),
            theory(
                "Ошибки — это подсказки",
                "Если что-то не работает, прочитай последнюю строку сообщения: в ней указан тип ошибки и место.",
                "print('Готово!')\nprint('Следующий шаг')",
            ),
        ],
        [
            choice(
                "hello-print",
                "Какая команда выводит текст на экран?",
                ["show('Привет')", "print('Привет')", "output('Привет')"],
                "print('Привет')",
                "В Python за вывод на экран отвечает функция print().",
            ),
            text(
                "hello-string",
                'Как называется значение `"Привет"` в Python?',
                ["строка", "string"],
                "Текст в кавычках — это строка (string).",
            ),
            code(
                "hello-code",
                "Выведи на экран фразу: `Я начинаю путь в Python!`",
                "# Напиши одну команду\n",
                [{"kind": "stdout", "expected": "Я начинаю путь в Python!"}],
                "Отлично! Твоя первая программа уже общается с пользователем.",
                "Используй print(), а фразу заключи в кавычки.",
            ),
        ],
    ),
    lesson(
        "variables",
        "start",
        2,
        "Переменные и типы",
        "Дадим значениям имена",
        9,
        25,
        [
            theory(
                "Переменная — подпись на коробке",
                "Оператор = сохраняет значение в переменной. Слева имя, справа — значение.",
                "score = 10\nname = 'Маша'",
                "Имя пишут без пробелов, часто в snake_case: total_score.",
            ),
            theory(
                "У значений есть тип",
                "Целые числа — int, дробные — float, текст — str, правда/ложь — bool.",
                "age = 18\nprice = 19.9\nis_ready = True",
            ),
            theory(
                "f-строки собирают текст",
                "Поставь f перед строкой и помести переменную в фигурные скобки.",
                "name = 'Лена'\nprint(f'Привет, {name}!')",
            ),
        ],
        [
            choice(
                "var-type",
                "Какой тип у значения `False`?",
                ["str", "bool", "int"],
                "bool",
                "False и True — логические значения типа bool.",
            ),
            text(
                "var-value",
                "После `coins = 4`, чему равно `coins + 3`?",
                ["7"],
                "Python подставляет значение переменной: 4 + 3 = 7.",
            ),
            code(
                "var-code",
                "Создай `city = 'Казань'` и выведи `Город: Казань` через f-строку.",
                "city = ''\n# выведи город\n",
                [{"kind": "stdout", "expected": "Город: Казань"}],
                "Переменная помогла не дублировать значение и сделать код гибче.",
                "Сначала присвой город, затем вызови print(f'Город: {city}').",
            ),
        ],
    ),
    lesson(
        "strings-input",
        "start",
        3,
        "Строки и ввод",
        "Получаем данные от человека",
        10,
        25,
        [
            theory(
                "input возвращает текст",
                "Функция input ждёт ответ пользователя и всегда возвращает str — даже если введены цифры.",
                "name = input('Как тебя зовут? ')\nprint(f'Рада знакомству, {name}!')",
            ),
            theory(
                "Преобразуем типы осознанно",
                "Чтобы получить число из ввода, оберни input в int() или float().",
                "age = int(input('Твой возраст: '))\nprint(age + 1)",
                "Преобразовывай в число, только когда ожидаешь цифры.",
            ),
            theory(
                "Методы строк",
                "lower() меняет регистр, strip() убирает пробелы по краям, len() считает символы.",
                "word = '  Python  '\nprint(word.strip().lower())",
            ),
        ],
        [
            choice(
                "input-type",
                "Какой тип вернёт `input()` без преобразования?",
                ["int", "str", "bool"],
                "str",
                "Даже введённое 42 сначала будет строкой '42'.",
            ),
            text("string-len", "Чему равно `len('кот')`?", ["3"], "В слове «кот» три символа."),
            code(
                "string-code",
                "Создай `word = 'python'` и выведи его длину.",
                "word = 'python'\n# выведи длину слова\n",
                [{"kind": "stdout", "expected": "6"}],
                "len() возвращает количество символов в строке.",
                "Передай word в len(), а результат — в print().",
            ),
        ],
    ),
    lesson(
        "conditions",
        "logic",
        4,
        "Условия: if и else",
        "Учимся принимать решения",
        12,
        30,
        [
            theory(
                "if проверяет условие",
                "Если условие истинно, Python выполняет вложенный блок. Отступ в четыре пробела — часть синтаксиса.",
                "temperature = 22\nif temperature > 20:\n    print('Можно без куртки')",
                "После условия ставится двоеточие.",
            ),
            theory(
                "else — запасной сценарий",
                "Когда условие ложно, срабатывает else. Для нескольких вариантов есть elif.",
                "if score >= 80:\n    print('Отлично')\nelse:\n    print('Продолжай')",
            ),
            theory(
                "Сравниваем, а не присваиваем",
                "== сравнивает значения, != означает «не равно», >= — «больше или равно».",
                "if password == 'python':\n    print('Вход выполнен')",
            ),
        ],
        [
            choice(
                "if-equality",
                "Каким оператором сравнивают два значения?",
                ["=", "==", ">="],
                "==",
                "Один знак = присваивает, два знака == сравнивают.",
            ),
            text(
                "if-result",
                "Что выведет `if 3 > 5: print('да') else: print('нет')`?",
                ["нет"],
                "3 не больше 5, поэтому выполняется ветка else.",
            ),
            code(
                "if-code",
                "Напиши `is_adult(age)`, возвращающую True при возрасте 18 и больше.",
                "def is_adult(age):\n    # твой код\n    pass\n",
                [
                    {"kind": "call", "call": "is_adult(18)", "expected": True},
                    {"kind": "call", "call": "is_adult(17)", "expected": False},
                ],
                "Условие внутри функции помогает вернуть нужный логический результат.",
                "Сравни age с 18 и верни результат сравнения либо используй if/else.",
            ),
        ],
    ),
    lesson(
        "for-loop",
        "logic",
        5,
        "Цикл for",
        "Повторяем действия без копипаста",
        11,
        30,
        [
            theory(
                "for проходит по элементам",
                "Цикл for по очереди берёт элементы из строки, списка или диапазона.",
                "for letter in 'код':\n    print(letter)",
            ),
            theory(
                "range создаёт числа",
                "range(5) выдаёт числа от 0 до 4: верхняя граница не включается.",
                "for number in range(1, 4):\n    print(number)  # 1, 2, 3",
            ),
            theory(
                "Накапливаем результат",
                "Создай переменную-накопитель до цикла и меняй её на каждом шаге.",
                "total = 0\nfor number in range(1, 4):\n    total += number",
            ),
        ],
        [
            choice(
                "for-range",
                "Сколько раз выполнится тело `for _ in range(4)`?",
                ["3", "4", "5"],
                "4",
                "range(4) содержит 0, 1, 2 и 3 — четыре значения.",
            ),
            text("for-sum", "Чему равна сумма чисел в `range(1, 4)`?", ["6"], "Это 1 + 2 + 3 = 6."),
            code(
                "for-code",
                "Напиши `sum_to(number)`, возвращающую сумму от 1 до number включительно.",
                "def sum_to(number):\n    # твой код\n    pass\n",
                [
                    {"kind": "call", "call": "sum_to(1)", "expected": 1},
                    {"kind": "call", "call": "sum_to(5)", "expected": 15},
                ],
                "Цикл избавляет от ручного сложения каждого числа.",
                "Создай total = 0 и пройди range(1, number + 1).",
            ),
        ],
    ),
    lesson(
        "while-loop",
        "logic",
        6,
        "Цикл while",
        "Повторяем, пока выполняется условие",
        12,
        30,
        [
            theory(
                "while проверяет условие",
                "Тело цикла выполняется, пока условие истинно. Важно менять переменную условия.",
                "count = 3\nwhile count > 0:\n    print(count)\n    count -= 1",
                "Если count не уменьшать, получится бесконечный цикл.",
            ),
            theory(
                "break завершает цикл",
                "break нужен, когда нужный ответ найден или работу следует прекратить раньше.",
                "while True:\n    command = 'стоп'\n    if command == 'стоп':\n        break",
            ),
            theory(
                "Выбираем цикл",
                "for удобен, когда известны элементы. while — когда важен момент, в который условие станет ложным.",
                "attempts = 0\nwhile attempts < 3:\n    attempts += 1",
            ),
        ],
        [
            choice(
                "while-infinite",
                "Что чаще всего вызывает бесконечный while-цикл?",
                ["Условие никогда не меняется", "В цикле есть print", "Есть переменная"],
                "Условие никогда не меняется",
                "Переменная условия должна приближать цикл к завершению.",
            ),
            text(
                "while-count",
                "Сколько чисел выведет цикл: count = 2, while count > 0, count -= 1?",
                ["2"],
                "Будут выведены 2 и 1, затем условие станет ложным.",
            ),
            code(
                "while-code",
                "Напиши `countdown(start)`, возвращающую список от start до 1 через while.",
                "def countdown(start):\n    # твой код\n    pass\n",
                [
                    {"kind": "call", "call": "countdown(1)", "expected": [1]},
                    {"kind": "call", "call": "countdown(4)", "expected": [4, 3, 2, 1]},
                ],
                "while хорош, когда счётчик меняется до достижения границы.",
                "Начни с result = [] и уменьшай start после добавления в список.",
            ),
        ],
    ),
    lesson(
        "functions",
        "structures",
        7,
        "Функции",
        "Убираем повторения из кода",
        13,
        35,
        [
            theory(
                "Функция упаковывает действие",
                "def создаёт функцию, а параметры принимают данные снаружи.",
                "def greet(name):\n    print(f'Привет, {name}!')",
            ),
            theory(
                "return отдаёт результат",
                "print показывает значение человеку, return возвращает его в программу для дальнейшей работы.",
                "def double(number):\n    return number * 2",
            ),
            theory(
                "Имя функции — обещание",
                "Хорошее имя отвечает на вопрос: что делает функция? Используй глагол или понятное действие.",
                "def calculate_discount(price):\n    return price * 0.9",
            ),
        ],
        [
            choice(
                "func-return",
                "Что позволяет использовать результат функции в выражении?",
                ["print", "return", "def"],
                "return",
                "return передаёт значение туда, где функцию вызвали.",
            ),
            text(
                "func-call",
                "Чему равно `triple(4)`, если функция возвращает number * 3?",
                ["12"],
                "Функция умножает переданное 4 на 3.",
            ),
            code(
                "func-code",
                "Напиши `greeting(name)`, возвращающую `Привет, <name>!`.",
                "def greeting(name):\n    # твой код\n    pass\n",
                [
                    {"kind": "call", "call": "greeting('Аня')", "expected": "Привет, Аня!"},
                    {"kind": "call", "call": "greeting('Илья')", "expected": "Привет, Илья!"},
                ],
                "Параметр делает одну функцию полезной для разных имён.",
                "Верни f-строку, не печатай её: здесь нужен return.",
            ),
        ],
    ),
    lesson(
        "lists",
        "structures",
        8,
        "Списки",
        "Храним несколько значений",
        13,
        35,
        [
            theory(
                "Список хранит порядок",
                "Элементы списка записывают в квадратных скобках через запятую.",
                "fruits = ['яблоко', 'груша', 'слива']",
            ),
            theory(
                "Индексы начинаются с нуля",
                "Первый элемент — [0], второй — [1]. Индекс -1 берёт элемент с конца.",
                "colors = ['красный', 'синий']\nprint(colors[0])",
            ),
            theory(
                "Методы меняют список",
                "append добавляет элемент в конец, pop удаляет и возвращает, len считает размер.",
                "tasks = ['код']\ntasks.append('отдых')",
            ),
        ],
        [
            choice(
                "list-index",
                "Как получить первый элемент списка `items`?",
                ["items[1]", "items[0]", "items.first"],
                "items[0]",
                "Индексация в Python начинается с нуля.",
            ),
            text("list-length", "Чему равно `len([10, 20, 30])`?", ["3"], "В списке три элемента."),
            code(
                "list-code",
                "Напиши `last_item(items)`, которая возвращает последний элемент списка.",
                "def last_item(items):\n    # твой код\n    pass\n",
                [
                    {"kind": "call", "call": "last_item(['a', 'b'])", "expected": "b"},
                    {"kind": "call", "call": "last_item([3, 7, 9])", "expected": 9},
                ],
                "Отрицательный индекс достаёт последний элемент независимо от длины списка.",
                "Используй индекс -1.",
            ),
        ],
    ),
    lesson(
        "dicts-sets",
        "structures",
        9,
        "Словари и множества",
        "Быстро находим данные и убираем повторы",
        14,
        35,
        [
            theory(
                "Словарь хранит пары",
                "По ключу можно быстро найти нужное значение. Ключи часто делают строками.",
                "user = {'name': 'Саша', 'level': 3}\nprint(user['name'])",
            ),
            theory(
                "get безопаснее",
                "dict.get('ключ', запасное) не выдаст ошибку, если ключ отсутствует.",
                "theme = settings.get('theme', 'light')",
            ),
            theory(
                "Множество хранит уникальное",
                "set автоматически удаляет дубликаты; порядок его элементов не гарантирован.",
                "tags = {'python', 'api', 'python'}\nprint(len(tags))  # 2",
            ),
        ],
        [
            choice(
                "dict-key",
                "Как получить имя из `user = {'name': 'Оля'}`?",
                ["user.name", "user['name']", "user('name')"],
                "user['name']",
                "Словарь получает значение по ключу в квадратных скобках.",
            ),
            text(
                "set-unique",
                "Сколько элементов в `set([1, 1, 2, 3, 3])`?",
                ["3"],
                "Множество оставит уникальные 1, 2 и 3.",
            ),
            code(
                "dict-code",
                "Напиши `get_level(profile)`: верни level, а если ключа нет — 1.",
                "def get_level(profile):\n    # твой код\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "get_level({'name': 'Аня', 'level': 4})",
                        "expected": 4,
                    },
                    {"kind": "call", "call": "get_level({'name': 'Аня'})", "expected": 1},
                ],
                "get позволяет задать понятное значение по умолчанию.",
                "Вспомни метод словаря .get('level', 1).",
            ),
        ],
    ),
    lesson(
        "files",
        "realworld",
        10,
        "Файлы",
        "Сохраняем данные между запусками",
        12,
        35,
        [
            theory(
                "Файл открывают через with",
                "with сам корректно закроет файл, даже если внутри произойдёт ошибка.",
                "with open('notes.txt', encoding='utf-8') as file:\n    text = file.read()",
            ),
            theory(
                "Режимы чтения и записи",
                "'r' читает, 'w' перезаписывает, 'a' дописывает. Для русского текста указывай utf-8.",
                "with open('notes.txt', 'w', encoding='utf-8') as file:\n    file.write('Первая заметка')",
            ),
            theory(
                "Работаем построчно",
                "Файл можно перебирать в цикле — не нужно загружать всё содержимое сразу.",
                "for line in file:\n    print(line.strip())",
            ),
        ],
        [
            choice(
                "file-mode",
                "Какой режим открывает файл для добавления в конец?",
                ["'r'", "'w'", "'a'"],
                "'a'",
                "Режим append ('a') дописывает текст, не стирая старое содержимое.",
            ),
            text(
                "file-with",
                "Какое ключевое слово помогает автоматически закрыть файл?",
                ["with"],
                "with управляет ресурсом и закроет файл после блока.",
            ),
            code(
                "file-code",
                "Напиши `format_note(title)`, возвращающую `Заметка: <title>`.",
                "def format_note(title):\n    # твой код\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "format_note('Список дел')",
                        "expected": "Заметка: Список дел",
                    }
                ],
                "Перед записью в файл полезно подготовить текст в отдельной функции.",
                "Верни f-строку с префиксом «Заметка: ».",
            ),
        ],
    ),
    lesson(
        "exceptions",
        "realworld",
        11,
        "Исключения",
        "Делаем программу устойчивой",
        13,
        40,
        [
            theory(
                "Исключение — сигнал",
                "Например, int('кот') вызывает ValueError: строку нельзя превратить в число.",
                "number = int('42')",
            ),
            theory(
                "try/except обрабатывает ожидаемое",
                "В try помещают рискованный код, а в except — понятный запасной сценарий.",
                "try:\n    age = int('не число')\nexcept ValueError:\n    print('Нужны цифры')",
                "Лови конкретные ошибки, чтобы не скрыть настоящий баг.",
            ),
            theory(
                "Проверка до ошибки",
                "Граничные случаи часто понятнее проверить заранее, чем использовать исключение.",
                "if text.strip():\n    print('Есть текст')",
            ),
        ],
        [
            choice(
                "except-error",
                "Какую ошибку вызовет `int('abc')`?",
                ["TypeError", "ValueError", "KeyError"],
                "ValueError",
                "Тип данных подходит, но само значение невозможно преобразовать в число — ValueError.",
            ),
            text(
                "try-keyword",
                "Какое ключевое слово начинает блок, где может возникнуть ошибка?",
                ["try"],
                "Рискованная операция начинается внутри try.",
            ),
            code(
                "exception-code",
                "Напиши `safe_divide(left, right)`. При right = 0 верни `Нельзя делить на ноль`, иначе — частное.",
                "def safe_divide(left, right):\n    # твой код\n    pass\n",
                [
                    {"kind": "call", "call": "safe_divide(8, 2)", "expected": 4.0},
                    {
                        "kind": "call",
                        "call": "safe_divide(8, 0)",
                        "expected": "Нельзя делить на ноль",
                    },
                ],
                "Проверка граничного случая до деления делает поведение функции понятным.",
                "Сначала проверь right == 0, иначе выполни left / right.",
            ),
        ],
    ),
    lesson(
        "classes",
        "realworld",
        12,
        "Классы и объекты",
        "Описываем собственные сущности",
        15,
        45,
        [
            theory(
                "Класс — чертёж",
                "Класс описывает общие данные и действия. Объект — конкретный экземпляр этого чертежа.",
                "class Player:\n    pass\n\nhero = Player()",
            ),
            theory(
                "__init__ задаёт состояние",
                "Метод __init__ запускается при создании объекта. self — это сам объект.",
                "class Player:\n    def __init__(self, name):\n        self.name = name",
            ),
            theory(
                "Методы описывают поведение",
                "Метод получает self первым параметром и может обращаться к данным объекта.",
                "class Player:\n    def level_up(self):\n        self.level += 1",
            ),
        ],
        [
            choice(
                "class-blueprint",
                "Что точнее всего описывает класс?",
                ["Конкретный объект", "Чертёж для объектов", "Цикл"],
                "Чертёж для объектов",
                "По одному классу можно создать много объектов с разными данными.",
            ),
            text(
                "class-init",
                "Как называется метод, который запускается при создании объекта?",
                ["__init__", "init"],
                "__init__ задаёт начальное состояние объекта.",
            ),
            code(
                "class-code",
                "Создай класс `Badge` с методом `label(self, name)`, возвращающим `Награда: <name>`.",
                "class Badge:\n    def label(self, name):\n        # твой код\n        pass\n",
                [
                    {
                        "kind": "call",
                        "call": "Badge().label('Первые шаги')",
                        "expected": "Награда: Первые шаги",
                    }
                ],
                "Поздравляем! Теперь ты умеешь описывать собственные объекты.",
                "Метод должен вернуть f-строку. self уже передан первым параметром.",
            ),
        ],
    ),
]


MODULES.extend(EXTRA_MODULES)
LESSONS.extend(EXTRA_LESSONS)


EXAMS = {
    "start": {
        "title": "Мини-экзамен: основы",
        "description": "Проверь, уверенно ли ты пишешь первые программы.",
        "question_ids": ["hello-print", "var-type", "input-type", "var-code"],
    },
    "logic": {
        "title": "Мини-экзамен: логика",
        "description": "Условия и циклы в одном коротком забеге.",
        "question_ids": ["if-equality", "for-range", "while-infinite", "for-code"],
    },
    "structures": {
        "title": "Мини-экзамен: структуры",
        "description": "Функции, списки и словари — твой новый инструментарий.",
        "question_ids": ["func-return", "list-index", "dict-key", "dict-code"],
    },
    "realworld": {
        "title": "Финальный экзамен",
        "description": "Закрепи навыки, которые используют в реальных программах.",
        "question_ids": [
            "file-mode",
            "except-error",
            "class-blueprint",
            "exception-code",
            "class-code",
        ],
    },
    **EXTRA_EXAMS,
}

LESSON_BY_ID = {item["id"]: item for item in LESSONS}
QUESTION_BY_ID = {question["id"]: question for item in LESSONS for question in item["questions"]}


def public_question(question: dict) -> dict:
    return {
        key: value for key, value in question.items() if key not in {"answer", "answers", "tests"}
    }


def public_lesson(item: dict, include_questions: bool = False) -> dict:
    output = {key: value for key, value in item.items() if key not in {"questions", "theory"}}
    if include_questions:
        output["theory"] = item["theory"]
        output["questions"] = [public_question(question) for question in item["questions"]]
    return output
