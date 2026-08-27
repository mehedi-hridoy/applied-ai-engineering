# Data Structures & Algorithms (Python-focused)

## List Comprehensions

A concise way to build a new list by applying an expression to each item of an iterable, optionally filtering.

```python
squares = [x ** 2 for x in range(5)]
print(squares)   # [0, 1, 4, 9, 16]
```

With a condition:

```python
evens = [x for x in range(10) if x % 2 == 0]
print(evens)   # [0, 2, 4, 6, 8]
```

Equivalent to the longer loop form:

```python
squares = []
for x in range(5):
    squares.append(x ** 2)
```

Comprehensions can also nest:

```python
matrix = [[1, 2], [3, 4]]
flat = [num for row in matrix for num in row]   # [1, 2, 3, 4]
```

---

## Dict Comprehensions

Builds a dictionary using the same comprehension pattern, with a `key: value` expression.

```python
squares = {x: x ** 2 for x in range(5)}
print(squares)   # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

With a condition:

```python
names = ["Mehedi", "Rafi", "Al"]
long_names = {name: len(name) for name in names if len(name) > 2}
```

Also useful for transforming an existing dict:

```python
prices = {"apple": 100, "banana": 50}
discounted = {item: price * 0.9 for item, price in prices.items()}
```

---

## Set Comprehensions

Builds a set using comprehension syntax — same idea, but with curly braces and no colon.

```python
numbers = [1, 2, 2, 3, 3, 4]
unique_squares = {x ** 2 for x in numbers}
print(unique_squares)   # {1, 4, 9, 16}
```

Since sets discard duplicates automatically, this is a convenient way to deduplicate while transforming.

---

## Generator Expressions

Similar to a list comprehension, but produces items lazily, one at a time, instead of building the whole list in memory. Written with parentheses instead of square brackets.

```python
squares = (x ** 2 for x in range(5))
print(squares)        # <generator object ...>
print(next(squares))  # 0
print(next(squares))  # 1
```

```python
total = sum(x ** 2 for x in range(1000000))
```

Generator expressions are more memory-efficient than list comprehensions for large or unbounded sequences, since values are computed on demand rather than all at once.

---

## Sorting (sort() vs sorted())

Two ways to sort a sequence.

### `.sort()`

A **list method** that sorts the list **in place** and returns `None`.

```python
numbers = [3, 1, 4, 1, 5]
numbers.sort()
print(numbers)   # [1, 1, 3, 4, 5]
```

### `sorted()`

A **built-in function** that returns a **new sorted list**, leaving the original unchanged. Works on any iterable, not just lists.

```python
numbers = [3, 1, 4, 1, 5]
result = sorted(numbers)
print(numbers)   # [3, 1, 4, 1, 5] — unchanged
print(result)    # [1, 1, 3, 4, 5]
```

```python
sorted("bca")          # ['a', 'b', 'c']
sorted({3, 1, 2})       # [1, 2, 3]
```

Both accept `reverse=True` for descending order:

```python
sorted(numbers, reverse=True)
```

---

## key Functions & itemgetter

Customizing how items are compared during sorting, using the `key` parameter.

```python
words = ["banana", "kiwi", "apple"]
sorted(words, key=len)   # ['kiwi', 'apple', 'banana'] — sorted by length
```

```python
people = [("Mehedi", 25), ("Rafi", 30), ("Al", 20)]
sorted(people, key=lambda person: person[1])   # sort by age
```

`key` takes a function; it's called once per item, and the results are used for comparison — the original items are returned, just reordered.

### `itemgetter`

From the `operator` module — a faster, more readable alternative to a lambda for extracting an item by index or key.

```python
from operator import itemgetter

people = [("Mehedi", 25), ("Rafi", 30), ("Al", 20)]
sorted(people, key=itemgetter(1))   # sort by age

records = [{"name": "Mehedi", "age": 25}, {"name": "Rafi", "age": 30}]
sorted(records, key=itemgetter("age"))   # sort by dict key
```

---

## Stack Using List

A **stack** follows Last-In-First-Out (LIFO) order. Python lists naturally support stack operations using `.append()` and `.pop()`.

```python
stack = []

stack.append(1)   # push
stack.append(2)
stack.append(3)

stack.pop()   # 3 — removes and returns the last item (LIFO)
print(stack)  # [1, 2]
```

- `.append()` — push an item onto the top
- `.pop()` — remove and return the top item
- `stack[-1]` — peek at the top without removing it

Common use cases: undo functionality, expression evaluation, backtracking (e.g. depth-first search).

---

## Queue Using List / deque

A **queue** follows First-In-First-Out (FIFO) order. Using a plain list works but is inefficient, since removing from the front (`pop(0)`) shifts every remaining element.

```python
queue = []
queue.append(1)   # enqueue
queue.append(2)
queue.append(3)

queue.pop(0)   # 1 — removes from the front (FIFO), but O(n)
```

The efficient approach uses `collections.deque`, which supports fast additions/removals from both ends:

```python
from collections import deque

queue = deque()
queue.append(1)      # enqueue
queue.append(2)
queue.append(3)

queue.popleft()   # 1 — removes from the front, O(1)
print(queue)      # deque([2, 3])
```

`deque` is generally preferred over a list whenever queue-like behavior is needed.

---

## Searching & Hashing Basics

### Linear Search

Checks each item one by one until a match is found. Works on any iterable, O(n) time.

```python
def linear_search(items, target):
    for i, value in enumerate(items):
        if value == target:
            return i
    return -1

linear_search([5, 3, 8, 1], 8)   # 2
```

### Binary Search

Works only on a **sorted** sequence. Repeatedly halves the search range, giving O(log n) time.

```python
def binary_search(items, target):
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

binary_search([1, 3, 5, 8, 9], 8)   # 3
```

### Hashing

Converts a value into a fixed-size number (a hash) used to quickly locate data. Python's `dict` and `set` are built on hash tables internally, which is why membership checks and key lookups run in roughly O(1) time on average.

```python
hash("hello")   # some integer, consistent within a run

my_set = {1, 2, 3}
5 in my_set   # O(1) average, thanks to hashing
```

This is why checking membership with a `set` or `dict` is typically far faster than scanning a `list`.

---

## Time Complexity Basics

**Time complexity** describes how the runtime of an operation grows as the input size (`n`) grows, using Big-O notation.

| Notation      | Name           | Example                              |
|---------------|-----------------|----------------------------------------|
| `O(1)`         | Constant        | Dict/set lookup, list index access    |
| `O(log n)`     | Logarithmic     | Binary search                         |
| `O(n)`         | Linear          | Linear search, iterating a list       |
| `O(n log n)`   | Linearithmic    | Efficient sorting (`sort`, `sorted`)  |
| `O(n²)`        | Quadratic       | Nested loops over the same list       |

```python
# O(n) — one pass
for item in items:
    print(item)

# O(n^2) — nested loop over the same data
for a in items:
    for b in items:
        print(a, b)

# O(1) — direct lookup
value = my_dict["key"]
```

Common Python operation costs worth knowing:

| Operation                  | List        | Dict / Set   |
|------------------------------|-------------|--------------|
| Access by index/key          | O(1)         | O(1) avg      |
| Search / membership (`in`)   | O(n)         | O(1) avg      |
| Insert at end                | O(1) amortized | O(1) avg   |
| Insert at front               | O(n)         | O(1) avg      |

Understanding time complexity helps in choosing the right data structure — e.g. preferring a `set` over a `list` when membership checks happen frequently.

---

## Key Points

- List/dict/set comprehensions build collections in one concise expression; generator expressions do the same lazily, saving memory
- `.sort()` sorts a list in place and returns `None`; `sorted()` returns a new sorted list from any iterable
- The `key` parameter customizes sort order; `itemgetter` is a clean alternative to lambdas for extracting fields
- A list can implement a stack efficiently (`append`/`pop`), but `collections.deque` is needed for an efficient queue (`append`/`popleft`)
- Linear search works on any sequence in O(n); binary search needs sorted data but runs in O(log n)
- Dicts and sets use hashing internally, giving average O(1) lookups — much faster than scanning a list
- Big-O notation describes how runtime scales with input size; it guides which data structure or algorithm fits a given problem