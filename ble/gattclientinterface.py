from abc import ABC, abstractmethod
import enum
from typing import Callable, List, Optional
from ble.android.androidtypes import T_Context

from ble.bleops import ContextConverter, OpResult, QOpManager

from enum import Enum

from ble.uuidtype import CHAR_UUID, DESC_UUID

class GATTCState(Enum):
    INIT = 0
    CONNECTED = 1
    DISCONNECTED = 2
    CANCELLED = 3
    CONNECTING = 4
    DISCONNECTING = 5

@enum.unique
class GATTResultCode(enum.IntEnum):
    # These values are derived from the Android stack
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

class GATTClientInterface(ABC):
    """
    A hopefully easy and convenient class to use to communicate with a GATT
    server.

    Optimised for convenience. BLE operations should hopefully happen in the
    background with no drama (which Android makes difficult), and you shouldn't
    need to think too hard to ensure correctness.

    Operations that can be done on a gatt server:

      Connect
      Disconnect
      Characteristic Write
      Characteristic Read
      Descriptor Write
      Descriptor Read
      Mtu Request ??? Not sure
      Set Notify

    """

    @abstractmethod
    def __init__(self, macaddress: str, qopmanager: QOpManager, contextconverter: ContextConverter, androidcontext : Optional[T_Context] = None):
        """
        Create an object to talk to a GATT Server. Will not actually do anything
        until connect is called.

        In android, provide the context in androidcontext
        """

    @abstractmethod
    def set_disc_callback(self, callback: Callable[[GATTCState], None]):
        """
        Set a callback that is called when we receive and unsolicited disconnection.
        See GATTCState.
        """

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shuts down everything. Disconnects everything if necessary.
        """

    @abstractmethod
    def getCharacteristicsUUIDs(self) -> List[str]:
        """
        Returns a list of UUIDs on this device
        """

    @abstractmethod
    async def async_connect(self) -> GATTCState:
        """
        Connect
        """
    
    @abstractmethod
    async def async_disconnect(self)  -> GATTCState:
        """
        Disconnect
        """

    @abstractmethod
    async def async_char_read(self, uuid : CHAR_UUID) -> bytes:
        """
        Write a characteristic in a background thread and return result when it is done.
        """

    @abstractmethod
    async def async_char_write(self, uuid: CHAR_UUID, data : bytes, requireresponse : bool):
        """
        Write a characteristic in a background thread and return result
        """

    # *** Synchronous interface

    @abstractmethod
    def connect(self) -> GATTCState:
        """
        Blocking connect
        """

    @abstractmethod
    def disconnect(self) -> GATTCState:
        """
        Blocking disconnect
        """

    @abstractmethod
    def char_read(self, uuid : CHAR_UUID) -> bytes:
        """
        Synchronous read of a characteristic. Read occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """

    @abstractmethod
    def char_write(self, uuid : CHAR_UUID, data : bytes, requireresponse : bool) -> None:
        """
        Synchronous (i.e. blocking) write of a characteristic. Write
        occurs in a background thread, but the calling thread is made to
        wait until there is a result.
        """

    @abstractmethod
    def descriptor_write(self, charuiid: CHAR_UUID, descuuid: DESC_UUID, data : bytes) -> None:
        """
        Synchronous write to a descriptor. Write occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """

    # *** Callback interface

    @abstractmethod
    def set_notify(self, uuid : CHAR_UUID, enable : bool, notifycallback : Callable[[CHAR_UUID,bytes], None]) -> None:
        """
        Synchronous request to enable/disable notifies on a characteristic.

        The callback will be called when a notification arrives.
        """

    @abstractmethod
    def callback_char_read(self, uuid : CHAR_UUID, callback : Callable[ [OpResult[bytes]], None ]):
        """
        Read a characteristic in a background thread and call back with
        an OpResult, which will contain a 'bytes' object.
        """

    @abstractmethod
    def callback_char_write(self, uuid : CHAR_UUID, data : bytes, requireresponse : bool, callback: Optional[ Callable[[OpResult[None]], None]] = None):
        """
        Write a characteristic in a background thread and call back with
        an OpResult.
        """

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Return true if we are connected
        """
