"""Human-first rules and automated checks for the learning sequence.

The content files stay intentionally simple dictionaries.  This module adds the
pedagogical metadata used by practice selection and provides a small curriculum
linter.  The linter is deliberately independent from FastAPI so CI can import it
without starting the application or touching the learner database.
"""

from __future__ import annotations

import ast
import re
import textwrap
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
    "operator:multiply": "warmup-numbers",
    "operator:division": "warmup-numbers",
    "operator:floor-division": "operators-integer-division",
    "operator:modulo": "operators-integer-division",
    "operator:and": "operators-booleans",
    "operator:or": "operators-booleans",
    "operator:not": "operators-booleans",
    "syntax:f-string": "warmup-fstring",
    "syntax:f-string-format": "strings-pro-formatting",
    "syntax:boolean": "warmup-boolean",
    "syntax:comparison": "warmup-compare",
    # Отдельного урока пока нет: любое появление должно остановить аудит,
    # а не незаметно научить форме ``x if condition else y``.
    "syntax:conditional-expression": "flow-advanced-conditional-expression",
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
    "syntax:slice": "strings-pro-indexes",
    "syntax:slice-step": "tuples-slices-slices",
    "syntax:tuple": "tuples-slices-tuples",
    "syntax:unpacking": "tuples-slices-unpacking",
    "value:none": "functions-return",
    "call:list": "lists",
    "method:append": "lists-append",
    "call:append": "lists-append",
    "method:extend": "lists-pro-list-methods",
    "method:insert": "lists-pro-list-methods",
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
    "method:sort": "lists-pro-list-methods",
    "syntax:elif": "flow-advanced-elif",
    "syntax:continue": "flow-advanced-break-continue",
    "syntax:loop-else": "flow-advanced-loop-else",
    "syntax:match": "flow-advanced-match",
    "syntax:default-parameter": "functions-pro-defaults",
    "syntax:keyword-argument": "functions-keyword-arguments",
    "call:connect": "functions-pro-keyword-args",
    "syntax:vararg": "functions-pro-varargs",
    "syntax:lambda": "scope-lambda-key",
    "syntax:list-comprehension": "comprehensions-list-comprehension",
    "syntax:comprehension-filter": "comprehensions-comprehension-filter",
    "syntax:dict-comprehension": "comprehensions-dict-comprehension",
    "syntax:generator-expression": "iterators-generator-expression",
    "call:iter": "iterators-iterable",
    "call:next": "iterators-iterable",
    "syntax:yield": "iterators-yield",
    "syntax:import": "modules-imports",
    "syntax:from-import": "modules-imports",
    "method:sqrt": "modules-imports",
    "call:sqrt": "modules-imports",
    "call:Path": "modules-stdlib-imports",
    "call:main": "modules-main-guard",
    "syntax:raise": "errors-debug-raise",
    "call:ValueError": "exceptions",
    "call:repr": "oop-design-repr-str",
    "method:__init__": "oop-design-init",
    "call:super": "oop-advanced-inheritance",
    "syntax:decorator": "oop-advanced-properties",
    "syntax:type-annotation": "typing-models-annotations",
    "syntax:assert": "testing-unit-tests",
    "call:timedelta": "stdlib-core-datetime",
    "method:choice": "stdlib-core-random",
    "method:mean": "stdlib-core-math-statistics",
    "call:Decimal": "stdlib-core-decimal",
    "call:Counter": "stdlib-productivity-collections",
    "method:combinations": "stdlib-productivity-itertools",
    "method:heappush": "stdlib-productivity-heapq-bisect",
    "method:fullmatch": "regex-patterns",
    "method:sub": "regex-substitution",
    "call:make_user": "testing-fixtures",
    "method:level_up": "testing-fixtures",
    "call:FakeClock": "testing-mocks",
    "method:execute": "databases-parameters",
    "call:ThreadPoolExecutor": "concurrency-thread-pool",
    "method:map": "concurrency-thread-pool",
    "method:put": "concurrency-queues",
    "call:Queue": "concurrency-queues",
    "method:empty": "concurrency-queues",
    "method:dump": "files-data-json",
    "method:load": "files-data-json",
    "method:dumps": "files-data-json",
    "syntax:async": "async-coroutines",
    "syntax:await": "async-coroutines",
    "method:sleep": "async-coroutines",
    "method:create_task": "async-tasks",
    "method:gather": "async-gather-timeouts",
    "method:run": "async-coroutines",
    "syntax:starred-unpacking": "functions-pro-varargs",
    "call:Task": "capstones-task-manager",
}

# sort() is already contrasted with sorted() in the dedicated sorting lesson;
# lambda/key later builds on it rather than introducing it.
FEATURE_INTRODUCTIONS["call:Task"] = "oop-design-init"
FEATURE_INTRODUCTIONS.update(
    {
        "call:Lock": "concurrency-locks",
        "call:dict": "dicts-sets",
        "call:lru_cache": "stdlib-productivity-functools",
        "method:ArgumentParser": "cli-environment-argv",
        "method:Random": "stdlib-core-random",
        "method:add_argument": "cli-environment-argv",
        "method:as_posix": "modules-stdlib-imports",
        "method:copy": "typing-models-generic-collections",
        "method:connect": "databases-parameters",
        "method:fetchone": "databases-parameters",
        "method:fromisoformat": "stdlib-core-datetime",
        "method:group": "regex-groups",
        "method:heappop": "stdlib-productivity-heapq-bisect",
        "method:isoformat": "stdlib-core-datetime",
        "method:loads": "files-data-json",
        "method:parse_args": "cli-environment-argv",
        "method:reader": "files-data-csv",
        "method:upper": "http-api-request-response",
    }
)


# The browser receives only the learner-facing fields from these entries.
# Internal ids keep curriculum authoring explicit: a task says which already
# taught tools it needs instead of trying to reverse-engineer a solution from
# hidden tests.
TOOL_CATALOG: dict[str, dict[str, str]] = {
    "print": {
        "name": "print()",
        "kind": "Встроенная функция",
        "signature": "print(value)",
        "description": "Показывает значение в консоли. Можно передать текст, число или переменную.",
        "example": "print('Привет')  # Привет",
        "introduced_in": "warmup-route",
    },
    "string": {
        "name": "Строка",
        "kind": "Тип данных",
        "signature": "'текст'",
        "description": "Хранит текст. Кавычки обозначают границы строки и не попадают в её значение.",
        "example": "'Тула'",
        "introduced_in": "warmup-text",
    },
    "comment": {
        "name": "# комментарий",
        "kind": "Синтаксис",
        "signature": "# пояснение для человека",
        "description": "Python пропускает текст после # до конца строки: это заметка, а не команда.",
        "example": "# показываем готовность\nprint('Готово')",
        "introduced_in": "warmup-read-code",
    },
    "assignment": {
        "name": "=",
        "kind": "Присваивание",
        "signature": "name = value",
        "description": "Сохраняет значение под именем переменной. Справа вычисляется значение, слева указывается имя.",
        "example": "score = 5",
        "introduced_in": "warmup-variables",
    },
    "arithmetic": {
        "name": "+  −  *  /",
        "kind": "Арифметические операторы",
        "signature": "left + right",
        "description": "Создают новое число: + складывает, − вычитает, * умножает, / делит.",
        "example": "total = price * count",
        "introduced_in": "warmup-numbers",
    },
    "multiply": {
        "name": "*",
        "kind": "Оператор умножения",
        "signature": "left * right",
        "description": "Умножает два числа и возвращает результат.",
        "example": "cost = 250 * 3  # 750",
        "introduced_in": "warmup-numbers",
    },
    "len": {
        "name": "len()",
        "kind": "Встроенная функция",
        "signature": "len(value)",
        "description": "Возвращает количество элементов: символов в строке, значений в списке или ключей в словаре.",
        "example": "len('python')  # 6",
        "introduced_in": "warmup-length",
    },
    "f-string": {
        "name": "f-строка",
        "kind": "Форматирование текста",
        "signature": "f'Текст {value}'",
        "description": "Подставляет значение выражения из фигурных скобок внутрь текста. Перед кавычкой нужна буква f.",
        "example": "name = 'Аня'\nmessage = f'Привет, {name}!'",
        "introduced_in": "warmup-fstring",
    },
    "input": {
        "name": "input()",
        "kind": "Встроенная функция",
        "signature": "input('Подсказка: ')",
        "description": "Показывает приглашение, ждёт ввод пользователя и всегда возвращает его как строку str.",
        "example": "name = input('Имя: ')",
        "introduced_in": "warmup-input",
    },
    "int": {
        "name": "int()",
        "kind": "Преобразование типа",
        "signature": "int(text)",
        "description": "Преобразует строку с целым числом в значение типа int, с которым можно считать.",
        "example": "age = int('18')  # 18",
        "introduced_in": "warmup-convert",
    },
    "bool": {
        "name": "True / False",
        "kind": "Булевы значения",
        "signature": "is_ready = True",
        "description": "Обозначают истину и ложь. Пишутся с заглавной буквы и без кавычек.",
        "example": "is_ready = True",
        "introduced_in": "warmup-boolean",
    },
    "comparison": {
        "name": "Операторы сравнения",
        "kind": "Синтаксис",
        "signature": "==  !=  <  <=  >  >=",
        "description": "Сравнивают значения и возвращают True или False. Равенство проверяется двумя знаками ==.",
        "example": "score >= 7  # не меньше семи",
        "introduced_in": "warmup-compare",
    },
    "indent": {
        "name": "Отступ",
        "kind": "Синтаксис",
        "signature": "четыре пробела перед вложенной строкой",
        "description": "Четыре пробела показывают, что строка принадлежит условию, циклу, функции или классу.",
        "example": "    print('строка внутри блока')",
        "introduced_in": "warmup-indent",
    },
    "name-error": {
        "name": "NameError",
        "kind": "Ошибка",
        "signature": "NameError: name 'city' is not defined",
        "description": "Означает, что Python встретил имя, которому ещё не присвоили значение, либо имя написано с ошибкой.",
        "example": "city = 'Тула'\nprint(city)",
        "introduced_in": "warmup-errors",
    },
    "lower": {
        "name": ".lower()",
        "kind": "Метод строки",
        "signature": "text.lower()",
        "description": "Возвращает новую строку в нижнем регистре. Исходную строку не изменяет.",
        "example": "'PyThOn'.lower()  # 'python'",
        "introduced_in": "warmup-methods",
    },
    "strip": {
        "name": ".strip()",
        "kind": "Метод строки",
        "signature": "text.strip()",
        "description": "Возвращает новую строку без пробелов и переносов в начале и конце. Символы внутри строки сохраняются.",
        "example": "'  Python  '.strip()  # 'Python'",
        "introduced_in": "strings-strip",
    },
    "if": {
        "name": "if",
        "kind": "Условие",
        "signature": "if condition:\n    action",
        "description": "Выполняет блок с отступом только тогда, когда условие равно True.",
        "example": "if age >= 18:\n    status = 'Вход разрешён'",
        "introduced_in": "conditions",
    },
    "else": {
        "name": "else",
        "kind": "Ветка условия",
        "signature": "else:\n    fallback",
        "description": "Выполняет запасную ветку, когда условие соответствующего if оказалось ложным.",
        "example": "if ready:\n    message = 'Старт'\nelse:\n    message = 'Ждём'",
        "introduced_in": "conditions-else",
    },
    "for": {
        "name": "for",
        "kind": "Цикл",
        "signature": "for item in items:\n    action",
        "description": "По очереди берёт каждый элемент последовательности и выполняет блок с отступом.",
        "example": "for name in names:\n    print(name)",
        "introduced_in": "for-loop",
    },
    "range": {
        "name": "range()",
        "kind": "Встроенная функция",
        "signature": "range(start, stop)",
        "description": "Создаёт последовательность целых чисел до stop, не включая саму правую границу.",
        "example": "range(1, 4)  # 1, 2, 3",
        "introduced_in": "for-loop",
    },
    "plus-equals": {
        "name": "+=",
        "kind": "Накопительное присваивание",
        "signature": "total += value",
        "description": "Прибавляет значение к текущему содержимому переменной и сохраняет новый результат обратно.",
        "example": "total = 0\ntotal += 3  # total теперь 3",
        "introduced_in": "for-accumulator",
    },
    "while": {
        "name": "while",
        "kind": "Цикл",
        "signature": "while condition:\n    action",
        "description": "Повторяет блок, пока условие остаётся истинным. Внутри обычно меняют значение, от которого зависит условие.",
        "example": "attempt = 0\nwhile attempt < 3:\n    attempt += 1",
        "introduced_in": "while-loop",
    },
    "break": {
        "name": "break",
        "kind": "Управление циклом",
        "signature": "if found:\n    break",
        "description": "Немедленно завершает ближайший цикл и продолжает выполнение после него.",
        "example": "for value in values:\n    if value == target:\n        break",
        "introduced_in": "while-break",
    },
    "def": {
        "name": "def",
        "kind": "Определение функции",
        "signature": "def function_name():\n    body",
        "description": "Создаёт функцию — именованный блок кода. Тело выполняется только после вызова функции.",
        "example": "def say_hello():\n    print('Привет')",
        "introduced_in": "functions",
    },
    "function-call": {
        "name": "Вызов функции",
        "kind": "Синтаксис",
        "signature": "function_name(arguments)",
        "description": "Запускает тело уже определённой функции. Скобки обязательны даже без аргументов.",
        "example": "say_hello()",
        "introduced_in": "functions",
    },
    "parameter": {
        "name": "Параметр и аргумент",
        "kind": "Функции",
        "signature": "def greet(name): ...\ngreet('Аня')",
        "description": "Параметр — имя внутри определения функции; аргумент — конкретное значение при вызове.",
        "example": "def double(number):\n    print(number * 2)\n\ndouble(4)",
        "introduced_in": "functions-parameters",
    },
    "return": {
        "name": "return",
        "kind": "Результат функции",
        "signature": "return value",
        "description": "Завершает функцию и отдаёт значение месту вызова. Это не то же самое, что показать значение через print().",
        "example": "def double(number):\n    return number * 2",
        "introduced_in": "functions-return",
    },
    "keyword-argument": {
        "name": "Именованный аргумент",
        "kind": "Вызов функции",
        "signature": "function(name=value)",
        "description": "Явно связывает переданное значение с параметром по имени, поэтому порядок таких аргументов понятнее.",
        "example": "greet(name='Аня', excited=True)",
        "introduced_in": "functions-keyword-arguments",
    },
    "list": {
        "name": "Список []",
        "kind": "Коллекция",
        "signature": "items = [first, second]",
        "description": "Хранит упорядоченный изменяемый набор значений. Индексы начинаются с нуля.",
        "example": "scores = [5, 4, 5]",
        "introduced_in": "lists",
    },
    "index": {
        "name": "Индекс []",
        "kind": "Доступ к элементу",
        "signature": "items[index]",
        "description": "Возвращает элемент по позиции. Индекс 0 — первый элемент, индекс -1 — последний.",
        "example": "names[-1]  # последний элемент",
        "introduced_in": "lists",
    },
    "append": {
        "name": ".append()",
        "kind": "Метод списка",
        "signature": "items.append(value)",
        "description": "Добавляет один элемент в конец существующего списка и изменяет этот список на месте.",
        "example": "tasks.append('Повторить Python')",
        "introduced_in": "lists-append",
    },
    "split": {
        "name": ".split()",
        "kind": "Метод строки",
        "signature": "text.split()",
        "description": "Разделяет строку по пробельным символам и возвращает список частей. Можно передать собственный разделитель.",
        "example": "'учу Python'.split()  # ['учу', 'Python']",
        "introduced_in": "strings-split",
    },
    "sum": {
        "name": "sum()",
        "kind": "Встроенная функция",
        "signature": "sum(numbers)",
        "description": "Складывает все числа последовательности. Для пустого списка возвращает 0.",
        "example": "sum([2, 3, 4])  # 9",
        "introduced_in": "lists-sum",
    },
    "dict": {
        "name": "Словарь {}",
        "kind": "Коллекция",
        "signature": "record = {'key': value}",
        "description": "Хранит значения по уникальным ключам. Значение можно получить через record['key'].",
        "example": "user = {'name': 'Аня', 'level': 2}",
        "introduced_in": "dicts-sets",
    },
    "get": {
        "name": ".get()",
        "kind": "Метод словаря",
        "signature": "record.get(key, default)",
        "description": "Возвращает значение ключа, а если ключа нет — default вместо ошибки KeyError.",
        "example": "user.get('level', 1)",
        "introduced_in": "dicts-sets",
    },
    "set": {
        "name": "set()",
        "kind": "Встроенная функция",
        "signature": "set(items)",
        "description": "Создаёт множество уникальных значений: повторяющиеся элементы исчезают.",
        "example": "set([1, 1, 2])  # {1, 2}",
        "introduced_in": "sets",
    },
    "with-open": {
        "name": "with open()",
        "kind": "Работа с файлами",
        "signature": "with open(path, mode, encoding='utf-8') as file:",
        "description": "Открывает файл внутри безопасного блока и автоматически закрывает его после выхода из блока.",
        "example": "with open('note.txt', 'w', encoding='utf-8') as file:\n    file.write('Привет')",
        "introduced_in": "files",
    },
    "try-except": {
        "name": "try / except",
        "kind": "Обработка ошибок",
        "signature": "try:\n    risky_action\nexcept ErrorType:\n    fallback",
        "description": "Пробует выполнить код и запускает подходящий except, если возник указанный тип ошибки.",
        "example": "try:\n    age = int(text)\nexcept ValueError:\n    age = 0",
        "introduced_in": "exceptions",
    },
    "class": {
        "name": "class",
        "kind": "Класс",
        "signature": "class Name:\n    attribute = value",
        "description": "Описывает общий чертёж объектов: их данные и доступные методы.",
        "example": "class Badge:\n    title = 'Первые шаги'",
        "introduced_in": "classes",
    },
    "division": {
        "name": "/",
        "kind": "Оператор деления",
        "signature": "left / right",
        "description": "Делит левое число на правое и возвращает частное. Делить на ноль нельзя.",
        "example": "8 / 2  # 4.0",
        "introduced_in": "warmup-numbers",
    },
    "modulo": {
        "name": "%",
        "kind": "Остаток от деления",
        "signature": "left % right",
        "description": "Возвращает остаток от деления. У чётного числа остаток от деления на 2 равен нулю.",
        "example": "8 % 2  # 0",
        "introduced_in": "operators-integer-division",
    },
    "slice": {
        "name": "Срез [start:stop:step]",
        "kind": "Последовательности",
        "signature": "value[start:stop:step]",
        "description": "Берёт часть последовательности. Шаг -1 проходит элементы в обратном порядке.",
        "example": "'код'[::-1]  # 'док'",
        "introduced_in": "tuples-slices-slices",
    },
    "string-slice": {
        "name": "Срез [start:stop]",
        "kind": "Строки и последовательности",
        "signature": "value[start:stop]",
        "description": "Возвращает часть последовательности от start до stop, не включая правую границу.",
        "example": "'python'[1:4]  # 'yth'",
        "introduced_in": "strings-pro-indexes",
    },
    "none": {
        "name": "None",
        "kind": "Специальное значение",
        "signature": "return None",
        "description": "Обозначает отсутствие значения. Это не ноль, не False и не пустая строка.",
        "example": "result = None",
        "introduced_in": "functions-return",
    },
    "tuple": {
        "name": "Кортеж ()",
        "kind": "Коллекция",
        "signature": "pair = (first, second)",
        "description": "Хранит упорядоченную последовательность, которую нельзя изменить после создания.",
        "example": "point = (10, 20)",
        "introduced_in": "tuples-slices-tuples",
    },
}

# The extended path uses real APIs as well as syntax.  Keeping their references
# in the same catalogue makes a forgotten method discoverable by its exact
# spelling instead of falling back to a broad lesson description.
TOOL_CATALOG.update(
    {
        "floor-division": {
            "name": "//",
            "kind": "Целочисленное деление",
            "signature": "left // right",
            "description": "Возвращает целую часть частного с округлением вниз.",
            "example": "17 // 5  # 3",
            "introduced_in": "operators-integer-division",
        },
        "boolean-logic": {
            "name": "and / or / not",
            "kind": "Логические операторы",
            "signature": "left and right",
            "description": "and требует истинности обеих частей, or — хотя бы одной, not меняет истину на ложь и наоборот.",
            "example": "is_ready = has_code and not has_error",
            "introduced_in": "operators-booleans",
        },
        "round": {
            "name": "round()",
            "kind": "Встроенная функция",
            "signature": "round(number, digits)",
            "description": "Возвращает число, округлённое до указанного количества знаков после точки.",
            "example": "round(3.14159, 2)  # 3.14",
            "introduced_in": "operators-floating-point",
        },
        "replace": {
            "name": ".replace()",
            "kind": "Метод строки",
            "signature": "text.replace(old, new)",
            "description": "Возвращает новую строку, где все вхождения old заменены на new.",
            "example": "'1,5'.replace(',', '.')  # '1.5'",
            "introduced_in": "strings-pro-search-replace",
        },
        "join": {
            "name": ".join()",
            "kind": "Метод строки",
            "signature": "separator.join(parts)",
            "description": "Склеивает строки из parts, вставляя separator между соседними частями.",
            "example": "', '.join(['api', 'tests'])  # 'api, tests'",
            "introduced_in": "strings-pro-split-join",
        },
        "f-string-format": {
            "name": "Формат после двоеточия",
            "kind": "f-строка",
            "signature": "f'{value:>5}'",
            "description": "Часть после : управляет шириной, выравниванием и видом числа внутри f-строки.",
            "example": "f'{7:>3}'  # '  7'",
            "introduced_in": "strings-pro-formatting",
        },
        "unpacking": {
            "name": "Распаковка",
            "kind": "Присваивание",
            "signature": "first, second = pair",
            "description": "Раздаёт элементы последовательности переменным слева в том же порядке.",
            "example": "x, y = (10, 20)",
            "introduced_in": "tuples-slices-unpacking",
        },
        "enumerate": {
            "name": "enumerate()",
            "kind": "Встроенная функция",
            "signature": "enumerate(items, start=0)",
            "description": "Во время обхода выдаёт пары (номер, элемент); start задаёт первый номер.",
            "example": "for index, name in enumerate(names, start=1): ...",
            "introduced_in": "tuples-slices-zip-enumerate",
        },
        "zip": {
            "name": "zip()",
            "kind": "Встроенная функция",
            "signature": "zip(left, right)",
            "description": "Объединяет элементы нескольких последовательностей по одинаковым позициям.",
            "example": "list(zip(['А', 'Б'], [1, 2]))  # [('А', 1), ('Б', 2)]",
            "introduced_in": "tuples-slices-zip-enumerate",
        },
        "extend": {
            "name": ".extend()",
            "kind": "Метод списка",
            "signature": "items.extend(other_items)",
            "description": "Добавляет в конец списка все элементы другой последовательности.",
            "example": "[1, 2].extend([3, 4])",
            "introduced_in": "lists-pro-list-methods",
        },
        "insert": {
            "name": ".insert()",
            "kind": "Метод списка",
            "signature": "items.insert(index, value)",
            "description": "Вставляет value перед указанным индексом и изменяет список на месте.",
            "example": "tasks.insert(0, 'Срочно')",
            "introduced_in": "lists-pro-list-methods",
        },
        "pop": {
            "name": ".pop()",
            "kind": "Метод списка",
            "signature": "items.pop(index=-1)",
            "description": "Удаляет элемент по индексу и возвращает его; без аргумента берёт последний.",
            "example": "last = stack.pop()",
            "introduced_in": "lists-pro-stacks-queues",
        },
        "remove": {
            "name": ".remove()",
            "kind": "Метод списка",
            "signature": "items.remove(value)",
            "description": "Удаляет первое равное value значение; если его нет, возникает ValueError.",
            "example": "items.remove('готово')",
            "introduced_in": "lists-pro-mutation",
        },
        "items": {
            "name": ".items()",
            "kind": "Метод словаря",
            "signature": "record.items()",
            "description": "Возвращает представление пар (ключ, значение), удобное для цикла.",
            "example": "for key, value in record.items(): ...",
            "introduced_in": "mappings-dict-loops",
        },
        "sorted": {
            "name": "sorted()",
            "kind": "Встроенная функция",
            "signature": "sorted(items, key=None, reverse=False)",
            "description": "Возвращает новый отсортированный список и не меняет исходную коллекцию.",
            "example": "sorted([3, 1, 2])  # [1, 2, 3]",
            "introduced_in": "lists-pro-sorting",
        },
        "sort": {
            "name": ".sort()",
            "kind": "Метод списка",
            "signature": "items.sort(key=None, reverse=False)",
            "description": "Сортирует существующий список на месте и возвращает None.",
            "example": "scores.sort(reverse=True)",
            "introduced_in": "lists-pro-list-methods",
        },
        "elif": {
            "name": "elif",
            "kind": "Ветка условия",
            "signature": "elif condition:\n    action",
            "description": "Проверяет следующее условие только если предыдущие ветки if/elif не сработали.",
            "example": "elif score >= 70:\n    grade = 'B'",
            "introduced_in": "flow-advanced-elif",
        },
        "continue": {
            "name": "continue",
            "kind": "Управление циклом",
            "signature": "if skip:\n    continue",
            "description": "Пропускает остаток текущей итерации и переходит к следующему элементу.",
            "example": "if value < 0:\n    continue",
            "introduced_in": "flow-advanced-break-continue",
        },
        "loop-else": {
            "name": "else у цикла",
            "kind": "Управление циклом",
            "signature": "for item in items:\n    ...\nelse:\n    fallback",
            "description": "Выполняется после естественного завершения цикла, но не после break.",
            "example": "for item in items:\n    ...\nelse:\n    print('Не найдено')",
            "introduced_in": "flow-advanced-loop-else",
        },
        "default-parameter": {
            "name": "Значение параметра по умолчанию",
            "kind": "Функции",
            "signature": "def greet(name='мир'):",
            "description": "Подставляется, если вызывающий код не передал соответствующий аргумент.",
            "example": "def greet(name='мир'):\n    return f'Привет, {name}!'",
            "introduced_in": "functions-pro-defaults",
        },
        "varargs": {
            "name": "*args / **kwargs",
            "kind": "Параметры функции",
            "signature": "def report(*items, **options):",
            "description": "*args собирает позиционные аргументы в кортеж, **kwargs — именованные в словарь.",
            "example": "def report(*items, **options): ...",
            "introduced_in": "functions-pro-varargs",
        },
        "lambda": {
            "name": "lambda",
            "kind": "Короткая функция",
            "signature": "lambda argument: expression",
            "description": "Создаёт небольшую функцию из одного выражения, часто для параметра key.",
            "example": "users.sort(key=lambda user: user['age'])",
            "introduced_in": "scope-lambda-key",
        },
        "list-comprehension": {
            "name": "List comprehension",
            "kind": "Создание списка",
            "signature": "[expression for item in items]",
            "description": "Создаёт новый список, применяя выражение к каждому элементу обхода.",
            "example": "squares = [n * n for n in numbers]",
            "introduced_in": "comprehensions-list-comprehension",
        },
        "comprehension-filter": {
            "name": "Фильтр comprehension",
            "kind": "Создание коллекции",
            "signature": "[item for item in items if condition]",
            "description": "Добавляет в новую коллекцию только элементы, для которых условие истинно.",
            "example": "evens = [n for n in numbers if n % 2 == 0]",
            "introduced_in": "comprehensions-comprehension-filter",
        },
        "dict-comprehension": {
            "name": "Dict comprehension",
            "kind": "Создание словаря",
            "signature": "{key: value for item in items}",
            "description": "Строит словарь из обхода, вычисляя ключ и значение для каждого элемента.",
            "example": "lengths = {word: len(word) for word in words}",
            "introduced_in": "comprehensions-dict-comprehension",
        },
        "generator-expression": {
            "name": "Генераторное выражение",
            "kind": "Ленивый обход",
            "signature": "(expression for item in items)",
            "description": "Вычисляет элементы по одному вместо создания готового списка целиком.",
            "example": "total = sum(n * n for n in numbers)",
            "introduced_in": "iterators-generator-expression",
        },
        "import": {
            "name": "import",
            "kind": "Импорт модуля",
            "signature": "import module",
            "description": "Подключает модуль, после чего его функции доступны через имя модуля и точку.",
            "example": "import math\nprint(math.sqrt(9))",
            "introduced_in": "modules-imports",
        },
        "path": {
            "name": "Path()",
            "kind": "Путь из pathlib",
            "signature": "Path(path_text)",
            "description": "Создаёт объект пути; оператор / добавляет к нему следующую часть пути.",
            "example": "Path('notes') / 'today.txt'",
            "introduced_in": "modules-stdlib-imports",
        },
        "json-dump": {
            "name": "json.dump()",
            "kind": "JSON и файл",
            "signature": "json.dump(data, file, ensure_ascii=False)",
            "description": "Преобразует Python-данные в JSON и записывает их в открытый файл.",
            "example": "json.dump(notes, file, ensure_ascii=False)",
            "introduced_in": "files-data-json",
        },
        "json-load": {
            "name": "json.load()",
            "kind": "JSON и файл",
            "signature": "json.load(file)",
            "description": "Читает JSON из открытого файла и возвращает соответствующие Python-данные.",
            "example": "notes = json.load(file)",
            "introduced_in": "files-data-json",
        },
        "json-dumps": {
            "name": "json.dumps()",
            "kind": "JSON-строка",
            "signature": "json.dumps(data, ensure_ascii=False)",
            "description": "Возвращает JSON как строку, не записывая его в файл.",
            "example": "payload = json.dumps(data, ensure_ascii=False)",
            "introduced_in": "files-data-json",
        },
        "raise": {
            "name": "raise",
            "kind": "Создание ошибки",
            "signature": "raise ValueError(message)",
            "description": "Немедленно останавливает текущий путь выполнения и создаёт указанное исключение.",
            "example": "raise ValueError('Возраст должен быть положительным')",
            "introduced_in": "errors-debug-raise",
        },
        "finally": {
            "name": "finally",
            "kind": "Обработка ошибок",
            "signature": "try:\n    action\nfinally:\n    cleanup",
            "description": "Выполняет блок очистки всегда: и при успехе, и при исключении.",
            "example": "finally:\n    print('Готово')",
            "introduced_in": "errors-debug-finally",
        },
        "init": {
            "name": "__init__()",
            "kind": "Инициализация объекта",
            "signature": "def __init__(self, value):",
            "description": "Получает данные нового объекта и обычно сохраняет их в атрибутах self.",
            "example": "def __init__(self, title):\n    self.title = title",
            "introduced_in": "oop-design-init",
        },
        "property": {
            "name": "@property",
            "kind": "Свойство объекта",
            "signature": "@property\ndef value(self):",
            "description": "Позволяет вызывать вычисляющий метод как обычный атрибут без скобок.",
            "example": "@property\ndef total(self):\n    return sum(self.items)",
            "introduced_in": "oop-advanced-properties",
        },
        "type-annotation": {
            "name": "Аннотация типа",
            "kind": "Типизация",
            "signature": "def total(values: list[int]) -> int:",
            "description": "Документирует ожидаемые типы параметров и результата, но сама не преобразует данные.",
            "example": "score: int = 10",
            "introduced_in": "typing-models-annotations",
        },
        "dataclass": {
            "name": "@dataclass",
            "kind": "Модель данных",
            "signature": "@dataclass\nclass User:",
            "description": "Автоматически создаёт служебные методы класса по объявленным полям.",
            "example": "@dataclass\nclass User:\n    name: str",
            "introduced_in": "typing-models-dataclasses-enums",
        },
        "timedelta": {
            "name": "timedelta()",
            "kind": "Дата и время",
            "signature": "timedelta(days=0, seconds=0)",
            "description": "Создаёт временной интервал, который можно прибавить к дате или вычесть из неё.",
            "example": "deadline = today + timedelta(days=7)",
            "introduced_in": "stdlib-core-datetime",
        },
        "random-choice": {
            "name": "random.choice()",
            "kind": "Случайный выбор",
            "signature": "random.choice(items)",
            "description": "Возвращает один псевдослучайно выбранный элемент непустой последовательности.",
            "example": "winner = random.choice(names)",
            "introduced_in": "stdlib-core-random",
        },
        "statistics-mean": {
            "name": "statistics.mean()",
            "kind": "Статистика",
            "signature": "statistics.mean(numbers)",
            "description": "Возвращает арифметическое среднее переданных чисел.",
            "example": "statistics.mean([2, 4, 6])  # 4",
            "introduced_in": "stdlib-core-math-statistics",
        },
        "decimal": {
            "name": "Decimal()",
            "kind": "Точные десятичные числа",
            "signature": "Decimal(text)",
            "description": "Создаёт десятичное число с предсказуемой точностью; для денег его передают строкой.",
            "example": "Decimal('19.90')",
            "introduced_in": "stdlib-core-decimal",
        },
        "counter": {
            "name": "Counter()",
            "kind": "collections",
            "signature": "Counter(items)",
            "description": "Подсчитывает, сколько раз встретился каждый элемент, и возвращает словарь-счётчик.",
            "example": "Counter(['a', 'a', 'b'])  # {'a': 2, 'b': 1}",
            "introduced_in": "stdlib-productivity-collections",
        },
        "combinations": {
            "name": "itertools.combinations()",
            "kind": "itertools",
            "signature": "itertools.combinations(items, size)",
            "description": "Перебирает сочетания указанного размера без повторения порядка элементов.",
            "example": "list(itertools.combinations(['A', 'B', 'C'], 2))",
            "introduced_in": "stdlib-productivity-itertools",
        },
        "lru-cache": {
            "name": "@lru_cache",
            "kind": "functools",
            "signature": "@lru_cache(maxsize=None)",
            "description": "Запоминает результаты функции для уже встречавшихся наборов аргументов.",
            "example": "@lru_cache(maxsize=None)\ndef fib(n): ...",
            "introduced_in": "stdlib-productivity-functools",
        },
        "heappush": {
            "name": "heapq.heappush()",
            "kind": "Очередь с приоритетом",
            "signature": "heapq.heappush(heap, item)",
            "description": "Добавляет item в кучу так, чтобы минимальный элемент оставался доступен первым.",
            "example": "heapq.heappush(queue, (priority, task))",
            "introduced_in": "stdlib-productivity-heapq-bisect",
        },
        "regex-fullmatch": {
            "name": "re.fullmatch()",
            "kind": "Регулярное выражение",
            "signature": "re.fullmatch(pattern, text)",
            "description": "Возвращает совпадение, только если шаблону соответствует вся строка целиком.",
            "example": "re.fullmatch(r'\\d{6}', postal_code)",
            "introduced_in": "regex-patterns",
        },
        "regex-sub": {
            "name": "re.sub()",
            "kind": "Регулярное выражение",
            "signature": "re.sub(pattern, replacement, text)",
            "description": "Возвращает строку, где совпадения шаблона заменены на replacement.",
            "example": "re.sub(r'\\s+', ' ', text)",
            "introduced_in": "regex-substitution",
        },
        "assert": {
            "name": "assert",
            "kind": "Проверка",
            "signature": "assert actual == expected",
            "description": "Продолжает работу при истинном условии и создаёт AssertionError при ложном.",
            "example": "assert discount(100) == 90",
            "introduced_in": "testing-unit-tests",
        },
        "sql-parameters": {
            "name": "Параметры SQL",
            "kind": "Базы данных",
            "signature": "cursor.execute(sql, params)",
            "description": "Передают значения отдельно от SQL-шаблона с ?, не склеивая пользовательский текст с запросом.",
            "example": "cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))",
            "introduced_in": "databases-parameters",
        },
        "async-def": {
            "name": "async def",
            "kind": "Корутина",
            "signature": "async def function_name():",
            "description": "Объявляет корутину, выполнение которой можно приостанавливать через await.",
            "example": "async def fetch():\n    await asyncio.sleep(0)",
            "introduced_in": "async-coroutines",
        },
        "await": {
            "name": "await",
            "kind": "Ожидание корутины",
            "signature": "result = await coroutine",
            "description": "Приостанавливает текущую корутину до получения результата, не блокируя цикл событий.",
            "example": "await asyncio.sleep(0)",
            "introduced_in": "async-coroutines",
        },
        "asyncio-sleep": {
            "name": "asyncio.sleep()",
            "kind": "Асинхронное ожидание",
            "signature": "await asyncio.sleep(seconds)",
            "description": "Приостанавливает корутину на заданное время и отдаёт управление другим задачам.",
            "example": "await asyncio.sleep(0.1)",
            "introduced_in": "async-coroutines",
        },
        "asyncio-create-task": {
            "name": "asyncio.create_task()",
            "kind": "Async-задача",
            "signature": "asyncio.create_task(coroutine)",
            "description": "Регистрирует корутину для конкурентного выполнения и возвращает объект Task.",
            "example": "task = asyncio.create_task(fetch())",
            "introduced_in": "async-tasks",
        },
        "asyncio-gather": {
            "name": "asyncio.gather()",
            "kind": "Группа async-задач",
            "signature": "await asyncio.gather(*awaitables)",
            "description": "Ждёт несколько awaitable-объектов и возвращает результаты в порядке аргументов.",
            "example": "results = await asyncio.gather(*tasks)",
            "introduced_in": "async-gather-timeouts",
        },
        "asyncio-run": {
            "name": "asyncio.run()",
            "kind": "Запуск async-программы",
            "signature": "asyncio.run(coroutine)",
            "description": "Создаёт цикл событий, выполняет корутину до конца и возвращает её результат.",
            "example": "result = asyncio.run(main())",
            "introduced_in": "async-coroutines",
        },
        "match": {
            "name": "match / case",
            "kind": "Сопоставление с образцом",
            "signature": "match value:\n    case pattern:\n        action",
            "description": "Сравнивает значение с образцами case сверху вниз и выполняет первую подходящую ветку.",
            "example": "match status:\n    case 'ready':\n        message = 'Старт'",
            "introduced_in": "flow-advanced-match",
        },
        "iter": {
            "name": "iter()",
            "kind": "Встроенная функция",
            "signature": "iterator = iter(iterable)",
            "description": "Получает итератор — объект, который выдаёт элементы последовательности по одному.",
            "example": "iterator = iter([10, 20])",
            "introduced_in": "iterators-iterable",
        },
        "next": {
            "name": "next()",
            "kind": "Встроенная функция",
            "signature": "next(iterator, default)",
            "description": "Берёт следующий элемент итератора; необязательный default возвращается вместо StopIteration.",
            "example": "next(iter([10, 20]))  # 10",
            "introduced_in": "iterators-iterable",
        },
        "yield": {
            "name": "yield",
            "kind": "Генератор",
            "signature": "yield value",
            "description": "Отдаёт одно значение и запоминает состояние функции до следующего вызова next().",
            "example": "def numbers():\n    yield 1\n    yield 2",
            "introduced_in": "iterators-yield",
        },
        "sqrt": {
            "name": "math.sqrt()",
            "kind": "Математическая функция",
            "signature": "math.sqrt(number)",
            "description": "Возвращает квадратный корень неотрицательного числа.",
            "example": "math.sqrt(81)  # 9.0",
            "introduced_in": "modules-imports",
        },
        "thread-pool": {
            "name": "ThreadPoolExecutor()",
            "kind": "Пул потоков",
            "signature": "ThreadPoolExecutor(max_workers=count)",
            "description": "Создаёт ограниченный набор потоков для параллельного запуска блокирующих задач.",
            "example": "with ThreadPoolExecutor(max_workers=4) as pool:\n    ...",
            "introduced_in": "concurrency-thread-pool",
        },
        "pool-map": {
            "name": ".map() у пула",
            "kind": "Конкурентное выполнение",
            "signature": "pool.map(function, items)",
            "description": "Запускает function для каждого элемента и выдаёт результаты в порядке исходных данных.",
            "example": "results = list(pool.map(load_page, urls))",
            "introduced_in": "concurrency-thread-pool",
        },
        "queue-put": {
            "name": "Queue.put()",
            "kind": "Потокобезопасная очередь",
            "signature": "tasks.put(item)",
            "description": "Добавляет item в очередь, безопасно разделяемую между потоками.",
            "example": "tasks.put('report.csv')",
            "introduced_in": "concurrency-queues",
        },
        "queue": {
            "name": "queue.Queue()",
            "kind": "Потокобезопасная очередь",
            "signature": "tasks = Queue()",
            "description": "Хранит элементы в порядке FIFO и безопасно координирует производителей и потребителей в потоках.",
            "example": "from queue import Queue\ntasks = Queue()",
            "introduced_in": "concurrency-queues",
        },
        "queue-get": {
            "name": "Queue.get()",
            "kind": "Потокобезопасная очередь",
            "signature": "item = tasks.get()",
            "description": "Извлекает следующий элемент; при пустой очереди по умолчанию ждёт его появления.",
            "example": "item = tasks.get()",
            "introduced_in": "concurrency-queues",
        },
        "queue-empty": {
            "name": "Queue.empty()",
            "kind": "Проверка очереди",
            "signature": "tasks.empty()",
            "description": "Возвращает True, если в очереди сейчас нет элементов.",
            "example": "while not tasks.empty():\n    item = tasks.get()",
            "introduced_in": "concurrency-queues",
        },
    }
)

TOOL_CATALOG.update(
    {
        "dict-merge": {
            "name": "| для словарей",
            "kind": "Объединение словарей",
            "signature": "merged = defaults | overrides",
            "description": "Создаёт новый словарь; при совпадении ключа значение справа побеждает.",
            "example": "{'theme': 'light'} | {'theme': 'dark'}  # {'theme': 'dark'}",
            "introduced_in": "mappings-dict-merge",
        },
        "main-guard": {
            "name": "main guard",
            "kind": "Точка входа",
            "signature": "if __name__ == '__main__':",
            "description": "Запускает блок только при прямом старте файла, но не при его импорте.",
            "example": "if __name__ == '__main__':\n    main()",
            "introduced_in": "modules-main-guard",
        },
        "path-posix": {
            "name": "Path.as_posix()",
            "kind": "Метод пути",
            "signature": "path.as_posix()",
            "description": "Возвращает текст пути с прямыми слешами независимо от операционной системы.",
            "example": "(Path('notes') / 'today.txt').as_posix()",
            "introduced_in": "modules-stdlib-imports",
        },
        "file-read-write": {
            "name": ".write() / .read()",
            "kind": "Методы файла",
            "signature": "file.write(text)\ntext = file.read()",
            "description": "write записывает текст в открытый файл, read возвращает его содержимое.",
            "example": "with open('note.txt', 'w') as file:\n    file.write('Привет')",
            "introduced_in": "files-data-text-files",
        },
        "json-loads": {
            "name": "json.loads()",
            "kind": "JSON-десериализация",
            "signature": "data = json.loads(text)",
            "description": "Преобразует JSON-текст обратно в словари, списки и простые значения Python.",
            "example": "json.loads('{\"done\": true}')  # {'done': True}",
            "introduced_in": "files-data-json",
        },
        "csv-reader": {
            "name": "csv.reader()",
            "kind": "Чтение CSV",
            "signature": "rows = csv.reader(lines)",
            "description": "Разбирает строки CSV и выдаёт каждую строку как список текстовых ячеек.",
            "example": "rows = csv.reader(['name,score', 'Аня,10'])",
            "introduced_in": "files-data-csv",
        },
        "repr-method": {
            "name": "__repr__()",
            "kind": "Представление объекта",
            "signature": "def __repr__(self):\n    return 'Class(...)'",
            "description": "Возвращает однозначную строку для разработчика и отладки объекта.",
            "example": "def __repr__(self):\n    return f'Task({self.title!r})'",
            "introduced_in": "oop-design-repr-str",
        },
        "super": {
            "name": "super()",
            "kind": "Наследование",
            "signature": "super().__init__(arguments)",
            "description": "Обращается к реализации базового класса, например к его __init__.",
            "example": "super().__init__(title)",
            "introduced_in": "oop-advanced-inheritance",
        },
        "iter-protocol": {
            "name": "__iter__()",
            "kind": "Протокол итерации",
            "signature": "def __iter__(self):\n    yield value",
            "description": "Позволяет объекту участвовать в for и выдавать значения по одному.",
            "example": "def __iter__(self):\n    yield from self.items",
            "introduced_in": "oop-advanced-protocols",
        },
        "len-protocol": {
            "name": "__len__()",
            "kind": "Специальный метод",
            "signature": "def __len__(self):\n    return count",
            "description": "Определяет результат встроенной функции len() для объекта.",
            "example": "def __len__(self):\n    return len(self.items)",
            "introduced_in": "oop-advanced-special-methods",
        },
        "union-type": {
            "name": "X | None",
            "kind": "Аннотация типа",
            "signature": "def find(...) -> str | None:",
            "description": "Показывает, что результатом может быть значение указанного типа либо None.",
            "example": "name: str | None = users.get(user_id)",
            "introduced_in": "typing-models-optional-union",
        },
        "copy": {
            "name": ".copy()",
            "kind": "Копирование коллекции",
            "signature": "updated = original.copy()",
            "description": "Создаёт поверхностную копию списка или словаря, чтобы не менять исходный объект.",
            "example": "updated = settings.copy()",
            "introduced_in": "typing-models-generic-collections",
        },
        "date-iso": {
            "name": "date.fromisoformat()",
            "kind": "Дата из текста",
            "signature": "day = date.fromisoformat('2026-07-15')",
            "description": "Создаёт date из строки YYYY-MM-DD; isoformat() выполняет обратное преобразование.",
            "example": "date.fromisoformat('2026-07-15').isoformat()",
            "introduced_in": "stdlib-core-datetime",
        },
        "random-generator": {
            "name": "random.Random()",
            "kind": "Локальный генератор",
            "signature": "generator = random.Random(seed)",
            "description": "Создаёт отдельный воспроизводимый генератор, не меняя глобальное состояние random.",
            "example": "generator = random.Random(7)\nwinner = generator.choice(names)",
            "introduced_in": "stdlib-core-random",
        },
        "heappop": {
            "name": "heapq.heappop()",
            "kind": "Извлечение из кучи",
            "signature": "smallest = heapq.heappop(heap)",
            "description": "Удаляет и возвращает наименьший элемент кучи.",
            "example": "priority, task = heapq.heappop(queue)",
            "introduced_in": "stdlib-productivity-heapq-bisect",
        },
        "regex-group": {
            "name": "match.group()",
            "kind": "Группа регулярного выражения",
            "signature": "value = match.group('name')",
            "description": "Возвращает текст, который попал в указанную обычную или именованную группу.",
            "example": "name = match.group('name')",
            "introduced_in": "regex-groups",
        },
        "docstring": {
            "name": "docstring",
            "kind": "Документация функции",
            "signature": 'def function():\n    """Что возвращает функция."""',
            "description": "Первая строка-литерал в теле функции хранит её встроенное описание.",
            "example": 'def total(values):\n    """Вернуть сумму значений."""\n    return sum(values)',
            "introduced_in": "quality-docstrings",
        },
        "argparse-parser": {
            "name": "argparse.ArgumentParser()",
            "kind": "CLI-парсер",
            "signature": "parser = argparse.ArgumentParser()",
            "description": "Описывает CLI: add_argument добавляет параметр, parse_args разбирает список.",
            "example": "parser.add_argument('--input')\nargs = parser.parse_args(['--input', 'data.csv'])",
            "introduced_in": "cli-environment-argv",
        },
        "upper": {
            "name": ".upper()",
            "kind": "Метод строки",
            "signature": "text.upper()",
            "description": "Возвращает новую строку в верхнем регистре, не изменяя исходную.",
            "example": "'get'.upper()  # 'GET'",
            "introduced_in": "http-api-request-response",
        },
        "sqlite-fetchone": {
            "name": "cursor.fetchone()",
            "kind": "Чтение одной строки SQL",
            "signature": "row = cursor.fetchone()",
            "description": "Возвращает следующую строку SELECT либо None, если строк больше нет.",
            "example": "row = connection.execute(sql, params).fetchone()",
            "introduced_in": "databases-parameters",
        },
        "lock": {
            "name": "threading.Lock()",
            "kind": "Блокировка",
            "signature": "lock = Lock()\nwith lock:\n    update()",
            "description": "Разрешает одному потоку выполнять защищённую критическую секцию.",
            "example": "with lock:\n    balance += amount",
            "introduced_in": "concurrency-locks",
        },
    }
)


# Callable cards are derived from the hidden author reference. This keeps a
# reminder synchronized with the API that the task really uses without exposing
# the ready solution itself.
SOURCE_FEATURE_TOOL_IDS: dict[str, str] = {
    "call:Counter": "counter",
    "call:Decimal": "decimal",
    "call:Lock": "lock",
    "call:Path": "path",
    "call:Queue": "queue",
    "call:ThreadPoolExecutor": "thread-pool",
    "call:ValueError": "try-except",
    "call:bool": "bool",
    "call:combinations": "combinations",
    "call:dict": "dict",
    "call:enumerate": "enumerate",
    "call:function": "function-call",
    "call:int": "int",
    "call:iter": "iter",
    "call:len": "len",
    "call:list": "list",
    "call:lru_cache": "lru-cache",
    "call:make_user": "function-call",
    "call:next": "next",
    "call:open": "with-open",
    "call:range": "range",
    "call:round": "round",
    "call:set": "set",
    "call:sorted": "sorted",
    "call:sum": "sum",
    "call:super": "super",
    "call:timedelta": "timedelta",
    "method:ArgumentParser": "argparse-parser",
    "method:Random": "random-generator",
    "method:add_argument": "argparse-parser",
    "method:append": "append",
    "method:as_posix": "path-posix",
    "method:choice": "random-choice",
    "method:connect": "sql-parameters",
    "method:copy": "copy",
    "method:create_task": "asyncio-create-task",
    "method:dumps": "json-dumps",
    "method:empty": "queue-empty",
    "method:execute": "sql-parameters",
    "method:fetchone": "sqlite-fetchone",
    "method:fromisoformat": "date-iso",
    "method:fullmatch": "regex-fullmatch",
    "method:gather": "asyncio-gather",
    "method:get": "get",
    "method:group": "regex-group",
    "method:heappop": "heappop",
    "method:heappush": "heappush",
    "method:isoformat": "date-iso",
    "method:items": "items",
    "method:join": "join",
    "method:loads": "json-loads",
    "method:map": "pool-map",
    "method:mean": "statistics-mean",
    "method:parse_args": "argparse-parser",
    "method:pop": "pop",
    "method:put": "queue-put",
    "method:read": "file-read-write",
    "method:reader": "csv-reader",
    "method:remove": "remove",
    "method:replace": "replace",
    "method:sleep": "asyncio-sleep",
    "method:sqrt": "sqrt",
    "method:strip": "strip",
    "method:sub": "regex-sub",
    "method:upper": "upper",
    "method:write": "file-read-write",
}

PUBLIC_TOOL_FIELDS = ("name", "kind", "signature", "description", "example", "language")


def public_tool_help(tools: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """Return only learner-facing fields from structured tool references."""
    return [
        {field: tool[field] for field in PUBLIC_TOOL_FIELDS if tool.get(field)} for tool in tools
    ]


def tool_reference_cards(tool_ids: Iterable[str]) -> list[dict[str, str]]:
    """Resolve explicit catalogue ids and remove duplicates without reordering."""
    cards: list[dict[str, str]] = []
    for tool_id in dict.fromkeys(tool_ids):
        tool = TOOL_CATALOG.get(tool_id)
        if tool:
            cards.append(public_tool_help([tool])[0])
    return cards


CONCEPT_TOOL_IDS: dict[str, tuple[str, ...]] = {
    "learning.route": ("print",),
    "io.print": ("print",),
    "io.print-call": ("print",),
    "value.string": ("string",),
    "syntax.comment": ("comment",),
    "data.variable": ("assignment",),
    "naming.snake-case": ("assignment",),
    "value.integer": ("arithmetic",),
    "operator.arithmetic": ("arithmetic",),
    "type.string-vs-number": ("string", "arithmetic"),
    "builtin.len": ("len",),
    "string.f-string": ("f-string",),
    "builtin.input": ("input",),
    "conversion.int": ("int",),
    "value.boolean": ("bool",),
    "operator.comparison": ("comparison",),
    "syntax.indentation": ("indent",),
    "debug.name-error": ("name-error", "assignment"),
    "method.string-lower": ("lower",),
    "method.string-strip": ("strip",),
    "review.dialogue": ("input", "f-string", "print"),
    "review.counter": ("assignment", "arithmetic", "print"),
    "transfer.print": ("print",),
    "transfer.variables": ("assignment", "f-string", "print"),
    "transfer.input": ("input", "f-string", "print"),
    "condition.if": ("if", "comparison"),
    "condition.else": ("if", "else"),
    "loop.for-range": ("for", "range"),
    "assignment.accumulator": ("for", "range", "plus-equals"),
    "loop.while": ("while", "comparison"),
    "loop.break": ("while", "break"),
    "function.call": ("def", "function-call"),
    "function.parameter": ("parameter", "function-call"),
    "function.return": ("return",),
    "function.compose": ("return", "f-string"),
    "function.keyword-argument": ("keyword-argument",),
    "collection.list-index": ("list", "index"),
    "method.list-append": ("append",),
    "method.string-split": ("split", "len"),
    "builtin.sum": ("sum",),
    "collection.dictionary": ("dict", "get"),
    "collection.set": ("set", "len"),
    "file.context-manager": ("with-open",),
    "error.try-except": ("try-except",),
    "object.class": ("class",),
}


# Cumulative foundation challenges intentionally combine earlier topics.  Their
# references are explicit so the hint never recommends a tool from the current
# lesson that the actual task does not need.
QUESTION_TOOL_IDS: dict[str, tuple[str, ...]] = {
    "warmup-read-code-code": ("comment", "print"),
    "warmup-names-code": ("assignment", "print"),
    "warmup-numbers-code": ("arithmetic", "print"),
    "warmup-types-code": ("string", "arithmetic", "print"),
    "warmup-input-code": ("input", "f-string", "print"),
    "warmup-convert-code": ("int", "arithmetic", "print"),
    "warmup-indent-code": ("indent", "print"),
    "warmup-methods-code": ("lower", "print"),
    "warmup-recap-one-code": ("f-string", "print"),
    "warmup-recap-two-code": ("f-string", "print"),
    "file-code": ("f-string", "return"),
    "challenge-strings-strip": ("strip", "lower", "print"),
    "challenge-hello": ("f-string", "print"),
    "challenge-variables": ("multiply", "assignment", "f-string", "print"),
    "challenge-strings-input": ("input", "strip", "f-string", "print"),
    "challenge-conditions": ("if", "comparison", "print"),
    "challenge-conditions-else": ("if", "else", "comparison", "print"),
    "challenge-for-loop": ("for", "range", "f-string", "print"),
    "challenge-for-accumulator": ("for", "range", "plus-equals", "print"),
    "challenge-while-loop": ("while", "comparison", "assignment", "print"),
    "challenge-while-break": ("while", "if", "break", "print"),
    "challenge-functions": ("function-call",),
    "challenge-functions-parameters": ("parameter", "function-call"),
    "challenge-functions-return": ("return", "multiply"),
    "challenge-functions-greeting": ("strip", "f-string", "return"),
    "challenge-functions-keyword-arguments": ("keyword-argument", "function-call"),
    "challenge-lists": ("index", "return"),
    "challenge-lists-append": ("append", "return"),
    "challenge-strings-split": ("split", "len", "return"),
    "challenge-lists-sum": ("sum", "return"),
    "challenge-dicts-sets": ("get", "return"),
    "challenge-sets": ("set", "len", "return"),
    "challenge-files": ("strip", "f-string", "return"),
    "challenge-exceptions": ("try-except", "int", "return"),
    "challenge-classes": ("class", "assignment"),
}


# Topic questions in the extended path used to expose one broad card generated
# from the lesson title.  These mappings replace it with exact callable/syntax
# references where the lesson introduces a concrete Python tool.
LESSON_TOOL_IDS: dict[str, tuple[str, ...]] = {
    "operators-arithmetic": ("arithmetic",),
    "operators-integer-division": ("floor-division", "modulo"),
    "operators-booleans": ("boolean-logic",),
    "operators-floating-point": ("round",),
    "strings-pro-indexes": ("string-slice",),
    "strings-pro-search-replace": ("replace",),
    "strings-pro-split-join": ("split", "join"),
    "strings-pro-formatting": ("f-string", "f-string-format"),
    "tuples-slices-tuples": ("tuple",),
    "tuples-slices-unpacking": ("unpacking",),
    "tuples-slices-slices": ("slice",),
    "tuples-slices-zip-enumerate": ("enumerate", "zip"),
    "lists-pro-list-methods": ("append", "extend", "insert"),
    "lists-pro-sorting": ("sorted", "sort"),
    "lists-pro-stacks-queues": ("append", "pop"),
    "lists-pro-mutation": ("slice", "remove"),
    "mappings-dict-basics": ("dict", "get"),
    "mappings-dict-loops": ("items",),
    "mappings-dict-merge": ("dict-merge",),
    "mappings-sets": ("set", "sorted"),
    "flow-advanced-elif": ("if", "elif", "else"),
    "flow-advanced-break-continue": ("break", "continue"),
    "flow-advanced-loop-else": ("for", "break", "loop-else"),
    "flow-advanced-match": ("match",),
    "functions-pro-parameters": ("parameter",),
    "functions-pro-defaults": ("default-parameter",),
    "functions-pro-keyword-args": ("keyword-argument",),
    "functions-pro-varargs": ("varargs",),
    "scope-legb": ("assignment", "return"),
    "scope-mutable-default": ("default-parameter", "none", "if", "append", "return"),
    "scope-closures": ("def", "multiply", "return"),
    "scope-lambda-key": ("lambda", "sort"),
    "comprehensions-list-comprehension": ("list-comprehension",),
    "comprehensions-comprehension-filter": ("list-comprehension", "comprehension-filter"),
    "comprehensions-dict-comprehension": ("dict-comprehension",),
    "comprehensions-nested-comprehension": ("list-comprehension",),
    "iterators-generator-expression": ("generator-expression",),
    "iterators-iterable": ("iter", "next"),
    "iterators-stop-iteration": ("iter", "next", "try-except"),
    "iterators-yield": ("yield",),
    "modules-imports": ("import", "sqrt"),
    "modules-main-guard": ("main-guard",),
    "modules-packages": ("f-string",),
    "modules-stdlib-imports": ("import", "path", "path-posix"),
    "files-data-pathlib": ("import", "path", "path-posix", "f-string"),
    "files-data-text-files": ("with-open", "file-read-write"),
    "files-data-json": ("import", "json-dumps", "json-loads"),
    "files-data-csv": ("import", "csv-reader", "next", "int", "dict"),
    "errors-debug-exception-types": ("try-except", "int", "none"),
    "errors-debug-raise": ("raise",),
    "errors-debug-finally": ("try-except", "finally"),
    "errors-debug-debugging": ("f-string", "f-string-format"),
    "oop-design-init": ("class", "init"),
    "oop-design-repr-str": ("class", "init", "repr-method", "f-string-format"),
    "oop-design-class-instance": ("class", "init", "assignment"),
    "oop-design-composition": ("class", "init", "append", "list-comprehension"),
    "oop-advanced-inheritance": ("class", "init", "super"),
    "oop-advanced-properties": ("property",),
    "oop-advanced-protocols": ("class", "init", "iter-protocol", "yield", "range"),
    "oop-advanced-special-methods": ("class", "init", "len-protocol", "len"),
    "typing-models-annotations": ("type-annotation",),
    "typing-models-optional-union": ("type-annotation", "union-type", "none", "get"),
    "typing-models-generic-collections": ("type-annotation", "copy", "dict"),
    "typing-models-dataclasses-enums": ("dataclass",),
    "stdlib-core-datetime": ("date-iso", "timedelta"),
    "stdlib-core-random": ("random-generator", "random-choice"),
    "stdlib-core-math-statistics": ("statistics-mean",),
    "stdlib-core-decimal": ("decimal",),
    "stdlib-productivity-collections": ("counter",),
    "stdlib-productivity-itertools": ("combinations",),
    "stdlib-productivity-functools": ("lru-cache",),
    "stdlib-productivity-heapq-bisect": ("heappush", "heappop"),
    "regex-patterns": ("regex-fullmatch",),
    "regex-groups": ("regex-fullmatch", "regex-group"),
    "regex-validation": ("regex-fullmatch",),
    "regex-substitution": ("regex-sub",),
    "testing-unit-tests": ("assert",),
    "testing-fixtures": ("function-call", "get", "plus-equals"),
    "testing-parametrize": ("list-comprehension", "unpacking", "comparison", "function-call"),
    "testing-mocks": ("class", "init", "return", "f-string"),
    "quality-pep8": ("sum", "return"),
    "quality-docstrings": ("docstring", "sum", "return"),
    "cli-environment-argv": ("import", "argparse-parser"),
    "cli-environment-environment": ("get",),
    "cli-environment-venv": ("if", "f-string"),
    "http-api-request-response": ("upper", "f-string"),
    "http-api-json-api": ("dict", "default-parameter"),
    "http-api-status-codes": ("if", "comparison"),
    "http-api-pagination": ("slice",),
    "databases-relational": ("unpacking", "dict"),
    "databases-crud": ("int", "f-string"),
    "databases-parameters": ("sql-parameters", "sqlite-fetchone"),
    "databases-transactions": ("copy", "if", "comparison"),
    "concurrency-threads-processes": ("if",),
    "concurrency-thread-pool": ("thread-pool", "pool-map"),
    "concurrency-locks": ("import", "lock", "for", "plus-equals"),
    "concurrency-queues": ("queue", "queue-put", "queue-get", "queue-empty"),
    "async-coroutines": ("import", "async-def", "await", "asyncio-sleep", "asyncio-run"),
    "async-tasks": ("asyncio-create-task",),
    "async-gather-timeouts": ("await", "asyncio-gather"),
    "async-async-design": ("async-def", "await", "asyncio-sleep", "for", "plus-equals"),
    "capstones-task-manager": ("copy", "get", "dict", "return"),
    "capstones-notes-app": ("import", "json-dumps", "json-loads"),
    "capstones-api-client": ("if", "comparison", "get", "f-string"),
    "capstones-release": ("list", "list-comprehension"),
}


def _topic_reference_card(lesson: dict[str, Any]) -> dict[str, str]:
    """Build a reference from the lesson's authored concept and example."""
    first_card = next(
        (card for card in lesson["theory"] if card.get("example")),
        {"text": lesson["subtitle"], "example": ""},
    )
    example = first_card.get("example", "")
    language = first_card.get("language", "python")
    signature = next((line for line in example.splitlines() if line.strip()), "")
    return {
        "name": lesson.get("concepts", [lesson["title"]])[0],
        "kind": "Тема этого урока",
        "signature": signature,
        "description": first_card.get("text", lesson["subtitle"]),
        "example": example,
        "language": language,
    }


def _reference_solution_tool_ids(question: dict[str, Any]) -> tuple[str, ...]:
    """Resolve documented callables used by the hidden author solution."""
    source = question.get("reference_solution", "")
    if not source:
        return ()
    try:
        features = _features_from_tree(ast.parse(source))
    except (SyntaxError, ValueError, TypeError):
        return ()
    local_names = _defined_names(source)
    return tuple(
        tool_id
        for feature, tool_id in SOURCE_FEATURE_TOOL_IDS.items()
        if feature in features
        and not (feature.startswith("call:") and feature.removeprefix("call:") in local_names)
    )


def _question_tool_help(question: dict[str, Any], lesson: dict[str, Any]) -> list[dict[str, str]]:
    authored_tool_ids = (
        QUESTION_TOOL_IDS.get(question["id"])
        or question.get("tool_ids")
        or LESSON_TOOL_IDS.get(lesson["id"], ())
    )
    if not authored_tool_ids:
        authored_tool_ids = tuple(
            tool_id
            for concept in question.get("focus_concepts", lesson.get("concepts", ()))
            for tool_id in CONCEPT_TOOL_IDS.get(concept, ())
        )
    tool_ids = tuple(dict.fromkeys([*authored_tool_ids, *_reference_solution_tool_ids(question)]))
    if tool_ids:
        question["tool_ids"] = list(dict.fromkeys(tool_ids))
    cards = tool_reference_cards(tool_ids)
    if cards:
        return cards
    if question.get("tool_help"):
        return public_tool_help(question["tool_help"])
    return [public_tool_help([_topic_reference_card(lesson)])[0]]


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
            question["tool_help"] = _question_tool_help(question, lesson)
            if kind == "code" and not question["review_concepts"]:
                try:
                    solution_features = _features_from_tree(
                        ast.parse(question.get("reference_solution", ""))
                    )
                except (SyntaxError, ValueError, TypeError):
                    solution_features = set()
                question["review_concepts"] = list(
                    dict.fromkeys(
                        concept
                        for feature in sorted(solution_features)
                        for introduction_id in [FEATURE_INTRODUCTIONS.get(feature)]
                        if introduction_id and introduction_id != lesson["id"]
                        for concept in concepts_by_lesson_id.get(introduction_id, ())
                    )
                )
                question["retrieves"] = list(question["review_concepts"])
            if kind == "code" and "hints" not in question:
                detailed_guide = question.get("guide", "")
                direct_hint = question.get("hint", "")
                has_stdout = any(test.get("kind") == "stdout" for test in question.get("tests", ()))
                task_check = (
                    "Запусти заготовку и сравни консоль с форматом из условия. Найди первое "
                    "место, где расходятся текст или значение."
                    if has_stdout
                    else "Проверка вызовет код с разными данными. Проследи, какое значение должна "
                    "вернуть функция в каждом случае, а не подгоняй один готовый ответ."
                )
                question["hints"] = list(
                    dict.fromkeys(
                        filter(
                            None,
                            (
                                "Забыл точное имя или форму вызова? Открой справочник инструментов "
                                "выше: там указано, что делает каждый нужный метод или функция.",
                                task_check,
                                detailed_guide,
                                direct_hint,
                            ),
                        )
                    )
                )
        concept_history.append(explicit)
        concepts_by_lesson_id[lesson["id"]] = explicit


def _target_contains_unpacking(target: ast.AST) -> bool:
    return isinstance(target, (ast.Tuple, ast.List))


def _function_has_annotations(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg:
        arguments.append(node.args.vararg)
    if node.args.kwarg:
        arguments.append(node.args.kwarg)
    return node.returns is not None or any(
        argument.annotation is not None for argument in arguments
    )


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
            if any(isinstance(argument, ast.Starred) for argument in node.args) or any(
                keyword.arg is None for keyword in node.keywords
            ):
                features.add("syntax:starred-unpacking")

        if isinstance(node, ast.Assign):
            features.add("syntax:assignment")
            if any(_target_contains_unpacking(target) for target in node.targets):
                features.add("syntax:unpacking")
        elif isinstance(node, ast.AnnAssign):
            features.update(("syntax:assignment", "syntax:type-annotation"))
            if _target_contains_unpacking(node.target):
                features.add("syntax:unpacking")
        elif isinstance(node, ast.BinOp):
            features.add("syntax:arithmetic")
            if isinstance(node.op, ast.Mult):
                features.add("operator:multiply")
            elif isinstance(node.op, ast.Div):
                features.add("operator:division")
            elif isinstance(node.op, ast.FloorDiv):
                features.add("operator:floor-division")
            elif isinstance(node.op, ast.Mod):
                features.add("operator:modulo")
        elif isinstance(node, ast.BoolOp):
            features.add("operator:and" if isinstance(node.op, ast.And) else "operator:or")
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            features.add("operator:not")
        elif isinstance(node, ast.JoinedStr):
            features.add("syntax:f-string")
            if any(
                isinstance(part, ast.FormattedValue) and part.format_spec is not None
                for part in node.values
            ):
                features.add("syntax:f-string-format")
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            features.add("syntax:boolean")
        elif isinstance(node, ast.Compare):
            features.add("syntax:comparison")
        elif isinstance(node, ast.IfExp):
            features.add("syntax:conditional-expression")
        elif isinstance(node, ast.Subscript):
            features.add("syntax:subscript")
            if isinstance(node.slice, ast.Slice):
                features.add("syntax:slice")
                if node.slice.step is not None:
                    features.add("syntax:slice-step")
        elif isinstance(node, ast.Constant) and node.value is None:
            features.add("value:none")

        if isinstance(node, ast.If):
            features.add("syntax:if")
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                features.add("syntax:elif")
            elif node.orelse:
                features.add("syntax:else")
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            features.add("syntax:for")
            if node.orelse:
                features.add("syntax:loop-else")
        elif isinstance(node, ast.While):
            features.add("syntax:while")
            if node.orelse:
                features.add("syntax:loop-else")
        elif isinstance(node, ast.Break):
            features.add("syntax:break")
        elif isinstance(node, ast.Continue):
            features.add("syntax:continue")
        elif isinstance(node, ast.AugAssign):
            features.add("syntax:augassign")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            features.add("syntax:function")
            if node.args.posonlyargs or node.args.args or node.args.kwonlyargs:
                features.add("syntax:parameter")
            if node.args.defaults or any(default is not None for default in node.args.kw_defaults):
                features.add("syntax:default-parameter")
            if node.args.vararg or node.args.kwarg:
                features.add("syntax:vararg")
            if node.decorator_list:
                features.add("syntax:decorator")
            if _function_has_annotations(node):
                features.add("syntax:type-annotation")
            if isinstance(node, ast.AsyncFunctionDef):
                features.add("syntax:async")
        elif isinstance(node, ast.Return):
            features.add("syntax:return")
        elif isinstance(node, ast.List):
            features.add("syntax:list")
        elif isinstance(node, ast.Tuple):
            features.add("syntax:tuple")
        elif isinstance(node, ast.Dict):
            features.add("syntax:dict")
        elif isinstance(node, ast.Set):
            features.add("syntax:set")
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            features.add("syntax:with")
        elif isinstance(node, (ast.Try, ast.TryStar)):
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
            if any(generator.ifs for generator in node.generators):
                features.add("syntax:comprehension-filter")
        elif isinstance(node, (ast.DictComp, ast.SetComp)):
            features.add("syntax:dict-comprehension")
            if any(generator.ifs for generator in node.generators):
                features.add("syntax:comprehension-filter")
        elif isinstance(node, ast.GeneratorExp):
            features.add("syntax:generator-expression")
            if any(generator.ifs for generator in node.generators):
                features.add("syntax:comprehension-filter")
        elif isinstance(node, ast.Import):
            features.add("syntax:import")
        elif isinstance(node, ast.ImportFrom):
            features.update(("syntax:import", "syntax:from-import"))
        elif isinstance(node, (ast.Yield, ast.YieldFrom)):
            features.add("syntax:yield")
        elif isinstance(node, ast.Raise):
            features.add("syntax:raise")
        elif isinstance(node, ast.Await):
            features.add("syntax:await")
        elif isinstance(node, ast.Assert):
            features.add("syntax:assert")
        elif isinstance(node, ast.Starred):
            features.add("syntax:starred-unpacking")
    return features


def _parse_features(source: str) -> set[str]:
    try:
        return _features_from_tree(ast.parse(source))
    except (SyntaxError, ValueError, TypeError):
        return set()


def _parse_error(source: str) -> str | None:
    try:
        ast.parse(source)
    except (SyntaxError, ValueError, TypeError) as error:
        if isinstance(error, SyntaxError):
            location = f", строка {error.lineno}" if error.lineno else ""
            return f"{error.msg}{location}"
        return str(error)
    return None


def _fragment_features(source: str) -> set[str]:
    """Parse a Parsons block even when it is only one indented statement."""
    candidates = [source, textwrap.dedent(source), source.strip()]
    stripped = source.strip()
    if stripped.endswith(":"):
        candidates.append(f"{stripped}\n    ...")
    if stripped.startswith(("return", "yield", "raise", "assert")):
        candidates.append(f"def _audit_fragment():\n    {stripped}")
    if stripped.startswith(("break", "continue")):
        candidates.append(f"for _audit_item in ():\n    {stripped}")
    for candidate in dict.fromkeys(candidates):
        features = _parse_features(candidate)
        if features:
            return features
    return set()


_DOTTED_CALL_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:[A-Za-z_][A-Za-z0-9_]*)?\.([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_BARE_CALL_RE = re.compile(r"(?<![.A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_NON_CALL_WORDS = {
    "and",
    "case",
    "class",
    "def",
    "elif",
    "else",
    "for",
    "if",
    "match",
    "not",
    "or",
    "while",
    "with",
}


def _call_like_features(value: str) -> set[str]:
    """Find API spellings in prose too, for example `.lower()` or `len(...)`."""
    features = {f"method:{name}" for name in _DOTTED_CALL_RE.findall(value or "")}
    features.update(
        f"call:{name}" for name in _BARE_CALL_RE.findall(value or "") if name not in _NON_CALL_WORDS
    )
    return features


def _surface_features(source: str, *, fragment: bool = False) -> set[str]:
    features = _fragment_features(source) if fragment else _parse_features(source)
    features.update(_call_like_features(source))
    if any(line.lstrip().startswith("#") for line in source.splitlines()):
        features.add("syntax:comment")
    return features


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


def _lesson_feature_surfaces(lesson: dict[str, Any]) -> Iterable[tuple[str, str, bool]]:
    for card_index, card in enumerate(lesson["theory"], start=1):
        if card.get("language", "python") == "python":
            yield (
                f"theory[{card_index}]",
                card.get("example", ""),
                card.get("language") == "python",
            )
        for field in ("text", "tip"):
            value = card.get(field, "")
            if value:
                yield f"theory[{card_index}].{field}", value, False
            for snippet in _inline_snippets(value):
                yield f"theory[{card_index}].{field}.inline", snippet, False

    for question in lesson["questions"]:
        question_id = question["id"]
        if question.get("starter"):
            yield f"question[{question_id}].starter", question["starter"], False
        if question.get("reference_solution"):
            yield (
                f"question[{question_id}].reference_solution",
                question["reference_solution"],
                True,
            )
        for test_index, test in enumerate(question.get("tests", []), start=1):
            if test.get("call"):
                yield f"question[{question_id}].test[{test_index}]", test["call"], True
        for block_index, block in enumerate(question.get("blocks", ()), start=1):
            block_source = block.get("text", "") if isinstance(block, dict) else str(block)
            yield f"question[{question_id}].block[{block_index}]", block_source, False
        for field in ("prompt", "guide", "hint", "explanation"):
            value = question.get(field, "")
            if value:
                yield f"question[{question_id}].{field}", value, False
            for snippet in _inline_snippets(value):
                yield f"question[{question_id}].{field}.inline", snippet, False
        for hint_index, hint in enumerate(question.get("hints", ()), start=1):
            yield f"question[{question_id}].hints[{hint_index}]", hint, False
            for snippet in _inline_snippets(hint):
                yield f"question[{question_id}].hints[{hint_index}].inline", snippet, False
        for tool_index, tool in enumerate(question.get("tool_help", ()), start=1):
            if tool.get("language", "python") != "python":
                continue
            for field in ("signature", "example"):
                if tool.get(field):
                    yield (
                        f"question[{question_id}].tool_help[{tool_index}].{field}",
                        tool[field],
                        False,
                    )
        for option_index, option in enumerate(question.get("options", []), start=1):
            if re.fullmatch(r"\{[A-Za-z_][A-Za-z0-9_]*\}", option):
                continue
            if _parse_features(option) or _call_like_features(option):
                yield f"question[{question_id}].option[{option_index}]", option, False


def _normalized_code_template(source: str) -> str:
    without_comments = re.sub(r"(?m)^\s*#.*$", "", source or "")
    return "\n".join(line.strip() for line in without_comments.splitlines() if line.strip())


def audit_learning_pipeline(lessons: list[dict[str, Any]]) -> list[str]:
    """Return actionable curriculum violations; an empty list means CI may pass."""
    errors: list[str] = []
    lesson_index = {lesson["id"]: index for index, lesson in enumerate(lessons)}
    introduced_concepts: set[str] = set()
    template_owners: dict[str, list[str]] = {}

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

        lesson_local_names = {
            name
            for source in [
                *(card.get("example", "") for card in lesson["theory"]),
                *(question.get("starter", "") for question in lesson["questions"]),
                *(question.get("reference_solution", "") for question in lesson["questions"]),
            ]
            for name in _defined_names(source)
        }

        for surface, source, declared_python in _lesson_feature_surfaces(lesson):
            if re.search(r"\bpass\b", source):
                errors.append(f"{lesson['id']} {surface}: незнакомая заглушка pass")
            if declared_python and source and (parse_error := _parse_error(source)):
                errors.append(
                    f"{lesson['id']} {surface}: пример объявлен как Python, но не разбирается: "
                    f"{parse_error}"
                )
            source_features = _surface_features(source, fragment=".block[" in surface)
            if surface.endswith(".inline"):
                source_features.discard("syntax:type-annotation")
            if ".option[" in surface:
                source_features.discard("syntax:tuple")
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
            if not question.get("tool_help"):
                errors.append(f"{question['id']}: отсутствует справочник нужных инструментов")
            else:
                for tool_index, tool in enumerate(question["tool_help"], start=1):
                    missing_tool_fields = {
                        "name",
                        "kind",
                        "signature",
                        "description",
                        "example",
                    } - tool.keys()
                    if missing_tool_fields:
                        errors.append(
                            f"{question['id']} tool_help[{tool_index}]: не хватает полей "
                            f"{', '.join(sorted(missing_tool_fields))}"
                        )
                    introduction_id = tool.get("introduced_in")
                    if introduction_id:
                        introduction_index = lesson_index.get(introduction_id)
                        if introduction_index is None:
                            errors.append(
                                f"{question['id']} tool_help[{tool_index}]: отсутствует урок "
                                f"{introduction_id}"
                            )
                        elif index < introduction_index:
                            errors.append(
                                f"{question['id']} tool_help[{tool_index}]: подсказка раньше "
                                f"объяснения в {introduction_id}"
                            )
            if question.get("kind") == "code" and question.get("hints"):
                revealed = _tool_names_revealed_in_hint(
                    question["hints"][0], question.get("tool_help", ())
                )
                if revealed:
                    errors.append(
                        f"{question['id']}: первая подсказка сразу называет инструмент "
                        f"{', '.join(revealed)}"
                    )
            for tool_id in question.get("tool_ids", ()):
                tool = TOOL_CATALOG.get(tool_id)
                if tool is None:
                    errors.append(f"{question['id']}: неизвестный tool_id {tool_id}")
                    continue
                introduction_id = tool["introduced_in"]
                introduction_index = lesson_index.get(introduction_id)
                if introduction_index is None:
                    errors.append(
                        f"{question['id']}: инструмент {tool_id} ссылается на отсутствующий урок "
                        f"{introduction_id}"
                    )
                elif index < introduction_index:
                    errors.append(
                        f"{question['id']}: инструмент {tool_id} раньше объяснения в "
                        f"{introduction_id}"
                    )
            local_names = _defined_names(question.get("starter", "")) | _defined_names(
                question.get("reference_solution", "")
            )
            reference_solution = question.get("reference_solution", "")
            if reference_solution:
                try:
                    reference_features = _features_from_tree(ast.parse(reference_solution))
                except (SyntaxError, ValueError, TypeError):
                    reference_features = set()
                undocumented_callables = {
                    feature
                    for feature in reference_features
                    if feature.startswith(("call:", "method:"))
                    and feature not in SOURCE_FEATURE_TOOL_IDS
                    and feature.split(":", 1)[1] not in local_names
                }
                if undocumented_callables:
                    errors.append(
                        f"{question['id']}: reference_solution использует инструмент без "
                        f"справочной карточки {', '.join(sorted(undocumented_callables))}"
                    )
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
                    and feature.split(":", 1)[1] not in option_local_names | lesson_local_names
                }
                if unknown_option_tools:
                    errors.append(
                        f"{question['id']} option[{option_index}]: незарегистрированный инструмент "
                        f"{', '.join(sorted(unknown_option_tools))}"
                    )
            if question.get("kind") == "parsons" and len(question.get("blocks", ())) < 2:
                errors.append(f"{question['id']}: Parsons-заданию нужно минимум два блока")
            if question.get("kind") == "code":
                lesson_concepts = set(lesson.get("concepts", ()))
                if not lesson_concepts.intersection(question.get("focus_concepts", ())):
                    errors.append(
                        f"{question['id']}: code-задание не связано с концептами своего урока"
                    )
                fingerprint = _normalized_code_template(question.get("starter", ""))
                if fingerprint:
                    template_owners.setdefault(fingerprint, []).append(question["id"])
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

        expected_topic_tools = set(LESSON_TOOL_IDS.get(lesson["id"], ()))
        if expected_topic_tools:
            referenced_tools = {
                tool_id
                for question in lesson["questions"]
                for tool_id in question.get("tool_ids", ())
            }
            if not expected_topic_tools.intersection(referenced_tools):
                errors.append(
                    f"{lesson['id']}: ни одно задание не ссылается на инструменты темы "
                    f"{', '.join(sorted(expected_topic_tools))}"
                )
        introduced_concepts.update(lesson.get("concepts", ()))

    for owners in template_owners.values():
        if len(owners) > 7:
            errors.append(
                "повторяется один и тот же шаблон code-задания более семи раз: " + ", ".join(owners)
            )

    return list(dict.fromkeys(errors))


def _project_feature_surfaces(project: dict[str, Any]) -> Iterable[tuple[str, str, bool]]:
    yield "starter", project.get("starter", ""), True
    yield "reference_solution", project.get("reference_solution", ""), True
    for field in ("description", "subtitle", "success"):
        if project.get(field):
            yield field, project[field], False
    for field in ("skills", "checklist", "hints"):
        for index, value in enumerate(project.get(field, ()), start=1):
            yield f"{field}[{index}]", value, False
    for tool_index, tool in enumerate(project.get("tool_help", ()), start=1):
        for field in ("signature", "example"):
            if tool.get(field):
                yield f"tool_help[{tool_index}].{field}", tool[field], False
    for test_index, test in enumerate(project.get("tests", ()), start=1):
        if test.get("call"):
            yield f"test[{test_index}]", test["call"], True
    for scenario_index, scenario in enumerate(project.get("scenarios", ()), start=1):
        for test_index, test in enumerate(scenario.get("tests", ()), start=1):
            if test.get("call"):
                yield f"scenario[{scenario_index}].test[{test_index}]", test["call"], True


def _tool_names_revealed_in_hint(hint: str, tools: Iterable[dict[str, str]]) -> list[str]:
    """Найти точные имена инструментов в первой направляющей подсказке."""
    lowered = hint.casefold()
    revealed: list[str] = []
    for tool in tools:
        name = tool.get("name", "").casefold().strip()
        base = name.strip(".").removesuffix("()")
        if len(base) >= 3 and re.search(rf"(?<!\w){re.escape(base)}(?!\w)", lowered):
            revealed.append(tool.get("name", base))
    return list(dict.fromkeys(revealed))


def audit_projects(projects: list[dict[str, Any]], lessons: list[dict[str, Any]]) -> list[str]:
    """Check progression, references, hints, and executable surfaces of projects."""
    errors: list[str] = []
    lesson_index = {lesson["id"]: index for index, lesson in enumerate(lessons)}
    orders = [project.get("order") for project in projects]
    if orders != list(range(1, len(projects) + 1)):
        errors.append(
            "projects: order должен быть уникальной последовательностью от 1 без пропусков"
        )

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
        if not project.get("tool_help"):
            errors.append(f"{project_id}: отсутствует справочник нужных инструментов")
        if not project.get("reference_solution"):
            errors.append(f"{project_id}: отсутствует проверяемое эталонное решение")
        if len(project.get("hints", ())) < 2:
            errors.append(f"{project_id}: нужно минимум две постепенные подсказки")
        if len(project.get("checklist", ())) < 2:
            errors.append(f"{project_id}: нужен пошаговый checklist")
        if project.get("hints"):
            revealed = _tool_names_revealed_in_hint(
                project["hints"][0], project.get("tool_help", ())
            )
            if revealed:
                errors.append(
                    f"{project_id}: первая подсказка сразу называет инструмент "
                    f"{', '.join(revealed)}"
                )

        for tool_id in project.get("tool_ids", ()):
            tool = TOOL_CATALOG.get(tool_id)
            if tool is None:
                errors.append(f"{project_id}: неизвестный tool_id {tool_id}")
                continue
            introduction_id = tool["introduced_in"]
            introduction_index = lesson_index.get(introduction_id)
            if introduction_index is None:
                errors.append(
                    f"{project_id}: инструмент {tool_id} ссылается на отсутствующий урок "
                    f"{introduction_id}"
                )
            elif introduction_index > unlock_index:
                errors.append(
                    f"{project_id}: инструмент {tool_id} раньше prerequisite {introduction_id}"
                )

        local_names = _defined_names(project.get("starter", "")) | _defined_names(
            project.get("reference_solution", "")
        )
        registered_calls = {
            feature.removeprefix("call:")
            for feature in FEATURE_INTRODUCTIONS
            if feature.startswith("call:")
        }
        for surface, source, declared_python in _project_feature_surfaces(project):
            if re.search(r"\bpass\b", source):
                errors.append(f"{project_id} {surface}: незнакомая заглушка pass")
            if declared_python and source and (parse_error := _parse_error(source)):
                errors.append(f"{project_id} {surface}: Python не разбирается: {parse_error}")
            for feature in _surface_features(source):
                introduction_id = FEATURE_INTRODUCTIONS.get(feature)
                introduction_index = lesson_index.get(introduction_id) if introduction_id else None
                if introduction_id and introduction_index is None:
                    errors.append(
                        f"{project_id} {surface}: {feature} ссылается на отсутствующий урок "
                        f"{introduction_id}"
                    )
                elif introduction_index is not None and introduction_index > unlock_index:
                    errors.append(
                        f"{project_id} {surface}: {feature} раньше prerequisite {introduction_id}"
                    )
            if surface.startswith(("test[", "scenario[")):
                unknown_calls = _called_names(source) - local_names - registered_calls
                if unknown_calls:
                    errors.append(
                        f"{project_id} {surface}: тест вызывает неизвестное имя "
                        f"{', '.join(sorted(unknown_calls))}"
                    )

        scenarios = project.get("scenarios", [])
        scenario_count = len(scenarios) if scenarios else len(project.get("tests", []))
        if scenario_count < 2:
            errors.append(f"{project_id}: нужно минимум два поведенческих сценария")
    return list(dict.fromkeys(errors))


def audit_exam_coverage(
    exams: dict[str, dict[str, Any]],
    lessons: list[dict[str, Any]],
    assessment_questions: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Validate that module exams mix recall with known, practical transfer."""
    errors: list[str] = []
    lesson_index = {lesson["id"]: index for index, lesson in enumerate(lessons)}
    source_questions = {
        question["id"]: question for lesson in lessons for question in lesson["questions"]
    }
    question_owner: dict[str, tuple[str, str]] = {
        question["id"]: (lesson["module_id"], question["kind"])
        for lesson in lessons
        for question in lesson["questions"]
    }
    for module_id, exam in exams.items():
        question_ids = exam.get("question_ids", ())
        source_question_ids = exam.get("source_question_ids", question_ids)
        mandatory_ids = set(exam.get("mandatory_question_ids", ()))
        if len(question_ids) != len(set(question_ids)):
            errors.append(f"exam {module_id}: вопрос добавлен несколько раз")
        if len(source_question_ids) != len(question_ids):
            errors.append(f"exam {module_id}: assessment-варианты не совпадают с источниками")
            continue
        if "source_question_ids" in exam and set(question_ids) & set(source_question_ids):
            errors.append(f"exam {module_id}: повторно выдаёт ID уже решённых уроковых заданий")
        source_by_delivery = dict(zip(question_ids, source_question_ids, strict=True))
        unknown_ids = set(source_question_ids) - question_owner.keys()
        if unknown_ids:
            errors.append(f"exam {module_id}: неизвестные вопросы {', '.join(sorted(unknown_ids))}")
            continue
        foreign_ids = {
            delivery_id
            for delivery_id, source_id in source_by_delivery.items()
            if question_owner[source_id][0] != module_id
        }
        if foreign_ids:
            errors.append(
                f"exam {module_id}: вопросы из другого модуля {', '.join(sorted(foreign_ids))}"
            )

        if assessment_questions is not None:
            module_lesson_indexes = [
                index for index, lesson in enumerate(lessons) if lesson["module_id"] == module_id
            ]
            module_end_index = max(module_lesson_indexes, default=-1)
            for delivery_id, source_id in source_by_delivery.items():
                delivery = assessment_questions.get(delivery_id)
                source = source_questions.get(source_id)
                if delivery is None or source is None:
                    errors.append(f"exam {module_id}: нет assessment-карточки {delivery_id}")
                    continue
                if source.get("kind") != "code":
                    delivery_prompt = delivery.get("prompt", "")
                    if (
                        source.get("kind") in {"choice", "parsons"}
                        and source.get("prompt") not in delivery_prompt
                    ):
                        errors.append(
                            f"{delivery_id}: контрольный вопрос потерял контекст исходной задачи"
                        )
                    explanation = source.get("explanation", "")
                    if explanation and explanation in delivery_prompt:
                        errors.append(f"{delivery_id}: формулировка раскрывает разбор и ответ")
                    if source.get("kind") == "input":
                        for answer in delivery.get("answers", ()):
                            normalized = str(answer).casefold().strip().strip(".")
                            normalized = normalized.removesuffix("()").strip()
                            if len(normalized) < 3 or normalized.isdecimal():
                                continue
                            if re.search(
                                rf"(?<!\w){re.escape(normalized)}(?!\w)",
                                delivery_prompt.casefold(),
                            ):
                                errors.append(
                                    f"{delivery_id}: формулировка дословно называет "
                                    f"принимаемый ответ {answer!r}"
                                )
                    continue

                delivery_tests = delivery.get("tests", ())
                if any(test.get("kind") in {"source", "ast"} for test in delivery_tests):
                    errors.append(
                        f"{delivery_id}: экзамен требует авторскую форму вместо поведения"
                    )
                source_behavioral = [
                    test
                    for test in source.get("tests", ())
                    if test.get("kind") not in {"source", "ast"}
                ]
                if not any(test not in source_behavioral for test in delivery_tests):
                    errors.append(f"{delivery_id}: нет нового поведенческого transfer-сценария")

                local_names = _defined_names(source.get("starter", "")) | _defined_names(
                    source.get("reference_solution", "")
                )
                registered_calls = {
                    feature.removeprefix("call:")
                    for feature in FEATURE_INTRODUCTIONS
                    if feature.startswith("call:")
                }
                for test_index, test in enumerate(delivery_tests, start=1):
                    call = test.get("call", "")
                    unknown_calls = _called_names(call) - local_names - registered_calls
                    if unknown_calls:
                        errors.append(
                            f"{delivery_id} test[{test_index}]: тест вызывает необъяснённое имя "
                            f"{', '.join(sorted(unknown_calls))}"
                        )
                    for feature in sorted(_surface_features(call) & FEATURE_INTRODUCTIONS.keys()):
                        introduction_id = FEATURE_INTRODUCTIONS[feature]
                        introduction_index = lesson_index.get(introduction_id)
                        if introduction_index is None:
                            errors.append(
                                f"{delivery_id} test[{test_index}]: {feature} ссылается на "
                                f"отсутствующий урок {introduction_id}"
                            )
                        elif module_end_index < introduction_index:
                            errors.append(
                                f"{delivery_id} test[{test_index}]: {feature} раньше объяснения "
                                f"в {introduction_id}"
                            )
        if not mandatory_ids or not mandatory_ids.issubset(question_ids):
            errors.append(f"exam {module_id}: обязательные вопросы не входят в экзамен")
        elif not any(
            question_owner[source_by_delivery[item]][1] in {"code", "parsons"}
            for item in mandatory_ids
        ):
            errors.append(f"exam {module_id}: нет обязательной практической задачи")
    return errors
