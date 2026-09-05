# Python Memory Management & Internals

This document covers what's actually happening beneath Python's syntax — how variables really work, how memory is allocated and reclaimed, and internals like reference counting, garbage collection, and the GIL. This is the kind of knowledge that separates someone who writes working Python from someone who can debug memory leaks, reason about performance, and understand *why* certain code behaves the way it does.

---

## 1. Everything Is an Object

In Python, every value — numbers, strings, functions, classes, modules — is an object living somewhere in memory. A **variable is not a box that holds a value**; it's a **name bound to an object**.

```python
x = 300
print(id(x))   # a memory address (as an integer) — the object's identity
print(type(x))   # <class 'int'>
```

`id()` returns a unique identifier for an object (in CPython, this is literally its memory address) for as long as it exists. `type()` returns the object's class.

### Assignment binds a name, it doesn't copy data

```python
a = [1, 2, 3]
b = a          # b is bound to the SAME object as a, not a copy

b.append(4)
print(a)         # [1, 2, 3, 4] — a is affected too, since they're the same object
print(a is b)      # True — same identity
```

This is fundamentally different from languages where assignment copies a value into a variable's storage slot. Understanding "names point to objects" instead of "variables contain values" resolves a huge share of confusing Python behavior.

---

## 2. `is` vs `==`

This distinction, touched on in the Operators doc, matters much more once you understand object identity.

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b   # True  — same VALUE
a is b   # False — different OBJECTS in memory
a is c   # True  — same OBJECT
```

- `==` calls `__eq__` and compares **value equality**
- `is` compares **object identity** — whether both names point to the exact same object in memory

`is` should be reserved for identity checks that are meant to be about identity — most importantly, comparisons with singletons: `None`, `True`, `False`.

```python
if value is None:      # correct — None is a true singleton
    ...

if value == None:       # works, but not idiomatic — triggers __eq__ unnecessarily
    ...
```

---

## 3. Mutable vs Immutable, Revisited

This was covered functionally in earlier docs — here's what's actually happening in memory.

```python
x = 5
y = x
y += 1

print(x)   # 5 — unchanged
print(y)    # 6
```

`y += 1` doesn't modify the object `5` in place — integers are immutable, so this creates a **new** integer object `6` and rebinds `y` to it. `x` still points to the original `5` object.

```python
a = [1, 2, 3]
b = a
b.append(4)

print(a)   # [1, 2, 3, 4] — DOES change, since lists are mutable
```

`b.append(4)` modifies the actual list object in place — and since `a` and `b` point to the same object, both "see" the change. No new object was created here.

This is the real mechanism behind the classic mutable-default-argument bug:

```python
def add_item(item, items=[]):   # the default list is ONE object, created once, at function definition time
    items.append(item)
    return items

add_item(1)   # [1]
add_item(2)    # [1, 2] — the SAME list object from before, not a fresh one
```

The default value is created exactly once, when the function is defined — every call that doesn't supply `items` explicitly shares that same mutable object.

---

## 4. Reference Counting

CPython's primary memory management mechanism. Every object keeps an internal count of how many references point to it. When that count hits zero, the object is immediately deallocated.

```python
import sys

x = [1, 2, 3]
print(sys.getrefcount(x))   # includes the temporary reference getrefcount() itself creates, so it's usually +1 higher than expected
```

```python
a = [1, 2, 3]   # refcount = 1
b = a             # refcount = 2 (both a and b reference the same object)
del a               # refcount = 1
del b                 # refcount = 0 -> object is deallocated immediately
```

This is why Python's memory management feels "automatic" and largely immediate — most objects are freed the instant their last reference disappears, without waiting for a garbage collection cycle.

```python
def create_list():
    temp = [1, 2, 3]   # refcount = 1
    return temp           # refcount stays 1, ownership transfers to the caller
    # if temp weren't returned, its refcount would drop to 0 here and it'd be freed
```

---

## 5. Reference Cycles and the Garbage Collector

Reference counting alone can't handle one specific case: objects that reference each other, forming a cycle, with no external references pointing in. Their refcounts never naturally reach zero, even though nothing outside the cycle can reach them.

```python
class Node:
    def __init__(self):
        self.other = None

a = Node()
b = Node()
a.other = b   # a references b
b.other = a    # b references a — a cycle

del a
del b
# a and b still reference EACH OTHER — refcount never hits 0 through reference counting alone
```

This is where Python's **cyclic garbage collector** (the `gc` module) comes in — it periodically scans for groups of objects that reference each other but are unreachable from anywhere else in the program, and reclaims them.

```python
import gc

gc.collect()   # manually trigger a collection cycle (rarely needed — runs automatically)
```

### Generational garbage collection

CPython's cyclic GC uses a **generational** strategy, based on the empirical observation that most objects die young.

- **Generation 0** — newly created objects; collected most frequently
- **Generation 1** — objects that survived at least one Gen 0 collection; collected less often
- **Generation 2** — long-lived objects that survived multiple collections; collected least often

```python
import gc
print(gc.get_threshold())   # e.g. (700, 10, 10) — collection thresholds per generation
```

Objects are promoted to older generations after surviving collections, and older generations are scanned less frequently, since long-lived objects are statistically less likely to become unreachable soon. This tiered approach keeps garbage collection overhead low in the common case.

---

## 6. `__del__` and Cleanup

`__del__` is called just before an object is destroyed — but relying on it for critical cleanup (closing files, releasing locks) is discouraged, since its exact timing isn't guaranteed, especially with reference cycles.

```python
class Resource:
    def __del__(self):
        print("Resource cleaned up")

r = Resource()
del r   # "Resource cleaned up" — usually prints immediately (refcount hits 0)
```

With cyclic references, `__del__` may be delayed until the next garbage collection cycle runs, or in rare/older cases might not run predictably at all. **The reliable pattern for deterministic cleanup is a context manager (`with`, `__enter__`/`__exit__`)**, not `__del__` — this was covered in the OOP Advanced and Exception Handling docs, and this is exactly why it's the recommended approach: cleanup runs deterministically, at a known point, rather than whenever the garbage collector happens to get around to it.

---

## 7. Small Integer Caching and String Interning

CPython applies specific optimizations for very common, small, immutable values — worth knowing about mainly so surprising `is` behavior doesn't cause confusion.

### Small integer caching

CPython pre-creates and reuses integer objects in the range **-5 to 256** — every reference to, say, `100`, in this range points to the exact same cached object.

```python
a = 100
b = 100
print(a is b)   # True — both point to the same cached object

x = 1000
y = 1000
print(x is y)     # False (usually) — outside the cached range, separate objects
```

### String interning

Certain strings (especially short ones that look like identifiers) are automatically "interned" — reused rather than recreated.

```python
a = "hello"
b = "hello"
print(a is b)   # True — often interned automatically

c = "hello world!"
d = "hello world!"
print(c is d)     # not guaranteed — may or may not be interned, depending on the string
```

**The practical takeaway:** this caching behavior is a CPython implementation detail, not a language guarantee — never rely on `is` to compare values, even when it happens to "work" for small numbers or short strings. Always use `==` for value comparison; reserve `is` strictly for identity checks like `is None`.

---

## 8. `sys.getsizeof()` — Measuring Memory Usage

Reports the memory footprint of an object, in bytes (note: for containers, this often doesn't include the size of the objects they *contain* — just the container's own overhead).

```python
import sys

sys.getsizeof(5)              # size of an int object
sys.getsizeof("hello")          # size of a str object
sys.getsizeof([1, 2, 3])          # size of the list itself (not the ints inside it)
sys.getsizeof([])                  # a list has overhead even when empty
```

```python
a = []
b = [0] * 1000

print(sys.getsizeof(a))   # small
print(sys.getsizeof(b))     # noticeably larger — the list has pre-allocated space for 1000 items
```

This ties directly back to why `__slots__` (covered in OOP Advanced) matters at scale — instances without `__slots__` carry a `__dict__`, which adds meaningful per-object overhead when creating large numbers of small objects.

---

## 9. Shallow Copy vs Deep Copy

Since assignment doesn't copy objects, explicit copying needs its own mechanism — and even that has two levels.

```python
import copy

original = [[1, 2], [3, 4]]

shallow = copy.copy(original)     # or original.copy(), or original[:]
deep = copy.deepcopy(original)
```

**Shallow copy** — creates a new outer container, but the *elements inside* are still the same shared objects as the original.

```python
shallow = copy.copy(original)
shallow.append([5, 6])         # only affects `shallow` — new top-level item
shallow[0].append(99)             # affects BOTH — original[0] is the SAME inner list object

print(original)   # [[1, 2, 99], [3, 4]] — inner list was shared and mutated
```

**Deep copy** — recursively copies every nested object, producing a fully independent structure.

```python
deep = copy.deepcopy(original)
deep[0].append(99)
print(original)   # unaffected — deep copy has entirely separate nested objects
```

For flat structures (a list of numbers/strings), shallow copy and deep copy behave identically — the distinction only matters once containers are nested.

---

## 10. Weak References

A normal reference keeps an object alive (its refcount stays above zero). A **weak reference** (`weakref` module) refers to an object *without* increasing its reference count — letting the object be garbage collected normally, even while the weak reference still exists.

```python
import weakref

class Data:
    pass

obj = Data()
weak = weakref.ref(obj)

print(weak())     # <Data object> — still alive, accessible through the weak reference
del obj
print(weak())        # None — the object was collected; the weak reference doesn't keep it alive
```

Use cases:

- **Caches** — you want to cache objects, but not prevent them from ever being freed just because they're in the cache
- **Avoiding reference cycles** — e.g. a parent-child relationship where the child holds a weak reference back to its parent, preventing a cycle that would otherwise need the cyclic GC to clean up

```python
class Parent:
    def __init__(self):
        self.children = []

class Child:
    def __init__(self, parent):
        self.parent = weakref.ref(parent)   # weak reference — doesn't keep parent alive artificially
```

`weakref.WeakValueDictionary` and `weakref.WeakKeyDictionary` extend this idea to whole dictionaries whose entries disappear automatically once the referenced object is no longer used elsewhere.

---

## 11. The Global Interpreter Lock (GIL)

The **GIL** is a mutex in CPython that ensures only one thread executes Python bytecode at any given moment, even on a multi-core machine. This is one of the most frequently discussed (and misunderstood) aspects of Python internals.

```python
import threading

def count():
    total = 0
    for _ in range(10_000_000):
        total += 1

# even with multiple threads, only one runs Python bytecode at a time due to the GIL
t1 = threading.Thread(target=count)
t2 = threading.Thread(target=count)
t1.start(); t2.start()
t1.join(); t2.join()
```

### Why the GIL exists

CPython's memory management (reference counting, specifically) isn't thread-safe by default — without the GIL, two threads simultaneously modifying an object's refcount could corrupt it. The GIL sidesteps this by only ever letting one thread run Python code at a time, simplifying memory management significantly.

### Practical implications

- **CPU-bound multi-threading doesn't parallelize** in standard CPython — threads competing for CPU-heavy Python code won't run faster with more threads, since only one runs at a time
- **I/O-bound multi-threading still works well** — the GIL is released during blocking I/O operations (network calls, file reads, `time.sleep()`), so threads waiting on I/O genuinely overlap
- **True CPU parallelism** requires either the `multiprocessing` module (separate processes, each with its own GIL and memory space) or C extensions that explicitly release the GIL (like NumPy's heavy numerical operations)

```python
from multiprocessing import Process

# separate processes — each has its own interpreter and GIL, genuinely parallel on multiple cores
p1 = Process(target=count)
p2 = Process(target=count)
p1.start(); p2.start()
p1.join(); p2.join()
```

Note: newer CPython versions have introduced work toward an optional "free-threaded" build without a GIL (PEP 703), but as of the current mainstream releases, the GIL remains the default and this distinction between CPU-bound and I/O-bound concurrency still applies in standard installs — worth verifying against the latest CPython release notes if this matters for a specific project.

---

## 12. Memory Views

`memoryview` allows accessing an object's underlying memory buffer directly, without copying the data — relevant for large binary data (arrays, images, network buffers) where copying would be wasteful.

```python
data = bytearray(b"hello world")
view = memoryview(data)

print(view[0])          # 104 — the byte value of 'h'
print(bytes(view[0:5]))    # b'hello' — a slice, still without copying the original buffer

view[0] = 72   # modifies the underlying bytearray directly through the view
print(data)      # bytearray(b'Hello world')
```

This is a fairly specialized tool — most application code never needs it directly — but it's foundational to how libraries like NumPy achieve efficient, zero-copy operations on large datasets.

---

## Key Points

- Variables are names bound to objects, not boxes containing values — assignment binds a name, it doesn't copy data
- `is` checks object identity; `==` checks value equality — use `is` only for singleton checks like `None`
- Immutable objects (`int`, `str`, `tuple`) can't change in place — operations that look like mutation actually create new objects; mutable objects (`list`, `dict`) can be changed in place, and shared references see the same change
- CPython primarily manages memory through reference counting — objects are freed the instant their reference count hits zero
- Reference cycles defeat plain reference counting; the generational cyclic garbage collector (`gc` module) periodically detects and reclaims unreachable cycles
- `__del__` timing isn't guaranteed, especially with cycles — context managers (`with`) are the reliable pattern for deterministic cleanup
- CPython caches small integers (-5 to 256) and interns some strings — this is an implementation detail, never rely on `is` for value comparison because of it
- `sys.getsizeof()` measures an object's own memory footprint, not what its contained objects add up to
- Shallow copy duplicates the outer container only; deep copy recursively duplicates all nested objects — the distinction only matters for nested/mutable structures
- Weak references (`weakref`) point to an object without keeping it alive, useful for caches and breaking reference cycles
- The GIL lets only one thread execute Python bytecode at a time in standard CPython — this limits CPU-bound multithreading but not I/O-bound concurrency; true CPU parallelism needs `multiprocessing` or GIL-releasing C extensions