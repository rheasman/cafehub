"""
This type stub file was generated by pyright.
"""

import os
import kivy.input.providers.tuio
import kivy.input.providers.mouse
from kivy.utils import platform as core_platform
from kivy.logger import Logger
from kivy.setupconfig import USE_SDL2

'''
Providers
=========

'''
platform = ...
if platform == 'win' or 'KIVY_DOC' in os.environ:
    ...
if platform == 'macosx' or 'KIVY_DOC' in os.environ:
    ...
if platform == 'linux' or 'KIVY_DOC' in os.environ:
    ...
if (platform == 'android' and notUSE_SDL2) or 'KIVY_DOC' in os.environ:
    ...