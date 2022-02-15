CafeHub's design
----------------

BLE
---

CafeHub uses the Android BLE stack, and the BLEAK BLE stack, meaning that it can
in theory be run on Android, Linux, MacOS and Windows. So far, it has been 
developed on Linux and Android, with partial testing on both.

The Android stack is threaded, with callbacks. BLEAK is based on 
asynchronous cooperative multitasking using asyncio. Async functions in 
Python can only be called by other async functions, meaning that using async 
in one place quickly causes your entire project to be async.

A further complication is that the Android BLE stack is famously fragile and 
poorly written. It's best to only have one operation going through the stack at
a time, and to manually queue any operations yourself.

CafeHub tries to hide all of this complexity. It has both synchronous and 
asynchronous APIs. To do this, it executes all work on background threads 
and translates to whatever the API needs. It tries to ensure that the BLE 
backend only has one operation outstanding at a time.

This requires careful attention to which threads are used for what task. I 
am documenting them here both to help those that come after me, and to help 
keep it straight in my mind too.

Right now, the default implementation is very conservative. Each GATTDevice
runs its own thread for a BLEOpManager, but then each op manager blocks when
submitting to a global background thread. This seems rather absurd, but it
does mean we can easily increase the number of outstanding operations in the
background in the future if this seems stable.


Android
-------
Android executes BLE operations in some unknown background manner, and 
interacts with Java using callbacks. CafeHub uses a Java object to receive 
the calls, and this is wrapped in a python object that queues the callbacks 
in a threadsafe manner. See BluetoothGattCallbackImpl.java and 
pybluetoothgattcallback.py.

All CafeHub BLE operations are submitted to a Queue Operations Manager, 
called a QOpManager. API calls create QOps and pass them to the manager. 
Each QOpManager will run in its own thread. It's not clear to me whether 
there should be exactly one QOpManager per BLE stack, or one per BLE 
device. We don't want to submit parallel operations to Android, but I'm not 
sure if that is per device or in total. So, I have left open the ability to 
do either. TODO: This adds some complications when dealing with disconnects. 
Go back and check that I am dealing with connections well in all cases.

If an operation is async, it will be run by the QOpManager in a background 
thread called 'GlobalBGAsyncThread' (see bgasyncthread.py). Once the 
operation is complete, any results are passed transparently back to the 
asyncio loop that called the API function.

If an operation is synchronous, it will be run in the QOpManager thread, 
named 'QOpExecutorThread'. If it has a callback, the callback is routed 
through a user-provided callback converter that will make sure the callback 
is running in the correct thread or async loop. (Yes, it's possible to 
trigger synchronous operations with a callback, and have the callback 
trigger an async function. This is to ease use in Kivy, as it is basically 
async behind the scenes).
