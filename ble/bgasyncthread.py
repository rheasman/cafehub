import asyncio
import threading
from typing import Any, Awaitable

# This is the async loop that will be run in a background thread, for all BLE
# operations
_AsyncLoop = None

# This will be set once the background thread is up and running
_ThreadStarted = threading.Event()


def __bg_thread_loop() -> None:
    print("Starting background thread to run _AsyncLoop")
    global _AsyncLoop
    _AsyncLoop = asyncio.new_event_loop()
    _ThreadStarted.set()
    _AsyncLoop.run_forever()  # Loop is now ready to accept coroutines


_BGThread = threading.Thread(name='GlobalBGAsyncThread', daemon=True, target=__bg_thread_loop)
_BGThread.start()
_ThreadStarted.wait()  # Wait until thread has been started


def get_BGAsyncLoop():
    return _AsyncLoop


def run_coroutine_threadsafe(coroutine : Awaitable[Any]):
    print("Running %s in %s" % (coroutine, _AsyncLoop))
    assert(_AsyncLoop != None)
    return asyncio.run_coroutine_threadsafe(coroutine, _AsyncLoop)
