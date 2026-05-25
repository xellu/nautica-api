from ...models.Service import Service
from ...manager import Config, ConfigBuilder

import os
class System(Service):
    def __init__(self):
        pass
    
    def onInstall(self):
        #config.n3
        Config.New("nautica",
            ConfigBuilder()
                .add("nautica.debug", True, "Enables tools and endpoints useful of debugging")
                .add("nautica.systemd", False, "Disables the shell service in order to work as a systemd service (Remote Access may be needed)")
                .build()
        )
        
        #package.n3
        dir_name = os.path.basename(os.path.abspath("."))        
        Config.New("package",
            ConfigBuilder()
                .add("name", dir_name, "About your project, feel free to edit this section")
                .add("version", "1.0.0")
                .add("description", "A Nautica3 Project")
                .add("author", [os.getlogin()])

                .add("app.dependsOn", [], "Your project's dependencies, to add use: nautica install <package>")
                .build()
        )
        
Service.Export(System)