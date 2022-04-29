from typing import Any


class ConfigParser:
    name: str
    def __init__(self, name: str = ...) -> None: ...
    def set(self, k1 : str, k2 : str, val : Any) -> None: ...

Config: ConfigParser