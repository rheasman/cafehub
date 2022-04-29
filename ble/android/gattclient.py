import time
from kivy.logger import Logger
import threading
from typing import Any, Callable, List, Optional, Tuple, Union

from jnius import autoclass # type: ignore
from ble.android.androidtypes import T_BluetoothAdapter, T_BluetoothGatt, T_BluetoothGattCallbackImpl, T_BluetoothGattCharacteristic, T_BluetoothGattDescriptor, T_Context, T_Java_UUID, T_PythonActivity 

from ble.android.pybluetoothgattcallback import AndroidGATTStatus, PyBluetoothGattCallback
from ble.bleexceptions import *
from ble.bleops import ContextConverter, CountingSemaphore, OpResult, QOp, QOpExecutor, QOpManager, async_wrap_sync_into_QOp, synchronized_with_lock, wrap_into_QOp
from ble.gattclientinterface import GATTClientInterface, GATTCState
from ble.uuidtype import CHAR_UUID, DESC_UUID

# NB NB NB
# There seems to be an issue with pyjnius not being able to find user defined classes unless
# it is running in the main thread.
# This causes serious issues for us, as we want to create a new PyBluetoothGattCallback 
# class for each GATTClient.

# TODO: THIS WILL PROBABLY BREAK FOR MORE THAN ONE GATT CLIENT? MAYBE?

# I'll see about getting pyjnius fixed, one way or another

PythonActivity : T_PythonActivity = autoclass('org.kivy.android.PythonActivity')
BluetoothGattCallbackImpl : T_BluetoothGattCallbackImpl = autoclass('org.decentespresso.dedebug.BluetoothGattCallbackImpl')
PyBLEGattCB = PyBluetoothGattCallback()
BluetoothGattDescriptor : T_BluetoothGattDescriptor = autoclass("android.bluetooth.BluetoothGattDescriptor")
BLE_UUID : T_Java_UUID = autoclass('java.util.UUID')
BluetoothAdapter : T_BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')

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

    TODO: set_disc_callback

    """

    def __init__(self, macaddress: str, qopexecutor: QOpExecutor, contextconverter: ContextConverter, androidcontext : T_Context):
        Logger.debug("ble.android.GATTClient.__init__(%s, %s, %s, %s)" % (macaddress, qopexecutor, contextconverter, androidcontext))
        self.MAC = macaddress
        self.AndroidContext = androidcontext

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

        self.GATTCallbackClass = PyBLEGattCB
        self.JavaGATTCallback.setImpl(self.GATTCallbackClass)
        
        adapter : T_BluetoothAdapter = BluetoothAdapter.getDefaultAdapter()

        macaddressbytes = [int(x, 16) for x in macaddress.split(":")]

        # Get an Android BluetoothDevice for the given MAC
        self.BluetoothDevice = adapter.getRemoteDevice(macaddressbytes)
        self.QOpTimeout = 30
        self.DisconnectionCallback : Union[Callable[[GATTCState], None], None] = None

        # self.Characteristics should only be written in the background thread.
        # Reading it in other threads is fine.
        self.Characteristics : dict[str, T_BluetoothGattCharacteristic] = {}
        self.NotifyThread = threading.Thread(target=self._notify_monitor, daemon=True)
        self.NotifyThread.start()

        self.ConnectStatusThread = threading.Thread(target=self._conn_monitor, daemon=True)
        self.ConnectStatusThread.start()

        self.NotifyCallback : dict[str, Union[Callable[[CHAR_UUID, bytes], None], None]] = {}
        self.ConnLock = threading.RLock()
        self.ConnStatus : Tuple[AndroidGATTStatus, GATTCState] = (AndroidGATTStatus(0), GATTCState.INIT)
        self._ConnectedSema = CountingSemaphore(value=0)

    def _notify_monitor(self, *args : Any):
        """
        Sit in an infinite loop and call a callback if we get a notify
        """
        Logger.debug("BLE: _notify_monitor thread starting")
        while True:
            gc = self.GATTCallbackClass
            gc.SemaOnCharacteristicChanged.down()
            Logger.debug("BLE: _notify_monitor: SemaOnCharacteristicChanged upped.")
            uuid, data = gc.QOnCharacteristicChanged.pop()
            if uuid in self.NotifyCallback:
                cb = self.NotifyCallback[uuid]
                if cb:
                    cb(CHAR_UUID(uuid), data)

    @synchronized_with_lock('ConnLock')
    def _set_conn_info(self, gattstatus : AndroidGATTStatus, aconninfo : GATTCState) -> None:
        self.ConnStatus = (gattstatus, aconninfo)

    @synchronized_with_lock('ConnLock')
    def _get_conn_info(self) -> Tuple[AndroidGATTStatus, GATTCState] :
        return self.ConnStatus

    def _raise_if_disconnected(self):
        _, cstate = self._get_conn_info()
        if cstate != GATTCState.CONNECTED:
            raise (BLEOperationNotIssued("No device connected"))

    def set_disc_callback(self, callback: Callable[[GATTCState], None]):
        self.DisconnectionCallback = callback

    def shutdown(self) -> None:
        self.QOpExecutor.shutdown()

    def is_connected(self) -> bool:
        _, cstate = self._get_conn_info()
        return cstate == GATTCState.CONNECTED

    def getCharacteristicsUUIDs(self) -> List[str]:
        return list(self.Characteristics.keys())

    """
    The (as usual, pathetically overcomplicated) android code to enable a notification is something I found on stackoverflow.
    Thank heavens that Tiramisu will finally be getting rid of the layers and layers of stupid in the Android BLE stack.

        protected static final UUID CHARACTERISTIC_UPDATE_NOTIFICATION_DESCRIPTOR_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");

        public boolean setCharacteristicNotification(BluetoothGatt bluetoothGatt, BluetoothGattCharacteristic characteristic,boolean enable) {
            Logger.d("setCharacteristicNotification");
            bluetoothGatt.setCharacteristicNotification(characteristic, enable);
            BluetoothGattDescriptor descriptor = characteristic.getDescriptor(CHARACTERISTIC_UPDATE_NOTIFICATION_DESCRIPTOR_UUID);
            descriptor.setValue(enable ? BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE : new byte[]{0x00, 0x00});
            return bluetoothGatt.writeDescriptor(descriptor); //descriptor write operation successfully started?
        }
    """

    def _set_notify(self, uuid : CHAR_UUID, enable : bool, notifycallback : Callable[[CHAR_UUID, bytes], None], manager: Union[QOpManager, None] = None, reason: Union[str, None] = None):
        Logger.debug("BLE: _set_notify(%s, %s, %s)" % (uuid.AsString, enable, notifycallback))
        if enable:
            self.NotifyCallback[uuid.AsString] = notifycallback
        else:
            self.NotifyCallback[uuid.AsString] = None

        char = self.Characteristics[uuid.AsString]

        if not self.BluetoothGatt:
            Logger.debug("No self.BluetoothGatt")
            return

        if not self.BluetoothGatt.setCharacteristicNotification(char, enable):
            Logger.debug("BLE: set_notify: Android stack failed when attempting to set notify")
            raise BLEOperationNotIssued("set_notify failed for unknown reason")

        if enable:
            self._desc_write(uuid, DESC_UUID("00002902-0000-1000-8000-00805f9b34fb"), BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE, manager = manager)
        else:
            self._desc_write(uuid, DESC_UUID("00002902-0000-1000-8000-00805f9b34fb"), BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE, manager = manager)

    # *** Internal functions. No touchy!

    def _procStateChange(self, manager : Union[QOpManager, None] = None, reason : Union[str, None] = None):
        """
        This does whatever is necessary when the connection state changes to disconnected.
        It can be fairly intensive, as on disconnect, all outstanding operations
        have to be cancelled.
        """
        Logger.debug("BLE: _procStateChange()")
        if reason is not None:
            # We've been told to cancel, so do nothing
            return

        self.Characteristics = {}
        status, connstate = self._get_conn_info()
            
        if self.DisconnectionCallback:
            cb = self.CBConverter.convert(self.DisconnectionCallback)
            cb(connstate)

        if manager is not None:
            manager.cancelQ(reason="Disconnected (%s, %s)" % (repr(status), repr(connstate)))

        self._set_conn_info(AndroidGATTStatus(0), GATTCState.DISCONNECTED)
        if self.BluetoothGatt:
            # Another Android bug: You can call disconnect, and it will call back with "DISCONNECTED".
            # But, it doesn't send the disconnect and the link is held up. There is no way to tell that you
            # are in this state and it becomes impossible to talk to the device or connect to it.
            # But if you call close() on the BluetoothGatt object and then discard any
            # references to it, it gets garbage collected and we win!
            try:
                self.BluetoothGatt.disconnect()
            except:
                self.BluetoothGatt.close()


        self.BluetoothGatt = None

        
    def _conn_monitor(self):
        """
        Monitor connection state
        """
        gc = self.GATTCallbackClass
        while 1:
            gc.SemaOnConnectionStateChange.down()
            Logger.debug("BLE: _conn_monitor waking up")
            (androidstatus, androidconnstate) = gc.QOnConnectionStateChange.pop()
            self._set_conn_info(androidstatus, androidconnstate.asGATTCState())

            if  ((androidconnstate.asGATTCState() == GATTCState.DISCONNECTING) or
                 (androidconnstate.asGATTCState() == GATTCState.DISCONNECTED)):
                # We're disconnecting, apparently
                # Put disconnection at FRONT of queue, as we're going to have to cancel
                # Any other ops in the queue
                man = self.QOpExecutor.getManager()
                man.addLIFOOp(QOp(self._procStateChange, callback=None))
            
            if (androidconnstate.asGATTCState() == GATTCState.CONNECTED) or (androidconnstate.asGATTCState() == GATTCState.DISCONNECTED):
                self._ConnectedSema.up()

    def _connect(self, manager: Union[QOpManager, None] = None, reason: Union[str, None] = None) -> GATTCState:
        Logger.debug("BLE: GATTClient._connect() to '%s'" % self.MAC)

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _connect() cancelled before execution. Reason: %s" % (reason,))
            raise BLEOperationNotIssued("Cancelled: %s" % (reason,))

        _, cstate = self._get_conn_info()
        #if (cstate == GATTCState.CONNECTED):
        #    raise (BLEOperationNotIssued("Device already connected"))

        self.Characteristics = {}

        if (cstate == GATTCState.CONNECTING):
            raise (BLEOperationNotIssued("We are already in the process of connecting to this device"))

        # TODO: Need to make sure connection state change q is empty when I start
        # this, so we don't return old data. I probably need to change this
        # interface as there is no real way to match callbacks with connect
        # requests. This is something of a design flaw in the original Android
        # stack. Not entirely sure how to fix it properly.

        Logger.debug("BLE: Issuing android connect")
        self.BluetoothGatt : Optional[T_BluetoothGatt] = self.BluetoothDevice.connectGatt(self.AndroidContext, False, self.JavaGATTCallback)

        if not self.BluetoothGatt:
            Logger.debug("No self.BluetoothGatt")
            raise BLEOperationNotIssued("No self.BluetoothGatt")

        Logger.debug("BLE: _connect: _ConnectedSema value: %s" % (self._ConnectedSema._value))  # type: ignore
        self._ConnectedSema.down()
        Logger.debug("BLE: _connect woke up on _ConnectedSema")

        _, result = self._get_conn_info()

        if (result == GATTCState.CONNECTED) and (len(self.getCharacteristicsUUIDs()) < 1):
            # Discover our services on first connect. Remember them so we don't do this for reconnects.
            issued = self.BluetoothGatt.discoverServices()
            if not issued:
                raise BLECouldntDiscoverServices("Could not start remote service discovery")

            # Wait for results
            Logger.debug("BLE: _connect sleeping on SemaOnServicesDiscovered")
            success = self.GATTCallbackClass.SemaOnServicesDiscovered.down(timeout=0.1)
            while not success:
                _, cstate = self._get_conn_info()
                if (cstate != GATTCState.CONNECTED):
                    raise BLEConnectionError("Disconnection occurred while attempting to read available services on new GATT client")
                success = self.GATTCallbackClass.SemaOnServicesDiscovered.down(timeout=0.1)

            Logger.debug("BLE: _connect woke up on SemaOnServicesDiscovered")
            self.GATTCallbackClass.QOnServicesDiscovered.pop()
            for serv in self.BluetoothGatt.getServices().toArray():
                servuuid = serv.getUuid().toString()
                for char in serv.getCharacteristics().toArray():
                    uuidstr = char.getUuid().toString()
                    self.Characteristics[uuidstr] = char
                    Logger.debug("BLE: Service UUID (%s) %s = %s" % (servuuid, uuidstr, char))

            # Logger.debug("BLE: connect() done")

        return result

    def _disconnect(self, manager: Union[QOpManager, None] = None, reason: Union[str, None] = None) -> GATTCState:
        Logger.debug("BLE: _disconnect(manager=%s, reason=%s)" % (manager, reason))
        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _disconnect() cancelled before execution. Reason: %s" % (reason,))
            raise BLEOperationNotIssued("Cancelled: %s" % (reason,))
        
        # self._raise_if_disconnected()
        
        if self.BluetoothGatt:
            self.BluetoothGatt.disconnect()
            self.BluetoothGatt.close()

        # Another Android bug: You can call disconnect, and it will call back with "DISCONNECTED".
        # But, it doesn't send the disconnect and the link is held up. There is no way to tell that you
        # are in this state and it becomes impossible to talk to the device or connect to it.
        # But if you call close() on the BluetoothGatt object and then discard any
        # references to it, it gets garbage collected and we win!

        self.BluetoothGatt = None
        return GATTCState.DISCONNECTED



    def _char_read(self, uuid: CHAR_UUID, manager: Union[QOpManager, None] = None, reason: Union[str, None] = None) -> bytes:
        Logger.debug("BLE: _char_read(%s, manager=%s, reason=%s)" % (uuid, manager, reason))
        
        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_read() cancelled before execution. Reason: %s" % (reason,))
            raise BLEOperationNotIssued("Cancelled: %s" % (reason,))

        if not self.BluetoothGatt:
            # This code should be unreachable
            Logger.debug("No self.BluetoothGatt")
            raise BLEOperationNotIssued("No self.BluetoothGatt")

        self._raise_if_disconnected()
        
        char = self.Characteristics[uuid.AsString]

        count = 0
        issued = self.BluetoothGatt.readCharacteristic(char)
        while (not issued) and (count < 3):
            Logger.debug("BLE: _char_read: Android declined to issue read. Trying again. (%d)" % (count,))
            time.sleep(0.001)
            issued = self.BluetoothGatt.readCharacteristic(char)
            count += 1

        if issued:
            # Sleep until there is a result
            self.GATTCallbackClass.SemaOnCharacteristicRead.down()
            result = self.GATTCallbackClass.QOnCharacteristicRead.pop()
            Logger.debug("BLE: _char_read result: %s" % (result,))
            return result[2]
        else:
            Logger.debug("BLE: Android would not issue read. Are you sure you have read permission on this characteristic?")
            raise BLEOperationNotIssued("Android refused to issue read. Are you sure you have read permission on this characteristic?")

    def _char_write(self, uuid: CHAR_UUID, data : bytes, requireresponse: bool, manager: Union[QOpManager, None] = None, reason: Union[str, None] = None) -> None:
        Logger.debug("BLE: _char_write(%s, manager=%s, reason=%s)" % (uuid, manager, reason))

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _char_write() cancelled before execution. Reason: %s" % (reason,))
            raise BLEOperationNotIssued("Cancelled: %s" % (reason,))


        if not self.BluetoothGatt:
            # This code should be unreachable
            Logger.debug("No self.BluetoothGatt")
            raise BLEOperationNotIssued("No self.BluetoothGatt")

        self._raise_if_disconnected()

        # Logger.debug("BLE: known characteristics: %s" % (self.Characteristics,))
        char = self.Characteristics[uuid.AsString]
        char.setValue(data)
        if requireresponse:
            char.setWriteType(char.WRITE_TYPE_DEFAULT)
        else:
            char.setWriteType(char.WRITE_TYPE_NO_RESPONSE)

        issued = self.BluetoothGatt.writeCharacteristic(char)

        if issued:
            # Sleep until there is a result
            if self.GATTCallbackClass.SemaOnCharacteristicWrite.down(timeout=10):
                result = self.GATTCallbackClass.QOnCharacteristicWrite.pop()
                Logger.debug("BLE: _char_write result: %s" % (result,))
                return 
            else:
                # The down timed out
                raise BLEOperationTimedOut("Android issued write but never called back with success or failure")
        else:
            Logger.debug("BLE: Android would not issue write. Are you sure you have write permission on this characteristic?")
            raise BLEOperationNotIssued("Android refused to issue write. Are you sure you have write permission on this characteristic?")

    def _desc_write(self, charuuid : CHAR_UUID, descid : DESC_UUID, data : bytes, manager: Union[QOpManager, None] = None, reason: Union[str, None] = None) -> None:
        """
        Write data to the given descriptor
        """
        Logger.debug("BLE: _desc_write(%s, %s, manager=%s, reason=%s)" % (charuuid, descid, manager, reason))        

        if reason is not None:
            # Reason being set means we are being asked to cancel
            Logger.debug("BLE: _desc_write() cancelled before execution. Reason: %s" % (reason,))
            raise BLEOperationNotIssued("Cancelled: %s" % (reason,))

        if not self.BluetoothGatt:
            # This code should be unreachable
            Logger.debug("No self.BluetoothGatt")
            raise BLEOperationNotIssued("No self.BluetoothGatt")

        self._raise_if_disconnected()
        
        char = self.Characteristics.get(charuuid.AsString)
        if char is None:
            raise BLEOperationNotIssued("Unknown UUID: %s" % (charuuid.AsString,))

        desc = BLE_UUID.fromString(descid.AsString)
        char_desc = char.getDescriptor(desc)
        if char_desc is None:
            raise BLEOperationNotIssued("Unknown descriptor %s on UUID %s" % (descid.AsString, charuuid.AsString,))

        if not char_desc.setValue(data):
            raise BLEOperationNotIssued("Could not set local value on Android descriptor")
        
        if not self.BluetoothGatt.writeDescriptor(char_desc):
            raise BLEOperationNotIssued("Android refused to issue write on descriptor")


        # Wait for a characteristic callback. It has to be this one,
        # as we only allow one transaction at a time.
        Logger.debug("BLE: _desc_write: Sleeping on SemaOnDescriptorWrite")
        success = self.GATTCallbackClass.SemaOnDescriptorWrite.down(timeout=1)
        if not success:
            # Yay. Android sometimes doesn't call the callback when a descriptor write finishes. It looks like it silently succeeds.
            # This screws up everything. I'm trying to make sure that there is only ever one operation in the Android stack at a time
            # and now it's impossible to know when this operation is done.
            raise BLEOperationTimedOut("Android reported initiating descriptor write, but then never reported success or failure")
        else:
            result = self.GATTCallbackClass.QOnDescriptorWrite.pop()
            Logger.debug("BLE: _desc_write result: %s" % (result,))

        if result[0] != descid.AsString:
           raise BLEMismatchedOperation("Descriptor write we requested '%s' doesn't match the callback we received ('%s')" % (descid.AsString, result[0]))


    # *** Async interface

    @async_wrap_sync_into_QOp(_connect)
    async def async_connect(self):
        """
        Connect
        """
        Logger.debug("BLE: async_connect(%s)" % (self.MAC,))

    @async_wrap_sync_into_QOp(_disconnect)
    async def async_disconnect(self):
        """
        Connect
        """
        Logger.debug("BLE: async_disconnect(%s)" % (self.MAC,))

    @async_wrap_sync_into_QOp(_char_read)
    async def async_char_read(self, uuid : CHAR_UUID):
        """
        Write a characteristic in a background thread and return result when it is done.
        """
        Logger.debug("BLE: async_char_read(%s)" % (uuid,))

    @async_wrap_sync_into_QOp(_char_write)
    async def async_char_write(self, uuid: CHAR_UUID, data : bytes, requireresponse : bool):
        """
        Write a characteristic in a background thread and return result
        """
        Logger.debug("BLE: async_char_write(%s, %s, %s)" % (uuid, data, requireresponse))

    # *** Synchronous interface

    @wrap_into_QOp(_connect)
    def connect(self):
        Logger.debug("BLE: GATTClient.connect() to '%s'" % self.MAC)

    @wrap_into_QOp(_disconnect)
    def disconnect(self):
        Logger.debug("BLE: GATTClient.disconnect() from '%s'" % self.MAC)

    @wrap_into_QOp(_set_notify)
    def set_notify(self, uuid : CHAR_UUID, enable : bool, notifycallback : Callable[[CHAR_UUID,bytes], None]):
        """
        Enables notifications for the given uuid.
        """
        Logger.debug("BLE: set_notify(%s, %s, %s)" % (uuid.AsString, enable, notifycallback))

    @wrap_into_QOp(_char_read)
    def char_read(self, uuid: CHAR_UUID) -> None:
        """
        Synchronous read of a characteristic. Read occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        Logger.debug("BLE: char_read(%s)" % (uuid,))

    @wrap_into_QOp(_char_write)
    def char_write(self, uuid: CHAR_UUID, data: bytes, requireresponse : bool) -> None:
        """
        Synchronous write to device. Write occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        Logger.debug("BLE: char_write(%s, %s, %s)" % (uuid,))

    @wrap_into_QOp(_desc_write)
    def descriptor_write(self, charuuid: CHAR_UUID, descid : DESC_UUID, data : bytes):
        """
        Synchronous write to a descriptor. Write occurs in a background thread,
        but the calling thread is made to wait until there is a result.
        """
        Logger.debug("BLE: descriptor_write(%s, %s, %s)" % (charuuid, descid, data))

    # *** Callback interface

    def callback_char_read(self, uuid: CHAR_UUID, callback : Callable[ [OpResult[bytes]], None ]):
        """
        Read a characteristic in a background thread and call back with
        an OpResult, which will contain a 'bytes' object.
        """
        Logger.debug("BLE: callback_char_read(%s, %s)" % (uuid, callback))
        op = QOp(self._char_read, uuid, callback=self.CBConverter.convert(callback))
        self.QOpExecutor.Manager.addFIFOOp(op)

    def callback_char_write(self, uuid: CHAR_UUID, data : bytes, requireresponse : bool, callback : Optional[ Callable[[OpResult[None]], None]] = None):
        """
        Write a characteristic in a background thread and call back with
        an OpResult.
        """
        Logger.debug("BLE: callback_char_write(%s, %s, %s)" % (uuid, data, requireresponse))
        op : QOp[None] = QOp(self._char_write, uuid, data, callback=self.CBConverter.convert(callback))
        self.QOpExecutor.Manager.addFIFOOp(op)


    def descriptorRead(self, uuid: CHAR_UUID):
        pass
