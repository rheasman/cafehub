from dataclasses import dataclass
from typing import Any, List


@dataclass
class BLEScanResult:
    MAC: str
    name: str
    uuids: List[str]
    device: Any  # Used by platform specific code, if it needs to store more info
    record: Any  # Used by platform specific code, if it needs to store more info
