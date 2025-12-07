import flask
from flask import Request
from functools import wraps

class RequestContext:
    def __init__(self, request: Request, args):
        self.request = request
        self.args = args

class RouteManager:
    def __init__(self):
        self.temp_routes = []
        self.routes = []
        
    def _create(self, method, func, name_override = None):        
        r = {
            "method": method,
            "func": func,
            "name_override": name_override
        }
        self.temp_routes.append(r)
        
    def _get(self, func):
        for r in self.routes:
            if r["func"] == func:
                return r
        raise ImportError(f"Unable to find '{func.__name__}', make sure @Request.<METHOD> is the top-most decorator")
        
    def GET(self, name_override: str | None = None):
        def decorator(func):
            # print(f"registering: {func.__name__}")
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                ctx = RequestContext(
                    flask.request, []
                )
                                
                return func(ctx, *args, **kwargs)
            
            self._create("get", wrapper, name_override)
            return wrapper
        return decorator

RouteRegistry = RouteManager()