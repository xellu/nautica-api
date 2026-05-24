
from nautica.manager import Logger

from nautica.services.builtins.http.middleware import Middleware
from nautica.models.Http import RouteRequirements, RequestContext as Context, Reply, ErrorReply as Error
from nautica.models import HttpRequirements
from nautica.ext import StatusCodes

from starlette.responses import JSONResponse, PlainTextResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse

Require = HttpRequirements

class RouteManager:
    def __init__(self):
        self.temp = []
        
    def _create(self, r):
        self.temp.append(r)
        Logger.debug(f"Registered route for {r.func.__name__}, {r.method=}, {r.name=}")

    def GET(self, name: str | None = None):
        return Middleware(self, "get", name).decorator
    
    def POST(self, name: str | None = None):
        return Middleware(self, "post", name).decorator
    
    def HEAD(self, name: str | None = None):
        return Middleware(self, "head", name).decorator
    
    def PUT(self, name: str | None = None):
        return Middleware(self, "put", name).decorator
    
    def DELETE(self, name: str | None = None):
        return Middleware(self, "delete", name).decorator
    
    def CONNECT(self, name: str | None = None):
        return Middleware(self, "connect", name).decorator

    def TRACE(self, name: str | None = None):
        return Middleware(self, "trace", name).decorator
    
    def PATCH(self, name: str | None = None):
        return Middleware(self, "patch", name).decorator

    def Require(self, body: dict = None, headers: dict = None, cookies: dict = None, query: dict = None):
        for field in [body or {}, headers or {}, cookies or {}, query or {}]:
            for v in field.values():
                if not (isinstance(v, type) or isinstance(v, HttpRequirements.Requirement)): raise TypeError(f"Context builder only accepts types and Requirements")
        
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
