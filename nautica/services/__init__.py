from ..models.Service import Service
from ..manager import Logger, Config

from ..ext.Util import importModule
import os

class ServiceRegistry:
    def __init__(self):
        self.instances: set[Service] = set()
        
        self.autoStart = False
        self.startQueue = []
        
    def Create(self, serv: Service):
        if not isinstance(serv, Service):
            raise Exception(f"'{serv}' has type {type(serv).__name__}, required type: Service")
    
        for s in self.instances:
            if s._getName() == serv._getName():
                serv.onClose(f"Service for '{serv._getName()}' was already created")
                return
            
        self.instances.add(serv) #doesnt allow duplicates anyway
    
        if self.autoStart: serv._onStart(self)
        else: self.startQueue.append(serv)
        
    def Cancel(self, serv: Service):
        if serv in self.instances:
            self.instances.remove(serv)
            
    def Get(self, serviceName) -> Service | None:
        for s in self.instances:
            if s._getName() == serviceName:
                return s
    
    def __getitem__(self, serviceName) -> Service | None:
        return self.Get(serviceName)
    
    def ImportAll(self):
        #import builtin services
        from .builtins import __init__
        if Config("nautica")["services.http"]: from .builtins import http
        
        Logger.info("Imported built-in services")
        
        os.makedirs("plugins", exist_ok=True)
        
        imported = 0
        for f in os.listdir("plugins"): #not using walkPath on purpose
            if not f.endswith(".py") or os.path.isdir(f): continue
            
            importModule(os.path.join("plugins", f))
            imported += 1
        Logger.ok(f"Imported {imported} plugins")
    
    def onStart(self):
        #run queued services
        for serv in self.startQueue:
            serv._onStart(self)

        self.autoStart = True #enable autostart upon initializing fully
        self.startQueue = []
        
        Logger.info("All services online")
        
    def onClose(self, reason: str | None = None):
        Logger.error(f"Stopping all services... {reason=}")
        for serv in self.instances:
            serv._onClose(reason, _avoidUnreg=True)
        
        self.instances = set()
        Logger.info("All services offline")
        
Registry = Services = ServiceRegistry()