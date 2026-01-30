import asyncio
import json
import time
import threading
import websockets

from ...services.logger import LogManager
from ...ext import utils
from ... import Core

from ...api.ws.router import RouteRegistry
from ...api.ws import Error

logger = LogManager("Servers.WebSocket")

class WebSocketHandler:
    def __init__(self, ws, path, parent):
        self.ws = ws
        self.path = path
        self.parent = parent

        self.ip = ws.remote_address[0]
        self.port = ws.remote_address[1]
        
        self.running = False
        
        self.threads = []
        
    async def onConnect(self):
        self.running = True
        logger.ok(f"{self.ip}: CONN <- {self.path}")
        
        await self.readLoop()
        
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
            
            logger.debug(f"{self.ip}: PIN <- {self.path} ({payload})")
            
            handler = RouteRegistry._getHandler(self.path, payload["id"])
            if not handler:
                await self.send(Error("No handler found for '{payload['id']}'"))

            res = await handler(payload)
            if res:
                await self.send(**res)
        
    async def send(self, **kwargs):
        logger.debug(f"{self.ip}: POUT -> {self.path} ({kwargs})")
        await self.ws.send(json.dumps(kwargs))
        
    async def drop(self, reason: str = "dropped"):
        self.running = False
        logger.info(f"{self.ip}: DROP -> {self.path} ({reason=})")

        try:
            await self.ws.close()
        except:
            pass

        self.kill()
        
    def kill(self):
        self.running = False
        self.parent.handlers.remove(self)

class WebSocketServer:
    def __init__(self, runner):
        self.runner = runner
        
        self.active = False
        self.handlers = []
        
    def start(self):
        self.preprocessor()
        
        logger.info("Server is starting...")
        
        self.active = True
        
        threading.Thread(target=self._start).start()
        
    def _start(self):
        asyncio.run(self.__start())
        
    async def __start(self):
        async with websockets.serve(self.handler, Core.Config.getMaster("servers.ws.host"), Core.Config.getMaster("servers.ws.port")):
            await asyncio.Future()
            
    async def handler(self, ws, path):
        h = WebSocketHandler(ws, path, self)
        self.handlers.append(h)
        
        await h.onConnect()
        
    def stop(self):
        logger.info("Server is stopping...")
        
        self.active = False
        
        for h in self.handlers.copy():
            h.kill()
            
    def preprocessor(self):
        logger.info("Running pre-processor...")
        start = time.time()
        
        files = utils.walkPath("src/routes/ws")
        processed = 0
        failed = []
        
        for file in files:
            if self.preprocess_file(file): processed += 1
            
        #show stats
        registeredPackets = 0
        for route in RouteRegistry.routes.values():
            registeredPackets += len(route.keys()) #count all packets registered for a route
            
        logger.ok(f"Pre-processed {processed} files, registered {len(RouteRegistry.routes.keys())} routes and {registeredPackets} packets, took {time.time()-start:.2f}s")
        if len(failed) > 0:
            logger.warn(f"{len(failed)} Files failed to process:")
            for f in failed:
                logger.warn(f" - {f}")
                
    def preprocess_file(self, path):
        if utils.getExt(path) not in ["py", "pyw"]: return False
        
        route_prefix = path.replace("src/routes/ws", ""
                            ).replace(".py", ""
                            ).replace(".pyw", ""
                            ).replace("_", "-"
                            ).replace(" ", "-")
        
        #imports a route file and tracks all new decorator calls
        RouteRegistry.temp_routes = [] #clear prev calls
        RouteRegistry.current_route = route_prefix
        
        #logger.info(f"{route_prefix=}")
        
        try: utils.importModule(path)
        except Exception as e: #in case the dev (me) is sped
            Core.Eventer.emit("error", e, "Servers.WS", f"Failed to pre-process file '{path}'")
            return False
        
        
        return True