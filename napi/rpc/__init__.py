from nautica.models.Rpc import RPCNamespace, RPCFunc, RPCArg
from nautica.manager import Logger

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

            for p in inspect.signature(func).parameters.values():
                Logger.info(f"{p.name}, {p.kind}, {p.annotation}, {p.default}")    
                 

            #TODO: figure out how to extract input args, etc. correctly
            Logger.info(get_type_hints(func))

            self.namespace.funcs.append(func)
            
            return func

        return decorator

RPC = _RPCNamespace = NamespaceManager()