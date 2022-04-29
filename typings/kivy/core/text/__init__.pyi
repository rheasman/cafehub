"""
This type stub file was generated by pyright.
"""

import re
import os
from ast import literal_eval
from functools import partial
from copy import copy
from kivy import kivy_data_dir
from kivy.config import Config
from kivy.utils import platform
from kivy.graphics.texture import Texture
from kivy.core import core_select_lib
from kivy.core.text.text_layout import LayoutWord, layout_text
from kivy.resources import resource_add_path, resource_find
from kivy.compat import PY2
from kivy.setupconfig import USE_PANGOFT2, USE_SDL2

'''
Text
====

An abstraction of te'''
__all__ = ('LabelBase', 'Label', 'FontContextManagerBase', 'FontContextManager')
if 'KIVY_DOC' not in os.environ:
    _default_font_paths = ...
    DEFAULT_FONT = ...
else:
    DEFAULT_FONT = ...
FONT_REGULAR = ...
FONT_ITALIC = ...
FONT_BOLD = ...
FONT_BOLDITALIC = ...
whitespace_pat = ...
class LabelBase:
    '''Core text label.
    This is the'''
    __slots__ = ...
    _cached_lines = ...
    _fonts = ...
    _fonts_cache = ...
    _fonts_dirs = ...
    _font_dirs_files = ...
    _texture_1px = ...
    _font_family_support = ...
    def __init__(self, text=..., font_size=..., font_name=..., bold=..., italic=..., underline=..., strikethrough=..., font_family=..., halign=..., valign=..., shorten=..., text_size=..., mipmap=..., color=..., line_height=..., strip=..., strip_reflow=..., shorten_from=..., split_str=..., unicode_errors=..., font_hinting=..., font_kerning=..., font_blended=..., outline_width=..., outline_color=..., font_context=..., font_features=..., base_direction=..., text_language=..., **kwargs) -> None:
        ...
    
    @staticmethod
    def register(name, fn_regular, fn_italic=..., fn_bold=..., fn_bolditalic=...): # -> None:
        '''Register an alias for a Font.

 '''
        ...
    
    def resolve_font_name(self): # -> None:
        ...
    
    @staticmethod
    def get_system_fonts_dir(): # -> list[Unknown]:
        '''Return the directories used by t'''
        ...
    
    def get_extents(self, text): # -> tuple[Literal[0], Literal[0]]:
        '''Return a tuple (width, height) i'''
        ...
    
    def get_cached_extents(self): # -> (text: Unknown) -> tuple[Literal[0], Literal[0]]:
        '''Returns a cached version of the '''
        ...
    
    def shorten(self, text, margin=...):
        ''' Shortens the text to fit into a'''
        ...
    
    def clear_texture(self): # -> None:
        ...
    
    @staticmethod
    def find_base_direction(text): # -> Literal['ltr']:
        '''Searches a string the first char'''
        ...
    
    def render_lines(self, lines, options, render_text, y, size):
        ...
    
    def render(self, real=...):
        '''Return a tuple (width, height) t'''
        ...
    
    def refresh(self): # -> None:
        '''Force re-rendering of the text
 '''
        ...
    
    text = ...
    label = ...
    @property
    def texture_1px(self):
        ...
    
    @property
    def size(self): # -> tuple[Unknown, Unknown]:
        ...
    
    @property
    def width(self):
        ...
    
    @property
    def height(self):
        ...
    
    @property
    def content_width(self): # -> Literal[0]:
        '''Return the content width; i.e. t'''
        ...
    
    @property
    def content_height(self): # -> Literal[0]:
        '''Return the content height; i.e. '''
        ...
    
    @property
    def content_size(self): # -> tuple[Literal[0], Literal[0]] | tuple[Unknown | Literal[0], Unknown | Literal[0]]:
        '''Return the content size (width, '''
        ...
    
    @property
    def fontid(self): # -> str:
        '''Return a unique id for all font '''
        ...
    
    text_size = ...
    usersize = ...


class FontContextManagerBase:
    @staticmethod
    def create(font_context):
        '''Create a font context, you must '''
        ...
    
    @staticmethod
    def exists(font_context):
        '''Returns True if a font context w'''
        ...
    
    @staticmethod
    def destroy(font_context):
        '''Destroy a named font context (if'''
        ...
    
    @staticmethod
    def list():
        '''Returns a list of `bytes` object'''
        ...
    
    @staticmethod
    def list_families(font_context):
        '''Returns a list of `bytes` object'''
        ...
    
    @staticmethod
    def list_custom(font_context):
        '''Returns a dictionary representin'''
        ...
    
    @staticmethod
    def add_font(font_context, filename, autocreate=..., family=...):
        '''Add a font file to a named font '''
        ...
    


label_libs = ...
if USE_PANGOFT2:
    ...
if USE_SDL2:
    ...
else:
    ...
Text = ...
if 'KIVY_DOC' not in os.environ:
    ...