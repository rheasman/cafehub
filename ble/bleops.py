import abc
import asyncio
import collections
import functools
import inspect
import queue
import threading
import traceback
from typing import Any, Awaitable, Callable, Coroutine, Deque, Generic, TypeVar, Union

from kivy.logger import Logger

from ble.bgasyncthread import run_coroutine_threadsafe
from ble.bleexceptions import *

import ble.bgthreadpool
from queue import Empty

T = TypeVar('T')
class OpResult(Generic[T]):
    def getResult(self) -> T:
        """
        Get a result. If the result is an exception, it raises the exception.
        """
        if hasattr(self, 'Exception'):
            raise self.Exception

        if hasattr(self, 'Result'):
            return self.Result
        else:
            raise Exception("No result or exception set on OpResult")

    def setException(self, e : Exception):
        self.Exception = e

    def setResult(self, r: T):
        self.Result = r


QOpMethod = Union[Callable[..., T], Coroutine[Any, Any, T]];
class QOp(Generic[T]):
    def __init__(self, op : QOpMethod[T], *args : Any, **kwargs : Any):
        """
        Represents an operation.

        When do() is called, Op will be called with manager, args and kwargs.
        If callback is set, then results will be passed to the callback
        """
        self.Op : QOpMethod[T] = op
        self.Args = args
        self.KwArgs = kwargs
        try:
            self.Callback = kwargs['callback']
            del kwargs['callback']
        except IndexError:
            self.Callback = None

    def do(self, manager : 'QOpManager'):
        opr : OpResult[T] = OpResult()
        try:
            Logger.debug("BLE: do() %s" % (repr(self.Op)))
            res : T = self.Op(*self.Args, **self.KwArgs, manager=manager)
            if inspect.isawaitable(res):
                # We might have been passed an async function or method, which means
                # it hasn't actually been run yet. If so we need to run it in the
                # background thread and get the result
                res : T = run_coroutine_threadsafe(res).result()  # type: ignore
            opr.setResult(res)
        except Exception as e:
            Logger.debug("EXCEPTION: do(): %s" % (traceback.format_exc(),))
            opr.setException(e)
        finally:
            manager.signalOpIsDone()

        if callable(self.Callback):
            Logger.debug("BLE: Calling %s" % (repr(self.Callback),))
            self.Callback(opr)

        Logger.debug("BLE: do() done")

    def cancel(self, manager : 'QOpManager', reason : str):
        Logger.debug("BLE: cancel() %s %s" % (manager, reason))
        opr : OpResult[T] = OpResult()

        try:
            res : T = self.Op(*self.Args, **self.KwArgs, manager=manager, reason=reason)
            if inspect.isawaitable(res):
                # We might have been passed an async function or method, which means
                # it hasn't actually been run yet. If so we need to run it in the
                # background thread and get the result
                res : T = run_coroutine_threadsafe(res).result()  # type: ignore
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

    def up(self, *args : Any, **kwargs : Any):
        return self.release(*args, **kwargs)

    def down(self, *args : Any, **kwargs : Any):
        return self.acquire(*args, **kwargs)

def synchronized_with_lock(lock_name : str) -> Callable[ [Callable[..., T]], Callable[..., T] ]:
    """
    Make a locking decorator that will mean that only one method/function
    associated with a lock can be active at a time
    """

    def decorator(method : Callable[..., T]) -> Callable[..., T]:
        def synced_method(self : Any, *args : Any, **kwargs : Any) -> T:
            Logger.debug("BLE: Entering %s" % (method.__name__,))
            lock = getattr(self, lock_name)
            with lock:
                result = method(self, *args, **kwargs)
            
            Logger.debug("BLE: Leaving %s" % (method.__name__,))                
            return result

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
        Logger.debug("BLE: _dumpQ")
        self.Q : Deque[QOp[Any]] = collections.deque()

    @synchronized_with_lock("QLock")
    def cancelQ(self, reason : str):
        """
        Cancels all operations, letting them know that they have been discarded
        and why. They can then do whatever is necessary.

        Cancelled operations can add things back to the queue. New items will be
        executed once the current cancelled items have all been dealt with.
        """
        Logger.debug("BLE: cancelQ() %s" % (reason,))
        cancelleditems = self.Q
        self._dumpQ()

        for i in cancelleditems:
            # Number of cancelled items will be <= OpCount.
            # So this can't lock up
            i.cancel(self, reason)
            self.OpCount.down()

    @synchronized_with_lock("QLock")
    def addFIFOOp(self, op: QOp[Any]):
        """
        Add an item to the back of the queue
        """
        #  Logger.debug("BLE: addFIFOOp: %s %s %s" % (self.QLock, self.OpCount._value, self.OpDone.is_set()))
        self.Q.appendleft(op)
        self.OpCount.up()  # Increment count of things to do
        Logger.debug("BLE: End of addFIFIOp")

    @synchronized_with_lock("QLock")
    def addLIFOOp(self, op: QOp[Any]):
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
        Logger.debug("BLE: signalOpIsDone()")
        self.OpDone.set()  # Operation is now "done"

    def waitUntilReady(self, timeout : Union[float, None] = None):
        self.OpDone.wait(timeout=timeout)

    def doNextOp(self):
        Logger.debug("BLE: doNextOp() %s %s %s" % (self.QLock, self.OpCount._value, self.OpDone.is_set()))  # type: ignore
        self.OpDone.wait()  # Wait until any pending operation is done (set)
        self.OpDone.clear()  # Just about to start new op. Mark it not done (ie. clear)

        Logger.debug("BLE: Sleeping on OpCount")
        self.OpCount.down()  # Sleep until there is something to do
        Logger.debug("BLE: Woke on OpCount")

        # do operation
        try:
            self.Q.pop().do(manager=self)
        except:
            Logger.debug("Exception catchall in doNextOp")

        Logger.debug("BLE: doNextOp() is done")


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
            Logger.debug("BLE: Loop!")
            try:
                # Submit to our background single thread
                self.Manager.waitUntilReady()
                ble.bgthreadpool.submit(self.Manager.doNextOp)
            except Exception:
                Logger.debug("BLE: EXCEPTION: %s" % (traceback.format_exc(),))
        Logger.debug("QOpExecutor: Exited _bgLoop")

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
    def convert(self, callback : Union[Callable[..., T], None], *args : Any, **kwargs : Any) -> Callable[..., T]:
        """
        Return a callback that calls the given callback in the correct context.
        """
        pass


def exceptionCatcherForAsyncDecorator(functowrap: Callable[..., Awaitable[Any]]):
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

    async def deco(*args: Any):
        try:
            return await functowrap(*args)
        except Exception:
            Logger.debug("EXCEPTION: %s" % (traceback.format_exc(),))
            raise  # re-raise exception to allow process in calling function

    return deco


# def thread_with_callback(convertername):
#     """
#     Make a decorator that converts a synchronous method into one
#     that puts work onto an operation queue and then calls a callback.

#     The method must be called with a "callback=foo"
#     keyword, although that isn't in the method signature.

#     Expects the class holding the method to have
#     ContextConverter named by convertername.
#     """

#     def decorator(method):

#         @functools.wraps(method)  # Clones info from wrapped function to improve info in debuggers and traces.
#         def method_wrapper(self, *args, **kwargs):
#             try:
#                 callback = kwargs["callback"]
#                 del kwargs["callback"]
#             except KeyError:
#                 print(
#                     "This decorator wraps a function to call a callback once completed. Please provide a callback keyword argument")
#                 raise

#             converter = getattr(self, convertername)
#             convertedcallback = converter.convert(callback)
#             op = QOp(method, *args, **kwargs, callback=convertedcallback)
#             self.QOpManager.addFIFOOp(op)

def wrap_into_QOp(actualmethod : Callable[..., T]) -> Callable[[Callable[..., Any]], Callable[..., T]]:
    """
    Wraps an existing method into a method
    that runs on a background QOp queue
    """

    # def decorator(newmethod : Callable[P, None]) -> Callable[P, T]:

    def decorator(newmethod : Callable[..., Any]) -> Callable[..., T]:
        # print("wiQ: decorator: ", actualmethod, newmethod)

        @functools.wraps(newmethod)  # newmethod is the decorated method
        def newmethodwrapper(self : Any, *args : Any, **kwargs: Any) -> T:

            newmethod(self, *args, **kwargs)
            res : queue.SimpleQueue[OpResult[T]] = queue.SimpleQueue()

            # print("Wrapped", newmethod.__name__)

            def cb_wrapper(opr: OpResult[T]):
                res.put(opr, block=False)

            op = QOp(actualmethod, self, *args, callback=cb_wrapper)
            self.QOpExecutor.Manager.addFIFOOp(op)

            try:
                r = res.get(block=True, timeout=self.QOpTimeout)
            except Empty:
                raise BLEOperationTimedOut(
                    "Issued %s returned no results in %s seconds" % (actualmethod.__name__, self.QOpTimeout)
                )

            return r.getResult()

        return newmethodwrapper  # Newmethodwrapper replaces newmethod

    return decorator  # decorator is the function that is called with a method to be replaced
    # wrap_into_qop is the function call used to pass any decorator parameters


def async_wrap_async_into_QOp(actualmethod):
    """
    Wraps an existing async method (newmethod) into a new async method (newmethodwrapper) that
    runs another method (actualmethod) on a background QOp queue.

    Oldmethod can be sync or async.

    To make it clear what is happening here:
        Example :   @async_wrap_async_into_QOp(_set_notify)
                    async def async_set_notify(self, uuid, enable, callback) -> None:

        "actualmethod" is the method passed to the decorator. i.e. _set_notify
        "newmethod" is the method being wrapped. i.e. async_set_notify

        First, the "newmethod" being wrapped is run. This is basically so it can generate
        log output or do anything that has to happen before an operation is queued.

        Then a QOP is created and passed to the background thread that runs async operations.
        Then it waits for a result, and either times out, or returns the result.
        The result is passed back via a callback which, in a threadsafe way, pushes the result
        back to the wrapper.
    """

    def decorator(newmethod):

        @functools.wraps(newmethod)  # newmethod is the decorated method
        async def newmethodwrapper(self, *args) -> OpResult:
            try:
                await newmethod(self, *args)
                loop = asyncio.get_running_loop()
                callfuture : asyncio.Future[OpResult] = loop.create_future()

                # print("async_wrap_async_into_QOp thread: ", threading.current_thread().name)

                def cb_wrapper(opr: OpResult) -> None:
                    # Convert the callback from the QOp to the local thread
                    async def set_result():
                        callfuture.set_result(opr)

                    # print("cb_wrapper() thread: ", threading.current_thread().name)
                    asyncio.run_coroutine_threadsafe(set_result(), loop)

                op = QOp(actualmethod, self, *args, callback=cb_wrapper)
                self.QOpExecutor.Manager.addFIFOOp(op)

                try:
                    r = await asyncio.wait_for(callfuture, self.QOpTimeout)
                    # print("Finished waiting for future")
                except asyncio.TimeoutError as e:
                    raise BLEOperationTimedOut(
                        "Issued %s returned no results in %s seconds" % (actualmethod.__name__, self.QOpTimeout))

                return r
            except Exception as e:
                Logger.debug(
                    "EXCEPTION: %s(): %s" % ("wrapper for %s" % (newmethod.__name__,), traceback.format_exc(),))
                raise

        return newmethodwrapper  # Newmethodwrapper replaces newmethod

    return decorator  # decorator is the function that is called with a method to be replaced
    # wrap_into_qop is the function call used to pass any decorator parameters
