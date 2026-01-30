from ...services.logger import LogManager

logger = LogManager("API.WS.Router")

class Router:
    def __init__(self):
        self.route_files = [
            # {
            #     "route": route,
            #     "path": path,
            #     "name": route_name,
            # }
        ]
        self.temp_routes = [] #same shi as route_files but gets cleared after a file is processed
        self.current_route = "" #current route that is being initialized
        
        self.routes = {
            # "/some/path": {
            #     "some.packetId": func
            # }
        }
        
    def _getHandler(self, path, packetId):
        return self.routes.get(path, {}).get(packetId)
        
    def On(self, packetId):
        def decorator(func):
            async def wrapper(payload, *args, **kwargs):
                return await func(payload, *args, **kwargs)

            self.temp_routes.append({
                "route": self.current_route,
                "packetId": packetId,
                "func": wrapper
            })
            
            if not self.routes.get(self.current_route):
                self.routes[self.current_route] = {}
                
            if self.routes[self.current_route].get(packetId):
                raise ImportError(f"Handler for packet '{packetId}' was already registered")
                
            self.routes[self.current_route][packetId] = wrapper
            logger.debug(f"Registered packet on route '{self.current_route}' with ID '{packetId}' ({func=})")

            return wrapper
        return decorator
        
RouteRegistry = Router()