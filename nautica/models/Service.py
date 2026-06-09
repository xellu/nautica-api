from ..ext.Util import randomHex
from ..ext.Path import getRoot
from ..manager import Logger

import os

class Service:
    """Base class for all Nautica services; handles registration and lifecycle hooks."""

    def __init__(self):
        self._instanceId = f"NSI_{randomHex(16)}"
        self._isInitialized = False
        
        self._depends_on: list[str] = []
        self._depends_on_ctx: list[ServiceContext] = []

    def _register(self):
        from ..services import Registry
        Registry.create(self)

    def _unregister(self):
        from ..services import Registry
        Registry.cancel(self)

    def _getName(self) -> str:
        return type(self).__name__

    @staticmethod
    def Export(service, srcDir: str | None = None, depends_on: list[str] = None):
        """Instantiates and registers a Service subclass; creates a src/ directory on disk if provided."""
        if not isinstance(service, type) or not issubclass(service, Service):
            raise TypeError(f"Cannot export non-Service type '{service}'")

        # path = os.path.join("src", str(srcDir))
        path = getRoot("src", str(srcDir))
        if srcDir and not os.path.exists(path):
            os.makedirs(path)

        s = service()
        s._depends_on = depends_on or []
        s._register()

    def onInstall(self):
        """Called when the service is being installed. Override to add config creation logic, etc."""
        pass
    
    def isEnabled(self):
        """Return True of False to indicate if the service is enabled"""
        return True

    # ON SETUP-----------
    
    def onSetup(self, registry):
        """Called when the service is being initialized. Override to open database connections, register middlewares."""
        pass

    # ON START-----------

    def _onStart(self, registry):
        self.onStart(registry)
        self._isInitialized = True

    def onStart(self, registry):
        """Called when the service is started by the registry. Override to add startup logic."""
        pass

    # ON CLOSE-----------

    def _onClose(self, reason: str | None = None, _avoidUnreg=False):
        if not _avoidUnreg:
            self._unregister()
        self.onClose(reason)

    def onClose(self, reason: str | None):
        """Called when the service is stopped. Override to add teardown logic."""
        pass

class ServiceContext:
    def __init__(self, name: str, optional: bool, after: bool):
        self.name = name
        self.optional = optional
        self.after = after
    
    def __str__(self):
        return f"ServiceContext({self.name=}, {self.optional=}, {self.after=})"
    
class ServiceHelper:
    def __init__(self, service: str):
        self.service = service
        
    def getContext(self) -> ServiceContext:
        s = self.service
        
        name = ""
        after = False
        
        #?
        optional = s.endswith("?")
        s = s.replace("?", "")
        
        #:after
        parts = s.split(":")
        if len(parts) >= 2:
            if parts[1] == "after":
                after = True
                
        name = parts[0]
        
        # print(parts, name)
        return ServiceContext(
            name, optional, after
        )