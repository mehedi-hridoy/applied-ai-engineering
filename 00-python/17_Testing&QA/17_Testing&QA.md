# Python Testing & QA

Writing code that works once isn't enough for real systems — it needs to keep working as the codebase changes. Testing is how you get that guarantee automatically instead of manually re-checking everything by hand. This document covers the practical skills: writing tests with `unittest` and `pytest`, structuring them well, mocking dependencies, and the surrounding QA mindset.

---

## 1. Why Testing Matters (Beyond "Catching Bugs")

- **Confidence to change code** — tests let you refactor or extend a codebase without fear of silently breaking something else
- **Executable documentation** — a good test shows exactly how a function is meant to be used, and what it guarantees
- **Faster feedback loop** — catching a bug via a failing test in seconds is far cheaper than catching it in production
- **Design pressure** — code that's hard to test is often a sign of poor design (too many responsibilities, hidden dependencies) — writing tests early tends to naturally push toward cleaner code

---

## 2. Types of Tests

| Type            | Scope                                        | Speed     | Example                                        |
|------------------|-------------------------------------------------|-----------|---------------------------------------------------|
| **Unit test**       | A single function/method, in isolation             | Very fast   | Testing `calculate_total()` with fixed inputs        |
| **Integration test**  | Multiple components working together              | Slower       | Testing that a service correctly saves to a real database |
| **End-to-end (E2E) test** | The entire system, as a user would experience it | Slowest        | Simulating a full user signup flow through the actual app |

A healthy test suite typically has **many** unit tests, **some** integration tests, and **few** end-to-end tests — commonly visualized as the "testing pyramid," since unit tests are cheapest to write and run, while E2E tests are the most expensive and brittle.

```text
        /\
       /E2E\        <- few, slow, expensive
      /------\
     /Integr. \      <- some
    /----------\
   /   Unit     \     <- many, fast, cheap
  /--------------\
```

---

## 3. `unittest` — Python's Built-in Testing Framework

Part of the standard library — no installation needed. Test cases are organized as classes inheriting from `unittest.TestCase`.

```python
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

if __name__ == "__main__":
    unittest.main()
```

Run with:

```bash
python -m unittest test_module.py
```

### Common assertion methods

```python
self.assertEqual(a, b)          # a == b
self.assertNotEqual(a, b)         # a != b
self.assertTrue(x)                  # bool(x) is True
self.assertFalse(x)                   # bool(x) is False
self.assertIsNone(x)                    # x is None
self.assertIn(item, container)            # item in container
self.assertRaises(ValueError, func, arg)   # calling func(arg) raises ValueError
self.assertAlmostEqual(0.1 + 0.2, 0.3, places=5)   # for float comparisons
```

### `assertRaises` as a context manager (more common in practice)

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class TestDivide(unittest.TestCase):
    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)
```

### `setUp` and `tearDown`

Run automatically before/after **each** test method — used to prepare and clean up shared state, so tests don't repeat setup code or leak state between each other.

```python
class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount(balance=100)   # fresh account before EVERY test

    def test_deposit(self):
        self.account.deposit(50)
        self.assertEqual(self.account.balance, 150)

    def test_withdraw(self):
        self.account.withdraw(30)
        self.assertEqual(self.account.balance, 70)

    def tearDown(self):
        pass   # e.g. close a connection, delete a temp file — runs after every test
```

Since `setUp` runs before every single test method, each test starts from a clean, independent state — this is essential for reliable, order-independent tests.

---

## 4. `pytest` — The Modern, Widely-Used Alternative

Not part of the standard library (`pip install pytest`), but the dominant testing tool across the Python ecosystem in practice — simpler syntax, more powerful features, better output.

```python
def add(a, b):
    return a + b

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2
```

Run with:

```bash
pytest
```

Key differences from `unittest`:

- Plain `assert` statements instead of `self.assertEqual(...)` — pytest rewrites assertions to give detailed failure output automatically
- Tests can be plain functions — no class or inheritance required (though classes are still supported)
- Test discovery is automatic — files named `test_*.py` or `*_test.py`, functions named `test_*`

```python
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

When an assertion fails, pytest shows exactly what the actual vs expected values were, without needing a specific assertion method for each comparison type:

```text
def test_add():
>       assert add(2, 3) == 6
E       assert 5 == 6
```

### Testing exceptions in pytest

```python
import pytest

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

def test_divide_by_zero_message():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

---

## 5. Fixtures (pytest)

A **fixture** provides reusable setup (and optional teardown) for tests — pytest's more flexible replacement for `setUp`/`tearDown`.

```python
import pytest

@pytest.fixture
def account():
    return BankAccount(balance=100)   # fresh account provided to any test that asks for it

def test_deposit(account):     # pytest automatically injects the fixture by parameter name
    account.deposit(50)
    assert account.balance == 150

def test_withdraw(account):
    account.withdraw(30)
    assert account.balance == 70
```

Each test gets its own independent `account` object, freshly created by the fixture — matching the isolation `setUp` provides, but declared once and reused across any test that needs it, simply by naming it as a parameter.

### Fixtures with teardown

```python
@pytest.fixture
def db_connection():
    conn = connect_to_test_db()   # setup
    yield conn                       # the test runs here, using `conn`
    conn.close()                       # teardown — runs after the test finishes
```

The `yield` splits the fixture into a setup phase (before `yield`) and a teardown phase (after `yield`), which always runs — even if the test itself fails.

### Fixture scope

```python
@pytest.fixture(scope="function")   # default — new instance per test
@pytest.fixture(scope="module")      # shared across all tests in one file
@pytest.fixture(scope="session")       # shared across the entire test run
```

Broader scopes are useful for expensive setup (like a real database connection) that doesn't need to be recreated for every single test.

---

## 6. Parametrized Tests

Running the same test logic against multiple sets of inputs, without duplicating the test function.

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

This runs as four separate test cases — if one combination fails, pytest reports exactly which input set failed, without needing four nearly-identical test functions written by hand.

---

## 7. Mocking and Test Doubles

Real code often depends on things you don't want to actually run during a test — network calls, databases, the current time, external APIs. **Mocking** replaces these dependencies with controlled stand-ins.

### Terminology

| Term       | Meaning                                                    |
|------------|----------------------------------------------------------------|
| **Mock**      | A fake object that records how it was called, for later verification |
| **Stub**       | A fake object that returns canned/fixed responses                       |
| **Fake**        | A simplified, working implementation (e.g. an in-memory database instead of a real one) |

In practice, Python's `unittest.mock` (built into the standard library) blurs these lines somewhat — its `Mock`/`MagicMock` objects can act as any of the three depending on how they're configured.

### Basic `Mock`

```python
from unittest.mock import Mock

mock_service = Mock()
mock_service.get_data.return_value = {"status": "ok"}

result = mock_service.get_data()
print(result)   # {"status": "ok"}

mock_service.get_data.assert_called_once()   # verify it was actually called
```

### `patch` — replacing real dependencies during a test

```python
from unittest.mock import patch

def get_current_price(api):
    return api.fetch_price("AAPL")

def test_get_current_price():
    with patch("mymodule.ExternalAPI") as mock_api_class:
        mock_api_class.return_value.fetch_price.return_value = 150.0
        api = mock_api_class()
        assert get_current_price(api) == 150.0
```

`patch()` temporarily replaces the target with a `Mock` for the duration of the `with` block (or, as a decorator, for the duration of the test function) — the real implementation is automatically restored afterward.

### Patching as a decorator

```python
from unittest.mock import patch

@patch("mymodule.requests.get")
def test_fetch_data(mock_get):
    mock_get.return_value.json.return_value = {"name": "Mehedi"}

    result = fetch_data("http://example.com")
    assert result == {"name": "Mehedi"}
    mock_get.assert_called_once_with("http://example.com")
```

This test never makes a real network call — `requests.get` is entirely replaced for the duration of the test, making the test fast, deterministic, and independent of any actual external service being available.

### Why mocking matters

- Tests stay **fast** — no real network/database round trips
- Tests stay **deterministic** — no flakiness from external services being slow, down, or returning different data over time
- Tests stay **isolated** — a unit test for `process_payment()` shouldn't fail because a third-party payment gateway happened to be down

---

## 8. Test Structure: Arrange-Act-Assert (AAA)

A widely used convention for organizing the body of a test clearly, regardless of framework.

```python
def test_withdraw_reduces_balance():
    # Arrange — set up the scenario
    account = BankAccount(balance=100)

    # Act — perform the action being tested
    account.withdraw(30)

    # Assert — verify the outcome
    assert account.balance == 70
```

Keeping these three sections visually distinct (even with just a blank line or comment) makes tests easier to read and debug — you can immediately see what's being set up, what's being tested, and what's expected.

---

## 9. What Makes a Good Test

- **Independent** — tests shouldn't depend on each other's execution order or shared mutable state
- **Repeatable** — running the same test twice should always give the same result (no reliance on the current time, random values, or external services without controlling them)
- **Fast** — a slow test suite gets run less often, which defeats the purpose; push slow integration/E2E tests to a separate, less-frequent run if needed
- **Focused** — a unit test should verify one specific behavior; when it fails, it should be immediately clear what broke
- **Clear failure messages** — a good test tells you *what* went wrong without needing to dig through the test code itself

```python
# unclear — doesn't test one specific thing, hard to know what failed if it does
def test_account():
    account = BankAccount(100)
    account.deposit(50)
    account.withdraw(30)
    assert account.balance == 120
    assert account.transaction_count == 2
    assert account.is_active

# clearer — one behavior per test
def test_deposit_increases_balance():
    account = BankAccount(100)
    account.deposit(50)
    assert account.balance == 150

def test_withdraw_decreases_balance():
    account = BankAccount(100)
    account.withdraw(30)
    assert account.balance == 70
```

---

## 10. Code Coverage

**Coverage** measures what percentage of your code is actually executed by your test suite — a useful signal, but not a goal to chase blindly.

```bash
pip install pytest-cov
pytest --cov=mymodule
```

```text
Name          Stmts   Miss  Cover
---------------------------------
mymodule.py      50      5    90%
```

Important caveat: **high coverage doesn't mean well-tested code.** A test can execute a line without ever actually verifying its behavior — coverage tells you what ran, not whether it was checked correctly.

```python
def divide(a, b):
    return a / b

# executes the line (100% coverage), but never checks the actual result — a weak test
def test_divide():
    divide(10, 2)   # no assertion at all!
```

Coverage is best used to find **obviously untested code** (a function or branch with 0% coverage is a clear gap), not as a target percentage to chase for its own sake.

---

## 11. Test-Driven Development (TDD)

A development style where tests are written **before** the implementation, following a short repeating cycle:

1. **Red** — write a failing test for behavior that doesn't exist yet
2. **Green** — write the minimum code needed to make the test pass
3. **Refactor** — clean up the implementation, with the test suite as a safety net

```python
# 1. RED — write the test first, for a function that doesn't exist yet
def test_is_palindrome():
    assert is_palindrome("racecar") == True
    assert is_palindrome("hello") == False

# 2. GREEN — write just enough code to pass
def is_palindrome(s):
    return s == s[::-1]

# 3. REFACTOR — improve the implementation if needed, tests confirm nothing broke
def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
```

TDD isn't universally practiced for every line of code in real teams, but the underlying discipline — thinking about expected behavior and edge cases *before* writing the implementation — tends to produce clearer, more testable code even when followed loosely.

---

## 12. Organizing a Test Suite

A typical project layout separates test code from application code, mirroring the structure being tested:

```text
myproject/
├── myapp/
│   ├── __init__.py
│   ├── models.py
│   └── services.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_services.py
```

Conventions worth following:

- Test file names start with `test_` (pytest's default discovery pattern)
- Test function/method names should describe the behavior being verified: `test_withdraw_raises_error_when_insufficient_funds`, not `test_1` or `test_withdraw`
- Group related tests into classes when it aids organization, even with pytest's function-style tests: `class TestBankAccount:` with methods inside

---

## Key Points

- Tests give confidence to change code safely, act as documentation, and provide fast feedback — a healthy suite favors many fast unit tests over few slow end-to-end tests
- `unittest` (standard library) uses `TestCase` classes, `assertEqual`-style methods, and `setUp`/`tearDown` for per-test isolation
- `pytest` is the dominant real-world tool — plain `assert` statements, automatic test discovery, and detailed failure output without needing many specialized assertion methods
- Fixtures (`@pytest.fixture`) provide reusable setup/teardown, injected by parameter name, with configurable scope for expensive resources
- Parametrized tests (`@pytest.mark.parametrize`) run the same logic against multiple input sets without duplicating test functions
- Mocking (`unittest.mock`, `patch`) replaces real dependencies (APIs, databases, network calls) with controlled stand-ins, keeping tests fast, deterministic, and isolated
- The Arrange-Act-Assert structure keeps individual tests readable and easy to debug
- Good tests are independent, repeatable, fast, and focused on one specific behavior each
- Code coverage highlights untested code but doesn't measure test quality — a covered line isn't necessarily a well-verified one
- TDD (write the test first, then the code, then refactor) is a discipline that tends to produce clearer, more testable designs even when not followed strictly for every change