from ..ext.Util import randomHex

class Service:
    def __init__(self):
        self._instanceId = f"NSI_{randomHex(16)}"
        self._isInitialized = False
        
        self._register()
    
    #registry-----
    def _register(self):
        from ..services import Registry
        
        Registry.Create(self)
    
    def _unregister(self):
        from ..services import Registry
        
        Registry.Cancel(self)
    
    #service logic------
    
    def onStart(self, registry):
        self._isInitialized = True
    
    def onClose(self, reason: str | None):
        # print(reason)
        self._unregister()
