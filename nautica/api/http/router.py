import time
import flask
from functools import wraps

from ...services.logger import LogManager

from .models import RequestContext, RouteData


logger = LogManager("API.HTTP.Router")
    
class Decorator:
    def __init__(self, manager, method, name_override):
        self.manager = manager
        
        self.method = method
        self.name_override = name_override
        
    def decorator(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from . import Require, Error

            created_at = time.time()
            request = flask.request
            requirements = Require._parse(func, request)
            
            if not requirements._ok:
                return Error(requirements._error), 400
            
            ctx = RequestContext(
                request = request,
                args = requirements,
                
                created_at = created_at
            )
                            
            return func(ctx, *args, **kwargs)
        
        # self.manager._create(self.method, wrapper, self.name_override)
        self.manager._create(RouteData(
            method = self.method,
            func = func,
            wrapper = wrapper,
            name_override = self.name_override
        ))
        
        return wrapper
    
class RouteManager:
    def __init__(self):
        self.temp_routes = []
        self.routes = []
        
    def _create(self, r: RouteData):
        self.temp_routes.append(r)
        logger.debug(f"Registered route for {r.func.__name__}, {r.method=}, {r.name_override=}")


    def GET(self, name_override: str | None = None):
        return Decorator(self, "get", name_override).decorator
    
    def POST(self, name_override: str | None = None):
        return Decorator(self, "post", name_override).decorator
    
    def HEAD(self, name_override: str | None = None):
        return Decorator(self, "head", name_override).decorator
    
    def PUT(self, name_override: str | None = None):
        return Decorator(self, "put", name_override).decorator
    
    def DELETE(self, name_override: str | None = None):
        return Decorator(self, "delete", name_override).decorator
    
    def CONNECT(self, name_override: str | None = None):
        return Decorator(self, "connect", name_override).decorator
    
    def OPTIONS(self, name_override: str | None = None):
        return Decorator(self, "options", name_override).decorator
    
    def TRACE(self, name_override: str | None = None):
        return Decorator(self, "trace", name_override).decorator
    
    def PATCH(self, name_override: str | None = None):
        return Decorator(self, "patch", name_override).decorator



RouteRegistry = RouteManager()