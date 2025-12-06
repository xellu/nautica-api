from ..services.config import ConfigManager
from ..services.logger import LogManager

logger = LogManager("Runner")

class Runner:
    def __init__(self):
        self.config: ConfigManager = None
        self.servers = {
            "http": None,
            "io": None,
            "ws": None,
        }
        
    def init(self, config):
        self.config = config
        
    def start_servers(self):
        from ..servers.http import HTTPServer
                
        self.servers["http"] = HTTPServer(self)
        self.servers["http"].start()