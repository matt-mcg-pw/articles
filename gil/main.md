# DEBUGGING PYTHON THREADS

## What is the GIL?
- Single lock in CPython interpreter that allows a Python thread to run
- Only 1
- Python process allows 1 main thread, arbitrary children threads, and a Single
lock that allows a thread to run
- The GIL located at ceval_gil.h, following block are comments from file
  ```
  Notes about the implementation:

  - The GIL is just a boolean variable (locked) whose access is protected
  by a mutex (gil_mutex), and whose changes are signalled by a condition
  variable (gil_cond). gil_mutex is taken for short periods of time,
  and therefore mostly uncontended.

  - In the GIL-holding thread, the main loop (PyEval_EvalFrameEx) must be
  able to release the GIL on demand by another thread. A volatile boolean
  variable (gil_drop_request) is used for that purpose, which is checked
  at every turn of the eval loop. That variable is set after a wait of
  `interval` microseconds on `gil_cond` has timed out.

  [Actually, another volatile boolean variable (eval_breaker) is used
   which ORs several conditions into one. Volatile booleans are
   sufficient as inter-thread signalling means since Python is run
   on cache-coherent architectures only.]

  - A thread wanting to take the GIL will first let pass a given amount of
  time (`interval` microseconds) before setting gil_drop_request. This
  encourages a defined switching period, but doesn't enforce it since
  opcodes can take an arbitrary time to execute.

  The `interval` value is available for the user to read and modify
  using the Python API `sys.{get,set}switchinterval()`.

  - When a thread releases the GIL and gil_drop_request is set, that thread
  ensures that another GIL-awaiting thread gets scheduled.
  It does so by waiting on a condition variable (switch_cond) until
  the value of last_holder is changed to something else than its
  own thread state pointer, indicating that another thread was able to
  take the GIL.

  This is meant to prohibit the latency-adverse behaviour on multi-core
  machines where one thread would speculatively release the GIL, but still
  run and end up being the first to re-acquire it, making the "timeslices"
  much longer than expected.
     (Note: this mechanism is enabled with FORCE_SWITCHING above)
```
- Header file that defines PyThread_type_lock
  - /Users/matthewmcguire/.pyenv/versions/3.6.2/Python.framework/Versions/3.6/include/python3.6m/pythread.h

## Is Python multi-threaded or good at context switching?

## Python Threads Good At:
- IO
- Sleeping
- Blocking

## Python Threads Bad At:
- Comms
  - Valuable data lost between threads by default
  - Decorators for passing data between threads
  - Need to maintain record for chain of execution
- Concurrency - in the historical sense, context switching more accurate

## Tools for debugging Python threads

### Profiling
- cProfile
- Line profiler
- Tracing
- Memory
  - Matplotlib for graphing

### Debugging
- ipython
  - Needs some lines of debug code to file
- rpdb
- Disassembler



# Random Notes
- Python runs on stack
  - Data stack
  - Call stack / instruction stack
-Frames
  - Frame per function call, not function def
  - Run functions, etc
  - Frames have there own data and lock stacks
- Disassembler
- Interpreter runs bytecode from simple compilation before interpret time

- Python VM
  - Collection of Frames
  - Data stacks on Frames
  - Way to run Frames

- c_eval.c
  - 1500 line switch statement for op-codes
  - Python3 computed go-to's
