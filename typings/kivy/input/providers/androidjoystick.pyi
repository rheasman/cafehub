"""
This type stub file was generated by pyright.
"""

import os
from kivy.input.provider import MotionEventProvider
from kivy.input.motionevent import MotionEvent

'''
Android Joystick Input Provider'''
__all__ = ('AndroidMotionEventProvider', )
if 'KIVY_DOC' not in os.environ:
    ...
class AndroidMotionEvent(MotionEvent):
    def __init__(self, *args, **kwargs) -> None:
        ...
    
    def depack(self, args): # -> None:
        ...
    


class AndroidMotionEventProvider(MotionEventProvider):
    def __init__(self, device, args) -> None:
        ...
    
    def create_joystick(self, index): # -> None:
        ...
    
    def start(self): # -> None:
        ...
    
    def stop(self): # -> None:
        ...
    
    def update(self, dispatch_fn):
        ...
    


