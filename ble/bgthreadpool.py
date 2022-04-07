import concurrent.futures
import queue

import threading


# This is a singleton thread pool to allow us to single thread operations in a background thread.
import traceback

from kivy.logger import Logger


class SingleThreader:
    def __init__(self):
        self.SubmitQ = queue.Queue()
        self.SingleThread = threading.Thread(name='SingleThread', daemon=True, target=self._bgloop)
        self.Running = True
        self.SingleThread.start()

    def shutdown(self):
        self.Running = False
        self.SingleThread.join()

    def submit(self, fn, /, *args, **kwargs):
        self.SubmitQ.put((fn, args, kwargs))

    def _bgloop(self):
        while self.Running:
            try:
                (fn, args, kwargs) = self.SubmitQ.get()
                fn(*args, **kwargs)
            except Exception as exc:
                Logger.debug("BLE: EXCEPTION: %s" % (traceback.format_exc(),))


__ST = SingleThreader()


def shutdown():
    __ST.shutdown()


def submit(fn, /, *args, **kwargs):
    """
    Submit a function to our single background thread.

    If the function throws an exception then the thread just log the exception.
    Functions must handle all exceptions themselves. There is no mechanism to pass back exceptions.

    Couldn't use a ThreadPoolExecutor, because it would insist on waiting on subthreads to finish execution.
    """
    Logger.debug("Submitted: %s" % (repr(fn),))
    __ST.submit(fn, *args, **kwargs)
