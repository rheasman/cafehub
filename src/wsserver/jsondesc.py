import base64
import json
import os
import sys

from ble.gattclientinterface import GATTCState

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../..')))
from ble.blescanresult import BLEScanResult
from typing import Dict, List, Literal, Any

from pydantic import BaseModel

T_MsgType_REQ = Literal["REQ"]
T_MsgType_RESP = Literal["RESP"]
T_MsgType_UPDATE = Literal["UPDATE"]
T_MsgType = Literal[T_MsgType_REQ, T_MsgType_RESP, T_MsgType_UPDATE]
T_ConnectionState = Literal["INIT", "DISCONNECTED", "CONNECTED", "CANCELLED"]
T_ReqCommand = Literal["Scan", "GATTConnect", "GATTDisconnect", "GATTRead", "GATTSetNotify", "GATTWrite"];

class T_Request(BaseModel):
    type : T_MsgType_REQ = "REQ"
    command: T_ReqCommand
    params: Any
    id: int

    class Config:
        allow_mutation = False



"""
Requests follow the following general format:
    {
        type    : "REQ",
        command : string,
        params  : { relevant params },
        id      : U32
    }

    Requests are always sent from the client to the server.
    Any responses to a request will be tagged with the given id.
    NB: Zero is a reserved id! It means "unknown id"
    NEVER USE 0 AS AN ID!

Responses:
    {
        type: "RESP", 
        id : U32,
        error : { eid: U32, errmsg : string }, 
        results : { results }
    }

If eid is != 0, then results will be empty.

Errors:
    0 - Okay
    1 - BLEOperationNotIssued(BLEOpException)
    2 - BLEOperationTimedOut(BLEOpException) 
    3 - BLEScanException(BLEException)
    4 - BLEAlreadyScanning(BLEScanException)
    5 - BLECouldntDiscoverServices(BLEException)

Request Commands:

    Scan(timeout : U32)

        Scan for up to 30 seconds.
        
    GATTConnect(MAC : string)
    
        Attempt to connect to MAC. Generates an update listing services once connected.

    GATTDisconnect(MAC : string)
    
        Attempt to disconnect MAC. Any outstanding operations will be cancelled.

    GATTRead(MAC : string, Char : string, Len : int)

        Response will come back later with the given id.

    GATTSetNotify(MAC : string, Char : string, Enable : bool)

        Will come back with error 0 (Okay) if it worked.

    GATTWrite(MAC : string, Char : string, Data : Base64Data)

Updates:

    {
        type    : "UPDATE",
        id      : U32,
        update  : string,
        results : { results }
    }

    Updates are sent by the server to inform the clients if something important changes. 
    Because they can be unsolicited, they do not always have an id. The type of update is in "update".

    ScanResult(MAC : string, Name : string, UUIDS : ArrayOfString)
    
        A result from an ongoing BLE scan
        
    GATTNotify(MAC : string, Char : string, Data : Base64Data)

        A notify that we subscribed to has delivered some data

    ConnectionState(id: int, MAC : string, state : str)

        Notification of a connection or disconnection. If id != 0, then this connection
        state is the direct result of a connect or disconnect request.
        
    ExecutionError(eid : number, errmsg : String)
    
        Used to report any runtime errors that occurred in the server
        
"""


class ParseException(Exception):
    pass


class WSBLEParser:
    def parse_obj(self, obj : Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses objects sent to the server by the client.
        """
        if len(obj) > 4:
            raise ParseException('Too many fields in input')
        self.check_exists(['type'], obj, "Could not find '%s' field")

        otype = obj['type']

        # child methods can assume type is valid
        if otype == "REQ":
            return self.parse_req(obj)
        elif otype == "RESP":
            return self.parse_resp(obj)
        else:
            raise ParseException('Unknown type: %s' % (otype,))

    def check_exists(self, keylist : List[str], obj : Dict[str, Any], err : str) -> None:
        for key in keylist:
            if key not in obj:
                raise ParseException(err % (key,))

    def parse_resp(self, resp : Dict[str, Any]) -> Dict[str, Any]:
        """
        {
            type   : "RESP",
            id     : U32,
            error  : {eid: U32, errmsg: string},
            results: {results}
        }
        """
        if len(resp) > 4:
            raise ParseException('Too many fields in response')

        self.check_exists(['id', 'error', 'results'], resp, "Could not find '%s' field")

        if resp['id'] == 0:
            raise ParseException('ID cannot be zero in a request. It means "Unknown ID".')

        error = resp['error']
        # res = resp['results']

        if len(error) > 2:
            raise ParseException('Too many fields in error')

        self.check_exists(['eid', 'errmsg'], error, "Could not find '%s' field in error")

        # TODO results
        return resp

    def parse_req(self, obj : Dict[str, Any]) -> Dict[str, Any]:
        """
        {
            type   : "REQ",
            command: string,
            params : { params },
            id     : U32
        }
        """
        if len(obj) > 4:
            raise ParseException('Too many fields in request')

        self.check_exists(['id', 'command', 'params'], obj, "Could not find '%s' field")
        if obj['command'] not in ('Scan', 'GATTRead', 'GATTSetNotify', 'GATTWrite', 'GATTConnect', 'GATTDisconnect'):
            raise ParseException('Unrecognized command: %s' % (obj['command'],))

        if obj['id'] == 0:
            raise ParseException('ID cannot be zero in a request. It means "Unknown ID".')

        params = obj['params']

        if obj['command'] == 'Scan':
            # Scan(Timeout : int)
            self.check_exists(['Timeout'], params, 'No %s in Scan request params')
            self.parse_Timeout(params['Timeout'], "Timeout is not an integer")
            return obj
        
        if obj['command'] == 'GATTRead':
            # GATTRead(MAC : string, Characteristic : string, Len : int)
            self.check_exists(['MAC', 'Char', 'Len'], params, 'No %s in GATTRead request params')

            self.parse_MAC(params['MAC'])
            self.parse_Char(params['Char'])
            self.parse_Len(params['Len'])
            return obj

        if obj['command'] == 'GATTSetNotify':
            # GATTSetNotify(MAC: string, Char: string, Enable: bool)
            self.check_exists(['MAC', 'Char', 'Enable'], params, 'No %s in GATTSetNotify request params')

            self.parse_MAC(params['MAC'])
            self.parse_Char(params['Char'])
            self.parse_Bool(params['Enable'])
            return obj

        if obj['command'] == 'GATTWrite':
            # GATTWrite(MAC: string: Char: string, Data: Base64Data)
            self.check_exists(['MAC', 'Char', 'Data', 'RR'], params, 'No %s in GATTWrite request params')

            self.parse_MAC(params['MAC'])
            self.parse_Char(params['Char'])
            self.parse_Data(params['Data'])
            return obj

        if obj['command'] == 'GATTConnect':
            # GATTConnect(MAC: string)
            self.check_exists(['MAC'], params, 'No %s in GATTConnect request params')

            self.parse_MAC(params['MAC'])
            return obj

        if obj['command'] == 'GATTDisconnect':
            # GATTDisconnect(MAC: string)
            self.check_exists(['MAC'], params, 'No %s in GATTConnect request params')

            self.parse_MAC(params['MAC'])
            return obj

        return obj

    def parse_int(self, num : Any, msg : str):
        if not isinstance(num, int):
            raise ParseException(msg)

    def parse_Timeout(self, num : Any, msg : str):
        self.parse_int(num, msg)
        if num > (1 << 32):
            raise ParseException("Timeout is too large")

    def parse_MAC(self, mac : Any):
        # TODO: Do a basic check of MAC. Nothing too slow or complex.
        pass

    def parse_Char(self, char: Any):
        # TODO: Do a basic check of Char UUID. Nothing too slow or complex.
        pass

    def parse_Bool(self, boolval: Any):
        # TODO: Do a basic check of boolval. Nothing too slow or complex.
        pass

    def parse_Data(self, data: Any):
        # TODO: Do a basic check of Data. Nothing too slow or complex.
        pass

    def parse_Len(self, rlen: Any):
        # TODO: Do a basic check of Length
        pass


def make_req(command : str, rid : int, params : Dict[str, Any]) -> Dict[str, Any]:
    return {
        'type'   : 'REQ',
        'command': command,
        'params' : params,
        'id'     : rid
    }


def make_error(eid : int, errmsg : str) -> Dict[str, Any]:
    return {
        'eid' : eid,
        'errmsg' : errmsg
    }


def make_resp(rid : int, error : Dict[str, Any], results : Dict[str, str]) -> Dict[str, Any]:
    return {
        'type'    : 'RESP',
        'id'      : rid,
        'error'   : error,
        'results' : results
    }


def make_update(uid : int, updatetype : str, results : Dict[str, Any]) -> Dict[str, Any]:
    return {
        'type'    : "UPDATE",
        'id'      : uid,
        'update'  : updatetype,
        'results' : results
    }


def make_Scan(timeout : int, rid : int):
    # Scan(timeout : U32)
    params = {
        'Timeout' : timeout
    }
    return make_req("Scan", rid, params)


def make_ConnectionState(uid : int, mac : str, state : GATTCState, uuids : List[str]) -> Dict[str, Any]:
    return make_update(uid, "ConnectionState", {
        "CState" : state.name,
        "MAC"    : mac,
        "UUIDs"  : uuids
    })


def make_GATTWrite(rid : int, mac : str, char : str, data : bytes, requireresponse : bool) -> Dict[str, Any]:
    params = {
        'MAC'  : mac,
        'Char' : char,
        'Data' : data,
        'RR'   : requireresponse
    }
    return make_req("GATTWrite", rid, params)


def make_GATTWrite_as_JSON(rid : int, mac : str, char : str, data : bytes, requireresponse : bool) -> str:
    params = {
        'MAC'  : mac,
        'Char' : char,
        'Data' : base64.standard_b64encode(data).decode('ascii'),
        'RR'   : requireresponse
    }
    return json.dumps(make_req("GATTWrite", rid, params))


def make_GATTRead(rid : int, mac : str, char : str, rlen : int):
    params = {
        'MAC'  : mac,
        'Char' : char,
        'Len'  : rlen
    }
    return make_req('GATTRead', rid, params)


def make_GATTRead_as_JSON(rid : int, mac : str, char : str, rlen : int):
    return json.dumps(make_GATTRead(rid, mac, char, rlen))


def make_GATTConnect(rid : int, mac : str) -> Dict[str, Any]:
    params = {
        'MAC' : mac,
    }
    return make_req('GATTConnect', rid, params)


def make_GATTDisconnect(rid : int, mac : str) -> Dict[str, Any]:
    params = {
        'MAC' : mac,
    }
    return make_req('GATTDisconnect', rid, params)


def make_update_from_blescanresult(uid : int, scanresult : BLEScanResult) -> Dict[str, Any]:
    # ScanResult(MAC : string, Name : string, UUIDS : List[str])
    results = {
        'MAC'   : scanresult.MAC,
        'Name'  : scanresult.name,
        'UUIDs' : scanresult.uuids
    }
    return make_update(uid, 'ScanResult', results)


def make_execution_error(uid : int, eid : int, error : str) -> Dict[str, Any]:
    # ExecutionError(Error)
    results = make_error(eid, error)
    return make_update(uid, 'ExecutionError', results)


TEST_MAC = "AA:11:22:33:44:55"
TEST_UUID = "0000a001-0000-1000-8000-00805f9b34fb"


def test_resp():
    pass


def test_req():
    pass
    # parser = WSBLEParser()

    # parser.parse_req(make_GATTRead(1, TEST_MAC, TEST_UUID, 10))
    # parser.parse_req(make_GATTWrite(1, TEST_MAC, TEST_UUID, 10))


def test_update():
    pass


def test():
    res = make_Scan(5, 1)
    print("Example Scan command:", json.dumps(res))
    print("Example GATTConnect command:", json.dumps(make_GATTConnect(1, TEST_MAC)))
    test_req()
    test_update()
    test_resp()


if __name__ == '__main__':
    test()
