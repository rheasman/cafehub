#!/usr/bin/python3
import threading
from typing import Any, Dict, Union

from kivy.logger import Logger
from jnius import autoclass # type: ignore
from ble.android.androidtypes import T_BluetoothAdapter, T_BluetoothClassicAdapter, T_BluetoothDevice, T_Context, T_Intent, T_Java_String, T_Native_Invocation_Handler, T_PythonActivity

# from android.broadcast import BroadcastReceiver

from ble.android.blescanner import BLEScanTool
from ble.android.gattclient import GATTClient
from ble.bleops import QOpExecutorFactory, ContextConverter
from ble.bleinterface import BLEInterface
from ble.blescantoolinterface import I_BLEScanTool
from ble.gattclientinterface import GATTClientInterface

PythonActivity : T_PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent : T_Intent = autoclass('android.content.Intent')
BluetoothDevice : T_BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
String : T_Java_String = autoclass('java.lang.String')
InvHandler : T_Native_Invocation_Handler = autoclass("org.jnius.NativeInvocationHandler")

class BLE(BLEInterface):
    """
    This is currently the Android specific BLE module.

    NB: ONLY CALL __init__() AFTER on_create()

    This is because BluetoothAdapter is dependent on getSystemService(),
    which is only initialized after the app exits onCreate().
    """

    def __init__(self, executorfactory: QOpExecutorFactory, contextconverter: ContextConverter, androidcontext : Any = None):
        Logger.debug("BLE.__init__()")

        self.AndroidContext = androidcontext
        self.QOpExecutorFactory = executorfactory
        self.ContextConverter = contextconverter
        self.BLEScanTool = None
        self.BLEAdapterClass : T_BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        self.BLEAdapter : T_BluetoothAdapter = self.BLEAdapterClass.getDefaultAdapter()
        self.BLEAdapter.cancelDiscovery()

        self.GATTClients : Dict[str, GATTClientInterface] = {}

        self.ConnectLock = threading.RLock()

        # action = BluetoothDevice.ACTION_FOUND
        # self.BR = BroadcastReceiver(self.on_broadcast, actions=[action])
        # Logger.info("Starting ACTION_FOUND BroadcastReceiver")
        # self.BR.start()

    def setScanTool(self, tool : I_BLEScanTool):
        """
        If getScanTool() hasn't yet been called, this method can be used to provide your
        own scan tool.

        Otherwise, if a tool hasn't been provided, the default one is created the first
        time getBLEScanTool() is called.
        """
        self.BLEScanTool = tool

    def on_pause(self):
        """Call if app is paused"""
        # Logger.debug("Stopping ACTION_FOUND BroadcastReceiver")
        # self.BR.stop()

    def on_resume(self):
        """Call is app is resumed"""
        # Logger.debug("Starting ACTION_FOUND BroadcastReceiver")
        # self.BR.start()

    def on_stop(self):
        """Call to gracefully shut down BLE, as part of stopping the app"""
        Logger.debug("on_stop() in android BLE.py")
        self.disconnectAllClients()

    def isBLESupported(self):
        """Returns True if BLE is supported"""
        return self.BLEAdapter is not None

    def isEnabled(self) -> bool:
        """Returns True if BLE is supported and enabled"""
        if not self.isBLESupported():
            return False

        return self.BLEAdapter.isEnabled()

    def requestBLEEnableIfRequired(self) -> bool:
        """
        Asks the user to enable BLE if required.
        Right now, has no way to tell if the user succeeded.
        Requires receiving an activity result that seems to need setup in the
        APK, which gets in the way of testing using kivy_launcher.

        Returns True if a request was generated for the user. Check for Activy result.
        Returns False if no request needed. Do nothing.
        """
        Logger.debug("requestBLEEnableIfRequired()")
        if self.isBLESupported():
            if not self.isEnabled():
                # Uri = autoclass('android.net.Uri')
                enableBtIntent : T_Intent = Intent()
                enableBtIntent.setAction(self.BLEAdapterClass.ACTION_REQUEST_ENABLE)
                PythonActivity.mActivity.startActivityForResult(enableBtIntent, 0x1)
                return True

        return False

    def getBLEScanTool(self) -> Union[I_BLEScanTool, None]:
        """
        If BLE is enabled, returns a BLEScanTool object, else returns None
        """
        # self.BLEAdapter.startDiscovery()  # Use to scan for Classic devices
        if self.isEnabled():
            if self.BLEScanTool is None:
                Logger.debug("BLE: BLEScanTool doesn't exist yet. Creating.")
                self.BLEScanTool = BLEScanTool(self.BLEAdapter)
            return self.BLEScanTool
        else:
            return None

    def scanForDevices(self, duration : float):
        Logger.debug("BLE: scanForDevices()")
        t = self.getBLEScanTool()
        if t is not None:
            t.startScan(duration)
        else:
            Logger.info("BLE: Could not get BLEScanTool")

    def _tobytes(self, macaddress : str):
        return [int(x, 16) for x in macaddress.split(":")]

    def getGATTClient(self, macaddress: str) -> GATTClientInterface:
        """
        Return a GATT client for the BLE device with the given MAC address. The
        device does not need to have been seen in a BLE scan. If you know what
        device you want, there is no need for a scan at all.

        There is only one GATTClient object for a MAC. Calling this more than once
        for a MAC will return the same object each time.

        Does not actually connect to the device. Call connect() on the GATTClient
        when you are ready.
        """
        Logger.debug("BLE: getGATTClient(%s)" % (macaddress,))

        if macaddress in self.GATTClients:
            return self.GATTClients[macaddress]

        gc = GATTClient(macaddress, self.QOpExecutorFactory.makeExecutor(), self.ContextConverter, self.AndroidContext)

        self.GATTClients[macaddress] = gc
        return gc

    def on_broadcast(self, context : T_Context, intent : T_Intent):
        """
        Set up by __init__ to receive broadcasts (to a BroadcastReceiver, self.BR)
        """
        Logger.info("Received broadcast '%s' with Context '%s'" % (context, intent))

    def disconnectAllClients(self):
        """
        Shut down all GATT Clients we know about
        """
        Logger.debug("BLE: disconnectAllClients")
        with self.ConnectLock:
            # Only do one disconnect at a time, as
            # BLEAK seems to start behaving erratically
            # for future connects, and we know the Android
            # stack would be unhappy too
            for client in self.GATTClients.values():
                if client.is_connected():
                    try:
                        client.disconnect()
                    except:
                        pass
