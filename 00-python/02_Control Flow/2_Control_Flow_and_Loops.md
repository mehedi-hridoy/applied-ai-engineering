# Control Flow and Loops

## if

Runs a block of code only if a condition is `True`.

```python
age = 20

if age >= 18:
    print("You are an adult")
```

- The condition must evaluate to a boolean (or something Python can treat as truthy/falsy)
- The indented block runs only when the condition is `True`
- Indentation (not braces) defines the block in Python

---

## elif

Checks an additional condition if the previous `if` (or `elif`) was `False`. Short for "else if".

```python
score = 75

if score >= 90:
    print("Grade A")
elif score >= 75:
    print("Grade B")
elif score >= 50:
    print("Grade C")
```

- Conditions are checked in order, top to bottom
- Only the first matching block runs; the rest are skipped
- There can be any number of `elif` blocks

---

## else

Runs when none of the preceding `if` / `elif` conditions were `True`.

```python
age = 15

if age >= 18:
    print("Adult")
else:
    print("Minor")
```

`else` is optional and always comes last, with no condition of its own.

---

## Nested Conditions

An `if` statement placed inside another `if` (or `elif`/`else`) block.

```python
age = 25
has_id = True

if age >= 18:
    if has_id:
        print("Entry allowed")
    else:
        print("ID required")
else:
    print("Entry denied")
```

Nested conditions are useful when a decision depends on multiple related checks, though deep nesting can often be simplified using `and` / `or`:

```python
if age >= 18 and has_id:
    print("Entry allowed")
```

---

## for loops

Iterates over a sequence (list, string, tuple, dict, range, etc.), executing the block once per item.

```python
fruits = ["apple", "banana", "mango"]

for fruit in fruits:
    print(fruit)
```

```python
for char in "abc":
    print(char)
```

Each iteration, the loop variable (`fruit`, `char`) takes the next value from the sequence.

---

## while loops

Repeats a block of code as long as a condition remains `True`.

```python
count = 0

while count < 5:
    print(count)
    count += 1
```

- The condition is checked before every iteration
- The loop body must eventually make the condition `False`, or it becomes an infinite loop
- Useful when the number of iterations isn't known in advance

---

## range()

Generates a sequence of numbers, commonly used with `for` loops.

```python
range(5)          # 0, 1, 2, 3, 4
range(2, 6)       # 2, 3, 4, 5
range(0, 10, 2)   # 0, 2, 4, 6, 8
```

```python
for i in range(5):
    print(i)
```

- `range(stop)` — starts at 0, up to (not including) `stop`
- `range(start, stop)` — starts at `start`, up to (not including) `stop`
- `range(start, stop, step)` — increments by `step` each time

`range()` produces values lazily; it doesn't build the full list in memory.

---

## break

Immediately exits the nearest enclosing loop, skipping any remaining iterations.

```python
for num in range(10):
    if num == 5:
        break
    print(num)
# prints 0 1 2 3 4
```

Commonly used to stop a loop early once some condition is met.

---

## continue

Skips the rest of the current iteration and moves to the next one, without exiting the loop.

```python
for num in range(5):
    if num == 2:
        continue
    print(num)
# prints 0 1 3 4
```

Useful for skipping specific cases while letting the loop keep running.

---

## pass

A statement that does nothing. Used as a placeholder where syntax requires a statement but no action is needed yet.

```python
if age >= 18:
    pass   # logic to be added later
```

```python
for item in items:
    pass   # loop body not implemented yet
```

Common during early development, or to define an empty function/class body:

```python
def not_done_yet():
    pass
```

---

## Conditional Expressions

A compact one-line form of `if / else`, often called a "ternary expression".

```python
age = 20
status = "adult" if age >= 18 else "minor"
```

Equivalent to:

```python
if age >= 18:
    status = "adult"
else:
    status = "minor"
```

Useful for simple, short conditions — for anything more complex, a full `if / else` block is clearer.

---

## Key Points

- `if` / `elif` / `else` run different blocks based on which condition is `True`; conditions are checked in order
- Conditions can be nested for multi-part decisions, though `and` / `or` can often flatten them
- `for` loops iterate over a known sequence; `while` loops repeat while a condition holds
- `range()` generates numeric sequences, commonly paired with `for`
- `break` exits a loop entirely; `continue` skips to the next iteration
- `pass` is a no-op placeholder where a statement is syntactically required
- Conditional expressions (`x if condition else y`) provide a one-line `if / else` for simple assignments