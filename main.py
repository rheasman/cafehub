import asyncio
import json
import os
from typing import *

import kivy

kivy.require('2.0.0')

from kivy.logger import Logger, LOG_LEVELS

# Uncomment this to allow all non-Kivy loggers to output
# logging.Logger.manager.root = Logger

print(os.path.dirname(kivy.__file__))

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
from ble.ble import BLE
from ble.bleops import QOpExecutorFactory, exceptionCatcherForAsyncDecorator

import traceback, functools


class KivyUICBConverter:
    """
    Converts a callback function to run in the Kivy execution loop. Will
    only run when the next frame is scheduled, so don't use this if
    speed is important.
    """

    def convert(self, fn):
        def wrapper(result):
            Clock.schedule_once(functools.partial(fn, result))

        return wrapper


class DEDebugApp(App):
    async def nice_async_run(self):
        try:
            return await self.async_run(async_lib='asyncio')
        except Exception as E:
            Logger.debug("EXCEPTION: %s" % (traceback.format_exc(),))
            raise  # re-raise exception to allow process in calling function

    def on_activity_result(self, requestCode, resultCode, data):
        Logger.info("### ACTIVITY CALLBACK ###", requestCode, resultCode, data)

    def on_new_intent(self, intent: Any) -> None:
        Logger.info("#### INTENT", intent)

    def build(self):
        Logger.info("UI: build()")
        root = Builder.load_file('./dedebugroot.kv')
        self.BLEScanWidget = root.ids.scanwidget

        # # ListView:
        # # id: logger
        # # adapter:
        # #     sla.SimpleListAdapter(data=[], cls=label.Label)

        return root

    def on_start(self):
        Logger.info("UI: on_start()")
        self.BLE = BLE(QOpExecutorFactory(), KivyUICBConverter())
        self.BLE.requestBLEEnableIfRequired()
        self.BLE.scanForDevices(4)
        self.ShownDevices = set()
        self.ScanEvent = Clock.schedule_interval(self.ble_scan_check, 0.5)

    def match_DE1_uuid(self, uuid) -> bool:
        if uuid is None:
            return False

        tomatch = '0000ffff-0000-1000-8000-00805f9b34fb'.split('-')[1:]
        matched = (tomatch == uuid.split('-')[1:])

        if matched:
            Logger.debug("UI: %s matched" % (uuid,))
        else:
            Logger.debug("UI: %s did not match" % (uuid,))

        return matched

    def match_DE1_uuid_list(self, uuidlist: List[str]) -> bool:
        for i in uuidlist:
            if self.match_DE1_uuid(i):
                return True

        return False

    def ble_scan_check(self, dt):
        """
        Runs and updates the view of BLE devices
        """
        Logger.debug("UI: Entering ble_scan_check()")
        sw = self.BLEScanWidget
        st = self.BLE.getBLEScanTool()
        if st is None:
            self.ScanEvent.cancel()
            return

        entries = st.getSeenEntries()
        for i in entries:
            if i not in self.ShownDevices:
                self.ShownDevices.add(i)
                Logger.debug(f"UI: ble_scan_check: {i} : {entries[i]}")
                item = entries[i]
                if (item.uuids is not None) and self.match_DE1_uuid_list(item.uuids) and item.name.startswith("DE1"):
                    sw.addDE1Node(item)
                else:
                    sw.addOtherNode(item)

        if st.isScanning():
            return

        # If we get here, we are done.
        Logger.info("UI: Cancelling ble_scan_check")
        self.ScanEvent.cancel()

        startedconn = False
        for i in self.ShownDevices:
            Logger.debug("UI: Found: %s" % i)

            item = entries[i]
            Logger.debug("UI: item: %s" % (item,))
            if (item.uuids is not None) and (self.match_DE1_uuid_list(item.uuids)) and item.name.startswith("DE1"):
                # We've found a DE1. Connect to it and break.
                with open('KnownDE1s.txt', 'w') as f:
                    json.dump(item.MAC, f)

                self.do_connect(item.MAC)
                startedconn = True
                break

        if not startedconn:
            # We haven't seen any DE1s this time.
            try:
                with open('KnownDE1s.txt', 'r') as f:
                    known = json.load(f)
                    self.do_connect(known)
            except FileNotFoundError as e:
                pass

    def do_connect(self, mac: str):
        self.DE1GATTClient = self.BLE.getGATTClient(mac)
        gc = self.DE1GATTClient
        gc.connect()
        Logger.debug("BLE: next")
        uuid = '0000a001-0000-1000-8000-00805f9b34fb'
        Logger.info("char_read: %s" % (gc.char_read(uuid),))
        gc.callback_char_read(uuid, callback=self.cb_cr_done)
        asyncio.run_coroutine_threadsafe(self.try_async_char_read(), asyncio.get_running_loop())

    @exceptionCatcherForAsyncDecorator
    async def try_async_char_read(self):
        Logger.debug("UI: try_async_char_read")
        r = await self.DE1GATTClient.async_char_read('0000a001-0000-1000-8000-00805f9b34fb')
        Logger.debug("async_char_read: %s" % (r,))

    def cb_cr_done(self, result, dt):
        Logger.debug("UI: cb_cr_done(%s, %s)" % (result.getResult(), dt))

    def cb_connect_done(self, result):
        Logger.info("BLE: cb_connect_done: %s" % (result,))

    def on_pause(self):
        self.BLE.on_pause()
        return True

    def on_resume(self):
        self.BLE.on_resume()
        return True

    def on_stop(self):
        Logger.debug("APP: on_stop()")
        if self.DE1GATTClient is not None:
            self.DE1GATTClient.disconnect()


if __name__ == '__main__':
    MainApp = DEDebugApp()
    from kivy.base import ExceptionHandler, ExceptionManager


    class E(ExceptionHandler):
        def handle_exception(self, inst):
            Logger.exception('Exception caught by ExceptionHandler')
            MainApp.stop()
            return ExceptionManager.PASS


    ExceptionManager.add_handler(E())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        MainApp.async_run(async_lib='asyncio')
    )
    loop.close()
