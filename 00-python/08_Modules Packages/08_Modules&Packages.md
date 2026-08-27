# Python Modules & Packages

## Creating Modules

A **module** is simply a `.py` file. Any Python file you write can be treated as a module and reused elsewhere — that's the entire idea. There's no special syntax needed to "make" something a module; saving code in a file is enough.

**`mathutils.py`**
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

PI = 3.14159
```

**`main.py`**
```python
import mathutils

print(mathutils.add(2, 3))     # 5
print(mathutils.PI)             # 3.14159
```

Why modules matter:

- They let you split a large program into smaller, focused files
- Code becomes reusable across multiple programs, instead of being copy-pasted
- They create a separate **namespace**, so names in one module don't clash with names in another, even if identical

```python
# file1.py
def process():
    return "from file1"

# file2.py
def process():
    return "from file2"

# main.py
import file1
import file2

file1.process()   # "from file1"
file2.process()   # "from file2" — no conflict
```

When a module is imported, Python runs the entire file top to bottom, once, and then caches the result — importing it again elsewhere in the same run does not re-execute it.

---

## import Variations

Python offers several forms of `import`, each with different trade-offs for namespace clarity.

### `import module`

Imports the whole module; access everything through the module name.

```python
import math
math.sqrt(16)   # 4.0
```

### `import module as alias`

Imports the module under a shorter or clearer name.

```python
import numpy as np
np.array([1, 2, 3])
```

### `from module import name`

Imports specific names directly into the current namespace — no prefix needed.

```python
from math import sqrt, pi
sqrt(16)   # 4.0
print(pi)   # 3.14159...
```

### `from module import name as alias`

```python
from math import sqrt as square_root
square_root(16)
```

### `from module import *`

Imports **all** public names from a module directly into the current namespace.

```python
from math import *
sqrt(16)
pi
```

This is generally discouraged in real code:

- It's unclear where a name came from when reading the code later
- It risks silently overwriting existing names in your namespace
- It can pull in far more names than you actually need

A module can control what `import *` exposes using an `__all__` list:

```python
# mathutils.py
__all__ = ["add"]   # only 'add' is exported by import *

def add(a, b):
    return a + b

def subtract(a, b):   # not exported by import *
    return a - b
```

**Rule of thumb:** prefer `import module` or `from module import specific_name` — both keep it clear where a name came from.

---

## `__name__ == '__main__'`

Every Python module has a built-in variable called `__name__`. Its value depends on how the file is being used:

- If the file is **run directly** (`python file.py`), `__name__` is set to `"__main__"`
- If the file is **imported** as a module into another file, `__name__` is set to the module's actual name

```python
# greetings.py
def greet():
    print("Hello!")

print(f"This module's __name__ is: {__name__}")

if __name__ == "__main__":
    greet()
```

- Running `python greetings.py` directly → prints the `__name__` line, then `"Hello!"`, since `__name__` is `"__main__"`
- Running `import greetings` from another file → only prints the `__name__` line (which now shows `"greetings"`); `greet()` does **not** run automatically

Why this matters: it lets a file act as **both** a reusable module and a standalone script.

```python
# calculator.py
def add(a, b):
    return a + b

def main():
    print(add(2, 3))

if __name__ == "__main__":
    main()
```

If another file does `from calculator import add`, only `add` is imported — `main()` never runs, and no unwanted output appears. But running `calculator.py` directly still works as a script. This pattern is extremely common and worth internalizing.

---

## Module Search Path (sys.path)

When you `import something`, Python needs to know where to look for that file. It searches, in order:

1. The directory of the script currently being run
2. Directories listed in the `PYTHONPATH` environment variable (if set)
3. The standard library's installation directories
4. Site-packages — where installed third-party packages live (via `pip`)

This search order is stored as a list in `sys.path`, which you can inspect and even modify at runtime.

```python
import sys
print(sys.path)
```

```text
['', '/usr/lib/python3.11', '/usr/lib/python3.11/site-packages', ...]
```

The empty string `''` at the start typically represents the current directory.

If Python can't find a module anywhere in `sys.path`, it raises:

```python
ModuleNotFoundError: No module named 'something'
```

You can add a directory to the search path manually (useful in scripts, though not the cleanest long-term solution):

```python
import sys
sys.path.append("/path/to/my/modules")
```

In real projects, path issues are more commonly solved using virtual environments, proper package structure, or setting `PYTHONPATH`, rather than editing `sys.path` directly.

---

## Packages & `__init__.py`

A **package** is a directory containing multiple related modules, structured so Python recognizes it as an importable unit.

```text
mypackage/
├── __init__.py
├── math_utils.py
└── string_utils.py
```

```python
# math_utils.py
def add(a, b):
    return a + b
```

```python
# main.py
from mypackage import math_utils
math_utils.add(2, 3)
```

or

```python
from mypackage.math_utils import add
add(2, 3)
```

### What `__init__.py` Does

`__init__.py` marks a directory as a Python package (required in older Python versions; optional but still very common and useful in Python 3.3+, where "namespace packages" without it are technically allowed).

It also runs automatically whenever the package is imported, which makes it useful for:

- Controlling what's exposed when someone does `from mypackage import *`
- Re-exporting names from submodules, for a cleaner public interface

```python
# mypackage/__init__.py
from .math_utils import add
from .string_utils import shout

__all__ = ["add", "shout"]
```

Now users can do:

```python
from mypackage import add, shout
```

instead of reaching into each submodule individually. This is a common pattern for designing a clean public API for a package.

### Nested Packages (Subpackages)

Packages can contain other packages:

```text
myapp/
├── __init__.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── models/
    ├── __init__.py
    └── user.py
```

```python
from myapp.utils.helpers import some_function
from myapp.models.user import User
```

---

## Standard Library Tour

Python ships with a large **standard library** — modules that are always available, with no installation needed (`pip install` not required). This is often summarized as Python's "batteries included" philosophy.

A few categories worth knowing exist:

| Category            | Examples                          |
|----------------------|-------------------------------------|
| Math & numbers        | `math`, `random`, `decimal`, `statistics` |
| Date & time            | `datetime`, `time`, `calendar`     |
| File & OS              | `os`, `sys`, `shutil`, `pathlib`    |
| Data handling          | `json`, `csv`, `re`, `collections` |
| Networking             | `socket`, `urllib`, `http`         |
| Concurrency            | `threading`, `multiprocessing`, `asyncio` |
| Testing                | `unittest`                          |

You can check what's available and read documentation directly from the interpreter:

```python
import math
help(math)          # shows documentation
dir(math)           # lists all names defined in the module
```

The two modules below (`random`, `datetime`) are two of the most frequently used in everyday scripts.

---

## math

Provides mathematical functions and constants beyond the basic arithmetic operators.

```python
import math

math.sqrt(16)        # 4.0
math.pow(2, 3)        # 8.0  (returns float, unlike ** which can return int)
math.floor(4.7)       # 4
math.ceil(4.2)         # 5
math.factorial(5)      # 120
math.gcd(12, 18)        # 6

math.pi                # 3.141592653589793
math.e                  # 2.718281828459045

math.log(100, 10)       # 2.0  (log base 10 of 100)
math.log(math.e)         # 1.0  (natural log)

math.sin(math.pi / 2)     # 1.0
```

Notable difference from the built-in `**` operator: `math.pow()` always returns a `float`, while `**` returns an `int` if both operands are ints.

```python
2 ** 3          # 8   (int)
math.pow(2, 3)   # 8.0 (float)
```

---

## random

Generates pseudo-random numbers and performs random selections. Not suitable for cryptographic/security purposes (use the `secrets` module for that).

```python
import random

random.random()             # random float between 0.0 and 1.0
random.randint(1, 10)        # random int between 1 and 10, inclusive
random.uniform(1.5, 5.5)      # random float in a range

fruits = ["apple", "banana", "mango"]
random.choice(fruits)          # a single random item
random.choices(fruits, k=2)     # random items, with replacement
random.sample(fruits, 2)         # random items, without replacement

random.shuffle(fruits)            # shuffles the list in place
```

Randomness can be made reproducible using a **seed** — the same seed always produces the same sequence of "random" results, which is useful for testing.

```python
random.seed(42)
random.randint(1, 100)   # same result every time this seed is used
```

---

## datetime

Represents and manipulates dates and times.

```python
from datetime import datetime, date, timedelta

now = datetime.now()
print(now)   # e.g. 2026-08-27 14:32:10.123456

today = date.today()
print(today)   # e.g. 2026-08-27
```

### Creating specific dates/times

```python
d = date(2026, 8, 27)
dt = datetime(2026, 8, 27, 14, 30, 0)
```

### Formatting (datetime → string)

```python
now.strftime("%Y-%m-%d")        # '2026-08-27'
now.strftime("%d/%m/%Y %H:%M")  # '27/08/2026 14:30'
```

### Parsing (string → datetime)

```python
datetime.strptime("2026-08-27", "%Y-%m-%d")
```

### Date Arithmetic

`timedelta` represents a duration, and can be added to or subtracted from dates/times.

```python
tomorrow = today + timedelta(days=1)
last_week = today - timedelta(weeks=1)

diff = date(2026, 12, 31) - date(2026, 8, 27)
print(diff.days)   # number of days between the two dates
```

`datetime` objects are also directly comparable:

```python
date(2026, 1, 1) < date(2026, 12, 31)   # True
```

---

## Key Points

- A module is just a `.py` file; importing it runs it once and caches the result for reuse
- `import module`, `from module import name`, and aliasing (`as`) are the main import forms — avoid `import *` in real code, since it hides where names come from
- `if __name__ == "__main__":` lets a file work as both an importable module and a standalone script
- `sys.path` defines where Python looks for modules — current directory, `PYTHONPATH`, standard library, then site-packages
- A package is a directory with an `__init__.py` file, treated as a namespace for related modules
- `__init__.py` runs on import and is commonly used to re-export names for a cleaner public API
- The standard library ships with Python and needs no installation — `math`, `random`, and `datetime` are three of the most commonly used modules
- `math` provides mathematical functions and constants; `random` generates pseudo-random values (seedable for reproducibility); `datetime` handles dates, times, formatting, and date arithmetic