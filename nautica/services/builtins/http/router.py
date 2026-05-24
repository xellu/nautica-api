from ....models.Service import Service
from ....models.Http import InFlightRouteData
from ....manager import Logger

from ....ext.Util import walkPath, importModule
from napi.http import Router

import os
class HTTPRouter(Service):
    def __init__(self):
        super().__init__()
        
        self.routes = []
    
    def pathToRoute(self, text):
        return text.replace(".py", "").replace("src/http", "")
    
    def onStart(self, registry):
        #import all files
        imported = 0
        for file in walkPath("src/http"):
            if not file.endswith(".py"): continue
            
            importModule(file)
            for PreFlightRoute in Router.temp:
                path = f"{self.pathToRoute(file)}/{PreFlightRoute.getFunc().__name__}"
                
                route = InFlightRouteData(path, PreFlightRoute)
                # print(route.getMethod(), route.getPath(), route.getRequirements().getBody())
                self.routes.append(route)
                
                
            imported += 1
        
        Logger.info(f"Imported {imported} route files")
        
Service.Export(HTTPRouter, srcDir = "http")