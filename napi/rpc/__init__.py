from nautica.models.Rpc import RPCNamespace, RPCFunc, RPCArg
import inspect
from typing import get_type_hints

class NamespaceManager:
    def __init__(self):
        self.namespace: RPCNamespace = None

    def Expose(self):
        def decorator(func):
            if not self.namespace: raise RuntimeError("RPC Namespace not set")

            args = []
            kwargs = []
            
            return func

        return decorator

RPC = _RPCNamespace = NamespaceManager()