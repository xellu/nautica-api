from . import router, server, openapi

from ....manager import Config, ConfigBuilder
from ....models.Service import Service

class HTTPConfig(Service):
    def __init__(self):
        super().__init__()
    
    def onInstall(self):
        Config.Update("nautica",
            ConfigBuilder()
                .add("services.http", False, comment="Enables the HTTP Server service")
                
                .add("http.host", "127.0.0.1", comment="Use 0.0.0.0 to expose your app, 127.0.0.1 to keep local")
                .add("http.port", 8100, comment="Port to host the app on, by default is set to 8100")
                .add("http.realIPHeader", "", comment="Name of the header which has the real ip, e.g. X-Real-IP, CF-Connecting-IP (if behind proxy), set to empty to use requesting machine's IP instead")
                .add("http.logRequests", True, comment="Logs all successful requests. If disabled, only error requests are displayed, and boosts performance.")
                
                #static files
                .add("http.static.enabled", False, comment="Set to true if you wish to send static files from a directory")
                .add("http.static.endpoint", "/static", comment="Endpoint by which the static directory will be reached")
                .add("http.static.directory", "/path/to/directory", comment="Files in this directory will be accessible by sending a GET request to endpoint above")
                
                #cors
                .add("http.cors.enabled", False, comment="Enable Cross-Origin Resource Sharing (refer to https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)")
                .add("http.cors.origins", ["*"], comment="List of allowed origins (Access-Control-Allow-Origin), empty list blocks all origins")
                .add("http.cors.methods", ["*"], comment="List of allowed methods (Access-Control-Request-Method)")
                .add("http.cors.headers", ["*"], comment="List of allowed headers (Access-Control-Request-Headers)")
                .add("http.cors.exposeHeaders", [], comment="List of exposed headers")
                .add("http.cors.credentials", False, comment="Allow cookies and auth headers (Authorization) to be sent with cross-origin requests")
                .build()
        )
        
    def isEnabled(self):
        return Config("nautica")["services.http"]
    
Service.Export(HTTPConfig)