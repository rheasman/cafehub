from bleak import BleakClient
from kivy.logger import Logger

from ble.bleops import ContextConverter, QOp, QOpExecutor, async_wrap_async_into_QOp, wrap_into_QOp
from ble.gattclientinterface import GATTClientInterface


class GATTCStates:
    INIT = 0
    CONNECTED = 1
    DISCONNECTED = 2


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
        Logger.debug("ble.bleak.GATTClient.__init__(%s, %s, %s)" % (macaddress, qopexecutor, contextconverter))
        self.MAC = macaddress
        self.BleakClient = BleakClient(self.MAC)

        self.State = GATTCStates.INIT
        self.QOpExecutor = qopexecutor  # Holds a queue of operations that are run in their own thread
        self.QOpExecutor.startBackgroundProcessing()

        self.CBConverter = contextconverter  # Used to convert callbacks out of the background thread

        self.QOpTimeout = 30

    def __del__(self):
        Logger.debug("BLE: sending disconnect to %s" % (self.MAC,))
        self.disconnect()

    # Most operations are available in 3 different flavours:
    # asynchronous, callback, and synchronous. All operations are run on
    # a background thread. My personal preference is to use the
    # synchronous and callback functions, in a ThreadProcessPool if
    # necessary, but we're trying to accommodate everybody.

    # A context converter can be used to move a callback from one thread
    # to another, or from one async loop to another.

    # *** Internal functions. No touchy!

    async def _connect(self, manager=None, reason=None):
        Logger.debug("BLE: GATTClient.connect() to '%s'" % self.MAC)

        if reason is not None:
            # We've been told to cancel, so do nothing
            return

        await self.BleakClient.connect()

        if not hasattr(self, "Characteristics"):
            # Discover our services on first connect. Remember them so we don't do this for reconnects.
            self.BleakGATTServiceCollection = await self.BleakClient.get_services()

            self.Characteristics = {}
            for serv in self.BleakGATTServiceCollection:
                for char in serv.characteristics:
                    uuidstr = char.uuid
                    self.Characteristics[uuidstr] = char
                    Logger.debug("BLE: Service UUID %s = %s" % (uuidstr, char))

        return

    async def _disconnect(self, manager=None, reason=None):
        if reason is not None:
            # We've been told to cancel, so do nothing
            return

        return await self.BleakClient.disconnect()

    async def _char_write(self, uuid, data, manager=None, reason=None):
        Logger.debug("BLE: _char_writed(%s, %s, manager=%s, reason=%s)" % (uuid, data, manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_write() cancelled before execution. Reason: %s" % (reason,))

        r = await self.BleakClient.write_gatt_char(uuid, data)
        Logger.debug("BLE: _char_write result: %s" % (r,))
        return r

    async def _char_read(self, uuid, manager=None, reason=None) -> bytearray:
        Logger.debug("BLE: _char_read(%s, manager=%s, reason=%s)" % (uuid, manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_read() cancelled before execution. Reason: %s" % (reason,))

        r = await self.BleakClient.read_gatt_char(uuid)
        Logger.debug("BLE: _char_read result: %s" % (r,))
        return r

    # *** Async interface

    @async_wrap_async_into_QOp(_connect)
    async def async_connect(self):
        """
        Connect
        """
        Logger.debug("BLE: async_connect(%s)" % (self.MAC,))

    @async_wrap_async_into_QOp(_char_read)
    async def async_char_read(self, uuid):
        """
        Write a characteristic in a background thread and return result when it is done.
        """
        Logger.debug("BLE: async_char_read(%s)" % (uuid,))

    @async_wrap_async_into_QOp(_char_write)
    async def async_char_write(self, uuid, data):
        """
        Write a characteristic in a background thread and return result
        """
        Logger.debug("BLE: async_char_write(%s, %s)" % (uuid, data))

    # *** Synchronous interface

    @wrap_into_QOp(_connect)
    def connect(self):
        """
        Blocking connect
        """
        Logger.debug("BLE: connect to %s" % (self.MAC,))
        self.disconnect()

    @wrap_into_QOp(_disconnect)
    def disconnect(self):
        """
        Block disconnect
        """
        Logger.debug("BLE: disconnect from %s" % (self.MAC,))

    @wrap_into_QOp(_char_read)
    def char_read(self, uuid):
        """
        Synchronous read of a characteristic. Read occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        Logger.debug("BLE: char_read(%s)" % (uuid,))

    @wrap_into_QOp(_char_write)
    def char_write(self, uuid, data):
        """
        Synchronous (ie. blocking) write of a characteristic. Write
        occurs in a background thread, but the calling thread is made to
        wait until there is a result.
        """
        Logger.debug("BLE: char_write(%s, %s)" % (uuid, data))

    # *** Callback interface

    def callback_char_read(self, uuid, callback=None):
        """
        Read a characteristic in a background thread and call back with
        an OpResult, which will contain a bytearray.
        """
        Logger.debug("BLE: callback_char_read(%s, %s)" % (uuid, callback))
        op = QOp(self._char_read, uuid, callback=self.CBConverter.convert(callback))
        self.QOpExecutor.Manager.addFIFOOp(op)

    def callback_char_write(self, uuid, data, callback=None):
        """
        Write a characteristic in a background thread and call back with
        an OpResult.
        """
        Logger.debug("BLE: callback_char_write(%s, %s)" % (uuid, data))
        op = QOp(self._char_write, uuid, data, callback=self.CBConverter.convert(callback))
        self.QOpExecutor.Manager.addFIFOOp(op)

    def descriptorWrite(self, uuid, etc):
        pass

    def descriptorRead(self, uuid, etc):
        pass

