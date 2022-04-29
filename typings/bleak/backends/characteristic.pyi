"""
This type stub file was generated by pyright.
"""

import abc
import enum
from uuid import UUID
from typing import Any, List, Union
from bleak.backends.descriptor import BleakGATTDescriptor

"""
Interface class for the Bleak r"""
class GattCharacteristicsFlags(enum.Enum):
    broadcast = ...
    read = ...
    write_without_response = ...
    write = ...
    notify = ...
    indicate = ...
    authenticated_signed_writes = ...
    extended_properties = ...
    reliable_write = ...
    writable_auxiliaries = ...


class BleakGATTCharacteristic(abc.ABC):
    """Interface for the Bleak represen"""
    def __init__(self, obj: Any) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    @property
    @abc.abstractmethod
    def service_uuid(self) -> str:
        """The UUID of the Service containi"""
        ...
    
    @property
    @abc.abstractmethod
    def service_handle(self) -> int:
        """The integer handle of the Servic"""
        ...
    
    @property
    @abc.abstractmethod
    def handle(self) -> int:
        """The handle for this characterist"""
        ...
    
    @property
    @abc.abstractmethod
    def uuid(self) -> str:
        """The UUID for this characteristic"""
        ...
    
    @property
    def description(self) -> str:
        """Description for this characteris"""
        ...
    
    @property
    @abc.abstractmethod
    def properties(self) -> List[str]:
        """Properties of this characteristi"""
        ...
    
    @property
    @abc.abstractmethod
    def descriptors(self) -> List:
        """List of descriptors for this ser"""
        ...
    
    @abc.abstractmethod
    def get_descriptor(self, specifier: Union[int, str, UUID]) -> Union[BleakGATTDescriptor, None]:
        """Get a descriptor by handle (int)"""
        ...
    
    @abc.abstractmethod
    def add_descriptor(self, descriptor: BleakGATTDescriptor):
        """Add a :py:class:`~BleakGATTDescr"""
        ...
    

