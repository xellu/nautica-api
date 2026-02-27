import time
import json
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from ...services.logger import LogManager
from ...ext.utils import maybeAwait

from .models import RequestContext, RouteData


logger = LogManager("API.HTTP.Router")
    
class Decorator:
    def __init__(self, manager, method: str, name_override: str | None):
        self.manager = manager
        
        self.method = method
        self.name_override = name_override

    def decorator(self, func):
        # @wraps(func)
        async def wrapper(request: Request):
            from . import Require

            created_at = time.time()
            
            requirements = await Require._parse(func, request)

            if not requirements._ok:
                return JSONResponse(
                    content = {
                        "error": requirements._error
                    },
                    status_code = 422
                )

            ctx = RequestContext(
                request = request,
                args = requirements,
                
                created_at = created_at
            )

            try: 
                res = await maybeAwait(func(ctx))

                # If your route returned a dict, wrap it in JSONResponse
                if isinstance(res, dict) or isinstance(res, list):
                    return JSONResponse(content=res)

                # If your route returned a tuple like (data, status_code)
                elif isinstance(res, tuple):
                    content, code = res
                    if isinstance(content, (dict, list)): return JSONResponse(content=content, status_code=code)
                    else: return PlainTextResponse(content, status_code=code)

                # If it’s already a Response object
                return res
            except Exception as err:
                logger.trace(err)
                return JSONResponse(
                    content = {
                        "error": str(err)
                    },
                    status_code = 500
                )

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
        self.routes = [
            # {
            #     "route": RouteData obj,
            #     "path": path to src file,
            #     "name": /api/v1/example,
            #     "rule": flask rule obj
            # }
        ]
        
    def _create(self, r: RouteData):
        self.temp_routes.append(r)
        logger.debug(f"Registered route for {r.func.__name__}, {r.method=}, {r.name_override=}")

    def _getFromName(self, name):
        for r in self.routes:
            if r["name"].lower() == name:
                return r

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