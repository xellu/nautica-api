
from nautica.manager import Logger

from nautica.services.builtins.http.middleware import Decorator
from nautica.models.Http import RouteRequirements, RequestContext as Context, Reply, Cookie
from nautica.models import HttpRequirements

Require = HttpRequirements

class RouteManager:
    def __init__(self):
        self.temp = []
        
    def _create(self, r):
        self.temp.append(r)
        Logger.debug(f"Registered route for {r.func.__name__}, {r.method=}, {r.name=}")

    def GET(self, name: str | None = None):
        return Decorator(self, "get", name).decorator
    
    def POST(self, name: str | None = None):
        return Decorator(self, "post", name).decorator
    
    def HEAD(self, name: str | None = None):
        return Decorator(self, "head", name).decorator
    
    def PUT(self, name: str | None = None):
        return Decorator(self, "put", name).decorator
    
    def DELETE(self, name: str | None = None):
        return Decorator(self, "delete", name).decorator
    
    def CONNECT(self, name: str | None = None):
        return Decorator(self, "connect", name).decorator

    def TRACE(self, name: str | None = None):
        return Decorator(self, "trace", name).decorator
    
    def PATCH(self, name: str | None = None):
        return Decorator(self, "patch", name).decorator

    def Require(self, body: dict = None, headers: dict = None, cookies: dict = None, query: dict = None):
        def decorator(func):
            func._requirements = RouteRequirements(
                body=body,
                headers=headers,
                cookies=cookies,
                query=query,
            )
            return func
        return decorator

HTTP = Router = RouteManager()
