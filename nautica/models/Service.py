from ..ext.Util import randomHex
from ..manager import Logger

import os

class Service:
    def __init__(self):
        self._instanceId = f"NSI_{randomHex(16)}"
        self._isInitialized = False
    
    #registry-----
    def _register(self):
        from ..services import Registry
        
        Registry.Create(self)
    
    def _unregister(self):
        from ..services import Registry
        
        Registry.Cancel(self)
    
    def _getName(self) -> str:
        return type(self).__name__
    
    @staticmethod
    def Export(service, srcDir: str | None = None):
        if not isinstance(service, type) or not issubclass(service, Service):
            raise TypeError(f"Cannot export non-Service type '{service}'")
        
        if srcDir:
            os.makedirs(os.path.join("project/src", srcDir))
        
        s = service()
        s._register()
    
    #service logic------
    
    def _onStart(self, registry):
        self.onStart(registry)
        
        self._isInitialized = True
        Logger.ok(f"Service started: {self._getName()}")
    
    def onStart(self, registry):
        pass
    
    def _onClose(self, reason: str | None = None, _avoidUnreg = False):
        if not _avoidUnreg: self._unregister()

        self.onClose(reason)
        Logger.ok(f"Service stopped {self._getName()}")

    def onClose(self, reason: str | None):
        pass