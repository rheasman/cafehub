"""
This type stub file was generated by pyright.
"""

'''
Touch Ripple
============

.. v'''
__all__ = ('TouchRippleBehavior', 'TouchRippleButtonBehavior')
class TouchRippleBehavior:
    '''Touch ripple behavior.

    Supp'''
    ripple_rad_default = ...
    ripple_duration_in = ...
    ripple_duration_out = ...
    ripple_fade_from_alpha = ...
    ripple_fade_to_alpha = ...
    ripple_scale = ...
    ripple_func_in = ...
    ripple_func_out = ...
    ripple_rad = ...
    ripple_pos = ...
    ripple_color = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def ripple_show(self, touch): # -> None:
        '''Begin ripple animation on curren'''
        ...
    
    def ripple_fade(self): # -> None:
        '''Finish ripple animation on curre'''
        ...
    


class TouchRippleButtonBehavior(TouchRippleBehavior):
    '''
    This `mixin <https://en.wik'''
    last_touch = ...
    always_release = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def on_touch_down(self, touch): # -> bool:
        ...
    
    def on_touch_move(self, touch): # -> bool:
        ...
    
    def on_touch_up(self, touch): # -> Literal[True] | None:
        ...
    
    def on_disabled(self, instance, value):
        ...
    
    def on_press(self): # -> None:
        ...
    
    def on_release(self): # -> None:
        ...
    


