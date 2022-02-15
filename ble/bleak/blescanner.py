import asyncio
import threading
import time
from collections import deque
from typing import Dict

from bleak import BleakScanner
from kivy.logger import Logger

from ble.bleexceptions import BLEAlreadyScanning
from ble.blescanresult import BLEScanResult
from ble.bgasyncthread import run_coroutine_threadsafe


class BLEScanTool:
    """
    Wraps everything to do with scanning, using bleak

    This is written under the assumption that BLE callbacks are running in a
    different thread. Uses collections.deque, which is thread-safe.

    A particular scantool object should only ever be used (ie. calling
    getSeenEntries) by a single thread. This is because the Seen dict is
    updated in the context of the calling thread, from a threadsafe queue
    updated by callbacks.

    Only one scantool object should be scanning at a time.
    """

    def __init__(self):
        self.ScanQ = deque()  # Thread safe, in case callbacks are in another thread
        self.Seen = {}  # Results of the current scan
        self.Previous = {}  # Results of previous scans
        self.StartTime = time.time()
        self.Duration = 0.0
        self.Scanning = False
        self.RequestStop = False
        self.Thread = threading.Thread(name='BleakScanner', daemon=True, target=self._bgScanThread)

    def getSeenEntries(self) -> Dict[str, BLEScanResult]:
        """
        Returns entries seen in this scan so far
        """
        Logger.debug("BLE: getSeenEntries()")
        try:
            while True:
                item = self.ScanQ.popleft()
                self.Seen[item.MAC] = item
        except IndexError:
            pass

        return self.Seen

    def stopScanning(self):
        self.RequestStop = True

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
            self.RequestStop = True

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

        self.Scanning = False
        self.RequestStop = False

        if self.Thread.is_alive():
            # In case thread hasn't terminated gracefully yet
            self.Thread.join()

        self.Thread = threading.Thread(name='BleakScanner', daemon=True, target=self._bgScanThread)

        self.Thread.start()

        self.Duration = duration
        for k in self.Seen.keys():
            self.Previous[k] = self.Seen[k]

        self.Seen = {}
        self.Scanning = True
        self._resetTimer()

    def _bgScanThread(self):
        Logger.debug("starting _bgScanThread()")
        run_coroutine_threadsafe(self._bgScan())
        Logger.info("Exiting _bgScanThread")

    async def _bgScan(self):
        self.BLEScanner = BleakScanner()
        self.BLEScanner.register_detection_callback(self.detection_callback)
        await self.BLEScanner.start()
        Logger.debug("Bleak scanner started")

        while True:
            if (self.scanTimeLeft() == 0.0) or self.RequestStop:
                # Stop scanning
                await self.BLEScanner.stop()
                self.Scanning = False
                self.RequestStop = False
                Logger.info("Exiting _bgScan")
                return
            else:
                await asyncio.sleep(0.25)

    def detection_callback(self, device, advertisement_data):
        Logger.debug("BLE: Bleak BLE Scanner detection_callback(%s, %s)" % (device, advertisement_data))
        item = BLEScanResult(device.address, device.name, advertisement_data.service_uuids, None, None)
        self._addEntry(item)
