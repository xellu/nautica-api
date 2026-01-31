import json
import asyncio
import threading
import websockets

from ...api.ws import Reply, Error
from ..logger import LogManager
from ... import Core, instances

logger = LogManager("Services.RemoteAccess")

packet_handlers = {}

class RemoteAccessHandler:
    def __init__(self, ws, path, parent):
        self.ws = ws
        self.path = path
        self.parent = parent

        self.ip = ws.remote_address[0]
        self.port = ws.remote_address[1]
        
        self.running = False
        self.authed = False
        
        self.threads = []
        self.msg_buffer = []
        
    async def onConnect(self):
        self.running = True
        logger.ok(f"{self.ip}: CONN <- {self.path}")

        if self.path != "/nautica:remote":
            await self.drop()
            return        

        for log in instances.LogManInstances:
            log.callbacks.append(self.loggerCallback)

        read_task = asyncio.create_task(self.readLoop())
        send_task = asyncio.create_task(self.sendLoop())

        # wait until one of them finishes
        done, pending = await asyncio.wait(
            [read_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # stop the other loop
        self.running = False
        for task in pending:
            task.cancel()

        
    async def readLoop(self):        
        while True:
            if not self.running: break
            
            #get data
            try:
                data = await self.ws.recv()
            except websockets.ConnectionClosed:
                await self.drop("Connection closed")
                break
            except Exception as e:
                await self.drop(f"Crashed ({e})")
                break

            if not data:
                await self.drop("No data received")
                break
            
            #parse payload
            try:
                payload = json.loads(data)
                if not payload.get('id'):
                    await self.drop("No packet ID")
                    break
            except:
                await self.drop("Corrupted data")
                break
            
            # logger.debug(f"{self.ip}: PIN <- {self.path} ({payload})")
            
            handler = packet_handlers.get(payload["id"])
            if not handler:
                await self.send(Error("No handler found for '{payload['id']}'"))

            res = await handler(self, payload)
            if res:
                await self.send(res)
        
    async def sendLoop(self):
        while True:
            if not self.running: break
            
            if self.msg_buffer:
                await self.send(Reply(
                    id = "log",
                    buffer = self.msg_buffer
                ))
                self.msg_buffer = []
                
            await asyncio.sleep(1/4)
        
    def loggerCallback(self, text, json):
        if not self.authed: return
        self.msg_buffer.append(json)
        
    async def send(self, kwargs):
        # logger.debug(f"{self.ip}: POUT -> {self.path} ({kwargs})")
        await self.ws.send(json.dumps(kwargs))
        
    async def drop(self, reason: str = "dropped"):
        self.running = False
        logger.info(f"{self.ip}: DROP -> {self.path} ({reason=})")

        for log in instances.LogManInstances:
            if self.loggerCallback in log.callbacks:
                log.callbacks.remove(self.loggerCallback)

        try:
            await self.ws.close()
        except:
            pass

        self.kill()
        
    def kill(self):
        self.running = False
        self.parent.handlers.remove(self)

class RemoteAccessServer:
    def __init__(self):
        self.active = False
        self.handlers = []
        
    def start(self):
        if not Core.Config.getMaster("services.remoteAccess.enabled"):
            logger.warn("Remote Access service is disabled")
            return
        
        self.active = True
        
        threading.Thread(target=self._start).start()
        
    def _start(self):
        asyncio.run(self.__start())
        
    async def __start(self):
        from . import handlers

        async with websockets.serve(self.handler, Core.Config.getMaster("services.remoteAccess.host"), Core.Config.getMaster("services.remoteAccess.port")):
            await asyncio.Future()
            
    async def handler(self, ws, path):
        h = RemoteAccessHandler(ws, path, self)
        self.handlers.append(h)
        
        await h.onConnect()
        
    def stop(self):
        logger.info("Server is stopping...")
        
        self.active = False
        
        for h in self.handlers.copy():
            h.kill()
            
            
RemoteAccess = RemoteAccessServer()