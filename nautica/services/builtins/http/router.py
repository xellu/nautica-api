from ....models.Service import Service
from ....models.Http import InFlightRouteData
from ....manager import Logger, Config

from ....ext.Util import walkPath, importModule
from ....ext.Path import getRoot
from napi.http import _HTTPRouter

import os
class HTTPRouter(Service):
    def __init__(self):
        super().__init__()
        
        self.routes: list[InFlightRouteData] = []
    
    def pathToRoute(self, path):
        path = path.replace(".py", "").replace(getRoot("src/http").replace("\\", "/"), "")
        path = path.replace("\\", "/")
        if os.path.basename(path) == "+root":
            path = path.split("/")
            path.remove("+root")
            path = "/".join(path)
        return path
    
    def getByFunc(self, func):
        for r in self.routes:
            if r.getFunc() is func:
                return r
    
    def getByPath(self, path):
        for r in self.routes:
            if r.getPath() == path:
                return r
    
    def isEnabled(self):
        return Config("nautica")["services.http"]
    
    def onStart(self, registry):
        #import all files
        imported = 0
        for file in walkPath(getRoot("src/http")):
            if not file.endswith(".py"): continue
            
            importModule(file)
            for PreFlightRoute in _HTTPRouter.temp:
                path = f"{self.pathToRoute(file)}/{PreFlightRoute.getName()}"
                path = path.replace("//", "/").replace("..", "")
                
                route = InFlightRouteData(
                    path = path,
                    preflight = PreFlightRoute,
                    sourceFile = file
                )
                # print(route.getMethod(), route.getPath(), route.getRequirements().getBody())
                self.routes.append(route)
               
            _HTTPRouter.temp = [] 
            imported += 1
        
        Logger.info(f"Processed {imported} files, registered {len(self.routes)} endpoints")
        
Service.Export(HTTPRouter, srcDir = "http", depends_on=["HTTPConfig"])