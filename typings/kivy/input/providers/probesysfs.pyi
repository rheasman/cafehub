"""
This type stub file was generated by pyright.
"""

import os
from kivy.input.provider import MotionEventProvider

'''
Auto Create Input Provider Conf'''
__all__ = ('ProbeSysfsHardwareProbe', )
if 'KIVY_DOC' in os.environ:
    ProbeSysfsHardwareProbe = ...
else:
    EventLoop = ...
    ABS_MT_POSITION_X = ...
    _cache_input = ...
    _cache_xinput = ...
    class Input:
        def __init__(self, path) -> None:
            ...
        
        @property
        def device(self): # -> str:
            ...
        
        @property
        def name(self): # -> str:
            ...
        
        def get_capabilities(self): # -> list[Unknown]:
            ...
        
        def has_capability(self, capability):
            ...
        
        @property
        def is_mouse(self):
            ...
        
    
    
    def getout(*args): # -> bytes | Literal['']:
        ...
    
    def query_xinput(): # -> None:
        ...
    
    def get_inputs(path): # -> list[Input]:
        ...
    
    def read_line(path): # -> str:
        ...
    
    class ProbeSysfsHardwareProbe(MotionEventProvider):
        def __new__(self, device, args): # -> None:
            ...
        
        def __init__(self, device, args) -> None:
            ...
        
        def should_use_mouse(self): # -> bool:
            ...
        
        def probe(self): # -> None:
            ...
        
    
    