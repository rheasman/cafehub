"""
This type stub file was generated by pyright.
"""

import re
import imghdr
import zipfile
import sys
from base64 import b64decode
from kivy.event import EventDispatcher
from kivy.core import core_register_libs
from kivy.logger import Logger
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.atlas import Atlas
from kivy.resources import resource_find
from kivy.utils import platform
from kivy.compat import string_types
from kivy.setupconfig import USE_SDL2
from io import BytesIO
from os import environ
from kivy.graphics.texture import Texture, TextureRegion

'''
Image
=====

Core classes for l'''
__all__ = ('Image', 'ImageLoader', 'ImageData')
Texture = ...
class ImageData:
    '''Container for images and mipmap '''
    __slots__ = ...
    _supported_fmts = ...
    def __init__(self, width, height, fmt, data, source=..., flip_vertical=..., source_image=..., rowlength=...) -> None:
        ...
    
    def release_data(self): # -> None:
        ...
    
    @property
    def width(self):
        '''Image width in pixels.
        ('''
        ...
    
    @property
    def height(self):
        '''Image height in pixels.
        '''
        ...
    
    @property
    def data(self):
        '''Image data.
        (If the imag'''
        ...
    
    @property
    def rowlength(self):
        '''Image rowlength.
        (If the'''
        ...
    
    @property
    def size(self): # -> tuple[Unknown, Unknown]:
        '''Image (width, height) in pixels.'''
        ...
    
    @property
    def have_mipmap(self): # -> bool:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def add_mipmap(self, level, width, height, data, rowlength): # -> None:
        '''Add a image for a specific mipma'''
        ...
    
    def get_mipmap(self, level): # -> tuple[Unknown, Unknown, Unknown, Unknown]:
        '''Get the mipmap image at a specif'''
        ...
    
    def iterate_mipmaps(self): # -> Generator[tuple[int, Unknown, Unknown, Unknown, Unknown], None, None]:
        '''Iterate over all mipmap images a'''
        ...
    


class ImageLoaderBase:
    '''Base to implement an image loade'''
    __slots__ = ...
    def __init__(self, filename, **kwargs) -> None:
        ...
    
    def load(self, filename): # -> None:
        '''Load an image'''
        ...
    
    @staticmethod
    def can_save(fmt, is_bytesio=...): # -> Literal[False]:
        '''Indicate if the loader can save '''
        ...
    
    @staticmethod
    def can_load_memory(): # -> Literal[False]:
        '''Indicate if the loader can load '''
        ...
    
    @staticmethod
    def save(*largs, **kwargs):
        ...
    
    def populate(self): # -> None:
        ...
    
    @property
    def width(self):
        '''Image width
        '''
        ...
    
    @property
    def height(self):
        '''Image height
        '''
        ...
    
    @property
    def size(self): # -> tuple[Unknown, Unknown]:
        '''Image size (width, height)
     '''
        ...
    
    @property
    def texture(self): # -> None:
        '''Get the image texture (created o'''
        ...
    
    @property
    def textures(self): # -> list[Unknown] | None:
        '''Get the textures list (for mipma'''
        ...
    
    @property
    def nocache(self): # -> bool:
        '''Indicate if the texture will not'''
        ...
    


class ImageLoader:
    loaders = ...
    @staticmethod
    def zip_loader(filename, **kwargs):
        '''Read images from an zip file.

 '''
        ...
    
    @staticmethod
    def register(defcls): # -> None:
        ...
    
    @staticmethod
    def load(filename, **kwargs):
        ...
    


class Image(EventDispatcher):
    '''Load an image and store the size'''
    copy_attributes = ...
    data_uri_re = ...
    _anim_ev = ...
    def __init__(self, arg, **kwargs) -> None:
        ...
    
    def remove_from_cache(self): # -> None:
        '''Remove the Image from cache. Thi'''
        ...
    
    def anim_reset(self, allow_anim): # -> None:
        '''Reset an animation if available.'''
        ...
    
    anim_delay = ...
    @property
    def anim_available(self): # -> bool:
        '''Return True if this Image instan'''
        ...
    
    @property
    def anim_index(self): # -> int:
        '''Return the index number of the i'''
        ...
    
    def on_texture(self, *largs): # -> None:
        '''This event is fired when the tex'''
        ...
    
    @staticmethod
    def load(filename, **kwargs): # -> Image:
        '''Load an image

        :Paramete'''
        ...
    
    image = ...
    filename = ...
    def load_memory(self, data, ext, filename=...): # -> None:
        '''(internal) Method to load an ima'''
        ...
    
    @property
    def size(self): # -> list[int] | Any | tuple[Any | Unknown, Any | Unknown]:
        '''Image size (width, height)
     '''
        ...
    
    @property
    def width(self): # -> int | Any:
        '''Image width
        '''
        ...
    
    @property
    def height(self): # -> int | Any:
        '''Image height
        '''
        ...
    
    @property
    def texture(self): # -> Unknown | Any | None:
        '''Texture of the image'''
        ...
    
    @property
    def nocache(self): # -> bool:
        '''Indicate whether the texture wil'''
        ...
    
    def save(self, filename, flipped=..., fmt=...):
        '''Save image texture to file.

   '''
        ...
    
    def read_pixel(self, x, y): # -> list[float]:
        '''For a given local x/y position, '''
        ...
    


def load(filename): # -> Image:
    '''Load an image'''
    ...

image_libs = ...
if platform in ('macosx', 'ios'):
    ...
if USE_SDL2:
    ...
else:
    ...
libs_loaded = ...
if 'KIVY_DOC' not in environ and notlibs_loaded:
    ...