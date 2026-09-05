# Functional Programming in Python

Python isn't a purely functional language — it's multi-paradigm — but it supports functional programming (FP) style extensively, and many idiomatic Python patterns borrow heavily from it. This document covers the FP mindset itself: the principles, not just the syntax (functions as values, `map`/`filter`/`lambda`, are covered in the Advanced Functions doc — this builds on top of that).

---

## 1. What Functional Programming Actually Means

Functional programming is a paradigm built around a few core ideas:

- **Functions as the primary building block** — programs are composed by combining functions, not by mutating shared state step by step
- **Avoiding mutable state** — data isn't changed in place; new data is produced instead
- **Avoiding side effects** — functions ideally only compute and return values, without affecting anything outside themselves
- **Declarative over imperative** — you describe *what* result you want, not the step-by-step *how*

```python
# imperative — describes HOW, step by step, with mutation
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x * x)

# functional/declarative — describes WHAT you want
result = [x * x for x in range(10) if x % 2 == 0]
```

Both produce the same output, but the second reads closer to a specification of the result than a sequence of instructions for building it.

---

## 2. Pure Functions

A **pure function** is the foundational unit of FP. It has two properties:

1. Given the same inputs, it **always** returns the same output
2. It has **no side effects** — it doesn't modify anything outside its own scope (no mutating arguments, no touching global variables, no printing, no writing to a file, no network calls)

```python
# pure
def add(a, b):
    return a + b
```

```python
# impure — depends on external mutable state
total = 0

def add_to_total(x):
    global total
    total += x
```

```python
# impure — mutates its input argument, a side effect on the caller's data
def add_item(item, items):
    items.append(item)   # the caller's list is modified
    return items
```

```python
# pure equivalent — returns a new list instead of mutating the input
def add_item(item, items):
    return items + [item]
```

### Why purity matters in practice

- **Predictability** — a pure function can be understood in complete isolation, without tracing through the rest of the program
- **Testability** — no setup/teardown of external state needed; just call it with inputs and assert on outputs
- **Safety under concurrency** — since nothing is shared or mutated, pure functions can run in parallel without race conditions
- **Referential transparency** — a call to a pure function can be mentally (or literally) replaced by its return value, without changing the program's behavior

```python
# referential transparency in action
def square(x):
    return x * x

y = square(4) + square(4)
# identical to:
y = 16 + 16
```

This property is what makes reasoning about functional code easier at scale — you don't need to track *when* something runs, only *what it returns*.

---

## 3. Immutability

FP favors data that, once created, cannot be changed — instead of modifying existing data, you produce new data.

Python's built-in immutable types: `int`, `float`, `str`, `tuple`, `frozenset`, `bool`, `None`. Its mutable types: `list`, `dict`, `set`.

```python
name = "mehedi"
name.upper()      # returns a NEW string; doesn't change `name`
print(name)         # still "mehedi"

numbers = (1, 2, 3)   # tuple — immutable
numbers[0] = 99        # raises TypeError
```

### Working immutably with normally-mutable data

```python
# mutating approach
def add_item(items, item):
    items.append(item)   # changes the original list
    return items

# immutable approach
def add_item(items, item):
    return items + [item]   # returns a new list, original untouched

original = [1, 2, 3]
updated = add_item(original, 4)
print(original)   # [1, 2, 3] — unchanged
print(updated)      # [1, 2, 3, 4]
```

`frozenset` is the immutable counterpart to `set`:

```python
frozen = frozenset([1, 2, 3])
frozen.add(4)   # raises AttributeError — frozensets have no mutating methods
```

Immutability isn't free — copying data instead of mutating it can cost more memory and CPU for large structures. In practice, Python code often mixes styles: mutable data structures used locally within a function, but functions themselves designed to be pure from the outside — not mutating anything the caller passed in or depends on.

---

## 4. Function Composition

Combining simple functions into more complex ones, where the output of one becomes the input of the next.

```python
def double(x):
    return x * 2

def increment(x):
    return x + 1

def compose(f, g):
    return lambda x: f(g(x))

double_then_increment = compose(increment, double)
print(double_then_increment(5))   # double(5)=10, then increment(10)=11
```

A more general composition helper for chaining any number of functions:

```python
from functools import reduce

def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions)

pipeline = compose(str, increment, double)
print(pipeline(5))   # double(5)=10 -> increment(10)=11 -> str(11) = "11"
```

Composition is how complex behavior is built from small, well-tested pieces in FP — instead of one large function doing everything, several small pure functions are chained together.

---

## 5. Partial Application and Currying

### Partial application — `functools.partial`

Fixes some arguments of a function ahead of time, producing a new function that needs fewer arguments.

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))   # 25
print(cube(5))       # 125
```

This is useful for specializing general-purpose functions into more specific ones without rewriting them:

```python
def log(level, message):
    print(f"[{level}] {message}")

warn = partial(log, "WARNING")
error = partial(log, "ERROR")

warn("Disk space low")   # [WARNING] Disk space low
error("Connection lost")  # [ERROR] Connection lost
```

### Currying

Transforming a function that takes multiple arguments into a chain of functions that each take a single argument. Python doesn't support currying natively the way languages like Haskell do, but it's straightforward to implement manually with closures or lambdas.

```python
def add(a):
    def inner(b):
        return a + b
    return inner

add(2)(3)   # 5

add_5 = add(5)
add_5(10)    # 15
```

```python
# equivalent with lambda
add = lambda a: lambda b: a + b
add(2)(3)   # 5
```

Currying and partial application solve a similar problem (specializing functions with fewer arguments) but differ in mechanism: currying transforms a function's shape into a chain of single-argument functions; partial application just pre-fills specific arguments of the original function without changing its shape.

---

## 6. Recursion as a Functional Tool

Since FP avoids mutable loop counters and in-place state changes, recursion is the natural replacement for iteration in a pure functional style (Python still uses `for`/`while` heavily in practice, but recursion is worth understanding as the FP-native alternative).

```python
# iterative, imperative style
def sum_list(numbers):
    total = 0
    for n in numbers:
        total += n
    return total

# recursive, functional style — no mutable accumulator variable
def sum_list(numbers):
    if not numbers:
        return 0
    return numbers[0] + sum_list(numbers[1:])
```

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

Python doesn't optimize tail recursion (unlike some functional languages), and has a limited recursion depth (commonly 1000), so deeply recursive pure-functional style isn't always practical here — it's more common in Python to blend the *mindset* (pure functions, immutability, composition) with ordinary loops for performance-sensitive code.

---

## 7. The `operator` Module

Provides function equivalents of Python's built-in operators — useful because FP tools like `map()`, `filter()`, and `reduce()` need actual functions, not operator symbols.

```python
from operator import add, mul, itemgetter, attrgetter
from functools import reduce

reduce(add, [1, 2, 3, 4])   # 10 — same as writing lambda a, b: a + b
reduce(mul, [1, 2, 3, 4])    # 24

people = [{"name": "Mehedi", "age": 25}, {"name": "Rafi", "age": 30}]
sorted(people, key=itemgetter("age"))   # cleaner than lambda p: p["age"]

sorted(people, key=lambda p: p["name"])  # equivalent to using itemgetter("name")
```

Using `operator` functions instead of equivalent lambdas is often preferred: they're implemented in C (slightly faster), and communicate intent clearly at a glance.

---

## 8. `functools` — The Core FP Toolkit

### `reduce()` — folding a sequence into one value (covered in Advanced Functions, included here for completeness)

```python
from functools import reduce
reduce(lambda acc, x: acc + x, [1, 2, 3, 4])   # 10
```

### `partial()` — covered above

### `lru_cache` / `cache` — memoization

Automatically caches a pure function's results, so repeated calls with the same arguments skip recomputation entirely. Only safe to use on pure functions, since the cache assumes the same input always produces the same output.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(50)   # computes instantly instead of recalculating overlapping subcalls
```

```python
from functools import cache   # Python 3.9+, equivalent to lru_cache(maxsize=None)

@cache
def expensive_computation(x):
    ...
```

This is one of the most immediately useful FP-adjacent tools in everyday Python — it turns purity into a free performance win.

### `wraps` — preserving metadata through decorators

```python
from functools import wraps

def log_call(func):
    @wraps(func)   # preserves func.__name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### `singledispatch` — function overloading by argument type

```python
from functools import singledispatch

@singledispatch
def describe(value):
    return f"Unknown type: {value}"

@describe.register
def _(value: int):
    return f"An integer: {value}"

@describe.register
def _(value: str):
    return f"A string: {value}"

describe(5)        # 'An integer: 5'
describe("hi")       # 'A string: hi'
```

Allows a function's behavior to branch cleanly by argument type, instead of a chain of `isinstance()` checks inside a single function body.

---

## 9. Comprehensions as Declarative FP

List, dict, set, and generator comprehensions (covered in earlier docs) are Python's most idiomatic expression of the FP mindset: they describe the transformation of data declaratively, rather than the mechanics of looping and mutating an accumulator.

```python
# FP style: map + filter combined declaratively
result = [x ** 2 for x in range(20) if x % 2 == 0]

# equivalent using map/filter directly
result = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, range(20))))
```

In Python, comprehensions are generally preferred over chained `map()`/`filter()` calls for exactly this kind of transformation — they're considered more readable and more "Pythonic," even though both are functional in spirit. `map()`/`filter()`/`reduce()` tend to be reached for when a named function is already available, or when working generically across other functional tools (like composing pipelines, as in Section 4).

---

## 10. Avoiding Side Effects — A Practical Discipline

Real Python programs need side effects somewhere (printing, saving to a database, sending a request) — the FP discipline isn't to eliminate side effects entirely, but to **isolate** them: keep the core logic pure, and push side effects to the edges of the program.

```python
# mixed concerns — hard to test, hard to reuse
def process_order(order):
    order["total"] = order["price"] * order["quantity"]
    print(f"Processing order: {order}")          # side effect
    save_to_database(order)                          # side effect
    return order
```

```python
# separated — pure core, side effects pushed to the caller
def calculate_total(order):
    return {**order, "total": order["price"] * order["quantity"]}

def process_order(order):
    updated_order = calculate_total(order)   # pure, testable in isolation
    print(f"Processing order: {updated_order}")   # side effects live here, at the edge
    save_to_database(updated_order)
    return updated_order
```

`calculate_total()` can now be tested with a plain assertion, no mocking, no database, no captured output — a direct practical payoff of following FP discipline even in an otherwise ordinary Python codebase.

---

## 11. Functional vs Imperative vs OOP — When to Reach for Which

These paradigms aren't mutually exclusive in Python — real code blends them constantly. A rough guide:

| Style        | Good fit for                                                  |
|--------------|------------------------------------------------------------------|
| Functional    | Data transformations, pipelines, parallelizable computation, anything benefiting from predictability and easy testing |
| Imperative     | Simple, linear step-by-step logic; performance-critical loops    |
| OOP             | Modeling stateful entities with identity and behavior over time (a `User`, a `Connection`, a game character) |

```python
# functional — transforming a stream of data
cleaned = [x.strip().lower() for x in raw_lines if x.strip()]

# OOP — modeling something with ongoing state and identity
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
```

Idiomatic Python (sometimes called "Pythonic" style) tends to draw from all three pragmatically — pure functions and comprehensions for data transformation, classes for stateful entities, and plain imperative code where it's simply the clearest option. Dogmatically forcing pure FP style throughout an entire codebase is uncommon in real Python projects; the value is in knowing the FP tools well enough to use them where they genuinely make the code better.

---

## Key Points

- FP centers on pure functions, immutability, and composing behavior from small building blocks rather than mutating shared state
- A pure function always returns the same output for the same input and has no side effects — this is what makes it predictable, testable, and safe under concurrency
- Immutability means producing new data instead of changing data in place; Python mixes mutable and immutable types, and FP style leans on the immutable ones
- Function composition chains simple functions into more complex behavior; `functools.reduce` can generalize composition across any number of functions
- `functools.partial` pre-fills arguments to specialize a function; manual currying transforms a multi-argument function into a chain of single-argument functions
- Recursion is the FP-native replacement for iteration, though Python's recursion limits mean loops are often still used in practice
- The `operator` module provides function versions of operators, useful with `map`/`filter`/`reduce`/`sorted`
- `functools` (`reduce`, `partial`, `lru_cache`/`cache`, `wraps`, `singledispatch`) is the core toolkit for functional-style Python
- Comprehensions are Python's most idiomatic declarative/functional construct, generally preferred over chained `map()`/`filter()` for readability
- Real-world FP discipline isn't eliminating side effects — it's isolating them, keeping core logic pure and pushing I/O/mutation to the edges
- Python is multi-paradigm — functional, imperative, and OOP styles are combined pragmatically rather than choosing just one