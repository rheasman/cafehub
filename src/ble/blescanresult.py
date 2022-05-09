from dataclasses import dataclass
from typing import Any, List, Union


@dataclass
class BLEScanResult:
    MAC: str
    name: Union[str, None]
    uuids: List[str]
    device: Any  # Used by platform specific code, if it needs to store more info
    record: Any  # Used by platform specific code, if it needs to store more info
