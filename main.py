from jnius import autoclass
import logging
import os

from kivy.config import Config

Config.set('graphics', 'maxfps', '10')

import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform

from jnius import autoclass

from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer


# kivy.require('2.0.0')

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
from kivy.clock import Clock

# coding: utf8
__version__ = '0.2'


SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.decentespresso.dedebug',
    servicename=u'Bleservice'
)

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
AndroidString = autoclass('java.lang.String')
NotificationBuilder = autoclass('android.app.Notification$Builder')
Action = autoclass('android.app.Notification$Action')
PythonService = autoclass('org.kivy.android.PythonService')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
String = autoclass('java.lang.String')
InvHandler = autoclass("org.jnius.NativeInvocationHandler")
PowerManager = autoclass('android.os.PowerManager')
BuildVersion = autoclass("android.os.Build$VERSION")
Settings = autoclass('android.provider.Settings')
Uri = autoclass('android.net.Uri')

KV = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: '120sp'
        Button:
            text: 'start service'
            on_press: app.start_service()
        Button:
            text: 'stop service'
            on_press: app.stop_service()

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
            text: 'ping'
            on_press: app.send()
        Button:
            text: 'clear'
            on_press: label.text = ''
        Label:
            id: date

'''

class ClientServerApp(App):
    def build(self):
        self.service = None

        self.server = server = OSCThreadServer()
        server.listen(
            address='localhost',
            port=3002,
            default=True,
        )

        server.bind(b'/message', self.display_message)
        server.bind(b'/date', self.date)

        self.client = OSCClient(b'localhost', 3000)
        self.root = Builder.load_string(KV)
        return self.root
    
    def on_start(self):
        Logger.debug("Main: SDK_INT: %s" % (BuildVersion.SDK_INT,))
        
        mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
        pm = mActivity.getSystemService(Context.POWER_SERVICE)
        wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, 'TAG')

        wl.acquire()

        if BuildVersion.SDK_INT >= 23: # Build.VERSION_CODES.M) {
            intent = Intent()
            packageName = u"org.decentespresso.dedebug"
            if not pm.isIgnoringBatteryOptimizations(packageName):
                intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                intent.setData(Uri.parse("package:" + packageName))
                mActivity.startActivity(intent)
        self.start_service()

    def start_service(self):
        if platform == 'android':

            service = autoclass(SERVICE_NAME)
            self.mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''

            if BuildVersion.SDK_INT > 26: # VERSION_CODES.O
                service.startForegroundService(self.mActivity, argument)
            else:
                service.start(self.mActivity, argument)
            self.service = service

        elif platform in ('linux', 'linux2', 'macos', 'win'):
            from runpy import run_path
            from threading import Thread
            self.service = Thread(
                target=run_path,
                args=['service/service.py'],
                kwargs={'run_name': '__main__'},
                daemon=True
            )
            self.service.start()
        else:
            raise NotImplementedError(
                "service start not implemented on this platform"
            )

    def stop_service(self):
        if self.service:
            if platform == "android":
                self.service.stop(self.mActivity)
            elif platform in ('linux', 'linux2', 'macos', 'win'):
                self.service.stop()
            else:
                raise NotImplementedError(
                    "service start not implemented on this platform"
                )
            self.service = None

    def send(self, *args):
        self.client.send_message(b'/ping', [])

    def display_message(self, message):
        if self.root:
            self.root.ids.label.text += '{}\n'.format(message.decode('utf8'))

    def date(self, message):
        if self.root:
            self.root.ids.date.text = message.decode('utf8')


if __name__ == '__main__':
    ClientServerApp().run()