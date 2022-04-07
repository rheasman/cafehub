from kivy.logger import Logger
from jnius import PythonJavaClass, java_method  # type: ignore
from ble.blescanresult import BLEScanResult

class PyScanCallback(PythonJavaClass):
  """
  Worker class for BLEScanTool. Not to be used by anything else.

  The Dalvik VM in Android makes it impossible to write a python proxy class
  that inherits from partially abstract classes. Unfortunately, some
  callbacks in Android are implemented this way.

  So, we have to have a Java wrapper that holds an interface with the same
  methods as the abstract class. Then we can implement the interface in
  Python, and pass it to the Java wrapper.

  We'll have to do this for callbacks from the scanner, and for some GATT
  operations as well.
  """
  __javainterfaces__ = ["org/decentespresso/dedebug/ScanCallbackImpl$IScanCallback"]
  __javacontext__ = 'app'  # Use the app class resolver, not the system resolver.

  @java_method('(Ljava/util/List;)V')
  def onBatchScanResults(self, srlist):
    # public void onBatchScanResults(List<ScanResult> results)
    Logger.debug(f"BLE: onBatchScanResults") #: {repr(srlist)}")

  @java_method('(I)V')
  def onScanFailed(self, errorCode):
    # void onScanFailed(int errorCode)
    Logger.debug(f"BLE: onScanFailed: {errorCode}")

  @java_method('(ILandroid/bluetooth/le/ScanResult;)V')
  def onScanResult(self, callbackType, result):
    # void onScanResult(int callbackType, ScanResult result);

    Logger.debug(f"BLE: onScanResult: callBackType: {callbackType}")
    record = result.getScanRecord()
    name = record.getDeviceName()
    if name:
      name = name.replace("\0", "")

    macaddress = result.device.getAddress()
    uuids = record.getServiceUuids()
    if uuids:
      uuids = [x.toString() for x in record.getServiceUuids().toArray()]
    Logger.debug(f"BLE: onScanResult: DeviceName: {name}")
    Logger.debug(f"BLE: onScanResult: Device MAC: {macaddress}")
    Logger.debug(f"BLE: onScanResult: UUIDs: {uuids}")

    res = BLEScanResult(macaddress, name, uuids, result.getDevice(), record)

    # 0000ffff-0000-1000-8000-00805f9b34fb
    self.Parent._addEntry(res)

  def setParent(self, parent):
    """
    At some point pyjnius became unable to find classes if not run in the main thread.
    This is a problem, because we want to run this in a background thread.
    So, we init the class in the main thread, then set the parent elsewhere before
    using the class.
    """
    self.Parent = parent

  def __init__(self,):
    super(PyScanCallback, self).__init__() 
