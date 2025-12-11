from ..services.config import ConfigManager
from ..services.logger import LogManager

logger = LogManager("Runner")

class Runner:
    def __init__(self):
        self.servers = {
            "http": None,
            "io": None,
            "ws": None,
        }
        
    def start_servers(self):
        from .. import Core
        from ..servers.http import HTTPServer
        # from ..servers.ws import WebSocketServer
        
        config = Core.Config
        
        if config.getMaster("servers.http.enabled"):
            self.servers["http"] = HTTPServer(self)
            self.servers["http"].start()
        else: logger.info("HTTP Server is disabled")
            
        # if config.getMaster("servers.ws.enabled"):
        #     self.servers["ws"] = WebSocketServer(self)
        #     self.servers["ws"].start()
        # else: logger.info("WebSocket Server is disabled")