from ...services.logger import LogManager
from ...ext import utils
from .router import RouteRegistry

import time
import flask
import waitress
import threading

from ... import Core, _release

from flask import request
from werkzeug.serving import WSGIRequestHandler

logger = LogManager("Servers.HTTP")

App = flask.Flask(__package__)

realIPHeader = Core.Config.getMaster("servers.http.realIPHeader")
class HTTPServer:
    def __init__(self, runner):
        self.runner = runner
        self.active = False
        
        self._thread = None
        self._routes = []
        
    def start(self):
        self.preprocessor()
        
        logger.info("Server is starting")
        
        self.active = True
        
        t = threading.Thread(target=self._run)
        t.start()
        self._thread = t
        
    def preprocessor(self):
        logger.info("Running pre-processor")
        start = time.time()

        files = utils.walkPath("src/routes/http")
        processed = 0
        failed = []
        
        for file in files:
            if utils.getExt(file) not in ["py", "pyw"]: continue
            
            #imports a route file and tracks all new decorator calls
            RouteRegistry.temp_routes = [] #clear prev calls
            try: utils.importModule(file)
            except Exception as e: #in case the dev (me) is sped
                Core.Eventer.emit("error", e, "Servers.HTTP", f"Failed to pre-process file '{file}'")

                failed.append(file)
                continue
            
            
            route_prefix = file.replace("src/routes/http", ""
                                ).replace(".py", ""
                                ).replace(".pyw", ""
                                ).replace("_", "-"
                                ).replace(" ", "-")
            
            for route in RouteRegistry.temp_routes:
                if route["name_override"] and utils.hasUnicode(route["name_override"], allowed="-_."):
                    logger.warn(f"Route '{route_prefix}/{route['name_override']}' contains disallowed characters")
                    continue
                
                route_name = route_prefix + "/" + (route["name_override"] or route["func"].__name__)
                # App.route(
                #     route_name.lower(),
                #     methods = [route["method"].upper()]
                # )(route["func"])
                App.add_url_rule(
                    rule = route_name,
                    view_func = route["func"],
                    methods = [route["method"].upper()]
                )
                
                self._routes.append(
                    {
                        "path": file,
                        "route": route_name,
                        "meta": route
                    }
                )
            
            processed += 1

        #show stats
        logger.ok(f"Pre-processed {processed} files, registered {len(self._routes)} routes, took {time.time()-start:.2f}s")
        if len(failed) > 0:
            logger.warn(f"{len(failed)} Files failed to process:")
            for f in failed:
                logger.warn(f" - {f}")
                
        from . import builtins
        
    def _run(self):
        #run in dev mode
        if Core.Config.getMaster("framework.devMode"):
            logger.warn("Running server in development mode")

            flask.cli.show_server_banner = self._on_load
            App.run(
                host = Core.Config.getMaster("servers.http.host"),
                port = Core.Config.getMaster("servers.http.port"),
                
                request_handler = WSGIOverride
            )
            return
        
        #run in prod using waitress
        self._on_load()
        waitress.serve(
            App,
            ident=f"NauticaAPI v{_release}",
            
            host = Core.Config.getMaster("servers.http.host"),
            port = Core.Config.getMaster("servers.http.port"),
        )
    
    def _on_load(self, *args, **kwargs):
        Core.Eventer.emit("ready.http", self)
        logger.ok(f"Listening on port {Core.Config.getMaster("servers.http.port")}")
    

class WSGIOverride(WSGIRequestHandler):
    #change "Server" header
    server_version = f"NauticaAPI v{_release}"
    sys_version = "(DEV)"
    
    def log_request(self, code='-', size='-'): pass #disable default logging
    
@App.before_request
def before_req():
    if realIPHeader is not None:
        request.remote_addr = request.headers.get(realIPHeader, request.remote_addr)

@App.after_request
def after_req(res):
    message = f"{request.remote_addr}: {request.method} -> {request.path} ({res.status_code})"
    if res.status_code in range(100, 399):
        logger.info(message)
    elif res.status_code in range(400, 499):
        logger.warn(message)
    else: #5XX & unknown
        logger.error(message)

    return res