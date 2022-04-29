"""
This type stub file was generated by pyright.
"""

import abc
from typing import Any, Callable, Optional, Union
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTServiceCollection
import uuid

"""
Base class for backend clients."""
class BaseBleakClient(abc.ABC):
    """The Client Interface for Bleak B"""
    def __init__(self, address_or_ble_device: Union[BLEDevice, str], **kwargs : Any) -> None:
        self.services : BleakGATTServiceCollection
        self.address  : str
    
    def __str__(self) -> str:
        ...
    
    def __repr__(self) -> str: # -> str:
        ...
    
    async def __aenter__(self) -> BaseBleakClient:
        ...
    
    async def __aexit__(self, exc_type : Any, exc_val : Any, exc_tb : Any) -> None:
        ...
    
    def set_disconnected_callback(self, callback: Optional[Callable[[BaseBleakClient], None]]) -> None:
        ...
    
    async def connect(self, **kwargs: Any) -> bool:
        ...

    async def get_services(self, **kwargs : Any) -> BleakGATTServiceCollection:
        ...

    async def disconnect(self) -> bool:
        ...

    async def write_gatt_char(self, char_specifier: Union[BleakGATTCharacteristic, int, str, uuid.UUID], data: Union[bytes, bytearray, memoryview], response: bool = ...) -> None:
        ...

    async def read_gatt_char(self, char_specifier: Union[BleakGATTCharacteristic, int, str, uuid.UUID], **kwargs : Any) -> bytearray:
        ...

    async def start_notify(self, char_specifier: Union[BleakGATTCharacteristic, int, str, uuid.UUID], callback: Callable[[int, bytearray], None], **kwargs: bool) -> None:
        ...
    
    async def stop_notify(self, char_specifier: Union[BleakGATTCharacteristic, int, str, uuid.UUID]) -> None:
        ...

    def is_connected(self) -> bool: ...


class BleakClient(BaseBleakClient):
    pass