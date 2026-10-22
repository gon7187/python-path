"""Рукописные уроки 81–88: collections, itertools, functools, heapq/bisect и re."""

from __future__ import annotations

from typing import Any


def _card(title: str, text: str, example: str, tip: str = "") -> dict[str, str]:
    return {"title": title, "text": text, "example": example, "tip": tip}


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
        "id": "stdlib-productivity-collections",
        "subtitle": "Counter, deque и defaultdict для частых задач",
        "theory": [
            _card(
                "Counter считает повторы",
                "`Counter` — это словарь, который сам считает, сколько раз встретился "
                "каждый элемент. Ты передаёшь ему список или строку, а он хранит пары "
                "«элемент — количество». Это удобнее ручного цикла с проверкой `if key in "
                "counts`. Достать счётчик можно по ключу, как у обычного словаря.",
                "from collections import Counter\n"
                "\n"
                "words = ['кот', 'пёс', 'кот']\n"
                "counts = Counter(words)\n"
                "print(counts['кот'])\n"
                "# Вывод:\n"
                "# 2",
                "Counter не падает на незнакомом ключе: он вернёт 0.",
            ),
            _card(
                "most_common отдаёт частые пары",
                "Метод `most_common(n)` возвращает список из `n` пар «элемент — "
                "количество», начиная с самого частого. Это готовый ответ для задачи "
                "«топ слов»: не нужно сортировать вручную и придумывать, как считать "
                "повторы. Если передать строку целиком, Counter посчитает символы, поэтому "
                "для слов сначала вызывай `split()`.",
                "from collections import Counter\n"
                "\n"
                "text = 'a b a c a b'\n"
                "counts = Counter(text.split())\n"
                "print(counts.most_common(2))\n"
                "# Вывод:\n"
                "# [('a', 3), ('b', 2)]",
                "Порядок при равном количестве сохраняется таким, каким элементы встретились.",
            ),
            _card(
                "Типичная ошибка: считать буквы вместо слов",
                "Если передать в `Counter` строку без `split()`, он разберёт её на "
                "отдельные символы. В результат попадут буквы и пробелы, а не слова. "
                "Заметить ошибку легко: в `most_common` появится пара с пробелом или "
                "однобуквенные ключи. Перед подсчётом слов раздели текст на список.",
                "from collections import Counter\n"
                "\n"
                "text = 'a b a'\n"
                "counts = Counter(text)\n"
                "print(counts.most_common(2))\n"
                "# Вывод:\n"
                "# [('a', 2), (' ', 2)]",
                "Проверь, что попало в Counter: строка или список слов.",
            ),
        ],
        "questions": [
            _choice(
                "stdlib-productivity-collections",
                "Что выведет этот код?\n"
                "from collections import Counter\n"
                "\n"
                "counts = Counter('abca')\n"
                "print(counts['a'])",
                ["2", "1", "3"],
                "2",
                "В строке 'abca' буква 'a' встречается дважды, поэтому Counter вернёт 2.",
            ),
            _term(
                "stdlib-productivity-collections",
                "Какой класс из collections считает, сколько раз встретился элемент?",
                ["Counter", "collections.Counter", "counter", "счётчик"],
                "`Counter` хранит элементы вместе с количеством их повторов.",
            ),
            _code(
                "stdlib-productivity-collections",
                "Напиши `top_words(text, n)`: верни список из `n` самых частых слов "
                "текста, начиная с самого частого. Используй `Counter` и его метод "
                "`most_common`. Слова разделены пробелами.",
                "def top_words(text, n):\n    # верни n самых частых слов\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "top_words('a b a c a b', 2)",
                        "expected": ["a", "b"],
                    },
                    {"kind": "call", "call": "top_words('', 3)", "expected": []},
                    {"kind": "call", "call": "top_words('x y x', 1)", "expected": ["x"]},
                ],
                "from collections import Counter\n"
                "\n"
                "def top_words(text, n):\n"
                "    counts = Counter(text.split())\n"
                "    return [word for word, _ in counts.most_common(n)]\n",
                "Верно: Counter посчитал слова, а most_common(2) выбрал две самые частые пары.",
                "Сначала получи `Counter(text.split())`, затем возьми из результата только слова.",
            ),
        ],
    },
    {
        "id": "stdlib-productivity-itertools",
        "subtitle": "combinations вместо вложенных циклов",
        "theory": [
            _card(
                "combinations собирает пары",
                "`itertools.combinations(items, 2)` перебирает все пары элементов без "
                "повторов и без учёта порядка: пара `('a', 'b')` и `('b', 'a')` — это одна "
                "и та же комбинация. Функция возвращает итератор, поэтому для печати или "
                "дальнейшей работы оберни его в `list()`. Так ты избавляешься от двух "
                "вложенных циклов и ручной проверки индексов.",
                "from itertools import combinations\n"
                "\n"
                "print(list(combinations(['a', 'b', 'c'], 2)))\n"
                "# Вывод:\n"
                "# [('a', 'b'), ('a', 'c'), ('b', 'c')]",
                "combinations не повторяет элемент на той же позиции.",
            ),
            _card(
                "Пары удобно обходить в цикле",
                "Результат `combinations` можно сразу передать в `for`: на каждом шаге "
                "ты получаешь кортеж из двух элементов. Внутри цикла с ним работают как с "
                "обычным кортежем — распаковывают в две переменные или передают в функцию. "
                "Этот приём подходит для сравнения всех пар, построения графа или проверки "
                "сочетаний.",
                "from itertools import combinations\n"
                "\n"
                "for left, right in combinations(['x', 'y', 'z'], 2):\n"
                "    print(left + right)\n"
                "# Вывод:\n"
                "# xy\n"
                "# xz\n"
                "# yz",
                "Итератор расходуется один раз: сохрани результат в list, если нужен повторно.",
            ),
            _card(
                "Типичная ошибка: ждать обратный порядок",
                "`combinations` не создаёт перестановки. Для двух элементов она вернёт "
                "только `('a', 'b')`, но не `('b', 'a')`. Если задача требует учитывать "
                "порядок, нужен `itertools.permutations`. Ошибку видно по количеству "
                "результатов: у combinations их меньше, чем у permutations.",
                "from itertools import combinations\n"
                "\n"
                "print(list(combinations(['a', 'b'], 2)))\n"
                "# Вывод:\n"
                "# [('a', 'b')]",
                "Спроси себя: порядок элементов важен или нет.",
            ),
        ],
        "questions": [
            _choice(
                "stdlib-productivity-itertools",
                "Что выведет этот код?\n"
                "from itertools import combinations\n"
                "\n"
                "print(len(list(combinations([1, 2, 3, 4], 2))))",
                ["6", "5", "4"],
                "6",
                "Из четырёх элементов можно составить шесть разных пар: 4 * 3 / 2 = 6.",
            ),
            _term(
                "stdlib-productivity-itertools",
                "Сколько пар вернёт combinations([1, 2, 3], 2)?",
                ["3", "три"],
                "Пары такие: (1, 2), (1, 3) и (2, 3) — всего три.",
            ),
            _code(
                "stdlib-productivity-itertools",
                "Напиши `pairs(items)`: верни список всех пар элементов по два без "
                "повторов и без учёта порядка. Используй `itertools.combinations`.",
                "def pairs(items):\n    # верни все пары по два\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "pairs([1, 2, 3]) == [(1, 2), (1, 3), (2, 3)]",
                        "expected": True,
                    },
                    {"kind": "call", "call": "pairs([1]) == []", "expected": True},
                    {"kind": "call", "call": "pairs([]) == []", "expected": True},
                ],
                "from itertools import combinations\n"
                "\n"
                "def pairs(items):\n"
                "    return list(combinations(items, 2))\n",
                "Верно: combinations перебрал пары без повторов, а list сделал результат списком.",
                "Верни `list(combinations(items, 2))`.",
            ),
        ],
    },
    {
        "id": "stdlib-productivity-functools",
        "subtitle": "reduce сворачивает список в одно значение",
        "theory": [
            _card(
                "reduce сворачивает список",
                "`functools.reduce` идёт по списку слева направо: берёт два первых "
                "элемента, применяет к ним функцию, затем берёт результат и следующий "
                "элемент — и так до конца. В итоге список превращается в одно значение. "
                "Так можно посчитать сумму или произведение без цикла и промежуточной "
                "переменной. Функция должна принимать два аргумента и возвращать один.",
                "from functools import reduce\n"
                "\n"
                "numbers = [1, 2, 3, 4]\n"
                "print(reduce(lambda a, b: a + b, numbers))\n"
                "# Вывод:\n"
                "# 10",
                "Свёртка идёт слева направо: reduce(f, [a, b, c]) — это f(f(a, b), c).",
            ),
            _card(
                "Начальное значение задаёт старт",
                "Третий аргумент `reduce` — начальное значение. Оно становится первым "
                "аргументом первого вызова, а для пустого списка сразу становится "
                "результатом. Для суммы это обычно `0`, для произведения — `1`. Тип "
                "результата задаёт сама функция: начальное значение только участвует "
                "в первом вызове.",
                "from functools import reduce\n"
                "\n"
                "numbers = [2, 3, 4]\n"
                "product = reduce(lambda a, b: a * b, numbers, 1)\n"
                "print(product)\n"
                "# Вывод:\n"
                "# 24",
                "Для произведения начальное значение 1, а не 0.",
            ),
            _card(
                "Типичная ошибка: начать произведение с нуля",
                "Если поставить начальным значением `0`, умножение сразу обнулит всё: "
                "ноль, умноженный на любое число, остаётся нулём. Для пустого списка "
                "результат тоже будет 0 вместо ожидаемой единицы. Заметишь ошибку по "
                "ответу: произведение положительных чисел вдруг равно нулю.",
                "from functools import reduce\n"
                "\n"
                "numbers = [2, 3, 4]\n"
                "print(reduce(lambda a, b: a * b, numbers, 0))\n"
                "# Вывод:\n"
                "# 0",
                "Проверь начальное значение: для умножения нужна единица.",
            ),
        ],
        "questions": [
            _choice(
                "stdlib-productivity-functools",
                "Что выведет этот код?\n"
                "from functools import reduce\n"
                "\n"
                "print(reduce(lambda a, b: a + b, [1, 2, 3], 10))",
                ["16", "15", "10"],
                "16",
                "reduce начнёт с 10: 10 + 1 + 2 + 3 = 16.",
            ),
            _term(
                "stdlib-productivity-functools",
                "Что вернёт reduce с пустым списком и начальным значением 1?",
                ["1", "единица", "единицу"],
                "Пустой список не даёт элементов, поэтому reduce возвращает начальное значение.",
            ),
            _code(
                "stdlib-productivity-functools",
                "Напиши `product(nums)`: верни произведение всех чисел. Используй "
                "`functools.reduce`. Для пустого списка верни 1.",
                "def product(nums):\n    # верни произведение чисел\n    pass\n",
                [
                    {"kind": "call", "call": "product([2, 3, 4])", "expected": 24},
                    {"kind": "call", "call": "product([])", "expected": 1},
                    {"kind": "call", "call": "product([7])", "expected": 7},
                ],
                "from functools import reduce\n"
                "\n"
                "def product(nums):\n"
                "    return reduce(lambda a, b: a * b, nums, 1)\n",
                "Верно: reduce перемножил числа, а начальная единица дала 1 для пустого списка.",
                "Передай в reduce функцию `lambda a, b: a * b` и начальное значение 1.",
            ),
        ],
    },
    {
        "id": "stdlib-productivity-heapq-bisect",
        "subtitle": "Приоритеты и место в отсортированном списке",
        "theory": [
            _card(
                "heapq достаёт минимум",
                "`heapq` хранит список так, чтобы самый маленький элемент всегда был "
                "первым. `heappush` добавляет элемент, `heappop` забирает минимальный. "
                "Если нужно просто выбрать несколько самых маленьких значений, "
                "`heapq.nsmallest(n, items)` сделает это без ручной сортировки всего "
                "списка.",
                "import heapq\n"
                "\n"
                "numbers = [5, 1, 4, 2]\n"
                "print(heapq.nsmallest(2, numbers))\n"
                "# Вывод:\n"
                "# [1, 2]",
                "nsmallest возвращает отсортированный список, а не кучу.",
            ),
            _card(
                "bisect держит список отсортированным",
                "`bisect.insort` находит место для нового элемента в уже отсортированном "
                "списке и вставляет его туда. Список остаётся отсортированным, а тебе не "
                "нужно вызывать `sort()` после каждой вставки. `bisect_left` и "
                "`bisect_right` подсказывают индекс, куда встанет значение.",
                "import bisect\n"
                "\n"
                "numbers = [1, 3, 5]\n"
                "bisect.insort(numbers, 4)\n"
                "print(numbers)\n"
                "# Вывод:\n"
                "# [1, 3, 4, 5]",
                "insort работает только со списком, который уже отсортирован.",
            ),
            _card(
                "Типичная ошибка: heappop без heapify",
                "`heappop` не проверяет, является ли список кучей. Если передать обычный "
                "список, функция вернёт не минимальный элемент, а первый по внутреннему "
                "устройству. Заметишь ошибку по ответу: минимум остался в списке, а "
                "вернулось большое число. Сначала вызови `heapq.heapify(items)`.",
                "import heapq\n"
                "\n"
                "numbers = [5, 1, 4, 2]\n"
                "print(heapq.heappop(numbers))\n"
                "# Вывод:\n"
                "# 5",
                "Перед heappop убедись, что список превращён в кучу.",
            ),
        ],
        "questions": [
            _choice(
                "stdlib-productivity-heapq-bisect",
                "Что выведет этот код?\n"
                "import bisect\n"
                "\n"
                "numbers = [10, 20, 30]\n"
                "print(bisect.bisect_left(numbers, 20))",
                ["1", "0", "2"],
                "1",
                "20 стоит на индексе 1, поэтому bisect_left вернёт 1.",
            ),
            _term(
                "stdlib-productivity-heapq-bisect",
                "Какая функция heapq возвращает n самых маленьких элементов?",
                ["nsmallest", "heapq.nsmallest", "n smallest"],
                "`heapq.nsmallest(n, items)` выбирает n минимальных значений.",
            ),
            _code(
                "stdlib-productivity-heapq-bisect",
                "Напиши `smallest(items, n)`: верни список из `n` самых маленьких "
                "элементов по возрастанию. Используй `heapq.nsmallest`.",
                "def smallest(items, n):\n    # верни n самых маленьких элементов\n    pass\n",
                [
                    {"kind": "call", "call": "smallest([5, 1, 4, 2], 2)", "expected": [1, 2]},
                    {"kind": "call", "call": "smallest([], 3)", "expected": []},
                    {
                        "kind": "call",
                        "call": "smallest([3, 1, 2], 10)",
                        "expected": [1, 2, 3],
                    },
                ],
                "import heapq\n\ndef smallest(items, n):\n    return heapq.nsmallest(n, items)\n",
                "Верно: nsmallest выбрал два минимума и вернул их по возрастанию.",
                "Верни `heapq.nsmallest(n, items)`.",
            ),
        ],
    },
    {
        "id": "regex-patterns",
        "subtitle": "Литералы, классы и квантификаторы",
        "theory": [
            _card(
                "Шаблон ищет форму текста",
                "Регулярное выражение описывает, как выглядит нужный фрагмент. `re.search` "
                "ищет первое совпадение в любом месте строки и возвращает объект `Match`. "
                "В шаблоне `\\d` означает одну цифру, `\\w` — букву или цифру, а обычные "
                "символы совпадают сами с собой. Пиши шаблон в raw-строке `r'...'`, чтобы "
                "обратные слеши не пришлось удваивать.",
                "import re\n"
                "\n"
                "text = 'заказ 42 готов'\n"
                "match = re.search(r'\\d+', text)\n"
                "print(match.group())\n"
                "# Вывод:\n"
                "# 42",
                "Группа без скобок — это всё найденное совпадение.",
            ),
            _card(
                "findall собирает все совпадения",
                "`re.findall` возвращает список всех фрагментов, которые подошли под "
                "шаблон. Это удобно, когда нужно вытащить из текста все числа, слова или "
                "коды сразу. Если в шаблоне есть скобки-группы, findall вернёт только их "
                "содержимое, поэтому для целых чисел скобки не нужны.",
                "import re\n"
                "\n"
                "text = 'в 2024 году 12 месяцев'\n"
                "print(re.findall(r'\\d+', text))\n"
                "# Вывод:\n"
                "# ['2024', '12']",
                "findall возвращает строки, даже если внутри только цифры.",
            ),
            _card(
                "Типичная ошибка: забыть квантификатор",
                "`\\d` совпадает ровно с одной цифрой. Без `+` или `{4}` шаблон найдёт "
                "каждую цифру отдельно, и вместо числа 2024 ты получишь четыре строки. "
                "Заметь ошибку по длине результата: элементов стало столько же, сколько "
                "цифр. Квантификатор `+` означает «один или больше».",
                "import re\n"
                "\n"
                "text = 'год 2024'\n"
                "print(re.findall(r'\\d', text))\n"
                "# Вывод:\n"
                "# ['2', '0', '2', '4']",
                "Сравни `\\d` и `\\d+`: плюс склеивает соседние цифры в одно число.",
            ),
        ],
        "questions": [
            _choice(
                "regex-patterns",
                "Что выведет этот код?\n"
                "import re\n"
                "\n"
                "print(re.findall(r'\\d+', 'дом 7, квартира 12'))",
                ["['7', '12']", "['12', '7']", "['7', '1']"],
                "['7', '12']",
                "findall идёт по тексту слева направо и возвращает числа строками: 7, затем 12.",
            ),
            _term(
                "regex-patterns",
                "Какая функция re возвращает список всех совпадений?",
                ["findall", "re.findall", "find all"],
                "`re.findall` собирает все подходящие фрагменты в список.",
            ),
            _code(
                "regex-patterns",
                "Напиши `find_numbers(text)`: верни список всех целых чисел из текста "
                "как `int`. Используй `re.findall`. Если чисел нет, верни пустой список.",
                "def find_numbers(text):\n    # верни все числа как int\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "find_numbers('в 2024 году 12 месяцев')",
                        "expected": [2024, 12],
                    },
                    {"kind": "call", "call": "find_numbers('нет')", "expected": []},
                    {"kind": "call", "call": "find_numbers('0 и 7')", "expected": [0, 7]},
                ],
                "import re\n"
                "\n"
                "def find_numbers(text):\n"
                "    return [int(value) for value in re.findall(r'\\d+', text)]\n",
                "Верно: findall нашёл числа строками, а int превратил каждое в число.",
                "Найди `re.findall(r'\\d+', text)` и примени `int` к каждому элементу.",
            ),
        ],
    },
    {
        "id": "regex-groups",
        "subtitle": "Достаём части совпадения по имени",
        "theory": [
            _card(
                "Группа выделяет часть совпадения",
                "Скобки в шаблоне создают группы. Всё совпадение целиком доступно как "
                "`group(0)`, а каждая группа — по номеру начиная с единицы. В шаблоне "
                "`(\\d{4})-(\\d{2})` первая группа — год, вторая — месяц. Группы позволяют "
                "одним проходом разобрать строку на части, не разрезая её вручную.",
                "import re\n"
                "\n"
                "text = 'дата: 2024-05-17'\n"
                "match = re.search(r'(\\d{4})-(\\d{2})-(\\d{2})', text)\n"
                "print(match.group(1))\n"
                "# Вывод:\n"
                "# 2024",
                "Нумерация групп идёт по открывающим скобкам слева направо.",
            ),
            _card(
                "Именованные группы читаются как словарь",
                "Вместо номеров группе можно дать имя: `(?P<year>\\d{4})`. Тогда результат "
                "достаётся через `group('year')`, а `groupdict()` возвращает все группы "
                "словарём. Имена делают сложный шаблон понятнее: через месяц ты не будешь "
                "вспоминать, что группа номер два — это день.",
                "import re\n"
                "\n"
                "text = 'дата: 2024-05-17'\n"
                "pattern = r'(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})'\n"
                "match = re.search(pattern, text)\n"
                "print(match.groupdict())\n"
                "# Вывод:\n"
                "# {'year': '2024', 'month': '05', 'day': '17'}",
                "Значения групп остаются строками: для чисел нужен int.",
            ),
            _card(
                "Типичная ошибка: group(0) вместо group(1)",
                "`group(0)` возвращает всё совпадение, а не первую часть. Если попросить "
                "год через `group(0)`, получишь всю дату целиком. Ошибку видно по "
                "результату: вместо четырёх цифр приходит строка с дефисами. Проверь "
                "номер или используй имя группы.",
                "import re\n"
                "\n"
                "match = re.search(r'(\\d{4})-(\\d{2})', '2024-05')\n"
                "print(match.group(0))\n"
                "# Вывод:\n"
                "# 2024-05",
                "group(0) — это совпадение целиком, группы начинаются с 1.",
            ),
        ],
        "questions": [
            _choice(
                "regex-groups",
                "Что выведет этот код?\n"
                "import re\n"
                "\n"
                "match = re.search(r'(?P<a>\\d+)-(?P<b>\\d+)', '12-7')\n"
                "print(match.group('b'))",
                ["7", "12", "-"],
                "7",
                "Группа с именем 'b' — это вторая часть после дефиса, то есть 7.",
            ),
            _term(
                "regex-groups",
                "Какой метод Match возвращает все именованные группы словарём?",
                ["groupdict", "groupdict()", "группдикт"],
                "`groupdict()` собирает именованные группы в словарь.",
            ),
            _code(
                "regex-groups",
                "Напиши `parse_date(text)`: найди дату вида `2024-05-17` и верни словарь "
                "`{'year': 2024, 'month': 5, 'day': 17}`. Используй именованные группы "
                "`(?P<...>)`. Если даты нет, верни `None`.",
                "def parse_date(text):\n    # разбери дату по именованным группам\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "parse_date('дата: 2024-05-17')",
                        "expected": {"year": 2024, "month": 5, "day": 17},
                    },
                    {"kind": "call", "call": "parse_date('без даты')", "expected": None},
                    {
                        "kind": "call",
                        "call": "parse_date('2024-01-01')",
                        "expected": {"year": 2024, "month": 1, "day": 1},
                    },
                ],
                "import re\n"
                "\n"
                "def parse_date(text):\n"
                "    pattern = r'(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})'\n"
                "    match = re.search(pattern, text)\n"
                "    if match is None:\n"
                "        return None\n"
                "    return {\n"
                "        'year': int(match.group('year')),\n"
                "        'month': int(match.group('month')),\n"
                "        'day': int(match.group('day')),\n"
                "    }\n",
                "Верно: именованные группы нашли части даты, а int убрал ведущие нули.",
                "Сначала проверь `match is None`, затем собери словарь из трёх групп.",
            ),
        ],
    },
    {
        "id": "regex-validation",
        "subtitle": "fullmatch проверяет формат целиком",
        "theory": [
            _card(
                "fullmatch проверяет всю строку",
                "`re.fullmatch` возвращает совпадение только тогда, когда шаблон покрывает "
                "строку от начала до конца. Это главный инструмент проверки формата: "
                "почтового индекса, кода, телефона. `re.search` ищет фрагмент где угодно и "
                "для валидации не подходит. Сравнивай результат с `None`, чтобы получить "
                "`True` или `False`.",
                "import re\n"
                "\n"
                "code = '123456'\n"
                "print(re.fullmatch(r'\\d{6}', code) is not None)\n"
                "# Вывод:\n"
                "# True",
                "Квантификатор `{6}` требует ровно шесть цифр.",
            ),
            _card(
                "Шаблон телефона целиком",
                "Для телефона запиши все части формата: код страны, пробел, три цифры, "
                "пробел, три цифры, дефис, две цифры, дефис и ещё две. Символ `+` в начале "
                "нужно экранировать: `\\+`. Такой шаблон в `fullmatch` пропустит только "
                "строку, полностью собранную по этому образцу.",
                "import re\n"
                "\n"
                "phone = '+7 999 123-45-67'\n"
                "pattern = r'\\+7 \\d{3} \\d{3}-\\d{2}-\\d{2}'\n"
                "print(re.fullmatch(pattern, phone) is not None)\n"
                "# Вывод:\n"
                "# True",
                "Пробелы и дефисы в шаблоне тоже обязательны.",
            ),
            _card(
                "Типичная ошибка: search вместо fullmatch",
                "`re.search` находит совпадение в любом месте строки. Если искать три "
                "цифры подряд, проверку пройдёт даже номер без плюса и пробелов: ведь три "
                "цифры в нём есть. Ошибка опасна тем, что неверные данные выглядят "
                "принятыми. Замени `search` на `fullmatch`, чтобы проверялась вся строка.",
                "import re\n"
                "\n"
                "phone = '89991234567'\n"
                "print(re.search(r'\\d{3}', phone) is not None)\n"
                "# Вывод:\n"
                "# True",
                "Формат проверяют только fullmatch, а не поиск подстроки.",
            ),
        ],
        "questions": [
            _choice(
                "regex-validation",
                "Что выведет этот код?\n"
                "import re\n"
                "\n"
                "print(re.fullmatch(r'\\d{2}', '12') is not None)",
                ["True", "False", "None"],
                "True",
                "Строка '12' целиком состоит из двух цифр, поэтому fullmatch её принимает.",
            ),
            _term(
                "regex-validation",
                "Какая функция re проверяет совпадение со всей строкой целиком?",
                ["fullmatch", "re.fullmatch", "full match"],
                "`re.fullmatch` требует, чтобы шаблон покрыл строку полностью.",
            ),
            _code(
                "regex-validation",
                "Напиши `is_phone(text)`: верни `True`, если строка целиком похожа на "
                "телефон `+7 999 123-45-67`, иначе `False`. Используй `re.fullmatch`.",
                "def is_phone(text):\n    # проверь формат телефона целиком\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "is_phone('+7 999 123-45-67')",
                        "expected": True,
                    },
                    {"kind": "call", "call": "is_phone('89991234567')", "expected": False},
                    {
                        "kind": "call",
                        "call": "is_phone('+7 999 123-45-678')",
                        "expected": False,
                    },
                ],
                "import re\n"
                "\n"
                "def is_phone(text):\n"
                "    pattern = r'\\+7 \\d{3} \\d{3}-\\d{2}-\\d{2}'\n"
                "    return re.fullmatch(pattern, text) is not None\n",
                "Верно: fullmatch проверил всю строку, а `is not None` дал True или False.",
                "Верни `re.fullmatch(pattern, text) is not None`.",
            ),
        ],
    },
    {
        "id": "regex-substitution",
        "subtitle": "sub заменяет, split делит по шаблону",
        "theory": [
            _card(
                "sub заменяет совпадения",
                "`re.sub(pattern, replacement, text)` заменяет все части строки, которые "
                "подошли под шаблон. Замена может быть обычной строкой или ссылкой на "
                "группу. В отличие от `str.replace`, шаблон описывает не точный текст, а "
                "форму: например, любое число. Результат — новая строка, исходная не "
                "меняется.",
                "import re\n\nprint(re.sub(r'\\d+', '#', 'заказ 42 и 7'))\n# Вывод:\n# заказ # и #",
                "Без флага count подставляется каждое совпадение.",
            ),
            _card(
                "Нормализация пробелов",
                "Комбинация `\\s+` и `sub` превращает любые пробельные последовательности "
                "— пробелы, табы, переводы строк — в один пробел. Остаётся убрать пробелы "
                "по краям методом `strip()`. Такой приём часто нужен перед сравнением "
                "пользовательского текста или сохранением его в базу.",
                "import re\n"
                "\n"
                "text = '  a \\t b\\n c '\n"
                "print(re.sub(r'\\s+', ' ', text).strip())\n"
                "# Вывод:\n"
                "# a b c",
                "`\\s` включает tab и перевод строки, а не только пробел.",
            ),
            _card(
                "Типичная ошибка: заменить один пробел",
                "Шаблон `r' '` совпадает ровно с одним пробелом. Если в тексте их два "
                "подряд, замена оставит второй, и двойные пробелы сохранятся. Ошибку видно "
                "по результату: между словами всё ещё больше одного пробела. Для любых "
                "последовательностей используй `r'\\s+'`.",
                "import re\n"
                "\n"
                "text = 'a  b   c'\n"
                "print(re.sub(r' ', ' ', text))\n"
                "# Вывод:\n"
                "# a  b   c",
                "Одиночный пробел в шаблоне не знает о соседних пробелах.",
            ),
        ],
        "questions": [
            _choice(
                "regex-substitution",
                "Что выведет этот код?\nimport re\n\nprint(re.sub(r'\\s+', '-', 'a  b c'))",
                ["a-b-c", "a--b-c", "a b c"],
                "a-b-c",
                "Шаблон `\\s+` забирает все пробелы подряд и меняет каждый набор на один дефис.",
            ),
            _term(
                "regex-substitution",
                "Какая функция re заменяет все совпадения шаблона?",
                ["sub", "re.sub", "замена"],
                "`re.sub` подставляет новое значение вместо каждого совпадения.",
            ),
            _code(
                "regex-substitution",
                "Напиши `normalize_spaces(text)`: замени любые последовательности "
                "пробельных символов одним пробелом и убери пробелы по краям. Используй "
                "`re.sub`.",
                "def normalize_spaces(text):\n    # приведи пробелы к одному\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "normalize_spaces('  a \\t b\\n c ')",
                        "expected": "a b c",
                    },
                    {"kind": "call", "call": "normalize_spaces('')", "expected": ""},
                    {"kind": "call", "call": "normalize_spaces('a')", "expected": "a"},
                ],
                "import re\n"
                "\n"
                "def normalize_spaces(text):\n"
                "    return re.sub(r'\\s+', ' ', text).strip()\n",
                "Верно: sub собрал все пробельные серии в один пробел, strip убрал края.",
                "Сначала `re.sub(r'\\s+', ' ', text)`, затем `.strip()`.",
            ),
        ],
    },
]
