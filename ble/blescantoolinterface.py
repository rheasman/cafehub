import abc
from typing import List, Dict, Any
from blescanresult import BLEScanResult


class BLEScanTool(metaclass=abc.ABCMeta):
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

  @abc.abstractmethod
  def getSeenEntries(self) -> Dict[BLEScanResult]:
    """
    Returns entries seen in this scan so far
    """

  @abc.abstractmethod
  def isScanning(self) -> bool:
    """
    Return True if a scan is in progress, else False
    """

  @abc.abstractmethod
  def scanTimeLeft(self) -> float:
    """
    Returns the amount of time left in this scan.

    0.0 means scanning completed (or has never happened)
    """

  @abc.abstractmethod
  def getPreviousEntries(self) -> Dict[BLEScanResult]:
    """
    Returns every entry seen before the most recent scan.

    ie. This is a way to find the results of previous scans.
    """

  @abc.abstractmethod
  def startScan(self, duration):
    """
    Copy self.Seen to self.Previous and fill self.Seen with new entries for "duration" seconds.

    Raises a BLEAlreadyScanning exception if a scan is already running.
    """
