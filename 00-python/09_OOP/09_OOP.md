# Python OOP — Core Concepts

Object-Oriented Programming (OOP) is a way of structuring code around **objects** — bundles of data (attributes) and behavior (methods) that model real-world or logical entities. This document covers the foundation every engineer needs before touching advanced patterns: classes, objects, the four pillars of OOP, and how Python actually implements them under the hood.

---

## 1. Classes and Objects

A **class** is a blueprint. An **object** (or instance) is a concrete thing built from that blueprint.

```python
class Car:
    pass

my_car = Car()      # an object / instance of Car
another_car = Car()  # a separate, independent object
```

- The class defines *what an object can have and do*
- Each object has its own independent copy of instance data, even though they share the same class

Think of `Car` as the concept of "a car" in general, and `my_car` as one specific car sitting in a driveway.

---

## 2. `__init__` and `self`

### `__init__` — the constructor

`__init__` is a special method automatically called when a new object is created. It's used to set up the object's initial state.

```python
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

my_car = Car("Toyota", "Corolla")
print(my_car.brand)   # Toyota
```

### `self` — the instance itself

`self` refers to the specific object the method is being called on. It's the mechanism that lets each object keep track of its own data.

```python
class Car:
    def __init__(self, brand):
        self.brand = brand   # store on THIS object

    def show(self):
        print(f"This car is a {self.brand}")

car1 = Car("Toyota")
car2 = Car("Honda")

car1.show()   # This car is a Toyota
car2.show()   # This car is a Honda
```

`self` is passed automatically — `car1.show()` is really `Car.show(car1)` under the hood. It must be the first parameter of any instance method, though Python handles the actual passing for you.

---

## 3. Instance Attributes vs Class Attributes

### Instance attributes

Belong to a specific object, usually set in `__init__` via `self`. Each object has its own copy.

```python
class Car:
    def __init__(self, brand):
        self.brand = brand   # instance attribute
```

### Class attributes

Defined directly in the class body, shared by **all** instances unless overridden.

```python
class Car:
    wheels = 4   # class attribute — shared by every Car

    def __init__(self, brand):
        self.brand = brand   # instance attribute — unique per Car

car1 = Car("Toyota")
car2 = Car("Honda")

print(car1.wheels, car2.wheels)   # 4 4

Car.wheels = 6            # change for all instances
print(car1.wheels)         # 6

car1.wheels = 3             # creates a new instance attribute on car1 only
print(car1.wheels, car2.wheels)   # 3 6
```

**Key gotcha:** assigning to `self.attr = value` always creates or updates an *instance* attribute, even if a class attribute of the same name exists — it doesn't modify the shared class attribute. This matters especially for mutable defaults:

```python
class Team:
    members = []   # DANGER: shared across every Team instance

    def add(self, name):
        self.members.append(name)

t1 = Team()
t2 = Team()
t1.add("Mehedi")
print(t2.members)   # ['Mehedi'] — unexpectedly shared!
```

The fix — put mutable defaults in `__init__`:

```python
class Team:
    def __init__(self):
        self.members = []   # instance attribute, independent per object
```

---

## 4. Instance, Class, and Static Methods

### Instance methods

The default kind. Take `self`, operate on a specific object's data.

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2
```

### Class methods

Take `cls` (the class itself) instead of `self`. Used when the logic concerns the class as a whole, not one instance — commonly for alternative constructors.

```python
class Car:
    def __init__(self, brand, year):
        self.brand = brand
        self.year = year

    @classmethod
    def from_string(cls, car_string):
        brand, year = car_string.split("-")
        return cls(brand, int(year))   # constructs a new instance

car = Car.from_string("Toyota-2022")
print(car.brand, car.year)   # Toyota 2022
```

### Static methods

Take neither `self` nor `cls`. Used for utility logic that's logically related to the class but doesn't need access to instance or class state.

```python
class MathHelper:
    @staticmethod
    def is_even(n):
        return n % 2 == 0

MathHelper.is_even(4)   # True — called without creating an instance
```

**Rule of thumb:** use an instance method when you need `self`, a class method when you need `cls` (often for alternate constructors), and a static method when you need neither — it's just grouped there for organization.

---

## 5. Encapsulation

**Encapsulation** means bundling data and the methods that operate on it together, and controlling access to that data from outside the object. Python doesn't enforce strict privacy the way some languages do — it relies on naming conventions.

| Convention     | Meaning                                   |
|----------------|---------------------------------------------|
| `name`         | Public — freely accessible                  |
| `_name`        | Protected (by convention) — internal use, "don't touch unless you know why" |
| `__name`       | Private (name-mangled) — strongly discouraged from outside access |

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance          # protected by convention
        self.__pin = "1234"                # name-mangled

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

account = BankAccount(100)
account.deposit(50)
print(account._balance)   # 150 — accessible, but "you shouldn't"
```

`__pin` gets name-mangled to `_BankAccount__pin` internally, making accidental external access harder (though not impossible):

```python
print(account._BankAccount__pin)   # '1234' — still reachable, just discouraged
```

### Properties — controlled access

The `@property` decorator lets you expose a method as if it were an attribute, enabling validation or computed values without changing how the object is used externally.

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value

account = BankAccount(100)
print(account.balance)      # 100 — looks like attribute access, calls the getter
account.balance = 200         # calls the setter, validated
account.balance = -50          # raises ValueError
```

This is the idiomatic Python way to do "getters and setters" — you can start with a plain attribute and introduce a property later without breaking calling code.

---

## 6. Inheritance

**Inheritance** lets a class (the child/subclass) reuse and extend the behavior of another class (the parent/superclass).

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} makes a sound")

class Dog(Animal):          # Dog inherits from Animal
    def speak(self):          # overrides the parent's method
        print(f"{self.name} barks")

class Cat(Animal):
    pass   # inherits speak() unchanged

dog = Dog("Rex")
cat = Cat("Whiskers")

dog.speak()   # Rex barks
cat.speak()   # Whiskers makes a sound
```

### `super()`

Calls a method from the parent class — commonly used in `__init__` to extend, not replace, the parent's setup logic.

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)   # runs Animal's __init__ first
        self.breed = breed

dog = Dog("Rex", "Labrador")
print(dog.name, dog.breed)   # Rex Labrador
```

### Multiple Inheritance and MRO

Python allows a class to inherit from more than one parent. When methods conflict, Python resolves the order using the **Method Resolution Order (MRO)**.

```python
class A:
    def greet(self):
        print("Hello from A")

class B:
    def greet(self):
        print("Hello from B")

class C(A, B):
    pass

C().greet()          # "Hello from A" — A comes first in the inheritance list
print(C.__mro__)     # shows the exact lookup order
```

The MRO is computed with the C3 linearization algorithm — in practice, Python searches left to right through the classes listed in the class definition, then up their parents, without visiting the same class twice.

---

## 7. Polymorphism

**Polymorphism** means objects of different classes can be used through the same interface, each responding to the same method call in its own way.

```python
class Dog:
    def speak(self):
        return "Bark"

class Cat:
    def speak(self):
        return "Meow"

animals = [Dog(), Cat()]

for animal in animals:
    print(animal.speak())   # Bark, then Meow
```

The calling code (`animal.speak()`) doesn't need to know or care which exact class it's dealing with — it just trusts that `.speak()` exists and does the right thing. This is what allows flexible, extensible systems: new animal types can be added later without changing the loop above.

Python supports this naturally through **duck typing**: "if it walks like a duck and quacks like a duck, it's a duck" — an object just needs to support the expected method, regardless of its actual class or a shared base class.

```python
class Duck:
    def speak(self):
        return "Quack"

class Robot:
    def speak(self):   # not related to Duck at all, but still works
        return "Beep"

for thing in [Duck(), Robot()]:
    print(thing.speak())   # Quack, then Beep
```

---

## 8. Abstraction

**Abstraction** means exposing only the essential behavior of an object, while hiding the implementation details behind a well-defined interface. In Python, this is commonly implemented with **abstract base classes**, using the `abc` module.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass   # no implementation — subclasses MUST provide one

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

rect = Rectangle(4, 5)
print(rect.area())   # 20

shape = Shape()   # raises TypeError — can't instantiate an abstract class
```

- A class inheriting from `ABC` with at least one `@abstractmethod` cannot be instantiated directly
- Any subclass must implement every abstract method, or it also becomes non-instantiable
- This enforces a contract: "any Shape must know how to compute its own area", without dictating how each shape does it

This is the foundation of designing systems around interfaces rather than concrete implementations — critical for building extensible, testable software.

---

## 9. Dunder (Magic) Methods

Methods surrounded by double underscores (`__init__`, `__str__`, etc.) let your objects integrate with Python's built-in syntax and functions — operators, printing, length, comparisons, and more.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Point({self.x}, {self.y})"   # used by print() and str()

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"   # used in debugging/REPL

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __len__(self):
        return 2   # arbitrary example

p1 = Point(1, 2)
p2 = Point(3, 4)

print(p1)          # Point(1, 2)          — calls __str__
p1 == Point(1, 2)   # True                 — calls __eq__
p3 = p1 + p2         # Point(4, 6)          — calls __add__
```

Common dunder methods worth knowing:

| Method       | Triggered by            |
|--------------|---------------------------|
| `__init__`   | Object creation             |
| `__str__`    | `print(obj)`, `str(obj)`     |
| `__repr__`   | Interactive shell, debugging |
| `__eq__`     | `obj1 == obj2`                |
| `__lt__`     | `obj1 < obj2`                  |
| `__len__`    | `len(obj)`                      |
| `__add__`    | `obj1 + obj2`                    |
| `__getitem__`| `obj[key]`                        |
| `__iter__`   | Used in `for x in obj`             |
| `__call__`   | `obj()` — makes an object callable |

`__str__` vs `__repr__`: `__str__` is meant to be readable for end users; `__repr__` is meant to be unambiguous, ideally something that could recreate the object if pasted back into Python. If `__str__` is missing, Python falls back to `__repr__`.

---

## 10. Composition vs Inheritance

Two ways to build relationships between classes.

### Inheritance — an "is-a" relationship

```python
class Vehicle:
    def move(self):
        print("Moving")

class Car(Vehicle):   # a Car IS A Vehicle
    pass
```

### Composition — a "has-a" relationship

Instead of inheriting behavior, an object holds a reference to another object and delegates to it.

```python
class Engine:
    def start(self):
        print("Engine starting")

class Car:
    def __init__(self):
        self.engine = Engine()   # a Car HAS AN Engine

    def start(self):
        self.engine.start()

car = Car()
car.start()   # Engine starting
```

**Why it matters:** Inheritance creates tight coupling — a subclass depends heavily on its parent's implementation, and deep inheritance hierarchies become fragile and hard to change. Composition is more flexible: components can be swapped, tested, and reused independently.

A well-known guiding principle in real-world system design: **"favor composition over inheritance"** — reach for inheritance mainly when there's a genuine, stable "is-a" relationship and shared behavior that truly belongs in a base class; reach for composition when you're really just reusing functionality.

---

## Key Points

- A class is a blueprint; an object is an independent instance built from it, with `self` referring to that specific instance
- `__init__` sets up initial state; instance attributes belong to one object, class attributes are shared unless overridden
- Instance methods use `self`, class methods use `cls` (often for alternate constructors), static methods use neither
- Encapsulation controls access via naming conventions (`_protected`, `__private`) and `@property` for validated, attribute-like access
- Inheritance lets a subclass reuse and override a parent's behavior; `super()` calls the parent's implementation; MRO resolves conflicts in multiple inheritance
- Polymorphism lets different classes be used through a shared interface — Python leans on duck typing rather than requiring a common base class
- Abstraction defines a contract via abstract base classes (`ABC`, `@abstractmethod`), preventing instantiation until the contract is fulfilled
- Dunder methods (`__str__`, `__eq__`, `__add__`, etc.) let custom objects integrate naturally with Python's built-in syntax and functions
- Composition ("has-a") is often more flexible than inheritance ("is-a") — favor composition unless a real, stable hierarchy exists