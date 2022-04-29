"""
This type stub file was generated by pyright.
"""

from kivy import Logger
from kivy.core import core_select_lib
from kivy.utils import platform
from kivy.setupconfig import USE_SDL2

'''
Clipboard
=========

Core class'''
__all__ = ('ClipboardBase', 'Clipboard')
class ClipboardBase:
    def get(self, mimetype): # -> None:
        '''Get the current data in clipboar'''
        ...
    
    def put(self, data, mimetype): # -> None:
        '''Put data on the clipboard, and a'''
        ...
    
    def get_types(self): # -> list[Unknown]:
        '''Return a list of supported mimet'''
        ...
    
    def copy(self, data=...): # -> None:
        ''' Copy the value provided in argu'''
        ...
    
    def paste(self): # -> Literal['']:
        ''' Get text from the system clipbo'''
        ...
    


_clipboards = ...
if platform == 'android':
    ...
else:
    ...
if USE_SDL2:
    ...
else:
    ...
Clipboard = ...
CutBuffer = ...
if platform == 'linux':
    _cutbuffers = ...