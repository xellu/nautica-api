from starlette.websockets import WebSocket
from starlette.datastructures import Address

class WebSocketContext:
    def __init__(self, ws: WebSocket):
        super().__setattr__("_store", {})
        
        self.ws = ws
        self.clientIp: Address | None = ws.client
        
                
    def __setattr__(self, name, value):
        if name.startswith("_") or name in ("ws", "clientIp", "id"):
            super().__setattr__(name, value)
        else:
            self._store[name] = value
    
    def __getattr__(self, name):
        try:
            return self._store[name]
        except KeyError:
            raise AttributeError(name)
        
        
    async def send(self, data: dict):
        await self.ws.send_json(data)
    
    async def close(self, code: int = 1000):
        await self.ws.close(code)
        
class WSRoute:
    def __init__(self):
        self.path: str = "(not set)"
        
        self.onDisconnect: callable | None = None
        self.onConnect: callable | None = None
        self.packets: dict[str, callable] = {
            #name: handler
        }
        
    def addPacket(self, packetId: str, func: callable) -> None:
        self.packets[packetId] = func
        
class WSError(Exception):
    def __init__(self, *args):
        super().__init__(*args)