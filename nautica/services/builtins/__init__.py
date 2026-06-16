from ...models.Service import Service
from ...manager import Config, ConfigBuilder, Scheduler

import asyncio
import threading

class System(Service):
    def __init__(self):
        super().__init__()
    
    def onInstall(self):
        #config.n3
        Config.New("nautica",
            ConfigBuilder()
                .add("nautica.debug", False, "Enables tools and endpoints useful of debugging")
                .add("services.shell", True, "Enables the interactive shell") #make sure services is the 2nd thing in the config
                .build()
        )
        
        #package-lock
        if not Config.Exists("lock"):
            Config.New("lock", ConfigBuilder().build())
        
    def isEnabled(self):
        return True
        
    def onStart(self, registry):
        threading.Thread(
            target = self.runScheduler,
            daemon = True
        ).start()
    
    def runScheduler(self):
        asyncio.run(Scheduler._loop())
        
        
Service.Export(System)