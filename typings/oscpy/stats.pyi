"""
This type stub file was generated by pyright.
"""

"Simple utility class to gather s"
from typing import Any


class Stats:
    def __init__(self, calls : int=..., bytes : int =..., params : int =..., types : Any =..., **kwargs : Any) -> None:
        ...
    
    def to_tuple(self): # -> tuple[Unknown | str, ...]:
        ...
    
    def __iadd__(self, other): # -> Self@Stats:
        ...
    
    def __add__(self, other): # -> Stats:
        ...
    
    def __eq__(self, other) -> bool:
        ...
    
    def __repr__(self): # -> str:
        ...
    

