'p4a example service using oscpy to communicate with main application.'
from random import sample, randint
from string import ascii_letters
from time import localtime, asctime, sleep

from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

from jnius import autoclass

from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["debug"])

from kivy.base import ExceptionHandler, ExceptionManager

from typing import Dict

from kivy.logger import Logger
# from android.broadcast import BroadcastReceiver

from ble.android.blescanner import BLEScanTool
from ble.android.gattclient import GATTClient
from ble.bleops import QOpExecutorFactory, QOp, ContextConverter, QOpExecutor
from ble.bleinterface import BLEInterface
from ble.gattclientinterface import GATTClientInterface

# class E(ExceptionHandler):
#     def handle_exception(self, inst):
#         Logger.exception('Exception caught by ExceptionHandler')
#         MainApp.stop()
#         return ExceptionManager.PASS


# ExceptionManager.add_handler(E())

# Uncomment this to allow all non-Kivy loggers to output
# logging.Logger.manager.root = Logger  # type: ignore

# Logger.debug("SYS:" + os.path.dirname(kivy.__file__))

CLIENT = OSCClient('localhost', 3002)

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
AndroidString = autoclass('java.lang.String')
NotificationBuilder = autoclass('android.app.Notification$Builder')
Action = autoclass('android.app.Notification$Action')
PythonService = autoclass('org.kivy.android.PythonService')
# PythonService = autoclass('org.decentespresso.dedebug.StickyService')
# PythonService = autoclass('org.kivy.android.StickyService')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
String = autoclass('java.lang.String')
InvHandler = autoclass("org.jnius.NativeInvocationHandler")
PowerManager = autoclass('android.os.PowerManager')

def ping(*_):
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

def setup_service_notify(ptext, pmessage):
    service = PythonService.mService
    Logger.info("BLEService: " + service.getPackageName())
    Drawable = autoclass("{}.R$drawable".format(service.getPackageName()))

    # convert input text into a java string
    text = AndroidString(ptext.encode('utf-8'))
    message = AndroidString(pmessage.encode('utf-8'))

    intent = Intent(service, service.getClass())
    contentIntent = PendingIntent.getActivity(service, 0, intent, 0)
    notification_builder = NotificationBuilder(service)
    notification_builder.setContentTitle(text)
    notification_builder.setContentText(message)
    notification_builder.setSmallIcon(Drawable.presplash)
    notification_builder.setContentIntent(contentIntent)

    notification = notification_builder.getNotification()
    service.startForeground(1, notification)
    Logger.info("BLEService: Posted foreground notification")

if __name__ == '__main__':
    SERVER = OSCThreadServer()
    SERVER.listen('localhost', port=3000, default=True)
    SERVER.bind(b'/ping', ping)
    setup_service_notify(u"CafeHub is proxying BLE", "Started: " + asctime(localtime()))

    activity = PythonActivity.mActivity
    PythonService.mService.setAutoRestartService(True)
    Logger.debug("Bleservice: StartType = %s" % (PythonService.mService.startType(),))


    pm = PythonService.mService.getSystemService(Context.POWER_SERVICE)
    wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, 'TAG')

    wl.acquire()

    import wsserver.server
    server = wsserver.server.SyncWSServer(Logger, PythonService.mService)

    try:
        while True:
            sleep(1)
            send_date()
    finally:
        wl.release()