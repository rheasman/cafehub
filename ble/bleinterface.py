#!/usr/bin/python3
import abc

from ble.bleops import ContextConverter, QOpExecutor


class BLEInterface(metaclass=abc.ABCMeta):
    """
    BLE module interface

    """

    @abc.abstractmethod
    def __init__(self, macaddress: str, qopexecutor: QOpExecutor, contextconverter: ContextConverter):
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
    def setScanTool(self, tool):
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
    def isBLESupported(self):
        """Returns True if BLE is supported"""

    @abc.abstractmethod
    def isEnabled(self):
        """Returns True if BLE is supported and enabled"""

    @abc.abstractmethod
    def requestBLEEnableIfRequired(self):
        """
        Asks the user to enable BLE if required.
        Right now, has no way to tell if the user succeeded.
        Requires receiving an activity result that seems to need setup in the
        APK, which gets in the way of testing using kivy_launcher.

        Returns True if a request was generated for the user. Check for Activy result.
        Returns False if no request needed. Do nothing.
        """

    @abc.abstractmethod
    def getBLEScanTool(self):
        """
        If BLE is enabled, returns a BLEScanTool object, else returns None
        """

    @abc.abstractmethod
    def scanForDevices(self, duration):
        """
        Uses the default scan tool to scan for devices for "duration" seconds.
        """
