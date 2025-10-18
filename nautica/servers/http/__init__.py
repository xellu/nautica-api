from ...services.logger import LogManager

import flask
import waitress
import threading

from ... import Core

logger = LogManager("Servers.HTTP")

App = flask.Flask(__package__)

class HTTPServer:
    def __init__(self, runner):
        self.runner = runner
        self.active = False
        
        self._thread = None
        
    def start(self):
        logger.info("Server is starting")
        
        self.active = True
        
        t = threading.Thread(target=self._run)
        t.start()
        self._thread = t
        
    def _run(self):
        if Core.Config.getMaster("framework.devMode"):
            logger.warn("Running server in development mode")

            flask.cli.show_server_banner = self._on_load
            App.run(
                host = Core.Config.getMaster("servers.http.host"),
                port = Core.Config.getMaster("servers.http.port")
            )
            return
        
        self._on_load()
        waitress.serve(
            App,
            
            host = Core.Config.getMaster("servers.http.host"),
            port = Core.Config.getMaster("servers.http.port"),
        )
    
    def _on_load(self, *args, **kwargs):
        Core.Eventer.emit("ready.http", self)
        logger.ok(f"Listening on port {Core.Config.getMaster("servers.http.port")}")
        