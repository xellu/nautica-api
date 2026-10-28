from ....models.Service import Service
from ....manager import Logger
from ....manager import Config, ConfigBuilder

class RPC(Service):
    def __init__(self):
        super().__init__()

        self.registry = None

    def onInstall(self):
        Config.Update("http", ConfigBuilder()
            .add("plugins.rpc", False, comment="Enable remote function calls using websockets")
            .build()              
        )

    def isEnabled(self):
        return  Config("http")["plugins.rpc"]
    
    def onSetup(self, registry):
        self.registry = registry

Service.Export(RPC, srcDir="rpc", depends_on=["WebSocket"])