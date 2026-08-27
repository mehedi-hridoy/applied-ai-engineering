# Python Basics: Collections

## Lists

An ordered, **mutable** collection of items, defined with square brackets.

```python
fruits = ["apple", "banana", "mango"]
mixed = [1, "two", 3.0, True]
```

- Items keep their insertion order
- Duplicate values are allowed
- Items can be added, removed, or changed after creation

```python
fruits.append("grape")
fruits.remove("banana")
fruits[0] = "orange"
```

---

## Tuples

An ordered, **immutable** collection of items, defined with parentheses.

```python
point = (10, 20)
person = ("Mehedi", 25, "Dhaka")
```

- Once created, items cannot be added, removed, or changed
- Faster and more memory-efficient than lists
- Commonly used for fixed collections of values, like coordinates or database rows

```python
point[0]     # 10
point[0] = 5   # raises TypeError
```

A single-item tuple needs a trailing comma:

```python
single = (5,)   # tuple
not_tuple = (5)  # just an int
```

---

## Sets

An unordered collection of **unique** items, defined with curly braces or `set()`.

```python
numbers = {1, 2, 3, 3, 2}
print(numbers)   # {1, 2, 3} — duplicates removed
```

- No duplicate values
- No guaranteed order
- Not indexable — you can't do `numbers[0]`

Common operations:

```python
a = {1, 2, 3}
b = {2, 3, 4}

a | b   # union → {1, 2, 3, 4}
a & b   # intersection → {2, 3}
a - b   # difference → {1}
```

An empty set must be created with `set()`, not `{}` (which creates an empty dict):

```python
empty_set = set()
```

---

## Dictionaries

An unordered collection of **key-value pairs**, defined with curly braces.

```python
person = {
    "name": "Mehedi",
    "age": 25,
    "city": "Dhaka"
}
```

- Keys must be unique and immutable (strings, numbers, tuples)
- Values can be of any type, including other dicts or lists
- Since Python 3.7, dicts preserve insertion order

```python
person["name"]          # 'Mehedi'
person["email"] = "m@example.com"   # add a new key
person["age"] = 26                  # update a value
del person["city"]                  # remove a key
```

---

## Indexing

Accessing an item by its position (lists, tuples) or by its key (dicts).

```python
fruits = ["apple", "banana", "mango"]
fruits[0]     # 'apple'
fruits[-1]    # 'mango'

person = {"name": "Mehedi"}
person["name"]   # 'Mehedi'
```

- Lists and tuples: 0-based positional indexing, negative indices count from the end
- Sets don't support indexing — they have no fixed order
- Dicts: accessed by key, not position

---

## Slicing

Extracting a portion of a list or tuple using `start:stop:step`. Works the same way as string slicing.

```python
numbers = [0, 1, 2, 3, 4, 5]

numbers[1:4]     # [1, 2, 3]
numbers[:3]      # [0, 1, 2]
numbers[3:]      # [3, 4, 5]
numbers[::2]     # [0, 2, 4]
numbers[::-1]    # [5, 4, 3, 2, 1, 0]
```

- `start` is included, `stop` is excluded
- Slicing a list returns a new list — the original is unchanged
- Sets and dicts don't support slicing

---

## Mutability

Whether a collection can be changed after creation.

| Type       | Mutable? |
|------------|----------|
| `list`     | Yes      |
| `tuple`    | No       |
| `set`      | Yes      |
| `dict`     | Yes      |

```python
my_list = [1, 2, 3]
my_list[0] = 99      # allowed

my_tuple = (1, 2, 3)
my_tuple[0] = 99      # raises TypeError
```

Since tuples are immutable, they can be used as dictionary keys; lists cannot.

```python
locations = {(23.8, 90.4): "Dhaka"}   # valid — tuple key
```

---

## Nested Collections

Collections can contain other collections as items or values.

```python
matrix = [[1, 2], [3, 4], [5, 6]]
matrix[1][0]   # 3

people = [
    {"name": "Mehedi", "age": 25},
    {"name": "Rafi", "age": 30}
]
people[0]["name"]   # 'Mehedi'

nested_dict = {
    "user": {
        "name": "Mehedi",
        "roles": ["admin", "editor"]
    }
}
nested_dict["user"]["roles"][0]   # 'admin'
```

Access nested items by chaining index/key lookups from outer to inner.

---

## Common Methods

Frequently used methods per collection type:

**List**
```python
fruits.append("kiwi")     # add to end
fruits.insert(1, "fig")   # insert at index
fruits.pop()               # remove & return last item
fruits.sort()               # sort in place
fruits.reverse()            # reverse in place
len(fruits)                 # number of items
```

**Tuple**
```python
point.count(10)   # count occurrences
point.index(20)   # find index of a value
```

**Set**
```python
numbers.add(4)         # add an item
numbers.discard(2)     # remove if present (no error if missing)
numbers.remove(2)      # remove (raises error if missing)
```

**Dict**
```python
person.keys()             # all keys
person.values()           # all values
person.items()            # key-value pairs
person.get("email", "N/A")  # safe lookup with default
person.update({"age": 26})  # merge/update values
```

---

## Iterating Collections

Looping through a collection's items.

```python
fruits = ["apple", "banana"]
for fruit in fruits:
    print(fruit)

numbers = {1, 2, 3}
for num in numbers:
    print(num)

person = {"name": "Mehedi", "age": 25}
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(key, value)
```

- Iterating a dict directly loops over its keys
- `.items()` gives both key and value together — the most common pattern
- Sets iterate in no guaranteed order

---

## Membership Testing

Checking whether a value exists in a collection, using `in` / `not in`.

```python
fruits = ["apple", "banana"]
"apple" in fruits        # True

numbers = {1, 2, 3}
5 in numbers              # False

person = {"name": "Mehedi"}
"name" in person           # True — checks keys by default
"Mehedi" in person.values()  # True — checks values explicitly
```

Membership testing on a `set` is significantly faster than on a `list`, since sets use hashing internally.

---

## Choosing the Right Data Structure

| Need                                   | Use          |
|------------------------------------------|--------------|
| Ordered, changeable collection            | `list`       |
| Ordered, fixed collection                 | `tuple`      |
| Unique items, no order needed             | `set`        |
| Fast lookup by key                        | `dict`       |
| Fast membership testing                   | `set`        |
| Data that shouldn't change (safety)       | `tuple`      |
| Key-value structured data (records, config) | `dict`     |

```python
# ordered, changing list of tasks
tasks = ["write code", "test", "deploy"]

# fixed coordinate, never changes
origin = (0, 0)

# unique tags, order doesn't matter
tags = {"python", "backend", "api"}

# structured record
user = {"name": "Mehedi", "role": "developer"}
```

---

## Key Points

- `list` — ordered, mutable, allows duplicates
- `tuple` — ordered, immutable, allows duplicates
- `set` — unordered, mutable, unique items only
- `dict` — unordered (insertion-preserving), mutable, key-value pairs
- Indexing works by position for lists/tuples, by key for dicts; sets aren't indexable
- Slicing works on lists and tuples, not on sets or dicts
- Mutability determines whether a type can be changed in place, and whether it can be used as a dict key
- Collections can be nested inside each other and accessed by chaining lookups
- `in` / `not in` test membership; it's fastest on sets
- Pick the structure based on what you need: order, uniqueness, fast lookup, or fixed data