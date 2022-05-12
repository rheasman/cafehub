from kivy.logger import Logger
from jnius import PythonJavaClass, java_method
from ble.android.androidtypes import T_JavaListOf, T_ScanResult
from ble.blescanresult import BLEScanResult
from ble.blescantoolinterface import I_BLEScanTool

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
  __javainterfaces__ = ["org/decentespresso/cafehub/ScanCallbackImpl$IScanCallback"]
  __javacontext__ = 'app'  # Use the app class resolver, not the system resolver.

  SCAN_FAILED_ALREADY_STARTED = 1
  SCAN_FAILED_APPLICATION_REGISTRATION_FAILED = 2
  SCAN_FAILED_FEATURE_UNSUPPORTED = 4
  SCAN_FAILED_INTERNAL_ERROR = 3

  @java_method('(Ljava/util/List;)V')
  def onBatchScanResults(self, srlist : T_JavaListOf[T_ScanResult]):
    # public void onBatchScanResults(List<ScanResult> results)
    Logger.debug(f"BLE: onBatchScanResults") #: {repr(srlist)}")

  @java_method('(I)V')
  def onScanFailed(self, errorCode : int):
    # void onScanFailed(int errorCode)
    Logger.debug(f"BLE: onScanFailed: {errorCode}")

  @java_method('(ILandroid/bluetooth/le/ScanResult;)V')
  def onScanResult(self, callbackType : int, result : T_ScanResult):
    # void onScanResult(int callbackType, ScanResult result);

    Logger.debug(f"BLE: onScanResult: callBackType: {callbackType}")
    record = result.getScanRecord()
    name = record.getDeviceName()
    if name:
      name = name.replace("\0", "")

    macaddress = result.device.getAddress()
    uuids = record.getServiceUuids()
    if uuids is not None:
      uuids = [x.toString() for x in uuids.toArray()]
    else:
      uuids = []
    Logger.debug(f"BLE: onScanResult: DeviceName: {name}")
    Logger.debug(f"BLE: onScanResult: Device MAC: {macaddress}")
    Logger.debug(f"BLE: onScanResult: UUIDs: {uuids}")

    res = BLEScanResult(macaddress, name, uuids, result.getDevice(), record)

    # 0000ffff-0000-1000-8000-00805f9b34fb
    self.Parent.addEntry(res)

  def setParent(self, parent: I_BLEScanTool):
    """
    At some point pyjnius became unable to find classes if not run in the main thread.
    This is a problem, because we want to run this in a background thread.
    So, we init the class in the main thread, then set the parent elsewhere before
    using the class.
    """
    self.Parent = parent

  def __init__(self):
    super(PyScanCallback, self).__init__() # type: ignore
