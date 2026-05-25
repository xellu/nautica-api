from ....models.Service import Service
from ....manager import Config, Logger

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.routing import Route, Mount

from contextlib import asynccontextmanager
import threading
import uvicorn

class HTTPServer(Service):
    def __init__(self):
        super().__init__()

        self.app = None
        self.router = None
        self.thread = None
        self.server = None

    def onStart(self, registry):
        super().onStart(registry)

        self.router = registry.Get("HTTPRouter")

        self.app = Starlette(
            debug = Config("nautica")["nautica.debug"],
            routes = self.transformRoutes(),
            lifespan = self.lifespan
        )
        self.thread = t = threading.Thread(target=self._run)
        t.start()

    def onClose(self, reason):
        if self.server:
            self.server.should_exit = True

    def _run(self):
        host = Config("nautica")["http.host"]
        port = Config("nautica")["http.port"]
        config = uvicorn.Config(self.app, host=host, port=port, log_config=None)
        self.server = uvicorn.Server(config)
        self.server.run()
        
    @asynccontextmanager
    async def lifespan(self, app):
        Logger.ok(f"HTTP Server listening on {Config('nautica')['http.host']}:{Config('nautica')['http.port']}")
        yield

    def transformRoutes(self):
        out = []
        for r in self.router.routes:
            out.append(
                Route(r.getPath(), r.getFunc(), methods=[r.getMethod()])
            )
            
        if Config("nautica")("http.static.enabled"):
            out.append(
                Mount(Config("nautica")["http.static.endpoint"], app=StaticFiles(directory=Config("nautica")["http.static.directory"]))
            )
            Logger.ok("Enabled static directory")
        return out

Service.Export(HTTPServer, depends_on=["HTTPRouter"])