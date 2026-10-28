from nautica.models.Rpc import RPCNamespace, RPCFunc, RPCArg
# from nautica.manager import Logger

import inspect
from typing import Any, get_type_hints

class NamespaceManager:
    def __init__(self):
        self.namespace: RPCNamespace = None

    def Expose(self):
        def decorator(func):
            if not self.namespace: raise RuntimeError("RPC Namespace not set")

            hints = get_type_hints(func)

            args = []
            kwargs = []

            for p in inspect.signature(func).parameters.values():
                if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                    raise TypeError(f"RPC function '{func.__name__}' cannot use *args/**kwargs ('{p.name}')")

                arg = RPCArg(p.name, hints.get(p.name, Any), p.default if p.default != inspect._empty else None)

                if p.kind == p.KEYWORD_ONLY or p.default is not p.empty: kwargs.append(arg)
                else: args.append(arg)

            self.namespace.addFunction(RPCFunc(func, func.__name__, args, kwargs, hints.get("return", Any)))

            return func

        return decorator

RPC = _RPCNamespace = NamespaceManager()