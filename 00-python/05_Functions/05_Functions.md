# Python Basics: Functions

## Function Definition

A **function** is a reusable, named block of code, defined with the `def` keyword.

```python
def greet():
    print("Hello!")

greet()   # calling the function
```

- `def` starts the definition, followed by the function name and parentheses
- The indented block is the function body
- A function must be called to actually run its code

```python
def add():
    result = 2 + 3
    print(result)

add()   # 5
```

---

## Parameters

**Parameters** are the named inputs a function is defined to accept, listed inside the parentheses.

```python
def greet(name):
    print(f"Hello, {name}!")
```

Here, `name` is a parameter — a placeholder for whatever value gets passed in when the function is called.

A function can have multiple parameters:

```python
def add(a, b):
    return a + b
```

---

## Arguments

**Arguments** are the actual values passed into a function when it's called.

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Mehedi")   # "Mehedi" is the argument
```

- Parameters are defined in the function signature
- Arguments are supplied at the call site
- The number of arguments must generally match the number of required parameters

```python
def add(a, b):
    return a + b

add(2, 3)   # 2 and 3 are arguments; result is 5
```

---

## Return Values

The `return` statement sends a value back to the code that called the function, and ends the function's execution.

```python
def add(a, b):
    return a + b

result = add(2, 3)
print(result)   # 5
```

- A function without an explicit `return` returns `None` by default
- `return` immediately exits the function — any code after it doesn't run
- A function can return any type, including tuples (effectively returning multiple values)

```python
def divide(a, b):
    return a // b, a % b

quotient, remainder = divide(7, 2)   # 3, 1
```

---

## Positional Arguments

Arguments matched to parameters based on their **order**.

```python
def introduce(name, age):
    print(f"{name} is {age} years old")

introduce("Mehedi", 25)
```

Here, `"Mehedi"` maps to `name` and `25` maps to `age`, purely by position. Swapping the order changes the meaning:

```python
introduce(25, "Mehedi")   # "25 is Mehedi years old" — likely wrong
```

---

## Keyword Arguments

Arguments passed by explicitly naming the parameter, regardless of order.

```python
def introduce(name, age):
    print(f"{name} is {age} years old")

introduce(age=25, name="Mehedi")
```

- Keyword arguments improve readability, especially with many parameters
- Positional and keyword arguments can be mixed, but positional ones must come first

```python
introduce("Mehedi", age=25)   # valid
introduce(name="Mehedi", 25)   # invalid — syntax error
```

---

## Default Arguments

Parameters that have a fallback value, used when the caller doesn't supply one.

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Mehedi")               # "Hello, Mehedi!"
greet("Mehedi", "Hi")          # "Hi, Mehedi!"
greet("Mehedi", greeting="Hey")  # "Hey, Mehedi!"
```

- Default arguments must come after non-default parameters in the definition
- Mutable defaults (like `[]` or `{}`) should generally be avoided due to a well-known Python gotcha:

```python
# risky pattern
def add_item(item, items=[]):
    items.append(item)
    return items
```

The same default list is reused across calls, which can cause unexpected shared state. A safer pattern:

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## *args and **kwargs

Special syntax for accepting a variable number of arguments.

### `*args` — variable positional arguments

Collects extra positional arguments into a tuple.

```python
def total(*args):
    return sum(args)

total(1, 2, 3)      # 6
total(5, 10)         # 15
```

### `**kwargs` — variable keyword arguments

Collects extra keyword arguments into a dict.

```python
def show_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

show_info(name="Mehedi", age=25)
```

Both can be combined, and used alongside regular parameters:

```python
def demo(a, b, *args, **kwargs):
    print(a, b, args, kwargs)

demo(1, 2, 3, 4, x=5, y=6)
# 1 2 (3, 4) {'x': 5, 'y': 6}
```

---

## Scope & LEGB Rule

**Scope** determines where a variable name is visible/accessible. Python resolves names using the **LEGB rule**, checked in this order:

| Level     | Meaning                                     |
|-----------|-----------------------------------------------|
| **L**ocal    | Names defined inside the current function     |
| **E**nclosing | Names in any enclosing (outer) function      |
| **G**lobal   | Names defined at the top level of the module  |
| **B**uilt-in | Python's built-in names (`len`, `print`, ...)|

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)   # 'local'

    inner()
    print(x)   # 'enclosing'

outer()
print(x)   # 'global'
```

Python looks up a name by searching Local → Enclosing → Global → Built-in, and stops at the first match.

---

## global and nonlocal

Keywords used to modify a variable from an outer scope, instead of creating a new local one.

### `global`

Allows a function to modify a variable defined at the module (global) level.

```python
count = 0

def increment():
    global count
    count += 1

increment()
print(count)   # 1
```

Without `global`, `count += 1` inside the function would raise an error, since Python would treat `count` as a new local variable.

### `nonlocal`

Allows a nested function to modify a variable from its enclosing (non-global) scope.

```python
def outer():
    count = 0

    def inner():
        nonlocal count
        count += 1

    inner()
    print(count)   # 1

outer()
```

`nonlocal` looks one level up (the enclosing function), while `global` looks at the module's top level.

---

## Docstrings & Type Hints

### Docstrings

A string literal placed as the first statement in a function, used to document what it does.

```python
def add(a, b):
    """Return the sum of a and b."""
    return a + b

print(add.__doc__)   # 'Return the sum of a and b.'
```

Triple quotes are conventional, even for single-line docstrings.

### Type Hints

Optional annotations indicating the expected types of parameters and the return value. They don't enforce types at runtime — they're for readability and tooling (linters, IDEs).

```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> None:
    print(f"Hello, {name}")
```

Type hints can also be applied to variables:

```python
age: int = 25
```

---

## Pure Functions

A **pure function** always returns the same output for the same input, and produces no side effects (it doesn't modify anything outside its own scope).

```python
# pure
def add(a, b):
    return a + b
```

```python
# impure — depends on external state
total = 0

def add_to_total(x):
    global total
    total += x
```

```python
# impure — has a side effect (printing, modifying an external list)
def add_and_log(a, b, log):
    result = a + b
    log.append(result)   # modifies something outside the function
    return result
```

Pure functions are easier to test, reason about, and reuse, since they don't depend on or affect anything beyond their own inputs and outputs.

---

## Key Points

- Functions are defined with `def`, and must be called to execute
- Parameters are placeholders in the definition; arguments are the actual values passed at the call
- `return` sends a value back and ends the function; without it, a function returns `None`
- Arguments can be positional (order-based) or keyword (name-based); defaults provide fallback values
- `*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict
- The LEGB rule (Local, Enclosing, Global, Built-in) governs how Python resolves variable names
- `global` modifies a module-level variable from inside a function; `nonlocal` modifies a variable from an enclosing function
- Docstrings document what a function does; type hints indicate expected types without enforcing them
- Pure functions have no side effects and always return the same output for the same input