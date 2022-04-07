import asyncio
import threading

# This is the async loop that will be run in a background thread, for all WebSockets
# operations
_WSAsyncLoop = None

# This will be set once the background thread is up and running
_WSThreadStarted = threading.Event()


def __ws_thread_loop() -> None:
    global _WSAsyncLoop
    _WSAsyncLoop = asyncio.new_event_loop()
    _WSThreadStarted.set()
    _WSAsyncLoop.run_forever()  # Loop is now ready to accept coroutines


_WSBGThread = threading.Thread(name='GlobalWSAsyncThread', daemon=True, target=__ws_thread_loop)
_WSBGThread.start()
_WSThreadStarted.wait()  # Wait until thread has been started


def get_WSAsyncLoop():
    return _WSAsyncLoop


def run_coroutine_threadsafe(coroutine):
    return asyncio.run_coroutine_threadsafe(coroutine, _WSAsyncLoop)  # type: ignore
