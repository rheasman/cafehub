"""
This type stub file was generated by pyright.
"""

import os
from kivy.input.motionevent import MotionEvent
from kivy.input.provider import MotionEventProvider

'''
Support for WM_TOUCH messages ('''
__all__ = ('WM_MotionEventProvider', 'WM_MotionEvent')
Window = ...
class WM_MotionEvent(MotionEvent):
    '''MotionEvent representing the WM_'''
    __attrs__ = ...
    def __init__(self, *args, **kwargs) -> None:
        ...
    
    def depack(self, args): # -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


if 'KIVY_DOC' in os.environ:
    WM_MotionEventProvider = ...
else:
    class WM_MotionEventProvider(MotionEventProvider):
        def start(self): # -> None:
            ...
        
        def update(self, dispatch_fn): # -> None:
            ...
        
        def stop(self): # -> None:
            ...
        
    
    
