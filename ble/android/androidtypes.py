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
        raise NotImplementedError

class T_BluetoothGattDescriptor(Protocol):
    ENABLE_NOTIFICATION_VALUE : bytes
    DISABLE_NOTIFICATION_VALUE : bytes

    def setValue(self, data: bytes) -> None:
        raise NotImplementedError

T = TypeVar('T')
class T_JavaListOf(Protocol, Generic[T]):
    def toArray(self) -> List[T]:
        raise NotImplementedError

class T_Java_UUID(Protocol):
    def toString(self) -> str:
        raise NotImplementedError

    def fromString(self, s: str) -> 'T_Java_UUID':
        raise NotImplementedError

class T_BluetoothGattCharacteristic(Protocol):
    WRITE_TYPE_NO_RESPONSE : int
    WRITE_TYPE_DEFAULT : int
    def getUuid(self) -> T_Java_UUID:
        raise NotImplementedError

    def setValue(self, data: bytes) -> None:
        raise NotImplementedError

    def setWriteType(self, type: int) -> None:
        raise NotImplementedError

    def getDescriptor(self, uuid: T_Java_UUID) -> T_BluetoothGattDescriptor:
        raise NotImplementedError

class T_BluetoothClassicAdapter(Protocol):
    def cancelDiscovery(self):
        pass
    def isEnabled(self) -> bool:
        raise NotImplementedError

class T_Context(Protocol):
    pass

class T_BluetoothGattService(Protocol):
    def getUuid(self) -> T_Java_UUID:
        raise NotImplementedError

    def getCharacteristics(self) -> T_JavaListOf[T_BluetoothGattCharacteristic]:
        raise NotImplementedError


class T_BluetoothGatt(Protocol):
    def discoverServices(self) -> boolean:
        raise NotImplementedError

    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def setCharacteristicNotification(self, char: Any, enable : bool) -> bool:
        raise NotImplementedError

    def getServices(self) -> T_JavaListOf[T_BluetoothGattService]:
        raise NotImplementedError

    def readCharacteristic(self, char : T_BluetoothGattCharacteristic) -> bool:
        raise NotImplementedError

    def writeCharacteristic(self, char: T_BluetoothGattCharacteristic) -> bool:
        raise NotImplementedError

    def writeDescriptor(self, desc: T_BluetoothGattDescriptor) -> bool:
        raise NotImplementedError

class T_BluetoothGattCallbackImpl(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> 'T_BluetoothGattCallbackImpl':
        raise NotImplementedError
    
    def setImpl(self, impl : PythonJavaClass) -> None:
        raise NotImplementedError

class T_BluetoothDevice(Protocol):
    def connectGatt(self, context : T_Context, autoconnect: bool, cbimpl : T_BluetoothGattCallbackImpl) -> T_BluetoothGatt:
        raise NotImplementedError

class T_BluetoothAdapter(Protocol):
    ACTION_REQUEST_ENABLE : str
    def getDefaultAdapter(self) -> 'T_BluetoothAdapter':
        raise NotImplementedError

    def getRemoteDevice(self, mac : List[int]) -> T_BluetoothDevice:
        raise NotImplementedError

# class T_JNIUS_Initable(Protocol):
#     def __call__(self, *args: Any, **kwds: Any) -> 'T_JNIUS_Initable':
#         raise NotImplementedError

class T_Intent(Protocol):
    def __call__(self, *args: Any, **kwds: Any) -> 'T_Intent':
        raise NotImplementedError

    def setAction(self, s : str)->None:
        raise NotImplementedError

class T_Activity(T_Context, Protocol):
    def startActivityForResult(self, intent : T_Intent, result : int, options : Any = None) -> None:
        raise NotImplementedError

class T_PythonActivity(Protocol):
    mActivity : T_Activity
    pass

class T_Java_String(Protocol):
    pass

class T_Native_Invocation_Handler(Protocol):
    pass

