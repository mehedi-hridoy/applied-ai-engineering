# Python OOP — Advanced Concepts

This is Part 2, building on `python-oop-core.md`. These are the concepts that separate someone who can write classes from someone who can architect systems with them — the internals of how Python's object model actually works, and the patterns used in real production codebases.

---

## 1. `__new__` vs `__init__`

Object creation in Python is actually a two-step process, and `__init__` is only the second step.

```python
class Car:
    def __new__(cls, *args, **kwargs):
        print("Creating the object")
        instance = super().__new__(cls)   # actually allocates the object
        return instance

    def __init__(self, brand):
        print("Initializing the object")
        self.brand = brand

car = Car("Toyota")
# Creating the object
# Initializing the object
```

- `__new__` is responsible for **creating and returning** the actual object (a `classmethod`, though you don't need `@classmethod` — Python treats it specially)
- `__init__` receives that already-created object as `self` and just **configures** it
- `__init__` returns `None` implicitly — it cannot return a value

`__new__` is rarely overridden in everyday code, but it matters for:

- Implementing immutable types (subclassing `tuple` or `str`)
- Controlling instance creation itself (e.g. the Singleton pattern, below)
- Metaclasses (where `__new__` decides what class gets built)

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

a = Singleton()
b = Singleton()
print(a is b)   # True — same object, __new__ intercepted creation
```

---

## 2. `__slots__`

By default, every instance carries a `__dict__` to store its attributes dynamically — flexible, but with memory overhead. `__slots__` restricts an object to a fixed set of attributes, storing them more compactly and disallowing new ones.

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 5   # raises AttributeError — 'z' isn't in __slots__
```

Why it matters in real systems:

- Significantly reduces memory usage when creating millions of small objects (common in data pipelines, simulations, game entities)
- Prevents accidental attribute typos from silently creating new attributes (`self.nmae = x` would normally just work and go unnoticed)
- Trade-off: no `__dict__` means no dynamic attributes, and some other features (like weak references) need extra setup

```python
class WithDict:
    def __init__(self, x):
        self.x = x

class WithSlots:
    __slots__ = ("x",)
    def __init__(self, x):
        self.x = x

# WithSlots instances use meaningfully less memory than WithDict at scale
```

---

## 3. Descriptors

A **descriptor** is an object that defines custom behavior for attribute access, by implementing `__get__`, `__set__`, or `__delete__`. This is the actual mechanism behind `@property`, methods, and `@staticmethod`/`@classmethod` — understanding descriptors means understanding what Python's attribute lookup is really doing.

```python
class PositiveNumber:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError(f"{self.name} must be positive")
        setattr(instance, self.name, value)

class Product:
    price = PositiveNumber()   # descriptor reused across attributes

    def __init__(self, price):
        self.price = price   # triggers PositiveNumber.__set__

p = Product(100)
print(p.price)     # 100 — triggers __get__
p.price = -10        # raises ValueError
```

Why this matters: descriptors let you write validation/computation logic **once** and reuse it across many attributes or classes, instead of repeating `@property` boilerplate everywhere. Libraries like Django's ORM (`models.CharField()`, etc.) and dataclasses are built on this exact mechanism.

There are two kinds:

- **Data descriptors** — implement `__set__` (or `__delete__`); they take priority over instance `__dict__`
- **Non-data descriptors** — implement only `__get__`; instance `__dict__` takes priority over them (this is how instance attributes can "shadow" methods)

---

## 4. Metaclasses

If a class is a blueprint for objects, a **metaclass** is a blueprint for classes — it controls how classes themselves are created. By default, every class is created by `type`.

```python
print(type(3))            # <class 'int'>
print(type(int))           # <class 'type'>  — classes are instances of type
```

A custom metaclass intercepts and customizes class creation:

```python
class UpperAttrMeta(type):
    def __new__(mcs, name, bases, namespace):
        # uppercase all non-dunder attribute names
        new_namespace = {
            (key.upper() if not key.startswith("__") else key): value
            for key, value in namespace.items()
        }
        return super().__new__(mcs, name, bases, new_namespace)

class Config(metaclass=UpperAttrMeta):
    debug = True
    version = "1.0"

print(Config.DEBUG)     # True — 'debug' was uppercased at class-creation time
```

Real-world uses of metaclasses:

- **ORMs** (Django, SQLAlchemy) use metaclasses to turn class attribute declarations into database schema/mapping logic
- **Enforcing interfaces** — automatically validating that subclasses implement required methods
- **Registering subclasses** automatically (plugin systems)

```python
class PluginMeta(type):
    registry = []

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:   # skip the base class itself
            mcs.registry.append(cls)
        return cls

class Plugin(metaclass=PluginMeta):
    pass

class PluginA(Plugin):
    pass

class PluginB(Plugin):
    pass

print(PluginMeta.registry)   # [PluginA, PluginB] — auto-registered
```

**Guidance:** metaclasses are powerful but rarely necessary — they're a tool for framework/library authors more than everyday application code. The well-known engineering guideline: "metaclasses are deeper magic than 99% of users should worry about; if you wonder whether you need them, you don't" (paraphrased from Tim Peters). Still, understanding them is essential for reading and working with frameworks that use them.

---

## 5. Abstract Base Classes with `collections.abc`

Beyond writing your own `ABC` subclasses, Python's `collections.abc` module defines the abstract base classes behind built-in behavior — implementing the right dunder methods lets your custom class integrate seamlessly with Python's built-in protocols.

```python
from collections.abc import Iterable, Sized, Container

class MyCollection:
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

c = MyCollection([1, 2, 3])

for item in c:          # works because of __iter__
    print(item)

len(c)                    # works because of __len__
2 in c                      # works because of __contains__

isinstance(c, Iterable)      # True — even without explicit inheritance!
```

`isinstance(c, Iterable)` returns `True` because `collections.abc` classes use `__subclasshook__` to check for the right methods structurally — this is Python's built-in version of duck typing formalized into the type system.

This is the foundation for building custom container types (custom lists, queues, trees) that behave exactly like built-ins when used with `for`, `len()`, `in`, slicing, etc.

---

## 6. Operator Overloading (Full Picture)

Beyond `__add__` and `__eq__` (covered in the core doc), a complete numeric/comparison type typically implements a broader set of dunder methods to behave consistently.

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __sub__(self, other):
        return Money(self.amount - other.amount)

    def __mul__(self, factor):
        return Money(self.amount * factor)

    def __lt__(self, other):
        return self.amount < other.amount

    def __le__(self, other):
        return self.amount <= other.amount

    def __eq__(self, other):
        return self.amount == other.amount

    def __repr__(self):
        return f"Money({self.amount})"

a = Money(100)
b = Money(50)
print(a + b)         # Money(150)
print(a > b)          # True — Python derives __gt__ from __lt__ via functools.total_ordering, or you implement it directly
```

To avoid manually writing every comparison method, `functools.total_ordering` fills in the rest from just `__eq__` and one of `__lt__`/`__le__`/`__gt__`/`__ge__`:

```python
from functools import total_ordering

@total_ordering
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __eq__(self, other):
        return self.amount == other.amount

    def __lt__(self, other):
        return self.amount < other.amount

# __le__, __gt__, __ge__ are auto-generated
```

Also worth knowing: `__radd__`, `__iadd__` handle reflected (`other + self`) and in-place (`self += other`) operations respectively, for full symmetry with built-in numeric types.

---

## 7. Class Decorators and `@dataclass`

### Class decorators

Just like function decorators, a decorator can wrap an entire class to modify or extend it.

```python
def add_greeting(cls):
    cls.greet = lambda self: f"Hello from {self.__class__.__name__}"
    return cls

@add_greeting
class Person:
    pass

print(Person().greet())   # Hello from Person
```

### `@dataclass`

A built-in decorator (from `dataclasses`) that auto-generates common boilerplate — `__init__`, `__repr__`, `__eq__` — for classes that are primarily containers of data.

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(1, 2)

print(p1)          # Point(x=1, y=2)  — __repr__ generated for you
print(p1 == p2)      # True — __eq__ generated for you
```

Useful options:

```python
@dataclass(frozen=True)   # makes instances immutable, like a namedtuple
class ImmutablePoint:
    x: int
    y: int

@dataclass
class Team:
    name: str
    members: list = field(default_factory=list)   # safe way to default a mutable type
```

`@dataclass` doesn't replace regular classes for behavior-heavy objects, but for data containers (DTOs, config objects, records) it eliminates a large amount of repetitive code.

---

## 8. Mixins

A **mixin** is a class designed to be combined with others via multiple inheritance, contributing a specific piece of reusable behavior — not meant to stand on its own or represent an "is-a" relationship.

```python
class JSONSerializableMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class LoggerMixin:
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")

class User(JSONSerializableMixin, LoggerMixin):
    def __init__(self, name):
        self.name = name

user = User("Mehedi")
user.log("User created")     # [User] User created
print(user.to_json())          # {"name": "Mehedi"}
```

Mixins let you compose small, independent capabilities into a class without deep, rigid inheritance chains. Conventionally named with a `Mixin` suffix, and they typically don't define `__init__` or hold their own state — they just add methods.

This is a common way frameworks (like Django's class-based views) let you assemble a class's capabilities piece by piece: `class MyView(LoginRequiredMixin, ListView):`.

---

## 9. Context Managers as Classes

The `with` statement relies on the **context manager protocol** — `__enter__` and `__exit__`. Implementing these on a class lets your objects manage setup/teardown automatically (files, connections, locks).

```python
class DatabaseConnection:
    def __enter__(self):
        print("Opening connection")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Closing connection")
        return False   # False means: don't suppress exceptions

    def query(self, sql):
        print(f"Running: {sql}")

with DatabaseConnection() as db:
    db.query("SELECT * FROM users")

# Opening connection
# Running: SELECT * FROM users
# Closing connection
```

`__exit__` is guaranteed to run even if an exception occurs inside the `with` block — which is exactly why this pattern is preferred over manual try/finally for resource management.

```python
class DatabaseConnection:
    def __exit__(self, exc_type, exc_value, traceback):
        print("Closing connection, even after an error")
        return False   # let the exception propagate

with DatabaseConnection() as db:
    raise ValueError("Something broke")
# Closing connection, even after an error
# (then the ValueError still propagates upward)
```

---

## 10. Design Patterns (OOP Fundamentals in Practice)

Design patterns are reusable, named solutions to recurring design problems. A few that come up constantly in real systems:

### Singleton

Ensures a class has only one instance (shown earlier via `__new__`). Common for shared resources like configuration or logging.

### Factory

Delegates object creation to a dedicated method/class, decoupling the caller from the specific class being instantiated.

```python
class Dog:
    def speak(self):
        return "Bark"

class Cat:
    def speak(self):
        return "Meow"

class AnimalFactory:
    @staticmethod
    def create(animal_type):
        animals = {"dog": Dog, "cat": Cat}
        return animals[animal_type]()

animal = AnimalFactory.create("dog")
print(animal.speak())   # Bark
```

The caller never directly references `Dog` or `Cat` — new animal types can be added without changing the calling code.

### Observer

Objects (observers) subscribe to be notified when another object's (subject's) state changes. Foundation of event systems, GUIs, pub/sub architectures.

```python
class Subject:
    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Logger:
    def update(self, event):
        print(f"Logged: {event}")

subject = Subject()
subject.subscribe(Logger())
subject.notify("user_signed_up")   # Logged: user_signed_up
```

### Strategy

Encapsulates interchangeable algorithms/behaviors behind a common interface, so behavior can be swapped at runtime.

```python
class PayByCard:
    def pay(self, amount):
        print(f"Paid {amount} by card")

class PayByCash:
    def pay(self, amount):
        print(f"Paid {amount} by cash")

class Checkout:
    def __init__(self, payment_strategy):
        self.payment_strategy = payment_strategy

    def complete(self, amount):
        self.payment_strategy.pay(amount)

checkout = Checkout(PayByCard())
checkout.complete(100)   # Paid 100 by card
```

These four patterns alone cover a large share of what shows up in real backend/application codebases — recognizing them (and knowing when *not* to force one in) is a core engineering skill.

---

## 11. SOLID Principles

A set of five design principles for writing maintainable, extensible object-oriented code. Widely referenced in industry code reviews and system design discussions.

| Principle | Meaning |
|-----------|---------|
| **S** — Single Responsibility | A class should have exactly one reason to change — one responsibility |
| **O** — Open/Closed | Classes should be open for extension, but closed for modification (extend via new code, not by editing existing tested code) |
| **L** — Liskov Substitution | A subclass should be usable anywhere its parent class is expected, without breaking behavior |
| **I** — Interface Segregation | Prefer several small, specific interfaces over one large general-purpose one |
| **D** — Dependency Inversion | Depend on abstractions (interfaces/abstract classes), not concrete implementations |

```python
# Violates Single Responsibility — this class does two unrelated things
class Report:
    def generate(self):
        ...
    def save_to_file(self, path):
        ...   # formatting AND persistence in one class

# Better — split responsibilities
class Report:
    def generate(self):
        ...

class ReportSaver:
    def save(self, report, path):
        ...
```

```python
# Dependency Inversion — depend on an abstraction, not a concrete class
class Notifier:
    def send(self, message):
        raise NotImplementedError

class EmailNotifier(Notifier):
    def send(self, message):
        print(f"Email: {message}")

class OrderService:
    def __init__(self, notifier: Notifier):   # depends on the abstraction
        self.notifier = notifier

    def complete_order(self):
        self.notifier.send("Order completed")

service = OrderService(EmailNotifier())   # swap in any Notifier subclass freely
```

SOLID isn't a checklist to apply everywhere rigidly — it's a way of recognizing *why* a design is becoming brittle, and having a vocabulary to reason about the fix.

---

## Key Points

- `__new__` creates the object, `__init__` configures it — most code only needs `__init__`, but `__new__` matters for singletons and immutable types
- `__slots__` trades dynamic attributes for reduced memory footprint and stricter attribute control, valuable at scale
- Descriptors (`__get__`/`__set__`) are the mechanism behind `@property`, methods, and ORMs — reusable, structured attribute logic
- Metaclasses control how classes themselves are constructed — powerful for frameworks, rarely needed in application code
- `collections.abc` defines the structural contracts (`Iterable`, `Sized`, `Container`, etc.) behind Python's built-in protocols
- A complete overloaded type typically implements a full comparison/arithmetic set, often simplified using `functools.total_ordering`
- `@dataclass` eliminates boilerplate for data-centric classes; class decorators can modify or extend a class the same way function decorators modify functions
- Mixins compose independent, reusable behavior into a class via multiple inheritance, without an "is-a" relationship
- Implementing `__enter__`/`__exit__` makes a class usable with `with`, guaranteeing cleanup even when exceptions occur
- Singleton, Factory, Observer, and Strategy are foundational design patterns that recur constantly in real systems
- SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) guide maintainable, extensible OOP design at a system level