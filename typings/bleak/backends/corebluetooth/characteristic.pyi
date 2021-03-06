"""
This type stub file was generated by pyright.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from CoreBluetooth import CBCharacteristic
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.corebluetooth.descriptor import BleakGATTDescriptorCoreBluetooth

"""
Interface class for the Bleak r"""
class CBCharacteristicProperties(Enum):
    BROADCAST = ...
    READ = ...
    WRITE_WITHOUT_RESPONSE = ...
    WRITE = ...
    NOTIFY = ...
    INDICATE = ...
    AUTHENTICATED_SIGNED_WRITES = ...
    EXTENDED_PROPERTIES = ...
    NOTIFY_ENCRYPTION_REQUIRED = ...
    INDICATE_ENCRYPTION_REQUIRED = ...


_GattCharacteristicsPropertiesEnum: Dict[Optional[int], Tuple[str, str]] = ...
class BleakGATTCharacteristicCoreBluetooth(BleakGATTCharacteristic):
    """GATT Characteristic implementati"""
    def __init__(self, obj: CBCharacteristic) -> None:
        ...
    
    @property
    def service_uuid(self) -> str:
        """The uuid of the Service containi"""
        ...
    
    @property
    def service_handle(self) -> int:
        ...
    
    @property
    def handle(self) -> int:
        """Integer handle for this characte"""
        ...
    
    @property
    def uuid(self) -> str:
        """The uuid of this characteristic"""
        ...
    
    @property
    def properties(self) -> List[str]:
        """Properties of this characteristi"""
        ...
    
    @property
    def descriptors(self) -> List[BleakGATTDescriptorCoreBluetooth]:
        """List of descriptors for this ser"""
        ...
    
    def get_descriptor(self, specifier) -> Union[BleakGATTDescriptorCoreBluetooth, None]:
        """Get a descriptor by handle (int)"""
        ...
    
    def add_descriptor(self, descriptor: BleakGATTDescriptorCoreBluetooth): # -> None:
        """Add a :py:class:`~BleakGATTDescr"""
        ...
    


