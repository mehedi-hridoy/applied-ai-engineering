# Python Exception Handling

Errors happen — bad input, missing files, network failures, bugs. **Exception handling** is how a program detects these problems and responds to them deliberately, instead of crashing unpredictably. This is one of the most important practical skills in writing production-grade Python.

---

## 1. What Is an Exception

An **exception** is an object Python creates and "raises" when something goes wrong during execution. If nothing handles it, the program stops and prints a **traceback**.

```python
print(10 / 0)
```

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print(10 / 0)
ZeroDivisionError: division by zero
```

The traceback tells you: the type of exception (`ZeroDivisionError`), the error message, and the exact line/call stack where it happened. Reading tracebacks carefully — from the bottom up — is a core debugging skill.

---

## 2. try / except

The basic mechanism for catching and handling an exception instead of letting it crash the program.

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
```

```python
try:
    age = int(input("Enter your age: "))
except ValueError:
    print("That's not a valid number")
```

- Code in `try` runs first
- If an exception occurs, Python immediately jumps to the matching `except` block — the rest of the `try` block is skipped
- If no exception occurs, `except` is skipped entirely

### Catching the exception object

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error occurred: {e}")   # Error occurred: division by zero
```

`e` is the actual exception instance — it carries the error message and any extra data the exception type provides.

---

## 3. Catching Multiple Exceptions

### Separate `except` blocks (different handling per error)

```python
try:
    value = int(input("Enter a number: "))
    result = 10 / value
except ValueError:
    print("Invalid input — not a number")
except ZeroDivisionError:
    print("Cannot divide by zero")
```

### One `except` block for multiple types (same handling)

```python
try:
    ...
except (ValueError, TypeError) as e:
    print(f"Input problem: {e}")
```

### Catching everything (use sparingly)

```python
try:
    ...
except Exception as e:
    print(f"Something went wrong: {e}")
```

`except Exception` catches almost all runtime errors, but not things like `KeyboardInterrupt` or `SystemExit` (which inherit from `BaseException`, not `Exception` — see the hierarchy below). A bare `except:` (no type at all) catches literally everything, including those — this is almost always a mistake in real code, since it can silently swallow `Ctrl+C` or hide bugs unrelated to what you intended to handle.

**Order matters:** Python checks `except` blocks top to bottom and stops at the first match. More specific exceptions should come before more general ones.

```python
try:
    ...
except Exception:      # too broad, placed first — this WILL run for everything below
    print("generic")
except ValueError:       # unreachable! Exception already caught it
    print("specific")
```

---

## 4. else and finally

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Division failed")
else:
    print(f"Success: {result}")   # runs ONLY if no exception occurred
finally:
    print("This always runs")     # runs no matter what
```

```text
Success: 5.0
This always runs
```

- **`else`** — runs only when the `try` block completes with no exception. Useful for code that should run after success, but that you don't want accidentally caught by the `except` block if it also fails.
- **`finally`** — always runs, whether an exception occurred, was caught, or wasn't caught at all. Used for cleanup that must happen regardless of outcome (closing files, releasing locks, closing connections).

```python
file = None
try:
    file = open("data.txt")
    content = file.read()
except FileNotFoundError:
    print("File not found")
finally:
    if file:
        file.close()   # always closes, even if read() failed
```

(In practice, a `with` statement — see Section 9 — is the preferred way to handle this exact pattern.)

---

## 5. Raising Exceptions

Use `raise` to trigger an exception deliberately — either a built-in type or a custom one.

```python
def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("Insufficient funds")
    return balance - amount

withdraw(100, 500)   # raises ValueError: Insufficient funds
```

### Re-raising

Inside an `except` block, a bare `raise` re-raises the exception currently being handled — useful for logging or partial handling before letting it propagate further up.

```python
try:
    risky_operation()
except ValueError as e:
    print(f"Logging the error: {e}")
    raise   # re-raise the same exception, preserving the original traceback
```

### Raising a different exception (exception chaining)

```python
try:
    connect_to_database()
except ConnectionError as e:
    raise RuntimeError("Failed to start application") from e
```

`from e` preserves the original exception as the documented **cause**, so the traceback shows both errors — this is far more useful for debugging than losing the original context.

```text
ConnectionError: could not connect
The above exception was the direct cause of the following exception:
RuntimeError: Failed to start application
```

---

## 6. Custom Exceptions

Defining your own exception types makes error handling more precise and self-documenting than relying only on generic built-ins.

```python
class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""
    pass

class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount}, balance is only {self.balance}"
            )
        self.balance -= amount

account = BankAccount(100)
account.withdraw(500)   # raises InsufficientFundsError
```

Custom exceptions should always inherit (directly or indirectly) from `Exception`, never from `BaseException` directly.

### Building an exception hierarchy for an application

```python
class AppError(Exception):
    """Base exception for all application-specific errors."""

class ValidationError(AppError):
    pass

class AuthenticationError(AppError):
    pass

class NotFoundError(AppError):
    pass
```

This lets calling code catch broadly or narrowly, depending on what it needs:

```python
try:
    process_request()
except ValidationError:
    print("Fix your input")
except AppError:              # catches AuthenticationError, NotFoundError, and any other AppError subclass
    print("Something else went wrong in the app")
```

Adding custom data to an exception:

```python
class ValidationError(AppError):
    def __init__(self, field, message):
        self.field = field
        super().__init__(message)

try:
    raise ValidationError("email", "Invalid email format")
except ValidationError as e:
    print(f"Field '{e.field}' failed: {e}")
```

---

## 7. The Exception Hierarchy

Every exception in Python inherits from `BaseException`. Understanding this hierarchy explains why `except Exception` doesn't catch everything, and why that's actually the correct default behavior.

```text
BaseException
 ├── SystemExit           (raised by sys.exit())
 ├── KeyboardInterrupt    (raised by Ctrl+C)
 ├── GeneratorExit
 └── Exception             ← almost everything you should ever catch
      ├── ArithmeticError
      │    └── ZeroDivisionError
      ├── LookupError
      │    ├── IndexError
      │    └── KeyError
      ├── ValueError
      ├── TypeError
      ├── AttributeError
      ├── FileNotFoundError  (subclass of OSError)
      ├── OSError
      ├── RuntimeError
      │    └── RecursionError
      ├── StopIteration
      └── ImportError
           └── ModuleNotFoundError
```

Why this design matters: `SystemExit` and `KeyboardInterrupt` deliberately sit outside `Exception`, so that a broad `except Exception:` handler (or logging middleware) doesn't accidentally block a program from exiting cleanly or responding to `Ctrl+C`.

A few of the most commonly encountered built-ins, worth recognizing on sight:

| Exception              | Typical cause                                       |
|--------------------------|--------------------------------------------------------|
| `ValueError`              | Right type, invalid value (`int("abc")`)               |
| `TypeError`               | Wrong type used for an operation (`"a" + 1`)             |
| `KeyError`                 | Missing dictionary key                                    |
| `IndexError`                | List/sequence index out of range                          |
| `AttributeError`             | Accessing a nonexistent attribute/method                    |
| `FileNotFoundError`           | Opening a file that doesn't exist                             |
| `ZeroDivisionError`             | Dividing by zero                                                |
| `ImportError`/`ModuleNotFoundError` | Importing a module that can't be found                    |
| `StopIteration`                   | Raised internally when an iterator is exhausted                |

---

## 8. assert

`assert` checks that a condition is true, and raises `AssertionError` if it isn't. It's meant for catching **programming bugs and invariants during development**, not for handling expected runtime errors like bad user input.

```python
def divide(a, b):
    assert b != 0, "b must not be zero"
    return a / b

divide(10, 0)   # AssertionError: b must not be zero
```

Important caveat: assertions can be **globally disabled** by running Python with the `-O` (optimize) flag, in which case every `assert` statement is skipped entirely. This means `assert` should **never** be used to enforce security checks, validate untrusted user input, or run logic your program depends on for correctness.

```python
# WRONG — assert should never guard real logic
assert user.is_authenticated, "Not authenticated"   # can be stripped in production!

# RIGHT — use a real exception for anything that must always run
if not user.is_authenticated:
    raise PermissionError("Not authenticated")
```

`assert` is best reserved for internal sanity checks and tests (`unittest`, `pytest` rely on it heavily for that reason).

---

## 9. Exceptions and Context Managers (`with`)

The `with` statement (backed by `__enter__`/`__exit__`, covered in the OOP Advanced doc) is the standard, safer alternative to manual `try/finally` for resource cleanup.

```python
try:
    file = open("data.txt")
    content = file.read()
finally:
    file.close()
```

is more reliably written as:

```python
with open("data.txt") as file:
    content = file.read()
# file is automatically closed here, even if read() raises an exception
```

### `contextlib.suppress` — silencing specific expected exceptions

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    import os
    os.remove("temp.txt")   # if the file doesn't exist, just move on silently
```

This is a cleaner, more explicit alternative to:

```python
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass
```

---

## 10. EAFP vs LBYL

Two philosophies for handling potential errors, both valid, with Python culturally leaning toward the first.

### EAFP — "Easier to Ask Forgiveness than Permission"

Attempt the operation, and handle the exception if it fails.

```python
try:
    value = my_dict["key"]
except KeyError:
    value = "default"
```

### LBYL — "Look Before You Leap"

Check conditions before attempting the operation.

```python
if "key" in my_dict:
    value = my_dict["key"]
else:
    value = "default"
```

Python idiomatically favors EAFP for several reasons:

- It avoids a **race condition** where a condition can become false between the check and the actual operation (e.g. checking `os.path.exists(file)` then opening it — the file could be deleted in between)
- It's often faster in the common case, since no separate check is performed before the operation
- It reads more naturally for many built-in patterns (`dict.get()`, exception-based iteration via `StopIteration`, etc.)

```python
# EAFP — preferred idiom
try:
    with open("config.json") as f:
        data = f.read()
except FileNotFoundError:
    data = "{}"
```

```python
# LBYL — has a race condition: file could vanish between the check and the open()
if os.path.exists("config.json"):
    with open("config.json") as f:
        data = f.read()
```

`dict.get(key, default)` is itself a common shortcut that avoids needing either pattern for simple lookups:

```python
value = my_dict.get("key", "default")
```

---

## 11. Logging Exceptions

In real applications, exceptions caught during operation should almost always be **logged**, not just printed or silently ignored — visibility into failures is critical for debugging production issues.

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    result = 10 / 0
except ZeroDivisionError:
    logger.error("Division failed", exc_info=True)
```

`exc_info=True` includes the full traceback in the log output, not just the error message — essential for diagnosing what actually happened.

```python
try:
    process_order(order_id)
except AppError as e:
    logger.exception(f"Failed to process order {order_id}")
    # logger.exception() is shorthand for logger.error(..., exc_info=True), used inside an except block
```

Silently swallowing exceptions (`except Exception: pass`) is one of the most common real-world bugs — it hides failures instead of surfacing them, and makes debugging production issues far harder later.

---

## Key Points

- Exceptions are objects Python raises when something goes wrong; uncaught ones produce a traceback and stop the program
- `try`/`except` catches and handles specific exception types; order `except` blocks from most to least specific
- `else` runs only on success, `finally` always runs — typically used for cleanup
- `raise` triggers exceptions manually; a bare `raise` inside `except` re-raises the current exception; `raise NewError from original` chains exceptions with full context
- Custom exceptions (subclassing `Exception`) make error handling precise and self-documenting — build a small hierarchy for larger applications
- `BaseException` sits above `Exception`, deliberately excluding `SystemExit`/`KeyboardInterrupt` so broad handlers don't block program exit
- `assert` is for development-time invariants only — it can be disabled with `-O` and must never guard real application logic
- `with` (and `contextlib.suppress`) is the preferred, safer alternative to manual `try/finally` for resource cleanup
- EAFP (try it, handle failure) is the Pythonic default over LBYL (check first) — it avoids race conditions and often reads more naturally
- Caught exceptions should be logged with full context (`exc_info=True` / `logger.exception()`), never silently swallowed