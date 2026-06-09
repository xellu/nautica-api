from ..models.Service import Service, ServiceContext, ServiceHelper
from ..manager import Logger

from ..ext.Util import importModule
from ..ext.Path import getRoot

import os
import time
from typing import Type, TypeVar, overload, Any

T = TypeVar('T', bound='Service')

class ServiceRegistryManager:
    def __init__(self):
        self.instances: set[Service] = set()
        
        self.autoStart = False
        self.startQueue: list[Service] = []
        
        self.should_exit = False
        
    def create(self, serv: Service):
        if not isinstance(serv, Service):
            raise Exception(f"'{serv}' has type {type(serv).__name__}, required type: Service")
    
        for s in self.instances:
            if s._getName() == serv._getName():
                serv.onClose(f"Service for '{serv._getName()}' was already created")
                return
            
        self.instances.add(serv)
    
        if self.autoStart:
            serv.onInstall()
            serv.onSetup()
            serv._onStart(self)
            return
        
        self.startQueue.append(serv)
        
    def cancel(self, serv: Service):
        if serv in self.instances:
            self.instances.remove(serv)
            
    @overload
    def get(self, target: Type[T]) -> T | None:
        pass
    
    @overload
    def get(self, target: str) -> Service | None:
        pass

    #this is kinda how java works
    def get(self, target: Service | str) -> Any | None:
        if isinstance(target, str):
            for s in self.instances:
                if s._getName() == target:
                    return s
        else:
            for s in self.instances:
                if isinstance(s, target):
                    return s
                    
        return None
    
    def __getitem__(self, serviceName) -> Service | None:
        return self.get(serviceName)
    
    def importAll(self):
        #import builtin services
        from .builtins.__init__ import System
        from .builtins import http, websocket, shell
        
        # Logger.info("Imported built-in services")
        
        os.makedirs(getRoot("plugins"), exist_ok=True)

        imported = 0
        for f in os.listdir(getRoot("plugins")):
            full_path = getRoot("plugins", f)
            if os.path.isdir(full_path):
                init = os.path.join(full_path, "__init__.py")
                if not os.path.exists(init): continue
                importModule(init, name=f"plugins.{f}")
            elif f.endswith(".py"):
                importModule(full_path, name=f"plugins.{os.path.splitext(f)[0]}")
            else:
                continue
            imported += 1
                    
        if imported > 0: Logger.info(f"Imported {imported} plugins")
        
    def _prioritize(self, queue: list) -> list:
        return sorted(queue, key=lambda s: 0 if s._getName() == "System" else 1)

    def onInstall(self):
        for serv in self._prioritize(self.startQueue):
            try:
                serv.isEnabled()
                serv.onInstall()
            except Exception as e:
                Logger.trace(e)
            else:
                Logger.debug(f"Service Installed: {serv._getName()}")
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
        # INSTALL---------------
        Logger.info("Running pre-setup configuration...")
        for serv in self.startQueue:
            if not serv.isEnabled(): continue
            
            try:
                serv.onInstall()
            except Exception as e:
                Logger.trace(e)
                self.onClose("Failed to handle pre-setup configuration")
        
            #resolve dependencies
            deps: list[ServiceContext] = []
            for dep in serv._depends_on.copy():
                ctx: ServiceContext = ServiceHelper(dep).getContext()

                deps.append(ctx)
                if ctx.after:
                    #handle :after
                    target: Service | None = self.get(ctx.name)
                    if (not target or not target.isEnabled()) and not ctx.optional:
                        Logger.critical(f"Unable to resolve service dependencies, dependency '{dep}' {'not found' if not dep else 'is disabled'}")
                        self.onClose("Failed to resolve dependencies")
                        return
                    
                    if target:
                        target._depends_on.append(serv._getName() + "?" if ctx.optional else "")
                        target._depends_on_ctx.append(ctx)
                    
                    serv._depends_on.remove(dep)
                else:
                    #add to ctx if not :after
                    serv._depends_on_ctx.append(ctx)
                            
        boot_order: list[Service] = self._topoSort(self._prioritize(self.startQueue))
        
        # SETUP----------------------
        Logger.info("Running service setup...")
        for serv in boot_order:
            if not serv.isEnabled():
                Logger.info(f"Service disabled: {serv._getName()}")
                continue #skip disabled services
            
            
            for ctx in serv._depends_on_ctx: #crash on dependency error
                dep: Service = self.get(ctx.name)
                if (not dep or not dep.isEnabled()) and not ctx.optional:
                    Logger.critical(f"Unable to load service, dependency '{ctx.name}' {'not found' if not dep else 'is disabled'}")
                    
                    self.onClose("Unable to initialize") #crash
                    return
            
            try:
                serv.onSetup(self)
            except Exception as e:
                Logger.trace(e)
                self.onClose(f"Failed to initialize")
                return
            else:
                Logger.debug(f"Service Setup: {serv._getName()}")

        # STARTUP --------------------------
        Logger.info("Booting up services...")
        for serv in boot_order:
            if not serv.isEnabled():
                continue
            
            try:
                serv._onStart(self)
            except Exception as e:
                Logger.trace(e)
                self.onClose(f"Failed to start services")
                return
            else:
                Logger.debug(f"Service Started: {serv._getName()}")
                
        self.autoStart = True
        self.startQueue = []

        Logger.ok("All services online")
        
        #keep main thread from exiting------------------
        while True:
            if self.should_exit: break
            time.sleep(0.1) 
        
        
        
    def onClose(self, reason: str | None = None):
        Logger.info(f"Stopping all services... {reason=}")
        for serv in self.instances:
            try:
                serv._onClose(reason, _avoidUnreg=True)
            except Exception as e:
                Logger.trace(e)
            else:
                Logger.ok(f"Service stopped: {serv._getName()}")
        
        self.instances = set()
        self.should_exit = True
        Logger.info("All services offline")
        
Registry = Services = ServiceRegistryManager()