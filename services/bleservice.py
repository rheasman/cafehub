from jnius import autoclass
import asyncio
import json
import logging
import os
import threading
import wsserver.server

import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform

from jnius import autoclass

from kivy.logger import Logger, LOG_LEVELS

# Uncomment this to allow all non-Kivy loggers to output
logging.Logger.manager.root = Logger  # type: ignore

from ble.ble import BLE

Logger.debug("SYS:" + os.path.dirname(kivy.__file__))

from kivy.config import Config

# Config.setInt('kivy', 'log_maxfiles', 1)
fpath = os.path.dirname(os.path.abspath(__file__))
logfilepath = os.path.join(fpath, '.kivy/logs/')
try:
    os.remove(os.path.join(logfilepath, 'lastlog.txt'))
except OSError:
    pass

Logger.setLevel(LOG_LEVELS["critical"])
Config.set('kivy', 'log_maxfiles', 1)
Config.set('kivy', 'log_dir', logfilepath)
Logger.setLevel(LOG_LEVELS["debug"])
Config.set('kivy', 'log_name', 'lastlog.txt')
# Config.set('kivy', 'kivy_clock', 'free_only')

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.clock import Clock
from ble.bleops import QOpExecutorFactory, exceptionCatcherForAsyncDecorator

import traceback
import functools

if __name__ == '__main__':
    server = wsserver.server.SyncWSServer(Logger)
