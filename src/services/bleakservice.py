from random import sample, randint
from string import ascii_letters
import threading
import logging
from time import localtime, asctime, sleep
from typing import Optional

from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

from kivy.logger import Logger, LOG_LEVELS
from MsgHandler import MsgHandler
from webserver.httpserver import BackgroundThreadedHTTPServer

Logger.setLevel(LOG_LEVELS["debug"])

# class E(ExceptionHandler):
#     def handle_exception(self, inst):
#         Logger.exception('Exception caught by ExceptionHandler')
#         MainApp.stop()
#         return ExceptionManager.PASS


# ExceptionManager.add_handler(E())

# Uncomment this to allow all non-Kivy loggers to output
logging.Logger.manager.root = Logger  # type: ignore

# Logger.debug("SYS:" + os.path.dirname(kivy.__file__))

CLIENT = OSCClient('localhost', 4002, encoding="UTF-8")

def ping():
    'answer to ping messages'
    CLIENT.send_message(
        b'/message',
        [
            ''.join(sample(ascii_letters, randint(10, 20)))
            .encode('utf8'),
        ],
    )


def send_date():
    'send date to the application'
    CLIENT.send_message(
        b'/date',
        [asctime(localtime()).encode('utf8'), ],
    )

import wsserver.server

class GenericServer:
    def __init__(self):
        self.WSServer : Optional[wsserver.server.SyncWSServer] = None
        self.httpserver : Optional[BackgroundThreadedHTTPServer] = None
        self.OscServer = OSCThreadServer()
        self.OscServer.listen('localhost', port=4000, default=True)
        self.OscServer.bind(b'/ping', ping)
        self.OscServer.bind(b'/stop', self.stop)

        self.StopEvent = threading.Event()
        self.thread = threading.Thread(target=self.dateserver, daemon=True)   
        Logger.addHandler(MsgHandler(oscclient=CLIENT))

        
    def start(self):
        if self.WSServer is None:
            self.WSServer = wsserver.server.SyncWSServer(Logger)
            self.thread.start()

        if self.httpserver is None:
            self.httpserver = BackgroundThreadedHTTPServer(5000, 3, "./webserverdata/test_app")
            self.httpserver.start()

    def stop(self):
        Logger.debug("BleakService: Stopping server")
        if self.WSServer:
            self.WSServer.shutdown()

        if self.httpserver:
            self.httpserver.shutdown()
            self.httpserver = None
            
        self.StopEvent.set()

    def dateserver(self):
        try:
            while not self.StopEvent.isSet():
                sleep(1)
                send_date()
        finally:
            pass
