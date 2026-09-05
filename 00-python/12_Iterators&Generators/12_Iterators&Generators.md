# Python Iterators & Generators

Iteration is everywhere in Python — every `for` loop, every unpacking, every comprehension relies on it. This document explains what's actually happening underneath `for x in something`, and how to build your own lazy, memory-efficient sequences using iterators and generators.

---

## 1. Iterables vs Iterators

These two words are related but mean different things — mixing them up is one of the most common sources of confusion.

### Iterable

Any object you can loop over — it implements `__iter__()`, which returns an **iterator**.

```python
numbers = [1, 2, 3]   # a list is iterable
for n in numbers:
    print(n)
```

### Iterator

The object that actually produces items **one at a time**, keeping track of where it is. It implements both `__iter__()` (returning itself) and `__next__()` (returning the next value, or raising `StopIteration` when exhausted).

```python
numbers = [1, 2, 3]
iterator = iter(numbers)   # get an iterator FROM the iterable

print(next(iterator))   # 1
print(next(iterator))   # 2
print(next(iterator))   # 3
print(next(iterator))   # raises StopIteration
```

**Key distinction:** a list is iterable, but it is *not* itself an iterator — it doesn't remember position between loops. Calling `iter()` on it creates a fresh iterator every time.

```python
numbers = [1, 2, 3]

for n in numbers:   # first pass
    pass

for n in numbers:   # second pass — starts over from the beginning
    print(n)          # 1, 2, 3 — works fine, because iter() creates a new iterator each time
```

An iterator, by contrast, is exhausted after one pass and cannot be reset:

```python
iterator = iter([1, 2, 3])
list(iterator)   # [1, 2, 3]
list(iterator)   # [] — already exhausted
```

### What `for` actually does

A `for` loop is syntactic sugar around this exact mechanism:

```python
for item in [1, 2, 3]:
    print(item)
```

is equivalent to:

```python
iterator = iter([1, 2, 3])
while True:
    try:
        item = next(iterator)
    except StopIteration:
        break
    print(item)
```

---

## 2. Building a Custom Iterator

Any class can be made iterable by implementing `__iter__` and `__next__` — this is called the **iterator protocol**.

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self   # the object is its own iterator

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for num in Countdown(3):
    print(num)   # 3, 2, 1
```

Because `Countdown` implements the protocol, it also works with everything else that expects an iterable:

```python
list(Countdown(3))       # [3, 2, 1]
sum(Countdown(3))         # 6
max(Countdown(3))          # 3
```

### Separating the iterable from the iterator

In the example above, `Countdown` is both — which means it can only be iterated once, like a raw iterator. A cleaner, reusable design separates the two: the class is the iterable and creates a fresh iterator object each time `__iter__` is called.

```python
class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)

class CountdownIterator:
    def __init__(self, current):
        self.current = current

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

cd = Countdown(3)
list(cd)   # [3, 2, 1]
list(cd)   # [3, 2, 1] — works again, since a new iterator is created each time
```

This two-class pattern is exactly what generators (below) eliminate the need to write by hand.

---

## 3. Generator Functions

A **generator function** is a much simpler way to write an iterator. It looks like a normal function, but uses `yield` instead of (or alongside) `return`. Calling it doesn't run the function body — it returns a generator object, which is itself an iterator.

```python
def countdown(start):
    while start > 0:
        yield start
        start -= 1

for num in countdown(3):
    print(num)   # 3, 2, 1
```

```python
gen = countdown(3)
print(gen)          # <generator object countdown at 0x...>
print(next(gen))     # 3
print(next(gen))     # 2
print(next(gen))     # 1
print(next(gen))     # raises StopIteration
```

### How `yield` actually works

Each time `next()` is called on the generator, the function runs until it hits a `yield`, returns that value, and **pauses** — with its entire local state (variables, position in the code) frozen in place. The next `next()` call resumes exactly where it left off.

```python
def demo():
    print("start")
    yield 1
    print("middle")
    yield 2
    print("end")

gen = demo()
next(gen)   # prints "start", returns 1
next(gen)   # prints "middle", returns 2
next(gen)   # prints "end", then raises StopIteration
```

This pause-and-resume behavior — impossible with a plain `return`-based function — is what makes generators fundamentally different from regular functions, and is the entire mechanism behind lazy evaluation.

---

## 4. Why Generators Matter: Laziness and Memory

The core benefit of generators is that values are produced **one at a time, on demand**, instead of computing and storing everything in memory at once.

```python
# eager — builds the entire list in memory before returning
def get_squares(n):
    return [x ** 2 for x in range(n)]

# lazy — computes one value at a time, only when asked
def get_squares_gen(n):
    for x in range(n):
        yield x ** 2
```

```python
squares = get_squares(10_000_000)        # builds a 10-million-item list in memory right now
squares_gen = get_squares_gen(10_000_000)   # builds essentially nothing yet — just a paused function
```

This matters enormously for:

- Processing huge or unbounded data (large files, infinite streams, API pagination)
- Pipelines where only a few values are actually needed, avoiding wasted computation
- Reducing peak memory usage in data-heavy programs

```python
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

for line in read_large_file("huge_log.txt"):
    if "ERROR" in line:
        print(line)
        break   # stops immediately — the rest of the file is never even read
```

A regular function that first loaded the whole file into a list would read and store the entire file even though only the first matching line was needed.

---

## 5. Generator Expressions

A compact, one-line way to create a generator, using the same syntax as a list comprehension but with parentheses instead of brackets (covered briefly in the DSA doc — expanded here).

```python
squares = (x ** 2 for x in range(5))
print(squares)          # <generator object <genexpr> at 0x...>
print(list(squares))     # [0, 1, 4, 9, 16]
```

```python
total = sum(x ** 2 for x in range(1_000_000))   # never builds the full list — computed lazily, one value at a time
```

Generator expressions are ideal when a generator's result is only going to be consumed once, immediately, by something like `sum()`, `max()`, `any()`, or a `for` loop — for anything more complex (multiple `yield` points, conditional logic across lines), a full generator function is clearer.

---

## 6. Infinite Generators

Since values are computed lazily, generators can represent sequences that never end — something a list obviously cannot do.

```python
def infinite_counter(start=0):
    while True:
        yield start
        start += 1

counter = infinite_counter()
print(next(counter))   # 0
print(next(counter))    # 1
print(next(counter))     # 2
# ... goes on forever if you keep calling next()
```

This is only safe because the consumer controls how many values to pull — usually paired with something that stops early:

```python
from itertools import islice

first_five = list(islice(infinite_counter(), 5))
print(first_five)   # [0, 1, 2, 3, 4]
```

---

## 7. yield vs return, and Multiple Yields

A function containing `yield` anywhere in its body becomes a generator function — this changes its behavior fundamentally, even if `yield` only appears once.

```python
def one_value():
    return 5   # regular function — runs completely, returns once

def one_yield():
    yield 5   # generator function — returns a generator; body runs only when iterated

print(one_value())     # 5
print(one_yield())      # <generator object ...>
print(next(one_yield()))  # 5
```

A generator can `yield` multiple times, producing a sequence of values across repeated calls to `next()`:

```python
def sequence():
    yield "first"
    yield "second"
    yield "third"

for value in sequence():
    print(value)
# first
# second
# third
```

A generator can still use `return` to stop early — but unlike a normal function, `return` inside a generator doesn't send back a value to the caller through `next()`; it simply ends the generator (raising `StopIteration`).

```python
def limited():
    yield 1
    yield 2
    return   # stops the generator here
    yield 3    # never reached

list(limited())   # [1, 2]
```

---

## 8. send(), throw(), and close()

Generators support a richer interaction model than plain iterators — values can flow back **into** a paused generator, not just out of it.

### `send()` — pass a value into the generator

```python
def echo():
    while True:
        received = yield
        print(f"Received: {received}")

gen = echo()
next(gen)          # "prime" the generator — advances to the first yield
gen.send("hello")   # Received: hello
gen.send("world")    # Received: world
```

`yield` here acts as an expression: the generator pauses at `yield`, and whatever is passed via `.send()` becomes the value that expression evaluates to when execution resumes.

### `throw()` — raise an exception inside the generator

```python
gen = echo()
next(gen)
gen.throw(ValueError, "something broke")   # raises ValueError inside the generator, at the yield point
```

### `close()` — stop the generator early

```python
gen = echo()
next(gen)
gen.close()   # raises GeneratorExit inside the generator, cleanly stopping it
```

These advanced features are the foundation `asyncio` and coroutine-based concurrency were historically built on, though modern async code typically uses `async`/`await` syntax instead of raw generators for that purpose.

---

## 9. itertools — The Standard Library's Iterator Toolkit

`itertools` provides efficient, memory-friendly building blocks for working with iterators, avoiding the need to hand-write common patterns.

```python
from itertools import count, cycle, islice, chain, combinations, permutations, groupby

# count() — infinite counter, like range() without an end
list(islice(count(10, 2), 5))   # [10, 12, 14, 16, 18]

# cycle() — repeats a sequence forever
list(islice(cycle([1, 2, 3]), 7))   # [1, 2, 3, 1, 2, 3, 1]

# chain() — combines multiple iterables into one
list(chain([1, 2], [3, 4]))   # [1, 2, 3, 4]

# combinations() / permutations()
list(combinations([1, 2, 3], 2))   # [(1, 2), (1, 3), (2, 3)]
list(permutations([1, 2], 2))       # [(1, 2), (2, 1)]

# groupby() — groups consecutive equal items
data = [1, 1, 2, 2, 3]
for key, group in groupby(data):
    print(key, list(group))
# 1 [1, 1]
# 2 [2, 2]
# 3 [3]
```

`islice()` in particular is essential for safely working with infinite generators — it lets you take just the first `n` values without ever calling `next()` in a loop yourself.

---

## 10. Generators in Pipelines

A powerful, idiomatic pattern: chain generators together to build lazy, memory-efficient data-processing pipelines, where each stage only pulls what the next stage actually needs.

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

def filter_errors(lines):
    for line in lines:
        if "ERROR" in line:
            yield line

def extract_messages(lines):
    for line in lines:
        yield line.split("ERROR:")[-1].strip()

lines = read_lines("app.log")
errors = filter_errors(lines)
messages = extract_messages(errors)

for message in messages:
    print(message)
```

Nothing is actually read or processed until the final `for` loop starts pulling values — and even then, only one line moves through the entire pipeline at a time, regardless of how large the file is. This composability is one of the most practical, high-leverage uses of generators in real backend and data-processing code.

---

## Key Points

- An iterable implements `__iter__()` and can produce a new iterator each time; an iterator implements `__next__()` and gets exhausted after one pass
- `for` loops are sugar over calling `iter()` once and `next()` repeatedly until `StopIteration`
- Custom iterators are built by implementing `__iter__`/`__next__` on a class — generators achieve the same thing with far less code
- A function containing `yield` becomes a generator function; calling it returns a paused, resumable generator object
- Generators are lazy — values are computed one at a time, on demand, which is critical for memory efficiency with large or infinite data
- Generator expressions `(x for x in ...)` are a compact alternative to generator functions for simple, single-use cases
- Generators can represent infinite sequences safely, as long as the consumer controls how many values are pulled (e.g. via `itertools.islice`)
- `return` inside a generator ends it (raises `StopIteration`) rather than sending back a value through `next()`
- `send()`, `throw()`, and `close()` allow richer two-way interaction with a running generator
- `itertools` provides efficient, ready-made iterator utilities (`count`, `cycle`, `chain`, `groupby`, etc.) instead of reinventing them
- Chaining generators together builds lazy, composable data pipelines that process one item at a time through every stage