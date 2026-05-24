from ..ext.Util import randomHex
from ..manager import Logger

import os

class Service:
    """Base class for all Nautica services; handles registration and lifecycle hooks."""

    def __init__(self):
        self._instanceId = f"NSI_{randomHex(16)}"
        self._isInitialized = False

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
        """Instantiates and registers a Service subclass; creates a src/ directory on disk if provided."""
        if not isinstance(service, type) or not issubclass(service, Service):
            raise TypeError(f"Cannot export non-Service type '{service}'")

        path = os.path.join("src", str(srcDir))
        if srcDir and not os.path.exists(path):
            os.makedirs(path)

        s = service()
        s._register()

    def _onStart(self, registry):
        self.onStart(registry)
        self._isInitialized = True
        Logger.ok(f"Service started: {self._getName()}")

    def onStart(self, registry):
        """Called when the service is started by the registry. Override to add startup logic."""
        pass

    def _onClose(self, reason: str | None = None, _avoidUnreg=False):
        if not _avoidUnreg:
            self._unregister()
        self.onClose(reason)
        Logger.ok(f"Service stopped {self._getName()}")

    def onClose(self, reason: str | None):
        """Called when the service is stopped. Override to add teardown logic."""
        pass