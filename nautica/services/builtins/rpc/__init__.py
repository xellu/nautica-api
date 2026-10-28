from ....models.Service import Service
from ....manager import Config, ConfigBuilder, Logger
from ....ext.Util import walkPath, importModule, getRoot
from ....models.Rpc import RPCNamespace

from napi.rpc import _RPCNamespace

import os

class RPC(Service):
    def __init__(self):
        super().__init__()

        self.registry = None
        self.namespaces = {
            #name: RPCName
        }

    def onInstall(self):
        Config.Update("http", ConfigBuilder()
            .add("plugins.rpc", False, comment="Enable remote function calls using websockets")
            .build()              
        )

    def isEnabled(self):
        return  Config("http")["plugins.rpc"]
    
    def onSetup(self, registry):
        self.registry = registry

    def onStart(self, registry):
        for file in walkPath(getRoot("src/rpc")):
            if not file.endswith(".py"): continue

            name = self.pathToNamespace(file)
            namespace = self.namespaces.get(name)
            if not namespace:
                namespace = RPCNamespace(name)
                self.namespaces[name] = self.namespaces
            
            _RPCNamespace.namespace = namespace
            importModule(file)

            Logger.info(f"{_RPCNamespace.namespace.name}={_RPCNamespace.namespace.funcs}")


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

Service.Export(RPC, srcDir="rpc", depends_on=["WebSocket"])