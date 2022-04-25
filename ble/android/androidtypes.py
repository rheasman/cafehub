from enum import Enum
from typing import Any, Generic, List, Protocol, TypeVar
from xmlrpc.client import boolean

from jnius import PythonJavaClass

"""
    NOTE: THIS ENTIRE FILE IS JUST TO KEEP THE TYPECHECKER HAPPY

    This file adds types so that PyLance is happy with the Android gatt client implementation.

    This should make it easier for the unfamiliar to edit this code, because the typechecker will tell them
    if they're making a mistake.

    None of this code is executed. It just hints to the checker what types the Android Java classes are expecting
"""
class T_Logger(Protocol):
    def debug(self, s: str) -> None:
        ...

class T_BluetoothGattDescriptor(Protocol):
    ENABLE_NOTIFICATION_VALUE : bytes
    DISABLE_NOTIFICATION_VALUE : bytes

    def setValue(self, data: bytes) -> None:
        ...

T = TypeVar('T')
class T_JavaListOf(Protocol, Generic[T]):
    def toArray(self) -> List[T]:
        ...

class T_Java_String(Protocol):
    ...

class T_Java_UUID(Protocol):
    def toString(self) -> str:
        ...

    def fromString(self, s: str) -> 'T_Java_UUID':
        ...

class T_ScanRecord(Protocol):
    def getDeviceName(self) -> str:
        ...        
    def getServiceUuids(self) -> T_JavaListOf[T_Java_UUID]:
        ...

class T_ScanResult(Protocol):
    device : 'T_BluetoothDevice'
    def getDevice(self) -> 'T_BluetoothDevice':
        ...
    def getScanRecord(self) -> T_ScanRecord:
        ...

class T_ScanCallback(Protocol):
    SCAN_FAILED_ALREADY_STARTED = 1
    SCAN_FAILED_APPLICATION_REGISTRATION_FAILED = 2
    SCAN_FAILED_FEATURE_UNSUPPORTED = 4
    SCAN_FAILED_INTERNAL_ERROR = 3
    def onBatchScanResults(self, results: T_JavaListOf[T_ScanResult]) -> None:
        ...
    def onScanFailed(self, errorCode: int) -> None:
        ...
    def onScanResult(self, callbackType: int, result: T_ScanResult) -> None:
        ...

class T_ScanCallbackImpl(T_ScanCallback, Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> 'T_ScanCallbackImpl':
        ...

    def setImpl(self, impl: T_ScanCallback) -> None:
        ...

class T_BluetoothLeScanner(Protocol):
    def startScan(self, scancb : T_ScanCallback) -> None:
        ...
    def stopScan(self, scancb : T_ScanCallback) -> None:
        ...

class T_BluetoothGattCharacteristic(Protocol):
    WRITE_TYPE_NO_RESPONSE : int
    WRITE_TYPE_DEFAULT : int
    def getUuid(self) -> T_Java_UUID:
        ...

    def setValue(self, data: bytes) -> None:
        ...

    def setWriteType(self, type: int) -> None:
        ...

    def getDescriptor(self, uuid: T_Java_UUID) -> T_BluetoothGattDescriptor:
        ...

class T_BluetoothClassicAdapter(Protocol):
    def cancelDiscovery(self):
        pass
    def isEnabled(self) -> bool:
        ...

class T_Context(Protocol):
    pass

class T_BluetoothGattService(Protocol):
    def getUuid(self) -> T_Java_UUID:
        ...

    def getCharacteristics(self) -> T_JavaListOf[T_BluetoothGattCharacteristic]:
        ...


class T_BluetoothGatt(Protocol):
    def discoverServices(self) -> boolean:
        ...

    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def close(self) -> None:
        ...

    def setCharacteristicNotification(self, char: Any, enable : bool) -> bool:
        ...

    def getServices(self) -> T_JavaListOf[T_BluetoothGattService]:
        ...

    def readCharacteristic(self, char : T_BluetoothGattCharacteristic) -> bool:
        ...

    def writeCharacteristic(self, char: T_BluetoothGattCharacteristic) -> bool:
        ...

    def writeDescriptor(self, desc: T_BluetoothGattDescriptor) -> bool:
        ...

class T_BluetoothGattCallbackImpl(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> 'T_BluetoothGattCallbackImpl':
        ...
    
    def setImpl(self, impl : PythonJavaClass) -> None:
        ...

class T_BluetoothDevice(Protocol):
    def getAddress(self) -> str:
        ...

    def connectGatt(self, context : T_Context, autoconnect: bool, cbimpl : T_BluetoothGattCallbackImpl) -> T_BluetoothGatt:
        ...

class T_BluetoothAdapter(T_BluetoothClassicAdapter, Protocol):
    ACTION_REQUEST_ENABLE : str
    def getDefaultAdapter(self) -> 'T_BluetoothAdapter':
        ...

    def getRemoteDevice(self, mac : List[int]) -> T_BluetoothDevice:
        ...

    def getBluetoothLeScanner(self) -> T_BluetoothLeScanner:
        ...

# class T_JNIUS_Initable(Protocol):
#     def __call__(self, *args: Any, **kwds: Any) -> 'T_JNIUS_Initable':
#         ...

class T_Intent(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> 'T_Intent':
        ...

    def setAction(self, s : str)->None:
        ...

class T_Activity(T_Context, Protocol):
    def startActivityForResult(self, intent : T_Intent, result : int, options : Any = None) -> None:
        ...

class T_PythonActivity(Protocol):
    mActivity : T_Activity
    pass

class T_Native_Invocation_Handler(Protocol):
    pass

