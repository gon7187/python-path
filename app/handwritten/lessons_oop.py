"""Рукописные уроки 65–72: проектирование и расширение классов."""

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
        "id": "oop-design-init",
        "theory": [
            _card(
                "Что такое конструктор и зачем он нужен",
                "Конструктор — это метод `__init__`, который Python вызывает сам в момент "
                "создания объекта. В нём ты задаёшь начальное состояние: какие данные объект "
                "получает при рождении. Без конструктора пришлось бы создавать пустой объект "
                "и вручную добавлять каждое поле. С конструктором объект сразу готов к работе.",
                """class Task:
    def __init__(self, title):
        self.title = title

task = Task('Купить хлеб')
print(task.title)
# Вывод:
# Купить хлеб""",
                "`__init__` не создаёт объект, а наполняет его данными.",
            ),
            _card(
                "Как пользоваться: сохрани каждый аргумент",
                "Внутри `__init__` аргументы превращаются в атрибуты через `self`. Пиши "
                "`self.x = x`, тогда значение останется в объекте и после выхода из метода. "
                "`self` — это ссылка на конкретный экземпляр, поэтому два объекта хранят свои "
                "значения независимо. В примере две точки помнят разные координаты.",
                """class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

first = Point(1, 2)
second = Point(10, 20)
print(first.x + second.y)
# Вывод:
# 21""",
                "Передавай в конструктор ровно те данные, без которых объект не имеет смысла.",
            ),
            _card(
                "Типичная ошибка: присвоить значение не в self",
                "Если написать `title = title` вместо `self.title = title`, значение останется "
                "в локальной переменной и исчезнет после выхода из конструктора. Ошибка не "
                "падает: объект создаётся, только нужного атрибута в нём нет. Заметь её через "
                "`hasattr`: если поле не находится, проверь, есть ли перед именем `self`.",
                """class Task:
    def __init__(self, title):
        title = title

task = Task('Отчёт')
print(hasattr(task, 'title'))
# Вывод:
# False""",
                "Атрибут появляется только при присваивании в `self.имя`.",
            ),
        ],
        "questions": [
            _choice(
                "oop-design-init",
                "Что выведет код?\n\n"
                "class Point:\n"
                "    def __init__(self, x, y):\n"
                "        self.x = x\n"
                "        self.y = y\n"
                "\n"
                "point = Point(2, 5)\n"
                "print(point.x * point.y)",
                ["10", "15", "20", "25"],
                "10",
                "Конструктор сохранил 2 и 5 в поля, а `point.x * point.y` перемножил их.",
            ),
            _term(
                "oop-design-init",
                "Какой метод класса вызывается автоматически при создании объекта?",
                ["__init__", "init", "конструктор", "метод __init__"],
                "При создании экземпляра Python сам вызывает `__init__` с переданными аргументами.",
            ),
            _code(
                "oop-design-init",
                "Создай `class Point` с конструктором `__init__(self, x, y)` и методом "
                "`distance_to_origin()`. Метод возвращает расстояние от точки до начала координат.",
                """class Point:
    def __init__(self, x, y):
        pass

    def distance_to_origin(self):
        pass
""",
                [
                    {"kind": "call", "call": "Point(3, 4).distance_to_origin()", "expected": 5.0},
                    {"kind": "call", "call": "Point(0, 0).distance_to_origin()", "expected": 0.0},
                    {"kind": "call", "call": "Point(0, 0).x", "expected": 0},
                ],
                """class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
""",
                "Конструктор сохранил координаты в экземпляре, а метод прочитал их через `self`.",
                "Сохрани `x` и `y` в `self`, а расстояние посчитай как "
                "`(self.x ** 2 + self.y ** 2) ** 0.5`.",
            ),
        ],
    },
    {
        "id": "oop-design-repr-str",
        "theory": [
            _card(
                "Что такое __str__ и зачем он нужен",
                "`__str__` возвращает строку для человека: её печатает `print` и показывает "
                "большинство интерфейсов. Без него Python печатает служебное представление с "
                "адресом объекта, и по нему ничего не понять. Метод должен вернуть именно "
                "строку, а не напечатать её. Тогда объект читается как обычное значение.",
                """class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f'{self.amount} {self.currency}'

print(Money(100, 'RUB'))
# Вывод:
# 100 RUB""",
                "`print(obj)` вызывает `__str__`, если он определён.",
            ),
            _card(
                "Как пользоваться: два взгляда на объект",
                "`__str__` нужен пользователю, а `__repr__` — разработчику: по нему удобно "
                "видеть объект в списке и отладчике. В `__repr__` принято писать выражение, "
                "похожее на код создания объекта. `!r` добавляет кавычки вокруг строки, чтобы "
                "представление можно было скопировать в код. Проверяй оба метода отдельно "
                "через `str()` и `repr()`.",
                """class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f'{self.amount} {self.currency}'

    def __repr__(self):
        return f'Money({self.amount}, {self.currency!r})'

money = Money(5, 'USD')
print(str(money))
print(repr(money))
# Вывод:
# 5 USD
# Money(5, 'USD')""",
                "Для строкового поля в `__repr__` ставь `!r`.",
            ),
            _card(
                "Типичная ошибка: потерять кавычки в __repr__",
                "Если в `__repr__` вывести строку без `!r`, кавычки исчезнут. `Money(5, USD)` "
                "выглядит как вызов с неизвестным именем, а не как данные, которые можно "
                "скопировать в код. Заметь это по выводу `repr()`: строковые поля должны быть "
                "в кавычках. Исправление — `{self.currency!r}`.",
                """class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f'Money({self.amount}, {self.currency})'

print(repr(Money(5, 'USD')))
# Вывод:
# Money(5, USD)""",
                "Сравни `repr(obj)` с тем, как ты сам записал бы создание объекта.",
            ),
        ],
        "questions": [
            _choice(
                "oop-design-repr-str",
                "Что выведет код?\n\n"
                "class Money:\n"
                "    def __init__(self, amount):\n"
                "        self.amount = amount\n"
                "\n"
                "    def __str__(self):\n"
                "        return f'{self.amount} руб.'\n"
                "\n"
                "    def __repr__(self):\n"
                "        return f'Money({self.amount})'\n"
                "\n"
                "print(repr(Money(7)))",
                ["Money(7)", "Money[7]", "Money(7.0)", "Money('7')"],
                "Money(7)",
                "`repr` собирает `Money(...)` из числа, а `__str__` с рублями здесь не участвует.",
            ),
            _term(
                "oop-design-repr-str",
                "Какой метод задаёт представление объекта для разработчика — в отладчике и списках?",
                ["__repr__", "repr", "метод __repr__", "__repr__()"],
                "`__repr__` показывает объект разработчику, а `__str__` — пользователю.",
            ),
            _code(
                "oop-design-repr-str",
                "Создай `class Money` с конструктором `__init__(self, amount, currency)`. "
                "`__str__` должен возвращать `'100 RUB'`, а `__repr__` — `\"Money(100, 'RUB')\"`.",
                """class Money:
    def __init__(self, amount, currency):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass
""",
                [
                    {"kind": "call", "call": "str(Money(100, 'RUB'))", "expected": "100 RUB"},
                    {
                        "kind": "call",
                        "call": "repr(Money(5, 'USD'))",
                        "expected": "Money(5, 'USD')",
                    },
                    {
                        "kind": "call",
                        "call": "str(Money(0, 'EUR'))",
                        "expected": "0 EUR",
                    },
                ],
                """class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return f'{self.amount} {self.currency}'

    def __repr__(self):
        return f'Money({self.amount}, {self.currency!r})'
""",
                "`__str__` показывает сумму и валюту человеку, а `__repr__` добавляет кавычки "
                "вокруг валюты через `!r`.",
                "В `__repr__` используй `{self.currency!r}`, чтобы вокруг кода валюты "
                "появились кавычки.",
            ),
        ],
    },
    {
        "id": "oop-design-class-instance",
        "theory": [
            _card(
                "Что такое атрибут класса и атрибут экземпляра",
                "Атрибут класса объявлен прямо в теле класса и общий для всех экземпляров. "
                "Атрибут экземпляра создаётся через `self` в методе и принадлежит только "
                "этому объекту. В примере `species` один на всех, а `name` у каждой кошки "
                "свой. Python сначала ищет имя у экземпляра, а потом у класса.",
                """class Cat:
    species = 'кошка'

    def __init__(self, name):
        self.name = name

cat = Cat('Мурка')
print(cat.species)
print(cat.name)
# Вывод:
# кошка
# Мурка""",
                "Общее для всех — в классе, личное — в экземпляре.",
            ),
            _card(
                "Как пользоваться: общее поведение и личные данные",
                "Классовое поле удобно для того, что действительно одинаково: вид животного, "
                "валюта по умолчанию, версия формата. Личные данные передавай в конструктор и "
                "сохраняй через `self`. Тогда метод может соединить общее и личное в одной "
                "строке. Если поменять поле у одного экземпляра, остальные сохранят классовое "
                "значение.",
                """class Cat:
    species = 'кошка'

    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f'{self.name}, {self.species}'

print(Cat('Барсик').introduce())
# Вывод:
# Барсик, кошка""",
                "Метод читает оба вида атрибутов через `self` одинаково.",
            ),
            _card(
                "Типичная ошибка: изменяемый атрибут класса",
                "Список в теле класса создаётся один раз и делится между всеми экземплярами. "
                "Если одна кошка добавит игрушку, она появится и у другой. Ошибка тихая: код "
                "работает, но данные протекают между объектами. Заметь её по неожиданно общему "
                "списку; личные списки создавай в `__init__` через `self.toys = []`.",
                """class Cat:
    toys = []

    def __init__(self, name):
        self.name = name

cat_a = Cat('Мурка')
cat_b = Cat('Барсик')
cat_a.toys.append('мяч')
print(cat_b.toys)
# Вывод:
# ['мяч']""",
                "Изменяемые данные всегда создавай внутри `__init__`.",
            ),
        ],
        "questions": [
            _choice(
                "oop-design-class-instance",
                "Что выведет код?\n\n"
                "class Cat:\n"
                "    species = 'кошка'\n"
                "\n"
                "    def __init__(self, name):\n"
                "        self.name = name\n"
                "\n"
                "cat = Cat('Мурка')\n"
                "cat.species = 'тигр'\n"
                "print(Cat('Барсик').species)",
                ["кошка", "тигр", "Мурка", "Барсик"],
                "кошка",
                "Присваивание создало атрибут только у `cat`, а классовое поле осталось прежним.",
            ),
            _term(
                "oop-design-class-instance",
                "Как называется атрибут, заданный в теле класса и общий для всех экземпляров?",
                [
                    "атрибут класса",
                    "class attribute",
                    "классовый атрибут",
                    "атрибут класса (class attribute)",
                ],
                "Поле в теле класса принадлежит классу, поэтому его видят все экземпляры.",
            ),
            _code(
                "oop-design-class-instance",
                "Создай `class Cat` с атрибутом класса `species = 'кошка'` и конструктором "
                "`__init__(self, name)`, который сохраняет имя экземпляра.",
                """class Cat:
    species = 'кошка'

    def __init__(self, name):
        pass
""",
                [
                    {"kind": "call", "call": "Cat('Мурка').species", "expected": "кошка"},
                    {"kind": "call", "call": "Cat('Барсик').name", "expected": "Барсик"},
                    {"kind": "call", "call": "Cat('Барсик').species", "expected": "кошка"},
                ],
                """class Cat:
    species = 'кошка'

    def __init__(self, name):
        self.name = name
""",
                "`species` объявлен в теле класса и общий, а `name` сохранён в экземпляре.",
                "Оставь `species` на уровне класса, а в `__init__` присвой `self.name = name`.",
            ),
        ],
    },
    {
        "id": "oop-design-composition",
        "theory": [
            _card(
                "Что такое композиция",
                "Композиция — это когда один объект хранит другой как свою часть. Машина не "
                "является двигателем, она содержит двигатель. Внутри `Car` лежит готовый "
                "`Engine`, и машина пользуется его данными через `self.engine`. Так части "
                "можно менять и проверять отдельно друг от друга.",
                """class Engine:
    def __init__(self, power):
        self.power = power

class Car:
    def __init__(self, engine):
        self.engine = engine

car = Car(Engine(150))
print(car.engine.power)
# Вывод:
# 150""",
                "Композиция отвечает на вопрос «из чего состоит объект».",
            ),
            _card(
                "Как пользоваться: собери объект из готовых частей",
                "Создавай части снаружи и передавай их в конструктор. Тогда `Car` не знает, "
                "как собирать двигатель, и не дублирует его логику. Метод `describe` читает "
                "`self.engine.power` и добавляет своё оформление. Если завтра появится другой "
                "двигатель, машине будет достаточно того же метода.",
                """class Engine:
    def __init__(self, power):
        self.power = power

class Car:
    def __init__(self, engine):
        self.engine = engine

    def describe(self):
        return f'Машина с двигателем {self.engine.power} л.с.'

print(Car(Engine(150)).describe())
# Вывод:
# Машина с двигателем 150 л.с.""",
                "Передавай зависимость аргументом, а не создавай её жёстко внутри.",
            ),
            _card(
                "Типичная ошибка: наследование вместо композиции",
                "Иногда `Car` делают наследником `Engine`, потому что хочется взять готовое "
                "поле `power`. Тогда машина становится разновидностью двигателя, хотя это не "
                "так. Проверить просто: `isinstance(car, Engine)` истинно, а отдельного "
                "`car.engine` нет. Если объект «состоит из», выбирай поле, а не родителя.",
                """class Engine:
    def __init__(self, power):
        self.power = power

class Car(Engine):
    def __init__(self, power):
        self.power = power

car = Car(150)
print(isinstance(car, Engine))
print(hasattr(car, 'engine'))
# Вывод:
# True
# False""",
                "Наследование говорит «является», композиция — «содержит».",
            ),
        ],
        "questions": [
            _choice(
                "oop-design-composition",
                "Что выведет код?\n\n"
                "class Engine:\n"
                "    def __init__(self, power):\n"
                "        self.power = power\n"
                "\n"
                "class Car:\n"
                "    def __init__(self, engine):\n"
                "        self.engine = engine\n"
                "\n"
                "print([Car(Engine(p)).engine.power for p in [100, 150]])",
                ["[100, 150]", "[150, 100]", "[150, 150]", "[100, 100]"],
                "[100, 150]",
                "Каждый `Car` получил свой `Engine`, а обход сохранил порядок мощностей.",
            ),
            _term(
                "oop-design-composition",
                "Как называется отношение, когда один объект хранит другой объект как свою часть?",
                ["композиция", "composition", "композиция объектов", "has-a"],
                "Объект-часть хранится в поле, поэтому это композиция, а не наследование.",
            ),
            _code(
                "oop-design-composition",
                "Создай `class Engine` с конструктором `__init__(self, power)` и `class Car` "
                "с конструктором `__init__(self, engine)`. Метод `describe()` возвращает "
                "`'Машина с двигателем 150 л.с.'` для `Car(Engine(150))`.",
                """class Engine:
    def __init__(self, power):
        pass

class Car:
    def __init__(self, engine):
        pass

    def describe(self):
        pass
""",
                [
                    {
                        "kind": "call",
                        "call": "Car(Engine(150)).describe()",
                        "expected": "Машина с двигателем 150 л.с.",
                    },
                    {
                        "kind": "call",
                        "call": "Car(Engine(0)).describe()",
                        "expected": "Машина с двигателем 0 л.с.",
                    },
                ],
                """class Engine:
    def __init__(self, power):
        self.power = power

class Car:
    def __init__(self, engine):
        self.engine = engine

    def describe(self):
        return f'Машина с двигателем {self.engine.power} л.с.'
""",
                "`Car` хранит готовый `Engine` в поле и читает его мощность в `describe`.",
                "Сохрани двигатель как `self.engine`, а в строке возьми `self.engine.power`.",
            ),
        ],
    },
    {
        "id": "oop-advanced-inheritance",
        "theory": [
            _card(
                "Что такое наследование",
                "Наследование позволяет новому классу взять поведение родителя и добавить своё. "
                "`Dog` является `Animal`, поэтому получает его методы. Родительский конструктор "
                "вызывают через `super().__init__(...)`, чтобы общее состояние создалось один "
                "раз. Дочерний класс дополняет родителя, а не копирует его.",
                """class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)

dog = Dog('Шарик')
print(dog.name)
# Вывод:
# Шарик""",
                "Наследование — отношение «является».",
            ),
            _card(
                "Как пользоваться: расширяй, а не переписывай",
                "Если метод родителя почти подходит, переопредели только отличие. В примере "
                "`Animal.speak` возвращает заглушку, а `Dog.speak` добавляет имя и лай. "
                "`super().__init__` сохраняет `name` в том же месте, где это делает родитель. "
                "Так изменение родительского конструктора подхватится всеми наследниками.",
                """class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return '...'

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)

    def speak(self):
        return f'{self.name}: Гав'

print(Dog('Шарик').speak())
# Вывод:
# Шарик: Гав""",
                "Сначала вызови `super().__init__`, потом добавляй свои поля.",
            ),
            _card(
                "Типичная ошибка: не вызвать super().__init__",
                "Если дочерний конструктор просто содержит `pass`, родительское состояние не "
                "создаётся. Объект появляется, но `name` в нём нет, и обращение к нему упадёт "
                "позже, в другом методе. Заметь это через `hasattr` сразу после создания. "
                "Исправление — вызвать `super().__init__(name)` первой строкой.",
                """class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name):
        pass

dog = Dog('Шарик')
print(hasattr(dog, 'name'))
# Вывод:
# False""",
                "Наследник не получает атрибуты родителя без вызова его конструктора.",
            ),
        ],
        "questions": [
            _choice(
                "oop-advanced-inheritance",
                "Что выведет код?\n\n"
                "class Animal:\n"
                "    def speak(self):\n"
                "        return '...'\n"
                "\n"
                "class Dog(Animal):\n"
                "    def speak(self):\n"
                "        return 'Гав'\n"
                "\n"
                "print(Animal().speak(), Dog().speak())",
                ["... Гав", "Гав ...", "... ...", "Гав Гав"],
                "... Гав",
                "`Animal` использует свой метод, а `Dog` переопределил его и вернул лай.",
            ),
            _term(
                "oop-advanced-inheritance",
                "Какая функция вызывает метод родительского класса из дочернего?",
                ["super", "super()", "вызов super", "функция super"],
                "`super()` даёт доступ к методам родителя, в том числе к его конструктору.",
            ),
            _code(
                "oop-advanced-inheritance",
                "Создай `class Animal` с конструктором `__init__(self, name)` и `class Dog`, "
                "который наследует `Animal`, вызывает `super().__init__(name)` и возвращает из "
                "`speak()` строку `'Шарик: Гав'`.",
                """class Animal:
    def __init__(self, name):
        pass

class Dog(Animal):
    def __init__(self, name):
        pass

    def speak(self):
        pass
""",
                [
                    {"kind": "call", "call": "Dog('Шарик').speak()", "expected": "Шарик: Гав"},
                    {"kind": "call", "call": "Dog('Шарик').name", "expected": "Шарик"},
                    {"kind": "call", "call": "Dog('').speak()", "expected": ": Гав"},
                ],
                """class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)

    def speak(self):
        return f'{self.name}: Гав'
""",
                "`Dog` унаследовал `Animal`, сохранил имя через `super().__init__` и добавил лай.",
                "В `Dog.__init__` вызови `super().__init__(name)`, а в `speak` верни "
                "f-строку с `self.name`.",
            ),
        ],
    },
    {
        "id": "oop-advanced-properties",
        "theory": [
            _card(
                "Что такое свойство",
                "Свойство — это метод, к которому обращаются как к атрибуту. Декоратор "
                "`@property` прячет вызов скобок: снаружи `temperature.fahrenheit` выглядит "
                "как поле. Внутри может быть формула, проверка или обращение к другому полю. "
                "Так удобное имя не раскрывает, как значение получено.",
                """class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

temperature = Temperature(100)
print(temperature.fahrenheit)
# Вывод:
# 212.0""",
                "Свойство читают без скобок: `obj.value`, а не `obj.value()`.",
            ),
            _card(
                "Как пользоваться: вычисляемое значение и запись",
                "Свойство хорошо подходит для производного значения, которое не нужно хранить "
                "дважды. Читая `fahrenheit`, ты получаешь пересчёт из `celsius`. Сеттер через "
                "`@fahrenheit.setter` переводит записанное значение обратно в `celsius`. "
                "Снаружи работают с привычной шкалой, а внутри хранится одно поле.",
                """class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9

temperature = Temperature(0)
temperature.fahrenheit = 212
print(temperature.celsius)
# Вывод:
# 100.0""",
                "Храни одно исходное значение, остальное вычисляй.",
            ),
            _card(
                "Типичная ошибка: забыть @property",
                "Без декоратора метод остаётся методом: `temperature.fahrenheit` возвращает "
                "функцию, а не число. `print` покажет её, вычисления сломаются, и ошибка "
                "проявится далеко от места определения. Заметь это через `callable`: у "
                "настоящего свойства результат — число. Исправление — поставить `@property` "
                "над методом.",
                """class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

temperature = Temperature(100)
print(callable(temperature.fahrenheit))
print(temperature.fahrenheit())
# Вывод:
# True
# 212.0""",
                "Если для получения значения нужны скобки, свойство не сработало.",
            ),
        ],
        "questions": [
            _choice(
                "oop-advanced-properties",
                "Что выведет код?\n\n"
                "class Temperature:\n"
                "    def __init__(self, celsius):\n"
                "        self.celsius = celsius\n"
                "\n"
                "    @property\n"
                "    def fahrenheit(self):\n"
                "        return self.celsius * 9 / 5 + 32\n"
                "\n"
                "temperature = Temperature(0)\n"
                "print(temperature.fahrenheit)",
                ["32.0", "0.00", "100.0", "212.0"],
                "32.0",
                "0 градусов по Цельсию переводится в 32 градуса по Фаренгейту, и деление даёт float.",
            ),
            _term(
                "oop-advanced-properties",
                "Каким декоратором помечают метод, чтобы обращаться к нему как к атрибуту?",
                ["@property", "property", "декоратор property", "@property()"],
                "`@property` превращает метод в вычисляемый атрибут без скобок при чтении.",
            ),
            _code(
                "oop-advanced-properties",
                "Создай `class Temperature` с конструктором `__init__(self, celsius)` и "
                "свойством `fahrenheit`, которое переводит температуру по формуле "
                "`celsius * 9 / 5 + 32`.",
                """class Temperature:
    def __init__(self, celsius):
        pass

    def fahrenheit(self):
        pass
""",
                [
                    {"kind": "call", "call": "Temperature(100).fahrenheit", "expected": 212.0},
                    {"kind": "call", "call": "Temperature(0).fahrenheit", "expected": 32.0},
                    {"kind": "call", "call": "Temperature(-40).fahrenheit", "expected": -40.0},
                ],
                """class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32
""",
                "`@property` позволил читать `fahrenheit` без скобок, а формула пересчитала шкалу.",
                "Поставь `@property` над `fahrenheit` и верни `self.celsius * 9 / 5 + 32`.",
            ),
        ],
    },
    {
        "id": "oop-advanced-protocols",
        "theory": [
            _card(
                "Что такое протокол и утиная типизация",
                "Протокол — это набор методов, которых достаточно для работы с объектом. "
                "Python часто не спрашивает класс, а просто вызывает нужный метод: если у "
                "объекта есть `area()`, его можно считать фигурой. Это называют утиной "
                "типизацией. Разные классы подходят под один код без общего родителя.",
                """class Square:
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

for shape in [Square(2), Rect(2, 3)]:
    print(shape.area())
# Вывод:
# 4
# 6""",
                "Смотри на методы, а не на имя класса.",
            ),
            _card(
                "Как пользоваться: общий код для разных классов",
                "Функция `total_area` перебирает фигуры и складывает `shape.area()`. Ей не "
                "важно, квадрат это или прямоугольник: важен только метод. Поэтому новый "
                "класс с `area()` сразу работает со старой функцией. Держи протокол "
                "маленьким: один-два метода, которые действительно нужны.",
                """class Square:
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

def total_area(shapes):
    return sum(shape.area() for shape in shapes)

print(total_area([Square(2), Rect(2, 3)]))
# Вывод:
# 10""",
                "Проверяй, что функция вызывает только методы протокола.",
            ),
            _card(
                "Типичная ошибка: проверять класс через isinstance",
                "Если функция принимает только `Square`, прямоугольник молча выпадет из "
                "суммы. Исключения не будет: результат просто станет меньше. Заметь это по "
                "количеству обработанных фигур или по сумме, которая не сходится. Убирай "
                "проверку класса, если все объекты умеют нужный метод.",
                """class Square:
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

def total_area(shapes):
    total = 0
    for shape in shapes:
        if isinstance(shape, Square):
            total += shape.area()
    return total

print(total_area([Square(2), Rect(2, 3)]))
# Вывод:
# 4""",
                "Сравни количество фигур на входе и слагаемых в сумме.",
            ),
        ],
        "questions": [
            _choice(
                "oop-advanced-protocols",
                "Что выведет код?\n\n"
                "class Square:\n"
                "    def __init__(self, side):\n"
                "        self.side = side\n"
                "\n"
                "    def area(self):\n"
                "        return self.side ** 2\n"
                "\n"
                "class Rect:\n"
                "    def __init__(self, w, h):\n"
                "        self.w = w\n"
                "        self.h = h\n"
                "\n"
                "    def area(self):\n"
                "        return self.w * self.h\n"
                "\n"
                "def total_area(shapes):\n"
                "    return sum(shape.area() for shape in shapes)\n"
                "\n"
                "print(total_area([Square(3), Rect(2, 4)]))",
                ["17", "14", "20", "24"],
                "17",
                "Квадрат дал 9, прямоугольник — 8, а `sum` сложил оба значения.",
            ),
            _term(
                "oop-advanced-protocols",
                "Как называется подход, когда код опирается на наличие метода, а не на класс?",
                [
                    "утиная типизация",
                    "duck typing",
                    "duck-typing",
                    "утиная типизация (duck typing)",
                ],
                "Утиная типизация проверяет поведение: есть метод — объект подходит.",
            ),
            _code(
                "oop-advanced-protocols",
                "Создай `class Square` с `area()`, `class Rect` с `area()` и функцию "
                "`total_area(shapes)`, которая складывает площади всех фигур через их общий "
                "метод, без проверки класса.",
                """class Square:
    def __init__(self, side):
        pass

    def area(self):
        pass

class Rect:
    def __init__(self, w, h):
        pass

    def area(self):
        pass

def total_area(shapes):
    pass
""",
                [
                    {"kind": "call", "call": "total_area([Square(2), Rect(2, 3)])", "expected": 10},
                    {"kind": "call", "call": "total_area([])", "expected": 0},
                    {"kind": "call", "call": "total_area([Square(0)])", "expected": 0},
                ],
                """class Square:
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

def total_area(shapes):
    return sum(shape.area() for shape in shapes)
""",
                "`total_area` не проверяет классы: она просто вызывает `area()` у каждой фигуры.",
                "Сложи `shape.area()` для всех элементов через `sum`, не используя `isinstance`.",
            ),
        ],
    },
    {
        "id": "oop-advanced-special-methods",
        "theory": [
            _card(
                "Что такое специальные методы",
                "Специальные методы с двойными подчёркиваниями подключают объект к синтаксису "
                "Python. `__add__` вызывается при `+`, `__eq__` — при `==`, `__repr__` — при "
                "печати в отладке. Ты не вызываешь их напрямую: Python делает это сам. Так "
                "твой класс начинает вести себя как встроенное значение.",
                """class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f'Vector({self.x}, {self.y})'

print(Vector(1, 2) + Vector(3, 4))
# Вывод:
# Vector(4, 6)""",
                "Имя метода — это операция, которую Python выполняет за тебя.",
            ),
            _card(
                "Как пользоваться: сложение возвращает новый объект",
                "`__add__` получает второй объект и должен вернуть новый результат, а не менять "
                "исходные. Сложи поля по отдельности и собери новый `Vector`. `__eq__` "
                "сравнивает состояние и возвращает `True` или `False`. Вместе они позволяют "
                "писать `(a + b) == c`.",
                """class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

print(Vector(1, 2) == Vector(1, 2))
print(Vector(1, 2) == Vector(2, 1))
# Вывод:
# True
# False""",
                "Не меняй `self` в `__add__`: создавай новый экземпляр.",
            ),
            _card(
                "Типичная ошибка: сравнить только часть полей",
                "Если `__eq__` смотрит только на `x`, векторы с разными `y` окажутся равными. "
                "Код не падает, но условие `==` начинает врать. Заметь это на паре объектов, "
                "которые отличаются одним полем. Сравнивай все поля, которые задают состояние.",
                """class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x

print(Vector(1, 2) == Vector(1, 9))
# Вывод:
# True""",
                "Проверь `==` на объектах, у которых совпадает только одно поле.",
            ),
        ],
        "questions": [
            _choice(
                "oop-advanced-special-methods",
                "Что выведет код?\n\n"
                "class Vector:\n"
                "    def __init__(self, x, y):\n"
                "        self.x = x\n"
                "        self.y = y\n"
                "\n"
                "    def __add__(self, other):\n"
                "        return Vector(self.x + other.x, self.y + other.y)\n"
                "\n"
                "    def __repr__(self):\n"
                "        return f'Vector({self.x}, {self.y})'\n"
                "\n"
                "print(Vector(2, 3) + Vector(4, 5))",
                ["Vector(6, 8)", "Vector(8, 6)", "Vector(6, 9)", "Vector(4, 5)"],
                "Vector(6, 8)",
                "`__add__` сложил координаты по отдельности: 2 + 4 и 3 + 5.",
            ),
            _term(
                "oop-advanced-special-methods",
                "Какой специальный метод вызывается при сложении объектов через `+`?",
                ["__add__", "add", "__add__()", "метод __add__"],
                "Оператор `+` вызывает `__add__` у левого объекта.",
            ),
            _code(
                "oop-advanced-special-methods",
                "Создай `class Vector` с конструктором `__init__(self, x, y)`, методом "
                "`__add__` для сложения двух векторов и методом `__eq__` для сравнения координат.",
                """class Vector:
    def __init__(self, x, y):
        pass

    def __add__(self, other):
        pass

    def __eq__(self, other):
        pass
""",
                [
                    {
                        "kind": "call",
                        "call": "(Vector(1, 2) + Vector(3, 4)) == Vector(4, 6)",
                        "expected": True,
                    },
                    {
                        "kind": "call",
                        "call": "(Vector(0, 0) == Vector(0, 1)) is False",
                        "expected": True,
                    },
                    {"kind": "call", "call": "Vector(0, 0) == Vector(0, 0)", "expected": True},
                ],
                """class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
""",
                "`__add__` вернул новый вектор, а `__eq__` сравнил обе координаты.",
                "В `__add__` создай `Vector(self.x + other.x, self.y + other.y)`, а в "
                "`__eq__` сравни `x` и `y` через `and`.",
            ),
        ],
    },
]
