import asyncio
import string
import threading
import traceback
from time import sleep

import websockets

import wsserver.threadtools
from ble.ble import BLE
from ble.bleexceptions import BLEException
from ble.bleops import ContextConverter, QOpExecutorFactory, synchronized_with_lock
from wsserver.jsondesc import *

"""
Implementation of a WebSocket JSON BLE API.

See jsondesc.py to see a description of the websocket JSON API and message types.
"""

import logging
from websocket_server import WebsocketServer


class NoOpConverter:
    """
    This converter doesn't need to do anything
    """

    def convert(self, fn):
        def wrapper(result):
            print("Wrapped")
            fn(result)

        return wrapper


class SyncWSServer:
    """
    Threaded WebSocket server.

    Async server was not playing well with Kivy. There are timeouts and things I
    can't interrupt.
    """
    def __init__(self, logger):
        self.Logger = logger
        self.SeenDevices = set()
        self.BLE = BLE(QOpExecutorFactory(), NoOpConverter())
        self.BLE.requestBLEEnableIfRequired()
        self.Parser = wsserver.jsondesc.WSBLEParser()
        self.run()
        self.Stop = False
        self.ConnLock = threading.RLock()
        self.ConnSet = set()

    @synchronized_with_lock("ConnLock")
    def addConn(self, clientid):
        self.ConnSet.add(clientid)

    @synchronized_with_lock("ConnLock")
    def remConn(self, clientid):
        self.ConnSet.discard(clientid)

    @synchronized_with_lock("ConnLock")
    def getConnSet(self):
        return self.ConnSet

    def shutdown(self):
        self.Stop = True
        self.BLE.on_stop()
        if self.Server:
            self.Server.shutdown_gracefully()

    def do_scan(self, client, uid, timeout):
        """
        Scan for timeout seconds. Check for results 4 times per second and pass them on.
        """
        try:
            self.SeenDevices = set()
            self.BLE.scanForDevices(timeout)
            st = self.BLE.getBLEScanTool()
            if st is not None:
                while st.isScanning():
                    if self.Stop:
                        self.Logger.debug("WSServer: Stop is set")
                        st.stopScanning()
                        return
                    entries = st.getSeenEntries()
                    for i in entries:
                        if i not in self.SeenDevices:
                            self.SeenDevices.add(i)
                            self.Logger.info(f"UI: ble_scan_check: {i} : {entries[i]}")
                            item = entries[i]
                            self.Logger.info("Seen: %s" % (item,))
                            update = make_update_from_blescanresult(uid, item)
                            self.sendJSON(client, update)

                    sleep(0.25)

            stopresult = BLEScanResult("", "", [], None, None)
            update = make_update_from_blescanresult(uid, stopresult)
            self.sendJSON(client, update)

        except BLEException as pe:
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
            self.sendJSON(client, result)
        except:
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))
            self.sendJSON(client, result)

    def do_connect(self, client, uid, mac):
        """
        Connect to GATT Client
        """
        try:
            gc = self.BLE.getGATTClient(mac)

            # This call blocks, but we're running in our own thread anyway
            result = gc.connect()
            print("do_connect: got result", result)
            update = make_ConnectionState(uid, mac, result, list(gc.Characteristics.keys()))
            self.sendJSON(client, update)
        except BLEException as pe:
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
            self.sendJSON(client, result)
        except:
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))
            self.sendJSON(client, result)

    def do_disconnect(self, client, uid, mac):
        """
        Disconnect GATT Client
        """
        try:
            gc = self.BLE.getGATTClient(mac)
            result = gc.disconnect()
            update = make_ConnectionState(uid, mac, result)
            self.sendJSON(client, update)
        except BLEException as pe:
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
            self.sendJSON(client, result)
        except:
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))
            self.sendJSON(client, result)

    def do_read(self, client, uid, mac, char, rlen):
        """
        Read 'rlen' bytes from 'mac' characteristic 'char'.
        """
        gc = self.BLE.getGATTClient(mac)
        res = gc.char_read(char)
        res = bytes(res.getResult())
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, base64.standard_b64encode(res).decode('ascii'))
        print(resp)
        self.sendJSON(client, resp)

    def do_write(self, client, uid : int, mac : str, char : str, wdata : bytes):
        """
        Write 'wdata' to 'mac' characteristic 'char'.
        """
        gc = self.BLE.getGATTClient(mac)
        res = gc.char_write(char, wdata)
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, '')
        print(resp)
        self.sendJSON(client, resp)

    def _cb_NewClient(self, client, server):
        """
        Called when a new client connects
        """
        # We only allow 1 connection at a time.
        # Disable any further connections
        if client is None:
            return

        self.Server.deny_new_connections()
        self.addConn(client['id'])
        self.Logger.debug("SyncWS: new client: %s" % client)

    def _cb_ClientLeft(self, client, server):
        """
        Called when a client leaves.

        Seems to be called more than once sometimes, hence the use of sets instead
        of a counter. Can also be called with None? No idea why.
        """
        if client is None:
            return

        self.remConn(client['id'])

        connset = self.getConnSet()
        if len(connset) == 0:
            # We only allow 1 connection at a time.
            # Disconnect any BLE devices
            self.BLE.shutDownAllClients()
            # If we have zero clients, allow connections again.
            self.Server.allow_new_connections()

        self.Logger.debug("SyncWS: client left: %s" % client)

    def _cb_MessageReceived(self, client, server, message : string):
        """
        Called when a client sends information

        Each call is in a new thread, so blocking operations in a thread are fine
        """
        self.Logger.debug("SyncWS: new message: %s" % message)

        result = None
        # noinspection PyBroadException
        try:
            cmd = {}
            cmd = json.loads(message)
            self.parseCommand(client, cmd)
        except json.decoder.JSONDecodeError as de:
            result = make_execution_error(0, repr(de))
        except ParseException as pe:
            uid = cmd.get('uid', 0)
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
        except:
            uid = cmd.get('uid', 0)
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))

        if result is not None:
            self.sendJSON(client, result)

    def parseCommand(self, client, cmd):
        params = cmd['params']
        uid = cmd['id']
        self.Parser.parse_obj(cmd)
        if cmd['type'] == 'REQ':
            if cmd['command'] == 'GATTWrite':
                self.do_write(client, uid, params['MAC'], params['Char'], params['Data'])

            if cmd['command'] == 'GATTRead':
                self.do_read(client, uid, params['MAC'], params['Char'], params['Len'])

            if cmd['command'] == 'Scan':
                self.do_scan(client, uid, params['Timeout'])

            if cmd['command'] == 'GATTConnect':
                self.do_connect(client, uid, params['MAC'])

            if cmd['command'] == 'GATTDisconnect':
                self.do_disconnect(client, uid, params['MAC'])

            if cmd['command'] == 'GATTSetNotify':
                self.do_set_notify(client, uid, params['MAC'], params['UUID'], params['Enable'])

        return None

    def sendJSON(self, client, ob):
        """
        Internal. Send message to the client
        """
        print("sendJSON %s" % (ob,))
        result = json.dumps(ob, indent=2)
        self.Server.send_message(client, result)
        print(">>> %s" % (result,))
        if (ob['type'] == "UPDATE") and (ob['update'] == "ExecutionError"):
            err = ob['results']['Error']
            print(err.encode('latin-1', 'backslashreplace').decode('unicode-escape'))

    def run(self):
        """
        Run the server in its own thread
        """
        self.Server = WebsocketServer(host='127.0.0.1', port=8765, loglevel=logging.INFO)

        # Set up callbacks
        # Every message callback is called in a newly created thread.
        self.Server.set_fn_new_client(self._cb_NewClient)
        self.Server.set_fn_client_left(self._cb_ClientLeft)
        self.Server.set_fn_message_received(self._cb_MessageReceived)
        self.Server.run_forever(threaded=True)

