from nautica.models.Websocket import WSRoute, WebSocketContext as Context, WSError as Error

class RouteManager:
    def __init__(self):
        self.temp: WSRoute = WSRoute()
        
    def OnConnect(self):
        def decorator(func):
            self.temp.onConnect = func
            return func
        return decorator

    def OnDisconnect(self):
        def decorator(func):
            self.temp.onDisconnect = func
            return func
        return decorator

    def OnPacket(self, id: str):
        def decorator(func):
            self.temp.packets[id] = func
            return func
        return decorator
        
WS = _WSRouter = RouteManager()