from ..models.Service import Service
from ..manager import Logger, Config

from ..ext.Util import importModule

import os
import time

class ServiceRegistryManager:
    def __init__(self):
        self.instances: set[Service] = set()
        
        self.autoStart = False
        self.startQueue = []
        
        self.should_exit = False
        
    def Create(self, serv: Service):
        if not isinstance(serv, Service):
            raise Exception(f"'{serv}' has type {type(serv).__name__}, required type: Service")
    
        for s in self.instances:
            if s._getName() == serv._getName():
                serv.onClose(f"Service for '{serv._getName()}' was already created")
                return
            
        self.instances.add(serv)
    
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
        from .builtins.__init__ import System
        from .builtins import http, websocket, shell
        
        Logger.info("Imported built-in services")
        
        os.makedirs("plugins", exist_ok=True)
        
        imported = 0
        for f in os.listdir("plugins"): #not using walkPath on purpose
            if not f.endswith(".py") or os.path.isdir(f): continue
            
            importModule(os.path.join("plugins", f))
            imported += 1
        Logger.ok(f"Imported {imported} plugins")
    
    def _prioritize(self, queue: list) -> list:
        return sorted(queue, key=lambda s: 0 if s._getName() == "System" else 1)

    def onInstall(self):
        for serv in self._prioritize(self.startQueue):
            serv.onInstall()
            Logger.ok(f"Service Installed: {serv._getName()}")
        Logger.ok(f"Installed {len(self.startQueue)} services")

    def _topoSort(self, queue: list) -> list: #guess school is useful for something after all lol
        name_map = {s._getName(): s for s in queue}
        in_degree = {s._getName(): 0 for s in queue}
        dependents = {s._getName(): [] for s in queue}

        for s in queue:
            for dep in s._depends_on:
                if dep in in_degree:
                    in_degree[s._getName()] += 1
                    dependents[dep].append(s._getName())

        ready = [n for n, deg in in_degree.items() if deg == 0]
        result = []
        while ready:
            name = ready.pop(0)
            result.append(name_map[name])
            for dependent in dependents[name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    ready.append(dependent)

        if len(result) != len(queue):
            Logger.critical("Circular dependency detected in service start queue, unable to initialize")
            return [] #return empty list to exit
        return result

    def onStart(self):
        for serv in self._topoSort(self._prioritize(self.startQueue)):
            if not serv.isEnabled():
                Logger.warn(f"Service disabled: {serv._getName()}")
                continue #skip disabled services
            
            for dep in serv._depends_on: #crash on dependency error
                if not self.Get(dep):
                    Logger.critical(f"Unable to load service, dependency '{dep}' not found")
                    
                    self.onClose("Failed to initialize") #crash
                    return
                    
            serv.onInstall()
            serv._onStart(self)
            Logger.ok(f"Service started: {serv._getName()}")

        self.autoStart = True
        self.startQueue = []

        Logger.info("All services online")
        
        while True:
            if self.should_exit: break
            time.sleep(0.1) #keep main thread from exiting
        
    def onClose(self, reason: str | None = None):
        Logger.info(f"Stopping all services... {reason=}")
        for serv in self.instances:
            serv._onClose(reason, _avoidUnreg=True)
            Logger.ok(f"Service stopped: {serv._getName()}")
        
        self.instances = set()
        self.should_exit = True
        Logger.info("All services offline")
        
Registry = Services = ServiceRegistryManager()