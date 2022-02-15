from jnius import autoclass, cast
from kivy.logger import Logger

from ble.android.pybluetoothgattcallback import PyBluetoothGattCallback
from ble.bleexceptions import *
from ble.bleops import ContextConverter, QOp, QOpExecutor, async_wrap_async_into_QOp, wrap_into_QOp
from ble.gattclientinterface import GATTClientInterface, GATTCState

PythonActivity = autoclass('org.kivy.android.PythonActivity')
CurrentActivity = cast('android.app.Activity', PythonActivity.mActivity)
ApplicationContext = cast('android.content.Context', CurrentActivity.getApplicationContext())
BluetoothGattCallbackImpl = autoclass('org.decentespresso.dedebug.BluetoothGattCallbackImpl')


class GATTClient(GATTClientInterface):
    """
    A hopefully easy and convenient class to use to communicate with a GATT
    server.

    Optimised for convenience. BLE operations should hopefully happen in the
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
        Logger.debug("ble.android.GATTClient.__init__(%s, %s, %s)" % (macaddress, qopexecutor, contextconverter))
        self.MAC = macaddress

        self.State = GATTCState.INIT
        self.QOpExecutor = qopexecutor  # Holds a queue of operations that are run in their own thread
        self.QOpExecutor.startBackgroundProcessing()

        self.CBConverter = contextconverter  # Used to convert callbacks out of the background thread
        # self.AsyncConverter = asynccontextconverter # Used to convert callbacks into an async await
        self.JavaGATTCallback = BluetoothGattCallbackImpl()

        # NB: Keep a local copy of the gatt callback python object, as being given to the
        # java class does not increase its refcount. This means it can be silently garbage
        # collected by the python VM, although the java VM thinks it is still live.
        # This shows up as bizarre "could not invoke" errors on random unrelated types

        self.GATTCallback = PyBluetoothGattCallback()
        self.JavaGATTCallback.setImpl(self.GATTCallback)
        adapter = autoclass('android.bluetooth.BluetoothAdapter').getDefaultAdapter()

        macaddressbytes = [int(x, 16) for x in macaddress.split(":")]

        # Get an Android BluetoothDevice for the given MAC
        self.BluetoothDevice = adapter.getRemoteDevice(macaddressbytes)
        self.QOpTimeout = 30

    # *** Internal functions. No touchy!

    def _connect(self, manager=None, reason=None):
        Logger.debug("BLE: GATTClient._connect() to '%s'" % self.MAC)

        if reason is not None:
            # We've been told to cancel, so do nothing
            return GATTCState.CANCELLED

        # TODO: Need to make sure connection state change q is empty when I start
        # this, so we don't return old data. I probably need to change this
        # interface as there is no real way to match callbacks with connect
        # requests. This is something of a design flaw in the original Android
        # stack. Not entirely sure how to fix it properly.

        self.BluetoothGatt = self.BluetoothDevice.connectGatt(ApplicationContext, False, self.JavaGATTCallback)
        self.GATTCallback.SemaOnConnectionStateChange.down()
        result = self.GATTCallback.QOnConnectionStateChange.pop()

        if not hasattr(self, "Characteristics"):
            # Discover our services on first connect. Remember them so we don't do this for reconnects.
            issued = self.BluetoothGatt.discoverServices()
            if not issued:
                raise BLECouldntDiscoverServices("Could not start remote service discovery")

            # Wait for results
            self.GATTCallback.SemaOnServicesDiscovered.down()
            self.GATTCallback.QOnServicesDiscovered.pop()
            self.Characteristics = {}
            for serv in self.BluetoothGatt.getServices().toArray():
                for char in serv.getCharacteristics().toArray():
                    uuidstr = char.getUuid().toString()
                    self.Characteristics[uuidstr] = char
                    Logger.debug("BLE: Service UUID %s = %s" % (uuidstr, char))

            # Logger.debug("BLE: connect() done")

        return result

    def _disconnect(self):
        self.BluetoothGatt.disconnect()

    def _char_read(self, uuid, manager=None, reason=None):
        Logger.debug("BLE: _char_read(%s, manager=%s, reason=%s)" % (uuid, manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_read() cancelled before execution. Reason: %s" % (reason,))
            return

        char = self.Characteristics[uuid]
        issued = self.BluetoothGatt.readCharacteristic(char)

        if issued:
            # Sleep until there is a result
            self.GATTCallback.SemaOnCharacteristicRead.down()
            result = self.GATTCallback.QOnCharacteristicRead.pop()
            Logger.debug("BLE: _char_read result: %s" % (result,))
            return result
        else:
            Logger.debug("BLE: Android would not issue read")
            raise BLEOperationNotIssued("Android refused to issue read")

    def _char_write(self, uuid, databytes, manager=None, reason=None):
        Logger.debug("BLE: _char_write(%s, manager=%s, reason=%s)" % (uuid, manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_write() cancelled before execution. Reason: %s" % (reason,))
            return

        char = self.Characteristics[uuid]
        char.setValue(databytes)
        issued = self.BluetoothGatt.writeCharacteristic(char)

        if issued:
            # Sleep until there is a result
            self.GATTCallback.SemaOnCharacteristicWrite.down()
            result = self.GATTCallback.QOnCharacteristicWrite.pop()
            Logger.debug("BLE: _char_write result: %s" % (result,))
            return result
        else:
            Logger.debug("BLE: Android would not issue write")
            raise BLEOperationNotIssued("Android refused to issue write")

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
        Logger.debug("BLE: GATTClient.connect() to '%s'" % self.MAC)

    @wrap_into_QOp(_disconnect)
    def disconnect(self):
        Logger.debug("BLE: GATTClient.disconnect() from '%s'" % self.MAC)

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
        Synchronous write to device. Write occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        Logger.debug("BLE: char_read(%s)" % (uuid,))

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
