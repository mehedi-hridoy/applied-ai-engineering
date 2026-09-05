# Python File Handling & I/O

Almost every real program reads or writes data outside itself — files, logs, config, exported reports. This document covers how Python handles files and I/O correctly and efficiently: opening, reading, writing, paths, encodings, and the standard tools for structured formats like JSON and CSV.

---

## 1. Opening and Closing Files

The built-in `open()` function returns a **file object**, which you read from or write to.

```python
file = open("data.txt", "r")   # open for reading
content = file.read()
file.close()                     # must be closed manually
```

Manually closing files is error-prone — if an exception happens before `file.close()`, the file stays open. **This is why `with` is the standard, correct approach in real code:**

```python
with open("data.txt", "r") as file:
    content = file.read()
# file is automatically closed here, even if an exception occurred inside the block
```

The `with` statement relies on the file object's context manager protocol (`__enter__`/`__exit__`, covered in the OOP Advanced and Exception Handling docs) — this guarantees cleanup, which is why virtually all Python file code should use it instead of manual `open()`/`close()`.

---

## 2. File Modes

The second argument to `open()` controls how the file is accessed.

| Mode  | Meaning                                             |
|-------|--------------------------------------------------------|
| `"r"`  | Read (default) — file must already exist                 |
| `"w"`  | Write — creates the file if missing, **overwrites** if it exists |
| `"a"`  | Append — creates the file if missing, adds to the end     |
| `"x"`  | Exclusive creation — fails if the file already exists       |
| `"r+"` | Read and write — file must exist                             |
| `"b"`  | Binary mode (combined with another mode, e.g. `"rb"`, `"wb"`) |
| `"t"`  | Text mode (default, combined with another mode, e.g. `"rt"`)  |

```python
with open("log.txt", "a") as f:
    f.write("New log entry\n")   # appended, not overwritten
```

```python
with open("new_file.txt", "x") as f:   # fails with FileExistsError if it already exists
    f.write("First write")
```

**Common mistake:** opening in `"w"` mode truncates (empties) the file immediately upon opening, even before any `write()` call — this happens whether or not you actually write anything.

```python
with open("important.txt", "w") as f:
    pass   # the file is now empty, even though nothing was written
```

---

## 3. Reading Files

```python
with open("data.txt", "r") as f:
    content = f.read()        # reads the ENTIRE file as one string
```

```python
with open("data.txt", "r") as f:
    line = f.readline()        # reads a single line, including the trailing '\n'
```

```python
with open("data.txt", "r") as f:
    lines = f.readlines()       # reads all lines into a list of strings
```

### Iterating line by line (the preferred approach for large files)

```python
with open("data.txt", "r") as f:
    for line in f:                # reads one line at a time — memory efficient
        print(line.strip())         # .strip() removes the trailing newline
```

This works because a file object is itself an **iterator** (see the Iterators & Generators doc) — each iteration pulls the next line lazily, without ever loading the whole file into memory. For large files (logs, datasets), this is strongly preferred over `.read()` or `.readlines()`, both of which load everything at once.

```python
# reads the entire multi-gigabyte file into memory — risky
with open("huge.log") as f:
    lines = f.readlines()

# reads one line at a time — safe regardless of file size
with open("huge.log") as f:
    for line in f:
        process(line)
```

---

## 4. Writing Files

```python
with open("output.txt", "w") as f:
    f.write("Hello, world!\n")
    f.write("Second line\n")
```

`write()` does **not** add a newline automatically — you must include `\n` yourself.

### Writing multiple lines at once

```python
lines = ["first\n", "second\n", "third\n"]

with open("output.txt", "w") as f:
    f.writelines(lines)   # writes each string as-is; does NOT add newlines for you
```

### `print()` to a file

```python
with open("output.txt", "w") as f:
    print("Hello, world!", file=f)   # print() adds the newline automatically
```

`print(..., file=f)` is often more convenient than `write()` since it handles the newline and formatting (multiple arguments, `sep`, etc.) automatically.

---

## 5. seek() and tell()

Every open file has a **cursor** — the current read/write position. `tell()` reports it, `seek()` moves it.

```python
with open("data.txt", "r") as f:
    print(f.tell())        # 0 — cursor at the start

    f.read(5)                # read 5 characters
    print(f.tell())          # 5 — cursor advanced

    f.seek(0)                  # move cursor back to the beginning
    content = f.read()          # reads from the start again
```

Useful for re-reading a file, or jumping to a specific byte offset in binary files (e.g. reading a fixed-size record from a structured file).

---

## 6. Text Encoding

Files are stored as raw bytes; text mode automatically encodes/decodes between bytes and Python `str`. Getting the encoding wrong is a common source of bugs, especially with non-English text.

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

**Always specify `encoding="utf-8"` explicitly** rather than relying on the system default, which varies by OS and environment (Windows commonly defaults to something other than UTF-8). Omitting it can cause `UnicodeDecodeError` in production even though the code worked fine locally.

```python
# fragile — depends on the OS/environment's default encoding
with open("data.txt") as f:
    ...

# reliable — explicit and portable
with open("data.txt", encoding="utf-8") as f:
    ...
```

Handling decode errors gracefully:

```python
with open("data.txt", encoding="utf-8", errors="replace") as f:
    content = f.read()   # invalid bytes become the replacement character '�' instead of raising
```

---

## 7. Binary Files

Binary mode (`"rb"`, `"wb"`) reads/writes raw `bytes` instead of decoded text — necessary for images, PDFs, executables, or any non-text data.

```python
with open("image.png", "rb") as f:
    data = f.read()      # returns bytes, not str
    print(type(data))     # <class 'bytes'>
```

```python
with open("copy.png", "wb") as f:
    f.write(data)
```

Copying a file in chunks (avoids loading the entire file into memory at once):

```python
with open("source.bin", "rb") as src, open("dest.bin", "wb") as dst:
    while chunk := src.read(4096):   # read 4KB at a time; walrus operator assigns and checks in one line
        dst.write(chunk)
```

---

## 8. Working with Paths — `pathlib` (Modern Approach)

`pathlib` represents filesystem paths as objects, and is the modern, preferred alternative to string-based path manipulation (`os.path`).

```python
from pathlib import Path

p = Path("data/reports/summary.txt")

p.name          # 'summary.txt'
p.stem            # 'summary'
p.suffix           # '.txt'
p.parent            # Path('data/reports')
p.exists()            # True/False
p.is_file()            # True/False
p.is_dir()               # True/False
```

### Building paths (cross-platform, no manual string concatenation)

```python
base = Path("data")
file_path = base / "reports" / "summary.txt"   # '/' operator joins path parts
```

This automatically uses the correct path separator for the current OS (`/` on Linux/macOS, `\` on Windows) — manually concatenating strings with `+` is fragile and non-portable.

### Reading/writing directly through a Path object

```python
p = Path("data.txt")
content = p.read_text(encoding="utf-8")     # reads the whole file, no need for 'with'
p.write_text("new content", encoding="utf-8")

data = Path("image.png").read_bytes()
```

### Listing and searching directories

```python
p = Path("data")

for file in p.iterdir():          # immediate children only
    print(file)

for file in p.glob("*.txt"):        # all .txt files directly inside
    print(file)

for file in p.rglob("*.txt"):        # recursive — all .txt files in all subdirectories
    print(file)
```

### Creating directories and files

```python
Path("new_folder").mkdir(exist_ok=True)          # create a directory, no error if it exists
Path("nested/folders").mkdir(parents=True, exist_ok=True)   # creates intermediate dirs too
```

---

## 9. `os` and `os.path` (Legacy but Still Common)

Older codebases and some low-level operations still use the `os` module directly.

```python
import os

os.getcwd()                    # current working directory
os.listdir(".")                  # list files/folders in a directory
os.path.exists("data.txt")         # True/False
os.path.join("data", "file.txt")     # 'data/file.txt' — cross-platform join
os.path.abspath("data.txt")           # absolute path
os.remove("old_file.txt")              # delete a file
os.rename("a.txt", "b.txt")              # rename/move a file
os.makedirs("a/b/c", exist_ok=True)        # nested directory creation
```

### Walking a directory tree

```python
for root, dirs, files in os.walk("project"):
    for file in files:
        print(os.path.join(root, file))
```

**Guidance:** for new code, prefer `pathlib` — it's more readable, object-oriented, and less error-prone than chaining `os.path` string functions. `os` is still essential for things `pathlib` doesn't cover (environment variables, process info, permissions), but for pure path manipulation, `pathlib` is the modern standard.

---

## 10. `shutil` — Higher-Level File Operations

For copying, moving, and deleting files/directories beyond what `os` provides directly.

```python
import shutil

shutil.copy("source.txt", "destination.txt")        # copy a single file
shutil.copytree("source_folder", "dest_folder")       # copy an entire directory tree
shutil.move("old_path.txt", "new_path.txt")              # move/rename
shutil.rmtree("folder_to_delete")                           # delete a directory and everything inside it
```

`shutil.rmtree()` is irreversible and deletes recursively — worth being deliberate about before calling it.

---

## 11. Working with JSON

The `json` module converts between Python objects and JSON text — one of the most common I/O tasks in real applications (APIs, config files, data exchange).

```python
import json

data = {"name": "Mehedi", "age": 25, "skills": ["Python", "SQL"]}

# Python object -> JSON string
json_string = json.dumps(data)
json_string_pretty = json.dumps(data, indent=2)   # human-readable formatting

# JSON string -> Python object
parsed = json.loads(json_string)
```

### Reading/writing JSON files directly

```python
with open("config.json", "w") as f:
    json.dump(data, f, indent=2)   # writes directly to the file

with open("config.json", "r") as f:
    loaded = json.load(f)            # reads and parses directly from the file
```

Type mapping between JSON and Python:

| JSON      | Python  |
|-----------|---------|
| object     | `dict`  |
| array       | `list`  |
| string       | `str`   |
| number        | `int`/`float` |
| `true`/`false`  | `bool`  |
| `null`           | `None`  |

---

## 12. Working with CSV

The `csv` module handles reading and writing comma-separated (or otherwise delimited) tabular data correctly — including edge cases like commas inside quoted fields, which naive `split(",")` handles incorrectly.

```python
import csv

with open("data.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)   # each row is a list of strings
```

### Reading as dictionaries (using the header row as keys)

```python
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])   # access by column name
```

### Writing CSV

```python
with open("output.csv", "w", newline="") as f:   # newline="" avoids extra blank lines on Windows
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerow(["Mehedi", 25])
```

```python
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Mehedi", "age": 25})
```

---

## 13. In-Memory "Files" — `io.StringIO` / `io.BytesIO`

Sometimes code expects a file-like object, but the data is already in memory (e.g. testing, or building content before deciding whether to save it). `io.StringIO`/`io.BytesIO` wrap a string/bytes object so it behaves like an open file — supporting `.read()`, `.write()`, iteration, and being passed to functions that expect a file object.

```python
from io import StringIO

fake_file = StringIO("line1\nline2\nline3")

for line in fake_file:
    print(line.strip())
```

```python
buffer = StringIO()
buffer.write("Hello, ")
buffer.write("world!")
print(buffer.getvalue())   # 'Hello, world!'
```

Common in testing — you can pass a `StringIO` object anywhere a real file would be expected, without touching the actual filesystem.

---

## 14. File-Related Exceptions

File operations are one of the most common places real programs encounter runtime errors — the filesystem is inherently unpredictable (permissions, missing files, disks filling up).

```python
try:
    with open("missing.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("File does not exist")
except PermissionError:
    print("No permission to access this file")
except IsADirectoryError:
    print("Expected a file, got a directory")
```

Following the EAFP principle from the Exception Handling doc, this is generally preferred over checking `Path.exists()` first — the file could still disappear between the check and the actual `open()` call.

---

## Key Points

- Always use `with open(...) as f:` — it guarantees the file is closed even if an exception occurs
- File modes (`r`, `w`, `a`, `x`, `+`, `b`) control read/write access and whether the file is truncated, appended to, or must/mustn't already exist
- Iterate a file line by line (`for line in f:`) for large files instead of `.read()`/`.readlines()`, which load everything into memory at once
- Always specify `encoding="utf-8"` explicitly for text files — relying on the system default is a common source of production-only bugs
- Binary mode (`"rb"`/`"wb"`) works with raw `bytes`, needed for non-text files like images or PDFs
- `pathlib.Path` is the modern, object-oriented, cross-platform way to work with filesystem paths — preferred over manual `os.path` string manipulation for new code
- `shutil` handles higher-level operations: copying, moving, and recursively deleting files/directories
- `json` and `csv` are the standard tools for structured text formats — both can read/write directly to files or convert to/from Python strings
- `io.StringIO`/`io.BytesIO` let in-memory data act like a file, useful for testing or building content before persisting it
- Wrap file operations in `try`/`except`, catching specific exceptions like `FileNotFoundError` and `PermissionError` — the filesystem fails in ways your code can't always predict in advance