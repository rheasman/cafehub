import collections

from jnius import PythonJavaClass, java_method
from kivy.logger import Logger

from ble.bleops import CountingSemaphore


class AndroidGATTCodes:
    StatusFromInt = {
        0  : 'GATT_SUCCESS',
        2  : 'GATT_READ_NOT_PERMITTED',
        3  : 'GATT_WRITE_NOT_PERMITTED',
        5  : 'GATT_INSUFFICIENT_AUTHENTICATION',
        6  : 'GATT_REQUEST_NOT_SUPPORTED',
        7  : 'GATT_INVALID_OFFSET',
        13 : 'GATT_INVALID_ATTRIBUTE_LENGTH',
        15 : 'GATT_INSUFFICIENT_ENCRYPTION',
        143: 'GATT_CONNECTION_CONGESTED',
        257: 'GATT_FAILURE'
    }


class AndroidConnStateCodes:
    StateFromInt = {
        0: "STATE_DISCONNECTED",
        1: "STATE_CONNECTING",
        2: "STATE_CONNECTED",
        3: "STATE_DISCONNECTING"
    }


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
    __javainterfaces__ = ['org.decentespresso.dedebug.BluetoothGattCallbackImpl$Interface']
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

        self.QOnConnectionStateChange = collections.deque()
        self.QOnServicesDiscovered = collections.deque()
        self.QOnCharacteristicChanged = collections.deque()
        self.QOnCharacteristicRead = collections.deque()
        self.QOnCharacteristicWrite = collections.deque()
        self.QOnDescriptorRead = collections.deque()
        self.QOnDescriptorWrite = collections.deque()

    def _convertStatusToStr(self, status):
        if status in AndroidGATTCodes.StatusFromInt:
            return AndroidGATTCodes.StatusFromInt[status]

        return "UnknownGATTStatus"

    def _convertConnStateToStr(self, state):
        if state in AndroidConnStateCodes.StateFromInt:
            return AndroidConnStateCodes.StateFromInt[state]

        return "UnknownConnState"

    @java_method("(II)V")
    def onConnectionStateChange(self, status, new_state):
        status = self._convertStatusToStr(status)
        new_state = self._convertConnStateToStr(new_state)
        Logger.debug("BLE: onConnectionStateChange(%s, %s)" % (status, new_state))

        self.QOnConnectionStateChange.appendleft((status, new_state))
        self.SemaOnConnectionStateChange.up()

    @java_method("(I)V")
    def onServicesDiscovered(self, status):
        status = self._convertStatusToStr(status)
        Logger.debug("BLE: onServicesDiscovered(%s)" % (status,))

        self.QOnServicesDiscovered.appendleft(status)
        self.SemaOnServicesDiscovered.up()

    @java_method("(Ljava/lang/String;[B)V")
    def onCharacteristicChanged(self, uuid, value):
        value = bytearray(value)
        Logger.debug("BLE: onCharacteristicChanged(%s, %s)" % (uuid, value))

        self.QOnCharacteristicChanged.appendleft((uuid, value))
        self.SemaOnCharacteristicChanged.up()

    @java_method("(Ljava/lang/String;I[B)V")
    def onCharacteristicRead(self, uuid, status, value):
        status = self._convertStatusToStr(status)
        value = bytearray(value)
        Logger.debug("BLE: onCharacteristicRead(%s, %s, %s)" % (uuid, status, value.hex().upper()))

        self.QOnCharacteristicRead.appendleft((uuid, status, value))
        self.SemaOnCharacteristicRead.up()

    @java_method("(Ljava/lang/String;I)V")
    def onCharacteristicWrite(self, uuid, status):
        status = self._convertStatusToStr(status)
        Logger.debug("BLE: onCharacteristicWrite(%s, %s)" % (uuid, status))

        self.QOnCharacteristicWrite.appendleft((uuid, status))
        self.SemaOnCharacteristicWrite.up()

    @java_method("(Ljava/lang/String;I[B)V")
    def onDescriptorRead(self, uuid, status, value):
        status = self._convertStatusToStr(status)
        Logger.debug("BLE: onDescriptorRead(%s, %s, %s)" % (uuid, status, value))

        self.QOnDescriptorRead.appendleft((uuid, status, value))
        self.SemaOnDescriptorRead.up()

    @java_method("(Ljava/lang/String;I)V")
    def onDescriptorWrite(self, uuid, status):
        status = self._convertStatusToStr(status)
        Logger.debug("BLE: onDescriptorWrite(%s, %s)" % (uuid, status))

        self.QOnDescriptorWrite.appendleft((uuid, status))
        self.SemaOnDescriptorWrite.up()
