# Python Performance Optimization & Profiling

Fast code starts with knowing *where* time is actually being spent — not guessing. This document covers how to measure performance correctly (profiling, benchmarking), the most impactful optimization techniques in Python, and the discipline of optimizing based on evidence rather than intuition.

---

## 1. The Golden Rule: Measure First

The single most important principle in this entire topic: **don't optimize based on assumptions.** Human intuition about "slow code" is frequently wrong — the actual bottleneck is often in a place nobody expected.

> "Premature optimization is the root of all evil" — Donald Knuth (often paraphrased, but the underlying point holds: optimizing code before you know where the real bottleneck is wastes effort and often makes the code harder to read for no real benefit).

The correct workflow:

```text
1. Write clear, correct code first
2. Profile it to find the ACTUAL bottleneck
3. Optimize only that specific bottleneck
4. Re-measure to confirm the optimization actually helped
```

Skipping step 2 is the most common mistake — engineers frequently spend hours optimizing code that accounts for 1% of total runtime, while the real 90% bottleneck sits untouched elsewhere.

---

## 2. `timeit` — Measuring Small Code Snippets

Best for comparing small, isolated pieces of code — handles the tricky parts of benchmarking automatically (running multiple times, avoiding one-off timing noise).

```python
import timeit

# as a string
time_taken = timeit.timeit("sum(range(100))", number=100000)
print(time_taken)
```

### Comparing two approaches

```python
import timeit

list_comp_time = timeit.timeit(
    "[x**2 for x in range(1000)]",
    number=10000
)

map_time = timeit.timeit(
    "list(map(lambda x: x**2, range(1000)))",
    number=10000
)

print(f"List comprehension: {list_comp_time:.4f}s")
print(f"map(): {map_time:.4f}s")
```

### From the command line

```bash
python -m timeit "sum(range(100))"
python -m timeit -s "data = list(range(1000))" "sorted(data)"
```

`-s` runs setup code once, outside the timed loop — essential when you want to benchmark an operation on prepared data, without including the setup cost in the measurement.

### In Jupyter/IPython

```python
%timeit sum(range(100))          # single line
%%timeit
total = 0
for x in range(100):
    total += x
```

`timeit` automatically runs the snippet many times and reports the best/average result, avoiding the trap of trusting a single, noisy measurement (system load, background processes, and caching effects can all skew a one-off timing).

---

## 3. `cProfile` — Profiling Entire Programs

Where `timeit` measures a small snippet, `cProfile` profiles an entire function or program, breaking down exactly how much time was spent in each function call.

```python
import cProfile

def slow_function():
    total = 0
    for i in range(1_000_000):
        total += i ** 2
    return total

cProfile.run("slow_function()")
```

```text
         4 function calls in 0.312 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.312    0.312    0.312    0.312 script.py:3(slow_function)
```

Key columns to know:

- **ncalls** — how many times the function was called
- **tottime** — total time spent *inside* the function itself, excluding calls to other functions
- **cumtime** — cumulative time, *including* time spent in functions it calls
- **percall** — time per call (tottime or cumtime divided by ncalls)

### Profiling a whole script from the command line

```bash
python -m cProfile -s cumulative my_script.py
```

`-s cumulative` sorts the output by cumulative time — usually the most useful sort order for quickly spotting the biggest contributors to total runtime.

### Saving profile data for visual analysis

```python
import cProfile
import pstats

cProfile.run("slow_function()", "profile_output")

stats = pstats.Stats("profile_output")
stats.sort_stats("cumulative")
stats.print_stats(10)   # top 10 functions by cumulative time
```

Tools like `snakeviz` (a separate package: `pip install snakeviz`) can turn this saved profile data into an interactive visual chart, which is often much faster to interpret than reading raw text output for a complex program.

---

## 4. Reading Profiler Output — Finding the Real Bottleneck

The goal of profiling is to find where the **cumulative time is concentrated**, not to obsess over every function.

```text
   ncalls  tottime  cumtime  filename:lineno(function)
    10000    0.050    2.800   app.py:12(process_order)
    10000    2.700    2.750   app.py:25(validate_address)  <- HERE — clear bottleneck
    10000    0.030    0.030   app.py:40(calculate_tax)
```

Here, `validate_address` accounts for nearly all the time (`tottime` of 2.7 out of a 2.8 total) — that's where optimization effort should go, even if intuition initially pointed elsewhere (e.g. assuming `calculate_tax`, doing "more math," was the slow part).

A useful heuristic (related to the **80/20 rule**): in most real programs, a small fraction of the code accounts for the vast majority of runtime. Profiling exists specifically to identify that fraction reliably.

---

## 5. Common, High-Impact Optimizations

### Choose the right data structure (revisit the DSA doc)

The single biggest performance win in most real code isn't clever tricks — it's picking a data structure with the right time complexity for the operation being performed.

```python
# O(n) membership check — slow for large lists, repeated checks
items = list(range(100_000))
if 99_999 in items:   # scans the whole list in the worst case
    ...

# O(1) average membership check — dramatically faster at scale
items = set(range(100_000))
if 99_999 in items:
    ...
```

### Avoid unnecessary work inside loops

```python
# recomputes len(data) every single iteration
for i in range(len(data)):
    ...

# computed once
n = len(data)
for i in range(n):
    ...
```

```python
# repeated attribute/dict lookups inside a hot loop
for item in items:
    results.append(processor.transform(item))   # 'processor.transform' looked up every iteration

# cache the lookup outside the loop
transform = processor.transform
for item in items:
    results.append(transform(item))
```

### Prefer built-in functions and comprehensions over manual loops

Built-ins like `sum()`, `min()`, `max()`, `sorted()`, and comprehensions are implemented in C internally and are typically faster than an equivalent hand-written Python loop.

```python
# slower — pure Python loop
total = 0
for x in numbers:
    total += x

# faster — built-in, implemented in C
total = sum(numbers)
```

### String concatenation

```python
# slow — creates a new string object on every += (strings are immutable)
result = ""
for word in words:
    result += word + " "

# fast — builds the list, joins once at the end
result = " ".join(words)
```

Each `+=` on a string in a loop creates an entirely new string object, copying everything so far — for large loops, this turns an O(n) operation into effectively O(n²). `str.join()` avoids this by building the final string in one pass.

### Memoization / caching (revisit the Functional Programming doc)

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

For pure functions called repeatedly with the same arguments (recursive algorithms, expensive lookups), caching turns redundant recomputation into a simple dictionary lookup.

### Use generators for large data instead of building full lists (revisit the Iterators doc)

```python
# loads everything into memory at once
def get_squares(n):
    return [x ** 2 for x in range(n)]

# processes lazily, one value at a time
def get_squares(n):
    return (x ** 2 for x in range(n))
```

Memory pressure itself can be a performance problem — excessive memory use leads to more garbage collection overhead and, in extreme cases, swapping to disk.

---

## 6. Time Complexity — The Foundation Beneath All of This

No amount of micro-optimization fixes a fundamentally wrong algorithm. This was covered in depth in the DSA doc — worth restating here as the highest-leverage form of "optimization":

```python
# O(n^2) — nested loop checking for duplicates
def has_duplicates(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False

# O(n) — using a set for membership tracking
def has_duplicates(items):
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
```

For large inputs, the algorithmic improvement (O(n²) → O(n)) dwarfs any micro-optimization you could apply to the slower version — this is almost always where the biggest wins live, and profiling is what reveals when this is the actual issue.

---

## 7. Memory Profiling

Profiling isn't only about CPU time — memory usage matters too, especially for data-heavy programs.

```python
# pip install memory-profiler
from memory_profiler import profile

@profile
def process_data():
    data = [i for i in range(1_000_000)]
    return sum(data)

process_data()
```

```text
Line #    Mem usage    Increment  Line Contents
     3     40.0 MiB     40.0 MiB  @profile
     4                            def process_data():
     5     78.5 MiB     38.5 MiB      data = [i for i in range(1_000_000)]
     6     78.5 MiB      0.0 MiB      return sum(data)
```

This shows exactly which line is responsible for the memory jump — useful for tracking down unexpectedly large allocations, or confirming that a generator-based rewrite actually reduced memory usage as intended.

---

## 8. When Python Itself Is the Bottleneck

Sometimes profiling reveals that pure Python simply can't go faster without changing tools — this is a legitimate, common conclusion, not a failure of optimization effort.

### NumPy for numerical work

Pure Python loops over large numeric arrays are much slower than vectorized operations, since NumPy pushes the actual computation down into optimized C code.

```python
import numpy as np

# slow — pure Python loop
result = [x ** 2 for x in range(1_000_000)]

# fast — vectorized, runs in optimized C under the hood
arr = np.arange(1_000_000)
result = arr ** 2
```

### Multiprocessing for CPU-bound parallel work

Covered in depth in the Concurrency doc — when a computation is CPU-bound and profiling confirms Python's per-operation overhead itself is the limit, distributing the work across processes (using multiple cores) can help, where a single-threaded optimization can't.

### PyPy — an alternative Python interpreter

An alternative implementation of Python (instead of the standard CPython) that uses Just-In-Time (JIT) compilation, often providing significant speedups for long-running, computation-heavy pure-Python code — with no source code changes required in many cases. Worth knowing exists, though not always a drop-in option (some C-extension libraries have limited or no PyPy compatibility).

### Cython — compiling Python-like code to C

Lets performance-critical sections be written in a Python-like syntax that compiles down to actual C, callable from regular Python code. Used when a very specific, well-identified hot path (found via profiling) needs to be dramatically faster than even well-optimized pure Python can achieve.

**The common thread:** all of these are reached for *after* profiling has clearly identified that pure Python is the actual constraint — not as a first resort.

---

## 9. Benchmarking Pitfalls to Avoid

- **Timing on too small a sample** — a single run can be dominated by system noise (background processes, disk caching); always run multiple iterations (which `timeit` does automatically)
- **Forgetting warm-up effects** — the first call to a function can be slower due to import overhead, caching, or JIT warm-up (if using PyPy); later calls may be meaningfully faster
- **Optimizing on the wrong machine/data** — code that's fast on a small test dataset may behave completely differently at production scale; benchmark with realistic data sizes when possible
- **Micro-benchmarking in isolation, ignoring real-world context** — a technique that wins by milliseconds in an isolated benchmark may make no measurable difference in the full application if it isn't part of the actual bottleneck the profiler identified

---

## 10. A Practical Optimization Workflow

```text
1. Write correct, readable code first — don't guess-optimize upfront
2. If performance actually matters for this code path, profile it (cProfile)
3. Identify the function/line actually consuming the most time (or memory)
4. Ask: is this an algorithmic problem (wrong data structure/complexity)?
   -> If yes, fix the algorithm first — usually the biggest win
5. If the algorithm is already good, apply targeted optimizations:
   built-ins, caching, avoiding redundant work, generators for memory
6. Re-measure to confirm the change actually helped
7. If pure Python is fundamentally the limit, consider NumPy,
   multiprocessing, PyPy, or Cython — depending on the specific bottleneck
8. Don't optimize further once performance is acceptable for the
   actual requirement — more speed isn't free; it often costs readability
```

Step 8 is easy to overlook: optimization has a real cost in code complexity and maintainability. The goal is code that's fast *enough* for its actual requirements, found and verified through measurement — not code that's maximally fast at the expense of everything else.

---

## Key Points

- Always measure before optimizing — intuition about what's "slow" is frequently wrong, and profiling reveals the real bottleneck
- `timeit` is for comparing small code snippets reliably; `cProfile` is for finding where time goes across an entire program or function
- In profiler output, focus on cumulative time to find where effort is actually concentrated, not every function indiscriminately
- Choosing the right data structure (e.g. `set` over `list` for membership checks) is usually the single biggest performance lever available
- Built-in functions, comprehensions, and `str.join()` are typically faster than hand-written loops or repeated string concatenation
- `functools.lru_cache` eliminates redundant recomputation for pure functions called repeatedly with the same arguments
- Generators reduce memory pressure for large datasets, which is itself a performance factor via reduced GC overhead
- No micro-optimization beats fixing a bad algorithmic complexity — this is almost always the highest-leverage fix when it applies
- Memory profiling (`memory_profiler`) surfaces unexpected allocations the same way `cProfile` surfaces unexpected CPU time
- When pure Python itself is the bottleneck (confirmed via profiling), NumPy, multiprocessing, PyPy, or Cython are legitimate next steps — reached for after profiling, not before
- Avoid common benchmarking pitfalls: too-small samples, warm-up effects, unrealistic test data, and optimizing code that isn't actually the bottleneck