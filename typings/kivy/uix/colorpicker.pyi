"""
This type stub file was generated by pyright.
"""

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.graphics import InstructionGroup
from kivy.app import App

'''
Color Picker
============

.. v'''
__all__ = ('ColorPicker', 'ColorWheel')
def distance(pt1, pt2): # -> float:
    ...

def polar_to_rect(origin, r, theta): # -> tuple[Unknown, Unknown]:
    ...

def rect_to_polar(origin, x, y): # -> tuple[Literal[0], Literal[0]] | tuple[Unknown, float] | tuple[float, float]:
    ...

class ColorWheel(Widget):
    '''Chromatic wheel for the ColorPic'''
    r = ...
    g = ...
    b = ...
    a = ...
    color = ...
    _origin = ...
    _radius = ...
    _piece_divisions = ...
    _pieces_of_pie = ...
    _inertia_slowdown = ...
    _inertia_cutoff = ...
    _num_touches = ...
    _pinch_flag = ...
    _hsv = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def on__origin(self, instance, value): # -> None:
        ...
    
    def on__radius(self, instance, value): # -> None:
        ...
    
    def init_wheel(self, dt): # -> None:
        ...
    
    def recolor_wheel(self): # -> None:
        ...
    
    def change_alpha(self, val): # -> None:
        ...
    
    def inertial_incr_sv_idx(self, dt): # -> Literal[False] | None:
        ...
    
    def inertial_decr_sv_idx(self, dt): # -> Literal[False] | None:
        ...
    
    def on_touch_down(self, touch): # -> Literal[False] | None:
        ...
    
    def on_touch_move(self, touch): # -> None:
        ...
    
    def on_touch_up(self, touch): # -> None:
        ...
    


class _ColorArc(InstructionGroup):
    def __init__(self, r_min, r_max, theta_min, theta_max, color=..., origin=..., **kwargs) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    def get_mesh(self):
        ...
    
    def change_color(self, color=..., color_delta=..., sv=..., a=...): # -> None:
        ...
    


class ColorPicker(RelativeLayout):
    '''
    See module documentation.
 '''
    font_name = ...
    color = ...
    hsv = ...
    hex_color = ...
    wheel = ...
    _update_clr_ev = ...
    foreground_color = ...
    def set_color(self, color): # -> None:
        ...
    
    def __init__(self, **kwargs) -> None:
        ...
    


if __name__ in ('__android__', '__main__'):
    class ColorPickerApp(App):
        def build(self): # -> ColorPicker:
            ...
        
    
    
