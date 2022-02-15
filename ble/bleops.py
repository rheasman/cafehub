import abc
import asyncio
import collections
import functools
import inspect
import queue
import threading
import traceback
from typing import Any

from kivy.logger import Logger

from ble.bgasyncthread import run_coroutine_threadsafe
from ble.bleexceptions import *

import ble.bgthreadpool


class OpResult:
    def getResult(self) -> Any:
        """
        Get a result. If the result is an exception, it raises the exception.
        """
        if hasattr(self, 'Exception'):
            raise self.Exception

        if hasattr(self, 'Result'):
            return self.Result

        return None

    def setException(self, e):
        self.Exception = e

    def setResult(self, r):
        self.Result = r


class QOp:
    def __init__(self, op, *args, **kwargs):
        """
        Represents an operation.

        When do() is called, Op will be called with manager, args and kwargs.
        If callback is set, then results will be passed to the callback
        """
        self.Op = op
        self.Args = args
        self.KwArgs = kwargs
        try:
            self.Callback = kwargs['callback']
            del kwargs['callback']
        except IndexError:
            self.Callback = None

    def do(self, manager):
        opr = OpResult()
        try:
            Logger.debug("BLE: do() %s" % (repr(self.Op)))
            res = self.Op(*self.Args, **self.KwArgs, manager=manager)
            if inspect.isawaitable(res):
                # We might have been passed an async function or method, which means
                # it hasn't actually been run yet. If so we need to run it in the
                # background thread and get the result
                res = run_coroutine_threadsafe(res).result()
            opr.setResult(res)
        except Exception as e:
            # Logger.debug("EXCEPTION: do(): %s" % (traceback.format_exc(),))
            opr.setException(e)

        manager.signalOpIsDone()
        if callable(self.Callback):
            print("Calling", repr(self.Callback))
            self.Callback(opr)

        Logger.debug("BLE: do() done")

    def cancel(self, manager, reason):
        opr = OpResult()
        try:

            res = self.Op(*self.Args, **self.KwArgs, manager=manager, reason=reason)
            if inspect.isawaitable(res):
                # We might have been passed an async function or method, which means
                # it hasn't actually been run yet. If so we need to run it in the
                # background thread and get the result
                res = run_coroutine_threadsafe(res).result()
            opr.setResult(res)
        except Exception as e:
            Logger.debug("EXCEPTION: cancel(): %s" % (traceback.format_exc(),))
            opr.setException(e)

        manager.signalOpIsDone()
        if callable(self.Callback):
            self.Callback(opr)


class CountingSemaphore(threading.Semaphore):
    """
    My own semaphore object that adds "up" and "down" to the naming scheme.
    Just makes things a little easier to read.
    """

    def up(self, *args, **kwargs):
        self.release(*args, **kwargs)

    def down(self, *args, **kwargs):
        self.acquire(*args, **kwargs)


def synchronized_with_lock(lock_name):
    """
    Make a locking decorator that will mean that only one method/function
    associated with a lock can be active at a time
    """

    def decorator(method):
        def synced_method(self, *args, **kwargs):
            # Logger.debug("BLE: Entering %s" % (method.__name__,))
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kwargs)

        return synced_method

    return decorator


class QOpManager:
    """
    Operations (QOps)can be added to a queue, and will be executed in their own
    thread.

    doNextOp() is a blocking operation that should be called over and over,
    probably in its own thread.

    For BLE operations we'll have a singleton of this being called for all ops,
    so that BLE operations are explicitely single threaded and running in the
    background.
    """

    def __init__(self):
        Logger.debug("BLE: CREATED QOpManager")
        self.QLock = threading.RLock()
        self.OpCount = CountingSemaphore(value=0)
        self.OpDone = threading.Event()
        self.OpDone.set()  # There is no outstanding operation. It is "done".
        self._dumpQ()

    @synchronized_with_lock("QLock")
    def _dumpQ(self):
        """
        Throws away all operations. Callbacks are not called, etc.
        Probably not what you want (unless, you know, it is).
        """
        self.Q = collections.deque()

    @synchronized_with_lock("QLock")
    def cancelQ(self, reason):
        """
        Cancels all operations, letting them know that they have been discarded
        and why. They can then do whatever is necessary.

        Cancelled operations can add things back to the queue. New items will be
        executed once the current cancelled items have all been dealt with.
        """
        cancelleditems = self.Q
        self._dumpQ()

        for i in cancelleditems:
            # Number of cancelled items will be <= OpCount.
            # So this can't lock up
            i.cancel(reason)
            self.OpCount.down()

    @synchronized_with_lock("QLock")
    def addFIFOOp(self, op: QOp):
        """
        Add an item to the back of the queue
        """
        # Logger.debug("BLE: addFIFOOp")
        self.Q.appendleft(op)
        self.OpCount.up()  # Increment count of things to do

    @synchronized_with_lock("QLock")
    def addLIFOOp(self, op: QOp):
        """
        Add an item that will be the next thing to be executed
        """
        self.Q.append(op)
        self.OpCount.up()  # Increment count of things to do

    def signalOpIsDone(self):
        """
        Called after the current op to signal that it is done, by the op. Don't use.
        i.e. Don't call this from a callback.
        """
        self.OpDone.set()  # Operation is now "done"

    def waitUntilReady(self, timeout=None):
        self.OpDone.wait(timeout=timeout)

    def doNextOp(self):
        self.OpDone.wait()  # Wait until any pending operation is done (set)
        self.OpDone.clear()  # Just about to start new op. Mark it not done (ie. clear)

        self.OpCount.down()  # Sleep until there is something to do

        # do operation
        self.Q.pop().do(manager=self)


class QOpExecutor:
    """
    A QOpExecutor provides the threadpool for a manager.
    
    This was originally just a thread, but I am concerned about submitting more
    than one task at a time to the android stack, so now this thread submits work
    to a singleton background thread.
    """

    def __init__(self, qopmanager: QOpManager):
        self.Manager = qopmanager
        self.TimeToExit = False
        self.Thread = threading.Thread(name='QOpExecutorThread', daemon=True, target=self._bgLoop)

    def getManager(self):
        return self.Manager

    def shutdown(self):
        Logger.debug("BLE: QOpExecutor shutdown()")
        self.TimeToExit = True

    def _bgLoop(self):
        while not self.TimeToExit:
            try:
                # Submit to our background single thread
                self.Manager.waitUntilReady(timeout=1.0)
                ble.bgthreadpool.submit(self.Manager.doNextOp)
            except Exception as exc:
                Logger.debug("BLE: EXCEPTION: %s" % (traceback.format_exc(),))

    def startBackgroundProcessing(self):
        """
        Run our ops on our background thread.
        """
        Logger.debug("BLE: startBackgroundProcessing()")
        self.Thread.start()


class QOpExecutorFactory:
    """
    A class that makes a QOpManager and QOpExecutor pair.

    Each BLE device gets its own thread. An executor monitors a queue of QOps
    and executes them.
    """

    def makeExecutor(self) -> QOpExecutor:
        qope = QOpExecutor(QOpManager())
        return qope


class ContextConverter(metaclass=abc.ABCMeta):
    """
    Callbacks are called in the thread context of the BLE stack. This
    is almost certainly not what we want. So, call callbackConvert
    in this class to magically make your callback better.
    """

    @abc.abstractmethod
    def convert(self, callback, *args, **kwargs):
        """
        Return a callback that calls the given callback in the correct context.
        """
        pass


def exceptionCatcherForAsyncDecorator(functowrap):
    """

    This started off as a decorator I found online that makes it easier
    to debug async functions by wrapping them in code so that they
    immediately output exceptions.

    But, it pretty much didn't work for my needs, as I needed to run
    methods from run_coroutine_threadsafe. Fixed and then modified to
    log the output instead.

    Original source:
      https://hackernoon.com/python-async-decorator-to-reduce-debug-woes-nv2dg30q5
    """

    async def deco(*args):
        try:
            return await functowrap(*args)
        except Exception as E:
            Logger.debug("EXCEPTION: %s" % (traceback.format_exc(),))
            raise  # re-raise exception to allow process in calling function

    return deco


def thread_with_callback(convertername):
    """
    Make a decorator that converts a synchronous method into one
    that puts work onto an operation queue and then calls a callback.

    The method must be called with a "callback=foo"
    keyword, although that isn't in the method signature.

    Expects the class holding the method to have
    ContextConverter named by convertername.
    """

    def decorator(method):

        @functools.wraps(method)  # Clones info from wrapped function to improve info in debuggers and traces.
        def method_wrapper(self, *args, **kwargs):
            try:
                callback = kwargs["callback"]
                del kwargs["callback"]
            except KeyError:
                print(
                    "This decorator wraps a function to call a callback once completed. Please provide a callback keyword argument")
                raise

            converter = getattr(self, convertername)
            convertedcallback = converter.convert(callback)
            op = QOp(method, *args, **kwargs, callback=convertedcallback)
            self.QOpManager.addFIFOOp(op)


def wrap_into_QOp(oldmethod):
    """
    Wraps an existing method into a method
    that runs on a background QOp queue
    """

    def decorator(newmethod):

        @functools.wraps(newmethod)  # newmethod is the decorated method
        def newmethodwrapper(self, *args):

            newmethod(self, *args)
            res = queue.SimpleQueue()

            print("Wrapped", newmethod.__name__)

            def cb_wrapper(opr: OpResult):
                res.put(opr, block=False)

            op = QOp(oldmethod, self, *args, callback=cb_wrapper)
            self.QOpExecutor.Manager.addFIFOOp(op)

            try:
                r = res.get(block=True, timeout=self.QOpTimeout)
            except queue.Empty:
                raise BLEOperationTimedOut(
                    "Issued %s returned no results in %s seconds" % (oldmethod.__name__, self.QOpTimeout))

            return r.getResult()

        return newmethodwrapper  # Newmethodwrapper replaces newmethod

    return decorator  # decorator is the function that is called with a method to be replaced
    # wrap_into_qop is the function call used to pass any decorator parameters


def async_wrap_async_into_QOp(oldmethod):
    """
    Wraps an existing async method (newmethod) into a new async method (newmethodwrapper) that
    runs another method (oldmethod) on a background QOp queue.

    Oldmethod can be sync or async.
    """

    def decorator(newmethod):

        @functools.wraps(newmethod)  # newmethod is the decorated method
        async def newmethodwrapper(self, *args):
            try:
                await newmethod(self, *args)
                loop = asyncio.get_running_loop()
                callfuture = loop.create_future()

                # print("async_wrap_async_into_QOp thread: ", threading.current_thread().name)

                def cb_wrapper(opr: OpResult):
                    # Convert the callback from the QOp to the local thread
                    async def set_result():
                        callfuture.set_result(opr)

                    # print("cb_wrapper() thread: ", threading.current_thread().name)
                    asyncio.run_coroutine_threadsafe(set_result(), loop)

                op = QOp(oldmethod, self, *args, callback=cb_wrapper)
                self.QOpExecutor.Manager.addFIFOOp(op)

                try:
                    r = await asyncio.wait_for(callfuture, self.QOpTimeout)
                    print("Finished waiting for future")
                except asyncio.TimeoutError as e:
                    raise BLEOperationTimedOut(
                        "Issued %s returned no results in %s seconds" % (oldmethod.__name__, self.QOpTimeout))

                return r
            except Exception as e:
                Logger.debug(
                    "EXCEPTION: %s(): %s" % ("wrapper for %s" % (newmethod.__name__,), traceback.format_exc(),))
                raise

        return newmethodwrapper  # Newmethodwrapper replaces newmethod

    return decorator  # decorator is the function that is called with a method to be replaced
    # wrap_into_qop is the function call used to pass any decorator parameters
