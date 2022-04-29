"""
This type stub file was generated by pyright.
"""

from kivy.config import Config

'''
Focus Behavior
==============

'''
__all__ = ('FocusBehavior', )
_is_desktop = ...
_keyboard_mode = ...
if Config:
    _is_desktop = ...
    _keyboard_mode = ...
class FocusBehavior:
    '''Provides keyboard focus behavior'''
    _requested_keyboard = ...
    _keyboard = ...
    _keyboards = ...
    ignored_touch = ...
    keyboard = ...
    is_focusable = ...
    focus = ...
    focused = ...
    keyboard_suggestions = ...
    focus_next = ...
    focus_previous = ...
    keyboard_mode = ...
    input_type = ...
    unfocus_on_touch = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def keyboard_on_textinput(self, window, text): # -> None:
        ...
    
    def on_touch_down(self, touch): # -> None:
        ...
    
    def get_focus_next(self):
        '''Returns the next focusable widge'''
        ...
    
    def get_focus_previous(self):
        '''Returns the previous focusable w'''
        ...
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers): # -> bool:
        '''The method bound to the keyboard'''
        ...
    
    def keyboard_on_key_up(self, window, keycode): # -> bool:
        '''The method bound to the keyboard'''
        ...
    
    def show_keyboard(self): # -> None:
        '''
        Convenience function to'''
        ...
    
    def hide_keyboard(self): # -> None:
        '''
        Convenience function to'''
        ...
    


