# DEBUGGING PYTHON THREADS

## What is the Global Interpreter Lock (GIL)?
- Single lock in CPython interpreter that allows a Python thread to run
- Python process allows 1 main thread, ~~arbitrary~~ children threads, and a lock that allows a thread to run
- GIL protects pointer to PyThreadState
  - PyThreadState saved before interpreter allows spawning of child thread
  - C macros in interpreter handle allowing and ending allowance of threads
  - Thread state is restored after child threads return with state that was saved before threads spawned
- GIL is not held by third party library or C threads
  - If a call to Python is necessary from these threads than a callback API is usually provided with the library
  - Idiom for handling GIL python thread state from external thread CallSomeFunction
    ```c
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    /* Perform Python actions here. */
    result = CallSomeFunction();
    /* evaluate result or handle exception */

    /* Release the thread. No Python API allowed beyond this point. */
    PyGILState_Release(gstate);

    ```

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


## Python Threads Good At:
- Potentially blocking I/O calls and sleeping

## Python Threads Bad At:
- Comms
  - Valuable data lost between threads by default
  - Decorators for passing data between threads
  - Need to maintain record for chain of execution
- Concurrency - fast context switching more accurate

## Tools for debugging Python threads

### Profiling
- cProfile
- Line profiler
- Tracing
- Memory
  - Matplotlib for graphing

### Debugging
- Idiom for passing thread data through chain / decorators to do this
- ipython
  - Needs some lines of debug code to file
- rpdb
- Disassembler


# NEED ANSWERS
- Interpreter is not thread safe:
  - ~~How is memory accessed for each thread when GIL is held~~
    - All python threads have access to all memory in python process
  - How does Python know what section of memory to read from
    - PyThreadState is saved, whats in this object
    - Does it have memory state snapshot for thread
    - Does a thread create its own stacks
      - Data stack
      - Instruction stack


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

- ceval.c
  - 2.7 1500 line switch statement for op-codes
  - Python3 computed go-to's

- Output from `threads_example` in `src`
```
matthewmcguire@ip-192-168-0-211 ~/hack/articles/gil/src                                                                                            [12:27:58]
> $ python threads_example.py                                                                                                                     [±master ●]
Getting date time from json test site...
0th request for date
Getting headers from json test site...
0th request for headers
1th request for headers
1th request for date
2th request for headers
2th request for date
3th request for date
3th request for headers
0
4th request for date
4th request for headers
5th request for date
5th request for headers
6th request for date
6th request for headers
1
7th request for date
7th request for headers
8th request for headers
8th request for date
9th request for date
9th request for headers
10th request for headers
10th request for date
2
11th request for headers
11th request for date
12th request for date
12th request for headers
13th request for date
13th request for headers
14th request for date
14th request for headers
3
15th request for date
15th request for headers
16th request for headers
16th request for date
17th request for headers
17th request for date
4
18th request for headers
18th request for date
19th request for headers
19th request for date
20th request for date
20th request for headers
21th request for headers
21th request for date
5
22th request for headers
22th request for date
23th request for headers
23th request for date
24th request for headers
24th request for date
25th request for headers
25th request for date
6
26th request for headers
26th request for date
27th request for headers
27th request for date
28th request for date
28th request for headers
29th request for date
29th request for headers
7
30th request for date
'Headers response: <Response [200]>'
31th request for date
32th request for date
33th request for date
8
34th request for date
35th request for date
36th request for date
37th request for date
9
38th request for date
39th request for date
40th request for date
10
41th request for date
42th request for date
43th request for date
44th request for date
11
45th request for date
46th request for date
47th request for date
12
48th request for date
49th request for date
'DateTime response: <Response [200]>'
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
```

- Second Example (Show timing discrepancy)
```
matthewmcguire@ip-192-168-0-211 ~/hack/articles/gil/src                                                                                            [12:31:02]
> $ python threads_example.py                                                                                                                     [±master ●]
Getting date time from json test site...
0th request for date
Getting headers from json test site...
0th request for headers
1th request for headers
1th request for date
0
2th request for headers
2th request for date
1
3th request for headers
3th request for date
2
4th request for headers
4th request for date
3
5th request for headers
5th request for date
6th request for headers
6th request for date
4
7th request for headers
7th request for date
5
8th request for headers
8th request for date
6
9th request for headers
9th request for date
10th request for headers
7
10th request for date
11th request for headers
11th request for date
8
12th request for headers
12th request for date
9
13th request for headers
13th request for date
10
14th request for headers
14th request for date
11
15th request for headers
15th request for date
16th request for headers
16th request for date
12
17th request for headers
17th request for date
13
18th request for date
18th request for headers
14
19th request for headers
19th request for date
15
20th request for headers
20th request for date
21th request for headers
21th request for date
16
22th request for date
22th request for headers
17
23th request for date
23th request for headers
18
24th request for date
24th request for headers
19
25th request for headers
25th request for date
26th request for date
26th request for headers
20
27th request for headers
27th request for date
21
28th request for headers
28th request for date
22
29th request for headers
29th request for date
23
30th request for date
'Headers response: <Response [200]>'
31th request for date
24
32th request for date
25
33th request for date
26
34th request for date
27
35th request for date
36th request for date
28
37th request for date
29
38th request for date
39th request for date
40th request for date
41th request for date
42th request for date
43th request for date
44th request for date
45th request for date
46th request for date
47th request for date
48th request for date
49th request for date
'DateTime response: <Response [200]>'
```
