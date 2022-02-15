import threading

"""
Provide a threadsafe global counter.

This will be used to provide a canonical ordering for things that happen.

If we need to worry about the relative order of different operations, they will each
grab a counter value at the start of their operation. Smaller values are older.

TODO: This will eventually be used to resolve possible race conditions in connect/disconnect
in the websockets server.
"""

_Counter = 0
_CounterSema = threading.Semaphore()


def get_and_inc_global_count():
    global _Counter
    global _CounterSema

    _CounterSema.acquire()
    _Counter = _Counter + 1
    _CounterSema.acquire()
    return _Counter
