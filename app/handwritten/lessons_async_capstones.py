"""Рукописные уроки 113–120: асинхронность и выпускные проекты."""

from __future__ import annotations

from typing import Any


def _card(
    title: str,
    text: str,
    example: str,
    tip: str = "",
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
        "async-coroutines",
        "Функция, которая умеет ждать",
        [
            _card(
                "Корутина — это функция с паузами",
                "Корутина умеет приостановиться в точке `await` и продолжить с того же "
                "места, когда результат будет готов. Внешне она похожа на обычную "
                "функцию, но возвращает не готовый ответ, а объект, который нужно "
                "запустить. Пока она ждёт, цикл событий может заняться другой работой.",
                "def steps():\n"
                "    print('шаг 1')\n"
                "    yield 'пауза'\n"
                "    print('шаг 2')\n"
                "    yield 'готово'\n"
                "\n"
                "gen = steps()\n"
                "print(next(gen))\n"
                "print(next(gen))\n"
                "# Вывод:\n"
                "# шаг 1\n"
                "# пауза\n"
                "# шаг 2\n"
                "# готово",
            ),
            _card(
                "Запуск и ожидание результата",
                "Корутину запускает цикл событий, а `await` говорит: подожди результат "
                "этой операции, но не блокируй весь процесс. В примере генератор тоже "
                "приостанавливается на `yield` и потом продолжает работу — это удобная "
                "модель того, как устроено ожидание.",
                "def counter(n):\n"
                "    for number in range(1, n + 1):\n"
                "        yield f'готово {number}'\n"
                "\n"
                "for result in counter(3):\n"
                "    print(result)\n"
                "# Вывод:\n"
                "# готово 1\n"
                "# готово 2\n"
                "# готово 3",
            ),
            _card(
                "Типичная ошибка: забыть await",
                "Если создать корутину и не дождаться её, код внутри просто не "
                "выполнится. Ошибка не роняет программу: в консоли появится "
                "предупреждение, а результата не будет. Замечай её по пустому выводу и "
                "по тексту `coroutine ... was never awaited`.",
                "import asyncio\n"
                "\n"
                "async def work():\n"
                "    print('работа выполнена')\n"
                "\n"
                "async def main():\n"
                "    work()\n"
                "    print('конец')\n"
                "\n"
                "asyncio.run(main())\n"
                "# Вывод:\n"
                "# конец",
                "Сохрани корутину в переменную и сделай await — иначе работа не начнётся.",
                run=False,
            ),
        ],
        [
            _choice(
                "async-coroutines",
                "Что выведет этот код?\n"
                "def gen():\n"
                "    yield 'раз'\n"
                "    yield 'два'\n"
                "\n"
                "print(next(gen()))",
                ["раз", "два", "ничего", "ошибка"],
                "раз",
                "`next` запускает генератор до первого `yield` и возвращает 'раз'. "
                "Второе значение появится только при следующем `next`.",
            ),
            _term(
                "async-coroutines",
                "Каким словом внутри `async def` ждут результат операции?",
                ["await", "оператор await", "await ..."],
                "`await` приостанавливает корутину до готовности результата и отдаёт "
                "управление циклу событий.",
            ),
            _code(
                "async-coroutines",
                "Напиши генератор `steps(name, n)`: он отдаёт строки "
                "`'<name>: шаг <i>'` для `i` от 1 до `n`. При `n = 0` не отдаёт ничего.",
                "def steps(name, n):\n    # верни генератор строк\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "list(steps('загрузка', 2))",
                        "expected": ["загрузка: шаг 1", "загрузка: шаг 2"],
                    },
                    {
                        "kind": "call",
                        "call": "list(steps('тест', 0))",
                        "expected": [],
                    },
                    {
                        "kind": "call",
                        "call": "list(steps('a', 1))",
                        "expected": ["a: шаг 1"],
                    },
                ],
                "def steps(name, n):\n"
                "    for i in range(1, n + 1):\n"
                "        yield f'{name}: шаг {i}'\n",
                "Генератор не собирает список, а отдаёт значения по одному через "
                "`yield`. `range(1, n + 1)` включает `n` и не даёт лишних шагов.",
                "Помести `yield` внутрь цикла `for i in range(1, n + 1)`.",
            ),
        ],
    ),
    _lesson(
        "async-tasks",
        "Несколько корутин одновременно",
        [
            _card(
                "Задача запускает корутину в цикле событий",
                "Задача (`Task`) — это корутина, которую цикл событий уже принял в "
                "работу. Пока одна задача ждёт ответа сети, другая успевает сделать "
                "свой шаг. В примере два итератора по очереди отдают значения — так "
                "выглядит конкурентное выполнение без потоков.",
                "first = iter('ab')\n"
                "second = iter('xy')\n"
                "print(next(first) + next(second))\n"
                "print(next(first) + next(second))\n"
                "# Вывод:\n"
                "# ax\n"
                "# by",
            ),
            _card(
                "Планировщик идёт по кругу",
                "Планировщик даёт каждой задаче один шаг и переходит к следующей, пока "
                "есть работа. Когда итератор заканчивается, его убирают из круга. "
                "Такой обход удобно писать через список активных задач и "
                "`try`/`except StopIteration`.",
                "tasks = [iter('ab'), iter('xyz')]\n"
                "done = False\n"
                "while not done:\n"
                "    done = True\n"
                "    for task in tasks:\n"
                "        try:\n"
                "            print(next(task))\n"
                "        except StopIteration:\n"
                "            continue\n"
                "        done = False\n"
                "# Вывод:\n"
                "# a\n"
                "# x\n"
                "# b\n"
                "# y\n"
                "# z",
            ),
            _card(
                "Типичная ошибка: не дождаться задачи",
                "`create_task` только ставит корутину в очередь. Если сразу завершить "
                "программу, задача может не успеть выполниться, а её результат "
                "потеряется. Замечай по отсутствию ожидаемого вывода: сохраняй задачу "
                "в переменную и делай `await task`.",
                "import asyncio\n"
                "\n"
                "async def job():\n"
                "    await asyncio.sleep(1)\n"
                "    print('задача выполнена')\n"
                "\n"
                "async def main():\n"
                "    asyncio.create_task(job())\n"
                "    print('главная завершилась')\n"
                "\n"
                "asyncio.run(main())\n"
                "# Вывод:\n"
                "# главная завершилась",
                "Храни ссылку на задачу и дожидайся её через await.",
                run=False,
            ),
        ],
        [
            _choice(
                "async-tasks",
                "Что выведет этот код?\n"
                "tasks = [iter('ab'), iter('xy')]\n"
                "print(next(tasks[0]) + next(tasks[1]))",
                ["ax", "ay", "bx", "by"],
                "ax",
                "Первый `next` берёт 'a' из первого итератора, второй — 'x' из "
                "второго. Конкатенация даёт 'ax'.",
            ),
            _term(
                "async-tasks",
                "Какой объект планирует корутину в цикле событий?",
                ["Task", "задача", "task", "Задача"],
                "`asyncio.create_task` возвращает `Task` — корутину, уже поставленную "
                "в очередь цикла событий.",
            ),
            _code(
                "async-tasks",
                "Напиши `round_robin(gens)`: бери по одному значению из каждого "
                "генератора по кругу, пока все не закончатся, и верни общий список.",
                "def round_robin(gens):\n    # обойди генераторы по кругу\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "round_robin([iter('ab'), iter('xyz')])",
                        "expected": ["a", "x", "b", "y", "z"],
                    },
                    {
                        "kind": "call",
                        "call": "round_robin([])",
                        "expected": [],
                    },
                    {
                        "kind": "call",
                        "call": "round_robin([iter('a'), iter('')])",
                        "expected": ["a"],
                    },
                ],
                "def round_robin(gens):\n"
                "    result = []\n"
                "    active = list(gens)\n"
                "    while active:\n"
                "        remaining = []\n"
                "        for gen in active:\n"
                "            try:\n"
                "                result.append(next(gen))\n"
                "                remaining.append(gen)\n"
                "            except StopIteration:\n"
                "                pass\n"
                "        active = remaining\n"
                "    return result\n",
                "На каждом круге добавляй в новый список только те генераторы, "
                "которые ещё не закончились. Когда список опустеет, работа готова.",
                "Собери `active` и после каждого круга оставь в нём живые генераторы.",
            ),
        ],
    ),
    _lesson(
        "async-gather-timeouts",
        "Один результат на каждую задачу",
        [
            _card(
                "gather собирает результаты по порядку",
                "`asyncio.gather` запускает несколько операций и возвращает список "
                "результатов в том же порядке, в каком ты передал задачи. Быстрая "
                "задача не перескакивает вперёд: место в списке закреплено за входом. "
                "Поэтому результат удобно сверять с исходным списком.",
                "durations = [1, 5, 2]\n"
                "timeout = 3\n"
                "results = ['ok' if d <= timeout else 'timeout' for d in durations]\n"
                "print(results)\n"
                "# Вывод:\n"
                "# ['ok', 'timeout', 'ok']",
            ),
            _card(
                "Таймаут решает судьбу каждой задачи",
                "Таймаут — это предел ожидания. Если операция уложилась в него, "
                "получаем `'ok'`, иначе помечаем `'timeout'`. В реальном коде для "
                "этого берут `asyncio.wait_for`; ниже — живой пример с настоящим "
                "ожиданием.",
                "import asyncio\n"
                "\n"
                "async def fetch(delay):\n"
                "    await asyncio.sleep(delay)\n"
                "    return delay\n"
                "\n"
                "async def main():\n"
                "    try:\n"
                "        result = await asyncio.wait_for(fetch(5), timeout=1)\n"
                "    except TimeoutError:\n"
                "        result = 'timeout'\n"
                "    print(result)\n"
                "\n"
                "asyncio.run(main())\n"
                "# Вывод:\n"
                "# timeout",
                "Таймаут задаётся на конкретную операцию и не отменяет остальные.",
                run=False,
            ),
            _card(
                "Типичная ошибка: выбросить медленные задачи",
                "Соблазнительно отфильтровать всё, что не успело, но тогда пропадут "
                "позиции и количество результатов. Получатель не поймёт, какая именно "
                "задача не ответила. Замечай ошибку по короткому списку: результатов "
                "должно быть столько же, сколько задач.",
                "durations = [1, 5, 2]\n"
                "timeout = 3\n"
                "results = [d for d in durations if d <= timeout]\n"
                "print(results)\n"
                "print(len(results))\n"
                "# Вывод:\n"
                "# [1, 2]\n"
                "# 2",
            ),
        ],
        [
            _choice(
                "async-gather-timeouts",
                "Что выведет этот код?\n"
                "durations = [1, 5, 2]\n"
                "timeout = 3\n"
                "print(['ok' if d <= timeout else 'timeout' for d in durations])",
                [
                    "['ok', 'timeout', 'ok']",
                    "['ok', 'ok', 'timeout']",
                    "['timeout', 'ok', 'ok']",
                    "['ok', 'ok', 'ok']",
                ],
                "['ok', 'timeout', 'ok']",
                "Проверка идёт по каждой длительности: 1 и 2 не больше 3, а 5 больше. "
                "Порядок результатов повторяет порядок входа.",
            ),
            _term(
                "async-gather-timeouts",
                "Сколько результатов вернёт gather для трёх задач?",
                ["3", "три", "3 результата"],
                "`gather` возвращает по результату на каждую задачу, даже если часть "
                "из них завершилась таймаутом.",
            ),
            _code(
                "async-gather-timeouts",
                "Напиши `gather_results(durations, timeout)`: верни `'ok'` для "
                "длительности не больше таймаута и `'timeout'` для остальных. Порядок "
                "результатов совпадает с порядком входа.",
                "def gather_results(durations, timeout):\n"
                "    # собери результат для каждой длительности\n"
                "    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "gather_results([1, 5, 2], 3)",
                        "expected": ["ok", "timeout", "ok"],
                    },
                    {
                        "kind": "call",
                        "call": "gather_results([], 3)",
                        "expected": [],
                    },
                    {
                        "kind": "call",
                        "call": "gather_results([3], 3)",
                        "expected": ["ok"],
                    },
                ],
                "def gather_results(durations, timeout):\n"
                "    return ['ok' if duration <= timeout else 'timeout' for duration in durations]\n",
                "Граница включается: длительность, равная таймауту, ещё успевает. "
                "Список-результат строится в том же порядке, что и вход.",
                "Используй списковое включение и сравнивай каждую длительность с timeout.",
            ),
        ],
    ),
    _lesson(
        "async-async-design",
        "Где ждать, а где считать",
        [
            _card(
                "Асинхронность ускоряет ожидание",
                "Когда несколько задач ждут сеть или диск, они могут ждать "
                "одновременно. Общее время тогда близко к самой долгой операции, а не "
                "к сумме всех. Если же задачи выполняются по очереди, время "
                "складывается.",
                "durations = [1, 2, 3]\n"
                "print(max(durations))\n"
                "print(sum(durations))\n"
                "# Вывод:\n"
                "# 3\n"
                "# 6",
            ),
            _card(
                "Считай время по сценарию",
                "Перед выбором подхода прикинь общее время. При конкурентном "
                "выполнении берут максимум длительностей, при последовательном — сумму. "
                "Пустой список даёт ноль: ждать нечего.",
                "def estimate(durations, concurrent):\n"
                "    if concurrent:\n"
                "        return max(durations, default=0)\n"
                "    return sum(durations)\n"
                "\n"
                "print('конкурентно:', estimate([1, 2, 3], True))\n"
                "print('по очереди:', estimate([1, 2, 3], False))\n"
                "# Вывод:\n"
                "# конкурентно: 3\n"
                "# по очереди: 6",
            ),
            _card(
                "Типичная ошибка: блокировать цикл событий",
                "Асинхронность не ускоряет вычисления на процессоре. Если внутри "
                "`async def` надолго занять Python тяжёлым циклом, цикл событий не "
                "сможет переключиться на другие задачи. Замечай по «замиранию» всех "
                "запросов одновременно; вычисления выносят в отдельный процесс или "
                "поток.",
                "import asyncio\n"
                "\n"
                "async def handler():\n"
                "    total = sum(range(10_000_000))\n"
                "    print('готово', total > 0)\n"
                "\n"
                "asyncio.run(handler())\n"
                "# Вывод:\n"
                "# готово True",
                "Долгую CPU-работу не запускай прямо в обработчике async.",
                run=False,
            ),
        ],
        [
            _choice(
                "async-async-design",
                "Что выведет этот код?\n"
                "durations = [1, 2, 3]  # секунды на запрос\n"
                "one_by_one = sum(durations)\n"
                "together = max(durations)  # как при asyncio.gather\n"
                "print(one_by_one, together)",
                ["6 3", "3 6", "6 6", "3 3"],
                "6 3",
                "По очереди запросы ждут друг друга — время складывается. "
                "Вместе ждут одновременно — итог равен самому долгому.",
            ),
            _term(
                "async-async-design",
                "Сколько времени займут три задачи по 2 секунды при конкурентном выполнении?",
                ["2", "2 секунды", "2 сек"],
                "При конкурентном ожидании общее время равно самой долгой задаче, "
                "то есть 2 секундам.",
            ),
            _code(
                "async-async-design",
                "Напиши `total_time(durations, concurrent)`: при `concurrent=True` "
                "верни время самой долгой операции, иначе — сумму всех. Для пустого "
                "списка верни 0.",
                "def total_time(durations, concurrent):\n    # посчитай общее время\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "total_time([1, 2, 3], True)",
                        "expected": 3,
                    },
                    {
                        "kind": "call",
                        "call": "total_time([1, 2, 3], False)",
                        "expected": 6,
                    },
                    {
                        "kind": "call",
                        "call": "total_time([], True)",
                        "expected": 0,
                    },
                ],
                "def total_time(durations, concurrent):\n"
                "    if concurrent:\n"
                "        return max(durations, default=0)\n"
                "    return sum(durations)\n",
                "При конкурентном выполнении операции перекрываются, поэтому берём "
                "максимум. `default=0` спасает пустой список от ошибки.",
                "Для конкурентного случая используй `max(durations, default=0)`.",
            ),
        ],
    ),
    _lesson(
        "capstones-task-manager",
        "Задачи, статусы и порядок",
        [
            _card(
                "Менеджер задач хранит список",
                "Начни с простого: каждая задача — это заголовок и признак "
                "выполнения. Список сохраняет порядок добавления, поэтому `pending()` "
                "вернёт задачи в том же порядке, в каком их создали. Этого достаточно "
                "для первого рабочего варианта.",
                "class TaskManager:\n"
                "    def __init__(self):\n"
                "        self.titles = []\n"
                "\n"
                "    def add(self, title):\n"
                "        self.titles.append(title)\n"
                "\n"
                "tm = TaskManager()\n"
                "tm.add('купить хлеб')\n"
                "print(tm.titles)\n"
                "# Вывод:\n"
                "# ['купить хлеб']",
            ),
            _card(
                "Отметка выполнения не удаляет задачу",
                "`done` меняет статус, а не выбрасывает запись: история остаётся, а "
                "`pending` просто фильтрует выполненные. Так пользователь видит и "
                "текущие дела, и то, что уже закрыто.",
                "tasks = [['a', False], ['b', False]]\n"
                "tasks[0][1] = True\n"
                "pending = [title for title, done in tasks if not done]\n"
                "print(pending)\n"
                "# Вывод:\n"
                "# ['b']",
            ),
            _card(
                "Типичная ошибка: удалять во время перебора",
                "Если удалять элементы прямо внутри `for`, итератор пропускает "
                "соседний элемент. В результате часть выполненных задач остаётся в "
                "списке. Замечай по количеству: после прохода должно остаться ровно "
                "столько, сколько нужно.",
                "tasks = [('a', False), ('b', False)]\n"
                "for title, done in tasks:\n"
                "    if not done:\n"
                "        tasks.remove((title, done))\n"
                "print(tasks)\n"
                "# Вывод:\n"
                "# [('b', False)]",
            ),
        ],
        [
            _choice(
                "capstones-task-manager",
                "Что выведет этот код?\n"
                "tasks = [('a', True), ('b', False), ('c', False)]\n"
                "print([title for title, done in tasks if not done])",
                ["['b', 'c']", "['a', 'b']", "['c', 'b']", "['a']"],
                "['b', 'c']",
                "Фильтр оставляет только задачи с `done=False`, сохраняя их порядок: "
                "сначала 'b', затем 'c'.",
            ),
            _term(
                "capstones-task-manager",
                "В каком порядке `pending()` возвращает невыполненные задачи?",
                ["в порядке добавления", "порядок добавления", "добавления"],
                "Список хранит задачи в порядке добавления, и фильтр `pending` этот "
                "порядок не меняет.",
            ),
            _code(
                "capstones-task-manager",
                "Напиши `class TaskManager` с методами `add(title)`, `done(title)` и "
                "`pending()`. `pending()` возвращает заголовки невыполненных задач в "
                "порядке добавления.",
                "class TaskManager:\n"
                "    def __init__(self):\n"
                "        # заведи хранилище задач\n"
                "        pass\n"
                "\n"
                "    def add(self, title):\n"
                "        pass\n"
                "\n"
                "    def done(self, title):\n"
                "        pass\n"
                "\n"
                "    def pending(self):\n"
                "        pass\n",
                [
                    {
                        "kind": "call",
                        "call": "(lambda tm: (tm.add('a'), tm.add('b'), tm.done('a'), "
                        "tm.pending())[3])(TaskManager())",
                        "expected": ["b"],
                    },
                    {
                        "kind": "call",
                        "call": "(lambda tm: (tm.add('a'), tm.done('b'), "
                        "tm.pending())[2])(TaskManager())",
                        "expected": ["a"],
                    },
                    {
                        "kind": "call",
                        "call": "(lambda tm: (tm.add('a'), tm.add('b'), tm.done('a'), "
                        "tm.done('b'), tm.pending())[4])(TaskManager())",
                        "expected": [],
                    },
                ],
                "class TaskManager:\n"
                "    def __init__(self):\n"
                "        self.items = []\n"
                "\n"
                "    def add(self, title):\n"
                "        self.items.append([title, False])\n"
                "\n"
                "    def done(self, title):\n"
                "        for item in self.items:\n"
                "            if item[0] == title:\n"
                "                item[1] = True\n"
                "\n"
                "    def pending(self):\n"
                "        return [title for title, done in self.items if not done]\n",
                "Каждая задача хранится парой «заголовок и статус». `done` находит "
                "задачу по заголовку и меняет статус, а `pending` фильтрует список "
                "без изменения порядка.",
                "Храни в `self.items` пары `[title, False]` и перебирай их в `done`.",
            ),
        ],
    ),
    _lesson(
        "capstones-notes-app",
        "Поиск по заголовку и тексту",
        [
            _card(
                "Заметка — это словарь с полями",
                "У заметки два главных поля: заголовок и текст. Словарь даёт к ним "
                "доступ по имени, а список заметок сохраняет порядок. Такую структуру "
                "легко превратить в JSON и обратно, когда понадобится хранение.",
                "note = {'title': 'Покупки', 'text': 'хлеб и молоко'}\n"
                "print(note['title'])\n"
                "print(len(note['text']))\n"
                "# Вывод:\n"
                "# Покупки\n"
                "# 13",
            ),
            _card(
                "Поиск без учёта регистра",
                "Пользователь может ввести `ХЛЕБ`, а в заметке написано `хлеб`. Перед "
                "сравнением приведи и запрос, и поля к нижнему регистру. Ищи "
                "совпадение и в заголовке, и в тексте — иначе часть заметок "
                "потеряется.",
                "notes = [\n"
                "    {'title': 'Покупки', 'text': 'хлеб и молоко'},\n"
                "    {'title': 'Идеи', 'text': 'бот для кухни'},\n"
                "]\n"
                "query = 'ХЛЕБ'\n"
                "found = [\n"
                "    note['title']\n"
                "    for note in notes\n"
                "    if query.lower() in note['title'].lower()\n"
                "    or query.lower() in note['text'].lower()\n"
                "]\n"
                "print(found)\n"
                "# Вывод:\n"
                "# ['Покупки']",
            ),
            _card(
                "Типичная ошибка: сравнивать без lower",
                "Регистр ломает поиск: `'Хлеб'` и `'хлеб'` — разные строки. Программа "
                "не падает, просто ничего не находит. Замечай по пустому результату "
                "при явном совпадении и проверяй оба поля, а не только заголовок.",
                "notes = [{'title': 'Покупки', 'text': 'Хлеб'}]\n"
                "query = 'хлеб'\n"
                "found = [note['title'] for note in notes if query in note['text']]\n"
                "print(found)\n"
                "# Вывод:\n"
                "# []",
            ),
        ],
        [
            _choice(
                "capstones-notes-app",
                "Что выведет этот код?\n"
                "notes = [{'title': 'Покупки', 'text': 'хлеб'}, "
                "{'title': 'Идеи', 'text': 'бот'}]\n"
                "query = 'покуп'\n"
                "print([note['title'] for note in notes if query in note['title'].lower()])",
                ["['Покупки']", "['Заметки']", "['Идеи']", "['хлеб']"],
                "['Покупки']",
                "Запрос `покуп` есть в заголовке «Покупки» после приведения к нижнему "
                "регистру. Заголовок «Идеи» не совпадает.",
            ),
            _term(
                "capstones-notes-app",
                "Каким методом строки приводят запрос к нижнему регистру?",
                ["lower", "lower()", "метод lower"],
                "`lower()` возвращает копию строки в нижнем регистре, не меняя исходную строку.",
            ),
            _code(
                "capstones-notes-app",
                "Напиши `search_notes(notes, query)`: верни заголовки заметок, у "
                "которых `query` встречается в заголовке или тексте без учёта "
                "регистра. Порядок заметок сохраняется.",
                "def search_notes(notes, query):\n    # найди подходящие заголовки\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "search_notes([{'title': 'Покупки', 'text': 'хлеб'}, "
                        "{'title': 'Идеи', 'text': 'бот'}], 'ХЛЕБ')",
                        "expected": ["Покупки"],
                    },
                    {
                        "kind": "call",
                        "call": "search_notes([{'title': 'Идеи', 'text': 'бот'}], 'идеи')",
                        "expected": ["Идеи"],
                    },
                    {
                        "kind": "call",
                        "call": "search_notes([], 'хлеб')",
                        "expected": [],
                    },
                ],
                "def search_notes(notes, query):\n"
                "    needle = query.lower()\n"
                "    result = []\n"
                "    for note in notes:\n"
                "        if needle in note['title'].lower() or needle in note['text'].lower():\n"
                "            result.append(note['title'])\n"
                "    return result\n",
                "Приведи запрос к нижнему регистру один раз, затем сравнивай с "
                "заголовком и текстом. Заголовок добавляй в результат, не меняя "
                "порядок заметок.",
                "Сохрани `query.lower()` в переменную и проверь оба поля через `in`.",
            ),
        ],
    ),
    _lesson(
        "capstones-api-client",
        "Страницы, пока не придёт пустая",
        [
            _card(
                "Страница — это порция данных",
                "API отдаёт данные порциями: страница 1, страница 2 и так далее. "
                "Пустая страница служит сигналом, что данных больше нет. Клиент должен "
                "уметь читать одну страницу и понимать этот сигнал.",
                "pages = [[1, 2], [3], []]\n"
                "\n"
                "def get_page(number):\n"
                "    return pages[number - 1]\n"
                "\n"
                "print(get_page(1))\n"
                "print(get_page(3))\n"
                "# Вывод:\n"
                "# [1, 2]\n"
                "# []",
            ),
            _card(
                "Собирай страницы в один список",
                "Начни с первой страницы и добавляй её элементы в общий результат. "
                "Как только пришла пустая страница, остановись — следующая уже не "
                "нужна. Счётчик страниц увеличивай только после успешного чтения.",
                "def get_page(number):\n"
                "    pages = [['a', 'b'], ['c'], []]\n"
                "    return pages[number - 1]\n"
                "\n"
                "def fetch_all(get_page):\n"
                "    result = []\n"
                "    page = 1\n"
                "    while True:\n"
                "        items = get_page(page)\n"
                "        if not items:\n"
                "            break\n"
                "        result.extend(items)\n"
                "        page += 1\n"
                "    return result\n"
                "\n"
                "print(fetch_all(get_page))\n"
                "# Вывод:\n"
                "# ['a', 'b', 'c']",
            ),
            _card(
                "Типичная ошибка: остановиться после первой страницы",
                "Один вызов `get_page(1)` возвращает только первую порцию. Если на "
                "этом закончить, в результате не будет остальных данных. Замечай по "
                "длине: сравни количество элементов с тем, что ожидаешь увидеть, и "
                "проверь, что цикл дошёл до пустой страницы.",
                "def get_page(number):\n"
                "    return [[1, 2], [3], []][number - 1]\n"
                "\n"
                "items = get_page(1)\n"
                "print(items)\n"
                "# Вывод:\n"
                "# [1, 2]",
            ),
        ],
        [
            _choice(
                "capstones-api-client",
                "Что выведет этот код?\n"
                "def get_page(n):\n"
                "    return [[1, 2], [3], []][n - 1]\n"
                "\n"
                "items = []\n"
                "page = 1\n"
                "while get_page(page):\n"
                "    items.extend(get_page(page))\n"
                "    page += 1\n"
                "print(items)",
                ["[1, 2, 3]", "[0, 1, 2]", "[1, 2]", "[1, 2, 3, 3]"],
                "[1, 2, 3]",
                "Цикл читает непустые страницы, пока не дойдёт до пустой. Элементы "
                "склеиваются по порядку: сначала 1 и 2, затем 3.",
            ),
            _term(
                "capstones-api-client",
                "Какое значение страницы говорит, что пора остановиться?",
                ["пустая", "пустой список", "[]", "пустая страница"],
                "Пустая страница — сигнал конца данных: следующий номер уже не запрашивают.",
            ),
            _code(
                "capstones-api-client",
                "Напиши `fetch_all(get_page)`: вызывай `get_page(1)`, `get_page(2)` и "
                "так далее, пока страница не пустая, и склей все элементы в один "
                "список.",
                "def fetch_all(get_page):\n    # собери все страницы\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "fetch_all(lambda n: [[1, 2], [3], []][n - 1])",
                        "expected": [1, 2, 3],
                    },
                    {
                        "kind": "call",
                        "call": "fetch_all(lambda n: [])",
                        "expected": [],
                    },
                    {
                        "kind": "call",
                        "call": "fetch_all(lambda n: [['a'], [], ['b']][n - 1])",
                        "expected": ["a"],
                    },
                ],
                "def fetch_all(get_page):\n"
                "    result = []\n"
                "    page = 1\n"
                "    while True:\n"
                "        items = get_page(page)\n"
                "        if not items:\n"
                "            break\n"
                "        result.extend(items)\n"
                "        page += 1\n"
                "    return result\n",
                "Цикл завершается на первой пустой странице. `extend` добавляет "
                "элементы по одному, сохраняя их порядок внутри общего списка.",
                "Проверяй страницу на пустоту до `extend` и увеличивай номер после добавления.",
            ),
        ],
    ),
    _lesson(
        "capstones-release",
        "Собираем релиз без пустых разделов",
        [
            _card(
                "Префикс задаёт раздел",
                "В списке изменений первая часть строки до двоеточия говорит, что это: "
                "`feat` — новая возможность, `fix` — исправление. Разделяй строку один "
                "раз, чтобы двоеточие внутри текста не сломало разбор.",
                "changes = ['feat: поиск', 'fix: вход']\n"
                "for change in changes:\n"
                "    kind, text = change.split(': ', 1)\n"
                "    print(kind, text)\n"
                "# Вывод:\n"
                "# feat поиск\n"
                "# fix вход",
            ),
            _card(
                "Сначала собери разделы, потом склеивай",
                "Собери новинки и исправления в два отдельных списка. Затем добавь "
                "раздел только если в нём есть хотя бы один пункт. Пустой раздел "
                "смотрится как ошибка и запутывает читателя.",
                "def release_notes(changes):\n"
                "    features = []\n"
                "    fixes = []\n"
                "    for change in changes:\n"
                "        kind, text = change.split(': ', 1)\n"
                "        if kind == 'feat':\n"
                "            features.append(text)\n"
                "        elif kind == 'fix':\n"
                "            fixes.append(text)\n"
                "    sections = []\n"
                "    if features:\n"
                "        sections.append('Новое:\\n' + '\\n'.join('- ' + text for text in features))\n"
                "    if fixes:\n"
                "        sections.append(\n"
                "            'Исправлено:\\n' + '\\n'.join('- ' + text for text in fixes)\n"
                "        )\n"
                "    return '\\n'.join(sections)\n"
                "\n"
                "print(release_notes(['feat: поиск', 'fix: вход']))\n"
                "# Вывод:\n"
                "# Новое:\n"
                "# - поиск\n"
                "# Исправлено:\n"
                "# - вход",
            ),
            _card(
                "Типичная ошибка: печатать пустой раздел",
                "Если выводить заголовок раздела всегда, в релизе появится «Новое:» "
                "без единого пункта. Читатель решит, что данные потерялись. Замечай по "
                "заголовку, за которым сразу идёт следующий заголовок или конец текста.",
                "changes = ['fix: вход']\n"
                "text = 'Новое:\\n' + str([]) + '\\nИсправлено:\\n- вход'\n"
                "print(text)\n"
                "# Вывод:\n"
                "# Новое:\n"
                "# []\n"
                "# Исправлено:\n"
                "# - вход",
            ),
        ],
        [
            _choice(
                "capstones-release",
                "Что выведет этот код?\nprint('feat: поиск'.split(': ')[1])",
                ["поиск", "feat", "feat:", "поиск:"],
                "поиск",
                "`split(': ')` делит строку на `'feat'` и `'поиск'`. Индекс 1 берёт "
                "вторую часть — текст изменения.",
            ),
            _term(
                "capstones-release",
                "Какой раздел собирает строки с префиксом `fix`?",
                ["Исправлено", "Исправлено:", "раздел Исправлено"],
                "Префикс `fix` означает исправление, поэтому такие строки попадают в "
                "раздел «Исправлено».",
            ),
            _code(
                "capstones-release",
                "Напиши `release_notes(changes)`: собери строки `'feat: …'` в раздел "
                "«Новое:», а `'fix: …'` — в «Исправлено:». Каждый пункт начинается с "
                "`'- '`, пустой раздел не выводится.",
                "def release_notes(changes):\n    # собери текст релиза\n    pass\n",
                [
                    {
                        "kind": "call",
                        "call": "release_notes(['feat: поиск', 'fix: вход', 'feat: экспорт'])",
                        "expected": "Новое:\n- поиск\n- экспорт\nИсправлено:\n- вход",
                    },
                    {
                        "kind": "call",
                        "call": "release_notes(['fix: вход'])",
                        "expected": "Исправлено:\n- вход",
                    },
                    {
                        "kind": "call",
                        "call": "release_notes([])",
                        "expected": "",
                    },
                ],
                "def release_notes(changes):\n"
                "    features = []\n"
                "    fixes = []\n"
                "    for change in changes:\n"
                "        kind, text = change.split(': ', 1)\n"
                "        if kind == 'feat':\n"
                "            features.append(text)\n"
                "        elif kind == 'fix':\n"
                "            fixes.append(text)\n"
                "    sections = []\n"
                "    if features:\n"
                "        sections.append('Новое:\\n' + '\\n'.join('- ' + text for text in features))\n"
                "    if fixes:\n"
                "        sections.append(\n"
                "            'Исправлено:\\n' + '\\n'.join('- ' + text for text in fixes)\n"
                "        )\n"
                "    return '\\n'.join(sections)\n",
                "Сначала разложи изменения по двум спискам, затем добавляй заголовок "
                "раздела только при наличии пунктов. Склей разделы через перевод "
                "строки.",
                "Проверяй `if features:` и `if fixes:` перед добавлением заголовка.",
            ),
        ],
    ),
]
