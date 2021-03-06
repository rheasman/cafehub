"""
This type stub file was generated by pyright.
"""

from typing import List, NamedTuple, Optional
from bleak_winrt.windows.devices.bluetooth.advertisement import BluetoothLEAdvertisementReceivedEventArgs
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import BaseBleakScanner

logger = ...
_here = ...
class _RawAdvData(NamedTuple):
    """
    Platform-specific advertise"""
    adv: BluetoothLEAdvertisementReceivedEventArgs
    scan: Optional[BluetoothLEAdvertisementReceivedEventArgs]
    ...


class BleakScannerWinRT(BaseBleakScanner):
    """The native Windows Bleak BLE Sca"""
    def __init__(self, **kwargs) -> None:
        ...
    
    async def start(self): # -> None:
        ...
    
    async def stop(self): # -> None:
        ...
    
    def set_scanning_filter(self, **kwargs): # -> None:
        """Set a scanning filter for the Bl"""
        ...
    
    @property
    def discovered_devices(self) -> List[BLEDevice]:
        ...
    


