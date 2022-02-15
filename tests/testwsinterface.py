import asyncio
import base64
import os
import sys
import time
import websockets

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../..')))

from  wsserver.jsondesc import *


class IDManager:
    def __init__(self):
        self.ID = 0

    def getId(self):
        self.ID = (self.ID + 1) % (1 << 32)
        if self.ID == 0:
            self.ID += 1

        return self.ID


IDM = IDManager()


async def test_disconnect(webs, target):
    disconn = make_GATTDisconnect(IDM.getId(), target)
    await webs.send(json.dumps(disconn))

    resp = await asyncio.wait_for(webs.recv(), timeout=6)
    print(resp)


async def test_read(webs, target):
    read = make_GATTRead_as_JSON(IDM.getId(), target, '0000a001-0000-1000-8000-00805f9b34fb', 0)
    await webs.send(read)
    resp = await asyncio.wait_for(webs.recv(), timeout=6)
    print(resp)
    resp = json.loads(resp)
    print(resp)
    if resp['type'] == 'RESP':
        resp['results'] = base64.b64decode(resp['results'])
        print(resp)


async def test_write(webs, target):
    char = '0000a002-0000-1000-8000-00805f9b34fb'
    wdata = b'\x02'
    write = make_GATTWrite_as_JSON(IDM.getId(), target, char, wdata)
    resp = await webs.send(write)
    print(resp)


async def test_connect(webs):
    scan = make_Scan(5, IDM.getId())
    now = time.time()
    await webs.send(json.dumps(scan))
    target = None

    while time.time() < (now+6):
        try:
            resp = await asyncio.wait_for(webs.recv(), timeout=0.25)
        except asyncio.TimeoutError:
            pass
        else:
            print(resp)
            foo = json.loads(resp)
            print("Result is: ", repr(foo))
            if foo['type'] == "UPDATE":
                info = foo['results']
                if info['Name'] == "DE1":
                    target = info['MAC']

    print("Test Scan done")

    # target = "E5:DC:80:27:DF:7C"

    if target:
        conn = make_GATTConnect(IDM.getId(), target)
        print(conn)
        await webs.send(json.dumps(conn))
        now = time.time()
        while time.time() < (now+10):
            try:
                result = await asyncio.wait_for(webs.recv(), timeout=0.25)
            except asyncio.TimeoutError:
                pass
            else:
                print(result)

    if target:
        await test_read(webs, target)
        await test_write(webs, target)
        await test_disconnect(webs, target)


async def test():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as webs:
        try:
            await test_connect(webs)
        except websockets.exceptions.ConnectionClosedOK:
            pass

if __name__ == '__main__':
    asyncio.run(test())
