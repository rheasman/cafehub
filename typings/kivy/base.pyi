"""
This type stub file was generated by pyright.
"""

from kivy.event import EventDispatcher

'''
Kivy Base
=========

This modul'''
__all__ = ('EventLoop', 'EventLoopBase', 'ExceptionHandler', 'ExceptionManagerBase', 'ExceptionManager', 'runTouchApp', 'async_runTouchApp', 'stopTouchApp')
EventLoop = ...
class ExceptionHandler:
    '''Base handler that catches except'''
    def handle_exception(self, exception): # -> Literal[0]:
        '''Called by :class:`ExceptionManag'''
        ...
    


class ExceptionManagerBase:
    '''ExceptionManager manages excepti'''
    RAISE = ...
    PASS = ...
    def __init__(self) -> None:
        ...
    
    def add_handler(self, cls): # -> None:
        '''Add a new exception handler to t'''
        ...
    
    def remove_handler(self, cls): # -> None:
        '''Remove the exception handler fro'''
        ...
    
    def handle_exception(self, inst): # -> int:
        '''Called when an exception occurre'''
        ...
    


ExceptionManager: ExceptionManagerBase = ...
class EventLoopBase(EventDispatcher):
    '''Main event loop. This loop handl'''
    __events__ = ...
    def __init__(self) -> None:
        ...
    
    @property
    def touches(self): # -> list[Unknown]:
        '''Return the list of all touches c'''
        ...
    
    def ensure_window(self): # -> None:
        '''Ensure that we have a window.
  '''
        ...
    
    def set_window(self, window): # -> None:
        '''Set the window used for the even'''
        ...
    
    def add_input_provider(self, provider, auto_remove=...): # -> None:
        '''Add a new input provider to list'''
        ...
    
    def remove_input_provider(self, provider): # -> None:
        '''Remove an input provider.

     '''
        ...
    
    def add_event_listener(self, listener): # -> None:
        '''Add a new event listener for get'''
        ...
    
    def remove_event_listener(self, listener): # -> None:
        '''Remove an event listener from th'''
        ...
    
    def start(self): # -> None:
        '''Must be called before :meth:`Eve'''
        ...
    
    def close(self): # -> None:
        '''Exit from the main loop and stop'''
        ...
    
    def stop(self): # -> None:
        '''Stop all input providers and cal'''
        ...
    
    def add_postproc_module(self, mod): # -> None:
        '''Add a postproc input module (Dou'''
        ...
    
    def remove_postproc_module(self, mod): # -> None:
        '''Remove a postproc module.'''
        ...
    
    def remove_android_splash(self, *args): # -> None:
        '''Remove android presplash in SDL2'''
        ...
    
    def post_dispatch_input(self, etype, me):
        '''This function is called by :meth'''
        ...
    
    def dispatch_input(self): # -> None:
        '''Called by :meth:`EventLoopBase.i'''
        ...
    
    def mainloop(self): # -> None:
        ...
    
    async def async_mainloop(self): # -> None:
        ...
    
    def idle(self): # -> bool:
        '''This function is called after ev'''
        ...
    
    async def async_idle(self): # -> bool:
        '''Identical to :meth:`idle`, but i'''
        ...
    
    def run(self): # -> None:
        '''Main loop'''
        ...
    
    def exit(self): # -> None:
        '''Close the main loop and close th'''
        ...
    
    def on_stop(self): # -> None:
        '''Event handler for `on_stop` even'''
        ...
    
    def on_pause(self): # -> None:
        '''Event handler for `on_pause` whi'''
        ...
    
    def on_start(self): # -> None:
        '''Event handler for `on_start` whi'''
        ...
    


EventLoop = ...
def runTouchApp(widget=..., embedded=...): # -> None:
    '''Static main function that starts'''
    ...

async def async_runTouchApp(widget=..., embedded=..., async_lib=...): # -> None:
    '''Identical to :func:`runTouchApp`'''
    ...

def stopTouchApp(): # -> None:
    '''Stop the current application by '''
    ...
