#!/usr/bin/python3
from kivy.logger import Logger
from jnius import PythonJavaClass, autoclass, cast, java_method
from android.broadcast import BroadcastReceiver

from ble.android.blescanner import BLEScanTool
from ble.android.gattclient import GATTClient
from ble.bleops import QOpExecutorFactory, QOp, ContextConverter, QOpExecutor
from ble.bleinterface import BLEInterface

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
String = autoclass('java.lang.String')

class BLE(BLEInterface):
  """
  This is currently the Android specific BLE module.

  NB: ONLY CALL __init__() AFTER on_create()

  This is because BluetoothAdapter is dependent on getSystemService(),
  which is only initialized after the app exits onCreate().
  """
  def __init__(self, executorfactory: QOpExecutorFactory, contextconverter: ContextConverter):
    Logger.info("BLE.__init__()")

    self.QOpExecutorFactory = executorfactory
    self.ContextConverter = contextconverter
    self.BLEScanTool = None
    self.BLEAdapterClass = autoclass('android.bluetooth.BluetoothAdapter')
    self.BClassicAdapter = self.BLEAdapterClass.getDefaultAdapter();
    self.BClassicAdapter.cancelDiscovery()

    self.GATTClients = {}

    #action = BluetoothDevice.ACTION_FOUND
    #self.BR = BroadcastReceiver(self.on_broadcast, actions=[action])
    #Logger.info("Starting ACTION_FOUND BroadcastReceiver")
    #self.BR.start()

  def setScanTool(self, tool):
    """
    If getScanTool() hasn't yet been called, this method can be used to provide your
    own scan tool.

    Otherwise, if a tool hasn't been provided, the default one is created the first
    time getBLEScanTool() is called.
    """
    self.BLEScanTool = tool

  def on_pause(self):
    """Call if app is paused"""
    #Logger.debug("Stopping ACTION_FOUND BroadcastReceiver")
    #self.BR.stop()

  def on_resume(self):
    """Call is app is resumed"""
    #Logger.debug("Starting ACTION_FOUND BroadcastReceiver")
    #self.BR.start()

  def isBLESupported(self):
    """Returns True if BLE is supported"""
    return self.BClassicAdapter != None

  def isEnabled(self):
    """Returns True if BLE is supported and enabled"""
    if not self.isBLESupported():
      return False
    
    return self.BClassicAdapter.isEnabled()

  def requestBLEEnableIfRequired(self):
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
        enableBtIntent = Intent()
        enableBtIntent.setAction(self.BLEAdapterClass.ACTION_REQUEST_ENABLE)
        PythonActivity.mActivity.startActivityForResult(enableBtIntent, 0x1)
        return True

    return False

  def getBLEScanTool(self):
    """
    If BLE is enabled, returns a BLEScanTool object, else returns None
    """
    #self.BClassicAdapter.startDiscovery()  # Use to scan for Classic devices
    if self.isEnabled():
      if self.BLEScanTool == None:
        self.BLEScanTool = BLEScanTool()
      return self.BLEScanTool
    else:
      return None

  def scanForDevices(self, duration):
    Logger.debug("scanForDevices()")
    t = self.getBLEScanTool()
    if t != None:
      t.startScan(duration)

  def _tobytes(self, macaddress):
    return [int(x, 16) for x in macaddress.split(":")]

  def getGATTClient(self, macaddress: str) -> GATTClient:
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

  def on_broadcast(self, context, intent):
    """
    Set up by __init__ to receive broadcasts (to a BroadcastReceiver, self.BR)
    """
    Logger.info("Received broadcast '%s' with Context '%s'" % (context, intent))

