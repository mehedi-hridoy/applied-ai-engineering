# Python Concurrency & Parallelism

This builds directly on the GIL section from the Memory Management doc. Concurrency and parallelism are two different things that get conflated constantly — this document covers Python's three main tools (threading, multiprocessing, asyncio), when each actually helps, and the core hazards (race conditions, deadlocks) that come with sharing state across execution paths.

---

## 1. Concurrency vs Parallelism

These terms are often used interchangeably, but they describe different things.

- **Concurrency** — dealing with multiple tasks by interleaving progress on them, not necessarily running at the exact same instant. Like one chef switching between three dishes, making progress on each.
- **Parallelism** — actually running multiple tasks at the exact same instant, using multiple CPU cores. Like three chefs, each cooking a separate dish simultaneously.

```text
Concurrency (single core, interleaved):
Task A: ---   ---   ---
Task B:    ---   ---   ---
(progress on both, but only one runs at any instant)

Parallelism (multiple cores, simultaneous):
Task A: ------------------
Task B: ------------------
(both genuinely running at the same time)
```

A program can be concurrent without being parallel (as with Python threads, due to the GIL), and it's possible to be parallel without much concurrency structure (simple batch processing across cores). Understanding which one a given problem actually needs is the first and most important decision.

---

## 2. Two Kinds of Workload: CPU-Bound vs I/O-Bound

This distinction determines which tool is appropriate — using the wrong one for the wrong workload is the most common concurrency mistake in Python.

| Workload type | Bottleneck                                     | Examples                                  |
|-----------------|---------------------------------------------------|---------------------------------------------|
| **CPU-bound**     | Computation — the CPU is constantly busy calculating | Image processing, number crunching, parsing large data |
| **I/O-bound**      | Waiting — the CPU is mostly idle, waiting on something external | Network requests, database queries, file/disk operations |

```python
# CPU-bound — the CPU never stops working
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# I/O-bound — the CPU is idle while waiting for a response
import requests
def fetch(url):
    return requests.get(url)   # the program just waits here
```

- **Threads help I/O-bound work** — while one thread waits on a network response, the GIL is released and another thread can run
- **Threads do NOT help CPU-bound work** — the GIL means only one thread executes Python bytecode at a time, so adding threads to CPU-heavy code doesn't speed it up
- **Processes help CPU-bound work** — each process has its own interpreter and GIL, so they can run on separate CPU cores simultaneously
- **`asyncio` helps I/O-bound work**, using a fundamentally different mechanism (a single thread, cooperative switching) rather than OS threads

---

## 3. Threading

The `threading` module runs multiple threads within a single process, sharing the same memory space.

```python
import threading
import time

def download(name, seconds):
    print(f"Starting {name}")
    time.sleep(seconds)   # simulates an I/O wait (e.g. a network call)
    print(f"Finished {name}")

t1 = threading.Thread(target=download, args=("file1", 2))
t2 = threading.Thread(target=download, args=("file2", 2))

t1.start()
t2.start()

t1.join()   # wait for t1 to finish
t2.join()    # wait for t2 to finish

print("All downloads complete")
```

Both downloads run concurrently — the total time is roughly 2 seconds (the two `sleep()` calls overlap), not 4, because while one thread sleeps, the GIL is released and the other can run.

### Race Conditions

When multiple threads read and modify shared data without coordination, the result can become inconsistent — this is one of the most important hazards in concurrent programming.

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1   # NOT atomic — read, add, write, as three separate steps

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)   # often NOT 200,000 — some increments get lost due to interleaved access
```

`counter += 1` looks like a single operation but is really three: read the value, add one, write it back. If two threads interleave these steps, one thread's update can be silently overwritten by another's.

### Locks — Fixing Race Conditions

A `Lock` ensures only one thread can execute a critical section at a time.

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100_000):
        with lock:            # only one thread can be inside this block at a time
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)   # reliably 200,000
```

`with lock:` acquires the lock on entry and releases it automatically on exit, even if an exception occurs — the same context manager pattern used elsewhere in Python for guaranteed cleanup.

### Deadlocks

A deadlock occurs when two or more threads are each waiting on a resource the other holds, and neither can proceed.

```python
lock_a = threading.Lock()
lock_b = threading.Lock()

def task_1():
    with lock_a:
        with lock_b:   # waits for lock_b, held by task_2
            ...

def task_2():
    with lock_b:
        with lock_a:   # waits for lock_a, held by task_1
            ...
# both threads wait forever — classic deadlock
```

**Avoiding deadlocks:** always acquire multiple locks in a **consistent, agreed-upon order** across every part of the code that needs them together — if every function always locks `lock_a` before `lock_b`, this particular deadlock can't occur.

---

## 4. Multiprocessing

The `multiprocessing` module runs separate **processes**, each with its own Python interpreter, memory space, and GIL — enabling genuine parallel execution on multiple CPU cores.

```python
from multiprocessing import Process
import time

def cpu_heavy_task(n):
    total = 0
    for i in range(n):
        total += i * i
    print(f"Done: {total}")

if __name__ == "__main__":   # required on some platforms (esp. Windows) for multiprocessing to work correctly
    p1 = Process(target=cpu_heavy_task, args=(50_000_000,))
    p2 = Process(target=cpu_heavy_task, args=(50_000_000,))

    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

Unlike threading, this genuinely uses multiple CPU cores simultaneously for CPU-bound work.

### The `if __name__ == "__main__":` Guard

On platforms that create new processes by re-importing the main module (notably Windows, and macOS in some configurations), code at the top level of the script would otherwise run again in every spawned child process, potentially causing infinite process creation. Guarding process-starting code behind `if __name__ == "__main__":` prevents this — a direct, practical application of the pattern covered in the Modules & Packages doc.

### Sharing Data Between Processes

Since each process has its own separate memory, variables aren't shared automatically the way they are between threads — data must be explicitly passed using dedicated mechanisms.

```python
from multiprocessing import Process, Queue

def worker(q, n):
    q.put(n * n)

if __name__ == "__main__":
    q = Queue()
    processes = [Process(target=worker, args=(q, i)) for i in range(5)]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    results = [q.get() for _ in processes]
    print(results)
```

`multiprocessing.Queue` and `multiprocessing.Value`/`Array` (for simple shared primitive data) are the standard ways to move data between processes, since direct shared memory the way threads have it isn't available by default.

---

## 5. `concurrent.futures` — A Simpler, Unified Interface

A higher-level abstraction over both threading and multiprocessing, using a consistent pool-based API — generally preferred over raw `Thread`/`Process` objects for everyday code.

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def fetch(url):
    ...
    return f"data from {url}"

urls = ["url1", "url2", "url3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch, urls))   # runs fetch() concurrently across threads
```

```python
def cpu_task(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_task, [1_000_000] * 4))
```

Swapping `ThreadPoolExecutor` for `ProcessPoolExecutor` (identical API) switches from threads to processes — making it easy to pick the right tool for I/O-bound vs CPU-bound work without rewriting the surrounding logic.

### Working with individual futures

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    future = executor.submit(fetch, "some_url")
    print(future.result())   # blocks until this specific task completes
```

`executor.submit()` returns a `Future` object immediately — representing work that may still be in progress — while `.result()` blocks until that particular task finishes and returns its value.

---

## 6. `asyncio` — Cooperative Concurrency

`asyncio` provides concurrency using a **single thread** and an **event loop**, rather than OS-level threads or processes. Instead of the OS preemptively switching between threads, code voluntarily ("cooperatively") yields control at specific points, letting other tasks run while it waits.

```python
import asyncio

async def download(name, seconds):
    print(f"Starting {name}")
    await asyncio.sleep(seconds)   # yields control here — other tasks can run during the wait
    print(f"Finished {name}")

async def main():
    await asyncio.gather(
        download("file1", 2),
        download("file2", 2),
    )

asyncio.run(main())
```

Total time is roughly 2 seconds, not 4 — while one coroutine is "sleeping," control returns to the event loop, which runs the other coroutine.

### `async` / `await`

- `async def` defines a **coroutine function** — calling it doesn't run the body immediately; it returns a coroutine object (similar to how calling a generator function doesn't run its body either)
- `await` pauses the current coroutine until the awaited operation completes, yielding control back to the event loop in the meantime

```python
async def greet():
    print("Hello")

coro = greet()   # doesn't print anything yet — just creates a coroutine object
asyncio.run(coro)   # NOW it actually runs, printing "Hello"
```

### Why asyncio over threading for I/O-bound work

- No race conditions from shared mutable state in the same way threads have — only one coroutine actually executes Python code at any instant, and control only switches at explicit `await` points, not at unpredictable moments
- Can scale to a very large number of concurrent tasks (thousands of open connections) far more cheaply than an equivalent number of OS threads, which each carry real memory/scheduling overhead
- Requires an "async-aware" ecosystem — libraries must be written to support `async`/`await` (e.g. `aiohttp` instead of `requests`) to actually benefit; calling a blocking, non-async library from inside a coroutine defeats the purpose, since it blocks the entire event loop

```python
# WRONG — blocks the entire event loop, defeating the purpose of asyncio
import time

async def bad_task():
    time.sleep(2)   # a regular, blocking sleep — freezes everything, not just this coroutine

# RIGHT — yields control properly
async def good_task():
    await asyncio.sleep(2)
```

### Running multiple coroutines

```python
async def main():
    results = await asyncio.gather(
        download("a", 1),
        download("b", 2),
        download("c", 1),
    )
```

`asyncio.gather()` runs all given coroutines concurrently and waits for all of them to finish, collecting their results in order.

---

## 7. Comparing the Three Tools

| Tool             | Best for      | Mechanism                              | True parallelism? |
|--------------------|---------------|--------------------------------------------|----------------------|
| `threading`          | I/O-bound      | OS threads, GIL-limited                       | No                     |
| `multiprocessing`      | CPU-bound      | Separate processes, separate GILs each          | Yes                     |
| `asyncio`                | I/O-bound (high volume) | Single thread, cooperative event loop           | No                       |

A rough decision guide:

```text
Is the work mostly waiting on I/O (network, disk, DB)?
├── Yes, and you need to coordinate MANY (hundreds/thousands) of tasks efficiently → asyncio
├── Yes, and it's a smaller number of tasks, or working with non-async libraries → threading
└── No — it's CPU-heavy computation → multiprocessing
```

In real systems, these tools are sometimes combined — e.g. a `ProcessPoolExecutor` running CPU-heavy work, dispatched from within an `asyncio` application handling I/O for the rest of the system (`loop.run_in_executor()` bridges the two).

---

## 8. Queues for Coordinating Work

Across all three models, **queues** are the standard, safe way to pass data between concurrent workers, instead of sharing raw mutable state directly.

### Thread-safe queue

```python
import threading
import queue

q = queue.Queue()

def producer():
    for i in range(5):
        q.put(i)

def consumer():
    while True:
        item = q.get()
        if item is None:   # sentinel value signaling "stop"
            break
        print(f"Consumed: {item}")

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
```

`queue.Queue` handles all the internal locking automatically — safe to use across multiple threads without manually managing locks yourself.

### Async queue

```python
import asyncio

async def producer(q):
    for i in range(5):
        await q.put(i)

async def consumer(q):
    while True:
        item = await q.get()
        print(f"Consumed: {item}")
        q.task_done()
```

`asyncio.Queue` provides the equivalent pattern for coroutine-based concurrency — the producer/consumer pattern itself is identical in spirit across threading, multiprocessing, and asyncio; only the specific queue type changes.

---

## Key Points

- Concurrency is about interleaving progress on multiple tasks; parallelism is about genuinely running tasks at the same instant on multiple cores — they're related but distinct
- Identify the workload first: CPU-bound (computation-heavy) needs `multiprocessing`; I/O-bound (waiting-heavy) benefits from `threading` or `asyncio`
- `threading` allows concurrency within a single process, but the GIL prevents true CPU parallelism — it helps mainly because I/O operations release the GIL while waiting
- Race conditions arise when threads read/modify shared state without coordination; `Lock` objects (usually via `with lock:`) prevent this by serializing access to critical sections
- Deadlocks occur when threads wait on each other's locks in a cycle — avoided by acquiring multiple locks in a consistent order everywhere
- `multiprocessing` runs separate processes with independent memory and GILs, enabling true parallel execution for CPU-bound work; data must be explicitly shared via `Queue`, `Value`, or `Array`
- `concurrent.futures` (`ThreadPoolExecutor`/`ProcessPoolExecutor`) provides a simpler, unified pool-based API over both threading and multiprocessing
- `asyncio` achieves high-volume I/O concurrency with a single thread and a cooperative event loop — `async`/`await` explicitly mark where control can be yielded; blocking calls inside a coroutine freeze the entire event loop
- Guard multiprocessing entry points with `if __name__ == "__main__":` to avoid runaway process creation on platforms that re-import the main module
- Queues (`queue.Queue`, `multiprocessing.Queue`, `asyncio.Queue`) are the standard, safe way to pass data between concurrent workers across all three models