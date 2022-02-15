import sys, os
from kivy.logger import Logger

if os.environ.get("P4A_BOOTSTRAP") is not None:
    # We are on android
    Logger.info("BLE: Using Android BLE stack")
    from ble.android.ble import BLE
    from ble.android.gattclient import GATTClient
else:
    # Not Android
    if sys.platform == 'linux':
        # Linux
        Logger.info("BLE: Using Linux Bleak BLE stack")
        from ble.bleak.ble import BLE
