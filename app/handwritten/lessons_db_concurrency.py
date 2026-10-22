"""Рукописные уроки 105–112: базы данных и параллельность."""

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


def _holds(expression: str) -> dict[str, Any]:
    """Сравнение внутри выражения: JSON не сохраняет кортежи и числовые ключи."""
    return {"kind": "call", "call": expression, "expected": True}


LESSONS: list[dict[str, Any]] = [
    _lesson(
        "databases-relational",
        "Таблицы связываются общим ключом",
        [
            _card(
                "Строка, ключ и связь",
                "Реляционная таблица — это набор однотипных строк. У каждой строки есть "
                "первичный ключ: значение, которое отличает её от остальных. Связанная "
                "таблица хранит тот же ключ как ссылку, например `user_id` в заказах. Так "
                "одни данные не приходится дублировать.",
                "users = [{'id': 1, 'name': 'Аня'}]\n"
                "orders = [{'user_id': 1, 'sum': 100}, {'user_id': 1, 'sum': 50}]\n"
                "total = 0\n"
                "for order in orders:\n"
                "    if order['user_id'] == users[0]['id']:\n"
                "        total += order['sum']\n"
                "print(users[0]['name'], total)\n"
                "# Вывод:\n"
                "# Аня 150",
                "Сначала найди ключ, по которому таблицы связаны, и только потом считай.",
            ),
            _card(
                "Соединяй строки по user_id",
                "Чтобы получить имя и сумму заказа, пройди по обеим таблицам и сравни "
                "`user_id` заказа с `id` пользователя. Это и есть соединение таблиц. В SQL "
                "его записывают через `JOIN`, а в обычном Python — вложенным циклом или "
                "словарём.",
                "users = [{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Борис'}]\n"
                "orders = [{'user_id': 1, 'sum': 100}]\n"
                "for user in users:\n"
                "    for order in orders:\n"
                "        if order['user_id'] == user['id']:\n"
                "            print(user['name'], order['sum'])\n"
                "# Вывод:\n"
                "# Аня 100",
                "Пользователь без заказов просто не попадёт во внутренний цикл.",
            ),
            _card(
                "Типичная ошибка: связь по позиции",
                "Если взять первый заказ по индексу, а не по `user_id`, чужая покупка "
                "припишется первому пользователю. Ошибка не падает: код печатает правдоподобную "
                "строку. Заметь её по несовпадению ключей — сверь `id` пользователя и "
                "`user_id` заказа.",
                "users = [{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Борис'}]\n"
                "orders = [{'user_id': 2, 'sum': 100}]\n"
                "print(users[0]['name'], orders[0]['sum'])\n"
                "# Вывод:\n"
                "# Аня 100",
                "Проверяй не только сумму, но и то, кому она принадлежит.",
            ),
        ],
        [
            _choice(
                "databases-relational",
                "Найди ошибку в коде.\n\n"
                "users = [{'id': 1, 'name': 'Аня'}]\n"
                "orders = [{'user_id': 2, 'sum': 100}]\n"
                "print(users[0]['name'], orders[0]['sum'])",
                [
                    "заказ взят по позиции, а не по ключу",
                    "в словаре users вообще нет поля name",
                    "в orders нет поля user_id и sum",
                ],
                "заказ взят по позиции, а не по ключу",
                "orders[0] относится к user_id=2, но код берёт первого пользователя по "
                "позиции. Соединять нужно по совпадению id и user_id.",
            ),
            _term(
                "databases-relational",
                "Какой столбец однозначно отличает каждую строку таблицы?",
                ["первичный ключ", "primary key", "id"],
                "Первичный ключ уникален внутри таблицы, поэтому по нему и находят строку.",
            ),
            _code(
                "databases-relational",
                "Напиши `user_totals(users, orders)`: соедини таблицы по `user_id` и верни "
                "список пар `(имя, сумма)`. Пользователь без заказов даёт `0`, порядок — как "
                "в `users`.",
                "def user_totals(users, orders):\n    # сложи суммы заказов по user_id\n    pass\n",
                [
                    _holds(
                        "user_totals([{'id': 1, 'name': 'Аня'}], "
                        "[{'user_id': 1, 'sum': 100}, {'user_id': 1, 'sum': 50}]) "
                        "== [('Аня', 150)]"
                    ),
                    _holds(
                        "user_totals([{'id': 1, 'name': 'Аня'}, {'id': 2, 'name': 'Борис'}], "
                        "[{'user_id': 1, 'sum': 100}, {'user_id': 1, 'sum': 50}]) "
                        "== [('Аня', 150), ('Борис', 0)]"
                    ),
                    _holds("user_totals([], []) == []"),
                ],
                "def user_totals(users, orders):\n"
                "    totals = {}\n"
                "    for order in orders:\n"
                "        user_id = order['user_id']\n"
                "        totals[user_id] = totals.get(user_id, 0) + order['sum']\n"
                "    return [(user['name'], totals.get(user['id'], 0)) for user in users]\n",
                "Сначала собери суммы по user_id в словарь, затем пройди по users и подставь "
                "нули там, где заказов не было.",
                "Суммы удобно копить в словаре: ключ — user_id, значение — общая сумма.",
            ),
        ],
    ),
    _lesson(
        "databases-crud",
        "Четыре операции над записями",
        [
            _card(
                "Create, read, update, delete",
                "CRUD — это четыре базовые операции с данными: создать запись, прочитать, "
                "изменить и удалить. В памяти их можно показать обычным словарём. Создание "
                "добавляет ключ, чтение берёт значение, обновление заменяет его, удаление "
                "убирает запись.",
                "db = {}\n"
                "db[1] = 'Аня'\n"
                "print(db[1])\n"
                "db[1] = 'Аня П.'\n"
                "del db[1]\n"
                "print(len(db))\n"
                "# Вывод:\n"
                "# Аня\n"
                "# 0",
                "Одна и та же запись проходит через все четыре операции.",
            ),
            _card(
                "Меняй копию, а не исходник",
                "Полезная привычка: операция получает текущий словарь и возвращает новый. "
                "Тогда вызывающий код решает, когда заменить данные, а исходное состояние "
                "остаётся целым для отката или повторной попытки.",
                "db = {1: 'Аня'}\n"
                "new = dict(db)\n"
                "new[2] = 'Борис'\n"
                "del new[1]\n"
                "print(db)\n"
                "print(new)\n"
                "# Вывод:\n"
                "# {1: 'Аня'}\n"
                "# {2: 'Борис'}",
                "dict(db) создаёт поверхностную копию: ключи и значения можно менять отдельно.",
            ),
            _card(
                "Типичная ошибка: псевдоним вместо копии",
                "`alias = db` не создаёт новую таблицу, а даёт второе имя тому же словарю. "
                "После изменения через `alias` меняется и `db`. Ошибку видно по исходнику, "
                "который изменился без явного присваивания. Нужна копия — вызывай `dict(db)`.",
                "db = {1: 'Аня'}\nalias = db\nalias[1] = 'Борис'\nprint(db[1])\n# Вывод:\n# Борис",
                "Сравни id(db) и id(alias): у копии они разные, у псевдонима совпадают.",
            ),
        ],
        [
            _choice(
                "databases-crud",
                "Что выведет этот код?\n\n"
                "db = {1: 'a'}\n"
                "new = dict(db)\n"
                "new[2] = 'b'\n"
                "del new[1]\n"
                "print(len(db), len(new))",
                ["1 1", "2 1", "1 2"],
                "1 1",
                "dict(db) создаёт отдельный словарь: в db остаётся один ключ, а в new после "
                "добавления и удаления тоже остаётся один.",
            ),
            _term(
                "databases-crud",
                "Какая операция CRUD удаляет запись?",
                ["delete", "удаление", "D", "Delete"],
                "Delete убирает запись по ключу, остальные операции создают, читают и меняют.",
            ),
            _code(
                "databases-crud",
                "Напиши `apply(db, op)`: выполни операцию CRUD и верни новый словарь. "
                "Операции: `('create', id, data)`, `('update', id, data)`, `('delete', id)`. "
                "Исходный `db` меняться не должен.",
                "def apply(db, op):\n    # верни новый словарь после операции\n    pass\n",
                [
                    _holds("apply({}, ('create', 1, 'a')) == {1: 'a'}"),
                    _holds("apply({1: 'a'}, ('update', 1, 'b')) == {1: 'b'}"),
                    _holds("apply({1: 'a'}, ('delete', 1)) == {}"),
                    _holds(
                        "(lambda db: (apply(db, ('create', 2, 'b')), db)[1])({1: 'a'}) == {1: 'a'}"
                    ),
                    _holds("(lambda db: (apply(db, ('delete', 1)), db)[1])({1: 'a'}) == {1: 'a'}"),
                ],
                "def apply(db, op):\n"
                "    result = dict(db)\n"
                "    action = op[0]\n"
                "    if action == 'create' or action == 'update':\n"
                "        result[op[1]] = op[2]\n"
                "    elif action == 'delete':\n"
                "        result.pop(op[1], None)\n"
                "    return result\n",
                "Копия в начале защищает исходный словарь, а ветки разбирают вид операции.",
                "Начни с result = dict(db), затем добавь ветки для create, update и delete.",
            ),
        ],
    ),
    _lesson(
        "databases-parameters",
        "Данные отдельно от текста SQL",
        [
            _card(
                "Плейсхолдер вместо значения",
                "Параметризованный запрос держит текст SQL и данные отдельно. На месте "
                "значения остаётся `?`, а само значение передаётся кортежем. База подставит "
                "его безопасно и не станет разбирать как часть команды.",
                "city = 'Москва'\n"
                "sql = 'SELECT * FROM users WHERE city = ?'\n"
                "values = (city,)\n"
                "print(sql)\n"
                "print(values)\n"
                "# Вывод:\n"
                "# SELECT * FROM users WHERE city = ?\n"
                "# ('Москва',)",
                "Порядок значений в кортеже должен совпадать с порядком плейсхолдеров.",
            ),
            _card(
                "Собирай условия по алфавиту",
                "Когда фильтров несколько, договорись о стабильном порядке ключей. Тогда "
                "текст запроса и кортеж значений собираются одинаково при каждом вызове, и "
                "тесты не зависят от порядка словаря.",
                "filters = {'city': 'Москва', 'age': 20}\n"
                "parts = []\n"
                "values = []\n"
                "for key in sorted(filters):\n"
                "    parts.append(key + ' = ?')\n"
                "    values.append(filters[key])\n"
                "sql = 'SELECT * FROM users WHERE ' + ' AND '.join(parts)\n"
                "print(sql)\n"
                "print(tuple(values))\n"
                "# Вывод:\n"
                "# SELECT * FROM users WHERE age = ? AND city = ?\n"
                "# (20, 'Москва')",
                "Сортируй ключи до сборки, иначе запрос и значения могут разъехаться.",
            ),
            _card(
                "Типичная ошибка: склейка строкой",
                "Если подставить ввод прямо в SQL через `+` или f-строку, кавычка во вводе "
                "закроет строку и добавит чужое условие. Ошибка выглядит как рабочий запрос, "
                "но возвращает лишние строки. Заметь её по фрагменту ввода внутри текста SQL.",
                "name = \"Аня' OR '1'='1\"\n"
                'sql = "SELECT * FROM users WHERE name = \'" + name + "\'"\n'
                "print(sql)\n"
                "# Вывод:\n"
                "# SELECT * FROM users WHERE name = 'Аня' OR '1'='1'",
                "Значения не должны появляться в строке SQL — только в кортеже параметров.",
            ),
        ],
        [
            _choice(
                "databases-parameters",
                "Что выведет этот код?\n\n"
                "filters = {'b': 2, 'a': 1}\n"
                "keys = sorted(filters)\n"
                "print(' AND '.join(key + ' = ?' for key in keys), "
                "tuple(filters[key] for key in keys))",
                [
                    "a = ? AND b = ? (1, 2)",
                    "b = ? AND a = ? (1, 2)",
                    "a = ? AND b = ? (2, 1)",
                ],
                "a = ? AND b = ? (1, 2)",
                "sorted(filters) даёт ключи a и b, а значения берутся в том же порядке: "
                "сначала 1, затем 2.",
            ),
            _term(
                "databases-parameters",
                "Чем заменяют значения в SQL-запросе, чтобы не склеивать их со строкой?",
                ["плейсхолдер", "placeholder", "?", "знак вопроса"],
                "Плейсхолдер оставляет место для значения, а данные передаются отдельно.",
            ),
            _code(
                "databases-parameters",
                "Напиши `build_query(table, filters)`: верни пару `(sql, values)`. Ключи "
                "фильтров идут по алфавиту, на месте значений стоят `?`, сами значения — "
                "кортеж. Без фильтров верни запрос без `WHERE`.",
                "def build_query(table, filters):\n    # собери SQL с плейсхолдерами\n    pass\n",
                [
                    _holds(
                        "build_query('users', {'city': 'Москва', 'age': 20}) "
                        "== ('SELECT * FROM users WHERE age = ? AND city = ?', (20, 'Москва'))"
                    ),
                    _holds("build_query('users', {}) == ('SELECT * FROM users', ())"),
                    _holds("'Москва' not in build_query('users', {'city': 'Москва'})[0]"),
                ],
                "def build_query(table, filters):\n"
                "    keys = sorted(filters)\n"
                "    if not keys:\n"
                "        return 'SELECT * FROM ' + table, ()\n"
                "    conditions = ' AND '.join(key + ' = ?' for key in keys)\n"
                "    values = tuple(filters[key] for key in keys)\n"
                "    return 'SELECT * FROM ' + table + ' WHERE ' + conditions, values\n",
                "Сортировка ключей задаёт одинаковый порядок и в условиях, и в значениях.",
                "Сначала получи keys = sorted(filters), затем собери условия и кортеж значений.",
            ),
        ],
    ),
    _lesson(
        "databases-transactions",
        "Всё изменение целиком или никак",
        [
            _card(
                "Транзакция не оставляет половину работы",
                "Транзакция объединяет несколько изменений в одну единицу. Если все шаги "
                "удались, изменения фиксируются вместе; если хоть один не удался, не "
                "применяется ни один. Для перевода это значит, что деньги не пропадут между "
                "списанием и зачислением.",
                "balances = {'a': 100, 'b': 0}\n"
                "amount = 30\n"
                "if balances['a'] >= amount:\n"
                "    balances['a'] -= amount\n"
                "    balances['b'] += amount\n"
                "print(balances)\n"
                "# Вывод:\n"
                "# {'a': 70, 'b': 30}",
                "Проверка достаточности суммы стоит до первого изменения.",
            ),
            _card(
                "Сначала черновик, потом фиксация",
                "Удобная модель транзакции в памяти: скопируй состояние, выполни изменения "
                "на копии и замени исходное состояние только после успешной проверки. Если "
                "проверка не прошла, копия просто выбрасывается.",
                "balances = {'a': 100, 'b': 0}\n"
                "draft = dict(balances)\n"
                "draft['a'] -= 30\n"
                "draft['b'] += 30\n"
                "if draft['a'] >= 0:\n"
                "    balances = draft\n"
                "print(balances)\n"
                "# Вывод:\n"
                "# {'a': 70, 'b': 30}",
                "Фиксация — это замена старого состояния новым, а не правка по частям.",
            ),
            _card(
                "Типичная ошибка: списать до проверки",
                "Если сначала уменьшить баланс, а потом проверить результат, отказ уже "
                "поздно отменять: часть денег исчезла. Ошибку видно по нулевому или "
                "отрицательному балансу после неудачной операции. Проверяй и меняй в одной "
                "транзакции.",
                "balances = {'a': 10, 'b': 0}\n"
                "balances['a'] -= 30\n"
                "if balances['a'] < 0:\n"
                "    balances['a'] = 0\n"
                "print(balances)\n"
                "# Вывод:\n"
                "# {'a': 0, 'b': 0}",
                "При нехватке денег исходные значения должны остаться нетронутыми.",
            ),
        ],
        [
            _choice(
                "databases-transactions",
                "Что выведет этот код?\n\n"
                "balances = {'a': 10, 'b': 0}\n"
                "draft = dict(balances)\n"
                "draft['a'] -= 30\n"
                "if draft['a'] >= 0:\n"
                "    balances = draft\n"
                "print(balances)",
                [
                    "{'a': 10, 'b': 0}",
                    "{'a': 0, 'b': 0}",
                    "{'a': -20, 'b': 0}",
                ],
                "{'a': 10, 'b': 0}",
                "В черновике баланс стал -20, проверка не прошла, поэтому balances остался "
                "исходным.",
            ),
            _term(
                "databases-transactions",
                "Как называется отмена всех изменений транзакции?",
                ["rollback", "откат", "откат транзакции", "отмена"],
                "Rollback возвращает данные к состоянию до начала транзакции.",
            ),
            _code(
                "databases-transactions",
                "Напиши `transfer(balances, src, dst, amount)`: верни новый словарь после "
                "перевода. Если у `src` не хватает денег, верни исходные балансы без "
                "изменений.",
                "def transfer(balances, src, dst, amount):\n    # переведи сумму или верни копию\n    pass\n",
                [
                    _holds("transfer({'a': 100, 'b': 0}, 'a', 'b', 30) == {'a': 70, 'b': 30}"),
                    _holds("transfer({'a': 10, 'b': 0}, 'a', 'b', 30) == {'a': 10, 'b': 0}"),
                    _holds(
                        "(lambda b: (transfer(b, 'a', 'b', 30), b)[1])"
                        "({'a': 100, 'b': 0}) == {'a': 100, 'b': 0}"
                    ),
                ],
                "def transfer(balances, src, dst, amount):\n"
                "    result = dict(balances)\n"
                "    if result[src] < amount:\n"
                "        return result\n"
                "    result[src] -= amount\n"
                "    result[dst] += amount\n"
                "    return result\n",
                "Копия и ранний возврат при нехватке дают эффект «всё или ничего».",
                "Скопируй словарь, проверь баланс src, и только потом меняй обе стороны.",
            ),
        ],
    ),
    _lesson(
        "concurrency-threads-processes",
        "Поток делит память, процесс — нет",
        [
            _card(
                "Зачем вообще несколько исполнителей",
                "Один исполнитель делает задачи по очереди. Пока он ждёт ответа сети, "
                "процессор простаивает. Несколько исполнителей позволяют начать другую работу "
                "в это время. Важно выбрать модель: поток живёт в том же процессе, а процесс "
                "получает отдельную память.",
                "def work(name):\n"
                "    return name + ': готово'\n"
                "print(work('поток'))\n"
                "print(work('процесс'))\n"
                "# Вывод:\n"
                "# поток: готово\n"
                "# процесс: готово",
                "Сначала пойми, чего задача ждёт: сети, диска или вычислений.",
            ),
            _card(
                "Поток запускают и дожидаются",
                "Поток создают с функцией и аргументами, затем вызывают `start()`. Без "
                "`join()` главный поток может закончить раньше, чем рабочий успеет напечатать "
                "результат. `join()` блокирует главный поток до завершения рабочего.",
                "import threading\n"
                "\n"
                "def work(name):\n"
                "    print(name + ': готово')\n"
                "\n"
                "worker = threading.Thread(target=work, args=('поток',))\n"
                "worker.start()\n"
                "worker.join()\n"
                "print('главный поток закончил')\n"
                "# Вывод:\n"
                "# поток: готово\n"
                "# главный поток закончил",
                "join() ставят перед кодом, который рассчитывает на результат потока.",
                run=False,
            ),
            _card(
                "Типичная ошибка: ждать общих данных от процесса",
                "Процесс получает копию данных, а не общую память. Если изменить список "
                "внутри процесса, родительский список не изменится. Ошибку замечают по "
                "старому содержимому после «успешной» работы. Для общей памяти нужны потоки "
                "или явная передача результата.",
                "data = [1, 2, 3]\n"
                "copy = list(data)\n"
                "copy.append(4)\n"
                "print(data)\n"
                "print(copy)\n"
                "# Вывод:\n"
                "# [1, 2, 3]\n"
                "# [1, 2, 3, 4]",
                "Спроси, должен ли исполнитель менять именно исходный объект.",
            ),
        ],
        [
            _choice(
                "concurrency-threads-processes",
                "Что выведет этот код?\n\n"
                "import threading\n"
                "\n"
                "result = []\n"
                "def work():\n"
                "    result.append('готово')\n"
                "worker = threading.Thread(target=work)\n"
                "worker.start()\n"
                "worker.join()\n"
                "print(result[0])",
                ["готово", "ошибка", "ничего"],
                "готово",
                "join() дожидается рабочего потока, поэтому к моменту печати список уже "
                "содержит 'готово'.",
            ),
            _term(
                "concurrency-threads-processes",
                "Какая модель подходит для задач, где программа ждёт ответа сети?",
                ["потоки", "threads", "потоки threads", "поток"],
                "Пока один поток ждёт сеть, другие потоки того же процесса могут работать.",
            ),
            _code(
                "concurrency-threads-processes",
                "Напиши `split_chunks(items, n)`: раздай элементы `n` исполнителям почти "
                "поровну и сохрани порядок. Первые порции получают на один элемент больше. "
                "Пустой список даёт `n` пустых порций.",
                "def split_chunks(items, n):\n    # раздели работу между n исполнителями\n    pass\n",
                [
                    _holds("split_chunks([1, 2, 3, 4, 5], 2) == [[1, 2, 3], [4, 5]]"),
                    _holds("split_chunks([], 3) == [[], [], []]"),
                    _holds("split_chunks([1, 2, 3], 5) == [[1], [2], [3], [], []]"),
                ],
                "def split_chunks(items, n):\n"
                "    size, extra = divmod(len(items), n)\n"
                "    chunks = []\n"
                "    start = 0\n"
                "    for index in range(n):\n"
                "        end = start + size + (1 if index < extra else 0)\n"
                "        chunks.append(list(items[start:end]))\n"
                "        start = end\n"
                "    return chunks\n",
                "divmod делит длину на равные части, а остаток достаётся первым порциям.",
                "Посчитай size и extra через divmod(len(items), n), затем нарезай срезом.",
            ),
        ],
    ),
    _lesson(
        "concurrency-thread-pool",
        "Ограниченное число рабочих",
        [
            _card(
                "Пул не создаёт поток на каждую задачу",
                "Пул держит несколько постоянных рабочих и очередь задач. Каждый рабочий "
                "берёт следующую задачу, когда освобождается. Так тысяча запросов не "
                "превращается в тысячу потоков, и нагрузка остаётся предсказуемой.",
                "from concurrent.futures import ThreadPoolExecutor\n"
                "\n"
                "def double(x):\n"
                "    return x * 2\n"
                "\n"
                "with ThreadPoolExecutor(max_workers=2) as pool:\n"
                "    print(list(pool.map(double, [1, 2, 3])))\n"
                "# Вывод:\n"
                "# [2, 4, 6]",
                "max_workers ограничивает число одновременных задач, а не размер очереди.",
                run=False,
            ),
            _card(
                "map возвращает результаты по порядку входа",
                "`pool.map` похож на обычный `map`: ты передаёшь функцию и список, а получаешь "
                "результаты в том же порядке. Даже если третья задача закончилась раньше "
                "первой, её результат не перескочит вперёд.",
                "def pool_map(func, items):\n"
                "    return [func(item) for item in items]\n"
                "\n"
                "print(pool_map(lambda x: x * 2, [1, 2, 3]))\n"
                "# Вывод:\n"
                "# [2, 4, 6]",
                "Порядок результатов определяет входной список, а не скорость задач.",
            ),
            _card(
                "Типичная ошибка: складывать по мере готовности",
                "Если добавлять результат сразу после завершения задачи, порядок станет "
                "порядком завершения. При разной скорости задач список перемешается. Ошибку "
                "видно по несовпадению позиций входа и выхода. Собирай результаты по индексам "
                "или возвращай их через `map`.",
                "items = [1, 2, 3]\n"
                "results = []\n"
                "for item in reversed(items):\n"
                "    results.append(item * 2)\n"
                "print(results)\n"
                "# Вывод:\n"
                "# [6, 4, 2]",
                "Сверь первый результат с первым элементом входа.",
            ),
        ],
        [
            _choice(
                "concurrency-thread-pool",
                "Что выведет этот код?\n\n"
                "def run(func, items):\n"
                "    return [func(x) for x in items]\n"
                "\n"
                "print(run(lambda x: x + 1, [1, 2, 3]))",
                ["[2, 3, 4]", "[1, 2, 3]", "[3, 4, 5]"],
                "[2, 3, 4]",
                "Функция прибавляет единицу к каждому элементу и сохраняет порядок входа.",
            ),
            _term(
                "concurrency-thread-pool",
                "Сколько задач одновременно выполняет пул с max_workers=4?",
                ["4", "четыре", "не больше 4", "4 задачи"],
                "max_workers задаёт верхнюю границу числа рабочих, а не общее число задач.",
            ),
            _code(
                "concurrency-thread-pool",
                "Напиши `pool_map(func, items, workers)`: верни результаты в порядке входа "
                "независимо от числа рабочих. `workers` ограничивает параллелизм, но не "
                "меняет порядок.",
                "def pool_map(func, items, workers):\n    # верни результаты в порядке входа\n    pass\n",
                [
                    _holds("pool_map(lambda x: x * 2, [1, 2, 3], 2) == [2, 4, 6]"),
                    _holds("pool_map(lambda x: x * 2, [1, 2, 3], 1) == [2, 4, 6]"),
                    _holds("pool_map(lambda x: x * 2, [], 2) == []"),
                ],
                "def pool_map(func, items, workers):\n    return [func(item) for item in items]\n",
                "Результат зависит от входа, а workers — только от того, сколько задач "
                "разрешено делать одновременно.",
                "Собери результаты в список, проходя items слева направо.",
            ),
        ],
    ),
    _lesson(
        "concurrency-locks",
        "Проверка и изменение под одним замком",
        [
            _card(
                "Гонка ломает общее состояние",
                "Когда несколько исполнителей читают и меняют одно значение, порядок "
                "операций становится непредсказуемым. Два исполнителя могут прочитать "
                "старое значение и оба записать новое — одно изменение потеряется. "
                "Блокировка пропускает к общему состоянию только одного.",
                "import threading\n"
                "\n"
                "balance = 0\n"
                "lock = threading.Lock()\n"
                "\n"
                "def add():\n"
                "    global balance\n"
                "    with lock:\n"
                "        balance += 1\n"
                "\n"
                "workers = [threading.Thread(target=add) for _ in range(100)]\n"
                "for worker in workers:\n"
                "    worker.start()\n"
                "for worker in workers:\n"
                "    worker.join()\n"
                "print(balance)\n"
                "# Вывод:\n"
                "# 100",
                "with lock: держит замок ровно на время своего блока.",
                run=False,
            ),
            _card(
                "Решай и меняй одним шагом",
                "Проверка «хватает ли денег» и списание должны быть одной неделимой "
                "операцией. Тогда второй исполнитель не сможет вклиниться между проверкой и "
                "изменением. В коде это выглядит как один блок под замком или один метод.",
                "balance = 100\n"
                "amount = 70\n"
                "if balance >= amount:\n"
                "    balance -= amount\n"
                "    print(True)\n"
                "else:\n"
                "    print(False)\n"
                "print(balance)\n"
                "# Вывод:\n"
                "# True\n"
                "# 30",
                "Внутри шага не должно быть паузы, в которую может войти другой исполнитель.",
            ),
            _card(
                "Типичная ошибка: проверка на старых данных",
                "Если сохранить результат проверки, а потом изменить данные, решение "
                "применится к устаревшему состоянию. Ошибку видно по операции, которая прошла "
                "при недостатке средств. Перечитывай состояние и проверяй его в том же "
                "защищённом шаге.",
                "balance = 100\n"
                "allowed = balance >= 70\n"
                "balance -= 90\n"
                "if allowed:\n"
                "    balance -= 70\n"
                "print(balance)\n"
                "# Вывод:\n"
                "# -60",
                "Смотри не только на итог, но и на момент, когда принималось решение.",
            ),
        ],
        [
            _choice(
                "concurrency-locks",
                "Что выведет этот код?\n\n"
                "balance = 100\n"
                "def withdraw(amount):\n"
                "    global balance\n"
                "    if balance >= amount:\n"
                "        balance -= amount\n"
                "        return True\n"
                "    return False\n"
                "print(withdraw(70), withdraw(70), balance)",
                ["True False 30", "False True 30", "True True 30"],
                "True False 30",
                "Первый вызов списывает 70 и оставляет 30, второй видит нехватку и возвращает "
                "False.",
            ),
            _term(
                "concurrency-locks",
                "Что защищает общее состояние от одновременного изменения?",
                ["блокировка", "lock", "мьютекс", "mutex", "замок"],
                "Блокировка делает проверку и изменение неделимым шагом для других исполнителей.",
            ),
            _code(
                "concurrency-locks",
                "Напиши класс `Account(balance)` с методом `withdraw(amount)`: если денег "
                "хватает, спиши сумму и верни `True`, иначе верни `False` и не меняй баланс. "
                "Проверка и списание должны быть одним шагом.",
                "class Account:\n"
                "    def __init__(self, balance):\n"
                "        # сохрани баланс\n"
                "        pass\n"
                "\n"
                "    def withdraw(self, amount):\n"
                "        # проверь баланс и спиши сумму\n"
                "        pass\n",
                [
                    _holds(
                        "(lambda a: [a.withdraw(70) is True, a.withdraw(70) is False, "
                        "a.balance == 30])(Account(100)) == [True, True, True]"
                    ),
                    _holds(
                        "(lambda a: [a.withdraw(101) is False, a.balance])(Account(100)) "
                        "== [True, 100]"
                    ),
                    _holds(
                        "(lambda a: [a.withdraw(100) is True, a.balance])(Account(100)) "
                        "== [True, 0]"
                    ),
                ],
                "class Account:\n"
                "    def __init__(self, balance):\n"
                "        self.balance = balance\n"
                "\n"
                "    def withdraw(self, amount):\n"
                "        if self.balance < amount:\n"
                "            return False\n"
                "        self.balance -= amount\n"
                "        return True\n",
                "Метод сначала проверяет баланс, а списание делает только после успешной "
                "проверки — без промежуточного возврата управления.",
                "В withdraw сначала сравни self.balance с amount, затем меняй balance.",
            ),
        ],
    ),
    _lesson(
        "concurrency-queues",
        "Очередь развязывает создание и обработку",
        [
            _card(
                "Задачи ждут в очереди по порядку",
                "Очередь хранит задачи и отдаёт их в порядке прихода: first in, first out. "
                "Создатель работы кладёт задачи, обработчик забирает их с другого конца. "
                "Для частых операций с началом берут `collections.deque`.",
                "from collections import deque\n"
                "\n"
                "queue = deque(['a', 'b'])\n"
                "print(queue.popleft())\n"
                "print(list(queue))\n"
                "# Вывод:\n"
                "# a\n"
                "# ['b']",
                "popleft() снимает начало, append() добавляет в конец.",
            ),
            _card(
                "Верни задачу в конец, если нужно повторить",
                "Иногда задачу нельзя выполнить с первого раза. Тогда её возвращают в конец "
                "очереди, чтобы обработать позже, после остальных. Важно снять пометку, иначе "
                "задача будет возвращаться бесконечно.",
                "from collections import deque\n"
                "\n"
                "queue = deque(['a', 'b!', 'c'])\n"
                "done = []\n"
                "while queue:\n"
                "    task = queue.popleft()\n"
                "    if task.endswith('!'):\n"
                "        queue.append(task[:-1])\n"
                "    else:\n"
                "        done.append(task)\n"
                "print(done)\n"
                "# Вывод:\n"
                "# ['a', 'c', 'b']",
                "Срез task[:-1] убирает восклицательный знак перед повторной постановкой.",
            ),
            _card(
                "Типичная ошибка: pop вместо popleft",
                "`pop()` без аргумента снимает последний элемент, поэтому очередь начинает "
                "работать как стек. Порядок задач меняется, хотя код выглядит рабочим. "
                "Ошибку видно по тому, что первой обработана последняя добавленная задача.",
                "from collections import deque\n"
                "\n"
                "queue = deque(['a', 'b', 'c'])\n"
                "print(queue.pop())\n"
                "print(list(queue))\n"
                "# Вывод:\n"
                "# c\n"
                "# ['a', 'b']",
                "Для FIFO нужен popleft(): он забирает именно начало очереди.",
            ),
        ],
        [
            _choice(
                "concurrency-queues",
                "Что выведет этот код?\n\n"
                "from collections import deque\n"
                "\n"
                "queue = deque([1, 2, 3])\n"
                "queue.append(queue.popleft())\n"
                "print(list(queue))",
                ["[2, 3, 1]", "[3, 2, 1]", "[1, 2, 3]"],
                "[2, 3, 1]",
                "popleft() забирает 1 из начала, append() ставит её в конец; остальные "
                "элементы сдвигаются влево.",
            ),
            _term(
                "concurrency-queues",
                "По какому правилу очередь отдаёт задачи?",
                ["FIFO", "первым пришёл — первым вышел", "первым пришел первым вышел", "fifo"],
                "FIFO означает first in, first out: раньше пришла — раньше обработана.",
            ),
            _code(
                "concurrency-queues",
                "Напиши `process_queue(tasks)`: обработай задачи через `collections.deque` в "
                "порядке FIFO. Задачу с именем на `!` один раз верни в конец очереди без `!`. "
                "Верни список выполненных задач.",
                "from collections import deque\n"
                "\n"
                "def process_queue(tasks):\n"
                "    # обработай задачи в порядке очереди\n"
                "    pass\n",
                [
                    _holds("process_queue(['a', 'b!', 'c']) == ['a', 'c', 'b']"),
                    _holds("process_queue(['b!']) == ['b']"),
                    _holds("process_queue([]) == []"),
                    _holds("process_queue(['a!', 'b!']) == ['a', 'b']"),
                ],
                "from collections import deque\n"
                "\n"
                "def process_queue(tasks):\n"
                "    queue = deque(tasks)\n"
                "    done = []\n"
                "    while queue:\n"
                "        task = queue.popleft()\n"
                "        if task.endswith('!'):\n"
                "            queue.append(task[:-1])\n"
                "        else:\n"
                "            done.append(task)\n"
                "    return done\n",
                "deque и popleft() дают FIFO, а возврат в конец делается через append().",
                "Создай queue = deque(tasks), забирай popleft() и возвращай помеченные задачи "
                "в конец.",
            ),
        ],
    ),
]
