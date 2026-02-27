from ...services.logger import LogManager
from ...ext import utils
from ...ext.static import STATUS_CODES
from ...ext.logging_patch import PatchLog, LogData
from ...api.http.router import RouteRegistry

import time
import logging
import uvicorn
import threading

from ... import Core, _release

from fastapi import (
    FastAPI,
    Request
)
from werkzeug.serving import WSGIRequestHandler

logger = LogManager("Servers.HTTP")

App = FastAPI()

realIPHeader = Core.Config.getMaster("servers.http.realIPHeader")
class HTTPServer:
    def __init__(self, runner):
        self.runner = runner
        self.active = False
        
        self._thread = None
        
    def start(self):
        self.preprocessor()
        
        logger.info("Server is starting...")
        
        self.active = True
        
        t = threading.Thread(target=self._run)
        t.start()
        self._thread = t
        
    def preprocessor(self):
        logger.info("Running pre-processor...")
        start = time.time()

        files = utils.walkPath("src/routes/http")
        processed = 0
        failed = []
        
        for file in files:
            if self.preprocess_file(file): processed += 1

        #show stats
        logger.ok(f"Pre-processed {processed} files, registered {len(RouteRegistry.routes)} routes, took {time.time()-start:.2f}s")
        if len(failed) > 0:
            logger.warn(f"{len(failed)} Files failed to process:")
            for f in failed:
                logger.warn(f" - {f}")
                
        from . import builtins
        
    def preprocess_file(self, path):
        if utils.getExt(path) not in ["py", "pyw"]: return False
        
        #imports a route file and tracks all new decorator calls
        RouteRegistry.temp_routes = [] #clear prev calls
        try: utils.importModule(path)
        except Exception as e: #in case the dev (me) is sped
            Core.Eventer.emit("error", e, "Servers.HTTP", f"Failed to pre-process file '{path}'")
            return False
        
        
        route_prefix = path.replace("src/routes/http", ""
                            ).replace(".py", ""
                            ).replace(".pyw", ""
                            ).replace("_", "-"
                            ).replace(" ", "-"
                            ).replace("[", "<"
                            ).replace("]", ">")
        
        for route in RouteRegistry.temp_routes:
            if route.name_override and utils.hasUnicode(route.name_override, allowed="-_.<>/"):
                logger.warn(f"Route '{route_prefix}/{route.name_override}' contains disallowed characters")
                continue
            
            route_name = route_prefix + "/" + (route.name_override or route.func.__name__)
            route_name = route_name.replace("+root/", "")
            
            # rule = App.add_url_rule( #does not return rule obj - needs fixing
            #     rule = route_name,
            #     view_func = route.wrapper,
            #     methods = [route.method.upper()]
            # )
            rule = App.add_api_route(
                path = route_name,
                endpoint = route.wrapper,
                methods = [ route.method.upper() ],
                name = route_name
            )
            
            RouteRegistry.routes.append(
                {
                    "route": route,
                    "path": path,
                    "name": route_name,
                    "rule": rule
                }
            )
        return True
        
        
    def remove_routes(self, path):
        """Remove all routes that matches any parameter (path, route, rule or meta)"""
        to_remove = []
        for r in RouteRegistry.routes:
            if (r["path"] == path): to_remove.append(r)
            
        for r in to_remove:
            self.remove_route(r)
            
        return len(to_remove)
                
    def remove_route(self, route: dict):
        App.router.routes = [
            r for r in App.router.routes if r.path != route["name"]
        ]
        
    def get_rule(self, route: dict):
        for rule in App.url_map.iter_rules():
            if rule.rule == route["name"]:
                return rule
        
    def _run(self):
        #run in dev mode
        if Core.Config.getMaster("framework.devMode"):
            logger.warn("Running server in development mode")

        self._on_load()
        
        PatchLog(LogData(logging.getLogger("uvicorn")))
        PatchLog(LogData(logging.getLogger("uvicorn.error"), rename="Uvicorn"))
        PatchLog(LogData(logging.getLogger("uvicorn.access")))
        
        uvicorn.run(
            App,
            
            host = Core.Config.getMaster("servers.http.host"),
            port = Core.Config.getMaster("servers.http.port"),   
            
            server_header = False,
            access_log = False
        )
    
    def _on_load(self, *args, **kwargs):
        Core.Eventer.emit("ready.http", self)
        logger.ok(f"Listening on port {Core.Config.getMaster("servers.http.port")}")
    

@App.middleware("http")
async def log_middleware(request: Request, call_next):
    real_ip_header = Core.Config.getMaster("servers.http.realIPHeader")

    if real_ip_header:
        request.scope["client"] = (
            request.headers.get(real_ip_header),
            0
        )

    res = await call_next(request)
    res.headers["server"] = f"NauticaAPI v{_release}"

    message = f"{request.client.host}: {request.method} -> {request.url.path} ({res.status_code} {STATUS_CODES.get(res.status_code, 'UNKNOWN')})"

    if 100 <= res.status_code < 399:
        logger.info(message)
    elif 400 <= res.status_code < 499:
        logger.warn(message)
    else:
        logger.error(message)

    return res

# class WSGIOverride(WSGIRequestHandler):
#     #change "Server" header
#     server_version = f"NauticaAPI v{_release}"
#     sys_version = "(DEV)"
    
#     def log_request(self, code='-', size='-'): pass #disable default logging
    
# @App.before_request
# def before_req():
#     if realIPHeader is not None:
#         request.remote_addr = request.headers.get(realIPHeader, request.remote_addr)

# @App.after_request
# def after_req(res):
#     message = f"{request.remote_addr}: {request.method} -> {request.path} ({res.status_code})"
#     if res.status_code in range(100, 399):
#         logger.info(message)
#     elif res.status_code in range(400, 499):
#         logger.warn(message)
#     else: #5XX & unknown
#         logger.error(message)

#     return res

# @App.errorhandler(TypeError)
# def onTypeError(error):
#     logger.trace(error)
#     return Error("Internal server error"), 500

# @App.errorhandler(500)
# def onInternalServerError(error):
#     logger.trace(error)
#     return Error("Internal server error"), 500

# @App.errorhandler(404)
# def onNotFound(error):
#     return Error("Resource not found"), 404