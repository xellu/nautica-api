from ....manager import Logger
from ....models.Service import Service
from ....models.Websocket import WSRoute, WebSocketContext, WSError
from ....manager import Config, ConfigBuilder
from ....ext.Util import walkPath, importModule, maybeAwait
from ....ext.Path import getRoot

from starlette.websockets import WebSocketDisconnect, WebSocket as StarletteWS

from napi.ws import _WSRouter

import os

class WebSocket(Service):
    def __init__(self):
        super().__init__()
        
        self.routes: list[WSRoute] = []
        
    def onInstall(self):
        Config.Update("nautica", ConfigBuilder()
            .add("http.websockets", False, "Enable support for WebSockets")
            .build()       
        )
        
    def isEnabled(self):
        return Config("nautica")["http.websockets"] and Config("nautica")["services.http"]
        
    def onStart(self, registry):
        for file in walkPath(getRoot("src/ws")):
            if not file.endswith(".py"): continue
            
            importModule(file)
            route = _WSRouter.temp
            route.path = self.pathToRoute(file)
            self.routes.append(route)

            _WSRouter.temp = WSRoute()
        
        Logger.info(f"Registered {len(self.routes)} WebSocket endpoints")
 
    def pathToRoute(self, path):
        path = path.replace(".py", "").replace(getRoot("src/ws").replace("\\", "/"), "")
        path = path.replace("\\", "/")
        if os.path.basename(path) == "+root":
            path = path.split("/")
            path.remove("+root")
            path = "/".join(path)
            
        if not path.startswith("/"): path = "/" + path;
        return path
    
    def createHandler(self, route: WSRoute):
        async def handler(websocket: StarletteWS):
            await websocket.accept()
            ctx = WebSocketContext(websocket)
            
            Logger.info(f"{websocket.client.host}: CONN -> {route.path}")
            
            if route.onConnect:
                try:
                    await maybeAwait(route.onConnect(ctx))
                except Exception as e:
                    Logger.trace(e)
                    await websocket.close(1011)
                    return
            
            try:
                async for message in websocket.iter_json():
                    packet_id = message.get("id")
                    data = message.get("data", {})
                    
                    handler_fn = route.packets.get(packet_id)
                    if not handler_fn:
                        await websocket.send_json({"id": "error", "data": {"details": f"Unknown packet: '{packet_id}'"}})
                        continue
                    
                    try:
                        result = await maybeAwait(handler_fn(ctx, data))
                        if result:
                            await websocket.send_json({"id": packet_id, "data": result})
                    except Exception as e:
                        if not isinstance(e, WSError): Logger.trace(e)
                        await websocket.send_json({"id": "error", "data": {"details": str(e)}})
            
            except WebSocketDisconnect:
                pass
            
            finally:
                Logger.info(f"{websocket.client.host}: DISCONN -> {route.path}")
                if route.onDisconnect:
                    try:
                        await maybeAwait(route.onDisconnect(ctx))
                    except Exception as e:
                        Logger.trace(e)
        
        return handler
    
Service.Export(
    WebSocket,
    srcDir = "ws",
    depends_on = ["HTTPRouter"]
)