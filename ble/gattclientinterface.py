from abc import ABC, abstractmethod

from ble.bleops import ContextConverter, QOpManager


class GATTCStates:
    INIT = 0
    CONNECTED = 1
    DISCONNECTED = 2


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

    """

    @abstractmethod
    def __init__(self, macaddress: str, qopmanager: QOpManager, contextconverter: ContextConverter):
        """
        Create an object to talk to a GATT Server. Will not actually do anything
        until connect is called.
        """

    @abstractmethod
    async def async_connect(self):
        """
        Connect
        """

    @abstractmethod
    async def async_char_read(self, uuid):
        """
        Write a characteristic in a background thread and return result when it is done.
        """

    @abstractmethod
    async def async_char_write(self, uuid, data):
        """
        Write a characteristic in a background thread and return result
        """

    # *** Synchronous interface

    @abstractmethod
    def connect(self):
        """
        Blocking connect
        """

    @abstractmethod
    def disconnect(self):
        """
        Block disconnect
        """

    @abstractmethod
    def char_read(self, uuid):
        """
        Synchronous read of a characteristic. Read occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """

    @abstractmethod
    def char_write(self, uuid, data):
        """
        Synchronous (ie. blocking) write of a characteristic. Write
        occurs in a background thread, but the calling thread is made to
        wait until there is a result.
        """

    # *** Callback interface

    @abstractmethod
    def callback_char_read(self, uuid, callback=None):
        """
        Read a characteristic in a background thread and call back with
        an OpResult, which will contain a bytearray.
        """

    @abstractmethod
    def callback_char_write(self, uuid, data, callback=None):
        """
        Write a characteristic in a background thread and call back with
        an OpResult.
        """

    @abstractmethod
    def descriptorWrite(self, uuid, etc):
        pass

    def descriptorRead(self, uuid, etc):
        pass
