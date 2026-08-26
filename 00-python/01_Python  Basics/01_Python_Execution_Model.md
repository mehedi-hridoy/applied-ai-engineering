# Python Execution Model

Python is an **interpreted language**. Instead of directly executing Python source code as machine code, Python processes the source code and converts it into an intermediate form called **bytecode**. This bytecode is then executed by the **Python Virtual Machine (PVM)**.

The overall process can be understood as:

```text
Source Code
    ↓
Lexical Analysis / Tokenization
    ↓
Syntax Analysis / AST
    ↓
Bytecode Compilation
    ↓
Python Virtual Machine (PVM)
    ↓
Execution
```

## 1. Source Code

**Source code** is the original Python code written by the programmer.

Example:

```python
x = 5 + 3
```

---

## 2. Lexical Analysis and Tokenization

The first step is **lexical analysis**, also called **tokenization**.

The Python source code is broken into smaller meaningful units called **tokens**.

For:

```python
x = 5 + 3
```

The tokens are:

* `x` → identifier
* `=` → operator
* `5` → literal
* `+` → operator
* `3` → literal

Tokens are the basic building blocks that Python uses to understand the source code.

---

## 3. Syntax Analysis and AST

After tokenization, Python analyzes the structure of the tokens to determine whether they follow Python's grammar.

This produces an **Abstract Syntax Tree (AST)**.

For:

```python
x = 5 + 3
```

A simplified AST looks like:

```text
Assignment
├── Target: x
└── Value
    ├── Left: 5
    └── Right: 3
        └── Operator: +
```

The AST represents the **structure and meaning** of the code.

---

## 4. Bytecode Compilation

The AST is then compiled into **bytecode**.

Bytecode is an intermediate, platform-independent representation of Python instructions. It is not the same as CPU machine code.

For example:

```text
LOAD_CONST 5
LOAD_CONST 3
BINARY_ADD
STORE_NAME x
```

These instructions represent the operations needed to calculate:

```python
x = 5 + 3
```

Python may store compiled bytecode in `.pyc` files inside the `__pycache__` directory.

---

## 5. Execution by the Python Virtual Machine (PVM)

Finally, the **Python Virtual Machine (PVM)** executes the bytecode.

The PVM processes the bytecode instructions and performs the actual operations.

For:

```python
x = 5 + 3
```

The PVM effectively:

```text
Load 5
   ↓
Load 3
   ↓
Add them
   ↓
Store result in x
```

So:

```python
x = 5 + 3
```

produces:

```text
x = 8
```

---

## Complete Execution Flow

```text
Python Source Code

        ↓

   Tokenization

        ↓

   Syntax Analysis

        ↓

       AST

        ↓

Bytecode Compilation

        ↓

     Bytecode

        ↓

       PVM

        ↓

     Execution

        ↓

      Result
```

---

# 6. Mathematical Foundations

Several computer-science concepts help explain how Python processes and executes code.

## Finite Automata

Finite automata are simple computational models that process input **one symbol at a time** while moving between a finite number of states.

They help explain how a **lexer/tokenizer recognizes tokens**.

```text
Input → State → State → State → Token
```

> **Finite Automata → help recognize tokens.**

## Context-Free Grammar (CFG)

A context-free grammar defines rules for how valid programming-language structures can be formed.

For example:

```text
Assignment
    ↓
Identifier + "=" + Expression
```

So:

```python
x = 5
```

follows the grammar, while invalid arrangements do not.

> **CFG → defines valid syntax structures.**

## Stack-Based Computation

The PVM uses a **stack-based execution model**.

A stack works like a pile of plates:

```text
    ┌─────┐
    │  3  │ ← top
    ├─────┤
    │  5  │
    └─────┘
```

Values can be **pushed** onto the stack and **popped** from it.

For:

```python
x = 5 + 3
```

Conceptually:

```text
Push 5
Push 3
   ↓
Add
   ↓
8
   ↓
Store in x
```

> **Stack-based computation → the PVM uses a stack to manage temporary values during execution.**

---

# 7. Execution Optimization

Python can perform optimizations to make execution more efficient.

## Compile-Time Optimization

Some operations can be evaluated before runtime.

Example:

```python
x = 10 * 20
```

Python can recognize that the result is always `200`.

This is called **constant folding**.

## Runtime Optimization

During execution, Python can optimize frequently executed operations through techniques such as **caching and specialization**.

> **Optimization → improve execution speed without changing the program's result.**

---

# 8. Global Interpreter Lock (GIL)

The **Global Interpreter Lock (GIL)** is a mechanism in traditional CPython execution that allows only one thread at a time to execute Python bytecode within a process.

This mainly matters when using multiple threads for **CPU-bound Python code**.

```text
Thread 1 ──┐
Thread 2 ──┼──→ Python Interpreter
Thread 3 ──┘
```

For I/O-bound work, threads can still be useful because a thread can wait for I/O while another thread performs work.

> **GIL → affects how threads execute Python code in CPython.**

---

# 9. Concurrency vs Parallelism

## Concurrency

Multiple tasks make progress during the same period.

```text
A → B → A → C → B
```

Tasks may take turns.

## Parallelism

Multiple tasks execute **at the same time**, usually on different CPU cores.

```text
Core 1 → A
Core 2 → B
Core 3 → C
```

> **Concurrency = multiple tasks making progress.**

> **Parallelism = multiple tasks executing simultaneously.**

---

# 10. Handling Multiple Tasks

Different problems require different approaches.

## Threads

Useful mainly for **I/O-bound tasks**.

Examples:

* Network requests
* File operations
* Waiting for external services

## `asyncio`

Provides asynchronous concurrency, especially useful for applications handling many I/O operations.

Examples:

* APIs
* Network requests
* Database operations
* Web servers

## Multiprocessing

Uses separate processes, each with its own Python interpreter and memory space.

This allows **true CPU parallelism**.

Useful for:

* CPU-heavy calculations
* CPU-intensive data processing

---

# 11. C / Cython / Native Extensions

Python is convenient and productive, but some CPU-intensive operations may be faster when implemented in compiled native code.

The idea is:

```text
Python
   ↓
Native Extension
   ↓
Compiled Machine Code
   ↓
CPU
```

Common technologies include:

* **C**
* **C++**
* **Cython**
* **Rust**

### Cython

Cython allows Python-like code to be compiled into native code and can use C-style type declarations for performance.

Conceptually:

```text
Python-like Code
      ↓
    Cython
      ↓
Compiled Native Code
      ↓
     CPU
```

Native extensions are useful when **profiling shows that a specific operation is a performance bottleneck**.

> **Measure first → find the bottleneck → optimize.**

---

# Complete Mental Model

```text
                  Python Source Code
                         │
                         ▼
                 Tokenization
                         │
                         ▼
                  Finite Automata
                  "Recognize tokens"
                         │
                         ▼
                    Parsing / AST
                         │
                         ▼
               Context-Free Grammar
                "Valid syntax?"
                         │
                         ▼
                Bytecode Compilation
                         │
                         ▼
                      Bytecode
                         │
                         ▼
                        PVM
                         │
                         ▼
               Stack-Based Execution
                         │
                         ▼
                    Optimization
                         │
                         ▼
                     Execution
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Threads    asyncio   Multiprocessing
              │          │          │
             I/O        I/O       CPU work
                         │
                         ▼
                If performance is
                    a bottleneck
                         │
                         ▼
                Native Extensions
              C / C++ / Cython / Rust
```

# Key Takeaways

* **Source code** → code written by the programmer.
* **Tokenization** → breaks source code into tokens.
* **Finite automata** → help recognize tokens.
* **Parsing / AST** → represents the structure of the code.
* **CFG** → defines valid syntax structures.
* **Bytecode** → intermediate instructions.
* **PVM** → executes the bytecode.
* **Stack-based execution** → PVM uses a stack for temporary values.
* **Optimization** → improves execution efficiency.
* **GIL** → affects thread execution in CPython.
* **Concurrency** → multiple tasks making progress.
* **Parallelism** → multiple tasks executing simultaneously.
* **Threads / `asyncio`** → particularly useful for I/O-bound work.
* **Multiprocessing** → useful for CPU-bound parallel work.
* **Native extensions** → compiled code for specific performance-critical operations.
* **Best optimization rule:** **Measure → find the bottleneck → optimize.**
