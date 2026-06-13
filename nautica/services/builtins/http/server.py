from ....models.Service import Service
from ....manager import Config, Logger

from .middleware import Middleware
from ....models.Http import ErrorReply
from ....ext.StatusCodes import NOT_FOUND, METHOD_NOT_ALLOWED, BAD_REQUEST, INTERNAL_SERVER_ERROR
from ....ext.Path import getRoot

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import threading
import uvicorn

class HTTPServer(Service):
    def __init__(self):
        super().__init__()

        from .router import HTTPRouter

        self.app = None
        self.router: HTTPRouter = None
        self.thread = None
        self.server = None
        
        self.registry = None
        
        
    def isEnabled(self):
        return Config("nautica")["services.http"]

    def onSetup(self, registry):
        if not registry.get("Shell"): return
        
        from ..shell.decorator import RegisterCommand
        
        @RegisterCommand("lshttp", "Lists all HTTP Endpoints")
        def list_http_endpoints():
            for r in self.router.routes:
                beforeCount = len(r.getBeforeHandlers() or [])
                afterCount = len(r.getAfterHandlers() or [])
                
                Logger.info(f"- [{r.getMethod().upper()}] {r.getPath()} - {'@Before='+str(beforeCount)+', ' if beforeCount else ''}{'@After='+str(afterCount)+', ' if afterCount else ''}func={r.getFunc()}")
        
        

    def onStart(self, registry):
        super().onStart(registry)

        self.router = registry.get("HTTPRouter")
        self.registry = registry

        self.app = Starlette(
            debug = Config("nautica")["nautica.debug"],
            routes = self.transformRoutes(),
            lifespan = self.lifespan,
            exception_handlers = {
                500: self.handle_500,
                HTTPException: self.handle_error
            }
        )
        
        #cors middleware
        if Config("nautica")["http.cors.enabled"]:
            self.app.add_middleware(
                CORSMiddleware,
                    allow_origins = Config("nautica")["http.cors.origins"],
                    allow_methods = Config("nautica")["http.cors.methods"],
                    allow_headers = Config("nautica")["http.cors.headers"],
                    allow_credentials = Config("nautica")["http.cors.credentials"],
                    expose_headers = Config("nautica")["http.cors.exposeHeaders"]
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
        
        #regular routes
        for r in self.router.routes:
            out.append(
                Route(r.getPath(), r.getFunc(), methods=[r.getMethod()])
            )
            
        #static routes
        if Config("nautica")["http.static.enabled"]:
            out.append(
                Mount(Config("nautica")["http.static.endpoint"], app=StaticFiles(directory=getRoot(Config("nautica")["http.static.directory"])))
            )
            Logger.ok("Enabled static directory")
        
        #websocket routes
        ws = self.registry["WebSocket"]
        if not ws:
            return out #return routes if websockets are disabled, before adding ws routes
        
        for r in ws.routes:
            out.append(
                WebSocketRoute(r.path, ws.createHandler(r))
            )
            
        return out
        
    async def handle_500(self, request: Request, exc: HTTPException):
        Logger.trace(exc)
        return Middleware.constructResponse(
            ErrorReply(INTERNAL_SERVER_ERROR, details={"exception": str(exc)}).toReply(), INTERNAL_SERVER_ERROR
        )
        
    async def handle_error(self, request: Request, exc: HTTPException):
        return Middleware.constructResponse(
            ErrorReply(exc.status_code, details={"exception": str(exc)}).toReply(), exc.status_code
        )        

    
Service.Export(HTTPServer, depends_on=["HTTPRouter", "Shell?"])