"""
This type stub file was generated by pyright.
"""

'''
Button Behavior
==============='''
__all__ = ('ButtonBehavior', )
class ButtonBehavior:
    '''
    This `mixin <https://en.wik'''
    state = ...
    last_touch = ...
    min_state_time = ...
    always_release = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def cancel_event(self, *args): # -> None:
        ...
    
    def on_touch_down(self, touch): # -> bool:
        ...
    
    def on_touch_move(self, touch): # -> bool:
        ...
    
    def on_touch_up(self, touch): # -> Literal[True] | None:
        ...
    
    def on_press(self): # -> None:
        ...
    
    def on_release(self): # -> None:
        ...
    
    def trigger_action(self, duration=...): # -> None:
        '''Trigger whatever action(s) have '''
        ...
    

