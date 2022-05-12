import collections
import enum
from typing import Deque, Iterable, Tuple

from jnius import PythonJavaClass, java_method  # type: ignore
from kivy.logger import Logger

from ble.bleops import CountingSemaphore
from ble.gattclientinterface import GATTCState

@enum.unique
class AndroidGATTStatus(enum.IntEnum):
    GATT_SUCCESS = 0
    GATT_READ_NOT_PERMITTED = 2
    GATT_WRITE_NOT_PERMITTED = 3
    GATT_INSUFFICIENT_AUTHENTICATION = 5
    GATT_REQUEST_NOT_SUPPORTED = 6
    GATT_INVALID_OFFSET = 7
    GATT_INVALID_ATTRIBUTE_LENGTH = 13
    GATT_INSUFFICIENT_ENCRYPTION = 15
    GATT_CONNECTION_CONGESTED = 143
    GATT_FAILURE = 257

class AndroidConnStateCodes:
    StateFromInt = {
        0: "STATE_DISCONNECTED",
        1: "STATE_CONNECTING",
        2: "STATE_CONNECTED",
        3: "STATE_DISCONNECTING"
    }

ConversionFromACSToGCS = {
     0 : GATTCState.DISCONNECTED,
     1 : GATTCState.CONNECTING,
     2 : GATTCState.CONNECTED,
     3 : GATTCState.DISCONNECTING
}

class AndroidConnState(enum.IntEnum):
    STATE_DISCONNECTED = 0
    STATE_CONNECTING = 1
    STATE_CONNECTED = 2
    STATE_DISCONNECTING = 3
    
    def asGATTCState(self) -> GATTCState:
        return ConversionFromACSToGCS[self.value]

class PyBluetoothGattCallback(PythonJavaClass):
    """
    Worker class for GATT Client. Not to be used by anything else.

    The Dalvik VM in Android makes it impossible to write a python proxy class
    that inherits from partially abstract classes. Unfortunately, some
    callbacks in Android are implemented this way.

    So, we have to have a Java wrapper that holds an interface with the same
    methods as the abstract class. Then we can implement the interface in
    Python, and pass it to the Java wrapper.
    """
    __javainterfaces__ = ['org.decentespresso.cafehub.BluetoothGattCallbackImpl$Interface']
    __javacontext__ = 'app'  # Use the app class resolver, not the system resolver.

    def __init__(self):
        super().__init__()
        Logger.debug("BLE: PyBluetoothGattCallback.__init__()")


        self.SemaOnConnectionStateChange = CountingSemaphore(value=0)
        self.SemaOnServicesDiscovered = CountingSemaphore(value=0)
        self.SemaOnCharacteristicChanged = CountingSemaphore(value=0)
        self.SemaOnCharacteristicRead = CountingSemaphore(value=0)
        self.SemaOnCharacteristicWrite = CountingSemaphore(value=0)
        self.SemaOnDescriptorRead = CountingSemaphore(value=0)
        self.SemaOnDescriptorWrite = CountingSemaphore(value=0)

        self.QOnConnectionStateChange : Deque[Tuple[AndroidGATTStatus, AndroidConnState]] = collections.deque()
        self.QOnServicesDiscovered : Deque[AndroidGATTStatus] = collections.deque()
        self.QOnCharacteristicChanged : Deque[Tuple[str, bytearray]] = collections.deque()
        self.QOnCharacteristicRead : Deque[Tuple[str, AndroidGATTStatus, bytearray]] = collections.deque()
        self.QOnCharacteristicWrite : Deque[Tuple[str, AndroidGATTStatus]] = collections.deque()
        self.QOnDescriptorRead : Deque[Tuple[str, AndroidGATTStatus, bytearray]] = collections.deque()
        self.QOnDescriptorWrite : Deque[Tuple[str, AndroidGATTStatus]] = collections.deque()

    @java_method("(II)V")
    def onConnectionStateChange(self, status : int, new_state : int) -> None:
        status = AndroidGATTStatus(status)
        new_state = AndroidConnState(new_state)
        Logger.debug("BLE: onConnectionStateChange(%s, %s)" % (status, new_state))

        self.QOnConnectionStateChange.appendleft((status, new_state))
        self.SemaOnConnectionStateChange.up()

    @java_method("(I)V")
    def onServicesDiscovered(self, status : int) -> None:
        status = AndroidGATTStatus(status)
        Logger.debug("BLE: onServicesDiscovered(%s)" % (status,))

        self.QOnServicesDiscovered.appendleft(status)
        self.SemaOnServicesDiscovered.up()

    @java_method("(Ljava/lang/String;[B)V")
    def onCharacteristicChanged(self, uuid : str, value : Iterable[int]) -> None:
        value = bytearray(value)
        Logger.debug("BLE: onCharacteristicChanged(%s, %s)" % (uuid, value))

        self.QOnCharacteristicChanged.appendleft((uuid, value))
        self.SemaOnCharacteristicChanged.up()

    @java_method("(Ljava/lang/String;I[B)V")
    def onCharacteristicRead(self, uuid : str, status : int, value : Iterable[int]) -> None:
        status = AndroidGATTStatus(status)
        value = bytearray(value)
        Logger.debug("BLE: onCharacteristicRead(%s, %s, %s)" % (uuid, status, value.hex().upper()))

        self.QOnCharacteristicRead.appendleft((uuid, status, value))
        self.SemaOnCharacteristicRead.up()

    @java_method("(Ljava/lang/String;I)V")
    def onCharacteristicWrite(self, uuid : str, status : int) -> None:
        status = AndroidGATTStatus(status)
        Logger.debug("BLE: onCharacteristicWrite(%s, %s)" % (uuid, status))

        self.QOnCharacteristicWrite.appendleft((uuid, status))
        self.SemaOnCharacteristicWrite.up()

    @java_method("(Ljava/lang/String;I[B)V")
    def onDescriptorRead(self, uuid : str, status : int, value : Iterable[int]) -> None:
        status = AndroidGATTStatus(status)
        value = bytearray(value)
        Logger.debug("BLE: onDescriptorRead(%s, %s, %s)" % (uuid, status, value))

        self.QOnDescriptorRead.appendleft((uuid, status, value))
        self.SemaOnDescriptorRead.up()

    @java_method("(Ljava/lang/String;I)V")
    def onDescriptorWrite(self, uuid : str, status : int) -> None:
        status = AndroidGATTStatus(status)
        Logger.debug("BLE: onDescriptorWrite(%s, %s)" % (uuid, status))

        self.QOnDescriptorWrite.appendleft((uuid, status))
        self.SemaOnDescriptorWrite.up()
