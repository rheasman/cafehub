from typing import Callable, List, Optional, Union

from bleak import BleakClient  # type: ignore
from bleak.exc import BleakError
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.client import BaseBleakClient
from bleak.backends.service import BleakGATTServiceCollection
from kivy.logger import Logger

from ble.bleops import ContextConverter, QOp, QOpExecutor, QOpManager, async_wrap_async_into_QOp, wrap_into_QOp
from ble.gattclientinterface import GATTClientInterface, GATTCState
from ble.bleexceptions import *
from ble.uuidtype import CHAR_UUID, DESC_UUID


class GATTClient(GATTClientInterface):
    """
    A hopefully easy and convenient class to use to communicate with a GATT
    server.

    Optimised for convenience. BLE operations should happen in the
    background with no drama (which Android makes difficult), and you shouldn't
    need to think too hard to ensure correctness.

    Operations that can be done on a gatt server:

      Connect
      Disconnect
      CharacteristicWrite
      CharacteristicRead
      DescriptorWrite
      DescriptorRead
      MtuRequest

    """

    def __init__(self, macaddress: str, qopexecutor: QOpExecutor, contextconverter: ContextConverter):
        Logger.debug("BLE: ble.bleak.GATTClient.__init__(%s, %s, %s)" % (macaddress, qopexecutor, contextconverter))
        self.MAC = macaddress
        self.BleakClient : BaseBleakClient = BleakClient(self.MAC)

        self.State = GATTCState.INIT
        self.QOpExecutor = qopexecutor  # Holds a queue of operations that are run in their own thread
        self.QOpExecutor.startBackgroundProcessing()

        self.CBConverter = contextconverter  # Used to convert callbacks out of the background thread

        self.QOpTimeout = 10
        self.ConnCallback = None

    def __del__(self):
        Logger.debug("BLE: __del__() on bleak variant of GATTClient %s" % (self.MAC,))

    def shutdown(self):
        self.QOpExecutor.shutdown()

    def getCharacteristicsUUIDs(self) -> List[str]:
        return list(self.Characteristics.keys())

    def set_disc_callback(self, callback: Callable[[GATTCState], None]):
        """
        Set a callback that is called when an unsolicited disconnection occurs.

        Use None as a callback to disable the callback

        For now there is only one callback, as I am assuming one user for a gattclient.
        """
        self.ConnCallback = callback

        def disc_cb(client : BaseBleakClient) -> None:
            # Called by BLEAK when a disconnect occurs
            Logger.debug("BLE: Unsolicited disconnect from %s" % (client.address,))
            if self.ConnCallback:
                self.ConnCallback(GATTCState.DISCONNECTED)

        self.BleakClient.set_disconnected_callback(disc_cb)

    # Most operations are available in 3 different flavours:
    # asynchronous, callback, and synchronous. All operations are run on
    # a background thread. My personal preference is to use the
    # synchronous and callback functions, in a ThreadProcessPool if
    # necessary, but we're trying to accommodate everybody.

    # A context converter can be used to move a callback from one thread
    # to another, or from one async loop to another.

    # *** Internal functions. No touchy!

    async def _connect(self, manager : Optional[QOpManager] = None, reason : Optional[str] = None) -> GATTCState:
        Logger.debug("BLE: GATTClient.connect() to '%s'" % self.MAC)

        if reason is not None:
            # We've been told to cancel, so do nothing
            return GATTCState.CANCELLED

        try:
            # Next line of code is a hack to circumvent a BLEAK bug. See https://github.com/hbldh/bleak/issues/376
            # Clear the list of services associated with a peripheral, to stop intermittent exceptions
            # that complain that the list already has entries.
            self.BleakClient.services = BleakGATTServiceCollection()

            connected = await self.BleakClient.connect()
        except BleakError as be:
            Logger.debug("BLE: Exception while attempting to connect")
            raise BLEConnectionError(getattr(be, 'message', repr(be)))

        if not connected:
            return GATTCState.DISCONNECTED

        if not hasattr(self, "Characteristics"):
            # Discover our services on first connect. Remember them so we don't do this for reconnects.
            self.BleakGATTServiceCollection = await self.BleakClient.get_services()

            self.Characteristics : dict[str, BleakGATTCharacteristic] = {}
            for serv in self.BleakGATTServiceCollection:
                for char in serv.characteristics:
                    uuidstr = char.uuid
                    self.Characteristics[uuidstr] = char
                    Logger.debug("BLE: Service UUID %s = %s" % (uuidstr, char))

        return GATTCState.CONNECTED

    async def _disconnect(self, manager: Union[QOpManager, None], reason: Union[str, None]) -> GATTCState:
        if reason is not None:
            # We've been told to cancel, so do nothing
            return GATTCState.CANCELLED

        boolresult = await self.BleakClient.disconnect()
        if boolresult:
            # API doc is unclear. I think True = Disconnect succeeded (Docs say it's the connection state)
            return GATTCState.DISCONNECTED
        else:
            return GATTCState.CONNECTED

    async def _char_write(self, manager: Union[QOpManager, None], reason: Union[str, None], uuid : CHAR_UUID, data : bytes):
        Logger.debug("BLE: _char_writed(%s, %s, manager=%s, reason=%s)" % (uuid, data.hex(), manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_write() cancelled before execution. Reason: %s" % (reason,))

        r = await self.BleakClient.write_gatt_char(uuid.AsString, data)
        Logger.debug("BLE: _char_write result: %s" % (r,))
        return r

    async def _char_read(self, manager: Union[QOpManager, None], reason: Union[str, None], uuid : CHAR_UUID) -> bytearray:
        Logger.debug("BLE: _char_read(%s, manager=%s, reason=%s)" % (uuid, manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_read() cancelled before execution. Reason: %s" % (reason,))

        r = await self.BleakClient.read_gatt_char(uuid.AsString)
        Logger.debug("BLE: _char_read result: %s" % (r,))
        return r

    async def _set_notify(self, manager: Union[QOpManager, None], reason: Union[str, None], uuid : CHAR_UUID, enable : bool, notifycallback : Callable[[CHAR_UUID, bytes], None]) -> None:
        Logger.debug("BLE: _set_notify(%s, %s, %s, %s, %s)" % (uuid, enable, notifycallback, manager, reason))

        def do_cb(sender: int, data: bytearray):
            # We want our callback to work with anything, not just bleak, so pass back the original UUID
            notifycallback(uuid, data)

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _set_notify() cancelled before execution. Reason: %s" % (reason,))

        if enable:
            await self.BleakClient.start_notify(uuid.AsString, do_cb)
        else:
            await self.BleakClient.stop_notify(uuid.AsString)

    # *** Async interface

    @async_wrap_async_into_QOp(_set_notify)
    async def async_set_notify(self, uuid : CHAR_UUID, enable : bool, callback : Callable[[CHAR_UUID, bytes], None]) -> None:
        """
        Set notify on or off
        """
        Logger.debug("BLE: async_set_notify")

    @async_wrap_async_into_QOp(_connect)  # Returns OPResult containing GATTCState
    async def async_connect(self):
        """
        Connect
        """
        Logger.debug("BLE: async_connect(%s)" % (self.MAC,))

    @async_wrap_async_into_QOp(_disconnect)  # Returns OPResult containing GATTCState
    async def async_disconnect(self):
        """
        Disconnect
        """
        Logger.debug("BLE: async_disconnect(%s)" % (self.MAC,))

    @async_wrap_async_into_QOp(_char_read)
    async def async_char_read(self, uuid : CHAR_UUID):
        """
        Write a characteristic in a background thread and return result when it is done.
        """
        Logger.debug("BLE: async_char_read(%s)" % (uuid,))

    @async_wrap_async_into_QOp(_char_write)
    async def async_char_write(self, uuid : CHAR_UUID, data : bytes, requireresponse : bool):
        """
        Write a characteristic in a background thread and return result
        """
        Logger.debug("BLE: async_char_write(%s, %s, %s)" % (uuid, data, requireresponse))

    # *** Synchronous interface

    @wrap_into_QOp(_connect)
    def connect(self) -> GATTCState:
        """
        Blocking connect
        """
        Logger.debug("BLE: connect to %s" % (self.MAC,))
        return GATTCState.DISCONNECTED

    @wrap_into_QOp(_disconnect)
    def disconnect(self):
        """
        Blocking disconnect
        """
        Logger.debug("BLE: disconnect from %s" % (self.MAC,))

    @wrap_into_QOp(_char_read)
    def char_read(self, uuid : CHAR_UUID):
        """
        Synchronous read of a characteristic. Read occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        Logger.debug("BLE: char_read(%s)" % (uuid,))

    @wrap_into_QOp(_char_write)
    def char_write(self, uuid : CHAR_UUID, data) -> None:
        """
        Synchronous (i.e. blocking) write of a characteristic. Write
        occurs in a background thread, but the calling thread is made to
        wait until there is a result.
        """
        Logger.debug("BLE: char_write(%s, %s)" % (uuid, data))

    @wrap_into_QOp(_set_notify)
    def set_notify(self, uuid : CHAR_UUID, enable : bool, notifycallback) -> None:
        """
        Synchronous request to enable/disable notifies on a characteristic.
        """
        Logger.debug("BLE: set_notify(%s, %s, %s)" % (uuid, enable, notifycallback))

    def descriptor_write(self, charuiid: CHAR_UUID, descuuid: DESC_UUID, data : bytes) -> None:
        """
        Synchronous write to a descriptor. Write occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        raise NotImplementedError()

    # *** Callback interface

    def callback_char_read(self, uuid : CHAR_UUID, callback=None):
        """
        Read a characteristic in a background thread and call back with
        an OpResult, which will contain a bytearray.
        """
        Logger.debug("BLE: callback_char_read(%s, %s)" % (uuid, callback))
        op = QOp(self._char_read, uuid, callback=self.CBConverter.convert(callback))
        self.QOpExecutor.Manager.addFIFOOp(op)

    def callback_char_write(self, uuid : CHAR_UUID, data : bytes, requireresponse : bool, callback=None):
        """
        Write a characteristic in a background thread and call back with
        an OpResult.
        """
        Logger.debug("BLE: callback_char_write(%s, %s)" % (uuid, data))
        op = QOp(self._char_write, uuid, data, requireresponse, callback=self.CBConverter.convert(callback))
        self.QOpExecutor.Manager.addFIFOOp(op)

    def is_connected(self) -> bool:
        return self.BleakClient.is_connected
