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


class WSCBConverter(ContextConverter):
    """
    Converts a callback function to run in WSServer execution loop
    """

    def convert(self, fn):
        def wrapper(result):
            print("Wrapped")
            sys.exit(1)
            #  wsserver.threadtools.run_coroutine_threadsafe(functools.partial(fn, result))

        return wrapper


"""
Implementation of a WebSocket JSON BLE API.

See jsondesc.py to see a description of the websocket JSON API and message types.
"""


class AsyncWSServer:
    def __init__(self, logger):
        self.Logger = logger
        self.Loop = wsserver.threadtools.get_WSAsyncLoop()
        self.StopFuture = asyncio.Future(loop=self.Loop)
        self.SendQ = asyncio.Queue(loop=self.Loop)
        self.SeenDevices = set()
        self.BLE = BLE(QOpExecutorFactory(), WSCBConverter())
        self.BLE.requestBLEEnableIfRequired()
        wsserver.threadtools.run_coroutine_threadsafe(self.ServerCoro())
        self.Parser = wsserver.jsondesc.WSBLEParser()
        self.Done = threading.Event()
        self.Stop = False

    def shutdown(self):
        # Close the WebSockets server nicely
        self.Logger.debug("WSServer: shutdown() current thread: %s" % (threading.current_thread().name,))
        self.BLE.on_stop()
        wsserver.threadtools.run_coroutine_threadsafe(self._shutdown())
        self.Done.wait(timeout=100)

    async def _shutdown(self):
        self.Logger.debug("WSServer: _shutdown() current thread: %s" % (threading.current_thread().name,))
        self.Logger.debug("WSServer: Shutting down nicely")
        self.StopFuture.set_result(1)
        self.Stop = True

    async def ServerCoro(self):
        self.Logger.debug("WSServer: Server coroutine is running in thread %s" % (threading.current_thread().name,))

        async with websockets.serve(self.handler, "localhost", 8765, close_timeout=0.5):
            self.Logger.debug("WSServer: Starting main server loop")
            await self.StopFuture

        self.Logger.debug("WSServer: Exiting main loop")
        self.Done.set()

    async def _wait_closed(self):
        self.Logger.debug("WSServer Waiting for connections to close")
        # await self.Server.wait_closed()

    async def do_scan(self, uid, timeout):
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
                            await self.sendJSON(update)

                    await asyncio.sleep(0.25)

            stopresult = BLEScanResult("", "", [], None, None)
            update = make_update_from_blescanresult(uid, stopresult)
            await self.sendJSON(update)

        except BLEException as pe:
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
            await self.sendJSON(result)
        except:
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))
            await self.sendJSON(result)

    async def do_connect(self, uid, mac):
        """
        Start a GATT Client to talk to MAC.
        """
        try:
            gc = self.BLE.getGATTClient(mac)
            result = await gc.async_connect()
            print("Got result", result)
            result = result.getResult()
            update = make_ConnectionState(uid, mac, result)
            await self.sendJSON(update)
        except BLEException as pe:
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
            await self.sendJSON(result)
        except:
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))
            await self.sendJSON(result)

    async def do_disconnect(self, uid, mac):
        """
        Disconnect GATT Client
        """
        try:
            gc = self.BLE.getGATTClient(mac)
            result = await gc.async_disconnect()
            result = result.getResult()
            update = make_ConnectionState(uid, mac, result)
            await self.sendJSON(update)
        except BLEException as pe:
            result = make_execution_error(uid, getattr(pe, 'message', repr(pe)))
            await self.sendJSON(result)
        except:
            tb = traceback.format_exc()
            result = make_execution_error(uid, repr(tb))
            await self.sendJSON(result)

    async def do_read(self, uid, mac, char, rlen):
        """
        Read 'rlen' bytes from 'mac' characteristic 'char'.
        """
        gc = self.BLE.getGATTClient(mac)
        res = await gc.async_char_read(char)
        res = bytes(res.getResult())
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, {base64.standard_b64encode(res).decode('ascii')})
        print(resp)
        await self.sendJSON(resp)

    async def do_write(self, uid : int, mac : str, char : str, wdata : bytes):
        """
        Write 'wdata' to 'mac' characteristic 'char'.
        """
        gc = gc = self.BLE.getGATTClient(mac)
        res = await gc.async_char_write(char, wdata)
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, '')
        print(resp)
        await self.sendJSON(resp)

    async def rx_handler(self, websocket, path):
        # Collects data from the websocket
        self.Logger.debug("WSServer: rx_handler main loop: %s connected. Path %s" % (websocket.remote_address, path))
        while True:
            async for message in websocket:
                await self.rx(message, websocket)

    async def tx_handler(self, websocket, path):
        """
        Writes data to websocket
        """
        try:
            while True:
                if websocket.open:
                    message = await self.SendQ.get()
                    await websocket.send(message)
                else:
                    await websocket.send("")  # Have to try to send before we get an exception

        except websockets.ConnectionClosed as cce:
            print(repr(cce))
            self.Logger.debug("WSSerrver: Connection (%s) closed" % (websocket.remote_address,))

    async def sleeper(self):
        while not self.Stop:
            await asyncio.sleep(0.1)

    async def handler(self, websocket, path):
        """
        Main websocket handler that sets up tasks for RX and TX
        """
        rx_task = asyncio.ensure_future(self.rx_handler(websocket, path), loop=self.Loop)
        tx_task = asyncio.ensure_future(self.tx_handler(websocket, path), loop=self.Loop)
        sleeper_task = asyncio.ensure_future(self.sleeper(), loop=self.Loop)

        done, pending = await asyncio.wait(
            [rx_task, tx_task, sleeper_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        self.Logger.debug("WSServer: Exiting wait")

        for task in pending:
            task.cancel()

        self.Logger.debug("WSServer: Pending tasks cancelled")
        self.Done.set()

    async def rx(self, ctext, websocket):
        """
        Validate and process a message from the websocket
        try to generate a useful error message to send back if something goes wrong.
        """
        print(f"<<< {ctext}")

        result = None
        # noinspection PyBroadException
        try:
            cmd = {}
            cmd = json.loads(ctext)
            await self.parseCommand(cmd)
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
            await self.sendJSON(result)

    async def sendJSON(self, ob):
        """
        Internal. Call this to schedule an obj to be sent back to the client
        """
        print("sendJSON %s" % (ob,))
        result = json.dumps(ob, indent=2)
        await self.SendQ.put(result)
        print(">>> %s" % (result,))
        if (ob['type'] == "UPDATE") and (ob['update'] == "ExecutionError"):
            err = ob['results']['Error']
            print(err.encode('latin-1', 'backslashreplace').decode('unicode-escape'))

    async def parseCommand(self, cmd):
        params = cmd['params']
        uid = cmd['id']
        self.Parser.parse_obj(cmd)
        if cmd['type'] == 'REQ':
            if cmd['command'] == 'GATTWrite':
                await self.do_write(uid, params['MAC'], params['Char'], params['Data'])

            if cmd['command'] == 'GATTRead':
                await self.do_read(uid, params['MAC'], params['Char'], params['Len'])

            if cmd['command'] == 'Scan':
                await self.do_scan(uid, params['Timeout'])

            if cmd['command'] == 'GATTConnect':
                await self.do_connect(uid, params['MAC'])

            if cmd['command'] == 'GATTDisconnect':
                await self.do_disconnect(uid, params['MAC'])

        return None


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

