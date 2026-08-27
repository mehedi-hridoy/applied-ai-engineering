# Python Advanced Functions

## First-Class Functions

In Python, functions are **first-class objects** — they can be treated like any other value: assigned to variables, passed as arguments, stored in data structures, and returned from other functions.

```python
def greet():
    return "Hello!"

say_hi = greet     # assign function to a variable (no parentheses — not calling it)
print(say_hi())    # 'Hello!'
```

```python
functions = [greet, str.upper, len]
```

```python
def get_function():
    return greet

fn = get_function()
print(fn())   # 'Hello!'
```

This capability is what makes higher-order functions, decorators, and callbacks possible in Python.

---

## Higher-Order Functions

A function that either **takes another function as an argument**, **returns a function**, or both.

```python
def apply(func, value):
    return func(value)

def square(x):
    return x * x

apply(square, 5)   # 25
```

```python
def multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply   # returning a function

double = multiplier(2)
double(10)   # 20
```

`map()`, `filter()`, and `sorted(key=...)` are common built-in higher-order functions.

---

## map()

Applies a function to every item in an iterable, returning a map object (lazy iterator).

```python
numbers = [1, 2, 3, 4]

squared = map(lambda x: x ** 2, numbers)
print(list(squared))   # [1, 4, 9, 16]
```

```python
def to_upper(s):
    return s.upper()

names = ["mehedi", "rafi"]
list(map(to_upper, names))   # ['MEHEDI', 'RAFI']
```

`map()` can also take multiple iterables, applying the function pairwise:

```python
a = [1, 2, 3]
b = [10, 20, 30]
list(map(lambda x, y: x + y, a, b))   # [11, 22, 33]
```

---

## filter()

Keeps only the items from an iterable for which a function returns `True`.

```python
numbers = [1, 2, 3, 4, 5, 6]

evens = filter(lambda x: x % 2 == 0, numbers)
print(list(evens))   # [2, 4, 6]
```

```python
words = ["", "hello", "", "world"]
non_empty = filter(None, words)   # filters out falsy values
list(non_empty)   # ['hello', 'world']
```

Like `map()`, `filter()` returns a lazy iterator — wrap it in `list()` to see the results.

---

## reduce()

Repeatedly applies a function to pairs of items, reducing an iterable to a single accumulated value. Lives in the `functools` module.

```python
from functools import reduce

numbers = [1, 2, 3, 4]
total = reduce(lambda acc, x: acc + x, numbers)
print(total)   # 10
```

It works by carrying an accumulator through the sequence:

```text
step 1: acc=1, x=2 -> 3
step 2: acc=3, x=3 -> 6
step 3: acc=6, x=4 -> 10
```

An optional initial value can be provided:

```python
reduce(lambda acc, x: acc + x, numbers, 100)   # 110
```

For simple sums or products, built-ins like `sum()` are usually preferred over `reduce()`.

---

## Lambda Functions

Small, anonymous, single-expression functions defined with the `lambda` keyword.

```python
square = lambda x: x ** 2
square(5)   # 25

add = lambda a, b: a + b
add(2, 3)   # 5
```

- No `def`, no name required, no `return` keyword — the expression's value is returned automatically
- Limited to a single expression — no statements, loops, or multiple lines
- Commonly used inline, especially as arguments to `map()`, `filter()`, `sorted()`

```python
people = [("Mehedi", 25), ("Rafi", 30)]
people.sort(key=lambda person: person[1])   # sort by age
```

For anything beyond a simple expression, a regular `def` function is clearer.

---

## Closures

A **closure** is a nested function that "remembers" variables from its enclosing scope, even after the outer function has finished running.

```python
def multiplier(factor):
    def multiply(x):
        return x * factor   # 'factor' is remembered
    return multiply

double = multiplier(2)
triple = multiplier(3)

double(5)   # 10
triple(5)   # 15
```

Each call to `multiplier()` creates a new closure with its own captured value of `factor` — `double` and `triple` don't interfere with each other.

Closures are the mechanism behind function factories and are closely related to how decorators work.

---

## Decorators

A **decorator** is a function that wraps another function to extend or modify its behavior, without changing its actual code. Applied using the `@decorator_name` syntax.

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@log_call
def greet(name):
    print(f"Hello, {name}!")

greet("Mehedi")
```

This is equivalent to:

```python
def greet(name):
    print(f"Hello, {name}!")

greet = log_call(greet)
```

Decorators are commonly used for logging, timing, access control, and caching. Multiple decorators can be stacked:

```python
@decorator_one
@decorator_two
def my_function():
    pass
```

---

## Function Introspection

Inspecting a function's properties at runtime — its name, docstring, arguments, and more.

```python
def add(a, b):
    """Add two numbers."""
    return a + b

add.__name__       # 'add'
add.__doc__        # 'Add two numbers.'
```

The `inspect` module provides more detail:

```python
import inspect

inspect.signature(add)      # (a, b)
inspect.getsource(add)       # returns the function's source code as a string
```

Introspection is useful for debugging, building documentation tools, and writing decorators that preserve the original function's metadata (commonly done with `functools.wraps`).

```python
from functools import wraps

def log_call(func):
    @wraps(func)   # preserves func.__name__ and __doc__
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

---

## Recursion

A function that calls **itself**, used to break a problem down into smaller instances of the same problem.

```python
def factorial(n):
    if n == 0:
        return 1           # base case
    return n * factorial(n - 1)   # recursive case

factorial(5)   # 120
```

Every recursive function needs:

- A **base case** — a condition where the function stops calling itself
- A **recursive case** — where the function calls itself with a smaller/simpler input

```python
def countdown(n):
    if n <= 0:
        print("Done!")
        return
    print(n)
    countdown(n - 1)
```

Without a base case (or if it's never reached), recursion leads to infinite calls and a `RecursionError`. Python has a default recursion depth limit (commonly 1000), so deeply recursive problems may need an iterative approach instead.

---

## Key Points

- Functions are first-class objects in Python — they can be assigned, passed, and returned like any value
- Higher-order functions take or return other functions; `map()`, `filter()`, and `sorted(key=...)` are common examples
- `map()` transforms items, `filter()` selects items, `reduce()` (from `functools`) folds items into one value
- `lambda` creates small, single-expression anonymous functions, often used inline
- A closure is a nested function that captures and remembers variables from its enclosing scope
- Decorators (`@decorator`) wrap a function to add behavior without modifying its source
- Introspection (`__name__`, `__doc__`, `inspect`) lets you examine a function's metadata at runtime
- Recursion solves a problem by having a function call itself, always requiring a base case to terminate