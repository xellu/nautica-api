from ....models.Service import Service

from starlette.applications import Starlette
from starlette.routing import Route

class HTTPServer(Service):
    def __init__(self):
        super().__init__()
        
        self.app = Starlette()
        
        
HTTPServer()