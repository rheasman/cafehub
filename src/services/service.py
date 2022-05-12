'p4a example service using oscpy to communicate with main application.'
from random import sample, randint
from string import ascii_letters
from time import localtime, asctime, sleep
import typing

from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

from jnius import autoclass # type: ignore

from kivy.logger import Logger, LOG_LEVELS
from MsgHandler import MsgHandler

from ble.android.androidtypes import T_BLEService, T_BluetoothDevice, T_BuildVersion, T_Context, T_Drawable, T_Intent, T_Java_String, T_Native_Invocation_Handler, T_NotificationAction, T_NotificationBuilder, T_NotificationChannel, T_NotificationManager, T_PendingIntent, T_PowerManager, T_PythonActivity, T_PythonService
from httpserver.httpserver import BackgroundThreadedHTTPServer
Logger.setLevel(LOG_LEVELS["debug"])

# from kivy.base import ExceptionHandler, ExceptionManager

from typing import Any

from kivy.logger import Logger

# class E(ExceptionHandler):
#     def handle_exception(self, inst):
#         Logger.exception('Exception caught by ExceptionHandler')
#         MainApp.stop()
#         return ExceptionManager.PASS


# ExceptionManager.add_handler(E())

# Uncomment this to allow all non-Kivy loggers to output
import logging
logging.Logger.manager.root = Logger  # type: ignore

# Logger.debug("SYS:" + os.path.dirname(kivy.__file__))

CLIENT = OSCClient('localhost', 4002, encoding="UTF-8")

Context : T_Context = autoclass('android.content.Context')
Intent : T_Intent = autoclass('android.content.Intent')
PendingIntent : T_PendingIntent = autoclass('android.app.PendingIntent')
AndroidString : T_Java_String = autoclass('java.lang.String')
NotificationBuilder : T_NotificationBuilder = autoclass('android.app.Notification$Builder')
Action : T_NotificationAction = autoclass('android.app.Notification$Action')
PythonService : T_PythonService = autoclass('org.kivy.android.PythonService')
# PythonService = autoclass('org.decentespresso.cafehub.StickyService')
# PythonService = autoclass('org.kivy.android.StickyService')
PythonActivity : T_PythonActivity = autoclass('org.kivy.android.PythonActivity')
BluetoothDevice : T_BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
String : T_Java_String = autoclass('java.lang.String')
InvHandler : T_Native_Invocation_Handler = autoclass("org.jnius.NativeInvocationHandler")
PowerManager : T_PowerManager = autoclass('android.os.PowerManager')
BuildVersion : T_BuildVersion = autoclass("android.os.Build$VERSION")

if BuildVersion.SDK_INT >= 26:
    NotificationChannel : T_NotificationChannel = autoclass("android.app.NotificationChannel")

def ping(*_ : Any):
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

"""
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    CharSequence name = getString(R.string.channel_name);
    String description = getString(R.string.channel_description);
    int importance = NotificationManager.IMPORTANCE_DEFAULT;
    NotificationChannel channel = new NotificationChannel(CHANNEL_ID, name, importance);
    channel.setDescription(description);

    // Don't see these lines in your code...
    NotificationManager notificationManager = getSystemService(NotificationManager.class);
    notificationManager.createNotificationChannel(channel);
}

"""
def setup_service_notify(ptext : str, pmessage : str):
    service : T_BLEService = typing.cast(T_BLEService, PythonService.mService)
    Logger.info("BLEService: " + service.getPackageName())
    Drawable : T_Drawable = autoclass("{}.R$drawable".format(service.getPackageName()))

    chan_id = AndroidString('misc'.encode('utf-8'))

    if BuildVersion.SDK_INT >= 26: # Build.VERSION_CODES.O) {
        Logger.info("Creating notification channel 'misc'")
        chan_name = AndroidString('CafeHub Notification Channel'.encode('utf-8'))
        desc = AndroidString('CafeHUb Notifications'.encode('utf-8'))
        importance : int = 3 # NotificationManager.IMPORTANCE_DEFAULT is value 3
        chan : T_NotificationChannel = NotificationChannel(chan_id, chan_name, importance)
        chan.setDescription(desc)

        nm : T_NotificationManager = PythonService.mService.getSystemService(Context.NOTIFICATION_SERVICE)
        nm.createNotificationChannel(chan)

    # convert input text into a java string
    text = AndroidString(ptext.encode('utf-8'))
    message = AndroidString(pmessage.encode('utf-8'))

    intent = Intent(service, service.getClass())
    contentIntent = PendingIntent.getActivity(service, 0, intent, 0)

    if BuildVersion.SDK_INT >= 26: # Build.VERSION_CODES.O) {
        notification_builder = NotificationBuilder(service, chan_id)
    else:
        notification_builder = NotificationBuilder(service)

    notification_builder.setContentTitle(text)
    notification_builder.setContentText(message)
    notification_builder.setSmallIcon(Drawable.presplash)
    notification_builder.setContentIntent(contentIntent)

    notification = notification_builder.getNotification()
    service.startForeground(1, notification)
    Logger.info("BLEService: Posted foreground notification")

KeepRunning = True

def shutdown(*args : Any):
    PythonService.mService.setAutoRestartService(False)
    global KeepRunning
    KeepRunning = False
    PythonService.mService.stopSelf()
    
if __name__ == '__main__':
    SERVER = OSCThreadServer()
    SERVER.listen('localhost', port=4000, default=True)
    SERVER.bind(b'/ping', ping)
    SERVER.bind(b'/shutdown', shutdown)

    setup_service_notify(u"CafeHub is proxying BLE", "Started: " + asctime(localtime()))

    activity = PythonActivity.mActivity
    PythonService.mService.setAutoRestartService(True)
    Logger.debug("Bleservice: StartType = %s" % (PythonService.mService.startType(),))


    pm : T_PowerManager = PythonService.mService.getSystemService(Context.POWER_SERVICE)
    wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, 'TAG')

    wl.acquire()

    Logger.addHandler(MsgHandler(oscclient=CLIENT))

    import wsserver.server
    server = wsserver.server.SyncWSServer(Logger, PythonService.mService)

    httpserver = BackgroundThreadedHTTPServer(5000, 3, "./webserverdata/test_app")
    httpserver.start()
    try:
        while KeepRunning:
            sleep(1)
            send_date()
    finally:
        wl.release()
        httpserver.shutdown()