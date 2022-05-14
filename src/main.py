from abc import ABC, abstractmethod
import logging
import os
import enum
from typing import List

import typing
from typing import Any
from kivy.config import Config

from kivy.uix.widget import Widget

from webserver.httpserver import getlocalip

Config.set('graphics', 'maxfps', '10')

import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer


from kivy.logger import Logger, LOG_LEVELS

# Uncomment this to allow all non-Kivy loggers to output
logging.Logger.manager.root = Logger  # type: ignore

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

# coding: utf8
__version__ = '0.2'


SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.decentespresso.cafehub',
    servicename=u'Bleservice'
)

if platform == 'android':
    from jnius import autoclass # type: ignore
    from ble.android.androidtypes import *

    from android.permissions import request_permissions, Permission

    Context : T_Context = autoclass('android.content.Context')
    Intent : T_Intent = autoclass('android.content.Intent')
    PendingIntent : T_PendingIntent = autoclass('android.app.PendingIntent')
    AndroidString : T_Java_String = autoclass('java.lang.String')
    NotificationBuilder : T_NotificationBuilder = autoclass('android.app.Notification$Builder')
    Action : T_NotificationAction = autoclass('android.app.Notification$Action')
    PythonService : T_PythonService = autoclass('org.kivy.android.PythonService')
    PythonActivity : T_PythonActivity = autoclass('org.kivy.android.PythonActivity')
    BluetoothDevice : T_BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    String : T_Java_String = autoclass('java.lang.String')
    InvHandler : T_Native_Invocation_Handler = autoclass("org.jnius.NativeInvocationHandler")
    PowerManager : T_PowerManager = autoclass('android.os.PowerManager')
    BuildVersion : T_BuildVersion = autoclass("android.os.Build$VERSION")
    Settings : T_Settings = autoclass('android.provider.Settings')
    Uri : T_Uri = autoclass('android.net.Uri')

    def checkPermissions(activity : T_Activity):
        permbase = "android.permission."
        # PERMISSION_GRANTED = 0
        PERMISSION_DENIED = -1
        perms = [
                "INTERNET", 
                "ACCESS_COARSE_LOCATION", 
                "ACCESS_FINE_LOCATION", 
                "BLUETOOTH", 
                "BLUETOOTH_ADMIN", 
                "BLUETOOTH_PRIVILEGED",
                "WAKE_LOCK", 
                "FOREGROUND_SERVICE", 
                "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
        ]

        perms = [permbase+x for x in perms]

        needed : List[str] = []
        for perm in perms:
            if activity.checkSelfPermission(perm) == PERMISSION_DENIED:
                Logger.info(f"Main: We do not have permission {perm}")
                needed.append(perm)
            else:
                Logger.info(f"Main: We have permission {perm}")

        if len(needed):
            Logger.info(f"Main: Requesting permissions for: {needed}")
            request_permissions(needed)


class Stacks(enum.Enum):
    BLEAK   = 1
    ANDROID = 2
    UNKNOWN = 3

Use_Stack = Stacks.UNKNOWN

if platform in ('linux', 'linux2', 'macos', 'win'):
    import services.bleakservice
    Use_Stack=Stacks.BLEAK

if platform == 'android':
    Use_Stack=Stacks.ANDROID

if Use_Stack == Stacks.UNKNOWN:
    raise NotImplementedError("Unsupported platform")


KV = '''
BoxLayout:
    orientation: 'vertical'

    BoxLayout:
        size_hint_y: None
        height: '60sp'
        Label:
            id: ipaddr
            font_size: 24

    ScrollView:
        Label:
            id: label
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.size[0], None

    BoxLayout:
        size_hint_y: None
        height: '120sp'
        Button:
            text: 'Stop & Exit'
            font_size: 36
            on_press: app.stop_service()
        Button:
            text: 'clear'
            font_size: 36
            on_press: label.text = ''
        Label:
            id: date
            font_size: 18

'''

class ClientServerApp(App, ABC):
    """
    The parts of the app that can run on any device
    """
    def build(self) -> Widget :
        self.service = None

        self.server = server = OSCThreadServer()
        server.listen(
            address='localhost',
            port=4002,
            default=True,
        )

        # /message will be used to display debug info
        server.bind(b'/message', self.display_message)

        # /date is updated by the other side once a second
        # so you can tell that it's still running.
        server.bind(b'/date', self.date)

        self.client = OSCClient(b'localhost', 4000)
        self.root = Builder.load_string(KV)
        self.root.ids.ipaddr.text = f"IP Address: {getlocalip()}"
        return self.root

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def start_service(self):
        pass

    @abstractmethod
    def stop_service(self):
        pass

    def send(self, *args : Any):
        self.client.send_message(b'/ping', [])

    def display_message(self, message : bytes):
        if self.root:
            self.root.ids.label.text += '{}\n'.format(message.decode('utf8'))  # type: ignore

    def date(self, message : bytes):
        if self.root:
            self.root.ids.date.text = message.decode('utf8')  # type: ignore

class ClientServerAndroidApp(ClientServerApp):
    """
    The parts of the app that are Android specific
    """
    def requestBLEEnableIfRequired(self) -> bool:
        """
        Asks the user to enable BLE if required.
        Right now, has no way to tell if the user succeeded.
        Requires receiving an activity result that seems to need setup in the
        APK, which gets in the way of testing using kivy_launcher.

        Returns True if a request was generated for the user. Check for Activy result.
        Returns False if no request needed. Do nothing.
        """
        Logger.debug("requestBLEEnableIfRequired()")
        BLEAdapterClass : T_BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        enableBtIntent : T_Intent = Intent()
        enableBtIntent.setAction(BLEAdapterClass.ACTION_REQUEST_ENABLE)
        PythonActivity.mActivity.startActivityForResult(enableBtIntent, 0x1)
        return True

    def on_start(self):
        if platform == 'android':
            Logger.debug("Main: SDK_INT: %s" % (BuildVersion.SDK_INT,))
            self.requestBLEEnableIfRequired()
            pa : T_PythonActivity = autoclass(u'org.kivy.android.PythonActivity')
            mActivity : T_Activity = pa.mActivity
            checkPermissions(mActivity)
            pm : T_PowerManager = typing.cast(T_PowerManager, mActivity.getSystemService(Context.POWER_SERVICE))
            wl : T_PowerManager.WakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, 'CafeHub:BLEProxy')

            wl.acquire()

            if BuildVersion.SDK_INT >= 23: # Build.VERSION_CODES.M) {
                intent = Intent()
                packageName = u"org.decentespresso.cafehub"
                if not pm.isIgnoringBatteryOptimizations(packageName):
                    intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                    intent.setData(Uri.parse("package:" + packageName))
                    mActivity.startActivity(intent)
            
            self.start_service()

    def start_service(self):
        if platform == 'android':
            service : T_BLEService = autoclass(SERVICE_NAME)
            pa : T_PythonActivity = autoclass(u'org.kivy.android.PythonActivity')
            self.mActivity : T_Activity = pa.mActivity
            argument = ''

            service.start(self.mActivity, argument)
            self.androidservice = service

    def stop_service(self):
        if self.androidservice:
            self.client.send_message(b'/shutdown', [])
            self.stop()


class ClientServerBleakApp(ClientServerApp):
    """
    The parts of the app that are Bleak specific
    """
    def on_start(self):
        self.start_service()

    def start_service(self):
        if not self.service:
            self.service = services.bleakservice.GenericServer()
            self.service.start()

    def stop_service(self):
        if self.service:
            self.service.stop()
            self.service = None
            self.stop()


if __name__ == '__main__':
    if Use_Stack == Stacks.ANDROID:
        ClientServerAndroidApp().run()
    elif Use_Stack == Stacks.BLEAK:
        ClientServerBleakApp().run()