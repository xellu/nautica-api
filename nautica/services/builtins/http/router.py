from ....models.Service import Service
from ....manager import Logger

class HTTPRouter(Service):
    def __init__(self):
        super().__init__()
    
    def onStart(self, registry):
        pass
        
Service.Export(HTTPRouter, srcDir = "http")