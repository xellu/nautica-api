from ...models.Service import Service
from ...manager import Config, ConfigBuilder, Scheduler

import asyncio
import threading

class System(Service):
    def __init__(self):
        pass
    
    def onInstall(self):
        #config.n3
        Config.New("nautica",
            ConfigBuilder()
                .add("nautica.debug", False, "Enables tools and endpoints useful of debugging")
                .build()
        )
        
        # #package.n3
        # dir_name = os.path.basename(os.path.abspath("."))        
        # Config.New("package",
        #     ConfigBuilder()
        #         .add("name", dir_name, "About your project, feel free to edit this section")
        #         .add("version", "1.0.0")
        #         .add("description", "A Nautica3 Project")
        #         .add("author", [os.getlogin()])

        #         .add("app.dependsOn", [], "Your project's dependencies, to add use: nautica install <package>")
        #         .build()
        # ) #deprecated
        
        #package-lock
        if not Config.Exists("lock"):
            Config.New("lock", ConfigBuilder().build())
        
    def onStart(self, registry):
        threading.Thread(
            target = self.runScheduler,
            daemon = True
        ).start()
    
    def runScheduler(self):
        asyncio.run(Scheduler._loop())
        
        
Service.Export(System)