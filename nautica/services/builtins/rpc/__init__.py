from ....models.Service import Service
from ....manager import Config, ConfigBuilder, Logger
from ....ext.Util import walkPath, importModule, getRoot, maybeAwait
from ....models.Rpc import RPCNamespace
from ...builtins.websocket import WebSocket
from ....models.Websocket import WSRoute

from napi.rpc import _RPCNamespace
from napi.ws import WebSocketContext

import os

class RPC(Service):
    def __init__(self):
        super().__init__()

        self.registry = None
        self.namespaces: dict[str, RPCNamespace] = {
            #name: RPCNamespace
        }
        self.router = WSRoute()

    def onInstall(self):
        Config.Update("http", ConfigBuilder()
            .add("plugins.rpc", False, comment="Enable remote function calls using websockets")
                        
            .add("rpc.endpoint", "/rpc", comment="WebSocket endpoint for the RPC to be hosted on")
            .build()              
        )

    def isEnabled(self):
        return  Config("http")["plugins.rpc"]
    
    def onSetup(self, registry):
        self.registry = registry

        #register shell commands
        if not registry.get("Shell"): return
        from ..shell.decorator import RegisterCommand

        @RegisterCommand("lsrpc", "Lists all RPC Namespaces")
        def list_rpc_namespaces():
            # print(self.namespaces)
            for ns in self.namespaces.values():
                Logger.info(f"Showing data for namespace '{ns.name}':")
                t = Logger.table()
                t.labels(["Function", "Type Hint", "Args", "Kwargs"])
                for fn in ns.funcs:
                    t.row([
                        fn.name,
                        fn.type_hint,
                        ', '.join([str(arg) for arg in fn.args]),
                        ', '.join([str(kwarg) for kwarg in fn.kwargs]),                                    
                    ])
                t.display()

    def onStart(self, registry):
        #import rpc functions
        for file in walkPath(getRoot("src/rpc")):
            if not file.endswith(".py"): continue

            name = self.pathToNamespace(file)
            namespace = self.namespaces.get(name)
            if not namespace:
                namespace = RPCNamespace(name)
                self.namespaces[name] = namespace
            
            _RPCNamespace.namespace = namespace
            importModule(file)

        #attach into websocket
        ws: WebSocket = self.registry.get(WebSocket)
        if not ws: raise ImportError("Unable to attach RPC to a WebSocket connection")

        self.router.path = Config("http")["rpc.endpoint"]
        self.router.addPacket("call", self._remoteCall)

        ws.routes.append(self.router)

    async def _remoteCall(self, ctx: WebSocketContext, data: dict):
        for k in ["namespace", "func", "args", "kwargs"]:
            if k not in data.keys():
                return await ctx.send({"id": "error", "data": {"details": f"Malformed function call, '{k}' is missing"}})

        args = data.get("args") or []
        kwargs = data.get("kwargs") or {}
        if not isinstance(args, list): return await ctx.send({"id": "error", "data": {"details": "Malformed function call, args is not a list"}})
        if not isinstance(kwargs, dict): return await ctx.send({"id": "error", "data": {"details": "Malformed function call, kwargs is not a dict"}})
        
            
        ns = self.namespaces.get(data.get("namespace"))
        if ns is None:
            return await ctx.send({"id": "error", "data": {"details": "No such namespace found"}})

        func_name = data.get("func")
        for fn in ns.funcs:
            if fn.name == func_name:
                try:
                    out = await maybeAwait(fn.func(*args, **kwargs))
                except Exception as e:
                    Logger.trace(e)
                    return await ctx.send({"id": "error", "data": {"details": "Function failed to execute"}})
                return await ctx.send({"id": "call", "data": {"output": out}})

        
        return await ctx.send({"id": "error", "data": {"details": f"Function not found"}})
            
    def pathToNamespace(self, path: str) -> str:
        path = path.replace(".py", "").replace(getRoot("src/rpc").replace("\\", "/"), "")
        path = path.replace("\\", "/")

        if os.path.basename(path) == "+root":
            path = path.split("/")
            path.remove("+root")
            path = "/".join(path)

        path = path.split("/")
        for i, part in enumerate(path):
            path[i] = part.capitalize()

        return "".join(path)

Service.Export(
    RPC,
    srcDir="rpc",
    depends_on=["WebSocket", "Shell?", "HTTPServer:after"]
)