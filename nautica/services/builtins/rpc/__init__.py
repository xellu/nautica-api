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
            .add("rpc.generateTo", [], comment="A path to where should auto-generate client files to (example: ../frontend/src/lib/client.ts - relative to app path); available languages: ts, py (determined by file extension)")
            .build()              
        )

    def isEnabled(self):
        return  Config("http")["plugins.rpc"]
    
    def onSetup(self, registry):
        self.registry = registry

        #register shell commands
        if not registry.get("Shell"): return
        from ..shell.decorator import RegisterCommand
        from ....models.Shell import CommandRequirements

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

        @RegisterCommand(
            "rpcgen", "Generates a typed client for all RPC Namespaces, language is picked by extension (.ts or .py)",
            CommandRequirements(
                args = {"path": str}
            )
        )
        def rpc_gen(path: str):
            self.generate_client(path)

    def generate_client(self, path: str):
        from .adapters import TypeScriptGenerator, PythonGenerator

        generators = {".ts": ("TypeScript", TypeScriptGenerator), ".py": ("Python", PythonGenerator)}
        lang, generator = generators.get(os.path.splitext(path)[1].lower(), (None, None))
        if not generator:
            Logger.error(f"Unsupported client type, expected one of: {', '.join(generators.keys())}")
            return

        out = getRoot(path)
        with open(out, "w", encoding="utf-8") as f:
            f.write(generator(self.namespaces))
        Logger.ok(f"Generated {lang} RPC client at '{out}'")

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

        for file in Config("http")["rpc.generateTo"]:
            self.generate_client(getRoot(file))

    async def _remoteCall(self, ctx: WebSocketContext, data: dict):
        ref = data.get("ref")
        if not isinstance(ref, str) or len(ref) > 32 or len(ref) < 3: return await ctx.close()

        for k in ["namespace", "func", "args", "kwargs"]:
            if k not in data.keys():
                return await ctx.send({"id": "error", "data": {"details": f"Malformed function call, '{k}' is missing", "ref": ref}})

        args = data.get("args") or []
        kwargs = data.get("kwargs") or {}
        if not isinstance(args, list): return await ctx.send({"id": "error", "data": {"details": "Malformed function call, args is not a list", "ref": ref}})
        if not isinstance(kwargs, dict): return await ctx.send({"id": "error", "data": {"details": "Malformed function call, kwargs is not a dict", "ref": ref}})
        
            
        ns = self.namespaces.get(data.get("namespace"))
        if ns is None:
            return await ctx.send({"id": "error", "data": {"details": "No such namespace found", "ref": ref}})

        func_name = data.get("func")
        for fn in ns.funcs:
            if fn.name == func_name:
                try:
                    out = await maybeAwait(fn.func(*args, **kwargs))
                    return await ctx.send({"id": "call", "data": {"output": out, "ref": ref}})
                except Exception as e:
                    Logger.trace(e)
                    return await ctx.send({"id": "error", "data": {"details": "Function failed to execute", "ref": ref}})

        
        return await ctx.send({"id": "error", "data": {"details": f"Function not found", "ref": ref}})
            
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