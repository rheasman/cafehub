#!/usr/bin/python3
import threading
import traceback
from typing import Any, Dict, Union

from kivy.logger import Logger
from ble.android.androidtypes import T_Context, T_Intent

from ble.bleak.blescanner import BLEScanTool
from ble.bleak.gattclient import GATTClient
from ble.bleexceptions import BLEException
from ble.bleinterface import BLEInterface
from ble.bleops import ContextConverter, QOpExecutorFactory
from ble.blescantoolinterface import I_BLEScanTool
from ble.gattclientinterface import GATTClientInterface


class BLE(BLEInterface):
    """
    This is the BLEAK specific BLE module.
    """

    def __init__(self, executorfactory: QOpExecutorFactory, contextconverter: ContextConverter, androidcontext : Any = None):
        Logger.info("UI: BLE.__init__()")

        print("BLE(__init__) current thread", threading.current_thread().name)

        self.QOpExecutorFactory = executorfactory
        self.ContextConverter = contextconverter
        self.BLEScanTool : Union[I_BLEScanTool, None] = None

        self.ConnectLock = threading.RLock()
        self.GATTClients : Dict[str, GATTClientInterface] = {}

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
        """Call if app is resumed"""
        # Logger.debug("Starting ACTION_FOUND BroadcastReceiver")
        # self.BR.start()

    def on_stop(self):
        """Call when app is stopped"""
        Logger.debug("BLE on_stop()")
        self.disconnectAllClients()

    def isBLESupported(self) -> bool:
        """Returns True if BLE is supported"""
        return True

    def isEnabled(self) -> bool:
        """Returns True if BLE is supported and enabled"""
        if not self.isBLESupported():
            return False

        return True

    def requestBLEEnableIfRequired(self) -> bool:
        """
        Asks the user to enable BLE if required.
        Right now, has no way to tell if the user succeeded.
        Requires receiving an activity result that seems to need setup in the
        APK, which gets in the way of testing using kivy_launcher.

        Returns True if a request was generated for the user. Check for Activy result.
        Returns False if no request needed. Do nothing.
        """
        Logger.debug("BLE: requestBLEEnableIfRequired()")

        return True

    def getBLEScanTool(self) -> Union[I_BLEScanTool, None]:
        """
        If BLE is enabled, returns a BLEScanTool object, else returns None
        """
        # self.BClassicAdapter.startDiscovery()  # Use to scan for Classic devices
        if self.isEnabled():
            if self.BLEScanTool is None:
                self.BLEScanTool : Union[I_BLEScanTool, None] = BLEScanTool()
            return self.BLEScanTool
        else:
            return None

    def scanForDevices(self, duration : float):
        Logger.debug("BLE: scanForDevices()")
        t = self.getBLEScanTool()
        if t is not None:
            t.startScan(duration)

    def _tobytes(self,  macaddress : str):
        return [int(x, 16) for x in macaddress.split(":")]

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
                try:
                    if client.is_connected():
                        client.disconnect()
                except BLEException:
                    Logger.debug("BLE: disconnectAllClients() caught exception: %s" % (traceback.format_exc(),))


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

        gc = GATTClient(macaddress, self.QOpExecutorFactory.makeExecutor(), self.ContextConverter)

        self.GATTClients[macaddress] = gc
        return gc

    def on_broadcast(self, context : T_Context, intent : T_Intent):
        """
        Set up by __init__ to receive broadcasts (to a BroadcastReceiver, self.BR)
        """
        Logger.info("Received broadcast '%s' with Context '%s'" % (context, intent))
