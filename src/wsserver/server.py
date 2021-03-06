import functools
import threading
import traceback
import logging
from time import sleep
from typing import Callable, Optional, Set, Tuple, TypeVar, TypedDict

from ble.ble import BLE
from ble.bleexceptions import BLEException, UnknownException
from ble.bleops import ContextConverter, QOpExecutorFactory, synchronized_with_lock
from ble.uuidtype import CHAR_UUID
from websocket_server.websocket_server import WebSocketHandler
from wsserver.jsondesc import *

class T_WebsocketClient(TypedDict):
    id : int
    handler : WebSocketHandler
    address : Tuple[str, int]

"""
Implementation of a WebSocket JSON BLE API.

See jsondesc.py to see a description of the websocket JSON API and message types.
"""

from websocket_server import WebsocketServer

T = TypeVar('T')
class NoOpConverter(ContextConverter):
    """
    This converter doesn't need to do anything
    """

    def convert(self, callback : Optional[Callable[..., None]]) -> Callable[..., None]:
        def wrapper(*args : Any, **kwargs : Any):
            print("Wrapped")
            if callback is not None:
                callback(*args, **kwargs)

        return wrapper

def catch_exceptions_and_send_as_JSON(oldmethod : Callable[..., T]) -> Callable[..., Optional[T]]:
    
    """
    Wraps an existing method so that if an exception occurs, the results
    is sent as a JSON error update. This removes a lot of boilerplate in the
    websocket server. Crashes will send a message to the websocket client
    with full details of the crash.

    Basically wraps the entire decorated method in a try-except that bundles
    up any error traceback and sends it.

    I find the documentation on decorators horribly opaque, so here is what I
    have discovered:

    oldmethod is a pointer to the (to-be-decorated aka TBD) method in the class.
    wrapper() in the decorator is handed all the parameters to the TBD method, including self
    """

    # functools.wraps() just copies the name etc. of the wrapped function over the wrapper name.
    # It's cosmetic and only helps when inspecting method names, using help() or dir(), etc.
    @functools.wraps(oldmethod)  # oldmethod is the decorated method
    def wrapper(self : 'SyncWSServer', client: T_WebsocketClient, uid : int, *args : Any, **kwargs : Any):
        try:
            return oldmethod(self, client , uid, *args, **kwargs)
        except BLEException as pe:
            result = make_execution_error(uid, pe.EID, getattr(pe, 'message', repr(pe)))
            self.sendJSON(client, result)
        except:
            tb = traceback.format_exc()
            print(tb)
            result = make_execution_error(uid, UnknownException.EID, repr(tb))
            self.sendJSON(client, result)

    return wrapper  # Wrapper replaces oldmethod


class SyncWSServer:
    """
    Threaded WebSocket server.

    Async server was not playing well with Kivy. There are timeouts and things I
    can't interrupt.
    """
    def __init__(self, logger : logging.Logger, androidcontext : Any = None):
        self.Logger = logger
        self.SeenDevices : set[str] = set()
        self.BLE = BLE(QOpExecutorFactory(), NoOpConverter(), androidcontext = androidcontext)

        # Can't call this from a service. :-/
        #   self.BLE.requestBLEEnableIfRequired()
        # Copied the important bits into main.py instead()
        
        self.Parser = WSBLEParser()
        self.run()
        self.Stop = False
        self.ConnLock = threading.RLock()
        self.ConnSet : set[int] = set()

    @synchronized_with_lock("ConnLock")
    def addConn(self, clientid : int) -> None:
        self.ConnSet.add(clientid)

    @synchronized_with_lock("ConnLock")
    def remConn(self, clientid : int) -> None:
        self.ConnSet.discard(clientid)

    @synchronized_with_lock("ConnLock")
    def getConnSet(self) -> Set[int]:
        return self.ConnSet

    def shutdown(self) -> None:
        self.Stop = True
        self.BLE.on_stop()
        if self.Server:
            self.Server.shutdown_gracefully()

    @catch_exceptions_and_send_as_JSON
    def do_scan(self, client: T_WebsocketClient, uid : int, timeout : float):
        """
        Scan for timeout seconds. Check for results 4 times per second and pass them on.
        """
        self.SeenDevices : set[str] = set()
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

    @catch_exceptions_and_send_as_JSON
    def do_connect(self, client: T_WebsocketClient, uid : int, mac : str):
        """
        Connect to GATT Client
        """
        gc = self.BLE.getGATTClient(mac)

        def disc_callback(cstate : GATTCState):
            upd = make_ConnectionState(uid, mac, cstate, []) 
            self.sendJSON(client, upd)

        gc.set_disc_callback(disc_callback)

        # This call blocks, but we're running in our own thread anyway
        result = gc.connect()
        print("do_connect: got result", result)
        update = make_ConnectionState(uid, mac, result, gc.getCharacteristicsUUIDs())
        self.sendJSON(client, update)

    @catch_exceptions_and_send_as_JSON
    def do_set_notify(self, client: T_WebsocketClient, uid : int, mac : str, uuid : CHAR_UUID, enable : bool) -> None:
        def sendcallback(characteristic : CHAR_UUID, data : bytes):
            results = {
                "MAC"  : mac,
                "Char" : characteristic.AsString,
                "Data" : str(base64.b64encode(data), "utf-8")
            }
            upd = make_update(0, "GATTNotify", results)
            self.sendJSON(client, upd)

        gc = self.BLE.getGATTClient(mac)
        gc.set_notify(uuid, enable, sendcallback)
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, {})
        self.sendJSON(client, resp)

    @catch_exceptions_and_send_as_JSON
    def do_disconnect(self, client: T_WebsocketClient, uid : int, mac : str) -> None:
        """
        Disconnect GATT Client
        """
        gc = self.BLE.getGATTClient(mac)
        result = gc.disconnect()
        update = make_ConnectionState(uid, mac, result, [])
        self.sendJSON(client, update)

    @catch_exceptions_and_send_as_JSON
    def do_read(self, client: T_WebsocketClient, uid : int, mac : str, char : CHAR_UUID, rlen : int) -> None:
        """
        Read 'rlen' bytes from 'mac' characteristic 'char'.
        """
        gc = self.BLE.getGATTClient(mac)
        res = gc.char_read(char)
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, {"Data:" : base64.standard_b64encode(res).decode('ascii')})
        print(resp)
        self.sendJSON(client, resp)

    @catch_exceptions_and_send_as_JSON
    def do_write(self, client: T_WebsocketClient, uid : int, mac : str, char : CHAR_UUID, wdata : bytes, requireresponse : bool):
        """
        Write 'wdata' to 'mac' characteristic 'char'.
        """
        gc = self.BLE.getGATTClient(mac)
        decodedata = base64.b64decode(wdata)
        gc.char_write(char, decodedata, requireresponse)
        resp = make_resp(uid, {'eid' : 0, 'errmsg' : ''}, {})
        self.sendJSON(client, resp)

    def _cb_NewClient(self, client: T_WebsocketClient, server : WebsocketServer):
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

    def _cb_ClientLeft(self, client: T_WebsocketClient, server : WebsocketServer):
        """
        Called when a client leaves.

        Seems to be called more than once sometimes, hence the use of sets instead
        of a counter. Can also be called with None? No idea why.
        """
        if client is None:
            return

        self.Server.deny_new_connections()
        self.remConn(client['id'])

        connset = self.getConnSet()
        if len(connset) == 0:
            # We only allow 1 connection at a time.
            # Disconnect any BLE devices
            try:
                self.BLE.disconnectAllClients()
            except:
                # We really can't do anything if a disconnect fails
                pass

            # If we have zero clients, allow connections again.
            self.Server.allow_new_connections()

        self.Logger.debug("SyncWS: client left: %s" % client)

    def _cb_MessageReceived(self, client: T_WebsocketClient, server : WebsocketServer, message : str):
        """
        Called when a client sends information

        Each call is in a new thread, so blocking operations in a thread are fine
        """
        self.Logger.debug("SyncWS: new message: %s" % message)

        cmd = {}

        result = None
        # noinspection PyBroadException
        try:
            cmd = json.loads(message)
            cmd = self.parseCommand(client, cmd)
        except json.decoder.JSONDecodeError as de:
            result = make_execution_error(0, UnknownException.EID, repr(de))
        except ParseException as pe:
            uid = cmd.get('uid', 0) # type: ignore
            result = make_execution_error(uid, UnknownException.EID, getattr(pe, 'message', repr(pe))) # type: ignore
        except:
            uid = cmd.get('uid', 0) # type: ignore
            tb = traceback.format_exc()
            result = make_execution_error(uid, UnknownException.EID, repr(tb)) # type: ignore

        if result is not None:
            self.sendJSON(client, result)

    def parseCommand(self, client: T_WebsocketClient, cmd : Dict[str, Any]) -> Dict[str, Any]:
        cmd = self.Parser.parse_obj(cmd)
        params = cmd['params']
        uid = cmd['id']
        if cmd['type'] == 'REQ':
            if cmd['command'] == 'GATTWrite':
                self.do_write(client, uid, params['MAC'], CHAR_UUID(params['Char']), params['Data'], params['RR'])

            if cmd['command'] == 'GATTRead':
                self.do_read(client, uid, params['MAC'], CHAR_UUID(params['Char']), params['Len'])

            if cmd['command'] == 'Scan':
                self.do_scan(client, uid, params['Timeout'])

            if cmd['command'] == 'GATTConnect':
                self.do_connect(client, uid, params['MAC'])

            if cmd['command'] == 'GATTDisconnect':
                self.do_disconnect(client, uid, params['MAC'])

            if cmd['command'] == 'GATTSetNotify':
                self.do_set_notify(client, uid, params['MAC'], CHAR_UUID(params['Char']), params['Enable'])

        return cmd

    # Do I need a lock here? It would make sense that Server.send_message is multithreaded, as
    # server is multithreaded.
    # Okay, checking the source for send_message, it runs with a lock, so we're good.
    def sendJSON(self, client: T_WebsocketClient, ob : Dict[str, Any]):
        """
        Internal. Send message to the client
        """
        self.Logger.debug("WSServer: sendJSON %s" % (ob,))
        result = json.dumps(ob, indent=2)
        try:
            self.Server.send_message(client, result)
        except BrokenPipeError:
            self.Logger.debug("WSServer: sendJSON: Broken Pipe")
            
        self.Logger.debug("WSServer: >>> %s" % (result,))
        if (ob['type'] == "UPDATE") and (ob['update'] == "ExecutionError"):
            self.Logger.debug("WSServer: Error: %s" % (ob,))
            err = ob['results']['errmsg']
            self.Logger.debug("WSServer: sendJSON: %s" % (err.encode('latin-1', 'backslashreplace').decode('unicode-escape'),))

    def run(self):
        """
        Run the server in its own thread
        """
        self.Server = WebsocketServer(host='0.0.0.0', port=8765, loglevel=logging.INFO)

        # Set up callbacks
        # Every message callback is called in a newly created thread.
        self.Server.set_fn_new_client(self._cb_NewClient)
        self.Server.set_fn_client_left(self._cb_ClientLeft)
        self.Server.set_fn_message_received(self._cb_MessageReceived)
        self.Server.run_forever(threaded=True)
