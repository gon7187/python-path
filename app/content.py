"""Русский учебный план: мягкий старт, практика и контрольные точки."""

from __future__ import annotations

import ast
import hashlib
from copy import deepcopy

from app.exam_transfer import EXAM_TRANSFER_TESTS
from app.extended_curriculum import EXTRA_EXAMS, EXTRA_LESSONS, EXTRA_MODULES
from app.foundation_expansion import (
    FOUNDATION_CHALLENGES,
    FOUNDATION_INSERTIONS,
    FOUNDATION_REPLACEMENTS,
)
from app.gentle_start import GENTLE_START_EXAMS, GENTLE_START_LESSONS, GENTLE_START_MODULES
from app.learning_design import enrich_curriculum, public_tool_help


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
    question_id: str,
    prompt: str,
    starter: str,
    tests: list[dict],
    explanation: str,
    hint: str,
    test_inputs: list[str] | None = None,
) -> dict:
    question = {
        "id": question_id,
        "kind": "code",
        "prompt": prompt,
        "starter": starter,
        "tests": tests,
        "explanation": explanation,
        "hint": hint,
    }
    if test_inputs:
        question["test_inputs"] = test_inputs
        question["input_example"] = test_inputs
    return question


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
    *GENTLE_START_MODULES,
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
    *GENTLE_START_LESSONS,
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
                ["только строка 'Привет'", "print('Привет')", "переменная с текстом"],
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
                "Мы уже встречали целые числа int, текст str и логические значения bool. Здесь связываем их с переменными.",
                "age = 18\nname = 'Маша'\nis_ready = True",
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
                "Повторяем знакомое преобразование",
                "Чтобы получить целое число из ввода, оберни input в уже изученный int().",
                "age = int(input('Твой возраст: '))\nprint(age + 1)",
                "Преобразовывай в число, только когда ожидаешь цифры.",
            ),
            theory(
                "Собираем ответ через f-строку",
                "Полученный текст можно сразу подставить в уже знакомую f-строку и показать человеку.",
                "city = input('Город: ')\nprint(f'Ты из города {city}')",
            ),
        ],
        [
            choice(
                "input-type",
                "Какой тип вернёт `input()` без преобразования?",
                ["число", "str", "команда"],
                "str",
                "Даже введённое 42 сначала будет строкой '42'.",
            ),
            text("string-len", "Чему равно `len('кот')`?", ["3"], "В слове «кот» три символа."),
            code(
                "string-code",
                "Спроси имя через `input('Имя: ')` и выведи `Привет, <имя>!`.",
                "name = input('Имя: ')\n# выведи приветствие с name\n",
                [{"kind": "stdout", "expected": "Имя: Лена\nПривет, Лена!"}],
                "input() вернул текст, и он подставился в приветствие.",
                "Используй print(f'Привет, {name}!').",
                ["Лена"],
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
                "Измени возраст на 18, чтобы программа вывела `Доступ открыт`.",
                "age = 17\nif age >= 18:\n    print('Доступ открыт')\nelse:\n    print('Доступ закрыт')\n",
                [{"kind": "stdout", "expected": "Доступ открыт"}],
                "Изменив значение age, ты увидел, как условие выбирает другую ветку.",
                "Сейчас age = 17. Замени только число на 18.",
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
                "Измени верхнюю границу, чтобы цикл сложил числа от 1 до 5 и вывел `15`.",
                "total = 0\nfor number in range(1, 4):\n    total += number\nprint(total)\n",
                [{"kind": "stdout", "expected": "15"}],
                "Цикл избавляет от ручного сложения каждого числа.",
                "Верхняя граница range не включается: замени 4 на 6.",
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
                "Измени стартовое число, чтобы цикл вывел 3, 2, 1.",
                "count = 1\nwhile count > 0:\n    print(count)\n    count -= 1\n",
                [{"kind": "stdout", "expected": "3\n2\n1"}],
                "while хорош, когда счётчик меняется до достижения границы.",
                "Измени только первую строку: count должен начинаться с 3.",
            ),
        ],
    ),
    lesson(
        "functions",
        "structures",
        7,
        "Функция: первый запуск",
        "Даём знакомому действию имя",
        6,
        35,
        [
            theory(
                "Функция — это команда, которой дали имя",
                "Если одно действие понадобится несколько раз, его можно записать под понятным именем. Пока функция ничего не получает снаружи — она просто выполняет знакомую команду print.",
                "def say_hello():\n    print('Привет!')",
            ),
            theory(
                "Сначала создаём, потом вызываем",
                "Строки после def только создают функцию. Чтобы она сработала, нужно отдельно написать её имя со скобками.",
                "def say_hello():\n    print('Привет!')\n\nsay_hello()",
            ),
            theory(
                "Отступ показывает, что находится внутри",
                "Строка с четырьмя пробелами после def — тело функции. Сейчас запомни только форму: def, имя, скобки, двоеточие и отступ.",
                "def say_hello():\n    print('Привет!')",
                "Не пытайся запомнить всё: в этой задаче нужно лишь вызвать уже готовую функцию.",
            ),
        ],
        [
            choice(
                "func-definition",
                "Какая строка создаёт функцию с именем say_hello?",
                ["say_hello()", "def say_hello():", "print('say_hello')"],
                "def say_hello():",
                "def начинает создание функции, затем идут имя, скобки и двоеточие.",
            ),
            text(
                "func-first-call",
                "Как записать вызов функции `say_hello`?",
                ["say_hello()"],
                "Функцию запускают её именем и круглыми скобками: say_hello().",
            ),
            code(
                "func-first-code",
                "Запусти готовую функцию: добавь внизу `say_hello()`.",
                "def say_hello():\n    print('Привет!')\n\n# вызови функцию здесь\n",
                [{"kind": "stdout", "expected": "Привет!"}],
                "Функция уже создана. Последняя строка с её вызовом запустит print внутри функции.",
                "На новой строке после комментария напиши только say_hello().",
            ),
        ],
    ),
    lesson(
        "functions-parameters",
        "structures",
        8,
        "Функция с параметром",
        "Передаём функции одно значение",
        7,
        35,
        [
            theory(
                "Параметр — пустое место внутри функции",
                "Имя в скобках после названия функции называется параметром. Когда функция запустится, параметр получит значение, которое мы ей передали.",
                "def greet(name):\n    print('Привет, ' + name)",
            ),
            theory(
                "Аргумент заполняет параметр",
                "В вызове мы передаём аргумент. В примере строка 'Аня' попадает в параметр name.",
                "greet('Аня')  # name станет 'Аня'",
            ),
            theory(
                "Одна функция — разные значения",
                "Форма функции не меняется. Меняем только аргумент при вызове — и получаем другое приветствие.",
                "greet('Аня')\ngreet('Илья')",
            ),
        ],
        [
            choice(
                "func-parameter",
                "Как называется name в строке `def greet(name):`?",
                ["Параметр", "Аргумент", "Комментарий"],
                "Параметр",
                "Параметр стоит в определении функции и ждёт значение.",
            ),
            text(
                "func-argument",
                "Что передаётся в параметр name при вызове `greet('Аня')`?",
                ["Аня", "'Аня'"],
                "Аргумент 'Аня' становится значением параметра name внутри функции.",
            ),
            code(
                "func-parameter-code",
                "Вызови готовую функцию с именем `Аня`, чтобы она вывела приветствие.",
                "def greet(name):\n    print('Привет, ' + name)\n\n# вызови greet с именем Аня\n",
                [{"kind": "stdout", "expected": "Привет, Аня"}],
                "Функция уже умеет печатать текст. Нужно передать ей одно значение в скобках.",
                "После комментария напиши greet('Аня').",
            ),
        ],
    ),
    lesson(
        "functions-return",
        "structures",
        9,
        "Функция возвращает результат",
        "Отличаем return от print",
        7,
        35,
        [
            theory(
                "print показывает, return отдаёт",
                "print показывает значение на экране. return передаёт его обратно в программу: результат можно сохранить, посчитать или напечатать позже.",
                "def double(number):\n    return number * 2",
            ),
            theory(
                "Вызов можно поставить внутрь print",
                "Сначала Python вызывает функцию и получает результат от return. Затем print показывает этот результат человеку.",
                "print(double(3))  # 6",
            ),
            theory(
                "Начинаем с готового примера",
                "В этой практике не нужно писать return самому. Измени одно число и посмотри, как готовая функция возвращает новый результат.",
                "def double(number):\n    return number * 2\n\nprint(double(3))",
            ),
        ],
        [
            choice(
                "func-return",
                "Что позволяет использовать результат функции в следующем вычислении?",
                ["print", "return", "def"],
                "return",
                "return передаёт значение туда, где функцию вызвали.",
            ),
            text(
                "func-call",
                "Что выведет `print(double(3))`, если `double` возвращает number * 2?",
                ["6"],
                "Функция возвращает 3 * 2, а print показывает 6.",
            ),
            code(
                "func-return-code",
                "Измени 3 на 4, чтобы программа вывела `8`.",
                "def double(number):\n    return number * 2\n\nprint(double(3))\n",
                [{"kind": "stdout", "expected": "8"}],
                "Форма функции уже готова. Достаточно передать в неё другое число.",
                "Замени только 3 внутри двойных скобок на 4.",
            ),
        ],
    ),
    lesson(
        "functions-greeting",
        "structures",
        10,
        "Собираем приветствие",
        "Параметр, return и знакомая f-строка",
        8,
        35,
        [
            theory(
                "Собираем знакомые детали",
                "Здесь нет новой магии: параметр name ты уже видел, return уже возвращал число, а f-строка уже подставляла переменную в текст.",
                "def greeting(name):\n    return f'Привет, {name}!'",
            ),
            theory(
                "Сначала верни текст",
                "Внутри функции после return стоит готовое выражение. Его не нужно оборачивать в print: тест сам вызовет функцию и проверит то, что она вернула.",
                "return f'Привет, {name}!'",
            ),
            theory(
                "Проверь себя на двух именах",
                "Одна и та же функция должна работать с любым переданным именем. Поэтому проверка использует не один, а два примера.",
                "greeting('Аня')  # Привет, Аня!\ngreeting('Илья')  # Привет, Илья!",
            ),
        ],
        [
            choice(
                "func-greeting-piece",
                "Что нужно поставить перед строкой, чтобы `{name}` подставилось в текст?",
                ["f", "def", "return"],
                "f",
                "Буква f перед кавычкой включает подстановку значения из фигурных скобок.",
            ),
            text(
                "func-greeting-result",
                "Что вернёт `greeting('Аня')`?",
                ["Привет, Аня!"],
                "Параметр name получил значение Аня и подставился в f-строку.",
            ),
            code(
                "func-code",
                "Заполни одну строку: верни приветствие для переданного name.",
                "def greeting(name):\n    return ''\n",
                [
                    {"kind": "call", "call": "greeting('Аня')", "expected": "Привет, Аня!"},
                    {"kind": "call", "call": "greeting('Илья')", "expected": "Привет, Илья!"},
                ],
                "Все части уже знакомы: верни f-строку, в которой {name} стоит внутри текста.",
                "Замени пустую строку после return на f'Привет, {name}!'.",
            ),
        ],
    ),
    lesson(
        "lists",
        "structures",
        11,
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
                "Выведи последний элемент списка — `вода`.",
                "items = ['чай', 'кофе', 'вода']\n# напечатай последний элемент\n",
                [{"kind": "stdout", "expected": "вода"}],
                "Отрицательный индекс достаёт последний элемент независимо от длины списка.",
                "Используй print(items[-1]).",
            ),
        ],
    ),
    lesson(
        "dicts-sets",
        "structures",
        12,
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
                "Выведи уровень из словаря, а если его нет — число `1`.",
                "profile = {'name': 'Аня'}\n# напечатай level или 1\n",
                [{"kind": "stdout", "expected": "1"}],
                "get позволяет задать понятное значение по умолчанию.",
                "Используй print(profile.get('level', 1)).",
            ),
        ],
    ),
    lesson(
        "files",
        "realworld",
        13,
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
                "def format_note(title):\n    # верни текст заметки здесь\n    return ''\n",
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
        14,
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
                "Добавь обработчик ValueError, чтобы вместо ошибки появилось `Нужны цифры`.",
                "try:\n    number = int('кот')\n    print(number)\n# добавь except ниже\n",
                [{"kind": "stdout", "expected": "Нужны цифры"}],
                "int('кот') вызывает ValueError. В except можно показать человеку понятное сообщение.",
                "Добавь две строки: except ValueError: и с отступом print('Нужны цифры').",
            ),
        ],
    ),
    lesson(
        "classes",
        "realworld",
        15,
        "Классы и объекты",
        "Описываем собственные сущности",
        15,
        45,
        [
            theory(
                "Класс — чертёж",
                "Класс описывает общие данные и действия. Объект — конкретный экземпляр этого чертежа.",
                "class Player:\n    role = 'игрок'\n\nhero = Player()",
            ),
            theory(
                "Создаём объект по чертежу",
                "После `Badge()` появляется конкретный объект. Его можно сохранить в переменную и обратиться к данным через точку.",
                "badge = Badge()\nprint(badge.title)",
            ),
            theory(
                "Сначала только одно свойство",
                "Пока не добавляем __init__, self и методы. Достаточно положить один общий текст title в класс и прочитать его у объекта.",
                "class Badge:\n    title = 'Первые шаги'",
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
                "Как называется переменная, в которой лежит созданный объект в примере `badge = Badge()`?",
                ["badge"],
                "Badge() создаёт объект, а badge сохраняет его для дальнейшей работы.",
            ),
            code(
                "class-code",
                "Измени title на `Первые шаги`, чтобы объект вывел это название.",
                "class Badge:\n    title = 'Награда'\n\nbadge = Badge()\nprint(badge.title)\n",
                [{"kind": "stdout", "expected": "Первые шаги"}],
                "Класс и объект уже готовы. В этой задаче меняется только текст свойства title.",
                "Замени только слово Награда в кавычках на Первые шаги.",
            ),
        ],
    ),
]


def apply_foundation_expansion() -> None:
    """Split overloaded topics into one-concept steps while preserving old lesson IDs."""
    by_id = {item["id"]: item for item in LESSONS}
    for lesson_id, replacement in FOUNDATION_REPLACEMENTS.items():
        by_id[lesson_id].update(replacement)
    for anchor_id, new_lesson in FOUNDATION_INSERTIONS:
        anchor_index = next(index for index, item in enumerate(LESSONS) if item["id"] == anchor_id)
        LESSONS.insert(anchor_index + 1, new_lesson)
    by_id = {item["id"]: item for item in LESSONS}
    for lesson_id, challenge in FOUNDATION_CHALLENGES.items():
        by_id[lesson_id]["questions"].append(challenge)


apply_foundation_expansion()

MODULES.extend(EXTRA_MODULES)
LESSONS.extend(EXTRA_LESSONS)


def default_guide(question: dict) -> str:
    """Даёт опору до ответа, а не только объяснение после ошибки."""
    kind = question["kind"]
    if kind == "code":
        return (
            "Работай маленькими шагами: 1) назови вход и ожидаемый результат; "
            "2) измени только один ближайший шаг; 3) запусти код; 4) сравни результат "
            "с условием. Точную форму забытой функции можно открыть в справочнике."
        )
    if kind == "input":
        return "Ответ короткий. Найди ключевое слово или результат в примере выше и введи его без лишнего текста."
    return "Сначала вспомни пример из объяснения. Затем исключи варианты, которые не относятся к правилу урока."


def add_learning_scaffolds() -> None:
    """Добавляет повторяемый педагогический шаг ко всем урокам курса."""
    for item in LESSONS:
        practice_card = theory(
            "Перед практикой: не нужно угадывать",
            "Посмотри на пример ещё раз. Выполняй задание по одному действию и проверяй код отдельно. Ошибка — это подсказка, а не оценка твоих способностей.",
            "1. Прочитай задание\n2. Предскажи результат\n3. Измени один шаг\n4. Запусти и сравни",
            "Если застрял, открой подсказку и измени в примере только одну часть.",
        )
        practice_card["language"] = "text"
        item["theory"].append(practice_card)
        for question in item["questions"]:
            question.setdefault("guide", default_guide(question))


add_learning_scaffolds()
enrich_curriculum(LESSONS)
for lesson_order, item in enumerate(LESSONS, start=1):
    item["order"] = lesson_order


EXAMS = {
    **deepcopy(GENTLE_START_EXAMS),
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
    **deepcopy(EXTRA_EXAMS),
}


def strengthen_foundation_exams() -> None:
    """Make every early exam mixed and impossible to pass without writing code."""
    for module in MODULES:
        exam = EXAMS[module["id"]]
        if exam.get("mandatory_question_ids"):
            continue
        module_questions = [
            question
            for item in LESSONS
            if item["module_id"] == module["id"]
            for question in item["questions"]
        ]
        by_kind = {
            kind: [question for question in module_questions if question["kind"] == kind]
            for kind in ("choice", "input", "code")
        }
        proposed = [
            by_kind["choice"][0],
            by_kind["input"][len(by_kind["input"]) // 2],
            by_kind["code"][len(by_kind["code"]) // 3],
            by_kind["choice"][-1],
            by_kind["input"][-1],
            by_kind["code"][-1],
        ]
        selected = list(dict.fromkeys(question["id"] for question in proposed))
        selected.extend(
            question["id"]
            for question in module_questions
            if question["id"] not in selected and len(selected) < 6
        )
        exam["question_ids"] = selected
        exam["mandatory_question_ids"] = [
            question_id
            for question_id in selected
            if next(question for question in module_questions if question["id"] == question_id)[
                "kind"
            ]
            == "code"
        ]
        exam["description"] += (
            " Здесь смешаны воспроизведение, понимание и обязательный код по всему разделу."
        )


strengthen_foundation_exams()

LESSON_BY_ID = {item["id"]: item for item in LESSONS}
LESSON_QUESTION_BY_ID = {
    question["id"]: question for item in LESSONS for question in item["questions"]
}
LESSON_ID_BY_QUESTION_ID = {
    question["id"]: item["id"] for item in LESSONS for question in item["questions"]
}
EXAM_QUESTIONS: dict[str, dict] = {}
EXAM_SOURCE_QUESTION_ID: dict[str, str] = {}
EXAM_QUESTION_LESSON_ID: dict[str, str] = {}
EXAM_MODULE_BY_QUESTION_ID: dict[str, str] = {}


def _exam_starter(source_id: str, starter: str) -> str:
    """Убрать учебные комментарии, оставив валидный каркас и сигнатуры."""
    if source_id == "exception-code":
        return (
            "try:\n"
            "    number = int('кот')\n"
            "    print(number)\n"
            "except ValueError:\n"
            "    print('Замени этот текст')\n"
        )
    lines = [line for line in starter.splitlines() if not line.lstrip().startswith("#")]
    candidate = "\n".join(lines).rstrip() + "\n"
    try:
        ast.parse(candidate)
    except SyntaxError:
        return starter
    return candidate


EXAM_INPUT_CUES: dict[str, dict[str, object]] = {
    "class-init": {
        "prompt": (
            "Какое короткое английское имя переменной подходит объекту-награде, если "
            "имя должно означать «значок»? Введи только имя."
        )
    },
    "tuples-slices-unpacking-term": {
        "prompt": (
            "Как называется приём, когда `first, second = values` одним присваиванием "
            "забирает элементы последовательности в несколько переменных?"
        )
    },
    "flow-advanced-match-term": {
        "prompt": (
            "Какое ключевое слово начинает сопоставление одного значения с несколькими "
            "шаблонами `case`?"
        )
    },
    "errors-debug-raise-term": {
        "prompt": (
            "Какое ключевое слово вручную создаёт исключение, если данные не прошли проверку?"
        )
    },
    "oop-design-repr-str-term": {
        "prompt": (
            "Какой dunder-метод должен вернуть техническое представление объекта для разработчика?"
        )
    },
    "stdlib-productivity-itertools-term": {
        "prompt": (
            "Как называется модуль стандартной библиотеки с ленивыми комбинациями, "
            "цепочками и бесконечными итераторами?"
        )
    },
    "quality-format-lint-term": {
        "prompt": (
            "Как называется инструмент, который без запуска программы сообщает о "
            "подозрительных местах и нарушениях стиля в коде?"
        )
    },
    "http-api-json-api-term": {
        "prompt": (
            "Как называется текстовый формат обмена данными с объектами, массивами, "
            "строками, числами и булевыми значениями, который часто использует API?"
        )
    },
    "databases-crud-term": {
        "prompt": (
            "Какая английская аббревиатура объединяет создание, чтение, изменение и "
            "удаление записей?"
        )
    },
}


def build_exam_variants() -> None:
    """Создать отдельные assessment-карточки вместо повторной выдачи уроковых ID."""
    for module_id, exam in EXAMS.items():
        source_ids = list(exam["question_ids"])
        source_mandatory = set(exam.get("mandatory_question_ids", ()))
        variant_ids: list[str] = []
        mandatory_variant_ids: list[str] = []

        for source_id in source_ids:
            source = LESSON_QUESTION_BY_ID[source_id]
            variant = deepcopy(source)
            variant_id = f"exam-{module_id}-{source_id}"
            variant["id"] = variant_id
            variant["prompt"] = f"Контрольный перенос. {source['prompt']}"
            variant["purpose"] = "exam_retrieval"
            variant["scaffold_level"] = "assessment"
            variant["scaffold"] = "assessment"
            variant["badge"] = "🏁 Контрольный перенос"
            variant["review_concepts"] = list(source.get("review_concepts", ()))
            variant["retrieves"] = list(source.get("retrieves", ()))
            variant.pop("hint", None)
            if variant["kind"] == "choice":
                variant["prompt"] = (
                    "Контрольное применение. "
                    f"{source['prompt']} Выбери ответ и объясни себе, почему остальные "
                    "варианты не подходят."
                )
            elif variant["kind"] == "input":
                cue = EXAM_INPUT_CUES.get(source_id, {})
                variant["prompt"] = (
                    "Контрольное воспроизведение без списка вариантов. "
                    f"{cue.get('prompt', source['prompt'])}"
                )
                if "answers" in cue:
                    variant["answers"] = deepcopy(cue["answers"])
            elif variant["kind"] == "parsons":
                source_blocks = {block["id"]: block["text"] for block in source["blocks"]}
                ordered_texts = [source_blocks[block_id] for block_id in source["answer"]]
                ordered_blocks = [
                    {
                        "id": (
                            f"{variant_id}-block-h"
                            + hashlib.sha256(f"{variant_id}\0{text}\0{index}".encode()).hexdigest()[
                                :12
                            ]
                        ),
                        "text": text,
                    }
                    for index, text in enumerate(ordered_texts)
                ]
                variant["answer"] = [block["id"] for block in ordered_blocks]
                variant["blocks"] = sorted(
                    ordered_blocks,
                    key=lambda block: hashlib.sha256(
                        f"{variant_id}\0exam-scramble\0{block['id']}".encode()
                    ).hexdigest(),
                )
                if variant["blocks"] == ordered_blocks:
                    variant["blocks"] = list(reversed(ordered_blocks))
            if variant["kind"] == "code":
                variant["purpose"] = "exam_transfer"
                # На экзамене оцениваем поведение, а не совпадение с авторской
                # формой решения. Сохраняем поведенческие lesson-сценарии,
                # отбрасываем проверки исходного текста/AST и добавляем новый
                # transfer-сценарий, которого ученик раньше не видел.
                variant["tests"] = [
                    deepcopy(test)
                    for test in source["tests"]
                    if test.get("kind") not in {"source", "ast"}
                ] + deepcopy(EXAM_TRANSFER_TESTS[source_id])
                variant["starter"] = _exam_starter(source_id, variant["starter"])
                variant["guide"] = (
                    "Сначала восстанови алгоритм без почти готового ответа. Раздели вход, "
                    "преобразование и результат; затем проверь решение на другом мысленном входе."
                )
                variant["hints"] = [
                    "Назови три шага решения своими словами и реализуй только первый из них.",
                    "Если забыл точное имя уже изученной функции или метода, открой справочник "
                    "инструментов; готового решения в экзамене нет.",
                ]

            EXAM_QUESTIONS[variant_id] = variant
            EXAM_SOURCE_QUESTION_ID[variant_id] = source_id
            EXAM_QUESTION_LESSON_ID[variant_id] = LESSON_ID_BY_QUESTION_ID[source_id]
            EXAM_MODULE_BY_QUESTION_ID[variant_id] = module_id
            variant_ids.append(variant_id)
            if source_id in source_mandatory:
                mandatory_variant_ids.append(variant_id)

        exam["source_question_ids"] = source_ids
        exam["source_mandatory_question_ids"] = [
            source_id for source_id in source_ids if source_id in source_mandatory
        ]
        exam["question_ids"] = variant_ids
        exam["mandatory_question_ids"] = mandatory_variant_ids


build_exam_variants()

QUESTION_BY_ID = {**LESSON_QUESTION_BY_ID, **EXAM_QUESTIONS}


def public_question(question: dict) -> dict:
    output = {
        key: value
        for key, value in question.items()
        if key
        not in {
            "answer",
            "answers",
            "explanation",
            "hint",
            "source_question_id",
            "reference_solution",
            "required_tokens",
            "solution",
            "tests",
            "test_inputs",
            "tool_ids",
            "tool_help",
        }
    }
    # В recognition/free-recall/Parsons справочник часто буквально содержит ответ.
    # При написании кода он остаётся доступным как честная документация по уже изученным API.
    output["tool_help"] = (
        public_tool_help(question.get("tool_help", ())) if question["kind"] == "code" else []
    )
    return output


def public_lesson(item: dict, include_questions: bool = False) -> dict:
    output = {key: value for key, value in item.items() if key not in {"questions", "theory"}}
    if include_questions:
        output["theory"] = item["theory"]
        output["questions"] = [public_question(question) for question in item["questions"]]
    return output
