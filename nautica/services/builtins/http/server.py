from ....models.Service import Service

from starlette.applications import Starlette
from starlette.routing import Route

class HTTPServer(Service):
    def __init__(self):
        super().__init__()
        
        self.app = Starlette()
        self.router = None
        
    def onStart(self, registry):
        super().onStart(registry)
        
        # self.router = registry.Get("HTTPRouter")
        # print(self.router)
        
Service.Export(HTTPServer)