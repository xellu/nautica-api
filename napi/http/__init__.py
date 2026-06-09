
from nautica.manager import Logger

from nautica.services.builtins.http.middleware import Middleware
from nautica.models.Http import RouteRequirements, RequestContext as Context, Reply, ErrorReply as Error
from nautica.models import Requirements
from nautica.ext import StatusCodes

from starlette.responses import JSONResponse, PlainTextResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse

Require = Requirements

class RouteManager:
    def __init__(self):
        self.temp = []
        
    def _create(self, r):
        self.temp.append(r)
        Logger.debug(f"Registered route for {r.func.__name__}, {r.method=}, {r.name=}")

    def GET(self, name: str | None = None):
        """Register a GET route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "get", name).decorator
    
    def POST(self, name: str | None = None):
        """Register a POST route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "post", name).decorator
    
    def HEAD(self, name: str | None = None):
        """Register a HEAD route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "head", name).decorator
    
    def PUT(self, name: str | None = None):
        """Register a PUT route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "put", name).decorator
    
    def DELETE(self, name: str | None = None):
        """Register a DELETE route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "delete", name).decorator
    
    def CONNECT(self, name: str | None = None):
        """Register a CONNECT route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "connect", name).decorator

    def TRACE(self, name: str | None = None):
        """Register a TRACE route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "trace", name).decorator
    
    def PATCH(self, name: str | None = None):
        """Register a PATCH route. `name` overrides the auto-derived URL path."""
        return Middleware(self, "patch", name).decorator

    def Require(self,
            body: dict = None,
            headers: dict = None,
            cookies: dict = None,
            query: dict = None,
            files: dict = None
    ):
        """
        Declare required inputs for a route handler.

        Each field accepts a dict mapping key names to expected types,
        `Requirement` expressions, or nested dicts for JSON objects.
        File fields must map to `Requirements.File` instances.

        Raises `TypeError` if any value in the schema is not a valid type.

        Example:

            @HTTP.POST()
            @HTTP.Require(
                body={"username": str, "age": int},
                files={"avatar": Require.File(Require.File.MB(2))},
                query={"tokenType": Require.AnyOf("JWT", "NAuth")}
            )
            async def create_user(ctx: Context):
                ...
        """
        
        for field in [body or {}, headers or {}, cookies or {}, query or {}]:
            for v in field.values():
                if not (isinstance(v, type) or isinstance(v, Requirements.Requirement) or isinstance(v, dict)): raise TypeError(f"Context builder only accepts types, dicts and Requirements")
        
        for v in (files or {}).values():
            if not isinstance(v, Requirements.File): raise TypeError(f"File dict only accepts Requirements.File, provided '{type(v).__name__}'")
        
        def decorator(func):
            func._requirements = RouteRequirements(
                body=body,
                headers=headers,
                cookies=cookies,
                query=query,
                files = files
            )
            return func
    
        return decorator
    
    def ReplyModel(self, model: type | dict | Requirements.Requirement):
        """
        Declare the expected response schema for a route.

        Used for documentation and validation purposes. `model` can be
        a type, a dict schema, or a `Requirement` expression.
        """
        def decorator(func):
            func._replyModel = model
            return func
        
        return decorator
    
    def Before(self, fn):
        """
        Register a before-hook for a route.

        `fn` will be called before the decorated handler on each request.
        Multiple hooks can be chained by applying `@Before` multiple times.

        Example::

            @HTTP.GET()
            @HTTP.Before(auth_check)
            async def dashboard(ctx: Context): ...
        """
        
        def decorator(func):
            if not hasattr(fn, "_before"):
                fn._before = []
            fn._before.append(func)
            return func
        return decorator

    def After(self, fn):
        """
        Register an after-hook for a route.

        `fn` will be called after the decorated handler on each request.
        Multiple hooks can be chained by applying `@After` multiple times.
        """
        def decorator(func):
            if not hasattr(fn, "_after"):
                fn._after = []
            fn._after.append(func)
            return func
        return decorator

    
    
        

HTTP = _HTTPRouter = RouteManager()
