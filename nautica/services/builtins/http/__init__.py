from . import router, server

from ....manager import Config, ConfigBuilder
from ....models.Service import Service

class HTTPConfig(Service):
    def __init__(self):
        pass
    
    def onInstall(self):
        Config.Update("nautica",
            ConfigBuilder()
                .add("services.http", True, comment="Enables the HTTP Server service")

                .add("http.host", "127.0.0.1", comment="Use 0.0.0.0 to expose your app, 127.0.0.1 to keep local")
                .add("http.port", 8100, comment="Port to host the app on, by default is set to 8100")
                .add("http.realIPHeader", "", comment="Name of the header which has the real ip, e.g. X-Real-IP, CF-Connecting-IP (if behind proxy), set to empty to use requesting machine's IP instead")
                
                .add("http.static.enabled", False, comment="Set to true if you wish to send static files from a directory")
                .add("http.static.endpoint", "/static", comment="Endpoint by which the static directory will be reached")
                .add("http.static.directory", "/path/to/directory", comment="Files in this directory will be accessible by sending a GET request to endpoint above")
                .build()
        )
        
Service.Export(HTTPConfig)