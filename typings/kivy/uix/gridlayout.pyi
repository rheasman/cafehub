"""
This type stub file was generated by pyright.
"""

from kivy.uix.layout import Layout

'''
Grid Layout
===========

.. onl'''
__all__ = ('GridLayout', 'GridLayoutException')
def nmax(*args):
    ...

def nmin(*args):
    ...

class GridLayoutException(Exception):
    '''Exception for errors if the grid'''
    ...


class GridLayout(Layout):
    '''Grid layout class. See module do'''
    spacing = ...
    padding = ...
    cols = ...
    rows = ...
    col_default_width = ...
    row_default_height = ...
    col_force_default = ...
    row_force_default = ...
    cols_minimum = ...
    rows_minimum = ...
    minimum_width = ...
    minimum_height = ...
    minimum_size = ...
    orientation = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def get_max_widgets(self): # -> None:
        ...
    
    def on_children(self, instance, value): # -> None:
        ...
    
    def do_layout(self, *largs):
        ...
    


