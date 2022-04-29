"""
This type stub file was generated by pyright.
"""

from kivy.input.provider import MotionEventProvider
from kivy.input.motionevent import MotionEvent

'''
Mouse provider implementation
='''
__all__ = ('MouseMotionEventProvider', )
Color = ...
class MouseMotionEvent(MotionEvent):
    def __init__(self, *args, **kwargs) -> None:
        ...
    
    def depack(self, args): # -> None:
        ...
    
    def update_graphics(self, win, create=...): # -> None:
        ...
    
    def clear_graphics(self, win): # -> None:
        ...
    


class MouseMotionEventProvider(MotionEventProvider):
    __handlers__ = ...
    def __init__(self, device, args) -> None:
        ...
    
    disable_hover = ...
    def start(self): # -> None:
        '''Start the mouse provider'''
        ...
    
    def stop(self): # -> None:
        '''Stop the mouse provider'''
        ...
    
    def test_activity(self): # -> bool:
        ...
    
    def find_touch(self, win, x, y): # -> None:
        ...
    
    def create_event_id(self):
        ...
    
    def create_touch(self, win, nx, ny, is_double_tap, do_graphics, button): # -> MouseMotionEvent:
        ...
    
    def remove_touch(self, win, touch): # -> None:
        ...
    
    def create_hover(self, win, etype): # -> None:
        ...
    
    def on_mouse_motion(self, win, x, y, modifiers): # -> None:
        ...
    
    def on_mouse_press(self, win, x, y, button, modifiers): # -> None:
        ...
    
    def on_mouse_release(self, win, x, y, button, modifiers):
        ...
    
    def update_touch_graphics(self, win, *args): # -> None:
        ...
    
    def begin_or_update_hover_event(self, win, *args): # -> None:
        ...
    
    def begin_hover_event(self, win, *args): # -> None:
        ...
    
    def update_hover_event(self, win, *args): # -> None:
        ...
    
    def end_hover_event(self, win, *args): # -> None:
        ...
    
    def update(self, dispatch_fn): # -> None:
        '''Update the mouse provider (pop e'''
        ...
    

