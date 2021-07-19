from kivy.logger import Logger
from jnius import PythonJavaClass, autoclass, cast, java_method
from collections import deque
import time

from dataclasses import dataclass
from typing import List, Dict, Any

from ble.bleexceptions import BLEAlreadyScanning
from ble.android.pyscancallback import PyScanCallback
from ble.blescanresult import BLEScanResult

class BLEScanTool:
  """
  Wraps everything to do with scanning, as it's a lot of code.

  This is written under the assumption that BLE callbacks are running in a
  different thread. Uses collections.deque, which is thread-safe.

  A particular scantool object should only ever be used (ie. calling
  getSeenEntries) by a single thread. This is because the Seen dict is
  updated in the context of the calling thread, from a threadsafe queue
  updated by callbacks.

  Only one scantool object should be scanning at a time.
  """
  def __init__(self):
    self.ScanQ = deque() # Thread safe, in case callbacks are in another thread
    self.Seen = {}   # Results of the current scan
    self.Previous = {} # Results of previous scans
    self.StartTime = time.time()
    self.Duration = 0.0
    self.Scanning = False

  def getSeenEntries(self) -> Dict[str, BLEScanResult]:
    """
    Returns entries seen in this scan so far
    """
    try:
      while True:
        item = self.ScanQ.popleft()
        self.Seen[item.MAC] = item
    except IndexError:
      pass

    return self.Seen

  def isScanning(self):
    return self.Scanning

  def scanTimeLeft(self):
    """
    Returns the amount of time left in this scan.

    0.0 means scanning completed (or has never happened)
    """
    left = self.Duration - (time.time() - self.StartTime)
    if left > 0.0:
      return left
    else:
      return 0.0

  def getPreviousEntries(self) -> Dict[str, BLEScanResult]:
    """
    Returns every entry seen before the most recent scan.

    ie. This is a way to find the results of previous scans.
    """
    return self.Previous

  def _addEntry(self, entry: BLEScanResult):
    """
    Internal call to add scanned entries
    """
    self.ScanQ.append(entry)
    tdelta = time.time() - self.StartTime
    if tdelta > self.Duration:
      # We have been scanning for long enough
      self.BLEScanner.stopScan(self.ScanCallback)
      self.Scanning = False
      Logger.debug("Duration reached. Asking Android to stop scan.");

  def _resetTimer(self):
    """
    Sets timestamp to now, so we can measure the duration of a scan
    """
    self.StartTime = time.time()

  def startScan(self, duration: float):
    """
    Copy self.Seen to self.Previous and fill self.Seen with new entries for "duration" seconds.

    Raises a BLEAlreadyScanning exception if a scan is already running.
    """
    if self.isScanning():
      raise BLEAlreadyScanning("A BLE scan is already running")

    self.Duration = duration
    for k in self.Seen.keys():
      self.Previous[k] = self.Seen[k]

    self.Seen = {}

    ScanCallbackImpl = autoclass("org/decentespresso/dedebug/ScanCallbackImpl")
    pycallback = PyScanCallback(self)

    self.BLEAdapterClass = autoclass('android.bluetooth.BluetoothAdapter')

    self.ScanCallback = ScanCallbackImpl()
    self.ScanCallback.setImpl(pycallback)
    
    # NB: pyjnius doesn't increase an objects refcount if it is given to a
    # java object, so we keep a local copy. Else it could be garbage
    # collected by the python vm, but not the java vm. This causes random
    # pyjnius "Could not invoke" errors on random unrelated types.

    self.ScanCallbackRef = pycallback

    self.BLEScanner = self.BLEAdapterClass.getBluetoothLeScanner()
    self.BLEScanner.stopScan(self.ScanCallback)
    self.BLEScanner.startScan(self.ScanCallback)
    self.Scanning = True
    self._resetTimer()
