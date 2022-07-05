#!/usr/bin/python3
import abc
from typing import Any, Union

from ble.bleops import ContextConverter, QOpExecutorFactory
from ble.blescantoolinterface import I_BLEScanTool
from ble.gattclientinterface import GATTClientInterface


class BLEInterface(metaclass=abc.ABCMeta):
    """
    BLE module interface

    """

    @abc.abstractmethod
    def __init__(self, macaddress: str, qopexecutorfac: QOpExecutorFactory, contextconverter: ContextConverter, androidcontext : Any = None):
        """
        NB on Android: ONLY CALL __init__() AFTER on_create()

        This is because BluetoothAdapter is dependent on
        getSystemService(), which is only initialized after the app
        exits onCreate().

        All BLE operations will be fed through a single queue per remote
        device, managed by the given QOpExecutor. Callbacks are passed
        through a context converter to make sure that callbacks are run
        in the user's thread rather than the BLE thread.
        """

    @abc.abstractmethod
    def setScanTool(self, tool : I_BLEScanTool):
        """

        If getScanTool() hasn't yet been called, this method can be used
        to provide your own scan tool.

        Otherwise, if a tool hasn't been provided, the default one is
        created the first time getBLEScanTool() is called.

        """

    @abc.abstractmethod
    def on_pause(self):
        """Call if app is paused"""

    @abc.abstractmethod
    def on_resume(self):
        """Call is app is resumed"""

    @abc.abstractmethod
    def on_stop(self):
        """Call to gracefully shut down BLE, as part of stopping the app"""

    @abc.abstractmethod
    def disconnectAllClients(self):
        """
        Iterate through and disconnect all known clients
        """
        
    @abc.abstractmethod
    def isBLESupported(self) -> bool :
        """Returns True if BLE is supported"""

    @abc.abstractmethod
    def isEnabled(self) -> bool:
        """Returns True if BLE is supported and enabled"""

    @abc.abstractmethod
    def requestBLEEnableIfRequired(self) -> bool:
        """
        Asks the user to enable BLE if required.
        Right now, has no way to tell if the user succeeded.
        Requires receiving an activity result that seems to need setup in the
        APK, which gets in the way of testing using kivy_launcher.

        Returns True if a request was generated for the user. Check for Activy result.
        Returns False if no request needed. Do nothing.
        """

    @abc.abstractmethod
    def getBLEScanTool(self) -> Union[I_BLEScanTool, None]:
        """
        If BLE is enabled, returns a BLEScanTool object, else returns None
        """

    @abc.abstractmethod
    def scanForDevices(self, duration : float):
        """
        Uses the default scan tool to scan for devices for "duration" seconds.
        """

    @abc.abstractmethod
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
