"""Рукописные уроки 49–56: итераторы, генераторы, модули и пакеты."""

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
    theory: list[dict[str, str]],
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
        "iterators-iterable",
        "Кто хранит данные, а кто выдаёт следующий элемент",
        [
            _card(
                "Iterable хранит, iterator выдаёт",
                "Список, строка и range — это iterable: по ним можно пройти циклом. "
                "Но сам список не помнит, на каком месте ты остановился. Итератор — "
                "отдельный объект, который выдаёт по одному элементу и хранит текущую "
                "позицию. Его создаёт встроенная функция iter(), а next() забирает "
                "следующий элемент.",
                "numbers = [10, 20]\n"
                "iterator = iter(numbers)\n"
                "print(next(iterator))\n"
                "# Вывод:\n"
                "# 10",
                "iter() не копирует список, а создаёт отдельный объект чтения.",
            ),
            _card(
                "Итератор помнит, где остановился",
                "Когда итератор создан, он живёт отдельно от списка. Каждый next() "
                "сдвигает его вперёд, а цикл for забирает остаток. Поэтому после одного "
                "next() цикл начнётся со второго элемента, а не с первого. Так удобно "
                "прочитать заголовок, а потом обработать остальные строки.",
                "letters = iter('abc')\n"
                "print(next(letters))\n"
                "for letter in letters:\n"
                "    print(letter)\n"
                "# Вывод:\n"
                "# a\n"
                "# b\n"
                "# c",
                "Один и тот же итератор нельзя пройти дважды: позиция не сбрасывается.",
            ),
            _card(
                "Типичная ошибка: next() на списке",
                "next() работает только с итератором. Если передать ему список, Python "
                "бросит TypeError: 'list' object is not an iterator. Ошибка заметна "
                "сразу по тексту исключения. Исправление простое: сначала вызови "
                "iter(numbers), а уже потом next().",
                "numbers = [10, 20]\n"
                "try:\n"
                "    next(numbers)\n"
                "except TypeError:\n"
                "    print('нужен iter(numbers)')\n"
                "# Вывод:\n"
                "# нужен iter(numbers)",
                "Список — iterable, но не iterator: ему нужен iter().",
            ),
        ],
        [
            _choice(
                "iterators-iterable",
                "Что выведет этот код?\n"
                "numbers = [1, 2, 3]\n"
                "iterator = iter(numbers)\n"
                "print(next(iterator), next(iterator))",
                ["1 2", "2 3", "1 3", "3 2"],
                "1 2",
                "Первый next() вернул 1, второй сдвинул итератор и вернул 2.",
            ),
            _term(
                "iterators-iterable",
                "Какая встроенная функция возвращает итератор из списка?",
                ["iter", "iter()", "функция iter"],
                "iter(numbers) создаёт итератор, у которого работает next().",
            ),
            _code(
                "iterators-iterable",
                "Напиши `take(iterable, n)`: верни список из первых n элементов. Бери "
                "элементы через `iter()` и `next()`, без срезов. Если элементов меньше, "
                "верни сколько есть. Работать должно и с генератором.",
                "def take(iterable, n):\n    # верни первые n элементов\n    pass\n",
                [
                    {"kind": "call", "call": "take('abc', 2)", "expected": ["a", "b"]},
                    {
                        "kind": "call",
                        "call": "take((c for c in 'abc'), 2)",
                        "expected": ["a", "b"],
                    },
                    {"kind": "call", "call": "take(range(10), 3)", "expected": [0, 1, 2]},
                    {"kind": "call", "call": "take([1], 5)", "expected": [1]},
                ],
                "def take(iterable, n):\n"
                "    iterator = iter(iterable)\n"
                "    result = []\n"
                "    for _ in range(n):\n"
                "        try:\n"
                "            result.append(next(iterator))\n"
                "        except StopIteration:\n"
                "            break\n"
                "    return result\n",
                "Верно: iter() создаёт итератор, next() выдаёт элементы, а "
                "StopIteration завершает короткую последовательность.",
                "Заведи пустой список и цикл range(n); внутри вызывай next() и лови StopIteration.",
            ),
        ],
    ),
    _lesson(
        "iterators-stop-iteration",
        "StopIteration и запасное значение next",
        [
            _card(
                "StopIteration сообщает о конце",
                "Итератор не знает заранее, когда закончится. Когда элементы кончились, "
                "next() бросает исключение StopIteration. Это не поломка, а сигнал "
                "«больше нет». Цикл for ловит его сам и поэтому останавливается без "
                "ошибки.",
                "iterator = iter(['яблоко'])\n"
                "print(next(iterator))\n"
                "try:\n"
                "    next(iterator)\n"
                "except StopIteration:\n"
                "    print('элементы кончились')\n"
                "# Вывод:\n"
                "# яблоко\n"
                "# элементы кончились",
                "StopIteration — штатный конец итератора, а не сбой программы.",
            ),
            _card(
                "У next() есть запасное значение",
                "Второй аргумент next() задаёт значение по умолчанию. Если элементы "
                "кончились, next(iterator, default) вернёт default и не бросит "
                "StopIteration. Это удобно, когда отсутствие элемента — нормальная "
                "ситуация. Например, так читают необязательный заголовок.",
                "iterator = iter([])\n"
                "print(next(iterator, 'пусто'))\n"
                "print(next(iter([1, 2]), 0))\n"
                "# Вывод:\n"
                "# пусто\n"
                "# 1",
                "Значение по умолчанию спасает от лишнего try/except.",
            ),
            _card(
                "Типичная ошибка: next() без обработки",
                "Если вызывать next() в цикле while и не ловить StopIteration, программа "
                "упадёт с traceback на последнем шаге. Ошибка видна по строке "
                "StopIteration в конце вывода. Либо используй for, либо возьми "
                "next(iterator, default), либо оберни вызов в try/except.",
                "iterator = iter([1])\n"
                "try:\n"
                "    while True:\n"
                "        print(next(iterator))\n"
                "except StopIteration:\n"
                "    print('готово')\n"
                "# Вывод:\n"
                "# 1\n"
                "# готово",
                "После последнего элемента next() бросает StopIteration.",
            ),
        ],
        [
            _choice(
                "iterators-stop-iteration",
                "Что выведет этот код?\n"
                "iterator = iter([7])\n"
                "print(next(iterator, 0))\n"
                "print(next(iterator, 0))",
                ["7\n0", "7\n7", "0\n7", "0\n0"],
                "7\n0",
                "Первый вызов вернул 7, второй упёрся в конец и вернул запасной 0.",
            ),
            _term(
                "iterators-stop-iteration",
                "Какое исключение бросает next(), когда элементы закончились?",
                ["StopIteration", "StopIteration()", "исключение StopIteration"],
                "StopIteration — сигнал конца итератора; for перехватывает его сам.",
            ),
            _code(
                "iterators-stop-iteration",
                "Напиши `safe_next(iterator, default)`: верни следующий элемент, а если "
                "итератор закончился — default. Используй try/except StopIteration.",
                "def safe_next(iterator, default):\n    # верни next или default\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "(lambda it: [safe_next(it, 0), safe_next(it, 0)])(iter([1]))",
                        "expected": [1, 0],
                    },
                    {
                        "kind": "call",
                        "call": "safe_next(iter([]), 'пусто')",
                        "expected": "пусто",
                    },
                ],
                "def safe_next(iterator, default):\n"
                "    try:\n"
                "        return next(iterator)\n"
                "    except StopIteration:\n"
                "        return default\n",
                "Верно: первый next() отдаёт элемент, второй ловит StopIteration и "
                "возвращает default.",
                "Оберни next(iterator) в try, а в except StopIteration верни default.",
            ),
        ],
    ),
    _lesson(
        "iterators-yield",
        "Функция, которая выдаёт значения по одному",
        [
            _card(
                "yield превращает функцию в генератор",
                "Функция с yield не выполняется сразу целиком. При вызове она возвращает "
                "генератор: объект, который выдаёт значения по одному. Каждый next() "
                "запускает функцию до следующего yield и приостанавливает её. Так можно "
                "описать последовательность, не строя весь список в памяти.",
                "def count_up(limit):\n"
                "    for value in range(1, limit + 1):\n"
                "        yield value\n"
                "\n"
                "print(list(count_up(3)))\n"
                "# Вывод:\n"
                "# [1, 2, 3]",
                "list() забирает из генератора все значения до конца.",
            ),
            _card(
                "Генератор выдаёт значения по требованию",
                "Генератор удобно читать через for: цикл сам вызывает next() и "
                "останавливается, когда функция закончилась. Можно и вручную: первый "
                "next() вернёт первое значение и замрёт на yield. Второй next() продолжит "
                "с того же места. Поэтому генератор подходит для больших потоков данных.",
                "def letters():\n"
                "    yield 'a'\n"
                "    yield 'b'\n"
                "\n"
                "generator = letters()\n"
                "print(next(generator))\n"
                "print(next(generator))\n"
                "# Вывод:\n"
                "# a\n"
                "# b",
                "Генератор не хранит все значения: он помнит место остановки.",
            ),
            _card(
                "Типичная ошибка: генератор исчерпывается",
                "Генератор одноразовый: когда значения закончились, повторный проход "
                "ничего не даст. Если сохранить generator и дважды вызвать "
                "list(generator), второй список будет пустым. Ошибка не падает, поэтому "
                "её легко не заметить. Нужен повторный проход — создай новый генератор "
                "вызовом функции.",
                "def numbers():\n"
                "    yield 1\n"
                "    yield 2\n"
                "\n"
                "generator = numbers()\n"
                "print(list(generator))\n"
                "print(list(generator))\n"
                "# Вывод:\n"
                "# [1, 2]\n"
                "# []",
                "Новый проход — новый вызов функции-генератора.",
            ),
        ],
        [
            _choice(
                "iterators-yield",
                "Что выведет этот код?\n"
                "def countdown(n):\n"
                "    while n > 0:\n"
                "        yield n\n"
                "        n -= 1\n"
                "\n"
                "print(list(countdown(2)))",
                ["[2, 1]", "[1, 2]", "[2, 1, 0]", "[1, 2, 3]"],
                "[2, 1]",
                "Генератор начинает с n = 2, выдаёт 2, затем 1 и завершается.",
            ),
            _term(
                "iterators-yield",
                "Какое ключевое слово делает функцию генератором?",
                ["yield", "yield()", "ключевое слово yield"],
                "yield приостанавливает функцию и отдаёт очередное значение.",
            ),
            _code(
                "iterators-yield",
                "Напиши генератор `countdown(n)`: он выдаёт числа от n до 1 через "
                "`yield`. Для n = 0 не выдаёт ничего.",
                "def countdown(n):\n    # выдавай числа от n до 1\n    pass\n",
                [
                    {"kind": "call", "call": "list(countdown(3))", "expected": [3, 2, 1]},
                    {"kind": "call", "call": "list(countdown(0))", "expected": []},
                    {"kind": "call", "call": "list(countdown(1))", "expected": [1]},
                ],
                "def countdown(n):\n    while n > 0:\n        yield n\n        n -= 1\n",
                "Верно: yield отдаёт текущее n и возвращает управление на следующем "
                "next(), а условие while завершает генератор на нуле.",
                "Уменьшай n после yield, иначе генератор зациклится.",
            ),
        ],
    ),
    _lesson(
        "iterators-generator-expression",
        "Ленивая версия list comprehension",
        [
            _card(
                "Круглые скобки создают поток",
                "Круглые скобки вместо квадратных создают генераторное выражение. Оно не "
                "строит список, а вычисляет следующий элемент по запросу. Поэтому его "
                "удобно передавать в sum(), min() или any(): функция сама вытянет "
                "значения. Память тратится на один элемент, а не на всю "
                "последовательность.",
                "squares = (n * n for n in range(4))\n"
                "print(list(squares))\n"
                "# Вывод:\n"
                "# [0, 1, 4, 9]",
                "list() нужен только чтобы увидеть все значения сразу.",
            ),
            _card(
                "Генераторное выражение внутри sum()",
                "Когда генераторное выражение — единственный аргумент функции, вторые "
                "скобки можно не писать: sum(n * 2 for n in numbers). Это читается как "
                "«сумма удвоенных чисел». В отличие от [n * 2 for n in numbers], список "
                "целиком не создаётся. Для больших данных это заметно экономит память.",
                "numbers = [1, 2, 3]\nprint(sum(n * 2 for n in numbers))\n# Вывод:\n# 12",
                "sum() отлично работает с ленивым потоком значений.",
            ),
            _card(
                "Типичная ошибка: генератор вместо списка",
                "Генератор не поддерживает индексы и len(): у него нет готовых элементов. "
                "Выражение lengths[0] бросит TypeError: 'generator' object is not "
                "subscriptable. Ошибка заметна по слову generator в тексте. Если нужен "
                "доступ по индексу, сначала собери список: list(lengths).",
                "words = ['ab', 'cde']\n"
                "lengths = (len(word) for word in words)\n"
                "print(next(lengths))\n"
                "print(next(lengths))\n"
                "# Вывод:\n"
                "# 2\n"
                "# 3",
                "Для индексов и len() нужен список, а не генератор.",
            ),
        ],
        [
            _choice(
                "iterators-generator-expression",
                "Что выведет этот код?\nnumbers = [1, 2, 3]\nprint(sum(n + 1 for n in numbers))",
                ["9", "6", "7", "8"],
                "9",
                "К каждому числу прибавилась единица: 2 + 3 + 4 = 9.",
            ),
            _term(
                "iterators-generator-expression",
                "Как называется выражение (x * x for x in numbers)?",
                ["генераторное выражение", "генератор", "generator expression"],
                "Круглые скобки дают генераторное выражение — ленивый поток значений.",
            ),
            _code(
                "iterators-generator-expression",
                "Напиши `total_length(words)`: верни суммарную длину слов. Используй "
                "`sum` и генераторное выражение, без промежуточного списка.",
                "def total_length(words):\n    # сумма длин слов\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "total_length(['ab', 'cde'])",
                        "expected": 5,
                    },
                    {"kind": "call", "call": "total_length([])", "expected": 0},
                    {"kind": "call", "call": "total_length(['a'])", "expected": 1},
                ],
                "def total_length(words):\n    return sum(len(word) for word in words)\n",
                "Верно: sum() обходит генераторное выражение и складывает длины, не "
                "создавая промежуточный список.",
                "Передай в sum() выражение len(word) for word in words.",
            ),
        ],
    ),
    _lesson(
        "modules-imports",
        "Подключаем готовый код из другого файла",
        [
            _card(
                "Модуль — это файл с готовым кодом",
                "Модуль — обычный Python-файл, код которого можно подключить в другой "
                "файл. Команда import math подключает модуль стандартной библиотеки и "
                "даёт доступ к его функциям через точку: math.sqrt(16). Имя модуля "
                "становится именем в твоей программе. Так один и тот же код не "
                "приходится копировать.",
                "import math\n\nprint(math.sqrt(16))\n# Вывод:\n# 4.0",
                "После import обращайся к функциям через имя модуля и точку.",
            ),
            _card(
                "from ... import берёт конкретное имя",
                "Если нужна одна функция, её можно импортировать напрямую: from math "
                "import floor. Тогда пиши floor(3.9), без префикса math. Это короче, но "
                "по имени уже не видно, откуда оно. Для ясности крупные модули чаще "
                "импортируют целиком, а короткие имена берут через from.",
                "from math import floor\n\nprint(floor(3.9))\n# Вывод:\n# 3",
                "from удобен для одного-двух имён, но не для всего модуля.",
            ),
            _card(
                "Типичная ошибка: затереть имя модуля",
                "Если назвать переменную так же, как модуль, переменная заменит модуль в "
                "твоём файле. После math = 'строка' вызов math.sqrt упадёт с "
                "AttributeError: 'str' object has no attribute 'sqrt'. Ошибку видно по "
                "тому, что имя модуля стало строкой. Не используй имена модулей для "
                "своих переменных.",
                "import math\n\nmath = 'это уже строка'\nprint(math)\n# Вывод:\n# это уже строка",
                "Проверь, не занято ли имя модуля твоей переменной.",
            ),
        ],
        [
            _choice(
                "modules-imports",
                "Что выведет этот код?\nimport math\nprint(math.ceil(2.1))",
                ["3", "2", "4", "1"],
                "3",
                "ceil округляет вверх: ближайшее целое не меньше 2.1 — это 3.",
            ),
            _term(
                "modules-imports",
                "Какой модуль стандартной библиотеки даёт sqrt, ceil и pi?",
                ["math", "модуль math"],
                "math — модуль с математическими функциями и константами.",
            ),
            _code(
                "modules-imports",
                "Напиши `circle_area(r)`: верни площадь круга с округлением до двух "
                "знаков. Используй `import math` и `math.pi`.",
                "def circle_area(r):\n    # площадь круга\n    pass\n",
                [
                    {"kind": "call", "call": "circle_area(1)", "expected": 3.14},
                    {"kind": "call", "call": "circle_area(2)", "expected": 12.57},
                    {"kind": "call", "call": "circle_area(0)", "expected": 0.0},
                ],
                "import math\n\n\ndef circle_area(r):\n    return round(math.pi * r ** 2, 2)\n",
                "Верно: math.pi даёт точное число пи, а round(..., 2) оставляет два "
                "знака после запятой.",
                "Формула площади: pi умножить на радиус в квадрате.",
            ),
        ],
    ),
    _lesson(
        "modules-main-guard",
        "Запускаем файл, но не мешаем импорту",
        [
            _card(
                "main() собирает запуск в функцию",
                "Сценарий запуска удобно собрать в функцию main(). Тогда весь код "
                "программы не разбросан по файлу, а вызывается в одном месте. Функцию "
                "можно импортировать и вызвать в тесте, не запуская всё заново. Это "
                "первый шаг к аккуратной точке входа.",
                "def main():\n    print('Готово')\n\nmain()\n# Вывод:\n# Готово",
                "main() — обычная функция, её можно вызвать и проверить отдельно.",
            ),
            _card(
                "Защитный блок запускает только напрямую",
                "При прямом запуске файла Python ставит переменной __name__ значение "
                "'__main__'. При импорте там будет имя модуля. Поэтому блок "
                "if __name__ == '__main__': main() выполняет main() только при запуске "
                "файла. Импорт просто подключает функции: блок пропускается, а остальной "
                "код модуля продолжает выполняться.",
                "def main():\n"
                "    print('Готово')\n"
                "\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
                "\n"
                "print('строка после блока выполнилась')\n"
                "# Вывод:\n"
                "# строка после блока выполнилась",
                "Под защитой main() не сработает при импорте модуля.",
            ),
            _card(
                "Типичная ошибка: main() без защитного блока",
                "Если оставить вызов main() на верхнем уровне, он сработает и при "
                "импорте модуля. Тогда тест или другой файл получит лишний запуск и "
                "неожиданный вывод. Ошибка видна по тому, что импорт печатает «Готово». "
                "Прячь запуск под if __name__ == '__main__'.",
                "def main():\n    print('Готово')\n\nmain()\n# Вывод:\n# Готово",
                "Вызов на верхнем уровне выполняется всегда, даже при импорте.",
            ),
        ],
        [
            _choice(
                "modules-main-guard",
                "Какой код запустит main() только при прямом запуске файла?",
                [
                    "if __name__ == '__main__': main()",
                    "if __name__ = '__main__': main()",
                    "if name == '__main__': main()",
                    "if __name__ == '__learner__': main()",
                ],
                "if __name__ == '__main__': main()",
                "Сравнивать нужно именно __name__ с '__main__': тогда импорт блок пропустит.",
            ),
            _term(
                "modules-main-guard",
                "Какое значение получает __name__ у файла, запущенного напрямую?",
                ["__main__", "'__main__'", "main"],
                "При прямом запуске __name__ равен '__main__', при импорте — имени модуля.",
            ),
            _code(
                "modules-main-guard",
                "Напиши `main()`, которая возвращает строку 'Готово'. Вызови её под "
                "защитным блоком if __name__ == '__main__'. При импорте ничего не "
                "должно печататься.",
                "def main():\n    pass\n",
                [
                    {"kind": "call", "call": "main()", "expected": "Готово"},
                    {"kind": "stdout", "expected": ""},
                ],
                "def main():\n    return 'Готово'\n\n\nif __name__ == '__main__':\n    main()\n",
                "Верно: main() возвращает строку, а защитный блок не выполняет её при "
                "импорте, поэтому stdout остаётся пустым.",
                "Верни строку из main() и помести вызов под проверку __name__.",
            ),
        ],
    ),
    _lesson(
        "modules-packages",
        "Каталог с модулями и общим именем",
        [
            _card(
                "Пакет — каталог с модулями",
                "Пакет — это каталог, в котором лежат модули и файл __init__.py. Точки в "
                "имени показывают вложенность: app.utils.text означает файл text.py "
                "внутри пакета utils внутри пакета app. Такая структура помогает "
                "раскладывать код по смыслу. Путь к файлу получается заменой точек на "
                "слеши.",
                "parts = 'app.utils.text'.split('.')\n"
                "print('/'.join(parts) + '.py')\n"
                "# Вывод:\n"
                "# app/utils/text.py",
                "Каждая точка в имени модуля — ещё один уровень каталога.",
            ),
            _card(
                "Импорт между файлами пакета",
                "Внутри пакета модули импортируют друг друга по полному имени: from "
                "app.utils.text import clean. Python находит пакет по структуре каталогов "
                "от корня проекта. Так функция clean живёт в одном файле, а пользуются "
                "ею в main.py. Это и есть переиспользование кода.",
                "# app/utils/text.py\n"
                "def clean(text):\n"
                "    return text.strip()\n"
                "\n"
                "# main.py\n"
                "from app.utils.text import clean\n"
                "\n"
                "print(clean('  привет  '))\n"
                "# Вывод:\n"
                "# привет",
                "Абсолютный импорт начинается от корня проекта, а не от текущего файла.",
                run=False,
            ),
            _card(
                "Типичная ошибка: относительный импорт в скрипте",
                "Относительный импорт from .helpers import clean работает только внутри "
                "пакета. Если запустить файл напрямую, Python не знает родительский пакет "
                "и падает с ImportError: attempted relative import with no known parent "
                "package. Ошибка видна по слову relative import. Запускай такой файл как "
                "модуль: python -m app.utils.text.",
                "# файл app/utils/text.py\n"
                "from .helpers import clean\n"
                "\n"
                "print(clean('  привет  '))\n"
                "# Вывод:\n"
                "# привет",
                "Точка в начале импорта означает «рядом со мной внутри пакета».",
                run=False,
            ),
        ],
        [
            _choice(
                "modules-packages",
                "Что выведет этот код?\n"
                "dotted = 'app.utils.text'\n"
                "print(dotted.replace('.', '/') + '.py')",
                ["app/utils/text.py", "app.utils/text.py", "app/utils.py", "app/utils/text"],
                "app/utils/text.py",
                "Точки заменяются на слеши, а расширение .py добавляется в конце.",
            ),
            _term(
                "modules-packages",
                "Как называется каталог с __init__.py, который объединяет модули?",
                ["пакет", "package", "python-пакет"],
                "Пакет — каталог модулей с общим пространством имён.",
            ),
            _code(
                "modules-packages",
                "Напиши `module_path(dotted)`: преврати точечное имя модуля в путь к "
                "файлу. module_path('app.utils.text') должен вернуть 'app/utils/text.py', "
                "а module_path('main') — 'main.py'.",
                "def module_path(dotted):\n    # имя модуля -> путь к файлу\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "module_path('app.utils.text')",
                        "expected": "app/utils/text.py",
                    },
                    {"kind": "call", "call": "module_path('main')", "expected": "main.py"},
                    {"kind": "call", "call": "module_path('a.b')", "expected": "a/b.py"},
                ],
                "def module_path(dotted):\n    return dotted.replace('.', '/') + '.py'\n",
                "Верно: replace() меняет все точки на слеши, а '.py' завершает путь к файлу.",
                "Замени точки на '/' и добавь '.py' в конце.",
            ),
        ],
    ),
    _lesson(
        "modules-stdlib-imports",
        "Готовые инструменты вместо своих велосипедов",
        [
            _card(
                "Стандартная библиотека уже под рукой",
                "Стандартная библиотека — набор модулей, которые идут вместе с Python. В "
                "ней есть математика, даты, JSON, регулярные выражения и коллекции. Не "
                "нужно писать своё, если готовая функция уже решает задачу. Подключай "
                "модуль через import и читай его документацию.",
                "from collections import Counter\n"
                "\n"
                "print(Counter('ааб').most_common())\n"
                "# Вывод:\n"
                "# [('а', 2), ('б', 1)]",
                "Counter сразу считает повторы за тебя.",
            ),
            _card(
                "Разные задачи — разные модули",
                "Модули стандартной библиотеки подключаются так же, как math. Например, "
                "datetime хранит даты, json разбирает JSON, а re ищет по шаблону. Импорт "
                "не замедляет программу заметно: Python загружает модуль один раз. "
                "Проверь стандартную библиотеку до того, как писать свой велосипед.",
                "from datetime import date\n\nprint(date(2026, 1, 1).year)\n# Вывод:\n# 2026",
                "У date есть готовые атрибуты вроде year, month и day.",
            ),
            _card(
                "Типичная ошибка: most_common возвращает пары",
                "Метод most_common(1) возвращает список кортежей, а не слово. Если сразу "
                "вывести результат, получится [('кот', 2)], и сравнение со строкой не "
                "сработает. Ошибка заметна по скобкам вокруг пары. Чтобы достать само "
                "слово, возьми top[0][0].",
                "from collections import Counter\n"
                "\n"
                "words = 'кот пёс кот'.split()\n"
                "top = Counter(words).most_common(1)\n"
                "print(top)\n"
                "# Вывод:\n"
                "# [('кот', 2)]",
                "Сначала выбери пару, потом её первый элемент — слово.",
            ),
        ],
        [
            _choice(
                "modules-stdlib-imports",
                "Что выведет этот код?\n"
                "from collections import Counter\n"
                "print(Counter('ааб').most_common(1))",
                ["[('а', 2)]", "[('б', 1)]", "[('а', 1)]", "('а', 2)"],
                "[('а', 2)]",
                "most_common(1) возвращает список с одной парой «а» и её количеством 2.",
            ),
            _term(
                "modules-stdlib-imports",
                "Какая коллекция из collections считает повторы элементов?",
                ["Counter", "counter", "счётчик"],
                "Counter — словарь, где ключом является элемент, а значением — число повторов.",
            ),
            _code(
                "modules-stdlib-imports",
                "Напиши `most_common_word(text)`: верни самое частое слово в нижнем "
                "регистре. Используй `from collections import Counter`. Если текст пуст, "
                "верни пустую строку.",
                "def most_common_word(text):\n    # самое частое слово\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "most_common_word('кот Кот пёс')",
                        "expected": "кот",
                    },
                    {"kind": "call", "call": "most_common_word('')", "expected": ""},
                    {
                        "kind": "call",
                        "call": "most_common_word('a b b c')",
                        "expected": "b",
                    },
                ],
                "from collections import Counter\n"
                "\n"
                "\n"
                "def most_common_word(text):\n"
                "    words = text.lower().split()\n"
                "    if not words:\n"
                "        return ''\n"
                "    return Counter(words).most_common(1)[0][0]\n",
                "Верно: lower() приводит слова к одному регистру, Counter считает "
                "повторы, а most_common(1)[0][0] достаёт само слово.",
                "Приведи текст к нижнему регистру, разбей на слова и посчитай Counter.",
            ),
        ],
    ),
]
